"""Synthetic boundary checks; none of these fixtures are real models or media proof."""
import copy
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'standards/ai_production.py'
spec = importlib.util.spec_from_file_location('ai_production', HELPER)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


class ProductionArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.files = {'proof.txt': b'SYNTHETIC receipt: not human, model, rights or consumer proof.\n',
                      'master.svg': b'<svg xmlns="http://www.w3.org/2000/svg"/>',
                      'export.png': b'SYNTHETIC FILE; NEVER RENDERED',
                      'tokenizer.json': b'{"synthetic":true}',
                      'adapter.safetensors': b'SYNTHETIC ADAPTER; NEVER LOADED',
                      'signature.json': b'{"synthetic_signature":true}',
                      'weights.safetensors': b'SYNTHETIC MODEL FILE; NEVER LOADED'}
        for name, raw in self.files.items():
            (self.root / name).write_bytes(raw)
        self.rows = self.fixture()

    def pin(self, path):
        data = (self.root / path).read_bytes()
        return {'path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

    def record(self, kind, ident, payload, paths=('proof.txt',)):
        return {'schema_version': A.VERSION, 'kind': kind, 'id': ident,
                'project_id': 'SYNTHETIC-PROJECT', 'project_root': str(self.root),
                'owner': 'fixture-owner', 'inputs': [self.pin(p) for p in paths], 'payload': payload}

    def fixture(self):
        observation = lambda proof: {'proof_type': proof, 'actor': 'reviewer',
                                    'procedure': 'Synthetic boundary observation, not actual use',
                                    'environment': 'test fixture', 'evidence_ref': 'proof.txt'}
        times = ['2026-01-01T00:00:00Z', '2026-01-03T00:00:00Z', '2026-01-05T00:00:00Z']
        rows = [{'record_id': ident, 'group_id': 'group-' + ident,
                 'prediction_at': at, 'features_available_at': at, 'label_available_at': at}
                for ident, at in zip(('r1', 'r2', 'r3'), times)]
        money = lambda value: {'currency': 'USD', 'amount': value}
        records = [
            self.record('SourceContract', 'S', {
                'locator': 'https://example.invalid/fixture', 'acquisition': 'api',
                'rights_ref': 'proof.txt', 'privacy_ref': 'proof.txt', 'schema_ref': 'proof.txt',
                'consumer': 'Synthetic boundary test only', 'rate_limit': {'requests': 1, 'period_seconds': 60},
                'bounds': {'requests': 1, 'bytes': 1024, 'retries': 0}}),
            self.record('DatasetManifest', 'D', {
                'source_ids': ['S'], 'record_ids': ['r1', 'r2', 'r3'], 'dedup_key': 'source ID',
                'transform_ref': 'proof.txt', 'counts': {'received': 3, 'accepted': 3,
                    'duplicates': 0, 'quarantined': 0, 'excluded': 0}, 'quarantine': [],
                'coverage': {'scope': 'Three fixture rows', 'status': 'complete',
                             'expected': 3, 'observed': 3, 'gaps': [], 'next_cursor': None}}),
            self.record('SplitManifest', 'T', {
                'dataset_id': 'D', 'strategy': 'group_time',
                'partitions': {'train': ['r1'], 'validation': ['r2'], 'test': ['r3']},
                'excluded_ids': [], 'rows': rows, 'embargo_seconds': 3600,
                'label_cutoffs': {'train': '2026-01-02T00:00:00Z',
                                  'validation': '2026-01-04T00:00:00Z', 'test': '2026-01-06T00:00:00Z'}}),
            self.record('FeatureManifest', 'F', {
                'dataset_id': 'D', 'split_id': 'T', 'fit_record_ids': ['r1'],
                'features': [{'name': 'prelaunch_feature', 'source_ref': 'proof.txt',
                              'availability': [{'record_id': row['record_id'], 'available_at': row['prediction_at']}
                                               for row in rows]}]}),
            self.record('PredictionContract', 'P', {
                'decision': 'Synthetic CPA guard only; no actual prediction', 'target': 'CPA',
                'unit': 'USD/acquisition', 'horizon_seconds': 604800, 'kind': 'cpa',
                'feature_manifest_id': 'F', 'forbidden_features': ['postlaunch_spend'],
                'zero_denominator_policy': 'abstain', 'currency': 'USD', 'attribution_window': '7d'}),
            self.record('WorkflowRun', 'W', {
                'recipe_ref': 'proof.txt', 'status': 'completed',
                'nodes': [{'id': 'N', 'status': 'completed', 'completion_attempt_id': 'A',
                           'attempts': [{'id': 'A', 'status': 'completed', 'receipt_ref': 'proof.txt'}]}],
                'effects': [{'id': 'E', 'status': 'known_success',
                             'retry_requested': False, 'receipt_ref': 'proof.txt'}]}),
            self.record('EvaluationPlan', 'EP', {
                'case_ids': ['CASE'], 'must_case_ids': ['CASE'], 'author': 'author',
                'requires_independent': True, 'baseline_ref': 'proof.txt', 'candidate_ref': 'proof.txt',
                'rubric_ref': 'proof.txt', 'required_proofs': ['source', 'consumer', 'serving']}),
            self.record('EvaluationReport', 'ER', {
                'plan_id': 'EP', 'reviewer': 'reviewer', 'conclusion': 'recorded-pass',
                'results': [{'case_id': 'CASE', 'verdict': 'pass',
                             'observations': [observation('source'), observation('consumer'), observation('serving')]}]},
                        ('proof.txt', 'weights.safetensors', 'tokenizer.json', 'adapter.safetensors',
                         'signature.json', 'master.svg', 'export.png')),
            self.record('TrainingRecipe', 'TR', {
                'dataset_id': 'D', 'split_id': 'T', 'method': 'lora',
                'base_model': {'id': 'fixture', 'revision': 'base-v1', 'license_ref': 'proof.txt'},
                'tokenizer': {'id': 'fixture', 'revision': 'token-v1', 'template_ref': 'proof.txt'},
                'measured_gap_ref': 'proof.txt', 'environment_ref': 'proof.txt',
                'budget': {'max_seconds': 1, 'max_bytes': 1024, 'max_cost': money('1')},
                'adapter': {'rank': 4, 'target_modules': ['fixture'], 'config_ref': 'proof.txt'}}),
            self.record('ModelBundle', 'M', {
                'recipe_id': 'TR', 'base_revision': 'base-v1', 'tokenizer_revision': 'token-v1',
                'format': 'safetensors', 'loader_review_ref': 'proof.txt', 'remote_code': False,
                'files': [self.pin('weights.safetensors'), self.pin('tokenizer.json'),
                          self.pin('adapter.safetensors'), self.pin('signature.json')],
                'weights_ref': 'weights.safetensors', 'tokenizer_ref': 'tokenizer.json',
                'signature_ref': 'signature.json',
                'evaluation_report_id': 'ER', 'serving_proof_ref': 'proof.txt',
                'adapter_ref': 'adapter.safetensors'},
                        ('proof.txt', 'weights.safetensors', 'tokenizer.json', 'adapter.safetensors', 'signature.json')),
            self.record('BatchPlan', 'BP', {
                'recipe_ref': 'proof.txt', 'budget': money('1'),
                'items': [{'item_id': 'asset', 'variant': 'hero', 'master_ref': 'master.svg', 'consumer': 'fixture'},
                          {'item_id': 'icon', 'variant': 'primary', 'master_ref': 'master.svg', 'consumer': 'fixture'}]},
                        ('proof.txt', 'master.svg')),
            self.record('ItemManifest', 'I', {
                'plan_id': 'BP', 'item_id': 'asset', 'variant': 'hero', 'master_ref': 'master.svg',
                'outputs': [self.pin('export.png')], 'verdict': 'accepted',
                'review_ref': 'proof.txt', 'consumer_proof_ref': 'proof.txt',
                'evaluation_report_id': 'ER'}, ('proof.txt', 'master.svg')),
            self.record('GenerationBatch', 'GB', {
                'plan_id': 'BP', 'status': 'closed', 'overheads': [],
                'attempts': [
                    {'id': 'retry-0', 'item_id': 'asset', 'variant': 'hero', 'status': 'failed', 'retry_requested': False, 'cost': money('0.1')},
                    {'id': 'rejected', 'item_id': 'icon', 'variant': 'primary', 'status': 'rejected', 'retry_requested': False, 'cost': money('0.2')},
                    {'id': 'retry-1', 'item_id': 'asset', 'variant': 'hero', 'status': 'succeeded',
                     'retry_requested': False, 'cost': money('0.5'), 'receipt_ref': 'proof.txt', 'output_manifest_id': 'I'}],
                'outcomes': [{'item_id': 'icon', 'variant': 'primary', 'status': 'rejected'},
                             {'item_id': 'asset', 'variant': 'hero', 'status': 'accepted', 'manifest_id': 'I'}]}),
        ]
        plan = next(row for row in records if row['kind'] == 'EvaluationPlan')
        report = next(row for row in records if row['kind'] == 'EvaluationReport')
        report['payload']['plan_sha256'] = A.record_sha256(plan)
        return records

    def row(self, kind):
        return next(row['payload'] for row in self.rows if row['kind'] == kind)

    def check(self):
        return A.check_records(self.rows, self.root)

    def test_all_thirteen_types_and_declared_guards_do_not_certify_actual_quality(self):
        result = self.check()
        self.assertEqual(result['records_checked'], 13)
        self.assertEqual({row['kind'] for row in result['checks']}, set(A.PAYLOADS))
        for key in ('quality_certified', 'authority_authenticated', 'actual_execution_authenticated'):
            self.assertIs(result[key], False)

    def test_schema_file_matches_emitted_contract_exactly(self):
        saved = json.loads((ROOT / 'standards/ai-production.schema.json').read_text())
        self.assertEqual(saved, A.schema_document())
        self.assertEqual(set(saved['$defs']), set(A.PAYLOADS))

    def test_only_applicable_record_needed_and_missing_dependency_is_not_silently_ignored(self):
        self.assertTrue(A.check_records(self.rows[:1], self.root)['ok'])
        with self.assertRaisesRegex(A.ArtifactError, 'missing referenced SourceContract'):
            A.check_records(self.rows[1:2], self.root)

    def test_cross_project_or_wrong_canonical_root_rejected(self):
        for key, value in (('project_id', 'OTHER'), ('project_root', str(self.root / 'other'))):
            rows = copy.deepcopy(self.rows)
            rows[1][key] = value
            with self.assertRaises(A.ArtifactError):
                A.check_records(rows, self.root)

    def test_changed_or_missing_source_pin_rejected(self):
        (self.root / 'proof.txt').write_bytes(b'changed')
        with self.assertRaisesRegex(A.ArtifactError, 'drift'):
            self.check()
        (self.root / 'proof.txt').unlink()
        with self.assertRaisesRegex(A.ArtifactError, 'missing'):
            self.check()

    def test_paths_links_credential_names_and_pin_budget_are_bounded(self):
        for ref in ('../outside', '/absolute', 'a/../proof.txt', '.env', '.aws/key'):
            with self.subTest(ref=ref), self.assertRaises(A.ArtifactError):
                A.safe_file(self.root, ref)
        (self.root / 'link').symlink_to(self.root / 'proof.txt')
        with self.assertRaisesRegex(A.ArtifactError, 'linked'):
            A.safe_file(self.root, 'link')
        with self.assertRaisesRegex(A.ArtifactError, 'budget'):
            A.check_records(self.rows, self.root, max_pin_bytes=1)

    def test_reference_cannot_claim_unpinned_consumed_source(self):
        self.row('SourceContract')['rights_ref'] = 'undeclared.txt'
        with self.assertRaisesRegex(A.ArtifactError, 'no consumed input pin'):
            self.check()

    def test_dataset_denominator_quarantine_and_remaining_page_cannot_fake_complete(self):
        cases = [({'received': 4}, None), ({'quarantined': 1}, None), ({}, 'more-pages')]
        for counts, cursor in cases:
            rows = copy.deepcopy(self.rows)
            p = next(row['payload'] for row in rows if row['kind'] == 'DatasetManifest')
            p['counts'].update(counts)
            p['coverage']['next_cursor'] = cursor
            with self.subTest(counts=counts, cursor=cursor), self.assertRaises(A.ArtifactError):
                A.check_records(rows, self.root)

    def test_partial_collection_preserves_counts_and_gaps(self):
        p = self.row('DatasetManifest')
        p['coverage'].update(status='partial', expected=7, gaps=['four source rows unavailable'], next_cursor='cursor')
        self.assertTrue(self.check()['ok'])
        self.assertEqual(p['counts']['accepted'], 3)

    def test_record_group_or_time_split_leakage_rejected(self):
        for change in ('membership', 'group', 'chronology', 'label-cutoff'):
            rows = copy.deepcopy(self.rows)
            p = next(row['payload'] for row in rows if row['kind'] == 'SplitManifest')
            if change == 'membership':
                p['partitions']['test'] = ['r1']
            elif change == 'group':
                p['rows'][2]['group_id'] = p['rows'][0]['group_id']
            elif change == 'chronology':
                p['rows'][2]['prediction_at'] = p['rows'][0]['prediction_at']
            else:
                p['rows'][0]['label_available_at'] = '2026-02-01T00:00:00Z'
            with self.subTest(change=change), self.assertRaises(A.ArtifactError):
                A.check_records(rows, self.root)

    def test_future_feature_availability_or_test_fit_rejected(self):
        p = self.row('FeatureManifest')
        p['features'][0]['availability'][0]['available_at'] = '2027-01-01T00:00:00Z'
        with self.assertRaisesRegex(A.ArtifactError, 'prediction time'):
            self.check()
        p['features'][0]['availability'][0]['available_at'] = '2026-01-01T00:00:00Z'
        p['fit_record_ids'] = ['r1', 'r3']
        with self.assertRaisesRegex(A.ArtifactError, 'non-training'):
            self.check()

    def test_naive_timestamp_and_train_label_after_later_prediction_rejected(self):
        p = self.row('SplitManifest')
        p['rows'][0]['prediction_at'] = '2026-01-01T00:00:00'
        with self.assertRaisesRegex(A.ArtifactError, 'timezone'):
            self.check()
        p['rows'][0]['prediction_at'] += 'Z'
        p['label_cutoffs']['train'] = '2026-01-04T00:00:00Z'
        with self.assertRaisesRegex(A.ArtifactError, 'later prediction'):
            self.check()

    def test_empty_validation_still_checks_train_label_cutoff_before_test_prediction(self):
        p = self.row('SplitManifest')
        p['partitions']['validation'] = []
        p['excluded_ids'] = ['r2']
        p['label_cutoffs']['train'] = '2026-01-08T00:00:00Z'
        p['rows'][0]['label_available_at'] = '2026-01-07T00:00:00Z'
        with self.assertRaisesRegex(A.ArtifactError, 'later prediction'):
            self.check()

    def test_cpa_requires_zero_outcome_policy_and_forbids_postlaunch_feature(self):
        p = self.row('PredictionContract')
        p['zero_denominator_policy'] = 'not-applicable'
        with self.assertRaisesRegex(A.ArtifactError, 'CPA requires'):
            self.check()
        p['zero_denominator_policy'] = 'abstain'
        p['forbidden_features'].append('prelaunch_feature')
        with self.assertRaisesRegex(A.ArtifactError, 'post-outcome'):
            self.check()

    def test_unknown_workflow_effect_cannot_be_retried_or_hidden_by_completion(self):
        p = self.row('WorkflowRun')
        p['status'] = 'outcome_unknown'
        p['effects'][0].update(status='outcome_unknown', retry_requested=True)
        with self.assertRaisesRegex(A.ArtifactError, 'reconciled'):
            self.check()
        p['effects'][0]['retry_requested'] = False
        p['status'] = 'completed'
        with self.assertRaisesRegex(A.ArtifactError, 'unfinished/unknown'):
            self.check()

    def test_workflow_uses_explicit_completion_identity_not_array_order(self):
        p = self.row('WorkflowRun')
        p['nodes'][0]['attempts'].append({'id': 'older', 'status': 'failed', 'receipt_ref': 'proof.txt'})
        self.assertTrue(self.check()['ok'])
        p['nodes'][0]['completion_attempt_id'] = 'not-observed'
        with self.assertRaisesRegex(A.ArtifactError, 'explicit completed attempt'):
            self.check()

    def test_dispatched_or_successful_workflow_effect_cannot_request_retry(self):
        p = self.row('WorkflowRun')
        p['status'] = 'running'
        for status in ('planned', 'dispatched', 'known_success', 'outcome_unknown'):
            p['effects'][0].update(status=status, retry_requested=True)
            with self.subTest(status=status), self.assertRaisesRegex(A.ArtifactError, 'reconciled'):
                self.check()

    def test_known_failure_retry_requires_observed_receipt_and_pinned_bounded_policy(self):
        p = self.row('WorkflowRun')
        p['status'] = 'running'
        effect = p['effects'][0]
        effect.update(status='known_failure', retry_requested=True)
        with self.assertRaisesRegex(A.ArtifactError, 'safe policy'):
            self.check()
        effect['retry_policy'] = {'mode': 'known-failure-only', 'basis_ref': 'proof.txt',
                                  'retry_number': 1, 'max_retries': 1}
        self.assertTrue(self.check()['ok'])
        effect['retry_policy']['retry_number'] = 2
        with self.assertRaisesRegex(A.ArtifactError, 'safe policy'):
            self.check()

    def test_planned_work_does_not_need_fabricated_execution_receipts(self):
        p = self.row('WorkflowRun')
        p['status'] = 'planned'
        p['nodes'] = [{'id': 'N', 'status': 'planned', 'attempts': [{'id': 'future', 'status': 'planned'}]}]
        p['effects'] = [{'id': 'future-effect', 'status': 'planned', 'retry_requested': False}]
        self.assertFalse(self.check()['actual_execution_authenticated'])

    def test_eval_missing_case_proof_or_self_review_cannot_be_recorded_pass(self):
        for change in ('missing-case', 'missing-proof', 'self-review', 'unknown'):
            rows = copy.deepcopy(self.rows)
            p = next(row['payload'] for row in rows if row['kind'] == 'EvaluationReport')
            if change == 'missing-case':
                p['results'] = []
            elif change == 'missing-proof':
                p['results'][0]['observations'] = p['results'][0]['observations'][:1]
            elif change == 'self-review':
                p['reviewer'] = 'author'
            else:
                p['results'][0]['verdict'] = 'unknown'
            with self.subTest(change=change), self.assertRaises(A.ArtifactError):
                A.check_records(rows, self.root)

    def test_failed_or_unknown_model_evaluation_and_wrong_base_rejected(self):
        p = self.row('ModelBundle')
        p['base_revision'] = 'other-base'
        with self.assertRaisesRegex(A.ArtifactError, 'base/tokenizer'):
            self.check()
        p['base_revision'] = 'base-v1'
        self.row('EvaluationReport')['results'][0]['verdict'] = 'unknown'
        self.row('EvaluationReport')['conclusion'] = 'incomplete'
        with self.assertRaisesRegex(A.ArtifactError, 'evaluation has failed or missing'):
            self.check()

    def test_lora_config_and_untrusted_serialization_never_load(self):
        p = self.row('TrainingRecipe')
        del p['adapter']
        with self.assertRaisesRegex(A.ArtifactError, 'LoRA needs'):
            self.check()
        p['adapter'] = {'rank': 4, 'target_modules': ['q'], 'config_ref': 'proof.txt'}
        (self.root / 'model.pkl').write_bytes(b'never deserialized')
        self.row('ModelBundle')['files'].append(self.pin('model.pkl'))
        with self.assertRaisesRegex(A.ArtifactError, 'serialization'):
            self.check()

    def test_old_evaluation_cannot_be_rebound_to_new_model_or_media_bytes(self):
        report = next(row for row in self.rows if row['kind'] == 'EvaluationReport')
        for missing in ('weights.safetensors', 'tokenizer.json', 'adapter.safetensors',
                        'signature.json', 'export.png', 'master.svg'):
            original = report['inputs']
            report['inputs'] = [pin for pin in original if pin['path'] != missing]
            with self.subTest(missing=missing), self.assertRaisesRegex(A.ArtifactError, 'old evaluation'):
                self.check()
            report['inputs'] = original

    def test_adapter_and_signature_are_actual_delivered_bundle_members(self):
        bundle = self.row('ModelBundle')
        for omitted in ('adapter.safetensors', 'signature.json'):
            original = bundle['files']
            bundle['files'] = [pin for pin in original if pin['path'] != omitted]
            with self.subTest(omitted=omitted), self.assertRaisesRegex(A.ArtifactError, 'delivered adapter or signature'):
                self.check()
            bundle['files'] = original

    def test_nonempty_serving_ref_is_insufficient_without_matching_observation(self):
        report = self.row('EvaluationReport')
        report['results'][0]['observations'][-1]['proof_type'] = 'some-other-proof'
        self.row('EvaluationPlan')['required_proofs'] = ['source', 'consumer']
        report['plan_sha256'] = A.record_sha256(next(row for row in self.rows if row['kind'] == 'EvaluationPlan'))
        with self.assertRaisesRegex(A.ArtifactError, 'explicit serving observation'):
            self.check()

    def test_unchanged_report_cannot_rebind_replaced_plan_rubric_or_metadata(self):
        plan = next(row for row in self.rows if row['kind'] == 'EvaluationPlan')
        original = copy.deepcopy(plan)
        for mutation in ('rubric', 'candidate', 'baseline', 'owner'):
            plan.clear()
            plan.update(copy.deepcopy(original))
            if mutation == 'owner':
                plan['owner'] = 'replacement-owner'
            else:
                name = 'replacement-' + mutation + '.txt'
                (self.root / name).write_text('new current ' + mutation)
                plan['inputs'].append(self.pin(name))
                plan['payload'][mutation + '_ref'] = name
            with self.subTest(mutation=mutation), self.assertRaisesRegex(A.ArtifactError, 'plan content changed'):
                self.check()

    def test_even_refreshed_plan_digest_requires_all_current_plan_pins_in_report(self):
        plan = next(row for row in self.rows if row['kind'] == 'EvaluationPlan')
        report = next(row for row in self.rows if row['kind'] == 'EvaluationReport')
        (self.root / 'additional-context.txt').write_text('new native constraint')
        pin = self.pin('additional-context.txt')
        plan['inputs'].append(pin)
        report['payload']['plan_sha256'] = A.record_sha256(plan)
        with self.assertRaisesRegex(A.ArtifactError, 'all current plan input pins'):
            self.check()
        report['inputs'].append(pin)
        self.assertTrue(self.check()['ok'])

    def test_batch_cost_includes_retries_rejections_and_out_of_order_outcomes(self):
        result = self.check()['batch_summaries']['GB']
        self.assertEqual(result['known_cost'], '0.8')
        self.assertEqual(result['cost_per_accepted_item'], '0.8')
        self.assertEqual(result['requested_items'], 2)
        self.assertEqual(result['accepted_items'], 1)
        self.assertFalse(result['all_requested_delivered'])
        self.rows.reverse()
        self.row('GenerationBatch')['attempts'].reverse()
        self.assertEqual(self.check()['batch_summaries']['GB'], result)

    def test_batch_duplicate_missing_unplanned_ids_and_wrong_master_rejected(self):
        for change in ('duplicate', 'missing', 'unplanned', 'master'):
            rows = copy.deepcopy(self.rows)
            batch = next(row['payload'] for row in rows if row['kind'] == 'GenerationBatch')
            if change == 'duplicate':
                batch['outcomes'].append(batch['outcomes'][0])
            elif change == 'missing':
                batch['outcomes'].pop()
            elif change == 'unplanned':
                batch['attempts'][0]['variant'] = 'not-requested'
            else:
                next(row['payload'] for row in rows if row['kind'] == 'ItemManifest')['master_ref'] = 'proof.txt'
            with self.subTest(change=change), self.assertRaises(A.ArtifactError):
                A.check_records(rows, self.root)

    def test_unknown_batch_outcome_cost_is_not_zero_or_success(self):
        p = self.row('GenerationBatch')
        p['status'] = 'open'
        a = p['attempts'][0]
        a.update(status='outcome_unknown', retry_requested=False)
        del a['cost']
        p['outcomes'][1] = {'item_id': 'asset', 'variant': 'hero', 'status': 'outcome_unknown'}
        result = self.check()['batch_summaries']['GB']
        self.assertIsNone(result['cost_per_accepted_item'])
        self.assertFalse(result['declared_costs_complete'])
        a['retry_requested'] = True
        with self.assertRaisesRegex(A.ArtifactError, 'cannot be retried'):
            self.check()

    def test_dispatched_batch_retry_is_denied_even_with_zero_cost_and_open_run(self):
        p = self.row('GenerationBatch')
        p['status'] = 'open'
        p['attempts'].append({'id': 'inflight', 'item_id': 'asset', 'variant': 'hero',
                              'status': 'dispatched', 'retry_requested': True,
                              'cost': {'currency': 'USD', 'amount': '0'}})
        with self.assertRaisesRegex(A.ArtifactError, 'cannot be retried'):
            self.check()

    def test_failed_batch_retry_requires_safe_policy_and_remaining_bound(self):
        p = self.row('GenerationBatch')
        p['status'] = 'open'
        attempt = p['attempts'][0]
        attempt.update(retry_requested=True, receipt_ref='proof.txt')
        with self.assertRaisesRegex(A.ArtifactError, 'safe policy'):
            self.check()
        attempt['retry_policy'] = {'mode': 'known-failure-only', 'basis_ref': 'proof.txt',
                                   'retry_number': 1, 'max_retries': 1}
        self.assertTrue(self.check()['ok'])
        attempt['retry_policy']['retry_number'] = 2
        with self.assertRaisesRegex(A.ArtifactError, 'safe policy'):
            self.check()

    def test_cost_cap_currency_and_closed_unknown_cost_rejected(self):
        p = self.row('GenerationBatch')
        p['attempts'][0]['cost']['amount'] = '2'
        with self.assertRaisesRegex(A.ArtifactError, 'exceeds budget'):
            self.check()
        p['attempts'][0]['cost'] = {'currency': 'EUR', 'amount': '0.1'}
        with self.assertRaisesRegex(A.ArtifactError, 'currencies'):
            self.check()
        del p['attempts'][0]['cost']
        with self.assertRaisesRegex(A.ArtifactError, 'missing/unknown work or cost'):
            self.check()

    def test_edit_export_import_and_qa_overheads_count_and_unknown_is_not_free(self):
        p = self.row('GenerationBatch')
        p['overheads'] = [{'id': 'QA', 'phase': 'actual-medium review and import',
                           'cost': {'currency': 'USD', 'amount': '0.1'}, 'receipt_ref': 'proof.txt'}]
        self.assertEqual(self.check()['batch_summaries']['GB']['known_cost'], '0.9')
        del p['overheads'][0]['cost']
        p['status'] = 'open'
        result = self.check()['batch_summaries']['GB']
        self.assertEqual(result['unknown_cost_overheads'], 1)
        self.assertIsNone(result['cost_per_accepted_item'])
        self.assertFalse(result['declared_costs_complete'])

    def test_duplicate_nonfinite_json_and_cli_readback(self):
        path = self.root / 'input.json'
        for raw in ('{"kind":"SourceContract","kind":"ModelBundle"}', '{"n":NaN}',
                    '{"extensions":{"nested":[{"n":1e999}]}}'):
            path.write_text(raw)
            with self.assertRaises(A.ArtifactError):
                A.load_record(self.root, 'input.json')
        path.write_text(json.dumps(self.rows[0]))
        before = path.read_bytes()
        result = subprocess.run([sys.executable, '-B', str(HELPER), 'check', '--root', str(self.root),
                                 '--input', 'input.json'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        body = json.loads(result.stdout)
        self.assertTrue(body['ok'])
        self.assertFalse(body['actual_execution_authenticated'])
        self.assertEqual(body['artifact_files'][0]['sha256'], hashlib.sha256(before).hexdigest())
        self.assertEqual(path.read_bytes(), before)

    def test_plan_digest_cli_binds_complete_canonical_content_not_whitespace(self):
        plan = next(row for row in self.rows if row['kind'] == 'EvaluationPlan')
        path = self.root / 'plan.json'
        for indent in (None, 2):
            path.write_text(json.dumps(plan, indent=indent))
            result = subprocess.run([sys.executable, '-B', str(HELPER), 'digest', '--root', str(self.root),
                                     '--input', 'plan.json'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            body = json.loads(result.stdout)
            self.assertEqual(body['canonical_sha256'], A.record_sha256(plan))
            self.assertIn('no input-pin or cross-record verification', body['validation_scope'])

    def test_direct_api_nonfinite_extensions_and_container_values_rejected(self):
        for value in (float('inf'), float('-inf'), float('nan')):
            rows = copy.deepcopy(self.rows)
            rows[0]['extensions'] = {'nested': [{'overflow': value}]}
            with self.subTest(value=value), self.assertRaisesRegex(A.ArtifactError, 'nonfinite'):
                A.check_records(rows, self.root)
        record = copy.deepcopy(self.rows[0])
        record['extensions'] = {'not-json': {1, 2}}
        with self.assertRaisesRegex(A.ArtifactError, 'JSON scalar'):
            A.check_records([record], self.root)

    def test_artifact_changed_during_check_cannot_receive_current_file_pass(self):
        path = self.root / 'input.json'
        path.write_text(json.dumps(self.rows[0]))
        original = A.load_record
        calls = []
        def changing(root, ref):
            result = original(root, ref)
            calls.append(ref)
            if len(calls) == 1:
                changed = copy.deepcopy(self.rows[0])
                changed['owner'] = 'changed-after-read'
                path.write_text(json.dumps(changed))
            return result
        output = io.StringIO()
        with patch.object(A, 'load_record', side_effect=changing), redirect_stdout(output):
            code = A.main(['check', '--root', str(self.root), '--input', 'input.json'])
        self.assertEqual(code, 1)
        self.assertIn('artifact changed during validation', output.getvalue())


if __name__ == '__main__':
    unittest.main()
