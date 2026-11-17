#!/usr/bin/env python3
"""Exercise planning proposals against native-source pins and recorded work."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_refine.py"


class TicketRefinementTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.write_json("requirements.json", {"requirements": [
            {"id": "R-STAMP", "text": "Each export names the time zone."},
            {"id": "R-PROVIDER", "text": "The operator can change exporter.", "priority": "should",
             "always_review": True},
            {"id": "R-WEEK", "text": "The operator can schedule a weekly export."},
        ]})
        (self.root / "decision.md").write_text(
            "# Export decisions\nRecord the selected time zone in ISO-8601 format.\n"
        )
        (self.root / "export-result.txt").write_text("Observed export names UTC.")
        criterion = "UTC is displayed in the export."
        self.write_json("export-receipt.json", {
            "schema_version": "atelier.ticket-acceptance/1",
            "project_id": "exports", "native_revision": "r17", "ticket_id": "T-STAMP",
            "criterion_sha256": hashlib.sha256(criterion.encode()).hexdigest(),
            "subject": self.pin("export-result.txt"),
        })
        self.projection = {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "exports", "native_revision": "r17",
            "requirement_sources": [self.pin("requirements.json")],
            "tickets": [
                {"id": "I-REPORT", "kind": "initiative", "title": "Improve exports",
                 "status": "planned"},
                {"id": "E-EXPORT", "kind": "epic", "parent": "I-REPORT",
                 "title": "Export history", "status": "planned"},
                {"id": "E-SCHEDULE", "kind": "epic", "parent": "I-REPORT",
                 "title": "Scheduled exports", "status": "deferred"},
                {"id": "T-STAMP", "kind": "story", "parent": "E-EXPORT",
                 "title": "Stamp", "status": "accepted", "requirement_ids": ["R-STAMP"],
                 "acceptance": criterion, "evidence": [self.pin("export-receipt.json")]},
                {"id": "T-PROVIDER", "kind": "story", "parent": "E-EXPORT",
                 "title": "Choice of exporter", "status": "in-progress",
                 "requirement_ids": ["R-PROVIDER"]},
                {"id": "T-WEEK", "kind": "story", "parent": "E-SCHEDULE",
                 "title": "Run weekly", "status": "planned", "requirement_ids": ["R-WEEK"]},
            ],
        }
        self.write_json("tickets.json", self.projection)
        self.proposal = {
            "schema_version": "atelier.ticket-refinement/1",
            "project_id": "exports", "native_revision": "r17",
            "projection_sha256": self.pin("tickets.json")["sha256"],
            "changes": [],
        }

    def write_json(self, name, data):
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def pin(self, name):
        raw = (self.root / name).read_bytes()
        return {"path": name, "sha256": hashlib.sha256(raw).hexdigest()}

    def source(self, path="decision.md", excerpt=None, **fields):
        return dict(self.pin(path), excerpt=excerpt or
                    "Record the selected time zone in ISO-8601 format.", **fields)

    def change(self, key, patch, sources=None):
        self.proposal["changes"].append({
            "ticket_id": key, "patch": patch, "sources": sources or [self.source()],
            "rationale": "Apply the format agreed for exports.",
        })

    def snapshot(self):
        return {path.name: path.read_bytes() for path in self.root.iterdir() if path.is_file()}

    def run_cli(self, *args, expected=0):
        self.write_json("proposal.json", self.proposal)
        before = self.snapshot()
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root), "--input", "tickets.json",
             *args], capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        self.assertEqual(self.snapshot(), before)
        return json.loads(result.stdout or result.stderr)

    def propose(self, *, expected=0):
        return self.run_cli("propose", "--proposal", "proposal.json", expected=expected)

    def test_refine_prepares_readable_sources_and_keeps_historical_receipt(self):
        brief = self.run_cli("brief", "--select", "T-STAMP")
        self.assertEqual(brief["selected_tickets"][0]["acceptance_status"], "supported")
        self.assertEqual(brief["requirements"][0]["verbatim"], "Each export names the time zone.")
        self.assertEqual(brief["projection"], self.pin("tickets.json"))

        criterion = "The export time includes the selected zone as an ISO-8601 offset."
        self.change("T-STAMP", {"acceptance": criterion}, [
            self.source("requirements.json", "names the time zone", requirement_id="R-STAMP"),
            self.source(),
        ])
        self.change("T-PROVIDER", {"title": "Let operators switch exporter"})
        result = self.propose()
        self.assertFalse(result["applied"])
        self.assertFalse(result["semantic_support_verified"])
        accepted, active = result["changes"]
        self.assertEqual(accepted["changes"]["acceptance"], {
            "from": "UTC is displayed in the export.",
            "to": criterion,
        })
        self.assertEqual(accepted["baseline_evidence"][0]["status"], "verified")
        self.assertEqual(accepted["recorded_status"], "accepted")
        self.assertEqual(accepted["follow_up"], {
            "action": "review-new-evidence", "suggested_role": "foundry-qa",
        })
        self.assertEqual(accepted["sources"][0]["requirement_id"], "R-STAMP")
        self.assertEqual(accepted["sources"][1]["first_line"], 2)
        self.assertEqual(active["recorded_status"], "in-progress")
        self.assertEqual(active["follow_up"]["action"], "reconcile-with-current-owner")

    def test_refinement_keeps_exact_project_revision_and_citation(self):
        self.change("T-PROVIDER", {"title": "Exporter selection"})
        self.proposal["native_revision"] = "r16"
        self.assertIn("baseline mismatch", self.propose(expected=2)["error"])
        self.proposal["native_revision"] = "r17"
        (self.root / "decision.md").write_text("# Later decision\n")
        self.assertEqual(self.propose(expected=2)["error"], "SOURCE_DRIFT: decision.md")
        self.proposal["changes"][0]["sources"] = [self.source()]
        self.assertIn("excerpt is absent", self.propose(expected=2)["error"])

    def test_refinement_requires_citation_to_named_requirement_text(self):
        self.change("T-STAMP", {"acceptance": "Use the selected time zone."}, [
            self.source("requirements.json", "can change exporter", requirement_id="R-STAMP")
        ])
        self.assertIn("absent from the named requirement", self.propose(expected=2)["error"])
        self.proposal["changes"][0]["sources"] = [self.source()]
        self.assertIn("requires a citation to a linked requirement", self.propose(expected=2)["error"])
        self.proposal["changes"][0]["sources"] = [
            self.source("requirements.json", "Native acceptance retained", requirement_id="R-STAMP")
        ]
        self.assertIn("absent from the named requirement", self.propose(expected=2)["error"])

    def test_protects_always_review_and_inherited_deferral(self):
        self.change("T-PROVIDER", {"requirement_ids": []}, [
            self.source("requirements.json", "operator can change exporter",
                        requirement_id="R-PROVIDER")
        ])
        self.assertEqual(self.propose(expected=2)["error"],
                         "mandatory or always-review coverage regressed: R-PROVIDER")
        self.proposal["changes"] = []
        self.change("T-WEEK", {"parent": "E-EXPORT"})
        self.assertEqual(self.propose(expected=2)["error"],
                         "refinement changes native deferral: T-WEEK")

    def test_review_sees_dependencies_inherited_from_a_new_epic_prerequisite(self):
        self.change("E-SCHEDULE", {"depends_on": ["T-STAMP"]})
        result = self.propose()
        by_ticket = {row["ticket_id"]: row["changes"] for row in result["graph_changes"]}
        self.assertEqual(by_ticket["T-WEEK"]["effective_prerequisites"], {
            "from": [], "to": ["T-STAMP"],
        })
        self.assertEqual(result["changes"][0]["follow_up"]["action"],
                         "review-without-activating-deferred-work")

    def test_refinement_preserves_retired_history_without_giving_it_coverage(self):
        self.projection["replan_retirements"] = [{
            "ticket_id": "T-WEEK", "action": "drop", "retired_in": "r17", "successors": [],
        }]
        next(row for row in self.projection["tickets"] if row["id"] == "T-WEEK")["status"] = "deferred"
        self.write_json("tickets.json", self.projection)
        self.proposal["projection_sha256"] = self.pin("tickets.json")["sha256"]

        brief = self.run_cli("brief", "--select", "T-WEEK")
        self.assertEqual(brief["selected_tickets"][0]["recorded_status"], "deferred")
        self.assertIn("replan_retirement", brief["selected_tickets"][0])
        self.change("T-WEEK", {"title": "Rewrite the archived work"})
        self.assertEqual(self.propose(expected=2)["error"], "retired work is historical: T-WEEK")
        self.proposal["changes"] = []
        self.change("T-PROVIDER", {"title": "Refine the operator's active task"})
        result = self.propose()
        self.assertEqual(result["proposed_coverage"]["unmapped_must_requirements"], ["R-WEEK"])
        self.assertEqual(result["proposed_coverage"]["deferred_only_must_requirements"], [])

    def test_preserves_recorded_status_and_refuses_proof_as_source(self):
        self.change("T-PROVIDER", {"status": "accepted"})
        self.assertIn("only planning fields", self.propose(expected=2)["error"])
        self.proposal["changes"] = []
        self.change("T-PROVIDER", {"title": "Exporter selection"}, [
            self.source("export-result.txt", "Observed export")
        ])
        self.assertIn("citation source is a proposal, projection or ticket proof",
                      self.propose(expected=2)["error"])


if __name__ == "__main__":
    unittest.main()
