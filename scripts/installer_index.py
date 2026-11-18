#!/usr/bin/env python3
"""Assemble an exact-commit installer release, separate from legacy BUILD.json."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
from build_commercial import digest,need
from build_installer import LABELS,inspect_ready_zip

def build(root,artifacts,output,require_all=False):
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    need(not subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=root),'Release index requires a clean checkout')
    version=json.loads((root/'releases/current.json').read_text())['repository_version']
    locksha=digest(root/'commercial/runtime/portable-sources.json')
    rows=[];seen=set();receipts=[]
    for receipt in sorted(artifacts.rglob('*.build.json')):
        data=json.loads(receipt.read_text())
        if data.get('schema')!='codex-agents.installer-build/1':continue
        need(data['source_commit']==source and data['source_clean'] is True and data['product_version']==version and data['input_lock_sha256']==locksha,'Mismatched installer build source: '+receipt.name)
        need(len(data['files'])==1,'Expected one installer per build receipt')
        row=data['files'][0];name=row['name']
        need(Path(name).name==name and name not in seen,'Unsafe or duplicate installer name');seen.add(name)
        file=receipt.parent/name
        need(file.is_file() and not file.is_symlink() and file.stat().st_size==row['size'] and digest(file)==row['sha256'],'Installer bytes differ from receipt')
        need(isinstance(row['platforms'],list) and len(set(row['platforms']))==len(row['platforms']) and set(row['platforms'])<=set(LABELS) and len(row['platforms']) in (1,6),'Unexpected platform declaration')
        expected='Universal' if len(row['platforms'])==6 else LABELS[row['platforms'][0]]
        need(name==f'Agent-System-{version}-{expected}.zip','Unexpected installer filename')
        inspect_ready_zip(file,source,version,row['platforms'],locksha)
        rows.append((file,row));receipts.append(receipt)
    expected={f'Agent-System-{version}-{label}.zip' for label in ['Universal',*LABELS.values()]}
    need(rows and (not require_all or seen==expected),'All seven declared installers are required')
    output.mkdir(parents=True,exist_ok=True)
    for file,row in rows:
        dest=output/row['name']
        need(not dest.exists(),'Release output already exists')
        shutil.copyfile(file,dest);need(digest(dest)==row['sha256'],'Release copy changed')
    result={'schema':'codex-agents.installer-release/1','product_version':version,'source_commit':source,'source_clean':True,'input_lock_sha256':locksha,'files':[r for _,r in rows],'entry_point':'START_HERE.html','trust':'Verify GitHub artifact attestations for this exact repository and main workflow; SHA alone is not independent authenticity.','commercial_sale':'Not launched; edition terms remain separate owner-review drafts.'}
    (output/'INSTALLER-BUILD.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    (output/'INSTALLER-SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['name']+'\n' for _,r in rows)+digest(output/'INSTALLER-BUILD.json')+'  INSTALLER-BUILD.json\n',encoding='utf8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--artifacts-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--require-all',action='store_true');a=p.parse_args()
    try:print(json.dumps(build(a.root.resolve(),a.artifacts_dir.resolve(),a.output.resolve(),a.require_all),indent=2));return 0
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:print(json.dumps({'status':'blocked','reason':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
