"""Exercise exact inverse planning and applying a new revision through the local adapter."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_replan_correction as correction
import ticket_replan_plan as model
import ticket_replan_store as store

context, tree = model.context, model.tree


class TicketReplanCorrectionTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.projection = "tickets.json"
        self.requirement = "Keep the accepted export headers."
        self.save("requirements.json", {"requirements": [{"id": "RC", "text": self.requirement}]})
        self.baseline = {
            "schema_version": tree.PROJECTION, "project_id": "exports", "native_revision": "r1",
            "requirement_sources": [self.pin("requirements.json")], "custom": {"keep": "me"},
            "tickets": [
                {"id": "I", "title": "Exports", "kind": "initiative", "status": "planned"},
                self.ticket("T1"), self.ticket("T2", depends_on=["T1"]),
                self.ticket("T3", status="in-progress"),
            ],
        }
        for name in (self.projection, "baseline.json"):
            self.save(name, self.baseline)
        self.save("request.json", {
            "schema_version": model.REQUEST, "project_id": "exports", "native_revision": "r1",
            "projection_sha256": self.pin(self.projection)["sha256"], "target_revision": "r2",
            "changes": [{
                "action": "split", "ticket_id": "T1", "rationale": "Separate model and validation.",
                "sources": [{**self.pin("requirements.json"), "requirement_id": "RC",
                             "excerpt": self.requirement}],
                "tickets": [self.ticket("T11"), self.ticket("T12", depends_on=["T11"])],
            }],
        })
        self.original = model.build_plan(self.root, self.projection, "request.json")
        self.apply("request.json", self.original, "landed")
        self.dispatch = {
            "schema_version": correction.NO_DISPATCH, "status": "no-dispatch-observed",
            "project_id": "exports", "native_revision": "r2", "operation_id": "landed",
            "projection": self.pin(self.projection), "plan_sha256": store.plan_sha256(self.original),
            "authority_ref": "Fixture operator checked the only authorized dispatch channel",
        }
        self.save("no-dispatch.json", self.dispatch)
        self.request = {
            "schema_version": correction.REQUEST, "project_id": "exports", "native_revision": "r2",
            "projection_sha256": self.pin(self.projection)["sha256"], "target_revision": "r3",
            "undo_operation_id": "landed", "undo_plan_sha256": store.plan_sha256(self.original),
            "baseline": self.pin("baseline.json"), "no_dispatch": self.pin("no-dispatch.json"),
            "rationale": "Retain one implementation story before starting work.",
        }

    def save(self, name, record):
        (self.root / name).write_text(json.dumps(record), encoding="utf-8")

    def pin(self, name):
        return {"path": name, "sha256": context.digest((self.root / name).read_bytes())}

    def ticket(self, key, **extras):
        return {"id": key, "kind": "story", "title": key, "parent": "I", "status": "planned",
                "requirement_ids": ["RC"], "acceptance": self.requirement, **extras}

    def apply(self, request_name, plan, operation_id):
        decision_name = operation_id + "-decision.json"
        self.save(decision_name, {
            "schema_version": store.DECISION, "decision": "approve", "operation_id": operation_id,
            "plan_sha256": store.plan_sha256(plan), "authority_ref": "Fixture approved the exact plan",
            **{field: plan[field] for field in store.BINDING},
        })
        return store.apply_plan(self.root, self.projection, request_name, decision_name,
                                self.pin(decision_name)["sha256"])

    def preview(self):
        self.save("correction.json", self.request)
        return correction.build_correction(self.root, self.projection, "correction.json")

    def test_correction_restores_original_rows_and_retains_two_commits(self):
        before = (self.root / self.projection).read_bytes()
        plan = self.preview()
        self.assertEqual((self.root / self.projection).read_bytes(), before)
        self.assertEqual(plan["correction"]["restored_ticket_ids"], ["T1", "T2"])
        self.assertEqual(plan["correction"]["retired_ticket_ids"], ["T11", "T12"])
        self.assertFalse(plan["no_execution_independently_verified"])
        applied = self.apply("correction.json", plan, "corrected")
        self.assertEqual(applied["status"], "applied")
        self.assertEqual(applied["native_revision"], "r3")
        observed = context.json_object((self.root / self.projection).read_bytes())
        self.assertEqual(observed["tickets"][:len(self.baseline["tickets"])], self.baseline["tickets"])
        self.assertEqual([row["status"] for row in observed["tickets"][-2:]], ["deferred", "deferred"])
        self.assertEqual([r["ticket_id"] for r in observed["replan_retirements"]], ["T11", "T12"])
        self.assertEqual([r["operation_id"] for r in observed[store.HISTORY]], ["landed", "corrected"])
        self.assertEqual(observed["custom"], self.baseline["custom"])
        self.assertEqual(tree.project_board(self.root, self.projection)["board"]["ready"], ["T1"])
        old = store.read_receipt(self.root, self.projection, "landed", store.plan_sha256(self.original))
        self.assertEqual(old["status"], "historical")
        self.assertFalse(old["verified_readback"])
        self.assertEqual(self.apply("correction.json", plan, "corrected")["status"], "replayed")

    def test_refuses_different_archived_baseline_or_missing_dispatch_evidence(self):
        landed = (self.root / self.projection).read_bytes()
        self.save("different.json", {**self.baseline, "custom": {"other": "value"}})
        initial_pin = self.request["baseline"]
        self.request["baseline"] = self.pin("different.json")
        with self.assertRaisesRegex(context.ContextError, "archived baseline does not match"):
            self.preview()
        self.request["baseline"] = initial_pin
        self.save("no-dispatch.json", {**self.dispatch, "status": "running"})
        self.request["no_dispatch"] = self.pin("no-dispatch.json")
        with self.assertRaisesRegex(context.ContextError, "reconciled no-dispatch record"):
            self.preview()
        self.assertEqual((self.root / self.projection).read_bytes(), landed)

    def test_refuses_a_projection_changed_after_review(self):
        self.preview()
        observed = context.json_object((self.root / self.projection).read_bytes())
        observed["tickets"][-1]["status"] = "in-progress"
        self.save(self.projection, observed)
        self.request["projection_sha256"] = self.pin(self.projection)["sha256"]
        with self.assertRaisesRegex(context.ContextError, "does not match the committed replan target"):
            self.preview()


if __name__ == "__main__":
    unittest.main()
