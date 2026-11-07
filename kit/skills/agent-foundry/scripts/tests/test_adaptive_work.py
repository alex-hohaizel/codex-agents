"""Behavioral checks for bytes, scope declarations, recovery and cooperative CAS."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "adaptive_work.py"
spec = importlib.util.spec_from_file_location("adaptive_work", MODULE)
aw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aw)


class AdaptiveWorkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs/raw-request.txt").write_text("Repair the stated defect within current scope.\n")
        self.doc = json.loads((MODULE.parent.parent / "assets/adaptive-task.example.json").read_text())
        self.doc["sources"][0]["sha256"] = aw.digest(self.root / "docs/raw-request.txt")

    def check(self, doc=None):
        return aw.validate(doc or self.doc, self.root)

    def assertInvalid(self, fragment, doc=None):
        result = self.check(doc)
        self.assertFalse(result["valid"], result)
        self.assertTrue(any(fragment in e for e in result["errors"]), result)
        return result

    def produced(self):
        (self.root / "docs/result.txt").write_text("The actual resulting artifact\n")
        (self.root / "docs/review.txt").write_text("Observed the relevant assertion in the stated fixture\n")
        out = self.doc["outputs"][0]
        out.update(status="accepted", path="docs/result.txt", sha256=aw.digest(self.root / "docs/result.txt"), evidence_ids=["EV-1"])
        self.doc["evidence"] = [{"id":"EV-1", "kind":"semantic", "observer":"independent-actor", "result":"pass", "output_ids":["OUT-1"], "subjects":[{"output_id":"OUT-1", "sha256":out["sha256"]}], "limitations":"Synthetic fixture only", "path":"docs/review.txt", "sha256":aw.digest(self.root / "docs/review.txt")}]

    def route(self):
        self.doc["authority"]["route"] = {"basis":"unique_verified", "chosen":"mac", "options":[{"id":"mac", "destination":"existing-project-codex", "available":True, "allowed":True, "identity_verified":True, "proof_source_ids":["SRC-1"]}], "state":"prepared", "receipt_evidence_ids":[]}
        return self.doc["authority"]["route"]

    def test_local_fast_path_is_valid_without_heavy_review(self):
        r = self.check()
        self.assertTrue(r["valid"], r)
        self.assertFalse(r["quality_certified"])
        self.assertFalse(r["native_gate_checked"])
        self.assertFalse(r["execution_observed"])

    def test_stale_raw_source_rejected(self):
        (self.root / "docs/raw-request.txt").write_text("The user changed scope")
        self.assertInvalid("stale SHA-256")

    def test_unsafe_and_missing_paths_rejected(self):
        for path in ("../outside", "/absolute", "docs/../result", "docs\\result", "C:/file", "docs/missing"):
            with self.subTest(path=path):
                d = copy.deepcopy(self.doc); d["sources"][0]["path"] = path
                self.assertFalse(self.check(d)["valid"])

    def test_symlink_source_rejected_even_inside_root(self):
        (self.root / "docs/link.txt").symlink_to(self.root / "docs/raw-request.txt")
        self.doc["sources"][0]["path"] = "docs/link.txt"
        self.assertInvalid("symlink")

    def test_unmapped_declared_obligation_source_rejected(self):
        src = copy.deepcopy(self.doc["sources"][0]); src["id"] = "SRC-2"
        self.doc["sources"].append(src)
        self.assertInvalid("no declared obligation mapping")

    def test_example_source_does_not_require_new_product_obligation(self):
        src = copy.deepcopy(self.doc["sources"][0]); src.update(id="EXAMPLE-1", kind="example")
        self.doc["sources"].append(src)
        self.assertTrue(self.check()["valid"])

    def test_deferred_result_must_keep_due_and_disposition(self):
        self.doc["obligations"][0].update(status="deferred", output_ids=[])
        self.assertInvalid("disposition")
        self.doc["obligations"][0]["disposition"] = "Due after the recorded prerequisite; remains in scope"
        self.assertTrue(self.check()["valid"])
        del self.doc["obligations"][0]["due"]
        self.assertInvalid("due")

    def test_reviewed_output_requires_current_bytes_and_receipt(self):
        self.doc["outputs"][0]["status"] = "accepted"
        self.assertInvalid("exact path/hash")
        self.produced()
        self.assertTrue(self.check()["valid"])
        (self.root / "docs/result.txt").write_text("Changed after review")
        self.assertInvalid("stale SHA-256")

    def test_refreshing_output_hash_cannot_reuse_old_accepted_evidence(self):
        self.produced()
        self.doc["task"]["status"] = "accepted"
        self.assertTrue(self.check()["valid"])
        old_evidence = copy.deepcopy(self.doc["evidence"][0])
        evidence_bytes = (self.root / "docs/review.txt").read_bytes()
        (self.root / "docs/result.txt").write_text("A materially different result after acceptance\n")
        # The current artifact snapshot is refreshed, but no new observation occurred.
        self.doc["outputs"][0]["sha256"] = aw.digest(self.root / "docs/result.txt")
        self.assertInvalid("stale immutable subject SHA-256")
        self.assertEqual(self.doc["evidence"][0], old_evidence)
        self.assertEqual((self.root / "docs/review.txt").read_bytes(), evidence_bytes)

    def test_actual_output_evidence_cannot_drop_subject_binding(self):
        self.produced(); self.doc["evidence"][0]["subjects"] = []
        self.assertInvalid("actual output requires immutable subject")

    def test_evidence_must_bind_the_reviewed_output_both_directions(self):
        self.produced(); self.doc["evidence"][0]["output_ids"] = []
        self.assertInvalid("at least one record")

    def test_critical_observation_not_same_author(self):
        self.produced(); self.doc["assessment"]["consequence"] = "critical"
        self.doc["evidence"][0]["observer"] = self.doc["outputs"][0]["author"]
        self.assertInvalid("another declared observer")

    def test_unknown_effect_blocks_retry_and_acceptance(self):
        self.doc["effects"] = [{"id":"FX-1", "destination":"exact-provider-operation", "state":"unknown", "grant_source_ids":["SRC-1"], "evidence_ids":[], "retry_requested":True}]
        self.assertInvalid("cannot retry")
        self.doc["effects"][0]["retry_requested"] = False
        self.assertTrue(self.check()["valid"])
        self.doc["task"]["status"] = "accepted"
        self.assertInvalid("unknown external effects")

    def test_untrusted_document_is_not_grant(self):
        self.doc["sources"][0]["authority"] = "untrusted"
        self.assertInvalid("not a grant")

    def test_illustrative_example_cannot_be_an_action_grant(self):
        self.doc["sources"][0]["kind"] = "example"
        self.assertInvalid("example/evidence is not itself a grant")

    def test_unique_route_rejects_hidden_material_alternative(self):
        route = self.route()
        self.assertTrue(self.check()["valid"])
        option = copy.deepcopy(route["options"][0]); option["id"] = "other"
        route["options"].append(option)
        self.assertInvalid("exactly one eligible")
        route["basis"] = "owner_chosen"
        route["grant_source_ids"] = ["SRC-1"]
        self.assertTrue(self.check()["valid"])

    def test_delivery_and_start_need_receipt(self):
        route = self.route(); route["state"] = "started"
        self.assertInvalid("bound receipt")

    def test_unresolved_route_cannot_claim_delivery(self):
        route = self.route(); route.update(basis="unresolved", state="delivered")
        self.assertInvalid("unresolved choice")

    def test_owner_action_has_concrete_place_and_success(self):
        self.doc["next"]["requires_user"] = True
        self.assertInvalid("next.where")
        self.doc["next"].update(where="Existing project chat", instruction="Insert the filled handoff", success_signal="Receipt with the exact task/revision", return_to="This task in the same project")
        self.assertTrue(self.check()["valid"])

    def test_create_and_cas_preserve_other_writer(self):
        result = aw.create(self.doc, self.root, "docs/task.json")
        self.assertTrue(result["saved"])
        original = (self.root / "docs/task.json").read_bytes()
        with self.assertRaisesRegex(aw.Invalid, "overwrite lacks"):
            aw.create(self.doc, self.root, "docs/task.json")
        changed = copy.deepcopy(self.doc); changed["task"]["revision"] = 2
        second = aw.create(changed, self.root, "docs/task.json", result["sha256"])
        self.assertTrue(second["saved"])
        with self.assertRaisesRegex(aw.Invalid, "changed"):
            aw.create(changed, self.root, "docs/task.json", result["sha256"])
        self.assertNotEqual(original, (self.root / "docs/task.json").read_bytes())
        self.assertEqual(json.loads((self.root / "docs/task.json").read_text())["task"]["revision"], 2)

    def test_lock_requires_reconciliation_not_blind_takeover(self):
        (self.root / "docs/task.json.lock").write_text("Existing writer or interrupted outcome")
        with self.assertRaisesRegex(aw.Invalid, "writer lock exists"):
            aw.create(self.doc, self.root, "docs/task.json")
        self.assertFalse((self.root / "docs/task.json").exists())
        self.assertTrue((self.root / "docs/task.json.lock").exists())

    def test_cas_cannot_change_project_or_skip_revision(self):
        result = aw.create(self.doc, self.root, "docs/task.json")
        changed = copy.deepcopy(self.doc); changed["task"]["revision"] = 3
        with self.assertRaisesRegex(aw.Invalid, "next task revision"):
            aw.create(changed, self.root, "docs/task.json", result["sha256"])
        changed["task"]["revision"] = 2; changed["project"]["id"] = "other-project"
        with self.assertRaisesRegex(aw.Invalid, "another project/task"):
            aw.create(changed, self.root, "docs/task.json", result["sha256"])

    def test_registration_needs_actual_canonical_reference(self):
        registry = self.root / "docs/native-state.json"
        registry.write_text('{"artifacts": []}')
        self.doc["project"]["registry_path"] = "docs/native-state.json"
        self.doc["registration"] = {"state":"pending"}
        result = aw.create(self.doc, self.root, "docs/task.json")
        self.assertTrue(result["valid"]); self.assertFalse(result["artifact_registered"])
        path = self.root / "docs/task.json"
        self.doc["registration"] = {"state":"registered", "registry_path":"docs/native-state.json", "entry_pointer":"/artifacts/0"}
        path.write_text(json.dumps(self.doc))
        self.assertFalse(aw.validate(self.doc, self.root, path)["artifact_registered"])
        registry.write_text(json.dumps({"artifacts":[{"path":"docs/task.json", "sha256":aw.digest(path)}]}))
        verdict = aw.validate(self.doc, self.root, path)
        self.assertTrue(verdict["valid"], verdict)
        self.assertTrue(verdict["artifact_registered"])
        self.assertFalse(verdict["native_gate_checked"])
        self.assertFalse(verdict["quality_certified"])

    def test_deep_accepted_scope_requires_raw_source_review(self):
        self.produced(); self.doc["assessment"]["depth"] = "deep"
        self.doc["task"]["status"] = "accepted"
        self.assertInvalid("raw-source reviewer")
        self.doc["review"] = {"state":"complete", "actor":"other-actor", "source_ids":["SRC-1"], "source_bindings":[{"source_id":"SRC-1", "sha256":self.doc["sources"][0]["sha256"]}], "raw_sources_reviewed":True, "findings":[]}
        self.assertTrue(self.check()["valid"])
        self.doc["review"]["actor"] = self.doc["task"]["owner"]
        self.assertInvalid("raw-source reviewer")

    def test_complete_review_cannot_omit_declared_user_example(self):
        src = copy.deepcopy(self.doc["sources"][0]); src.update(id="EXAMPLE-1", kind="example")
        self.doc["sources"].append(src)
        self.doc["review"] = {"state":"complete", "actor":"other-actor", "source_ids":["SRC-1"], "source_bindings":[{"source_id":"SRC-1", "sha256":self.doc["sources"][0]["sha256"]}], "raw_sources_reviewed":True, "findings":[]}
        self.assertInvalid("all declared primary")
        self.doc["review"]["source_ids"].append("EXAMPLE-1")
        self.doc["review"]["source_bindings"].append({"source_id":"EXAMPLE-1", "sha256":src["sha256"]})
        self.assertTrue(self.check()["valid"])

    def test_refreshing_source_hash_invalidates_completed_raw_source_review(self):
        self.produced(); self.doc["assessment"]["depth"] = "deep"
        self.doc["task"]["status"] = "accepted"
        self.doc["review"] = {"state":"complete", "actor":"other-actor", "source_ids":["SRC-1"], "source_bindings":[{"source_id":"SRC-1", "sha256":self.doc["sources"][0]["sha256"]}], "raw_sources_reviewed":True, "findings":[]}
        self.assertTrue(self.check()["valid"])
        old_review = copy.deepcopy(self.doc["review"])
        (self.root / "docs/raw-request.txt").write_text("Changed requirement and a new material constraint\n")
        # Updating current source bytes/hash cannot transfer the old review to them.
        self.doc["sources"][0]["sha256"] = aw.digest(self.root / "docs/raw-request.txt")
        self.assertInvalid("stale immutable source SHA-256")
        self.assertEqual(self.doc["review"], old_review)

    def test_completed_review_cannot_drop_immutable_source_snapshot(self):
        self.doc["review"] = {"state":"complete", "actor":"other-actor", "source_ids":["SRC-1"], "source_bindings":[], "raw_sources_reviewed":True, "findings":[]}
        self.assertInvalid("immutable hashes for every reviewed source")

    def test_json_duplicate_keys_not_silently_overwritten(self):
        p = self.root / "duplicate.json"; p.write_text('{"scope":"first","scope":"second"}')
        with self.assertRaisesRegex(aw.Invalid, "duplicate JSON key"):
            aw.read_json(p)

    def test_malformed_root_is_validation_failure_without_write(self):
        result = aw.create([], self.root, "docs/task.json")
        self.assertFalse(result["valid"])
        self.assertFalse((self.root / "docs/task.json").exists())

    def test_render_reports_limitations_and_next_action(self):
        text = aw.render(self.doc, self.check())
        self.assertIn("Наступний крок", text)
        self.assertIn("не сертифікуються", text)

    def test_cli_create_then_read_only_views_and_malformed_status(self):
        source = self.root / "input.json"
        source.write_text(json.dumps(self.doc))
        command = [sys.executable, "-B", str(MODULE)]
        p = subprocess.run(command + ["create", "--project-root", str(self.root), "--input", str(source), "--output", "docs/task.json"], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        task = self.root / "docs/task.json"
        before = task.read_bytes()
        for op in ("validate", "render", "status"):
            p = subprocess.run(command + [op, "--project-root", str(self.root), "--task", "docs/task.json"], text=True, capture_output=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertEqual(task.read_bytes(), before)
        malformed = copy.deepcopy(self.doc); malformed["effects"] = 42
        task.write_text(json.dumps(malformed))
        p = subprocess.run(command + ["status", "--project-root", str(self.root), "--task", "docs/task.json"], text=True, capture_output=True)
        self.assertEqual(p.returncode, 1)
        self.assertFalse(json.loads(p.stdout)["valid"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
