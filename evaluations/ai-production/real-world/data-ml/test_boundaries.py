"""Generic adversarial controls; these tests are not real-task quality evidence."""
from datetime import date, timedelta
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest
from common import atomic_json, decode_json, private_root, sha_file
import forecast
from ingestion import ingest, normalized, parse_articles, SameOriginRedirect
import reviews
from source_guards import consume, cpa_gate
import urllib.request


class Boundaries(unittest.TestCase):
    def test_output_boundary_survives_copy_to_portable_bundle(self):
        with self.assertRaises(ValueError):
            private_root(Path(__file__).parent / 'never-written-private-data')
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / 'common.py'
            copied.write_bytes(Path(__file__).with_name('common.py').read_bytes())
            spec = importlib.util.spec_from_file_location('copied_common_for_test', copied)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual((Path(temporary) / 'output').resolve(), module.private_root(Path(temporary) / 'output'))

    def test_strict_json(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":1e999}', b'{"x":NaN}', b'{"nested":[Infinity]}'):
            with self.assertRaises(ValueError):
                decode_json(raw)

    def test_bad_timestamp_and_unit_quarantinable(self):
        for changes in ({'created_at': None}, {'created_at': '2026-01-01'}, {'unit': 'USD'}):
            with self.assertRaises(ValueError):
                normalized({'id': 'generic', 'text': 'generic text', 'created_at': '2026-01-01T00:00:00Z', **changes})

    def test_source_url_boundary(self):
        for url in ('https://github.com/anything', 'http://127.0.0.1@hostile.invalid/a', 'http://user:secret@127.0.0.1/a'):
            with self.assertRaises(ValueError):
                ingest(url, '/unused/never-created.sqlite', '0' * 64)
        request = urllib.request.Request('http://127.0.0.1:8000/a')
        with self.assertRaises(ValueError):
            SameOriginRedirect().redirect_request(request, None, 302, '', {}, 'http://127.0.0.1:8001/a')

    def test_static_login_and_selector(self):
        value = '<article data-id="generic" data-created-at="2026-01-01T00:00:00Z">Generic text</article>'
        self.assertEqual(1, len(parse_articles(value)))
        for bad in ('<input type="password">' + value, value.replace('article', 'section'), value[:-10]):
            with self.assertRaises(ValueError):
                parse_articles(bad)

    def test_forecast_delay_and_missing_history(self):
        day = date(2012, 10, 1)
        rows = {day - timedelta(days=i): {'cnt': 100 + i, 'available_at': forecast.midnight(day)} for i in range(2, 9)}
        self.assertIsNotNone(forecast.features(day, rows)[0])
        rows[day - timedelta(days=2)]['available_at'] = forecast.midnight(day + timedelta(days=1))
        with self.assertRaisesRegex(ValueError, 'future/delayed'):
            forecast.features(day, rows)
        self.assertIsNone(forecast.features(day, {})[0])

    def test_forecast_current_outcome_not_feature(self):
        day = date(2012, 10, 1)
        rows = {day - timedelta(days=i): {'cnt': i * 100, 'available_at': forecast.midnight(day)} for i in range(2, 9)}
        before = forecast.features(day, rows)[0]
        rows[day] = {'cnt': 999999999, 'casual': 4, 'registered': 7, 'holiday': 0}
        self.assertEqual(before, forecast.features(day, rows)[0])

    def test_actual_predictor_abstains_for_unvalidated_intermittent_history(self):
        day = date(2012, 10, 1)
        rows = {day - timedelta(days=i): {'cnt': 0, 'available_at': forecast.midnight(day)} for i in range(2, 9)}
        result = forecast.predict({}, day, rows, 'ridge', True)
        self.assertEqual('abstained', result['status'])
        self.assertEqual('intermittent_history_not_validated', result['reason'])
        self.assertIsNone(result['prediction'])

    def test_duplicate_text_unifies_paper_group_before_split(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'source.json'
            atomic_json(path, {'paper': [{'id': key, 'review': [{'id': 'r', 'text': text, 'lan': 'es', 'orientation': 1}]}
                                         for key, text in (('alpha', 'Misma reseña'), ('beta', 'MISMA   RESEÑA'))]})
            rows, quarantine, _ = reviews.read_rows(path)
            self.assertEqual([], quarantine)
            self.assertEqual(rows[0]['group'], rows[1]['group'])
            self.assertEqual(rows[0]['split'], rows[1]['split'])

    def test_train_only_vocabulary_and_code_pin(self):
        training = [{'text': 'positivo útil ejemplo', 'label': 1}, {'text': 'positivo útil ejemplo', 'label': 1}]
        model = reviews.fit(training, 'word', 1)
        self.assertNotIn('w:heldoutsecret', model['vocabulary'])
        self.assertEqual('fallback', reviews.predict(model, 'heldoutsecret')['status'])
        model['source_code_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            reviews.predict(model, '', baseline=True)

    def test_revocation_reaches_transitive_consumer_and_detects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'cache.json'
            atomic_json(path, {'generic': 1})
            graph = {'source': {'kind': 'source', 'sha256': 'a' * 64},
                     'cache': {'kind': 'derived', 'path': str(path), 'sha256': sha_file(path), 'parents': ['source']}}
            self.assertTrue(consume(graph, 'cache', {'source': {'sha256': 'a' * 64, 'revoked': False}}))
            for state in ({'sha256': 'a' * 64, 'revoked': True}, {'sha256': 'b' * 64, 'revoked': False}):
                with self.assertRaises(ValueError):
                    consume(graph, 'cache', {'source': state})
            path.write_text('{}')
            with self.assertRaises(ValueError):
                consume(graph, 'cache', {'source': {'sha256': 'a' * 64, 'revoked': False}})

    def test_cpa_no_data_and_zero_not_deleted(self):
        with self.assertRaisesRegex(ValueError, 'No representative'):
            cpa_gate([])
        row = {'campaign_id': 'generic', 'spend': 10, 'conversions': 0, 'currency': 'USD', 'attribution_window': '7d',
               'launch_at': '2026-01-02T00:00:00Z', 'feature_available_at': '2026-01-01T00:00:00Z', 'features': ['color']}
        self.assertEqual(1, cpa_gate([row], True)['zero_conversion_campaigns_retained'])
        for changed in ({'feature_available_at': '2026-01-03T00:00:00Z'}, {'features': ['conversions']},
                        {'spend': float('inf')}, {'spend': float('nan')}, {'conversions': .5},
                        {'launch_at': '2026-01-02T00:00:00'}, {'currency': ''}):
            with self.assertRaises(ValueError):
                cpa_gate([{**row, **changed}], True)
        with self.assertRaisesRegex(ValueError, 'mixed currency'):
            cpa_gate([row, {**row, 'campaign_id': 'other', 'currency': 'EUR'}], True)


if __name__ == '__main__':
    unittest.main()
