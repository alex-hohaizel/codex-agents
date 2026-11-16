# Feature acceptance criteria

## Feature receipt

Before implementation, map requirements to frozen decisions and data, fixtures, and expected player-visible outcomes. After implementation, map changed source and assets through actual runtime bindings, build and device evidence, and independent review. `assets/feature-slice.example.json` illustrates the record format.

| Area | Acceptance |
|---|---|
| Gameplay | Input, cancellation, boundaries, correct timing and physics, readable feedback, success, failure, and retry |
| Presentation | Accepted materials, palette, fonts and layout, whole-frame composition, and correct assets |
| Motion | Anticipation, contact and recovery, collision and rig, interruption and blending, appropriate camera, and demonstrated action |
| Audio and haptics | Exact cue-event mapping, mix, voices and ducking, contextual feedback, mute, reduced mode, and unsupported devices |
| UI and state | Applicable loading, empty, error, offline, and disabled states, focus, back and pointer ownership |
| Data | Atomic writes, migrations, idempotency, clock and network and state conflicts |
| Performance | Representative low-tier device, worst-case content, and frame-time and memory budget |
| Rights and accessibility | Lineage and license, contrast, scale, reduced motion, and captions where applicable |

For a narrow invisible fix, derive verification from the dependency impact. A new visible function includes applicable motion, audio, and user experience in its own acceptance.

## Causal scope

Record current model hash and object IDs, dependency closure, runtime bindings, and canonical scenario IDs. Establish expected behavior from a design oracle before implementation and record the observed result after execution. For a new capability, check changed decisions and a counterfactual without the rule. For actors, world, and equipment, test an actual interaction with another system. For rewards and offers, verify durable grants, meaningful use, and the free alternative when required. Choose a scope that covers these effects.

Before scaling content, pass the representative slice. Before beta, verify the accepted finite inventory and flows. Release additionally needs platform-specific QA and current store, purchase, and privacy evidence. Assign unmet device and human checks an owner and due gate. Keep structural checks and independently observed behavior separate.

## Repair cycle

1. Reproduce on exact build, state, and input and retain failure evidence.
2. Compare with the frozen independent expected result.
3. Locate the cause and affected dependencies.
4. Make the smallest complete repair at the code, asset, data, or rule source.
5. Run affected regression and required neighboring cases.
6. Have an independent reviewer confirm closure. Return any material change to the owner.

After two identical failures, use a different diagnosis, such as instrumentation, a minimal reproduction, another responsible owner or tool, or rule and source review. Match the process to the change. Record actual closure evidence.

## Fidelity and performance

Profile first to identify CPU, GPU, memory, or I/O limits. Measure the representative scene. Choose optimizations that preserve the acceptance target, such as batching, atlases, LOD with tested silhouettes, mesh compression, pooling, audio voice management, and deterministic scheduling. When the target hardware cannot meet the baseline, show the measured comparison and trade-off before changing visible or audible behavior.

## Test selection

Cover invariants, boundaries, failures, recurrence risk, and deterministic data checks. Use independent expectations for duplicate purchase callbacks, content softlocks, and corrupt saves. Repeat tests in response to relevant changes or findings.

## Game Model acceptance cases

For the affected feature, verify applicable rule, state, catalogue, and production-operation links to consumers and required observations. Damage checks include duplicate hurtboxes, snapshot and live modifiers, damage-over-time expiry and resume, HP versus barrier predicates, boss phase, death, cleanup, and reward kill boundaries. Save cases include termination, stale or disk-full writes, offline branch conflicts, old account callbacks, and golden migration. Production cases include ignored parameters, semantic loss, unknown attempts, and assembly mismatches.

After the change, rerun cases derived from the affected design. Record author checks, independent review, structural results, and each applicable medium separately.
