#!/usr/bin/env python3
"""Compile/verify a declared task context; no jobs, permissions or quality certification."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MAX_JSON = 4 * 1024 * 1024
MAX_INPUT = 64 * 1024 * 1024
SCHEMA = 'atelier.context-projection/1'
CAPSULE = 'atelier.context-capsule/1'


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


def load(path):
    require(path.is_file() and not path.is_symlink(), 'missing/linked JSON input')
    require(path.stat().st_size <= MAX_JSON, 'JSON input exceeds 4 MiB')
    try:
        result = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                            parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ContextError('invalid UTF-8 JSON') from error
    require(isinstance(result, dict), 'JSON input must be an object')
    return result


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
    require(isinstance(value, str) and value, 'missing relative path')
    pure = PurePosixPath(value)
    require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in value
            and pure.as_posix() == value, 'unsafe relative path: ' + value)
    path = root
    for part in pure.parts:
        path = path / part
        require(not path.is_symlink(), 'linked input/output path rejected')
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


def compile_packet(data, task_id, root, projection_path):
    require(data.get('schema_version') == SCHEMA, 'unsupported projection schema')
    project_id, revision = text(data, 'project_id'), text(data, 'native_revision')
    requirements = records(data, 'requirements')
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
    packet['capsule_sha256'] = digest(canonical(packet))
    return packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('build', 'verify'))
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--input', required=True, help='projection path relative to root')
    parser.add_argument('--task', required=True)
    parser.add_argument('--output', required=True, help='capsule path relative to root')
    args = parser.parse_args()
    try:
        require(args.root.is_absolute() and args.root.is_dir(), 'absolute existing root required')
        root = args.root
        require(not any(x.is_symlink() for x in (root, *root.parents)), 'linked root rejected')
        projection_path = local(root, args.input)
        before = digest(projection_path.read_bytes())
        packet = compile_packet(load(projection_path), args.task, root, projection_path)
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
                          'inputs': len(packet['inputs']), 'quality_certified': False}))
        return 0
    except (ContextError, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error), 'quality_certified': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
