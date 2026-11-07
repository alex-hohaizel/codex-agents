"""Synthetic transport/contract tests. Fixtures are not real play/device proof."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("game_model", ROOT / "scripts/game_model.py")
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)


fixture_spec = importlib.util.spec_from_file_location("current_contract_fixture", ROOT / "tests/test_v4_contract.py")
current_contract = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(current_contract)


class GameModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.model = current_contract.fixture(self.root)

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value)
        return path

    def evidence(self, check, proof, stage=None):
        return {
            "id": "FIXTURE-" + check["id"], "domain": check["domain"],
            "check_id": check["id"], "stage": stage or check["due_stage"],
            "modality": check["modality"], "proof_path": str(proof.relative_to(self.root)),
            "sha256": gm.sha(proof), "model_sha256": gm.digest(self.model),
            "scope_sha256": gm.scope_digest(self.model, check["domain"], check["id"]),
            "observer_id": "synthetic-independent-observer", "author_ids": [],
            "method": "unit-test fixture, not an actual observation",
            "observed_at": "2026-11-02T12:00:00+02:00", "environment": "synthetic test fixture",
            "origin": check["origin"],
        }

    def concept_evidence(self):
        proof = self.put("review.md", "Synthetic independent review receipt used only to test transport integrity.")
        self.model["evidence"] = [self.evidence(c, proof) for c in gm.requirements(self.model, "concept")]

    def check_named(self, name, stage="slice"):
        return next(c for c in gm.requirements(self.model, stage) if c["id"] == name)

    def observation(self, kind, **extra):
        # Recognizable media header is intentionally synthetic; this tests byte
        # routing, not whether a human actually captured a native game.
        image = self.root / "sample.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\n" + b"synthetic media fixture")
        receipt = {
            "schema_version": "game-atelier-observation/1", "kind": kind,
            "build_sha256": "a" * 64, "scenario_ids": ["SCENARIO-BASE"],
            "platform": "android",
            "samples": [{"path": "sample.png", "sha256": gm.sha(image), "kind": "image"}],
        }
        receipt.update(extra)
        return self.put(kind + ".json", receipt)

    def test_future_observation_is_not_gate_evidence(self):
        self.concept_evidence()
        self.model["evidence"][0]["observed_at"] = "2099-01-01T00:00:00+00:00"
        result = gm.validate(self.model, self.root)
        self.assertFalse(result["stage_ready"])
        self.assertTrue(any("future" in " ".join(e["errors"]) for e in result["evidence_errors"]))

    def test_malformed_device_is_a_reported_error_not_a_crash(self):
        proof = self.observation("device", device=[])
        check = self.check_named("product.device")
        errors = gm.proof_errors(self.model, self.evidence(check, proof), check, self.root)
        self.assertTrue(any("device must be an object" in error for error in errors), errors)

    def test_six_heterogeneous_examples_are_structurally_valid_but_not_stage_ready(self):
        paths = sorted((ROOT / "assets/examples").glob("model-*.json"))
        self.assertEqual(6, len(paths))
        for path in paths:
            with self.subTest(path=path.name):
                model = gm.read_json(path)
                self.assertEqual([], gm.design_errors(model))
                authoring = gm.validate(model, path.parent, design_only=True)
                self.assertTrue(authoring["structurally_valid"])
                self.assertFalse(authoring["stage_ready"])
                gate = gm.validate(model, path.parent)
                self.assertFalse(gate["stage_ready"])
                self.assertIn("product.applicability", gate["missing_checks"])

    def test_no_enemy_and_no_offer_do_not_require_enemy_or_purchase_system(self):
        self.assertNotIn("actors", gm.enabled(self.model))
        self.assertEqual("none", self.model["domains"]["commerce"]["model"])
        ids = {c["id"] for c in gm.requirements(self.model, "release")}
        self.assertNotIn("actors.runtime", ids)
        self.assertNotIn("commerce.integration", ids)

    def test_ui_only_board_can_disable_camera(self):
        board = gm.read_json(ROOT / "assets/examples/model-tactics.json")
        self.assertFalse(board["features"]["camera"]["enabled"])
        self.assertEqual([], gm.design_errors(board))

    def test_gameplay_feedback_cycles_allowed_but_unlock_cycle_rejected(self):
        self.model["dependencies"].append({"from": "RULE-B", "to": "RULE-A", "reason": "Feedback changes the next action"})
        self.assertEqual([], gm.design_errors(self.model))
        self.model["domains"]["progression"]["nodes"][0]["prerequisites"] = ["UNLOCK-ADVANCED"]
        self.assertIn("progression prerequisite cycle", gm.design_errors(self.model))

    def test_missing_rule_reference_rejected(self):
        self.model["domains"]["systems"]["links"][0]["to"] = "MISSING"
        self.assertIn("system link must reference rules", gm.design_errors(self.model))

    def test_missing_world_space_reference_rejected(self):
        self.model["domains"]["world"]["transitions"].append({
            "from": "SPACE-START", "to": "MISSING", "condition": "test", "new_decision": "test", "return_reason": "test"})
        self.assertIn("world transition must reference spaces", gm.design_errors(self.model))

    def test_core_cannot_be_disabled_by_feature_or_task_flag(self):
        self.model["features"]["input"]["enabled"] = False
        del self.model["domains"]["input"]
        self.model["required_evidence"] = []
        self.model["skip_device"] = True
        self.assertIn("core domain cannot be disabled: input", gm.design_errors(self.model))

    def test_scenario_coverage_and_counterfactual_required(self):
        self.model["scenarios"][0]["domains"].remove("camera")
        del self.model["scenarios"][0]["without_rule"]
        self.assertTrue(any("without_rule" in error for error in gm.design_errors(self.model)))

    def test_duplicate_ids_rejected(self):
        self.model["domains"]["input"]["actions"][0]["id"] = "RULE-A"
        self.assertIn("duplicate ID: RULE-A", gm.design_errors(self.model))

    def test_invalid_camera_fraction_and_bool_number_rejected(self):
        self.model["domains"]["camera"]["subject_fraction"] = {"min": .5, "max": .2}
        self.assertIn("camera subject_fraction min exceeds max", gm.design_errors(self.model))
        self.model["constraints"]["target_fps"] = True
        self.assertTrue(any("target_fps must be number" in e for e in gm.design_errors(self.model)))

    def test_concept_gate_accepts_only_current_independent_record(self):
        self.concept_evidence()
        self.assertTrue(gm.validate(self.model, self.root)["stage_ready"])
        self.model["evidence"][0]["observer_id"] = self.model["author_ids"][0]
        self.assertFalse(gm.validate(self.model, self.root)["stage_ready"])

    def test_stale_model_or_proof_invalidates_evidence(self):
        self.concept_evidence()
        self.model["title"] += " changed"
        result = gm.validate(self.model, self.root)
        self.assertTrue(any("scope hash is stale" in " ".join(e["errors"]) for e in result["evidence_errors"]))
        self.model["title"] = self.model["title"].replace(" changed", "")
        self.put("review.md", "changed fixture")
        result = gm.validate(self.model, self.root)
        self.assertTrue(any("proof hash mismatch" in " ".join(e["errors"]) for e in result["evidence_errors"]))

    def test_scoped_proof_reuses_unchanged_domain_and_rejects_changed_upstream(self):
        proof = self.put("review.md", "Synthetic scoped review fixture")
        check = self.check_named("input.design", "concept")
        ev = self.evidence(check, proof)
        ev["scope_sha256"] = gm.scope_digest(self.model, "input", check["id"])
        old_model_hash = ev["model_sha256"]
        self.model["domains"]["art"]["style"]["materials"] += " independently clarified"
        self.assertNotEqual(old_model_hash, gm.digest(self.model))
        self.assertEqual([], gm.proof_errors(self.model, ev, check, self.root))
        # Declared upstream edges make a rule part of the input contract scope.
        self.model["dependencies"].append({"from": "RULE-A", "to": "input", "reason": "Input feedback depends on this rule"})
        ev["scope_sha256"] = gm.scope_digest(self.model, "input", check["id"])
        self.model["domains"]["systems"]["rules"][0]["limit"] += " changed"
        self.assertTrue(any("scope hash is stale" in e for e in gm.proof_errors(self.model, ev, check, self.root)))

    def test_whole_model_hash_does_not_replace_required_scope_hash(self):
        proof = self.put("review.md", "Synthetic review fixture")
        check = self.check_named("input.design", "concept")
        evidence = self.evidence(check, proof)
        evidence.pop("scope_sha256")
        self.assertEqual(gm.digest(self.model), evidence["model_sha256"])
        self.assertTrue(any("requires the current dependency scope hash" in e
                            for e in gm.proof_errors(self.model, evidence, check, self.root)))

    def test_product_applicability_review_is_global_even_with_scope(self):
        proof = self.put("review.md", "Synthetic applicability review fixture")
        check = self.check_named("product.applicability", "concept")
        ev = self.evidence(check, proof)
        ev["scope_sha256"] = gm.scope_digest(self.model, "product", check["id"])
        self.model["domains"]["art"]["style"]["materials"] += " changed"
        self.assertTrue(gm.proof_errors(self.model, ev, check, self.root))

    def test_historical_reference_never_closes_runtime_check(self):
        c = self.check_named("systems.runtime")
        proof = self.put("history.md", "Historical concept reference, no runtime observation.")
        ev = self.evidence(c, proof)
        ev["origin"] = "historical_reference"
        self.assertTrue(gm.proof_errors(self.model, ev, c, self.root))

    def test_historical_and_explicit_superseded_records_do_not_poison_current_gate(self):
        self.concept_evidence()
        original = self.model["evidence"][0]
        historical = copy.deepcopy(original)
        historical.update(id="HISTORICAL-FIXTURE", origin="historical_reference", model_sha256="0" * 64)
        superseded = copy.deepcopy(original)
        superseded.update(id="SUPERSEDED-FIXTURE", status="superseded", superseded_by=original["id"], model_sha256="0" * 64)
        self.model["evidence"] += [historical, superseded]
        self.assertTrue(gm.validate(self.model, self.root)["stage_ready"])
        superseded["superseded_by"] = "MISSING"
        self.assertFalse(gm.validate(self.model, self.root)["structurally_valid"])

    def test_json_renamed_video_is_rejected(self):
        c = self.check_named("input.runtime")
        proof = self.put("fake.mp4", {"device": "claimed"})
        self.assertTrue(gm.proof_errors(self.model, self.evidence(c, proof), c, self.root))

    def test_static_image_does_not_prove_camera_motion(self):
        c = self.check_named("camera.runtime")
        proof = self.observation("runtime")
        self.assertTrue(any("motion" in e for e in gm.proof_errors(self.model, self.evidence(c, proof), c, self.root)))

    def test_device_receipt_needs_physical_device_and_supporting_sample(self):
        c = self.check_named("product.device")
        proof = self.observation("device", device={"platform": "android", "model": "fixture", "os": "fixture", "physical": False})
        self.assertTrue(gm.proof_errors(self.model, self.evidence(c, proof), c, self.root))
        receipt = gm.read_json(proof)
        receipt["device"]["physical"] = True
        proof = self.put("device.json", receipt)
        self.assertEqual([], gm.proof_errors(self.model, self.evidence(c, proof), c, self.root))
        receipt["samples"] = []
        proof = self.put("device.json", receipt)
        self.assertTrue(gm.proof_errors(self.model, self.evidence(c, proof), c, self.root))

    def test_player_receipt_needs_participants_and_concrete_outcomes(self):
        c = self.check_named("systems.player", "beta")
        proof = self.observation("player", participant_count=0, method="synthetic test fixture", outcomes=[])
        self.assertTrue(gm.proof_errors(self.model, self.evidence(c, proof), c, self.root))

    def test_safe_relative_paths_and_symlink_escape(self):
        for name in ("../elsewhere", "/etc/passwd", "C:\\proof.json", "https://example.test/proof"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                gm.safe_file(self.root, name)
        outside = self.root.parent / (self.root.name + "-outside.txt")
        outside.write_text("outside")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (self.root / "escape.txt").symlink_to(outside)
        with self.assertRaises(ValueError):
            gm.safe_file(self.root, "escape.txt")

    def test_preproduction_requires_pinned_detailed_specs(self):
        errors = gm.spec_errors(self.model, "preproduction", self.root)
        self.assertEqual(len(gm.enabled(self.model)), len(errors))
        specfile = self.put("specs.md", "Synthetic detailed spec fixture")
        self.model["spec_refs"] = [{"domain": d, "path": "specs.md", "sha256": gm.sha(specfile)} for d in gm.enabled(self.model)]
        self.assertEqual([], gm.spec_errors(self.model, "preproduction", self.root))
        self.put("specs.md", "changed")
        self.assertTrue(gm.spec_errors(self.model, "preproduction", self.root))

    def test_native_container_check_rejects_web_mock(self):
        path = self.root / "web.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("index.html", "web mock")
        with self.assertRaises(ValueError):
            gm.native_artifact(path, "android")
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("AndroidManifest.xml", "synthetic fixture")
            archive.writestr("classes.dex", "synthetic fixture")
        gm.native_artifact(path, "android")

    def native_gate_fixture(self, stage):
        """All output is marked synthetic; tests no actual device capability."""
        typed = current_contract.V4ContractTests()
        typed.model, typed.root = self.model, self.root
        typed.complete_t_fixture()
        doc = self.put("spec.md", "Synthetic detailed design and independent review fixture")
        self.model["spec_refs"] = [{"domain": d, "path": "spec.md", "sha256": gm.sha(doc)} for d in sorted(gm.enabled(self.model))]
        video = self.root / "capture.webm"
        video.write_bytes(b"\x1aE\xdf\xa3" + b"synthetic video container fixture")
        samples = [{"path": "capture.webm", "sha256": gm.sha(video), "kind": "video"}]
        hashes = {}
        artifacts = {}
        for platform in ("android", "ios"):
            artifact = self.root / (platform + ".zip")
            with zipfile.ZipFile(artifact, "w") as archive:
                if platform == "android":
                    archive.writestr("AndroidManifest.xml", "synthetic fixture")
                    archive.writestr("classes.dex", "synthetic fixture")
                else:
                    archive.writestr("Payload/Fixture.app/Info.plist", "synthetic fixture")
            artifacts[platform] = artifact
            hashes[platform] = gm.sha(artifact)
        evidence = []
        for check in gm.requirements(self.model, stage):
            platforms = ("android", "ios") if check["modality"] in {"build", "device"} else ("android",)
            for platform in platforms:
                if check["modality"] == "document":
                    proof = doc
                else:
                    receipt = {"schema_version": "game-atelier-observation/1", "kind": check["modality"],
                               "platform": platform, "build_sha256": hashes[platform],
                               "scenario_ids": check["required_scenario_ids"], "samples": samples}
                    if check["modality"] == "build":
                        receipt.update(platform=platform, artifact_path=artifacts[platform].name,
                                       artifact_sha256=hashes[platform], toolchain="synthetic fixture")
                    if check["modality"] == "device":
                        receipt["device"] = {"platform": platform, "model": "synthetic fixture", "os": "fixture", "physical": True}
                    if check["modality"] == "player":
                        receipt.update(participant_count=1, method="synthetic fixture, not an actual human observation",
                                       outcomes=[{"scenario_id": scenario_id, "observation": "synthetic fixture outcome"}
                                                 for scenario_id in receipt["scenario_ids"]])
                    proof = self.put(check["id"] + "-" + platform + ".json", receipt)
                ev = self.evidence(check, proof)
                ev.update(build_sha256=hashes[platform], scenario_ids=check["required_scenario_ids"], platform=platform)
                ev["id"] += "-" + platform
                ev["scope_sha256"] = gm.scope_digest(self.model, check["domain"], check["id"])
                evidence.append(ev)
        self.model["evidence"] = evidence
        ops_spec = importlib.util.spec_from_file_location("native_fixture", ROOT / "tests/test_production_contract.py")
        ops_module = importlib.util.module_from_spec(ops_spec); ops_spec.loader.exec_module(ops_module)
        operations, _ = ops_module.native_operations()
        req = self.model["source_requirement_ids"][0]
        operations["recipes"][0]["requirement_ids"] = [req]
        operations["obligations"][0]["requirement_id"] = req
        base_assembly = operations["assemblies"][0]
        operations["assemblies"] = []
        for platform in ("android", "ios"):
            assembly = copy.deepcopy(base_assembly)
            assembly.update(id="ASM-native-" + platform, build_digest=hashes[platform], scenario="SCENARIO-BASE", evidence_refs=["FIXTURE-product.device-" + platform])
            assembly["native_scope"]["platform"] = platform
            operations["assemblies"].append(assembly)
        operations["obligations"][0]["witness_refs"] = [a["id"] for a in operations["assemblies"]]
        self.model["production"]["operations"] = operations
        # Assemblies are part of current proof scope; seal evidence after assembly binding.
        for ev in evidence:
            ev["model_sha256"] = gm.digest(self.model)
            ev["scope_sha256"] = gm.scope_digest(self.model, ev["domain"], ev["check_id"])

    def test_native_gate_links_observations_and_requires_both_platforms(self):
        self.native_gate_fixture("slice")
        result = gm.validate(self.model, self.root, "slice")
        self.assertTrue(result["stage_ready"], result)
        ev = next(e for e in self.model["evidence"] if e["check_id"] == "systems.runtime")
        receipt = gm.read_json(self.root / ev["proof_path"])
        receipt["build_sha256"] = "f" * 64
        proof = self.put(ev["proof_path"], receipt)
        ev["sha256"] = gm.sha(proof)
        result = gm.validate(self.model, self.root, "slice")
        self.assertFalse(result["stage_ready"])
        self.assertTrue(any("validated native build" in " ".join(x["errors"]) for x in result["evidence_errors"]))

    def test_release_requires_fresh_device_coverage_on_each_platform(self):
        self.native_gate_fixture("release")
        self.assertTrue(gm.validate(self.model, self.root, "release")["stage_ready"])
        self.model["evidence"] = [e for e in self.model["evidence"]
                                  if not (e["check_id"] == "product.release_device" and e["id"].endswith("-ios"))]
        result = gm.validate(self.model, self.root, "release")
        self.assertFalse(result["stage_ready"])
        self.assertIn("product.release_device:ios", result["missing_checks"])

    def test_art_only_scenario_cannot_close_input_runtime(self):
        scenario = copy.deepcopy(self.model["scenarios"][0])
        scenario["id"], scenario["domains"] = "ART-ONLY", ["art"]
        self.model["scenarios"].append(scenario)
        check = self.check_named("input.runtime")
        proof = self.observation("runtime")
        receipt = gm.read_json(proof)
        receipt["scenario_ids"] = ["ART-ONLY"]
        video = self.root / "motion.webm"
        video.write_bytes(b"\x1aE\xdf\xa3synthetic fixture")
        receipt["samples"] = [{"path": "motion.webm", "sha256": gm.sha(video), "kind": "video"}]
        proof = self.put("runtime.json", receipt)
        self.assertTrue(any("required due domain" in e for e in gm.proof_errors(self.model, self.evidence(check, proof), check, self.root)))

    def test_partial_due_scenario_coverage_cannot_close_runtime(self):
        self.native_gate_fixture("slice")
        ev = next(e for e in self.model["evidence"] if e["check_id"] == "systems.runtime")
        receipt = gm.read_json(self.root / ev["proof_path"])
        receipt["scenario_ids"] = ["SCENARIO-BASE"]
        proof = self.put(ev["proof_path"], receipt)
        ev["sha256"] = gm.sha(proof)
        result = gm.validate(self.model, self.root, "slice")
        self.assertFalse(result["stage_ready"])
        self.assertIn("systems.runtime:scenarios:SCENARIO-ADVANCED", result["missing_checks"])

    def test_ios_device_cannot_reference_android_build(self):
        self.native_gate_fixture("slice")
        ios = next(e for e in self.model["evidence"] if e["check_id"] == "product.device" and e["id"].endswith("-ios"))
        android = next(e for e in self.model["evidence"] if e["check_id"] == "product.native_build" and e["id"].endswith("-android"))
        receipt = gm.read_json(self.root / ios["proof_path"])
        receipt["build_sha256"] = gm.read_json(self.root / android["proof_path"])["build_sha256"]
        proof = self.put(ios["proof_path"], receipt)
        ios["sha256"] = gm.sha(proof)
        result = gm.validate(self.model, self.root, "slice")
        self.assertFalse(result["stage_ready"])
        self.assertIn("product.device:ios", result["missing_checks"])

    def test_later_scenario_can_be_scheduled_without_hiding_slice_representative(self):
        self.model["scenarios"][1]["due_stage"] = "beta"
        slice_check = self.check_named("systems.runtime", "slice")
        beta_check = self.check_named("systems.runtime", "beta")
        self.assertEqual(["SCENARIO-BASE"], slice_check["required_scenario_ids"])
        self.assertEqual(["SCENARIO-BASE", "SCENARIO-ADVANCED"], beta_check["required_scenario_ids"])

    def test_player_claimed_coverage_needs_outcome_for_each_scenario(self):
        self.native_gate_fixture("beta")
        ev = next(e for e in self.model["evidence"] if e["check_id"] == "systems.player")
        receipt = gm.read_json(self.root / ev["proof_path"])
        receipt["outcomes"] = receipt["outcomes"][:1]
        proof = self.put(ev["proof_path"], receipt)
        ev["sha256"] = gm.sha(proof)
        result = gm.validate(self.model, self.root, "beta")
        self.assertFalse(result["stage_ready"])
        self.assertTrue(any("outcome for every claimed scenario" in " ".join(e["errors"]) for e in result["evidence_errors"]))

    def test_trace_without_captured_media_cannot_close_motion_or_device(self):
        trace = self.put("trace.json", {"events": [{"t": 0, "state": "start"}, {"t": 1, "state": "end"}]})
        proof = self.observation("runtime")
        receipt = gm.read_json(proof)
        receipt["samples"] = [{"path": "trace.json", "sha256": gm.sha(trace), "kind": "trace"}]
        proof = self.put("runtime.json", receipt)
        check = self.check_named("input.runtime")
        self.assertTrue(gm.proof_errors(self.model, self.evidence(check, proof), check, self.root))
        image = self.root / "sample.png"
        receipt["samples"].append({"path": "sample.png", "sha256": gm.sha(image), "kind": "image"})
        proof = self.put("runtime.json", receipt)
        self.assertEqual([], gm.proof_errors(self.model, self.evidence(check, proof), check, self.root))

    def test_impact_uses_rule_owner_and_only_active_domains(self):
        result = gm.impact(self.model, "RULE-A")
        self.assertIn("systems", result["direct_domains"])
        self.assertIn("commerce", result["review_domains"])
        self.assertNotIn("actors", result["review_domains"])
        self.assertTrue(result["requires_semantic_triage"])
        self.assertTrue(gm.impact(self.model, "missing")["errors"])

    def test_portfolio_keeps_projection_and_tracking_separate(self):
        models = [gm.read_json(p) for p in (ROOT / "assets/examples").glob("model-*.json")]
        result = gm.portfolio({"candidates": models})
        self.assertEqual([], result["errors"])
        self.assertIn("projection", result["distributions"])
        self.assertIn("tracking", result["distributions"])
        self.assertFalse(result["semantic_diversity_certified"])
        duplicate = copy.deepcopy(models[0])
        duplicate["id"] += "-neighbor"
        result = gm.portfolio({"candidates": [models[0], duplicate]})
        self.assertEqual("needs_semantic_neighbor_review", result["neighbors"][0]["status"])

    def test_duplicate_json_keys_rejected(self):
        path = self.put("duplicate.json", '{"id":"a","id":"b"}')
        with self.assertRaises(ValueError):
            gm.read_json(path)

    def test_schema_is_current_and_cli_authoring_mode_never_stage_ready(self):
        self.assertEqual(gm.schema(), gm.read_json(ROOT / "assets/game-model.schema.json"))
        path = ROOT / "assets/examples/model-no-enemy.json"
        command = [sys.executable, str(ROOT / "scripts/game_model.py"), "validate", str(path), "--design-only", "--json"]
        run = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        self.assertFalse(json.loads(run.stdout)["stage_ready"])
        run = subprocess.run(command[:-1] + ["--stage", "slice"], capture_output=True, text=True)
        self.assertEqual(2, run.returncode)  # conflicting modes cannot bypass a gate


if __name__ == "__main__":
    unittest.main()
