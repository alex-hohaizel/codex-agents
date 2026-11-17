#!/usr/bin/env python3
"""Build and verify an offline interactive prototype from exact reviewed UX sources."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "codex-agents.ux-prototype/1"
ASSETS = Path(__file__).resolve().parents[1] / "assets/prototype"
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")
LIMIT = 2 * 1024 * 1024


def require(value, message):
    if not value:
        raise ValueError(message)


def keys(obj, required, optional=()):
    require(isinstance(obj, dict) and set(required) <= set(obj) <= set(required) | set(optional),
            "Unexpected or missing fields: " + ", ".join(required))


def text(value, label, maxlen=500):
    require(isinstance(value, str) and 0 < len(value.strip()) and len(value) <= maxlen, f"Invalid {label}")
    return value


def ident(value):
    require(isinstance(value, str) and ID.fullmatch(value), "Invalid stable ID")
    return value


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def get_file(root, rel):
    require(isinstance(rel, str) and not set(rel).intersection("\\\0\n\r"), "Unsafe path")
    parts = rel.split("/")
    require(parts and all(part not in {"", ".", "..", ".git", ".ssh", ".env"} and not part.startswith(".env.") for part in parts),
            "Use a safe relative path under the project")
    candidate = root
    for part in parts:
        candidate = candidate / part
        require(not candidate.is_symlink(), "Linked sources are not accepted")
    require(candidate.is_file(), "Required source absent: " + rel)
    with candidate.open("rb") as file:
        raw = file.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "Source exceeds prototype size limit")
    return raw


def pairs(seq):
    result = {}
    for key, value in seq:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def rgb(hexvalue):
    require(isinstance(hexvalue, str) and HEX.fullmatch(hexvalue), "Design tokens must be #RRGGBB")
    return tuple(int(hexvalue[i:i+2], 16) / 255 for i in (1, 3, 5))


def luminance(color):
    return sum(k * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4)
               for k, v in zip((.2126, .7152, .0722), rgb(color)))


def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)))
    return (y + .05) / (x + .05)


def validate(root, spec):
    keys(spec, ("schema", "id", "title", "summary", "locale", "start", "sources", "theme", "screens"))
    require(spec["schema"] == SCHEMA, "Unsupported prototype schema")
    ident(spec["id"])
    text(spec["title"], "title", 90)
    text(spec["summary"], "summary")
    require(isinstance(spec["locale"], str) and re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z]{2,8})?", spec["locale"]), "Invalid locale")
    keys(spec["theme"], ("background", "surface", "ink", "accent", "onAccent"))
    theme = spec["theme"]
    pairs_to_check = (("ink", "background"), ("ink", "surface"), ("onAccent", "accent"))
    for a, b in pairs_to_check:
        require(contrast(theme[a], theme[b]) >= 4.5, f"Text contrast fails: {a} on {b}")
    require(contrast(theme["accent"], theme["surface"]) >= 3 and contrast(theme["accent"], theme["background"]) >= 3,
            "Focus color must be visible on both backgrounds")
    sources = spec["sources"]
    require(isinstance(sources, list) and 2 <= len(sources) <= 24, "Bind reviewed DESIGN and EXPERIENCE sources")
    bound = {}
    scopes = set()
    for pin in sources:
        keys(pin, ("id", "kind", "path", "sha256"))
        key = ident(pin["id"])
        require(key not in bound and pin["kind"] in ("design", "experience", "requirement", "decision"), "Invalid repeated source")
        raw = get_file(root, pin["path"])
        require(isinstance(pin["sha256"], str) and HASH.fullmatch(pin["sha256"]) and digest(raw) == pin["sha256"],
                "Stale source: " + pin["path"])
        bound[key] = raw.decode("utf8")
        scopes.add(pin["kind"])
    require({"design", "experience"} <= scopes, "Review both design and experience separately")
    all_screens = spec["screens"]
    require(isinstance(all_screens, list) and 2 <= len(all_screens) <= 40, "Expected 2–40 screens")
    screens = {}
    for screen in all_screens:
        keys(screen, ("id", "label", "heading", "body", "state", "refs", "actions"), ("fields", "details"))
        key = ident(screen["id"])
        require(key not in screens, "Repeated screen ID")
        screens[key] = screen
        text(screen["label"], "step label", 48)
        text(screen["heading"], "screen heading", 100)
        text(screen["body"], "screen body", 1200)
        require(screen["state"] in ("normal", "pending", "conflict", "success"), "Unsupported interaction state")
        refs = screen["refs"]
        require(isinstance(refs, list) and 1 <= len(refs) <= 8, "Each screen needs reviewed references")
        for ref in refs:
            keys(ref, ("source", "excerpt"))
            source = ident(ref["source"])
            require(source in bound and text(ref["excerpt"], "source excerpt") in bound[source],
                    "Screen lacks its exact source excerpt")
        details = screen.get("details", [])
        require(isinstance(details, list) and len(details) <= 8, "Too many screen details")
        for row in details:
            keys(row, ("label", "value"))
            text(row["label"], "detail label", 60)
            text(row["value"], "detail value", 300)
        fields = screen.get("fields", [])
        require(isinstance(fields, list) and len(fields) <= 6, "Too many fields")
        field_ids = set()
        for field in fields:
            keys(field, ("id", "label", "type"), ("options", "help"))
            field_id = ident(field["id"])
            require(field_id not in field_ids, "Repeated field ID")
            field_ids.add(field_id)
            text(field["label"], "field label", 90)
            require(field["type"] in ("text", "check", "choice"), "Unsupported prototype field")
            if "help" in field:
                text(field["help"], "field help", 200)
            if field["type"] == "choice":
                labels = field.get("options")
                require(isinstance(labels,list) and 2 <= len(labels) <= 12, "Choice needs 2–12 labels")
                for label in labels:
                    text(label, "option", 90)
                require(len(set(labels)) == len(labels), "Choice labels repeat")
            else:
                require("options" not in field, "Only choices have options")
        actions = screen["actions"]
        require(isinstance(actions, list) and len(actions) <= 6, "Too many actions")
        action_ids = set()
        for action in actions:
            keys(action, ("id", "label", "to"), ("requires", "style"))
            aid = ident(action["id"])
            require(aid not in action_ids, "Repeated screen action ID")
            action_ids.add(aid)
            ident(action["to"])
            text(action["label"], "button label", 90)
            require(action.get("style", "secondary") in ("primary", "secondary"), "Invalid action style")
            needs = action.get("requires", [])
            require(isinstance(needs, list) and all(ident(n) in field_ids for n in needs), "Action requires an unknown field")
    start = ident(spec["start"])
    require(start in screens, "Start screen absent")
    pending, seen = [start], set()
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        require(key in screens, "Action points to a nonexistent screen")
        seen.add(key)
        pending.extend(a["to"] for a in screens[key]["actions"])
    require(seen == set(screens), "Unreachable screen: " + ", ".join(sorted(set(screens) - seen)))
    can_finish = {key for key, screen in screens.items() if not screen["actions"]}
    require(any(screens[key]["state"]=="success" for key in can_finish), "At least one success ending is needed")
    while True:
        extended = can_finish | {key for key, screen in screens.items() if any(a["to"] in can_finish for a in screen["actions"])}
        if extended == can_finish:
            break
        can_finish = extended
    require(can_finish == set(screens), "A screen cannot reach any ending")


def csp_hash(string):
    return "'sha256-" + base64.b64encode(hashlib.sha256(string.encode()).digest()).decode() + "'"


def build(root, input_file):
    source = get_file(root, input_file)
    spec = json.loads(source, object_pairs_hook=pairs)
    validate(root, spec)
    css = ":root{" + ";".join("--" + k + ":" + v for k,v in spec["theme"].items()) + "}" + (ASSETS/"prototype.css").read_text()
    js = (ASSETS/"prototype.js").read_text()
    binding = digest((digest(source) + digest(css.encode()) + digest(js.encode())).encode())
    payload = json.dumps({"binding":binding, "prototype":spec}, ensure_ascii=False).replace("<", "\\u003c")
    csp = "default-src 'none'; script-src " + csp_hash(js) + "; style-src " + csp_hash(css) + "; base-uri 'none'; form-action 'none'"
    title = html.escape(spec["title"])
    page = f"""<!doctype html>
<html lang="{html.escape(spec['locale'])}">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<title>{title} — UX prototype</title>
<style>{css}</style>
<div id="prototype"></div>
<noscript>Enable JavaScript for this local interaction prototype.</noscript>
<script id="prototype-data" type="application/json">{payload}</script>
<script>{js}</script>
</html>
"""
    raw = page.encode()
    return raw, {"schema":"codex-agents.ux-prototype-build/1", "id":spec["id"], "binding":binding,
                 "spec_sha256":digest(source), "html_sha256":digest(raw), "sources":spec["sources"],
                 "screens":len(spec["screens"]), "runtime_verified":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", required=True, help="Project relative JSON manifest")
    parser.add_argument("--artifact", type=Path, required=True, help="Local HTML prototype path")
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        require(root.is_dir(), "Project root is not a directory")
        raw, receipt = build(root, args.input)
        require(not args.artifact.is_symlink(), "Artifact cannot be a symbolic link")
        if args.action == "build":
            with args.artifact.open("xb") as file:
                file.write(raw)
        else:
            require(args.artifact.read_bytes() == raw, "HTML is stale or inconsistent with current reviewed sources")
        receipt["status"] = "built" if args.action == "build" else "verified-exact-bytes"
        print(json.dumps(receipt, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
