#!/usr/bin/env python3
"""Audit, install, verify or roll back the exact personal Atelier skill suite.

Python 3.9+, standard library only. No network, shell commands, configuration,
AGENTS.md, plugins or product data are touched. Requires exclusive control of
the chosen source/target ancestor directories; not a sandbox against a hostile
same-user process changing ancestors between checks.
"""
import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import sys
import unicodedata
import uuid



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

NAMES = frozenset({
    'agent-foundry', 'design-specialist-skills',
    'gamedev-director', 'gamedev-studio', 'gamedev-concepts',
    'gamedev-preproduction', 'gamedev-assets', 'gamedev-build',
    'gamedev-qa', 'gamedev-release', 'gamedev-liveops',
    'app-atelier-director', 'app-atelier-research', 'app-atelier-concepts',
    'app-atelier-specification', 'app-atelier-experience', 'app-atelier-build',
    'app-atelier-support', 'app-atelier-qa', 'app-atelier-release',
    'app-atelier-growth', 'app-atelier-operations',
    'chatbot-atelier-director', 'chatbot-atelier-research',
    'chatbot-atelier-specification', 'chatbot-atelier-conversation',
    'chatbot-atelier-knowledge', 'chatbot-atelier-integrations',
    'chatbot-atelier-media', 'chatbot-atelier-build', 'chatbot-atelier-qa',
    'chatbot-atelier-release', 'chatbot-atelier-operations',
})
HEX = re.compile(r'^[0-9a-f]{64}$')
MAX_FILE = 64 * 1024 * 1024
MAX_KIT = 500 * 1024 * 1024
VISUAL_POLICY = 'preserve-existing/v1'
UI_PATH = 'agents/openai.yaml'
VISUAL_KEYS = frozenset({'icon_small', 'icon_large', 'brand_color'})
IMAGE_SUFFIXES = frozenset({'.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico'})


class SuiteError(Exception):
    pass


def require(ok, message):
    if not ok:
        raise SuiteError(message)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_path(value):
    path = Path(os.path.abspath(os.fspath(value)))
    for part in reversed((path,) + tuple(path.parents)):
        try:
            mode = part.lstat().st_mode
        except FileNotFoundError:
            continue
        require(not platform_support.is_link_or_reparse(part), 'Symlink/reparse point is not permitted: ' + str(part))
        if part != path:
            require(stat.S_ISDIR(mode), 'Non-directory ancestor: ' + str(part))
    return path


def read_bytes(path, limit=MAX_FILE):
    path = safe_path(path)
    observed = path.lstat()
    require(stat.S_ISREG(observed.st_mode), 'Expected regular file: ' + str(path))
    require(observed.st_size <= limit, 'File exceeds bounded input size: ' + str(path))
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        state = os.fstat(fd)
        require(stat.S_ISREG(state.st_mode), 'File type changed: ' + str(path))
        require(state.st_size <= limit, 'File exceeds bounded input size: ' + str(path))
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        require(len(data) <= limit, 'File grew beyond size limit: ' + str(path))
        return data
    finally:
        os.close(fd)


def read_json(path):
    try:
        return strict_json_loads(read_bytes(path, 16 * 1024 * 1024).decode('utf-8'))
    except (ValueError, UnicodeError) as error:
        raise SuiteError('Invalid UTF-8 JSON: ' + str(path)) from error


def atomic_json(path, value, exclusive=False):
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not exclusive or not path.exists(), 'Output already exists: ' + str(path))
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('xb') as stream:
            platform_support.fchmod(stream.fileno(), 0o600)
            stream.write(encode(value)); stream.flush(); os.fsync(stream.fileno())
        require(not exclusive or not path.exists(), 'Output appeared: ' + str(path))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def relative_file(value):
    require(isinstance(value, str) and value and '\\' not in value and '\x00' not in value,
            'Invalid manifest file path')
    try:
        platform_support.safe_relative(value)
    except ValueError as error:
        raise SuiteError(str(error)) from error
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(x not in ('', '.', '..') for x in value.split('/')),
            'Unsafe manifest path: ' + value)
    require(all(not x.endswith((' ', '.')) and ':' not in x for x in path.parts),
            'Nonportable manifest path: ' + value)
    require('.git' not in path.parts and '__pycache__' not in path.parts and path.name != '.DS_Store',
            'Cache/Git content is not allowed in kit: ' + value)
    return value


def volatile(relative):
    parts = PurePosixPath(relative).parts
    return '__pycache__' in parts or parts[-1] == '.DS_Store'


def mode_of(path):
    mode = path.lstat().st_mode
    require(not mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX),
            'Special permission bits are not supported: ' + str(path))
    return platform_support.file_mode(path)


def logical_sha(files):
    text = ''.join(k + '\0' + files[k]['sha256'] + '\n' for k in sorted(files) if not volatile(k))
    return sha(text.encode('utf-8'))


def snapshot(root):
    root = safe_path(root)
    if not root.exists():
        return None
    require(root.is_dir(), 'Expected skill directory: ' + str(root))
    files, directories = {}, {'.': mode_of(root)}
    for current, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(current) / name
            mode = p.lstat().st_mode
            require(not platform_support.is_link_or_reparse(p) and (stat.S_ISREG(mode) or stat.S_ISDIR(mode)),
                    'Link or special file in tree: ' + str(p))
        for name in dirs:
            p = Path(current) / name
            directories[p.relative_to(root).as_posix()] = mode_of(p)
        for name in names:
            p = Path(current) / name
            data = read_bytes(p)
            files[p.relative_to(root).as_posix()] = {'sha256': sha(data), 'size': len(data), 'mode': mode_of(p)}
    return {'files': files, 'directories': directories, 'tree_sha256': logical_sha(files)}


def declared_name(root):
    text = read_bytes(root / 'SKILL.md', 4 * 1024 * 1024).decode('utf-8').lstrip('\ufeff').replace('\r\n', '\n')
    require(text.startswith('---\n') and '\n---\n' in text, 'Missing frontmatter: ' + str(root))
    header, body = text[4:].split('\n---\n', 1)
    found = re.findall(r'^name:[ \t]*([^\n]+)$', header, re.M)
    require(len(found) == 1 and body.strip(), 'Ambiguous name or empty body: ' + str(root))
    name = found[0].strip().strip('\"\'')
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) is not None, 'Invalid declared name: ' + str(root))
    return name


def visual_yaml(text):
    """Read only three single-line interface scalars; never interpret general YAML.

    The rest of the YAML is compared literally with an approved baseline. A
    formatting-only change elsewhere can therefore require reconciliation, but
    cannot accidentally become permission to alter policy/dependencies/prompts.
    """
    require(isinstance(text, str), 'Visual YAML must be UTF-8 text')
    lines = text.lstrip('\ufeff').replace('\r\n', '\n').splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if re.fullmatch(r'interface:[ \t]*\n?', line)]
    require(len(starts) == 1, 'Expected exactly one plain interface mapping for icon preservation')
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith((' ', '#', '\n'))), len(lines))
    child_indent = min((len(line) - len(line.lstrip(' ')) for line in lines[start + 1:end]
                        if line.strip() and not line.lstrip().startswith('#')), default=2)
    require(child_indent > 0, 'Invalid interface indentation')
    fields, remove = {}, set()
    for i in range(start + 1, end):
        match = re.fullmatch(r' {' + str(child_indent) + r'}(icon_small|icon_large|brand_color):[ \t]*(.*?)\n?', lines[i])
        if not match:
            require(re.match(r' {' + str(child_indent) + r'}[\"\']?(icon_small|icon_large|brand_color)[\"\']?[ \t]*:', lines[i]) is None,
                    'Unsupported visual field syntax; reconcile YAML before updating')
            continue
        key, raw = match.groups()
        require(key not in fields, 'Duplicate visual interface field: ' + key)
        if raw.startswith('"'):
            try:
                value = strict_json_loads(raw)
            except ValueError as error:
                raise SuiteError('Unsupported visual YAML scalar: ' + key) from error
        elif raw.startswith("'"):
            require(raw.endswith("'") and len(raw) >= 2, 'Unsupported visual YAML scalar: ' + key)
            value = raw[1:-1].replace("''", "'")
        else:
            value = raw
        require(isinstance(value, str) and value and '\n' not in value and '\r' not in value,
                'Visual interface scalar must be a nonempty single-line string: ' + key)
        if key == 'brand_color':
            require(re.fullmatch(r'#[0-9a-fA-F]{6}', value) is not None, 'Invalid brand_color')
        else:
            icon_path(value)
        fields[key] = value
        remove.add(i)
    normalized = ''.join(line for i, line in enumerate(lines) if i not in remove)
    return fields, normalized, lines, start, end, child_indent, remove


def icon_path(value):
    """Normalize one historical ./ prefix for lookup, retaining the raw UI value."""
    relative = value[2:] if value.startswith('./') else value
    relative_file(relative)
    require(PurePosixPath(relative).parts[0] == 'assets'
            and PurePosixPath(relative).suffix.lower() in IMAGE_SUFFIXES,
            'Icons must be image files under assets/: ' + value)
    return relative


def merge_visual_yaml(canonical, fields):
    current, _, lines, start, end, indent, remove = visual_yaml(canonical)
    if current == fields:
        return canonical
    additions = [(' ' * indent) + key + ': ' + json.dumps(fields[key], ensure_ascii=False) + '\n'
                 for key in ('icon_small', 'icon_large', 'brand_color') if key in fields]
    # End of the interface block is stable even when all visual fields vanish.
    return ''.join(line for i, line in enumerate(lines[:end]) if i not in remove) + ''.join(additions) + ''.join(lines[end:])


def visual_assets(fields, state):
    files = {}
    for key in ('icon_small', 'icon_large'):
        if key not in fields:
            continue
        relative = icon_path(fields[key])
        require(relative in state['files'], 'Referenced icon is missing: ' + relative)
        files[relative] = state['files'][relative]
    return files


def content_records(files, excluded=()):
    return {k: {'sha256': v['sha256'], 'size': v['size']}
            for k, v in files.items() if not volatile(k) and k not in excluded}


def recognized_with_visual(row, state, ui_text):
    """Recognize icon-only drift against explicit byte-bound baselines."""
    if state is None or ui_text is None or UI_PATH not in state['files']:
        return False
    require(sha(ui_text.encode('utf-8')) == state['files'][UI_PATH]['sha256'], 'Predecessor UI text binding mismatch')
    fields, normalized, *_ = visual_yaml(ui_text)
    local_icons = set(visual_assets(fields, state))
    baselines = [{'files': row['files'], 'ui_yaml': row.get('_canonical_ui_yaml')}]
    baselines += [x for x in row.get('previous_trees', []) if 'files' in x]
    nonvisual = set()
    for baseline in baselines:
        if isinstance(baseline.get('ui_yaml'), str):
            baseline_fields, *_ = visual_yaml(baseline['ui_yaml'])
            baseline_icons = set(visual_assets(baseline_fields, {'files': baseline['files']}))
            nonvisual.update(set(baseline['files']) - baseline_icons)
    if local_icons & nonvisual:
        return False  # A different approved revision must not weaken this guard.
    for baseline in baselines:
        if not isinstance(baseline.get('ui_yaml'), str):
            continue
        old_fields, old_normalized, *_ = visual_yaml(baseline['ui_yaml'])
        old_icons = set(visual_assets(old_fields, {'files': baseline['files']}))
        if any(p in baseline['files'] and p not in old_icons for p in local_icons):
            continue  # An icon pointer cannot hide drift in another baseline file.
        excluded = {UI_PATH} | local_icons | old_icons
        if normalized == old_normalized and content_records(state['files'], excluded) == content_records(baseline['files'], excluded):
            return True
    return False


def make_visual_overlay(row, state, ui_text, enabled):
    if not enabled or state is None or UI_PATH not in state['files']:
        return None
    require(isinstance(ui_text, str) and sha(ui_text.encode('utf-8')) == state['files'][UI_PATH]['sha256'],
            'Predecessor UI text binding mismatch')
    require(row.get('_canonical_ui_yaml') is not None, 'Canonical UI is required to preserve existing icons')
    fields, *_ = visual_yaml(ui_text)
    assets = visual_assets(fields, state)
    canonical_fields, *_ = visual_yaml(row['_canonical_ui_yaml'])
    canonical_icons = set(visual_assets(canonical_fields, {'files': row['files']}))
    require(not any(p in row['files'] and p not in canonical_icons for p in assets),
            'Preserved icon collides with a nonvisual kit file')
    effective_ui = merge_visual_yaml(row['_canonical_ui_yaml'], fields)
    return {'schema_version': 'atelier.visual-overlay/1', 'original_ui_yaml': ui_text,
            'interface': fields, 'files': assets, 'effective_ui_yaml': effective_ui}


def effective_files(row, overlay):
    result = dict(row['files'])
    if overlay is not None:
        result.update(overlay['files'])
        data = overlay['effective_ui_yaml'].encode('utf-8')
        result[UI_PATH] = dict(row['files'][UI_PATH], sha256=sha(data), size=len(data))
    folded = set()
    for relative in result:
        relative_file(relative)
        value = unicodedata.normalize('NFC', relative).casefold()
        require(value not in folded, 'Preserved icon creates a case/Unicode path collision')
        folded.add(value)
    require(not any(str(parent) in folded for p in folded for parent in PurePosixPath(p).parents if str(parent) != '.'),
            'Preserved icon creates a file/directory path collision')
    return result


def read_kit(kit):
    kit = safe_path(kit)
    raw = read_bytes(kit / 'manifest.json', 16 * 1024 * 1024)
    manifest = strict_json_loads(raw.decode('utf-8'))
    require(isinstance(manifest, dict) and manifest.get('schema_version') == 'atelier.skill-suite/1', 'Unsupported suite manifest')
    require(isinstance(manifest.get('suite_id'), str) and manifest['suite_id'].strip(), 'suite_id is required')
    require(manifest.get('visual_identity_policy') in (None, VISUAL_POLICY), 'Unsupported visual identity policy')
    rows = manifest.get('skills')
    require(isinstance(rows, list) and len(rows) == len(NAMES), 'Manifest must contain exact 33-skill suite')
    result, total = {}, 0
    for row in rows:
        require(isinstance(row, dict), 'Each manifest skill must be an object')
        name = row.get('name')
        require(name in NAMES and name not in result, 'Unexpected or duplicate suite skill: ' + str(name))
        require(isinstance(row.get('version'), str) and row['version'].strip(), 'Skill version is required')
        files = row.get('files')
        require(isinstance(files, dict) and 'SKILL.md' in files, 'Hashed skill files are required: ' + name)
        folded = {}
        for relative, record in files.items():
            relative_file(relative)
            folded_path = unicodedata.normalize('NFC', relative).casefold()
            require(folded_path not in folded, 'Case/Unicode path collision: ' + name + '/' + relative)
            folded[folded_path] = relative
            require(isinstance(record, dict) and HEX.fullmatch(str(record.get('sha256', ''))), 'Invalid file hash')
            require(type(record.get('size')) is int and 0 <= record['size'] <= MAX_FILE, 'Invalid file size')
            require(type(record.get('mode')) is int and 0 <= record['mode'] <= 0o777, 'Invalid file mode')
            total += record['size']
        for path in folded:
            require(not any(parent in folded for parent in (str(x) for x in PurePosixPath(path).parents) if parent != '.'),
                    'File/directory path collision: ' + name + '/' + path)
        require(total <= MAX_KIT, 'Suite exceeds bounded total size')
        source = kit / 'skills' / name
        actual = snapshot(source)
        # ZIP extraction tools differ in whether they restore POSIX permission
        # bits. Source bytes/paths must match; declared target modes are applied
        # explicitly when installing and verified on the target.
        content = lambda rows: {k: {'sha256': v['sha256'], 'size': v['size']} for k, v in rows.items()}
        require(actual is not None and content(actual['files']) == content(files), 'Kit source differs from manifest: ' + name)
        require(declared_name(source) == name, 'Declared source name mismatch: ' + name)
        previous = row.get('previous_trees', [])
        require(isinstance(previous, list), 'previous_trees must be a list')
        for old in previous:
            require(isinstance(old, dict) and HEX.fullmatch(str(old.get('tree_sha256', '')))
                    and isinstance(old.get('source'), str) and old['source'].strip(), 'Invalid previous tree binding')
            if 'files' in old or 'ui_yaml' in old:
                require(isinstance(old.get('files'), dict) and isinstance(old.get('ui_yaml'), str)
                        and UI_PATH in old['files'], 'Visual predecessor requires files and exact ui_yaml')
                for relative, record in old['files'].items():
                    relative_file(relative)
                    require(isinstance(record, dict) and HEX.fullmatch(str(record.get('sha256', '')))
                            and type(record.get('size')) is int and 0 <= record['size'] <= MAX_FILE
                            and type(record.get('mode')) is int and 0 <= record['mode'] <= 0o777,
                            'Invalid visual predecessor file record')
                require(logical_sha(old['files']) == old['tree_sha256'], 'Visual predecessor tree binding mismatch')
                ui_bytes = old['ui_yaml'].encode('utf-8')
                require(len(ui_bytes) == old['files'][UI_PATH]['size']
                        and sha(ui_bytes) == old['files'][UI_PATH]['sha256'], 'Visual predecessor YAML hash mismatch')
                old_fields, *_ = visual_yaml(old['ui_yaml'])
                visual_assets(old_fields, {'files': old['files']})
        ui_text = read_bytes(source / UI_PATH).decode('utf-8') if UI_PATH in files else None
        if manifest.get('visual_identity_policy') == VISUAL_POLICY:
            require(ui_text is not None, 'Visual preservation requires canonical agents/openai.yaml')
            ui_fields, *_ = visual_yaml(ui_text)
            visual_assets(ui_fields, {'files': files})
        result[name] = dict(row, tree_sha256=logical_sha(files), _canonical_ui_yaml=ui_text)
    require(set(result) == NAMES, 'Suite skill allowlist mismatch')
    root = safe_path(kit / 'skills')
    require(set(x.name for x in root.iterdir()) == NAMES, 'Unexpected entry in kit skills directory')
    return kit, sha(raw), manifest, result


def is_under(path, parent):
    return path == parent or parent in path.parents


def roots(destination, legacy_root, backup_root, projects):
    destination, legacy_root, backup_root = [safe_path(x) for x in (destination, legacy_root, backup_root)]
    require(destination.name == 'skills' and not {'.system', 'plugins', 'cache'} & set(destination.parts),
            'Destination must be a non-system skills directory')
    require(destination != legacy_root and not is_under(destination, legacy_root) and not is_under(legacy_root, destination),
            'Personal skill roots must be distinct and non-nested')
    project_skill_roots = []
    for project in projects:
        project = safe_path(project)
        project_skill_roots.extend((project / '.agents/skills', project / '.codex/skills'))
    watched = [destination, legacy_root] + project_skill_roots
    require(not any(is_under(backup_root, p) or is_under(p, backup_root) for p in watched),
            'Backups must be outside all skill-discovery roots and their ancestors')
    return destination, legacy_root, backup_root, project_skill_roots


def discover(root, kind):
    root = safe_path(root)
    if not root.exists():
        return []
    require(root.is_dir(), 'Skill root is not a directory: ' + str(root))
    records = []
    for child in sorted(root.iterdir()):
        if child.name.startswith('.'):
            continue
        # Never follow an unknown directory symlink to discover its name.
        if platform_support.is_link_or_reparse(child):
            raise SuiteError('Uninspected symlink in skill-discovery root; reconcile independently: ' + str(child))
        if not child.is_dir() or not (child / 'SKILL.md').exists():
            continue
        try:
            name = declared_name(child)
        except (SuiteError, UnicodeError):
            if child.name in NAMES:
                raise
            continue
        if name in NAMES:
            records.append({'name': name, 'path': str(child), 'kind': kind, 'snapshot': snapshot(child)})
    return records


def known(row, state, ui_text=None, preserve_visual=False):
    exact = state is not None and state['tree_sha256'] in {row['tree_sha256']} | {x['tree_sha256'] for x in row.get('previous_trees', [])}
    return exact or (preserve_visual and recognized_with_visual(row, state, ui_text))


def files_match(actual, expected):
    # Keep canonical Git/ZIP modes in manifests/plans. Compare their explicit
    # native projection only on Windows, where NTFS has no executable bit.
    def projected(rows):
        return {k: dict(v, mode=platform_support.project_mode(v['mode'])) for k,v in rows.items()}
    return projected(actual) == projected(expected)


def desired_matches(row, state):
    return state is not None and files_match({k:v for k,v in state['files'].items() if not volatile(k)}, row['files'])


def audit(kit, destination, legacy_root, backup_root, projects=(), retire_known=False):
    kit, kit_hash, manifest, skills = read_kit(kit)
    destination, legacy_root, backup_root, project_roots = roots(destination, legacy_root, backup_root, projects)
    require(not any(is_under(kit, x) or is_under(x, kit) for x in [destination, legacy_root]), 'Kit must be separate from installation roots')
    discovered = discover(destination, 'destination') + discover(legacy_root, 'legacy')
    for p in project_roots:
        discovered += discover(p, 'project-report-only')
    entries, blockers = [], []
    preserve_visual = manifest.get('visual_identity_policy') == VISUAL_POLICY
    for name in sorted(NAMES):
        row = skills[name]
        target = destination / name
        before = snapshot(target)
        ui_text = read_bytes(target / UI_PATH).decode('utf-8') if before is not None and UI_PATH in before['files'] else None
        overlay = make_visual_overlay(row, before, ui_text, preserve_visual)
        desired = effective_files(row, overlay)
        if before is not None:
            try:
                correct = declared_name(target) == name
            except (SuiteError, UnicodeError, FileNotFoundError):
                correct = False
            if not correct:
                blockers.append('Target is unmanaged or has another declared name: ' + str(target))
            elif not known(row, before, ui_text, preserve_visual):
                blockers.append('Unrecognized target drift; preserve/reconcile source before updating: ' + str(target))
        action = 'noop' if desired_matches({'files': desired}, before) else 'install'
        entries.append({'name': name, 'action': action, 'target': str(target), 'before': before,
                        'desired_files': desired, 'desired_tree_sha256': logical_sha(desired),
                        'visual_preservation': overlay})
    for record in discovered:
        if record['path'] == str(destination / record['name']):
            continue
        source = Path(record['path'])
        duplicate_ui = read_bytes(source / UI_PATH).decode('utf-8') if UI_PATH in record['snapshot']['files'] else None
        if record['kind'] == 'project-report-only':
            blockers.append('Project duplicate is report-only; resolve explicitly in that project: ' + str(source))
        elif not retire_known:
            blockers.append('Duplicate requires explicit reviewed --retire-known-duplicates audit: ' + str(source))
        elif not known(skills[record['name']], record['snapshot'],
                       duplicate_ui,
                       preserve_visual):
            blockers.append('Duplicate has unknown source drift; cannot retire: ' + str(source))
        elif preserve_visual and duplicate_ui is not None and not duplicate_visual_matches(record, duplicate_ui, entries):
            blockers.append('Duplicate has a different visual identity; reconcile the canonical target before retirement: ' + str(source))
        else:
            entries.append({'name': record['name'], 'action': 'retire', 'target': str(source),
                            'before': record['snapshot'], 'predecessor_ui_yaml': duplicate_ui,
                            'desired_files': None, 'desired_tree_sha256': None})
    return {'schema_version': 'atelier.skill-suite-plan/1', 'created_at': now(), 'suite_id': manifest['suite_id'],
            'visual_identity_policy': manifest.get('visual_identity_policy'),
            'kit': str(kit), 'manifest_sha256': kit_hash, 'destination': str(destination), 'legacy_root': str(legacy_root),
            'backup_root': str(backup_root), 'projects': [str(safe_path(x)) for x in projects],
            'retire_known_duplicates': bool(retire_known), 'discovered': discovered, 'entries': entries,
            'blockers': blockers, 'ready': not blockers,
            'limits': 'Integrity and placement only; not runtime discovery, product acceptance or user-consent authentication.'}


def comparable(plan):
    return {k: v for k, v in plan.items() if k != 'created_at'}


def duplicate_visual_matches(record, ui_text, entries):
    candidate = next(x for x in entries if x['name'] == record['name'] and x['action'] != 'retire')
    overlay = candidate.get('visual_preservation')
    if overlay is None:
        return False  # Do not silently discard the only observed existing icon.
    fields, *_ = visual_yaml(ui_text)
    return fields == overlay['interface'] and visual_assets(fields, record['snapshot']) == overlay['files']


def load_plan(path):
    plan = read_json(path)
    require(isinstance(plan, dict) and plan.get('schema_version') == 'atelier.skill-suite-plan/1', 'Unsupported audit plan')
    require(plan.get('ready') is True and not plan.get('blockers'), 'Audit plan has blockers')
    fresh = audit(plan['kit'], plan['destination'], plan['legacy_root'], plan['backup_root'],
                  plan.get('projects', []), plan.get('retire_known_duplicates', False))
    require(comparable(fresh) == comparable(plan), 'Kit or observed installation changed after audit; create a fresh plan')
    return plan


def remove_tree(path):
    path = safe_path(path)
    if path.exists():
        snapshot(path)  # reject links/special files even in operation-owned staging
        shutil.rmtree(path)


def copy_tree(source, target, expected):
    source, target = safe_path(source), safe_path(target)
    require(not target.exists(), 'Copy target already exists: ' + str(target))
    shutil.copytree(source, target, symlinks=False, copy_function=shutil.copy2)
    require(snapshot(target) == expected, 'Backup/copy verification failed: ' + str(target))


def create_payload(kit, name, target, files):
    target = safe_path(target)
    if target.exists():
        remove_tree(target)
    target.mkdir(parents=True, mode=0o755)
    platform_support.set_mode(target, 0o755)
    for relative, record in sorted(files.items()):
        data = read_bytes(kit / 'skills' / name / relative)
        require(len(data) == record['size'] and sha(data) == record['sha256'], 'Kit changed during preparation: ' + name + '/' + relative)
        out = safe_path(target / relative)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('xb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        platform_support.set_mode(out, record['mode'])
    require(files_match(snapshot(target)['files'], files), 'Prepared skill differs from manifest: ' + name)


def create_preserved_payload(kit, row, target, entry, backup):
    """Preserve only audited image bytes from a fully verified private backup."""
    create_payload(kit, entry['name'], target, row['files'])
    overlay = entry['visual_preservation']
    require(snapshot(backup) == entry['before'], 'Visual preservation backup changed')
    for relative, record in overlay['files'].items():
        data = read_bytes(backup / relative)
        require(len(data) == record['size'] and sha(data) == record['sha256'], 'Preserved icon changed: ' + relative)
        output = safe_path(target / relative)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        platform_support.set_mode(output, record['mode'])
    output = safe_path(target / UI_PATH)
    with output.open('wb') as stream:
        stream.write(overlay['effective_ui_yaml'].encode('utf-8')); stream.flush(); os.fsync(stream.fileno())
    platform_support.set_mode(output, entry['desired_files'][UI_PATH]['mode'])
    require(files_match(snapshot(target)['files'], entry['desired_files']), 'Preserved payload differs from audited effective manifest')


def journal_paths(entry, operation, index):
    target = safe_path(entry['target'])
    stage = target.parent.parent / ('.skill-suite-' + operation.name) / str(index)
    return target, safe_path(operation / 'backup' / str(index)), safe_path(stage / 'new'), safe_path(stage / 'old')


def check_entry_roots(plan):
    destination, legacy, backup, project_roots = roots(plan['destination'], plan['legacy_root'], plan['backup_root'], plan.get('projects', []))
    require(isinstance(plan.get('entries'), list), 'Invalid plan entries')
    install_names, targets = [], set()
    for row in plan['entries']:
        require(isinstance(row, dict) and row.get('name') in NAMES, 'Unexpected journal skill')
        target = safe_path(row['target'])
        require(str(target) not in targets, 'Duplicate journal target'); targets.add(str(target))
        require(row.get('action') in ('noop', 'install', 'retire'), 'Unknown journal operation')
        if row['action'] in ('noop', 'install'):
            require(target == destination / row['name'], 'Noncanonical install target')
            install_names.append(row['name'])
        else:
            require(target.parent in (destination, legacy) and target.name not in ('.system', 'plugins'), 'Retirement outside personal roots')
    require(len(install_names) == len(NAMES) and set(install_names) == NAMES, 'Journal lost exact suite install scope')
    return destination, legacy, backup


def bind_plan_manifest(plan, manifest, skills):
    """Recovery still consumes the same exact manifest, not arbitrary plan paths."""
    require(plan.get('suite_id') == manifest['suite_id'], 'Plan suite differs from manifest')
    require(plan.get('visual_identity_policy') == manifest.get('visual_identity_policy'), 'Plan visual policy differs from manifest')
    check_entry_roots(plan)
    for entry in plan['entries']:
        row = skills[entry['name']]
        before = entry.get('before')
        overlay = entry.get('visual_preservation')
        ui_text = overlay.get('original_ui_yaml') if isinstance(overlay, dict) else entry.get('predecessor_ui_yaml')
        preserve_visual = manifest.get('visual_identity_policy') == VISUAL_POLICY
        if entry['action'] in ('noop', 'install'):
            expected_overlay = make_visual_overlay(row, before, ui_text, preserve_visual)
            require(overlay == expected_overlay, 'Plan visual overlay differs from byte-bound predecessor: ' + entry['name'])
            desired = effective_files(row, expected_overlay)
            require(entry.get('desired_files') == desired
                    and entry.get('desired_tree_sha256') == logical_sha(desired),
                    'Plan payload differs from manifest: ' + entry['name'])
        else:
            require(entry.get('desired_files') is None and entry.get('desired_tree_sha256') is None,
                    'Retirement must not contain a payload')
            require(overlay is None, 'Retirement must not contain a visual payload')
            if preserve_visual and ui_text is not None:
                require(duplicate_visual_matches({'name': entry['name'], 'snapshot': before}, ui_text, plan['entries']),
                        'Retirement would discard a different visual identity')
        if before is not None:
            require(isinstance(before, dict) and isinstance(before.get('files'), dict)
                    and before.get('tree_sha256') == logical_sha(before['files'])
                    and known(row, before, ui_text, preserve_visual),
                    'Plan predecessor is not bound to a known manifest source: ' + entry['name'])


def acquire_lock(backup_root, operation, plan_hash, resume=False):
    backup_root.mkdir(parents=True, exist_ok=True)
    lock = safe_path(backup_root / '.skill-suite.lock')
    if lock.exists():
        old = read_json(lock)
        require(resume and old.get('operation') == str(operation) and old.get('plan_sha256') == plan_hash,
                'Another update lock exists; inspect its journal, do not bypass it')
        require(old.get('hostname') == socket.gethostname() and type(old.get('pid')) is int, 'Cannot prove stale lock ownership on this host')
        try:
            alive = platform_support.process_alive(old['pid'])
        except OSError as error:
            raise SuiteError('Cannot establish lock process status') from error
        require(not alive, 'Update lock process is still alive')
        lock.unlink()
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        if platform_support.WINDOWS: platform_support.fchmod(fd, 0o600)
        data = encode({'operation': str(operation), 'plan_sha256': plan_hash, 'pid': os.getpid(), 'hostname': socket.gethostname()})
        os.write(fd, data); os.fsync(fd)
    finally:
        os.close(fd)
    return lock


def save_journal(operation, journal):
    atomic_json(operation / 'journal.json', journal)


def load_journal(path):
    path = safe_path(path)
    journal = read_json(path)
    require(isinstance(journal, dict) and journal.get('schema_version') == 'atelier.skill-suite-journal/1', 'Unsupported update journal')
    operation = safe_path(journal['operation'])
    require(path == operation / 'journal.json' and operation.name.startswith('run-'), 'Journal operation path mismatch')
    _, _, backup = check_entry_roots(journal['plan'])
    require(operation.parent == backup and operation.is_dir(), 'Journal outside recorded backup root')
    require(sha(encode(journal['plan'])) == journal['plan_sha256'], 'Journal plan integrity mismatch')
    require(isinstance(journal.get('states'), list) and len(journal['states']) == len(journal['plan']['entries']), 'Journal entry count mismatch')
    return operation, journal


def initial_journal(plan, operation):
    return {'schema_version': 'atelier.skill-suite-journal/1', 'operation': str(operation),
            'plan': plan, 'plan_sha256': sha(encode(plan)), 'status': 'starting', 'created_at': now(),
            'states': [{'phase': 'pending'} for _ in plan['entries']]}


def recover_orphan_initialization(plan_path, journal_path):
    """A crash before first journal write cannot have changed skill targets."""
    plan = load_plan(plan_path)  # All audited targets and kit must still match.
    journal_path = safe_path(journal_path)
    operation = journal_path.parent
    backup = safe_path(plan['backup_root'])
    require(journal_path.name == 'journal.json' and operation.parent == backup
            and re.fullmatch(r'run-[0-9a-f]{32}', operation.name), 'Invalid missing-journal recovery path')
    lock = read_json(backup / '.skill-suite.lock')
    require(lock.get('operation') == str(operation) and lock.get('plan_sha256') == sha(encode(plan)),
            'Missing journal has no matching initialization lock')
    if operation.exists():
        require(operation.is_dir(), 'Initialization operation is not a directory')
        for p in operation.iterdir():
            require(re.fullmatch(r'\.journal\.json\.[0-9a-f]{32}\.tmp', p.name)
                    and stat.S_ISREG(p.lstat().st_mode) and not platform_support.is_link_or_reparse(p),
                    'Missing journal has unexpected operation contents; reconcile manually')
    for root in (Path(plan['destination']), Path(plan['legacy_root'])):
        require(not (root.parent / ('.skill-suite-' + operation.name)).exists(),
                'Missing journal has staging data; reconcile manually')
    # acquire_lock still requires same-host, definitively dead PID below.
    return operation, initial_journal(plan, operation)


def apply_plan(path, resume=None):
    plan_path = safe_path(path)
    recovered_initialization = False
    if resume:
        if safe_path(resume).exists():
            operation, journal = load_journal(resume)
        else:
            operation, journal = recover_orphan_initialization(plan_path, resume)
            recovered_initialization = True
        plan = read_json(plan_path)
        require(encode(plan) == encode(journal['plan']), 'Resume plan differs from journal')
        require(plan.get('ready') is True and not plan.get('blockers'), 'Audit plan has blockers')
        require(journal.get('status') not in ('rolled_back', 'rollback_failed', 'rolling_back'), 'Cannot apply after rollback began')
        kit, kit_hash, manifest, skills = read_kit(plan['kit'])
        require(kit_hash == plan['manifest_sha256'], 'Kit manifest changed since audit')
        bind_plan_manifest(plan, manifest, skills)
    else:
        plan = read_json(plan_path)
        require(isinstance(plan, dict) and plan.get('schema_version') == 'atelier.skill-suite-plan/1', 'Unsupported audit plan')
        require(plan.get('ready') is True and not plan.get('blockers'), 'Audit plan has blockers')
        check_entry_roots(plan)
        kit, kit_hash, manifest, skills = read_kit(plan['kit'])
        require(kit_hash == plan['manifest_sha256'], 'Kit manifest changed since audit')
        bind_plan_manifest(plan, manifest, skills)
        backup_root = safe_path(plan['backup_root'])
        plan_hash = sha(encode(plan))
        consumed = backup_root / ('plan-' + plan_hash + '.json')
        if consumed.exists():
            prior = read_json(consumed)
            operation, journal = load_journal(prior['journal'])
            require(journal.get('status') == 'complete', 'Plan already started; use apply --resume JOURNAL')
            require(encode(journal['plan']) == encode(plan), 'Consumed plan differs from journal')
            require(all(snapshot(Path(x['target'])) == state.get('after') for x, state in zip(plan['entries'], journal['states'])),
                    'Previously applied plan has changed targets')
            return {'status': 'already_applied', 'journal': str(operation / 'journal.json'), 'changed': 0}
        plan = load_plan(plan_path)
        operation = backup_root / ('run-' + uuid.uuid4().hex)
        journal = initial_journal(plan, operation)
        kit = Path(plan['kit'])
    backup_root = Path(plan['backup_root'])
    lock = acquire_lock(backup_root, operation, journal['plan_sha256'], resume=bool(resume))
    try:
        if not resume or recovered_initialization:
            operation.mkdir(mode=0o700, exist_ok=recovered_initialization)
            if platform_support.WINDOWS: platform_support.make_private(operation)
            save_journal(operation, journal)
        consumed = backup_root / ('plan-' + journal['plan_sha256'] + '.json')
        if consumed.exists():
            require(read_json(consumed) == {'journal': str(operation / 'journal.json')}, 'Plan receipt belongs to another operation')
        else:
            atomic_json(consumed, {'journal': str(operation / 'journal.json')}, exclusive=True)
        journal['status'] = 'applying'; journal.pop('error', None); save_journal(operation, journal)
        changed = 0
        for index, (entry, state) in enumerate(zip(plan['entries'], journal['states'])):
            target, backup, prepared, old = journal_paths(entry, operation, index)
            before = entry['before']
            if state['phase'] == 'complete':
                require(snapshot(target) == state.get('after'), 'Completed target changed; cannot resume: ' + str(target))
                continue
            if entry['action'] == 'noop':
                require(snapshot(target) == before, 'No-op target changed: ' + str(target))
                state.update(phase='complete', after=before); save_journal(operation, journal); continue
            if state['phase'] == 'pending':
                require(snapshot(target) == before, 'Target changed before backup: ' + str(target))
                if before is not None:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    if backup.exists():
                        # With the original still exactly audited, an interrupted
                        # operation-owned backup copy can safely be rebuilt.
                        if snapshot(backup) != before:
                            remove_tree(backup)
                            copy_tree(target, backup, before)
                    else:
                        copy_tree(target, backup, before)
                state['phase'] = 'backed_up'; save_journal(operation, journal)
            if state['phase'] == 'backed_up':
                require(snapshot(target) == before, 'Target changed during backup: ' + str(target))
                prepared.parent.mkdir(parents=True, exist_ok=True)
                # Staging is outside skill discovery, but on target filesystem.
                if target.parent.exists():
                    require(os.stat(target.parent).st_dev == os.stat(prepared.parent).st_dev,
                            'Target and outside-discovery staging must share a filesystem')
                if entry['action'] == 'install':
                    if entry.get('visual_preservation') is not None:
                        create_preserved_payload(kit, skills[entry['name']], prepared, entry, backup)
                    else:
                        create_payload(kit, entry['name'], prepared, entry['desired_files'])
                    state['expected_after'] = snapshot(prepared)
                else:
                    state['expected_after'] = None
                state['phase'] = 'prepared'; save_journal(operation, journal)
            if state['phase'] == 'prepared':
                if old.exists():
                    require(snapshot(old) == before and not target.exists(), 'Ambiguous interrupted old-tree move')
                else:
                    require(snapshot(target) == before, 'Target changed before atomic replacement: ' + str(target))
                    if before is not None:
                        old.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(target, old)
                state['phase'] = 'old_moved'; save_journal(operation, journal)
            if state['phase'] == 'old_moved':
                if entry['action'] == 'install':
                    if target.exists():
                        require(not prepared.exists() and snapshot(target) == state['expected_after'], 'Ambiguous interrupted install')
                    else:
                        require(snapshot(prepared) == state['expected_after'], 'Prepared payload changed')
                        target.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(prepared, target)
                else:
                    require(not target.exists(), 'Retired target unexpectedly reappeared')
                state['phase'] = 'installed'; save_journal(operation, journal)
            if state['phase'] == 'installed':
                require(snapshot(target) == state['expected_after'], 'Installed target changed before commit')
                remove_tree(old)
                state.update(phase='complete', after=state['expected_after']); save_journal(operation, journal)
                changed += 1
        journal['status'] = 'complete'; journal['finished_at'] = now(); save_journal(operation, journal)
        return {'status': 'complete', 'journal': str(operation / 'journal.json'), 'changed': changed,
                'limits': 'Files installed; catalog refresh/discovery/behavior on the actual Codex host remains a separate check.'}
    except BaseException as error:
        journal['status'] = 'failed'; journal['error'] = str(error); save_journal(operation, journal)
        try:
            error.suite_journal = str(operation / 'journal.json')
        except AttributeError:
            pass
        raise
    finally:
        if lock.exists():
            lock.unlink()


def rollback(path):
    operation, journal = load_journal(path)
    require(journal.get('status') in ('complete', 'failed', 'applying', 'rolling_back', 'rollback_failed', 'rolled_back'), 'Journal is not rollbackable')
    if journal['status'] == 'rolled_back':
        return {'status': 'already_rolled_back', 'journal': str(path)}
    plan = journal['plan']
    lock = acquire_lock(Path(plan['backup_root']), operation, journal['plan_sha256'], resume=True)
    try:
        # Discover conflicts across the entire suite before changing any target.
        # Per-entry checks below still protect against later concurrent changes.
        for index, (entry, state) in enumerate(zip(plan['entries'], journal['states'])):
            target, backup, prepared, old = journal_paths(entry, operation, index)
            before, current = entry['before'], snapshot(target)
            if state.get('rollback') == 'complete' or current == before:
                require(current == before, 'Rolled-back target changed')
                continue
            after = state.get('after', state.get('expected_after'))
            discard = prepared.with_name('rollback-discard')
            require(current == after or (current is None and old.exists() and snapshot(old) == before)
                    or (current is None and discard.exists() and snapshot(discard) == after),
                    'Target changed after update; rollback would overwrite work: ' + str(target))
            if before is not None:
                require(snapshot(backup) == before, 'Backup integrity failure')
        journal['status'] = 'rolling_back'; save_journal(operation, journal)
        for index in reversed(range(len(plan['entries']))):
            entry, state = plan['entries'][index], journal['states'][index]
            target, backup, prepared, old = journal_paths(entry, operation, index)
            before = entry['before']
            if state.get('rollback') == 'complete':
                require(snapshot(target) == before, 'Rolled-back target changed')
                continue
            if state['phase'] in ('pending', 'backed_up'):
                require(snapshot(target) == before, 'Unchanged target drifted; rollback blocked')
                remove_tree(prepared)
                state['rollback'] = 'complete'; save_journal(operation, journal); continue
            current = snapshot(target)
            after = state.get('after', state.get('expected_after'))
            rollback_discard = prepared.with_name('rollback-discard')
            if current == before:
                # Includes crash after restoring original but before journal write.
                remove_tree(prepared); remove_tree(old); remove_tree(rollback_discard)
                state['rollback'] = 'complete'; save_journal(operation, journal); continue
            discard_pending = (current is None and rollback_discard.exists()
                               and snapshot(rollback_discard) == after)
            require(current == after or discard_pending or (current is None and old.exists() and snapshot(old) == before),
                    'Target changed after update; rollback would overwrite work: ' + str(target))
            if before is not None:
                require(snapshot(backup) == before, 'Backup integrity failure')
                restored = prepared.with_name('restore')
                if restored.exists():
                    if snapshot(restored) != before:
                        remove_tree(restored)
                        copy_tree(backup, restored, before)
                else:
                    restored.parent.mkdir(parents=True, exist_ok=True)
                    copy_tree(backup, restored, before)
            else:
                restored = None
            if target.exists():
                require(not rollback_discard.exists(), 'Interrupted rollback discard exists; inspect journal')
                os.replace(target, rollback_discard)
                state['rollback_discard'] = str(rollback_discard); save_journal(operation, journal)
            if restored is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(restored, target)
            require(snapshot(target) == before, 'Restored target differs from backup')
            remove_tree(prepared); remove_tree(old)
            remove_tree(rollback_discard)
            state['rollback'] = 'complete'; save_journal(operation, journal)
        journal['status'] = 'rolled_back'; journal['rollback_finished_at'] = now(); save_journal(operation, journal)
        return {'status': 'rolled_back', 'journal': str(path), 'restored_entries': len(plan['entries'])}
    except BaseException as error:
        journal['status'] = 'rollback_failed'; journal['error'] = str(error); save_journal(operation, journal)
        try:
            error.suite_journal = str(operation / 'journal.json')
        except AttributeError:
            pass
        raise
    finally:
        if lock.exists():lock.unlink()


def verify(kit, destination, legacy_root, journal_path=None):
    _, kit_hash, manifest, skills = read_kit(kit)
    destination = safe_path(destination)
    failures, core_failures, preserved = [], [], []
    receipt_entries = None
    if journal_path is not None:
        _, journal = load_journal(journal_path)
        require(journal.get('status') == 'complete', 'Visual continuity requires a completed apply journal')
        plan = journal['plan']
        require(plan.get('manifest_sha256') == kit_hash and Path(plan['destination']) == destination
                and safe_path(plan['legacy_root']) == safe_path(legacy_root), 'Verification journal belongs to another kit or destination')
        bind_plan_manifest(plan, manifest, skills)
        receipt_entries = {x['name']: x for x in plan['entries'] if x['action'] != 'retire'}
    for name, row in sorted(skills.items()):
        target = destination / name
        current = snapshot(target)
        core_matches = desired_matches(row, current)
        current_visual = None
        if manifest.get('visual_identity_policy') == VISUAL_POLICY and current is not None and UI_PATH in current['files']:
            ui_text = read_bytes(target / UI_PATH).decode('utf-8')
            try:
                current_visual = make_visual_overlay(row, current, ui_text, True)
                core_matches = desired_matches({'files': effective_files(row, current_visual)}, current)
            except SuiteError:
                core_matches = False
        if not core_matches:
            core_failures.append(name)
        expected = row['files'] if receipt_entries is None else receipt_entries[name]['desired_files']
        if not desired_matches({'files': expected}, current):
            reason = 'file/hash/mode mismatch or missing target'
            if receipt_entries is None and current_visual is not None:
                if core_matches:
                    reason = 'Custom visual identity requires exact apply --journal receipt to verify continuity'
            failures.append({'name': name, 'reason': reason})
        elif declared_name(target) != name:
            failures.append({'name': name, 'reason': 'declared name mismatch'})
        elif receipt_entries is not None and receipt_entries[name].get('visual_preservation') is not None:
            preserved.append(name)
    duplicate = [x for x in discover(destination, 'destination') + discover(safe_path(legacy_root), 'legacy')
                 if x['path'] != str(destination / x['name'])]
    return {'schema_version': 'atelier.skill-suite-verification/1', 'suite_id': manifest['suite_id'],
            'manifest_sha256': kit_hash, 'ready': not failures and not duplicate,
            'verified_skills': len(skills) - len(failures), 'failures': failures,
            'canonical_core_verified': not core_failures,
            'canonical_core_failures': core_failures,
            'visual_preservation_verified': receipt_entries is not None and not failures,
            'preserved_visual_identities': preserved,
            'visual_preservation_journal': str(safe_path(journal_path)) if journal_path is not None else None,
            'duplicates': [{'name': x['name'], 'path': x['path']} for x in duplicate],
            'runtime_discovery_verified': False, 'behavior_verified': False,
            'next': 'In the actual Codex host refresh the skill catalog or open a fresh session, resolve the 33 skills, then run the accepted bounded interaction scenarios.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('audit', 'verify'):
        p = sub.add_parser(command)
        p.add_argument('--kit', type=Path, required=True)
        p.add_argument('--destination', type=Path, default=Path.home() / '.agents/skills')
        p.add_argument('--legacy-root', type=Path, default=Path.home() / '.codex/skills')
        if command == 'audit':
            p.add_argument('--plan', type=Path)
            p.add_argument('--backup-root', type=Path, default=Path.home() / 'Codex_Skill_Backups')
            p.add_argument('--project-root', type=Path, action='append', default=[])
            p.add_argument('--retire-known-duplicates', action='store_true')
        else:
            p.add_argument('--journal', type=Path, help='Exact completed apply journal, required to prove custom-icon continuity')
    p = sub.add_parser('apply'); p.add_argument('--plan', type=Path, required=True); p.add_argument('--resume', type=Path)
    p = sub.add_parser('rollback'); p.add_argument('--journal', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'audit':
        result = audit(args.kit, args.destination, args.legacy_root, args.backup_root, args.project_root, args.retire_known_duplicates)
        if args.plan:
            # Plans/receipts are never written in skill discovery trees.
            plan_out = safe_path(args.plan)
            protected = [Path(result[x]) for x in ('destination', 'legacy_root')]
            for project in result['projects']:
                protected.extend((Path(project) / '.agents/skills', Path(project) / '.codex/skills'))
            require(not any(is_under(plan_out, p) for p in protected), 'Plan must be outside all skill-discovery roots')
            atomic_json(plan_out, result, exclusive=True)
        print(encode(result).decode(), end=''); return 0 if result['ready'] else 1
    if args.command == 'apply':result = apply_plan(args.plan, args.resume)
    elif args.command == 'rollback':result = rollback(args.journal)
    else:result = verify(args.kit, args.destination, args.legacy_root, args.journal)
    print(encode(result).decode(), end='')
    return 0 if result.get('ready', True) else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (SuiteError, OSError, ValueError, KeyError, TypeError) as error:
        result = {'error': str(error), 'completed': False}
        if getattr(error, 'suite_journal', None):
            result['journal'] = error.suite_journal
        print(encode(result).decode(), file=sys.stderr, end='')
        raise SystemExit(2)
