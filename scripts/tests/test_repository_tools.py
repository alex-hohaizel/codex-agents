"""Failure-injection and reproducible-build checks using synthetic source material."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_packages import build, collect
from check_repository import check


def sha(data):
    return hashlib.sha256(data).hexdigest()


class RepositoryToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.write("kit/skills/example/SKILL.md", "---\nname: example\ndescription: A synthetic task\n---\nDo the task.\n")
        self.write("kit/skills/example/agents/openai.yaml", "interface:\n  display_name: Example\n")
        files = {}
        for p in (self.root / "kit/skills/example").rglob("*"):
            if p.is_file():
                files[p.relative_to(self.root / "kit/skills/example").as_posix()] = {"sha256": sha(p.read_bytes()), "size": p.stat().st_size, "mode": 420}
        self.json("kit/manifest.json", {"suite_id": "agent-system-5.0.0", "skills": [{"name": "example", "version": "5.0.0", "files": files}]})
        self.json("releases/current.json", {"repository_version": "1.0.0", "suite_version": "5.0.0", "stable_skill_names": ["example"], "release_notes": "releases/5.0.0.md", "migration": "releases/migrations/5.0.0.md", "requirements": "governance/requirements.csv"})
        self.write("releases/5.0.0.md", "# Synthetic release\n" + "Release evidence. " * 12)
        self.write("releases/migrations/5.0.0.md", "# Migration\n## Before\nSave context.\n## Steps\nAudit then apply.\n## Verify\nCheck result.\n## Rollback\nRestore.\n## Existing projects\nKeep requirements.\n")
        self.write("governance/requirements.csv", "id,requirement,acceptance,evidence,status\nREQ-1,Keep sources,Verified hashes,kit/manifest.json,implemented\n")
        self.write("docs/en/GUIDE.md", "# Synthetic guide\n" + "A complete procedure. " * 10)
        entries = []
        source_hash = sha((self.root / "docs/en/GUIDE.md").read_bytes())
        for locale in ("uk", "de", "it"):
            self.write(f"docs/{locale}/GUIDE.md", f"# {locale} guide\n" + "A complete translation. " * 10)
            entries.append({"locale": locale, "path": f"docs/{locale}/GUIDE.md", "source_sha256": source_hash, "status": "complete"})
        self.json("docs/translations.json", {"source": "docs/en/GUIDE.md", "source_sha256": source_hash, "translations": entries})
        self.write("README.md", "# Synthetic kit\n\n[Guide](docs/en/GUIDE.md)\n")

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")

    def json(self, relative, data):
        self.write(relative, json.dumps(data, indent=2) + "\n")

    def test_source_corruption_is_detected_and_prevents_package(self):
        self.assertTrue(check(self.root)["ok"])
        self.write("kit/skills/example/SKILL.md", "tampered")
        self.assertFalse(check(self.root)["ok"])
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            build(self.root, Path(self.temp.name) / "out")

    def test_changed_english_guide_invalidates_translations(self):
        p = self.root / "docs/en/GUIDE.md"
        p.write_text(p.read_text() + "\nA new installation step.\n")
        errors = check(self.root)["errors"]
        self.assertTrue(any("stale" in x for x in errors))

    def test_private_project_export_is_rejected(self):
        self.write("kit/PROJECT_AGENT_SOURCE/customer.json", '{"private":true}')
        self.assertTrue(any("excluded private" in x for x in check(self.root)["errors"]))

    def test_packages_are_byte_reproducible_and_have_correct_descriptor(self):
        first = build(self.root, Path(self.temp.name) / "first")
        for p in self.root.rglob("*"):
            if p.is_file():
                os.utime(p, (1700000000, 1700000000))
        second = build(self.root, Path(self.temp.name) / "second")
        self.assertEqual(first["files"], second["files"])
        archive = Path(self.temp.name) / "first" / "Agent_System_5.0.0_CODEX.zip"
        with zipfile.ZipFile(archive) as z:
            self.assertIn("kit/skills/example/SKILL.md", z.namelist())
            self.assertFalse(json.loads(z.read("PACKAGE.json"))["installation_performed"])
            self.assertEqual(json.loads(z.read("PACKAGE.json"))["mode"], "CODEX")

    def test_symlink_and_path_escape_are_rejected(self):
        outside = Path(self.temp.name) / "outside-secret"
        outside.write_text("private")
        (self.root / "templates").mkdir()
        (self.root / "templates/leak").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"):
            collect(self.root, ["templates"])

    def test_excluded_dependency_links_are_not_sources_but_included_links_still_reject(self):
        self.write("apps/example/server.mjs", "// source")
        self.write("apps/example/node_modules/library/index.mjs", "// dependency")
        binary = self.root / "apps/example/node_modules/.bin/tool"
        binary.parent.mkdir(); binary.symlink_to("../library/index.mjs")
        paths = {p.relative_to(self.root).as_posix() for p in collect(self.root, ["apps"])}
        self.assertEqual(paths, {"apps/example/server.mjs"})
        (self.root / "apps/example/linked-source.mjs").symlink_to("server.mjs")
        with self.assertRaisesRegex(ValueError, "symlink"):
            collect(self.root, ["apps"])

    def test_missing_migration_and_broken_link_are_detected(self):
        (self.root / "releases/migrations/5.0.0.md").unlink()
        self.write("README.md", "[missing instructions](docs/no-such-guide.md)\n")
        errors = check(self.root)["errors"]
        self.assertTrue(any("migration" in x for x in errors))
        self.assertTrue(any("broken local link" in x for x in errors))

    def test_icon_change_is_caught_even_after_source_manifest_refresh(self):
        old_icon = b"<svg><title>Established icon</title></svg>"
        self.write("kit/skills/example/assets/icon.svg", old_icon.decode())
        self.json("governance/ICON_BASELINE.json", {"skills": {"example": {"interface": {}, "files": {"assets/icon.svg": sha(old_icon)}}}})
        self.write("kit/skills/example/assets/icon.svg", "<svg><title>Unexpected redesign</title></svg>")
        manifest = json.loads((self.root / "kit/manifest.json").read_text())
        p = self.root / "kit/skills/example/assets/icon.svg"
        manifest["skills"][0]["files"]["assets/icon.svg"] = {"sha256": sha(p.read_bytes()), "size": p.stat().st_size, "mode": 420}
        self.json("kit/manifest.json", manifest)
        self.assertTrue(any("existing icon changed" in x for x in check(self.root)["errors"]))


if __name__ == "__main__":
    unittest.main()
