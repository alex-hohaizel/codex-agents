"""Restore a bounded interrupted worktree through exact Git and filesystem evidence."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_worktree_checkpoint as checkpoint


class WorktreeCheckpointTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.temp = Path(scratch.name).resolve()
        self.root = self.temp / "repo"
        self.root.mkdir()
        (self.root / "catalog.py").write_text("price = 100\n")
        (self.root / "quote.py").write_text("currency = 'EUR'\n")
        (self.root / ".gitignore").write_text("ignore-this\n")
        self.git(self.root, "init", "-q", "--template=")
        self.git(self.root, "add", "-A")
        self.git(self.root, "-c", "user.name=Checkpoint Fixture", "-c",
                 "user.email=fixture@example.invalid", "commit", "-q", "-m", "Baseline")
        self.base = self.git(self.root, "rev-parse", "HEAD").strip()
        self.first, self.other = self.temp / "first", self.temp / "other"
        for ref, branch in ((self.first, "codex/first"), (self.other, "codex/other")):
            self.git(self.root, "worktree", "add", "-q", "-b", branch, str(ref), self.base)
        self.binding = self.temp / "binding.json"
        self.stop = self.temp / "interruption.json"
        self.frozen = self.temp / "checkpoint.json"
        data = {
            "schema_version": "atelier.ticket-worktree-binding/1",
            "root": str(self.root), "base": self.base, "worktree": str(self.first),
            "branch": "codex/first", "git_common_dir": str(self.root / ".git"),
            "write_paths": ["catalog.py"],
        }
        self.save(self.binding, data)
        self.stop_data = {
            "schema_version": checkpoint.INTERRUPTION,
            "binding_sha256": self.sha(self.binding), "state": "interrupted",
            "native_run_ref": "local-fixture:terminated-process",
            "readback_ref": "fixture:observed-terminal-return",
            "next_action": "Complete price validation from the partial catalog edit.",
        }
        self.save(self.stop, self.stop_data)

    def git(self, root, *argv):
        return subprocess.run(
            ("git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
             "-c", "commit.gpgsign=false", *argv),
            capture_output=True, text=True, check=True
        ).stdout

    def save(self, path, data):
        path.write_text(json.dumps(data, indent=2) + "\n")

    def sha(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def partial(self):
        (self.first / "catalog.py").write_text("price = round(100)\n")

    def capture(self):
        return checkpoint.capture(self.binding, self.sha(self.binding), self.stop, self.sha(self.stop))

    def test_new_session_receives_the_exact_partial_while_sibling_continues(self):
        self.partial()
        frozen = self.capture()
        self.save(self.frozen, frozen)
        (self.other / "quote.py").write_text("currency = 'UAH'\n")
        admitted = checkpoint.resume(self.frozen, self.sha(self.frozen))
        self.assertEqual(admitted["status"], "ready-to-resume")
        self.assertEqual(admitted["scoped_files"]["catalog.py"]["sha256"],
                         self.sha(self.first / "catalog.py"))
        self.assertFalse(admitted["new_session_started"])
        self.assertEqual((self.root / "quote.py").read_text(), "currency = 'EUR'\n")

    def test_same_git_status_with_later_bytes_requires_reconciliation(self):
        self.partial()
        self.save(self.frozen, self.capture())
        (self.first / "catalog.py").write_text("price = round(102)\n")
        with self.assertRaisesRegex(checkpoint.context.ContextError, "checkpoint is stale"):
            checkpoint.resume(self.frozen, self.sha(self.frozen))

    def test_cannot_resume_unknown_launch_or_hidden_extra_writes(self):
        self.partial()
        with self.assertRaisesRegex(checkpoint.context.ContextError, "canonical absolute binding"):
            checkpoint.capture(Path("binding.json"), self.sha(self.binding), self.stop, self.sha(self.stop))
        self.save(self.stop, {**self.stop_data, "state": "cancel-requested"})
        with self.assertRaisesRegex(checkpoint.context.ContextError, "terminal readback"):
            self.capture()
        self.save(self.stop, self.stop_data)
        (self.first / "ignore-this").write_text("outside scope\n")
        with self.assertRaisesRegex(checkpoint.context.ContextError, "unexpected staged, ignored"):
            self.capture()
        (self.first / "ignore-this").unlink()
        self.git(self.first, "add", "catalog.py")
        with self.assertRaisesRegex(checkpoint.context.ContextError, "unexpected staged, ignored"):
            self.capture()


if __name__ == "__main__":
    unittest.main()
