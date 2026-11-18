"""Keep actual child phase output when a native acceptance command times out."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'native_installer_acceptance.py'
SPEC = importlib.util.spec_from_file_location('acceptance_timeout_under_test', SOURCE)
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)


class NativeTimeoutReceipt(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
