#!/usr/bin/env python3
"""Surface disagreements among pinned requirement registers before a replan."""

import argparse
from collections import defaultdict, deque
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree

context = ticket_tree.context
REQUEST = "atelier.ticket-spec-sources/1"
REVIEW = "atelier.ticket-spec-review/1"
CLAIM_FIELDS = (
    "verbatim", "interpretation", "acceptance", "priority", "applicable",
    "applicability_reason", "always_review", "dependencies", "owner", "due_gate",
)


def claims(snapshot, pins):
    grouped = defaultdict(list)
    for path, digest in pins.items():
        raw = snapshot.read(path)
        context.require(context.digest(raw) == digest, f"SOURCE_DRIFT: {path}")
        rows = context.native_rows(
            context.json_object(raw), ("requirements", "requirement_registry", "requirement")
        )
        context.require(rows, f"source has no requirements: {path}")
        known = set()
        for row in rows:
            normalized = context.normalize_requirement(row, {"path": path, "sha256": digest})
            ident = normalized["id"]
            context.require(ident not in known, f"duplicate requirement {ident} in {path}")
            known.add(ident)
            value = {key: normalized.get(key) for key in CLAIM_FIELDS}
            value["dependencies"] = sorted(value["dependencies"])
            grouped[ident].append({"source": {"path": path, "sha256": digest}, "claim": value})
        context.require(len(grouped) <= context.MAX_IDS, "too many requirement IDs")
    return grouped


def review(root, name):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    snapshot = ticket_tree.Snapshot(root)
    request_bytes = snapshot.read(name)
    request = context.json_object(request_bytes)
    names = {"schema_version", "project_id", "native_revision", "sources", "requirement_ids"}
    context.require(set(request) == names and request["schema_version"] == REQUEST,
                    "expected an exact requirements source review request")
    project = context.text(request, "project_id")
    revision = context.text(request, "native_revision")
    pinned = ticket_tree.pins(request["sources"])
    context.require(pinned and name not in pinned, "choose separate pinned requirements sources")
    records = claims(snapshot, pinned)
    selected = context.bounded_ids(request["requirement_ids"], "selected requirement IDs")
    seed = selected or sorted(records)
    queue, queued = deque(seed), set(seed)
    missing, disagreements, compared = [], [], []
    while queue:
        ident = queue.popleft()
        prior = records.get(ident)
        if not prior:
            missing.append(ident)
            continue
        compared.append(ident)
        fields = [key for key in CLAIM_FIELDS
                  if any(item["claim"][key] != prior[0]["claim"][key] for item in prior[1:])]
        if fields:
            disagreements.append({"requirement_id": ident, "differing_fields": fields, "sources": prior,
                                  "next": "review the exact source statements and record the decision"})
        for entry in prior:
            for dependency in entry["claim"]["dependencies"]:
                if dependency not in queued:
                    queued.add(dependency)
                    context.require(len(queued) <= context.MAX_IDS,
                                    "too many selected or dependency IDs")
                    queue.append(dependency)
    snapshot.verify_unchanged()
    return {
        "schema_version": REVIEW, "status": "decision-needed" if disagreements or missing else "compared",
        "request": {"path": name, "sha256": context.digest(request_bytes)},
        "project_id": project, "native_revision": revision, "requirement_ids_compared": compared,
        "missing_requirement_ids": missing, "disagreements": disagreements,
        "authority_authenticated": False, "semantic_equivalence_certified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    try:
        result = review(args.root, args.input)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "source-review-refused", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if args.require_clean and result["status"] != "compared" else 0


if __name__ == "__main__":
    sys.exit(main())
