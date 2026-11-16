# Map the design to data and runtime

Use the common model format for authoritative type and field definitions. The domain checklist adds semantics. Treat forms in `assets/domain-templates/` as draft attachments until completed and linked to model IDs.

## One identity chain

Trace source and intent to model record, rule and data, runtime consumer, scenario, and observed evidence.

For each record define owner, dependencies, source decision, due gate, and evidence type. For each consumer name actual scene or component or module or configuration field, import or generation recipe, authority for updates and resets and persistence, and acceptance case. Derive documents, tables, and runtime data from the same authority. Include source version and hash, recipe version, and mapping in derived exports. Regenerate affected exports after input changes.

| Contract | Resolve | Consumers and verification |
|---|---|---|
| Camera | Projection and tracking, lookahead and limits, damping and zoom, modes, framing, reaction visibility, occlusion and offscreen, aspect and reduced motion | Controller, geometry, HUD, asset density, normal, peak and transition captures |
| Input | Gesture and action, units and thresholds, ownership and concurrent contacts, guards, press and release and cancel, buffering and assist, cues and latency | Adapter, intent, motion, camera and UI, interruption, two-thumb and low-frame-rate cases |
| Action and capability | Preconditions, phases, costs, targeting, order, state transforms, cooldown and cancellation, counters and consequences | Simulation, AI, collision, events, forecast, save, before and after scenarios |
| Actor | Role, senses, knowledge and memory, decisions and goals, actions, navigation, cues and commit and recovery, adaptation limits and counters, spawning and composition budgets | Behavior, encounter grammar, motion, performance, and fairness |
| Item and property | Units and formula, consumers, bounds, stacking and refresh and order, synergy and exclusion, access, equip and use and upgrade, reset and persistence | Inventory, resolver, collection and shop, cues, migration, meaningful use and abuse cases |
| World and route | Topology and access, connectors, entries and exits, materials and interaction, risk and reward, constraints, revisit, persistent outcomes | Scenes, generator and navigation, encounter and camera and progression and save, reachability and novelty |
| Progression | Prerequisites and cost, new capability, practice and combination, reinterpretation and next goal, catch-up and reset | Unlock authority and gates and learning and rewards, reachability from initial state and long progression |
| Reward | Trigger, eligibility, pool and version and odds where relevant, exact grant, duplicate handling, persistence, notification and first use | Ledger, progression and inventory and world, presentation and analytics, repeat, restart and revoke |
| Learning | Knowledge prerequisite, trigger, cue, safe practice, application and combination, independent transfer, help and skip and return | Onboarding, level and encounter, controls and UI, saves and observation with a first-time player |
| Commerce | Actual desire and offer, fit, eligibility and cap, SKU and grant and price authority, free and decline, cumulative effects, pending and refund and restore | Catalogue, store adapter, economy and inventory and UI and support, transaction and portfolio cases |
| Craft | Exact target and hash, fixed properties and tolerances, editable source and export and import, functional variants, events, and rights | Assets, materials, rig and clips, UI, audio and haptics, assembly, source reopening, and contextual review |

## Resolve conflicts before code

Define priorities and tie-break for simultaneous actions on one object, scene change during reward, spending the last resource while upgrading, equipment switch without automatic refill or reset, obscured AI cue, death during grant, and offline return to an expired offer. Document policy and version for important nondeterministic outcomes and record reproducible context. Verify cross-platform determinism separately if claimed.

Cover applicable novice and expert, early, mid and late, base and alternate equipment, safe and risky route, lucky and adverse draws, mute/no-haptic/reduced-motion, narrow and wide devices, and interruption and return. Choose runs based on risks and coverage.

## Use scenarios as oracles

Record exact initial state and config and seed, available actions, expected outcomes, and which decision changes. Link cue, asset, UI, and data IDs. Separate calculation, design review, and runtime observation. Assess actual content independently of filled fields.

Counterexamples include a new ability changing only damage, different enemies requiring the same response, a location changing only textures, camera zoom losing needed action, unused rewards, an owned portfolio bypassing every weakness, and onboarding without observed understanding. Repair the cause or change scope with the proper decision.

## Due evidence

Design freeze requires concrete accepted contracts, execution of applicable models, and independent semantic review. The representative slice requires actual source, import, runtime and named media checks before scaling. Physical comfort, haptics, and thermal need devices. Enjoyment and comprehension need people. Revenue and retention need real observations. Record owner and due gate for future evidence.

## Compatibility and gates

Use [model format](model-format.md) for schema 4.0 and actual CLI. Validate result formats against the current model contract. Map stable IDs across `camera`, `input`, `systems`, `actors`, `world`, `progression`, `rewards`, `learning`, `art`, `commerce`, `lifecycle`, and `equipment`. Keep dependencies and `initial_state/action/expected_observable/changed_decision/without_rule`. Add evidence only after observation. The gates are `concept`, `preproduction`, `slice`, `beta`, and `release`. Use preproduction for design freeze and slice for bounded Assets or Build verification. Handoff 1.0.0 and runtime 2.0.0 remain separate schemas. Read the toolkit marker from `scripts/pipeline.py` and `scripts/atelier.py`.

## Contact, results, and continuation

Connect action instance, target generation and window to contact facts and provenance, eligibility, typed channels, modifiers and defenses, resources and parts, statuses and reactions, then lifecycle, objective, credit, and reward intent. Deduplicate contact and retain designed multi-hit. Damage-over-time uses effect, target and tick identity with capture and expiry priority. Map physical impulse or energy to HP only by an explicit unit-safe rule.

Simulation commit applies coherent state and immediate cues. Durable commit protects critical rewards, spend, and victory. Cloud acknowledgment is separate. Exercise kill and retry and reorder and duplicate and resume, including simultaneous player and boss death. Grant kill credit at its defined authority.

For each design, source, export, import, and runtime link, record preserved properties, units, axes, timebase, color and sound, intentional losses, mapping, and validator. Verify deformation, contact, loop and semantic parity in the actual consumer.
