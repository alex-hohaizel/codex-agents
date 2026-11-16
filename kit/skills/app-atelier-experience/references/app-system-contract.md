# App Atelier domain model and end-to-end production

Use this contract with `cross-domain-core.md`, current core, workflow and runtime, and the project profile. It extends preserved REQ-ID records. Profile, ledger and economics use distinct current schema IDs. Earlier result formats are unsupported. Installing a skill does not migrate a product, database or user data.

## 1. Derive applicability from the product

For each area in `assets/app-system.template.json`, record `required`, `conditional`, `absent_by_design` or `unknown`, with reason and due gate. Missing tools, SDK, access or evidence for required work are blockers. A critical unknown needs an owner, question or bounded probe, limit and next decision.

Consider user, payer and domain event, definitions and capabilities, causal rules and calculations, journeys, Android/iOS/web, guest/auth/tenant, local state and restore, optional sync, API and integrations, documents/media/generation, UX/motion/audio/haptics, accessibility and locales, commerce and entitlements, support and knowledge, distribution and acquisition, security and privacy, performance and cost, and deploy, operations and retirement. AI, cloud, microservices, subscriptions, RAG and analytics are conditional. For a new product show proposed platforms and decide scope before dependent promises or implementation. For an existing product preserve the agreed client set. A reduction requires an explicit change decision, and a missing target or SDK does not cancel a requirement.

Distinguish a direction sketch, a complete concept for decision, and an executable specification or production handoff. A concept identifies active systems, journeys, operating model, feasibility and critical unknowns. Tunable values may include a range and due gate. A handoff defines transitions, values, formulas, authority, permissions and errors before implementation. A tunable parameter includes baseline, range, owner and criterion. An early bounded probe does not close the handoff.

## Profile, method and current decisions

The general method requires applicable intent, causal contracts and adequate proof. Platforms, monetization, owner labor, allowed human tests, spending and product goals come from the current profile and sources. Treat family defaults as proposals. Another product's history does not create a policy here. Keep zero external spending and restrictions on human experiments or daily manual labor where accepted or enforced by conservative runtime defaults. A new route requires exact scope and a source of authority.

Use [adaptive work](adaptive-work.md) for material scope and [shared competencies](research-and-synthesis.md) when research, synthesis or independent reconciliation is needed. Register the resulting artifacts in the current ledger. Show the sufficient method and evidence limits. Use a short impact-based route for a clear local repair.

## 2. Exact domain contract

For each entity define stable definition and instance IDs, owner and tenant, field types, units, valid ranges, optional/null/absent, truth source, sensitivity, changes and versions. Use a domain-defined numerical representation for money. Distinguish UTC instant, local calendar date, timezone, monotonic elapsed time and display format. Verify large integer ID round trips across client, JSON, API and database.

For each command define actor and authorization, input schema, preconditions, value snapshot, atomic consistency group, order of checks/calculations/rounding, transitions, response, UI feedback, durable acknowledgement, emitted events, idempotency, cancellation, expiry, timeout and unknown result, and compensation. Event delivery or callback does not automatically authorize a new action. Define behavior for repeated taps, duplicate webhooks and background replay.

Transition tables include start state, event, guard, destination, data change, forbidden transition, retry/reconcile and oracle. For concurrent events specify priority, tie-break and concurrency revision. For probabilistic or AI output define variability, model and version, supported parameters, acceptable results, malformed output, refusal, fallback and the quality criterion. Do not promise bitwise repeatability for an opaque generator. Use worked calculations with intermediate values, boundaries and tolerances.

Represent resources, quotas, subscriptions and rights as causal states. Server expiry, a delayed local event and cached data have different authority. Use the same domain fixtures across agreed clients and document platform-specific adaptations without removing required core behavior.

## 3. Persistence, sync and failure

A state field has scope, lifetime, authority, serialization, sensitivity, consistency group, commit trigger, recovery, migration and deletion behavior. Separate derived cache from canonical data. Define atomicity, durability, ordering and previous-good value for local writes. Show Saved only after the applicable success. A process can terminate without a lifecycle callback. Optimistic UI feedback, durable local commitment and remote confirmation are separate states.

Restore through bounded untrusted parsing, integrity and owner/schema/content compatibility checks, preservation of the original, known migration, invariant verification, atomic logical application, dependency-ordered recovery, reconciliation of pending work and neutral input/UI state. An unrecognized newer schema must not silently reset data. Backup, checksum or encryption does not establish semantic compatibility or access rights. Use a suitable SQLite snapshot operation. Copying a live WAL database is not generally a backup.

Sync is a separate adapter. Define revision ancestry and conflict resolution, queue, retry/backoff/cap, lease, account and session binding, and deletion tombstones when needed. Generic max, sum or latest-time rules are not universally valid. An event log cannot legitimize two offline spends of the same resource. A delayed callback from an earlier account must not write to the new one. Reconcile unknown remote effects first. Continue the authorized local core according to design.

Test disk exhaustion, truncated/corrupt/newer data, termination before and after commit, reordered writes, offline divergence, auth expiry or account switching, quota, timeout, delayed callback, duplicate grant or spend, and restore after deletion or revocation. Record restore results for the exact build and schema. Installing an earlier binary does not undo migrated data.

## 4. Transformations and complete inventory

Inventory launch features, rules and data, screens and states, assets, content and locales, API and native bridges, billing products, support articles, builds/configs/symbols and operational jobs. For each output define consumer, recipe, input hashes, editable master or source, runtime derivative, validators and due evidence. Extend the taxonomy where needed without producing unnecessary outputs.

For each spec to design to source to export to import to client to release transition, record preserved invariants, deliberate changes and losses. Verify units, precision, rounding, currency, timezones, calendars and DST, enumerations, schema, null and IDs, tokens, font metrics and density, color and alpha, frame/second/sample, accessibility semantics and focus, callback/thread/account/session, localization grammar and length, and content rights. A format check cannot establish semantic fidelity, visuals, sound or accessibility.

Image generation may produce a conceptual raster. Editable vectors, layered source, UI tokens and accessible components require their own operations. A screenshot, clickable prototype, runtime screen and store screenshot have distinct scope. Preserve the accepted original and hash during repair. Use music, voice or animation only where it adds product value, with rights, editable source, runtime routing and appropriate listening or device evidence.

## 5. Production operation and evidence

For each work class bind capability, recipe, semantic transformation, attempt and assembly. Capability identifies operation, host/toolchain/model, actual schema/catalog, supported and unsupported parameters, rights, cost, limits, required probe and freshness triggers. Plugin description, binary presence and performed operation are separate facts. For a material input establish `requirement → schema field → provider support → consumption check`.

A recipe has accepted inputs and hashes, output/interface/consumer, competence, owner and paths, ordered steps or dependency graph, exact bound command/API or numbered GUI steps, toolchain, validators/oracles/tolerances and budget, effects, repair and stop. Before a costly or external action record a pending attempt with stable effect identity. After invocation record actual request/job IDs, append-only observations, outputs and hashes, cost and receipt. Keep a timeout unknown until reconciled. Do not invent a missing job.

Select competencies from deliverables: domain research, requirements/math, UX/accessibility/content, native clients, API/data/security, commerce, QA/performance and release/operations. The lead produces and integrates. Critical acceptance requires a different actual reviewer. Use one writer on shared source, state, device or account even across worktrees. Change diagnosis after two equivalent failed repairs. Cache by semantic input hashes, recipe/tool/model/export/import/platform/data scope. A new importer invalidates dependent derivatives and preserves the accepted master.

## 6. Accept the integrated application

Before scaling, accept a representative assembly with exact source/build/config/component hashes, actors, initial data, account/network/device settings, actions, expected and observed results, evidence modes and gaps. Exercise the journey from useful action to domain state, persistence, presentation and restart/recovery, with applicable sync, payment and support. Verify the core separately on every agreed client, including Android, iOS and web when in scope. Native performance, purchases and device behavior require appropriate actual target proof.

Keep structural, arithmetic/domain, integration, accessibility/perceptual, platform/device, security and observed business evidence separate. Choose a negative test that could expose an actual defect. Test depth should match impact. A simple reversible text decision need not have a programmatic test. Complete a concept or specification at its own acceptance gate without requiring it to be production-ready.

A change to input, permission, toolchain, schema or target invalidates dependent claims. Give a cold receiver an exact index, sources and hashes, contracts, launch/return steps, oracles, blockers and next action without relying on chat history. Keep authority in current profile and state. Register linked model assets as hashed artifacts rather than a second mutable ledger. Record exact checkpoints for release, observation and waiting. A closed chat does not run monitoring.

## Primary sources and limits

Reviewed on 2026-11-03 as method references. Check current SDKs, rights and limits at binding time.

- Android offline-first architecture: https://developer.android.com/topic/architecture/data-layer/offline-first. Use its local/network modeling and write and conflict guidance. It does not provide a universal sync policy.
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/. Select applicable accessibility criteria and prove the claimed scope and level. Browser automation does not establish native accessibility.
- SQLite atomic commit/WAL: https://www.sqlite.org/atomiccommit.html and https://www.sqlite.org/wal.html. Apply commit assumptions and recovery guidance for the actual durability mode and platform.
