#!/usr/bin/env python3
"""Build deterministic Work and Codex source bundles after repository validation.

These archives contain sources, not an installed plugin or a live executor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

from check_repository import check

EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".DS_Store", "node_modules",
                  "dist", ".atelier-local", "test-results", "playwright-report"}
COMMON = ["AGENTS.md", "README.md", "START_HERE.md", "CHANGELOG.md", "RIGHTS.md", "locales.json", "maintenance-skill",
          "START_HERE.html", "ПОЧАТИ.html", "Start.command", "Start.sh", "Start.cmd",
          "Start-Workbench.command", "Start-Workbench.sh", "Start-Workbench.cmd",
          "docs", "templates", "governance", "releases", "scripts", "marketing", "assets",
          "commercial", "standards", "host-profiles", "agent-profiles", "optional-skills", "evaluations", "apps"]


def tracked_sources(root: Path) -> set[str] | None:
    """Use the index only for this checkout; exported source trees still work.

    Ignored files may contain buyer or developer data even in a clean checkout.
    A parent repository must not silently turn a nested source export into a
    checkout, and invalid checkout metadata must fail rather than widen inputs.
    """
    root = root.resolve()
    metadata = root / ".git"
    if not metadata.exists() and not metadata.is_symlink():
        return None
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}}
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=root,
                                      env=env, stderr=subprocess.PIPE)
        if Path(os.fsdecode(top).strip()).resolve() != root:
            raise ValueError("package source must be the exact Git checkout root")
        entries = subprocess.check_output(["git", "ls-files", "--cached", "-z"], cwd=root,
                                          env=env, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ValueError("cannot establish tracked package sources for this Git checkout") from exc
    return {os.fsdecode(relative) for relative in entries.split(b"\0") if relative}


def collect(root: Path, relative_roots: list[str]) -> list[Path]:
    tracked = tracked_sources(root)
    files = set()
    for relative in relative_roots:
        p = root / relative
        if EXCLUDED_PARTS.intersection(p.relative_to(root).parts):
            continue
        if p.is_symlink():
            raise ValueError(f"refusing symlink in package: {relative}")
        if not p.exists():
            continue
        for candidate in ([p] if p.is_file() else p.rglob("*")):
            rel = candidate.relative_to(root)
            if EXCLUDED_PARTS.intersection(rel.parts):
                continue
            if tracked is not None and rel.as_posix() not in tracked:
                continue
            if candidate.is_symlink():
                raise ValueError(f"refusing symlink in package: {rel}")
            if not candidate.is_file() or candidate.suffix == ".pyc":
                continue
            if any(part.startswith(".env") for part in rel.parts):
                raise ValueError(f"refusing possible secret file: {rel}")
            files.add(candidate)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def write_zip(root: Path, output: Path, files: list[Path], mode: str, release: dict):
    version = release["suite_version"]
    if release.get("managed_model"):
        from managed_release_checks import audit_model_sources
        errors = audit_model_sources(root, ((path.relative_to(root).as_posix(),path) for path in files))
        if errors:
            raise ValueError("managed model archive audit failed:\n" + "\n".join(errors))
    baseline_count = len(json.loads((root / "kit/manifest.json").read_text(encoding="utf-8"))["skills"])
    descriptor = {"schema": "codex-agents.package/1", "mode": mode,
                  "suite_version": version, "repository_version": release["repository_version"],
                  "requirements": release["requirements"], "installation_performed": False,
                  "entry_point": "START_HERE.md", "skill_sources": "kit/skills",
                  "manifest": "kit/manifest.json", "baseline_skill_count": baseline_count,
                  "optional_maintenance_skill": "maintenance-skill",
                  "installation_workflow": ("supported Work personal-skill manager; one save per skill; verify registry and actual invocation"
                                            if mode == "WORK" else "for managed releases: verify stable provenance and staged kit, then portable audit -> apply -> verify; verify host discovery separately")}
    if release["repository_branch"]:
        descriptor["repository_branch"] = release["repository_branch"]
    if release.get("release_stage") is not None:
        descriptor["release_stage"] = release["release_stage"]
    package_readme = (f"# Agent System {version} — {mode} source bundle\n\n"
                      "Choose your language in [START_HERE.md](START_HERE.md), then read that complete guide.\n\n"
                      f"[Release and component versions](releases/current.json) · [Requirements]({release['requirements']})\n\n"
                      "This archive contains the same verified reusable sources and continuity records as the other mode's bundle. "
                      "PACKAGE.json and this introduction identify the intended installation workflow; extracting an archive does not install a skill.\n\n")
    if mode == "WORK":
        package_readme += ("In ChatGPT Work, connect the GitHub repository or provide these extracted sources. Ask the supported personal-skill manager "
                           f"to inspect and install/update the {baseline_count} baseline skills from kit/skills. It must save each personal skill through the supported "
                           "management workflow and verify the registered sources. A repository connection, a read SKILL.md or a copied archive alone "
                           "is not installation. Work's host avatar may differ from portable Codex icons.\n\n")
    else:
        package_readme += ("For managed Codex adoption, verify the approved stable archive and its GitHub attestation. Audit the exact staged kit "
                           "from the admission receipt using the trusted portable updater. Follow [installation and operation](docs/INSTALL.md). Keep plans and backups "
                           "outside skill discovery roots, preserve existing icons and local modifications, pass the actual journal to verify, and check fresh "
                           "host discovery separately. A local source build can be used for inspection and isolated fixture rehearsal.\n\n")
    package_readme += (f"maintenance-skill/ is an optional repository-maintenance instruction skill, separate from the {baseline_count} baseline skills. "
                       "Install it through the supported manager only when requested; including its sources in this archive does not activate it. "
                       "Review ownership and current product state before adopting an update in an existing project.\n")
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
        write_zip(root, path, files, mode, result)
        result_files.append({"name": path.name, "size": path.stat().st_size,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    sums = "".join(f"{item['sha256']}  {item['name']}\n" for item in result_files)
    (output / "SHA256SUMS").write_text(sums, encoding="utf-8")
    receipt = {"schema": "codex-agents.build/1", "suite_version": result["suite_version"],
               "repository_version": result["repository_version"], "source_files": len(files),
               "files": result_files, "host_installation_verified": False}
    if result["repository_branch"]:
        receipt["repository_branch"] = result["repository_branch"]
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
