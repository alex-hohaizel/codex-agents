import importlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import_codex = importlib.import_module("import_codex")


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        self.addCleanup(self.context.cleanup)
        self.root = Path(self.context.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        self.target = self.root / "project"
        self.target.mkdir()
        self.manifest = self.source / "import.json"
        self.output = self.root / "preview"
        self.skill = self.source / "receipt-reader"
        self.skill.mkdir()
        self.entry = self.skill / "SKILL.md"
        self.entry.write_bytes(
            b"---\r\nname: receipt-reader\r\n"
            b"description: Parse the fixture's receipt records.\r\n---\r\n"
            b"Original prompt.\r\n"
        )
        script = self.skill / "parse.py"
        script.write_text("print('verified-import-fixture')\n")
        script.chmod(0o755)
        (self.skill / "assets").mkdir()
        (self.skill / "agents").mkdir()
        (self.skill / "agents/openai.yaml").write_text(
            'interface:\n  brand_color: "#247F69"\npolicy:\n  allow_implicit_invocation: false\n'
        )
        self.module = {
            "id": "ledger",
            "version": "1.2.3",
            "members": [{"kind": "skill", "name": "receipt-reader", "source": "receipt-reader"}],
            "optional": ["reports"],
        }

    def write_manifest(self, modules=None, overlays=None):
        record = {"schema": import_codex.SCHEMA, "modules": modules or [self.module]}
        if overlays is not None:
            record["customizations"] = overlays
        self.manifest.write_bytes(import_codex.files.encode(record))

    def overlay(self, scope, mode, name, expected, kind="skill", member="receipt-reader"):
        return {"scope": scope, "mode": mode, "name": member, "kind": kind,
                "source": name, "expected_sha256": import_codex.files.digest(expected)}

    def audit(self):
        return import_codex.audit(self.manifest, self.target)[0]

    def stage(self, plan):
        return import_codex.stage(self.manifest, self.target, self.output, plan["plan_sha256"])

    def test_native_skill_stages_without_editing_target(self):
        self.write_manifest()
        plan = self.audit()
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["modules"][0]["missing_optional"], ["reports"])
        self.assertEqual(plan["members"][0]["original"], plan["members"][0]["output"])
        receipt = self.stage(plan)
        staged = self.output / ".agents/skills/receipt-reader"
        self.assertEqual((staged / "SKILL.md").read_bytes(), self.entry.read_bytes())
        self.assertEqual((staged / "agents/openai.yaml").read_bytes(),
                         (self.skill / "agents/openai.yaml").read_bytes())
        self.assertEqual((staged / "parse.py").stat().st_mode & 0o777, 0o755)
        self.assertTrue((staged / "assets").is_dir())
        self.assertFalse(receipt["target_modified"])
        self.assertEqual(list(self.target.iterdir()), [])
        with self.assertRaisesRegex(ValueError, "fresh directory"):
            self.stage(plan)

    def test_team_user_body_only_precedence_is_exact(self):
        team = self.source / "team.md"
        personal = self.source / "personal.md"
        team.write_text("Team instruction.\n")
        personal.write_text("Personal instruction.\n")
        original = self.entry.read_bytes()
        intermediate = original.replace(b"Original prompt.\r\n", b"Team instruction.\n\nOriginal prompt.\r\n")
        # Reversed input order does not change the team's precedence.
        self.write_manifest(overlays=[
            self.overlay("personal", "append", personal.name, intermediate),
            self.overlay("team", "prepend", team.name, original),
        ])
        plan = self.audit()
        self.assertEqual([row["scope"] for row in plan["members"][0]["customizations"]], ["team", "personal"])
        self.stage(plan)
        staged = self.output / ".agents/skills/receipt-reader/SKILL.md"
        self.assertEqual(staged.read_bytes(), intermediate.rstrip() + b"\n\nPersonal instruction.\n")
        self.assertEqual(self.entry.read_bytes(), original)

    def test_rejects_stale_override_or_path_escape(self):
        team = self.source / "team.md"
        team.write_text("Team instruction.")
        self.write_manifest(overlays=[self.overlay("team", "replace", team.name, b"stale")])
        with self.assertRaisesRegex(ValueError, "Stale customization"):
            self.audit()
        self.module["members"][0]["source"] = "../project"
        self.write_manifest()
        with self.assertRaisesRegex(import_codex.files.InstallError, "Unsafe manifest file path"):
            self.audit()

    def test_approved_plan_cannot_follow_edited_source(self):
        self.write_manifest()
        plan = self.audit()
        self.entry.write_bytes(self.entry.read_bytes() + b"\nChanged.")
        with self.assertRaisesRegex(ValueError, "drifted"):
            self.stage(plan)
        self.assertFalse(self.output.exists())

    def test_stage_cleans_up_if_target_changes_after_copy(self):
        self.write_manifest()
        plan = self.audit()
        original_audit = import_codex.audit
        calls = 0

        def changes_after_first_audit(manifest, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.entry.write_bytes(self.entry.read_bytes() + b"\nNew author change.\n")
            return original_audit(manifest, target)

        with patch.object(import_codex, "audit", changes_after_first_audit):
            with self.assertRaisesRegex(ValueError, "while staging"):
                self.stage(plan)
        self.assertFalse(self.output.exists())
        self.assertFalse(any(self.root.glob(".codex-import-*")))
        self.assertFalse(any(self.root.glob(".*.import-lock")))

    def test_target_exact_match_is_clean_and_case_alias_collides(self):
        self.write_manifest()
        plan = self.audit()
        self.stage(plan)
        other = import_codex.audit(self.manifest, self.output)[0]
        self.assertTrue(other["ready"])
        self.assertTrue(other["members"][0]["target_entries"][0]["matches"])
        folder = self.output / ".agents/skills/receipt-reader"
        # Rename through another spelling on case-insensitive volume.
        temporary = folder.with_name("temporary")
        folder.rename(temporary)
        temporary.rename(folder.with_name("Receipt-reader"))
        collision = import_codex.audit(self.manifest, self.output)[0]
        self.assertFalse(collision["ready"])
        self.assertIn("aliases", collision["blockers"][0]["reason"])

    def test_nonmatching_installed_file_keeps_local_bytes(self):
        self.write_manifest()
        self.stage(self.audit())
        source = self.output
        self.output = self.root / "candidate"
        self.target = source
        local = source / ".agents/skills/receipt-reader/SKILL.md"
        local.write_bytes(local.read_bytes() + b"User instruction.\n")
        untouched = local.read_bytes()
        plan = self.audit()
        self.assertFalse(plan["ready"])
        with self.assertRaisesRegex(ValueError, "collision"):
            self.stage(plan)
        self.assertEqual(local.read_bytes(), untouched)
        self.assertFalse(self.output.exists())

    def test_no_implicit_dependency_or_cyclic_module_resolution(self):
        self.module["requires"] = ["missing"]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Missing required module"):
            self.audit()
        self.module["requires"] = ["second"]
        self.write_manifest([self.module, {
            "id": "second", "version": "1", "members": [self.module["members"][0]], "optional": ["ledger"]
        }])
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.audit()

    def test_audit_rejects_missing_local_reference_before_stage(self):
        with self.entry.open("ab") as stream:
            stream.write(b"Review [rules](references/rules.md).\n")
        self.write_manifest()
        with self.assertRaisesRegex(import_codex.files.InstallError, "Missing/unsafe local SKILL.md reference"):
            self.audit()
        self.assertFalse(self.output.exists())

    def test_rejects_link_before_staging(self):
        (self.skill / "outside").symlink_to(self.root / "unreviewed")
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Link or special"):
            self.audit()

    @unittest.skipIf(import_codex.tomllib is None, "role imports require Python 3.11")
    def test_mixed_module_role_customization_preserves_supported_fields(self):
        role_path = self.source / "local-role.toml"
        role = (
            '# Original user preferences.\nname = "receipt_checker"\n'
            'description = "Checks reviewed receipts"\nmodel = "gpt-6.1-sol"\n'
            'model_reasoning_effort = "low"\ndeveloper_instructions = """\n'
            'Original review instruction.\n"""\n\n'
            '[[skills.config]]\nname = "browser-launch"\nenabled = false\n'
        )
        role_path.write_text(role)
        (self.source / "personal-role.md").write_text("Personal review instruction.\n")
        self.write_manifest([
            {"id": "review", "version": "2", "requires": ["ledger"], "members": [{
                "kind": "role", "name": "receipt_checker", "source": role_path.name
            }]},
            self.module,
        ], overlays=[self.overlay("personal", "append", "personal-role.md", role.encode(),
                                  "role", "receipt_checker")])
        plan = self.audit()
        self.assertEqual([module["id"] for module in plan["modules"]], ["ledger", "review"])
        receipt = self.stage(plan)
        registry = self.output / ".codex/config.toml"
        self.assertEqual(import_codex.files.digest(registry.read_bytes()), plan["role_registry_sha256"])
        self.assertEqual(import_codex.tomllib.loads(registry.read_text())["agents"]["receipt_checker"]["config_file"],
                         "agents/receipt_checker.toml")
        result = self.output / ".codex/agents/receipt_checker.toml"
        self.assertEqual(receipt["role_launch_overrides"][-1],
                         'agents.receipt_checker.config_file="' + str(result) + '"')
        self.assertTrue(import_codex.audit(self.manifest, self.output)[0]["ready"])
        raw_result = result.read_text()
        original = import_codex.tomllib.loads(role)
        actual = import_codex.tomllib.loads(raw_result)
        self.assertEqual(actual.pop("developer_instructions"),
                         original.pop("developer_instructions").rstrip() + "\n\nPersonal review instruction.\n")
        self.assertEqual(original, actual)
        self.assertTrue(raw_result.startswith("# Original user preferences.\n"))

    @unittest.skipIf(import_codex.tomllib is None, "role imports require Python 3.11")
    def test_target_role_registry_collision_blocks_publish_without_overwrite(self):
        (self.source / "role.toml").write_text(
            'name = "receipt_checker"\ndescription = "Fixture"\n'
            'developer_instructions = "Check receipts."\n'
        )
        self.module["members"] = [{"kind": "role", "name": "receipt_checker", "source": "role.toml"}]
        self.write_manifest()
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = '[agents.receipt_checker]\ndescription = "Existing user role"\nconfig_file = "custom.toml"\n'
        config.write_text(original)
        plan = self.audit()
        self.assertFalse(plan["ready"])
        self.assertEqual(plan["blockers"][0]["reason"], "existing project role registration differs")
        with self.assertRaisesRegex(ValueError, "collision"):
            self.stage(plan)
        self.assertEqual(config.read_text(), original)
        self.assertFalse(self.output.exists())

    @unittest.skipIf(import_codex.tomllib is None, "role imports require Python 3.11")
    def test_unknown_native_role_runtime_authority_is_reported(self):
        (self.source / "role.toml").write_text(
            'name = "receipt_checker"\ndescription = "Fixture"\n'
            'developer_instructions = "Check receipts."\nsandbox_mode = "danger-full-access"\n'
        )
        self.module["members"] = [{"kind": "role", "name": "receipt_checker", "source": "role.toml"}]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "unsupported runtime fields: sandbox_mode"):
            self.audit()


if __name__ == "__main__":
    unittest.main()
