import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'verify_depth.py'
spec = importlib.util.spec_from_file_location('verify_depth', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DepthChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'input.txt').write_text('requirement revision 1')
        (self.root / 'result.txt').write_text('observed fixture result')
        self.file = lambda p: {'path': p, 'sha256': hashlib.sha256((self.root/p).read_bytes()).hexdigest()}
        self.data = {'schema_version':'depth/2','project_id':'fixture','revision':'1','maturity':'design','scope':'bounded fixture','consumer':'receiver',
          'requirements':[{'id':'R1','source':'fixture','owner':'writer','applicability':'required','due':'design','acceptance':'exact fixture','negative_case':'wrong fixture','contract_ids':['C1'],'evidence_ids':['E1'],'required_evidence_kinds':['independent']}],
          'contracts':[{'id':'C1','owner':'writer','consumer':'receiver','inputs':['fixture'],'outputs':['result'],'rule':'identity','failure':'report error','acceptance':'exact fixture','requirement_ids':['R1'],'operation_ids':[]}],
          'evidence':[{'id':'E1','kind':'independent','actor':'reviewer','author_actor':'writer','reviewer_actor':'reviewer','scope':'R1 fixture only','environment':'temporary fixture','observed_at':'2026-11-03','method':'compare fixture','verdict':'pass','status':'current','requirement_ids':['R1'],'files':[self.file('result.txt')],'inputs':[self.file('input.txt')]}],
          'systems':[],'operations':[],'capabilities':[],'recipes':[],'attempts':[],'transformations':[],'assemblies':[],'handoff':{'status':'pending'}}

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, data=None, gate='design'):
        return module.validate(self.data if data is None else data, self.root, gate)

    def test_positive_design_fixture(self):
        self.assertEqual([], self.check())

    def test_unresolved_evidence(self):
        self.data['requirements'][0]['evidence_ids']=['absent']
        self.assertTrue(any('unresolved' in e for e in self.check()))

    def test_self_review(self):
        self.data['evidence'][0]['reviewer_actor']='writer'
        self.assertTrue(any('review self' in e for e in self.check()))

    def test_stale_input_invalidates(self):
        (self.root/'input.txt').write_text('revision 2')
        self.assertTrue(any('stale bytes' in e for e in self.check()))

    def test_narrow_evidence(self):
        self.data['evidence'][0]['requirement_ids']=[]
        self.assertTrue(any('does not cover' in e for e in self.check()))

    def test_path_escape(self):
        self.data['evidence'][0]['files'][0]['path']='../elsewhere'
        self.assertTrue(any('escapes' in e for e in self.check()))

    def test_missing_file(self):
        (self.root/'result.txt').unlink()
        self.assertTrue(any('missing file' in e for e in self.check()))

    def test_structural_proof_not_human(self):
        self.data['requirements'][0]['required_evidence_kinds']=['human']
        self.assertTrue(any('kinds missing' in e for e in self.check()))

    def test_unsupported_result_version(self):
        self.data['schema_version']='depth/1'
        self.assertTrue(any('unsupported schema_version' in e for e in self.check()))

    def test_draft_not_production(self):
        self.data['maturity']='draft'
        self.assertTrue(any('below requested' in e for e in self.check(gate='production')))

    def test_na_requires_subject_reason(self):
        self.data['requirements'][0]['applicability']='not_applicable'
        self.assertTrue(any('reopen_when' in e for e in self.check()))

    def test_duplicate_id(self):
        self.data['requirements'].append(copy.deepcopy(self.data['requirements'][0]))
        self.assertTrue(any('duplicate' in e for e in self.check()))

    def test_unknown_attempt_requires_reconcile(self):
        self.data['attempts']=[{'id':'A1','actor':'writer','recipe_id':'missing','outcome':'unknown','parameters':{'mode':'fixture'},'resources':{'cost':0}}]
        self.assertTrue(any('reconcile' in e for e in self.check()))

    def test_envelope_template_draft_only(self):
        path=SCRIPT.parents[1]/'assets/depth/project.template.json'
        self.assertEqual([], self.check(json.loads(path.read_text()), 'draft'))
        self.assertTrue(self.check(json.loads(path.read_text()), 'design'))

    def production(self):
        d=self.data
        d['maturity']='production'
        d['contracts'][0]['operation_ids']=['O1']
        d['systems']=[{'id':'S1','owner':'writer','applicability':'required','state_fields':['state'],'transitions':['start→done'],'invariants':['one result'],'interactions':['C1 writes result']}]
        d['operations']=[{'id':'O1','owner':'writer','consumer':'receiver','status':'verified','capability_ids':['P1'],'recipe_ids':['T1'],'attempt_ids':['A1'],'accepted_attempt_id':'A1'}]
        d['capabilities']=[{'id':'P1','operation':'fixture','tool_version':'fixture1','environment':'temporary fixture','parameters':['mode'],'limits':['fixture only'],'rights':'fixture','cost':'zero','status':'exercised','evidence_ids':['E2']}]
        d['recipes']=[{'id':'T1','owner':'writer','consumer':'receiver','inputs':['input.txt'],'steps':['copy exact'],'outputs':['result.txt'],'acceptance':'exact fixture','fallback':'report error','budget':'zero','transformation_ids':['X1']}]
        d['transformations']=[{'id':'X1','input_semantics':'text','output_semantics':'text','preserve':['text'],'check':'compare'}]
        d['attempts']=[{'id':'A1','actor':'writer','recipe_id':'T1','outcome':'succeeded','parameters':{'mode':'fixture'},'resources':{'cost':0},'outputs':[self.file('result.txt')]}]
        d['assemblies']=[{'id':'B1','owner':'writer','consumer':'receiver','build':'fixture1','environment':'temporary fixture','scenario':'one result','expected':'one result','actual':'one result','recovery':'repeat fixture','evidence_ids':['E2'],'operation_ids':['O1'],'artifacts':[self.file('result.txt')],'component_files':[self.file('result.txt')]}]
        e=copy.deepcopy(d['evidence'][0]);e.update(id='E2',kind='integration',build='fixture1',capability_ids=['P1'],assembly_ids=['B1']);e['inputs'].append(self.file('result.txt'));d['evidence'].append(e)
        d['handoff']={'status':'accepted','receiver':'receiver','reconstruction':'fixture recipe','permissions':'fixture only','budget':'zero','checkpoint':'fixture1','next_action':'none'}
        return d

    def test_positive_production_fixture(self):
        self.assertEqual([],self.check(self.production(),'production'))

    def test_assembly_build_mismatch(self):
        self.production()['evidence'][1]['build']='another'
        self.assertTrue(any('build/environment/scope' in e for e in self.check(gate='production')))

    def test_operation_failed_attempt(self):
        self.production()['attempts'][0]['outcome']='failed'
        self.assertTrue(any('successful linked' in e for e in self.check(gate='production')))

    def test_generic_capability_proof_rejected(self):
        self.production()['evidence'][1]['capability_ids']=[]
        self.assertTrue(any('capability evidence scope' in e for e in self.check(gate='production')))


    def test_proof_unrelated_artifact_rejected(self):
        self.production()['evidence'][1]['files']=[self.file('input.txt')]
        self.assertTrue(any('not bound to artifacts' in e for e in self.check(gate='production')))

    def test_capability_environment_mismatch(self):
        self.production()['capabilities'][0]['environment']='other device'
        self.assertTrue(any('environment mismatch' in e for e in self.check(gate='production')))

    def test_contract_wrong_requirement(self):
        self.data['contracts'][0]['requirement_ids']=[]
        self.assertTrue(any('contract does not cover' in e for e in self.check()))

    def test_pending_or_invalid_system(self):
        self.production()['systems'][0]['applicability']='pending'
        self.assertTrue(any('applicability unresolved' in e for e in self.check(gate='production')))
        self.data['systems'][0]['applicability']='banana'
        self.assertTrue(any('invalid system applicability' in e for e in self.check(gate='production')))

    def test_unresolved_duplicate_attempt(self):
        self.production()['attempts'].append({'id':'A2','actor':'writer','recipe_id':'T1','outcome':'unknown','parameters':{'mode':'fixture'},'resources':{'cost':0},'reconcile':'query job id'})
        self.data['operations'][0]['attempt_ids'].append('A2')
        self.assertTrue(any('unresolved attempt' in e for e in self.check(gate='production')))

    def test_independent_actor_is_reviewer(self):
        self.data['evidence'][0]['actor']='writer'
        self.assertTrue(any('actual reviewer' in e for e in self.check()))

    def test_malformed_handoff_json_error(self):
        self.production()['handoff']=[]
        self.assertTrue(any('expected object' in e for e in self.check(gate='production')))

    def test_component_not_accepted_output(self):
        self.production()['assemblies'][0]['component_files']=[self.file('input.txt')]
        self.assertTrue(any('missing accepted operation output' in e for e in self.check(gate='production')))

    def test_active_conditional_system_requires_model(self):
        self.production()['systems'][0]={'id':'S1','owner':'writer','applicability':'conditional','condition':'enabled','active':True}
        self.assertTrue(any('missing state_fields' in e for e in self.check(gate='production')))


if __name__ == '__main__':
    unittest.main()
