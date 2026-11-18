#!/usr/bin/env python3
"""Materialize reviewed shared resources into independently usable skill bundles."""
import argparse
import hashlib
import json
import stat
from pathlib import Path

RESOURCES = {
    'production-quality.md': 'references/production-quality.md',
    'tool-compatibility.md': 'references/tool-compatibility.md',
    'visual-identity.md': 'references/visual-identity.md',
    'research-and-synthesis.md': 'references/research-and-synthesis.md',
    'joint-work-codex.md': 'references/joint-work-codex.md',
    'interaction-protocol.md': 'references/interaction-protocol.md',
    'briefing-protocol.md': 'references/briefing-protocol.md',
    'adaptive-work.md': 'references/adaptive-work.md',
    'context-capsule.md': 'references/context-capsule.md',
    'production-profiles.json': 'assets/production-profiles.json',
    'context_capsule.py': 'scripts/context_capsule.py',
    'ai-production.md': 'references/ai-production.md',
    'ai-production.schema.json': 'assets/ai-production.schema.json',
    'ai_production.py': 'scripts/ai_production.py',
    'platform_support.py': 'scripts/platform_support.py',
}


def linked(path):
    try: info = path.lstat()
    except FileNotFoundError: return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    names = json.loads((root / 'releases/current.json').read_text())['stable_skill_names']
    errors, records = [], []
    bundles = [root / 'kit/skills' / name for name in names]
    bundles.append(root / 'optional-skills/atelier-orchestrator')
    # Read the complete reviewed source closure before replacing any bundle.
    # A missing new master must not leave a partly materialized old bundle.
    masters = {}
    for source in RESOURCES:
        master = root / 'standards' / source
        if linked(master) or not master.is_file():
            errors.append(str(master.relative_to(root)) + ': missing/linked master')
        else:
            masters[source] = master.read_bytes()
    for bundle in bundles:
        for target in RESOURCES.values():
            path = bundle / target
            if any(linked(part) for part in (path, *path.parents)
                   if part != root and root in part.parents):
                errors.append(str(path.relative_to(root)) + ': linked target path')
    platform_targets = ['scripts/platform_support.py', 'kit/portable/platform_support.py',
                        'commercial/platform_support.py', 'commercial/setup/platform_support.py',
                        'apps/agent-atelier/server/platform_support.py']
    for relative in platform_targets:
        path = root / relative
        if any(linked(part) for part in (path, *path.parents)
               if part != root and root in part.parents):
            errors.append(relative + ': linked/reparse platform target path')
    if errors:
        print(json.dumps({'ok': False, 'check_only': args.check,
                          'resources': records, 'errors': errors}, indent=2))
        return 1
    if 'platform_support.py' in masters:
        for relative in platform_targets:
            path = root / relative
            if args.check:
                if not path.is_file() or path.read_bytes() != masters['platform_support.py']:
                    errors.append(relative + ': platform source drift')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(masters['platform_support.py'])
    for source, target in RESOURCES.items():
        data = masters[source]
        for bundle in bundles:
            path = bundle / target
            if args.check:
                if not path.is_file() or path.read_bytes() != data:
                    errors.append(str(path.relative_to(root)) + ': source drift')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        records.append({'source': 'standards/' + source, 'target': target,
                        'sha256': hashlib.sha256(data).hexdigest(), 'bundles': len(bundles),
                        'core_bundles': len(names), 'optional_bundles': 1})
    print(json.dumps({'ok': not errors, 'check_only': args.check,
                      'resources': records, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
