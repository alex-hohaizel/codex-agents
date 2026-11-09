"""Native ledger lifecycle and scoped amendment regressions, synthetic only."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'state.py'
spec=importlib.util.spec_from_file_location('state_under_test',SCRIPT)
state=importlib.util.module_from_spec(spec);spec.loader.exec_module(state)

def sourced(row):return dict(row,source='synthetic regression fixture',verbatim='Synthetic fixture; no real user or external effect')
def auth(subject):return sourced({'actor':'user','subject_sha256':state.digest(subject)})
def requirement(ident,priority='must'):
    return sourced({'id':ident,'intent':'Requirement '+ident,'priority':priority,'acceptance':'Recorded fixture proof','owner':'author','status':'pending'})

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve());self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.serial=0
        self.profile={'schema_version':'app-atelier-profile/1','id':'fixture','constraints':{'no_human_experiments':False,'owner_operational_work':True},'requirements':[]}
    def file(self,obj):
        self.serial+=1;p=self.root/('record-%d.json'%self.serial);p.write_text(json.dumps(obj));return p
    def cli(self,*args,code=0):
        r=subprocess.run([sys.executable,'-B',str(SCRIPT),'--project',str(self.root),*map(str,args)],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(r.returncode,code,r.stderr or r.stdout)
        return json.loads(r.stdout or r.stderr)
    def put(self,kind,row,code=0):return self.cli('put','--kind',kind,'--record',self.file(sourced(row)),code=code)
    def ledger(self):return json.loads((self.root/'.appatelier/state.json').read_text())
    def init(self):
        self.cli('init','--profile',self.file(self.profile))
        ex={'id':'X','scope':'fixture','phase_ids':['repair','other'],'status':'current'}
        ex['authority']=auth(state.execution_subject(ex));self.put('execution',ex)
    def proof(self,label,req_ids=()):
        artifact='ART-'+label;evidence='E-'+label
        (self.root/(label+'.txt')).write_text('Synthetic artifact '+label)
        (self.root/(label+'.proof')).write_text('Synthetic reviewer evidence '+label)
        self.put('artifact',{'id':artifact,'path':label+'.txt','author_ids':['author']})
        self.put('evidence',{'id':evidence,'artifact_ids':[artifact],'proof_path':label+'.proof','observer':'reviewer','method':'fixture observation','environment':'local synthetic','status':'pass','independent':True,'requirement_ids':list(req_ids)})
        return artifact,evidence
    def close_req(self,rid):
        _,eid=self.proof('REQ-'+rid,[rid]);r=copy.deepcopy(self.ledger()['requirement'][rid]);r['status']='closed';r['evidence_ids']=[eid];self.put('requirement',r)
    def job(self,jid,req_ids=(),phase='repair',fulfills=(),dependencies=(),decisions=(),complete=True):
        aid,eid=self.proof(jid)
        self.put('job',{'id':jid,'phase':phase,'scope':'fixture','owner':'author','goal':'Synthetic useful result','execution_id':'X','requirement_ids':list(req_ids),'fulfills_requirements':list(fulfills),'depends_on':list(dependencies),'decision_ids':list(decisions),'artifact_ids':[aid],'evidence_ids':[eid]})
        self.cli('start','--job',jid)
        if complete:self.cli('complete','--job',jid)
    def amend(self,value):
        subject={'old_profile_sha256':self.ledger()['profile_sha256'],'new_profile_content_sha256':state.digest(value)}
        return self.cli('amend-profile','--profile',self.file(value),'--record',self.file(auth(subject)))

    def test_pending_optional_input_completes_and_remains_current(self):
        self.init();self.put('requirement',requirement('OPTION','should'));self.job('J',['OPTION'])
        self.assertEqual(self.cli('status')['stale_completed_jobs'],[])
        self.assertIn('OPTION',self.ledger()['job']['J']['input_requirement_hashes'])

    def test_completion_evidence_replacement_reopens_job_and_phase(self):
        self.init()
        for case in ('self_review','unrelated_artifact','method','proof'):
            with self.subTest(case=case):
                jid='J-'+case;self.job(jid)
                e=self.ledger()['evidence']['E-'+jid]
                if case=='self_review':e.update(independent=False,observer='author')
                elif case=='unrelated_artifact':e['artifact_ids']=[self.proof('OTHER')[0]]
                elif case=='method':e['method']='Replaced observation protocol'
                else:
                    (self.root/'replacement.proof').write_text('Different synthetic observation')
                    e['proof_path']='replacement.proof'
                # This case deliberately records a new observation of its new
                # subject/proof. Carrying old pins instead is tested below.
                e['artifact_hashes']={aid:self.ledger()['artifact'][aid]['sha256'] for aid in e['artifact_ids']}
                e['proof_sha256']=state.file_sha(self.root/e['proof_path'])
                self.put('evidence',e)
                ledger=self.ledger()
                self.assertTrue(state.fresh_evidence(self.root,ledger,ledger['evidence']['E-'+jid]))
                self.assertFalse(state.completed_current(self.root,ledger,ledger['job'][jid]))
                self.assertIn(jid,self.cli('status')['stale_completed_jobs'])
                self.assertIn('completed job stale: '+jid,self.cli('phase-check','--phase','repair',code=1)['blockers'])

    def test_completion_evidence_change_preserves_unrelated_job(self):
        self.init();self.job('JA');self.job('JB')
        e=self.ledger()['evidence']['E-JA'];e['method']='Changed method';self.put('evidence',e)
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['JA'])

    def test_completion_bookkeeping_changes_keep_semantic_evidence_pin(self):
        self.init();self.job('J');before=self.ledger()['job']['J']['completion_evidence_hashes']
        e=self.ledger()['evidence']['E-J']
        e.update(created_at='synthetic creation annotation',updated_at='synthetic update annotation',recorded_at='synthetic ledger annotation')
        self.put('evidence',e)
        p=copy.deepcopy(self.profile);p['metadata']={'audit':'bookkeeping only'};self.amend(p)
        after=self.ledger()
        self.assertEqual(after['job']['J']['completion_evidence_hashes'],before)
        self.assertEqual(self.cli('status')['stale_completed_jobs'],[])
        self.assertTrue(self.cli('phase-check','--phase','repair')['ready'])

    def test_historical_completion_without_evidence_snapshot_requires_repair(self):
        self.init();self.job('J');ledger=self.ledger()
        del ledger['job']['J']['completion_evidence_hashes']
        state.atomic(self.root/'.appatelier/state.json',ledger)
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['J'])
        self.assertFalse(self.cli('phase-check','--phase','repair',code=1)['ready'])
        self.assertIn('completion evidence snapshot missing/mismatched; reconcile with a repair job',state.completion_proof_blockers(self.root,ledger,ledger['job']['J'],pinned=True))

    def test_initial_completion_checks_independent_output_coverage(self):
        self.init();self.job('J',complete=False)
        e=self.ledger()['evidence']['E-J'];e.update(independent=False,observer='author');self.put('evidence',e)
        result=self.cli('complete','--job','J',code=2)
        self.assertIn('independent review required for every declared output',result['error'])
        e.update(independent=True,observer='reviewer');e['artifact_ids']=[self.proof('OTHER')[0]]
        e['artifact_hashes']={aid:self.ledger()['artifact'][aid]['sha256'] for aid in e['artifact_ids']};self.put('evidence',e)
        result=self.cli('complete','--job','J',code=2)
        self.assertIn('evidence does not cover every output',result['error'])

    def test_optional_definition_change_invalidates_completed_job(self):
        self.init();self.put('requirement',requirement('OPTION','should'));self.job('J',['OPTION'])
        r=requirement('OPTION','should');r['intent']='Changed optional input definition';self.put('requirement',r)
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['J'])

    def test_pending_must_input_still_blocks_admission(self):
        self.init();self.put('requirement',requirement('MUST'))
        aid,eid=self.proof('J')
        self.put('job',{'id':'J','phase':'repair','scope':'fixture','owner':'author','goal':'Fixture','execution_id':'X','requirement_ids':['MUST'],'artifact_ids':[aid],'evidence_ids':[eid]})
        r=self.cli('gate','--job','J',code=1)
        self.assertIn('required input requirement pending/stale: MUST',r['blockers'])

    def test_fulfilled_requirement_may_start_pending_but_needs_closure(self):
        self.init();self.put('requirement',requirement('MUST'));self.job('J',['MUST'],fulfills=['MUST'],complete=False)
        self.cli('complete','--job','J',code=2)
        self.close_req('MUST');self.cli('complete','--job','J')
        self.assertEqual(self.cli('status')['stale_completed_jobs'],[])

    def test_metadata_amendment_keeps_current_job_and_authority(self):
        self.init();self.job('J');before=self.ledger();p=copy.deepcopy(self.profile);p['audit_annotation']='nonoperative note'
        result=self.amend(p);after=self.ledger()
        self.assertEqual(result['impact']['mode'],'metadata_only')
        self.assertEqual(self.cli('status')['stale_completed_jobs'],[])
        self.assertEqual(after['execution']['X']['authority'],before['execution']['X']['authority'])
        self.assertTrue(all(not v for v in result['impact']['invalidated'].values()))

    def test_requirement_delta_reopens_only_linked_job_same_phase(self):
        self.profile['requirements']=[requirement('A'),requirement('B')];self.init()
        self.close_req('A');self.close_req('B');self.job('JA',['A']);self.job('JB',['B'])
        p=copy.deepcopy(self.profile);p['requirements'][0]['intent']='Changed A'
        result=self.amend(p)
        self.assertEqual(result['impact']['mode'],'dependency_scoped')
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['JA'])
        self.assertIn('JB',result['impact']['carried_forward']['job'])
        self.assertTrue(state.current_requirement(self.root,self.ledger(),self.ledger()['requirement']['B']))

    def test_requirement_delta_invalidates_job_dependency_transitively(self):
        self.profile['requirements']=[requirement('A')];self.init();self.close_req('A');self.job('JA',['A']);self.job('JB',dependencies=['JA'])
        p=copy.deepcopy(self.profile);p['requirements'][0]['intent']='Changed A';result=self.amend(p)
        self.assertEqual(set(result['impact']['invalidated']['job']),{'JA','JB'})

    def test_explicit_independent_decision_keeps_its_job_current(self):
        self.profile['requirements']=[requirement('A'),requirement('B')];self.init();self.close_req('A');self.close_req('B')
        for ident in ('A','B'):
            d={'id':'D'+ident,'category':'fixture-choice','scope':'fixture','question':'Fixture '+ident,'options':['yes','no'],'answer':'yes','status':'confirmed','requirement_ids':[ident]}
            d['authority']=auth(state.decision_subject(d));self.put('decision',d)
        self.job('JA',['A'],decisions=['DA']);self.job('JB',['B'],decisions=['DB'])
        p=copy.deepcopy(self.profile);p['requirements'][0]['intent']='Changed A';r=self.amend(p)
        self.assertEqual(r['impact']['invalidated']['decision'],['DA'])
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['JA'])
        self.assertEqual(self.ledger()['history'][-1]['record']['status'],'closed')

    def test_decision_dependency_binding_cannot_be_changed_under_old_authority(self):
        self.init()
        d={'id':'D','category':'fixture-choice','scope':'fixture','question':'Bound choice','options':['yes','no'],'answer':'yes','status':'confirmed','requirement_ids':['A']}
        d['authority']=auth(state.decision_subject(d));d['requirement_ids']=['B']
        self.put('decision',d,code=2)

    def test_phase_policy_change_preserves_other_phase(self):
        self.init();self.job('JA');self.job('JB',phase='other');p=copy.deepcopy(self.profile)
        p['owner_decision_gates']={'repair':['new-choice']};result=self.amend(p)
        self.assertEqual(result['impact']['mode'],'dependency_scoped')
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['JA'])

    def test_global_constraint_and_unknown_field_changes_are_conservative(self):
        for change in ({'constraints':{'no_human_experiments':True}},{'unclassified_product_rule':'new behavior'}):
            # A separate ledger per variation, preserving explicit true isolation.
            with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as folder:
                oldroot=self.root;self.root=Path(folder)
                try:
                    self.init();self.job('J');p=copy.deepcopy(self.profile);p.update(change);r=self.amend(p)
                    self.assertEqual(r['impact']['mode'],'conservative_global')
                    self.assertEqual(self.cli('status')['stale_completed_jobs'],['J'])
                finally:self.root=oldroot

    def test_metadata_change_does_not_revive_previously_stale_records(self):
        self.init();self.job('J');p=copy.deepcopy(self.profile);p['unknown_rule']='changed';self.amend(p)
        p['metadata']={'note':'annotation'};self.amend(p)
        self.assertEqual(self.cli('status')['stale_completed_jobs'],['J'])

    def test_old_supplied_evidence_bindings_are_rejected_without_rewrite(self):
        self.init();aid,eid=self.proof('OBS')
        old=copy.deepcopy(self.ledger()['evidence'][eid])
        (self.root/'OBS.txt').write_text('Materially different subject')
        self.put('artifact',{'id':aid,'path':'OBS.txt','author_ids':['author']})
        old.update(id='E-NEW',status='pass')
        result=self.put('evidence',old,code=2)
        self.assertIn('supplied observation snapshot',result['error'])
        self.assertNotIn('E-NEW',self.ledger()['evidence'])

    def test_duplicate_policy_keys_reject_before_interpretation(self):
        p=self.root/'ambiguous.json';p.write_text('{"no_human_experiments":true,"no_human_experiments":false}')
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            state.read_json(p)

if __name__=='__main__':unittest.main()
