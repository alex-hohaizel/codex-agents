"""Negative controls for chatbot formal-contract consistency and readiness."""
import copy
import unittest
from check_chat_contract import validate, brief_hash, attempt_hash
from test_platform_adapter import fixture as adapter_fixture


def specified():
    return {
        'schema_version': 'chatbot.blueprint/3',
        'brief': {'id': 'B1', 'version': '1', 'user_intent': 'Store a scoped note', 'audiences': ['user1'], 'platforms': ['web']},
        'platform_adapters': [dict(adapter_fixture(),id='AD1')],
        'applicability': [{'id': 'notes', 'state': 'active', 'reason': 'Explicit user request'}],
        'requirements': [{'id': 'R1', 'intent': 'Saved note is private', 'owner': 'data', 'acceptance': 'Own note returned', 'negative_probe': 'Other actor cannot read'}],
        'systems': [{'id': 'notes', 'owner': 'data', 'requirement_ids': ['R1'], 'inputs': ['text'], 'outputs': ['noteId'], 'rules': [{'id': 'save', 'algorithm': 'validate actor; persist scoped note', 'types': ['actorId:string', 'text:string'], 'order': ['authorize', 'commit']}], 'failure': ['reject wrong actor'], 'acceptance_vectors': ['own succeeds; wrong rejected']}],
        'interactions': [],
        'journeys': [{'id': 'J1', 'owner': 'product', 'requirement_ids': ['R1'], 'trigger': 'save note', 'audience': ['user1'], 'outcome': 'scoped note stored', 'delivery': 'confirmed note id', 'recovery': 'dedup retry', 'system_ids': ['notes'], 'adapter_ids':['AD1']}],
        'operations': [{'id': 'O1', 'owner': 'data', 'requirement_ids': ['R1'], 'inputs': ['scope', 'text'], 'outputs': ['noteId'], 'consumer': 'journey', 'capability_status': 'specified', 'recipe_ids': ['P1']}],
        'recipes': [{'id': 'P1', 'owner': 'data', 'requirement_ids': ['R1'], 'operation_ids': ['O1'], 'steps': ['authorize', 'commit', 'confirm'], 'checks': ['wrong actor rejected'], 'stop': 'failed auth', 'consumer': 'O1'}],
        'attempts': [], 'evidence': [],
        'completion': {'maturity': 'specified', 'unknowns': []}
    }


def integrated():
    """Synthetic linked declarations only, not proof a provider or product ran."""
    d = specified()
    d['completion']['maturity'] = 'integrated'
    d['operations'][0]['capability_status'] = 'exercised'
    adapter = d['platform_adapters'][0]
    adapter['maturity'] = 'exercised'
    adapter['capabilities'][0].update(status='exercised', evidence_ids=['AE1'])
    adapter['evidence'] = [{'id': 'AE1', 'result': 'pass', 'environment': adapter['environment'],
                            'capability_ids': ['C1'], 'artifact': 'synthetic-adapter.json', 'sha256': 'a' * 64}]
    d['journeys'][0].update(operation_ids=['O1'], attempt_ids=['A1'], evidence_ids=['E1'], verification='passed')
    d['attempts'] = [{'id': 'A1', 'operation_ids': ['O1'], 'recipe_ids': ['P1'],
                      'actual_run_id': 'SYNTHETIC-A1', 'input_snapshot': {'hash': 'a' * 64},
                      'effective_parameters': {'scope': 'synthetic'}, 'result': 'passed',
                      'subject': {'brief_id': d['brief']['id'], 'brief_version': d['brief']['version'],
                                  'brief_sha256': brief_hash(d['brief'])}}]
    d['evidence'] = [{'id': 'E1', 'kind': 'execution', 'artifact': 'synthetic-output.log',
                      'sha256': 'b' * 64, 'procedure': 'synthetic consistency probe',
                      'result': 'passed', 'limitations': ['SYNTHETIC; no actual product or provider run'],
                      'attempt_ids': ['A1'], 'attempt_sha256s': {'A1': attempt_hash(d['attempts'][0])}}]
    return d


class FormalContractTests(unittest.TestCase):
    def assert_rejects(self, record, fragment):
        self.assertTrue(any(fragment in e for e in validate(record)), validate(record))

    def test_valid_spec_does_not_need_fake_execution(self):
        self.assertEqual(validate(specified()), [])

    def test_unknown_system_blocks_specified(self):
        d = specified(); d['applicability'][0]['state'] = 'unknown'
        self.assert_rejects(d, 'unknown applicability')

    def test_active_system_missing_is_not_omission(self):
        d = specified(); d['systems'] = []
        self.assert_rejects(d, 'active system missing')

    def test_dangling_requirement_rejected(self):
        d = specified(); d['systems'][0]['requirement_ids'] = ['MISSING']
        self.assert_rejects(d, 'dangling requirement_ids')

    def test_duplicate_id_rejected(self):
        d = specified(); d['operations'].append(copy.deepcopy(d['operations'][0]))
        self.assert_rejects(d, 'duplicate id')

    def test_untyped_algorithm_rejected(self):
        d = specified(); del d['systems'][0]['rules'][0]['types']
        self.assert_rejects(d, 'rule requires')

    def test_interaction_requires_two_distinct_systems(self):
        d = specified(); d['interactions'] = [{'id': 'I1', 'system_ids': ['notes', 'notes']}]
        self.assert_rejects(d, 'two distinct systems')

    def test_missing_output_consumer_rejected(self):
        d = specified(); d['operations'][0]['consumer'] = ''
        self.assert_rejects(d, 'missing consumer')

    def test_integrated_cannot_promote_unexecuted_spec(self):
        d = specified(); d['completion']['maturity'] = 'integrated'
        self.assert_rejects(d, 'actual attempts and evidence')

    def test_live_evidence_requires_observation_reference(self):
        d = specified(); d['evidence'] = [{'id': 'E1', 'kind': 'live_provider', 'artifact': 'receipt.json', 'sha256': 'a' * 64, 'procedure': 'readback', 'result': 'accepted', 'limitations': []}]
        self.assert_rejects(d, 'actual observation reference')

    def test_actual_attempt_cannot_omit_effective_parameters(self):
        d = specified(); d['attempts'] = [{'id': 'A1', 'operation_ids': ['O1'], 'recipe_ids': ['P1'], 'actual_run_id': 'run1', 'input_snapshot': {'hash': 'a' * 64}, 'result': 'passed'}]
        self.assert_rejects(d, 'actual effective_parameters')

    def test_unsupported_schema_rejected(self):
        d = specified(); d['schema_version'] = 'chatbot.blueprint/2'
        self.assert_rejects(d, 'unsupported record format')

    def test_selected_channel_requires_adapter_contract(self):
        d=specified();d['platform_adapters']=[]
        self.assert_rejects(d,'every selected platform')

    def test_journey_requires_adapter_binding(self):
        d=specified();d['journeys'][0].pop('adapter_ids')
        self.assert_rejects(d,'selected adapter_ids')

    def test_ambiguous_selected_channel_rejected(self):
        d=specified();d['brief']['platforms']=['смак']
        self.assert_rejects(d,'explicit unique')

    def test_old_blueprint_format_rejected(self):
        d=specified();d['schema_version']='chatbot.blueprint/2'
        self.assert_rejects(d,'unsupported record format')

    def test_malformed_rows_give_diagnostics(self):
        d = specified(); d['systems'] = ['broken']; d['operations'] = None
        self.assertTrue(validate(d))

    def test_integrated_consistent_links_pass_structure_only(self):
        self.assertEqual(validate(integrated()), [])

    def test_failed_or_unknown_current_attempt_cannot_be_integrated(self):
        for status in ('failed', 'unknown', 'cancelled', 'uncertain', 'pending', 'running'):
            with self.subTest(status=status):
                d = integrated(); d['attempts'][0]['result'] = status
                self.assert_rejects(d, 'linked attempt not passed')

    def test_failed_evidence_cannot_be_overridden_by_journey_pass(self):
        d = integrated(); d['evidence'][0]['result'] = 'failed'
        self.assert_rejects(d, 'linked evidence not passed')

    def test_old_failure_history_does_not_block_successful_current_attempt(self):
        d = integrated(); old = copy.deepcopy(d['attempts'][0]); old.update(id='OLD', result='failed')
        d['attempts'].append(old)
        self.assertEqual(validate(d), [])

    def test_wrong_brief_subject_and_changed_intent_reject_old_proof(self):
        for mutate in ('id', 'version', 'user_intent'):
            with self.subTest(field=mutate):
                d = integrated(); d['brief'][mutate] += '-changed'
                self.assert_rejects(d, 'subject differs from current brief')

    def test_integrated_needs_explicit_current_operation_scope(self):
        d = integrated(); d['journeys'][0].pop('operation_ids')
        self.assert_rejects(d, 'explicit operation_ids')

    def test_evidence_must_bind_actual_journey_attempts(self):
        d = integrated(); d['evidence'][0].pop('attempt_ids')
        self.assert_rejects(d, 'evidence not bound to journey attempts')

    def test_unrelated_recipe_or_evidence_cannot_prove_operation(self):
        d = integrated(); d['recipes'][0]['operation_ids'] = []
        self.assert_rejects(d, 'operation/recipe scope mismatch')

    def test_source_or_human_observation_does_not_prove_executed_integration(self):
        for kind in ('source', 'human'):
            with self.subTest(kind=kind):
                d = integrated(); d['evidence'][0].update(kind=kind, actual_observation_ref='synthetic-observation')
                self.assert_rejects(d, 'lack successful linked execution evidence')

    def test_integrated_operation_needs_exercised_capability(self):
        d = integrated(); d['operations'][0]['capability_status'] = 'specified'
        self.assert_rejects(d, 'capability not exercised')

    def test_changed_attempt_inputs_cannot_reuse_previous_proof(self):
        d = integrated(); d['attempts'][0]['input_snapshot']['hash'] = 'c' * 64
        self.assert_rejects(d, 'attempt snapshot differs')

    def test_parameterless_operation_records_empty_actual_parameter_object(self):
        d = integrated(); d['attempts'][0]['effective_parameters'] = {}
        d['evidence'][0]['attempt_sha256s']['A1'] = attempt_hash(d['attempts'][0])
        self.assertEqual(validate(d), [])

    def test_rule_lists_are_typed_and_unique(self):
        for field, value in [('rules', 'free prose'), ('types', 'string'), ('order', 17)]:
            with self.subTest(field=field):
                d = specified()
                if field == 'rules': d['systems'][0][field] = value
                else: d['systems'][0]['rules'][0][field] = value
                self.assertTrue(validate(d))
        d = specified(); d['systems'][0]['rules'].append(copy.deepcopy(d['systems'][0]['rules'][0]))
        self.assert_rejects(d, 'duplicate rule id')

    def test_unknown_capability_or_result_is_rejected(self):
        d = specified(); d['operations'][0]['capability_status'] = 'banana'
        self.assert_rejects(d, 'invalid capability_status')
        d = integrated(); d['attempts'][0]['result'] = 'banana'
        self.assert_rejects(d, 'invalid attempt result')

    def test_orphan_requirement_must_have_full_design_chain(self):
        d = specified(); extra = copy.deepcopy(d['requirements'][0]); extra['id'] = 'R2'; d['requirements'].append(extra)
        for category in ('systems', 'journeys', 'operations', 'recipes'):
            self.assert_rejects(d, 'R2 has no ' + category + ' coverage')

    def test_explicit_deferred_requirement_can_be_outside_claimed_scope(self):
        d = specified(); extra = copy.deepcopy(d['requirements'][0]); extra.update(id='R2', state='deferred',
            scope_decision_ref='SYNTHETIC-owner-scope', reason='separate accepted future milestone', due_gate='next accepted milestone')
        d['requirements'].append(extra)
        self.assertEqual(validate(d), [])
        extra.pop('scope_decision_ref'); self.assert_rejects(d, 'explicit scope decision')

    def test_malformed_nested_payloads_return_diagnostics(self):
        cases = [('platforms', [{}]), ('requirement_ids', [{}]), ('result', {})]
        for field, value in cases:
            with self.subTest(field=field):
                d = integrated()
                if field == 'platforms': d['brief'][field] = value
                elif field == 'requirement_ids': d['journeys'][0][field] = value
                else: d['attempts'][0][field] = value
                self.assertTrue(validate(d))


if __name__ == '__main__':
    unittest.main()
