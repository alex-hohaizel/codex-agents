"""Production choice stage and provenance regression checks."""

from datetime import timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fixture_production_choices import current_pin, make_choice, put
from production_choices import ChoiceError, decision_subject, utc_today, verify_project


CLI = Path(__file__).resolve().parents[2] / "standards/production_choices.py"


class ProductionChoicesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.record = "production-choices.json"

    def load(self):
        return json.loads((self.root / self.record).read_bytes())

    def save(self, value):
        return put(self.root, self.record, value)

    def test_experiment_allows_open_choice_but_cannot_implement(self):
        report = make_choice(self.root, phase="explore")
        self.assertTrue(report["ok"])
        self.assertIsNone(report["decision_sha256"])
        with self.assertRaisesRegex(ChoiceError, "production decision"):
            verify_project(self.root, "implement")

    def test_material_experiment_requires_a_candidate_and_bound_procedure(self):
        make_choice(self.root, phase="explore")
        value = self.load()
        experiment = value.pop("experiment")
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "experiment"):
            verify_project(self.root, "explore")
        value["experiment"] = dict(experiment, candidate_id="hosted")
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "declared feasible candidate"):
            verify_project(self.root, "explore")
        value["experiment"] = experiment
        self.save(value)
        self.assertTrue(verify_project(self.root, "explore")["ok"])
        (self.root / experiment["procedure"]["path"]).write_text("Changed experiment procedure")
        with self.assertRaisesRegex(ChoiceError, "stale exploration procedure"):
            verify_project(self.root, "explore")

    def test_acceptance_binds_approved_variants_and_actual_stage_receipts(self):
        report = make_choice(self.root, target_kind="web", phase="accept")
        self.assertEqual(report["decision_sha256"], decision_subject(self.root))
        self.assertEqual(report["decision_sha256"],
                         verify_project(self.root, "implement")["decision_sha256"])
        self.assertEqual(report["master_count"], 1)
        self.assertEqual(report["flow_count"], 1)
        self.assertEqual(set(report["evidence_artifacts"]), {"scale", "accept"})
        self.assertFalse(report["authority_authenticated"])
        self.assertFalse(report["runtime_authenticated"])
        self.assertFalse(report["craft_certified"])

    def test_unavailable_hard_constraint_cannot_be_averaged(self):
        make_choice(self.root)
        value = self.load()
        value["candidates"][0]["checks"]["R1"] = "unknown"
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "failed or unknown hard requirements"):
            verify_project(self.root, "implement")

    def test_changed_technology_does_not_inherit_approval(self):
        make_choice(self.root)
        value = self.load()
        value["candidates"][0]["components"][0]["version"] = "RFC 8785"
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "different decision revision"):
            verify_project(self.root, "implement")

    def test_protected_master_and_flow_reject_changed_bytes(self):
        for keyword in ("masters", "flows"):
            with self.subTest(keyword=keyword):
                make_choice(self.root, target_kind="web", phase="accept")
                relative = self.load()["decision"][keyword][0]["path"]
                (self.root / relative).write_text("Replaced without decision", encoding="utf-8")
                with self.assertRaisesRegex(ChoiceError, "stale approved (master|flow)"):
                    verify_project(self.root, "accept")

    def test_target_specific_requirements_cannot_use_another_domain_record(self):
        make_choice(self.root, target_kind="script")
        with self.assertRaisesRegex(ChoiceError, "target kind must be web"):
            verify_project(self.root, "implement", required_kind="web")
        value = self.load()
        value["target_kind"] = "web"
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "approved master"):
            decision_subject(self.root)

    def test_mismatched_exact_record_fails_before_stage_validation(self):
        report = make_choice(self.root)
        original = report["record_sha256"]
        with (self.root / self.record).open("ab") as handle:
            handle.write(b" ")
        with self.assertRaisesRegex(ChoiceError, "previously inspected bytes"):
            verify_project(self.root, "implement", expected_sha256=original)

    def test_expired_decision_and_source_are_distinguished(self):
        make_choice(self.root)
        value = self.load()
        value["decision"]["review_by"] = (utc_today() - timedelta(days=1)).isoformat()
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "decision review is overdue"):
            verify_project(self.root, "implement")
        make_choice(self.root)
        value = self.load()
        source = value["candidates"][0]["sources"][0]
        source["checked_on"] = (utc_today() - timedelta(days=3)).isoformat()
        source["review_by"] = (utc_today() - timedelta(days=1)).isoformat()
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "candidate source review is overdue"):
            verify_project(self.root, "implement")

    def test_metadata_review_does_not_substitute_for_observation_or_independence(self):
        for key, replacement, message in (
            ("reviewer", " Fixture-Author ", "distinct reviewer"),
            ("method", "screenshot", "actual consumer method"),
            ("decision_sha256", "0" * 64, "stale evidence decision"),
        ):
            with self.subTest(key=key):
                make_choice(self.root, target_kind="web", phase="scale")
                value = self.load()
                value["evidence"][0][key] = replacement
                self.save(value)
                with self.assertRaisesRegex(ChoiceError, message):
                    verify_project(self.root, "scale")

    def test_stage_checks_missing_negative_and_failed_observation(self):
        make_choice(self.root, phase="scale")
        value = self.load()
        controls = value["evidence"][0]["controls"]
        negative = controls.pop()
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "positive and negative controls"):
            verify_project(self.root, "scale")
        negative["outcome"] = "fail"
        controls.append(negative)
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "failed control"):
            verify_project(self.root, "scale")

    def test_first_slice_cannot_be_reused_as_final_acceptance(self):
        make_choice(self.root, phase="scale")
        with self.assertRaisesRegex(ChoiceError, "required evidence missing for: accept"):
            verify_project(self.root, "accept")

    def test_changed_consumer_output_invalidates_later_acceptance(self):
        make_choice(self.root, phase="accept")
        relative = self.load()["evidence"][1]["artifacts"][0]["path"]
        (self.root / relative).write_text("New artifact bytes\n", encoding="utf-8")
        with self.assertRaisesRegex(ChoiceError, "stale observed artifact"):
            verify_project(self.root, "accept")

    def test_refuse_paths_outside_scope_and_vendor_secrets(self):
        make_choice(self.root, phase="explore")
        secret = self.root / ".env"
        secret.write_bytes(b"PRIVATE=fixture\n")
        value = self.load()
        for relative in (".env", "../other.txt", "/data.txt", "C:/data.txt", "docs//data.txt"):
            with self.subTest(relative=relative):
                value["requirements"][0]["source"] = {
                    "path": relative, "sha256": hashlib.sha256(secret.read_bytes()).hexdigest(),
                }
                self.save(value)
                with self.assertRaisesRegex(ChoiceError, "unsafe or protected"):
                    verify_project(self.root, "explore")

    def test_refuse_symlink_parent_even_if_target_is_inside_project(self):
        make_choice(self.root, phase="explore")
        try:
            (self.root / "alias").symlink_to(self.root / "_choice-fixture", target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("symlink creation unavailable on this host")
        value = self.load()
        value["requirements"][0]["source"] = current_pin(self.root, "alias/requirement.md")
        self.save(value)
        with self.assertRaisesRegex(ChoiceError, "linked or invalid parent"):
            verify_project(self.root, "explore")

    def test_cli_rejects_duplicate_record_keys_and_returns_nonzero_json(self):
        (self.root / self.record).write_bytes(b'{"schema": "one", "schema": "two"}')
        output = subprocess.run(
            [sys.executable, "-B", str(CLI), "verify", str(self.root), "--phase", "explore"],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(output.returncode, 1)
        self.assertEqual(json.loads(output.stdout),
                         {"ok": False, "error": "duplicate JSON object key"})


if __name__ == "__main__":
    unittest.main()
