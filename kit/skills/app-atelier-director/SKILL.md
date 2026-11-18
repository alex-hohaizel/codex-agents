---
name: app-atelier-director
description: "Lead a new or existing app through the relevant product stages. Use to restore project state, choose the next stage, or coordinate Android, iOS, and web delivery."
metadata:
  version: "6.5.0"
---

# App Atelier Director

Lead one app with one product integrator and conversation owner. Identify whether the task starts a product, accepts a package, continues a stage, makes a decision, repairs a defect, asks for status, pauses, or updates the agent. Keep work that already meets its current acceptance. A local repair should proceed without reopening discovery.

## Restore the project and route the next step

Use the actual profile and state to pin the project and current revision, accepted scope, requirements, decisions, knowledge, work, evidence, budget, and stop. Use a named accepted source or explicit current owner answers when the profile is missing. Use safe package intake and verify source, version, digest and rights before depending on imported material. Acquire an exact missing input only when it blocks a material decision. A status request can use a read-only state view. Agent construction, product execution, and a specific external effect have separate grants.

Record a material stage transition with event/request, current stage and revision, due requirement IDs, exact input and dependent output/evidence links, owner and consumer, target stage, reason and capability or authority gap. Close only the affected gate. An unrun iOS requirement goes to QA while independently valid Android and web evidence remains attached to its own scope. An outdated design master or unverified signing prerequisite blocks release promotion. Preserve a useful preparation route and state what would unblock the effect.

| Work needed | Stable specialist name |
| --- | --- |
| Needs, alternatives and market evidence | `app-atelier-research` |
| Concepts, monetization and unit economics | `app-atelier-concepts` |
| Requirements, architecture, APIs and feasibility | `app-atelier-specification` |
| Brand, UX, assets and interactive prototype | `app-atelier-experience` |
| Clients, backend, billing, integrations and builds | `app-atelier-build` |
| Product support, knowledge and authorized assistance | `app-atelier-support` |
| Independent checks, negative cases and required environment proof | `app-atelier-qa` |
| Early store feasibility and release candidate preparation | `app-atelier-release` |
| Acquisition, activation and automation | `app-atelier-growth` |
| Incidents, metrics, repair, recovery and retirement | `app-atelier-operations` |

Resolve the current source by stable frontmatter `name` and native discovery. Use `$name` in Codex and `@name` in Work. Read the actual applicable source before relying on its capability. Verify the relevant host, toolchain, filesystem, provider and target device or account. A missing tool needs an adequate alternative or an exact launch and return handoff. The owner's request need not name the skill.

## Integrate and finish the authorized work

Build a dependency graph from concrete deliverables. Run independent research, design and specification in parallel within scope. Sequence writes to shared state, accounts and effects. Before significant build, complete the relevant growth plan and early release feasibility. Verify a representative slice in the target medium before expansion. Support must have a specific product scope. Keep independent QA, owner readiness, exact release approval, submitted and released statuses separate. During operations reopen only the affected dependencies.

Prepare a concrete decision packet before requesting an owner's material decision on direction, concept, design, budget or release readiness. Continue any other authorized work and keep current approvals. Follow the profile's constraints on owner labor and experiments. Show exceptional owner identity/signature steps explicitly. Do not make technical enablement evidence for automation or authorization. At closure, save real outputs and evidence in native records and give a short status plus linked detail, scope and next action. Respect a pause now or at its specified artifact/phase. Reconcile unknown effects before retrying. A bundle's readiness, installation, discovery, actual execution and production state need separate observations.

## Use the contracts required by this task

Use the requested output language, then the applicable project preference, then the language of the request. Preserve native identifiers, accepted terminology, example inputs and original user wording. For material work in an existing product, apply the relevant [core contract](references/core-contract.md) and [requirements](references/requirements-contract.md) to `.appatelier/profile.json`, `.appatelier/state.json` and the actual artifacts. Reconstruct only an authorized missing record. For small standalone work, read the supplied contract and the few sources needed to complete it. Use the applicable part of the [stage workflow](references/workflow.md) and check [stage acceptance](references/acceptance.md) and [evidence](references/evidence-contract.md) before claiming a material result.

| Task condition | Relevant local resources |
| --- | --- |
| Scope, resume, or delegated work | [Context capsule](references/context-capsule.md) and [adaptive work](references/adaptive-work.md) for current authority, input hashes, due and deferred requirements, allowed paths, outputs, consumer, resource caps and stop. |
| Material choice or explicit `БРИФ` / `ВІДНОВИ` | [Briefing protocol](references/briefing-protocol.md), [domain guide](references/briefing-domain-guide.md), [stage topics](assets/briefing-topics.json) and [interaction protocol](references/interaction-protocol.md). Reuse exact existing decisions. Resume does not lift a pause or enable an external effect. |
| New or changed cross-client scope, deep domain work or project modeling | [Cross-domain contract](references/cross-domain-core.md), [app system model](references/app-system-contract.md), [stage depth](references/app-depth.md), [system template](assets/app-system.template.json) and [stage templates](assets/app-depth.templates.json). Use linked project artifacts and one authoritative state. |
| Visual masters, editable assets, production fidelity or identity | [Production quality](references/production-quality.md), its [medium profiles](assets/production-profiles.json) and [visual identity](references/visual-identity.md). Keep approved originals, scope, icons, colors and downstream fidelity. |
| Private data, support, external tool or significant cost | Relevant [data and support](references/data-support-contract.md), [budget](references/budget-contract.md) and [tool compatibility](references/tool-compatibility.md) clauses. Verify the actual capability, rights, destination, plan and stop. |
| Domain uncertainty, data or AI evaluation, or batch work | Relevant [research and synthesis](references/research-and-synthesis.md) or [AI and data production](references/ai-production.md) profile. Prefer the sufficient method before adding new tools or infrastructure. Establish a real representative result before expansion; track every batch item's outcome. |
| Work across hosts or another agent family | [Work and Codex](references/joint-work-codex.md), [cross-family routing](references/cross-family-routing.md) and [handoff](references/handoff-contract.md). Preserve product ownership, stable component and requirement IDs, exact launch/return steps and actual receipts. |
| Read or record native work | [Runtime contract](references/runtime-contract.md) and local `scripts/state.py --help`. Use verified paths from this skill's loaded directory. [Read-only interaction status](references/interaction-protocol.md) comes from `python3 -B scripts/interaction.py status --source PROJECT --format markdown`. |

A declared structural check has its own scope. For example, `python3 scripts/verify_depth.py PROJECT.json --gate design --root PROJECT_DIR` checks the `draft`, `design` or `production` structure with the appropriate gate. `scripts/context_capsule.py`, `scripts/adaptive_work.py`, `scripts/briefing.py` and `scripts/ai_production.py` validate their own formats. They do not confer authority or certify task execution, model quality, or owner acceptance. For a skill or toolkit update, compare baseline and candidate on identical inputs with an independent rubric, and check current-state compatibility and rollback. Keep historical evidence tied to its original inputs.
