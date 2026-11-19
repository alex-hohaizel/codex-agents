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
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('materialize_operating', SCRIPT)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class OperatingMaterializationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.constructors = ('agent-foundry', 'design-specialist-skills')
        self.core = ('one', 'two', *self.constructors)
        self.orchestrator = self.root / 'optional-skills/atelier-orchestrator'
        self.managed_model = json.loads((ROOT / 'releases/current.json').read_bytes())['managed_model']
        (self.root / 'releases').mkdir()
        (self.root / 'releases/current.json').write_text(json.dumps({
            'stable_skill_names': self.core, 'managed_model': self.managed_model,
        }))
        self.expected = {}
        for source in (*M.RESOURCES, *M.CORE_RESOURCES, *M.CONSTRUCTOR_RESOURCES):
            data = ('fixture reviewed bytes: ' + source + '\n').encode()
            master = self.root / 'standards' / source
            master.parent.mkdir(parents=True, exist_ok=True)
            master.write_bytes(data)
            self.expected[source] = data
        for template in M.ORCHESTRATOR_TEMPLATES:
            master = self.root / 'kit/skills/agent-foundry' / template
            master.parent.mkdir(parents=True, exist_ok=True)
            master.write_text('fixture reviewed template: ' + template + '\n')

    def run_materializer(self, *arguments):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--root', str(self.root), *arguments],
                                text=True, capture_output=True, timeout=8)
        return result.returncode, json.loads(result.stdout)

    def test_operating_resources_are_local_in_core_and_optional_orchestrator(self):
        code, result = self.run_materializer()
        self.assertEqual(code, 0, result)
        resources = {row['source']: row for row in result['resources']}
        self.assertIn('standards/tool-compatibility.md', resources)
        for source, target in M.RESOURCES.items():
            self.assertEqual((self.orchestrator / target).read_bytes(), self.expected[source])
            for name in self.core:
                self.assertEqual((self.root / 'kit/skills' / name / target).read_bytes(), self.expected[source])
            row = resources['standards/' + source]
            self.assertEqual((row['core_bundles'], row['optional_bundles']), (len(self.core), 1))
        for source, target in M.CORE_RESOURCES.items():
            for name in self.core:
                self.assertEqual((self.root / 'kit/skills' / name / target).read_bytes(), self.expected[source])
            self.assertFalse((self.orchestrator / target).exists())
        for source, target in M.CONSTRUCTOR_RESOURCES.items():
            for name in self.core:
                path = self.root / 'kit/skills' / name / target
                if name in self.constructors:
                    self.assertEqual(path.read_bytes(), self.expected[source])
                else:
                    self.assertFalse(path.exists())
            self.assertFalse((self.orchestrator / target).exists())
        for name in self.core:
            model = self.root / 'kit/skills' / name / 'assets/managed-model.json'
            if name in self.constructors:
                self.assertEqual(json.loads(model.read_bytes()), self.managed_model)
            else:
                self.assertFalse(model.exists())
        for template in M.ORCHESTRATOR_TEMPLATES:
            master = self.root / 'kit/skills/agent-foundry' / template
            self.assertEqual((self.orchestrator / template).read_bytes(), master.read_bytes())
        self.assertFalse((self.orchestrator / 'assets/managed-model.json').exists())
        code, checked = self.run_materializer('--check')
        self.assertEqual(code, 0, checked)

    def test_missing_new_master_prevents_any_partial_replacement(self):
        sentinel = self.root / 'kit/skills/one/references/production-quality.md'
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text('preserved old bundle')
        (self.root / 'standards/ai_production.py').unlink()
        code, result = self.run_materializer()
        self.assertEqual(code, 1, result)
        self.assertEqual(result['errors'], ['standards/ai_production.py: missing/linked master'])
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
        self.assertTrue(result['errors'])
        self.assertTrue(all(error.startswith('kit/skills/two/references/') and error.endswith(': linked target path')
                            for error in result['errors']), result)
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
