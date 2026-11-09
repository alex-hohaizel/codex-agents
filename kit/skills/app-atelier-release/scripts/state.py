#!/usr/bin/env python3
"""App Atelier local ledger. Records evidence/authority; never executes a remote action or model."""
import argparse
import contextlib
import copy
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile



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

VERSION = 'app-atelier-state/1'
GROUPS = ('requirement','decision','knowledge','job','artifact','evidence','execution','capability','grant','effect')
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$')
HEX = re.compile(r'^[a-f0-9]{64}$')
LIMIT = 16 * 1024 * 1024
MAX_FILE_BYTES = 512 * 1024 * 1024
DEFAULT_GATES = {'concepts':['direction'], 'specification':['concept'], 'experience':['concept'],
                 'build':['concept','design','budget'], 'support':['concept','design','budget'],
                 'release':['release_readiness','budget'], 'growth_activation':['release_readiness','budget']}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def require(row, *keys):
    need(isinstance(row,dict),'record must be an object')
    for key in keys:
        need(key in row and row[key] is not None and row[key] != '', 'missing field: '+key)

def strings(value):
    need(isinstance(value,list) and all(isinstance(x,str) and x for x in value),'expected string list')
    need(len(set(value))==len(value),'duplicate list values')
    return value

def number(v):
    try:valid=type(v) in (int,float) and math.isfinite(v) and v>=0
    except (OverflowError,TypeError,ValueError):valid=False
    need(valid,'expected finite nonnegative number')
    return v

def phase(value):
    need(isinstance(value,str) and value,'phase must be a nonempty string')
    p=value.lower().replace('_','-')
    if p.startswith('ph-'):p=p[3:]
    need(re.fullmatch(r'[a-z][a-z0-9-]{0,63}',p) is not None,'invalid phase')
    return {'spec':'specification','intake':'intake','growth':'growth_activation','growth-activation':'growth_activation'}.get(p,p)

def normalize_profile(value):
    need(isinstance(value,dict) and value.get('schema_version')=='app-atelier-profile/1','unsupported profile schema')
    p=copy.deepcopy(value);constraints=p.setdefault('constraints',{})
    need(isinstance(constraints,dict),'constraints must be object')
    number(constraints.get('new_external_spend_usd',0));number(constraints.get('recurring_spend_usd',0))
    for key in ('no_human_experiments','owner_operational_work'):
        if key in constraints:need(type(constraints[key]) is bool,key+' must be boolean')
    for key in ('owner_decision_gates','phase_prerequisites'):
        original=p.setdefault(key,{})
        need(isinstance(original,dict),key+' must be object')
        normalized={}
        for raw,items in original.items():
            target=phase(raw);strings(items)
            vals=[phase(x) for x in items] if key=='phase_prerequisites' else items
            normalized.setdefault(target,[])
            for item in vals:
                if item not in normalized[target]:normalized[target].append(item)
        p[key]=normalized
    cycle({k:{'depends_on':v} for k,v in p['phase_prerequisites'].items()})
    need(isinstance(p.get('requirements',[]),list),'profile requirements must be a list')
    seen=set()
    for row in p.get('requirements',[]):
        require(row,'id','intent')
        need(isinstance(row['id'],str) and ID.fullmatch(row['id']) and row['id'] not in seen,'profile requirement IDs must be unique valid IDs')
        seen.add(row['id'])
    return p

def no_symlinks(path):
    path=Path(path).absolute()
    for p in [path]+list(path.parents):
        need(not p.is_symlink(),'symlink forbidden: '+str(p))
    return path

def read_json(path):
    path=no_symlinks(path)
    need(path.is_file() and path.stat().st_size<=LIMIT,'missing/oversize regular JSON: '+str(path))
    with path.open(encoding='utf-8') as f:
        obj=strict_json_loads(f.read(),parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON value')))
    canonical(obj)
    return obj

def file_sha(path):
    path=no_symlinks(path)
    fd=os.open(str(path),os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as f:
        info=os.fstat(f.fileno());need(stat.S_ISREG(info.st_mode) and info.st_size<=MAX_FILE_BYTES,'missing/oversize regular file: '+str(path))
        h=hashlib.sha256()
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def contained(root, name):
    need(isinstance(name,str) and name and '\\' not in name and ':' not in name,'unsafe relative path')
    rel=PurePosixPath(name)
    need(not rel.is_absolute() and '..' not in rel.parts and str(rel)==name,'unsafe relative path')
    return no_symlinks(root.joinpath(*rel.parts))

def atomic(path,obj):
    data=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    need(len(data)<=LIMIT,'ledger exceeds bounded size; archive completed records')
    fd,name=tempfile.mkstemp(prefix='.write-',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.chmod(name,0o600);os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

@contextlib.contextmanager
def locked(root,create=False):
    no_symlinks(root)
    need(root.is_dir(),'project directory must exist')
    folder=root/'.appatelier';no_symlinks(folder)
    if create:folder.mkdir(mode=0o700,exist_ok=True)
    need(folder.is_dir(),'project not initialized')
    lock=no_symlinks(folder/'state.lock')
    fd=os.open(str(lock),os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'r+') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        yield folder

def source(row):
    require(row,'source','verbatim')
    need(isinstance(row['source'],str) and isinstance(row['verbatim'],str),'source/verbatim must be strings')

def authority(value,subject):
    need(isinstance(value,dict),'actual user authority record required')
    source(value)
    need(value.get('actor')=='user','authority actor must be user')
    need(value.get('subject_sha256')==digest(subject),'authority must pin exact current subject')
    need(value.get('decision','approve')=='approve','authority is not positive approval')
    need(not value.get('revoked',False),'authority revoked')

def decision_subject(r):
    subject={k:r[k] for k in ('category','scope','question','options','answer')}
    subject['artifact_hashes']=r.get('artifact_hashes',{})
    for key in ('requirement_ids','job_ids'):
        if key in r:subject[key]=strings(r[key])
    return subject

def execution_subject(r):
    return {'scope':r['scope'],'phase_ids':r['phase_ids']}

def effect_subject(r):
    subject={k:r[k] for k in ('type','scope','target','parameters','artifact_ids','spend_usd','recurring_usd','idempotency_key')}
    hashes=r.get('artifact_hashes',{})
    need(isinstance(hashes,dict) and set(hashes)==set(r['artifact_ids']),'effect subject needs exact artifact_hashes; use subject --kind effect')
    need(all(isinstance(v,str) and HEX.fullmatch(v) for v in hashes.values()),'effect artifact hash required')
    subject['artifact_hashes']=hashes
    return subject

def requirement_definition(r):
    excluded={'status','evidence_ids','change_authority','_profile_sha256','created_at','updated_at','recorded_at'}
    definition={k:copy.deepcopy(v) for k,v in r.items() if k not in excluded}
    for key in ('phase','due_phase','recheck_phase'):
        if key in definition and definition[key] is not None:definition[key]=phase(definition[key])
    return definition

def profile_current(state,folder):
    return file_sha(folder/'profile.json')==state['profile_sha256']

def fresh_artifact(root,r):
    try:return file_sha(contained(root,r['path']))==r['sha256']
    except (ValueError,OSError):return False

def fresh_evidence(root,state,r):
    try:
        if r.get('status')!='pass' or file_sha(contained(root,r['proof_path']))!=r['proof_sha256']:return False
        if set(r.get('artifact_ids',[]))!=set(r.get('artifact_hashes',{})):return False
        for aid,h in r['artifact_hashes'].items():
            a=state['artifact'].get(aid)
            if not a or a['sha256']!=h or not fresh_artifact(root,a):return False
        if r.get('_profile_sha256')!=state['profile_sha256']:return False
        if set(r.get('requirement_ids',[]))!=set(r.get('requirement_hashes',{})):return False
        for rid,h in r.get('requirement_hashes',{}).items():
            requirement=state['requirement'].get(rid)
            if not requirement or digest(requirement_definition(requirement))!=h:return False
        if r.get('independent'):
            for aid in r['artifact_ids']:
                if r['observer'] in state['artifact'][aid]['author_ids']:return False
        return True
    except (KeyError,ValueError,OSError):return False

def evidence_definition(r):
    # Observation time, method, observer, claims and all unknown fields are
    # semantic. Only these controller/profile bookkeeping fields may change
    # without replacing the evidence accepted by a completed job.
    excluded={'_profile_sha256','created_at','updated_at','recorded_at'}
    return {k:copy.deepcopy(v) for k,v in r.items() if k not in excluded}

def completion_proof_blockers(root,state,j,pinned=False):
    reasons=[];artifacts=j.get('artifact_ids',[]);evidences=j.get('evidence_ids',[])
    if not artifacts or not evidences:return ['completion requires actual artifacts and evidence']
    for aid in artifacts:
        if aid not in state['artifact'] or not fresh_artifact(root,state['artifact'][aid]):reasons.append('completion artifact missing/stale: '+aid)
    current=[]
    for eid in evidences:
        e=state['evidence'].get(eid)
        if not e or not fresh_evidence(root,state,e):reasons.append('completion evidence missing/stale: '+eid)
        else:current.append(e)
    covered={aid for e in current for aid in e['artifact_ids']}
    if not set(artifacts)<=covered:reasons.append('evidence does not cover every output')
    if j.get('independent_review_required',True):
        independent_covered={aid for e in current if e.get('independent') and e['observer']!=j['owner'] for aid in e['artifact_ids']}
        if not set(artifacts)<=independent_covered:reasons.append('independent review required for every declared output')
    if pinned:
        hashes=j.get('completion_hashes');proofs=j.get('completion_evidence_hashes')
        if not isinstance(hashes,dict) or set(hashes)!=set(artifacts):reasons.append('completion output snapshot missing/mismatched; reconcile with a repair job')
        elif any(aid not in state['artifact'] or state['artifact'][aid]['sha256']!=h for aid,h in hashes.items()):reasons.append('completion output changed')
        if not isinstance(proofs,dict) or set(proofs)!=set(evidences):reasons.append('completion evidence snapshot missing/mismatched; reconcile with a repair job')
        elif any(eid not in state['evidence'] or digest(evidence_definition(state['evidence'][eid]))!=h for eid,h in proofs.items()):reasons.append('completion evidence record changed')
    return sorted(set(reasons))

def decision_valid(r):
    try:
        need(r.get('status')=='confirmed','decision is not confirmed')
        need(r.get('answer') in r['options'],'answer must be one explicit option')
        authority(r['authority'],decision_subject(r));return True
    except (ValueError,KeyError):return False

def decision_current(root,state,r):
    if not decision_valid(r) or r.get('_profile_sha256')!=state['profile_sha256']:return False
    return all(aid in state['artifact'] and state['artifact'][aid]['sha256']==h and fresh_artifact(root,state['artifact'][aid]) for aid,h in r.get('artifact_hashes',{}).items())

def current_requirement(root,state,r):
    if r.get('status') not in ('complete','closed') or r.get('_profile_sha256')!=state['profile_sha256']:return False
    evidences=r.get('evidence_ids',[])
    if not evidences:return False
    for eid in evidences:
        e=state['evidence'].get(eid)
        if not e or not fresh_evidence(root,state,e) or e.get('requirement_hashes',{}).get(r['id'])!=digest(requirement_definition(r)):return False
    return True

def cycle(group):
    done=set();active=set()
    def visit(k):
        need(k not in active,'cyclic dependency')
        if k in done or k not in group:return
        active.add(k)
        for dep in group[k].get('depends_on',[]):visit(dep)
        active.remove(k);done.add(k)
    for ident in group:visit(ident)

def phase_mapping(state,key):
    result={}
    for raw,items in state['profile'].get(key,{}).items():
        normalized=phase(raw);strings(items);result.setdefault(normalized,[])
        values=[phase(x) for x in items] if key=='phase_prerequisites' else items
        for item in values:
            if item not in result[normalized]:result[normalized].append(item)
    return result

def owner_categories(state,j):
    return set(DEFAULT_GATES.get(j['phase'],[])) | set(phase_mapping(state,'owner_decision_gates').get(j['phase'],[]))

def effect_dependency_current(root,e):
    try:
        if e.get('status') not in ('succeeded','failed'):return False
        receipt=e['receipts'][-1]
        return receipt['outcome']==e['status'] and file_sha(contained(root,receipt['proof_path']))==receipt['proof_sha256']
    except (KeyError,IndexError,ValueError,OSError):return False

def job_requirement_blockers(root,state,j,completion=False):
    """One admission/freshness policy; optional inputs pin definitions, not closure."""
    reasons=[];fulfills=set(j.get('fulfills_requirements',[]));pins=j.get('input_requirement_hashes')
    if completion and j.get('requirement_ids') and not isinstance(pins,dict):
        reasons.append('job input definition snapshot missing; reconcile with a repair job')
    for rid in j.get('requirement_ids',[]):
        r=state['requirement'].get(rid)
        if r is None:
            reasons.append('unknown requirement: '+rid);continue
        if isinstance(pins,dict) and pins.get(rid)!=digest(requirement_definition(r)):
            reasons.append('input requirement definition changed: '+rid)
        required=(rid in fulfills and completion) or (rid not in fulfills and (r.get('priority')=='must' or r.get('emphasis')))
        if required and not current_requirement(root,state,r):reasons.append('required input requirement pending/stale: '+rid)
    return reasons

PROFILE_METADATA_FIELDS={'metadata','annotations','audit_annotation'}

def profile_impact(state,new_profile):
    """Conservative, recorded carry-forward using only explicit native dependencies.

    Unknown fields/constraints have no demonstrated independence and invalidate all.
    Annotation fields are expressly nonoperative. Phase policies and requirements
    have scoped links; unbound decisions on a material requirement change reopen.
    """
    old=state['profile'];keys=set(old)|set(new_profile)
    changed={k for k in keys if canonical(old.get(k))!=canonical(new_profile.get(k))}
    specialized={'requirements','owner_decision_gates','phase_prerequisites'}
    unknown=changed-PROFILE_METADATA_FIELDS-specialized
    invalid={k:set() for k in GROUPS};affected_phases=set()
    old_reqs={r['id']:r for r in old.get('requirements',[])}
    new_reqs={r['id']:r for r in new_profile.get('requirements',[])}
    changed_reqs={rid for rid in set(old_reqs)|set(new_reqs)
                  if digest(requirement_definition(old_reqs.get(rid,{})))!=digest(requirement_definition(new_reqs.get(rid,{})))}
    for key in ('owner_decision_gates','phase_prerequisites'):
        before=old.get(key,{});after=new_profile.get(key,{})
        affected_phases.update(p for p in set(before)|set(after) if before.get(p,[])!=after.get(p,[]))
    policy_phases=set(affected_phases)
    reasons=['unrecognized or global profile fields changed: '+', '.join(sorted(unknown))] if unknown else []
    for rid in changed_reqs:
        rows=[r for r in (state['requirement'].get(rid),old_reqs.get(rid),new_reqs.get(rid)) if r]
        linked=any(rid in j.get('requirement_ids',[]) for j in state['job'].values())
        for r in rows:
            due=r.get('phase',r.get('due_phase'))
            if due:affected_phases.add(phase(due));linked=True
            if r.get('blocks_work'):linked=True
        if not linked:reasons.append('changed requirement has no demonstrated impact boundary: '+rid)
    if reasons:
        for kind in GROUPS:invalid[kind].update(state[kind])
        affected_phases.update(j['phase'] for j in state['job'].values())
        affected_phases.update(state.get('phase_closures',{}))
        mode='conservative_global'
    else:
        mode='metadata_only' if not changed-PROFILE_METADATA_FIELDS and not changed_reqs else 'dependency_scoped'
        invalid['requirement'].update(changed_reqs)
        for jid,j in state['job'].items():
            if set(j.get('requirement_ids',[]))&changed_reqs or j['phase'] in policy_phases:invalid['job'].add(jid)
            for rid in changed_reqs:
                for r in (state['requirement'].get(rid),old_reqs.get(rid),new_reqs.get(rid)):
                    if r and r.get('blocks_work') and (not r.get('blocks_job_ids') or jid in r['blocks_job_ids']):invalid['job'].add(jid)
        # A fixpoint covers prerequisite phases, job DAG, proof/artifact links and
        # explicit requirement dependencies. No all-to-all lineage is invented.
        previous=None
        while previous!=(tuple((k,tuple(sorted(v))) for k,v in invalid.items()),tuple(sorted(affected_phases))):
            previous=(tuple((k,tuple(sorted(v))) for k,v in invalid.items()),tuple(sorted(affected_phases)))
            for rid,r in state['requirement'].items():
                if set(r.get('depends_on',[]))&invalid['requirement']:invalid['requirement'].add(rid)
            for jid in list(invalid['job']):
                j=state['job'][jid];invalid['artifact'].update(j.get('artifact_ids',[]));invalid['evidence'].update(j.get('evidence_ids',[]));affected_phases.add(j['phase'])
            for eid,e in state['evidence'].items():
                if set(e.get('requirement_ids',[]))&invalid['requirement'] or set(e.get('artifact_ids',[]))&invalid['artifact']:invalid['evidence'].add(eid)
            for did,d in state['decision'].items():
                explicit=any(k in d for k in ('requirement_ids','job_ids','artifact_ids'))
                if (set(d.get('requirement_ids',[]))&invalid['requirement'] or set(d.get('job_ids',[]))&invalid['job']
                    or set(d.get('artifact_ids',[]))&invalid['artifact'] or (changed_reqs and not explicit)):invalid['decision'].add(did)
            for jid,j in state['job'].items():
                prerequisites=set(new_profile.get('phase_prerequisites',{}).get(j['phase'],[]))|set(old.get('phase_prerequisites',{}).get(j['phase'],[]))
                if (set(j.get('depends_on',[]))&invalid['job'] or set(j.get('requirement_ids',[]))&invalid['requirement']
                    or set(j.get('decision_ids',[]))&invalid['decision'] or set(j.get('evidence_ids',[]))&invalid['evidence']
                    or set(j.get('artifact_ids',[]))&invalid['artifact'] or prerequisites&affected_phases):invalid['job'].add(jid)
                categories=set(DEFAULT_GATES.get(j['phase'],[]))|set(old.get('owner_decision_gates',{}).get(j['phase'],[]))|set(new_profile.get('owner_decision_gates',{}).get(j['phase'],[]))
                if any(did in invalid['decision'] and d.get('scope')==j['scope'] and d.get('category') in categories for did,d in state['decision'].items()):invalid['job'].add(jid)
            for kid,k in state['knowledge'].items():
                if set(k.get('impact_ids',[]))&(invalid['requirement']|invalid['job']|invalid['artifact']):invalid['knowledge'].add(kid)
        for eid,e in state['effect'].items():
            if set(e.get('artifact_ids',[]))&invalid['artifact']:invalid['effect'].add(eid)
        for gid,g in state['grant'].items():
            if g.get('effect_id') in invalid['effect']:invalid['grant'].add(gid)
    return {'mode':mode,'changed_fields':sorted(changed),'changed_requirement_ids':sorted(changed_reqs),
            'affected_phases':sorted(affected_phases),'conservative_reasons':reasons,
            'invalidated':{k:sorted(v&set(state[k])) for k,v in invalid.items()},
            'carried_forward':{k:sorted(set(state[k])-v) for k,v in invalid.items()}}

def apply_profile_amendment(root,folder,state,new_profile,approval):
    impact=profile_impact(state,new_profile);old_hash=state['profile_sha256']
    state['history'].append({'kind':'profile','record':state['profile'],'authority':approval,'superseded_at':now(),'impact':impact,'old_profile_sha256':old_hash})
    for rid in impact['invalidated']['requirement']:
        state['history'].append({'kind':'requirement','record':copy.deepcopy(state['requirement'][rid]),'reason':'profile_amendment','superseded_at':now()})
    atomic(folder/'profile.json',new_profile);state['profile']=new_profile;state['profile_sha256']=file_sha(folder/'profile.json')
    new_hash=state['profile_sha256']
    for kind in GROUPS:
        for ident,row in state[kind].items():
            # Already stale records cannot be revived by an unrelated amendment.
            if ident in impact['carried_forward'][kind] and row.get('_profile_sha256')==old_hash:row['_profile_sha256']=new_hash
    for r in state['requirement'].values():
        if r['id'] in impact['invalidated']['requirement']:r['status']='stale'
    changed=set(impact['changed_requirement_ids'])
    for item in new_profile.get('requirements',[]):
        if item['id'] in changed:
            state['requirement'][item['id']]=dict(item,status='pending',_profile_sha256=new_hash)
    for p,closure in state.get('phase_closures',{}).items():
        if p not in impact['affected_phases'] and closure.get('profile_sha256')==old_hash:closure['profile_sha256']=new_hash
    return impact

def gate(root,folder,state,jid,for_completion=False):
    need(jid in state['job'],'unknown job')
    j=state['job'][jid];reasons=[]
    def check(ok,msg):
        if not ok:reasons.append(msg)
    check(profile_current(state,folder),'profile changed; reconcile explicit amendment before work')
    check(not state['pause'].get('active'),'project is paused')
    check(j.get('_profile_sha256')==state['profile_sha256'],'job belongs to stale profile')
    if not for_completion:check(j.get('status') not in ('completed','running'),'job already running/completed; reconcile instead of replay')
    ex=state['execution'].get(j.get('execution_id'))
    try:
        need(ex and ex.get('status')=='current' and ex.get('_profile_sha256')==state['profile_sha256'],'execution missing or stale')
        authority(ex['authority'],execution_subject(ex))
        need(ex['scope']==j['scope'] and j['phase'] in [phase(p) for p in ex['phase_ids']],'execution does not cover job scope/phase')
    except (ValueError,KeyError) as e:reasons.append(str(e))
    constraints=state['profile'].get('constraints',{})
    if constraints.get('no_human_experiments',True):check(not j.get('human_experiment',False),'intentional human experiments prohibited')
    if constraints.get('owner_operational_work',False) is False:check(not j.get('requires_owner_operations',False),'regular owner operations prohibited')
    gates=owner_categories(state,j)
    for category in sorted(gates):
        check(any(d.get('category')==category and d.get('scope')==j['scope'] and decision_current(root,state,d) and d.get('_profile_sha256')==state['profile_sha256'] for d in state['decision'].values()),'owner decision missing/stale: '+category)
    for did in j.get('decision_ids',[]):
        d=state['decision'].get(did)
        check(bool(d and d.get('scope')==j['scope'] and decision_current(root,state,d)),'job decision missing/stale: '+did)
    for dep in j.get('depends_on',[]):
        dj=state['job'].get(dep)
        check(bool(dj and dj.get('status')=='completed' and completed_current(root,state,dj)),'job dependency missing/stale: '+dep)
    for prerequisite in phase_mapping(state,'phase_prerequisites').get(j['phase'],[]):
        pp=phase(prerequisite);closure=state.get('phase_closures',{}).get(pp)
        check(bool(closure and closure.get('profile_sha256')==state['profile_sha256'] and not phase_blockers(root,state,pp)),'phase prerequisite missing/stale: '+pp)
    for eid in j.get('effect_ids',[]):
        effect=state['effect'].get(eid)
        check(bool(effect and effect_dependency_current(root,effect)),'effect dependency missing/pending/unknown/stale: '+eid)
    for pin in j.get('inputs',[]):
        try:check(file_sha(contained(root,pin['path']))==pin['sha256'],'input changed: '+pin['path'])
        except (ValueError,OSError,KeyError):reasons.append('input unavailable')
    reasons.extend(job_requirement_blockers(root,state,j,for_completion))
    for r in state['requirement'].values():
        if r.get('blocks_work') and (not r.get('blocks_job_ids') or jid in r['blocks_job_ids']):check(current_requirement(root,state,r),'blocking requirement pending/stale: '+r['id'])
    if j.get('experiment'):
        for k in ('metric','threshold','horizon','stop','budget_usd'):check(k in j['experiment'] and j['experiment'][k] is not None,'experiment missing '+k)
    return sorted(set(reasons))

def phase_blockers(root,state,p,seen=None):
    blockers=[]
    for r in state['requirement'].values():
        due=r.get('phase',r.get('due_phase'))
        if due and phase(due)==p and (r.get('priority')=='must' or r.get('emphasis')):
            if not current_requirement(root,state,r):blockers.append('due requirement pending/stale: '+r['id'])
    for j in state['job'].values():
        if j['phase']==p:
            if j['status']!='completed':blockers.append('job not completed: '+j['id'])
            elif not completed_current(root,state,j,seen):blockers.append('completed job stale: '+j['id'])
    return blockers

def completed_current(root,state,j,seen=None):
    if j.get('status')!='completed' or j.get('_profile_sha256')!=state['profile_sha256']:return False
    visited=set(seen or ())
    if j['id'] in visited:return False
    visited.add(j['id'])
    try:
        if file_sha(root/'.appatelier/profile.json')!=state['profile_sha256']:return False
        ex=state['execution'][j['execution_id']]
        if ex.get('status')!='current' or ex.get('_profile_sha256')!=state['profile_sha256']:return False
        authority(ex['authority'],execution_subject(ex))
        if ex['scope']!=j['scope'] or j['phase'] not in [phase(x) for x in ex['phase_ids']]:return False
        for category in owner_categories(state,j):
            if not any(d.get('category')==category and d.get('scope')==j['scope'] and d.get('_profile_sha256')==state['profile_sha256'] and decision_current(root,state,d) for d in state['decision'].values()):return False
        for did in j.get('decision_ids',[]):
            d=state['decision'].get(did)
            if not d or d.get('scope')!=j['scope'] or not decision_current(root,state,d):return False
        for dep in j.get('depends_on',[]):
            if dep not in state['job'] or not completed_current(root,state,state['job'][dep],visited):return False
        for prerequisite in phase_mapping(state,'phase_prerequisites').get(j['phase'],[]):
            closure=state.get('phase_closures',{}).get(prerequisite)
            if not closure or closure.get('profile_sha256')!=state['profile_sha256'] or phase_blockers(root,state,prerequisite,visited):return False
        for eid in j.get('effect_ids',[]):
            if eid not in state['effect'] or not effect_dependency_current(root,state['effect'][eid]):return False
        for pin in j.get('inputs',[]):
            if file_sha(contained(root,pin['path']))!=pin['sha256']:return False
        if job_requirement_blockers(root,state,j,completion=True):return False
    except (KeyError,ValueError,OSError):return False
    return not completion_proof_blockers(root,state,j,pinned=True)

def validate_record(root,folder,state,kind,r):
    require(r,'id');need(ID.fullmatch(r['id']) is not None,'invalid id');source(r)
    r=copy.deepcopy(r);r['_profile_sha256']=state['profile_sha256']
    if kind=='requirement':
        require(r,'intent','priority','acceptance','owner');need(r['priority'] in ('must','should','explore'),'invalid priority')
        r.setdefault('status','pending');strings(r.get('evidence_ids',[]))
        for key in ('phase','due_phase','recheck_phase'):
            if key in r and r[key] is not None:r[key]=phase(r[key])
        if r.get('phase') and r.get('due_phase'):need(r['phase']==r['due_phase'],'phase and due_phase must identify the same due gate')
        old=state[kind].get(r['id'])
        if old and (old.get('priority')=='must' or old.get('emphasis')):
            if digest(requirement_definition(old))!=digest(requirement_definition(r)):authority(r.get('change_authority'),requirement_definition(r))
        if r['status'] in ('closed','complete'):need(current_requirement(root,state,r),'requirement completion needs current evidence pinned to this definition')
    elif kind=='decision':
        require(r,'category','scope','question','options');strings(r['options']);need(r['options'],'decision needs options')
        for key in ('requirement_ids','job_ids'):
            if key in r:strings(r[key])
        if r.get('status')=='confirmed':
            r['artifact_hashes']={}
            for aid in r.get('artifact_ids',[]):
                a=state['artifact'].get(aid);need(a and fresh_artifact(root,a),'decision artifact missing/stale');r['artifact_hashes'][aid]=a['sha256']
            need(decision_valid(r),'invalid decision authority or answer')
    elif kind=='execution':
        require(r,'scope','phase_ids','authority');strings(r['phase_ids']);authority(r['authority'],execution_subject(r));r.setdefault('status','current')
    elif kind=='job':
        require(r,'phase','scope','owner','goal','execution_id');r['phase']=phase(r['phase']);r.setdefault('status','pending')
        r.pop('input_requirement_hashes',None);r.pop('completion_hashes',None);r.pop('completion_evidence_hashes',None)
        need(r['status']=='pending','new/updated job must start pending')
        for k in ('depends_on','requirement_ids','fulfills_requirements','artifact_ids','evidence_ids','decision_ids','effect_ids'):strings(r.setdefault(k,[]))
        need(set(r['fulfills_requirements'])<=set(r['requirement_ids']),'fulfilled requirements must be assigned')
        need(type(r.get('human_experiment',False)) is bool and type(r.get('requires_owner_operations',False)) is bool,'explicit booleans required')
        for pin in r.get('inputs',[]):require(pin,'path','sha256');need(HEX.fullmatch(pin['sha256']),'input hash required');contained(root,pin['path'])
        old=state[kind].get(r['id']);need(not old or old.get('status')=='pending','running/completed job cannot be overwritten; create a repair job')
    elif kind=='artifact':
        require(r,'path','author_ids');strings(r['author_ids']);need(r['author_ids'],'artifact author required')
        need(not r['path'].startswith('.appatelier/'),'ledger internals are not product artifacts')
        h=file_sha(contained(root,r['path']));need(r.get('sha256',h)==h,'artifact hash differs');r['sha256']=h
    elif kind=='evidence':
        require(r,'artifact_ids','proof_path','observer','method','environment','status');strings(r['artifact_ids']);need(r['artifact_ids'],'evidence needs artifacts')
        need(type(r.get('independent')) is bool,'explicit independent flag required')
        supplied={key:r[key] for key in ('artifact_hashes','requirement_hashes','proof_sha256') if key in r}
        r['artifact_hashes']={}
        need(r['status'] in ('pass','fail','blocked'),'invalid evidence status')
        for aid in r['artifact_ids']:
            a=state['artifact'].get(aid);need(a and fresh_artifact(root,a),'evidence artifact missing/stale')
            if r['independent']:need(r['observer'] not in a['author_ids'],'author cannot independently review own artifact')
            r['artifact_hashes'][aid]=a['sha256']
        r['proof_sha256']=file_sha(contained(root,r['proof_path']));strings(r.get('requirement_ids',[]));r['requirement_hashes']={}
        for rid in r.get('requirement_ids',[]):
            requirement=state['requirement'].get(rid);need(requirement is not None,'evidence references unknown requirement')
            r['requirement_hashes'][rid]=digest(requirement_definition(requirement))
        for key,value in supplied.items():
            need(value==r[key],'evidence '+key+' differs from supplied observation snapshot; record a new observation')
    elif kind=='capability':
        require(r,'scope','environment','effect_types','available');strings(r['effect_types']);need(type(r['available']) is bool,'available must be boolean')
    elif kind=='grant':
        require(r,'effect_id','subject_sha256','authority','capability_id');need(HEX.fullmatch(r['subject_sha256']),'grant needs exact subject hash')
        authority(r['authority'],{'effect_id':r['effect_id'],'effect_sha256':r['subject_sha256']});r.setdefault('status','current')
    elif kind=='effect':
        require(r,'type','scope','target','parameters','artifact_ids','spend_usd','recurring_usd','idempotency_key','grant_id')
        need(isinstance(r['parameters'],dict),'effect parameters must be object')
        strings(r['artifact_ids']);number(r['spend_usd']);number(r['recurring_usd']);r['status']='prepared';provided=r.get('artifact_hashes');r['artifact_hashes']={}
        for aid in r['artifact_ids']:
            a=state['artifact'].get(aid);need(a and fresh_artifact(root,a),'effect artifact missing/stale');r['artifact_hashes'][aid]=a['sha256']
        need(provided is None or provided==r['artifact_hashes'],'prepared effect artifact snapshot changed; new subject approval required')
        need(not any(e['id']!=r['id'] and e['idempotency_key']==r['idempotency_key'] for e in state[kind].values()),'idempotency key already belongs to an effect')
        old=state[kind].get(r['id']);need(not old or old['status']=='prepared','dispatched effect cannot be overwritten/replayed')
    elif kind=='knowledge':
        require(r,'text','confidence','scope','impact_ids');strings(r['impact_ids'])
        for pin in r.get('inputs',[]):require(pin,'path','sha256');contained(root,pin['path'])
    return r

def effect_gate(root,folder,state,r):
    need(profile_current(state,folder),'profile changed')
    need(r.get('_profile_sha256')==state['profile_sha256'],'prepared effect belongs to stale profile')
    need(not state['pause']['active'],'project paused')
    need(r['status']=='prepared','effect already dispatched/unknown/completed; reconcile, do not replay')
    g=state['grant'].get(r['grant_id']);need(g and g.get('status')=='current','effect grant missing/revoked')
    need(g['_profile_sha256']==state['profile_sha256'],'stale effect grant')
    authority(g['authority'],{'effect_id':g['effect_id'],'effect_sha256':g['subject_sha256']})
    need(g['effect_id']==r['id'] and g['subject_sha256']==digest(effect_subject(r)),'grant differs from prepared effect')
    c=state['capability'].get(g['capability_id']);need(c and c['available'] and c.get('_profile_sha256')==state['profile_sha256'] and r['type'] in c['effect_types'] and c['scope']==r['scope'],'capability unavailable or outside effect scope')
    for aid,h in r['artifact_hashes'].items():need(aid in state['artifact'] and state['artifact'][aid]['sha256']==h and fresh_artifact(root,state['artifact'][aid]),'effect artifact changed')
    constraints=state['profile'].get('constraints',{})
    total=sum(e['spend_usd'] for e in state['effect'].values() if e['id']!=r['id'] and e['status'] in ('pending','unknown','succeeded'))+r['spend_usd']
    recurring=sum(e['recurring_usd'] for e in state['effect'].values() if e['id']!=r['id'] and e['status'] in ('pending','unknown','succeeded'))+r['recurring_usd']
    need(total<=number(constraints.get('new_external_spend_usd',0)),'new external spend cap exceeded')
    need(recurring<=number(constraints.get('recurring_spend_usd',0)),'recurring spend cap exceeded')
    human=r['parameters'].get('human_experiment',False) or r['type'] in ('ab_test','survey','interview','recruit_testers','human_pilot')
    need(not constraints.get('no_human_experiments',True) or not human,'intentional human experiment prohibited')

def status(root,folder,state,query=None):
    stale_artifacts=[x['id'] for x in state['artifact'].values() if not fresh_artifact(root,x)]
    stale_evidence=[x['id'] for x in state['evidence'].values() if x.get('status')=='pass' and not fresh_evidence(root,state,x)]
    result={'schema_version':VERSION,'project_id':state['project_id'],'revision':state['revision'],'profile_current':profile_current(state,folder),'pause':state['pause'],'pending_jobs':[j['id'] for j in state['job'].values() if j['status']!='completed'],'stale_artifacts':stale_artifacts,'stale_evidence':stale_evidence,'stale_completed_jobs':[j['id'] for j in state['job'].values() if j['status']=='completed' and not completed_current(root,state,j)],'unknown_effects':[e['id'] for e in state['effect'].values() if e['status'] in ('pending','unknown')],'next':'Read current profile/requirements and reconcile unknown effects before dependent work. CLI executes no remote action.'}
    result['optional_input_gaps']={j['id']:[rid for rid in j.get('requirement_ids',[]) if rid not in j.get('fulfills_requirements',[]) and rid in state['requirement'] and state['requirement'][rid].get('priority')!='must' and not state['requirement'][rid].get('emphasis') and not current_requirement(root,state,state['requirement'][rid])] for j in state['job'].values()}
    result['optional_input_gaps']={jid:ids for jid,ids in result['optional_input_gaps'].items() if ids}
    if query is not None:
        result['records']={k:[r for r in state[k].values() if not query or query.casefold() in canonical(r).casefold()] for k in GROUPS}
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__,epilog='All put records need id, source, verbatim. Source/authority records pin claims, not authenticate humans. Use subject --kind decision|execution|effect|grant --record FILE to compute the exact authority digest before recording an actual user response.')
    parser.add_argument('--project',type=Path,required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    x=sub.add_parser('init');x.add_argument('--profile',type=Path,required=True)
    x=sub.add_parser('amend-profile');x.add_argument('--profile',type=Path,required=True);x.add_argument('--record',type=Path,required=True)
    sub.add_parser('status');x=sub.add_parser('context');x.add_argument('--query',default='')
    x=sub.add_parser('subject');x.add_argument('--kind',choices=['decision','execution','effect','grant','profile','requirement'],required=True);x.add_argument('--record',type=Path,required=True)
    x=sub.add_parser('put');x.add_argument('--kind',choices=GROUPS,required=True);x.add_argument('--record',type=Path,required=True)
    for cmd in ('gate','start','complete'):
        x=sub.add_parser(cmd);x.add_argument('--job',required=True)
    for cmd in ('phase-check','phase-complete'):
        x=sub.add_parser(cmd);x.add_argument('--phase',required=True)
    x=sub.add_parser('pause');x.add_argument('--boundary',choices=['now','after_job','after_phase','after_artifact'],default='now');x.add_argument('--target');x.add_argument('--record',type=Path,required=True)
    x=sub.add_parser('resume');x.add_argument('--record',type=Path,required=True)
    x=sub.add_parser('dispatch');x.add_argument('--effect',required=True)
    for cmd in ('receipt','reconcile'):
        x=sub.add_parser(cmd);x.add_argument('--effect',required=True);x.add_argument('--record',type=Path,required=True)
    a=parser.parse_args();root=a.project.absolute();cmd=a.command
    if cmd=='subject':
        r=read_json(a.record)
        if a.kind=='profile':
            s=read_json(root/'.appatelier/state.json');obj={'old_profile_sha256':s['profile_sha256'],'new_profile_content_sha256':digest(r)}
        else:
            if a.kind in ('decision','effect') and r.get('artifact_ids'):
                s=read_json(root/'.appatelier/state.json');hashes={}
                for aid in r['artifact_ids']:
                    artifact=s['artifact'][aid];need(fresh_artifact(root,artifact),'subject artifact missing/stale');hashes[aid]=artifact['sha256']
                need(r.get('artifact_hashes',hashes)==hashes,'subject artifact snapshot changed')
                r['artifact_hashes']=hashes
            obj={'decision':decision_subject,'execution':execution_subject,'effect':effect_subject,'grant':lambda z:{'effect_id':z['effect_id'],'effect_sha256':z['subject_sha256']},'requirement':requirement_definition}[a.kind](r)
        return {'subject':obj,'subject_sha256':digest(obj),'authority_created':False}
    with locked(root,cmd=='init') as folder:
        path=folder/'state.json'
        if cmd=='init':
            need(not path.exists(),'already initialized; do not overwrite')
            p=normalize_profile(read_json(a.profile))
            atomic(folder/'profile.json',p)
            s={'schema_version':VERSION,'project_id':p.get('id','product'),'profile':p,'profile_sha256':file_sha(folder/'profile.json'),'revision':1,'created_at':now(),'pause':{'active':False},'history':[],'phase_closures':{}}
            for k in GROUPS:s[k]={}
            for r in p.get('requirements',[]):
                require(r,'id','intent');s['requirement'][r['id']]=dict(r,status='pending',_profile_sha256=s['profile_sha256'])
            atomic(path,s);return {'initialized':True,'execution_authorized':False,'profile_sha256':s['profile_sha256']}
        s=read_json(path);need(s.get('schema_version')==VERSION,'unsupported ledger schema')
        if cmd in ('status','context'):return status(root,folder,s,getattr(a,'query',None))
        changed=True;result={}
        if cmd=='amend-profile':
            raw=read_json(a.profile);r=read_json(a.record)
            authority(r,{'old_profile_sha256':s['profile_sha256'],'new_profile_content_sha256':digest(raw)})
            p=normalize_profile(raw)
            impact=apply_profile_amendment(root,folder,s,p,r)
            result={'profile_amended':True,'impact':impact,'profile_sha256':s['profile_sha256']}
        elif cmd=='put':
            r=validate_record(root,folder,s,a.kind,read_json(a.record));old=s[a.kind].get(r['id'])
            if old:s['history'].append({'kind':a.kind,'record':old,'superseded_at':now()})
            s[a.kind][r['id']]=r
            if a.kind=='job':cycle(s['job'])
            if a.kind=='artifact' and s['pause'].get('boundary')=='after_artifact' and s['pause'].get('target')==r['id']:s['pause']['active']=True
            result={'recorded':r['id'],'kind':a.kind,'executes':False,'paused':s['pause']['active']}
        elif cmd in ('phase-check','phase-complete'):
            pp=phase(a.phase);reasons=phase_blockers(root,s,pp)
            if not profile_current(s,folder):reasons.append('profile changed')
            if cmd=='phase-check':return {'ready':not reasons,'phase':pp,'blockers':reasons,'executes':False}
            need(not reasons,'phase blocked: '+'; '.join(reasons));need(not s['pause']['active'],'project paused')
            s.setdefault('phase_closures',{})[pp]={'profile_sha256':s['profile_sha256'],'closed_at':now()}
            pause=s['pause']
            if pause.get('boundary')=='after_phase' and phase(pause.get('target',''))==pp:pause['active']=True
            result={'phase_complete':pp,'scope':'current due requirements and declared jobs','paused':pause['active']}
        elif cmd in ('gate','start','complete'):
            reasons=gate(root,folder,s,a.job,cmd=='complete')
            if cmd=='gate':return {'ready':not reasons,'blockers':reasons,'executes':False}
            need(not reasons,'job blocked: '+'; '.join(reasons));j=s['job'][a.job]
            if cmd=='start':
                j['status']='running';j['started_at']=now()
                j['input_requirement_hashes']={rid:digest(requirement_definition(s['requirement'][rid])) for rid in j.get('requirement_ids',[])}
                result={'started':a.job,'executes':False}
            else:
                need(j['status']=='running','only running job can complete')
                proof_blockers=completion_proof_blockers(root,s,j)
                need(not proof_blockers,'; '.join(proof_blockers))
                for rid in j['fulfills_requirements']:need(current_requirement(root,s,s['requirement'][rid]),'declared requirement not closed with current evidence: '+rid)
                j['status']='completed';j['completed_at']=now();j['completion_hashes']={aid:s['artifact'][aid]['sha256'] for aid in j['artifact_ids']}
                j['completion_evidence_hashes']={eid:digest(evidence_definition(s['evidence'][eid])) for eid in j['evidence_ids']}
                p=s['pause']
                if p.get('boundary')=='after_job' and p.get('target')==a.job or p.get('boundary')=='after_artifact' and p.get('target') in j['artifact_ids']:p['active']=True
                result={'completed':a.job,'proof_scope':'declared artifacts and evidence only','paused':s['pause']['active']}
        elif cmd=='pause':
            r=read_json(a.record);source(r);need(a.boundary=='now' or a.target,'boundary target required')
            old=s['pause'];need(not old.get('active') or a.boundary=='now','active pause cannot be weakened by a future stop')
            s['pause']={'active':a.boundary=='now','boundary':a.boundary,'target':a.target,'source':r['source'],'verbatim':r['verbatim']};result=s['pause']
        elif cmd=='resume':
            r=read_json(a.record);source(r);need(r.get('actor')=='user','resume needs actual user request')
            unresolved=[e['id'] for e in s['effect'].values() if e['status'] in ('pending','unknown')]
            need(not unresolved,'reconcile pending/unknown effects before resume: '+', '.join(unresolved))
            s['pause']={'active':False,'resumed_from':s['pause'],'source':r['source'],'verbatim':r['verbatim']};result={'resumed':True,'replays_effects':False}
        elif cmd=='dispatch':
            need(a.effect in s['effect'],'unknown effect');r=s['effect'][a.effect];effect_gate(root,folder,s,r);r['status']='pending';r['dispatched_at']=now();result={'pending':a.effect,'executes':False,'next':'Perform the exact authorized host operation once; then record actual receipt. Unknown outcome requires reconciliation.'}
        elif cmd in ('receipt','reconcile'):
            need(a.effect in s['effect'],'unknown effect');e=s['effect'][a.effect];r=read_json(a.record);source(r)
            need(e['status'] in ('pending','unknown'),'only pending/unknown effect accepts a receipt')
            need(r.get('outcome') in ('succeeded','failed','unknown'),'valid outcome required')
            require(r,'provider_ref','proof_path');h=file_sha(contained(root,r['proof_path']))
            if cmd=='reconcile':need(r.get('read_only_status_check') is True,'reconciliation needs actual read-only provider status evidence')
            if r['outcome']=='failed':need(r.get('confirmed_no_effect') is True,'failure must establish no effect; otherwise unknown')
            e['receipts']=e.get('receipts',[])+[dict(r,proof_sha256=h,recorded_at=now(),reconciled=cmd=='reconcile')];e['status']=r['outcome'];result={'effect':a.effect,'status':e['status'],'replay_authorized':False}
        s['revision']+=1;s['updated_at']=now();atomic(path,s);return result

if __name__=='__main__':
    try:
        out=main();print(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
        if isinstance(out,dict) and out.get('ready') is False:raise SystemExit(1)
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as e:
        print(json.dumps({'error':str(e),'executed':False},ensure_ascii=False),file=sys.stderr);raise SystemExit(2)
