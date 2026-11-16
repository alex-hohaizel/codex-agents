# Passport, components, and architecture of a generated agent

Read this after researching intent and before approving, building, or materially changing an agent. Blueprint forms and runtime records live in the assets. Read the actual help for scripts/foundry.py before issuing commands. This document defines what the records must describe; their schemas define the machine format.

Contents: units of architecture → passport → team → dependencies → approval → verification and change.

## Units of architecture

One public agent provides one clear point of contact and an accountable integrator. The number of skills, phases, specialists, and tools can vary independently. A skill may lead several phases, and a phase may use several capabilities. Package count does not determine process count or the number of independent checks.

Compare a cohesive design with a justified split. Choose a family when artifacts, expertise, environments, access, acceptance points, or independently repeatable work differ. Choose a compact module for a cohesive task with related expertise. Do not set a minimum number of roles or phases for appearance.

Every claimed capability needs a tangible result and a route to it. Naming an expert, plugin, or method does not implement it. For each automation specify the operation, available tool, access, verification, and recovery. Provide a specific manual return path for unavailable operations.

## Complete, readable passport

Before building the target agent, show the user a versioned passport and component list. The readable document and the structured blueprint must describe the same scope.

1. **Mission and value:** who it helps, what it delivers, and where to see the result.
2. **Boundaries:** included and excluded work, available materials and constraints, and where the agent's competence ends.
3. **Capability catalog:** actions, scenarios, exceptions, results, interactions, quality, and acceptance for every capability.
4. **Requirements across phases:** the user's exact requirements and priorities, their sources and dependencies, and the evidence due at each relevant phase.
5. **Workflow:** domain-specific phase graph with inputs, outputs, gates, parallel work, targeted returns, pause and resume.
6. **Skill architecture:** one public entry, actual modules, triggers, shared contracts, and separate dependencies.
7. **Team:** expertise, artifact ownership, accountability, independent QA, and triggers for additional review.
8. **Tools:** sufficient tools, CLI and connections; installed and unverified capabilities, alternatives, rights, licenses, and costs.
9. **Environments:** what executes where, prerequisites, isolation, settings, version control, and exact transitions.
10. **Data and knowledge:** source of truth, project memory, provenance, retrieval, freshness, deletion and revocation, and access.
11. **Human experience:** language, clarity, interaction character and design, required channels, accessibility, state explanation, and recovery.
12. **Resources and value:** budget, ongoing costs, production capacity, and a commercial route where applicable.
13. **External effects:** allowed classes, exact separate decisions, data and recipients, user-only steps, and unknown outcomes.
14. **Evidence and QA:** tests, scenarios, independence, actual observations, performance, and domain-relevant negative cases.
15. **Packages and launch:** actual files, installation in Work or Codex, first verified useful action, operating instructions, and handoff.
16. **Support:** monitoring, defects, new capabilities, agent and product updates, rollback, and retirement.
17. **Risks and unknowns:** construction blockers, defined deferrals, options, and review triggers.
18. **Exact approval subject:** version, hash, scope, the final component list, and what approval authorizes.

For every capability, bind source and intent → capability → owner → phase → component → artifact → test and evidence → acceptance. Explain why something does not apply. Record critical unknowns explicitly. Names, counts, and component paths must agree across documents and the blueprint.

## Effective team and independent review

Derive expertise from artifacts, risks, and acceptance. One integrator owns intent, requirements, dependencies, and the result. The domain lead produces or integrates material, divides work, and accepts interfaces. Specialists receive bounded assignments. QA checks a concrete result and reports to the integrator independently of its author.

A task contract specifies requirement IDs, exact inputs and hashes, allowed paths, expected outputs, owner, interfaces, resource cap, stop condition, and completion check. Actual agent spawning, production accountability, and acceptance authority are separate relationships. Credit only roles that ran.

Combine adjacent responsibilities when workload and expertise permit. An author cannot serve as independent QA for their own artifact. A new independent opinion needs someone other than the author or previous reviewer. Use broader review for a material freeze, critical disagreement, or consequential option.

If subagents are unavailable, work sequentially. Record self-checks and missing independent acceptance separately. Message or role count does not add empirical evidence. Pick team size, model, and review rounds for the actual work.

## Execution and resource graph

Derive phases from the domain. Give each inputs, outputs, prerequisites, acceptance, blockers, and return paths. Keep a planned pass acyclic; a repair creates an explicit new pass over the affected branch.

Dependencies include user decisions, source versions, permissions, external service state, check results, knowledge, budget, and availability, as well as files. A shared change reopens transitively dependent checks. Explain why unchanged independent evidence remains valid.

Parallelize independent deliverables within real slot, resource, and access limits. Sequence shared mutations, admissions, migrations, and integration. Assign paths or isolated workspaces. A separate checkout does not isolate a shared database, account, or production effect.

Set resource boundaries for time, generations, storage, network, calls, and spend, and state when to change the diagnosis. Run inexpensive contract checks before costly production attempts. If an identical repair repeats without progress, change the diagnosis.

Start memory with versioned sources, IDs, structured or lexical retrieval, a dependency graph, and readable checkpoints. Add semantic retrieval, an SDK, workflow framework, remote tracing, or a separate service for a measured need with assessed cost, permissions, and verification. Technology names do not establish memory, autonomy, or correctness.

## Required approval gate

Finish analysis, passport, alternatives, and component list before requesting approval. Target skill creation and installation, and product execution, must wait for passport approval. Label any exploratory material or samples for consideration by their actual status.

Run structural and domain review on the current blueprint, then show what the user will receive, why this design fits, open questions, costs, access, and the exact next action. Resolve critical construction questions. Give permitted future decisions an owner and due gate.

Pin approval to the exact revision, sha256, scope, and actual affirmative response. A recommendation, populated JSON, prior approval of another version, silence, and elapsed time do not supply consent. A substantive passport change requires a decision on that change. Never substitute an approval record for the user's actual decision.

Verify the current build gate before every dependent build. Old green reports or copied manifest pins do not satisfy the gate. Explain blocking reasons by ID, what is missing, why it matters, what is ready, and the next step. Continue independent authorized preparation.

Passport approval authorizes construction of the described agent. A future product, publication, payment, data transfer, or ongoing monitoring uses its own current authorization.

Separate factory and execution sessions. Declare factory or project purpose at initialization; reinitialization must not replace the purpose of existing state. Work on the end result needs precise execution authority with blueprint hash, scope, and permitted phases. One actual response can expressly grant both construction and execution; record both scopes without asking again. Neither record grants external effects by itself.

## Verification and targeted changes

After construction, verify the current bytes, capability coverage, exact skill set, standalone references, documentation alignment, real tests, independent acceptance, and first useful action. Files and named capabilities do not prove quality. Track prepared, structurally_valid, independently_reviewed, accepted, installed, and actually_used separately.

Give forward tests the raw request and required sources without an answer or diagnosis. Test missing approval, ambiguous input, critical questions, requirement or source changes, self-review, pause and resume, unavailable capabilities, and recovery from an unknown effect. Do not make real publications or incur costs to test the route.

Route a new requirement through source → impact → blueprint and component changes → dependent evidence → targeted acceptance. Use local repairs for local gaps. Agree on mission expansion or new mandatory capabilities; make reversible corrections within current scope directly. Maintain the [generated agent contract](generated-agent-contract.md) and [support workflow](lifecycle-and-support.md).

## Domain and production handoff

The M1 passport includes applicable systems, exact behavioral promises, causal interactions, the first result's scope, and how it can expand. M2 materializes typed rules, state, catalog and fixtures, operation capabilities, recipes, transformations, attempts, consumer assemblies, and proof. Derive required output and variant classes from the requirements; avoid claims of completeness for an unknown domain. Numeric tuning needs a baseline, range, owner, and criterion; define the underlying rule separately.

For every component, specify its inherited core, domain, production and evaluation profiles; stable parent and child IDs; exact bundled paths and hashes; input, output and consumer; negative acceptance; cold recipient; and dependencies. A shared model change reopens dependent tests and proof. Preserve accepted originals. Keep invariants and due gates when shortening a SKILL file or splitting a family. Digest-link the relevant `foundry-depth/2` to the current blueprint. Do not change formats merely for a display version or represent a new record as the original approval.

## Selected product components

For `components.kind` values app, chatbot, or agent_skill, provide `specialist_route` with a stable `selector`, `handoff_artifact_id`, and `shared_contract_artifact_ids`. Declare the handoff as its own JSON artifact of kind `component_handoff`. A future self-referential ZIP is not the handoff. In a mixed app and chatbot product, identify shared contract artifacts and their single owner. This declaration plans a specialist route. Verify actual resolution, invocation and outputs under the [shared handoff contract](specialist-orchestration.md); factory approval does not prove those events.

## Evidence for architecture and sufficiency decisions

Separate the architecture of agent work (public owner, packaging, expertise, actual actors, handoffs and acceptance) from the architecture of the target result (product, process, research or another output). Add a compact strategy map to the passport: full intent and reconciled sources; results and due stages; comparison of reuse/compose/extend/create_gap; adequacy of expertise; actual gaps; choice and review triggers. Skill, phase and actor are independent units. Demonstrate specialization through outputs and representative requests.

When applicable, design the concepts, visual and interaction language, whole and component architecture, justified choice of languages, tools and patterns, and ongoing support for the target result. A specific future setting can have an owner and a due gate; define the corresponding capability and operating route now. Assess criticality and uncertainty separately from diff size. Research or independent review does not require fixed staffing.
