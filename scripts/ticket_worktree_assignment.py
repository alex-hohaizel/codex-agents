#!/usr/bin/env python3
"""Verify a ready replan handoff against a separate Git worktree before dispatch."""

import argparse
import json
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
import ticket_handoff as handoff
import ticket_worktree as worktree

context = handoff.context
ASSIGNMENT = "atelier.ticket-worktree-assignment/1"


def file_observation(root, ref):
    path = handoff.scoped_file(root, ref)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return {"sha256": None, "mode": None}
    context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                    f"assignment requires a regular unlinked file: {ref}")
    raw = context.bound_bytes(root, ref)
    after = path.lstat()
    attributes = ("st_ino", "st_dev", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    context.require(all(getattr(after, field) == getattr(info, field) for field in attributes),
                    f"file changed during assignment readback: {ref}")
    return {"sha256": context.digest(raw), "mode": stat.S_IMODE(info.st_mode)}


def starting_files(coordinator, worker, approved):
    observed = []
    for item in approved:
        path = item["path"]
        source = file_observation(coordinator, path)
        target = file_observation(worker, path)
        context.require(source["sha256"] == item["sha256"],
                        f"coordinator file differs from the approved handoff: {path}")
        context.require(target["sha256"] == source["sha256"],
                        f"worker starting bytes differ from the approved handoff: {path}")
        context.require(target["mode"] == source["mode"],
                        f"worker starting file mode differs from the coordinator: {path}")
        observed.append({"path": path, **target})
    return observed


def assign(root, handoff_ref, handoff_sha256, binding_path, binding_sha256):
    coordinator = worktree.absolute_path(root, "coordinator")
    binding_path = Path(binding_path)
    context.require(binding_path.is_absolute() and binding_path.resolve() == binding_path,
                    "expected a canonical absolute worktree binding file")
    binding = worktree.load_binding(binding_path, binding_sha256)
    context.require(binding["root"] == str(coordinator),
                    "worktree binding belongs to a different coordinator")
    observed = worktree.check_binding(binding, require_clean=True)
    worker = Path(binding["worktree"])
    context.require(worker not in binding_path.parents,
                    "keep the binding outside the worker checkout")
    current = handoff.verify(coordinator, handoff_ref, handoff_sha256)["handoff"]
    context.require(current["git"]["project_root"] == str(coordinator)
                    and current["git"]["head"] == observed["head"] == binding["base"],
                    "worktree HEAD and selected base must match the approved handoff")
    approved = current["write_paths"]
    context.require(binding["write_paths"] == [item["path"] for item in approved],
                    "worker paths must exactly match the approved product scope")
    files = starting_files(coordinator, worker, approved)
    # Re-read both inputs and both file observations before returning admission.
    context.require(starting_files(coordinator, worker, approved) == files
                    and worktree.load_binding(binding_path, binding_sha256) == binding
                    and worktree.check_binding(binding, require_clean=True) == observed
                    and handoff.verify(coordinator, handoff_ref, handoff_sha256)["handoff"] == current,
                    "handoff, binding, or starting files changed during admission")
    return {
        "schema_version": ASSIGNMENT,
        "status": "ready-for-operator-dispatch",
        "project_id": current["project_id"], "native_revision": current["native_revision"],
        "operation_id": current["operation_id"], "plan_sha256": current["plan_sha256"],
        "receipt_sha256": current["receipt_sha256"], "ticket": current["ticket"],
        "requirement_ids": [item["id"] for item in current["requirements"]],
        "projection": current["projection"],
        "coordinator": str(coordinator),
        "handoff": {"path": handoff_ref, "sha256": handoff_sha256},
        "worktree_binding": {"path": str(binding_path), "sha256": binding_sha256},
        "worker": {"path": str(worker), "branch": binding["branch"], "base": binding["base"],
                   "git_common_dir": binding["git_common_dir"], "starting_files": files},
        "coordinator_return": {"root": str(coordinator), "path": current["return_path"]},
        "operator_authority_authenticated": current["operator_authority_authenticated"],
        "reservation_verified": False, "process_permissions_enforced": False,
        "execution_observed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--handoff", required=True, help="coordinator-relative handoff file")
    parser.add_argument("--handoff-sha256", required=True)
    parser.add_argument("--binding", type=Path, required=True, help="absolute saved worktree binding")
    parser.add_argument("--binding-sha256", required=True)
    args = parser.parse_args()
    try:
        result = assign(args.root, args.handoff, args.handoff_sha256,
                        args.binding, args.binding_sha256)
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as error:
        print(json.dumps({"status": "worktree-assignment-refused", "error": str(error)}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
