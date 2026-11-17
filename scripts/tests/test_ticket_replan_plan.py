#!/usr/bin/env python3
"""Exercise source-bound replanning against actual native projection files."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import ticket_replan_plan as replan


class TicketReplanPlanTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.requirements = {
            "R-HIST": "Export history exposes the prior release code.",
            "R-CSV": "CSV uses UTF-8 and retains the accepted header.",
            "R-UI": "UI offers a confirmation before downloading.",
            "R-OTHER": "Independent scheduling continues.",
            "R-FALLBACK": "Legacy fallback can be retired.",
            "R-NEW": "Spreadsheet download says when the export was created.",
        }
        self.write("requirements.json", {"requirements": [
            {"id": ident, "text": body, "priority": "should" if ident == "R-FALLBACK" else "must"}
            for ident, body in self.requirements.items()
        ]})
        (self.root / "prior-export.txt").write_text("Observed FSL R3.1 export", encoding="utf-8")
        historical = self.ticket("EXP-12", "R-HIST", status="accepted")
        self.write("export-receipt.json", {
            "schema_version": "atelier.ticket-acceptance/1", "project_id": "field-slate",
            "native_revision": "r31", "ticket_id": historical["id"],
            "criterion_sha256": self.sha(historical["acceptance"].encode()),
            "subject": self.pin("prior-export.txt"),
        })
        historical["evidence"] = [self.pin("export-receipt.json")]
        self.projection = {
            "schema_version": "atelier.ticket-projection/1", "project_id": "field-slate",
            "native_revision": "r31", "requirement_sources": [self.pin("requirements.json")],
            "native_owner_metadata": {"team": "allowlisted-example"},
            "replan_receipts": [{"previous": "r30", "issued": "r31"}],
            "tickets": [
                {"id": "I-OPS", "kind": "initiative", "title": "Operations", "status": "planned"},
                {"id": "E-EXP", "kind": "epic", "title": "Export", "status": "planned", "parent": "I-OPS"},
                historical,
                self.ticket("EXP-30", "R-CSV"),
                self.ticket("EXP-40", "R-UI", depends_on=["EXP-30"]),
                self.ticket("UI-07", "R-OTHER", status="in-progress"),
                self.ticket("EXP-50", "R-FALLBACK"),
            ],
        }
        self.request = {
            "schema_version": replan.REQUEST, "project_id": "field-slate",
            "native_revision": "r31", "target_revision": "r32", "changes": [],
        }

    def ticket(self, key, requirement, **fields):
        return {
            "id": key, "kind": "story", "title": key, "parent": "E-EXP", "status": "planned",
            "requirement_ids": [requirement], "acceptance": self.requirements[requirement], **fields,
        }

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def sha(self, raw):
        return hashlib.sha256(raw).hexdigest()

    def pin(self, name):
        return {"path": name, "sha256": self.sha((self.root / name).read_bytes())}

    def prepare(self):
        self.write("tickets.json", self.projection)
        self.request["projection_sha256"] = self.pin("tickets.json")["sha256"]
        self.write("replan.json", self.request)

    def change(self, action, *requirements, **fields):
        self.request["changes"].append({
            "action": action, "rationale": "Update the export backlog after requirements review.",
            "sources": [
                {**self.pin("requirements.json"), "requirement_id": key,
                 "excerpt": self.requirements[key]} for key in requirements
            ], **fields,
        })

    def build(self):
        self.prepare()
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        try:
            return replan.build_plan(self.root, "tickets.json", "replan.json")
        finally:
            self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)

    def test_plan_creates_splits_retires_and_exposes_affected_readiness(self):
        self.change("create", "R-NEW", ticket=self.ticket("EXP-13", "R-NEW"))
        self.change("split", "R-CSV", ticket_id="EXP-30", tickets=[
            self.ticket("EXP-31", "R-CSV", depends_on=["EXP-13"]),
            self.ticket("EXP-32", "R-CSV", depends_on=["EXP-31"]),
        ])
        self.change("drop", "R-FALLBACK", ticket_id="EXP-50")
        plan = self.build()
        rows = replan.context.records(plan["target"], "tickets")
        original = replan.context.records(self.projection, "tickets")
        for key in ("EXP-12", "UI-07"):
            self.assertEqual(rows[key], original[key])
        self.assertEqual(rows["EXP-30"], {**original["EXP-30"], "status": "deferred"})
        self.assertEqual(rows["EXP-50"], {**original["EXP-50"], "status": "deferred"})
        self.assertEqual(rows["EXP-40"]["depends_on"], ["EXP-31", "EXP-32"])
        self.assertEqual(plan["target"]["replan_retirements"], [
            {"ticket_id": "EXP-30", "action": "split", "retired_in": "r32", "successors": ["EXP-31", "EXP-32"]},
            {"ticket_id": "EXP-50", "action": "drop", "retired_in": "r32", "successors": []},
        ])
        self.assertEqual(plan["target"]["native_owner_metadata"], self.projection["native_owner_metadata"])
        self.assertEqual(plan["target"]["replan_receipts"], self.projection["replan_receipts"])
        self.assertEqual(plan["projection"], self.pin("tickets.json"))
        self.assertEqual(plan["request"], self.pin("replan.json"))
        self.assertEqual(plan["readiness"]["ready_ticket_ids"], ["EXP-13"])
        self.assertEqual(plan["readiness"]["previously_supported_acceptance_needs_recheck"], ["EXP-12"])
        self.assertEqual(plan["readiness"]["unsupported_acceptance_claims"], ["EXP-12"])
        self.assertEqual(plan["coverage"]["unmapped_must_requirements"], [])
        states = {row["ticket_id"]: row["after"] for row in plan["readiness"]["affected_tickets"]}
        self.assertEqual(states["EXP-40"], "blocked")
        self.assertNotIn("UI-07", states)
        self.assertEqual(replan.build_plan(self.root, "tickets.json", "replan.json"), plan)

    def test_replace_requires_linked_sources_and_preserves_downstream_barrier(self):
        self.change("replace", "R-CSV", ticket_id="EXP-30", ticket=self.ticket("EXP-33", "R-CSV"))
        plan = self.build()
        self.assertEqual(plan["rewired_dependencies"], [{
            "ticket_id": "EXP-40", "before": ["EXP-30"], "after": ["EXP-33"],
        }])
        self.assertEqual(plan["readiness"]["ready_ticket_ids"], ["EXP-33"])
        self.request["changes"][0]["sources"][0]["excerpt"] = "Independent scheduling continues."
        with self.assertRaisesRegex(replan.context.ContextError, "absent from the named requirement"):
            self.build()

    def test_does_not_drop_live_prerequisite_or_mandatory_coverage(self):
        self.change("drop", "R-CSV", ticket_id="EXP-30")
        with self.assertRaisesRegex(replan.context.ContextError, "prerequisite of retained work"):
            self.build()
        self.request["changes"] = []
        self.change("drop", "R-UI", ticket_id="EXP-40")
        with self.assertRaisesRegex(replan.context.ContextError, "coverage regressed: R-UI"):
            self.build()

    def test_refuses_direct_and_indirect_mutation_of_active_or_accepted_work(self):
        self.change("drop", "R-HIST", ticket_id="EXP-12")
        with self.assertRaisesRegex(replan.context.ContextError, "only a planned leaf"):
            self.build()
        self.request["changes"] = []
        self.change("replace", "R-CSV", ticket_id="EXP-30", ticket=self.ticket("EXP-33", "R-CSV"))
        replan.context.records(self.projection, "tickets")["UI-07"]["depends_on"] = ["EXP-40"]
        with self.assertRaisesRegex(replan.context.ContextError, "prerequisite of active or accepted work: UI-07"):
            self.build()

    def test_refuses_implicit_cycle_and_fabricated_acceptance(self):
        self.change("replace", "R-CSV", ticket_id="EXP-30",
                    ticket=self.ticket("EXP-33", "R-CSV", depends_on=["EXP-40"]))
        with self.assertRaisesRegex(replan.context.ContextError, "cyclic ticket dependencies"):
            self.build()
        self.request["changes"][0]["ticket"]["status"] = "accepted"
        with self.assertRaisesRegex(replan.context.ContextError, "new ticket must be planned"):
            self.build()
        self.request["changes"][0]["ticket"]["evidence"] = [self.pin("export-receipt.json")]
        with self.assertRaisesRegex(replan.context.ContextError, "new tickets allow only planning"):
            self.build()

    def test_cli_hashes_exact_plan_and_blocks_digest_drift(self):
        self.change("create", "R-NEW", ticket=self.ticket("EXP-13", "R-NEW"))
        self.prepare()
        argv = [sys.executable, "-B", str(SCRIPTS / "ticket_replan_plan.py"), "--root",
                str(self.root), "--projection", "tickets.json", "--request", "replan.json"]
        good = subprocess.run(argv, text=True, capture_output=True, timeout=10)
        self.assertEqual(good.returncode, 0, good.stderr)
        package = json.loads(good.stdout)
        self.assertEqual(package["plan_sha256"], self.sha(replan.context.canonical(package["plan"])))
        (self.root / "tickets.json").write_bytes((self.root / "tickets.json").read_bytes() + b"\n")
        stale = subprocess.run(argv, text=True, capture_output=True, timeout=10)
        self.assertEqual(stale.returncode, 2)
        self.assertIn("baseline mismatch", stale.stderr)


if __name__ == "__main__":
    unittest.main()
