# Bind the canonical model to the playable game

Use this before designing import or data flow and before changing a system. The [model format](model-format.md) defines canonical objects, rules, and dependencies. GDD, CSV, engine resources, and interface labels are projections of the shared rules.

## Binding and generation

For each imported object and rule, record model ID, domain, revision and hash, canonical path, runtime target and type and units, adapter and schema version, event consumers, fixtures, oracle, and scenario IDs. Keep generated output separate from editable sources. Map each consumer of a common field to one authority. Change generated numbers through that source.

Use `assets/runtime-bindings.template.json` as a starting format. Add measured evidence after observation. Derive affected work from model dependencies and runtime consumers. `game_model.py impact MODEL --changed ID` reports structural reach. Review semantic impact as a separate step.

| Domain | Runtime binding | Domain oracle |
|---|---|---|
| Camera | Projection, FOV and zoom, tracking and dead zones and lookahead, transitions and aspect and visibility and collision | Required actions, threats, and contact visible at actual play speed with the accepted follow behavior |
| Input | Intent and thresholds, context and cancel and hold and release, UI ownership, concurrent actions | Intended combinations are usable and gestures have predictable outcomes |
| Systems and equipment | State and effect, units, stack and cap order, conditions, cost and recovery | An item changes a concrete decision and counters and limits hold after swap and restart |
| Actors | Perception, knowledge and memory, decision and action, cooldown and cues, navigation and roles | Actors use available knowledge and different roles change player responses |
| World | Topology and grammar, gates and routes, interactive states, event and pacing budget, revisit | Reachable fair composition, meaningful risks and rewards, persistent consequences, and bounded fallback |
| Progression | Unlock and access, new capability, resets and catch-up, long progression milestones | Reachability from initial state and new ways to solve known contexts |
| Rewards | Trigger and authority and identity, tables and odds and guarantees and caps and duplicates, UI | Durable grant once, meaningful use, and recovery from adverse random draws or failures |
| Learning | Dependencies and unlocks, triggers and hints and mastery and skip and reentry | Players use learned capabilities independently and known prerequisites are reachable |
| Art | Source and import, motion and cues, audio bus, haptics, and quality | Exact lineage, normal and peak readability, and fallback for unsupported devices |
| Commerce | Eligibility and offer and store price, entitlements and transaction and reconciliation, ad cap | Free and no-offer path, pending and cancellation and refund and restore and restart, and combined purchase effects |
| Lifecycle | Atomic save and migration and checkpoint and RNG and pending effects, offline and auth and sync and telemetry | Kill and resume and corruption and migration and cloud conflict preserve progress without duplication |

## Events and state authority

Define simulation ownership and ordering of simultaneous events. Gameplay rules emit semantic events for motion, sound, and UI. Grant damage, rewards, and entitlements at their proper authority. Predictive cues can precede a durable commit where their meaning is clear and rollback or reconciliation is defined.

Define the clocks and tick policy for physics, rendering, and input. Keep simulation speed independent of render rate. Replay binds engine and content versions and tolerances. Verify actual determinism per target. Use distinct RNG streams for content, reward, and cosmetic effects as needed. Duplicate callbacks, reconnection, and scene reentry preserve durable effect identity.

## Scenarios and acceptance

Each scenario pins initial state, action, independent expected outcome, changed decision, and counterfactual. For an executed case, add actual input, seed, save, build, device, reproduction, evidence, and verdict. Use `assets/system-scenarios.template.csv` as a projection of canonical scenario IDs.

Use applicable deterministic numeric and property tests, state and event integration, authored and generated content validation, visual and motion and audio review, device touch and thermal and haptic checks, and human playtests. Keep simulation, actual retention and revenue, and enjoyment separate.

Before scaling content, use the native slice to verify risky shared bindings. Beta covers the accepted finite scope, boundaries and lifecycle, and target devices. Release adds the exact platform, commerce, and privacy checks. Keep unavailable gates blocked or unperformed.

## Negative controls

- Importer loads obsolete numbers under a new hash.
- Equipment claims a different style but changes only damage.
- AI families share all decisions but have different HP.
- A generator passes inventory count while producing softlocks or one universal strategy.
- Onboarding requires a locked capability or marks a button press as mastery.
- A successful build with mismatched camera, HUD, or inputs leaves experience acceptance open.

## Transformations and production records

Verify unit, precision, capture time, axes, color, sound, and motion as well as ID and path. A `SemanticTransformation` defines source and target conventions, preserved properties, intentional loss, and a discriminating validator. Verify shared design and runtime parity using golden fixtures.

For each production edge, pin accepted inputs, interface, owner and resource locks, supported operation and recipe, outputs and consumer. Link attempts and unknown-result reconciliation, semantic cache freshness, post-import checks and source round trip, and whole-scene `AssemblyEvidence` to the current model. Reverify relevant operations and versions after change.
