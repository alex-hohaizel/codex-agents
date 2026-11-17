import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('profile', ROOT / 'scripts/install_host_profile.py')
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)


class HostProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.codex = self.folder / 'codex'
        self.codex.mkdir()
        self.instructions = self.codex / 'AGENTS.md'
        self.instructions.write_text('Existing owner instructions.\n')
        self.plan = self.folder / 'plan.json'
        self.journal = self.folder / 'journal.json'
        self.standard = self.folder / 'skills/agent-foundry'

    def make_plan(self):
        H.save(self.plan, H.audit(ROOT, self.codex, self.standard))

    def copy_repo(self):
        repo = self.folder / 'repo'
        shutil.copytree(ROOT / 'host-profiles', repo / 'host-profiles')
        shutil.copytree(ROOT / 'agent-profiles', repo / 'agent-profiles')
        return repo

    def old_profile(self):
        relative, expected = H.PREVIOUS_PROFILE_TEMPLATES[0]
        raw = H.read(ROOT / relative)
        self.assertEqual(H.sha(raw), expected)
        return raw.replace('{{STANDARD_ROOT}}', str(self.standard)).strip()

    def test_exact_previous_profile_upgrades_preserving_outside_bytes_and_rollback(self):
        before = 'Owner prefix.\r\n\r\n' + self.old_profile() + '\r\n\r\nOwner suffix.\r\n'
        self.instructions.write_bytes(before.encode('utf-8'))
        self.make_plan()
        plan = H.load(self.plan)
        self.assertEqual(len(plan['changes'][0]['compatibility_sources']), len(H.PREVIOUS_PROFILE_TEMPLATES))
        H.apply(self.plan, self.journal)
        installed = H.read(self.instructions)
        self.assertTrue(installed.startswith('Owner prefix.\r\n\r\n'))
        self.assertTrue(installed.endswith('\r\n\r\nOwner suffix.\r\n'))
        self.assertIn('production profile 6.2.0', installed)
        self.assertNotIn('production profile 6.0.0', installed)
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(self.instructions.read_bytes(), before.encode('utf-8'))

    def test_installed_61_can_update_and_roll_back_with_role_settings(self):
        path, expected = H.PREVIOUS_PROFILE_TEMPLATES[1]
        prior = H.read(ROOT / path)
        self.assertEqual(H.sha(prior), expected)
        before = prior.replace('{{STANDARD_ROOT}}', str(self.standard)) + '\nOwner appendix.\n'
        self.instructions.write_text(before)
        self.make_plan()
        H.apply(self.plan, self.journal)
        self.assertIn('then the language of the request', H.read(self.instructions))
        self.assertIn('Owner appendix.', H.read(self.instructions))
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(self.instructions), before)

    def test_unknown_change_inside_managed_block_is_not_overwritten(self):
        customized = self.old_profile().replace(H.END, 'Keep this owner policy.\n' + H.END)
        before = 'Before\n' + customized + '\nAfter\n'
        self.instructions.write_text(before)
        with self.assertRaisesRegex(ValueError, 'unknown customized managed profile; reconcile without overwrite'):
            self.make_plan()
        self.assertEqual(H.read(self.instructions), before)
        self.assertFalse(self.plan.exists())
        self.assertFalse((self.codex / 'agents').exists())

    def test_current_exact_block_remains_idempotent(self):
        self.make_plan()
        H.apply(self.plan, self.journal)
        before = self.instructions.read_bytes()
        plan = H.audit(ROOT, self.codex, self.standard)
        self.assertEqual(plan['changes'][0]['before_sha256'], plan['changes'][0]['after_sha256'])
        self.assertEqual(plan['changes'][0]['desired'].encode('utf-8'), before)

    def test_tampered_trusted_predecessor_is_rejected_before_audit(self):
        repo = self.copy_repo()
        relative, _ = H.PREVIOUS_PROFILE_TEMPLATES[0]
        history = repo / relative
        history.write_text(H.read(history) + 'Unreviewed source.\n')
        before = self.old_profile() + '\n'
        self.instructions.write_text(before)
        with self.assertRaisesRegex(ValueError, 'trusted prior profile source drift'):
            H.audit(repo, self.codex, self.standard)
        self.assertEqual(H.read(self.instructions), before)

    def test_predecessor_source_changed_after_audit_blocks_apply(self):
        repo = self.copy_repo()
        H.save(self.plan, H.audit(repo, self.codex, self.standard))
        history = repo / H.PREVIOUS_PROFILE_TEMPLATES[0][0]
        history.write_text(H.read(history) + 'Later change.\n')
        with self.assertRaisesRegex(ValueError, 'prior profile source changed since audit'):
            H.apply(self.plan, self.journal)
        self.assertEqual(H.read(self.instructions), 'Existing owner instructions.\n')
        self.assertFalse(self.journal.exists())

    def test_linked_predecessor_is_not_a_trusted_regular_source(self):
        repo = self.copy_repo()
        relative, _ = H.PREVIOUS_PROFILE_TEMPLATES[0]
        history = repo / relative
        history.unlink()
        history.symlink_to(ROOT / relative)
        with self.assertRaisesRegex(ValueError, 'symlink path rejected'):
            H.audit(repo, self.codex, self.standard)
        self.assertEqual(H.read(self.instructions), 'Existing owner instructions.\n')

    def test_later_inside_block_change_blocks_rollback_without_overwrite(self):
        self.make_plan()
        H.apply(self.plan, self.journal)
        later = H.read(self.instructions).replace(H.END, 'New owner rule.\n' + H.END)
        self.instructions.write_text(later)
        with self.assertRaisesRegex(ValueError, 'preserve later work'):
            H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(self.instructions), later)

    def test_legacy_plan_and_journal_without_compatibility_metadata_stay_supported(self):
        plan = H.audit(ROOT, self.codex, self.standard)
        plan['changes'][0].pop('compatibility_sources')
        H.save(self.plan, plan)
        H.apply(self.plan, self.journal)
        self.assertNotIn('compatibility_sources', H.load(self.journal)['changes'][0])
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(self.instructions), 'Existing owner instructions.\n')

    def test_verify_and_rollback_use_actual_journal_without_repository_history(self):
        repo = self.copy_repo()
        before = self.old_profile() + '\n'
        self.instructions.write_text(before)
        H.save(self.plan, H.audit(repo, self.codex, self.standard))
        H.apply(self.plan, self.journal)
        (repo / H.PREVIOUS_PROFILE_TEMPLATES[0][0]).unlink()
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(self.instructions), before)

    def test_apply_preserves_unmanaged_instructions_and_exact_rollback(self):
        self.make_plan()
        H.apply(self.plan, self.journal)
        installed = self.instructions.read_text()
        self.assertTrue(installed.startswith('Existing owner instructions.\n'))
        self.assertEqual(installed.count(H.START), 1)
        self.assertNotIn('{{STANDARD_ROOT}}', installed)
        self.assertFalse(H.verify_or_rollback(self.journal)['host_discovery_verified'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(self.instructions.read_text(), 'Existing owner instructions.\n')
        self.assertFalse((self.codex / 'agents/foundry-qa.toml').exists())

    def test_unknown_role_customization_is_not_overwritten(self):
        (self.codex / 'agents').mkdir()
        (self.codex / 'agents/foundry-qa.toml').write_text('unknown local customization')
        with self.assertRaisesRegex(ValueError, 'unknown customized role'):
            self.make_plan()

    def test_audit_preserves_exact_role_bytes_with_omitted_or_local_selectors(self):
        agents = self.codex / 'agents'
        agents.mkdir()
        cost_source = H.read(ROOT / 'agent-profiles/foundry-cost.toml')
        qa_source = H.read(ROOT / 'agent-profiles/foundry-qa.toml')
        cost_target, qa_target = agents / 'foundry-cost.toml', agents / 'foundry-qa.toml'
        local_cost = cost_source.replace('model = "gpt-6-luna"\nmodel_reasoning_effort = "medium"\n', '')
        local_qa = qa_source + "model = 'provider/model:1' # local selection\nmodel_reasoning_effort = 'high'\n"
        cost_target.write_bytes(local_cost.encode())
        qa_target.write_bytes(local_qa.encode())
        self.make_plan()
        rows = {Path(row['target']).name: row for row in H.load(self.plan)['changes']}
        for name, local, canonical in (('foundry-cost.toml', local_cost, cost_source),
                                       ('foundry-qa.toml', local_qa, qa_source)):
            with self.subTest(name=name):
                row = rows[name]
                self.assertEqual(row['desired'], local)
                self.assertEqual(row['source_sha256'], H.sha(canonical))
                self.assertEqual(row['before_sha256'], H.sha(local))
                self.assertEqual(row['after_sha256'], H.sha(local))
        H.apply(self.plan, self.journal)
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(cost_target.read_bytes(), local_cost.encode())
        self.assertEqual(qa_target.read_bytes(), local_qa.encode())

    def test_invalid_selectors_or_role_edits_are_not_recognized_as_tuning(self):
        (self.codex / 'agents').mkdir()
        target = self.codex / 'agents/foundry-cost.toml'
        canonical = H.read(ROOT / 'agent-profiles/foundry-cost.toml')
        edited = {
            'duplicate': canonical + 'model = "gpt-6-sol"\n',
            'quoted duplicate': canonical + '"model" = "gpt-6-sol"\n',
            'unknown role field': canonical + 'sandbox_mode = "workspace-write"\n',
            'invalid selector type': canonical.replace('"gpt-6-luna"', 'false'),
            'unknown effort': canonical.replace('"medium"', '"enormous"'),
            'role identity': canonical.replace('name = "foundry-cost"', 'name = "other-role"'),
            'description': canonical.replace('Cost and performance auditor.', 'Other description.'),
            'selector-like instruction': canonical.replace('developer_instructions = """\n',
                                                           'developer_instructions = """\nmodel = "inner"\n'),
        }
        for reason, text in edited.items():
            with self.subTest(reason=reason):
                target.write_bytes(text.encode())
                with self.assertRaisesRegex(ValueError, 'unknown customized role'):
                    self.make_plan()
                self.assertEqual(target.read_bytes(), text.encode())
                self.assertFalse(self.plan.exists())

    def test_change_to_preserved_local_tuning_after_audit_blocks_apply(self):
        (self.codex / 'agents').mkdir()
        target = self.codex / 'agents/foundry-cost.toml'
        canonical = H.read(ROOT / 'agent-profiles/foundry-cost.toml')
        target.write_bytes(canonical.replace('"medium"', '"high"').encode())
        self.make_plan()
        updated = canonical.replace('"medium"', '"low"')
        target.write_bytes(updated.encode())
        with self.assertRaisesRegex(ValueError, 'target changed since audit'):
            H.apply(self.plan, self.journal)
        self.assertEqual(target.read_bytes(), updated.encode())
        self.assertFalse(self.journal.exists())

    def test_stale_plan_and_later_edit_block_apply_and_rollback(self):
        self.make_plan()
        self.instructions.write_text('Newer owner change')
        with self.assertRaisesRegex(ValueError, 'changed since audit'):
            H.apply(self.plan, self.journal)
        self.assertEqual(self.instructions.read_text(), 'Newer owner change')
        self.make_plan()
        H.apply(self.plan, self.journal)
        self.instructions.write_text(self.instructions.read_text() + '\nLater work\n')
        with self.assertRaisesRegex(ValueError, 'preserve later work'):
            H.verify_or_rollback(self.journal, rollback=True)

    def test_duplicate_markers_and_json_admission_rejected(self):
        with self.assertRaises(ValueError):
            H.merge(H.START + H.START + H.END, 'new')
        self.plan.write_text('{"changes":[],"changes":[1]}')
        with self.assertRaises(ValueError):
            H.load(self.plan)


    def test_resume_rejects_forged_journal_target_and_keeps_outside_file(self):
        self.make_plan(); H.apply(self.plan, self.journal)
        outside = self.folder / 'outside'; outside.write_text('preserve')
        journal = H.load(self.journal)
        journal['changes'][0].update(target=str(outside), desired='forged', after_sha256=H.sha('forged'), before='preserve', before_sha256=H.sha('preserve'))
        H.save(self.journal, journal)
        with self.assertRaisesRegex(ValueError, 'outside managed|differs from exact plan'):
            H.apply(self.plan, self.journal)
        self.assertEqual(outside.read_text(), 'preserve')

    def test_resume_rejects_in_scope_forgery_and_changed_backup(self):
        self.make_plan(); H.apply(self.plan, self.journal)
        original = H.load(self.journal)
        forged = H.load(self.journal)
        forged['changes'][0].update(desired='forged', after_sha256=H.sha('forged'))
        H.save(self.journal, forged)
        with self.assertRaisesRegex(ValueError, 'differs from exact plan'):
            H.apply(self.plan, self.journal)
        H.save(self.journal, original)
        original['changes'][0]['before'] = 'false backup'
        H.save(self.journal, original)
        with self.assertRaisesRegex(ValueError, 'backup changed'):
            H.verify_or_rollback(self.journal, rollback=True)
        self.assertIn(H.START, self.instructions.read_text())


if __name__ == '__main__':
    unittest.main()
