#!/usr/bin/env python3
"""Exercise ticket reporting through its public CLI against isolated project files."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_tree.py"


class TicketTreeTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.write("requirements.json", {
            "requirements": [
                {"id": "R-HOUR", "priority": "must", "text": "A booking records the local time."},
                {"id": "R-DOOR", "priority": "must", "text": "The door shows the booking.",
                 "dependencies": ["R-HOUR"]},
                {"id": "R-FREE", "priority": "must", "text": "A reviewed booking can be freed."},
                {"id": "R-LATER", "priority": "must", "text": "The operator can export audits."},
            ],
        })
        (self.root / "check-in-proof.txt").write_text("Door displays room 2 at 10:00.")
        (self.root / "check-in-review.txt").write_text("Reviewed the check-in with the office manager.")
        self.data = {
            "schema_version": "atelier.ticket-projection/1", "project_id": "room-booker",
            "native_revision": "room-booker-r17",
            "requirement_sources": [self.pin("requirements.json")],
            "tickets": [
                {"id": "I-DOOR", "kind": "initiative", "title": "Self-service check-in",
                 "status": "planned"},
                {"id": "I-NOSHOW", "kind": "initiative", "title": "Reduce unused rooms",
                 "status": "planned"},
                {"id": "E-DOOR", "kind": "epic", "title": "Install room tablets",
                 "status": "accepted", "parent": "I-DOOR", "acceptance": "Review every door.",
                 },
                {"id": "E-NOSHOW", "kind": "epic", "title": "Release unused slots",
                 "status": "planned", "parent": "I-NOSHOW", "depends_on": ["E-DOOR"]},
                {"id": "S-FREE", "kind": "story", "title": "Show the release button",
                 "status": "planned", "parent": "E-NOSHOW", "requirement_ids": ["R-FREE"],
                 "acceptance": "A user releases an unused room without losing a current booking."},
                {"id": "S-DOOR", "kind": "story", "title": "Show the booked room",
                 "status": "accepted", "parent": "E-DOOR", "requirement_ids": ["R-DOOR"],
                 "acceptance": "Read room and time on the tablet.",
                 },
                {"id": "S-UPDATE", "kind": "story", "title": "Refresh the freed slot",
                 "status": "planned", "parent": "E-NOSHOW", "depends_on": ["S-FREE"],
                 "requirement_ids": ["R-FREE"], "acceptance": "The slot becomes available."},
                {"id": "B-CLOCK", "kind": "bug", "title": "The clock moves an hour",
                 "status": "planned"},
                {"id": "I-AUDIT", "kind": "initiative", "title": "Audit export",
                 "status": "deferred", "parent": "I-NOSHOW"},
                {"id": "SP-AUDIT", "kind": "spike", "title": "Check export formats",
                 "status": "planned", "parent": "I-AUDIT", "requirement_ids": ["R-LATER"],
                 "acceptance": "Report the two formats accepted by the operator."},
            ],
        }

        self.set_receipt("S-DOOR", "check-in-proof.txt")
        self.set_receipt("E-DOOR", "check-in-review.txt")

    def set_receipt(self, key, subject, **overrides):
        ticket = self.record(key)
        receipt = f"{key}-acceptance.json"
        self.write(receipt, {
            "schema_version": "atelier.ticket-acceptance/1",
            "project_id": self.data["project_id"],
            "native_revision": self.data["native_revision"],
            "ticket_id": key,
            "criterion_sha256": hashlib.sha256(ticket["acceptance"].encode("utf-8")).hexdigest(),
            "subject": self.pin(subject),
            **overrides,
        })
        ticket["evidence"] = [self.pin(receipt)]

    def write(self, ref, data):
        (self.root / ref).write_text(json.dumps(data), encoding="utf-8")

    def pin(self, ref):
        return {"path": ref, "sha256": hashlib.sha256((self.root / ref).read_bytes()).hexdigest()}

    def record(self, key):
        return next(row for row in self.data["tickets"] if row["id"] == key)

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file() and not p.is_symlink()}

    def run_cli(self, operation="board", *, expected=0, complete=False, selectors=()):
        self.write("tickets.json", self.data)
        before = self.snapshot()
        arguments = [sys.executable, "-B", str(SCRIPT), operation, "--root", str(self.root),
                     "--input", "tickets.json"]
        if complete:
            arguments.append("--require-complete")
        for selector in selectors:
            arguments.extend(("--select", selector))
        result = subprocess.run(
            arguments,
            capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        self.assertEqual(self.snapshot(), before)
        return json.loads(result.stdout or result.stderr)

    def test_reports_room_booking_work_from_multiple_initiatives(self):
        board = self.run_cli("validate")
        self.assertEqual(board["roots"], ["I-DOOR", "I-NOSHOW", "B-CLOCK"])
        self.assertEqual(board["board"]["ready"], ["S-FREE"])
        self.assertEqual(board["board"]["needs-refinement"], ["B-CLOCK"])
        self.assertEqual(board["board"]["accepted"], ["S-DOOR", "E-DOOR"])
        self.assertEqual(board["board"]["deferred"], ["I-AUDIT"])
        self.assertEqual(board["unmapped_must_requirements"], [])
        self.assertEqual(board["deferred_only_must_requirements"], ["R-LATER"])
        self.assertEqual(self.run_cli("validate", complete=True), board)
        self.assertLess(board["evaluation_order"].index("E-DOOR"),
                        board["evaluation_order"].index("S-FREE"))
        indexed = {row["id"]: row for row in board["tickets"]}
        self.assertEqual(indexed["S-DOOR"]["requirement_closure"], ["R-DOOR", "R-HOUR"])
        self.assertEqual(indexed["S-FREE"]["effective_prerequisites"], ["E-DOOR"])
        self.assertEqual(indexed["S-UPDATE"]["blockers"],
                         [{"code": "prerequisite-open", "ticket": "S-FREE"}])
        self.assertEqual(indexed["SP-AUDIT"]["blockers"],
                         [{"code": "ancestor-deferred", "ticket": "I-AUDIT"}])
        self.assertEqual(board["projection"], self.pin("tickets.json"))
        self.assertFalse(board["authority_authenticated"])
        self.assertFalse(board["functional_outcome_verified"])
        self.assertEqual(self.run_cli("validate"), board)

    def test_preserves_unsupported_acceptance_without_unlocking_dependencies(self):
        (self.root / "check-in-proof.txt").unlink()
        board = self.run_cli("validate", expected=2)
        self.assertEqual(board["unsupported_acceptance_claims"], ["S-DOOR", "E-DOOR"])
        item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
        self.assertEqual(item["recorded_status"], "accepted")
        self.assertEqual(item["board_state"], "blocked")
        self.assertEqual(item["blockers"],
                         [{"code": "evidence-subject-unavailable", "path": "S-DOOR-acceptance.json"}])
        self.assertNotIn("S-FREE", board["board"]["ready"])
        self.assertEqual(self.run_cli(), board)

    def test_an_explicit_group_block_applies_to_its_open_children(self):
        self.record("E-NOSHOW")["status"] = "blocked"
        self.record("E-NOSHOW")["blocked_reason"] = "Waiting for the access window."
        board = self.run_cli("validate")
        item = next(row for row in board["tickets"] if row["id"] == "S-FREE")
        self.assertEqual(item["recorded_status"], "planned")
        self.assertEqual(item["board_state"], "blocked")
        self.assertEqual(item["blockers"], [{
            "code": "ancestor-blocked", "ticket": "E-NOSHOW",
            "reason": "Waiting for the access window.",
        }])

    def test_rejects_stale_registry_and_reports_modified_evidence(self):
        proof = self.root / "check-in-proof.txt"
        proof.write_text("Different results.")
        board = self.run_cli("validate", expected=2)
        item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
        self.assertEqual(item["blockers"], [
            {"code": "evidence-subject-stale", "path": "S-DOOR-acceptance.json"},
        ])
        (self.root / "requirements.json").write_text('{"requirements": []}')
        error = self.run_cli(expected=2)
        self.assertEqual(error["error"], "SOURCE_DRIFT: requirements.json")

    def test_rejects_orphan_and_cycle_through_epic_completion(self):
        self.record("S-FREE")["parent"] = "E-MISSING"
        self.assertEqual(self.run_cli(expected=2)["error"], "unknown parent: S-FREE")
        self.record("S-FREE")["parent"] = "E-NOSHOW"
        self.record("S-DOOR")["depends_on"] = ["S-FREE"]
        self.assertEqual(self.run_cli(expected=2)["error"],
                         "cyclic ticket dependencies or group completion")

    def test_missing_criterion_or_requirement_cannot_be_accepted(self):
        self.record("S-DOOR").pop("acceptance")
        self.record("S-DOOR").pop("requirement_ids")
        board = self.run_cli("validate", expected=2)
        item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
        self.assertEqual({blocker["code"] for blocker in item["acceptance_blockers"]}, {
            "evidence-binding-mismatch", "missing-acceptance-criterion", "missing-requirement-link",
        })

    def test_complete_validation_requires_leaf_coverage_for_each_active_must(self):
        self.record("SP-AUDIT").pop("requirement_ids")
        self.record("I-NOSHOW")["requirement_ids"] = ["R-LATER"]
        partial = self.run_cli("validate")
        self.assertEqual(partial["unmapped_must_requirements"], ["R-LATER"])
        self.assertEqual(partial["deferred_only_must_requirements"], [])
        self.assertEqual(self.run_cli("validate", complete=True, expected=2), partial)

    def test_unrelated_pinned_artifact_cannot_unlock_work(self):
        unrelated = "unrelated.txt"
        (self.root / unrelated).write_text("Reviewed a different task.")
        self.record("S-DOOR")["evidence"] = [self.pin(unrelated)]
        board = self.run_cli("validate", expected=2)
        item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
        self.assertEqual(item["recorded_status"], "accepted")
        self.assertEqual(item["acceptance_status"], "unsupported")
        self.assertEqual(item["acceptance_blockers"], [{"code": "missing-bound-acceptance-evidence"}])
        self.assertNotIn("S-FREE", board["board"]["ready"])

    def test_bound_evidence_rejects_wrong_ticket_project_revision_or_criterion(self):
        for field, bad in (
            ("ticket_id", "S-FREE"), ("project_id", "other-project"),
            ("native_revision", "room-booker-r16"), ("criterion_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                self.set_receipt("S-DOOR", "check-in-proof.txt", **{field: bad})
                board = self.run_cli("validate", expected=2)
                item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
                self.assertEqual(item["acceptance_blockers"], [
                    {"code": "evidence-binding-mismatch", "path": "S-DOOR-acceptance.json"},
                ])
                self.assertNotIn("S-FREE", board["board"]["ready"])

    def test_deferred_ancestor_holds_accepted_children_without_erasing_support(self):
        self.record("I-DOOR")["status"] = "deferred"
        self.record("B-CLOCK").update(
            depends_on=["S-DOOR"], acceptance="Show the correct booking time.",
            requirement_ids=["R-DOOR"],
        )
        board = self.run_cli("validate")
        indexed = {row["id"]: row for row in board["tickets"]}
        self.assertEqual(board["unsupported_acceptance_claims"], [])
        for key in ("S-DOOR", "E-DOOR"):
            self.assertEqual(indexed[key]["acceptance_status"], "supported")
            self.assertEqual(indexed[key]["board_state"], "accepted")
            self.assertEqual(indexed[key]["execution_disposition"], "held")
        self.assertEqual(indexed["S-DOOR"]["blockers"], [
            {"code": "ancestor-deferred", "ticket": "I-DOOR"},
        ])
        self.assertEqual(indexed["B-CLOCK"]["board_state"], "blocked")
        self.assertEqual(indexed["B-CLOCK"]["blockers"], [
            {"code": "prerequisite-held", "ticket": "S-DOOR"},
        ])
        self.assertEqual(indexed["S-FREE"]["blockers"], [
            {"code": "prerequisite-held", "ticket": "E-DOOR"},
        ])

    def test_acceptance_subject_cannot_be_a_requirement_even_under_a_new_path(self):
        subject = self.root / "looks-like-proof.json"
        subject.write_bytes((self.root / "requirements.json").read_bytes())
        self.set_receipt("S-DOOR", subject.name)
        board = self.run_cli("validate", expected=2)
        item = next(row for row in board["tickets"] if row["id"] == "S-DOOR")
        self.assertEqual(item["acceptance_blockers"], [
            {"code": "evidence-invalid-subject", "path": "S-DOOR-acceptance.json"},
        ])

    def test_rejects_unsafe_source_and_refuses_to_use_registry_as_evidence(self):
        (self.root / "linked.json").symlink_to(self.root / "requirements.json")
        real = self.pin("requirements.json")
        self.data["requirement_sources"] = [{**real, "path": "linked.json"}]
        self.assertEqual(self.run_cli(expected=2)["error"], "linked input/output path rejected")
        self.data["requirement_sources"] = [real]
        self.record("S-DOOR")["evidence"] = [real]
        self.assertEqual(self.run_cli(expected=2)["error"],
                         "evidence cannot be the projection or a requirement source")

    def test_sprint_expands_groups_and_separates_internal_and_external_gates(self):
        self.data["tickets"].append({
            "id": "SP-TIME", "kind": "spike", "title": "Confirm clock data sources",
            "status": "planned", "requirement_ids": ["R-HOUR"], "acceptance": "Choose a clock source.",
        })
        self.record("B-CLOCK").update(
            depends_on=["SP-TIME"],
            acceptance="Booking time is stable across time changes.",
            requirement_ids=["R-HOUR"],
        )
        selectors = ["E-NOSHOW", "S-FREE", "I-AUDIT", "B-CLOCK", "S-DOOR"]
        sprint = self.run_cli("sprint", selectors=selectors)
        self.assertEqual(sprint["schema_version"], "atelier.ticket-sprint/1")
        self.assertEqual(sprint["selectors"], selectors)
        self.assertEqual(sprint["sprint"], {
            "ready": ["S-FREE"], "held": ["SP-AUDIT"], "blocked": ["B-CLOCK"],
            "future": ["S-UPDATE"], "accepted": ["S-DOOR"],
        })
        selected = {row["id"]: row for row in sprint["tickets"]}
        self.assertEqual(len(selected), len(sprint["tickets"]))
        self.assertEqual(
            {(gate["ticket"], gate["scope"], gate["satisfied"])
             for gate in selected["S-UPDATE"]["prerequisites"]},
            {("E-DOOR", "inside", True), ("S-FREE", "inside", False)},
        )
        self.assertEqual(selected["B-CLOCK"]["prerequisites"], [{
            "ticket": "SP-TIME", "scope": "outside", "satisfied": False,
            "execution_disposition": "open", "outside_selected_work_count": 1,
        }])
        self.assertEqual(self.run_cli("sprint", selectors=selectors), sprint)

    def test_retired_leaf_keeps_history_without_occupying_group_completion_or_sprint(self):
        self.data["tickets"].append({
            "id": "S-OBSOLETE", "kind": "story", "parent": "E-DOOR",
            "title": "Obsolete planning path", "status": "deferred", "requirement_ids": ["R-DOOR"],
            "acceptance": "Review the obsolete path.",
            "evidence": [self.pin("check-in-proof.txt")],
        })
        ordinary = self.run_cli()
        self.assertNotIn("E-DOOR", ordinary["board"]["accepted"])
        self.assertIn("S-OBSOLETE", self.run_cli("sprint", selectors=["E-DOOR"])["sprint"]["held"])

        retirement = {
            "ticket_id": "S-OBSOLETE", "action": "drop",
            "retired_in": self.data["native_revision"], "successors": [],
        }
        self.data["replan_retirements"] = [retirement]
        board = self.run_cli("validate", complete=True)
        indexed = {row["id"]: row for row in board["tickets"]}
        self.assertIn("E-DOOR", board["board"]["accepted"])
        self.assertEqual(indexed["E-DOOR"]["children"], ["S-DOOR", "S-OBSOLETE"])
        self.assertEqual(indexed["E-DOOR"]["completion_children"], ["S-DOOR"])
        self.assertEqual(indexed["S-OBSOLETE"]["parent"], "E-DOOR")
        self.assertEqual(indexed["S-OBSOLETE"]["replan_retirement"], retirement)
        self.assertEqual(indexed["S-OBSOLETE"]["evidence"][0]["status"], "verified")
        sprint = self.run_cli("sprint", selectors=["E-DOOR", "E-NOSHOW"])
        self.assertEqual(sprint["sprint"]["accepted"], ["S-DOOR"])
        self.assertEqual(sprint["sprint"]["held"], [])
        self.assertIn("S-FREE", sprint["sprint"]["ready"])
        self.assertEqual(self.run_cli("sprint", selectors=["S-OBSOLETE"], expected=2)["error"],
                         "sprint selector has no leaf work: S-OBSOLETE")

        self.record("S-OBSOLETE")["status"] = "in-progress"
        self.assertIn("retirement must identify one retained deferred leaf",
                      self.run_cli(expected=2)["error"])

    def test_sprint_keeps_held_historical_acceptance_from_unlocking_future_work(self):
        self.record("I-DOOR")["status"] = "deferred"
        sprint = self.run_cli("sprint", selectors=["I-DOOR", "E-NOSHOW"])
        selected = {row["id"]: row for row in sprint["tickets"]}
        self.assertEqual(sprint["sprint"]["accepted"], ["S-DOOR"])
        self.assertEqual(selected["S-DOOR"]["execution_disposition"], "held")
        self.assertFalse(selected["S-FREE"]["prerequisites"][0]["satisfied"])
        self.assertIn("S-FREE", sprint["sprint"]["future"])
        self.assertNotIn("S-FREE", sprint["sprint"]["ready"])
        outside = self.run_cli("sprint", selectors=["E-NOSHOW"])
        self.assertEqual(outside["sprint"]["blocked"], ["S-FREE", "S-UPDATE"])

    def test_sprint_rejects_missing_unknown_duplicate_or_empty_group_selection(self):
        for selectors, reason in (
            ([], "select at least one ticket or group for the sprint"),
            (["NO-TICKET"], "unknown sprint selector: NO-TICKET"),
            (["B-CLOCK", "B-CLOCK"], "duplicate in sprint selectors"),
        ):
            with self.subTest(selectors=selectors):
                error = self.run_cli("sprint", selectors=selectors, expected=2)
                self.assertEqual(error, {"status": "invalid-sprint", "error": reason})
        self.data["tickets"].append({
            "id": "I-EMPTY", "kind": "initiative", "title": "Await scope", "status": "planned",
        })
        error = self.run_cli("sprint", selectors=["I-EMPTY"], expected=2)
        self.assertEqual(error["error"], "sprint selector has no leaf work: I-EMPTY")


if __name__ == "__main__":
    unittest.main()
