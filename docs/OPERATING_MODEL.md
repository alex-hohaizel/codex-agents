# Engineering with Codex Agent System

The unit of work is a result with a source, owner, and acceptance check. From a single-file repair to a production workflow, pick the shortest route that preserves the required result and its evidence. [Capability map](CAPABILITIES.md)

## Harness and authority

| Layer | Where it lives | What to inspect |
| --- | --- | --- |
| Runtime | Native Codex host and tools | Effective sandbox, connector availability, approvals, and account scope |
| Instructions and discovery | `AGENTS.md`, skill frontmatter, and linked resources | Loaded source, working-directory precedence, stable names, and exact paths |
| Workflow | Orchestrator, product families, and constructors | Task intent, prerequisites, applicable domain rules, and consumer |
| State | Native project records and a bounded task capsule | Exact revision, current decision, musts, deferred work, and pins |
| Checks | Schemas, source reads, sandbox fixtures, native evals, and independent review | Test outcome, actual artifact and consumer behavior, attribution, and limits |

Put stable routing guidance and exact resource links in `AGENTS.md` and skill entrypoints. Enforce type, path, target, rights, and state-transition controls at the actual operation. A scope declared in prose still needs the host’s permission checks. Select or delegate only what the job requires. [Adaptive work](../standards/adaptive-work.md) · [Tool compatibility](../standards/tool-compatibility.md)

## Routes and subagents

1. Start from the requested outcome, existing owner, actual inputs, permitted changes, and one appropriate acceptance check.
2. Work directly for a narrow task. Use a relevant skill or director for a recurring method or connected lifecycle. Let Orchestrator choose when the route is uncertain.
3. Delegate when the outputs are separable or review must be independent. Give each actor a bounded task, paths, authorized actions, source revision, budget, stop conditions, output, and return address. Assign a single writer per shared mutable target unless the consumer implements a tested concurrency contract.
4. Use Foundry to build an agent for a demonstrated recurring gap. Agree on the passport and verify the staged consumer using an original task. Build a reusable skill when its trigger, resources, and result can be specified and tested independently.
5. Integrate the actual result, retain its source and checks, and record each accepted and unresolved obligation. Route preparation, a subagent spawn, a result, and independent review are distinct observations.

[Orchestrator instructions](../optional-skills/atelier-orchestrator/SKILL.md) · [Agent Foundry](../kit/skills/agent-foundry/SKILL.md) · [Role sources](../agent-profiles/manifest.json)

## Project context and handoffs

Open the project’s authoritative requirements, identity, decisions, and checkpoint by ID or exact path. Use a capsule to carry a focused projection across a task, session, agent, or environment. Identify the original goal, applicable requirements and musts, source and revision hashes, accepted decisions and supersession, deferred work, allowed effects, output, recovery and next action. Record the gaps alongside the loaded references. A changed dependency invalidates the proof it affects.

In a handoff, preserve the project owner, actual files, and current authority. Limit read scope to what the consumer needs. When history is unavailable or incomplete, use verified project sources and name any unresolved context. Native project and provider state decide operational truth. A summary or retrieval result helps find sources and cannot amend their decisions. [Context capsule](../standards/context-capsule.md) · [Handoff template](../templates/HANDOFF.md) · [Project context template](../templates/project-context.json)

## Retrieval and RAG

Retrieval-augmented generation gives the model evidence selected from a corpus for the present query. Keep exact IDs, owned APIs, and ordinary lexical searches for cases they already solve. Add scoped semantic or hybrid ranking when examples reveal costly misses that those routes cannot cover.

1. Freeze a corpus with source ownership, authorized audience, revision, and lifecycle. Separate operational records with authoritative structured reads from discovery material.
2. Record representative questions and expected evidence, including exact IDs, paraphrases, mixed languages, ambiguity, no-answer, stale and revoked data, and neighboring private scopes.
3. Compare lexical, semantic, and hybrid retrieval on the same corpus and authorization rules. Check ranking and relevant hit rate, answer citation and abstention, latency, ingestion/storage cost, and deletion. Use independent or held-out examples for guidance instead of tuning solely against the public fixture.
4. If deploying an index, pin each chunk to its origin and revision, the index, embedding model and version, filters, ranking configuration, retention and rebuild plan. Filter permissions before retrieval and recheck source rights before citation. Remove stale or revoked content from indexes and caches. Treat retrieved material as data, not instructions.
5. Choose an index backend only for a demonstrated need. Keep a safe fallback or rebuild route and verify the actual consumer. A hosted vector store requires permission to send the corpus, a retention policy, and a deletion path.

The repository provides scoped context, a knowledge workflow, and eval patterns. Build and verify the index appropriate to your application when it needs one. [ChatBot knowledge skill](../kit/skills/chatbot-atelier-knowledge/SKILL.md) · [AI and data profiles](../standards/ai-production.md)

## Tools, evidence, and recovery

Choose an actual supported tool operation with known input schema, target, rights, cost, and receipt. Verify inputs before the effect and read the result from the owning system. After a timeout, pending status, or missing receipt, check the authoritative state for the exact target and request before any replay. Retry only with authority and a tested duplicate-prevention mechanism. Keep an unresolved effect open with the next fact needed to resolve it.

Agent Atelier discovers local native Codex project and chat metadata with coverage, opens history on demand, binds explicit folders, and prepares source-backed tasks. Review the original goal, selected skills, access, plan and acceptance before preparing and starting the task. Dispatch rechecks authority and sources. A workbench instance coordinates its supported jobs and cannot fence a separate Codex desktop writer. Inspect the native result and exact receipt before accepting an effect. Keep evidence local and scope any telemetry with explicit ownership and content policy. [Workbench guide](../apps/agent-atelier/README.md) · [Operation API](../apps/agent-atelier/shared/API.md) · [Resumable work](../governance/RESUMABLE_WORK.md)

## Evals and evidence

| Check | Evidence to keep |
| --- | --- |
| Trigger and route | Positive and nearby negative requests, explicit and natural routing, and the resolved skill source |
| Context and handoff | Original requirements, denied reads, stale references, restored identity, and resumed behavior |
| Consumer and tool effect | Exact artifact, real runtime when available, target/state/receipt, and relevant failure and recovery behavior |
| Attribution and cost | Source, input, model and host, observed actor, retries, elapsed time, cost and usage when reported |
| Judgment | Criteria, independent actor or method, scoped verdict, and unverified areas |

Start with deterministic checks and use native sessions for behavior. Measure the result and the quality of what was preserved, with an appropriate oracle. A fixture can demonstrate behavior within its controlled environment; use a real device, environment, channel, target, or independent actor when the claim requires one.

```bash
python3 -B kit/verify_release.py
python3 -B scripts/materialize_standards.py --check
python3 -B scripts/check_repository.py
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

Run the first three from the repository source directory. The canary uses the native Codex CLI and a signed-in host. Keep raw inputs, paths, and diagnostics private and publish only the permitted, scoped result. [Native eval suite](../evaluations/README.md) · [Validation and evidence](../governance/VALIDATION.md)

## Install, verify, and recover

Use the stable GitHub asset, exact source, attestation, and manifest. Review the audit, apply its plan once, retain the journal, and check fresh Codex discovery and behavior separately. Use per-component journals when recovering. Reconcile unknown external effects before resuming. Preserve existing project authority and unpublished local changes. [Install in Codex](INSTALL.md) · [Packages](../governance/PACKAGES.md)
