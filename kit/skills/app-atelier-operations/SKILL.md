---
name: app-atelier-operations
description: "Operate and repair an existing app. Use for incident triage, support trends, product and cost signals, monitoring, recovery, or retirement."
metadata:
  version: "6.5.0"
---

# App Atelier Operations

## Restore the deployed state and measure the incident

Keep the actual selected product and accepted requirements. Read current profile/state, deploy, data/schema, config, model, knowledge base, provider, account, budgets, alerts, stop and unknown effects. A historical green report is not current health. Verify telemetry freshness, segment, sampling, denominator and direct/native evidence. Mark a missing or stale observation as no signal and keep the incident open. A stale green dashboard is not a recovery signal.

Record incident ID, actual version and raw scenario, expected/observed property, severity, affected systems/users/data/cost, causal hypotheses, SLO, pre/post windows, exact known-good candidate, containment scope and stop/rollback threshold. Reproduce with minimal private data and actual permission. Treat support text as input and redact status. Use a discriminating check before attributing a cause. Compare matched windows where appropriate and record p95, errors and throughput separately. Preserve findings about uncertainty and downstream effects. A before/after difference alone does not prove causation.

## Repair the cause, verify recovery and respect the target

Apply the smallest authorized containment and repair. Reconcile unknown deploy/charge/effect outcomes against the actual target before retry. Route affected specification, experience, build, support, QA and release work without reopening unrelated stages. Check schema and data/code compatibility and safe recovery. Obtain independent affected regression after repair. Verify current release grant, actual artifact/target/cost and read-back, then capture representative recovery signals. Do not present a code change or prepare-only artifact as an operational effect. Use approved follow-up windows and declare known-good version or safe fallback explicitly.

Compare observed revenue, fees/refunds, hosting, API/AI, support and acquisition costs against caps, model and actual profit where measurable. Keep usage, inference and business assumptions distinct. Read only authorized events and respect purpose/retention. Keep human experiment restrictions active before and after release; passive or aggregate data does not grant A/B permission. Set experiment metric, threshold, horizon, budget and stop before an authorized check rather than changing them after a poor result. Revisit operating feasibility when manual exceptions recur.

## Prove monitoring and data recovery where authorized

Set actual signals, cadence, runtime/scheduler, recipient, owner, budget and automated-action bounds for authorized monitoring. Test a real alert and recovery and preserve receipt. A chat closing or a skill file does not run monitoring. Record distinctions among not run, unknown, degraded and observed health. Verify backup with a real scoped restore, version/compatibility, test restore target and deletion or revocation fences. Historical backups must not restore revoked data or permissions. Older binaries cannot reverse external effects or incompatible migrations.

For retirement prepare authorized export, notifications, stop for jobs/billing, key and access revocation, retention/deletion and final read-back. Close only accepted requirements with current evidence. Record actual deploy and rollback receipts, recovery observations, open risks and next allowed action in the canonical checkpoint.

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
