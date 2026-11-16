# Capabilities, skills, and roles

Choose the result you want and where it must work. The same project can use a direct Codex request, a reusable skill, a native specialist role, or an agent with its own package. Its own requirements, decisions, and acceptance evidence remain the record of the work. [Engineering guide](OPERATING_MODEL.md)

## Product families

| Family | Workflow | Example of acceptance |
| --- | --- | --- |
| App Atelier | Research the need, choose a concept, specify behavior, design and build the UX, verify, release, and operate | A target client performs the agreed flow, including the expected failure and recovery behavior |
| ChatBot Atelier | Shape the product, language, knowledge corpus, integrations, media, runtime, and support | The intended channel exhibits the approved behavior, cites the permitted current sources, and records action receipts |
| Game Atelier | Define studio identity, playable concepts, systems and assets, build, test, release, and evolve | The agreed gameplay loop runs on the target environment, with evidence for controls, performance, recovery, and media |

## Constructors and roles

**Agent Foundry** turns recurring work into an agent, a team where needed, and a source-backed passport of tasks, constraints, tools, and checks. Review the exact passport before construction, stage the package, discover it in a fresh consumer, and exercise the original job. **Design Specialist Skills** builds a narrow function or family of reusable skills. Check the trigger against a matching request and nearby requests, then test the actual output.

**Atelier Orchestrator** picks a proportionate route, continues bound projects, and keeps ownership and handoffs visible. Its conversational entry is `$atelier-orchestrator`. **Repository maintenance** handles authorized reusable source changes, evidence, packaging, and reviewed adoption. Install these two optional skills individually. [Installation](INSTALL.md#optional-components)

Native Codex specialist roles are `foundry-architecture`, `foundry-backend`, `foundry-conversation`, `foundry-cost`, `foundry-integrations`, `foundry-judge`, `foundry-platform`, `foundry-privacy`, `foundry-product`, `foundry-qa`, `foundry-reliability`, and `foundry-skeptic`. Assign each actor scoped inputs, an owned result, and an evidence standard. Check the actor actually started and returned its result. [Role manifest](../agent-profiles/manifest.json)

## All skills and roles

| Selector | Responsibility |
| --- | --- |
| [`$agent-foundry`](../kit/skills/agent-foundry/SKILL.md) | Design, build, and verify an agent or team for a recurring job |
| [`$design-specialist-skills`](../kit/skills/design-specialist-skills/SKILL.md) | Define triggers, workflow, resources, and evals for reusable skills |
| [`$app-atelier-director`](../kit/skills/app-atelier-director/SKILL.md) | Lead an application project through its lifecycle |
| [`$app-atelier-research`](../kit/skills/app-atelier-research/SKILL.md) | Find evidence for user needs, services, and market constraints |
| [`$app-atelier-concepts`](../kit/skills/app-atelier-concepts/SKILL.md) | Compare viable product directions, experience, cost, and scope |
| [`$app-atelier-specification`](../kit/skills/app-atelier-specification/SKILL.md) | Specify behavior, data, API, identity, and payments |
| [`$app-atelier-experience`](../kit/skills/app-atelier-experience/SKILL.md) | Design visual identity, interactions, states, and accessibility |
| [`$app-atelier-build`](../kit/skills/app-atelier-build/SKILL.md) | Build the agreed native or web implementation and integrations |
| [`$app-atelier-growth`](../kit/skills/app-atelier-growth/SKILL.md) | Select and prepare a measurable, authorized acquisition route |
| [`$app-atelier-support`](../kit/skills/app-atelier-support/SKILL.md) | Build support knowledge, escalation, and bounded actions |
| [`$app-atelier-qa`](../kit/skills/app-atelier-qa/SKILL.md) | Review product, design, functional and recovery risk |
| [`$app-atelier-release`](../kit/skills/app-atelier-release/SKILL.md) | Prepare scoped publication, records, and recovery |
| [`$app-atelier-operations`](../kit/skills/app-atelier-operations/SKILL.md) | Manage changes, incidents, reliability, support, and costs |
| [`$chatbot-atelier-director`](../kit/skills/chatbot-atelier-director/SKILL.md) | Keep chatbot scope, implementation, and outcomes coherent |
| [`$chatbot-atelier-research`](../kit/skills/chatbot-atelier-research/SKILL.md) | Map users, channels, domain, competitors, and risks |
| [`$chatbot-atelier-specification`](../kit/skills/chatbot-atelier-specification/SKILL.md) | Define architecture, behavior, context, and state contracts |
| [`$chatbot-atelier-conversation`](../kit/skills/chatbot-atelier-conversation/SKILL.md) | Design dialogue, voice, interaction, boundaries, and confirmation |
| [`$chatbot-atelier-knowledge`](../kit/skills/chatbot-atelier-knowledge/SKILL.md) | Prepare scoped knowledge, retrieval, grounded answers, and lifecycle |
| [`$chatbot-atelier-integrations`](../kit/skills/chatbot-atelier-integrations/SKILL.md) | Specify tools, delivery, idempotency, and integration receipts |
| [`$chatbot-atelier-media`](../kit/skills/chatbot-atelier-media/SKILL.md) | Produce and verify images, audio, and other channel assets |
| [`$chatbot-atelier-build`](../kit/skills/chatbot-atelier-build/SKILL.md) | Implement and integrate the agreed chatbot workflow |
| [`$chatbot-atelier-qa`](../kit/skills/chatbot-atelier-qa/SKILL.md) | Verify conversation, data, roles, boundaries, and recovery |
| [`$chatbot-atelier-release`](../kit/skills/chatbot-atelier-release/SKILL.md) | Stage, publish within scope, verify, and prepare rollback |
| [`$chatbot-atelier-operations`](../kit/skills/chatbot-atelier-operations/SKILL.md) | Monitor channels, records, failures, and safer retries |
| [`$gamedev-director`](../kit/skills/gamedev-director/SKILL.md) | Coordinate a game from studio and intent through live operations |
| [`$gamedev-studio`](../kit/skills/gamedev-studio/SKILL.md) | Define studio practice, identity, responsibilities, and intake |
| [`$gamedev-concepts`](../kit/skills/gamedev-concepts/SKILL.md) | Develop and compare testable game loops and directions |
| [`$gamedev-preproduction`](../kit/skills/gamedev-preproduction/SKILL.md) | Specify systems, content, runtime contracts, and production scope |
| [`$gamedev-assets`](../kit/skills/gamedev-assets/SKILL.md) | Author and verify a coherent asset and media pipeline |
| [`$gamedev-build`](../kit/skills/gamedev-build/SKILL.md) | Implement gameplay and integrate assets and platform capabilities |
| [`$gamedev-qa`](../kit/skills/gamedev-qa/SKILL.md) | Test the user journey, performance, saves, and recovery |
| [`$gamedev-release`](../kit/skills/gamedev-release/SKILL.md) | Prepare release artifacts, supported publication, and rollback |
| [`$gamedev-liveops`](../kit/skills/gamedev-liveops/SKILL.md) | Support live updates, telemetry, issues, and player experience |
| [`$atelier-orchestrator`](../optional-skills/atelier-orchestrator/SKILL.md) | Choose direct, specialist, project, or construction routes |
| [`$codex-agents-maintenance`](../maintenance-skill/SKILL.md) | Maintain reusable sources, product documentation, and releases |

## Tools and data paths

| Need | Available path and scope |
| --- | --- |
| Inspect or change a local repository | Native Codex tools, shell, Git, reviewed source paths, and scoped working copies |
| Delegate a check | A configured native role, task-specific inputs, and an actual child result in the parent host |
| Discover projects and continue work | Agent Atelier’s local portfolio, work inspection, explicit project binding, task preparation, and bounded native Codex dispatch |
| Read long native records | Paged local history and source views with explicit coverage. Continue a native chat only with supported context and an idle handoff |
| Inspect capability and account availability | The workbench’s connection inventory. Each operation still requires its own native support, access, and observed result |
| Research official OpenAI docs or produce a PNG | Documented Agent Atelier OpenAI Docs MCP and native Codex image operation using a supported host and sign-in |
| Discover files, repo metadata, or media | Exact files and lexical searches, GitHub CLI read metadata under an authenticated account, and supported Openverse image/audio search with license and origin evidence |
| Use tools and integrations | Supported host connector, explicit target and scope, exact permissions and receipt. Source availability, reading, and changing are distinct observations |
| Add RAG, model or data work | Existing domain skill, scoped corpus and authoritative sources, applied AI/data profile, and retrieval and downstream evals |
| Verify behavior and outputs | Structural checks, native fixtures, domain evals, and independent review of the actual consumer or medium |
| Publish or update managed components | The official stable asset, attestation, exact plan and journal, and a fresh native check |

[Local workbench API](../apps/agent-atelier/shared/API.md) · [Retrieval and evals](OPERATING_MODEL.md#retrieval-and-rag) · [Install and recover](INSTALL.md) · [Visual showcase](../marketing/README.md)
