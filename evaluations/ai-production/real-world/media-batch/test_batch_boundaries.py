"""Generic accounting controls; no actual provider invoice or media quality claim."""
import unittest
from pathlib import Path
import tempfile
from campaign_batch import controlled_boundaries, ledger_check
from cache_guard import check


class BatchBoundaries(unittest.TestCase):
    def test_old_receipt_pin_cannot_rebind_changed_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'batch-report.json').write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError, 'old batch proof'):
                check(root, '0' * 64)

    def test_unknown_and_inflight_retry_rejected(self):
        result = controlled_boundaries()
        self.assertEqual(6, len(result['negative_controls']))
        self.assertIsNone(result['ledger']['full_unit_cost'])
        self.assertEqual(5, result['ledger']['attempts'])

    def test_exact_membership_variant_and_attempt_identity(self):
        expected = ['generic:01/en', 'generic:01/uk']
        outcomes = [{'key': key, 'status': 'accepted'} for key in expected]
        attempts = [{'id': str(i), 'key': key, 'status': 'succeeded', 'known_cost': 0} for i, key in enumerate(expected)]
        self.assertEqual(2, ledger_check(expected, list(reversed(outcomes)), attempts)['accepted_variants'])
        for changed in (outcomes[:1], [outcomes[0], outcomes[0]], [{**outcomes[0], 'key': 'generic:01/fr'}, outcomes[1]]):
            with self.assertRaises(ValueError):
                ledger_check(expected, changed, attempts)
        with self.assertRaises(ValueError):
            ledger_check(expected, outcomes, [attempts[0], attempts[0]])

    def test_no_fictional_zero_or_nonfinite_cost(self):
        expected = ['generic:01/en']
        outcomes = [{'key': expected[0], 'status': 'outcome_unknown'}]
        attempts = [{'id': 'one', 'key': expected[0], 'status': 'outcome_unknown', 'known_cost': None}]
        result = ledger_check(expected, outcomes, attempts)
        self.assertIsNone(result['full_unit_cost'])
        self.assertIsNone(result['known_cost_per_accepted_variant'])
        for value in (float('inf'), float('nan'), -1, True):
            with self.assertRaises(ValueError):
                ledger_check(expected, outcomes, [{**attempts[0], 'known_cost': value}])

    def test_retry_needs_declared_bound_and_safe_policy(self):
        expected = ['generic:01/en']
        outcomes = [{'key': expected[0], 'status': 'rejected'}]
        attempt = {'id': 'one', 'key': expected[0], 'status': 'known_failure', 'known_cost': .02,
                   'retry_requested': True, 'safe_retry_policy': 'known-failure-only', 'retry_number': 1, 'max_retries': 1}
        ledger_check(expected, outcomes, [attempt])
        for changed in ({'safe_retry_policy': ''}, {'retry_number': 2}, {'max_retries': 100}, {'status': 'dispatched'}):
            with self.assertRaises(ValueError):
                ledger_check(expected, outcomes, [{**attempt, **changed}])


if __name__ == '__main__':
    unittest.main()
