"""Synthetic planning records; neither approval nor executed evidence."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import blueprint as b
from test_blueprint import fixture


def fixture2():
    d = fixture()
    d['schema_version'] = 'skill.blueprint/2'
    d['toolkit_version'] = '2.2.0'
    d['specialization_depth'] = {
        'maturity': 'specification',
        'applicability': [{'id': 'A1', 'criterion_id': 'accuracy', 'status': 'applicable', 'reason': 'requested factual report', 'owner_domain': 'analysis', 'due_gate': 'analysis acceptance'}],
        'source_methods': [{'id':'S1', 'source_ref':'synthetic-source', 'claim':'facts need attributable support', 'applicability':'factual report', 'method':'trace assertions to supplied material', 'verification_due':'before claim', 'limits':'does not prove source truth'}],
        'domain_contracts': [{'id':'C1', 'criterion_ids':['accuracy'], 'owner_domain':'analysis', 'typed_inputs':{'source':'UTF8 text'}, 'typed_outputs':{'report':'UTF8 markdown'}, 'rules':'quote has exact source locator; inference is labeled', 'state_policy':'single report revision; no runtime state', 'failure_recovery':'missing source becomes unresolved, not fact', 'invariants':['all factual claims attributable'], 'consumer':'owner', 'source_method_ids':['S1']}],
        'operations': [{'id':'O1', 'criterion_ids':['accuracy'], 'contract_ids':['C1'], 'owner_domain':'analysis', 'consumer':'owner', 'capability_plan':'read supplied source text then create Markdown', 'recipe_plan':'read→extract→support assertions→independent review', 'transformation_checks':['source meaning unchanged'], 'evidence_due':'before report accepted', 'permissions':'read supplied materials; write report', 'budget':'bounded source set', 'stop_condition':'unsupported material marked gap'}],
        'acceptance_cases': [{'id':'T1', 'criterion_ids':['accuracy'], 'preconditions':'supplied two factual notes', 'action':'write report', 'expected':'two supported assertions and explicit unknown', 'negative_case':'unsupported assertion rejected', 'proof_kind':'semantic factual review', 'review_policy':'independent reviewer for material claim'}],
        'child_contracts': [{'id':'CH1', 'stage_id':'analyze', 'criterion_ids':['accuracy'], 'input_contract':'supplied source text', 'output_contract':'attributable report plus gaps', 'consumer':'owner', 'capability_recipe_policy':'verify actual IO operation before relying', 'evidence_policy':'supported assertion; no deployment claims', 'inheritance_check':'requirement IDs all assigned and exact constraints preserved', 'checkpoint_handoff':'actual files plus current gap and next action', 'independence':'author differs from reviewer for material claim'}],
        'change_policy': {'dependency_invalidation':'changed source stales dependent assertions', 'migration':'new file preserving original', 'carry_forward':'only unchanged semantic inputs'},
        'recovery_policy': {'checkpoint':'actual report revision and unresolved sources', 'effect_reconciliation':'no external effects in this report scope', 'repair_budget':'two repeated failures trigger new diagnosis', 'stop_condition':'requested scope delivered or explicit blocker'}}
    return d


class BlueprintV2Tests(unittest.TestCase):
    def setUp(self):
        self.d = fixture2()
    def approve(self):
        self.d['approval']={'actor':'user','decision':'approve','proposal_hash':b.proposal_hash(self.d),'proposal_version':self.d['version'],'verbatim':'SYNTHETIC','source':'synthetic transcript','timestamp':'2026-11-03','scope':'fixture only'}
    def test_v2_plan_accepts_without_forging_execution(self):
        self.assertEqual(b.check(self.d), [])
        self.assertTrue(b.check(self.d, approved=True))
    def test_v2_structural_approval(self):
        self.approve()
        self.assertEqual(b.check(self.d, approved=True), [])
    def add_stage(self):
        self.d['stages'].append(dict(copy.deepcopy(self.d['stages'][0]), id='review', name='review', depends_on=['analyze']))
        child = copy.deepcopy(self.d['specialization_depth']['child_contracts'][0])
        child.update(id='CH2', stage_id='review')
        self.d['specialization_depth']['child_contracts'].append(child)
    def test_single_skill_can_own_multiple_dependent_phases(self):
        self.add_stage()
        self.assertEqual(b.check(self.d), [])
        self.approve()
        self.assertEqual(b.check(self.d, approved=True), [])
    def test_single_explicit_module_can_own_multiple_phases(self):
        self.add_stage()
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['analyze', 'review']}]
        self.assertEqual(b.check(self.d), [])
    def test_family_can_share_a_single_phase_with_explicit_modules(self):
        self.d['architecture']['kind'] = 'family'
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['analyze']}, {'name': 'review-agent', 'stage_ids': ['analyze']}]
        self.assertEqual(b.check(self.d), [])
    def test_family_cannot_infer_modules_from_phase_count(self):
        self.add_stage();self.d['architecture']['kind'] = 'family'
        self.assertTrue(any('explicit installable modules' in x for x in b.check(self.d)))
    def test_module_assignment_covers_actual_phase_graph(self):
        self.add_stage()
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['analyze']}]
        self.assertTrue(any('every workflow stage' in x for x in b.check(self.d)))
    def test_module_cannot_claim_unknown_phase(self):
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['not-a-phase']}]
        self.assertTrue(any('unknown or duplicate stages' in x for x in b.check(self.d)))
    def test_module_names_must_be_unique(self):
        self.d['architecture']['kind'] = 'family'
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['analyze']}, {'name': 'report-agent', 'stage_ids': ['analyze']}]
        self.assertTrue(any('unique portable' in x for x in b.check(self.d)))
    def test_single_module_count_is_independent_from_phase_count(self):
        self.d['architecture']['modules'] = [{'name': 'report-agent', 'stage_ids': ['analyze']}, {'name': 'review-agent', 'stage_ids': ['analyze']}]
        self.assertTrue(any('module count' in x for x in b.check(self.d)))
    def test_previous_output_format_is_rejected(self):
        old=fixture();old['schema_version']='skill.blueprint/1'
        self.assertTrue(b.check(old))
        self.assertTrue(b.check(old, approved=True))
    def test_missing_consumer(self):
        del self.d['specialization_depth']['operations'][0]['consumer']
        self.assertTrue(b.check(self.d))
    def test_broken_contract_ref(self):
        self.d['specialization_depth']['operations'][0]['contract_ids']=['missing']
        self.assertTrue(b.check(self.d))
    def test_uncovered_requirement(self):
        self.d['specialization_depth']['acceptance_cases']=[]
        self.assertTrue(b.check(self.d))
    def test_missing_child_inheritance(self):
        self.d['specialization_depth']['child_contracts']=[]
        self.assertTrue(b.check(self.d))
    def test_n_a_requires_explicit_domain_decision(self):
        self.d['specialization_depth']['applicability'][0]['status']='absent_by_design'
        self.assertTrue(b.check(self.d))
    def test_blocked_capability_does_not_pass_creation(self):
        self.d['specialization_depth']['applicability'][0]['status']='blocked'
        self.approve()
        self.assertTrue(b.check(self.d, approved=True))
    def test_sketch_does_not_pass_creation(self):
        self.d['specialization_depth']['maturity']='sketch'
        self.approve()
        self.assertTrue(b.check(self.d, approved=True))
    def test_changed_contract_invalidates_approval(self):
        self.approve()
        self.d['specialization_depth']['domain_contracts'][0]['rules']='different result'
        self.assertTrue(b.check(self.d, approved=True))
    def test_unknown_output_format_is_rejected(self):
        self.d['schema_version']='unknown'
        self.assertTrue(b.check(self.d))
    def test_malformed_contract_reference_fails_without_crash(self):
        self.d['specialization_depth']['operations'][0]['contract_ids']=[{'invalid':'reference'}]
        self.assertTrue(b.check(self.d))
    def test_malformed_current_brief_fails_without_crash(self):
        d = fixture()
        d['brief'] = []
        self.assertTrue(b.check(d))
    def test_removed_migration_command_rejects_without_changing_source(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as t:
            src=Path(t)/'previous.json'; original=json.dumps(dict(fixture(),schema_version='skill.blueprint/1'));src.write_text(original)
            dst=Path(t)/'current.json'
            result=subprocess.run([sys.executable,str(Path(b.__file__)),'migrate',str(src),'--output',str(dst)],capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertEqual(src.read_text(),original);self.assertFalse(dst.exists())
    def test_hash_cli_rejects_previous_format(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as t:
            src=Path(t)/'previous.json';src.write_text(json.dumps(dict(fixture(),schema_version='skill.blueprint/1')))
            result=subprocess.run([sys.executable,str(Path(b.__file__)),'hash',str(src)],capture_output=True)
            self.assertNotEqual(result.returncode,0)


if __name__ == '__main__':
    unittest.main()
