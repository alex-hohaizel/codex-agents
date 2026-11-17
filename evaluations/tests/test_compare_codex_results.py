from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import TestCase

COMPARATOR = Path(__file__).resolve().parents[1] / "compare_codex_results.py"
VARIANTS = ("bare-codex", "reference", "product-baseline", "candidate")
CASE_SCHEMA = "atelier.codex-comparison/2"
RUN_SCHEMA = "atelier.codex-comparison-run/2"
CHECK = "preserve-original-order"
USAGE = {"input_tokens": 570, "cached_input_tokens": 105, "output_tokens": 200}


def digest(data):
    return sha256(data).hexdigest()


class ComparisonTest(TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        (self.root / "records").mkdir()
        self.case = {
            "schema": CASE_SCHEMA, "case_id": "labels-plan",
            "input": self.write("inputs.txt", b"Plan a case-insensitive change; preserve first order."),
            "scope_profile": self.write("scope.json", b'{"mode":"read-only","external":[]}' + bytes([10])),
            "model": "codex-model", "effort": "medium",
            "budget": {"max_wall_ms": 30000, "max_input_tokens": 2000, "max_output_tokens": 500},
            "required_checks": [CHECK],
            "variants": {name: digest(name.encode()) for name in VARIANTS},
            "observers": ["runner-one"], "reviewers": ["reviewer-one"],
        }
        self.case_pin = self.write_json("case.json", self.case)
        self.paths = {}

    def write(self, name, body):
        (self.root / name).write_bytes(body)
        return {"path": name, "sha256": digest(body)}

    def write_json(self, name, body):
        return self.write(name, (json.dumps(body, sort_keys=True) + "\n").encode())

    def record(self, variant, *, terminal="completed", outcome="pass", wall_ms=9200,
               thread=None):
        index = VARIANTS.index(variant) + 1
        thread = thread or f"00000000-0000-4000-8000-{index:012d}"
        events = [{"type": "thread.started", "thread_id": thread}]
        counts = USAGE.copy() if terminal == "completed" else None
        if terminal == "completed":
            events.append({"type": "turn.completed", "usage": counts})
        if terminal == "failed":
            events.append({"type": "turn.failed", "error": {"message": "Fixture failure"}})
        trace = "\n".join(json.dumps(event) for event in events) + "\n"
        receipt = {
            "schema": RUN_SCHEMA, "case_sha256": self.case_pin["sha256"],
            "case_id": self.case["case_id"], "variant": variant,
            "input_sha256": self.case["input"]["sha256"],
            "source_sha256": self.case["variants"][variant],
            "scope_sha256": self.case["scope_profile"]["sha256"],
            "model": self.case["model"], "effort": self.case["effort"],
            "budget": self.case["budget"], "observer": "runner-one",
            "reviewer": "reviewer-one", "native": {
                "thread_id": thread, "terminal": terminal,
                "trace": self.write(f"records/{variant}.jsonl", trace.encode()),
            },
            "metrics": {"wall_ms": wall_ms, "usage": counts},
            "checks": {CHECK: {
                "status": outcome,
                "evidence": [self.write(
                    f"records/{variant}-review.txt",
                    f"{variant} review: preservation {outcome}".encode())],
            }},
        }
        path = f"records/{variant}.json"
        self.paths[variant] = path
        self.write_json(path, receipt)
        return receipt

    def compare(self, expected_exit):
        args = [sys.executable, "-B", str(COMPARATOR), "--root", str(self.root),
                "--case", "case.json"]
        for variant, path in self.paths.items():
            args.extend(("--receipt", f"{variant}={path}"))
        result = subprocess.run(args, check=False, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_completed_comparison_retains_failed_check_and_native_usage(self):
        for variant in VARIANTS:
            self.record(variant, outcome="fail" if variant == "reference" else "pass")
        result = self.compare(0)
        self.assertEqual(result["comparison_status"], "complete")
        self.assertEqual(result["runs"]["reference"]["status"], "failed")
        self.assertEqual(result["runs"]["candidate"]["status"], "passed")
        self.assertEqual(result["runs"]["candidate"]["trace_usage"], USAGE)
        self.assertFalse(result["native_origin_authenticated"])
        self.assertFalse(result["reviewer_independence_authenticated"])
        self.assertNotIn("winner", result)
        self.assertEqual(self.compare(0), result)

    def test_three_product_variants_are_a_complete_case(self):
        self.case["variants"].pop("reference")
        self.case_pin = self.write_json("case.json", self.case)
        for variant in self.case["variants"]:
            self.record(variant)
        result = self.compare(0)
        self.assertEqual(set(result["runs"]), set(self.case["variants"]))
        self.paths["reference"] = "records/undeclared.json"
        invalid = self.compare(2)
        self.assertEqual(invalid["error"], "receipt variant is absent from frozen case")

    def test_missing_and_interrupted_runs_preserve_known_negative(self):
        self.record("bare-codex", terminal="failed", outcome="fail")
        self.record("reference", terminal="interrupted", outcome="unverified")
        self.record("product-baseline", wall_ms=30001)
        result = self.compare(1)["runs"]
        self.assertEqual(result["bare-codex"]["status"], "failed")
        self.assertIn("native turn failed", result["bare-codex"]["failures"])
        self.assertIn("wall budget exceeded", result["product-baseline"]["failures"])
        self.assertEqual(result["candidate"]["issues"], ["receipt missing"])
        self.assertEqual(result["reference"]["status"], "incomplete")

    def test_separate_frozen_controls_must_match(self):
        for variant, field, replacement in (
                ("bare-codex", "model", "different-model"),
                ("reference", "input_sha256", "e" * 64),
                ("product-baseline", "source_sha256", "e" * 64),
                ("candidate", "scope_sha256", "e" * 64)):
            receipt = self.record(variant)
            receipt[field] = replacement
            self.write_json(self.paths[variant], receipt)
        runs = self.compare(1)["runs"]
        for variant, field in zip(VARIANTS, ("model", "input_sha256", "source_sha256", "scope_sha256")):
            self.assertEqual(runs[variant]["issues"], [f"run {field} differs from frozen case"])

    def test_refuses_cross_lane_thread_reuse_and_invented_metrics(self):
        first = self.record("bare-codex")
        self.record("reference", thread=first["native"]["thread_id"])
        inflated = self.record("candidate")
        inflated["metrics"]["usage"]["output_tokens"] += 5
        self.write_json(self.paths["candidate"], inflated)
        runs = self.compare(1)["runs"]
        self.assertIn("native thread reused across variants", runs["bare-codex"]["issues"])
        self.assertIn("native thread reused across variants", runs["reference"]["issues"])
        self.assertIn("reported usage differs from native trace", runs["candidate"]["issues"])

    def test_mutated_or_missing_check_evidence_remains_unverified(self):
        receipt = self.record("candidate", outcome="fail")
        artifact = receipt["checks"][CHECK]["evidence"][0]
        self.write(artifact["path"], b"Changed review after recording.")
        row = self.compare(1)["runs"]["candidate"]
        self.assertEqual(row["checks"][CHECK]["status"], "unverified")
        self.assertEqual(row["checks"][CHECK]["reported_status"], "fail")
        receipt["checks"] = {}
        self.write_json(self.paths["candidate"], receipt)
        row = self.compare(1)["runs"]["candidate"]
        self.assertEqual(row["checks"][CHECK], {"status": "unverified", "reason": "check missing"})

    def test_rejects_linked_and_malformed_evidence(self):
        first = self.record("bare-codex")
        path = first["native"]["trace"]["path"]
        target = self.root / "copied-trace.jsonl"
        (self.root / path).rename(target)
        (self.root / path).symlink_to(target)
        wrong_thread = self.record("reference")
        wrong_thread["native"]["thread_id"] = first["native"]["thread_id"]
        self.write_json(self.paths["reference"], wrong_thread)
        self.paths["candidate"] = "../other.json"
        runs = self.compare(1)["runs"]
        self.assertIn("symlink", runs["bare-codex"]["issues"][0])
        self.assertIn("matching thread start", runs["reference"]["issues"][0])
        self.assertIn("evidence root", runs["candidate"]["issues"][0])

    def test_rejects_malformed_or_unpinned_case(self):
        self.write("inputs.txt", b"Unapproved revision")
        result = self.compare(2)
        self.assertIn("SHA-256 differs", result["error"])
        self.write("case.json", b'{"schema":"a","schema":"b"}')
        result = self.compare(2)
        self.assertEqual(result["error"], "invalid JSON object")
