#!/usr/bin/env python3
"""Validate declared production contracts, never execute jobs or infer proof.

The records belong to canonical Game Model.production.operations. A standalone
JSON file is accepted only as a linked artifact whose digest the model owns.
validate(operations, root=None) returns actionable errors; an empty list proves
structural consistency only. Optional root verifies declared local file bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VERSION = "4.0.0"
KINDS = ("capabilities", "recipes", "transformations", "attempts", "assemblies", "obligations")
PROOFS = ("candidate", "descriptor_discovered", "schema_discovered", "catalog_verified",
          "configured", "operation_tested", "integrated", "native_verified")
TESTED = {"operation_tested", "integrated", "native_verified"}
ATTEMPT_STATES = {"pending", "submitted", "running", "unknown", "cancel_requested",
                  "succeeded", "failed", "cancelled", "effect_absent"}
UNRESOLVED = {"pending", "submitted", "running", "unknown", "cancel_requested"}
SHA_LENGTH = 64
GATES = ("C0", "C1", "T", "A", "B", "Q", "R", "L")


def _sha(value):
    return isinstance(value, str) and len(value) == SHA_LENGTH and all(c in "0123456789abcdef" for c in value)


def _present(value):
    return value not in (None, "", [], {})


def _cycle(nodes):
    active, complete = set(), set()
    def visit(key):
        if key in active:
            return True
        if key in complete:
            return False
        active.add(key)
        for parent in nodes.get(key, []):
            if isinstance(parent, str) and parent in nodes and visit(parent):
                return True
        active.remove(key)
        complete.add(key)
        return False
    return any(visit(key) for key in nodes)


def _validate_records(operations, root=None, context=None):
    """Return list[str] errors. No semantic, native, human or truth guarantee."""
    errors = []
    def fail(where, message):
        errors.append(f"{where}: {message}")
    def require(record, fields, where):
        if not isinstance(record, dict):
            fail(where, "expected object")
            return False
        for field in fields:
            if not _present(record.get(field)):
                fail(where, f"missing {field}")
        return True
    if not isinstance(operations, dict):
        return ["production.operations: expected object"]
    gate = operations.get("gate", "C0")
    if gate not in GATES:
        fail("production.operations", "unknown gate")
    records, id_kind = {}, {}
    for kind in KINDS:
        rows = operations.get(kind, [])
        if not isinstance(rows, list):
            fail(kind, "expected array")
            continue
        records[kind] = {}
        for index, item in enumerate(rows):
            where = f"{kind}[{index}]"
            if not require(item, ["id"], where):
                continue
            ident = item.get("id")
            if not isinstance(ident, str) or not ident.strip():
                fail(where, "id must be nonempty string")
                continue
            if ident in id_kind:
                fail(where, f"duplicate record id {ident}")
            id_kind[ident] = kind
            records[kind][ident] = item
    def ref(ident, kind, where):
        if not isinstance(ident, str) or ident not in records.get(kind, {}):
            fail(where, f"unknown {kind} reference {ident}")
            return None
        return records[kind][ident]
    def strings(record, field, where, nonempty=False):
        values = record.get(field, [])
        if not isinstance(values, list) or any(not isinstance(value, str) or not value.strip() for value in values):
            fail(where, f"{field} must be an array of nonempty strings")
            return []
        if nonempty and not values:
            fail(where, f"{field} must be nonempty")
        return values
    context = context if isinstance(context, dict) else {}
    evidence_index = {row["id"]: row for row in context.get("evidence", [])
                      if isinstance(row, dict) and isinstance(row.get("id"), str)}
    scenario_ids = {row["id"] for row in context.get("scenarios", [])
                    if isinstance(row, dict) and isinstance(row.get("id"), str)}
    def artifacts(items, where, check_bytes=False):
        if not isinstance(items, list):
            fail(where, "expected artifact array")
            return
        ids = set()
        for idx, item in enumerate(items):
            loc = f"{where}[{idx}]"
            if not require(item, ["id", "sha256"], loc):
                continue
            artifact_id = item.get("id")
            if not isinstance(artifact_id, str):
                fail(loc, "artifact id must be string")
                continue
            if artifact_id in ids:
                fail(loc, "duplicate artifact id")
            ids.add(artifact_id)
            if not _sha(item.get("sha256")):
                fail(loc, "invalid sha256")
            if check_bytes and root is not None and item.get("path"):
                base = Path(root).resolve()
                path = (base / item["path"]).resolve()
                if not path.is_relative_to(base):
                    fail(loc, "path escapes declared root")
                elif not path.is_file():
                    fail(loc, "declared file absent")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
                    fail(loc, "file digest mismatch")
    def budget_fields(record, field, where):
        budget = record.get(field)
        if not isinstance(budget, dict):
            fail(where, f"{field} expected object")
            return
        for name in ("maximum_minor_units", "observed_minor_units", "reserved_minor_units"):
            value = budget.get(name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                fail(where, f"{name} must be nonnegative integer minor units")
        maximum = budget.get("maximum_minor_units")
        if isinstance(maximum, int) and maximum > 0 and not _present(budget.get("authorized_scope_ref")):
            fail(where, "paid budget needs authorized_scope_ref")
        observed = budget.get("observed_minor_units")
        if isinstance(maximum, int) and isinstance(observed, int) and observed > maximum:
            fail(where, "actual cost exceeds declared budget; preserve receipt and escalate")
    for ident, cap in records.get("capabilities", {}).items():
        where = f"capability:{ident}"
        require(cap, ["operation_id", "tool", "toolchain", "host", "target", "supported_outputs",
                      "proof_level", "freshness", "rights", "cost", "fallback"], where)
        budget_fields(cap, "cost", where)
        strings(cap, "supported_outputs", where, True)
        strings(cap, "witness_refs", where)
        level = cap.get("proof_level")
        if level not in PROOFS:
            fail(where, "unknown proof_level")
        if level in TESTED:
            require(cap, ["witness_refs", "subject_digest"], where)
            if not _sha(cap.get("subject_digest")):
                fail(where, "tested capability requires subject digest")
            if cap.get("stale"):
                fail(where, "tested capability is stale")
            current = cap.get("current_subject_digest")
            if current is not None and current != cap.get("subject_digest"):
                fail(where, "capability witness subject changed")
        if level == "native_verified":
            require(cap, ["native_scope"], where)
        bindings = cap.get("parameter_bindings", [])
        if not isinstance(bindings, list):
            fail(where, "parameter_bindings expected array")
        else:
            for binding in bindings:
                if require(binding, ["requirement_id", "schema_field", "supported", "consumption_check"], where + ":binding"):
                    if binding.get("material") and binding.get("supported") is not True:
                        fail(where, "unsupported material parameter")
    for ident, recipe in records.get("recipes", {}).items():
        where = f"recipe:{ident}"
        require(recipe, ["requirement_ids", "owner", "consumer", "inputs", "outputs", "steps",
                         "budget", "allowed_effects", "acceptance", "repair"], where)
        budget_fields(recipe, "budget", where)
        strings(recipe, "requirement_ids", where, True)
        strings(recipe, "allowed_effects", where, True)
        strings(recipe, "transformation_ids", where)
        if recipe.get("status") not in {"template", "planned", "bound", "accepted"}:
            fail(where, "unknown recipe status")
        if recipe.get("status") in {"bound", "accepted"}:
            artifacts(recipe.get("inputs"), where + ":inputs", check_bytes=True)
        outputs = recipe.get("outputs", [])
        if not isinstance(outputs, list):
            fail(where, "outputs expected array")
            outputs = []
        for output in outputs:
            require(output, ["id", "type", "consumer", "acceptance"], where + ":output")
        steps = recipe.get("steps", [])
        if not isinstance(steps, list):
            fail(where, "steps expected array")
            continue
        graph = {}
        for step in steps:
            if not require(step, ["id", "operation_id", "capability_id", "binding", "output_ids", "validator"], where + ":step"):
                continue
            strings(step, "output_ids", where + ":step", True)
            sid = step.get("id")
            if not isinstance(sid, str):
                fail(where, "step id must be string")
                continue
            if sid in graph:
                fail(where, f"duplicate step {sid}")
            graph[sid] = step.get("depends_on", [])
            if not isinstance(graph[sid], list):
                fail(where, f"depends_on must be array for {sid}")
                graph[sid] = []
            cap = ref(step.get("capability_id"), "capabilities", where)
            if cap and cap.get("operation_id") != step.get("operation_id"):
                fail(where, f"operation mismatch in {sid}")
            if cap and recipe.get("status") in {"bound", "accepted"} and cap.get("stale"):
                fail(where, f"stale capability in {sid}")
            binding = step.get("binding")
            if isinstance(binding, dict):
                kind = binding.get("kind")
                if kind == "command":
                    argv = binding.get("argv")
                    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
                        fail(where, f"command binding needs argv array in {sid}")
                elif kind == "api":
                    require(binding, ["tool_id", "schema_ref", "fields"], where + ":api")
                elif kind == "procedure":
                    require(binding, ["actions", "preset_refs", "expected_observations"], where + ":procedure")
                else:
                    fail(where, f"unknown binding kind in {sid}")
            else:
                fail(where, f"invalid binding in {sid}")
        for sid, parents in graph.items():
            for parent in parents:
                if not isinstance(parent, str) or parent not in graph:
                    fail(where, f"unknown step dependency {parent}")
        if _cycle(graph):
            fail(where, "execution step DAG contains cycle")
        for transform in recipe.get("transformation_ids", []):
            ref(transform, "transformations", where)
    artifact_ids = set()
    artifact_definitions = {}
    for recipe in records.get("recipes", {}).values():
        for field in ("inputs", "outputs"):
            rows = recipe.get(field, [])
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and isinstance(row.get("id"), str):
                        artifact_ids.add(row["id"])
                        artifact_definitions[row["id"]] = {**artifact_definitions.get(row["id"], {}), **row}
        output_ids = {row["id"] for row in recipe.get("outputs", []) if isinstance(row, dict) and isinstance(row.get("id"), str)} if isinstance(recipe.get("outputs"), list) else set()
        for step in recipe.get("steps", []) if isinstance(recipe.get("steps"), list) else []:
            if isinstance(step, dict):
                for output in step.get("output_ids", []) if isinstance(step.get("output_ids"), list) else []:
                    if not isinstance(output, str) or output not in output_ids:
                        fail("recipe:" + recipe["id"], "step output absent from declared output inventory")
    for ident, trans in records.get("transformations", {}).items():
        where = f"transformation:{ident}"
        require(trans, ["source_ref", "target_ref", "conventions", "preserved_invariants",
                        "mapping", "validators"], where)
        for field in ("source_ref", "target_ref"):
            if not isinstance(trans.get(field), str) or trans.get(field) not in artifact_ids:
                fail(where, f"{field} absent from recipe artifact inventory")
        for field in ("intentional_changes", "known_losses", "uncertainties"):
            if not isinstance(trans.get(field), list):
                fail(where, f"{field} expected array, including explicit empty array")
    effect_keys, attempt_graph = {}, {}
    for ident, attempt in records.get("attempts", {}).items():
        where = f"attempt:{ident}"
        require(attempt, ["recipe_id", "effect_key", "recipe_digest", "input_digests", "toolchain_digests",
                          "status", "observations", "cost"], where)
        budget_fields(attempt, "cost", where)
        recipe = ref(attempt.get("recipe_id"), "recipes", where)
        if recipe and recipe.get("status") not in {"bound", "accepted"}:
            fail(where, "attempt requires bound recipe")
        if not _sha(attempt.get("recipe_digest")):
            fail(where, "invalid recipe_digest")
        status = attempt.get("status")
        if status not in ATTEMPT_STATES:
            fail(where, "unknown attempt status")
        observations = attempt.get("observations")
        if not isinstance(observations, list) or not observations:
            fail(where, "append-only observations required")
        else:
            last = observations[-1]
            if not isinstance(last, dict) or last.get("status") != status:
                fail(where, "status differs from latest observation")
            previous = -1
            for observation in observations:
                if not isinstance(observation, dict):
                    fail(where, "observation expected object")
                    continue
                seq = observation.get("sequence")
                if not isinstance(seq, int) or seq <= previous:
                    fail(where, "observation sequence must strictly increase")
                previous = seq if isinstance(seq, int) else previous
                require(observation, ["at", "status", "receipt_ref"], where + ":observation")
        if status in {"submitted", "running", "succeeded"}:
            require(attempt, ["run_ref"], where)
        if status in {"unknown", "cancel_requested"}:
            require(attempt, ["reconciliation"], where)
        if status == "succeeded":
            require(attempt, ["receipt_ref", "outputs"], where)
            artifacts(attempt.get("outputs"), where + ":outputs", check_bytes=True)
            if recipe:
                declared = {row["id"]: row for row in recipe.get("outputs", [])
                            if isinstance(row, dict) and isinstance(row.get("id"), str)}
                expected = set(declared)
                if attempt.get("step_id"):
                    step = next((row for row in recipe.get("steps", []) if row.get("id") == attempt["step_id"]), None)
                    if step is None:
                        fail(where, "unknown recipe step_id")
                        expected = set()
                    else:
                        expected = set(step.get("output_ids", []))
                produced = {row["id"] for row in attempt.get("outputs", [])
                            if isinstance(row, dict) and isinstance(row.get("id"), str)}
                if not produced <= expected:
                    fail(where, "successful output absent from declared recipe/step output inventory")
                required = {key for key in expected if declared.get(key, {}).get("required", True)}
                if not required <= produced:
                    fail(where, "succeeded attempt lacks required recipe/step outputs")
        key = attempt.get("effect_key")
        if isinstance(key, str) and key:
            effect_keys.setdefault(key, []).append((ident, status))
        else:
            fail(where, "effect_key must be string")
        prior = attempt.get("retry_of")
        attempt_graph[ident] = [prior] if isinstance(prior, str) and prior else []
        if prior:
            old = ref(prior, "attempts", where)
            if old and (old.get("status") in UNRESOLVED or old.get("status") == "succeeded"):
                fail(where, "retry before effect absence/failure reconciliation")
            if old and not _present(attempt.get("retry_reason")):
                fail(where, "retry_reason required")
    if _cycle(attempt_graph):
        fail("attempts", "retry DAG contains cycle")
    for key, states in effect_keys.items():
        if len(states) > 1 and any(state in UNRESOLVED or state == "succeeded" for _, state in states):
            fail("attempts", f"effect key {key} duplicated with unresolved/completed effect")
    def achieved(level, required):
        # Descriptor and schema are independent claims. Only configured/tested
        # levels imply readiness above catalogue discovery, never the reverse.
        if level == required:
            return True
        return level in PROOFS and required in PROOFS and PROOFS.index(level) >= PROOFS.index(required) and required not in {"descriptor_discovered", "schema_discovered"}
    for ident, cap in records.get("capabilities", {}).items():
        if cap.get("proof_level") not in TESTED:
            continue
        witnesses = strings(cap, "witness_refs", "capability:" + ident, True)
        for witness_id in witnesses:
            attempt = records.get("attempts", {}).get(witness_id)
            assembly = records.get("assemblies", {}).get(witness_id)
            if attempt is not None:
                if attempt.get("status") != "succeeded":
                    fail("capability:" + ident, "capability witness attempt has not succeeded")
                recipe = records.get("recipes", {}).get(attempt.get("recipe_id"), {})
                steps = recipe.get("steps", [])
                if attempt.get("step_id"):
                    steps = [step for step in steps if step.get("id") == attempt["step_id"]]
                if not any(step.get("capability_id") == ident for step in steps):
                    fail("capability:" + ident, "witness attempt does not exercise capability")
                if cap.get("proof_level") in {"integrated", "native_verified"}:
                    fail("capability:" + ident, "integrated/native capability needs matching assembly witness")
            elif assembly is not None:
                if not achieved(assembly.get("proof_level"), cap.get("proof_level")):
                    fail("capability:" + ident, "assembly witness proof insufficient")
                if ident not in assembly.get("capability_ids", []):
                    fail("capability:" + ident, "assembly witness does not bind capability")
            else:
                fail("capability:" + ident, "unknown capability witness reference " + witness_id)
    for ident, assembly in records.get("assemblies", {}).items():
        where = f"assembly:{ident}"
        require(assembly, ["scene_ref", "build_digest", "config_digest", "components", "scenario",
                           "invariants", "evidence_refs", "author_id", "reviewer_id", "proof_level"], where)
        for field in ("build_digest", "config_digest"):
            if not _sha(assembly.get(field)):
                fail(where, f"invalid {field}")
        if assembly.get("author_id") == assembly.get("reviewer_id"):
            fail(where, "independent assembly reviewer equals author")
        artifacts(assembly.get("components"), where + ":components")
        references = strings(assembly, "evidence_refs", where, True)
        scenario = assembly.get("scenario")
        scenario_id = scenario.get("id") if isinstance(scenario, dict) else scenario
        if not isinstance(scenario_id, str) or scenario_id not in scenario_ids:
            fail(where, "unknown assembly scenario reference")
        scene = assembly.get("scene_ref")
        scene_definition = artifact_definitions.get(scene) if isinstance(scene, str) else None
        if scene_definition is not None:
            if not any(token in str(scene_definition.get("type", "")).casefold() for token in ("scene", "tscn", "prefab", "umap")):
                fail(where, "scene_ref artifact is not declared as scene format")
        elif root is not None and isinstance(scene, str) and _sha(assembly.get("scene_digest")):
            artifacts([{"id": "assembly-scene", "path": scene, "sha256": assembly["scene_digest"]}], where + ":scene", True)
        else:
            fail(where, "scene_ref must bind declared scene artifact or pinned local scene file")
        runtime_witness = False
        for evidence_id in references:
            evidence = evidence_index.get(evidence_id)
            if evidence is None:
                fail(where, "unknown canonical evidence reference " + evidence_id)
                continue
            if evidence.get("origin") == "historical_reference" or evidence.get("status") == "superseded":
                fail(where, "assembly evidence is historical/superseded")
            if evidence.get("modality") in {"runtime", "device"}:
                if evidence.get("build_sha256") != assembly.get("build_digest"):
                    fail(where, "runtime evidence build differs from assembly")
                if scenario_id not in evidence.get("scenario_ids", []):
                    fail(where, "runtime evidence does not exercise assembly scenario")
                runtime_witness = True
        if assembly.get("proof_level") in {"integrated", "native_verified"} and not runtime_witness:
            fail(where, "assembly needs canonical runtime/device witness")
        components = assembly.get("components", [])
        if isinstance(components, list):
            for component in components:
                require(component, ["binding"], where + ":component")
                if assembly.get("proof_level") in {"integrated", "native_verified"} and isinstance(component, dict):
                    actual = [output.get("sha256") for attempt in records.get("attempts", {}).values()
                              if attempt.get("status") == "succeeded"
                              for output in attempt.get("outputs", [])
                              if isinstance(output, dict) and output.get("id") == component.get("id")]
                    if component.get("sha256") not in actual:
                        fail(where, "assembly component lacks matching successful attempt output digest")
        invariants = assembly.get("invariants", [])
        if not isinstance(invariants, list):
            fail(where, "invariants expected array")
        else:
            for invariant in invariants:
                if require(invariant, ["id", "expected", "observed", "verdict"], where + ":invariant"):
                    if invariant.get("verdict") not in {"pending", "pass", "fail", "blocked"}:
                        fail(where, "unknown invariant verdict")
                    if assembly.get("proof_level") in {"integrated", "native_verified"} and invariant.get("verdict") != "pass":
                        fail(where, "assembly proof claims unresolved invariant")
        if assembly.get("proof_level") == "native_verified":
            require(assembly, ["native_scope"], where)
            scope = assembly.get("native_scope", {})
            if not isinstance(scope, dict):
                fail(where, "native_scope must be object")
                scope = {}
            if scope.get("platform") not in context.get("constraints", {}).get("platforms", []):
                fail(where, "native scope platform outside canonical target constraints")
            for evidence_id in references:
                evidence = evidence_index.get(evidence_id, {})
                if evidence.get("modality") in {"runtime", "device"} and evidence.get("platform") != scope.get("platform"):
                    fail(where, "native assembly evidence platform mismatch")
        if assembly.get("proof_level") not in PROOFS:
            fail(where, "unknown proof_level")
        if assembly.get("stale"):
            fail(where, "assembly evidence is stale")
    obligations = operations.get("obligations", [])
    if not isinstance(obligations, list):
        fail("obligations", "expected array")
    else:
        for obligation in obligations:
            if not require(obligation, ["id", "requirement_id", "artifact_type", "recipe_id", "due_gate", "status"], "obligation"):
                continue
            if not isinstance(obligation.get("requirement_id"), str):
                fail("obligation", "requirement_id must be nonempty string")
            if obligation.get("status") not in {"planned", "pending", "blocked", "accepted"}:
                fail("obligation", "unknown obligation status")
            recipe = ref(obligation.get("recipe_id"), "recipes", "obligation")
            if obligation.get("status") == "accepted" and recipe and recipe.get("status") != "accepted":
                fail("obligation", "accepted obligation requires accepted recipe")
            due_gate = obligation.get("due_gate")
            if due_gate not in GATES:
                fail("obligation", "unknown due_gate")
            if due_gate in GATES and gate in GATES and GATES.index(due_gate) <= GATES.index(gate) and obligation.get("status") != "accepted":
                fail("obligation", f"due obligation {obligation.get('id')} not accepted")
            required_proof = obligation.get("required_proof", "candidate")
            if required_proof not in PROOFS:
                fail("obligation", "unknown required_proof")
            if obligation.get("status") == "accepted" and required_proof != "candidate":
                witnesses = strings(obligation, "witness_refs", "obligation", True)
                for witness_id in witnesses:
                    witness_kind = id_kind.get(witness_id)
                    witness = records.get(witness_kind, {}).get(witness_id) if witness_kind else None
                    if witness_kind not in {"capabilities", "assemblies"} or witness is None:
                        fail("obligation", "unknown proof witness reference " + witness_id)
                        continue
                    if not achieved(witness.get("proof_level"), required_proof):
                        fail("obligation", "witness proof is insufficient for required_proof")
                    if witness.get("stale"):
                        fail("obligation", "proof witness is stale")
                    if witness_kind == "capabilities" and recipe and not any(step.get("capability_id") == witness_id for step in recipe.get("steps", [])):
                        fail("obligation", "proof witness capability does not belong to obligation recipe")
                    if witness_kind == "assemblies" and recipe:
                        output_ids = {row["id"] for row in recipe.get("outputs", []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
                        component_ids = {row["id"] for row in witness.get("components", []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
                        if not output_ids & component_ids:
                            fail("obligation", "proof witness assembly does not consume obligation recipe output")
    if gate in GATES and GATES.index(gate) >= GATES.index("A"):
        if not any(row.get("proof_level") == "native_verified" for row in records.get("assemblies", {}).values()):
            fail("assemblies", "slice and later gates require native_verified assembly; candidate records are plans")
    return errors


def validate(operations, root=None, context=None):
    """Return errors for malformed data instead of crashing the model validator.

    Contract validation checks declared structure, not the honesty of producers.
    Artifact aliases may repeat; record IDs must be unique.
    """
    try:
        return _validate_records(operations, root, context)
    except (TypeError, KeyError, ValueError, OSError) as error:
        return [f"production.operations: malformed record data ({type(error).__name__}: {error})"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--root", type=Path, help="Optional local bytes root; no effects performed")
    args = parser.parse_args()
    try:
        document = json.loads(args.file.read_text(encoding="utf-8"))
        operations = document.get("production", {}).get("operations", document)
        errors = validate(operations, args.root, context=document if "production" in document else None)
    except (OSError, ValueError, TypeError) as error:
        errors = [str(error)]
    print(json.dumps({"validator": "production_contract", "version": VERSION,
                      "scope": "declared_structure_refs_dag_and_evidence_boundaries_only",
                      "valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
