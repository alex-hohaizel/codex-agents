#!/usr/bin/env python3
"""Materialize reviewed shared resources into independently usable skill bundles."""
import argparse
import hashlib
import json
import stat
from pathlib import Path

from managed_release_checks import managed_model_policy

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
    'adaptive_work.py': 'scripts/adaptive_work.py',
    'briefing.py': 'scripts/briefing.py',
    'interaction.py': 'scripts/interaction.py',
    'status-view.schema.json': 'assets/status-view.schema.json',
}
CORE_RESOURCES = {
    'tests/test_briefing.py': 'scripts/tests/test_briefing.py',
    'tests/test_interaction.py': 'scripts/tests/test_interaction.py',
}
CONSTRUCTOR_RESOURCES = {
    'managed-execution.md': 'references/managed-execution.md',
}
ORCHESTRATOR_TEMPLATES = (
    'assets/decision-card.template.md',
    'assets/briefing-intake.template.json',
    'assets/execution-script.template.md',
    'assets/stage-closeout.template.md',
)


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
    release = json.loads((root / 'releases/current.json').read_text())
    names = release['stable_skill_names']
    errors, records = [], []
    core = [root / 'kit/skills' / name for name in names]
    orchestrator = root / 'optional-skills/atelier-orchestrator'
    constructors = [path for path in core if path.name in ('agent-foundry', 'design-specialist-skills')]
    resources = [('standards/' + source, target, bundles)
                 for table, bundles in ((RESOURCES, [*core, orchestrator]), (CORE_RESOURCES, core),
                                        (CONSTRUCTOR_RESOURCES, constructors))
                 for source, target in table.items()]
    resources.extend(('kit/skills/agent-foundry/' + target, target, [orchestrator])
                     for target in ORCHESTRATOR_TEMPLATES)
    # Read the complete reviewed source closure before replacing any bundle.
    # A missing new master must not leave a partly materialized old bundle.
    masters = {}
    for source, _, _ in resources:
        master = root / source
        if (not master.is_file() or any(linked(part) for part in (master, *master.parents)
                                      if part != root and root in part.parents)):
            errors.append(str(master.relative_to(root)) + ': missing/linked master')
        else:
            masters[source] = master.read_bytes()
    model = release.get('managed_model')
    if not managed_model_policy(model):
        errors.append('releases/current.json: missing or invalid managed model or reasoning effort')
    else:
        model_source = 'releases/current.json#managed_model'
        masters[model_source] = (json.dumps(model, indent=2) + '\n').encode('utf-8')
        resources.append((model_source, 'assets/managed-model.json', constructors))
    for _, target, bundles in resources:
        for bundle in bundles:
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
    if 'standards/platform_support.py' in masters:
        for relative in platform_targets:
            path = root / relative
            if args.check:
                if not path.is_file() or path.read_bytes() != masters['standards/platform_support.py']:
                    errors.append(relative + ': platform source drift')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(masters['standards/platform_support.py'])
    for source, target, bundles in resources:
        data = masters[source]
        for bundle in bundles:
            path = bundle / target
            if args.check:
                if not path.is_file() or path.read_bytes() != data:
                    errors.append(str(path.relative_to(root)) + ': source drift')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        records.append({'source': source, 'target': target,
                        'sha256': hashlib.sha256(data).hexdigest(), 'bundles': len(bundles),
                        'core_bundles': sum(bundle in core for bundle in bundles),
                        'optional_bundles': int(orchestrator in bundles)})
    print(json.dumps({'ok': not errors, 'check_only': args.check,
                      'resources': records, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
