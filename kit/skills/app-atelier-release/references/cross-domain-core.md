# Cross-domain execution model 2.3.0

This guide covers applicability, analysis, formal modeling, production, evidence, team responsibilities and handoff.

## Scope and authority

Each project has its own domain rules, criteria, team and production paths. Connect current user intent and permission to requirements and decisions, the domain model, specifications and source, the integrated result, and actual evidence. Use one authoritative project-owned register. The model may project that register into a review artifact. Preserve source, decision, version and hash references.

Choose local, feature, critical or stage scope by impact. Detail should resolve dependencies. A simple document needs no server, retrieval infrastructure, recurring jobs or programmatic validator. These work modes describe internal organization, not product UI.

## Initial analysis and applicability

1. Recover the user, need, current alternative, useful outcome, first and repeat value. Establish whether a new product or agent is needed.
2. Establish domain concepts, units, boundaries, users, roles, resources, data and countries/platforms from actual sources. Read primary docs and standards and compare strong alternatives. Define the coverage boundary before claiming «абсолютно всі» practices.
3. Separate musts, shoulds, assumptions, unknowns, rejected simplifications and owner decisions. Each requirement has ID, source, priority, owner, consumer, artifact, due gate, positive and negative oracle, and required evidence type.
4. Classify systems as required, conditional, not_applicable or pending. Record the reason and reopen condition for N/A. A missing tool or access blocks dependent work.
5. Derive competencies, tools, resources, expense and operations from active requirements. New spending or access requires authorization. Reuse current authorization for unchanged work.
6. Clarify an unknown only when it changes an important decision, safety, quality or cost. Continue independent work. Record an assumption for a secondary reversible decision. A research hypothesis becomes a requirement only with a source or decision.

## Formal domain model

For active systems define entities, identities, fields, types, units, allowed ranges, authority, lifetime, readers and writers, and invariants. For behavior define preconditions, commit point, input/output, ordering, snapshot or current read, priorities, rounding, precision, time bounds and effect. For non-determinism specify scope, reproducibility or seed where needed, distribution, bounds and evaluation. LLM temperature does not guarantee repeatability.

Model transitions with initiator, guard, permitted action, data change, side effect, cancel, timeout, retry, compensation, terminal state and recovery. Distinguish accepted intent, locally executed action, durable commit, external confirmation and delivery to the user. A duplicate callback or webhook must not issue a second entitlement, spend or message. Specify domain identity, idempotency, retention and reconciliation of unknown outcomes.

Specify which read, write, event or failure connects systems. Check cross-system authorization, validation, data/cache/retrieval, concurrency, external services, UI or conversation, accessibility, billing as applicable, support, telemetry and recovery. The capability catalog includes compatibility, dependencies, exclusions, versions, rollout scope and extension paths. Select combination coverage by risk. Pairwise is not exhaustive.

For numerical rules, provide worked examples, intermediate values, boundaries, precision, rounding and tolerances, and an independent calculation. Give assumptions, sensitivities and sources for product and financial forecasts. Account for distributions and tails when averages miss them. For private data define access, provenance, retention, export/delete, recovery and barriers to restoring deleted data from backups.

## Maturity and depth

**Draft** describes scope, value, alternatives, systems, risks, a possible implementation and open gaps. **Design** is a coherent concept with every active journey, exception, catalog, dataset, UX, and applicable operations and commercial logic. Do not hide unresolved core behavior as TBD. **Production handoff** supplies exact rules, schemas and contracts, source/export/import, fixtures, budgets, dependency graph, consumers and acceptance. A tunable parameter includes a baseline, range, owner and criterion, so an implementer has the promised behavior.

An early risk-reduction prototype does not close the specification. Verify a representative end-to-end slice in the target environment before creating a large catalog or scaling. A concept image or mock does not prove feasibility. Record requirements, the available production path and assessed deviations. Preserve exact accepted originals during repair.

## Production unit

Each necessary operation has five related records.

| Record | Required content |
| --- | --- |
| Capability | Exact operation, provider and version, environment, input, parameters, limits, rights, cost, availability, scope and freshness of proof |
| Recipe | Inputs and hashes, owner and consumer, method, steps and parameters, editable outputs, export/import, acceptance, fallback and budget |
| Transformation | Semantics, identities, units, scale, timing, color, sound or rights preserved or deliberately changed, with verification beyond the file format |
| Attempt | Actual actor, version, inputs and parameters, time, job and idempotency IDs, resource use, outputs, outcome and diagnostics |
| Assembly | Exact components, version/build/config/environment, integrated scenario, expected and actual result, failure/recovery and evidence |

Separately observe catalog entry, available API, actual invocation, received bytes, integrated result and target device or chat experience. Verify that the consumer uses each critical parameter. Descriptors and schemas can differ from behavior. Reconcile an unknown external job by provider ID before a repeat.

Choose tools and skills for the exact operation using current official docs, actual availability, compatibility and rights. Popular libraries alone are not quality evidence. For code document boundaries, versions and dependencies, style/static checks, invariant tests, measured profiling, CI and release provenance. For data verify migration, consistency and backup/restore. For media verify source, editability, license, runtime integration and actual listening or viewing. Hand missing operations to a capable environment with precise steps and verify the return.

## Evidence, acceptance and changes

Each claim has ID, exact scope and dependency versions or hashes, method, environment, expected and observed result, file or receipt, date and owner. Distinguish source fact, calculation, assumption, local test, integration, independent review, and human, device or external observation. A passing build does not prove UX, natural conversation, all security paths or demand. Accept each due must independently. An average score cannot compensate for a failure.

Changes in inputs, models, rules, exporters, dependencies, data or builds invalidate transitive evidence. Use actual dependencies in the semantic cache key and carry unchanged independent evidence within its verified scope. The integrator analyzes unknown dependencies. Honor cancellation and data deletion in caching and recovery.

`scripts/verify_depth.py PROJECT.json --gate design --root PROJECT_DIR` checks declared fields, links, coverage, stage scope and freshness of bytes. Use `assets/depth/project.template.json` and `assets/depth/project.schema.json`. At the production gate, the operation has `accepted_attempt_id`. The assembly lists `component_files` from accepted outputs and exact `artifacts`. Integration evidence binds those inputs and files, build and environment. This validates the declared assembly against bytes without authenticating the reported observation. A structural pass does not prove domain completion, and `quality_certified=false` remains explicit. Keep records in the current runtime and generate a review projection when useful. Simple conversations need no separate projection.

## Team and repair

Use one integrator, actual domain leads and implementers, independent QA, and a review group only where needed. Derive the team from expertise, artifacts and risk. Record actual actor IDs and outputs. Role-playing the same author does not supply independence. Give each implementer owned paths, inputs, consumer, definition of done, caps and dependencies. Assign one writer to a shared file, database, device, account or external effect and parallelize independent work.

Complete a local repair with the applicable check. Group related issues and change the hypothesis after two equivalent failed repairs. Keep musts and accepted work intact and use only actual evidence.

## Handoff, installation and operations

Give a cold receiver intent, decisions, requirements, model, exact outputs and hashes, recipes, acceptance, permissions, budget, jobs and unknown outcomes, stop and next action without reliance on chat history. Work and Codex share domain rules and have separate capability checks. Actual connections and permissions determine access to Mac, production, communication platforms and other chat context. Moving environments does not strengthen proof.

Create and check skill outputs in one declared current format. Reject other versions without automatic readers, converters or hidden fallback. An existing document may inform new work while its prior acceptance stays tied to its original scope. Design product data versions, backup/restore and migrations for that product. Installing skills does not modify product source, data or deployment. Release binds exact artifact, config, schema and receipt, rollback, symbols, diagnostics and recovery. Save a checkpoint after a session. Recurring monitoring requires an authorized running scheduler or service. On continuation, verify current state and affected dependencies.

## Primary method references

Use W3C PROV-DM for entity/activity/agent and derivation relationships: https://www.w3.org/TR/prov-dm/. For build and source provenance see SLSA 1.2: https://slsa.dev/spec/v1.2/provenance. These references do not certify the package. NIST AI 600-1 helps scope generative-AI risks and evaluation: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence. It does not approve a system automatically. Select testable web accessibility criteria and journeys from WCAG 2.2: https://www.w3.org/TR/WCAG22/. A citation does not establish conformance. Source review date: 2026-11-03. Check the exact documentation version and current tool limits before use.

## Stable invocation and displayed versions

The frontmatter `name` is the immutable machine identifier. Where a UI surfaces a toolkit release, use a current release record and preserve separate data format IDs. Use names without numeric suffixes in prose. Invoke with stable `@skill-name` in Work and `$skill-name` in Codex. Select the actual skill in Work's @ picker. Text mentioning it does not establish invocation.

Before handoff, resolve an available current skill by frontmatter or catalog and read its input, output, rules and contract. Record resolved version, source hash, accepted schema and actual consumer in the execution record. A stable name does not guarantee protocol compatibility. Return an exact gap for an incompatible input. Use an included equivalent procedure or keep dependent work blocked when the required tool is unavailable.

When a new specialized skill is required, `@design-specialist-skills` / `$design-specialist-skills` converts the accepted plan into an executable method. `@agent-foundry` / `$agent-foundry` owns agent products, `@app-atelier-director` / `$app-atelier-director` owns apps, and `@chatbot-atelier-director` / `$chatbot-atelier-director` owns chatbots. Activate only the needed components and roles. A reference alone does not open another review cycle or product scope.

Several components can share a product. One integrator owns intent and common REQ IDs. Each component has an ID, owner, accepted auth/data/API/event boundaries, outputs and due proof. Pass the current component handoff, source hashes, permissions, budget, stop, open jobs and consumer acceptance. The receiver verifies it, executes its assignment and returns exact evidence. Resolve incompatibilities in the shared contract.

## General applicability in 5.0

Use the [adaptive contract](adaptive-work.md) and [scoped research capabilities](research-and-synthesis.md) beyond current family names. Choose sufficient skills and evidence from the actual intent and risk. Keep the general method, family defaults and current product policy separate. An example does not establish a global rule. Use the existing project registry.
