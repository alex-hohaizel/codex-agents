#!/usr/bin/env python3
"""Prepare or recheck a Builder handoff for a ready, applied project ticket."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import unicodedata

sys.dont_write_bytecode = True
import ticket_replan_store as store
import ticket_tree as tree

context = tree.context
HANDOFF = "atelier.ticket-builder-handoff/1"
RETURN = "atelier.ticket-builder-return/1"


def git_identity(root):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
            capture_output=True, text=True, env=env, timeout=10, check=True,
        )
    except (subprocess.SubprocessError, OSError) as error:
        raise context.ContextError("a committed, accessible Git worktree is required") from error
    lines = result.stdout.splitlines()
    context.require(len(lines) == 2 and lines[0] == str(root)
                    and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", lines[1]),
                    "Git worktree must match the canonical project root")
    return {"project_root": str(root), "head": lines[1]}


def scoped_file(root, ref):
    path = context.local(root, ref, existing=False)
    parts = PurePosixPath(ref).parts
    protected_parts = context.PRIVATE_PARTS | {
        ".agents", ".codex", "agents.md", ".ticket-dispatch.json", ".ticket-replan.lock",
    }
    context.require(parts and not any(
        part.casefold() in protected_parts or context.PRIVATE_NAME.fullmatch(part) for part in parts
    ), f"protected write path: {ref}")
    context.require(path.parent.is_dir(), f"expected an existing project directory: {ref}")
    if path.exists():
        info = path.lstat()
        context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                        f"writable path must be a regular file without hard links: {ref}")
    return path


def comparable_path(ref):
    return PurePosixPath(unicodedata.normalize("NFD", ref).casefold())


def overlaps(first, second):
    left, right = comparable_path(first), comparable_path(second)
    return left == right or left in right.parents or right in left.parents


def receipt_scope(result, board, ticket_id):
    receipt = result["receipt"]
    context.require(result["status"] == "verified" and result["verified_readback"]
                    and result["projection"] == board["projection"]
                    and board["native_revision"] == receipt["target_revision"]
                    and board["project_id"] == receipt["project_id"],
                    "the approved replan receipt is historical or its target changed")
    scope = set(receipt["created_ticket_ids"]) | set(receipt["changed_ticket_ids"])
    context.require(ticket_id in scope, "ticket was outside the applied replan")
    ticket = next((row for row in board["tickets"] if row["id"] == ticket_id), None)
    context.require(ticket is not None and ticket["board_state"] == "ready"
                    and ticket["kind"] not in tree.GROUPS and ticket["acceptance"],
                    "ticket is not ready for Builder")
    return receipt, ticket


def bound_replan_sources(snapshot, receipt):
    request = None
    sources = {}
    for field in ("request", "decision"):
        pin = receipt[field]
        raw = snapshot.read(pin["path"])
        context.require(context.digest(raw) == pin["sha256"], f"applied replan {field} changed")
        if field == "request":
            request = context.json_object(raw)
        sources[pin["path"]] = pin["sha256"]
    if request.get("schema_version") == "atelier.ticket-replan-correction-request/1":
        citations = [request["baseline"], request["no_dispatch"]]
    else:
        changes = request.get("changes")
        context.require(isinstance(changes, list) and changes,
                        "handoff requires a replan with directly reviewable source citations")
        citations = [source for change in changes for source in change["sources"]]
    for citation in citations:
        path, expected = citation["path"], citation["sha256"]
        context.require(context.digest(snapshot.read(path)) == expected,
                        f"applied replan source changed: {path}")
        sources[path] = expected
    return sources


def prepare(root, projection, operation_id, plan_sha256, ticket_id, write_paths, return_path,
            *, returning=False):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    git = git_identity(root)
    result = store.read_receipt(root, projection, operation_id, plan_sha256)
    snapshot = tree.Snapshot(root)
    board = tree.project_board(root, projection, snapshot=snapshot)
    receipt, ticket = receipt_scope(result, board, ticket_id)
    replan_sources = bound_replan_sources(snapshot, receipt)
    protected = {projection, *board["requirement_sources"], *replan_sources}
    for row in board["tickets"]:
        for evidence in row["evidence"]:
            protected.add(evidence["path"])
            if "subject" in evidence:
                protected.add(evidence["subject"]["path"])
            elif (evidence.get("kind") == "acceptance-receipt"
                  and evidence["status"] == "binding-mismatch"):
                # The board does not inspect a prior revision's subject after a binding
                # mismatch. Its declared path remains part of the protected project history.
                raw = snapshot.read(evidence["path"])
                record = tree.acceptance_record(raw)
                if record and isinstance(record.get("subject"), dict):
                    path = record["subject"].get("path")
                    if isinstance(path, str) and path:
                        protected.add(path)

    supplied_paths = context.string_list(write_paths, "write paths")
    context.require(1 <= len(supplied_paths) <= 24, "name 1 to 24 exact writable product files")
    writes = []
    for ref in sorted(supplied_paths):
        context.require(not any(overlaps(ref, item["path"]) for item in writes),
                        f"write path aliases another scoped file: {ref}")
        path = scoped_file(root, ref)
        context.require(not any(overlaps(ref, item) for item in protected),
                        f"write path overlaps a project record: {ref}")
        writes.append({"path": ref, "sha256": context.digest(snapshot.read(ref))
                       if path.exists() else None})
    output = scoped_file(root, return_path)
    context.require((returning or not output.exists()) and not any(
        overlaps(return_path, item) for item in {*protected, *supplied_paths}
    ), "return path must be new and separate from inputs and implementation")
    requirements = tree.read_requirements(snapshot, board["requirement_sources"])
    selected_sources = [
        {key: requirements[identifier][key] for key in (
            "id", "source_ref", "source_sha256", "verbatim", "acceptance",
        )} for identifier in ticket["requirement_closure"]
    ]
    snapshot.verify_unchanged()
    context.require(git_identity(root) == git, "Git HEAD changed while preparing the handoff")
    context.require(all(item["sha256"] is not None or not scoped_file(root, item["path"]).exists()
                        for item in writes) and (returning or not scoped_file(root, return_path).exists()),
                    "a previously absent output appeared during preparation")
    return {
        "schema_version": HANDOFF,
        "status": "ready-for-operator-handoff",
        "project_id": board["project_id"], "native_revision": board["native_revision"],
        "projection": board["projection"], "git": git,
        "operation_id": operation_id, "plan_sha256": plan_sha256,
        "receipt_sha256": context.digest(context.canonical(receipt)),
        "ticket": {key: ticket[key] for key in (
            "id", "kind", "title", "acceptance", "effective_prerequisites",
        )},
        "requirements": selected_sources,
        "replan_sources": replan_sources,
        "write_paths": writes, "return_path": return_path,
        "operator_authority_authenticated": False,
        "process_permissions_enforced": False,
        "execution_observed": False,
    }


def verified_inputs(root, name, expected, *, returning=False):
    context.require(context.HASH.fullmatch(expected) is not None, "invalid handoff SHA-256")
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    raw = context.bound_bytes(root, name)
    context.require(context.digest(raw) == expected, "handoff changed")
    handoff = context.json_object(raw)
    context.require(handoff.get("schema_version") == HANDOFF, "unsupported handoff schema")
    try:
        paths = [item["path"] for item in handoff["write_paths"]]
        context.require(not any(overlaps(name, path) for path in [*paths, handoff["return_path"]]),
                        "handoff overlaps writable paths")
        current = prepare(root, handoff["projection"]["path"], handoff["operation_id"],
                          handoff["plan_sha256"], handoff["ticket"]["id"], paths,
                          handoff["return_path"], returning=returning)
    except (KeyError, TypeError) as error:
        raise context.ContextError("invalid handoff structure") from error
    admission = {**current, "write_paths": handoff["write_paths"]} if returning else current
    context.require(admission == handoff and context.bound_bytes(root, name) == raw,
                    "handoff is stale; reconcile project, permission and Builder inputs")
    return handoff, current


def verify(root, name, expected):
    _, current = verified_inputs(root, name, expected)
    return {"status": "verified-at-admission", "handoff_sha256": expected, "handoff": current}


def verify_result(root, name, expected):
    handoff, current = verified_inputs(root, name, expected, returning=True)
    path = handoff["return_path"]
    raw = context.bound_bytes(root, path)
    result = context.json_object(raw)
    binding = {
        "schema_version": RETURN, "handoff_sha256": expected,
        "ticket_id": handoff["ticket"]["id"], "status": "changes-prepared",
    }
    context.require(set(result) == {*binding, "artifacts", "checks"} and all(
        result[key] == value for key, value in binding.items()
    ), "Builder return is not bound to this handoff")
    context.require(isinstance(result["checks"], list) and result["checks"],
                    "Builder return needs reported checks")
    original = {item["path"]: item["sha256"] for item in handoff["write_paths"]}
    observed = {item["path"]: item["sha256"] for item in current["write_paths"]
                if original[item["path"]] != item["sha256"]}
    artifacts = tree.pins(result["artifacts"])
    context.require(artifacts and artifacts == observed,
                    "Builder return differs from the observed changes in scoped files")
    _, confirmed = verified_inputs(root, name, expected, returning=True)
    context.require(confirmed == current, "Builder inputs or outputs changed during readback")
    context.require(context.bound_bytes(root, path) == raw
                    and all(context.digest(context.bound_bytes(root, ref)) == digest
                            for ref, digest in artifacts.items()),
                    "Builder return or its artifacts drifted during readback")
    return {
        "status": "returned-artifacts-verified",
        "handoff_sha256": expected,
        "return": {"path": path, "sha256": context.digest(raw)},
        "artifacts": artifacts, "reported_checks": result["checks"],
        "functional_outcome_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    make = modes.add_parser("prepare")
    check = modes.add_parser("verify")
    returned = modes.add_parser("verify-result")
    for mode in (make, check, returned):
        mode.add_argument("--root", type=Path, required=True)
    for field in ("projection", "operation-id", "plan-sha256", "ticket", "return-path"):
        make.add_argument("--" + field, required=True)
    make.add_argument("--write-path", action="append", required=True)
    for mode in (check, returned):
        mode.add_argument("--handoff", required=True)
        mode.add_argument("--handoff-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.mode == "prepare":
            result = prepare(args.root, args.projection, args.operation_id, args.plan_sha256,
                             args.ticket, args.write_path, args.return_path)
        elif args.mode == "verify":
            result = verify(args.root, args.handoff, args.handoff_sha256)
        else:
            result = verify_result(args.root, args.handoff, args.handoff_sha256)
    except (context.ContextError, OSError) as error:
        print(json.dumps({"status": "invalid-handoff", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
