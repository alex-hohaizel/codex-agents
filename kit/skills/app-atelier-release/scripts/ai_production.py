#!/usr/bin/env python3
"""Check declared AI/data/media artifacts; no acquisition, model loading or effects.

Only Python's standard library is used. The emitted JSON Schema describes these
13 records; this is not a general JSON Schema engine or a second project ledger.
"""
import argparse
from datetime import datetime, timedelta
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re

VERSION = 'atelier.ai-production/1'
MAX_JSON = 2 * 1024 * 1024
MAX_JSON_TOTAL = 16 * 1024 * 1024
MAX_ROWS = 100000
S = {'type': 'string', 'minLength': 1, 'maxLength': 8000}
ID = {'type': 'string', 'minLength': 1, 'maxLength': 240}
UINT = {'type': 'integer', 'minimum': 0}
AMOUNT = {'type': 'string', 'maxLength': 40, 'pattern': r'^(0|[1-9][0-9]*)(\.[0-9]{1,9})?$'}


def arr(items, maximum=MAX_ROWS):
    return {'type': 'array', 'items': items, 'maxItems': maximum}


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required,
            'additionalProperties': False}


def choice(*values):
    return {'type': 'string', 'enum': list(values)}


PIN = obj({'path': S, 'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
           'bytes': UINT}, ['path', 'sha256'])
MONEY = obj({'currency': {'type': 'string', 'pattern': '^[A-Z]{3}$'}, 'amount': AMOUNT})
BUDGET = obj({'max_seconds': UINT, 'max_bytes': UINT, 'max_cost': MONEY})
STATUS = choice('planned', 'running', 'completed', 'failed', 'interrupted', 'outcome_unknown')
EVIDENCE = obj({'proof_type': S, 'actor': ID, 'procedure': S,
                'environment': S, 'evidence_ref': S})
RETRY_POLICY = obj({'mode': choice('known-failure-only'), 'basis_ref': S,
                    'retry_number': {'type': 'integer', 'minimum': 1},
                    'max_retries': {'type': 'integer', 'minimum': 1}})
SPLIT_ROW = obj({'record_id': ID, 'group_id': ID, 'prediction_at': S,
                 'features_available_at': S, 'label_available_at': S})
PAYLOADS = {
    'SourceContract': obj({
        'locator': S, 'acquisition': choice('api', 'export', 'http', 'browser', 'local'),
        'rights_ref': S, 'privacy_ref': S, 'schema_ref': S, 'consumer': S,
        'rate_limit': obj({'requests': UINT, 'period_seconds': {'type': 'integer', 'minimum': 1}}),
        'bounds': obj({'requests': UINT, 'bytes': UINT, 'retries': UINT}),
    }),
    'DatasetManifest': obj({
        'source_ids': arr(ID, 1000), 'record_ids': arr(ID), 'dedup_key': S,
        'transform_ref': S,
        'counts': obj({key: UINT for key in ('received', 'accepted', 'duplicates', 'quarantined', 'excluded')}),
        'quarantine': arr(obj({'id': ID, 'reason': S})),
        'coverage': obj({'scope': S, 'status': choice('complete', 'partial'),
                         'expected': UINT, 'observed': UINT, 'gaps': arr(S, 1000),
                         'next_cursor': {'type': ['string', 'null']}},
                        ['scope', 'status', 'observed', 'gaps']),
    }),
    'SplitManifest': obj({
        'dataset_id': ID, 'strategy': choice('random', 'group', 'time', 'group_time'),
        'partitions': obj({key: arr(ID) for key in ('train', 'validation', 'test')}),
        'excluded_ids': arr(ID), 'rows': arr(SPLIT_ROW), 'embargo_seconds': UINT,
        'label_cutoffs': obj({key: S for key in ('train', 'validation', 'test')}),
    }),
    'FeatureManifest': obj({
        'dataset_id': ID, 'split_id': ID, 'fit_record_ids': arr(ID),
        'features': arr(obj({'name': ID, 'source_ref': S,
                             'availability': arr(obj({'record_id': ID, 'available_at': S}))}), 1000),
    }),
    'PredictionContract': obj({
        'decision': S, 'target': S, 'unit': S, 'horizon_seconds': {'type': 'integer', 'minimum': 1},
        'kind': choice('regression', 'classification', 'ranking', 'probability', 'cpa'),
        'feature_manifest_id': ID, 'forbidden_features': arr(ID, 1000),
        'zero_denominator_policy': choice('abstain', 'separate-target', 'not-applicable'),
        'currency': S, 'attribution_window': S,
    }, ['decision', 'target', 'unit', 'horizon_seconds', 'kind',
        'feature_manifest_id', 'forbidden_features', 'zero_denominator_policy']),
    'WorkflowRun': obj({
        'recipe_ref': S, 'status': STATUS,
        'nodes': arr(obj({'id': ID, 'status': STATUS, 'completion_attempt_id': ID,
                          'attempts': arr(obj({'id': ID, 'status': STATUS, 'receipt_ref': S},
                                              ['id', 'status']), 1000)}, ['id', 'status', 'attempts']), 1000),
        'effects': arr(obj({'id': ID, 'status': choice('planned', 'dispatched', 'known_success',
                                                        'known_failure', 'outcome_unknown'),
                           'retry_requested': {'type': 'boolean'}, 'receipt_ref': S,
                           'retry_policy': RETRY_POLICY},
                          ['id', 'status', 'retry_requested']), 1000),
    }),
    'EvaluationPlan': obj({
        'case_ids': arr(ID), 'must_case_ids': arr(ID), 'author': ID,
        'requires_independent': {'type': 'boolean'}, 'baseline_ref': S,
        'candidate_ref': S, 'rubric_ref': S, 'required_proofs': arr(ID, 1000),
    }),
    'EvaluationReport': obj({
        'plan_id': ID, 'plan_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
        'reviewer': ID, 'conclusion': choice('recorded-pass', 'recorded-fail', 'incomplete'),
        'results': arr(obj({'case_id': ID, 'verdict': choice('pass', 'fail', 'unknown', 'blocked'),
                            'observations': arr(EVIDENCE, 1000)})),
    }),
    'TrainingRecipe': obj({
        'dataset_id': ID, 'split_id': ID, 'method': choice('baseline', 'lora', 'full', 'distillation'),
        'base_model': obj({'id': ID, 'revision': S, 'license_ref': S}),
        'tokenizer': obj({'id': ID, 'revision': S, 'template_ref': S}),
        'measured_gap_ref': S, 'environment_ref': S, 'budget': BUDGET,
        'adapter': obj({'rank': {'type': 'integer', 'minimum': 1},
                        'target_modules': arr(ID, 1000), 'config_ref': S}),
    }, ['dataset_id', 'split_id', 'method', 'base_model', 'tokenizer',
        'measured_gap_ref', 'environment_ref', 'budget']),
    'ModelBundle': obj({
        'recipe_id': ID, 'base_revision': S, 'tokenizer_revision': S,
        'format': choice('safetensors', 'gguf', 'onnx', 'coreml', 'other-reviewed'),
        'loader_review_ref': S, 'remote_code': {'const': False, 'type': 'boolean'},
        'files': arr(PIN, 1000), 'weights_ref': S, 'tokenizer_ref': S,
        'signature_ref': S, 'evaluation_report_id': ID,
        'serving_proof_ref': S, 'adapter_ref': S,
    }, ['recipe_id', 'base_revision', 'tokenizer_revision', 'format', 'loader_review_ref',
        'remote_code', 'files', 'weights_ref', 'tokenizer_ref', 'signature_ref',
        'evaluation_report_id', 'serving_proof_ref']),
    'BatchPlan': obj({
        'recipe_ref': S, 'budget': MONEY,
        'items': arr(obj({'item_id': ID, 'variant': ID, 'master_ref': S, 'consumer': S})),
    }),
    'ItemManifest': obj({
        'plan_id': ID, 'item_id': ID, 'variant': ID, 'master_ref': S,
        'outputs': arr(PIN, 1000), 'verdict': choice('unreviewed', 'accepted', 'rejected'),
        'review_ref': S, 'consumer_proof_ref': S, 'evaluation_report_id': ID,
    }, ['plan_id', 'item_id', 'variant', 'master_ref', 'outputs', 'verdict']),
    'GenerationBatch': obj({
        'plan_id': ID, 'status': choice('open', 'closed'),
        'overheads': arr(obj({'id': ID, 'phase': S, 'cost': MONEY, 'receipt_ref': S},
                             ['id', 'phase']), 1000),
        'attempts': arr(obj({'id': ID, 'item_id': ID, 'variant': ID,
                            'status': choice('planned', 'dispatched', 'succeeded', 'failed',
                                             'rejected', 'cancelled', 'outcome_unknown'),
                            'cost': MONEY, 'receipt_ref': S, 'output_manifest_id': ID,
                            'retry_requested': {'type': 'boolean'}, 'retry_policy': RETRY_POLICY},
                           ['id', 'item_id', 'variant', 'status', 'retry_requested'])),
        'outcomes': arr(obj({'item_id': ID, 'variant': ID,
                            'status': choice('accepted', 'rejected', 'failed', 'missing',
                                             'cancelled', 'outcome_unknown'), 'manifest_id': ID},
                           ['item_id', 'variant', 'status'])),
    }),
}


class ArtifactError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ArtifactError(message)


def finite_json(value, depth=0, ancestors=None):
    """Reject non-JSON/nonfinite direct API values too, including nested extensions."""
    require(depth <= 100, 'JSON nesting exceeds bounded depth')
    if isinstance(value, (dict, list)):
        ancestors = set() if ancestors is None else ancestors
        require(id(value) not in ancestors, 'cyclic value is not JSON')
        ancestors.add(id(value))
        if isinstance(value, dict):
            require(all(isinstance(key, str) for key in value), 'JSON object keys must be strings')
            children = value.values()
        else:
            children = value
        for child in children:
            finite_json(child, depth + 1, ancestors)
        ancestors.remove(id(value))
    elif type(value) is float:
        require(math.isfinite(value), 'nonfinite JSON number rejected')
    else:
        require(value is None or type(value) in (str, int, bool), 'value is not a JSON scalar')


def record_sha256(record):
    """Canonical complete-record content identity, independent of JSON whitespace."""
    finite_json(record)
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def schema_document():
    definitions = {}
    for kind, payload in PAYLOADS.items():
        definitions[kind] = obj({
            'schema_version': {'const': VERSION, 'type': 'string'},
            'kind': {'const': kind, 'type': 'string'}, 'id': ID, 'project_id': ID,
            'project_root': S, 'owner': ID, 'inputs': arr(PIN, 1000),
            'payload': payload, 'extensions': {'type': 'object'},
        }, ['schema_version', 'kind', 'id', 'project_id', 'project_root', 'owner', 'inputs', 'payload'])
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'urn:atelier:ai-production:1',
            'title': 'Declared AI/data/media artifacts; structure is not execution or quality proof',
            'oneOf': [{'$ref': '#/$defs/' + kind} for kind in PAYLOADS], '$defs': definitions}


def structure(value, spec, label):
    """Validate only the fixed structural vocabulary emitted above, not external schemas."""
    types = {'string': lambda x: isinstance(x, str), 'integer': lambda x: type(x) is int,
             'boolean': lambda x: type(x) is bool, 'object': lambda x: isinstance(x, dict),
             'array': lambda x: isinstance(x, list), 'null': lambda x: x is None}
    allowed = spec.get('type')
    if allowed:
        require(any(types[t](value) for t in ([allowed] if isinstance(allowed, str) else allowed)),
                label + ': wrong type')
    if 'const' in spec:
        require(value == spec['const'], label + ': wrong constant')
    if 'enum' in spec:
        require(value in spec['enum'], label + ': unsupported value')
    if isinstance(value, str):
        require(len(value) >= spec.get('minLength', 0) and len(value) <= spec.get('maxLength', MAX_JSON),
                label + ': invalid text length')
        require(not spec.get('minLength') or value.strip(), label + ': blank text')
        if 'pattern' in spec:
            require(re.fullmatch(spec['pattern'], value) is not None, label + ': invalid format')
    if type(value) is int and 'minimum' in spec:
        require(value >= spec['minimum'], label + ': below minimum')
    if isinstance(value, list):
        require(len(value) <= spec.get('maxItems', MAX_ROWS), label + ': too many items')
        for i, item in enumerate(value):
            structure(item, spec['items'], label + '[' + str(i) + ']')
    if isinstance(value, dict) and 'properties' in spec:
        require(set(spec.get('required', [])) <= set(value), label + ': missing required fields')
        require(spec.get('additionalProperties') is not False or set(value) <= set(spec['properties']),
                label + ': unexpected fields; use extensions for domain additions')
        for key, item in value.items():
            if key in spec['properties']:
                structure(item, spec['properties'][key], label + '.' + key)


def unique(values, label):
    require(len(values) == len(set(values)), label + ': duplicate identity')
    return set(values)


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(result.tzinfo is not None, 'timestamp needs an explicit timezone')
        return result
    except (ValueError, TypeError) as error:
        raise ArtifactError('invalid timezone-aware timestamp: ' + str(value)) from error


def safe_file(root, ref):
    pure = PurePosixPath(ref)
    require(ref and not pure.is_absolute() and '..' not in pure.parts and '\\' not in ref and ':' not in ref
            and pure.as_posix() == ref, 'unsafe relative path: ' + ref)
    path = root
    for part in pure.parts:
        require(part not in ('.aws', '.ssh') and not re.fullmatch(
            r'(?i)(\.env.*|auth\.json|owner-credentials\.json|credentials.*|.*\.(pem|key|p12|pfx))', part),
            'credential path cannot be a production artifact input')
        path = path / part
        require(not path.is_symlink(), 'linked artifact/input path rejected')
    require(path.is_file(), 'missing artifact/input file: ' + ref)
    return path


def pin_bytes(root, pin, max_bytes):
    path = safe_file(root, pin['path'])
    size = path.stat().st_size
    require(size <= max_bytes, 'input exceeds declared hashing budget: ' + pin['path'])
    if 'bytes' in pin:
        require(size == pin['bytes'], 'input size drift: ' + pin['path'])
    hasher, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            count += len(chunk)
            require(count <= max_bytes, 'input grew beyond hashing budget')
            hasher.update(chunk)
    require(size == count == path.stat().st_size, 'input changed while hashing')
    require(hasher.hexdigest() == pin['sha256'], 'input SHA-256 drift: ' + pin['path'])


def load_record(root, ref):
    path = safe_file(root, ref)
    require(path.stat().st_size <= MAX_JSON, 'artifact exceeds 2 MiB')
    with path.open('rb') as stream:
        raw = stream.read(MAX_JSON + 1)
    require(len(raw) <= MAX_JSON, 'artifact grew beyond 2 MiB')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key: ' + key)
            result[key] = value
        return result
    def nonfinite(value):
        raise ArtifactError('nonfinite JSON number: ' + value)
    def finite_float(value):
        result = float(value)
        require(math.isfinite(result), 'nonfinite JSON numeric overflow: ' + value)
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite, parse_float=finite_float)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ArtifactError('invalid bounded UTF-8 JSON artifact') from error
    finite_json(value)
    return value, hashlib.sha256(raw).hexdigest()


def check_records(records, root, max_pin_bytes=64 * 1024 * 1024):
    require(0 < len(records) <= 1000, 'supply 1 to 1000 explicit artifacts')
    require(type(max_pin_bytes) is int and 0 < max_pin_bytes <= 64 * 1024 ** 3,
            'hashing bound must be 1 byte to 64 GiB')
    root = Path(root).resolve()
    require(root.is_dir(), 'project root must exist')
    index, checks, summaries, declared_pins = {}, [], {}, {}
    definitions = schema_document()['$defs']
    projects = set()
    for record in records:
        finite_json(record)
        require(isinstance(record, dict) and record.get('kind') in PAYLOADS, 'unknown artifact kind')
        structure(record, definitions[record['kind']], record['kind'])
        require(record['project_root'] == str(root), 'artifact belongs to a different canonical project root')
        projects.add(record['project_id'])
        key = (record['kind'], record['id'])
        require(key not in index, 'duplicate artifact kind/ID')
        index[key] = record
        pins = record['inputs']
        unique([pin['path'] for pin in pins], 'input pins')
        for pin in pins:
            require(pin['path'] not in declared_pins or declared_pins[pin['path']] == pin['sha256'],
                    'the same input path has conflicting versions; use immutable version paths')
            declared_pins[pin['path']] = pin['sha256']
            pin_bytes(root, pin, max_pin_bytes)
        def refs(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key.endswith('_ref'):
                        require(isinstance(item, str) and any(p['path'] == item for p in pins),
                                record['id'] + ': reference has no consumed input pin: ' + key)
                    else:
                        refs(item)
            elif isinstance(value, list):
                for item in value:
                    refs(item)
        refs(record['payload'])
    require(len(projects) == 1, 'cross-project artifact set rejected')
    def find(kind, ident):
        require((kind, ident) in index, 'missing referenced ' + kind + ': ' + ident)
        return index[(kind, ident)]['payload']
    def evaluation_covers(report_id, pins):
        report = find('EvaluationReport', report_id)
        require(report['conclusion'] == 'recorded-pass', 'evaluation has failed or missing proof')
        consumed = {(pin['path'], pin['sha256']) for pin in index[('EvaluationReport', report_id)]['inputs']}
        require(all((pin['path'], pin['sha256']) in consumed for pin in pins),
                'old evaluation does not bind the current output/master bytes')
    def retry_allowed(row, retryable, message):
        if not row['retry_requested']:
            return
        require(row['status'] in retryable, message)
        policy = row.get('retry_policy')
        require(policy and policy['mode'] == 'known-failure-only'
                and policy['retry_number'] <= policy['max_retries'] and row.get('receipt_ref'),
                'retry requires a pinned declared safe policy, observed failure receipt and remaining retry bound')
    for record in records:
        p, kind, ident = record['payload'], record['kind'], record['id']
        if kind == 'DatasetManifest':
            require(p['source_ids'], 'dataset has no declared source contract')
            for source in unique(p['source_ids'], 'source_ids'):
                find('SourceContract', source)
            unique(p['record_ids'], 'dataset records')
            c, coverage = p['counts'], p['coverage']
            require(c['received'] == sum(c[k] for k in ('accepted', 'duplicates', 'quarantined', 'excluded')),
                    'dataset denominator does not reconcile')
            require(c['accepted'] == len(p['record_ids']) and c['quarantined'] == len(p['quarantine']),
                    'dataset record/quarantine count mismatch')
            unique([row['id'] for row in p['quarantine']], 'quarantine rows')
            require(coverage['observed'] == c['received'], 'observed source-row denominator mismatch')
            if coverage['status'] == 'complete':
                require(coverage.get('expected') == coverage['observed'] and not coverage['gaps']
                        and not coverage.get('next_cursor'), 'complete coverage has missing/remaining source rows')
        elif kind == 'SplitManifest':
            dataset = find('DatasetManifest', p['dataset_id'])
            universe = set(dataset['record_ids'])
            sets = {key: unique(ids, key + ' split') for key, ids in p['partitions'].items()}
            unique(p['excluded_ids'], 'excluded IDs')
            all_ids = [item for values in p['partitions'].values() for item in values] + p['excluded_ids']
            require(unique(all_ids, 'split/excluded membership') == universe, 'split loses or invents dataset IDs')
            rows = {row['record_id']: row for row in p['rows']}
            require(len(rows) == len(p['rows']) and set(rows) == universe, 'split row metadata incomplete/duplicated')
            for key, members in sets.items():
                cutoff = timestamp(p['label_cutoffs'][key])
                for item in members:
                    row = rows[item]
                    require(timestamp(row['features_available_at']) <= timestamp(row['prediction_at']),
                            'future information leaks into prediction')
                    require(timestamp(row['label_available_at']) <= cutoff, 'label was unavailable at split cutoff')
            if p['strategy'] in ('group', 'group_time'):
                groups = [{rows[item]['group_id'] for item in sets[key]} for key in ('train', 'validation', 'test')]
                require(not any(a & b for i, a in enumerate(groups) for b in groups[i + 1:]), 'group leakage across splits')
            if p['strategy'] in ('time', 'group_time'):
                nonempty = [[timestamp(rows[item]['prediction_at']) for item in sets[key]]
                            for key in ('train', 'validation', 'test') if sets[key]]
                embargo = timedelta(seconds=p['embargo_seconds'])
                require(all(max(a) + embargo < min(b) for a, b in zip(nonempty, nonempty[1:])),
                        'time split order/embargo violated')
                populated = [key for key in ('train', 'validation', 'test') if sets[key]]
                for prior, later in zip(populated, populated[1:]):
                    require(timestamp(p['label_cutoffs'][prior]) <=
                            min(timestamp(rows[item]['prediction_at']) for item in sets[later]),
                            'earlier-partition labels were not available before later prediction')
        elif kind == 'FeatureManifest':
            split = find('SplitManifest', p['split_id'])
            require(split['dataset_id'] == p['dataset_id'], 'feature and split datasets differ')
            dataset = find('DatasetManifest', p['dataset_id'])
            require(unique(p['fit_record_ids'], 'fit records') <= set(split['partitions']['train']),
                    'preprocessing fit includes non-training rows')
            unique([row['name'] for row in p['features']], 'feature names')
            predictions = {row['record_id']: timestamp(row['prediction_at']) for row in split['rows']}
            for feature in p['features']:
                availability = {row['record_id']: row for row in feature['availability']}
                require(len(availability) == len(feature['availability']) and set(availability) == set(dataset['record_ids']),
                        'feature availability coverage incomplete/duplicated')
                require(all(timestamp(row['available_at']) <= predictions[key] for key, row in availability.items()),
                        'feature was unavailable at prediction time')
        elif kind == 'PredictionContract':
            features = find('FeatureManifest', p['feature_manifest_id'])
            require(not set(p['forbidden_features']) & {row['name'] for row in features['features']},
                    'forbidden post-outcome feature included')
            if p['kind'] == 'cpa':
                require(p.get('currency') and p.get('attribution_window')
                        and p['zero_denominator_policy'] != 'not-applicable',
                        'CPA requires currency, attribution window and zero-acquisition policy')
        elif kind == 'WorkflowRun':
            unique([row['id'] for row in p['nodes']], 'workflow nodes')
            unique([row['id'] for row in p['effects']], 'workflow effects')
            for node in p['nodes']:
                unique([row['id'] for row in node['attempts']], 'node attempts')
                for attempt in node['attempts']:
                    if attempt['status'] in ('completed', 'failed'):
                        require(attempt.get('receipt_ref'), 'terminal node attempt has no observed receipt')
                if node['status'] == 'completed':
                    require(any(row['id'] == node.get('completion_attempt_id') and row['status'] == 'completed'
                                for row in node['attempts'])
                            and all(row['status'] not in ('planned', 'running', 'outcome_unknown') for row in node['attempts']),
                            'node lacks explicit completed attempt or retains unknown work')
            for effect in p['effects']:
                retry_allowed(effect, {'known_failure'},
                              'unresolved/successful external outcome must be reconciled; only known failure can request retry')
                if effect['status'] in ('known_success', 'known_failure'):
                    require(effect.get('receipt_ref'), 'known effect has no observed receipt')
            if p['status'] == 'completed':
                require(all(row['status'] == 'completed' for row in p['nodes'])
                        and all(row['status'] in ('known_success', 'known_failure')
                                and not row['retry_requested'] for row in p['effects']),
                        'completed workflow contains unfinished/unknown work')
        elif kind == 'EvaluationPlan':
            cases = unique(p['case_ids'], 'evaluation cases')
            require(cases, 'evaluation plan has no cases')
            require(unique(p['must_case_ids'], 'must cases') <= cases, 'must case absent from plan')
            unique(p['required_proofs'], 'required proof types')
        elif kind == 'EvaluationReport':
            plan = find('EvaluationPlan', p['plan_id'])
            plan_record = index[('EvaluationPlan', p['plan_id'])]
            require(p['plan_sha256'] == record_sha256(plan_record), 'evaluation plan content changed; old report cannot be rebound')
            consumed = {(pin['path'], pin['sha256']) for pin in record['inputs']}
            require(all((pin['path'], pin['sha256']) in consumed for pin in plan_record['inputs']),
                    'evaluation report does not consume all current plan input pins')
            require(unique([r['case_id'] for r in p['results']], 'evaluation results') == set(plan['case_ids']),
                    'evaluation result denominator incomplete')
            require(not plan['requires_independent'] or p['reviewer'] != plan['author'],
                    'author cannot be declared independent reviewer')
            for row in p['results']:
                if row['verdict'] == 'pass':
                    require(row['observations'] and set(plan['required_proofs']) <=
                            {obs['proof_type'] for obs in row['observations']}, 'passed case missing required proof type')
            verdicts = {row['verdict'] for row in p['results']}
            expected = 'recorded-fail' if 'fail' in verdicts else ('incomplete' if verdicts & {'unknown', 'blocked'} else 'recorded-pass')
            require(p['conclusion'] == expected, 'evaluation conclusion hides failure or missing proof')
        elif kind == 'TrainingRecipe':
            find('DatasetManifest', p['dataset_id'])
            split = find('SplitManifest', p['split_id'])
            require(split['dataset_id'] == p['dataset_id'], 'training split dataset differs')
            require(split['partitions']['train'], 'training recipe has no training records')
            if p['method'] == 'lora':
                require(p.get('adapter') and p['adapter']['target_modules'], 'LoRA needs rank, target modules and config')
        elif kind == 'ModelBundle':
            recipe = find('TrainingRecipe', p['recipe_id'])
            require(p['base_revision'] == recipe['base_model']['revision']
                    and p['tokenizer_revision'] == recipe['tokenizer']['revision'], 'model base/tokenizer mismatch')
            require(p['files'], 'model bundle has no actual files')
            unique([row['path'] for row in p['files']], 'model files')
            require({p['weights_ref'], p['tokenizer_ref']} <= {row['path'] for row in p['files']},
                    'model bundle omits weights or tokenizer files')
            delivery_refs = {p['signature_ref']}
            if recipe['method'] == 'lora':
                require(p.get('adapter_ref'), 'LoRA bundle omits its pinned adapter')
            if p.get('adapter_ref'):
                delivery_refs.add(p['adapter_ref'])
            require(delivery_refs <= {row['path'] for row in p['files']},
                    'model bundle omits delivered adapter or signature members')
            for pin in p['files']:
                pin_bytes(root, pin, max_pin_bytes)
                require(Path(pin['path']).suffix.lower() not in ('.pkl', '.pickle', '.joblib', '.pt', '.pth', '.bin'),
                        'this bounded helper does not admit executable serialization; use the separately reviewed native loader contract')
            component_refs = {p['signature_ref'], p['serving_proof_ref']}
            if p.get('adapter_ref'):
                component_refs.add(p['adapter_ref'])
            evaluation_covers(p['evaluation_report_id'], p['files'] +
                              [pin for pin in record['inputs'] if pin['path'] in component_refs])
            evaluation = find('EvaluationReport', p['evaluation_report_id'])
            require(any(obs['proof_type'] == 'serving' and obs['evidence_ref'] == p['serving_proof_ref']
                        for row in evaluation['results'] for obs in row['observations']),
                    'model lacks an explicit serving observation bound to its consumed proof')
        elif kind == 'BatchPlan':
            unique([(row['item_id'], row['variant']) for row in p['items']], 'planned item/variant')
            require(p['items'], 'batch has no requested items')
        elif kind == 'ItemManifest':
            plan = find('BatchPlan', p['plan_id'])
            target = next((row for row in plan['items'] if (row['item_id'], row['variant']) == (p['item_id'], p['variant'])), None)
            require(target and target['master_ref'] == p['master_ref'], 'unplanned item/variant or master drift')
            unique([row['path'] for row in p['outputs']], 'item outputs')
            for pin in p['outputs']:
                pin_bytes(root, pin, max_pin_bytes)
            if p['verdict'] == 'accepted':
                require(p['outputs'] and p.get('review_ref') and p.get('consumer_proof_ref')
                        and p.get('evaluation_report_id'),
                        'accepted item lacks output/review/consumer record')
                evaluation_covers(p['evaluation_report_id'], p['outputs'] +
                                  [pin for pin in record['inputs'] if pin['path'] == p['master_ref']])
        elif kind == 'GenerationBatch':
            plan = find('BatchPlan', p['plan_id'])
            targets = {(row['item_id'], row['variant']) for row in plan['items']}
            unique([row['id'] for row in p['attempts']], 'batch attempts')
            outcomes = {(row['item_id'], row['variant']): row for row in p['outcomes']}
            require(len(outcomes) == len(p['outcomes']) and set(outcomes) == targets, 'batch outcomes lose or invent requested items')
            costs, unknown_costs, accepted = [], 0, 0
            for attempt in p['attempts']:
                pair = (attempt['item_id'], attempt['variant'])
                require(pair in targets, 'attempt refers to unplanned item/variant')
                retry_allowed(attempt, {'failed', 'rejected'},
                              'unresolved/successful batch effect cannot be retried before a known safe terminal result')
                if attempt.get('cost'):
                    require(attempt['cost']['currency'] == plan['budget']['currency'], 'mixed batch cost currencies')
                    costs.append(Decimal(attempt['cost']['amount']))
                elif attempt['status'] != 'planned':
                    unknown_costs += 1
                if attempt['status'] == 'succeeded':
                    require(attempt.get('receipt_ref') and attempt.get('output_manifest_id'), 'success has no receipt/output manifest')
                    item = find('ItemManifest', attempt['output_manifest_id'])
                    require(item['plan_id'] == p['plan_id'] and (item['item_id'], item['variant']) == pair, 'attempt output maps to wrong item')
            unique([row['id'] for row in p['overheads']], 'batch overheads')
            unknown_overheads = 0
            for overhead in p['overheads']:
                if overhead.get('cost'):
                    require(overhead['cost']['currency'] == plan['budget']['currency'], 'mixed batch cost currencies')
                    costs.append(Decimal(overhead['cost']['amount']))
                else:
                    unknown_overheads += 1
            for pair, outcome in outcomes.items():
                matching = [a for a in p['attempts'] if (a['item_id'], a['variant']) == pair]
                if outcome['status'] == 'accepted':
                    item = find('ItemManifest', outcome.get('manifest_id', ''))
                    require(item['verdict'] == 'accepted' and item['plan_id'] == p['plan_id']
                            and (item['item_id'], item['variant']) == pair
                            and any(a.get('output_manifest_id') == outcome['manifest_id'] and a['status'] == 'succeeded' for a in matching),
                            'accepted outcome lacks matching successful attempt and accepted item')
                    accepted += 1
                if any(a['status'] == 'outcome_unknown' for a in matching):
                    require(outcome['status'] == 'outcome_unknown', 'unknown attempt cannot be hidden by item outcome')
            with localcontext() as context:
                context.prec = 80
                spent = sum(costs, Decimal(0))
                unit_cost = str(spent / accepted) if accepted and not (unknown_costs or unknown_overheads) else None
            require(spent <= Decimal(plan['budget']['amount']), 'known batch cost exceeds budget')
            if p['status'] == 'closed':
                require(not (unknown_costs or unknown_overheads) and all(a['status'] not in ('planned', 'dispatched', 'outcome_unknown')
                        and not a['retry_requested'] for a in p['attempts'])
                        and all(o['status'] not in ('missing', 'outcome_unknown') for o in p['outcomes']), 'closed batch has missing/unknown work or cost')
            summaries[ident] = {'requested_items': len(targets), 'accepted_items': accepted,
                                'attempts': len(p['attempts']), 'known_cost': str(spent),
                                'currency': plan['budget']['currency'], 'unknown_cost_attempts': unknown_costs,
                                'unknown_cost_overheads': unknown_overheads,
                                'cost_per_accepted_item': unit_cost,
                                'all_requested_delivered': accepted == len(targets),
                                'declared_costs_complete': not (unknown_costs or unknown_overheads)}
        checks.append({'kind': kind, 'id': ident, 'declared_structure_and_invariants': 'passed'})
    return {'ok': True, 'schema_version': VERSION, 'records_checked': len(records),
            'checks': checks, 'batch_summaries': summaries,
            'quality_certified': False, 'authority_authenticated': False,
            'actual_execution_authenticated': False,
            'notice': 'Only declared structure, local pins and applicable cross-record invariants checked. No source completeness, semantic correctness, actual training, craft, playback, consumer success or owner acceptance is certified.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('schema', 'digest', 'check'))
    parser.add_argument('--root', type=Path)
    parser.add_argument('--input', action='append', default=[], help='explicit artifact path relative to project root; repeat as needed')
    parser.add_argument('--max-pin-bytes', type=int, default=64 * 1024 * 1024,
                        help='per-file hashing bound; never loads or executes model files')
    args = parser.parse_args(argv)
    try:
        if args.operation == 'schema':
            print(json.dumps(schema_document(), ensure_ascii=False, indent=2))
            return 0
        require(args.root is not None and args.root.is_dir(), '--root is required for check')
        require(0 < args.max_pin_bytes <= 64 * 1024 ** 3, 'hashing bound must be 1 byte to 64 GiB')
        root = args.root.resolve()
        require(0 < len(args.input) <= 1000, 'supply 1 to 1000 explicit artifacts')
        require(sum(safe_file(root, ref).stat().st_size for ref in args.input) <= MAX_JSON_TOTAL,
                'artifact set exceeds 16 MiB; use a capable native dataset workflow without dropping obligations')
        loaded = [load_record(root, ref) for ref in args.input]
        if args.operation == 'digest':
            require(len(loaded) == 1, 'digest requires exactly one explicit artifact')
            record = loaded[0][0]
            require(isinstance(record, dict) and record.get('kind') in PAYLOADS, 'unknown artifact kind')
            structure(record, schema_document()['$defs'][record['kind']], record['kind'])
            require(record['project_root'] == str(root), 'artifact belongs to a different canonical project root')
            result = {'ok': True, 'operation': 'digest', 'canonical_sha256': record_sha256(record),
                      'validation_scope': 'record identity/shape only; no input-pin or cross-record verification',
                      'quality_certified': False, 'authority_authenticated': False,
                      'actual_execution_authenticated': False}
        else:
            result = check_records([row[0] for row in loaded], root, args.max_pin_bytes)
        for ref, row in zip(args.input, loaded):
            require(load_record(root, ref)[1] == row[1], 'artifact changed during validation: ' + ref)
        result['artifact_files'] = [{'path': ref, 'sha256': row[1]} for ref, row in zip(args.input, loaded)]
    except (ArtifactError, OSError, ValueError, OverflowError, RecursionError) as error:
        result = {'ok': False, 'errors': [str(error)], 'quality_certified': False,
                  'authority_authenticated': False, 'actual_execution_authenticated': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
