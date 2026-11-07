#!/usr/bin/env python3
"""Game Model 4 production extension; structural obligations, never quality proof.

The canonical data remains game-model.json. Algorithms are ordinary pinned code,
tables or prose, not evaluated by this checker. Dependency completeness, useful
variety, mathematical validity and actual observations require domain review.
"""
import copy
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

VERSION = '4.0.0'
MATURITIES = ('C0', 'C1', 'T')
TRACKS = (
    ('TR01', 'intent'), ('TR02', 'lore'), ('TR03', 'entity_state'),
    ('TR04', 'actions_physics'), ('TR05', 'equipment_capabilities'),
    ('TR06', 'ai_participants'), ('TR07', 'world_structure'),
    ('TR08', 'situation_composition'), ('TR09', 'playthrough'),
    ('TR10', 'player_development'), ('TR11', 'rewards_economy'),
    ('TR12', 'monetization'), ('TR13', 'input_camera'), ('TR14', 'ux_learning'),
    ('TR15', 'visual'), ('TR16', 'audio_haptics'), ('TR17', 'runtime_persistence'),
    ('TR18', 'content_production'), ('TR19', 'verification_measurement'),
    ('TR20', 'release_evolution'))
TRACK_IDS = {x[0] for x in TRACKS}
CORE_TRACKS = {'TR01', 'TR03', 'TR04', 'TR09', 'TR13', 'TR14', 'TR15',
               'TR16', 'TR17', 'TR18', 'TR19', 'TR20'}
KINDS = ('behavior', 'state_machine', 'numeric', 'rng', 'family', 'generator',
         'ai', 'persistence', 'damage', 'physics', 'input', 'presentation',
         'economy', 'commerce', 'journey', 'asset', 'release', 'measurement')
FLAGS = ('damage', 'physics', 'ai', 'cloud', 'procedural', 'purchases')


def text():
    return {'type': 'string', 'minLength': 1}


def strings(minimum=0):
    return {'type': 'array', 'items': text(), 'minItems': minimum}


def object_schema(required, properties=None, extra=True):
    return {'type': 'object', 'required': list(required),
            'properties': properties or {k: text() for k in required},
            'additionalProperties': extra}


def rows(required, properties=None, minimum=0):
    return {'type': 'array', 'items': object_schema(required, properties), 'minItems': minimum}


def ref_schema():
    return object_schema(('path', 'sha256'), {
        'path': text(), 'sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}})


def schema():
    typed_value = object_schema(('name', 'type', 'units', 'encoding', 'capture'), {
        'name': text(), 'type': {'type': 'string', 'enum': ['integer', 'number', 'boolean', 'string', 'enum', 'vector', 'object', 'array']},
        'units': text(), 'encoding': text(), 'capture': text(),
        'minimum': {'type': 'number'}, 'maximum': {'type': 'number'},
        'initial': {}, 'rounding': text(), 'precision': text()})
    track_required = ('id', 'name', 'enabled', 'rationale', 'owner', 'receiver',
                      'requirement_ids', 'summary', 'reads', 'writes', 'contract_ids',
                      'invariants', 'scenario_ids', 'progression', 'content',
                      'feedback', 'persistence', 'budget', 'concept_refs', 'spec_refs')
    track_props = {k: text() for k in track_required}
    for key in ('requirement_ids', 'reads', 'writes', 'contract_ids', 'invariants', 'scenario_ids'):
        track_props[key] = strings()
    track_props['enabled'] = {'type': 'boolean'}
    track_props['concept_refs'] = {'type': 'array', 'items': ref_schema()}
    track_props['spec_refs'] = {'type': 'array', 'items': ref_schema()}
    contract_required = ('id', 'kind', 'version', 'track_id', 'owner', 'requirement_ids',
                         'purpose', 'status', 'inputs', 'outputs', 'read_refs',
                         'write_refs', 'depends_on', 'algorithm', 'invariants',
                         'cases', 'feedback', 'persistence', 'telemetry', 'body')
    contract_props = {k: text() for k in contract_required}
    contract_props['kind'] = {'type': 'string', 'enum': list(KINDS)}
    contract_props['status'] = {'type': 'string', 'enum': ['unresolved', 'defined', 'tuning']}
    for key in ('requirement_ids', 'read_refs', 'write_refs', 'depends_on', 'invariants'):
        contract_props[key] = strings()
    for key in ('inputs', 'outputs'):
        contract_props[key] = {'type': 'array', 'items': typed_value}
    contract_props['cases'] = rows(('id', 'scenario_id', 'kind', 'initial', 'action', 'expected'), {
        'id': text(), 'scenario_id': text(),
        'kind': {'type': 'string', 'enum': ['positive', 'negative', 'boundary']},
        'initial': {'type': 'object'}, 'action': {'type': 'object'}, 'expected': {'type': 'object'}}, 1)
    contract_props['body'] = {'type': 'object'}
    contract_props['algorithm_ref'] = ref_schema()
    contract_props['tuning'] = object_schema(('initial', 'minimum', 'maximum', 'goal', 'method'), {
        'initial': {'type': 'number'}, 'minimum': {'type': 'number'},
        'maximum': {'type': 'number'}, 'goal': text(), 'method': text()})
    field_required = ('id', 'owner', 'type', 'units', 'initial', 'classification', 'scope',
                      'authority', 'storage', 'encoding', 'consistency_group',
                      'commit', 'restore', 'merge', 'migration', 'retention', 'status')
    field_props = {k: text() for k in field_required}
    field_props['initial'] = {}
    field_props['status'] = {'type': 'string', 'enum': ['unresolved', 'defined']}
    field_props['type'] = {'type': 'string', 'enum': ['integer', 'number', 'boolean', 'string', 'enum', 'vector', 'object', 'array']}
    field_props['classification'] = {'type': 'string', 'enum': ['durable', 'reconstructible', 'ephemeral', 'cache', 'secret']}
    feature = object_schema(('enabled', 'rationale'), {'enabled': {'type': 'boolean'}, 'rationale': text()})
    return object_schema(('maturity', 'tracks', 'applicability', 'contracts', 'state_fields',
                          'dependencies', 'operations', 'unresolved'), {
        'maturity': {'type': 'string', 'enum': list(MATURITIES)},
        'tracks': {'type': 'array', 'items': object_schema(track_required, track_props), 'minItems': 20},
        'applicability': object_schema(FLAGS, {x: feature for x in FLAGS}, False),
        'contracts': {'type': 'array', 'items': object_schema(contract_required, contract_props)},
        'state_fields': {'type': 'array', 'items': object_schema(field_required, field_props)},
        'dependencies': rows(('from', 'to', 'reason')),
        'operations': {'type': 'object'},
        'unresolved': rows(('id', 'description', 'owner', 'due', 'blocks'), {
            'id': text(), 'description': text(), 'owner': text(),
            'due': {'type': 'string', 'enum': list(MATURITIES)}, 'blocks': strings(1)}),
        })


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def load_production_checker():
    # File-path import works both from the CLI and importlib-loaded game_model.
    import importlib.util
    path = Path(__file__).with_name('production_contract.py')
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location('game_atelier_production_contract', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_refs(model):
    """Map actual IDs in canonical model, excluding proof metadata."""
    found = defaultdict(list)
    def walk(value, location):
        if isinstance(value, dict):
            if isinstance(value.get('id'), str):
                found[value['id']].append(location)
            for key, child in value.items():
                if key not in {'evidence', 'migration', 'cases', 'body', 'operations'}:
                    walk(child, location + '.' + key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, '{}[{}]'.format(location, i))
    walk(model, 'model')
    for key in ('capabilities', 'recipes', 'transformations', 'attempts', 'assemblies', 'obligations'):
        for record in model.get('production', {}).get('operations', {}).get(key, []):
            if isinstance(record, dict) and isinstance(record.get('id'), str):
                found[record['id']].append('production.operations.' + key)
    for name, flag in model.get('features', {}).items():
        if flag.get('enabled'):
            found[name].append('domain')
    return found


def _required(body, keys, location, out):
    for key in keys:
        value = body.get(key)
        if value is None or value == '' or value == [] or value == {}:
            out.append(location + '.' + key + ' requires a concrete value')


def _list_dicts(body, key, keys, location, out):
    values = body.get(key)
    if not isinstance(values, list) or not values:
        out.append(location + '.' + key + ' requires nonempty records')
        return []
    for i, value in enumerate(values):
        at = '{}.{}[{}]'.format(location, key, i)
        if not isinstance(value, dict):
            out.append(at + ' must be an object')
        else:
            _required(value, keys, at, out)
    return [v for v in values if isinstance(v, dict)]


def errors(model, maturity=None, root=None, stage=None):
    """Check declared contracts/links, not semantics or undocumented game state.

    Base schema validation is performed by game_model before this function.
    This public function also defends its own extension shape for direct use.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location('_v4_base_model', Path(__file__).with_name('game_model.py'))
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    p = model.get('production', {})
    out = []
    if 'migration' in p:
        out.append('production.migration is not part of the current model; author the current production contract')
    base.check_type(p, schema(), 'production', out)
    if out:
        return out
    requested_maturity = maturity
    if stage is not None and stage not in {'concept', 'preproduction', 'slice', 'beta', 'release'}:
        return ['unsupported production stage']
    if stage is not None and stage != 'concept':
        if requested_maturity not in {None, 'T'}:
            out.append('preproduction and later gates require maturity T; direct caller cannot lower it')
        maturity = 'T'
    else:
        maturity = maturity or p['maturity']
    if maturity not in MATURITIES:
        return ['unsupported maturity']
    level = MATURITIES.index(maturity)
    track_ids = [x['id'] for x in p['tracks']]
    if set(track_ids) != TRACK_IDS or len(track_ids) != 20:
        out.append('production.tracks must contain each TR01..TR20 exactly once')
    tracks = {x['id']: x for x in p['tracks']}
    for ident, name in TRACKS:
        if ident in tracks and tracks[ident]['name'] != name:
            out.append(ident + ': track name must remain ' + name)
    active = {x['id'] for x in p['tracks'] if x['enabled']}
    for ident in sorted(CORE_TRACKS - active):
        out.append('core production track cannot be disabled: ' + ident)
    requirement_ids = set(model.get('source_requirement_ids', []))
    scenarios = {s['id'] for s in model.get('scenarios', [])}
    index = local_refs(model)
    for ident, locations in index.items():
        if len(locations) != 1:
            out.append('duplicate canonical ID: ' + ident)
    contracts = {x['id']: x for x in p['contracts']}
    for track in p['tracks']:
        at = track['id']
        if not set(track['requirement_ids']) <= requirement_ids:
            out.append(at + ': unknown source requirement IDs')
        if track['enabled'] and level >= 1:
            for key in ('requirement_ids', 'contract_ids', 'invariants', 'scenario_ids', 'concept_refs'):
                if not track[key]:
                    out.append(at + ': C1 requires ' + key)
            if level >= 2 and not track['spec_refs']:
                out.append(at + ': T requires pinned spec_refs')
        if not track['enabled'] and track['contract_ids']:
            out.append(at + ': inactive track cannot own active contracts')
        for ident in track['contract_ids']:
            if ident not in contracts or contracts[ident]['track_id'] != at:
                out.append(at + ': contract ownership/reference mismatch: ' + ident)
        if not set(track['scenario_ids']) <= scenarios:
            out.append(at + ': unknown scenario IDs')
        for key in ('reads', 'writes'):
            for ref in track[key]:
                if ref not in index:
                    out.append(at + ': unknown ' + key + ' reference: ' + ref)
        for key in ('concept_refs', 'spec_refs'):
            if root is not None and (key == 'concept_refs' and level >= 1 or key == 'spec_refs' and level >= 2):
                for ref in track[key]:
                    try:
                        if base.sha(base.safe_file(Path(root), ref['path'])) != ref['sha256']:
                            out.append(at + ': pinned ' + key + ' hash mismatch')
                    except (ValueError, OSError) as exc:
                        out.append(at + ': ' + str(exc))
    for edge in p['dependencies']:
        if edge['from'] not in index or edge['to'] not in index:
            out.append('production dependency references missing canonical ID')
    for unresolved in p['unresolved']:
        if not set(unresolved['blocks']) <= set(index):
            out.append('unresolved issue blocks unknown IDs: ' + unresolved['id'])
        if MATURITIES.index(unresolved['due']) <= level:
            out.append('unresolved obligation due by ' + maturity + ': ' + unresolved['id'])
    referenced = {r for t in p['tracks'] for r in t['contract_ids']}
    for contract in p['contracts']:
        at = contract['id']
        if contract['track_id'] not in active or at not in referenced:
            out.append(at + ': contract must belong to one active track')
        if not set(contract['requirement_ids']) <= requirement_ids:
            out.append(at + ': unknown source requirement IDs')
        for key in ('read_refs', 'write_refs', 'depends_on'):
            for ref in contract[key]:
                if ref not in index:
                    out.append(at + ': unknown ' + key + ' reference: ' + ref)
        if contract['id'] in contract['depends_on']:
            out.append(at + ': direct self dependency')
        if level >= 1 and contract['status'] == 'unresolved':
            out.append(at + ': unresolved behavior cannot close C1')
        if level >= 1:
            kinds = {c['kind'] for c in contract['cases']}
            if not {'positive', 'negative'} <= kinds:
                out.append(at + ': positive and negative cases required for C1')
            if not contract['invariants']:
                out.append(at + ': invariants required')
        case_ids = [case['id'] for case in contract['cases']]
        if len(case_ids) != len(set(case_ids)):
            out.append(at + ': duplicate case ID')
        for case in contract['cases']:
            if case['scenario_id'] not in scenarios:
                out.append(at + ': case references unknown scenario')
            if contract['track_id'] in tracks and case['scenario_id'] not in tracks[contract['track_id']]['scenario_ids']:
                out.append(at + ': case scenario not declared by owning track')
            if not case['expected']:
                out.append(at + ': expected case outcome must be explicit')
        for value in contract['inputs'] + contract['outputs']:
            if value.get('minimum', 0) > value.get('maximum', float('inf')):
                out.append(at + ': typed value minimum exceeds maximum')
            if value['type'] in {'integer', 'number'} and level >= 2:
                _required(value, ('rounding', 'precision'), at + '.' + value['name'], out)
        if contract['status'] == 'tuning':
            tuning = contract.get('tuning', {})
            _required(tuning, ('goal', 'method'), at + '.tuning', out)
            if not all(type(tuning.get(k)) in (int, float) for k in ('initial', 'minimum', 'maximum')) or not tuning.get('minimum', 1) <= tuning.get('initial', 0) <= tuning.get('maximum', -1):
                out.append(at + ': tuning requires bounded initial/minimum/maximum')
        if root is not None and contract.get('algorithm_ref'):
            try:
                ref = contract['algorithm_ref']
                if base.sha(base.safe_file(Path(root), ref['path'])) != ref['sha256']:
                    out.append(at + ': algorithm_ref hash mismatch')
            except (ValueError, OSError) as exc:
                out.append(at + ': ' + str(exc))
        if level >= 2:
            detailed_contract_errors(contract, p, out)
    fields = {f['id']: f for f in p['state_fields']}
    if level >= 2 and not fields:
        out.append('T requires state catalogue (including explicit ephemeral/reconstructible classification)')
    for field in p['state_fields']:
        if level >= 2 and field['status'] != 'defined':
            out.append(field['id'] + ': unresolved state field blocks T')
        if field['classification'] == 'durable' and field['storage'].casefold() in {'none', 'runtime', 'cache', 'tmp'}:
            out.append(field['id'] + ': durable state needs durable storage')
        if field['classification'] == 'ephemeral' and field['restore'].casefold() in {'serialize pointer', 'restore pointer'}:
            out.append(field['id'] + ': ephemeral runtime pointers cannot be restored')
    if p['applicability']['ai']['enabled'] != model.get('features', {}).get('actors', {}).get('enabled', False):
        out.append('AI applicability must agree with actors feature')
    if p['applicability']['ai']['enabled'] and 'TR06' not in active:
        out.append('AI requires active TR06')
    if level >= 1:
        kinds = {c['kind'] for c in p['contracts']}
        for feature, kind in (('ai', 'ai'), ('damage', 'damage'), ('physics', 'physics'),
                              ('procedural', 'generator'), ('cloud', 'persistence'), ('purchases', 'commerce')):
            if p['applicability'][feature]['enabled'] and kind not in kinds:
                out.append(feature + ' requires ' + kind + ' contract')
    if level >= 2 and 'persistence' not in {c['kind'] for c in p['contracts']}:
        out.append('T always requires local persistence contract')
    operations = p['operations']
    if stage in {'slice', 'beta', 'release'}:
        assemblies = operations.get('assemblies', [])
        if not isinstance(assemblies, list) or not any(isinstance(a, dict) and a.get('proof_level') == 'native_verified' for a in assemblies):
            out.append(stage + ' requires representative native_verified assembly evidence; candidate records are not an integrated slice')
    def inspect_requirement_refs(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == 'requirement_id' and isinstance(child, str) and child not in requirement_ids:
                    out.append('operation references unknown source requirement: ' + child)
                if key == 'requirement_ids' and isinstance(child, list) and any(x not in requirement_ids for x in child if isinstance(x, str)):
                    out.append('operation references unknown source requirement IDs')
                inspect_requirement_refs(child)
        elif isinstance(value, list):
            for child in value:
                inspect_requirement_refs(child)
    inspect_requirement_refs(operations)
    if level >= 2 and not operations.get('obligations'):
        out.append('T requires nonempty due production operation obligations; coverage is reviewed by the receiver')
    if operations or level >= 2:
        checker = load_production_checker()
        if checker is None:
            out.append('production_contract.py unavailable; cannot validate operation contracts')
        else:
            staged = copy.deepcopy(operations)
            staged['gate'] = {'preproduction': 'T', 'slice': 'A', 'beta': 'B', 'release': 'R'}.get(stage, maturity)
            out.extend('operations: ' + e for e in checker.validate(staged, root=root, context=model))
    return sorted(set(out))


def detailed_contract_errors(c, p, out):
    at, body, kind = c['id'], c['body'], c['kind']
    common = ('update_order', 'time_domain', 'exceptions', 'save_resume')
    _required(body, common, at, out)
    if kind == 'state_machine':
        states = _list_dicts(body, 'states', ('id', 'entry', 'exit'), at, out)
        state_ids = {s.get('id') for s in states}
        transitions = _list_dicts(body, 'transitions', ('from', 'to', 'guard', 'priority', 'effects'), at, out)
        for t in transitions:
            if t.get('from') not in state_ids or t.get('to') not in state_ids:
                out.append(at + ': transition references unknown state')
        _required(body, ('initial_state', 'tie_break', 'unhandled_event'), at, out)
        if body.get('initial_state') not in state_ids:
            out.append(at + ': initial_state not in states')
    elif kind == 'numeric':
        _required(body, ('formula_or_table', 'domain', 'units', 'rounding', 'clamp', 'overflow', 'division_by_zero', 'tolerance'), at, out)
        if not any(case['kind'] == 'boundary' for case in c['cases']):
            out.append(at + ': numeric contract requires boundary case')
    elif kind == 'rng':
        _required(body, ('algorithm', 'version', 'independence_policy', 'resume', 'encoding'), at, out)
        streams = _list_dicts(body, 'streams', ('id', 'purpose', 'state_field_ref', 'draw_policy', 'distribution', 'bounds', 'correlation'), at, out)
        fields = {f['id'] for f in p['state_fields']}
        for stream in streams:
            if stream.get('state_field_ref') not in fields:
                out.append(at + ': RNG state_field_ref not in catalogue')
    elif kind == 'family':
        _required(body, ('dimensions', 'compatibility', 'progression', 'opportunities', 'dominance_counterexample', 'launch_catalog_ref'), at, out)
    elif kind == 'generator':
        _required(body, ('inputs', 'constraints', 'validators', 'repair', 'attempt_limit', 'fallback', 'rng_stream_ref', 'novelty_signature', 'progression_envelope'), at, out)
        if type(body.get('attempt_limit')) is not int or body['attempt_limit'] < 1:
            out.append(at + ': generator attempt_limit must be positive integer')
    elif kind == 'ai':
        _required(body, ('actor_families', 'perception', 'knowledge', 'decision_model', 'actions', 'navigation', 'encounter_budget', 'fallback', 'trace', 'counterplay', 'boss_policy'), at, out)
        _list_dicts(body, 'knowledge', ('fact', 'source', 'confidence', 'expires', 'sharing'), at, out)
        _list_dicts(body, 'actions', ('id', 'guards', 'cost', 'startup', 'active', 'recovery', 'cancel', 'telegraph', 'counterplay'), at, out)
    elif kind == 'persistence':
        groups = _list_dicts(body, 'consistency_groups', ('id', 'member_refs', 'atomicity', 'conflict_policy'), at, out)
        fields = {f['id']: f for f in p['state_fields']}
        group_index = {}
        for group in groups:
            ident = group.get('id')
            members = group.get('member_refs', [])
            if not isinstance(ident, str) or not isinstance(members, list) or any(not isinstance(x, str) for x in members):
                out.append(at + ': malformed consistency group ID/member_refs')
                continue
            if ident in group_index:
                out.append(at + ': duplicate consistency group ID')
            group_index[ident] = group
            for ref in members:
                if ref not in fields or fields[ref]['consistency_group'] != ident:
                    out.append(at + ': consistency group member missing or ownership mismatch: ' + ref)
        for field in fields.values():
            if field['classification'] == 'durable':
                group = group_index.get(field['consistency_group'], {})
                if field['id'] not in group.get('member_refs', []):
                    out.append(at + ': durable state omitted from declared consistency group: ' + field['id'])
        _required(body, ('authority', 'consistency_groups', 'transaction', 'generation_guard', 'disk_full', 'recovery', 'restore_pipeline', 'migration', 'clock_policy', 'identity', 'cloud_policy', 'deletion_policy'), at, out)
        if type(body.get('dirty_window_ms')) not in (int, float) or body.get('dirty_window_ms', -1) < 0:
            out.append(at + ': persistence dirty_window_ms must be nonnegative')
        restore = body.get('restore_pipeline', [])
        required = ['envelope', 'owner', 'compatibility', 'migration', 'semantic_validation', 'apply', 'rebuild', 'safe_input']
        if not isinstance(restore, list) or any(x not in restore for x in required):
            out.append(at + ': restore_pipeline missing required stages')
        elif [restore.index(x) for x in required] != sorted(restore.index(x) for x in required):
            out.append(at + ': restore_pipeline stages have unsafe order')
        if p['applicability']['cloud']['enabled']:
            _required(body.get('cloud_policy', {}) if isinstance(body.get('cloud_policy'), dict) else {}, ('opt_in', 'owner_binding', 'conflict', 'ack_states', 'quota', 'late_callback'), at + '.cloud_policy', out)
    elif kind == 'damage':
        expected = ['intent', 'contact', 'eligibility', 'channels', 'modifiers', 'resources', 'reactions', 'outcome', 'commit']
        pipeline = body.get('pipeline')
        if not isinstance(pipeline, list) or any(not isinstance(x, str) for x in pipeline) or set(pipeline) != set(expected) or len(pipeline) != len(expected):
            out.append(at + ': damage pipeline must name all nine distinct steps; order is game-defined')
        _required(body, ('contact_provenance', 'instance_generation_guard', 'repeat_gate', 'channels', 'capture', 'modifier_order', 'rounding', 'resource_routing', 'reaction_predicates', 'lifecycle_priority', 'cascade_limit', 'simulation_commit', 'durable_commit', 'credit', 'dot_policy'), at, out)
        if type(body.get('cascade_limit')) is not int or body['cascade_limit'] < 1:
            out.append(at + ': damage cascade_limit must be positive integer')
        contracts = {x['id']: x for x in p['contracts']}
        channels = _list_dicts(body, 'channels', ('id', 'units', 'numeric_contract_ref'), at, out)
        for channel in channels:
            ref = channel.get('numeric_contract_ref')
            if not isinstance(ref, str) or contracts.get(ref, {}).get('kind') != 'numeric':
                out.append(at + ': damage channel must reference numeric contract')
        _list_dicts(body, 'capture', ('input', 'moment', 'mode'), at, out)
        if body.get('simulation_commit') == body.get('durable_commit'):
            out.append(at + ': simulation and durable commit boundaries must be distinguished')
    elif kind == 'physics':
        if type(body.get('fixed_timestep')) not in (int, float) or body.get('fixed_timestep', -1) <= 0:
            out.append(at + ': physics fixed_timestep must be positive seconds')
        if type(body.get('substeps')) is not int or body.get('substeps', 0) < 1:
            out.append(at + ': physics substeps must be positive integer')
        _required(body, ('engine_version', 'solver_config', 'units_axes', 'fixed_timestep', 'substeps', 'collision_layers', 'queries', 'contact_adapter', 'transform_ownership', 'tolerance', 'determinism_scope', 'crash_policy', 'destruction_topology'), at, out)
    elif kind == 'input':
        _required(body, ('intents', 'bindings', 'recognizer', 'pointer_ownership', 'cancel', 'simultaneity', 'camera_arbitration', 'peak_case', 'accessibility'), at, out)
    elif kind == 'commerce':
        _required(body, ('offers', 'earned_path', 'paid_path', 'portfolio_effect', 'partial_ownership', 'grant_idempotency', 'cancel', 'refund', 'reconcile', 'authority'), at, out)
    elif kind == 'asset':
        _required(body, ('state_inventory', 'editable_sources', 'exports', 'import_settings', 'semantic_invariants', 'rights', 'runtime_scene', 'budgets'), at, out)
    elif kind == 'economy':
        _required(body, ('sources', 'sinks', 'caps', 'rounding', 'grant_identity', 'duplicates', 'overflow', 'completion', 'cohort_assumptions'), at, out)
    else:
        _required(body, ('states', 'failure', 'recovery', 'acceptance'), at, out)


def maturity_for_stage(model, stage, override=None):
    # A caller flag cannot lower the normative production contract maturity.
    if stage != 'concept':
        return 'T'
    return override or model.get('production', {}).get('maturity', 'C1')


def requirements(model, stage, maturity=None):
    maturity = maturity_for_stage(model, stage, maturity)
    if maturity == 'C0':
        return []
    result = []
    for track in model['production']['tracks']:
        if not track['enabled']:
            continue
        suffix = 'concept' if maturity == 'C1' else 'contract'
        result.append({'id': 'v4.' + track['id'] + '.' + suffix, 'domain': 'product',
                       'due_stage': 'concept' if suffix == 'concept' else 'preproduction',
                       'modality': 'document', 'origin': 'design_review' if suffix == 'concept' else 'contract_review',
                       'independent': True, 'motion_required': False,
                       'required_scenario_ids': track['scenario_ids']})
    return result


def referenced_ids(value):
    """Declared semantic references, including ordinary production bindings."""
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith(('_ref', '_id')) and isinstance(child, str):
                found.add(child)
            elif key.endswith(('_refs', '_ids')) and isinstance(child, list):
                found.update(x for x in child if isinstance(x, str))
            found.update(referenced_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(referenced_ids(child))
    return found


def dependency_index(model):
    """One declared graph for scope reuse and impact; cyclic gameplay is allowed."""
    p = model['production']
    payloads = {t['id']: t for t in p['tracks']}
    payloads.update({c['id']: c for c in p['contracts']})
    payloads.update({f['id']: f for f in p['state_fields']})
    for kind in ('capabilities', 'recipes', 'transformations', 'attempts', 'assemblies', 'obligations'):
        for record in p['operations'].get(kind, []):
            if isinstance(record, dict) and isinstance(record.get('id'), str):
                payloads[record['id']] = record
    upstream = defaultdict(set)
    for track in p['tracks']:
        upstream[track['id']].update(track['contract_ids'] + track['reads'])
        for target in track['writes']:
            upstream[target].add(track['id'])
    for contract in p['contracts']:
        upstream[contract['id']].update(contract['depends_on'] + contract['read_refs'])
        for target in contract['write_refs']:
            upstream[target].add(contract['id'])
    def walk(value, domain):
        if isinstance(value, dict):
            if isinstance(value.get('id'), str):
                payloads.setdefault(value['id'], value)
                upstream[domain].add(value['id'])
            for child in value.values():
                walk(child, domain)
        elif isinstance(value, list):
            for child in value:
                walk(child, domain)
    for domain, payload in model.get('domains', {}).items():
        payloads[domain] = payload
        walk(payload, domain)
    for edge in p['dependencies'] + model.get('dependencies', []):
        upstream[edge['to']].add(edge['from'])
    for edge in model.get('domains', {}).get('systems', {}).get('links', []):
        upstream[edge['to']].add(edge['from'])
    for node in model.get('domains', {}).get('progression', {}).get('nodes', []):
        upstream[node['id']].update(node['prerequisites'])
    all_ids = set(payloads)
    for ident, payload in payloads.items():
        upstream[ident].update(referenced_ids(payload) & all_ids - {ident})
    return payloads, upstream


def scope_digest(model, check_id):
    """Hash declared upstream closure; never infer undocumented dependencies."""
    p = model['production']
    track_id = check_id.split('.')[1]
    payloads, upstream = dependency_index(model)
    wanted, queue = {track_id}, deque([track_id])
    while queue:
        for parent in upstream[queue.popleft()]:
            if parent not in wanted:
                wanted.add(parent)
                queue.append(parent)
    relevant_scenarios = {s for key in wanted if key in payloads and isinstance(payloads[key], dict) for s in payloads[key].get('scenario_ids', [])}
    return stable_hash({'check_id': check_id, 'model_id': model['id'], 'schema_version': model['schema_version'],
                        'constraints': model['constraints'], 'source_requirement_ids': model['source_requirement_ids'], 'author_ids': model['author_ids'],
                        'applicability': p['applicability'], 'payloads': {k: payloads[k] for k in sorted(wanted) if k in payloads},
                        'unresolved': [u for u in p['unresolved'] if set(u['blocks']) & wanted],
                        'edges': {key: sorted(upstream[key]) for key in sorted(wanted)},
                        'scenarios': [s for s in model.get('scenarios', []) if s['id'] in relevant_scenarios]})


def impact(model, changed):
    payloads, upstream = dependency_index(model)
    graph = defaultdict(set)
    for child, parents in upstream.items():
        for parent in parents:
            graph[parent].add(child)
    seen, queue = {changed}, deque([changed])
    while queue:
        for child in graph[queue.popleft()]:
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return {'affected_ids': sorted(seen), 'production_tracks': sorted(TRACK_IDS & seen),
            'requires_semantic_triage': True, 'quality_certified': False}



def new_production(features=None):
    """Create a new current authoring scaffold; no prior results are imported."""
    features = features or {}
    flags = {x: {'enabled': False, 'rationale': 'Determine applicability from the current project brief.'} for x in FLAGS}
    flags['ai'] = {'enabled': bool(features.get('actors', {}).get('enabled', False)),
                   'rationale': 'Current actors applicability; author the detailed AI contract if enabled.'}
    tracks = []
    for ident, name in TRACKS:
        tracks.append({'id': ident, 'name': name, 'enabled': ident in CORE_TRACKS,
                       'rationale': 'Current authoring scaffold; determine applicability from project requirements.',
                       'owner': 'unassigned', 'receiver': 'unassigned',
                       'requirement_ids': [], 'summary': 'Unresolved current sketch; not an accepted concept.',
                       'reads': [], 'writes': [], 'contract_ids': [], 'invariants': [], 'scenario_ids': [],
                       'progression': 'Unresolved', 'content': 'Unresolved', 'feedback': 'Unresolved',
                       'persistence': 'Unresolved', 'budget': 'Unresolved', 'concept_refs': [], 'spec_refs': []})
    if flags['ai']['enabled']:
        next(t for t in tracks if t['id'] == 'TR06')['enabled'] = True
    return {'maturity': 'C0', 'tracks': tracks, 'applicability': flags,
            'contracts': [], 'state_fields': [], 'dependencies': [], 'operations': {},
            'unresolved': [{'id': 'AUTHOR-CURRENT-CONTRACTS',
                            'description': 'Define current applicability and contracts before completing the concept.',
                            'owner': 'project-integrator', 'due': 'C1',
                            'blocks': [x['id'] for x in tracks if x['enabled']]}]}
