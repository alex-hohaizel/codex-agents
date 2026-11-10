"""Ephemeral loopback-only inference TEST adapter, never an installed service.

Client requests select no files, tools, URLs or model paths. The launcher binds
fixed reviewed local artifacts. No ambient provider or Codex credentials are read.
"""
import argparse
from datetime import date, timedelta
import copy
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
from common import atomic_json, canonical, load_json, observed_resources, private_root, require, sha_file
import forecast
import reviews
from source_guards import consume


def review_result(model, text, language):
    admitted = model['admission']['candidate_admitted']
    result = reviews.predict(model, text, baseline=not admitted)
    result.update(candidate_admitted=admitted, target=model['target'],
                  requires_human_review=not admitted or model['source_languages'].get(language, 0) < 30)
    return result


def serve(args):
    keypath = Path(args.key)
    require(stat.S_IMODE(keypath.stat().st_mode) == 0o600, 'test key must be a private0600 file')
    key = keypath.read_text().strip()
    require(len(key) >= 32, 'test key too short')
    fmodel, rmodel = load_json(args.forecast_model), load_json(args.review_model)
    require(fmodel['source_sha256'] == sha_file(args.source), 'forecast source pin mismatch')
    days = forecast.load_days(args.source)
    # Eagerly check code pins even before a request to an abstention path.
    require(fmodel['inference_source_sha256'] == sha_file(forecast.__file__), 'forecast code pin mismatch')
    reviews.predict(rmodel, '', baseline=True)
    count = [0]
    model_invocations = [0]
    lineage = load_json(args.lineage_graph) if args.lineage_graph else None

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Never log Authorization, request text, keys or raw source data.

        def answer(self, code, payload):
            raw = canonical(payload)
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            count[0] += 1
            if count[0] > 24:
                return self.answer(429, {'error': 'test rate/request cap'})
            host = '127.0.0.1:' + str(self.server.server_port)
            if self.headers.get('Host') != host or self.headers.get('Origin', 'http://' + host) != 'http://' + host:
                return self.answer(403, {'error': 'loopback origin required'})
            token = self.headers.get('Authorization', '')
            if not hmac.compare_digest(token, 'Bearer ' + key):
                return self.answer(401, {'error': 'test authentication required'})
            try:
                size = int(self.headers.get('Content-Length', '-1'))
                require(0 <= size <= 4096 and self.headers.get('Content-Type') == 'application/json', 'bounded JSON required')
                raw = self.rfile.read(size)
                require(len(raw) == size, 'truncated request')
                def number(value):
                    result = float(value)
                    require(math.isfinite(result), 'nonfinite input')
                    return result
                def pairs(values):
                    result = {}
                    for k, v in values:
                        require(k not in result, 'duplicate request key')
                        result[k] = v
                    return result
                value = json.loads(raw, object_pairs_hook=pairs, parse_float=number,
                                   parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite input')))
                require(isinstance(value, dict), 'request must be object')
                if self.path in ('/forecast', '/forecast/intermittent-control'):
                    require(set(value) == {'date'} and isinstance(value['date'], str), 'fixed date contract required')
                    day = date.fromisoformat(value['date'])
                    if lineage:
                        states = load_json(args.source_state)
                        states['source']['sha256'] = sha_file(args.source)
                        try:
                            consume(lineage, 'signature', states)
                        except ValueError:
                            return self.answer(409, {'error': 'project-test source withdrawn/changed or derived artifact stale',
                                                     'model_invocations': model_invocations[0]})
                    actual_days = days
                    if self.path == '/forecast/intermittent-control':
                        require(args.test_controls and day == date(2012, 10, 1), 'counterfactual test route disabled')
                        actual_days = copy.deepcopy(days)
                        for offset in range(2, 9):
                            actual_days[day - timedelta(days=offset)]['cnt'] = 0
                    model_invocations[0] += 1
                    result = forecast.predict(fmodel, day, actual_days,
                                              fmodel['selected_route'], True)
                    result['model_invocations'] = model_invocations[0]
                    if result['prediction'] is not None:
                        radius = fmodel['interval_radius']
                        result['interval'] = [max(0, result['prediction'] - radius), result['prediction'] + radius]
                elif self.path == '/review':
                    require(set(value) == {'text', 'language'} and isinstance(value['text'], str)
                            and len(value['text']) <= 2000 and value['language'] in ('en', 'es'), 'fixed text/language contract required')
                    result = review_result(rmodel, value['text'], value['language'])
                else:
                    return self.answer(404, {'error': 'unknown test route'})
                self.answer(200, result)
            except (ValueError, KeyError, TypeError):
                self.answer(400, {'error': 'invalid inference input'})

    server = HTTPServer(('127.0.0.1', 0), Handler)
    server.timeout = 1
    atomic_json(args.ready, {'port': server.server_port, 'pid': os.getpid()})
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and count[0] < 25:
        server.handle_request()
    server.server_close()


def exercise(args):
    start = time.monotonic()
    out = private_root(args.out)
    keypath, ready = out / 'test-key', out / 'ready.json'
    key = secrets.token_urlsafe(32)
    fd = os.open(keypath, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(key)
    # The actual copied source/model/signature feed the HTTP inference gate.
    # Withdrawal is this isolated project's test policy, not a revoked UCI license.
    copied_source = out / 'consumer-source.csv'
    copied_source.write_bytes(Path(args.source).read_bytes())
    original_source = copied_source.read_bytes()
    signature_path = out / 'prediction-signature.json'
    atomic_json(signature_path, {'model_sha256': sha_file(args.forecast_model), 'source_sha256': sha_file(copied_source),
                                 'consumer_sha256': sha_file(__file__), 'scope': 'isolated project-test withdrawal only'})
    graph_path, state_path = out / 'lineage-graph.json', out / 'source-state.json'
    graph = {'source': {'kind': 'source', 'sha256': sha_file(copied_source)},
             'model': {'kind': 'derived', 'path': str(Path(args.forecast_model).resolve()),
                       'sha256': sha_file(args.forecast_model), 'parents': ['source']},
             'signature': {'kind': 'derived', 'path': str(signature_path.resolve()),
                           'sha256': sha_file(signature_path), 'parents': ['model']}}
    atomic_json(graph_path, graph)
    original_state = {'source': {'sha256': sha_file(copied_source), 'revoked': False}}
    atomic_json(state_path, original_state)
    command = [sys.executable, '-E', '-B', __file__, 'serve', '--key', str(keypath), '--ready', str(ready),
               '--forecast-model', args.forecast_model, '--review-model', args.review_model, '--source', str(copied_source),
               '--lineage-graph', str(graph_path), '--source-state', str(state_path), '--test-controls']
    child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    observations = []
    try:
        deadline = time.monotonic() + 8
        while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(.03)
        require(ready.exists() and child.poll() is None, 'fresh-process consumer did not start')
        port = load_json(ready)['port']
        def request(path, payload, authorization=True, origin=None, raw=None):
            headers = {'Content-Type': 'application/json'}
            if authorization:
                headers['Authorization'] = 'Bearer ' + key
            if origin:
                headers['Origin'] = origin
            req = urllib.request.Request('http://127.0.0.1:' + str(port) + path,
                                         data=raw if raw is not None else canonical(payload), headers=headers, method='POST')
            try:
                with urllib.request.urlopen(req, timeout=3) as response:
                    status, body = response.status, json.load(response)
            except urllib.error.HTTPError as error:
                status, body = error.code, json.load(error)
            observations.append({'path': path, 'status': status, 'response': body})
            return status, body
        require(request('/forecast', {'date': '2012-10-01'}, False)[0] == 401, 'missing auth admitted')
        require(request('/forecast', {'date': '2012-10-01'}, origin='https://hostile.invalid')[0] == 403, 'foreign origin admitted')
        status, inferred = request('/forecast', {'date': '2012-10-01'})
        require(status == 200 and inferred['prediction'] is not None, 'actual forecast consumer failed')
        fm = load_json(args.forecast_model)
        direct = forecast.predict(fm, date(2012, 10, 1), forecast.load_days(args.source), fm['selected_route'], True)
        require(inferred['prediction'] == direct['prediction'], 'fresh process inference parity failed')
        require(request('/forecast', {'date': '2026-11-10'})[1]['status'] == 'abstained', 'OOD forecast admitted')
        status, reviewed = request('/review', {'text': 'El trabajo presenta una contribución interesante y resultados claros.', 'language': 'es'})
        require(status == 200 and not reviewed['candidate_admitted'] and reviewed['requires_human_review'], 'rejected model bypassed default admission')
        require(request('/review', {'text': '', 'language': 'en'})[1]['status'] == 'abstained', 'empty text fabricated prediction')
        for payload in ({'date': '2012-10-01', 'tool': 'shell'}, {'date': '2012-10-01', 'path': '/etc/passwd'}, {'date': 'https://hostile.invalid'}):
            require(request('/forecast', payload)[0] == 400, 'hostile schema admitted')
        require(request('/forecast', {}, raw=b'{"date":"2012-10-01","date":"2012-10-02"}')[0] == 400, 'duplicate keys admitted')
        require(request('/review', {'text': 'x' * 5000, 'language': 'es'})[0] == 400, 'request byte cap ignored')
        status, intermittent = request('/forecast/intermittent-control', {'date': '2012-10-01'})
        require(status == 200 and intermittent['status'] == 'abstained'
                and intermittent['reason'] == 'intermittent_history_not_validated', 'actual consumer admitted unsupported sparse history')
        invocation_count = intermittent['model_invocations']
        copied_source.write_bytes(original_source + b'\n')
        status, changed = request('/forecast', {'date': '2012-10-01'})
        require(status == 409 and changed['model_invocations'] == invocation_count, 'changed actual source reached model')
        copied_source.write_bytes(original_source)
        atomic_json(state_path, {'source': {'sha256': sha_file(copied_source), 'revoked': True}})
        status, withdrawn = request('/forecast', {'date': '2012-10-01'})
        require(status == 409 and withdrawn['model_invocations'] == invocation_count, 'project-withdrawn source reached model')
        atomic_json(state_path, original_state)
        status, restored = request('/forecast', {'date': '2012-10-01'})
        require(status == 200 and restored['prediction'] == inferred['prediction'], 'valid restored source changed actual forecast')
        for _ in range(25 - len(observations)):
            final_status, _ = request('/forecast', {'date': '2026-11-10'})
        require(final_status == 429, 'actual request/rate cap did not reject request25')
        report = {'schema': 'atelier.actual-model-consumer/1', 'fresh_process': True, 'loopback_only': True,
                  'ephemeral_private_key_mode': '0600', 'ambient_credentials_read': False,
                  'forecast_model_sha256': sha_file(args.forecast_model), 'review_model_sha256': sha_file(args.review_model),
                  'consumer_sha256': sha_file(__file__), 'observations': observations,
                  'actual_source_model_signature_lineage': {'graph_sha256': sha_file(graph_path),
                      'signature_sha256': sha_file(signature_path), 'project_test_withdrawal_only': True,
                      'changed_source_model_invocations_added': 0, 'withdrawn_source_model_invocations_added': 0},
                  'intermittent_history_control': {'synthetic_counterfactual': True, 'source_positive_history_replaced_by_seven_zeros': True,
                                                    'actual_consumer_abstained': True, 'not_real_forecast_score': True},
                  'exact_forecast_parity': True, 'request25_rate_cap_observed': True, 'resources': observed_resources(start),
                  'limits': ['Isolated local test adapter only; no installation, provider, external deployment, actual customers or production SLA',
                             'Spanish example demonstrates consumer routing, not additional heldout accuracy']}
        atomic_json(out / 'consumer-report.json', report)
        return report
    finally:
        child.terminate()
        child.communicate(timeout=5)
        keypath.unlink(missing_ok=True)
        ready.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('serve', 'exercise'):
        item = sub.add_parser(name)
        item.add_argument('--forecast-model', required=True)
        item.add_argument('--review-model', required=True)
        item.add_argument('--source', required=True)
        if name == 'serve':
            item.add_argument('--key', required=True)
            item.add_argument('--ready', required=True)
            item.add_argument('--lineage-graph')
            item.add_argument('--source-state')
            item.add_argument('--test-controls', action='store_true')
        else:
            item.add_argument('--out', required=True)
    args = parser.parse_args()
    if args.command == 'serve':
        serve(args)
    else:
        report = exercise(args)
        print(json.dumps({'fresh_process': report['fresh_process'], 'statuses': [o['status'] for o in report['observations']],
                          'exact_forecast_parity': report['exact_forecast_parity'], 'resources': report['resources']}))
