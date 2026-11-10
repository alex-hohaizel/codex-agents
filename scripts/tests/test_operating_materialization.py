"""Isolated self-contained resource delivery; no host installation or execution."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/materialize_standards.py'
spec = importlib.util.spec_from_file_location('materialize_operating', SCRIPT)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class OperatingMaterializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'releases').mkdir()
        (self.root / 'releases/current.json').write_text(json.dumps({'stable_skill_names': ['one', 'two']}))
        (self.root / 'standards').mkdir()
        self.expected = {}
        for source in M.RESOURCES:
            data = ('fixture reviewed bytes: ' + source + '\n').encode()
            (self.root / 'standards' / source).write_bytes(data)
            self.expected[source] = data

    def run_materializer(self, *arguments):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--root', str(self.root), *arguments],
                                text=True, capture_output=True, timeout=8)
        return result.returncode, json.loads(result.stdout)

    def test_all_seven_resources_are_local_in_core_and_optional_orchestrator(self):
        code, result = self.run_materializer()
        self.assertEqual(code, 0, result)
        self.assertEqual(len(result['resources']), 7)
        for source, target in M.RESOURCES.items():
            for bundle in ('kit/skills/one', 'kit/skills/two', 'optional-skills/atelier-orchestrator'):
                self.assertEqual((self.root / bundle / target).read_bytes(), self.expected[source])
        self.assertTrue(all(row['core_bundles'] == 2 and row['optional_bundles'] == 1 for row in result['resources']))
        code, checked = self.run_materializer('--check')
        self.assertEqual(code, 0, checked)

    def test_missing_new_master_prevents_any_partial_replacement(self):
        sentinel = self.root / 'kit/skills/one/references/production-quality.md'
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text('preserved old bundle')
        (self.root / 'standards/ai_production.py').unlink()
        code, result = self.run_materializer()
        self.assertEqual(code, 1, result)
        self.assertEqual(sentinel.read_text(), 'preserved old bundle')
        self.assertFalse((self.root / 'kit/skills/two').exists())

    def test_linked_target_ancestor_is_rejected_before_writing_other_bundles(self):
        outside = self.root / 'outside';outside.mkdir()
        bundle = self.root / 'kit/skills/two';bundle.mkdir(parents=True)
        try:
            (bundle / 'references').symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(str(error))
        code, result = self.run_materializer()
        self.assertEqual(code, 1, result)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.root / 'kit/skills/one').exists())

    def test_check_detects_drift_without_replacing_it(self):
        self.assertEqual(self.run_materializer()[0], 0)
        changed = self.root / 'optional-skills/atelier-orchestrator/scripts/ai_production.py'
        changed.write_text('retained unexplained drift')
        code, result = self.run_materializer('--check')
        self.assertEqual(code, 1, result)
        self.assertEqual(changed.read_text(), 'retained unexplained drift')
        self.assertTrue(any('atelier-orchestrator/scripts/ai_production.py' in row for row in result['errors']))


if __name__ == '__main__':
    unittest.main()
