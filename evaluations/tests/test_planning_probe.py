"""Check reviewed planning routes and configurable artifact discovery."""

from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import planning_probe as probe


class PlanningProbeTest(unittest.TestCase):
    def test_quoted_status_and_status_outside_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            output = project / "review-plans"
            output.mkdir()
            spec = b"---\nstatus: 'ready-for-dev'\n---\n# Plan\n"
            (output / "spec.md").write_bytes(spec)
            (output / "result.md").write_text("---\nstatus: blocked\n---\nstatus: ready-for-dev\n")
            (output / "unframed.md").write_text("status: ready-for-dev\n")
            self.assertEqual(probe.ready_specs(project, "review-plans", "ready-for-dev"), [{
                "path": "review-plans/spec.md", "sha256": sha256(spec).hexdigest()
            }])

    def test_distinct_reviewed_routes_share_inputs_and_are_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            baseline = self.skill(root, "baseline", probe.LOCAL_SKILL, "released")
            candidate = self.skill(root, "candidate", probe.LOCAL_SKILL, "proposed")
            reference = self.skill(root, "user-route", "local-review", "admitted")
            config = root / "reference.json"
            probe.write_json(config, {
                "schema": probe.REFERENCE_SCHEMA,
                "source": str(reference),
                "source_sha256": probe.inventory_digest(probe.native.inspect_files(reference)),
                "skill": "local-review",
                "artifact_directory": "drafts/planning",
                "ready_status": "reviewed",
                "observed_command": "summarize-plan.py",
            })
            case = root / "case"
            result = probe.prepare(case, baseline, candidate, use_git=False, reference=config)
            self.assertEqual(tuple(result["variants"]), probe.VARIANTS)
            self.assertEqual(len(set(result["route_sha256"].values())), 4)
            for variant in probe.VARIANTS:
                project = case / variant / "project"
                self.assertFalse((project / ".git").exists())
                for ref, expected in probe.PROTECTED.items():
                    self.assertEqual((project / ref).read_text(), expected)
            self.assertFalse((case / "bare-codex/project/.agents").exists())
            route = probe.native.load_json(case / "reference/route.json")
            self.assertNotIn("source", route)
            self.assertEqual(route["artifact_directory"], "drafts/planning")
            (case / "candidate/project/.agents/skills" / probe.LOCAL_SKILL / "SKILL.md").write_text("modified")
            with self.assertRaisesRegex(ValueError, "staged route changed"):
                probe.run_lane(case, "candidate", "never-started", "model", "low", 10)

    def test_reference_requires_the_admitted_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            baseline = self.skill(root, "baseline", probe.LOCAL_SKILL, "released")
            reference = self.skill(root, "user-route", "local-review", "admitted")
            config = root / "reference.json"
            probe.write_json(config, {"schema": probe.REFERENCE_SCHEMA, "source": str(reference),
                                      "source_sha256": "0" * 64, "skill": "local-review"})
            with self.assertRaisesRegex(ValueError, "differs from the reviewed digest"):
                probe.prepare(root / "case", baseline, baseline, use_git=False, reference=config)

    @staticmethod
    def skill(root, directory, name, text):
        source = root / directory
        source.mkdir()
        (source / "SKILL.md").write_text(f"---\nname: {name}\n---\n{text}\n")
        return source


if __name__ == "__main__":
    unittest.main()
