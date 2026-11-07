"""Exercise authored-child checking separately from blueprint-record readiness."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

from test_blueprint_v2 import fixture2

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    module = types.ModuleType("test_current_source")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class GeneratedChildrenTests(unittest.TestCase):
    def run_check(self, complete):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            blueprint = base / "blueprint.json"
            blueprint.write_text(json.dumps(fixture2()))
            child = base / "neutral-child"
            child.mkdir()
            if complete:
                checker = load(ROOT / "scripts/check_generated_inheritance.py")
                for relative in checker.RESOURCES:
                    target = child / relative;target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / relative, target)
                links = "".join("Read [method](" + p + ").\n" for p in checker.ENTRY_LINKS)
                (child / "SKILL.md").write_text("---\nname: neutral-child\ndescription: Analyze the assigned bounded task.\n---\n\n" + links)
                visual = load(ROOT / "scripts/visual_identity.py")
                visual.create(child, "N")
                (child / "agents").mkdir()
                (child / "agents/openai.yaml").write_text("interface:\n  display_name: Neutral project\n  icon_small: assets/icon.svg\n  icon_large: assets/icon.svg\n")
                snapshot = visual.freeze(child, "project")
                (child / "assets/visual-identity.lock.json").write_text(json.dumps(snapshot))
                (child / "assets/visual-identity-origin.json").write_text(json.dumps({"schema":"visual-identity-origin/1", "kind":"created"}))
            before = sorted(str(p.relative_to(child)) for p in child.rglob("*"))
            proc = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/blueprint.py"), "check", str(blueprint), "--child", str(child)], text=True, capture_output=True, timeout=8)
            self.assertEqual(before, sorted(str(p.relative_to(child)) for p in child.rglob("*")))
            return proc.returncode, json.loads(proc.stdout)

    def test_authored_child_carries_local_current_resources(self):
        code, result = self.run_check(True)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["children_checked"], 1)
        self.assertEqual(result["operating_standard"]["release"], "5.0.0")
        self.assertIs(result["quality_certified"], False)

    def test_empty_child_cannot_pass_record_check_as_materialized(self):
        code, result = self.run_check(False)
        self.assertEqual(code, 1)
        self.assertEqual(result["children_checked"], 1)
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
