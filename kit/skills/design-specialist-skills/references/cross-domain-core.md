# Cross-domain execution contract 2.3.0

## Scope and authority

Derive each project's rules, criteria, team, and production process from its own domain. Trace current user intent and authority to project requirements and decisions, model, specifications and sources, integrated result, and observed evidence. Maintain one authoritative project registry. Use this format as a projection where useful. Record source, decision, version, and hash references.

Choose local, feature, critical, or stage scope based on impact. Include only the detail that resolves actual dependencies. A straightforward document may need no server, RAG, background jobs, or validator. The modes organize agent work and impose no product interface.

## Analysis and applicability

1. Recover the user, problem, current approach, goal, first value, and recurring value. Determine whether a new product or agent helps.
2. Establish domain, terms and units, system boundaries, users, roles, resources, data, countries, and platforms from actual sources. Identify current primary documentation, relevant standards, and strong alternatives. Define the coverage boundary of each recommendation.
3. Separate musts, shoulds, assumptions, unknowns, rejected simplifications, and owner choices. For each requirement, record ID, source, priority, owner, recipient, artifact, due gate, positive and negative oracle, and required evidence type.
4. Derive a `required`/`conditional`/`not_applicable`/`pending` system matrix. Record why a case is N/A and when it would reopen. Missing tools or access remain blocked.
5. Derive competences, tools, resources, costs, and operations from active requirements. Confirm authority for new spending and access and retain existing authorization.
6. Clarify only unknowns that change the result, safety, quality, cost, or a material decision. Continue independent work and state reversible minor assumptions. A hypothesis enters the requirements through an authoritative source or an actual decision.

## Formal domain model

For every active system, define entities, identities, fields, types, units, ranges, authority, lifetimes, readers and writers, and invariants. Specify behavior with prerequisites, commitment point, inputs, outputs, order, snapshot and current reads, priorities, rounding, precision, time, and effects. Define the scope of randomness and nondeterminism, reproducibility and seeds as needed, distributions, bounds, and evaluation. Validate reproducibility independently of LLM temperature.

Capture state as transitions with initiator, guard, allowed action, data changes, effects, cancellation, timeout, retry, compensation, terminal state, and recovery. Distinguish accepted intent, local action, durable commit, external acknowledgment, and actual delivery. A duplicate callback or webhook must not grant rights, consume resources, or send a message twice. Specify domain idempotency identity, retention, and unknown-outcome reconciliation.

Map system dependencies to concrete reads, writes, events, or failures. Keep the graph sparse. Check shared boundaries in authorization, validation, data and cache and retrieval, asynchronous work, external providers, user interfaces and dialogue, accessibility, applicable billing, support, telemetry, and recovery. For the capability catalogue define compatibility, dependencies, exclusions, versions, launch scope, and expansion. Choose combinatorial coverage by risk and document its limits.

Provide calculation examples, including intermediate results, boundaries, precision, rounding and tolerances, and independent recomputation. Projections need assumptions, sensitivity, and sources. Include distributions and tails where they change the interpretation. For private data, define access, provenance, retention, export and deletion, recovery, and prevention of resurrection from backup.

## Maturity and depth

- **Draft.** Scope, value, alternatives, systems, risks, implementation sketch, and explicit gaps.
- **Design.** Coherent accepted concept with applicable scenarios and exceptions, catalogues, data, experience, operation, and business model. Settle required behavior.
- **Production handoff.** Exact rules, schemas, interfaces, source/export/import, fixtures, budgets, tasks and dependencies, consumers, and acceptance. A tunable parameter needs a baseline, range, owner, and criterion so downstream work can follow the defined behavior.

A prototype may retire a specific risk before the full specification, while the handoff gate remains open. Verify a representative end-to-end slice in the target environment before constructing a large catalogue or scaling. Record visible requirements, feasible production routes, and assessed deviations. Preserve exact accepted originals.

## Production records

| Record | Required contents |
|---|---|
| Capability | Exact operation, provider and version, environment, inputs, parameters, limits, rights, cost, availability, proof scope, and freshness |
| Recipe | Inputs and hashes, owner and consumer, method, stages and parameters, editable outputs, export and import, acceptance, fallback, and budget |
| Transformation | Domain meaning, identity, units, scale, timing, color, audio, and rights retained or explicitly changed, with semantic verification |
| Attempt | Actual actor, version, inputs and parameters, time, job and idempotency IDs, resources consumed, outputs, result, and diagnostics |
| Assembly | Exact components, version/build/configuration/environment, integrated scenario, expected and actual result, failure and recovery, and evidence |

Track the catalogue, available API, actual invocation, returned bytes, integration, and observation independently. Verify actual consumption of critical parameters, since schemas and descriptors can differ from implementation. Reconcile unknown external effects using the provider identifier before retrying.

Select tools and skills based on the operation, official documentation, actual access, compatibility, and authority. For code, define justified boundaries, versions and dependencies, static and style checks, invariant tests, measured profiling, CI, and release provenance. For data, define migration, consistency, backup, and restoration. For media, track source, editability, licensing, runtime integration, and actual viewing or listening. When an operation is unavailable, hand off the exact operation to a capable environment and verify the result.

## Evidence, acceptance, and change

Each claim records ID, exact scope, dependency versions and hashes, method and environment, expected and observed result, evidence file or receipt, date, and owner. Separate source fact, calculation, assumption, local test, integration, independent review, and human/device/external observation. An accepted build establishes only its observed results. Evaluate each due must individually.

Changes to input, model, rule, exporter, dependency, data, or build invalidate transitive evidence. Use actual dependencies in a semantic cache key. Document the unaffected scope before reusing evidence. Have the integrator investigate uncertain dependencies. Honor cancellation and deletion across caches and restoration.

`scripts/verify_depth.py PROJECT.json --gate design --root PROJECT_DIR` checks declared fields, references, coverage, stage scope, and byte freshness. The template is `assets/depth/project.template.json` and the schema is `assets/depth/project.schema.json`. At the production gate each operation sets `accepted_attempt_id`. Assembly records `component_files` from accepted outputs and exact `artifacts`. Integration evidence pins applicable inputs and files, build, and environment. The tool checks stated composition against observed bytes. Verify the actual observations separately. `quality_certified=false` is explicit. Project data may remain in its existing runtime and generate a projection when needed. A straightforward conversation needs no additional file.

## Team and repair

Assign one integrator, working domain leads and producers, independent QA, and a review group only for applicable decisions. Size the team from competence, artifacts, and risk. Record actual actor IDs and outputs. Treat role-play within one actor as self-review. Give each actor owned paths, inputs, consumer, completion requirements, budget, and dependencies. Use one writer per shared file, database, device, account, or remote effect. Parallelize disjoint work.

Verify a narrow repair within its scope. Bundle related defects. After two identical failures, change the diagnosis or method. Preserve musts, report actual evidence, and reopen accepted scope only when there is a relevant change or newly observed defect.

## Handoff, installation, and operation

Give a fresh receiver the intent, decisions, requirements and model, exact outputs and hashes, recipes, acceptance, permissions, budget, jobs and unknown effects, stop point, and next action without needing the chat history. Apply the same domain rules in Work and Codex. Verify each host's tools, Mac or production access, communication platforms, and chat permissions independently. Keep evidence bound to the original environment.

Produce and validate skill results in the declared current format. Reject unsupported versions without automatic conversion or fallback. Use prior human documents as source evidence and revalidate results against current scope. Plan the product's own data versioning, backup and restore, and migrations separately. Skill updates preserve product code, data, and production state. Release pins the exact artifact, configuration, schema, receipt, rollback, symbols, diagnostics, and recovery. Close with a checkpoint. Record continuous monitoring only for an authorized scheduler or service running in fact. Reconcile current state and affected dependencies on resumption.

## Primary method references

Use entity, activity, agent, and derivation to model provenance. [W3C PROV-DM](https://www.w3.org/TR/prov-dm/)

Distinguish build and source provenance. [SLSA 1.2 provenance](https://slsa.dev/spec/v1.2/provenance)

For generative systems, use the applicable context and risk methods. [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

For accessibility, select verifiable web criteria and actual test scenarios. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)

The original reference review is dated 2026-11-03. Verify the current version and applicability for each real task and establish conformance through its evidence.

## Stable selectors and version metadata

Keep frontmatter `name` as the stable machine ID. Read current versions from release and source metadata, and distinguish data format identifiers. Use the ordinary skill name in prose, `@skill-name` in Work, and `$skill-name` in Codex. In Work, verify the actual picker selection and invocation.

Before handing off, resolve the active skill by frontmatter and the actual host catalogue, then read its inputs, outputs, rules, and contract. Record resolved version, source hash, accepted schema, and actual recipient. Return an incompatible input to its author with the exact mismatch. Use a bundled equivalent when permitted, otherwise mark the missing capability blocked. Record the operation actually performed.

Use `@design-specialist-skills` or `$design-specialist-skills` for a reusable specialized workflow when needed, `@agent-foundry` or `$agent-foundry` for an agent product, `@app-atelier-director` or `$app-atelier-director` for an app, and `@chatbot-atelier-director` or `$chatbot-atelier-director` for a chatbot. Activate only applicable components and reuse accepted research and approval when those still bind the task.

For a compound product, a single integrator owns product intent and common requirement IDs. Each component has an ID, owner, accepted authorization and data and API and event boundaries, outputs, and due evidence. Transfer a current component handoff with source hashes, permissions, budget and stop, unfinished jobs, and acceptance. The recipient verifies and returns its exact outputs and proof. Resolve incompatibilities in the shared contract with its owner.

## Apply the method across domains

Use the [adaptive contract](adaptive-work.md) and [research competences](research-and-synthesis.md) in applicable tasks beyond named families. Derive evidence and competence from intent and risk. Keep shared methods, family defaults, and project policy distinct. Reuse the authoritative project registry.
