"""Bounded discovery cases use fake future skills, with no external effects."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "discover_specialists.py"
spec = importlib.util.spec_from_file_location("discover_specialists", SCRIPT)
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def skill(self, folder="future", name="future-spectrum-lab", body="", version="7.4.2"):
        path = self.root / folder / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {name}\ndescription: Analyze spectroscopy data\n---\n# Spectrum Lab {version}\n{body}\n")
        return path

    def scan(self, metadata=()):
        return discovery.inventory("codex", [self.root], metadata)

    def analysis(self, candidate, covered=("R1",), fit="usable"):
        return {"candidate_id": candidate["id"], "source_sha256": candidate["source"].get("sha256"),
                "requirement_ids": list(covered), "fit": fit,
                **{key: "Source analysis: " + key + " matches bounded spectroscopy task" for key in discovery.FIT_FIELDS}}

    def decision(self, candidate, mode="reuse"):
        return {"decision": mode, "requirement_ids": ["R1"], "selected": [candidate["id"]],
                "reason": "Reuse actual spectroscopy method rather than manufacture another engine",
                "search_scope": "Current host metadata and approved spectroscopy skill source",
                "authority_ref": "project/authority#planning", "analyses": [self.analysis(candidate)]}

    def test_novel_future_specialist_without_card_is_retained_and_reusable_after_analysis(self):
        self.skill()
        report = self.scan()
        row = report["candidates"][0]
        self.assertEqual(row["name"], "future-spectrum-lab")
        self.assertEqual(row["source"]["version"], "7.4.2")
        self.assertIsNone(row["capability_card"])
        self.assertTrue(row["source_analysis_required"])
        self.assertEqual(row["selectors"], {"work": "@future-spectrum-lab", "codex": "$future-spectrum-lab"})
        result = discovery.validate_decision(report, self.decision(row))
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["grants_created"], [])
        self.assertFalse(result["execution_performed"])

    def test_missing_counterpart_does_not_probe_or_claim_other_host_availability(self):
        self.skill()
        report = self.scan([{"entries": [{"name": "future-spectrum-lab", "host": "work",
                           "source": "/unavailable/other-machine/SKILL.md", "installed": True}]}])
        other = next(r for r in report["candidates"] if r["host"] == "work")
        self.assertEqual(other["availability_status"], "unverified")
        self.assertFalse(other["availability"]["installed"])
        self.assertFalse(other["selectable_after_analysis"])

    def test_work_reader_snapshot_preserves_locator_without_inventing_installation(self):
        path = self.skill()
        metadata = {"entries": [{"host": "work", "name": "future-spectrum-lab", "source": "skill://current/future-spectrum-lab/SKILL.md",
                                  "source_snapshot": str(path), "listed": True}]}
        report = discovery.inventory("work", catalogs=[metadata], snapshot_roots=[self.root])
        row = report["candidates"][0]
        self.assertTrue(row["availability"]["listed"])
        self.assertTrue(row["availability"]["source_checked"])
        self.assertFalse(row["availability"]["installed"])
        self.assertEqual(row["source"]["reference"], metadata["entries"][0]["source"])
        self.assertTrue(discovery.validate_decision(report, self.decision(row))["valid"])

    def counterpart_case(self, status=None):
        path = self.skill("work-source-snapshot")
        reference = "skill://work/future-spectrum-lab/SKILL.md"
        report = discovery.inventory("codex", catalogs=[{"entries": [{"host": "work", "name": "future-spectrum-lab", "source": reference}]}],
                                     snapshot_roots=[self.root])
        row = report["candidates"][0]
        decision = {"decision": "create_gap", "reason": "No matching current-host engine found", "search_scope": "Bounded domain shortlist",
                    "authority_ref": "project/authority#planning", "requirement_ids": ["R1"], "gap_requirement_ids": ["R1"],
                    "selected": [], "analyses": []}
        if status:
            decision["counterpart_assessments"] = [{"candidate_id": row["id"], "status": status, "reason": "Actual source and task applicability reviewed",
                "requirement_ids": ["R1"], "need_fit": "Source-backed comparison with the stated requirement",
                "source_review": {"path": str(path), "sha256": discovery.digest(path.read_bytes()), "host": "work", "reference": reference}}]
        return report, decision, path

    def test_known_work_only_candidate_does_not_allow_false_creation_gap(self):
        report, decision, _ = self.counterpart_case()
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        decision["counterpart_assessments"] = [{"candidate_id": report["candidates"][0]["id"], "status": "unknown", "reason": "Source not yet read"}]
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_source_backed_other_host_bridge_does_not_grant_duplicate_engine(self):
        report, decision, _ = self.counterpart_case("bridge")
        decision["counterpart_assessments"][0]["bridge_ref"] = "project/handoffs/work-spectrum-stage"
        result = discovery.validate_decision(report, decision)
        self.assertFalse(result["valid"])
        self.assertEqual(result["grants_created"], [])
        self.assertFalse(report["candidates"][0]["availability"]["installed"])
        self.assertFalse(report["candidates"][0]["availability"]["source_checked"])

    def test_actually_irrelevant_other_host_source_does_not_block_unrelated_domain(self):
        report, decision, _ = self.counterpart_case("irrelevant")
        decision["counterpart_assessments"][0]["need_fit"] = "Read source only covers laboratory spectra; R1 is warehouse picking routes"
        result = discovery.validate_decision(report, decision)
        self.assertTrue(result["valid"], result)
        self.assertEqual(report["candidates"][0]["availability_status"], "unverified")

    def test_other_host_exclusion_requires_actual_current_source_review(self):
        report, decision, path = self.counterpart_case("incompatible")
        self.assertTrue(discovery.validate_decision(report, decision)["valid"])
        path.write_text(path.read_text() + "Changed scope\n")
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        del decision["counterpart_assessments"][0]["source_review"]
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_partial_other_host_assessment_does_not_hide_other_required_capabilities(self):
        report, decision, _ = self.counterpart_case("irrelevant")
        decision.update(requirement_ids=["R1", "R2"], gap_requirement_ids=["R1", "R2"])
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_archived_source_is_not_an_installed_candidate(self):
        self.skill("uninstalled/old")
        self.skill("current")
        report = self.scan()
        archived = next(r for r in report["candidates"] if r["status"] == "archived")
        current = next(r for r in report["candidates"] if r["status"] == "active")
        self.assertFalse(archived["selectable_after_analysis"])
        self.assertTrue(current["selectable_after_analysis"])

    def test_same_name_two_active_sources_is_ambiguous_even_with_later_version(self):
        self.skill("one", version="1.0.0")
        self.skill("two", version="9.0.0")
        report = self.scan()
        for row in report["candidates"]:
            self.assertIn("ambiguous_installed_identity", row["issues"])
            self.assertFalse(discovery.validate_decision(report, self.decision(row))["valid"])

    def test_explicit_actual_host_binding_resolves_duplicate_without_hiding_sources(self):
        self.skill("plugin", version="1.0.0")
        self.skill("personal", version="9.0.0")
        report = self.scan()
        row = report["candidates"][0]
        decision = self.decision(row)
        decision["identity_resolutions"] = [{"candidate_id": row["id"], "binding_ref": "current-tool-listing#resolved-package",
                                             "reason": "Current host package binding resolves to this exact source"}]
        result = discovery.validate_decision(report, decision)
        self.assertTrue(result["valid"], result)
        self.assertEqual(len(report["candidates"]), 2)
        self.assertTrue(all(r["status"] == "active" for r in report["candidates"]))
        decision["identity_resolutions"][0]["binding_ref"] = ""
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_expected_old_hash_is_not_silently_replaced_by_current_source(self):
        path = self.skill()
        report = self.scan([{"entries": [{"host": "codex", "name": "future-spectrum-lab",
                           "source": str(path), "sha256": "0" * 64, "installed": True}]}])
        self.assertEqual(len(report["candidates"]), 1)
        row = report["candidates"][0]
        self.assertIn("stale_metadata_hash", row["issues"])
        self.assertFalse(discovery.validate_decision(report, self.decision(row))["valid"])

    def test_source_changed_after_analysis_requires_new_read_and_decision(self):
        path = self.skill()
        report = self.scan()
        decision = self.decision(report["candidates"][0])
        path.write_text(path.read_text() + "Changed calibration rule\n")
        result = discovery.validate_decision(report, decision)
        self.assertFalse(result["valid"])
        self.assertTrue(any("source changed" in e for e in result["errors"]))

    def test_consulted_source_dependency_change_invalidates_analysis(self):
        path = self.skill()
        rules = path.parent / "rules.md"
        rules.write_text("Known spectroscopy calibration rule")
        report = self.scan()
        decision = self.decision(report["candidates"][0])
        decision["analyses"][0]["source_files"] = [{"path": str(rules), "sha256": discovery.digest(rules.read_bytes())}]
        self.assertTrue(discovery.validate_decision(report, decision)["valid"])
        rules.write_text("Changed calibration rule")
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_body_name_and_stale_analysis_pin_cannot_select_a_different_skill(self):
        self.skill(body="```yaml\nname: made-up-current-skill\n```")
        report = self.scan()
        row = report["candidates"][0]
        self.assertEqual(row["name"], "future-spectrum-lab")
        decision = self.decision(row)
        decision["analyses"][0]["source_sha256"] = "0" * 64
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_missing_source_fit_dimensions_are_not_filled_from_capability_match(self):
        self.skill()
        report = self.scan()
        decision = self.decision(report["candidates"][0])
        del decision["analyses"][0]["rights"]
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        decision["analyses"][0]["rights"] = "No current permission for external publication"
        decision["analyses"][0]["fit"] = "incompatible"
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_composition_requires_complete_coverage_and_interface_contract(self):
        self.skill("calibrate", "future-calibrate")
        self.skill("classify", "future-classify")
        report = self.scan()
        a, b = report["candidates"]
        decision = self.decision(a, "compose")
        decision.update(requirement_ids=["R1", "R2"], selected=[a["id"], b["id"]],
                        analyses=[self.analysis(a, ["R1"]), self.analysis(b, ["R2"])])
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        decision["interface_contract_ref"] = "project/contracts/spectrum-flow-v1"
        self.assertTrue(discovery.validate_decision(report, decision)["valid"])

    def test_extend_and_create_gap_cannot_hide_reusable_or_unreviewed_source(self):
        self.skill()
        report = self.scan()
        row = report["candidates"][0]
        decision = self.decision(row, "extend")
        decision.update(requirement_ids=["R1", "R2"], gap_requirement_ids=["R2"])
        self.assertTrue(discovery.validate_decision(report, decision)["valid"])
        decision.update(decision="create_gap", selected=[], gap_requirement_ids=["R1", "R2"])
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        decision["analyses"][0]["fit"] = "unknown"
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])
        decision["analyses"][0]["fit"] = "incompatible"
        self.assertTrue(discovery.validate_decision(report, decision)["valid"])
        decision["analyses"] = []
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_scope_exclusion_prevents_source_read(self):
        path = self.skill()
        path.write_text("not parseable frontmatter")
        report = discovery.inventory("codex", [self.root], [], [path])
        self.assertEqual(report["candidates"], [])
        self.assertEqual(report["diagnostics"], [])

    def test_unreadable_identity_does_not_prove_a_creation_gap(self):
        path = self.skill()
        path.write_text("Missing actual identity")
        report = self.scan()
        decision = {"decision": "create_gap", "reason": "Need spectroscopy", "search_scope": "Approved source",
                    "authority_ref": "project/authority", "requirement_ids": ["R1"], "gap_requirement_ids": ["R1"],
                    "selected": [], "analyses": []}
        self.assertFalse(discovery.validate_decision(report, decision)["valid"])

    def test_missing_approved_root_is_not_reported_as_a_successful_empty_search(self):
        with self.assertRaises(ValueError):
            discovery.inventory("codex", [self.root / "does-not-exist"])

    def test_source_outside_approved_roots_is_not_read(self):
        path = self.skill()
        report = discovery.inventory("codex", [], [{"entries": [{"name": "future-spectrum-lab",
                           "source": str(path), "installed": True}]}])
        row = report["candidates"][0]
        self.assertFalse(row["availability"]["source_checked"])
        self.assertFalse(row["selectable_after_analysis"])


if __name__ == "__main__":
    unittest.main()
