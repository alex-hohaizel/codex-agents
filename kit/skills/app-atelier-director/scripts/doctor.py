#!/usr/bin/env python3
"""Read-only local toolchain/skill inventory. Does not install, log in, inspect secrets, or probe remote accounts."""
import argparse
import json
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys

TOOLS={'python3':['--version'],'git':['--version'],'node':['--version'],'npm':['--version'],
       'dart':['--version'],'flutter':['--version'],'java':['-version'],'gradle':['--version'],
       'adb':['version'],'xcodebuild':['-version'],'xcrun':['--version'],'swift':['--version'],
       'ffmpeg':['-version'],'pdftotext':['-v']}

def skill_inventory(roots):
    names={};warnings=[]
    for root in roots:
        root=Path(root).expanduser().absolute()
        if root.is_symlink():warnings.append('Symlink skill root skipped: '+str(root));continue
        if not root.is_dir():continue
        candidates=list(root.glob('*/SKILL.md'))
        if (root/'remote-skills').is_dir():candidates+=list((root/'remote-skills').glob('*/SKILL.md'))
        for p in candidates[:10000]:
            if p.is_symlink() or p.parent.is_symlink():continue
            try:
                if p.stat().st_size>1024*1024:continue
                text=p.read_text(encoding='utf-8')
                m=re.search(r'^name:\s*[\"\']?([a-z0-9-]+)[\"\']?\s*$',text,re.M)
                if m and m.group(1).startswith('app-atelier-'):names.setdefault(m.group(1),set()).add(str(p))
            except (OSError,UnicodeError):warnings.append('Unreadable skill: '+str(p))
    records=[{'name':n,'paths':sorted(paths),'duplicate':len(paths)>1} for n,paths in sorted(names.items())]
    return records,warnings

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path)
    parser.add_argument('--skill-root',type=Path,action='append',default=[])
    parser.add_argument('--strict',action='store_true',help='Exit 1 when duplicate App Atelier skills exist; missing platform tools remain reported facts.')
    args=parser.parse_args()
    records=[]
    for name,flags in TOOLS.items():
        path=shutil.which(name);entry={'tool':name,'path':path,'status':'not_found' if not path else 'present_not_invoked'}
        if path:
            try:
                r=subprocess.run([path]+flags,capture_output=True,text=True,timeout=12)
                entry.update(status='verified' if r.returncode==0 else 'present_check_failed',version=(r.stdout or r.stderr).strip()[:512],exit_code=r.returncode)
            except (OSError,subprocess.TimeoutExpired) as e:entry.update(status='present_check_failed',reason=type(e).__name__)
        records.append(entry)
    home=Path.home();roots=args.skill_root or [home/'.agents/skills',home/'.codex/skills']
    if args.project:roots.append(args.project/'.agents/skills')
    skills,warnings=skill_inventory(roots)
    result={'scope':'this local host only','platform':platform.system(),'architecture':platform.machine(),
            'python':platform.python_version(),'tools':records,'app_atelier_skills':skills,'warnings':warnings,
            'accounts_signing_devices':'not_verified','network_services':'not_probed',
            'limitations':'Tool presence/version does not establish SDK completeness, license acceptance, account permissions, signing, device execution, hosting or budget. No secrets or environment dump read.'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if args.strict and any(s['duplicate'] for s in skills) else 0

if __name__=='__main__':raise SystemExit(main())
