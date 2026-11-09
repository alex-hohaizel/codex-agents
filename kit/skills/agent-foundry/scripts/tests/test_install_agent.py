"""Actual subprocess tests using neutral fixtures; no host discovery or external effects."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import signal
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
import zipfile

SOURCE = Path(__file__).absolute().parents[1]


def module(path):
    result = types.ModuleType("test_installer_source")
    result.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), result.__dict__)
    return result


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.base = Path(self.tmp.name)
        self.tools = self.base / "constructor/scripts"
        self.tools.mkdir(parents=True)
        for name in ("install_agent.py", "package_agent.py", "check_generated_inheritance.py"):
            shutil.copy2(SOURCE / name, self.tools / name)
        inheritance = module(SOURCE / "check_generated_inheritance.py")
        self.operating_resources = inheritance.RESOURCES
        for name in self.operating_resources:
            source = SOURCE.parent / name
            target = self.tools.parent / name
            target.parent.mkdir(parents=True, exist_ok=True)
            # These fixtures test packaging/inheritance, not execution of the
            # subject-method scripts. Use real visual code for image checking.
            target.write_bytes(source.read_bytes() if source.exists() else ("neutral operating fixture: " + name + "\n").encode())
        (self.tools.parent / "SKILL.md").write_text("---\nname: agent-foundry\ndescription: Construct a scoped agent.\n---\n\n# Constructor\n")
        (self.tools / "foundry.py").write_text('import json,sys\nfrom pathlib import Path\nr=json.loads(Path(sys.argv[2]).read_text())\nif sys.argv[1]=="bundle-check":r={"valid":r.get("bundle_valid",r.get("ready")),"blockers":[]}\nprint(json.dumps(r));sys.exit(0 if r.get("ready",r.get("valid")) else 1)\n')
        self.kit = self.base / "Input Kit UA"
        self.kit.mkdir()
        self.project = self.base / "Existing Project UA"
        self.installer = self.tools / "install_agent.py"
        self.builder = self.tools / "package_agent.py"
        self.api = module(self.installer)
        self.session = self.base / "session.json"
        self.names = []

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, script, args, expected=0, timeout=8):
        proc = subprocess.run([sys.executable, "-B", str(script), *map(str, args)], capture_output=True, text=True, timeout=timeout)
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        return json.loads(proc.stdout or proc.stderr)

    def gate(self, ready=True, names=None, entry=None):
        names = names or self.names
        entry = entry or names[0]
        value = {"ready": ready, "blockers": [] if ready else ["approval pending"], "blueprint": {"id": "passport-a", "revision": 1, "sha256": "a" * 64, "entry_skill": entry, "skill_names": names}, "approval_ref": {"source": "test-user-message", "verbatim": "Approve this test fixture", "scope": "test-passport", "blueprint_sha256": "a" * 64, "blueprint_revision": 1, "recorded_at": "fixture"}}
        self.session.write_text(json.dumps(value))
        return value

    def skills(self, count=3, prefix="sample", kit=None):
        kit = kit or self.kit
        names = [prefix + "-entry"] + [prefix + "-part-" + str(n) for n in range(1, count)]
        for name in names:
            root = kit / "skills" / name
            (root / "references").mkdir(parents=True, exist_ok=True)
            (root / "references/rules.md").write_text("Concrete source and acceptance contract.\n")
            links = "".join("Read [operating method](" + path + ").\n" for path in self.operating_resources if path.startswith("references/"))
            (root / "SKILL.md").write_text("---\nname: " + name + "\ndescription: Use for the assigned bounded result.\n---\n\n# Assigned work\nRead [rules](references/rules.md).\n" + links)
            for path in self.operating_resources:
                target = root / path;target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((self.tools.parent / path).read_bytes())
            (root / "agents").mkdir(exist_ok=True)
            (root / "agents/openai.yaml").write_text("interface:\n  display_name: Assigned Agent\n  icon_small: assets/icon.svg\n  icon_large: assets/icon.svg\n")
            icon = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><metadata>agent-style:project-card-v1</metadata><polygon points="4,4 72,4 92,24 92,92 4,92" fill="#F8FAFC" stroke="#0F766E"/><text x="48" y="85">PROJECT</text><text>F</text></svg>\n'
            (root / "assets/icon.svg").write_bytes(icon)
            snapshot = {"schema":"visual-identity/1","class":"project","interface":{"icon_small":"assets/icon.svg","icon_large":"assets/icon.svg"},"files":{"assets/icon.svg":hashlib.sha256(icon).hexdigest()},"regenerate_on_update":False}
            (root / "assets/visual-identity.lock.json").write_text(json.dumps(snapshot))
            (root / "assets/visual-identity-origin.json").write_text(json.dumps({"schema":"visual-identity-origin/1","kind":"created"}))
            (root / "run.py").write_text("print('fixture')\n")
            os.chmod(root / "run.py", 0o755)
        self.names = names
        self.gate()
        return names

    def build(self, kit=None, entry=None, agent_id=None, extra=(), expected=0):
        entry = entry or self.names[0]
        return self.call(self.builder, ["--kit", kit or self.kit, "--agent-id", agent_id or entry, "--entry-skill", entry, "--version", "1.0.0", "--purpose", "generated", "--session", self.session, *extra], expected)

    def install(self, mode="apply", kit=None, project=None, extra=(), expected=0, timeout=8):
        return self.call(self.installer, ["--kit", kit or self.kit, "--project", project or self.project, "--mode", mode, *extra], expected, timeout)

    def refresh_visual_lock(self, root, origin="created", kind="project"):
        visual = module(self.tools.parent / "scripts/visual_identity.py")
        snapshot = visual.freeze(root, kind)
        (root / "assets/visual-identity.lock.json").write_text(json.dumps(snapshot))
        provenance = {"schema":"visual-identity-origin/1", "kind":origin}
        if origin == "preserved":
            prior = root / "assets/visual-identity-prior.json"
            prior.write_text(json.dumps(snapshot))
            provenance["prior_snapshot"] = {"path":"assets/visual-identity-prior.json", "sha256":hashlib.sha256(prior.read_bytes()).hexdigest()}
        (root / "assets/visual-identity-origin.json").write_text(json.dumps(provenance))

    def reusable_system_skill(self, preserved=False, project_card=False):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        if not project_card:
            (root / "assets/icon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="#111827" stroke="#D4AF37"/><text x="48">SYS</text></svg>')
        self.refresh_visual_lock(root, "preserved" if preserved else "created", "system")
        path = root / "assets/visual-identity-origin.json"
        origin = json.loads(path.read_text())
        origin.update(scope="reusable_system", scope_basis={"source":"Synthetic accepted task: build a reusable global helper", "reason":"Product-independent method may be used by multiple unrelated projects; placement grants no authority"})
        if not preserved:
            sample = root / "assets/system-style-reference.svg"
            sample.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="22" fill="#111827" stroke="#D4AF37"/><text x="48">AG</text></svg>')
            origin["style_reference"] = {"path":"assets/system-style-reference.svg", "sha256":hashlib.sha256(sample.read_bytes()).hexdigest()}
        path.write_text(json.dumps(origin))
        return root

    def test_generated_export_requires_all_portable_methods_and_local_links(self):
        self.skills(1)
        root = self.kit / "skills" / self.names[0]
        source = root / "references/research-and-synthesis.md"
        old = source.read_bytes();source.unlink()
        self.assertIn("inheritance blocks export", self.build(expected=2)["error"])
        self.assertFalse((self.kit / "manifest.json").exists())
        source.write_bytes(old)
        entry = root / "SKILL.md"
        entry.write_text(entry.read_text().replace("[operating method](references/adaptive-work.md)", "adaptive work"))
        self.assertIn("local operating-resource link", self.build(expected=2)["error"])

    def test_generated_export_rejects_different_method_bytes(self):
        self.skills(1)
        (self.kit / "skills" / self.names[0] / "scripts/adaptive_work.py").write_text("print('different method')\n")
        self.assertIn("differs from", self.build(expected=2)["error"])

    def test_new_project_style_must_be_actual_distinct_geometry(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        (root / "assets/icon.svg").write_text('<svg><metadata>agent-style:project-card-v1</metadata><text>copied system mark</text></svg>')
        self.refresh_visual_lock(root)
        self.assertIn("project-card-v1", self.build(expected=2)["error"])

    def test_project_class_and_bound_preservation_are_required(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        path = root / "assets/visual-identity.lock.json"
        lock = json.loads(path.read_text());lock["class"] = "system";path.write_text(json.dumps(lock))
        self.assertIn("reusable_system", self.build(expected=2)["error"])
        (root / "assets/icon.svg").write_text('<svg><text>existing accepted project identity</text></svg>')
        self.refresh_visual_lock(root, "preserved")
        self.build();self.install();self.install("verify")
        (root / "assets/visual-identity-prior.json").write_text('{}')
        self.assertIn("bound prior snapshot", self.build(expected=2)["error"])

    def test_legacy_manifest_is_readable_without_upgraded_inheritance_claim(self):
        self.skills(1);self.build()
        path = self.kit / "manifest.json";manifest = json.loads(path.read_text());manifest.pop("operating_standard");path.write_text(json.dumps(manifest))
        result = self.install();self.assertEqual(result["operating_standard"], "legacy_not_declared")
        self.assertTrue(any("Legacy package" in x for x in result["warnings"]))
        self.install("verify")

    def test_project_update_keeps_icons_and_colors_but_updates_other_metadata(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        ui = root / "agents/openai.yaml";ui.write_text(ui.read_text() + '  brand_color: "#112233"\n')
        self.refresh_visual_lock(root);self.build();self.install()
        target = self.project / ".agents/skills" / self.names[0]
        before = (target / "assets/icon.svg").read_bytes()
        (root / "assets/icon.svg").write_bytes(before.replace(b'<text>F</text>', b'<text>NEW</text>'))
        ui.write_text(ui.read_text().replace("Assigned Agent", "Assigned Agent 5.0.0").replace("#112233", "#AABBCC"))
        self.refresh_visual_lock(root);self.build()
        result = self.install();self.assertEqual(result["preserved_visuals"], self.names)
        self.assertEqual((target / "assets/icon.svg").read_bytes(), before)
        actual = (target / "agents/openai.yaml").read_text()
        self.assertIn("Assigned Agent 5.0.0", actual);self.assertIn("#112233", actual);self.assertNotIn("#AABBCC", actual)
        self.assertNotEqual(result["manifest_sha256"], result["source_manifest_sha256"])
        self.install("verify");self.assertTrue(self.install()["idempotent"])
        self.api.validate_project_identity(target)

    def test_changed_incoming_icon_path_does_not_create_an_icon_for_existing_skill(self):
        self.skills(1);self.build();self.install()
        root = self.kit / "skills" / self.names[0]
        (root / "assets/icon.svg").rename(root / "assets/renamed.svg")
        ui = root / "agents/openai.yaml";ui.write_text(ui.read_text().replace("assets/icon.svg", "assets/renamed.svg"))
        self.refresh_visual_lock(root);self.build();self.install();self.install("verify")
        target = self.project / ".agents/skills" / self.names[0]
        self.assertTrue((target / "assets/icon.svg").exists());self.assertFalse((target / "assets/renamed.svg").exists())
        self.assertIn("assets/icon.svg", (target / "agents/openai.yaml").read_text())

    def test_recorded_visual_only_changes_survive_update_and_verify(self):
        self.skills(1);self.build();self.install()
        root = self.kit / "skills" / self.names[0]
        target = self.project / ".agents/skills" / self.names[0]
        changed = b'<svg><text>the existing local project icon</text></svg>'
        (target / "assets/icon.svg").write_bytes(changed)
        (root / "run.py").write_text("print('new implementation')\n");self.build()
        self.install();self.install("verify")
        self.assertEqual((target / "assets/icon.svg").read_bytes(), changed)
        self.assertIn("new implementation", (target / "run.py").read_text())
        self.api.validate_project_identity(target)

    def test_code_drift_is_not_admitted_as_visual_customization(self):
        self.skills(1);self.build();self.install()
        target = self.project / ".agents/skills" / self.names[0]
        (target / "assets/icon.svg").write_text('<svg>local icon</svg>')
        (target / "run.py").write_text("unreviewed implementation\n")
        result = self.install(expected=2)
        self.assertIn("semantic/code drift", result["error"])
        self.assertEqual((target / "run.py").read_text(), "unreviewed implementation\n")

    def test_legacy_ui_drift_without_baseline_blocks_without_changing_icons(self):
        self.skills(1);self.build();self.install()
        state = self.project / ".agents/agent-installs" / (self.names[0] + ".json")
        old = json.loads(state.read_text());old.pop("visuals");state.write_text(json.dumps(old))
        target = self.project / ".agents/skills" / self.names[0]
        ui = target / "agents/openai.yaml";ui.write_text(ui.read_text() + '  brand_color: "#112233"\n')
        icon = (target / "assets/icon.svg").read_bytes()
        result = self.install(expected=2)
        self.assertIn("legacy UI edit", result["error"])
        self.assertEqual((target / "assets/icon.svg").read_bytes(), icon)

    def test_icon_overlay_failure_rolls_back_to_actual_visual_state(self):
        self.skills(1);self.build();self.install()
        root = self.kit / "skills" / self.names[0]
        target = self.project / ".agents/skills" / self.names[0]
        changed = b'<svg><text>local icon before interrupted update</text></svg>'
        (target / "assets/icon.svg").write_bytes(changed)
        (root / "run.py").write_text("print('updated')\n");self.build()
        real_replace = self.api.os.replace;fired = []
        def failed(source, destination):
            if "/prepared/.agents/skills/" in str(source) and not fired:
                fired.append(True);raise OSError("injected overlay promotion failure")
            return real_replace(source, destination)
        with mock.patch.object(self.api.os, "replace", side_effect=failed):
            with self.assertRaises(OSError):self.api.apply_install(self.kit, self.project)
        self.assertEqual((target / "assets/icon.svg").read_bytes(), changed)
        self.assertIn("fixture", (target / "run.py").read_text())
        self.install();self.install("verify")

    def test_json_ui_visuals_are_preserved_with_updated_nonvisual_metadata(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        ui = root / "agents/openai.yaml"
        metadata = {"interface":{"display_name":"Existing", "icon_small":"assets/icon.svg", "icon_large":"assets/icon.svg", "brand_color":"#112233"}, "policy":{"allow_implicit_invocation":False}}
        ui.write_text(json.dumps(metadata));self.refresh_visual_lock(root);self.build();self.install()
        metadata["interface"]["display_name"] = "Updated 5.0.0";metadata["interface"]["brand_color"] = "#AABBCC"
        ui.write_text(json.dumps(metadata));self.refresh_visual_lock(root);self.build();self.install();self.install("verify")
        actual = json.loads((self.project / ".agents/skills" / self.names[0] / "agents/openai.yaml").read_text())
        self.assertEqual(actual["interface"]["brand_color"], "#112233")
        self.assertEqual(actual["interface"]["display_name"], "Updated 5.0.0")
        self.assertIs(actual["policy"]["allow_implicit_invocation"], False)

    def test_nested_and_merged_visual_yaml_are_conflicts(self):
        for raw in (b'interface:\n    icon_small: assets/icon.svg\n', b'interface:\n  <<: *other\n'):
            with self.subTest(raw=raw):
                with self.assertRaises(self.api.InstallError):self.api.visual_ui(raw)

    def test_existing_dot_slash_icon_bindings_remain_exact(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        ui = root / "agents/openai.yaml";ui.write_text(ui.read_text().replace("assets/icon.svg", "./assets/icon.svg"))
        self.refresh_visual_lock(root);self.build();self.install()
        ui.write_text(ui.read_text().replace("./assets/icon.svg", "assets/icon.svg").replace("Assigned Agent", "Updated"))
        self.refresh_visual_lock(root);self.build();self.install();self.install("verify")
        actual = (self.project / ".agents/skills" / self.names[0] / "agents/openai.yaml").read_text()
        self.assertIn('"./assets/icon.svg"', actual)
        self.assertIn("Updated", actual)

    def test_created_reusable_system_skill_keeps_system_class_inside_project(self):
        root = self.reusable_system_skill();self.build();self.install();self.install("verify")
        target = self.project / ".agents/skills" / self.names[0]
        before = (target / "assets/icon.svg").read_bytes()
        self.assertEqual(json.loads((target / "assets/visual-identity.lock.json").read_text())["class"], "system")
        (root / "assets/icon.svg").write_bytes(before.replace(b"SYS", b"NEW"))
        ui = root / "agents/openai.yaml";ui.write_text(ui.read_text().replace("Assigned Agent", "Updated reusable system tool"))
        self.refresh_visual_lock(root, kind="system")
        origin = {"schema":"visual-identity-origin/1", "kind":"created", "scope":"reusable_system", "scope_basis":{"source":"Synthetic accepted reusable-system task", "reason":"A general capability, independent of any product"}, "style_reference":{"path":"assets/system-style-reference.svg", "sha256":hashlib.sha256((root / "assets/system-style-reference.svg").read_bytes()).hexdigest()}}
        (root / "assets/visual-identity-origin.json").write_text(json.dumps(origin))
        self.build();self.install();self.install("verify")
        self.assertEqual((target / "assets/icon.svg").read_bytes(), before)
        self.assertEqual(json.loads((target / "assets/visual-identity.lock.json").read_text())["class"], "system")
        self.assertTrue((target / "assets/system-style-reference.svg").exists())
        self.api.validate_project_identity(target)

    def test_system_class_without_explicit_source_basis_is_blocked(self):
        root = self.reusable_system_skill();self.build()
        manifest = json.loads((self.kit / "manifest.json").read_text())
        path = root / "assets/visual-identity-origin.json"
        origin = json.loads(path.read_text());origin.pop("scope_basis");path.write_text(json.dumps(origin))
        self.assertIn("scope_basis", self.build(expected=2)["error"])
        self.api.write_manifest(self.kit, {key:value for key,value in manifest.items() if key != "skills"})
        self.assertIn("scope_basis", self.install(expected=2)["error"])

    def test_project_card_cannot_be_relabelled_as_created_system_icon(self):
        self.reusable_system_skill(project_card=True)
        self.assertIn("Project-card", self.build(expected=2)["error"])

    def test_preserved_system_identity_keeps_class_on_visual_drift(self):
        root = self.reusable_system_skill(preserved=True);self.build();self.install()
        target = self.project / ".agents/skills" / self.names[0]
        changed = b'<svg><text>existing reusable system icon, preserved</text></svg>'
        (target / "assets/icon.svg").write_bytes(changed)
        (root / "run.py").write_text("print('updated reusable implementation')\n");self.build();self.install();self.install("verify")
        lock = json.loads((target / "assets/visual-identity.lock.json").read_text())
        self.assertEqual(lock["class"], "system")
        self.assertEqual((target / "assets/icon.svg").read_bytes(), changed)
        self.assertEqual(json.loads((target / "assets/visual-identity-origin.json").read_text())["scope"], "reusable_system")
        self.api.validate_project_identity(target)

    def test_preserved_project_snapshot_cannot_be_relabelled_system(self):
        self.skills(1);root = self.kit / "skills" / self.names[0]
        self.refresh_visual_lock(root, "preserved")
        lock_path = root / "assets/visual-identity.lock.json"
        lock = json.loads(lock_path.read_text());lock["class"] = "system";lock_path.write_text(json.dumps(lock))
        path = root / "assets/visual-identity-origin.json";origin = json.loads(path.read_text())
        origin.update(scope="reusable_system", scope_basis={"source":"Synthetic classification claim", "reason":"A new label does not change the bound original project class"})
        path.write_text(json.dumps(origin))
        self.assertIn("bound prior snapshot", self.build(expected=2)["error"])

    def test_project_installer_does_not_silently_switch_existing_class(self):
        self.skills(1);self.build();self.install()
        target = self.project / ".agents/skills" / self.names[0]
        before = (target / "assets/icon.svg").read_bytes()
        self.reusable_system_skill();self.build()
        self.assertIn("explicit actual scope migration", self.install(expected=2)["error"])
        self.assertEqual(json.loads((target / "assets/visual-identity.lock.json").read_text())["class"], "project")
        self.assertEqual((target / "assets/icon.svg").read_bytes(), before)

    def test_variable_skill_counts_real_install_and_idempotence(self):
        for count in (1, 3, 7):
            with self.subTest(count=count):
                kit = self.base / ("kit-" + str(count));kit.mkdir()
                names = self.skills(count, prefix="agent" + str(count), kit=kit)
                self.build(kit=kit)
                project = self.base / ("project-" + str(count))
                self.install("preflight", kit, project);self.install("dry-run", kit, project)
                self.assertFalse(project.exists())
                first = self.install("apply", kit, project)
                self.assertEqual(first["skills"], count)
                self.install("verify", kit, project)
                snapshot = {p.relative_to(project).as_posix(): p.stat().st_mtime_ns for p in project.rglob("*") if p.is_file()}
                again = self.install("apply", kit, project)
                self.assertTrue(again["idempotent"])
                self.assertEqual(snapshot, {p.relative_to(project).as_posix(): p.stat().st_mtime_ns for p in project.rglob("*") if p.is_file()})
                self.assertEqual(len(list((project / ".agents/skills").iterdir())), len(names))

    def test_existing_bytes_modes_and_foreign_state_preserved(self):
        self.skills();self.build();self.project.mkdir()
        originals = {"AGENTS.md": "Owner's instructions.\r\n", ".git/sentinel": "commit bytes", "source/core.txt": "source bytes", "state/current.json": '{"revision":9}', ".agents/skills/unrelated/SKILL.md": "unrelated"}
        for name, text in originals.items():
            p = self.project / name;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(text.encode())
        os.chmod(self.project / "AGENTS.md", 0o600)
        self.install();self.install("verify")
        for name, text in originals.items():
            actual = (self.project / name).read_bytes()
            self.assertTrue(actual.startswith(text.encode())) if name == "AGENTS.md" else self.assertEqual(actual, text.encode())
        self.assertEqual(stat.S_IMODE((self.project / "AGENTS.md").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((self.project / ".agents/skills" / self.names[0] / "run.py").stat().st_mode), 0o755)

    def test_disjoint_agents_coexist_and_cross_owner_collision_is_blocked(self):
        self.skills(1, "alpha");self.build();self.install()
        old_agents = (self.project / "AGENTS.md").read_bytes()
        second = self.base / "second";second.mkdir();self.skills(1, "beta", second);self.build(second);self.install(kit=second)
        self.assertTrue((self.project / "AGENTS.md").read_bytes().startswith(old_agents))
        third = self.base / "third";shutil.copytree(self.kit, third)
        value = json.loads((third / "manifest.json").read_text());value["agent_id"] = "third-owner";(third / "manifest.json").write_text(json.dumps(value))
        result = self.install(kit=third, expected=2)
        self.assertIn("another installed agent", result["error"])

    def test_unmanaged_even_identical_skill_is_not_adopted(self):
        self.skills(1);self.build()
        target = self.project / ".agents/skills" / self.names[0]
        target.parent.mkdir(parents=True);shutil.copytree(self.kit / "skills" / self.names[0], target)
        self.install(expected=2)
        self.assertFalse((self.project / ".agents/agent-installs").exists())

    def test_dirty_owned_files_modes_and_managed_block_refuse_update(self):
        self.skills(1);self.build();self.install()
        path = self.project / ".agents/skills" / self.names[0] / "run.py"
        path.write_text("local edit\n");self.install(expected=2)
        shutil.copy2(self.kit / "skills" / self.names[0] / "run.py", path)
        os.chmod(path, 0o644);self.install("verify", expected=2)
        os.chmod(path, 0o755)
        p = self.project / "AGENTS.md";p.write_text(p.read_text().replace("single entry point", "edited instructions"));self.install(expected=2)

    def test_owned_skill_addition_and_reviewed_removal(self):
        self.skills(1);self.build();self.install()
        self.skills(3);self.build();self.install();self.install("verify")
        for name in self.names[1:]:shutil.rmtree(self.kit / "skills" / name)
        self.names = self.names[:1];self.gate();self.build()
        self.install(expected=2)
        self.install(extra=["--allow-remove-owned"]);self.install("verify")
        self.assertEqual([p.name for p in (self.project / ".agents/skills").iterdir()], self.names)

    def test_symlinks_special_paths_and_nested_targets_rejected(self):
        self.skills(1);self.build()
        link = self.base / "kit-link";link.symlink_to(self.kit, target_is_directory=True)
        self.install(kit=link, expected=2)
        self.install(project=self.kit / "nested", expected=2)
        (self.kit / "skills" / self.names[0] / "link").symlink_to(self.base)
        self.install(expected=2)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO")
    def test_fifo_reads_do_not_hang(self):
        self.skills(1);self.build();self.project.mkdir()
        fifo = self.project / "AGENTS.md";os.mkfifo(fifo)
        self.install(expected=2, timeout=2)
        fifo.unlink();self.install()
        state = self.project / ".agents/agent-installs" / (self.names[0] + ".json")
        state.unlink();os.mkfifo(state);self.install(expected=2, timeout=2)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO")
    def test_fifo_replacement_race_is_nonblocking(self):
        path = self.base / "regular";path.write_text("bytes")
        real_open = self.api.os.open
        fired = []
        def raced(p, flags, *args):
            if Path(p) == path and not fired:
                fired.append(True);path.unlink();os.mkfifo(path)
            return real_open(p, flags, *args)
        with mock.patch.object(self.api.os, "open", raced):
            with self.assertRaises(self.api.InstallError):self.api.read_bytes(path)

    def test_bad_metadata_missing_links_and_hash_modes_rejected(self):
        self.skills(1)
        path = self.kit / "skills" / self.names[0] / "SKILL.md";original = path.read_text()
        for value in ("", original.replace("name: " + self.names[0], "name: other"), original.replace("Use for the assigned bounded result.", "[]"), original.replace("Use for the assigned bounded result.", '"unterminated'), original.replace("references/rules.md", "missing.md")):
            path.write_text(value);self.build(expected=2);self.assertFalse((self.kit / "manifest.json").exists())
        path.write_text(original);self.build()
        script = self.kit / "skills" / self.names[0] / "run.py";os.chmod(script, 0o644);self.install(expected=2)

    def test_metadata_ambiguous_scalars_require_quotes(self):
        self.skills(1)
        path = self.kit / "skills" / self.names[0] / "SKILL.md";original = path.read_text()
        for text in ("0", "false # comment", "Null", "2026-11-01", "yes", "OFF", ".nan", "0x10", "# only comment", "- item", "> invalid-header"):
            with self.subTest(text=text):
                path.write_text(original.replace("Use for the assigned bounded result.", text));self.build(expected=2)
                path.write_text(original.replace("Use for the assigned bounded result.", "'" + text + "'"));self.build()

    def test_empty_directory_entry_reference_is_not_claimed_delivered(self):
        self.skills(1);self.build()
        root = self.kit / "skills" / self.names[0];(root / "references/empty").mkdir()
        p = root / "SKILL.md";p.write_text(p.read_text().replace("references/rules.md", "references/empty"))
        self.build(expected=2)
        manifest_path = self.kit / "manifest.json";value = json.loads(manifest_path.read_text())
        value["skills"][0]["files"]["SKILL.md"] = hashlib.sha256(p.read_bytes()).hexdigest();manifest_path.write_text(json.dumps(value))
        self.install(expected=2);self.assertFalse(self.project.exists())

    def test_archive_writes_captured_bytes_without_reopening_source(self):
        package = module(self.builder)
        root = self.base / "payload";root.mkdir();p = root / "data.bin";p.write_bytes(b"approved bytes")
        output = self.base / "snapshot.zip";real_read = self.api.read_bytes;reads = []
        def change_after_capture(path):
            result = real_read(path)
            if Path(path) == p:
                reads.append(True)
                if len(reads) == 2:p.write_bytes(b"later changed bytes")
            return result
        with mock.patch.object(self.api, "read_bytes", change_after_capture), mock.patch.object(package.zipfile.ZipFile, "write", side_effect=AssertionError("must not reopen source")):
            package.write_archive(root, output, self.api)
        self.assertEqual(p.read_bytes(), b"later changed bytes")
        with zipfile.ZipFile(output) as z:self.assertEqual(z.read("payload/data.bin"), b"approved bytes")

    def test_archive_rejects_cross_platform_unsafe_names_and_collisions(self):
        package = module(self.builder)
        bad_root = self.base / "..\\outside";bad_root.mkdir();(bad_root / "data.txt").write_text("bytes")
        with self.assertRaises(ValueError):package.write_archive(bad_root, self.base / "bad-root.zip", self.api)
        for n, name in enumerate(("C:drive", "NUL.txt", "trailing.", "line\nname")):
            root = self.base / ("invalid" + str(n));root.mkdir();(root / name).write_text("bytes")
            with self.subTest(name=name), self.assertRaises(ValueError):package.write_archive(root, self.base / ("bad" + str(n) + ".zip"), self.api)
        root = self.base / "case-conflict";(root / "A").mkdir(parents=True);(root / "A/one").write_text("one")
        if (root / "a").exists():
            # APFS cannot hold both entries. Exercise the real portable-prefix
            # admission guard with the equivalent inventory, before the second
            # conflicting path can be opened. Other files retain real bytes.
            inventory={'A/one':self.api.digest(b'one'),'a/two':self.api.digest(b'two')}
            with mock.patch.object(self.api,'file_map',return_value=inventory),self.assertRaisesRegex(ValueError,'Case/normalization'):
                package.write_archive(root, self.base / 'collision.zip', self.api)
        else:
            (root / "a").mkdir();(root / "a/two").write_text("two")
            with self.assertRaises(ValueError):package.write_archive(root, self.base / "collision.zip", self.api)

    def test_manifest_paths_names_emptyset_and_unknown_extra_skill(self):
        self.skills(1);self.build();path = self.kit / "manifest.json";original = json.loads(path.read_text())
        for change in ({"agent_id": "../outside"}, {"skills": []}, {"entry_skill": "missing"}, {"version": "1.0.0-01"}):
            value = dict(original, **change);path.write_text(json.dumps(value));self.install(expected=2)
        path.write_text(json.dumps(original));(self.kit / "skills/undeclared").mkdir();self.install(expected=2)

    def test_historical_operating_standard_keeps_its_exact_eight_resource_contract(self):
        self.skills(1);self.build()
        manifest=json.loads((self.kit/'manifest.json').read_text())
        standard=manifest['operating_standard'];standard['release']='5.0.0'
        standard['resources']={key:value for key,value in standard['resources'].items() if key in self.api.LEGACY_OPERATING_RESOURCES}
        self.assertTrue(self.api.validate_manifest(manifest))
        standard['release']='6.0.0'
        with self.assertRaisesRegex(self.api.InstallError,'every portable resource'):
            self.api.validate_manifest(manifest)

    def test_gate_pending_changed_skillset_and_identity_cannot_export(self):
        self.skills(3);self.gate(False)
        self.build(expected=2);self.assertFalse((self.kit / "manifest.json").exists())
        self.gate(True, [self.names[0]])
        self.build(expected=2)
        self.gate();self.build(agent_id="unapproved-id", expected=2)
        value = self.gate();value["bundle_valid"] = False;self.session.write_text(json.dumps(value))
        output = self.base / "no-evidence.zip"
        self.build(extra=["--kit-output", output], expected=2);self.assertFalse(output.exists())

    def test_factory_purpose_cannot_bypass_target_gate(self):
        self.skills(1)
        args = ["--kit", self.kit, "--agent-id", "agent-foundry", "--entry-skill", self.names[0], "--version", "1.0.0", "--purpose", "factory"]
        self.call(self.builder, args, 2)
        shutil.rmtree(self.kit / "skills")
        shutil.copytree(self.tools.parent, self.kit / "skills/agent-foundry")
        args[args.index(self.names[0])] = "agent-foundry"
        self.call(self.builder, args)
        (self.kit / "skills/agent-foundry/SKILL.md").write_text("---\nname: agent-foundry\ndescription: Altered scope.\n---\n# Different\n")
        self.call(self.builder, args, 2)

    def test_exports_private_plugin_structure_and_omit_only_host_policy(self):
        self.skills(3)
        for name in self.names:
            p = self.kit / "skills" / name / "agents/openai.yaml";p.parent.mkdir(exist_ok=True)
            p.write_text("interface:\n  display_name: Assigned Agent\n  short_description: Assigned bounded work\n  icon_small: assets/icon.svg\n  icon_large: assets/icon.svg\npolicy:\n  products:\n    - chatgpt\n    - codex\n  allow_implicit_invocation: false\n")
        plugin = self.base / "private.zip";kit_zip = self.base / "delivery.zip"
        result = self.build(extra=["--plugin-output", plugin, "--kit-output", kit_zip, "--display-name", "Scoped Agent", "--subtitle", "Assigned result"])
        self.assertEqual(len(result["normalized_host_ui"]), 3)
        self.assertEqual(result["exports"][0]["account_registration"], "not_performed")
        with zipfile.ZipFile(plugin) as z:
            self.assertIsNone(z.testzip())
            m = json.loads(z.read(self.names[0] + "/plugin.json"));self.assertEqual(m["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
            self.assertEqual(len([p for p in z.namelist() if p.endswith("/SKILL.md")]), 3)
            ui = z.read(self.names[0] + "/skills/" + self.names[0] + "/agents/openai.yaml").decode()
            self.assertNotIn("products:", ui);self.assertIn("allow_implicit_invocation: false", ui)
        self.assertFalse(list(self.tools.parent.rglob("*.pyc")))

    def test_host_indentless_product_sequence_preserves_sibling_policy_and_interface(self):
        package = module(self.builder)
        prefix = "interface:\n  display_name: Assigned Agent\n  short_description: Assigned bounded work\n  default_prompt: 'Use the current entry.'\n"
        suffix = "dependencies:\n  tools: []\n"
        products = "  products:\n  - chatgpt\n  - codex\n  - api\n  - atlas\n"
        for n, policy in enumerate(("  allow_implicit_invocation: true\n" + products, products + "  allow_implicit_invocation: false\n")):
            with self.subTest(order=n):
                path = self.base / ("host-ui-" + str(n) + ".yaml")
                path.write_text(prefix + "policy:\n" + policy + suffix)
                self.assertTrue(package.normalize_ui(path, self.api))
                expected = prefix + "policy:\n  allow_implicit_invocation: " + ("true" if n == 0 else "false") + "\n" + suffix
                self.assertEqual(path.read_text(), expected)
        portable = self.base / "portable-ui.yaml"
        original = prefix + "policy:\n  products:\n  - CHAT\n  - CODEX\n  allow_implicit_invocation: false\n" + suffix
        portable.write_text(original)
        self.assertFalse(package.normalize_ui(portable, self.api))
        self.assertEqual(portable.read_text(), original)
        unknown = self.base / "unknown-ui.yaml"
        original = prefix + "policy:\n  allow_implicit_invocation: true\n  products:\n  - chatgpt\n  - unsupported\n" + suffix
        unknown.write_text(original)
        with self.assertRaises(ValueError):package.normalize_ui(unknown, self.api)
        self.assertEqual(unknown.read_text(), original)

    def test_cache_and_private_files_are_not_silently_exported(self):
        self.skills(1)
        cache = self.kit / "skills" / self.names[0] / "__pycache__";cache.mkdir();(cache / "test.pyc").write_bytes(b"cache")
        self.build(expected=2);shutil.rmtree(cache)
        (self.kit / ".env").write_text("test fixture, not a secret")
        output = self.base / "out.zip"
        self.build(extra=["--kit-output", output], expected=2);self.assertFalse(output.exists())

    def test_atomic_rollback_restores_originals_and_modes(self):
        self.skills(3);self.build();self.install()
        before = {p.relative_to(self.project).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode)) for p in self.project.rglob("*") if p.is_file() and "agent-install-backups" not in p.parts}
        (self.kit / "skills" / self.names[0] / "run.py").write_text("print('new fixture')\n");self.build()
        real_replace = self.api.os.replace;fired = []
        def failed(source, target):
            if "/prepared/.agents/skills/" in str(source) and not fired:
                fired.append(True);raise OSError("injected promotion failure")
            return real_replace(source, target)
        with mock.patch.object(self.api.os, "replace", failed):
            with self.assertRaises(OSError):self.api.apply_install(self.kit, self.project)
        self.assertTrue(fired)
        for name, value in before.items():self.assertEqual(((self.project / name).read_bytes(), stat.S_IMODE((self.project / name).stat().st_mode)), value)

    def interrupted_update(self):
        self.skills(3);self.build();self.install()
        before = {p.relative_to(self.project).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode)) for p in self.project.rglob("*") if p.is_file() and "agent-install-backups" not in p.parts}
        (self.kit / "skills" / self.names[0] / "run.py").write_text("print('next fixture')\n");self.build()
        driver = r'''import os,signal,sys,types
from pathlib import Path
p=Path(sys.argv[1]);m=types.ModuleType("installer");m.__file__=str(p)
exec(compile(p.read_bytes(),str(p),"exec"),m.__dict__)
original=m.os.replace
def interrupted(source,target):
    result=original(source,target)
    if "/prepared/.agents/skills/" in str(source):os.kill(os.getpid(),signal.SIGKILL)
    return result
m.os.replace=interrupted
m.apply_install(Path(sys.argv[2]),Path(sys.argv[3]))
'''
        proc = subprocess.run([sys.executable, "-B", "-c", driver, str(self.installer), str(self.kit), str(self.project)], capture_output=True, text=True, timeout=8)
        self.assertEqual(proc.returncode, -signal.SIGKILL)
        journals = [p for p in (self.project / self.api.BACKUPS).glob("*/transaction.json") if json.loads(p.read_text())["status"] == "prepared"]
        self.assertEqual(len(journals), 1)
        self.install("preflight", expected=2)
        # The child is reaped and cannot still own this known stale lock.
        (self.project / self.api.LOCK).unlink()
        return before, journals[0]

    @unittest.skipUnless(hasattr(signal, "SIGKILL"), "POSIX termination")
    def test_real_interruption_and_explicit_recovery(self):
        before, journal = self.interrupted_update()
        self.install("recover", extra=["--transaction", journal.parent.name])
        for name, value in before.items():self.assertEqual(((self.project / name).read_bytes(), stat.S_IMODE((self.project / name).stat().st_mode)), value)
        self.assertEqual(json.loads(journal.read_text())["status"], "rolled_back")
        self.install();self.install("verify")

    @unittest.skipUnless(hasattr(signal, "SIGKILL"), "POSIX termination")
    def test_recovery_refuses_later_edits_and_unsafe_operations(self):
        before, journal = self.interrupted_update()
        changed = self.project / ".agents/skills" / self.names[0] / "run.py";changed.write_text("later owner edit\n")
        self.install("recover", extra=["--transaction", journal.parent.name], expected=2)
        self.assertEqual(changed.read_text(), "later owner edit\n")
        saved = json.loads(journal.read_text());saved["operations"][0]["path"] = ".git/sentinel";journal.write_text(json.dumps(saved))
        self.install("recover", extra=["--transaction", journal.parent.name], expected=2)

    def test_corrupt_state_ambiguous_markers_and_foreign_lock_block(self):
        self.skills(1);self.build();self.install()
        state = self.project / ".agents/agent-installs" / (self.names[0] + ".json");original = state.read_bytes();state.write_text("[]")
        self.install(expected=2);state.write_bytes(original)
        p = self.project / "AGENTS.md";original = p.read_bytes();p.write_text(p.read_text() + self.api.markers(self.names[0])[0]);self.install(expected=2);p.write_bytes(original)
        (self.kit / "skills" / self.names[0] / "run.py").write_text("new fixture\n");self.build()
        lock = self.project / self.api.LOCK;lock.write_text("live-owner-fixture")
        self.install(expected=2);self.assertEqual(lock.read_text(), "live-owner-fixture")


if __name__ == "__main__":
    unittest.main()
