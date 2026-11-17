#!/usr/bin/env python3
"""Prepare an exact sprint scope and read its current progress from the project board."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree

context = tree.context
PLAN = "atelier.sprint-plan/1"
REPORT = "atelier.sprint-progress/1"


def exact_date(value):
    context.require(isinstance(value, str), "expected a date in YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise context.ContextError("expected a date in YYYY-MM-DD") from error
    context.require(parsed.isoformat() == value, "expected a date in YYYY-MM-DD")
    return parsed


def inspect_plan(plan):
    context.require(set(plan) == {
        "schema_version", "sprint_id", "project_id", "goal", "starts_on", "ends_on",
        "scope_at", "select", "members", "member_contract_sha256", "previous",
    } and plan["schema_version"] == PLAN, "invalid sprint plan")
    for key in ("sprint_id", "project_id", "goal"):
        field = context.text(plan, key)
        context.require(len(field) <= (4096 if key == "goal" else 240) and field.strip() == field,
                        f"invalid sprint {key}")
    context.require(exact_date(plan["starts_on"]) <= exact_date(plan["ends_on"]),
                    "sprint ends before it starts")
    scope = plan["scope_at"]
    context.require(isinstance(scope, dict) and set(scope) == {"native_revision", "projection"},
                    "invalid planned source scope")
    context.text(scope, "native_revision")
    tree.pins([scope["projection"]])
    for key in ("select", "members"):
        context.require(context.bounded_ids(plan[key], key), f"sprint needs at least one {key} entry")
    pins = plan["member_contract_sha256"]
    context.require(isinstance(pins, dict) and set(pins) == set(plan["members"])
                    and all(isinstance(value, str) and context.HASH.fullmatch(value)
                            for value in pins.values()), "invalid planned member contracts")
    if plan["previous"] is not None:
        tree.pins([plan["previous"]])
    return plan


def read_plan(snapshot, name, expected, project_id):
    raw = snapshot.read(name)
    context.require(context.digest(raw) == expected, f"SOURCE_DRIFT: {name}")
    plan = inspect_plan(context.json_object(raw))
    context.require(plan["project_id"] == project_id, "sprint plan is from a different project")
    return plan


def member_contracts(board, members, snapshot):
    tickets = {row["id"]: row for row in board["tickets"]}
    requirements = tree.read_requirements(snapshot, board["requirement_sources"])
    result = {}
    for key in members:
        ticket = tickets[key]
        contract = {field: ticket[field] for field in (
            "id", "kind", "title", "acceptance", "parent", "effective_prerequisites",
        )}
        contract["requirements"] = {
            ident: requirements[ident]["raw_native_record"]
            for ident in ticket["requirement_closure"]
        }
        result[key] = context.digest(context.canonical(contract))
    return result


def propose(board, args, snapshot):
    selected = tree.select_sprint(board, args.select)
    previous = None
    if args.previous is not None:
        earlier = read_plan(snapshot, args.previous, args.previous_sha256, board["project_id"])
        context.require(args.sprint_id == earlier["sprint_id"], "previous plan names a different sprint")
        previous = {"path": args.previous, "sha256": args.previous_sha256}
    members = [row["id"] for row in selected["tickets"]]
    plan = inspect_plan({
        "schema_version": PLAN, "sprint_id": args.sprint_id, "project_id": board["project_id"],
        "goal": args.goal, "starts_on": args.starts_on, "ends_on": args.ends_on,
        "scope_at": {key: board[key] for key in ("projection", "native_revision")},
        "select": args.select, "members": members,
        "member_contract_sha256": member_contracts(board, members, snapshot),
        "previous": previous,
    })
    return plan


def current_expansion(board, selectors):
    """Describe missing selectors without replacing any previously planned member."""
    by_id = {row["id"]: row for row in board["tickets"]}
    leaves = tree.sprint_leaves(by_id, board["evaluation_order"])
    missing = [key for key in selectors if not leaves.get(key)]
    expansion = set().union(*(leaves.get(key, set()) for key in selectors))
    return by_id, expansion, missing


def progress(board, plan, name, expected, snapshot):
    tickets, expansion, unavailable = current_expansion(board, plan["select"])
    retained = [key for key in plan["members"]
                if key in tickets and tickets[key]["kind"] not in tree.GROUPS
                and not tickets[key].get("replan_retirement")]
    removed = [key for key in plan["members"] if key not in retained]
    view = tree.select_sprint(board, retained) if retained else None
    outside_original = expansion - set(plan["members"])
    relocated = [key for key in retained if key not in expansion]
    current_contracts = member_contracts(board, retained, snapshot)
    changed_contract = [key for key in retained
                        if current_contracts[key] != plan["member_contract_sha256"][key]]
    source = plan["scope_at"]
    source_flags = []
    if source["projection"]["path"] != board["projection"]["path"]:
        source_flags.append("projection-path-changed")
    if source["native_revision"] == board["native_revision"] and source["projection"] != board["projection"]:
        source_flags.append("revision-reused-for-changed-projection")
    needs_review = bool(removed or outside_original or unavailable or relocated or changed_contract or source_flags)
    return {
        "schema_version": REPORT,
        "status": "scope-review-due" if needs_review else "scope-current",
        "project_id": board["project_id"], "sprint_id": plan["sprint_id"],
        "goal": plan["goal"], "starts_on": plan["starts_on"], "ends_on": plan["ends_on"],
        "planned_revision": plan["scope_at"], "current_revision": {
            key: board[key] for key in ("projection", "native_revision")
        },
        "plan": {"path": name, "sha256": expected},
        "recorded_members": plan["members"],
        "unavailable_selectors": unavailable,
        "removed_or_retired": removed,
        "outside_current_selectors": relocated,
        "changed_member_contracts": changed_contract,
        "source_flags": source_flags,
        "new_members_for_review": [key for key in board["evaluation_order"] if key in outside_original],
        "current_view_of_recorded_members": view,
        "acceptance_authenticated": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    for command in ("plan", "status"):
        mode = modes.add_parser(command)
        mode.add_argument("--root", required=True, type=Path)
        mode.add_argument("--projection", required=True)
        if command == "plan":
            mode.add_argument("--sprint-id", required=True)
            mode.add_argument("--goal", required=True)
            mode.add_argument("--starts-on", required=True)
            mode.add_argument("--ends-on", required=True)
            mode.add_argument("--select", action="append", required=True)
            mode.add_argument("--previous")
            mode.add_argument("--previous-sha256")
        else:
            mode.add_argument("--sprint", required=True)
            mode.add_argument("--sprint-sha256", required=True)
    args = parser.parse_args()
    snapshot = tree.Snapshot(args.root)
    try:
        board = tree.project_board(args.root, args.projection, snapshot=snapshot)
        if args.mode == "plan":
            if bool(args.previous) != bool(args.previous_sha256):
                parser.error("--previous and --previous-sha256 are required together")
            result = propose(board, args, snapshot)
        else:
            plan = read_plan(snapshot, args.sprint, args.sprint_sha256, board["project_id"])
            result = progress(board, plan, args.sprint, args.sprint_sha256, snapshot)
        snapshot.verify_unchanged()
    except (OSError, context.ContextError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
