#!/usr/bin/env python3
"""Exercise buyer changes with a real medium-integrity non-admin Windows token.

The SDK broker never creates an account, uses alternate credentials, or copies
the runner's profile. This proves restricted same-SID rights, not first-login UX.
Microsoft contracts:
https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-createrestrictedtoken
https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessasuserw
https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control
"""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import subprocess
import sys
import time
import uuid

sys.dont_write_bytecode = True
SCHEMA = 'codex-agents.windows-standard-user-proof/1'
OWNED_OUTPUT = None


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def ordinary(path):
    path = Path(os.path.abspath(os.fspath(path)))
    for ancestor in (path, *path.parents):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                'Linked or reparse probe input is not permitted')
    return path


class SIDAttributes(ctypes.Structure):
    _fields_ = [('Sid', W.LPVOID), ('Attributes', W.DWORD)]


class LUID(ctypes.Structure):
    _fields_ = [('LowPart', W.DWORD), ('HighPart', W.LONG)]


class LUIDAttributes(ctypes.Structure):
    _fields_ = [('Luid', LUID), ('Attributes', W.DWORD)]


class SecurityAttributes(ctypes.Structure):
    _fields_ = [('nLength', W.DWORD), ('lpSecurityDescriptor', W.LPVOID), ('bInheritHandle', W.BOOL)]


class StartupInfo(ctypes.Structure):
    _fields_ = [('cb', W.DWORD), ('lpReserved', W.LPWSTR), ('lpDesktop', W.LPWSTR), ('lpTitle', W.LPWSTR),
                ('dwX', W.DWORD), ('dwY', W.DWORD), ('dwXSize', W.DWORD), ('dwYSize', W.DWORD),
                ('dwXCountChars', W.DWORD), ('dwYCountChars', W.DWORD), ('dwFillAttribute', W.DWORD),
                ('dwFlags', W.DWORD), ('wShowWindow', W.WORD), ('cbReserved2', W.WORD),
                ('lpReserved2', ctypes.POINTER(W.BYTE)), ('hStdInput', W.HANDLE),
                ('hStdOutput', W.HANDLE), ('hStdError', W.HANDLE)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [('hProcess', W.HANDLE), ('hThread', W.HANDLE), ('dwProcessId', W.DWORD), ('dwThreadId', W.DWORD)]


class Windows:
    def __init__(self):
        require(os.name == 'nt', 'A real Windows environment is required; this probe cannot be emulated by metadata.')
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.a = ctypes.WinDLL('advapi32', use_last_error=True)
        self.u = ctypes.WinDLL('user32', use_last_error=True)
        self.s = ctypes.WinDLL('shell32', use_last_error=True)
        signatures = [
            (self.k, 'GetCurrentProcess', [], W.HANDLE),
            (self.k, 'GetCurrentThreadId', [], W.DWORD),
            (self.k, 'CloseHandle', [W.HANDLE], W.BOOL),
            (self.k, 'LocalFree', [W.LPVOID], W.LPVOID),
            (self.k, 'WaitForSingleObject', [W.HANDLE, W.DWORD], W.DWORD),
            (self.k, 'GetExitCodeProcess', [W.HANDLE, ctypes.POINTER(W.DWORD)], W.BOOL),
            (self.k, 'CreateFileW', [W.LPCWSTR, W.DWORD, W.DWORD, W.LPVOID, W.DWORD, W.DWORD, W.HANDLE], W.HANDLE),
            (self.a, 'OpenProcessToken', [W.HANDLE, W.DWORD, ctypes.POINTER(W.HANDLE)], W.BOOL),
            (self.a, 'GetTokenInformation', [W.HANDLE, W.DWORD, W.LPVOID, W.DWORD, ctypes.POINTER(W.DWORD)], W.BOOL),
            (self.a, 'SetTokenInformation', [W.HANDLE, W.DWORD, W.LPVOID, W.DWORD], W.BOOL),
            (self.a, 'ConvertStringSidToSidW', [W.LPCWSTR, ctypes.POINTER(W.LPVOID)], W.BOOL),
            (self.a, 'ConvertSidToStringSidW', [W.LPVOID, ctypes.POINTER(W.LPWSTR)], W.BOOL),
            (self.a, 'GetLengthSid', [W.LPVOID], W.DWORD),
            (self.a, 'CheckTokenMembership', [W.HANDLE, W.LPVOID, ctypes.POINTER(W.BOOL)], W.BOOL),
            (self.a, 'LookupPrivilegeNameW', [W.LPCWSTR, ctypes.POINTER(LUID), W.LPWSTR, ctypes.POINTER(W.DWORD)], W.BOOL),
            (self.a, 'CreateRestrictedToken', [W.HANDLE, W.DWORD, W.DWORD, ctypes.POINTER(SIDAttributes), W.DWORD, W.LPVOID, W.DWORD, W.LPVOID, ctypes.POINTER(W.HANDLE)], W.BOOL),
            (self.a, 'DuplicateToken', [W.HANDLE, W.DWORD, ctypes.POINTER(W.HANDLE)], W.BOOL),
            (self.a, 'ImpersonateLoggedOnUser', [W.HANDLE], W.BOOL),
            (self.a, 'RevertToSelf', [], W.BOOL),
            (self.a, 'ConvertStringSecurityDescriptorToSecurityDescriptorW', [W.LPCWSTR, W.DWORD, ctypes.POINTER(W.LPVOID), ctypes.POINTER(W.DWORD)], W.BOOL),
            (self.a, 'GetSecurityDescriptorDacl', [W.LPVOID, ctypes.POINTER(W.BOOL), ctypes.POINTER(W.LPVOID), ctypes.POINTER(W.BOOL)], W.BOOL),
            (self.a, 'CreateProcessAsUserW', [W.HANDLE, W.LPCWSTR, W.LPWSTR, W.LPVOID, W.LPVOID, W.BOOL, W.DWORD, W.LPVOID, W.LPCWSTR, ctypes.POINTER(StartupInfo), ctypes.POINTER(ProcessInfo)], W.BOOL),
            (self.u, 'CreateDesktopW', [W.LPCWSTR, W.LPCWSTR, W.LPVOID, W.DWORD, W.DWORD, ctypes.POINTER(SecurityAttributes)], W.HANDLE),
            (self.u, 'GetThreadDesktop', [W.DWORD], W.HANDLE),
            (self.u, 'SetThreadDesktop', [W.HANDLE], W.BOOL),
            (self.u, 'CloseDesktop', [W.HANDLE], W.BOOL),
            (self.s, 'IsUserAnAdmin', [], W.BOOL),
        ]
        for library, name, arguments, result in signatures:
            function = getattr(library, name)
            function.argtypes, function.restype = arguments, result

    def ok(self, result, operation):
        if not result:
            code = ctypes.get_last_error()
            raise OSError(code, operation + ': ' + ctypes.FormatError(code))
        return result

    def sid(self, value):
        pointer = W.LPVOID()
        self.ok(self.a.ConvertStringSidToSidW(value, ctypes.byref(pointer)), 'ConvertStringSidToSidW')
        return pointer

    def sid_text(self, pointer):
        text = W.LPWSTR()
        self.ok(self.a.ConvertSidToStringSidW(pointer, ctypes.byref(text)), 'ConvertSidToStringSidW')
        try:
            return text.value
        finally:
            self.k.LocalFree(ctypes.cast(text, W.LPVOID))

    def information(self, token, kind):
        size = W.DWORD()
        self.a.GetTokenInformation(token, kind, None, 0, ctypes.byref(size))
        require(size.value and size.value < 1024 * 1024, 'Unexpected Windows token information size')
        buffer = ctypes.create_string_buffer(size.value)
        self.ok(self.a.GetTokenInformation(token, kind, buffer, size, ctypes.byref(size)), 'GetTokenInformation')
        return buffer

    def token(self, rights=0x8):
        handle = W.HANDLE()
        self.ok(self.a.OpenProcessToken(self.k.GetCurrentProcess(), rights, ctypes.byref(handle)), 'OpenProcessToken')
        return handle

    def token_boolean(self, token, kind):
        """Read only the scalar bytes actually returned by this SDK query.

        TokenHasRestrictions is a BOOLEAN at a DWORD-aligned address, despite
        the older DWORD reference documentation. Microsoft clarification:
        https://github.com/microsoft/win32metadata/discussions/2308
        Preserve compatibility with the documented four-byte representation;
        never decode unreturned trailing bytes as part of a one-byte result.
        TokenElevation remains a four-byte TOKEN_ELEVATION value.
        """
        require(kind in (20, 21), 'Unsupported Windows token scalar class')
        storage = ctypes.c_uint32()  # zero initialized, DWORD size/alignment
        returned = W.DWORD()
        self.ok(self.a.GetTokenInformation(token, kind, ctypes.byref(storage), ctypes.sizeof(storage),
                                         ctypes.byref(returned)), 'GetTokenInformation scalar ' + str(kind))
        allowed = (1, 4) if kind == 21 else (4,)
        require(returned.value in allowed, 'Unexpected Windows token scalar size for class ' + str(kind))
        return bool(int.from_bytes(ctypes.string_at(ctypes.byref(storage), returned.value), 'little'))

    def identity(self):
        handle = self.token()
        admin = self.sid('S-1-5-32-544')
        try:
            member = W.BOOL()
            self.ok(self.a.CheckTokenMembership(None, admin, ctypes.byref(member)), 'CheckTokenMembership')
            user = self.information(handle, 1)
            user_sid = self.sid_text(SIDAttributes.from_buffer(user).Sid)
            owner_info = self.information(handle, 4)
            owner_sid = self.sid_text(W.LPVOID.from_buffer(owner_info).value)
            integrity = self.information(handle, 25)
            integrity_sid = self.sid_text(SIDAttributes.from_buffer(integrity).Sid)
            privileges = self.information(handle, 3)
            count = W.DWORD.from_buffer(privileges).value
            require(count <= 256, 'Unexpected token privilege count')
            enabled = []
            for index in range(count):
                row = LUIDAttributes.from_buffer(privileges, ctypes.sizeof(W.DWORD) + index * ctypes.sizeof(LUIDAttributes))
                if not row.Attributes & 2:
                    continue
                size = W.DWORD(256)
                name = ctypes.create_unicode_buffer(size.value)
                self.ok(self.a.LookupPrivilegeNameW(None, ctypes.byref(row.Luid), name, ctypes.byref(size)), 'LookupPrivilegeNameW')
                enabled.append(name.value)
            return {'is_user_an_admin': bool(self.s.IsUserAnAdmin()), 'admin_group_enabled': bool(member.value),
                    'integrity_sid': integrity_sid, 'enabled_privileges': enabled,
                    'token_has_restrictions': self.token_boolean(handle, 21),
                    'token_elevated': self.token_boolean(handle, 20),
                    'default_owner_is_user': owner_sid == user_sid,
                    'user_sid_sha256': hashlib.sha256(user_sid.encode('ascii')).hexdigest(),
                    'pid': os.getpid(), 'python': sys.executable, 'machine': platform.machine()}
        finally:
            self.k.LocalFree(admin)
            self.k.CloseHandle(handle)


def selected_runtime(package, python):
    require(package.is_dir() and not package.is_symlink(), 'Expected the already validated received package')
    manifest = json.loads((package / 'product-manifest.json').read_text(encoding='utf8'))
    require(manifest.get('product_id') == 'codex-agent-system' and manifest.get('source_clean') is True,
            'This proof requires an exact clean received product')
    machine = {'amd64': 'x64', 'x86_64': 'x64', 'arm64': 'arm64', 'aarch64': 'arm64'}.get(platform.machine().lower())
    target = 'win32-' + str(machine)
    tools = manifest.get('portable_runtimes', {}).get(target)
    require(tools and tools['python_executable'] in manifest['files'], 'Package lacks its actual native Windows runtime')
    for key in ('python_executable', 'node_executable'):
        name = tools[key]
        relative = PurePosixPath(name)
        require(relative.as_posix() == name and not relative.is_absolute() and '..' not in relative.parts
                and '\\' not in name and ':' not in name and name in manifest['files'], 'Unsafe runtime inventory reference')
        ordinary(package / relative)
    require(python.resolve() == (package / tools['python_executable']).resolve(), 'Use the exact received bundled Python')
    require(sha(python) == manifest['files'][tools['python_executable']]['sha256'], 'Bundled interpreter changed')
    helper = ordinary(package / 'setup/platform_support.py')
    require(sha(helper) == manifest['files']['setup/platform_support.py']['sha256'], 'Private-path helper differs from the received inventory')
    return manifest, tools, target


def child_environment(home, temporary, package, tools):
    system = Path(os.environ.get('SYSTEMROOT', 'C:/Windows'))
    env = {key.upper(): value for key, value in os.environ.items() if key.upper() in {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT'}}
    python, node = package / tools['python_executable'], package / tools['node_executable']
    env.update(HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / '.codex'),
               APPDATA=str(home / 'AppData/Roaming'), LOCALAPPDATA=str(home / 'AppData/Local'),
               TMP=str(temporary), TEMP=str(temporary), TMPDIR=str(temporary),
               AGENT_SYSTEM_PYTHON=str(python), AGENT_SYSTEM_NODE=str(node),
               PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
               PATH=os.pathsep.join(map(str, [system / 'System32', system / 'System32/WindowsPowerShell/v1.0', python.parent, node.parent])))
    return env


def completed_child_observation(destination, code, source_commit=None):
    """Keep a failed child's actual exit status when no Python receipt exists."""
    write(destination.with_name('CHILD-EXIT.json'), {
        'schema': 'codex-agents.windows-child-exit/1', 'phase': 'child-process-completed',
        'source_commit': source_commit, 'exit_code': code, 'exit_code_hex': '0x' + format(code, '08X'),
        'observation_exists': destination.is_file(), 'native_acceptance': False})
    if not destination.is_file():
        raise RuntimeError('Restricted child exited before writing its observation: exit_code='
                           + str(code) + ' (0x' + format(code, '08X') + ')')
    return json.loads(destination.read_text(encoding='utf8'))


def restricted_read_access(win, token, targets):
    """Observe file read/execute access without modifying any target or ACL."""
    duplicate = W.HANDLE()
    win.ok(win.a.DuplicateToken(token, 2, ctypes.byref(duplicate)), 'DuplicateToken diagnostic')
    impersonating = False
    results = []
    try:
        win.ok(win.a.ImpersonateLoggedOnUser(duplicate), 'ImpersonateLoggedOnUser diagnostic')
        impersonating = True
        for name, path, executable, directory in targets:
            access = 0x100000 | 0x80 | 1 | (0x20 if executable else 0)
            handle = win.k.CreateFileW(str(path), access, 7, None, 3,
                                      0x02000000 if directory else 0x80, None)
            invalid = ctypes.c_void_p(-1).value
            if handle is None or handle == invalid:
                code = ctypes.get_last_error()
                results.append({'target': name, 'access': 'read-execute' if executable else 'read',
                                'opened': False, 'windows_error': code, 'message': ctypes.FormatError(code)})
            else:
                try:
                    results.append({'target': name, 'access': 'read-execute' if executable else 'read', 'opened': True})
                finally:
                    win.k.CloseHandle(handle)
        return results
    finally:
        try:
            if impersonating:
                win.ok(win.a.RevertToSelf(), 'RevertToSelf diagnostic')
        finally:
            win.k.CloseHandle(duplicate)


def child(args, win):
    package, output, python = (ordinary(value).resolve() for value in (args.package, args.output, args.python))
    ownership = json.loads((output / 'PROBE-OWNERSHIP.json').read_text(encoding='utf8'))
    require(ownership.get('schema') == 'codex-agents.standard-user-probe-owner/1'
            and ownership.get('broker_pid') == os.getppid(), 'Child output was not created by its live broker')
    report = {'schema': SCHEMA, 'status': 'running', 'scope': 'Actual medium-integrity restricted same-user SID; no separate-account first-login or graphical proof.', 'checks': [], 'lifecycle_verified': False, 'model_execution': False}
    destination = output / 'STANDARD-USER-OBSERVATION.json'
    try:
        identity = win.identity()
        report['child'] = identity
        require(identity['is_user_an_admin'] is False and identity['admin_group_enabled'] is False, 'Child still has administrator group access')
        require(identity['integrity_sid'] == 'S-1-16-8192', 'Child is not at standard medium integrity')
        require(identity['token_has_restrictions'] is True and set(identity['enabled_privileges']) <= {'SeChangeNotifyPrivilege'}, 'Child token still has unexpected privileges')
        require(identity['default_owner_is_user'] is True, 'New child objects would use a different default owner')
        manifest, tools, target = selected_runtime(package, python)
        report.update(source_commit=manifest['source_commit'], source_clean=True, target=target,
                      package_manifest_sha256=sha(package / 'product-manifest.json'))
        if args.identity_only:
            report.update(status='token-observed', lifecycle_verified=False,
                          limitation='Token API preflight only. No installation lifecycle was performed and C03 is not accepted by this receipt.')
            return 0
        home = output / 'standard buyer HOME'
        home.mkdir(mode=0o700)
        state = home / '.local/share/codex-agent-system'
        foreign = home / '.agents/skills/personal-notes/notes.txt'
        foreign.parent.mkdir(parents=True)
        foreign.write_text('Preserve standard buyer notes.\n', encoding='utf8')
        project = home / 'Accepted project & Unicode Проєкт'
        project.mkdir()
        accepted = project / 'accepted.md'
        accepted.write_text('Preserve the accepted project.\n', encoding='utf8')
        instructions = home / '.codex/AGENTS.md'
        instructions.parent.mkdir(parents=True)
        personal = '# Personal instructions\nPreserve my accepted work.\n'
        instructions.write_text(personal, encoding='utf8')
        preserved = {str(path): sha(path) for path in (foreign, accepted)}
        def command(verb, *extra, expected=(0,)):
            write(output / 'CHILD-PROGRESS.json', {'phase': verb, 'status': 'running', 'model_execution': False})
            argv = [str(python), '-I', '-X', 'utf8', '-B', str(package / 'setup/setup.py'), '--package', str(package), '--home', str(home), '--state', str(state), '--json', verb, *map(str, extra)]
            started = time.monotonic()
            result = subprocess.run(argv, env=dict(os.environ), cwd=home, capture_output=True, timeout=600)
            raw = (result.stdout.strip() or result.stderr.strip()).decode('utf8')
            receipt = json.loads(raw)
            report['checks'].append({'operation': verb, 'seconds': round(time.monotonic()-started, 3), 'exit_code': result.returncode, 'receipt': receipt})
            write(destination, report)
            require(result.returncode in expected, 'Standard-user ' + verb + ' blocked: ' + str(receipt))
            return receipt
        doctor = command('doctor', expected=(0, 2))
        require(doctor['platform']['supported_skills'] and doctor['package_manifest_sha256'] == report['package_manifest_sha256'], 'Doctor did not validate the exact native package')
        plan = output / 'approved setup plan.json'
        audit = command('audit', '--plan', plan)
        require(audit['status'] == 'ready' and audit['mode'] == 'fresh', 'Standard-user audit did not prepare a fresh plan')
        installed = command('install', '--plan', plan, '--approve', audit['plan_sha256'])
        require(installed['status'] == 'installed' and installed['verification']['skills'] == 33, 'Standard-user install is incomplete')
        verified = command('verify', '--journal', installed['journal'])
        require(verified['status'] == 'verified-files' and verified['skills'] == 33 and verified['orchestrator'], 'Standard-user files are not verified')
        require(all(sha(path) == pin for path, pin in preserved.items()) and personal in instructions.read_text(encoding='utf8'), 'Standard-user install changed accepted work')
        rolled = command('rollback', '--journal', installed['journal'])
        require(rolled['status'] == 'rolled-back', 'Standard-user rollback is incomplete')
        require(all(sha(path) == pin for path, pin in preserved.items()) and instructions.read_text(encoding='utf8') == personal, 'Standard-user rollback lost accepted work')
        require(not any((home / root / 'agent-foundry').exists() for root in ('.agents/skills','.codex/skills')),
                'Rollback retained a newly installed managed skill')
        report['child_after'] = win.identity()
        require(report['child_after']['is_user_an_admin'] is False and report['child_after']['integrity_sid'] == 'S-1-16-8192', 'Child rights changed during the probe')
        report.update(status='passed', lifecycle_verified=True, preserved_project_files=True, privilege_elevation_performed=False,
                      cache_cleanup='Fixture retained package removed only after completed verified rollback; exact received package and operation records remain.')
        cache = state / 'packages'
        require(cache.is_relative_to(home), 'Fixture cache escaped its owned home')
        if cache.exists():
            shutil.rmtree(cache)
        return 0
    except Exception as error:
        report.update(status='blocked', lifecycle_verified=False, reason=str(error), error_type=type(error).__name__,
                      next='Inspect this private journal and actual Windows SDK error before retrying; no unknown mutation is replayed.')
        return 1
    finally:
        write(destination, report)


def broker(args, win):
    global OWNED_OUTPUT
    OWNED_OUTPUT = None
    package, output, python = (ordinary(value).resolve() for value in (args.package, args.output, args.python))
    manifest, tools, target = selected_runtime(package, python)
    require(not output.is_relative_to(package) and not package.is_relative_to(output), 'Keep probe output outside the immutable received package')
    require(not output.exists(), 'Choose a NEW private standard-user proof directory')
    output.mkdir(parents=True, mode=0o700)
    OWNED_OUTPUT = output
    helper = package / 'setup/platform_support.py'
    subprocess.run([str(python), '-I', '-X', 'utf8', '-B', str(helper), '--make-private', str(output)], check=True, capture_output=True)
    system = Path(os.environ.get('SYSTEMROOT', 'C:/Windows'))
    subprocess.run([str(system / 'System32/icacls.exe'), str(output), '/setintegritylevel', '(OI)(CI)M'], check=True, capture_output=True)
    write(output / 'PROBE-OWNERSHIP.json', {'schema':'codex-agents.standard-user-probe-owner/1', 'broker_pid':os.getpid()})
    temporary = output / 'temporary'
    temporary.mkdir()
    environment = child_environment(output / 'standard buyer HOME', temporary, package, tools)
    control = subprocess.run([str(python), '-I', '-X', 'utf8', '-B', '--version'], env=environment,
                             cwd=output, capture_output=True, timeout=15)
    diagnostics = {'schema': 'codex-agents.windows-sdk-diagnostics/1', 'source_commit': manifest['source_commit'],
                   'clean_environment_parent': {'exit_code': control.returncode,
                       'exit_code_hex': '0x' + format(control.returncode & 0xffffffff, '08X'),
                       'stdout': control.stdout.decode('utf8', errors='replace')[:2048],
                       'stderr': control.stderr.decode('utf8', errors='replace')[:2048]},
                   'acl_changed': False, 'parent_path_added': False, 'native_acceptance': False}
    write(output / 'SDK-DIAGNOSTICS.json', diagnostics)
    parent = win.identity()
    original = restricted = admin_sid = medium_sid = security = desktop = None
    process = ProcessInfo()
    try:
        original = win.token(0x1 | 0x2 | 0x8 | 0x80)
        restricted = W.HANDLE()
        admin_sid = win.sid('S-1-5-32-544')
        disabled = SIDAttributes(admin_sid, 0)
        win.ok(win.a.CreateRestrictedToken(original, 1, 1, ctypes.byref(disabled), 0, None, 0, None, ctypes.byref(restricted)), 'CreateRestrictedToken')
        medium_sid = win.sid('S-1-16-8192')
        label = SIDAttributes(medium_sid, 0x20)
        win.ok(win.a.SetTokenInformation(restricted, 25, ctypes.byref(label), ctypes.sizeof(label)+win.a.GetLengthSid(medium_sid)), 'SetTokenInformation medium integrity')
        user = win.information(original, 1)
        owner = W.LPVOID(SIDAttributes.from_buffer(user).Sid)
        user_sid = win.sid_text(owner)
        win.ok(win.a.SetTokenInformation(restricted, 4, ctypes.byref(owner), ctypes.sizeof(owner)), 'SetTokenInformation user default owner')
        descriptor = 'D:P(A;;GA;;;SY)(A;;GA;;;' + user_sid + ')S:(ML;;NW;;;ME)'
        security = W.LPVOID()
        win.ok(win.a.ConvertStringSecurityDescriptorToSecurityDescriptorW(descriptor, 1, ctypes.byref(security), None), 'Create private desktop security descriptor')
        dacl, present, defaulted = W.LPVOID(), W.BOOL(), W.BOOL()
        win.ok(win.a.GetSecurityDescriptorDacl(security, ctypes.byref(present), ctypes.byref(dacl), ctypes.byref(defaulted)), 'Read private default DACL')
        require(present.value and dacl.value, 'Private default DACL is missing')
        win.ok(win.a.SetTokenInformation(restricted, 6, ctypes.byref(dacl), ctypes.sizeof(dacl)), 'SetTokenInformation user default DACL')
        python_root = python.parent
        targets = [('python-executable', python, True, False),
                   ('python-runtime-dll', python_root / 'python313.dll', True, False),
                   ('vc-runtime-dll', python_root / 'vcruntime140.dll', True, False),
                   ('vc-runtime-extra-dll', python_root / 'vcruntime140_1.dll', True, False),
                   ('probe-source', Path(__file__).resolve(), False, False),
                   ('owned-output', output, False, True),
                   ('owned-output-marker', output / 'PROBE-OWNERSHIP.json', False, False)]
        diagnostics['restricted_input_access'] = restricted_read_access(win, restricted, targets)
        write(output / 'SDK-DIAGNOSTICS.json', diagnostics)
        attributes = SecurityAttributes(ctypes.sizeof(SecurityAttributes), security, False)
        desktop_name = 'AgentInstallerProbe_' + uuid.uuid4().hex
        previous = win.u.GetThreadDesktop(win.k.GetCurrentThreadId())
        desktop = win.ok(win.u.CreateDesktopW(desktop_name, None, None, 0, 0x10000000, ctypes.byref(attributes)), 'CreateDesktopW')
        win.ok(win.u.SetThreadDesktop(previous), 'Restore broker thread desktop')
        startup = StartupInfo()
        startup.cb, startup.lpDesktop = ctypes.sizeof(startup), desktop_name
        argv = [str(python), '-I', '-X', 'utf8', '-B', str(Path(__file__).resolve()), '--child', '--package', str(package), '--output', str(output), '--python', str(python)]
        if args.identity_only:
            argv.append('--identity-only')
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        block = ctypes.create_unicode_buffer('\0'.join(key+'='+value for key, value in sorted(environment.items()))+'\0\0')
        win.ok(win.a.CreateProcessAsUserW(restricted, str(python), command, None, None, False, 0x400 | 0x08000000, block, str(output), ctypes.byref(startup), ctypes.byref(process)), 'CreateProcessAsUserW')
        deadline = time.monotonic()+args.timeout_seconds
        last_phase = None
        while time.monotonic() < deadline:
            result = win.k.WaitForSingleObject(process.hProcess, 500)
            if result == 0:
                break
            require(result == 0x102, 'Windows child wait failed')
            try:
                phase = json.loads((output / 'CHILD-PROGRESS.json').read_text(encoding='utf8'))['phase']
                if phase != last_phase:
                    print('Actual non-admin Windows child: '+phase, flush=True)
                    last_phase = phase
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        else:
            subprocess.run([str(system / 'System32/taskkill.exe'), '/PID', str(process.dwProcessId), '/T', '/F'], capture_output=True, timeout=30)
            raise TimeoutError('Restricted child timed out; its private journal must be reconciled before retry')
        code = W.DWORD()
        win.ok(win.k.GetExitCodeProcess(process.hProcess, ctypes.byref(code)), 'GetExitCodeProcess')
        destination = output / 'STANDARD-USER-OBSERVATION.json'
        report = completed_child_observation(destination, code.value, manifest['source_commit'])
        report['sdk_diagnostics'] = diagnostics
        report['parent'] = parent
        report['broker'] = {'method':'CreateRestrictedToken + medium integrity + private desktop + CreateProcessAsUserW', 'child_exit_code':code.value, 'new_account_created':False, 'account_credentials_used':False}
        write(destination, report)
        expected_status, expected_lifecycle = ('token-observed', False) if args.identity_only else ('passed', True)
        require(code.value == 0 and report.get('status') == expected_status and report.get('lifecycle_verified') is expected_lifecycle,
                'Restricted standard-user probe did not complete its declared scope: '+str(report.get('reason')))
        require(report['package_manifest_sha256'] == sha(package / 'product-manifest.json') and report['source_commit'] == manifest['source_commit'], 'Restricted proof belongs to different package bytes')
        require(report['child']['user_sid_sha256'] == parent['user_sid_sha256'] and report['child']['is_user_an_admin'] is False, 'Child identity did not retain the exact user while dropping admin rights')
        return report
    finally:
        for handle in (process.hThread, process.hProcess, restricted, original):
            if handle:
                win.k.CloseHandle(handle)
        if desktop:
            win.u.CloseDesktop(desktop)
        for pointer in (admin_sid, medium_sid, security):
            if pointer:
                win.k.LocalFree(pointer)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--timeout-seconds', type=int, default=1200)
    parser.add_argument('--identity-only', action='store_true', help='Observe the actual restricted token only; never accepts the installation lifecycle.')
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        require(1 <= args.timeout_seconds <= 2400, 'Use a bounded native probe deadline')
        win = Windows()
        if args.child:
            return child(args, win)
        report = broker(args, win)
        print(json.dumps({'status':report['status'], 'lifecycle_verified':report['lifecycle_verified'], 'source_commit':report['source_commit'], 'is_user_an_admin':report['child']['is_user_an_admin'], 'model_execution':False}))
        return 0
    except Exception as error:
        report = {'schema':SCHEMA, 'status':'blocked', 'lifecycle_verified':False, 'reason':str(error), 'error_type':type(error).__name__, 'model_execution':False,
                  'next':'Run on a native Windows runner with token creation rights; retain the private child journal and SDK error. No acceptance is inferred.'}
        if OWNED_OUTPUT == args.output.resolve() and not args.child:
            diagnostics_path = args.output / 'SDK-DIAGNOSTICS.json'
            if diagnostics_path.exists():
                report['sdk_diagnostics'] = json.loads(diagnostics_path.read_text(encoding='utf8'))
            exit_path = args.output / 'CHILD-EXIT.json'
            if exit_path.exists():
                report['child_exit'] = json.loads(exit_path.read_text(encoding='utf8'))
            destination = args.output / 'STANDARD-USER-OBSERVATION.json'
            if destination.exists():
                previous = json.loads(destination.read_text(encoding='utf8'))
                previous['broker_failure'] = report
                previous['status'] = 'blocked'
                previous['lifecycle_verified'] = False
                report = previous
            write(destination, report)
        if sys.stderr is not None:
            print(json.dumps({'status':'blocked', 'reason':str(error)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
