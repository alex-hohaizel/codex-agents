#!/usr/bin/env python3
"""Prepare a verified existing project agent's maintenance kit; never apply it.

Python3.9+ standard library. Place beside PROJECT_AGENT_SOURCE/ and portable/.
The project must already have exactly one valid installer ownership record for
the supplied agent skill. No ownership, blueprint approval or product acceptance
is invented. Files are written only into a new output directory outside project.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import types

VERSION = "5.0.0"
MAINTENANCE_QUOTE = "Роби абсолютно все за своїми рекомендаціями."


def load_installer():
    path = Path(__file__).absolute().parent / "portable/install_agent.py"
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("Keep this helper beside the verified release's portable/install_agent.py")
    module = types.ModuleType("trusted_project_installer")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module, path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_source(api, root):
    manifest_path = api.safe_path(root / "source-manifest.json")
    data = api.read_json(manifest_path)
    require(isinstance(data, dict) and api.valid_name(data.get("name")) and data.get("version") == VERSION,
            "Source manifest must identify exactly one verified project skill at version5.0.0")
    source = api.safe_path(root / data["name"])
    require(source.is_dir(), "Project agent source folder is missing")
    records = data.get("files")
    require(isinstance(records, dict) and 1 <= len(records) <= 20000, "Source manifest requires bounded exact file records")
    expected, modes = {}, {}
    total = 0
    for name, row in records.items():
        api.relative_file(name)
        require(isinstance(row, dict) and isinstance(row.get("sha256"), str) and api.HEX.fullmatch(row["sha256"]), "Invalid source hash: " + name)
        require(type(row.get("mode")) is int and 0 <= row["mode"] <= 0o777, "Invalid source mode: " + name)
        require(type(row.get("size")) is int and row["size"] >= 0, "Invalid source size: " + name)
        payload = api.read_bytes(source / name)
        total += len(payload)
        require(total <= 128 * 1024 * 1024, "Project agent source exceeds128MiB guard")
        require(api.digest(payload) == row["sha256"] and len(payload) == row["size"], "Source bytes differ from manifest: " + name)
        require(api.file_mode(source / name) == row["mode"], "Source permissions differ from manifest: " + name)
        expected[name] = row["sha256"];modes[name] = row["mode"]
    require(api.file_map(source) == expected, "Source has missing, extra or linked files; use verified release source")
    return data["name"], source, records, api.digest(api.read_bytes(manifest_path))


def find_owner(api, project, name):
    directory = api.safe_path(project / ".agents/agent-installs")
    require(directory.is_dir(), "No project installer ownership record. Reconcile the original agent installation and its real blueprint/receipt; this helper will not create ownership")
    owners = []
    for path in sorted(directory.iterdir()):
        path = api.safe_path(path)
        require(path.is_file() and path.suffix == ".json" and api.valid_name(path.stem), "Unexpected ownership entry; reconcile it before updating: " + path.name)
        record = api.read_json(path)
        require(isinstance(record, dict) and type(record.get("format_version")) is int and record["format_version"] == 1 and record.get("kit_id") == "agent-package", "Unsupported installed ownership record: " + path.name)
        manifest = record.get("manifest")
        require(isinstance(manifest, dict) and type(manifest.get("format_version")) is int, "Unsupported installed manifest format: " + path.name)
        entries = api.validate_manifest(manifest)
        require(record.get("agent_id") == path.stem == manifest["agent_id"], "Ownership identity mismatch: " + path.name)
        require(record.get("manifest_sha256") == api.digest(api.encode(manifest)), "Installed ownership manifest hash mismatch: " + path.name)
        if name in entries:
            owners.append((path, record, entries))
    require(len(owners) == 1, "Need exactly one verified owner of " + name + "; found " + str(len(owners)) + ". Reconcile missing/duplicate ownership without copying or reinitializing the agent")
    path, record, entries = owners[0]
    require(set(entries) == {name} and record["manifest"]["entry_skill"] == name,
            "Existing owner manages a different/multiple-skill set. Prepare an explicit whole-family update; no sibling skill will be removed")
    require(record["manifest"]["purpose"] == "generated", "This source is a project agent, not a factory self-package")
    require((project / ".agents/skills" / name).is_dir(), "Owned project skill is missing; reconcile its installation before update")
    return path, record, api.digest(api.read_bytes(path))


def prepare(project, output, source_root=None):
    api, installer = load_installer()
    require(Path(project).is_absolute() and Path(output).is_absolute(), "Use absolute --project and --output paths")
    project = api.safe_path(project);output = api.safe_path(output)
    source_root = api.safe_path(source_root or Path(__file__).absolute().parent / "PROJECT_AGENT_SOURCE")
    require(project.is_dir(), "Existing project folder is missing; open the actual existing project")
    require(not output.exists(), "Output already exists; choose a new outside-project directory")
    require(output.parent.is_dir(), "Output parent must already exist outside the project")
    require(output != project and project not in output.parents and output not in project.parents,
            "Output must be outside the existing project and cannot contain it")
    require(output != source_root and source_root not in output.parents and output not in source_root.parents,
            "Output must be separate from the verified source bundle")
    name, source, records, source_hash = read_source(api, source_root)
    owner_path, old, owner_hash = find_owner(api, project, name)
    old_manifest = old["manifest"]
    metadata = {key: value for key, value in json.loads(json.dumps(old_manifest)).items() if key not in ("skills", "format_version", "kit_id")}
    metadata["version"] = VERSION
    metadata["operating_standard"] = {"schema":api.OPERATING_SCHEMA, "release":VERSION,
        "resources":{path:records[path]["sha256"] for path in api.OPERATING_RESOURCES}}
    metadata["blueprint_status"] = "historical_origin_only"
    metadata["maintenance_authority"] = {
        "schema":"agent-maintenance-authority/1", "actor":"user",
        "source":"Current SKILLS MANAGEMENT [WORK] instruction authorizing the general5.0.0 maintenance release",
        "verbatim":MAINTENANCE_QUOTE,
        "scope":"Generic operating-standard/version maintenance; retain original product scope, requirements, real agent identity and project icons",
        "origin_manifest_sha256":old["manifest_sha256"], "origin_record_sha256":owner_hash,
        "product_acceptance_granted":False, "new_product_effects_granted":False}
    with tempfile.TemporaryDirectory(prefix=".prepare-agent-update-", dir=output.parent) as temporary:
        staged = Path(temporary) / "kit"
        for relative, row in records.items():
            payload = api.read_bytes(source / relative)
            require(api.digest(payload) == row["sha256"] and len(payload) == row["size"] and api.file_mode(source / relative) == row["mode"], "Source changed during preparation: " + relative)
            api.write_file(staged / "skills" / name / relative, payload, row["mode"])
        api.write_manifest(staged, metadata)
        api.load_kit(staged)
        # Uses the same read-only admission, drift checks and icon overlay as
        # installer --mode dry-run. It performs no apply and no project writes.
        plan = api.plan_install(staged, project)
        dry_run = api.summary(plan, "dry-run")
        require(api.digest(api.read_bytes(owner_path)) == owner_hash, "Ownership changed during preparation; rerun against current state")
        receipt = {"status":"prepared", "applied":False, "project_writes_performed":False,
            "project":str(project), "skill":name, "agent_id":old_manifest["agent_id"], "version":VERSION,
            "origin_manifest_sha256":old["manifest_sha256"], "origin_record_sha256":owner_hash,
            "source_manifest_sha256":source_hash, "blueprint_status":"historical_origin_only",
            "original_blueprint":old_manifest["blueprint"], "dry_run":dry_run,
            "claim_boundary":"Prepared maintenance files only; no new product acceptance, project mutation, host discovery or agent execution performed"}
        receipt["output"] = str(output)
        receipt["next_argv"] = {
            mode:[sys.executable, "-B", str(installer), "--kit", str(output), "--project", str(project), "--mode", mode]
            for mode in ("preflight", "apply", "verify")}
        api.write_file(staged / "PREPARATION.json", api.encode(receipt), 0o644)
        # Exclusively create the new destination; never replace an old output.
        output.mkdir(mode=0o700)
        try:
            for relative in api.file_map(staged):
                api.write_file(output / relative, api.read_bytes(staged / relative), api.file_mode(staged / relative))
        except BaseException:
            raise ValueError("Output preparation interrupted; project untouched. Inspect the partial output before choosing a new directory")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, help="Optional verified PROJECT_AGENT_SOURCE folder; default is beside this helper")
    args = parser.parse_args(argv)
    try:
        result = prepare(args.project, args.output, args.source_root)
        print(json.dumps(result, ensure_ascii=False, indent=2));return 0
    except Exception as error:
        print(json.dumps({"status":"blocked", "applied":False, "project_writes_performed":False, "error":str(error)}, ensure_ascii=False, indent=2));return 2


if __name__ == "__main__":
    raise SystemExit(main())
