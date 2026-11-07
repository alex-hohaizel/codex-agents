#!/usr/bin/env python3
"""Portable structural task-artifact checks; no LLM, transport, approval or native gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile

SCHEMA = "adaptive-task/1"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets/adaptive-task.schema.json"
LIMITATIONS = {
    "quality_certified": False,
    "semantic_completeness_certified": False,
    "authority_authenticated": False,
    "native_gate_checked": False,
    "execution_observed": False,
}


class Invalid(ValueError):
    pass


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_path(root: Path, value: str, *, must_exist: bool = True) -> Path:
    """Require portable project-relative paths and reject symlink components."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise Invalid(f"unsafe project-relative path: {value!r}")
    parts = value.split("/")
    if value.startswith("/") or any(x in {"", ".", ".."} for x in parts):
        raise Invalid(f"unsafe project-relative path: {value!r}")
    if PurePosixPath(value).is_absolute():
        raise Invalid(f"absolute path is not portable: {value!r}")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise Invalid("project root is not a directory")
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise Invalid(f"symlink component is not accepted: {value}")
    if not p.resolve(strict=False).is_relative_to(root):
        raise Invalid(f"path escapes project root: {value}")
    if must_exist:
        if not p.exists() or not stat.S_ISREG(p.stat().st_mode):
            raise Invalid(f"missing regular project file: {value}")
    return p


def read_json(path: Path):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise Invalid(f"duplicate JSON key: {k}")
            d[k] = v
        return d
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f"invalid UTF-8 JSON in {path.name}: {exc}") from exc


def shape(value, spec, loc="$", errors=None):
    """Validate precisely the JSON Schema keywords used in the bundled schema."""
    if errors is None:
        errors = []
    types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    typ = spec.get("type")
    if typ and (not isinstance(value, types[typ]) or typ == "integer" and isinstance(value, bool)):
        errors.append(f"{loc}: expected {typ}")
        return errors
    if "const" in spec and value != spec["const"]:
        errors.append(f"{loc}: expected {spec['const']!r}")
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{loc}: unsupported value {value!r}")
    if isinstance(value, str):
        if len(value.strip()) < spec.get("minLength", 0):
            errors.append(f"{loc}: empty text")
        if "pattern" in spec and re.fullmatch(spec["pattern"], value) is None:
            errors.append(f"{loc}: invalid format")
    if typ == "integer" and value < spec.get("minimum", value):
        errors.append(f"{loc}: below minimum")
    if isinstance(value, dict):
        props = spec.get("properties", {})
        for name in spec.get("required", []):
            if name not in value:
                errors.append(f"{loc}.{name}: required")
        for name, child in value.items():
            if name in props:
                shape(child, props[name], f"{loc}.{name}", errors)
            elif spec.get("additionalProperties") is False:
                errors.append(f"{loc}.{name}: unsupported field")
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            errors.append(f"{loc}: too few items")
        for i, child in enumerate(value):
            shape(child, spec.get("items", {}), f"{loc}[{i}]", errors)
    return errors


def json_pointer(document, pointer):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise Invalid("registration entry_pointer must be a non-root JSON Pointer")
    value = document
    for raw in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw):
            raise Invalid("invalid JSON Pointer escape")
        key = raw.replace("~1", "/").replace("~0", "~")
        try:
            value = value[int(key)] if isinstance(value, list) and key.isdecimal() else value[key]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise Invalid("registration entry_pointer was not found") from exc
    return value


def validate(document, root: Path, task_path: Path | None = None):
    errors = shape(document, read_json(SCHEMA_PATH))
    verdict = {
        "schema": SCHEMA, "valid": False, "errors": errors,
        "artifact_registered": False, "registration_declared": None,
        "source_integrity_checked": False, "evidence_integrity_checked": False,
        **LIMITATIONS,
    }
    if errors:
        return verdict
    sources = {x["id"]: x for x in document["sources"]}
    obligations = {x["id"]: x for x in document["obligations"]}
    outputs = {x["id"]: x for x in document["outputs"]}
    evidence = {x["id"]: x for x in document.get("evidence", [])}
    effects = {x["id"]: x for x in document.get("effects", [])}
    all_ids = []
    for label in ("sources", "obligations", "outputs", "evidence", "effects"):
        all_ids.extend(x["id"] for x in document.get(label, []))
    all_ids.extend(x["id"] for x in document["strategy"]["competencies"])
    if len(all_ids) != len(set(all_ids)):
        errors.append("IDs must be globally unique across artifact record kinds")

    def refs(values, known, loc, nonempty=False):
        if len(values) != len(set(values)):
            errors.append(f"{loc}: duplicate references")
        if nonempty and not values:
            errors.append(f"{loc}: must reference at least one record")
        for ref in values:
            if ref not in known:
                errors.append(f"{loc}: unknown reference {ref}")

    def bound(record, loc):
        try:
            path = safe_path(root, record["path"])
            if task_path is not None and path == task_path:
                raise Invalid("artifact cannot use itself as a source/output/evidence")
            if digest(path) != record["sha256"]:
                errors.append(f"{loc}: stale SHA-256 for {record['path']}")
        except (Invalid, OSError) as exc:
            errors.append(f"{loc}: {exc}")

    for src in sources.values():
        bound(src, f"source {src['id']}")
    verdict["source_integrity_checked"] = True
    for obligation in obligations.values():
        rid = obligation["id"]
        refs(obligation["source_ids"], sources, rid, True)
        refs(obligation["output_ids"], outputs, rid)
        if obligation["status"] == "included" and not obligation["output_ids"]:
            errors.append(f"{rid}: included obligation requires an output")
        if obligation["status"] in {"deferred", "excluded", "unknown"} and not obligation.get("disposition"):
            errors.append(f"{rid}: disposition and actual basis are required")
    used_sources = {s for ob in obligations.values() for s in ob["source_ids"]}
    for src in sources.values():
        if src["kind"] in {"obligation", "question", "constraint"} and src["id"] not in used_sources:
            errors.append(f"source {src['id']}: no declared obligation mapping")
    for competence in document["strategy"]["competencies"]:
        refs(competence["source_ids"], sources, competence["id"])
        refs(competence["output_ids"], outputs, competence["id"], True)
        if competence["availability"] == "verified" and not competence["source_ids"]:
            errors.append(f"{competence['id']}: verified availability needs source binding")
    for output in outputs.values():
        refs(output["evidence_ids"], evidence, output["id"])
        if output["status"] != "planned":
            if "path" not in output or "sha256" not in output:
                errors.append(f"{output['id']}: actual output needs exact path/hash")
            else:
                bound(output, output["id"])
        elif "path" in output or "sha256" in output:
            if "path" not in output or "sha256" not in output:
                errors.append(f"{output['id']}: path and hash must occur together")
            else:
                bound(output, output["id"])
        if output["status"] in {"reviewed", "accepted"}:
            passes = [evidence[e] for e in output["evidence_ids"] if e in evidence and evidence[e]["result"] == "pass"]
            if not passes:
                errors.append(f"{output['id']}: reviewed/accepted claim needs a bound passing observation")
            if document["assessment"]["consequence"] == "critical" and not any(e["observer"] != output["author"] for e in passes):
                errors.append(f"{output['id']}: critical acceptance requires another declared observer")
    for ev in evidence.values():
        bound(ev, ev["id"])
        refs(ev["output_ids"], outputs, ev["id"], True)
        subjects = {subject["output_id"]: subject["sha256"] for subject in ev["subjects"]}
        if len(subjects) != len(ev["subjects"]):
            errors.append(f"{ev['id']}: duplicate evidence subject bindings")
        refs(list(subjects), outputs, f"{ev['id']} subjects")
        for oid, subject_hash in subjects.items():
            if oid not in ev["output_ids"]:
                errors.append(f"{ev['id']}: subject is outside declared output_ids")
            if oid in outputs and outputs[oid].get("sha256") != subject_hash:
                errors.append(f"{ev['id']}: stale immutable subject SHA-256 for {oid}")
        for oid in ev["output_ids"]:
            if oid in outputs and ev["id"] not in outputs[oid]["evidence_ids"]:
                errors.append(f"{ev['id']}: output/evidence links must be bidirectional")
            if oid in outputs and outputs[oid].get("sha256") and oid not in subjects:
                errors.append(f"{ev['id']}: actual output requires immutable subject SHA-256 for {oid}")
    for output in outputs.values():
        for eid in output["evidence_ids"]:
            if eid in evidence and output["id"] not in evidence[eid]["output_ids"]:
                errors.append(f"{output['id']}: evidence does not bind this output")
    verdict["evidence_integrity_checked"] = True

    def grants(ids, loc):
        refs(ids, sources, loc)
        for sid in ids:
            if sid in sources and sources[sid]["authority"] not in {"user", "project"}:
                errors.append(f"{loc}: reference/untrusted source is not a grant")
            if sid in sources and sources[sid]["kind"] in {"example", "evidence"}:
                errors.append(f"{loc}: example/evidence is not itself a grant")
    grants(document["authority"]["grant_source_ids"], "authority")
    for effect in effects.values():
        grants(effect["grant_source_ids"], effect["id"])
        refs(effect["evidence_ids"], evidence, effect["id"])
        if effect["retry_requested"] and effect["state"] in {"unknown", "confirmed_success"}:
            errors.append(f"{effect['id']}: cannot retry unknown or already successful effect")
        if effect["state"].startswith("confirmed_") and not effect["evidence_ids"]:
            errors.append(f"{effect['id']}: confirmed effect requires receipt evidence")
        if effect["state"] != "planned" and not effect["grant_source_ids"]:
            errors.append(f"{effect['id']}: actual effect requires a declared grant source")
    route = document["authority"].get("route")
    if route:
        options = {o["id"]: o for o in route["options"]}
        if len(options) != len(route["options"]):
            errors.append("route: duplicate option IDs")
        eligible = [o for o in options.values() if o["available"] and o["allowed"] and o["identity_verified"]]
        for option in options.values():
            refs(option["proof_source_ids"], sources, f"route {option['id']}")
            if option in eligible and not option["proof_source_ids"]:
                errors.append(f"route {option['id']}: verified option requires proof source")
        if route["basis"] == "unique_verified":
            if len(eligible) != 1 or route.get("chosen") != eligible[0]["id"]:
                errors.append("route: unique_verified requires exactly one eligible chosen option")
        if route["basis"] == "owner_chosen":
            grants(route.get("grant_source_ids", []), "route")
            if not route.get("grant_source_ids") or route.get("chosen") not in {o["id"] for o in eligible}:
                errors.append("route: owner_chosen needs a grant and an eligible chosen option")
        if route["basis"] == "unresolved" and ("chosen" in route or route["state"] != "prepared"):
            errors.append("route: unresolved choice cannot claim selection or downstream progress")
        refs(route["receipt_evidence_ids"], evidence, "route receipts")
        if route["state"] in {"delivered", "admitted", "started", "result", "reviewed", "accepted"} and not route["receipt_evidence_ids"]:
            errors.append("route: downstream progress requires a bound receipt")
    review = document.get("review")
    if review:
        refs(review["source_ids"], sources, "review", review["state"] == "complete")
        reviewed_hashes = {binding["source_id"]: binding["sha256"] for binding in review["source_bindings"]}
        if len(reviewed_hashes) != len(review["source_bindings"]):
            errors.append("review: duplicate source snapshot bindings")
        refs(list(reviewed_hashes), sources, "review source bindings")
        for sid, reviewed_hash in reviewed_hashes.items():
            if sid not in review["source_ids"]:
                errors.append(f"review: source snapshot {sid} is outside reviewed source_ids")
            if sid in sources and sources[sid]["sha256"] != reviewed_hash:
                errors.append(f"review: stale immutable source SHA-256 for {sid}")
        if review["state"] == "complete" and set(review["source_ids"]) != set(reviewed_hashes):
            errors.append("review: complete review requires immutable hashes for every reviewed source")
        if review["state"] == "complete" and not review["raw_sources_reviewed"]:
            errors.append("review: complete reconciliation must declare raw-source review")
        raw_required = {sid for ob in obligations.values() for sid in ob["source_ids"]}
        raw_required.update(sid for sid, src in sources.items() if src["authority"] in {"user", "project"} and src["kind"] in {"decision", "example", "context"})
        if review["state"] == "complete" and not raw_required.issubset(set(review["source_ids"])):
            errors.append("review: complete reconciliation must bind all declared primary and obligation sources")
    if document["assessment"]["depth"] == "deep" and document["task"]["status"] == "accepted":
        if not review or review["state"] != "complete" or review["actor"] == document["task"]["owner"]:
            errors.append("deep accepted task requires another declared raw-source reviewer")
    if document["task"]["status"] == "accepted":
        if any(ob["status"] == "unknown" for ob in obligations.values()):
            errors.append("accepted task cannot retain unknown obligations")
        due_outputs = {o for ob in obligations.values() if ob["status"] == "included" for o in ob["output_ids"]}
        if any(outputs[o]["status"] != "accepted" for o in due_outputs if o in outputs):
            errors.append("accepted task requires accepted included outputs")
        if any(e["state"] == "unknown" for e in effects.values()):
            errors.append("accepted task cannot retain unknown external effects")
    if document["next"]["requires_user"]:
        for field in ("where", "instruction", "success_signal", "return_to"):
            if not document["next"].get(field):
                errors.append(f"next.{field}: exact user step is required")

    registration = document["registration"]
    verdict["registration_declared"] = registration["state"]
    registry_path = document["project"].get("registry_path")
    if registry_path:
        try:
            safe_path(root, registry_path)
        except (Invalid, OSError) as exc:
            errors.append(f"project.registry_path: {exc}")
        if registration["state"] == "not_required":
            errors.append("project with a native registry requires pending or registered artifact admission")
    if registration["state"] == "registered":
        try:
            if not registry_path or registration.get("registry_path") != registry_path:
                raise Invalid("registration must use the declared canonical native registry")
            if task_path is None or not task_path.is_file():
                raise Invalid("registration can only be verified against a saved artifact")
            reg = read_json(safe_path(root, registry_path))
            entry = json_pointer(reg, registration.get("entry_pointer"))
            if not isinstance(entry, dict):
                raise Invalid("native artifact reference must resolve to an object")
            relative = str(task_path.relative_to(root.resolve())).replace(os.sep, "/")
            if entry.get(registration.get("path_field", "path")) != relative or entry.get(registration.get("hash_field", "sha256")) != digest(task_path):
                raise Invalid("native registry does not reference these exact artifact bytes")
            verdict["artifact_registered"] = True
        except (Invalid, OSError, ValueError) as exc:
            errors.append(f"registration: {exc}")
    verdict["valid"] = not errors
    return verdict


def create(document, root: Path, output: str, expected: str | None = None):
    root = root.resolve(strict=True)
    path = safe_path(root, output, must_exist=False)
    if not path.parent.is_dir():
        raise Invalid("output parent must already exist inside the project")
    verdict = validate(document, root, path)
    if not verdict["valid"]:
        return verdict
    if document["registration"]["state"] == "registered":
        raise Invalid("create pending artifact first; native registration is a separate operation")
    lock = safe_path(root, output + ".lock", must_exist=False)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise Invalid("artifact writer lock exists; reconcile owner/result before retry") from exc
    temporary = None
    try:
        os.write(fd, json.dumps({"pid": os.getpid(), "artifact": output}).encode())
        os.fsync(fd)
        safe_path(root, output, must_exist=False)
        if path.exists():
            if expected is None or digest(path) != expected:
                raise Invalid("existing artifact changed or overwrite lacks expected SHA-256")
            old = read_json(path)
            if old.get("project", {}).get("id") != document["project"]["id"] or old.get("task", {}).get("id") != document["task"]["id"]:
                raise Invalid("cannot replace another project/task identity")
            if document["task"]["revision"] != old.get("task", {}).get("revision", 0) + 1:
                raise Invalid("replacement requires exactly the next task revision")
        elif expected is not None:
            raise Invalid("expected existing artifact is absent")
        fresh = validate(document, root, path)
        if not fresh["valid"]:
            return fresh
        payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        tfd, temp_name = tempfile.mkstemp(prefix=".adaptive-", dir=path.parent)
        temporary = Path(temp_name)
        with os.fdopen(tfd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        # Preserve a target's permissions; new private artifacts start at 0600.
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
            if expected is None or digest(path) != expected:
                raise Invalid("artifact changed before atomic replacement")
        safe_path(root, output, must_exist=False)
        os.replace(temporary, path)
        temporary = None
        return {**fresh, "saved": True, "artifact_path": output, "sha256": digest(path), "registration_action": "use canonical native tool" if document["registration"]["state"] == "pending" else "task-only artifact"}
    finally:
        os.close(fd)
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def render(document, verdict):
    task = document["task"]
    lines = [f"**{task['id']} · ревізія {task['revision']} · {task['status']}**", "", task["goal"], "", f"Обсяг: {task['scope']}", f"Підхід: {document['assessment']['depth']} — {document['assessment']['rationale']}", f"Стратегія: {document['strategy']['mode']} / {document['strategy']['reuse_choice']} — {document['strategy']['rationale']}", "", "| Вимога | Статус / коли | Результат | Приймання |", "|---|---|---|---|"]
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    for r in document["obligations"]:
        lines.append(f"| {cell(r['id'] + ': ' + r['text'])} | {cell(r['status'] + ' / ' + r['due'])} | {cell(', '.join(r['output_ids']))} | {cell(r['acceptance'])} |")
    lines += ["", f"Наступний крок: {document['next']['action']}", f"Відповідальний: {document['next']['owner']}"]
    if document["next"]["requires_user"]:
        lines += [f"Де: {document['next']['where']}", f"Що виконати: {document['next']['instruction']}", f"Ознака успіху: {document['next']['success_signal']}", f"Повернути результат: {document['next']['return_to']}"]
    lines += ["", f"Структура/bytes: {'PASS' if verdict['valid'] else 'FAIL'}. Native registration: {verdict['artifact_registered']}.", "Змістова якість, згода, native gate і фактичне виконання цим інструментом не сертифікуються."]
    if verdict["errors"]:
        lines += ["", "Помилки:"] + [f"- {e}" for e in verdict["errors"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "validate", "render", "status"):
        p = sub.add_parser(command)
        p.add_argument("--project-root", required=True, type=Path)
        if command == "create":
            p.add_argument("--input", required=True, type=Path)
            p.add_argument("--output", required=True)
            p.add_argument("--expected-sha256")
        else:
            p.add_argument("--task", required=True)
    args = parser.parse_args(argv)
    try:
        root = args.project_root.resolve(strict=True)
        if args.command == "create":
            result = create(read_json(args.input), root, args.output, args.expected_sha256)
        else:
            task_path = safe_path(root, args.task)
            document = read_json(task_path)
            result = validate(document, root, task_path)
            result.update({"artifact_path": args.task, "artifact_sha256": digest(task_path)})
            if args.command == "status" and isinstance(document, dict) and isinstance(document.get("task"), dict):
                effects = document.get("effects", [])
                result.update({"declared_task_status": document["task"].get("status"), "next": document.get("next"), "unknown_effects": [x.get("id") for x in effects if isinstance(x, dict) and x.get("state") == "unknown"] if isinstance(effects, list) else None})
            if args.command == "render" and not shape(document, read_json(SCHEMA_PATH)):
                print(render(document, result), end="")
                return 0 if result["valid"] else 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    except (Invalid, OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)], "artifact_registered": False, **LIMITATIONS}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
