"""Meaningful binding/gate tests; no mocked claim of human authentication."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "briefing.py"
SPEC = importlib.util.spec_from_file_location("atelier_briefing", SCRIPT)
briefing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(briefing)


class BriefingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.record_path = self.root / "briefing.json"
        (self.root / "inputs").mkdir()
        snapshot = self.root / "inputs" / "baseline.txt"
        snapshot.write_text("Original baseline.\n", encoding="utf-8")
        self.record = briefing.template("brief", "app-atelier", "design", "Повний погоджений застосунок")
        self.record["authority_refs"] = [{"source_role": "user", "source_ref": "message:task-7"}]
        self.record["baseline"]["source"] = {
            "facts": [{"text": "Current accepted baseline snapshot", "source_ref": "repo:abc123"}],
            "unknowns": [], "inputs": [{"path": "inputs/baseline.txt", "sha256": briefing.digest_bytes(snapshot.read_bytes())}]}
        self.record["execution_spec"] = {
            "revision": "r1", "outcomes": ["Full design and precise implementation handoff"],
            "steps": [
                {"id": "ANALYZE", "depends_on": [], "outputs": ["analysis.md"], "acceptance": ["Source-linked gaps"]},
                {"id": "BUILD", "depends_on": ["ANALYZE"], "outputs": ["app.py"], "acceptance": ["Accepted behavior verified"]},
                {"id": "RELEASE", "depends_on": ["BUILD"], "outputs": ["release-receipt"], "acceptance": ["Actual release receipt"]},
            ],
            "resources": [{"host": "Codex", "available": "source executor"}],
            "limits": {"cost_usd": 0, "publication": "separate exact effect permission"},
            "milestones": [{"after": "ANALYZE", "review": "show findings"}],
            "stop": {"after": "RELEASE"},
            "delegation": {"technical": "Within accepted architecture and quality"},
            "next_route": {"stage": "operations", "host": "Codex", "selector": "$app-atelier-director"}}
        self.record["topics"] = [{"id": "GOAL", "criticality": "material", "status": "confirmed",
                                  "answer": "Full accepted target", "source_ref": "message:task-7", "dependent_steps": ["BUILD"]}]

    def bind(self):
        script = briefing.render_script(self.record)
        (self.root / "script.md").write_bytes(script)
        self.record["script_binding"] = {"path": "script.md", "scope_hash": briefing.scope_hash(self.record),
                                          "script_sha256": briefing.digest_bytes(script), "render_locale": "en",
                                          "render_version": briefing.RENDER_VERSION}

    def approve(self, decision="approved", approved=None, excluded=None):
        if self.record.get("script_binding") is None:
            self.bind()
        self.record["approval"] = {
            "source_role": "user", "source_ref": "message:actual-reply-8", "quote": "Погоджую цю редакцію та вказаний scope.",
            "decision": decision, "revision": self.record["execution_spec"]["revision"],
            "scope_hash": briefing.scope_hash(self.record), "script_sha256": self.record["script_binding"]["script_sha256"],
            "approved_steps": approved if approved is not None else ["ANALYZE", "BUILD", "RELEASE"],
            "excluded_steps": excluded if excluded is not None else []}
        binding = self.record["script_binding"]
        for key in ("render_locale", "render_version"):
            if key in binding:
                self.record["approval"][key] = binding[key]

    def gate(self, name="execution", step=None):
        return briefing.check(self.record, self.root, name, step)

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)], text=True, capture_output=True, check=False)

    def test_valid_exact_approval_allows_bound_scope_but_claims_no_authentication(self):
        self.approve()
        result = self.gate()
        self.assertTrue(result["ok"], result)
        self.assertFalse(result["human_authority_authenticated"])
        self.assertFalse(result["quality_certified"])
        self.assertFalse(result["executes_actions"])

    def test_init_is_nonoverwriting_and_creates_no_approval(self):
        args = ("init", self.record_path, "--mode", "resume", "--family", "chatbot-atelier", "--stage", "repair", "--goal", "Resume", "--json")
        first = self.cli(*args)
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        initial = self.record_path.read_bytes()
        self.assertIsNone(json.loads(initial)["approval"])
        self.assertEqual(self.cli(*args).returncode, 1)
        self.assertEqual(self.record_path.read_bytes(), initial)

    def test_rendered_script_is_human_markdown_and_deterministic(self):
        first = briefing.render_script(self.record)
        reordered = json.loads(json.dumps(self.record, sort_keys=True))
        self.assertEqual(first, briefing.render_script(reordered))
        text = first.decode("utf-8")
        self.assertNotIn("```json", text)
        self.assertIn("Acceptance criteria", text)
        self.assertIn("Current accepted baseline snapshot", text)
        self.assertIn("Full design and precise implementation handoff", text)
        self.assertIn("BUILD", text)
        self.assertIn("show findings", text)

    def test_missing_approval_and_synthetic_ack_do_not_open_execution(self):
        self.bind()
        self.record["approved"] = True
        self.record["user_acknowledged"] = True
        self.assertFalse(self.gate()["ok"])

    def test_immutable_input_drift_blocks_even_unchanged_record(self):
        self.approve()
        (self.root / "inputs" / "baseline.txt").write_text("Different input", encoding="utf-8")
        result = self.gate()
        self.assertFalse(result["ok"])
        self.assertIn("drift", " ".join(result["errors"]))

    def test_mutable_output_hashes_and_closeout_do_not_change_scope(self):
        self.approve()
        original_scope = briefing.scope_hash(self.record)
        output = self.root / "app.py"
        output.write_text("version one", encoding="utf-8")
        self.record["closeout"] = {"artifacts": [{"path": "app.py", "sha256": briefing.digest_bytes(output.read_bytes())}]}
        output.write_text("version two", encoding="utf-8")
        self.record["closeout"]["artifacts"][0]["sha256"] = briefing.digest_bytes(output.read_bytes())
        self.assertEqual(briefing.scope_hash(self.record), original_scope)
        self.assertTrue(self.gate()["ok"])

    def test_changed_goal_or_revision_stales_bound_script_and_approval(self):
        for field in ("goal", "revision"):
            with self.subTest(field=field):
                saved = copy.deepcopy(self.record)
                self.approve()
                if field == "goal":
                    self.record["goal"] = "Materially different goal"
                else:
                    self.record["execution_spec"]["revision"] = "r2"
                self.assertFalse(self.gate()["ok"])
                self.record = saved

    def test_script_byte_tampering_blocks_execution(self):
        self.approve()
        with (self.root / "script.md").open("a", encoding="utf-8") as stream:
            stream.write("\nAn unapproved extra promise")
        self.assertFalse(self.gate()["ok"])

    def test_pending_material_only_blocks_its_declared_dependency_closure(self):
        self.record["topics"].append({"id": "PRICE", "status": "pending", "criticality": "material", "dependent_steps": ["BUILD"]})
        self.approve()
        self.assertTrue(self.gate(step="ANALYZE")["ok"])
        self.assertFalse(self.gate(step="BUILD")["ok"])
        self.assertFalse(self.gate(step="RELEASE")["ok"])
        self.assertIn("dependency", " ".join(self.gate(step="RELEASE")["errors"]))

    def test_deferred_material_does_not_become_approved_by_deferral(self):
        self.record["topics"].append({"id": "STORE", "status": "deferred", "criticality": "material", "dependent_steps": ["RELEASE"],
                                      "owner": "user", "due_gate": "before release", "rationale": "Select after prepared release"})
        self.approve()
        self.assertTrue(self.gate(step="BUILD")["ok"])
        self.assertFalse(self.gate(step="RELEASE")["ok"])

    def test_partial_approval_preserves_independent_approved_step(self):
        self.approve("partial", ["ANALYZE"], ["BUILD", "RELEASE"])
        self.assertTrue(self.gate()["ok"])
        self.assertTrue(self.gate(step="ANALYZE")["ok"])
        self.assertFalse(self.gate(step="BUILD")["ok"])

    def test_approved_step_cannot_use_excluded_dependency(self):
        self.approve("partial", ["ANALYZE", "RELEASE"], ["BUILD"])
        self.assertTrue(self.gate(step="ANALYZE")["ok"])
        result = self.gate(step="RELEASE")
        self.assertFalse(result["ok"])
        self.assertIn("BUILD is outside", " ".join(result["errors"]))

    def test_incomplete_partial_partition_and_overlapping_sets_rejected(self):
        self.approve("partial", ["ANALYZE"], ["BUILD"])
        self.assertFalse(self.gate()["ok"])
        self.record["approval"]["excluded_steps"] = ["ANALYZE", "BUILD", "RELEASE"]
        self.assertFalse(self.gate()["ok"])

    def test_material_delegation_needs_actual_user_source_and_bounded_acceptance(self):
        topic = {"id": "DESIGN", "criticality": "material", "status": "delegated", "dependent_steps": ["BUILD"],
                 "owner": "design lead", "bounds": "Preserve accepted persistent world and full target",
                 "acceptance": "All accepted journeys preserved", "source_role": "user", "source_ref": "message:actual-delegation-3"}
        self.record["topics"].append(topic)
        self.approve()
        self.assertTrue(self.gate()["ok"])
        topic.pop("source_ref")
        self.assertFalse(self.gate("interview")["ok"])

    def test_technical_delegation_requires_owner_bounds_and_acceptance(self):
        topic = {"id": "LIB", "criticality": "technical", "status": "delegated", "dependent_steps": ["BUILD"],
                 "owner": "implementation lead", "bounds": "No new spend", "acceptance": "Current supported dependency"}
        self.record["topics"].append(topic)
        self.approve()
        self.assertTrue(self.gate()["ok"])
        topic["bounds"] = ""
        self.assertFalse(self.gate("interview")["ok"])

    def test_resume_runtime_unknown_does_not_block_independent_source_analysis(self):
        self.record["mode"] = "resume"
        for name, section in self.record["baseline"].items():
            if not section["facts"]:
                section["unknowns"] = [{"text": f"Unverified {name}", "blocking_steps": []}]
        self.record["baseline"]["runtime"]["unknowns"][0]["blocking_steps"] = ["RELEASE"]
        self.approve()
        self.assertTrue(self.gate(step="ANALYZE")["ok"])
        self.assertTrue(self.gate(step="BUILD")["ok"])
        self.assertFalse(self.gate(step="RELEASE")["ok"])
        self.record["baseline"]["evidence"] = {"facts": [], "unknowns": [], "inputs": []}
        self.assertFalse(self.gate("interview")["ok"])

    def test_active_pause_blocks_execution_without_blocking_reconstruction_or_clearing_pause(self):
        self.approve()
        self.record["pause"] = {"active": True, "reason": "User stop now"}
        before = copy.deepcopy(self.record)
        self.assertTrue(self.gate("interview")["ok"])
        self.assertTrue(self.gate("approval", "ANALYZE")["ok"])
        self.assertFalse(self.gate(step="ANALYZE")["ok"])
        self.assertEqual(self.record, before)

    def test_nonhuman_unavailable_and_self_generated_approval_rejected(self):
        self.approve()
        valid = copy.deepcopy(self.record["approval"])
        for changes in ({"source_role": "assistant"}, {"source_ref": "generated:approval"}, {"source_ref": "EXAMPLE"},
                        {"source_status": "unavailable"}, {"quote": ""}):
            with self.subTest(changes=changes):
                self.record["approval"] = {**valid, **changes}
                self.assertFalse(self.gate()["ok"])

    def test_rejected_and_revoked_responses_are_recordable_but_not_authorization(self):
        self.bind()
        for decision in ("rejected", "revoked"):
            self.approve(decision, [], ["ANALYZE", "BUILD", "RELEASE"])
            self.assertEqual(briefing.approval_errors(self.record, self.record["approval"]), [])
            self.assertFalse(self.gate()["ok"])

    def test_bad_dependency_graphs_and_duplicate_ids_fail(self):
        variants = [
            lambda: self.record["execution_spec"]["steps"][0]["depends_on"].append("MISSING"),
            lambda: self.record["execution_spec"]["steps"][0]["depends_on"].append("RELEASE"),
            lambda: self.record["execution_spec"]["steps"].append(copy.deepcopy(self.record["execution_spec"]["steps"][0])),
            lambda: self.record["topics"].append(copy.deepcopy(self.record["topics"][0])),
        ]
        for mutate in variants:
            saved = copy.deepcopy(self.record)
            mutate()
            self.assertFalse(self.gate("interview")["ok"])
            self.record = saved

    def closeout(self):
        for name, text in (("output.md", "Actual output"), ("next.txt", "Read checkpoint; preserve stop; return evidence.")):
            (self.root / name).write_text(text, encoding="utf-8")
        self.record["closeout"] = {"result": "Prepared bounded handoff", "readiness": "prepared",
            "checks": [{"name": "scope review", "result": "prepared only"}], "gaps": ["Runtime unverified"],
            "recommendation": "Clarify next stage before production", "next_stage": {"stage": "build", "host": "Codex", "selector": "$app-atelier-director"},
            "artifacts": [{"path": "output.md", "sha256": briefing.digest_bytes((self.root / "output.md").read_bytes())}],
            "next_launch_prompt": {"path": "next.txt", "sha256": briefing.digest_bytes((self.root / "next.txt").read_bytes())},
            "return_validation": "Compare actual output and dependency hashes against this snapshot",
            "questionnaire_offer": "Пропоную перед наступним етапом провести БРИФ."}

    def test_prepared_or_blocked_closeout_does_not_grant_execution(self):
        self.bind()
        self.closeout()
        self.record["closeout"]["readiness"] = "blocked"
        self.assertTrue(self.gate("closeout")["ok"])
        self.assertFalse(self.gate()["ok"])

    def test_continuation_requires_real_artifact_prompt_route_and_due_brief(self):
        self.bind()
        self.closeout()
        self.record["closeout"]["needs_brief"] = True
        self.assertTrue(self.gate("closeout")["ok"])
        saved = copy.deepcopy(self.record["closeout"])
        for mutate in (lambda: self.record["closeout"].pop("questionnaire_offer"),
                       lambda: self.record["closeout"]["next_stage"].pop("selector"),
                       lambda: self.record["closeout"].update(artifacts=[]),
                       lambda: (self.root / "next.txt").write_text("changed prompt", encoding="utf-8")):
            mutate()
            self.assertFalse(self.gate("closeout")["ok"])
            self.record["closeout"] = copy.deepcopy(saved)

    def test_terminal_acceptance_needs_current_actual_result_acceptance_but_no_next_stage(self):
        self.bind()
        self.closeout()
        c = self.record["closeout"]
        c.update(outcome="accepted_done", next_stage=None, next_launch_prompt=None, needs_brief=False)
        c.pop("questionnaire_offer")
        self.assertFalse(self.gate("closeout")["ok"])
        c["owner_acceptance"] = {"source_role": "user", "source_ref": "message:result-acceptance-12",
            "quote": "Приймаю наданий результат", "decision": "accepted",
            "scope_hash": briefing.scope_hash(self.record), "artifacts_sha256": briefing.digest_bytes(briefing.canonical(c["artifacts"]))}
        self.assertTrue(self.gate("closeout")["ok"], self.gate("closeout"))
        self.assertFalse(self.gate()["ok"])
        c["owner_acceptance"]["source_ref"] = "self:asserted"
        self.assertFalse(self.gate("closeout")["ok"])
        c["owner_acceptance"]["source_ref"] = "message:result-acceptance-12"
        c["owner_acceptance"]["artifacts_sha256"] = "0" * 64
        self.assertFalse(self.gate("closeout")["ok"])

    def test_ready_waiting_paused_blocked_cancelled_need_no_fabricated_next_prompt(self):
        self.bind()
        self.closeout()
        c = self.record["closeout"]
        c.update(next_stage=None, next_launch_prompt=None, needs_brief=False)
        c.pop("questionnaire_offer")
        for outcome in ("ready_for_acceptance", "waiting_decision", "paused", "blocked", "cancelled"):
            with self.subTest(outcome=outcome):
                c["outcome"] = outcome
                self.assertTrue(self.gate("closeout")["ok"], self.gate("closeout"))
                self.assertFalse(self.gate()["ok"])
        c["next_stage"] = {"stage": "invented"}
        self.assertFalse(self.gate("closeout")["ok"])

    def test_small_continuation_does_not_require_another_questionnaire(self):
        self.bind()
        self.closeout()
        self.record["closeout"].pop("questionnaire_offer")
        self.assertTrue(self.gate("closeout")["ok"])
        self.record["closeout"]["outcome"] = "unsupported"
        self.assertFalse(self.gate("closeout")["ok"])

    def test_path_escape_and_symlink_escape_rejected(self):
        self.record["baseline"]["source"]["inputs"][0]["path"] = "../outside.txt"
        self.assertFalse(self.gate("interview")["ok"])
        outside = self.root.parent / (self.root.name + "-outside.txt")
        outside.write_text("private", encoding="utf-8")
        self.addCleanup(outside.unlink)
        (self.root / "link.txt").symlink_to(outside)
        self.record["baseline"]["source"]["inputs"][0] = {"path": "link.txt", "sha256": briefing.digest_bytes(outside.read_bytes())}
        self.assertFalse(self.gate("interview")["ok"])

    def test_cli_records_exact_actual_reply_and_never_changes_pause(self):
        briefing.write_json(self.record_path, self.record)
        rendered = self.cli("render-script", self.record_path, "--output", "script.md", "--root", self.root, "--json")
        self.assertEqual(rendered.returncode, 0, rendered.stdout + rendered.stderr)
        self.record = briefing.load_json(self.record_path)
        self.approve()
        reply = self.root / "actual-reply.json"
        briefing.write_json(reply, self.record["approval"])
        recorded = self.cli("record-approval", self.record_path, "--approval", reply, "--root", self.root, "--json")
        self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
        self.assertFalse(briefing.load_json(self.record_path)["pause"]["active"])
        checked = self.cli("check", self.record_path, "--gate", "execution", "--step", "ANALYZE", "--root", self.root, "--json")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertTrue(json.loads(checked.stdout)["ok"])

    def test_rerender_material_delta_archives_prior_approval_and_closes_gate(self):
        self.approve()
        self.record["goal"] = "Materially amended goal"
        briefing.write_json(self.record_path, self.record)
        response = self.cli("render-script", self.record_path, "--output", "script.md", "--root", self.root, "--json")
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        updated = briefing.load_json(self.record_path)
        self.assertIsNone(updated["approval"])
        self.assertEqual(len(updated["approval_history"]), 1)
        self.assertFalse(briefing.check(updated, self.root, "execution")["ok"])

    def test_v18_approval_survives_an_alternate_language_view_byte_for_byte(self):
        old = briefing.render_script(self.record, "uk", 1)
        self.assertEqual("e31d4efaeb2759477eb09928c0b4e37f3413b793c00cdc851ae21b7173e01ee2",
                         briefing.digest_bytes(old))
        bound = self.root / "script.md"
        bound.write_bytes(old)
        self.record["script_binding"] = {"path": "script.md", "scope_hash": briefing.scope_hash(self.record),
                                         "script_sha256": briefing.digest_bytes(old)}
        self.approve()
        briefing.write_json(self.record_path, self.record)
        saved = self.record_path.read_bytes()
        result = self.cli("render-script", self.record_path, "--locale", "en", "--output", "view.md", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("preview", json.loads(result.stdout))
        self.assertIn(self.record["goal"], (self.root / "view.md").read_text(encoding="utf-8"))
        self.assertEqual(saved, self.record_path.read_bytes())
        self.assertEqual(old, bound.read_bytes())
        self.assertTrue(self.gate()["ok"])
        self.assertNotEqual(self.cli("render-script", self.record_path, "--locale", "en",
                                    "--output", "script.md", "--json").returncode, 0)
        self.assertEqual(old, bound.read_bytes())

    def test_new_explicit_locale_is_bound_and_mismatched_reply_fails(self):
        self.record["preferred_language"] = "uk"
        briefing.write_json(self.record_path, self.record)
        response = self.cli("render-script", self.record_path, "--locale", "en", "--output", "script.md", "--json")
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        self.record = briefing.load_json(self.record_path)
        self.approve()
        self.assertEqual(self.record["script_binding"]["render_locale"], "en")
        self.assertEqual(self.record["preferred_language"], "uk")
        self.assertTrue(self.gate()["ok"])
        self.record["approval"]["render_locale"] = "uk"
        self.assertFalse(self.gate()["ok"])
        self.record["script_binding"].pop("render_version")
        self.assertFalse(self.gate()["ok"])

    def test_duplicate_json_keys_rejected_instead_of_silently_rebinding(self):
        self.record_path.write_text('{"schema_version":"briefing/1","schema_version":"other"}', encoding="utf-8")
        response = self.cli("check", self.record_path, "--gate", "interview", "--json")
        self.assertEqual(response.returncode, 1)
        self.assertIn("Duplicate JSON key", response.stdout)


if __name__ == "__main__":
    unittest.main()
