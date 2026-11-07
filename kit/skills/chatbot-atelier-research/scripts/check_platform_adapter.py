#!/usr/bin/env python3
"""Check current channel adapter declarations; not provider/runtime proof."""
import argparse
import json
from pathlib import Path
import re

PLATFORMS={'telegram','instagram','slack','discord','whatsapp','teams','web','other'}
MODES={'telegram':{'webhook','polling'},'instagram':{'webhook'},'slack':{'events_webhook','socket_mode'},'discord':{'interactions_webhook','gateway'},'whatsapp':{'webhook'},'teams':{'webhook'},'web':{'http_api','browser_session','webhook','realtime'}}
STATUS={'candidate','catalog_verified','configured','exercised','unsupported'}
PROOFS={'provider_accepted','delivered','read','observed_in_client'}


def _validate(data):
    errors=[]
    def need(ok,message):
        if not ok:errors.append(message)
        return bool(ok)
    def nonempty(x):return isinstance(x,str) and bool(x.strip())
    if not isinstance(data,dict):return ['adapter must be object']
    def secret_walk(value):
        if isinstance(value,dict):
            for k,v in value.items():
                need(k not in {'access_token','bot_token','client_secret','signing_secret','credential_value'},'secret values forbidden; use credential_selector')
                secret_walk(v)
        elif isinstance(value,list):
            for v in value:secret_walk(v)
    secret_walk(data)
    need(data.get('schema_version')=='chatbot.adapter/1','unsupported adapter format; use chatbot.adapter/1')
    maturity=data.get('maturity');need(maturity in {'draft','specified','exercised'},'invalid adapter maturity')
    strict=maturity in {'specified','exercised'}
    platform=data.get('platform');need(platform in PLATFORMS,'unknown platform; ambiguous name must be clarified')
    if not strict:return errors
    for key in ['id','official_documentation','api_version','environment','account_eligibility','selected_channel','audience','identity_rule','authorization_rule','revocation_rule']:
        need(nonempty(data.get(key)),'missing '+key)
    ingress=data.get('ingress',{});egress=data.get('egress',{})
    if not isinstance(ingress,dict):errors.append('ingress must be object');ingress={}
    if not isinstance(egress,dict):errors.append('egress must be object');egress={}
    mode=ingress.get('mode');need(nonempty(mode),'ingress.mode required')
    if platform in MODES:need(mode in MODES[platform],'ingress mode not declared for selected platform')
    for key in ['verification','dedupe_key_rule','durable_boundary','retry_reconcile','expiry_rule']:
        need(nonempty(ingress.get(key)),'ingress missing '+key)
    need(isinstance(ingress.get('ack_required'),bool),'ingress ack_required must be boolean')
    if ingress.get('ack_required') is True:
        deadline=ingress.get('ack_deadline_ms')
        need(isinstance(deadline,int) and not isinstance(deadline,bool) and deadline>0,'positive current ack_deadline_ms required')
        need(nonempty(ingress.get('deadline_source')),'ack deadline official source required')
    for key in ['operation','audience_resolution','idempotency_rule','uncertain_outcome','policy_check','rate_limit_policy']:
        need(nonempty(egress.get(key)),'egress missing '+key)
    claims=egress.get('claim_levels',[])
    need(isinstance(claims,list) and bool(claims) and all(x in PROOFS for x in claims) and len(set(claims))==len(claims),'egress claim_levels must name unique actual proof levels')
    proof_map=egress.get('proof_rules',{})
    need(isinstance(proof_map,dict) and all(nonempty(proof_map.get(x)) for x in claims),'each delivery claim needs a distinct observation rule')
    if 'delivered' in claims and isinstance(proof_map,dict):need(proof_map.get('delivered')!=proof_map.get('provider_accepted'),'provider acceptance is not delivery')
    capabilities=data.get('capabilities')
    if not need(isinstance(capabilities,list) and bool(capabilities),'capabilities required'):capabilities=[]
    ids=[]
    for index,c in enumerate(capabilities):
        if not isinstance(c,dict):errors.append('capability must be object');continue
        ids.append(c.get('id'))
        for key in ['id','operation','tool_source','status','permissions','parameter_consumption_check','fallback']:
            need(bool(c.get(key)),'capability missing '+key)
        permissions=c.get('permissions')
        need(isinstance(permissions,list) and bool(permissions) and all(nonempty(x) for x in permissions),'capability permissions must name nonempty permission list')
        need(c.get('status') in STATUS,'invalid capability status')
        need(c.get('tool_source') in {'official_api','official_mcp','connector','sdk','browser','custom'},'unknown capability tool source')
        if c.get('tool_source') in {'official_mcp','connector'}:
            need(nonempty(c.get('tool_catalog_ref')) and nonempty(c.get('catalog_checked_at')),'MCP/connector requires actual current catalog record')
            need(c.get('status')!='exercised' or bool(c.get('evidence_ids')),'MCP advertised is not exercised')
        if c.get('status')=='exercised':need(bool(c.get('evidence_ids')),'exercised capability needs evidence')
        if 'evidence_ids' in c:
            refs=c['evidence_ids']
            need(isinstance(refs,list) and all(nonempty(x) for x in refs) and len(refs)==len(set(refs)),
                 'capability evidence_ids must be unique string list')
    need(all(nonempty(x) for x in ids) and len(set(ids))==len(ids),'capability ids must be unique')
    evidence=data.get('evidence',[])
    if not isinstance(evidence,list):errors.append('evidence must be array');evidence=[]
    evidence_ids=[x.get('id') for x in evidence if isinstance(x,dict)]
    valid_ids=all(nonempty(x) for x in evidence_ids)
    need(valid_ids and len(evidence_ids)==len(evidence) and len(set(evidence_ids))==len(evidence_ids),
         'adapter evidence ids must be unique nonempty strings')
    indexed={x['id']:x for x in evidence if isinstance(x,dict) and nonempty(x.get('id'))}
    for c in capabilities:
        if not isinstance(c,dict) or c.get('status')!='exercised':continue
        for eid in c.get('evidence_ids',[]):
            e=indexed.get(eid,{})
            h=e.get('sha256')
            need(e.get('result')=='pass' and e.get('environment')==data.get('environment') and c.get('id') in e.get('capability_ids',[]) and nonempty(e.get('artifact')) and isinstance(h,str) and re.fullmatch('[a-fA-F0-9]{64}',h) is not None,'execution evidence scope/environment/artifact mismatch')
    if maturity=='exercised':
        need(bool(evidence),'exercised adapter needs actual evidence')
        need(any(isinstance(c,dict) and c.get('status')=='exercised' for c in capabilities),'exercised adapter needs exercised operation')
    return errors


def validate(data):
    try:return _validate(data)
    except (TypeError,ValueError,AttributeError,KeyError) as exc:
        return ['malformed typed adapter fields: '+type(exc).__name__]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);a=p.parse_args()
    try:errors=validate(json.loads(a.file.read_text()))
    except (OSError,ValueError,TypeError,AttributeError) as exc:errors=[str(exc)]
    print(json.dumps({'ok':not errors,'errors':errors,'quality_certified':False,'scope':'Current record declarations only; real provider/current policy and observations require evidence.'},ensure_ascii=False,indent=2))
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
