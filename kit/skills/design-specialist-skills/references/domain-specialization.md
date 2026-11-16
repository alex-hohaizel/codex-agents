# Domain analysis without importing another domain's assumptions

This contract covers intent, the domain model, coverage, methods, team ownership, and readiness.

## 1. Turn expressed intent into verifiable outcomes

Accept ordinary descriptions, even when incomplete. Establish the problem, current workaround, recipient, action they take, consequence of error, and expected change. Distinguish the end user, operator, administrator, data owner, and approver. One person may fill several roles. Compare the current process, deterministic automation, a reusable skill, and an application before deciding whether the task calls for an agent. Explain the decision using the scenario and constraints.

Create a requirement record with an immutable ID, exact wording or source locator, interpretation, must/should/could priority, applicability, domain owner, artifact and consumer, observable acceptance, counterexample, due gate, required evidence type, and status or gap. Translate terms such as “high quality,” “detailed,” and “best” into domain criteria and constraints. The owner sets any fixed quota for pages, roles, or features. Record rejected simplifications and examples of unacceptable results.

Classify open questions by consequence: product choice, missing fact, configuration, resource, or external authority. Ask only when the answer materially changes the result, required access, cost, or an irreversible effect. State a reversible local assumption and continue independent work while a critical answer is pending. Retain the owner's existing approvals.

## 2. Model the domain explicitly

Identify entities and their definition and instance IDs, roles and rights, owners and trust boundaries, facts and assumptions, external observations, and vocabulary and units. For each mutable field, define its type, range, unit, source of truth, permitted writers, consistency group, commit/restore/reset behavior, retention and deletion, migration and merge, and failure semantics. Document who owns the state at runtime.

For a process, describe its initial and terminal states, commands and events, preconditions and guards, transition ordering, atomicity and commit points, cancellation, retries and timeouts, idempotency identity, concurrency, compensation, and recovery. If the model has no persistent state, explain that property. Resolve ambiguous automation into a trigger, rule, effect, and observable acknowledgment.

For calculations and transformations, define input types, units, order, capture time, rounding or tolerance, bounds, random distributions and seed support, output, and the test oracle. Label probabilistic scores as estimates. For AI behavior, specify deterministic constraints, probabilistic output, confidence and abstention, fallback, and the owner accountable for the consequence. Every mandatory constraint must pass independently of aggregate scores.

For each system dependency, name its source and output, target and input, interface version, transformation, allowed states, error handling, and consumer check. Keep the graph sparse. Review critical dependencies against the actual domain to find missing relationships that the declared graph cannot detect.

## 3. Establish applicability, catalogue, and scenarios

Map capabilities, data, interfaces, integrations, evidence, and production operations to `applicable`, `absent_by_design`, `blocked`, or `pending`. Record the domain rationale and decision for N/A. Missing access or tooling is a blocker. Extend the initial catalogue when a supported future case falls outside its taxonomy.

Where applicable, cover first use, normal use, peak or bulk use, empty and boundary data, partial results, failures, cancellation, duplicate callbacks, reruns, pausing and resuming cold, version changes, export and deletion, and service shutdown. Each scenario needs exact input and starting state, an action, the expected transition or result, acceptance criteria, and recovery. For a large input space, define the grammar, constraints, boundary/property/combinatorial coverage, and explicitly untested combinations. Provide the complete applicable catalogue or its derivation rule alongside examples.

Derive a variant matrix from the intent, using relevant locales, platforms, channels, permission models, and scale. Verify compatibility, dependencies, forbidden combinations, and an actual opportunity to use each capability. Add functionality only when it serves the intended outcome.

## 4. Select domain methods and evidence

For each material method, record source ID, URL, version and verification date, the exact claim and its applicability limit, alternatives, rationale, adaptation, and a validating probe. Prefer official specifications, provider documentation, research, and relevant standards for technical claims. Confirm actual support before relying on product marketing. Check current SDKs, APIs, models, prices, and policies when binding them to a real task. Compare models against the task's criteria before making a quality claim.

Review the inputs, outputs, scope, and policies of available specialist skills before invoking them. Record actual invocations. Add RAG, a workflow engine, an agent framework, a vector database, multimodality, or a server only for an established retrieval, state, or integration requirement. Specify the owner, contract, cost, evaluation, and operational consequences of each addition.

Ground causal rules, provenance, and production procedures in the actual domain. Formal references include W3C SCXML https://www.w3.org/TR/scxml/ for state and event semantics without an XML requirement, W3C PROV-DM https://www.w3.org/TR/prov-dm/ for provenance records, and SLSA provenance https://slsa.dev/spec/v1.2/provenance for build lineage. Confirm the current version-specific text and apply evidence from the target skill independently of these references.

## 5. Define the team that performs the work

Assign every required output an accountable owner, competence, reviewer, consumer, inputs, outputs, owned paths and resources, and budget. The technical lead decomposes work and integrates actual artifacts. Use one writer for a shared source, account, device, or scene. Independent paths may still affect the same remote resource. Use distinct authors and reviewers for critical findings, and label an unlaunched role as a perspective or self-check.

Size the team to match genuinely independent artifacts and expertise. Convene a review group only for a material decision, conflict, or stage acceptance. Record actual actor IDs and outputs after execution. Before admitting work, verify the input hashes, capabilities, permissions, resources, budget, consumer interface, and acceptance criteria. A change invalidates only findings that depend on the affected node.

## 6. Define readiness

A sketch records the problem, promise, directions, risks, and next route, with its provisional status. A complete specification defines the entire accepted scope, applicability, causal rules, and feasible production routes. A production handoff adds an exact baseline, schemas and interfaces, fixtures and oracles, executable procedures, permissions, budgets, a task dependency graph, and acceptance by a receiver starting without the prior conversation. Release has separate evidence.

Resolve any uncertainty that otherwise forces downstream teams to invent behavior. A tunable parameter needs a baseline, range, owner, experiment, acceptance criterion, and affected requirement IDs. Accept a representative end-to-end result in the actual target environment before scaling production. Record structural validation, semantic review, actual integration, device testing, human testing, and production observation separately.

## Preserve intent when the owner supplies examples

Before specializing, map raw sources to obligations, questions, and priorities. Distinguish illustrative examples, facts, hypotheses, and recommendations. An independent reviewer with relevant competence checks material scope against the primary sources. Show which requirements are addressed, inherited, or open with an owner and due stage. Choose scope, depth, and team independently for a quick repair, a large defined task, or unfamiliar work using `adaptive-work.md`. Give each applicable conceptual, language, design, architecture, technical, and operational result its own acceptance criteria.
