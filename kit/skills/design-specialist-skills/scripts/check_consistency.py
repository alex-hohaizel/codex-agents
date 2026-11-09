#!/usr/bin/env python3
"""Offline consistency checks for a self-contained personal skill package."""
import argparse
import ast
import json
import re
from pathlib import Path




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


def check(root):
    root = Path(root).resolve()
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    def load(path):
        return strict_json_loads(path.read_text(encoding='utf-8'))
    skill = root / 'SKILL.md'
    if not skill.is_file():
        return ['SKILL.md missing']
    text = skill.read_text(encoding='utf-8')
    contract_file = root / 'assets/consistency-contract.json'
    if not contract_file.is_file():
        return ['assets/consistency-contract.json missing']
    config = load(contract_file)
    need(config.get('schema_version') == 'skill.consistency/1', 'unsupported consistency contract')
    checker = config.get('current_checker', '')
    checker_path = root / 'scripts' / checker
    need(checker_path.is_file(), 'current domain checker missing: ' + checker)
    need(checker in text, 'current checker not described in SKILL.md')
    for flag in config.get('root_required_flags', []):
        need(flag in text, 'current SKILL.md route omits ' + flag)
        if checker_path.exists():
            need(flag in checker_path.read_text(), 'documented flag unsupported by checker: ' + flag)

    history = set(config.get('history_documents', []))
    docs = [skill] + sorted((root / 'references').glob('*.md'))
    # A dated primary source or historical research date is not a method pin.
    date = r'(?![0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}\b)'
    end = r'(?!\w|\.[0-9])'
    method_pin = re.compile(r'Іскр[\w’\'-]*\s+[vV]?' + date + r'[0-9]+(?:\.[0-9]+)*' + end + r'|(?:методологі[\w’\'-]*|редакці[яї])\s+' + date + r'[0-9]+\.[0-9]+' + end, re.I)
    obsolete_staff = re.compile(r'Зберегти канонічних\s+\d+\s+base.*specialist/judge|\b\d+\s+техлідів,\s*\d+\s+QA|по одному (?:окремому )?(?:actual )?judge-агенту на кожен must|кожен фіналіст потребує\s+\d+\s+актуальних суддів|разом\s+\d+\s+з окремим вайбом', re.I)
    for doc in docs:
        content = doc.read_text(encoding='utf-8')
        rel = doc.relative_to(root).as_posix()
        if rel not in history:
            for number, line in enumerate(content.splitlines(), 1):
                need(not method_pin.search(line), rel + ':' + str(number) + ': cosmetic methodology edition pin')
                need(not obsolete_staff.search(line), rel + ':' + str(number) + ': fixed historical staff instruction')
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', content):
            target = match.group(1).split('#', 1)[0]
            if not target or re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', target):
                continue
            path = (doc.parent / target).resolve()
            need(path == root or root in path.parents, rel + ': hidden external filesystem dependency: ' + target)
            need(path.exists(), rel + ': broken local reference: ' + target)
    # Root commands are the executable entry points. Shared technical references
    # can explicitly describe other data formats without implying local tools.
    tools = set(re.findall(r'\bscripts/([A-Za-z_][A-Za-z_0-9-]*\.py)\b', text))
    tools.update(re.findall(r'\b([A-Za-z_][A-Za-z_0-9-]*\.py)\s+(?:init|check|freeze|pack|plan|hashes|inventory)\b', text))
    for script in tools:
        need((root / 'scripts' / script).is_file(), 'SKILL.md advertises an unavailable local script: ' + script)

    profile_file = root / 'assets/team-profile.json'
    if profile_file.exists():
        profile = load(profile_file)
        need(profile.get('schema_version') == 'iskra.team-profile/2', 'unknown team profile schema')
        need(profile.get('stage') == config.get('canonical_stage'), 'stage/profile/consistency contract disagree')
        domains = profile.get('domains', [])
        domain_ids = [d['id'] for d in domains]
        need(len(domain_ids) == len(set(domain_ids)), 'duplicate subject domains')
        actual = [rid for d in domains for rid in d['requirement_ids']]
        need(len(actual) == len(set(actual)), 'criterion has multiple primary owners')
        expected = set()
        for name in ('mobile-breakout-contract.json', 'base-requirements.json', 'stage-contract.json', 'requirements.json'):
            path = root / 'assets' / name
            if path.exists():
                expected.update(row['id'] for row in load(path)['requirements'])
        if profile.get('stage') == 'studio' and checker_path.exists():
            for node in ast.parse(checker_path.read_text()).body:
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CRITERIA' for t in node.targets):
                    expected.update(ast.literal_eval(node.value))
        need(set(actual) == expected, 'profile must cover every canonical criterion exactly once')
        need(set(profile.get('critical_requirement_ids', [])) <= set(actual), 'unknown critical criterion')
        for name in ('team_policy.py', 'teamctl.py'):
            need((root / 'scripts' / name).exists(), 'current team helper missing: ' + name)
        registry_file = root / 'assets/team-profile-registry.json'
        if registry_file.exists():
            own = [p for p in load(registry_file)['profiles'] if p['stage'] == profile['stage']]
            need(own == [profile], 'self-contained trusted profile registry is stale')
        policy = root / 'references/team-policy.md'
        need(policy.is_file(), 'current team policy missing')
        if policy.is_file():
            need('scoped_complete' in policy.read_text(), 'team policy lacks explicit local completion')
    provenance_file = root / 'assets/method-provenance.json'
    if provenance_file.exists():
        provenance = load(provenance_file)
        need(provenance.get('record_kind') == 'historical_method_provenance' and provenance.get('historical_origin_is_execution_policy') is False, 'historical origin must not define current execution policy')
        need((root / provenance.get('current_policy_ref', '')).is_file(), 'current policy reference missing in provenance')
        need(isinstance(provenance.get('historical_origin'), dict), 'original provenance must remain intact')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors = check(args.root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, SyntaxError) as exc:
        errors = ['invalid package metadata: ' + str(exc)]
    print(json.dumps({'ok': not errors, 'errors': errors, 'scope': 'Instructions, local routes and contract coherence; not product quality or real consent.'}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
