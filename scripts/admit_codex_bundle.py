#!/usr/bin/env python3
"""Verify and stage an approved Codex source bundle for the portable updater.

The expected Git commit, release versions, archive and manifest digests, and
signer workflow come from the operator's approved release record. Embedded
metadata is only checked against those pins. Declare a first install or provide
the observed installed suite version. The portable updater audits the actual
destination before installation.
"""
from __future__ import annotations

import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

from build_packages import COMMON, EXCLUDED_PARTS


REPOSITORY = "alex-hohaizel/codex-agents"
PREDICATE = "https://slsa.dev/provenance/v1"
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_CONTENT = 2 * 1024 * 1024 * 1024
MAX_MEMBER = 128 * 1024 * 1024
MAX_ENTRIES = 20_000
REQUIRED = {"PACKAGE.json", "releases/current.json", "kit/manifest.json",
            "kit/portable/update_skill_suite.py"}
ALLOWED_ROOTS = {"kit", "PACKAGE.json", "PACKAGE_README.md", *COMMON}
GIT_SHA = re.compile(r"[a-f0-9]{40}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
STABLE_VERSION = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\Z")
SIGNER = re.compile(r"\.github/workflows/[A-Za-z0-9][A-Za-z0-9_.-]*\.ya?ml\Z")
REF = re.compile(r"refs/(?:heads|tags)/[A-Za-z0-9][A-Za-z0-9._/-]*\Z")


@dataclass(frozen=True)
class ReleasePin:
    source_sha: str
    source_ref: str
    signer_workflow: str
    archive_sha256: str
    manifest_sha256: str
    repository_version: str
    suite_version: str
    installed_suite_version: str | None

    def validate(self):
        if not GIT_SHA.fullmatch(self.source_sha):
            raise ValueError("Expected the full lowercase approved Git commit")
        if (not REF.fullmatch(self.source_ref) or ".." in self.source_ref
                or any(not part or part.endswith((".", ".lock"))
                       for part in self.source_ref.split("/"))):
            raise ValueError("Expected an exact approved Git branch or release tag ref")
        if not SIGNER.fullmatch(self.signer_workflow):
            raise ValueError("Expected the approved workflow path in .github/workflows")
        if not all(SHA256.fullmatch(x) for x in (self.archive_sha256, self.manifest_sha256)):
            raise ValueError("Approved archive and manifest must have lowercase SHA-256 pins")
        versions = [self.repository_version, self.suite_version]
        if self.installed_suite_version is not None:
            versions.append(self.installed_suite_version)
        if not all(STABLE_VERSION.fullmatch(value) for value in versions):
            raise ValueError("Admission expects stable X.Y.Z version pins")
        if self.installed_suite_version is not None:
            target = tuple(map(int, self.suite_version.split(".")))
            installed = tuple(map(int, self.installed_suite_version.split(".")))
            if target < installed:
                raise ValueError("The target core suite is older than the installed baseline; use rollback")


def load_json(data):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"Duplicate JSON field: {key}")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError(f"Invalid non-finite JSON value: {value}")

    return json.loads(data, object_pairs_hook=pairs, parse_constant=nonfinite)


def copy_archive(source, snapshot):
    digest = hashlib.sha256()
    with os.fdopen(os.open(source, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)), "rb") as origin:
        state = os.fstat(origin.fileno())
        if not stat.S_ISREG(state.st_mode) or not 0 < state.st_size <= MAX_ARCHIVE:
            raise ValueError("Expected a regular, bounded Codex ZIP archive")
        size = 0
        with snapshot.open("xb") as out:
            while True:
                data = origin.read(1024 * 1024)
                if not data:
                    break
                size += len(data)
                if size > MAX_ARCHIVE:
                    raise ValueError("The input archive exceeded the size limit")
                digest.update(data)
                out.write(data)
        if size != state.st_size:
            raise ValueError("The archive changed while copying")
    return digest.hexdigest()


def sha256_file(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_attestation(snapshot, pin):
    action = [
        "gh", "attestation", "verify", str(snapshot), "--hostname", "github.com",
        "--repo", REPOSITORY,
        "--signer-workflow", f"{REPOSITORY}/{pin.signer_workflow}",
        "--source-digest", pin.source_sha, "--source-ref", pin.source_ref,
        "--predicate-type", PREDICATE, "--deny-self-hosted-runners", "--format", "json",
    ]
    verified = subprocess.run(
        action, stdin=subprocess.DEVNULL, capture_output=True, timeout=90, check=False,
        env={**os.environ, "GH_PROMPT_DISABLED": "1"},
    )
    if verified.returncode:
        raise ValueError("GitHub CLI did not verify attestation for the pinned repository, source and workflow")
    results = load_json(verified.stdout)
    if not isinstance(results, list):
        raise ValueError("GitHub CLI returned no verified attestation array")
    matches = 0
    for item in results:
        if not isinstance(item, dict):
            raise ValueError("Unexpected GitHub attestation output")
        result = item.get("verificationResult", {})
        if not isinstance(result, dict):
            raise ValueError("Unexpected GitHub verification result")
        statement = result.get("statement", {})
        if not isinstance(statement, dict) or statement.get("predicateType") != PREDICATE:
            continue
        subjects = statement.get("subject", [])
        if isinstance(subjects, list) and any(
            isinstance(subject, dict) and isinstance(subject.get("digest"), dict)
            and subject["digest"].get("sha256") == pin.archive_sha256
            for subject in subjects
        ):
            matches += 1
    if not matches:
        raise ValueError("No verified SLSA statement matches the approved artifact digest")
    return matches


def archive_entries(bundle):
    entries = bundle.infolist()
    if not 0 < len(entries) <= MAX_ENTRIES:
        raise ValueError("ZIP entry count exceeds the supported envelope")
    names = {}
    folded = {}
    total = 0
    for entry in entries:
        name = entry.orig_filename
        parts = name.split("/")
        if (name != entry.filename or any(
            not part or part in {".", ".."} or part.rstrip(" .") != part
            or "\\" in part or ":" in part or any(ord(ch) < 32 for ch in part)
            or part in EXCLUDED_PARTS or part.startswith(".env")
            for part in parts
        ) or parts[0] not in ALLOWED_ROOTS or name in names):
            raise ValueError(f"Unsafe, duplicate or unapproved archive path: {name!r}")
        mode = entry.external_attr >> 16
        if (entry.create_system != 3 or not stat.S_ISREG(mode)
                or stat.S_IMODE(mode) not in {0o644, 0o755}
                or entry.flag_bits & 1
                or entry.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}):
            raise ValueError(f"Unsupported archive member type or mode: {name!r}")
        total += entry.file_size
        if entry.file_size > MAX_MEMBER or total > MAX_CONTENT:
            raise ValueError("ZIP exceeds the supported expanded size")
        for index in range(1, len(parts) + 1):
            prefix = "/".join(parts[:index])
            key = unicodedata.normalize("NFKC", prefix).casefold()
            if folded.setdefault(key, prefix) != prefix:
                raise ValueError(f"Case or Unicode path collision: {name!r}")
        names[name] = entry
    for name in names:
        parts = name.split("/")
        if any("/".join(parts[:index]) in names for index in range(1, len(parts))):
            raise ValueError(f"Archive file/directory collision: {name!r}")
    if not REQUIRED <= names.keys():
        raise ValueError("Archive is missing required Codex package files")
    return names


def checked_metadata(bundle, files, pin):
    def read(name):
        entry = files[name]
        if entry.file_size > 16 * 1024 * 1024:
            raise ValueError(f"Archive metadata exceeds the supported envelope: {name}")
        return bundle.read(entry)

    package = load_json(read("PACKAGE.json"))
    release = load_json(read("releases/current.json"))
    manifest_bytes = read("kit/manifest.json")
    if not isinstance(package, dict) or not isinstance(release, dict):
        raise ValueError("Package and release metadata must be JSON objects")
    required_package = {"schema": "codex-agents.package/1", "mode": "CODEX",
                        "suite_version": pin.suite_version,
                        "repository_version": pin.repository_version,
                        "manifest": "kit/manifest.json", "skill_sources": "kit/skills"}
    required_release = {"schema_version": "codex-agents.release/1",
                        "repository_version": pin.repository_version,
                        "suite_version": pin.suite_version,
                        "source_manifest_sha256": pin.manifest_sha256}
    if (any(package.get(key) != value for key, value in required_package.items())
            or any(release.get(key) != value for key, value in required_release.items())
            or package.get("installation_performed") is not False):
        raise ValueError("Codex package metadata differs from the approved release pins")
    stages = package.get("release_stage"), release.get("release_stage")
    if stages != ("stable", "stable"):
        raise ValueError("Bundle and release must both be promoted to stable before managed adoption")
    if hashlib.sha256(manifest_bytes).hexdigest() != pin.manifest_sha256:
        raise ValueError("Kit manifest digest differs from the approved release")
    if pin.source_ref.startswith("refs/heads/") and (
        release.get("repository_branch") != pin.source_ref[len("refs/heads/"):]
        or package.get("repository_branch") != release["repository_branch"]
    ):
        raise ValueError("Codex package metadata names a different source branch")


def trusted_read_kit(kit):
    # Validate the extracted data with the existing updater code from this
    # trusted checkout, never by executing a Python file inside the archive.
    path = Path(__file__).resolve().parents[1] / "kit/portable/update_skill_suite.py"
    spec = importlib.util.spec_from_file_location("trusted_portable_updater", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return module.read_kit(kit)
    except module.SuiteError as exc:
        raise ValueError(f"Portable core validation failed: {exc}") from exc


def fresh_staging(path):
    if not path.is_absolute() or not path.parent.is_dir() or platform_support.is_link_or_reparse(path) or path.exists():
        raise ValueError("Stage must be a fresh absolute directory inside an existing parent")
    path = path.parent.resolve() / path.name
    parts = path.parts
    if any(part in {".agents", ".codex"} and parts[index + 1] == "skills"
           for index, part in enumerate(parts[:-1])) or path.is_relative_to(Path("/etc/codex/skills")):
        raise ValueError("Stage must be outside skill discovery roots")
    return path


def admit(archive, stage, pin):
    pin.validate()
    stage = fresh_staging(stage)
    with tempfile.TemporaryDirectory(prefix=".codex-admission-", dir=stage.parent) as temp:
        root = Path(temp)
        snapshot = root / "candidate.zip"
        if copy_archive(archive, snapshot) != pin.archive_sha256:
            raise ValueError("Archive digest differs from the approved bundle")
        verified = verify_attestation(snapshot, pin)
        payload = root / "bundle"
        payload.mkdir(mode=0o700)
        with zipfile.ZipFile(snapshot) as bundle:
            entries = archive_entries(bundle)
            checked_metadata(bundle, entries, pin)
            for name, entry in entries.items():
                target = payload.joinpath(*name.split("/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(entry) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
                platform_support.set_mode(target,stat.S_IMODE(entry.external_attr >> 16))
        if sha256_file(snapshot) != pin.archive_sha256:
            raise ValueError("The verified archive changed before staging")
        trusted_read_kit(payload / "kit")
        stage.mkdir(mode=0o700)
        payload.replace(stage / "bundle")

    return {"status": "admitted-for-updater-audit", "repository": REPOSITORY,
            "source_sha": pin.source_sha, "source_ref": pin.source_ref,
            "signer_workflow": pin.signer_workflow,
            "repository_version": pin.repository_version, "suite_version": pin.suite_version,
            "installation_mode": "fresh" if pin.installed_suite_version is None else "update",
            "installed_suite_version": pin.installed_suite_version,
            "archive_sha256": pin.archive_sha256, "manifest_sha256": pin.manifest_sha256,
            "verified_attestations": verified, "kit": str(stage / "bundle/kit")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--signer-workflow", required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--repository-version", required=True)
    parser.add_argument("--suite-version", required=True)
    installation = parser.add_mutually_exclusive_group(required=True)
    installation.add_argument("--fresh-install", action="store_true",
                              help="Stage a bundle for a destination without managed core skills")
    installation.add_argument("--installed-suite-version",
                              help="Observed version of the installed core suite")
    args = parser.parse_args()
    pin = ReleasePin(**{name: getattr(args, name) for name in ReleasePin.__dataclass_fields__})
    try:
        print(json.dumps(admit(args.archive, args.stage, pin), indent=2))
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
