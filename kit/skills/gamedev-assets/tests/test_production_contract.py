"""Synthetic structural fixtures, never claims of production execution."""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "production_contract.py"
spec = importlib.util.spec_from_file_location("production_contract", MODULE)
production = importlib.util.module_from_spec(spec)
spec.loader.exec_module(production)
SHA = "a" * 64


def valid_operations():
    """Smallest bound recipe fixture; no actual capability evidence is claimed."""
    return {
        "gate": "T",
        "capabilities": [{"id": "CAP-synthetic", "operation_id": "O07", "tool": "synthetic-tool",
            "toolchain": {"version": "fixture"}, "host": "fixture-host", "target": "fixture-target",
            "supported_outputs": ["PNG"], "proof_level": "candidate", "freshness": {"triggers": ["version"]},
            "rights": {"scope": "synthetic"}, "cost": {"maximum_minor_units": 0}, "fallback": "report blocker"}],
        "recipes": [{"id": "REC-synthetic", "status": "accepted", "requirement_ids": ["REQ-synthetic"],
            "owner": "fixture-author", "consumer": "fixture-consumer", "inputs": [{"id": "ART-source", "sha256": SHA}],
            "outputs": [{"id": "ART-export", "type": "PNG", "consumer": "fixture-consumer", "acceptance": ["fixture oracle"]}],
            "steps": [{"id": "STEP-export", "operation_id": "O07", "capability_id": "CAP-synthetic", "depends_on": [],
                "binding": {"kind": "command", "argv": ["fixture-tool", "--export", "fixture-source"]},
                "output_ids": ["ART-export"], "validator": "CHECK-synthetic"}],
            "transformation_ids": ["TR-synthetic"], "budget": {"maximum_minor_units": 0},
            "allowed_effects": ["local reversible fixture"], "acceptance": ["fixture oracle"], "repair": {"cap": 2}}],
        "transformations": [{"id": "TR-synthetic", "source_ref": "ART-source", "target_ref": "ART-export",
            "conventions": {"units": "pixels"}, "preserved_invariants": ["pivot"], "mapping": "identity for fixture",
            "validators": ["CHECK-synthetic"], "intentional_changes": [], "known_losses": [], "uncertainties": []}],
        "attempts": [], "assemblies": [],
        "obligations": [{"id": "OB-synthetic", "requirement_id": "REQ-synthetic", "artifact_type": "sprite",
            "recipe_id": "REC-synthetic", "due_gate": "T", "status": "accepted", "required_proof": "candidate"}]
    }


def attempt(ident="ATT-synthetic", status="pending"):
    item = {"id": ident, "recipe_id": "REC-synthetic", "effect_key": "fixture-effect", "recipe_digest": SHA,
        "input_digests": {"ART-source": SHA}, "toolchain_digests": {"tool": SHA}, "status": status,
        "observations": [{"sequence": 1, "at": "fixture-time", "status": status, "receipt_ref": "fixture-local-ledger"}],
        "cost": {"maximum_minor_units": 0}}
    if status in {"submitted", "running", "succeeded"}:
        item["run_ref"] = "fixture-local-run"
    if status in {"unknown", "cancel_requested"}:
        item["reconciliation"] = {"query": "fixture-query-before-repeat"}
    if status == "succeeded":
        item.update(receipt_ref="fixture-receipt", outputs=[{"id": "ART-export", "sha256": SHA}])
    return item


def native_operations():
    """Closed synthetic declarations; no physical/native truth is asserted."""
    data = valid_operations()
    data["gate"] = "A"
    recipe = data["recipes"][0]
    recipe["outputs"].append({"id": "ART-scene", "type": "Godot scene", "consumer": "fixture-runtime", "acceptance": ["fixture scene oracle"]})
    recipe["steps"][0]["output_ids"].append("ART-scene")
    done = attempt(status="succeeded")
    done["outputs"].append({"id": "ART-scene", "sha256": SHA})
    data["attempts"] = [done]
    data["assemblies"] = [{"id": "ASM-native", "scene_ref": "ART-scene", "build_digest": SHA,
        "config_digest": SHA, "components": [{"id": "ART-export", "sha256": SHA, "binding": "fixture-resource"},
            {"id": "ART-scene", "sha256": SHA, "binding": "fixture-scene"}],
        "scenario": "SCENARIO-slice", "invariants": [{"id": "INV-fixture", "expected": "accepted once",
            "observed": "accepted once", "verdict": "pass"}], "evidence_refs": ["EV-runtime"],
        "author_id": "fixture-author", "reviewer_id": "fixture-reviewer", "proof_level": "native_verified",
        "native_scope": {"platform": "android", "environment": "synthetic fixture only"}}]
    data["obligations"][0].update(required_proof="native_verified", witness_refs=["ASM-native"])
    context = {"scenarios": [{"id": "SCENARIO-slice"}], "constraints": {"platforms": ["android"]},
        "evidence": [{"id": "EV-runtime", "modality": "runtime", "origin": "fixture-runtime-observation",
            "build_sha256": SHA, "scenario_ids": ["SCENARIO-slice"], "platform": "android", "status": "current"}]}
    return data, context


class ProductionContractTests(unittest.TestCase):
    def errors(self, data):
        return "\n".join(production.validate(data))

    def test_valid_structural_fixture(self):
        self.assertEqual(production.validate(valid_operations()), [])

    def test_step_dependency_cycle_rejected(self):
        data = valid_operations(); data["recipes"][0]["steps"][0]["depends_on"] = ["STEP-export"]
        self.assertIn("contains cycle", self.errors(data))

    def test_dangling_step_and_capability_rejected(self):
        data = valid_operations(); step = data["recipes"][0]["steps"][0]
        step.update(depends_on=["STEP-absent"], capability_id="CAP-absent")
        errors = self.errors(data)
        self.assertIn("unknown capabilities", errors); self.assertIn("unknown step dependency", errors)

    def test_format_valid_but_unmapped_export_rejected(self):
        data = valid_operations(); data["transformations"][0]["target_ref"] = "ART-unbound-export"
        self.assertIn("absent from recipe artifact inventory", self.errors(data))

    def test_step_output_must_have_consumer_inventory(self):
        data = valid_operations(); data["recipes"][0]["steps"][0]["output_ids"] = ["ART-forgotten"]
        self.assertIn("declared output inventory", self.errors(data))

    def test_unsupported_material_argument_rejected(self):
        data = valid_operations(); data["capabilities"][0]["parameter_bindings"] = [{"requirement_id": "REQ-material",
            "schema_field": "prompt", "supported": False, "material": True, "consumption_check": "actual shape"}]
        self.assertIn("unsupported material parameter", self.errors(data))

    def test_command_needs_argv_not_shell(self):
        data = valid_operations(); data["recipes"][0]["steps"][0]["binding"]["argv"] = "tool source; echo claim"
        self.assertIn("argv array", self.errors(data))

    def test_operation_test_claim_needs_witness_and_fresh_subject(self):
        data = valid_operations(); data["capabilities"][0]["proof_level"] = "operation_tested"
        self.assertIn("witness_refs", self.errors(data))
        data["capabilities"][0].update(witness_refs=["fixture-witness"], subject_digest=SHA, current_subject_digest="b" * 64)
        self.assertIn("subject changed", self.errors(data))

    def test_native_claim_requires_native_scope(self):
        data = valid_operations(); data["capabilities"][0].update(proof_level="native_verified", witness_refs=["fixture"], subject_digest=SHA)
        self.assertIn("native_scope", self.errors(data))

    def test_due_obligation_not_green_from_neighbor(self):
        data = valid_operations(); data["obligations"][0]["status"] = "pending"
        self.assertIn("due obligation", self.errors(data))

    def test_past_due_obligation_blocks_later_gate(self):
        data = valid_operations(); data["gate"] = "R"; data["obligations"][0]["status"] = "pending"
        self.assertIn("due obligation", self.errors(data))

    def test_unknown_gate_rejected(self):
        data = valid_operations(); data["obligations"][0]["due_gate"] = "invented"
        self.assertIn("unknown due_gate", self.errors(data))

    def test_malformed_unhashable_values_rejected(self):
        data = valid_operations(); data["capabilities"][0]["proof_level"] = {}
        self.assertTrue(production.validate(data))

    def test_later_obligation_can_be_pending(self):
        data = valid_operations(); data["obligations"][0].update(status="pending", due_gate="B")
        self.assertEqual(production.validate(data), [])

    def test_template_is_not_executable_recipe(self):
        data = valid_operations(); data["recipes"][0]["status"] = "template"; data["attempts"] = [attempt()]
        self.assertIn("attempt requires bound recipe", self.errors(data))

    def test_unknown_job_can_lack_provider_id_but_requires_reconcile(self):
        data = valid_operations(); data["attempts"] = [attempt(status="unknown")]
        self.assertEqual(production.validate(data), [])
        del data["attempts"][0]["reconciliation"]
        self.assertIn("reconciliation", self.errors(data))

    def test_unknown_effect_not_retried(self):
        data = valid_operations(); old = attempt(status="unknown"); new = attempt("ATT-retry")
        new.update(retry_of=old["id"], retry_reason="fixture hypothesis", effect_key="new-effect")
        data["attempts"] = [old, new]
        self.assertIn("retry before", self.errors(data))

    def test_failed_reconciled_effect_allows_new_attempt_identity(self):
        data = valid_operations(); old = attempt(status="failed"); new = attempt("ATT-retry")
        new.update(retry_of=old["id"], retry_reason="correct input", effect_key="new-effect")
        data["attempts"] = [old, new]
        self.assertEqual(production.validate(data), [])

    def test_duplicate_effect_blocks_unrelated_retry_label(self):
        data = valid_operations(); data["attempts"] = [attempt("ATT-one", "unknown"), attempt("ATT-two")]
        self.assertIn("effect key", self.errors(data))

    def test_observations_strict_sequence_and_final_state(self):
        data = valid_operations(); item = attempt(); item["observations"].append(dict(item["observations"][0]))
        data["attempts"] = [item]
        self.assertIn("strictly increase", self.errors(data))
        item["status"] = "failed"
        self.assertIn("differs from latest", self.errors(data))

    def test_real_output_digest_optional_root(self):
        data = valid_operations(); item = attempt(status="succeeded"); data["attempts"] = [item]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "actual.bin"; path.write_bytes(b"actual")
            item["outputs"][0]["path"] = "actual.bin"
            self.assertIn("digest mismatch", "\n".join(production.validate(data, tmp)))
            item["outputs"][0]["path"] = "../outside.bin"
            self.assertIn("escapes declared root", "\n".join(production.validate(data, tmp)))

    def test_independent_assembly_not_same_actor(self):
        data = valid_operations(); data["assemblies"] = [{"id": "ASM-fixture", "scene_ref": "scene",
            "build_digest": SHA, "config_digest": SHA, "components": [{"id": "ART-export", "sha256": SHA}],
            "scenario": "fixture", "invariants": ["fixture"], "evidence_refs": ["fixture"],
            "author_id": "same", "reviewer_id": "same", "proof_level": "integrated"}]
        self.assertIn("reviewer equals author", self.errors(data))

    def test_empty_c0_is_only_structural_pass(self):
        self.assertEqual(production.validate({"gate": "C0"}), [])

    def test_duplicate_global_record_id_rejected(self):
        data = valid_operations(); data["transformations"][0]["id"] = "CAP-synthetic"
        self.assertIn("duplicate record id", self.errors(data))

    def test_paid_budget_needs_real_scope_reference(self):
        data = valid_operations(); data["recipes"][0]["budget"]["maximum_minor_units"] = 100
        self.assertIn("authorized_scope_ref", self.errors(data))

    def test_negative_minor_units_rejected(self):
        data = valid_operations(); data["capabilities"][0]["cost"]["maximum_minor_units"] = -1
        self.assertIn("nonnegative integer", self.errors(data))

    def test_obligation_unknown_required_proof_rejected(self):
        data = valid_operations(); data["obligations"][0]["required_proof"] = "nativ_verify_typo"
        self.assertIn("unknown required_proof", self.errors(data))

    def test_native_obligation_needs_resolved_native_witness(self):
        data = valid_operations(); data["obligations"][0].update(required_proof="native_verified", witness_refs=["NO-SUCH-WITNESS"])
        self.assertIn("unknown proof witness", self.errors(data))
        data["obligations"][0]["witness_refs"] = ["CAP-synthetic"]
        self.assertIn("insufficient", self.errors(data))

    def test_operation_test_witness_closes_actual_attempt_declarations(self):
        data = valid_operations(); data["attempts"] = [attempt(status="succeeded")]
        data["capabilities"][0].update(proof_level="operation_tested", witness_refs=["ATT-synthetic"], subject_digest=SHA)
        data["obligations"][0].update(required_proof="operation_tested", witness_refs=["CAP-synthetic"])
        self.assertEqual(production.validate(data), [])
        data["attempts"][0]["status"] = "failed"
        self.assertIn("has not succeeded", self.errors(data))

    def test_recipe_requirement_ids_must_be_typed_array(self):
        data = valid_operations(); data["recipes"][0]["requirement_ids"] = "NO-SUCH-REQUIREMENT"
        self.assertIn("array of nonempty strings", self.errors(data))

    def test_succeeded_output_must_belong_to_bound_recipe(self):
        data = valid_operations(); data["attempts"] = [attempt(status="succeeded")]
        data["attempts"][0]["outputs"][0]["id"] = "ART-UNDECLARED-OUTPUT"
        self.assertIn("successful output absent", self.errors(data))
        self.assertIn("lacks required", self.errors(data))

    def test_closed_native_declarations_pass_structural_check(self):
        data, context = native_operations()
        self.assertEqual(production.validate(data, context=context), [])

    def test_candidate_assembly_never_closes_slice_gate(self):
        data, context = native_operations(); data["assemblies"][0]["proof_level"] = "candidate"
        self.assertIn("native_verified assembly", "\n".join(production.validate(data, context=context)))

    def test_native_assembly_needs_current_scenario_evidence_and_matching_build(self):
        data, context = native_operations()
        data["assemblies"][0]["scenario"] = "SCENARIO-absent"
        errors = "\n".join(production.validate(data, context=context))
        self.assertIn("unknown assembly scenario", errors)
        self.assertIn("does not exercise", errors)
        data, context = native_operations(); context["evidence"][0]["status"] = "superseded"
        self.assertIn("historical/superseded", "\n".join(production.validate(data, context=context)))
        data, context = native_operations(); context["evidence"][0]["build_sha256"] = "b" * 64
        self.assertIn("build differs", "\n".join(production.validate(data, context=context)))

    def test_native_assembly_rejects_dangling_scene_or_evidence(self):
        data, context = native_operations(); data["assemblies"][0]["scene_ref"] = "SCENE-absent"
        self.assertIn("scene_ref must bind", "\n".join(production.validate(data, context=context)))
        data, context = native_operations(); data["assemblies"][0]["evidence_refs"] = ["EV-absent"]
        self.assertIn("unknown canonical evidence", "\n".join(production.validate(data, context=context)))

    def test_native_assembly_pending_invariant_cannot_be_ready(self):
        data, context = native_operations(); data["assemblies"][0]["invariants"][0]["verdict"] = "pending"
        self.assertIn("unresolved invariant", "\n".join(production.validate(data, context=context)))

    def test_native_assembly_component_digest_from_attempt(self):
        data, context = native_operations(); data["assemblies"][0]["components"][0]["sha256"] = "b" * 64
        self.assertIn("matching successful attempt", "\n".join(production.validate(data, context=context)))

    def test_native_scope_wrong_type_rejected_without_crash(self):
        data, context = native_operations(); data["assemblies"][0]["native_scope"] = "android"
        self.assertIn("native_scope must be object", "\n".join(production.validate(data, context=context)))

    def test_native_assembly_platform_matches_runtime_evidence(self):
        data, context = native_operations(); context["evidence"][0]["platform"] = "ios"
        self.assertIn("platform mismatch", "\n".join(production.validate(data, context=context)))

    def test_malformed_record_shape_has_errors(self):
        self.assertTrue(production.validate({"capabilities": [None], "recipes": "bad"}))


if __name__ == "__main__":
    unittest.main()
