"""Declared-source continuity and negative admission; no host/model/provider calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'standards/context_capsule.py'
spec = importlib.util.spec_from_file_location('continuity_capsule', HELPER)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class ContextContinuityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.atelier').mkdir()
        self.path = self.root / 'projection.json'
        self.bind_path = self.root / C.DEFAULT_BINDINGS
        self.original = 'Preserve accepted identity.'
        (self.root / 'brief.md').write_text(self.original + '\nKeep editable masters.\n')
        self.native = {
            'schema': 'native-test/1',
            'requirements': [
                {'id': 'R01', 'source_text_uk': self.original, 'priority': 'must',
                 'dependencies': ['R02'], 'owner': 'product-owner'},
                {'id': 'R02', 'source_text_uk': 'Keep editable masters.', 'priority': 'should'},
                {'id': 'R03', 'source_text_uk': 'Optional later work.', 'priority': 'should'},
            ],
            'decisions': [{'id': 'D-old', 'text': 'Earlier scope'},
                          {'id': 'D-current', 'text': 'Accepted correction', 'supersedes': ['D-old']}],
            'deferred_work': [{'id': 'LATER', 'text': 'Retain deferred work'}],
            'identity': {'name': 'Accepted product'},
        }
        self.data = {
            'schema_version': C.SCHEMA, 'project_id': 'P', 'native_revision': 'r1',
            'requirements': [self.requirement('TASK')], 'inputs': [],
            'tasks': [{'id': 'T', 'objective': 'Continue the same task', 'owner': 'worker',
                       'authority_ref': 'actual owner source', 'gate': 'review',
                       'stop': 'after bounded result', 'recovery': 'restore the same source pins',
                       'requirement_ids': ['TASK'], 'input_ids': [],
                       'budget': {'attempts': 1}, 'outputs': ['reviewable result']}],
        }
        self.bind = {
            'schema': C.BINDINGS, 'project_root': str(self.root),
            'sources': [], 'expected_requirement_ids': ['R01', 'R02'],
            'expected_must_ids': ['R01'],
            'requirement_links': [{'requirement_id': 'R01', 'source_path': 'brief.md',
                                   'source_excerpt': self.original}],
        }
        self.save()

    def requirement(self, ident, **changes):
        return {'id': ident, 'source_ref': 'current-task', 'verbatim': ident,
                'interpretation': ident, 'acceptance': 'actual result',
                'owner': 'worker', 'due_gate': 'review', 'priority': 'should',
                'applicable': True, 'dependencies': [], **changes}

    def pin(self, ref, role, **extra):
        return {'path': ref, 'role': role,
                'sha256': hashlib.sha256((self.root / ref).read_bytes()).hexdigest(), **extra}

    def save(self):
        self.path.write_text(json.dumps(self.data))
        (self.root / 'registry.json').write_text(json.dumps(self.native))
        self.bind['sources'] = [self.pin('registry.json', 'requirements',
                                         requirement_ids=['R01', 'R02']),
                                self.pin('brief.md', 'original-request')]
        self.bind_path.write_text(json.dumps(self.bind))

    def save_manifest(self):
        self.bind_path.write_text(json.dumps(self.bind))

    def compile(self, **kwargs):
        return C.compile_packet(C.load(self.path), 'T', self.root, self.path, **kwargs)

    def test_native_must_and_dependencies_survive_narrow_assignment(self):
        packet = self.compile(require_complete=True)
        self.assertEqual({x['id'] for x in packet['requirements']}, {'TASK', 'R01', 'R02'})
        source = next(x for x in packet['requirements'] if x['id'] == 'R01')
        self.assertEqual(source['verbatim'], self.original)
        self.assertEqual(source['source_ref'], 'registry.json')
        self.assertEqual(source['source_sha256'], self.bind['sources'][0]['sha256'])
        self.assertEqual(source['raw_native_record'], self.native['requirements'][0])
        self.assertEqual(packet['context_coverage']['status'], 'verified-declared-bindings')
        self.assertEqual(packet['context_coverage']['requirement_checks'][0]['status'],
                         'verified-excerpt')
        self.assertEqual(next(x for x in packet['omitted_requirements'] if x['id'] == 'R03')['reason'],
                         'not assigned/dependent/must/always-review')
        self.assertFalse(packet['quality_certified'])
        self.assertFalse(packet['authority_authenticated'])
        self.assertFalse(packet['source_completeness_authenticated'])
        self.assertEqual(packet, self.compile(require_complete=True))

    def test_actual_management_request_schema_keeps_all_rows_and_provenance(self):
        management = ROOT / 'docs/evolution/2026-11-10/REQUESTS.json'
        raw = management.read_bytes()
        native = json.loads(raw)
        (self.root / 'management.json').write_bytes(raw)
        self.bind['sources'] = [self.pin('management.json', 'requirements')]
        ids = [x['id'] for x in native['requirements']]
        self.assertGreaterEqual(len(ids), 27)
        self.bind.update(expected_requirement_ids=ids, expected_must_ids=ids,
                         requirement_links=[])
        self.save_manifest()
        packet = self.compile(require_complete=True)
        rows = {x['id']: x for x in packet['requirements']}
        self.assertEqual(set(rows), set(ids) | {'TASK'})
        for original in native['requirements']:
            row = rows[original['id']]
            self.assertEqual(row['verbatim'], original['source_text_uk'])
            self.assertEqual(row['source_ref'], 'management.json')
            self.assertEqual(row['source_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(row['raw_native_record'], original)
            self.assertEqual(row['priority'], 'must')

    def test_legacy_capsule_shape_and_cli_verify_stay_usable_but_unverified(self):
        self.bind_path.unlink()
        packet = self.compile()
        self.assertNotIn('context_coverage', packet)
        self.assertFalse(packet['source_completeness_authenticated'])
        self.assertEqual({x['id'] for x in packet['requirements']}, {'TASK'})
        (self.root / 'old.json').write_text(json.dumps(packet))
        result = self.command('verify', output='old.json')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['context_coverage'], 'unverified')
        with self.assertRaisesRegex(C.ContextError, 'verified declared context'):
            self.compile(require_complete=True)

    def test_required_source_drift_or_missing_always_blocks_not_only_strict_flag(self):
        for condition in ('changed', 'missing'):
            with self.subTest(condition=condition):
                self.save()
                if condition == 'changed':
                    (self.root / 'brief.md').write_text('Changed original')
                else:
                    (self.root / 'brief.md').unlink()
                with self.assertRaises(C.ContextError):
                    self.compile()
                (self.root / 'brief.md').write_text(self.original + '\nKeep editable masters.\n')

    def test_wrong_project_binding_and_multiple_manifests_fail(self):
        self.bind['project_root'] = str(self.root / 'another-project')
        self.save_manifest()
        with self.assertRaisesRegex(C.ContextError, 'another project'):
            self.compile()
        self.bind['project_root'] = str(self.root)
        self.save_manifest()
        (self.root / 'other.json').write_text(json.dumps(self.bind))
        with self.assertRaisesRegex(C.ContextError, 'multiple context'):
            self.compile(bindings_path='other.json')

    def test_missing_expected_native_id_cannot_be_faked_by_projection(self):
        self.data['requirements'].append(self.requirement('R-missing', source_ref='registry.json'))
        self.path.write_text(json.dumps(self.data))
        self.bind['expected_requirement_ids'].append('R-missing')
        self.save_manifest()
        with self.assertRaisesRegex(C.ContextError, 'omits/weakens'):
            self.compile()

    def test_source_requirement_ids_are_registry_bindings_not_raw_quote_links(self):
        self.bind['sources'][1]['requirement_ids'] = ['R01']
        self.save_manifest()
        with self.assertRaisesRegex(C.ContextError, 'absent from native register'):
            self.compile()

    def test_expected_must_cannot_be_weakened_in_native_or_projection(self):
        self.native['requirements'][0]['priority'] = 'should'
        self.save()
        with self.assertRaisesRegex(C.ContextError, 'omits/weakens'):
            self.compile()
        self.native['requirements'][0]['priority'] = 'must'
        self.save()
        baseline = self.requirement('R01', source_ref='registry.json', verbatim=self.original,
                                    priority='must', dependencies=['R02'])
        for changes in ({'priority': 'should'}, {'applicable': False},
                        {'dependencies': []}, {'verbatim': 'A weaker summary'},
                        {'source_ref': 'another.json'}):
            with self.subTest(changes=changes):
                self.data['requirements'] = [self.requirement('TASK'), {**baseline, **changes}]
                self.path.write_text(json.dumps(self.data))
                with self.assertRaisesRegex(C.ContextError, 'CONTEXT_CONFLICT'):
                    self.compile()

    def test_original_excerpt_must_be_in_both_pinned_source_and_requirement(self):
        for quote in ('An invented quote', 'Keep editable masters.'):
            with self.subTest(quote=quote):
                self.bind['requirement_links'][0]['source_excerpt'] = quote
                self.save_manifest()
                with self.assertRaisesRegex(C.ContextError, 'excerpt not preserved'):
                    self.compile()

    def test_optional_gap_is_visible_usable_and_never_complete(self):
        self.bind['sources'].append({'path': 'optional.md', 'role': 'optional-reference',
                                     'sha256': '0' * 64, 'required': False})
        self.save_manifest()
        packet = self.compile()
        coverage = packet['context_coverage']
        self.assertEqual(coverage['status'], 'incomplete')
        self.assertFalse(coverage['issues'][0]['blocking'])
        with self.assertRaisesRegex(C.ContextError, 'verified declared context'):
            self.compile(require_complete=True)

    def test_native_decisions_deferred_work_identity_and_corrections_keep_provenance(self):
        packet = self.compile(require_complete=True)
        self.assertEqual([x['id'] for x in packet['decisions']], ['D-old', 'D-current'])
        self.assertEqual([x['id'] for x in packet['current_decisions']], ['D-current'])
        self.assertEqual(packet['corrections'][0]['supersedes'], ['D-old'])
        for row in [*packet['decisions'], *packet['deferred_work'], *packet['native_identity']]:
            self.assertEqual(row['source_ref'], 'registry.json')
            self.assertEqual(row['source_sha256'], self.bind['sources'][0]['sha256'])
        self.assertEqual(packet['deferred_work'][0]['id'], 'LATER')
        self.assertEqual(packet['native_identity'][0]['name'], 'Accepted product')

    def test_decision_missing_duplicate_cycle_do_not_silently_pick_winner(self):
        scenarios = [
            [{'id': 'N', 'supersedes': ['missing']}],
            [{'id': 'D', 'text': 'one'}, {'id': 'D', 'text': 'another'}],
            [{'id': 'A', 'supersedes': ['B']}, {'id': 'B', 'supersedes': ['A']}],
        ]
        for decisions in scenarios:
            with self.subTest(decisions=decisions):
                result = C.reconcile_decisions(decisions)
                self.assertEqual(result['current_decisions'], decisions)
                self.assertTrue(result['issues'])
                self.native['decisions'] = decisions
                self.save()
                with self.assertRaisesRegex(C.ContextError, 'CONTEXT_CONFLICT'):
                    self.compile()
        decisions = [{'id': 'old', 'time': '2020'}, {'id': 'new', 'time': '2026'}]
        self.assertEqual(C.reconcile_decisions(decisions)['current_decisions'], decisions)

    def test_symlinks_traversal_private_files_and_malformed_sources_fail(self):
        (self.root / 'alias.md').symlink_to(self.root / 'brief.md')
        (self.root / '.env').write_text('private fixture; no actual credential')
        for ref in ('alias.md', '../brief.md', '/brief.md', '.env'):
            with self.subTest(path=ref):
                self.bind['sources'] = [{'path': ref, 'role': 'original-request', 'sha256': '0' * 64}]
                self.save_manifest()
                with self.assertRaises(C.ContextError):
                    self.compile()
        self.save()
        self.bind['sources'].append(copy.deepcopy(self.bind['sources'][0]))
        self.save_manifest()
        with self.assertRaisesRegex(C.ContextError, 'duplicated/self-bound'):
            self.compile()

    def test_duplicate_json_overflow_and_unsupported_structured_source_fail(self):
        for raw in ('{"schema":"one","schema":"two"}', '{"value":1e999}'):
            self.bind_path.write_text(raw)
            with self.assertRaises(C.ContextError):
                self.compile()
        self.save()
        (self.root / 'registry.json').write_text('{"unrelated":"no native records"}')
        self.bind['sources'][0] = self.pin('registry.json', 'requirements')
        self.save_manifest()
        with self.assertRaisesRegex(C.ContextError, 'supported native record group'):
            self.compile()

    def test_inapplicable_dependency_cannot_disappear_or_be_treated_as_satisfied(self):
        self.native['requirements'][1].update(applicable=False,
                                               applicability_reason='Not part of this task')
        self.save()
        with self.assertRaisesRegex(C.ContextError, 'dependency marked inapplicable'):
            self.compile()

    def test_cli_complete_build_verify_and_changed_dependency(self):
        result = self.command('build', output='capsule.json', strict=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['context_coverage'], 'verified-declared-bindings')
        self.assertEqual(self.command('verify', output='capsule.json', strict=True).returncode, 0)
        self.native['deferred_work'].append({'id': 'NEW', 'text': 'Unfinished later correction'})
        self.save()
        self.assertNotEqual(self.command('verify', output='capsule.json', strict=True).returncode, 0)

    def command(self, operation, output, strict=False):
        return subprocess.run([sys.executable, '-B', str(HELPER), operation,
                               '--root', str(self.root), '--input', 'projection.json',
                               '--task', 'T', '--output', output,
                               *(['--require-complete'] if strict else [])],
                              text=True, capture_output=True, timeout=15, check=False)


if __name__ == '__main__':
    unittest.main()
