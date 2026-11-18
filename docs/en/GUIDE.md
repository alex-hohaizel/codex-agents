# Codex Agent System guide

Use Codex for a focused task, develop a product with specialists, or design a reusable agent. The system connects work to its actual source, an owner, and a result you can verify.

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md)

For a guided first session, open [Start here](../../START_HERE.md#install-and-verify). Then [follow one request through a complete project](../technical/END_TO_END.md), from assembling the team to reviewing its release evidence. [Read the whole system map](../../assets/marketing/release-1.7/workflow-en.svg) · [Documentation index](../INDEX.md)

The commercial buyer candidate has a coordinated setup and acquired-version records. Read [the buyer guide](../commercial/BUYER_GUIDE.md), [license terms](../commercial/LICENSING.md), and [runtime limits](../commercial/WORKBENCH_RUNTIME.md) before selecting that distribution.

## Choose where to start

- **Try Codex.** [Install and verify](#install) · [Do a first task](#first-task) · [See illustrated workflows](../../marketing/en/README.md)
- **Develop or run a project.** [Choose a workflow](#workflow) · [Find a skill or role](#catalog) · [Local workbench](#workbench) · [Operations and recovery](#operations)
- **Understand the system.** [Harness](#harness) · [Subagents](#subagents) · [Context capsules](#context) · [Models and cost](#models)
- **Find and verify evidence.** [Retrieval (RAG)](#retrieval) · [Evals](#evals) · [Tools and permissions](#permissions)

[Engineering topics](../OPERATING_MODEL.md#engineering-topics) · [Worked RAG example](../technical/RETRIEVAL.md) · [Product requirements](../../governance/requirements.csv)

<a name="install"></a>
## Install and check discovery

### Ready installer for Windows, macOS and Linux

If trusted delivery supplied a purchase confirmation or entitlement JSON, open **Keep your purchase document · optional** and choose that original file before preparing the plan. It stays private outside the package and skill folders. A changed document clears the old plan and approval; prepare and review a new plan. Updates automatically retain the existing purchase record. Document retention does not verify a purchase signature or grant rights. The technical installer also works without a purchase document.

Download the ready **Universal** archive or the matching OS/CPU asset from the [stable Release](https://github.com/alex-hohaizel/codex-agents/releases/latest). Fully extract it, read `START_HERE.html`, then open `Start.cmd` (Windows), `Start.command` (macOS), or `Start.sh` (Linux). The ready package includes Python, Node and the built interface; GitHub's automatic source ZIP is a source route. The wizard interface is English/Ukrainian; this guide covers the same workflow.

Use **Check now → Prepare plan → review destinations/conflicts → approve → Install reviewed plan → Verify files → Check in Codex**. The standard selection includes 33 skills, Orchestrator, the profile and twelve roles. Use your own Codex account for agent execution. **Create practice project → Open folder → Open Codex → Copy prompt** prepares the first exercise; it does not execute a model. Keep the journal. Recovery uses the selected saved operation and exact plan. [Complete installer and recovery guide](../INSTALL.md#recommended-local-browser-installer)

Project Python/venv and Node keep their priority. Use `AGENT_SYSTEM_PYTHON` for the toolkit's helper scripts. Maintenance remains a separate owner tool: use the bundled `product/maintenance-skill` or repository `maintenance-skill` through the supported skill manager, preview its source/target, then verify. Models and external services keep their own accounts and costs.

Personal skill locations follow the native Codex host. `CODEX_HOME` means the Codex home selected for that session; the audit shows the exact resolved destination.

| Installation scope | Skill directory |
| --- | --- |
| Windows personal skills | `CODEX_HOME/skills`, normally `<selected-home>/.codex/skills` |
| macOS / Linux personal skills | `<selected-home>/.agents/skills` (normally `~/.agents/skills`) |
| Project-local skills on every system | `<project>/.agents/skills` — unchanged |

For an earlier Windows personal installation under `<selected-home>/.agents/skills`, prepare a new audit with the current installer. The reviewed plan identifies the canonical target and retirement of recognized managed legacy copies; supported core icon-only tuning is preserved. Unknown source or policy edits and conflicting copies or icons require reconciliation instead of forced replacement. Do not manually move or delete either tree. Approve the exact migration plan, verify files and fresh Codex discovery, and retain its journal and backups. Rollback uses that original journal to restore the prior locations and owned bytes; already saved journals keep their validated original roots. [Root selection and migration](../INSTALL.md#personal-skill-roots)

### Advanced source route

1. Open the stable release for `alex-hohaizel/codex-agents`. On macOS or Linux, the terminal procedure uses Bash, Python 3.9+, Git, an authenticated GitHub CLI (`gh`), and Codex. For a guided installation, ask Codex to explain each step in English and keep flags and paths exact.
2. Follow the signed installation. The verifier checks the archive digest and its GitHub attestation against the source commit, workflow, and manifest. Select a fresh install when there is no managed suite, or supply the verified installed version for an existing suite. [Stable release](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Exact commands](../INSTALL.md#steps)
3. Read the audit for the 33 skills, destination, preservation of icon files and references, and any unresolved conflict. Apply the reviewed plan, retain the returned journal, and verify the files with that journal. Install the managed profile and twelve roles with their separate audit and journal if you need them. [Profile and roles](../INSTALL.md#profile-and-roles)
4. Install Orchestrator and maintenance separately if you need them. In Agent Atelier, preview the exact optional source, inspect the target and differences, then apply and verify. In Codex, use the supported personal-skill manager with the whole optional source. [Optional components](../INSTALL.md#optional-components)
5. Open a fresh Codex chat in the intended product folder. Use `$agent-foundry` or your selected skill. Where the host exposes the path, verify the resolved source against the installed one. A task with a visible result checks actual use. [Native discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work uses its own personal-skill interface. Use the Work asset and verify the records saved and loaded on that host. A local Codex update is independent of Work. [Packages](../../governance/PACKAGES.md)

<a name="first-task"></a>
## Make a first change

Create a disposable folder and open a fresh Codex chat there. Put `# Cheklist` into `README.md` and a line you want preserved into `notes.txt`. Ask Codex in English:

```text
Correct the heading in README.md. Keep notes.txt intact.
Show the resulting heading and how you checked both files.
```

Accept the result after observing `# Checklist` and the original `notes.txt`. For a focused task, a direct route is enough. For a larger project, give Orchestrator the outcome, project location, permitted changes and an observable acceptance check. For example, ask for a checkout-flow review that preserves the approved payment contract and returns only consistently reproducible issues. [Reproducible first task](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## Route a project and retain context

Work directly, invoke a skill, or ask `$atelier-orchestrator` to choose. Select a director for the whole lifecycle of an app, chatbot, or game. Use `$agent-foundry` for a recurring agent or team. Review its passport before construction, then test its staged package on an original task. Use `$design-specialist-skills` for a reusable workflow with clear triggers and acceptance cases.

<a name="harness"></a>
### Harness and authority

Codex supplies the runtime, tools, and permission controls. The repository supplies `AGENTS.md`, skill descriptions and resources, domain contracts, role definitions, and checks. Confirm the loaded instructions and apply authorization at the actual tool boundary. [Harness and authority](../OPERATING_MODEL.md#harness-and-authority)

<a name="subagents"></a>
### Roles and subagents

Delegate separate outputs or independent review. Name the actor, source revision, input paths, write scope, expected output, limits, stop condition, and return address. Keep a single writer for shared state. Collect the actual child result before integration. [Routes and subagents](../OPERATING_MODEL.md#routes-and-subagents)

A project that owns its backlog as a local ticket projection can draft, review, and apply an approved replan. Read the committed receipt before passing a ready ticket to Builder. Check the handoff again in the receiving Codex session and retain the returned result for independent review. [Approved replan and Builder handoff](../technical/TICKET_REPLAN.md)

For parallel work, assign separate Git worktrees at the same commit. Keep a checkpoint when a worker stops, verify it in the fresh session, and integrate only reviewed commits in a dedicated worktree. [Coordinate worktrees and resume](../technical/TICKET_WORKTREES.md)

Use the project projection to reconcile explicitly mapped GitHub Issues. Ask independent QA to link the acceptance criteria and risk checks to evidence from the exact candidate. Verify a suspected external effect at its destination before recording a decision. [Reconcile GitHub Issues](../technical/TICKET_GITHUB.md) · [Review candidate evidence](../technical/TICKET_QUALITY_GATE.md)

For a consequential decision, collect different specialist positions on the same evidence, then ask them to address the strongest disagreement. Let the decision owner choose the next step. [Deliberate with a team](../../optional-skills/atelier-orchestrator/references/team-deliberation.md)

Keep the original sprint plan as the backlog changes. Review proposed additions and dependencies before changing its scope. Check that both the PRD and architecture still describe every applicable requirement and request a fresh review of the new revision. [Sprint planning](../technical/TICKET_TREE.md#keep-a-sprint-plan-while-the-backlog-changes) · [Product specification review](../technical/TICKET_PRODUCT_SPEC.md)

Use an exact workshop record to continue brainstorming or challenge a proposal in a fresh session. Build a source-backed brief, PRFAQ, or separate design and experience documents with unresolved decisions visible. Audit imported Codex skills and roles before staging them in a fresh project. For an explicitly mapped GitHub issue, review one proposed change and read back the result before any repeat. [Workshop](../technical/WORKSHOP.md) · [Product facilitation](../technical/PRODUCT_FACILITATION.md) · [Constructor import](../technical/CONSTRUCTOR_IMPORT.md) · [GitHub writes](../technical/TICKET_GITHUB.md#apply-a-reviewed-change-to-a-mapped-issue)

Build an interactive browser prototype from reviewed DESIGN and EXPERIENCE, or use the template registry to keep drafts, revisions and reviews tied to exact sources. Audit an existing module and stage a reviewed migration in a fresh directory. For tracker trees, reconcile one effect after checking local, prior and remote state. [UX prototype](../technical/UX_PROTOTYPE.md) · [Templates](../technical/DOCUMENT_TEMPLATES.md) · [Module migration](../technical/MODULE_MIGRATION.md) · [Tracker tree](../technical/TRACKER_SYNC.md) · [Tracker providers](../technical/TRACKER_PROVIDERS.md)

<a name="context"></a>
### Context capsules

Start from authoritative project requirements, identity, current decisions and checkpoint. Pin exact source hashes and carry relevant requirements, allowed effects, deferred work, output, unresolved effects, and next action. If a source changes or is unavailable, verify the affected obligation again. A handoff carries this projection to another task or host. The original sources stay authoritative.

Record `preferred_language` in project context and pass it through handoffs. Keep commands, selectors, IDs, citations, and original quotations exact. [Operating model](../OPERATING_MODEL.md#project-context-and-handoffs) · [Project context](../../templates/project-context.json) · [Handoff](../../templates/HANDOFF.md)

<a name="models"></a>
### Models and cost

Record the model, reasoning setting, and result when comparing routes. Use a lower-cost setup when it passes the same acceptance checks on the same inputs. [Engineering reference for model choice and cost](../OPERATING_MODEL.md#models-and-cost)

<a name="retrieval"></a>
## Add knowledge retrieval and RAG

Start with verified paths, exact IDs, structured queries and lexical search. Add retrieval-augmented generation when relevant evidence often remains hard to find. Compare lexical, semantic, and hybrid retrieval on one authorized corpus before choosing an index or vector store. Check successful retrieval, faithful citations, no-answer behavior, mixed languages, revoked and stale sources, adjacent private projects, latency and cost. Keep permissions and source revision with each chunk, check rights before retrieval and citation, and support deletion or rebuilding. Retrieved text is data. Keep task authority in the project and actual tools.

Use `$chatbot-atelier-knowledge` for corpus, retrieval, grounded answer and lifecycle design. DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA and EVALUATION are profiles for work that needs them. Choose the smallest relevant profile and verify the actual downstream result. [Technical retrieval guide](../OPERATING_MODEL.md#retrieval-and-rag) · [AI and data profiles](../../standards/ai-production.md)

<a name="evals"></a>
## Test behavior and evidence with evals

Freeze representative inputs, source revision, model and host, expected outcome, failure cases and cost or time limits. Test explicit and natural routing, nearby requests, denied access, stale references and recovery. Check exact artifacts with their actual consumer and separate structural checks, native behavior, tool receipts and independent acceptance. Keep raw prompts and private paths in a private fixture.

From the repository root, run a small actual Codex canary with the native CLI and a supported sign-in:

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

It fixes the expected typo in a disposable project and checks the other file. Use the native suite for a scoped handoff, an approved constructor passport, or a fresh generated skill consumer. An external product claim requires evidence in its actual environment. [Eval suite, fixtures and receipts](../../evaluations/README.md) · [Validation](../../governance/VALIDATION.md)

<a name="workbench"></a>
## Work in Agent Atelier on Windows, macOS or Linux

Ready assets provide `Start-Workbench.cmd`, `Start-Workbench.command`, and `Start-Workbench.sh` for Windows, macOS and Linux. Open the matching launcher; no npm build is required for the ready interface. Check the release's declared native test coverage separately from runtime availability. The following source-build procedure remains an optional developer route; the project inspection and recovery steps apply to both routes. [Ready workbench and data recovery](../commercial/WORKBENCH_RUNTIME.md)

1. Open the current source and build with the pinned Node.js lockfile. From `apps/agent-atelier/`, run:

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. In the loopback panel, find the local project and inspect the reported coverage. Native registered projects may appear without chats. The panel loads selected history and artifacts when you open them. Preview the exact project folder and bind it explicitly. Demo mode uses fictional records.
3. Read the work item and its source-backed next action. Carry that action into the task form, check objective, acceptance, inputs, permissions and selected skills, then review the Orchestrator route. Prepare the task. Start only the authorized job and verify its result and receipt. Resume an existing chat only if its context, identity, and idle ownership are supported. Prepare a new scoped task when the saved context cannot be recovered there.
4. In Connections, inspect the availability of apps, plugins and connectors. When supported, the panel can query official OpenAI docs, preview and download a Codex-generated PNG, search Openverse image/audio with origin and license, and read repository metadata through an existing GitHub CLI login. Use only operations supported by the actual host and account. [Workbench operations](../../apps/agent-atelier/README.md) · [API and connection scope](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## Operate, recover, and update

<a name="permissions"></a>
### Tools and permissions

Before a tool write, verify operation, target, authorization, cost, limits and required receipt. After a timeout or a missing receipt, read authoritative state for the exact request, then retry only with current authority and a duplicate-prevention guarantee. Keep unresolved effects and evidence visible. Review outcomes in the real product, independent of successful preparation, command execution or file creation. [Tool effects and evidence](../OPERATING_MODEL.md#tools-evidence-and-recovery)

### Recovery and updates

Use the stable asset and exact plan for component updates. Keep journals and existing state. After an interruption, inspect the actual target before resuming. Roll back the core, profile, or optional kit using its own verified journal. Back up the workbench’s database and service-owned files with the documented procedure. Restart on the owned data directory and check the project inventory and a scoped task. Live product data, native chat and account state have their own owners and recovery rules. [Install and recovery](../INSTALL.md#rollback) · [Resumable work](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## Choose a skill or product family

| Selector | Start here for |
| --- | --- |
| `$atelier-orchestrator` | One place to choose, continue and coordinate the right route |
| `$agent-foundry` | An agent or team for a real recurring job |
| `$design-specialist-skills` | A focused reusable skill or family of skills |
| `$app-atelier-director` | App research, concepts, specification, UX, implementation, support, growth, QA, release and operations |
| `$chatbot-atelier-director` | Audience and channel research, product design, conversation, knowledge, integration, media, build, QA, release and operations |
| `$gamedev-director` | Studio, game concepts, preproduction, assets, build, QA, release and live operations |
| `$codex-agents-maintenance` | Authorized changes to reusable skills, documentation, release verification and packaging |

### Complete family and role inventory

**Application team**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · Lifecycle lead
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · User and market research
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · Product concepts
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · Requirements and contracts
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · Experience and accessibility
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · Implementation
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · Acquisition
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · Customer support workflow
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · Independent quality review
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · Release
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · Operations

**Chatbot team**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · Lifecycle lead
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · Audience and channel research
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · Behavior and state contracts
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · Conversation design
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · Knowledge and retrieval
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · Integrations and receipts
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · Media
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · Implementation
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · Quality review
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · Release
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · Operations and recovery

**Game team**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · Lifecycle lead
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · Studio practice
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · Playable concepts
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · Systems and production planning
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · Asset pipeline
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · Gameplay implementation
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · Quality review
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · Release
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · Live operations

**Codex specialist roles**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · Architecture
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · Backend
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · Conversations
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · Cost
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · Integrations
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · Independent judgment
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · Target platforms
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · Privacy
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · Product
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · Quality
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · Reliability
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · Critical review

The catalog lists every specialist by stable name and all twelve roles. [Full selector and role catalog](../CAPABILITIES.md#all-skills-and-roles) · [Visual workflows](../../marketing/en/README.md) · [Other languages](../../START_HERE.md#use-another-language)
