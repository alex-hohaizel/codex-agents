#!/usr/bin/env python3
"""Check the source contract for commercial release candidates, without publishing."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

def check(root):
    errors=[]
    def require(value,message):
        if not value:errors.append(message)
    def load(rel):return json.loads((root/rel).read_text())
    try:
        release=load('releases/current.json')
        product=load('commercial/product.json')
        offer=load('commercial/offer.json')
        registry=load('governance/commercial/requirements.json')
        text=(root/'governance/COMMERCIAL_PRODUCT_CONTRACT.uk.md').read_bytes()
        require(hashlib.sha256(text).hexdigest()==registry['contract_sha256'],'Original commercial contract drift')
        rows=registry['requirements']
        found=[r['id'] for r in rows]
        require(len(found)==len(set(found)),'Duplicate commercial requirement ID')
        require({f'C{i:02d}' for i in range(1,29)}<=set(found),'Missing C01–C28 acceptance scenarios')
        original=text.decode().splitlines()
        for r in rows:
            s=r['source']
            require(s['text']==original[s['line']-1],r['id']+': broken literal contract link')
            require(r.get('implementation') and r.get('verification'),r['id']+': missing implementation or verification route')
        require(product['product_id']==offer['product_id']=='codex-agent-system','Product ID mismatch')
        require(product['release_record']=='releases/current.json','Commercial version must derive from existing release record')
        require(offer['editions']['solo']['price_minor']==4900 and offer['editions']['team']['price_minor']==14900,'Owner draft price assumptions changed')
        require(offer['editions']['solo']['named_seats']==1 and offer['editions']['team']['named_seats']==5,'Edition seat assumptions changed')
        for ed in offer['editions'].values():
            require(ed['use_right']=='perpetual-purchased-product-major' and ed['included_updates']=='purchased-product-major','Acquired-major rights changed')
        required=('commercial/legal/LICENSE.txt','commercial/legal/THIRD_PARTY_NOTICES.txt','commercial/setup/setup.py',
                  'commercial/fulfillment.py','commercial/verify_distribution.py','scripts/build_commercial.py',
                  'scripts/build_workbench_runtime.py','docs/commercial/BUYER_GUIDE.md','docs/commercial/BUYER_GUIDE.uk.md')
        for rel in required:require((root/rel).is_file(),'Missing commercial surface: '+rel)
        for loc in ('en','uk'):
            for name in ('start','sales'):
                p=root/f'commercial/site/{name}-{loc}.html'
                require(p.is_file(),'Missing buyer locale: '+str(p))
                if p.exists():
                    raw=p.read_text()
                    require(f'lang="{loc}"' in raw and release['repository_version'] in raw and offer['license_version'] in raw,'Stale buyer page: '+str(p))
        for channel in ('agensi','promptbase'):
            path=root/f'commercial/channels/{channel}/SKILL.md'
            require(path.is_file(),'Missing bounded channel skill')
            if path.exists():
                raw=path.read_text()
                require(len(raw)<=5000 and raw.startswith('---\n') and 'name:' in raw and 'description:' in raw,'Single-file export contract failed')
        for path,needle in [('AGENTS.md','COMMERCIAL_PRODUCT_CONTRACT'),('governance/UPDATE_CONTRACT.md','commercial'),
            ('governance/PACKAGES.md','commercial'),('governance/VALIDATION.md','commercial'),
            ('governance/RELEASE_CHECKLIST.md','Commercial'),('maintenance-skill/SKILL.md','commercial'),
            ('.github/workflows/validate.yml','check_commercial.py')]:
            require(needle in (root/path).read_text(),'Missing commercial rule: '+path)
        require(len(release['stable_skill_names'])==33,'Core scope changed')
        require(not product['recommended_components']['maintenance'],'Owner maintenance cannot be silently installed as buyer capability')
    except (ValueError,KeyError,OSError,IndexError) as exc:errors.append(str(exc))
    return {'schema':'codex-agents.commercial-source-check/1','ok':not errors,'errors':errors,'scope':'source consistency only; buyer-path observations and platform acceptance are separate'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    result=check(a.root.resolve());print(json.dumps(result,indent=2));return 0 if result['ok'] else 2
if __name__=='__main__':sys.exit(main())
