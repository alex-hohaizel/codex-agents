#!/usr/bin/env python3
"""Preview a new authorized revision that corrects an unstarted, landed replan."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_replan_plan as model
import ticket_replan_store as store

context, tree = model.context, model.tree
REQUEST = "atelier.ticket-replan-correction-request/1"
NO_DISPATCH = "atelier.ticket-replan-no-dispatch/1"
CORRECTIONS = "replan_corrections"
RETIREMENTS = "replan_retirements"


def checked_source(snapshot, pin):
    source = snapshot.read(pin["path"])
    context.require(context.digest(source) == pin["sha256"], f"correction source changed: {pin['path']}")
    return source


def read_request(snapshot, board, name):
    raw = snapshot.read(name)
    request = context.json_object(raw)
    expected = {
        "schema_version": REQUEST,
        "project_id": board["project_id"],
        "native_revision": board["native_revision"],
        "projection_sha256": board["projection"]["sha256"],
    }
    context.require(set(request) == {*expected, "target_revision", "undo_operation_id", "undo_plan_sha256",
                                    "baseline", "no_dispatch", "rationale"}, "invalid correction request fields")
    context.require(all(request[key] == value for key, value in expected.items()),
                    "correction baseline mismatch: use the exact landed projection")
    revision = store.checked_identifier(request, "target_revision")
    context.require(revision != board["native_revision"], "correction requires a new revision")
    store.checked_identifier(request, "undo_operation_id")
    store.check_digest(request["undo_plan_sha256"], "original plan")
    context.text(request, "rationale")
    pin = {"path": name, "sha256": context.digest(raw)}
    tree.pins([board["projection"], pin, request["baseline"], request["no_dispatch"]])
    return request, pin


def check_no_dispatch(snapshot, pin, readback):
    row = context.json_object(checked_source(snapshot, pin))
    receipt = readback["receipt"]
    expected = {
        "schema_version": NO_DISPATCH,
        "status": "no-dispatch-observed",
        "project_id": receipt["project_id"],
        "native_revision": readback["native_revision"],
        "operation_id": receipt["operation_id"],
        "projection": readback["projection"],
        "plan_sha256": receipt["plan_sha256"],
    }
    context.require(set(row) == {*expected, "authority_ref"}
                    and all(row[key] == value for key, value in expected.items()),
                    "expected an operator's reconciled no-dispatch record for the exact landed operation")
    context.text(row, "authority_ref")


def restore_rows(baseline, current, receipt, revision):
    old = context.records(baseline, "tickets")
    active = context.records(current, "tickets")
    context.require(old.keys() <= active.keys(), "landed replan removed a baseline ticket")
    created = sorted(active.keys() - old.keys())
    changed = sorted(key for key in old if old[key] != active[key])
    context.require(created == receipt["created_ticket_ids"] and changed == receipt["changed_ticket_ids"],
                    "landed ticket fields no longer match the recorded replan scope")
    for key in changed:
        context.require(old[key]["kind"] not in tree.GROUPS and old[key]["status"] == "planned"
                        and active[key]["status"] in {"planned", "deferred"},
                        f"correction requires planned leaf history: {key}")
    for key in created:
        row = active[key]
        context.require(row["kind"] not in tree.GROUPS and row["status"] == "planned"
                        and not row.get("evidence") and not row.get("blocked_reason"),
                        f"correction requires an unstarted introduced leaf: {key}")
    return (
        [*deepcopy(list(old.values())), *[{**active[key], "status": "deferred"} for key in created]],
        [*deepcopy(baseline.get(RETIREMENTS, [])), *[
            {"ticket_id": key, "action": "drop", "retired_in": revision, "successors": []}
            for key in created
        ]],
    )


def build_correction(root, projection_name, request_name):
    snapshot, current_board, current, requirements = model.refine.load_plan(root, projection_name)
    request, request_pin = read_request(snapshot, current_board, request_name)
    readback = store.read_receipt(root, projection_name, request["undo_operation_id"], request["undo_plan_sha256"])
    context.require(readback["verified_readback"] and readback["projection"] == current_board["projection"],
                    "correction requires the current verified and unchanged landed replan")
    receipt = readback["receipt"]
    baseline_pin = request["baseline"]
    context.require(baseline_pin["sha256"] == receipt["projection"]["sha256"],
                    "archived baseline does not match the original replan receipt")
    archived_raw = checked_source(snapshot, baseline_pin)
    check_no_dispatch(snapshot, request["no_dispatch"], readback)
    baseline = context.json_object(archived_raw)
    context.require(baseline.get("project_id") == current["project_id"]
                    and baseline.get("native_revision") == receipt["native_revision"]
                    and baseline.get("requirement_sources") == current.get("requirement_sources")
                    and baseline.get(store.HISTORY, []) == current[store.HISTORY][:-1],
                    "archived projection has a different project, revision, sources or receipt history")
    corrections = current.get(CORRECTIONS, [])
    context.require(isinstance(corrections, list) and all(isinstance(item, dict) for item in corrections),
                    "invalid prior correction history")
    context.require(not any(item.get("target_revision") == current["native_revision"] for item in corrections),
                    "correcting a correction requires a separately designed replan")
    previous_board = tree.project_board(root, projection_name, snapshot=model.TargetSnapshot(
        snapshot, projection_name, archived_raw
    ))
    revision = request["target_revision"]
    rows, retirements = restore_rows(baseline, current, receipt, revision)
    lineage = {
        "corrects_operation_id": receipt["operation_id"],
        "original_receipt_sha256": store.plan_sha256(receipt),
        "baseline": baseline_pin,
        "no_dispatch": request["no_dispatch"],
        "target_revision": revision,
        "rationale": request["rationale"],
    }
    target = {**deepcopy(current), "native_revision": revision, "tickets": rows,
              RETIREMENTS: retirements, CORRECTIONS: [*corrections, lineage]}
    prospective = tree.project_board(root, projection_name, snapshot=model.TargetSnapshot(
        snapshot, projection_name, context.canonical(target)
    ))
    coverage = model.compare_coverage(previous_board, prospective, requirements)
    snapshot.verify_unchanged()
    return {
        "schema_version": model.PLAN,
        "project_id": current["project_id"],
        "native_revision": current["native_revision"],
        "target_revision": revision,
        "projection": current_board["projection"],
        "request": request_pin,
        "requirement_sources": current_board["requirement_sources"],
        "target": target,
        "correction": {**lineage, "restored_ticket_ids": receipt["changed_ticket_ids"],
                       "retired_ticket_ids": receipt["created_ticket_ids"]},
        "coverage": coverage,
        "readiness": model.readiness(previous_board, prospective, set(receipt["changed_ticket_ids"])),
        "authority_authenticated": False,
        "no_execution_independently_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--projection", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    try:
        plan = build_correction(args.root, args.projection, args.request)
        print(json.dumps({"plan_sha256": store.plan_sha256(plan), "plan": plan}, ensure_ascii=False, indent=2))
        return 0
    except (context.ContextError, OSError, UnicodeError, RecursionError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
