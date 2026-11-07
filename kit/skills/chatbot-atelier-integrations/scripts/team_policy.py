#!/usr/bin/env python3
"""Adaptive team record integrity. Never certifies real agents or product quality."""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath

SCHEMA = 'chatbot.team/1'
PRODUCTION = {'specialist', 'lead', 'integration', 'executive', 'orchestrator', 'supreme',
              'craft', 'product_brief', 'chief_plan', 'decomposition', 'lead_integration',
              'product_integration', 'technical_integration'}
QA = {'qa', 'guardian', 'qa_signoff'}
INPUT_CONSUMERS = QA | {'judge', 'orchestrator', 'supreme'}
PERSPECTIVES = {'product', 'experience', 'growth', 'finance', 'technology', 'delivery'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load_profile(stage=None):
    assets = Path(__file__).resolve().parents[1] / 'assets'
    own = json.loads((assets / 'team-profile.json').read_text())
    if stage is None or stage == own['stage']:
        return own
    raise ValueError('Unknown current chat team stage')


def scaffold(ids, kind='stage', active=None, profile=None, requirement_domains=None):
    profile = profile or load_profile()
    assigned = {rid: d['id'] for d in profile['domains'] for rid in d['requirement_ids']}
    # Project-owned domains extend the profile; canonical ownership is immutable.
    for rid, domain in (requirement_domains or {}).items():
        if rid not in assigned and isinstance(domain, str) and domain.strip():
            assigned[rid] = domain
    active = list(ids) if active is None else list(active)
    return {'schema_version': SCHEMA, 'profile_version': profile['version'], 'stage': profile['stage'],
            'scope': {'kind': kind, 'active_requirement_ids': active,
                      'changed_component_ids': [], 'statement': 'DRAFT: import the actual task and baseline'},
            'components': {}, 'impact_run': '', 'guardian_run': '', 'orchestrator_run': '',
            'assignments': {rid: {'domain_id': assigned.get(rid, ''),
                                 'status': 'active' if rid in active else 'out_of_scope',
                                 'component_ids': [], 'owner_run': '', 'qa_run': '', 'judge_run': '',
                                 'reason': 'DRAFT: establish impact before accepting unchanged scope'} for rid in ids},
            'perspectives': {}, 'repair_history': [], 'reopens': []}


def snapshot_inputs(plan, run, runs, profile=None, requirement_records=None):
    """Describe exact declared inputs; recording this never authenticates an actor.

    Call before executing/reviewing a run. A completed run keeps this snapshot;
    the checker compares it to current scoped inputs without refreshing it.
    """
    profile = profile or load_profile()
    def ids(value, label):
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value) or len(value) != len(set(value)):
            raise ValueError(label + ' must be unique string list')
        return value
    rids = ids(run.get('requirement_ids', []), 'run requirement_ids')
    if not rids: raise ValueError('run input scope needs requirement_ids')
    assignments, components = plan.get('assignments', {}), plan.get('components', {})
    canonical_rows = json.loads((Path(__file__).resolve().parents[1] / 'assets/requirements.json').read_text())['requirements']
    canonical_map = {row['id']: row for row in canonical_rows}
    records = {row['id']: row for row in (requirement_records or []) if isinstance(row, dict) and isinstance(row.get('id'), str)}
    dependencies = set()
    evidence_inputs = {}
    consuming = run.get('kind') in INPUT_CONSUMERS
    def closure(cid, visiting):
        if cid not in components or cid in visiting: raise ValueError('missing/cyclic component dependency: ' + cid)
        item = components[cid]
        if not isinstance(item, dict): raise ValueError('invalid component: ' + cid)
        dependencies.add(cid)
        for dep in ids(item.get('depends_on', []), 'component dependencies'):
            closure(dep, visiting | {cid})
    requirements = {}
    producer_ids = set(ids(run.get('input_run_ids', []), 'input_run_ids'))
    for rid in rids:
        assignment = assignments.get(rid)
        if not isinstance(assignment, dict): raise ValueError('run input scope missing assignment: ' + rid)
        if consuming or 'input_component_ids' not in run:
            for cid in ids(assignment.get('component_ids', []), 'assignment component_ids'):
                closure(cid, set())
        if rid not in canonical_map and rid not in records:
            raise ValueError('project input requirement needs accepted source record: ' + rid)
        requirements[rid] = digest(canonical({'canonical': canonical_map.get(rid), 'project': records.get(rid)}))
        if consuming:
            for key in ('owner_run', 'qa_run') if run.get('kind') in {'judge', 'orchestrator', 'supreme'} else ('owner_run',):
                producer = assignment.get(key)
                if producer and producer != run.get('id'): producer_ids.add(producer)
            for ref in ids(assignment.get('evidence_refs', []), 'primary evidence_refs'):
                evidence_inputs[ref] = assignment.get('evidence_sha256s', {}).get(ref)
            carry = assignment.get('carry_forward', {})
            if isinstance(carry, dict) and carry.get('reviewer_run') == run.get('id') and carry.get('receipt_ref'):
                evidence_inputs[carry['receipt_ref']] = carry.get('receipt_sha256')
    if 'input_component_ids' in run:
        if not consuming and (not isinstance(run.get('input_scope_reason'), str) or not run['input_scope_reason'].strip()):
            raise ValueError('explicit producer input_component_ids needs input_scope_reason')
        for cid in ids(run['input_component_ids'], 'input_component_ids'):
            closure(cid, set())
    for ref, h in evidence_inputs.items():
        if not isinstance(h, str) or len(h) != 64:
            raise ValueError('review input needs current primary evidence hash: ' + str(ref))
    component_inputs = {}
    for cid in sorted(dependencies):
        item = components[cid]
        value = {key: item.get(key) for key in ('sha256', 'environment')}
        if not isinstance(value['sha256'], str) or len(value['sha256']) != 64 or not isinstance(value['environment'], str) or not value['environment'].strip():
            raise ValueError('input component needs current hash/environment: ' + cid)
        component_inputs[cid] = value
    indexed = {row['id']: row for row in runs if isinstance(row, dict) and isinstance(row.get('id'), str)}
    reviewed = {}
    for identity in sorted(producer_ids):
        item = indexed.get(identity, {})
        if identity == run.get('id') or item.get('status') != 'completed' or not item.get('output_ref') or not isinstance(item.get('output_sha256'), str) or len(item['output_sha256']) != 64:
            raise ValueError('review input needs completed authored output: ' + str(identity))
        reviewed[identity] = {'output_ref': item['output_ref'], 'output_sha256': item['output_sha256']}
    return {'schema_version': 'chatbot.run-inputs/1',
            'scope': {'stage': profile['stage'], 'kind': run.get('kind'),
                      'requirement_ids': sorted(rids), 'domain_ids': sorted(ids(run.get('domain_ids', []), 'domain_ids'))},
            'components': component_inputs, 'requirements': requirements, 'reviewed_outputs': reviewed,
            'reviewed_evidence': evidence_inputs}


def normalize_run(raw):
    """Project the one current run record; field aliases are not accepted."""
    run = dict(raw)
    run['id'] = raw.get('id')
    run['actor'] = raw.get('actor_id')
    run['kind'] = raw.get('kind')
    run['output_ref'] = raw.get('output_ref')
    return run


def check(plan, ids, runs, package_hash=None, root=None, ready=False, profile=None, requirement_records=None):
    errors = []
    def need(ok, message):
        if not ok:
            errors.append('team: ' + message)
        return bool(ok)
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def unique(value, allowed=None, nonempty=False):
        ok = isinstance(value, list) and all(text(x) for x in value)
        ok = ok and len(value) == len(set(value)) and (not nonempty or bool(value))
        return ok and (allowed is None or set(value) <= set(allowed))
    def material(ref, expected=None):
        if not need(text(ref), 'missing artifact reference'):
            return None
        path = PurePosixPath(ref)
        if not need(not path.is_absolute() and '\\' not in ref and all(x not in ('', '.', '..') for x in path.parts), 'unsafe artifact reference'):
            return None
        if root is None:
            return None
        if callable(root):
            try:
                raw = root(ref)
            except (OSError, KeyError, ValueError):
                need(False, 'artifact absent from verified archive: ' + ref)
                return None
            if expected is not None:
                need(isinstance(expected, str) and len(expected) == 64 and digest(raw) == expected, 'artifact hash differs: ' + ref)
            return raw
        base = Path(root).resolve()
        actual = base / path
        if not need(actual.is_file() and not any(p.is_symlink() for p in [actual, *actual.parents] if p != base.parent), 'artifact absent or symlink: ' + ref):
            return None
        raw = actual.read_bytes()
        if expected is not None:
            need(isinstance(expected, str) and len(expected) == 64 and digest(raw) == expected, 'artifact hash differs: ' + ref)
        return raw

    profile = profile or load_profile()
    expected = set(ids)
    if not need(isinstance(plan, dict) and plan.get('schema_version') == SCHEMA, 'current chatbot.team/1 plan required'):
        return errors
    need(plan.get('stage') == profile['stage'], 'team stage differs from trusted profile')
    need(plan.get('profile_version') == profile['version'], 'team profile version differs')
    domain_map = {rid: d['id'] for d in profile['domains'] for rid in d['requirement_ids']}
    need(expected >= set(domain_map), 'canonical profile requirements are missing')
    scope = plan.get('scope', {})
    kind = scope.get('kind')
    need(kind in {'local', 'feature', 'critical', 'stage'}, 'invalid scope kind')
    active = scope.get('active_requirement_ids', [])
    if not need(unique(active, expected, nonempty=True), 'active IDs must be unique known requirements'):
        active = []
    active = set(active)
    need(text(scope.get('statement')), 'scope statement required')
    assignments = plan.get('assignments')
    if not need(isinstance(assignments, dict) and set(assignments) == expected, 'one assignment for every canonical/user requirement required'):
        return errors
    raw_runs = runs if isinstance(runs, list) else []
    unsupported = {'run_id', 'agent_id', 'actual_agent_id', 'actual_handle', 'artifact_ref', 'artifact', 'role'}
    for raw in raw_runs:
        need(isinstance(raw, dict) and not (unsupported & set(raw)), 'unsupported run field alias; use id/actor_id/kind/output_ref')
    normalized = [normalize_run(r) for r in raw_runs if isinstance(r, dict)]
    indexed = {r.get('id'): r for r in normalized}
    need(len(indexed) == len(normalized) and all(text(x) for x in indexed), 'duplicate or missing actual run ID')
    complete = {key: r for key, r in indexed.items() if r.get('status') == 'completed'}
    authors = {r.get('actor') for r in complete.values() if r.get('kind') in PRODUCTION}
    nonjudges = {r.get('actor') for r in complete.values() if r.get('kind') != 'judge'}
    for run in complete.values():
        need(text(run.get('actor')), 'completed run needs actual actor ID')
        need(unique(run.get('requirement_ids', []), expected), 'run references unknown or duplicate requirements')
        if ready and root is not None:
            material(run.get('output_ref'), run.get('output_sha256'))
            need(text(run.get('output_sha256')), 'current completed output needs exact SHA256')

    input_checks = set()
    def get(ref, kinds, rid=None, domain=None):
        run = complete.get(ref)
        if not need(run is not None and run.get('kind') in kinds, 'required completed ' + '/'.join(sorted(kinds)) + ' run: ' + str(ref)):
            return {}
        need(run.get('verdict') == 'accept', 'run has not accepted its scope: ' + str(ref))
        if ready and run.get('kind') in INPUT_CONSUMERS and ref not in input_checks:
            input_checks.add(ref)
            try:
                expected_inputs = snapshot_inputs(plan, run, raw_runs, profile, requirement_records)
                need(run.get('input_snapshot') == expected_inputs,
                     'completed run input snapshot missing/stale (including reviewed authored outputs): ' + str(ref))
            except (ValueError, TypeError, KeyError) as exc:
                need(False, 'cannot bind current run inputs ' + str(ref) + ': ' + str(exc))
        if rid is not None:
            need(rid in run.get('requirement_ids', []), 'run does not cover requirement: ' + rid)
        if domain is not None:
            need(domain in run.get('domain_ids', []), 'run lacks assigned domain competence: ' + domain)
        if run.get('kind') in QA:
            need(run.get('actor') not in authors, 'QA/guardian reuses a production actor')
        if run.get('kind') == 'judge':
            need(run.get('actor') not in nonjudges, 'judge reuses an author, manager or QA actor')
            need(run.get('package_hash') == package_hash and bool(package_hash), 'judge references stale frozen package')
            mode = run.get('review_mode', 'primary')
            need(mode in {'primary', 'addressed'}, 'invalid judge review mode')
            if mode == 'primary':
                need(run.get('context_mode') == 'fresh', 'primary judge needs fresh context')
            else:
                need(text(run.get('previous_review_ref')), 'addressed judge needs previous review reference')
                if root is not None:
                    material(run.get('previous_review_ref'), run.get('previous_review_sha256'))
        return run

    components = plan.get('components', {})
    if not need(isinstance(components, dict), 'components must be a dictionary'):
        components = {}
    changed = scope.get('changed_component_ids', [])
    if not need(unique(changed, components), 'changed components unknown or duplicated'):
        changed = []
    closure_cache = {}
    def closure(cid, visiting=None):
        if cid in closure_cache:
            return closure_cache[cid]
        visiting = set() if visiting is None else set(visiting)
        if not need(cid in components and cid not in visiting, 'missing/cyclic component dependency: ' + str(cid)):
            return set()
        visiting.add(cid)
        item = components[cid]
        if not need(isinstance(item, dict), 'invalid component record'):
            return {cid}
        needs = item.get('depends_on', [])
        if not need(unique(needs, components), 'invalid component dependency list'):
            needs = []
        found = {cid}
        for dep in needs:
            found |= closure(dep, visiting)
        closure_cache[cid] = found
        return found
    for cid, component in components.items():
        closure(cid)
        need(text(component.get('environment')), 'component needs explicit environment/config identity: ' + cid)
        if root is not None:
            material(component.get('artifact_ref'), component.get('sha256'))
        if component.get('baseline_sha256') and component.get('baseline_sha256') != component.get('sha256'):
            need(cid in changed, 'changed component omitted from impact: ' + cid)
    critical = set(profile.get('critical_requirement_ids', [])) & active
    council = kind in {'stage', 'critical'} or bool(critical) or bool(scope.get('material_baseline_change'))
    needs_impact = set(expected) - active
    if ready and needs_impact:
        impact = get(plan.get('impact_run'), QA)
        need(needs_impact <= set(impact.get('requirement_ids', [])), 'impact QA must cover every inactive requirement')
    if ready and kind == 'stage':
        guardian = get(plan.get('guardian_run'), QA)
        need(expected <= set(guardian.get('requirement_ids', [])), 'guardian must cover the full brief')
        perspectives = plan.get('perspectives', {})
        need(isinstance(perspectives, dict) and set(perspectives) == PERSPECTIVES, 'six cross-domain questions need accountable owners, not six mandatory executives')
        for item in perspectives.values() if isinstance(perspectives, dict) else []:
            need(isinstance(item, dict) and item.get('owner_run') in complete and text(item.get('finding')), 'perspective needs an actual owner run and finding')
    if ready:
        orchestrator = get(plan.get('orchestrator_run'), {'orchestrator', 'supreme'})
        need(active <= set(orchestrator.get('requirement_ids', [])), 'orchestrator must cover active scope')

    def carry(row, rid, deps):
        record = row.get('carry_forward', {})
        if not need(isinstance(record, dict) and text(record.get('reason')), 'carry-forward needs reason: ' + rid):
            return
        get(record.get('reviewer_run'), QA, rid)
        source = material(record.get('receipt_ref'), record.get('receipt_sha256'))
        if source is None:
            need(root is not None or not ready, 'ready carry-forward needs source bytes')
            return
        try:
            receipt = json.loads(source)
        except (ValueError, UnicodeError):
            need(False, 'invalid immutable review receipt')
            return
        need(receipt.get('schema_version') == 'chatbot.review/1', 'unsupported carry receipt')
        need(receipt.get('requirement_id') == rid and receipt.get('verdict') == 'accept', 'source review did not accept exact criterion')
        need(text(receipt.get('actor_id')) and text(receipt.get('source_version')) and text(receipt.get('source_package_hash')), 'source review provenance absent')
        need(receipt.get('kind') == 'judge' if council else receipt.get('kind') in {'qa', 'judge'}, 'carry receipt lacks required review level')
        material(receipt.get('report_ref'), receipt.get('report_sha256'))
        snapshots = {cid: {k: components[cid].get(k) for k in ('sha256', 'environment')} for cid in sorted(deps)}
        need(receipt.get('components') == snapshots, 'carry crosses changed component, transitive dependency or environment: ' + rid)
        need(not (deps & set(changed)), 'changed dependency cannot retain previous acceptance: ' + rid)

    for rid, row in assignments.items():
        if not need(isinstance(row, dict), 'invalid assignment: ' + rid):
            continue
        domain = row.get('domain_id')
        need(text(domain) and (rid not in domain_map or domain == domain_map[rid]), 'canonical domain ownership changed: ' + rid)
        status = row.get('status')
        need(status in {'active', 'carried', 'out_of_scope'}, 'invalid assignment status: ' + rid)
        need((status == 'active') == (rid in active), 'active assignment and scope differ: ' + rid)
        cids = row.get('component_ids', [])
        if not need(unique(cids, components, nonempty=ready), 'component scope missing or invalid: ' + rid):
            cids = []
        deps = set().union(*(closure(cid) for cid in cids)) if cids else set()
        if status != 'active':
            need(text(row.get('reason')), 'inactive requirement needs impact reason: ' + rid)
            need(not deps & set(changed), 'inactive criterion has a changed dependency: ' + rid)
            need(row.get('impact', 'unknown') == 'unchanged', 'unknown impact must activate criterion: ' + rid)
            if kind == 'stage':
                need(status == 'carried', 'stage completion cannot omit a criterion: ' + rid)
            if ready and status == 'carried':
                carry(row, rid, deps)
            continue
        if not ready:
            continue
        owner = get(row.get('owner_run'), PRODUCTION, rid, domain)
        qa = get(row.get('qa_run'), QA, rid, domain)
        need(owner.get('actor') != qa.get('actor'), 'author cannot accept own result: ' + rid)
        need(row.get('verdict') == 'accept', 'criterion not accepted: ' + rid)
        evidence = row.get('evidence_refs', [])
        need(unique(evidence, nonempty=True), 'criterion needs primary evidence refs: ' + rid)
        for ref in evidence:
            if root is not None:
                evidence_hash = row.get('evidence_sha256s', {}).get(ref)
                need(text(evidence_hash), 'primary evidence needs exact SHA256: ' + ref)
                material(ref, evidence_hash)
        if council:
            judge = get(row.get('judge_run'), {'judge'}, rid, domain)
            judgments = judge.get('criteria', {})
            item = judgments.get(rid, {}) if isinstance(judgments, dict) else {}
            need(item.get('verdict') == 'accept' and all(text(item.get(k)) for k in ('positive_claim', 'strongest_objection', 'uncertainty', 'reversal_condition')), 'grouped judge needs substantive separate criterion conclusion: ' + rid)

    histories = plan.get('repair_history', [])
    need(isinstance(histories, list), 'repair_history must be an array')
    seen = {}
    for item in histories if isinstance(histories, list) else []:
        if not need(isinstance(item, dict), 'invalid repair history entry'):
            continue
        key = item.get('issue_id')
        need(text(key) and text(item.get('strategy_ref')), 'repair needs issue and strategy')
        previous = seen.setdefault(key, [])
        if len(previous) >= 2 and all(p.get('result') == 'failed' for p in previous[-2:]):
            need(item.get('strategy_ref') != previous[-1].get('strategy_ref') and text(item.get('diagnostic_ref')), 'two failed repeats require a new diagnosed repair strategy')
        previous.append(item)
    for item in plan.get('reopens', []):
        if not need(isinstance(item, dict) and text(item.get('issue_id')) and text(item.get('reason')), 'reopening needs exact issue and reason'):
            continue
        evidence = item.get('new_evidence', {})
        need(isinstance(evidence, dict) and evidence.get('sha256') not in item.get('previous_evidence_sha256s', []) and text(evidence.get('sha256')), 'reopening needs genuinely new evidence')
        if root is not None and isinstance(evidence, dict):
            material(evidence.get('artifact_ref'), evidence.get('sha256'))
    return errors


def snapshot_hash(data):
    """Freeze substance and pre-judge records without a signature/hash cycle."""
    excluded = {'reviews', 'judgments', 'completion', 'checkpoint', 'runs', 'decision', 'package_hash'}
    payload = {k: v for k, v in data.items() if k not in excluded}
    payload['prejudge_runs'] = [{k: v for k, v in r.items() if k != 'package_hash'}
                                for r in data.get('runs', [])
                                if normalize_run(r)['kind'] not in {'judge', 'orchestrator', 'supreme'}]
    return digest(canonical(payload))
