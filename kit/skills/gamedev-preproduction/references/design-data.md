# GDD and TDD production data

## Required sections

| Document or data | Required contents | Acceptance |
|---|---|---|
| Product brief | Audience, fantasy, core promise, controls, session, differentiation, full scope and exclusions | Explain the first 60 seconds, first completed loop, and reason to return |
| Core rules | States, actions, inputs, guards, timing, contact, scoring, success and failure and retry | Two implementers derive the same outcome for the same inputs and seeds |
| Progression and content | Run and metagame and skill and social scope, unlock graph, authored vocabulary, grammar, pacing | Early, later and late-play examples lead to different decisions, including the first 3 and 10 loops where relevant |
| Economy and commerce | Ledger, sources and sinks, catalogues, availability, prices, earned and paid access, refunds | Trace balances through each action and failure |
| UX | Reachable screens, states and transitions, layout and tokens, back and focus and keyboard, localization, accessibility | Every reachable state has a clear path and specified behavior |
| Creative | Exact visual target, construction data, world and characters and rigs and motion, UI, effects, audio, haptics | Producers can identify required output, units, formats, and acceptance |
| TDD | Components and interfaces, data and events, save and versioning and backend and security, lifecycle and platform | Implementation can proceed from the specified architecture |
| Verification | Invariants, state coverage, seeded simulations, usability, fidelity, performance, and devices | Every requirement has artifact, owner, method, and evidence type |
| Production plan | Dependencies, milestones, finite asset and component inventory, costs, risks, reopening | Every required item is explicit |

Keep canonical machine data beside readable explanation. Reference stable IDs and label derived views. Pin schema, units, rounding, clamp, tie-break, and versioning alongside data.

## Minimum data layout

Use these suggested paths within the common package format:

- `design/core-rules.json` for actions, states, timers, units, ranges, and deterministic order.
- `design/input-map.json` for device and action, deadzone and threshold, buffering, cancellation, and assists.
- `design/progression.json` for run and metagame graphs, prerequisites, rewards, mastery, caps, resets, and catch-up.
- `design/content-catalog.csv` for IDs, tags, difficulty, prerequisites, weights, exclusions, and asset sources.
- `design/generation-rules.json` for grammar, budgets, constraints, RNG and version, repair, and fallback.
- `design/economy.json` and `design/offers.csv` for currencies, earn and spend, prices, SKU, grants, availability, and caps.
- `design/screens.csv` and `design/transitions.csv` for states, actions, guards, effects, destination, failure, and recovery.
- `design/events.json` for event schema, version, authority, and idempotency, distinguishing gameplay, audio, and analytics.
- `design/asset-scope.csv` for all required assets, variants, clips, states, consumers, counts, dependencies, and acceptance.
- `design/quality-budgets.json` for target devices and frame rate and timing, memory, installation and load, power, network, draw, textures, and audio.
- `design/verification.csv` for requirement, data, implementation, test, evidence, and owner.

`assets/domain-templates/` contains examples to adapt. Keep incomplete forms in draft status.

## Numeric evidence

For each value record unit, source and rationale, range, dependencies, authority, and test case. A retention target such as 35% needs an actual audience, sample, event definition, denominator, window, and uncertainty before it can be reported as measured. Label simulated revenue as a scenario.

Provide applicable worked examples for beginner, practiced and expert play, unlucky and lucky progression, payers and nonpayers with matched playtime, price and reward boundaries, purchase return offline, and interrupted saves. For complex formulas retain executable model, configuration, seed, and raw output. Rerun after dependency changes or materially unresolved results.

## Cross-system checks

A named ability retains its IDs and semantics across combat, unlocks, shop, UI, animation and event, saves, and analytics. Define stacking, duration, refresh, immunity, death and reset, and cues for each status effect. Define source, grant, persistence, retry and deduplication, and presentation for each reward. Resolve disagreement before Build.

## Game Model 4.0

Apply the [game model workflow](game-model-workflow.md), [model format](model-format.md), and [design-to-runtime mapping](design-runtime-mapping.md). Derived exports carry model version and hash and stable IDs. Use concrete model records for camera, input, actors, world, rewards, and learning. Fill applicable contracts completely.

## T production data

For applicable tracks among the 20, provide complete launch rules and data and catalogue or grammar, all reachable states and transitions and exceptions, finite assets and audio and UI and locale scope, and exact recipes. Numerical rules bind input types and units and domains, function or table, ordering and rounding and clamping and capture, time, outputs and side effects, and independent golden trace. Discrete rules define state and decision, priority and tie-break, commit and abort and recovery. Solvers pin backend, config, inputs, tolerances, and oracles. Use typed supported rules.

Add State Catalogue, Consistency Groups, Save Resume Matrix, migrations, and golden saves. Include applicable Actor/Knowledge/Action/Decision/Encounter/Boss contracts, damage, contact and lifecycle with deduplication and ticks and random streams and priority and topology effects. Derive alternate layouts from the same authority.

For each material output, specify `ToolCapabilityRecord`, `ProductionRecipe`, and `SemanticTransformation`. Record `ProductionAttempt` after actual execution and `AssemblyEvidence` after integration. T closes only with defined behavior, complete launch scope, and sufficient consumer inputs. Specify tuning with initial value, range, objective, and change procedure.
