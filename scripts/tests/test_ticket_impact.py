#!/usr/bin/env python3
"""Exercise a change to the implementation roadmap through the public CLI."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "ticket_impact.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(root, path):
    return {"path": path, "sha256": sha((root / path).read_bytes())}


def write(root, path, data, indent=2):
    (root / path).write_text(json.dumps(data, indent=indent), encoding="utf-8")


def add_receipt(root, projection, ticket, subject):
    path = f"{ticket['id']}-review.json"
    write(root, path, {
        "schema_version": "atelier.ticket-acceptance/1",
        "project_id": projection["project_id"],
        "native_revision": projection["native_revision"],
        "ticket_id": ticket["id"],
        "criterion_sha256": sha(ticket["acceptance"].encode("utf-8")),
        "subject": pin(root, subject),
    })
    ticket["evidence"] = [pin(root, path)]


class TicketImpactTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.before = self.make_revision(self.root / "before", updated=False)
        self.after = self.make_revision(self.root / "after", updated=True)

    def make_revision(self, root, *, updated):
        root.mkdir()
        lease = "Only one agent owns a write lease for a worktree."
        if updated:
            lease += " A superseded lease must never write after reassignment."
        write(root, "requirements.json", {"requirements": [
            {"id": "R-LEASE", "text": lease},
            {"id": "R-RETURN", "text": "A cold receiver continues accepted work.",
             "dependencies": ["R-LEASE"]},
            {"id": "R-ICON", "text": "Keep the installed role icon."},
            {"id": "R-DOC", "text": "Document the existing Codex startup command."},
            {"id": "R-RENEW" if updated else "R-EXPORT",
             "text": "Record lease renewal." if updated else "Export archived handoff."},
        ]})
        tickets = [
            {"id": "I-CONT", "title": "Parallel work and continuity", "kind": "initiative",
             "status": "planned"},
            {"id": "E-LEASE", "title": "Isolate parallel writes", "kind": "epic",
             "status": "planned", "parent": "I-CONT"},
            {"id": "S-LEASE", "title": "Hold a worktree write lease", "kind": "story",
             "status": "accepted", "parent": "E-LEASE", "requirement_ids": ["R-LEASE"],
             "acceptance": "The repository has only one writer."},
            {"id": "S-FORM", "title": "Explain how blocked agents can recover in the guide",
             "kind": "story", "status": "planned", "parent": "E-LEASE",
             "requirement_ids": ["R-DOC"]},
            {"id": "E-RETURN", "title": "Resume an independent session", "kind": "epic",
             "status": "planned", "parent": "I-CONT", "depends_on": ["E-LEASE"]},
            {"id": "S-RETURN", "title": "Recover the accepted decision", "kind": "story",
             "status": "planned", "parent": "E-RETURN", "requirement_ids": ["R-RETURN"]},
            {"id": "S-RESTART", "title": "Keep help for interrupted work",
             "kind": "story", "status": "planned", "parent": "E-RETURN",
             "requirement_ids": ["R-DOC"]},
            {"id": "B-ICON", "title": "Preserve the established role artwork", "kind": "bug",
             "status": "planned", "requirement_ids": ["R-ICON"]},
            {"id": "SP-RENEW" if updated else "SP-EXPORT", "title": "Explore audit options",
             "kind": "spike", "status": "planned", "requirement_ids": [
                 "R-RENEW" if updated else "R-EXPORT"
             ]},
        ]
        projection = self.projection(root, tickets, "worktree-r04" if updated else "worktree-r03")
        proof = root / "lease-observation.txt"
        proof.write_text("A single writer acquired the lease.\n", encoding="utf-8")
        if not updated:
            add_receipt(root, projection, tickets[2], proof.name)
        else:
            historical = (self.before / "S-LEASE-review.json").read_bytes()
            (root / "S-LEASE-review.json").write_bytes(historical)
            tickets[2]["evidence"] = [pin(root, "S-LEASE-review.json")]
        guide = root / "recovery-review.md"
        guide.write_text("The guide documents the Codex recovery command.\n", encoding="utf-8")
        tickets[3]["evidence"] = [pin(root, guide.name)]
        stale = root / "icon-review.txt"
        stale.write_text("Original installation proof.\n", encoding="utf-8")
        tickets[7]["evidence"] = [pin(root, stale.name)]
        stale.write_text("Proof artifact changed since its pin.\n", encoding="utf-8")
        write(root, "tickets.json", projection)
        return root

    def projection(self, root, tickets, revision):
        return {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "codex-delivery-roadmap",
            "native_revision": revision,
            "requirement_sources": [pin(root, "requirements.json")],
            "tickets": tickets,
        }

    def inventory(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def cli(self, *args, expected=0):
        old = self.inventory()
        process = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                                 text=True, capture_output=True, check=False)
        self.assertEqual(expected, process.returncode, process.stderr)
        self.assertEqual(old, self.inventory(), "reporting mutated project or historical proof")
        return json.loads(process.stdout if expected == 0 else process.stderr)

    def capture(self, root, name):
        data = self.cli("capture", "--root", root, "--input", "tickets.json")
        write(self.root, name, data)
        return self.root / name

    def compare(self, before, after, *, before_sha=None, expected=0):
        return self.cli("compare", "--before", before, "--after", after,
                        "--before-sha256", before_sha or sha(before.read_bytes()),
                        "--after-sha256", sha(after.read_bytes()), expected=expected)

    def test_mid_sprint_change_tracks_scope_and_preserves_historical_reviews(self):
        old = self.capture(self.before, "before-impact.json")
        new = self.capture(self.after, "after-impact.json")
        report = self.compare(old, new)
        changed = {row["id"]: row["change"] for row in report["requirement_changes"]}
        self.assertEqual({"R-LEASE": "changed", "R-EXPORT": "removed", "R-RENEW": "added"}, changed)
        self.assertEqual(["requirements.json"],
                         [item["path"] for item in report["requirement_source_drift"]])
        affected = {row["ticket_id"]: row for row in report["affected_tickets"]}
        self.assertEqual({"I-CONT", "E-LEASE", "E-RETURN", "S-LEASE", "S-RETURN", "S-RESTART",
                          "SP-EXPORT", "SP-RENEW"}, set(affected))
        self.assertIn({"code": "direct-requirement", "id": "R-LEASE"}, affected["S-LEASE"]["reasons"])
        self.assertIn({"code": "requirement-prerequisite", "id": "R-LEASE"},
                      affected["S-RETURN"]["reasons"])
        self.assertIn({"code": "ticket-prerequisite", "id": "E-LEASE"},
                      affected["S-RESTART"]["reasons"])
        self.assertIn({"code": "group-member", "id": "S-LEASE"}, affected["E-LEASE"]["reasons"])
        lease = affected["S-LEASE"]
        self.assertTrue(lease["review_prior_acceptance"])
        self.assertEqual("supported", lease["prior_acceptance_status"])
        review, = lease["prior_evidence_requiring_review"]
        self.assertEqual("verified", review["prior"]["status"])
        self.assertEqual("same-declared-pin", review["current_relation"])
        self.assertEqual("binding-mismatch", review["current"]["status"])
        self.assertEqual("review-required", review["disposition"])
        self.assertFalse(report["acceptance_reissued"])
        self.assertFalse(report["authority_authenticated"])
        self.assertEqual(["B-ICON", "S-FORM"], report["other_ticket_ids"])
        self.assertIn(("B-ICON", "stale"),
                      [(row["ticket_id"], row["status"]) for row in report["current_evidence_warnings"]])

    def test_group_criterion_change_rechecks_member_and_its_prior_artifact(self):
        old = self.capture(self.before, "before-impact.json")
        current = json.loads((self.before / "tickets.json").read_bytes())
        epic = next(row for row in current["tickets"] if row["id"] == "E-LEASE")
        epic["acceptance"] = "Review recovery for lock contention."
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(old, new)
        self.assertTrue(report["native_revision_reused_with_source_changes"])
        self.assertEqual([], report["requirement_changes"])
        affected = {row["ticket_id"]: row for row in report["affected_tickets"]}
        self.assertIn({"code": "group-contract", "id": "E-LEASE"}, affected["S-FORM"]["reasons"])
        review, = affected["S-FORM"]["prior_evidence_requiring_review"]
        self.assertEqual("recovery-review.md", review["prior"]["path"])
        self.assertEqual("verified", review["current"]["status"])

    def test_new_group_prerequisite_rechecks_unchanged_work_ticket(self):
        current = json.loads((self.before / "tickets.json").read_bytes())
        epic = {"id": "E-EXPORT", "title": "Archive handoff evidence", "kind": "epic",
                "status": "planned", "parent": "I-CONT"}
        current["tickets"].extend([epic, {
            "id": "UI-07", "title": "Show archive status", "kind": "bug", "status": "planned",
            "requirement_ids": ["R-ICON"],
        }])
        story = next(row for row in current["tickets"] if row["id"] == "SP-EXPORT")
        story["parent"] = epic["id"]
        (self.before / "archive-observation.txt").write_text("Archive verified.", encoding="utf-8")
        story["evidence"] = [pin(self.before, "archive-observation.txt")]
        write(self.before, "tickets.json", current)
        old = self.capture(self.before, "before-impact.json")
        epic["depends_on"] = ["UI-07"]
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(old, new)
        affected = {row["ticket_id"]: row for row in report["affected_tickets"]}
        self.assertEqual({"I-CONT", "E-EXPORT", "SP-EXPORT"}, set(affected))
        self.assertIn({"code": "effective-prerequisite-changed", "id": "UI-07"},
                      affected["SP-EXPORT"]["reasons"])
        self.assertIsNone(affected["SP-EXPORT"]["plan_change"])
        review, = affected["SP-EXPORT"]["prior_evidence_requiring_review"]
        self.assertEqual("archive-observation.txt", review["prior"]["path"])
        self.assertIn("UI-07", report["other_ticket_ids"])
        self.assertIn("S-FORM", report["other_ticket_ids"])

    def test_ancestor_move_rechecks_changed_ownership_and_hold(self):
        current = json.loads((self.before / "tickets.json").read_bytes())
        current["tickets"].append({"id": "I-HOLD", "kind": "initiative", "status": "deferred",
                                   "title": "Work awaiting a release decision"})
        write(self.before, "tickets.json", current)
        old = self.capture(self.before, "before-impact.json")
        epic = next(row for row in current["tickets"] if row["id"] == "E-LEASE")
        epic["parent"] = "I-HOLD"
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(old, new)
        affected = {row["ticket_id"]: row for row in report["affected_tickets"]}
        reasons = affected["S-LEASE"]["reasons"]
        self.assertIn({"code": "ancestor-hold-changed", "id": "I-HOLD"}, reasons)
        self.assertIn({"code": "ancestor-path-changed", "id": "I-HOLD"}, reasons)
        self.assertIn({"code": "ancestor-path-changed", "id": "I-CONT"}, reasons)
        self.assertIn("B-ICON", report["other_ticket_ids"])

    def test_current_unsupported_acceptance_includes_removed_receipt(self):
        old = self.capture(self.before, "before-impact.json")
        current = json.loads((self.before / "tickets.json").read_bytes())
        story = next(row for row in current["tickets"] if row["id"] == "S-LEASE")
        del story["evidence"]
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(old, new)
        self.assertEqual(["S-LEASE"], report["current_unsupported_acceptance_claims"])
        self.assertEqual([], report["affected_tickets"])

    def test_registry_formatting_drift_leaves_membership_and_proofs_alone(self):
        old = self.capture(self.before, "before-impact.json")
        rows = json.loads((self.before / "requirements.json").read_bytes())
        write(self.before, "requirements.json", rows, indent=4)
        current = json.loads((self.before / "tickets.json").read_bytes())
        current["requirement_sources"] = [pin(self.before, "requirements.json")]
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(old, new)
        self.assertEqual(1, len(report["requirement_source_drift"]))
        self.assertEqual([], report["requirement_changes"])
        self.assertEqual([], report["affected_tickets"])

    def test_moved_requirements_recheck_linked_tickets(self):
        baseline = self.capture(self.before, "before-impact.json")
        (self.before / "requirements.json").rename(self.before / "roadmap.json")
        current = json.loads((self.before / "tickets.json").read_bytes())
        current["requirement_sources"] = [pin(self.before, "roadmap.json")]
        write(self.before, "tickets.json", current)
        new = self.capture(self.before, "after-impact.json")
        report = self.compare(baseline, new)
        self.assertEqual({"source-moved"}, {row["change"] for row in report["requirement_changes"]})
        self.assertEqual({"added", "removed"}, {row["change"] for row in report["requirement_source_drift"]})
        self.assertEqual([], report["other_ticket_ids"])

    def test_old_snapshot_compares_against_marker_only_retirement_and_restoration(self):
        current = json.loads((self.before / "tickets.json").read_bytes())
        work = next(row for row in current["tickets"] if row["id"] == "S-FORM")
        work["status"] = "deferred"
        write(self.before, "tickets.json", current)
        baseline = self.capture(self.before, "before-impact.json")
        self.assertNotIn("replan_retirements", json.loads(baseline.read_bytes()))

        marker = {"ticket_id": "S-FORM", "action": "drop", "retired_in": "worktree-r04", "successors": []}
        current["replan_retirements"] = [marker]
        write(self.before, "tickets.json", current)
        retired = self.capture(self.before, "after-impact.json")
        self.assertEqual(json.loads(retired.read_bytes())["replan_retirements"], [marker])
        report = self.compare(baseline, retired)
        affected = {row["ticket_id"]: row for row in report["affected_tickets"]}
        self.assertEqual(affected["S-FORM"]["plan_change"], {
            "change": "changed", "fields": ["replan_retirement"],
            "retirement": {"before": None, "after": marker},
        })
        self.assertIn({"code": "ticket-retirement-changed", "id": "S-FORM"}, affected["S-FORM"]["reasons"])
        self.assertIn("E-LEASE", affected)
        self.assertIn("S-RETURN", affected)
        self.assertIn("B-ICON", report["other_ticket_ids"])

        reopened = self.compare(retired, baseline)
        restored = next(row for row in reopened["affected_tickets"] if row["ticket_id"] == "S-FORM")
        self.assertEqual(restored["plan_change"]["retirement"], {"before": marker, "after": None})

    def test_capture_rejects_stale_registry_pin(self):
        (self.after / "requirements.json").write_text("{}", encoding="utf-8")
        failure = self.cli("capture", "--root", self.after, "--input", "tickets.json", expected=2)
        self.assertIn("SOURCE_DRIFT: requirements.json", failure["error"])

    def test_compare_rejects_snapshot_drift_and_other_project(self):
        old = self.capture(self.before, "before-impact.json")
        new = self.capture(self.after, "after-impact.json")
        failure = self.compare(old, new, before_sha="0" * 64, expected=2)
        self.assertIn("SNAPSHOT_DRIFT", failure["error"])
        unrelated = json.loads((self.after / "tickets.json").read_bytes())
        unrelated["project_id"] = "another-project"
        write(self.after, "tickets.json", unrelated)
        other = self.capture(self.after, "other-impact.json")
        self.assertIn("project mismatch", self.compare(old, other, expected=2)["error"])


if __name__ == "__main__":
    unittest.main()
