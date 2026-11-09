# Agent System · Work + Codex

**A focused task. An existing product. A whole new direction.**

A reusable system of **33 specialized skills** for research, requirements, design, implementation, verification and continued improvement. Review a backend architecture, build an integration, restore an existing service, create an application or develop a game. The specialist team and depth follow the actual task.

[English](docs/en/GUIDE.md) · [Українська](docs/uk/GUIDE.md) · [Deutsch](docs/de/GUIDE.md) · [Italiano](docs/it/GUIDE.md) · [Español](docs/es/GUIDE.md) · [Français](docs/fr/GUIDE.md) · [简体中文](docs/zh-CN/GUIDE.md)

**[Start here →](START_HERE.md)** · **[English campaign](marketing/campaign/README.md)** · **[Українська реклама](marketing/campaign/README.uk.md)** · [Changes](CHANGELOG.md) · [Existing-project adoption](releases/migrations/6.0.0.md)

![Agent System: English campaign cover](assets/marketing/campaign/en/01-original.png)

The campaign contains **ten matching materials in English and Ukrainian**: applications, game/studio creation, conversational products, platforms, automation, both constructors, product lifecycle, project continuity and a useful next task. The English artwork localizes the corresponding Ukrainian composition. The exact Ukrainian source cover remains preserved. These are conceptual examples of capabilities, not evidence of real customers, orders or released products.

Open the campaign README in your language for its PDF, lightweight download and offline-gallery links. GitHub displays HTML source; download the repository or source package before opening `marketing/campaign/index.html` locally. The current campaign pointer is [CURRENT_CAMPAIGN.json](marketing/CURRENT_CAMPAIGN.json). Superseded concept galleries, draft artwork and the rejected vector replacement have been removed from the current tree.

## Choose the work you need

| Your goal | Start with | Useful outcome |
| --- | --- | --- |
| Review retries, consistency or performance in a backend | Agent constructor | A scoped specialist, evidence and a reviewable change |
| Reconcile spreadsheets and prepare shipping documents | Agent constructor | A tailored workflow with clear data, actions and exception handling |
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

The optional [repository maintenance skill](maintenance-skill/SKILL.md) and [Atelier orchestrator](optional-skills/atelier-orchestrator/SKILL.md) are separate from the 33 baseline skills. The [Agent Atelier local Mac workbench](apps/agent-atelier/README.md) shows actual projects, sources, context, tasks, outcomes and reviewed skill updates.

## Installation and existing projects

1. Open [START_HERE.md](START_HERE.md) and choose your language.
2. Connect GitHub in the host you use and grant this private repository access.
3. Follow the complete Work or Codex installation section. Reading a repository or extracting an archive is not installation.
4. Verify source integrity, actual discovery and a small real task separately.
5. For an existing product, keep its requirements, design identity, native state, decisions and checkpoint, then follow its applicable adoption instructions.

**Suite6.0.0 / repository edition 1.2.2** includes production/context contracts, stronger evidence and writer admission, supported Codex host profiles and a real local workbench. Preserve the 33 names/icons and all existing accepted product state. Use the exact [6.0.0 migration](releases/migrations/6.0.0.md); installation is separate from project adoption, discovery and behavior. WORK live audit/update/install/control remains a separate host task.

Optional `atelier-orchestrator`1.0.1 is the coordinating skill with Ukrainian entry/UI text and PNG bindings derived from its original SVG icon. Agent Atelier0.1.1 is the separately launched local application/server. See [the presentation patch](releases/repository-1.2.2.md) and [targeted update/rollback](releases/migrations/repository-1.2.2.md); neither core reinstallation nor product migration is required.

## Verify and package

From the repository root:

```sh
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -B marketing/campaign/check_campaign.py
python3 -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

Source bundles identify suite 6.0.0 and repository edition 1.2.2. They include local-service source and its pinned lockfile; build the client using the service instructions. [Package instructions](governance/PACKAGES.md) explain local builds and exact-commit Actions artifacts. The existence of a workflow is separate from a successful CI run.

[Update contract](governance/UPDATE_CONTRACT.md) · [Requirements](governance/requirements.csv) · [Validation](governance/VALIDATION.md) · [Quality model](governance/QUALITY_MODEL.md) · [Source provenance](kit/PROVENANCE.md) · [Rights](RIGHTS.md)

This independent project is not an official OpenAI product. Host capabilities vary. No measured speed, revenue or superiority claim is made.
