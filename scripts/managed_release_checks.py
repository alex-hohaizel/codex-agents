"""Fail a managed release when an old Sol selector escapes its exact exception."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess

LEGACY_SELECTOR = re.compile(rb'\bgpt[- _]6[._]1[- _]sol\b', re.IGNORECASE)


def audit_model_sources(root, subjects, *, all_exceptions=False):
    """Check exact subject bytes and line-specific fixture identities."""
    exceptions = json.loads((root / 'governance/MANAGED-MODEL-EXCEPTIONS.json').read_text(encoding='utf8'))
    if exceptions.get('schema') != 'codex-agents.managed-model-exceptions/1':
        raise ValueError('Invalid managed model exception registry')
    allowed = {}
    for row in exceptions['exceptions']:
        key = row['path'], row['line_sha256']
        if key in allowed or type(row['count']) is not int or row['count'] < 1 or not row['purpose']:
            raise ValueError('Invalid or duplicate legacy model exception: ' + row['path'])
        allowed[key] = row['count']
    observed = Counter()
    errors = []
    for name, path in subjects:
        data = path.read_bytes()
        if not LEGACY_SELECTOR.search(data):
            continue
        for line_number, line in enumerate(data.splitlines(), 1):
            matches = LEGACY_SELECTOR.findall(line)
            if matches:
                key = name, sha256(line).hexdigest()
                observed[key] += len(matches)
                if observed[key] > allowed.get(key, 0):
                    errors.append(f'{name}:{line_number}: unmanaged legacy Sol selector')
    if all_exceptions:
        for key in allowed.keys() - observed.keys():
            errors.append(f'{key[0]}: stale legacy model exception')
        for key in allowed.keys() & observed.keys():
            if observed[key] != allowed[key]:
                errors.append(f'{key[0]}: legacy model exception count changed')
    return errors


def audit_checkout_models(root):
    root = root.resolve()
    metadata = root / '.git'
    is_checkout = metadata.exists() or metadata.is_symlink()
    if is_checkout:
        env = {key:value for key,value in os.environ.items()
               if key not in {'GIT_DIR','GIT_COMMON_DIR','GIT_WORK_TREE','GIT_INDEX_FILE'}}
        top = subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=root,env=env)
        if Path(os.fsdecode(top).strip()).resolve() != root:
            raise ValueError('Model audit requires the exact checkout root')
        tracked = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root,env=env)
        names = (os.fsdecode(value) for value in tracked.split(b'\0') if value)
    else:
        # Downloaded source bundles retain standalone source checks. They may
        # omit release-only test fixtures and never inherit a parent checkout.
        excluded = {'.git','__pycache__','node_modules','dist','.atelier-local','.AIWorking','test-results','playwright-report'}
        names = (path.relative_to(root).as_posix() for path in root.rglob('*')
                 if not excluded.intersection(path.relative_to(root).parts))
    subjects = []
    for name in names:
        path = root / name
        if path.is_symlink():
            raise ValueError('Linked source rejected during model audit: ' + name)
        if path.is_file():
            subjects.append((name, path))
    return audit_model_sources(root, subjects, all_exceptions=is_checkout)


def buyer_model_sources(stage):
    for path in sorted(stage.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        name = path.relative_to(stage).as_posix()
        if name.startswith('runtimes/'):
            continue
        canonical = name.removeprefix('product/')
        if name.startswith('setup/'):
            canonical = 'commercial/' + name
        yield canonical, path
