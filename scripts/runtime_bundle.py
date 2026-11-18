#!/usr/bin/env python3
"""Fetch pinned vendor runtimes and build a self-contained native tool bundle."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

SCHEMA = 'codex-agents.portable-runtime/1'
EPOCH = (2026, 11, 18, 0, 0, 0)


def require(value, message):
    if not value: raise ValueError(message)


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def member(name):
    p=PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
            and not any(ord(c)<32 for c in name),'Unsafe vendor member')
    return p


def download(row, cache):
    cache.mkdir(parents=True,exist_ok=True)
    target=cache/row['name']
    if target.exists():
        require(not target.is_symlink() and digest(target)==row['sha256'],'Cached vendor input differs: '+target.name)
        return target
    require(row['url'].startswith('https://'),'Vendor source must use HTTPS')
    temp=cache/(row['name']+'.partial')
    try:
        req=urllib.request.Request(row['url'],headers={'User-Agent':'Codex-Agent-System-runtime-builder'})
        with urllib.request.urlopen(req,timeout=120) as src,temp.open('xb') as dst:
            total=0
            while b:=src.read(1024*1024):
                total+=len(b);require(total<=256*1024*1024,'Vendor archive exceeds limit');dst.write(b)
        require(digest(temp)==row['sha256'],'Vendor archive digest mismatch: '+target.name)
        if 'size' in row:require(temp.stat().st_size==row['size'],'Vendor archive size mismatch')
        os.replace(temp,target)
    finally:temp.unlink(missing_ok=True)
    return target


def node_archive(archive, output, row):
    prefix='node-v'+row['version']+'-'+('win' if '-win-' in row['name'] else 'darwin' if '-darwin-' in row['name'] else 'linux')+'-'+('arm64' if '-arm64.' in row['name'] else 'x64')+'/'
    wanted={'node.exe' if row['name'].endswith('.zip') else 'bin/node','LICENSE'}
    found=set()
    def put(name,reader):
        require(name not in found,'Duplicate Node member');found.add(name)
        to=output/'node'/name;to.parent.mkdir(parents=True,exist_ok=True)
        with to.open('xb') as dst:shutil.copyfileobj(reader,dst,128*1024)
        to.chmod(0o755 if name!='LICENSE' else 0o644)
    if archive.suffix=='.zip':
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():
                member(m.filename)
                require(m.filename.startswith(prefix),'Unexpected Node namespace')
                name=m.filename[len(prefix):]
                if name in wanted:
                    require(not m.is_dir() and m.file_size<=256*1024*1024,'Invalid Node member')
                    with z.open(m) as r:put(name,r)
    else:
        with tarfile.open(archive,'r:*') as z:
            for m in z:
                member(m.name)
                if m.name.rstrip('/')==prefix.rstrip('/'):continue
                require(m.name.startswith(prefix),'Unexpected Node namespace')
                name=m.name[len(prefix):]
                if name in wanted:
                    require(m.isfile() and m.size<=256*1024*1024,'Invalid Node member')
                    with z.extractfile(m) as r:put(name,r)
    require(found==wanted,'Node executable/license missing')


def python_archive(archive, output):
    """Materialize only reviewed in-namespace links; no links enter a buyer ZIP."""
    links={};total=0;count=0
    with tarfile.open(archive,'r:gz') as z:
        for m in z:
            p=member(m.name);require(p.parts[0]=='python','Unexpected Python namespace')
            count+=1;require(count<=30000,'Python member limit exceeded')
            target=output/p
            if m.isdir():target.mkdir(parents=True,exist_ok=True);continue
            if m.issym() or m.islnk():
                raw=m.linkname
                require(not PurePosixPath(raw).is_absolute() and '\\' not in raw,'Unsafe Python link')
                joined=posixpath.normpath(posixpath.join(posixpath.dirname(m.name),raw)) if m.issym() else posixpath.normpath(raw)
                resolved=member(joined);require(resolved.parts[0]=='python','Python link escapes namespace')
                links[m.name]=resolved.as_posix();continue
            require(m.isfile() and m.size<=256*1024*1024,'Unexpected special Python member')
            total+=m.size;require(total<=512*1024*1024,'Python archive expands beyond limit')
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.extractfile(m) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,128*1024)
            target.chmod(0o755 if m.mode&0o111 else 0o644)
    def resolve(name,seen=()):
        require(name not in seen and len(seen)<16,'Cyclic Python link')
        return resolve(links[name],(*seen,name)) if name in links else output/member(name)
    for name in sorted(links):
        source=resolve(name);require(source.exists(),'Missing Python link target')
        target=output/member(name);target.parent.mkdir(parents=True,exist_ok=True)
        if source.is_dir():
            require(not target.exists(),'Duplicate Python directory alias')
            shutil.copytree(source,target)
        else:
            require(source.is_file() and not target.exists(),'Invalid Python file alias')
            with source.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,128*1024)
            target.chmod(stat.S_IMODE(source.stat().st_mode))
    require(any('license' in p.name.lower() for p in (output/'python').rglob('*') if p.is_file()),'Python licenses missing')


def add_yaml(archive, output, target, version):
    site=output/'python'/('Lib/site-packages' if target.startswith('win32-') else 'lib/python3.13/site-packages')
    found=0;license_bytes=None;metadata=None
    with tarfile.open(archive,'r:gz') as z:
        for m in z:
            p=member(m.name)
            require(m.isfile() or m.isdir(),'Unexpected PyYAML archive link')
            if not m.isfile():continue
            parts=p.parts[1:]
            if parts[:2]==('lib','yaml'):
                rel=PurePosixPath(*parts[1:]);to=site/rel;to.parent.mkdir(parents=True,exist_ok=True)
                with z.extractfile(m) as src,to.open('xb') as dst:shutil.copyfileobj(src,dst)
                to.chmod(0o644);found+=1
            elif len(parts)==1 and parts[0].upper()=='LICENSE':license_bytes=z.extractfile(m).read()
            elif len(parts)==1 and parts[0]=='PKG-INFO':metadata=z.extractfile(m).read()
    require(found>=10 and license_bytes and b'Permission' in license_bytes,'Incomplete PyYAML source/license')
    info=site/('pyyaml-'+version+'.dist-info');info.mkdir(parents=True,exist_ok=True)
    (info/'LICENSE').write_bytes(license_bytes)
    if metadata:(info/'METADATA').write_bytes(metadata)


def zip_tree(directory, output, modes=None):
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(directory.rglob('*')):
            if not p.is_file():continue
            require(not p.is_symlink(),'Linked runtime output')
            info=zipfile.ZipInfo(directory.name+'/'+p.relative_to(directory).as_posix(),EPOCH)
            mode=(modes or {}).get(p.relative_to(directory).as_posix(),0o644)
            info.create_system=3;info.external_attr=(stat.S_IFREG|mode)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def stage(root, target, cache, output, *, allow_dirty=False, verify_signature=False):
    root=root.resolve();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=root))
    require(allow_dirty or not dirty,'Commit reviewed sources before building a release runtime')
    lock_path=root/'commercial/runtime/portable-sources.json';lock=json.loads(lock_path.read_text());row=lock['targets'][target]
    n=download(row['node'],cache);p=download(row['python'],cache);y=download(lock['pyyaml'],cache)
    signature={'verification':'archive SHA matches reviewed source lock; upstream signature not executed on this runner'}
    if verify_signature:
        np=lock['node_provenance']
        sums=download({'name':'SHASUMS256.txt.asc','url':np['official_release']+'SHASUMS256.txt.asc','sha256':np['signed_checksums_sha256']},cache)
        keys=download({'name':'nodejs-keyring.kbx','url':np['keyring']['source'],'sha256':np['keyring']['sha256']},cache)
        spec=importlib.util.spec_from_file_location('runtime_node_verifier',root/'scripts/build_workbench_runtime.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        proof={**np,'archives':{target:row['node']}}
        signature=module.verify_node(n,sums,keys,proof,target)
    output.mkdir(parents=True,exist_ok=True);directory=output/target
    require(not directory.exists(),'Choose fresh runtime output directory')
    directory.mkdir();node_archive(n,directory,row['node']);python_archive(p,directory);add_yaml(y,directory,target,lock['pyyaml']['version'])
    if target.startswith('win32-'):
        exe=directory/row['python']['executable'];require(exe.is_file(),'Expected native Python executable missing')
        alias=directory/'python/python3.exe'
        if not alias.exists():
            with exe.open('rb') as src,alias.open('xb') as dst:shutil.copyfileobj(src,dst,128*1024)
            alias.chmod(0o755)
    for kind in ('node','python'):require((directory/row[kind]['executable']).is_file(),'Missing '+kind+' executable')
    # NTFS does not expose POSIX execute bits. Preserve a canonical public-file
    # inventory independently of the build host's umask or chmod emulation.
    modes={f.relative_to(directory).as_posix():
           (0o755 if f.suffix.lower()=='.exe' else 0o644) if target.startswith('win32-')
           else (0o755 if f.stat().st_mode&0o111 else 0o644)
           for f in directory.rglob('*') if f.is_file()}
    inventory={f.relative_to(directory).as_posix():{'sha256':digest(f),'size':f.stat().st_size,'mode':modes[f.relative_to(directory).as_posix()]} for f in sorted(directory.rglob('*')) if f.is_file()}
    desc={'schema':SCHEMA,'target':target,'os':row['os'],'arch':row['arch'],'source_commit':source,'source_clean':not dirty,'input_lock_sha256':digest(lock_path),'node':row['node'],'python':row['python'],'pyyaml':lock['pyyaml'],'node_signature':signature,'files':inventory,'runtime_execution':'unverified until the exact target package executes on a native runner','link_policy':'upstream in-namespace symlinks materialized; no links distributed','windows_python3_alias':'same official python.exe bytes' if target.startswith('win32-') else None}
    (directory/'runtime.json').write_text(json.dumps(desc,indent=2,sort_keys=True)+'\n',encoding='utf8')
    archive=output/('runtime-'+target+'.zip');zip_tree(directory,archive,modes)
    receipt={'schema':SCHEMA,'target':target,'source_commit':source,'source_clean':not dirty,'input_lock_sha256':desc['input_lock_sha256'],'archive':str(archive),'sha256':digest(archive),'size':archive.stat().st_size,'files':len(inventory),'node_executable':target+'/'+row['node']['executable'],'python_executable':target+'/'+row['python']['executable']}
    (output/('runtime-'+target+'.build.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--target',required=True);p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-dirty',action='store_true');p.add_argument('--verify-node-signature',action='store_true');a=p.parse_args()
    try:print(json.dumps(stage(a.root,a.target,a.cache,a.output,allow_dirty=a.allow_dirty,verify_signature=a.verify_node_signature),indent=2));return 0
    except (OSError,ValueError,KeyError,subprocess.SubprocessError,tarfile.TarError,zipfile.BadZipFile) as e:print(json.dumps({'status':'blocked','reason':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
