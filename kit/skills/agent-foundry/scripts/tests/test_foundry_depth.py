import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
import shutil
import subprocess
import sys
import test_foundry as factory_fixtures

S = Path(__file__).resolve().parents[1] / 'check_foundry_depth.py'
spec = importlib.util.spec_from_file_location('check_foundry_depth', S)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DepthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.root = Path(self.tmp.name)
        module = self.root / 'skills' / 'target'
        module.mkdir(parents=True)
        (module / 'SKILL.md').write_text('---\nname: target\ndescription: A specific target agent\n---\nActual workflow\n')
        (self.root / 'out.txt').write_text('accepted result')
        self.digest = hashlib.sha256((self.root / 'out.txt').read_bytes()).hexdigest()
        contract_path = 'skills/target/SKILL.md'
        cd = hashlib.sha256((self.root / contract_path).read_bytes()).hexdigest()
        self.subject = {'blueprint_id': 'BP-1', 'blueprint_revision': 1, 'blueprint_sha256': 'a' * 64, 'authority_source': 'synthetic authority fixture'}
        self.model = {
            'schema_version': 'foundry-depth/2', 'is_template': False, 'maturity': 'M2',
            'subject': dict(self.subject),
            'requirements': [{'id':'REQ','source':'raw request','owner':'author','acceptance':'exact output','negative_case':'changed output fails','due_gate':'delivery','applicability':'applicable'}],
            'systems': [{'id':'SYS','purpose':'produce','owner':'author','input_contract':'input','output_contract':'text','invariants':['identity']}],
            'rules': [{'id':'RULE','requirement_ids':['REQ'],'input_contract':'input','steps':['transform'],'output_contract':'text','oracle':'exact comparison','failure_policy':'preserve input'}],
            'state_fields': [],
            'capabilities': [{'id':'CAP','tool':'actual tool','operation':'render','environment':'local','status':'integrated','evidence_ids':['EV']}],
            'operations': [{'id':'OP','requirement_ids':['REQ'],'capability_id':'CAP','recipe_id':'REC','consumer_id':'recipient','output_ids':['OUT'],'parameter_bindings':[{'requirement_id':'REQ','field':'output','status':'consumed','consumption_check':'compare actual output'}]}],
            'recipes': [{'id':'REC','operation_ids':['OP'],'input_ids':['raw request'],'output_ids':['OUT'],'consumer_id':'recipient','steps':['render','compare'],'validators':['exact text'],'repair_policy':'changed hypothesis after failure'}],
            'artifacts': [{'id':'OUT','path':'out.txt','sha256':self.digest,'owner':'author','kind':'text'}],
            'evidence': [{'id':'EV','artifact_ids':['OUT'],'subject_sha256':{'OUT':self.digest},'level':'integration','result':'pass','observer':'reviewer','independent':True,'environment':'local','method':'consumer scenario','scope':'OUT in scenario'}],
            'modules': [{'id':'MOD','name':'target','path':'skills/target','requirement_ids':['REQ'],'inherited_contracts':[{'kind':k,'path':contract_path,'sha256':cd} for k in sorted(mod.KINDS)]}],
            'assemblies': [{'id':'ASM','artifact_ids':['OUT'],'required_evidence_ids':['EV'],'consumer_id':'recipient','scenario':'open output','expected_result':'accepted result'}]
        }

    def tearDown(self):
        self.tmp.cleanup()

    def check_bad(self, mutate, expected):
        m = copy.deepcopy(self.model)
        mutate(m)
        errors = mod.validate(m, self.root, True, self.subject)
        self.assertTrue(any(expected in x for x in errors), errors)

    def test_valid_bound_package(self):
        self.assertEqual(mod.validate(self.model, self.root, True, self.subject), [])

    def test_ready_requires_current_session_even_with_well_formed_subject(self):
        self.assertTrue(any('current Foundry session' in x for x in mod.validate(self.model, self.root, True)))

    def test_missing_blueprint_subject_fails(self):
        self.check_bad(lambda m:m.pop('subject'), 'subject must bind')

    def test_unrelated_blueprint_subject_fails(self):
        self.check_bad(lambda m:m['subject'].update(blueprint_id='OTHER'), 'subject differs')

    def test_stale_blueprint_revision_fails(self):
        self.check_bad(lambda m:m['subject'].update(blueprint_revision=2), 'subject differs')

    def test_stale_blueprint_hash_fails(self):
        self.check_bad(lambda m:m['subject'].update(blueprint_sha256='b'*64), 'subject differs')

    def test_wrong_authority_source_fails(self):
        self.check_bad(lambda m:m['subject'].update(authority_source='OTHER'), 'subject differs')

    def test_bool_is_not_a_blueprint_revision(self):
        self.check_bad(lambda m:m['subject'].update(blueprint_revision=True), 'positive blueprint_revision')

    def test_plan_can_be_checked_before_current_approval(self):
        model = copy.deepcopy(self.model)
        model['maturity'] = 'M1'
        self.assertEqual(mod.validate(model, self.root), [])

    def test_unbound_sketch_remains_a_plan(self):
        model = copy.deepcopy(self.model)
        model['maturity'] = 'M0'
        model.pop('subject')
        self.assertEqual(mod.validate(model, self.root), [])

    def test_malformed_current_binding_fails_without_crashing(self):
        self.assertTrue(any('current session subject' in x for x in mod.validate(self.model, self.root, True, [])))

    def test_template_cannot_be_ready(self):
        self.check_bad(lambda m:m.update(is_template=True), 'template')

    def test_missing_evidence(self):
        self.check_bad(lambda m:m.update(evidence=[]), 'missing reference')

    def test_source_proof_is_not_integration(self):
        self.check_bad(lambda m:m['evidence'][0].update(level='source'), 'appropriate passing evidence')

    def test_stale_subject_digest(self):
        self.check_bad(lambda m:m['evidence'][0]['subject_sha256'].update(OUT='0'*64), 'stale')

    def test_changed_actual_bytes(self):
        (self.root/'out.txt').write_text('wrong')
        self.assertTrue(any('digest mismatch' in x for x in mod.validate(self.model,self.root,True,self.subject)))

    def test_self_review(self):
        self.check_bad(lambda m:m['evidence'][0].update(observer='author'), 'independent')

    def test_pending_applicability(self):
        self.check_bad(lambda m:m['requirements'][0].update(applicability='pending',rationale='not known'), 'pending applicability')

    def test_unsupported_parameter(self):
        self.check_bad(lambda m:m['operations'][0]['parameter_bindings'][0].update(status='unsupported'), 'not consumed')

    def test_missing_recipe(self):
        self.check_bad(lambda m:m.update(recipes=[]), 'missing recipe')

    def test_unknown_requirement(self):
        self.check_bad(lambda m:m['operations'][0].update(requirement_ids=['GHOST']), 'missing reference')

    def test_missing_inherited_domain_contract(self):
        self.check_bad(lambda m:m['modules'][0].update(inherited_contracts=m['modules'][0]['inherited_contracts'][:1]), 'missing inherited contract')

    def test_path_escape(self):
        self.check_bad(lambda m:m['artifacts'][0].update(path='../outside.txt'), 'unsafe path')

    def test_symlink(self):
        (self.root/'link.txt').symlink_to(self.root/'out.txt')
        self.check_bad(lambda m:m['artifacts'][0].update(path='link.txt'), 'symlink')

    def test_wrong_module(self):
        self.check_bad(lambda m:m['modules'][0].update(path='../target'), 'module path')

    def test_not_run_is_not_tested(self):
        self.check_bad(lambda m:m['evidence'][0].update(result='not_run'), 'appropriate passing evidence')

    def test_malformed_nested_record_fails(self):
        self.check_bad(lambda m:m['operations'][0].update(parameter_bindings=['wrong']), 'invalid parameter')

    def test_m0_is_not_ready(self):
        self.check_bad(lambda m:m.update(maturity='M0'), 'ready requires M2')

    def test_uncovered_requirement(self):
        def add(m):
            r=copy.deepcopy(m['requirements'][0]);r['id']='EXTRA';m['requirements'].append(r)
        self.check_bad(add,'no production operation')

    def test_recipe_consumer_mismatch(self):
        self.check_bad(lambda m:m['recipes'][0].update(consumer_id='someone else'),'consumer mismatch')

    def test_wrong_capability_output_witness(self):
        def change(m):
            a=copy.deepcopy(m['artifacts'][0]);a['id']='OTHER';m['artifacts'].append(a)
            m['evidence'][0]['artifact_ids']=['OTHER'];m['evidence'][0]['subject_sha256']={'OTHER':self.digest}
        self.check_bad(change,'does not cover operation outputs')

    def test_missing_assembly(self):
        self.check_bad(lambda m:m.update(assemblies=[]),'consumer assembly')


class DepthCurrentSessionTests(unittest.TestCase):
    """Actual isolated runtime binding, not a copied readiness receipt."""
    def setUp(self):
        self.factory = factory_fixtures.FoundryTests(methodName='runTest')
        self.factory.setUp()
        self.factory.ready_design()
        self.packet = DepthTests(methodName='runTest')
        self.packet.setUp()
        state = self.factory.state()
        bp = state['blueprint']
        self.packet.model['subject'] = {
            'blueprint_id': bp['data']['id'], 'blueprint_revision': bp['data']['revision'],
            'blueprint_sha256': bp['sha256'], 'authority_source': state['approval']['source'],
        }
        self.checker = self.factory.bundle / 'scripts/check_foundry_depth.py'
        shutil.copyfile(S, self.checker)
        self.model = self.packet.root / 'model.json'
        self.model.write_text(json.dumps(self.packet.model))

    def tearDown(self):
        self.packet.tearDown()
        self.factory.tearDown()

    def run_checker(self, session=None, root=None):
        command = [sys.executable, '-B', str(self.checker), str(self.model), '--root', str(root or self.packet.root), '--ready']
        if session is not None:
            command += ['--session', str(session)]
        result = subprocess.run(command, text=True, capture_output=True, timeout=8)
        return result.returncode, json.loads(result.stdout)

    def test_actual_current_session_ready_is_read_only_and_pinned(self):
        path = self.factory.root / '.agent-foundry/state.json'
        before = path.read_bytes()
        code, result = self.run_checker(self.factory.root)
        self.assertEqual(code, 0, result)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(result['model_sha256'], hashlib.sha256(self.model.read_bytes()).hexdigest())
        self.assertEqual(result['current_subject']['session_state_sha256'], hashlib.sha256(before).hexdigest())
        self.assertFalse(result['quality_certified'])

    def test_missing_session_has_actionable_hint(self):
        code, result = self.run_checker()
        self.assertNotEqual(code, 0)
        self.assertTrue(any('--session SESSION' in x for x in result['errors']), result)

    def test_initialized_root_automatically_resolves_current_session(self):
        shutil.copytree(self.packet.root / 'skills', self.factory.root / 'skills')
        shutil.copyfile(self.packet.root / 'out.txt', self.factory.root / 'out.txt')
        code, result = self.run_checker(root=self.factory.root)
        self.assertEqual(code, 0, result)

    def test_copied_gate_is_not_a_current_session(self):
        copied = self.factory.write('copied-gate.json', json.dumps(self.factory.call('build-gate')))
        code, result = self.run_checker(copied)
        self.assertNotEqual(code, 0)
        self.assertTrue(any('not a copied gate JSON' in x for x in result['errors']), result)

    def test_changed_blueprint_cannot_use_old_depth_subject(self):
        self.factory.bp['revision'] = 2
        self.factory.register()
        self.factory.approve()
        code, result = self.run_checker(self.factory.root)
        self.assertNotEqual(code, 0)
        self.assertTrue(any('subject differs' in x for x in result['errors']), result)

    def test_matching_stored_strings_do_not_replace_canonical_digest(self):
        state = self.factory.state()
        state['blueprint']['sha256'] = 'b' * 64
        state['approval']['blueprint_sha256'] = 'b' * 64
        state['snapshot_hash'] = factory_fixtures.digest({key: value for key, value in state.items() if key != 'snapshot_hash'})
        (self.factory.root / '.agent-foundry/state.json').write_text(json.dumps(state))
        code, result = self.run_checker(self.factory.root)
        self.assertNotEqual(code, 0)
        self.assertTrue(any('canonical digest mismatch' in x for x in result['errors']), result)

    def test_revoked_canonical_authority_rejected_without_saving(self):
        state = self.factory.state()
        doc = {'schema_version': 'foundry-authority/1', 'items': [{'id': 'A1', 'actor': 'user', 'decision': 'approve', 'scope': self.factory.bp['scope'], 'subject_sha256': state['blueprint']['sha256']}]}
        path = self.factory.write('inputs/authority.json', json.dumps(doc))
        record = self.factory.auth()
        record['canonical_authority'] = {'path': 'inputs/authority.json', 'record_id': 'A1', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        self.factory.call('approve', '--sha256', state['blueprint']['sha256'], '--revision', 1, '--scope', self.factory.bp['scope'], record=record)
        doc['items'][0]['decision'] = 'revoked'
        path.write_text(json.dumps(doc))
        snapshot = self.factory.root / '.agent-foundry/state.json'
        before = snapshot.read_bytes()
        code, result = self.run_checker(self.factory.root)
        self.assertNotEqual(code, 0)
        self.assertTrue(any('approval blocks readiness' in x for x in result['errors']), result)
        self.assertEqual(snapshot.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
