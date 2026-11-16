# App specification workflow

## Contents

1. Pin the baseline.
2. Model domain rules and the product core.
3. Specify data, identity, and sync.
4. Design architecture and dependencies.
5. Specify commerce, operations, and acquisition.
6. Plan scope, a representative slice, and release feasibility.
7. Deliver the packet and manage changes.

## 1. Pin the baseline

Read `.appatelier/profile.json` and `.appatelier/state.json` under the common contracts. Use the typed requirements, decisions, knowledge, jobs, artifacts, evidence, executions, capabilities, grants, and effects registries. Reuse the accepted concept ID, revision, owner decision, evidence and input hashes. Carry audience, market and languages, recurring value, commerce hypotheses, operations and acquisition into the baseline. Resolve routine technical questions within the accepted direction. Route a material concept change through the director with affected REQ-ID, effects and decision delta.

Create `spec-index.json`:

| Field | Record |
|---|---|
| `spec_id/revision/status` | Identity and draft, spec-ready, blocked, or superseded status. |
| `inputs` | Exact path or ID, hash, revision and purpose. |
| `profile_version/requirements_version/decision_ids` | Sources of constraints and authority. |
| `outputs` | Path, hash, evidence type, REQ-ID and owner for each output. |
| `gaps/blockers/recheck` | Unknown, blocked action, due gate, owner and next check. |
| `resource_cap/stop/checkpoint` | Work and resumption boundaries. |

Distinguish facts, assumptions and decisions. Verify mutable API, license, price and platform requirements through current primary sources, recording URL, date, version, region and access limits. Keep live integrations, purchases and registration outside specification. Without read-only access, mark unknown and the affected gate.

## 2. Model the domain and product core

Create `prd.md` with problem, audience, context, useful outcome, recurring value, release scope and non-goals while preserving mandatory requirements. Separate user success and technical indicators. Synthetic UX supports scoped observations, and demand or willingness to pay requires corresponding evidence.

Create `domain-model.md`. For each entity define:

- Stable ID, user meaning, source of truth and ownership.
- Fields, types, units, constraints, validation, defaults and nullability.
- States and transitions with actor, guard, command or event, effect and resulting state.
- Invariants, relations and cardinality, terminology and deletion.
- Duplicates and concurrency, time, timezone and expiry, retry, recovery and compensation.
- Valid and invalid synthetic records and boundary cases.

For each `RULE-ID`, link precondition → decision → observable outcome → failure or recovery. Define exact permitted transitions. For external data specify provenance, freshness, confidence, and stale or partial behavior.

Create `client-core-matrix.md` with first use, first value, repeat use and recovery. For each step, record Android, iOS and web, common rule, valid platform difference and acceptance ID. Require a complete core in each client and separate observed proofs even when code is shared. Define material loading, empty, success, invalid input, denied permissions, error, offline, stale, and retry states. Give experience domain terms, content hierarchy, types, states and constraints. Route material design choices to the owner. Justify OS, browser and device support, text scaling, keyboard, screen reader, contrast, input, and performance budgets. Address accessibility, older devices, and offline behavior even without a profile minimum.

## 3. Specify data, identity and sync

Create `data-auth-contract.md` and schemas. Compare local-only without accounts, optional account and sync, and required cloud on value, cost, rights and recovery. Choose the minimum sufficient data and surface material architecture choices.

| Aspect | For each field or flow |
|---|---|
| Meaning | Type, sensitivity, owner, source, purpose and necessity. |
| Copies | Device, backend, vendor, backup, logs, cache and derived indexes. |
| Rights | Actor and role, resource and action, server guard, and distinct guest and account access. |
| Transfer | Recipient, transport, region as applicable, AI scope and redaction. |
| Lifecycle | Retention, expiry, export, deletion, revocation, backup retention and restore behavior. |
| Gate | Source and decision, consent and config, test ID, specified or verified status. |

Specify account necessity, guest lifecycle, sign-in and sign-out, recovery, deletion and device changes as applicable. For guest-to-account merge, define ownership proof, duplicates, partial failure and safe retry. Explain intentionally absent accounts and avoid collecting identity solely for marketing. Define backend resource and action authorization, tenant boundaries, replay and idempotency. Obtain identity from trusted server context.

Define sync authority, revision, conflict detection and resolution, tombstones, retry queue and pending UI. Cover offline create, edit and delete, concurrent changes, skew, stale cache, and recovery after long disconnection. Preserve deletion and revocation across old backups and devices. Specify migration, version compatibility, code and data rollback, backup and restore acceptance and limits.

Specify public knowledge, owned guest session, allowed account context on app and web, and separately selected channel linking. Require server proof of identity, link, scope, expiry and revocation. Usernames or identifiers claimed in chat convey no authorization. Model dialogues, attachments, logs, indexes, caches, and AI inputs and outputs as distinct flows. Keep private requests out of public knowledge, training and unrestricted diagnostics.

Keep initial support read-only. Specify separate auth, confirmation, idempotency, and receipt for mutations. Keep telemetry disabled or pending until events, properties, purpose, consent, retention and cost are authorized. Track operational signals, product analytics and intentional experiments with their own permissions.

## 4. Design architecture and dependencies

Create `tdd.md`, `api-contracts/` and `dependency-options.md`. Derive drivers from domain, privacy, offline, platform, cost and resources before selecting frameworks or vendors. Compare a feasible baseline with strong alternatives. Evaluate native, shared and web technology against the full core. Show components, ownership, interfaces, deploy units, trust boundaries and failure propagation.

For API define protocol, path and method, schema and validation, auth and authorization, errors, pagination, rate and cost caps, timeout, retry, idempotency, and compatibility. Specify event producer, ID, schema and version, consumer, order, deduplication, late and poison-event handling, and retention. Distinguish unknown external outcomes from repeatable operations before retrying. Define secret storage, injection and rotation without embedding values.

| Dependency | Compare |
|---|---|
| Need | Concrete benefit, quality boundary, and route without the provider. |
| Price | Setup, recurring and usage cost, overage, free limits, currency, date, taxes and cap. |
| Rights | Commercial use, attribution, redistribution, derived data, caching, export, termination and platform limits. |
| Data | Transmitted fields, retention, documented training policy, region and deletion. |
| Quality | Freshness, accuracy, latency, availability, uncertainty and unacceptable failures. |
| Failure | Quota, outage, stale and offline behavior, fallback and visible limitations. |
| Replacement | Portable schema and adapter, export and exit, migration effort and lock-in. |

Treat unknown pricing or licensing as a blocker or bounded assumption according to impact. Include low, expected and stress usage, abuse, retry storms and runaway cost. For AI, define allowed task, data and effect, validation, failure and fallback, and user and system caps. Verify actual outputs rather than inferring correctness from a model or API.

## 5. Specify commerce, operations and acquisition

Create `economics-operations-growth.md`, retaining the accepted model and explicit assumption deltas. Include selected or conditional free, paid, ads, module, subscription, usage, team and affiliate branches. Define value, offer timing, price hypothesis, free and paid paths, costs, refunds and sustainability. Calculate operating profit from revenue less fees, refunds, infrastructure, AI, API, data, acquisition, support, content and other operations. Track owner time and personal taxes separately and avoid double counting. Show sensitivity to conversion, retention, usage, refunds, margins and vendor price. Keep targets, forecasts and outcomes distinct. Control recurring liabilities funded by one-time payments with caps, reserves and justification.

Create `billing-entitlements.md` for the selected model. Specify product and provider IDs, entitlement, scope, duration and units, authority, platform and region, and portability limits. Keep intent, transaction, verification, entitlement and displayed access separate. Define applicable pending, active, grace, expired, revoked, refunded and cancelled states. Determine expiry from the applicable policy. Specify validation and signatures, dedupe keys, replay, delayed and reordered events, and reconciliation.

Cover restore, new device, sign-out and sign-in, guest linking, recovery, offline allowance and expiry, and process death between successful payment and local record. Verify Android, iOS and web access under current rules, including cross-store portability. Define refunds, chargebacks, partial consumption, expiry and cancellation when relevant. Mark precise no-purchase branches `not_applicable` with reasons and preserve applicable ad, affiliate and usage rules. Define build and QA sandbox tests. Keep live purchases outside specification acceptance.

Map trigger → job and tool → input and output → permission → cap → failure and retry → unresolved case. Include content and data, applicable moderation, support, incident diagnosis, billing reconciliation, backup, updates and vendor changes. Give unresolved cases IDs, permitted diagnostics and state, and a route to engineering. Ground staffing and SLA in the real model. Flag recurring manual work for a model decision. Link zero-audience acquisition to channel, automated production and distribution, rights, cadence, cap, metric and stop. Deliver growth planning before full build and activate after actual release and a separate gate. Keep messages, outreach, ads, publication and scheduled effects outside specification.

## 6. Plan scope, slice and release feasibility

Create `scope-estimate-roadmap.md`. Compare complete core and wider scope under the same assumptions. Break down Android, iOS, web, backend, data, design, support, QA, release and operations. State ranges, critical path, integration effort, unknowns, buffer, and resource and host caps. Verify actual reuse, license and readiness. Route material tradeoffs for time, scope and quality to the owner. Use approved dates or dependency-based estimates.

Create `representative-slice-plan.md` for the greatest architectural risk. Include a real core path through client, domain, persistence, sync, API, permissions and recovery as applicable, and payment if a critical risk. Define fixtures, target environments and clients, inputs, observed output and oracle, threshold, controlled failure, cap, and stop. Include the most expensive or uncertain dependency and use bounded checks where sufficient. Give build a scoped job before mass work. Keep `slice_planned` until actual artifacts, logs and tests arrive.

Create `release-feasibility.md` with the release skill before significant build. Verify current, dated official rules and fees, client routes, account type and status, ownership, signing and build host, testing, submission, privacy and commercial prerequisites. Mark accounts `unverified` without appropriate read-only proof. Expose mandatory equipment, fees and recurring costs even under a spending freeze. Check required human participation against current limits. Keep recruitment or simulation outside the spec action. List exact MFA, payment, signature or legal prerequisites and blocked effects. Provide an allowed route, scope, time or budget decision, or stop. Set `recheck_due: before-release` for rules, prices, accounts, signing and testing and recheck on platform, account or model changes.

| Gate | Require |
|---|---|
| `spec-ready` | Concrete contracts, estimates, due checks, and resolved specification blockers. |
| `before-full-build` | Accepted scope and design, economics, operations and acquisition, cap, early feasibility, and observed slice. |
| `before-release` | Actual client, support and billing tests, current prerequisites, data, brand and model decisions, owner readiness and authority for the effect. |

Resolve due specification rules and decisions before spec-ready. Leave external feasibility blockers on their dependent production actions. Require working product evidence at the build and release gates where due.

## 7. Deliver and manage changes

Save results under `project/specification/`. For narrow work, combine documents while preserving named sections and IDs. Create `acceptance-matrix.md` tracing REQ-ID → artifact or rule → platform and model applicability → test or fixture → due gate → evidence and state → blocker and owner. Include domain checks for REQ-11/REQ-16/REQ-19, early REQ-38 and cross-cutting mandatory requirements. Keep future build, QA and release `specified_not_implemented` or the appropriate common status until observed. For `not_applicable`, record reason, scope and owning decision.

Give experience states and terminology, build rules, schemas, API and slice, support data, auth and knowledge, QA fixtures and oracles, release recheck, and growth and operations costs, jobs and caps. Bind exact inputs, outputs, hashes, decisions, evidence limits, blockers, stop and next action using the handoff contract. For entity, data, API, paid-access or platform changes, record change ID, affected REQ-ID, consumers, invalidated evidence and recheck. Reuse unaffected proof with valid dependency pins and show impacts on time, cost, authority and release.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show the whole-product and component model, languages and stack and ADRs as needed, exact rules and contracts, fixtures, and due acceptance. Distinguish completed work, inherited decisions, and future results with due gates. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review semantic completeness, architecture tradeoffs, feasibility and missing dependencies. Inspect raw inputs for omissions. Verify reviewer competence beyond actor ID and keep structural checks at their actual proof level. Preserve context, approvals and unaffected results.
