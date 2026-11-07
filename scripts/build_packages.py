#!/usr/bin/env python3
"""Build deterministic Work and Codex source bundles after repository validation.

These archives contain sources, not an installed plugin or a live executor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path

from check_repository import check

EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}
COMMON = ["AGENTS.md", "README.md", "START_HERE.md", "CHANGELOG.md", "RIGHTS.md", "locales.json", "maintenance-skill",
          "docs", "templates", "governance", "releases", "scripts", "marketing", "assets"]


def collect(root: Path, relative_roots: list[str]) -> list[Path]:
    files = set()
    for relative in relative_roots:
        p = root / relative
        if not p.exists():
            continue
        for candidate in ([p] if p.is_file() else p.rglob("*")):
            rel = candidate.relative_to(root)
            if candidate.is_symlink():
                raise ValueError(f"refusing symlink in package: {rel}")
            if not candidate.is_file() or EXCLUDED_PARTS.intersection(rel.parts) or candidate.suffix == ".pyc":
                continue
            if any(part.startswith(".env") for part in rel.parts):
                raise ValueError(f"refusing possible secret file: {rel}")
            files.add(candidate)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def write_zip(root: Path, output: Path, files: list[Path], mode: str, version: str):
    baseline_count = len(json.loads((root / "kit/manifest.json").read_text(encoding="utf-8"))["skills"])
    descriptor = {"schema": "codex-agents.package/1", "mode": mode,
                  "suite_version": version, "installation_performed": False,
                  "entry_point": "START_HERE.md", "skill_sources": "kit/skills",
                  "manifest": "kit/manifest.json", "baseline_skill_count": baseline_count,
                  "optional_maintenance_skill": "maintenance-skill",
                  "installation_workflow": ("supported Work personal-skill manager; one save per skill; verify registry and actual invocation"
                                            if mode == "WORK" else "portable updater audit -> apply -> verify with actual journal; verify host discovery separately")}
    package_readme = (f"# Agent System {version} — {mode} source bundle\n\n"
                      "Choose your language in START_HERE.md, then read that complete guide.\n\n"
                      "This archive contains the same verified reusable sources and continuity records as the other mode's bundle. "
                      "PACKAGE.json and this introduction identify the intended installation workflow; extracting an archive does not install a skill.\n\n")
    if mode == "WORK":
        package_readme += ("In ChatGPT Work, connect the GitHub repository or provide these extracted sources. Ask the supported personal-skill manager "
                           f"to inspect and install/update the {baseline_count} baseline skills from kit/skills. It must save each personal skill through the supported "
                           "management workflow and verify the registered sources. A repository connection, a read SKILL.md or a copied archive alone "
                           "is not installation. Work's host avatar may differ from portable Codex icons.\n\n")
    else:
        package_readme += ("In Codex, inspect kit/manifest.json and kit/BUILD_VERIFICATION.json, then use kit/portable/update_skill_suite.py "
                           "with audit, apply and verify according to the guide. Keep plans/backups outside skill discovery roots and pass the actual "
                           "apply journal to verify. Preserve existing icons and local modifications; check runtime discovery separately.\n\n")
    package_readme += (f"maintenance-skill/ is an optional repository-maintenance instruction skill, separate from the {baseline_count} baseline skills. "
                       "Install it through the supported manager only when requested; including its sources in this archive does not activate it. "
                       f"Existing projects still need compatibility intake and preserved-context adoption. See releases/migrations/{version}.md.\n")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        entries = [(p.relative_to(root).as_posix(), p.read_bytes(), 0o755 if p.stat().st_mode & stat.S_IXUSR else 0o644) for p in files]
        entries.append(("PACKAGE.json", (json.dumps(descriptor, indent=2, sort_keys=True) + "\n").encode(), 0o644))
        entries.append(("PACKAGE_README.md", package_readme.encode(), 0o644))
        for relative, data, mode_bits in sorted(entries):
            info = zipfile.ZipInfo(relative, date_time=(2026, 11, 7, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode_bits) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(root: Path, output: Path) -> dict:
    result = check(root)
    if not result["ok"]:
        raise ValueError("repository validation failed:\n" + "\n".join(result["errors"]))
    output.mkdir(parents=True, exist_ok=True)
    # Exact curated kit only; never include a parent release backup or project export.
    files = collect(root, ["kit", *COMMON])
    result_files = []
    for mode in ("WORK", "CODEX"):
        path = output / f"Agent_System_{result['suite_version']}_{mode}.zip"
        write_zip(root, path, files, mode, result["suite_version"])
        result_files.append({"name": path.name, "size": path.stat().st_size,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    sums = "".join(f"{item['sha256']}  {item['name']}\n" for item in result_files)
    (output / "SHA256SUMS").write_text(sums, encoding="utf-8")
    receipt = {"schema": "codex-agents.build/1", "suite_version": result["suite_version"],
               "repository_version": result["repository_version"], "source_files": len(files),
               "files": result_files, "host_installation_verified": False}
    (output / "BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="defaults to ROOT/dist; keep outside skill discovery roots")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        print(json.dumps(build(root, args.output.resolve() if args.output else root / "dist"), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
