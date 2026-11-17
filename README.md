# Codex Agent System

**One conversation. A whole product team. From the first idea to release evidence.**

Start with a goal in your own words. Codex helps you choose the smallest
workflow that fits, bring in the specialists you need, and keep the sources,
decisions, and next action with the project. Use it for one task, a whole
product, or an agent your team can use again.

**[Start in Codex](START_HERE.md)** · **[Install or update](docs/INSTALL.md)** · **[See the workflow](#one-entry-from-idea-to-release)** · **[Browse all documentation](docs/INDEX.md)** · [Почати українською](docs/uk/FIRST_RUN.md)

<a name="your-first-task"></a>
<a name="choose-a-path"></a>

## Choose where to start

| I want to… | Start here |
| --- | --- |
| **Try one task** | [Guided start](START_HERE.md#install-and-verify) for a small, observable result in a fresh Codex chat. [Exact setup commands](docs/INSTALL.md) are available if you prefer the terminal. |
| **Run a project from one conversation** | Start with the optional `$atelier-orchestrator`, or call a [product director](docs/CAPABILITIES.md#product-families) for an app, chatbot, or game. [Follow a complete example](docs/technical/END_TO_END.md). |
| **Build a reusable specialist** | Start with `$agent-foundry` for an agent or `$design-specialist-skills` for a specialist skill family. [Constructors and roles](docs/CAPABILITIES.md#constructors-and-roles) |
| **Work in a visual interface on Mac** | [Build and launch Agent Atelier](apps/agent-atelier/README.md#build-and-launch) to browse local Codex projects, prepare tasks, and inspect evidence in a browser. |

<a name="one-entry-from-idea-to-release"></a>

## One entry, from idea to release

[![Workflow map: a request flows through route and scope, product, architecture, build, and independent QA. Results go to delivery with evidence or back to a checkpoint for recovery.](assets/marketing/release-1.7/workflow-en.svg)](docs/technical/END_TO_END.md)

[Follow the worked project with copyable prompts](docs/technical/END_TO_END.md) · [Open diagram at full size](assets/marketing/release-1.7/workflow-en.svg) · [Схема українською](assets/marketing/release-1.7/workflow-uk.svg)

1. **State the goal.** Open a project in Codex. Describe the outcome, existing sources, and limits. Use `$atelier-orchestrator` when you want one coordinating conversation.
2. **Choose a route.** The orchestrator can suggest direct work, a focused skill, or a product director. When a job will recur, the constructor helps define and verify a reusable specialist.
3. **Give the team distinct jobs.** Product sets the goal and acceptance criteria. Architecture settles shared contracts. Builders own bounded changes in separate worktrees when useful. An independent reviewer checks the integrated result.
4. **Carry context through changes and recovery.** Retain sources, decisions, and checkpoints. Trace a changed requirement to the tasks and evidence it affects. Reconcile an uncertain external action before trying again.
5. **Review, hand off, and ship.** Connect the exact candidate to observed results and the next action. Apply an approved release or tracker action under the project's own authority.

## What carries through a difficult project

- A requirement changes: [see the affected task and proof](docs/technical/TICKET_CHANGE_REVIEW.md) and the [reviewed replan](docs/technical/TICKET_REPLAN.md).
- Two builders work at once, or one stops: [tie their own worktrees and checkpoints to the exact base](docs/technical/TICKET_WORKTREES.md).
- An external response is lost: [read back what the provider actually did](docs/technical/TRACKER_SYNC.md) before another effect.
- A new owner needs to deliver the result: [find the exact candidate, observed behavior, and acceptance decisions](docs/technical/TICKET_QUALITY_GATE.md).

<a name="what-is-new-in-v170"></a>

## What you can do

| Work | Product routes |
| --- | --- |
| **Explore an idea and agree on the plan** | [Resumable workshops](docs/technical/WORKSHOP.md) · [Team deliberation](optional-skills/atelier-orchestrator/references/team-deliberation.md) · [Brief and PRFAQ](docs/technical/PRODUCT_FACILITATION.md) · [Reusable document templates](docs/technical/DOCUMENT_TEMPLATES.md) |
| **Design and test the experience** | [Interactive UX prototype](docs/technical/UX_PROTOTYPE.md) ties screens, errors, and recovery to reviewed design and experience sources. [PRD and architecture](docs/technical/TICKET_PRODUCT_SPEC.md) keep technical decisions attached to requirements. |
| **Assemble agents and migrate existing work** | [Skill and role catalog](docs/CAPABILITIES.md#all-skills-and-roles) · [Native skill and role import](docs/technical/CONSTRUCTOR_IMPORT.md) · [Module import and migration](docs/technical/MODULE_MIGRATION.md) |
| **Plan changes, track them, and build in parallel** | [Requirement impact](docs/technical/TICKET_CHANGE_REVIEW.md) · [Reviewed replan](docs/technical/TICKET_REPLAN.md) · [Ticket tree and sprint continuity](docs/technical/TICKET_TREE.md) · [Parallel worktrees](docs/technical/TICKET_WORKTREES.md) |
| **Connect a ticket tree to a tracker** | [Preview, apply, and reconcile](docs/technical/TRACKER_SYNC.md) one reviewed effect. [Configure GitHub, Linear, Jira Cloud, Notion, or Trello](docs/technical/TRACKER_PROVIDERS.md). [Mapped GitHub Issues](docs/technical/TICKET_GITHUB.md) also have a focused route. |
| **Check a result and hand it off** | [Candidate quality gate](docs/technical/TICKET_QUALITY_GATE.md) · [Behavioral evaluations](evaluations/README.md) · [Recover an interrupted workflow](docs/OPERATING_MODEL.md#tools-evidence-and-recovery) · [Package and release verification](governance/PACKAGES.md) |

## Product guides

| Section | Where to go |
| --- | --- |
| **Getting started** | [First task in Codex](START_HERE.md) · [Deeper guided setup](docs/FIRST_RUN.md) · [Installation, verification, and rollback](docs/INSTALL.md) |
| **How the system fits together** | [Worked project](docs/technical/END_TO_END.md) · [Operating model](docs/OPERATING_MODEL.md) · [All skills and roles](docs/CAPABILITIES.md#all-skills-and-roles) |
| **Product families** | [App Atelier](docs/CAPABILITIES.md#product-families) · [ChatBot Atelier](docs/CAPABILITIES.md#product-families) · [Game Atelier](docs/CAPABILITIES.md#product-families) · [Agent Atelier for macOS](apps/agent-atelier/README.md) |
| **All procedures and reference** | [Documentation index](docs/INDEX.md) · [Release and component versions](releases/README.md) · [Stable downloads](https://github.com/alex-hohaizel/codex-agents/releases/latest) |
| **Localized guides** | [English](docs/en/GUIDE.md) · [Українська](docs/uk/GUIDE.md) · [Deutsch](docs/de/GUIDE.md) · [Italiano](docs/it/GUIDE.md) · [Español](docs/es/GUIDE.md) · [Français](docs/fr/GUIDE.md) · [简体中文](docs/zh-CN/GUIDE.md) · [Another language](START_HERE.md#use-another-language) |

<a name="how-it-works"></a>

## Technical topics

| When you need… | Open |
| --- | --- |
| **Work grounded in your own sources** | [Context and handoffs](docs/OPERATING_MODEL.md#project-context-and-handoffs) · [Retrieval and RAG](docs/OPERATING_MODEL.md#retrieval-and-rag) · [Worked retrieval example](docs/technical/RETRIEVAL.md) |
| **Clear boundaries for models, tools, and roles** | [Harness and authority](docs/OPERATING_MODEL.md#harness-and-authority) · [Routing and subagents](docs/OPERATING_MODEL.md#routes-and-subagents) · [Model choice and cost](docs/OPERATING_MODEL.md#models-and-cost) |
| **Proof that a change works** | [Evaluations and evidence](docs/OPERATING_MODEL.md#evals-and-evidence) · [Native Codex canary](evaluations/README.md#run-a-focused-native-codex-canary) · [Reproduce evidence on a pinned task](docs/technical/CODEX_COMPARISONS.md) |
| **Recovery from a partial or unknown outcome** | [Tools, receipts, and recovery](docs/OPERATING_MODEL.md#tools-evidence-and-recovery) · [Verification expectations](governance/VALIDATION.md) · [Install and rollback](docs/INSTALL.md) |

<a name="see-what-you-can-build"></a>

## Illustrated workflows

[![A logistics network, a daily planner, and a coastal game world. Illustration of possible product workflows.](assets/marketing/current/overview.png)](marketing/README.md)

[My Day: revise a daily plan](marketing/en/README.md#showcase-product) · [Global Logistics: handle a delayed shipment](marketing/en/README.md#showcase-operations) · [Sunridge Studio: build a playable slice](marketing/en/README.md#showcase-game) · [RAG](marketing/en/README.md#showcase-retrieval) · [Evals](marketing/en/README.md#showcase-evaluation) · [Усі ілюстрації](marketing/uk/README.md)

[Stable release](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Component versions](releases/README.md) · [Package verification](governance/PACKAGES.md) · [Contributor and update process](governance/UPDATE_CONTRACT.md) · [Rights](RIGHTS.md)
