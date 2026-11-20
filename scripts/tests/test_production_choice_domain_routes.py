import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from fixture_production_choices import current_pin, make_choice, put
from production_choices import decision_subject


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "kit" / "skills"
WEB = ROOT / "evaluations" / "fixtures" / "production-choice-web"


class DomainRouteTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.project = Path(temp.name).resolve()

    def run_script(self, skill, script, *args):
        return subprocess.run(
            [sys.executable, "-B", str(SKILLS / skill / "scripts" / script), *map(str, args)],
            capture_output=True, text=True, check=False,
        )

    def prototype(self, action, artifact, *args):
        return self.run_script("app-atelier-experience", "ux_prototype.py", action,
                               "--root", self.project, "--artifact", artifact, *args)

    def test_direct_walkthrough_generation_checks_choice_before_writing(self):
        artifact = self.project / "walkthrough.html"
        blocked = self.prototype("build", artifact, "--input", "unknown-walkthrough.json")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("production-choices.json", blocked.stderr)
        self.assertFalse(artifact.exists())

    def test_approved_master_checks_editable_source_and_flow_on_each_call(self):
        make_choice(self.project, target_kind="web")
        record = self.project / "production-choices.json"
        choice = json.loads(record.read_bytes())
        for name in ("riverdesk.html", "reports.js", "riverdesk.js", "riverdesk.css", "interaction.md"):
            shutil.copyfile(WEB / name, self.project / name)
        choice["decision"]["masters"] = [current_pin(self.project, "riverdesk.html")]
        choice["decision"]["flows"] = [current_pin(self.project, "interaction.md")]
        choice["decision"]["configuration"] = [current_pin(self.project, name)
                                                 for name in ("reports.js", "riverdesk.js", "riverdesk.css")]
        put(self.project, record.name, choice)
        approval_path = choice["decision"]["approval"]["path"]
        approval = json.loads((self.project / approval_path).read_bytes())
        approval["subject_sha256"] = decision_subject(self.project)
        choice["decision"]["approval"] = put(self.project, approval_path, approval)
        put(self.project, record.name, choice)

        artifact = self.project / "riverdesk.html"
        unchanged = self.prototype("verify-master", artifact)
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        receipt = json.loads(unchanged.stdout)
        self.assertEqual(receipt["master_sha256"], current_pin(self.project, "riverdesk.html")["sha256"])
        self.assertEqual(receipt["flows"][0]["path"], "interaction.md")
        self.assertFalse(receipt["runtime_verified"])

        duplicate = self.project / "substitute.html"
        shutil.copyfile(artifact, duplicate)
        substituted = self.prototype("verify-master", duplicate)
        self.assertEqual(substituted.returncode, 2)
        self.assertIn("exact approved master", substituted.stderr)

        for name in ("riverdesk.css", "interaction.md", "riverdesk.html"):
            with self.subTest(name=name):
                file = self.project / name
                original = file.read_bytes()
                file.write_bytes(original + b"\nmaterial drift\n")
                drift = self.prototype("verify-master", artifact)
                self.assertEqual(drift.returncode, 2)
                self.assertIn(name, drift.stderr)
                file.write_bytes(original)

    def test_game_illustration_missing_choice_precedes_passport_parsing(self):
        passport = self.project / "invalid-passport.json"
        passport.write_text("{'not': 'json'}", encoding="utf-8")
        current = self.run_script("gamedev-concepts", "concept_gate.py", passport,
                                  "--project-root", self.project, "--for-illustration")
        self.assertNotEqual(current.returncode, 0)
        self.assertIn("production-choices.json", current.stdout + current.stderr)
        historical = self.run_script("gamedev-concepts", "concept_gate.py", passport,
                                     "--project-root", self.project, "--for-illustration", "--historical")
        self.assertNotEqual(historical.returncode, 0)
        self.assertNotIn("production-choices.json", historical.stdout + historical.stderr)

    def test_app_native_phase_checks_choices_without_gating_legacy_repair(self):
        def app(*arguments, code=0):
            result = self.run_script("app-atelier-director", "state.py", "--project", self.project, *arguments)
            self.assertEqual(result.returncode, code, result.stdout + result.stderr)
            return json.loads(result.stdout)

        put(self.project, "profile.json", {"schema_version": "app-atelier-profile/1", "id": "fixture", "requirements": []})
        app("init", "--profile", self.project / "profile.json")
        self.assertTrue(app("phase-check", "--phase", "repair")["ready"])
        result = app("phase-check", "--phase", "build", code=1)
        self.assertFalse(result["ready"])
        self.assertIn("production-choices.json", " ".join(result["blockers"]))
        make_choice(self.project, target_kind="web", phase="scale")
        self.assertTrue(app("phase-check", "--phase", "build")["ready"])

    def test_chat_freeze_adopts_exact_choice_and_refuses_missing_or_stale_binding(self):
        material = {"schema_version": "chatbot.round/1", "requirements": [], "runs": [],
                    "team_policy": {"scope": {"kind": "stage"}}, "completion": {"stage": "prepared"}}
        round_file = self.project / "round.json"
        put(self.project, round_file.name, material)

        def freeze():
            return self.run_script("chatbot-atelier-director", "teamctl.py", "freeze", round_file)

        absent = freeze()
        self.assertEqual(absent.returncode, 1)
        self.assertIn("production-choices.json", absent.stdout)
        current = make_choice(self.project, target_kind="chatbot", phase="implement")
        accepted = freeze()
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        frozen = json.loads(round_file.read_bytes())
        self.assertEqual(frozen["production_choice_decision_sha256"], current["decision_sha256"])
        frozen["runs"] = [{"id": "prior", "kind": "integration", "status": "completed",
                           "production_choice_binding": {"phase": "implement", "decision_sha256": "0" * 64}}]
        put(self.project, round_file.name, frozen)
        previous = round_file.read_bytes()
        stale = freeze()
        self.assertEqual(stale.returncode, 1)
        self.assertIn("stale production decision", stale.stdout)
        self.assertEqual(round_file.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
