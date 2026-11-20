#!/usr/bin/env python3
"""Resolve reviewed Markdown document templates and deliver auditable revisions."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
import ticket_tree as tree
from production_choice_route import verify_route
import document_templates_view as view

context = tree.context
REGISTRY = "atelier.document-template-registry/1"
REQUEST = "atelier.document-template-request/1"
DRAFT = "atelier.document-template-draft/1"
REVIEW = "atelier.document-template-review/1"
DECISION = "atelier.document-template-review-input/1"
CATALOG = "atelier.document-template-catalog/1"
LIBRARY = Path(__file__).with_name("document_templates_catalog.json")
SCOPES = ("module", "agent", "library", "personal", "team")
ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
DOC_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][a-zA-Z0-9.-]+)?")
HEAD = re.compile(r"^##[ \t]+(.+?)\s*$")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
FENCE = re.compile(r"^ {0,3}([\x60~]{3,})")
RESOURCE = {"guidance", "rubric", "methods", "style", "view"}
META = {
    "title", "template", "extends", "version", "description", "not_for",
    "paced", "facilitation_order", "guidance", "agents", "rubric",
    "methods", "output", "style", "view", "html_view", "status", "created", "updated",
}


def check_fields(value, required, optional, label):
    context.require(isinstance(value, dict)
                    and required <= value.keys() <= required | optional,
                    f"invalid fields for {label}")


def checked(value, label, limit=16000):
    context.require(isinstance(value, str) and value == value.strip()
                    and 0 < len(value) <= limit and "\0" not in value,
                    f"invalid text for {label}")
    return value


def record_hash(value):
    return context.digest(context.canonical(value))


def read_json(snapshot, path):
    return context.json_object(snapshot.read(path))


def scalar(raw):
    raw = raw.strip()
    if raw == "true" or raw == "false":
        return raw == "true"
    if raw.startswith("["):
        context.require(raw.endswith("]"), "unterminated inline template list")
        return [scalar(item) for item in raw[1:-1].split(",") if item.strip()]
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise context.ContextError("invalid double-quoted template value") from error
        context.require(isinstance(value, str), "expected a quoted text value")
        return value
    if raw.startswith("'"):
        context.require(raw.endswith("'") and len(raw) > 1, "invalid single-quoted template value")
        return raw[1:-1].replace("''", "'")
    context.require(not raw or raw[0] not in "&*!>|{}", "unsupported template YAML value")
    return raw


def slug(text):
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", text.lower()).strip())


def frontmatter(text):
    text = text.removeprefix("\ufeff").replace("\r\n", "\n")
    parts = text.split("\n---\n", 1)
    context.require(text.startswith("---\n") and len(parts) == 2,
                    "template must start with Markdown frontmatter")
    meta = {}
    for line in parts[0].splitlines()[1:]:
        if not line.strip() or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        context.require(sep and key in META and key not in meta,
                        f"unsupported or duplicate template field: {key}")
        meta[key] = scalar(value)
    return meta, parts[1]


def split_sections(body):
    """Recognize second-level headings outside comments and fenced code."""
    intro, sections, current = [], [], None
    fence, in_comment = None, False
    for line in body.splitlines(keepends=True):
        marker = FENCE.match(line)
        heading = None
        if marker and not in_comment:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line[marker.end():].strip():
                fence = None
        elif fence is None:
            if not in_comment:
                heading = HEAD.fullmatch(line.rstrip("\r\n"))
            for token in re.findall(r"<!--|-->", line):
                in_comment = token == "<!--"
        if heading:
            current = (heading[1].strip(), [])
            sections.append(current)
        (intro if current is None else current[1]).append(line)
    context.require(fence is None and not in_comment, "unterminated template fence or comment")
    return "".join(intro), [(name, "".join(lines[1:])) for name, lines in sections]


def parse_template(raw, path):
    meta, body = frontmatter(raw.decode("utf-8"))
    key = "template" if "template" in meta else "extends"
    name = meta.get(key)
    context.require(isinstance(name, str) and ID.fullmatch(name)
                    and ("template" in meta) != ("extends" in meta), "expected one template or extends ID")
    version = meta.get("version", "0.0.0")
    context.require(isinstance(version, str) and VERSION.fullmatch(version), "invalid template version")
    context.require(isinstance(meta.get("paced", False), bool), "paced must be a boolean")
    context.require(meta.get("html_view", "offer") in ("offer", "always", "never"), "invalid html_view")
    for key in RESOURCE | {"description", "not_for", "output"}:
        context.require(key not in meta or isinstance(meta[key], str), f"{key} must be text")
    intro, source_sections = split_sections(body)
    hints = {}
    for comment in COMMENT.findall(intro):
        field, sep, value = comment.partition(":")
        if sep and field.strip() in {"purpose", "stance", "inputs", "writing", "done when", "companions", "view", "next"}:
            hints.setdefault(field.strip(), []).append(value.strip())
    rows = {}
    for heading, raw_section in source_sections:
        section_id = slug(heading)
        context.require(section_id and section_id not in rows, f"duplicate or empty section ID: {heading}")
        checked(heading, "heading", 300)
        instructions = "\n".join(comment.strip() for comment in COMMENT.findall(raw_section))
        condition = re.match(r"include when\s*:\s*(.*)", instructions, re.I)
        diagram = re.search(r"\bdiagram:\s*([a-z]+)", instructions)
        rows[section_id] = {
            "id": section_id, "heading": heading, "instructions": instructions,
            "starter": COMMENT.sub("", raw_section).strip(), "source": path,
            "rule": ("index" if section_id == "table-of-contents"
                     else "conditional" if condition
                     else "optional" if re.match(r"optional\b", instructions, re.I) else "required"),
            "condition": condition[1] if condition else None,
            "diagram": diagram[1] if diagram else None,
        }
    return {"id": name, "version": version, "path": path, "meta": meta, "hints": hints, "sections": rows}


def registry(snapshot, path):
    value = read_json(snapshot, path)
    check_fields(value, {"schema", "layers"}, {"html_view", "source_pins"}, "template registry")
    context.require(value["schema"] == REGISTRY and value.get("html_view", "offer") in ("offer", "always", "never"),
                    "unsupported template registry")
    layers = value["layers"]
    if "source_pins" in value:
        read_sources(snapshot, value["source_pins"])
    context.require(isinstance(layers, list) and 0 < len(layers) <= len(SCOPES), "invalid registry layers")
    entries, resources, origins, seen = [], {}, {}, set()
    for layer in layers:
        check_fields(layer, {"scope", "templates"}, {"resources"}, "registry layer")
        scope = layer["scope"]
        context.require(scope in SCOPES and scope not in seen, "invalid or duplicate template scope")
        seen.add(scope)
        resource_pins = tree.pins(layer.get("resources", []))
        template_pins = tree.pins(layer["templates"])
        context.require(not template_pins.keys() & resource_pins.keys(), "file cannot be both template and resource")
        for ref, sha in (template_pins | resource_pins).items():
            data = snapshot.read(ref)
            context.require(context.digest(data) == sha, f"SOURCE_DRIFT: {ref}")
            context.require(ref not in origins, f"duplicate registry file: {ref}")
            origins[ref] = sha
            if ref in resource_pins:
                resources[ref] = sha
            else:
                entries.append((SCOPES.index(scope), parse_template(data, ref)))
    entries.sort(key=lambda pair: pair[0])
    names = {(rank, item["id"], "extends" in item["meta"]) for rank, item in entries}
    context.require(len(names) == len(entries), "ambiguous template ID in one scope")
    known = {item["id"] for _, item in entries if "template" in item["meta"]}
    context.require(all(item["id"] in known for _, item in entries), "extension has no template")
    return entries, resources, value.get("html_view", "offer")


def section_order(meta, rows):
    order = meta.get("facilitation_order")
    if order is None:
        return [ident for ident, row in rows.items() if row["rule"] != "index"]
    context.require(isinstance(order, list) and all(isinstance(x, str) for x in order),
                    "facilitation_order must be a list of IDs")
    names = [item.removesuffix("?") for item in order]
    expected = {ident for ident, row in rows.items() if row["rule"] != "index"}
    context.require(set(names) == expected and len(names) == len(expected),
                    "facilitation order must name each content section once")
    for tag, name in zip(order, names):
        if tag.endswith("?") and rows[name]["rule"] == "required":
            rows[name]["rule"] = "optional"
    return names


def position(section, rows, coach):
    instructions = section["instructions"]
    if re.match(r"(?:optional[.]\s*)?first\b", instructions, re.I):
        return (1 if next(iter(rows), None) == "table-of-contents" else 0), 0
    anchor = re.match(r"(After|Before) (.+?)[.]\s*", instructions, re.I)
    if anchor:
        ident = slug(anchor[2])
        context.require(ident in rows, f"missing placement anchor: {anchor[2]}")
        offset = anchor[1].lower() == "after"
        return list(rows).index(ident) + offset, coach.index(ident) + offset if ident in coach else 0
    return len(rows), len(coach)


def apply_extension(rows, coach, meta, overlay):
    for ident, old in list(rows.items()):
        if ident in overlay["sections"]:
            new = overlay["sections"][ident]
            if re.match(r"adds? to\b", new["instructions"], re.I):
                rows[ident] = {**old, "instructions": old["instructions"] + "\n" + new["instructions"],
                               "source": new["source"]}
            else:
                rows[ident] = dict(new)
    for ident, row in overlay["sections"].items():
        if ident not in rows:
            index, coaching_index = position(row, rows, coach)
            before = list(rows)[:index]
            after = list(rows)[index:]
            rows = {**{name: rows[name] for name in before}, ident: dict(row),
                    **{name: rows[name] for name in after}}
            if row["rule"] != "index":
                coach.insert(coaching_index, ident)
    for name, value in overlay["meta"].items():
        if name not in {"extends", "version", "facilitation_order"}:
            meta[name] = value
    if "facilitation_order" in overlay["meta"]:
        raw_order = overlay["meta"]["facilitation_order"]
        context.require(isinstance(raw_order, list) and all(isinstance(tag, str) for tag in raw_order),
                        "extension facilitation_order must be a list of IDs")
        names = {tag.removesuffix("?") for tag in raw_order}
        removed = [ident for ident, row in rows.items() if ident not in names and row["rule"] != "index"]
        rows = {ident: row for ident, row in rows.items() if ident not in removed}
        coach = section_order(overlay["meta"], rows)
    else:
        removed = []
    return rows, coach, removed


def resolve_resource(ref, origin, resources):
    direct = (PurePosixPath(origin).parent / ref).as_posix()
    if direct in resources:
        return direct
    if "/" not in ref and "." not in ref:
        matching = [path for path in resources if PurePosixPath(path).stem == ref]
        context.require(len(matching) == 1, f"missing or ambiguous named resource: {ref}")
        return matching[0]
    context.require(False, f"template resource must be in the registry: {ref}")


def resolve(snapshot, registry_path, template_id):
    entries, resources, team_view = registry(snapshot, registry_path)
    selected = [(rank, item) for rank, item in entries if item["id"] == template_id]
    bases = [(rank, item) for rank, item in selected if "template" in item["meta"]]
    context.require(bases, f"unknown template: {template_id}")
    rank, base = bases[-1]
    meta, rows = dict(base["meta"]), {ident: dict(row) for ident, row in base["sections"].items()}
    coach = section_order(meta, rows)
    hints = {key: list(vals) for key, vals in base["hints"].items()}
    overlays, dropped = [], []
    owners = {key: base["path"] for key in RESOURCE}
    for extension_rank, extension in selected:
        if "extends" not in extension["meta"] or extension_rank < rank:
            continue
        rows, coach, removed = apply_extension(rows, coach, meta, extension)
        dropped += removed
        overlays.append(extension["path"])
        for key in RESOURCE & extension["meta"].keys():
            owners[key] = extension["path"]
        for key, vals in extension["hints"].items():
            hints.setdefault(key, []).extend(vals)
    context.require(rows and coach, "template has no document sections")
    selected_resources = {}
    for key in sorted(RESOURCE):
        ref = meta.get(key)
        if not ref or (key == "view" and ref in ("document", "slides")):
            continue
        path = resolve_resource(ref, owners[key], resources)
        selected_resources[key] = {"path": path, "sha256": resources[path]}
    source = [base["path"], *overlays]
    plan = {
        "template": template_id, "version": base["version"], "base": base["path"],
        "overlays": overlays, "removed_sections": dropped,
        "sources": {ref: context.digest(snapshot.read(ref)) for ref in source},
        "registry_sha256": context.digest(snapshot.read(registry_path)),
        "resources": selected_resources, "hints": hints, "meta": meta,
        "sections": list(rows.values()), "coaching_order": coach,
        "html_view": "never" if team_view == "never" else meta.get("html_view", team_view),
    }
    return {**plan, "plan_sha256": record_hash(plan)}


def under_source(upstream, path):
    context.require(isinstance(path, str), "catalog path must be text")
    leaf = PurePosixPath(path)
    context.require(not leaf.is_absolute() and leaf.as_posix() == path and ".." not in leaf.parts
                    and bool(leaf.parts), "catalog paths must stay within the declared source")
    return (PurePosixPath(upstream) / leaf).as_posix()


def catalog_registry(snapshot, upstream, catalog_path):
    catalog = read_json(snapshot, catalog_path)
    schema = catalog.get("schema")
    context.require(isinstance(schema, str) and (schema == CATALOG or schema.endswith("-document-template-catalog/1")),
                    "expected a version 1 template catalog")
    pins = [{"path": catalog_path, "sha256": context.digest(snapshot.read(catalog_path))}]
    if "license_path" in catalog or "license_sha256" in catalog:
        notice = under_source(upstream, catalog.get("license_path"))
        expected = catalog.get("license_sha256")
        context.require(context.digest(snapshot.read(notice)) == expected, "source notice differs from catalog")
        pins.append({"path": notice, "sha256": expected})
    context.require(isinstance(catalog.get("files"), list) and 0 < len(catalog["files"]) <= 200,
                    "catalog must declare 1 to 200 files")
    layers = {scope: [] for scope in SCOPES}
    seen = set()
    for row in catalog["files"]:
        context.require(isinstance(row, dict) and {"path", "sha256", "scope", "kind"} <= row.keys(),
                        "catalog file needs path, SHA-256, scope and kind")
        ref = under_source(upstream, row["path"])
        context.require(ref not in seen, f"duplicate catalog path: {ref}")
        seen.add(ref)
        context.require(row["scope"] in SCOPES and row["kind"] in ("template", "resource"),
                        f"invalid catalog scope or kind: {ref}")
        expected = row["sha256"]
        context.require(context.digest(snapshot.read(ref)) == expected,
                        f"source differs from pinned template catalog: {row['path']}")
        layers[row["scope"]].append((row["kind"], {"path": ref, "sha256": expected}))
    context.require(any(kind == "template" for rows in layers.values() for kind, _ in rows),
                    "expected at least one template in the catalog")
    return {"schema": REGISTRY, "source_pins": pins, "layers": [
        {"scope": scope, "templates": [pin for kind, pin in pins if kind == "template"],
         "resources": [pin for kind, pin in pins if kind == "resource"]}
        for scope, pins in layers.items() if pins]}


def read_sources(snapshot, sources):
    pins = tree.pins(sources)
    context.require(pins, "document requires at least one reviewed source")
    for ref, sha in pins.items():
        context.require(context.digest(snapshot.read(ref)) == sha, f"SOURCE_DRIFT: {ref}")
    return pins


def content_rows(items, evidence, label):
    context.require(isinstance(items, list) and 0 < len(items) <= 80, f"need bounded content in {label}")
    result = []
    for row in items:
        check_fields(row, {"id", "body", "sources"}, {"title"}, label)
        ident = row["id"]
        context.require(isinstance(ident, str) and DOC_ID.fullmatch(ident), f"invalid content ID in {label}")
        cites = context.bounded_ids(row["sources"], f"sources for {ident}")
        context.require(cites and set(cites) <= evidence.keys(), f"unknown or missing sources for {ident}")
        item = {"id": ident, "body": checked(row["body"], f"body of {ident}"), "sources": cites}
        if "title" in row:
            item["title"] = checked(row["title"], f"title of {ident}", 300)
            context.require("\n" not in item["title"], "content title must be on one line")
        result.append(item)
    return result


def companion_defs(plan, doc_id, title):
    definitions = {}
    for hint in plan["hints"].get("companions", []):
        for ref in re.findall(r"\x60([a-zA-Z0-9_{}-]+[.]md)\x60", hint):
            out = ref.replace("{id}", doc_id).replace("{slug}", slug(title))
            context.require(re.fullmatch(r"[a-zA-Z0-9_][\w-]*[.]md", out)
                            and out != "document.md", "unsafe or reserved companion name")
            definitions[out] = hint
    return definitions


def draft(snapshot, request_path, plan, previous=None):
    request = read_json(snapshot, request_path)
    check_fields(request, {"schema", "id", "title", "owner", "sources", "sections"},
                 {"assumptions", "companions", "html", "change_reason"}, "document request")
    context.require(request["schema"] == REQUEST, "unsupported document request")
    title = checked(request["title"], "title", 300)
    context.require("\n" not in title, "title must be on one line")
    owner = checked(request["owner"], "owner", 300)
    doc_id = request["id"]
    context.require(isinstance(doc_id, str) and DOC_ID.fullmatch(doc_id), "invalid document ID")
    pins = read_sources(snapshot, request["sources"])
    rows = {row["id"]: row for row in plan["sections"] if row["rule"] != "index"}
    sections = request["sections"]
    context.require(isinstance(sections, dict) and sections.keys() == rows.keys(),
                    "each section needs an explicit included or omitted decision")
    settled, item_ids = {}, set()
    for ident, row in rows.items():
        decision = sections[ident]
        check_fields(decision, {"include"}, {"reason", "items"}, f"section {ident}")
        included = decision["include"]
        context.require(isinstance(included, bool), f"invalid decision for section {ident}")
        if row["rule"] != "required":
            checked(decision.get("reason"), f"reason for section {ident}")
        if included:
            items = content_rows(decision.get("items"), pins, ident)
            for item in items:
                context.require(item["id"] not in item_ids, f"duplicate content ID: {item['id']}")
                item_ids.add(item["id"])
            settled[ident] = {**decision, "items": items}
        else:
            context.require(row["rule"] != "required" and "items" not in decision,
                            f"required or filled section cannot be omitted: {ident}")
            settled[ident] = decision
    assumptions = context.records(request, "assumptions")
    for ident, row in assumptions.items():
        check_fields(row, {"id", "text", "status"}, {"resolution", "sources"}, f"assumption {ident}")
        checked(row["text"], f"assumption {ident}")
        context.require(row["status"] in ("open", "accepted", "corrected"), "invalid assumption status")
        if row["status"] != "open":
            checked(row.get("resolution"), f"resolution to {ident}")
            cites = context.bounded_ids(row.get("sources"), f"assumption {ident} sources")
            context.require(cites and set(cites) <= pins.keys(), f"unbound assumption resolution: {ident}")
    companions = request.get("companions", {})
    definitions = companion_defs(plan, doc_id, title)
    context.require(isinstance(companions, dict) and companions.keys() == definitions.keys(),
                    "each declared companion needs an explicit decision")
    for file, decision in companions.items():
        check_fields(decision, {"include", "reason"}, {"items"}, f"companion {file}")
        context.require(isinstance(decision["include"], bool), f"invalid companion decision: {file}")
        checked(decision["reason"], f"companion {file} reason")
        if decision["include"]:
            decision["items"] = content_rows(decision.get("items"), pins, file)
        else:
            context.require("items" not in decision, f"omitted companion has content: {file}")
    offered = request.get("html", False)
    context.require(isinstance(offered, bool), "html must be a boolean")
    revision = 1
    parent = None
    changes = {}
    if previous:
        context.require(previous["id"] == doc_id and previous["template"]["template"] == plan["template"],
                        "prior document and template ID must match")
        checked(request.get("change_reason"), "change reason")
        revision = previous["revision"] + 1
        parent = previous["sha256"]
        for ident in sorted(set(previous["sections"]) | settled.keys()):
            before = previous["sections"].get(ident)
            after = settled.get(ident)
            if before != after:
                changes[ident] = {"before_sha256": record_hash(before), "after_sha256": record_hash(after)}
    result = {
        "schema": DRAFT, "id": doc_id, "title": title, "owner": owner, "revision": revision,
        "previous_sha256": parent, "change_reason": request.get("change_reason"),
        "changes": changes, "request_sha256": context.digest(snapshot.read(request_path)),
        "sources": pins, "template": plan, "sections": settled, "assumptions": list(assumptions.values()),
        "companions": companions, "render_html": (plan["html_view"] == "always"
                                                 or plan["html_view"] == "offer" and offered),
    }
    return {**result, "sha256": record_hash(result)}


def read_draft(snapshot, path, expected):
    value = read_json(snapshot, path)
    sha = value.pop("sha256", None)
    context.require(value.get("schema") == DRAFT and sha == expected == record_hash(value),
                    "draft differs from the expected reviewed revision")
    parent = PurePosixPath(path).parent
    receipt = read_json(snapshot, (parent / "receipt.json").as_posix())
    context.require(receipt.get("draft_sha256") == sha, "output receipt belongs to another draft")
    artifacts = receipt.get("artifacts_sha256")
    required = {"draft.json", "document.md"} | {name for name, decision in value["companions"].items()
                                                    if decision["include"]}
    if value["render_html"]:
        required.add("document.html")
    context.require(isinstance(artifacts, dict) and artifacts.keys() == required
                    and PurePosixPath(path).name == "draft.json", "draft artifact inventory has changed")
    context.require(value.get("artifacts_sha256") == {k: v for k, v in artifacts.items() if k != "draft.json"},
                    "output receipt differs from artifact hashes pinned in the reviewed draft")
    for name, pin in artifacts.items():
        context.require(PurePosixPath(name).name == name
                        and context.digest(snapshot.read((parent / name).as_posix())) == pin,
                        f"draft artifact changed: {name}")
    return {**value, "sha256": sha}


def progress(snapshot, request_path, plan):
    request = read_json(snapshot, request_path)
    by_id = {row["id"]: row for row in plan["sections"] if row["rule"] != "index"}
    rows = request.get("sections")
    context.require(isinstance(rows, dict) and rows.keys() <= by_id.keys(), "unknown section in progress request")
    settled, next_rows = [], []
    for ident in plan["coaching_order"]:
        row = by_id[ident]
        value = rows.get(ident, {})
        context.require(isinstance(value, dict), f"invalid in-progress section: {ident}")
        if value.get("include") is True and value.get("items") and (
            row["rule"] == "required" or isinstance(value.get("reason"), str) and value["reason"].strip()
        ):
            settled.append(ident)
        elif value.get("include") is False and row["rule"] != "required" and isinstance(
            value.get("reason"), str
        ) and value["reason"].strip():
            settled.append(ident)
        else:
            next_rows.append(row)
    return {"template_sha256": plan["plan_sha256"], "settled": settled, "total": len(by_id),
            "next": next_rows[:1] if plan["meta"].get("paced") else next_rows,
            "remaining": len(next_rows)}


def review(snapshot, draft_record, review_path, reviewed_plan):
    review_input = read_json(snapshot, review_path)
    check_fields(review_input, {"schema", "draft_sha256", "reviewer", "findings"}, set(), "review")
    context.require(review_input["schema"] == DECISION and review_input["draft_sha256"] == draft_record["sha256"],
                    "review must name the exact current draft")
    reviewer = checked(review_input["reviewer"], "reviewer", 300)
    context.require(reviewer.casefold() != draft_record["owner"].casefold(),
                    "record a reviewer other than the document owner")
    context.require(reviewed_plan["plan_sha256"] == draft_record["template"]["plan_sha256"],
                    "template changed after the draft was created")
    findings = review_input["findings"]
    required = {key for key, item in draft_record["sections"].items() if item["include"]}
    required |= {f"companion/{key}" for key, item in draft_record["companions"].items() if item["include"]}
    context.require(isinstance(findings, dict) and findings.keys() == required,
                    "review must cover each included section and companion")
    for key, row in findings.items():
        check_fields(row, {"status", "note"}, set(), f"review result {key}")
        context.require(row["status"] in ("pass", "revise"), f"invalid review status: {key}")
        checked(row["note"], f"review note about {key}")
    read_sources(snapshot, [{"path": ref, "sha256": sha} for ref, sha in draft_record["sources"].items()])
    blockers = [row["id"] for row in draft_record["assumptions"] if row["status"] == "open"]
    return {"schema": REVIEW, "draft_sha256": draft_record["sha256"], "reviewer": reviewer,
            "review_input_sha256": context.digest(snapshot.read(review_path)), "findings": findings,
            "remaining_assumptions": blockers,
            "status": "revise" if blockers or any(row["status"] == "revise" for row in findings.values()) else "reviewed"}


def emit_outputs(root, relative, result, payloads):
    output = context.local(root, relative, existing=False)
    context.require(not any(part in context.PRIVATE_PARTS or context.PRIVATE_NAME.fullmatch(part)
                            for part in PurePosixPath(relative).parts), "private output path rejected")
    context.require(output.parent.is_dir() and not output.exists(), "output needs a new local directory")
    for name in (*payloads, "receipt.json"):
        context.require(Path(name).name == name and name not in (".", ".."), "unsafe output filename")
    context.require("receipt.json" not in payloads, "reserved receipt filename")
    context.require(all(len(body) <= context.MAX_BOUND_SOURCE for body in payloads.values()),
                    "generated artifact exceeds the review read limit")
    receipt = {**result, "artifacts_sha256": {name: context.digest(body) for name, body in payloads.items()}}
    output.mkdir(mode=0o700)
    for name, body in payloads.items():
        with (output / name).open("xb") as stream:
            stream.write(body)
    with (output / "receipt.json").open("xb") as stream:
        stream.write(context.canonical(receipt) + b"\n")
    return receipt


def init_library(root, relative):
    library = context.load(LIBRARY)
    context.require(library.get("schema") == CATALOG, "unsupported starter library")
    version = library["version"]
    resources = {name: value.encode("utf-8") for name, value in library["resources"].items()}
    templates = {}
    for ident, document in context.records(library, "templates").items():
        context.require(ID.fullmatch(ident), "invalid starter template ID")
        metadata = {"template": ident, "version": version, "description": document["description"],
                    "rubric": "planning-rubric.md", **document.get("metadata", {})}
        work = document["sections"]
        if "facilitation_order" not in metadata:
            metadata["facilitation_order"] = [slug(row["heading"]) + ("?" if row.get("rule") else "")
                                               for row in work if slug(row["heading"]) != "table-of-contents"]
        lines = ["---", *[f"{name}: {json.dumps(value, ensure_ascii=False)}"
                          for name, value in metadata.items()], "---", ""]
        lines.extend(f"<!-- {key}: {value} -->\n" for key, value in document.get("guidance", {}).items())
        lines.append("# {title}\n")
        for row in work:
            lines.append("## " + row["heading"])
            hint = (row.get("rule", "") + " " + row.get("prompt", "")).strip()
            if hint:
                lines.append(f"<!-- {hint} -->")
            lines.append("")
        name = f"template-{ident}.md"
        raw = "\n".join(lines).encode("utf-8")
        parse_template(raw, name)
        templates[name] = raw

    def pins(payloads):
        return [{"path": (PurePosixPath(relative) / name).as_posix(), "sha256": context.digest(raw)}
                for name, raw in payloads.items()]

    registry_record = {"schema": REGISTRY, "layers": [{"scope": "module", "templates": pins(templates),
                                                      "resources": pins(resources)}]}
    payloads = {**templates, **resources, "registry.json": context.canonical(registry_record) + b"\n"}
    return emit_outputs(root, relative, {"registry": (PurePosixPath(relative) / "registry.json").as_posix(),
                                         "templates": len(templates), "library_version": version}, payloads)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    catalog = commands.add_parser("upstream-registry")
    catalog.add_argument("--upstream", required=True)
    catalog.add_argument("--catalog", required=True, help="project-relative reviewed source catalog JSON")
    starter = commands.add_parser("init-library")
    starter.add_argument("--output", required=True, help="new project-relative library directory")
    for command in ("list", "inspect", "progress", "draft", "update", "review"):
        cmd = commands.add_parser(command)
        cmd.add_argument("--registry", required=True)
        if command != "list":
            cmd.add_argument("--template", required=True)
        if command == "progress":
            cmd.add_argument("--request", required=True)
        if command in ("draft", "update"):
            cmd.add_argument("--request", required=True)
            cmd.add_argument("--expect-template", required=True)
            cmd.add_argument("--output", required=True)
        if command in ("update", "review"):
            cmd.add_argument("--draft", required=True)
            cmd.add_argument("--expect-draft", required=True)
        if command == "review":
            cmd.add_argument("--findings", required=True)
    args = parser.parse_args(argv)
    try:
        root = args.root.absolute()
        context.require(root.is_dir() and root.resolve() == root, "root must be an existing canonical directory")
        snapshot = tree.Snapshot(root)
        production = (verify_route(root, "explore" if args.command == "draft" else "implement")
                      if args.command in ("draft", "update") else None)
        if args.command == "upstream-registry":
            response = catalog_registry(snapshot, args.upstream, args.catalog)
        elif args.command == "init-library":
            response = init_library(root, args.output)
        elif args.command == "list":
            entries, _, _ = registry(snapshot, args.registry)
            response = [resolve(snapshot, args.registry, name) for name in sorted(
                {item["id"] for _, item in entries if "template" in item["meta"]})]
        else:
            plan = resolve(snapshot, args.registry, args.template)
            if args.command == "inspect":
                response = plan
            elif args.command == "progress":
                response = progress(snapshot, args.request, plan)
            elif args.command == "review":
                old = read_draft(snapshot, args.draft, args.expect_draft)
                response = review(snapshot, old, args.findings, plan)
            else:
                context.require(plan["plan_sha256"] == args.expect_template, "template plan differs from reviewed SHA-256")
                old = read_draft(snapshot, args.draft, args.expect_draft) if args.command == "update" else None
                record = draft(snapshot, args.request, plan, old)
                payloads, unplaced = view.build(record, snapshot)
                record.pop("sha256")
                record["artifacts_sha256"] = {name: context.digest(body) for name, body in payloads.items()}
                record["sha256"] = record_hash(record)
                payloads["draft.json"] = context.canonical(record) + b"\n"
                snapshot.verify_unchanged()
                response = emit_outputs(root, args.output, {"draft_sha256": record["sha256"],
                                                           "revision": record["revision"],
                                                           **({"production_choice": production}
                                                              if production else {}),
                                                           "unplaced_html_sections": unplaced}, payloads)
        if args.command not in ("draft", "update"):
            snapshot.verify_unchanged()
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 0
    except (context.ContextError, OSError, UnicodeError, ValueError) as error:
        print(f"document templates: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
