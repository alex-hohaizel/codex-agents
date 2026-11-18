#!/usr/bin/env python3
"""Native CI tooling and buyer/browser acceptance; all state stays in RUNNER_TEMP."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def npm_command():
    node = Path(shutil.which('node') or '').resolve()
    candidates = [node.parent / 'node_modules/npm/bin/npm-cli.js',
                  node.parent.parent / 'lib/node_modules/npm/bin/npm-cli.js']
    npm = shutil.which('npm')
    if npm and Path(npm).resolve().suffix == '.js':
        candidates.append(Path(npm).resolve())
    cli = next((path for path in candidates if path.is_file()), None)
    require(node.is_file() and cli, 'The pinned build Node/npm tools are unavailable')
    return [str(node), str(cli)]


def tools(output):
    require(not output.exists(), 'Choose a new test tooling directory')
    output.mkdir(parents=True)
    command = npm_command()
    subprocess.run([*command, 'install', '--global', '--prefix', str(output), '--ignore-scripts',
                    '--no-audit', '--no-fund', '@openai/codex@0.166.0'], check=True)
    codex = output / ('codex.cmd' if os.name == 'nt' else 'bin/codex')
    require(codex.is_file(), 'Pinned Codex CLI entry is missing')
    if os.name == 'nt':
        candidates = [Path(os.environ.get(name, 'C:/Program Files')) / 'Microsoft/Edge/Application/msedge.exe'
                      for name in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA')]
        browser = next((path for path in candidates if path.is_file()), None)
        require(browser, 'The standard Windows runner must include Microsoft Edge; no paid or emulated runner fallback is used')
    else:
        subprocess.run([*command, 'install', '--global', '--prefix', str(output), '--ignore-scripts',
                        '--no-audit', '--no-fund', 'playwright@1.56.1'], check=True)
        playwright = output / 'lib/node_modules/playwright'
        if not playwright.is_dir():
            playwright = output / 'node_modules/playwright'
        environment = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(output / 'browsers'))
        argv = [command[0], str(playwright / 'cli.js'), 'install', 'chromium']
        if sys.platform == 'linux':
            argv.append('--with-deps')
        subprocess.run(argv, check=True, env=environment)
        browser = Path(subprocess.check_output([command[0], '-e',
            'console.log(require(process.argv[1]).chromium.executablePath())', str(playwright)],
            text=True, env=environment).strip())
        require(browser.is_file(), 'Pinned test Chromium is unavailable')
    result = {'codex': str(codex), 'browser': str(browser), 'codex_version': '0.166.0',
              'browser_provider': 'standard-runner Microsoft Edge' if os.name == 'nt' else 'playwright1.56.1 Chromium',
              'node': command[0], 'npm_cli': command[1]}
    write(output / 'TOOLS.json', result)
    return result


def environment(home, node, python):
    allowed = {'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TMP', 'TEMP', 'TMPDIR',
               'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'NODE_EXTRA_CA_CERTS'}
    result = {(key.upper() if os.name == 'nt' else key): value for key, value in os.environ.items() if key.upper() in allowed}
    result.update(HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / '.codex'),
        APPDATA=str(home / 'AppData/Roaming'), LOCALAPPDATA=str(home / 'AppData/Local'),
        XDG_DATA_HOME=str(home / '.local/share'), XDG_CONFIG_HOME=str(home / '.config'),
        AGENT_SYSTEM_NODE=str(node), AGENT_SYSTEM_PYTHON=str(python),
        PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    return result


def sanitize(value):
    if isinstance(value, dict):
        return {key: ('[REDACTED]' if key.lower() in {'control_key', 'csrf_token', 'launch_token', 'session',
            'cookie', 'authorization', 'access_token', 'refresh_token', 'password', 'secret'} else sanitize(item))
            for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return re.sub(r'([#?&](?:launch|atelier_launch)=)[^\s"&]+', r'\1[REDACTED]', value)
    return value


def collect(output):
    """Upload only reviewed receipts/screens, never HOME, browser profiles or ready tokens."""
    public = output / 'public-proof'
    public.mkdir(exist_ok=True)
    selected = [output / 'backend/native-acceptance.json',
                output / 'gui-proof/BROWSER-OBSERVATION.json', output / 'gui-proof/BROWSER-FAILURE.json',
                output / 'NATIVE-CI.json', output / 'GUI-RECONCILIATION-REQUIRED.json']
    selected += list((output / 'backend/commands').glob('*.json'))
    index = []
    for path in selected:
        if not path.is_file():
            continue
        rel = path.relative_to(output)
        dest = public / rel
        write(dest, sanitize(json.loads(path.read_text(encoding='utf8'))))
        index.append({'file': rel.as_posix(), 'original_sha256': sha(path), 'redacted_sha256': sha(dest)})
    for path in (output / 'gui-proof').glob('GUI-*.png'):
        dest = public / 'gui-proof' / path.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, dest)
        index.append({'file': dest.relative_to(public).as_posix(), 'sha256': sha(dest)})
    write(public / 'PROOF-INVENTORY.json', {'schema': 'codex-agents.redacted-native-proof/1',
        'policy': 'Only synthetic acceptance receipts and page screenshots. No HOME, browser profile, ready token or owner credentials.', 'files': index})


def remove_owned_cache(path):
    def writable(operation, target, error):
        os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
        operation(target)
    if path.exists():
        shutil.rmtree(path, onerror=writable)


def validate_backend(report, source, archive_sha256):
    require(report.get('status') == 'passed' and report.get('source_clean') is True
            and report.get('source_commit') == source and report.get('archive_sha256') == archive_sha256,
            'Native evidence does not match the clean exact source and received archive bytes')


def validate_pair(report, observed, source, archive_sha256):
    validate_backend(report, source, archive_sha256)
    require(observed.get('status') == 'passed' and observed.get('package', {}).get('source_commit') == source
            and observed.get('package', {}).get('manifest_sha256') == report['package_manifest_sha256'],
            'Browser evidence belongs to different package bytes or is incomplete')


def check(archive, output, codex, browser):
    require(not output.exists(), 'Choose a new private native CI output directory')
    output.mkdir(parents=True, mode=0o700)
    backend = output / 'backend'
    engine = None
    status = 1
    try:
        subprocess.run([sys.executable, '-B', str(REPO / 'scripts/native_installer_acceptance.py'),
                        '--archive', str(archive), '--output', str(backend), '--codex', str(codex)], check=True)
        report = json.loads((backend / 'native-acceptance.json').read_text(encoding='utf8'))
        source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
        validate_backend(report, source, sha(archive))
        node, python = Path(report['runtime']['node']['executable']), Path(report['runtime']['python']['executable'])
        package = next(path for path in (backend / 'received package').iterdir() if (path / 'product-manifest.json').is_file())
        # Backend uninstall/rollback has completed and its receipts are retained.
        # Remove only its disposable full-package cache before the separate GUI
        # buyer install, so Universal is not retained three times simultaneously.
        cache = backend / 'Покупець native & test HOME/.local/share/codex-agent-system/packages'
        require(cache.is_relative_to(backend), 'Cache escaped the owned acceptance root')
        remove_owned_cache(cache)
        gui = output / 'gui-private'
        gui.mkdir(mode=0o700)
        home = gui / 'Покупець GUI & spaces HOME'
        home.mkdir(mode=0o700)
        state = home / '.local/share/codex-agent-system'
        env = environment(home, node, python)
        for folder in (gui, home):
            subprocess.run([str(python), '-I', '-X', 'utf8', '-B', str(package / 'setup/platform_support.py'), '--make-private', str(folder)], env=env, check=True, capture_output=True)
        ready = gui / 'ready.json'
        with (gui / 'engine.log').open('wb') as log:
            engine = subprocess.Popen([str(node), str(package / 'setup/web.mjs'), '--package', str(package),
                '--python', str(python), '--home', str(home), '--state', str(state), '--codex', str(codex),
                '--ready', str(ready), '--no-open'], env=env, cwd=package, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 30
            while not ready.exists() and engine.poll() is None and time.monotonic() < deadline:
                time.sleep(.05)
            require(ready.exists() and engine.poll() is None, 'Received package GUI did not become ready')
            subprocess.run([str(node), str(REPO / 'commercial/tests/gui/native-browser.mjs'), '--ready-file', str(ready),
                '--output', str(output / 'gui-proof'), '--browser', str(browser), '--python', str(python),
                '--expect-codex-version', '0.166.0', '--timeout-seconds', '600'], env=env, cwd=REPO, check=True)
            require(engine.wait(timeout=20) == 0, 'GUI did not exit after the browser shutdown button')
        observed = json.loads((output / 'gui-proof/BROWSER-OBSERVATION.json').read_text(encoding='utf8'))
        validate_pair(report, observed, source, sha(archive))
        write(output / 'NATIVE-CI.json', {'schema': 'codex-agents.native-installer-ci/1', 'status': 'passed',
            'archive_sha256': report['archive_sha256'], 'source_commit': source, 'target': report['native']['target'],
            'harness_sha256': sha(REPO / 'scripts/native_installer_acceptance.py'),
            'browser_driver_sha256': observed['driver_sha256'], 'backend_and_real_browser': True})
        status = 0
    finally:
        if engine and engine.poll() is None:
            # Do not classify or replay an interrupted GUI mutation. The hosted
            # ephemeral runner will clean its own process tree after job exit.
            write(output / 'GUI-RECONCILIATION-REQUIRED.json', {'pid': engine.pid, 'status': 'unverified',
                'next': 'Inspect the private engine journal before any retry; no mutation is replayed automatically.'})
        collect(output)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    setup = sub.add_parser('tools'); setup.add_argument('--output', type=Path, required=True)
    run = sub.add_parser('check'); run.add_argument('--archive', type=Path, required=True)
    run.add_argument('--output', type=Path, required=True); run.add_argument('--codex', type=Path, required=True)
    run.add_argument('--browser', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'tools':
            print(json.dumps(tools(args.output.resolve()), indent=2)); return 0
        return check(args.archive.resolve(), args.output.resolve(), args.codex.resolve(), args.browser.resolve())
    except (OSError, ValueError, subprocess.SubprocessError, StopIteration) as error:
        print(json.dumps({'status': 'failed', 'reason': str(error)}), file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
