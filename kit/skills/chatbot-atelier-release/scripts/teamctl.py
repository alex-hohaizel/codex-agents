#!/usr/bin/env python3
"""Plan and freeze one current chatbot.round/1 record; never executes a role."""
import argparse
import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
fcntl = platform_support
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import team_policy
from check_round import EXPLORATORY_RUNS, check_current_choice, production_choice_for_round




def strict_json_loads(raw, **kwargs):
    """Reject ambiguous/nonfinite JSON before hashing, validation or mutation."""
    if len(raw) > 256 * 1024 * 1024:
        raise ValueError("JSON exceeds bounded input limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)
    kwargs.setdefault("object_pairs_hook", unique)
    kwargs.setdefault("parse_constant", finite)
    return json.loads(raw, **kwargs)

MAX_RECORD_BYTES = 16 * 1024 * 1024


class Record(dict):
    """An in-memory read revision; never persisted as competing domain state."""


def safe_file(path):
    path = Path(os.path.abspath(path))
    if any(platform_support.is_link_or_reparse(part) for part in (path, *path.parents)):
        raise ValueError('Round path must not traverse symlinks')
    return path


def record_bytes(path):
    fd = os.open(safe_file(path), os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_RECORD_BYTES:
            raise ValueError('Round must be a bounded regular file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES:
            raise ValueError('Round exceeds record limit')
        return raw
    finally:
        os.close(fd)


def read(path):
    path = safe_file(path)
    raw = record_bytes(path)
    value = strict_json_loads(raw)
    if not isinstance(value, dict):
        raise ValueError('Round must be an object')
    value = Record(value)
    value.source_sha256 = hashlib.sha256(raw).hexdigest()
    value.source_path = path
    return value


def save(path, value, expected_sha256=None):
    """Compare-and-swap one native round under a shared writer lock.

    Callers must read again after a conflict. A timeout/failed replace never
    authorizes discarding another writer's data or re-running an external job.
    """
    path = safe_file(path)
    if getattr(value, 'source_path', path) != path:
        raise ValueError('Round snapshot belongs to a different path')
    expected = expected_sha256 or getattr(value, 'source_sha256', None)
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    if len(encoded) > MAX_RECORD_BYTES:
        raise ValueError('Round exceeds record limit')
    lock_path = safe_file(path.with_name('.' + path.name + '.lock'))
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0), 0o600)
    temporary = None
    try:
        if not stat.S_ISREG(os.fstat(lock_fd).st_mode):
            raise ValueError('Round lock must be a regular file')
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        current = record_bytes(path) if path.exists() else None
        if current is not None and (not expected or hashlib.sha256(current).hexdigest() != expected):
            raise ValueError('Round revision conflict; reread current state before applying this change')
        if current is None and expected is not None:
            raise ValueError('Round revision conflict; previously read source is missing')
        fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
        mode = stat.S_IMODE(path.stat().st_mode) if current is not None else 0o600
        if platform_support.WINDOWS and current is not None and platform_support.private_acl_report(path)['private']:
            mode = 0o600
        platform_support.fchmod(fd, mode)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        platform_support.sync_dir(path.parent)
        if isinstance(value, Record):
            value.source_sha256 = hashlib.sha256(encoded).hexdigest()
            value.source_path = path
    finally:
        if temporary is not None:
            os.unlink(temporary)
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def require_own_container(data, stage='chat'):
    if stage != 'chat' or not isinstance(data, dict) or data.get('schema_version') != 'chatbot.round/1' or not isinstance(data.get('requirements'), list) or not isinstance(data.get('completion'), dict):
        raise ValueError('Only current chatbot.round/1 chat container is supported')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('plan', 'bind-inputs', 'hashes', 'freeze', 'check'))
    p.add_argument('file', type=Path)
    p.add_argument('--kind', choices=('local', 'feature', 'critical', 'stage'), default='stage')
    p.add_argument('--active', nargs='+')
    p.add_argument('--ready', action='store_true')
    p.add_argument('--project-root', type=Path, help='Owning project for production choices; defaults to the round directory')
    p.add_argument('--run', help='Actual prepared/planned/running run whose input snapshot is captured')
    p.add_argument('--expected-sha256', help='Reject a stale caller revision before planning or mutation')
    a = p.parse_args()
    try:
        data = read(a.file)
        if a.expected_sha256 and a.expected_sha256 != data.source_sha256:
            raise ValueError('Round revision conflict; caller must reread current state')
        require_own_container(data)
        ids = [r['id'] for r in data['requirements']]
        if a.command == 'plan':
            if data.get('team_policy'):
                raise ValueError('Existing plan retained; edit its explicit scope')
            if not ids:
                raise ValueError('Current requirements required before team planning')
            domains = {r['id']: r.get('domain_id') for r in data['requirements'] if isinstance(r, dict)}
            data['team_policy'] = team_policy.scaffold(ids, a.kind, a.active, requirement_domains=domains)
            save(a.file, data)
            print('Draft current plan written; no role, outcome or acceptance manufactured.')
            return 0
        plan, runs, root = data['team_policy'], data.get('runs', []), a.file.parent
        project_root = a.project_root or root
        if a.command == 'bind-inputs':
            matches = [row for row in runs if row.get('id') == a.run]
            if not a.run or len(matches) != 1: raise ValueError('Exact existing --run ID required')
            run = matches[0]
            if run.get('status') not in {'prepared', 'planned', 'running'}:
                raise ValueError('Completed/failed/cancelled run inputs are immutable; use an actual new run')
            if run.get('input_snapshot'):
                raise ValueError('Existing input snapshot retained; use an actual new run for changed inputs')
            phase = 'explore' if run.get('kind') in EXPLORATORY_RUNS else 'implement'
            choice = production_choice_for_round(data, project_root, phase)
            snapshot = team_policy.snapshot_inputs(plan, run, runs, requirement_records=data['requirements'])
            for cid, item in snapshot['components'].items():
                ref = plan['components'][cid]['artifact_ref']
                actual = root / ref
                if not actual.is_file() or platform_support.is_link_or_reparse(actual) or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError('Input component bytes differ; reconcile current component hash first: ' + cid)
            for identity, item in snapshot['reviewed_outputs'].items():
                actual = root / item['output_ref']
                if not actual.is_file() or platform_support.is_link_or_reparse(actual) or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != item['output_sha256']:
                    raise ValueError('Reviewed authored output bytes differ: ' + identity)
            for ref, expected_hash in snapshot['reviewed_evidence'].items():
                actual = root / ref
                if not actual.is_file() or platform_support.is_link_or_reparse(actual) or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != expected_hash:
                    raise ValueError('Reviewed primary evidence bytes differ: ' + ref)
            run['input_snapshot'] = snapshot
            if choice is not None:
                run['production_choice_binding'] = {key: choice[key] for key in ('phase', 'record_sha256', 'decision_sha256')}
            save(a.file, data)
            print('Current scoped inputs captured; no execution, result or acceptance created.')
            return 0
        if a.command == 'hashes':
            def sha(ref):
                path = root / ref
                if not path.is_file() or platform_support.is_link_or_reparse(path) or root.resolve() not in path.resolve().parents:
                    raise ValueError('Unsafe/missing material: ' + ref)
                return hashlib.sha256(path.read_bytes()).hexdigest()
            for cid, row in plan['components'].items():
                current = sha(row['artifact_ref'])
                previous = row.get('baseline_sha256') or row.get('sha256')
                if previous and previous != current and cid not in plan['scope']['changed_component_ids']:
                    raise ValueError('Declare changed dependency before updating its hash: ' + cid)
                row['sha256'] = current
            for run in runs:
                if run.get('status') == 'completed':
                    current = sha(run['output_ref'])
                    if run.get('output_sha256') and run['output_sha256'] != current:
                        raise ValueError('Completed run output changed; use an actual new run: ' + str(run.get('id')))
                    run['output_sha256'] = current
            for row in plan['assignments'].values():
                row['evidence_sha256s'] = {ref: sha(ref) for ref in row.get('evidence_refs', [])}
            save(a.file, data)
            print('Current input/output byte hashes recorded; acceptance is separate.')
            return 0
        if a.command == 'freeze':
            choice = production_choice_for_round(data, project_root, 'implement')
            if choice is not None:
                data['production_choice_decision_sha256'] = choice['decision_sha256']
                check_current_choice(data, project_root, 'implement')
            h = team_policy.snapshot_hash(data)
            data['completion']['package_hash'] = h
            save(a.file, data)
            print(json.dumps({'package_hash': h, 'acceptance_created': False}))
            return 0
        if a.ready:
            check_current_choice(data, project_root, 'accept')
        errors = team_policy.check(plan, ids, runs, data['completion'].get('package_hash'), root=root,
                                   ready=a.ready, requirement_records=data['requirements'])
        print(json.dumps({'ok': not errors, 'errors': errors, 'limits': 'Current team record only; not domain quality.'}, ensure_ascii=False, indent=2))
        return bool(errors)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
