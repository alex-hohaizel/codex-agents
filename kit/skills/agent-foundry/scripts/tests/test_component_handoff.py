import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'check_component_handoff.py'
spec=importlib.util.spec_from_file_location('component_handoff',SCRIPT)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class ComponentHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'input.md').write_text('synthetic accepted product requirements')
        (self.root/'skill.md').write_text('---\nname: app-atelier-director\ndescription: fixture\n---\nFixture method.')
        (self.root/'contract.md').write_text('Shared identity and user consent contract, one owner.')
        (self.root/'output.md').write_text('synthetic component output')
        self.file=lambda p:{'path':p,'sha256':hashlib.sha256((self.root/p).read_bytes()).hexdigest()}
        self.d={'schema_version':'atelier-component-handoff/1','is_template':False,'product_id':'product-fixture','component_id':'app','component_kind':'app','status':'prepared','parent_intent_ref':'synthetic request','authority_ref':'synthetic exact user scope','parent_requirement_ids':['P1','P2'],'owned_requirement_ids':['P1'],'scope':{'goal':'orders client','included':['orders'],'excluded':['payments'],'stop':'prepared design'},'consumer':'app lead','permissions':{'source_ref':'synthetic scope','grant':'planning_only','allowed_effects':[]},'budget':{'cap':'zero external cost'},'decisions':['product scope selected'],'environment_capabilities':['local fixture read/write'],'inputs':[self.file('input.md')],'shared_contract_refs':[],'related_components':[],'invocation':{'selector':'app-atelier-director','activity':'planning','environment':'codex','availability':'available','status':'planned','resolution':{'source_ref':'actual local fixture','snapshot':self.file('skill.md')},'receipt_refs':[]},'fallback':None,'deliverables':[],'acceptance':['exact orders design'],'evidence':[],'actual_jobs':[],'open_questions':[],'checkpoint':{'next':'app design'},'next_action':'invoke selected app scope','return_condition':'missing identity contract returns to parent'}
        self.d.update(return_to={'selector':'agent-foundry','component_id':'root'},orchestrator_chain=['agent-foundry','app-atelier-director'],selected_channels=[],proposed_channels=[],platform_adapter_contract_refs=[])
    def tearDown(self):self.temp.cleanup()
    def check(self,ready=False):return c.check(self.d,self.root,ready)
    def executed(self):
        self.d['status']='executed';self.d['permissions']['grant']='component_execution';self.d['invocation'].update(status='performed',activity='product_execution',actor='fixture specialist',receipt_refs=['E1'])
        self.d['evidence']=[dict(self.file('output.md'),id='E1',claim='fixture component completed',actor='fixture specialist',method='fixture operation',scope='P1 only',component_id='app',requirement_ids=['P1'])]
        self.d['deliverables']=[self.file('output.md')]
    def mixed(self):
        self.d['shared_contract_refs']=[dict(self.file('contract.md'),id='ID1',owner='parent integrator',component_ids=['app','bot'])]
        self.d['related_components']=[{'component_id':'bot','component_kind':'chatbot','contract_ids':['ID1']}]
    def test_current_prepared_handoff_not_runtime_claim(self):self.assertEqual([],self.check(True))
    def test_current_executed_handoff(self):self.executed();self.assertEqual([],self.check(True))
    def test_missing_specialist_cannot_claim_invoked(self):
        self.executed();self.d['invocation']['availability']='unavailable';self.assertTrue(any('missing skill' in e for e in self.check()))
    def test_unknown_specialist_blocks_ready(self):
        self.d['invocation']['availability']='unknown';self.assertTrue(any('specialist missing' in e for e in self.check(True)))
    def test_construction_grant_does_not_start_app(self):
        self.executed();self.d['permissions']['grant']='construction_only';self.assertTrue(any('product execution' in e for e in self.check()))
    def test_parent_scope_reused_without_new_approval_object(self):
        self.assertNotIn('approval',self.d);self.assertEqual([],self.check(True))
    def test_missing_invocation_receipt(self):
        self.executed();self.d['invocation']['receipt_refs']=[];self.assertTrue(any('receipt evidence' in e for e in self.check()))
    def test_stale_source_snapshot(self):
        (self.root/'skill.md').write_text('changed source');self.assertTrue(any('hash is stale' in e for e in self.check()))
    def test_wrong_resolved_source(self):
        (self.root/'skill.md').write_text('---\nname: chatbot-atelier-director\n---\nWrong source');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertTrue(any('frontmatter differs' in e for e in self.check()))
    def test_version_not_part_of_selector(self):
        self.d['invocation']['selector']='app-atelier-director-2.2.0';self.assertTrue(any('stable supported selector' in e for e in self.check()))
    def test_direct_stage_invocation_is_factual_without_claiming_director(self):
        self.d['invocation']['selector']='app-atelier-support';self.d['orchestrator_chain'][-1]='app-atelier-support';(self.root/'skill.md').write_text('---\nname: app-atelier-support\n---\nFixture support method.');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertEqual([],self.check(True))
    def test_wrong_family_stage_is_rejected(self):
        self.d['invocation']['selector']='chatbot-atelier-integrations';self.assertTrue(any('own family' in e for e in self.check()))
    def test_mixed_product_has_shared_contract(self):self.mixed();self.assertEqual([],self.check(True))
    def test_mixed_product_missing_shared_contract(self):
        self.mixed();self.d['shared_contract_refs']=[];self.assertTrue(any('missing shared contract' in e for e in self.check()))
    def test_shared_contract_must_bind_peer(self):
        self.mixed();self.d['shared_contract_refs'][0]['component_ids']=['app'];self.assertTrue(any('bind related component' in e for e in self.check()))
    def test_dropped_parent_requirement_is_rejected(self):
        self.d['owned_requirement_ids']=['foreign'];self.assertTrue(any('parent authority' in e for e in self.check()))
    def test_component_paths_cannot_escape(self):
        self.d['inputs'][0]['path']='../secret';self.assertTrue(any('contained relative' in e for e in self.check()))
    def test_constructor_embedded_method_fallback_preserves_missing_status(self):
        self.d.update(component_kind='agent_skill',component_id='skills');self.d['permissions']['grant']='construction_only';self.d['invocation'].update(selector='design-specialist-skills',activity='skill_construction',availability='unavailable',status='blocked',resolution=None);self.d['orchestrator_chain'][-1]='design-specialist-skills'
        self.d['fallback']=dict(mode='embedded_method',reason='specialized constructor absent on fixture host',owner='factory',consumer='child skill receiver',acceptance='same child contract accepted',method=self.file('contract.md'))
        self.assertEqual([],self.check(True));self.assertEqual('blocked',self.d['invocation']['status'])
    def test_app_missing_skill_cannot_use_constructor_fallback(self):
        self.d['invocation']['availability']='unavailable';self.d['fallback']=dict(mode='embedded_method',reason='missing',owner='factory',consumer='app',acceptance='same contract',method=self.file('contract.md'));self.assertTrue(self.check(True))
    def test_unresolved_product_choice_blocks_receiving_readiness(self):
        self.d['open_questions']=[{'blocking':True,'status':'pending','question':'which channels'}];self.assertTrue(any('unresolved' in e for e in self.check(True)))
    def test_unsupported_prior_format_rejected(self):
        self.d['schema_version']='atelier-component-handoff/0';self.assertTrue(any('unsupported' in e for e in self.check()))
    def test_cli_malformed_input_returns_json_failure(self):
        p=self.root/'bad.json';p.write_text('[]');run=subprocess.run([sys.executable,'-B',str(SCRIPT),str(p)],text=True,capture_output=True);self.assertEqual(1,run.returncode);self.assertFalse(json.loads(run.stdout)['structurally_valid'])

    def select(self, selector, kind=None):
        self.d['invocation']['selector']=selector;self.d['orchestrator_chain'][-1]=selector
        (self.root/'skill.md').write_text('---\nname: '+selector+'\n---\nFixture method.')
        self.d['invocation']['resolution']['snapshot']=self.file('skill.md')
        if kind:self.d['component_kind']=kind
    def test_name_in_body_does_not_override_actual_frontmatter(self):
        (self.root/'skill.md').write_text('---\nname: chatbot-atelier-director\n---\nExample only:\nname: app-atelier-director\n');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertTrue(any('frontmatter differs' in e for e in self.check(True)))
    def test_missing_initial_frontmatter_is_rejected(self):
        (self.root/'skill.md').write_text('Body only\nname: app-atelier-director\n');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertTrue(self.check(True))
    def test_duplicate_frontmatter_name_is_rejected(self):
        (self.root/'skill.md').write_text('---\nname: app-atelier-director\nname: chatbot-atelier-director\n---\n');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertTrue(self.check(True))
    def test_quoted_actual_frontmatter_is_accepted(self):
        (self.root/'skill.md').write_text('---\nname: "app-atelier-director"\n---\nFixture');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertEqual([],self.check(True))
    def test_windows_newline_frontmatter_is_accepted(self):
        (self.root/'skill.md').write_bytes(b'---\r\nname: app-atelier-director\r\n---\r\nFixture');self.d['invocation']['resolution']['snapshot']=self.file('skill.md');self.assertEqual([],self.check(True))
    def test_receipt_actor_must_match_actual_invocation_actor(self):
        self.executed();self.d['invocation']['actor']='another actor';self.assertTrue(any('actor differs' in e for e in self.check(True)))
    def test_receipt_must_bind_current_component(self):
        self.executed();self.d['evidence'][0]['component_id']='unrelated';self.assertTrue(any('bind this component' in e for e in self.check(True)))
    def test_receipt_requirements_must_be_owned(self):
        self.executed();self.d['evidence'][0]['requirement_ids']=['P2'];self.assertTrue(any('outside component scope' in e for e in self.check(True)))
    def test_receipt_requires_explicit_requirement_bindings(self):
        self.executed();del self.d['evidence'][0]['requirement_ids'];self.assertTrue(any('requirement_ids' in e for e in self.check(True)))
    def test_stage_chain_cannot_claim_director(self):
        self.select('app-atelier-support');self.d['orchestrator_chain'][-1]='app-atelier-director';self.assertTrue(any('terminate' in e for e in self.check(True)))
    def test_version_number_not_allowed_in_return_selector(self):
        self.d['return_to']['selector']='agent-foundry-2.2.0';self.assertTrue(any('stable return' in e for e in self.check(True)))
    def test_return_selector_must_match_immediate_parent(self):
        self.d['return_to']['selector']='unrelated-project-integrator';self.assertTrue(any('immediate parent' in e for e in self.check(True)))
    def test_malformed_open_question_cannot_be_ignored(self):
        self.d['open_questions']=['blocking pending'];self.assertTrue(any('open question' in e for e in self.check(True)))
    def test_open_question_requires_explicit_boolean_blocking(self):
        self.d['open_questions']=[{'question':'channel','status':'pending','blocking':'false'}];self.assertTrue(any('must be boolean' in e for e in self.check(True)))
    def test_resolved_open_question_requires_decision_source(self):
        self.d['open_questions']=[{'question':'channel','status':'resolved','blocking':True}];self.assertTrue(any('resolution_ref' in e for e in self.check(True)))
    def test_resolved_question_with_current_source_is_receivable(self):
        self.d['open_questions']=[{'question':'channel','status':'resolved','blocking':True,'resolution_ref':'accepted parent decision D1'}];self.assertEqual([],self.check(True))
    def test_prepared_deliverable_cannot_escape(self):
        self.d['deliverables']=[{'path':'../private','sha256':'0'*64}];self.assertTrue(any('contained relative' in e for e in self.check(True)))
    def test_draft_deliverable_hash_is_checked(self):
        self.d['status']='draft';self.d['deliverables']=[{'path':'output.md','sha256':'0'*64}];self.assertTrue(any('hash is stale' in e for e in self.check()))
    def test_prepared_actual_deliverable_is_valid(self):
        self.d['deliverables']=[self.file('output.md')];self.assertEqual([],self.check(True))
    def test_planning_research_does_not_require_product_execution_grant(self):
        self.executed();self.select('app-atelier-research');self.d['invocation']['activity']='planning';self.d['permissions']['grant']='planning_only';self.assertEqual([],self.check(True))
    def test_planning_constructor_does_not_require_construction_grant(self):
        self.executed();self.select('design-specialist-skills','agent_skill');self.d['invocation']['activity']='planning';self.d['permissions']['grant']='planning_only';self.assertEqual([],self.check(True))
    def test_actual_activity_and_grant_matrix(self):
        for activity,selector,kind in [('planning','app-atelier-research','app'),('skill_construction','design-specialist-skills','agent_skill'),('product_execution','chatbot-atelier-build','chatbot')]:
            for grant in ('planning_only','construction_only','component_execution'):
                with self.subTest(activity=activity,grant=grant):
                    self.executed();self.select(selector,kind);self.d['invocation']['activity']=activity;self.d['permissions']['grant']=grant
                    self.assertEqual(grant in c.ACTIVITY_GRANTS[activity],not self.check(True))
    def test_embedded_construction_cannot_bypass_construction_grant(self):
        self.d.update(component_kind='agent_skill',status='executed');self.d['invocation'].update(selector='design-specialist-skills',activity='skill_construction',availability='unavailable',status='blocked',resolution=None);self.d['orchestrator_chain'][-1]='design-specialist-skills';self.d['fallback']=dict(mode='embedded_method',reason='missing constructor',owner='factory',consumer='child',acceptance='same contract',method=self.file('contract.md'));self.d['deliverables']=[self.file('output.md')];self.d['evidence']=[dict(self.file('output.md'),id='E1',claim='constructed',actor='factory',method='embedded',scope='P1')];self.assertTrue(any('does not authorize skill construction' in e for e in self.check()))
    def test_ready_construction_requires_grant_but_draft_proposal_does_not(self):
        self.select('design-specialist-skills','agent_skill');self.d['invocation']['activity']='skill_construction';self.assertEqual([],self.check());self.assertTrue(any('does not authorize skill construction' in e for e in self.check(True)))


if __name__=='__main__':unittest.main()
