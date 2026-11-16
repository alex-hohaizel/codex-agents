"""Failure recovery checks for persisted work, staged artifacts and child commands."""
import contextlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from showcase_pipeline import (LOG_LIMIT, Pipeline, Stage, execution_lock,
                               run_command, sha, validate_export)


class PipelineRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.state = Path(self.temp.name) / "state/pipeline.json"
        (self.root / "source.txt").write_text("accepted source")

    def run_pipeline(self, stages, runner, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return Pipeline(self.root, self.state, stages, runner=runner).run(**kwargs)

    def test_resume_after_interruption_keeps_completed_work(self):
        stages = [Stage("first", (("first",),), ("source.txt",), ("first.txt",)),
                  Stage("second", (("second",),), ("first.txt",), ("second.txt",))]
        calls = []

        def interrupted(command, root, timeout, log):
            calls.append(command[0])
            if command[0] == "second":
                raise KeyboardInterrupt()
            (root / "first.txt").write_text("first accepted")

        with self.assertRaises(KeyboardInterrupt):
            self.run_pipeline(stages, interrupted)
        receipt = json.loads(self.state.read_text())
        self.assertEqual(receipt["stages"]["first"]["status"], "complete")
        self.assertEqual(receipt["stages"]["second"]["status"], "interrupted")

        def resumed(command, root, timeout, log):
            calls.append(command[0])
            (root / "second.txt").write_text("second accepted")

        result = self.run_pipeline(stages, resumed)
        self.assertEqual(calls, ["first", "second", "second"])
        self.assertEqual(result["stages"][0]["status"], "verified-cache")
        self.assertFalse(result["publication_performed"])
        self.assertFalse(result["chat_platform_repair_claimed"])

    def test_missing_or_corrupt_output_and_changed_input_require_work(self):
        stages = [Stage("generate", (("generate",),), ("source.txt",), ("result.txt",))]
        calls = []

        def runner(command, root, timeout, log):
            calls.append(1)
            (root / "result.txt").write_text((root / "source.txt").read_text())

        self.run_pipeline(stages, runner)
        self.run_pipeline(stages, runner)
        self.assertEqual(len(calls), 1)
        (self.root / "result.txt").write_text("corruption")
        self.run_pipeline(stages, runner)
        (self.root / "result.txt").unlink()
        self.run_pipeline(stages, runner)
        (self.root / "source.txt").write_text("new accepted source")
        self.run_pipeline(stages, runner)
        self.assertEqual(len(calls), 4)
        self.assertEqual((self.root / "result.txt").read_text(), "new accepted source")

    def test_replaced_release_archive_invalidates_the_package_cache(self):
        filename = "Agent_System_6.2.0_CODEX.zip"
        relative_path = f"dist/{filename}"
        stages = [Stage("package", (("{output}",),), ("source.txt",),
                        (relative_path,), staged_output_dir="dist")]
        archive = self.root / relative_path
        original = b"accepted archive"

        def runner(command, root, timeout, log):
            (Path(command[0]) / filename).write_bytes(original)

        self.run_pipeline(stages, runner)
        accepted = json.loads(self.state.read_text())["stages"]["package"]["outputs"]
        self.assertEqual(accepted[relative_path]["sha256"], sha(archive))
        self.assertEqual(self.run_pipeline(stages, runner)["stages"][0]["status"], "verified-cache")

        archive.write_bytes(b"modified archive")
        self.assertEqual(self.run_pipeline(stages, runner)["stages"][0]["status"], "complete")
        self.assertEqual(archive.read_bytes(), original)

    def test_missing_private_artifact_invalidates_completed_export(self):
        stages = [Stage("export", (("generate",),), ("source.txt",), ("result.txt",),
                        private_outputs=("reports/local-artifacts/full.pdf",))]
        calls = []

        def runner(command, root, timeout, log):
            calls.append(1)
            (root / "result.txt").write_text("tracked result")
            private = root / "reports/local-artifacts/full.pdf"
            private.parent.mkdir(parents=True, exist_ok=True)
            private.write_bytes(b"full private export")

        self.run_pipeline(stages, runner)
        self.run_pipeline(stages, runner)
        self.assertEqual(len(calls), 1)
        (self.root / "reports/local-artifacts/full.pdf").unlink()
        self.run_pipeline(stages, runner)
        self.assertEqual(len(calls), 2)

    def test_running_receipt_from_hard_stop_is_not_a_success(self):
        stages = [Stage("generate", (("generate",),), ("source.txt",), ("result.txt",))]

        def runner(command, root, timeout, log):
            (root / "result.txt").write_text("verified")

        self.run_pipeline(stages, runner)
        receipt = json.loads(self.state.read_text())
        receipt["stages"]["generate"]["status"] = "running"
        self.state.write_text(json.dumps(receipt))
        calls = []

        def restarted(command, root, timeout, log):
            calls.append(1)
            runner(command, root, timeout, log)

        self.run_pipeline(stages, restarted)
        self.assertEqual(calls, [1])
        self.assertEqual(json.loads(self.state.read_text())["stages"]["generate"]["attempt"], 2)

    def test_incomplete_staged_set_never_replaces_previous_files(self):
        target = self.root / "output"
        target.mkdir()
        (target / "one.txt").write_text("previous accepted result")
        stages = [Stage("export", (("{output}",),), ("source.txt",),
                        ("output/one.txt", "output/two.txt"), staged_output_dir="output")]

        def incomplete(command, root, timeout, log):
            self.assertTrue(Path(command[0]).is_relative_to(root / "reports"))
            (Path(command[0]) / "one.txt").write_text("unaccepted partial result")

        with self.assertRaisesRegex(ValueError, "missing staged output"):
            self.run_pipeline(stages, incomplete)
        self.assertEqual((target / "one.txt").read_text(), "previous accepted result")
        self.assertEqual(json.loads(self.state.read_text())["stages"]["export"]["status"], "failed")

    def test_changed_inputs_during_export_prevent_promotion(self):
        stages = [Stage("export", (("{output}",),), ("source.txt",),
                        ("output/result.txt",), staged_output_dir="output")]

        def changing_source(command, root, timeout, log):
            (Path(command[0]) / "result.txt").write_text("stale result")
            (root / "source.txt").write_text("concurrent edit")

        with self.assertRaisesRegex(ValueError, "inputs changed"):
            self.run_pipeline(stages, changing_source)
        self.assertFalse((self.root / "output/result.txt").exists())

    def test_missing_input_and_packaged_state_are_rejected(self):
        stages = [Stage("check", (), ("missing.txt",))]
        with self.assertRaisesRegex(ValueError, "missing stage inputs"):
            self.run_pipeline(stages, lambda *args: None)
        with self.assertRaisesRegex(ValueError, "outside packaged inputs"):
            Pipeline(self.root, self.root / "marketing/state.json", [])

    def test_duplicate_writer_is_rejected_even_with_another_state_path(self):
        with execution_lock(self.root / "reports/local-showcase-pipeline.lock"):
            with self.assertRaisesRegex(ValueError, "already running"):
                self.run_pipeline([], lambda *args: None)

    def test_invalid_checkpoint_is_retained_for_diagnosis(self):
        self.state.parent.mkdir()
        self.state.write_text('{"schema": "unrelated", "stages": []}')
        with self.assertRaisesRegex(ValueError, "checkpoint schema"):
            self.run_pipeline([], lambda *args: None)
        self.assertEqual(json.loads(self.state.read_text())["schema"], "unrelated")

    def test_pdf_receipt_cannot_hide_wrong_page_count(self):
        directory = self.root / "staged-pdf"
        directory.mkdir()
        records = []
        for name in ("index.html", "en.html", "uk.html", "pdf/Campaign.en.pdf", "pdf/Campaign.uk.pdf"):
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = (b"%PDF-1.4\n" + b"/Type /Page\n" * 10 if path.suffix == ".pdf"
                       else b"<!doctype html><html>campaign</html>")
            path.write_bytes(payload)
            records.append({"path": name, "sha256": sha(path), "size": len(payload)})
        receipt = directory / "exports.json"
        receipt.write_text(json.dumps({"files": records}))
        validate_export(directory)
        path = directory / "pdf/Campaign.uk.pdf"
        path.write_bytes(b"%PDF-1.4\n/Type /Page\n")
        records[-1].update(sha256=sha(path), size=path.stat().st_size)
        receipt.write_text(json.dumps({"files": records}))
        with self.assertRaisesRegex(ValueError, "page count mismatch"):
            validate_export(directory)

    def test_command_failure_has_bounded_log_and_useful_tail(self):
        log = Path(self.temp.name) / "command.log"
        command = [sys.executable, "-c", "import sys;sys.stdout.write('x'*400000+'FINAL FAILURE');sys.exit(7)"]
        with self.assertRaisesRegex(RuntimeError, "FINAL FAILURE"):
            run_command(command, self.root, 5, log)
        self.assertLessEqual(log.stat().st_size, LOG_LIMIT)
        self.assertTrue(log.read_text().endswith("FINAL FAILURE"))

    @unittest.skipUnless(os.name == "posix", "process-group ownership check")
    def test_timeout_kills_descendant_before_it_can_write(self):
        marker = self.root / "unexpected.txt"
        child = "import time,pathlib;time.sleep(.5);pathlib.Path('unexpected.txt').write_text('leaked')"
        command = [sys.executable, "-c",
                   "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',sys.argv[1]]);time.sleep(5)", child]
        with self.assertRaises(subprocess.TimeoutExpired):
            run_command(command, self.root, .1, Path(self.temp.name) / "timeout.log")
        time.sleep(.6)
        self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == "posix", "process-group ownership check")
    def test_successful_command_cannot_leave_background_writer(self):
        child = "import time,pathlib;time.sleep(.5);pathlib.Path('unexpected.txt').write_text('leaked')"
        command = [sys.executable, "-c",
                   "import subprocess,sys;subprocess.Popen([sys.executable,'-c',sys.argv[1]],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)", child]
        run_command(command, self.root, 3, Path(self.temp.name) / "background.log")
        time.sleep(.6)
        self.assertFalse((self.root / "unexpected.txt").exists())

    @unittest.skipUnless(os.name == "posix", "POSIX termination cleanup")
    def test_sigterm_stops_cli_child_and_saves_interrupted_stage(self):
        source = self.root / "marketing/campaign"
        source.mkdir(parents=True)
        (self.root / "assets/marketing/campaign").mkdir(parents=True)
        releases = self.root / "releases"
        releases.mkdir()
        (releases / "current.json").write_text('{"suite_version":"5.0.0"}')
        scripts = self.root / "scripts"
        scripts.mkdir()
        (scripts / "showcase_pipeline.py").write_text("fingerprinted runner source")
        (source / "campaign.json").write_text("{}")
        (source / "capabilities.json").write_text("{}")
        (source / "build_campaign.py").write_text(
            "import time,pathlib\npathlib.Path('started').write_text('yes')\n"
            "time.sleep(.5)\npathlib.Path('unexpected.txt').write_text('orphan')\ntime.sleep(5)\n")
        script = Path(__file__).resolve().parents[1] / "showcase_pipeline.py"
        process = subprocess.Popen([sys.executable, str(script), "--root", str(self.root), "--until", "export"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        limit = time.monotonic() + 3
        while not (self.root / "started").exists() and time.monotonic() < limit:
            time.sleep(.01)
        self.assertTrue((self.root / "started").exists(), "export child did not start")
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=3)
        self.assertEqual(process.returncode, 128 + signal.SIGTERM)
        receipt = json.loads((self.root / "reports/local-showcase-pipeline.json").read_text())
        self.assertEqual(receipt["stages"]["export"]["status"], "interrupted")
        time.sleep(.6)
        self.assertFalse((self.root / "unexpected.txt").exists())


if __name__ == "__main__":
    unittest.main()
