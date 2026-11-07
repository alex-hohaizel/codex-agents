#!/usr/bin/env python3
"""Read-only file integrity check of this release; no hardware-bound signing."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args()
try:
    root=a.root.absolute()
    if any(x.is_symlink() for x in (root,*root.parents)):raise ValueError('linked root')
    record=root/'BUILD_VERIFICATION.json'
    if record.is_symlink():raise ValueError('linked verification record')
    data=json.loads(record.read_text());assert data['schema']=='agent-release-integrity/1';errors=[]
    observed=set()
    for candidate in root.rglob('*'):
        if candidate.is_symlink():raise ValueError('linked resource')
        if candidate.is_file() and candidate.relative_to(root).as_posix()!='BUILD_VERIFICATION.json' and candidate.name!='.DS_Store' and '__pycache__' not in candidate.relative_to(root).parts:
            observed.add(candidate.relative_to(root).as_posix())
    if observed!=set(data['files']):
        errors.extend('unexpected file: '+name for name in sorted(observed-set(data['files'])))
        errors.extend('missing file: '+name for name in sorted(set(data['files'])-observed))
    for rel,expected in data['files'].items():
        pure=PurePosixPath(rel)
        if pure.is_absolute() or '..' in pure.parts or pure.as_posix()!=rel or '\\' in rel or ':' in rel:raise ValueError('unsafe declared path')
        file=root.joinpath(*pure.parts)
        if any(root.joinpath(*pure.parts[:i]).is_symlink() for i in range(1,len(pure.parts)+1)):raise ValueError('linked resource')
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected['sha256'] or file.stat().st_size!=expected['size']:errors.append(rel)
    actual_manifest=hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest()
    if actual_manifest!=data['manifest_sha256']:errors.append('manifest binding')
    print(json.dumps({'valid':not errors,'release':data['release'],'files_checked':len(data['files']),'manifest_sha256':actual_manifest,'errors':errors,'runtime_verified':False},ensure_ascii=False,indent=2));raise SystemExit(0 if not errors else 2)
except (ValueError,OSError,KeyError,TypeError,AssertionError) as e:
    print(json.dumps({'valid':False,'error':str(e)},ensure_ascii=False));raise SystemExit(2)
