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
import subprocess
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


def version_from_skill(path: Path) -> str | None:
    boundary = re.match(r"^---\n([\s\S]*?)\n---(?:\n|$)", path.read_text(encoding="utf-8"))
    header = boundary.group(1) + "\n" if boundary else ""
    metadata = re.findall(r'^metadata:[ \t]*\n((?:[ \t][^\n]+\n)*)', header, re.M)
    markers = re.findall(r'^  version: "([^"]+)"[ \t]*$', metadata[0], re.M) if len(metadata) == 1 else []
    return markers[0] if len(markers) == 1 else None


def check(root: Path, *, links: bool = True) -> dict:
    errors, warnings = [], []

    def load(relative):
        try:
            return json.loads(safe_path(root, relative).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            return {}

    current = load("releases/current.json")
    repository_version = str(current.get("repository_version", ""))
    managed_stage = re.match(r"^(\d+)\.(\d+)\.(\d+)",repository_version)
    model = current.get("managed_model")
    managed_release = bool(managed_stage and tuple(map(int, managed_stage.groups())) >= (1, 9, 0))
    if managed_release:
        from managed_release_checks import audit_checkout_models, managed_model_policy
        if not managed_model_policy(model):
            errors.append("managed release requires an explicit hosted Sol model and ultra effort in releases/current.json")
        inheritance_checker = "check_generated_inheritance.py"
        try:
            factory_checker = digest(safe_path(root, f"kit/skills/agent-foundry/scripts/{inheritance_checker}"))
            for relative in (f"kit/portable/{inheritance_checker}",
                             f"kit/skills/design-specialist-skills/scripts/{inheritance_checker}"):
                if digest(safe_path(root, relative)) != factory_checker:
                    errors.append(f"{relative}: generated inheritance checker differs from the factory source")
        except (OSError, ValueError) as exc:
            errors.append(f"generated inheritance checker: {exc}")
        if current.get("commercial",{}).get("installer_payments_enabled") is not False:
            errors.append("managed release installer payments must be disabled")
        try:
            errors.extend(audit_checkout_models(root))
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as exc:
            errors.append("managed legacy-model audit: " + str(exc))
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

    release_paths = ["release_notes", "installation_guide", "requirements"]
    for field in release_paths:
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
    branch = current.get("repository_branch")
    if branch is not None and (
        not isinstance(branch, str) or not branch or any(char.isspace() for char in branch)
    ):
        errors.append("release repository_branch must name the active GitHub branch")

    release_stage = current.get("release_stage")
    if release_stage is not None:
        if release_stage not in ("candidate", "stable"):
            errors.append("release_stage must be candidate or stable")
        versions = [(f"kit/skills/{name}/SKILL.md", suite_version) for name in expected]
        versions.extend((f"{item.get('source')}/SKILL.md", item.get("version"))
                        for item in current.get("optional_skills", []))
        for target, version in versions:
            try:
                if not version or version_from_skill(safe_path(root, target)) != version:
                    errors.append(f"{target}: metadata.version differs from the current component record")
            except (OSError, ValueError) as exc:
                errors.append(f"{target}: {exc}")
        role_record = current.get("role_profiles", {})
        roles = load(role_record.get("manifest", "agent-profiles/manifest.json"))
        if roles.get("release") != role_record.get("version") or len(roles.get("roles", [])) != 12:
            errors.append("role profile inventory or version differs from the current component record")
        else:
            for role in roles["roles"]:
                relative = f"agent-profiles/{role.get('file')}"
                try:
                    role_path = safe_path(root, relative)
                    if digest(role_path) != role.get("sha256"):
                        errors.append(f"{relative}: role hash differs from its manifest")
                    if managed_release and managed_model_policy(model):
                        from install_host_profile import role_parts
                        with role_path.open(encoding="utf-8", newline="") as stream:
                            parts = role_parts(stream.read())
                        selectors = {key: value[3] for key, value in parts[1].items()} if parts else {}
                        if selectors != {"model": model["id"], "model_reasoning_effort": model["reasoning_effort"]}:
                            errors.append(f"{relative}: role model and effort differ from managed release policy")
                except (OSError, ValueError) as exc:
                    errors.append(f"{relative}: {exc}")
        profile = current.get("host_profile", {})
        try:
            relative = profile.get("source", "host-profiles/codex/AGENTS.md")
            raw = safe_path(root, relative).read_text(encoding="utf-8")
            marker = re.search(r"^# Agent System production profile (\S+)$", raw, re.M)
            if not marker or marker.group(1) != profile.get("version"):
                errors.append("host profile version differs from the current component record")
        except (OSError, ValueError) as exc:
            errors.append(f"host profile release record: {exc}")

    service = current.get("local_service")
    if service:
        try:
            source = service.get("source")
            version = service.get("version")
            if not isinstance(source, str) or not source or not isinstance(version, str) or not version:
                raise ValueError("local service source and version are required")
            package = load(f"{source}/package.json")
            lock = load(f"{source}/package-lock.json")
            contracts = safe_path(root, f"{source}/shared/contracts.mjs").read_text(encoding="utf-8")
            runtime = re.search(r'^export const SERVICE_VERSION = "([^"]+)";$', contracts, re.M)
            versions = {
                "package.json": package.get("version"),
                "package-lock.json": lock.get("version"),
                "package-lock.json root package": lock.get("packages", {}).get("", {}).get("version"),
                "shared/contracts.mjs": runtime.group(1) if runtime else None,
            }
            requirements_file = safe_path(root, f"{source}/requirements.json")
            if requirements_file.is_file():
                versions["requirements.json version"] = load(
                    f"{source}/requirements.json"
                ).get("version")
            for origin, actual in versions.items():
                if actual != version:
                    errors.append(f"local service {origin} version {actual!r} differs from release {version}")
        except (OSError, ValueError) as exc:
            errors.append(f"local service release record: {exc}")

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
                if row.get("status") not in {"implemented", "in-progress", "awaiting-owner-selection", "documented-boundary"}:
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
            if rel.parts[0] in {"kit", "dist", ".git"} or any(
                    part in {"node_modules", ".atelier-local", "test-results", "playwright-report"}
                    for part in rel.parts):
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
            "repository_branch": branch, "release_stage": release_stage,
            "requirements": current.get("requirements"),
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
