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
from blueprint import proposal_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[2] / "scripts/tests"))
from fixture_production_choices import make_choice


def load(path):
    module = types.ModuleType("test_current_source")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class GeneratedChildrenTests(unittest.TestCase):
    def run_check(self, complete, missing=None, execute_helpers=False, decision=None):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as tmp:
            base = Path(tmp)
            blueprint = base / "blueprint.json"
            proposal = fixture2()
            child = base / "neutral-child"
            child.mkdir()
            if complete:
                checker = load(ROOT / "scripts/check_generated_inheritance.py")
                for relative in (*checker.RESOURCES, *checker.BRIEFING_TEMPLATES, *checker.DOMAIN_BRIEFING):
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
                if missing:
                    (child/missing).unlink()
                if decision == 'wrong-entry':
                    entry = child / 'SKILL.md'
                    entry.write_text(entry.read_text().replace('name: neutral-child', 'name: other-child'))
                if execute_helpers:
                    # Execute the actual copied utility from the child, with no
                    # constructor path on its import path and without a model job.
                    emitted = subprocess.run(
                        [sys.executable, "-B", str(child / "scripts/ai_production.py"), "schema"],
                        cwd=child, text=True, capture_output=True, timeout=8,
                    )
                    self.assertEqual(emitted.returncode, 0, emitted.stderr)
                    self.assertEqual(json.loads(emitted.stdout),
                                     json.loads((child / "assets/ai-production.schema.json").read_text()))
                    capsule_help = subprocess.run(
                        [sys.executable, "-B", str(child / "scripts/context_capsule.py"), "--help"],
                        cwd=child, text=True, capture_output=True, timeout=8,
                    )
                    self.assertEqual(capsule_help.returncode, 0, capsule_help.stderr)
                    self.assertIn('--require-complete', capsule_help.stdout)
            command = [sys.executable, "-B", str(ROOT / "scripts/blueprint.py"), "check",
                       str(blueprint), "--child", str(child)]
            if decision:
                if decision != 'no-modules':
                    proposal['architecture']['modules'] = [
                        {'name': 'different-child' if decision == 'wrong-module' else child.name,
                         'stage_ids': [stage['id'] for stage in proposal['stages']]},
                    ]
                if decision != 'missing':
                    artifacts = [child.relative_to(base).as_posix() + '/SKILL.md'] if decision != 'unrelated' else None
                    receipt = make_choice(base, target_kind='agent', phase='accept',
                                          accepted_artifacts=artifacts)
                    proposal['production_decision_sha256'] = receipt['decision_sha256']
                    if decision == 'stale':
                        (base / '_choice-fixture/configuration.md').write_text('Unapproved replacement')
                proposal['approval'] = {
                    'actor': 'user', 'decision': 'approve', 'proposal_hash': proposal_hash(proposal),
                    'proposal_version': proposal['version'], 'verbatim': 'Fixture only.',
                    'source': 'synthetic record', 'timestamp': '2026-11-20', 'scope': 'test only',
                }
                command.append('--approved')
            blueprint.write_text(json.dumps(proposal))
            before = sorted(str(p.relative_to(child)) for p in child.rglob("*"))
            proc = subprocess.run(command, text=True, capture_output=True, timeout=8)
            if execute_helpers:
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertTrue(json.loads(proc.stdout)['material_gate_passed'])
                self.exercise_staged_consumer(base, child)
            self.assertEqual(before, sorted(str(p.relative_to(child)) for p in child.rglob("*")))
            return proc.returncode, json.loads(proc.stdout)

    def exercise_staged_consumer(self, base, child):
        source = base / 'native-import.json'
        source.write_text(json.dumps({
            'schema': 'codex-agent-import/1',
            'modules': [{'id': 'design-fixture', 'version': '1.0.0',
                         'members': [{'kind': 'skill', 'name': child.name, 'source': child.name}]}],
        }))
        target = base / 'existing-project'
        target.mkdir()
        importer = ROOT.parent / 'agent-foundry/scripts/import_codex.py'
        command = [sys.executable, '-B', str(importer)]
        subject = [str(source), '--target', str(target)]
        audit = subprocess.run([*command, 'audit', *subject], text=True, capture_output=True, timeout=8)
        self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
        plan = json.loads(audit.stdout)
        staged = base / 'isolated-consumer'
        stage = subprocess.run([*command, 'stage', *subject, '--expect', plan['plan_sha256'],
                                '--output', str(staged)], text=True, capture_output=True, timeout=8)
        self.assertEqual(stage.returncode, 0, stage.stdout + stage.stderr)
        self.assertEqual(list(target.iterdir()), [])
        installed = staged / '.agents/skills' / child.name
        self.assertEqual((installed / 'SKILL.md').read_bytes(), (child / 'SKILL.md').read_bytes())
        verify = [sys.executable, '-B', str(installed / 'scripts/production_choices.py'),
                  'verify', str(staged), '--phase', 'implement']
        unsupported = subprocess.run(verify, cwd=staged, text=True, capture_output=True, timeout=8)
        self.assertEqual(unsupported.returncode, 1, unsupported.stdout + unsupported.stderr)
        make_choice(staged, target_kind='agent')
        checked = subprocess.run(verify, cwd=staged, text=True, capture_output=True, timeout=8)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertTrue(json.loads(checked.stdout)['ok'])

    def test_authored_child_carries_local_current_resources(self):
        code, result = self.run_check(True)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["children_checked"], 1)
        standard = result["operating_standard"]
        self.assertEqual(standard["release"], "6.7.0")
        self.assertIn("scripts/briefing.py", standard["resources"])
        self.assertIn("scripts/interaction.py", standard["resources"])
        self.assertIn("assets/status-view.schema.json", standard["resources"])
        self.assertEqual(standard["managed_model"],
                         json.loads((ROOT / "assets/managed-model.json").read_bytes()))
        self.assertIs(result["quality_certified"], False)
        self.assertFalse(result["material_gate_passed"])

    def test_current_approved_child_requires_choice_and_exact_child_evidence(self):
        code, result = self.run_check(True, decision='accepted')
        self.assertEqual(code, 0, result)
        self.assertTrue(result['material_gate_passed'])
        for state, message in [('missing', 'production_decision_sha256'),
                               ('stale', 'configuration.md'),
                               ('no-modules', 'exact installable module names'),
                               ('wrong-module', 'exact approved module set'),
                               ('wrong-entry', 'frontmatter name'),
                               ('unrelated', 'exact child skill')]:
            with self.subTest(state=state):
                code, result = self.run_check(True, decision=state)
                self.assertEqual(code, 1, result)
                self.assertIn(message, str(result['errors']))
                self.assertFalse(result['material_gate_passed'])

    def test_empty_child_cannot_pass_record_check_as_materialized(self):
        code, result = self.run_check(False)
        self.assertEqual(code, 1)
        self.assertEqual(result["children_checked"], 1)
        self.assertTrue(result["errors"])

    def test_real_copied_helpers_execute_without_a_neighboring_constructor(self):
        code, result = self.run_check(True, execute_helpers=True, decision='accepted')
        self.assertEqual(code, 0, result)
        self.assertIs(result['quality_certified'], False)

    def test_quality_and_context_are_material_resources_not_only_entry_labels(self):
        for resource in ('references/production-quality.md','references/context-capsule.md','assets/production-profiles.json','scripts/context_capsule.py','references/ai-production.md','assets/ai-production.schema.json','scripts/ai_production.py','references/production-choices.md','assets/technology-catalog.json','scripts/production_choices.py'):
            with self.subTest(resource=resource):
                code,result=self.run_check(True,missing=resource)
                self.assertEqual(code,1,result)
                self.assertTrue(any(resource in issue for issue in result['errors']))


if __name__ == "__main__":
    unittest.main()
