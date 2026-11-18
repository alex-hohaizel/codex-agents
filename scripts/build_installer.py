#!/usr/bin/env python3
"""Build self-contained installers, preserving the canonical buyer/setup engine."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
sys.dont_write_bytecode=True
from build_commercial import prepare_buyer_stage, digest, read, need
from build_workbench_runtime import copy_compiled_client, dependencies_notices
from installer_entry import render
from platform_support import safe_relative

LABELS={'darwin-arm64':'macOS-arm64','darwin-x64':'macOS-x64','win32-arm64':'Windows-arm64','win32-x64':'Windows-x64','linux-arm64':'Linux-arm64','linux-x64':'Linux-x64'}
EPOCH=(2026,11,18,0,0,0)

def git_modes(root):
    result={}
    for row in subprocess.check_output(['git','ls-files','--stage','-z'],cwd=root).split(b'\0'):
        if not row:continue
        meta,name=row.split(b'\t',1);mode,_,stage=meta.split()
        need(stage==b'0' and mode in (b'100644',b'100755'),'Unmerged or linked source')
        result[name.decode('utf8')]=0o755 if mode==b'100755' else 0o644
    return result

def safe(name):
    safe_relative(name)
    p=PurePosixPath(name)
    need(name and p.as_posix()==name and not p.is_absolute() and not {'.','..'}.intersection(p.parts) and '\\' not in name and ':' not in name and not any(ord(c)<32 for c in name),'Unsafe runtime archive member')
    return p

def runtime_input(archive,source,locksha,allow_dirty):
    need(archive.is_file() and not archive.is_symlink(),'Runtime must be a regular ZIP')
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist();need(len(infos)<=30000,'Runtime file limit exceeded')
        names=[m.filename for m in infos];need(len({n.casefold() for n in names})==len(names),'Duplicate or case-colliding runtime members')
        descriptors=[n for n in names if n.count('/')==1 and n.endswith('/runtime.json')]
        need(len(descriptors)==1,'Expected one runtime descriptor')
        info=z.getinfo(descriptors[0]);need(info.file_size<16*1024*1024,'Oversized runtime descriptor')
        desc=json.loads(z.read(info));key=desc.get('target')
        need(key in LABELS and descriptors[0]==key+'/runtime.json','Runtime platform mismatch')
        need(key==str(desc.get('os'))+'-'+str(desc.get('arch')),'Runtime target, OS or architecture disagree')
        need(desc['schema']=='codex-agents.portable-runtime/1' and desc['source_commit']==source and desc['input_lock_sha256']==locksha,'Runtime differs from source or input lock')
        terminfo=desc.get('terminfo_dirs',[])
        need(isinstance(terminfo,list) and len(terminfo)==len(set(terminfo)) and all(
             re.fullmatch(r'python/share/terminfo(?:-extra(?:[2-9]|[1-9][0-9]+)?)?',name)
             and any(path.startswith(name+'/') for path in desc['files']) for name in terminfo),'Invalid portable terminfo search layers')
        need(type(desc['source_clean']) is bool and (allow_dirty or desc['source_clean']),'Uncommitted runtime cannot be distributed')
        expected={key+'/'+n for n in desc['files']}|{key+'/runtime.json'}
        need(set(names)==expected,'Runtime inventory mismatch')
        for kind in ('node','python'):
            executable=desc[kind]['executable'];safe(executable)
            need(executable.startswith(kind+'/') and executable in desc['files'] and desc['files'][executable]['mode']==0o755,'Missing or unsafe runtime executable')
        total=0
        for m in infos:
            safe(m.filename);mode=(m.external_attr>>16)&0xffff
            need(stat.S_IFMT(mode) in (0,stat.S_IFREG) and m.file_size<=256*1024*1024,'Linked or oversized runtime member')
            total+=m.file_size;need(total<=1024*1024*1024,'Runtime expands beyond limit')
            if m.filename==descriptors[0]:continue
            row=desc['files'][m.filename[len(key)+1:]]
            need(row['mode'] in (0o644,0o755) and m.file_size==row['size'] and stat.S_IMODE(mode)==row['mode'],'Runtime size or mode mismatch')
            with z.open(m) as f:
                h=hashlib.sha256()
                for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            need(h.hexdigest()==row['sha256'],'Runtime digest mismatch')
    return desc

def install_runtime(archive,desc,stage,modes):
    key=desc['target']
    with zipfile.ZipFile(archive) as z:
        for m in z.infolist():
            rel=PurePosixPath('runtimes')/safe(m.filename);to=stage/rel
            to.parent.mkdir(parents=True,exist_ok=True)
            with z.open(m) as src,to.open('xb') as dst:shutil.copyfileobj(src,dst,128*1024)
            mode=desc['files'].get(m.filename[len(key)+1:],{}).get('mode',0o644)
            to.chmod(mode);modes[rel.as_posix()]=mode

def archive(stage,destination,modes):
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(stage).as_posix();need(not p.is_symlink(),'Linked staged output')
            info=zipfile.ZipInfo(stage.name+'/'+rel,EPOCH);info.create_system=3
            info.external_attr=(stat.S_IFREG|modes.get(rel,0o644))<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            with z.open(info,'w',force_zip64=True) as out,p.open('rb') as src:shutil.copyfileobj(src,out,1024*1024)

def inspect_ready_zip(file,source,version,platforms,locksha):
    """Bind actual archive contents to the release index, independently of receipts."""
    with zipfile.ZipFile(file) as z:
        infos=z.infolist();names=[m.filename for m in infos]
        need(0<len(names)<=65000 and len({n.casefold() for n in names})==len(names),'Duplicate or oversized ready archive inventory')
        descriptors=[m for m in infos if m.filename.count('/')==1 and m.filename.endswith('/product-manifest.json')]
        need(len(descriptors)==1 and descriptors[0].file_size<=16*1024*1024,'Expected one bounded product manifest')
        desc=json.loads(z.read(descriptors[0]));prefix=descriptors[0].filename.split('/')[0]+'/'
        need(desc['schema']=='codex-agents.commercial-package/1' and desc['product_id']=='codex-agent-system'
             and desc['source_commit']==source and desc['source_clean'] is True and desc['product_version']==version
             and desc['edition']=='unassigned','Installer manifest identity differs from release index')
        need(set(desc['portable_runtimes'])==set(platforms) and all(row['input_lock_sha256']==locksha for row in desc['portable_runtimes'].values()),'Installer native platforms differ from index')
        expected={prefix+n for n in desc['files']}|{prefix+'product-manifest.json',prefix+'SHA256SUMS'}
        need(set(names)==expected,'Ready archive inventory differs from manifest')
        total=0
        for m in infos:
            safe(m.filename);mode=(m.external_attr>>16)&0xffff
            need(stat.S_IFMT(mode) in (0,stat.S_IFREG) and m.file_size<=256*1024*1024,'Linked or oversized ready archive member')
            total+=m.file_size;need(total<=4*1024*1024*1024,'Ready archive expansion limit exceeded')
            rel=m.filename[len(prefix):]
            if rel in ('product-manifest.json','SHA256SUMS'):continue
            row=desc['files'][rel]
            need(type(row['size']) is int and m.file_size==row['size'] and row['mode'] in (0o644,0o755) and stat.S_IMODE(mode)==row['mode'],'Ready member size or mode differs')
            with z.open(m) as f:
                h=hashlib.sha256()
                for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            need(h.hexdigest()==row['sha256'],'Ready member digest differs')
    return desc

def build(root,output,runtime_bundles,*,allow_dirty=False,edition='unassigned'):
    root=root.resolve();output=output.resolve()
    need(not output.is_relative_to(root),'Output must be outside source')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=root))
    need(allow_dirty or not dirty,'Commit reviewed sources before building a distributable')
    release=read(root/'releases/current.json');offer=read(root/'commercial/offer.json')
    version=release['repository_version'];tracked=git_modes(root)
    need(edition in ('unassigned','solo','team'),'Unknown distribution edition')
    locksha=digest(root/'commercial/runtime/portable-sources.json')
    selected=[(a,runtime_input(a,source,locksha,allow_dirty)) for a in runtime_bundles]
    keys=[d['target'] for _,d in selected]
    need(len(keys)==len(set(keys)) and len(keys) in (1,6),'Supply one platform, or all six for Universal')
    label='Universal' if len(keys)==6 else LABELS[keys[0]]
    name=f'Agent-System-{version}-'+('' if edition=='unassigned' else edition+'-')+label;output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='agent-installer-stage-') as temp:
        stage=Path(temp)/name
        m=prepare_buyer_stage(root,stage,release,offer,source,edition)
        modes={}
        for p in stage.rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(stage).as_posix();original=rel[len('product/'):] if rel.startswith('product/') else 'commercial/setup/'+rel[len('setup/'):] if rel.startswith('setup/') else rel
            modes[rel]=tracked.get(original,0o644)
        portable={}
        for file,desc in selected:
            install_runtime(file,desc,stage,modes);key=desc['target']
            portable[key]={'os':desc['os'],'arch':desc['arch'],'node_executable':'runtimes/'+key+'/'+desc['node']['executable'],'python_executable':'runtimes/'+key+'/'+desc['python']['executable'],'runtime_descriptor':'runtimes/'+key+'/runtime.json','input_lock_sha256':locksha,'terminfo_dirs':['runtimes/'+key+'/'+name for name in desc.get('terminfo_dirs',[])]}
        for launcher in ('Start.command','Start.sh','Start.cmd','Start-Workbench.command','Start-Workbench.sh','Start-Workbench.cmd'):
            need(launcher in tracked,'Launcher is not tracked: '+launcher)
            shutil.copyfile(root/launcher,stage/launcher);modes[launcher]=0o644 if launcher.endswith('.cmd') else 0o755
            (stage/launcher).chmod(modes[launcher])
        shutil.copyfile(root/'commercial/runtime/control.mjs',stage/'control.mjs');modes['control.mjs']=0o644
        compiled=copy_compiled_client(root,'apps/agent-atelier/dist/client',stage/'product/apps/agent-atelier/dist/client')
        (stage/'notices').mkdir()
        deps=dependencies_notices(root/'apps/agent-atelier',stage/'notices')
        for locale,filename in [('en','START_HERE.html'),('uk','ПОЧАТИ.html')]:
            (stage/filename).write_text(render(version,locale,True),encoding='utf8',newline='\n')
        (stage/'README.md').write_text('# Codex Agent System '+version+'\n\nOpen START_HERE.html. Windows: Start.cmd; macOS: Start.command; Linux: Start.sh. Python and Node are included. Start-Workbench opens the optional local panel.\n\n[Installation](product/docs/INSTALL.md) · [Buyer guide](docs/commercial/BUYER_GUIDE.md) · [Українська](docs/commercial/BUYER_GUIDE.uk.md) · [Full documentation](product/docs/INDEX.md)\n\nKeep this extracted package intact. Verify the release SHA256 and GitHub attestation before first run. Codex and its account are separate. This technical distribution does not issue a paid entitlement or finalize commercial terms.\n',encoding='utf8',newline='\n')
        m.update(source_clean=not dirty,edition=edition,recommended_setup={'win32':'Start.cmd','darwin':'Start.command','linux':'Start.sh'},portable_runtimes=portable)
        if edition=='unassigned':
            m['build_trust']='Obtain this technical archive through the trusted GitHub Release; verify exact repository/main artifact attestations and INSTALLER-BUILD.json. A checksum from the archive itself is consistency, not independent authenticity.'
        m['components'].update(workbench=release['local_service']['version'],maintenance=next(s['version'] for s in release['optional_skills'] if s['name']=='codex-agents-maintenance'))
        m['runtime']={'status':'included-built-client-and-native-runtimes','entry':'control.mjs','sqlite_schema_max':1,'compiled_client':compiled,'production_dependencies':deps,'execution_evidence':'See exact-commit native acceptance from the release workflow; inclusion alone is not execution proof.'}
        m['distribution']={'kind':'universal' if len(keys)==6 else 'native','platforms':sorted(keys),'rights':'Existing entitlement and license controls remain unchanged. No entitlement is issued by downloading.','product_signing':'Product launchers are unsigned; vendor binary signatures retained where provided. No platform signing or notarization is claimed.'}
        m['files']={}
        for p in sorted(stage.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(stage).as_posix()
            if rel in ('product-manifest.json','SHA256SUMS'):continue
            m['files'][rel]={'sha256':digest(p),'size':p.stat().st_size,'mode':modes.get(rel,0o644)}
        (stage/'product-manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        (stage/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+n+'\n' for n,v in m['files'].items())+digest(stage/'product-manifest.json')+'  product-manifest.json\n',encoding='utf8',newline='\n')
        destination=output/(name+'.zip');archive(stage,destination,modes)
        receipt={'schema':'codex-agents.installer-build/1','product_version':version,'source_commit':source,'source_clean':not dirty,'input_lock_sha256':locksha,'files':[{'name':destination.name,'sha256':digest(destination),'size':destination.stat().st_size,'platforms':sorted(keys),'edition':edition,'product_version':version,'source_commit':source,'entry_point':'START_HERE.html'}],'entry_point':'START_HERE.html','native_execution':'pending separate acceptance of these exact archive bytes','publication_performed':False}
        need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==source,'Source commit changed during build')
        need(allow_dirty or not subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=root),'Source changed during build')
        (output/(name+'.build.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime-bundle',type=Path,action='append',required=True);p.add_argument('--allow-dirty',action='store_true');a=p.parse_args()
    try:print(json.dumps(build(a.root,a.output,a.runtime_bundle,allow_dirty=a.allow_dirty),indent=2));return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,subprocess.SubprocessError) as e:print(json.dumps({'status':'blocked','reason':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
