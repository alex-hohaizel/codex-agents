#!/usr/bin/env python3
"""Verify a signed release index against a separately trusted key before staging."""
import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

LIMIT=1024*1024*1024

def need(ok,message):
    if not ok: raise ValueError(message)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(128*1024),b''):h.update(b)
    return h.hexdigest()

def snapshot(source, target, limit):
    source=source.absolute()
    need(not any(platform_support.is_link_or_reparse(p) for p in (source,*source.parents)), "Linked trust source rejected")
    fd=os.open(source,os.O_RDONLY|getattr(os,"O_NOFOLLOW",0))
    try:
        info=os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=limit,"Invalid trust source")
        with os.fdopen(fd,"rb",closefd=False) as stream,target.open("xb") as dest:
            copied=0
            for block in iter(lambda:stream.read(128*1024),b""):
                copied+=len(block)
                need(copied<=limit,"Trust snapshot exceeds bound")
                dest.write(block)
        need(copied==info.st_size,"Trust source changed while reading")
    finally:
        os.close(fd)


def stage(archive,index,signature,key,expected,output,openssl):
    output=output.absolute()
    need(not any(platform_support.is_link_or_reparse(p) for p in (output,*output.parents)),"Linked staging path rejected")
    need(not output.exists(),"Choose a new staging directory")
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".trust-snapshot-",dir=output.parent) as private:
        root=Path(private)
        snaps=[]
        for name,source,limit in (("archive.zip",archive,LIMIT),("BUILD.json",index,1024*1024),("BUILD.sig",signature,8192),("public.pem",key,8192)):
            target=root/name
            snapshot(source,target,limit)
            snaps.append(target)
        return stage_snapshot(*snaps,expected,output,openssl,archive.name)


def stage_snapshot(archive,index,signature,key,expected,output,openssl,original_name):
    need(not output.exists(),"Choose a new staging directory")
    need(all(p.is_file() and not platform_support.is_link_or_reparse(p) for p in (archive,index,signature,key)),"Trust inputs must be regular files")
    need(index.stat().st_size<=1024*1024 and signature.stat().st_size<=8192 and key.stat().st_size<=8192,"Invalid signature inputs")
    verified=subprocess.run([openssl,"pkeyutl","-verify","-pubin","-inkey",str(key),
        "-rawin","-in",str(index),"-sigfile",str(signature)],capture_output=True,timeout=15)
    need(verified.returncode==0,"Signature failed or OpenSSL does not support Ed25519; use supported OpenSSL and the seller-trusted public key")
    obj=json.loads(index.read_text(encoding='utf8'))
    need(obj["schema"]=="codex-agents.commercial-build/1" and obj["source_commit"]==expected,"Unexpected source or release schema")
    candidates=[a for a in obj["files"] if a["name"]==original_name]
    need(len(candidates)==1 and archive.stat().st_size<=LIMIT,"Archive not selected by the trusted index")
    selected=candidates[0]
    need(selected["size"]==archive.stat().st_size and selected["sha256"]==sha(archive),"Downloaded archive digest does not match authenticated release")
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".commercial-stage-",dir=output.parent) as temp:
        root=Path(temp)
        with zipfile.ZipFile(archive) as z:
            names=set();expanded=0
            for entry in z.infolist():
                raw=entry.filename;platform_support.safe_relative(raw);p=PurePosixPath(raw)
                need(not p.is_absolute() and '..' not in p.parts and '\\' not in raw and str(p)==raw and '\0' not in raw,"Unsafe archive path")
                need(raw.casefold() not in names,"Duplicate archive path");names.add(raw.casefold())
                kind=(entry.external_attr>>16)&0o170000
                need(kind in (0,stat.S_IFREG) and not entry.is_dir(),"Archive contains nonregular object")
                expanded+=entry.file_size
                need(expanded<=4*LIMIT and entry.file_size<=256*1024*1024 and len(names)<=65000,"Archive limits exceeded")
                target=root/p
                target.parent.mkdir(parents=True,exist_ok=True)
                with z.open(entry) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,128*1024)
                platform_support.set_mode(target,(entry.external_attr>>16)&0o777 or 0o644)
        top=list(root.iterdir())
        need(len(top)==1 and top[0].is_dir(),"Expected one product root")
        manifest=json.loads((top[0]/"product-manifest.json").read_text(encoding="utf8"))
        need(manifest["schema"]=="codex-agents.commercial-package/1" and
             manifest["source_commit"]==expected and manifest["product_id"]==obj["product_id"] and
             manifest["product_version"]==obj["product_version"]==selected["product_version"] and
             manifest["edition"]==selected["edition"],"Package identity conflicts with authenticated index")
        expected_files=manifest["files"]
        actual={p.relative_to(top[0]).as_posix() for p in top[0].rglob('*') if p.is_file()}
        need(actual==set(expected_files)|{"product-manifest.json","SHA256SUMS"},"Package inventory mismatch")
        for rel,record in expected_files.items():
            platform_support.safe_relative(rel)
            p=PurePosixPath(rel)
            need(not p.is_absolute() and '..' not in p.parts and str(p)==rel and '\\' not in rel,"Unsafe inventory path")
            file=top[0]/p
            need(file.stat().st_size==record["size"] and sha(file)==record["sha256"] and platform_support.mode_matches(file,record["mode"]),"Package member differs: "+rel)
        os.replace(top[0],output)
    return {"status":"signature-and-inventory-verified","source_commit":expected,"package":str(output),"edition":selected["edition"],"archive_sha256":selected["sha256"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','index','signature','public-key','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--expected-source',required=True);p.add_argument('--openssl',default='openssl')
    a=p.parse_args()
    try:
        print(json.dumps(stage(a.archive,a.index,a.signature,a.public_key,a.expected_source,a.output,a.openssl),indent=2));return 0
    except (OSError,ValueError,KeyError,subprocess.SubprocessError,zipfile.BadZipFile) as e:
        print(json.dumps({"status":"blocked","reason":str(e)}),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
