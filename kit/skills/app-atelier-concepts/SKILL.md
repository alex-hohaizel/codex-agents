---
name: app-atelier-concepts
description: "Compare app concepts, monetization, and economics for an accepted direction. Use when choosing a complete core, pricing model, or viable operating approach."
metadata:
  version: "6.3.0"
---

# App Atelier Concepts and Economics

## Build and compare viable candidates

Bind the accepted direction, current market research, competitive exception, project profile, platforms, operating constraints and budget. If the direction remains undecided, provide a concrete decision packet and proceed only with independent preparation. For an existing product, compare the authorized pivot against its baseline. Concept approval does not open build, a support bot, a paid campaign or release.

Define the user and payer, trigger, complete first useful action, value of returning, and fallback when it fails. Specify a small complete core and compare broader alternatives at comparable resources. Preserve the accepted clients, onboarding, useful action, errors, recovery, repeated use and data retention or deletion. Establish a plausible design brief, adoption route, operational map and evidence of reuse. Check automation and rights for data, data suppliers, moderation, sales, content and support. Remove must failures before scoring and show the strongest objection to the favorite.

Compare relevant free, trial, freemium, advertising/removal, one-time, modular, subscription, usage, team and affiliate alternatives. Show the value already available, additional benefit, when and why the offer appears, clear terms, post-purchase result and repeat need. Name recurring value and cost for subscriptions; model maintenance of one-time purchases. Specify acceptable ad placement, consent, frequency and cost. Evaluate the combined payment journey, including duplicated rights or damaged free/trial paths. Select models from the actual product and profile.

## Make the economics reproducible

Deliver a versioned calculator or table with formulas, sources and dates, units/currency, periods, input assumptions and unknowns. Separate revenue, direct contribution and profit. Include setup, recurring and variable costs, provider/storage/AI calls, support, acquisition, fees, refunds and release expenses. Compute acquisition recovery and contribution/LTV under explicit repeat use or retention scenarios. Show how sensitivity to conversion, retention, cost and other critical assumptions changes the recommendation. State required scale, cash shortfall before receipts and coverage of long-term obligations. Do not fit unsupported parameters to a target. Use ranges and an explicit pending verdict for unknown inputs. A high score with negative baseline contribution stays on hold or is rejected unless a falsifiable condition justifies reevaluation.

## Give the owner a decision and reusable inputs

Define the metric, threshold, cohort or denominator, time, rights, budget and stop for each approved validation. Honor limits on deliberate human experiments, including post-release A/B. Desk and synthetic checks cannot establish willingness to pay. Preserve assumptions and inputs that would reverse the conclusion. Save candidate cards, calculator, operations/acquisition and prototype briefs, rejected options and decision packet in `artifacts/concepts/<run-id>/` and register their actual hashes. Give specification, experience and growth the accepted concept, exact scope, musts, rationale, unknowns and gates. Early release/account/testing/budget and human-work feasibility, acquisition and a representative technical slice need later evidence before significant build.

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
