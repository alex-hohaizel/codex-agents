import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TOOL = Path(__file__).resolve().parents[1] / "workshop.py"


class WorkshopTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "catalog.csv").write_text(
            "num,direction,method_name,description,form,tier,aliases\n"
            "1,wrong,Critique,Probe the claim,Strength and weakness,more,\n",
            encoding="utf-8",
        )
        (self.root / "need.txt").write_text("Preserve accepted project decisions.", encoding="utf-8")

    def call(self, operation, *args):
        return subprocess.run([sys.executable, "-B", str(TOOL), operation, "--root",
                               str(self.root), *args], capture_output=True, text=True)

    def sha(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def save(self, name, record):
        (self.root / name).write_text(json.dumps(record), encoding="utf-8")

    def test_resume_decide_and_detect_evidence_drift(self):
        start = self.call("start", "--catalog", "catalog.csv", "--catalog-sha256", self.sha("catalog.csv"),
                          "--goal", "Keep exact intent", "--mode", "pressure-test", "--evidence", "need.txt",
                          "--limit", "1")
        self.assertEqual(start.returncode, 0, start.stderr)
        (self.root / "r0.json").write_text(start.stdout)
        self.save("round.json", dict(method="Critique", actor="Reviewer", topic="Recovery",
                                      question="Which source applies?", response="Check exact version",
                                      ideas=[{"id": "A", "text": "<private>"}]))
        args = ("--state", "r0.json", "--state-sha256", self.sha("r0.json"))
        first = self.call("append", *args, "--record", "round.json")
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.root / "r1.json").write_text(first.stdout)
        self.assertEqual(json.loads(first.stdout)["previous_sha256"], self.sha("r0.json"))
        args = ("--state", "r1.json", "--state-sha256", self.sha("r1.json"))
        self.assertEqual(self.call("append", *args, "--record", "round.json").returncode, 2)
        self.save("decision.json", dict(decided_by="Owner", decisions=[
            {"id": "A", "outcome": "reframe", "reason": "Keep a bounded source receipt."}]))
        finished = self.call("decide", *args, "--record", "decision.json")
        self.assertEqual(finished.returncode, 0, finished.stderr)
        (self.root / "r2.json").write_text(finished.stdout)
        args = ("--state", "r2.json", "--state-sha256", self.sha("r2.json"), "--format", "html")
        self.assertIn("&lt;private&gt;", self.call("report", *args).stdout)
        (self.root / "need.txt").write_text("Changed evidence.", encoding="utf-8")
        blocked = self.call("report", *args)
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("source changed: need.txt", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
