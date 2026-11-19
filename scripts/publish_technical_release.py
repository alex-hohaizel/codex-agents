#!/usr/bin/env python3
"""Manually publish exact-main accepted technical artifacts; never issue a sale.

All validation and attestation checks precede the first remote mutation. A failed
write is reconciled against GitHub once; an unknown effect is left for a later
explicit invocation, never overwritten or blindly retried.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
REPO = 'alex-hohaizel/codex-agents'
NATIVE = '.github/workflows/universal-installers.yml'
SOURCE = '.github/workflows/validate.yml'
TARGETS = {'darwin-arm64', 'darwin-x64', 'win32-arm64', 'win32-x64', 'linux-arm64', 'linux-x64'}
LABELS = {'darwin-arm64': 'macOS-arm64', 'darwin-x64': 'macOS-x64',
          'win32-arm64': 'Windows-arm64', 'win32-x64': 'Windows-x64',
          'linux-arm64': 'Linux-arm64', 'linux-x64': 'Linux-x64'}


def need(value, message):
    if not value:
        raise ValueError(message)


def stream_sha(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(chunk)
    return digest.hexdigest()


def sha(path):
    with path.open('rb') as stream:
        return stream_sha(stream)


def read(path):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= 32 * 1024 * 1024,
         'Missing or unsafe bounded record: ' + path.name)
    return json.loads(path.read_text(encoding='utf8'))


def validate_run(run, expected, workflow):
    need(run.get('repository', {}).get('full_name') == REPO
         and run.get('head_repository', {}).get('full_name') == REPO
         and run.get('event') == 'push' and run.get('head_branch') == 'main'
         and run.get('head_sha') == expected and run.get('path') == workflow
         and run.get('status') == 'completed' and run.get('conclusion') == 'success',
         'Run is not a successful exact-source main push for ' + workflow)


def validate_dispatch(env, expected):
    need(re.fullmatch('[a-f0-9]{40}', expected), 'Expected a full lowercase source commit')
    need(env.get('GITHUB_REPOSITORY') == REPO and env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
         and env.get('GITHUB_REF') == 'refs/heads/main' and env.get('GITHUB_SHA') == expected,
         'Publication is limited to an explicit dispatch on this exact main source')


def check_sums(directory, name, expected):
    lines = (directory / name).read_text(encoding='utf8').splitlines()
    rows = {}
    for line in lines:
        match = re.fullmatch(r'([a-f0-9]{64})  ([A-Za-z0-9_.-]+)', line)
        need(match and match[2] not in rows, 'Malformed or duplicate checksum line')
        rows[match[2]] = match[1]
    need(rows == {path.name: sha(path) for path in expected}, 'Checksum closure differs: ' + name)


def verified_file(directory, row):
    name = row.get('name', '')
    need(re.fullmatch(r'[A-Za-z0-9_.-]+', name), 'Unsafe subject name')
    path = directory / name
    need(path.is_file() and not path.is_symlink() and path.stat().st_size == row.get('size')
         and sha(path) == row.get('sha256'), 'Subject differs from build receipt: ' + name)
    return path


def proof_record(archive, name):
    info = archive.getinfo(name)
    need(info.file_size <= 32 * 1024 * 1024, 'Oversized native proof record')
    return json.loads(archive.read(info))


def verify_native_proofs(path, expected, pairs):
    observed = set()
    limitations = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        need(len(names) == len(set(names)) and len(names) <= 10000, 'Duplicate or excessive proof entries')
        for name in names:
            parts = PurePosixPath(name)
            need(not parts.is_absolute() and not {'.', '..'}.intersection(parts.parts)
                 and '\\' not in name and parts.suffix in ('.json', '.png'), 'Unsafe native proof member')
        receipts = [name for name in names if name.endswith('/NATIVE-CI.json')]
        need(len(receipts) == 12, 'Exactly twelve native acceptance receipts are required')
        for name in receipts:
            prefix = name[:-len('NATIVE-CI.json')]
            ci = proof_record(archive, name)
            pair = (ci.get('archive_sha256'), ci.get('target'))
            need(ci.get('status') == 'passed' and ci.get('source_commit') == expected
                 and ci.get('backend_and_real_browser') is True
                 and ci.get('workbench_browser_transport_verified') is True
                 and ci.get('purchase_document_gui_verified') is True
                 and ci.get('purchase_document_inherited_without_reimport') is True
                 and pair in pairs and pair not in observed, 'Invalid, duplicate, or foreign native acceptance')
            if ci['target'].startswith('win32-'):
                need(ci.get('windows_restricted_non_admin_verified') is True, 'Windows non-admin proof is missing')
            backend = proof_record(archive, prefix + 'backend/native-acceptance.json')
            gui = proof_record(archive, prefix + 'gui-proof/BROWSER-OBSERVATION.json')
            workbench = proof_record(archive, prefix + 'workbench-proof/WORKBENCH-BROWSER-PRIVACY.json')
            purchase = proof_record(archive, prefix + 'GUI-PURCHASE-INHERITANCE.json')
            need(backend.get('status') == 'passed' and backend.get('source_clean') is True
                 and backend.get('source_commit') == expected and backend.get('archive_sha256') == pair[0]
                 and backend.get('native', {}).get('target') == pair[1], 'Backend proof binding differs')
            manifest = backend['package_manifest_sha256']
            need(gui.get('status') == 'passed' and gui.get('package', {}).get('source_commit') == expected
                 and gui['package'].get('manifest_sha256') == manifest
                 and gui.get('browser_cleanup', {}).get('root_exit_observed') is True
                 and gui['browser_cleanup'].get('profile_removed') is True,
                 'Installer browser proof binding or cleanup differs')
            document = gui.get('purchase_document', {})
            need(document.get('retained_bytes_verified') is True and document.get('old_plan_rejected') is True
                 and document.get('selection_clears_approved_plan') is True
                 and re.fullmatch('[a-f0-9]{64}', document.get('sha256', ''))
                 and purchase.get('status') == 'passed' and purchase.get('source_commit') == expected
                 and purchase.get('archive_sha256') == pair[0]
                 and purchase.get('original_document_sha256') == document['sha256']
                 and purchase.get('after_browser_shutdown') is True and purchase.get('entitlement_argument_supplied') is False,
                 'Browser purchase document was not retained and inherited by a fresh setup session')
            need(workbench.get('status') == 'passed' and workbench.get('source', {}).get('source_commit') == expected
                 and workbench['source'].get('package_manifest_sha256') == manifest
                 and workbench.get('browser_cleanup', {}).get('parent_exit_observed') is True
                 and workbench['browser_cleanup'].get('private_root_removed') is True,
                 'Workbench browser proof binding or cleanup differs')
            need(ci.get('environment_limits', []) == workbench.get('limitations', []), 'Codec limitations were lost')
            limitations += [{'target': pair[1], 'archive_sha256': pair[0], **row} for row in ci.get('environment_limits', [])]
            inventory = proof_record(archive, prefix + 'PROOF-INVENTORY.json')
            for row in inventory['files']:
                member = prefix + row['file']
                need(member in names and hashlib.sha256(archive.read(member)).hexdigest()
                     == row.get('redacted_sha256', row.get('sha256')), 'Durable redacted proof digest differs')
            observed.add(pair)
    need(observed == pairs, 'Native evidence does not cover all seven exact archives and Universal targets')
    return limitations


def installer_subjects(directory, release, expected):
    index = read(directory / 'INSTALLER-BUILD.json')
    version = release['repository_version']
    need(index.get('schema') == 'codex-agents.installer-release/1' and index.get('source_clean') is True
         and index.get('source_commit') == expected and index.get('product_version') == version,
         'Installer index is not the accepted exact source')
    need(len(index['files']) == 7, 'All seven ready installers are required')
    subjects, pairs, seen = [], set(), set()
    for row in index['files']:
        path = verified_file(directory, row)
        targets = row['platforms']
        need(isinstance(targets, list) and len(targets) == len(set(targets))
             and (len(targets) == 1 or set(targets) == TARGETS) and set(targets) <= TARGETS,
             'Unexpected installer platform mapping')
        label = 'Universal' if len(targets) == 6 else LABELS[targets[0]]
        need(path.name == f'Agent-System-{version}-{label}.zip' and path.name not in seen,
             'Unexpected or duplicate installer filename')
        with zipfile.ZipFile(path) as archive:
            manifests = [name for name in archive.namelist() if name.count('/') == 1 and name.endswith('/product-manifest.json')]
            need(len(manifests) == 1, 'Missing installer product manifest')
            manifest = proof_record(archive, manifests[0])
            need(manifest.get('source_commit') == expected and manifest.get('source_clean') is True
                 and manifest.get('product_version') == version
                 and set(manifest.get('portable_runtimes', {})) == set(targets), 'Installer manifest binding differs')
        pairs.update((row['sha256'], target) for target in targets)
        subjects.append(path); seen.add(path.name)
    need(len(pairs) == 12 and len(seen) == 7, 'Six native packages and Universal are required')
    index_path = directory / 'INSTALLER-BUILD.json'
    check_sums(directory, 'INSTALLER-SHA256SUMS', [*subjects, index_path])
    proof = directory / 'NATIVE-ACCEPTANCE.zip'
    check_sums(directory, 'NATIVE-ACCEPTANCE-SHA256SUMS', [proof])
    limits = verify_native_proofs(proof, expected, pairs)
    subjects += [index_path, directory / 'INSTALLER-SHA256SUMS', proof, directory / 'NATIVE-ACCEPTANCE-SHA256SUMS']
    need({p.name for p in directory.iterdir()} == {p.name for p in subjects}, 'Unexpected accepted installer artifact files')
    return subjects, limits


def source_subjects(directory, release, root):
    record = read(directory / 'BUILD.json')
    need(record.get('schema') == 'codex-agents.build/1' and record.get('repository_branch') == 'main'
         and record.get('repository_version') == release['repository_version']
         and record.get('suite_version') == release['suite_version'] and len(record['files']) == 2,
         'Source bundle receipt differs from the current release')
    subjects = []
    for mode, row in zip(('WORK', 'CODEX'), record['files']):
        path = verified_file(directory, row)
        need(path.name == f"Agent_System_{release['suite_version']}_{mode}.zip", 'Unexpected source bundle filename')
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist(); need(len(names) == len(set(names)) and len(names) <= 30000, 'Invalid source bundle inventory')
            descriptor = proof_record(archive, 'PACKAGE.json')
            need(descriptor.get('mode') == mode and descriptor.get('repository_branch') == 'main'
                 and descriptor.get('repository_version') == release['repository_version']
                 and descriptor.get('suite_version') == release['suite_version'], 'Source package descriptor differs')
            need(proof_record(archive, 'releases/current.json') == release, 'Source package release record differs')
            for info in archive.infolist():
                name = info.filename
                if name in ('PACKAGE.json', 'PACKAGE_README.md'):
                    continue
                parts = PurePosixPath(name)
                need(not parts.is_absolute() and not {'.', '..'}.intersection(parts.parts) and '\\' not in name
                     and info.file_size <= 256 * 1024 * 1024, 'Unsafe source bundle entry')
                original = root / name
                need(original.is_file() and not original.is_symlink(), 'Source bundle member is absent from exact checkout')
                with archive.open(info) as stream:
                    need(stream_sha(stream) == sha(original), 'Source bytes differ from exact checkout: ' + name)
        subjects.append(path)
    check_sums(directory, 'SHA256SUMS', subjects)
    subjects += [directory / 'BUILD.json', directory / 'SHA256SUMS']
    need({p.name for p in directory.iterdir()} == {p.name for p in subjects}, 'Unexpected source artifact files')
    return subjects


class GitHub:
    def __init__(self, work):
        self.work = work

    def command(self, args, *, timeout=120, optional=False, output=None, json_result=True):
        with output.open('wb') if output else tempfile.TemporaryFile() as stream:
            result = subprocess.run(['gh', *args], stdout=stream, stderr=subprocess.PIPE, timeout=timeout)
            if result.returncode:
                error = result.stderr.decode('utf8', 'replace')
                if optional and '(HTTP 404)' in error:
                    return None
                raise ValueError('GitHub command failed; reconcile its target before retry: ' + error[-1500:])
            if output:
                return None
            stream.seek(0); raw = stream.read()
        return (json.loads(raw) if json_result else raw.decode('utf8', 'replace')) if raw else None

    def api(self, path, *, method='GET', data=None, optional=False):
        args = ['api', f'repos/{REPO}/{path}', '--method', method]
        if data is None:
            return self.command(args, optional=optional)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf8', dir=self.work, suffix='.json') as body:
            json.dump(data, body); body.flush()
            return self.command([*args, '--input', body.name])

    def main_is(self, expected):
        need(self.api('git/ref/heads/main')['object']['sha'] == expected, 'Current remote main advanced; do not publish stale source')

    def tag_commit(self, tag):
        ref = self.api('git/ref/tags/' + tag, optional=True)
        if ref is None:
            return None
        obj = ref['object']
        for _ in range(5):
            if obj['type'] == 'commit':
                return obj['sha']
            need(obj['type'] == 'tag', 'Unsupported tag object')
            obj = self.api('git/tags/' + obj['sha'])['object']
        raise ValueError('Tag nesting exceeds the release guard')

    def download(self, run_id, name, directory):
        matches = []
        for page in range(1, 20):
            batch = self.api(f'actions/runs/{run_id}/artifacts?per_page=100&page={page}')['artifacts']
            matches += [row for row in batch if row['name'] == name]
            if len(batch) < 100:
                break
        need(len(matches) == 1 and matches[0].get('expired') is False, 'Missing, duplicate, or expired required artifact: ' + name)
        directory.mkdir()
        self.command(['run', 'download', str(run_id), '--repo', REPO, '--name', name, '--dir', str(directory)], timeout=1200, json_result=False)
        return {'id': matches[0]['id'], 'name': name, 'digest': matches[0].get('digest')}

    def verify_attestation(self, path, expected, workflow):
        # The exact certificate SAN pins the workflow and ref. gh accepts only one identity selector.
        self.command(['attestation', 'verify', str(path), '--repo', REPO,
                      '--source-ref', 'refs/heads/main', '--source-digest', expected,
                      '--signer-digest', expected,
                      '--cert-identity', 'https://github.com/' + REPO + '/' + workflow + '@refs/heads/main',
                      '--deny-self-hosted-runners', '--format', 'json'], timeout=180)

    def release(self, tag):
        # List releases as the owner: the public tag lookup is not a reliable
        # draft lookup. Unknown transport/authentication errors are never absence.
        matches = []
        for page in range(1, 20):
            rows = self.api(f'releases?per_page=100&page={page}')
            matches += [row for row in rows if row.get('tag_name') == tag]
            if len(rows) < 100:
                need(len(matches) <= 1, 'Multiple releases use the expected tag')
                return matches[0] if matches else None
        raise ValueError('Release list exceeds the bounded draft lookup')

    def assets(self, release_id):
        rows = []
        for page in range(1, 20):
            batch = self.api(f'releases/{release_id}/assets?per_page=100&page={page}')
            rows += batch
            if len(batch) < 100:
                return rows
        raise ValueError('Release asset list exceeds guard')

    def same_asset(self, asset, path):
        need(asset.get('state') == 'uploaded' and asset.get('size') == path.stat().st_size,
             'Existing remote asset size/state differs; it will not be overwritten: ' + path.name)
        expected = 'sha256:' + sha(path)
        if asset.get('digest'):
            need(asset['digest'] == expected, 'Existing remote asset digest differs; it will not be overwritten: ' + path.name)
        else:
            # Older GitHub assets may lack a digest; verify their actual bytes.
            with tempfile.TemporaryDirectory(dir=self.work) as directory:
                received = Path(directory) / path.name
                self.command(['api', f'repos/{REPO}/releases/assets/{asset["id"]}', '-H', 'Accept: application/octet-stream'], timeout=1200, output=received)
                need(received.stat().st_size == path.stat().st_size and sha(received) == sha(path), 'Remote asset bytes differ: ' + path.name)


def release_body(release, expected, native_run, source_run, limitations):
    version = release['repository_version']
    marker = f'<!-- codex-agents.technical-release/1 source={expected} native-run={native_run} source-run={source_run} -->'
    body = f'''{marker}
Codex Agent System {version}: self-contained technical installers for Windows, macOS and Linux on x64 and ARM64.

Download the ZIP for your system, or Universal for all six platforms. Extract the entire package, open START_HERE.html, then run Start.cmd (Windows), Start.command (macOS) or Start.sh (Linux). Python, Node and the complete workbench client are included. Codex and its account remain separate.

[Installation and trust verification](https://github.com/{REPO}/blob/{expected}/docs/INSTALL.md) · [Complete guide](https://github.com/{REPO}/blob/{expected}/docs/INDEX.md) · [Component and release records](https://github.com/{REPO}/blob/{expected}/releases/README.md)

Source: `{expected}`. All six native packages and the exact Universal ZIP passed native buyer, installer GUI and bounded workbench transport checks. NATIVE-ACCEPTANCE.zip retains all twelve archive-bound proof sets. Verify SHA256SUMS/INSTALLER-SHA256SUMS and GitHub artifact attestations for this repository, main ref and exact source commit.

This publishes the technical product only. Commercial edition terms remain an owner-review draft; downloading does not issue a paid entitlement, execute a purchase, or launch public sales. Product launchers are unsigned; vendor signatures are retained where provided. No platform notarization is claimed.
'''
    if limitations:
        body += '\nObserved test-environment limitations (not accepted as codec playback):\n'
        for row in limitations:
            body += '- ' + row['target'] + ': ' + row.get('reason', 'See exact native proof.') + '\n'
    return marker, body


def publish(github, release, expected, native_run, source_run, subjects, limitations):
    tag = 'v' + release['repository_version']
    need(re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag) and release.get('release_tag') == tag,
         'Only the exact current stable technical release tag is supported')
    marker, body = release_body(release, expected, native_run, source_run, limitations)
    expected_files = {path.name: path for path in subjects}
    need(len(expected_files) == len(subjects), 'Duplicate release asset names')
    github.main_is(expected)
    commit = github.tag_commit(tag)
    need(commit in (None, expected), 'Existing tag points elsewhere; it will not be moved')
    existing = github.release(tag)
    if existing:
        need(existing.get('tag_name') == tag and existing.get('body') == body and marker in existing['body']
             and existing.get('name') == 'Codex Agent System ' + release['repository_version']
             and existing.get('prerelease') is False, 'Existing release is not this exact owned technical draft/publication')
        known_assets = github.assets(existing['id'])
        need(len({row['name'] for row in known_assets}) == len(known_assets)
             and all(row['name'] in expected_files for row in known_assets), 'Unknown remote assets prevent any draft/tag mutation')
        for row in known_assets:
            github.same_asset(row, expected_files[row['name']])
    if commit is None:
        try:
            github.api('git/refs', method='POST', data={'ref': 'refs/tags/' + tag, 'sha': expected})
        except (ValueError, subprocess.TimeoutExpired):
            need(github.tag_commit(tag) == expected, 'Tag creation outcome is unverified; reconcile before another explicit invocation')
        need(github.tag_commit(tag) == expected, 'Created tag did not resolve to exact source')
    if existing is None:
        try:
            github.api('releases', method='POST', data={'tag_name': tag, 'target_commitish': expected,
                'name': 'Codex Agent System ' + release['repository_version'], 'body': body,
                'draft': True, 'prerelease': False, 'make_latest': 'false'})
        except (ValueError, subprocess.TimeoutExpired):
            pass  # Reconcile the exact target before interpreting/repeating a write.
        existing = github.release(tag)
        need(existing and existing.get('draft') is True and existing.get('body') == body,
             'Draft creation outcome is unknown or belongs to another author; no write is retried')
    rows = github.assets(existing['id'])
    need(len({row['name'] for row in rows}) == len(rows) and all(row['name'] in expected_files for row in rows),
         'Unknown or duplicate remote assets will not be deleted or overwritten')
    for row in rows:
        github.same_asset(row, expected_files[row['name']])
    present = {row['name'] for row in rows}
    need(existing['draft'] is True or present == set(expected_files), 'A published release is incomplete; automatic modification is blocked')
    for name, path in expected_files.items():
        if name in present:
            continue
        try:
            github.command(['release', 'upload', tag, str(path), '--repo', REPO], timeout=1200, json_result=False)
        except (ValueError, subprocess.TimeoutExpired):
            pass
        candidates = [row for row in github.assets(existing['id']) if row['name'] == name]
        need(len(candidates) == 1, 'Upload outcome is unknown; leave the draft and reconcile before retry: ' + name)
        github.same_asset(candidates[0], path)
    # Repeat the authoritative full readback before the single publish step.
    rows = github.assets(existing['id'])
    need(len(rows) == len(expected_files) and {row['name'] for row in rows} == set(expected_files), 'Final remote asset closure differs')
    for row in rows:
        github.same_asset(row, expected_files[row['name']])
    github.main_is(expected); need(github.tag_commit(tag) == expected, 'Tag changed during upload')
    already_latest = existing['draft'] is False and github.api('releases/latest')['id'] == existing['id']
    if not already_latest:
        try:
            github.api('releases/' + str(existing['id']), method='PATCH', data={'draft': False, 'make_latest': 'true'})
        except (ValueError, subprocess.TimeoutExpired):
            pass
    final = github.release(tag)
    need(final and final.get('draft') is False and final.get('body') == body
         and github.api('releases/latest')['id'] == final['id'] and github.tag_commit(tag) == expected,
         'Publication/latest outcome is unverified; read back this exact release before retry')
    final_assets = github.assets(final['id'])
    need(len(final_assets) == len(expected_files) and {row['name'] for row in final_assets} == set(expected_files),
         'Published remote asset closure differs; publication needs reconciliation')
    for row in final_assets:
        github.same_asset(row, expected_files[row['name']])
    return {'tag': tag, 'release_id': final['id'], 'url': final['html_url'], 'publication_performed': not already_latest,
            'assets': [{'name': row['name'], 'size': row['size'], 'digest': row.get('digest'),
                        'url': row['browser_download_url']} for row in final_assets]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-source-sha', required=True)
    parser.add_argument('--accepted-native-run-id', required=True, type=int)
    parser.add_argument('--source-validation-run-id', required=True, type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    record = {'schema': 'codex-agents.technical-publication/1', 'source_commit': args.expected_source_sha,
              'native_run_id': args.accepted_native_run_id, 'source_run_id': args.source_validation_run_id,
              'sales_launched': False, 'publication_performed': False}
    try:
        validate_dispatch(os.environ, args.expected_source_sha)
        need(args.accepted_native_run_id > 0 and args.source_validation_run_id > 0, 'Positive run IDs are required')
        need(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == args.expected_source_sha
             and not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=root), 'Exact clean checkout is required')
        github = GitHub(output); github.main_is(args.expected_source_sha)
        for run_id, workflow in ((args.accepted_native_run_id, NATIVE), (args.source_validation_run_id, SOURCE)):
            validate_run(github.api('actions/runs/' + str(run_id)), args.expected_source_sha, workflow)
        release = read(root / 'releases/current.json')
        installer_dir, source_dir = output / 'installers', output / 'source-bundles'
        record['artifacts'] = [github.download(args.accepted_native_run_id, 'installer-accepted-release', installer_dir),
                               github.download(args.source_validation_run_id, 'agent-system-bundles', source_dir)]
        installers, limits = installer_subjects(installer_dir, release, args.expected_source_sha)
        sources = source_subjects(source_dir, release, root)
        for path in installers:
            github.verify_attestation(path, args.expected_source_sha, NATIVE)
        for path in sources:
            if path.suffix == '.zip':
                github.verify_attestation(path, args.expected_source_sha, SOURCE)
        record['verified_subjects'] = [{'name': path.name, 'size': path.stat().st_size, 'sha256': sha(path)} for path in [*installers, *sources]]
        record['environment_limits'] = limits
        record['release'] = publish(github, release, args.expected_source_sha, args.accepted_native_run_id,
                                    args.source_validation_run_id, [*installers, *sources], limits)
        record.update(status='published-and-read-back', publication_performed=record['release']['publication_performed'])
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        record.update(status='blocked-or-unverified', reason=str(error),
                      next='Inspect the exact tag/draft/assets and this receipt before an explicit retry. No unknown remote asset was overwritten or deleted.')
        print(record['reason'], file=sys.stderr); return 1
    finally:
        (output / 'PUBLICATION.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    raise SystemExit(main())
