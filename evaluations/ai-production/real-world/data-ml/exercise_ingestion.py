"""Execute restart/partial/static/dynamic controls against a real frozen issue sample.

The HTTP and HTML transports are controlled local fixtures, not live scraping of
GitHub. Source text is data and is never interpreted as an instruction or code.
"""
import argparse
import base64
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import parse_qs, urlparse
from common import atomic_json, canonical, load_json, observed_resources, private_root, require, sha_file
from ingestion import ingest, parse_articles


def run(corpus, output, chrome=None):
    start = time.monotonic()
    out = private_root(output)
    original = load_json(corpus)
    if isinstance(original, dict):
        original = original.get('rows', original.get('issues', original.get('records')))
    require(isinstance(original, list) and len(original) == 100, 'expected frozen100-issue sample')
    rows = [{'id': str(r['id']), 'text': r['title'] + '\n' + (r.get('body') or ''),
             'created_at': r['created_at'], 'unit': 'issue'} for r in original]
    source = sha_file(corpus)
    requests = []
    seen = set()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlparse(self.path)
            cursor = int(parse_qs(parsed.query).get('cursor', ['0'])[0])
            requests.append({'route': parsed.path, 'cursor': cursor})
            if parsed.path == '/redirect':
                self.send_response(302)
                self.send_header('Location', 'http://192.0.2.1/not-authorized')
                self.end_headers()
                return
            if parsed.path == '/missing' and cursor == 1:
                self.send_error(503)
                return
            if parsed.path == '/login':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<input type="password">')
                return
            if parsed.path == '/normal' and parsed.path not in seen:
                seen.add(parsed.path)
                self.send_response(429)
                self.send_header('Retry-After', '0')
                self.end_headers()
                return
            items = list(rows[cursor * 25:(cursor + 1) * 25])
            if cursor == 0:
                items += [dict(rows[0]), {'id': 'quarantined-negative-control', 'text': '', 'created_at': rows[0]['created_at']}]
            page = {'source_sha256': source, 'items': items,
                    'next_cursor': str(cursor + 1) if cursor < 3 else None}
            if parsed.path == '/repeat':
                page['next_cursor'] = str(cursor)
            if parsed.path == '/source-drift':
                page['source_sha256'] = '0' * 64
            raw = canonical(page)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(raw)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    try:
        db = out / 'actual-issues.sqlite'
        command = [sys.executable, str(Path(__file__).with_name('ingestion.py')), '--url', base + '/normal',
                   '--database', str(db), '--source-sha256', source, '--crash-before-cursor']
        crashed = subprocess.run(command, capture_output=True, timeout=15)
        require(crashed.returncode == 97, 'isolated crash control did not interrupt transaction')
        connection = sqlite3.connect(db)
        before = {'rows': connection.execute('SELECT count(*) FROM rows').fetchone()[0],
                  'pages': connection.execute('SELECT count(*) FROM pages').fetchone()[0]}
        connection.close()
        require(before == {'rows': 0, 'pages': 0}, 'cursor/data commit was torn by crash')
        resumed = ingest(base + '/normal', db, source)
        require(resumed['records'] == 100 and resumed['received'] == 102 and resumed['duplicates'] == 1
                and resumed['quarantined'] == 1 and resumed['collection_complete'], 'actual denominator or recovery failed')
        request_count = len(requests)
        same = ingest(base + '/normal', db, source)
        require(same == resumed and len(requests) == request_count, 'completed replay requested source again')
        negatives = {}
        for route in ('missing', 'login', 'repeat', 'source-drift', 'redirect'):
            result = ingest(base + '/' + route, out / (route + '.sqlite'), source)
            require(not result['collection_complete'] and result['error'], route + ' was silently admitted')
            negatives[route] = result
    finally:
        server.shutdown()
        server.server_close()
    articles = ''.join('<article data-id="' + escape(r['id'], quote=True) + '" data-created-at="' +
                       escape(r['created_at'], quote=True) + '">' + escape(r['text']) + '</article>' for r in rows)
    static = '<!doctype html><meta charset="utf-8">' + articles
    (out / 'static.html').write_text(static, encoding='utf-8')
    require(len(parse_articles(static)) == 100, 'actual static parse lost records')
    selector_negatives = {}
    for name, value in {'login': '<input type="password">' + static,
                        'selector': static.replace('<article ', '<section ').replace('</article>', '</section>'),
                        'unit': static.replace('<article ', '<article data-unit="USD" ', 1),
                        'incomplete': static[:-10]}.items():
        try:
            parse_articles(value)
        except (ValueError, TypeError, AttributeError) as error:
            selector_negatives[name] = str(error)
    require(len(selector_negatives) == 4, 'static contract negative control escaped')
    dynamic_result = {'status': 'not-run', 'reason': 'actual browser required for dynamic-render claim'}
    if chrome:
        encoded = base64.b64encode(canonical(rows)).decode('ascii')
        script = ('const rows=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob("' + encoded +
                  '"), c=>c.charCodeAt(0))));for(const r of rows){const a=document.createElement("article");'
                  'a.dataset.id=r.id;a.dataset.createdAt=r.created_at;a.textContent=r.text;document.body.append(a);}')
        dynamic = '<!doctype html><meta charset="utf-8"><body><script>' + script + '</script>'
        path = out / 'dynamic.html'
        path.write_text(dynamic, encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='atelier-browser-') as profile:
            rendered = subprocess.run([chrome, '--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
                                       '--user-data-dir=' + profile, '--virtual-time-budget=1000', '--dump-dom', path.as_uri()],
                                      capture_output=True, timeout=20)
        require(rendered.returncode == 0, 'controlled browser rendering failed')
        dom = rendered.stdout.decode('utf-8')
        (out / 'dynamic-dom.html').write_text(dom, encoding='utf-8')
        actual = parse_articles(dom)
        require(len(actual) == 100 and {r['id'] for r in actual} == {r['id'] for r in rows}, 'dynamic rendered parse mismatch')
        require(not parse_articles.__name__ in script, 'parser cannot be its own rendering oracle')
        dynamic_result = {'status': 'observed', 'records': len(actual), 'html_sha256': sha_file(path),
                          'rendered_dom_sha256': sha_file(out / 'dynamic-dom.html'), 'browser_binary_sha256': sha_file(chrome)}
    report = {'source_sha256': source, 'source_rows': 100, 'controlled_transport': True,
              'adapter_sha256': sha_file(Path(__file__).with_name('ingestion.py')), 'driver_sha256': sha_file(__file__),
              'common_sha256': sha_file(Path(__file__).with_name('common.py')),
              'crash_exit': crashed.returncode, 'before_resume': before, 'resumed': resumed,
              'completed_replay_network_requests': 0, 'negative_controls': negatives,
              'static_records': 100, 'static_contract_negatives': selector_negatives, 'dynamic': dynamic_result,
              'request_observations': requests, 'resources': observed_resources(start),
              'limits': ['Controlled transports prove adapter recovery/parser boundaries, not live GitHub scraping rights or resilience',
                         'One malformed control is synthetic; all100 accepted records are actual frozen public issues']}
    atomic_json(out / 'ingestion-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--chrome')
    args = parser.parse_args()
    result = run(args.corpus, args.out, args.chrome)
    print(json.dumps({key: result[key] for key in ('source_rows', 'crash_exit', 'before_resume', 'resumed', 'dynamic', 'resources')}))
