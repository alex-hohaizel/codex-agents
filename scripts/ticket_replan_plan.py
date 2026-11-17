#!/usr/bin/env python3
"""Build a reviewable, source-bound transition for the native ticket projection."""

import argparse
from collections import defaultdict, deque
from copy import deepcopy
import json
from pathlib import Path
import sys

import ticket_refine as refine

tree = refine.tree
context = tree.context

REQUEST = "atelier.ticket-replan-request/1"
PLAN = "atelier.ticket-replan-plan/1"
ACTION_FIELDS = {
    "create": {"ticket"},
    "replace": {"ticket_id", "ticket"},
    "split": {"ticket_id", "tickets"},
    "drop": {"ticket_id"},
}
DRAFT_FIELDS = tree.FIELDS - {"evidence", "blocked_reason"}
PROTECTED_STATUSES = {"accepted", "in-progress", "in-review"}


class TargetSnapshot(tree.Snapshot):
    """Evaluate prospective projection bytes against the same pinned native inputs."""

    def __init__(self, baseline, projection_name, raw):
        super().__init__(baseline.root)
        self.baseline = baseline
        self.projection_name = projection_name
        self.raw = raw

    def read(self, path):
        if path == self.projection_name:
            return self.raw
        return self.baseline.read(path)

    def verify_unchanged(self):
        self.baseline.verify_unchanged()


def read_request(snapshot, board, name):
    protected = {board["projection"]["path"]: board["projection"]["sha256"]}
    for ticket in board["tickets"]:
        for evidence in ticket["evidence"]:
            protected[evidence["path"]] = evidence["sha256"]
            if "subject" in evidence:
                protected[evidence["subject"]["path"]] = evidence["subject"]["sha256"]
    context.require(name not in protected and name not in board["requirement_sources"],
                    "expected a separate replan request file")
    raw = snapshot.read(name)
    pin = {"path": name, "sha256": context.digest(raw)}
    request = context.json_object(raw)
    expected = {
        "schema_version": REQUEST,
        "project_id": board["project_id"],
        "native_revision": board["native_revision"],
        "projection_sha256": board["projection"]["sha256"],
    }
    context.require(set(request) == {*expected, "target_revision", "changes"},
                    "invalid replan request fields")
    context.require(all(request[key] == value for key, value in expected.items()),
                    "replan baseline mismatch: expected current project, revision and projection")
    revision = context.text(request, "target_revision")
    context.require(revision == revision.strip() and len(revision) <= 240
                    and revision != board["native_revision"], "target revision must be new")
    changes = request["changes"]
    context.require(isinstance(changes, list) and 1 <= len(changes) <= 100,
                    "expected 1 to 100 explicit replan actions")
    protected[name] = pin["sha256"]
    return request, pin, protected


def normalize_draft(row, *, leaf_only=False):
    context.require(isinstance(row, dict) and set(row) <= DRAFT_FIELDS,
                    "new tickets allow only planning fields and planned status")
    key = context.text(row, "id")
    kind = context.text(row, "kind")
    context.text(row, "title")
    context.require(kind in tree.PARENTS, f"unsupported ticket kind: {key}")
    context.require(row.get("status", "planned") == "planned", f"new ticket must be planned: {key}")
    requirement_ids = context.bounded_ids(row.get("requirement_ids", []), "requirement_ids")
    if leaf_only:
        context.require(kind not in tree.GROUPS, f"expected a leaf successor: {key}")
    if kind not in tree.GROUPS:
        context.require(requirement_ids, f"new work needs a governing requirement: {key}")
        context.text(row, "acceptance")
    return {**row, "status": "planned"}


def prepare_actions(changes, rows, snapshot, requirements, protected):
    reviewed, replacements, additions = [], {}, {}
    for row in changes:
        context.require(isinstance(row, dict), "expected a replan action object")
        action = context.text(row, "action")
        context.require(action in ACTION_FIELDS and set(row) == {
            "action", "rationale", "sources", *ACTION_FIELDS[action],
        }, f"invalid replan action fields: {action}")
        rationale = context.text(row, "rationale")
        old = None
        if "ticket_id" in row:
            key = context.text(row, "ticket_id")
            old = rows.get(key)
            context.require(old is not None and key not in replacements,
                            f"unknown or duplicate retirement: {key}")
            context.require(old["kind"] not in tree.GROUPS and old["status"] == "planned",
                            f"only a planned leaf can be retired: {key}")
        drafts = []
        if action == "split":
            context.require(isinstance(row["tickets"], list) and 2 <= len(row["tickets"]) <= 30,
                            "a split needs 2 to 30 new leaf tickets")
            drafts = [normalize_draft(x, leaf_only=True) for x in row["tickets"]]
        elif action != "drop":
            drafts = [normalize_draft(row["ticket"], leaf_only=action == "replace")]
        sources = refine.checked_citations(snapshot, row["sources"], requirements, protected)
        cited_ids = {source["requirement_id"] for source in sources if source["kind"] == "requirement"}
        linked_ids = {ident for ticket in [*drafts, *([old] if old else [])]
                      for ident in ticket.get("requirement_ids", [])}
        context.require(linked_ids <= cited_ids,
                        "missing citation for linked requirements: " + ", ".join(sorted(linked_ids - cited_ids)))
        for draft in drafts:
            key = draft["id"]
            context.require(key not in rows and key not in additions, f"ticket ID already exists: {key}")
            additions[key] = draft
        change = {"action": action, "rationale": rationale, "sources": sources, "created": drafts}
        if old is not None:
            old_key = old["id"]
            replacements[old_key] = [draft["id"] for draft in drafts]
            change["retired"] = {"id": old_key, "before": old, "after": {**old, "status": "deferred"}}
        reviewed.append(change)
    return reviewed, replacements, additions


def update_dependencies(rows, replacements, additions):
    updated = []
    for key, row in rows.items():
        if key in replacements or row["status"] == "deferred":
            continue
        prior = row.get("depends_on", [])
        retired_dependencies = replacements.keys() & set(prior)
        if not retired_dependencies:
            continue
        context.require(key not in additions, f"new ticket depends on work being retired: {key}")
        context.require(row["kind"] not in tree.GROUPS and row["status"] == "planned",
                        f"retirement would alter non-planned or grouped work: {key}")
        context.require(all(replacements[dep] for dep in retired_dependencies),
                        f"cannot drop a prerequisite of retained work: {key}")
        following = list(dict.fromkeys(target for dep in prior for target in replacements.get(dep, [dep])))
        row["depends_on"] = following
        updated.append({"ticket_id": key, "before": prior, "after": following})
    return updated


def active_and_deferred(board):
    active, deferred = set(), set()
    for ticket in board["tickets"]:
        if ticket["kind"] in tree.GROUPS or "replan_retirement" in ticket:
            continue
        members = deferred if refine.is_deferred(ticket, ticket["blockers"]) else active
        members.update(ticket["requirement_closure"])
    return active, deferred


def compare_coverage(before, after, requirements):
    prior, prior_deferred = active_and_deferred(before)
    active, deferred = active_and_deferred(after)
    protected = {key for key, row in requirements.items()
                 if row["applicable"] and (row["priority"] == "must" or row["always_review"])}
    regressed = protected & ((prior - active) | (prior_deferred - active - deferred))
    context.require(not regressed,
                    "mandatory or always-review coverage regressed: " + ", ".join(sorted(regressed)))
    return {
        "unmapped_must_requirements": after["unmapped_must_requirements"],
        "deferred_only_must_requirements": after["deferred_only_must_requirements"],
        "unmapped_always_review_requirements": sorted(
            key for key in protected - active - deferred if requirements[key]["always_review"]
        ),
    }


def compare_graph(before, after, replacements):
    old = {row["id"]: row for row in before["tickets"]}
    differences = []
    for row in after["tickets"]:
        key = row["id"]
        previous = old.get(key)
        if previous is None:
            context.require(not refine.is_deferred(row, row["blockers"]),
                            f"new work belongs to a deferred branch: {key}")
            continue
        if key not in replacements:
            context.require(refine.is_deferred(previous, previous["blockers"])
                            == refine.is_deferred(row, row["blockers"]),
                            f"replan changes existing deferral indirectly: {key}")
        changed = {
            field: {"before": previous[field], "after": row[field]}
            for field in ("effective_prerequisites", "children") if previous[field] != row[field]
        }
        before_members = previous.get("completion_children", previous["children"])
        after_members = row.get("completion_children", row["children"])
        if before_members != after_members:
            changed["completion_children"] = {"before": before_members, "after": after_members}
        if changed:
            context.require(previous["recorded_status"] not in PROTECTED_STATUSES,
                            f"replan would change active or accepted work indirectly: {key}")
            differences.append({"ticket_id": key, "changes": changed})
    return differences


def expand_affected(before, after, edited):
    """Include downstream work in both revisions through dependency and completion edges."""
    followers = defaultdict(set)
    for board in (before, after):
        for row in board["tickets"]:
            members = row.get("completion_children", row["children"])
            for predecessor in (*row["effective_prerequisites"], *members):
                followers[predecessor].add(row["id"])
    affected = set(edited)
    queue = deque(edited)
    while queue:
        for key in followers[queue.popleft()] - affected:
            affected.add(key)
            queue.append(key)
    for row in before["tickets"]:
        if row["id"] in affected:
            context.require(row["recorded_status"] not in PROTECTED_STATUSES,
                            f"replan touches a prerequisite of active or accepted work: {row['id']}")
    return affected


def readiness(before, after, affected):
    previous = {row["id"]: row for row in before["tickets"]}
    ready = [key for key in after["board"]["ready"] if key in affected]
    review = []
    for row in after["tickets"]:
        key = row["id"]
        if key not in affected:
            continue
        old_state = previous[key]["board_state"] if key in previous else None
        review.append({
            "ticket_id": key,
            "before": old_state,
            "after": row["board_state"],
            "blockers": row["blockers"],
        })
    invalidated = [key for key in after["unsupported_acceptance_claims"]
                   if key in previous and previous[key]["acceptance_status"] == "supported"]
    return {
        "ready_ticket_ids": ready,
        "affected_tickets": review,
        "unsupported_acceptance_claims": after["unsupported_acceptance_claims"],
        "previously_supported_acceptance_needs_recheck": invalidated,
    }


def build_plan(root, projection_name, request_name):
    """Return a deterministic, read-only proposal with an exact next projection."""
    snapshot, before, projection, requirements = refine.load_plan(root, projection_name)
    request, pin, protected = read_request(snapshot, before, request_name)
    rows = context.records(projection, "tickets")
    changes, replacements, additions = prepare_actions(
        request["changes"], rows, snapshot, requirements, protected
    )
    target = deepcopy(projection)
    target["native_revision"] = request["target_revision"]
    target_rows = context.records(target, "tickets")
    for key in replacements:
        target_rows[key]["status"] = "deferred"
    target_rows.update(deepcopy(additions))
    previous_retirements = {entry["ticket_id"] for entry in target.get("replan_retirements", [])}
    for key, draft in additions.items():
        direct = context.bounded_ids(draft.get("depends_on", []), "depends_on")
        context.require(not previous_retirements.intersection(direct),
                        f"new ticket depends on previously retired work: {key}")
    if replacements:
        target["replan_retirements"] = [
            *target.get("replan_retirements", []),
            *(
                {
                    "ticket_id": change["retired"]["id"],
                    "action": change["action"],
                    "retired_in": target["native_revision"],
                    "successors": replacements[change["retired"]["id"]],
                }
                for change in changes if "retired" in change
            ),
        ]
    rewired = update_dependencies(target_rows, replacements, additions)
    target["tickets"] = list(target_rows.values())
    raw = context.canonical(target)
    context.require(len(raw) <= context.MAX_BOUND_SOURCE, "target projection exceeds 2 MiB")
    after = tree.project_board(
        root, projection_name, snapshot=TargetSnapshot(snapshot, projection_name, raw)
    )
    graph = compare_graph(before, after, replacements)
    coverage = compare_coverage(before, after, requirements)
    affected = {*replacements, *additions, *(item["ticket_id"] for item in rewired)}
    affected.update(item["ticket_id"] for item in graph)
    affected = expand_affected(before, after, affected)
    snapshot.verify_unchanged()
    return {
        "schema_version": PLAN,
        "project_id": before["project_id"],
        "native_revision": before["native_revision"],
        "target_revision": request["target_revision"],
        "projection": before["projection"],
        "request": pin,
        "requirement_sources": before["requirement_sources"],
        "target": target,
        "changes": changes,
        "rewired_dependencies": rewired,
        "graph_changes": graph,
        "coverage": coverage,
        "readiness": readiness(before, after, affected),
        "authority_authenticated": False,
        "semantic_support_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--projection", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    try:
        plan = build_plan(args.root, args.projection, args.request)
        result = {"plan_sha256": context.digest(context.canonical(plan)), "plan": plan}
    except (context.ContextError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
