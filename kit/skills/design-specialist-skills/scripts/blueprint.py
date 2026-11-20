#!/usr/bin/env python3
"""Versioned skill proposal checks; a recorded approval is not proof of consent."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import types




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

def proposal_hash(data):
    content = {k: v for k, v in data.items() if k not in {'approval', 'checkpoint'}}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _check(data, approved=False):
    errors = []
    def need(value, message):
        if not value:
            errors.append(message)
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    if not isinstance(data, dict):
        return ['blueprint must be an object']
    if data.get('schema_version') != 'skill.blueprint/2':
        return ['unsupported blueprint schema; prepare a current blueprint from actual sources']
    need(text(data.get('id')) and type(data.get('version')) is int and data['version'] > 0, 'proposal identity/version required')
    brief = data.get('brief', {})
    for key in ('goal', 'audience', 'deliverable', 'quality', 'constraints', 'sources'):
        need(bool(brief.get(key)), 'brief missing ' + key)
    criteria = data.get('criteria', [])
    need(isinstance(criteria, list) and bool(criteria), 'nonempty domain criteria required')
    ids = [r.get('id') for r in criteria if isinstance(r, dict)]
    need(len(ids) == len(criteria) and len(ids) == len(set(ids)) and all(text(x) for x in ids), 'unique criterion IDs required')
    for row in criteria:
        for key in ('source', 'intent', 'priority', 'owner_domain', 'artifact', 'acceptance', 'negative_probe', 'proof'):
            need(bool(row.get(key)), 'criterion ' + str(row.get('id')) + ' missing ' + key)
        need(row.get('priority') in {'must', 'should', 'could'}, 'invalid criterion priority')
    architecture = data.get('architecture', {})
    need(architecture.get('kind') in {'single', 'family'}, 'single/family decision required')
    need(text(architecture.get('reason')) and text(architecture.get('alternative')), 'compare organization alternatives')
    stages = data.get('stages', [])
    stage_ids = [s.get('id') for s in stages if isinstance(s, dict)]
    need(bool(stages) and len(stage_ids) == len(stages) and len(stage_ids) == len(set(stage_ids)), 'unique stages required')
    # Installable modules and workflow phases are independent dimensions.
    # A single coherent skill can carry a multi-phase DAG; several independent
    # modules can also contribute to the same phase.
    modules = architecture.get('modules')
    if modules is None:
        need(architecture.get('kind') != 'family', 'family requires explicit installable modules, not a phase count')
    else:
        need(isinstance(modules, list) and bool(modules), 'nonempty architecture modules required')
        if isinstance(modules, list):
            names = [row.get('name') for row in modules if isinstance(row, dict)]
            need(len(names) == len(modules) and all(text(name) and len(name) <= 64 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) for name in names) and len(names) == len(set(names)), 'unique portable installable module names required')
            need(len(modules) == 1 if architecture.get('kind') == 'single' else len(modules) >= 2, 'module count differs from organization decision')
            module_stages = set()
            for row in modules:
                need(isinstance(row, dict), 'module must be an object')
                if not isinstance(row, dict):
                    continue
                assigned = row.get('stage_ids')
                need(isinstance(assigned, list) and bool(assigned) and len(assigned) == len(set(assigned)) and set(assigned) <= set(stage_ids), 'module references unknown or duplicate stages')
                if isinstance(assigned, list):
                    module_stages.update(assigned)
            need(module_stages == set(stage_ids), 'every workflow stage needs an installable module')
    covered = set()
    for stage in stages:
        for key in ('name', 'purpose', 'inputs', 'outputs', 'acceptance', 'handoff', 'permissions', 'quality_process'):
            need(bool(stage.get(key)), 'stage missing ' + key)
        assigned = stage.get('criterion_ids', [])
        need(isinstance(assigned, list) and set(assigned) <= set(ids), 'stage references unknown criteria')
        covered.update(assigned)
        deps = stage.get('depends_on', [])
        need(isinstance(deps, list) and set(deps) <= set(stage_ids) and stage['id'] not in deps, 'invalid stage prerequisites')
    need(covered == set(ids), 'every criterion needs an execution stage')
    graph = {s['id']: s.get('depends_on', []) for s in stages}
    def visit(sid, stack):
        if sid in stack:
            return False
        return all(visit(x, stack | {sid}) for x in graph.get(sid, []) if x in graph)
    need(all(visit(sid, set()) for sid in graph), 'cyclic family prerequisites')
    domains = data.get('team', {}).get('domains', [])
    domain_ids = {d.get('id') for d in domains if isinstance(d, dict)}
    need(bool(domains) and len(domain_ids) == len(domains), 'unique subject-matter domains required')
    need(all(r.get('owner_domain') in domain_ids for r in criteria), 'criterion lacks a real domain owner')
    for domain in domains:
        for key in ('expertise', 'outputs', 'activation', 'independent_qa'):
            need(bool(domain.get(key)), 'domain missing ' + key)
    for key in ('orchestrator', 'independence', 'council_activation', 'local_completion', 'carry_forward', 'anti_loop'):
        need(bool(data.get('team', {}).get(key)), 'team policy missing ' + key)
    errors.extend(check_depth(data, approved))
    if approved:
        pending = data.get('open_questions', [])
        need(not any(q.get('blocking') and q.get('status') != 'resolved' for q in pending), 'blocking question unresolved')
        approval = data.get('approval') or {}
        if not isinstance(approval, dict):
            return errors + ['explicit approval record must be an object']
        need(approval.get('actor') == 'user' and approval.get('proposal_hash') == proposal_hash(data), 'explicit approval of this exact proposal required')
        need(approval.get('proposal_version') == data.get('version'), 'stale proposal approval')
        for key in ('verbatim', 'source', 'timestamp', 'scope'):
            need(bool(approval.get(key)), 'approval provenance missing ' + key)
        need(approval.get('decision') == 'approve', 'approval decision required')
    return errors



def check(data, approved=False):
    """Return a negative result for malformed input instead of crashing a handoff."""
    try:
        return _check(data, approved)
    except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as exc:
        return ['invalid blueprint structure: ' + str(exc)]


def check_depth(data, approved=False):
    """Plan-level cross-reference checks; no claim of actual operation execution."""
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())
    depth = data.get('specialization_depth')
    if not isinstance(depth, dict):
        return ['specialization_depth object required']
    need(depth.get('maturity') in {'sketch', 'specification', 'handoff'}, 'invalid specialization maturity')
    if approved:
        need(depth.get('maturity') in {'specification', 'handoff'}, 'sketch cannot authorize production creation')
    criteria = {row['id'] for row in data.get('criteria', []) if isinstance(row, dict) and 'id' in row}
    stages = {row['id'] for row in data.get('stages', []) if isinstance(row, dict) and 'id' in row}
    domains = {row['id'] for row in data.get('team', {}).get('domains', []) if isinstance(row, dict) and 'id' in row}
    def rows(key, fields):
        values = depth.get(key)
        if not isinstance(values, list):
            errors.append(key + ' must be a list')
            return []
        need(bool(values), key + ' cannot be empty')
        seen = set()
        for row in values:
            if not isinstance(row, dict):
                errors.append(key + ' row must be an object')
                continue
            rid = row.get('id')
            need(nonempty(rid) and rid not in seen, key + ' requires unique IDs')
            if isinstance(rid, str):
                seen.add(rid)
            for field in fields:
                need(bool(row.get(field)), key + ' ' + str(rid) + ' missing ' + field)
        return [r for r in values if isinstance(r, dict)]
    applicability = rows('applicability', ('criterion_id', 'status', 'reason', 'owner_domain', 'due_gate'))
    need({r.get('criterion_id') for r in applicability} == criteria, 'applicability must cover every criterion exactly')
    need(len(applicability) == len({r.get('criterion_id') for r in applicability}), 'duplicate criterion applicability')
    active = set()
    for row in applicability:
        need(row.get('status') in {'applicable', 'absent_by_design', 'blocked', 'pending'}, 'invalid applicability status')
        need(row.get('owner_domain') in domains, 'applicability owner not in team')
        if row.get('status') != 'absent_by_design':
            active.add(row.get('criterion_id'))
        if row.get('status') == 'absent_by_design':
            need(nonempty(row.get('design_decision_ref')), 'absent_by_design needs design decision; tool absence is blocked')
        if approved:
            need(row.get('status') not in {'blocked', 'pending'}, 'creation blocked by unresolved applicability')
    sources = rows('source_methods', ('source_ref', 'claim', 'applicability', 'method', 'verification_due', 'limits'))
    source_ids = {r.get('id') for r in sources}
    contracts = rows('domain_contracts', ('criterion_ids', 'owner_domain', 'typed_inputs', 'typed_outputs', 'rules', 'state_policy', 'failure_recovery', 'invariants', 'consumer', 'source_method_ids'))
    contract_ids = {r.get('id') for r in contracts}
    for row in contracts:
        refs = row.get('criterion_ids', [])
        need(isinstance(refs, list) and bool(refs) and set(refs) <= criteria, 'domain contract references unknown criteria')
        need(row.get('owner_domain') in domains, 'domain contract owner not in team')
        refs = row.get('source_method_ids', [])
        need(isinstance(refs, list) and bool(refs) and set(refs) <= source_ids, 'domain contract references unknown source methods')
    operations = rows('operations', ('criterion_ids', 'contract_ids', 'owner_domain', 'consumer', 'capability_plan', 'recipe_plan', 'transformation_checks', 'evidence_due', 'permissions', 'budget', 'stop_condition'))
    for row in operations:
        need(row.get('owner_domain') in domains, 'operation owner not in team')
        for field, valid in [('criterion_ids', criteria), ('contract_ids', contract_ids)]:
            refs = row.get(field, [])
            need(isinstance(refs, list) and bool(refs) and set(refs) <= valid, 'operation references unknown ' + field)
    cases = rows('acceptance_cases', ('criterion_ids', 'preconditions', 'action', 'expected', 'negative_case', 'proof_kind', 'review_policy'))
    for row in cases:
        refs = row.get('criterion_ids', [])
        need(isinstance(refs, list) and bool(refs) and set(refs) <= criteria, 'acceptance case references unknown criteria')
    children = rows('child_contracts', ('stage_id', 'criterion_ids', 'input_contract', 'output_contract', 'consumer', 'capability_recipe_policy', 'evidence_policy', 'inheritance_check', 'checkpoint_handoff', 'independence'))
    need({r.get('stage_id') for r in children} == stages, 'every stage needs child inheritance contract')
    for row in children:
        refs = row.get('criterion_ids', [])
        need(isinstance(refs, list) and bool(refs) and set(refs) <= criteria, 'child references unknown criteria')
    for values, label in [(contracts, 'domain contracts'), (operations, 'operations'), (cases, 'acceptance cases'), (children, 'child contracts')]:
        covered = set()
        for row in values:
            refs = row.get('criterion_ids', [])
            if isinstance(refs, list):
                covered.update(x for x in refs if isinstance(x, str))
        need(active <= covered, label + ' do not cover all active criteria')
    for key, fields in [('change_policy', ('dependency_invalidation', 'migration', 'carry_forward')), ('recovery_policy', ('checkpoint', 'effect_reconciliation', 'repair_budget', 'stop_condition'))]:
        record = depth.get(key)
        if not isinstance(record, dict):
            errors.append(key + ' object required')
            continue
        for field in fields:
            need(nonempty(record.get(field)), key + ' missing ' + field)
    return errors



def load_bundled(name):
    helper = Path(__file__).resolve().with_name(name + '.py')
    module = types.ModuleType('bundled_' + name)
    module.__file__ = str(helper)
    exec(compile(helper.read_bytes(), str(helper), 'exec'), module.__dict__)
    return module


def current_choice(root, data, children, phase, child_reader=None):
    pin = data.get('production_decision_sha256')
    if not isinstance(pin, str) or not re.fullmatch('[a-f0-9]{64}', pin):
        raise ValueError('bind production_decision_sha256 to the current choice before approving the proposal')
    modules = data['architecture'].get('modules')
    if not modules:
        raise ValueError('declare the exact installable module names and stages before approving creation')
    report = load_bundled('production_choices').verify_project(
        root, 'accept' if children else phase, required_kind='agent')
    if report['decision_sha256'] != pin:
        raise ValueError('production decision differs from the approved proposal; approve a new revision')
    if children:
        expected = {module['name'] for module in modules}
        if len(children) != len(expected) or {child.name for child in children} != expected:
            raise ValueError('supplied child roots differ from the exact approved module set')
        accepted = {row['sha256'] for row in report['evidence_artifacts']['accept']}
        for child in children:
            entry = child_reader(child / 'SKILL.md')
            header = re.match(r'\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', entry.decode('utf-8'), re.S)
            names = re.findall(r'^name:[ \t]*(.*)$', header[1], re.M) if header else []
            if len(names) != 1 or names[0].strip() not in {child.name, f"'{child.name}'", f'"{child.name}"'}:
                raise ValueError('child frontmatter name differs from the approved module: ' + child.name)
            if hashlib.sha256(entry).hexdigest() not in accepted:
                raise ValueError('acceptance evidence does not cover this exact child skill: ' + child.name)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'check', 'hash'))
    parser.add_argument('file', type=Path)
    parser.add_argument('--approved', action='store_true')
    parser.add_argument('--project-root', type=Path, help='Directory containing production-choices.json; defaults to the blueprint directory')
    parser.add_argument('--scale', action='store_true', help='Require reviewed representative-slice evidence with --approved')
    parser.add_argument('--child', action='append', type=Path, default=[], help='Also verify each authored child package inherits the current portable operating standard')
    args = parser.parse_args()
    try:
        if args.scale and (args.command != 'check' or not args.approved):
            raise ValueError('use --scale with check --approved')
        if args.command == 'init':
            template = Path(__file__).resolve().parents[1] / 'assets/blueprint-template.json'
            with args.file.open('x') as stream:
                stream.write(template.read_text())
            print('Draft created; not approved and not ready to create skills.')
            return 0
        data = strict_json_loads(args.file.read_text())
        if not isinstance(data, dict) or data.get('schema_version') != 'skill.blueprint/2':
            raise ValueError('unsupported blueprint schema; prepare a current blueprint from actual sources')
        if args.command == 'hash':
            print(proposal_hash(data))
            return 0
        errors = check(data, args.approved)
        inheritance = None
        child_reader = None
        if args.child:
            module = load_bundled('check_generated_inheritance')
            child_reader = module.read_regular
            inheritance, inherited_errors = module.inspect_children(args.child, Path(__file__).resolve().parents[1])
            errors.extend(inherited_errors)
        choice = None
        if args.approved and not errors:
            try:
                phase = 'scale' if args.scale else 'implement'
                choice = current_choice(args.project_root or args.file.absolute().parent, data,
                                        args.child, phase, child_reader)
            except (OSError, ValueError) as error:
                errors.append('production choices: ' + str(error))
        print(json.dumps({'ok': not errors, 'proposal_hash': proposal_hash(data), 'errors': errors,
                          'limits': 'Record integrity only; verify actual user consent and domain quality.',
                          'supported_schema': 'skill.blueprint/2', 'quality_certified': False,
                          'children_checked': len(args.child), 'operating_standard': inheritance,
                          'production_choice': choice, 'material_gate_passed': choice is not None}, ensure_ascii=False, indent=2))
        return bool(errors)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
