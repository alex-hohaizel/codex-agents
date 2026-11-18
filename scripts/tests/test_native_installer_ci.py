"""Protect the native release runner's shell-free tools and exact proof binding."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'native_installer_ci.py'
SPEC = importlib.util.spec_from_file_location('native_installer_ci_under_test', SOURCE)
ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci)


class NativeCIGuards(unittest.TestCase):
    def test_windows_npm_uses_node_and_exact_js_entry_instead_of_batch_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            node = root / 'node.exe'; node.write_bytes(b'not executed in this argument-contract test')
            batch = root / 'npm.cmd'; batch.write_text('echo must not execute')
            script = root / 'node_modules/npm/bin/npm-cli.js'
            script.parent.mkdir(parents=True); script.write_text('// declared npm entry')
            with patch.object(ci.shutil, 'which', side_effect=lambda name: str(node if name == 'node' else batch)):
                self.assertEqual(ci.npm_command(), [str(node), str(script)])
                script.unlink()
                with self.assertRaisesRegex(ValueError, 'Node/npm'):
                    ci.npm_command()

    def test_receipts_require_same_clean_commit_and_exact_archive_and_manifest(self):
        source, archive, manifest = 'a' * 40, 'b' * 64, 'c' * 64
        backend = {'status': 'passed', 'source_clean': True, 'source_commit': source,
                   'archive_sha256': archive, 'package_manifest_sha256': manifest}
        browser = {'status': 'passed', 'package': {'source_commit': source, 'manifest_sha256': manifest}}
        ci.validate_pair(backend, browser, source, archive)
        for key, wrong in [('status', 'failed'), ('source_clean', False), ('source_clean', 'true'),
                           ('source_commit', 'd' * 40), ('archive_sha256', 'd' * 64)]:
            changed = copy.deepcopy(backend); changed[key] = wrong
            with self.subTest(backend_field=key, value=wrong), self.assertRaises(ValueError):
                ci.validate_pair(changed, browser, source, archive)
        for key, wrong in [('source_commit', 'd' * 40), ('manifest_sha256', 'd' * 64)]:
            changed = copy.deepcopy(browser); changed['package'][key] = wrong
            with self.subTest(browser_field=key), self.assertRaises(ValueError):
                ci.validate_pair(backend, changed, source, archive)

    def test_public_proof_redaction_removes_authentication_but_keeps_artifact_identity(self):
        result = ci.sanitize({'archive_sha256': 'a' * 64, 'control_key': 'never publish',
                              'detail': ['http://127.0.0.1:1234/#launch=private-token'],
                              'nested': {'csrf_token': 'never publish either'}})
        self.assertEqual(result['archive_sha256'], 'a' * 64)
        self.assertNotIn('private-token', str(result))
        self.assertNotIn('never publish', str(result))


if __name__ == '__main__':
    unittest.main()
