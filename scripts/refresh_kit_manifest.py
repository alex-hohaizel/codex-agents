#!/usr/bin/env python3
"""Rebuild reviewed kit descriptors while retaining an exact Git predecessor.

No host installation, product migration or provenance certification is performed.
Use only after source review. --write is explicit; the default compares only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def descriptor(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected regular source: ' + str(path))
    data = path.read_bytes()
    return {'sha256': sha(data), 'size': len(data), 'mode': stat.S_IMODE(path.stat().st_mode)}


def git_read(root, revision, path):
    return subprocess.check_output(['git', 'show', revision + ':' + path], cwd=root)


def refresh(root, predecessor, write):
    current_path = root / 'releases/current.json'
    current = json.loads(current_path.read_text())
    baseline = json.loads(git_read(root, predecessor, 'kit/manifest.json'))
    baseline_commit = subprocess.check_output(['git', 'rev-parse', '--verify', predecessor + '^{commit}'], cwd=root, text=True).strip()
    if sorted(current['stable_skill_names']) != sorted(row['name'] for row in baseline['skills']):
        raise ValueError('Stable core inventory differs from reviewed predecessor')
    manifest = {key: value for key, value in baseline.items() if key != 'skills'}
    manifest.update(suite_id='agent-system-' + current['suite_version'], skills=[])
    for old in baseline['skills']:
        name = old['name']; directory = root / 'kit/skills' / name
        if directory.is_symlink(): raise ValueError('Linked skill root')
        paths = sorted(path for path in directory.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and path.name != '.DS_Store')
        if any(path.is_symlink() for path in directory.rglob('*')): raise ValueError('Linked skill source')
        files = {path.relative_to(directory).as_posix(): descriptor(path) for path in paths}
        old_ui = git_read(root, predecessor, 'kit/skills/' + name + '/agents/openai.yaml').decode()
        if sha(old_ui.encode()) != old['files']['agents/openai.yaml']['sha256']:
            raise ValueError('Predecessor interface bytes differ from its manifest')
        previous = list(old.get('previous_trees', []))
        old_tree = sha(''.join(key + '\0' + old['files'][key]['sha256'] + '\n' for key in sorted(old['files'])).encode())
        if not any(row.get('tree_sha256') == old_tree for row in previous):
            previous.append({'source': 'Verified canonical ' + old['version'] + ' predecessor at repository commit ' + baseline_commit,
                             'tree_sha256': old_tree, 'ui_yaml': old_ui, 'files': old['files']})
        manifest['skills'].append({'name': name, 'version': current['suite_version'], 'files': files, 'previous_trees': previous})
    changes = []
    def save(path, data):
        if not path.exists() or path.read_bytes() != data:
            changes.append(path.relative_to(root).as_posix())
            if write: path.write_bytes(data)
    manifest_data = encoded(manifest)
    save(root / 'kit/manifest.json', manifest_data)
    current['source_manifest_sha256'] = sha(manifest_data)
    save(current_path, (json.dumps(current, ensure_ascii=False, indent=2) + '\n').encode())
    files = {}
    for path in sorted((root / 'kit').rglob('*')):
        relative = path.relative_to(root / 'kit').as_posix()
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc' or path.name in {'.DS_Store', 'BUILD_VERIFICATION.json'}: continue
        if path.is_symlink(): raise ValueError('Linked kit resource')
        data = manifest_data if relative == 'manifest.json' else path.read_bytes()
        files[relative] = {'sha256': sha(data), 'size': len(data)}
    integrity = {'schema': 'agent-release-integrity/1', 'release': current['suite_version'], 'scope': 'curated-reusable-core-33-skills', 'hardware_bound': False,
                 'manifest_sha256': sha(manifest_data), 'files': files}
    save(root / 'kit/BUILD_VERIFICATION.json', encoded(integrity))
    return {'ok': write or not changes, 'write': write, 'predecessor_commit': baseline_commit,
            'suite_version': current['suite_version'], 'skills': len(manifest['skills']), 'skill_files': sum(len(row['files']) for row in manifest['skills']),
            'kit_files': len(files), 'manifest_sha256': sha(manifest_data), 'changed': changes}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--predecessor', required=True, help='Exact reviewed previous release commit')
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    try:
        result = refresh(args.root.resolve(), args.predecessor, args.write)
        print(json.dumps(result, indent=2)); return 0 if result['ok'] else 1
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)})); return 2

if __name__ == '__main__': raise SystemExit(main())
