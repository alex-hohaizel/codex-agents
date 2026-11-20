"""Actual isolated CLI guards. Fixtures are synthetic, not human/provider evidence."""
import concurrent.futures
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(SOURCE.parents[3] / 'scripts/tests'))
from fixture_production_choices import make_choice


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def blueprint():
    result = {
        'schema_version':'1.0.0','is_template':False,'id':'BP-1','revision':1,
        'source':'user-fixture-1','verbatim':'Preserve the stated outcome and verify its exact result.',
        'goal':'Produce an explicitly bounded verified result.','scope':'fixture-construction','non_goals':['Unapproved effects'],
        'entry_skill':'target-agent','skills':[{'name':'target-agent','purpose':'Coordinate the approved result.','capability_ids':['CAP-1'],'phase_ids':['PHASE-1']}],
        'capabilities':[{'id':'CAP-1','source':'user-fixture-1','verbatim':'Preserve the stated outcome and verify its exact result.','intent':'Preserve explicit requirements.','priority':'must','emphasis':True,'applicability':'applicable','owner':'ROLE-1','acceptance':'Current result matches the original requirement and test.','phase_ids':['PHASE-1'],'component_ids':['COMP-1'],'artifact_ids':['ART-1'],'test_ids':['TEST-1'],'depends_on':[]}],
        'phases':[{'id':'PHASE-1','name':'Produce result','acceptance':'Required result and independent proof are current.','handoff':'Return exact artifact and proof.','return_route':'Repair only affected result.','capability_ids':['CAP-1'],'artifact_ids':['ART-1'],'depends_on':[]}],
        'roles':[{'id':'ROLE-1','competence':'Domain-specific execution','responsibility':'Produce the declared artifact.'}],
        'components':[{'id':'COMP-1','kind':'skill','purpose':'Coordinate a bounded result.','owner':'ROLE-1','capability_ids':['CAP-1'],'phase_ids':['PHASE-1']}],
        'artifacts':[{'id':'ART-1','path':'skills/target-agent/SKILL.md','kind':'instruction','phase_id':'PHASE-1','owner':'ROLE-1','acceptance':'Complete declared behavior.','capability_ids':['CAP-1']}],
        'tests':[{'id':'TEST-1','method':'Inspect actual contract and negative case.','negative_case':'Requirement omitted from output.','due_phase':'PHASE-1','independent':True,'capability_ids':['CAP-1'],'artifact_ids':['ART-1']}],
        'questions':[],'input_sources':[],
        'continuity':{key:'Preserve current source-linked '+key+' and verify affected changes.' for key in ('requirements','knowledge','decisions','dependencies','evidence','pauses','approvals','handoffs','maintenance','honesty')}
    }
    catalog=SOURCE.parent/'assets/discovery-topics.json'
    result['discovery_catalog_sha256']=hashlib.sha256(catalog.read_bytes()).hexdigest()
    result['discovery_coverage']=[{'topic_id':t['id'],'applicability':'applicable','rationale':'Inspected bounded fixture scope.','source':'actual-fixture-analysis','current_question_ids':[],'current_status':'resolved','owner':'ROLE-1','due_gate':'before-construction','deferred_product_decisions':[],'evidence_ids':[],'affected_capability_ids':['CAP-1']} for t in json.loads(catalog.read_text())['topics']]
    return result


class FoundryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve());self.base=Path(self.temp.name)
        self.bundle=self.base/'bundle';(self.bundle/'scripts').mkdir(parents=True);(self.bundle/'assets').mkdir();(self.bundle/'references').mkdir()
        shutil.copyfile(SOURCE/'foundry.py',self.bundle/'scripts/foundry.py')
        shutil.copyfile(SOURCE/'platform_support.py',self.bundle/'scripts/platform_support.py')
        shutil.copyfile(SOURCE/'production_choices.py', self.bundle/'scripts/production_choices.py')
        shutil.copyfile(SOURCE/'check_foundry_depth.py',self.bundle/'scripts/check_foundry_depth.py')
        shutil.copyfile(SOURCE.parent/'assets/blueprint.template.json',self.bundle/'assets/blueprint.template.json')
        shutil.copyfile(SOURCE.parent/'assets/discovery-topics.json',self.bundle/'assets/discovery-topics.json')
        (self.bundle/'references/generated-agent-contract.md').write_text('Fixed fixture contract.')
        for relative in ('references/adaptive-work.md', 'references/research-and-synthesis.md', 'references/visual-identity.md', 'scripts/adaptive_work.py', 'scripts/visual_identity.py', 'assets/adaptive-task.schema.json', 'assets/adaptive-task.example.json'):
            shutil.copyfile(SOURCE.parent/relative,self.bundle/relative)
        self.script=self.bundle/'scripts/foundry.py';self.root=self.base/'session'
        self.call('init','--project-id','fixture')
        self.bp=blueprint()
        self.bp['production_decision_sha256'] = make_choice(self.root, target_kind='agent')['decision_sha256']

    def tearDown(self):self.temp.cleanup()

    def call(self,cmd,*args,record=None,expected=0,root=None):
        argv=[sys.executable,str(self.script),cmd,str(root or self.root),*map(str,args)]
        if record is not None:argv+=['--record','-']
        p=subprocess.run(argv,input=json.dumps(record) if record is not None else None,text=True,capture_output=True,timeout=8)
        self.assertEqual(p.returncode,expected,p.stdout+p.stderr+'\n'+' '.join(argv))
        return json.loads(p.stdout or p.stderr)

    def state(self):return json.loads((self.root/'.agent-foundry/state.json').read_text())
    def write(self,name,value='fixture bytes'):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value);return p
    def register(self,bp=None):return self.call('blueprint',record=bp or self.bp)
    def auth(self,scope='fixture-construction'):
        return {'source':'actual-fixture-response','verbatim':'Approve the exact stated fixture scope.','actor':'user','scope':scope}
    def approve(self):
        row=self.state()['blueprint'];return self.call('approve','--sha256',row['sha256'],'--revision',row['data']['revision'],'--scope',row['data']['scope'],record=self.auth())
    def ready_design(self):self.register();self.approve()
    def artifact(self,ident='ART-1',name='deliverable/skills/target-agent/SKILL.md',**extra):
        self.write(name,'---\nname: target-agent\ndescription: Coordinate the declared result.\n---\n\nPreserve current requirements and exact scoped decisions.\n')
        row={'id':ident,'path':name,'bundle_path':'skills/target-agent/SKILL.md','phase_id':'PHASE-1','kind':'instruction','author_ids':['maker'],'capability_ids':['CAP-1']};row.update(extra)
        return self.call('artifact',record=row)
    def evidence(self,ident='EV-1',artifact='ART-1',**extra):
        self.write(ident.lower()+'.json','{"synthetic_observation":"fixture only"}')
        row={'id':ident,'source':'fixture-inspection','verbatim':'Inspected the declared fixture.','test_id':'TEST-1','artifact_ids':[artifact],'proof_path':ident.lower()+'.json','observer':'reviewer','status':'pass','environment':'isolated subprocess fixture','method':'Actual fixture assertion','observed_at':'2026-11-01T00:00:00Z'};row.update(extra)
        expected=row.pop('expected',0);return self.call('evidence',record=row,expected=expected)
    def execution(self,ident='EXEC-1',scope='work',phases=None,**extra):
        row=dict(self.auth(scope),id=ident,blueprint_sha256=self.state()['blueprint']['sha256'],phase_ids=phases or ['PHASE-1']);row.update(extra)
        return self.call('execution',record=row)
    def requirement(self,ident='REQ-1',status='pending',priority='must',**extra):
        row={'id':ident,'source':'current-user-fixture','verbatim':'Preserve exact content.','intent':'Preserve exact content.','scope':'work','phase_id':'PHASE-1','owner':'maker','priority':priority,'capability_ids':['CAP-1'],'acceptance':'Exact current output is covered by current proof.','status':status,'artifact_ids':[],'evidence_ids':[]};row.update(extra)
        return self.call('requirement',record=row)
    def task(self,ident='TASK-1',**extra):
        row={'id':ident,'source':'current-user-fixture','verbatim':'Perform the exact declared work.','phase_id':'PHASE-1','scope':'work','goal':'Produce and verify the result.','owner':'maker','execution_id':'EXEC-1','depends_on':[],'requirement_ids':[],'fulfills_requirements':[],'artifact_ids':['ART-1'],'test_ids':['TEST-1'],'independent_review_required':True};row.update(extra)
        return self.call('task',record=row)
    def complete(self,ident='TASK-1'):
        return self.call('complete','--id',ident,'--evidence','EV-1')
    def work(self):
        self.ready_design();self.execution();self.task();self.call('start','--id','TASK-1');self.artifact();self.evidence();self.complete()
    def effect(self,decision='approve',available=True):
        self.ready_design();self.execution();self.task();self.call('start','--id','TASK-1');self.artifact()
        self.call('capability',record={'id':'TOOL-1','source':'fixture-tool-inspection','verbatim':'Observed fixture availability.','scope':'work','environment':'isolated fixture provider','verified_at':'2026-11-01T00:00:00Z','available':available,'effect_types':['write']})
        grant=dict(self.auth('work'),id='GRANT-1',type='write',capability_id='TOOL-1',artifact_ids=['ART-1'],parameters={'target':'fixture-target'},decision=decision,action_id='ACTION-1',idempotency_key='stable-key')
        self.call('grant',record=grant)
        action={'id':'ACTION-1','source':'fixture-request','verbatim':'Perform exact fixture effect.','grant_id':'GRANT-1','idempotency_key':'stable-key','task_id':'TASK-1','type':'write','scope':'work','capability_id':'TOOL-1','artifact_ids':['ART-1'],'parameters':{'target':'fixture-target'}}
        self.call('action',record=action)
        return action
    def dispatch(self,expected=0):return self.call('dispatch','--id','ACTION-1','--revision',self.state()['revision'],expected=expected)
    def receipt(self,outcome='unknown',**extra):
        self.write('receipt.json','{"provider_fixture":"not a live effect"}')
        row={'source':'actual-fixture-provider-response','verbatim':'Fixture provider result observed.','provider_ref':'fixture-operation-1','proof_path':'receipt.json','reconciled':False};row.update(extra)
        expected=row.pop('expected',0);return self.call('receipt','--id','ACTION-1','--outcome',outcome,record=row,expected=expected)

    def test_template_and_missing_blueprint_cannot_build(self):
        self.call('build-gate',expected=1)
        template=json.loads((self.bundle/'assets/blueprint.template.json').read_text());self.call('blueprint',record=template,expected=2)
    def component_route(self,kind='app'):
        self.bp['components'][0]['kind']=kind
        self.bp['components'][0]['specialist_route']={'selector':{'app':'app-atelier-director','chatbot':'chatbot-atelier-director','agent_skill':'design-specialist-skills'}[kind],'handoff_artifact_id':'ART-2','shared_contract_artifact_ids':[]}
        self.bp['artifacts'].append(dict(self.bp['artifacts'][0],id='ART-2',path='components/main-handoff.json',kind='component_handoff'))
        self.bp['capabilities'][0]['artifact_ids'].append('ART-2');self.bp['phases'][0]['artifact_ids'].append('ART-2');self.bp['tests'][0]['artifact_ids'].append('ART-2')
    def test_selected_app_component_requires_declared_route(self):
        self.bp['components'][0]['kind']='app';self.call('blueprint',record=self.bp,expected=2)
    def test_current_component_route_can_be_planned_before_product_execution(self):
        self.component_route();self.register();self.approve();self.assertTrue(self.call('build-gate')['ready']);self.assertEqual({},self.state()['executions'])
    def test_versioned_specialist_selector_is_not_current_identity(self):
        self.component_route();self.bp['components'][0]['specialist_route']['selector']='app-atelier-director-2.2.0';self.call('blueprint',record=self.bp,expected=2)
    def test_bounded_app_stage_route_avoids_new_full_cycle(self):
        self.component_route();self.bp['components'][0]['specialist_route']['selector']='app-atelier-support';self.register();self.approve();self.assertTrue(self.call('build-gate')['ready'])
    def test_cross_family_stage_cannot_substitute_app_route(self):
        self.component_route();self.bp['components'][0]['specialist_route']['selector']='chatbot-atelier-integrations';self.call('blueprint',record=self.bp,expected=2)
    def test_full_coverage_and_unknown_references_rejected(self):
        bp=copy.deepcopy(self.bp);bp['capabilities'][0]['test_ids']=[];self.call('blueprint',record=bp,expected=2)
        bp=copy.deepcopy(self.bp);bp['components'][0]['owner']='MISSING';self.call('blueprint',record=bp,expected=2)
    def test_dynamic_phase_dag_not_skill_count(self):
        bp=self.bp;phase=copy.deepcopy(bp['phases'][0]);phase.update(id='PHASE-2',name='Second phase',depends_on=['PHASE-1']);bp['phases'].append(phase)
        bp['capabilities'][0]['phase_ids'].append('PHASE-2');bp['skills'][0]['phase_ids'].append('PHASE-2')
        self.register();self.approve();self.assertTrue(self.call('build-gate')['ready'])
    def test_phase_cycles_and_cross_output_coverage_rejected(self):
        bp=copy.deepcopy(self.bp);bp['phases'][0]['depends_on']=['PHASE-1'];self.call('blueprint',record=bp,expected=2)
        bp=copy.deepcopy(self.bp);bp['tests'][0]['artifact_ids']=['UNKNOWN'];self.call('blueprint',record=bp,expected=2)
    def test_blocking_questions_prevent_approval(self):
        self.bp['questions']=[{'id':'Q-1','question':'Select concrete scope.','explanation':'Different result paths.','status':'pending','blocking':True}]
        out=self.register();self.assertFalse(out['ready_for_approval'])
        row=self.state()['blueprint'];self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=self.auth(),expected=2)
    def test_approval_exact_hash_revision_scope_actor(self):
        self.register();row=self.state()['blueprint']
        self.call('approve','--sha256','0'*64,'--revision',1,'--scope','fixture-construction',record=self.auth(),expected=2)
        self.call('approve','--sha256',row['sha256'],'--revision',2,'--scope','fixture-construction',record=self.auth(),expected=2)
        self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','other',record=self.auth(),expected=2)
        a=self.auth();a['actor']='agent';self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=a,expected=2)
        self.approve();self.assertTrue(self.call('build-gate')['ready'])
    def test_blueprint_change_stales_approval_preserves_must_history(self):
        self.ready_design();new=copy.deepcopy(self.bp);new['revision']=2;new['capabilities'][0]['priority']='should'
        self.call('blueprint',record=new,expected=2)
        oldhash=self.state()['blueprint']['sha256'];a=dict(self.auth(),from_sha256=oldhash,to_sha256=digest(new),changed_ids=['CAP-1'])
        path=self.write('amendment.json',json.dumps(a));self.call('blueprint','--change-authority',path,record=new)
        self.call('build-gate',expected=1);self.assertEqual(self.state()['blueprint_history'][0]['data']['capabilities'][0]['priority'],'must')
    def test_input_source_change_latches_approval_stale(self):
        p=self.write('inputs/reference.txt','original');self.bp['input_sources']=[{'path':'inputs/reference.txt','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'actual original fixture'}]
        self.ready_design();p.write_text('changed');self.call('build-gate',expected=1);p.write_text('original');self.call('build-gate',expected=1)
    def test_material_lesson_stales_approval(self):
        self.ready_design();self.call('lesson',record={'id':'L-1','source':'actual observation','verbatim':'The rule changes.','text':'The rule changes.','scope':'fixture','confidence':'observed','material':True,'impact_ids':['CAP-1'],'phase_ids':[],'impact_reason':'Alters the required result.'});self.call('build-gate',expected=1)
    def test_nonmaterial_lesson_invalidates_only_affected_outputs(self):
        self.ready_design();self.artifact();self.evidence();self.call('lesson',record={'id':'L-1','source':'actual observation','verbatim':'Recheck the current output.','text':'Recheck the current output.','scope':'fixture','confidence':'observed','material':False,'impact_ids':['ART-1'],'phase_ids':[],'impact_reason':'Output-specific proof.'})
        self.assertTrue(self.call('build-gate')['ready']);self.assertEqual(self.state()['artifacts']['ART-1']['status'],'stale');self.call('refresh');self.assertEqual(self.state()['evidence']['EV-1']['status'],'stale')
    def test_independent_test_rejects_author_and_observed(self):
        self.ready_design();self.artifact();self.evidence(observer='maker',expected=2);self.evidence(status='observed',expected=2);self.evidence()
    def test_evidence_must_cover_declared_artifacts(self):
        self.ready_design();self.artifact();self.evidence(artifact='OTHER',expected=2)

    def test_supplied_old_observation_is_never_rebound_to_new_bytes(self):
        self.ready_design();self.artifact();self.evidence()
        old = self.state()['evidence']['EV-1']
        self.write('deliverable/skills/target-agent/SKILL.md', 'materially changed output')
        record = self.state()['artifacts']['ART-1']
        for key in ('sha256', 'definition_sha256', 'revision', 'status'): record.pop(key, None)
        self.call('artifact', record=record)
        self.assertEqual(self.state()['evidence']['EV-1']['status'], 'stale')
        old.update(id='EV-2', status='pass')
        self.call('evidence', record=old, expected=2)
        self.assertNotIn('EV-2', self.state()['evidence'])

    def test_operating_source_changes_outside_old_eleven_pins_block_execution(self):
        self.ready_design()
        self.bundle.joinpath('SKILL.md').write_text('Material operating instruction')
        self.assertFalse(self.call('build-gate', expected=1)['ready'])

    def test_duplicate_json_keys_are_rejected_before_record_mutation(self):
        payload = '{"id":"GOOD","id":"CONTRADICTORY"}'
        command = [sys.executable, str(self.script), 'requirement', str(self.root), '--record', '-']
        result = subprocess.run(command, input=payload, text=True, capture_output=True, timeout=8)
        self.assertEqual(result.returncode, 2)
        self.assertIn('duplicate JSON key', result.stderr + result.stdout)
        self.assertFalse(self.state()['requirements'])
    def test_immutable_artifact_cannot_be_replaced(self):
        self.ready_design();self.artifact(immutable=True);self.write('deliverable/skills/target-agent/SKILL.md','changed');self.call('artifact',record={'id':'ART-1','path':'deliverable/skills/target-agent/SKILL.md','bundle_path':'skills/target-agent/SKILL.md','phase_id':'PHASE-1','kind':'instruction','author_ids':['maker'],'capability_ids':['CAP-1'],'immutable':False},expected=2)
    def test_design_approval_does_not_authorize_product_execution(self):
        self.ready_design();self.task();self.call('readiness','--id','TASK-1',expected=1)
    def test_pending_requirement_can_be_implemented_not_skipped(self):
        self.ready_design();self.execution();self.requirement();self.task(requirement_ids=['REQ-1'],fulfills_requirements=['REQ-1']);self.call('start','--id','TASK-1');self.artifact();self.evidence();self.call('complete','--id','TASK-1','--evidence','EV-1',expected=2)
        self.requirement(status='met',artifact_ids=['ART-1'],evidence_ids=['EV-1']);self.complete();self.assertEqual(self.state()['tasks']['TASK-1']['status'],'completed')
    def test_should_declared_fulfillment_must_close(self):
        self.ready_design();self.execution();self.requirement(priority='should');self.task(fulfills_requirements=['REQ-1']);self.call('start','--id','TASK-1');self.artifact();self.evidence();self.call('complete','--id','TASK-1','--evidence','EV-1',expected=2)
    def test_completed_task_and_downstream_stale_after_proof_change(self):
        self.work();self.task('TASK-2',depends_on=['TASK-1']);self.call('start','--id','TASK-2');self.complete('TASK-2');self.write('ev-1.json','changed proof');self.call('context');self.assertEqual(self.state()['tasks']['TASK-1']['status'],'stale');self.assertEqual(self.state()['tasks']['TASK-2']['status'],'stale')
    def test_phase_prerequisite_cannot_be_omitted(self):
        phase=copy.deepcopy(self.bp['phases'][0]);phase.update(id='PHASE-2',name='Second phase',depends_on=['PHASE-1']);self.bp['phases'].append(phase);self.bp['capabilities'][0]['phase_ids'].append('PHASE-2');self.bp['skills'][0]['phase_ids'].append('PHASE-2')
        self.ready_design();self.execution(phases=['PHASE-1','PHASE-2']);self.task('TASK-2',phase_id='PHASE-2');self.call('readiness','--id','TASK-2',expected=1)
    def test_current_due_must_blocks_phase_completion(self):
        self.work();self.requirement();self.call('phase-check','--id','PHASE-1','--scope','work','--execution-id','EXEC-1',expected=1)
    def test_query_keeps_required_dependencies_and_must(self):
        self.ready_design();self.execution();self.requirement();self.task(requirement_ids=['REQ-1'],fulfills_requirements=['REQ-1'],goal='unique-query-phrase');out=self.call('context','--query','unique-query-phrase');self.assertEqual(out['records']['requirements'][0]['id'],'REQ-1');self.assertTrue(out['always_review']['must_or_emphasized'])
    def test_pause_now_cannot_be_rearmed_and_blocks_start(self):
        self.ready_design();self.execution();self.task();self.call('pause',record={'source':'user-fixture','verbatim':'Pause now.','reason':'User stop','boundary':'now'});self.call('start','--id','TASK-1',expected=2);self.call('pause',record={'source':'user-fixture','verbatim':'After task.','reason':'future stop','boundary':'after_task','task_id':'TASK-1'},expected=2);self.call('resume');self.call('start','--id','TASK-1')
    def test_exact_after_artifact_pause(self):
        self.ready_design();self.call('pause',record={'source':'user-fixture','verbatim':'Stop after exact output.','reason':'preview','boundary':'after_artifact','artifact_id':'ART-1'});self.artifact();self.assertTrue(self.state()['pause']['active']);self.call('build-gate',expected=1)
    def test_after_task_and_phase_pause(self):
        self.ready_design();self.execution();self.task();self.call('pause',record={'source':'user-fixture','verbatim':'After task.','reason':'preview','boundary':'after_task','task_id':'TASK-1'});self.call('start','--id','TASK-1');self.artifact();self.evidence();self.complete();self.assertTrue(self.state()['pause']['active']);self.call('resume')
        self.call('pause',record={'source':'user-fixture','verbatim':'After phase.','reason':'review','boundary':'after_phase','phase_id':'PHASE-1','scope':'work','execution_id':'EXEC-1'});self.call('phase-check','--id','PHASE-1','--scope','work','--execution-id','EXEC-1');self.assertTrue(self.state()['pause']['active'])
    def test_decline_or_missing_capability_cannot_dispatch(self):
        self.effect(decision='decline');self.dispatch(expected=2)
    def test_unavailable_capability_cannot_dispatch(self):
        self.effect(available=False);self.dispatch(expected=2)
    def test_unknown_outcome_no_retry_and_reconcile(self):
        self.effect();out=self.dispatch();self.assertFalse(out['executed']);self.dispatch(expected=2);self.receipt();self.call('resume',expected=2);self.receipt('succeeded',expected=2);self.receipt('succeeded',reconciled=True);self.call('resume');self.dispatch(expected=2)
    def test_grant_is_single_action_and_exact_prepared_bytes(self):
        action=self.effect();copy_action=dict(action,id='ACTION-2',idempotency_key='different-key');self.call('action',record=copy_action,expected=2)
        self.write('deliverable/skills/target-agent/SKILL.md','changed bytes');self.dispatch(expected=2)
    def test_stale_project_revision_rejected_before_effect(self):
        self.effect();self.call('dispatch','--id','ACTION-1','--revision',1,expected=2)
    def test_canonical_denial_and_revocation_cannot_become_approval(self):
        self.register();row=self.state()['blueprint'];doc={'schema_version':'foundry-authority/1','items':[{'id':'A-1','actor':'user','decision':'decline','scope':'fixture-construction','subject_sha256':row['sha256']}]};p=self.write('inputs/authority.json',json.dumps(doc));a=self.auth();a['canonical_authority']={'path':'inputs/authority.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'record_id':'A-1'}
        self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=a,expected=2)
        doc['items'][0]['decision']='approve';p.write_text(json.dumps(doc));a['canonical_authority']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=a)
        doc['items'][0]['decision']='revoked';p.write_text(json.dumps(doc));self.call('build-gate',expected=1)
    def test_explicit_decline_without_canonical_binding_never_confirms(self):
        self.register();row=self.state()['blueprint'];record=dict(self.auth(),decision='decline',verbatim='I decline the proposed scope.')
        self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=record,expected=2)
        self.assertIsNone(self.state()['approval']);self.call('build-gate',expected=1)
    def test_negative_typed_authority_variants_cannot_confirm(self):
        self.register();row=self.state()['blueprint']
        for extra in ({'decision':'revoked'},{'decision':'pending'},{'revoked':True},{'revoked':'true'},{'revoked':0},{'status':'declined'},{'status':'pending'}):
            self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=dict(self.auth(),**extra),expected=2)
            self.assertIsNone(self.state()['approval'])
    def test_approve_command_normalizes_conversational_authority(self):
        self.ready_design();self.assertEqual(self.state()['approval']['decision'],'approve');self.assertTrue(self.call('build-gate')['ready'])
    def test_historical_contradictory_typed_approval_is_not_current(self):
        self.ready_design();state=self.state();state['approval']['decision']='decline'
        state['snapshot_hash']=digest({k:v for k,v in state.items() if k!='snapshot_hash'})
        (self.root/'.agent-foundry/state.json').write_text(json.dumps(state))
        self.call('build-gate',expected=1)
    def test_safe_intake_rejects_traversal_links_case_duplicates(self):
        variants=[('../escape.txt',b'x',None),('linked',b'x',stat.S_IFLNK|0o777)]
        for number,(name,value,mode) in enumerate(variants):
            p=self.base/('bad'+str(number)+'.zip')
            with zipfile.ZipFile(p,'w') as z:
                info=zipfile.ZipInfo(name)
                if mode:info.external_attr=mode<<16
                z.writestr(info,value)
            self.call('intake','--source',p,record={'id':'bad-'+str(number),'source':'fixture archive','rights':'fixture owned'},expected=2)
        p=self.base/'duplicate.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr('A.txt','one');z.writestr('a.txt','two')
        self.call('intake','--source',p,record={'id':'case-duplicate','source':'fixture archive','rights':'fixture owned'},expected=2)
        self.assertFalse((self.root/'escape.txt').exists())
    def test_import_preserves_originals_never_executes_and_never_overwrites(self):
        p=self.base/'original.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr('source.txt','original bytes');z.writestr('instruction.py','raise RuntimeError("must never execute")')
        rec={'id':'original','source':'actual fixture origin','rights':'fixture owned'};out=self.call('intake','--source',p,record=rec);self.assertFalse(out['executed']);self.call('intake','--source',p,record=rec,expected=2)
        self.write('inputs/original/source.txt','changed');self.call('refresh',expected=1)
    def test_concurrent_writers_and_journal_integrity(self):
        def worker(i):return self.call('capability',record={'id':'TOOL-'+str(i),'source':'fixture observation','verbatim':'Observed fixture.','scope':'fixture','environment':'local fixture','verified_at':'fixture time','available':False})
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(worker,range(12)))
        self.assertEqual(len(self.state()['capabilities']),12);self.call('context')
    def test_state_tamper_and_fifo_fail_without_hang(self):
        p=self.root/'.agent-foundry/state.json';state=self.state();state['project_id']='tampered';p.write_text(json.dumps(state));self.call('context',expected=2)
        p.unlink();p.parent.joinpath('state.json').touch();p.unlink()
        import os
        os.mkfifo(p);self.call('context',expected=2)
    def test_compatible_suite_review_does_not_reask_design_approval(self):
        self.ready_design();p=self.bundle/'references/generated-agent-contract.md';p.write_text('Compatible editorial cleanup.');self.call('build-gate',expected=1)
        plan=self.call('suite-update-plan')
        review={'source':'actual compatibility review','verbatim':'Only editorial clarification changed.','review':'Reviewed exact diff.','impact_ids':[],'material':False,
                'expected_state_sha256':plan['expected_state_sha256'],'target_suite_sha256':plan['target_suite_sha256']}
        before=(self.root/'.agent-foundry/state.json').read_bytes()
        result=self.call('refresh','--accept-suite-update',record=review)
        self.assertEqual((self.root/result['backup_path']).read_bytes(),before)
        self.assertTrue(self.call('build-gate')['ready'])
        current=(self.root/'.agent-foundry/state.json').read_bytes()
        self.assertTrue(self.call('refresh','--accept-suite-update',record=review)['replayed'])
        self.assertEqual((self.root/'.agent-foundry/state.json').read_bytes(),current)

    def test_suite_update_plan_is_read_only_and_rejects_changed_target(self):
        self.ready_design();path=self.root/'.agent-foundry/state.json';before=path.read_bytes()
        plan=self.call('suite-update-plan');self.assertEqual(path.read_bytes(),before)
        self.assertFalse((self.root/'.agent-foundry/backups').exists())
        self.bundle.joinpath('references/generated-agent-contract.md').write_text('Changed after exact preview')
        review={'source':'SYNTHETIC','verbatim':'Review exact snapshot only','review':'Fixture review','impact_ids':[],'material':False,
                'expected_state_sha256':plan['expected_state_sha256'],'target_suite_sha256':plan['target_suite_sha256']}
        self.call('refresh','--accept-suite-update',record=review,expected=2)
        self.assertEqual(self.state()['suite_reviews'],[])

    def test_suite_adoption_rejects_stale_project_state(self):
        self.ready_design();plan=self.call('suite-update-plan')
        self.requirement('NEW-MUST')
        review={'source':'SYNTHETIC','verbatim':'Review exact snapshot only','review':'Fixture review','impact_ids':[],'material':False,
                'expected_state_sha256':plan['expected_state_sha256'],'target_suite_sha256':plan['target_suite_sha256']}
        self.call('refresh','--accept-suite-update',record=review,expected=2)
        self.assertIn('NEW-MUST',self.state()['requirements'])
    def test_bundle_check_exact_approved_skills_proofs_and_bytes(self):
        self.ready_design();self.artifact();self.call('bundle-check','--directory',self.root/'deliverable',expected=1);self.evidence()
        make_choice(self.root, target_kind='agent', phase='accept',
                    accepted_artifacts=['deliverable/skills/target-agent/SKILL.md'])
        self.assertTrue(self.call('bundle-check','--directory',self.root/'deliverable')['valid'])
        self.write('deliverable/skills/unapproved/SKILL.md','---\nname: unapproved\ndescription: Unexpected scope.\n---\n\nUnexpected instruction.\n');self.call('bundle-check','--directory',self.root/'deliverable',expected=1)

    def test_material_gate_blocks_legacy_blueprint_and_stale_choice_after_resume(self):
        original = self.bp['production_decision_sha256']
        del self.bp['production_decision_sha256']
        self.ready_design()
        self.assertTrue(self.call('check')['valid'])
        self.assertIn('production_decision_sha256', str(self.call('build-gate', expected=1)['blockers']))
        self.bp.update(revision=2, production_decision_sha256=original)
        self.ready_design();self.execution();self.task()
        self.assertTrue(self.call('build-gate')['ready'])
        self.assertFalse(self.call('build-gate','--phase','scale',expected=1)['ready'])
        self.call('pause',record={'source':'fixture','verbatim':'Pause this task.', 'reason':'pause for review','boundary':'now'})
        self.write('_choice-fixture/configuration.md', 'Unreviewed replacement')
        self.call('resume')
        self.assertIn('configuration.md', str(self.call('readiness','--id','TASK-1',expected=1)['blockers']))

    def test_real_foundry_exports_and_installs_the_verified_child(self):
        from test_install_agent import PortableTests

        portable = PortableTests(methodName='runTest')
        portable.setUp()
        self.addCleanup(portable.tearDown)
        self.script = SOURCE / 'foundry.py'
        self.root = self.base / 'real-session'
        self.call('init', '--project-id', 'real-fixture')
        self.bp['production_decision_sha256'] = make_choice(self.root, target_kind='agent')['decision_sha256']
        kit = self.root / 'deliverable'
        entry, = portable.skills(1, prefix='real', kit=kit)
        self.bp['entry_skill'] = self.bp['skills'][0]['name'] = entry
        relative = f'skills/{entry}/SKILL.md'
        staged = 'deliverable/' + relative
        self.bp['artifacts'][0]['path'] = relative
        self.ready_design()
        self.call('artifact', record={'id': 'ART-1', 'path': staged, 'bundle_path': relative,
                                     'phase_id': 'PHASE-1', 'kind': 'instruction',
                                     'author_ids': ['maker'], 'capability_ids': ['CAP-1']})
        self.evidence()
        output = self.base / 'verified-child.zip'
        args = ['--kit', kit, '--agent-id', entry, '--entry-skill', entry, '--version', '1.0.0',
                '--purpose', 'generated', '--session', self.root, '--kit-output', output]
        make_choice(self.root, target_kind='agent', phase='accept')
        failure = portable.call(SOURCE / 'package_agent.py', args, expected=2)
        self.assertIn('exact packaged skill', failure['error'])
        self.assertFalse(output.exists())
        receipt = make_choice(self.root, target_kind='agent', phase='accept',
                              accepted_artifacts=[staged])
        portable.call(SOURCE / 'package_agent.py', args)
        with zipfile.ZipFile(output) as archive:
            for member in archive.infolist():
                extracted = Path(archive.extract(member, self.base / 'extracted'))
                if not member.is_dir():
                    extracted.chmod(stat.S_IMODE(member.external_attr >> 16))
        delivered = next((self.base / 'extracted').rglob('manifest.json')).parent
        manifest = json.loads((delivered / 'manifest.json').read_bytes())
        self.assertEqual(receipt['decision_sha256'], manifest['blueprint']['production_decision_sha256'])
        installer = SOURCE.parents[2] / 'portable/install_agent.py'
        consumer = self.base / 'recipient'
        portable.call(installer, ['--kit', delivered, '--project', consumer, '--mode', 'apply'])
        verifier = consumer / '.agents/skills' / entry / 'scripts/production_choices.py'
        verify = ['verify', consumer, '--phase', 'implement']
        self.assertFalse(portable.call(verifier, verify, expected=1)['ok'])
        make_choice(consumer)
        self.assertTrue(portable.call(verifier, verify)['ok'])
    def test_regular_usage_creates_no_installed_cache(self):
        before={str(p.relative_to(self.bundle)) for p in self.bundle.rglob('*')};self.ready_design();self.call('context');self.call('build-gate');self.assertEqual(before,{str(p.relative_to(self.bundle)) for p in self.bundle.rglob('*')})
    def test_purposes_use_separate_sessions_preserve_existing_project(self):
        self.write('existing/source.txt','keep original');other=self.base/'target-project';self.call('init','--project-id','target','--purpose','project',root=other);self.call('init','--project-id','fixture','--purpose','project',expected=2);self.assertEqual((self.root/'existing/source.txt').read_text(),'keep original');self.assertEqual(self.state()['purpose'],'factory')
    def test_discovery_catalog_coverage_and_pending_construction_topic(self):
        bp=copy.deepcopy(self.bp);bp['discovery_coverage'].pop();self.call('blueprint',record=bp,expected=2)
        self.bp['discovery_coverage'][0]['current_status']='pending';self.register();self.call('build-gate',expected=1)
        row=self.state()['blueprint'];self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=self.auth(),expected=2)
    def test_future_product_decision_resolves_without_reapproving_agent(self):
        self.bp['questions']=[{'id':'Q-LATER','question':'Choose the current output route.','explanation':'Changes this result.','status':'deferred','blocking':False,'due_phase':'PHASE-1','options':['route-a','route-b']}]
        self.ready_design();self.execution();self.task();self.call('readiness','--id','TASK-1',expected=1)
        d={'id':'Q-LATER','source':'current-user-fixture','verbatim':'Choose current route.','question':'Choose the current output route.','options':['route-a','route-b'],'scope':'work','phase_ids':['PHASE-1'],'task_ids':[],'material':True,'status':'pending'}
        self.call('decision',record=d);definition={k:d[k] for k in ('id','question','options','scope','phase_ids','task_ids','material')};d.update(status='confirmed',answer='route-a',confirms_sha256=digest(definition),authority=dict(self.auth('work'),choice='route-a'))
        self.call('decision',record=d);self.assertTrue(self.call('readiness','--id','TASK-1')['ready']);self.assertTrue(self.call('build-gate')['ready'])
    def test_parallel_tasks_fulfill_separate_musts_without_deadlock(self):
        self.ready_design();self.execution();self.requirement('REQ-A');self.requirement('REQ-B');self.task('TASK-A',requirement_ids=['REQ-A'],fulfills_requirements=['REQ-A']);self.task('TASK-B',requirement_ids=['REQ-B'],fulfills_requirements=['REQ-B'])
        self.assertTrue(self.call('readiness','--id','TASK-A')['ready']);self.assertTrue(self.call('readiness','--id','TASK-B')['ready'])
    def test_reopened_requirement_invalidates_completed_task(self):
        self.ready_design();self.execution();self.requirement();self.task(requirement_ids=['REQ-1'],fulfills_requirements=['REQ-1']);self.call('start','--id','TASK-1');self.artifact();self.evidence();self.requirement(status='met',artifact_ids=['ART-1'],evidence_ids=['EV-1']);self.complete();self.requirement(status='pending');self.call('context');self.assertEqual(self.state()['tasks']['TASK-1']['status'],'stale')
    def test_canonical_approval_binding_cannot_be_dropped(self):
        self.register();row=self.state()['blueprint'];doc={'schema_version':'foundry-authority/1','items':[{'id':'AUTH-1','actor':'user','decision':'approve','scope':'fixture-construction','subject_sha256':row['sha256']}]};p=self.write('inputs/authority.json',json.dumps(doc));a=self.auth();a['canonical_authority']={'path':'inputs/authority.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'record_id':'AUTH-1'};self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=a)
        doc['items'][0]['decision']='revoked';p.write_text(json.dumps(doc));self.call('approve','--sha256',row['sha256'],'--revision',1,'--scope','fixture-construction',record=self.auth(),expected=2)
    def test_material_project_decision_cannot_be_silently_downgraded(self):
        self.ready_design();d={'id':'Q-CURRENT','source':'actual-user-fixture','verbatim':'Choose current route.','question':'Choose a route.','options':['a','b'],'scope':'work','phase_ids':['PHASE-1'],'task_ids':[],'material':True,'status':'pending'};self.call('decision',record=d);d['material']=False;self.call('decision',record=d,expected=2)
    def test_emphasized_requirement_remains_visible_for_unrelated_query(self):
        self.ready_design();self.requirement(priority='should',emphasis=True);out=self.call('context','--query','unrelated-search');self.assertEqual(out['always_review']['current_project_must'][0]['id'],'REQ-1')


if __name__=='__main__':unittest.main()
