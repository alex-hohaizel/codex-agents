#!/usr/bin/env python3
"""Read reviewed method catalogs and continue a project workshop by exact revision."""

import argparse
import csv
from html import escape
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree

context = tree.context
SCHEMA = "atelier.workshop/1"
CATALOGS = {
    ("category", "technique_name", "description", "detail", "provenance", "good_for", "audience"):
        ("brainstorm", "category", "technique_name", "detail"),
    ("num", "category", "method_name", "description", "output_pattern"):
        ("elicitation", "category", "method_name", "output_pattern"),
    ("num", "direction", "method_name", "description", "form", "tier", "aliases"):
        ("elicitation", "direction", "method_name", "form"),
}


def catalog(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    shape = CATALOGS.get(tuple(reader.fieldnames or ()))
    context.require(shape is not None, "unsupported catalog columns")
    kind, group, name, form = shape
    methods = {}
    for row in reader:
        context.require(len(methods) < 500 and all(isinstance(value, str) for value in row.values()),
                        "invalid method row or too many methods")
        title = context.text(row, name).strip()
        context.require(title not in methods, f"duplicate method: {title}")
        audience = row.get("audience", "either")
        context.require(audience in {"solo", "group", "either"}, f"invalid audience for {title}")
        methods[title] = {
            "name": title,
            "group": context.text(row, group).strip(),
            "description": context.text(row, "description"),
            "format": row[form],
            "audience": audience,
            "goals": list(filter(None, row.get("good_for", "").split("|"))),
            "tier": row.get("tier"),
            "aliases": row.get("aliases"),
        }
    context.require(methods, "empty catalog")
    return kind, methods


def pinned(snapshot, path, digest):
    raw = snapshot.read(path)
    context.require(context.digest(raw) == digest, f"source changed: {path}")
    return raw


def choices(methods, audience, goal):
    return [item for item in methods.values() if item["audience"] in {"either", audience}
            and (not goal or goal == item["group"] or goal in item["goals"])]


def text(row, key, limit=8000):
    value = context.text(row, key).strip()
    context.require(len(value) <= limit, f"value too long: {key}")
    return value


def check_revision(snapshot, item):
    fields = {"schema_version", "status", "mode", "goal", "audience", "limit", "catalog", "rounds", "evidence"}
    if "previous_sha256" in item:
        fields.add("previous_sha256")
        context.require(isinstance(item["previous_sha256"], str) and context.HASH.fullmatch(item["previous_sha256"]),
                        "invalid earlier revision digest")
    if item.get("status") == "decided":
        fields.update(("decided_by", "decisions"))
    context.require(set(item) == fields, "invalid workshop fields")
    context.require(item.get("schema_version") == SCHEMA and item.get("status") in {"open", "decided"},
                    "unsupported workshop")
    context.require(item.get("mode") in {"brainstorm", "pressure-test"}, "unsupported workshop mode")
    context.require(item.get("audience") in {"solo", "group"}, "unsupported audience")
    text(item, "goal")
    entry = item.get("catalog")
    tree.pins([entry])
    _, methods = catalog(pinned(snapshot, entry["path"], entry["sha256"]))
    for path, digest in tree.pins(item.get("evidence")).items():
        pinned(snapshot, path, digest)
    limit, rounds = item.get("limit"), item.get("rounds")
    context.require(type(limit) is int and 1 <= limit <= 30 and isinstance(rounds, list)
                    and len(rounds) <= limit, "invalid round budget")
    names = {}
    for row in rounds:
        context.require(isinstance(row, dict) and set(row) == {"method", "actor", "topic", "question", "response", "ideas"},
                        "invalid round")
        method = text(row, "method")
        context.require(method in methods and methods[method]["audience"] in {"either", item["audience"]},
                        "unknown or unsuitable round method")
        for field in ("actor", "topic", "question", "response"):
            text(row, field)
        for idea_id, idea in context.records(row, "ideas").items():
            context.require(set(idea) == {"id", "text"} and idea_id not in names and len(names) < 250,
                            f"invalid or duplicate idea: {idea_id}")
            names[idea_id] = text(idea, "text")
    if item["status"] == "decided":
        outcomes = context.records(item, "decisions")
        context.require(names and outcomes.keys() == names.keys(), "decide every recorded idea")
        for row in outcomes.values():
            context.require(set(row) == {"id", "outcome", "reason"} and row.get("outcome") in {"continue", "reframe", "drop"}, "invalid decision")
            text(row, "reason")
        text(item, "decided_by")


def render(item, kind):
    heading = "Workshop: " + item["goal"]
    rows = [("Status", item["status"]), ("Mode", item["mode"]), ("Audience", item["audience"])]
    rows.extend(("Evidence", p["path"] + " (" + p["sha256"] + ")") for p in item["evidence"])
    for i, row in enumerate(item["rounds"], 1):
        rows.extend([(f"Round {i}", row["topic"] + " · " + row["method"] + " · " + row["actor"]),
                     ("Question", row["question"]), ("Response", row["response"])])
        rows.extend((idea["id"], idea["text"]) for idea in row["ideas"])
    if item["status"] == "decided":
        rows.append(("Decision owner", item["decided_by"]))
        rows.extend((row["id"], row["outcome"] + " · " + row["reason"]) for row in item["decisions"])
    if kind == "html":
        return ('<!doctype html><html><meta charset="utf-8"><title>' + escape(heading) +
                '</title><h1>' + escape(heading) + '</h1><dl>' +
                "".join("<dt>" + escape(label) + "</dt><dd>" + escape(value) + "</dd>"
                        for label, value in rows) + "</dl></html>")
    return "# " + heading + "\n\n" + "\n\n".join("**" + label + "**\n\n" + value
                                                               for label, value in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("catalog", "start", "append", "decide", "report"):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True, type=Path)
        if name in {"catalog", "start"}:
            p.add_argument("--catalog", required=True)
            p.add_argument("--catalog-sha256", required=True)
            p.add_argument("--audience", choices=("solo", "group"), default="solo")
        if name == "catalog":
            p.add_argument("--goal")
        if name == "start":
            p.add_argument("--goal", required=True)
            p.add_argument("--mode", choices=("brainstorm", "pressure-test"), required=True)
            p.add_argument("--limit", type=int, default=8)
            p.add_argument("--evidence", action="append", default=[])
        if name in {"append", "decide", "report"}:
            p.add_argument("--state", required=True)
            p.add_argument("--state-sha256", required=True)
        if name in {"append", "decide"}:
            p.add_argument("--record", required=True)
        if name == "report":
            p.add_argument("--format", choices=("markdown", "html"), required=True)
    args = parser.parse_args()
    snapshot = tree.Snapshot(args.root.resolve())
    try:
        if args.command == "catalog":
            source = {"path": args.catalog, "sha256": args.catalog_sha256}
            kind, methods = catalog(pinned(snapshot, args.catalog, args.catalog_sha256))
            output = {"kind": kind, "source": source, "total": len(methods),
                      "groups": sorted({row["group"] for row in methods.values()}),
                      "methods": choices(methods, args.audience, args.goal)}
        elif args.command == "start":
            output = {"schema_version": SCHEMA, "status": "open", "mode": args.mode,
                      "goal": args.goal, "audience": args.audience, "limit": args.limit,
                      "catalog": {"path": args.catalog, "sha256": args.catalog_sha256}, "rounds": [],
                      "evidence": [{"path": path, "sha256": context.digest(snapshot.read(path))}
                                   for path in args.evidence]}
            check_revision(snapshot, output)
        else:
            state = context.json_object(pinned(snapshot, args.state, args.state_sha256))
            check_revision(snapshot, state)
            if args.command == "report":
                output = render(state, args.format)
            else:
                context.require(state["status"] == "open", "workshop already decided")
                item = context.json_object(snapshot.read(args.record))
                output = {**state, "previous_sha256": args.state_sha256}
                if args.command == "append":
                    context.require(set(item) == {"method", "actor", "topic", "question", "response", "ideas"},
                                    "invalid round fields")
                    output["rounds"] = [*state["rounds"], item]
                else:
                    context.require(set(item) == {"decided_by", "decisions"}, "invalid decision fields")
                    output.update(item, status="decided")
                check_revision(snapshot, output)
        snapshot.verify_unchanged()
        print(output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, csv.Error, KeyError) as error:
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
