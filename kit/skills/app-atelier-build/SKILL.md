---
name: app-atelier-build
description: "Implement or repair an accepted app on its target Android, iOS, and web clients. Use for a working slice, integration, build, or implementation regression."
metadata:
  version: "6.6.0"
---

# App Atelier Build

## Check production scope and choose the simplest approach

Bind the actual repository, branch or worktree, owned paths and baseline. Read the accepted concept, PRD/TDD, masters, client set, domain/data/API/auth contracts, billing model, operating and acquisition plans, resource limits and due gates as applicable. Before significant build, verify current account, store, signing, testing and cost feasibility under the profile, including human-work limits. Use primary SDK and provider docs and verify actual capability. Missing access stays blocked for the affected target. Ordinary implementation authority does not confer release, live payment or migration permission.

Compare native, cross-platform, web and shared-code options against the actual core, data/offline model, support, cost and device quality. Choose an adequate toolchain and keep separate domain rules, platform adapters and effects only where needed. Preserve platform differences and compatible shared semantics explicitly. Deliver a complete core in each agreed client. Do not substitute a landing page for web or a wrapper that drops accepted offline behavior for a mobile app.

## Prove a working slice and preserve data

Exercise the critical path from input and rule through data or integration, UI feedback, useful outcome and recovery on each agreed target. Use accepted assets, authorization, commerce and support interfaces that the slice requires. Cover empty, error, pending and offline states. Establish the exact source/build/config, platform capability, observed interaction, evidence method and consumer. Verify the riskiest dependency before scaling and resolve any material drift from the accepted design or behavior first.

Implement data schema and API version compatibility, validation and errors, local-first storage where sufficient, sync/retry/conflicts, migrations and recovery. Test older saved state through restore, offline queue, reconnect and repeated dispatch on the relevant clients. Separate UI stub, local harness, simulated integration and observed native result. Authorize all data reads and mutations at trusted boundaries. Enforce subject and tenant isolation across API, files, cache, support and effects. Keep secrets and private content out of logs, telemetry, AI tools and networks without the appropriate purpose, scope and rights. Support export/delete/revoke and backup/restore with revocation fences where required.

## Verify commerce and integrated behavior

Implement the agreed free/paid and advertising boundaries. For purchases, verify provider-backed receipts/signatures/state through official routes. Maintain separate pending, purchased, active, expired, cancelled, refunded and revoked states as appropriate. Cancelling renewal alone does not remove an already valid paid period. Handle restore, reinstall, duplicates, delayed and reordered events, retries, unknown state and offline entitlement/recovery. Reconcile newer rights with provider authority. State cross-client/store and anonymous-purchase limits explicitly. For no-purchase models, document inapplicable branches. Verify clear ads, caps, placement, failure and rewards where applicable. Use sandbox where sufficient and retain separate grants for real money.

Integrate accepted UI, accessibility, assets and support without broad privileges. Measure accepted performance budgets in suitable environments. Use meaningful domain, contract, integration and end-to-end checks. Separate compile, simulator/emulator, headless browser, physical device and production evidence. Record the specific blocked device check and launch/return route when access is missing. Do not bypass approved constraints on recruiting or human experiments with synthetic accounts.

## Hand off the reproducible build

Provide source/build/config and accepted master digests, actual assemblies, build instructions, environment and platform versions, test commands and independent-ready receipts. Pin reproducible dependencies and CI, manage secrets and grants, include migrations, rollback compatibility, recovery and known gaps. Reconcile unknown live effects before retrying. Tag author checks accurately and send affected raw proof and fixtures to QA. Update canonical state with exact next action. Building, readiness, deployment, availability and measured business outcomes are separate claims.

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
