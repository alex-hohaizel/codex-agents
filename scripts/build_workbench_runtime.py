#!/usr/bin/env python3
"""Build an offline macOS workbench runtime from an exact source and signed Node archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOTS = ("kit", "scripts", "standards", "host-profiles", "agent-profiles", "optional-skills",
         "maintenance-skill", "releases", "templates", "governance")
IGNORE = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", ".DS_Store"}
NODE_VERSION = "24.22.2"
SCHEMA = "codex-agents.workbench-runtime/1"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, timeout=180, **kwargs)
    require(result.returncode == 0, f"Command failed: {Path(str(args[0])).name}: " + result.stderr[-1800:])
    return result.stdout


def safe_file(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "Expected regular source file: " + str(path))
    return path


def copy_tree(source, destination, *, skip_tests=False):
    require(source.is_dir() and not source.is_symlink(), "Required runtime source absent: " + str(source))
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if IGNORE.intersection(rel.parts) or (skip_tests and "tests" in rel.parts) or path.suffix == ".pyc":
            continue
        require(not path.is_symlink(), "Linked runtime source rejected: " + str(path))
        if not path.is_file():
            continue
        require(not any(p.startswith(".env") for p in rel.parts), "Credential-like runtime path rejected")
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        target.chmod(0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644)


def extract_node(archive, destination, arch):
    prefix = f"node-v{NODE_VERSION}-darwin-{arch}/"
    required = {"bin/node", "LICENSE"}
    result = {}
    with tarfile.open(archive, "r:gz") as package:
        for item in package:
            if item.isdir() and item.name.rstrip("/") == prefix.rstrip("/"):
                continue
            require(item.name.startswith(prefix), "Unexpected Node archive namespace")
            name = item.name[len(prefix):]
            parts = PurePosixPath(name).parts
            require(not PurePosixPath(name).is_absolute() and ".." not in parts, "Unsafe Node archive path")
            if name not in required:
                continue
            require(item.isfile() and item.size <= 256 * 1024 * 1024 and name not in result,
                    "Invalid or duplicate Node runtime member")
            output = destination / ("bin/node" if name == "bin/node" else "notices/Node-LICENSE.txt")
            output.parent.mkdir(parents=True, exist_ok=True)
            with package.extractfile(item) as reader, output.open("xb") as target:
                shutil.copyfileobj(reader, target)
            output.chmod(0o755 if name == "bin/node" else 0o644)
            result[name] = output
    require(set(result) == required, "Node archive omits runtime or notices")
    return result


def verify_node(archive, signed_sums, keyring, lock, arch):
    arch_lock = lock["archives"][arch]
    require(archive.name == arch_lock["name"] and sha(archive) == arch_lock["sha256"], "Wrong or corrupted official Node archive")
    require(sha(keyring) == lock["keyring"]["sha256"], "Node release keyring differs from the reviewed source")
    require(sha(signed_sums) == lock["signed_checksums_sha256"], "Node signed checksums differ from the reviewed release")
    gpgv = shutil.which("gpgv")
    require(gpgv is not None, "Developer build requires gpgv to verify official Node release signatures")
    with tempfile.TemporaryDirectory(prefix="agent-runtime-gpg-") as scratch:
        home = Path(scratch); home.chmod(0o700)
        result = subprocess.run([gpgv, "--homedir", str(home), "--keyring", str(keyring),
                                 "--status-fd", "2", "--output", "-", str(signed_sums)],
                                capture_output=True, text=True, timeout=45)
        require(result.returncode == 0, "Official Node signed checksum verification failed")
        valid = [row.split()[2] for row in result.stderr.splitlines() if row.startswith("[GNUPG:] VALIDSIG ")]
        require(valid and set(valid) <= set(lock["accepted_signing_fingerprints"]), "Node signer is not in the reviewed release record")
        rows = result.stdout.splitlines()
        require(f"{arch_lock['sha256']}  {arch_lock['name']}" in rows, "The signed Node release omits the requested archive")
    return {"archive": arch_lock, "signed_checksums_sha256": sha(signed_sums),
            "keyring_sha256": sha(keyring), "valid_signer_fingerprints": valid,
            "verification": "gpgv-valid-signed-checksums"}


def dependencies_notices(app, destination):
    lock = json.loads((app/"package-lock.json").read_text())
    included = []
    pending = list(json.loads((app/"package.json").read_text())["dependencies"])
    names = set()
    while pending:
        package_name = pending.pop()
        if package_name in names:
            continue
        names.add(package_name)
        manifest = json.loads(safe_file(app/"node_modules"/package_name/"package.json").read_text())
        pending.extend(manifest.get("dependencies", {}))
    for package_name in sorted(names):
        name = "node_modules/" + package_name
        entry = lock["packages"][name]
        require(name.startswith("node_modules/") and ".." not in Path(name).parts, "Invalid dependency path")
        folder = app/name
        package = json.loads(safe_file(folder/"package.json").read_text())
        candidates = sorted(p for p in folder.iterdir() if p.name.lower() in {"license", "license.md", "license.txt", "copying"})
        require(candidates, "Production dependency omits redistribution license: " + name)
        for file in candidates:
            safe_file(file)
            target = destination/(package["name"].replace("/", "-") + "-" + package["version"] + "-" + file.name)
            shutil.copyfile(file, target)
        included.append({"name": package["name"], "version": package["version"], "license": package.get("license"),
                         "integrity": entry.get("integrity"), "delivery": "compiled-into-client"})
    return included


def write_zip(directory, path):
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(directory.rglob("*")):
            if not file.is_file():
                continue
            name = directory.name + "/" + file.relative_to(directory).as_posix()
            info = zipfile.ZipInfo(name, (2026, 11, 18, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | stat.S_IMODE(file.stat().st_mode)) << 16
            archive.writestr(info, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(root, output, arch, node_archive, signed_sums, keyring, *, allow_dirty=False):
    root = root.resolve(strict=True)
    commit = run(["git", "rev-parse", "HEAD"], cwd=root).strip()
    require(re.fullmatch("[a-f0-9]{40}", commit), "Expected actual exact source commit")
    dirty = run(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=root).strip()
    require(allow_dirty or not dirty, "Commit the reviewed source before producing a distributable; --allow-dirty is rehearsal only")
    sources = root/"commercial/runtime"
    lock = json.loads((sources/"node-sources.json").read_text())
    provenance = verify_node(safe_file(node_archive).resolve(), safe_file(signed_sums).resolve(),
                             safe_file(keyring).resolve(), lock, arch)
    release = json.loads((root/"releases/current.json").read_text())
    app = root/"apps/agent-atelier"
    version = json.loads((app/"package.json").read_text())["version"]
    require((app/"dist/client/index.html").is_file(), "Developer step required: npm ci --ignore-scripts && npm run build in apps/agent-atelier")
    output = output.resolve()
    require(output != root and root not in output.parents, "Build runtime artifacts outside the source checkout")
    require(not output.exists() or (output.is_dir() and not output.is_symlink()), "Invalid output directory")
    output.mkdir(parents=True, exist_ok=True)
    name = f"Agent-Atelier-{version}-macOS-{arch}"
    destination = output/name
    require(not destination.exists() and not (output/(name+".zip")).exists(), "Runtime output already exists; choose a fresh destination")
    destination.mkdir()
    extract_node(node_archive, destination, arch)
    for relative in ROOTS:
        copy_tree(root/relative, destination/relative, skip_tests=True)
    for relative in ("AGENTS.md", "RIGHTS.md"):
        shutil.copyfile(root/relative, destination/relative)
    for relative in ("server", "shared", "launcher", "dist/client"):
        copy_tree(app/relative, destination/"apps/agent-atelier"/relative)
    for relative in ("package.json", "requirements.json"):
        shutil.copyfile(app/relative, destination/"apps/agent-atelier"/relative)
    for relative in ("control.mjs", "Runtime.command", "Launch.command", "Stop.command", "README.md", "README.uk.md"):
        shutil.copyfile(sources/relative, destination/relative)
        (destination/relative).chmod(0o755 if relative.endswith(".command") else 0o644)
    deps = dependencies_notices(app, destination/"notices")
    for relative in ("node-sources.json",):
        shutil.copyfile(sources/relative, destination/relative)
    desc = {"schema": SCHEMA, "product_version": release["repository_version"], "service_version": version,
            "source_commit": commit, "release_candidate": True, "source_clean": not bool(dirty),
            "platform": {"os": "darwin", "arch": arch, "minimum_version": "13.5", "hardware_models_verified": []},
            "node_version": NODE_VERSION, "node_provenance": provenance, "production_dependencies": deps,
            "sqlite_schema_max": 1, "backups": "agent-atelier.backup/1",
            "developer_id_signature": "not-signed-for-product-distribution",
            "notarization": "not-submitted; developer credentials and owner release approval required",
            "runtime_execution": "unverified-until-tested-on-target", "files": {}}
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            desc["files"][path.relative_to(destination).as_posix()] = {
                "sha256": sha(path), "size": path.stat().st_size, "mode": stat.S_IMODE(path.stat().st_mode)}
    require(run(["git", "rev-parse", "HEAD"], cwd=root).strip() == commit,
            "Source commit changed during runtime build")
    require(allow_dirty or not run(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=root).strip(),
            "Source bytes changed during runtime build; keep this output unshipped and rebuild")
    (destination/"runtime-manifest.json").write_text(json.dumps(desc, indent=2, sort_keys=True)+"\n")
    zip_path = output/(name+".zip")
    write_zip(destination, zip_path)
    receipt = {"schema": "codex-agents.workbench-runtime-build/1", "directory": str(destination),
               "artifact": str(zip_path), "sha256": sha(zip_path), "size": zip_path.stat().st_size,
               "manifest_sha256": sha(destination/"runtime-manifest.json"), "source_commit": commit,
               "source_clean": not bool(dirty), "target": desc["platform"], "notarized": False,
               "production_dependencies": deps}
    (output/(name+".build.json")).write_text(json.dumps(receipt, indent=2)+"\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--arch", choices=("arm64", "x64"), required=True)
    parser.add_argument("--node-archive", type=Path, required=True)
    parser.add_argument("--signed-checksums", type=Path, required=True)
    parser.add_argument("--keyring", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true", help="Local rehearsal only, marked in descriptor")
    args = parser.parse_args()
    try:
        result = build(args.root,args.output,args.arch,args.node_archive,args.signed_checksums,args.keyring,allow_dirty=args.allow_dirty)
        print(json.dumps(result, indent=2)); return 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"status":"blocked","reason":str(error)}),file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
