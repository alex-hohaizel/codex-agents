import importlib.util
import json
from pathlib import Path
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
