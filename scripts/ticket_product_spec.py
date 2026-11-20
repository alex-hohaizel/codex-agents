#!/usr/bin/env python3
"""Capture, compare, and review a source-bound PRD and architecture companion."""

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_spec_review as spec_review
import ticket_tree as tree
from production_choice_route import RECORD, verify_route

context = tree.context
MANIFEST = "atelier.ticket-product-spec-manifest/1"
CAPTURE = "atelier.ticket-product-spec-capture/1"
COMPARE = "atelier.ticket-product-spec-comparison/1"
REVIEW = "atelier.ticket-product-spec-review/1"
ROLES = ("prd", "architecture")


def exact_fields(record, fields, label):
    context.require(isinstance(record, dict) and set(record) == set(fields),
                    f"invalid {label} fields")


def digest(record):
    return context.digest(context.canonical(record))


def checked_text(record, field, limit=8000):
    value = context.text(record, field)
    context.require(len(value) <= limit and value.strip() == value,
                    f"out-of-bounds text: {field}")
    return value


def pin_bytes(snapshot, path, expected):
    raw = snapshot.read(path)
    context.require(context.digest(raw) == expected, f"SOURCE_DRIFT: {path}")
    return raw


def read_pins(snapshot, value):
    return {path: (sha, pin_bytes(snapshot, path, sha))
            for path, sha in tree.pins(value).items()}


def decision_rows(snapshot, pins):
    rows = []
    for path, (sha, raw) in read_pins(snapshot, pins).items():
        current = context.native_rows(context.json_object(raw), ("decisions", "decision"))
        context.require(current, f"empty decision register: {path}")
        for item in current:
            checked_text(item, "id", 240)
            rows.append({**item, "source_ref": path, "source_sha256": sha})
        context.require(len(rows) <= context.MAX_IDS, "too many decision records")
    reconciliation = context.reconcile_decisions(rows)
    context.require(not reconciliation["issues"], "ambiguous decision corrections")
    return {item["id"]: item for item in reconciliation["current_decisions"]}


def documents(snapshot, value):
    context.require(isinstance(value, dict) and set(value) == set(ROLES),
                    "expected exact PRD and architecture companions")
    pins = read_pins(snapshot, list(value.values()))
    texts = {}
    for role in ROLES:
        path = value[role]["path"]
        context.require(Path(path).suffix.lower() == ".md", f"{role} must be editable Markdown")
        texts[role] = pins[path][1].decode("utf-8")
    return texts


def claims_from_alternatives(snapshot, pins, requirements, selected):
    by_id = spec_review.claims(snapshot, pins)
    for ident in selected:
        official = requirements[ident]
        for item in by_id.get(ident, ()):
            context.require(all(
                item["claim"][field] == (
                    sorted(official[field]) if field == "dependencies" else official.get(field)
                ) for field in spec_review.CLAIM_FIELDS
            ), f"requirement {ident} disagrees with {item['source']['path']}; resolve source claims")


def coverage_rows(request, requirements, sources, choices, texts):
    rows = context.records(request, "coverage")
    required = {
        ident for ident, row in requirements.items()
        if row["applicable"] and (row["priority"] == "must" or row["always_review"])
    }
    selected = tree.requirement_closure(sorted(required | rows.keys()), requirements, "product spec")
    missing = sorted(set(selected) - rows.keys())
    context.require(selected and not missing, f"missing mandatory or dependent coverage: {', '.join(missing)}")

    coverage = {}
    for ident in selected:
        row, requirement = rows[ident], requirements[ident]
        exact_fields(row, {"id", "source_path", "source_excerpt", "decision_ids",
                           "prd_excerpt", "architecture_excerpt"}, f"coverage {ident}")
        path = checked_text(row, "source_path", 4096)
        excerpt = checked_text(row, "source_excerpt")
        context.require(path in sources, f"unpinned raw source for {ident}")
        context.require(excerpt in sources[path][1].decode("utf-8")
                        and excerpt in requirement["verbatim"],
                        f"raw quotation does not match the native requirement: {ident}")
        acceptance = requirement["raw_native_record"]
        context.require(acceptance.get("acceptance") or acceptance.get("acceptance_criteria"),
                        f"missing explicit native acceptance criterion: {ident}")
        for role in ROLES:
            quote = checked_text(row, f"{role}_excerpt")
            context.require(quote in texts[role], f"{role} omits cited criterion: {ident}")
        decision_ids = context.bounded_ids(row["decision_ids"], f"decision IDs for {ident}")
        context.require(set(decision_ids) <= choices.keys(),
                        f"unknown or superseded decision for {ident}")
        coverage[ident] = {
            **{key: row[key] for key in ("id", "source_path", "source_excerpt",
                                         "prd_excerpt", "architecture_excerpt", "decision_ids")},
            "source_sha256": sources[path][0],
            "requirement_sha256": digest(requirement["raw_native_record"]),
            "acceptance": requirement["acceptance"],
            "dependencies": requirement["dependencies"],
            "decision_sha256": {
                key: digest({field: value for field, value in choices[key].items()
                             if field != "source_sha256"}) for key in decision_ids
            },
        }
    return coverage


def collect(root, projection, name, snapshot):
    board = tree.project_board(root, projection, snapshot=snapshot)
    raw = snapshot.read(name)
    request = context.json_object(raw)
    exact_fields(request, {"schema_version", "project_id", "native_revision", "projection_sha256",
                           "author", "documents", "sources", "decision_sources", "comparison_sources",
                           "coverage"}, "product specification manifest")
    context.require(request["schema_version"] == MANIFEST, "unsupported spec manifest schema")
    context.require(all(request[field] == board[field] for field in ("project_id", "native_revision"))
                    and request["projection_sha256"] == board["projection"]["sha256"],
                    "product specification targets a different native projection")
    sources = read_pins(snapshot, request["sources"])
    production = verify_route(Path(root), "explore", required=RECORD in sources)
    if production:
        context.require(RECORD in sources and
                        context.digest(snapshot.read(RECORD)) == production["record_sha256"],
                        "The product specification must include its current production choice among its source pins")
    requirements = tree.read_requirements(snapshot, board["requirement_sources"])
    choices = decision_rows(snapshot, request["decision_sources"])
    texts = documents(snapshot, request["documents"])
    alternatives = tree.pins(request["comparison_sources"])
    input_paths = {name, projection, *sources, *board["requirement_sources"],
                   *tree.pins(request["decision_sources"]), *alternatives}
    input_hashes = {context.digest(snapshot.read(path)) for path in input_paths}
    for role, pin in request["documents"].items():
        context.require(pin["path"] not in input_paths and pin["sha256"] not in input_hashes,
                        f"{role} aliases an input instead of being a separate companion")
    context.require(request["documents"]["prd"]["sha256"] != request["documents"]["architecture"]["sha256"],
                    "PRD and architecture must be distinct documents")
    coverage = coverage_rows(request, requirements, sources, choices, texts)
    claims_from_alternatives(snapshot, alternatives, requirements, coverage)
    ticket_requirements = {item["id"]: item["requirement_closure"] for item in board["tickets"]}
    payload = {
        "schema_version": CAPTURE,
        "project_id": board["project_id"],
        "native_revision": board["native_revision"],
        "projection": board["projection"],
        "manifest": {"path": name, "sha256": context.digest(raw)},
        "author": checked_text(request, "author", 240),
        "documents": request["documents"],
        "coverage": coverage,
        "ticket_requirements": ticket_requirements,
    }
    return {**payload, "bundle_sha256": digest(payload)}


def load_history(path, expected):
    context.require(path.is_absolute() and path.resolve() == path,
                    "prior capture needs a canonical absolute file path")
    raw = context.bound_bytes(path.parent, path.name)
    context.require(context.digest(raw) == expected, "prior capture bytes changed")
    old = context.json_object(raw)
    exact_fields(old, {"schema_version", "project_id", "native_revision", "projection", "manifest",
                       "author", "documents", "coverage", "ticket_requirements", "bundle_sha256"},
                 "historical capture")
    fingerprint = old.pop("bundle_sha256")
    context.require(old["schema_version"] == CAPTURE and digest(old) == fingerprint,
                    "not an exact product specification capture")
    context.require(isinstance(old["documents"], dict) and set(old["documents"]) == set(ROLES),
                    "invalid historical companions")
    tree.pins(list(old["documents"].values()))
    context.require(all(isinstance(old[field], dict) for field in ("coverage", "ticket_requirements")),
                    "invalid historical coverage")
    for ident, row in old["coverage"].items():
        context.require(isinstance(row, dict) and row.get("id") == ident,
                        "invalid historical requirement")
        context.bounded_ids(row.get("dependencies"), f"historical requirements for {ident}")
    for ids in old["ticket_requirements"].values():
        context.bounded_ids(ids, "historical ticket requirement IDs")
    return {**old, "bundle_sha256": fingerprint}


def compare(old, new):
    context.require(old["project_id"] == new["project_id"]
                    and old["native_revision"] != new["native_revision"],
                    "expected a prior revision of the same project")
    before, after = old["coverage"], new["coverage"]
    changes = {}
    for ident in sorted(before.keys() | after.keys()):
        if ident not in before:
            changes[ident] = ["added"]
        elif ident not in after:
            changes[ident] = ["removed"]
        else:
            fields = sorted(key for key, value in after[ident].items()
                            if before[ident].get(key) != value)
            if fields:
                changes[ident] = fields
    affected = set(changes)
    requirements = {**before, **after}
    while True:
        more = {ident for ident, row in requirements.items() if set(row["dependencies"]) & affected}
        if more <= affected:
            break
        affected.update(more)
    tickets = {ticket for spec in (old, new) for ticket, ids in spec["ticket_requirements"].items()
               if set(ids) & affected}
    old_links, new_links = old["ticket_requirements"], new["ticket_requirements"]
    link_changes = {}
    for ticket in sorted(old_links.keys() | new_links.keys()):
        previous = sorted(old_links.get(ticket, []))
        current = sorted(new_links.get(ticket, []))
        if previous != current:
            link_changes[ticket] = {"before": previous, "after": current}
    return {
        "schema_version": COMPARE,
        "project_id": new["project_id"],
        "before_bundle_sha256": old["bundle_sha256"],
        "after_bundle_sha256": new["bundle_sha256"],
        "before_revision": old["native_revision"],
        "after_revision": new["native_revision"],
        "changed_fields_by_requirement": changes,
        "affected_requirement_ids": sorted(affected),
        "affected_ticket_ids": sorted(tickets | link_changes.keys()),
        "changed_ticket_requirement_links": link_changes,
        "changed_documents": [role for role in ROLES if old["documents"][role] != new["documents"][role]],
        "previous_review_applies": False,
    }


def review(current, record):
    exact_fields(record, {"schema_version", "bundle_sha256", "reviewer", "checks", "verdict", "summary"},
                 "product specification review")
    context.require(record["schema_version"] == REVIEW
                    and record["bundle_sha256"] == current["bundle_sha256"],
                    "review belongs to a different specification bundle")
    reviewer = checked_text(record, "reviewer", 240)
    context.require(reviewer.casefold() != current["author"].casefold(),
                    "reviewer must differ from the author")
    verdict = checked_text(record, "verdict", 32)
    context.require(verdict in {"approve", "changes-requested"}, "invalid review verdict")
    summary = checked_text(record, "summary")
    checks = context.records(record, "checks")
    context.require(checks.keys() == current["coverage"].keys(),
                    "review must address all captured criteria")
    for ident, row in checks.items():
        exact_fields(row, {"id", "outcome", "observation"}, f"review criterion {ident}")
        context.require(row["outcome"] in ("matches", "needs-change"),
                        f"invalid review criterion outcome: {ident}")
        checked_text(row, "observation")
    matches = all(item["outcome"] == "matches" for item in checks.values())
    context.require(verdict != "approve" or matches, "approval contradicts an open review finding")
    return {"status": "reviewed" if verdict == "approve" else "changes-requested",
            "project_id": current["project_id"], "native_revision": current["native_revision"],
            "bundle_sha256": current["bundle_sha256"], "reviewer": reviewer,
            "checks": checks, "summary": summary, "reviewer_identity_authenticated": False,
            "owner_acceptance_authenticated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    for mode in ("capture", "compare", "review"):
        sub = subparsers.add_parser(mode)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--projection", required=True)
        sub.add_argument("--input", required=True)
        if mode == "compare":
            sub.add_argument("--before", required=True, type=Path)
            sub.add_argument("--before-sha256", required=True)
        if mode == "review":
            sub.add_argument("--review", required=True)
            sub.add_argument("--review-sha256", required=True)
    args = parser.parse_args()
    try:
        snapshot = tree.Snapshot(args.root)
        current = collect(args.root, args.projection, args.input, snapshot)
        result = current
        if args.mode == "compare":
            result = compare(load_history(args.before, args.before_sha256), current)
        if args.mode == "review":
            raw = pin_bytes(snapshot, args.review, args.review_sha256)
            result = review(current, context.json_object(raw))
        snapshot.verify_unchanged()
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 3 if result.get("status") == "changes-requested" else 0


if __name__ == "__main__":
    sys.exit(main())
