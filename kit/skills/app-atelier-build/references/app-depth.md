# Production implementation in App Atelier

Contents: 1 scope, 2 domain rules, 3 data and sync, 4 production, 5 assembly, 6 handoff.
Read the current workflow, acceptance, cross-domain-core, and [app system model](app-system-contract.md). Use `assets/app-depth.templates.json` as a project artifact template and register project-bound artifacts in canonical state. Record completed builds separately.

## 1. Derive the complete implementation scope

Build the inventory `requirement → use case → state/variant/platform → rule → output → consumer → proof`. Define the variation rules and boundaries for each class. Include loading, empty, invalid, denied permission, offline, conflict, pending, revocation, upgrade and resumption, locales, text scaling, and input methods where applicable. Distinguish a blocked tool from a feature deliberately excluded from the product.

Give every module and output an owner. Separate rules, immutable definitions, mutable state, storage, network and platform adapters, and presentation according to how they change. Choose architectural patterns according to coupling and risk, including microservices, DDD, CQRS, or event sourcing only where justified. Use appropriate specialists and evidence for consequential financial or professional domains.

For risky libraries or capabilities, verify the exact operation, version, platform and host, inputs and supported parameters, editable output, rights, data and cost, probe, and known loss. Verify actual import, callback, and integration beyond CLI or plugin discovery.

## 2. Specify and implement every rule

Define inputs, types, units, ranges and null semantics, preconditions and authority, capture time, ordered calculation, precision and rounding, output, transition, errors, cancellation, timeout, deduplication, and invariant. Distinguish values captured at start from those read at commit. Define price revalidation and user notice when a displayed price is stale.

Verify numerical rules with independent golden vectors and boundaries. Specify currency and scale, discount, tax and commission order, rounding, and a justified representation for money. Distinguish calendar dates, timezones, instants, and durations. Define time authority, DST, monotonic deadlines, simultaneous-event ordering, and policy for clock changes. Test applicable random distribution, seed scope, tail and failure rates as well as aggregate measures.

Distinguish the user command, transport event, durable operation, and UI notification. A repeated tap or callback uses the appropriate existing identity. Define `command_id`, `entity_id`, `revision`, `operation_key`, and deduplication retention. API retries need provider-supported identity and reconciliation to support an exactly-once claim.

Implement applicable states from created and validated through pending, committed, failed or unknown, and reconciled or compensated. Check actual cancellation outcome. For multiple steps, specify point of no return, partial result, compensation ownership, retry boundary, and effects outside compensation.

## 3. Data, sync, and continuity

Each field has a stable ID, type and unit, default, owner and authority, source, persistence class, schema version, privacy scope, retention and deletion, and migration. Distinguish reference data, user and session state, transient UI, and derived cache. Rebuild derived state only from current authorized sources.

Define atomic boundary and commit acknowledgement for each consistency group. UI wording identifies locally accepted, remote confirmed, and queued status. Keep independent local feedback responsive and confirm irreversible purchases, rights, and awards at their durable boundary. Specify outcomes for full storage, interrupted write, corruption, process death, and restore.

Give an offline queue durable identity, ordering and dependencies, cap, expires_at, account binding, and pending feedback. Preserve A's commands under A when switching to B. Specify conflicts per field or command, including revision, merge, authoritative replacement, or explicit conflict, with an authority policy for client timestamps and skew.

Preserve deletion, revocation, and tombstones through retries and backup restore. Test upgrade from supported prior schemas and code and data compatibility before rollback. Retry migrations only under their specific contract.

## 4. Execute production recipes

Bind inputs and hashes, required expertise and owned paths, exact toolchain, argv or API fields or numbered GUI steps, DAG, outputs and masters, consumer bindings, validators, cost and time cap, fallback, and stopping condition for each output. Resolve template bindings before execution.

Verify `requirement → schema field → actual support → consumption proof` for material parameters. Preserve accepted originals, editable sources, and runtime derivatives separately. Confirm distinct rights for tools, fonts, samples, and inputs. Import UI, audio, and animation with their event, timing, scale, color, and encoding contracts.

Before costly or external work, record a pending attempt with input, toolchain and recipe hashes and stable key. After submission, record the actual job or request ID, observations, cost, output hashes and receipts. Reconcile unknown outcomes and costs before retrying. Change prompts with a testable hypothesis. After two equivalent failures, change diagnosis or method or mark a precise blocker.

Cache identity includes inputs, recipes, tool, model, exporter and importer versions, target profile, parameters, rights, and data scope. SDK changes reopen dependent derivatives and proof. Preserve approved masters. Device proof is specific to its build and platform.

## 5. Verify integrated assembly

Capture source, build, config and component hashes, bindings, initial state and actions, invariants and tolerances, platform, device and input method, and actor IDs. Exercise `input → rule → state/storage/provider → UI/accessibility → support → restart/resume`. The representative slice includes the highest-risk interaction, accepted assets, and target client.

Check simultaneous submit and cancel, timeout after actual commit, mid-flow revocation, offline to online, account switch, schema upgrade, late notification, quota cap, cold start, and peak load. Conditional billing covers sandbox receipt, restore, duplicate and reordered events, refund and expiry, and consistent cross-client rights. Exercise applicable keyboard, touch, back, focus, text scaling, reduced motion, and mute.

Measure startup and latency p50, p95, and p99 where relevant, memory, storage growth, network and cost, and background work. Derive thresholds from the audience and product outcome. Track compile, emulator and simulator, browser E2E, physical device, and live service proofs separately.

## 6. Hand off explicit dependencies

Provide specifications, rule fixtures, source and build, lockfiles and config, editable assets and rights, migrations and recovery, attempts, assembly proof, and open gates. Verify actual commands and paths. Give independent QA raw inputs and outputs without suggesting its verdict. Carry forward unchanged proofs with dependency justification and reopen only affected scope after an intent, input, model, or toolchain change.

Record actual Android, iOS, web, and release evidence separately from recipes, valid JSON, and unit tests. For pending or blocked items give an owner, environment, and exact next action.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show the working accepted slice or change, technology choices under actual constraints, exact diff or build, and relevant proof. Distinguish executed work, inherited decisions, and future results with due gates. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review integration, correctness, changed risks, and alignment with accepted design and specification. Inspect raw inputs for omitted requirements. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve project context, approvals, and unaffected results.
