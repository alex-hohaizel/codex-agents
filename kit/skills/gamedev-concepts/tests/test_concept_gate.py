"""Behavioral regression tests for the pre-illustration passport gate.

Fixtures are synthetic structural examples, never actual semantic approvals.
Run: python3 -m unittest discover -s tests -p 'test_concept_gate.py' -v
"""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("concept_gate", SKILL / "scripts" / "concept_gate.py")
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
SCHEMA = json.loads((SKILL / "assets" / "systemic-passport.schema.json").read_text(encoding="utf-8"))


def fixture_passport():
    def rule(condition, action, change, cost, failure, recovery):
        return {"condition": condition, "action_or_event": action, "state_change": change,
                "cost_or_limit": cost, "counterplay_or_failure": failure, "recovery": recovery}

    def system(ident, family, name, state, choices, rules, cue):
        return {"id": ident, "family": family, "name": name, "state_variables": state,
                "player_choices": choices, "rules": rules, "reader_cues": [cue]}

    def edge(ident, origin, target, condition, state, decision, removal):
        return {"id": ident, "from_system": origin, "to_system": target, "condition": condition,
                "changed_state": state, "changed_player_decision": decision, "without_this_edge": removal}

    def trace(ident, context, inputs, refs, changes, decisions, contrast):
        return {"id": ident, "initial_context": context, "player_goal": "Reach the stranded worker before the beam collapses",
                "steps": [{"input": inp, "mechanic_refs": ref, "state_change": change,
                           "readable_feedback": "Floor arrows and a visible hose stream show the result", "next_decision": decision}
                          for inp, ref, change, decision in zip(inputs, refs, changes, decisions)],
                "ending_and_persistence": "Worker returns to the depot and opens a new equipment route",
                "mistake_and_recovery": "Release the hose before turning; retreat to the marked cool tile if overheated",
                "contrast_trace_ref": contrast, "why_the_best_action_differs": "The ventilation state changes whether cooling or sealing the door is safer"}

    def milestone(goal, capability, decision, reinterpretation, discovery, next_goal):
        return {"player_goal": goal, "introduced_capability_or_world_state": capability,
                "new_decision": decision, "familiar_action_reinterpreted": reinterpretation,
                "how_discovered": discovery, "next_visible_goal": next_goal}

    p = {
        "passport_format": "gameatelier.systemic-passport.1", "concept_id": "FIXTURE-RESCUE-1",
        "revision": "1", "title": "Depot Rescue — synthetic structural fixture",
        "scope": {"track": "fixture", "scale": "S", "genre": "Rescue action simulation",
                  "spatial_limit": "One changing warehouse floor", "experience_span": "Learn linked heat, hose and door systems over a rescue campaign"},
        "source_requirement_refs": ["TEST-SYSTEMS", "TEST-UX", "TEST-COMMERCE", "TEST-FIDELITY"],
        "player_fantasy": {"role": "A compact rescue robot", "immediate_goal": "Reach the worker beyond the heated gate",
                           "whole_game_goal": "Restore the depot while keeping its workers safe",
                           "why_the_activity_is_desirable": "A deliberate route changes both danger and rescue opportunities",
                           "understandable_world_rule": "Opening a hot door feeds oxygen into its room",
                           "later_discovery_reframes_the_game": "Steam can turn a familiar blocked corridor into a temporary shield"},
        "systems": [
            system("drive", "player", "Movement and load", ["traction", "carried worker"], ["brace", "carry", "retreat"],
                   [rule("robot is loaded", "turn sharply", "traction falls", "turn radius grows", "slide toward heat", "brace on a cool tile")], "Wheel sparks show lost traction"),
            system("hose", "tool_or_ability", "Hose routing", ["water", "nozzle angle"], ["cool a beam", "push debris"],
                   [rule("water remains", "hold and aim nozzle", "cool or push target", "water is consumed", "stream misses a moving target", "release and re-aim")], "A visible cone previews the stream"),
            system("heat", "environment_or_world", "Fire and steam", ["room heat", "steam cloud"], ["cool before entering", "route around steam"],
                   [rule("hot surface meets water", "cool surface", "steam obscures the route", "water used and visibility lost", "beam cracks behind cloud", "follow floor markers")], "Orange beams and white steam have distinct silhouettes"),
            system("doors", "environment_or_world", "Ventilation network", ["gate state", "airflow"], ["seal a door", "open a vent"],
                   [rule("door opens onto a hot room", "open gate", "airflow raises heat", "safe path may shrink", "fire spreads across the floor", "close the gate from a marked lever")], "Wind ribbons preview incoming airflow"),
            system("workers", "pressure_or_agent", "Worker trust", ["panic", "route confidence"], ["signal a safe route", "carry a panicked worker"],
                   [rule("route is clearly cool", "signal worker", "worker follows without loading the robot", "requires line of sight", "steam breaks confidence", "return to the visible rendezvous tile")], "A stance and route line show confidence"),
        ],
        "causal_interactions": [
            edge("hose_heat", "hose", "heat", "water contacts hot beam", "heat becomes steam", "cool before or after sealing ventilation", "watering would be a generic damage action"),
            edge("heat_drive", "heat", "drive", "robot crosses hot floor", "traction deteriorates", "brace before carrying a worker", "route temperature would not affect movement"),
            edge("door_heat", "doors", "heat", "hot-room gate is opened", "oxygen raises room heat", "seal gate before cooling", "doors would only be spatial locks"),
            edge("drive_hose", "drive", "hose", "robot is braced", "stream aim stabilizes", "trade mobility for precise cooling", "movement would not change tool use"),
            edge("heat_workers", "heat", "workers", "steam blocks the worker's route", "panic rises", "clear vision or carry the worker", "worker behavior would not respond to hazards"),
            edge("workers_drive", "workers", "drive", "worker must be carried", "turn radius grows", "choose a wide cooled route", "rescue would not affect traversal"),
        ],
        "causal_traces": [
            trace("trace_vented", "Gate is open and the beam is already steaming", ["pull the gate lever", "brace and aim the nozzle"],
                  [["doors", "door_heat"], ["hose_heat", "drive_hose"]], ["airflow stops feeding heat", "beam cools without a spreading fire"],
                  ["seal first rather than waste water", "signal the worker along the now-visible route"], "trace_sealed"),
            trace("trace_sealed", "Gate is shut and a worker is already coughing in the room", ["aim through a small vent", "pick up and carry the worker"],
                  [["hose", "hose_heat"], ["workers_drive", "heat_drive"]], ["a narrow cool path forms", "robot load increases"],
                  ["cool first to make opening the gate safe", "brace around the wider turn instead of signalling"], "trace_vented"),
        ],
        "contextual_resources": [
            {"id": "water", "system_ref": "hose", "name": "Tank water", "kind": "material", "sources": ["refill valves on cooled floors"],
             "uses_and_sinks": ["cool beams", "push debris away from a worker"], "action_or_world_effect": "Water lowers heat but makes steam",
             "competing_use_tradeoff": "Cooling a beam leaves less water for clearing the exit", "depletion_or_accumulation_risk": "An empty tank forces a longer refill route",
             "recovery": "Reach a cooled refill valve", "player_readable_cue": "Transparent tank and shorter stream", "persistence_or_reset": "Refill between rescues; no paid refill wall",
             "interaction_refs": ["hose_heat"]},
            {"id": "traction", "system_ref": "drive", "name": "Wheel grip", "kind": "contextual_state", "sources": ["brace on a cool rough floor"],
             "uses_and_sinks": ["sharp loaded turns", "bracing against hose recoil"], "action_or_world_effect": "Low grip turns a short path into a slide risk",
             "competing_use_tradeoff": "A stable firing position delays the rescue", "depletion_or_accumulation_risk": "Hot smooth tiles remove safe turning margin",
             "recovery": "Release the nozzle and brace on a marked rough tile", "player_readable_cue": "Wheel sparks and a widening turn preview", "persistence_or_reset": "Local floor state persists within the rescue",
             "interaction_refs": ["heat_drive", "drive_hose"]},
        ],
        "ux": {
            "orientation_and_camera": "Landscape high orthographic view; full route and two thumb zones remain visible",
            "stable_input_grammar": [
                {"input": "left drag", "meaning": "steer robot", "precondition": "robot is not in a pause menu", "preview_cue": "turn arc shows loaded radius",
                 "confirmation": "wheels turn and a path line updates", "ambiguity_resolution": "left zone never aims the hose", "cancel_or_recovery": "release to brake"},
                {"input": "right hold and drag", "meaning": "aim and spray", "precondition": "nozzle is raised and water remains", "preview_cue": "aim cone points before water starts",
                 "confirmation": "stream hits the outlined surface", "ambiguity_resolution": "tool mode is visible before touching; lever requires the separate context tap", "cancel_or_recovery": "release stops water immediately"},
            ],
            "peak_episode": {"situation": "Carry a worker across a steaming bend while controlling a short spray",
                             "simultaneous_player_demands": "Steer left and aim right; gate is resolved before entry",
                             "thumb_or_pointer_load": "At most two contacts; no third-finger modifier",
                             "occlusion_and_targeting": "Thumb zones sit below the rescue route and cone projects past the thumb",
                             "why_it_is_comfortable": "Braking is a release, not an extra button",
                             "next_input_if_interrupted": "Resume paused with a visible route preview before movement begins"},
            "screen_states": {"first_play": "Only movement zone and a reachable cooled valve are highlighted", "normal": "Tank and gate airflow show near the relevant objects",
                              "peak": "Worker route, turn arc and heat silhouette remain visible without opening inventory"},
            "discovery_and_affordances": "A safe first gate shows the wind ribbon before the heated version appears",
            "muted_and_no_haptic_information": "Visible beam cracks and route lines retain every warning",
            "controls_to_visible_hud_mapping": "Two bottom zones match left drag and right hold; contextual lever shows its own reachable label",
        },
        "evolution": {
            "early": milestone("Save one worker", "Direct water jet", "Spend water on heat or debris", "A door is a simple obstacle", "A small guided rescue", "Reach the sealed wing"),
            "middle": milestone("Open the sealed wing", "Remote vent control", "Change airflow before committing to a room", "Opening a familiar gate can now feed fire", "A visible wind ribbon warns before opening", "Rescue workers across linked rooms"),
            "late": milestone("Restore the depot", "Steam shielding and paired worker routes", "Use a temporary steam screen while another route stays readable", "Cooling can deliberately create cover rather than only remove danger", "A worker demonstrates a safe steam corridor", "Choose a self-directed no-loss campaign route"),
            "progression_links": [{"from": "early", "to": "middle", "requires": "Rescue the vent engineer"}, {"from": "middle", "to": "late", "requires": "Restore the paired room controllers"}],
            "persistent_and_reset_states": "Rescued workers and restored controllers persist; tank and local heat reset for the next rescue",
            "self_directed_goal_after_initial_mastery": "Restore every wing without sacrificing its original machinery",
        },
        "replay_grammar": {
            "authored_families": ["vent-linked rooms", "movable beam structures", "worker confidence patterns"],
            "combination_axes": ["airflow state", "loaded turn space", "worker visibility"],
            "compatibility_and_fairness_constraints": ["A refill remains reachable before the final mandatory cooling step", "No worker begins beyond both blocked visibility and an impossible carry turn"],
            "concrete_contexts": [
                {"id": "open_vent", "grammar_axes": ["airflow state"], "concrete_situation": "Open vent feeds a hot narrow corner", "preferred_tactic_and_reason": "Seal before spraying to conserve water",
                 "other_context_ref": "sealed_worker", "why_that_tactic_changes": "There is time to operate the gate before the worker enters danger"},
                {"id": "sealed_worker", "grammar_axes": ["worker visibility"], "concrete_situation": "Worker is trapped behind a sealed hot gate", "preferred_tactic_and_reason": "Cool through the slit before opening the gate",
                 "other_context_ref": "open_vent", "why_that_tactic_changes": "Sealing again would not remove the worker's immediate heat risk"},
            ],
            "same_policy_counterexample": "Always opening first increases heat in the vented corner; always sealing first does not rescue the trapped worker",
            "finite_launch_capacity_and_source_cost": "A finite set of room modules is authored once and combined under the refill and turning constraints",
            "long_arc_without_manual_weekly_events": "Restored workers expose new route constraints and optional preservation objectives",
        },
        "alternate_experience_commerce": {
            "model_hypothesis": "Optional sidegrade equipment pack; synthetic design hypothesis only", "exact_optional_offer": "Foam nozzle and its training rescues",
            "desire_from_core_activity": "The player wants to hold heat back while carrying a worker", "trial": "Free loan in the training wing", "natural_choice_moment": "After rescuing the worker who demonstrates foam",
            "same_encounter_comparison": {
                "shared_encounter": "A vented beam blocks the worker's exit", "baseline_input_and_decisions": "Seal the gate, then brace and direct the water jet",
                "alternate_input_and_decisions": "Sweep a foam barrier, then carry the worker while the barrier holds",
                "different_feeling_or_rhythm": "Direct continuous correction becomes advance preparation followed by committed movement",
                "alternate_strength": "Foam holds a cooled boundary briefly after the nozzle stops",
                "alternate_limit_or_tradeoff": "Foam cannot push debris and takes longer to clear a blocked turn",
                "both_viable_outcomes": "Water clears the turn and foam protects the carry; neither removes the rescue route requirement",
            },
            "repeated_use_and_next_goal": "Replay preservation rescues with a different preparation rhythm",
            "complete_free_experience": "Water equipment completes every main rescue and restoration goal",
            "access_model_and_earned_comparables": "A free vent kit supplies another planning-oriented route without copying foam",
            "no_offer_control": "Campaign retains the water and vent progression when no offer is displayed",
            "cumulative_portfolio_counterexample": "Instant switching from foam to water would remove the foam debris weakness",
            "mitigation_or_unresolved_gap": "One nozzle is selected at the depot; in-rescue free swapping is unavailable and requires balance testing",
            "production_and_recurring_cost_route": "Reuse existing heat states with a finite foam decal and nozzle animation set; no required live event service",
            "unselected_commercial_decisions": ["regional price", "store model"],
        },
        "visual_production": {
            "profile_ref": "PROFILE-2D", "capability_evidence_refs": ["CAP-LOCAL-TOOLS"],
            "feasible_target_description": "Layered painted 2D depot with cutout robot and bounded particle steam",
            "camera_scale_density_ui": "High orthographic landscape; six readable interactables, two bottom thumb zones and no cinematic depth of field",
            "reference_constraints": ["No simulated cloth or 3D water volume", "Keep the complete playable bend visible"],
            "element_map": [{"element_id": "robot", "visible_role_and_state": "Loaded robot bracing before the turn", "representation": "Painted cutout sprite",
                             "editable_source_route": "Layered source separates wheels, nozzle, torso and carried worker", "runtime_assembly": "Sprite nodes with authored pivots and collision shapes",
                             "tool_profile_ref": "PROFILE-2D", "known_unknown_or_blocked": "planned", "risk_and_due_proof": "Loaded turn and hose contact need a representative native slice"}],
            "candidate_specific_risks": ["Steam must not hide the worker route"], "what_was_actually_verified": "Synthetic fixture tests only validate linked declarations",
            "what_remains_unproved_and_due_stage": "Native import, touch feel and device performance require later actual evidence",
            "reference_freeze_and_parity_rule": "Freeze selected source bytes, camera and silhouettes; compare the native slice in the same scene state",
            "source_rights_and_extra_cost": "Original sources are planned; no paid external asset purchase is assumed",
        },
        "counterfactual_review": {
            "remove_decorative_systems_test": "Removing airflow makes sealing the gate irrelevant to heat decisions", "strongest_simple_policy_test": "Always spray fails when water is needed for debris",
            "early_late_decision_difference": "The first rescue avoids steam; a later rescue uses it as temporary cover",
            "familiarity_and_player_comprehension": "A rescue robot, fire, doors and a visible hose explain the fantasy before its systemic combinations",
            "strongest_objection": "Players may misread beneficial steam as a universal hazard", "next_discriminating_test": "Observe whether a new player predicts the safe steam route without text",
        },
        "review_refs": ["REVIEW-FIXTURE"], "user_acceptance_ref": None, "status": "draft",
    }
    return p


def fixture_profiles():
    return {"profiles": [{"id": "PROFILE-2D", "capability_evidence_refs": ["CAP-LOCAL-TOOLS"]}],
            "capability_evidence": [{"id": "CAP-LOCAL-TOOLS", "kind": "synthetic unit-test record, not production evidence"}]}


def fixture_reviews(passport):
    return {"items": [{"id": "REVIEW-FIXTURE", "reviewer_id": "fixture-independent-observer",
                       "author_ids": ["fixture-author"], "status": "pass", "scope": GATE.REVIEW_SCOPE,
                       "passport_hashes": {passport["concept_id"]: GATE.canonical_passport_sha256(passport)},
                       "checked_requirement_refs": passport["source_requirement_refs"],
                       "limitations": "Synthetic unit-test receipt only; no actual gameplay, native or commercial validation."}]}


class ConceptGateTests(unittest.TestCase):
    def setUp(self):
        self.passport = fixture_passport()

    def check(self, passport=None, **kwargs):
        return GATE.validate_passports(passport or self.passport, SCHEMA, **kwargs)

    def codes(self, result):
        return {p["code"] for row in result["candidates"] for p in row["issues"]} | {p["code"] for p in result["registry_issues"]}

    def test_complete_fixture_is_structural_not_quality_certificate(self):
        result = self.check()
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["status"], "structurally_valid_review_pending")
        self.assertFalse(result["quality_certified"])
        self.assertEqual(result["candidates"][0]["semantic_review_receipts_verified"], [])

    def test_current_independent_receipt_can_be_checked_without_mutating_status(self):
        result = self.check(profiles=fixture_profiles(), reviews=fixture_reviews(self.passport), for_illustration=True)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["status"], "pre_illustration_receipts_valid")
        self.assertEqual(self.passport["status"], "draft")
        self.assertIsNone(self.passport["user_acceptance_ref"])

    def test_actual_r5_shape_cannot_bypass_passport(self):
        old = {"id": "R5-G-S-A1", "title": "Клінч над тріщиною", "rules": ["push", "tilt", "fall"],
               "controls": "Two thumbs", "commerce": {"offer": "Cosmetic club kit"}}
        result = self.check(old)
        self.assertFalse(result["valid"])
        self.assertIn("required", self.codes(result))

    def test_broken_causal_reference_and_isolated_system_are_rejected(self):
        p = copy.deepcopy(self.passport)
        p["causal_interactions"][0]["to_system"] = "missing"
        self.assertIn("unresolved_system", self.codes(self.check(p)))
        p = copy.deepcopy(self.passport)
        p["systems"].append(dict(p["systems"][0], id="unconnected", name="Unconnected storage"))
        self.assertIn("disconnected_system", self.codes(self.check(p)))

    def test_resources_cannot_be_only_currencies_or_link_to_unrelated_edges(self):
        p = copy.deepcopy(self.passport)
        for r in p["contextual_resources"]:
            r["kind"] = "economy"
        self.assertIn("only_generic_resources", self.codes(self.check(p)))
        p = copy.deepcopy(self.passport)
        p["contextual_resources"][0]["interaction_refs"] = ["door_heat"]
        self.assertIn("unbound_resource", self.codes(self.check(p)))

    def test_progression_dependencies_reject_cycles_and_undefined_milestones(self):
        p = copy.deepcopy(self.passport)
        p["evolution"]["progression_links"].append({"from": "late", "to": "early", "requires": "Impossible circular unlock"})
        self.assertIn("progression_cycle", self.codes(self.check(p)))
        p["evolution"]["progression_links"][0]["from"] = "undefined"
        self.assertIn("enum", self.codes(self.check(p)))

    def test_copy_variation_is_not_accepted_as_contrast(self):
        p = copy.deepcopy(self.passport)
        p["causal_traces"][1] = dict(p["causal_traces"][0], id="trace_sealed", contrast_trace_ref="trace_vented")
        self.assertIn("copied_trace", self.codes(self.check(p)))
        p = copy.deepcopy(self.passport)
        p["evolution"]["late"] = copy.deepcopy(p["evolution"]["early"])
        self.assertIn("copied_evolution", self.codes(self.check(p)))

    def test_renaming_a_candidate_does_not_make_an_exact_duplicate_new(self):
        clone = copy.deepcopy(self.passport)
        clone["concept_id"] = "FIXTURE-RESCUE-2"
        clone["title"] = "Different title on the same game"
        result = GATE.validate_passports([self.passport, clone], SCHEMA)
        self.assertIn("copied_candidate", self.codes(result))

    def test_repair_status_cannot_progress_even_with_a_matching_receipt(self):
        self.passport["status"] = "repair"
        result = self.check(profiles=fixture_profiles(), reviews=fixture_reviews(self.passport), for_illustration=True)
        self.assertIn("repair_pending", self.codes(result))

    def test_cosmetic_clone_or_explicitly_dominant_alternate_is_rejected(self):
        p = copy.deepcopy(self.passport)
        comparison = p["alternate_experience_commerce"]["same_encounter_comparison"]
        comparison["alternate_input_and_decisions"] = comparison["baseline_input_and_decisions"]
        self.assertIn("identical_alternate", self.codes(self.check(p)))
        comparison["alternate_input_and_decisions"] = "Do every baseline action faster with no lost ability"
        comparison["alternate_limit_or_tradeoff"] = "none"
        self.assertIn("missing_tradeoff", self.codes(self.check(p)))
        del p["alternate_experience_commerce"]["cumulative_portfolio_counterexample"]
        self.assertIn("required", self.codes(self.check(p)))

    def test_unbound_camera_hud_and_wrong_profile_are_rejected(self):
        p = copy.deepcopy(self.passport)
        p["ux"]["controls_to_visible_hud_mapping"] = ""
        self.assertIn("empty", self.codes(self.check(p)))
        p = copy.deepcopy(self.passport)
        p["visual_production"]["element_map"][0]["tool_profile_ref"] = "UNRELATED-3D"
        self.assertIn("profile_mismatch", self.codes(self.check(p)))
        profiles = fixture_profiles()
        profiles["profiles"][0]["id"] = "OTHER"
        self.assertIn("unresolved_profile", self.codes(self.check(profiles=profiles)))

    def test_stale_self_or_incomplete_review_cannot_release_image_gate(self):
        reviews = fixture_reviews(self.passport)
        self.passport["player_fantasy"]["immediate_goal"] += " and save another worker"
        self.assertIn("stale_review", self.codes(self.check(profiles=fixture_profiles(), reviews=reviews, for_illustration=True)))
        reviews = fixture_reviews(self.passport)
        reviews["items"][0]["reviewer_id"] = "fixture-author"
        self.assertIn("review_independence", self.codes(self.check(profiles=fixture_profiles(), reviews=reviews, for_illustration=True)))
        reviews = fixture_reviews(self.passport)
        reviews["items"][0]["checked_requirement_refs"] = ["TEST-UX"]
        self.assertIn("review_coverage", self.codes(self.check(profiles=fixture_profiles(), reviews=reviews, for_illustration=True)))

    def test_readable_card_links_preserve_canonical_concept_id(self):
        cards = [{"concept_id": self.passport["concept_id"], "systemic_passport_ref": self.passport["concept_id"]}]
        self.assertTrue(self.check(cards=cards)["valid"])
        cards[0]["id"] = "a-different-concept"
        self.assertIn("card_identity_conflict", self.codes(self.check(cards=cards)))
        self.assertIn("card_missing", self.codes(self.check(cards=[])))

    def test_malformed_json_values_report_validation_failures(self):
        p = copy.deepcopy(self.passport)
        p["causal_interactions"][0]["from_system"] = {"not": "an ID"}
        result = self.check(p)
        self.assertFalse(result["valid"])
        self.assertIn("type", self.codes(result))

    def test_image_file_hash_and_visible_input_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.bin"
            path.write_bytes(b"synthetic reference bytes; not an image generation")
            import hashlib
            images = {"images": [{"concept_id": self.passport["concept_id"], "path": str(path),
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                   "profile_ref": "PROFILE-2D", "visible_input_refs": ["left drag"]}]}
            self.assertTrue(self.check(images=images, check_files=True)["valid"])
            path.write_bytes(b"changed reference")
            self.assertIn("image_hash", self.codes(self.check(images=images, check_files=True)))
            images["images"][0]["visible_input_refs"] = ["nonexistent third-finger control"]
            self.assertIn("unresolved_ref", self.codes(self.check(images=images)))

    def test_cli_and_python39_syntax(self):
        import ast
        ast.parse((SKILL / "scripts" / "concept_gate.py").read_text(), feature_version=(3, 9))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "passport.json"
            path.write_text(json.dumps(self.passport, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SKILL / "scripts" / "concept_gate.py"), str(path), "--json"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertFalse(json.loads(result.stdout)["quality_certified"])


if __name__ == "__main__":
    unittest.main()
