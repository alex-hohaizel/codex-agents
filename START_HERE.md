# Start using Codex Agent System

Already have the skills in Codex? Open a fresh chat in a practice folder
and run the first task below. New installation? Ask Codex to guide you
through the official setup and show what each step found. If you work from
the terminal, follow the exact release procedure and run the canary.
[Repository home](README.md) · [Illustrated workflows](marketing/README.md) · [Documentation index](docs/INDEX.md)

## Install and verify

1. **Install the 33 core skills.** Follow the signed release setup. In a Codex
   chat you can ask for help identifying your installed version and reviewing
   the exact audit before any changes. The setup uses local tools and
   permissions. If your chat cannot run a step, use the command shown in the
   installation guide or ask the person who manages that computer.
   [Install, update, verify, and roll back](docs/INSTALL.md)
2. **Open a practice folder.** In your file manager and text editor, make a
   disposable folder. Save a plain-text file named exactly `README.md`
   with the line `# Cheklist`. Save `notes.txt` with a line you want to
   keep. Open a new Codex chat in that folder and paste this request.

   ```text
   Correct Cheklist to Checklist in the heading of README.md in this folder.
   Keep any other content and notes.txt unchanged. Read notes.txt before
   and after the edit and confirm it stayed the same. Show me the resulting
   heading and the file you changed.
   ```

   Look for `# Checklist`, an edit limited to the heading, and the same
   `notes.txt`. This is a useful first check of the workspace. To repeat it
   with a machine-readable receipt, run the native direct repair case.
   [Repeatable first check](evaluations/README.md#run-a-focused-native-codex-canary)
3. **Check skill discovery.** In a fresh chat in the same folder, select
   `$agent-foundry` from the skill picker when your host shows it. Ask Codex
   to report the loaded source path and version. In a chat without a picker,
   use the exact skill name and ask which source the host resolved. If the
   skill is missing or the source differs, check the installed path with the
   setup receipt before using it. [Fresh session verification](docs/INSTALL.md#verify)

## Choose the entry point for your work

| Entry point | When to use it | How to find it |
| --- | --- | --- |
| **Core skills in Codex** | A known domain task or a reusable specialist | In a project chat, select the relevant skill, such as `$app-atelier-director` for an app or `$agent-foundry` for building an agent. [Skill catalog](docs/CAPABILITIES.md#all-skills-and-roles) |
| **Atelier Orchestrator** | Choosing a route, coordinating roles, or resuming existing work | Install the optional skill separately. In a fresh Codex chat, use `$atelier-orchestrator`. [Optional installation](docs/INSTALL.md#optional-components) |
| **Agent Atelier for Mac** | Browsing local Codex projects, reviewing task sources, and following prepared work in a browser | Build and launch the local workbench using its guide. On Mac, double-click `launcher/Agent Atelier.command` after building. [Workbench build and launch](apps/agent-atelier/README.md#build-and-launch) |

Continue the same example by briefing a recurring review, creating a
specialist, bringing in a real team, and handing off the result.
[First task through handoff](docs/FIRST_RUN.md#extend-the-task-into-a-project-workflow) ·
[Exact commands and checks](docs/FIRST_RUN.md#precision-path)

## Use another language

Use the written guide for your language or ask Codex to guide you through
the task in your preferred language. Keep commands, paths, skill names,
flags, source references, and permission limits exact.

| Language | Complete guide |
| --- | --- |
| English | [Open the guide](docs/en/GUIDE.md) |
| Українська | [Відкрити посібник](docs/uk/GUIDE.md) |
| Deutsch | [Anleitung öffnen](docs/de/GUIDE.md) |
| Italiano | [Apri la guida](docs/it/GUIDE.md) |
| Español | [Abrir la guía](docs/es/GUIDE.md) |
| Français | [Ouvrir le guide](docs/fr/GUIDE.md) |
| 简体中文 | [打开指南](docs/zh-CN/GUIDE.md) |

For an ongoing project, record `preferred_language` in its context and
carry it into handoffs. [Project context](templates/project-context.json)

## Keep going

- Take an existing product forward using its current owner, requirements,
  decisions and checkpoint. [Project context and handoffs](docs/OPERATING_MODEL.md#project-context-and-handoffs)
- Pick a domain workflow. [App, ChatBot, and Game](docs/CAPABILITIES.md#product-families) · [Constructors and roles](docs/CAPABILITIES.md#constructors-and-roles)
- Explore worked examples. [My Day](marketing/en/README.md#showcase-product) · [Global Logistics](marketing/en/README.md#showcase-operations)
- Verify the result in its real environment. [Tools, evidence, and recovery](docs/OPERATING_MODEL.md#tools-evidence-and-recovery) · [Evals](docs/OPERATING_MODEL.md#evals-and-evidence)
