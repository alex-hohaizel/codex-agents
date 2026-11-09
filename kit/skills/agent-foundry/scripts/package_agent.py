#!/usr/bin/env python3
"""Prepare an already-authored agent delivery kit and optional private plugin export.

No expert content is generated, installed, registered, deployed, or uploaded.
Generated kits require the current constructor build gate, not a copied receipt.
Requires exclusive control of input/output ancestor directories; it is not a
sandbox against a hostile process with the same filesystem authority.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import types
import unicodedata
import zipfile



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


sys.dont_write_bytecode = True
HERE = Path(__file__).absolute().parent


def load_installer():
    """Execute the actual bundled source; never consume a timestamp bytecode cache."""
    path = HERE / "install_agent.py"
    if path.is_symlink() or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Bundled installer source must be a regular file")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("Bundled installer source is not regular")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            source = stream.read()
    finally:
        os.close(fd)
    module = types.ModuleType("bundled_agent_installer")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def inherited_standard(kit, names, api):
    """New exports must carry this constructor's exact portable operating method."""
    path = HERE / "check_generated_inheritance.py"
    source = api.read_bytes(path)
    module = types.ModuleType("bundled_generated_inheritance")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    contract, errors = module.inspect_children([kit / "skills" / name for name in names], HERE.parent)
    if errors:
        raise ValueError("Generated-agent operating inheritance blocks export: " + json.dumps(errors, ensure_ascii=False))
    return contract


def gate(session):
    runtime = HERE / "foundry.py"
    if runtime.is_symlink() or not runtime.is_file():
        raise ValueError("Current bundled constructor runtime is unavailable")
    p = subprocess.run([sys.executable, "-B", str(runtime), "build-gate", str(session)], capture_output=True, text=True, timeout=45)
    try:
        result = strict_json_loads(p.stdout)
    except ValueError as error:
        raise ValueError("Constructor build gate did not return JSON") from error
    if p.returncode != 0 or not isinstance(result, dict) or result.get("ready") is not True:
        raise ValueError("Current constructor build gate blocks packaging: " + json.dumps(result, ensure_ascii=False))
    blueprint = result.get("blueprint")
    approval = result.get("approval_ref")
    if not isinstance(blueprint, dict) or not isinstance(approval, dict):
        raise ValueError("Build gate lacks exact blueprint/approval provenance")
    if approval.get("blueprint_sha256") != blueprint.get("sha256") or approval.get("blueprint_revision") != blueprint.get("revision") or not isinstance(approval.get("source"), str) or not approval["source"]:
        raise ValueError("Build gate approval does not pin its current blueprint")
    return result


def bundle_gate(session, directory):
    runtime = HERE / "foundry.py"
    p = subprocess.run([sys.executable, "-B", str(runtime), "bundle-check", str(session), "--directory", str(directory)], capture_output=True, text=True, timeout=45)
    try:
        result = strict_json_loads(p.stdout)
    except ValueError as error:
        raise ValueError("Constructor bundle check did not return JSON") from error
    if p.returncode != 0 or not isinstance(result, dict) or result.get("valid") is not True:
        raise ValueError("Current bundle evidence blocks export: " + json.dumps(result, ensure_ascii=False))
    return result


def normalize_ui(path, api):
    """Remove only known host-generated product policy; preserve other UI bytes."""
    raw = api.read_bytes(path).decode("utf-8")
    lines = raw.splitlines(keepends=True)
    policy = False
    removed = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() and not line.startswith((" ", "\t", "#")):
            policy = line.strip() == "policy:"
        if policy and re.match(r"^\s+allow_implicit_invocation:", line):
            value = line.split(":", 1)[1].strip()
            if value not in ("true", "false", "null", "~"):
                raise ValueError("Implicit invocation policy must be a YAML boolean or null")
        match = re.match(r"^( +)products:\s*(.*?)\s*$", line)
        if not (policy and match):
            i += 1
            continue
        start = i
        indent = len(match[1])
        text = match[2]
        i += 1
        while i < len(lines):
            following = lines[i]
            following_indent = len(following) - len(following.lstrip(" "))
            # YAML permits a block sequence at the mapping key's indentation.
            # Consume its dash items, but stop before a sibling policy key.
            indentless_item = following_indent == indent and re.match(r"^-(?:[ \t]|$)", following[indent:].rstrip("\r\n"))
            if following.strip() and following_indent <= indent and not indentless_item:
                break
            text += " " + following.strip()
            i += 1
        tokens = re.findall(r"[A-Za-z_]+", text)
        host = {"chatgpt", "codex", "api", "atlas"}
        portable = {"CHAT", "CODEX", "HERMES"}
        if tokens and set(tokens) <= host:
            removed.append((start, i))
        elif tokens and set(tokens) <= portable or text.strip() in ("null", "~", "[]"):
            continue
        else:
            raise ValueError("Unknown product policy; resolve its portability explicitly")
    if not removed:
        return False
    filtered = "".join(line for n, line in enumerate(lines) if not any(a <= n < b for a, b in removed))
    # An empty policy object may be omitted; preserve interface and actual invocation policy.
    filtered = re.sub(r"(?m)^policy:\s*\n(?=\S|\Z)", "", filtered)
    if filtered != raw:
        temporary = path.with_name(".ui-" + os.urandom(8).hex() + ".yaml")
        api.write_file(temporary, filtered.encode("utf-8"), api.file_mode(path))
        os.replace(temporary, path)
    return True


def skill_names(kit, api):
    root = api.safe_path(kit / "skills")
    if not root.is_dir():
        raise ValueError("Kit requires skills/")
    result = []
    for path in sorted(root.iterdir()):
        path = api.safe_path(path)
        if not path.is_dir() or not api.valid_name(path.name):
            raise ValueError("Invalid skill directory")
        result.append(path.name)
    return result


def own_factory(kit, names, api):
    if names != ["agent-foundry"]:
        raise ValueError("Factory purpose is only for the constructor's exact own skill")
    actual_root = HERE.parent
    candidate = kit / "skills/agent-foundry"
    source = api.file_map(actual_root)
    copied = api.file_map(candidate)
    wrapper = {"agents/openai.yaml", "assets/icon.svg", "assets/icon.png"}
    def core(items):
        return {k: v for k, v in items.items() if k not in wrapper and "__pycache__" not in Path(k).parts and not k.endswith(".pyc")}
    if core(source) != core(copied):
        raise ValueError("Factory selfpackage differs from the current trusted constructor source")


def reject_export_path(path, base, api):
    path = api.safe_path(path)
    if path == base or base in path.parents:
        raise ValueError("Write an archive outside the directory being packaged")
    if path.exists():
        raise ValueError("Export destination already exists; use a new output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def portable_component(value):
    if not value or value in (".", "..") or value.endswith((".", " ")) or any(ord(c) < 32 or ord(c) == 127 or c in '\\:<>|?*' for c in value):
        raise ValueError("Unsafe portable archive name: " + repr(value))
    if value.split(".", 1)[0].upper() in {"CON", "PRN", "AUX", "NUL", *["COM" + str(n) for n in range(1, 10)], *["LPT" + str(n) for n in range(1, 10)]}:
        raise ValueError("Reserved portable archive name: " + value)


def capture_files(base, api):
    """Capture exact bytes/modes once; reject edits between inventory and capture."""
    portable_component(base.name)
    files = api.file_map(base)
    if len(files) > 20000:
        raise ValueError("Delivery snapshot exceeds the 20000-file resource guard")
    captured = {}
    prefixes = {}
    total = 0
    for relative, expected in files.items():
        parts = Path(relative).parts
        for at, part in enumerate(parts):
            portable_component(part)
            prefix = "/".join(parts[:at + 1])
            key = unicodedata.normalize("NFC", prefix).casefold()
            if key in prefixes and prefixes[key] != prefix:
                raise ValueError("Case/normalization-conflicting portable paths: " + prefix)
            prefixes[key] = prefix
        name = Path(relative).name.lower()
        environment_secret = name.startswith(".env") and name not in (".env.example", ".env.template", ".env.sample")
        if any(p in (".git", "node_modules", "__pycache__", ".venv") for p in parts) or environment_secret or name.endswith((".pyc", ".p12", ".p8", ".jks", ".keystore")):
            raise ValueError("Excluded private/generated material in export: " + relative)
        data = api.read_bytes(base / relative)
        if api.digest(data) != expected:
            raise ValueError("Source changed during snapshot: " + relative)
        total += len(data)
        if total > 512 * 1024 * 1024:
            raise ValueError("Delivery snapshot exceeds the 512-MiB resource guard; split the delivery")
        if re.search(br"(?m)^-----BEGIN (?:[A-Z ]*PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----", data):
            raise ValueError("Private key material is not an export artifact: " + relative)
        captured[relative] = {"bytes": data, "mode": api.file_mode(base / relative)}
    return captured


def write_snapshot(base, snapshot, api):
    for relative, record in snapshot.items():
        api.write_file(base / relative, record["bytes"], record["mode"])


def write_archive(base, destination, api, snapshot=None):
    """Write the exact captured bytes, never reopen files through ZipFile.write."""
    snapshot = snapshot if snapshot is not None else capture_files(base, api)
    portable_component(base.name)
    temporary = destination.with_name("." + destination.name + ".partial")
    if temporary.exists():
        raise ValueError("Partial export exists; inspect before retry")
    try:
        with zipfile.ZipFile(temporary, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for relative, record in sorted(snapshot.items()):
                for part in Path(relative).parts:
                    portable_component(part)
                info = zipfile.ZipInfo(base.name + "/" + relative)
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | record["mode"]) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, record["bytes"])
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError("Archive integrity verification failed")
        # Atomic exclusive publication: a concurrent creator must not be overwritten.
        os.link(temporary, destination)
        temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"path": str(destination), "sha256": api.digest(api.read_bytes(destination)), "size_bytes": destination.stat().st_size}


def build(args):
    api = load_installer()
    kit = api.safe_path(args.kit)
    names = skill_names(kit, api)
    if not api.valid_name(args.agent_id) or not api.valid_name(args.entry_skill) or args.entry_skill not in names:
        raise ValueError("Agent identity and entry skill must match declared skills")
    if args.plugin_output and args.kit_output and api.safe_path(args.plugin_output) == api.safe_path(args.kit_output):
        raise ValueError("Plugin and delivery archive outputs must be distinct")
    pin = None
    observed = None
    if args.purpose == "factory":
        if args.agent_id != "agent-foundry" or args.entry_skill != "agent-foundry" or args.session is not None:
            raise ValueError("Factory purpose cannot bypass a target's blueprint approval")
        own_factory(kit, names, api)
    else:
        if args.session is None:
            raise ValueError("Generated package requires --session")
        observed = gate(args.session)
        blueprint = observed["blueprint"]
        if names != sorted(blueprint.get("skill_names", [])) or args.entry_skill != blueprint.get("entry_skill"):
            raise ValueError("Kit skill set/entry differs from the current approved blueprint")
        if args.agent_id != args.entry_skill:
            raise ValueError("Generated package agent_id must equal its approved entry_skill")
        pin = {"id": blueprint["id"], "revision": blueprint["revision"], "sha256": blueprint["sha256"], "approval_source": observed["approval_ref"]["source"]}
    normalized = []
    for name in names:
        ui = kit / "skills" / name / "agents/openai.yaml"
        if ui.exists() and normalize_ui(ui, api):
            normalized.append(name)
    metadata = {"agent_id": args.agent_id, "version": args.version, "entry_skill": args.entry_skill, "purpose": args.purpose, "blueprint": pin}
    if args.purpose == "generated":
        metadata["operating_standard"] = inherited_standard(kit, names, api)
    manifest = api.write_manifest(kit, metadata)
    api.load_kit(kit)
    snapshot = capture_files(kit, api)
    exports = []
    with tempfile.TemporaryDirectory(prefix="agent-delivery-") as temporary:
        frozen = Path(temporary).resolve() / kit.name
        write_snapshot(frozen, snapshot, api)
        api.load_kit(frozen)
        if observed is not None:
            bundle_gate(args.session, frozen)
            current = gate(args.session)
            if current["blueprint"] != observed["blueprint"] or current["approval_ref"] != observed["approval_ref"]:
                raise ValueError("Approval changed during packaging; do not export")
        else:
            own_factory(frozen, names, api)
        expected_files = {name: api.digest(record["bytes"]) for name, record in snapshot.items()}
        expected_modes = {name: record["mode"] for name, record in snapshot.items()}
        if api.file_map(frozen) != expected_files or api.mode_map(frozen, expected_files) != expected_modes:
            raise ValueError("Frozen delivery snapshot changed during validation")
        if args.plugin_output:
            output = reject_export_path(args.plugin_output, kit, api)
            if not args.display_name or not args.subtitle or len(args.subtitle) > 30:
                raise ValueError("Plugin display name and subtitle (1..30 characters) are required")
            root = Path(temporary).resolve() / args.agent_id
            if root == frozen:
                root = Path(temporary).resolve() / "plugin" / args.agent_id
            root.mkdir(parents=True)
            plugin_snapshot = {name: record for name, record in snapshot.items() if name.startswith("skills/")}
            plugin = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "name": args.agent_id, "version": args.version, "description": "A scoped agent with specialist instructions and verified delivery contracts.", "extensions": {"com.openai": {"interface": {"displayName": args.display_name, "shortDescription": args.subtitle, "capabilities": []}}}}
            plugin_snapshot["plugin.json"] = {"bytes": api.encode(plugin), "mode": 0o644}
            exports.append(dict(write_archive(root, output, api, plugin_snapshot), kind="private_plugin_export", account_registration="not_performed"))
        if args.kit_output:
            output = reject_export_path(args.kit_output, kit, api)
            exports.append(dict(write_archive(frozen, output, api, snapshot), kind="delivery_kit"))
    return {"ok": True, "agent_id": args.agent_id, "purpose": args.purpose, "manifest": str(kit / "manifest.json"), "manifest_sha256": api.digest(api.encode(manifest)), "skills": names, "entry_skill": args.entry_skill, "normalized_host_ui": normalized, "blueprint": pin, "exports": exports, "claim_boundary": "files prepared; no host discovery, account registration, product execution or publication performed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--entry-skill", required=True)
    parser.add_argument("--purpose", choices=("factory", "generated"), required=True)
    parser.add_argument("--session", type=Path)
    parser.add_argument("--plugin-output", type=Path)
    parser.add_argument("--kit-output", type=Path)
    parser.add_argument("--display-name", default="")
    parser.add_argument("--subtitle", default="")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args), ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
