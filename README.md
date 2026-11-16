# Codex Agent System

Reusable Codex skills, specialist roles, and a local Mac workbench. Use them to finish one task, run a repeatable product workflow, or design a specialist for work your team does often.

[English](docs/en/GUIDE.md) · [Українська](docs/uk/GUIDE.md) · [Deutsch](docs/de/GUIDE.md) · [Italiano](docs/it/GUIDE.md) · [Español](docs/es/GUIDE.md) · [Français](docs/fr/GUIDE.md) · [简体中文](docs/zh-CN/GUIDE.md) · [Another language](START_HERE.md#use-another-language)

[Stable download](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Component versions](releases/README.md) · [What is included](docs/CAPABILITIES.md#built-in-optional-or-supplied-by-your-project)

**Jump to:** [RAG](docs/OPERATING_MODEL.md#retrieval-and-rag) · [Evals](docs/OPERATING_MODEL.md#evals-and-evidence) · [Harness](docs/OPERATING_MODEL.md#harness-and-authority) · [Context](docs/OPERATING_MODEL.md#project-context-and-handoffs) · [Showcase](#illustrated-workflows)

<a name="your-first-task"></a>
<a name="choose-a-path"></a>

## Choose where to start

| If you want to… | Go directly to… |
| --- | --- |
| **Try it** — install, then see one real result | [Install in Codex](docs/INSTALL.md) · [Run your first task](START_HERE.md#install-and-verify) |
| **Build something** — choose a workflow, study an example, or create a specialist | [App, ChatBot, and Game workflows](docs/CAPABILITIES.md#product-families) · [Illustrated examples](#illustrated-workflows) · [Constructors and roles](docs/CAPABILITIES.md#constructors-and-roles) |
| **Inspect the engineering** — understand the design or verify a claim | [Technical topics](#technical-topics) · [All skills and roles](docs/CAPABILITIES.md#all-skills-and-roles) · [What the checks prove](governance/VALIDATION.md) |

<a name="how-it-works"></a>

## Technical topics

Each link opens the relevant section. Use the [engineering guide](docs/OPERATING_MODEL.md) for the whole system.

| Topic | What you can do there |
| --- | --- |
| [**RAG and vector search**](docs/OPERATING_MODEL.md#retrieval-and-rag) | Start with exact sources and lexical search. Decide whether embeddings help, then [follow a worked example](docs/technical/RETRIEVAL.md). |
| [**Evaluations (evals)**](docs/OPERATING_MODEL.md#evals-and-evidence) | Choose behavioral tests, evidence, and failure cases. [Run a real Codex canary](evaluations/README.md#run-a-focused-native-codex-canary). |
| [**Harness and permissions**](docs/OPERATING_MODEL.md#harness-and-authority) | See which layer controls instructions, tool access, workflow state, and acceptance. |
| [**Context capsules and handoffs**](docs/OPERATING_MODEL.md#project-context-and-handoffs) | Carry decisions, source revisions, and the next allowed action into a new task or session. |
| [**Routing, skills, and subagents**](docs/OPERATING_MODEL.md#routes-and-subagents) | Choose direct work, a skill, a director, delegation, or a new agent. |
| [**Model choice and cost**](docs/OPERATING_MODEL.md#models-and-cost) | See where settings come from and how to compare task quality with cost and time. |
| [**Tools, receipts, and recovery**](docs/OPERATING_MODEL.md#tools-evidence-and-recovery) | Check what a connector can do, prove an effect, and recover when an outcome is unknown. |
| [**Agent Atelier for macOS**](apps/agent-atelier/README.md) | Inspect local Codex projects, prepare a scoped task, and review its evidence in the workbench. |

<a name="see-what-you-can-build"></a>

## Illustrated workflows

See the product concepts and the diagrams that explain how the workflows operate. These examples cover a small selection of possible uses.

[My Day: revise a daily plan](marketing/en/README.md#showcase-product) · [Global Logistics: handle a delayed shipment](marketing/en/README.md#showcase-operations) · [Sunridge Studio: build a playable slice](marketing/en/README.md#showcase-game)

[RAG: answer from permitted sources](marketing/en/README.md#showcase-retrieval) · [Evals: compare outcomes](marketing/en/README.md#showcase-evaluation) · [All illustrated workflows](marketing/README.md) · [Огляд українською](marketing/uk/README.md)

[![A logistics network, a daily planner and a coastal game world in the visual showcase](assets/marketing/current/overview.png)](marketing/README.md)

[Release and package verification](governance/PACKAGES.md) · [Contributor and update process](governance/UPDATE_CONTRACT.md) · [Rights](RIGHTS.md)
