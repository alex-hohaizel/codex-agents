#!/usr/bin/env python3
"""Compile/verify a declared task context; no jobs, permissions or quality certification."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MAX_JSON = 4 * 1024 * 1024
MAX_INPUT = 64 * 1024 * 1024
SCHEMA = 'atelier.context-projection/1'
CAPSULE = 'atelier.context-capsule/1'
BINDINGS = 'atelier.context-bindings/1'
COVERAGE = 'atelier.context-coverage/1'
DEFAULT_BINDINGS = '.atelier/context-bindings.json'
MAX_BOUND_SOURCE = 2 * 1024 * 1024
MAX_IDS = 2000
HASH = re.compile(r'^[a-f0-9]{64}$')
PRIVATE_NAME = re.compile(
    r'^(?:\.env(?:\..*)?|credentials(?:\..*)?|owner-credentials\.json|'
    r'id_(?:rsa|ed25519)|.*\.(?:pem|key|p12|pfx)|auth\.json)$', re.I)
PRIVATE_PARTS = {'.git', '.aws', '.ssh', '.config', 'node_modules'}


class ContextError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContextError(message)


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def constant(value):
    raise ContextError('nonfinite JSON number: ' + value)


def finite_float(value):
    result = float(value)
    require(math.isfinite(result), 'nonfinite JSON number: ' + value)
    return result


def json_object(raw):
    try:
        result = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                            parse_constant=constant, parse_float=finite_float)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ContextError('invalid or overly nested UTF-8 JSON') from error
    require(isinstance(result, dict), 'JSON input must be an object')
    return result


def _linked(path):
    # This validator is exported under historical self-contained operating
    # contracts. Keep this tiny native-path check dependency-free so previously
    # acquired agent packages do not gain a missing sibling dependency.
    try: info = Path(path).lstat()
    except FileNotFoundError: return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def load(path):
    require(path.is_file() and not _linked(path), 'missing/linked JSON input')
    require(path.stat().st_size <= MAX_JSON, 'JSON input exceeds 4 MiB')
    return json_object(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def text(row, key):
    value = row.get(key)
    require(isinstance(value, str) and value.strip(), 'missing text: ' + key)
    return value


def local(root, value, existing=True):
    require(isinstance(value, str) and value and '\0' not in value,
            'missing/invalid relative path')
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in value
            and pure.as_posix() == value, 'unsafe relative path: ' + value)
    if sys.platform == 'win32':
        reserved = re.compile(r'^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)', re.I)
        require(all(not any(c in part for c in ':<>"|?*') and not part.endswith((' ', '.'))
                    and not reserved.match(part) and not any(ord(c) < 32 for c in part)
                    for part in pure.parts), 'unsafe Windows relative path: ' + value)
    path = root
    for part in pure.parts:
        path = path / part
        require(not _linked(path), 'linked input/output path rejected')
    if existing:
        require(path.is_file(), 'missing local input: ' + value)
    return path


def records(data, key):
    rows = data.get(key, [])
    require(isinstance(rows, list) and all(isinstance(x, dict) for x in rows),
            key + ' must be an array of objects')
    result = {}
    for row in rows:
        ident = text(row, 'id')
        require(ident not in result, 'duplicate ' + key + ' ID: ' + ident)
        result[ident] = row
    return result


def string_list(value, label):
    require(isinstance(value, list) and all(isinstance(x, str) and x for x in value),
            label + ' must be an array of nonempty strings')
    require(len(value) == len(set(value)), 'duplicate in ' + label)
    return value


def bounded_ids(value, label):
    result = string_list(value, label)
    require(len(result) <= MAX_IDS and all(len(x) <= 240 for x in result),
            label + ' exceeds bounded requirement IDs')
    return result


def bound_bytes(root, ref):
    require(isinstance(ref, str) and len(ref) <= 4096, 'invalid bound source path')
    path = local(root, ref)
    require(not any(PRIVATE_NAME.fullmatch(part) or part in PRIVATE_PARTS
                    for part in PurePosixPath(ref).parts), 'private context source rejected')
    with path.open('rb') as stream:
        raw = stream.read(MAX_BOUND_SOURCE + 1)
    require(len(raw) <= MAX_BOUND_SOURCE, 'bound context source exceeds 2 MiB')
    return raw


def native_rows(document, names):
    value = next((document[x] for x in names if document.get(x) is not None), None)
    if value is None:
        return None
    require(isinstance(value, (dict, list)), 'unsupported native record group')
    if isinstance(value, list):
        rows = [({'text': row} if isinstance(row, str) else row) for row in value]
    else:
        rows = [{'id': key, **row} if isinstance(row, dict) else {'id': key, 'value': row}
                for key, row in value.items()]
    require(len(rows) <= MAX_IDS and all(isinstance(row, dict) for row in rows),
            'native records require bounded objects and stable IDs')
    return rows


def native_text(row, keys, default):
    value = next((row[x] for x in keys if row.get(x) is not None), default)
    return value if isinstance(value, str) else canonical(value).decode('utf-8')


def normalize_requirement(row, source):
    ident = row.get('id', row.get('requirement_id', row.get('key')))
    require(isinstance(ident, str) and 0 < len(ident) <= 240,
            'native requirement needs a stable string ID')
    priority = str(row.get('priority', row.get('severity', 'must'))).lower()
    priority = priority if priority in ('must', 'should', 'could') else 'must'
    verbatim = native_text(row, ('verbatim', 'source_text', 'source_text_uk', 'text',
                                 'description', 'requirement'), canonical(row).decode('utf-8'))
    return {
        'id': ident, 'source_ref': source['path'], 'source_sha256': source['sha256'],
        'verbatim': verbatim,
        'interpretation': native_text(row, ('interpretation', 'requirement_en', 'text',
                                            'description', 'requirement'), verbatim),
        'priority': priority, 'applicable': row.get('applicable') is not False,
        **({'applicability_reason': row['applicability_reason']}
           if 'applicability_reason' in row else {}),
        'always_review': row.get('always_review') is True,
        'dependencies': bounded_ids(row.get('dependencies', row.get('depends_on', [])),
                                    'native dependencies'),
        'acceptance': native_text(row, ('acceptance', 'acceptance_criteria'),
                                  'Native acceptance retained in raw record; not owner acceptance'),
        'owner': native_text(row, ('owner',), 'native-project-owner'),
        'due_gate': native_text(row, ('due_gate', 'phase'), 'native-unspecified'),
        'raw_native_record': row,
    }


def reconcile_decisions(decisions):
    indexed, edges, superseded, corrections, issues = {}, {}, set(), [], []
    for row in decisions:
        if isinstance(row, dict) and isinstance(row.get('id'), str):
            indexed.setdefault(row['id'], []).append(row)
    if any(len(rows) != 1 for rows in indexed.values()):
        issues.append({'code': 'CONTEXT_CONFLICT', 'message': 'duplicate native decision ID',
                       'blocking': True})
    for row in decisions:
        if not isinstance(row, dict) or 'supersedes' not in row:
            continue
        try:
            ident = text(row, 'id')
            prior = bounded_ids(row['supersedes'], 'decision supersedes')
            require(len(indexed.get(ident, [])) == 1 and
                    all(len(indexed.get(x, [])) == 1 for x in prior),
                    'decision correction refers to missing/ambiguous ID')
            edges[ident] = prior
            superseded.update(prior)
            corrections.append({key: row[key] for key in
                                ('id', 'supersedes', 'source_ref', 'source_sha256') if key in row})
        except ContextError as error:
            issues.append({'code': 'CONTEXT_CONFLICT', 'message': str(error), 'blocking': True})
    visiting, visited = set(), set()

    def visit(ident):
        require(ident not in visiting, 'native decision corrections form a cycle')
        if ident in visited:
            return
        visiting.add(ident)
        for prior in edges.get(ident, []):
            visit(prior)
        visiting.remove(ident)
        visited.add(ident)

    try:
        for ident in edges:
            visit(ident)
    except ContextError as error:
        issues.append({'code': 'CONTEXT_CONFLICT', 'message': str(error), 'blocking': True})
    return {'current_decisions': decisions if issues else [row for row in decisions
            if not isinstance(row, dict) or row.get('id') not in superseded],
            'corrections': corrections, 'issues': issues}


def declared_context(data, root, projection_path, bindings_path=None):
    """Read only one explicit/conventional binding; never scan or create native state."""
    conventional = root / DEFAULT_BINDINGS
    refs = [DEFAULT_BINDINGS] if conventional.exists() or _linked(conventional) else []
    if bindings_path is not None and bindings_path not in refs:
        refs.append(bindings_path)
    if not refs:
        return None
    require(len(refs) == 1, 'CONTEXT_CONFLICT: multiple context binding manifests')
    ref = refs[0]
    require(root.is_absolute() and root.resolve() == root and
            not any(_linked(x) for x in (root, *root.parents)),
            'SCOPE_MISMATCH: canonical unlinked root required')
    raw = bound_bytes(root, ref)
    manifest = json_object(raw)
    require(manifest.get('schema') == BINDINGS, 'unsupported context bindings schema')
    require(manifest.get('project_root') == str(root),
            'SCOPE_MISMATCH: context binding belongs to another project')
    expected = bounded_ids(manifest.get('expected_requirement_ids', []), 'expected_requirement_ids')
    must = bounded_ids(manifest.get('expected_must_ids', []), 'expected_must_ids')
    sources = manifest.get('sources')
    require(isinstance(sources, list) and 1 <= len(sources) <= 40,
            'context bindings require 1 to 40 source pins')
    checks, loaded, requirements, decisions, deferred, identities, issues = [], [], [], [], [], [], []
    seen = set()

    def issue(code, message, **details):
        issues.append({'code': code, 'message': message, 'blocking': True, **details})

    for row in sources:
        require(isinstance(row, dict), 'invalid context source record')
        path, role, sha = text(row, 'path'), text(row, 'role'), text(row, 'sha256')
        require(len(path) <= 4096 and len(role) <= 120 and HASH.fullmatch(sha),
                'invalid context source path/role/SHA-256')
        pure = PurePosixPath(path)
        require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in path
                and '\0' not in path and pure.as_posix() == path,
                'unsafe bound source path')
        require('required' not in row or type(row['required']) is bool, 'invalid required flag')
        declared = bounded_ids(row.get('requirement_ids', []), 'source requirement_ids')
        require(path not in seen and path != ref, 'CONTEXT_CONFLICT: duplicated/self-bound source')
        seen.add(path)
        check = {'path': path, 'role': role, 'required': row.get('required') is not False,
                 'expected_sha256': sha, 'requirement_ids': declared}
        checks.append(check)
        try:
            source_raw = bound_bytes(root, path)
            actual = digest(source_raw)
            check.update(observed_sha256=actual,
                         status='verified' if actual == sha else 'changed')
            source = {'path': path, 'sha256': actual, 'bytes': len(source_raw)}
            try:
                source['text'] = source_raw.decode('utf-8')
            except UnicodeError:
                source['text'] = None
            loaded.append(source)
            if actual != sha:
                issue('SOURCE_DRIFT', 'declared context source changed', path=path,
                      blocking=check['required'])
                continue
            document = None
            if path.lower().endswith('.json') or role in ('requirements', 'decisions'):
                try:
                    document = json_object(source_raw)
                except ContextError:
                    if role in ('requirements', 'decisions'):
                        raise
            if document is None:
                continue
            req_rows = native_rows(document, ('requirements', 'requirement_registry', 'requirement'))
            decision_rows = native_rows(document, ('decisions', 'decision'))
            if role in ('requirements', 'decisions'):
                rows = req_rows if role == 'requirements' else decision_rows
                require(rows is not None, 'structured source has no supported native record group')
                check['projection_status'] = 'native-records-read'
            for native in req_rows or []:
                requirements.append(normalize_requirement(native, source))
            for key, target, aliases in [('decisions', decisions, ('decisions', 'decision')),
                                         ('deferred', deferred, ('deferred_work', 'deferred')),
                                         ('identity', identities, ('identity',))]:
                values = document.get(aliases[0], document.get(aliases[-1]))
                if key == 'identity' and isinstance(values, dict):
                    values = [values]
                elif values is not None:
                    values = native_rows(document, aliases)
                for native in values or []:
                    target.append({**native, 'source_ref': path, 'source_sha256': actual})
        except (ContextError, OSError, ValueError) as error:
            if 'status' not in check:
                check['status'] = 'missing' if isinstance(error, FileNotFoundError) else 'unreadable'
            elif check['status'] == 'verified' and role in ('requirements', 'decisions'):
                check['projection_status'] = 'unsupported'
            issue('CONTEXT_INCOMPLETE', str(error), path=path, blocking=check['required'])
    native_index = {}
    for row in requirements:
        if row['id'] in native_index:
            issue('CONTEXT_CONFLICT', 'duplicate native requirement ID', requirement_ids=[row['id']])
        native_index[row['id']] = row
    missing = [x for x in expected if x not in native_index]
    missing_must = [x for x in must if x not in native_index or
                    not native_index[x]['applicable'] or native_index[x]['priority'] != 'must']
    if missing or missing_must:
        issue('CONTEXT_INCOMPLETE', 'native register omits/weakens declared obligations',
              requirement_ids=sorted(set(missing + missing_must)))
    for check in checks:
        absent = [x for x in check['requirement_ids'] if x not in native_index or
                  native_index[x]['source_ref'] != check['path']]
        if absent:
            issue('CONTEXT_INCOMPLETE', 'source requirement IDs absent from native register',
                  path=check['path'], requirement_ids=absent, blocking=check['required'])
    projected = records(data, 'requirements')
    for ident, row in native_index.items():
        if ident not in projected:
            projected[ident] = row
            continue
        explicit = projected[ident]
        require(explicit.get('source_ref') == row['source_ref'],
                'CONTEXT_CONFLICT: projected native requirement has another source: ' + ident)
        require(row['verbatim'] in explicit.get('verbatim', '') and
                not (row['priority'] == 'must' and explicit.get('priority') != 'must') and
                explicit.get('applicable') == row['applicable'] and
                set(row['dependencies']) <= set(explicit.get('dependencies', [])),
                'CONTEXT_CONFLICT: projection weakens native requirement: ' + ident)
        require(explicit.get('source_sha256', row['source_sha256']) == row['source_sha256'],
                'SOURCE_DRIFT: projected requirement provenance changed: ' + ident)
        projected[ident] = {**explicit, 'source_sha256': row['source_sha256'],
                            'raw_native_record': row['raw_native_record']}
    require(len(projected) <= MAX_IDS, 'combined native requirements exceed 2000 IDs')
    links = manifest.get('requirement_links', [])
    require(isinstance(links, list) and len(links) <= MAX_IDS, 'invalid requirement_links')
    link_checks = []
    for link in links:
        require(isinstance(link, dict), 'invalid requirement link')
        ident, path, excerpt = (text(link, x) for x in
                                ('requirement_id', 'source_path', 'source_excerpt'))
        require(len(ident) <= 240 and len(path) <= 4096 and len(excerpt) <= 20000,
                'requirement link exceeds bounds')
        check = next((x for x in checks if x['path'] == path), None)
        source = next((x for x in loaded if x['path'] == path), None)
        row = projected.get(ident)
        status = ('source-not-bound' if check is None else
                  'original-unverified' if check['status'] != 'verified' else
                  'missing-requirement' if row is None else
                  'quote-not-in-source' if excerpt not in (source.get('text') or '') else
                  'quote-not-in-requirement' if excerpt not in row.get('verbatim', '') else
                  'verified-excerpt')
        link_checks.append({**link, **({'source_sha256': source['sha256']} if source else {}),
                            'status': status})
        if status != 'verified-excerpt':
            issue('CONTEXT_INCOMPLETE', 'declared original excerpt not preserved', path=path,
                  requirement_ids=[ident], blocking=check is None or check['required'])
    projection_ref = str(projection_path.relative_to(root))
    projection_sha = digest(projection_path.read_bytes())
    def projected_rows(aliases):
        return [{**row, 'source_ref': projection_ref, 'source_sha256': projection_sha,
                 'raw_native_record': row} for row in native_rows(data, aliases) or []]
    decisions = [*projected_rows(('decisions', 'decision')), *decisions]
    deferred = [*projected_rows(('deferred_work', 'deferred')), *deferred]
    decision_context = reconcile_decisions(decisions)
    issues.extend(decision_context['issues'])
    coverage = {'schema_version': COVERAGE,
                'status': ('conflict' if any(x['code'] in ('CONTEXT_CONFLICT', 'SCOPE_MISMATCH')
                                           for x in issues) else
                           'incomplete' if issues else 'verified-declared-bindings'),
                'manifest_ref': {'path': ref, 'sha256': digest(raw)},
                'source_checks': checks, 'requirement_checks': link_checks,
                'expected_requirement_ids': expected, 'expected_must_ids': must,
                'missing_requirement_ids': missing, 'missing_must_ids': missing_must,
                'issues': issues, 'source_completeness_authenticated': False,
                'notice': 'Declared pins/IDs/excerpts/corrections only; undeclared omissions, '
                          'meaning, human approval and independent completeness are not proved.'}
    return {'coverage': coverage, 'requirements': projected, 'decisions': decisions,
            'current_decisions': decision_context['current_decisions'],
            'corrections': decision_context['corrections'], 'deferred_work': deferred,
            'native_identity': identities, 'loaded': loaded}


def compile_packet(data, task_id, root, projection_path, bindings_path=None, require_complete=False):
    require(data.get('schema_version') == SCHEMA, 'unsupported projection schema')
    project_id, revision = text(data, 'project_id'), text(data, 'native_revision')
    binding = declared_context(data, root, projection_path, bindings_path)
    if binding:
        blocked = next((x for x in binding['coverage']['issues'] if x['blocking']), None)
        require(blocked is None, (blocked['code'] + ': ' + blocked['message']) if blocked else '')
    require(not require_complete or binding is not None and
            binding['coverage']['status'] == 'verified-declared-bindings',
            'CONTEXT_INCOMPLETE: verified declared context bindings required; not independent completeness')
    requirements = binding['requirements'] if binding else records(data, 'requirements')
    tasks, inputs = records(data, 'tasks'), records(data, 'inputs')
    require(task_id in tasks, 'unknown task ID')
    task = tasks[task_id]
    for key in ('objective', 'owner', 'authority_ref', 'gate', 'stop', 'recovery'):
        text(task, key)
    assigned = string_list(task.get('requirement_ids'), 'requirement_ids')
    require(assigned, 'task requires at least one requirement')
    require(isinstance(task.get('budget'), dict) and task['budget'], 'explicit budget required')
    require(isinstance(task.get('outputs'), list) and task['outputs'], 'explicit outputs required')
    for ident, row in requirements.items():
        for key in ('source_ref', 'verbatim', 'interpretation', 'acceptance', 'owner', 'due_gate'):
            text(row, key)
        require(row.get('priority') in ('must', 'should', 'could'), 'invalid priority: ' + ident)
        require(type(row.get('applicable')) is bool, 'explicit applicability required: ' + ident)
        if not row['applicable']:
            text(row, 'applicability_reason')
        for dependency in string_list(row.get('dependencies', []), 'dependencies'):
            require(dependency in requirements, 'unknown requirement dependency: ' + dependency)
    selected = set(assigned)
    for ident in assigned:
        require(ident in requirements, 'assigned requirement missing: ' + ident)
        require(requirements[ident]['applicable'], 'assigned requirement declared inapplicable: ' + ident)
    selected.update(ident for ident, row in requirements.items()
                    if row['applicable'] and (row['priority'] == 'must' or row.get('always_review') is True))
    visiting, visited = set(), set()

    def visit(ident):
        require(ident not in visiting, 'cyclic requirement dependency: ' + ident)
        if ident in visited:
            return
        require(requirements[ident]['applicable'], 'required dependency marked inapplicable: ' + ident)
        visiting.add(ident)
        for dependency in requirements[ident].get('dependencies', []):
            selected.add(dependency)
            visit(dependency)
        visiting.remove(ident)
        visited.add(ident)

    for ident in list(selected):
        visit(ident)
    wanted_inputs = set(string_list(task.get('input_ids', []), 'input_ids'))
    for ident in selected:
        wanted_inputs.update(string_list(requirements[ident].get('input_ids', []), 'input_ids'))
    pins, total = [], 0
    for ident in sorted(wanted_inputs):
        require(ident in inputs, 'referenced input missing: ' + ident)
        row = inputs[ident]
        path = local(root, text(row, 'path'))
        size = path.stat().st_size
        require(size <= MAX_INPUT, 'input exceeds bounded read: ' + ident)
        total += size
        require(total <= 256 * 1024 * 1024, 'total inputs exceed 256 MiB')
        actual = digest(path.read_bytes())
        require(actual == text(row, 'sha256'), 'input hash drift: ' + ident)
        pins.append({**row, 'bytes': size})
    require(projection_path.stat().st_size <= MAX_JSON, 'projection grew during read')
    packet = {'schema_version': CAPSULE, 'project_id': project_id,
              'native_revision': revision, 'task': task,
              'projection': {'path': str(projection_path.relative_to(root)),
                             'sha256': digest(projection_path.read_bytes())},
              'requirements': [requirements[x] for x in sorted(selected)],
              'inputs': pins, 'decisions': data.get('decisions', []),
              'identity': data.get('identity', {}), 'capabilities': data.get('capabilities', []),
              'unresolved': data.get('unresolved', []),
              'omitted_requirements': [{'id': ident, 'reason': ('inapplicable: ' + row['applicability_reason'])
                                        if not row['applicable'] else 'not assigned/dependent/must/always-review'}
                                       for ident, row in sorted(requirements.items()) if ident not in selected],
              'quality_certified': False, 'authority_authenticated': False,
              'source_completeness_authenticated': False}
    if binding:
        packet.update(context_coverage=binding['coverage'], decisions=binding['decisions'],
                      current_decisions=binding['current_decisions'], corrections=binding['corrections'],
                      deferred_work=binding['deferred_work'],
                      native_identity=binding['native_identity'])
        for source in [binding['coverage']['manifest_ref'], *binding['loaded']]:
            require(digest(bound_bytes(root, source['path'])) == source['sha256'],
                    'SOURCE_DRIFT: context source changed during compilation: ' + source['path'])
        require(len(canonical(packet)) <= MAX_JSON, 'bound capsule exceeds 4 MiB')
    packet['capsule_sha256'] = digest(canonical(packet))
    return packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('build', 'verify'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--input', required=True, help='projection path relative to root')
    parser.add_argument('--task', required=True)
    parser.add_argument('--output', required=True, help='capsule path relative to root')
    parser.add_argument('--bindings', help='explicit context-bindings path relative to root')
    parser.add_argument('--require-complete', action='store_true',
                        help='require verified declared bindings; never proves independent completeness')
    args = parser.parse_args()
    try:
        require(args.root.is_absolute() and args.root.is_dir(), 'absolute existing root required')
        root = args.root
        require(not any(_linked(x) for x in (root, *root.parents)), 'linked root rejected')
        projection_path = local(root, args.input)
        before = digest(projection_path.read_bytes())
        packet = compile_packet(load(projection_path), args.task, root, projection_path,
                                args.bindings, args.require_complete)
        require(before == digest(projection_path.read_bytes()), 'projection changed during compilation')
        output = local(root, args.output, existing=args.operation == 'verify')
        require(output != projection_path, 'output cannot overwrite projection')
        if args.operation == 'verify':
            require(load(output) == packet, 'capsule or source dependencies changed')
        else:
            require(not output.exists(), 'output exists; preserve old capsule and use a new revision path')
            require(output.parent.is_dir(), 'output parent missing')
            with output.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'ok': True, 'operation': args.operation,
                          'capsule_sha256': packet['capsule_sha256'],
                          'requirements': len(packet['requirements']),
                          'inputs': len(packet['inputs']), 'quality_certified': False,
                          'context_coverage': packet.get('context_coverage', {}).get('status', 'unverified'),
                          'source_completeness_authenticated': False}))
        return 0
    except (ContextError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error), 'quality_certified': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
