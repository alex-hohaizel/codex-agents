#!/usr/bin/env python3
"""Trace selected project requirements to scoped evidence and review a candidate."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree
from production_choice_route import CORE_REQUIREMENTS, ChoiceError, verify_route

context = tree.context
PLAN = "atelier.ticket-quality-plan/1"
REVIEW = "atelier.ticket-quality-review/1"
REPORT = "atelier.ticket-quality-gate/1"
PRIORITIES = {"P0", "P1", "P2", "P3"}


def exact_fields(row, fields, label):
    context.require(isinstance(row, dict) and set(row) == set(fields),
                    f"invalid {label} fields")


def read_record(snapshot, name, expected):
    raw = snapshot.read(name)
    context.require(context.digest(raw) == expected, f"SOURCE_DRIFT: {name}")
    return context.json_object(raw)


def verify_pins(snapshot, pins, excluded, *, allow_stale=False):
    checked = []
    excluded_digests = set(excluded.values())
    for path, expected in tree.pins(pins).items():
        context.require(path not in excluded and expected not in excluded_digests,
                        f"record aliases an input instead of supplying proof: {path}")
        try:
            observed = context.digest(snapshot.read(path))
        except (context.ContextError, OSError):
            if not allow_stale:
                raise
            observed = None
        if not allow_stale:
            context.require(observed == expected, f"SOURCE_DRIFT: {path}")
        checked.append({"path": path, "sha256": expected, "current": observed == expected})
    return checked


def project_scope(board, selectors):
    sprint = tree.select_sprint(board, selectors)
    tickets = {row["id"]: row for row in board["tickets"]}
    leaves = {row["id"]: row for row in sprint["tickets"]}
    groups = set()
    pending = [key for key in selectors if tickets[key]["kind"] in tree.GROUPS]
    while pending:
        key = pending.pop()
        if key in groups:
            continue
        groups.add(key)
        pending.extend(child for child in tickets[key]["children"]
                       if tickets[child]["kind"] in tree.GROUPS)

    scoped = {}
    for key in board["evaluation_order"]:
        row = tickets[key]
        if key not in leaves and (key not in groups or not (row["requirement_ids"] or row["acceptance"])):
            continue
        context.require(row["board_state"] != "deferred" and not row.get("replan_retirement"),
                        f"deferred or retired ticket in gate scope: {key}")
        context.require(row["acceptance"] and row["requirement_ids"],
                        f"ticket has no explicit acceptance and requirements: {key}")
        if key in leaves:
            prerequisites = leaves[key]["prerequisites"]
        else:
            prerequisites = [
                {"ticket": dep, "scope": "inside" if dep in leaves or dep in groups else "outside",
                 "satisfied": tickets[dep]["execution_disposition"] == "satisfied"}
                for dep in row["effective_prerequisites"]
            ]
        scoped[key] = {
            "acceptance": row["acceptance"],
            "requirement_ids": row["requirement_closure"],
            "prerequisites": prerequisites,
            "recorded_holds": [item for item in row["blockers"]
                               if item["code"] in {"ancestor-blocked", "ancestor-deferred", "recorded-block"}],
        }
    return scoped


def read_checks(plan, scoped):
    checks = context.records(plan, "checks")
    context.require(0 < len(checks) <= 100, "expected 1 to 100 checks")
    context.bounded_ids(list(checks), "quality check IDs")
    for key, row in checks.items():
        exact_fields(row, ("id", "ticket_id", "requirement_ids", "priority",
                           "risk", "procedure", "expected"), f"check {key}")
        ticket_id = context.text(row, "ticket_id")
        context.require(ticket_id in scoped, f"check outside selected tickets: {key}")
        ids = context.bounded_ids(row["requirement_ids"], f"check requirements: {key}")
        context.require(ids and set(ids) <= set(scoped[ticket_id]["requirement_ids"]),
                        f"check requirements outside ticket scope: {key}")
        context.require(context.text(row, "priority") in PRIORITIES, f"invalid check risk: {key}")
        for field in ("risk", "procedure", "expected"):
            context.text(row, field)
    return checks


def parse_date(value):
    context.require(isinstance(value, str), "expected date YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise context.ContextError("expected date YYYY-MM-DD") from error
    context.require(parsed.isoformat() == value, "expected date YYYY-MM-DD")
    return parsed


def read_results(snapshot, record, plan_sha, producer, checks, excluded, as_of):
    exact_fields(record, ("schema_version", "plan_sha256", "reviewer", "results"), "quality review")
    context.require(record["schema_version"] == REVIEW and record["plan_sha256"] == plan_sha,
                    "quality review is for different plan bytes")
    reviewer = context.text(record, "reviewer")
    context.require(reviewer.strip() == reviewer and reviewer.casefold() != producer.casefold(),
                    "quality reviewer must be distinct from the candidate producer")
    results = context.records(record, "results")
    context.require(set(results) <= set(checks), "review contains a check outside the plan")
    for key, result in results.items():
        fields = {"id", "outcome", "observation", "artifacts"}
        context.require(set(result) in (fields, fields | {"waiver"}), f"invalid review result: {key}")
        outcome = context.text(result, "outcome")
        context.require(outcome in {"pass", "fail", "unobserved", "unknown-effect"},
                        f"unsupported outcome: {key}")
        context.text(result, "observation")
        artifacts = verify_pins(snapshot, result["artifacts"], excluded, allow_stale=True)
        if outcome in {"pass", "fail"}:
            context.require(artifacts, f"observed result needs an artifact: {key}")
        result["artifacts"] = artifacts
        waiver = result.get("waiver")
        if waiver is not None:
            context.require(not CORE_REQUIREMENTS.intersection(checks[key]["requirement_ids"]),
                            f"required production choice checks cannot be waived: {key}")
            exact_fields(waiver, ("by", "reason", "expires_on", "decision"), "waiver")
            by = context.text(waiver, "by")
            context.require(by.strip() == by and by.casefold() not in {
                producer.casefold(), reviewer.casefold(),
            }, f"waiver needs a separate recorded decision owner: {key}")
            context.text(waiver, "reason")
            context.require(outcome == "fail" and checks[key]["priority"] != "P0",
                            f"only a known non-P0 failure can be waived: {key}")
            authority = verify_pins(snapshot, [waiver["decision"]], excluded, allow_stale=True)[0]
            context.require(authority["path"] not in {pin["path"] for pin in artifacts},
                            f"waiver decision must be separate from check evidence: {key}")
            result["waiver_current"] = authority["current"] and parse_date(waiver["expires_on"]) >= as_of
    return reviewer, results


def disposition(result):
    if result is None:
        return "unobserved"
    if any(not artifact["current"] for artifact in result["artifacts"]):
        return "stale-evidence"
    outcome = result["outcome"]
    if outcome == "fail" and result.get("waiver_current"):
        return "waived"
    return outcome


def classify(rows, gaps, upstream_holds):
    if any(row["disposition"] == "fail" for row in rows):
        return "FAIL"
    if gaps or upstream_holds or any(
        row["disposition"] not in {"pass", "waived"} for row in rows
    ):
        return "CONCERNS"
    return "WAIVED" if any(row["disposition"] == "waived" for row in rows) else "PASS"


def evaluate(root, projection, plan_name, plan_sha, review_name=None, review_sha=None, *, as_of):
    production = verify_route(Path(root), "accept" if review_name is not None else "implement")
    snapshot = tree.Snapshot(root)
    board = tree.project_board(root, projection, snapshot=snapshot)
    plan = read_record(snapshot, plan_name, plan_sha)
    identity = {key: board[key] for key in ("project_id", "native_revision")}
    expected = {**identity, "schema_version": PLAN, "projection_sha256": board["projection"]["sha256"]}
    exact_fields(plan, {*expected, "select", "producer", "subject", "checks"}, "quality plan")
    context.require(all(plan[k] == value for k, value in expected.items()),
                    "quality plan is for a different project projection")
    producer = context.text(plan, "producer")
    context.require(producer.strip() == producer, "invalid producer identity")
    excluded = {**board["requirement_sources"], projection: board["projection"]["sha256"],
                plan_name: plan_sha}
    if review_name is not None:
        excluded[review_name] = review_sha
    subject = verify_pins(snapshot, plan["subject"], excluded)
    context.require(subject, "quality plan needs at least one pinned candidate input")
    excluded.update((pin["path"], pin["sha256"]) for pin in subject)
    scoped = project_scope(board, plan["select"])
    checks = read_checks(plan, scoped)
    reviewer, results = None, {}
    if review_name is not None:
        context.require(review_name != plan_name and review_sha is not None,
                        "quality review requires a distinct reviewed record and digest")
        review = read_record(snapshot, review_name, review_sha)
        reviewer, results = read_results(snapshot, review, plan_sha, producer, checks, excluded, as_of)
    trace = {(ticket_id, requirement_id): [] for ticket_id, ticket in scoped.items()
             for requirement_id in ticket["requirement_ids"]}
    rows = []
    for key, check in checks.items():
        result = results.get(key)
        rows.append({**check, "disposition": disposition(result), "review": result})
        for requirement_id in check["requirement_ids"]:
            trace[(check["ticket_id"], requirement_id)].append(key)
    gaps = [{"ticket_id": ticket_id, "requirement_id": requirement_id}
            for (ticket_id, requirement_id), ids in trace.items() if not ids]
    upstream_holds = []
    for ticket_id, ticket in scoped.items():
        missing = [item["ticket"] for item in ticket["prerequisites"]
                   if item["scope"] == "outside" and not item["satisfied"]]
        if missing or ticket["recorded_holds"]:
            upstream_holds.append({
                "ticket_id": ticket_id, "unsatisfied_prerequisites": missing,
                "recorded_holds": ticket["recorded_holds"],
            })
    requirement_sources = {row["id"]: row for row in board["requirements"]}
    snapshot.verify_unchanged()
    return {
        "schema_version": REPORT, **identity, "projection": board["projection"], "subject": subject,
        "plan": {"path": plan_name, "sha256": plan_sha},
        "review": {"path": review_name, "sha256": review_sha} if reviewer else None,
        "reviewer": reviewer, "evaluated_on": as_of.isoformat(),
        "gate": classify(rows, gaps, upstream_holds), "selected_tickets": scoped,
        "trace": [{"ticket_id": t, "requirement_id": r, "check_ids": ids,
                   "source": requirement_sources[r]}
                  for (t, r), ids in trace.items()],
        "unmapped": gaps, "upstream_holds": upstream_holds, "checks": rows,
        "review_identity_authenticated": False, "release_authorized": False,
        **({"production_choice": production} if production else {}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--projection", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--review")
    parser.add_argument("--review-sha256")
    parser.add_argument("--as-of", help="evaluation date YYYY-MM-DD, defaults to today")
    parser.add_argument("--require-pass", action="store_true", help="exit 3 unless the gate is PASS")
    args = parser.parse_args()
    if bool(args.review) != bool(args.review_sha256):
        parser.error("--review and --review-sha256 are required together")
    try:
        result = evaluate(args.root, args.projection, args.plan, args.plan_sha256,
                          args.review, args.review_sha256,
                          as_of=parse_date(args.as_of) if args.as_of else date.today())
    except (context.ContextError, ChoiceError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 3 if args.require_pass and result["gate"] != "PASS" else 0


if __name__ == "__main__":
    sys.exit(main())
