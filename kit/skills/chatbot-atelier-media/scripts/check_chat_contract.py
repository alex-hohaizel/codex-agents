#!/usr/bin/env python3
"""Validate chatbot.blueprint/3 records. This is structural, not runtime proof."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from check_platform_adapter import validate as validate_adapter, PLATFORMS



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

MATURITIES = {'draft', 'specified', 'integrated'}
STATES = {'active', 'conditional', 'not_applicable', 'unknown'}
REQUIREMENT_STATES = {'active', 'deferred', 'excluded', 'not_applicable'}
CAPABILITY_STATES = {'unverified', 'candidate', 'catalog_verified', 'specified', 'configured', 'exercised', 'unsupported'}
ATTEMPT_RESULTS = {'passed', 'failed', 'unknown', 'cancelled', 'uncertain', 'pending', 'running'}
EVIDENCE_RESULTS = {'pass', 'passed', 'failed', 'unknown', 'cancelled', 'uncertain', 'accepted', 'rejected', 'observed'}
EVIDENCE_KINDS = {'source', 'code', 'execution', 'human', 'telemetry', 'live_provider', 'integration', 'device'}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, nonempty_list=False):
    return (isinstance(value, list) and all(nonempty(x) for x in value)
            and len(value) == len(set(value)) and (bool(value) or not nonempty_list))


def sha256(value):
    return isinstance(value, str) and re.fullmatch(r'[a-fA-F0-9]{64}', value) is not None


def brief_hash(brief):
    """Identity of the declared current brief, not proof of the owner's consent."""
    return hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def attempt_hash(attempt):
    """Freeze the declared run, inputs, parameters, operations and outcome."""
    return brief_hash(attempt)


def contract_hash(data):
    """Pin the declared semantic contract, excluding observations about it.

    This conservative scope is the complete current blueprint. Attempts and
    evidence must be renewed after a normative definition changes; historical
    records remain readable and are never silently re-signed.
    """
    fields = ('brief', 'applicability', 'requirements', 'systems', 'interactions',
              'journeys', 'operations', 'recipes', 'platform_adapters')
    subject = {field: data.get(field) for field in fields}
    subject['journeys'] = [{key: value for key, value in row.items()
                            if key not in {'attempt_ids', 'evidence_ids', 'verification'}}
                           if isinstance(row, dict) else row
                           for row in data.get('journeys', [])]
    return brief_hash(subject)


def _validate(data):
    errors = []
    def error(message): errors.append(message)
    if not isinstance(data, dict): return ['root must be an object']
    if data.get('schema_version') != 'chatbot.blueprint/3':
        error('schema_version must be chatbot.blueprint/3; unsupported record format')
    maturity = data.get('completion', {}).get('maturity') if isinstance(data.get('completion'), dict) else None
    if maturity not in MATURITIES: error('completion.maturity must be draft/specified/integrated')
    strict = maturity in {'specified', 'integrated'}
    tables = {}
    for field in ('applicability', 'requirements', 'systems', 'interactions', 'journeys', 'operations', 'recipes', 'attempts', 'evidence', 'platform_adapters'):
        rows = data.get(field)
        if not isinstance(rows, list):
            error(field + ' must be a list'); rows = []
        table = {}
        for index, row in enumerate(rows):
            if not isinstance(row, dict): error(f'{field}[{index}] must be object'); continue
            identity = row.get('id')
            if not isinstance(identity, str) or not identity.strip():
                error(f'{field}[{index}] missing nonempty id'); continue
            if identity in table: error(f'{field} duplicate id {identity}')
            table[identity] = row
        tables[field] = table
    brief = data.get('brief')
    if not isinstance(brief, dict): error('brief must be object'); brief = {}
    if strict:
        for field in ('id', 'version', 'user_intent'):
            if not brief.get(field): error('brief.' + field + ' required for specification')
        if not brief.get('audiences') or not brief.get('platforms'):
            error('brief audiences/platforms required')
        for field in ('applicability', 'requirements', 'systems', 'journeys'):
            if not tables[field]: error(field + ' must not be empty for specification')
    selected = brief.get('platforms', [])
    if strict and (not isinstance(selected, list) or not selected or any(x not in PLATFORMS for x in selected) or len(selected) != len(set(selected))):
        error('brief.platforms must contain explicit unique selected platforms')
        selected = []
    for key, adapter in tables['platform_adapters'].items():
        errors.extend(key + ': ' + issue for issue in validate_adapter(adapter))
        if strict and adapter.get('maturity') not in {'specified', 'exercised'}:
            error(key + ' selected adapter not specified')
        if strict and adapter.get('platform') not in selected:
            error(key + ' adapter platform not selected')
        if maturity == 'integrated' and adapter.get('maturity') != 'exercised':
            error(key + ' integrated scope needs exercised adapter')
    if strict and set(selected) != {a.get('platform') for a in tables['platform_adapters'].values()}:
        error('every selected platform needs a current adapter contract')
    for key, row in tables['applicability'].items():
        if row.get('state') not in STATES: error(key + ' invalid applicability state')
        if not row.get('reason'): error(key + ' applicability reason required')
        if strict and row.get('state') == 'unknown': error(key + ' unknown applicability blocks specified scope')
        if row.get('state') == 'active' and key not in tables['systems']:
            error(key + ' active system missing')
    active_requirements = set()
    for key, row in tables['requirements'].items():
        state = row.get('state', 'active')
        if state not in REQUIREMENT_STATES: error(key + ' invalid requirement state')
        if state == 'active': active_requirements.add(key)
        if strict:
            for field in ('intent', 'owner', 'acceptance', 'negative_probe'):
                if not nonempty(row.get(field)): error(key + ' missing ' + field)
            if state != 'active':
                if not nonempty(row.get('scope_decision_ref')) or not nonempty(row.get('reason')):
                    error(key + ' nonactive requirement needs explicit scope decision and reason')
                if state == 'deferred' and not nonempty(row.get('due_gate')):
                    error(key + ' deferred requirement needs due_gate')
    links = {'requirement_ids': 'requirements', 'system_ids': 'systems', 'operation_ids': 'operations', 'recipe_ids': 'recipes', 'attempt_ids': 'attempts', 'evidence_ids': 'evidence', 'adapter_ids': 'platform_adapters'}
    def ids(row, field):
        value = row.get(field, [])
        return value if strings(value) else []
    for field in ('systems', 'interactions', 'journeys', 'operations', 'recipes', 'attempts', 'evidence'):
        for key, row in tables[field].items():
            for link, target in links.items():
                if link not in row: continue
                values = row[link]
                if not strings(values): error(key + ' ' + link + ' must be unique string list'); continue
                for value in values:
                    if not isinstance(value, str) or value not in tables[target]: error(key + ' dangling ' + link + ': ' + str(value))
            if strict and field in ('systems', 'journeys', 'operations', 'recipes'):
                for required in ('owner', 'requirement_ids'):
                    if not row.get(required): error(key + ' missing ' + required)
            if field == 'systems' and strict:
                for required in ('inputs', 'outputs', 'rules', 'failure', 'acceptance_vectors'):
                    if not row.get(required): error(key + ' missing ' + required)
                rules = row.get('rules')
                if not isinstance(rules, list) or not rules:
                    error(key + ' rules must be a nonempty list')
                rule_ids = set()
                for rule in rules if isinstance(rules, list) else []:
                    if not (isinstance(rule, dict) and nonempty(rule.get('id'))
                            and nonempty(rule.get('algorithm')) and strings(rule.get('types'), True)
                            and strings(rule.get('order'), True)):
                        error(key + ' rule requires id/algorithm/types/order with typed lists')
                        continue
                    if rule['id'] in rule_ids: error(key + ' duplicate rule id ' + rule['id'])
                    rule_ids.add(rule['id'])
            if field == 'interactions':
                endpoints = row.get('system_ids')
                if not isinstance(endpoints, list) or len(set(endpoints)) < 2:
                    error(key + ' interaction needs at least two distinct systems')
                if strict and not all(row.get(x) for x in ('cause', 'effect', 'failure', 'acceptance')):
                    error(key + ' interaction missing cause/effect/failure/acceptance')
            if field == 'journeys' and strict:
                if row.get('channel_scope') != 'internal' and not row.get('adapter_ids'):
                    error(key + ' user journey needs selected adapter_ids')
                for required in ('trigger', 'audience', 'outcome', 'delivery', 'recovery', 'system_ids'):
                    if not row.get(required): error(key + ' missing ' + required)
            if field == 'operations' and strict:
                for required in ('inputs', 'outputs', 'consumer', 'capability_status', 'recipe_ids'):
                    if not row.get(required): error(key + ' missing ' + required)
                if row.get('capability_status') not in CAPABILITY_STATES:
                    error(key + ' invalid capability_status')
            if field == 'recipes' and strict:
                for required in ('operation_ids', 'steps', 'checks', 'stop', 'consumer'):
                    if not row.get(required): error(key + ' missing ' + required)
            if field == 'attempts':
                for required in ('operation_ids', 'recipe_ids', 'actual_run_id', 'input_snapshot', 'effective_parameters', 'result'):
                    if required not in row or row[required] in (None, '', []): error(key + ' missing actual ' + required)
                if not strings(row.get('operation_ids'), True) or not strings(row.get('recipe_ids'), True):
                    error(key + ' actual operation_ids/recipe_ids must be nonempty string lists')
                if not nonempty(row.get('actual_run_id')): error(key + ' actual_run_id must be nonempty string')
                snapshot = row.get('input_snapshot')
                if not isinstance(snapshot, dict) or not sha256(snapshot.get('hash')):
                    error(key + ' actual input_snapshot needs hash')
                if not isinstance(row.get('effective_parameters'), dict):
                    error(key + ' missing actual effective_parameters object')
                if row.get('result') not in ATTEMPT_RESULTS: error(key + ' invalid attempt result')
                for oid in ids(row, 'operation_ids'):
                    if not any(oid in ids(tables['recipes'].get(rid, {}), 'operation_ids')
                               and rid in ids(tables['operations'].get(oid, {}), 'recipe_ids')
                               for rid in ids(row, 'recipe_ids')):
                        error(key + ' attempt operation/recipe scope mismatch: ' + oid)
            if field == 'evidence':
                for required in ('kind', 'artifact', 'sha256', 'procedure', 'result', 'limitations'):
                    if required not in row or row[required] is None or row[required] == '': error(key + ' missing evidence ' + required)
                if row.get('kind') in ('human', 'live_provider') and not row.get('actual_observation_ref'):
                    error(key + ' needs actual observation reference')
                if row.get('kind') not in EVIDENCE_KINDS: error(key + ' invalid evidence kind')
                if row.get('result') not in EVIDENCE_RESULTS: error(key + ' invalid evidence result')
                if not sha256(row.get('sha256')): error(key + ' evidence sha256 must be hex SHA256')
                if not isinstance(row.get('limitations'), list) or not all(nonempty(x) for x in row['limitations']):
                    error(key + ' evidence limitations must be string list')
    if strict:
        for rid in active_requirements:
            for field in ('systems', 'journeys', 'operations', 'recipes'):
                if not any(rid in ids(row, 'requirement_ids') for row in tables[field].values()):
                    error(rid + ' has no ' + field + ' coverage')
        for key, row in tables['operations'].items():
            if not any(key in ids(tables['recipes'].get(ref, {}), 'operation_ids') for ref in ids(row, 'recipe_ids')):
                error(key + ' has no matching operation/recipe binding')
    if maturity == 'integrated':
        if not tables['attempts'] or not tables['evidence']: error('integrated maturity needs actual attempts and evidence')
        subject = {'brief_id': brief.get('id'), 'brief_version': brief.get('version'), 'brief_sha256': brief_hash(brief),
                   'contract_sha256': contract_hash(data)}
        for key, row in tables['journeys'].items():
            if not row.get('attempt_ids') or not row.get('evidence_ids'): error(key + ' integrated journey missing actual attempt/evidence links')
            if row.get('verification') != 'passed': error(key + ' integrated journey not passed')
            j_attempts, j_evidence, j_operations = ids(row, 'attempt_ids'), ids(row, 'evidence_ids'), ids(row, 'operation_ids')
            if not j_operations: error(key + ' integrated journey needs explicit operation_ids')
            covered_operations, covered_requirements = set(), set()
            for aid in j_attempts:
                attempt = tables['attempts'].get(aid, {})
                if attempt.get('result') != 'passed': error(key + ' linked attempt not passed: ' + aid)
                if attempt.get('subject') != subject: error(key + ' attempt subject differs from current brief or semantic contract: ' + aid)
                attempt_ops = set(ids(attempt, 'operation_ids'))
                if not attempt_ops or not attempt_ops <= set(j_operations):
                    error(key + ' attempt outside journey operation scope: ' + aid)
            for eid in j_evidence:
                evidence = tables['evidence'].get(eid, {})
                if evidence.get('result') not in ('pass', 'passed'): error(key + ' linked evidence not passed: ' + eid)
                e_attempts = ids(evidence, 'attempt_ids')
                if not e_attempts or not set(e_attempts) <= set(j_attempts):
                    error(key + ' evidence not bound to journey attempts: ' + eid)
                snapshots = evidence.get('attempt_sha256s')
                if not isinstance(snapshots, dict) or set(snapshots) != set(e_attempts):
                    error(key + ' evidence needs exact attempt_sha256s: ' + eid)
                    snapshots = {}
                for aid in e_attempts:
                    if aid in tables['attempts'] and snapshots.get(aid) != attempt_hash(tables['attempts'][aid]):
                        error(key + ' evidence attempt snapshot differs: ' + aid)
                if evidence.get('kind') not in ('execution', 'integration', 'device', 'live_provider') or evidence.get('result') not in ('pass', 'passed'):
                    continue
                for aid in e_attempts:
                    attempt = tables['attempts'].get(aid, {})
                    if attempt.get('result') != 'passed' or attempt.get('subject') != subject: continue
                    for oid in ids(attempt, 'operation_ids'):
                        if oid in j_operations:
                            covered_operations.add(oid)
                            covered_requirements.update(ids(tables['operations'].get(oid, {}), 'requirement_ids'))
            if not set(j_operations) <= covered_operations: error(key + ' operations lack successful linked execution evidence')
            if not set(ids(row, 'requirement_ids')) <= covered_requirements: error(key + ' requirements lack successful operation coverage')
            for oid in j_operations:
                if tables['operations'].get(oid, {}).get('capability_status') != 'exercised':
                    error(key + ' integrated operation capability not exercised: ' + oid)
        if data.get('completion', {}).get('unknowns'): error('integrated claimed scope has unresolved unknowns')
    return errors


def validate(data):
    try:
        return _validate(data)
    except (TypeError, ValueError, AttributeError, KeyError) as exc:
        return ['malformed typed blueprint fields: ' + type(exc).__name__]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    parser.add_argument('--subject', action='store_true', help='Read-only current brief/semantic-contract pins; not execution evidence')
    args = parser.parse_args()
    try:
        data = strict_json_loads(args.path.read_text())
        if args.subject:
            if not isinstance(data, dict) or data.get('schema_version') != 'chatbot.blueprint/3' or not isinstance(data.get('brief'), dict):
                raise ValueError('Current chatbot.blueprint/3 object and brief required for subject pins')
            brief = data.get('brief', {})
            print(json.dumps({'brief_id': brief.get('id'), 'brief_version': brief.get('version'),
                              'brief_sha256': brief_hash(brief), 'contract_sha256': contract_hash(data)},
                             ensure_ascii=False, indent=2))
            return 0
        errors = validate(data)
    except (OSError, ValueError, TypeError) as exc:
        errors = ['cannot read valid record: ' + str(exc)]
    print(json.dumps({'ok': not errors, 'errors': errors, 'proof_limit': 'Structural consistency only; does not prove actual execution, observation, privacy or human quality.'}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
