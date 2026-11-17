"""Exercise worktree admission and exact integration against a real local Git repository."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_worktree as worktree

context = worktree.context
GIT_ACTOR = {
    "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


class TicketWorktreeTest(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory()
        self.addCleanup(fixture.cleanup)
        self.scratch = Path(fixture.name).resolve()
        self.repo = self.scratch / "repo"
        self.repo.mkdir()
        worktree.git(self.repo, "init", "-q", "-b", "main", "--template=")
        for name in ("a.txt", "b.txt", "state.txt"):
            (self.repo / name).write_text("base\n", encoding="utf-8")
        self.base = self.commit(self.repo, "Baseline", "a.txt", "b.txt", "state.txt")

    def commit(self, root, message, *paths):
        worktree.git(root, "add", "--", *paths)
        worktree.git(root, "commit", "-qm", message, extra_env=GIT_ACTOR)
        return worktree.git_text(root, "rev-parse", "HEAD")

    def bind(self, name, *paths):
        return worktree.make_binding(self.repo, self.base, self.scratch / name,
                                     "codex/" + name, list(paths), create=True)

    def record(self, name, value):
        raw = json.dumps(value, sort_keys=True).encode("utf-8")
        path = self.scratch / name
        path.write_bytes(raw)
        return path, context.digest(raw)

    def worker(self, name, filename, *extra_scope):
        binding = self.bind(name, filename, *extra_scope)
        root = Path(binding["worktree"])
        (root / filename).write_text(name + "\n", encoding="utf-8")
        commit = self.commit(root, name, filename)
        return (*self.record(name + ".json", binding), commit)

    def test_review_apply_and_replay_preserve_parent_and_exact_worker_bytes(self):
        a = self.worker("worker-a", "a.txt")
        b = self.worker("worker-b", "b.txt")
        target = Path(self.bind("integration", "a.txt")["worktree"])
        plan = worktree.build_plan(self.repo, target, [a, b])
        self.assertEqual(plan, worktree.build_plan(self.repo, target, [a, b]))
        self.assertEqual(worktree.git_text(target, "rev-parse", "HEAD"), self.base)
        saved = self.record("plan.json", plan)
        result = worktree.apply_plan(*saved)
        self.assertEqual(result["status"], "integrated")
        self.assertEqual(result["head"], plan["commit"])
        self.assertEqual((target / "a.txt").read_text(), "worker-a\n")
        self.assertEqual((target / "b.txt").read_text(), "worker-b\n")
        self.assertEqual((target / "state.txt").read_text(), "base\n")
        self.assertEqual(worktree.git_text(self.repo, "rev-parse", "main"), self.base)
        self.assertEqual(worktree.git_text(self.repo, "rev-parse", "codex/worker-a"), a[-1])
        self.assertEqual(worktree.git_text(self.repo, "rev-parse", "codex/worker-b"), b[-1])
        self.assertEqual(worktree.apply_plan(*saved)["status"], "already-integrated")

    def test_overlapping_work_is_rejected_before_integration(self):
        a = self.worker("worker-a", "a.txt", "state.txt")
        b = self.worker("worker-b", "b.txt", "state.txt")
        target = Path(self.bind("integration", "a.txt")["worktree"])
        with self.assertRaisesRegex(context.ContextError, "overlapping writable paths"):
            worktree.build_plan(self.repo, target, [a, b])
        self.assertEqual(worktree.git_text(target, "rev-parse", "HEAD"), self.base)

    def test_out_of_scope_and_nonregular_worker_changes_are_refused(self):
        binding = self.bind("worker", "a.txt")
        root = Path(binding["worktree"])
        (root / "b.txt").write_text("unexpected\n", encoding="utf-8")
        changed = self.commit(root, "Unexpected change", "b.txt")
        with self.assertRaisesRegex(context.ContextError, "outside the approved scope"):
            worktree.candidate(binding, changed)
        second = self.bind("other", "a.txt")
        root = Path(second["worktree"])
        (root / "a.txt").unlink()
        (root / "a.txt").symlink_to("b.txt")
        changed = self.commit(root, "Wrong kind", "a.txt")
        with self.assertRaisesRegex(context.ContextError, "linked|non-regular|regular file|symbolic"):
            worktree.candidate(second, changed)

    def test_both_worker_and_target_drift_block_saved_integration(self):
        a = self.worker("worker-a", "a.txt")
        b = self.worker("worker-b", "b.txt")
        target = Path(self.bind("integration", "a.txt")["worktree"])
        saved = self.record("plan.json", worktree.build_plan(self.repo, target, [a, b]))
        (target / "state.txt").write_text("uncommitted\n", encoding="utf-8")
        with self.assertRaisesRegex(context.ContextError, "worktree is not clean"):
            worktree.apply_plan(*saved)
        (target / "state.txt").write_text("base\n", encoding="utf-8")
        worker = self.scratch / "worker-a"
        (worker / "a.txt").write_text("second commit\n", encoding="utf-8")
        self.commit(worker, "Drift", "a.txt")
        with self.assertRaisesRegex(context.ContextError, "advanced"):
            worktree.apply_plan(*saved)
        self.assertEqual(worktree.git_text(target, "rev-parse", "HEAD"), self.base)

    def test_existing_worktree_binding_and_input_pins(self):
        initial = self.bind("worker-a", "a.txt")
        target = Path(initial["worktree"])
        self.assertEqual(worktree.make_binding(self.repo, self.base, target, "codex/worker-a",
                                               ["a.txt"]), initial)
        path, digest = self.record("worker.json", initial)
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(context.ContextError, "SHA-256 changed"):
            worktree.load_binding(path, digest)
        with self.assertRaisesRegex(context.ContextError, "nonnested"):
            worktree.make_binding(self.repo, self.base, self.repo / "unsafe", "codex/unsafe",
                                   ["a.txt"], create=True)
        self.assertFalse((self.repo / "unsafe").exists())


    def test_invalid_scope_does_not_create_a_branch_or_worktree(self):
        with self.assertRaisesRegex(context.ContextError, "no existing directory"):
            self.bind("worker", "unknown/nested.txt")
        self.assertFalse((self.scratch / "worker").exists())
        self.assertEqual(worktree.git_text(self.repo, "branch", "--list", "codex/worker"), "")


if __name__ == "__main__":
    unittest.main()
