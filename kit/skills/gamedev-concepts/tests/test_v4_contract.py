"""Synthetic authoring/evidence tests; never game balance/device/fun evidence."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm, vc = load('game_model'), load('v4_contract')


def fixture(root=None):
    """Finite C1 fixture with disclosed synthetic prose, no claimed observations."""
    original = gm.read_json(ROOT / 'assets/examples/model-compact-physics.json')
    model = copy.deepcopy(original)
    p = model['production']
    p['maturity'], p['unresolved'] = 'C1', []
    req = model['source_requirement_ids'][0]
    scene = model['scenarios'][0]['id']
    pin = {'path': 'contract.md', 'sha256': '0' * 64}
    if root:
        path = root / 'contract.md'
        path.write_text('Synthetic fixture contract for structural tests only.\n', encoding='utf-8')
        pin['sha256'] = gm.sha(path)
    for track in p['tracks']:
        if not track['enabled']:
            continue
        ident = 'CONTRACT-' + track['id']
        track.update(owner='fixture-author', receiver='fixture-receiver', requirement_ids=[req],
                     summary='Test intent; technical structural fixture only.',
                     contract_ids=[ident], invariants=['One accepted result per logical operation.'],
                     scenario_ids=[scene], concept_refs=[copy.deepcopy(pin)], spec_refs=[copy.deepcopy(pin)])
        p['contracts'].append({
            'id': ident, 'kind': 'behavior', 'version': '1', 'track_id': track['id'],
            'owner': 'fixture-author', 'requirement_ids': [req], 'purpose': 'Fixture operation semantics',
            'status': 'defined', 'inputs': [], 'outputs': [], 'read_refs': [], 'write_refs': [],
            'depends_on': [], 'algorithm': 'Accept an eligible operation once; reject a duplicate logical identity.',
            'invariants': ['Duplicate intent cannot produce a second grant.'],
            'cases': [
                {'id': ident + '-POS', 'scenario_id': scene, 'kind': 'positive', 'initial': {'count': 0},
                 'action': {'identity': 'one'}, 'expected': {'count': 1}},
                {'id': ident + '-NEG', 'scenario_id': scene, 'kind': 'negative', 'initial': {'count': 1},
                 'action': {'identity': 'one'}, 'expected': {'count': 1}}],
            'feedback': 'Accepted once, duplicate silent.', 'persistence': 'Uses explicit durable grant identity.',
            'telemetry': 'Reason and operation identity.', 'body': {
                'update_order': ['eligibility', 'apply'], 'time_domain': 'simulation tick',
                'exceptions': 'Reject invalid identity without mutation.', 'save_resume': 'Accepted identity persists.',
                'states': ['eligible', 'accepted'], 'failure': 'Rejected with reason',
                'recovery': 'Retry original identity', 'acceptance': 'Compare observable count'}})
    return model


def specialization(model, kind, body):
    contract = next(c for c in model['production']['contracts'] if c['track_id'] == 'TR04')
    contract['kind'] = kind
    contract['body'].update(body)
    return contract


class V4ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.model = fixture(self.root)

    def test_current_schema_only(self):
        current = gm.read_json(ROOT / 'assets/examples/model-compact-physics.json')
        self.assertEqual([], gm.design_errors(current))
        self.assertEqual('4.0.0', gm.schema()['properties']['schema_version']['const'])
        self.assertIn('production', gm.schema()['required'])
        previous = copy.deepcopy(current); previous['schema_version'] = '3.0.0'
        self.assertTrue(gm.design_errors(previous))
        with self.assertRaises(ValueError):
            gm.schema('3.0.0')

    def test_complete_c1_structure_needs_actual_independent_evidence(self):
        self.assertEqual([], gm.design_errors(self.model))
        result = gm.validate(self.model, self.root)
        self.assertEqual('C1', result['maturity'])
        self.assertFalse(result['stage_ready'])
        self.assertIn('v4.TR04.concept', result['missing_checks'])
        self.assertFalse(result['quality_certified'])

    def test_fresh_scaffold_has_no_prior_result_payload(self):
        created = vc.new_production()
        self.assertEqual('C0', created['maturity'])
        self.assertNotIn('migration', created)
        self.assertEqual([], created['contracts'])
        created['tracks'][0]['owner'] = 'changed'
        self.assertEqual('unassigned', vc.new_production()['tracks'][0]['owner'])

    def test_removed_conversion_metadata_is_rejected(self):
        self.model['production']['migration'] = {'from_schema': '3.0.0'}
        self.assertTrue(any('not part of the current model' in x for x in gm.design_errors(self.model)))

    def test_c0_scaffold_never_closes_concept(self):
        current = gm.read_json(ROOT / 'assets/examples/model-compact-physics.json')
        self.assertEqual([], gm.design_errors(current))
        result = gm.validate(current, self.root)
        self.assertFalse(result['stage_ready'])
        self.assertTrue(any('C0' in x for x in result['errors']))

    def test_four_model_missing_extension_fails_closed(self):
        del self.model['production']
        self.assertTrue(any('production' in e for e in gm.design_errors(self.model)))

    def test_missing_track_and_unknown_requirement_rejected(self):
        self.model['production']['tracks'].pop()
        self.assertTrue(any('tracks' in e for e in gm.design_errors(self.model)))
        self.model = fixture(self.root)
        self.model['production']['tracks'][0]['requirement_ids'] = ['UNDECLARED']
        self.assertTrue(any('unknown source' in e for e in gm.design_errors(self.model)))

    def test_disabled_ai_is_not_a_missing_tool_escape(self):
        self.model['production']['applicability']['ai']['enabled'] = True
        self.assertTrue(any('actors feature' in e for e in gm.design_errors(self.model)))

    def test_c1_requires_positive_negative_and_owner_case_scope(self):
        self.model['production']['contracts'][0]['cases'].pop()
        self.assertTrue(any('positive and negative' in e for e in gm.design_errors(self.model)))
        self.model = fixture(self.root)
        self.model['production']['tracks'][0]['contract_ids'] = []
        self.assertTrue(any('active track' in e or 'contract_ids' in e for e in gm.design_errors(self.model)))

    def test_pinned_concept_hash_and_path_escape_rejected(self):
        self.model['production']['tracks'][0]['concept_refs'][0]['sha256'] = 'f' * 64
        result = gm.validate(self.model, self.root)
        self.assertTrue(any('hash mismatch' in e for e in result['errors']))
        self.model['production']['tracks'][0]['concept_refs'][0]['path'] = '../outside.md'
        self.assertTrue(any('unsafe' in e for e in vc.errors(self.model, root=self.root)))

    def test_tuning_requires_bounded_initial(self):
        c = self.model['production']['contracts'][0]
        c['status'] = 'tuning'
        c['tuning'] = {'initial': 5, 'minimum': 1, 'maximum': 3, 'goal': 'readability', 'method': 'bounded test'}
        self.assertTrue(any('tuning' in e for e in gm.design_errors(self.model)))

    def test_causal_scope_reuses_unaffected_track_but_invalidates_dependents(self):
        p = self.model['production']
        a = next(c for c in p['contracts'] if c['track_id'] == 'TR04')
        b = next(c for c in p['contracts'] if c['track_id'] == 'TR17')
        b['depends_on'] = [a['id']]
        before = {t: gm.scope_digest(self.model, 'product', 'v4.' + t + '.concept') for t in ('TR04', 'TR17', 'TR15')}
        a['algorithm'] += ' Revised contact eligibility.'
        after = {t: gm.scope_digest(self.model, 'product', 'v4.' + t + '.concept') for t in before}
        self.assertNotEqual(before['TR04'], after['TR04'])
        self.assertNotEqual(before['TR17'], after['TR17'])
        self.assertEqual(before['TR15'], after['TR15'])
        effect = gm.impact(self.model, a['id'])['production_impact']
        self.assertEqual(['TR04', 'TR17'], effect['production_tracks'])

    def test_existing_domain_evidence_tracks_new_semantic_contracts(self):
        before = gm.scope_digest(self.model, 'systems', 'systems.design')
        c = next(c for c in self.model['production']['contracts'] if c['track_id'] == 'TR04')
        c['algorithm'] += ' changed'
        self.assertNotEqual(before, gm.scope_digest(self.model, 'systems', 'systems.design'))

    def test_damage_schema_rejects_empty_pipeline_and_conflated_commit(self):
        c = specialization(self.model, 'damage', {'pipeline': ['contact'],
                            'simulation_commit': 'after cloud ack', 'durable_commit': 'after cloud ack', 'cascade_limit': 0})
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('pipeline' in e for e in out))
        self.assertTrue(any('distinguished' in e for e in out))
        self.assertTrue(any('cascade_limit' in e for e in out))
        c['body']['pipeline'] = [{}]
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('pipeline' in e for e in out))

    def test_restore_pipeline_order_and_dirty_window_rejected(self):
        c = specialization(self.model, 'persistence', {'restore_pipeline': ['apply', 'envelope'], 'dirty_window_ms': -1})
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('restore_pipeline' in e for e in out))
        self.assertTrue(any('dirty_window' in e for e in out))

    def test_rng_exact_state_catalogue_binding_required(self):
        c = specialization(self.model, 'rng', {'streams': [{'id': 'combat', 'purpose': 'crit',
                           'state_field_ref': 'absent', 'draw_policy': 'accepted hit', 'distribution': 'uniform',
                           'bounds': [0, 9999], 'correlation': 'independent stream'}]})
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('state_field_ref' in e for e in out))

    def test_generator_bounded_repair_and_state_machine_links_required(self):
        c = specialization(self.model, 'generator', {'attempt_limit': 0})
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('attempt_limit' in e for e in out))
        c['kind'] = 'state_machine'
        c['body'].update(states=[{'id': 'alive', 'entry': 'initialize', 'exit': 'freeze'}],
                         transitions=[{'from': 'alive', 'to': 'missing', 'guard': 'zeroHP', 'priority': 1, 'effects': ['stop actions']}],
                         initial_state='alive')
        out = []
        vc.detailed_contract_errors(c, self.model['production'], out)
        self.assertTrue(any('unknown state' in e for e in out))

    def test_removed_converter_is_not_a_cli_command(self):
        source = ROOT / 'assets/examples/model-compact-physics.json'
        command = [sys.executable, str(ROOT / 'scripts/game_model.py'), 'migrate-v4', str(source), '--output', str(self.root / 'out.json')]
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(2, run.returncode)
        self.assertIn('invalid choice', run.stderr)
        self.assertFalse((self.root / 'out.json').exists())

    def complete_t_fixture(self):
        operations_module_spec = importlib.util.spec_from_file_location('production_fixture', ROOT / 'tests/test_production_contract.py')
        operations_module = importlib.util.module_from_spec(operations_module_spec)
        operations_module_spec.loader.exec_module(operations_module)
        p = self.model['production']
        p['maturity'] = 'T'
        p['operations'] = operations_module.valid_operations()
        req = self.model['source_requirement_ids'][0]
        p['operations']['recipes'][0]['requirement_ids'] = [req]
        p['operations']['obligations'][0]['requirement_id'] = req
        p['state_fields'] = [{'id': 'STATE-GRANTS', 'owner': 'TR17', 'type': 'array', 'units': 'logical operation IDs',
            'initial': [], 'classification': 'durable', 'scope': 'profile', 'authority': 'local single profile',
            'storage': 'transactional local database', 'encoding': 'UTF8 exact IDs', 'consistency_group': 'GROUP-PROFILE',
            'commit': 'transaction before critical grant confirmation', 'restore': 'validate IDs before apply',
            'merge': 'choose coherent branch', 'migration': 'versioned add-only field', 'retention': 'until profile deletion', 'status': 'defined'}]
        c = next(c for c in p['contracts'] if c['track_id'] == 'TR17')
        c['kind'] = 'persistence'
        c['body'].update({'authority': 'local profile authority',
            'consistency_groups': [{'id': 'GROUP-PROFILE', 'member_refs': ['STATE-GRANTS'],
                'atomicity': 'single local transaction', 'conflict_policy': 'preserve one coherent branch'}],
            'transaction': 'journaled atomic commit', 'generation_guard': 'reject stale revision',
            'disk_full': 'preserve old good generation and report unsaved', 'recovery': 'replay accepted journal',
            'restore_pipeline': ['envelope', 'owner', 'compatibility', 'migration', 'semantic_validation', 'apply', 'rebuild', 'safe_input'],
            'migration': 'pinned forward changes with golden save fixtures', 'clock_policy': 'simulation and calendar separate',
            'identity': 'profile owner immutable binding', 'cloud_policy': 'not in this synthetic fixture',
            'deletion_policy': 'explicit profile tombstone', 'dirty_window_ms': 250})
    def test_complete_t_structure_and_consistency_group_validation(self):
        self.complete_t_fixture()
        p = self.model['production']
        self.assertEqual([], gm.design_errors(self.model))
        self.assertEqual([], vc.errors(self.model, 'T', self.root))
        p['state_fields'][0]['consistency_group'] = 'WRONG'
        self.assertTrue(any('ownership mismatch' in e or 'omitted' in e for e in vc.errors(self.model, 'T')))

    def test_operation_toolchain_change_invalidates_only_consuming_track(self):
        operations_module_spec = importlib.util.spec_from_file_location('production_fixture', ROOT / 'tests/test_production_contract.py')
        operations_module = importlib.util.module_from_spec(operations_module_spec)
        operations_module_spec.loader.exec_module(operations_module)
        self.model['production']['operations'] = operations_module.valid_operations()
        track = next(t for t in self.model['production']['tracks'] if t['id'] == 'TR15')
        track['reads'] = ['REC-synthetic']
        before = {t: vc.scope_digest(self.model, 'v4.' + t + '.concept') for t in ('TR15', 'TR04')}
        self.model['production']['operations']['capabilities'][0]['toolchain']['version'] = 'fixture-v2'
        after = {t: vc.scope_digest(self.model, 'v4.' + t + '.concept') for t in before}
        self.assertNotEqual(before['TR15'], after['TR15'])
        self.assertEqual(before['TR04'], after['TR04'])

    def test_gate_flags_cannot_downgrade_production_maturity(self):
        for stage in ('preproduction', 'slice', 'release'):
            for lower in ('C0', 'C1'):
                with self.subTest(stage=stage, lower=lower):
                    result = gm.plan(self.model, stage, maturity=lower)
                    self.assertEqual('T', result['maturity'])
                    self.assertTrue(any('cannot lower' in e for e in result['errors']))

    def test_operation_gate_tracks_stage_and_assembly_is_due_from_slice(self):
        fixture_spec = importlib.util.spec_from_file_location('production_fixture', ROOT / 'tests/test_production_contract.py')
        ops = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(ops)
        p = self.model['production']
        p['operations'] = ops.valid_operations()
        p['operations']['obligations'][0].update(status='pending', due_gate='A')
        early = vc.errors(self.model, 'T', stage='preproduction')
        late = vc.errors(self.model, 'T', stage='slice')
        self.assertFalse(any('due obligation' in e for e in early))
        self.assertTrue(any('due obligation' in e for e in late))
        self.assertTrue(any('assembly evidence' in e for e in late))

    def test_direct_contract_api_cannot_lower_stage_floor(self):
        for stage in ('preproduction', 'slice', 'release'):
            for lower in ('C0', 'C1'):
                out = vc.errors(self.model, lower, stage=stage)
                self.assertTrue(any('direct caller cannot lower' in e for e in out), out)
                self.assertTrue(any('T requires' in e for e in out), out)

    def test_candidate_assembly_with_unknown_scope_never_closes_native_slice(self):
        fixture_spec = importlib.util.spec_from_file_location('production_fixture', ROOT / 'tests/test_production_contract.py')
        ops = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(ops)
        operations = ops.valid_operations()
        requirement = self.model['source_requirement_ids'][0]
        operations['recipes'][0]['requirement_ids'] = [requirement]
        operations['obligations'][0]['requirement_id'] = requirement
        operations['assemblies'] = [{'id': 'ASM-candidate', 'scene_ref': 'SCENE-absent',
            'build_digest': 'a' * 64, 'config_digest': 'b' * 64,
            'components': [{'id': 'ART-export', 'sha256': 'a' * 64, 'binding': 'fixture'}],
            'scenario': 'SCENARIO-absent', 'invariants': [{'id': 'INV', 'expected': 'one', 'observed': 'not run', 'verdict': 'pending'}],
            'evidence_refs': ['EV-absent'], 'author_id': 'author', 'reviewer_id': 'reviewer', 'proof_level': 'candidate'}]
        self.model['production']['operations'] = operations
        out = vc.errors(self.model, 'C1', stage='slice')
        self.assertTrue(any('native_verified assembly' in e for e in out), out)
        self.assertTrue(any('unknown assembly scenario' in e for e in out), out)
        self.assertTrue(any('unknown canonical evidence' in e for e in out), out)
        self.assertTrue(any('scene_ref' in e for e in out), out)

    def test_typed_action_reference_has_matching_scope_and_impact(self):
        model = gm.read_json(ROOT / 'assets/examples/model-camera-action.json')
        track = next(t for t in model['production']['tracks'] if t['id'] == 'TR06')
        track['reads'] = ['AGENT-RESPONDER']
        self.assertEqual([], gm.design_errors(model))
        before = vc.scope_digest(model, 'v4.TR06.concept')
        rule = next(r for r in model['domains']['systems']['rules'] if r['id'] == 'RULE-B')
        rule['change'] += ' Revised action.'
        self.assertNotEqual(before, vc.scope_digest(model, 'v4.TR06.concept'))
        effect = gm.impact(model, 'RULE-B')['production_impact']
        self.assertIn('TR06', effect['production_tracks'])
        self.assertIn('AGENT-RESPONDER', effect['affected_ids'])

    def test_native_assembly_requires_checked_device_receipt_not_only_metadata(self):
        self.complete_t_fixture()
        fixture_spec = importlib.util.spec_from_file_location('production_fixture', ROOT / 'tests/test_production_contract.py')
        ops = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(ops)
        operations, unused_context = ops.native_operations()
        requirement = self.model['source_requirement_ids'][0]
        operations['recipes'][0]['requirement_ids'] = [requirement]
        operations['obligations'][0]['requirement_id'] = requirement
        scenario = self.model['scenarios'][0]['id']
        assembly = operations['assemblies'][0]
        assembly.update(scenario=scenario, evidence_refs=['EV-DEVICE'])
        self.model['production']['operations'] = operations
        image = self.root / 'fixture.png'
        image.write_bytes(b'\x89PNG\r\n\x1a\nsynthetic fixture only')
        apk = self.root / 'fixture.apk'
        with zipfile.ZipFile(apk, 'w') as archive:
            archive.writestr('AndroidManifest.xml', 'synthetic fixture manifest')
            archive.writestr('classes.dex', 'synthetic fixture dex')
        build_hash = gm.sha(apk)
        assembly['build_digest'] = build_hash
        shared = {'schema_version': 'game-atelier-observation/1', 'build_sha256': build_hash,
            'platform': 'android', 'scenario_ids': [scenario],
            'samples': [{'path': image.name, 'sha256': gm.sha(image), 'kind': 'image'}]}
        build = dict(shared, kind='build', artifact_path=apk.name, artifact_sha256=build_hash, toolchain='synthetic fixture')
        device = dict(shared, kind='device', device={'physical': True, 'platform': 'android', 'model': 'synthetic test fixture', 'os': 'fixture'})
        evidence = []
        for ident, name, receipt, check_id, origin in (
                ('EV-BUILD', 'build.json', build, 'product.native_build', 'native_build'),
                ('EV-DEVICE', 'device.json', device, 'product.device', 'device_observation')):
            path = self.root / name
            path.write_text(json.dumps(receipt), encoding='utf-8')
            evidence.append({'id': ident, 'domain': 'product', 'check_id': check_id,
                'stage': 'slice', 'modality': receipt['kind'], 'origin': origin,
                'proof_path': name, 'sha256': gm.sha(path), 'model_sha256': gm.digest(self.model),
                'scope_sha256': gm.scope_digest(self.model, 'product', check_id),
                'observer_id': 'synthetic-fixture-observer', 'author_ids': [],
                'method': 'synthetic transport fixture only; no physical truth',
                'observed_at': datetime.now(timezone.utc).isoformat(), 'environment': 'test fixture',
                'build_sha256': build_hash, 'scenario_ids': [scenario], 'platform': 'android'})
        self.model['evidence'] = evidence
        self.assertEqual([], gm.design_errors(self.model))
        result = gm.validate(self.model, self.root, 'slice')
        self.assertFalse(result['stage_ready'])  # Other domain/iOS evidence intentionally absent.
        self.assertFalse(any('native assembly' in e for e in result['errors']), result['errors'])
        # Keep declaration metadata plausible, but change the actual byte-pinned
        # receipt to a different build. This must reopen native assembly proof.
        device['build_sha256'] = 'f' * 64
        path = self.root / 'device.json'
        path.write_text(json.dumps(device), encoding='utf-8')
        evidence[1]['sha256'] = gm.sha(path)
        result = gm.validate(self.model, self.root, 'slice')
        self.assertTrue(any('native assembly lacks validated matching device' in e for e in result['errors']), result['errors'])

    def test_v4_schema_artifact_matches_code(self):
        self.assertEqual(gm.schema('4.0.0'), gm.read_json(ROOT / 'assets/game-model.schema.json'))


if __name__ == '__main__':
    unittest.main()
