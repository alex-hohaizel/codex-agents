#!/usr/bin/env python3
"""Check installed Game Atelier4 contracts and optional nine-skill shared bytes.

Checks structure, references, metadata and copy equality only; not design quality,
truth of observations, authorization or native execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re



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


NAMES = set('gamedev-director gamedev-studio gamedev-concepts gamedev-preproduction gamedev-assets gamedev-build gamedev-qa gamedev-release gamedev-liveops'.split())


def skill_name(path):
    m = re.search(r'^name:\s*([a-z0-9-]+)\s*$', (path/'SKILL.md').read_text(), re.M)
    return m[1] if m else None


def repository_toolkit_version(skill):
    """Use the release record when checking the canonical checkout."""
    source = skill.resolve()
    if source.parent.name != 'skills' or source.parent.parent.name != 'kit':
        return None
    release_record = source.parent.parent.parent/'releases/current.json'
    if not release_record.is_file():
        return None
    release = strict_json_loads(release_record.read_text(encoding='utf-8'))
    if release.get('schema_version') != 'codex-agents.release/1':
        raise ValueError('unsupported release metadata schema')
    version = release.get('suite_version')
    if not isinstance(version, str) or re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version) is None:
        raise ValueError('invalid toolkit version in release metadata')
    return version


def check_one(path):
    errors = []
    if path.is_symlink():
        return ['skill directory is linked: ' + str(path)]
    skill = (path/'SKILL.md').read_text(encoding='utf-8')
    if skill_name(path) not in NAMES:
        errors.append('unexpected skill name')
    if len(skill.splitlines()) >= 500:
        errors.append('SKILL exceeds progressive disclosure limit')
    for p in path.rglob('*'):
        if '__pycache__' in p.parts:
            continue
        if p.is_symlink():
            errors.append('symlink resource: ' + str(p.relative_to(path)))
        if p.is_file() and p.suffix == '.json':
            try:
                strict_json_loads(p.read_text(encoding='utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite ' + x)))
            except (ValueError, UnicodeError) as e:
                errors.append(str(p.relative_to(path)) + ': ' + str(e))
    for p in [path/'SKILL.md', *(path/'references').rglob('*.md')]:
        text = p.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]*\]\(([^\n)]+)\)', text):
            target = target.strip('<>')
            if re.match(r'^(?:https?:|mailto:|#|skill:|plugin:)', target):
                continue
            target = target.split('#', 1)[0]
            if not target or any(x in target for x in ('<', '>')):
                continue
            candidate = p.parent/target
            if not candidate.exists():
                errors.append(str(p.relative_to(path)) + ': missing link ' + target)
    registry = strict_json_loads((path/'assets/requirements-4.0.json').read_text())
    ids = [x['id'] for x in registry['items']]
    if len(ids) != 74 or len(set(ids)) != 74:
        errors.append('4.0 extension must retain74 unique approved IDs')
    for stem, count in [('GA4-U',8),('GA4-D1-Q',36),('GA4-D2-X',11)]:
        if sum(x.startswith(stem) for x in ids) != count:
            errors.append('missing approved coverage ' + stem)
    sources = strict_json_loads((path/'assets/approved-baseline-4.0.json').read_text())
    if {x['id'] for x in sources['sources']} != {'P1','D1','D2'}:
        errors.append('approved source baseline incomplete')
    catalog = strict_json_loads((path/'assets/stage-catalog.json').read_text())
    toolkit = catalog.get('toolkit_version')
    if not isinstance(toolkit, str) or re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', toolkit) is None:
        errors.append('invalid toolkit version in stage catalogue')
    elif (expected := repository_toolkit_version(path)) is not None and toolkit != expected:
        errors.append('stage catalogue toolkit version differs from release metadata')
    if (catalog.get('schema_version') != '1.0.0'
            or catalog.get('unique_skill_count') != len(NAMES)
            or catalog.get('entry_skill') != 'gamedev-director'):
        errors.append('invalid stage catalogue schema or scope')
    shared = strict_json_loads((path/'assets/suite-shared-paths.json').read_text())['paths']
    for rel in shared:
        if not (path/rel).is_file():
            errors.append('missing standalone resource: ' + rel)
    return errors


def check(root=None, single=None):
    errors, matched = [], {}
    if single is not None:
        matched = {skill_name(single): single}
    else:
        for p in root.glob('*/SKILL.md'):
            try:
                name = skill_name(p.parent)
            except (OSError, UnicodeError):
                continue
            if name in NAMES:
                if name in matched:
                    errors.append('duplicate installed name: ' + name)
                matched[name] = p.parent
        if set(matched) != NAMES:
            errors.append('nine installed named skills required')
    for name, path in sorted(matched.items()):
        errors.extend(name + ': ' + x for x in check_one(path))
    if len(matched) == 9:
        canonical = matched['gamedev-director']
        shared = strict_json_loads((canonical/'assets/suite-shared-paths.json').read_text())['paths']
        for name, path in sorted(matched.items()):
            for rel in shared:
                if (path/rel).is_file() and hashlib.sha256((path/rel).read_bytes()).digest() != hashlib.sha256((canonical/rel).read_bytes()).digest():
                    errors.append(name + ': divergent shared resource ' + rel)
    return {'valid': not errors, 'skills_checked': len(matched), 'errors': errors,
            'scope': 'installed metadata, local references, approved coverage IDs and shared byte equality',
            'quality_certified': False, 'native_runtime_verified': False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group()
    g.add_argument('--suite-root',type=Path)
    g.add_argument('--skill',type=Path)
    a=p.parse_args()
    try:
        result=check(root=a.suite_root, single=a.skill or (None if a.suite_root else Path(__file__).resolve().parent.parent))
    except (OSError,ValueError,TypeError,KeyError) as e:
        result={'valid':False,'errors':[str(e)],'quality_certified':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['valid'] else 1


if __name__=='__main__':
    raise SystemExit(main())
