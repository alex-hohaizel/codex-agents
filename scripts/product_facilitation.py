#!/usr/bin/env python3
"""Prepare or review a source-bound product brief, PRFAQ, or UX workshop."""

import argparse
from html import escape
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import ticket_product_spec as spec
import ticket_tree as tree

context = tree.context
REQUEST = "atelier.product-facilitation/1"
DRAFT = "atelier.product-facilitation-draft/1"
REVIEW = "atelier.product-facilitation-review/1"
ROUTES = {
    "brief": {
        "BRIEF": (("need", "Need and audience"), ("current", "Current workflow"),
                  ("outcome", "Proposed outcome and measures"), ("bounds", "Scope and exclusions")),
    },
    "prfaq": {
        "PRFAQ": (("release", "Draft press release"), ("customer", "Customer FAQ"),
                  ("stakeholder", "Stakeholder FAQ")),
    },
    "ux": {
        "DESIGN": (("visual", "Visual direction and existing design"), ("components", "Components")),
        "EXPERIENCE": (("journey", "Key journey"), ("states", "Error and recovery states"),
                       ("accessibility", "Accessibility"), ("acceptance", "Acceptance and prototype plan")),
    },
}


def notes(snapshot, request):
    sources = spec.read_pins(snapshot, request["sources"])
    texts = {path: raw.decode("utf-8") for path, (_, raw) in sources.items()}
    records = context.records(request, "notes")
    context.require(0 < len(records) <= 80, "expected 1 to 80 source notes")
    result = {}
    for ident, row in records.items():
        spec.exact_fields(row, {"id", "source_path", "speaker", "excerpt"}, f"note {ident}")
        spec.checked_text(row, "id", 240)
        spec.checked_text(row, "speaker", 240)
        path = spec.checked_text(row, "source_path", 4096)
        excerpt = spec.checked_text(row, "excerpt")
        context.require(path in texts, f"unpinned source for note: {ident}")
        source = texts[path]
        start = source.find(excerpt)
        context.require(start >= 0 and source.find(excerpt, start + 1) == -1,
                        f"note excerpt is missing or ambiguous: {ident}")
        first_line = source.count("\n", 0, start) + 1
        observed = {
            **row, "sha256": sources[path][0], "first_line": first_line,
            "last_line": first_line + excerpt.count("\n"),
        }
        result[ident] = {**observed, "binding_sha256": spec.digest(observed)}
    return result


def questions(request, decisions, selected, source_notes, board):
    rows = context.records(request, "questions")
    context.require(len(rows) <= 40, "expected at most 40 questions")
    result = []
    by_question = {}
    for decision in decisions.values():
        ident = decision.get("question_id")
        if isinstance(ident, str) and ident in rows:
            context.require(ident not in by_question,
                            f"multiple current decisions for question: {ident}")
            by_question[ident] = decision
    for ident, row in rows.items():
        spec.exact_fields(row, {"id", "prompt", "owner", "needed_by", "positions", "blocks"},
                          f"question {ident}")
        for key, limit in (("id", 240), ("prompt", 1200), ("owner", 240), ("needed_by", 240)):
            spec.checked_text(row, key, limit)
        positions = context.bounded_ids(row["positions"], f"positions for {ident}")
        context.require(set(positions) <= source_notes.keys(), f"unknown position for {ident}")
        blocks = context.bounded_ids(row["blocks"], f"blocked requirements for {ident}")
        context.require(set(blocks) <= selected, f"unexpected blocked requirement for {ident}")
        question_sha = spec.digest(row)
        decision = by_question.get(ident)
        resolution = None
        if decision is not None:
            choice = spec.checked_text(decision, "selected_note_id", 240)
            context.require(choice in positions, f"decision selects an unsupported position: {ident}")
            current_positions = {note_id: source_notes[note_id]["binding_sha256"]
                                 for note_id in positions}
            context.require(decision.get("question_sha256") == question_sha
                            and decision.get("position_sha256") == current_positions,
                            f"decision needs renewed review for changed question or evidence: {ident}")
            resolution = {
                "decision_id": decision["id"], "selected_note_id": choice,
                "position_sha256": current_positions,
                "source": {"path": decision["source_ref"], "sha256": decision["source_sha256"]},
            }
        affected_tickets = sorted(
            ticket["id"] for ticket in board["tickets"]
            if set(ticket["requirement_closure"]) & set(blocks)
        )
        result.append({**row, "question_sha256": question_sha, "resolution": resolution,
                       "affected_ticket_ids": affected_tickets})
    return result


def content(request, layout, source_notes):
    sections = request["sections"]
    context.require(isinstance(sections, dict), "expected section content object")
    required = {section for groups in layout.values() for section, _ in groups}
    context.require(sections.keys() == required, "missing or unknown route section")
    for key, entries in sections.items():
        context.require(isinstance(entries, list) and 0 < len(entries) <= 10,
                        f"section needs 1 to 10 entries: {key}")
        for entry in entries:
            spec.exact_fields(entry, {"heading", "body", "source_notes"}, f"entry in {key}")
            spec.checked_text(entry, "heading", 300)
            spec.checked_text(entry, "body", 8000)
            references = context.bounded_ids(entry["source_notes"], f"entry notes for {key}")
            context.require(references and set(references) <= source_notes.keys(),
                            f"entry needs known source notes: {key}")
    return sections


def evidence_text(note):
    line = str(note["first_line"])
    if note["last_line"] != note["first_line"]:
        line += f"–{note['last_line']}"
    return f"{note['id']} · {note['speaker']} · {note['source_path']}:{line}"


def question_lines(row):
    text = [f"{row['id']} · {row['prompt']}",
            f"Owner: {row['owner']}. Needed by: {row['needed_by']}."]
    if row["positions"]:
        text.append("Recorded positions: " + ", ".join(row["positions"]) + ".")
    if row["blocks"]:
        text.append("Affected requirements: " + ", ".join(row["blocks"]) + ".")
    if row["affected_ticket_ids"]:
        text.append("Affected tickets: " + ", ".join(row["affected_ticket_ids"]) + ".")
    resolved = row["resolution"]
    if resolved:
        text.append(f"Recorded decision: {resolved['decision_id']} selects {resolved['selected_note_id']}.")
    else:
        text.append("Open blocking question." if row["blocks"] else "Open question.")
    return text


def as_markdown(title, document, groups, sections, source_notes, issues, held):
    lines = [f"# {title} · {document}", "", "Draft for review."]
    if held:
        lines.append("Blocking questions remain open.")
    if document == "PRFAQ":
        lines.append("The press release is a proposal for discussion.")
    used = set()
    for key, heading in groups:
        lines.extend(("", f"## {heading}"))
        for entry in sections[key]:
            used.update(entry["source_notes"])
            lines.extend(("", f"### {entry['heading']}", "", entry["body"], "",
                          "Sources: " + ", ".join(entry["source_notes"]) + "."))
    if issues:
        lines.extend(("", "## Questions and decisions"))
        for row in issues:
            used.update(row["positions"])
            first, *rest = question_lines(row)
            lines.extend(("", f"### {first}", "", *rest))
    lines.extend(("", "## Source excerpts"))
    for ident in source_notes:
        if ident in used:
            note = source_notes[ident]
            lines.extend(("", f"### {evidence_text(note)}", "",
                          *["> " + escape(line, quote=False) for line in note["excerpt"].splitlines()]))
    return "\n".join(lines) + "\n"


def paragraphs(text):
    return "".join(f"<p>{escape(part).replace(chr(10), '<br>')}</p>"
                   for part in text.split("\n\n") if part)


def as_html(title, document, groups, sections, source_notes, issues, held):
    name = f"{title} · {document}"
    parts = ["<!doctype html>",
             '<html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>{escape(name)}</title>",
             "<style>body{max-width:70ch;margin:2rem auto;padding:0 1rem;font:1rem/1.6 system-ui}"
             "h1,h2,h3{line-height:1.25}blockquote{margin-left:0;padding-left:1rem;"
             "border-left:.2rem solid currentColor}</style></head><body><main>",
             f"<h1>{escape(name)}</h1>", "<p>Draft for review.</p>"]
    if held:
        parts.append("<p>Blocking questions remain open.</p>")
    if document == "PRFAQ":
        parts.append("<p>The press release is a proposal for discussion.</p>")
    used = set()
    for key, heading in groups:
        parts.append(f"<section><h2>{escape(heading)}</h2>")
        for entry in sections[key]:
            used.update(entry["source_notes"])
            parts.append(f"<h3>{escape(entry['heading'])}</h3>")
            parts.append(paragraphs(entry["body"]))
            parts.append("<p>Sources: " + escape(", ".join(entry["source_notes"])) + ".</p>")
        parts.append("</section>")
    if issues:
        parts.append("<section><h2>Questions and decisions</h2>")
        for row in issues:
            used.update(row["positions"])
            first, *rest = question_lines(row)
            parts.append(f"<h3>{escape(first)}</h3>")
            parts.append(paragraphs("\n\n".join(rest)))
        parts.append("</section>")
    parts.append("<section><h2>Source excerpts</h2>")
    for ident in source_notes:
        if ident in used:
            note = source_notes[ident]
            parts.append(f"<h3>{escape(evidence_text(note))}</h3>")
            parts.append(f"<blockquote>{paragraphs(note['excerpt'])}</blockquote>")
    parts.append("</section></main></body></html>")
    return "\n".join(parts) + "\n"


def draft(root, projection, name, snapshot):
    board = tree.project_board(root, projection, snapshot=snapshot)
    raw = snapshot.read(name)
    request = context.json_object(raw)
    spec.exact_fields(request, {
        "schema_version", "project_id", "native_revision", "projection_sha256", "author",
        "route", "title", "sources", "decision_sources", "requirement_ids", "notes",
        "questions", "sections",
    }, "facilitation request")
    context.require(request["schema_version"] == REQUEST, "unsupported facilitation schema")
    context.require(all(request[key] == board[key] for key in ("project_id", "native_revision"))
                    and request["projection_sha256"] == board["projection"]["sha256"],
                    "facilitation targets a different project projection")
    route = spec.checked_text(request, "route", 32)
    context.require(route in ROUTES, "unsupported facilitation route")
    layout = ROUTES[route]
    title = spec.checked_text(request, "title", 300)
    author = spec.checked_text(request, "author", 240)
    requirements = tree.read_requirements(snapshot, board["requirement_sources"])
    requested = context.bounded_ids(request["requirement_ids"], "facilitation requirement IDs")
    selected = tree.requirement_closure(requested, requirements, "facilitation")
    source_notes = notes(snapshot, request)
    decisions = spec.decision_rows(snapshot, request["decision_sources"])
    issues = questions(request, decisions, set(selected), source_notes, board)
    held = [row["id"] for row in issues if row["blocks"] and row["resolution"] is None]
    sections = content(request, layout, source_notes)
    payload = {
        "schema_version": DRAFT,
        "project_id": board["project_id"], "native_revision": board["native_revision"],
        "projection": board["projection"],
        "request": {"path": name, "sha256": context.digest(raw)},
        "author": author, "route": route,
        "requirements": {ident: {
            key: requirements[ident][key] for key in ("source_ref", "source_sha256", "verbatim",
                                                     "acceptance", "dependencies")
        } for ident in selected},
        "notes": source_notes, "questions": issues,
        "status": "awaiting-decision" if held else "draft-for-review",
        "blocking_question_ids": held, "section_ids": list(sections),
        "documents": {doc: {
            "markdown": as_markdown(title, doc, groups, sections, source_notes, issues, held),
            "html": as_html(title, doc, groups, sections, source_notes, issues, held),
        } for doc, groups in layout.items()},
    }
    return {**payload, "bundle_sha256": spec.digest(payload)}


def review(candidate, record):
    spec.exact_fields(record, {"schema_version", "bundle_sha256", "reviewer",
                               "checks", "verdict", "summary"}, "facilitation review")
    context.require(record["schema_version"] == REVIEW
                    and record["bundle_sha256"] == candidate["bundle_sha256"],
                    "review belongs to a different facilitation bundle")
    reviewer = spec.checked_text(record, "reviewer", 240)
    context.require(reviewer.casefold() != candidate["author"].casefold(),
                    "facilitation reviewer must differ from the author")
    verdict = spec.checked_text(record, "verdict", 32)
    context.require(verdict in ("approve", "changes-requested"), "unsupported review verdict")
    summary = spec.checked_text(record, "summary")
    checks = context.records(record, "checks")
    context.require(set(checks) == set(candidate["section_ids"]),
                    "review must address every authored section")
    for ident, check in checks.items():
        spec.exact_fields(check, {"id", "outcome", "observation"}, f"section review {ident}")
        context.require(check["outcome"] in ("matches", "needs-change"),
                        f"unsupported section outcome: {ident}")
        spec.checked_text(check, "observation")
    context.require(verdict != "approve" or all(row["outcome"] == "matches" for row in checks.values()),
                    "review approval contradicts its observations")
    status = "changes-requested"
    if verdict == "approve":
        status = "awaiting-decision" if candidate["blocking_question_ids"] else "reviewed"
    return {
        "status": status,
        "project_id": candidate["project_id"], "native_revision": candidate["native_revision"],
        "route": candidate["route"], "bundle_sha256": candidate["bundle_sha256"],
        "reviewer": reviewer, "summary": summary, "checks": checks,
        "blocking_question_ids": candidate["blocking_question_ids"],
        "reviewer_identity_authenticated": False, "owner_acceptance_authenticated": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    for action in ("draft", "review"):
        sub = actions.add_parser(action)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--projection", required=True)
        sub.add_argument("--input", required=True)
        if action == "draft":
            sub.add_argument("--format", choices=("json", "markdown", "html"), default="json")
            sub.add_argument("--document", choices=("BRIEF", "PRFAQ", "DESIGN", "EXPERIENCE"))
            sub.add_argument("--require-ready", action="store_true",
                             help="exit 3 if the draft retains open blocking decisions")
        else:
            sub.add_argument("--review", required=True)
            sub.add_argument("--review-sha256", required=True)
    args = parser.parse_args()
    try:
        snapshot = tree.Snapshot(args.root)
        candidate = draft(args.root, args.projection, args.input, snapshot)
        result, exit_code, view = candidate, 0, None
        if args.action == "review":
            raw = spec.pin_bytes(snapshot, args.review, args.review_sha256)
            result = review(candidate, context.json_object(raw))
            exit_code = 0 if result["status"] == "reviewed" else 3
        elif args.format != "json":
            views = candidate["documents"]
            document = args.document or (next(iter(views)) if len(views) == 1 else None)
            context.require(document in views, "select a document in the current route")
            view = views[document][args.format]
        if args.action == "draft" and args.require_ready and candidate["blocking_question_ids"]:
            exit_code = 3
        snapshot.verify_unchanged()
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}), file=sys.stderr)
        return 2
    if view is None:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(view)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
