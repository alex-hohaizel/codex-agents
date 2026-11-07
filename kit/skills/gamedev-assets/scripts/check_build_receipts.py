#!/usr/bin/env python3
"""Check local receipt bytes/shape. Does not prove execution, signing or quality.

Usage: check_build_receipts.py PACKAGE RECEIPTS_JSON
Folder digest: SHA256 of UTF-8 JSON [[relative_posix_path,file_sha256],...]
with sorted paths and separators=(',',':'); symlinks are rejected.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import re
import sys
from zipfile import BadZipFile, ZipFile

TYPES = {
    'apk': ('android', False),
    'aab': ('android', False),
    'ipa': ('ios', False),
    'xcarchive': ('ios', True),
    'simulator-app': ('ios', True),
}

def digest(path: Path) -> str:
    if path.is_file():
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        return h.hexdigest()
    rows = []
    for child in sorted(path.rglob('*')):
        if child.is_symlink():
            raise ValueError('symlink inside artifact')
        if child.is_file():
            rows.append([child.relative_to(path).as_posix(), digest(child)])
    if not rows:
        raise ValueError('empty folder artifact')
    return hashlib.sha256(json.dumps(rows, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def local_path(root: Path, value: object, *, folder: bool = False) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError('missing relative path')
    raw = Path(value)
    if raw.is_absolute() or '..' in raw.parts:
        raise ValueError('path must be package-relative without parent traversal')
    candidate = root / raw
    check = candidate
    while check != root:
        if check.is_symlink():
            raise ValueError('symlink path is not accepted')
        check = check.parent
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError('path leaves package')
    if folder and not resolved.is_dir():
        raise ValueError('expected folder artifact')
    if not folder and (not resolved.is_file() or resolved.stat().st_size == 0):
        raise ValueError('expected nonempty file')
    return resolved

def artifact_shape(path: Path, kind: str) -> None:
    if kind in ('apk', 'aab', 'ipa'):
        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())
                if kind == 'apk' and 'AndroidManifest.xml' not in names:
                    raise ValueError('APK lacks AndroidManifest.xml')
                if kind == 'aab' and not {'BundleConfig.pb', 'base/manifest/AndroidManifest.xml'}.issubset(names):
                    raise ValueError('AAB lacks required bundle structure')
                if kind == 'ipa' and not any(re.fullmatch(r'Payload/[^/]+\.app/Info\.plist', name) for name in names):
                    raise ValueError('IPA lacks Payload app metadata')
        except BadZipFile as exc:
            raise ValueError('artifact is not a readable ZIP container') from exc
    else:
        metadata = path / 'Info.plist'
        if not metadata.is_file():
            raise ValueError('folder artifact lacks Info.plist')
        try:
            info = plistlib.loads(metadata.read_bytes())
        except Exception as exc:
            raise ValueError('Info.plist cannot be parsed') from exc
        if kind == 'xcarchive' and not (path / 'Products' / 'Applications').is_dir():
            raise ValueError('archive lacks Products/Applications')
        if kind == 'simulator-app':
            executable = info.get('CFBundleExecutable')
            if not isinstance(executable, str) or '/' in executable or not (path / executable).is_file():
                raise ValueError('simulator app lacks declared executable')

def verify(root: Path, document: object) -> list[str]:
    errors = []
    if not isinstance(document, dict) or document.get('kind') != 'actual_build_receipts':
        return ['document kind must be actual_build_receipts; examples/plans are not execution receipts']
    receipts = document.get('receipts')
    if not isinstance(receipts, list) or not receipts:
        return ['receipts must be a nonempty array']
    seen = set()
    for index, receipt in enumerate(receipts):
        prefix = f'receipt[{index}]'
        try:
            if not isinstance(receipt, dict):
                raise ValueError('expected object')
            rid = receipt.get('receipt_id')
            if not isinstance(rid, str) or not rid or rid in seen:
                raise ValueError('receipt_id must be unique and nonempty')
            seen.add(rid)
            kind = receipt.get('artifact_type')
            if kind not in TYPES:
                raise ValueError('unsupported artifact_type')
            platform, folder = TYPES[kind]
            if receipt.get('platform') != platform:
                raise ValueError('artifact_type/platform mismatch')
            for field in ('game_id', 'source_commit', 'built_at', 'build_profile', 'signing_status'):
                value = receipt.get(field)
                if not isinstance(value, str) or not value.strip() or 'REPLACE' in value:
                    raise ValueError(f'{field} must contain actual metadata')
            for field in ('artifact_sha256', 'baseline_sha256'):
                if not re.fullmatch(r'[0-9a-f]{64}', str(receipt.get(field, ''))):
                    raise ValueError(f'{field} must be lowercase SHA256')
            if type(receipt.get('exit_code')) is not int or receipt['exit_code'] != 0:
                raise ValueError('successful actual build requires exit_code=0')
            command = receipt.get('command')
            if not (isinstance(command, str) and command.strip()) and not (
                isinstance(command, list) and command and all(isinstance(x, str) and x for x in command)
            ):
                raise ValueError('command must record the executed command')
            if not isinstance(receipt.get('toolchain'), dict) or not receipt['toolchain']:
                raise ValueError('toolchain metadata required')
            if not isinstance(receipt.get('limitations'), list):
                raise ValueError('limitations must be an array')
            path = local_path(root, receipt.get('artifact_path'), folder=folder)
            local_path(root, receipt.get('log_path'))
            if digest(path) != receipt['artifact_sha256']:
                raise ValueError('artifact bytes do not match artifact_sha256')
            artifact_shape(path, kind)
        except (ValueError, OSError) as exc:
            errors.append(f'{prefix}: {exc}')
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('receipts_json', type=Path)
    args = parser.parse_args()
    try:
        root = args.package.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('package must be a directory')
        document = json.loads(args.receipts_json.read_text())
        errors = verify(root, document)
    except (ValueError, OSError) as exc:
        errors = [str(exc)]
    if errors:
        print(json.dumps({'status': 'failed', 'errors': errors}, ensure_ascii=False))
        return 1
    print(json.dumps({'status': 'structural_bytes_verified', 'receipts': len(document['receipts']),
                      'does_not_prove': ['actual execution', 'signing', 'device install', 'quality']}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    sys.exit(main())
