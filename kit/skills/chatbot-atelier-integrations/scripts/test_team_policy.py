#!/usr/bin/env python3
"""Synthetic record fixtures only; no real agents, product or listening claims."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import team_policy as t


def fixture(directory, local=False):
    profile = t.load_profile()
    ids = [r for d in profile['domains'] for r in d['requirement_ids']]
    candidates = [r for d in profile['domains'] for r in d['requirement_ids'] if r not in profile['critical_requirement_ids']]
    active = candidates[:1] if local else ids
    plan = t.scaffold(ids, 'local' if local else 'stage', active)
    root = Path(directory)
    (root/'audit').mkdir(exist_ok=True)
    (root/'component.txt').write_text('SYNTHETIC actual bytes, not a product')
    (root/'baseline.txt').write_text('SYNTHETIC unchanged baseline')
    def sha(path): return t.digest((root/path).read_bytes())
    plan['components'] = {
        'changed': {'artifact_ref':'component.txt','sha256':sha('component.txt'),'environment':'fixture-env-v1','depends_on':[]},
        'baseline': {'artifact_ref':'baseline.txt','sha256':sha('baseline.txt'),'environment':'fixture-env-v1','depends_on':[]}}
    plan['scope']['changed_component_ids'] = ['changed'] if local else []
    runs = []
    def run(rid,kind,actor,rids,domains):
        path='audit/'+rid+'.md';(root/path).write_text('SYNTHETIC report: '+rid)
        r={'id':rid,'kind':kind,'actor_id':actor,'status':'completed','verdict':'accept',
           'requirement_ids':list(rids),'domain_ids':domains,'output_ref':path,'output_sha256':sha(path)}
        runs.append(r);return r
    for number,domain in enumerate(profile['domains']):
        rids=[r for r in domain['requirement_ids'] if r in active]
        if not rids:continue
        owner=run('owner'+str(number),'specialist','author'+str(number),rids,[domain['id']])
        qa=run('qa'+str(number),'qa','qa'+str(number%3),rids,[domain['id']])
        judge=run('judge'+str(number),'judge','judge'+str(number%3),rids,[domain['id']]) if not local else None
        if judge:
            judge.update(package_hash='a'*64,context_mode='fresh',review_mode='primary',criteria={rid:{'verdict':'accept','positive_claim':'criterion-specific fixture '+rid,'strongest_objection':'tested fixture limitation','uncertainty':'synthetic only','reversal_condition':'changed dependency'} for rid in rids})
        for rid in rids:
            plan['assignments'][rid].update(component_ids=['changed'],owner_run=owner['id'],qa_run=qa['id'],judge_run=judge['id'] if judge else '',verdict='accept',evidence_refs=['component.txt'],evidence_sha256s={'component.txt':sha('component.txt')})
    for rid in set(ids)-set(active):
        plan['assignments'][rid].update(component_ids=['baseline'],impact='unchanged',reason='Independent fixture impact inspection, no shared dependency')
    impact=run('impact','qa','qa-impact',ids,list(d['id'] for d in profile['domains']))
    guardian=run('guardian','guardian','qa-guardian',ids,list(d['id'] for d in profile['domains']))
    rootrun=run('root','orchestrator','root',active,list(d['id'] for d in profile['domains']))
    plan.update(impact_run='impact',guardian_run='guardian',orchestrator_run='root',perspectives={k:{'owner_run':'root','finding':'SYNTHETIC integrated '+k} for k in t.PERSPECTIVES})
    for actual in runs:
        actual['input_snapshot'] = t.snapshot_inputs(plan, actual, runs, profile)
    return plan,runs,ids,profile


class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve());self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.plan,self.runs,self.ids,self.profile=fixture(self.root)
    def check(self,plan=None,runs=None):
        return t.check(plan or self.plan,self.ids,runs or self.runs,'a'*64,root=self.root,ready=True)
    def bad(self,part):self.assertTrue(any(part in e for e in self.check()),self.check())
    def test_full_stage_groups_many_criteria_into_fewer_authors_and_judges(self):
        self.assertEqual(self.check(),[])
        self.assertLess(len({r['actor_id'] for r in self.runs if r['kind']=='specialist'}),len(self.ids))
        self.assertEqual(len({r['actor_id'] for r in self.runs if r['kind']=='judge'}),3)
    def test_local_acceptance_needs_qa_without_council(self):
        plan,runs,ids,_=fixture(self.root,True)
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True),[])
        self.assertFalse(any(r['kind']=='judge' for r in runs))
    def test_omitted_requirement_fails(self):
        self.plan['assignments'].pop(self.ids[0]);self.bad('every canonical')
    def test_same_actor_cannot_author_and_verify(self):
        owner=next(r for r in self.runs if r['kind']=='specialist');qa=next(r for r in self.runs if r['kind']=='qa');qa['actor_id']=owner['actor_id'];self.bad('production actor')
    def test_judge_is_independent_of_qa(self):
        judge=next(r for r in self.runs if r['kind']=='judge');judge['actor_id']='qa0';self.bad('reuses an author')
    def test_one_grouped_judge_missing_one_criterion_fails(self):
        judge=next(r for r in self.runs if r['kind']=='judge');judge['criteria'].pop(judge['requirement_ids'][0]);self.bad('separate criterion')
    def test_stale_package_hash_fails(self):
        next(r for r in self.runs if r['kind']=='judge')['package_hash']='b'*64;self.bad('stale frozen')
    def test_primary_context_cannot_be_inherited(self):
        next(r for r in self.runs if r['kind']=='judge')['context_mode']='inherited';self.bad('fresh context')
    def test_wrong_domain_competence_fails(self):
        next(r for r in self.runs if r['kind']=='qa')['domain_ids']=[];self.bad('domain competence')
    def test_mutated_report_bytes_fail(self):
        ref=next(r for r in self.runs if r['kind']=='qa')['output_ref'];(self.root/ref).write_text('changed');self.bad('hash differs')
    def test_mutated_primary_evidence_fails(self):
        (self.root/'component.txt').write_text('changed');self.bad('hash differs')
    def test_dependency_cycle_fails(self):
        self.plan['components']['changed']['depends_on']=['baseline'];self.plan['components']['baseline']['depends_on']=['changed'];self.bad('cyclic')
    def test_unknown_impact_cannot_be_unchanged(self):
        plan,runs,ids,_=fixture(self.root,True);rid=next(r for r in ids if r not in plan['scope']['active_requirement_ids']);plan['assignments'][rid]['impact']='unknown'
        self.assertTrue(any('unknown impact' in e for e in t.check(plan,ids,runs,'a'*64,root=self.root,ready=True)))
    def test_transitively_affected_inactive_criterion_is_rejected(self):
        plan,runs,ids,_=fixture(self.root,True);plan['components']['baseline']['depends_on']=['changed']
        self.assertTrue(any('inactive criterion' in e for e in t.check(plan,ids,runs,'a'*64,root=self.root,ready=True)))
    def test_critical_scope_cannot_downgrade_to_local_without_judge(self):
        if not self.profile['critical_requirement_ids']:self.skipTest('No critical path in this stage profile')
        self.plan['scope']['kind']='local'
        for row in self.plan['assignments'].values():row['judge_run']=''
        self.bad('required completed judge')
    def test_stage_cannot_hide_out_of_scope(self):
        row=self.plan['assignments'][self.ids[0]];row.update(status='out_of_scope',impact='unchanged',reason='fixture')
        self.plan['scope']['active_requirement_ids'].remove(self.ids[0]);self.bad('stage completion cannot omit')
    def test_failed_same_strategy_third_time_is_rejected(self):
        self.plan['repair_history']=[{'issue_id':'I1','strategy_ref':'same','result':'failed'} for _ in range(3)];self.bad('new diagnosed repair strategy')
    def test_diagnosed_new_strategy_after_two_failures_is_allowed(self):
        self.plan['repair_history']=[{'issue_id':'I1','strategy_ref':'old','result':'failed'} for _ in range(2)]+[{'issue_id':'I1','strategy_ref':'new','result':'fixed','diagnostic_ref':'root-cause.md'}]
        self.assertEqual(self.check(),[])
    def test_reopened_old_evidence_is_rejected(self):
        h=t.digest(b'old');self.plan['reopens']=[{'issue_id':'I1','reason':'reworded','new_evidence':{'artifact_ref':'component.txt','sha256':h},'previous_evidence_sha256s':[h]}];self.bad('genuinely new')
    def test_carry_requires_matching_transitive_hashes_and_source_review(self):
        rid=self.ids[0];row=self.plan['assignments'][rid];self.plan['scope']['active_requirement_ids'].remove(rid)
        row.update(status='carried',impact='unchanged',reason='verified stable input')
        receipt={'schema_version':'chatbot.review/1','requirement_id':rid,'verdict':'accept','kind':'judge','actor_id':'old-judge','source_version':'v1','source_package_hash':'c'*64,'report_ref':'audit/guardian.md','report_sha256':t.digest((self.root/'audit/guardian.md').read_bytes()),'components':{'changed':{k:self.plan['components']['changed'][k] for k in ('sha256','environment')}}}
        path=self.root/'receipt.json';path.write_text(json.dumps(receipt))
        row['carry_forward']={'reason':'QA verified exact old input closure','reviewer_run':'carry-impact','receipt_ref':'receipt.json','receipt_sha256':t.digest(path.read_bytes())}
        # This new synthetic QA run reads the newly supplied immutable receipt;
        # the previous completed impact run is retained without rebinding it.
        fresh=copy.deepcopy(next(r for r in self.runs if r['id']=='impact'))
        fresh.update(id='carry-impact',output_ref='audit/carry-impact.md')
        fresh['input_snapshot']=t.snapshot_inputs(self.plan,fresh,self.runs,self.profile)
        (self.root/fresh['output_ref']).write_text('SYNTHETIC new carry review')
        fresh['output_sha256']=t.digest((self.root/fresh['output_ref']).read_bytes())
        self.runs.append(fresh);self.plan['impact_run']='carry-impact'
        self.assertEqual(self.check(),[])
        self.plan['components']['changed']['environment']='new-runtime';self.bad('carry crosses changed')
    def test_old_input_hash_change_without_change_declaration_fails(self):
        self.plan['components']['changed']['baseline_sha256']='b'*64;self.bad('omitted from impact')
    def test_snapshot_changes_with_plan_but_not_new_judge(self):
        data={'brief':'actual','team_policy':self.plan,'runs':self.runs}
        h=t.snapshot_hash(data);data['runs'].append({'id':'new-judge','kind':'judge','actor_id':'new'});self.assertEqual(h,t.snapshot_hash(data))
        data['team_policy']['scope']['statement']='different';self.assertNotEqual(h,t.snapshot_hash(data))

    def test_local_qa_cannot_reuse_old_input_after_current_component_hash_refresh(self):
        plan,runs,ids,_=fixture(self.root,True)
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True),[])
        original_reports={r['id']:(self.root/r['output_ref']).read_bytes() for r in runs}
        (self.root/'component.txt').write_text('SYNTHETIC changed active implementation')
        plan['components']['changed']['sha256']=t.digest((self.root/'component.txt').read_bytes())
        for row in plan['assignments'].values():
            if row['status']=='active':row['evidence_sha256s']['component.txt']=plan['components']['changed']['sha256']
        issues=t.check(plan,ids,runs,'b'*64,root=self.root,ready=True)
        self.assertTrue(any('input snapshot missing/stale' in e for e in issues),issues)
        self.assertEqual(original_reports,{r['id']:(self.root/r['output_ref']).read_bytes() for r in runs})

    def test_qa_snapshot_includes_exact_authored_output_not_only_component_hash(self):
        plan,runs,ids,_=fixture(self.root,True)
        owner=next(r for r in runs if r['kind']=='specialist')
        qa=next(r for r in runs if r['kind']=='qa' and r['id'].startswith('qa'))
        self.assertIn(owner['id'],qa['input_snapshot']['reviewed_outputs'])
        (self.root/owner['output_ref']).write_text('SYNTHETIC changed authored report')
        owner['output_sha256']=t.digest((self.root/owner['output_ref']).read_bytes())
        issues=t.check(plan,ids,runs,'a'*64,root=self.root,ready=True)
        self.assertTrue(any('input snapshot missing/stale' in e and qa['id'] in e for e in issues),issues)

    def test_unrelated_component_does_not_invalidate_scoped_run_inputs(self):
        plan,runs,ids,_=fixture(self.root,True)
        (self.root/'unrelated.txt').write_text('SYNTHETIC unrelated scope')
        plan['components']['unrelated']={'artifact_ref':'unrelated.txt','sha256':t.digest((self.root/'unrelated.txt').read_bytes()),
            'environment':'different-feature','depends_on':[]}
        plan['scope']['changed_component_ids'].append('unrelated')
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True),[])

    def test_changed_requirement_contract_invalidates_its_input_snapshot(self):
        plan,runs,ids,profile=fixture(self.root,True)
        records=[{'id':rid,'state':'active' if rid in plan['scope']['active_requirement_ids'] else 'unchanged',
                  'reason':'SYNTHETIC original contract'} for rid in ids]
        for run in runs:run['input_snapshot']=t.snapshot_inputs(plan,run,runs,profile,records)
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True,requirement_records=records),[])
        next(row for row in records if row['id'] in plan['scope']['active_requirement_ids'])['acceptance']='changed accepted behavior'
        issues=t.check(plan,ids,runs,'a'*64,root=self.root,ready=True,requirement_records=records)
        self.assertTrue(any('input snapshot missing/stale' in e for e in issues),issues)

    def test_changed_primary_observation_cannot_reuse_old_qa_input_binding(self):
        plan,runs,ids,profile=fixture(self.root,True)
        (self.root/'metric.log').write_text('SYNTHETIC original measurement')
        for row in plan['assignments'].values():
            if row['status']=='active':
                row.update(evidence_refs=['metric.log'],evidence_sha256s={'metric.log':t.digest((self.root/'metric.log').read_bytes())})
        for run in runs:run['input_snapshot']=t.snapshot_inputs(plan,run,runs,profile)
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True),[])
        (self.root/'metric.log').write_text('SYNTHETIC changed measurement')
        for row in plan['assignments'].values():
            if row['status']=='active':row['evidence_sha256s']['metric.log']=t.digest((self.root/'metric.log').read_bytes())
        issues=t.check(plan,ids,runs,'a'*64,root=self.root,ready=True)
        self.assertTrue(any('input snapshot missing/stale' in e for e in issues),issues)

    def test_producer_historical_inputs_do_not_self_stale_after_normal_write(self):
        plan,runs,ids,_=fixture(self.root,True)
        owner=next(r for r in runs if r['kind']=='specialist')
        # The final synthetic state describes a producer that read older input,
        # wrote its immutable current output, then received fresh current QA.
        owner['input_snapshot']['components']['changed']['sha256']='b'*64
        self.assertEqual(t.check(plan,ids,runs,'a'*64,root=self.root,ready=True),[])

    def test_consumer_cannot_opt_out_of_required_component_inputs(self):
        plan,runs,ids,profile=fixture(self.root,True)
        qa=next(r for r in runs if r['id'].startswith('qa'))
        qa['input_component_ids']=[]
        self.assertIn('changed',t.snapshot_inputs(plan,qa,runs,profile)['components'])
        qa['input_snapshot']['components']={}
        issues=t.check(plan,ids,runs,'a'*64,root=self.root,ready=True)
        self.assertTrue(any('input snapshot missing/stale' in e for e in issues),issues)


if __name__=='__main__':unittest.main()
