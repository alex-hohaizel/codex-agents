#!/usr/bin/env python3
"""Verify portable operating resources in newly generated agents, without execution.

This is a byte/link check, not semantic coverage review, host discovery, consent
authentication or a proof that the generated agent behaves correctly.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import types
import xml.etree.ElementTree as ET

SCHEMA = "agent-operating-standard/1"
RELEASE = "5.0.0"
RESOURCES = (
    "references/adaptive-work.md",
    "references/research-and-synthesis.md",
    "references/visual-identity.md",
    "references/joint-work-codex.md",
    "scripts/adaptive_work.py",
    "scripts/visual_identity.py",
    "assets/adaptive-task.schema.json",
    "assets/adaptive-task.example.json",
)
ENTRY_LINKS = tuple(p for p in RESOURCES if p.startswith("references/"))
VISUAL_LOCK = "assets/visual-identity.lock.json"
VISUAL_ORIGIN = "assets/visual-identity-origin.json"
LIMIT = 4 * 1024 * 1024


def read_regular(path):
    path = Path(os.path.abspath(path))
    for part in reversed((path,) + tuple(path.parents)):
        if part.is_symlink():
            raise ValueError("Operating resource must not traverse a symlink: " + str(path))
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
            raise ValueError("Operating resource must be a bounded regular file: " + str(path))
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise ValueError("Operating resource exceeds limit: " + str(path))
        return data
    finally:
        os.close(fd)


def expected_resources(source_root):
    return {name: hashlib.sha256(read_regular(Path(source_root) / name)).hexdigest() for name in RESOURCES}


def entry_errors(content, label="SKILL.md"):
    errors = []
    for resource in ENTRY_LINKS:
        if not re.search(r"\]\((?:\./)?" + re.escape(resource) + r"\)", content):
            errors.append(label + " lacks a local operating-resource link: " + resource)
    return errors


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


def bound_asset(root, binding, label):
    if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(binding.get("sha256", ""))):
        raise ValueError(label + " requires a bound actual asset")
    rel = Path(binding["path"])
    if rel.is_absolute() or ".." in rel.parts or "\\" in binding["path"] or ":" in binding["path"] or rel.as_posix() != binding["path"] or not rel.parts or rel.parts[0] != "assets":
        raise ValueError(label + " must have a portable bundled assets path")
    data = read_regular(Path(root) / rel)
    if hashlib.sha256(data).hexdigest() != binding["sha256"]:
        raise ValueError(label + " differs from its bound source")
    return rel.as_posix(), data


def reusable_system_basis(origin):
    basis = origin.get("scope_basis")
    return (origin.get("scope") == "reusable_system" and isinstance(basis, dict)
            and all(isinstance(basis.get(key), str) and basis[key].strip() for key in ("source", "reason")))


def visual_errors(root, source_root):
    path = Path(source_root) / "scripts/visual_identity.py"
    module = types.ModuleType("trusted_visual_identity")
    module.__file__ = str(path)
    exec(compile(read_regular(path), str(path), "exec"), module.__dict__)
    lock = json.loads(read_regular(Path(root) / VISUAL_LOCK))
    kind = lock.get("class") if isinstance(lock, dict) else None
    if kind not in ("project", "system"):
        return ["Visual class must be project or system, chosen from the accepted task's purpose"]
    current = module.freeze(module.safe_root(root), kind)
    if lock != current or not current.get("files"):
        return ["Visual lock must equal actual declared-class icon paths/bytes/colors"]
    origin = json.loads(read_regular(Path(root) / VISUAL_ORIGIN))
    if not isinstance(origin, dict) or origin.get("schema") != "visual-identity-origin/1":
        return ["Generated icon requires explicit created/preserved provenance"]
    if kind == "system" and not reusable_system_basis(origin):
        return ["System class requires reusable_system scope and scope_basis source/reason; a label grants no global permissions"]
    if origin.get("kind") == "created":
        if kind == "project" and any(not name.endswith(".svg") or not project_style(read_regular(Path(root) / name)) for name in current["files"]):
            return ["A newly created project icon must use project-card-v1, distinct from system icons"]
        if kind == "system":
            reference, sample = bound_asset(root, origin.get("style_reference"), "Reusable system style reference")
            if reference in current["files"] or Path(reference).suffix.lower() not in module.SUFFIXES:
                return ["New system icon requires a separate actual existing system-style image sample"]
            if project_style(sample) or b"agent-style:project-card-v1" in sample or any(project_style(read_regular(Path(root) / name)) or b"agent-style:project-card-v1" in read_regular(Path(root) / name) for name in current["files"]):
                return ["Project-card imagery cannot be declared a newly created reusable system icon/style"]
    elif origin.get("kind") == "preserved":
        binding = origin.get("prior_snapshot")
        if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(binding.get("sha256", ""))):
            return ["Preserved icon requires a bound actual prior snapshot"]
        rel = Path(binding["path"])
        if rel.is_absolute() or ".." in rel.parts or "\\" in binding["path"] or rel.as_posix() != binding["path"] or not rel.parts or rel.parts[0] != "assets":
            return ["Prior visual snapshot must have a portable bundled assets path"]
        prior = read_regular(Path(root) / rel)
        if hashlib.sha256(prior).hexdigest() != binding["sha256"] or json.loads(prior) != current:
            return ["Preserved icon differs from its bound prior snapshot"]
    else:
        return ["Visual origin kind must be created or preserved"]
    return []


def verify_child(root, expected, entry="SKILL.md", source_root=None):
    errors = []
    try:
        content = read_regular(Path(root) / entry).decode("utf-8")
        errors.extend(entry_errors(content, entry))
        for resource, wanted in expected.items():
            try:
                actual = hashlib.sha256(read_regular(Path(root) / resource)).hexdigest()
                if actual != wanted:
                    errors.append(resource + " differs from the constructor's operating standard")
            except (OSError, ValueError) as error:
                errors.append(resource + ": " + str(error))
        errors.extend(visual_errors(root, source_root or Path(__file__).resolve().parents[1]))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append(str(error))
    return errors


def inspect_children(roots, source_root=None, entry="SKILL.md"):
    source_root = Path(source_root or Path(__file__).resolve().parents[1])
    expected = expected_resources(source_root)
    errors = []
    for root in roots:
        errors.extend(str(root) + ": " + error for error in verify_child(root, expected, entry, source_root))
    return {"schema": SCHEMA, "release": RELEASE, "resources": expected}, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("child_roots", type=Path, nargs="+")
    parser.add_argument("--entry", choices=("SKILL.md", "AGENTS.md"), default="SKILL.md")
    args = parser.parse_args(argv)
    try:
        contract, errors = inspect_children(args.child_roots, entry=args.entry)
        result = {"valid": not errors, "operating_standard": contract, "children_checked": len(args.child_roots), "errors": errors,
                  "quality_certified": False, "behavior_verified": False, "human_authority_authenticated": False}
    except (OSError, ValueError) as error:
        result = {"valid": False, "errors": [str(error)], "quality_certified": False, "behavior_verified": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
