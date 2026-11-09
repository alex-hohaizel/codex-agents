import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('capsule', ROOT / 'standards/context_capsule.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class ContextCapsuleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'master.txt').write_text('accepted mechanism')
        def requirement(ident, priority='should', deps=()):
            return {'id': ident, 'source_ref': 'original-brief', 'verbatim': ident,
                    'interpretation': ident, 'acceptance': 'actual artifact',
                    'owner': 'integrator', 'due_gate': 'release', 'priority': priority,
                    'applicable': True, 'dependencies': list(deps)}
        self.data = {'schema_version': C.SCHEMA, 'project_id': 'P', 'native_revision': 'r1',
                     'requirements': [requirement('TASK'), requirement('IDENTITY', 'must', ['MASTER']),
                                      requirement('MASTER'), requirement('DEFERRED')],
                     'inputs': [{'id': 'M', 'path': 'master.txt',
                                 'sha256': hashlib.sha256((self.root / 'master.txt').read_bytes()).hexdigest()}],
                     'tasks': [{'id': 'T', 'objective': 'repair', 'owner': 'worker', 'authority_ref': 'actual-source',
                                'gate': 'design', 'stop': 'after artifact', 'recovery': 'read current pins',
                                'requirement_ids': ['TASK'], 'input_ids': ['M'],
                                'budget': {'attempts': 1}, 'outputs': ['reviewable artifact']}]}
        self.path = self.root / 'projection.json'
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data))

    def compile(self):
        return C.compile_packet(C.load(self.path), 'T', self.root, self.path)

    def test_always_retains_must_and_transitive_identity(self):
        packet = self.compile()
        self.assertEqual({x['id'] for x in packet['requirements']}, {'TASK', 'IDENTITY', 'MASTER'})
        self.assertEqual(packet['omitted_requirements'][0]['id'], 'DEFERRED')
        self.assertFalse(packet['quality_certified'])
        self.assertFalse(packet['authority_authenticated'])
        self.assertEqual(packet, self.compile())

    def test_old_master_hash_is_rejected_not_rebound(self):
        (self.root / 'master.txt').write_text('changed design')
        with self.assertRaisesRegex(C.ContextError, 'hash drift'):
            self.compile()

    def test_missing_requirement_and_dependency_cycle_rejected(self):
        self.data['requirements'][1]['dependencies'] = ['MISSING']
        self.save()
        with self.assertRaisesRegex(C.ContextError, 'unknown requirement dependency'):
            self.compile()
        self.data['requirements'][1]['dependencies'] = ['MASTER']
        self.data['requirements'][2]['dependencies'] = ['IDENTITY']
        self.save()
        with self.assertRaisesRegex(C.ContextError, 'cyclic'):
            self.compile()

    def test_duplicate_keys_and_nonfinite_rejected(self):
        for text in ['{"x":1,"x":2}', '{"x":NaN}']:
            self.path.write_text(text)
            with self.assertRaises(C.ContextError):
                C.load(self.path)

    def test_symlink_and_parent_escape_rejected(self):
        (self.root / 'alias.txt').symlink_to(self.root / 'master.txt')
        for value in ['alias.txt', '../master.txt', '/master.txt']:
            with self.assertRaises(C.ContextError):
                C.local(self.root, value)


if __name__ == '__main__':
    unittest.main()
