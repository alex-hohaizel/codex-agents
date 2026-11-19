import json
from argparse import Namespace
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import native_canary as native


class NativeModelPolicyTests(unittest.TestCase):
    def test_candidate_uses_release_model_and_alternate_requires_baseline(self):
        self.assertEqual(native.managed_model(), "gpt-6.2-sol")
        with self.assertRaisesRegex(ValueError, "explicit baseline replays"):
            native.managed_model("gpt-6.1-sol")
        self.assertEqual(
            native.managed_model("gpt-6.1-sol", baseline=True), "gpt-6.1-sol"
        )

    def test_missing_policy_fails_even_with_explicit_model(self):
        with tempfile.TemporaryDirectory() as location, patch.object(native, "REPO", Path(location)):
            with self.assertRaisesRegex(ValueError, "managed model policy is missing or invalid"):
                native.managed_model("gpt-6.1-sol", baseline=True)

    def test_native_typed_model_receipts_distinguish_config_and_actual_model(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict("os.environ", {"CODEX_HOME": directory}):
            thread = str(uuid4())
            day = Path(directory) / "sessions" / datetime.now().astimezone().strftime("%Y/%m/%d")
            day.mkdir(parents=True)
            path = day / f"rollout-exact-{thread}.jsonl"
            unrelated = day / f"rollout-unrelated-{uuid4()}.jsonl"
            unrelated.write_text("private malformed contents", encoding="utf8")
            context = {
                "type": "turn_context",
                "payload": {"model": "gpt-6.2-sol", "effort": "high"},
            }
            events = [
                {"type": "session_meta", "payload": {"id": thread}},
                {"type": "event_msg", "payload": {"model": "gpt-6.1-sol", "effort": "low"}},
                context,
            ]
            encoded = [(json.dumps(event) + "\n").encode() for event in events]
            path.write_bytes(b"".join(encoded))
            receipt = native.native_turn_receipt(thread)
            self.assertTrue(native.matches_model(receipt, "gpt-6.2-sol", "high"))
            self.assertFalse(native.matches_model(receipt, "gpt-6.1-sol", "high"))
            self.assertEqual(receipt["event_sha256"], native.sha(encoded[2]))
            self.assertEqual(receipt["event_line"], 3)
            path.write_bytes(b"".join(encoded + [encoded[2]]))
            self.assertIsNone(native.native_turn_receipt(thread))

    def test_ephemeral_fixture_retains_no_rollout_by_default(self):
        case = {"sandbox": "read-only", "persist": False, "skills": [], "files": {},
                "allowed_changes": [], "checks": [], "prompt": "Read-only synthetic task"}
        model = native.managed_model()
        native_id = str(uuid4())
        event_data = (
            {"type": "thread.started", "thread_id": native_id},
            {"type": "turn.completed", "usage": {}},
        )
        def launch(argv, prompt, out, diagnostics, deadline):
            self.assertEqual("--ephemeral" in argv, not args.persist_model_receipt)
            out.write(b"".join((json.dumps(event) + "\n").encode() for event in event_data))
            return 0

        with tempfile.TemporaryDirectory() as folder:
            for persist in (False, True):
                with self.subTest(persist=persist):
                    args = Namespace(prepare_only=False, model=model, effort="high", codex="codex",
                                     deadline=30, persist_model_receipt=persist)
                    model_receipt = {"observed_model": model, "observed_effort": "high"}
                    with patch.object(native, "run_native", side_effect=launch), patch.object(
                        native, "native_turn_receipt", return_value=model_receipt
                    ) as read:
                        result = native.execute(f"ephemeral-{persist}", case, args, Path(folder))
                    self.assertEqual(result["persisted"], persist)
                    self.assertEqual(result["model_receipt"], model_receipt if persist else None)
                    self.assertEqual(result["status"], "passed-controlled" if persist else "unverified-effective-model")
                    if persist:
                        read.assert_called_once_with(native_id)
                    else:
                        read.assert_not_called()

    def test_only_authoritative_spawn_activity_and_all_child_turns_support_role_proof(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict("os.environ", {"CODEX_HOME": folder}):
            day = Path(folder) / "sessions" / datetime.now().astimezone().strftime("%Y/%m/%d")
            day.mkdir(parents=True)
            parent, child = str(uuid4()), str(uuid4())
            role = "test-role"
            model = native.managed_model()
            prose = "Inspect only the named fixture."
            profile = f'developer_instructions = """\n{prose}\n"""'
            def record(kind, **payload):
                return {"type": kind, "payload": payload}
            def save(thread, events):
                path = day / f"rollout-fixture-{thread}.jsonl"
                path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf8")
            parent_events = [
                record("session_meta", id=parent),
                record("response_item", type="function_call", name="spawn_agent", call_id="failed",
                       arguments=json.dumps({"agent_type": role, "wrong_field": True})),
                record("response_item", type="function_call_output", call_id="failed",
                       output="failed to parse function arguments: wrong_field"),
                record("response_item", type="function_call", name="spawn_agent", call_id="confirmed",
                       arguments=json.dumps({"agent_type": role})),
                record("event_msg", type="item_completed",
                       item={"type": "SubAgentActivity", "kind": "started", "id": "confirmed",
                             "agent_thread_id": child}),
            ]
            child_events = [
                record("session_meta", id=child,
                       source={"subagent": {"thread_spawn": {"parent_thread_id": parent, "agent_role": role}}}),
                record("turn_context", model=model, effort="high"),
                record("response_item", type="message", role="developer", content=[{"text": prose}]),
                record("event_msg", type="task_complete"),
                record("turn_context", model=model, effort="high"),
                record("event_msg", type="task_complete"),
            ]
            save(parent, parent_events)
            save(child, child_events)
            proof = native.owned_role_provenance(parent, role, profile, model, "high")
            self.assertTrue(proof["observed"])
            self.assertEqual(proof["requested_spawn_attempts"], 2)
            self.assertEqual(proof["spawn_count"], 1)
            self.assertEqual(proof["invalid_arguments_rejected_without_effect"], 1)
            self.assertEqual(len(proof["child_model_receipts"]), 2)

            child_events[-2]["payload"]["effort"] = "low"
            save(child, child_events)
            self.assertFalse(native.owned_role_provenance(parent, role, profile, model, "high")["observed"])
            save(child, child_events[:4])
            parent_events[2]["payload"]["output"] = "unknown outcome"
            save(parent, parent_events)
            self.assertFalse(native.owned_role_provenance(parent, role, profile, model, "high")["observed"])

    def test_environment_does_not_forward_provider_credentials(self):
        with patch.dict("os.environ", {
            "CODEX_HOME": "/existing/codex",
            "OPENAI_API_KEY": "ambient-key",
            "CHATGPT_ACCESS_TOKEN": "ambient-token",
        }):
            environment = native.native_environment()
        self.assertEqual(environment["CODEX_HOME"], "/existing/codex")
        self.assertNotIn("OPENAI_API_KEY", environment)
        self.assertNotIn("CHATGPT_ACCESS_TOKEN", environment)


if __name__ == "__main__":
    unittest.main()
