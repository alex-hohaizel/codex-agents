import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bmad_module as mod


class BmadModuleTest(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name).resolve()
        self.project = self.root / "project"
        self.project.mkdir()
        self.source = self.root / "sources"
        self.record = self.source / "bmod-dock"
        self.owner = self.source / "dock-review"
        self.args = argparse.Namespace(project=self.project, source=[self.source], previous=[],
                                       legacy_version=None, previous_legacy_version=None, legacy_runtime=None,
                                       license=[], change_set=None, output=self.root / "staged")
        self.skill(self.record, "dock")
        self.skill(self.owner, "source-pin")
        self.write(self.record / "bmod.toml", """
[bmod]
code = "dock"
version = "2.1.0"
update_source = "github:example/dock/skills"
skills = ["dock-review"]
recommended_skills = ["dock-eval"]
""")
        self.write(self.owner / "bmod.toml", """
[skill]
bmod = "bmod-dock"
source = "github:example/dock/skills"
scripts = ["scripts/report.py"]
""")
        self.write(self.owner / "scripts/report.py", 'raise RuntimeError("No import-time execution")\n')
        self.write(self.record / "help/help.md", "# Dock review\n")
        self.write(self.record / "doc-templates/template-report.md", "# Open risks\n")
        self.write(self.record / "roster.toml", '[[members]]\ncode = "dock-review"\nskill = "dock-review"\n')
        self.write(self.record / "retired.toml", 'renamed = [{from="dock-audit",to="dock-review"}]\nremoved = ["dock-old"]\n')
        self.guide = self.record / "migration-2.toml"
        self.write(self.guide, """
[migration]
module = "dock"
from = "1"
to = "2"
title = "Move a report"
summary = "Keep evidence within the ticket folder."
detect = "An audit outside tickets/"
guide = "Move report and update the source reference"
checklist = ["Review the report using the new location."]
""")

    def write(self, path, text):
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(text, encoding="utf-8")
        return path

    def skill(self, path, description):
        self.write(path / "SKILL.md",
                   f"---\nname: {path.name}\ndescription: {description}\n---\n\nRead the review evidence.\n")

    def change_set(self):
        evidence = self.write(self.project / "_bmad-output/old/audit.md", "Source: inspection 42.\n")
        companion = self.write(self.project / "_bmad-output/links.md", "Audit at audit.md.\n")
        replacement = self.write(self.root / "new-links.md", "Audit at tickets/audit.md.\n")
        self.args.change_set = self.write(self.root / "changes.json", json.dumps({
            "schema": "bmad-project-migration/1", "module": "dock", "number": 2,
            "definition_sha256": mod.fs.digest(self.guide.read_bytes()), "roots": ["_bmad-output"],
            "files": [
                {"path": "_bmad-output/old/audit.md", "sha256": mod.fs.digest(evidence.read_bytes()),
                 "to": "_bmad-output/tickets/audit.md"},
                {"path": "_bmad-output/links.md", "sha256": mod.fs.digest(companion.read_bytes()),
                 "to": "_bmad-output/links.md", "replacement": replacement.name},
            ],
        }))
        return evidence, companion

    def test_exact_rehearsal_preserves_personal_configuration_and_source(self):
        team = self.write(self.project / "_bmad/custom/dock-audit.toml", '[agent]\nrole = "team"\n')
        personal = self.write(self.project / "_bmad/custom/dock-audit.user.toml", '[agent]\nrole = "personal"\n')
        retired = self.write(self.project / "_bmad/custom/dock-old.toml", '[workflow]\nvalue = "retired"\n')
        evidence, companion = self.change_set()
        plan, _ = mod.audit(self.args)
        self.assertTrue(plan["ready"])
        self.assertEqual([row["status"] for row in plan["dependencies"]], ["missing"])
        self.assertEqual(plan["migration"]["guide_checklist_pending"], ["Review the report using the new location."])
        self.args.expect = plan["plan_sha256"]
        receipt = mod.stage(self.args)
        stage = self.args.output
        self.assertEqual(receipt["source_project_writes"], 0)
        self.assertEqual(receipt["hooks_executed"], 0)
        for original, name in ((team, "dock-review.toml"), (personal, "dock-review.user.toml"), (retired, retired.name)):
            self.assertEqual((stage / "_bmad/custom" / name).read_bytes(), original.read_bytes())
        self.assertEqual((stage / "_bmad/custom/dock-review.user.toml").stat().st_mode & 0o777, 0o600)
        self.assertEqual((stage / "_bmad-output/tickets/audit.md").read_bytes(), evidence.read_bytes())
        self.assertFalse((stage / "_bmad-output/old").exists())
        self.assertTrue(evidence.is_file())
        self.assertIn("tickets/audit.md", (stage / "_bmad-output/links.md").read_text())
        self.assertEqual(companion.read_text(), "Audit at audit.md.\n")
        self.assertTrue((stage / ".agents/skills/bmod-dock/doc-templates/template-report.md").is_file())
        self.assertTrue((stage / "_bmad/dock/scripts/report.py").is_file())
        self.assertTrue(mod.verify(stage, self.args.expect)["ready"])
        (stage / "_bmad-output/tickets/audit.md").write_text("drift")
        with self.assertRaisesRegex(ValueError, "differ from the reviewed plan"):
            mod.verify(stage, self.args.expect)

    def test_required_dependencies_and_existing_overrides_are_blockers(self):
        self.write(self.record / "bmod.toml", (self.record / "bmod.toml").read_text()
                   + 'required_skills = ["dock-backend"]\n')
        self.write(self.project / "_bmad/custom/dock-audit.toml", "[agent]\n")
        self.write(self.project / "_bmad/custom/dock-review.toml", "[agent]\n")
        self.skill(self.project / ".agents/skills/dock-review", "local edited")
        plan, _ = mod.audit(self.args)
        self.assertFalse(plan["ready"])
        self.assertEqual(len(plan["blockers"]), 3)
        self.args.expect = plan["plan_sha256"]
        with self.assertRaisesRegex(ValueError, "Resolve plan blockers"):
            mod.stage(self.args)
        self.assertFalse(self.args.output.exists())

    def test_stale_plan_cannot_use_changed_input(self):
        evidence, _ = self.change_set()
        plan, _ = mod.audit(self.args)
        self.args.expect = plan["plan_sha256"]
        evidence.write_text("new inspection")
        with self.assertRaisesRegex(ValueError, "Migration source changed"):
            mod.stage(self.args)
        self.assertFalse(self.args.output.exists())

    def test_old_version_matches_exact_native_snapshot(self):
        previous = self.root / "previous"
        self.skill(previous / "dock-review", "old approved skill")
        self.write(previous / "dock-review/bmod.toml", """
[bmod]
code = "dock"
version = "1.0.0"
update_source = "github:example/dock/skills"
[skill]
""")
        self.write(previous / "dock-review/help/help.md", "# Old help\n")
        import shutil
        target = self.project / ".agents/skills/dock-review"
        shutil.copytree(previous / "dock-review", target)
        self.args.previous = [previous]
        self.assertEqual(mod.audit(self.args)[0]["target_entries"][0]["classification"], "reviewed-previous")
        (target / "local-change.txt").write_text("unreviewed")
        self.assertFalse(mod.audit(self.args)[0]["ready"])

    @unittest.skipUnless(importlib.util.find_spec("yaml"), "Legacy YAML support needs PyYAML")
    def test_legacy_yaml_help_and_skill_shims(self):
        legacy = self.root / "legacy"
        self.write(legacy / "module.yaml", 'code: core\nname: Stable core\n')
        self.write(legacy / "module-help.csv", "skill,display-name\ndock-compat,Dock compatibility\n")
        self.skill(legacy / "v6-shims/dock-compat", "Handle a prior invocation")
        self.args.source = [legacy]
        self.args.legacy_version = "6.12.4"
        self.args.convert_legacy = "file:/reviewed/dock"
        plan, _ = mod.audit(self.args)
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["modules"][0]["metadata"]["catalog"][0]["skill"], "dock-compat")
        self.args.expect = plan["plan_sha256"]
        mod.stage(self.args)
        self.assertTrue((self.args.output / ".agents/skills/dock-compat/SKILL.md").is_file())
        self.assertTrue((self.args.output / ".bmad-import/modules/core/module-help.csv").is_file())
        converted = mod.read_modules([self.args.output / ".agents/skills"], None)["core"]
        self.assertEqual(converted.format, "bmod")
        self.assertEqual(list(converted.registrations), ["dock-compat"])
