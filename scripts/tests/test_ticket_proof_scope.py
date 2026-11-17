"""Prove the distinction between unaffected historical evidence and current acceptance."""

import hashlib
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_proof_scope as proof


class ProofScopeTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name).resolve()
        self.before, self.after = root / "before", root / "after"
        self.before.mkdir()
        self.acceptance = "Operators can still export reports."
        self.write(self.before, "requirements.json", {"requirements": [
            {"id": "R-EXPORT", "text": "Authorized operators can export reports."},
            {"id": "R-SCHEDULE", "text": "Show calendar week."},
        ]})
        (self.before / "tested.py").write_text("print('unchanged export runtime')\n")
        (self.before / "runtime-log.txt").write_text("Output of the witnessed export test.\n")
        self.write(self.before, "receipt.json", {
            "schema_version": "atelier.ticket-acceptance/1",
            "project_id": "reports", "native_revision": "r1", "ticket_id": "T-EXPORT",
            "criterion_sha256": self.digest(self.acceptance.encode()),
            "subject": self.pin(self.before, "runtime-log.txt"),
        })
        self.projection = {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "reports", "native_revision": "r1",
            "requirement_sources": [self.pin(self.before, "requirements.json")],
            "tickets": [
                {"id": "I", "kind": "initiative", "title": "Delivery", "status": "planned"},
                {"id": "T-EXPORT", "kind": "story", "title": "Export", "parent": "I",
                 "status": "accepted", "requirement_ids": ["R-EXPORT"], "acceptance": self.acceptance,
                 "evidence": [self.pin(self.before, "receipt.json")]},
                {"id": "T-SCHEDULE", "kind": "story", "title": "Calendar", "parent": "I",
                 "status": "planned", "requirement_ids": ["R-SCHEDULE"]},
            ],
        }
        self.write(self.before, "tickets.json", self.projection)
        self.write(self.before, "scope.json", {
            "schema_version": proof.SCOPE, "project_id": "reports", "native_revision": "r1",
            "ticket_id": "T-EXPORT", "receipt": self.pin(self.before, "receipt.json"),
            "inputs": [self.pin(self.before, "tested.py")],
        })
        self.scope_sha = self.pin(self.before, "scope.json")["sha256"]
        shutil.copytree(self.before, self.after)
        self.requirements = {"requirements": [
            {"id": "R-EXPORT", "text": "Authorized operators can export reports."},
            {"id": "R-SCHEDULE", "text": "Show calendar quarter next to week."},
        ]}
        self.refresh()

    @staticmethod
    def digest(data):
        return hashlib.sha256(data).hexdigest()

    def pin(self, root, name):
        return {"path": name, "sha256": self.digest((root / name).read_bytes())}

    def write(self, root, name, obj):
        (root / name).write_text(json.dumps(obj) + "\n")

    def refresh(self):
        self.write(self.after, "requirements.json", self.requirements)
        self.projection["native_revision"] = "r2"
        self.projection["requirement_sources"] = [self.pin(self.after, "requirements.json")]
        self.write(self.after, "tickets.json", self.projection)

    def assess(self):
        return proof.assess(self.before, self.after, "tickets.json", "scope.json", self.scope_sha)

    def test_an_unrelated_change_keeps_proof_eligible_but_requires_a_current_decision(self):
        result = self.assess()
        self.assertEqual(result["status"], "eligible-for-independent-reuse-review")
        self.assertFalse(result["current_acceptance_granted"])
        self.assertFalse(result["proof_scope_completeness_verified"])
        self.assertEqual(result["blockers"], [])

    def test_removed_supporting_evidence_is_not_a_revision_only_change(self):
        (self.before / "other.log").write_text("Previously retained test material.\n")
        ticket = self.projection["tickets"][1]
        ticket["evidence"].append(self.pin(self.before, "other.log"))
        self.projection["native_revision"] = "r1"
        self.projection["requirement_sources"] = [self.pin(self.before, "requirements.json")]
        self.write(self.before, "tickets.json", self.projection)
        ticket["evidence"].pop()
        self.refresh()
        reasons = {item["reason"] for item in self.assess()["blockers"]}
        self.assertIn("historical-ticket-evidence-changed", reasons)

    def test_a_reopened_or_unproven_prerequisite_requires_fresh_proof(self):
        for root in (self.before, self.after):
            (root / "check-auth.txt").write_text("Historical verified authorization.\n")
            self.write(root, "auth-receipt.json", {
                "schema_version": "atelier.ticket-acceptance/1",
                "project_id": "reports", "native_revision": "r1", "ticket_id": "T-AUTH",
                "criterion_sha256": self.digest(b"Authorized users can act."),
                "subject": self.pin(root, "check-auth.txt"),
            })
        self.projection["tickets"][1]["depends_on"] = ["T-AUTH"]
        authorization = {
            "id": "T-AUTH", "kind": "story", "title": "Authorization", "parent": "I",
            "status": "accepted", "requirement_ids": ["R-EXPORT"], "acceptance": "Authorized users can act.",
            "evidence": [self.pin(self.before, "auth-receipt.json")],
        }
        self.projection["tickets"].append(authorization)
        self.projection["native_revision"] = "r1"
        self.projection["requirement_sources"] = [self.pin(self.before, "requirements.json")]
        self.write(self.before, "tickets.json", self.projection)
        self.refresh()
        self.assertEqual(self.assess()["status"], "eligible-for-independent-reuse-review")
        authorization.pop("evidence")
        self.refresh()
        self.assertEqual(self.assess()["blockers"], [
            {"reason": "prerequisite-evidence-changed", "ticket_id": "T-AUTH"},
        ])
        authorization["status"] = "in-progress"
        self.refresh()
        self.assertEqual(self.assess()["blockers"], [
            {"reason": "prerequisite-acceptance-changed", "ticket_id": "T-AUTH"},
        ])

    def test_refuses_reuse_if_the_requirement_or_execution_input_changes(self):
        (self.after / "tested.py").write_text("print('new execution input')\n")
        self.requirements["requirements"][0]["text"] = "Exports now need a supervisor."
        self.refresh()
        result = self.assess()
        self.assertEqual(result["status"], "fresh-proof-required")
        self.assertEqual({item["reason"] for item in result["blockers"]},
                         {"affected-by-replan", "proof-input-drift"})


if __name__ == "__main__":
    unittest.main()
