#!/usr/bin/env python3
"""Materialize reviewed shared resources into independently usable skill bundles."""
import argparse
import hashlib
import json
from pathlib import Path

RESOURCES = {
    'production-quality.md': 'references/production-quality.md',
    'context-capsule.md': 'references/context-capsule.md',
    'production-profiles.json': 'assets/production-profiles.json',
    'context_capsule.py': 'scripts/context_capsule.py',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    names = json.loads((root / 'releases/current.json').read_text())['stable_skill_names']
    errors, records = [], []
    for source, target in RESOURCES.items():
        master = root / 'standards' / source
        data = master.read_bytes()
        for name in names:
            path = root / 'kit/skills' / name / target
            if path.is_symlink():
                errors.append(str(path.relative_to(root)) + ': symlink')
                continue
            if args.check:
                if not path.is_file() or path.read_bytes() != data:
                    errors.append(str(path.relative_to(root)) + ': source drift')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        records.append({'source': 'standards/' + source, 'target': target,
                        'sha256': hashlib.sha256(data).hexdigest(), 'bundles': len(names)})
    print(json.dumps({'ok': not errors, 'check_only': args.check,
                      'resources': records, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
