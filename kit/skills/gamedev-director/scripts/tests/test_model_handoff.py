"""Integration boundaries: new handoffs cannot substitute transport for model proof."""
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

SOURCE = Path(__file__).absolute().parents[1]


def load(name):
    path = SOURCE / (name + '.py')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class ModelHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'handoff'
        self.pipeline = load('pipeline')
        self.pipeline.init(self.root, 'concepts', 'test-game')

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return json.loads((self.root / 'manifest.json').read_text())

    def write_manifest(self, m):
        (self.root / 'manifest.json').write_text(json.dumps(m))

    def test_new_draft_does_not_claim_model_readiness(self):
        result = self.pipeline.verify(self.root)
        self.assertTrue(result['valid'], result)
        self.assertIsNone(result['game_model_report'])
        self.assertFalse(result['quality_certified'])
        self.assertTrue(any('draft transport' in w for w in result['warnings']))

    def test_new_accepted_package_cannot_omit_model(self):
        m = self.manifest();m['stage_status'] = 'accepted';self.write_manifest(m)
        result = self.pipeline.verify(self.root)
        self.assertFalse(result['valid'])
        self.assertTrue(any('requires game_model' in e for e in result['errors']))

    def test_stale_model_is_rejected_even_in_transport(self):
        p = self.root / 'model.json';p.write_text('{}')
        m = self.manifest();m['game_model'] = {'path': p.name, 'sha256': '0'*64};self.write_manifest(m)
        result = self.pipeline.verify(self.root)
        self.assertFalse(result['valid'])
        self.assertTrue(any('stale game_model' in e for e in result['errors']))

    def test_current_draft_model_stays_review_pending(self):
        example = SOURCE.parent / 'assets/examples/model-no-enemy.json'
        p = self.root / 'model.json';p.write_bytes(example.read_bytes())
        m = self.manifest();m['game_model'] = {'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()};self.write_manifest(m)
        result = self.pipeline.verify(self.root)
        self.assertTrue(result['game_model_report']['structurally_valid'], result)
        self.assertFalse(result['game_model_report']['stage_ready'])

    def test_scoped_qa_and_incident_keep_actual_gate(self):
        model = {'path': 'model.json', 'sha256': '0'*64, 'acceptance_scope': 'slice_review', 'scope_ref': 'REQ-SLICE', 'scope_description': 'Review the accepted representative slice only'}
        self.assertEqual(self.pipeline.model_gate({'stage': 'qa', 'toolkit_version':'5.0.0', 'game_model': model}), ('slice', 'slice_review'))
        model['acceptance_scope'] = 'incident_analysis'
        self.assertEqual(self.pipeline.model_gate({'stage': 'liveops', 'toolkit_version':'5.0.0', 'game_model': model}), ('concept', 'incident_analysis'))

    def test_release_gate_cannot_be_downgraded_by_scope_label(self):
        self.assertEqual(self.pipeline.model_gate({'stage': 'release'}), ('release', 'full_stage'))
        with self.assertRaises(ValueError):
            self.pipeline.model_gate({'stage': 'release', 'game_model': {'acceptance_scope': 'slice_review', 'scope_ref': 'REQ', 'scope_description': 'A label cannot lower release'}})
        with self.assertRaises(ValueError):
            self.pipeline.model_gate({'stage': 'qa', 'game_model': {'acceptance_scope': 'slice_review'}})

    def test_accepted_concept_qa_preserves_unselected_production(self):
        # Synthetic integrity fixture, never a claim of real design/player QA.
        gm = load('game_model')
        import importlib.util
        spec = importlib.util.spec_from_file_location('current_v4_fixture', SOURCE.parent / 'tests/test_v4_contract.py')
        fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
        model = fixture.fixture(self.root)
        proof = self.root / 'review.md';proof.write_text('Synthetic unit-test independent observation, not a real game review.')
        proof_hash = hashlib.sha256(proof.read_bytes()).hexdigest()
        model['evidence'] = [{'id': 'EV-'+c['id'], 'domain': c['domain'], 'check_id': c['id'], 'stage': 'concept', 'modality': 'document', 'proof_path': 'review.md', 'sha256': proof_hash, 'model_sha256': gm.digest(model), 'scope_sha256':gm.scope_digest(model,c['domain'],c['id']), 'observer_id': 'synthetic-reviewer', 'author_ids': [], 'method': 'Synthetic integrity fixture', 'observed_at': '2026-11-02T10:00:00+00:00', 'environment': 'unit test', 'origin': c['origin']} for c in gm.requirements(model, 'concept')]
        model_path = self.root / 'model.json';model_path.write_text(json.dumps(model))
        (self.root / 'report.txt').write_text('Synthetic scoped review report')
        (self.root / 'defects.txt').write_text('Synthetic scoped defects inventory')
        artifacts = []
        for ident, path, kind in [('REPORT', 'report.txt', 'test_report'), ('DEFECTS', 'defects.txt', 'defects'), ('MODEL', 'model.json', 'game_model'), ('PROOF', 'review.md', 'evidence'), ('CONTRACT','contract.md','contract'), ('ENTRY', 'START_HERE.md', 'human_entrypoint')]:
            artifacts.append({'id': ident, 'path': path, 'kind': kind, 'sha256': hashlib.sha256((self.root/path).read_bytes()).hexdigest(), 'status': 'final', 'author_ids': ['synthetic-author'] if kind!='evidence' else [], 'depends_on': []})
        records = {'requirements': [{'id':'REQ-REVIEW', 'status':'met', 'owner':'synthetic-author', 'acceptance':'Bounded independent concept review only', 'artifact_ids':['REPORT'], 'evidence_ids':['PROOF']}], 'decisions': [], 'claims': [], 'reviews': []}
        for a in artifacts:
            if a['kind'] not in {'evidence', 'human_entrypoint'}:
                records['reviews'].append({'id':'REV-'+a['id'], 'status':'pass', 'reviewer_id':'synthetic-reviewer', 'artifact_ids':[a['id']], 'artifact_hashes':{a['id']:a['sha256']}, 'dependency_hashes':{}, 'evidence_ids':['PROOF'], 'evidence_hashes':{'PROOF':proof_hash}})
        for name, rows in records.items():
            path = self.root/'records'/(name+'.json');path.write_text(json.dumps({'items':rows}))
            artifacts.append({'id':'REC-'+name, 'path':'records/'+path.name, 'kind':'record', 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'status':'final', 'author_ids':[], 'depends_on':[]})
        m = self.manifest();m.update(stage='qa', stage_status='accepted', artifacts=artifacts)
        m['game_model']={'path':'model.json', 'sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(), 'acceptance_scope':'design_review', 'scope_ref':'REQ-REVIEW', 'scope_description':'Independent review before selecting production concept'}
        self.write_manifest(m)
        result = self.pipeline.verify(self.root, require_accepted=True)
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['model_gate'], 'concept')
        self.assertEqual(result['acceptance_scope'], 'design_review')
        self.assertEqual(result['required_decision_ids'], [])
        self.assertFalse(result['game_model_report']['scope_is_product_release'])
        self.assertEqual(records['decisions'], [])
        self.assertFalse(result['quality_certified'])


    def test_candidate_c1_completion_does_not_require_production_selection(self):
        self.test_accepted_concept_qa_preserves_unselected_production()
        manifest = self.manifest()
        manifest['stage'] = 'concepts'
        manifest['scope'] = 'candidate-C1'
        manifest['game_model'].update(acceptance_scope='candidate_completion', scope_description='Complete this specific C1 candidate before final game choice')
        profile = self.pipeline.acceptance_profile(manifest)
        self.assertEqual(profile['gate'], 'concept')
        self.assertEqual(profile['decisions'], [])
        present = {row['kind'] for row in manifest['artifacts']}
        review_path = self.root/'records/reviews.json'
        reviews = json.loads(review_path.read_text())['items']
        proof = next(row for row in manifest['artifacts'] if row['id']=='PROOF')
        for index, kind in enumerate(profile['kinds']):
            if kind in present:
                continue
            path = self.root/(kind+'.txt')
            path.write_text('Synthetic C1 candidate contract artifact: '+kind+'; not a real game acceptance')
            row = {'id':'CANDIDATE-'+str(index), 'path':path.name, 'kind':kind, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'status':'final', 'author_ids':['synthetic-author'], 'depends_on':[]}
            manifest['artifacts'].append(row)
            reviews.append({'id':'REV-'+row['id'], 'status':'pass', 'reviewer_id':'synthetic-reviewer', 'artifact_ids':[row['id']], 'artifact_hashes':{row['id']:row['sha256']}, 'dependency_hashes':{}, 'evidence_ids':['PROOF'], 'evidence_hashes':{'PROOF':proof['sha256']}})
        review_path.write_text(json.dumps({'items':reviews}))
        for row in manifest['artifacts']:
            if row['path']=='records/reviews.json':
                row['sha256']=hashlib.sha256(review_path.read_bytes()).hexdigest()
        self.write_manifest(manifest)
        result=self.pipeline.verify(self.root, require_accepted=True)
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['acceptance_scope'], 'candidate_completion')
        self.assertFalse(result['game_model_report']['scope_is_product_release'])
        self.assertEqual(json.loads((self.root/'records/decisions.json').read_text())['items'], [])
        # A candidate-completion label cannot weaken any production release.
        manifest['stage']='release'
        self.write_manifest(manifest)
        result=self.pipeline.verify(self.root, require_accepted=True)
        self.assertFalse(result['valid'])
        self.assertTrue(any('acceptance_scope is not allowed' in error for error in result['errors']))

    def test_current_manifest_rejects_previous_model_even_in_draft(self):
        self.assertEqual(self.manifest()['toolkit_version'], '5.0.0')
        p = self.root/'model.json'
        data=json.loads((SOURCE.parent/'assets/examples/model-no-enemy.json').read_text());data['schema_version']='3.0.0'
        p.write_text(json.dumps(data))
        m = self.manifest()
        m['game_model']={'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        self.write_manifest(m)
        result=self.pipeline.verify(self.root)
        self.assertFalse(result['valid'])
        self.assertTrue(any('requires game-model schema4.0.0' in x for x in result['errors']), result)

    def test_previous_toolkit_marker_is_rejected_without_modifying_input(self):
        manifest = self.manifest(); manifest['toolkit_version'] = '4.0.0'
        self.write_manifest(manifest)
        source = self.root / 'manifest.json'; before = source.read_bytes()
        result = self.pipeline.verify(self.root)
        self.assertFalse(result['valid'])
        self.assertTrue(any('current toolkit_version' in e for e in result['errors']))
        self.assertEqual(before, source.read_bytes())

    def test_missing_current_toolkit_marker_is_rejected(self):
        m = self.manifest();m.pop('toolkit_version');self.write_manifest(m)
        result = self.pipeline.verify(self.root)
        self.assertFalse(result['valid'])
        self.assertTrue(any('current toolkit_version' in e for e in result['errors']))
        self.assertFalse(result['quality_certified'])


if __name__ == '__main__':
    unittest.main()
