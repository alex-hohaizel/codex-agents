#!/usr/bin/env python3
"""Small stdlib platform boundary shared by self-contained Agent System tools.

POSIX keeps flock and permission bits. Windows uses byte-range locks, protected
current-user/SYSTEM DACLs for private state and a documented mode projection:
regular payload files are writable (0644), directories0755, because NTFS has no
POSIX executable bit. Content hashes remain exact on every platform.
"""
from __future__ import annotations
import argparse
import ctypes
import errno
from functools import lru_cache
import json
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import time

WINDOWS = os.name == 'nt'
LOCK_SH, LOCK_EX, LOCK_NB, LOCK_UN = 1, 2, 4, 8
_RESERVED = re.compile(r'^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)', re.I)


def configure_utf8():
    if WINDOWS:
        os.environ.setdefault('PYTHONUTF8', '1')
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        for stream in (sys.stdin,sys.stdout,sys.stderr):
            if hasattr(stream,'reconfigure'):
                stream.reconfigure(encoding='utf-8')


configure_utf8()


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value or '\0' in value:
        raise ValueError('Invalid portable relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('Unsafe portable relative path: ' + value)
    for part in path.parts:
        if any(c in part for c in ':<>"|?*') or part.endswith((' ', '.')) or _RESERVED.match(part) or any(ord(c) < 32 for c in part):
            raise ValueError('Windows-incompatible relative path: ' + value)
    return value


def is_link_or_reparse(path):
    try:
        info = Path(path).lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def safe_path(path):
    path = Path(os.path.abspath(os.fspath(path)))
    for part in reversed((path, *path.parents)):
        if is_link_or_reparse(part):
            raise ValueError('Linked/reparse path is not permitted: ' + str(part))
    return path


def _need(value, message):
    if not value: raise ValueError(message)


def file_identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink)


def opened_path(fd):
    """Return the kernel-bound final name, rather than resolve user paths."""
    if WINDOWS:
        from ctypes import wintypes
        import msvcrt
        api = getattr(opened_path, '_windows_api', None)
        if api is None:
            api = ctypes.WinDLL('kernel32', use_last_error=True).GetFinalPathNameByHandleW
            api.argtypes = (wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD)
            api.restype = wintypes.DWORD
            opened_path._windows_api = api
        handle = msvcrt.get_osfhandle(fd)
        size = api(handle, None, 0, 0)
        if not size: raise ctypes.WinError(ctypes.get_last_error())
        buffer = ctypes.create_unicode_buffer(size + 1)
        written = api(handle, buffer, len(buffer), 0)
        if not written: raise ctypes.WinError(ctypes.get_last_error())
        _need(written < len(buffer), 'Opened path grew during validation')
        return buffer.value
    if sys.platform == 'darwin':
        import fcntl
        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, b'\0' * 1024).split(b'\0', 1)[0])
    if sys.platform.startswith('linux'):
        try: return os.readlink('/proc/self/fd/' + str(fd))
        except FileNotFoundError: return None
    return None


def normal_handle_path(value):
    if WINDOWS:
        if value.startswith('\\\\?\\UNC\\'): value = '\\\\' + value[8:]
        elif value.startswith('\\\\?\\'): value = value[4:]
    return os.path.normcase(os.path.normpath(value))


def canonical_directory(path):
    """Check ancestors once and retain the actual directory's canonical name."""
    original = safe_path(path)
    observed = original.lstat()
    _need(stat.S_ISDIR(observed.st_mode), 'Expected a regular directory')
    result = original.resolve()
    safe_path(original)
    current, resolved = original.lstat(), result.lstat()
    identity = (observed.st_dev, observed.st_ino)
    _need((current.st_dev,current.st_ino) == identity and (resolved.st_dev,resolved.st_ino) == identity,
          'Directory changed during validation')
    if not WINDOWS:
        fd = os.open(result, os.O_RDONLY | getattr(os,'O_DIRECTORY',0) | getattr(os,'O_NOFOLLOW',0))
        try:
            current = os.fstat(fd)
            _need((current.st_dev,current.st_ino) == identity, 'Directory changed while opening')
            safe_path(original)
            actual = opened_path(fd)
            if actual is not None: result = Path(actual)
        finally: os.close(fd)
    return result


def hash_scanned(path, observed, limit):
    """Hash fresh bounded bytes after a guarded traversal, with FD binding.

    No file hashes or path approvals survive this read. The kernel-bound final
    path rejects a parent swapped after the tree scan, before any content read.
    The descriptor also keeps POSIX nonblocking/no-follow flags for FIFO/link
    replacement attacks. Unsupported POSIX FD queries retain the ancestor check.
    """
    path = Path(path)
    _need(stat.S_ISREG(observed.st_mode) and not getattr(observed,'st_file_attributes',0)&0x400,
          'Scanned member must be a regular non-reparse file')
    _need(observed.st_nlink == 1 and observed.st_size <= limit, 'Scanned member is linked or exceeds its bound')
    fd = os.open(path, os.O_RDONLY | getattr(os,'O_NOFOLLOW',0) | getattr(os,'O_NONBLOCK',0) | getattr(os,'O_BINARY',0))
    try:
        before = os.fstat(fd)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
              and before.st_size <= limit and file_identity(before) == file_identity(observed),
              'Scanned member changed before validation')
        actual = opened_path(fd)
        if actual is None: safe_path(path)
        else: _need(normal_handle_path(actual) == normal_handle_path(str(path)), 'Scanned member path changed during validation')
        hashed = hashlib.sha256()
        total = 0
        with os.fdopen(fd,'rb',closefd=False) as source:
            while chunk := source.read(1024 * 1024):
                total += len(chunk)
                _need(total <= limit and total <= before.st_size, 'Scanned member grew beyond its bound')
                hashed.update(chunk)
        _need(file_identity(os.fstat(fd)) == file_identity(before) and total == before.st_size,
              'Scanned member changed during validation')
        return {'sha256':hashed.hexdigest(),'size':total}
    finally: os.close(fd)


def sync_dir(path):
    """Flush directory metadata on POSIX; Windows relies on flushed file+rename.

    Windows does not expose a supported directory fsync through the Python CRT.
    This does not claim a power-loss guarantee; journals still reconcile actual
    state after process interruption. Do not remove the POSIX durability check.
    """
    if WINDOWS:
        return
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def flock(fd, operation):
    if not WINDOWS:
        import fcntl
        return fcntl.flock(fd, operation)
    import msvcrt
    fd = fd.fileno() if hasattr(fd, "fileno") else fd
    # All callers own a regular read/write lock file. Reserve the first byte;
    # lock operations restore the caller's file position and never edit its PID.
    position = os.lseek(fd, 0, os.SEEK_CUR)
    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, b'\0'); os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        if operation & LOCK_UN:
            return msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        shared = not (operation & LOCK_EX)
        nonblocking = operation & LOCK_NB
        mode = msvcrt.LK_NBRLCK if shared else msvcrt.LK_NBLCK
        while True:
            try:
                return msvcrt.locking(fd, mode, 1)
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if nonblocking:
                    raise BlockingIOError(errno.EAGAIN, 'Another process owns the lock') from exc
                time.sleep(.05)
    finally:
        os.lseek(fd, position, os.SEEK_SET)


def process_alive(pid):
    if type(pid) is not int or pid <= 0:
        raise ValueError('Positive process ID required')
    if not WINDOWS:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenProcess(0x100000 | 0x1000, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:  # no process with this ID
            return False
        if error == 5:   # protected process: never reclaim an unknown live owner
            return True
        raise ctypes.WinError(error)
    try:
        result = kernel.WaitForSingleObject(handle, 0)
        if result == 0x102:
            return True
        if result == 0:
            return False
        raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


@lru_cache(maxsize=1)
def _security():
    if not WINDOWS:
        raise OSError('Windows security API requested on another platform')
    from ctypes import wintypes as w
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    ptr = ctypes.c_void_p
    adv.OpenProcessToken.argtypes = (w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE))
    adv.OpenProcessToken.restype = w.BOOL
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = (w.HANDLE,)
    kernel.LocalFree.argtypes = (ptr,); kernel.LocalFree.restype = ptr
    adv.GetTokenInformation.argtypes = (w.HANDLE, ctypes.c_int, ptr, w.DWORD, ctypes.POINTER(w.DWORD))
    adv.GetTokenInformation.restype = w.BOOL
    adv.ConvertSidToStringSidW.argtypes = (ptr, ctypes.POINTER(w.LPWSTR)); adv.ConvertSidToStringSidW.restype = w.BOOL
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = (w.LPCWSTR,w.DWORD,ctypes.POINTER(ptr),ctypes.POINTER(w.DWORD)); adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = w.BOOL
    adv.GetSecurityDescriptorDacl.argtypes = (ptr,ctypes.POINTER(w.BOOL),ctypes.POINTER(ptr),ctypes.POINTER(w.BOOL)); adv.GetSecurityDescriptorDacl.restype=w.BOOL
    adv.SetNamedSecurityInfoW.argtypes = (w.LPWSTR,w.DWORD,w.DWORD,ptr,ptr,ptr,ptr);adv.SetNamedSecurityInfoW.restype=w.DWORD
    adv.GetNamedSecurityInfoW.argtypes = (w.LPCWSTR,w.DWORD,w.DWORD,ctypes.POINTER(ptr),ctypes.POINTER(ptr),ctypes.POINTER(ptr),ctypes.POINTER(ptr),ctypes.POINTER(ptr));adv.GetNamedSecurityInfoW.restype=w.DWORD
    adv.GetSecurityDescriptorControl.argtypes = (ptr,ctypes.POINTER(w.WORD),ctypes.POINTER(w.DWORD));adv.GetSecurityDescriptorControl.restype=w.BOOL
    adv.GetAclInformation.argtypes = (ptr,ptr,w.DWORD,ctypes.c_int);adv.GetAclInformation.restype=w.BOOL
    adv.GetAce.argtypes = (ptr,w.DWORD,ctypes.POINTER(ptr));adv.GetAce.restype=w.BOOL
    return adv,kernel


def _sid_text(sid):
    from ctypes import wintypes as w
    adv,kernel=_security();value=w.LPWSTR()
    if not adv.ConvertSidToStringSidW(sid,ctypes.byref(value)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:return value.value
    finally:kernel.LocalFree(ctypes.cast(value,ctypes.c_void_p))


@lru_cache(maxsize=1)
def current_user_sid():
    from ctypes import wintypes as w
    adv,kernel=_security();token=w.HANDLE();needed=w.DWORD()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(),8,ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        adv.GetTokenInformation(token,1,None,0,ctypes.byref(needed))
        buf=ctypes.create_string_buffer(needed.value)
        if not adv.GetTokenInformation(token,1,buf,len(buf),ctypes.byref(needed)):
            raise ctypes.WinError(ctypes.get_last_error())
        # TOKEN_USER begins with SID_AND_ATTRIBUTES, whose first field is PSID.
        return _sid_text(ctypes.cast(buf,ctypes.POINTER(ctypes.c_void_p))[0])
    finally:kernel.CloseHandle(token)


def make_private(path):
    path=safe_path(path)
    if not WINDOWS:
        os.chmod(path,0o700 if path.is_dir() else 0o600);return
    from ctypes import wintypes as w
    adv,kernel=_security();descriptor=ctypes.c_void_p();size=w.DWORD();present=w.BOOL();defaulted=w.BOOL();dacl=ctypes.c_void_p()
    inherit='OICI' if path.is_dir() else ''
    sddl='D:P(A;'+inherit+';FA;;;'+current_user_sid()+')(A;'+inherit+';FA;;;SY)'
    if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,ctypes.byref(descriptor),ctypes.byref(size)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not adv.GetSecurityDescriptorDacl(descriptor,ctypes.byref(present),ctypes.byref(dacl),ctypes.byref(defaulted)):
            raise ctypes.WinError(ctypes.get_last_error())
        code=adv.SetNamedSecurityInfoW(str(path),1,0x80000004,None,None,dacl,None)
        if code:raise ctypes.WinError(code)
    finally:kernel.LocalFree(descriptor)
    assert_private(path)


def private_acl_report(path):
    path=safe_path(path)
    if not WINDOWS:
        mode=stat.S_IMODE(path.stat().st_mode)
        return {'private':not bool(mode&0o077),'policy':'posix-owner-only','mode':mode}
    from ctypes import wintypes as w
    adv,kernel=_security();descriptor=ctypes.c_void_p();dacl=ctypes.c_void_p()
    code=adv.GetNamedSecurityInfoW(str(path),1,4,None,None,ctypes.byref(dacl),None,ctypes.byref(descriptor))
    if code:raise ctypes.WinError(code)
    class AclSize(ctypes.Structure):_fields_=[('AceCount',w.DWORD),('AclBytesInUse',w.DWORD),('AclBytesFree',w.DWORD)]
    try:
        control=w.WORD();revision=w.DWORD()
        if not adv.GetSecurityDescriptorControl(descriptor,ctypes.byref(control),ctypes.byref(revision)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not dacl.value or not control.value&0x1000:
            return {'private':False,'policy':'windows-protected-dacl','reason':'unprotected-or-null-dacl'}
        size=AclSize()
        if not adv.GetAclInformation(dacl,ctypes.byref(size),ctypes.sizeof(size),2):raise ctypes.WinError(ctypes.get_last_error())
        sid=current_user_sid();allowed={sid,'S-1-5-18'};user_full=False;aces=[]
        for i in range(size.AceCount):
            ace=ctypes.c_void_p()
            if not adv.GetAce(dacl,i,ctypes.byref(ace)):raise ctypes.WinError(ctypes.get_last_error())
            header=ctypes.string_at(ace,4);kind=header[0]
            if kind==1:continue  # a DENY cannot broaden access
            if kind!=0:return {'private':False,'policy':'windows-protected-dacl','reason':'unsupported-ace'}
            mask=ctypes.c_uint32.from_address(ace.value+4).value;principal=_sid_text(ace.value+8)
            aces.append({'sid':principal,'mask':mask})
            if principal not in allowed and mask:return {'private':False,'policy':'windows-protected-dacl','reason':'foreign-allow-ace'}
            if principal==sid and mask&0x1f01ff==0x1f01ff:user_full=True
        return {'private':user_full,'policy':'windows-protected-current-user-and-system','aces':aces}
    finally:kernel.LocalFree(descriptor)


def assert_private(path):
    report=private_acl_report(path)
    if not report['private']:raise PermissionError('Private owner-only permissions required: '+str(path))
    return report


def set_mode(path,mode):
    path=safe_path(path)
    if WINDOWS:
        if mode in (0o600,0o700):return make_private(path)
        os.chmod(path,stat.S_IREAD | (stat.S_IWRITE if mode&0o200 else 0))
    else:os.chmod(path,mode)



def fchmod(fd, mode):
    if not WINDOWS:
        return os.fchmod(fd, mode)
    import msvcrt
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetFinalPathNameByHandleW.argtypes = (w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD)
    kernel.GetFinalPathNameByHandleW.restype = w.DWORD
    handle = msvcrt.get_osfhandle(fd)
    size = kernel.GetFinalPathNameByHandleW(handle, None, 0, 0)
    if not size: raise ctypes.WinError(ctypes.get_last_error())
    buffer = ctypes.create_unicode_buffer(size+1)
    if not kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0):
        raise ctypes.WinError(ctypes.get_last_error())
    return set_mode(buffer.value, mode)


def project_mode(mode,is_directory=False):
    if not WINDOWS:return mode
    return (0o755 if is_directory else 0o644) if mode&0o200 else (0o555 if is_directory else 0o444)


def file_mode(path,expected=None):
    info=Path(path).lstat()
    if not WINDOWS:return stat.S_IMODE(info.st_mode)
    if expected in (0o600,0o700):
        assert_private(path);return expected
    return project_mode(stat.S_IMODE(info.st_mode),stat.S_ISDIR(info.st_mode))


def mode_matches(path,expected):
    return file_mode(path,expected)==(expected if expected in (0o600,0o700) else project_mode(expected,Path(path).is_dir()))


def codex_command(candidate=None):
    """Return an executable argv prefix, never execute a Windows batch shell."""
    candidate=candidate or shutil.which('codex.exe') or shutil.which('codex')
    if not candidate:return None
    if not Path(candidate).is_absolute(): candidate=shutil.which(candidate) or candidate
    path=Path(candidate)
    if not WINDOWS:
        # npm's POSIX entry is a codex.js symlink with /usr/bin/env node.
        # Agent System owns an explicit runtime; project PATH remains unchanged.
        node=os.environ.get('AGENT_SYSTEM_NODE')
        if node:
            resolved=path.resolve()
            if tuple(resolved.parts[-5:])==('node_modules','@openai','codex','bin','codex.js') and resolved.is_file():
                metadata=resolved.parent.parent/'package.json'
                if metadata.is_file() and metadata.stat().st_size<=1024*1024:
                    manifest=json.loads(safe_path(metadata).read_text(encoding='utf8'))
                    bins=manifest.get('bin',{})
                    if manifest.get('name')=='@openai/codex' and isinstance(bins,dict) and bins.get('codex') in ('bin/codex.js','./bin/codex.js'):
                        return [str(node),str(safe_path(resolved))]
        return [str(path)]
    if path.suffix.lower() not in ('.cmd','.bat','.ps1'):
        return [str(path)]
    folder=path.resolve().parent
    js=folder/'node_modules/@openai/codex/bin/codex.js'
    if not js.is_file():
        raise ValueError('Windows Codex wrapper needs the official @openai/codex package; use native codex.exe or reinstall the official CLI')
    for package in ('codex-win32-arm64','codex-win32-x64','codex-windows-arm64','codex-windows-x64'):
        base=folder/'node_modules/@openai'/package/'vendor'
        if base.is_dir():
            matches=sorted(base.glob('*/codex/codex.exe'))
            if len(matches)==1:return [str(safe_path(matches[0]))]
    node=os.environ.get('AGENT_SYSTEM_NODE') or shutil.which('node.exe') or shutil.which('node')
    if not node:raise ValueError('Official npm Codex needs node.exe; use native codex.exe or install Node')
    return [str(node),str(safe_path(js))]


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--make-private',type=Path);g.add_argument('--assert-private',type=Path);g.add_argument('--is-alive',type=int)
    a=p.parse_args(argv)
    if a.make_private is not None:make_private(a.make_private);result=private_acl_report(a.make_private)
    elif a.assert_private is not None:result=assert_private(a.assert_private)
    else:result={'alive':process_alive(a.is_alive)}
    print(json.dumps(result,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
