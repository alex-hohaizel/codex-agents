"""Acquire the two approved, small UCI archives; no model or dependency download."""
import argparse
import io
from pathlib import Path
import time
import urllib.parse
import urllib.request
import zipfile
from common import at, atomic_json, load_json, private_root, require, sha_bytes

SOURCES = {
    'bike': {'url': 'https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip',
             'page': 'https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset',
             'doi': '10.24432/C5W894', 'creator': 'Hadi Fanaee-T',
             'members': ['day.csv', 'Readme.txt']},
    'reviews': {'url': 'https://archive.ics.uci.edu/static/public/410/paper+reviews.zip',
                'page': 'https://archive.ics.uci.edu/dataset/410/paper+reviews',
                'doi': '10.24432/C50G60', 'creator': 'Brian Keith', 'members': ['reviews.json']},
}


def acquire(out):
    out = private_root(out)
    journal_path = out / 'acquisition.json'
    journal = load_json(journal_path) if journal_path.exists() else {
        'schema': 'atelier.real-data-acquisition/1', 'license': 'CC-BY-4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'scope': 'bounded local evaluation; raw files not redistributed',
        'requests': [], 'sources': {}}
    for name, source in SOURCES.items():
        target = out / (name + '.zip')
        previous = journal['sources'].get(name)
        if previous and target.is_file():
            require(sha_bytes(target.read_bytes()) == previous['sha256'], 'cached archive drift')
            continue
        require(len(journal['requests']) < 12, 'request budget exhausted')
        request_record = {'source': name, 'url': source['url'], 'started_at': at(), 'status': 'requested'}
        journal['requests'].append(request_record)
        atomic_json(journal_path, journal)
        request = urllib.request.Request(source['url'], headers={'User-Agent': 'Agent-System-bounded-evaluation/1'})
        start = time.monotonic()
        with urllib.request.urlopen(request, timeout=20) as response:
            require(response.status == 200, 'source did not return HTTP200')
            require(urllib.parse.urlparse(response.url).hostname == 'archive.ics.uci.edu', 'unreviewed source redirect')
            raw = response.read(1024 * 1024 + 1)
            require(len(raw) <= 1024 * 1024 and raw.startswith(b'PK'), 'source too large or not a ZIP archive')
            request_record.update(status='received', http_status=response.status,
                                  content_type=response.headers.get('Content-Type'),
                                  elapsed_seconds=time.monotonic() - start, bytes=len(raw))
        prior_total = sum(row.get('bytes', 0) for row in journal['requests'])
        require(prior_total <= 2 * 1024 * 1024, 'combined network byte cap exceeded')
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            require(sum(row.file_size for row in archive.infolist()) <= 5 * 1024 * 1024, 'archive expansion cap exceeded')
            members = []
            for basename in source['members']:
                candidates = [row for row in archive.infolist() if Path(row.filename).name == basename]
                require(len(candidates) == 1, 'missing/ambiguous expected archive member: ' + basename)
                row = candidates[0]
                require(not row.is_dir() and not (row.external_attr >> 16 & 0o170000) == 0o120000,
                        'linked/non-file archive member')
                content = archive.read(row)
                destination = out / name / basename
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                destination.write_bytes(content)
                destination.chmod(0o600)
                members.append({'name': basename, 'source_member': row.filename,
                                'bytes': len(content), 'sha256': sha_bytes(content)})
        target.write_bytes(raw)
        target.chmod(0o600)
        journal['sources'][name] = {**source, 'sha256': sha_bytes(raw), 'bytes': len(raw),
                                     'members_observed': members, 'observed_at': at()}
        atomic_json(journal_path, journal)
    return journal


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    result = acquire(parser.parse_args().out)
    import json
    print(json.dumps({'sources': len(result['sources']), 'requests': len(result['requests']),
                      'bytes': sum(row.get('bytes', 0) for row in result['requests']), 'new_spending': 0}))
