"""Task projection guards keep factory, execution and observed receipts separate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "optional-skills/atelier-orchestrator"
SPEC = importlib.util.spec_from_file_location("orchestrator_routing", SKILL / "scripts/check_routing.py")
ROUTING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTING)


def task():
    value = json.loads((SKILL / "assets/task-contract.json").read_text(encoding="utf8"))
    value.update(is_template=False, task_id="isolated-task", objective="Explain this isolated example",
                 owner="current-integrator", authority_ref="original-user-request", consumer="owner",
                 stop="Return the requested explanation", recovery="Reconcile the same task before retry",
                 original_result_acceptance=["The explanation answers the original question"])
    value["entry"] = {"surface": "chat", "request_ref": "original-user-request",
                      "original_objective": value["objective"]}
    value["routing"] = {"route": "direct", "reason": "The request is self-contained",
                        "execution_owner": "current-integrator", "source_pins": [], "capability_gaps": []}
    value["execution_scope"] = {"requested": True, "activity": "task_execution",
                                "authority_ref": "original-user-request", "acceptance": value["original_result_acceptance"]}
    value["continuation"]["next_action"] = "Answer the original question"
    return value


def source_pin(selector="future-project-agent"):
    return {"selector": selector, "source_ref": "actual-host-source", "sha256": "a" * 64}


class RoutingContractTests(unittest.TestCase):
    def test_projectless_direct_request_needs_no_factory_or_project(self):
        value = task()
        self.assertIsNone(value["project_id"])
        result = ROUTING.validate(value, ready=True)
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(value["creation_scope"]["requested"])
        self.assertFalse(result["execution_performed"])
        self.assertFalse(result["quality_certified"])

    def test_unknown_project_agent_is_not_an_active_continuation(self):
        value = task()
        value["routing"].update(route="project_agent", source_pins=[source_pin()])
        value["continuation"].update(preferred_project_agent="future-project-agent",
                                     project_agent_status="planned", project_agent_source_pin=source_pin(),
                                     recommendation="Continue through the project agent")
        result = ROUTING.validate(value, ready=True)
        self.assertFalse(result["valid"])
        value["continuation"]["project_agent_status"] = "host_discovered"
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])

    def test_delivery_receipt_does_not_start_executor(self):
        value = task()
        value["execution"].update(state="started", executor_ref="native-executor",
                                   receipt_refs=[{"kind": "delivery", "ref": "saved-message", "actor": "host"}])
        result = ROUTING.validate(value, ready=True)
        self.assertFalse(result["valid"])
        value["execution"]["receipt_refs"].append({"kind": "execution_start", "ref": "native-start", "actor": "host"})
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])

    def test_constructed_agent_does_not_complete_product(self):
        value = task()
        value["creation_scope"].update(requested=True, stage="construction", authority_ref="approved-agent-scope",
                                         acceptance=["Accepted installed agent"])
        value["execution_scope"]["activity"] = "product_execution"
        value["execution"].update(state="result", executor_ref="native-executor",
                                   receipt_refs=[{"kind": "execution_result", "ref": "agent-package",
                                                  "actor": "foundry", "activity": "skill_construction"}])
        result = ROUTING.validate(value, ready=True)
        self.assertFalse(result["valid"])
        value["execution"]["receipt_refs"].append({"kind": "execution_result", "ref": "integrated-product-output",
                                                    "actor": "project-agent", "activity": "product_execution"})
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])

    def test_agent_only_scope_can_end_with_agent_output(self):
        value = task()
        value["routing"].update(route="create_agent", source_pins=[source_pin("agent-foundry")])
        value["creation_scope"].update(requested=True, stage="construction", authority_ref="approved-agent-scope",
                                         acceptance=["Accepted installed agent"])
        value["execution_scope"]["requested"] = False
        value["execution"].update(state="result", executor_ref="foundry",
                                   receipt_refs=[{"kind": "execution_result", "ref": "agent-package",
                                                  "actor": "foundry", "activity": "skill_construction"}])
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])

    def test_self_maintenance_apply_requires_review_before_copy_and_resolved_conflicts(self):
        value = task()
        value["routing"]["route"] = "maintain_system"
        value["maintenance"] = {"target_kind": "self", "action": "apply", "target_refs": [source_pin("atelier-orchestrator")],
                                 "preservation": ["current-identity-and-settings"], "unresolved_conflicts": []}
        self.assertFalse(ROUTING.validate(value, ready=True)["valid"])
        value["maintenance"].update(review_ref="reviewed-diff", rollback_ref="actual-before-copy")
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])
        value["maintenance"]["unresolved_conflicts"] = ["unknown-local-source-edit"]
        self.assertFalse(ROUTING.validate(value, ready=True)["valid"])

    def test_acceptance_needs_review_and_owner_source_not_just_completion(self):
        value = task()
        value["execution"].update(state="accepted", executor_ref="native-executor", receipt_refs=[
            {"kind": "execution_result", "ref": "answer-output", "actor": "executor", "activity": "task_execution"}])
        self.assertFalse(ROUTING.validate(value, ready=True)["valid"])
        value["execution"]["receipt_refs"] += [
            {"kind": "review", "ref": "scoped-self-check", "actor": "executor", "independent": False},
            {"kind": "owner_acceptance", "ref": "exact-owner-decision", "actor": "owner"}]
        result = ROUTING.validate(value, ready=True)
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["human_authority_authenticated"])

    def test_missing_capability_is_explicit_and_does_not_create_an_engine(self):
        value = task()
        value["routing"].update(route="bridge", capability_gaps=["No supported device operation"])
        value["execution"].update(state="blocked")
        self.assertTrue(ROUTING.validate(value, ready=True)["valid"])
        value["routing"]["capability_gaps"] = []
        self.assertFalse(ROUTING.validate(value, ready=True)["valid"])

    def test_old_projection_is_readable_but_not_retroactively_ready(self):
        value = {"schema_version": "atelier.orchestrator-task/1", "is_template": False, "objective": "old task"}
        result = ROUTING.validate(value)
        self.assertTrue(result["valid"])
        self.assertEqual(result["routing_status"], "legacy_not_declared")
        self.assertFalse(ROUTING.validate(value, ready=True)["valid"])

    def test_untrusted_shape_and_duplicate_json_are_rejected(self):
        for bad in ({}, [], {"route": "direct"}):
            value = task()
            value["execution"]["state"] = bad
            self.assertFalse(ROUTING.validate(value, ready=True)["valid"])
        with self.assertRaises(ValueError):
            ROUTING.strict_json_loads('{"authority_ref":"old","authority_ref":"new"}')
        with self.assertRaises(ValueError):
            ROUTING.strict_json_loads('{"budget":NaN}')

    def test_cli_checks_current_projection_without_executing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task.json"
            path.write_text(json.dumps(task()), encoding="utf8")
            p = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/check_routing.py"), str(path), "--ready"],
                               capture_output=True, text=True, timeout=5)
            self.assertEqual(p.returncode, 0, p.stderr)
            result = json.loads(p.stdout)
            self.assertTrue(result["valid"])
            self.assertEqual(result["grants_created"], [])

    def test_documented_helpers_are_self_contained_and_source_pinned(self):
        pins = json.loads((SKILL / "assets/helper-source-pins.json").read_text(encoding="utf8"))
        for record in pins["files"]:
            local, source = SKILL / record["path"], REPO / record["source"]
            self.assertEqual(hashlib.sha256(local.read_bytes()).hexdigest(), record["sha256"])
            self.assertEqual(local.read_bytes(), source.read_bytes())
        for script in ("discover_specialists.py", "check_component_handoff.py"):
            p = subprocess.run([sys.executable, "-B", str(SKILL / "scripts" / script), "--help"],
                               capture_output=True, text=True, timeout=5)
            self.assertEqual(p.returncode, 0, p.stderr)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "SKILL.md"
            source.write_text('---\nname: isolated-specialist\ndescription: Isolated source fixture\n---\n# Isolated 1.0.0\n', encoding="utf8")
            p = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/discover_specialists.py"),
                                "inventory", "--host", "codex", "--root", str(root)], capture_output=True, text=True, timeout=5)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data["candidates"][0]["name"], "isolated-specialist")
            self.assertTrue(data["candidates"][0]["availability"]["source_checked"])
            self.assertFalse(data["execution_performed"])


if __name__ == "__main__":
    unittest.main()
