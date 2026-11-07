"""Regression fixtures for stale instructions and unavailable local commands."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from check_consistency import check


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('scripts','assets','references'):(self.root/name).mkdir()
        self.skill='---\nname: fixture\ndescription: Offline fixture.\n---\n\n# Fixture\n\nRun `python3 scripts/check.py record.json --ready`.\n'
        self.config={'schema_version':'skill.consistency/1','container_kind':'blueprint','current_checker':'check.py','root_required_flags':['--ready'],'history_documents':['references/legacy-records.md'],'canonical_stage':None}
        (self.root/'SKILL.md').write_text(self.skill)
        (self.root/'scripts/check.py').write_text('parser.add_argument("--ready")\n')
        self.save_config()
    def save_config(self):
        (self.root/'assets/consistency-contract.json').write_text(json.dumps(self.config))
    def test_coherent_local_route_passes(self):self.assertEqual(check(self.root),[])
    def test_old_parent_method_pin_is_rejected(self):
        (self.root/'references/old.md').write_text('Використовувати правила Іскри 5.0.')
        self.assertTrue(any('edition pin' in e for e in check(self.root)))
    def test_primary_source_date_is_preserved(self):
        (self.root/'references/sources.md').write_text('Досліджений раунд Іскри 29.10.2026. Paid use, редакція 03.09.2026.')
        self.assertEqual(check(self.root),[])
    def test_non_tool_project_filename_does_not_create_a_dependency(self):
        (self.root/'SKILL.md').write_text(self.skill+'Майбутній вихідний файл проєкту може називатися app.py.\n')
        self.assertEqual(check(self.root),[])
    def test_unavailable_sibling_command_is_rejected(self):
        (self.root/'SKILL.md').write_text(self.skill+'Виконати `pipeline.py check --ready`.\n')
        self.assertTrue(any('unavailable local script' in e for e in check(self.root)))
    def test_broken_link_is_rejected(self):
        (self.root/'SKILL.md').write_text(self.skill+'[Reference](references/missing.md)\n')
        self.assertTrue(any('broken local' in e for e in check(self.root)))
    def test_hidden_sibling_filesystem_dependency_is_rejected(self):
        (self.root/'SKILL.md').write_text(self.skill+'[Other](../another-skill/SKILL.md)\n')
        self.assertTrue(any('hidden external' in e for e in check(self.root)))
    def test_old_staff_instruction_is_rejected_in_active_reference(self):
        (self.root/'references/team.md').write_text('Зберегти канонічних 23 base і 28 stage specialist/judge.')
        self.assertTrue(any('historical staff' in e for e in check(self.root)))
    def test_history_is_separate_from_current_instructions(self):
        (self.root/'references/legacy-records.md').write_text('Історичний формат. Зберегти канонічних 23 base і 28 stage specialist/judge.')
        self.assertEqual(check(self.root),[])
    def test_missing_current_flag_is_rejected(self):
        (self.root/'SKILL.md').write_text(self.skill.replace(' --ready',''))
        self.assertTrue(any('route omits' in e for e in check(self.root)))


if __name__=='__main__':unittest.main()
