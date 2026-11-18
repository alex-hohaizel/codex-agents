#!/usr/bin/env python3
"""Game Atelier project state and gates; internal to an agent, never an executor.

The agent supplies structured intent and records actual tool/human evidence. This
stdlib runtime does not interpret natural language, execute commands, access a
store, schedule jobs, or certify artistic/product quality. See each subcommand's
help. JSON input files can be '-' for stdin. Exit 0 = recorded/read, 1 = blocked,
2 = invalid request. Readiness is a gate, not approval to cause an external effect.
"""
import argparse
import copy
import datetime as dt
import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
fcntl = platform_support
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import types
import zipfile
from contextlib import contextmanager
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


TOOLKIT_VERSION = "6.0.0"
RUNTIME_SCHEMA_VERSION = "2.0.0"
VERSION = TOOLKIT_VERSION  # Public tool-version marker; state schema is separate.
HANDOFF_PROTOCOL = "1.0.0"
STAGES = ("studio", "concepts", "preproduction", "assets", "build", "qa", "release", "liveops")
GROUPS = ("requirements", "knowledge", "artifacts", "evidence", "decisions", "tasks", "capabilities", "actions")
SCRIPT_ROOT = Path(__file__).resolve().parent
PRODUCTION_STAGES = {"preproduction", "assets", "build", "qa", "release"}
REVIEW_OPERATIONS = {"design_review", "contract_review"}
# Historical source versions are deliberate migration inputs, not display
# metadata. Never replace these entries while bumping TOOLKIT_VERSION.
WORKFLOW_UPGRADE_FROM = {"5.0.0": {"4.2.0", "4.3.0"},
                         "6.0.0": {"4.2.0", "4.3.0", "5.0.0"}}
ACTION_TYPES = {"purchase", "upload", "deploy", "store_write", "account", "signature", "legal", "destructive", "public_effect", "schedule", "monitor"}
EVIDENCE_MODALITIES = frozenset({"visual", "audio", "haptic", "play", "device", "build", "document", "external_receipt"})
MAX_FILES, MAX_BYTES = 10000, 256 * 1024 * 1024
HEX = re.compile(r"^[0-9a-f]{64}$")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(record, *names):
    require(isinstance(record, dict), "record must be an object")
    for name in names:
        require(name in record and record[name] not in (None, "", []), "missing/nonempty field: " + name)


def strings(value, field):
    require(isinstance(value, list) and all(isinstance(x, str) and x for x in value), field + " must be an array of nonempty strings")
    return value


def task_modalities(record):
    require(isinstance(record, dict), "task record must be an object")
    values = strings(record.get("required_modalities", []), "required_modalities")
    require(set(values) <= EVIDENCE_MODALITIES, "unsupported required_modalities: " + ", ".join(sorted(set(values) - EVIDENCE_MODALITIES)))
    return values


def stage_of(record):
    require(record.get("stage") in STAGES, "explicit valid stage required")
    if "stages" in record:
        values = strings(record["stages"], "stages")
        require(values and len(values) == len(set(values)) and set(values) <= set(STAGES) | {"all"}, "stages must contain unique valid stage IDs or all")
    if "scope" in record:
        require(isinstance(record["scope"], str) and record["scope"].strip(), "scope must be nonempty text")
    return record["stage"]


def safe_path(root, name):
    require(isinstance(name, str), "relative path must be text")
    if platform_support.WINDOWS: platform_support.safe_relative(name)
    pure = PurePosixPath(name)
    require(name and "\\" not in name and ":" not in name and not pure.is_absolute()
            and ".." not in pure.parts and name == pure.as_posix(), "unsafe/noncanonical relative path: " + name)
    target = root.joinpath(*pure.parts)
    require(target.resolve().is_relative_to(root.resolve()), "path escapes root: " + name)
    require(not any(platform_support.is_link_or_reparse(root.joinpath(*pure.parts[:i])) for i in range(1, len(pure.parts) + 1)), "symlink forbidden: " + name)
    return target


def public_path(root, name):
    require(bool(PurePosixPath(name).parts), "nonempty project artifact path required")
    require(PurePosixPath(name).parts[0] != ".gameatelier", "project artifact cannot modify canonical project/runtime state")
    return safe_path(root, name)


def suite_lock():
    """Pin executable code and the shared normative contract, not local UI/docs.

    Every standalone stage carries the same declared shared resources. Its own
    stage-local guides remain source provenance, rather than changing the common
    runtime identity whenever a task moves to another stage entrypoint. All
    executable Python is still pinned byte-for-byte, including added helpers.
    """
    result = {}
    base = SCRIPT_ROOT.parent
    names = {"scripts/atelier.py", "scripts/pipeline.py", "assets/stage-catalog.json", "references/experience-contract.md"}
    declaration = base / "assets/suite-shared-paths.json"
    if declaration.is_file():
        require(not platform_support.is_link_or_reparse(declaration), "shared suite declaration cannot be linked")
        paths = strict_json_loads(declaration.read_text(encoding="utf-8")).get("paths")
        strings(paths, "shared suite paths")
        require(len(paths) == len(set(paths)), "shared suite paths must be unique")
        names.add("assets/suite-shared-paths.json")
        for name in paths:
            safe_path(base, name)
            if not any(part in {"tests", "__pycache__"} for part in PurePosixPath(name).parts):
                names.add(name)
    else:
        # A bounded synthetic/minimal runtime has no full-suite declaration.
        # Pin all its data/contract bytes; an installed suite requires the
        # declaration through check_suite.py before installation acceptance.
        for folder, suffix in (("references", ".md"), ("assets", ".json")):
            names.update(path.relative_to(base).as_posix() for path in (base / folder).rglob("*" + suffix))
    for path in (base / "scripts").rglob("*.py"):
        if not any(part in {"tests", "__pycache__"} for part in path.relative_to(base).parts):
            names.add(path.relative_to(base).as_posix())
    for name in sorted(names):
        path = safe_path(base, name)
        result[name] = sha(path) if path.is_file() else None
    return result


def suite_sources():
    """Raw local source provenance; changes never disappear behind a UI label."""
    base = SCRIPT_ROOT.parent
    return {p.relative_to(base).as_posix(): sha(p) for p in sorted(base.rglob("*"))
            if p.is_file() and p.suffix in {".py", ".md", ".json", ".yaml"}
            and not any(part in {"tests", "__pycache__"} for part in p.relative_to(base).parts)
            and not platform_support.is_link_or_reparse(p)}


def canonical_sources(root):
    result = {}
    for name in ("state", "decisions", "requirements", "toolchain", "capabilities", "sync-lock"):
        relative = ".gameatelier/" + name + ".json"
        path = safe_path(root, relative)
        if path.is_file():
            result[relative] = sha(path)
    return result


def canonical_rows(root, name):
    path = safe_path(root, ".gameatelier/" + name + ".json")
    if not path.is_file():
        return {}
    data = strict_json_loads(path.read_text(encoding="utf-8"))
    rows = data.get("items", data.get(name, data)) if isinstance(data, dict) else data
    if isinstance(rows, dict):
        return {key: value for key, value in rows.items() if isinstance(value, dict)}
    require(isinstance(rows, list), "unsupported canonical " + name + " shape; explicit adapter required")
    return {row["id"]: row for row in rows if isinstance(row, dict) and row.get("id")}


def canonical_binding(root, name, ident):
    """Pin a typed fragment plus global envelope, retaining the whole-file hash.

    Explicit items/name containers have a distinct global envelope. Bare maps
    and unfamiliar record fields remain conservative whole-document bindings:
    the runtime must not guess that an unknown field has no dependency effect.
    """
    path = safe_path(root, ".gameatelier/" + name + ".json")
    if not path.is_file():
        return None
    data = strict_json_loads(path.read_text(encoding="utf-8"))
    container = next((key for key in ("items", name) if isinstance(data, dict) and key in data), None)
    if container:
        raw = data[container]
        envelope = {"container": container, "container_type": type(raw).__name__,
                    "global": {key: value for key, value in data.items() if key != container}}
    elif isinstance(data, list):
        raw, envelope = data, {"container": "root-list"}
    else:
        raw, envelope = data, {"opaque_document": data}
    if isinstance(raw, list):
        require(all(isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"] for row in raw), "canonical records need typed unique IDs")
        require(len({row["id"] for row in raw}) == len(raw), "duplicate canonical record IDs")
        rows = {row["id"]: row for row in raw}
    elif isinstance(raw, dict):
        rows = {key: value for key, value in raw.items() if isinstance(value, dict)}
        require(all(value.get("id", key) == key for key, value in rows.items()), "canonical map ID differs from record ID")
    else:
        raise ValueError("unsupported canonical record container; explicit adapter required")
    row = rows.get(ident)
    if row is None:
        return None
    known = set("id source stage stages scope status depends_on version owner record_type canonical_ref canonical_sha256".split())
    if name == "requirements":
        known |= set("verbatim_source intent priority acceptance artifact_ids evidence_ids closure definition_revision closure_snapshot".split())
    elif name == "decisions":
        known |= set("question options consequences recommendation explanation material effect approved_sha256 approval approval_artifact_hashes answer authority_ref confirmed_project_revision decision_revision imported_authority author_ids".split())
    else:
        envelope = {"opaque_document": data}
    if set(row) - known:
        envelope = {"opaque_document": data}
    approval = row.get("approval")
    if isinstance(approval, dict) and set(approval) - {"option", "effects", "artifact_ids"}:
        envelope = {"opaque_document": data}
    return {"record_sha256": digest(row), "envelope_sha256": digest(envelope), "source_sha256": sha(path)}


def fragment_matches(record, binding):
    return bool(binding and record.get("canonical_record_sha256") == binding["record_sha256"]
                and record.get("canonical_envelope_sha256") == binding["envelope_sha256"])


def link_canonical(root, record, name):
    existing = canonical_rows(root, name).get(record["id"])
    if existing is not None:
        expected = ".gameatelier/" + name + ".json#" + record["id"]
        require(record.get("canonical_ref") == expected, "existing canonical ID requires exact canonical_ref: " + expected)
        binding = canonical_binding(root, name, record["id"])
        require(record.get("canonical_sha256") == binding["source_sha256"] or fragment_matches(record, binding), "canonical record/envelope hash differs; reconcile authoritative source")
        record["canonical_record_sha256"] = binding["record_sha256"]
        record["canonical_envelope_sha256"] = binding["envelope_sha256"]
        record["canonical_observed_sha256"] = binding["source_sha256"]
    if existing is not None:
        if name == "requirements":
            for key in ("source", "verbatim_source", "intent", "stage", "stages", "scope", "owner", "acceptance", "depends_on", "artifact_ids", "evidence_ids", "closure"):
                if key in existing:
                    require(record.get(key) == existing[key], "canonical requirement field cannot be overridden: " + key)
            for key, default in (("priority", "must"), ("status", "pending")):
                require(record.get(key) == existing.get(key, default), "canonical requirement authority cannot be downgraded/overridden: " + key)
        if name == "decisions":
            for key in ("stages", "depends_on", "material"):
                if key in existing and key not in record:
                    record[key] = copy.deepcopy(existing[key])
            for key in ("stage", "stages", "scope", "depends_on", "material", "question", "options", "consequences", "effect", "approved_sha256", "approval", "approval_artifact_hashes"):
                if key in existing:
                    require(record.get(key) == existing[key], "canonical decision authority differs: " + key)
                elif key in {"effect", "approved_sha256", "approval"}:
                    require(key not in record, "cannot add authority absent from canonical decision: " + key)
        if name == "decisions" and set(existing.get("approval", {}).get("effects", [])) & ACTION_TYPES:
            require(existing.get("approval_artifact_hashes"), "canonical external authority requires original approved artifact hashes")
    return existing


def load_input(path):
    if str(path) == "-":
        return strict_json_loads(sys.stdin.read(256 * 1024 * 1024 + 1))
    return strict_json_loads(Path(path).read_text(encoding="utf-8"))


@contextmanager
def locked(root):
    require(not platform_support.is_link_or_reparse(root), "project directory cannot be a symlink")
    root.mkdir(parents=True, exist_ok=True)
    container = root / ".gameatelier"
    require(not platform_support.is_link_or_reparse(container), "canonical project directory cannot be a symlink")
    container.mkdir(exist_ok=True)
    home = container / "orchestrator"
    require(not platform_support.is_link_or_reparse(home), "runtime directory cannot be a symlink")
    home.mkdir(exist_ok=True)
    if platform_support.WINDOWS: platform_support.make_private(home)
    fd = os.open(home / "lock", os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield home
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def read_state(home, accepted_toolkits=None):
    path = home / "state.json"
    require(path.is_file() and not platform_support.is_link_or_reparse(path), "project not initialized or state is a symlink")
    state = strict_json_loads(path.read_text(encoding="utf-8"))
    require(state.get("schema_version") == RUNTIME_SCHEMA_VERSION, "unsupported runtime schema; create a current project state from current inputs")
    require(state.get("toolkit_version") in (accepted_toolkits or {TOOLKIT_VERSION}), "unsupported toolkit result; use an explicit supported workflow-upgrade or reconstruct a current state from current inputs")
    previous = None
    for seq, event in enumerate(state["journal"], 1):
        expected = dict(event)
        event_hash = expected.pop("hash", None)
        require(event.get("seq") == seq and event.get("previous") == previous and digest(expected) == event_hash, "journal integrity failure")
        previous = event_hash
    require(state.get("snapshot_hash") == digest({k: v for k, v in state.items() if k != "snapshot_hash"}), "snapshot integrity failure; restore an intact checkpoint")
    return state


def save_state(home, state, command, details):
    state["revision"] += 1
    event = {"seq": len(state["journal"]) + 1, "at": now(), "command": command, "details": details,
             "knowledge_revision": state["knowledge_revision"], "previous": state["journal"][-1]["hash"] if state["journal"] else None}
    event["hash"] = digest(event)
    state["journal"].append(event)
    state["snapshot_hash"] = digest({k: v for k, v in state.items() if k != "snapshot_hash"})
    fd, name = tempfile.mkstemp(prefix="state-", dir=home)
    try:
        if platform_support.WINDOWS: platform_support.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as out:
            out.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, home / "state.json")
        platform_support.sync_dir(home)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def workflow_upgrade(state, home, root, args):
    """Preview/apply an exact reviewed metadata upgrade; never replay work.

    Only the same native state schema and an explicit from→to map are supported.
    The user/agent supplies the actual review authority; these bindings cannot
    authenticate human intent or certify the project under a new tool version.
    """
    source_bytes = (home / "state.json").read_bytes()
    require(strict_json_loads(source_bytes) == state, "workflow source changed while reading; repeat preview")
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    target_lock = suite_lock()
    require(all(value is not None for value in target_lock.values()), "target shared runtime resources missing; repair installation before upgrade")
    target_sources = suite_sources()
    target_binding = digest({"toolkit_version": TOOLKIT_VERSION, "runtime_schema": RUNTIME_SCHEMA_VERSION,
                             "runtime_lock": target_lock, "delivery_sources": target_sources})
    source_version = state["toolkit_version"]
    allowed = WORKFLOW_UPGRADE_FROM.get(TOOLKIT_VERSION, set())
    current_version = source_version == TOOLKIT_VERSION
    require(current_version or source_version in allowed, "unsupported workflow upgrade path; no automatic conversion of unrelated formats")
    impact = sorted(set(args.impact))
    require(set(impact) <= set(nodes(state)), "unknown upgrade-impact ID")
    preview = {"ready": True, "preview": not args.apply, "project_id": state["project_id"],
               "from_toolkit": source_version, "to_toolkit": TOOLKIT_VERSION,
               "runtime_schema": RUNTIME_SCHEMA_VERSION, "source_state_sha256": source_hash,
               "source_snapshot_hash": state["snapshot_hash"], "target_suite_sha256": target_binding,
               "impact_ids": impact, "already_current": current_version,
               "pause": copy.deepcopy(state["pause"]),
               "unresolved_external_actions": sorted(ident for ident, row in state["actions"].items() if row.get("status") in {"pending", "unknown"}),
               "workflow_state_updated": False, "external_actions_executed": [], "product_files_changed": False,
               "limitations": "Preview/apply only workflow metadata. Historical acceptance remains scoped to its original evidence; the new toolkit does not certify it."}
    if not args.apply:
        return preview
    require(args.authority and args.authority.strip(), "workflow upgrade needs actual reviewed authority source")
    require(HEX.fullmatch(args.expected_state_hash or "") and HEX.fullmatch(args.target_suite_hash or ""), "apply needs exact preview --expected-state-hash and --target-suite-hash")
    require(args.target_suite_hash == target_binding, "target suite changed since review; repeat preview before apply")
    if current_version:
        replay = next((entry for entry in reversed(state.get("workflow_upgrades", []))
                       if entry.get("source_state_sha256") == args.expected_state_hash
                       and entry.get("target_suite_sha256") == args.target_suite_hash
                       and entry.get("authority_ref") == args.authority
                       and entry.get("impact_ids") == impact), None)
        require(replay is not None, "workflow is already current; use refresh for a new reviewed source change")
        return {**preview, "preview": False, "replayed": True, "backup_path": replay["backup_path"]}
    require(args.expected_state_hash == source_hash, "workflow state changed since preview; reread current state and repeat preview")
    # Validate actual originals/proofs against current files on a copy. A paused
    # project or an unresolved effect can be migrated, but remains paused/unknown.
    updated = copy.deepcopy(state)
    refresh(updated, root)
    require(not updated["integrity_errors"], "workflow upgrade blocked by changed/missing approved originals: " + "; ".join(updated["integrity_errors"]))
    backup_dir = home / "backups"
    require(not platform_support.is_link_or_reparse(backup_dir), "workflow backup directory cannot be linked")
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / ("workflow-" + source_version + "-r" + str(state["revision"]) + "-" + source_hash + ".json")
    if backup.exists():
        require(not platform_support.is_link_or_reparse(backup) and backup.read_bytes() == source_bytes, "existing workflow backup differs; reconcile before apply")
    else:
        fd = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(source_bytes)
            stream.flush()
            os.fsync(stream.fileno())
    require(sha(home / "state.json") == source_hash, "workflow state changed while backing up; repeat preview")
    require(digest({"toolkit_version": TOOLKIT_VERSION, "runtime_schema": RUNTIME_SCHEMA_VERSION,
                    "runtime_lock": suite_lock(), "delivery_sources": suite_sources()}) == target_binding,
            "target suite changed during upgrade; repeat preview")
    updated["toolkit_version"] = TOOLKIT_VERSION
    updated["suite_lock"] = target_lock
    updated["observed_suite_sources"] = target_sources
    updated["suite_mismatch"] = False
    updated["knowledge_revision"] += 1
    updated["last_reconciled_knowledge_revision"] = updated["knowledge_revision"]
    for ident in impact:
        row = nodes(updated)[ident][1]
        row["status"] = "stale"
        row.setdefault("stale_reasons", []).append("reviewed workflow upgrade " + source_version + " -> " + TOOLKIT_VERSION)
    affected = invalidate(updated, impact, "reviewed workflow upgrade affected dependency")
    receipt = {"from_toolkit": source_version, "to_toolkit": TOOLKIT_VERSION,
               "source_state_sha256": source_hash, "source_snapshot_hash": state["snapshot_hash"],
               "target_suite_sha256": target_binding, "authority_ref": args.authority,
               "impact_ids": impact, "affected_ids": affected,
               "backup_path": str(backup.relative_to(root)), "backup_sha256": source_hash,
               "previous_stage_checks_require_current_validation": list(range(len(state["stage_checks"]))),
               "at": now(), "external_actions_executed": []}
    updated.setdefault("workflow_upgrades", []).append(receipt)
    save_state(home, updated, "workflow-upgrade", receipt)
    return {**preview, "preview": False, "workflow_state_updated": True, "replayed": False,
            "backup_path": receipt["backup_path"], "affected_ids": affected,
            "current_state_sha256": sha(home / "state.json"), "project_revision": updated["revision"]}


def nodes(state):
    return {ident: (group, row) for group in GROUPS for ident, row in state[group].items()}


def token(row):
    if row.get("record_type") == "requirement":
        definition = {k: row.get(k) for k in ("id", "definition_revision", "source", "verbatim_source", "intent", "stage", "scope", "owner", "priority", "acceptance", "depends_on")}
        # The optional applicability extension changes a definition when used;
        # absence retains the exact existing native2.0 requirement fingerprint.
        if "stages" in row:
            definition["stages"] = row["stages"]
        return digest(definition)
    return digest({k: v for k, v in row.items() if k not in ("dependency_snapshot", "stale_reasons", "reconciled_knowledge_revision", "canonical_observed_sha256")})


def closure(state, identifiers):
    index = nodes(state)
    result, pending = set(), list(identifiers)
    while pending:
        ident = pending.pop()
        if ident in result:
            continue
        require(ident in index, "unknown dependency: " + ident)
        result.add(ident)
        pending.extend(index[ident][1].get("depends_on", []))
    return result


def snapshot(state, ids):
    index = nodes(state)
    return {ident: token(index[ident][1]) for ident in sorted(closure(state, ids))}


def invalidate(state, changed, reason):
    affected = set(changed)
    index = nodes(state)
    while True:
        following = {ident for ident, (_, row) in index.items() if set(row.get("depends_on", [])) & affected}
        if following <= affected:
            break
        affected |= following
    for ident in affected - set(changed):
        group, row = index[ident]
        if group in {"artifacts", "evidence", "decisions", "tasks", "requirements"}:
            if row.get("status") not in {"pending", "planned", "failed", "not_applicable"}:
                row["status"] = "stale"
            row.setdefault("stale_reasons", [])
            if reason not in row["stale_reasons"]:
                row["stale_reasons"].append(reason)
    return sorted(affected)


def put(state, group, record):
    fields(record, "id")
    require(isinstance(record["id"], str), "id must be text")
    index = nodes(state)
    require(record["id"] not in index or index[record["id"]][0] == group, "ID already used in another ledger")
    old = state[group].get(record["id"])
    record = copy.deepcopy(record)
    record["version"] = old.get("version", 0) + 1 if old else 1
    record.setdefault("depends_on", [])
    strings(record["depends_on"], "depends_on")
    require(record["id"] not in closure(state, record["depends_on"]), "dependency cycle")
    record["dependency_snapshot"] = snapshot(state, record["depends_on"])
    record["reconciled_knowledge_revision"] = state["knowledge_revision"]
    state[group][record["id"]] = record
    affected = invalidate(state, [record["id"]], "updated " + record["id"]) if old and token(old) != token(record) else [record["id"]]
    return record, affected


def applicable(row, stage, scope):
    stages = set(row.get("stages", [])) | {row.get("stage")}
    return (stage in stages or "all" in stages) and row.get("scope", "project") in {"project", scope}


def requirement_satisfied(state, ident):
    row = state["requirements"].get(ident, {})
    return current(state, ident, "requirements") and ((row.get("status") == "met" and requirement_proofs_cover(state, row)) or
            (row.get("status") == "not_applicable" and bool(row.get("closure"))))


def output_scope_matches(artifact, scope):
    """A project assembly can contain scoped outputs; other scopes stay bounded."""
    return scope == "project" or artifact.get("scope", "project") in {"project", scope}


def requirement_proofs_cover(state, row):
    scope = row.get("scope", "project")
    artifacts = row.get("artifact_ids", [])
    evidence = row.get("evidence_ids", [])
    if not artifacts or not evidence or any(not current(state, ident, "artifacts") or not output_scope_matches(state["artifacts"][ident], scope) for ident in artifacts):
        return False
    if any(not current(state, ident, "evidence") for ident in evidence):
        return False
    stages = set(row.get("stages", [])) | {row.get("stage")}
    stages = STAGES if "all" in stages else stages
    for stage in stages:
        covered = {artifact for ident in evidence if applicable(state["evidence"][ident], stage, scope)
                   for artifact in state["evidence"][ident].get("artifact_ids", [])}
        if not set(artifacts) <= covered:
            return False
    return bool(stages)


def review_operation(stage, operation):
    return stage == "qa" and operation in REVIEW_OPERATIONS


def production_operation(stage, operation):
    require(operation != "full_concepts" or stage == "concepts", "full_concepts is a concepts-stage operation")
    require(operation not in REVIEW_OPERATIONS or stage == "qa", "design_review/contract_review are QA operations")
    return operation == "production" or (stage in PRODUCTION_STAGES and not review_operation(stage, operation))


def refresh(state, root):
    changed = []
    state["integrity_errors"] = []
    state["suite_mismatch"] = suite_lock() != state["suite_lock"]
    state["observed_suite_sources"] = suite_sources()
    observed_canonical = canonical_sources(root)
    changed_canonical = {path for path in set(observed_canonical) | set(state.get("canonical_sources", {})) if observed_canonical.get(path) != state.get("canonical_sources", {}).get(path)}
    if changed_canonical:
        state["knowledge_revision"] += 1
        state["canonical_sources"] = observed_canonical
        for ident, (_, row) in nodes(state).items():
            path, _, canonical_id = row.get("canonical_ref", "").partition("#")
            if path in changed_canonical:
                name = PurePosixPath(path).stem
                binding = canonical_binding(root, name, canonical_id)
                if fragment_matches(row, binding):
                    # Retain the original approved source hash. Observed parent
                    # bytes are provenance, not a new authority or task input.
                    row["canonical_observed_sha256"] = binding["source_sha256"]
                    continue
                row["status"] = "stale"
                row.setdefault("stale_reasons", []).append("canonical fragment/envelope changed or lacks pins; relink exact current source")
                changed.append(ident)
    for ident, row in state["artifacts"].items():
        path = public_path(root, row["path"])
        observed = sha(path) if path.is_file() else None
        if observed != row.get("observed_sha256", row["sha256"]):
            row["observed_sha256"] = observed
            row["status"] = "stale"
            changed.append(ident)
        if observed != row["sha256"] and row.get("immutable"):
            state["integrity_errors"].append("approved original changed/missing: " + ident)
    for ident, row in state["evidence"].items():
        proof = public_path(root, row["proof_path"])
        observed = sha(proof) if proof.is_file() else None
        if observed != row["proof_sha256"] and row.get("status") != "stale":
            row["status"] = "stale"
            row.setdefault("stale_reasons", []).append("proof bytes changed/missing")
            changed.append(ident)
    for ident, row in state['tasks'].items():
        pins = row.get('consumed_sources')
        mismatched = (not isinstance(pins, dict) or
                      any(state['observed_suite_sources'].get(path) != expected for path, expected in pins.items()))
        if mismatched and row.get('status') != 'stale':
            row['status'] = 'stale'
            row.setdefault('stale_reasons', []).append('consumed operating source missing/changed; review context and record a new task')
            changed.append(ident)
    for row in state["actions"].values():
        receipt = row.get("receipt")
        if receipt:
            path = public_path(root, receipt["proof_path"])
            if not path.is_file() or sha(path) != receipt["proof_sha256"]:
                row["status"] = "unknown"
                row["reconciliation_reason"] = "receipt proof changed/missing; read-only provider reconciliation required"
    for intake in state["intakes"]:
        for item in intake["files"]:
            path = safe_path(root / ".gameatelier" / "orchestrator" / "intakes" / intake["id"] / "payload", item["path"])
            if not path.is_file() or sha(path) != item["sha256"]:
                state["integrity_errors"].append("imported original changed/missing: " + intake["id"] + "/" + item["path"])
    if changed:
        state["knowledge_revision"] += 1
        invalidate(state, changed, "source bytes changed: " + ",".join(changed))
    for group in ("evidence", "decisions", "tasks"):
        for row in state[group].values():
            if row.get("dependency_snapshot", {}) != snapshot(state, row.get("depends_on", [])):
                if row.get("status") not in {"pending", "planned", "failed"}:
                    row["status"] = "stale"
                if "dependency snapshot differs" not in row.setdefault("stale_reasons", []):
                    row["stale_reasons"].append("dependency snapshot differs")
    for ident, row in state["requirements"].items():
        if row.get("status") == "met" and not requirement_satisfied(state, ident):
            row["status"] = "stale"
            invalidate(state, [ident], "requirement closure proof stale: " + ident)
    for ident, row in state["tasks"].items():
        if row.get("status") == "completed" and row.get("completion_snapshot") != completion_snapshot(state, row):
            row["status"] = "stale"
            row.setdefault("stale_reasons", []).append("completed outputs/proofs changed")
            invalidate(state, [ident], "upstream task completion proof stale: " + ident)
    reconcile_choices(state)
    state["last_reconciled_knowledge_revision"] = state["knowledge_revision"]
    return changed


def global_blockers(state, work=True):
    result = list(state["integrity_errors"])
    if state["suite_mismatch"]:
        result.append("installed suite files changed; review and refresh --accept-suite-update --authority SOURCE")
    if work and state["pause"]["active"]:
        result.append("project paused at " + state["pause"]["reason"])
    return result


def current(state, ident, group=None):
    index = nodes(state)
    if ident not in index or (group and index[ident][0] != group):
        return False
    row = index[ident][1]
    if row.get("status") in {"stale", "pending", "planned", "failed", "fail", "unknown", "prepared", "superseded"} or row.get("stale_reasons"):
        return False
    if index[ident][0] == "tasks" and row.get("status") == "completed" and row.get("completion_snapshot") != completion_snapshot(state, row):
        return False
    if index[ident][0] == "requirements" and row.get("status") == "met":
        if row.get("closure_snapshot") != snapshot(state, row.get("artifact_ids", []) + row.get("evidence_ids", [])):
            return False
    return row.get("dependency_snapshot", {}) == snapshot(state, row.get("depends_on", []))


def reconcile_choices(state):
    stops = [row for ident, row in state["decisions"].items() if row.get("effect") == "stop_search" and current(state, ident, "decisions") and row.get("status") == "confirmed" and row.get("answer") == "stop"]
    choices = [row for ident, row in state["decisions"].items() if row.get("effect") == "production_choice" and current(state, ident, "decisions") and row.get("status") == "confirmed"]
    answers = {row["answer"] for row in choices if row.get("answer") != "none"}
    state["search_stopped"] = bool(stops)
    state["production_choice"] = next(iter(answers)) if stops and len(answers) == 1 else None
    state["choice_authority"] = {"stop_decisions": sorted(row["id"] for row in stops), "production_decisions": sorted(row["id"] for row in choices)}


def completion_snapshot(state, row):
    result = snapshot(state, row.get("artifact_ids", []) + row.get("completion_evidence", []))
    result.pop(row["id"], None)
    return result


def stage_context(state, stage, scope=None):
    result = {}
    for group in ("requirements", "knowledge", "decisions"):
        for ident, row in state[group].items():
            if (scope is None and (row.get("stage") == stage or stage in row.get("stages", []) or "all" in row.get("stages", []))) or (scope is not None and applicable(row, stage, scope)):
                result[ident] = token(row)
    return result


def approved_for(state, decision, effect, artifact_ids=None):
    approval = decision.get("approval", {})
    if decision.get("status") != "confirmed" or decision.get("answer") != approval.get("option") or effect not in approval.get("effects", []):
        return False
    if artifact_ids is not None:
        expected = {ident: state["artifacts"][ident]["sha256"] for ident in artifact_ids}
        return decision.get("approval_artifact_hashes") == expected
    return True


def readiness(state, task_id, phase="start"):
    require(task_id in state["tasks"], "unknown task")
    task = state["tasks"][task_id]
    blockers = global_blockers(state)
    pins = task.get('consumed_sources')
    if not isinstance(pins, dict) or any(state.get('observed_suite_sources', {}).get(path) != expected for path, expected in pins.items()):
        blockers.append('task consumed-source snapshot missing/changed; reconcile exact current context')
    try:
        task_modalities(task)
    except ValueError as exc:
        blockers.append(str(exc) + "; reconcile the legacy task modality contract before work")
    if task.get("status") == "stale" or task.get("stale_reasons"):
        blockers.append("task contract stale; re-record after reconciling context")
    for ident in task.get("depends_on", []):
        group, row = nodes(state)[ident]
        if group in {"artifacts", "evidence", "decisions", "tasks"} and (not current(state, ident) or (group == "tasks" and row.get("status") != "completed")):
            blockers.append("dependency not current: " + ident)
    for ident in task.get("required_decisions", []):
        if not current(state, ident, "decisions") or state["decisions"].get(ident, {}).get("status") != "confirmed":
            blockers.append("pending/stale decision: " + ident)
    requirements = set(task.get("required_requirements", [])) | {ident for ident, row in state["requirements"].items() if row.get("priority") == "must" and applicable(row, task["stage"], task["scope"])}
    if phase == "complete":
        requirements |= set(task.get("fulfills_requirements", []))
    for ident in sorted(requirements):
        row = state["requirements"].get(ident, {})
        if phase == "start" and ident in task.get("fulfills_requirements", []):
            continue
        if not requirement_satisfied(state, ident):
            blockers.append("unmet/unsupported must requirement: " + ident)
    for ident in task.get("required_evidence", []):
        if not current(state, ident, "evidence"):
            blockers.append("missing/stale evidence: " + ident)
    for ident in task.get("capabilities", []):
        row = state["capabilities"].get(ident, {})
        if row.get("available") is not True or row.get("scope") not in {"project", task["scope"]}:
            blockers.append("missing capability/manual bridge required: " + ident)
    for ident in task.get("external_actions", []):
        if state["actions"].get(ident, {}).get("status") != "succeeded":
            blockers.append("external outcome pending/unknown/failed: " + ident)
    if task["stage"] in PRODUCTION_STAGES and task.get("requires_production_choice") is False:
        intent = task.get("maintenance_intent", {})
        review = task.get("review_intent", {})
        valid_review = review_operation(task["stage"], task.get("operation")) and task.get("work_class") == "review" and all(review.get(key) == task.get(key) for key in ("stage", "scope", "source", "operation"))
        valid_maintenance = task.get("work_class") == "maintenance" and intent.get("kind") in {"incident", "feature"} and all(intent.get(key) == task.get(key) for key in ("stage", "scope", "source")) and intent.get("operation") not in {"production", "full_concepts"}
        if not valid_review and not valid_maintenance:
            blockers.append("production authority cannot be disabled by a task flag")
    if task.get("operation") == "production" and task.get("requires_production_choice") is not True:
        blockers.append("production operation cannot disable its authority gate")
    if task.get("requires_production_choice", production_operation(task["stage"], task.get("operation", "work"))) or task.get("operation") == "production":
        if not state["production_choice"] or not state["search_stopped"]:
            blockers.append("production choice absent or search not explicitly stopped; saved favorites are not selection")
    if task.get("status") == "completed":
        blockers.append("task already completed; no replay")
    return {"ready": not blockers, "task": task_id, "task_token": token(task), "task_status": task.get("status"), "blockers": sorted(set(blockers)), "knowledge_revision": state["knowledge_revision"]}


def reconcile_task_modalities(state, record):
    """Correct only unsupported modality names; preserve execution and authority."""
    fields(record, "id", "expected_task_token", "expected_status", "modality_replacements", "source", "reason")
    require(set(record) == {"id", "expected_task_token", "expected_status", "modality_replacements", "source", "reason"}, "modality reconciliation accepts only its exact correction fields")
    require(not global_blockers(state, work=False), "cannot reconcile against unresolved integrity/suite state")
    require(all(isinstance(record[name], str) and record[name].strip() for name in ("source", "reason")), "concrete correction source and reason must be nonempty text")
    row = state["tasks"].get(record["id"])
    require(row is not None, "unknown task")
    require(row.get("status") in {"planned", "running"} and record["expected_status"] == row["status"], "modality reconciliation requires the exact current planned/running task status")
    require(isinstance(record["expected_task_token"], str) and HEX.fullmatch(record["expected_task_token"]) and record["expected_task_token"] == token(row), "task token changed; reread readiness before modality reconciliation")
    original = strings(row.get("required_modalities", []), "legacy required_modalities")
    unsupported = set(original) - EVIDENCE_MODALITIES
    require(unsupported, "task has no unsupported modalities to reconcile")
    replacements = record["modality_replacements"]
    require(isinstance(replacements, dict) and set(replacements) == unsupported, "map exactly every unsupported modality; supported requirements cannot be changed")
    for old, values in replacements.items():
        strings(values, "replacement for " + old)
        require(values and len(values) == len(set(values)) and set(values) <= EVIDENCE_MODALITIES, "each unsupported modality needs unique supported replacements")
    linked = {ident for ident, action in state["actions"].items() if action.get("task") == row["id"]} | set(row.get("external_actions", []))
    unresolved = sorted(ident for ident in linked if ident not in state["actions"] or state["actions"][ident].get("status") in {"pending", "unknown"})
    require(not unresolved, "reconcile task-linked pending/unknown external outcomes first: " + ", ".join(unresolved))
    history = row.get("modality_reconciliations", [])
    require(isinstance(history, list), "invalid existing modality reconciliation history")
    corrected = [value for modality in original for value in replacements.get(modality, [modality])]
    row["required_modalities"] = corrected
    row["modality_reconciliations"] = history + [{"prior_task_token": record["expected_task_token"], "status": row["status"], "previous_modalities": original, "corrected_modalities": corrected, "modality_replacements": copy.deepcopy(replacements), "source": record["source"], "reason": record["reason"], "recorded_at": now()}]
    affected = invalidate(state, [row["id"]], "task modality contract reconciled: " + row["id"])
    return {"task": row, "task_token": token(row), "invalidated_dependents": [ident for ident in affected if ident != row["id"]], "actual_execution": False, "completed": False, "next": "Reread readiness; record only actual applicable proof. This correction neither repeats work nor grants execution permission."}


def stop_boundary(state, kind, target):
    pause = state["pause"]
    if not pause["active"] and pause.get("when") == kind and pause.get("target") == target:
        pause.update(active=True, reason="after " + kind + " " + target, reached_at=now())


def import_source(state, root, source, provenance):
    fields(provenance, "id", "source", "rights", "authority_ref")
    require(re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", provenance["id"]) is not None, "intake id must be a safe slug")
    require(not platform_support.is_link_or_reparse(source), "source symlink forbidden")
    require(not source.is_file() or source.stat().st_size <= MAX_BYTES, "source archive exceeds compressed size limit")
    require(not source.resolve().is_relative_to((root / ".gameatelier/orchestrator").resolve()) and not root.resolve().is_relative_to(source.resolve()), "intake source cannot contain or be runtime state")
    archive_sha = sha(source) if source.is_file() else None
    for old in state["intakes"]:
        if old["id"] == provenance["id"]:
            require(old["provenance"] == provenance and old.get("archive_sha256") == archive_sha, "intake ID already used with different provenance/source")
            if archive_sha is None:
                require(directory_inventory(source) == old["files"], "intake ID already used with changed source directory")
            return {"intake": old["id"], "replayed": True, "executed": False}
    destination = root / ".gameatelier" / "orchestrator" / "intakes" / provenance["id"]
    require(not destination.exists(), "untracked intake destination exists; reconcile without overwriting")
    with tempfile.TemporaryDirectory(prefix="intake-", dir=root / ".gameatelier" / "orchestrator") as temp:
        payload = Path(temp) / "payload"
        payload.mkdir()
        if source.is_dir():
            listing = directory_inventory(source)
            require(len(listing) <= MAX_FILES and sum(x["bytes"] for x in listing) <= MAX_BYTES, "source exceeds resource limits")
            for item in listing:
                target = safe_path(payload, item["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(safe_path(source, item["path"]), target)
        else:
            require(source.is_file(), "source must exist")
            safe_unzip(source, payload)
        listing = directory_inventory(payload)
        for master in provenance.get("approved_masters", []):
            fields(master, "path", "sha256", "approval_scope", "authority_ref")
            require(sha(safe_path(payload, master["path"])) == master["sha256"], "approved master hash mismatch")
        destination.parent.mkdir(exist_ok=True)
        os.replace(temp, destination)
        state["intakes"].append({"id": provenance["id"], "provenance": copy.deepcopy(provenance), "archive_sha256": archive_sha, "files": listing, "executed": False})
    state["knowledge_revision"] += 1
    return {"intake": provenance["id"], "files": len(listing), "archive_sha256": archive_sha, "executed": False, "production_choice_changed": False}


def directory_inventory(source):
    files = []
    total = 0
    require(source.is_dir() and not platform_support.is_link_or_reparse(source), "source directory required; symlink forbidden")
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source).as_posix()
        safe_path(source, relative)
        require(not platform_support.is_link_or_reparse(path), "symlink forbidden")
        if path.is_dir():
            continue
        require(path.is_file(), "nonregular source forbidden")
        parts = PurePosixPath(relative).parts
        require(".git" not in parts and not (path.name.startswith(".env") and path.name != ".env.example") and path.suffix.lower() not in {".p12", ".p8", ".jks", ".keystore", ".mobileprovision"}, "private/signing/repository file forbidden: " + relative)
        size = path.stat().st_size
        total += size
        require(len(files) < MAX_FILES and total <= MAX_BYTES, "source exceeds resource limits")
        files.append({"path": relative, "sha256": sha(path), "bytes": size})
    return files


def safe_unzip(source, destination):
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        require(len(infos) <= MAX_FILES and sum(x.file_size for x in infos) <= MAX_BYTES, "archive exceeds resource limits")
        names = set()
        for item in infos:
            name = item.filename.rstrip("/")
            safe_path(destination, name)
            require(name not in names, "duplicate ZIP path")
            names.add(name)
            mode = item.external_attr >> 16
            require(not stat.S_ISLNK(mode), "ZIP symlink forbidden")
            require(stat.S_IFMT(mode) in {0, stat.S_IFREG, stat.S_IFDIR}, "nonregular ZIP member forbidden")
            require(not item.flag_bits & 1, "encrypted ZIP member forbidden")
            require(item.file_size <= MAX_BYTES and (item.file_size < 1024 * 1024 or item.file_size <= max(1, item.compress_size) * 1000), "ZIP expansion ratio exceeds limit")
        for item in infos:
            target = safe_path(destination, item.filename.rstrip("/"))
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as src, target.open("xb") as out:
                    copied = 0
                    for chunk in iter(lambda: src.read(1024 * 1024), b""):
                        copied += len(chunk)
                        require(copied <= item.file_size and copied <= MAX_BYTES, "ZIP member expanded beyond declared size")
                        out.write(chunk)


def record_ledger(state, kind, record):
    if kind == "requirement":
        fields(record, "id", "source", "verbatim_source", "intent", "stage", "owner", "status", "priority", "acceptance")
        stage_of(record)
        require(record["status"] in {"pending", "met", "not_applicable"} and record["priority"] in {"must", "should", "could"}, "invalid requirement status/priority")
        for name in ("depends_on", "artifact_ids", "evidence_ids"):
            strings(record.get(name, []), name)
        if record["status"] == "met":
            fields(record, "closure", "artifact_ids", "evidence_ids")
            require(all(current(state, x, "artifacts") for x in record["artifact_ids"]) and all(current(state, x, "evidence") for x in record["evidence_ids"]), "met requirement requires current actual artifacts and evidence")
            covered = {artifact for ident in record["evidence_ids"] for artifact in state["evidence"][ident]["artifact_ids"]}
            require(set(record["artifact_ids"]) <= covered, "requirement closure evidence must cover its exact artifacts")
            require(requirement_proofs_cover(state, record), "requirement closure proof must cover its declared stages/scope and output scope")
        if record["status"] == "not_applicable":
            fields(record, "closure")
        record["depends_on"] = record.get("depends_on", [])
        state["knowledge_revision"] += 1
        previous = state["requirements"].get(record["id"], {})
        definition_keys = ("source", "verbatim_source", "intent", "stage", "stages", "scope", "owner", "priority", "acceptance", "depends_on")
        same_definition = bool(previous) and all(previous.get(k) == record.get(k) for k in definition_keys)
        record["record_type"] = "requirement"
        record["definition_revision"] = previous.get("definition_revision", 1) if same_definition else previous.get("definition_revision", 0) + 1
        record["closure_snapshot"] = snapshot(state, record.get("artifact_ids", []) + record.get("evidence_ids", [])) if record["status"] == "met" else {}
        return put(state, "requirements", record)
    fields(record, "id", "source", "verbatim_source", "text", "scope", "confidence", "stages", "impact_reason")
    strings(record["stages"], "stages")
    require(set(record["stages"]) <= set(STAGES) | {"all"}, "unknown applicable stage")
    require(record["confidence"] in {"hypothesis", "observed", "confirmed"}, "invalid knowledge confidence")
    strings(record.get("impact_ids", []), "impact_ids")
    for ident in record.get("impact_ids", []):
        require(ident in nodes(state), "unknown impact ID: " + ident)
    record["status"] = "recorded"
    state["knowledge_revision"] += 1
    result, affected = put(state, "knowledge", record)
    impacted = set(record.get("impact_ids", []))
    for ident, (group, row) in nodes(state).items():
        if ident != record["id"] and group in {"tasks", "artifacts", "evidence", "decisions"} and applicable(record, row.get("stage"), row.get("scope")):
            impacted.add(ident)
    for ident in impacted:
        row = nodes(state)[ident][1]
        if record["id"] not in closure(state, row.get("depends_on", [])):
            require(ident not in closure(state, record.get("depends_on", [])), "knowledge applicability would create dependency cycle; scope impact explicitly")
            row.setdefault("depends_on", []).append(record["id"])
    affected = sorted(set(affected) | set(invalidate(state, [record["id"]], "project lesson " + record["id"] + ": " + record["impact_reason"])))
    return result, affected


def brief(state, root):
    lines = ["Game Atelier: " + state["project_id"], "Project revision %s; knowledge revision %s" % (state["revision"], state["knowledge_revision"]),
             "Project: " + str(root), "Pause: " + canonical(state["pause"]),
             "Production concept: " + str(state["production_choice"]) + "; search stopped: " + str(state["search_stopped"]),
             "Saved favorites (not selection): " + ", ".join(x["id"] for x in state["favorites"]),
             "Completed: " + ", ".join(x for x, r in state["tasks"].items() if r["status"] == "completed"),
             "Current jobs: " + ", ".join(x + " (" + r["status"] + ")" for x, r in state["tasks"].items() if r["status"] != "completed"),
             "Pending decisions: " + ", ".join(x for x, r in state["decisions"].items() if r["status"] != "confirmed"),
             "External actions requiring reconciliation: " + ", ".join(x for x, r in state["actions"].items() if r["status"] in {"pending", "unknown"})]
    lines += ["Blocker: " + x for x in global_blockers(state, work=False)]
    lines += ["Next action: use context and readiness for the exact task; execute only actual available tools after gates pass.",
              "Return: python3 " + str(SCRIPT_ROOT / "atelier.py") + " brief " + str(root),
              "Resume: python3 " + str(SCRIPT_ROOT / "atelier.py") + " resume " + str(root)]
    if state.get("bridges"):
        lines.append("Latest manual bridge: " + canonical(state["bridges"][-1]))
    return "\n".join(lines) + "\n"


def dispatch(state, root, args):
    command = args.command
    record = args._task_record if hasattr(args, "_task_record") else load_input(args.record) if getattr(args, "record", None) else None
    args._record = copy.deepcopy(record)
    if command == "intake":
        return import_source(state, root, args.source, record)
    if command == "route":
        intent = load_input(args.intent)
        fields(intent, "kind", "stage", "scope", "source")
        stage_of(intent)
        require(intent["kind"] in {"new_project", "stage", "feature", "incident", "research", "resume", "intake"}, "kind must be an explicit structured intent; agent interprets natural language")
        blockers = global_blockers(state)
        needs_choice = production_operation(intent["stage"], intent.get("operation", "work"))
        # Ordinary stage routing is planning. Explicit production operations are
        # gated here; all actual production tasks are gated again at readiness.
        if intent.get("operation") == "production" and (not state["search_stopped"] or not state["production_choice"]):
            blockers.append("explicit stop-search and chosen production concept required")
        state["current_intent"] = intent
        return {"ready": not blockers, "blockers": blockers, "stage": intent["stage"], "skill": "gamedev-" + intent["stage"], "scope": intent["scope"], "requires_production_choice": needs_choice, "partial_route": intent["kind"] in {"feature", "incident"}, "next": "Read actual stage skill, record bounded task, run readiness; runtime does not invoke skill/tools."}
    if command == "ledger":
        if args.kind == "requirement":
            link_canonical(root, record, "requirements")
        row, affected = record_ledger(state, args.kind, record)
        return {"record": row, "affected_ids": affected}
    if command == "artifact":
        require(not global_blockers(state), "artifact work blocked: " + "; ".join(global_blockers(state)))
        fields(record, "id", "path", "stage", "scope", "kind", "author_ids", "status")
        stage_of(record)
        strings(record["author_ids"], "author_ids")
        require(record["status"] in {"draft", "final", "reference"}, "artifact status must be draft/final/reference; acceptance is a separate exact decision")
        path = public_path(root, record["path"])
        require(path.is_file(), "artifact bytes missing")
        old = state["artifacts"].get(record["id"])
        if old and old.get("immutable"):
            require(old["path"] == record["path"] and old["sha256"] == sha(path), "accepted original immutable; create a new derivative ID")
            require(record.get("approval_decision") == old.get("approval_decision"), "accepted original approval cannot be removed/replaced")
        record["sha256"] = record["observed_sha256"] = sha(path)
        record["immutable"] = False
        if record.get("approval_decision"):
            decision = state["decisions"].get(record["approval_decision"], {})
            require(current(state, record["approval_decision"], "decisions") and decision.get("status") == "confirmed" and decision["scope"] == record["scope"], "current exact-scope approval decision required")
            require(approved_for(state, decision, "master"), "confirmed option does not approve master acceptance")
            require(decision.get("approved_sha256") == record["sha256"], "approval must name exact original bytes via approved_sha256")
            record["immutable"] = True
        if record["kind"] == "visual_preview" and not old:
            limit = state.get("constraints", {}).get("visual_preview_limit")
            require(limit is None or sum(a.get("kind") == "visual_preview" for a in state["artifacts"].values()) < limit, "visual preview boundary reached; explicit new scope decision required")
        record["depends_on"] = sorted(set(record.get("depends_on", []) + [x for x, k in state["knowledge"].items() if applicable(k, record["stage"], record["scope"])]))
        row, affected = put(state, "artifacts", record)
        if row["status"] in {"final", "reference"}:
            stop_boundary(state, "artifact", row["id"])
        return {"artifact": row, "affected_ids": affected}
    if command == "evidence":
        fields(record, "id", "source", "stage", "scope", "modality", "artifact_ids", "observer", "status")
        stage_of(record)
        require(record["status"] in {"observed", "pass", "fail"}, "evidence must record an actual observation/review; no synthesized pass")
        strings(record["artifact_ids"], "artifact_ids")
        require(all(current(state, x, "artifacts") for x in record["artifact_ids"]), "evidence references missing/stale artifacts")
        require(all(output_scope_matches(state["artifacts"][ident], record["scope"]) for ident in record["artifact_ids"]), "evidence scope contradicts covered artifact scope")
        require(record["modality"] in EVIDENCE_MODALITIES, "explicit supported evidence modality required")
        if record["status"] == "pass":
            require(all(record["observer"] not in state["artifacts"][x].get("author_ids", []) for x in record["artifact_ids"]), "independent review cannot be authored by artifact author")
        fields(record, "proof_path")
        proof = public_path(root, record["proof_path"])
        require(proof.is_file(), "actual proof file required; text claim alone does not create a modality proof")
        if record["modality"] == "audio":
            require(proof.suffix.lower() in {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".aiff", ".mp4", ".webm"}, "audio proof must include actual audio media; a text description is insufficient")
        if record["modality"] == "visual":
            require(proof.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm", ".pdf"}, "visual proof must include actual rendered/captured media")
        if record["modality"] != "document":
            fields(record, "environment", "observed_at", "method")
        record["proof_sha256"] = sha(proof)
        record["depends_on"] = sorted(set(record.get("depends_on", []) + record["artifact_ids"]))
        return {"evidence": put(state, "evidence", record)[0], "certifies_quality": False, "observation_is_agent_recorded": True}
    if command == "decision":
        fields(record, "id", "source", "stage", "scope", "question", "options", "consequences", "recommendation", "explanation")
        stage_of(record)
        strings(record["options"], "options")
        require(record["recommendation"] in record["options"] and isinstance(record["consequences"], dict) and set(record["options"]) <= set(record["consequences"]), "each option needs consequences and recommendation must be an option")
        require(record.get("effect") in {None, "stop_search", "production_choice"}, "unsupported decision effect")
        approval = record.get("approval")
        if approval is not None:
            fields(approval, "option", "effects")
            strings(approval["effects"], "approval.effects")
            require(approval["option"] in record["options"] and set(approval["effects"]) <= ACTION_TYPES | {"master"}, "explicit approving option/effects required")
            if set(approval["effects"]) & ACTION_TYPES:
                fields(approval, "artifact_ids")
                strings(approval["artifact_ids"], "approval.artifact_ids")
                require(all(current(state, ident, "artifacts") for ident in approval["artifact_ids"]), "approval requires actual current reviewable artifacts")
                record["approval_artifact_hashes"] = {ident: state["artifacts"][ident]["sha256"] for ident in approval["artifact_ids"]}
                record["depends_on"] = sorted(set(record.get("depends_on", []) + approval["artifact_ids"]))
        if record.get("approved_sha256"):
            require(approval and "master" in approval["effects"] and HEX.fullmatch(record["approved_sha256"]), "exact master approval requires explicit approving option/effect and SHA256")
        canonical_authority = link_canonical(root, record, "decisions")
        record["status"] = "pending"
        record["decision_revision"] = state["decisions"].get(record["id"], {}).get("decision_revision", 0) + 1
        for key in ("answer", "authority_ref", "confirmed_project_revision"):
            record.pop(key, None)
        if canonical_authority and canonical_authority.get("status") == "confirmed":
            require(canonical_authority.get("scope") == record["scope"] and canonical_authority.get("answer") in record["options"] and canonical_authority.get("authority_ref"), "canonical confirmed authority scope/answer/reference mismatch")
            record.update(status="confirmed", answer=canonical_authority["answer"], authority_ref=canonical_authority["authority_ref"], imported_authority=True)
            if record.get("effect") == "stop_search":
                pass
            if record.get("effect") == "production_choice":
                require(state["search_stopped"] or record["answer"] == "none", "import stop-search authority before production-choice authority")
                pass
        for ident, previous in state["decisions"].items():
            if ident != record["id"] and record.get("effect") and previous.get("effect") == record["effect"] and previous.get("scope") == record["scope"]:
                previous["status"] = "superseded"
                invalidate(state, [ident], "replacement decision " + record["id"])
        row = put(state, "decisions", record)[0]
        reconcile_choices(state)
        return {"decision": row, "approval_granted": False, "existing_canonical_authority_preserved": bool(canonical_authority)}
    if command == "confirm":
        require(not global_blockers(state, work=False), "cannot confirm against unresolved integrity/suite state")
        row = state["decisions"].get(args.id)
        require(row is not None, "unknown decision")
        canonical_authority = link_canonical(root, row, "decisions")
        require(canonical_authority is None or (canonical_authority.get("status") == "confirmed" and canonical_authority.get("answer") == args.choice and canonical_authority.get("scope") == args.scope and canonical_authority.get("authority_ref") == args.authority), "canonical decision must contain this exact confirmed authority first; preserve one authority by updating canonical source and relinking")
        if row.get("status") == "confirmed" and row.get("answer") == args.choice and row.get("authority_ref") == args.authority and row["scope"] == args.scope and row["decision_revision"] == args.decision_revision and row.get("confirmed_project_revision") == args.project_revision:
            return {"decision": row, "replayed": True}
        require(args.project_revision == state["revision"], "wrong project revision; reread current concrete decision")
        require(args.decision_revision == row["decision_revision"] and args.scope == row["scope"], "wrong decision revision or approval scope")
        require(args.choice in row["options"], "answer is not an offered option")
        require(row.get("status") != "stale" and not row.get("stale_reasons") and row["dependency_snapshot"] == snapshot(state, row["depends_on"]), "stale decision; re-record concrete options")
        if row.get("effect") == "production_choice":
            require(state["search_stopped"], "stop search explicitly before production choice")
            pass
        if row.get("effect") == "stop_search":
            pass
        row.update(status="confirmed", answer=args.choice, authority_ref=args.authority, confirmed_project_revision=args.project_revision)
        invalidate(state, [args.id], "decision confirmed " + args.id)
        reconcile_choices(state)
        return {"decision": row, "approval_scope": row["scope"]}
    if command == "task":
        fields(record, "id", "stage", "scope", "source", "goal", "owner", "skill")
        stage_of(record)
        task_modalities(record)
        available_sources = suite_sources()
        consumed = record.get('consumed_sources', available_sources)
        require(isinstance(consumed, dict) and all(isinstance(path, str) and HEX.fullmatch(str(value)) for path, value in consumed.items()), 'consumed_sources must map exact relative operating paths to SHA256')
        require(all(available_sources.get(path) == value for path, value in consumed.items()), 'consumed operating source differs from supplied task context')
        record['consumed_sources'] = dict(consumed)
        require(record["skill"] == "gamedev-" + record["stage"], "task must name the actual stage skill")
        intent = state.get("current_intent", {})
        same_route = intent.get("stage") == record["stage"] and intent.get("scope") == record["scope"]
        if same_route and intent.get("operation") in {"full_concepts", "production"} | REVIEW_OPERATIONS:
            require(intent.get("source") == record["source"], "task source must preserve exact current material operation intent")
            require(record.get("operation", intent["operation"]) == intent["operation"], "task cannot downgrade current material operation intent")
            record["operation"] = intent["operation"]
        else:
            record.setdefault("operation", intent.get("operation", "work") if same_route and intent.get("source") == record["source"] else "work")
        production_operation(record["stage"], record["operation"])
        if record["operation"] == "production":
            require(record.get("requires_production_choice") is not False, "production operations require current stop-search and production authority")
            record["requires_production_choice"] = True
        if review_operation(record["stage"], record["operation"]):
            require(record.get("work_class") not in {"production", "maintenance"}, "review operation cannot be relabeled production/maintenance")
            require(not record.get("external_actions"), "bounded design/contract review cannot dispatch external effects")
            record["work_class"] = "review"
            record["requires_production_choice"] = False
            record["review_intent"] = {key: record[key] for key in ("stage", "scope", "source", "operation")}
        elif record["stage"] in PRODUCTION_STAGES:
            intent = state.get("current_intent", {})
            partial = intent.get("kind") in {"incident", "feature"} and intent.get("stage") == record["stage"] and intent.get("scope") == record["scope"] and intent.get("source") == record["source"] and intent.get("operation") not in {"production", "full_concepts"} and record.get("work_class") != "production"
            require(record.get("requires_production_choice") is not False or partial, "production stages cannot disable production authority; only an exact matching incident/feature route permits a partial maintenance task")
            if partial and record.get("requires_production_choice") is False:
                record["maintenance_intent"] = copy.deepcopy(intent)
            record["work_class"] = "maintenance" if partial and record.get("requires_production_choice") is False else "production"
            record["requires_production_choice"] = record["work_class"] == "production"
        old = state["tasks"].get(record["id"], {})
        require(old.get("status") not in {"completed", "running"}, "running/completed task cannot be reset; use a new derivative task ID or reconcile stale task")
        for name in ("required_decisions", "required_requirements", "fulfills_requirements", "required_evidence", "capabilities", "artifact_ids", "external_actions", "required_modalities"):
            strings(record.get(name, []), name)
        record["depends_on"] = sorted(set(record.get("depends_on", []) + [x for group in ("knowledge", "requirements") for x, k in state[group].items() if applicable(k, record["stage"], record["scope"])]))
        record["status"] = "planned"
        return {"task": put(state, "tasks", record)[0]}
    if command == "reconcile-task-modalities":
        return reconcile_task_modalities(state, record)
    if command in {"readiness", "start", "complete"}:
        result = readiness(state, args.task, "complete" if command == "complete" else "start")
        if command == "readiness" or not result["ready"]:
            return result
        task = state["tasks"][args.task]
        if command == "start":
            require(task["status"] == "planned", "task already started; do not replay execution")
            task["status"] = "running"
            task["started_at"] = now()
            return {"started": args.task, "actual_execution": False, "next": "Agent uses actual skill/tools within task contract."}
        require(task["status"] == "running", "start task before recording completion")
        require(args.evidence, "completion requires actual evidence")
        require(all(current(state, x, "evidence") and state["evidence"][x]["status"] != "fail" for x in args.evidence), "completion evidence missing/stale/failed")
        require(all(applicable(state["evidence"][ident], task["stage"], task["scope"]) for ident in args.evidence), "completion evidence must apply to the task stage/scope; record explicit multi-stage applicability for shared proof")
        require(all(current(state, x, "artifacts") and state["artifacts"][x]["status"] in {"final", "reference"} for x in task.get("artifact_ids", [])), "task outputs missing/stale/draft")
        require(all(output_scope_matches(state["artifacts"][ident], task["scope"]) for ident in task.get("artifact_ids", [])), "task output scope contradicts the task scope")
        covered = {a for x in args.evidence for a in state["evidence"][x]["artifact_ids"]}
        require(set(task.get("artifact_ids", [])) <= covered, "completion proof must cover the task's actual outputs")
        provided = {state["evidence"][x]["modality"] for x in args.evidence}
        require(set(task.get("required_modalities", [])) <= provided, "required actual modality proofs missing")
        if task.get("independent_review_required"):
            require(all(state["evidence"][ident]["status"] == "pass" for ident in args.evidence), "task requires actual independent pass reviews")
        task.update(status="completed", completion_evidence=args.evidence, completed_at=now())
        task["completion_snapshot"] = completion_snapshot(state, task)
        invalidate(state, [args.task], "upstream task completed; reconcile completion proof " + args.task)
        return {"completed": args.task, "quality_certified": False}
    if command == "capability":
        fields(record, "id", "source", "scope", "environment", "verified_at")
        require(type(record.get("available")) is bool, "available must be an actual observed boolean")
        record["status"] = "available" if record["available"] else "unavailable"
        return {"capability": put(state, "capabilities", record)[0]}
    if command == "action":
        fields(record, "id", "idempotency_key", "type", "scope", "source", "decision_id", "decision_revision", "capability_id", "environment", "prepared_artifact_ids", "task")
        require(record["type"] in {"purchase", "upload", "deploy", "store_write", "account", "signature", "legal", "destructive", "public_effect", "schedule", "monitor"}, "explicit external action type required")
        require(record["task"] in state["tasks"], "action requires a bounded task contract")
        require(state["tasks"][record["task"]]["scope"] == record["scope"], "external action must remain in exact bounded task scope")
        for old in state["actions"].values():
            if old["idempotency_key"] == record["idempotency_key"] or old["id"] == record["id"]:
                comparison = {k: v for k, v in old.items() if k in record}
                require(comparison == record, "duplicate action/idempotency key with changed parameters")
                return {"action": old, "replayed": True, "actual_execution": False}
        strings(record["prepared_artifact_ids"], "prepared_artifact_ids")
        require(all(current(state, x, "artifacts") for x in record["prepared_artifact_ids"]), "prepare actual reviewable artifacts before external action")
        record["depends_on"] = sorted(set(record.get("depends_on", []) + record["prepared_artifact_ids"] + [record["decision_id"], record["capability_id"]]))
        record["status"] = "prepared"
        return {"action": put(state, "actions", record)[0], "actual_execution": False}
    if command == "dispatch":
        row = state["actions"].get(args.id)
        require(row is not None, "unknown action")
        require(row["status"] == "prepared", "action already dispatched/terminal/unknown; reconcile, never replay")
        require(args.project_revision == state["revision"], "wrong project revision for dispatch")
        require(state["tasks"][row["task"]]["status"] == "running", "start the bounded action task before dispatch")
        blockers = readiness(state, row["task"])["blockers"]
        blockers = [x for x in blockers if x != "external outcome pending/unknown/failed: " + args.id]
        require(not blockers, "action task blocked: " + "; ".join(blockers))
        require(not any(a["status"] in {"pending", "unknown"} for a in state["actions"].values()), "pending/unknown external outcome must be reconciled before another dispatch")
        decision = state["decisions"].get(row["decision_id"], {})
        capability = state["capabilities"].get(row["capability_id"], {})
        require(current(state, row["decision_id"], "decisions") and decision.get("status") == "confirmed" and decision["scope"] == row["scope"] and decision["decision_revision"] == row["decision_revision"], "exact current action approval required")
        require(approved_for(state, decision, row["type"], row["prepared_artifact_ids"]), "confirmed option does not approve this exact effect and artifact set")
        require(capability.get("available") is True and capability["environment"] == row["environment"] and capability["scope"] in {"project", row["scope"]}, "actual exact-environment capability unavailable; use handoff")
        expected_snapshot = snapshot(state, row["depends_on"])
        require({k: v for k, v in row["dependency_snapshot"].items() if k != row["decision_id"]} == {k: v for k, v in expected_snapshot.items() if k != row["decision_id"]}, "prepared action stale; prepare a new action and review its exact scope")
        row["dependency_snapshot"] = expected_snapshot
        row.update(status="pending", dispatched_at=now())
        return {"action": row, "actual_execution": False, "next": "Agent may now perform exactly the approved action once using actual capability; immediately record provider receipt. Crash/no receipt remains pending and requires read-only reconciliation."}
    if command == "receipt":
        row = state["actions"].get(args.id)
        require(row is not None, "unknown action")
        fields(record, "source", "provider_ref", "proof_path")
        proof = public_path(root, record["proof_path"])
        require(proof.is_file(), "real provider/read-only reconciliation proof file required")
        receipt = dict(record, outcome=args.outcome, proof_sha256=sha(proof))
        if row.get("receipt") == receipt:
            return {"action": row, "replayed": True}
        require(row["status"] in {"pending", "unknown"}, "terminal/prepared action cannot receive a conflicting receipt")
        require(row["status"] != "unknown" or (record.get("reconciled") is True and args.outcome != "unknown"), "unknown outcome requires explicit read-only reconciliation proof; no retry")
        row.setdefault("receipt_history", []).append(receipt)
        row.update(status=args.outcome, receipt=receipt)
        return {"action": row, "replayed": False}
    if command == "pause":
        require(args.when == "now" or not state["pause"]["active"], "active pause must be explicitly resumed before arming a future boundary")
        require(args.when == "now" or args.target, "artifact/stage pause requires exact target")
        if args.when == "stage":
            require(args.target in STAGES, "pause stage target must be a stage ID")
        if args.when == "artifact":
            require(args.target not in state["artifacts"], "artifact already exists; pause now or choose next derivative ID")
        state["pause"] = {"active": args.when == "now", "when": args.when, "target": args.target, "reason": "user pause now" if args.when == "now" else "waiting for exact boundary", "requested_at": now()}
        return {"pause": state["pause"], "checkpoint": brief(state, root)}
    if command == "resume":
        blockers = global_blockers(state, work=False)
        blockers += ["reconcile external outcome before resume: " + x for x, r in state["actions"].items() if r["status"] in {"pending", "unknown"}]
        if blockers:
            return {"ready": False, "blockers": blockers, "replayed_actions": []}
        state["pause"] = {"active": False, "when": None, "target": None, "reason": "explicit resume", "resumed_at": now()}
        return {"ready": True, "replayed_actions": [], "next": "Refresh context and task readiness; completed tasks/actions are never automatically repeated."}
    if command == "refresh":
        if args.accept_suite_update:
            require(args.authority, "suite update acceptance requires concrete review source")
            changed_files = [x for x, h in suite_lock().items() if state["suite_lock"].get(x) != h]
            state["suite_lock"] = suite_lock()
            state["suite_mismatch"] = False
            state["knowledge_revision"] += 1
            impacted = set(args.impact)
            index = nodes(state)
            require(impacted <= set(index), "unknown suite-impact ID")
            for ident in impacted:
                row = index[ident][1]
                row["status"] = "stale"
                row.setdefault("stale_reasons", []).append("review updated suite contract: " + ",".join(changed_files))
            invalidate(state, impacted, "review updated suite contract: " + ",".join(changed_files))
            state.setdefault("suite_updates", []).append({"files": changed_files, "impact_ids": sorted(impacted), "authority_ref": args.authority, "at": now()})
        return {"knowledge_revision": state["knowledge_revision"], "suite_mismatch": state["suite_mismatch"], "integrity_errors": state["integrity_errors"], "reconciled": True}
    if command == "context":
        terms = set((args.query or "").casefold().split())
        selected = []
        for ident, (group, row) in nodes(state).items():
            if args.stage and row.get("stage") != args.stage and args.stage not in row.get("stages", []) and "all" not in row.get("stages", []):
                continue
            score = sum(term in canonical(row).casefold() for term in terms)
            if not terms or score:
                selected.append((score, ident, group, row))
        selected.sort(key=lambda item: (-item[0], item[1]))
        ids = {x[1] for x in selected[:args.limit]}
        ids |= closure(state, ids)
        return {"retrieval": "structured stage filter + lexical terms + dependency closure", "knowledge_revision": state["knowledge_revision"], "suite_lock": state["suite_lock"], "observed_suite_sources": state.get("observed_suite_sources", {}), "stage_context_snapshot": stage_context(state, args.stage, args.scope) if args.stage else None, "canonical_sources": state.get("canonical_sources", {}), "items": [{"group": nodes(state)[x][0], **nodes(state)[x][1]} for x in sorted(ids)], "blockers": global_blockers(state, work=False)}
    if command == "brief":
        return brief(state, root)
    if command == "handoff":
        fields(record, "id", "environment", "working_path", "command", "expected_result", "return_path", "return_instructions", "scope", "missing_capability", "launch_steps")
        require(Path(record["working_path"]).is_absolute() and Path(record["return_path"]).is_absolute(), "manual bridge working/return paths must be absolute")
        strings(record["command"], "command argv")
        strings(record["launch_steps"], "launch_steps")
        require(not any(x["id"] == record["id"] for x in state["bridges"]), "manual bridge ID already used; preserve history")
        state["bridges"].append(record)
        return brief(state, root) + "\nMANUAL BRIDGE (not executed)\n" + json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if command == "stage-check":
        require(not global_blockers(state), "stage check blocked before loading validator: " + "; ".join(global_blockers(state)))
        package = args.package.resolve()
        require(package.is_dir(), "stage-check uses an already safely imported/created package directory")
        manifest = strict_json_loads((package / "manifest.json").read_text(encoding="utf-8"))
        if args.require_accepted or manifest.get("stage_status") == "accepted":
            stage = manifest.get("stage")
            require(stage in STAGES, "unknown package stage")
            scope = manifest.get("scope", "project")
            require(isinstance(scope, str) and scope.strip(), "package scope must be nonempty text")
            require(manifest.get("project_id") == state["project_id"], "stage package belongs to another project")
            package_requirements = {row["id"]: row for row in strict_json_loads(safe_path(package, "records/requirements.json").read_text(encoding="utf-8"))["items"]}
            package_decisions = {row["id"]: row for row in strict_json_loads(safe_path(package, "records/decisions.json").read_text(encoding="utf-8"))["items"]}
            for ident, row in state["requirements"].items():
                if applicable(row, stage, scope) and row.get("priority") == "must":
                    require(requirement_satisfied(state, ident), "current project must requirement blocks stage: " + ident)
                    exported = package_requirements.get(ident)
                    require(exported is not None, "package omits applicable current project must requirement: " + ident)
                    require(all(exported.get(key) == row.get(key) for key in ("status", "owner", "acceptance")), "package reinterprets current project must requirement: " + ident)
            for ident, row in state["decisions"].items():
                if applicable(row, stage, scope) and row.get("material", True) and row.get("status") != "superseded":
                    require(row.get("status") == "confirmed" and current(state, ident, "decisions"), "current project decision blocks stage: " + ident)
                    exported = package_decisions.get(ident)
                    require(exported is not None and all(exported.get(key) == row.get(key) for key in ("status", "answer", "authority_ref")), "package omits/reinterprets current project decision: " + ident)
            required_context = stage_context(state, stage, scope)
            require(not required_context or manifest.get("project_context") == required_context, "package lacks current project_context; use context --stage and reconcile package records/reviews before resealing")
        # Execute exactly the bytes whose digest is pinned, never a loader's .pyc
        # cache. Import loaders may accept timestamp-valid stale bytecode and may
        # write __pycache__ into an otherwise immutable installed skill tree.
        pipeline_path = SCRIPT_ROOT / "pipeline.py"
        require(not platform_support.is_link_or_reparse(pipeline_path), "bundled validator source cannot be a symlink")
        pipeline_source = pipeline_path.read_bytes()
        require(hashlib.sha256(pipeline_source).hexdigest() == state["suite_lock"].get("scripts/pipeline.py"), "bundled validator changed after suite preflight")
        module = types.ModuleType("atelier_pipeline")
        module.__file__ = str(pipeline_path)
        module.__package__ = ""
        module.__cached__ = None
        exec(compile(pipeline_source, str(pipeline_path), "exec", dont_inherit=True), module.__dict__)
        if manifest.get("toolkit_version") == TOOLKIT_VERSION and manifest.get("stage") != "studio":
            model_source = SCRIPT_ROOT / "game_model.py"
            require(model_source.is_file() and not platform_support.is_link_or_reparse(model_source), "game model checker missing/linked")
            require(sha(model_source) == state["suite_lock"].get("scripts/game_model.py"), "game model checker changed after suite preflight")
        result = module.verify(package, args.require_accepted)
        if result["valid"] and args.require_accepted:
            require(suite_lock() == state["suite_lock"], "installed suite changed during validator execution; reconcile before accepting stage")
            require(not global_blockers(state), "cannot cross stage boundary while paused/integrity blocked")
            manifest_path = package / "manifest.json"
            manifest = strict_json_loads(manifest_path.read_text(encoding="utf-8"))
            require(manifest["project_id"] == state["project_id"], "stage package belongs to another project")
            state["stage_checks"].append({"stage": result["stage"], "scope": manifest.get("scope", "project"), "toolkit_version": TOOLKIT_VERSION, "runtime_suite_sha256": digest(state["suite_lock"]), "manifest_path": str(manifest_path), "manifest_sha256": sha(manifest_path), "knowledge_revision": state["knowledge_revision"], "model_gate": result.get("model_gate"), "acceptance_scope": result.get("acceptance_scope"), "at": now()})
            stop_boundary(state, "stage", result["stage"])
        return result
    raise ValueError("unsupported command")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    descriptions = {
        "project-init": "Create a local project, preserving optional intake seed as history; no production authorization.",
        "intake": "Safely copy ZIP/directory originals and provenance; never execute imported scripts.",
        "route": "Route explicit JSON intent (kind/stage/scope/source); the agent interprets natural language.",
        "ledger": "Version requirement or project lesson; attach dependencies and invalidate impacted outputs.",
        "artifact": "Register actual project-relative bytes/hash; exact approved originals remain immutable.",
        "evidence": "Record actual proof file, modality, artifacts and observer; never certifies product quality.",
        "decision": "Prepare concrete exact-scope options/consequences; remains pending until confirm.",
        "confirm": "Record actual user authority against exact scope, decision and project revisions.",
        "task": "Record bounded task and actual stage skill; explicit dependencies and modality requirements.",
        "reconcile-task-modalities": "Correct only unsupported modalities on an exact legacy planned/running task; no work/replay/closeout.",
        "readiness": "Reconcile actual hashes/knowledge; report blocking requirements, choices and outcomes.",
        "start": "Gate a planned task once; agent performs actual tools separately.",
        "complete": "Close a running task with current actual evidence; no automatic next stage.",
        "capability": "Record observed tool/environment availability; absence requires a manual bridge.",
        "action": "Prepare an exact external action/idempotency key; no execution.",
        "dispatch": "Journal pending before agent executes one approved effect; never retries on crash.",
        "receipt": "Record actual provider outcome/proof; unknown requires read-only reconciliation.",
        "pause": "Checkpoint now, or stop at exact artifact registration/accepted stage boundary.",
        "resume": "Reconcile safely; refuses pending/unknown effects and never replays actions/tasks.",
        "refresh": "Reconcile files and suite hashes; optionally acknowledge a reviewed suite update.",
        "context": "Retrieve stage/lexical records and their dependency closure, with current revisions.",
        "brief": "Readable completed/current/pending/next/return checkpoint.",
        "handoff": "Record concrete manual bridge environment/path/argv/expected/return instructions.",
        "stage-check": "Delegate handoff acceptance to bundled authoritative pipeline.py; no quality certification.",
        "workflow-upgrade": "Preview/apply a supported reviewed native workflow-state upgrade; no product mutation or effect replay.",
    }
    for command, description in descriptions.items():
        p = sub.add_parser(command, help=description, description=description)
        p.add_argument("project", type=Path, help="Project directory; state lives in .gameatelier/orchestrator/state.json")
        if command == "project-init":
            p.add_argument("--project-id", required=True)
            p.add_argument("--seed", type=Path, help="Preserved imported project metadata; favorites remain saved only")
        if command in {"intake", "ledger", "artifact", "evidence", "decision", "task", "reconcile-task-modalities", "capability", "action", "receipt", "handoff"}:
            p.add_argument("--record", required=True, help="JSON object file, or '-' for stdin; see runtime-records.json asset")
        if command == "intake":
            p.add_argument("--source", type=Path, required=True)
        if command == "route":
            p.add_argument("--intent", required=True, help="JSON object file, or '-' for stdin")
        if command == "ledger":
            p.add_argument("--kind", choices=("requirement", "knowledge"), required=True)
        if command == "confirm":
            p.add_argument("--id", required=True)
            p.add_argument("--choice", required=True)
            p.add_argument("--scope", required=True)
            p.add_argument("--decision-revision", type=int, required=True)
            p.add_argument("--project-revision", type=int, required=True)
            p.add_argument("--authority", required=True, help="Concrete actual user decision/source reference; never generated approval")
        if command in {"readiness", "start", "complete"}:
            p.add_argument("--task", required=True)
        if command == "complete":
            p.add_argument("--evidence", action="append", default=[], help="Current actual evidence ID; repeat for modalities")
        if command in {"dispatch", "receipt"}:
            p.add_argument("--id", required=True)
        if command == "dispatch":
            p.add_argument("--project-revision", type=int, required=True)
        if command == "receipt":
            p.add_argument("--outcome", required=True, choices=("succeeded", "failed", "unknown"))
        if command == "pause":
            p.add_argument("--when", required=True, choices=("now", "artifact", "stage"))
            p.add_argument("--target", help="Exact artifact ID or stage ID for after-boundary pause")
        if command == "refresh":
            p.add_argument("--accept-suite-update", action="store_true")
            p.add_argument("--authority", help="Actual review source for a current project decision")
            p.add_argument("--impact", action="append", default=[], help="Exact record ID invalidated by reviewed suite change; repeat; omit for verified compatible cleanup")
        if command == "context":
            p.add_argument("--stage", choices=STAGES)
            p.add_argument("--scope", help="Exact package/task scope; project requirements also apply")
            p.add_argument("--query", help="Lexical query only; never used as an intent classifier")
            p.add_argument("--limit", type=int, default=40)
        if command == "stage-check":
            p.add_argument("--package", type=Path, required=True)
            p.add_argument("--require-accepted", action="store_true")
        if command == "workflow-upgrade":
            p.add_argument("--apply", action="store_true", help="Default is read-only preview; apply requires both exact preview bindings and authority")
            p.add_argument("--authority", help="Actual source of the reviewed upgrade permission")
            p.add_argument("--expected-state-hash", help="Exact source_state_sha256 returned by preview")
            p.add_argument("--target-suite-hash", help="Exact target_suite_sha256 returned by preview")
            p.add_argument("--impact", action="append", default=[], help="Exact IDs invalidated by reviewed semantic impact; repeat; unrelated proofs retained")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = args.project.absolute()
    try:
        with locked(root) as home:
            if args.command == "project-init":
                require(not (home / "state.json").exists(), "project already initialized; resume existing state")
                require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", args.project_id) is not None, "project-id must be a lowercase slug")
                seed = load_input(args.seed) if args.seed else {}
                require(isinstance(seed, dict), "seed must be an object")
                require(not seed.get("production_choice"), "seed cannot silently authorize production choice; record imported exact authority as an explicit decision")
                favorites = seed.get("favorites", [])
                require(isinstance(favorites, list), "favorites must be an array")
                normalized = [{"id": x if isinstance(x, str) else x["id"], "status": "saved_only"} for x in favorites]
                state = {"schema_version": RUNTIME_SCHEMA_VERSION, "toolkit_version": TOOLKIT_VERSION, "handoff_protocol": HANDOFF_PROTOCOL, "project_id": args.project_id, "revision": 0, "knowledge_revision": 1,
                         "suite_lock": suite_lock(), "observed_suite_sources": suite_sources(), "suite_mismatch": False, "canonical_sources": canonical_sources(root), "seed_history": seed, "favorites": normalized,
                         "production_choice": None, "search_stopped": False, "constraints": seed.get("constraints", {}),
                         "pause": {"active": False, "when": None, "target": None, "reason": "new project"},
                         "intakes": [], "bridges": [], "stage_checks": [], "integrity_errors": [], "journal": [],
                         "last_reconciled_knowledge_revision": 1, **{name: {} for name in GROUPS}}
                save_state(home, state, "project-init", {"project_id": args.project_id, "seed": seed})
                result = {"project": str(root), "project_revision": state["revision"], "knowledge_revision": 1, "production_choice": None, "favorites": normalized, "imported_master_bytes_verified": False}
            elif args.command == "workflow-upgrade":
                accepted_versions = WORKFLOW_UPGRADE_FROM.get(TOOLKIT_VERSION, set()) | {TOOLKIT_VERSION}
                state = read_state(home, accepted_toolkits=accepted_versions)
                result = workflow_upgrade(state, home, root, args)
            else:
                state = read_state(home)
                if args.command == "task":
                    # Reject an unrecordable contract before even persisting a
                    # routine refresh; stdin is consumed exactly once.
                    args._task_record = load_input(args.record)
                    task_modalities(args._task_record)
                original = copy.deepcopy(state)
                refresh(state, root)
                refreshed = copy.deepcopy(state)
                try:
                    result = dispatch(state, root, args)
                    reconcile_choices(state)
                except Exception:
                    if refreshed != original:
                        save_state(home, refreshed, "refresh-before-rejected-" + args.command, {})
                    raise
                if state != original:
                    details = {"record": args._record} if getattr(args, "_record", None) is not None else {"id": getattr(args, "id", None), "task": getattr(args, "task", None)}
                    save_state(home, state, args.command, details)
                if args.command == "brief":
                    result = brief(state, root)
                elif args.command == "handoff":
                    result = brief(state, root) + "\nMANUAL BRIDGE (not executed)\n" + json.dumps(args._record, ensure_ascii=False, indent=2) + "\n"
                elif args.command == "pause":
                    result["checkpoint"] = brief(state, root)
                if isinstance(result, dict):
                    result["project_revision"] = state["revision"]
                    result["knowledge_revision"] = state["knowledge_revision"]
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and (result.get("ready") is False or result.get("valid") is False) else 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"error": str(exc), "executed": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
