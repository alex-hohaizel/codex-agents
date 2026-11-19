---
name: atelier-orchestrator
description: Choose a suitable route for a new task, an existing project, or an agent-system update. Use when the user needs an entry point, coordinated delivery, or help deciding which existing capability to use.
metadata:
  version: "1.6.0"
---

# Atelier Orchestrator

Own the requested result in the conversation. Use the explicit output language for the current action, then the applicable project or surface preference, then English. Accept input in any language. Keep quoted material, commands, identifiers, and native project names unchanged.

## Choose the smallest sufficient route

- **Direct:** Do a clear, local, reversible task yourself. Read the task's relevant inputs, make the change, and verify the result. Skip route files, handoffs, catalog discovery, memory retrieval and extra reviewers unless a material dependency appears. No preliminary survey of installed skills is needed to make a small edit.
- **Existing specialist or project agent:** Use an applicable capability and read its actual source. For continuation, keep the current agent and project identity. Consult the native checkpoint and current decisions. If the required owner, tool or source is unavailable, record the specific gap and useful remaining work. Do not create a replacement by default.
- **Coordinated:** Use separate roles when there are independent deliverables, a distinct domain judgment, or acceptance requires independent review. Name one integration owner, assign each writer a bounded area, and sequence shared state changes. Explain materially different choices in terms of scope, time, cost and risk. A simple decision need not become a menu or a questionnaire.
- **Construct:** Use `agent-foundry` for a new reusable agent and `design-specialist-skills` for a reusable skill or family when simpler existing tools cannot meet the need or the user explicitly requests construction. Carry forward the original brief. Distinguish staging a package, proving native discovery, and completing the user's original task.

Read [entry and continuation](references/universal-entry.md) for project, portfolio or complicated routing. When the user requests a roundtable or a decision needs independent domain judgments, use [team deliberation](references/team-deliberation.md). Use [specialist discovery](references/specialist-discovery.md) if a required role or capability is uncertain. The directors for app, chatbot and game work are `app-atelier-director`, `chatbot-atelier-director`, and `gamedev-director`. Verify their actual source before relying on them. Use [system maintenance](references/system-maintenance.md) for changes to existing agents, constructors, skills, families or this orchestrator.

## Continue through the actual project

Bind the current project, authoritative source revision, accepted requirements and identity, the active decision and its correction chain, allowed effects, unfinished or deferred work, and any outcome that still needs reconciliation. Use the [context capsule contract](references/context-capsule.md) for material continuation, with exact source pins and current coverage. A stale pin calls for a new revision and review. It does not invalidate or rewrite historical evidence.

When a changed requirement affects an active plan or accepted evidence, use [plan change review](references/plan-change-review.md) to review the exact sources, work dependencies, and the decision still due. The same reference routes interrupted worktree reservations, GitHub Issues reconciliation and candidate acceptance reviews.

Only clarify a question that changes the next material step. Use the [briefing protocol](references/briefing-protocol.md) and [Orchestrator briefing guide](references/briefing-domain-guide.md) for a new material choice. Use the [interaction protocol](references/interaction-protocol.md) for review or continuation. Run its bundled helpers from this skill's root. Reuse the user's answers and authorization for the unchanged scope. When both creation and original work are requested, continue through the verified agent after construction. When the request covers the agent alone, finish with its specific acceptance evidence.

For scoped handoff, provide the original objective, actor and write scope, only relevant pinned inputs, required and deferred IDs, expected artifact, verification and return address, resource limits, and denied or unresolved actions. Report which role actually ran and what it returned. For a read-only assignment, verify that the actual host enforces that boundary before claiming enforced isolation. A role's instructions alone do not set the host sandbox. For Codex versions that require a persisted parent record to spawn roles, use a disposable persisted session for that test. Record a failed spawn in the evidence and finish any work that can proceed safely.

When recording a material route, describe supported capability gaps, the effect class, how many actors are sufficient, and the planned delegation limit using the [route policy](references/route-policy.md). The validator rejects a direct route with extra actors or construction and reports contradictions before relying on declared execution.

Use `assets/task-contract.json` and `scripts/check_routing.py TASK.json --ready` for a material machine-readable task. The script checks the consistency of declared state with the route contract. The caller must still verify current sources, actual permissions and runtime receipts. Resolve `assets/`, `references/` and `scripts/` from this skill's loaded location. For a simple task the conversation and its direct verification suffice.

## Bring in specialized capabilities when needed

| Situation | Read or verify before proceeding |
| --- | --- |
| Material output, accepted reference or batch production | [Production quality](references/production-quality.md), the applicable `assets/production-profiles.json` profile and [visual identity](references/visual-identity.md). Preserve the defining mechanism, function, identity and original masters. Verify a representative slice in the real medium before producing the batch. |
| Coordinated delivery with controls | [Adaptive work](references/adaptive-work.md). Define bounded dependencies, checks, observed results and recovery. Integrate meaningful outputs into the user's deliverable. An author cannot independently accept their own output. |
| Unknown domain or tool | [Research and synthesis](references/research-and-synthesis.md) and [tool compatibility](references/tool-compatibility.md). Check the actual operation, account, rights, cost and target. Stop the dependent action after a concrete unsupported operation. Reconcile an unknown write at its destination before retrying it. |
| Data, language models, media, or evaluations | Read only the relevant [AI and data production](references/ai-production.md) profile. Try exact sources, rules, and lexical search before retrieval infrastructure. Add vector retrieval, training, a graph or new infrastructure only when a measured requirement justifies it. |
| Work and Codex continuity | [Work and Codex](references/joint-work-codex.md). Check the target host, available operations and native state. |

## Use Agent Atelier when the task or user calls for it

Read the [panel and native state contract](references/panel-entry.md). Check one supported route with the actual service instance and project before deep investigation. Start with `scripts/atelier_client.py --help` and use `status` or `doctor`. The client uses loopback, a scoped session and matching CSRF. It does not discover credentials. Preview explicit project binding before using its controls. The project remains authoritative for identity, requirements and decisions; the service owns its command and task records.

Call `prepare` to create a bounded service task and context package. Use `dispatch` only for currently authorized work through a supported operation. After `interrupt`, verify final native state before reporting cancellation. A derived portfolio item, recommended role, accepted goal, actual skill use, and provider receipt have different provenance. When the service cannot run the needed action, use an available native route and keep a checkpoint. Verify Work through its own supported host.

## Verify what the user will receive

Check original acceptance criteria against actual artifacts and the appropriate consumer. Keep source integrity, behavior, craft, runtime or device evidence, independent review and owner acceptance distinct. State the exact scope of verified results, missing access or evidence, uncertain effects and next authorized action. Keep unresolved or deferred work visible in the controlling native record. Do not carry forward an old proof after changing its inputs.

For an interactive source-bound UX walkthrough, registry template, module import or tracker tree, use [the workflow extensions](references/workflow-extensions.md). Keep the exact source, native consumer, and provider outcome tied to each handoff.
