#!/usr/bin/env python3
"""Capture a bounded interrupted Git worktree and verify it before resuming."""

import argparse
import json
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
import ticket_tree
import ticket_worktree as worktree

context = ticket_tree.context
INTERRUPTION = "atelier.worktree-interruption/1"
CHECKPOINT = "atelier.ticket-worktree-checkpoint/1"
ADMISSION = "atelier.ticket-worktree-resume/1"


def read_pinned(path, digest):
    context.require(isinstance(digest, str) and context.HASH.fullmatch(digest),
                    "invalid input SHA-256")
    context.require(path.is_absolute() and path.resolve() == path and path.is_file(),
                    "expected a canonical absolute input file")
    with path.open("rb") as stream:
        raw = stream.read(context.MAX_BOUND_SOURCE + 1)
    context.require(len(raw) <= context.MAX_BOUND_SOURCE and context.digest(raw) == digest,
                    f"input pin mismatch: {path.name}")
    return context.json_object(raw)


def pin(path, digest):
    return {"path": str(path), "sha256": digest}


def interrupt_record(path, digest, binding_sha256):
    record = read_pinned(path, digest)
    fields = {"schema_version", "binding_sha256", "state", "native_run_ref",
              "readback_ref", "next_action"}
    context.require(set(record) == fields and record["schema_version"] == INTERRUPTION
                    and record["state"] == "interrupted"
                    and record["binding_sha256"] == binding_sha256,
                    "expected the exact interrupted operation's terminal readback")
    for key in ("native_run_ref", "readback_ref", "next_action"):
        context.require(len(context.text(record, key)) <= 2000, f"interruption {key} is too large")
    return record


def work_status(root, allowed):
    output = worktree.git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                          "--no-renames", "--ignored=matching", "--ignore-submodules=none")
    parts = output.decode("utf-8").split("\0")
    context.require(parts.pop() == "", "malformed Git status")
    result = {}
    for line in parts:
        state, name = line[:2], line[3:]
        context.require(len(line) > 3 and line[2] == " " and state in {" M", " D", "??"},
                        f"unexpected staged, ignored or conflicted Git state: {line[:160]}")
        context.require(name in allowed and name not in result,
                        f"interrupted worktree has changes outside the assignment: {name}")
        result[name] = state
    return result


def file_state(root, paths):
    states = {}
    total = 0
    for name in paths:
        path = context.local(root, name, existing=False)
        if not path.exists():
            states[name] = None
            continue
        info = path.lstat()
        context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                        f"checkpoint requires a regular unlinked file: {name}")
        with path.open("rb") as stream:
            raw = stream.read(context.MAX_BOUND_SOURCE + 1)
        total += len(raw)
        context.require(len(raw) <= context.MAX_BOUND_SOURCE and total <= 32 * 1024 * 1024,
                        f"checkpoint file or aggregate limit exceeded: {name}")
        states[name] = {"sha256": context.digest(raw), "mode": stat.S_IMODE(info.st_mode)}
    return states


def observe(binding):
    identity = worktree.check_binding(binding, require_clean=False)
    context.require(identity["head"] == binding["base"],
                    "expected to resume from the original uncommitted worktree")
    worker = Path(binding["worktree"])
    paths = binding["write_paths"]
    before = work_status(worker, paths)
    context.require(before, "no durable unfinished changes to resume")
    states = file_state(worker, paths)
    context.require(before == work_status(worker, paths)
                    and states == file_state(worker, paths)
                    and identity == worktree.check_binding(binding, require_clean=False),
                    "worktree changed during the checkpoint readback")
    return {"head": identity["head"], "dirty_paths": before, "scoped_files": states}


def capture(binding_path, binding_sha, interruption_path, interruption_sha):
    context.require(binding_path.is_absolute() and binding_path.resolve() == binding_path,
                    "expected a canonical absolute binding file")
    binding = worktree.load_binding(binding_path, binding_sha)
    worker = Path(binding["worktree"])
    context.require(worker not in binding_path.parents and worker not in interruption_path.parents,
                    "keep checkpoint inputs outside the write worktree")
    stop = interrupt_record(interruption_path, interruption_sha, binding_sha)
    state = observe(binding)
    context.require(stop == interrupt_record(interruption_path, interruption_sha, binding_sha)
                    and binding == worktree.load_binding(binding_path, binding_sha),
                    "checkpoint inputs changed during capture")
    return {
        "schema_version": CHECKPOINT,
        "binding": pin(binding_path, binding_sha),
        "interruption": pin(interruption_path, interruption_sha),
        "worktree": binding["worktree"], "next_action": stop["next_action"],
        **state, "native_run_ref": stop["native_run_ref"],
        "native_interruption_authenticated": False, "new_session_started": False,
    }


def resume(path, digest):
    record = read_pinned(path, digest)
    context.require(record.get("schema_version") == CHECKPOINT, "unsupported worktree checkpoint")
    try:
        binding = record["binding"]
        interruption = record["interruption"]
        observed = capture(Path(binding["path"]), binding["sha256"],
                           Path(interruption["path"]), interruption["sha256"])
    except (KeyError, TypeError) as error:
        raise context.ContextError("invalid worktree checkpoint fields") from error
    context.require(Path(observed["worktree"]) not in path.parents,
                    "keep the checkpoint outside the write worktree")
    context.require(observed == record and record == read_pinned(path, digest),
                    "worktree checkpoint is stale; reconcile the interrupted work")
    return {
        "schema_version": ADMISSION, "status": "ready-to-resume",
        "checkpoint": pin(path, digest), "worktree": observed["worktree"],
        "resumed_from": observed["native_run_ref"], "next_action": observed["next_action"],
        "scoped_files": observed["scoped_files"], "new_session_started": False,
        "native_interruption_authenticated": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    start, finish = modes.add_parser("capture"), modes.add_parser("resume")
    for opt in ("binding", "interruption"):
        start.add_argument("--" + opt, type=Path, required=True)
        start.add_argument("--" + opt + "-sha256", required=True)
    finish.add_argument("--checkpoint", type=Path, required=True)
    finish.add_argument("--checkpoint-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.mode == "capture":
            result = capture(args.binding, args.binding_sha256,
                             args.interruption, args.interruption_sha256)
        else:
            result = resume(args.checkpoint, args.checkpoint_sha256)
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "worktree-admission-refused", "error": str(error)},
                         ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
