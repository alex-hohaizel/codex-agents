#!/usr/bin/env python3
"""Typed, engine-independent design/evidence checks; Python 3.9 standard library.

This tool does not execute models or certify play quality. Only the current
game model is accepted; state and handoff have separate current protocols.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

VERSION = "4.0.0"
TOOLKIT_VERSION = "6.0.0"


def v4():
    """Resolve the bundled extension from this same skill, including importlib use."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("game_atelier_v4_contract", Path(__file__).with_name("v4_contract.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

STAGES = ("concept", "preproduction", "slice", "beta", "release")
DOMAINS = ("camera", "input", "systems", "actors", "world", "progression",
           "rewards", "learning", "art", "commerce", "lifecycle", "equipment")
CORE = {"input", "systems", "art", "lifecycle"}
MODALITIES = {"document", "runtime", "build", "device", "player", "external_receipt"}
ORIGINS = {"design_review", "contract_review", "runtime_capture", "native_build",
           "device_observation", "player_observation", "release_review",
           "external_receipt", "historical_reference"}
HASH = re.compile(r"^[0-9a-f]{64}$")


def obj(required, properties=None):
    return {"type": "object", "required": list(required),
            "properties": properties or {k: {"type": "string", "minLength": 1} for k in required}}


TEXT = {"type": "string", "minLength": 1}
STRINGS = {"type": "array", "items": TEXT, "minItems": 1}
EMPTY_STRINGS = {"type": "array", "items": TEXT}


def rows(required, extra=None, minimum=1):
    props = {k: TEXT for k in required}
    props.update(extra or {})
    return {"type": "array", "items": obj(required, props), "minItems": minimum}


def domain_schemas():
    return {
        "camera": obj(("projection", "tracking", "focus_subject", "states"), {
            "projection": TEXT, "tracking": TEXT, "focus_subject": TEXT,
            "states": rows(("id", "when", "behavior", "readability_risk")),
            "subject_fraction": obj(("min", "max"), {
                "min": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
                "max": {"type": "number", "exclusiveMinimum": 0, "maximum": 1}})}),
        "input": obj(("scheme", "simultaneous_contacts", "actions", "peak_load_scenario", "accessibility"), {
            "scheme": TEXT, "simultaneous_contacts": {"type": "integer", "minimum": 1, "maximum": 10},
            "actions": rows(("id", "intent", "gesture", "context", "feedback", "cost_or_limit", "recovery")),
            "peak_load_scenario": TEXT, "accessibility": STRINGS}),
        "systems": obj(("rules", "links"), {
            "rules": rows(("id", "state", "trigger", "change", "limit", "counterplay", "feedback")),
            "links": rows(("from", "to", "decision_effect"))}),
        "actors": obj(("agents",), {"agents": rows(
            ("id", "role", "perception", "states", "action_refs", "telegraph", "counterplay", "variation"),
            {"states": STRINGS, "action_refs": STRINGS})}),
        "world": obj(("topology", "spaces", "transitions"), {
            "topology": TEXT,
            "spaces": rows(("id", "purpose", "interactive_states", "route_choices"),
                           {"interactive_states": STRINGS, "route_choices": STRINGS}),
            "transitions": rows(("from", "to", "condition", "new_decision", "return_reason"), minimum=0)}),
        "progression": obj(("nodes", "reset_policy", "long_horizon"), {
            "nodes": rows(("id", "unlock", "prerequisites", "new_decision", "revisit_effect"),
                          {"prerequisites": EMPTY_STRINGS}),
            "reset_policy": TEXT, "long_horizon": TEXT}),
        "rewards": obj(("entries", "fairness_recovery"), {
            "entries": rows(("id", "trigger", "grants", "feedback", "purpose", "cap_or_rule")),
            "fairness_recovery": TEXT}),
        "learning": obj(("curriculum", "timing", "return_resume"), {
            "curriculum": rows(("id", "teaches", "practice", "assessment", "remediation"), {"unlock_ref": TEXT}),
            "timing": TEXT, "return_resume": TEXT}),
        "art": obj(("style", "production_route"), {
            "style": obj(("shape", "materials", "palette", "lighting", "motion", "ui", "audio", "haptics")),
            "production_route": obj(("tools", "editable_sources", "exports", "runtime_import", "cost", "license", "risks", "verified_status"), {
                "tools": STRINGS, "editable_sources": TEXT, "exports": TEXT,
                "runtime_import": TEXT, "cost": TEXT, "license": TEXT,
                "risks": TEXT, "verified_status": TEXT})}),
        "commerce": obj(("model", "resources", "offers", "journeys"), {
            "model": {"type": "string", "enum": ["none", "premium", "dlc", "ads", "iap", "pass", "subscription", "hybrid"]},
            "resources": rows(("id", "sources", "sinks", "cap", "reset", "persistence"),
                              {"sources": STRINGS, "sinks": STRINGS}, minimum=0),
            "offers": rows(("id", "desire", "grants", "earned_path", "decline_path", "limits", "cumulative_effect", "price_basis"), minimum=0),
            "journeys": rows(("id", "trigger", "steps", "cancel_recovery", "restore_or_reconcile"),
                             {"steps": STRINGS}, minimum=0),
            "no_offer_reason": TEXT, "free_path": TEXT, "dominance_counterexample": TEXT}),
        "lifecycle": obj(("launch_scope", "content_grammar", "support_plan"), {
            "launch_scope": obj(("content_units", "early", "mid", "late", "end_or_replay")),
            "content_grammar": obj(("vocabulary", "composition_rules", "forbidden_combinations", "novel_decisions"), {
                k: STRINGS for k in ("vocabulary", "composition_rules", "forbidden_combinations", "novel_decisions")}),
            "support_plan": obj(("save", "resume", "offline", "update", "finite_content_end"))}),
        "equipment": obj(("items",), {"items": rows(("id", "function", "properties", "rule_refs", "progression", "tradeoff"), {
            "properties": rows(("name", "effect", "limit")), "rule_refs": STRINGS})}),
    }


def schema(version=VERSION):
    if version != VERSION:
        raise ValueError("unsupported game-model schema version: " + str(version) + "; create the current model from the current project requirements")
    features = {name: obj(("enabled", "rationale"), {
        "enabled": {"type": "boolean"}, "rationale": TEXT}) for name in DOMAINS}
    evidence = rows(("id", "domain", "check_id", "stage", "modality", "proof_path", "sha256", "model_sha256",
                     "observer_id", "author_ids", "method", "observed_at", "environment", "origin", "scope_sha256"), {
        "domain": {"type": "string", "enum": list(DOMAINS) + ["product"]},
        "stage": {"type": "string", "enum": list(STAGES)},
        "modality": {"type": "string", "enum": sorted(MODALITIES)},
        "origin": {"type": "string", "enum": sorted(ORIGINS)},
        "sha256": {"type": "string", "pattern": HASH.pattern},
        "model_sha256": {"type": "string", "pattern": HASH.pattern},
        "scope_sha256": {"type": "string", "pattern": HASH.pattern},
        "build_sha256": {"type": "string", "pattern": HASH.pattern},
        "scenario_ids": STRINGS,
        "platform": TEXT,
        "status": {"type": "string", "enum": ["current", "superseded"]},
        "superseded_by": TEXT,
        "author_ids": EMPTY_STRINGS}, minimum=0)
    result = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:game-atelier:game-model:4.0.0",
        "title": "Game Atelier typed game model (structural schema, not quality certification)",
        **obj(("schema_version", "id", "title", "author_ids", "source_requirement_ids", "constraints", "features", "domains", "dependencies", "scenarios", "evidence"), {
            "schema_version": {"const": version}, "id": TEXT, "title": TEXT,
            "author_ids": STRINGS, "source_requirement_ids": STRINGS,
            "constraints": obj(("platforms", "target_fps", "extra_paid_services"), {
                "platforms": STRINGS, "target_fps": {"type": "number", "exclusiveMinimum": 0},
                "extra_paid_services": {"type": "boolean"}}),
            "features": {**obj(DOMAINS, features), "additionalProperties": False},
            "domains": {"type": "object", "properties": domain_schemas(), "additionalProperties": False},
            "dependencies": rows(("from", "to", "reason"), minimum=0),
            "scenarios": rows(("id", "domains", "initial_state", "action", "expected_observable", "changed_decision", "without_rule"), {
                "domains": {"type": "array", "items": {"type": "string", "enum": list(DOMAINS)}, "minItems": 1},
                "due_stage": {"type": "string", "enum": ["slice", "beta", "release"]}}),
            "spec_refs": rows(("domain", "path", "sha256"), {
                "domain": {"type": "string", "enum": list(DOMAINS)},
                "sha256": {"type": "string", "pattern": HASH.pattern}}, minimum=0),
            "evidence": evidence})}
    result["required"].append("production")
    result["properties"]["production"] = v4().schema()
    return result


def check_type(value, spec, path, errors):
    """Small, explicit subset used by our bundled JSON schema; no dependencies."""
    typ = spec.get("type")
    matches = {"object": isinstance(value, dict), "array": isinstance(value, list),
               "string": isinstance(value, str), "boolean": type(value) is bool,
               "integer": type(value) is int, "number": type(value) in (int, float)}
    if typ and not matches[typ]:
        errors.append(path + " must be " + typ)
        return
    if "const" in spec and value != spec["const"]:
        errors.append(path + " has unsupported value")
    if "enum" in spec and value not in spec["enum"]:
        errors.append(path + " has unsupported value")
    if typ == "string":
        if not value.strip() and spec.get("minLength"):
            errors.append(path + " must be nonempty text")
        if "pattern" in spec and not re.fullmatch(spec["pattern"], value):
            errors.append(path + " has invalid format")
    if typ in ("integer", "number"):
        if value != value or value in (float("inf"), float("-inf")):
            errors.append(path + " must be finite")
        for key, bad in (("minimum", lambda n: value < n), ("maximum", lambda n: value > n),
                         ("exclusiveMinimum", lambda n: value <= n)):
            if key in spec and bad(spec[key]):
                errors.append(path + " violates " + key)
    if typ == "array":
        if len(value) < spec.get("minItems", 0):
            errors.append(path + " has too few entries")
        for i, item in enumerate(value):
            check_type(item, spec.get("items", {}), "{}[{}]".format(path, i), errors)
    if typ == "object":
        for key in spec.get("required", []):
            if key not in value:
                errors.append(path + "." + key + " is required")
        props = spec.get("properties", {})
        for key, item in value.items():
            if key in props:
                check_type(item, props[key], path + "." + key, errors)
            elif spec.get("additionalProperties") is False:
                errors.append(path + "." + key + " is unknown")


def digest(model):
    body = {k: v for k, v in model.items() if k != "evidence"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def scope_digest(model, domain, check_id):
    """Hash declared semantic inputs, not every unrelated model field.

    Ownership and typed references add dependency edges. Explicit upstream
    dependencies must still be complete; this is not a semantic inference
    engine. The integrator reviews missing edges before accepting proof reuse.
    """
    if model.get("schema_version") == VERSION and check_id.startswith("v4."):
        return v4().scope_digest(model, check_id)
    if check_id == "product.applicability":
        return digest(model)
    common = {"schema_version": model["schema_version"], "model_id": model["id"],
              "source_requirement_ids": model["source_requirement_ids"],
              "constraints": model["constraints"], "author_ids": model["author_ids"],
              "domain": domain, "check_id": check_id}
    if domain == "product":
        # Build/device receipts attest to actual artifact bytes and platform
        # observations. Behavioral compatibility is checked by domain scopes,
        # not by pretending a build receipt proves every design rule.
        common["applicability"] = model["features"]
    else:
        payloads = {model["id"]: {k: v for k, v in model.items() if k != "evidence"}}
        owner = {}
        upstream = defaultdict(set)
        for name in enabled(model):
            payloads[name] = model["domains"][name]
            owner[name] = name
            def walk(value):
                if isinstance(value, dict):
                    if isinstance(value.get("id"), str):
                        payloads[value["id"]] = value
                        owner[value["id"]] = name
                        upstream[name].add(value["id"])
                    for child in value.values():
                        walk(child)
                elif isinstance(value, list):
                    for child in value:
                        walk(child)
            walk(model["domains"][name])
        for edge in model["dependencies"]:
            upstream[edge["to"]].add(edge["from"])
        for link in model["domains"]["systems"]["links"]:
            upstream[link["to"]].add(link["from"])
        for actor in model["domains"].get("actors", {}).get("agents", []):
            upstream[actor["id"]].update(actor["action_refs"])
        for item in model["domains"].get("equipment", {}).get("items", []):
            upstream[item["id"]].update(item["rule_refs"])
        for node in model["domains"].get("progression", {}).get("nodes", []):
            upstream[node["id"]].update(node["prerequisites"])
        for lesson in model["domains"].get("learning", {}).get("curriculum", []):
            if lesson.get("unlock_ref"):
                upstream[lesson["id"]].add(lesson["unlock_ref"])
        wanted, queue = {domain}, deque([domain])
        while queue:
            current = queue.popleft()
            for parent in upstream[current]:
                if parent not in wanted:
                    wanted.add(parent)
                    queue.append(parent)
        owners = {owner[x] for x in wanted if x in owner}
        common["applicability"] = {name: model["features"][name] for name in sorted(owners)}
        common["payloads"] = {name: payloads[name] for name in sorted(wanted) if name in payloads}
        common["declared_upstream_edges"] = sorted(
            (edge for edge in model["dependencies"] if edge["to"] in wanted),
            key=lambda edge: (edge["from"], edge["to"], edge["reason"]))
        common["scenarios"] = [s for s in model["scenarios"] if domain in s["domains"] or s["id"] in wanted]
        common["spec_refs"] = sorted(
            (ref for ref in model.get("spec_refs", []) if ref["domain"] in owners),
            key=lambda ref: (ref["domain"], ref["path"]))
    if model.get("schema_version") == VERSION and domain != "product":
        mapping = {"camera": ["TR13"], "input": ["TR13"], "systems": ["TR03", "TR04"],
                   "actors": ["TR06"], "world": ["TR07", "TR08"], "progression": ["TR09", "TR10"],
                   "rewards": ["TR11"], "learning": ["TR14"], "art": ["TR15", "TR16", "TR18"],
                   "commerce": ["TR12"], "lifecycle": ["TR17", "TR20"], "equipment": ["TR05"]}
        common["production_scopes"] = {ident: v4().scope_digest(model, "v4." + ident + ".contract")
                                       for ident in mapping.get(domain, [])}
    return hashlib.sha256(json.dumps(common, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError("nonfinite JSON number: " + value)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      parse_constant=reject, object_pairs_hook=pairs)


def safe_file(root, name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("invalid relative proof/spec path")
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts or ":" in name or "\x00" in name:
        raise ValueError("unsafe relative proof/spec path: " + name)
    root = root.resolve()
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("proof/spec symlink escapes model directory: " + name)
    if not path.is_file():
        raise ValueError("proof/spec file missing: " + name)
    return path


def enabled(model):
    return {d for d in DOMAINS if model.get("features", {}).get(d, {}).get("enabled") is True}


def entity_index(model):
    found = defaultdict(list)
    found[model.get("id", "")].append("model")
    for domain in enabled(model):
        found[domain].append("domain")
        def walk(value, location):
            if isinstance(value, dict):
                if isinstance(value.get("id"), str):
                    found[value["id"]].append(domain)
                for key, child in value.items():
                    walk(child, location + "." + key)
            elif isinstance(value, list):
                for child in value:
                    walk(child, location)
        walk(model.get("domains", {}).get(domain, {}), domain)
    if model.get("schema_version") == VERSION:
        def production_walk(value):
            if isinstance(value, dict):
                if isinstance(value.get("id"), str):
                    found[value["id"]].append("production")
                for key, child in value.items():
                    if key not in {"cases", "migration", "body", "operations"}:
                        production_walk(child)
            elif isinstance(value, list):
                for child in value:
                    production_walk(child)
        production_walk(model.get("production", {}))
        for kind in ("capabilities", "recipes", "transformations", "attempts", "assemblies", "obligations"):
            for record in model.get("production", {}).get("operations", {}).get(kind, []):
                if isinstance(record, dict) and isinstance(record.get("id"), str):
                    found[record["id"]].append("production.operations." + kind)
    for scenario in model.get("scenarios", []):
        if isinstance(scenario, dict) and isinstance(scenario.get("id"), str):
            found[scenario["id"]].append("scenario")
    return found


def cycle(graph):
    active, done = set(), set()
    def visit(node):
        if node in active:
            return True
        if node in done:
            return False
        active.add(node)
        if any(visit(child) for child in graph.get(node, [])):
            return True
        active.remove(node)
        done.add(node)
        return False
    return any(visit(node) for node in graph)


def design_errors(model):
    errors = []
    try:
        model_schema = schema(model.get("schema_version"))
    except ValueError as exc:
        return [str(exc)]
    check_type(model, model_schema, "model", errors)
    if errors:
        return errors
    active = enabled(model)
    for domain in DOMAINS:
        if domain in CORE and domain not in active:
            errors.append("core domain cannot be disabled: " + domain)
        if domain in active and domain not in model["domains"]:
            errors.append("enabled domain payload missing: " + domain)
        if domain not in active and domain in model["domains"]:
            errors.append("disabled domain has active payload: " + domain)
    if errors:
        return errors
    index = entity_index(model)
    for ident, owners in index.items():
        if len(owners) != 1:
            errors.append("duplicate ID: " + ident)
    for edge in model["dependencies"]:
        for key in ("from", "to"):
            if edge[key] not in index:
                errors.append("dependency references missing ID: " + edge[key])
    covered = set()
    for scenario in model["scenarios"]:
        domains = set(scenario["domains"])
        if not domains <= active:
            errors.append("scenario references inactive domain: " + scenario["id"])
        covered |= domains
    for domain in sorted(active - covered):
        errors.append("domain has no observable scenario: " + domain)
    if not any(len(set(s["domains"])) > 1 for s in model["scenarios"]):
        errors.append("at least one cross-domain causal scenario is required")
    camera = model["domains"].get("camera", {})
    fraction = camera.get("subject_fraction")
    if fraction and fraction["min"] > fraction["max"]:
        errors.append("camera subject_fraction min exceeds max")
    rules = {r["id"] for r in model["domains"]["systems"]["rules"]}
    for link in model["domains"]["systems"]["links"]:
        if link["from"] not in rules or link["to"] not in rules:
            errors.append("system link must reference rules")
    for actor in model["domains"].get("actors", {}).get("agents", []):
        if not set(actor["action_refs"]) <= rules:
            errors.append("actor action_refs must reference rules: " + actor["id"])
    for item in model["domains"].get("equipment", {}).get("items", []):
        if not set(item["rule_refs"]) <= rules:
            errors.append("equipment rule_refs must reference rules: " + item["id"])
    world = model["domains"].get("world", {})
    spaces = {s["id"] for s in world.get("spaces", [])}
    for transition in world.get("transitions", []):
        if transition["from"] not in spaces or transition["to"] not in spaces:
            errors.append("world transition must reference spaces")
    progression = model["domains"].get("progression", {})
    nodes = {n["id"] for n in progression.get("nodes", [])}
    graph = {}
    for node in progression.get("nodes", []):
        graph[node["id"]] = node["prerequisites"]
        if not set(node["prerequisites"]) <= nodes:
            errors.append("unlock prerequisites reference missing node: " + node["id"])
    if cycle(graph):
        errors.append("progression prerequisite cycle")
    for lesson in model["domains"].get("learning", {}).get("curriculum", []):
        if lesson.get("unlock_ref") and lesson["unlock_ref"] not in nodes:
            errors.append("lesson unlock_ref references missing progression node")
    commerce = model["domains"].get("commerce", {})
    if commerce.get("model") == "none":
        if not isinstance(commerce.get("no_offer_reason"), str) or not commerce["no_offer_reason"].strip():
            errors.append("no-offer commerce requires no_offer_reason")
        if commerce["offers"] or commerce["journeys"]:
            errors.append("no-offer commerce cannot contain offers/journeys")
    elif commerce:
        for key in ("free_path", "dominance_counterexample"):
            if not isinstance(commerce.get(key), str) or not commerce[key].strip():
                errors.append("commerce requires " + key)
        if not commerce["offers"] or not commerce["journeys"]:
            errors.append("commercial model requires concrete offers and journeys")
    # Source IDs and actual subject coverage are retained; lexical equality is
    # a warning only in portfolio, not a counterfeit depth certificate here.
    if len(set(model["source_requirement_ids"])) != len(model["source_requirement_ids"]):
        errors.append("duplicate source requirement ID")
    evidence_ids = [e["id"] for e in model["evidence"]]
    if len(evidence_ids) != len(set(evidence_ids)) or set(evidence_ids) & set(index):
        errors.append("duplicate evidence/entity ID")
    evidence_index = {e["id"]: e for e in model["evidence"]}
    for evidence in model["evidence"]:
        if evidence.get("status") == "superseded":
            replacement = evidence_index.get(evidence.get("superseded_by"), {})
            if not replacement or replacement is evidence or replacement.get("status", "current") != "current" or replacement["check_id"] != evidence["check_id"] or replacement["origin"] == "historical_reference":
                errors.append("superseded evidence requires a current replacement for the same check: " + evidence["id"])
    if model.get("schema_version") == VERSION:
        errors.extend(v4().errors(model))
    return sorted(set(errors))


def requirements(model, stage, maturity=None):
    """Normative due checks: no task flag or receipt can disable these."""
    active = enabled(model)
    due = []
    def add(ident, domain, at, modality, origin, independent=False, motion=False):
        if STAGES.index(at) <= STAGES.index(stage):
            due.append({"id": ident, "domain": domain, "due_stage": at,
                        "modality": modality, "origin": origin,
                        "independent": independent, "motion_required": motion,
                        "required_scenario_ids": [s["id"] for s in model["scenarios"]
                            if (domain == "product" or domain in s["domains"])
                            and (modality == "document" or STAGES.index(s.get("due_stage", "slice")) <= STAGES.index(stage))]})
    add("product.applicability", "product", "concept", "document", "design_review", True)
    for domain in sorted(active):
        add(domain + ".design", domain, "concept", "document", "design_review", True)
        add(domain + ".contract", domain, "preproduction", "document", "contract_review", True)
        add(domain + ".runtime", domain, "slice", "runtime", "runtime_capture",
            motion=domain in {"camera", "input", "actors"})
        if domain in {"input", "learning", "systems", "lifecycle", "actors", "world", "progression", "rewards", "commerce"}:
            add(domain + ".player", domain, "beta", "player", "player_observation")
        add(domain + ".release", domain, "release", "document", "release_review", True)
    add("product.native_build", "product", "slice", "build", "native_build")
    add("product.device", "product", "slice", "device", "device_observation")
    add("product.release_device", "product", "release", "device", "device_observation")
    commerce = model.get("domains", {}).get("commerce", {})
    if commerce and commerce.get("model") != "none":
        add("commerce.integration", "commerce", "release", "external_receipt", "external_receipt", True)
    if model.get("schema_version") == VERSION:
        due.extend(v4().requirements(model, stage, maturity))
    return due


def media_kind(path):
    with path.open("rb") as stream:
        head = stream.read(64)
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image"
    if head.startswith(b"\xff\xd8\xff") or (head[:4] == b"RIFF" and head[8:12] == b"WEBP"):
        return "image"
    if head.startswith(b"\x1aE\xdf\xa3") or (len(head) >= 12 and head[4:8] == b"ftyp"):
        return "video"
    return None


def checked_sample(root, sample):
    if not isinstance(sample, dict) or not all(k in sample for k in ("path", "sha256", "kind")):
        raise ValueError("sample requires path/sha256/kind")
    path = safe_file(root, sample["path"])
    if sample["sha256"] != sha(path):
        raise ValueError("sample hash mismatch: " + sample["path"])
    actual = media_kind(path)
    if sample["kind"] in {"image", "video"} and actual != sample["kind"]:
        raise ValueError("sample bytes do not match declared media: " + sample["path"])
    if sample["kind"] == "trace":
        trace = read_json(path)
        events = trace.get("events", []) if isinstance(trace, dict) else []
        if len(events) < 2 or any(not isinstance(e, dict) or type(e.get("t")) not in (int, float) or "state" not in e for e in events):
            raise ValueError("timed trace requires at least two timestamped states")
        if any(a["t"] >= b["t"] for a, b in zip(events, events[1:])):
            raise ValueError("trace timestamps must increase")
        return "trace"
    if sample["kind"] not in {"image", "video", "trace", "document"}:
        raise ValueError("unknown sample kind")
    if sample["kind"] == "document":
        if path.suffix not in {".json", ".md", ".txt", ".csv"} or not path.read_text(encoding="utf-8").strip():
            raise ValueError("document sample needs actual nonempty text")
    return actual or sample["kind"]


def native_artifact(path, platform):
    """Container integrity only; does not establish signing/device execution."""
    if not zipfile.is_zipfile(path):
        raise ValueError("native build artifact must be a readable APK/AAB/IPA/app zip")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if any(Path(n).is_absolute() or ".." in Path(n).parts or "\\" in n for n in names):
            raise ValueError("native artifact has unsafe paths")
        if archive.testzip() is not None:
            raise ValueError("native artifact CRC failure")
        if platform == "android":
            ok = ("AndroidManifest.xml" in names and any(n.endswith(".dex") or n.startswith("lib/") for n in names)) or (
                "BundleConfig.pb" in names and "base/manifest/AndroidManifest.xml" in names)
        elif platform == "ios":
            ok = any(n.startswith("Payload/") and ".app/" in n and n.endswith("/Info.plist") for n in names)
        else:
            raise ValueError("native artifact platform must be android or ios")
        if not ok:
            raise ValueError("native artifact lacks platform container markers")


def proof_errors(model, evidence, requirement, root):
    errors = []
    try:
        if not evidence.get("scope_sha256"):
            raise ValueError("evidence requires the current dependency scope hash")
        if evidence["scope_sha256"] != scope_digest(model, requirement["domain"], requirement["id"]):
            raise ValueError("evidence dependency scope hash is stale")
        if evidence["domain"] != requirement["domain"] or evidence["modality"] != requirement["modality"] or evidence["origin"] != requirement["origin"]:
            raise ValueError("evidence domain/modality/origin does not match normative check")
        if STAGES.index(evidence["stage"]) < STAGES.index(requirement["due_stage"]):
            raise ValueError("evidence predates required stage")
        if requirement["independent"] and evidence["observer_id"] in set(model["author_ids"]) | set(evidence["author_ids"]):
            raise ValueError("independent review observer is an author")
        try:
            stamp = datetime.fromisoformat(evidence["observed_at"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise ValueError("observed_at must be ISO-8601 with timezone")
        if stamp.tzinfo is None:
            raise ValueError("observed_at must include timezone")
        if stamp > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("observed_at cannot be in the future beyond clock skew")
        path = safe_file(root, evidence["proof_path"])
        if sha(path) != evidence["sha256"]:
            raise ValueError("proof hash mismatch")
        modality = evidence["modality"]
        if modality == "document":
            if path.suffix not in {".md", ".txt", ".json"} or not path.read_text(encoding="utf-8").strip():
                raise ValueError("document review needs nonempty readable text")
            return []
        actual = media_kind(path)
        if modality == "runtime" and actual:
            if not HASH.fullmatch(str(evidence.get("build_sha256", ""))):
                raise ValueError("direct runtime media needs build_sha256 metadata")
            scenarios = {s["id"] for s in model["scenarios"]}
            refs = evidence.get("scenario_ids")
            if not isinstance(refs, list) or not refs or not set(refs) <= scenarios:
                raise ValueError("direct runtime media needs valid scenario_ids metadata")
            if not set(refs) & set(requirement["required_scenario_ids"]):
                raise ValueError("runtime scenario_ids do not exercise the required due domain")
            if evidence.get("platform") not in model["constraints"]["platforms"]:
                raise ValueError("direct runtime media requires a declared target platform")
            if requirement["motion_required"] and actual != "video":
                raise ValueError("this runtime check requires motion evidence")
            return []
        if path.suffix != ".json":
            raise ValueError("proof is neither recognized runtime media nor a structured JSON receipt")
        receipt = read_json(path)
        if not isinstance(receipt, dict) or receipt.get("schema_version") != "game-atelier-observation/1" or receipt.get("kind") != modality:
            raise ValueError("receipt schema/kind mismatch")
        if not HASH.fullmatch(str(receipt.get("build_sha256", ""))):
            raise ValueError("receipt requires build_sha256")
        scenarios = {s["id"] for s in model["scenarios"]}
        refs = receipt.get("scenario_ids")
        if not isinstance(refs, list) or not refs or not set(refs) <= scenarios:
            raise ValueError("receipt scenario_ids must reference model scenarios")
        if not set(refs) & set(requirement["required_scenario_ids"]):
            raise ValueError("receipt scenario_ids do not exercise the required due domain")
        samples = receipt.get("samples")
        if not isinstance(samples, list) or not samples:
            raise ValueError("receipt requires supporting samples")
        kinds = [checked_sample(root, sample) for sample in samples]
        if modality in {"runtime", "device"} and not set(kinds) & {"image", "video"}:
            raise ValueError("runtime/device observation requires captured state evidence")
        if requirement["motion_required"] and not ("video" in kinds or {"trace", "image"} <= set(kinds)):
            raise ValueError("runtime motion observation requires video or timed states with captured media")
        if modality == "device":
            device = receipt.get("device", {})
            if not isinstance(device, dict):
                raise ValueError("device must be an object")
            if device.get("physical") is not True or not all(isinstance(device.get(k), str) and device[k].strip() for k in ("platform", "model", "os")):
                raise ValueError("device receipt needs explicit physical platform/model/os")
            if device["platform"] not in model["constraints"]["platforms"]:
                raise ValueError("device platform outside model constraints")
        elif receipt.get("platform") not in model["constraints"]["platforms"]:
            raise ValueError("native observation requires a declared target platform")
        if modality == "player":
            outcomes = receipt.get("outcomes")
            if type(receipt.get("participant_count")) is not int or receipt["participant_count"] < 1 or not isinstance(receipt.get("method"), str) or not receipt["method"].strip():
                raise ValueError("player receipt needs participants and observation method")
            if not isinstance(outcomes, list) or not outcomes or any(not isinstance(o, dict) or o.get("scenario_id") not in refs or not isinstance(o.get("observation"), str) or not o["observation"].strip() for o in outcomes):
                raise ValueError("player receipt needs concrete scenario outcomes")
            if {o["scenario_id"] for o in outcomes} != set(refs):
                raise ValueError("player receipt must record an outcome for every claimed scenario")
        if modality == "build":
            for key in ("platform", "artifact_path", "artifact_sha256", "toolchain"):
                if not isinstance(receipt.get(key), str) or not receipt[key].strip():
                    raise ValueError("build receipt missing " + key)
            artifact = safe_file(root, receipt["artifact_path"])
            artifact_hash = sha(artifact)
            if artifact_hash != receipt["artifact_sha256"] or artifact_hash != receipt["build_sha256"]:
                raise ValueError("native artifact/build hash mismatch")
            if receipt["platform"] not in model["constraints"]["platforms"]:
                raise ValueError("build platform outside model constraints")
            native_artifact(artifact, receipt["platform"])
        if modality == "external_receipt":
            for key in ("provider", "operation", "observed_status", "transaction_reference"):
                if not isinstance(receipt.get(key), str) or not receipt[key].strip():
                    raise ValueError("external receipt missing " + key)
            if receipt["observed_status"] not in {"succeeded", "confirmed", "verified"}:
                raise ValueError("external operation is not confirmed")
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        errors.append(str(exc))
    return errors


def spec_errors(model, stage, root):
    if STAGES.index(stage) < STAGES.index("preproduction"):
        return []
    errors, covered = [], set()
    for ref in model.get("spec_refs", []):
        try:
            path = safe_file(root, ref["path"])
            if ref["domain"] not in enabled(model):
                raise ValueError("spec ref uses inactive domain")
            if sha(path) != ref["sha256"]:
                raise ValueError("spec hash mismatch: " + ref["path"])
            covered.add(ref["domain"])
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    errors += ["missing pinned detailed spec: " + d for d in sorted(enabled(model) - covered)]
    return errors


def plan(model, stage, maturity=None):
    errors = design_errors(model)
    is_v4 = model.get("schema_version") == VERSION
    effective_maturity = v4().maturity_for_stage(model, stage, maturity) if is_v4 else None
    if is_v4 and stage != "concept" and maturity not in {None, "T"}:
        errors.append("preproduction and later gates require maturity T; flags cannot lower it")
    if is_v4 and not errors:
        errors.extend(v4().errors(model, effective_maturity, stage=stage))
    checks = requirements(model, stage, effective_maturity) if not errors else []
    for check in checks:
        check["scope_sha256"] = scope_digest(model, check["domain"], check["id"])
    return {"toolkit_version": TOOLKIT_VERSION, "model_schema_version": model.get("schema_version"),
            "maturity": effective_maturity,
            "model_id": model.get("id"), "stage": stage,
            "model_sha256": digest(model), "structurally_valid": not errors,
            "errors": errors, "required_checks": checks,
            "required_spec_domains": sorted(enabled(model)) if stage != "concept" else [],
            "stage_ready": False, "quality_certified": False,
            "limitations": ["No model execution or fun certification; professional and player review remain necessary.",
                            "Proof bytes and actor records cannot establish actual human/device truth alone.",
                            "Scoped proof reuse requires an integrator to inspect completeness of semantic dependencies."]}


def validate(model, root, stage="concept", design_only=False, maturity=None):
    result = plan(model, stage, maturity)
    result["mode"] = "design_only" if design_only else "stage_gate"
    result["missing_checks"], result["evidence_errors"] = [], []
    if result["errors"] or design_only:
        return result
    if model.get("schema_version") == VERSION:
        result["errors"] += v4().errors(model, result["maturity"], root=root, stage=stage)
        if result["maturity"] == "C0":
            result["errors"].append("C0 is an unfinished sketch; never a completed concept or handoff")
    result["errors"] += spec_errors(model, stage, root)
    due = {r["id"]: r for r in result["required_checks"]}
    all_checks = {r["id"] for r in requirements(model, "release")}
    if model.get("schema_version") == VERSION:
        all_checks |= {r["id"] for r in v4().requirements(model, "concept", "C1")}
    by_check = defaultdict(list)
    for evidence in model["evidence"]:
        if evidence["origin"] == "historical_reference" or evidence.get("status") == "superseded":
            continue
        if evidence["check_id"] in due:
            by_check[evidence["check_id"]].append(evidence)
        elif evidence["check_id"] not in all_checks and evidence["origin"] != "historical_reference":
            result["evidence_errors"].append({"id": evidence["id"], "errors": ["unknown check_id"]})
    for ident, requirement in due.items():
        candidates = by_check.get(ident, [])
        valid = False
        for evidence in candidates:
            defects = proof_errors(model, evidence, requirement, root)
            if defects:
                result["evidence_errors"].append({"id": evidence["id"], "errors": defects})
            else:
                valid = True
        if not valid:
            result["missing_checks"].append(ident)
        if requirement["modality"] != "document":
            covered = set()
            for ev in candidates:
                if not proof_errors(model, ev, requirement, root):
                    proof = safe_file(root, ev["proof_path"])
                    meta = ev if media_kind(proof) else read_json(proof)
                    covered.update(meta["scenario_ids"])
            missing = set(requirement["required_scenario_ids"]) - covered
            if not requirement["required_scenario_ids"]:
                result["errors"].append("no representative scenario due for native check: " + ident)
            elif missing:
                result["missing_checks"].append(ident + ":scenarios:" + ",".join(sorted(missing)))
    if STAGES.index(stage) >= STAGES.index("slice"):
        # Link captures/observations to an actual byte-pinned native artifact
        # receipt in this model. A plausible screenshot plus an arbitrary build
        # name is not enough. This still does not prove a real device/player.
        known_builds = defaultdict(set)
        for ev in by_check.get("product.native_build", []):
            if not proof_errors(model, ev, due["product.native_build"], root):
                receipt = read_json(safe_file(root, ev["proof_path"]))
                known_builds[receipt["platform"]].add(receipt["build_sha256"])
        if model.get("schema_version") == VERSION:
            evidence_index = {e["id"]: e for e in model["evidence"]}
            for assembly in model["production"]["operations"].get("assemblies", []):
                if assembly.get("proof_level") != "native_verified":
                    continue
                scope = assembly.get("native_scope", {})
                platform = scope.get("platform") if isinstance(scope, dict) else None
                build_hash = assembly.get("build_digest")
                scenario = assembly.get("scenario")
                scenario_id = scenario.get("id") if isinstance(scenario, dict) else scenario
                if build_hash not in known_builds[platform]:
                    result["errors"].append("native assembly lacks validated platform build artifact linkage: " + assembly.get("id", "unknown"))
                # A native claim must consume an actual checked device receipt,
                # not only a declared evidence ID or a candidate screenshot.
                observed = False
                for ref in assembly.get("evidence_refs", []):
                    ev = evidence_index.get(ref)
                    if not ev or ev.get("modality") != "device" or ev.get("status") == "superseded":
                        continue
                    requirement = due.get(ev["check_id"])
                    if not requirement or proof_errors(model, ev, requirement, root):
                        continue
                    receipt = read_json(safe_file(root, ev["proof_path"]))
                    if (receipt.get("build_sha256") == build_hash
                            and receipt.get("device", {}).get("platform") == platform
                            and scenario_id in receipt.get("scenario_ids", [])):
                        observed = True
                if not observed:
                    result["errors"].append("native assembly lacks validated matching device observation: " + assembly.get("id", "unknown"))
        for ident, requirement in due.items():
            if requirement["modality"] not in {"runtime", "device", "player", "external_receipt"}:
                continue
            linked = False
            for ev in by_check.get(ident, []):
                if proof_errors(model, ev, requirement, root):
                    continue
                proof = safe_file(root, ev["proof_path"])
                meta = ev if media_kind(proof) else read_json(proof)
                build_hash = meta.get("build_sha256")
                platform = meta.get("device", {}).get("platform") if requirement["modality"] == "device" else meta.get("platform")
                if build_hash in known_builds[platform]:
                    linked = True
                else:
                    result["evidence_errors"].append({"id": ev["id"], "errors": ["observation does not reference a validated native build artifact for its platform"]})
            if by_check.get(ident) and not linked and ident not in result["missing_checks"]:
                result["missing_checks"].append(ident)
    # Native readiness is platform-specific. A single Android receipt cannot
    # close a model whose declared target also includes iOS.
    if STAGES.index(stage) >= STAGES.index("slice"):
        for platform in set(model["constraints"]["platforms"]) & {"android", "ios"}:
            platform_checks = ["product.native_build", "product.device"]
            if stage == "release":
                platform_checks.append("product.release_device")
            for check in platform_checks:
                covered = set()
                for ev in by_check.get(check, []):
                    if proof_errors(model, ev, due[check], root):
                        continue
                    try:
                        receipt = read_json(safe_file(root, ev["proof_path"]))
                        observed = receipt.get("platform") if check.endswith("native_build") else receipt.get("device", {}).get("platform")
                        if observed == platform and (check.endswith("native_build") or receipt["build_sha256"] in known_builds[platform]):
                            covered.update(receipt["scenario_ids"])
                    except (ValueError, OSError):
                        pass
                if not set(due[check]["required_scenario_ids"]) <= covered:
                    result["missing_checks"].append(check + ":" + platform)
    result["stage_ready"] = not (result["errors"] or result["missing_checks"] or result["evidence_errors"])
    return result


# Domain-level consequences supplement project-authored graph edges. They do
# not require that an inapplicable feature be activated.
CROSS_IMPACT = {
    "camera": {"input", "world", "actors", "art", "learning", "lifecycle"},
    "input": {"camera", "systems", "actors", "learning", "art"},
    "systems": {"actors", "world", "progression", "rewards", "equipment", "learning", "commerce", "lifecycle"},
    "actors": {"systems", "world", "input", "progression", "rewards", "learning", "art"},
    "world": {"camera", "systems", "actors", "progression", "rewards", "learning", "art", "lifecycle"},
    "progression": {"systems", "equipment", "actors", "world", "rewards", "learning", "commerce", "lifecycle"},
    "rewards": {"progression", "systems", "commerce", "learning", "lifecycle"},
    "learning": {"input", "art", "lifecycle"},
    "art": {"camera", "input", "actors", "world", "learning", "lifecycle"},
    "commerce": {"systems", "progression", "rewards", "equipment", "learning", "lifecycle"},
    "equipment": {"systems", "actors", "input", "progression", "rewards", "commerce", "art"},
    "lifecycle": {"world", "progression", "rewards", "commerce", "learning"},
}


def impact(model, changed):
    errors = design_errors(model)
    index = entity_index(model) if not errors else {}
    if errors:
        return {"errors": errors, "quality_certified": False}
    if changed not in index:
        return {"errors": ["unknown changed ID: " + changed], "quality_certified": False}
    graph = defaultdict(set)
    for edge in model["dependencies"]:
        graph[edge["from"]].add(edge["to"])
    for scenario in model["scenarios"]:
        for domain in scenario["domains"]:
            graph[domain].add(scenario["id"])
    owners = {owner for owner in index[changed] if owner in DOMAINS}
    if changed in enabled(model):
        owners.add(changed)
    if changed == model["id"]:
        owners |= enabled(model)
    starts = {changed} | owners
    seen, queue = set(starts), deque(starts)
    while queue:
        current = queue.popleft()
        for downstream in graph[current]:
            if downstream not in seen:
                seen.add(downstream)
                queue.append(downstream)
    direct_domains = owners | {d for d in enabled(model) if d in seen}
    for ident in seen:
        direct_domains |= {o for o in index.get(ident, []) if o in DOMAINS}
    # One normative hop is a review recommendation. Do not transitively fan
    # out every generic dependency until it opens all domains on every edit.
    review_domains = set(direct_domains)
    for domain in direct_domains:
        review_domains |= CROSS_IMPACT.get(domain, set()) & enabled(model)
    checks = [r["id"] for r in requirements(model, "release")
              if r["domain"] in review_domains or r["domain"] == "product"]
    result = {"model_id": model["id"], "changed": changed,
            "affected_ids": sorted(seen), "direct_domains": sorted(direct_domains),
            "review_domains": sorted(review_domains), "checks_to_revisit": checks,
            "requires_semantic_triage": True, "quality_certified": False,
            "note": "Review impact before invalidating unaffected proof; this command makes no mutations."}
    if model.get("schema_version") == VERSION:
        result["production_impact"] = v4().impact(model, changed)
    return result


AXES = ("scale", "topology", "projection", "tracking", "framing", "genre", "input", "art", "commerce")


def facets(candidate):
    if "facets" in candidate:
        return candidate["facets"]
    domains = candidate.get("domains", {})
    camera = domains.get("camera", {})
    fraction = camera.get("subject_fraction", {})
    return {
        "scale": candidate.get("portfolio", {}).get("scale", "unspecified"),
        "topology": domains.get("world", {}).get("topology", "not_applicable"),
        "projection": camera.get("projection", "not_applicable"),
        "tracking": camera.get("tracking", "not_applicable"),
        "framing": candidate.get("portfolio", {}).get("framing", str(fraction) if fraction else "not_applicable"),
        "genre": candidate.get("portfolio", {}).get("genre", "unspecified"),
        "input": domains.get("input", {}).get("scheme", "unspecified"),
        "art": candidate.get("portfolio", {}).get("art", domains.get("art", {}).get("style", {}).get("shape", "unspecified")),
        "commerce": domains.get("commerce", {}).get("model", "not_applicable")}


def tokens(text):
    return set(re.findall(r"[\w]+", text.lower(), re.UNICODE))


def portfolio(data):
    candidates = data.get("candidates") if isinstance(data, dict) else None
    errors = []
    if not isinstance(candidates, list) or not candidates:
        return {"errors": ["portfolio requires nonempty candidates array"], "quality_certified": False}
    prepared, seen = [], set()
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("id"), str) or not candidate["id"].strip():
            errors.append("candidate needs stable id")
            continue
        if candidate["id"] in seen:
            errors.append("duplicate portfolio candidate ID: " + candidate["id"])
        seen.add(candidate["id"])
        if "schema_version" in candidate:
            errors.extend(candidate["id"] + ": " + e for e in design_errors(candidate))
        fs = facets(candidate)
        if not isinstance(fs, dict) or any(not isinstance(fs.get(a), str) or not fs[a].strip() for a in AXES):
            errors.append(candidate["id"] + ": all independent facet axes require text")
            continue
        signature = candidate.get("decision_signature")
        if signature is None:
            signature = " ".join(s.get("changed_decision", "") for s in candidate.get("scenarios", []))
        if not isinstance(signature, str) or not signature.strip():
            errors.append(candidate["id"] + ": decision_signature or model scenarios required")
            continue
        if not isinstance(candidate.get("source_requirement_ids"), list) or not candidate["source_requirement_ids"]:
            errors.append(candidate["id"] + ": source_requirement_ids required")
        prepared.append((candidate["id"], fs, tokens(signature)))
    distributions = {axis: dict(Counter(fs[axis] for _, fs, _ in prepared)) for axis in AXES}
    neighbors = []
    for i, (ident, fs, ts) in enumerate(prepared):
        for other, ofs, ots in prepared[i + 1:]:
            equal = [a for a in AXES if fs[a].casefold() == ofs[a].casefold()]
            similarity = len(ts & ots) / len(ts | ots) if ts | ots else 0
            if len(equal) >= 6 or similarity >= .55:
                neighbors.append({"candidates": [ident, other], "matching_axes": equal,
                                  "decision_token_overlap": round(similarity, 3),
                                  "status": "needs_semantic_neighbor_review"})
    return {"candidate_count": len(prepared), "distributions": distributions,
            "neighbors": neighbors, "errors": errors, "quality_certified": False,
            "semantic_diversity_certified": False,
            "note": "Heuristic neighbor flags and declared facets require actual design/image review; no automatic quality score."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "plan", "impact", "portfolio"):
        child = sub.add_parser(command)
        child.add_argument("file", type=Path)
        child.add_argument("--json", action="store_true", help="emit machine-readable JSON")
        if command in {"validate", "plan"}:
            child.add_argument("--stage", choices=STAGES, default=None)
            child.add_argument("--maturity", choices=("C0", "C1", "T"), default=None)
        if command == "validate":
            child.add_argument("--design-only", action="store_true", help="authoring structure only; never stage ready")
        if command == "impact":
            child.add_argument("--changed", required=True)
    args = parser.parse_args(argv)
    if getattr(args, "design_only", False) and args.stage:
        parser.error("--design-only cannot be combined with --stage")
    try:
        data = read_json(args.file)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        if args.command == "portfolio":
            result = portfolio(data)
        elif args.command == "impact":
            result = impact(data, args.changed)
        elif args.command == "plan":
            result = plan(data, args.stage or "concept", args.maturity)
        else:
            result = validate(data, args.file.parent, args.stage or "concept", args.design_only, args.maturity)
        ok = not result.get("errors")
        if args.command == "validate" and not args.design_only:
            ok = result["stage_ready"]
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if ok else 1
    except (ValueError, OSError, TypeError, RecursionError) as exc:
        print(json.dumps({"errors": [str(exc)], "quality_certified": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
