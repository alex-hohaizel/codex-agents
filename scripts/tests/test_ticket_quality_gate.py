#!/usr/bin/env python3
"""Verify that incomplete or stale evidence cannot be used as a passing gate."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_quality_gate.py"


class TicketQualityGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.write("requirements.json", {"requirements": [
            {"id": "R-1", "text": "Do not quote an invalid SKU.", "priority": "must"},
            {"id": "R-2", "text": "Show the quote's currency.", "priority": "must",
             "dependencies": ["R-1"]},
        ]})
        self.write("tickets.json", {
            "schema_version": "atelier.ticket-projection/1", "project_id": "quotes",
            "native_revision": "r2", "requirement_sources": [self.pin("requirements.json")],
            "tickets": [
                {"id": "BUG-1", "kind": "bug", "title": "Display currency", "status": "in-review",
                 "requirement_ids": ["R-2"], "acceptance": "Give the quoted amount in USD."},
            ],
        })
        (self.root / "service.py").write_text("PRICE = '1.50 USD'\n")
        (self.root / "evidence.txt").write_text("Read HTTP status 400 for unknown item.")
        (self.root / "display.txt").write_text("Browser displayed a quote of 1.50 USD.")
        self.plan = {
            "schema_version": "atelier.ticket-quality-plan/1", "project_id": "quotes",
            "native_revision": "r2", "projection_sha256": self.pin("tickets.json")["sha256"],
            "select": ["BUG-1"], "subject": [self.pin("service.py")], "producer": "builder",
            "checks": [
                {"id": "BAD-SKU", "ticket_id": "BUG-1", "requirement_ids": ["R-1"],
                 "priority": "P0", "risk": "Charge against wrong item",
                 "procedure": "Call the quote API with an unknown item", "expected": "HTTP 400"},
                {"id": "USD", "ticket_id": "BUG-1", "requirement_ids": ["R-2"], "priority": "P1",
                 "risk": "Wrong currency", "procedure": "Read the displayed price",
                 "expected": "Displayed amount in USD"},
            ],
        }
        self.results = [
            {"id": "BAD-SKU", "outcome": "pass", "observation": "HTTP 400",
             "artifacts": [self.pin("evidence.txt")]},
            {"id": "USD", "outcome": "pass", "observation": "USD price shown",
             "artifacts": [self.pin("display.txt")]},
        ]

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def pin(self, name):
        return {"path": name, "sha256": sha256((self.root / name).read_bytes()).hexdigest()}

    def run_gate(self, *, expected=0, reviewer="qa", include_review=True, plan_digest=None):
        self.write("plan.json", self.plan)
        plan_sha = self.pin("plan.json")["sha256"]
        args = [
            sys.executable, "-B", str(SCRIPT), "--root", str(self.root),
            "--projection", "tickets.json", "--plan", "plan.json",
            "--plan-sha256", plan_digest or plan_sha, "--as-of", "2026-11-17",
            "--require-pass",
        ]
        if include_review:
            self.write("review.json", {"schema_version": "atelier.ticket-quality-review/1",
                                       "plan_sha256": plan_sha, "reviewer": reviewer,
                                       "results": self.results})
            args += ["--review", "review.json", "--review-sha256", self.pin("review.json")["sha256"]]
        output = subprocess.run(args, capture_output=True, text=True, timeout=10)
        self.assertEqual(output.returncode, expected, output.stderr or output.stdout)
        return json.loads(output.stdout or output.stderr)

    def test_complete_review_passes_and_preserves_source_trace(self):
        result = self.run_gate()
        self.assertEqual(result["gate"], "PASS")
        trace = {row["requirement_id"]: row for row in result["trace"]}
        self.assertEqual(trace["R-1"]["check_ids"], ["BAD-SKU"])
        self.assertEqual(trace["R-1"]["source"]["source_sha256"],
                         self.pin("requirements.json")["sha256"])
        self.assertFalse(result["release_authorized"])

    def test_missing_and_unknown_evidence_are_reported_separately(self):
        result = self.run_gate(expected=3, include_review=False)
        self.assertEqual(result["gate"], "CONCERNS")
        self.plan["checks"].pop()
        self.results.pop()
        self.results[0].update(outcome="unknown-effect", artifacts=[])
        result = self.run_gate(expected=3)
        self.assertEqual(result["gate"], "CONCERNS")
        self.assertEqual(result["checks"][0]["disposition"], "unknown-effect")
        self.assertEqual(result["unmapped"], [{"ticket_id": "BUG-1", "requirement_id": "R-2"}])

    def test_candidate_drift_blocks_and_evidence_drift_reopens(self):
        (self.root / "evidence.txt").write_text("Unreviewed replacement.")
        result = self.run_gate(expected=3)
        self.assertEqual(result["checks"][0]["disposition"], "stale-evidence")
        (self.root / "service.py").write_text("PRICE = '1.50 EUR'\n")
        self.assertIn("SOURCE_DRIFT", self.run_gate(expected=2)["error"])

    def test_known_failure_can_only_be_waived_with_current_decision(self):
        self.results[1]["outcome"] = "fail"
        self.assertEqual(self.run_gate(expected=3)["gate"], "FAIL")
        (self.root / "decision.txt").write_text("Exception recorded by product owner.")
        waiver = {"by": "product-owner", "reason": "Limited locale",
                  "expires_on": "2026-11-17", "decision": self.pin("decision.txt")}
        self.results[1]["waiver"] = waiver
        self.assertEqual(self.run_gate(expected=3)["gate"], "WAIVED")
        waiver["expires_on"] = "2026-11-16"
        self.assertEqual(self.run_gate(expected=3)["gate"], "FAIL")
        self.results[0].update(outcome="fail", waiver=self.results[1].pop("waiver"))
        self.assertIn("non-P0", self.run_gate(expected=2)["error"])

    def test_passing_check_does_not_reopen_a_deferred_ancestor(self):
        projection = json.loads((self.root / "tickets.json").read_bytes())
        projection["tickets"][0]["parent"] = "I-LATER"
        projection["tickets"].append({
            "id": "I-LATER", "kind": "initiative", "title": "Deferred orders",
            "status": "deferred",
        })
        self.write("tickets.json", projection)
        self.plan["projection_sha256"] = self.pin("tickets.json")["sha256"]
        result = self.run_gate(expected=3)
        self.assertEqual(result["gate"], "CONCERNS")
        self.assertEqual(result["upstream_holds"][0]["recorded_holds"],
                         [{"code": "ancestor-deferred", "ticket": "I-LATER"}])

    def test_selected_group_has_its_own_criteria(self):
        requirements = json.loads((self.root / "requirements.json").read_bytes())
        requirements["requirements"].append(
            {"id": "R-GROUP", "text": "Refresh the aggregate results.", "priority": "must"},
        )
        self.write("requirements.json", requirements)
        projection = json.loads((self.root / "tickets.json").read_bytes())
        projection["requirement_sources"] = [self.pin("requirements.json")]
        projection["tickets"][0]["parent"] = "E-SALES"
        projection["tickets"].extend([
            {"id": "GOAL", "kind": "initiative", "title": "Sales", "status": "planned"},
            {"id": "E-SALES", "kind": "epic", "parent": "GOAL", "title": "Roll up sales",
             "status": "planned", "requirement_ids": ["R-GROUP"],
             "acceptance": "Aggregate results equal the underlying sales."},
        ])
        self.write("tickets.json", projection)
        self.plan["projection_sha256"] = self.pin("tickets.json")["sha256"]
        self.plan["select"] = ["GOAL"]
        result = self.run_gate(expected=3)
        self.assertEqual(result["unmapped"], [{"ticket_id": "E-SALES", "requirement_id": "R-GROUP"}])
        self.plan["checks"].append({
            **self.plan["checks"][0], "id": "AGGREGATE", "ticket_id": "E-SALES",
            "requirement_ids": ["R-GROUP"], "procedure": "Read sales aggregate",
            "expected": "Same total",
        })
        (self.root / "totals.txt").write_text("Observed totals reconciled.")
        self.results.append({
            "id": "AGGREGATE", "outcome": "pass", "observation": "Same total",
            "artifacts": [self.pin("totals.txt")],
        })
        self.assertEqual(self.run_gate()["gate"], "PASS")

    def test_candidate_bytes_cannot_be_reused_as_their_own_review(self):
        (self.root / "alias.txt").write_bytes((self.root / "service.py").read_bytes())
        self.results[0]["artifacts"] = [self.pin("alias.txt")]
        self.assertIn("aliases an input", self.run_gate(expected=2)["error"])

    def test_rejects_self_review_and_changed_plan_bytes(self):
        self.assertIn("distinct", self.run_gate(expected=2, reviewer="Builder")["error"])
        self.assertIn("SOURCE_DRIFT", self.run_gate(expected=2, plan_digest="0" * 64)["error"])


if __name__ == "__main__":
    unittest.main()
