#!/usr/bin/env python3
"""Offline checks for current self-contained ChatBot Atelier resources."""
import argparse
import json
from pathlib import Path
import re




def strict_json_loads(raw, **kwargs):
    """Reject ambiguous/nonfinite JSON before hashing, validation or mutation."""
    if len(raw) > 256 * 1024 * 1024:
        raise ValueError("JSON exceeds bounded input limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)
    kwargs.setdefault("object_pairs_hook", unique)
    kwargs.setdefault("parse_constant", finite)
    return json.loads(raw, **kwargs)


def check(root):
    root=Path(root).resolve();errors=[]
    def need(ok,msg):
        if not ok:errors.append(msg)
    skill=root/'SKILL.md'
    if not skill.is_file():return ['SKILL.md missing']
    text=skill.read_text()
    config=strict_json_loads((root/'assets/consistency-contract.json').read_text())
    need(config.get('schema_version')=='skill.consistency/1','unsupported consistency contract')
    checker=config.get('current_checker','')
    need((root/'scripts'/checker).is_file(),'current domain checker missing')
    need(checker in text,'current checker not described in SKILL.md')
    profile=strict_json_loads((root/'assets/team-profile.json').read_text())
    need(profile.get('schema_version')=='chatbot.team-profile/1','current chatbot team profile required')
    need(profile.get('stage')=='chat' and config.get('canonical_stage')=='chat','current chat stage required')
    requirements=strict_json_loads((root/'assets/requirements.json').read_text())['requirements']
    ids=[row['id'] for row in requirements]
    owners=[rid for domain in profile['domains'] for rid in domain['requirement_ids']]
    need(len(ids)==len(set(ids)) and set(ids)==set(owners) and len(owners)==len(set(owners)),'each current criterion needs exactly one domain owner')
    for name in ['team_policy.py','teamctl.py','check_chat_contract.py','check_platform_adapter.py']:
        need((root/'scripts'/name).is_file(),'current helper missing: '+name)
    for doc in [skill,*sorted((root/'references').glob('*.md'))]:
        content=doc.read_text()
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',content):
            ref=match.group(1).split('#',1)[0]
            if not ref or re.match(r'[A-Za-z][A-Za-z0-9+.-]*:',ref):continue
            target=(doc.parent/ref).resolve()
            need((target==root or root in target.parents) and target.exists(),str(doc.relative_to(root))+': missing/external local reference '+ref)
        need('assets/legacy-overlay' not in content,'removed overlay cannot be a current resource')
    for script in re.findall(r'\bscripts/([A-Za-z_][A-Za-z_0-9-]*\.py)\b',text):
        need((root/'scripts'/script).is_file(),'advertised script absent: '+script)
    return errors


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    try:errors=check(a.root)
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:errors=[str(exc)]
    print(json.dumps({'ok':not errors,'errors':errors,'quality_certified':False,'scope':'Current local formats, resources and routes only.'},ensure_ascii=False,indent=2));return bool(errors)


if __name__=='__main__':raise SystemExit(main())
