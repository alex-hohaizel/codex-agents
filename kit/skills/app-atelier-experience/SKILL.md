---
name: app-atelier-experience
description: "Design or repair an app brand, UX, visual system, and interactive prototype. Use for Android, iOS, and web experience and tested design handoff."
metadata:
  version: "6.3.0"
---

# App Atelier Experience

## Bind the accepted experience

Identify whether the work is new direction, design refinement, a prototype, build handoff or implementation QA. Pin the accepted concept, source masters, paths, assets and rights, version, product contracts, budget and stop. Identify the interaction whose failure would invalidate the design. Keep the accepted composition, scale, visual meaning and interaction mechanism. Run reversible work independently and return a concrete decision only for a material design, premise, cost or fidelity change. Delay significant asset production until the selected direction and architecture can support it.

## Design the full interaction and brand

Trace intention, action, product rule, feedback, useful result and next step. Cover return to saved state, errors, cancellation, recovery and help. Map navigation, screens and states across Android, iOS and web. Each accepted client needs a complete core. A landing page, unverified wrapper or unsupported sync button cannot stand in for the accepted behavior. Resolve product language, timing, access, limits and offline/degraded behavior alongside the specification.

Define a distinctive brand, hierarchy, typography, iconography, voice and interactions from the real user job. Verify asset rights and avoid reusing unrelated admitted identities. When the owner still needs to choose, compare materially different directions and their usability, production and support implications. Bind the decision to the actual artifacts. Version tokens, UI components, adaptive layout, copy, assets and allowed derived work with master and derivative digests.

Design the selected free, trial, limited or paid model. Expose benefit, price, period, limits, renewal, cancel and restore before a purchase. Evaluate combined payments and advertising through the entire journey. Label ads, respect consent and caps, and prevent obstruction or accidental clicks. Show voluntary rewards or ad removal only where the product supports them. Design clear pending, failed, unavailable, expired, refunded and restored states where applicable. A paywall is not evidence of willingness to pay.

## Prove the representative interaction

Build a runnable prototype of the critical journey with labeled test data and exact start steps. Verify its main transition, error/recovery and accepted mechanism in the actual consumer. Where relevant, record a narrow touch route, keyboard traversal, visible focus at the required text/zoom scale, readable labels, contrast, long strings, reduced motion and offline or degraded behavior. Specify representative OS/browser/viewport/input settings and use primary platform guidance for constraints. Compare behavior, not just appearance. A render, returned DOM or screenshot does not establish interaction, and a tablet or headless environment does not establish physical-device behavior.

Bound any optional browser or device probe. If the operation is unavailable or times out, preserve supported observations and mark the particular interactive proof open with a concrete check on the right host. Do not restart broad capability discovery or report a synthetic capture as observed usage. Preserve any applicable restrictions on human tests, outreach and telemetry. Before scaling, compare the accepted prototype with a working client slice and arrange an independent review where required.

## Hand off for build

Provide the exact accepted masters, state and platform map, allowed adaptations, interaction and motion expectations, tokens, components, copy, asset rights and provenance, actual launch/return steps, acceptance criteria and unresolved input. Version only the affected derivative work when a master changes. Record due proof, review actors and owner decision separately. Save the checkpoint at stop. A design review validates its actual scope and method, not a production release or human adoption.

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
