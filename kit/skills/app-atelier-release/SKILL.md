---
name: app-atelier-release
description: "Assess app store and deployment feasibility, then prepare and execute an authorized release candidate. Use for exact packages, target tracks, signing, and rollout verification."
metadata:
  version: "6.3.0"
---

# App Atelier Release

## Check feasibility before significant build

Read the actual product profile, target clients, scope, model, budget and accountable owner. Verify current operation-level feasibility for Android/iOS stores, web/backend, support, data and billing where applicable. Check official store, account, signing, testing, access, country, cost, SDK and human prerequisites before development commits to them. Include applicable licensing, age/content/privacy/accessibility requirements and domain specialists for high-responsibility products. Verify ownership and account access. An unavailable account or signer is a blocker, not proof of an available route or a naturally inapplicable feature. Report the concrete conflict and authorized options. Respect budget and human-work restrictions, without bypassing store testing or identity requirements.

## Bind the exact release candidate and decision

Prepare a versioned release record linking source commit, approved requirement and UI versions, exact app package/binary digests and signing identity, web/backend/support assemblies and configs, target store/account/track, exact effect scope, readiness QA, migration, rollback and health criteria. Pin current authority and both one-time and recurring cost. Verify actual independent client, data, billing/entitlement and support evidence for the claimed scope. Recheck prerequisites before submission and preserve open blockers. Distinguish readiness recommendation, owner's decision and approval for the concrete external effect. A matching marketing version or signed package cannot override a digest mismatch. Block promotion if the receipt or read-back resolves a different binary, account, track or release.

Prepare truthful listings, actual product renders or previews, localizations, privacy/support URLs, reviewer notes and demo path, product IDs and entitlements, restore/cancel/return behavior, monitoring and support. Do not invent certification, reviews or an observed product. Keep the approved presentation and scope. Give the owner a reviewable packet with exact operation, costs, capabilities and remaining gaps. Prepare the precise launch/return steps for any separately required MFA, signature, identity or device action. Never ask for secrets in chat or packages.

## Execute only the authorized operation and verify the effect

Use the authorized host/account/route with the correct candidate and parameters. Prefer a staged local or sandbox verification when suitable and distinguish it from external release. Record stable effect ID, actual provider receipt or unknown outcome, and current read-back. Reconcile timeout or unknown response before a retry or source change. Track submitted, approved, deployed, released, available and observed core separately. A completed upload is not proof of availability or useful operation. Verify the actual running result where authorized. On repair, re-open affected QA and recheck the exact current approval.

Hand operations the effective URLs/builds, source and package evidence, observed result, monitoring and support signals, data/code compatibility, rollback thresholds and recovery, incomplete gates and next action. A binary rollback is not reliable evidence of data or effect reversal. Preserve history and write the actual release status to canonical state after verification.

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
