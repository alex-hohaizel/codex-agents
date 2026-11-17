"""Check product-spec lifecycle using real editable companion files and native pins."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_product_spec.py"


class ProductSpecTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.raw = {
            "delivery.md": "The confirmation states the recipient.\n",
            "receipt.md": "A pending receipt survives reopening.\n",
        }
        self.requirements = {"requirements": [
            {"id": "SCOPE", "text": self.raw["delivery.md"].strip(), "priority": "should",
             "acceptance": "The displayed recipient is the one on the stored delivery."},
            {"id": "RECEIPT", "text": self.raw["receipt.md"].strip(), "priority": "must",
             "dependencies": ["SCOPE"], "acceptance": "Pending confirmation reappears on reopening."},
        ]}
        self.decisions = {"decisions": [{"id": "PERSIST", "text": "Use existing storage."}]}
        self.coverage = [
            {"id": "SCOPE", "source_path": "delivery.md",
             "source_excerpt": self.raw["delivery.md"].strip(),
             "prd_excerpt": "Open the delivery with the recorded recipient visible.",
             "architecture_excerpt": "Render the persisted recipient ID from the selected receipt.",
             "decision_ids": []},
            {"id": "RECEIPT", "source_path": "receipt.md",
             "source_excerpt": self.raw["receipt.md"].strip(),
             "prd_excerpt": "Reopening returns the pending receipt to the operator.",
             "architecture_excerpt": "Load the pending key from existing receipt storage.",
             "decision_ids": ["PERSIST"]},
        ]
        self.revision = "r1"
        self.alternatives = []
        self.tickets = [
            {"id": "T-RESULT", "kind": "bug", "status": "planned", "title": "Restore result",
             "requirement_ids": ["RECEIPT"], "acceptance": "Restore a pending result."},
        ]

    def json(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def pin(self, name):
        return {"path": name, "sha256": sha256((self.root / name).read_bytes()).hexdigest()}

    def record_inputs(self, documents=True):
        for path, body in self.raw.items():
            (self.root / path).write_text(body, encoding="utf-8")
        self.json("requirements.json", self.requirements)
        self.json("decisions.json", self.decisions)
        self.json("tickets.json", {
            "schema_version": "atelier.ticket-projection/1", "project_id": "dispatch-receipts",
            "native_revision": self.revision, "requirement_sources": [self.pin("requirements.json")],
            "tickets": self.tickets,
        })
        if documents:
            for role, title in (("prd", "PRD"), ("architecture", "Architecture")):
                (self.root / f"{role}.md").write_text(
                    f"# {title}\n\n" + "\n\n".join(
                        f"## {row['id']}\n\n{row[role + '_excerpt']}" for row in self.coverage
                    ) + "\n", encoding="utf-8",
                )
        self.json("manifest.json", {
            "schema_version": "atelier.ticket-product-spec-manifest/1",
            "project_id": "dispatch-receipts", "native_revision": self.revision,
            "projection_sha256": self.pin("tickets.json")["sha256"], "author": "product",
            "sources": [self.pin(path) for path in self.raw],
            "decision_sources": [self.pin("decisions.json")],
            "comparison_sources": [self.pin(path) for path in self.alternatives],
            "documents": {role: self.pin(role + ".md") for role in ("prd", "architecture")},
            "coverage": self.coverage,
        })

    def run_spec(self, mode, *args, expected=0):
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), mode, "--root", str(self.root),
             "--projection", "tickets.json", "--input", "manifest.json", *args],
            check=False, text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(proc.returncode, expected, proc.stdout or proc.stderr)
        return json.loads(proc.stdout or proc.stderr)

    def write_review(self, capture, **overrides):
        self.json("review.json", {
            "schema_version": "atelier.ticket-product-spec-review/1",
            "reviewer": "independent-qa", "bundle_sha256": capture["bundle_sha256"],
            "verdict": "approve", "summary": "Reviewed against both project sources.",
            "checks": [
                {"id": ident, "outcome": "matches", "observation": "Mapped to the original rule."}
                for ident in capture["coverage"]
            ],
            **overrides,
        })

    def run_review(self, expected=0):
        return self.run_spec("review", "--review", "review.json", "--review-sha256",
                             self.pin("review.json")["sha256"], expected=expected)

    def test_create_and_review_separate_criteria_and_files(self):
        self.record_inputs()
        captured = self.run_spec("capture")
        self.assertEqual(set(captured["coverage"]), {"RECEIPT", "SCOPE"})
        self.assertEqual(captured, self.run_spec("capture"))
        self.write_review(captured)
        self.assertEqual(self.run_review()["status"], "reviewed")
        self.write_review(captured, reviewer="PRODUCT")
        self.assertIn("reviewer must differ", self.run_review(expected=2)["error"])

    def test_revision_invalidates_stale_source_and_old_review(self):
        self.record_inputs()
        previous = self.run_spec("capture")
        self.json("before.json", previous)
        self.write_review(previous)
        (self.root / "delivery.md").write_text(self.raw["delivery.md"] + "New discussion.\n")
        self.assertIn("SOURCE_DRIFT", self.run_spec("capture", expected=2)["error"])
        self.revision = "r2"
        self.raw["delivery.md"] += "New discussion.\n"
        self.record_inputs()
        changes = self.run_spec("compare", "--before", str(self.root / "before.json"),
                                "--before-sha256", self.pin("before.json")["sha256"])
        self.assertEqual(changes["changed_fields_by_requirement"], {"SCOPE": ["source_sha256"]})
        self.assertEqual(changes["affected_requirement_ids"], ["RECEIPT", "SCOPE"])
        self.assertEqual(changes["affected_ticket_ids"], ["T-RESULT"])
        self.assertFalse(changes["previous_review_applies"])
        self.assertIn("different specification bundle", self.run_review(expected=2)["error"])
        self.write_review(self.run_spec("capture"))
        self.assertEqual(self.run_review()["status"], "reviewed")

    def test_reassigned_requirement_affects_both_tickets_without_document_changes(self):
        self.tickets.append({
            "id": "T-SCOPE", "kind": "bug", "status": "planned", "title": "Verify delivery",
            "requirement_ids": ["SCOPE"], "acceptance": "Verify the delivery record.",
        })
        self.record_inputs()
        self.json("before.json", self.run_spec("capture"))
        self.revision = "r2"
        self.tickets[0]["requirement_ids"] = ["SCOPE"]
        self.tickets[1]["requirement_ids"] = ["RECEIPT"]
        self.record_inputs()

        changes = self.run_spec("compare", "--before", str(self.root / "before.json"),
                                "--before-sha256", self.pin("before.json")["sha256"])
        self.assertEqual(changes["changed_fields_by_requirement"], {})
        self.assertEqual(changes["affected_requirement_ids"], [])
        self.assertEqual(changes["changed_documents"], [])
        self.assertEqual(changes["affected_ticket_ids"], ["T-RESULT", "T-SCOPE"])
        self.assertEqual(changes["changed_ticket_requirement_links"], {
            "T-RESULT": {"before": ["RECEIPT", "SCOPE"], "after": ["SCOPE"]},
            "T-SCOPE": {"before": ["SCOPE"], "after": ["RECEIPT", "SCOPE"]},
        })

    def test_omitted_dependency_or_companion_criterion_refuses(self):
        self.record_inputs()
        architecture = self.root / "architecture.md"
        architecture.write_text("# Architecture\n\nOther behavior.\n")
        self.record_inputs(documents=False)
        error = self.run_spec("capture", expected=2)["error"]
        self.assertIn("architecture omits cited criterion", error)
        self.coverage.remove(self.coverage[0])
        self.record_inputs()
        self.assertIn("missing mandatory or dependent coverage: SCOPE",
                      self.run_spec("capture", expected=2)["error"])

    def test_alternate_claim_and_superseded_decision_are_visible(self):
        alternate = {"requirements": [dict(self.requirements["requirements"][0], priority="must")]}
        self.json("alternate.json", alternate)
        self.alternatives = ["alternate.json"]
        self.record_inputs()
        self.assertIn("disagrees with alternate.json", self.run_spec("capture", expected=2)["error"])
        self.alternatives = []
        self.decisions["decisions"].append({
            "id": "NEW", "text": "Use existing storage with delivery ownership.",
            "supersedes": ["PERSIST"],
        })
        self.record_inputs()
        self.assertIn("superseded decision", self.run_spec("capture", expected=2)["error"])
        self.coverage[1]["decision_ids"] = ["NEW"]
        self.record_inputs()
        self.assertIn("NEW", self.run_spec("capture")["coverage"]["RECEIPT"]["decision_sha256"])

    def test_withdrawn_context_and_open_review_finding(self):
        self.record_inputs()
        capture = self.run_spec("capture")
        self.write_review(capture, verdict="changes-requested", checks=[
            {"id": ident, "outcome": "needs-change", "observation": "Wrong receipt is possible."}
            for ident in capture["coverage"]
        ])
        self.assertEqual(self.run_review(expected=3)["status"], "changes-requested")
        self.json("before.json", capture)
        self.revision = "r2"
        self.record_inputs()
        self.assertIn("prior capture bytes changed", self.run_spec(
            "compare", "--before", str(self.root / "before.json"),
            "--before-sha256", "0" * 64, expected=2,
        )["error"])


if __name__ == "__main__":
    unittest.main()
