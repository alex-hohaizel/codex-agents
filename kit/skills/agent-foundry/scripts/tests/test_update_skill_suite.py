"""Filesystem-only synthetic suite update/recovery regressions; no host install."""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'update_skill_suite.py'
SPEC = importlib.util.spec_from_file_location('suite_update_under_test', SCRIPT)
U = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(U)


class SuiteUpdateTests(unittest.TestCase):
    def setUp(self):
        tmp = Path(os.environ.get('TMPDIR', tempfile.gettempdir()))
        tmp.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='suite-fixture-', dir=str(tmp))
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.kit = self.base / 'kit'
        self.dest = self.base / 'home/.agents/skills'
        self.legacy = self.base / 'home/.codex/skills'
        self.backups = self.base / 'backups'
        self.plan_path = self.base / 'plan.json'
        rows = []
        for name in sorted(U.NAMES):
            root = self.kit / 'skills' / name
            root.mkdir(parents=True)
            (root / 'SKILL.md').write_text('---\nname: ' + name + '\ndescription: Synthetic fixture only\n---\n# Fixture\nNew accepted source.\n')
            (root / 'scripts').mkdir()
            (root / 'scripts/example.py').write_text('print("fixture")\n')
            os.chmod(root / 'SKILL.md', 0o644)
            os.chmod(root / 'scripts/example.py', 0o755)
            rows.append({'name': name, 'version': '4.3.0' if name.startswith('gamedev-') else '2.3.0',
                         'files': U.snapshot(root)['files'], 'previous_trees': []})
        self.manifest = {'schema_version': 'atelier.skill-suite/1', 'suite_id': 'synthetic-suite', 'skills': rows}
        self.write_manifest()

    def write_manifest(self):
        (self.kit / 'manifest.json').write_bytes(U.encode(self.manifest))

    def row(self, name='agent-foundry'):
        return next(x for x in self.manifest['skills'] if x['name'] == name)

    def make_old(self, name='agent-foundry', root=None):
        target = (root or self.dest) / name
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('---\nname: ' + name + '\ndescription: Old synthetic fixture\n---\n# Original\nPreserve exact original.\n')
        (target / '__pycache__').mkdir()
        (target / '__pycache__/fixture.pyc').write_bytes(b'cached fixture bytes')
        (target / 'empty-directory').mkdir()
        os.chmod(target, 0o700)
        os.chmod(target / 'SKILL.md', 0o600)
        state = U.snapshot(target)
        self.row(name)['previous_trees'].append({'tree_sha256': state['tree_sha256'], 'source': 'explicit synthetic old baseline'})
        self.write_manifest()
        return target, state

    def plan(self, retire=False, projects=()):
        plan = U.audit(self.kit, self.dest, self.legacy, self.backups, projects, retire)
        self.plan_path.write_bytes(U.encode(plan))
        return plan

    def apply(self):
        self.plan()
        result = U.apply_plan(self.plan_path)
        return Path(result['journal'])

    def latest_journal(self):
        return next(self.backups.glob('run-*/journal.json'))

    def test_python39_syntax(self):
        ast.parse(SCRIPT.read_text(), feature_version=(3, 9))

    def test_exact_allowlist_and_full_manifest(self):
        self.assertEqual(len(U.read_kit(self.kit)[3]), 33)
        self.manifest['skills'].pop(); self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'exact 33'):
            U.read_kit(self.kit)

    def test_manifest_path_traversal_rejected(self):
        self.row()['files']['../config.toml'] = dict(next(iter(self.row()['files'].values())))
        self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'Unsafe'):
            U.read_kit(self.kit)

    def test_case_and_unicode_collision_rejected(self):
        self.row()['files']['skill.md'] = dict(self.row()['files']['SKILL.md'])
        self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'collision'):
            U.read_kit(self.kit)

    def test_file_directory_collision_rejected(self):
        self.row()['files']['scripts'] = dict(self.row()['files']['SKILL.md'])
        self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'collision'):
            U.read_kit(self.kit)

    def test_unexpected_kit_file_rejected(self):
        (self.kit / 'skills/agent-foundry/extra.txt').write_text('unexpected')
        with self.assertRaisesRegex(U.SuiteError, 'differs'):
            U.read_kit(self.kit)

    def test_zip_extraction_source_modes_do_not_change_declared_target_modes(self):
        for p in (self.kit / 'skills').rglob('*.py'):
            os.chmod(p, 0o644)
        self.apply()
        self.assertEqual((self.dest / 'agent-foundry/scripts/example.py').stat().st_mode & 0o777, 0o755)
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_uninspected_discovery_symlink_blocks_without_following(self):
        self.dest.mkdir(parents=True)
        (self.dest / 'unknown-link').symlink_to(self.base / 'outside-missing', target_is_directory=True)
        with self.assertRaisesRegex(U.SuiteError, 'Uninspected symlink'):
            self.plan()

    def test_symlink_kit_file_rejected(self):
        p = self.kit / 'skills/agent-foundry/SKILL.md'
        data = p.read_bytes(); p.unlink(); outside = self.base / 'outside'
        outside.write_bytes(data); p.symlink_to(outside)
        with self.assertRaisesRegex(U.SuiteError, 'Link|Symlink'):
            U.read_kit(self.kit)

    def test_audit_leaves_installation_and_backup_roots_absent(self):
        self.assertTrue(self.plan()['ready'])
        self.assertFalse(self.dest.exists())
        self.assertFalse(self.backups.exists())

    def test_install_verify_idempotence_preserves_unrelated(self):
        self.dest.mkdir(parents=True)
        unrelated = self.dest / 'unrelated'; unrelated.mkdir(); (unrelated / 'keep.bin').write_bytes(b'owner data')
        config = self.base / 'home/.codex/config.toml'; config.parent.mkdir(exist_ok=True); config.write_text('owner configuration')
        agents = self.base / 'home/AGENTS.md'; agents.write_text('owner instructions')
        self.plan(); first = U.apply_plan(self.plan_path)
        self.assertEqual(first['changed'], 33)
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])
        self.assertFalse(U.verify(self.kit, self.dest, self.legacy)['runtime_discovery_verified'])
        self.assertEqual(U.apply_plan(self.plan_path)['status'], 'already_applied')
        self.assertEqual((unrelated / 'keep.bin').read_bytes(), b'owner data')
        self.assertEqual(config.read_text(), 'owner configuration')
        self.assertEqual(agents.read_text(), 'owner instructions')
        self.assertEqual((self.dest / 'agent-foundry/scripts/example.py').stat().st_mode & 0o777, 0o755)
        fresh = self.plan(); self.assertTrue(all(x['action'] == 'noop' for x in fresh['entries']))
        self.assertEqual(U.apply_plan(self.plan_path)['changed'], 0)

    def test_known_old_full_backup_and_rollback_preserve_modes_cache_and_empty_dirs(self):
        target, before = self.make_old()
        journal = self.apply()
        payload = U.read_json(journal)
        index = next(i for i, x in enumerate(payload['plan']['entries']) if x['target'] == str(target))
        backup = journal.parent / 'backup' / str(index)
        self.assertEqual(U.snapshot(backup), before)
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])
        U.rollback(journal)
        self.assertEqual(U.snapshot(target), before)
        self.assertEqual(U.rollback(journal)['status'], 'already_rolled_back')
        self.assertFalse((self.dest / 'gamedev-assets').exists())

    def test_unknown_old_tree_blocks(self):
        self.make_old(); self.row()['previous_trees'] = []; self.write_manifest()
        plan = self.plan(); self.assertFalse(plan['ready'])
        with self.assertRaisesRegex(U.SuiteError, 'blockers'):
            U.apply_plan(self.plan_path)

    def test_mode_changed_after_audit_blocks_before_mutation(self):
        target, _ = self.make_old(); self.plan(); os.chmod(target / 'SKILL.md', 0o644)
        with self.assertRaisesRegex(U.SuiteError, 'changed after audit'):
            U.apply_plan(self.plan_path)
        self.assertFalse(self.backups.exists())

    def test_payload_tamper_after_audit_blocks(self):
        self.plan(); (self.kit / 'skills/agent-foundry/SKILL.md').write_text('tampered')
        with self.assertRaisesRegex(U.SuiteError, 'differs'):
            U.apply_plan(self.plan_path)
        self.assertFalse(self.dest.exists())

    def test_plan_cannot_redirect_target(self):
        plan = self.plan(); plan['entries'][0]['target'] = str(self.base / 'outside')
        self.plan_path.write_bytes(U.encode(plan))
        with self.assertRaisesRegex(U.SuiteError, 'Noncanonical'):
            U.apply_plan(self.plan_path)

    def test_backup_inside_skill_root_rejected(self):
        with self.assertRaisesRegex(U.SuiteError, 'outside'):
            U.audit(self.kit, self.dest, self.legacy, self.dest / 'backups')

    def test_unknown_canonical_declared_name_not_overwritten(self):
        self.make_old(); p = self.dest / 'agent-foundry/SKILL.md'
        p.write_text('---\nname: owner-unrelated\ndescription: Owner\n---\nContent\n')
        self.assertFalse(self.plan()['ready'])

    def test_duplicate_report_only_and_explicit_known_retirement_roundtrip(self):
        legacy_target, original = self.make_old(root=self.legacy)
        self.assertFalse(self.plan()['ready'])
        plan = self.plan(retire=True)
        self.assertTrue(plan['ready'])
        self.assertEqual(sum(x['action'] == 'retire' for x in plan['entries']), 1)
        journal = Path(U.apply_plan(self.plan_path)['journal'])
        self.assertFalse(legacy_target.exists())
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])
        U.rollback(journal)
        self.assertEqual(U.snapshot(legacy_target), original)

    def test_project_duplicate_never_retired(self):
        project = self.base / 'product'
        target, original = self.make_old(root=project / '.agents/skills')
        plan = self.plan(retire=True, projects=[project])
        self.assertFalse(plan['ready'])
        self.assertTrue(any('report-only' in x for x in plan['blockers']))
        self.assertEqual(U.snapshot(target), original)

    def test_cache_drift_admitted_logically_but_bound_in_stale_plan(self):
        target, _ = self.make_old()
        (target / '__pycache__/fixture.pyc').write_bytes(b'fresh legitimate cache')
        self.assertTrue(self.plan()['ready'])
        (target / '__pycache__/fixture.pyc').write_bytes(b'cache changed after audit')
        with self.assertRaisesRegex(U.SuiteError, 'changed after audit'):
            U.apply_plan(self.plan_path)

    def test_resume_after_partial_backup_copy(self):
        target, _ = self.make_old(); self.plan()
        real = U.copy_tree
        failed = [False]
        def interrupted(source, dest, expected):
            if not failed[0]:
                failed[0] = True; dest.mkdir(parents=True); (dest / 'partial.txt').write_text('incomplete')
                raise OSError('synthetic partial backup crash')
            return real(source, dest, expected)
        with mock.patch.object(U, 'copy_tree', side_effect=interrupted):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        U.apply_plan(self.plan_path, resume=self.latest_journal())
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_resume_after_old_tree_rename_before_journal(self):
        target, _ = self.make_old(); self.plan(); real = os.replace; failed = [False]
        def interrupted(source, dest):
            real(source, dest)
            if Path(source) == target and Path(dest).name == 'old' and not failed[0]:
                failed[0] = True; raise OSError('synthetic crash after old rename')
        with mock.patch.object(U.os, 'replace', side_effect=interrupted):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        self.assertFalse(target.exists())
        U.apply_plan(self.plan_path, resume=self.latest_journal())
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_resume_after_new_tree_rename_before_journal(self):
        self.plan(); real = os.replace; failed = [False]
        def interrupted(source, dest):
            real(source, dest)
            if Path(source).name == 'new' and not failed[0]:
                failed[0] = True; raise OSError('synthetic crash after new rename')
        with mock.patch.object(U.os, 'replace', side_effect=interrupted):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        U.apply_plan(self.plan_path, resume=self.latest_journal())
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_resume_after_partial_preparation(self):
        self.plan(); real = U.create_payload; failed = [False]
        def interrupted(kit, name, target, files):
            if not failed[0]:
                failed[0] = True; target.mkdir(parents=True); (target / 'partial.txt').write_text('incomplete')
                raise OSError('synthetic partial preparation')
            return real(kit, name, target, files)
        with mock.patch.object(U, 'create_payload', side_effect=interrupted):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        U.apply_plan(self.plan_path, resume=self.latest_journal())
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_forged_resume_payload_cannot_escape_manifest(self):
        self.plan()
        with mock.patch.object(U, 'create_payload', side_effect=OSError('synthetic preparation interruption')):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        path = self.latest_journal(); journal = U.read_json(path)
        plan = journal['plan']
        plan['entries'][0]['desired_files']['../../outside.txt'] = dict(self.row()['files']['SKILL.md'])
        journal['plan_sha256'] = U.sha(U.encode(plan))
        self.plan_path.write_bytes(U.encode(plan)); path.write_bytes(U.encode(journal))
        with self.assertRaisesRegex(U.SuiteError, 'differs from manifest'):
            U.apply_plan(self.plan_path, resume=path)
        self.assertFalse((self.dest.parent / 'outside.txt').exists())

    def test_rollback_refuses_post_update_user_changes(self):
        journal = self.apply(); target = self.dest / 'gamedev-studio/SKILL.md'
        target.write_text('owner post-update changes')
        all_before = {x.name: U.snapshot(x) for x in self.dest.iterdir()}
        with self.assertRaisesRegex(U.SuiteError, 'overwrite work'):
            U.rollback(journal)
        self.assertEqual(target.read_text(), 'owner post-update changes')
        self.assertEqual({x.name: U.snapshot(x) for x in self.dest.iterdir()}, all_before)

    def test_corrupt_backup_blocks_rollback(self):
        self.make_old(); journal = self.apply()
        (journal.parent / 'backup/0/SKILL.md').write_text('corrupt')
        with self.assertRaisesRegex(U.SuiteError, 'Backup integrity'):
            U.rollback(journal)
        self.assertEqual(U.declared_name(self.dest / 'agent-foundry'), 'agent-foundry')

    def test_rollback_resume_after_discard_rename(self):
        target, original = self.make_old(); journal = self.apply()
        real = os.replace; failed = [False]
        def interrupted(source, dest):
            real(source, dest)
            if Path(source) == target and Path(dest).name == 'rollback-discard' and not failed[0]:
                failed[0] = True; raise OSError('synthetic rollback crash after discard')
        with mock.patch.object(U.os, 'replace', side_effect=interrupted):
            with self.assertRaises(OSError):U.rollback(journal)
        U.rollback(journal)
        self.assertEqual(U.snapshot(target), original)

    def test_active_update_lock_blocks(self):
        self.plan(); self.backups.mkdir()
        lock = self.backups / '.skill-suite.lock'
        lock.write_bytes(U.encode({'operation': '/another/run', 'plan_sha256': '0' * 64, 'pid': os.getpid(), 'hostname': 'fixture'}))
        with self.assertRaisesRegex(U.SuiteError, 'lock exists'):
            U.apply_plan(self.plan_path)
        self.assertFalse(self.dest.exists())

    def test_orphan_lock_before_initial_journal_is_recoverable_with_unchanged_plan(self):
        plan = self.plan(); self.backups.mkdir()
        operation = self.backups / ('run-' + '1' * 32)
        (self.backups / '.skill-suite.lock').write_bytes(U.encode({
            'operation': str(operation), 'plan_sha256': U.sha(U.encode(plan)),
            'pid': 1234567, 'hostname': U.socket.gethostname()}))
        with mock.patch.object(U.os, 'kill', side_effect=ProcessLookupError()):
            result = U.apply_plan(self.plan_path, resume=operation / 'journal.json')
        self.assertEqual(result['status'], 'complete')
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy)['ready'])

    def test_orphan_lock_unknown_files_are_not_discarded(self):
        plan = self.plan(); self.backups.mkdir()
        operation = self.backups / ('run-' + '1' * 32); operation.mkdir()
        precious = operation / 'unknown-owner-file'; precious.write_text('preserve')
        (self.backups / '.skill-suite.lock').write_bytes(U.encode({
            'operation': str(operation), 'plan_sha256': U.sha(U.encode(plan)),
            'pid': 1234567, 'hostname': U.socket.gethostname()}))
        with self.assertRaisesRegex(U.SuiteError, 'unexpected operation'):
            U.apply_plan(self.plan_path, resume=operation / 'journal.json')
        self.assertEqual(precious.read_text(), 'preserve')

    def test_project_report_only_skill_root_cannot_contain_output_plan(self):
        project = self.base / 'product'
        output = project / '.agents/skills/audit-plan.json'
        with self.assertRaisesRegex(U.SuiteError, 'outside all skill-discovery'):
            with contextlib.redirect_stdout(io.StringIO()):
                U.main(['audit', '--kit', str(self.kit), '--destination', str(self.dest),
                        '--legacy-root', str(self.legacy), '--backup-root', str(self.backups),
                        '--project-root', str(project), '--plan', str(output)])
        self.assertFalse(output.exists())

    def test_audit_cli_plan_output_is_explicit_and_exclusive(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = U.main(['audit', '--kit', str(self.kit), '--destination', str(self.dest),
                           '--legacy-root', str(self.legacy), '--backup-root', str(self.backups), '--plan', str(self.plan_path)])
        self.assertEqual(code, 0)
        with self.assertRaisesRegex(U.SuiteError, 'already exists'):
            with contextlib.redirect_stdout(io.StringIO()):
                U.main(['audit', '--kit', str(self.kit), '--destination', str(self.dest),
                        '--legacy-root', str(self.legacy), '--backup-root', str(self.backups), '--plan', str(self.plan_path)])


class VisualIdentityTests(unittest.TestCase):
    setUp_base = SuiteUpdateTests.setUp
    write_manifest = SuiteUpdateTests.write_manifest
    row = SuiteUpdateTests.row
    make_old = SuiteUpdateTests.make_old
    plan = SuiteUpdateTests.plan
    latest_journal = SuiteUpdateTests.latest_journal

    @staticmethod
    def ui(version='5.0.0'):
        return ('interface:\n  display_name: Fixture · ' + version + '\n'
                '  short_description: A stable fixture\n'
                '  default_prompt: Use the known fixture\n'
                '  icon_small: assets/icon.svg\n  icon_large: assets/icon.svg\n'
                '  brand_color: "#334455"\n'
                'policy:\n  allow_implicit_invocation: true\n'
                'dependencies:\n  tools:\n  - name: exact-approved-tool\n')

    def setUp(self):
        self.setUp_base()
        for row in self.manifest['skills']:
            root = self.kit / 'skills' / row['name']
            (root / 'agents').mkdir(); (root / 'assets').mkdir()
            (root / U.UI_PATH).write_text(self.ui())
            (root / 'assets/icon.svg').write_bytes(b'<svg>canonical icon</svg>')
            row['files'] = U.snapshot(root)['files']
            row['version'] = '5.0.0'
        self.manifest['visual_identity_policy'] = U.VISUAL_POLICY
        self.write_manifest()

    def visual_old(self):
        target, _ = self.make_old()
        (target / 'agents').mkdir(); (target / 'assets').mkdir()
        (target / U.UI_PATH).write_text(self.ui('2.3.0'))
        (target / 'assets/icon.svg').write_bytes(b'<svg>approved old icon</svg>')
        self.bind_old(target)
        return target

    def bind_old(self, target):
        state = U.snapshot(target)
        self.row()['previous_trees'].append({'tree_sha256': state['tree_sha256'], 'source': 'Explicit pre-customization baseline',
                                              'files': {k: v for k, v in state['files'].items() if not U.volatile(k)},
                                              'ui_yaml': (target / U.UI_PATH).read_text()})
        self.write_manifest()

    def customize(self, target, relative='assets/local-icon.svg'):
        icon = target / relative; icon.parent.mkdir(parents=True, exist_ok=True)
        icon.write_bytes(b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        os.chmod(icon, 0o600)
        text = (target / U.UI_PATH).read_text().replace('assets/icon.svg', relative).replace('#334455', '#AABBCC')
        (target / U.UI_PATH).write_text(text)
        return U.snapshot(target)

    def apply_visual(self):
        plan = self.plan(); self.assertTrue(plan['ready'], plan['blockers'])
        return Path(U.apply_plan(self.plan_path)['journal'])

    def test_custom_icon_path_bytes_brand_and_current_version_survive_with_exact_receipt_and_rollback(self):
        target = self.visual_old(); original = self.customize(target)
        journal = self.apply_visual()
        self.assertEqual((target / 'assets/local-icon.svg').read_bytes(), b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        fields, *_ = U.visual_yaml((target / U.UI_PATH).read_text())
        self.assertEqual(fields, {'icon_small': 'assets/local-icon.svg', 'icon_large': 'assets/local-icon.svg', 'brand_color': '#AABBCC'})
        self.assertIn('Fixture · 5.0.0', (target / U.UI_PATH).read_text())
        result = U.verify(self.kit, self.dest, self.legacy, journal)
        self.assertTrue(result['ready']); self.assertTrue(result['visual_preservation_verified'])
        self.assertIn('agent-foundry', result['preserved_visual_identities'])
        plain = U.verify(self.kit, self.dest, self.legacy)
        self.assertFalse(plain['ready']); self.assertIn('receipt', plain['failures'][0]['reason'])
        self.assertTrue(plain['canonical_core_verified'])
        U.rollback(journal)
        self.assertEqual(U.snapshot(target), original)

    def test_custom_icon_same_path_and_shared_small_large_alias_preserved(self):
        target = self.visual_old(); self.customize(target, 'assets/icon.svg')
        journal = self.apply_visual()
        self.assertEqual((target / 'assets/icon.svg').read_bytes(), b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy, journal)['ready'])

    def test_historical_single_dot_prefix_keeps_exact_raw_bindings_and_bytes(self):
        target = self.visual_old()
        p = target / U.UI_PATH
        p.write_text(p.read_text().replace('assets/icon.svg', './assets/icon.svg'))
        self.bind_old(target)
        self.customize(target, 'assets/local-icon.svg')
        journal = self.apply_visual()
        fields, *_ = U.visual_yaml((target / U.UI_PATH).read_text())
        self.assertEqual(fields['icon_small'], './assets/local-icon.svg')
        self.assertEqual(fields['icon_large'], './assets/local-icon.svg')
        self.assertEqual((target / 'assets/local-icon.svg').read_bytes(), b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy, journal)['ready'])

    def test_real_code_drift_is_not_hidden_by_visual_overlay(self):
        target = self.visual_old(); self.customize(target)
        (target / 'SKILL.md').write_text((target / 'SKILL.md').read_text() + 'Unapproved functional change\n')
        self.assertFalse(self.plan()['ready'])

    def test_policy_dependency_and_prompt_drift_remain_blockers(self):
        for before, after in [('allow_implicit_invocation: true', 'allow_implicit_invocation: false'),
                              ('exact-approved-tool', 'unapproved-tool'), ('Use the known fixture', 'Expand permissions')]:
            with self.subTest(before=before):
                target = self.visual_old(); self.customize(target)
                p = target / U.UI_PATH; p.write_text(p.read_text().replace(before, after))
                self.assertFalse(self.plan()['ready'])
                shutil.rmtree(target)

    def test_missing_icon_and_external_or_traversing_paths_are_rejected(self):
        for path in ['assets/missing.svg', '/outside/owner.svg', '../outside.svg', 'assets/../owner.svg', 'scripts/tool.py']:
            with self.subTest(path=path):
                target = self.visual_old()
                p = target / U.UI_PATH; p.write_text(p.read_text().replace('assets/icon.svg', path))
                with self.assertRaises(U.SuiteError):self.plan()
                shutil.rmtree(target)

    def test_icon_symlink_is_not_followed(self):
        target = self.visual_old(); (target / 'assets/icon.svg').unlink()
        (target / 'assets/icon.svg').symlink_to(self.kit / 'skills/agent-foundry/assets/icon.svg')
        with self.assertRaisesRegex(U.SuiteError, 'Link|Symlink'):self.plan()

    def test_icon_cannot_hide_changed_nonvisual_baseline_image(self):
        target = self.visual_old()
        (target / 'assets/reference.svg').write_bytes(b'Important reference')
        self.bind_old(target)
        self.customize(target, 'assets/reference.svg')
        self.assertFalse(self.plan()['ready'])

    def test_icon_cannot_overwrite_nonvisual_new_payload_file(self):
        target = self.visual_old(); self.customize(target, 'assets/reference.svg')
        source = self.kit / 'skills/agent-foundry'
        (source / 'assets/reference.svg').write_bytes(b'New accepted design reference')
        self.row()['files'] = U.snapshot(source)['files']; self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'nonvisual kit file'):self.plan()

    def test_duplicate_visual_fields_and_unsafe_color_rejected(self):
        for addition in ['  icon_small: assets/icon.svg\n', '  brand_color: "not-a-color"\n']:
            with self.subTest(addition=addition):
                target = self.visual_old()
                p = target / U.UI_PATH; p.write_text(p.read_text().replace('policy:\n', addition + 'policy:\n'))
                with self.assertRaises(U.SuiteError):self.plan()
                shutil.rmtree(target)

    def test_unsupported_visual_key_format_blocks_instead_of_silently_losing_identity(self):
        target = self.visual_old()
        p = target / U.UI_PATH
        p.write_text(p.read_text().replace('icon_small:', '"icon_small":'))
        with self.assertRaisesRegex(U.SuiteError, 'Unsupported visual field syntax'):self.plan()

    def test_icon_change_after_audit_blocks_before_backup(self):
        target = self.visual_old(); self.customize(target); self.plan()
        (target / 'assets/local-icon.svg').write_bytes(b'Changed after audit')
        with self.assertRaisesRegex(U.SuiteError, 'changed after audit'):U.apply_plan(self.plan_path)
        self.assertFalse(self.backups.exists())

    def test_forged_overlay_cannot_add_arbitrary_script(self):
        target = self.visual_old(); self.customize(target); plan = self.plan()
        entry = next(x for x in plan['entries'] if x['name'] == 'agent-foundry')
        entry['visual_preservation']['files']['scripts/unapproved.py'] = dict(entry['before']['files']['SKILL.md'])
        self.plan_path.write_bytes(U.encode(plan))
        with self.assertRaisesRegex(U.SuiteError, 'overlay differs'):U.apply_plan(self.plan_path)

    def test_forged_predecessor_yaml_binding_is_rejected(self):
        self.visual_old()
        self.row()['previous_trees'][-1]['ui_yaml'] += 'policy: unapproved\n'; self.write_manifest()
        with self.assertRaisesRegex(U.SuiteError, 'YAML hash mismatch'):U.read_kit(self.kit)

    def test_repeated_apply_and_fresh_noop_keep_icons(self):
        target = self.visual_old(); self.customize(target); journal = self.apply_visual()
        after = U.snapshot(target)
        self.assertEqual(U.apply_plan(self.plan_path)['status'], 'already_applied')
        plan = self.plan(); self.assertTrue(all(x['action'] == 'noop' for x in plan['entries']))
        journal2 = Path(U.apply_plan(self.plan_path)['journal'])
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy, journal2)['ready'])
        self.assertEqual(U.snapshot(target), after)
        self.assertNotEqual(journal, journal2)

    def test_next_release_preserves_existing_custom_identity(self):
        target = self.visual_old(); self.customize(target); self.apply_visual()
        row = self.row(); source = self.kit / 'skills/agent-foundry'
        row['previous_trees'].append({'tree_sha256': U.logical_sha(row['files']), 'source': 'Previous canonical release',
                                      'files': row['files'], 'ui_yaml': (source / U.UI_PATH).read_text()})
        (source / U.UI_PATH).write_text(self.ui('5.1.0'))
        (source / 'SKILL.md').write_text((source / 'SKILL.md').read_text() + 'A new release\n')
        row['files'] = U.snapshot(source)['files']; row['version'] = '5.1.0'; self.manifest['suite_id'] = 'synthetic-next'
        self.write_manifest(); journal = self.apply_visual()
        self.assertIn('5.1.0', (target / U.UI_PATH).read_text())
        self.assertEqual((target / 'assets/local-icon.svg').read_bytes(), b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy, journal)['ready'])

    def test_post_update_icon_change_fails_receipt_verification_and_rollback(self):
        target = self.visual_old(); self.customize(target); journal = self.apply_visual()
        (target / 'assets/local-icon.svg').write_bytes(b'Owner change after installation')
        self.assertFalse(U.verify(self.kit, self.dest, self.legacy, journal)['ready'])
        with self.assertRaisesRegex(U.SuiteError, 'overwrite work'):U.rollback(journal)

    def test_case_alias_cannot_make_nonportable_effective_payload(self):
        target = self.visual_old(); self.customize(target, 'assets/Icon.svg')
        with self.assertRaisesRegex(U.SuiteError, 'case/Unicode'):self.plan()

    def test_custom_icons_resume_after_old_tree_move(self):
        target = self.visual_old(); self.customize(target); self.plan()
        real = os.replace; failed = [False]
        def interrupted(source, dest):
            real(source, dest)
            if Path(source) == target and Path(dest).name == 'old' and not failed[0]:
                failed[0] = True
                raise OSError('Synthetic interruption after icon-preserving old move')
        with mock.patch.object(U.os, 'replace', side_effect=interrupted):
            with self.assertRaises(OSError):U.apply_plan(self.plan_path)
        journal = self.latest_journal()
        U.apply_plan(self.plan_path, resume=journal)
        self.assertEqual((target / 'assets/local-icon.svg').read_bytes(), b'<svg>OWNER IDENTITY - keep exact bytes</svg>')
        self.assertTrue(U.verify(self.kit, self.dest, self.legacy, journal)['ready'])


if __name__ == '__main__':
    unittest.main()
