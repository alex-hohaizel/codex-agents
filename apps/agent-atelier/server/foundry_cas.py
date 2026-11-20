"""Source-pinned adapter: compare state inside the native controller's own lock.

The native main/parser/validation/writes remain unchanged. This adapter adds a
compare-and-set admission check at the yielded native exclusive-lock boundary.
It never runs a model, shell command or external provider operation.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types
_support = None


def support(expected):
    path = Path(__file__).with_name('platform_support.py')
    for entry in (path, *path.parents):
        info = entry.lstat()
        if stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400):
            raise ValueError('Linked/reparse platform adapter is not permitted')
    if not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('Unlinked regular platform adapter required')
    raw = path.read_bytes()
    if not expected or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Reviewed platform adapter changed')
    module = types.ModuleType('atelier_platform_support')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def closure_check(root, operation_dir, expected):
    raw = (operation_dir / 'closure.json').read_bytes()
    files = json.loads(raw)
    canonical = json.dumps(files, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    if hashlib.sha256(canonical).hexdigest() != expected:
        raise ValueError('Reviewed controller manifest changed')
    observed = {}
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if any(p in {'tests', '__pycache__'} for p in relative.parts) or path.name.startswith('test_') or path.suffix in {'.pyc', '.pyo'}:
            continue
        if _support.is_link_or_reparse(path):
            raise ValueError('Linked controller closure entry')
        if path.is_file():
            observed[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise ValueError('Irregular controller closure entry')
    if observed != files:
        raise ValueError('Reviewed controller closure changed')


def invoke(args, operation_dir):
    if (operation_dir / 'revoked').exists():
        raise ValueError('Native invocation was revoked during reconciliation')
    path = Path(args.script).absolute()
    closure_check(path.parent.parent, operation_dir, args.closure_sha256)
    if _support.is_link_or_reparse(path) or not path.is_file():
        raise ValueError('Unlinked trusted controller required')
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != args.script_sha256:
        raise ValueError('Controller source changed before execution')
    module = types.ModuleType('atelier_pinned_foundry')
    module.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), module.__dict__)
    native_lock = module.lock

    @contextmanager
    def admitted_lock(root, create=False):
        with native_lock(root, create) as home:
            closure_check(path.parent.parent, operation_dir, args.closure_sha256)
            state = home / 'state.json'
            actual = module.sha(state) if state.exists() else 'missing'
            if actual != args.expected_state:
                raise ValueError('Native state changed since the reviewed preview')
            if args.expected_choice:
                helper = path.with_name("production_choices.py")
                engine = types.ModuleType("atelier_pinned_choice")
                engine.__file__ = str(helper)
                exec(compile(helper.read_bytes(), str(helper), "exec"), engine.__dict__)
                engine.verify_project(Path(root), args.choice_phase, expected_sha256=args.expected_choice)
            yield home

    module.lock = admitted_lock
    native_args = args.native_args
    if native_args[:1] == ['--']:
        native_args = native_args[1:]
    sys.argv = [str(path), *native_args]
    return module.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--operation-dir', required=True)
    parser.add_argument('--platform-support-sha256', required=True)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--revoke', action='store_true')
    parser.add_argument('--script')
    parser.add_argument('--script-sha256')
    parser.add_argument('--closure-sha256')
    parser.add_argument('--expected-state')
    parser.add_argument('--expected-choice')
    parser.add_argument('--choice-phase', choices=('implement', 'scale', 'accept'))
    parser.add_argument('native_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    global _support
    _support = support(args.platform_support_sha256)
    directory = _support.safe_path(args.operation_dir)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Owned operation directory required')
    lock_path = _support.safe_path(directory / 'operation.lock')
    descriptor = os.open(lock_path, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, 'r+') as lease:
        if not stat.S_ISREG(os.fstat(lease.fileno()).st_mode) or os.fstat(lease.fileno()).st_nlink != 1:
            raise ValueError('Regular owned operation lease required')
        try:
            _support.flock(lease, _support.LOCK_EX | (_support.LOCK_NB if args.inspect or args.revoke else 0))
        except BlockingIOError as error:
            raise ValueError('Previous native writer is still active') from error
        if args.revoke:
            with open(directory / 'revoked', 'w') as marker:
                marker.write('Owner confirmed reconciliation; never replay this invocation.\n')
                marker.flush()
                os.fsync(marker.fileno())
            _support.sync_dir(directory)
        if args.inspect or args.revoke:
            print(json.dumps({'quiescent': True, 'revoked': (directory / 'revoked').exists()}))
            return 0
        if not all([args.script, args.script_sha256, args.closure_sha256, args.expected_state]):
            raise ValueError('Exact reviewed invocation required')
        return invoke(args, directory)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error), 'executed': False}), file=sys.stderr)
        raise SystemExit(2)
