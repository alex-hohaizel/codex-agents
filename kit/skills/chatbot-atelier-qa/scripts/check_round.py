#!/usr/bin/env python3
"""Check traceability and independence, never infer product quality from structure."""
import argparse
import json
import sys
from pathlib import Path

EVIDENCE_RESULTS = {'pass', 'passed', 'accept', 'accepted', 'observed', 'fail', 'failed', 'reject', 'rejected',
                    'pending', 'not_run', 'running', 'unknown', 'uncertain', 'cancelled', 'inconclusive', 'blocked'}
ACCEPTED_RESULTS = {'pass', 'passed', 'accept', 'accepted'}

def _check(data, source_root=None):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    if not isinstance(data, dict):
        return ['round must be an object']
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    profile = json.loads((Path(__file__).resolve().parents[1] / 'assets/requirements.json').read_text())
    baseline = {r['id'] for r in profile['requirements']}
    require(data.get('schema_version') == 'chatbot.round/1', 'schema_version must be chatbot.round/1')
    brief = data.get('brief', {})
    for key in ('id', 'version', 'user_intent', 'baseline', 'constraints', 'authorization'):
        require(key in brief and brief[key] is not None, 'brief missing ' + key)
    requirements = data.get('requirements', [])
    require(isinstance(requirements, list) and all(isinstance(row, dict) for row in requirements), 'requirements must be object array')
    if not isinstance(requirements, list): requirements = []
    requirements = [row for row in requirements if isinstance(row, dict)]
    ids = [r.get('id') for r in requirements]
    valid_ids = all(text(rid) for rid in ids)
    expected = set(ids) if valid_ids else baseline
    require(valid_ids and len(ids) == len(expected) and baseline <= expected,
            'all 24 unique baseline requirement IDs required; project IDs may extend them')
    for row in requirements:
        require(row.get('state') in ('active', 'unchanged'), 'invalid requirement state: ' + str(row.get('id')))
        require(bool(row.get('reason')), 'requirement needs impact reason: ' + str(row.get('id')))
        if text(row.get('id')) and row['id'] not in baseline:
            for key in ('source_ref', 'owner', 'domain_id', 'acceptance', 'negative_probe'):
                require(text(row.get(key)), 'project requirement ' + row['id'] + ' missing ' + key)
    for key in ('findings', 'decisions', 'changes', 'evidence', 'runs', 'reviews'):
        require(isinstance(data.get(key), list), key + ' must be an array')
    evidence = data.get('evidence', [])
    require(isinstance(evidence, list) and all(isinstance(e, dict) and text(e.get('id')) for e in evidence),
            'evidence must have nonempty string IDs in object records')
    if not isinstance(evidence, list): evidence = []
    evidence = [e for e in evidence if isinstance(e, dict) and text(e.get('id'))]
    evidence_ids = {e.get('id') for e in evidence}
    require(len(evidence_ids) == len(evidence), 'duplicate evidence IDs')
    for item in evidence:
        for key in ('id', 'version', 'kind', 'provenance', 'artifact', 'procedure', 'result', 'limitations'):
            require(key in item, 'evidence missing ' + key)
        require(isinstance(item.get('result'), str) and item['result'] in EVIDENCE_RESULTS,
                'invalid evidence result: ' + str(item.get('id')))
    runs = data.get('runs', [])
    run_ids = [r.get('id') for r in runs]
    require(len(run_ids) == len(set(run_ids)), 'duplicate run IDs')
    completion = data.get('completion', {})
    stages = ('prepared', 'locally_verified', 'independently_reviewed', 'deployed', 'observed_in_chat')
    stage = completion.get('stage')
    require(stage in stages, 'invalid completion stage')
    if stage == 'human_validated':
        require(False, 'human assessment is a separate completion.assessments.human axis, not a completion stage')
    require(bool(completion.get('scope')), 'completion scope required')
    unresolved = set(completion.get('unresolved_requirement_ids', []))
    require(unresolved <= expected, 'unknown unresolved requirement')
    require(bool(data.get('checkpoint')), 'checkpoint required')
    active = {r['id'] for r in requirements if r.get('state') == 'active'}
    reviews = data.get('reviews', [])
    evidence_map = {e.get('id'): e for e in evidence}
    for review in reviews:
        require(review.get('requirement_id') in active, 'review for inactive/unknown requirement')
        require(review.get('verdict') in ('accept', 'revise', 'block', 'unknown'), 'invalid review verdict')
        refs = review.get('evidence_ids', [])
        valid_refs = isinstance(refs, list) and all(text(x) for x in refs) and len(refs) == len(set(refs))
        require(valid_refs and set(refs) <= evidence_ids, 'review references missing or invalid evidence')
        if review.get('verdict') == 'accept':
            require(valid_refs and bool(refs), 'accepting review needs primary evidence IDs')
            for eid in refs if valid_refs else []:
                require(evidence_map.get(eid, {}).get('result') in ACCEPTED_RESULTS,
                        'accepting review references unsuccessful evidence: ' + str(eid))
        if review.get('verdict') != 'accept':
            require(review.get('requirement_id') in unresolved, 'nonaccepting review must remain unresolved')
    adaptive = data.get('team_policy')
    require(isinstance(adaptive, dict) and adaptive.get('schema_version') == 'chatbot.team/1', 'current team_policy chatbot.team/1 required')
    if isinstance(adaptive, dict) and adaptive.get('schema_version') == 'chatbot.team/1':
        import team_policy
        if stage in stages[2:]:
            require(completion.get('package_hash') == team_policy.snapshot_hash(data), 'stale frozen companion package')
        require(set(adaptive.get('scope', {}).get('active_requirement_ids', [])) == active, 'active profile and team scope differ')
        assignments = adaptive.get('assignments', {})
        for row in requirements:
            if row.get('id') not in baseline and text(row.get('id')):
                require(assignments.get(row['id'], {}).get('domain_id') == row.get('domain_id'),
                        'project requirement domain differs from accepted record: ' + row['id'])
        errors.extend(team_policy.check(adaptive, expected, runs, completion.get('package_hash'), root=source_root,
                                        ready=stage in stages[2:], requirement_records=requirements))
        if stage in stages[2:]:
            for finding in data.get('findings', []):
                if finding.get('severity') in {'critical', 'fatal_to_version'} and (not finding.get('requirement_ids') or set(finding['requirement_ids']) & active or adaptive['scope']['kind'] == 'stage'):
                    require(finding.get('resolution', finding.get('status')) in {'fixed', 'rebutted'}, 'open critical finding blocks acceptance')
            require(not (unresolved & active), 'unresolved active criteria block scoped completion')
            expected_status = 'stage_complete' if adaptive.get('scope', {}).get('kind') == 'stage' else 'scoped_complete'
            require(completion.get('status') == expected_status, 'local/stage completion status differs')
            completed = {r.get('id'): r for r in runs if r.get('status') == 'completed'}
            for review in reviews:
                row = adaptive.get('assignments', {}).get(review.get('requirement_id'), {})
                expected_run = row.get('judge_run') or row.get('qa_run')
                require(review.get('run_id') == expected_run and expected_run in completed, 'review not bound to accepted independent run')
                require(review.get('actor_id') == completed.get(expected_run, {}).get('actor_id'), 'review actor differs from actual run')
                require(review.get('package_hash') == completion.get('package_hash'), 'stale independent review package')
            require({r.get('requirement_id') for r in reviews} == active, 'every active criterion needs a substantive independent review')
    if stage in stages[3:]:
        require(bool(completion.get('deployed_version')) and bool(completion.get('deployment_evidence_ids')), 'deployed stage needs version and receipts')
        require(set(completion.get('deployment_evidence_ids', [])) <= evidence_ids, 'missing deployment evidence')
        for eid in completion.get('deployment_evidence_ids', []):
            require(evidence_map.get(eid, {}).get('result') in ('pass', 'passed', 'accepted', 'observed'),
                    'deployment evidence has not succeeded: ' + str(eid))
    if stage == 'observed_in_chat':
        require(bool(completion.get('chat_evidence_ids')) and set(completion.get('chat_evidence_ids', [])) <= evidence_ids, 'chat observation evidence required')
        for eid in completion.get('chat_evidence_ids', []):
            item = evidence_map.get(eid, {})
            require(item.get('result') in ('pass', 'passed', 'observed') and text(item.get('actual_observation_ref')),
                    'chat observation needs successful actual observation evidence: ' + str(eid))
    assessments = completion.get('assessments', {})
    require(isinstance(assessments, dict), 'completion.assessments must be object')
    for axis, row in assessments.items() if isinstance(assessments, dict) else []:
        require(axis in {'specification', 'code', 'integration', 'device', 'human'}, 'unknown readiness axis: ' + str(axis))
        if not isinstance(row, dict):
            require(False, 'readiness assessment must be object: ' + str(axis)); continue
        status = row.get('status')
        require(status in ('not_assessed', 'pending', 'passed', 'failed', 'not_applicable'), 'invalid readiness axis status: ' + str(axis))
        require(text(row.get('scope')), 'readiness axis scope required: ' + str(axis))
        refs = row.get('evidence_ids', [])
        valid_refs = isinstance(refs, list) and all(text(x) for x in refs) and len(refs) == len(set(refs))
        require(valid_refs and set(refs) <= evidence_ids, 'readiness axis has missing/invalid evidence: ' + str(axis))
        if status == 'not_applicable':
            require(text(row.get('reason')), 'not-applicable readiness axis needs reason: ' + str(axis))
        if status == 'passed':
            require(valid_refs and bool(refs), 'passed readiness axis needs evidence: ' + str(axis))
            for eid in refs if valid_refs else []:
                item = evidence_map.get(eid, {})
                require(item.get('result') in ('pass', 'passed', 'accept', 'accepted'), 'passed readiness axis has unsuccessful evidence: ' + str(axis))
                if axis == 'human':
                    require(item.get('kind') == 'human' and text(item.get('actual_observation_ref')),
                            'human readiness needs actual human observation evidence')
                if axis == 'device':
                    require(item.get('kind') == 'device' and text(item.get('actual_observation_ref')),
                            'device readiness needs actual target observation evidence')
    return errors


def check(data, source_root=None):
    try:
        return _check(data, source_root)
    except (TypeError, ValueError, AttributeError, KeyError, IndexError) as exc:
        return ['malformed typed round fields: ' + type(exc).__name__]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text())
        issues = check(data, source_root=args.file.parent)
    except (OSError, ValueError, IndexError, KeyError, TypeError, AttributeError) as error:
        print('INVALID: ' + str(error))
        sys.exit(1)
    for issue in issues:
        print('INVALID: ' + issue)
    if issues:
        sys.exit(1)
    print('Traceability structure valid; product quality and evidence truth require review.')
