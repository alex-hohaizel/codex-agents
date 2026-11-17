"""Check Builder admission over an applied, exact replan."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_handoff as handoff
import ticket_replan_plan as model
import ticket_replan_store as store

context = handoff.context


class BuilderHandoffTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name).resolve()
        (self.root / "review").mkdir()
        (self.root / "export.py").write_text("def export(): return 'v1'\n")
        (self.root / "review/architecture.md").write_text("Use one serializer for both export routes.\n")
        self.save("requirements.json", {"requirements": [
            {"id": "R-CSV", "text": "Exports use the four current columns."},
        ]})
        self.save("tickets.json", {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "exports", "native_revision": "r1",
            "requirement_sources": [self.pin("requirements.json")],
            "tickets": [{"id": "I", "kind": "initiative", "title": "Delivery", "status": "planned"}],
        })
        self.command("git", "init", "-q", "--template=")
        self.command("git", "add", "tickets.json", "requirements.json", "export.py")
        self.command("git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                     "commit", "-qm", "initial files")
        self.save("review/request.json", {
            "schema_version": model.REQUEST,
            "project_id": "exports", "native_revision": "r1",
            "target_revision": "r2", "projection_sha256": self.pin("tickets.json")["sha256"],
            "changes": [{
                "action": "create", "rationale": "Rework CSV to match current requirements.",
                "sources": [{**self.pin("requirements.json"), "requirement_id": "R-CSV",
                             "excerpt": "Exports use the four current columns."},
                            {**self.pin("review/architecture.md"),
                             "excerpt": "Use one serializer for both export routes."}],
                "ticket": {"id": "T-CSV", "title": "Export revised columns", "kind": "story",
                           "parent": "I", "requirement_ids": ["R-CSV"], "acceptance": "Exact header"},
            }],
        })
        plan = model.build_plan(self.root, "tickets.json", "review/request.json")
        self.plan_sha = store.plan_sha256(plan)
        self.save("review/approval.json", {
            "schema_version": store.DECISION,
            "decision": "approve", "operation_id": "fixture-op", "authority_ref": "Fixture owner",
            **{field: plan[field] for field in store.BINDING}, "plan_sha256": self.plan_sha,
        })
        store.apply_plan(self.root, "tickets.json", "review/request.json", "review/approval.json",
                         self.pin("review/approval.json")["sha256"])

    def save(self, path, value):
        (self.root / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def pin(self, ref):
        return {"path": ref, "sha256": hashlib.sha256((self.root / ref).read_bytes()).hexdigest()}

    def command(self, *argv):
        return subprocess.run(argv, cwd=self.root, capture_output=True, check=True, text=True)

    def prepare(self, write="export.py", receipt="review/builder.json", ticket="T-CSV"):
        return handoff.prepare(self.root, "tickets.json", "fixture-op", self.plan_sha,
                               ticket, [write], receipt)

    def test_builder_can_receive_then_detect_stale_starting_file(self):
        self.save("review/handoff.json", self.prepare())
        sha = self.pin("review/handoff.json")["sha256"]
        result = handoff.verify(self.root, "review/handoff.json", sha)
        self.assertEqual(result["status"], "verified-at-admission")
        self.assertEqual(result["handoff"]["requirements"][0]["id"], "R-CSV")
        self.assertFalse(result["handoff"]["process_permissions_enforced"])
        (self.root / "export.py").write_text("def export(): return 'other worker'\n")
        with self.assertRaisesRegex(context.ContextError, "stale"):
            handoff.verify(self.root, "review/handoff.json", sha)

    def test_review_uses_actual_returned_artifact_not_only_builder_claim(self):
        self.save("review/handoff.json", self.prepare())
        digest = self.pin("review/handoff.json")["sha256"]
        (self.root / "export.py").write_text("def export(): return 'new code'\n")
        self.save("review/builder.json", {
            "schema_version": handoff.RETURN, "status": "changes-prepared",
            "handoff_sha256": digest, "ticket_id": "T-CSV",
            "artifacts": [self.pin("export.py")], "checks": ["Builder reported a test run"],
        })
        result = handoff.verify_result(self.root, "review/handoff.json", digest)
        self.assertEqual(result["status"], "returned-artifacts-verified")
        self.assertFalse(result["functional_outcome_verified"])
        (self.root / "export.py").write_text("def export(): return 'after return'\n")
        with self.assertRaisesRegex(context.ContextError, "differs"):
            handoff.verify_result(self.root, "review/handoff.json", digest)

    def test_rechecks_immutable_inputs_after_opening_builder_return(self):
        self.save("review/handoff.json", self.prepare())
        digest = self.pin("review/handoff.json")["sha256"]
        (self.root / "export.py").write_text("def export(): return 'changed'\n")
        self.save("review/builder.json", {
            "schema_version": handoff.RETURN, "status": "changes-prepared",
            "handoff_sha256": digest, "ticket_id": "T-CSV",
            "artifacts": [self.pin("export.py")], "checks": ["Observed checks"],
        })
        read_bytes = context.bound_bytes
        def drift_when_opening_return(root, name):
            observed = read_bytes(root, name)
            if name == "review/builder.json":
                (self.root / "review/architecture.md").write_text("Changed while reading return.\n")
            return observed
        with patch.object(context, "bound_bytes", side_effect=drift_when_opening_return):
            with self.assertRaisesRegex(context.ContextError, "replan source changed"):
                handoff.verify_result(self.root, "review/handoff.json", digest)

    def test_handoff_rechecks_supplemental_source_since_the_applied_decision(self):
        result = self.prepare()
        self.assertEqual(result["replan_sources"]["review/architecture.md"],
                         self.pin("review/architecture.md")["sha256"])
        with self.assertRaisesRegex(context.ContextError, "overlaps"):
            self.prepare(write="review/architecture.md")
        (self.root / "review/architecture.md").write_text("Change after the replan.\n")
        with self.assertRaisesRegex(context.ContextError, "source changed"):
            self.prepare()

    def test_gates_protect_decision_sources_and_off_plan_work(self):
        for write in ("tickets.json", "requirements.json", "review/request.json", "review/approval.json"):
            with self.subTest(write=write), self.assertRaisesRegex(context.ContextError, "overlaps"):
                self.prepare(write=write)
        with self.assertRaisesRegex(context.ContextError, "overlaps"):
            self.prepare(write="REQUIREMENTS.json")
        with self.assertRaisesRegex(context.ContextError, "aliases"):
            handoff.prepare(self.root, "tickets.json", "fixture-op", self.plan_sha,
                            "T-CSV", ["export.py", "EXPORT.py"], "review/builder.json")
        os.link(self.root / "requirements.json", self.root / "alias.py")
        with self.assertRaisesRegex(context.ContextError, "hard links"):
            self.prepare(write="alias.py")
        with self.assertRaisesRegex(context.ContextError, "outside"):
            self.prepare(ticket="I")
        for write in (".git/config", ".ticket-dispatch.json", "review/.ticket-replan.lock"):
            with self.subTest(write=write), self.assertRaisesRegex(context.ContextError, "protected"):
                self.prepare(write=write)
        self.save("review/approval.json", {"replaced": True})
        with self.assertRaisesRegex(context.ContextError, "decision changed"):
            self.prepare()


if __name__ == "__main__":
    unittest.main()
