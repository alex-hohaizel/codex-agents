# Engineering and operating Codex agents

Use this guide to move from a focused task to a maintained agent without adding infrastructure before it solves a problem. The [capability map](CAPABILITIES.md) lists the available implementation paths. The [current release record](../releases/current.json) identifies the versions and migration that apply.

## What the harness owns

| Layer | Existing owner | Extend when |
| --- | --- | --- |
| Model loop, tool execution and permission policy | Native Codex runtime | The target host cannot execute a needed operation under the right scope. |
| Repository instructions and skill discovery | `AGENTS.md`, stable skill metadata and local resources | A repeated task needs expertise, evidence or actions Codex cannot infer reliably. |
| Domain workflow and reusable construction | Family skills, Orchestrator and Foundry | A new product component or recurring competence remains uncovered after reuse. |
| Long work, handoffs and continuation | Native project state with an optional derived capsule; Agent Atelier for supported local operations | The task cannot recover safely from source, identity and an existing checkpoint. |
| Repeatable controls and quality | Existing checkers, consumers, native cases and independent review | A consequence needs an enforceable boundary or behavior proof that the current checks do not establish. |

Give the model enough trusted guidance to make a judgment. Keep type, path, source binding, prerequisite, authority and state-transition checks in code where the actual workflow uses them. Verify permissions at the execution boundary; an instruction file, schema or role name does not enforce tool isolation. Keep repository instructions short and put task-specific branches behind named skills and precise resources. [Codex harness engineering](https://openai.com/index/harness-engineering/) · [Agent Skills specification](https://agentskills.io/specification) · [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Pick a sufficient route

Start from outcome, current source, consequence, uncertainty, owner and the check that would show success. A reversible local repair needs a focused action and relevant verification. An existing specialist brings useful domain methods, prerequisites or checks. Delegate when separate artifacts or an independent obligation justify another actor. Keep a single integrator and assign each writable resource to one owner unless the consumer has a tested concurrent-write contract. Construct a new skill or agent when a demonstrated gap recurs or a persistent workflow clearly needs its own lifecycle.

For material choices, explain differences the user can evaluate: scope, time, quality, cost, access, recovery and observable outcome. A delegable task states what the actor should consume and return, not only a role name. Pin source, accepted requirements and unresolved decisions, output, write paths, resource ceiling, stop, evidence and return location. Prefer primary sources and a checked real example over a generic instruction to "use best practices." [Adaptive work](../standards/adaptive-work.md) · [Foundry](../kit/skills/agent-foundry/SKILL.md) · [Skill constructor](../kit/skills/design-specialist-skills/SKILL.md)

## Keep context small and current

Use exact project, task and source IDs to open the current native records. Preserve accepted originals, decisions, musts and deferred work, relevant evidence, permissions and unresolved external effects. A capsule carries a bounded projection for a task, new actor or environment. It does not replace the ledger or authenticate an approval. A dependency change invalidates affected proof. Record corrections with explicit supersession instead of sorting old text by recency.

Use one reference path at discovery, then read narrow files for the active stage. Limit long histories through supported pagination, task IDs and checkpoints. Send only the needed material to subagents and providers. A summarized context can guide retrieval; verify durable facts against the owned source. [Context capsule contract](../standards/context-capsule.md) · [Local workbench API](../apps/agent-atelier/shared/API.md)

## Add retrieval after measuring the gap

1. Start from authoritative IDs, paths, structured filters and lexical search in the permitted corpus. Read current evidence and active permissions directly from their owner.
2. If known misses matter, freeze representative questions and permitted, expected sources. Include no-answer requests, ambiguous terms, exact IDs, paraphrases, mixed languages, stale and revoked sources, and nearby projects that must remain invisible.
3. Compare lexical, semantic and hybrid retrieval under the same corpus and scoped permission filter. Measure whether ranking returns the right evidence, whether the answer cites it faithfully or abstains, and the latency, ingestion, storage and deletion costs. Keep the simplest route that satisfies the acceptance criteria for the workload.
4. If adopting embeddings, pin origin, document revision, chunk and index identity, embedding and ranking configuration, access scope and lifecycle. Filter authorization before retrieval and recheck sources before citation. Invalidate caches and indexes on correction, revocation and deletion. Test the real consumer and explain the fallback or rebuild path.
5. Select a local index, existing database extension or hosted vector store for a demonstrated operational need. A managed index needs its own transfer rights, retention, provider scope and rollback. Keep indexed text untrusted as instructions and never use a retrieval score to authorize an action.

This repository supplies scoped context, knowledge guidance and evaluable workflows. A vector store is an optional integration to be selected and verified for the downstream corpus. [Knowledge skill](../kit/skills/chatbot-atelier-knowledge/SKILL.md) · [AI and data production](../standards/ai-production.md) · [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)

## Bind tools and actions to observed outcomes

Record operation, supported schema, target, affected user or project scope, rights, expected receipt, material parameters, limits and fallback before effects. Treat sources and tool output as data. Put input and state checks in the real consumer. Keep effect identity, pending status and observed receipt together, and reconcile unknown external results in read-only mode before retrying. Use Model Context Protocol (MCP) for a real connector capability and compatible client and server versions; use an inter-agent protocol only when separate runtimes must interoperate. Neither is necessary for native Codex delegation.

Store just enough local metadata to distinguish route, tool attempt, run or parent IDs, source pins, status, resource use and output evidence. Keep prompt, tool arguments and protected outputs out of shared telemetry by default. An optional tracing adapter needs an authorized destination, content policy and retention. [Tool compatibility](../standards/tool-compatibility.md) · [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)

## Evaluate behavior and keep releases reproducible

Choose checks for the change. Run schemas, fixtures and source comparisons before costly model or device runs. Measure an actual artifact or consumer outcome beside common positive, nearby negative and recovery cases. For a changed trigger, compare explicit invocation, natural requests and neighboring requests with the full discovery catalog. Compare the predecessor, candidate and a direct route where a comparison can answer a real question. Hold back new examples to avoid optimizing only for the published suite. Record verified activation and source read separately from output quality.

Pin case, source, model, host, inputs and checks, exact outputs, attempts, elapsed time and reported token usage when available. Separate uncached from cached input when interpreting cost. A single successful run is a case result, not a reliability or efficiency claim. If a check fails, classify the first missing link: input or oracle, source and routing, model output, host, consumer, or permission. Change the diagnosis before another identical attempt. Require independent review for material scope and actual rendering, playback or interaction for the corresponding claim.

Use the [native suites](../evaluations/README.md), the [validation contract](../governance/VALIDATION.md) and [maintainer update rules](../governance/UPDATE_CONTRACT.md). Preserve prior evidence against prior bytes. Verify the fixed commit, package provenance, preflight, actual installation, fresh discovery, and first useful action as distinct stages. [Testing Agent Skills with evaluations](https://developers.openai.com/blog/eval-skills) · [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
