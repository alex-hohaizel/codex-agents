#!/usr/bin/env python3
"""Check universal distribution source invariants; execution evidence is separate."""
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
from installer_entry import public_installer_version,render
from build_installer import LABELS,safe
from build_commercial import ROOTS
from build_packages import COMMON

def check(root):
 errors=[]
 def require(ok,message):
  if not ok:errors.append(message)
 try:
  release=json.loads((root/'releases/current.json').read_text());lock=json.loads((root/'commercial/runtime/portable-sources.json').read_text())
  registry=json.loads((root/'governance/universal-requirements.json').read_text())
  require({r['id'] for r in registry['requirements']}=={f'U{i:02}' for i in range(1,9)},'Universal requirement registry incomplete')
  for row in registry['requirements']:
   for rel in row['implementation']:require((root/rel).exists(),row['id']+': missing implementation '+rel)
  require(set(lock['targets'])==set(LABELS),'Six declared native input locks required')
  for key,row in lock['targets'].items():
   require(key==row['os']+'-'+row['arch'],'Target OS/CPU mismatch')
   for kind in ('node','python'):
    item=row[kind];safe(item['executable']);require(item['executable'].startswith(kind+'/'),'Wrong runtime executable scope')
    require(item['url'].startswith('https://') and re.fullmatch('[a-f0-9]{64}',item['sha256']),'Unpinned vendor input')
  stable=public_installer_version(release)
  require(f'releases/download/v{stable}/Agent-System-{stable}-Universal.zip' in (root/'README.md').read_text(),'Front page must directly download the verified public Universal installer')
  for locale,name in [('en','START_HERE.html'),('uk','ПОЧАТИ.html')]:
   require((root/name).read_bytes()==render(release['repository_version'],locale,download_version=stable).encode(),'Stale installer HTML: '+name)
   require(name in ROOTS and name in COMMON,'Installer HTML missing from source/package closure')
  for rel in ('AGENTS.md','governance/UPDATE_CONTRACT.md','governance/PACKAGES.md','governance/VALIDATION.md','maintenance-skill/SKILL.md'):
   require('UNIVERSAL_INSTALLATION.md' in (root/rel).read_text(),'Missing durable universal rule: '+rel)
  for rel in ('Start.cmd','Start.command','Start.sh','Start-Workbench.cmd','Start-Workbench.command','Start-Workbench.sh','commercial/setup/launch.mjs','commercial/setup/web.mjs','commercial/setup/ui/index.html','commercial/setup/ui/app.mjs','commercial/setup/ui/style.css','scripts/native_installer_acceptance.py','commercial/tests/gui/native-browser.mjs','.github/workflows/universal-installers.yml'):
   require((root/rel).is_file(),'Missing universal surface: '+rel)
  require(json.loads((root/'commercial/offer.json').read_text())['status']=='release-candidate-not-offered-for-sale','Technical release must not start sales')
 except (OSError,KeyError,ValueError) as e:errors.append(str(e))
 return {'schema':'codex-agents.universal-source-check/1','ok':not errors,'errors':errors,'scope':'Source invariants only; actual archive/native/browser/remote evidence remains required'}
if __name__=='__main__':
 result=check(Path(__file__).resolve().parents[1]);print(json.dumps(result,indent=2));raise SystemExit(0 if result['ok'] else 2)
