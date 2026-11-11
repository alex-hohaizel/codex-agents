# Agent System · Work + Codex

**A focused task. An existing product. A whole new direction.**

A reusable system of **33 specialized skills** for research, requirements, design, implementation, verification and continued improvement. Review a backend architecture, build an integration, restore an existing service, create an application or develop a game. The specialist team and depth follow the actual task.

[English](docs/en/GUIDE.md) · [Українська](docs/uk/GUIDE.md) · [Deutsch](docs/de/GUIDE.md) · [Italiano](docs/it/GUIDE.md) · [Español](docs/es/GUIDE.md) · [Français](docs/fr/GUIDE.md) · [简体中文](docs/zh-CN/GUIDE.md)

**[Start here →](START_HERE.md)** · **[English campaign](marketing/campaign/README.md)** · **[Українська реклама](marketing/campaign/README.uk.md)** · [Changes](CHANGELOG.md) · [Current release](releases/current.json) · [Requirements](governance/requirements.csv)

The active branch is **`main`**. The published repository candidate is **1.4.0-rc.5** with **core 6.1.0**, **Atelier Orchestrator 1.2.0**, **maintenance skill 1.1.0** and **Agent Atelier 0.5.0**. The release record gives the exact source and verification links. [Current release](releases/current.json) · [Requirements](governance/requirements.csv) · [Release evidence](releases/repository-1.4.0-rc.5.md)

The owner approved the passport 0.2 implementation and the shown visual foundation. The case ledger records the observed results and outstanding work for full adoption. [Implementation and evidence](docs/evolution/2026-11-10/README.md) · [Український довідник і паспорт](docs/evolution/2026-11-10/README.uk.md) · [29-case ledger](docs/evolution/2026-11-10/FULL-CASE-RESULTS.en.md)

![Agent System: English campaign cover](assets/marketing/campaign/en/01-original.png)

The campaign contains **ten matching materials in English and Ukrainian**: applications, game/studio creation, conversational products, platforms, automation, both constructors, product lifecycle, project continuity and a useful next task. The English artwork localizes the corresponding Ukrainian composition. The exact Ukrainian source cover remains preserved. These are conceptual examples of capabilities, not evidence of real customers, orders or released products.

Open the campaign README in your language for its PDF, lightweight download and offline-gallery links. GitHub displays HTML source; download the repository or source package before opening `marketing/campaign/index.html` locally. The current campaign pointer is [CURRENT_CAMPAIGN.json](marketing/CURRENT_CAMPAIGN.json). Superseded concept galleries, draft artwork and the rejected vector replacement have been removed from the current tree.

## Choose the work you need

| Your goal | Start with | Useful outcome |
| --- | --- | --- |
| Describe any task, continue a project or improve the agent system | Atelier Orchestrator | An appropriate route through direct work, existing skills/project agents or justified agent construction |
| Review retries, consistency or performance in a backend | Orchestrator or an appropriate existing specialist | A scoped investigation, evidence and a reviewable change |
| Reconcile spreadsheets and prepare shipping documents | Orchestrator or an appropriate existing specialist | A tailored workflow with clear data, actions and exception handling |
| Create or improve an Android, iOS or web application | App director | Product decisions, specification, UX, implementation, QA and release preparation |
| Improve a support bot or conversational product | ChatBot director | Preserved personality and memory rules, knowledge, actions, media and verification |
| Develop a mobile game | Game director | Studio identity, concepts, game systems, assets, native implementation, QA and live operations |
| Fix a known issue in an existing product | The relevant existing agent | A targeted change with accepted product requirements preserved |

Outputs depend on the actual scope, connected tools, data access and execution environment. The toolkit provides instructions and working methods; it does not grant service access or replace native-device testing.

## One project across Work and Codex

Work is useful for clarifying a goal, comparing choices, reviewing designs and inspecting connected evidence. Codex is useful for editing a real repository, running scripts, testing and preparing implementation. Their capabilities overlap when the relevant tools exist.

Continuity comes from the same source revision, requirements, decisions, selected language and checkpoint. A handoff carries those records and actual results. It does not silently open another chat or start a desktop session.

| Family | Skills | Scope |
| --- | ---: | --- |
| Constructors | 2 | Tailored agents and reusable specialist skills |
| App | 11 | Research through application operations |
| ChatBot | 11 | Conversation, knowledge, integration and continued service |
| Game | 9 | Studio creation through native games and live operations |

The optional [repository maintenance skill](maintenance-skill/SKILL.md) and [Atelier orchestrator](optional-skills/atelier-orchestrator/SKILL.md) are separate from the 33 baseline skills. The [Agent Atelier local Mac workbench](apps/agent-atelier/README.md) shows a source-backed portfolio of available native Codex work, grouped project/task records, goal provenance, next actions and bounded work preparation. Coverage and actual operation receipts remain visible; discovery does not take over another writer.

## Installation and existing projects

1. Open [START_HERE.md](START_HERE.md) and choose your language.
2. Connect GitHub in the host you use and grant this private repository access.
3. Follow the complete Work or Codex installation section. Reading a repository or extracting an archive is not installation.
4. Verify source integrity, actual discovery and a small real task separately.
5. For an existing product, keep its requirements, design identity, native state, decisions and checkpoint, then follow its applicable adoption instructions.

Use the core 6.1.0 migration to install or update the 33 baseline skills. Atelier Orchestrator 1.2.0 provides the optional universal entry for new work, project continuation and reviewed maintenance. Existing projects keep their own adoption and compatibility records. WORK live adoption remains deferred. [Core migration](releases/migrations/6.1.0.md) · [Component handbook](docs/evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md)

Agent Atelier 0.5.0 provides local Codex project and history discovery, source-backed task preparation, direct OpenAI Docs MCP search and native Codex image generation on a supported host. The versioned service migration covers installation, verification and rollback. [Workbench guide](apps/agent-atelier/README.md) · [Service migration](releases/migrations/repository-1.4.0-rc.5.md)

## Verify and package

From the repository root:

```sh
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -B marketing/campaign/check_campaign.py
python3 -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

The source bundles identify their core suite and repository edition. They include the service source and its pinned lockfile. Obtain the bundles for the exact source revision and verify their hashes before use. [Package instructions](governance/PACKAGES.md) · [Current build evidence](releases/current.json)

[Update contract](governance/UPDATE_CONTRACT.md) · [Requirements](governance/requirements.csv) · [Validation](governance/VALIDATION.md) · [Quality model](governance/QUALITY_MODEL.md) · [Source provenance](kit/PROVENANCE.md) · [Rights](RIGHTS.md)

This independent project is not an official OpenAI product. Host capabilities vary. No measured speed, revenue or superiority claim is made.
