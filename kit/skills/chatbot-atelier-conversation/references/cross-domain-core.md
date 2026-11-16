# End-to-end execution model 2.3.0

Determine applicability, analyze the task, formalize rules, produce the result, verify it, and hand it to the appropriate owner.

## Boundaries and authority

Each project defines its own domain rules, criteria, team and production methods. Trace the current user intent and permissions through project requirements and decisions, domain model, specifications and source, integrated result and observed evidence. Preserve one project-owned authoritative registry. Use this format as a projection where useful and retain source, decision, version and hash references.

Choose local, feature, critical or stage by impact. Describe the real dependencies in sufficient detail. A small document task usually needs no server, retrieval, background job or validator. These work-scope names are for implementers.

## Initial analysis and applicability

1. Recover the user, problem, current alternative, outcome and first and recurring value. Consider whether a new product or agent is needed.
2. Establish domain, terms, units, system boundaries, users, roles, resources, data, region and platform from actual sources. Read primary documentation, standards and strong alternatives. State the verified coverage.
3. Record musts, preferences, assumptions, unknowns, rejected tradeoffs and owner decisions separately. For each requirement give ID, source, priority, owner, receiver, artifact, due gate, positive and negative checks and the required evidence.
4. Classify systems required, conditional, not_applicable or pending. Give a reason and reopening condition for N/A. Missing tools or access leave an applicable task blocked.
5. Derive competence, tools, resources, costs and operations from active requirements. Check authority before new paid services or access. Retain valid permission.
6. Ask only about unknowns that materially change the decision, safety, quality or cost. Proceed with independent work and document safe reversible assumptions. Promote a hypothesis to a requirement only from a source or decision.

## Formal domain model

Define entities, identities, fields, types, units, ranges, authoritative source, lifetimes, readers, writers and invariants. A behavior rule defines prerequisites, commitment point, inputs and outputs, order, snapshot or live reads, precedence, rounding, precision, time bounds and effect. When applicable, bound randomness and non-determinism by scope, reproducibility or seed, distribution, limits and evaluation method. Temperature alone cannot guarantee reproducibility.

For each transition give initiator, guard, permitted action, data change, side effects, cancel, timeout, retry, compensation, terminal state and recovery. Distinguish accepted intent, performed local action, durable commit, external confirmation and user delivery. Repeated callbacks and webhooks retain the original privilege, debit or message result. Define domain identity, idempotency and retention and how to reconcile uncertainty.

Use specific reads, state changes, events or failures to explain interactions. Verify cross-system authorization, validation, data/cache/search, async, external services, UI/dialogue, accessibility, applicable billing, support, telemetry and recovery. The capability catalog records compatibility, dependencies, exclusions, versions, confirmed execution and extensions. Explain combination coverage by risk, including pairwise limits.

Numerical rules need worked examples, bounds, precision/rounding/tolerance and independent calculations. Product and financial projections need assumptions, sensitivity and sources. Preserve distributions and tails when they matter. For private data specify access, provenance, retention, export, deletion, recovery and protection against restoring erased data.

## Result maturity

**Draft:** scope, value, options, systems, risks and implementation outline with open gaps. **Design:** coherent intent, all active scenarios, exceptions, catalogs, data, UX and applicable operating/commercial model. Resolve material behavior before declaring the design complete. **Production handoff:** exact rules, schemas and contracts, source/export/import, fixtures, budgets, tasks and dependency graph, receiving owner and acceptance. Every tunable parameter has a baseline, range, owner and criterion.

A prototype can reduce risk before the full specification. A handoff still needs the complete applicable contract. Verify one representative end-to-end path on the actual target before scaling. A concept or mock describes its own visible qualities. Record the feasible production route and differences. Preserve approved originals unless a justified change calls for new material.

## Production records

| Record | Required details |
|---|---|
| Capability | Exact operation, provider and version, environment, inputs, parameters and limits, rights, costs, access, evidence scope and freshness. |
| Recipe | Inputs and hashes, owner and consumer, method, stages and parameters, editable source, export/import, acceptance, fallback and budget. |
| Transformation | Meaning, identity, units, scale, time, color, audio or rights to preserve or deliberately change. Verify semantics and format. |
| Attempt | Actual actor and tool version, inputs and parameters, time, job/idempotency IDs, resources used, outputs, outcome and diagnostic evidence. |
| Assembly | Exact components, version/build/config/environment, integrated scenario, expected versus observed results, failure/recovery and evidence. |

Distinguish catalog presence, usable API, actual call, output bytes, verified integration and direct device/chat observation. Verify that a required parameter was consumed. Reconcile an uncertain external job by provider ID before retrying.

Select tools and skills by operation, current primary documentation, actual access, compatibility and authority. For code verify architecture and versioned dependencies, conventions and static checks, invariant behavior, performance where measured, CI and release provenance. For data verify migrations, consistency and recovery. For media preserve source, edits and rights and check integration and actual listening or viewing. If an operation is unavailable, prepare an exact handoff to a capable environment and verify what comes back.

## Evidence, acceptance and change

Each claim has ID, exact scope, dependency versions and hashes, procedure and environment, expected versus actual, artifact or receipt, date and owner. Distinguish inspected source, calculation, assumption, local test, integration, independent review and actual human/device/provider observation. Accept each due requirement independently with evidence for that claim. A passing build establishes its own checks.

Changed input, model, rule, exporter, dependency, data or build invalidates transitive evidence. Include actual dependencies in semantic cache keys. Carry unchanged independent evidence only for verified scope. Ask the integrator to resolve unknown impact. Honor cancellation and deletion in cache and recovery.

`scripts/verify_depth.py PROJECT.json --gate design --root PROJECT_DIR` checks declared fields, links, coverage, scope and byte freshness. See `assets/depth/project.template.json` and `assets/depth/project.schema.json`. At production gate, an operation has `accepted_attempt_id`, an assembly binds accepted outputs in `component_files` and exact `artifacts`, and integration evidence binds matching inputs/files, build and environment. The check records declared structure and bytes with `quality_certified=false`. Verify the underlying observations separately. Generate a projection from authoritative runtime state when useful. A simple conversation does not require a new projection.

## Team and repair

Assign one integrator, working domain leads and executors, independent QA and reviewers matched to the risk. Use actual actor IDs and outputs. A single actor simulating several roles provides a self-check. Assign owned paths, inputs, consumer, completion checks, budget and dependencies. Keep one writer for each shared file, database, device, account or remote effect. Parallelize independent work.

Close a local repair with relevant verification. Group related defects. After two failures with the same method, change hypothesis or diagnostic approach. Retain mandatory criteria, actual evidence and accepted work. Reopen a closed decision only with a relevant change or new evidence.

## Handoff, installation and operations

Give the receiver intent, decisions, requirements and model, exact outputs and hashes, recipes, acceptance, authority, budget, jobs and uncertain effects, stop conditions and next action without relying on chat history. Work and Codex use the same domain rules. Verify access and capabilities separately for local Mac, production, platforms and other chats. Changing hosts needs its own observations.

Use one current declared output format. Reject other versions as machine inputs. Historical human documents can inform fresh analysis. Preserve approval and proof only for their actual matched scope. Plan product data versioning, backup, recovery and migrations separately. Skill updates leave code, data and production in their existing scope. A release binds exact artifact, config, schema, receipt, rollback, symbols or diagnostics and recovery. Finish the session with a checkpoint. Ongoing monitoring needs a verified authorized scheduler or service. Reconcile current state and affected dependencies on continuation.

## Primary method references

Use W3C PROV-DM for entity, activity, agent and derivation https://www.w3.org/TR/prov-dm/. Distinguish build and source provenance using SLSA 1.2 https://slsa.dev/spec/v1.2/provenance. NIST AI 600-1 informs context and risk evaluation for generative systems https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence. Use testable WCAG 2.2 criteria and representative scenarios for web accessibility https://www.w3.org/TR/WCAG22/. Treat these as sources for methods and verify actual conformance independently. Recorded source review date: 2026-11-03. Verify applicable version-specific documentation and tool scope for the current task.

## Stable invocation and observed versions

`name` in frontmatter is the stable machine identifier. Keep visible labels stable and obtain the actual version from release and source records. Data formats have independent identifiers. Use the unversioned skill name in prose, `@skill-name` in Work and `$skill-name` in Codex. The Work user selects the correct skill from the @ list. Confirm actual invocation separately from reference text.

Resolve the available skill by frontmatter or catalog before handoff. Read its current input, output and rules. Record resolved version, source hash, schema and actual receiver. Return incompatible inputs to their owner with an exact gap. When a capability is unavailable, use an included equivalent recipe or record the blocked step.

`@design-specialist-skills` or `$design-specialist-skills` turns an agreed specialist-skill concept into an executable method when needed. `@agent-foundry` or `$agent-foundry` owns agent construction. `@app-atelier-director` or `$app-atelier-director` owns applications. `@chatbot-atelier-director` or `$chatbot-atelier-director` owns chatbot product coordination. Invoke only needed components and keep existing analysis, authority and scope.

A composite product keeps one integrator for intent and shared REQ IDs. Each component has its ID, owner, agreed auth/data/API/event boundary, outputs and due evidence. Handoff binds source hashes, permissions, budget and stop conditions, pending jobs and receiving acceptance. The receiver verifies inputs, implements its assigned scope and returns exact artifact and evidence. Resolve incompatibilities at the shared contract and preserve adjacent scope.

## Applicability beyond built-in families

Use [adaptive work](adaptive-work.md) and [focused research and synthesis](research-and-synthesis.md) beyond current family names. Derive competence and proof from intent and risk. Keep shared methods, family defaults and current project policies separate. Treat examples as scoped and preserve the authoritative registry.
