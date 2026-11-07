# Quality that can be checked

“High quality” must become a concrete agreement about the requested result. For a narrow backend repair, this may mean preserving the API, proving a concurrency invariant and measuring the affected query. A mobile product needs additional user journeys, platform behavior, visual and language checks. A game needs actual controls, progression, save recovery and performance on representative devices. The task determines the applicable depth.

This model summarizes existing 5.0.0 contracts; it does not add a new universal product specification. Record each dimension as **required**, **conditional**, **absent by design**, or **unknown**, with a reason and the stage at which evidence is due. Missing access or a device is an unresolved proof obligation for a required feature. It is not a reason to silently remove the feature.

## From a promise to an observable result

| Dimension | What the project must decide | Evidence that helps close it |
| --- | --- | --- |
| Complete requirements | Every accepted need, constraint and emphasis has an ID, interpretation, owner, dependency and acceptance criterion. Deferred requirements retain an explicit place in the plan. | Compare original user sources with the requirement register; follow selected IDs through specification, implementation and verification. |
| Research and causal model | Which sources support a choice; what remains uncertain; which rules, state transitions, calculations and competing alternatives matter. | Dated primary sources where appropriate, counterevidence, worked examples, explicit assumptions and a bounded investigation for critical unknowns. |
| API, identity and data | Actors, authorization, tenant/owner boundaries, types, units, null/default semantics, schema versions and the authority for each state change. | Contract and negative tests, boundary fixtures, unauthorized/cross-tenant cases, and actual client→API→storage round trips where applicable. |
| Concurrency and consistency | Atomic groups, ordering, revision conflicts, duplicate inputs, retries, cancellation and ambiguous remote outcomes. | Failure injection around commit/dispatch, repeated events, out-of-order callbacks and restart; reconcile uncertain effects before retrying. Use queues or workflow engines only when justified. |
| Security and privacy | Trust boundaries, secret handling, least necessary access, sensitive data scope, consent, retention, deletion and export obligations. | Relevant adversarial cases, access-boundary tests, privacy-safe traces and observed deletion/revocation behavior. A checklist does not establish legal compliance. |
| UX and language | Normal, empty, loading, error, offline, permission and recovery states; conversation and product languages; truthful progress and durable success messages. | Inspect actual screens or conversations against the agreed journeys, content and locale fixtures. Keep optimistic feedback distinct from confirmed persistence or delivery. |
| Design identity and media | Approved originals, palette, typography, composition, motion, audio and allowed platform adaptations. | Preserve source hashes and editable masters; compare the representative runtime slice with the accepted reference. Check time-based media by actual playback/capture, not a static image. |
| Accessibility | The relevant interaction, readability, focus, semantics, input alternatives and platform-specific accessibility needs. Select a precise standard/scope/level when one is required. | Checks on the actual applicable web/native surface, assistive interaction where needed and human assessment for qualities automation cannot establish. Do not extend a web test result to every native property. |
| Performance and cost | Real input sizes, target devices/environments, concurrency, latency or frame-time budget, memory, startup, network, battery/thermal and operating cost where material. | Reproducible measurements with hardware/build/configuration, warm/cold conditions and denominators. Exercise representative peak and long-session cases; label provisional budgets and missing device evidence. |
| Payments and external actions | Authoritative amounts/units/rounding, entitlement rules, effect identity, webhook replay, restore/refund, timeout and compensation where these features exist. | Boundary and duplicate-action cases, actual provider contract checks, durable-state reconciliation and a trace from the request to its observed effect. A provider acknowledgment is not proof of human receipt. |
| Saves, memory and migration | Durable/reconstructible/ephemeral state, commit timing, backup/restore, schema compatibility, account binding and conflict policy. | Kill/restart, disk-full/corruption, unknown-newer-schema, offline divergence, account switch and isolated restore tests. Never turn an unfamiliar schema into a silent reset. |
| QA and release | The affected acceptance criteria, exact source/build, environment, reviewer, unresolved gates, deployment scope and rollback trigger. | Appropriate unit/contract/integration and actual-platform checks; inspect raw artifacts. Independent QA requires another actor. Keep source checks, host discovery, behavior, delivery and owner acceptance separate. |
| Operations and continuity | Useful health signals, incident recovery, support owner, exact checkpoint, open jobs, uncertain effects and the next action. | Privacy-safe error/retry/duplicate/queue-age and resource signals where relevant, observed health/delivery, a recovery exercise and a handoff that a new session can actually use. |

For a project-specific acceptance record, include the requirement or claim ID, exact artifact/build revision, environment and tool versions, procedure, observed result, limitations, actor/reviewer and evidence location. Mark outcomes **pass**, **fail**, **unknown**, or **not applicable with reason**. A critical privacy or false-success failure cannot be hidden inside an average quality score.

## Keep depth proportional and claims precise

An approved specification is evidence about the design. A deterministic test with mocks is evidence inside that test boundary. An integrated run, a live transport observation, a physical-device measurement and a human judgment answer different questions. Select the evidence needed for the actual claim and name anything unavailable.

Before dependent work, verify the current official platform, SDK or provider rules that matter to the project and pin the versions used. Agree applicable standards explicitly. This repository does not claim blanket certification, universal production readiness or superiority over every other tool. It supplies contracts and working procedures that help a capable host produce inspectable results.

## Canonical foundations

- [Application system contract](../kit/skills/app-atelier-specification/references/app-system-contract.md): applicability, causal commands, persistence, transformations and production evidence.
- [Application executable specification](../kit/skills/app-atelier-specification/references/app-depth.md): exact rules, API/data/state boundaries and acceptance.
- [Requirements continuity](../kit/skills/app-atelier-specification/references/requirements-contract.md): original intent, deferred requirements and evidence.
- [Chatbot quality and operations](../kit/skills/chatbot-atelier-specification/references/quality-and-operations.md): distinct evidence, negative scenarios, privacy and recovery.
- [Game architecture and device budgets](../kit/skills/gamedev-preproduction/references/engineering-architecture.md): numeric contracts, tool feasibility, saves and actual devices.
- [Concept-to-runtime fidelity](../kit/skills/gamedev-preproduction/references/fidelity-slice.md): approved identity, representative slice and controlled visual change.

Use these instructions with the actual product's accepted requirements and native state. Updating this summary alone does not alter the canonical skill sources, migrate a product or certify its behavior.
