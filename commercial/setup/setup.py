#!/usr/bin/env python3
"""Install and recover an audited Agent System buyer package without development tools."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import selectors
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import uuid

sys.dont_write_bytecode = True
PLAN = 'codex-agents.buyer-setup-plan/1'
JOURNAL = 'codex-agents.buyer-setup-journal/1'
MANIFEST = 'codex-agents.commercial-package/1'
ORCHESTRATOR = 'atelier-orchestrator'
HASH = re.compile(r'[0-9a-f]{64}\Z')
COMMIT = re.compile(r'[0-9a-f]{40}\Z')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def pairs(values):
    result = {}
    for name, val in values:
        require(name not in result, 'Duplicate JSON field: ' + name)
        result[name] = val
    return result


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(path):
    path = Path(os.path.abspath(os.fspath(path)))
    for ancestor in reversed((path, *path.parents)):
        try:
            mode = ancestor.lstat().st_mode
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(mode), 'Linked setup or target path: ' + str(ancestor))
    return path


def inside(root, rel):
    require(isinstance(rel, str) and rel and '\\' not in rel and '\0' not in rel,
            'Unsafe package path')
    pure = PurePosixPath(rel)
    require(not pure.is_absolute() and '..' not in pure.parts and pure.as_posix() == rel,
            'Unsafe package path')
    return safe(root / pure)


def read(path, limit=32 * 1024 * 1024):
    path = safe(path)
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_size <= limit, 'Unexpected or oversized setup input')
    with path.open('rb') as source:
        data = source.read(limit + 1)
    require(len(data) <= limit, 'Setup input grew beyond its bound')
    return data


def load(path):
    return json.loads(read(path).decode('utf8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write(path, value, *, exclusive=False):
    path = safe(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = encoded(value)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        if exclusive:
            os.link(temp, path)
        else:
            os.replace(temp, path)
        sync_dir(path.parent)
    finally:
        Path(temp).unlink(missing_ok=True)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def package_info(package):
    package = safe(package)
    raw = read(package / 'product-manifest.json')
    data = json.loads(raw.decode(), object_pairs_hook=pairs)
    require(data.get('schema') == MANIFEST and data.get('product_id') == 'codex-agent-system',
            'This is not a supported commercial package')
    require(COMMIT.fullmatch(str(data.get('source_commit', ''))), 'Package source commit is missing')
    entries = data.get('files')
    require(isinstance(entries, dict) and 34 <= len(entries) <= 20000, 'Invalid package file inventory')
    actual = set()
    total = 0
    for root, directories, names in os.walk(package, followlinks=False):
        for name in directories + names:
            path = Path(root) / name
            info = path.lstat()
            require(not stat.S_ISLNK(info.st_mode), 'Package contains a link')
            require(stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode), 'Package contains a special file')
        for name in names:
            relative = (Path(root) / name).relative_to(package).as_posix()
            if relative not in ('product-manifest.json', 'SHA256SUMS'):
                actual.add(relative)
    require(actual == set(entries), 'Package has missing or unexpected files; extract a clean verified copy')
    folded = set()
    for relative, entry in entries.items():
        path = inside(package, relative)
        require(isinstance(entry, dict) and set(entry) == {'sha256', 'size', 'mode'}, 'Invalid package file record')
        require(HASH.fullmatch(str(entry['sha256'])) and type(entry['size']) is int
                and 0 <= entry['size'] <= 256 * 1024 * 1024 and type(entry['mode']) is int
                and entry['mode'] in (0o644, 0o755, 0o600), 'Invalid file digest, size or mode')
        key = relative.casefold()
        require(key not in folded, 'Package has case-colliding paths')
        folded.add(key)
        total += entry['size']
        require(total <= 2 * 1024 * 1024 * 1024, 'Package exceeds supported size')
        content = read(path, 256 * 1024 * 1024)
        require(len(content) == entry['size'] and digest(content) == entry['sha256'],
                'Package file differs from inventory: ' + relative)
        # Extraction may lose executable flags. Installation applies declared modes.
    product = safe(package / 'product')
    require((product / 'kit/manifest.json').is_file(), 'Package core resource is absent')
    return data, digest(raw)


def paths(home, state=None):
    home = safe(Path(home).expanduser().resolve())
    state = safe(Path(state).expanduser().resolve() if state else home / '.local/share/codex-agent-system')
    destination = home / '.agents/skills'
    legacy = home / '.codex/skills'
    for root in (destination, legacy):
        require(not state.is_relative_to(root) and not root.is_relative_to(state),
                'State and backups must stay outside skill discovery directories')
    return home, state, destination, legacy


def engines(package):
    product = package / 'product'
    return (module(product / 'kit/portable/update_skill_suite.py', '_buyer_core_updater'),
            module(product / 'scripts/install_host_profile.py', '_buyer_host_updater'))


def tree(root):
    root = safe(root)
    if not root.exists():
        return None
    require(root.is_dir(), 'Expected an optional skill directory')
    result = {}
    for parent, directories, names in os.walk(root, followlinks=False):
        for name in directories + names:
            mode = (Path(parent) / name).lstat().st_mode
            require(not stat.S_ISLNK(mode) and (stat.S_ISREG(mode) or stat.S_ISDIR(mode)),
                    'Linked or special optional skill input')
        for name in names:
            path = Path(parent) / name
            result[path.relative_to(root).as_posix()] = {'sha256': digest(read(path)),
                 'bytes': path.stat().st_size, 'mode': stat.S_IMODE(path.stat().st_mode)}
    return result


def optional_plan(package, destination, legacy):
    source = package / 'product/optional-skills' / ORCHESTRATOR
    target = destination / ORCHESTRATOR
    desired, before = tree(source), tree(target)
    require(desired and 'SKILL.md' in desired, 'Orchestrator resources are missing')
    conflicts = []
    baseline = load(package / 'product/optional-skills/UPDATE_BASELINES.json')
    known = [row['files'] for row in baseline['skills'][ORCHESTRATOR].values()]
    if before is not None and before != desired and before not in known:
        conflicts.append('Orchestrator has unknown local changes; reconcile them without overwrite.')
    if (legacy / ORCHESTRATOR).exists():
        conflicts.append('An Orchestrator also exists in the legacy root; resolve the duplicate first.')
    return {'source': str(source), 'target': str(target), 'before': before, 'after': desired,
            'action': 'noop' if before == desired else 'install', 'conflicts': conflicts}


def host_check(codex, home):
    executable = codex or shutil.which('codex')
    result = {'executable': executable, 'version': None, 'authentication': 'unverified', 'ready': False,
              'next': 'Install Codex using its official setup, then sign in with your own account.'}
    if not executable:
        return result
    try:
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / '.codex'))
        check = subprocess.run([executable, '--version'], capture_output=True, timeout=10, env=env, text=True)
        match = re.search(r'codex-cli (\d+)\.(\d+)\.(\d+)', check.stdout)
        if not match:
            result['next'] = 'Use a supported Codex CLI; the executable did not return a recognized version.'
            return result
        result['version'] = '.'.join(match.groups())
        if tuple(map(int, match.groups())) < (0, 166, 0):
            result['next'] = 'Update Codex CLI to 0.166.0 or later, then run doctor again.'
            return result
        login = subprocess.run([executable, 'login', 'status'], capture_output=True, timeout=15, env=env, text=True)
        result['authentication'] = 'signed-in' if login.returncode == 0 else 'sign-in-required'
        result['ready'] = login.returncode == 0
        result['next'] = 'Open a fresh Codex session after installation.' if result['ready'] else 'Run codex login using your own account.'
    except (OSError, subprocess.TimeoutExpired):
        result['next'] = 'Codex did not respond. Run codex --version and codex login status in your terminal.'
    return result


def doctor(package, home, state=None, codex=None):
    home, state, destination, legacy = paths(home, state)
    metadata, fingerprint = package_info(package)
    system, machine = platform.system(), platform.machine().lower()
    supported = system in ('Darwin', 'Linux') and machine in ('arm64', 'aarch64', 'x86_64', 'amd64')
    host = host_check(codex, home)
    runtime = metadata.get('runtime', {})
    return {'status': 'ready' if supported and host['ready'] else 'action-required',
            'product_id': metadata['product_id'], 'product_version': metadata['product_version'],
            'source_commit': metadata['source_commit'], 'package_manifest_sha256': fingerprint,
            'platform': {'os': system, 'architecture': machine, 'supported_skills': supported,
                         'python': platform.python_version()},
            'components': {'skills': {'ready_for_audit': supported, 'expected': 33},
                           'orchestrator': {'included': True, 'recommended': True},
                           'profile_and_roles': {'included': True, 'native_configuration_mutated': False},
                           'workbench': runtime or {'status': 'separate-artifact', 'next': 'Use the supplied runtime guide.'}},
            'host': host, 'destination': str(destination), 'state': str(state),
            'next': host['next'] if not host['ready'] else 'Run audit, inspect its targets, then install the approved plan.'}


def retained_package(package, state, fingerprint):
    """Keep verified sources available when a buyer moves or removes Downloads."""
    cached = safe(state / 'packages' / fingerprint)
    require(not state.is_relative_to(package), 'Setup state cannot be inside the received package')
    if package == cached:
        return package
    with locked(state):
        if cached.exists():
            require(package_info(cached)[1] == fingerprint, 'Retained package source was changed')
            return cached
        cached.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = cached.parent / ('.staging-' + uuid.uuid4().hex)
        try:
            shutil.copytree(package, temporary)
            require(package_info(temporary)[1] == fingerprint, 'Package changed while retaining recovery sources')
            os.replace(temporary, cached)
            sync_dir(cached.parent)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return cached


def audit(package, home, state, plan_path, entitlement=None):
    package = safe(package)
    metadata, manifest_sha = package_info(package)
    home, state, destination, legacy = paths(home, state)
    require(platform.system() in ('Darwin', 'Linux'), 'This setup supports skills on macOS and Linux. Use the Work importer for the Work bundle.')
    package = retained_package(package, state, manifest_sha)
    core, host = engines(package)
    plan_path = safe(plan_path)
    require(not plan_path.exists(), 'Choose a new plan path for this audit')
    require(not any(plan_path.is_relative_to(p) for p in (package, destination, legacy)), 'Plans must be outside the package and discovery roots')
    key = uuid.uuid4().hex
    operation = state / 'operations' / key
    core_plan = core.audit(package / 'product/kit', destination, legacy, operation / 'core-backups')
    profile_plan = host.audit(package / 'product', home / '.codex', destination / 'agent-foundry')
    optional = optional_plan(package, destination, legacy)
    blockers = list(core_plan['blockers']) + optional['conflicts']
    launcher = state / 'Open Codex.command'
    launcher_text = read(launcher).decode() if launcher.exists() else None
    launcher_before = digest(launcher_text.encode()) if launcher_text is not None else None
    if launcher_before is not None:
        previous = state / 'installed.json'
        known_launcher = False
        if previous.exists():
            old = load(Path(load(previous)['journal']))
            known_launcher = old.get('launcher') == str(launcher) and old.get('launcher_sha256') == launcher_before
        if not known_launcher:
            blockers.append('The generated launcher has unknown changes; preserve them and reconcile before another install.')
    license_record = None
    entitlement_data = None
    if entitlement:
        data = read(safe(entitlement), 256 * 1024)
        entitlement_data = data
        license_record = {'source': str(operation / 'entitlement-document.json'), 'sha256': digest(data)}
        # Entitlement validation belongs to the delivery trust boundary. Preserve exact bytes here.
    core_path, profile_path = operation / 'core-plan.json', operation / 'host-plan.json'
    mode = 'fresh' if not core_plan['discovered'] and optional['before'] is None else (
        'known-current' if all(e['action'] == 'noop' for e in core_plan['entries']) and optional['action'] == 'noop' else
        'partial' if len(core_plan['discovered']) < 33 else 'update')
    plan = {'schema': PLAN, 'operation': str(operation), 'package': str(package), 'manifest_sha256': manifest_sha,
            'source_commit': metadata['source_commit'], 'product_id': metadata['product_id'], 'product_version': metadata['product_version'],
            'edition': metadata.get('edition'), 'home': str(home), 'state': str(state), 'mode': mode,
            'core_plan': str(core_path), 'core_plan_sha256': digest(encoded(core_plan)),
            'profile_plan': str(profile_path), 'profile_plan_sha256': digest(encoded(profile_plan)),
            'optional': optional, 'entitlement': license_record, 'launcher_before_sha256': launcher_before,
            'launcher_before': launcher_text,
            'blockers': blockers, 'ready': not blockers, 'created_at': timestamp()}
    operation.mkdir(mode=0o700, parents=True)
    if entitlement_data is not None:
        with (operation / 'entitlement-document.json').open('xb') as receipt:
            receipt.write(entitlement_data)
            receipt.flush()
            os.fsync(receipt.fileno())
        os.chmod(operation / 'entitlement-document.json', 0o600)
    write(core_path, core_plan, exclusive=True)
    write(profile_path, profile_plan, exclusive=True)
    write(plan_path, plan, exclusive=True)
    return {'status': 'ready' if plan['ready'] else 'blocked', 'plan': str(plan_path),
            'plan_sha256': digest(read(plan_path)), 'mode': mode, 'expected_skills': 33,
            'recommended_orchestrator': True, 'roles': 12, 'destination': str(destination),
            'journal': str(operation / 'journal.json'), 'blockers': blockers,
            'next': 'Approve the exact plan SHA-256 before install.' if plan['ready'] else 'Preserve changes and resolve the listed conflicts; run a new audit.'}


@contextmanager
def locked(state, home=None):
    state = safe(state)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = safe((home / '.agents/.buyer-setup.lock') if home is not None else state / '.setup.lock')
    lock.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        require(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1, 'Invalid buyer setup lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another buyer setup process is active. Wait and inspect its journal before another action.')
        yield
    finally:
        os.close(fd)


def checked_plan(path, expected):
    path = safe(path)
    raw = read(path)
    require(isinstance(expected, str) and HASH.fullmatch(expected) and digest(raw) == expected,
            'Approval does not match the exact saved setup plan')
    plan = json.loads(raw.decode(), object_pairs_hook=pairs)
    require(plan.get('schema') == PLAN and plan.get('ready') is True and not plan.get('blockers'), 'Setup plan is blocked')
    package = safe(plan['package'])
    metadata, fingerprint = package_info(package)
    require(fingerprint == plan['manifest_sha256'] and metadata['source_commit'] == plan['source_commit'], 'Package changed after audit')
    home, state, _, _ = paths(plan['home'], plan['state'])
    operation = safe(plan['operation'])
    require(operation.parent == state / 'operations' and re.fullmatch('[a-f0-9]{32}', operation.name), 'Setup operation outside owned state')
    for name in ('core', 'profile'):
        other = safe(plan[name + '_plan'])
        expected_name = 'core-plan.json' if name == 'core' else 'host-plan.json'
        require(other == operation / expected_name and digest(read(other)) == plan[name + '_plan_sha256'], 'Subplan changed after audit')
    return plan, package, home, state, operation


def checked_journal(journal_path):
    journal_path = safe(journal_path)
    journal = load(journal_path)
    require(journal.get('schema') == JOURNAL and journal_path == safe(journal['operation']) / 'journal.json', 'Unknown setup journal')
    plan, package, home, state, operation = checked_plan(Path(journal['plan']), journal['plan_sha256'])
    require(operation == journal_path.parent and journal['manifest_sha256'] == plan['manifest_sha256'], 'Journal scope mismatch')
    if 'core_journal' in journal:
        core, _ = engines(package)
        native_path = safe(journal['core_journal'])
        require(native_path.name == 'journal.json' and native_path.parent.parent == operation / 'core-backups',
                'Core journal outside the composite operation')
        native = core.load_journal(native_path)[1]
        require(native['plan'] == core.read_json(plan['core_plan']), 'Core journal belongs to another saved plan')
    if 'profile_journal' in journal:
        require(safe(journal['profile_journal']) == operation / 'host-journal.json', 'Host journal outside the composite operation')
    if 'launcher' in journal:
        require(safe(journal['launcher']) == state / 'Open Codex.command', 'Launcher outside the setup state')
    if 'uninstall_entries' in journal:
        require(journal['status'] in ('uninstalling','uninstalled') and isinstance(journal['uninstall_entries'], list),
                'Unexpected uninstall record')
        permitted_trees = {str(home / '.agents/skills' / n) for n in engines(package)[0].NAMES | {ORCHESTRATOR}}
        permitted_files = {str(home / '.codex/agents' / row['file']) for row in load(package / 'product/agent-profiles/manifest.json')['roles']}
        permitted_files.add(str(state / 'Open Codex.command'))
        observed = set()
        for entry in journal['uninstall_entries']:
            target = str(safe(entry['target']))
            require(target not in observed, 'Duplicate uninstall target')
            observed.add(target)
            valid = (entry['kind'] == 'tree' and target in permitted_trees or
                     entry['kind'] == 'file' and target in permitted_files or
                     entry['kind'] == 'profile' and target == str(home / '.codex/AGENTS.md'))
            require(valid, 'Uninstall journal exceeds managed scope')
    return journal, plan, package, home, state, operation


def core_receipt(core, plan):
    native = core.read_json(plan['core_plan'])
    ref = Path(native['backup_root']) / ('plan-' + core.sha(core.encode(native)) + '.json')
    if ref.exists():
        path = Path(core.read_json(ref)['journal'])
        core.load_journal(path)
        return path
    lock = Path(native['backup_root']) / '.skill-suite.lock'
    if lock.exists():
        row = core.read_json(lock)
        require(row['plan_sha256'] == core.sha(core.encode(native)), 'Another core operation is unresolved')
        return Path(row['operation']) / 'journal.json'
    return None


def apply_optional(plan, operation, journal):
    item = plan['optional']
    target, source = Path(item['target']), Path(item['source'])
    before, after = item['before'], item['after']
    backup = operation / 'orchestrator-before'
    phase = journal.get('optional_phase', 'pending')
    if phase == 'complete':
        require(tree(target) == after, 'Orchestrator changed since installation')
        return
    if phase == 'pending':
        require(tree(target) == before, 'Orchestrator changed since audit')
        if before is not None and item['action'] != 'noop':
            if backup.exists():
                require(tree(backup) == before, 'Unknown optional backup')
            else:
                shutil.copytree(target, backup)
        journal['optional_phase'] = 'backed-up'
        write(operation / 'journal.json', journal)
        phase = 'backed-up'
    if phase == 'backed-up':
        require(tree(target) == before, 'Orchestrator changed before staging')
        if item['action'] != 'noop':
            # Destination and state may be on different filesystems. Stage beside target parent but outside discovery.
            stage = target.parent.parent / ('.buyer-orchestrator-' + operation.name)
            require(not stage.exists(), 'Unknown external optional staging path; reconcile it first')
            journal['optional_stage'] = str(stage)
        journal['optional_phase'] = 'staging'
        write(operation / 'journal.json', journal)
        phase = 'staging'
    if phase == 'staging':
        require(tree(target) == before, 'Orchestrator changed while preparing its payload')
        if item['action'] != 'noop':
            stage = safe(journal['optional_stage'])
            require(stage == target.parent.parent / ('.buyer-orchestrator-' + operation.name), 'Optional stage ownership changed')
            if stage.exists():
                if tree(stage) != after:
                    # The durable staging phase owns this incomplete copy. Original target is still intact.
                    shutil.rmtree(stage)
            if not stage.exists():
                stage.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, stage)
            require(tree(stage) == after, 'Optional source changed during copy')
        journal['optional_phase'] = 'prepared'
        write(operation / 'journal.json', journal)
        phase = 'prepared'
    if phase == 'prepared':
        if item['action'] != 'noop':
            stage = safe(journal['optional_stage'])
            old = target.parent.parent / ('.buyer-orchestrator-old-' + operation.name)
            if old.exists():
                require(tree(old) == before and not target.exists(), 'Ambiguous optional old move')
            else:
                require(tree(target) == before, 'Optional target changed before replacement')
                if before is not None:
                    os.replace(target, old)
            journal['optional_old'] = str(old)
        journal['optional_phase'] = 'old-moved'
        write(operation / 'journal.json', journal)
        phase = 'old-moved'
    if phase == 'old-moved':
        if item['action'] != 'noop':
            stage, old = safe(journal['optional_stage']), safe(journal['optional_old'])
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                require(tree(target) == after and not stage.exists(), 'Ambiguous optional install')
            else:
                require(tree(stage) == after, 'Optional staged bytes changed')
                os.replace(stage, target)
            if old.exists():
                require(tree(old) == before, 'Optional old bytes changed')
                shutil.rmtree(old)
        require(tree(target) == after, 'Optional target verification failed')
        journal['optional_phase'] = 'complete'
        write(operation / 'journal.json', journal)


def launch_arguments(home, product):
    rows = load(product / 'agent-profiles/manifest.json')['roles']
    arguments = []
    for role in rows:
        path = home / '.codex/agents' / role['file']
        text = read(path).decode()
        description = re.search(r'^description = (".*")$', text, re.M)
        require(description is not None, 'Role description is missing')
        name = role['file'][:-5]
        arguments += ['-c', 'agents.' + name + '.description=' + description.group(1),
                      '-c', 'agents.' + name + '.config_file=' + json.dumps(str(path))]
    return arguments


def make_launcher(home, state, product, expected_before=None):
    flags = launch_arguments(home, product)
    executable = shutil.which('codex')
    if executable is None and (home / '.local/bin/codex').is_file():
        executable = str(home / '.local/bin/codex')
    executable = executable or 'codex'
    environment = ['HOME=' + str(home), 'CODEX_HOME=' + str(home / '.codex')]
    content = '#!/bin/sh\nset -eu\nexec env ' + ' '.join(shlex.quote(x) for x in environment) + ' ' + shlex.quote(executable) + ' ' + ' '.join(shlex.quote(x) for x in flags) + ' "$@"\n'
    path = state / 'Open Codex.command'
    before = digest(read(path)) if path.exists() else None
    require(before in (expected_before, digest(content.encode())), 'Generated launcher changed during setup; preserve it')
    fd, tmp = tempfile.mkstemp(prefix='.codex-launch-', dir=state)
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(content.encode()); file.flush(); os.fsync(file.fileno())
        os.chmod(tmp, 0o755)
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return str(path)


def install(plan_path, expected, *, resume=None):
    plan, package, home, state, operation = checked_plan(plan_path, expected)
    core, host = engines(package)
    journal_path = operation / 'journal.json'
    with locked(state, home):
        if journal_path.exists():
            journal, saved, *_ = checked_journal(journal_path)
            require(saved == plan, 'Resume uses a different setup plan')
            require(resume is not None and safe(resume) == journal_path or journal['status'] == 'complete',
                    'This operation started already; use install --resume with its journal')
            require(journal['status'] not in ('rolling-back', 'rolled-back', 'uninstalling', 'uninstalled'), 'Cannot install after recovery or uninstall began')
            if journal['status'] == 'complete':
                return {'status': 'installed', 'journal': str(journal_path), 'verification': verify(journal_path),
                        'launcher': journal['launcher'], 'next': 'Open a fresh Codex session through the generated launcher.'}
        else:
            require(resume is None, 'The requested journal does not exist; inspect the audited operation path')
            require(core.comparable(core.audit(package / 'product/kit', home / '.agents/skills', home / '.codex/skills', operation / 'core-backups')) == core.comparable(core.read_json(plan['core_plan'])), 'Core targets changed after audit')
            require(host.audit(package / 'product', home / '.codex', home / '.agents/skills/agent-foundry') == host.load(Path(plan['profile_plan'])), 'Host target changed after audit')
            require(optional_plan(package, home / '.agents/skills', home / '.codex/skills') == plan['optional'], 'Orchestrator changed after audit')
            if plan['entitlement']:
                require(digest(read(Path(plan['entitlement']['source']))) == plan['entitlement']['sha256'], 'Entitlement document changed after audit')
            journal = {'schema': JOURNAL, 'operation': str(operation), 'plan': str(safe(plan_path)), 'plan_sha256': expected,
                       'manifest_sha256': plan['manifest_sha256'], 'status': 'installing', 'created_at': timestamp()}
            write(journal_path, journal, exclusive=True)
        try:
            if not journal.get('core_complete'):
                native_journal = core_receipt(core, plan)
                if native_journal and native_journal.exists() and core.load_journal(native_journal)[1]['status'] == 'complete':
                    result = core.apply_plan(Path(plan['core_plan']))
                else:
                    result = core.apply_plan(Path(plan['core_plan']), native_journal)
                journal.update(core_complete=True, core_journal=result['journal'])
                write(journal_path, journal)
            if not journal.get('profile_complete'):
                home.joinpath('.codex').mkdir(parents=True, exist_ok=True)
                result = host.apply(Path(plan['profile_plan']), operation / 'host-journal.json')
                journal.update(profile_complete=True, profile_journal=result['journal'])
                write(journal_path, journal)
            apply_optional(plan, operation, journal)
            if plan['entitlement']:
                destination = state / 'purchases' / (plan['entitlement']['sha256'] + '.json')
                destination.parent.mkdir(mode=0o700, exist_ok=True)
                content = read(Path(plan['entitlement']['source']))
                require(digest(content) == plan['entitlement']['sha256'], 'Entitlement changed during installation')
                if destination.exists():
                    require(read(destination) == content, 'Existing purchase record disagrees')
                else:
                    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'wb') as out:
                        out.write(content); out.flush(); os.fsync(out.fileno())
                journal['retained_entitlement'] = str(destination)
            journal['launcher'] = make_launcher(home, state, package / 'product', plan.get('launcher_before_sha256'))
            journal['launcher_sha256'] = digest(read(Path(journal['launcher'])))
            journal.update(status='complete', finished_at=timestamp())
            write(journal_path, journal)
            write(state / 'installed.json', {'schema': 'codex-agents.buyer-installation/1', 'journal': str(journal_path),
                  'source_commit': plan['source_commit'], 'product_version': plan['product_version'], 'edition': plan['edition']})
            report = verify(journal_path)
            return {'status': 'installed', 'journal': str(journal_path), 'verification': report,
                    'launcher': journal['launcher'], 'next': 'Open the generated Codex launcher, then run discover and your first task.'}
        except BaseException as exc:
            journal.update(status='interrupted', error=type(exc).__name__ + ': ' + str(exc))
            write(journal_path, journal)
            raise


def verify(journal_path):
    journal, plan, package, home, state, operation = checked_journal(journal_path)
    require(journal['status'] == 'complete', 'Installation is incomplete; resume its saved plan first')
    core, host = engines(package)
    core_status = core.verify(package / 'product/kit', home / '.agents/skills', home / '.codex/skills', journal['core_journal'])
    host_status = host.verify_or_rollback(Path(journal['profile_journal']))
    optional = tree(Path(plan['optional']['target'])) == plan['optional']['after']
    require(digest(read(Path(journal['launcher']))) == journal['launcher_sha256'], 'Generated launcher changed; preserve and reconcile its local edits')
    require(core_status['ready'] and host_status['ok'] and optional, 'Managed files changed; preserve them and create a new audit')
    return {'status': 'verified-files', 'source_commit': plan['source_commit'], 'product_version': plan['product_version'],
            'skills': core_status['verified_skills'], 'orchestrator': optional, 'profile_and_roles': host_status['files'],
            'icons_preserved': core_status['visual_preservation_verified'], 'host_discovery_verified': False,
            'behavior_verified': False, 'license_record_retained': journal.get('retained_entitlement')}


def rollback(journal_path):
    journal, plan, package, home, state, operation = checked_journal(journal_path)
    core, host = engines(package)
    with locked(state, home):
        if journal['status'] == 'rolled-back':
            return {'status': 'rolled-back', 'journal': str(journal_path), 'changed': 0}
        require(journal['status'] in ('complete', 'rolling-back'), 'Finish or reconcile installation before rollback')
        # Validate every boundary before starting a multi-component restore.
        if journal['status'] == 'complete':
            verify(journal_path)
            require(tree(Path(plan['optional']['target'])) == plan['optional']['after'], 'Optional source drift')
            native_operation, native = core.load_journal(Path(journal['core_journal']))
            for i, (entry, done) in enumerate(zip(native['plan']['entries'], native['states'])):
                if entry['before'] is not None and core.snapshot(Path(entry['target'])) != entry['before']:
                    _, backup, _, _ = core.journal_paths(entry, native_operation, i)
                    require(core.snapshot(backup) == entry['before'], 'Core rollback backup integrity failed')
            optional_target = Path(plan['optional']['target'])
            if plan['optional']['before'] is not None and plan['optional']['before'] != plan['optional']['after']:
                require(tree(operation / 'orchestrator-before') == plan['optional']['before'], 'Optional rollback backup integrity failed')
            for suffix in ('restore', 'discard'):
                require(not (optional_target.parent.parent / ('.buyer-orchestrator-' + suffix + '-' + operation.name)).exists(),
                        'Unknown optional rollback stage exists; reconcile before restore')
            journal['status'] = 'rolling-back'
            write(Path(journal_path), journal)
        item = plan['optional']
        target, before = Path(item['target']), item['before']
        if not journal.get('optional_rolled_back'):
            actual = tree(target)
            discarded = safe(target.parent.parent / ('.buyer-orchestrator-discard-' + operation.name))
            restored = safe(target.parent.parent / ('.buyer-orchestrator-restore-' + operation.name))
            require(actual in (item['after'], before) or
                    (actual is None and tree(discarded) == item['after']),
                    'Orchestrator changed after install; preserve later work')
            if actual != before:
                if before is not None:
                    backup = operation / 'orchestrator-before'
                    require(tree(backup) == before, 'Orchestrator backup unavailable')
                    if restored.exists() and tree(restored) != before:
                        shutil.rmtree(restored)
                    if not restored.exists():
                        shutil.copytree(backup, restored)
                    require(tree(restored) == before, 'Optional restore payload differs from backup')
                if target.exists():
                    require(not discarded.exists(), 'Optional discard conflicts with current source')
                    os.replace(target, discarded)
                if before is not None:
                    os.replace(restored, target)
            require(tree(target) == before, 'Optional rollback read-back failed')
            if discarded.exists():
                require(tree(discarded) == item['after'], 'Optional discard differs from installed source')
                shutil.rmtree(discarded)
            journal['optional_rolled_back'] = True
            write(Path(journal_path), journal)
        if not journal.get('profile_rolled_back'):
            profile = Path(journal['profile_journal'])
            if host.load(profile)['status'] != 'rolled_back':
                host.verify_or_rollback(profile, True)
            journal['profile_rolled_back'] = True
            write(Path(journal_path), journal)
        if not journal.get('core_rolled_back'):
            core.rollback(Path(journal['core_journal']))
            journal['core_rolled_back'] = True
            write(Path(journal_path), journal)
        if not journal.get('launcher_rolled_back'):
            launcher = Path(journal['launcher'])
            prior = plan.get('launcher_before')
            observed = read(launcher) if launcher.exists() else None
            prior_hash = digest(prior.encode()) if prior is not None else None
            require(prior_hash == plan.get('launcher_before_sha256'), 'Launcher backup differs from the approved plan')
            require((digest(observed) if observed is not None else None) in (journal['launcher_sha256'], prior_hash),
                    'Generated launcher changed during rollback')
            if prior is None:
                launcher.unlink(missing_ok=True)
            elif observed != prior.encode():
                host.atomic(launcher, prior, 0o755)
            journal['launcher_rolled_back'] = True
            write(Path(journal_path), journal)
        journal.update(status='rolled-back', rolled_back_at=timestamp())
        write(Path(journal_path), journal)
        return {'status': 'rolled-back', 'journal': str(journal_path), 'purchase_records_preserved': True,
                'next': 'Open a fresh Codex session and verify the prior workflow.'}


def uninstall(journal_path):
    journal, plan, package, home, state, operation = checked_journal(journal_path)
    core, host = engines(package)
    with locked(state, home):
        if journal['status'] == 'uninstalled':
            return {'status': 'uninstalled', 'journal': str(journal_path), 'changed': 0}
        require(journal['status'] in ('complete', 'uninstalling'), 'Reconcile or finish this installation first')
        if journal['status'] == 'complete':
            verify(journal_path)
            candidates = []
            native = core.load_journal(Path(journal['core_journal']))[1]
            for entry, done in zip(native['plan']['entries'], native['states']):
                if entry['action'] != 'retire':
                    candidates.append({'kind': 'tree', 'target': entry['target'], 'before': core.snapshot(Path(entry['target']))})
            candidates.append({'kind': 'tree', 'target': plan['optional']['target'], 'before': core.snapshot(Path(plan['optional']['target']))})
            for row in host.load(Path(journal['profile_journal']))['changes']:
                if Path(row['target']).name != 'AGENTS.md':
                    candidates.append({'kind': 'file', 'target': row['target'], 'before': row['desired']})
            profile = home / '.codex/AGENTS.md'
            content = host.read(profile)
            begin, end = content.index(host.START), content.index(host.END) + len(host.END)
            desired = content[:begin] + content[end:]
            candidates.append({'kind': 'profile', 'target': str(profile), 'before': content, 'after': desired})
            launcher = Path(journal['launcher'])
            require(digest(read(launcher)) == journal['launcher_sha256'], 'Generated launcher changed; preserve local work')
            candidates.append({'kind': 'file', 'target': str(launcher), 'before': read(launcher).decode()})
            journal.update(status='uninstalling', uninstall_entries=candidates, uninstall_done=[])
            write(Path(journal_path), journal)
        for index, entry in enumerate(journal['uninstall_entries']):
            if index in journal['uninstall_done']:
                continue
            target = safe(entry['target'])
            stash = operation / 'uninstalled' / str(index)
            stash.parent.mkdir(parents=True, exist_ok=True)
            if entry['kind'] == 'tree':
                observed = core.snapshot(target)
                if observed is not None:
                    require(observed == entry['before'], 'Uninstall tree changed; preserve local work')
                    if stash.exists() and core.snapshot(stash) != entry['before']:
                        shutil.rmtree(stash)
                    if not stash.exists():
                        shutil.copytree(target, stash)
                    require(core.snapshot(stash) == entry['before'], 'Uninstall backup failed')
                    shutil.rmtree(target)
                else:
                    require(core.snapshot(stash) == entry['before'], 'Uninstall target vanished without owned backup')
            elif entry['kind'] == 'file':
                observed = host.read(target)
                if observed is not None:
                    require(observed == entry['before'], 'Uninstall role changed; preserve local work')
                    if stash.exists():
                        require(stash.read_text() == observed, 'Uninstall file backup differs')
                    else:
                        host.atomic(stash, observed, 0o600)
                    target.unlink()
                else:
                    require(stash.exists() and stash.read_text() == entry['before'], 'Role missing without backup')
            else:
                observed = host.read(target)
                require(observed in (entry['before'], entry['after']), 'Profile changed during uninstall; reconcile first')
                if observed != entry['after']:
                    stash.write_text(observed)
                    host.atomic(target, entry['after'], 0o644)
            journal['uninstall_done'].append(index)
            write(Path(journal_path), journal)
        journal.update(status='uninstalled', uninstalled_at=timestamp())
        write(Path(journal_path), journal)
        return {'status': 'uninstalled', 'journal': str(journal_path), 'removed_managed_entries': len(journal['uninstall_entries']),
                'projects_preserved': True, 'purchase_records_preserved': True, 'backups': str(operation / 'uninstalled'),
                'next': 'Keep your purchase record and recovery journal. Other skills and project data remain in place.'}


def status(home, state=None):
    home, state, _, _ = paths(home, state)
    record = state / 'installed.json'
    if not record.exists():
        return {'status': 'not-installed-by-this-setup', 'state': str(state),
                'next': 'Run doctor and audit. Existing public installations will be inspected, not overwritten blindly.'}
    data = load(record)
    journal = load(Path(data['journal']))
    return {'status': journal['status'], 'product_version': data['product_version'], 'source_commit': data['source_commit'],
            'journal': data['journal'], 'host_discovery_verified': False,
            'next': 'Run verify for current on-disk state and discover for a fresh Codex host observation.'}


def discover(journal_path, codex=None, cwd=None):
    journal, plan, package, home, state, operation = checked_journal(journal_path)
    verify(journal_path)
    executable = codex or shutil.which('codex')
    require(executable, 'Install Codex or pass its actual --codex path')
    args = launch_arguments(home, package / 'product')
    project = safe(cwd or home)
    require(project.is_dir(), 'Discovery workspace must exist')
    process = subprocess.Popen([executable, *args, 'app-server', '--listen', 'stdio://', '--disable', 'apps',
                                '--disable', 'hooks', '--disable', 'plugins'], cwd=project,
                               env=dict(os.environ, HOME=str(home), CODEX_HOME=str(home / '.codex')),
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    waiting = b''
    def send(method, params=None, ident=None):
        row = {'method': method}
        if params is not None:
            row['params'] = params
        if ident is not None:
            row['id'] = ident
        process.stdin.write((json.dumps(row) + '\n').encode()); process.stdin.flush()
    def receive(ident):
        nonlocal waiting
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            while b'\n' in waiting:
                line, waiting = waiting.split(b'\n', 1)
                row = json.loads(line)
                if row.get('id') == ident:
                    require('error' not in row, 'Codex rejected native discovery')
                    return row['result']
            if not selector.select(max(.01, deadline - time.monotonic())):
                break
            content = os.read(process.stdout.fileno(), 65536)
            require(content, 'Codex discovery stopped before its receipt')
            waiting += content
            require(len(waiting) <= 16 * 1024 * 1024, 'Native discovery output exceeds bound')
        raise ValueError('Codex discovery timed out; verify the host and authentication')
    try:
        send('initialize', {'clientInfo': {'name': 'agent-system-buyer-setup', 'version': '1.0.0'}}, 1)
        receive(1); send('initialized')
        send('skills/list', {'cwds': [str(project)], 'forceReload': True}, 2)
        records = receive(2)
        actual = [s for row in records['data'] for s in row['skills']]
        names = set(engines(package)[0].NAMES) | {ORCHESTRATOR}
        rows = [s for s in actual if s['name'] in names]
        require(len(rows) == 34 and {s['name'] for s in rows} == names, 'Fresh Codex did not resolve one of each installed skill')
        for row in rows:
            require(row['enabled'] and safe(row['path']) == home / '.agents/skills' / row['name'] / 'SKILL.md',
                    'Codex resolved another source for ' + row['name'])
        receipt = {'status': 'native-discovery-verified', 'skills': len(rows), 'source_commit': plan['source_commit'],
                   'observed_paths': {row['name']: row['path'] for row in rows}, 'roles_explicitly_registered': 12,
                   'role_execution_verified': False, 'behavior_verified': False,
                   'next': 'Use the generated Codex launcher and ask Atelier Orchestrator for your first bounded task.'}
        write(operation / 'native-discovery.json', receipt)
        return receipt
    finally:
        selector.close()
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=3)


def first_task(locale='en'):
    prompt = ('Виправ Cheklist на Checklist лише в заголовку README.md. Збережи notes.txt. Прочитай обидва файли до і після правки; покажи результат і перевірку.'
              if locale == 'uk' else
              'Correct Cheklist to Checklist only in the README.md heading. Preserve notes.txt. Read both files before and after the edit; show the result and verification.')
    return {'status': 'ready-to-run', 'prompt': '$atelier-orchestrator\n\n' + prompt,
            'fixture': {'README.md': '# Cheklist\n', 'notes.txt': 'Preserve this note.\n'},
            'expected': {'README.md': '# Checklist\n', 'notes.txt': 'Preserve this note.\n'},
            'next': 'Create these two files in a disposable project; open the generated Codex launcher there and paste the prompt.',
            'execution_performed': False}


def wizard(package, home, state=None, codex=None, locale='en'):
    """Human entry for the double-click launcher; exact CLI plans stay available."""
    require(sys.stdin.isatty(), 'Run setup with a command such as doctor or audit, or open Start.command in a terminal for the guided menu.')
    home, state, *_ = paths(home, state)
    uk = locale == 'uk'
    say = lambda en, ua: print(ua if uk else en)
    say('Codex Agent System — guided setup', 'Codex Agent System — майстер встановлення')
    say('33 skills + Atelier Orchestrator + profile and 12 roles. Your projects and other skills stay in place.',
        '33 навички + Atelier Orchestrator + профіль і 12 ролей. Ваші проєкти та інші навички зберігаються.')
    say('1 Check prerequisites\n2 Install or update\n3 Verify installed files and fresh discovery\n4 Resume interrupted install\n5 Roll back the latest installation\n6 Uninstall managed files\n7 Show the first task\n0 Exit',
        '1 Перевірити передумови\n2 Встановити або оновити\n3 Перевірити файли й виявлення у свіжому Codex\n4 Продовжити перерване встановлення\n5 Відкотити останнє встановлення\n6 Видалити керовані файли\n7 Показати першу задачу\n0 Вийти')
    choice = input('Оберіть дію: ' if uk else 'Choose an action: ').strip()
    if choice == '0':
        return {'status': 'cancelled', 'next': 'Keep this package for setup or recovery.'}
    if choice == '1':
        return doctor(package, home, state, codex)
    if choice == '7':
        return first_task(locale)
    if choice == '2':
        diagnostic = doctor(package, home, state, codex)
        print(encoded(diagnostic).decode())
        require(diagnostic['platform']['supported_skills'], 'This computer is not in the supported skills platform set')
        say('The package can be installed offline. Sign in to your own Codex account before the first model task.',
            'Пакет можна встановити офлайн. Перед першою задачею увійдіть у власний обліковий запис Codex.')
        planfile = state / 'plans' / (uuid.uuid4().hex + '.json')
        reviewed = audit(package, home, state, planfile)
        print(encoded(reviewed).decode())
        require(reviewed['status'] == 'ready', 'Resolve the audit conflicts before installation')
        token = 'ВСТАНОВИТИ' if uk else 'INSTALL'
        say('Review the targets and exact plan shown above. Type INSTALL to apply that plan, or press Enter to stop.',
            'Перегляньте цільові шляхи й точний план вище. Введіть ВСТАНОВИТИ, щоб застосувати саме його, або Enter для виходу.')
        if input('> ').strip() != token:
            return {'status': 'not-applied', 'plan': str(planfile), 'next': 'The audit is retained. Apply its exact SHA-256 when ready.'}
        return install(planfile, reviewed['plan_sha256'])
    if choice == '4':
        candidates = []
        folder = state / 'operations'
        entries = sorted(folder.glob('*/journal.json')) if folder.exists() else []
        require(len(entries) <= 2000, 'Too many retained operations; select the exact journal in CLI recovery')
        for path in entries:
            record = load(path)
            if record.get('status') in ('interrupted', 'installing'):
                candidates.append((path, record))
        require(candidates, 'No interrupted buyer installation found. Use the exact journal if you kept state elsewhere.')
        for number, (path, row) in enumerate(candidates, 1):
            print(str(number) + '. ' + str(path) + ' — ' + row['created_at'])
        selection = input('Номер журналу: ' if uk else 'Journal number: ').strip()
        require(selection.isdigit() and 1 <= int(selection) <= len(candidates), 'Choose one exact retained journal')
        journal_path, row = candidates[int(selection)-1]
        checked_journal(journal_path)
        say('Resume this original plan? Type RESUME.', 'Продовжити початковий план? Введіть RESUME.')
        if input('> ').strip() != 'RESUME':
            return {'status': 'not-applied', 'journal': str(journal_path)}
        return install(Path(row['plan']), row['plan_sha256'], resume=journal_path)
    latest = state / 'installed.json'
    require(latest.exists(), 'No completed buyer installation here. Use install, or select your exact journal in the CLI.')
    journal = Path(load(latest)['journal'])
    if choice == '3':
        result = verify(journal)
        try:
            result['native_discovery'] = discover(journal, codex, home)
        except Exception as exc:
            result['native_discovery'] = {'status': 'unverified', 'reason': str(exc),
                                           'next': 'Open a fresh Codex with the generated launcher, then check the skill picker.'}
        return result
    if choice in ('5', '6'):
        say('Review the exact journal before continuing: ' + str(journal),
            'Перегляньте точний журнал перед продовженням: ' + str(journal))
        token = 'ROLLBACK' if choice == '5' else 'UNINSTALL'
        say('Type ' + token + ' to continue. Later unknown edits will block this operation.',
            'Введіть ' + token + ' для продовження. Пізніші невідомі зміни заблокують цю дію.')
        if input('> ').strip() != token:
            return {'status': 'not-applied', 'journal': str(journal)}
        return rollback(journal) if choice == '5' else uninstall(journal)
    raise ValueError('Choose one of the menu numbers')


def main(argv=None):
    if sys.version_info < (3, 9):
        print(json.dumps({'status': 'blocked', 'reason': 'Python 3.9 or later is required for buyer setup.',
                          'next': 'Install a supported Python from python.org, then reopen Start.command.'}), file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--state', type=Path)
    parser.add_argument('--locale', choices=('en', 'uk'), default='en')
    parser.add_argument('--codex', help='Actual supported Codex CLI path')
    parser.add_argument('--json', action='store_true', help='Machine-readable output; human summary otherwise')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('doctor')
    sub.add_parser('status')
    sub.add_parser('first-task')
    p = sub.add_parser('audit'); p.add_argument('--plan', type=Path, required=True); p.add_argument('--entitlement', type=Path)
    p = sub.add_parser('install'); p.add_argument('--plan', type=Path, required=True); p.add_argument('--approve', required=True); p.add_argument('--resume', type=Path)
    for name in ('verify', 'rollback', 'uninstall', 'discover'):
        p = sub.add_parser(name); p.add_argument('--journal', type=Path, required=True)
        if name == 'discover':
            p.add_argument('--cwd', type=Path)
    args = parser.parse_args(argv)
    try:
        package = safe(args.package.expanduser().resolve())
        if args.command is None:
            result = wizard(package, args.home, args.state, args.codex, args.locale)
        elif args.command == 'doctor':
            result = doctor(package, args.home, args.state, args.codex)
        elif args.command == 'audit':
            home, state, *_ = paths(args.home, args.state)
            result = audit(package, home, state, args.plan.expanduser().resolve(), args.entitlement)
        elif args.command == 'install':
            result = install(args.plan.expanduser().resolve(), args.approve, resume=args.resume)
        elif args.command == 'verify':
            result = verify(args.journal.expanduser().resolve())
        elif args.command == 'rollback':
            result = rollback(args.journal.expanduser().resolve())
        elif args.command == 'uninstall':
            result = uninstall(args.journal.expanduser().resolve())
        elif args.command == 'discover':
            result = discover(args.journal.expanduser().resolve(), args.codex, args.cwd)
        elif args.command == 'first-task':
            result = first_task(args.locale)
        else:
            result = status(args.home, args.state)
        if args.json:
            print(encoded(result).decode(), end='')
        else:
            title = 'Стан' if args.locale == 'uk' else 'Status'
            print(title + ': ' + str(result['status']))
            if 'next' in result:
                print(('Наступна дія: ' if args.locale == 'uk' else 'Next: ') + result['next'])
            print(encoded(result).decode(), end='')
        return 2 if result['status'] in ('blocked', 'action-required') else 0
    except Exception as exc:
        message = {'status': 'blocked', 'reason': str(exc),
                   'next': 'Keep the original package, plan and journal. Resolve the reported mismatch before retrying.'}
        print(encoded(message).decode(), end='', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
