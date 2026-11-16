# Implementable app specification

Contents include the domain model, interaction boundaries, exact rules, state, production handoff, and acceptance.

## Shared domain contract

Read `cross-domain-core.md` and `app-system-contract.md`. Specify every required track of the accepted concept within product scope. Link requirement → rule and state → API and UI → operation → recipe → output → test → consumer. Give each requirement an observable criterion and due proof. Evaluate the specification at its own gate and require a binary when runtime proof becomes due.

For each entity, definition, and instance, define stable ID, owner and tenant, types, units and ranges, null and default semantics, mutability, version, authority, and access policy. Resolve tenant and identity from trusted authority. For each command, define actor and input, authorization and preconditions, validation order, value capture, atomic group, next state, events and response, idempotency or effect identity, errors, cancel, timeout and reconciliation, and durable acknowledgement. Errors specify code, retryability, user message, state change, telemetry without sensitive values, and support route. A network timeout leaves the command outcome unresolved until reconciled.

## Rules and composition

Define exact order, units, rounding, clamping, capture point, and tie-break behavior for formulas, tables, curves, and composition. For example, check quota availability, purchase entitlement, and account role against their defined authority and revision as distinct permissions. Specify calendar, timezone and DST or elapsed time and rules for expiry and clock jumps. For stochastic or AI output, define permitted results, model and version, parameters, validation, fallback, and cost cap. A criterion such as «якісна відповідь» needs an observable definition.

Cover the complete launch catalogue or its exact grammar, prerequisites, exclusions, compatibility, ownership, entitlements, migrations, aliases, and removals. Define which systems read and write other systems and with what consequence. Product feedback loops are possible. Keep execution dependencies in a DAG with bounded repetition and event cascades with termination, budget, and deduplication.

## State and persistence

For each field, define scope, lifetime, authority, serialization, consistency group, commit trigger, recovery, and retention. Keep optimistic UI, local commit, pending remote effect, synced state, conflict, and error distinct. Preserve originals and previous-good state during restore and migration. Preserve unrecognized newer schemas for recovery. Define acceptable data loss and acknowledgement for critical spending, grants, and user work. Compare offline or local-first against the minimum adequate alternative. Adopt cloud when the product requires it.

For sync, define conflict detection, revision ancestry, causal merge per entity and command, idempotent replay, owner and session binding, tombstones, limits and retention, cancel, revoke, and restore. Use domain-safe conflict rules for independently consumed resources. Define typed adapter callbacks, threads, lifecycle, and account transitions. Bind late callbacks to their original session. Keep backup, sync, transfer, and purchase restore interfaces distinct.

## Production handoff

Inventory client screens, states, accessibility, locales, data, schemas and migrations, domain, API and native adapters, applicable commerce and support, content and media, and CI, build, config, symbols, release and operational jobs. For each item, specify exact producer and consumer formats, editable source, required tool capability, schema and parameter evidence, compatible pinned toolchain, and ordered recipe. Prove transformations for timezone and dates, currency and precision, enum, null and ID, font, density and locale, callback thread and account, and source export and import. Choose a minimal architecture based on change, risk, and measurement, including any framework, DDD, CQRS, ECS, DI, or distributed components only where justified.

Test design includes shared domain fixtures across agreed clients, useful negative, boundary and property tests, adapter conformance, persistence faults, accessibility, performance, security, and exact assembly scenarios. Each oracle records initial state, action, expected intermediate and final values, tolerance, diagnostics, and proof level. Replace vague goals such as «швидко» with a target, percentile, device, data, load, and measurement grounded in the product.

## Handoff without invented downstream work

Use assets/app-depth.templates.json as the specification form and bind it to the project. Have an independent receiver reproduce the core, edge and recovery story and expected tests from the document. Block dependencies on unresolved critical values. Distinguish a tunable baseline with range, owner, and acceptance from a critical unknown. Hand exact versions, accepted masters, current constraints, capabilities and probes, due gates, and next action to build, support, experience, QA, and release. Upstream changes invalidate affected dependencies.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show the whole-product and component model, chosen languages and stack and ADRs as needed, exact rules and contracts, fixtures, and due acceptance. Distinguish completed work, inherited decisions, and future results with due gates. Scale depth and specialist involvement to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review semantic coverage, architecture tradeoffs, production feasibility, and missing dependencies. Inspect raw sources for omitted requirements. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve project context, current approvals, and unaffected results.
