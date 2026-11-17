"""Exercise the approved ticket-to-worktree handoff using actual local Git."""

from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_ticket_handoff as fixture_tests
import ticket_worktree_assignment as assignment

context = assignment.context
worktree = assignment.worktree


class TicketWorktreeAssignmentTest(unittest.TestCase):
    def setUp(self):
        fixture = fixture_tests.BuilderHandoffTests()
        self.addCleanup(fixture.doCleanups)
        fixture.setUp()
        self.fixture = fixture
        self.root = fixture.root
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name).resolve()
        self.base = worktree.git_text(self.root, "rev-parse", "HEAD")
        self.handoff_ref = "review/handoff.json"
        fixture.save(self.handoff_ref, fixture.prepare())
        self.handoff_sha = fixture.pin(self.handoff_ref)["sha256"]

    def write_binding(self, owner=None, scopes=None):
        owner = owner or self.root
        worker = self.scratch / "worker"
        record = worktree.make_binding(owner, self.base, worker, "codex/worker",
                                       scopes or ["export.py"], create=True)
        path = self.scratch / "worker.json"
        raw = context.canonical(record)
        path.write_bytes(raw)
        return path, context.digest(raw)

    def test_applied_replan_admits_scoped_worker_and_preserves_central_return(self):
        path, digest = self.write_binding()
        result = assignment.assign(self.root, self.handoff_ref, self.handoff_sha, path, digest)
        self.assertEqual(result["status"], "ready-for-operator-dispatch")
        self.assertEqual(result["ticket"]["id"], "T-CSV")
        self.assertEqual(result["worker"]["branch"], "codex/worker")
        self.assertEqual(result["worker"]["base"], self.base)
        self.assertEqual(result["worker"]["starting_files"], [
            {**self.fixture.pin("export.py"), "mode": stat.S_IMODE((self.root / "export.py").stat().st_mode)},
        ])
        self.assertEqual(result["coordinator_return"], {
            "root": str(self.root), "path": "review/builder.json",
        })
        self.assertFalse(result["reservation_verified"])
        self.assertFalse(result["execution_observed"])
        self.assertFalse((self.root / "review/builder.json").exists())
        self.assertEqual(worktree.git_text(self.root, "rev-parse", "HEAD"), self.base)

    def test_a_worker_cannot_claim_extra_writable_paths(self):
        path, digest = self.write_binding(scopes=["export.py", "unapproved.py"])
        with self.assertRaisesRegex(context.ContextError, "approved product scope"):
            assignment.assign(self.root, self.handoff_ref, self.handoff_sha, path, digest)

    def test_same_commit_in_a_different_repository_is_refused(self):
        unrelated = self.scratch / "unrelated"
        worktree.git(self.scratch, "clone", "-q", "--no-hardlinks", "--",
                     str(self.root), str(unrelated))
        self.assertEqual(worktree.git_text(unrelated, "rev-parse", "HEAD"), self.base)
        path, digest = self.write_binding(owner=unrelated)
        with self.assertRaisesRegex(context.ContextError, "different coordinator"):
            assignment.assign(self.root, self.handoff_ref, self.handoff_sha, path, digest)

    def test_approved_uncommitted_coordinator_bytes_are_not_in_worker_base(self):
        path, digest = self.write_binding()
        (self.root / "export.py").write_text("approved draft outside the selected base\n")
        self.fixture.save(self.handoff_ref, self.fixture.prepare())
        approved_sha = self.fixture.pin(self.handoff_ref)["sha256"]
        with self.assertRaisesRegex(context.ContextError, "starting bytes differ"):
            assignment.assign(self.root, self.handoff_ref, approved_sha, path, digest)

    def test_mode_drift_without_byte_drift_is_refused(self):
        path, digest = self.write_binding()
        source = self.root / "export.py"
        source.chmod(stat.S_IMODE(source.stat().st_mode) ^ stat.S_IXUSR)
        with self.assertRaisesRegex(context.ContextError, "file mode differs"):
            assignment.assign(self.root, self.handoff_ref, self.handoff_sha, path, digest)

    def test_worker_preexisting_edit_is_refused(self):
        path, digest = self.write_binding()
        (self.scratch / "worker" / "export.py").write_text("preexisting worker edit\n")
        with self.assertRaisesRegex(context.ContextError, "worktree is not clean"):
            assignment.assign(self.root, self.handoff_ref, self.handoff_sha, path, digest)


if __name__ == "__main__":
    unittest.main()
