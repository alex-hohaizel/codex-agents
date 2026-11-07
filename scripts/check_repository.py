#!/usr/bin/env python3
"""Check distributable skill sources, release completeness and translation freshness.

This is a repository check. It does not install skills or prove host discovery.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root: Path, value: str) -> Path:
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or "\\" in value:
        raise ValueError(f"unsafe relative path: {value}")
    result = root.joinpath(*p.parts)
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {value}")
    return result


def check(root: Path, *, links: bool = True) -> dict:
    errors, warnings = [], []

    def load(relative):
        try:
            return json.loads(safe_path(root, relative).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            return {}

    current = load("releases/current.json")
    manifest = load("kit/manifest.json")
    suite_version = current.get("suite_version")
    skills = manifest.get("skills", [])
    expected = current.get("stable_skill_names", [])
    names = [s.get("name") for s in skills]
    if not expected or len(expected) != len(set(expected)):
        errors.append("release must record unique stable_skill_names")
    if sorted(names) != sorted(expected):
        errors.append("kit skill names differ from release inventory")
    if len(names) != len(set(names)):
        errors.append("duplicate stable skill name")
    if manifest.get("suite_id") != f"agent-system-{suite_version}":
        errors.append("manifest suite_id differs from release suite_version")
    if current.get("source_manifest_sha256") and (root / "kit/manifest.json").is_file():
        if current["source_manifest_sha256"] != digest(root / "kit/manifest.json"):
            errors.append("release record is stale for the current source manifest")
    verified_files = 0
    for skill in skills:
        name = skill.get("name", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append(f"invalid stable skill name: {name!r}")
            continue
        if skill.get("version") != suite_version:
            errors.append(f"{name}: skill version differs from suite version")
        skill_root = root / "kit" / "skills" / name
        recorded = set(skill.get("files", {}))
        actual = {p.relative_to(skill_root).as_posix() for p in skill_root.rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
        if actual != recorded:
            errors.append(f"{name}: untracked/missing files: {sorted(actual ^ recorded)[:8]}")
        for relative, info in skill.get("files", {}).items():
            try:
                p = safe_path(skill_root, relative)
                if not p.is_file():
                    raise ValueError("missing file")
                if digest(p) != info.get("sha256"):
                    raise ValueError("SHA-256 mismatch")
                if p.stat().st_size != info.get("size"):
                    raise ValueError("size mismatch")
                verified_files += 1
            except (OSError, ValueError) as exc:
                errors.append(f"{name}/{relative}: {exc}")
        if "SKILL.md" not in recorded or "agents/openai.yaml" not in recorded:
            errors.append(f"{name}: missing skill or interface metadata")

    # Complete coverage also prevents adding an unrecorded project-specific agent.
    skill_dirs = {p.name for p in (root / "kit" / "skills").iterdir() if p.is_dir()} if (root / "kit" / "skills").exists() else set()
    if skill_dirs != set(names):
        errors.append("kit/skills directories differ from canonical manifest")
    baseline_path = root / "governance/ICON_BASELINE.json"
    if baseline_path.is_file():
        baseline = load("governance/ICON_BASELINE.json")
        for name, identity in baseline.get("skills", {}).items():
            skill_root = root / "kit/skills" / name
            for relative, expected_hash in identity.get("files", {}).items():
                try:
                    p = safe_path(skill_root, relative)
                    if not p.is_file() or digest(p) != expected_hash:
                        errors.append(f"{name}: existing icon changed: {relative}")
                except (OSError, ValueError) as exc:
                    errors.append(f"{name}: icon baseline {exc}")
            ui = skill_root / "agents/openai.yaml"
            if ui.is_file():
                fields = {m[0]: m[1].strip().strip('\"\'') for m in re.findall(
                    r"^\s*(icon_small|icon_large|brand_color):\s*(.*?)\s*$", ui.read_text(encoding="utf-8"), re.M)}
                if fields != identity.get("interface", {}):
                    errors.append(f"{name}: existing icon references or brand colour changed")
    for forbidden in ["PROJECT_AGENT_SOURCE", "compatibility", "evidence", "SOURCE_BINDINGS.json"]:
        if (root / "kit" / forbidden).exists():
            errors.append(f"kit includes excluded private/history source: {forbidden}")
    integrity_path = root / "kit" / "BUILD_VERIFICATION.json"
    if integrity_path.exists():
        integrity = load("kit/BUILD_VERIFICATION.json")
        if integrity.get("manifest_sha256") != digest(root / "kit" / "manifest.json"):
            errors.append("kit integrity manifest hash mismatch")
        for relative, info in integrity.get("files", {}).items():
            try:
                p = safe_path(root / "kit", relative)
                if not p.is_file() or digest(p) != info.get("sha256") or p.stat().st_size != info.get("size"):
                    errors.append(f"kit integrity mismatch: {relative}")
            except (OSError, ValueError) as exc:
                errors.append(f"kit integrity {relative}: {exc}")

    for field in ["release_notes", "migration", "requirements"]:
        relative = current.get(field)
        if not relative:
            errors.append(f"release lacks {field}")
            continue
        try:
            p = safe_path(root, relative)
            if not p.is_file() or p.stat().st_size < 100:
                errors.append(f"{field}: missing or empty {relative}")
        except ValueError as exc:
            errors.append(str(exc))
    migration = root / current.get("migration", "__missing__")
    if migration.is_file():
        text = migration.read_text(encoding="utf-8")
        for marker in ["## Before", "## Steps", "## Verify", "## Rollback", "## Existing projects"]:
            if marker not in text:
                errors.append(f"migration lacks {marker}")

    requirements = root / current.get("requirements", "__missing__")
    if requirements.is_file():
        try:
            with requirements.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            if not rows:
                errors.append("empty requirements register")
            for row in rows:
                if not row.get("id") or not row.get("requirement") or not row.get("acceptance"):
                    errors.append("requirement lacks identity/content/acceptance")
                if row.get("status") not in {"implemented", "awaiting-owner-selection", "documented-boundary"}:
                    errors.append(f"{row.get('id')}: unknown requirement status")
                for target in row.get("evidence", "").split(";"):
                    if target and not safe_path(root, target).exists():
                        errors.append(f"{row.get('id')}: evidence target missing: {target}")
        except (OSError, ValueError) as exc:
            errors.append(f"requirements: {exc}")

    translations = load("docs/translations.json")
    source_relative = translations.get("source", "docs/en/GUIDE.md")
    source = root / source_relative
    source_hash = digest(source) if source.is_file() else None
    if source_hash is None or translations.get("source_sha256") != source_hash:
        errors.append("translation manifest English source hash is missing/stale")
    translated_locales = set()
    for entry in translations.get("translations", []):
        locale = entry.get("locale")
        translated_locales.add(locale)
        try:
            p = safe_path(root, entry.get("path", "__missing__"))
            if not p.is_file() or p.stat().st_size < 100:
                errors.append(f"{locale}: translation missing/empty")
            if entry.get("status") != "complete":
                errors.append(f"{locale}: translation is not complete")
            if entry.get("source_sha256") != source_hash:
                errors.append(f"{locale}: translation based on stale English guide")
            if entry.get("sha256") and p.is_file() and entry["sha256"] != digest(p):
                errors.append(f"{locale}: translated file changed without manifest refresh")
        except ValueError as exc:
            errors.append(f"{locale}: {exc}")
    if not {"uk", "de", "it"}.issubset(translated_locales):
        errors.append("required Ukrainian/German/Italian translations are missing")
    # Locale entry point coverage; allows either a mapping or an array registry.
    locales_path = root / "locales.json"
    if locales_path.is_file():
        locales = load("locales.json").get("locales", [])
        for item in (locales.values() if isinstance(locales, dict) else locales):
            if isinstance(item, dict):
                locale = item.get("code") or item.get("locale") or item.get("id")
                if locale and locale != "en" and locale not in translated_locales:
                    errors.append(f"advertised locale lacks complete guide: {locale}")

    # Markdown links outside immutable canonical skill sources are maintainable here.
    if links:
        for p in root.rglob("*.md"):
            rel = p.relative_to(root)
            if rel.parts[0] in {"kit", "dist", ".git"}:
                continue
            text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.S)
            for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
                target = target.strip("<>")
                if urlparse(target).scheme or target.startswith(("#", "//")):
                    continue
                target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if target and not (p.parent / target).exists():
                    errors.append(f"{rel}: broken local link: {target}")
    return {"ok": not errors, "suite_version": suite_version,
            "repository_version": current.get("repository_version"),
            "skills": len(skills), "verified_skill_files": verified_files,
            "translations": len(translated_locales), "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-links", action="store_true", help="diagnostic only; CI checks local links")
    args = parser.parse_args()
    result = check(args.root.resolve(), links=not args.skip_links)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
