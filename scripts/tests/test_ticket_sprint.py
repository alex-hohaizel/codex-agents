#!/usr/bin/env python3
"""Sprint progress preserves the selected work while the backlog evolves."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_sprint.py"


class SprintPlanTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.write("requirements.json", {"requirements": [
            {"id": "REQ-ROOM", "priority": "must", "text": "A new room can be reserved."},
            {"id": "REQ-ACK", "priority": "must", "text": "The reservation has a durable confirmation."},
        ]})
        self.projection = {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "bookings",
            "native_revision": "r1",
            "requirement_sources": [self.pin("requirements.json")],
            "tickets": [
                {"id": "GOAL", "kind": "initiative", "status": "planned", "title": "Reserve space"},
                {"id": "RESERVE", "kind": "story", "parent": "GOAL", "status": "planned",
                 "title": "Reserve a room", "requirement_ids": ["REQ-ROOM"],
                 "acceptance": "Reserve an available room once."},
            ],
        }
        self.write("tickets.json", self.projection)

    def pin(self, name):
        return {"path": name, "sha256": sha256((self.root / name).read_bytes()).hexdigest()}

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def run_cli(self, command, *args, expected=0, projection="tickets.json"):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), command,
                                 "--root", str(self.root), "--projection", projection, *args],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return json.loads(result.stdout or result.stderr)

    def draft(self, *extra):
        return self.run_cli("plan", "--sprint-id", "sprint-01", "--goal", "Finish reservations",
                            "--starts-on", "2026-11-17", "--ends-on", "2026-11-30",
                            "--select", "GOAL", *extra)

    def status(self, ref="sprint-r1.json", *, expected=0, digest=None, projection="tickets.json"):
        return self.run_cli("status", "--sprint", ref,
                            "--sprint-sha256", digest or self.pin(ref)["sha256"],
                            expected=expected, projection=projection)

    def test_new_dependency_is_visible_without_moving_it_into_sprint(self):
        self.write("sprint-r1.json", self.draft())
        self.assertEqual(self.status()["current_view_of_recorded_members"]["sprint"]["ready"], ["RESERVE"])
        original = self.pin("sprint-r1.json")

        self.projection["native_revision"] = "r2"
        self.projection["tickets"][1]["depends_on"] = ["CONFIRM"]
        self.projection["tickets"].append(
            {"id": "CONFIRM", "kind": "story", "parent": "GOAL", "status": "planned",
             "title": "Retain confirmation", "requirement_ids": ["REQ-ACK"],
             "acceptance": "Read back a confirmation after restart."},
        )
        self.write("tickets.json", self.projection)
        current = self.status()
        self.assertEqual(current["status"], "scope-review-due")
        self.assertEqual(current["new_members_for_review"], ["CONFIRM"])
        selected = current["current_view_of_recorded_members"]["tickets"]
        self.assertEqual([row["id"] for row in selected], ["RESERVE"])
        self.assertEqual(selected[0]["prerequisites"][0]["scope"], "outside")
        self.assertEqual(selected[0]["sprint_state"], "blocked")

        revised = self.draft("--previous", original["path"], "--previous-sha256", original["sha256"])
        self.assertEqual(revised["previous"], original)
        self.assertEqual(revised["members"], ["CONFIRM", "RESERVE"])
        self.assertEqual(self.pin("sprint-r1.json"), original)

    def test_reused_revision_or_projection_does_not_hide_changed_scope(self):
        self.write("sprint-r1.json", self.draft())
        self.projection["tickets"][1]["acceptance"] = "Reserve three nearby rooms."
        self.write("tickets.json", self.projection)
        result = self.status()
        self.assertEqual(result["status"], "scope-review-due")
        self.assertEqual(result["changed_member_contracts"], ["RESERVE"])
        self.assertEqual(result["source_flags"], ["revision-reused-for-changed-projection"])
        self.projection["native_revision"] = "r2"
        self.write("other-tickets.json", self.projection)
        result = self.status(projection="other-tickets.json")
        self.assertEqual(result["status"], "scope-review-due")
        self.assertEqual(result["source_flags"], ["projection-path-changed"])

    def test_progress_can_change_without_reopening_unchanged_contracts(self):
        self.write("sprint-r1.json", self.draft())
        self.projection["native_revision"] = "r2"
        self.projection["tickets"][1]["status"] = "in-progress"
        self.write("tickets.json", self.projection)
        result = self.status()
        self.assertEqual(result["status"], "scope-current")
        self.assertEqual(result["current_view_of_recorded_members"]["sprint"]["held"], ["RESERVE"])

    def test_group_loss_remains_visible_and_a_changed_plan_is_rejected(self):
        self.write("sprint-r1.json", self.draft())
        prior = self.pin("sprint-r1.json")
        self.projection["tickets"].pop()
        self.write("tickets.json", self.projection)
        current = self.status()
        self.assertEqual(current["unavailable_selectors"], ["GOAL"])
        self.assertEqual(current["removed_or_retired"], ["RESERVE"])
        self.assertIsNone(current["current_view_of_recorded_members"])
        (self.root / "sprint-r1.json").write_text("{}")
        self.assertIn("SOURCE_DRIFT", self.status(expected=2, digest=prior["sha256"])["error"])


if __name__ == "__main__":
    unittest.main()
