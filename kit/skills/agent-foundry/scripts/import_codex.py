#!/usr/bin/env python3
"""Audit reviewed local Codex skills and roles, then stage a fresh project.

The import materializes files only. Review prompts, resources and code before
authorizing staging or invocation. Use an output parent controlled by the caller.
The audited target is read-only and remains separate from the output project.
"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import unicodedata

try:
    import tomllib
except ImportError:
    tomllib = None

import install_agent as files


SCHEMA = "codex-agent-import/1"
SKILLS = Path(".agents/skills")
ROLES = Path(".codex/agents")
ROLE_FIELDS = {
    "name", "description", "developer_instructions", "model", "model_reasoning_effort",
    "skills",
}
BUILTIN_ROLES = {"default", "explorer", "worker"}
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
SCOPES = {"team": 0, "personal": 1}
ACTIONS = {"replace", "prepend", "append"}
NAME_FIELD = re.compile(r"^name:[ \t]*(.*)$", re.MULTILINE)
SKILL_HEADER = re.compile(r"\A\ufeff?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
ROLE_NAME = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
ROLE_PROMPT = re.compile(
    r"^developer_instructions[ \t]*=[ \t]*"
    r"""(?:""" + '"""[\\s\\S]*?"""' + r"""|'''[\s\S]*?'''|[^\r\n]+)""",
    re.MULTILINE,
)
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_FILES = 8000


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class File:
    content: bytes
    mode: int

    def identity(self):
        return {"sha256": files.digest(self.content), "mode": self.mode}


@dataclass
class Snapshot:
    files: dict
    directories: tuple = ()

    def identity(self):
        return {
            "files": {name: value.identity() for name, value in sorted(self.files.items())},
            "directories": list(self.directories),
        }


def object_keys(record, required, optional=()):
    require(isinstance(record, dict) and set(required) <= record.keys() <= set(required) | set(optional),
            "Expected exactly the required fields and recognized optional fields: " + ", ".join(required))
    return record


def read_file(path):
    mode = files.file_mode(path)
    require(path.stat().st_size <= MAX_FILE_BYTES, "File exceeds import size limit: " + str(path))
    data = files.read_bytes(path)
    require(len(data) <= MAX_FILE_BYTES, "File exceeds import size limit: " + str(path))
    return File(data, mode)


def source_path(base, name):
    return files.safe_path(base / files.relative_file(name))


def portable_key(name):
    return unicodedata.normalize("NFC", name).casefold()


def read_tree(root, bounded=True):
    require(files.safe_path(root).is_dir(), "Expected an import directory: " + str(root))
    result, directories, names, total = {}, [], set(), 0
    for current, folders, filenames in os.walk(root, followlinks=False):
        folders.sort()
        for name in sorted(folders + filenames):
            entry = Path(current) / name
            relative = entry.relative_to(root).as_posix()
            key = portable_key(relative)
            require(key not in names, "Case or Unicode path collision: " + relative)
            names.add(key)
            require(len(names) <= MAX_FILES, "Import tree exceeds file count limit")
            require(not bounded or name not in {".git", ".agents", ".codex", ".env", "__pycache__"},
                    "Nonportable private or host directory/file: " + relative)
            info = entry.lstat()
            if stat.S_ISDIR(info.st_mode):
                directories.append(relative)
            else:
                require(stat.S_ISREG(info.st_mode), "Link or special file is not permitted: " + relative)
                item = read_file(entry)
                total += len(item.content)
                require(total <= MAX_TOTAL_BYTES, "Import tree exceeds total size limit")
                result[relative] = item
    return Snapshot(result, tuple(sorted(directories)))


def skill_parts(item):
    text = item.content.decode("utf-8")
    header = SKILL_HEADER.match(text)
    require(header and text[header.end():].strip(), "SKILL.md needs frontmatter and a body")
    names = NAME_FIELD.findall(header.group(1))
    require(len(names) == 1, "SKILL.md needs a unique name field")
    field = re.split(r"\s+#", names[0].strip(), maxsplit=1)[0].strip()
    name = field.strip("'\"")
    require(files.valid_name(name), "Invalid native skill name")
    return name, text[:header.end()], text[header.end():]


def member_name(kind, name):
    if kind == "role":
        return isinstance(name, str) and 1 <= len(name) <= 64 and ROLE_NAME.fullmatch(name)
    return files.valid_name(name)


def read_role(item, name):
    require(tomllib is not None, "Role imports require Python 3.11 or later")
    role = tomllib.loads(item.content.decode("utf-8"))
    require(role.get("name") == name and name not in BUILTIN_ROLES,
            "Role name must match the manifest and cannot shadow a built-in role")
    for key in ("description", "developer_instructions"):
        require(isinstance(role.get(key), str) and role[key].strip(), "Role requires " + key)
    unknown = sorted(set(role) - ROLE_FIELDS)
    require(not unknown, "Role has unsupported runtime fields: " + ", ".join(unknown))
    if "model" in role:
        require(isinstance(role["model"], str) and role["model"].strip(), "Role model must be text")
    if "model_reasoning_effort" in role:
        require(isinstance(role["model_reasoning_effort"], str) and role["model_reasoning_effort"] in EFFORTS,
                "Unsupported role reasoning effort")
    if "skills" in role:
        section = object_keys(role["skills"], ("config",))
        require(isinstance(section["config"], list), "Role skill selectors must be an array")
        for selector in section["config"]:
            object_keys(selector, ("name", "enabled"))
            require(files.valid_name(selector["name"]) and selector["enabled"] is False,
                    "Only name-based skill disables are portable in a role")
    return role


def merge(current, payload, mode):
    if mode == "replace":
        return payload
    if mode == "prepend":
        return payload.rstrip() + "\n\n" + current
    return current.rstrip() + "\n\n" + payload


def customize(kind, name, item, content, mode):
    alternative = content.decode("utf-8")
    require(alternative.strip(), "Empty customization text")
    if kind == "skill":
        _, header, body = skill_parts(item)
        result = header + merge(body, alternative, mode)
    else:
        role = read_role(item, name)
        original = item.content.decode("utf-8")
        span = ROLE_PROMPT.search(original)
        require(span, "Role prompt assignment cannot be edited without rewriting other fields")
        revised = merge(role["developer_instructions"], alternative, mode)
        body = json.dumps(revised, ensure_ascii=False)
        result = original[:span.start()] + "developer_instructions = " + body + original[span.end():]
        updated = File(result.encode("utf-8"), item.mode)
        require(read_role(updated, name) == {**role, "developer_instructions": revised},
                "Role customization would rewrite other parsed fields")
    return File(result.encode("utf-8"), item.mode)


def module_order(records):
    require(isinstance(records, list) and 0 < len(records) <= 256, "Expected a bounded module list")
    modules = {}
    for record in records:
        object_keys(record, ("id", "version", "members"), ("requires", "optional"))
        key = record["id"]
        require(files.valid_name(key) and key not in modules, "Invalid or duplicate module ID")
        version = record["version"]
        require(isinstance(version, str) and version.strip() and len(version) <= 128,
                "Module version is required")
        require(isinstance(record["members"], list) and record["members"], "Module requires members")
        edges = []
        for group in ("requires", "optional"):
            values = record.get(group, [])
            require(isinstance(values, list) and all(files.valid_name(value) for value in values),
                    "Invalid module dependency list: " + key)
            edges.extend(values)
        require(len(edges) == len(set(edges)), "Duplicate dependency declaration: " + key)
        modules[key] = record
    active, order, visiting = set(), [], set()

    def visit(key):
        require(key not in visiting, "Module dependency cycle: " + key)
        if key in active:
            return
        visiting.add(key)
        module = modules[key]
        for dependency in sorted(module.get("requires", []) + module.get("optional", [])):
            require(dependency in modules or dependency in module.get("optional", []),
                    "Missing required module " + dependency + " for " + key)
            if dependency in modules:
                visit(dependency)
        visiting.remove(key)
        active.add(key)
        order.append(module)

    for key in sorted(modules):
        visit(key)
    return order


def record_item(base, member):
    object_keys(member, ("kind", "name", "source"))
    kind, name = member["kind"], member["name"]
    require(kind in ("skill", "role") and member_name(kind, name), "Invalid native member")
    source = source_path(base, member["source"])
    if kind == "role":
        item = read_file(source)
        read_role(item, name)
        return Snapshot({name + ".toml": item})
    snapshot = read_tree(source)
    entry = snapshot.files.get("SKILL.md")
    require(entry and skill_parts(entry)[0] == name, "SKILL.md name disagrees with the manifest: " + name)
    return snapshot


def collect_overrides(document):
    customizations = document.get("customizations", [])
    require(isinstance(customizations, list), "Customizations must be a list")
    ordered = defaultdict(list)
    seen = set()
    for entry in customizations:
        object_keys(entry, ("kind", "name", "scope", "mode", "source", "expected_sha256"))
        kind, name, scope, mode = (entry[key] for key in ("kind", "name", "scope", "mode"))
        require(kind in ("skill", "role") and member_name(kind, name)
                and isinstance(scope, str) and scope in SCOPES and isinstance(mode, str) and mode in ACTIONS,
                "Unsupported customization target, scope or mode")
        expected = entry["expected_sha256"]
        require(isinstance(expected, str) and files.HEX.fullmatch(expected), "Customization needs an input SHA-256")
        require((kind, name, scope) not in seen, "Duplicate customization in the same scope")
        seen.add((kind, name, scope))
        ordered[(kind, name)].append(entry)
    return ordered


def target_members(target):
    result = {"skill": defaultdict(list), "role": defaultdict(list)}
    for kind, native in (("skill", SKILLS), ("role", ROLES)):
        root = files.safe_path(target / native)
        if not root.exists():
            continue
        require(root.is_dir(), "Native discovery path is not a directory: " + str(root))
        for path in sorted(root.iterdir()):
            if kind == "role" and path.suffix.lower() != ".toml":
                continue
            matches = {portable_key(path.name if kind == "skill" else path.stem)}
            try:
                files.safe_path(path)
                if kind == "skill" and (path / "SKILL.md").is_file():
                    matches.add(portable_key(skill_parts(read_file(path / "SKILL.md"))[0]))
                elif kind == "role" and tomllib is not None:
                    internal = tomllib.loads(read_file(path).content.decode("utf-8")).get("name")
                    if isinstance(internal, str):
                        matches.add(portable_key(internal))
            except (OSError, ValueError, files.InstallError):
                # A malformed unrelated entry may still collide by its native path.
                pass
            for key in matches:
                result[kind][key].append(path)
    return result


def target_registry(target):
    config = files.safe_path(target / ".codex/config.toml")
    if not config.exists():
        return {}
    parsed = tomllib.loads(read_file(config).content.decode("utf-8"))
    agents = parsed.get("agents", {})
    require(isinstance(agents, dict), "Audited project role registry must be a TOML table")
    return agents


def registry_text(rows):
    lines = []
    for row in sorted(rows, key=lambda item: item["name"]):
        lines.append("[agents." + row["name"] + "]")
        for key in ("description", "config_file"):
            lines.append(key + " = " + json.dumps(row[key], ensure_ascii=False))
        lines.append("")
    return "\n".join(lines).encode("utf-8")


def role_launch_overrides(rows, output):
    overrides = []
    for row in sorted(rows, key=lambda item: item["name"]):
        prefix = "agents." + row["name"] + "."
        overrides.extend([
            prefix + "description=" + json.dumps(row["description"], ensure_ascii=False),
            prefix + "config_file=" + json.dumps(str(output / ".codex" / row["config_file"]), ensure_ascii=False),
        ])
    return overrides


def audit(manifest, target):
    target = files.safe_path(target)
    require(target.is_dir(), "The audited project directory must already exist")
    manifest = files.safe_path(manifest)
    raw = read_file(manifest)
    document = object_keys(files.strict_json_loads(raw.content.decode("utf-8")),
                           ("schema", "modules"), ("customizations",))
    require(document["schema"] == SCHEMA, "Unsupported import manifest schema")
    modules = module_order(document["modules"])
    overlays = collect_overrides(document)
    target_index = target_members(target)
    module_ids = {module["id"] for module in modules}
    plan = {"schema": "codex-agent-import-plan/1", "target": str(target), "manifest_sha256": raw.identity()["sha256"],
            "modules": [], "members": [], "role_registry": [], "blockers": []}
    snapshots = {}
    registry = None
    total_bytes = total_files = 0
    for module in modules:
        plan["modules"].append({"id": module["id"], "version": module["version"],
                                "required": sorted(module.get("requires", [])),
                                "optional": sorted(module.get("optional", [])),
                                "missing_optional": sorted(set(module.get("optional", [])) - module_ids)})
        for member in module["members"]:
            snapshot = record_item(manifest.parent, member)
            kind, name = member["kind"], member["name"]
            key = (kind, name)
            require(key not in snapshots, "Multiple modules declare the same native member: " + name)
            original = snapshot.identity()
            changes = []
            entry = "SKILL.md" if kind == "skill" else name + ".toml"
            for layer in sorted(overlays.pop(key, []), key=lambda record: SCOPES[record["scope"]]):
                current = snapshot.files[entry]
                require(current.identity()["sha256"] == layer["expected_sha256"],
                        "Stale customization input: " + layer["scope"] + " " + name)
                payload = read_file(source_path(manifest.parent, layer["source"]))
                changed = customize(kind, name, current, payload.content, layer["mode"])
                snapshot.files[entry] = changed
                changes.append({**layer, "source_sha256": payload.identity()["sha256"],
                                "result_sha256": changed.identity()["sha256"]})
            if kind == "skill":
                root = source_path(manifest.parent, member["source"])
                files.validate_skill_text(root, name, snapshot.files[entry].content.decode("utf-8"))
            desired = snapshot.identity()
            total_files += len(snapshot.files) + len(snapshot.directories)
            total_bytes += sum(len(item.content) for item in snapshot.files.values())
            require(total_files <= MAX_FILES and total_bytes <= MAX_TOTAL_BYTES, "Import exceeds total material size")
            target_states = []
            for path in target_index[kind].get(portable_key(name), []):
                identity = None
                if not path.is_symlink():
                    if path.is_dir() and kind == "skill":
                        identity = read_tree(path, bounded=False).identity()
                    elif path.is_file() and kind == "role":
                        identity = Snapshot({path.name: read_file(path)}).identity()
                native = SKILLS / name if kind == "skill" else ROLES / (name + ".toml")
                relative = path.relative_to(target).as_posix()
                match = identity == desired and relative == native.as_posix()
                target_states.append({"path": relative, "identity": identity, "matches": match})
                if not match:
                    plan["blockers"].append({"kind": kind, "name": name, "target_path": relative,
                                             "reason": "existing native entry differs or aliases the import"})
            if kind == "role":
                role = read_role(snapshot.files[entry], name)
                registration = {"description": role["description"], "config_file": "agents/" + entry}
                plan["role_registry"].append({"name": name, **registration})
                if registry is None:
                    registry = target_registry(target)
                for alias, value in registry.items():
                    if portable_key(alias) != portable_key(name):
                        continue
                    matches = alias == name and value == registration
                    target_states.append({"path": ".codex/config.toml", "role_alias": alias,
                                          "matches": matches})
                    if not matches:
                        plan["blockers"].append({"kind": kind, "name": name, "target_path": ".codex/config.toml",
                                                 "reason": "existing project role registration differs"})
            snapshots[key] = snapshot
            plan["members"].append({"module": module["id"], **member, "original": original,
                                    "output": desired, "customizations": changes, "target_entries": target_states})
    require(not overlays, "Customization names a member not present in the manifest")
    plan["ready"] = not plan["blockers"]
    plan["role_registry_sha256"] = (files.digest(registry_text(plan["role_registry"]))
                                    if plan["role_registry"] else None)
    plan["plan_sha256"] = files.digest(files.encode(plan))
    return plan, snapshots


def stage(manifest, target, output, expected):
    plan, snapshots = audit(manifest, target)
    require(plan["ready"], "Target collision blocks staging")
    require(expected == plan["plan_sha256"], "Reviewed import plan or source has drifted")
    output = files.safe_path(output)
    target_path = Path(plan["target"])
    require(not output.exists() and output.parent.is_dir(), "Output must be a fresh directory with an existing parent")
    require(output != target_path and target_path not in output.parents,
            "Stage outside the audited target project")
    lock = output.with_name("." + output.name + ".import-lock")
    lock.mkdir(mode=0o700)
    try:
        temp = Path(tempfile.mkdtemp(prefix=".codex-import-", dir=output.parent))
        try:
            for (kind, name), snapshot in snapshots.items():
                root = temp / (SKILLS / name if kind == "skill" else ROLES)
                root.mkdir(parents=True, exist_ok=True)
                for directory in snapshot.directories:
                    (root / directory).mkdir(parents=True, exist_ok=True)
                for relative, item in sorted(snapshot.files.items()):
                    files.write_file(root / relative, item.content, item.mode)
                if kind == "skill":
                    files.validate_skill(temp / ".agents", name)
            if plan["role_registry"]:
                config = registry_text(plan["role_registry"])
                require(files.digest(config) == plan["role_registry_sha256"], "Role registry bytes changed")
                files.write_file(temp / ".codex/config.toml", config, 0o600)
            refreshed, _ = audit(manifest, target)
            require(refreshed["plan_sha256"] == expected, "Source or audited target changed while staging")
            receipt = {"schema": "codex-agent-import-stage/1", "plan": plan, "output": str(output),
                       "role_launch_overrides": role_launch_overrides(plan["role_registry"], output),
                       "target_modified": False, "code_or_hooks_executed": False}
            files.write_file(temp / "IMPORT-RECEIPT.json", files.encode(receipt), 0o600)
            require(not output.exists(), "Staging output already exists")
            temp.rename(output)
            return receipt
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    finally:
        lock.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("audit", "stage"):
        command = commands.add_parser(action)
        command.add_argument("manifest", type=Path)
        command.add_argument("--target", type=Path, required=True)
        if action == "stage":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--expect", required=True)
    args = parser.parse_args()
    try:
        result = (audit(args.manifest, args.target)[0] if args.action == "audit"
                  else stage(args.manifest, args.target, args.output, args.expect))
        print(files.encode(result).decode(), end="")
        return 0 if result.get("ready", True) else 2
    except (OSError, ValueError, files.InstallError) as error:
        print(json.dumps({"ready": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
