#!/usr/bin/env python3
"""Prepare or verify a source-bound ticket refinement proposal without editing the project."""

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree

context = tree.context

REQUEST = "atelier.ticket-refinement/1"
BRIEF = "atelier.ticket-refinement-brief/1"
PROPOSAL = "atelier.ticket-refinement-proposal/1"
PLAN_FIELDS = {
    "title": "wording",
    "acceptance": "acceptance-criterion",
    "parent": "group-membership",
    "depends_on": "execution-order",
    "requirement_ids": "requirement-links",
}
BASE_FIELDS = ("project_id", "native_revision")


def load_plan(root, name):
    snapshot = tree.Snapshot(root)
    board = tree.project_board(root, name, snapshot=snapshot)
    raw = snapshot.read(name)
    requirements = tree.read_requirements(snapshot, board["requirement_sources"])
    return snapshot, board, context.json_object(raw), requirements


def prepare_brief(root, name, selectors):
    context.bounded_ids(selectors, "ticket selectors")
    context.require(selectors, "select at least one ticket for refinement")
    snapshot, board, _, requirements = load_plan(root, name)
    tickets = {row["id"]: row for row in board["tickets"]}
    selected = []
    for key in selectors:
        context.require(key in tickets, f"unknown ticket: {key}")
        selected.append(tickets[key])
    requirement_ids = sorted({key for row in selected for key in row["requirement_closure"]})
    sources = [
        {field: requirements[key][field] for field in (
            "id", "source_ref", "source_sha256", "verbatim", "acceptance", "dependencies",
            "priority", "applicable", "owner", "due_gate",
        )}
        for key in requirement_ids
    ]
    snapshot.verify_unchanged()
    return {
        "schema_version": BRIEF,
        **{key: board[key] for key in BASE_FIELDS},
        "projection": board["projection"],
        "requirement_sources": board["requirement_sources"],
        "selected_tickets": selected,
        "requirements": sources,
        "unmapped_must_requirements": board["unmapped_must_requirements"],
        "deferred_only_must_requirements": board["deferred_only_must_requirements"],
    }


def read_request(snapshot, board, name):
    protected = {board["projection"]["path"]: board["projection"]["sha256"],
                 **board["requirement_sources"]}
    for ticket in board["tickets"]:
        for evidence in ticket["evidence"]:
            protected[evidence["path"]] = evidence["sha256"]
            if "subject" in evidence:
                protected[evidence["subject"]["path"]] = evidence["subject"]["sha256"]
    context.require(name not in protected, "expected a separate proposal file")
    raw = snapshot.read(name)
    expected = {
        "schema_version": REQUEST,
        **{key: board[key] for key in BASE_FIELDS},
        "projection_sha256": board["projection"]["sha256"],
    }
    request = context.json_object(raw)
    context.require(set(request) == {*expected, "changes"}, "invalid refinement request fields")
    context.require(all(request[key] == value for key, value in expected.items()),
                    "refinement baseline mismatch: expected current project, revision and projection")
    changes = request["changes"]
    context.require(isinstance(changes, list) and 1 <= len(changes) <= 100,
                    "expected 1 to 100 explicit ticket changes")
    return changes, {"path": name, "sha256": context.digest(raw)}, protected


def checked_citations(snapshot, sources, requirements, blocked):
    context.require(isinstance(sources, list) and 1 <= len(sources) <= 20,
                    "expected 1 to 20 pinned source citations per change")
    result = []
    seen = set()
    for source in sources:
        context.require(isinstance(source, dict) and set(source) in (
            {"path", "sha256", "excerpt"}, {"path", "sha256", "excerpt", "requirement_id"}
        ), "invalid source citation fields")
        path, digest, excerpt = (context.text(source, key) for key in ("path", "sha256", "excerpt"))
        context.require(context.HASH.fullmatch(digest) and len(excerpt) <= 2000,
                        "invalid citation digest or excerpt length")
        context.require(path not in blocked and digest not in blocked.values(),
                        f"citation source is a proposal, projection or ticket proof: {path}")
        raw = snapshot.read(path)
        context.require(context.digest(raw) == digest, f"SOURCE_DRIFT: {path}")
        if "requirement_id" in source:
            key = context.text(source, "requirement_id")
            row = requirements.get(key)
            context.require(row and row["source_ref"] == path and row["source_sha256"] == digest,
                            f"citation is not from the pinned requirement record: {key}")
            fields = ["verbatim"]
            if any(row["raw_native_record"].get(field) is not None
                   for field in ("acceptance", "acceptance_criteria")):
                fields.append("acceptance")
            matched = next((field for field in fields if excerpt in row[field]), None)
            context.require(matched, f"citation excerpt is absent from the named requirement: {key}")
            receipt = {"kind": "requirement", "matched_field": matched}
        else:
            try:
                literal = raw.decode("utf-8")
            except UnicodeError as error:
                raise context.ContextError(f"citation source is not UTF-8: {path}") from error
            offset = literal.find(excerpt)
            context.require(offset >= 0, f"citation excerpt is absent from source: {path}")
            receipt = {"kind": "project-source", "first_line": literal.count("\n", 0, offset) + 1}
        signature = (path, source.get("requirement_id"), excerpt)
        context.require(signature not in seen, f"duplicate source citation: {path}")
        seen.add(signature)
        result.append({**source, **receipt})
    return result


def prepare_change(change, rows, current, snapshot, requirements, blocked, seen):
    context.require(isinstance(change, dict) and set(change) == {
        "ticket_id", "rationale", "patch", "sources",
    }, "invalid refinement change fields")
    key = context.text(change, "ticket_id")
    rationale = context.text(change, "rationale")
    context.require(key in rows and key not in seen, f"unknown or duplicate ticket: {key}")
    context.require("replan_retirement" not in current[key], f"retired work is historical: {key}")
    seen.add(key)
    patch = change["patch"]
    context.require(isinstance(patch, dict) and patch and set(patch) <= PLAN_FIELDS.keys(),
                    f"refinement may edit only planning fields: {key}")
    for field in ("title", "acceptance"):
        if field in patch:
            context.text(patch, field)
    for field in ("requirement_ids", "depends_on"):
        if field in patch:
            context.bounded_ids(patch[field], field)

    changes = {field: {"from": current[key][field], "to": value}
               for field, value in patch.items() if current[key][field] != value}
    context.require(changes, f"refinement has no effective changes: {key}")
    sources = checked_citations(snapshot, change["sources"], requirements, blocked)
    citation_ids = {row["requirement_id"] for row in sources if row["kind"] == "requirement"}
    linked_before = set(current[key]["requirement_ids"])
    linked_after = set(patch.get("requirement_ids", linked_before))
    link_delta = linked_before ^ linked_after
    context.require(link_delta <= citation_ids,
                    f"missing citation for changed requirement links on {key}: "
                    + ", ".join(sorted(link_delta - citation_ids)))
    if "acceptance" in changes and linked_after:
        context.require(citation_ids & linked_after,
                        f"acceptance change requires a citation to a linked requirement: {key}")

    rows[key].update(patch)
    return {
        "ticket_id": key,
        "rationale": rationale,
        "changes": changes,
        "classifications": [PLAN_FIELDS[field] for field in changes],
        "sources": sources,
        "recorded_status": current[key]["recorded_status"],
        "baseline_acceptance_status": current[key]["acceptance_status"],
        "baseline_evidence": current[key]["evidence"],
    }


def is_deferred(row, blockers):
    return row["recorded_status"] == "deferred" or any(
        blocker["code"] == "ancestor-deferred" for blocker in blockers
    )


def check_coverage(current, planned, requirements, ancestor_blockers):
    before_active, before_deferred, active, deferred = set(), set(), set(), set()
    for key, row in planned.items():
        if "replan_retirement" in current[key]:
            continue
        was_deferred = is_deferred(current[key], current[key]["blockers"])
        held = is_deferred(row, ancestor_blockers[key])
        context.require(was_deferred == held, f"refinement changes native deferral: {key}")
        if row["kind"] not in tree.GROUPS:
            previous_coverage = before_deferred if held else before_active
            previous_coverage.update(current[key]["requirement_closure"])
            coverage = deferred if held else active
            coverage.update(row["requirement_closure"])
    must = {key for key, row in requirements.items()
            if row["applicable"] and row["priority"] == "must"}
    protected = must | {key for key, row in requirements.items()
                        if row["applicable"] and row["always_review"]}
    missing = protected - active - deferred
    regressions = (missing & (before_active | before_deferred)) | ((protected & before_active) - active)
    context.require(not regressions,
                    "mandatory or always-review coverage regressed: " + ", ".join(sorted(regressions)))
    return {
        "unmapped_must_requirements": sorted(missing & must),
        "deferred_only_must_requirements": sorted((deferred & must) - active),
        "unmapped_always_review_requirements": sorted(key for key in missing
                                                      if requirements[key]["always_review"]),
    }


def task_followup(row, proposed):
    if row["recorded_status"] == "accepted":
        if set(row["changes"]) - {"title"}:
            return "review-new-evidence", "foundry-qa"
        return "review-preservation-of-accepted-history", "foundry-judge"
    if is_deferred(row, proposed):
        return "review-without-activating-deferred-work", "foundry-product"
    if set(row["changes"]) & {"parent", "depends_on"}:
        return "review-dependencies-and-handoff", "foundry-architecture"
    if row["recorded_status"] in {"in-progress", "in-review"}:
        return "reconcile-with-current-owner", "foundry-product"
    return "review-refinement-with-project-owner", "foundry-product"


def propose(root, name, proposal_name):
    snapshot, board, projection, requirements = load_plan(root, name)
    changes, proposal, protected = read_request(snapshot, board, proposal_name)
    rows = context.records(projection, "tickets")
    current = {row["id"]: row for row in board["tickets"]}
    source_blocked = {key: value for key, value in protected.items()
                      if key not in board["requirement_sources"]}
    source_blocked[proposal["path"]] = proposal["sha256"]

    seen = set()
    changes = [
        prepare_change(change, rows, current, snapshot, requirements, source_blocked, seen)
        for change in changes
    ]
    planned = tree.normalize_tickets(projection, requirements)
    retirements = tree.replan_retirements(projection, planned)
    children, prerequisites, ancestor_blockers, order = tree.ticket_graph(planned, retired=retirements)
    coverage = check_coverage(current, planned, requirements, ancestor_blockers)
    for row in changes:
        key = row["ticket_id"]
        row["proposed_requirement_closure"] = planned[key]["requirement_closure"]
        followup, role = task_followup(row, ancestor_blockers[key])
        row["follow_up"] = {"action": followup, "suggested_role": role}
    graph_changes = []
    for key in order:
        fields = {}
        for field, previous, value in (
            ("effective_prerequisites", current[key]["effective_prerequisites"], prerequisites[key]),
            ("children", current[key]["children"], children[key]),
            ("ancestor_blockers", [item for item in current[key]["blockers"]
                                   if item["code"].startswith("ancestor-")], ancestor_blockers[key]),
        ):
            if previous != value:
                fields[field] = {"from": previous, "to": value}
        previous_members = current[key].get("completion_children", current[key]["children"])
        next_members = [child for child in children[key] if child not in retirements]
        if previous_members != next_members and (
            "completion_children" in current[key] or next_members != children[key]
        ):
            fields["completion_children"] = {"from": previous_members, "to": next_members}
        if fields:
            graph_changes.append({"ticket_id": key, "changes": fields})
    snapshot.verify_unchanged()
    return {
        "schema_version": PROPOSAL,
        **{key: board[key] for key in BASE_FIELDS},
        "baseline_projection": board["projection"],
        "proposal": proposal,
        "requirement_sources": board["requirement_sources"],
        "changes": changes,
        "graph_changes": graph_changes,
        "proposed_coverage": coverage,
        "next": "Review with the project owner, then capture any authorized native revision independently.",
        "authority_authenticated": False,
        "semantic_support_verified": False,
        "applied": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("brief", "propose"))
    parser.add_argument("--root", type=Path, required=True, help="canonical absolute project root")
    parser.add_argument("--input", required=True, help="current projection path relative to the project")
    parser.add_argument("--proposal", help="explicit refinement request path relative to the project")
    parser.add_argument("--select", action="append", default=[], metavar="TICKET",
                        help="ticket to inspect in a refinement brief, repeat to select more")
    args = parser.parse_args()
    if args.operation == "brief" and args.proposal:
        parser.error("--proposal is only supported by propose")
    if args.operation == "propose" and (not args.proposal or args.select):
        parser.error("propose requires --proposal and takes scope from the request")
    try:
        if args.operation == "brief":
            result = prepare_brief(args.root, args.input, args.select)
        else:
            result = propose(args.root, args.input, args.proposal)
    except (context.ContextError, OSError) as error:
        print(json.dumps({"status": "invalid-refinement", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
