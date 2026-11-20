---
name: app-atelier-specification
description: "Turn an accepted app concept into PRD, technical design, and verifiable cross-client contracts. Use for requirements, data, APIs, entitlements, and build feasibility."
metadata:
  version: "6.7.0"
---

# App Atelier Specification

Before a material production choice or dependent artifact, follow the [production choice contract](references/production-choices.md). Bind the current project decision, accepted master and flow, and verify the phase before using the result. Reuse verified decisions for narrow repairs.

## Bind the project and the design decision

Start with the current accepted concept, profile, requirements, decisions, raw inputs, rights and previous specification. Record scope, versions, owner, target outputs, budget and stop. If the accepted concept is missing, complete independent preparation and surface the blocked dependency. Keep personal goals, numbers, markets, policies and account constraints in the product. Retain the owner's direction, concept, design, budget and readiness decisions. Make routine technical choices within scope and record the reason. Do not create a product, spend, create accounts, publish, run telemetry or start live jobs while specifying.

State the user, repeated job, complete core, valid alternatives, and launch slice versus full target. Model objects, ownership, rules, invariants, transitions, exceptions and empty/error/offline/recovery paths. Define a complete independent core for Android, iOS and web where accepted. Preserve usability, old device support and accessibility appropriate to the audience. Define platform differences with the same core outcome. Compare architectures after the domain model, including external services, actual rights, cost and fallback. Treat UI, support, acquisition and automated operation dependencies as product contracts.

## Connect requirements to interfaces and tests

For each critical requirement, bind the state transition/rule, API or event schema and version, error contract, consumer and a reproducible acceptance fixture for each applicable client. Document creation, ownership, guest/authenticated access, tenant, revision, invalid states, idempotency, delayed/reordered events, retries and recovery as applicable. Include an object-access matrix and a case where a second actor attempts an ID lookup. Backend authorization must validate actual actor and scope on each read or effect. A missing ownership gate or incompatible response for even one client leaves the integrated criterion open. Use observable expected results, including identical conditions where clients share an outcome, without inventing passed checks.

Begin with minimal, functionally sufficient local storage. Separate anonymous use, guest and authenticated identity. Specify local-first or justified cloud/sync storage, purpose and recipients, retention, redaction, export/delete/revoke, backups, derived copies/cache/index, telemetry and AI/support egress. Disable telemetry until its data gate. Describe explicitly allowed read-only support and bounded future effects with linking and consent. Treat human experiments, recruitment and external writes as separately governed, and keep owner review and synthetic validation correctly labeled.

Compare no-API, chosen API and fallback for `REQ-11`. Include setup, recurring, usage/overage, fees, refunds, support and acquisition cost. Link provider-backed entitlements to the selected monetization including restore, duplicates, delay, expiry, cancellation and refund where applicable. State no-purchase exclusions explicitly. Verify platform-dependent transfer behavior. A subscription or free tier cannot guarantee unlimited production API use. Identify fallback labor when profile autonomy restricts it. Size the smallest representative slice and significant build separately. Record unknowns by owner, blocked dependency and planned proof.

## Preserve separate gates and hand off

**Specification ready:** review PRD/TDD and domain/data/API/billing contracts, estimates and acceptance. Check `REQ-11`, `REQ-16`, `REQ-19`, early `REQ-38`, and cross-cutting musts. A binary is not required to accept a specification.

**Before significant build:** require current concept and design, economic/operational/acquisition and resource feasibility, with an accepted proof plan for the actual build slice. Verify the store, account, signing, testing, no-human and budget routes. Unknown account access remains unverified. Do not use synthetic users to bypass store or policy constraints.

**Before release:** recheck current prerequisites and preserve tested platform and billing evidence for later readiness and exact release approval. Record scope or route conflict as an explicit decision. Store PRD/TDD, domain/data/API/billing, dependencies, estimates, fixtures and gates in `project/specification/`. Index versions, hashes, requirement IDs, decisions, evidence and blockers and hand each consumer the exact interfaces and next action. Engineering assumptions or author checks do not substitute for an independent review or actual runtime acceptance.

## Use the contracts required by this task

Use the explicit output language for the current action, then the applicable project or surface preference, then English. Accept input in any language. Preserve native identifiers, accepted terminology, example inputs and original user wording. For material work in an existing product, apply the relevant [core contract](references/core-contract.md) and [requirements](references/requirements-contract.md) to `.appatelier/profile.json`, `.appatelier/state.json` and the actual artifacts. Reconstruct only an authorized missing record. For small standalone work, read the supplied contract and the few sources needed to complete it. Use the applicable part of the [stage workflow](references/workflow.md) and check [stage acceptance](references/acceptance.md) and [evidence](references/evidence-contract.md) before claiming a material result.

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
