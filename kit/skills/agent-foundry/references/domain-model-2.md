# Agent Foundry domain model

Contents: maturity → discovery → rules → state → interactions → acceptance → inheritance. Read before the passport, after a material domain change, and before production handoff. Adapt shared methods to the actual domain; do not import game entities or a fixed feature catalog.

## 1. Three levels, one lineage

**M0, exploratory sketch:** need, participants, possible result, value, core systems and risks. Separate untested examples from accepted concepts. For a distinguishing promise, identify a feasible route and the probe that is due. M0 does not establish that the agent is designed.

**M1, complete passport for choice and approval:** all applicable competencies, primary and peripheral scenarios, capabilities and variants, dependencies, data, rights, tools, quality, production capacity, failure and recovery rules, and support. Define the core behavior and benefit. Future numeric tuning has a method, owner and due gate. Give every proposed complete option the same M1 depth; avoid comparing one fully designed favorite to deliberately weak sketches.

**M2, exact production handoff:** accepted M1, complete rules, tables and formats, output catalog or finite grammar, inputs, baseline, interfaces and errors, operations and recipes, fixtures and acceptance. The recipient should not have to invent missing domain behavior. Accept a representative end-to-end result in the target environment before wider production.

Supported factory blueprint and state remain `1.0.0`, with a related `foundry-depth/2` domain model. These are separate current protocols, not generic readers for prior outputs. Reject unsupported formats. If a current record is needed, build it from current sources and preserve the earlier result's separate readiness status.

## 2. Derive scope from the assignment

For each competency establish actors and roles; entities and definition, instance and revision distinctions; lifecycle; data inputs and outputs; events; source of truth; permissions; resources; time boundaries; constraints; conflicts; errors; and verification. Include applicable creation, change, read, search, removal, cancellation, restart, handoff, completion, recovery, and external service loss scenarios.

Make a domain-specific system map. Each system has `id, purpose, applicability, rationale, owner, input, output, reads, writes, produces_events, consumes_events, invariants, dependencies, acceptance`. Analyze completeness directly. Add an interaction when it names a causal read, change or consequence. Missing mention requires analysis; unavailable tools are blockers; intentional inapplicability needs a scoped reason.

For industry practices, define the property and method, find the current primary source and version, separate documentation from adaptation, and compare options against the same requirements. DDD, CQRS, RAG, microservices, and FSM are options. Choose the sufficient method for risk, data, scale and team ability. Do not enable extra libraries, services or paid models by default.

## 3. Formalize behavior

Give each rule a stable ID and source, actor and target, preconditions, exact inputs, types, units, ranges and nullability, read timing, ordered steps, modifiers and priorities, output and effect, duration, cancellation, replay, conflicts, negative case, oracle and proof due. Make terms such as "correct," "high quality," "optimal," and "reasonable" observable.

For numeric rules specify order, precision, rounding, clamping, overflow, currency and units, time zone, calendar and monotonic clock, inclusive and exclusive boundaries, and tie breaks. For probability or generation define distribution support, randomness scope, correlations, method of evaluation, permitted variance, and boundary examples. A mean does not prove a percentile or an individual result. Do not assume seed support.

For conflicting events define the sequence across receipt, validation, authorization, normalization, calculation, logical apply, user feedback, and durable record or receipt at the appropriate boundary. The actual domain determines its transaction and causal order. Immediate UI feedback must not claim an unconfirmed effect completed. Define acceptance, execution, durable commit, and user confirmation separately.

Deduplication needs a domain action identity, actor, target, scope, validity window, restart policy, and verification source. Repeated callbacks or retries for the same intent must not create additional effects. Bound recursion, event cascades, fan-out, token, time and cost loops, and specify completion and escalation.

## 4. Model state and failure

For every state field define type, default, valid range, authority, persistence scope, consistency group, version and migration, retention and deletion, and recovery oracle. Distinguish transient presentation, session and derived cache, durable domain state, external provider state, and private data. Rebuild derived state only from current permitted sources.

Use lifecycle states as applicable: normal/partial/blocked/degraded/cancel_pending/cancelled/failed/recovering/completed. For each transition define trigger, guard, allowed actions, resources, cleanup, outstanding jobs, compensation, retained and lost data, replay or rollback, and user signal. Unknown outcome differs from failed. Cancellation requested differs from cancelled.

Define what survives a crash, which actions can replay, how to reconcile pending operations, how to detect a stale writer, and how to check partial output and duplicates. Inspect read-only status first and require real receipts. Recovery from backup respects tombstones, revoked authority, and schema compatibility. Removing a local file does not establish deletion from remote storage, caches or copies.

## 5. Trace requirements to results

`requirement → contract/rule → operation → recipe → transformation → attempt → output → consumer assembly → evidence → closure`. Label each edge with what is read, transformed, or confirmed and what changes. An artifact may satisfy several requirements; keep a verdict for each. The owner maintains dependency closure using explicit links.

For each transformation name source and target formats, IDs, encoding and locale, units, scale, time base, precision, schema semantics, rights and audience, preserved invariants, intentional losses, and validator. Text to structured data to API can lose units, recipients or ordering; JSON parsing does not detect semantic loss. For media distinguish source, editable master, derived export, and runtime consumption. A generated picture does not prove working UI or editable 3D assets.

For a material tool parameter bind requirement → actual schema field → supported operation → bound value → evidence that it was consumed. Asking for a property in a prompt does not prove support. An unsupported requirement blocks the dependent operation or calls for a justified alternative. A weighted score cannot offset it.

## 6. Team and inheritance

Derive the team from actual contracts, artifacts, and risks. The technical lead produces or integrates work. A specialist needs competency, exact inputs, owned paths and resources, output and consumer, completion criteria, budget and stop. Give reviewers original artifacts. The author cannot independently review their own work. Give a shared provider, account, database, device or export one writer or an explicit compatible write protocol; separate files do not isolate an external resource.

Bundle the necessary versioned core, specialized domain contract, production and evaluation obligations, and actual recipes and fixtures in each generated module. Preserve shared stable IDs and explicit local paths. The profile names what applies, what was adapted, where it lives, and how it was checked. Inheritance alone does not close a missing required component.

Use `check_foundry_depth.py` to check the exact model, modules and evidence references, and run the shared `verify_depth.py` according to its current help. These are structural checks. Domain completeness, authentic consent, generated agent quality and real outcomes each need their own independent evidence. For a handoff independent of chat history, give a fresh recipient the passport, rules, recipes and everything needed to execute an authorized example.
