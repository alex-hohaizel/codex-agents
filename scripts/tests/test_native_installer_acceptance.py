"""Keep actual child phase output when a native acceptance command times out."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import stat

SOURCE = Path(__file__).resolve().parents[1] / 'native_installer_acceptance.py'
SPEC = importlib.util.spec_from_file_location('acceptance_timeout_under_test', SOURCE)
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)


class NativeTimeoutReceipt(unittest.TestCase):
    def test_expected_blocked_json_allows_only_tagged_source_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = acceptance.Acceptance.__new__(acceptance.Acceptance)
            runner.home = runner.logs = Path(directory)
            runner.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1'); runner.counter = 0
            code = 'import sys,json;print(\'agent-system-setup {"phase":"install-plan-check-start"}\',file=sys.stderr);print(\'agent-system-core {"status":"applying","completed":0,"total":33,"next_phase":"pending"}\',file=sys.stderr);print(json.dumps({"status":"blocked","reason":"actual lock refusal"},indent=2),file=sys.stderr);sys.exit(2)'
            result = runner.run('diagnostic-negative', [sys.executable, '-B', '-c', code], expected=(2,))
            self.assertEqual(result['status'], 'blocked')
            receipt = json.loads((Path(directory) / '001-diagnostic-negative.json').read_text(encoding='utf8'))
            self.assertIn('agent-system-setup ', receipt['stderr'])
            self.assertIn('agent-system-core ', receipt['stderr'])
            unknown = 'import sys;print(\'unknown-debug-line\\n{"status":"blocked"}\',file=sys.stderr);sys.exit(2)'
            with self.assertRaisesRegex(AssertionError, 'one JSON result'):
                runner.run('unknown-negative', [sys.executable, '-B', '-c', unknown], expected=(2,))

    def test_actual_terminated_child_retains_stdout_and_stderr_phase_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = acceptance.Acceptance.__new__(acceptance.Acceptance)
            runner.home = runner.logs = Path(directory)
            runner.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            runner.counter = 0
            code = 'import sys,time;print("buyer-phase-started",flush=True);print("package-scan-complete",file=sys.stderr,flush=True);time.sleep(10)'
            with self.assertRaises(subprocess.TimeoutExpired):
                runner.run('actual-timeout', [sys.executable, '-B', '-c', code], timeout=.5)
            report = json.loads((Path(directory) / '001-actual-timeout.json').read_text(encoding='utf8'))
            self.assertEqual(report['status'], 'timeout')
            self.assertIn('buyer-phase-started', report['stdout'])
            self.assertIn('package-scan-complete', report['stderr'])


class NativeFixtureInheritance(unittest.TestCase):
    def test_output_privacy_runs_before_any_fixture_children(self):
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/'received.zip';archive.write_bytes(b'not extracted by constructor')
            output=Path(directory)/'new owned output';observed=[]
            actual=acceptance.private_output
            def protected(path):
                actual(path)
                self.assertEqual(list(path.iterdir()),[])
                observed.append(path)
            with patch.object(acceptance,'private_output',protected):
                acceptance.Acceptance(archive,output)
            self.assertEqual(observed,[output.resolve()])
            self.assertTrue((output/'commands').is_dir())

    def test_windows_payload_dirs_inherit_and_posix_payload_dirs_stay_private(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);archive=root/'received.zip'
            with zipfile.ZipFile(archive,'w') as z:
                z.writestr('buyer/product-manifest.json',b'{}')
                z.writestr('buyer/deep/payload.txt',b'Exact received bytes.\n')
            with patch.object(acceptance,'WINDOWS',True):
                self.assertEqual(acceptance.extraction_directory_mode(),0o755)
                package=acceptance.extract(archive,root/'windows fixture')
            self.assertEqual((package/'deep/payload.txt').read_bytes(),b'Exact received bytes.\n')
            if os.name!='nt':
                self.assertEqual(stat.S_IMODE((package/'deep').stat().st_mode),0o755)
            with patch.object(acceptance,'WINDOWS',False):
                self.assertEqual(acceptance.extraction_directory_mode(),0o700)
                package=acceptance.extract(archive,root/'posix fixture')
            if os.name!='nt':
                self.assertEqual(stat.S_IMODE((package/'deep').stat().st_mode),0o700)


if __name__ == '__main__':
    unittest.main()
