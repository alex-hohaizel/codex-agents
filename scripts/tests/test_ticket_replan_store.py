#!/usr/bin/env python3
"""Check the local tracker write boundary independently of the proposal model."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_replan_store as store

context = store.context


class ReplanStoreTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.name = "tickets.json"
        self.projection = self.root / self.name
        self.write(self.name, {
            "schema_version": store.tree.PROJECTION,
            "project_id": "project-a",
            "native_revision": "r1",
            "tickets": [{"id": "A", "title": "Existing report", "status": "accepted",
                         "evidence": ["prior/source.json"]}],
            "custom_metadata": {"retention": "preserve"},
        })

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def pin(self, name):
        return {"path": name, "sha256": context.digest((self.root / name).read_bytes())}

    def review(self, operation, target_revision):
        request_name = operation + "-request.json"
        decision_name = operation + "-decision.json"
        self.write(request_name, {"add": target_revision})
        before = json.loads(self.projection.read_bytes())
        target = deepcopy(before)
        target["native_revision"] = target_revision
        target["tickets"].append({"id": target_revision, "title": "New work", "status": "planned"})
        plan = {
            "project_id": before["project_id"],
            "native_revision": before["native_revision"],
            "target_revision": target_revision,
            "projection": self.pin(self.name),
            "request": self.pin(request_name),
            "target": target,
            "readiness": {"affected_tickets": [{"ticket_id": target_revision}]},
        }
        decision = {
            "schema_version": store.DECISION,
            "decision": "approve",
            "operation_id": operation,
            "authority_ref": "Project owner fixture review",
            **{field: plan[field] for field in store.BINDING},
            "plan_sha256": store.plan_sha256(plan),
        }
        self.write(decision_name, decision)
        return plan, (self.root, self.name, request_name, decision_name, self.pin(decision_name)["sha256"])

    def apply(self, plan, args):
        with patch.object(store, "build_plan", return_value=plan):
            return store.apply_plan(*args)

    def test_interrupt_after_commit_recovers_and_replays_without_second_write(self):
        plan, args = self.review("op-a", "r2")
        before = json.loads(self.projection.read_bytes())
        self.projection.chmod(0o640)
        original = store.atomic_replace

        def lose_response(*call):
            original(*call)
            raise OSError("connection interrupted after durable commit")

        with patch.object(store, "atomic_replace", side_effect=lose_response):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.apply(plan, args)
        readback = store.read_receipt(self.root, self.name, "op-a", store.plan_sha256(plan))
        self.assertEqual(readback["status"], "verified")
        self.assertTrue(readback["verified_readback"])
        self.assertFalse(readback["authority_authenticated"])
        self.assertEqual(readback["receipt"]["created_ticket_ids"], ["r2"])
        self.assertEqual(readback["receipt"]["decision"], self.pin(args[3]))
        self.assertEqual(readback["projection"], self.pin(self.name))
        self.assertEqual(self.projection.stat().st_mode & 0o777, 0o640)
        after = self.projection.read_bytes()
        updated = json.loads(after)
        self.assertEqual(updated["tickets"][0], before["tickets"][0])
        self.assertEqual(updated["custom_metadata"], before["custom_metadata"])
        with patch.object(store, "build_plan", side_effect=AssertionError("unexpected replay rebuild")):
            self.assertEqual(store.apply_plan(*args)["status"], "replayed")
        self.assertEqual(self.projection.read_bytes(), after)

    def test_rejects_stale_baseline_and_reused_operation_before_rebuilding(self):
        first, args = self.review("op-a", "r2")
        _, stale = self.review("op-stale", "r3")
        self.apply(first, args)
        after = self.projection.read_bytes()
        with patch.object(store, "build_plan", side_effect=AssertionError("unexpected stale rebuild")):
            with self.assertRaisesRegex(context.ContextError, "stale replan baseline"):
                store.apply_plan(*stale)
        _, reused = self.review("op-a", "r4")
        with self.assertRaisesRegex(context.ContextError, "different decision or plan"):
            store.apply_plan(*reused)
        self.assertEqual(self.projection.read_bytes(), after)

    def test_retains_old_receipt_and_rejects_reused_revision_and_current_drift(self):
        first, args = self.review("op-a", "r2")
        self.apply(first, args)
        _, reused = self.review("op-reuse", "r1")
        with self.assertRaisesRegex(context.ContextError, "historical revision"):
            store.apply_plan(*reused)
        second, args = self.review("op-b", "r3")
        self.apply(second, args)
        historical = store.read_receipt(self.root, self.name, "op-a", store.plan_sha256(first))
        self.assertEqual(historical["status"], "historical")
        self.assertFalse(historical["verified_readback"])
        self.assertEqual(historical["receipt"]["target_revision"], "r2")
        current = json.loads(self.projection.read_bytes())
        current["tickets"][-1]["title"] = "Externally modified"
        self.write(self.name, current)
        with self.assertRaisesRegex(context.ContextError, "does not match the committed replan target"):
            store.read_receipt(self.root, self.name, "op-b", store.plan_sha256(second))
        current[store.HISTORY][0]["created_ticket_ids"] = ["Altered lineage"]
        self.write(self.name, current)
        with self.assertRaisesRegex(context.ContextError, "broken replan receipt history"):
            store.read_receipt(self.root, self.name, "op-b", store.plan_sha256(second))

    def test_refuses_a_changed_review_at_final_commit_precondition(self):
        plan, args = self.review("op-a", "r2")
        before = self.projection.read_bytes()
        changed = {**plan, "request": {**plan["request"], "sha256": "a" * 64}}
        with patch.object(store, "build_plan", side_effect=[plan, changed]):
            with self.assertRaisesRegex(context.ContextError, "source or request drift before commit"):
                store.apply_plan(*args)
        self.assertEqual(self.projection.read_bytes(), before)
        with self.assertRaisesRegex(context.ContextError, "receipt not found"):
            store.read_receipt(self.root, self.name, "op-a", store.plan_sha256(plan))

    def test_cross_process_writer_lock_covers_filename_aliases(self):
        plan, args = self.review("op-a", "r2")
        before = self.projection.read_bytes()
        child_code = """
import sys
from pathlib import Path
import ticket_replan_store as store
with store.projection_lock(Path(sys.argv[1])):
    print('locked', flush=True)
    sys.stdin.readline()
"""
        alias = self.projection.with_name(self.projection.name.upper())
        with subprocess.Popen(
            [sys.executable, "-B", "-c", child_code, str(alias)],
            cwd=Path(store.__file__).parent, text=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ) as child:
            try:
                self.assertEqual(child.stdout.readline(), "locked\n")
                with self.assertRaisesRegex(context.ContextError, "projection is busy"):
                    self.apply(plan, args)
            finally:
                child.communicate(input="release\n", timeout=5)
            self.assertEqual(child.returncode, 0)
        self.assertEqual(self.projection.read_bytes(), before)
        self.assertEqual(self.apply(plan, args)["status"], "applied")


if __name__ == "__main__":
    unittest.main()
