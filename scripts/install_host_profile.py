#!/usr/bin/env python3
"""Audit/apply/verify/rollback the managed Codex profile with exact plans and journals."""
import argparse
from difflib import unified_diff
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
import re
import tempfile

START, END = '<!-- agent-system-quality:start -->', '<!-- agent-system-quality:end -->'
REPO = Path(__file__).resolve().parents[1]
# Exact predecessor releases from 43f113b8713588e3569b1c917037f75d88f78c6a and 8d8ecdf85fbb0924f686c4891383591c1513dcd7.
# This is a compatibility source, not an inferred installation/ownership receipt.
PREVIOUS_PROFILE_TEMPLATES = (
    ('host-profiles/codex/history/6.0.0-AGENTS.md',
     '8f47c4629edfdf1e4730527e5ea5b6e73e95b45affe8665d9eadadd80a88d891'),
    ('host-profiles/codex/history/6.1.0-AGENTS.md',
     '244b911f65c49f6302e90155d4ce1ca717dba814a89945d2bcd78e7972f5d589'),
    ('host-profiles/codex/history/6.2.0-AGENTS.md',
     '59dd12e4c89a0f043e1a5949c2843001440134f29ecaaefd8a1e6be94e3d68db'),
    ('host-profiles/codex/history/6.3.0-AGENTS.md',
     'a908d752e1ff531bc889776f5cbe6d1eb252a6c82d5c1696b3ce5cc7134cce73'),
)
# A managed role has a byte-pinned flat header and a literal triple-quoted body.
# Only these bounded selector lines may differ outside that body.
ROLE_PROMPT_OPEN = re.compile(r'^developer_instructions = """\r?\n$')
ROLE_PROMPT_CLOSE = re.compile(r'^"""(?:\r?\n)?$')
ROLE_SELECTOR = re.compile(
    r"[ \t]*(model|model_reasoning_effort)[ \t]*=[ \t]*(['\"])([A-Za-z0-9][A-Za-z0-9_.:/-]{0,127})\2"
    r"[ \t]*(?:#[^\x00-\x08\x0a-\x1f\x7f]*)?(?:\r?\n)?"
)
# Sol options observed from the pinned native App Server catalog. Legacy
# selectors can be recognized for a precise conflict without replacing them.
NATIVE_SOL_EFFORTS = {'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}
ROLE_EFFORTS = NATIVE_SOL_EFFORTS | {'none', 'minimal'}


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
    require(not any(platform_support.is_link_or_reparse(p) for p in (path, *path.parents)), 'symlink path rejected')
    return path


def read(path):
    safe(path)
    if not path.exists():
        return None
    require(path.is_file() and path.stat().st_size <= 2 * 1024 * 1024, 'unexpected/oversized file')
    with path.open('r', encoding='utf-8', newline='') as stream:
        return stream.read()


def parse(raw):
    require(raw is not None, 'record missing')
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def load(path):
    return parse(read(path))


def atomic(path, text, mode=0o600):
    safe(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        platform_support.fchmod(fd, mode)
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        platform_support.sync_dir(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save(path, record):
    atomic(path, json.dumps(record, ensure_ascii=False, indent=2) + '\n')


class ProfileConflict(ValueError):
    def __init__(self, message, target, source, installed, proposed):
        super().__init__(
            f'{message}: {target} (sha256 {sha(installed)}). Compare with {source} and reconcile '
            'the selected changes locally before auditing again.'
        )
        self.target, self.source = target, source
        self.installed, self.proposed = installed, proposed

    def diff(self):
        return ''.join(unified_diff(
            self.installed.splitlines(keepends=True), self.proposed.splitlines(keepends=True),
            fromfile=str(self.target), tofile=str(self.source),
        ))


def merge(existing, block, prior_blocks=(), *, target=None, source=None):
    existing = existing or ''
    require(existing.count(START) == existing.count(END) and existing.count(START) <= 1,
            'ambiguous managed profile markers')
    if START in existing:
        begin, end = existing.index(START), existing.index(END) + len(END)
        require(begin < end, 'reversed profile markers')
        proposed = existing[:begin] + block.strip() + existing[end:]
        if existing[begin:end] not in (block.strip(), *prior_blocks):
            raise ProfileConflict('unknown customized managed profile; reconcile without overwrite',
                                  target, source, existing, proposed)
        return proposed
    return existing.rstrip() + ('\n\n' if existing.strip() else '') + block.strip() + '\n'


def prior_profiles(repo, standard_root):
    blocks, sources = [], []
    for relative, expected_sha256 in PREVIOUS_PROFILE_TEMPLATES:
        path = repo / relative
        template = read(path)
        require(sha(template) == expected_sha256,
                'trusted prior profile source drift: ' + relative)
        blocks.append(template.replace('{{STANDARD_ROOT}}', str(standard_root)).strip())
        sources.append({'source': str(path), 'source_sha256': expected_sha256})
    return blocks, sources


def role_parts(text):
    """Parse the managed flat header without reserializing any local selectors."""
    output, selectors = [], {}
    began_prompt = in_prompt = False
    for line in text.splitlines(keepends=True):
        if in_prompt:
            in_prompt = ROLE_PROMPT_CLOSE.fullmatch(line) is None
        elif ROLE_PROMPT_OPEN.fullmatch(line):
            if began_prompt:
                return None
            began_prompt = in_prompt = True
        elif (match := ROLE_SELECTOR.fullmatch(line)) is not None:
            key, value = match[1], match[3]
            if key in selectors or (key == 'model_reasoning_effort' and value not in ROLE_EFFORTS):
                return None
            selectors[key] = (line, match.start(3), match.end(3), value)
            continue
        output.append(line)
    return (''.join(output), selectors) if began_prompt and not in_prompt else None


def reconcile_role(prior, canonical, role, model, target, source):
    canonical_parts = role_parts(canonical)
    require(canonical_parts is not None, 'invalid canonical role source')
    canonical_body, canonical_selectors = canonical_parts
    canonical_model = canonical_selectors.get('model')
    canonical_effort = canonical_selectors.get('model_reasoning_effort')
    require(canonical_model and canonical_model[3] == model and
            canonical_effort and canonical_effort[3] in NATIVE_SOL_EFFORTS,
            'role selectors differ from release policy')
    if prior is None or sha(prior) in [role['sha256'], *role['previous_sha256']]:
        return canonical
    parts = role_parts(prior)
    known_bodies = [sha(canonical_body), *role['previous_body_sha256']]
    conflict = 'unknown customized role; reconcile without overwrite'
    if parts is None or sha(parts[0]) not in known_bodies:
        raise ProfileConflict(conflict, target, source, prior, canonical)
    old_model, local_effort = (parts[1].get(name) for name in ('model', 'model_reasoning_effort'))
    if local_effort and local_effort[3] not in NATIVE_SOL_EFFORTS:
        choices = ', '.join(sorted(NATIVE_SOL_EFFORTS))
        raise ProfileConflict(
            f'{conflict}. Local reasoning effort {local_effort[3]} is unavailable for {model}; '
            f'choose a supported effort ({choices})',
            target, source, prior, canonical,
        )
    approved_legacy = {'gpt-6.1-sol'}
    if role['file'] == 'foundry-cost.toml' and sha(parts[0]) in role['previous_body_sha256']:
        approved_legacy.add('gpt-6-luna')
    replacements = {}
    if old_model is not None:
        line, start, end, configured = old_model
        if configured != model and configured not in approved_legacy:
            raise ProfileConflict(f'{conflict}. Local model {configured} has no managed migration to {model}',
                                  target, source, prior, canonical)
        if parts[0] == canonical_body and configured == model and local_effort is not None:
            return prior
        desired_model = line[:start] + model + line[end:]
        replacements[canonical_model[0]] = desired_model if desired_model.endswith('\n') else desired_model + '\n'
    if local_effort is not None:
        effort_line = local_effort[0]
        replacements[canonical_effort[0]] = effort_line if effort_line.endswith('\n') else effort_line + '\n'
    updated = ''.join(replacements.get(line, line) for line in canonical.splitlines(keepends=True))
    verified = role_parts(updated)
    expected_effort = (local_effort or canonical_effort)[3]
    require(verified is not None and verified[0] == canonical_body and
            verified[1]['model'][3] == model and verified[1]['model_reasoning_effort'][3] == expected_effort,
            'reconciled role selectors differ from the audited model and effort')
    return updated


def audit(repo, codex_root, standard_root):
    safe(repo); safe(codex_root); safe(standard_root)
    source = repo / 'host-profiles/codex/AGENTS.md'
    template = read(source)
    require(template is not None, 'managed profile source missing')
    block = template.replace('{{STANDARD_ROOT}}', str(standard_root))
    prior_blocks, compatibility_sources = prior_profiles(repo, standard_root)
    home=codex_root.parent
    personal={home/'.agents/skills/agent-foundry',home/'.codex/skills/agent-foundry'}
    if codex_root==home/'.codex' and standard_root in personal:
        # A root migration may render the same reviewed template at the other
        # exact personal root. Unknown instructions and arbitrary roots stay out.
        alternate=next(path for path in personal if path!=standard_root)
        prior_blocks.append(template.replace('{{STANDARD_ROOT}}',str(alternate)).strip())
        alternate_prior,_=prior_profiles(repo,alternate)
        prior_blocks.extend(alternate_prior)
    target = codex_root / 'AGENTS.md'
    prior = read(target)
    desired = merge(prior, block, prior_blocks, target=target, source=source)
    rows = [{'target': str(target), 'before_sha256': sha(prior), 'desired': desired,
             'after_sha256': sha(desired), 'source': str(source), 'source_sha256': sha(template),
             'compatibility_sources': compatibility_sources}]
    release_path = repo / 'releases/current.json'
    release_bytes = read(release_path)
    release = parse(release_bytes)
    model = release.get('managed_model', {}).get('id')
    require(release.get('schema_version') == 'codex-agents.release/1' and isinstance(model, str) and
            re.fullmatch(r'gpt-[0-9]+(?:\.[0-9]+)?-sol', model), 'invalid managed model release policy')
    manifest_path = repo / 'agent-profiles/manifest.json'
    manifest_bytes = read(manifest_path)
    manifest = parse(manifest_bytes)
    require(manifest.get('schema') == 'atelier.role-profiles/1' and
            manifest.get('release') == release.get('role_profiles', {}).get('version') and
            len(manifest['roles']) == 12 and len({role['file'] for role in manifest['roles']}) == 12,
            'expected twelve bounded role profiles at the managed release version')
    for role in manifest['roles']:
        name = role['file']
        require(Path(name).name == name and name.startswith('foundry-') and name.endswith('.toml'),
                'unsafe role file')
        source, target = repo / 'agent-profiles' / name, codex_root / 'agents' / name
        canonical, prior = read(source), read(target)
        require(sha(canonical) == role['sha256'], 'role source drift')
        before_sha256 = sha(prior)
        desired = reconcile_role(prior, canonical, role, model, target, source)
        rows.append({'target': str(target), 'before_sha256': before_sha256, 'desired': desired,
                     'after_sha256': sha(desired), 'source': str(source), 'source_sha256': role['sha256']})
    return {'schema': 'atelier.host-profile-plan/1', 'codex_root': str(codex_root),
            'standard_root': str(standard_root), 'changes': rows, 'installation_performed': False,
            'policy_sources': [{'source': str(path), 'source_sha256': sha(raw)}
                               for path, raw in ((release_path, release_bytes), (manifest_path, manifest_bytes))]}


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
        sources = row.get('compatibility_sources', [])
        require(isinstance(sources, list) and len(sources) <= len(PREVIOUS_PROFILE_TEMPLATES),
                'invalid profile compatibility source list')
        require(not sources or path == root / 'AGENTS.md',
                'profile compatibility source outside instruction row')
        for source in sources:
            require(isinstance(source, dict) and set(source) == {'source', 'source_sha256'}
                    and isinstance(source['source'], str)
                    and isinstance(source['source_sha256'], str)
                    and len(source['source_sha256']) == 64
                    and all(c in '0123456789abcdef' for c in source['source_sha256']),
                    'invalid profile compatibility source pin')
            safe(Path(source['source']))



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
        for source in plan.get('policy_sources', []):
            require(sha(read(Path(source['source']))) == source['source_sha256'],
                    'managed release policy or role manifest changed since audit')
        changes = []
        for row in plan['changes']:
            require(sha(read(Path(row['source']))) == row['source_sha256'], 'source changed since audit')
            for source in row.get('compatibility_sources', []):
                require(sha(read(Path(source['source']))) == source['source_sha256'],
                        'prior profile source changed since audit')
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
    p.add_argument('--standard-root', type=Path, default=platform_support.personal_skill_roots(Path.home())[0] / 'agent-foundry')
    p.add_argument('--plan', type=Path)
    p.add_argument('--journal', type=Path)
    p.add_argument('--conflict-diff', type=Path, help='Optional new private diff file for an audit conflict')
    args = p.parse_args()
    try:
        if args.operation == 'audit':
            require(args.plan is not None and not args.plan.exists(), 'new --plan path required')
            if args.conflict_diff:
                difference = safe(args.conflict_diff.absolute())
                require(difference != args.plan.absolute(), 'choose a separate conflict diff path')
            try:
                result = audit(args.repo.absolute(), args.codex_root.absolute(), args.standard_root.absolute())
            except ProfileConflict as conflict:
                if args.conflict_diff is None:
                    raise
                fd = os.open(difference, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, 'w', encoding='utf-8', newline='') as stream:
                    platform_support.fchmod(stream.fileno(), 0o600)
                    stream.write(conflict.diff())
                print(json.dumps({'ok': False, 'error': str(conflict), 'conflict_diff': str(difference)}))
                return 2
            save(args.plan.absolute(), result)
            print(json.dumps({'ok': True, 'plan': str(args.plan), 'changes': len(result['changes'])}))
        else:
            require(args.journal is not None, '--journal required')
            record = load(args.plan.absolute()) if args.operation == 'apply' else load(args.journal.absolute())
            root = safe(Path(record['codex_root'])); root.mkdir(parents=True, exist_ok=True)
            lockpath = safe(root / '.agent-system-profile.lock')
            with lockpath.open('a') as lock:
                if platform_support.WINDOWS: platform_support.fchmod(lock.fileno(),0o600)
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
