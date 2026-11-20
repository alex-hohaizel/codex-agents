#!/usr/bin/env python3
"""Portable handoff integrity checks; never grants approval or certifies game quality."""
import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import types
import zipfile
from pathlib import Path, PurePosixPath



def strict_json_loads(raw, **kwargs):
    """Reject ambiguous/nonfinite JSON before hashing, validation or mutation."""
    if len(raw) > 256 * 1024 * 1024:
        raise ValueError("JSON exceeds bounded input limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)
    kwargs.setdefault("object_pairs_hook", unique)
    kwargs.setdefault("parse_constant", finite)
    return json.loads(raw, **kwargs)

VERSION = "1.0.0"
TOOLKIT_VERSION = "6.0.0"
KINDS = {
    "studio": "studio_identity brand_master brand_rules setup_runbook rights_ledger",
    "concepts": "studio_identity concept_comparison selected_concept progression_model economy_model visual_baseline validation_plan",
    "preproduction": "studio_identity gdd tdd interaction_atlas progression_model economy_model fidelity_spec asset_plan audio_design test_plan",
    "assets": "studio_identity editable_sources runtime_exports asset_registry rights_ledger visual_comparison audio_audition import_receipt",
    "build": "studio_identity source_snapshot toolchain_lock build_receipt native_artifact implementation_coverage save_migration",
    "qa": "studio_identity test_report device_matrix fidelity_report economy_report defects release_recommendation",
    "release": "studio_identity release_manifest store_metadata privacy_inventory purchase_validation rollback_plan operator_runbook",
    "liveops": "studio_identity telemetry_plan support_runbook content_cadence experiment_plan incident_runbook",
}
RECORDS = ("requirements", "decisions", "reviews", "claims")
HEX = re.compile(r"^[0-9a-f]{64}$")
EXEMPT = {"record", "evidence", "human_entrypoint"}

def required_decisions(stage):
    result = ["DEC-BRAND"]
    if stage != "studio": result += ["DEC-PLATFORMS", "DEC-CONCEPT"]
    if stage not in {"studio", "concepts"}: result += ["DEC-ENGINE", "DEC-MONETIZATION"]
    return result

def read_json(path):
    return strict_json_loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_path(root, name):
    p = PurePosixPath(name)
    if not name or "\\" in name or ":" in name or p.is_absolute() or ".." in p.parts or name != p.as_posix():
        raise ValueError("unsafe/noncanonical relative path: " + str(name))
    candidate = root.joinpath(*p.parts)
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("path outside package: " + name)
    if any(root.joinpath(*p.parts[:i]).is_symlink() for i in range(1, len(p.parts) + 1)):
        raise ValueError("symlink forbidden: " + name)
    return candidate

def inventory(root):
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise ValueError("symlink forbidden: " + str(p))
        if p.is_file() and p.relative_to(root).as_posix() != "manifest.json":
            rel = p.relative_to(root)
            if ".git" in rel.parts or (p.name.startswith(".env") and p.name != ".env.example") or p.suffix.lower() in {".p12", ".p8", ".jks", ".keystore", ".mobileprovision"}:
                raise ValueError("private/signing/repository metadata must not enter handoff: " + str(rel))
            safe_path(root, p.relative_to(root).as_posix())
            files.append(p)
    return files

def init(root, stage, project_id):
    if root.exists() and any(root.iterdir()):
        raise ValueError("init requires an empty or new directory")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", project_id):
        raise ValueError("project-id must be a lowercase slug")
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / "manifest.json", {
        "schema_version": VERSION, "suite_version": VERSION, "toolkit_version": TOOLKIT_VERSION, "package_id": project_id + "-" + stage + "-r1",
        "project_id": project_id, "stage": stage, "revision": 1, "stage_status": "draft",
        "upstream": [], "artifacts": []})
    for record in RECORDS:
        items = []
        if record == "requirements":
            items = [{"id": "REQ-START", "source": "project brief", "priority": "must", "owner": "pending",
                      "status": "pending", "acceptance": "Replace with scoped stage requirements", "artifact_ids": [], "evidence_ids": [], "rationale": ""}]
        if record == "decisions":
            items = [{"id": ident, "question": "Record material choice and actual authority", "material": True,
                      "status": "pending", "answer": None, "authority_ref": None, "scope": stage}
                     for ident in required_decisions(stage)]
        write_json(root / "records" / (record + ".json"), {"items": items})
    (root / "START_HERE.md").write_text("# Draft handoff\n\nRecord actual scope, decisions, evidence, blockers, environment and next command.\n", encoding="utf-8")
    seal(root)

def seal(root):
    m = read_json(root / "manifest.json")
    old = {a["path"]: a for a in m.get("artifacts", [])}
    used = {a["id"] for a in old.values()}
    artifacts = []
    counter = 1
    for p in inventory(root):
        name = p.relative_to(root).as_posix()
        a = dict(old.get(name, {}))
        if not a:
            while "ART-%04d" % counter in used:
                counter += 1
            a = {"id": "ART-%04d" % counter, "path": name,
                 "kind": "record" if name.startswith("records/") else "human_entrypoint" if name == "START_HERE.md" else "unclassified",
                 "status": "draft", "author_ids": [], "depends_on": []}
            used.add(a["id"])
        a["sha256"] = sha(p)
        artifacts.append(a)
    m["artifacts"] = artifacts
    write_json(root / "manifest.json", m)
    print(json.dumps({"sealed": str(root), "files": len(artifacts), "approval_granted": False}))

def model_gate(manifest):
    """A scoped QA/ops acceptance never claims the full product release gate."""
    stage = manifest.get("stage")
    defaults = {"concepts": "concept", "preproduction": "preproduction", "assets": "slice", "build": "slice", "qa": "beta", "release": "release", "liveops": "release"}
    ref = manifest.get("game_model") or {}
    scope = ref.get("acceptance_scope")
    scopes = {
        "concepts": {"candidate_completion": "concept"},
        "qa": {"design_review": "concept", "contract_review": "preproduction", "slice_review": "slice", "beta_review": "beta", "release_readiness": "release"},
        "liveops": {"incident_analysis": "concept", "design_change": "preproduction", "runtime_change": "slice", "player_experiment": "beta", "release_change": "release"},
    }
    if scope is None:
        return defaults.get(stage, "concept"), "full_stage"
    if manifest.get("toolkit_version") != TOOLKIT_VERSION:
        raise ValueError("scoped acceptance requires the current toolkit marker and model gate")
    if scope not in scopes.get(stage, {}):
        raise ValueError("acceptance_scope is not allowed for this stage")
    if not all(isinstance(ref.get(k), str) and ref[k].strip() for k in ("scope_ref", "scope_description")):
        raise ValueError("scoped gate requires scope_ref and scope_description")
    return scopes[stage][scope], scope


def acceptance_profile(manifest):
    gate, scope = model_gate(manifest)
    stage = manifest.get("stage")
    kinds = KINDS.get(stage, "").split()
    decisions = required_decisions(stage)
    scoped_kinds = {
        "candidate_completion": "studio_identity concept_candidate progression_model economy_model visual_baseline validation_plan",
        "design_review": "test_report defects",
        "contract_review": "test_report defects validation_plan",
        "slice_review": "test_report device_matrix fidelity_report defects",
        "beta_review": "test_report device_matrix fidelity_report economy_report defects",
        "incident_analysis": "incident_report support_runbook",
        "design_change": "change_plan validation_plan",
        "runtime_change": "change_plan test_report",
        "player_experiment": "experiment_plan test_report",
        "release_change": "release_manifest rollback_plan operator_runbook",
    }
    if scope in scoped_kinds:
        kinds = scoped_kinds[scope].split()
        if scope != "release_change":
            decisions = []  # Candidate C1/review/analysis does not select production.
    return {"gate": gate, "scope": scope, "kinds": kinds, "decisions": decisions}


def verify(root, require_accepted=False, *, current_work=False, project_root=None):
    errors, warnings = [], []
    m = read_json(root / "manifest.json")
    for key in ("schema_version", "suite_version", "package_id", "project_id", "stage", "revision", "stage_status", "upstream", "artifacts"):
        if key not in m:
            errors.append("missing manifest field " + key)
    if m.get("schema_version") != VERSION:
        errors.append("unsupported handoff schema_version; create the current handoff")
    if m.get("suite_version") != VERSION:
        errors.append("unsupported handoff suite_version")
    if m.get("toolkit_version") != TOOLKIT_VERSION:
        errors.append("current toolkit_version required; previous result formats are not accepted")
    if m.get("stage") not in KINDS:
        errors.append("unknown stage")
    if m.get("stage_status") not in {"draft", "blocked", "accepted"}:
        errors.append("invalid stage_status")
    if not isinstance(m.get("revision"), int) or isinstance(m.get("revision"), bool) or m["revision"] < 1:
        errors.append("revision must be positive integer")
    accepted = require_accepted or m.get("stage_status") == "accepted"
    try:
        profile = acceptance_profile(m)
    except ValueError as error:
        errors.append(str(error))
        profile = {"gate": None, "scope": None, "kinds": [], "decisions": []}
    if require_accepted and m.get("stage_status") != "accepted":
        errors.append("stage_status is not accepted")
    production_choices = None
    if accepted and current_work and m.get("stage") != "studio":
        stage = m.get("stage")
        scope = profile.get("scope")
        choice_phase = {"concepts": "implement", "preproduction": "implement",
                        "assets": "scale", "build": "scale", "qa": "accept",
                        "release": "accept", "liveops": "accept"}.get(stage)
        if scope in {"candidate_completion", "design_review", "incident_analysis"}:
            choice_phase = "explore"
        elif scope in {"contract_review", "design_change"}:
            choice_phase = "implement"
        elif scope in {"slice_review", "runtime_change"}:
            choice_phase = "scale"
        if choice_phase:
            try:
                from production_choices import ChoiceError, verify_project
                try:
                    production_choices = verify_project(project_root or root, choice_phase, required_kind="game")
                    decision = production_choices["decision_sha256"]
                    if decision is not None and m.get("production_choice_decision_sha256") != decision:
                        errors.append("handoff does not bind the current production decision; reconcile and reseal")
                except ChoiceError as exc:
                    errors.append("production choices: " + str(exc))
            except ImportError:
                errors.append("missing installed production choice verifier")
    artifacts = m.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise ValueError("artifacts must be array")
    byid, paths = {}, set()
    for a in artifacts:
        if not isinstance(a, dict) or not isinstance(a.get("id"), str) or not a["id"]:
            errors.append("artifact missing ID"); continue
        if a["id"] in byid:
            errors.append("duplicate artifact ID " + a["id"])
        byid[a["id"]] = a
        name = a.get("path", "")
        if name in paths:
            errors.append("duplicate path " + name)
        paths.add(name)
        p = safe_path(root, name)
        if not p.is_file():
            errors.append("missing artifact " + name)
        elif not HEX.fullmatch(str(a.get("sha256", ""))) or sha(p) != a.get("sha256"):
            errors.append("checksum mismatch " + name)
        if a.get("status") not in {"draft", "final", "reference"}:
            errors.append("invalid artifact status " + name)
        for key in ("author_ids", "depends_on"):
            if not isinstance(a.get(key), list) or not all(isinstance(x, str) and x for x in a[key]):
                errors.append("invalid artifact " + key + " " + name)
        if accepted and a.get("kind") not in EXEMPT:
            if a.get("status") == "draft" or a.get("kind") == "unclassified" or not a.get("author_ids"):
                errors.append("unfinished artifact " + name)
    actual = {p.relative_to(root).as_posix() for p in inventory(root)}
    if actual != paths:
        errors.append("inventory differs: run seal and review changes")
    for a in artifacts:
        for dep in a.get("depends_on", []):
            if dep not in byid:
                errors.append("broken dependency " + str(dep))
    visiting, visited = set(), set()
    def visit(ident):
        if ident in visiting:
            errors.append("dependency cycle at " + ident); return
        if ident in visited: return
        visiting.add(ident)
        for dep in byid[ident].get("depends_on", []):
            if dep in byid: visit(dep)
        visiting.remove(ident); visited.add(ident)
    for ident in byid: visit(ident)
    def dependency_closure(ident, seen=None):
        seen = set() if seen is None else seen
        for dep in byid[ident].get("depends_on", []):
            if dep in byid and dep not in seen:
                seen.add(dep); dependency_closure(dep, seen)
        return seen
    records = {}
    for name in RECORDS:
        p = root / "records" / (name + ".json")
        records[name] = read_json(p).get("items", [])
        if not isinstance(records[name], list): raise ValueError(name + " items must be array")
        ids = [x.get("id") for x in records[name]]
        if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
            errors.append("missing/duplicate IDs in " + name)
        for row in records[name]:
            for field in ("artifact_ids", "evidence_ids"):
                if field in row:
                    if not isinstance(row[field], list):
                        errors.append("invalid " + name + " " + field); continue
                    for ident in row[field]:
                        if ident not in byid: errors.append("broken " + name + " reference " + str(ident))
    passed = set()
    for r in records["reviews"]:
        if r.get("status") not in {"pass", "fail", "pending"}: errors.append("invalid review status")
        for ident in r.get("artifact_ids", []):
            if ident not in byid: continue
            a = byid[ident]
            if not r.get("reviewer_id") or r["reviewer_id"] in a.get("author_ids", []):
                errors.append("self-review or missing reviewer " + r.get("id", ""))
            if r.get("status") == "pass":
                if r.get("artifact_hashes", {}).get(ident) != a.get("sha256"):
                    errors.append("stale review " + r["id"] + " for " + ident)
                elif any(r.get("dependency_hashes", {}).get(dep) != byid[dep].get("sha256") for dep in dependency_closure(ident)):
                    errors.append("stale transitive dependency review " + r["id"] + " for " + ident)
                elif any(r.get("evidence_hashes", {}).get(ev) != byid[ev].get("sha256") for ev in r.get("evidence_ids", []) if ev in byid):
                    errors.append("stale evidence review " + r["id"] + " for " + ident)
                elif r.get("reviewer_id") and r.get("evidence_ids"):
                    passed.add(ident)
                else: errors.append("pass review requires evidence " + r["id"])
    for c in records["claims"]:
        if c.get("status") not in {"hypothesis", "observed", "blocked"}: errors.append("invalid claim status")
        if c.get("status") == "observed" and not c.get("evidence_ids"):
            errors.append("observed claim without evidence " + c.get("id", ""))
        elif c.get("status") == "observed" and any(c.get("evidence_hashes", {}).get(ev) != byid[ev].get("sha256") for ev in c.get("evidence_ids", []) if ev in byid):
            errors.append("stale observed claim evidence " + c.get("id", ""))
    for u in m.get("upstream", []):
        if not u.get("package_id") or not HEX.fullmatch(str(u.get("manifest_sha256", ""))) or not u.get("schema_version"):
            errors.append("invalid upstream provenance")
    model_report = None
    actual_model_gate, acceptance_scope = None, None
    if m.get("stage") != "studio":
        model_ref = m.get("game_model")
        if not isinstance(model_ref, dict) or not model_ref.get("path"):
            if accepted:
                errors.append("Model-aware accepted package requires game_model path and current due evidence")
            else:
                warnings.append("Game model not linked; draft transport only")
        else:
            try:
                model_path = safe_path(root, model_ref["path"])
                if not model_path.is_file() or sha(model_path) != model_ref.get("sha256"):
                    raise ValueError("missing/stale game_model bytes")
                checker_path = Path(__file__).absolute().parent / "game_model.py"
                if checker_path.is_symlink() or not checker_path.is_file():
                    raise ValueError("game model checker missing/linked")
                checker = types.ModuleType("atelier_game_model")
                checker.__file__ = str(checker_path)
                exec(compile(checker_path.read_bytes(), str(checker_path), "exec", dont_inherit=True), checker.__dict__)
                gate, acceptance_scope = model_gate(m)
                actual_model_gate = gate
                if acceptance_scope != "full_stage":
                    scope_ids = {x["id"] for x in records["requirements"] + records["decisions"]}
                    if model_ref["scope_ref"] not in scope_ids:
                        raise ValueError("scope_ref must resolve to a package requirement or decision")
                model_data = read_json(model_path)
                if model_data.get("schema_version") != "4.0.0":
                    raise ValueError("current handoff requires game-model schema4.0.0")
                model_report = checker.validate(model_data, model_path.parent, stage=gate, design_only=not accepted)
                if accepted and model_report.get("maturity") == "C0":
                    raise ValueError("C0 sketch cannot be an accepted concept/handoff")
                model_report["acceptance_scope"] = acceptance_scope
                model_report["scope_ref"] = model_ref.get("scope_ref")
                model_report["scope_is_product_release"] = m.get("stage") == "release" or acceptance_scope == "release_change"
                if not model_report.get("structurally_valid"):
                    errors.append("invalid game model: " + "; ".join(model_report.get("errors", [])))
                if accepted and not model_report.get("stage_ready"):
                    errors.append("game model due gate not ready: " + gate)
            except (OSError, ValueError, TypeError, KeyError) as error:
                errors.append("game model validation failed: " + str(error))
    if accepted:
        kinds = {a.get("kind") for a in artifacts if a.get("status") in {"final", "reference"}}
        for kind in profile["kinds"]:
            if kind not in kinds: errors.append("missing required kind " + kind)
        if not records["requirements"]: errors.append("accepted scope requires explicit requirements")
        for r in records["requirements"]:
            if r.get("status") == "not_applicable":
                if not r.get("rationale"): errors.append("N/A requires rationale " + r["id"])
            elif r.get("status") != "met" or not r.get("artifact_ids") or not r.get("evidence_ids"):
                errors.append("unmet/unsupported requirement " + r["id"])
            if not r.get("acceptance") or not r.get("owner") or r.get("owner") == "pending":
                errors.append("undefined requirement " + r["id"])
        for d in records["decisions"]:
            if d.get("material") and (d.get("status") != "confirmed" or not d.get("answer") or not d.get("authority_ref")):
                errors.append("unconfirmed material decision " + d["id"])
        decision_ids = {d["id"] for d in records["decisions"] if d.get("material") is True and d.get("status") == "confirmed"}
        for ident in profile["decisions"]:
            if ident not in decision_ids: errors.append("missing confirmed decision " + ident)
        for a in artifacts:
            if a.get("status") in {"final", "reference"} and a.get("kind") not in EXEMPT and a["id"] not in passed:
                errors.append("no current independent review " + a["id"])
    else:
        warnings.append("Draft/blocked transport validity is not stage acceptance")
    current_ready = (not errors and accepted and current_work and m.get("toolkit_version") == TOOLKIT_VERSION
                     and (m.get("stage") == "studio" or production_choices is not None))
    return {"valid": not errors, "toolkit_version": m.get("toolkit_version"), "current_toolkit_ready": current_ready,
            "production_choices": production_choices, "historical_inspection": accepted and not current_work,
            "stage": m.get("stage"), "stage_status": m.get("stage_status"),
            "errors": sorted(set(errors)), "warnings": warnings, "game_model_report": model_report, "model_gate": actual_model_gate, "acceptance_scope": acceptance_scope, "required_artifact_kinds": profile["kinds"], "required_decision_ids": profile["decisions"], "quality_certified": False}

def impact(root, changed):
    m = read_json(root / "manifest.json")
    ids = {a["id"] for a in m["artifacts"]}
    if changed not in ids: raise ValueError("unknown changed artifact " + changed)
    affected = {changed}
    while True:
        more = {a["id"] for a in m["artifacts"] if set(a.get("depends_on", [])) & affected}
        if more <= affected: break
        affected |= more
    records = read_json(root / "records/reviews.json")["items"]
    return {"affected_artifacts": sorted(affected), "invalidate_reviews": [r["id"] for r in records if set(r.get("artifact_ids", [])) & affected], "mutated": False}

def unzip(archive, dest):
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if len(infos) > 50000 or sum(i.file_size for i in infos) > 2 * 1024**3:
            raise ValueError("archive exceeds safety limits")
        names = set()
        for info in infos:
            if info.filename in names: raise ValueError("duplicate ZIP path")
            names.add(info.filename)
            name = info.filename.rstrip("/")
            target = safe_path(dest, name)
            if stat.S_ISLNK(info.external_attr >> 16): raise ValueError("ZIP symlink forbidden")
            if info.is_dir(): target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, target.open("wb") as out:
                    while chunk := src.read(1024 * 1024): out.write(chunk)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "seal", "verify", "pack", "impact", "status"):
        p = sub.add_parser(command); p.add_argument("path", type=Path)
        if command == "init": p.add_argument("--stage", choices=KINDS, required=True); p.add_argument("--project-id", required=True)
        if command == "verify":
            p.add_argument("--require-accepted", action="store_true")
            p.add_argument("--historical", action="store_true", help="Inspect historical package evidence without current admission")
        if command in {"verify", "pack"}:
            p.add_argument("--project-root", type=Path, help="Project owning the current production choice; defaults to the package")
        if command == "pack": p.add_argument("--output", type=Path, required=True)
        if command == "impact": p.add_argument("--changed", required=True)
    args = parser.parse_args()
    root = args.path.resolve()
    try:
        if args.command == "init": init(root, args.stage, args.project_id); return 0
        if args.command == "seal": seal(root); return 0
        if args.command == "impact": print(json.dumps(impact(root, args.changed), indent=2)); return 0
        if args.command == "status":
            m = read_json(root / "manifest.json")
            print(json.dumps({k: m.get(k) for k in ("project_id", "stage", "revision", "stage_status", "upstream")}, indent=2)); return 0
        if root.is_file():
            if args.command != "verify": raise ValueError("only verify accepts an archive")
            with tempfile.TemporaryDirectory() as tmp:
                unpacked = Path(tmp)
                unzip(root, unpacked)
                result = verify(unpacked, args.require_accepted, current_work=not args.historical,
                                project_root=args.project_root)
        else:
            result = verify(root, getattr(args, "require_accepted", False),
                            current_work=not getattr(args, "historical", False), project_root=args.project_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["valid"]: return 1
        if args.command == "pack":
            output = args.output.resolve()
            if output.is_relative_to(root): raise ValueError("output ZIP must be outside package")
            if output.exists(): raise ValueError("refusing to overwrite existing ZIP")
            output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
                for path in [root / "manifest.json"] + inventory(root): z.write(path, path.relative_to(root))
            print(json.dumps({"output": str(output), "sha256": sha(output), "stage_accepted": result["stage_status"] == "accepted"}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}), file=sys.stderr); return 2

if __name__ == "__main__":
    sys.exit(main())
