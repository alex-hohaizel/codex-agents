#!/usr/bin/env python3
"""Audit/apply/verify/rollback the managed Codex profile with exact plans and journals."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

START, END = '<!-- agent-system-quality:start -->', '<!-- agent-system-quality:end -->'
REPO = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest() if text is not None else None


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def safe(path):
    require(path.is_absolute(), 'absolute path required')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink path rejected')
    return path


def read(path):
    safe(path)
    if not path.exists():
        return None
    require(path.is_file() and path.stat().st_size <= 2 * 1024 * 1024, 'unexpected/oversized file')
    return path.read_text(encoding='utf-8')


def load(path):
    raw = read(path)
    require(raw is not None, 'record missing')
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def atomic(path, text, mode=0o600):
    safe(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        parent = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save(path, record):
    atomic(path, json.dumps(record, ensure_ascii=False, indent=2) + '\n')


def merge(existing, block):
    existing = existing or ''
    require(existing.count(START) == existing.count(END) and existing.count(START) <= 1,
            'ambiguous managed profile markers')
    if START in existing:
        begin, end = existing.index(START), existing.index(END) + len(END)
        require(begin < end, 'reversed profile markers')
        return existing[:begin] + block.strip() + existing[end:]
    return existing.rstrip() + ('\n\n' if existing.strip() else '') + block.strip() + '\n'


def audit(repo, codex_root, standard_root):
    safe(repo); safe(codex_root); safe(standard_root)
    source = repo / 'host-profiles/codex/AGENTS.md'
    template = read(source)
    block = template.replace('{{STANDARD_ROOT}}', str(standard_root))
    target = codex_root / 'AGENTS.md'
    prior = read(target)
    desired = merge(prior, block)
    rows = [{'target': str(target), 'before_sha256': sha(prior), 'desired': desired,
             'after_sha256': sha(desired), 'source': str(source), 'source_sha256': sha(template)}]
    manifest = load(repo / 'agent-profiles/manifest.json')
    require(len(manifest['roles']) == 12, 'expected twelve bounded role profiles')
    for role in manifest['roles']:
        name = role['file']
        require(Path(name).name == name and name.startswith('foundry-') and name.endswith('.toml'),
                'unsafe role file')
        source, target = repo / 'agent-profiles' / name, codex_root / 'agents' / name
        desired, prior = read(source), read(target)
        require(sha(desired) == role['sha256'], 'role source drift')
        require(prior is None or sha(prior) in [role['sha256'], *role['previous_sha256']],
                'unknown customized role; reconcile without overwrite: ' + name)
        rows.append({'target': str(target), 'before_sha256': sha(prior), 'desired': desired,
                     'after_sha256': sha(desired), 'source': str(source), 'source_sha256': sha(desired)})
    return {'schema': 'atelier.host-profile-plan/1', 'codex_root': str(codex_root),
            'standard_root': str(standard_root), 'changes': rows, 'installation_performed': False}


def validate_rows(record):
    root = safe(Path(record['codex_root']))
    targets = set()
    for row in record['changes']:
        path = safe(Path(row['target']))
        require(path == root / 'AGENTS.md' or
                (path.parent == root / 'agents' and path.name.startswith('foundry-') and path.suffix == '.toml'),
                'target outside managed profile scope')
        require(path not in targets, 'duplicate target')
        targets.add(path)
        require(sha(row['desired']) == row['after_sha256'], 'desired bytes changed')



def validate_journal(journal, plan=None):
    require(journal.get('schema') == 'atelier.host-profile-journal/1', 'unsupported journal')
    validate_rows(journal)
    for row in journal['changes']:
        before = row.get('before')
        require(before is None or isinstance(before, str), 'invalid journal backup')
        require(sha(before) == row['before_sha256'], 'journal backup changed')
    if plan is not None:
        require(journal['codex_root'] == plan['codex_root'], 'journal root differs from plan')
        require(len(journal['changes']) == len(plan['changes']), 'journal rows differ from plan')
        for recorded, expected in zip(journal['changes'], plan['changes']):
            require({key: value for key, value in recorded.items() if key != 'before'} == expected,
                    'journal row differs from exact plan')


def apply(plan_path, journal_path):
    plan = load(plan_path)
    require(plan.get('schema') == 'atelier.host-profile-plan/1', 'unsupported plan')
    validate_rows(plan)
    if journal_path.exists():
        journal = load(journal_path)
        require(journal['plan_sha256'] == sha(read(plan_path)), 'journal/plan mismatch')
        validate_journal(journal, plan)
    else:
        changes = []
        for row in plan['changes']:
            require(sha(read(Path(row['source']))) == row['source_sha256'], 'source changed since audit')
            current = read(Path(row['target']))
            require(sha(current) == row['before_sha256'], 'target changed since audit')
            changes.append({**row, 'before': current})
        journal = {'schema': 'atelier.host-profile-journal/1', 'status': 'applying',
                   'codex_root': plan['codex_root'], 'plan_sha256': sha(read(plan_path)),
                   'changes': changes}
        save(journal_path, journal)
    require(journal['status'] in ('applying', 'applied'), 'journal is not apply-resumable')
    for row in journal['changes']:
        target = Path(row['target'])
        current = sha(read(target))
        if current == row['after_sha256']:
            continue
        require(current == row['before_sha256'], 'resume conflict; preserve current target')
        atomic(target, row['desired'], mode=0o644)
    journal['status'] = 'applied'
    save(journal_path, journal)
    return {'ok': True, 'journal': str(journal_path), 'files': len(journal['changes']),
            'host_discovery_verified': False}


def verify_or_rollback(journal_path, rollback=False):
    journal = load(journal_path)
    validate_journal(journal)
    require(journal['status'] in ('applied', 'rolling_back'), 'journal not applied')
    for row in journal['changes']:
        current = sha(read(Path(row['target'])))
        allowed = [row['after_sha256'], row['before_sha256']] if rollback and journal['status'] == 'rolling_back' else [row['after_sha256']]
        require(current in allowed, 'current target drift; preserve later work')
    if rollback:
        journal['status'] = 'rolling_back'; save(journal_path, journal)
        for row in reversed(journal['changes']):
            target = Path(row['target'])
            if sha(read(target)) == row['before_sha256']:
                continue
            if row['before'] is None:
                target.unlink()
            else:
                atomic(target, row['before'], mode=0o644)
        journal['status'] = 'rolled_back'; save(journal_path, journal)
    return {'ok': True, 'status': journal['status'], 'files': len(journal['changes']),
            'host_discovery_verified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['audit', 'apply', 'verify', 'rollback'])
    p.add_argument('--repo', type=Path, default=REPO)
    p.add_argument('--codex-root', type=Path, default=Path.home() / '.codex')
    p.add_argument('--standard-root', type=Path, default=Path.home() / '.agents/skills/agent-foundry')
    p.add_argument('--plan', type=Path)
    p.add_argument('--journal', type=Path)
    args = p.parse_args()
    try:
        if args.operation == 'audit':
            require(args.plan is not None and not args.plan.exists(), 'new --plan path required')
            result = audit(args.repo.absolute(), args.codex_root.absolute(), args.standard_root.absolute())
            save(args.plan.absolute(), result)
            print(json.dumps({'ok': True, 'plan': str(args.plan), 'changes': len(result['changes'])}))
        else:
            require(args.journal is not None, '--journal required')
            record = load(args.plan.absolute()) if args.operation == 'apply' else load(args.journal.absolute())
            root = safe(Path(record['codex_root'])); root.mkdir(parents=True, exist_ok=True)
            lockpath = safe(root / '.agent-system-profile.lock')
            with lockpath.open('a') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                if args.operation == 'apply':
                    result = apply(args.plan.absolute(), args.journal.absolute())
                else:
                    result = verify_or_rollback(args.journal.absolute(), args.operation == 'rollback')
                print(json.dumps(result))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
