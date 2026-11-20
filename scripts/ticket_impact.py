#!/usr/bin/env python3
"""Capture a source-bound ticket tree and report the impact between two captures."""

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree
import production_choices as choices

context = tree.context
SNAPSHOT = "atelier.ticket-impact-snapshot/1"
REPORT = "atelier.ticket-impact/1"
MAX_SNAPSHOT_BYTES = 32 * 1024 * 1024
PLAN_FIELDS = ("kind", "title", "parent", "depends_on", "requirement_ids", "criterion_sha256")
CHECK_STATES = {
    "verified", "unavailable", "stale", "binding-mismatch", "invalid-subject",
    "subject-unavailable", "subject-stale",
}
CHOICE_PHASES = {"implement", "scale", "accept"}
CHOICE_STATES = {"verified", "invalid-binding", "record-unavailable", "record-stale",
                 "decision-stale", "invalid-or-stale"}


@dataclass
class TicketGraph:
    requirements: dict
    tickets: dict
    closures: dict
    children: dict
    prerequisites: dict
    ancestor_blockers: dict
    retirements: dict


def capture(root, name):
    source = tree.Snapshot(root)
    board = tree.project_board(root, name, snapshot=source)
    requirements = tree.read_requirements(source, board["requirement_sources"])
    tickets = []
    for ticket in board["tickets"]:
        row = {field: ticket[field] for field in (
            "id", "kind", "title", "parent", "depends_on", "requirement_ids", "recorded_status",
            "blocked_reason", "acceptance_status", "evidence",
        )}
        criterion = ticket["acceptance"]
        row["criterion_sha256"] = context.digest(criterion.encode("utf-8")) if criterion else None
        tickets.append(row)
    result = {
        "schema_version": SNAPSHOT,
        "project_id": board["project_id"],
        "native_revision": board["native_revision"],
        "projection": board["projection"],
        "requirement_sources": board["requirement_sources"],
        "requirements": [
            {
                "id": key, "source_ref": row["source_ref"], "applicable": row["applicable"],
                "dependencies": sorted(row["dependencies"]),
                "record_sha256": context.digest(context.canonical(row["raw_native_record"])),
            }
            for key, row in requirements.items()
        ],
        "tickets": tickets,
    }
    retirements = [row["replan_retirement"] for row in board["tickets"] if "replan_retirement" in row]
    if retirements:
        result["replan_retirements"] = retirements
    choice = capture_choice(source, context.json_object(source.read(name)), requirements)
    if choice is not None:
        result["production_choice"] = choice
    source.verify_unchanged()
    return result


def is_hash(value):
    return isinstance(value, str) and context.HASH.fullmatch(value) is not None


def choice_binding(binding, requirements):
    context.require(isinstance(binding, dict) and set(binding) == {
        "record", "decision_sha256", "requirement_ids", "phase",
    }, "production choice binding needs record, decision_sha256, requirement_ids and phase")
    tree.pins([binding["record"]])
    context.require(is_hash(binding["decision_sha256"]), "invalid production decision SHA-256")
    phase = context.text(binding, "phase")
    context.require(phase in CHOICE_PHASES, "unsupported production choice phase")
    requirement_ids = context.bounded_ids(binding["requirement_ids"], "production choice requirements")
    context.require(requirement_ids and all(
        key in requirements and requirements[key]["applicable"] for key in requirement_ids
    ), "production choice binding needs explicit, applicable native requirement IDs")
    return {**binding, "requirement_ids": sorted(requirement_ids)}


def capture_choice(source, projection, requirements):
    binding = None
    if "production_choice" in projection:
        try:
            binding = choice_binding(projection["production_choice"], requirements)
        except context.ContextError as error:
            return {"status": "invalid-binding", "binding": None, "issue": str(error)}
    else:
        default = source.root / choices.DEFAULT_RECORD
        if not default.exists() and not default.is_symlink():
            return None
    path = binding["record"]["path"] if binding else choices.DEFAULT_RECORD
    phase = binding["phase"] if binding else "implement"
    result = {"binding": binding, "path": path, "phase": phase}
    try:
        record_sha = context.digest(source.read(path))
    except (context.ContextError, OSError) as error:
        return {**result, "status": "record-unavailable", "issue": str(error)}
    result["record_sha256"] = record_sha
    if binding and binding["record"]["sha256"] != record_sha:
        return {**result, "status": "record-stale", "issue": "The production choice record changed."}
    try:
        observed = choices.verify_project(source.root, phase, record=path, expected_sha256=record_sha)
    except choices.ChoiceError as error:
        return {**result, "status": "invalid-or-stale", "issue": str(error)}
    for field in ("record_id", "revision", "decision_sha256", "configuration_artifacts", "evidence_artifacts"):
        result[field] = observed[field]
    if binding and binding["decision_sha256"] != observed["decision_sha256"]:
        return {**result, "status": "decision-stale", "issue": "The approved decision differs from the projection pin."}
    return {**result, "status": "verified"}


def captured_choice(snapshot, graph):
    if "production_choice" not in snapshot:
        return None
    row = snapshot["production_choice"]
    context.require(isinstance(row, dict) and context.text(row, "status") in CHOICE_STATES
                    and "binding" in row, "invalid captured production choice")
    if row["binding"] is not None:
        choice_binding(row["binding"], graph.requirements)
    return row


def compare_choice(before, after, old_graph, new_graph):
    old, new = captured_choice(before, old_graph), captured_choice(after, new_graph)
    if old is None and new is None:
        return None, set()
    old_binding = old["binding"] if old else None
    new_binding = new["binding"] if new else None
    if new is None:
        change = "removed"
    elif old is None:
        change = "added"
    elif old_binding and not new_binding:
        change = "binding-removed"
    elif old != new:
        change = "changed"
    else:
        change = "unchanged"
    review = change != "unchanged" or new["status"] != "verified"
    exact_ids = {key for binding in (old_binding, new_binding) if binding for key in binding["requirement_ids"]}
    return {
        "before": old, "after": new, "change": change, "requires_review": review,
        "explicit_requirement_ids": sorted(exact_ids),
        "relationship_scope": "explicit native requirement IDs and declared graph dependencies",
    }, exact_ids if review else set()


def load_snapshot(path, expected):
    context.require(is_hash(expected), f"invalid expected snapshot hash: {path}")
    context.require(path.is_file() and not path.is_symlink(), f"missing/linked snapshot: {path}")
    with path.open("rb") as stream:
        raw = stream.read(MAX_SNAPSHOT_BYTES + 1)
    context.require(len(raw) <= MAX_SNAPSHOT_BYTES, f"snapshot exceeds 32 MiB: {path}")
    context.require(context.digest(raw) == expected, f"SNAPSHOT_DRIFT: {path}")
    return context.json_object(raw)


def validate_evidence(rows):
    context.require(isinstance(rows, list), "snapshot ticket evidence must be an array")
    for check in rows:
        context.require(isinstance(check, dict) and isinstance(check.get("status"), str)
                        and check["status"] in CHECK_STATES, "invalid snapshot evidence state")
        context.require(set(check) <= {"path", "sha256", "kind", "status", "subject"},
                        "unexpected snapshot evidence field")
        if "subject" in check:
            tree.pins([check["subject"]])
    tree.pins([{key: check.get(key) for key in ("path", "sha256")} for check in rows])


def read_graph(snapshot):
    context.require(snapshot.get("schema_version") == SNAPSHOT, "unsupported impact snapshot")
    context.text(snapshot, "project_id")
    context.text(snapshot, "native_revision")
    projection = tree.pins([snapshot.get("projection")])
    pins = snapshot.get("requirement_sources")
    context.require(isinstance(pins, dict) and len(pins) and not projection.keys() & pins.keys(),
                    "missing separate requirement source pins")
    tree.pins([{"path": path, "sha256": sha} for path, sha in pins.items()])
    requirements = context.records(snapshot, "requirements")
    tickets = context.records(snapshot, "tickets")
    context.require(1 <= len(requirements) <= context.MAX_IDS, "invalid snapshot requirement count")
    context.require(1 <= len(tickets) <= context.MAX_IDS, "invalid snapshot ticket count")
    requirement_graph = {}
    for key, row in requirements.items():
        context.require(is_hash(row.get("record_sha256")) and type(row.get("applicable")) is bool
                        and context.text(row, "source_ref") in pins,
                        f"invalid snapshot requirement: {key}")
        deps = context.bounded_ids(row.get("dependencies"), "requirement dependencies")
        context.require(all(dep in requirements for dep in deps), f"unknown requirement dependency: {key}")
        requirement_graph[key] = deps
    tree.evaluation_order(requirement_graph, "cyclic snapshot requirement dependencies")
    closures = {}
    for key, ticket in tickets.items():
        kind = context.text(ticket, "kind")
        parent = ticket.get("parent")
        context.require(parent is None or isinstance(parent, str) and parent in tickets,
                        f"unknown snapshot parent: {key}")
        parent_kind = context.text(tickets[parent], "kind") if parent is not None else None
        context.require(kind in tree.PARENTS and parent_kind in tree.PARENTS[kind],
                        f"invalid snapshot parent kind: {key}")
        context.text(ticket, "title")
        context.require(context.text(ticket, "recorded_status") in tree.STATUSES
                        and context.text(ticket, "acceptance_status") in {
                            "not-recorded", "supported", "unsupported",
                        }, f"invalid snapshot ticket status: {key}")
        criterion = ticket.get("criterion_sha256")
        context.require(criterion is None or is_hash(criterion), f"invalid snapshot criterion: {key}")
        context.require(ticket.get("blocked_reason") is None or isinstance(ticket["blocked_reason"], str),
                        f"invalid snapshot blocking reason: {key}")
        dependencies = context.bounded_ids(ticket.get("depends_on"), "ticket prerequisites")
        context.require(all(dep in tickets for dep in dependencies), f"unknown ticket dependency: {key}")
        assigned = context.bounded_ids(ticket.get("requirement_ids"), "ticket requirement IDs")
        closures[key] = set(tree.requirement_closure(assigned, requirements, key))
        validate_evidence(ticket.get("evidence"))
        context.require(all(field in ticket for field in (*PLAN_FIELDS, "blocked_reason")),
                        f"incomplete snapshot ticket: {key}")
    retirements = tree.replan_retirements(snapshot, tickets)
    children, prerequisites, ancestor_blockers, _ = tree.ticket_graph(tickets, retired=retirements)
    completion = {key: [child for child in children[key] if child not in retirements] for key in tickets}
    return TicketGraph(requirements, tickets, closures, completion, prerequisites, ancestor_blockers,
                       retirements)


def requirement_changes(before, after):
    changes = []
    for key in sorted(before.keys() | after.keys()):
        old, new = before.get(key), after.get(key)
        if old is None or new is None:
            kind = "added" if old is None else "removed"
        elif old["record_sha256"] != new["record_sha256"]:
            kind = "changed"
        elif old["source_ref"] != new["source_ref"]:
            kind = "source-moved"
        else:
            continue
        changes.append({"id": key, "change": kind, "before": old, "after": new})
    return changes


def source_drift(before, after):
    changes = []
    for path in sorted(before.keys() | after.keys()):
        old, new = before.get(path), after.get(path)
        if old != new:
            changed = "added" if old is None else ("removed" if new is None else "changed")
            changes.append({"path": path, "change": changed, "before_sha256": old, "after_sha256": new})
    return changes


def ancestor_path(tickets, key):
    path = []
    parent = tickets[key]["parent"]
    while parent is not None:
        path.append(parent)
        parent = tickets[parent]["parent"]
    return path


def inherited_changes(before, after, key):
    prerequisites = set(before.prerequisites[key]) ^ set(after.prerequisites[key])
    yield from (("effective-prerequisite-changed", dep) for dep in prerequisites)
    yield from (("requirement-closure-changed", requirement)
                for requirement in before.closures[key] ^ after.closures[key])
    old_holds = {hold["ticket"]: hold for hold in before.ancestor_blockers[key]}
    new_holds = {hold["ticket"]: hold for hold in after.ancestor_blockers[key]}
    yield from (("ancestor-hold-changed", group) for group in old_holds.keys() | new_holds.keys()
                if old_holds.get(group) != new_holds.get(group))
    old_path, new_path = ancestor_path(before.tickets, key), ancestor_path(after.tickets, key)
    if old_path != new_path:
        old_groups, new_groups = set(old_path), set(new_path)
        yield from (("ancestor-path-changed", group) for group in (old_groups ^ new_groups) or old_groups)


def record_impact(old_graph, new_graph, changed_requirements, choice_requirements=()):
    before, after = old_graph.tickets, new_graph.tickets
    reasons, downstream = defaultdict(set), defaultdict(set)
    structural = {}
    for key in sorted(before.keys() | after.keys()):
        old, new = before.get(key), after.get(key)
        if old is None or new is None:
            kind = "added" if old is None else "removed"
            structural[key] = {"change": kind, "fields": []}
            reasons[key].add(("ticket-" + kind, key))
        else:
            fields = [field for field in PLAN_FIELDS if old[field] != new[field]]
            if fields:
                structural[key] = {"change": "changed", "fields": fields}
                reasons[key].add(("ticket-plan-changed", key))
            for reason in inherited_changes(old_graph, new_graph, key):
                reasons[key].add(reason)
        prior_retirement = old_graph.retirements.get(key)
        current_retirement = new_graph.retirements.get(key)
        if prior_retirement != current_retirement:
            change = structural.setdefault(key, {"change": "changed", "fields": []})
            change["fields"].append("replan_retirement")
            change["retirement"] = {"before": prior_retirement, "after": current_retirement}
            reasons[key].add(("ticket-retirement-changed", key))

    choice_requirements = set(choice_requirements)
    reviewed_requirements = changed_requirements | choice_requirements
    for graph in (old_graph, new_graph):
        for key, ticket in graph.tickets.items():
            assigned = set(ticket["requirement_ids"])
            hits = reviewed_requirements & graph.closures[key]
            for requirement in hits:
                kind = "direct-requirement" if requirement in assigned else "requirement-prerequisite"
                if requirement in changed_requirements:
                    reasons[key].add((kind, requirement))
                if requirement in choice_requirements:
                    reasons[key].add(("production-choice-" + kind, requirement))
            for dep in graph.prerequisites[key]:
                downstream[dep].add(("ticket-prerequisite", key))
            for child in graph.children[key]:
                downstream[child].add(("group-member", key))
            group_contract_changes = {"criterion_sha256", "requirement_ids"}
            group_fields = structural.get(key, {}).get("fields", [])
            if graph.children[key] and (hits or group_contract_changes.intersection(group_fields)):
                pending = list(graph.children[key])
                while pending:
                    member = pending.pop()
                    reasons[member].add(("group-contract", key))
                    pending.extend(graph.children[member])

    pending = deque(sorted(reasons))
    while pending:
        key = pending.popleft()
        for kind, dependent in sorted(downstream[key]):
            if dependent not in reasons:
                pending.append(dependent)
            reasons[dependent].add((kind, key))
    return reasons, structural


def evidence_reviews(old_ticket, new_ticket):
    current = {row["path"]: row for row in new_ticket.get("evidence", [])}
    reviews = []
    for historical in old_ticket.get("evidence", []):
        now = current.get(historical["path"])
        if now is None:
            relation = "absent"
        elif historical["sha256"] != now["sha256"]:
            relation = "replacement"
        else:
            relation = "same-declared-pin"
        reviews.append({
            "prior": historical, "current": now,
            "current_relation": relation, "disposition": "review-required",
        })
    return reviews


def compare(before, after, before_sha256, after_sha256):
    old_graph = read_graph(before)
    new_graph = read_graph(after)
    context.require(before["project_id"] == after["project_id"], "snapshot project mismatch")
    old_tickets, new_tickets = old_graph.tickets, new_graph.tickets
    changes = requirement_changes(old_graph.requirements, new_graph.requirements)
    drift = source_drift(before["requirement_sources"], after["requirement_sources"])
    choice_change, choice_requirements = compare_choice(before, after, old_graph, new_graph)
    reasons, structure = record_impact(old_graph, new_graph, {change["id"] for change in changes},
                                      choice_requirements)
    affected = []
    for key, why in sorted(reasons.items()):
        old, new = old_tickets.get(key, {}), new_tickets.get(key, {})
        affected.append({
            "ticket_id": key,
            "reasons": [{"code": code, "id": ident} for code, ident in sorted(why)],
            "plan_change": structure.get(key),
            "prior_recorded_status": old.get("recorded_status"),
            "prior_acceptance_status": old.get("acceptance_status"),
            "current_recorded_status": new.get("recorded_status"),
            "prior_evidence_requiring_review": evidence_reviews(old, new),
            "review_prior_acceptance": old.get("recorded_status") == "accepted",
        })
    revisions = {}
    for label, snapshot, sha in (("before", before, before_sha256), ("after", after, after_sha256)):
        revisions[label] = {
            "native_revision": snapshot["native_revision"],
            "snapshot_sha256": sha,
            "projection": snapshot["projection"],
        }
    return {
        "schema_version": REPORT,
        "project_id": before["project_id"],
        **revisions,
        "native_revision_reused_with_source_changes": (
            before["native_revision"] == after["native_revision"]
            and (bool(drift) or before["projection"] != after["projection"]
                 or bool(choice_change and choice_change["change"] != "unchanged"))
        ),
        **({"production_choice_change": choice_change} if choice_change is not None else {}),
        "requirement_changes": changes,
        "requirement_source_drift": drift,
        "affected_tickets": affected,
        "other_ticket_ids": sorted(new_tickets.keys() - reasons.keys()),
        "current_evidence_warnings": [
            {"ticket_id": key, **check}
            for key, ticket in sorted(new_tickets.items()) for check in ticket["evidence"]
            if check["status"] != "verified"
        ],
        "current_unsupported_acceptance_claims": sorted(
            key for key, ticket in new_tickets.items() if ticket["acceptance_status"] == "unsupported"
        ),
        "scope": "declared-ticket-tree-and-linked-evidence",
        "authority_authenticated": False,
        "source_completeness_authenticated": False,
        "functional_outcome_verified": False,
        "acceptance_reissued": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    capture_args = commands.add_parser("capture", help="emit a source-checked snapshot")
    capture_args.add_argument("--root", type=Path, required=True)
    capture_args.add_argument("--input", required=True, help="projection path relative to the root")
    compare_args = commands.add_parser("compare", help="compare two independently retained snapshots")
    for label in ("before", "after"):
        compare_args.add_argument("--" + label, type=Path, required=True)
        compare_args.add_argument("--" + label + "-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.operation == "capture":
            result = capture(args.root, args.input)
        else:
            before = load_snapshot(args.before, args.before_sha256)
            after = load_snapshot(args.after, args.after_sha256)
            result = compare(before, after, args.before_sha256, args.after_sha256)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.operation == "capture":
            context.require(len(output.encode("utf-8")) + 1 <= MAX_SNAPSHOT_BYTES,
                            "snapshot exceeds 32 MiB")
    except (context.ContextError, OSError, UnicodeError, RecursionError) as error:
        print(json.dumps({"status": "invalid-" + args.operation, "error": str(error)}), file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
