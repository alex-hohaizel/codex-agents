# Capability and tool map

Choose a capability by the result you need, the environment where it must work, and the evidence required to accept it. Open the source for the current entrypoint, role, or operation. The [release record](../releases/current.json) supplies versions and migration links.

## System components

| Component | What it does | What a successful check proves |
| --- | --- | --- |
| [Atelier Orchestrator](../optional-skills/atelier-orchestrator/) | Takes a new request, continues source-backed work, selects a sufficient route, coordinates handoffs, and scopes system maintenance. | The route supports the actual task and a consumer can inspect its result. |
| [Agent Foundry](../kit/skills/agent-foundry/) | Researches a recurring job, prepares a candidate agent or team and its passport, stages a kit, and verifies the original task after discovery. | The exact staged artifact works in its declared scope. Installation and live effects require their own receipts. |
| [Skill constructor](../kit/skills/design-specialist-skills/) | Designs a focused skill or a family, including clear triggers, boundaries, resources, tests and handoffs. | Representative requests trigger the intended capability, nearby requests do not, and the actual consumer can use the output. |
| [App Atelier](../kit/skills/app-atelier-director/) | Research, concepts, specs, experience, build, growth, support, QA, release and operations for Android, iOS and web. | Check the actual artifact and target platform for the agreed scope. |
| [ChatBot Atelier](../kit/skills/chatbot-atelier-director/) | Product research, conversation, specification, knowledge, integrations, media, build, QA, release and operations. | Check message behavior, state, permissions, media and delivery in the intended channels. |
| [Game Atelier](../kit/skills/gamedev-director/) | Studio, concepts, preproduction, assets, build, QA, release and live operations. | Check gameplay, assets, controls, performance and recovery on their intended media or devices. |
| [Native specialist roles](../agent-profiles/) | Architecture, backend, conversation, cost, integrations, judgment, platforms, privacy, product, QA, reliability and skeptical review. | Observe the role actually start and return a result for exact scoped inputs. A role profile describes behavior. The host enforces permissions. |
| [Maintenance](../maintenance-skill/) | Audits changed sources, records impact, builds packages, checks adoption and preserves project state. | An artifact, GitHub read-back, installed files and fresh discovery each verify a different stage. |
| [Agent Atelier workbench](../apps/agent-atelier/) | Local project and work portfolio, source-backed continuation, task preparation, supported dispatch, connections and media. | Inspect the actual instance, operation and native result. |

## Tools and data paths

| Need | Available route | Conditions |
| --- | --- | --- |
| Review or change a repository | Codex skills, shell, file tools, Git and relevant scripts | Use the actual repository, sandbox, current branch, inputs and verified result. |
| Use a native Codex role | Configured role profile and native delegation | Use a persisted parent session where required. Give one bounded task with a result and a return address. |
| Inspect native Codex work | App-server, CLI, or read-only workbench portfolio | Bind the actual project and preserve thread, source and task identity. Paged history can be incomplete. |
| Resume or dispatch Codex work | Native Codex or a supported workbench handoff | Require idle ownership and pinned source. If saved execution context is unavailable, use the native host or prepare a fresh scoped task. The workbench does not fence a separate Desktop writer. |
| Search files or reference material | Exact paths, IDs, source reads, lexical search; optional scoped index | Compare retrieval and grounded-answer quality before adding embeddings. Enforce scope, source version, deletion and rebuild policies. |
| Use a Model Context Protocol (MCP) connector or provider | Host-managed connector or supported workbench operation | Check the exact schema, target, rights and observed effect. Connection, read support and write support are separate. |
| Research OpenAI docs or generate an image | Documented Agent Atelier OpenAI Docs and native Codex image operations | See the [local API](../apps/agent-atelier/shared/API.md) for the operation, output and evidence. Other platforms and formats need their own supported consumer. |
| Discover connections, assets or repository metadata | [Workbench plugin, app and managed connector inventory; Openverse image/audio search; GitHub CLI metadata](../apps/agent-atelier/shared/API.md#plugin-and-media-connections) | Inspect actual tool scope, original asset rights and account access. A catalog entry does not prove a tool ran. |
| Work with data, predictions, or model adaptation | Existing specialist with the relevant [AI and data production profile](../standards/ai-production.md) | Record provenance, schema and scope. Compare the simplest sufficient method and evaluate the downstream result. |
| Produce or inspect media and interfaces | Family asset workflow, native rendering or a compatible media provider | Preserve the accepted originals. Verify a representative output in the real medium before batch production. Inspect the actual file or intended interaction. |
| Evaluate behavior | Repository fixtures, Codex CLI or supported runtime, domain graders and independent review | Pin scope, source, input, model and configuration. Separate structural checks from native and external evidence. |
| Distribute or update | Core [portable kit](../kit/), host profiles, optional packages and local service migration | Review the current target and exact predecessor. Preserve identities and local changes. Check each installed scope with its supported verification and rollback. |

## Add a workflow

1. Record the original result, real inputs, acceptance check, target environment and permitted effects.
2. Try the available direct route or a current specialist. Introduce a reusable skill or agent for a demonstrated recurring gap.
3. Keep behavior-changing instructions short and describe when they apply. Put specialized resources behind precise references. Move repeatable validation and authority checks to the actual consumer where feasible.
4. Give separately owned work its needed source pins, paths, output, limits and revision. Continue from authoritative data after restart. Stop unsafe retries until a consuming outcome is reconciled.
5. Record a representative success and relevant negative case. Test the exact package and freshly discovered source before replacing a managed install.

[Start here](../START_HERE.md) · [Engineering guide](OPERATING_MODEL.md) · [Context and resume](../standards/context-capsule.md) · [Update and preservation contract](../governance/UPDATE_CONTRACT.md)
