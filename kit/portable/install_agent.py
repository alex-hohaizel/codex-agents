#!/usr/bin/env python3
"""Install a declared agent skill set into one project; Python standard library only.

No network, package installation, account changes, or project-state migration occurs.
A kit has manifest.json and skills/<declared skill name>/. See --help.

Requires exclusive control of kit/project ancestor directories during operations.
Observed links/special files and final-leaf races are checked; this is not a
sandbox against hostile same-user processes replacing ancestor directories.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
from urllib.parse import unquote, urlsplit
import uuid
import xml.etree.ElementTree as ET



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

LOCK = Path(".agents/.agent-install.lock")
BACKUPS = Path(".agents/agent-install-backups")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def valid_name(value):
    return isinstance(value, str) and 1 <= len(value) <= 64 and NAME.fullmatch(value)


def state_path(agent_id):
    return Path(".agents/agent-installs") / (agent_id + ".json")


def markers(agent_id):
    return "<!-- AGENT_INSTALL:BEGIN " + agent_id + " -->", "<!-- AGENT_INSTALL:END " + agent_id + " -->"


HEX = re.compile(r"^[0-9a-f]{64}$")
OPERATING_SCHEMA = "agent-operating-standard/1"
OPERATING_RESOURCES = (
    "references/adaptive-work.md", "references/research-and-synthesis.md",
    "references/visual-identity.md", "references/joint-work-codex.md",
    "scripts/adaptive_work.py", "scripts/visual_identity.py", "assets/adaptive-task.schema.json", "assets/adaptive-task.example.json",
    "references/production-quality.md", "references/context-capsule.md",
    "assets/production-profiles.json", "scripts/context_capsule.py",
    "references/ai-production.md", "assets/ai-production.schema.json", "scripts/ai_production.py",
    "references/managed-execution.md", "assets/managed-model.json",
    "references/briefing-protocol.md", "references/interaction-protocol.md", "references/tool-compatibility.md",
    "scripts/briefing.py", "scripts/interaction.py",
    "assets/status-view.schema.json", "assets/decision-card.template.md",
)
PORTABLE_BRIEFING_MATERIALS = {
    "assets/briefing-intake.template.json", "assets/execution-script.template.md",
    "assets/stage-closeout.template.md", "references/briefing-domain-guide.md",
    "assets/briefing-topics.json",
}
LEGACY_OPERATING_RESOURCES = OPERATING_RESOURCES[:8]
V6_0_OPERATING_RESOURCES = OPERATING_RESOURCES[:12]
V6_1_OPERATING_RESOURCES = OPERATING_RESOURCES[:15]
VISUAL_FIELDS = ("icon_small", "icon_large", "brand_color")


class InstallError(Exception):
    pass


def operating_resources_for_release(release):
    """Preserve each known declared contract; never infer future inheritance."""
    version = tuple(int(part) for part in release.split('.'))
    if version[0] < 6:
        return LEGACY_OPERATING_RESOURCES
    if version[:2] == (6, 0):
        return V6_0_OPERATING_RESOURCES
    if version[:2] == (6, 1):
        return V6_1_OPERATING_RESOURCES
    if version[:2] == (6, 6):
        return OPERATING_RESOURCES
    raise InstallError("Unsupported future generated-agent operating standard")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    """Check every existing component with lstat; never resolve through a link."""
    path = Path(os.path.abspath(os.fspath(path)))
    for part in reversed((path,) + tuple(path.parents)):
        try:
            mode = part.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise InstallError("Symlink is not permitted: " + str(part))
        if part != path and not stat.S_ISDIR(mode):
            raise InstallError("Path ancestor is not a directory: " + str(part))
    return path


def relative_file(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise InstallError("Invalid manifest file path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in (".", "..", "") for p in value.split("/")):
        raise InstallError("Unsafe manifest file path: " + value)
    return value


def read_bytes(path):
    path = safe_path(path)
    # Inspect before open: opening a FIFO read-only can block before fstat.
    # NONBLOCK closes the replacement race between this lstat and open.
    if not stat.S_ISREG(path.lstat().st_mode):
        raise InstallError("Expected a regular file: " + str(path))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InstallError("Expected a regular file: " + str(path))
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(fd)


def read_json(path):
    try:
        return strict_json_loads(read_bytes(path).decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise InstallError("Invalid UTF-8 JSON: " + str(path)) from error


def file_map(root):
    root = safe_path(root)
    if not root.exists():
        return None
    if not root.is_dir():
        raise InstallError("Expected a skill directory: " + str(root))
    files = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        for name in directories + filenames:
            entry = Path(current) / name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise InstallError("Link or special file is not permitted: " + str(entry))
        for name in filenames:
            path = Path(current) / name
            files[path.relative_to(root).as_posix()] = digest(read_bytes(path))
    return files


def file_mode(path):
    path = safe_path(path)
    observed = path.lstat()
    if not stat.S_ISREG(observed.st_mode):
        raise InstallError("Expected a regular file: " + str(path))
    if observed.st_mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX):
        raise InstallError("Special permission bits are not supported: " + str(path))
    return stat.S_IMODE(observed.st_mode)


def mode_map(root, files):
    return {relative: file_mode(root / relative) for relative in files}


def validate_files(files):
    if not isinstance(files, dict) or "SKILL.md" not in files:
        raise InstallError("Each skill must contain a hashed SKILL.md")
    for key, value in files.items():
        relative_file(key)
        if not isinstance(value, str) or not HEX.fullmatch(value):
            raise InstallError("Invalid SHA-256 for " + key)


def validate_modes(modes, files):
    if not isinstance(modes, dict) or set(modes) != set(files):
        raise InstallError("Manifest must record permission bits for every skill file")
    for value in modes.values():
        if type(value) is not int or not 0 <= value <= 0o777:
            raise InstallError("Invalid POSIX file permission bits")


def validate_skill(kit, name):
    """Check portable package structure, not the artistic quality of instructions."""
    root = kit / "skills" / name
    try:
        text = read_bytes(root / "SKILL.md").decode("utf-8")
    except UnicodeError as error:
        raise InstallError("SKILL.md must be UTF-8: " + name) from error
    validate_skill_text(root, name, text)


def validate_skill_text(root, name, text):
    """Validate captured skill instructions against their own resource root."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n")
    parts = text.split("\n---\n", 1) if text.startswith("---\n") else []
    if len(parts) != 2:
        raise InstallError("SKILL.md requires frontmatter and a nonempty body: " + name)
    frontmatter, body = parts[0][4:], parts[1]
    fields = {}
    for key in ("name", "description"):
        matches = list(re.finditer(r"^" + key + r":[ \t]*(.*)$", frontmatter, re.MULTILINE))
        if len(matches) != 1:
            raise InstallError("SKILL.md needs one " + key + " field: " + name)
        value = matches[0].group(1).strip()
        following = frontmatter[matches[0].end():].splitlines()
        continuation = []
        for line in following:
            if not line.strip():
                continue
            if not line.startswith((" ", "\t")):
                break
            continuation.append(line.strip())
        if key == "description" and value in ("|", "|-", "|+", ">", ">-", ">+"):
            value = " ".join(continuation)
        elif value.startswith(("\"", "'")):
            value = " ".join([value] + continuation)
            if value[0] == '"':
                try:
                    decoded, finish = json.JSONDecoder().raw_decode(value)
                    tail = value[finish:].strip()
                    if tail and not tail.startswith("#"):
                        raise ValueError("Trailing metadata syntax")
                    value = decoded
                except ValueError as error:
                    raise InstallError("Invalid portable quoted metadata: " + name) from error
            else:
                quoted = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
                if quoted is None:
                    raise InstallError("Invalid quoted metadata: " + name)
                value = quoted.group(1).replace("''", "'")
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            if value.startswith("#"):
                value = ""
            scalar_word = value.casefold() in {"null", "~", "true", "false", "yes", "no", "on", "off", ".nan", ".inf", "+.inf", "-.inf"}
            scalar_number = re.fullmatch(r"[-+]?(?:[0-9][0-9_]*(?::[0-9_]+)*(?:\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\.[0-9_]+(?:[eE][-+]?[0-9]+)?|0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+)", value)
            scalar_date = re.fullmatch(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}(?:[Tt \t]+[0-9].*)?", value)
            if scalar_word or scalar_number or scalar_date or value in ("[]", "{}") or value.startswith(("[", "{", "&", "*", "!", "|", ">", "%", "@", "`", "- ", "? ", ": ")) or ": " in value:
                raise InstallError("Metadata must use portable scalar strings; quote ambiguous values: " + name)
        fields[key] = value.strip()
    if fields["name"] != name or not fields["description"] or fields["description"] in ("null", "~") or not body.strip():
        raise InstallError("SKILL.md name/description/body is invalid: " + name)
    # Check ordinary relative Markdown links in the entry instructions. Full
    # reference parsing and domain review remain separate QA responsibilities.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", body):
        target = match.group(1).strip()
        target = target[1:target.index(">")] if target.startswith("<") and ">" in target else target.split()[0]
        parsed = urlsplit(target)
        if parsed.scheme and parsed.scheme != "file":
            continue
        local = unquote(parsed.path)
        if not local:
            continue
        if parsed.scheme == "file" or Path(local).is_absolute() or "\\" in local:
            raise InstallError("Non-portable local SKILL.md reference: " + name + ": " + target)
        destination = safe_path(root / local)
        if (root not in destination.parents and destination != root) or not destination.exists() or not (destination.is_file() or destination.is_dir()):
            raise InstallError("Missing/unsafe local SKILL.md reference: " + name + ": " + target)
        if destination.is_dir() and not file_map(destination):
            raise InstallError("Referenced directory has no delivered files: " + name + ": " + target)


def validate_manifest(value):
    if not isinstance(value, dict) or value.get("format_version") != 1 or value.get("kit_id") != "agent-package":
        raise InstallError("Unsupported delivery manifest")
    for field in ("agent_id", "entry_skill"):
        if not valid_name(value.get(field)):
            raise InstallError("Invalid " + field)
    if not isinstance(value.get("version"), str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", value["version"]):
        raise InstallError("Manifest version must be strict SemVer")
    prerelease = value["version"].split("+", 1)[0].partition("-")[2]
    if any(part.isdigit() and len(part) > 1 and part.startswith("0") for part in prerelease.split(".")):
        raise InstallError("Numeric prerelease identifiers cannot have leading zeros")
    if value.get("purpose") not in ("factory", "generated"):
        raise InstallError("Manifest purpose must be factory or generated")
    pin = value.get("blueprint")
    if value["purpose"] == "generated":
        if not isinstance(pin, dict) or not isinstance(pin.get("id"), str) or not pin["id"] or type(pin.get("revision")) is not int or pin["revision"] < 1 or not HEX.fullmatch(pin.get("sha256", "")) or not isinstance(pin.get("approval_source"), str) or not pin["approval_source"]:
            raise InstallError("Generated package requires exact approved-blueprint provenance")
    elif pin is not None:
        raise InstallError("Factory selfpackage cannot claim a target blueprint approval")
    skills = value.get("skills")
    if not isinstance(skills, list) or not 1 <= len(skills) <= 256:
        raise InstallError("Manifest must contain 1..256 declared skills")
    by_name = {}
    for item in skills:
        if not isinstance(item, dict) or not valid_name(item.get("name")):
            raise InstallError("Invalid skill name")
        name = item["name"]
        if name in by_name or item.get("path") != "skills/" + name:
            raise InstallError("Duplicate skill or unexpected skill path: " + name)
        validate_files(item.get("files"))
        validate_modes(item.get("modes"), item["files"])
        by_name[name] = item
    if value["entry_skill"] not in by_name:
        raise InstallError("Entry skill is not in the declared skill set")
    if value["purpose"] == "factory" and (value["agent_id"] != "agent-foundry" or value["entry_skill"] != "agent-foundry" or set(by_name) != {"agent-foundry"}):
        raise InstallError("Factory purpose is reserved for the constructor's own one-skill package")
    standard = value.get("operating_standard")
    if standard is not None:
        if not isinstance(standard, dict) or standard.get("schema") != OPERATING_SCHEMA or not isinstance(standard.get("release"), str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", standard["release"]):
            raise InstallError("Unsupported generated-agent operating standard")
        resources = standard.get("resources")
        required_resources = operating_resources_for_release(standard['release'])
        if not isinstance(resources, dict) or set(resources) != set(required_resources) or any(not isinstance(h, str) or not HEX.fullmatch(h) for h in resources.values()):
            raise InstallError("Operating standard must pin every portable resource")
        if "assets/managed-model.json" in required_resources:
            model = standard.get("managed_model")
            if not (isinstance(model, dict) and set(model) == {"id"} and
                    isinstance(model["id"], str) and re.fullmatch(r"gpt-[a-z0-9]+(?:[.-][a-z0-9]+)+", model["id"])):
                raise InstallError("Current generated operating standard requires a valid managed model")
        elif "managed_model" in standard:
            raise InstallError("Historical generated operating standard cannot declare a managed model")
        for name, entry in by_name.items():
            if any(entry["files"].get(path) != wanted for path, wanted in resources.items()):
                raise InstallError("Operating-standard resource pin mismatch: " + name)
            if ("scripts/briefing.py" in required_resources and
                    not PORTABLE_BRIEFING_MATERIALS <= entry["files"].keys()):
                raise InstallError("Current operating standard requires the child's complete briefing materials: " + name)
            if not {"assets/visual-identity.lock.json", "assets/visual-identity-origin.json"} <= set(entry["files"]):
                raise InstallError("Operating standard requires project visual identity/provenance: " + name)
    return by_name

def load_kit(kit):
    kit = safe_path(kit)
    manifest = read_json(kit / "manifest.json")
    entries = validate_manifest(manifest)
    skill_root = safe_path(kit / "skills")
    observed = set()
    for item in skill_root.iterdir():
        item = safe_path(item)
        if not item.is_dir():
            raise InstallError("skills/ may contain only declared skill directories")
        observed.add(item.name)
    if observed != set(entries):
        raise InstallError("Declared and actual skill sets differ")
    for name, entry in entries.items():
        actual = file_map(kit / entry["path"])
        if actual != entry["files"]:
            raise InstallError("Kit hash/file-set mismatch for " + name)
        if mode_map(kit / entry["path"], actual) != entry["modes"]:
            raise InstallError("Kit permission mismatch for " + name)
        validate_skill(kit, name)
        if manifest.get("operating_standard") is not None:
            content = read_bytes(kit / entry["path"] / "SKILL.md").decode("utf-8")
            for path in manifest['operating_standard']['resources']:
                if path.startswith("references/") and not re.search(r"\]\((?:\./)?" + re.escape(path) + r"\)", content):
                    raise InstallError("Missing local operating-standard entry link: " + name + ": " + path)
            model = manifest["operating_standard"].get("managed_model")
            if model is not None and read_json(kit / entry["path"] / "assets/managed-model.json") != model:
                raise InstallError("Managed model differs from the pinned policy in " + name)
            validate_project_identity(kit / entry["path"])
    return manifest, entries


def visual_ui(data):
    """Read conservative block-style UI fields without an external YAML parser.

    Unsupported visual YAML stops with an actionable conflict. It is never
    silently normalized into a different instruction or policy mapping.
    """
    text = data.decode("utf-8")
    if text.lstrip().startswith("{"):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise InstallError("Duplicate JSON UI field: " + key)
                result[key] = value
            return result
        value = strict_json_loads(text, object_pairs_hook=unique)
        if not isinstance(value, dict) or not isinstance(value.get("interface", {}), dict):
            raise InstallError("JSON UI interface must be a mapping")
        fields = {key: value["interface"].pop(key) for key in VISUAL_FIELDS if key in value.get("interface", {})}
        if any(not isinstance(v, str) or not v for v in fields.values()):
            raise InstallError("JSON visual metadata must use nonempty strings")
        return fields, encode(value)
    if "\t" in text:
        raise InstallError("Tabbed UI metadata needs explicit parsing before preserving icons")
    lines = text.splitlines(keepends=True)
    fields, cleaned = {}, []
    interface = False
    seen_interface = False
    for line in lines:
        if line.strip() and not line.startswith((" ", "\t", "#")):
            interface = bool(re.fullmatch(r"interface:\s*(?:#.*)?(?:\r?\n)?", line))
            if line.startswith("interface:"):
                if seen_interface or not interface:
                    raise InstallError("Visual metadata needs one block-style interface mapping; review agents/openai.yaml without changing existing icons")
                seen_interface = True
        if interface and line.lstrip().startswith("<<:"):
            raise InstallError("Merged UI metadata needs explicit parsing before preserving icons")
        if interface and re.match(r"^ +(" + "|".join(VISUAL_FIELDS) + r"):", line) and not re.match(r"^  [^ ]", line):
            raise InstallError("Nested/indented visual metadata needs explicit parsing before preserving icons")
        match = re.match(r"^  (" + "|".join(VISUAL_FIELDS) + r"):[ \t]*(.*?)(?:\r?\n)?$", line)
        if not (interface and match):
            cleaned.append(line)
            continue
        key, raw = match.groups()
        if key in fields or not raw or raw.startswith(("|", ">", "&", "*", "!", "[", "{")):
            raise InstallError("Ambiguous visual metadata; review " + key + " before update")
        if raw.startswith('"'):
            try:
                value, finish = json.JSONDecoder().raw_decode(raw)
            except ValueError as error:
                raise InstallError("Invalid quoted visual metadata: " + key) from error
            if raw[finish:].strip() and not raw[finish:].lstrip().startswith("#"):
                raise InstallError("Unexpected trailing visual metadata: " + key)
        elif raw.startswith("'"):
            m = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", raw)
            if not m:
                raise InstallError("Invalid quoted visual metadata: " + key)
            value = m.group(1).replace("''", "'")
        else:
            value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
        if not isinstance(value, str) or not value or value.casefold() in ("null", "true", "false", "~"):
            raise InstallError("Visual metadata must be a nonempty string: " + key)
        fields[key] = value
    return fields, "".join(cleaned).encode("utf-8")


def icon_paths(fields):
    result = set()
    for key in ("icon_small", "icon_large"):
        if key in fields:
            path = fields[key][2:] if fields[key].startswith("./") else fields[key]
            relative_file(path)
            if Path(path).suffix.casefold() not in {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}:
                raise InstallError("Icon must name a local image asset: " + path)
            result.add(path)
    return result


def overlay_ui(data, fields):
    _, cleaned = visual_ui(data)
    if data.decode("utf-8").lstrip().startswith("{"):
        value = strict_json_loads(cleaned)
        value.setdefault("interface", {}).update(fields)
        return encode(value)
    additions = "".join("  " + key + ": " + json.dumps(fields[key], ensure_ascii=False) + "\n" for key in VISUAL_FIELDS if key in fields)
    text = cleaned.decode("utf-8")
    match = re.search(r"(?m)^interface:\s*(?:#.*)?\r?\n", text)
    if match:
        return (text[:match.end()] + additions + text[match.end():]).encode("utf-8")
    if text.strip() and not text.endswith("\n"):
        text += "\n"
    return ("interface:\n" + additions + text).encode("utf-8")


def visual_snapshot(root):
    ui = root / "agents/openai.yaml"
    if not ui.exists():
        return None
    fields, non_visual = visual_ui(read_bytes(ui))
    if not icon_paths(fields):
        return None
    return {"interface": fields, "non_visual_ui_sha256": digest(non_visual),
            "icons": {path: {"sha256": digest(read_bytes(root / path)), "mode": file_mode(root / path)} for path in sorted(icon_paths(fields))}}


def validate_project_identity(root):
    """Validate generated visual identity; legacy API name also accepts system tools.

    Installation inside a project does not classify a reusable tool as a
    project-specific agent. A class is not an authorization or quality proof.
    """
    observed = visual_snapshot(root)
    if observed is None:
        raise InstallError("Generated operating standard requires actual icons")
    lock = read_json(root / "assets/visual-identity.lock.json")
    kind = lock.get("class") if isinstance(lock, dict) else None
    if kind not in ("project", "system"):
        raise InstallError("Visual class must be project or system, chosen by accepted task purpose")
    current = {"schema": "visual-identity/1", "class": kind, "interface": observed["interface"],
               "files": {name: value["sha256"] for name, value in observed["icons"].items()}, "regenerate_on_update": False}
    if lock != current:
        raise InstallError("Visual lock differs from actual declared-class icon paths/bytes/colors")
    origin = read_json(root / "assets/visual-identity-origin.json")
    if not isinstance(origin, dict) or origin.get("schema") != "visual-identity-origin/1":
        raise InstallError("Generated icon provenance is missing")
    if kind == "system" and not reusable_system_basis(origin):
        raise InstallError("System class requires reusable_system scope and scope_basis source/reason; no global permissions are granted by this classification")
    if origin.get("kind") == "created":
        if kind == "project" and any(not name.endswith(".svg") or not project_style(read_bytes(root / name)) for name in current["files"]):
            raise InstallError("New project icons require project-card-v1 style")
        if kind == "system":
            reference, sample = bound_visual_asset(root, origin.get("style_reference"), "Reusable system style reference")
            if reference in current["files"] or Path(reference).suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}:
                raise InstallError("New system icon requires a separate actual existing system-style image sample")
            if project_style(sample) or b"agent-style:project-card-v1" in sample or any(project_style(read_bytes(root / name)) or b"agent-style:project-card-v1" in read_bytes(root / name) for name in current["files"]):
                raise InstallError("Project-card imagery cannot become a newly created reusable system icon/style by relabeling")
    elif origin.get("kind") == "preserved":
        binding = origin.get("prior_snapshot")
        if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not HEX.fullmatch(str(binding.get("sha256", ""))):
            raise InstallError("Preserved project icon requires bound prior snapshot")
        rel = PurePosixPath(relative_file(binding["path"]))
        if not rel.parts or rel.parts[0] != "assets":
            raise InstallError("Prior icon snapshot must be bundled under assets/")
        prior = read_bytes(root / rel)
        if digest(prior) != binding["sha256"] or strict_json_loads(prior) != current:
            raise InstallError("Preserved project icon differs from its bound prior snapshot")
    else:
        raise InstallError("Generated icon origin must be created or preserved")


def reusable_system_basis(origin):
    basis = origin.get("scope_basis")
    return (origin.get("scope") == "reusable_system" and isinstance(basis, dict)
            and all(isinstance(basis.get(key), str) and basis[key].strip() for key in ("source", "reason")))


def bound_visual_asset(root, binding, label):
    if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not HEX.fullmatch(str(binding.get("sha256", ""))):
        raise InstallError(label + " requires a bound actual asset")
    rel = PurePosixPath(relative_file(binding["path"]))
    if not rel.parts or rel.parts[0] != "assets" or ":" in binding["path"]:
        raise InstallError(label + " must be bundled under a portable assets path")
    data = read_bytes(root / rel)
    if digest(data) != binding["sha256"]:
        raise InstallError(label + " differs from its bound source")
    return rel.as_posix(), data


def project_style(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return False
    tag = lambda element: element.tag.rsplit("}", 1)[-1]
    elements = list(root.iter())
    return (tag(root) == "svg" and root.get("viewBox") == "0 0 96 96"
            and any(tag(e) == "metadata" and e.text == "agent-style:project-card-v1" for e in elements)
            and any(tag(e) == "polygon" and e.get("points") == "4,4 72,4 92,24 92,92 4,92" and e.get("stroke") == "#0F766E" and e.get("fill") == "#F8FAFC" for e in elements)
            and any(tag(e) == "text" and e.get("x") == "48" and e.get("y") == "85" and e.text == "PROJECT" for e in elements))


def visual_drift_only(root, actual, previous, baseline):
    if not isinstance(baseline, dict) or not isinstance(baseline.get("interface"), dict) or not HEX.fullmatch(baseline.get("non_visual_ui_sha256", "")):
        return False
    current = visual_snapshot(root)
    if current is None or current["non_visual_ui_sha256"] != baseline["non_visual_ui_sha256"]:
        return False
    permitted = icon_paths(baseline["interface"]) | set(current["icons"]) | {"agents/openai.yaml"}
    all_paths = set(actual["files"]) | set(previous["files"])
    return all(path in permitted or (actual["files"].get(path) == previous["files"].get(path) and actual["modes"].get(path) == previous["modes"].get(path)) for path in all_paths)

def write_manifest(kit, metadata):
    """Low-level data operation; caller must enforce actual construction authority."""
    kit = safe_path(kit)
    skill_root = safe_path(kit / "skills")
    if not skill_root.is_dir():
        raise InstallError("Kit requires skills/")
    skills = []
    for folder in sorted(skill_root.iterdir()):
        folder = safe_path(folder)
        if not folder.is_dir() or not valid_name(folder.name):
            raise InstallError("Invalid skill directory")
        name = folder.name
        files = file_map(folder)
        validate_files(files)
        if any("__pycache__" in Path(f).parts or f.endswith(".pyc") for f in files):
            raise InstallError("Remove generated bytecode caches before packaging")
        validate_skill(kit, name)
        skills.append({"name": name, "path": "skills/" + name, "files": files, "modes": mode_map(folder, files)})
    value = dict(metadata, format_version=1, kit_id="agent-package", skills=skills)
    validate_manifest(value)
    destination = safe_path(kit / "manifest.json")
    if destination.exists() and not destination.is_file():
        raise InstallError("Manifest destination is not a regular file")
    temporary = destination.with_name(".manifest-" + uuid.uuid4().hex + ".json")
    write_file(temporary, encode(value), file_mode(destination) if destination.exists() else 0o644)
    os.replace(temporary, destination)
    return value

def managed_block(manifest, manifest_hash):
    begin, end = markers(manifest["agent_id"])
    model = (manifest.get("operating_standard") or {}).get("managed_model")
    model_instruction = (
        "Launch from this project with `codex --model " + model["id"] +
        "` or use the supported host picker. Check actual session metadata before crediting managed execution.\n"
        if model is not None else ""
    )
    return (begin + "\n"
        "## Agent: " + manifest["agent_id"] + "\n\n"
        "For work assigned to this agent, read `.agents/skills/" + manifest["entry_skill"] + "/SKILL.md` first.\n"
        "Use that single entry point to select the relevant specialist modules; the user need not invoke them.\n"
        "Reconcile current requirements, approved scope, source/evidence hashes, capabilities and pause boundaries.\n"
        "Use actual host tools and observed receipts; instructions do not install tools or grant external permissions.\n"
        "Preserve existing product source, version control, project state, accepted originals and unrelated instructions.\n"
        "Use one active instruction source for this agent; report overlapping profile/plugin copies without disabling them.\n"
        + model_instruction +
        "Installed version: " + manifest["version"] + "; manifest SHA-256: " + manifest_hash + ".\n" + end)

def split_block(text, agent_id):
    begin, end = markers(agent_id)
    starts, ends = text.count(begin), text.count(end)
    if not starts and not ends:
        return None
    if starts != 1 or ends != 1 or text.index(begin) > text.index(end):
        raise InstallError("AGENTS.md has ambiguous/incomplete agent markers")
    start = text.index(begin)
    finish = text.index(end) + len(end)
    return start, finish, text[start:finish]

def plan_install(kit, project, other_sources=(), allow_remove_owned=False):
    project = safe_path(project)
    if project.exists() and not project.is_dir():
        raise InstallError("Project must be a directory")
    if kit == project or kit in project.parents or project in kit.parents:
        raise InstallError("Keep kit and target project in separate, non-nested directories")
    manifest, entries = load_kit(kit)
    agent_id = manifest["agent_id"]
    source_manifest_hash = digest(encode(manifest))
    backup_root = safe_path(project / BACKUPS)
    if backup_root.exists():
        if not backup_root.is_dir():
            raise InstallError("Backup location is not a directory")
        for child in backup_root.iterdir():
            child = safe_path(child)
            journal = child / "transaction.json"
            if child.is_dir() and journal.exists():
                transaction = read_json(journal)
                if not isinstance(transaction, dict):
                    raise InstallError("Invalid transaction journal")
                if transaction.get("status") not in ("committed", "rolled_back"):
                    raise InstallError("Interrupted transaction " + child.name + "; use recover before another install")
    ownership = safe_path(project / ".agents/agent-installs")
    if ownership.exists():
        if not ownership.is_dir():
            raise InstallError("Agent ownership location is not a directory")
        for path in ownership.iterdir():
            path = safe_path(path)
            if not path.is_file() or path.suffix != ".json" or not valid_name(path.stem):
                raise InstallError("Unexpected ownership record; review before installation")
            record = read_json(path)
            if not isinstance(record, dict):
                raise InstallError("Invalid installed ownership record")
            owned = validate_manifest(record.get("manifest"))
            if record.get("agent_id") != path.stem or record["manifest"]["agent_id"] != path.stem or record.get("manifest_sha256") != digest(encode(record["manifest"])):
                raise InstallError("Inconsistent installed ownership record")
            if path.stem != agent_id and set(owned) & set(entries):
                raise InstallError("Skill name is owned by another installed agent: " + ",".join(sorted(set(owned) & set(entries))))
    state_relative = state_path(agent_id)
    installed_state = safe_path(project / state_relative)
    old_state = read_json(installed_state) if installed_state.exists() else None
    if old_state is not None:
        if not isinstance(old_state, dict) or old_state.get("agent_id") != agent_id:
            raise InstallError("Invalid installed state")
        old_entries = validate_manifest(old_state.get("manifest"))
        if old_state.get("format_version") != 1 or old_state.get("kit_id") != "agent-package" or old_state.get("manifest_sha256") != digest(encode(old_state["manifest"])):
            raise InstallError("Installed sync-lock is inconsistent")
    else:
        old_entries = {}
    removed = set(old_entries) - set(entries)
    if removed and not allow_remove_owned:
        raise InstallError("Update removes owned skills; review migration then use --allow-remove-owned: " + ",".join(sorted(removed)))
    operations = []
    overlays = {}
    preserved_visuals = []
    observed_old_manifest = strict_json_loads(json.dumps(old_state["manifest"])) if old_state else None
    for name in sorted(set(entries) | removed):
        target = safe_path(project / ".agents/skills" / name)
        actual = fingerprint(target, "skill")
        previous_entry = old_entries.get(name)
        previous = ({"files": previous_entry["files"], "modes": previous_entry["modes"]} if previous_entry else None)
        wanted = ({"files": entries[name]["files"], "modes": entries[name]["modes"]} if name in entries else None)
        if actual is not None and previous is None:
            raise InstallError("Unmanaged skill conflict: " + str(target))
        if actual != previous and actual != wanted:
            baseline = old_state.get("visuals", {}).get(name) if old_state and isinstance(old_state.get("visuals", {}), dict) else None
            if previous is None or actual is None or not visual_drift_only(target, actual, previous, baseline):
                raise InstallError("Modified installed skill: " + name + "; semantic/code drift is not overwritten. For a legacy UI edit without a recorded visual baseline, reconcile its exact previous UI before updating; existing icons remain untouched")
            for before_entry in observed_old_manifest["skills"]:
                if before_entry["name"] == name:
                    before_entry.update(files=actual["files"], modes=actual["modes"])
        if previous is not None and actual is None:
            raise InstallError("Owned installed skill is missing: " + name)
        if previous is not None and actual is not None and name in entries:
            visual = visual_snapshot(target)
            if visual is not None:
                candidate_ui = kit / "skills" / name / "agents/openai.yaml"
                original_ui = read_bytes(candidate_ui) if candidate_ui.exists() else read_bytes(target / "agents/openai.yaml")
                incoming_fields, _ = visual_ui(original_ui)
                old_icons = set(visual["icons"])
                entry = entries[name]
                # New kit icons are not created for an already represented skill.
                for path in icon_paths(incoming_fields) - old_icons:
                    entry["files"].pop(path, None)
                    entry["modes"].pop(path, None)
                ui_bytes = original_ui if incoming_fields == visual["interface"] else overlay_ui(original_ui, visual["interface"])
                overlay = {"agents/openai.yaml": {"bytes": ui_bytes, "mode": file_mode(target / "agents/openai.yaml")}}
                for path in old_icons:
                    overlay[path] = {"bytes": read_bytes(target / path), "mode": file_mode(target / path)}
                if manifest.get("operating_standard") is not None:
                    previous_lock = target / "assets/visual-identity.lock.json"
                    if previous_lock.exists():
                        declared_old = read_json(previous_lock)
                        declared_new = read_json(kit / "skills" / name / "assets/visual-identity.lock.json")
                        if (isinstance(declared_old, dict) and declared_old.get("class") in ("project", "system")
                                and declared_old.get("class") != declared_new.get("class")):
                            raise InstallError("Visual class change requires an explicit actual scope migration; routine maintenance preserves the existing class and icons")
                    try:
                        validate_project_identity(target)
                        origin = read_json(target / "assets/visual-identity-origin.json")
                        identity_files = {path: read_bytes(target / path) for path in ("assets/visual-identity.lock.json", "assets/visual-identity-origin.json")}
                        if origin["kind"] == "preserved":
                            rel = origin["prior_snapshot"]["path"]
                            identity_files[rel] = read_bytes(target / rel)
                        elif read_json(target / "assets/visual-identity.lock.json")["class"] == "system":
                            rel = origin["style_reference"]["path"]
                            identity_files[rel] = read_bytes(target / rel)
                    except (InstallError, OSError, ValueError, KeyError):
                        previous_lock = target / "assets/visual-identity.lock.json"
                        declared = read_json(previous_lock) if previous_lock.exists() else read_json(kit / "skills" / name / "assets/visual-identity.lock.json")
                        kind = declared.get("class") if isinstance(declared, dict) else None
                        if kind not in ("project", "system"):
                            raise InstallError("Cannot infer existing visual class; reconcile its actual project/system scope without regenerating icons")
                        snapshot = {"schema": "visual-identity/1", "class": kind, "interface": visual["interface"],
                                    "files": {path: digest(overlay[path]["bytes"]) for path in sorted(old_icons)}, "regenerate_on_update": False}
                        prior_bytes = encode(snapshot)
                        origin = {"schema": "visual-identity-origin/1", "kind": "preserved",
                                  "prior_snapshot": {"path": "assets/visual-identity-preserved.json", "sha256": digest(prior_bytes)},
                                  "source_receipt": old_state["manifest_sha256"]}
                        if kind == "system":
                            old_origin_path = target / "assets/visual-identity-origin.json"
                            old_origin = read_json(old_origin_path) if old_origin_path.exists() else {}
                            incoming_origin = read_json(kit / "skills" / name / "assets/visual-identity-origin.json")
                            basis = next((item for item in (old_origin, incoming_origin) if isinstance(item, dict) and reusable_system_basis(item)), None)
                            if basis is None:
                                raise InstallError("Existing system identity requires its reusable_system source basis; classification does not grant global rights")
                            origin.update(scope="reusable_system", scope_basis=basis["scope_basis"])
                        identity_files = {"assets/visual-identity.lock.json": prior_bytes,
                                          "assets/visual-identity-preserved.json": prior_bytes,
                                          "assets/visual-identity-origin.json": encode(origin)}
                    for path, data in identity_files.items():
                        overlay[path] = {"bytes": data, "mode": file_mode(target / path) if (target / path).exists() else 0o644}
                for path, record in overlay.items():
                    entry["files"][path] = digest(record["bytes"])
                    entry["modes"][path] = record["mode"]
                overlays[name] = overlay
                preserved_visuals.append(name)
                wanted = {"files": entry["files"], "modes": entry["modes"]}
        if actual != wanted:
            operations.append({"path": ".agents/skills/" + name, "kind": "skill", "existed": actual is not None, "before": actual, "after": wanted})
    # Installed receipts describe effective bytes, including each project's
    # frozen visuals, while retaining the original delivery manifest identity.
    manifest_hash = digest(encode(manifest))
    visuals = {}
    for name, entry in entries.items():
        if "agents/openai.yaml" not in entry["files"]:
            continue
        ui_record = overlays.get(name, {}).get("agents/openai.yaml")
        ui_bytes = ui_record["bytes"] if ui_record else read_bytes(kit / "skills" / name / "agents/openai.yaml")
        fields, non_visual = visual_ui(ui_bytes)
        paths = icon_paths(fields)
        if paths:
            if not paths <= set(entry["files"]):
                raise InstallError("Visual icon references are missing from the effective package: " + name)
            visuals[name] = {"interface": fields, "non_visual_ui_sha256": digest(non_visual),
                             "icons": {path: {"sha256": entry["files"][path], "mode": entry["modes"][path]} for path in sorted(paths)}}
    agents_path = safe_path(project / "AGENTS.md")
    agents_before = read_bytes(agents_path) if agents_path.exists() else None
    agents_mode = file_mode(agents_path) if agents_before is not None else 0o644
    try:
        agents_text = agents_before.decode("utf-8") if agents_before is not None else ""
    except UnicodeError as error:
        raise InstallError("AGENTS.md must be UTF-8; no changes made") from error
    block = managed_block(manifest, manifest_hash)
    found = split_block(agents_text, agent_id)
    if found:
        if not old_state:
            raise InstallError("Unmanaged agent block exists; review before adoption")
        if digest(found[2].encode("utf-8")) != old_state.get("agents_block_sha256") and found[2] != block:
            raise InstallError("Managed agent block was modified")
        agents_after = (agents_text[:found[0]] + block + agents_text[found[1]:]).encode("utf-8")
    else:
        if old_state:
            raise InstallError("Managed agent block is missing; review before repair")
        separator = "" if not agents_text else ("\n" if agents_text.endswith("\n") else "\n\n")
        agents_after = (agents_text + separator + block + "\n").encode("utf-8")
    if agents_before != agents_after:
        operations.append({"path": "AGENTS.md", "kind": "file", "existed": agents_before is not None, "before": {"sha256": digest(agents_before), "mode": agents_mode} if agents_before is not None else None, "after": {"sha256": digest(agents_after), "mode": agents_mode}})
    state = {"format_version": 1, "kit_id": "agent-package", "agent_id": agent_id, "version": manifest["version"], "manifest_sha256": manifest_hash, "source_manifest_sha256": source_manifest_hash, "manifest": manifest, "visuals": visuals, "agents_block_sha256": digest(block.encode("utf-8"))}
    state_after = encode(state)
    state_before = read_bytes(installed_state) if installed_state.exists() else None
    state_mode = file_mode(installed_state) if state_before is not None else 0o600
    if state_before != state_after:
        operations.append({"path": state_relative.as_posix(), "kind": "file", "existed": state_before is not None, "before": {"sha256": digest(state_before), "mode": state_mode} if state_before is not None else None, "after": {"sha256": digest(state_after), "mode": state_mode}})
    warnings = ["Use one active source per agent; host discovery and execution are separate from file installation."]
    if manifest.get("operating_standard") is None:
        warnings.append("Legacy package has no declared operating standard; no upgraded-inheritance or behavior claim is made.")
    elif tuple(int(part) for part in manifest['operating_standard']['release'].split('.')) < (6, 6, 0):
        warnings.append('Historical operating standard retained. Its existing resource pins remain active. Managed model adoption requires a separate verified consumer.')
    if preserved_visuals:
        warnings.append("Existing project icons/colors preserved: " + ", ".join(preserved_visuals))
    warnings.extend("Known additional active source: " + source + "; nothing disabled." for source in other_sources)
    return {"project": project, "manifest": manifest, "entries": entries, "manifest_sha256": manifest_hash, "source_manifest_sha256": source_manifest_hash, "overlays": overlays, "preserved_visuals": preserved_visuals, "operations": operations, "agents_after": agents_after, "state_after": state_after, "old_manifest": observed_old_manifest, "warnings": warnings}

def fingerprint(path, kind):
    path = safe_path(path)
    if not path.exists():
        return None
    if kind == "skill":
        files = file_map(path)
        return {"files": files, "modes": mode_map(path, files)}
    return {"sha256": digest(read_bytes(path)), "mode": file_mode(path)}


def write_file(path, data, mode=0o600):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also prevents an existing link from being followed.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        # Set the exact requested ordinary mode independently of the caller's umask.
        os.fchmod(stream.fileno(), mode)
        os.fsync(stream.fileno())


def journal_write(path, value):
    path = safe_path(path)
    temporary = path.with_name(".transaction-" + uuid.uuid4().hex + ".json")
    write_file(temporary, encode(value))
    os.replace(temporary, path)


def remove_owned(path):
    path = safe_path(path)
    if path.is_dir():
        file_map(path)  # reject links/special files before recursive removal
        shutil.rmtree(path)
    elif path.exists():
        if not path.is_file():
            raise InstallError("Cannot remove a special file: " + str(path))
        path.unlink()


def rollback(project, backup, transaction):
    """Recover only known new/old objects; never overwrite an unrelated later edit."""
    operations = transaction["operations"]
    for operation in operations:
        target = project / operation["path"]
        previous = backup / "previous" / operation["path"]
        current = fingerprint(target, operation["kind"])
        saved = fingerprint(previous, operation["kind"])
        if saved is not None and saved != operation["before"]:
            raise InstallError("Backup was modified: " + str(previous))
        if current not in (None, operation["before"], operation["after"]):
            raise InstallError("Recovery would replace a later edit: " + str(target))
        if operation["existed"] and current is None and saved is None:
            raise InstallError("Original and backup are both missing: " + str(target))
        if operation["existed"] and current == operation["after"] and saved is None and operation["before"] != operation["after"]:
            raise InstallError("Original backup is missing: " + str(target))
    for operation in reversed(operations):
        target = safe_path(project / operation["path"])
        previous = safe_path(backup / "previous" / operation["path"])
        if previous.exists():
            if target.exists():
                remove_owned(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(previous, target)
        elif not operation["existed"] and target.exists():
            remove_owned(target)
    transaction["status"] = "rolled_back"
    journal_write(backup / "transaction.json", transaction)


def acquire(project):
    project = safe_path(project)
    project.mkdir(parents=True, exist_ok=True)
    safe_path(project / ".agents").mkdir(exist_ok=True)
    lock = safe_path(project / LOCK)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    except FileExistsError as error:
        raise InstallError("Installer lock exists; another install may be active. Verify no installer is running before removing " + str(lock)) from error
    with os.fdopen(fd, "w") as stream:
        stream.write(str(os.getpid()) + "\n")
    return lock


def apply_install(kit, project, other_sources=(), allow_remove_owned=False):
    # Read-only validation happens before creating directories or a lock.
    initial = plan_install(kit, project, other_sources, allow_remove_owned)
    if not initial["operations"]:
        return initial, None
    lock = acquire(initial["project"])
    backup = None
    transaction = None
    try:
        plan = plan_install(kit, initial["project"], other_sources, allow_remove_owned)
        if not plan["operations"]:
            return plan, None
        project = plan["project"]
        txid = uuid.uuid4().hex
        backup = safe_path(project / BACKUPS / txid)
        backup.mkdir(parents=True)
        staged = backup / "prepared"
        for operation in plan["operations"]:
            output = staged / operation["path"]
            if operation["after"] is None:
                continue
            if operation["kind"] == "skill":
                name = Path(operation["path"]).name
                for relative, expected in plan["entries"][name]["files"].items():
                    preserved = plan["overlays"].get(name, {}).get(relative)
                    data = preserved["bytes"] if preserved else read_bytes(kit / "skills" / name / relative)
                    if digest(data) != expected:
                        raise InstallError("Kit changed during staging: " + name + "/" + relative)
                    mode = plan["entries"][name]["modes"][relative]
                    observed_mode = preserved["mode"] if preserved else file_mode(kit / "skills" / name / relative)
                    if observed_mode != mode:
                        raise InstallError("Kit permissions changed during staging: " + name + "/" + relative)
                    write_file(output / relative, data, mode)
            else:
                write_file(output, plan["agents_after"] if operation["path"] == "AGENTS.md" else plan["state_after"],
                           operation["after"]["mode"])
            if fingerprint(output, operation["kind"]) != operation["after"]:
                raise InstallError("Prepared copy did not verify: " + operation["path"])
        transaction = {"format_version": 1, "project": str(project), "status": "prepared",
                       "manifest_sha256": plan["manifest_sha256"], "agent_id": plan["manifest"]["agent_id"], "old_manifest": plan.get("old_manifest"), "manifest": plan["manifest"], "operations": plan["operations"]}
        journal_write(backup / "transaction.json", transaction)
        # Phase two: all bytes have verified; move originals to backup and promote staged copies.
        for operation in plan["operations"]:
            target = safe_path(project / operation["path"])
            if fingerprint(target, operation["kind"]) != operation["before"]:
                raise InstallError("Target changed during installation: " + operation["path"])
            previous = safe_path(backup / "previous" / operation["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            if operation["existed"]:
                previous.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, previous)
            if operation["after"] is not None:
                os.replace(staged / operation["path"], target)
        transaction["status"] = "committed"
        journal_write(backup / "transaction.json", transaction)
        return plan, backup
    except BaseException as error:
        if backup is not None and transaction is not None:
            try:
                rollback(initial["project"], backup, transaction)
            except BaseException as rollback_error:
                raise InstallError("Install interrupted; recovery requires review at " + str(backup) + ": " + str(rollback_error)) from error
        elif backup is not None:
            # No live object was changed before the prepared journal existed.
            remove_owned(backup)
        raise
    finally:
        lock.unlink()


def recover(project, txid):
    if not re.fullmatch(r"[0-9a-f]{32}", txid or ""):
        raise InstallError("Recovery requires a transaction ID from the installer")
    project = safe_path(project)
    backup = safe_path(project / BACKUPS / txid)
    transaction = read_json(backup / "transaction.json")
    if not isinstance(transaction, dict) or transaction.get("format_version") != 1 or transaction.get("project") != str(project):
        raise InstallError("Recovery journal belongs to a different project")
    if transaction.get("status") in ("committed", "rolled_back"):
        raise InstallError("Transaction is already complete")
    entries = validate_manifest(transaction.get("manifest"))
    agent_id = transaction.get("agent_id")
    if agent_id != transaction["manifest"]["agent_id"]:
        raise InstallError("Recovery agent identity differs")
    old_manifest = transaction.get("old_manifest")
    old_entries = validate_manifest(old_manifest) if old_manifest else {}
    if old_manifest and old_manifest["agent_id"] != agent_id:
        raise InstallError("Recovery previous agent identity differs")
    allowed = {".agents/skills/" + name for name in set(entries) | set(old_entries)} | {"AGENTS.md", state_path(agent_id).as_posix()}
    operations = transaction.get("operations")
    if not isinstance(operations, list) or len(operations) > len(allowed):
        raise InstallError("Invalid recovery operations")
    seen = set()
    for item in operations:
        if not isinstance(item, dict) or item.get("path") not in allowed or item["path"] in seen:
            raise InstallError("Unsafe recovery operation")
        seen.add(item["path"])
        expected_kind = "skill" if item["path"].startswith(".agents/skills/") else "file"
        if item.get("kind") != expected_kind or not isinstance(item.get("existed"), bool):
            raise InstallError("Invalid recovery operation kind")
        for key in ("before", "after"):
            value = item.get(key)
            if key == "before" and not item["existed"] and value is None:
                continue
            if key == "after" and expected_kind == "skill" and value is None and item["existed"]:
                name = Path(item["path"]).name
                if name not in old_entries or name in entries:
                    raise InstallError("Recovery removal is not an owned obsolete skill")
                continue
            if expected_kind == "skill":
                if not isinstance(value, dict):
                    raise InstallError("Invalid recovery skill snapshot")
                validate_files(value.get("files")); validate_modes(value.get("modes"), value["files"])
                name = Path(item["path"]).name
                owner = old_entries if key == "before" else entries
                declared = owner.get(name)
                if declared is None or value != {"files": declared["files"], "modes": declared["modes"]}:
                    raise InstallError("Recovery skill snapshot differs from its declared ownership")
            elif not isinstance(value, dict) or not HEX.fullmatch(value.get("sha256", "")) or type(value.get("mode")) is not int or not 0 <= value["mode"] <= 0o777:
                raise InstallError("Invalid recovery hash")
    lock = acquire(project)
    try:
        rollback(project, backup, transaction)
    finally:
        lock.unlink()
    return {"ok": True, "mode": "recover", "transaction": txid, "status": "rolled_back"}

def summary(plan, mode, backup=None):
    return {"ok": True, "mode": mode, "project": str(plan["project"]), "version": plan["manifest"]["version"],
            "manifest_sha256": plan["manifest_sha256"], "source_manifest_sha256": plan["source_manifest_sha256"], "agent_id": plan["manifest"]["agent_id"], "skills": len(plan["entries"]),
            "operating_standard": plan["manifest"].get("operating_standard", {}).get("release", "legacy_not_declared"), "preserved_visuals": plan["preserved_visuals"],
            "changes": [op["path"] for op in plan["operations"]], "idempotent": not plan["operations"],
            "backup": str(backup) if backup else None, "warnings": plan["warnings"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True, help="Root containing manifest.json and declared skills/")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--mode", choices=("preflight", "dry-run", "apply", "verify", "recover"), default="preflight")
    parser.add_argument("--other-active-source", action="append", default=[])
    parser.add_argument("--transaction")
    parser.add_argument("--allow-remove-owned", action="store_true", help="Apply a reviewed migration removing unchanged obsolete skills owned by this agent")
    args = parser.parse_args(argv)
    try:
        kit = safe_path(args.kit)
        if args.mode == "recover":
            result = recover(args.project, args.transaction)
        elif args.mode == "apply":
            plan, backup = apply_install(kit, args.project, args.other_active_source, args.allow_remove_owned)
            result = summary(plan, args.mode, backup)
        else:
            plan = plan_install(kit, args.project, args.other_active_source, args.allow_remove_owned)
            if args.mode == "verify" and plan["operations"]:
                raise InstallError("Installed files do not match this kit; review preflight/dry-run before apply")
            result = summary(plan, args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (InstallError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
