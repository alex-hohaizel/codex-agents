"""Release policy and reconciliation guards; these tests never access GitHub."""
import copy
import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location('technical_release_under_test', Path(__file__).resolve().parents[1] / 'publish_technical_release.py')
release = importlib.util.module_from_spec(SPEC)
exec(compile(Path(SPEC.origin).read_bytes(), SPEC.origin, 'exec'), release.__dict__)
SHA = 'a' * 40
CURRENT = {'repository_version': '1.8.0', 'suite_version': '6.5.0', 'release_tag': 'v1.8.0'}


class RemoteFixture:
    """A deterministic transport fixture, never a publication execution proof."""
    def __init__(self, paths, *, published=False, unknown=None, upload_unknown=False):
        self.paths = paths; self.writes = []; self.rows = []; self.upload_unknown = upload_unknown
        _, body = release.release_body(CURRENT, SHA, 1, 2, [])
        self.record = {'id': 9, 'tag_name': 'v1.8.0', 'name': 'Codex Agent System 1.8.0',
                       'body': body, 'draft': not published, 'prerelease': False, 'html_url': 'https://example.invalid/release'}
        if published:
            self.rows = [self.asset(path) for path in paths]
        if unknown:
            self.rows.append({'name': unknown})

    def asset(self, path):
        return {'id': len(self.rows) + 1, 'name': path.name, 'size': path.stat().st_size,
                'state': 'uploaded', 'digest': 'sha256:' + release.sha(path), 'browser_download_url': 'https://example.invalid/' + path.name}

    def main_is(self, expected):
        assert expected == SHA

    def tag_commit(self, tag):
        return SHA

    def release(self, tag):
        return copy.deepcopy(self.record)

    def assets(self, release_id):
        return copy.deepcopy(self.rows)

    def same_asset(self, asset, path):
        return release.GitHub.same_asset(self, asset, path)

    def command(self, args, **kwargs):
        assert args[:2] == ['release', 'upload']; assert '--clobber' not in args
        self.writes.append(('upload', args[3]))
        if self.upload_unknown == 'before-effect':
            raise ValueError('injected unknown upload before effect')
        self.rows.append(self.asset(Path(args[3])))
        if self.upload_unknown:
            raise ValueError('injected lost reply after effect')

    def api(self, path, *, method='GET', data=None):
        if path == 'releases/latest':
            return {'id': self.record['id']}
        assert method == 'PATCH' and data == {'draft': False, 'make_latest': 'true'}
        self.writes.append(('publish', path)); self.record['draft'] = False
        return copy.deepcopy(self.record)


class TechnicalPublicationGuards(unittest.TestCase):
    def test_all_twelve_archive_target_proofs_are_required_and_private_cleanup_cannot_be_lost(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proof.zip'
            pairs = {(('1' if universal else str(index + 2)) * 64, target)
                     for universal in (False, True) for index, target in enumerate(sorted(release.TARGETS))}
            def write_proofs(break_cleanup=False, gui_cleanup=None):
                with zipfile.ZipFile(path, 'w') as archive:
                    for index, (digest, target) in enumerate(sorted(pairs)):
                        prefix = 'proof-' + str(index) + '/'
                        manifest = 'f' * 64
                        records = {
                            'NATIVE-CI.json': {'status': 'passed', 'source_commit': SHA, 'archive_sha256': digest,
                                'target': target, 'backend_and_real_browser': True, 'workbench_browser_transport_verified': True,
                                'windows_restricted_non_admin_verified': True, 'environment_limits': []},
                            'backend/native-acceptance.json': {'status': 'passed', 'source_clean': True, 'source_commit': SHA,
                                'archive_sha256': digest, 'native': {'target': target}, 'package_manifest_sha256': manifest},
                            'gui-proof/BROWSER-OBSERVATION.json': {'status': 'passed', 'package': {'source_commit': SHA, 'manifest_sha256': manifest},
                                'browser_cleanup': {'root_exit_observed': True, 'profile_removed': True} if gui_cleanup is None else gui_cleanup},
                            'workbench-proof/WORKBENCH-BROWSER-PRIVACY.json': {'status': 'passed', 'source': {'source_commit': SHA,
                                'package_manifest_sha256': manifest}, 'browser_cleanup': {'parent_exit_observed': True,
                                'private_root_removed': not break_cleanup}, 'limitations': []}}
                        inventory = []
                        for name, data in records.items():
                            raw = json.dumps(data).encode(); archive.writestr(prefix + name, raw)
                            inventory.append({'file': name, 'redacted_sha256': hashlib.sha256(raw).hexdigest()})
                        archive.writestr(prefix + 'PROOF-INVENTORY.json', json.dumps({'files': inventory}))
            write_proofs()
            self.assertEqual(release.verify_native_proofs(path, SHA, pairs), [])
            with self.assertRaisesRegex(ValueError, 'Invalid, duplicate, or foreign'):
                release.verify_native_proofs(path, SHA, set(list(pairs)[1:]))
            for cleanup in ({}, {'root_exit_observed': False, 'profile_removed': True},
                            {'root_exit_observed': True, 'profile_removed': False}):
                with self.subTest(gui_cleanup=cleanup):
                    write_proofs(gui_cleanup=cleanup)
                    with self.assertRaisesRegex(ValueError, 'Installer browser proof binding or cleanup differs'):
                        release.verify_native_proofs(path, SHA, pairs)
            write_proofs(break_cleanup=True)
            with self.assertRaisesRegex(ValueError, 'cleanup differs'):
                release.verify_native_proofs(path, SHA, pairs)

    def test_dispatch_and_two_workflow_runs_must_be_exact_current_main_push(self):
        env = {'GITHUB_REPOSITORY': release.REPO, 'GITHUB_EVENT_NAME': 'workflow_dispatch',
               'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': SHA}
        release.validate_dispatch(env, SHA)
        for key, value in [('GITHUB_EVENT_NAME', 'push'), ('GITHUB_SHA', 'b' * 40), ('GITHUB_REF', 'refs/heads/feature')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                release.validate_dispatch(dict(env, **{key: value}), SHA)
        run = {'repository': {'full_name': release.REPO}, 'head_repository': {'full_name': release.REPO},
               'event': 'push', 'head_branch': 'main', 'head_sha': SHA, 'path': release.NATIVE,
               'status': 'completed', 'conclusion': 'success'}
        release.validate_run(run, SHA, release.NATIVE)
        for key, value in [('event', 'pull_request'), ('path', release.SOURCE), ('head_sha', 'b' * 40), ('conclusion', 'failure')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                release.validate_run(dict(run, **{key: value}), SHA, release.NATIVE)

    def test_unknown_remote_asset_blocks_all_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'accepted.zip'; path.write_bytes(b'accepted')
            remote = RemoteFixture([path], unknown='unrecognized.zip')
            with self.assertRaisesRegex(ValueError, 'Unknown remote assets'):
                release.publish(remote, CURRENT, SHA, 1, 2, [path], [])
            self.assertEqual(remote.writes, [])

    def test_lost_upload_reply_is_reconciled_without_duplicate_or_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'accepted.zip'; path.write_bytes(b'accepted')
            remote = RemoteFixture([path], upload_unknown=True)
            result = release.publish(remote, CURRENT, SHA, 1, 2, [path], [])
            self.assertEqual([kind for kind, _ in remote.writes], ['upload', 'publish'])
            self.assertTrue(result['publication_performed'])

    def test_unknown_missing_upload_stops_and_leaves_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'accepted.zip'; path.write_bytes(b'accepted')
            remote = RemoteFixture([path], upload_unknown='before-effect')
            with self.assertRaisesRegex(ValueError, 'Upload outcome is unknown'):
                release.publish(remote, CURRENT, SHA, 1, 2, [path], [])
            self.assertEqual(len(remote.writes), 1)
            self.assertTrue(remote.record['draft'])

    def test_already_published_exact_latest_is_read_only_and_wrong_digest_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'accepted.zip'; path.write_bytes(b'accepted')
            remote = RemoteFixture([path], published=True)
            result = release.publish(remote, CURRENT, SHA, 1, 2, [path], [])
            self.assertFalse(result['publication_performed']); self.assertEqual(remote.writes, [])
            remote.rows[0]['digest'] = 'sha256:' + '0' * 64
            with self.assertRaisesRegex(ValueError, 'digest differs'):
                release.publish(remote, CURRENT, SHA, 1, 2, [path], [])
            self.assertEqual(remote.writes, [])

    def test_draft_lookup_is_owner_list_and_does_not_assume_tag_endpoint_returns_drafts(self):
        remote = release.GitHub(Path('.'))
        requests = []
        def api(path):
            requests.append(path)
            return [{'tag_name': 'v1.8.0', 'draft': True, 'id': 7}]
        remote.api = api
        self.assertTrue(remote.release('v1.8.0')['draft'])
        self.assertEqual(requests, ['releases?per_page=100&page=1'])


if __name__ == '__main__':
    unittest.main()
