#!/usr/bin/env python3
"""Read a selected ticket projection and report its board and acceptance evidence."""

import argparse
from collections import defaultdict
import heapq
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "standards"))
import context_capsule as context

PROJECTION = "atelier.ticket-projection/1"
BOARD = "atelier.ticket-board/1"
SPRINT = "atelier.ticket-sprint/1"
ACCEPTANCE = "atelier.ticket-acceptance/1"
GROUPS = {"initiative", "epic"}
PARENTS = {
    "initiative": {None, "initiative"},
    "epic": {"initiative"},
    "story": {"initiative", "epic"},
    "bug": {None, "initiative", "epic"},
    "spike": {None, "initiative", "epic"},
}
STATUSES = {"planned", "in-progress", "in-review", "blocked", "accepted", "deferred"}
FIELDS = {
    "id", "kind", "title", "status", "parent", "depends_on", "requirement_ids",
    "acceptance", "evidence", "blocked_reason",
}


class Snapshot:
    """Keep all successfully read pins stable for the duration of the report."""

    def __init__(self, root):
        self.root = root
        self.paths = {}
        self.total_bytes = 0

    def read(self, path):
        if path not in self.paths:
            context.require(len(self.paths) < 256, "ticket projection references too many files")
            data = context.bound_bytes(self.root, path)
            self.total_bytes += len(data)
            context.require(self.total_bytes <= 64 * 1024 * 1024, "ticket inputs exceed 64 MiB")
            self.paths[path] = data
        return self.paths[path]

    def verify_unchanged(self):
        for path, data in self.paths.items():
            context.require(context.bound_bytes(self.root, path) == data,
                            f"SOURCE_DRIFT: {path}")


def pins(value):
    context.require(isinstance(value, list) and len(value) <= 40,
                    "expected up to 40 explicit file pins")
    result = {}
    for pin in value:
        context.require(isinstance(pin, dict) and set(pin) == {"path", "sha256"},
                        "file pin requires path and sha256")
        path, expected = context.text(pin, "path"), context.text(pin, "sha256")
        context.require(path not in result, f"duplicate file pin: {path}")
        context.require(context.HASH.fullmatch(expected), f"invalid SHA-256 pin: {path}")
        result[path] = expected
    return result


def read_requirements(snapshot, sources):
    requirements = {}
    for path, expected in sources.items():
        raw = snapshot.read(path)
        context.require(context.digest(raw) == expected, f"SOURCE_DRIFT: {path}")
        records = context.native_rows(
            context.json_object(raw), ("requirements", "requirement_registry", "requirement")
        )
        context.require(records is not None and len(records),
                        f"missing requirement records: {path}")
        for record in records:
            row = context.normalize_requirement(record, {"path": path, "sha256": expected})
            context.require(row["id"] not in requirements, f"duplicate requirement ID: {row['id']}")
            requirements[row["id"]] = row
        context.require(len(requirements) <= context.MAX_IDS, "too many requirement IDs")
    graph = {key: row["dependencies"] for key, row in requirements.items()}
    for key, dependencies in graph.items():
        context.require(all(dep in graph for dep in dependencies),
                        f"unknown requirement dependency: {key}")
    evaluation_order(graph, "cyclic requirement dependencies")
    return requirements


def evaluation_order(graph, cycle_error):
    """Visit prerequisites first and preserve declared order among available nodes."""
    rank = {key: order for order, key in enumerate(graph)}
    unmet = {key: len(dependencies) for key, dependencies in graph.items()}
    successors = defaultdict(list)
    ready = [(rank[key], key) for key in graph if not unmet[key]]
    heapq.heapify(ready)
    for key, dependencies in graph.items():
        for dep in dependencies:
            successors[dep].append(key)
    ordered = []
    while ready:
        _, key = heapq.heappop(ready)
        ordered.append(key)
        for successor in successors[key]:
            unmet[successor] -= 1
            if not unmet[successor]:
                heapq.heappush(ready, (rank[successor], successor))
    context.require(len(ordered) == len(graph), cycle_error)
    return ordered


def requirement_closure(assigned, requirements, ticket_id):
    chosen = set()
    pending = list(assigned)
    while pending:
        key = pending.pop()
        if key in chosen:
            continue
        context.require(key in requirements, f"unknown requirement {key} for ticket {ticket_id}")
        row = requirements[key]
        context.require(row["applicable"], f"inapplicable requirement {key} for ticket {ticket_id}")
        chosen.add(key)
        pending.extend(row["dependencies"])
    return sorted(chosen)


def normalize_tickets(projection, requirements):
    records = context.records(projection, "tickets")
    context.require(1 <= len(records) <= context.MAX_IDS, "expected a bounded nonempty ticket list")
    tickets = {}
    for key, row in records.items():
        context.require(len(key) <= 240 and key == key.strip(), f"invalid ticket ID: {key}")
        context.require(set(row) <= FIELDS, f"unexpected ticket field: {key}")
        kind, status, title = (context.text(row, name) for name in ("kind", "status", "title"))
        context.require(kind in PARENTS, f"unsupported ticket kind: {key}")
        context.require(status in STATUSES, f"unsupported recorded status: {key}")
        parent = row["parent"] if "parent" in row else None
        if parent is not None:
            context.require(isinstance(parent, str) and parent in records, f"unknown parent: {key}")
        parent_kind = context.text(records[parent], "kind") if parent is not None else None
        context.require(parent_kind in PARENTS[kind], f"invalid parent kind: {key}")
        dependencies = context.bounded_ids(row.get("depends_on", []), "depends_on")
        for dep in dependencies:
            context.require(dep in records and dep != key, f"invalid prerequisite {dep} for {key}")
        requirement_ids = context.bounded_ids(row.get("requirement_ids", []), "requirement_ids")
        description = context.text(row, "acceptance") if "acceptance" in row else None
        blocked_reason = context.text(row, "blocked_reason") if "blocked_reason" in row else None
        tickets[key] = {
            "id": key, "kind": kind, "title": title, "recorded_status": status,
            "parent": parent, "depends_on": dependencies, "requirement_ids": requirement_ids,
            "requirement_closure": requirement_closure(requirement_ids, requirements, key),
            "acceptance": description, "evidence": pins(row.get("evidence", [])),
            "blocked_reason": blocked_reason,
        }
    return tickets


def replan_retirements(projection, tickets):
    entries = projection.get("replan_retirements", [])
    context.require(isinstance(entries, list) and len(entries) <= context.MAX_IDS,
                    "expected a bounded replan retirement list")
    result = {}
    for entry in entries:
        context.require(isinstance(entry, dict) and set(entry) == {
            "ticket_id", "action", "retired_in", "successors",
        }, "invalid replan retirement fields")
        key = context.text(entry, "ticket_id")
        action = context.text(entry, "action")
        revision = context.text(entry, "retired_in")
        successors = context.bounded_ids(entry["successors"], "retirement successors")
        ticket = tickets.get(key)
        context.require(ticket and ticket["kind"] not in GROUPS
                        and ticket["recorded_status"] == "deferred" and key not in result,
                        f"retirement must identify one retained deferred leaf: {key}")
        context.require(revision == revision.strip() and len(revision) <= 240,
                        f"invalid retirement revision: {key}")
        limits = {"replace": (1, 1), "split": (2, 30), "drop": (0, 0)}
        context.require(action in limits and limits[action][0] <= len(successors) <= limits[action][1],
                        f"invalid retirement successor count: {key}")
        context.require(all(successor in tickets and successor != key
                            and tickets[successor]["kind"] not in GROUPS for successor in successors),
                        f"invalid retirement successor: {key}")
        result[key] = entry
    evaluation_order({key: [dep for dep in row["successors"] if dep in result]
                      for key, row in result.items()}, "cyclic replan retirement history")
    return result


def ticket_graph(tickets, *, retired=()):
    children = defaultdict(list)
    for key, ticket in tickets.items():
        children[ticket["parent"]].append(key)
    required = {}
    ancestor_blockers = {}
    edge_count = 0
    for key, ticket in tickets.items():
        parents = {key}
        ancestor_blockers[key] = []
        effective = dict.fromkeys(ticket["depends_on"])
        ancestor = ticket["parent"]
        while ancestor is not None:
            context.require(ancestor not in parents, f"cyclic ticket hierarchy: {key}")
            parents.add(ancestor)
            parent = tickets[ancestor]
            effective.update(dict.fromkeys(parent["depends_on"]))
            if parent["recorded_status"] == "deferred":
                ancestor_blockers[key].append({"code": "ancestor-deferred", "ticket": ancestor})
            elif parent["recorded_status"] == "blocked" or parent["blocked_reason"]:
                reason = {"code": "ancestor-blocked", "ticket": ancestor}
                if parent["blocked_reason"]:
                    reason["reason"] = parent["blocked_reason"]
                ancestor_blockers[key].append(reason)
            ancestor = parent["parent"]
        context.require(not parents.intersection(effective),
                        f"prerequisite refers to ticket or its ancestor: {key}")
        required[key] = list(effective)
        edge_count += len(effective)
        context.require(edge_count <= 40000, "too many effective prerequisites")
    graph = {
        key: list(dict.fromkeys([*required[key], *(child for child in children[key] if child not in retired)]))
        for key in tickets
    }
    order = evaluation_order(graph, "cyclic ticket dependencies or group completion")
    return children, required, ancestor_blockers, order


def acceptance_record(raw):
    if not raw.lstrip().startswith(b"{"):
        return None
    try:
        record = context.json_object(raw)
    except context.ContextError:
        return None
    return record if record.get("schema_version") == ACCEPTANCE else None


def inspect_receipt(snapshot, path, record, binding, non_evidence):
    fields = {*binding, "schema_version", "subject"}
    if set(record) != fields or any(record[key] != value for key, value in binding.items()):
        return {"kind": "acceptance-receipt", "status": "binding-mismatch"}
    try:
        subject, expected = next(iter(pins([record["subject"]]).items()))
        context.require(subject not in {path, *non_evidence}
                        and expected not in non_evidence.values(), "subject is a source")
    except context.ContextError:
        return {"kind": "acceptance-receipt", "status": "invalid-subject"}
    result = {"kind": "acceptance-receipt", "subject": {"path": subject, "sha256": expected}}
    try:
        raw = snapshot.read(subject)
    except (OSError, context.ContextError):
        return {**result, "status": "subject-unavailable"}
    if context.digest(raw) != expected:
        return {**result, "status": "subject-stale"}
    if acceptance_record(raw) is not None:
        return {**result, "status": "invalid-subject"}
    return {**result, "status": "verified"}


def inspect_evidence(snapshot, ticket, identity, non_evidence):
    binding = {
        **identity,
        "ticket_id": ticket["id"],
        "criterion_sha256": context.digest(ticket["acceptance"].encode("utf-8"))
        if ticket["acceptance"] else None,
    }
    checks = []
    for path, expected in ticket["evidence"].items():
        context.require(path not in non_evidence, "evidence cannot be the projection or a requirement source")
        pin = {"path": path, "sha256": expected}
        try:
            raw = snapshot.read(path)
        except (OSError, context.ContextError):
            checks.append({**pin, "status": "unavailable"})
            continue
        if context.digest(raw) != expected:
            checks.append({**pin, "status": "stale"})
            continue
        record = acceptance_record(raw)
        check = inspect_receipt(snapshot, path, record, binding, non_evidence) if record else {
            "kind": "artifact", "status": "verified",
        }
        checks.append({**pin, **check})
    return checks


def proof_blockers(evidence):
    return [{"code": f"evidence-{pin['status']}", "path": pin["path"]}
            for pin in evidence if pin["status"] != "verified"]


def acceptance_blockers(ticket, prerequisites, members, supported, evidence):
    blockers = [{"code": "prerequisite-open", "ticket": key} for key in prerequisites
                if key not in supported]
    blockers.extend({"code": "child-open", "ticket": key} for key in members
                    if key not in supported)
    blockers.extend(proof_blockers(evidence))
    if not ticket["acceptance"]:
        blockers.append({"code": "missing-acceptance-criterion"})
    if not evidence:
        blockers.append({"code": "missing-acceptance-evidence"})
    elif not any(pin.get("kind") == "acceptance-receipt" and pin["status"] == "verified"
                 for pin in evidence) and not proof_blockers(evidence):
        blockers.append({"code": "missing-bound-acceptance-evidence"})
    if ticket["kind"] not in GROUPS and not ticket["requirement_ids"]:
        blockers.append({"code": "missing-requirement-link"})
    return blockers


def execution_blockers(ticket, prerequisites, ancestor_blockers, supported, available):
    blockers = [{"code": "prerequisite-held" if key in supported else "prerequisite-open",
                 "ticket": key} for key in prerequisites if key not in available]
    blockers.extend(ancestor_blockers)
    if ticket["blocked_reason"] or ticket["recorded_status"] == "blocked":
        blocker = {"code": "recorded-block"}
        if ticket["blocked_reason"]:
            blocker["reason"] = ticket["blocked_reason"]
        blockers.append(blocker)
    return blockers


def board_state(ticket, blockers, acceptance):
    state = ticket["recorded_status"]
    if state == "accepted":
        return "accepted" if acceptance == "supported" else "blocked"
    if state == "deferred":
        return "deferred"
    if blockers:
        return "blocked"
    if state != "planned":
        return state
    if ticket["kind"] in GROUPS:
        return "grouped"
    if not ticket["acceptance"] or not ticket["requirement_ids"]:
        return "needs-refinement"
    return "ready"


def project_board(root, name, *, snapshot=None):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    if snapshot is None:
        snapshot = Snapshot(root)
    context.require(isinstance(snapshot, Snapshot) and snapshot.root == root,
                    "expected a snapshot owned by the same project root")
    projection_bytes = snapshot.read(name)
    projection = context.json_object(projection_bytes)
    context.require(projection.get("schema_version") == PROJECTION, "unsupported ticket projection schema")
    source_pins = pins(projection.get("requirement_sources"))
    context.require(source_pins and name not in source_pins,
                    "expected a separate pinned requirement registry")
    requirements = read_requirements(snapshot, source_pins)
    tickets = normalize_tickets(projection, requirements)
    retirements = replan_retirements(projection, tickets)
    children, prerequisites, ancestor_blockers, order = ticket_graph(tickets, retired=retirements)
    supported, available = set(), set()
    active_coverage, deferred_coverage = set(), set()
    invalid_claims = []
    states = {state: [] for state in (
        "ready", "needs-refinement", "in-progress", "in-review", "blocked",
        "accepted", "deferred", "grouped",
    )}
    view = {}
    identity = {field: context.text(projection, field) for field in ("project_id", "native_revision")}
    projection_sha = context.digest(projection_bytes)
    non_evidence = {**source_pins, name: projection_sha}
    for key in order:
        ticket = tickets[key]
        checks = inspect_evidence(snapshot, ticket, identity, non_evidence)
        members = [child for child in children[key] if child not in retirements]
        holding = execution_blockers(ticket, prerequisites[key], ancestor_blockers[key],
                                     supported, available)
        acceptance = "not-recorded"
        unsupported = []
        if ticket["recorded_status"] == "accepted":
            unsupported = acceptance_blockers(ticket, prerequisites[key], members,
                                             supported, checks)
            acceptance = "unsupported" if unsupported else "supported"
            if unsupported:
                invalid_claims.append(key)
            else:
                supported.add(key)
                holding.extend({"code": "child-held", "ticket": child} for child in members
                               if child not in available)
                if not holding:
                    available.add(key)
        else:
            holding.extend(proof_blockers(checks))
        if ticket["kind"] not in GROUPS and key not in retirements:
            deferred = ticket["recorded_status"] == "deferred" or any(
                blocker["code"] == "ancestor-deferred" for blocker in ancestor_blockers[key]
            )
            coverage = deferred_coverage if deferred else active_coverage
            coverage.update(ticket["requirement_closure"])
        blockers = holding + [item for item in unsupported if item not in holding]
        state = board_state(ticket, blockers, acceptance)
        disposition = "held" if blockers or state == "deferred" else (
            "satisfied" if acceptance == "supported" else "open"
        )
        states[state].append(key)
        view[key] = {
            **ticket, "evidence": checks, "children": children[key],
            "board_state": state, "blockers": blockers,
            "acceptance_status": acceptance, "acceptance_blockers": unsupported,
            "execution_disposition": disposition,
            "effective_prerequisites": prerequisites[key],
        }
        if members != children[key]:
            view[key]["completion_children"] = members
        if key in retirements:
            view[key]["replan_retirement"] = retirements[key]
    snapshot.verify_unchanged()
    must = {key for key, row in requirements.items()
            if row["applicable"] and row["priority"] == "must"}
    return {
        "schema_version": BOARD, **identity,
        "projection": {"path": name, "sha256": projection_sha},
        "requirement_sources": source_pins,
        "requirements": [{key: row[key] for key in ("id", "source_ref", "source_sha256", "priority")}
                         for row in requirements.values()],
        "roots": children[None], "evaluation_order": order, "board": states,
        "tickets": [view[key] for key in tickets],
        "unsupported_acceptance_claims": invalid_claims,
        "unmapped_must_requirements": sorted(must - active_coverage - deferred_coverage),
        "deferred_only_must_requirements": sorted((must & deferred_coverage) - active_coverage),
        "authority_authenticated": False, "functional_outcome_verified": False,
    }


def sprint_bucket(ticket, prerequisites):
    state = ticket["board_state"]
    if state == "accepted":
        return "accepted"
    holds = {"ancestor-deferred", "ancestor-blocked", "recorded-block"}
    if state == "deferred" or any(block["code"] in holds for block in ticket["blockers"]):
        return "held"
    if ticket["acceptance_status"] == "unsupported" or any(
        block["code"].startswith("evidence-") for block in ticket["blockers"]
    ):
        return "blocked"
    if any(gate["scope"] == "outside" and not gate["satisfied"] for gate in prerequisites):
        return "blocked"
    if any(not gate["satisfied"] for gate in prerequisites) or state == "needs-refinement":
        return "future"
    return "ready" if state == "ready" else "held"


def sprint_leaves(tickets, order):
    leaf_sets = {}
    for key in order:
        ticket = tickets[key]
        if ticket["kind"] in GROUPS:
            children = ticket.get("completion_children", ticket["children"])
            leaf_sets[key] = set().union(*(leaf_sets[child] for child in children))
        else:
            leaf_sets[key] = set() if "replan_retirement" in ticket else {key}
    return leaf_sets


def select_sprint(board, selectors):
    context.bounded_ids(selectors, "sprint selectors")
    context.require(selectors, "select at least one ticket or group for the sprint")
    tickets = {row["id"]: row for row in board["tickets"]}
    order = board["evaluation_order"]
    leaf_sets = sprint_leaves(tickets, order)
    selected = set()
    for key in selectors:
        context.require(key in tickets, f"unknown sprint selector: {key}")
        context.require(leaf_sets[key], f"sprint selector has no leaf work: {key}")
        selected.update(leaf_sets[key])
    outside_counts = {key: len(leaves - selected) for key, leaves in leaf_sets.items()}
    internal = {key for key, count in outside_counts.items() if not count and leaf_sets[key]}
    categories = {name: [] for name in ("ready", "held", "blocked", "future", "accepted")}
    work = []
    for key in order:
        if key not in selected:
            continue
        ticket = tickets[key]
        gates = []
        for prerequisite in ticket["effective_prerequisites"]:
            gate = tickets[prerequisite]
            gates.append({
                "ticket": prerequisite,
                "scope": "inside" if prerequisite in internal else "outside",
                "satisfied": gate["execution_disposition"] == "satisfied",
                "execution_disposition": gate["execution_disposition"],
                "outside_selected_work_count": outside_counts[prerequisite],
            })
        category = sprint_bucket(ticket, gates)
        categories[category].append(key)
        work.append({
            "id": key, "title": ticket["title"], "kind": ticket["kind"],
            "recorded_status": ticket["recorded_status"], "board_state": ticket["board_state"],
            "acceptance_status": ticket["acceptance_status"],
            "execution_disposition": ticket["execution_disposition"],
            "blockers": ticket["blockers"], "prerequisites": gates, "sprint_state": category,
        })
    return {
        "schema_version": SPRINT,
        "project_id": board["project_id"], "native_revision": board["native_revision"],
        "projection": board["projection"], "selectors": selectors,
        "sprint": categories, "tickets": work,
        "authority_authenticated": False, "functional_outcome_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("board", "validate", "sprint"))
    parser.add_argument("--root", type=Path, required=True, help="canonical absolute project root")
    parser.add_argument("--input", required=True, help="explicit projection path relative to the project")
    parser.add_argument("--require-complete", action="store_true",
                        help="fail validation when any must lacks a mapped work ticket or explicit deferral")
    parser.add_argument("--select", action="append", default=[], metavar="TICKET",
                        help="ticket or group ID to include in sprint; repeat to select more")
    args = parser.parse_args()
    if args.select and args.operation != "sprint":
        parser.error("--select is only supported by sprint")
    if args.require_complete and args.operation != "validate":
        parser.error("--require-complete is only supported by validate")
    try:
        board = project_board(args.root, args.input)
        if args.operation == "sprint":
            board = select_sprint(board, args.select)
    except (context.ContextError, OSError) as error:
        status = "invalid-sprint" if args.operation == "sprint" else "invalid-projection"
        print(json.dumps({"status": status, "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(board, ensure_ascii=False, indent=2))
    if args.operation == "validate" and (
        board["unsupported_acceptance_claims"]
        or (args.require_complete and board["unmapped_must_requirements"])
    ):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
