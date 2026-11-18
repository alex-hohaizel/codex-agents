"""Protect the native release runner's shell-free tools and exact proof binding."""
import copy
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'native_installer_ci.py'
SPEC = importlib.util.spec_from_file_location('native_installer_ci_under_test', SOURCE)
ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci)


class NativeCIGuards(unittest.TestCase):
    def test_standard_branded_browser_precedes_chromium_without_fake_arm_chrome(self):
        with tempfile.TemporaryDirectory() as directory:
            browser = Path(directory) / 'google-chrome'; browser.write_bytes(b'not executed')
            with patch.object(ci.shutil, 'which', return_value=str(browser)):
                selected, provider = ci.standard_browser(platform_name='linux', cpu='x64')
                self.assertEqual(selected, browser.resolve())
                self.assertEqual(provider, 'standard-runner Google Chrome')
                selected, provider = ci.standard_browser(platform_name='linux', cpu='arm64')
                self.assertIsNone(selected)
                self.assertIsNone(provider)

    def test_official_native_resolution_checks_version_and_cpu_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            base = root / 'lib/node_modules/@openai/codex'
            native = base / 'node_modules/@openai/codex-darwin-arm64'
            native.mkdir(parents=True)
            import json
            metadata = {'name': '@openai/codex', 'version': '0.166.0', 'optionalDependencies': {
                '@openai/codex-darwin-arm64': 'npm:@openai/codex@0.166.0-darwin-arm64'}}
            (base / 'package.json').write_text(json.dumps(metadata))
            (native / 'package.json').write_text(json.dumps({'name': '@openai/codex', 'version': '0.166.0-darwin-arm64'}))
            executable = native / 'vendor/aarch64-apple-darwin/bin/codex'
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'\xcf\xfa\xed\xfe' + (0x1000007).to_bytes(4, 'little') + b'\0' * 56)
            # This metadata/header fixture is deliberately never executed.
            reply = SimpleNamespace(returncode=0, stdout=str(native / 'package.json') + '\n')
            with patch.object(ci.subprocess, 'run', return_value=reply):
                with self.assertRaisesRegex(ValueError, 'architecture differs'):
                    ci.native_codex_from_npm(root, 'node', platform_name='darwin', cpu='arm64')
                executable.write_bytes(b'\xcf\xfa\xed\xfe' + (0x100000c).to_bytes(4, 'little') + b'\0' * 56)
                selected, provenance = ci.native_codex_from_npm(root, 'node', platform_name='darwin', cpu='arm64')
                self.assertEqual(selected, executable)
                self.assertEqual(provenance['target_triple'], 'aarch64-apple-darwin')
                metadata['version'] = '0.167.0'
                (base / 'package.json').write_text(json.dumps(metadata))
                with self.assertRaisesRegex(ValueError, 'pinned release'):
                    ci.native_codex_from_npm(root, 'node', platform_name='darwin', cpu='arm64')

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
        browser = {'status': 'passed', 'package': {'source_commit': source, 'manifest_sha256': manifest},
                   'purchase_document': {'retained_bytes_verified': True, 'old_plan_rejected': True,
                     'selection_clears_approved_plan': True, 'sha256': 'd' * 64}}
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

    def test_browser_document_proof_cannot_be_omitted_or_replaced_by_an_unbound_declaration(self):
        backend = {'status': 'passed', 'source_clean': True, 'source_commit': 'a' * 40,
                   'archive_sha256': 'b' * 64, 'package_manifest_sha256': 'c' * 64}
        browser = {'status': 'passed', 'package': {'source_commit': 'a' * 40, 'manifest_sha256': 'c' * 64}}
        for document in ({}, {'retained_bytes_verified': True}, {'retained_bytes_verified': True,
                         'old_plan_rejected': True, 'selection_clears_approved_plan': True, 'sha256': 'invalid'}):
            with self.subTest(document=document), self.assertRaisesRegex(ValueError, 'purchase-document'):
                ci.validate_pair(backend, dict(browser, purchase_document=document), 'a' * 40, 'b' * 64)

    def test_public_proof_redaction_removes_authentication_but_keeps_artifact_identity(self):
        result = ci.sanitize({'archive_sha256': 'a' * 64, 'control_key': 'never publish',
                              'detail': ['http://127.0.0.1:1234/#launch=private-token'],
                              'nested': {'csrf_token': 'never publish either'}})
        self.assertEqual(result['archive_sha256'], 'a' * 64)
        self.assertNotIn('private-token', str(result))
        self.assertNotIn('never publish', str(result))


if __name__ == '__main__':
    unittest.main()
