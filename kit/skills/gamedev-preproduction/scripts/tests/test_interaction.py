"""Read-only projections: real native shapes, honest evidence and hostile inputs."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "interaction.py"
spec = importlib.util.spec_from_file_location("interaction_under_test", SCRIPT)
interaction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(interaction)


def signed(data):
    """Native journal/snapshot specification, independent of helper functions."""
    data = copy.deepcopy(data)
    canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    event = {"seq": 1, "previous": None, "command": "init", "revision": 1}
    event["hash"] = hashlib.sha256(canonical(event)).hexdigest()
    data["journal"] = [event]
    data["snapshot_hash"] = hashlib.sha256(canonical(data)).hexdigest()
    return data


def foundry():
    return signed({"schema_version": "1.0.0", "project_id": "synthetic", "purpose": "project", "revision": 1,
                   "suite": {}, "blueprint": {"data": {"goal": "Useful complete outcome", "tests": []}},
                   "pause": {"active": False}, "integrity_errors": [], "tasks": {}, "decisions": {},
                   "requirements": {}, "evidence": {}, "artifacts": {}, "actions": {}})


def game():
    return signed({"schema_version": "2.0.0", "toolkit_version": "4.3.0", "project_id": "synthetic-game", "revision": 1,
                   "knowledge_revision": 1, "suite_lock": {}, "seed_history": {"goal": "Complete systemic game"},
                   "pause": {"active": False}, "tasks": {}, "decisions": {}, "requirements": {}, "evidence": {},
                   "artifacts": {}, "actions": {}, "integrity_errors": [], "suite_mismatch": False})


def app():
    return {"schema_version": "app-atelier-state/1", "project_id": "synthetic-app", "revision": 1,
            "profile": {"schema_version": "app-atelier-profile/1", "goal": "Useful native journey"},
            "pause": {"active": False}, "job": {}, "decision": {}, "requirement": {}, "evidence": {}, "artifact": {}, "effect": {}}


def chatbot(blueprint=False):
    d = {"schema_version": "chatbot.blueprint/3" if blueprint else "chatbot.round/1",
         "brief": {"id": "synthetic-chat", "version": "1", "user_intent": "Save a private note"},
         "requirements": [], "evidence": [], "completion": {"status": "pending", "maturity": "draft"}}
    if blueprint:d.update(attempts=[], journeys=[], platform_adapters=[], applicability=[], systems=[], interactions=[], operations=[], recipes=[])
    else:d.update(runs=[], decisions=[], reviews=[], changes=[{"component": "no-id-needed"}], findings=[{"severity": "minor"}], checkpoint={"next_action": "Inspect the actual conversation"})
    return d


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, data, name="round.json"):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False))
        return p

    def test_all_native_shapes_are_projected_without_authorizing(self):
        for name, data in (("foundry", foundry()), ("game", game()), ("app", app()),
                           ("chatbot_round", chatbot()), ("chatbot_blueprint", chatbot(True))):
            with self.subTest(domain=name):
                path = self.write(data)
                before = path.read_bytes()
                result = interaction.build_view(path)
                self.assertEqual(name, result["domain"])
                self.assertEqual(hashlib.sha256(before).hexdigest(), result["source"]["sha256"])
                self.assertFalse(result["native_gate_checked"])
                self.assertEqual("unresolved", result["workflow_status"])
                self.assertTrue(all(x["status"] == "unknown" for x in result["evidence_axes"].values()))
                self.assertEqual(before, path.read_bytes())

    def test_project_discovery_does_not_create_a_lock_or_ledger(self):
        path = self.write(foundry(), ".agent-foundry/state.json")
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        result = interaction.build_view(self.root)
        self.assertEqual(str(path), result["source"]["path"])
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))

    def test_ambiguous_project_requires_explicit_source(self):
        self.write(foundry(), ".agent-foundry/state.json")
        p = self.write(app(), ".appatelier/state.json")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            interaction.build_view(self.root)
        self.assertEqual("app", interaction.build_view(p)["domain"])

    def test_native_snapshot_and_journal_tampering_are_rejected(self):
        for change in ("goal", "journal"):
            data = foundry()
            if change == "goal":data["purpose"] = "changed after signature"
            else:data["journal"][0]["command"] = "changed"
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "integrity"):
                interaction.build_view(self.write(data))

    def test_false_pause_and_string_false_are_distinct(self):
        data = app()
        data["job"] = {"J1": {"id": "J1", "status": "running", "goal": "Work", "scope": "feature"}}
        self.assertEqual("active", interaction.build_view(self.write(data))["workflow_status"])
        data["pause"]["active"] = "false"
        with self.assertRaisesRegex(ValueError, "boolean"):
            interaction.build_view(self.write(data))

    def test_pause_overrides_a_recorded_next_action(self):
        data = chatbot()
        data["pause"] = {"active": True, "reason": "actual explicit pause"}
        result = interaction.build_view(self.write(data))
        self.assertEqual("paused", result["workflow_status"])
        self.assertIn("actual applicable", result["next_action"])

    def test_failed_linked_chat_attempt_overrides_passed_journey(self):
        data = chatbot(True)
        data["completion"]["maturity"] = "integrated"
        data["attempts"] = [{"id": "A1", "result": "failed"}]
        data["evidence"] = [{"id": "E1", "result": "pass", "kind": "execution"}]
        data["journeys"] = [{"id": "J1", "verification": "passed", "attempt_ids": ["A1"], "evidence_ids": ["E1"]}]
        result = interaction.build_view(self.write(data))
        self.assertEqual("recorded_failed", result["evidence_axes"]["integration"]["status"])
        self.assertEqual("unknown", result["evidence_axes"]["human"]["status"])
        self.assertNotEqual("recorded_completed", result["workflow_status"])

    def test_missing_proof_is_unknown_despite_maturity_label(self):
        data = chatbot(True)
        data["completion"]["maturity"] = "integrated"
        data["journeys"] = [{"id": "J1", "verification": "passed", "attempt_ids": [], "evidence_ids": []}]
        self.assertEqual("recorded_unresolved", interaction.build_view(self.write(data))["evidence_axes"]["integration"]["status"])

    def test_axes_remain_independent_and_pass_is_recorded_only(self):
        data = app()
        data["evidence"] = {"E1": {"id": "E1", "status": "pass", "modality": "build"},
                            "E2": {"id": "E2", "status": "fail", "modality": "device"}}
        result = interaction.build_view(self.write(data))
        self.assertEqual("recorded_pass", result["evidence_axes"]["code"]["status"])
        self.assertEqual("recorded_failed", result["evidence_axes"]["device"]["status"])
        self.assertEqual("unknown", result["evidence_axes"]["human"]["status"])
        self.assertFalse(result["evidence_axes"]["code"]["live_or_human_truth_certified"])

    def test_boolean_evidence_is_not_pass(self):
        data = app()
        data["evidence"] = {"E1": {"id": "E1", "result": True, "modality": "human"}}
        self.assertEqual("recorded_unresolved", interaction.build_view(self.write(data))["evidence_axes"]["human"]["status"])

    def test_native_status_not_an_extra_result_field_controls_ledger_evidence(self):
        for state, expected in (("fail", "recorded_failed"), ("stale", "recorded_unresolved"), ("pending", "recorded_pending")):
            data = app()
            data["evidence"] = {"E1": {"id": "E1", "status": state, "result": "pass", "modality": "code"}}
            self.assertEqual(expected, interaction.build_view(self.write(data))["evidence_axes"]["code"]["status"])
        data["evidence"]["E1"].update(status="pass", stale_reasons=["dependency changed"])
        self.assertEqual("recorded_unresolved", interaction.build_view(self.write(data))["evidence_axes"]["code"]["status"])

    def test_native_chat_accepted_is_positive_but_observed_is_not_acceptance(self):
        data = chatbot()
        for result, expected in (("accepted", "recorded_pass"), ("accept", "recorded_pass"), ("observed", "recorded_unresolved")):
            data["evidence"] = [{"id": "E1", "kind": "human", "result": result}]
            self.assertEqual(expected, interaction.build_view(self.write(data))["evidence_axes"]["human"]["status"])

    def test_extra_axis_does_not_override_native_evidence_modality(self):
        data = app()
        data["evidence"] = {"E1": {"id": "E1", "status": "pass", "modality": "code", "axis": "human"}}
        view = interaction.build_view(self.write(data))
        self.assertEqual("recorded_pass", view["evidence_axes"]["code"]["status"])
        self.assertEqual("unknown", view["evidence_axes"]["human"]["status"])

    def test_exact_scope_does_not_include_neighbor_decision_or_evidence(self):
        data = app()
        data["decision"] = {"D1": {"id": "D1", "status": "pending", "scope": "feature", "question": "Choose", "options": ["A", "B"]},
                            "D2": {"id": "D2", "status": "confirmed", "scope": "feature-more", "options": ["A", "B"]}}
        data["evidence"] = {"E1": {"id": "E1", "scope": "feature-more", "status": "pass", "modality": "device"}}
        result = interaction.build_view(self.write(data), scope="feature")
        self.assertEqual(["D1"], [r["id"] for r in result["recorded_decisions"]])
        self.assertEqual("unknown", result["evidence_axes"]["device"]["status"])
        self.assertIn("exact-scope", result["gaps"][0])

    def test_decision_card_preserves_negative_answer_and_is_not_consent(self):
        data = app()
        data["decision"] = {"D1": {"id": "D1", "status": "revoked", "scope": "release", "question": "Publish?",
                                       "options": ["yes", "no"], "answer": "no", "recommendation": "no", "consequences": {"no": "Wait"}}}
        view = interaction.build_view(self.write(data))
        text = interaction.markdown(view, "D1")
        self.assertIn("revoked", text)
        self.assertIn("Записана відповідь: no", text)
        self.assertFalse(view["recorded_decisions"][0]["authority_verified_by_view"])
        self.assertEqual([], view["pending_decisions"])

    def test_terminal_outcome_does_not_invent_another_stage(self):
        for status in ("accepted_done", "cancelled"):
            data = chatbot()
            data["completion"]["status"] = status
            result = interaction.build_view(self.write(data))
            self.assertIn(status if status == "cancelled" else "completed", result["workflow_status"])
            self.assertNotIn("Continue", result["next_action"])

    def test_native_round_stage_and_scoped_completion_use_reviews_not_applicability(self):
        for status in ("stage_complete", "scoped_complete"):
            data = chatbot()
            data["requirements"] = [{"id": "R1", "state": "active", "reason": "accepted scope"},
                                    {"id": "R2", "state": "unchanged", "reason": "carried scope"}]
            data["reviews"] = [{"requirement_id": "R1", "verdict": "accept", "evidence_ids": ["E1"]}]
            data["team_policy"] = {"assignments": {"R2": {"status": "carried"}}}
            data["completion"].update(status=status, stage="independently_reviewed", unresolved_requirement_ids=[])
            data["checkpoint"]["next_action"] = "perform actual checks"
            view = interaction.build_view(self.write(data))
            self.assertEqual("recorded_completed", view["workflow_status"])
            self.assertEqual([], view["open_requirements"])
            self.assertIn("no next stage", view["next_action"])
            self.assertFalse(view["native_gate_checked"])
            self.assertEqual("unknown", view["evidence_axes"]["human"]["status"])
            data["reviews"][0]["verdict"] = "revise"
            view = interaction.build_view(self.write(data))
            self.assertEqual(["R1"], [r["id"] for r in view["open_requirements"]])
            self.assertEqual("blocked", view["workflow_status"])

    def test_native_round_unresolved_ids_and_missing_reviews_remain_open(self):
        data = chatbot()
        data["requirements"] = [{"id": "R1", "state": "active"}, {"id": "R2", "state": "active"}]
        data["reviews"] = [{"requirement_id": "R1", "verdict": "accept"}]
        data["completion"]["unresolved_requirement_ids"] = ["R1"]
        self.assertEqual(["R1", "R2"], [r["id"] for r in interaction.build_view(self.write(data))["open_requirements"]])

    def test_native_assessment_failure_and_pending_override_raw_success(self):
        data = chatbot()
        data["evidence"] = [{"id": "E1", "kind": "code", "result": "passed"}]
        data["completion"]["assessments"] = {
            "code": {"status": "failed", "scope": "code scope", "evidence_ids": ["E1"]},
            "human": {"status": "pending", "scope": "user scope", "evidence_ids": []}}
        view = interaction.build_view(self.write(data))
        self.assertEqual("recorded_failed", view["evidence_axes"]["code"]["status"])
        self.assertEqual("recorded_pending", view["evidence_axes"]["human"]["status"])
        self.assertEqual("completion.assessments.code", view["evidence_axes"]["code"]["records"][-1]["id"])
        scoped = interaction.build_view(self.write(data), scope="neighbor")
        self.assertEqual("unknown", scoped["evidence_axes"]["code"]["status"])

    def test_passed_assessment_cannot_hide_bad_or_missing_linked_proof(self):
        for result, expected in (("failed", "recorded_failed"), ("pending", "recorded_pending"), ("passed", "recorded_pass")):
            data = chatbot()
            data["evidence"] = [{"id": "E1", "kind": "execution", "result": result}]
            data["completion"]["assessments"] = {"code": {"status": "passed", "scope": "source", "evidence_ids": ["E1"]}}
            self.assertEqual(expected, interaction.build_view(self.write(data))["evidence_axes"]["code"]["status"])
            data["completion"]["assessments"]["code"]["evidence_ids"] = ["MISSING"]
            self.assertEqual("recorded_unresolved", interaction.build_view(self.write(data))["evidence_axes"]["code"]["status"])
        data["completion"]["assessments"]["code"]["status"] = "not_assessed"
        self.assertEqual("unknown", interaction.build_view(self.write(data))["evidence_axes"]["code"]["status"])

    def test_blueprint_attempt_result_drives_work_and_preserves_maturity(self):
        data = chatbot(True)
        data["attempts"] = [{"id": "AP", "result": "passed"}, {"id": "AR", "result": "running"}, {"id": "AF", "result": "failed"}]
        data["completion"]["maturity"] = "specified"
        view = interaction.build_view(self.write(data))
        self.assertEqual(["AR"], [r["id"] for r in view["current_work"]])
        self.assertEqual(["AP"], [r["id"] for r in view["recorded_completed_work"]])
        self.assertEqual(["AF"], [r["id"] for r in view["pending_work"]])
        self.assertEqual("specified", view["recorded_completion"]["stage"])
        self.assertIn("Записаний етап: specified", interaction.markdown(view))

    def test_unknown_effect_prevents_a_repeat_suggestion(self):
        data = app()
        data["effect"] = {"FX1": {"id": "FX1", "status": "unknown", "scope": "payment"}}
        result = interaction.build_view(self.write(data))
        self.assertEqual(["FX1"], [r["id"] for r in result["unknown_effects"]])
        self.assertIn("Reconcile", result["next_action"])

    def test_native_integrity_block_and_recorded_staleness_are_visible(self):
        data = app()
        data["integrity_errors"] = ["Changed accepted source"]
        data["job"] = {"J1": {"id": "J1", "status": "completed", "stale_reasons": ["dependency changed"]}}
        view = interaction.build_view(self.write(data))
        self.assertEqual("blocked", view["workflow_status"])
        self.assertTrue(view["recorded_completed_work"][0]["recorded_stale"])
        self.assertIn("recorded stale", interaction.markdown(view))

    def test_projection_redacts_secret_shapes_without_dumping_extra_fields(self):
        data = app()
        secret = "rnd_" + "a" * 30
        data["profile"]["goal"] = "Do useful work. " + secret + " api_key=another-secret"
        data["private_config"] = {"raw": "must not be output"}
        text = json.dumps(interaction.build_view(self.write(data)))
        self.assertNotIn(secret, text)
        self.assertNotIn("another-secret", text)
        self.assertNotIn("private_config", text)
        self.assertIn("REDACTED", text)

    def test_quoted_json_and_single_quoted_secret_values_are_redacted(self):
        data = chatbot()
        secret = "synthetic-private-value-123"
        for assignment in ('{"api_key":"' + secret + '"}', "{'password': '" + secret + " with spaces'}", 'client_secret="' + secret + '\\"tail"'):
            data["brief"]["user_intent"] = "Example: " + assignment
            view = interaction.build_view(self.write(data))
            self.assertNotIn(secret, json.dumps(view))
            self.assertIn("REDACTED", view["goal"])

    def test_unsupported_or_template_schemas_fail_clearly(self):
        for data in ({"schema_version": "future/1"}, {"schema_version": "1.0.0", "is_template": True}):
            with self.assertRaisesRegex(ValueError, "unsupported"):
                interaction.build_view(self.write(data))
        data = chatbot(True)
        del data["operations"]
        with self.assertRaisesRegex(ValueError, "unsupported ChatBot native layout"):
            interaction.build_view(self.write(data))

    def test_input_safety_duplicate_nonfinite_and_symlink(self):
        p = self.root / "unsafe.json"
        for raw in ('{"schema_version":"x","schema_version":"y"}', '{"value":NaN}', '{"value":1e9999}', '{"value":' + '9' * 200 + '}'):
            p.write_text(raw)
            with self.assertRaises(ValueError):interaction.build_view(p)
        target = self.write(app())
        link = self.root / "link.json"
        link.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):interaction.build_view(link)
        with self.assertRaisesRegex(ValueError, "configuration/credential"):
            interaction.build_view(self.root / "config.json")

    def test_explicit_root_rejects_outside_source(self):
        path = self.write(app())
        unrelated = self.root / "other"
        unrelated.mkdir()
        with self.assertRaisesRegex(ValueError, "inside"):
            interaction.build_view(path, unrelated)

    def test_dotdot_is_normalized_before_containment_without_erasing_symlinks(self):
        inside = self.root / "inside"
        inside.mkdir()
        self.write(app(), "outside.json")
        with self.assertRaisesRegex(ValueError, "inside"):
            interaction.build_view(inside / ".." / "outside.json", inside)
        self.write(app(), "inside/state.json")
        link = inside / "link"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            interaction.build_view(link / ".." / "state.json", inside)
        view = interaction.build_view(inside / ".." / "inside" / "state.json", inside)
        self.assertEqual(str(inside / "state.json"), view["source"]["path"])

    def test_path_errors_do_not_echo_arbitrary_source_values(self):
        marker = "synthetic-private-value-123"
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "status", "--source", str(self.root / marker / "missing.json")], capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertNotIn(marker, result.stderr)
        self.assertFalse(json.loads(result.stderr)["writes_performed"])

    def test_cli_and_schema_contract(self):
        p = self.write(app())
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "status", "--source", str(p), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        view = json.loads(result.stdout)
        self.assertEqual("atelier-status-view/1", view["schema_version"])
        schema = json.loads((SCRIPT.parents[1] / "assets/status-view.schema.json").read_text())
        self.assertEqual(set(schema["required"]), set(view))
        self.assertEqual(set(schema["properties"]["evidence_axes"]["required"]), set(view["evidence_axes"]))
        missing = subprocess.run([sys.executable, "-B", str(SCRIPT), "decision", "--source", str(p), "--id", "missing"], capture_output=True, text=True)
        self.assertEqual(2, missing.returncode)
        self.assertFalse(json.loads(missing.stderr)["writes_performed"])


if __name__ == "__main__":
    unittest.main()
