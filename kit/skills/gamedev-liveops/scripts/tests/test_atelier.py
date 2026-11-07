"""Actual CLI integration tests: isolated projects; no network/store/device claims."""
import concurrent.futures
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.bundle = self.base / "bundle"
        (self.bundle / "scripts").mkdir(parents=True)
        (self.bundle / "assets").mkdir()
        (self.bundle / "references").mkdir()
        for name in ("atelier.py", "pipeline.py"):
            shutil.copyfile(SOURCE / name, self.bundle / "scripts" / name)
        (self.bundle / "assets/stage-catalog.json").write_text('{"schema_version":"2.0.0"}')
        (self.bundle / "references/experience-contract.md").write_text("Test contract v1")
        self.script = self.bundle / "scripts/atelier.py"
        self.project = self.base / "project"
        self.call("project-init", "--project-id", "test-project")
        self.counter = 0

    def tearDown(self):
        self.temp.cleanup()

    def call(self, command, *args, record=None, expected=0, parse=True):
        argv = [sys.executable, str(self.script), command, str(self.project), *map(str, args)]
        if record is not None:
            argv += ["--record", "-"]
        proc = subprocess.run(argv, input=json.dumps(record) if record is not None else None, capture_output=True, text=True)
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr + "\n" + " ".join(argv))
        value = proc.stdout if proc.stdout else proc.stderr
        return json.loads(value) if parse else value

    def state(self):
        return json.loads((self.project / ".gameatelier/orchestrator/state.json").read_text())

    def write(self, name, content="bytes"):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def artifact(self, ident="ART", stage="concepts", scope="project", **extra):
        name = ident.lower() + ".txt"
        self.write(name)
        return self.call("artifact", record={"id": ident, "path": name, "stage": stage, "scope": scope, "kind": "test_output", "author_ids": ["maker"], "status": "final", **extra})

    def task(self, ident="TASK", stage="concepts", scope="project", **extra):
        expected = extra.pop("expected", 0)
        return self.call("task", expected=expected, record={"id": ident, "stage": stage, "scope": scope, "source": "test user task", "goal": "Bounded test output", "owner": "maker", "skill": "gamedev-" + stage, **extra})

    def evidence(self, ident="PROOF", artifact="ART", stage="concepts", **extra):
        self.write(ident.lower() + ".json", '{"actual_observation":"fixture bytes, not playtest"}')
        expected = extra.pop("expected", 0)
        return self.call("evidence", expected=expected, record={"id": ident, "stage": stage, "scope": "project", "source": "test observer fixture", "modality": "document", "artifact_ids": [artifact], "observer": "reviewer", "status": "pass", "proof_path": ident.lower() + ".json", **extra})

    def decision(self, ident="DEC", stage="concepts", scope="project", **extra):
        expected = extra.pop("expected", 0)
        return self.call("decision", expected=expected, record={"id": ident, "stage": stage, "scope": scope, "source": "actual user reference", "question": "Choose concrete option", "options": ["yes", "no"], "consequences": {"yes": "Scoped work", "no": "Leave pending"}, "recommendation": "yes", "explanation": "Concrete bounded consequence", **extra})

    def confirm(self, ident="DEC", choice="yes", scope="project", **extra):
        row = self.state()["decisions"][ident]
        return self.call("confirm", "--id", ident, "--choice", choice, "--scope", scope, "--decision-revision", row["decision_revision"], "--project-revision", self.state()["revision"], "--authority", "user-message:actual-fixture", **extra)

    def test_current_runtime_protocol_rejects_previous_toolkit_results(self):
        current = self.state()
        self.assertEqual(current["schema_version"], "2.0.0")
        self.assertEqual(current["toolkit_version"], "5.0.0")
        self.assertEqual(current["handoff_protocol"], "1.0.0")
        # Previous toolkit results are rejected without modifying their files.
        current["toolkit_version"] = "2.0.0"
        current.pop("snapshot_hash")
        current["snapshot_hash"] = hashlib.sha256(json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        state_path = self.project / ".gameatelier/orchestrator/state.json"
        state_path.write_text(json.dumps(current, ensure_ascii=False))
        original = state_path.read_bytes()
        spec = importlib.util.spec_from_file_location("atelier_current_state_check", self.script)
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        with self.assertRaises(ValueError):
            runtime.read_state(state_path.parent)
        self.assertEqual(state_path.read_bytes(), original)

    def test_structured_partial_route_and_favorites_do_not_choose_production(self):
        other = self.base / "tatter"
        seed = self.base / "seed.json"
        master = "43b916d58c85db01360703aeef54a388abc60abb7499794177ac54ad1b3f6118"
        seed.write_text(json.dumps({"studio": "R10 accepted", "master_sha256": master, "favorites": ["R2-A1", "R2-B1", "R3-B2", "R3-C1", "R3-D3"], "constraints": {"visual_preview_limit": 12}, "platforms": ["Android", "iOS"], "extra_spend": 0}))
        result = subprocess.run([sys.executable, str(self.script), "project-init", str(other), "--project-id", "tatterjack", "--seed", str(seed)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        imported = json.loads((other / ".gameatelier/orchestrator/state.json").read_text())
        self.assertEqual(imported["seed_history"]["master_sha256"], master)
        self.assertIsNone(imported["production_choice"])
        self.assertEqual(len(imported["favorites"]), 5)
        self.assertTrue(all(row["status"] == "saved_only" for row in imported["favorites"]))
        intent = self.base / "intent.json"
        intent.write_text(json.dumps({"kind": "incident", "stage": "build", "scope": "save-migration", "source": "user incident"}))
        routed = self.call("route", "--intent", intent)
        self.assertEqual(routed["stage"], "build")
        self.assertTrue(routed["partial_route"])
        self.assertEqual(self.state()["tasks"], {})
        intent.write_text(json.dumps({"kind": "fix all the stuff", "stage": "build", "scope": "project", "source": "text"}))
        self.call("route", "--intent", intent, expected=2)

    def test_zip_traversal_symlink_and_duplicate_are_rejected_before_import(self):
        for name, members in (("traversal", [("../escape.txt", b"bad", None)]), ("symlink", [("link", b"../outside", stat.S_IFLNK | 0o777)]), ("duplicate", [("same", b"a", None), ("same", b"b", None)])):
            path = self.base / (name + ".zip")
            with zipfile.ZipFile(path, "w") as archive:
                for filename, content, mode in members:
                    info = zipfile.ZipInfo(filename)
                    if mode:
                        info.external_attr = mode << 16
                    archive.writestr(info, content)
            self.call("intake", "--source", path, record={"id": name, "source": "uploaded fixture", "rights": "fixture owned", "authority_ref": "user import"}, expected=2)
        self.assertFalse((self.base / "escape.txt").exists())
        self.assertEqual(self.state()["intakes"], [])
        self.assertEqual(list((self.project / ".gameatelier/orchestrator").glob("intake-*")), [])

    def test_intake_keeps_exact_originals_provenance_and_never_executes(self):
        src = self.base / "incoming"
        src.mkdir()
        marker = self.base / "SHOULD_NOT_EXIST"
        (src / "run.py").write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        (src / "master.bin").write_bytes(b"approved exact bytes")
        master_hash = hashlib.sha256(b"approved exact bytes").hexdigest()
        provenance = {"id": "upload1", "source": "actual upload fixture", "rights": "user-owned fixture", "authority_ref": "import only", "approved_masters": [{"path": "master.bin", "sha256": master_hash, "approval_scope": "studio-R10-only", "authority_ref": "prior-approval"}]}
        self.call("intake", "--source", src, record=provenance)
        self.assertFalse(marker.exists())
        self.assertTrue(self.call("intake", "--source", src, record=provenance)["replayed"])
        original = self.project / ".gameatelier/orchestrator/intakes/upload1/payload/master.bin"
        self.assertEqual(original.read_bytes(), b"approved exact bytes")
        original.write_bytes(b"tamper")
        self.assertTrue(self.call("refresh")["integrity_errors"])
        self.assertFalse(self.call("resume", expected=1)["ready"])

    def test_directory_symlink_rejected(self):
        src = self.base / "incoming"
        src.mkdir()
        (src / "sym").symlink_to(self.base / "outside")
        self.call("intake", "--source", src, record={"id": "directory", "source": "fixture", "rights": "fixture", "authority_ref": "import"}, expected=2)
        self.assertEqual(self.state()["intakes"], [])

    def test_approval_exact_revision_scope_replay_and_stale_dependency(self):
        self.artifact()
        self.decision(depends_on=["ART"])
        state = self.state()
        self.call("confirm", "--id", "DEC", "--choice", "yes", "--scope", "project", "--decision-revision", 1, "--project-revision", state["revision"] - 1, "--authority", "user-message:actual-fixture", expected=2)
        self.call("confirm", "--id", "DEC", "--choice", "yes", "--scope", "other", "--decision-revision", 1, "--project-revision", state["revision"], "--authority", "user-message:actual-fixture", expected=2)
        confirmed = self.confirm()
        original_revision = state["revision"]
        replay = self.call("confirm", "--id", "DEC", "--choice", "yes", "--scope", "project", "--decision-revision", 1, "--project-revision", original_revision, "--authority", "user-message:actual-fixture")
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["project_revision"], confirmed["project_revision"])
        self.write("art.txt", "new bytes")
        self.call("refresh")
        self.assertEqual(self.state()["decisions"]["DEC"]["status"], "stale")
        self.confirm(expected=2)

    def test_actual_task_evidence_completion_and_no_replay(self):
        self.task(artifact_ids=["ART"], required_modalities=["document"])
        self.call("start", "--task", "TASK")
        self.artifact()
        self.evidence()
        self.call("complete", "--task", "TASK", "--evidence", "PROOF")
        self.assertFalse(self.call("start", "--task", "TASK", expected=1)["ready"])
        self.call("resume")
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "completed")
        self.write("proof.json", "changed proof")
        self.call("refresh")
        self.assertEqual(self.state()["evidence"]["PROOF"]["status"], "stale")

    def test_independent_review_and_required_modalities(self):
        self.artifact()
        self.evidence(observer="maker", expected=2)
        self.evidence()
        self.task(artifact_ids=["ART"], required_modalities=["audio", "device"])
        self.call("start", "--task", "TASK")
        self.call("complete", "--task", "TASK", "--evidence", "PROOF", expected=2)
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "running")

    def legacy_task_modalities(self, ident="TASK", modalities=None, actions=None):
        """Synthetic pre-validation native state, never a suggested repair API."""
        state = self.state()
        state["tasks"][ident]["required_modalities"] = modalities if modalities is not None else ["simulation", "document"]
        state["actions"].update(actions or {})
        state.pop("snapshot_hash")
        state["snapshot_hash"] = hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        (self.project / ".gameatelier/orchestrator/state.json").write_text(json.dumps(state))

    def modality_correction(self, ident="TASK"):
        ready = self.call("readiness", "--task", ident, expected=1)
        return {"id": ident, "expected_task_token": ready["task_token"], "expected_status": ready["task_status"], "modality_replacements": {"simulation": ["document"]}, "source": "actual local simulation output and original task record", "reason": "Simulation is the procedure; its actual proof is a JSON document, not a media/play observation."}

    def test_unknown_task_modalities_reject_before_registration_or_replacement(self):
        state_path = self.project / ".gameatelier/orchestrator/state.json"
        before = state_path.read_bytes()
        self.task("FIRST", required_modalities=["simulation"], expected=2)
        self.assertEqual(state_path.read_bytes(), before)
        self.assertEqual(self.state()["tasks"], {})
        self.task(required_modalities=["document"])
        for ident, modalities in (("NEW", ["simulation"]), ("TASK", ["document", "simulation"]), ("BAD", "document")):
            with self.subTest(ident=ident):
                before = state_path.read_bytes()
                result = self.task(ident, required_modalities=modalities, expected=2)
                self.assertIn("required_modalities", result["error"])
                self.assertEqual(state_path.read_bytes(), before)
        self.assertEqual(set(self.state()["tasks"]), {"TASK"})

    def test_registry_modalities_are_supported_by_task_and_evidence_registration(self):
        self.artifact()
        for modality in ("visual", "audio", "haptic", "play", "device", "build", "document", "external_receipt"):
            with self.subTest(modality=modality):
                self.task("TASK-" + modality, required_modalities=[modality])
                suffix = ".png" if modality == "visual" else ".wav" if modality == "audio" else ".json"
                proof = "observed-" + modality + suffix
                # Fixture bytes exercise transport/registry only; no media-quality assertion.
                self.write(proof, "fixture representation only")
                self.evidence("PROOF-" + modality, modality=modality, proof_path=proof, environment="isolated fixture", observed_at="2026-11-04T00:00:00Z", method="Explicit synthetic registry transport check")
        self.evidence("UNSUPPORTED", modality="simulation", expected=2)

    def test_loaded_legacy_modalities_block_planned_and_running_work(self):
        self.task("PLANNED", required_modalities=["document"])
        self.task("RUNNING", required_modalities=["document"])
        self.call("start", "--task", "RUNNING")
        for ident in ("PLANNED", "RUNNING"):
            self.legacy_task_modalities(ident)
            ready = self.call("readiness", "--task", ident, expected=1)
            self.assertIn("unsupported required_modalities", " ".join(ready["blockers"]))
            self.assertEqual(len(ready["task_token"]), 64)
            self.assertEqual(ready["task_status"], self.state()["tasks"][ident]["status"])
            self.call("start", "--task", ident, expected=1)
            self.call("complete", "--task", ident, "--evidence", "MISSING", expected=1)

    def test_modality_reconciliation_requires_exact_narrow_request_and_terminal_guard(self):
        self.task(required_modalities=["document", "audio"])
        self.call("start", "--task", "TASK")
        self.legacy_task_modalities(modalities=["simulation", "document", "audio"])
        correct = self.modality_correction()
        variants = [
            {**correct, "expected_task_token": "0" * 64},
            {**correct, "expected_status": "planned"},
            {**correct, "modality_replacements": {"simulation": []}},
            {**correct, "modality_replacements": {"simulation": ["unknown"]}},
            {**correct, "modality_replacements": {"simulation": ["document", "document"]}},
            {**correct, "modality_replacements": {"simulation": ["document"], "audio": ["document"]}},
            {**correct, "modality_replacements": {"different": ["document"]}},
            {**correct, "goal": "silently change approved work"},
            {**correct, "source": " "},
            {**correct, "reason": False},
            {key: value for key, value in correct.items() if key != "expected_task_token"},
        ]
        state_path = self.project / ".gameatelier/orchestrator/state.json"
        for variant in variants:
            with self.subTest(variant=variant):
                before = state_path.read_bytes()
                self.call("reconcile-task-modalities", record=variant, expected=2)
                self.assertEqual(state_path.read_bytes(), before)
        self.task("VALID", required_modalities=["document"])
        ready = self.call("readiness", "--task", "VALID")
        self.call("reconcile-task-modalities", record={**correct, "id": "VALID", "expected_status": ready["task_status"], "expected_task_token": ready["task_token"]}, expected=2)
        self.task("DONE", artifact_ids=["ART"], required_modalities=["document"])
        self.call("start", "--task", "DONE")
        self.artifact(); self.evidence()
        self.call("complete", "--task", "DONE", "--evidence", "PROOF")
        self.legacy_task_modalities("DONE")
        ready = self.call("readiness", "--task", "DONE", expected=1)
        self.call("reconcile-task-modalities", record={**correct, "id": "DONE", "expected_status": ready["task_status"], "expected_task_token": ready["task_token"]}, expected=2)

    def test_modality_reconciliation_blocks_only_linked_unresolved_effects(self):
        self.task(required_modalities=["document"])
        self.call("start", "--task", "TASK")
        for status in ("pending", "unknown"):
            with self.subTest(status=status):
                self.legacy_task_modalities(actions={"EFFECT": {"id": "EFFECT", "task": "TASK", "status": status}})
                correction = self.modality_correction()
                before = self.state()
                result = self.call("reconcile-task-modalities", record=correction, expected=2)
                self.assertIn("pending/unknown", result["error"])
                self.assertEqual(self.state(), before)
        self.legacy_task_modalities(actions={"EFFECT": {"id": "EFFECT", "task": "OTHER", "status": "unknown"}})
        result = self.call("reconcile-task-modalities", record=self.modality_correction())
        self.assertFalse(result["actual_execution"])
        self.assertEqual(self.state()["actions"]["EFFECT"]["status"], "unknown")

    def test_running_modality_reconciliation_preserves_contract_pause_and_independent_work(self):
        self.task("UNRELATED", artifact_ids=["OTHER-ART"], required_modalities=["document"])
        self.call("start", "--task", "UNRELATED")
        self.artifact("OTHER-ART"); self.evidence("OTHER-PROOF", artifact="OTHER-ART")
        self.call("complete", "--task", "UNRELATED", "--evidence", "OTHER-PROOF")
        unrelated = self.state()["tasks"]["UNRELATED"]
        self.task(artifact_ids=["ART"], required_modalities=["document"], independent_review_required=True, stop="return after this bounded result", exact_authority_ref="actual original task source")
        self.call("start", "--task", "TASK")
        self.artifact(); self.evidence()
        self.legacy_task_modalities()
        self.task("DEPENDENT", depends_on=["TASK"])
        self.call("pause", "--when", "now")
        correction = self.modality_correction()
        before = self.state()
        result = self.call("reconcile-task-modalities", record=correction)
        after = self.state()
        self.assertEqual(after["tasks"]["TASK"]["required_modalities"], ["document", "document"])
        self.assertEqual({key: value for key, value in after["tasks"]["TASK"].items() if key not in {"required_modalities", "modality_reconciliations"}}, {key: value for key, value in before["tasks"]["TASK"].items() if key not in {"required_modalities", "modality_reconciliations"}})
        self.assertEqual(after["tasks"]["TASK"]["status"], "running")
        self.assertEqual(after["pause"], before["pause"])
        self.assertEqual(after["tasks"]["UNRELATED"], unrelated)
        self.assertEqual(result["invalidated_dependents"], ["DEPENDENT"])
        self.assertTrue(after["tasks"]["DEPENDENT"]["stale_reasons"])
        self.assertFalse(result["actual_execution"]); self.assertFalse(result["completed"])
        self.assertEqual(after["journal"][-1]["command"], "reconcile-task-modalities")
        audit = after["tasks"]["TASK"]["modality_reconciliations"][-1]
        self.assertEqual(audit["previous_modalities"], ["simulation", "document"])
        self.assertEqual(audit["prior_task_token"], correction["expected_task_token"])
        self.call("complete", "--task", "TASK", "--evidence", "PROOF", expected=1)
        self.call("resume")
        self.call("start", "--task", "TASK", expected=2)
        self.call("complete", "--task", "TASK", "--evidence", "PROOF")
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "completed")

    def test_planned_legacy_modality_reconciliation_never_starts_task(self):
        self.task(required_modalities=["document"])
        self.legacy_task_modalities(modalities=["simulation"])
        self.call("reconcile-task-modalities", record=self.modality_correction())
        row = self.state()["tasks"]["TASK"]
        self.assertEqual(row["status"], "planned")
        self.assertNotIn("started_at", row)
        self.assertNotIn("completed_at", row)
        self.assertTrue(self.call("readiness", "--task", "TASK")["ready"])

    def test_late_knowledge_invalidation_is_selective_and_context_current(self):
        self.artifact("CONCEPT", "concepts")
        self.artifact("STUDIO", "studio")
        self.evidence(artifact="CONCEPT")
        self.task(depends_on=["CONCEPT"])
        self.call("start", "--task", "TASK")
        before = self.state()["knowledge_revision"]
        lesson = {"id": "KN-MOTION", "source": "actual device study fixture", "verbatim_source": "Contact cue obscured", "text": "Revise contact cue", "scope": "project", "confidence": "observed", "stages": ["concepts"], "impact_ids": [], "impact_reason": "Contact cue changes concept decision"}
        changed = self.call("ledger", "--kind", "knowledge", record=lesson)
        self.assertIn("CONCEPT", changed["affected_ids"])
        state = self.state()
        self.assertGreater(state["knowledge_revision"], before)
        self.assertEqual(state["artifacts"]["CONCEPT"]["status"], "stale")
        self.assertEqual(state["evidence"]["PROOF"]["status"], "stale")
        self.assertEqual(state["tasks"]["TASK"]["status"], "stale")
        self.assertEqual(state["artifacts"]["STUDIO"]["status"], "final")
        context = self.call("context", "--stage", "concepts", "--query", "contact")
        self.assertIn("KN-MOTION", [r["id"] for r in context["items"]])
        self.task("TASK2")
        self.assertIn("KN-MOTION", self.state()["tasks"]["TASK2"]["depends_on"])

    def test_pending_requirement_can_be_implemented_but_completion_needs_closure(self):
        req = {"id": "REQ", "source": "actual user fixture", "verbatim_source": "Need a current document", "intent": "Document proof", "stage": "concepts", "scope": "project", "owner": "maker", "status": "pending", "priority": "must", "acceptance": "Current output and independent proof", "artifact_ids": [], "evidence_ids": [], "depends_on": []}
        self.call("ledger", "--kind", "requirement", record=req)
        self.task(fulfills_requirements=["REQ"], artifact_ids=["ART"])
        self.call("start", "--task", "TASK")
        self.artifact(depends_on=["REQ"])
        self.evidence()
        self.call("complete", "--task", "TASK", "--evidence", "PROOF", expected=1)
        req.update(status="met", closure="Actual proof recorded", artifact_ids=["ART"], evidence_ids=["PROOF"])
        self.call("ledger", "--kind", "requirement", record=req)
        self.call("complete", "--task", "TASK", "--evidence", "PROOF")

    def test_pause_exact_artifact_boundary_and_resume(self):
        self.task()
        self.call("pause", "--when", "artifact", "--target", "STOP")
        self.call("start", "--task", "TASK")
        self.artifact("OTHER")
        self.assertFalse(self.state()["pause"]["active"])
        self.artifact("STOP")
        self.assertTrue(self.state()["pause"]["active"])
        self.task("TASK2")
        self.assertFalse(self.call("start", "--task", "TASK2", expected=1)["ready"])
        checkpoint = self.call("brief", parse=False)
        self.assertIn("after artifact STOP", checkpoint)
        self.assertIn("Return:", checkpoint)
        self.call("resume")
        self.call("start", "--task", "TASK2")
        self.call("pause", "--when", "now")
        self.assertFalse(self.call("readiness", "--task", "TASK2", expected=1)["ready"])

    def setup_action(self):
        self.artifact(stage="liveops")
        self.decision(stage="liveops", scope="publish-scope", approval={"option": "yes", "effects": ["upload"], "artifact_ids": ["ART"]})
        self.confirm(scope="publish-scope")
        self.call("capability", record={"id": "CAP", "source": "actual service availability fixture", "available": True, "scope": "publish-scope", "environment": "fixture-only", "verified_at": "2026-11-01T00:00:00Z"})
        self.task(stage="liveops", scope="publish-scope", required_decisions=["DEC"])
        self.call("start", "--task", "TASK")
        action = {"id": "ACT", "idempotency_key": "once-key", "type": "upload", "scope": "publish-scope", "source": "actual user upload instruction fixture", "decision_id": "DEC", "decision_revision": 1, "capability_id": "CAP", "environment": "fixture-only", "prepared_artifact_ids": ["ART"], "task": "TASK"}
        self.call("action", record=action)
        return action

    def test_pending_unknown_action_never_retries_and_receipts_idempotent(self):
        action = self.setup_action()
        self.assertTrue(self.call("action", record=action)["replayed"])
        self.call("dispatch", "--id", "ACT", "--project-revision", self.state()["revision"])
        self.call("dispatch", "--id", "ACT", "--project-revision", self.state()["revision"], expected=2)
        self.assertFalse(self.call("resume", expected=1)["ready"])
        self.write("receipt.json", '{"provider_read":"unknown"}')
        receipt = {"source": "actual provider query fixture", "provider_ref": "provider-object-1", "proof_path": "receipt.json"}
        self.call("receipt", "--id", "ACT", "--outcome", "unknown", record=receipt)
        self.call("receipt", "--id", "ACT", "--outcome", "succeeded", record=receipt, expected=2)
        receipt["reconciled"] = True
        self.call("receipt", "--id", "ACT", "--outcome", "succeeded", record=receipt)
        final = self.call("receipt", "--id", "ACT", "--outcome", "succeeded", record=receipt)
        self.assertTrue(final["replayed"])
        self.assertEqual(len(self.state()["actions"]["ACT"]["receipt_history"]), 2)
        self.call("resume")
        self.call("dispatch", "--id", "ACT", "--project-revision", self.state()["revision"], expected=2)
        self.call("action", record={**action, "id": "ACT2"}, expected=2)

    def test_concurrent_writers_preserve_journal_and_changes(self):
        def write_cap(index):
            record = {"id": "CAP-" + str(index), "source": "concurrent fixture", "available": False, "scope": "project", "environment": "fixture", "verified_at": "2026-11-01T00:00:00Z"}
            return subprocess.run([sys.executable, str(self.script), "capability", str(self.project), "--record", "-"], input=json.dumps(record), capture_output=True, text=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(write_cap, range(6)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
        state = self.state()
        self.assertEqual(len(state["capabilities"]), 6)
        self.assertEqual(state["revision"], 7)
        self.assertEqual(len(state["journal"]), 7)
        self.call("brief", parse=False)  # validates event hash chain and snapshot

    def test_suite_hash_gate_needs_reviewed_refresh_and_preserves_handoff_protocol(self):
        self.task()
        (self.bundle / "assets/stage-catalog.json").write_text('{"schema_version":"2.0.0","changed":true}')
        self.assertFalse(self.call("readiness", "--task", "TASK", expected=1)["ready"])
        self.call("refresh", "--accept-suite-update", expected=2)
        result = self.call("refresh", "--accept-suite-update", "--authority", "agent-reviewed-contract-impact", "--impact", "TASK")
        self.assertFalse(result["suite_mismatch"])
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "stale")
        self.assertEqual(self.state()["handoff_protocol"], "1.0.0")

    def test_existing_canonical_authority_is_preserved_and_changes_invalidate(self):
        canonical = self.project / ".gameatelier/decisions.json"
        authority = {"items": [{"id": "DEC", "status": "confirmed", "answer": "yes", "scope": "project", "authority_ref": "old-actual-approval"}]}
        canonical.write_text(json.dumps(authority))
        self.decision(expected=2)
        linked = self.decision(canonical_ref=".gameatelier/decisions.json#DEC", canonical_sha256=hashlib.sha256(canonical.read_bytes()).hexdigest())
        self.assertEqual(linked["decision"]["authority_ref"], "old-actual-approval")
        self.assertEqual(linked["decision"]["status"], "confirmed")
        self.assertEqual(json.loads(canonical.read_text()), authority)
        self.task(required_decisions=["DEC"], depends_on=["DEC"])
        authority["items"][0]["answer"] = "no"
        canonical.write_text(json.dumps(authority))
        self.assertFalse(self.call("readiness", "--task", "TASK", expected=1)["ready"])
        self.assertEqual(self.state()["decisions"]["DEC"]["status"], "stale")

    def test_manual_bridge_requires_concrete_environment_paths_and_return(self):
        bridge = {"id": "BRIDGE", "environment": "macOS with installed Xcode", "working_path": "relative", "command": ["xcodebuild", "-version"], "expected_result": "Version output, no signing", "return_path": str(self.project / "return"), "return_instructions": "Return exact logs and toolchain version", "scope": "toolchain-observation", "missing_capability": "macOS executor", "launch_steps": ["Open the named local checkout", "Run exact argv", "Save output and return it"]}
        self.call("handoff", record=bridge, expected=2)
        bridge["working_path"] = str(self.project)
        result = self.call("handoff", record=bridge, parse=False)
        self.assertIn("MANUAL BRIDGE (not executed)", result)
        self.assertIn("xcodebuild", result)
        self.assertEqual(self.state()["bridges"][0]["return_path"], bridge["return_path"])

    def test_exact_original_byte_approval_cannot_be_replaced(self):
        original = self.write("master.bin", "exact accepted original")
        original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
        self.decision(scope="R10-master-only", approved_sha256=original_hash, approval={"option": "yes", "effects": ["master"]})
        self.confirm(scope="R10-master-only")
        self.call("artifact", record={"id": "MASTER", "path": "master.bin", "stage": "studio", "scope": "R10-master-only", "kind": "brand_master", "author_ids": ["maker"], "status": "reference", "approval_decision": "DEC"})
        self.assertTrue(self.state()["artifacts"]["MASTER"]["immutable"])
        original.write_text("replacement")
        self.call("artifact", record={"id": "MASTER", "path": "master.bin", "stage": "studio", "scope": "R10-master-only", "kind": "brand_master", "author_ids": ["maker"], "status": "reference", "approval_decision": "DEC"}, expected=2)
        self.assertEqual(self.state()["artifacts"]["MASTER"]["sha256"], original_hash)
        self.assertTrue(self.state()["integrity_errors"])

    def test_stop_search_and_production_choice_are_explicit_distinct_decisions(self):
        self.decision("DEC-STOP", scope="concept-search", effect="stop_search", options=["stop", "continue"], consequences={"stop": "Stop searching", "continue": "Search within current scope"}, recommendation="stop")
        self.confirm("DEC-STOP", "stop", "concept-search")
        self.assertTrue(self.state()["search_stopped"])
        self.assertIsNone(self.state()["production_choice"])
        self.decision("DEC-CHOOSE", scope="production-concept", effect="production_choice", options=["R2-A1", "R3-D3"], consequences={"R2-A1": "Develop exact chosen concept", "R3-D3": "Develop other exact concept"}, recommendation="R2-A1")
        self.confirm("DEC-CHOOSE", "R2-A1", "production-concept")
        self.assertEqual(self.state()["production_choice"], "R2-A1")

    def test_after_stage_pause_uses_authoritative_accepted_pipeline_gate(self):
        package = self.project / "handoff"
        package.mkdir()
        kinds = "studio_identity brand_master brand_rules setup_runbook rights_ledger".split()
        artifacts = []
        for index, kind in enumerate(kinds):
            path = package / (kind + ".txt")
            path.write_text("actual fixture bytes " + kind)
            artifacts.append({"id": "PKG-" + str(index), "path": path.name, "kind": kind, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "final", "author_ids": ["maker"], "depends_on": []})
        proof = package / "proof.json"
        proof.write_text('{"fixture":"integrity verification, not product quality"}')
        evidence_hash = hashlib.sha256(proof.read_bytes()).hexdigest()
        artifacts.append({"id": "PKG-EV", "path": proof.name, "kind": "evidence", "sha256": evidence_hash, "status": "reference", "author_ids": [], "depends_on": []})
        records = {
            "requirements": [{"id": "REQ-PKG", "status": "met", "owner": "maker", "acceptance": "Declared fixture scope", "artifact_ids": ["PKG-0"], "evidence_ids": ["PKG-EV"]}],
            "decisions": [{"id": "DEC-BRAND", "material": True, "status": "confirmed", "answer": "fixture brand", "authority_ref": "actual fixture authority"}],
            "claims": [],
            "reviews": [{"id": "REV-" + artifact["id"], "status": "pass", "reviewer_id": "independent-qa", "artifact_ids": [artifact["id"]], "artifact_hashes": {artifact["id"]: artifact["sha256"]}, "dependency_hashes": {}, "evidence_ids": ["PKG-EV"], "evidence_hashes": {"PKG-EV": evidence_hash}} for artifact in artifacts if artifact["kind"] != "evidence"]
        }
        for name, rows in records.items():
            path = package / "records" / (name + ".json")
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps({"items": rows}))
            artifacts.append({"id": "PKG-REC-" + name, "path": "records/" + path.name, "kind": "record", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "final", "author_ids": [], "depends_on": []})
        manifest = {"schema_version": "1.0.0", "suite_version": "1.0.0", "toolkit_version": "5.0.0", "package_id": "test-project-studio-r1", "project_id": "test-project", "stage": "studio", "revision": 1, "stage_status": "draft", "upstream": [], "artifacts": artifacts}
        manifest_path = package / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        self.call("pause", "--when", "stage", "--target", "studio")
        self.call("stage-check", "--package", package, "--require-accepted", expected=1)
        self.assertFalse(self.state()["pause"]["active"])
        manifest["stage_status"] = "accepted"
        manifest_path.write_text(json.dumps(manifest))
        result = self.call("stage-check", "--package", package, "--require-accepted")
        self.assertTrue(result["valid"])
        self.assertFalse(result["quality_certified"])
        self.assertTrue(self.state()["pause"]["active"])
        self.assertEqual(self.state()["pause"]["reason"], "after stage studio")
        self.assertEqual(len(self.state()["stage_checks"]), 1)

    def test_replaced_pending_choice_revokes_cached_production_authority(self):
        self.test_stop_search_and_production_choice_are_explicit_distinct_decisions()
        self.decision("DEC-CHOOSE", scope="production-concept", effect="production_choice", options=["C", "D"], consequences={"C": "Other concept", "D": "Different concept"}, recommendation="C")
        self.assertIsNone(self.state()["production_choice"])
        self.task("BUILD", stage="build")
        self.assertFalse(self.call("readiness", "--task", "BUILD", expected=1)["ready"])
        self.decision("DEC-STOP", scope="concept-search", effect="stop_search", options=["stop", "continue"], consequences={"stop": "Stop", "continue": "Continue"}, recommendation="stop")
        self.assertFalse(self.state()["search_stopped"])

    def test_completed_task_proof_change_invalidates_downstream_completion_dependency(self):
        self.task(artifact_ids=["ART"])
        self.call("start", "--task", "TASK")
        self.artifact()
        self.evidence()
        self.call("complete", "--task", "TASK", "--evidence", "PROOF")
        self.task("DOWN", depends_on=["TASK"])
        self.call("readiness", "--task", "DOWN")
        self.write("proof.json", "proof changed after review")
        self.call("refresh")
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "stale")
        self.assertFalse(self.call("readiness", "--task", "DOWN", expected=1)["ready"])

    def test_declining_exact_effect_permission_never_dispatches(self):
        self.artifact(stage="liveops")
        self.decision(stage="liveops", scope="publish-scope", approval={"option": "yes", "effects": ["upload"], "artifact_ids": ["ART"]})
        self.confirm(choice="no", scope="publish-scope")
        self.call("capability", record={"id": "CAP", "source": "observed fixture", "available": True, "scope": "publish-scope", "environment": "fixture-only", "verified_at": "2026-11-01"})
        self.task(stage="liveops", scope="publish-scope", required_decisions=["DEC"])
        self.call("start", "--task", "TASK")
        self.call("action", record={"id": "ACT", "idempotency_key": "declined-effect", "type": "upload", "scope": "publish-scope", "source": "actual instruction fixture", "decision_id": "DEC", "decision_revision": 1, "capability_id": "CAP", "environment": "fixture-only", "prepared_artifact_ids": ["ART"], "task": "TASK"})
        self.call("dispatch", "--id", "ACT", "--project-revision", self.state()["revision"], expected=2)
        self.assertEqual(self.state()["actions"]["ACT"]["status"], "prepared")

    def test_requirement_closure_must_cover_exact_artifacts(self):
        self.artifact("A")
        self.artifact("B")
        self.evidence(artifact="B")
        self.call("ledger", "--kind", "requirement", record={"id": "REQ", "source": "user fixture", "verbatim_source": "Need A", "intent": "A", "stage": "concepts", "scope": "project", "owner": "maker", "status": "met", "priority": "must", "acceptance": "Actual A proof", "artifact_ids": ["A"], "evidence_ids": ["PROOF"], "closure": "Wrong artifact proof"}, expected=2)
        self.assertNotIn("REQ", self.state()["requirements"])

    def test_canonical_requirement_cannot_be_downgraded_or_reinterpreted(self):
        path = self.project / ".gameatelier/requirements.json"
        canonical = {"id": "REQ", "source": "original", "verbatim_source": "Original must", "intent": "Original scope", "stage": "concepts", "scope": "project", "owner": "maker", "status": "pending", "priority": "must", "acceptance": "Original acceptance", "artifact_ids": [], "evidence_ids": [], "depends_on": []}
        path.write_text(json.dumps({"items": [canonical]}))
        linked = {**canonical, "canonical_ref": ".gameatelier/requirements.json#REQ", "canonical_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.call("ledger", "--kind", "requirement", record={**linked, "status": "not_applicable", "priority": "could", "closure": "Sidecar override"}, expected=2)
        self.call("ledger", "--kind", "requirement", record={**linked, "intent": "Different intent"}, expected=2)
        self.call("ledger", "--kind", "requirement", record=linked)
        self.assertEqual(self.state()["requirements"]["REQ"]["priority"], "must")

    def test_canonical_master_hash_cannot_be_repurposed(self):
        path = self.project / ".gameatelier/decisions.json"
        original = self.write("master.bin", "original")
        original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
        approval = {"option": "yes", "effects": ["master"]}
        canonical = {"id": "DEC", "status": "confirmed", "answer": "yes", "scope": "master-only", "authority_ref": "prior exact byte authority", "approved_sha256": original_hash, "approval": approval}
        path.write_text(json.dumps({"items": [canonical]}))
        link = {"canonical_ref": ".gameatelier/decisions.json#DEC", "canonical_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        changed = hashlib.sha256(b"replacement").hexdigest()
        self.decision(scope="master-only", approved_sha256=changed, approval=approval, **link, expected=2)
        self.decision(scope="master-only", approved_sha256=original_hash, approval=approval, **link)
        self.call("artifact", record={"id": "MASTER", "path": "master.bin", "stage": "studio", "scope": "master-only", "kind": "brand_master", "author_ids": ["maker"], "status": "reference", "approval_decision": "DEC"})
        self.assertEqual(self.state()["artifacts"]["MASTER"]["sha256"], original_hash)

    def test_production_flag_bypass_rejected_but_exact_partial_route_supported(self):
        self.task("BYPASS", stage="build", requires_production_choice=False, expected=2)
        intent = {"kind": "incident", "stage": "build", "scope": "migration-only", "source": "exact user incident", "operation": "repair"}
        source = self.base / "intent.json"
        source.write_text(json.dumps(intent))
        self.call("route", "--intent", source)
        self.task("PARTIAL", stage="build", scope="migration-only", source="exact user incident", requires_production_choice=False)
        self.call("readiness", "--task", "PARTIAL")
        self.task("WRONG-SCOPE", stage="build", scope="whole-product", source="exact user incident", requires_production_choice=False, expected=2)

    def test_changed_pipeline_is_never_imported_before_suite_guard(self):
        marker = self.base / "EXECUTED"
        path = self.bundle / "scripts/pipeline.py"
        path.write_text(path.read_text() + "\nfrom pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad import')\n")
        package = self.project / "empty-package"
        package.mkdir()
        self.call("stage-check", "--package", package, expected=2)
        self.assertFalse(marker.exists())
        self.assertTrue(self.state()["suite_mismatch"])

    def test_stage_acceptance_cannot_ignore_new_current_project_must(self):
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        self.call("resume")
        self.call("ledger", "--kind", "requirement", record={"id": "REQ-NEW", "source": "new user fixture", "verbatim_source": "New must", "intent": "New stage must", "stage": "studio", "scope": "project", "owner": "maker", "status": "pending", "priority": "must", "acceptance": "New acceptance", "artifact_ids": [], "evidence_ids": [], "depends_on": []})
        self.call("pause", "--when", "stage", "--target", "studio")
        self.call("stage-check", "--package", self.project / "handoff", "--require-accepted", expected=2)
        self.assertFalse(self.state()["pause"]["active"])

    def test_fulfilled_should_requirement_still_needs_actual_closure(self):
        self.call("ledger", "--kind", "requirement", record={"id": "REQ", "source": "user fixture", "verbatim_source": "Should complete this", "intent": "Declared task promise", "stage": "concepts", "scope": "project", "owner": "maker", "status": "pending", "priority": "should", "acceptance": "Actual closure", "artifact_ids": [], "evidence_ids": [], "depends_on": []})
        self.task(fulfills_requirements=["REQ"], artifact_ids=["ART"])
        self.call("start", "--task", "TASK")
        self.artifact()
        self.evidence()
        self.call("complete", "--task", "TASK", "--evidence", "PROOF", expected=1)
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "running")

    def test_future_pause_cannot_clear_active_pause_without_resume(self):
        self.call("pause", "--when", "now")
        self.call("pause", "--when", "artifact", "--target", "STOP", expected=2)
        self.task()
        self.call("start", "--task", "TASK", expected=1)
        self.assertTrue(self.state()["pause"]["active"])

    def test_explicit_full_concepts_operation_cannot_downgrade_into_preview_task(self):
        intent = {"kind": "stage", "stage": "concepts", "scope": "project", "source": "actual full concepts request", "operation": "full_concepts"}
        path = self.base / "intent.json"
        path.write_text(json.dumps(intent))
        self.call("route", "--intent", path)
        self.task("C1", source=intent["source"], requires_production_choice=False)
        self.call("readiness", "--task", "C1")
        self.task("WRONG-SOURCE", source="different request", expected=2)
        self.task("DOWNGRADE", source=intent["source"], operation="visual_previews", expected=2)
        self.task("FULL", source=intent["source"])
        self.assertEqual(self.state()["tasks"]["FULL"]["operation"], "full_concepts")
        self.call("readiness", "--task", "FULL")
        self.test_stop_search_and_production_choice_are_explicit_distinct_decisions()
        self.call("readiness", "--task", "FULL")

    def test_stage_check_never_creates_bundle_bytecode_cache(self):
        before = {path.relative_to(self.bundle).as_posix(): path.read_bytes() for path in self.bundle.rglob("*") if path.is_file()}
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        after = {path.relative_to(self.bundle).as_posix(): path.read_bytes() for path in self.bundle.rglob("*") if path.is_file()}
        self.assertEqual(after, before, "legitimate stage-check must leave installed bundle bytes and file set unchanged")
        self.assertFalse((self.bundle / "scripts/__pycache__").exists())

    def test_timestamp_valid_pipeline_bytecode_is_ignored(self):
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        self.call("resume")
        pipeline = self.bundle / "scripts/pipeline.py"
        marker = self.base / "MALICIOUS-CACHE-EXECUTED"
        malicious_source = "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\nraise RuntimeError('timestamp cache executed')\n"
        pipeline_stat = pipeline.stat()
        header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(pipeline_stat.st_mtime) & 0xffffffff, pipeline_stat.st_size & 0xffffffff)
        poisoned = header + marshal.dumps(compile(malicious_source, str(pipeline), "exec"))
        cache = Path(importlib.util.cache_from_source(str(pipeline)))
        cache.parent.mkdir(exist_ok=True)
        cache.write_bytes(poisoned)
        # This header is valid for the unchanged checked source: SourceFileLoader
        # would accept and execute it. The runtime must compile the source bytes.
        result = self.call("stage-check", "--package", self.project / "handoff", "--require-accepted")
        self.assertTrue(result["valid"])
        self.assertFalse(marker.exists())
        self.assertEqual(cache.read_bytes(), poisoned, "runtime must neither read for execution nor rewrite an existing .pyc")
        self.assertEqual(list(cache.parent.iterdir()), [cache])


    def reseal_package_records(self, **changes):
        package = self.project / "handoff"
        for name, rows in changes.items():
            (package / "records" / (name + ".json")).write_text(json.dumps({"items": rows}))
        manifest_path = package / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest["artifacts"]:
            if row["path"].startswith("records/"):
                row["sha256"] = hashlib.sha256((package / row["path"]).read_bytes()).hexdigest()
        manifest["project_context"] = self.call("context", "--stage", "studio", "--scope", manifest.get("scope", "project"))["stage_context_snapshot"]
        manifest_path.write_text(json.dumps(manifest))

    def project_requirement(self, **extra):
        return {"id": "REQ-MULTI", "source": "user fixture", "verbatim_source": "Required in both declared stages", "intent": "Multi-stage contract", "stage": "concepts", "stages": ["studio", "concepts"], "scope": "project", "owner": "maker", "status": "pending", "priority": "must", "acceptance": "Declared fixture acceptance", "artifact_ids": [], "evidence_ids": [], "depends_on": [], **extra}

    def test_multistage_must_blocks_task_and_accepted_package_even_without_flag(self):
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        self.call("resume")
        self.call("ledger", "--kind", "requirement", record=self.project_requirement())
        self.task("STUDIO", stage="studio")
        self.assertFalse(self.call("readiness", "--task", "STUDIO", expected=1)["ready"])
        self.reseal_package_records()
        for flags in [(), ("--require-accepted",)]:
            result = self.call("stage-check", "--package", self.project / "handoff", *flags, expected=2)
            self.assertIn("REQ-MULTI", result["error"])

    def test_accepted_package_must_include_current_closed_requirement(self):
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        self.call("resume")
        requirement = self.project_requirement(status="not_applicable", closure="Scoped fixture has no dependent feature")
        self.call("ledger", "--kind", "requirement", record=requirement)
        self.reseal_package_records()
        rejected = self.call("stage-check", "--package", self.project / "handoff", "--require-accepted", expected=2)
        self.assertIn("package omits", rejected["error"])
        rows = json.loads((self.project / "handoff/records/requirements.json").read_text())["items"]
        rows.append({"id": requirement["id"], "status": "not_applicable", "owner": requirement["owner"], "acceptance": requirement["acceptance"], "rationale": requirement["closure"]})
        self.reseal_package_records(requirements=rows)
        self.assertTrue(self.call("stage-check", "--package", self.project / "handoff", "--require-accepted")["valid"])

    def test_unrelated_scope_must_does_not_block_independent_stage_scope(self):
        self.test_after_stage_pause_uses_authoritative_accepted_pipeline_gate()
        self.call("resume")
        self.call("ledger", "--kind", "requirement", record=self.project_requirement(scope="unrelated-candidate"))
        self.task("STUDIO", stage="studio", scope="project")
        self.assertTrue(self.call("readiness", "--task", "STUDIO")["ready"])
        self.assertNotIn("REQ-MULTI", self.call("context", "--stage", "studio", "--scope", "project")["stage_context_snapshot"])
        self.assertTrue(self.call("stage-check", "--package", self.project / "handoff", "--require-accepted")["valid"])

    def test_requirement_stage_list_is_typed_and_definition_changes_invalidate(self):
        self.call("ledger", "--kind", "requirement", record=self.project_requirement(stages="studio"), expected=2)
        self.call("ledger", "--kind", "requirement", record=self.project_requirement(stages=["unknown"]), expected=2)
        first = self.call("ledger", "--kind", "requirement", record=self.project_requirement())
        self.task("TASK", stage="studio", fulfills_requirements=["REQ-MULTI"])
        second = self.call("ledger", "--kind", "requirement", record=self.project_requirement(stages=["studio"]))
        self.assertGreater(second["record"]["definition_revision"], first["record"]["definition_revision"])
        self.assertFalse(self.call("readiness", "--task", "TASK", expected=1)["ready"])

    def test_stale_na_requirement_does_not_bypass_readiness(self):
        self.artifact()
        self.call("ledger", "--kind", "requirement", record=self.project_requirement(status="not_applicable", closure="Original scoped reason", depends_on=["ART"]))
        self.task("STUDIO", stage="studio")
        self.call("readiness", "--task", "STUDIO")
        self.write("art.txt", "changed actual input")
        self.assertFalse(self.call("readiness", "--task", "STUDIO", expected=1)["ready"])

    def test_bounded_design_and_contract_reviews_do_not_choose_production(self):
        for operation in ("design_review", "contract_review"):
            intent = {"kind": "research", "stage": "qa", "scope": operation, "source": "Actual bounded review " + operation, "operation": operation}
            path = self.base / (operation + ".json")
            path.write_text(json.dumps(intent))
            route = self.call("route", "--intent", path)
            self.assertFalse(route["requires_production_choice"])
            task = self.task(operation, stage="qa", scope=operation, source=intent["source"], independent_review_required=True)["task"]
            self.assertEqual(task["work_class"], "review")
            self.assertFalse(task["requires_production_choice"])
            self.assertTrue(self.call("readiness", "--task", operation)["ready"])
            self.task(operation + "-wrong", stage="qa", scope=operation, source="Different source", operation=operation, expected=2)
        self.assertIsNone(self.state()["production_choice"])
        self.assertFalse(self.state()["search_stopped"])
        self.task("FULL-QA", stage="qa")
        self.assertFalse(self.call("readiness", "--task", "FULL-QA", expected=1)["ready"])
        self.task("FAKE-REVIEW", stage="build", operation="design_review", requires_production_choice=False, expected=2)
        self.task("REVIEW-EFFECT", stage="qa", operation="design_review", external_actions=["ACT"], expected=2)

    def test_shared_contract_lock_ignores_only_local_stage_delivery_and_pins_new_code(self):
        shared = self.bundle / "assets/suite-shared-paths.json"
        shared.write_text(json.dumps({"paths": ["scripts/atelier.py", "scripts/pipeline.py", "references/experience-contract.md", "assets/stage-catalog.json", "assets/suite-shared-paths.json"]}))
        self.call("refresh", "--accept-suite-update", "--authority", "Reviewed shared source declaration")
        self.task()
        local = self.bundle / "references/stage-only.md"
        local.write_text("Different stage entry guide; not a shared runtime contract")
        self.assertTrue(self.call("readiness", "--task", "TASK")["ready"])
        self.assertIn("references/stage-only.md", self.state()["observed_suite_sources"])
        local.write_text("Changed local stage guide remains explicitly observed")
        self.assertTrue(self.call("readiness", "--task", "TASK")["ready"])
        (self.bundle / "scripts/new-helper.py").write_text("# Any added executable code changes the lock")
        self.assertFalse(self.call("readiness", "--task", "TASK", expected=1)["ready"])

    def make_upgrade_target(self, source_version="4.2.0"):
        script = self.script.read_text()
        # This exact historical input is deliberate even after the production
        # TOOLKIT_VERSION is bumped; the migration tests retain a real4.2state.
        original = self.state()
        original["toolkit_version"] = source_version
        original.pop("snapshot_hash")
        original["snapshot_hash"] = hashlib.sha256(json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        (self.project / ".gameatelier/orchestrator/state.json").write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n")
        import re
        self.script.write_text(re.sub(r'^TOOLKIT_VERSION = "[0-9.]+"', 'TOOLKIT_VERSION = "5.0.0"', script, flags=re.M))

    def upgrade_apply(self, preview, **extra):
        return self.call("workflow-upgrade", "--apply", "--authority", "Actual reviewed workflow upgrade", "--expected-state-hash", preview["source_state_sha256"], "--target-suite-hash", preview["target_suite_sha256"], **extra)

    def test_workflow_upgrade_preserves_data_pause_effects_and_is_replay_safe(self):
        self.test_stop_search_and_production_choice_are_explicit_distinct_decisions()
        self.artifact()
        self.evidence()
        requirement = self.project_requirement(status="met", closure="Actual synthetic artifact observation", artifact_ids=["ART"], evidence_ids=["PROOF"])
        requirement.pop("stages")  # Real native4.2 token predates this optional extension.
        self.call("ledger", "--kind", "requirement", record=requirement)
        self.task("UNCHANGED", required_requirements=["REQ-MULTI"])
        self.call("pause", "--when", "now")
        before = self.state()
        before_bytes = (self.project / ".gameatelier/orchestrator/state.json").read_bytes()
        self.make_upgrade_target()
        before = self.state()
        before_bytes = (self.project / ".gameatelier/orchestrator/state.json").read_bytes()
        self.call("brief", expected=2, parse=False)
        preview = self.call("workflow-upgrade")
        self.assertTrue(preview["preview"])
        self.assertEqual((self.project / ".gameatelier/orchestrator/state.json").read_bytes(), before_bytes)
        self.assertFalse((self.project / ".gameatelier/orchestrator/backups").exists())
        result = self.upgrade_apply(preview)
        after = self.state()
        self.assertEqual(after["toolkit_version"], "5.0.0")
        for field in ("requirements", "decisions", "artifacts", "evidence", "actions", "favorites", "production_choice", "search_stopped", "pause", "seed_history", "stage_checks", "tasks"):
            self.assertEqual(after[field], before[field], field)
        self.assertEqual(after["journal"][:-1], before["journal"])
        self.assertEqual(after["journal"][-1]["command"], "workflow-upgrade")
        self.assertEqual((self.project / result["backup_path"]).read_bytes(), before_bytes)
        upgraded_bytes = (self.project / ".gameatelier/orchestrator/state.json").read_bytes()
        replay = self.upgrade_apply(preview)
        self.assertTrue(replay["replayed"])
        self.assertEqual((self.project / ".gameatelier/orchestrator/state.json").read_bytes(), upgraded_bytes)
        self.assertTrue(self.state()["pause"]["active"])

    def test_workflow_upgrade_from_4_3_preserves_project_identity(self):
        original_id = self.state()["project_id"]
        self.make_upgrade_target(source_version="4.3.0")
        preview = self.call("workflow-upgrade")
        self.assertEqual(preview["from_toolkit"], "4.3.0")
        self.assertEqual(preview["to_toolkit"], "5.0.0")
        self.upgrade_apply(preview)
        self.assertEqual(self.state()["project_id"], original_id)
        self.assertEqual(self.state()["toolkit_version"], "5.0.0")

    def test_workflow_upgrade_rejects_stale_state_target_corruption_and_unknown_versions(self):
        self.make_upgrade_target()
        preview = self.call("workflow-upgrade")
        # A delivery change, even if not a runtime-contract change, invalidates
        # the reviewed target binding and requires a fresh read-only preview.
        (self.bundle / "references/extra.md").write_text("New target instructions")
        self.assertIn("target suite changed", self.upgrade_apply(preview, expected=2)["error"])
        preview = self.call("workflow-upgrade")
        home = self.project / ".gameatelier/orchestrator"
        old = json.loads((home / "state.json").read_text())
        # Whitespace is also an exact-byte source change, not permission to use
        # an old expected-state binding.
        (home / "state.json").write_text(json.dumps(old))
        self.assertIn("state changed", self.upgrade_apply(preview, expected=2)["error"])
        corrupt = self.state()
        corrupt["production_choice"] = "forged"
        (home / "state.json").write_text(json.dumps(corrupt))
        self.assertIn("snapshot integrity", self.call("workflow-upgrade", expected=2)["error"])

    def test_workflow_upgrade_marks_only_reviewed_dependencies_and_keeps_effects_unreplayed(self):
        self.task("A")
        self.task("B", depends_on=["A"])
        self.task("INDEPENDENT")
        self.make_upgrade_target()
        preview = self.call("workflow-upgrade", "--impact", "A")
        result = self.call("workflow-upgrade", "--apply", "--authority", "Reviewed impact A", "--expected-state-hash", preview["source_state_sha256"], "--target-suite-hash", preview["target_suite_sha256"], "--impact", "A")
        self.assertEqual(set(result["affected_ids"]), {"A", "B"})
        state = self.state()
        self.assertEqual(state["tasks"]["A"]["status"], "stale")
        # A planned dependent is not started; the stale reason and readiness
        # dependency block it without manufacturing a completed status.
        self.assertIn("reviewed workflow upgrade affected dependency", state["tasks"]["B"]["stale_reasons"])
        self.assertEqual(state["tasks"]["INDEPENDENT"]["status"], "planned")
        self.assertEqual(result["external_actions_executed"], [])


    def test_workflow_upgrade_preserves_pending_effect_and_requires_bound_authority(self):
        self.artifact(scope="publish-scope")
        self.decision(scope="publish-scope", approval={"option": "yes", "effects": ["upload"], "artifact_ids": ["ART"]})
        self.confirm(scope="publish-scope")
        self.call("capability", record={"id": "CAP", "source": "observed synthetic fixture", "available": True, "scope": "publish-scope", "environment": "fixture-only", "verified_at": "2026-11-04"})
        self.task(stage="liveops", scope="publish-scope", required_decisions=["DEC"])
        self.call("start", "--task", "TASK")
        self.call("action", record={"id": "ACT", "idempotency_key": "synthetic-pending-effect", "type": "upload", "scope": "publish-scope", "source": "Actual fixture instruction", "decision_id": "DEC", "decision_revision": 1, "capability_id": "CAP", "environment": "fixture-only", "prepared_artifact_ids": ["ART"], "task": "TASK"})
        self.call("dispatch", "--id", "ACT", "--project-revision", self.state()["revision"])
        self.assertEqual(self.state()["actions"]["ACT"]["status"], "pending")
        original_action = self.state()["actions"]["ACT"]
        self.make_upgrade_target()
        preview = self.call("workflow-upgrade")
        self.assertEqual(preview["unresolved_external_actions"], ["ACT"])
        self.call("workflow-upgrade", "--apply", "--expected-state-hash", preview["source_state_sha256"], "--target-suite-hash", preview["target_suite_sha256"], expected=2)
        self.assertFalse((self.project / ".gameatelier/orchestrator/backups").exists())
        result = self.upgrade_apply(preview)
        self.assertEqual(result["external_actions_executed"], [])
        self.assertEqual(self.state()["actions"]["ACT"], original_action)
        self.assertFalse(self.call("resume", expected=1)["ready"])

    def test_workflow_upgrade_rejects_unrelated_version_and_old_schema_without_mutating(self):
        self.make_upgrade_target()
        path = self.project / ".gameatelier/orchestrator/state.json"
        for field,value,error in [("toolkit_version", "2.0.0", "unsupported toolkit"), ("schema_version", "previous-state", "unsupported runtime schema")]:
            current = self.state()
            current[field] = value
            current.pop("snapshot_hash")
            current["snapshot_hash"] = hashlib.sha256(json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            path.write_text(json.dumps(current))
            before = path.read_bytes()
            result = self.call("workflow-upgrade", expected=2)
            self.assertIn(error, result["error"])
            self.assertEqual(path.read_bytes(), before)
            current[field] = "4.2.0" if field == "toolkit_version" else "2.0.0"
            current.pop("snapshot_hash")
            current["snapshot_hash"] = hashlib.sha256(json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            path.write_text(json.dumps(current))


    def test_native_requirement_fingerprint_is_stable_without_new_stage_extension(self):
        import types
        runtime = types.ModuleType("atelier_native_token_check")
        runtime.__file__ = str(self.script)
        exec(compile(self.script.read_bytes(), str(self.script), "exec"), runtime.__dict__)
        row = self.project_requirement(record_type="requirement", definition_revision=1)
        row.pop("stages")
        native_definition = {key: row.get(key) for key in ("id", "definition_revision", "source", "verbatim_source", "intent", "stage", "scope", "owner", "priority", "acceptance", "depends_on")}
        self.assertEqual(runtime.token(row), runtime.digest(native_definition))
        extended = {**row, "stages": ["studio", "concepts"]}
        self.assertNotEqual(runtime.token(extended), runtime.token(row))


    def test_completion_rejects_literal_wrong_scope_and_wrong_stage_proof(self):
        self.task(stage="concepts", scope="candidate-a", artifact_ids=["ART"], required_modalities=["document"])
        self.call("start", "--task", "TASK")
        self.artifact(scope="candidate-a")
        bad_scope = self.evidence("WRONG-SCOPE", stage="studio", scope="candidate-b", expected=2)
        self.assertIn("scope contradicts", bad_scope["error"])
        self.evidence("WRONG-STAGE", stage="studio", scope="candidate-a")
        rejected = self.call("complete", "--task", "TASK", "--evidence", "WRONG-STAGE", expected=2)
        self.assertIn("task stage/scope", rejected["error"])
        self.assertEqual(self.state()["tasks"]["TASK"]["status"], "running")

    def test_explicit_multistage_project_evidence_can_close_scoped_task(self):
        self.task(stage="concepts", scope="candidate-a", artifact_ids=["ART"], required_modalities=["document"], independent_review_required=True)
        self.call("start", "--task", "TASK")
        self.artifact(scope="candidate-a")
        self.evidence("SHARED", stage="qa", stages=["qa", "concepts"], scope="project")
        result = self.call("complete", "--task", "TASK", "--evidence", "SHARED")
        self.assertEqual(result["completed"], "TASK")

    def test_requirement_closure_needs_matching_proof_applicability(self):
        self.artifact(scope="candidate-a")
        self.evidence("STUDIO", stage="studio", scope="candidate-a")
        requirement = self.project_requirement(stage="concepts", stages=["concepts"], scope="candidate-a", status="met", closure="Synthetic reviewed result", artifact_ids=["ART"], evidence_ids=["STUDIO"])
        result = self.call("ledger", "--kind", "requirement", record=requirement, expected=2)
        self.assertIn("declared stages/scope", result["error"])
        self.evidence("SHARED", stage="qa", stages=["concepts", "qa"], scope="project")
        requirement["evidence_ids"] = ["SHARED"]
        self.call("ledger", "--kind", "requirement", record=requirement)
        other = {**requirement, "id": "OTHER", "scope": "candidate-b"}
        self.call("ledger", "--kind", "requirement", record=other, expected=2)

    def test_primary_stage_cannot_be_removed_by_applicability_extension(self):
        import types
        runtime = types.ModuleType("atelier_stage_union_check")
        runtime.__file__ = str(self.script)
        exec(compile(self.script.read_bytes(), str(self.script), "exec"), runtime.__dict__)
        requirement = self.project_requirement(stage="concepts", stages=["studio"])
        self.assertTrue(runtime.applicable(requirement, "concepts", "project"))
        self.assertTrue(runtime.applicable(requirement, "studio", "project"))


    def linked_sibling_decisions(self):
        path = self.project / ".gameatelier/decisions.json"
        data = {"schema_version": "canonical-decision-fixture/1", "items": [{"id": "DA", "status": "confirmed", "answer": "yes", "scope": "candidate-a", "authority_ref": "Actual A approval"}, {"id": "DB", "status": "confirmed", "answer": "yes", "scope": "candidate-b", "authority_ref": "Actual B approval"}]}
        path.write_text(json.dumps(data))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for ident,scope in (("DA", "candidate-a"), ("DB", "candidate-b")):
            self.decision(ident, scope=scope, canonical_ref=".gameatelier/decisions.json#"+ident, canonical_sha256=digest)
        self.task("TB", scope="candidate-b", required_decisions=["DB"], depends_on=["DB"], artifact_ids=["ART"])
        self.call("start", "--task", "TB")
        self.artifact(scope="candidate-b")
        self.evidence(scope="candidate-b")
        self.call("complete", "--task", "TB", "--evidence", "PROOF")
        return path,data

    def test_canonical_sibling_edit_preserves_unrelated_decision_and_completed_task(self):
        path,data=self.linked_sibling_decisions()
        before=self.state()
        data["items"][0]["answer"]="no"
        path.write_text(json.dumps(data))
        self.call("refresh")
        after=self.state()
        self.assertEqual(after["decisions"]["DA"]["status"], "stale")
        self.assertEqual(after["decisions"]["DB"]["status"], "confirmed")
        self.assertEqual(after["decisions"]["DB"]["canonical_sha256"], before["decisions"]["DB"]["canonical_sha256"])
        self.assertEqual(after["decisions"]["DB"]["canonical_observed_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(after["tasks"]["TB"]["status"], "completed")
        self.assertEqual(after["tasks"]["TB"]["completion_snapshot"], before["tasks"]["TB"]["completion_snapshot"])

    def test_canonical_global_envelope_and_unknown_fields_still_invalidate(self):
        path,data=self.linked_sibling_decisions()
        data["schema_version"]="changed-global-policy/2"
        path.write_text(json.dumps(data))
        self.call("refresh")
        self.assertEqual(self.state()["decisions"]["DB"]["status"], "stale")
        self.assertEqual(self.state()["tasks"]["TB"]["status"], "stale")

    def test_canonical_declared_dependency_is_inherited_and_invalidated(self):
        path = self.project / ".gameatelier/decisions.json"
        data={"items":[{"id":"DA", "status":"confirmed", "answer":"yes", "scope":"candidate-a", "authority_ref":"Actual A approval"}, {"id":"DB", "status":"confirmed", "answer":"yes", "scope":"candidate-b", "authority_ref":"Actual B approval", "depends_on":["DA"]}]}
        path.write_text(json.dumps(data)); source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
        self.decision("DA", scope="candidate-a", canonical_ref=".gameatelier/decisions.json#DA", canonical_sha256=source_hash)
        self.decision("DB", scope="candidate-b", canonical_ref=".gameatelier/decisions.json#DB", canonical_sha256=source_hash)
        self.assertEqual(self.state()["decisions"]["DB"]["depends_on"], ["DA"])
        data["items"][0]["answer"]="no";path.write_text(json.dumps(data))
        self.call("refresh")
        self.assertEqual(self.state()["decisions"]["DB"]["status"], "stale")

    def test_old_canonical_binding_without_fragment_pins_requires_reconciliation(self):
        path,data=self.linked_sibling_decisions()
        home=self.project/".gameatelier/orchestrator"
        state=self.state()
        for key in ("canonical_record_sha256", "canonical_envelope_sha256", "canonical_observed_sha256"):
            state["decisions"]["DB"].pop(key)
        state.pop("snapshot_hash")
        state["snapshot_hash"]=hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        (home/"state.json").write_text(json.dumps(state))
        data["items"][0]["answer"]="no";path.write_text(json.dumps(data))
        self.call("refresh")
        self.assertEqual(self.state()["decisions"]["DB"]["status"], "stale")
        self.assertIn("lacks pins", self.state()["decisions"]["DB"]["stale_reasons"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
