"""Bounded read-only paginated adapter with atomic dataset/cursor commit."""
import argparse
from datetime import datetime
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from common import canonical, decode_json, require, sha_bytes


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        before, after = urllib.parse.urlparse(request.full_url), urllib.parse.urlparse(newurl)
        require((before.scheme, before.hostname, before.port) ==
                (after.scheme, after.hostname, after.port), 'source redirect leaves controlled origin')
        return super().redirect_request(request, fp, code, message, headers, newurl)


def normalized(row):
    require(isinstance(row, dict), 'record is not an object')
    require(isinstance(row.get('id'), str) and row['id'], 'missing stable source ID')
    require(isinstance(row.get('text'), str) and row['text'].strip(), 'missing text')
    require(len(row['text']) <= 40000, 'text exceeds source contract')
    require(row.get('unit', 'issue') == 'issue', 'source unit/schema drift')
    require(isinstance(row.get('created_at'), str), 'missing source timestamp')
    stamp = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
    require(stamp.tzinfo is not None, 'missing source timezone')
    return {key: row[key] for key in ('id', 'text', 'created_at')}


def connect(path):
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=FULL')
    db.executescript('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);'
                     'CREATE TABLE IF NOT EXISTS rows(id TEXT PRIMARY KEY,payload TEXT,source_sha TEXT);'
                     'CREATE TABLE IF NOT EXISTS pages(cursor TEXT PRIMARY KEY,sha256 TEXT,received INTEGER,duplicates INTEGER,quarantined INTEGER);'
                     'CREATE TABLE IF NOT EXISTS quarantine(id TEXT PRIMARY KEY,reason TEXT,source_sha TEXT);')
    return db


def get(db, key, default=None):
    row = db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
    return json.loads(row[0]) if row else default


def put(db, key, value):
    db.execute('INSERT INTO meta VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
               (key, json.dumps(value)))


def summary(db):
    pages = db.execute('SELECT received,duplicates,quarantined FROM pages').fetchall()
    return {'records': db.execute('SELECT count(*) FROM rows').fetchone()[0],
            'received': sum(row[0] for row in pages), 'duplicates': sum(row[1] for row in pages),
            'quarantined': sum(row[2] for row in pages), 'pages': len(pages),
            'requests': get(db, 'requests', 0), 'next_cursor': get(db, 'cursor', '0'),
            'collection_complete': get(db, 'complete', False), 'error': get(db, 'error'),
            'source_sha256': get(db, 'source_sha256')}


def ingest(url, database, expected_source, max_requests=12, crash=False):
    parsed = urllib.parse.urlparse(url)
    require(parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost'),
            'evaluation adapter only admits the explicitly controlled loopback source')
    require(not parsed.username and not parsed.password and not parsed.query and not parsed.fragment,
            'source URL cannot contain credentials or preexisting query/fragment')
    require(type(max_requests) is int and 1 <= max_requests <= 12, 'request budget exceeds declared cap')
    db = connect(database)
    try:
        require(get(db, 'source_sha256', expected_source) == expected_source, 'source identity drift')
        with db:
            put(db, 'source_sha256', expected_source)
        if get(db, 'complete', False):
            return summary(db)
        failures = 0
        while True:
            cursor = get(db, 'cursor', '0')
            require(cursor is not None, 'missing cursor without complete receipt')
            require(not db.execute('SELECT 1 FROM pages WHERE cursor=?', (cursor,)).fetchone(), 'repeated committed source cursor')
            requests = get(db, 'requests', 0)
            require(requests < max_requests, 'request budget exhausted')
            with db:
                put(db, 'requests', requests + 1)
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), SameOriginRedirect())
                with opener.open(url + '?cursor=' + urllib.parse.quote(cursor), timeout=5) as response:
                    require(response.status == 200 and response.headers.get_content_type() == 'application/json',
                            'login HTML/content-type drift is not a dataset')
                    raw = response.read(512 * 1024 + 1)
                    require(len(raw) <= 512 * 1024, 'page byte cap exceeded')
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    delay = float(error.headers.get('Retry-After', '0'))
                    require(0 <= delay <= 1 and failures < 2, 'rate/retry budget exceeded')
                    failures += 1
                    time.sleep(delay)
                    continue
                raise ValueError('source page unavailable: HTTP' + str(error.code)) from error
            page = decode_json(raw, 512 * 1024)
            require(isinstance(page, dict) and page.get('source_sha256') == expected_source
                    and isinstance(page.get('items'), list) and 'next_cursor' in page, 'page schema/source drift')
            following = page['next_cursor']
            require(following is None or isinstance(following, str) and following != cursor, 'repeated/invalid next cursor')
            duplicates, quarantined = 0, 0
            try:
                db.execute('BEGIN IMMEDIATE')
                for index, item in enumerate(page['items']):
                    try:
                        row = normalized(item)
                    except (ValueError, KeyError, TypeError) as error:
                        quarantined += 1
                        db.execute('INSERT INTO quarantine VALUES(?,?,?)',
                                   (cursor + ':' + str(index), str(error), sha_bytes(canonical(item))))
                        continue
                    existed = db.execute('SELECT payload FROM rows WHERE id=?', (row['id'],)).fetchone()
                    if existed:
                        require(existed[0] == canonical(row).decode(), 'stable source ID changed content')
                        duplicates += 1
                    else:
                        db.execute('INSERT INTO rows VALUES(?,?,?)', (row['id'], canonical(row).decode(), sha_bytes(raw)))
                if crash:
                    os._exit(97)  # Isolated negative control: transaction cannot commit cursor/data independently.
                db.execute('INSERT INTO pages VALUES(?,?,?,?,?)',
                           (cursor, sha_bytes(raw), len(page['items']), duplicates, quarantined))
                put(db, 'cursor', following)
                put(db, 'complete', following is None)
                put(db, 'error', None)
                db.commit()
            except BaseException:
                db.rollback()
                raise
            failures = 0
            if following is None:
                return summary(db)
    except (ValueError, OSError, urllib.error.URLError) as error:
        with db:
            put(db, 'error', str(error))
            put(db, 'complete', False)
        return summary(db)
    finally:
        db.close()


class ArticleParser(HTMLParser):
    """Parse a known static article contract, never execute source instructions."""
    def __init__(self):
        super().__init__()
        self.rows, self.current, self.login = [], None, False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'input' and attrs.get('type') == 'password':
            self.login = True
        if tag == 'article':
            require(self.current is None, 'nested article schema drift')
            self.current = {'id': attrs.get('data-id'), 'text': '', 'created_at': attrs.get('data-created-at'),
                            'unit': attrs.get('data-unit', 'issue')}

    def handle_data(self, value):
        if self.current is not None:
            self.current['text'] += value

    def handle_endtag(self, tag):
        if tag == 'article' and self.current is not None:
            self.rows.append(normalized(self.current))
            self.current = None


def parse_articles(html):
    parser = ArticleParser()
    parser.feed(html)
    require(not parser.login and parser.current is None and parser.rows,
            'login, missing selector or incomplete article source')
    require(len({row['id'] for row in parser.rows}) == len(parser.rows), 'duplicate static record ID')
    return parser.rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--crash-before-cursor', action='store_true')
    args = parser.parse_args()
    print(json.dumps(ingest(args.url, args.database, args.source_sha256, crash=args.crash_before_cursor)))
