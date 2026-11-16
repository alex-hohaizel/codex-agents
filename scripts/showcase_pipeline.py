#!/usr/bin/env python3
"""Run localized showcase stages with bounded commands and verified resume receipts.

This runner does not publish, deploy, install skills, or operate another chat.
Its stable filename and checkpoint schema preserve existing caller compatibility.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading
from typing import Callable
import zipfile

SCHEMA = "codex-agents.showcase-pipeline/1"
LOG_LIMIT = 64 * 1024
IGNORED = {".git", "__pycache__", ".pytest_cache", ".venv", ".DS_Store", "node_modules", "dist", ".atelier-local", "test-results", "playwright-report"}
PACKAGE_ROOTS = ("kit", "AGENTS.md", "README.md", "START_HERE.md", "CHANGELOG.md",
                 "RIGHTS.md", "locales.json", "maintenance-skill", "docs", "templates",
                 "governance", "releases", "scripts", "marketing", "assets",
                 "standards", "host-profiles", "agent-profiles", "optional-skills", "evaluations", "apps")


class TerminationRequested(KeyboardInterrupt):
    def __init__(self, signum: int):
        super().__init__(f"termination signal {signum}")
        self.signum = signum


@contextmanager
def termination_signals():
    """Turn termination into cleanup followed by exit, never continued execution."""
    previous = {}

    def terminate(signum, frame):
        raise TerminationRequested(signum)

    try:
        for name in ("SIGTERM", "SIGHUP"):
            signum = getattr(signal, name, None)
            if signum is not None:
                previous[signum] = signal.signal(signum, terminate)
        yield
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def within(root: Path, relative: str) -> Path:
    candidate = root / relative
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"path leaves repository: {relative}")
    return candidate


def inventory(root: Path, roots: tuple[str, ...], excluded: tuple[str, ...] = (), *,
              ignore_transient_files: bool = True) -> dict:
    """Fingerprint paths, contents and executable bits, including missing inputs."""
    files = {}
    for relative in roots:
        start = within(root, relative)
        candidates = sorted(start.rglob("*")) if start.is_dir() else [start]
        if not start.exists():
            files[relative] = {"missing": True}
        for path in candidates:
            relative_path = path.relative_to(root)
            rel = relative_path.as_posix()
            if ignore_transient_files and (IGNORED.intersection(relative_path.parts) or path.suffix == ".pyc"):
                continue
            if any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in excluded):
                continue
            if path.is_symlink():
                raise ValueError(f"symlink is not a stable pipeline input: {rel}")
            if path.is_file():
                files[rel] = {"sha256": sha(path), "size": path.stat().st_size,
                              "executable": bool(path.stat().st_mode & 0o100)}
    return dict(sorted(files.items()))


@dataclass(frozen=True)
class Stage:
    name: str
    commands: tuple[tuple[str, ...], ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...] = ()
    excluded_inputs: tuple[str, ...] = ()
    staged_output_dir: str | None = None
    validator: str | None = None
    private_outputs: tuple[str, ...] = ()


def input_digest(root: Path, stage: Stage) -> str:
    files = inventory(root, stage.inputs, stage.excluded_inputs)
    missing = [path for path, record in files.items() if record.get("missing")]
    if missing:
        raise ValueError("missing stage inputs: " + ", ".join(missing))
    source = {"stage": asdict(stage), "files": files}
    return hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()


def output_inventory(root: Path, stage: Stage) -> dict:
    result = inventory(root, stage.outputs + stage.private_outputs, ignore_transient_files=False)
    missing = [path for path, record in result.items() if record.get("missing")]
    if missing:
        raise ValueError("missing stage outputs: " + ", ".join(missing))
    return result


def run_command(command: list[str], root: Path, timeout: float, log: Path) -> None:
    """Kill the whole command group on timeout or interruption; preserve bounded logs."""
    log.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=(os.name == "posix"))
    reader_errors = []

    def capture():
        tail = bytearray()
        try:
            with log.open("wb") as stream:
                while block := os.read(process.stdout.fileno(), 8192):
                    tail.extend(block)
                    del tail[:-LOG_LIMIT]
                    stream.seek(0)
                    stream.write(tail)
                    stream.truncate()
                    stream.flush()
        except (OSError, ValueError) as exc:
            reader_errors.append(exc)

    def stop_group():
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        process.wait()

    reader = threading.Thread(target=capture, daemon=True)
    reader.start()
    try:
        status = process.wait(timeout=timeout)
    except BaseException:
        stop_group()
        raise
    finally:
        if os.name == "posix":
            # Command success does not transfer ownership to background
            # descendants, even when they detached their logging streams.
            stop_group()
        reader.join(timeout=1)
        if reader.is_alive():
            # A background descendant must not retain the log pipe after its
            # command exits. The stage owns its process group.
            stop_group()
            reader.join(timeout=1)
        if not reader.is_alive():
            process.stdout.close()
    if reader.is_alive():
        raise RuntimeError("command descendants retained the output pipe")
    if reader_errors:
        raise RuntimeError(f"could not capture command output: {reader_errors[0]}")
    if status:
        with log.open("rb") as stream:
            stream.seek(max(0, log.stat().st_size - 4096))
            detail = stream.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"command exited {status}; log={log}\n{detail}")


@contextmanager
def execution_lock(path: Path):
    """Only one process may write a checkpoint and promote its outputs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        if os.name == "posix":
            import fcntl
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError("pipeline already running; wait for its owner to finish") from exc
        else:
            import msvcrt
            stream.seek(0)
            stream.write(b"\0")
            stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError("pipeline already running; wait for its owner to finish") from exc
        try:
            yield
        finally:
            if os.name == "posix":
                fcntl.flock(stream, fcntl.LOCK_UN)
            else:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def validate_export(directory: Path) -> None:
    receipt = json.loads((directory / "exports.json").read_text(encoding="utf-8"))
    expected = {"index.html", "Showcase.pdf", *(f"{locale}.html" for locale in ("en", "uk", "de", "it", "es", "fr", "zh-CN"))}
    records = receipt.get("files", [])
    if len(records) != len(expected) or {entry.get("path") for entry in records} != expected:
        raise ValueError("export must contain the seven localized galleries, language selector, and showcase PDF")
    for entry in records:
        path = within(directory, entry["path"])
        payload = path.read_bytes()
        if path.suffix == ".pdf":
            count = len(re.findall(rb"/Type\s*/Page\b", payload))
            if not payload.startswith(b"%PDF-") or count != 10:
                raise ValueError(f"PDF page count mismatch: {path.name}")
        elif not payload.lstrip().lower().startswith(b"<!doctype html"):
            raise ValueError(f"invalid campaign gallery: {path.name}")
        if sha(path) != entry.get("sha256") or len(payload) != entry.get("size"):
            raise ValueError(f"campaign export receipt mismatch: {path.name}")


def validate_package(directory: Path) -> None:
    receipt = json.loads((directory / "BUILD.json").read_text(encoding="utf-8"))
    records = receipt.get("files", [])
    if len(records) != 2:
        raise ValueError("package must contain two source archives")
    for entry in records:
        if Path(entry["name"]).name != entry["name"]:
            raise ValueError("unsafe archive name in package receipt")
        path = directory / entry["name"]
        if sha(path) != entry.get("sha256") or path.stat().st_size != entry.get("size"):
            raise ValueError(f"package receipt mismatch: {path.name}")
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"corrupt archive member: {bad}")
            if json.loads(archive.read("PACKAGE.json")).get("installation_performed") is not False:
                raise ValueError("source archive must not claim installation")
    expected_sums = "".join(f"{entry['sha256']}  {entry['name']}\n" for entry in records)
    if (directory / "SHA256SUMS").read_text(encoding="utf-8") != expected_sums:
        raise ValueError("package SHA256SUMS mismatch")


def default_stages(root: Path) -> list[Stage]:
    s = "marketing/campaign"
    artifacts = "reports/local-campaign-artifacts"
    version = json.loads((root / "releases/current.json").read_text(encoding="utf-8"))["suite_version"]
    galleries = ("en", "uk", "de", "it", "es", "fr", "zh-CN")
    source = (s, "assets/marketing/current", "assets/marketing/concepts", "locales.json", "marketing/README.md",
              "releases/current.json", "scripts/showcase_pipeline.py",
              *(f"marketing/{locale}/README.md" for locale in galleries))
    exports = tuple(f"{s}/{name}" for name in ("index.html", "Showcase.pdf", "exports.json",
                                              *(f"{locale}.html" for locale in galleries)))
    packages = tuple(f"dist/Agent_System_{version}_{mode}.zip" for mode in ("WORK", "CODEX")) + ("dist/BUILD.json", "dist/SHA256SUMS")
    return [
        Stage("export", (("{python}", "-B", f"{s}/build_campaign.py", "--output", "{output}",
                           "--artifacts-output", "{root}/" + artifacts),
                          ("{python}", "-B", f"{s}/check_campaign.py", "--output", "{output}",
                           "--artifacts-output", "{root}/" + artifacts)),
              source, exports, exports, s, "export", (artifacts,)),
        Stage("build", (("{python}", "-B", f"{s}/check_campaign.py", "--check-source"),),
              source + exports),
        Stage("validate", (("{python}", "-B", "kit/verify_release.py"),
                           ("{python}", "-B", "scripts/check_repository.py"),
                           ("{python}", "-B", "-m", "unittest", "discover", "-s", "scripts/tests", "-v")), PACKAGE_ROOTS),
        Stage("package", (("{python}", "-B", "scripts/build_packages.py", "--output", "{output}"),),
              PACKAGE_ROOTS, packages, (), "dist", "package"),
    ]


class Pipeline:
    def __init__(self, root: Path, state_path: Path, stages: list[Stage], timeout: float = 180,
                 runner: Callable = run_command):
        self.root = root.resolve()
        self.state_path = state_path.resolve()
        self.stages = stages
        self.timeout = timeout
        self.runner = runner
        self.state = {"schema": SCHEMA, "root": str(self.root), "stages": {}}
        protected = set(PACKAGE_ROOTS)
        for stage in stages:
            protected.update(stage.inputs + stage.outputs + stage.private_outputs)
            if stage.staged_output_dir:
                protected.add(stage.staged_output_dir)
        for relative in protected:
            path = within(self.root, relative).resolve()
            if self.state_path.is_relative_to(path) or (self.state_path.parent / "local-showcase-logs").is_relative_to(path):
                raise ValueError("keep checkpoint and logs outside packaged inputs and stage outputs; use reports/local-showcase-pipeline.json")

    def load(self):
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(self.state, dict) or self.state.get("schema") != SCHEMA or self.state.get("root") != str(self.root):
                raise ValueError("checkpoint schema or repository differs; use a new state path")
            if not isinstance(self.state.get("stages"), dict) or any(not isinstance(record, dict) for record in self.state["stages"].values()):
                raise ValueError("checkpoint stage records are invalid; retain the file for diagnosis and use a new state path")

    def save(self):
        self.state["updated_at"] = now()
        atomic_json(self.state_path, self.state)

    def reusable(self, stage: Stage, digest: str) -> bool:
        record = self.state["stages"].get(stage.name, {})
        if record.get("status") != "complete" or record.get("input_digest") != digest:
            return False
        try:
            return record.get("outputs") == output_inventory(self.root, stage)
        except (ValueError, OSError):
            return False

    def run(self, until: str | None = None, force: tuple[str, ...] = ()) -> dict:
        with execution_lock(self.root / "reports/local-showcase-pipeline.lock"):
            self.load()  # Read after acquiring ownership, never from a stale instance.
            return self.run_stages(until, force)

    def run_stages(self, until: str | None = None, force: tuple[str, ...] = ()) -> dict:
        if until is not None and until not in {stage.name for stage in self.stages}:
            raise ValueError(f"unknown stage: {until}")
        if any(name != "all" and name not in {stage.name for stage in self.stages} for name in force):
            raise ValueError("unknown forced stage")
        result = []
        for stage in self.stages:
            digest = input_digest(self.root, stage)
            if "all" not in force and stage.name not in force and self.reusable(stage, digest):
                result.append({"stage": stage.name, "status": "verified-cache"})
                print(json.dumps(result[-1]), flush=True)
            else:
                previous = self.state["stages"].get(stage.name, {})
                record = {"status": "running", "started_at": now(), "input_digest": digest,
                          "attempt": previous.get("attempt", 0) + 1, "outputs": {}}
                self.state["stages"][stage.name] = record
                self.save()  # Never leave an old successful receipt for an in-flight attempt.
                print(json.dumps({"stage": stage.name, "status": "running", "attempt": record["attempt"]}), flush=True)
                try:
                    self.execute(stage, record)
                    if input_digest(self.root, stage) != digest:
                        raise ValueError("inputs changed during stage; result not accepted; resume after edits settle")
                    record.update(status="complete", completed_at=now(), outputs=output_inventory(self.root, stage))
                    self.save()
                except BaseException as exc:
                    record.update(status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                                  completed_at=now(), error_type=type(exc).__name__, error=str(exc))
                    self.save()
                    raise
                result.append({"stage": stage.name, "status": "complete"})
                print(json.dumps(result[-1]), flush=True)
            if stage.name == until:
                break
        return {"ok": True, "stages": result, "checkpoint": str(self.state_path),
                "publication_performed": False, "chat_platform_repair_claimed": False}

    def execute(self, stage: Stage, record: dict):
        target = within(self.root, stage.staged_output_dir) if stage.staged_output_dir else None
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
        staging = self.root / "reports"
        staging.mkdir(parents=True, exist_ok=True)
        # A hard kill cannot run TemporaryDirectory cleanup. Keep remnants
        # outside curated package inputs so a later build cannot ship them.
        with tempfile.TemporaryDirectory(prefix=f"local-showcase-{stage.name}-", dir=staging) as temp:
            output = Path(temp)
            for number, command in enumerate(stage.commands, 1):
                args = [part.format(python=sys.executable, root=str(self.root), output=str(output)) for part in command]
                log = self.state_path.parent / "local-showcase-logs" / f"{stage.name}-{record['attempt']:03}-{number:02}.log"
                record.setdefault("logs", []).append(str(log))
                self.save()
                self.runner(args, self.root, self.timeout, log)
            if stage.validator == "export":
                validate_export(output)
            elif stage.validator == "package":
                validate_package(output)
            if target:
                # Each file replacement is atomic on this filesystem. The whole set is
                # accepted only after its final output inventory has been checkpointed.
                for relative in stage.outputs:
                    destination = within(self.root, relative)
                    source = output / destination.relative_to(target)
                    if not source.is_file() or source.is_symlink():
                        raise ValueError(f"missing staged output: {source.name}")
                if input_digest(self.root, stage) != record["input_digest"]:
                    raise ValueError("inputs changed during stage; staged output not installed")
                for relative in stage.outputs:
                    destination = within(self.root, relative)
                    source = output / destination.relative_to(target)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--state", type=Path, help="defaults to ROOT/reports/local-showcase-pipeline.json")
    parser.add_argument("--until", choices=("export", "build", "validate", "package"), help="finish this stage, then stop cleanly")
    parser.add_argument("--force", choices=("all", "export", "build", "validate", "package"), action="append", default=[])
    parser.add_argument("--timeout", type=float, default=180, help="seconds per child command (default: 180)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    root = args.root.resolve()
    state = args.state or root / "reports/local-showcase-pipeline.json"
    try:
        with termination_signals():
            result = Pipeline(root, state, default_stages(root), args.timeout).run(args.until, tuple(args.force))
        print(json.dumps(result, indent=2))
        return 0
    except KeyboardInterrupt as exc:
        print("Interrupted; completed stages remain resumable. Re-run the same command.", file=sys.stderr)
        return 128 + getattr(exc, "signum", signal.SIGINT)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "checkpoint": str(state), "publication_performed": False}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
