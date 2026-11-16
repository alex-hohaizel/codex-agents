# Systems, catalogs, progression and handoff 4.0

## Navigation

1. C0, C1 and T boundaries and outputs
2. Register of twenty systems
3. Dependencies and change
4. Catalogs and progression
5. Lore and causality
6. Acceptance and sources

Use for ideation, technical design, implementation changes and returns from QA. The register uses canonical track IDs `TR01..TR20`. The project's canonical model owns IDs, rules and current decisions. This reference describes how to populate it. Keep GDD, spreadsheets, simulations and prompts bound to that source rather than independently editable models.

The six agreed P1 competencies have explicit resources. `math.md` covers behavior and math, `catalog-progression.md` covers catalogs and progression, `world-ai.md` covers world and AI, and `lore-narrative.md` covers lore. `experience-commerce.md` sections 1–3 cover experience and section 4 covers metagame and commerce. `systems.md` coordinates the register and handoff. `persistence.md` and the production reference span D1/D2. Choose staffing and features by actual requirements.

## 1. Set the output boundary

| Output | Deliverable | Decisions that can remain open |
|---|---|---|
| C0 concept sketch | Fantasy, main decision, distinction, risk and preliminary feasibility | Explicitly marked undeveloped systems. |
| C1 complete concept | Active systems, families, loops, progression, world, complete player journey, style, controls, economy, production route and scenarios | Numeric tuning with range, objective and selection method. Close material product choices. |
| T production handoff | Complete launch catalog or generator, typed rules, exact baseline numbers, states and transitions, resources, algorithms, adapters, fixtures, budgets and plan | Explicit future tuning with an initial value and method. Behavioral TBD blocks the recipient. |

A candidate presented as complete needs C1. Illustrations, screen examples and presentations can carry parts of the package. Develop T for concepts approved for implementation. An early risk spike needs a bounded question, measurement and rejection criterion. Establish production status separately from research code.

Record current, later, domain-inapplicable and unknown scope. Justify inapplicability from design. Missing SDK, time or unverifiable device availability leaves the applicable proof open. Preserve direct dynamic control, native targets, FPS and accepted artifacts when confirmed in the project profile. Keep previous decisions through new rounds. Apply [historical example](../historical-project-profiles.md) targets only to their recorded scope.

## 2. Maintain the twenty-system register

| ID | System | Minimum domain contract |
|---|---|---|
| TR01 | Concept and experience | Audience, fantasy, core decisions, pillars, limits and rejection criteria |
| TR02 | Lore and narrative | Canon, causality, knowledge, characters, factions and applicable quests or dialogue |
| TR03 | Entity state | Life, resources, ownership, states, recovery, death and failure |
| TR04 | Actions and physics | Intent, commitment, time, contact, solver mapping and interaction |
| TR05 | Items and capabilities | Families, characteristics, slots, compatibility, loadout and acquisition |
| TR06 | AI and other participants | Perception, knowledge, decisions, action, coordination and navigation |
| TR07 | World structure | Topology, locations, routes, transitions and persistent consequences |
| TR08 | Situation composition | Authored anchors and generation, legality, novelty, pacing, repair and fallback |
| TR09 | Playthrough | Session, stages or campaign, challenges, return and completion |
| TR10 | Player progression | Mastery, unlocks, specializations, collections, persistent and temporary aspects |
| TR11 | Rewards and economy | Sources and sinks, value, guaranteed and random results, limits and repair |
| TR12 | Monetization | Offers, metagame, effects, store, payment, entitlement and restore |
| TR13 | Controls and camera | Intent, gesture and action, grip, pointer ownership, mode and angle, cancellation |
| TR14 | Full UX | Launch, learning, session, error, exit, return, settings and support |
| TR15 | Visuals | Element and state style, readability, animation, VFX and budgets |
| TR16 | Audio and haptics | Events and states, SFX, music, voice, sync, mixing, priorities and alternatives |
| TR17 | Technical platform | Runtime, data, save, offline, conditional networking, performance and security |
| TR18 | Content production | Editable sources, recipes, authoring, import and export, localization |
| TR19 | Verification and measurement | Oracles, counterexamples and simulation, engine, native, device and human evidence |
| TR20 | Release and evolution | Versions, migrations, exact release, actual observations and support |

In the authoring view record applicability and reason, owner and recipient, purpose, source requirements, reads and writes, rules, content, progression, feedback, persistence, budget, invariants and due acceptance. Use `assets/v4-domain-templates/system-register.template.json` as an authoring worksheet. Verify the canonical field list and required evidence separately.

For `game-model.json` use the current schema. `production.tracks[]` has `id/name/enabled/rationale/owner/receiver/requirement_ids/summary/reads/writes/contract_ids/invariants/scenario_ids/progression/content/feedback/persistence/budget/concept_refs/spec_refs`. `concept_refs/spec_refs` contains `path/sha256`. Canonical keys stay fixed across languages and authoring views.

Record rules in `production.contracts[]` as `id/kind/version/track_id/owner/requirement_ids/purpose/status/inputs/outputs/read_refs/write_refs/depends_on/algorithm/invariants/cases/feedback/persistence/telemetry/body`. Status is `unresolved/defined/tuning`. Type I/O as `name/type/units/encoding/capture` and specify numeric precision and rounding at T. `scripts/v4_contract.py` verifies kind-specific `body`. Templates describe `materialization` into validated models. State fields belong in `production.state_fields`.

### Transfer the twelve authoring views into the canonical model

In templates, `template_only=true/status=draft`, null and empty lists mark unfinished input. Complete these before delivery as defined contracts. Store accepted detailed documents and tables as companion artifacts with path and SHA in `concept_refs/spec_refs` or `algorithm_ref`. Canonical contracts preserve IDs, typed interfaces, behavior and `cases`. Assign one authoritative location for every editable parameter.

| Worksheet | Canonical target and transformation |
|---|---|
| system-register | `systems[].id/name` → `production.tracks[].id/name`. applicability → enabled, consumer → receiver, purpose → summary, rules → contract_ids, references → concept_refs/spec_refs, due acceptance → scenarios, cases and evidence obligations. |
| behavior-rule | `production.contracts[] kind behavior/numeric/state_machine/rng`. Map type, unit and capture to inputs and outputs `type/units/capture`. Map concrete function to algorithm or algorithm_ref and exact details to the kind-specific body. |
| damage-resolution | kind damage,TR03/04. Map pipeline_order to body.pipeline with the nine canonical step names, dedup to repeat_gate and capture_inputs to capture. Channels require numeric_contract_ref, outcome_priority maps to lifecycle_priority, and simulation and durable commit stay distinct. |
| physics-contact | kind physics,TR04. Map engine to engine_version, step to fixed_timestep/substeps/solver_config, collision matrix to collision_layers/queries, measurement and curve to contact_adapter, destruction to destruction_topology, and motion and crash to crash_policy. |
| lifecycle-failure | kind state_machine/behavior,TR03/09. Map states, transitions and initial state to body semantics, profiles, priority and retry to algorithm and body, negatives to cases with concrete scenario IDs. |
| catalog-progression | kind family,TR05/10. Map dimensions, compatibility, progression, opportunities, dominance_counterexample and launch_catalog_ref to body, reward values to kind economy,TR11, and instances to state_fields. |
| world-generation | kind generator,TR07/08. Map inputs, constraints, repair, attempts, fallback and RNG to matching body fields, semantic_novelty to novelty_signature, progression to progression_envelope and exact authored transitions to state_machine. |
| actor-boss | kind ai,TR06. Map families, knowledge, actions, decisions and navigation to body actor_families, knowledge, actions, decision_model and navigation. Boss maps to boss_policy plus a concrete state_machine. State and save map to state_fields. |
| persistence-continuity | state_fields → `production.state_fields` using classification, units, consistency_group, commit, restore, merge, migration and retention. The kind persistence body contains consistency_groups, transaction, recovery, restore_pipeline, identity and cloud_policy. Keep the envelope in a pinned companion. |
| input-camera | kind input,TR13. Map intent_action_map to intents and bindings, input_profiles to recognizer, pointer_ownership, cancel, simultaneity and accessibility, camera to camera_arbitration, and first, peak and late cases to cases and peak_case. |
| experience-commerce | kind journey/presentation/economy/commerce across TR11/12/14/15/16. Map atlas and attention to states, failure, recovery and acceptance. Map earned, paid, portfolio, partial, grant, refund and reconcile to matching commerce body keys. Keep event matrices as pinned companions. |
| lore-narrative | kind behavior/state_machine,TR02. Map canon, knowledge, quest and scene conditions and changes to typed inputs, outputs, reads and writes, states, transitions and algorithm. Preserve exact text and graphs in a pinned companion and map restore choices to state_fields. |

Run the current structural and semantic checker after transfer. Verify kind-specific required keys in `scripts/v4_contract.py`. This table maps richer worksheets to the strict model envelope.

Record actual system edges. For each name source and output, target and input, type, unit and time base, legal states, version, conversion loss, error, owner and consumer check. For example, a punctured wheel can change grip, steering, available tracks, camera cue, repair cost and save. The studio logo may be independent.

## 3. Change through causal impact

1. Read current inputs, versions and decisions. Resume incomplete tasks and reuse valid completed results.
2. Identify changed IDs and contracts, including reads, writes, behavior, formats and assets.
3. Trace direct and transitive dependencies and inspect for missing edges.
4. Prepare a bounded repair package with one writer per file or scene and a named consumer.
5. Preserve independent outputs and evidence. Mark affected evidence stale pending new verification.
6. Run contract, integration, native and human checks required by each claim.
7. Update model revision, decisions, migration, observed facts and next action.

Hashes establish byte binding. Reuse evidence only with unchanged meaningful inputs, adapter and tool versions, environment and scope. A physics change needs affected review. Preserve independent studio identity when changing a damage curve.

## 4. Build catalogs around actual choices

At C1 specify the full taxonomy of launch families, mechanical dimensions, progression lines, acquisition, compatibility and contexts. T needs full data or exact grammar or generator, constraints, ranges, weights, versions and verified fallback.

For each family describe:

1. Role and the choice it adds.
2. Delivery, action, cycle and resource, with functional requirements beyond `+stat`.
3. Parameter types, units, ranges, formulas or rule references.
4. Slot, tag, dependency and exclusion rules, with legal and illegal loadouts.
5. Contextual use, cost, weakness, combinations and counters.
6. Acquisition, unlock, craft, repair, consume and respec with economy and save references.
7. Visual, audible and animated distinctions and required resource states.
8. Actual use opportunities after unlock and before and after completion.

Distinguish definition ID, instance ID and variant. Store runtime ownership at its proper boundary. Derive player-facing aggregates from exact parameters and comparable scenarios. For an aggregate such as «Прохідність» (“traversal capability”), name conditions and weights and make their meaning visible in the UI.

Check dominance across contexts and the paid portfolio as well as pairwise DPS. Set meaningful family and scenario coverage for this game. For a large design space use boundary, constraint, property and combinatorial checks and name untested combinations.

### Progression and rewards

For every progression edge define source capability, prerequisites, spend or achievement, exact change, new decision, next goal, opportunity, reset, loss or transfer, UI and learning, save and check. Keep separate run power, permanent unlocks, player mastery, collection and world completion.

Test unreachable prerequisites, cycles without purpose, trap choices, soft locks, mandatory repetition without purpose and rewards after their last opportunity. Discover, practice, transfer, combine and reinterpret describe functional relationships adaptable to the genre (D1Q09–10).

Each reward rule defines trigger, eligibility, amount or distribution, generation and claim ID, once or repeat scope, duplicates, cap and overflow, inventory, durable boundary, callback replay and downstream use. Check failure, retry or repair for indefinitely profitable cycles. At maximum level, complete collection and finale, define excess rewards, duplicate conversion, closed offers and honest completion (Q14).

## 5. Make lore causally meaningful

Distinguish world truth, character knowledge, belief or rumor, and presentation. A canon record contains `fact_id`, truth conditions, time and region, actors who know it, allowed changes, conflicts and dependent missions, assets and audio. Show the gameplay effects of narrative detail.

For scenes, quests and dialogue specify prerequisites, knowledge guards, priority and tie-break, speaker and addressee, choices and commitment, irreversible effects, interruption, resume and repetition, localization IDs, save and fallback. Guard mutually exclusive endings during merges. Align scarcity with economy and death and revival with failure rules.

Explain transitions in terms of motivation, losses and retained state, changed knowledge or goals, and possible return. Show understandable desired reward, conditions and odds where relevant. Give reused routes a functional purpose.

## 6. Accept the package with a recipient

Without chat history the recipient can reconstruct first action, late and peak situations, failure and recovery, new unlock and reward, pause and cold return, and conditional purchase or sync. They name IDs and versions read, outcomes, gaps and a new counterexample. Record author and independent checks separately.

Negative checks include a palette-only family, unlock with no opportunity, unusable reward, full collection that breaks store behavior, two writers for a lore flag, the recipient having to invent a rule, prior route proof surviving a grip change, and SDK availability mislabeled as integration.

For development and test specify a state lab with exact fixture, seed, loadout, locale and input profile, a legitimate transition, reset and expected result (D1Q16). Distinguish it from a bounded gameplay reproduction capsule (Q28) and runtime reason inspector (Q29). All use the same rule authority. Include a debug or cheat mode in release only for an explicit product reason.

Accept each scoped output against its due criteria. Record researched, specified, calculated, simulated, integrated, device-tested and human-reviewed status separately. Observe fun, balance, native performance and revenue at their actual boundaries.

## Source basis

Version 4.0 adapts approved P1/D1/D2 work. These sources were reviewed on 2026-11-02. Recheck version-specific claims when binding the actual project.

- MDA, links between mechanics, dynamics and experience: https://www.cs.northwestern.edu/~hunicke/MDA.pdf
- Epic Data Driven Gameplay, tables and curves: https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine
- W3C SCXML, event, state and transition concepts: https://www.w3.org/TR/scxml/
- W3C PROV-DM, entities, activities, agents and derivation: https://www.w3.org/TR/prov-dm/
- Dormans, mission and spatial structure: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
