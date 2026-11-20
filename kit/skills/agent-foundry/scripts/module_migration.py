#!/usr/bin/env python3
"""Audit and stage project modules and reviewed file migrations in a fresh directory."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from io import StringIO
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import tomllib

import import_codex as native
import install_agent as fs


RECEIPT = "MODULE-IMPORT.json"
RECEIPT_SCHEMA = "codex-agents.module-import-stage/1"
CHANGE_SET_SCHEMA = "codex-agents.project-module-migration/1"
MANIFEST = "bmod.toml"
PRIVATE_PATH_PARTS = {".git", ".agents", ".codex", ".module-import", ".env"}
RESERVED_CODES = {"custom", "modules", "scripts", "_config"}
BMOD_FIELDS = {
    "code", "version", "update_source", "skills", "required_skills",
    "recommended_skills", "pre_install_message", "post_install_message",
    "config_questions", "knowledge",
}
SKILL_FIELDS = {"bmod", "source", "required_skills", "recommended_skills", "scripts"}
MIGRATION_FIELDS = {"module", "from", "to", "title", "summary", "detect", "guide", "checklist"}
VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([\w.-]+))?(?:\+[\w.-]+)?")
require = native.require


def project_directory(value):
    path = fs.relative_file(value)
    require(not any(native.portable_key(part) in PRIVATE_PATH_PARTS for part in Path(path).parts),
            "Choose a project data directory outside host and import state: " + path)
    return path


def overlaps(left, right):
    left, right = map(native.portable_key, (left, right))
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


@dataclass(frozen=True)
class Layout:
    runtime: str = "_modules"
    artifacts: str = "_module-output"

    def __post_init__(self):
        project_directory(self.runtime)
        project_directory(self.artifacts)
        require(not overlaps(self.runtime, self.artifacts), "Module runtime and artifact roots overlap")


@dataclass
class Module:
    source: Path
    record: str
    code: str
    version: str
    format: str
    metadata: dict
    skills: dict
    registrations: dict = field(default_factory=dict)
    resources: dict = field(default_factory=dict)
    retired: dict = field(default_factory=dict)
    migrations: dict = field(default_factory=dict)
    exclusions: dict = field(default_factory=dict)
    conversion: dict | None = None


def tagged(value):
    # TOML and YAML can return types outside JSON. Reject them as inputs to
    # install metadata so that every material value has an unambiguous digest.
    return json.loads(json.dumps(value, allow_nan=False))


def toml(item):
    return tomllib.loads(item.content.decode("utf-8"))


def legacy_yaml(item):
    try:
        import yaml
    except ImportError as error:
        raise ValueError("Legacy YAML imports require PyYAML in this Python environment") from error

    class Loader(yaml.SafeLoader):
        def compose_node(self, parent, index):
            event = self.peek_event()
            require(not isinstance(event, yaml.AliasEvent) and getattr(event, "anchor", None) is None,
                    "Legacy module YAML must not contain aliases or anchors")
            return super().compose_node(parent, index)

        def construct_mapping(self, node, deep=False):
            self.flatten_mapping(node)
            result = {}
            for key, value in self.construct_pairs(node, deep=deep):
                require(isinstance(key, str) and key not in result, "Invalid or duplicate YAML key")
                result[key] = value
            return result

    try:
        value = yaml.load(item.content.decode("utf-8"), Loader=Loader)
    except yaml.YAMLError as error:
        raise ValueError("Invalid legacy module YAML: " + str(error)) from error
    require(isinstance(value, dict), "Legacy YAML must declare a module mapping")
    return value


def text(value, label):
    require(isinstance(value, str) and value.strip(), label + " must be nonempty text")
    return value


def name(value, label):
    require(fs.valid_name(value), "Invalid " + label)
    return value


def array(value, label):
    require(isinstance(value, list), "Expected a list for " + label)
    return value


def names(value, label):
    result = [name(item, label) for item in array(value, label)]
    require(len(set(result)) == len(result), "Duplicate " + label)
    return result


def version_key(value):
    match = VERSION.fullmatch(value) if isinstance(value, str) else None
    require(match, "Unorderable module version: " + str(value))
    pre = match[4]
    atoms = tuple((0, int(part)) if part.isdigit() else (1, part)
                  for part in pre.split(".")) if pre else ()
    return tuple(int(match[i]) for i in (1, 2, 3)), pre is None, atoms


def version_satisfies(actual, minimum):
    have, want = version_key(actual), version_key(minimum)
    return have >= want or (have[0] == want[0] and want[1] and have[2] == ((1, "next"),))


def entry(path):
    return native.read_file(fs.safe_path(path))


def skill_tree(path, exclusions=None):
    snapshot = native.read_tree(path, bounded=exclusions is None)
    if exclusions is not None:
        unportable = {".git", ".agents", ".codex", ".env"}
        for relative in [*snapshot.files, *snapshot.directories]:
            require(not unportable.intersection(Path(relative).parts), "Nonportable private or host path: " + relative)
        for relative, item in list(snapshot.files.items()):
            if "__pycache__" in Path(relative).parts:
                require(relative.endswith(".pyc"), "Unexpected file in legacy interpreter cache: " + relative)
                exclusions[path.name + "/" + relative] = item.identity()
                del snapshot.files[relative]
        snapshot.directories = tuple(directory for directory in snapshot.directories
                                     if "__pycache__" not in Path(directory).parts)
    skill = snapshot.files.get("SKILL.md")
    require(skill, "SKILL.md is missing from " + str(path))
    identifier, _, _ = native.skill_parts(skill)
    require(identifier == path.name, "Skill directory and SKILL.md name differ: " + str(path))
    fs.validate_skill_text(path, identifier, skill.content.decode("utf-8"))
    return snapshot


def resource_tree(root):
    snapshot = native.read_tree(root)
    # A nested skill is never treated as a record resource.
    require(not any(path.endswith("/SKILL.md") for path in snapshot.files),
            "Nested skills belong beside the module record: " + str(root))
    return snapshot


def retirement(module, raw):
    for pair in array(raw.get("renamed", []), "renamed skills"):
        native.object_keys(pair, ("from", "to"))
        old, new = name(pair["from"], "retired skill"), name(pair["to"], "replacement skill")
        require(new in module.skills and old not in module.retired, "Invalid retirement rename: " + old)
        module.retired[old] = new
    for old in names(raw.get("removed", []), "removed skill"):
        require(old not in module.retired, "Duplicate retired skill " + old)
        module.retired[old] = None
    require(not set(module.retired) & module.skills.keys(), "A retired skill is still listed as a current member")


def number_migrations(module, record):
    for path, item in record.files.items():
        if "/" in path or not path.startswith("migration-") or not path.endswith(".toml"):
            continue
        match = re.fullmatch(r"migration-([1-9][0-9]*)\.toml", path)
        require(match is not None, "Invalid numbered migration path " + path)
        migration = toml(item).get("migration")
        require(isinstance(migration, dict) and MIGRATION_FIELDS <= migration.keys(),
                "Incomplete numbered migration " + path)
        require(migration["module"] == module.code, "Numbered migration belongs to another module: " + path)
        for key in MIGRATION_FIELDS - {"checklist"}:
            text(migration[key], "migration " + key)
        require(all(isinstance(check, str) and check.strip() for check in array(migration["checklist"], "checklist")),
                "Migration checklist items must be text")
        module.migrations[int(match[1])] = {
            "path": path, "sha256": item.identity()["sha256"], **tagged(migration),
        }


def modern(record_path, document):
    metadata = document["bmod"]
    require(isinstance(metadata, dict), "Expected a [bmod] table")
    code = name(metadata.get("code"), "module code")
    require(code not in RESERVED_CODES, "Reserved module code " + code)
    version = text(metadata.get("version"), "module version")
    version_key(version)
    update_source = text(metadata.get("update_source"), "module update source")
    require(update_source.startswith(("github:", "https://", "file:", "plugin:")),
            "Unsupported update source syntax")
    multiple = "skills" in metadata
    if multiple:
        require(record_path.name == "bmod-" + code, "Module record directory must be bmod-" + code)
        members = names(metadata["skills"], "module member")
        require(members, "A multi-skill module requires members")
    else:
        require(isinstance(document.get("skill"), dict), "Single-skill module requires a [skill] table")
        members = [name(record_path.name, "single-skill member")]
    module = Module(record_path.parent, record_path.name, code, version, "bmod", tagged(metadata), {})
    for member in members:
        root = record_path.parent / member
        snapshot = skill_tree(root)
        require(MANIFEST in snapshot.files, "Missing member bmod.toml for " + member)
        registration = toml(snapshot.files[MANIFEST]).get("skill")
        require(isinstance(registration, dict), "Missing [skill] table for " + member)
        if multiple:
            require(registration.get("bmod") == record_path.name and registration.get("source") == update_source,
                    "Member registration source or record differs for " + member)
        module.skills[member] = snapshot
        module.registrations[member] = tagged(registration)
    record = resource_tree(record_path) if multiple else module.skills[members[0]]
    if multiple:
        require("SKILL.md" in record.files, "Missing module entry at " + str(record_path))
        fs.validate_skill_text(record_path, record_path.name, record.files["SKILL.md"].content.decode("utf-8"))
        module.skills[record_path.name] = record
    require("help/help.md" in record.files, "Missing module help/help.md for " + code)
    for knowledge in array(metadata.get("knowledge", []), "module knowledge"):
        require(isinstance(knowledge, dict), "Expected a module knowledge table")
        path = fs.relative_file(knowledge.get("path"))
        require(path in record.files, "Missing knowledge resource " + path)
    if "roster.toml" in record.files:
        module.metadata["roster"] = tagged(toml(record.files["roster.toml"]))
    if "retired.toml" in record.files:
        retirement(module, toml(record.files["retired.toml"]))
    number_migrations(module, record)
    return module


def legacy(source, module_path, version):
    item = entry(module_path)
    metadata = legacy_yaml(item)
    code = name(metadata.get("code"), "legacy module code")
    require(code not in RESERVED_CODES, "Reserved legacy module code " + code)
    version = metadata.get("version") or version
    version_key(version)
    module = Module(source, module_path.parent.name, code, version, "module.yaml", tagged(metadata), {})
    module.resources["module.yaml"] = item
    help_path = fs.safe_path(module_path.with_name("module-help.csv"))
    if help_path.exists():
        catalog = entry(help_path)
        rows = csv.DictReader(StringIO(catalog.content.decode("utf-8-sig")), strict=True)
        require(rows.fieldnames and "skill" in rows.fieldnames and len(set(rows.fieldnames)) == len(rows.fieldnames),
                "Legacy module help is missing its skill column or has duplicate columns")
        try:
            catalog_rows = list(rows)
        except csv.Error as error:
            raise ValueError("Invalid legacy module help CSV") from error
        require(all(None not in row and None not in row.values() for row in catalog_rows),
                "Legacy module help contains a malformed row")
        module.metadata["catalog"] = catalog_rows
        module.resources["module-help.csv"] = catalog
    for directory, folders, files in os.walk(source, followlinks=False):
        folders[:] = sorted(folders)
        for folder in folders:
            fs.safe_path(Path(directory) / folder)
        if "SKILL.md" not in files:
            continue
        skill_path = Path(directory)
        identifier = skill_path.name
        require(identifier not in module.skills, "Duplicate legacy skill " + identifier)
        module.skills[identifier] = skill_tree(skill_path, module.exclusions)
        folders.clear()
    require(module.skills, "No native skill folders in legacy module " + code)
    return module


def convert_legacy(module, update_source):
    require(update_source.startswith(("github:", "https://", "file:", "plugin:")),
            "Legacy conversion needs a module update source URI")
    record = "bmod-" + module.code
    require(record not in module.skills, "Existing skill has the generated module record's name")
    members = sorted(module.skills)
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    registration = ["[bmod]", "code = " + quote(module.code), "version = " + quote(module.version),
                    "update_source = " + quote(update_source), "skills = " + quote(members),
                    'pre_install_message = ""', 'post_install_message = ""']
    mapped_questions = []
    for key, fields in module.metadata.items():
        if not isinstance(fields, dict) or not {"default", "prompt"} <= fields.keys():
            continue
        prompt = fields["prompt"]
        if isinstance(prompt, list) and all(isinstance(line, str) for line in prompt):
            prompt = "\n".join(prompt)
        default = fields["default"]
        scope = fields.get("scope", "team")
        if not isinstance(prompt, str) or not isinstance(default, str) or scope not in {"team", "user"}:
            continue
        registration.extend(["", "[[bmod.config_questions]]", "key = " + quote(key), "prompt = " + quote(prompt),
                             "default = " + quote(default), "scope = " + quote(scope)])
        mapped_questions.append(key)
    for member, snapshot in module.skills.items():
        require(MANIFEST not in snapshot.files, "Legacy skill already contains current registration: " + member)
        content = f"[skill]\nbmod = {quote(record)}\nsource = {quote(update_source)}\n"
        snapshot.files[MANIFEST] = native.File(content.encode("utf-8"), 0o644)
        module.registrations[member] = {"bmod": record, "source": update_source}
    heading = module.metadata.get("name") or module.code
    entry = (
        f"---\nname: {record}\ndescription: {quote('Find the reviewed help and skills for ' + module.code + '.')}\n---\n\n"
        f"# {heading}\n\nRead [module help](help/help.md) to choose a skill or review the module configuration.\n"
    )
    catalog = [f"# {heading}", "", str(module.metadata.get("description", "")), "", "## Skills", ""]
    for row in module.metadata.get("catalog", []):
        if row["skill"] in module.skills:
            label = row.get("display-name") or row["skill"]
            catalog.append(f"- `{row['skill']}` — {label}. {row.get('description', '')}")
    if not any(line.startswith("- ") for line in catalog):
        catalog.extend(f"- `{member}`" for member in members)
    resources = {
        "SKILL.md": native.File(entry.encode("utf-8"), 0o644),
        MANIFEST: native.File(("\n".join(registration) + "\n").encode("utf-8"), 0o644),
        "help/help.md": native.File(("\n".join(catalog) + "\n").encode("utf-8"), 0o644),
    }
    roster = []
    for agent in module.metadata.get("agents", []):
        if isinstance(agent, dict) and agent.get("code") in module.skills:
            identifier = agent["code"]
            lines = ["[[members]]", "code = " + quote(identifier), "skill = " + quote(identifier)]
            for old, new in (("name", "name"), ("title", "title"), ("icon", "icon"), ("description", "persona")):
                if isinstance(agent.get(old), str):
                    lines.append(f"{new} = {quote(agent[old])}")
            roster.extend(lines + [""])
    if roster:
        resources["roster.toml"] = native.File("\n".join(roster).encode("utf-8"), 0o644)
    module.skills[record] = native.Snapshot(resources, ("help",))
    module.conversion = {
        "record": record, "update_source": update_source, "configuration_questions": mapped_questions,
        "preserved_legacy_semantics_for_review": ["directory setup", "result substitutions", "select constraints", "old runtime paths"],
    }


def read_modules(sources, legacy_version):
    modules = {}
    for source in sources:
        source = fs.safe_path(source)
        require(source.is_dir(), "Module source must be a local directory")
        first = fs.safe_path(source / MANIFEST)
        candidates = [first] if first.exists() else [
            path for folder in sorted(source.iterdir()) if folder.is_dir()
            if (path := fs.safe_path(folder / MANIFEST)).exists()
        ]
        records = [(path.parent, document) for path in candidates
                   if "bmod" in (document := toml(entry(path)))]
        if records:
            found = [modern(path, document) for path, document in records]
        else:
            legacy_path = fs.safe_path(source / "module.yaml")
            if not legacy_path.exists():
                matches = [path for folder in sorted(source.iterdir()) if folder.is_dir()
                           if (path := fs.safe_path(folder / "module.yaml")).exists()]
                require(len(matches) == 1, "Specify a single module source with bmod.toml or module.yaml: " + str(source))
                legacy_path = matches[0]
            found = [legacy(source, legacy_path, legacy_version)]
        for module in found:
            require(module.code not in modules, "Two inputs use module code " + module.code)
            modules[module.code] = module
    return modules


def materialize_runtime(module, output, layout):
    for member, registration in module.registrations.items():
        for path in array(registration.get("scripts", []), "member scripts"):
            path = fs.relative_file(path)
            require(path.startswith("scripts/") and path in module.skills[member].files,
                    "Missing registered script " + member + "/" + path)
            output.file(f"{layout.runtime}/{module.code}/{path}", module.skills[member].files[path])


def materialize_shared_runtime(paths, output, layout):
    sources = []
    for supplied in paths:
        path = fs.safe_path(supplied)
        require(path.is_dir(), "Shared runtime must be an existing directory")
        scripts = sorted(path.glob("*.py"))
        require(scripts, "Shared runtime directory must contain Python source files")
        sources.append(str(path))
        for script in scripts:
            relative = layout.runtime + "/scripts/" + script.name
            item = entry(script)
            existing = output.files.get(native.portable_key(relative))
            if existing is None:
                output.file(relative, item)
            else:
                require(existing == (relative, item), "Shared runtime paths or bytes conflict: " + relative)
    return sources


class Output:
    def __init__(self):
        self.files = {}
        self.directories = {}
        self.bytes = 0

    def directory(self, path):
        path = fs.relative_file(path)
        key = native.portable_key(path)
        if key in self.directories:
            require(self.directories[key] == path, "Directory alias in stage: " + path)
            return
        require(key not in self.files, "Directory conflicts with a file: " + path)
        parent = Path(path).parent.as_posix()
        if parent != ".":
            self.directory(parent)
        self.directories[key] = path
        self.check_bounds()

    def check_bounds(self):
        require(len(self.files) + len(self.directories) <= native.MAX_FILES
                and self.bytes <= native.MAX_TOTAL_BYTES, "Module stage exceeds size limits")

    def file(self, path, item):
        path = fs.relative_file(path)
        key = native.portable_key(path)
        require(key not in self.directories and key not in self.files, "Stage path collision: " + path)
        parent = Path(path).parent.as_posix()
        if parent != ".":
            self.directory(parent)
        self.files[key] = (path, item)
        self.bytes += len(item.content)
        self.check_bounds()

    def tree(self, path, snapshot):
        self.directory(path)
        for relative in snapshot.directories:
            self.directory(path + "/" + relative)
        for relative, item in snapshot.files.items():
            self.file(path + "/" + relative, item)

    def identity(self):
        return {"files": {path: item.identity() for path, item in sorted(self.files.values())},
                "directories": sorted(self.directories.values())}


def dependencies(modules, members, blockers):
    reports = []
    for module in modules.values():
        for owner, metadata in [(module.code, module.metadata), *module.registrations.items()]:
            for group, needed in (("required_skills", True), ("recommended_skills", False)):
                for item in array(metadata.get(group, []), group):
                    if isinstance(item, str):
                        dependency, wanted_source, minimum = name(item, "dependency"), None, None
                    else:
                        native.object_keys(item, ("skill", "source"), ("version",))
                        dependency = name(item["skill"], "dependency")
                        wanted_source = text(item["source"], "dependency source")
                        minimum = item.get("version")
                        if minimum is not None:
                            version_key(minimum)
                    actual = members.get(dependency)
                    observed = actual and actual.version
                    if actual is None:
                        status = "missing"
                    elif wanted_source and actual.metadata.get("update_source") != wanted_source:
                        status = "source-mismatch"
                    elif minimum and not version_satisfies(observed, minimum):
                        status = "outdated"
                    else:
                        status = "resolved"
                    row = {"owner": owner, "skill": dependency, "required": needed, "source": wanted_source,
                           "observed_module": actual.code if actual else None,
                           "minimum": minimum, "observed_version": observed, "status": status}
                    reports.append(row)
                    if needed and status != "resolved":
                        blockers.append({"dependency": row})
    return reports


def configure(project, modules, retired, output, plan, layout):
    def configuration(path, destination, item):
        plan["configuration_inputs"][path] = item.identity()
        if destination.endswith(".user.toml"):
            item = native.File(item.content, 0o600)
        output.file(destination, item)

    central_path = layout.runtime + "/config.toml"
    central = fs.safe_path(project / central_path)
    if central.exists():
        item = entry(central)
        toml(item)
        configuration(central_path, central_path, item)
    elif any(module.format == "bmod" for module in modules.values()):
        initial = (
            "[core]\nproject_name = " + json.dumps(project.name, ensure_ascii=False)
            + "\noutput_folder = " + json.dumps("{project-root}/" + layout.artifacts, ensure_ascii=False) + "\n"
        )
        output.file(central_path, native.File(initial.encode("utf-8"), 0o600))
    legacy_user_path = layout.runtime + "/config.user.toml"
    legacy_user = fs.safe_path(project / legacy_user_path)
    if legacy_user.exists():
        item = entry(legacy_user)
        toml(item)
        configuration(legacy_user_path, legacy_user_path, item)
    for module in modules.values():
        relative = f"{layout.runtime}/{module.code}/config.yaml"
        original = fs.safe_path(project / relative)
        if module.format == "module.yaml" and original.exists():
            item = entry(original)
            legacy_yaml(item)
            configuration(relative, relative, item)
    custom_path = layout.runtime + "/custom/"
    custom = fs.safe_path(project / custom_path)
    snapshot = native.read_tree(custom) if custom.exists() else native.Snapshot({})
    for directory in snapshot.directories:
        output.directory(custom_path + directory)
    names = set(snapshot.files)
    rename_targets = set()
    for path, item in sorted(snapshot.files.items()):
        destination = path
        if "/" not in path and path.endswith(".toml"):
            toml(item)
            suffix = ".user.toml" if path.endswith(".user.toml") else ".toml"
            identifier = path[:-len(suffix)]
            if identifier in retired:
                replacement = retired[identifier]
                if replacement is None:
                    plan["retired_customizations"].append({"path": path, "preserved": True})
                else:
                    destination = replacement + suffix
                    if destination in names or destination in rename_targets:
                        plan["blockers"].append({"path": path, "target": destination,
                                                 "reason": "Renamed override conflicts with an existing override"})
                        destination = path
                    else:
                        rename_targets.add(destination)
                        plan["customization_moves"].append({
                            "from": path, "to": destination, "scope": "user" if suffix.startswith(".user") else "team",
                            "sha256": item.identity()["sha256"],
                        })
        configuration(custom_path + path, custom_path + destination, item)
    if snapshot.files and ".gitignore" not in snapshot.files:
        output.file(custom_path + ".gitignore", native.File(b"*.user.toml\n", 0o644))


def selected_migrations(path, project, modules, output, layout, accepted_schema):
    if path is None:
        return None
    path = fs.safe_path(path)
    raw = entry(path)
    document = native.object_keys(fs.strict_json_loads(raw.content.decode("utf-8")),
                                  ("schema", "module", "number", "definition_sha256", "roots", "files"))
    require(document["schema"] == accepted_schema, "Unknown project migration format")
    module = modules.get(name(document["module"], "migration module"))
    require(type(document["number"]) is int and module is not None
            and document["number"] in module.migrations, "Select a numbered migration from this import")
    definition = module.migrations[document["number"]]
    require(definition["sha256"] == document["definition_sha256"], "Migration guide changed after planning")
    roots = [project_directory(value) for value in array(document["roots"], "migration roots")]
    require(roots, "Select one or more project artifact roots")
    observed, directories = {}, set()
    for root in roots:
        require(not overlaps(root, layout.runtime), "Migration root overlaps the module runtime: " + root)
        snapshot = native.read_tree(project / root)
        directories.add(root)
        directories.update(root + "/" + directory for directory in snapshot.directories)
        for relative, item in snapshot.files.items():
            location = root + "/" + relative
            require(location not in observed, "Overlapping migration roots at " + location)
            observed[location] = item
    results = []
    changed = {}
    for row in array(document["files"], "migration files"):
        native.object_keys(row, ("path", "sha256", "to"), ("replacement",))
        location, destination = fs.relative_file(row["path"]), fs.relative_file(row["to"])
        require(location in observed and location not in changed, "Missing or duplicate migration source: " + location)
        original = observed[location]
        require(row["sha256"] == original.identity()["sha256"], "Migration source changed: " + location)
        require(any(destination.startswith(root + "/") for root in roots),
                "Migration destination falls outside the selected roots: " + destination)
        item = original
        if "replacement" in row:
            replacement = entry(native.source_path(path.parent, row["replacement"]))
            item = native.File(replacement.content, original.mode)
        require(location != destination or item != original, "Migration file has no change: " + location)
        changed[location] = (destination, item)
        results.append({"source": location, "destination": destination,
                        "before": original.identity(), "after": item.identity()})
    final_files = [changed.get(location, (location, item)) for location, item in observed.items()]

    def parent_paths(paths):
        return {parent.as_posix() for path in paths for parent in Path(path).parents}

    emptied = (directories & parent_paths(observed)) - parent_paths(path for path, _ in final_files)
    emptied -= set(roots)
    for location in sorted(directories - emptied):
        output.directory(location)
    for location, item in final_files:
        output.file(location, item)
    return {"module": module.code, "number": document["number"], "definition_sha256": definition["sha256"],
            "change_set_sha256": raw.identity()["sha256"], "roots": roots,
            "input": {location: item.identity() for location, item in sorted(observed.items())},
            "changes": results, "emptied_source_directories": sorted(emptied),
            "guide_checklist_pending": definition["checklist"]}


def contract(module):
    known = BMOD_FIELDS | {"roster"}
    unsupported = sorted(set(module.metadata) - known) if module.format == "bmod" else []
    member_fields = {key: sorted(set(value) - SKILL_FIELDS) for key, value in module.registrations.items()}
    return {
        "code": module.code, "version": module.version, "format": module.format,
        "source": str(module.source), "record": module.record, "metadata": module.metadata,
        "members": sorted(module.skills), "registrations": module.registrations,
        "legacy_registration_conversion": module.conversion,
        "excluded_legacy_interpreter_cache": module.exclusions,
        "retired": module.retired, "numbered_migrations": [
            {"number": number, **migration} for number, migration in sorted(module.migrations.items())
        ],
        "preserved_unapplied_fields": {
            "module": unsupported, "skills": {key: fields for key, fields in member_fields.items() if fields},
        },
    }


def verify_collisions(project, members, previous_modules, plan):
    prior = {name: snapshot.identity() for module in previous_modules.values()
             for name, snapshot in module.skills.items()}
    existing = native.target_members(project)["skill"]
    for name, candidate in members.items():
        location = native.SKILLS / name
        for path in existing.get(native.portable_key(name), []):
            actual = native.read_tree(path, bounded=False).identity() if path.is_dir() and not path.is_symlink() else None
            classified = "identical" if actual == candidate.identity() else "reviewed-previous" if actual and prior.get(name) == actual else "unknown"
            row = {"name": name, "path": path.relative_to(project).as_posix(),
                   "classification": classified, "identity": actual}
            plan["target_entries"].append(row)
            if classified == "unknown" or row["path"] != location.as_posix():
                plan["blockers"].append({"path": row["path"], "reason": "Existing native entry differs or aliases this import"})


def audit(args):
    project = fs.safe_path(args.project)
    require(project.is_dir(), "The audited project directory must already exist")
    modules = read_modules(args.source, args.legacy_version)
    prior = read_modules(args.previous, args.previous_legacy_version or args.legacy_version)
    layout = Layout(args.runtime_root, args.artifact_root)
    plan = {"schema": "codex-agents.module-import-plan/1", "project": str(project), "modules": [], "configuration_inputs": {},
            "layout": {"runtime_root": layout.runtime, "artifact_root": layout.artifacts},
            "customization_moves": [], "retired_customizations": [], "target_entries": [], "blockers": [],
            "operator_steps": ["review-code-and-prompts", "answer-module-setup-questions-where-needed",
                               "review-and-run-numbered-migration-checklist", "open-and-test-staged-codex-project"]}
    output = Output()
    members, snapshots, retired = {}, {}, {}
    for module in modules.values():
        if module.format == "module.yaml" and getattr(args, "convert_legacy", None):
            convert_legacy(module, args.convert_legacy)
        plan["modules"].append(contract(module))
        for member, snapshot in module.skills.items():
            require(member not in members, "Duplicate member across imported modules: " + member)
            members[member], snapshots[member] = module, snapshot
            output.tree((native.SKILLS / member).as_posix(), snapshot)
        for old, new in module.retired.items():
            require(old not in retired, "Duplicate retired skill across imported modules: " + old)
            retired[old] = new
        for relative, item in module.resources.items():
            output.file(f".module-import/modules/{module.code}/{relative}", item)
        materialize_runtime(module, output, layout)
    require(not (retired.keys() & members.keys()), "A retired skill is present in another imported module")
    plan["shared_runtime"] = materialize_shared_runtime(args.shared_runtime, output, layout)
    for index, license_path in enumerate(args.license, 1):
        license_path = fs.safe_path(license_path)
        output.file(f".module-import/licenses/{index}-{license_path.name}", entry(license_path))
    plan["dependencies"] = dependencies(modules, members, plan["blockers"])
    configure(project, modules, retired, output, plan, layout)
    plan["migration"] = selected_migrations(args.change_set, project, modules, output, layout, args.change_set_schema)
    verify_collisions(project, snapshots, prior, plan)
    for old, new in sorted(retired.items()):
        path = fs.safe_path(project / native.SKILLS / old)
        if path.exists():
            plan["target_entries"].append({
                "name": old, "path": path.relative_to(project).as_posix(), "classification": "retired",
                "successor": new, "identity": native.read_tree(path, bounded=False).identity(),
            })
    plan["ready"] = not plan["blockers"]
    plan["output"] = output.identity()
    plan["plan_sha256"] = fs.digest(fs.encode(plan))
    return plan, output


def stage(args):
    plan, snapshot = audit(args)
    require(plan["ready"], "Resolve plan blockers before staging")
    require(args.expect == plan["plan_sha256"], "Reviewed import plan or its inputs have changed")
    output = fs.safe_path(args.output)
    require(not output.exists() and output.parent.is_dir(), "Output must be a fresh directory with an existing parent")
    project = Path(plan["project"])
    require(output != project and project not in output.parents, "Stage outside the audited project")
    for source in [*args.source, *args.previous, *args.shared_runtime]:
        source = fs.safe_path(source)
        require(output != source and source not in output.parents, "Stage outside the source modules")
    material = plan["migration"] is not None and bool(plan["migration"]["changes"])
    choice_root = getattr(args, "choice_root", None) or project
    choice = native.material_choice(choice_root, plan) if material else None
    lock = output.with_name("." + output.name + ".module-import-lock")
    lock.mkdir(mode=0o700)
    try:
        temp = Path(tempfile.mkdtemp(prefix=".module-import-", dir=output.parent))
        try:
            for path in sorted(snapshot.directories.values()):
                (temp / path).mkdir(parents=True, exist_ok=True)
            for path, item in sorted(snapshot.files.values()):
                fs.write_file(temp / path, item.content, item.mode)
            refreshed, _ = audit(args)
            require(refreshed["plan_sha256"] == args.expect, "Inputs changed while writing the staged project")
            receipt = {"schema": RECEIPT_SCHEMA, "plan": plan, "root": str(output),
                       "source_project_writes": 0, "hooks_executed": 0}
            if material:
                require(native.material_choice(choice_root, refreshed) == choice,
                        "Production choice changed while staging; rerun the reviewed plan")
                receipt["production_choice"] = choice
            fs.write_file(temp / RECEIPT, fs.encode(receipt), 0o600)
            require(not output.exists(), "Staging output already exists")
            temp.rename(output)
            return receipt
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    finally:
        lock.rmdir()


def verify(output, expect, receipt_name=RECEIPT, receipt_schema=RECEIPT_SCHEMA):
    output = fs.safe_path(output)
    require(output.is_dir(), "Expected a staged directory")
    require("/" not in fs.relative_file(receipt_name), "Receipt must be a top-level file name")
    receipt = fs.read_json(output / receipt_name)
    require(receipt.get("schema") == receipt_schema and receipt.get("root") == str(output),
            "Receipt refers to another stage")
    plan = dict(receipt["plan"])
    stored = plan.pop("plan_sha256")
    require(stored == expect == fs.digest(fs.encode(plan)), "Staged receipt differs from the reviewed plan")
    actual = native.read_tree(output, bounded=False)
    del actual.files[receipt_name]
    require(actual.identity() == plan.get("output"), "Observed stage bytes, paths, or modes differ from the reviewed plan")
    return {"ready": True, "verified_files": len(actual.files), "plan_sha256": expect, "root": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("audit", "stage"):
        command = commands.add_parser(action)
        command.add_argument("--source", type=Path, required=True, action="append")
        command.add_argument("--project", type=Path, required=True)
        command.add_argument("--previous", type=Path, action="append", default=[])
        command.add_argument("--legacy-version")
        command.add_argument("--previous-legacy-version")
        command.add_argument("--runtime-root", default=Layout.runtime)
        command.add_argument("--artifact-root", default=Layout.artifacts)
        command.add_argument("--shared-runtime", "--legacy-runtime", type=Path, action="append", default=[])
        command.add_argument("--convert-legacy", metavar="UPDATE_SOURCE")
        command.add_argument("--license", type=Path, action="append", default=[])
        command.add_argument("--change-set", type=Path)
        command.add_argument("--change-set-schema", default=CHANGE_SET_SCHEMA)
        if action == "audit":
            command.add_argument("--plan-file", type=Path, help="Also save exact canonical JSON to this new file")
        else:
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--expect", required=True)
            command.add_argument("--choice-root", type=Path,
                                 help="Approved production decision directory; defaults to the audited project")
    checker = commands.add_parser("verify")
    checker.add_argument("--output", type=Path, required=True)
    checker.add_argument("--expect", required=True)
    checker.add_argument("--receipt-name", default=RECEIPT)
    checker.add_argument("--receipt-schema", default=RECEIPT_SCHEMA)
    args = parser.parse_args()
    try:
        if args.action == "audit":
            result = audit(args)[0]
            if args.plan_file:
                native.export_audit_plan(args.plan_file, result)
        elif args.action == "stage":
            result = stage(args)
        else:
            result = verify(args.output, args.expect, args.receipt_name, args.receipt_schema)
        print(fs.encode(result).decode(), end="")
        return 0 if result.get("ready", True) else 2
    except (OSError, ValueError, TypeError, KeyError, fs.InstallError) as error:
        print(json.dumps({"ready": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
