# Start using Codex Agent System

[Repository home](README.md) · [Illustrated workflows](marketing/README.md) · [Technical topics](README.md#technical-topics)

Choose your guide, install the pieces you need, and finish one task in a disposable project. If you already have a project, start with [its decisions and context](docs/OPERATING_MODEL.md#project-context-and-handoffs). If you want to see concrete examples first, open [My Day](marketing/en/README.md#showcase-product) or [Global Logistics](marketing/en/README.md#showcase-operations).

| Language | Complete guide |
| --- | --- |
| English | [Open the guide](docs/en/GUIDE.md) |
| Українська | [Відкрити посібник](docs/uk/GUIDE.md) |
| Deutsch | [Anleitung öffnen](docs/de/GUIDE.md) |
| Italiano | [Apri la guida](docs/it/GUIDE.md) |
| Español | [Abrir la guía](docs/es/GUIDE.md) |
| Français | [Ouvrir le guide](docs/fr/GUIDE.md) |
| 简体中文 | [打开指南](docs/zh-CN/GUIDE.md) |

## Install and verify

1. [Install in Codex](docs/INSTALL.md). Download the stable Codex archive, verify its GitHub attestation, and inspect the installation plan before applying it. The procedure includes a fresh session check and recovery.
2. Start with a small, observable change in a disposable folder. Create `README.md` with `# Cheklist` and `notes.txt` with a line you want preserved. In a fresh Codex chat opened in that folder, request the following:

   ```text
   Correct the spelling of the heading in README.md. Keep notes.txt intact.
   Show the resulting heading and how you verified both files.
   ```

   Expect the heading `# Checklist` and the original contents of `notes.txt`. For a repeatable runtime check, use the [native eval canary](evaluations/README.md#run-a-focused-native-codex-canary).
3. For coordination install the optional Atelier Orchestrator, then start with `$atelier-orchestrator`. For a specific job, choose a [skill or product director](docs/CAPABILITIES.md#all-skills-and-roles). To see native Codex projects and bounded work in a browser, [launch Agent Atelier on your Mac](apps/agent-atelier/README.md#build-and-launch).

## Use another language

You can work in any language your Codex session handles. The seven guides above are the maintained written editions. Give Codex the following request for a guided adaptation into another language:

```text
Guide me through Codex Agent System in [language]. Read START_HERE.md and
follow the relevant links for the task I describe. Keep all commands, paths,
skill names, flags, source citations, and permission boundaries exact.
Explain each action in my language, including what I should observe and
how to recover if a check fails. Start with the smallest useful result.
```

For project-wide language preferences, record `preferred_language` in [project context](templates/project-context.json) and include it in handoffs.

## Keep going

- **Pick a workflow:** [App, ChatBot, and Game](docs/CAPABILITIES.md#product-families) · [Constructors and roles](docs/CAPABILITIES.md#constructors-and-roles) · [Agent Atelier](apps/agent-atelier/README.md).
- **Understand how it works:** [Harness and permissions](docs/OPERATING_MODEL.md#harness-and-authority) · [Context and handoffs](docs/OPERATING_MODEL.md#project-context-and-handoffs) · [Routing and subagents](docs/OPERATING_MODEL.md#routes-and-subagents).
- **Design and verify a knowledge workflow:** [RAG and vector search](docs/OPERATING_MODEL.md#retrieval-and-rag) · [Worked RAG example](docs/technical/RETRIEVAL.md) · [Evals and evidence](docs/OPERATING_MODEL.md#evals-and-evidence).
- **Operate it:** [Tool receipts and recovery](docs/OPERATING_MODEL.md#tools-evidence-and-recovery) · [Model choice and cost](docs/OPERATING_MODEL.md#models-and-cost) · [Install and update](docs/INSTALL.md).
