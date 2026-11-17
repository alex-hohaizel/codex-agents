#!/usr/bin/env python3
"""Check whether a historically accepted proof can be sent for scoped reuse review."""

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_impact as impact
import ticket_tree as tree

context = tree.context
SCOPE = "atelier.ticket-proof-scope/1"
ASSESSMENT = "atelier.ticket-proof-scope-assessment/1"


def prerequisite_closure(tickets, key):
    pending = list(tickets[key]["effective_prerequisites"])
    selected = set()
    while pending:
        dependency = pending.pop()
        if dependency in selected:
            continue
        selected.add(dependency)
        row = tickets[dependency]
        pending.extend(row["effective_prerequisites"])
        if row["kind"] in tree.GROUPS:
            pending.extend(child for child in row["children"]
                           if not tickets[child].get("replan_retirement"))
    return selected


def add_evidence_checks(ticket, checked):
    for pin in ticket["evidence"]:
        for evidence_pin in (pin, pin.get("subject")):
            if evidence_pin is None:
                continue
            path, digest = evidence_pin["path"], evidence_pin["sha256"]
            context.require(path not in checked or checked[path] == digest,
                            f"contradictory historical proof pin: {path}")
            checked[path] = digest


def evidence_pins(ticket):
    return {pin["path"]: pin["sha256"] for pin in ticket["evidence"]}


def add_prerequisite_checks(before, after, key, checked, blockers):
    for dependency in sorted(prerequisite_closure(before, key)):
        old = before[dependency]
        current = after.get(dependency)
        if (old["acceptance_status"] != "supported" or not current
                or current["recorded_status"] != "accepted"
                or current.get("replan_retirement") or current["effective_prerequisites"]
                != old["effective_prerequisites"]):
            blockers.append({"reason": "prerequisite-acceptance-changed", "ticket_id": dependency})
            continue
        if evidence_pins(old) != evidence_pins(current):
            blockers.append({"reason": "prerequisite-evidence-changed", "ticket_id": dependency})
            continue
        add_evidence_checks(old, checked)


def assess(before, after, projection, scope_name, scope_sha256):
    context.require(context.HASH.fullmatch(scope_sha256), "invalid scope record SHA-256")
    old, live = tree.Snapshot(before), tree.Snapshot(after)
    historical = tree.project_board(before, projection, snapshot=old)
    current = tree.project_board(after, projection, snapshot=live)
    context.require(historical["project_id"] == current["project_id"]
                    and historical["native_revision"] != current["native_revision"],
                    "expected separate revisions of the same project")
    raw = old.read(scope_name)
    context.require(context.digest(raw) == scope_sha256, "historical proof scope changed")
    scope = context.json_object(raw)
    expected = {"schema_version": SCOPE, "project_id": historical["project_id"],
                "native_revision": historical["native_revision"]}
    context.require(set(scope) == {*expected, "ticket_id", "receipt", "inputs"}
                    and all(scope[key] == value for key, value in expected.items()),
                    "proof scope must bind the historical project and revision")
    key = context.text(scope, "ticket_id")
    tickets_before = {row["id"]: row for row in historical["tickets"]}
    tickets_after = {row["id"]: row for row in current["tickets"]}
    old_ticket = tickets_before.get(key)
    next_ticket = tickets_after.get(key)
    context.require(old_ticket and old_ticket["kind"] not in tree.GROUPS
                    and old_ticket["acceptance_status"] == "supported",
                    "proof scope needs a historically accepted leaf with verified evidence")
    receipt_path, receipt_sha = next(iter(tree.pins([scope["receipt"]]).items()))
    receipt = next((pin for pin in old_ticket["evidence"] if pin["path"] == receipt_path
                    and pin["sha256"] == receipt_sha and pin["status"] == "verified"
                    and pin["kind"] == "acceptance-receipt"), None)
    context.require(receipt is not None, "scope does not bind a verified historical acceptance receipt")
    inputs = tree.pins(scope["inputs"])
    context.require(inputs and not (set(inputs) & {
        projection, receipt_path, receipt["subject"]["path"], scope_name,
        *historical["requirement_sources"],
    }), "record at least one exact execution input distinct from the plan, receipt and requirement sources")
    for path, digest in inputs.items():
        context.require(context.digest(old.read(path)) == digest, f"historical execution input changed: {path}")

    capture_before = impact.capture(before, projection)
    capture_after = impact.capture(after, projection)
    context.require(capture_before["projection"] == historical["projection"]
                    and capture_after["projection"] == current["projection"],
                    "project changed during proof comparison")
    report = impact.compare(capture_before, capture_after,
                            context.digest(context.canonical(capture_before)),
                            context.digest(context.canonical(capture_after)))
    blockers = []
    affected = next((entry for entry in report["affected_tickets"] if entry["ticket_id"] == key), None)
    if affected:
        blockers.append({"reason": "affected-by-replan", "details": affected["reasons"]})
    if next_ticket is None or next_ticket["recorded_status"] != "accepted" or next_ticket.get("replan_retirement"):
        blockers.append({"reason": "historical-ticket-no-longer-current"})
    expected_subject = receipt["subject"]
    if next_ticket is not None and evidence_pins(old_ticket) != evidence_pins(next_ticket):
        blockers.append({"reason": "historical-ticket-evidence-changed"})
    checked = dict(inputs)
    add_evidence_checks(old_ticket, checked)
    add_prerequisite_checks(tickets_before, tickets_after, key, checked, blockers)
    for path, digest in sorted(checked.items()):
        try:
            actual = context.digest(live.read(path))
        except (OSError, context.ContextError):
            actual = None
        if actual != digest:
            blockers.append({"reason": "proof-input-drift", "path": path, "expected_sha256": digest,
                             "observed_sha256": actual})
    historical_receipts = {(item["path"], item["sha256"]) for item in old_ticket["evidence"]
                           if item["kind"] == "acceptance-receipt" and item["status"] == "verified"}
    if next_ticket is not None and any(
        item["status"] != "verified" and not (
            item["status"] == "binding-mismatch"
            and (item["path"], item["sha256"]) in historical_receipts
        ) for item in next_ticket["evidence"]
    ):
        blockers.append({"reason": "additional-current-evidence-needs-review"})
    if next_ticket is not None and not any(
        item["path"] == receipt_path and item["sha256"] == receipt_sha for item in next_ticket["evidence"]
    ):
        blockers.append({"reason": "historical-receipt-not-referenced-by-current-ticket"})
    old.verify_unchanged()
    live.verify_unchanged()
    return {
        "schema_version": ASSESSMENT,
        "status": "fresh-proof-required" if blockers else "eligible-for-independent-reuse-review",
        "project_id": current["project_id"], "ticket_id": key,
        "historical_revision": historical["native_revision"], "current_revision": current["native_revision"],
        "historical_scope": {"path": scope_name, "sha256": scope_sha256},
        "receipt": scope["receipt"], "proof_subject": expected_subject,
        "execution_inputs": inputs, "blockers": blockers,
        "proof_scope_completeness_verified": False,
        "current_acceptance_granted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before-root", type=Path, required=True)
    parser.add_argument("--after-root", type=Path, required=True)
    parser.add_argument("--projection", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--scope-sha256", required=True)
    args = parser.parse_args()
    try:
        result = assess(args.before_root, args.after_root, args.projection, args.scope, args.scope_sha256)
    except (context.ContextError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
