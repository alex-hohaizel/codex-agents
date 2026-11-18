#!/usr/bin/env python3
"""Exercise a received ready ZIP on its actual native OS/CPU, with private test data.

This is an acceptance harness, not an installer or a model benchmark. It never
uses the account's real HOME/CODEX_HOME, credentials, projects or running service.
The JSON receipt explicitly distinguishes package/controller behavior, native
Codex discovery, graphical interaction and model/provider execution.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

sys.dont_write_bytecode = True
PUBLISHED_PREDECESSOR = '6eda958692eda18d0c3727e6452a970b5058532e'
WINDOWS = os.name == 'nt'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf8')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def private_output(path):
    """Protect the native fixture before creating any inherited child DACLs."""
    path.mkdir(parents=True, mode=0o700)
    if WINDOWS:
        # Trusted test-harness source, independent of the as-yet-unread buyer ZIP.
        source = Path(__file__).with_name('platform_support.py')
        spec = importlib.util.spec_from_file_location('native_fixture_platform', source)
        boundary = importlib.util.module_from_spec(spec)
        exec(compile(source.read_bytes(), str(source), 'exec'), boundary.__dict__)
        boundary.make_private(path)


def extraction_directory_mode():
    # Python3.13 Windows mkdir0700 creates a protected OWNER/Administrators DACL.
    # Payload dirs inherit the already private current-SID root instead.
    # https://docs.python.org/3.13/library/os.html#os.mkdir
    return 0o755 if WINDOWS else 0o700


def without_setup_diagnostics(value):
    """Keep one result JSON while allowing only the engines' tagged JSON lines.

    The raw stream remains in the command receipt. Unknown/malformed stderr is
    retained so it cannot silently turn into an apparently valid result.
    """
    retained = []
    for line in value.splitlines():
        prefix = next((item for item in ('agent-system-setup ', 'agent-system-core ') if line.startswith(item)), None)
        if prefix:
            try:
                if isinstance(json.loads(line[len(prefix):]), dict):
                    continue
            except json.JSONDecodeError:
                pass
        retained.append(line)
    return '\n'.join(retained)


def native_target():
    machine = platform.machine().lower()
    arch = {'aarch64': 'arm64', 'arm64': 'arm64', 'amd64': 'x64', 'x86_64': 'x64'}.get(machine)
    require(sys.platform in ('darwin', 'linux', 'win32') and arch, 'Unsupported native runner')
    return sys.platform + '-' + arch


def extract(archive, destination):
    """Keep archive traversal, aliases and links out of the native test workspace."""
    directory_mode = extraction_directory_mode()
    destination.mkdir(mode=directory_mode)
    observed = set()
    total = 0
    with zipfile.ZipFile(archive) as package:
        require(len(package.infolist()) <= 65000, 'Ready archive member limit exceeded')
        for item in package.infolist():
            name = item.filename.rstrip('/')
            path = PurePosixPath(name)
            require(name and not path.is_absolute() and str(path) == name and '\\' not in name
                    and all(part not in ('.', '..') and ':' not in part and not re.search(r'[. ]$', part)
                            and not re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', part, re.I)
                            for part in path.parts), 'Unsafe ready archive member')
            require(name.casefold() not in observed, 'Duplicate/case-colliding archive member')
            observed.add(name.casefold())
            mode = (item.external_attr >> 16) & 0xffff
            require(not stat.S_ISLNK(mode) and (not stat.S_IFMT(mode) or stat.S_ISREG(mode) or stat.S_ISDIR(mode)),
                    'Linked or special ready archive member')
            target = destination.joinpath(*path.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True, mode=directory_mode)
                continue
            total += item.file_size
            require(item.file_size <= 256 * 1024 * 1024 and total <= 4 * 1024 * 1024 * 1024,
                    'Ready archive expands beyond its bound')
            target.parent.mkdir(parents=True, exist_ok=True, mode=directory_mode)
            with package.open(item) as source, target.open('xb') as output:
                shutil.copyfileobj(source, output, 128 * 1024)
            target.chmod(0o755 if mode & 0o111 else 0o644)
    candidates = [destination] if (destination / 'product-manifest.json').is_file() else [
        item for item in destination.iterdir() if item.is_dir() and (item / 'product-manifest.json').is_file()]
    require(len(candidates) == 1, 'One product package root is required')
    return candidates[0].resolve()


class Acceptance:
    def __init__(self, archive, output, codex=None):
        self.archive = archive.resolve()
        self.output = output.resolve()
        require(self.archive.is_file(), 'Ready archive is missing')
        require(not self.output.exists(), 'Choose a NEW private acceptance output directory')
        private_output(self.output)
        self.logs = self.output / 'commands'
        self.logs.mkdir(mode=0o700)
        self.target = native_target()
        self.codex = codex
        self.started = time.monotonic()
        self.counter = 0
        self.running = []
        self.service = None
        self.report = {
            'schema': 'codex-agents.native-ready-installer-acceptance/1',
            'status': 'running', 'archive': str(self.archive), 'archive_sha256': digest(self.archive),
            'native': {'target': self.target, 'system': platform.system(), 'machine': platform.machine(),
                       'release': platform.release(), 'harness_python': platform.python_version()},
            'checks': [], 'limitations': [
                'Only the OS/CPU recorded in this receipt is exercised by this run.',
                'Graphical browser interaction is covered by a separate GUI acceptance receipt.',
                'No paid model turn, provider operation, real purchase, signing or notarization is performed.',
                'Controller checks are bounded real local workflows, not whole-product quality certification.'],
        }
        self.save()

    def save(self):
        self.report['elapsed_seconds'] = round(time.monotonic() - self.started, 3)
        (self.output / 'native-acceptance.json').write_bytes(encoded(self.report))

    def record(self, name, details=None):
        self.report['checks'].append({'name': name, 'status': 'passed', 'details': details or {}})
        self.save()
        print(name + ': passed', flush=True)

    def run(self, name, argv, *, expected=(0,), parse=True, timeout=180, input=None):
        self.counter += 1
        start = time.monotonic()
        print('Native command '+str(self.counter)+': '+name+' started', flush=True)
        try:
            result = subprocess.run([str(value) for value in argv], env=self.env, cwd=self.home,
                                    capture_output=True, input=input, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            decode = lambda value: value.decode('utf8', errors='replace') if isinstance(value, bytes) else value or ''
            receipt = {'name': name, 'argv': [str(value) for value in argv], 'status': 'timeout', 'returncode': None,
                       'seconds': round(time.monotonic() - start, 3), 'timeout_seconds': timeout,
                       'stdout': decode(error.stdout), 'stderr': decode(error.stderr)}
            (self.logs / ('%03d-' % self.counter + re.sub(r'[^a-zA-Z0-9_-]', '-', name) + '.json')).write_bytes(encoded(receipt))
            raise
        receipt = {'name': name, 'argv': [str(value) for value in argv], 'returncode': result.returncode,
                   'seconds': round(time.monotonic() - start, 3),
                   'stdout': result.stdout.decode('utf8', errors='replace'),
                   'stderr': result.stderr.decode('utf8', errors='replace')}
        (self.logs / ('%03d-' % self.counter + re.sub(r'[^a-zA-Z0-9_-]', '-', name) + '.json')).write_bytes(encoded(receipt))
        require(result.returncode in expected, name + ' returned ' + str(result.returncode) + ': ' + receipt['stdout'][-1500:] + receipt['stderr'][-1500:])
        if not parse:
            return receipt
        content = receipt['stdout'].strip() or without_setup_diagnostics(receipt['stderr']).strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise AssertionError(name + ' did not return one JSON result: ' + content[-1500:]) from error

    def setup_argv(self, verb, *args):
        result = [self.python, '-I', '-X', 'utf8', '-B', self.package / 'setup/setup.py',
                  '--package', self.package, '--home', self.home, '--state', self.state, '--json']
        if self.codex:
            result += ['--codex', self.codex]
        return result + [verb, *args]

    def setup(self, verb, *args, **kwargs):
        return self.run('setup-' + verb, self.setup_argv(verb, *args), **kwargs)

    def control(self, verb, *args, **kwargs):
        return self.run('workbench-' + verb, [self.node, self.package / 'control.mjs', verb, *args], **kwargs)

    def prepare(self):
        start = time.monotonic()
        self.package = extract(self.archive, self.output / 'received package')
        manifest = load(self.package / 'product-manifest.json')
        require(manifest['schema'] == 'codex-agents.commercial-package/1', 'Wrong product schema')
        require(re.fullmatch('[0-9a-f]{40}', manifest['source_commit']), 'Exact source commit is absent')
        self.manifest = manifest
        self.initial_bytecode = {path.relative_to(self.package).as_posix(): digest(path) for path in self.package.rglob('*.pyc')}
        self.initial_cache_directories = {path.relative_to(self.package).as_posix() for path in self.package.rglob('__pycache__')}
        tools = manifest.get('portable_runtimes', {}).get(self.target)
        require(tools, 'Archive does not contain the native target')
        for key in ('node_executable', 'python_executable'):
            require(tools[key] in manifest['files'], 'Runtime is outside the received inventory')
        self.node = self.package / tools['node_executable']
        self.python = self.package / tools['python_executable']
        self.home = self.output / 'Покупець native & test HOME'
        self.home.mkdir(mode=0o700)
        self.skills_root = self.home / ('.codex/skills' if WINDOWS else '.agents/skills')
        self.state = self.home / '.local/share/codex-agent-system'
        # Explicitly isolated HOME/CODEX_HOME; preserve only host prerequisites.
        self.env = {(key.upper() if os.name == 'nt' else key): value for key, value in os.environ.items() if key.upper() in {
            'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TMP', 'TEMP', 'TMPDIR',
            'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'NODE_EXTRA_CA_CERTS'}}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), CODEX_HOME=str(self.home / '.codex'),
                        APPDATA=str(self.home / 'AppData/Roaming'), LOCALAPPDATA=str(self.home / 'AppData/Local'),
                        XDG_DATA_HOME=str(self.home / '.local/share'), XDG_CONFIG_HOME=str(self.home / '.config'),
                        AGENT_SYSTEM_PYTHON=str(self.python), AGENT_SYSTEM_NODE=str(self.node),
                        AGENT_SYSTEM_SETUP_DIAGNOSTICS='1',
                        PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        self.env['PATH'] = str(self.python.parent) + os.pathsep + str(self.node.parent) + os.pathsep + self.env.get('PATH', '')
        self.report.update(source_commit=manifest['source_commit'], source_clean=manifest.get('source_clean'),
                           product_version=manifest['product_version'], package_manifest_sha256=digest(self.package / 'product-manifest.json'))
        info = self.run('included-python-native', [self.python, '-I', '-X', 'utf8', '-B', '-c',
            'import json,platform,sys,sqlite3,yaml;print(json.dumps(dict(version=platform.python_version(),machine=platform.machine(),platform=sys.platform,executable=sys.executable,pyyaml=yaml.__version__,sqlite=sqlite3.sqlite_version)))'])
        node = self.run('included-node-native', [self.node, '-p', 'JSON.stringify({version:process.versions.node,platform:process.platform,arch:process.arch,executable:process.execPath})'])
        require(node['platform'] + '-' + node['arch'] == self.target, 'Node is not native to the runner')
        pyarch = {'aarch64': 'arm64', 'arm64': 'arm64', 'amd64': 'x64', 'x86_64': 'x64'}.get(info['machine'].lower())
        require(info['platform'] + '-' + str(pyarch) == self.target, 'Python is not native to the runner')
        runtime = load(self.package / 'runtimes' / self.target / 'runtime.json')
        require(info['version'] == runtime['python']['version'] and node['version'] == runtime['node']['version'], 'Included runtime version differs from its provenance')
        self.report['runtime'] = {'python': info, 'node': node, 'input_lock_sha256': runtime['input_lock_sha256']}
        privacy = self.package / 'setup/platform_support.py'
        for folder in (self.output, self.logs, self.home):
            self.run('protect-test-data', [self.python, '-I', '-X', 'utf8', '-B', privacy, '--make-private', folder])
        if os.name == 'nt':
            # Files created before the first native ACL call must lose any
            # permissive inherited ACE too; Windows traversal bypass means a
            # private parent alone does not repair an older child's DACL.
            for path in [self.output / 'native-acceptance.json', *self.logs.iterdir()]:
                self.run('protect-existing-test-output', [self.python, '-I', '-X', 'utf8', '-B', privacy, '--make-private', path])
            probe_output = self.output / 'windows-token-preflight'
            self.run('windows-restricted-token-preflight', [sys.executable, '-B',
                Path(__file__).with_name('native_windows_standard_user.py'), '--package', self.package,
                '--output', probe_output, '--python', self.python, '--identity-only', '--timeout-seconds', '30'], timeout=60)
            token = load(probe_output / 'STANDARD-USER-OBSERVATION.json')
            require(token['status']=='token-observed' and token['lifecycle_verified'] is False
                    and token['child']['is_user_an_admin'] is False
                    and token['source_commit']==manifest['source_commit']
                    and token['package_manifest_sha256']==self.report['package_manifest_sha256'],
                    'Windows token preflight did not prove the exact restricted identity')
            self.report['windows_token_preflight']={'status':'token-observed','lifecycle_verified':False,
                'scope':'Environment capability only; full installation and C03 acceptance remain separate mandatory checks.'}
            self.save()
        self.record('native-ready-archive-and-runtimes', {'extraction_seconds': round(time.monotonic() - start, 3), 'target': self.target})

    def seed(self):
        self.foreign = self.home / '.agents/skills/personal-notes/notes.txt'
        self.foreign.parent.mkdir(parents=True)
        self.foreign.write_text('Customer-owned notes — preserve these bytes.\n', encoding='utf8')
        self.project = self.home / 'Проєкт with spaces & Unicode'
        self.project.mkdir()
        self.project_file = self.project / 'accepted.md'
        self.project_file.write_text('Accepted customer project — unchanged.\n', encoding='utf8')
        self.profile = self.home / '.codex/AGENTS.md'
        self.profile.parent.mkdir(parents=True)
        self.profile.write_text('# Personal instructions\nPreserve my accepted projects.\n', encoding='utf8')
        self.role = self.home / '.codex/agents/foundry-qa.toml'
        self.role.parent.mkdir()
        self.role.write_bytes(b'model = "native-acceptance-local-choice"\n' + (self.package / 'product/agent-profiles/foundry-qa.toml').read_bytes())
        self.preserved = {str(path): digest(path) for path in (self.foreign, self.project_file, self.role)}
        self.personal_profile = self.profile.read_text(encoding='utf8')

    def bundled_linux_terminfo(self):
        if sys.platform != 'linux':
            return
        tools = self.manifest['portable_runtimes'][self.target]
        runtime = load(self.package / 'runtimes' / self.target / 'runtime.json')
        references = tools.get('terminfo_dirs', [])
        require(references and references == ['runtimes/' + self.target + '/' + name for name in runtime.get('terminfo_dirs', [])],
                'Linux runtime does not declare matching portable terminal database layers')
        directories = [str(self.package / name) for name in references]
        previous = self.env
        self.env = dict(previous, TERMINFO_DIRS=os.pathsep.join(directories))
        self.env.pop('TERMINFO', None)
        try:
            observed = []
            for terminal in ('Eterm', 'eterm', '2621A', '2621a', 'xterm', 'xterm-256color'):
                matching = [Path(directory) / terminal[0] / terminal for directory in directories
                            if (Path(directory) / terminal[0] / terminal).is_file()]
                require(len(matching) == 1, 'The original terminal name was lost or duplicated: ' + terminal)
                result = self.run('native-curses-' + terminal, [self.python, '-I', '-X', 'utf8', '-B', '-c',
                    'import curses,json,os,sys;assert os.environ["TERMINFO_DIRS"]==os.pathsep.join(sys.argv[2:]);'
                    'curses.setupterm(term=sys.argv[1],fd=1);cap=curses.tigetstr("cup");assert cap;'
                    'print(json.dumps(dict(terminal=sys.argv[1],columns=curses.tigetnum("cols"),cursor_address_hex=cap.hex(),terminfo_dirs=os.environ["TERMINFO_DIRS"])))',
                    terminal, *directories])
                observed.append({'terminal': terminal, 'file_sha256': digest(matching[0]), 'columns': result['columns'],
                                 'fresh_interpreter': True, 'cursor_address_hex': result['cursor_address_hex']})
            self.record('native-linux-curses-loads-original-case-sensitive-terminal-names',
                        {'only_bundled_dirs': references, 'probes': observed, 'system_fallback_in_probe': False})
        finally:
            self.env = previous

    def preserve(self, name, *, restored_profile=False):
        for path, expected in self.preserved.items():
            # Rollback restores the original tuned role; uninstall intentionally
            # removes managed roles, but customer project/foreign skills remain.
            if not Path(path).exists() and path == str(self.role) and name == 'uninstall-preserves-customer-work':
                continue
            require(digest(path) == expected, name + ': customer-owned bytes changed: ' + path)
        if restored_profile:
            require(self.profile.read_text(encoding='utf8') == self.personal_profile, 'Rollback did not restore exact personal instructions')
        else:
            require(self.personal_profile in self.profile.read_text(encoding='utf8'), 'Personal instructions were lost')
        self.record(name)

    def buyer_install(self):
        doctor = self.setup('doctor', expected=(0, 2))
        require(doctor['source_commit'] == self.manifest['source_commit'] and doctor['components']['skills']['ready_for_audit'], 'Doctor did not observe native supported skills')
        self.report['codex'] = {key: doctor['host'].get(key) for key in ('executable', 'version', 'authentication', 'ready')}
        if self.codex:
            require(doctor['host']['version'] == '0.166.0', 'Native acceptance requires the pinned supported Codex CLI0.166.0')
        self.plan = self.output / 'approved plan.json'
        audit = self.setup('audit', '--plan', self.plan)
        require(audit['status'] == 'ready' and audit['mode'] == 'fresh', 'Fresh audit was not ready')
        require(Path(audit['destination']) == self.skills_root,
                'Fresh audit did not select the documented native personal skill root')
        self.approval = audit['plan_sha256']
        self.journal = Path(audit['journal'])
        self.record('buyer-doctor-and-exact-audit', {'doctor_status': doctor['status'], 'plan_sha256': self.approval})
        self.real_writer_lock()
        self.interrupt_install()
        installed = self.setup('install', '--plan', self.plan, '--approve', self.approval, '--resume', self.journal)
        require(installed['status'] == 'installed' and installed['verification']['skills'] == 33, 'Resume did not install the full managed suite')
        repeated = self.setup('install', '--plan', self.plan, '--approve', self.approval)
        require(repeated['journal'] == installed['journal'], 'Repeated install created another installation')
        verified = self.setup('verify', '--journal', self.journal)
        require(verified['skills'] == 33 and verified['orchestrator'], 'Installed-file verification is incomplete')
        self.preserve('install-preserves-customer-work')
        self.record('install-resume-repeat-and-verify', {'skills': verified['skills'], 'orchestrator': verified['orchestrator']})

    def native_entrypoint(self):
        suffix = 'cmd' if os.name == 'nt' else 'command' if sys.platform == 'darwin' else 'sh'
        launcher = self.package / ('Start.' + suffix)
        require(launcher.is_file(), 'Received package is missing its native installer launcher')
        ready = self.output / 'private installer ready.json'
        argv = [str(launcher), '--no-open', '--ready', str(ready), '--home', str(self.home), '--state', str(self.state)]
        if self.codex:
            argv += ['--codex', str(self.codex)]
        if os.name == 'nt':
            # Test the shipped batch entry in its actual command interpreter.
            # Every path is an owned test path; refuse expansion characters
            # rather than fabricate a generic safe cmd.exe quoting language.
            require(not any(re.search(r'[%!"\r\n]', value) for value in argv), 'Use an acceptance output path without cmd.exe expansion characters')
            argv = subprocess.list2cmdline([self.env.get('COMSPEC', 'cmd.exe'), '/d', '/v:off', '/s', '/c']) + ' "' + ' '.join('"' + value + '"' for value in argv) + '"'
        log = (self.logs / 'native-installer-entrypoint.log').open('wb')
        process = subprocess.Popen(argv, env=self.env, cwd=self.home, stdout=log, stderr=subprocess.STDOUT)
        self.running.append(process)
        try:
            deadline = time.monotonic() + 30
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(.02)
            require(ready.exists() and process.poll() is None, 'Native installer entry did not produce a private live ready receipt')
            receipt = load(ready)
            require(receipt['schema'] == 'codex-agents.setup-web-ready/1' and Path(receipt['package']) == self.package,
                    'Native entrypoint booted a different package')
            url = urllib.parse.urlsplit(receipt['url'])
            require(url.scheme == 'http' and url.hostname == '127.0.0.1' and url.fragment.startswith('launch='), 'Installer did not bind a loopback launcher session')
            origin = url.scheme + '://' + url.netloc
            for path, content_type in (('/', 'text/html'), ('/assets/app.mjs', 'javascript'), ('/assets/style.css', 'text/css')):
                with urllib.request.urlopen(origin + path, timeout=10) as response:
                    data = response.read(1024 * 1024)
                    require(response.status == 200 and content_type in response.headers.get('Content-Type', '') and data,
                            'Native installer HTML or asset is unavailable')
            with urllib.request.urlopen(origin + '/health', timeout=10) as response:
                health = json.loads(response.read())
            require(health['instance_id'] == receipt['instance_id'] and health['product'] == 'codex-agent-system-setup', 'Native installer health identity differs')
            token = urllib.parse.parse_qs(url.fragment)['launch'][0]
            request = urllib.request.Request(origin + '/api/session', data=encoded({'launch_token': token}),
                headers={'Origin': origin, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=10) as response:
                session = json.loads(response.read())
                cookie = response.headers['Set-Cookie'].split(';', 1)[0]
            request = urllib.request.Request(origin + '/api/action', data=encoded({'action': 'shutdown'}),
                headers={'Origin': origin, 'Content-Type': 'application/json', 'Cookie': cookie, 'X-Setup-CSRF': session['csrf_token']})
            with urllib.request.urlopen(request, timeout=10) as response:
                require(json.loads(response.read())['status'] == 'stopped', 'Native installer did not accept its owned shutdown')
            require(process.wait(timeout=15) == 0, 'Native installer launcher did not exit cleanly')
            self.record('ordinary-native-launcher-serves-live-installer-html-and-assets',
                        {'launcher': launcher.name, 'instance_id': receipt['instance_id'], 'graphical_rendering': 'separate GUI acceptance'})
        finally:
            if process.poll() is None:
                if os.name == 'nt':
                    # Start.cmd owns the Node child. Terminate only this known
                    # test wrapper tree if an entrypoint assertion failed.
                    subprocess.run([str(Path(self.env.get('SYSTEMROOT', 'C:/Windows')) / 'System32/taskkill.exe'),
                                    '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=10)
                else:
                    process.kill()
                process.wait(timeout=10)
            log.close()

    def real_writer_lock(self):
        marker = self.output / 'lock-holder-ready.json'
        code = '''import importlib.util,json,pathlib,sys,time
p=pathlib.Path(sys.argv[1]);s=importlib.util.spec_from_file_location('buyer_lock_holder',p);m=importlib.util.module_from_spec(s)
exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__)
with m.locked(pathlib.Path(sys.argv[2]),pathlib.Path(sys.argv[3])):
 pathlib.Path(sys.argv[4]).write_text(json.dumps({'pid':__import__('os').getpid()}));time.sleep(90)
'''
        holder = subprocess.Popen([str(self.python), '-I', '-X', 'utf8', '-B', '-c', code,
                                   str(self.package / 'setup/setup.py'), str(self.state), str(self.home), str(marker)],
                                  env=self.env, cwd=self.home, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.running.append(holder)
        try:
            deadline = time.monotonic() + 20
            while not marker.exists() and holder.poll() is None and time.monotonic() < deadline:
                time.sleep(.01)
            require(marker.exists() and holder.poll() is None, 'Actual lock holder did not become ready')
            refused = self.setup('install', '--plan', self.plan, '--approve', self.approval, expected=(2,))
            require('Another buyer setup process' in refused.get('reason', ''), 'Second process was not rejected by the actual native lock')
            require(not self.journal.exists(), 'Second writer changed the installation journal')
        finally:
            if holder.poll() is None:
                holder.kill()
            holder.communicate(timeout=10)
        self.record('two-real-processes-exclude-the-second-writer', {'lock_holder_pid': holder.pid, 'native_lock_released_by_process_exit': True})

    def interrupt_install(self):
        process = subprocess.Popen([str(x) for x in self.setup_argv('install', '--plan', self.plan, '--approve', self.approval)],
                                   env=self.env, cwd=self.home, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.running.append(process)
        deadline = time.monotonic() + 180
        observed = None
        installed_before_termination = []
        names = [row['name'] for row in load(self.package / 'product/kit/manifest.json')['skills']]
        while process.poll() is None and time.monotonic() < deadline:
            try:
                current = load(self.journal)
                installed_before_termination = [name for name in names if (self.skills_root / name / 'SKILL.md').is_file()]
                if current.get('status') == 'installing' and installed_before_termination:
                    observed = current
                    process.kill()  # SIGKILL on POSIX; TerminateProcess on Windows.
                    break
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(.002)
        if process.poll() is None:
            process.kill()
        stdout, stderr = process.communicate(timeout=15)
        (self.logs / 'interrupted-install.json').write_bytes(encoded({'pid': process.pid, 'returncode': process.returncode,
            'journal_observed': observed, 'stdout': stdout.decode('utf8', errors='replace'), 'stderr': stderr.decode('utf8', errors='replace')}))
        require(observed and installed_before_termination and process.returncode != 0, 'Could not terminate a real in-flight installation after its first managed files were installed')
        require(load(self.journal)['status'] != 'complete', 'Installation completed before the interruption boundary')
        operations = self.setup('operations')
        row = next((value for value in operations['operations'] if value['journal'] == str(self.journal)), None)
        require(row and row['can_resume'] and row['plan_sha256'] == self.approval, 'Interrupted operation is not resumable with its exact plan')
        self.record('actual-install-process-termination-retains-recovery-journal', {'termination': 'TerminateProcess' if os.name == 'nt' else 'SIGKILL', 'journal_status': load(self.journal)['status'], 'managed_skills_visible_before_termination': installed_before_termination})

    def controllers(self):
        skills = self.skills_root
        # Execute every installed native platform controller's CLI parser using
        # the included interpreter, including all separately shipped copies.
        tested = []
        for folder in sorted(skills.iterdir()):
            for name in ('foundry.py', 'state.py', 'atelier.py', 'teamctl.py', 'context_capsule.py'):
                script = folder / 'scripts' / name
                if script.exists():
                    self.run('controller-import-' + folder.name + '-' + name, [self.python, '-X', 'utf8', '-B', script, '--help'], parse=False)
                    tested.append(str(script.relative_to(skills)))
        self.record('all-installed-native-controller-entrypoints-load', {'entrypoints': tested, 'count': len(tested)})
        foundry = skills / 'agent-foundry/scripts/foundry.py'
        factory = self.project / 'agent factory'
        self.run('foundry-init', [self.python, '-X', 'utf8', '-B', foundry, 'init', factory, '--project-id', 'native-acceptance', '--purpose', 'factory'])
        context = self.run('foundry-context', [self.python, '-X', 'utf8', '-B', foundry, 'context', factory])
        require(context['project_id'] == 'native-acceptance', 'Foundry context lost the initialized project')
        app = skills / 'app-atelier-director/scripts/state.py'
        app_root = self.project / 'app workflow'
        app_root.mkdir()
        profile = self.output / 'app-profile.json'
        profile.write_bytes(encoded({'schema_version': 'app-atelier-profile/1', 'id': 'native-app',
                                    'constraints': {'no_human_experiments': True, 'owner_operational_work': False}, 'requirements': []}))
        init = self.run('app-init', [self.python, '-X', 'utf8', '-B', app, '--project', app_root, 'init', '--profile', profile])
        require(init['initialized'] and init['execution_authorized'] is False, 'App initialization fabricated execution authority')
        self.run('app-context', [self.python, '-X', 'utf8', '-B', app, '--project', app_root, 'context'])
        chat = skills / 'chatbot-atelier-director'
        baseline = load(chat / 'assets/requirements.json')['requirements']
        ids = [value['id'] for value in baseline]
        round_path = self.project / 'chat round.json'
        round_path.write_bytes(encoded({'schema_version': 'chatbot.round/1',
            'brief': {'id': 'native-chat', 'version': '1', 'user_intent': 'Plan a bounded local workflow',
                      'baseline': 'ready archive', 'constraints': ['no external actions'], 'authorization': 'local acceptance harness'},
            'requirements': [{'id': value, 'state': 'active', 'reason': 'native installation acceptance'} for value in ids],
            'findings': [], 'decisions': [], 'changes': [], 'evidence': [], 'runs': [], 'reviews': [],
            'completion': {'stage': 'prepared', 'scope': 'local acceptance only', 'unresolved_requirement_ids': ids},
            'checkpoint': {'next_action': 'Perform actual scoped work; no execution or acceptance claimed'}}))
        self.run('chat-plan', [self.python, '-X', 'utf8', '-B', chat / 'scripts/teamctl.py', 'plan', round_path], parse=False)
        self.run('chat-round-check', [self.python, '-X', 'utf8', '-B', chat / 'scripts/check_round.py', round_path], parse=False)
        planned = load(round_path)
        require(planned['team_policy'] and planned['runs'] == [] and planned['reviews'] == [], 'Chat planning fabricated execution or review')
        game = skills / 'gamedev-director/scripts/atelier.py'
        game_root = self.project / 'game workflow'
        self.run('game-init', [self.python, '-X', 'utf8', '-B', game, 'project-init', game_root, '--project-id', 'native-game'])
        self.run('game-context', [self.python, '-X', 'utf8', '-B', game, 'context', game_root])
        game_state = load(game_root / '.gameatelier/orchestrator/state.json')
        require(game_state['project_id'] == 'native-game' and game_state['production_choice'] is None, 'Game context fabricated a production decision')
        self.record('foundry-app-chat-game-real-local-workflows', {'external_effects': False, 'model_execution': False, 'acceptance_fabricated': False})

    def discovery(self):
        if not self.codex:
            self.report['checks'].append({'name': 'actual-native-codex-skills-list', 'status': 'unverified',
                'reason': '--codex was not supplied; install the pinned supported CLI and rerun this native archive acceptance with its actual path.'})
            self.save()
            return
        result = self.setup('discover', '--journal', self.journal, '--cwd', self.project, timeout=90)
        require(result['status'] == 'native-discovery-verified' and result['skills'] == 34, 'Actual Codex did not discover exactly the installed suite')
        self.record('actual-native-codex-skills-list', {'skills': 34, 'role_execution_verified': False})

    def request(self, path, body=None, *, headers=None, expected=200):
        outgoing = dict(headers or {})
        if path.startswith('/api/') and getattr(self, 'csrf', None):
            outgoing.setdefault('X-Atelier-CSRF', self.csrf)
        if body is not None:
            outgoing['Content-Type'] = 'application/json'
        request = urllib.request.Request(self.origin + path, data=encoded(body) if body is not None else None, headers=outgoing)
        try:
            response = urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            data = json.loads(response.read(32 * 1024 * 1024).decode('utf8'))
            require(response.status == expected, 'Unexpected workbench HTTP status: ' + str(response.status) + ' ' + str(data))
            return data, dict(response.headers)

    def command(self, operation, payload=None, *, expected=200):
        data, _ = self.request('/api/v1/commands', {'command_id': str(uuid.uuid4()), 'operation': operation, 'payload': payload or {}},
            headers={'Cookie': self.cookie, 'Origin': self.origin, 'X-Atelier-CSRF': self.csrf}, expected=expected)
        require(data['status'] == ('completed' if expected == 200 else 'failed'), 'Unexpected durable command outcome')
        return data

    def workbench(self):
        require((self.package / 'control.mjs').is_file(), 'Ready archive is missing its runtime control entry')
        verified = self.control('verify')
        require(verified['source_commit'] == self.manifest['source_commit'], 'Workbench runtime belongs to another source')
        self.data = self.output / 'private workbench data'
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        flags = ['--data-dir', self.data, '--port', str(port), '--no-open']
        self.service_flags = flags
        started = self.control('start', *flags)
        require(started['status'] == 'started', 'Actual packaged workbench did not start')
        self.service = started
        self.origin = started['origin']
        repeat = self.control('start', *flags)
        require(repeat['status'] == 'already_running' and repeat['pid'] == started['pid'] and repeat['instance_id'] == started['instance_id'], 'Repeated start created another writer')
        require(self.control('doctor', *flags)['database']['engine'] == 'SQLite', 'Doctor did not observe the actual store')
        owner = load(self.data / 'owner-credentials.json')
        session, headers = self.request('/api/v1/session', headers={'X-Atelier-Control': owner['control_key']})
        self.cookie = next(value for key, value in headers.items() if key.lower() == 'set-cookie').split(';', 1)[0]
        self.csrf = session['csrf_token']
        self.command('service.settings', {'locale': 'uk'})
        backup = self.command('service.backup')['result']
        self.command('service.settings', {'locale': 'en'})
        self.command('service.restore-preview', {'backup_id': backup['backup_id']})
        rejected = self.command('service.restore', {'backup_id': backup['backup_id'], 'sha256': '0' * 64, 'confirmed': True}, expected=409)
        require(rejected['error']['code'] == 'SCOPE_MISMATCH', 'Restore accepted the wrong approved digest')
        self.command('service.restore-preview', {'backup_id': backup['backup_id']})
        self.command('service.restore', {'backup_id': backup['backup_id'], 'sha256': backup['sha256'], 'confirmed': True})
        require(digest(self.project_file) == self.preserved[str(self.project_file)], 'Service restore wrote customer project files')
        stopped = self.control('stop', *flags)
        require(stopped['status'] == 'completed', 'Actual workbench stop did not complete')
        for _ in range(40):
            if self.control('status', *flags)['status'] == 'stopped':
                self.service = None
                break
            time.sleep(.1)
        require(self.service is None, 'Workbench remains alive after stop')
        self.record('actual-workbench-boot-repeat-authenticated-backup-restore-stop', {'port': port, 'model_or_provider_execution': False})
        snapshot = self.output / 'offline snapshot'
        receipt = self.control('snapshot', '--data-dir', self.data, '--output', snapshot)
        require(receipt['status'] == 'snapshot-verified', 'Offline snapshot was not verified')
        restored = self.output / 'restored workbench data'
        rejected = self.control('restore', '--snapshot', snapshot, '--sha256', '0' * 64, '--output', restored, expected=(1,))
        require(rejected['status'] == 'blocked' and not restored.exists(), 'Wrong snapshot digest changed restore output')
        restoration = self.control('restore', '--snapshot', snapshot, '--sha256', receipt['sha256'], '--output', restored)
        require(restoration['status'] == 'restored-new-directory' and restoration['source_preserved'], 'Offline restore did not preserve source state')
        source_files = load(snapshot / 'snapshot-manifest.json')['files']
        for relative, item in source_files.items():
            require(digest(self.data / relative) == item['sha256'] and digest(restored / relative) == item['sha256'], 'Offline restore changed exact source/snapshot bytes')
        restored_flags = ['--data-dir', restored, '--port', str(port), '--no-open']
        restored_start = self.control('start', *restored_flags)
        self.service, self.service_flags = restored_start, restored_flags
        require(restored_start['status'] == 'started' and restored_start['instance_id'] != started['instance_id'], 'Restored state did not boot as a fresh owned runtime instance')
        require(self.control('doctor', *restored_flags)['database']['engine'] == 'SQLite', 'Restored runtime doctor did not observe its real database')
        self.control('stop', *restored_flags)
        for _ in range(40):
            if self.control('status', *restored_flags)['status'] == 'stopped':
                self.service = None
                break
            time.sleep(.1)
        require(self.service is None, 'Restored workbench remains alive after stop')
        for relative, item in source_files.items():
            require(digest(self.data / relative) == item['sha256'], 'Booting restored state changed the original source state')
        newer = self.output / 'newer schema state'
        newer.mkdir(mode=0o700)
        self.run('create-newer-schema-fixture', [self.python, '-I', '-B', '-c',
            'import sqlite3,sys;d=sqlite3.connect(sys.argv[1]);d.execute("PRAGMA user_version=2");d.close();print("{}")', newer / 'atelier.sqlite'])
        before = digest(newer / 'atelier.sqlite')
        blocked = self.control('start', '--data-dir', newer, '--no-open', expected=(1,))
        require(blocked['status'] == 'blocked' and 'newer' in blocked['message'].lower(), 'Newer schema was not rejected by read-only preflight')
        require(digest(newer / 'atelier.sqlite') == before and not (newer / 'instance.lock').exists(), 'Newer-schema preflight changed original data or started a writer')
        self.record('offline-snapshot-exact-restore-and-newer-schema-preservation', {'snapshot_sha256': receipt['sha256'], 'restored_files': len(source_files), 'sqlite_schema_max': 1})

    def recover_and_uninstall(self):
        rolled = self.setup('rollback', '--journal', self.journal)
        require(rolled['status'] == 'rolled-back', 'Rollback did not complete')
        require(not (self.skills_root / 'agent-foundry').exists(), 'Rollback retained a newly installed managed skill')
        self.preserve('rollback-restores-customer-work', restored_profile=True)
        plan = self.output / 'reinstallation plan.json'
        audit = self.setup('audit', '--plan', plan)
        installed = self.setup('install', '--plan', plan, '--approve', audit['plan_sha256'])
        journal = Path(installed['journal'])
        self.setup('verify', '--journal', journal)
        current = self.setup('audit', '--plan', self.output / 'known current plan.json')
        require(current['mode'] == 'known-current' and current['status'] == 'ready', 'Repeated current-version audit is not stable')
        # Unknown user changes must block before any managed entry is deleted.
        source = self.skills_root / 'app-atelier-build/SKILL.md'
        original = source.read_bytes()
        source.write_bytes(original + b'\nCustomer local refinement.\n')
        blocked = self.setup('uninstall', '--journal', journal, expected=(2,))
        require(blocked['status'] == 'blocked' and (self.skills_root / 'agent-foundry/SKILL.md').exists(), 'Uninstall did not preserve a locally modified managed suite')
        source.write_bytes(original)
        result = self.setup('uninstall', '--journal', journal)
        require(result['status'] == 'uninstalled', 'Uninstall did not complete')
        if not self.role.exists():
            entries = load(journal)['uninstall_entries']
            index = next(i for i, value in enumerate(entries) if value['target'] == str(self.role))
            require(digest(Path(result['backups']) / str(index)) == self.preserved[str(self.role)], 'Uninstall did not retain the exact tuned role in its owned recovery backup')
        self.preserve('uninstall-preserves-customer-work')
        require('agent-system-quality:start' not in self.profile.read_text(encoding='utf8'), 'Uninstall retained the managed instructions block')
        retained = list((self.state / 'packages').iterdir())
        require(len(retained) == 1, 'Acceptance unnecessarily retained more than one complete product package')
        self.record('rollback-reinstall-current-audit-drift-block-and-uninstall', {'retained_full_packages': 1, 'projects_preserved': True})

    def published_predecessor_upgrade(self):
        """Exercise actual public6.4 bytes; Git is test infrastructure only.

        Reuse this test HOME and its one cached current package after uninstall.
        No old controller is executed: the received package's portable buyer
        engines must recognize, upgrade, verify and roll back the real baseline.
        """
        repo = Path(__file__).resolve().parents[1]
        git = ['git', '--no-replace-objects', '-C', str(repo)]

        def published(name):
            return subprocess.check_output([*git, 'show', PUBLISHED_PREDECESSOR + ':' + name])

        release = json.loads(published('releases/current.json'))
        baseline = json.loads(published('kit/manifest.json'))
        roles = json.loads(published('agent-profiles/manifest.json'))['roles']
        require(release['repository_version'] == '1.7.0' and release['suite_version'] == '6.4.0', 'Predecessor commit is not the declared published release')
        require(len(baseline['skills']) == 33 and len(roles) == 12, 'Published predecessor does not have the expected complete product')
        names = {row['name'] for row in baseline['skills']}
        skills = self.home / '.agents/skills'
        # The real published predecessor used .agents on every host. Windows
        # must migrate this exact tree to its supported CODEX_HOME/skills root;
        # rollback must restore the old root, not reinterpret the old journal.
        require(not any((skills / name).exists() for name in names | {'atelier-orchestrator'}), 'Stage predecessor only after the managed uninstall has completed')
        require('agent-system-quality:start' not in self.profile.read_text(encoding='utf8'), 'An unexpected managed profile is still installed')
        require(all(not (self.home / '.codex/agents' / row['file']).exists() for row in roles), 'Predecessor staging must not overwrite a role')
        before_customer = {str(path): digest(path) for path in (self.foreign, self.project_file)}
        role_names = {row['file'] for row in roles}
        copied = []
        command = [*git, 'archive', '--format=tar', PUBLISHED_PREDECESSOR, 'kit/skills',
                   'optional-skills/atelier-orchestrator', 'agent-profiles']
        archive = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=archive.stdout, mode='r|') as stream:
                for item in stream:
                    path = PurePosixPath(item.name)
                    require(not path.is_absolute() and '..' not in path.parts and '\\' not in item.name,
                            'Unexpected path in the exact Git predecessor archive')
                    require(item.isdir() or item.isfile(), 'Linked or special predecessor Git member')
                    if item.isdir():
                        continue
                    if item.name.startswith('kit/skills/'):
                        relative = path.relative_to('kit/skills')
                        require(relative.parts[0] in names, 'Unexpected predecessor core skill')
                        target = skills.joinpath(*relative.parts)
                    elif item.name.startswith('optional-skills/atelier-orchestrator/'):
                        relative = path.relative_to('optional-skills/atelier-orchestrator')
                        target = skills / 'atelier-orchestrator' / relative
                    elif path.parent.as_posix() == 'agent-profiles' and path.name in role_names:
                        target = self.home / '.codex/agents' / path.name
                    else:
                        continue
                    require(item.size <= 16 * 1024 * 1024 and not target.exists(), 'Oversized or colliding predecessor member')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with stream.extractfile(item) as source, target.open('xb') as output:
                        shutil.copyfileobj(source, output, 128 * 1024)
                    target.chmod(0o755 if item.mode & 0o111 else 0o644)
                    copied.append(target)
            archive.stdout.close()
            stderr = archive.stderr.read().decode('utf8', errors='replace')
            require(archive.wait(timeout=15) == 0, 'Reading exact predecessor Git objects failed: ' + stderr)
        finally:
            if archive.poll() is None:
                archive.kill(); archive.wait(timeout=10)
            archive.stdout.close(); archive.stderr.close()
        # Prove the complete published kit, not merely a fake older version label.
        for row in baseline['skills']:
            folder = skills / row['name']
            actual = {path.relative_to(folder).as_posix(): {'sha256': digest(path), 'size': path.stat().st_size}
                      for path in folder.rglob('*') if path.is_file()}
            expected = {name: {'sha256': record['sha256'], 'size': record['size']} for name, record in row['files'].items()}
            require(actual == expected, 'Staged predecessor differs from published kit manifest: ' + row['name'])
        for row in roles:
            require(digest(self.home / '.codex/agents' / row['file']) == row['sha256'], 'Published predecessor role differs')
        profile = published('host-profiles/codex/AGENTS.md').decode('utf8').replace('{{STANDARD_ROOT}}', str(skills / 'agent-foundry'))
        self.profile.write_bytes((self.profile.read_text(encoding='utf8').rstrip() + '\n\n' + profile.strip() + '\n').encode('utf8'))
        # This tuning is supported user configuration, outside the pinned prompt.
        self.role.write_bytes(b'model = "native-upgrade-owner-choice"\nmodel_reasoning_effort = "high"\n' + self.role.read_bytes())
        copied.append(self.profile)
        predecessor = {path.relative_to(self.home).as_posix(): {'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)} for path in copied}
        (self.output / 'published-predecessor-files.json').write_bytes(encoded({
            'source_commit': PUBLISHED_PREDECESSOR, 'repository_version': release['repository_version'],
            'suite_version': release['suite_version'], 'kit_manifest_sha256': hashlib.sha256(published('kit/manifest.json')).hexdigest(),
            'scope': 'All33 published core skills, Orchestrator,12 roles, managed profile; one supported role has explicit owner selector tuning.',
            'files': predecessor}))
        plan = self.output / 'published predecessor upgrade plan.json'
        audit = self.setup('audit', '--plan', plan)
        require(audit['status'] == 'ready' and audit['mode'] == 'update', 'Published6.4 predecessor is not a supported complete update')
        installed = self.setup('install', '--plan', plan, '--approve', audit['plan_sha256'])
        verified = self.setup('verify', '--journal', installed['journal'])
        require(verified['skills'] == 33 and verified['orchestrator'] and verified['source_commit'] == self.manifest['source_commit'], 'Predecessor upgrade did not verify the complete new product')
        if WINDOWS:
            require(all(not (skills / name).exists() and (self.skills_root / name / 'SKILL.md').is_file()
                        for name in names | {'atelier-orchestrator'}),
                    'Windows predecessor migration left duplicate or missing managed sources')
        for value in (b'model = "native-upgrade-owner-choice"', b'model_reasoning_effort = "high"'):
            require(value in self.role.read_bytes(), 'Upgrade dropped supported owner role tuning')
        for path, expected in before_customer.items():
            require(digest(path) == expected, 'Upgrade changed unrelated customer work')
        rolled = self.setup('rollback', '--journal', installed['journal'])
        require(rolled['status'] == 'rolled-back', 'Published-predecessor rollback did not complete')
        if WINDOWS:
            require(all(not (self.skills_root / name).exists() for name in names | {'atelier-orchestrator'}),
                    'Windows migration rollback retained a new-root managed source')
        roots = [skills / name for name in names | {'atelier-orchestrator'}]
        restored_files = {path.relative_to(self.home).as_posix() for root in roots for path in root.rglob('*') if path.is_file()}
        restored_files |= {str((Path('.codex/agents') / row['file']).as_posix()) for row in roles} | {'.codex/AGENTS.md'}
        require(restored_files == set(predecessor), 'Rollback did not restore the exact predecessor file inventory')
        for relative, expected in predecessor.items():
            path = self.home / relative
            require(digest(path) == expected['sha256'] and stat.S_IMODE(path.stat().st_mode) == expected['mode'], 'Rollback changed published predecessor bytes or native modes: ' + relative)
        for path, expected in before_customer.items():
            require(digest(path) == expected, 'Predecessor rollback changed unrelated customer work')
        require(len(list((self.state / 'packages').iterdir())) == 1, 'Predecessor test duplicated the full current package cache')
        self.record('published6-4-complete-upgrade-and-exact-rollback', {
            'predecessor_commit': PUBLISHED_PREDECESSOR, 'core_skills': 33, 'roles': 12,
            'predecessor_files': len(predecessor), 'orchestrator': True, 'owner_tuning_preserved': True,
            'foreign_skill_and_project_preserved': True, 'retained_full_packages': 1,
            'previous_personal_root': str(skills), 'current_personal_root': str(self.skills_root),
            'cross_root_migration_and_rollback': WINDOWS,
            'old_controllers_executed': False, 'current_portable_buyer_engines_executed': True})

    def immutable_received_package(self):
        # The authoritative ordinary buyer validator hashes every received file
        # again and rejects pyc, logs or unexpected runtime mutations.
        checked = self.setup('doctor', expected=(0, 2))
        require(checked['package_manifest_sha256'] == self.report['package_manifest_sha256'], 'Received package changed after execution')
        bytecode = {path.relative_to(self.package).as_posix(): digest(path) for path in self.package.rglob('*.pyc')}
        caches = {path.relative_to(self.package).as_posix() for path in self.package.rglob('__pycache__')}
        require(bytecode == self.initial_bytecode and caches == self.initial_cache_directories, 'Execution created or changed bytecode in the distributed package')
        self.record('received-package-reverified-without-bytecode-mutations-or-extra-files', {'unchanged_vendor_bytecode_files': len(bytecode)})

    def cleanup(self):
        if self.service:
            try:
                self.control('stop', *self.service_flags)
            except Exception as error:
                self.report['cleanup_error'] = str(error)
        for process in self.running:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)

    def execute(self):
        try:
            self.prepare()
            self.bundled_linux_terminfo()
            self.seed()
            self.native_entrypoint()
            self.buyer_install()
            self.controllers()
            self.discovery()
            self.workbench()
            self.recover_and_uninstall()
            self.published_predecessor_upgrade()
            self.immutable_received_package()
            self.report['status'] = 'passed'
            return 0
        except Exception as error:
            self.report['status'] = 'failed'
            self.report['failure'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
            print('Acceptance failed: ' + str(error), file=sys.stderr, flush=True)
            return 1
        finally:
            self.cleanup()
            self.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='NEW private native acceptance directory')
    parser.add_argument('--codex', help='Actual installed Codex CLI executable or official npm shim; no authentication is copied')
    args = parser.parse_args()
    try:
        return Acceptance(args.archive, args.output, args.codex).execute()
    except Exception as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
