#!/usr/bin/env python3
"""Validate systemic concept passports and their pre-illustration receipts.

This stdlib-only check verifies structure, references and pinned declarations.
It does not infer fun, depth, balance, ergonomics, production fidelity or FPS.
Use --for-illustration only with actual independent reviews and current profile
evidence. It never creates approval, edits input, or executes referenced files.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path




def strict_json_loads(raw, **kwargs):
    """Reject ambiguous/nonfinite JSON before hashing, validation or mutation."""
    if len(raw) > 256 * 1024 * 1024:
        raise ValueError("JSON exceeds bounded input limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)
    kwargs.setdefault("object_pairs_hook", unique)
    kwargs.setdefault("parse_constant", finite)
    return json.loads(raw, **kwargs)


DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "assets" / "systemic-passport.schema.json"
REVIEW_SCOPE = "pre_illustration_systemic_passport"


def canonical_passport_sha256(passport):
    """Hash the whole passport, including preassigned review_refs and status."""
    raw = json.dumps(passport, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _normal(value):
    return re.sub(r"\W+", " ", str(value), flags=re.UNICODE).strip().casefold()


def _issue(issues, path, code, message):
    issues.append({"path": path, "code": code, "message": message})


def _matches_type(value, kind):
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(kind, False)


def validate_schema(value, schema, root=None, path="$", issues=None):
    """Validate the JSON-Schema subset used by the bundled passport schema.

    This is deliberately not advertised as a general JSON-Schema implementation.
    Unknown schema keywords are annotations; unsupported validation keywords in
    this bundled schema must be added together with tests before use.
    """
    if issues is None:
        issues = []
    if root is None:
        root = schema
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            _issue(issues, path, "schema_ref", "Only local schema references are supported")
            return issues
        target = root
        try:
            for part in ref[2:].split("/"):
                target = target[part.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError):
            _issue(issues, path, "schema_ref", "Unresolved bundled schema reference: " + ref)
            return issues
        return validate_schema(value, target, root, path, issues)
    kinds = schema.get("type")
    if kinds:
        allowed = kinds if isinstance(kinds, list) else [kinds]
        if not any(_matches_type(value, kind) for kind in allowed):
            _issue(issues, path, "type", "Expected " + "/".join(allowed))
            return issues
    if "const" in schema and value != schema["const"]:
        _issue(issues, path, "const", "Expected constant " + repr(schema["const"]))
    if "enum" in schema and value not in schema["enum"]:
        _issue(issues, path, "enum", "Value is outside the allowed vocabulary")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            _issue(issues, path, "empty", "A nonempty authored value is required")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            _issue(issues, path, "pattern", "Value does not match the required identifier pattern")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            _issue(issues, path, "min_items", "Required explanatory coverage is missing")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(v, sort_keys=True, ensure_ascii=False) for v in value]
            if len(set(encoded)) != len(encoded):
                _issue(issues, path, "duplicate_item", "Items must be unique")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], root, path + "[" + str(index) + "]", issues)
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                _issue(issues, path + "." + key, "required", "Required field is missing")
        for key, item in value.items():
            if key in properties:
                validate_schema(item, properties[key], root, path + "." + key, issues)
            elif schema.get("additionalProperties") is False:
                _issue(issues, path + "." + key, "unknown_field", "Unknown field; do not silently drop authored data")
    return issues


def _objects(value):
    return value if isinstance(value, list) else []


def _id_map(rows, key, path, issues):
    result = {}
    for index, row in enumerate(_objects(rows)):
        if not isinstance(row, dict):
            continue
        ident = row.get(key)
        if not _text(ident):
            continue
        if ident in result:
            _issue(issues, path + "[" + str(index) + "]." + key, "duplicate_id", "Duplicate ID " + ident)
        result[ident] = row
    return result


def _check_refs(values, known, path, issues):
    for index, ref in enumerate(_objects(values)):
        if not isinstance(ref, str) or ref not in known:
            _issue(issues, path + "[" + str(index) + "]", "unresolved_ref", "Unknown reference " + repr(ref))


def _registry(value, keys, path, issues):
    """Accept a named list, a raw record list, or an ID-to-record mapping."""
    if value is None:
        return {}
    rows = value
    if isinstance(value, dict):
        for key in keys:
            if key in value:
                rows = value[key]
                break
        else:
            if "id" in value:
                rows = [value]
            elif all(isinstance(v, dict) for v in value.values()):
                rows = [dict(v, id=v.get("id", k)) for k, v in value.items()]
            else:
                rows = []
    if isinstance(rows, dict):
        rows = [dict(v, id=v.get("id", k)) for k, v in rows.items() if isinstance(v, dict)]
    if not isinstance(rows, list):
        _issue(issues, path, "registry_type", "Registry must contain a list or ID-to-record mapping")
        return {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not _text(row.get("id")):
            _issue(issues, path + "[" + str(index) + "]", "registry_id", "Registry record needs a nonempty ID")
    return _id_map(rows, "id", path, issues)


def _normalized_collection(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("passports", "items", "cards"):
            if isinstance(value.get(key), list):
                return value[key]
        return [value]
    return [value]


def extract_passports(value):
    """Support raw passports, a list, or cards with a nested passport object."""
    result = []
    for row in _normalized_collection(value):
        if isinstance(row, dict):
            nested = row.get("systemic_passport", row.get("passport"))
            if isinstance(nested, dict):
                result.append(nested)
                continue
        result.append(row)
    return result


def _gameplay_signature(passport):
    """Catch exact reskins, without pretending to understand paraphrased ideas."""
    aliases = {}
    for key, prefix in (("systems", "S"), ("causal_interactions", "E"), ("contextual_resources", "R")):
        for index, row in enumerate(passport.get(key, [])):
            aliases[row["id"]] = prefix + str(index)

    def normalize(value):
        if isinstance(value, str):
            return aliases.get(value, value)
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items() if key not in ("id", "name")}
        return value

    material = {key: normalize(passport.get(key)) for key in ("systems", "causal_interactions", "contextual_resources", "ux", "evolution")}
    return json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _progression(passport, issues):
    evolution = passport.get("evolution", {})
    if not isinstance(evolution, dict):
        return
    milestones = {"early", "middle", "late"}
    graph = {key: set() for key in milestones}
    for index, link in enumerate(_objects(evolution.get("progression_links"))):
        if not isinstance(link, dict):
            continue
        origin, target = link.get("from"), link.get("to")
        at = "$.evolution.progression_links[" + str(index) + "]"
        if origin not in milestones or target not in milestones:
            _issue(issues, at, "progression_ref", "Progression link refers to an undefined milestone")
        elif origin == target:
            _issue(issues, at, "progression_self", "An unlock prerequisite cannot depend on itself")
        else:
            graph[origin].add(target)
    visiting, visited = set(), set()

    def visit(node):
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(node) for node in graph):
        _issue(issues, "$.evolution.progression_links", "progression_cycle", "Unlock dependencies contain a cycle")
    seen = {}
    for stage in ("early", "middle", "late"):
        row = evolution.get(stage)
        if isinstance(row, dict):
            signature = tuple(_normal(row.get(k, "")) for k in ("introduced_capability_or_world_state", "new_decision", "familiar_action_reinterpreted"))
            if signature in seen:
                _issue(issues, "$.evolution." + stage, "copied_evolution", "Milestone repeats " + seen[signature] + " without an authored decision difference")
            seen[signature] = stage


def _structural_links(passport, issues):
    if not isinstance(passport, dict):
        return
    systems = _id_map(passport.get("systems"), "id", "$.systems", issues)
    interactions = _id_map(passport.get("causal_interactions"), "id", "$.causal_interactions", issues)
    traces = _id_map(passport.get("causal_traces"), "id", "$.causal_traces", issues)
    resources = _id_map(passport.get("contextual_resources"), "id", "$.contextual_resources", issues)
    replay = passport.get("replay_grammar", {})
    contexts = _id_map(replay.get("concrete_contexts") if isinstance(replay, dict) else [], "id", "$.replay_grammar.concrete_contexts", issues)
    if set(systems) & set(interactions):
        _issue(issues, "$.causal_interactions", "ambiguous_mechanic_id", "System and interaction IDs must be disjoint")
    neighbours = {key: set() for key in systems}
    cross_family = False
    for ident, edge in interactions.items():
        at = "$.causal_interactions[" + ident + "]"
        origin, target = edge.get("from_system"), edge.get("to_system")
        for name, value in (("from_system", origin), ("to_system", target)):
            if value not in systems:
                _issue(issues, at + "." + name, "unresolved_system", "Unknown system " + repr(value))
        if origin in systems and target in systems:
            neighbours[origin].add(target)
            neighbours[target].add(origin)
            if systems[origin].get("family") != systems[target].get("family"):
                cross_family = True
    if systems and not cross_family:
        _issue(issues, "$.causal_interactions", "no_cross_family_edge", "No authored interaction crosses mechanic families")
    if systems:
        reachable, pending = set(), [next(iter(systems))]
        while pending:
            node = pending.pop()
            if node not in reachable:
                reachable.add(node)
                pending.extend(neighbours[node] - reachable)
        for node in set(systems) - reachable:
            _issue(issues, "$.systems[" + node + "]", "disconnected_system", "System is disconnected from the causal graph")
        for node, links in neighbours.items():
            if not (links - {node}):
                _issue(issues, "$.systems[" + node + "]", "isolated_system", "System has no interaction with another system")
    system_signatures = {}
    for ident, system in systems.items():
        signature = json.dumps({k: system.get(k) for k in ("family", "state_variables", "player_choices", "rules", "reader_cues")}, ensure_ascii=False, sort_keys=True)
        if signature in system_signatures:
            _issue(issues, "$.systems[" + ident + "]", "copied_system", "Authored system content duplicates " + system_signatures[signature])
        system_signatures[signature] = ident
    trace_signatures = {}
    for ident, trace in traces.items():
        at = "$.causal_traces[" + ident + "]"
        contrast = trace.get("contrast_trace_ref")
        if contrast not in traces or contrast == ident:
            _issue(issues, at + ".contrast_trace_ref", "contrast_ref", "Contrast must reference another recorded trace")
        for index, step in enumerate(_objects(trace.get("steps"))):
            if isinstance(step, dict):
                _check_refs(step.get("mechanic_refs"), set(systems) | set(interactions), at + ".steps[" + str(index) + "].mechanic_refs", issues)
        signature = json.dumps({k: trace.get(k) for k in ("initial_context", "player_goal", "steps", "ending_and_persistence", "mistake_and_recovery")}, ensure_ascii=False, sort_keys=True)
        if signature in trace_signatures:
            _issue(issues, at, "copied_trace", "Contrasted trace duplicates " + trace_signatures[signature])
        trace_signatures[signature] = ident
    for ident, resource in resources.items():
        at = "$.contextual_resources[" + ident + "]"
        owner = resource.get("system_ref")
        if owner not in systems:
            _issue(issues, at + ".system_ref", "unresolved_system", "Resource must be owned by a defined system")
        refs = resource.get("interaction_refs")
        _check_refs(refs, interactions, at + ".interaction_refs", issues)
        incident = any(owner in (interactions[r].get("from_system"), interactions[r].get("to_system")) for r in _objects(refs) if r in interactions)
        if owner in systems and not incident:
            _issue(issues, at + ".interaction_refs", "unbound_resource", "Resource must reference an incident causal interaction, not an unrelated edge")
    if resources and not any(r.get("kind") not in ("health", "economy") for r in resources.values()):
        _issue(issues, "$.contextual_resources", "only_generic_resources", "HP/economy alone does not cover the requested contextual resource system")
    context_signatures = {}
    for ident, context in contexts.items():
        at = "$.replay_grammar.concrete_contexts[" + ident + "]"
        other = context.get("other_context_ref")
        if other not in contexts or other == ident:
            _issue(issues, at + ".other_context_ref", "contrast_ref", "Context must reference another recorded context")
        signature = tuple(_normal(context.get(k, "")) for k in ("concrete_situation", "preferred_tactic_and_reason", "why_that_tactic_changes"))
        if signature in context_signatures:
            _issue(issues, at, "copied_context", "Replay context repeats " + context_signatures[signature])
        context_signatures[signature] = ident
    ux = passport.get("ux", {})
    if isinstance(ux, dict):
        labels = [_normal(r.get("input")) for r in _objects(ux.get("stable_input_grammar")) if isinstance(r, dict)]
        if len(labels) != len(set(labels)):
            _issue(issues, "$.ux.stable_input_grammar", "ambiguous_input", "Input labels are duplicated; author one stable context rule or distinguish the states")
    _progression(passport, issues)
    commerce = passport.get("alternate_experience_commerce", {})
    comparison = commerce.get("same_encounter_comparison", {}) if isinstance(commerce, dict) else {}
    if isinstance(comparison, dict):
        baseline, alternate = comparison.get("baseline_input_and_decisions"), comparison.get("alternate_input_and_decisions")
        if _text(baseline) and _normal(baseline) == _normal(alternate):
            _issue(issues, "$.alternate_experience_commerce.same_encounter_comparison", "identical_alternate", "Baseline and alternate contain identical input/decision descriptions")
        limit = _normal(comparison.get("alternate_limit_or_tradeoff", ""))
        if limit in {"none", "no tradeoff", "no limits", "немає", "відсутні", "без обмежень"}:
            _issue(issues, "$.alternate_experience_commerce.same_encounter_comparison.alternate_limit_or_tradeoff", "missing_tradeoff", "Explicitly absent limits do not cover alternate-experience tradeoffs")
    visual = passport.get("visual_production", {})
    if isinstance(visual, dict):
        profile_ref = visual.get("profile_ref")
        elements = _id_map(visual.get("element_map"), "element_id", "$.visual_production.element_map", issues)
        for ident, element in elements.items():
            if element.get("tool_profile_ref") != profile_ref:
                _issue(issues, "$.visual_production.element_map[" + ident + "].tool_profile_ref", "profile_mismatch", "Element must use this candidate's production profile; tool details belong inside that profile")
            if element.get("known_unknown_or_blocked") == "blocked":
                _issue(issues, "$.visual_production.element_map[" + ident + "]", "blocked_visual_element", "A blocked required element must be repaired or its route resolved before illustration")
    if passport.get("status") == "user_reference_accepted" and not _text(passport.get("user_acceptance_ref")):
        _issue(issues, "$.user_acceptance_ref", "acceptance_authority", "Accepted reference status requires an actual user authority reference")


def validate_passports(value, schema, profiles=None, evidence=None, reviews=None,
                       cards=None, for_illustration=False, images=None,
                       check_files=False, base_dir=None):
    issues, results = [], []
    passports = extract_passports(value)
    profile_map = _registry(profiles, ("profiles", "visual_production_profiles", "production_profiles", "items"), "$profiles", issues)
    evidence_value = evidence
    if evidence_value is None and isinstance(profiles, dict):
        evidence_value = profiles.get("capability_evidence", profiles.get("evidence"))
    evidence_map = _registry(evidence_value, ("capability_evidence", "evidence", "items"), "$evidence", issues)
    review_map = _registry(reviews, ("items", "reviews"), "$reviews", issues)
    image_map = {}
    # Image records naturally use concept_id rather than a separate generic ID.
    if images is not None:
        raw_images = images.get("images", images.get("items", [])) if isinstance(images, dict) else images
        if isinstance(raw_images, list):
            image_map = {}
            for row in raw_images:
                if isinstance(row, dict):
                    ident = row.get("concept_id", row.get("id"))
                    if ident in image_map:
                        _issue(issues, "$images", "duplicate_id", "Duplicate image record for " + str(ident))
                    if _text(ident):
                        image_map[ident] = row
    if for_illustration and profiles is None:
        _issue(issues, "$profiles", "profiles_required", "--for-illustration requires a current production-profile registry")
    if for_illustration and reviews is None:
        _issue(issues, "$reviews", "reviews_required", "--for-illustration requires actual independent semantic-review receipts")
    seen = set()
    gameplay_signatures = {}
    for index, passport in enumerate(passports):
        local = validate_schema(passport, schema)
        schema_valid = not local
        if schema_valid:
            _structural_links(passport, local)
        ident = passport.get("concept_id") if isinstance(passport, dict) else None
        if isinstance(ident, str) and ident in seen:
            _issue(local, "$.concept_id", "duplicate_concept", "Duplicate concept ID " + str(ident))
        if isinstance(ident, str):
            seen.add(ident)
        fingerprint = canonical_passport_sha256(passport)
        if not schema_valid:
            results.append({"concept_id": ident if isinstance(ident, str) else None,
                            "index": index, "canonical_passport_sha256": fingerprint,
                            "structurally_valid": False,
                            "semantic_review_receipts_verified": [], "issues": local})
            continue
        signature = _gameplay_signature(passport)
        if signature in gameplay_signatures:
            _issue(local, "$", "copied_candidate", "Authored gameplay structure exactly duplicates " + str(gameplay_signatures[signature]) + "; a title or identity change is not a new candidate")
        else:
            gameplay_signatures[signature] = ident
        if for_illustration and passport.get("status") == "repair":
            _issue(local, "$.status", "repair_pending", "Known repair status cannot pass the pre-illustration gate")
        visual = passport.get("visual_production", {}) if isinstance(passport, dict) else {}
        if isinstance(visual, dict) and profiles is not None:
            ref = visual.get("profile_ref")
            if ref not in profile_map:
                _issue(local, "$.visual_production.profile_ref", "unresolved_profile", "Production profile is not in the supplied registry")
            _check_refs(visual.get("capability_evidence_refs"), evidence_map, "$.visual_production.capability_evidence_refs", local)
        verified_refs = []
        refs = passport.get("review_refs", []) if isinstance(passport, dict) else []
        if reviews is not None or for_illustration:
            if for_illustration and not refs:
                _issue(local, "$.review_refs", "review_required", "No pinned semantic review is referenced")
            for ref in _objects(refs):
                review = review_map.get(ref)
                if review is None:
                    _issue(local, "$.review_refs", "unresolved_review", "Review receipt not found: " + str(ref))
                    continue
                if review.get("status") != "pass" or review.get("scope") != REVIEW_SCOPE:
                    _issue(local, "$.review_refs", "review_scope", "Review must pass the pre-illustration systemic-passport scope")
                    continue
                authors = review.get("author_ids")
                reviewer = review.get("reviewer_id")
                if not _text(reviewer) or not isinstance(authors, list) or not authors or not all(_text(a) for a in authors) or reviewer in authors:
                    _issue(local, "$.review_refs", "review_independence", "Review must identify an observer distinct from the recorded actual authors")
                    continue
                hashes = review.get("passport_hashes", {})
                if not isinstance(hashes, dict) or hashes.get(ident) != fingerprint:
                    _issue(local, "$.review_refs", "stale_review", "Review does not pin this exact current canonical passport hash")
                    continue
                requirements = passport.get("source_requirement_refs", [])
                checked = review.get("checked_requirement_refs", [])
                if not isinstance(checked, list) or not all(_text(r) for r in checked) or not set(requirements).issubset(set(checked)):
                    _issue(local, "$.review_refs", "review_coverage", "Review does not name all source requirements of this passport")
                    continue
                if not _text(review.get("limitations")):
                    _issue(local, "$.review_refs", "review_limits", "Review must state evidence limitations")
                    continue
                verified_refs.append(ref)
            if for_illustration and not verified_refs:
                _issue(local, "$.review_refs", "no_current_review", "No current independent semantic-review receipt covers this passport")
        if images is not None:
            record = image_map.get(ident)
            if record is None:
                _issue(local, "$image", "image_missing", "No image-reference record for this passport")
            else:
                if record.get("profile_ref") != visual.get("profile_ref"):
                    _issue(local, "$image.profile_ref", "image_profile", "Image references a different visual production profile")
                if check_files:
                    raw_path = record.get("path")
                    if not _text(raw_path):
                        _issue(local, "$image.path", "image_path", "Image record needs a real file path")
                    else:
                        image_path = Path(raw_path)
                        if not image_path.is_absolute():
                            image_path = Path(base_dir or ".") / image_path
                        if not image_path.is_file():
                            _issue(local, "$image.path", "image_file", "Referenced image file does not exist")
                        else:
                            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                            if digest != record.get("sha256"):
                                _issue(local, "$image.sha256", "image_hash", "Referenced image bytes differ from their recorded hash")
                if isinstance(record.get("visible_input_refs"), list):
                    ux = passport.get("ux", {})
                    input_labels = {r.get("input") for r in _objects(ux.get("stable_input_grammar")) if isinstance(r, dict)}
                    _check_refs(record["visible_input_refs"], input_labels, "$image.visible_input_refs", local)
        results.append({"concept_id": ident, "index": index,
                        "canonical_passport_sha256": fingerprint,
                        "structurally_valid": not local,
                        "semantic_review_receipts_verified": verified_refs,
                        "issues": local})
    linked_cards = cards
    if linked_cards is None and isinstance(value, dict) and "passports" in value:
        linked_cards = value.get("cards")
    if linked_cards is not None:
        card_ids = set()
        for index, card in enumerate(_normalized_collection(linked_cards)):
            if not isinstance(card, dict):
                _issue(issues, "$cards[" + str(index) + "]", "card_type", "Readable card must be an object")
                continue
            ident = card.get("id", card.get("concept_id"))
            ref = card.get("passport_ref", card.get("systemic_passport_ref"))
            if "id" in card and "concept_id" in card and card["id"] != card["concept_id"]:
                _issue(issues, "$cards[" + str(index) + "]", "card_identity_conflict", "id and concept_id must agree when both are present")
            if "passport_ref" in card and "systemic_passport_ref" in card and card["passport_ref"] != card["systemic_passport_ref"]:
                _issue(issues, "$cards[" + str(index) + "]", "card_identity_conflict", "Passport reference aliases must agree when both are present")
            if ident in card_ids:
                _issue(issues, "$cards[" + str(index) + "]", "duplicate_card", "Readable card ID is duplicated")
            card_ids.add(ident)
            if not _text(ref) or ref not in seen or ident != ref:
                _issue(issues, "$cards[" + str(index) + "]", "card_passport_link", "Card ID and passport_ref must resolve to the same concept passport")
        for missing in seen - card_ids:
            _issue(issues, "$cards", "card_missing", "No readable card is linked to passport " + missing)
    failures = len(issues) + sum(len(row["issues"]) for row in results)
    valid = not failures and bool(passports)
    if not passports:
        _issue(issues, "$", "empty_collection", "No candidate passports were supplied")
    return {
        "status": ("pre_illustration_receipts_valid" if for_illustration else "structurally_valid_review_pending") if valid else "repair_required",
        "valid": valid, "candidate_count": len(passports),
        "for_illustration": for_illustration,
        "hash_method": "sha256(canonical JSON: UTF-8, ensure_ascii=False, sort_keys=True, separators=(',',':')); whole passport",
        "quality_certified": False,
        "limitations": ["Structure and pinned receipt declarations only; independent review truth is not inferred.",
                        "No native build, device performance, human enjoyment, ergonomic feel or commercial outcome is certified.",
                        "Exact-copy detection cannot detect semantic paraphrases or judge meaningful variety."],
        "registry_issues": issues, "candidates": results,
    }


def _load(path):
    if path == "-":
        return strict_json_loads(sys.stdin.read(256 * 1024 * 1024 + 1))
    return strict_json_loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Passport, list, or {passports:[...],cards:[...]} JSON; '-' reads stdin")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Bundled systemic-passport schema (default: %(default)s)")
    parser.add_argument("--profiles", help="Current {profiles:[{id,...}],capability_evidence:[{id,...}]} registry")
    parser.add_argument("--evidence", help="Optional separate capability-evidence registry")
    parser.add_argument("--reviews", help="Actual independent semantic-review receipts; see review scope below")
    parser.add_argument("--cards", help="Readable cards linked by id and passport_ref")
    parser.add_argument("--for-illustration", action="store_true", help="Require resolved profiles/evidence plus current independent pre_illustration_systemic_passport receipts")
    parser.add_argument("--images", help="Optional {images:[{concept_id,path,sha256,profile_ref,visible_input_refs}]} reference records")
    parser.add_argument("--check-files", action="store_true", help="With --images, verify referenced file existence and exact SHA-256")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON rather than a short human report")
    args = parser.parse_args(argv)
    try:
        data, schema = _load(args.input), _load(args.schema)
        kwargs = {name: _load(getattr(args, name)) if getattr(args, name) else None for name in ("profiles", "evidence", "reviews", "cards", "images")}
        if args.check_files and not args.images:
            raise ValueError("--check-files requires --images")
        result = validate_passports(data, schema, for_illustration=args.for_illustration,
                                    check_files=args.check_files,
                                    base_dir=Path(args.input).resolve().parent if args.input != "-" else Path.cwd(), **kwargs)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({"status": "input_error", "valid": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["status"] + ": " + str(result["candidate_count"]) + " candidate(s)")
        for row in result["candidates"]:
            print(str(row["concept_id"]) + " " + row["canonical_passport_sha256"])
            for problem in row["issues"]:
                print("  " + problem["path"] + " [" + problem["code"] + "] " + problem["message"])
        for problem in result["registry_issues"]:
            print(problem["path"] + " [" + problem["code"] + "] " + problem["message"])
        print("No automatic claim of depth, fun, balance, ergonomics, native fidelity or FPS.")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
