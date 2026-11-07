#!/usr/bin/env python3
"""Plan and freeze one current chatbot.round/1 record; never executes a role."""
import argparse
import hashlib
import json
from pathlib import Path
import team_policy


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


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
    p.add_argument('--run', help='Actual prepared/planned/running run whose input snapshot is captured')
    a = p.parse_args()
    try:
        data = read(a.file)
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
        if a.command == 'bind-inputs':
            matches = [row for row in runs if row.get('id') == a.run]
            if not a.run or len(matches) != 1: raise ValueError('Exact existing --run ID required')
            run = matches[0]
            if run.get('status') not in {'prepared', 'planned', 'running'}:
                raise ValueError('Completed/failed/cancelled run inputs are immutable; use an actual new run')
            if run.get('input_snapshot'):
                raise ValueError('Existing input snapshot retained; use an actual new run for changed inputs')
            snapshot = team_policy.snapshot_inputs(plan, run, runs, requirement_records=data['requirements'])
            for cid, item in snapshot['components'].items():
                ref = plan['components'][cid]['artifact_ref']
                actual = root / ref
                if not actual.is_file() or actual.is_symlink() or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError('Input component bytes differ; reconcile current component hash first: ' + cid)
            for identity, item in snapshot['reviewed_outputs'].items():
                actual = root / item['output_ref']
                if not actual.is_file() or actual.is_symlink() or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != item['output_sha256']:
                    raise ValueError('Reviewed authored output bytes differ: ' + identity)
            for ref, expected_hash in snapshot['reviewed_evidence'].items():
                actual = root / ref
                if not actual.is_file() or actual.is_symlink() or root.resolve() not in actual.resolve().parents or hashlib.sha256(actual.read_bytes()).hexdigest() != expected_hash:
                    raise ValueError('Reviewed primary evidence bytes differ: ' + ref)
            run['input_snapshot'] = snapshot
            save(a.file, data)
            print('Current scoped inputs captured; no execution, result or acceptance created.')
            return 0
        if a.command == 'hashes':
            def sha(ref):
                path = root / ref
                if not path.is_file() or path.is_symlink() or root.resolve() not in path.resolve().parents:
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
            h = team_policy.snapshot_hash(data)
            data['completion']['package_hash'] = h
            save(a.file, data)
            print(json.dumps({'package_hash': h, 'acceptance_created': False}))
            return 0
        errors = team_policy.check(plan, ids, runs, data['completion'].get('package_hash'), root=root,
                                   ready=a.ready, requirement_records=data['requirements'])
        print(json.dumps({'ok': not errors, 'errors': errors, 'limits': 'Current team record only; not domain quality.'}, ensure_ascii=False, indent=2))
        return bool(errors)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
