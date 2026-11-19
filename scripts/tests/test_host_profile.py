import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
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
        (repo / 'releases').mkdir()
        shutil.copy2(ROOT / 'releases/current.json', repo / 'releases/current.json')
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
        self.assertIn('production profile 6.4.0', installed)
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
        self.assertIn('then English', H.read(self.instructions))
        self.assertIn('Owner appendix.', H.read(self.instructions))
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(self.instructions), before)

    def test_installed_62_upgrades_exactly_and_preserves_unknown_drift(self):
        relative,expected=H.PREVIOUS_PROFILE_TEMPLATES[2]
        template=H.read(ROOT/relative)
        self.assertEqual(H.sha(template),expected)
        before='Owner prefix.\n'+template.replace('{{STANDARD_ROOT}}',str(self.standard))+'Owner suffix.\n'
        self.instructions.write_bytes(before.encode('utf8'))
        self.make_plan();H.apply(self.plan,self.journal)
        installed=H.read(self.instructions)
        self.assertIn('production profile 6.4.0',installed)
        self.assertIn('AGENT_SYSTEM_PYTHON',installed)
        self.assertIn('preserve a working project PATH',installed)
        H.verify_or_rollback(self.journal,rollback=True)
        self.assertEqual(self.instructions.read_bytes(),before.encode('utf8'))
        drift=before.replace('production profile 6.2.0','production profile 6.2.0\nCustom owner instruction.')
        self.instructions.write_bytes(drift.encode('utf8'))
        with self.assertRaisesRegex(ValueError,'unknown customized managed profile'):
            H.audit(ROOT,self.codex,self.standard)
        self.assertEqual(self.instructions.read_bytes(),drift.encode('utf8'))

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

    def predecessor_role(self, filename):
        canonical = H.read(ROOT / 'agent-profiles' / filename)
        body, _ = H.role_parts(canonical)
        language = ('Use the task or project preferred language, with Ukrainian as the default when none is set.'
                    if filename == 'foundry-qa.toml' else
                    'Use the parent task/project preferred language; default to Ukrainian only when no preference is set.')
        return body.replace(
            'Use the explicit output language of the assigned action, then the saved language of its project or originating surface, then English. Preserve original quotations and source literals.',
            language,
        )

    def test_approved_predecessors_migrate_model_and_preserve_equivalent_effort_and_unmanaged_files(self):
        agents = self.codex / 'agents'
        agents.mkdir()
        cost_target, qa_target = agents / 'foundry-cost.toml', agents / 'foundry-qa.toml'
        local_cost = self.predecessor_role(cost_target.name)
        local_qa = self.predecessor_role(qa_target.name)
        local_qa += 'model = "gpt-6.1-sol" # managed model_reasoning_effort = "high"\n'
        local_qa += "model_reasoning_effort = 'ultra' # local effort\n"
        cost_target.write_bytes(local_cost.encode())
        qa_target.write_bytes(local_qa.encode())
        unmanaged = {self.codex / 'config.toml': 'model = "gpt-6.1-sol"\n',
                     agents / 'unrelated.toml': 'model = "foreign-model"\n'}
        for path, text in unmanaged.items():
            path.write_text(text)
        self.make_plan()
        rows = {Path(row['target']).name: row for row in H.load(self.plan)['changes']}
        for target, local in ((cost_target, local_cost), (qa_target, local_qa)):
            with self.subTest(role=target.name):
                row = rows[target.name]
                self.assertIn('then English', row['desired'])
                self.assertNotIn('default to Ukrainian', row['desired'])
                self.assertNotIn('gpt-6.1-sol', row['desired'])
                self.assertIn('gpt-6.2-sol', row['desired'])
                self.assertEqual(row['before_sha256'], H.sha(local))
        self.assertIn("model_reasoning_effort = 'ultra' # local effort", rows[qa_target.name]['desired'])
        self.assertIn('model = "gpt-6.2-sol" # managed model_reasoning_effort = "high"\n', rows[qa_target.name]['desired'])
        self.assertIn('model_reasoning_effort = "ultra"', rows[cost_target.name]['desired'])
        H.apply(self.plan, self.journal)
        self.assertTrue(H.verify_or_rollback(self.journal)['ok'])
        self.assertEqual(H.read(qa_target), rows[qa_target.name]['desired'])
        for path, text in unmanaged.items():
            self.assertEqual(H.read(path), text)
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(cost_target.read_bytes(), local_cost.encode())
        self.assertEqual(qa_target.read_bytes(), local_qa.encode())

    def test_foreign_model_on_exact_predecessor_body_has_local_review_paths(self):
        (self.codex / 'agents').mkdir()
        target = self.codex / 'agents/foundry-qa.toml'
        local = self.predecessor_role(target.name) + 'model = "provider/model:1"\n'
        target.write_text(local)
        with self.assertRaisesRegex(ValueError, 'Local model provider/model:1 has no managed migration') as error:
            self.make_plan()
        self.assertIn(str(target), str(error.exception))
        self.assertIn(str(ROOT / 'agent-profiles' / target.name), str(error.exception))
        self.assertEqual(H.read(target), local)
        self.assertFalse(self.plan.exists())

    def test_audit_conflict_diff_is_private_and_preserves_unknown_effort(self):
        (self.codex / 'agents').mkdir()
        target = self.codex / 'agents/foundry-qa.toml'
        current = self.predecessor_role(target.name) + 'model_reasoning_effort = "minimal"\n'
        target.write_text(current)
        diff = self.folder / 'private.diff'
        result = subprocess.run(
            [sys.executable, '-B', str(ROOT / 'scripts/install_host_profile.py'),
             'audit', '--codex-root', str(self.codex), '--standard-root', str(self.standard),
             '--plan', str(self.plan), '--conflict-diff', str(diff)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        receipt = json.loads(result.stdout)
        self.assertIn('Local reasoning effort minimal differs from managed ultra', receipt['error'])
        self.assertEqual(receipt['conflict_diff'], str(diff))
        self.assertIn('-model_reasoning_effort = "minimal"', H.read(diff))
        self.assertIn('+model_reasoning_effort = "ultra"', H.read(diff))
        self.assertEqual(H.read(target), current)
        self.assertFalse(self.plan.exists())

    def test_exact_high_candidate_migrates_but_custom_lower_effort_conflicts(self):
        agents = self.codex / 'agents'
        agents.mkdir()
        target = agents / 'foundry-qa.toml'
        canonical = H.read(ROOT / 'agent-profiles' / target.name)
        prior = canonical.replace('model_reasoning_effort = "ultra"', 'model_reasoning_effort = "high"')
        self.assertIn(H.sha(prior), next(row for row in H.load(ROOT / 'agent-profiles/manifest.json')['roles']
                                         if row['file'] == target.name)['previous_sha256'])
        target.write_text(prior)
        self.make_plan()
        H.apply(self.plan, self.journal)
        self.assertEqual(H.read(target), canonical)
        H.verify_or_rollback(self.journal, rollback=True)
        self.assertEqual(H.read(target), prior)

        custom = prior.replace('model_reasoning_effort = "high"', 'model_reasoning_effort = "high" # owner choice')
        target.write_text(custom)
        with self.assertRaisesRegex(H.ProfileConflict, 'Local reasoning effort high differs from managed ultra') as error:
            H.audit(ROOT, self.codex, self.standard)
        self.assertIn('+model_reasoning_effort = "ultra"', error.exception.diff())
        self.assertEqual(H.read(target), custom)

    def test_policy_changed_after_audit_prevents_any_apply(self):
        repo = self.copy_repo()
        H.save(self.plan, H.audit(repo, self.codex, self.standard))
        path = repo / 'releases/current.json'
        path.write_text(H.read(path) + '\n')
        with self.assertRaisesRegex(ValueError, 'managed release policy or role manifest changed since audit'):
            H.apply(self.plan, self.journal)
        self.assertFalse(self.journal.exists())
        self.assertEqual(H.read(self.instructions), 'Existing owner instructions.\n')

    def test_invalid_selectors_or_role_edits_are_not_recognized_as_tuning(self):
        (self.codex / 'agents').mkdir()
        target = self.codex / 'agents/foundry-cost.toml'
        canonical = H.read(ROOT / 'agent-profiles/foundry-cost.toml')
        edited = {
            'duplicate': canonical + 'model = "gpt-6-sol"\n',
            'quoted duplicate': canonical + '"model" = "gpt-6-sol"\n',
            'unknown role field': canonical + 'sandbox_mode = "workspace-write"\n',
            'invalid selector type': canonical.replace('"gpt-6.2-sol"', 'false'),
            'unknown effort': canonical.replace('"ultra"', '"enormous"'),
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
        target.write_bytes(canonical.replace('"ultra"', "'ultra' # preserved comment").encode())
        self.make_plan()
        updated = canonical.replace('"ultra"', "'ultra' # changed after audit")
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
