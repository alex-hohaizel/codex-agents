"""Recognize actual BMad planning artifacts from the documented front matter."""

from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bmad_planning_probe import ready_specs


class ReadySpecsTest(unittest.TestCase):
    def test_real_quoted_status_and_status_outside_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            output = project / "_bmad-output"
            output.mkdir()
            spec = b"---\nstatus: 'ready-for-dev'\n---\n# Plan\n"
            (output / "spec.md").write_bytes(spec)
            (output / "result.md").write_text("---\nstatus: blocked\n---\nstatus: ready-for-dev\n")
            (output / "unframed.md").write_text("status: ready-for-dev\n")
            self.assertEqual(ready_specs(project), [{
                "path": "_bmad-output/spec.md", "sha256": sha256(spec).hexdigest()
            }])


if __name__ == "__main__":
    unittest.main()
