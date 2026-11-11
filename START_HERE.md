# Start here

Choose the language you want to read **and use with your agent**. Each guide contains the complete installation, daily-work, handoff and existing-project adoption instructions.

| Language | Full guide | Interaction preference | Campaign |
| --- | --- | --- | --- |
| English (default) | [Open](docs/en/GUIDE.md) | `preferred_language=en` | [English](marketing/campaign/README.md) |
| Українська | [Відкрити](docs/uk/GUIDE.md) | `preferred_language=uk` | [Українська](marketing/campaign/README.uk.md) |
| Deutsch | [Öffnen](docs/de/GUIDE.md) | `preferred_language=de` | [English](marketing/campaign/README.md) · [Українська](marketing/campaign/README.uk.md) |
| Italiano | [Apri](docs/it/GUIDE.md) | `preferred_language=it` | [English](marketing/campaign/README.md) · [Українська](marketing/campaign/README.uk.md) |
| Español | [Abrir](docs/es/GUIDE.md) | `preferred_language=es` | [English](marketing/campaign/README.md) · [Українська](marketing/campaign/README.uk.md) |
| Français | [Ouvrir](docs/fr/GUIDE.md) | `preferred_language=fr` | [English](marketing/campaign/README.md) · [Українська](marketing/campaign/README.uk.md) |
| 简体中文 | [打开](docs/zh-CN/GUIDE.md) | `preferred_language=zh-CN` | [English](marketing/campaign/README.md) · [Українська](marketing/campaign/README.uk.md) |

The guides are complete in all seven languages. Advertising artwork is available in English and Ukrainian only; the other guide languages do not imply additional artwork translations.

## Before installation

Use the current version record on `main`. The published repository candidate **1.4.0-rc.5** includes **core 6.1.0**, optional **Atelier Orchestrator 1.2.0**, optional **maintenance 1.1.0** and **Agent Atelier 0.5.0**. The active requirements register records each scope and its evidence. Full 1.4.0 acceptance remains open. [Current release and verification](releases/current.json) · [Requirements](governance/requirements.csv)

Follow the versioned migration for the component you are updating. The workbench can discover local projects, prepare the displayed next action, search OpenAI Docs MCP and generate a PNG through Codex Image when the host supports it. Use the current release record for its exact GitHub Actions run and downloadable source bundles. [Core migration](releases/migrations/6.1.0.md) · [Workbench guide](apps/agent-atelier/README.md) · [Service update and rollback](releases/migrations/repository-1.4.0-rc.5.md)

1. Sign in to the Work or Codex surface available to your account.
2. Enable the GitHub connection and grant `alex-hohaizel/codex-agents` access. Repository visibility remains private.
3. Read the guide in your language and copy its bootstrap request into the skills-management conversation. It includes the language preference and asks the agent to verify actual source and tools.
4. If repository access is unavailable, download it while signed in to GitHub using **Code → Download ZIP**, extract it and provide the folder through the host's supported file-access mechanism.
5. Follow Work or Codex installation, then verify source integrity, saved installation, discovery and a bounded real task separately.

For a product you already work on, open that existing project and continue from its accepted requirements, decisions, identity and checkpoint. A new conversation is not a new product.

The accepted visual foundation shows the work, its evidence and the next scoped action. Project records and runtime results keep their original sources. The 29-case ledger records the cases and gates that still need work. [Case ledger](docs/evolution/2026-11-10/FULL-CASE-RESULTS.en.md)

## Historical baseline: suite6.0.0 and edition1.3.0

The 33 stable core skills now carry production-quality and context-continuity contracts, stronger evidence/source admission and explicit compatible adoption. Existing names, icons, accepted product requirements and native state remain preserved. Read the [6.0.0 migration](releases/migrations/6.0.0.md), audit the exact installed sources, then use the reviewed updater plan. Existing generated agents need their own source-to-target adoption; no product is reset.

The [local Mac workbench](apps/agent-atelier/README.md) and optional `atelier-orchestrator` are separate components. Follow the ten-step section0 in your full guide. WORK live audit/update/installation remains a separate host task; reusable source bundles do not certify a live Work installation.

The [1.2.1 service patch](releases/repository-1.2.1.md) preserves the6.0.0 core and existing products; old unpinned tasks need fresh preparation.

The [1.2.2 presentation patch](releases/repository-1.2.2.md) updates optional Orchestrator to1.0.1 with Ukrainian entry/UI text and PNG renderings of its unchanged SVG icon. Agent Atelier0.1.1 remains the separate local application; no core reinstall, service restart or product migration is needed. Follow the [targeted update and rollback](releases/migrations/repository-1.2.2.md).

The historical [1.3.0 feature release](releases/repository-1.3.0.md) introduced optional Orchestrator1.1.0 as a universal entry and Agent Atelier0.2.0 as the separate portfolio workbench. Its [exact update/rollback](releases/migrations/repository-1.3.0.md) applies to that historical target. The universal-entry behavior remains in the candidate: describe an outcome, continue an existing project agent, construct one when justified or request compatible system maintenance. Native work discovery, goal/work/source provenance and bounded route preparation remain distinct from executing or adopting a change.

## Change the interaction language

Tell the agent: “Change preferred_language to [language code] in the current project context and use it for future explanations, clarification, progress, handoffs and installation advice. Keep API keys, code and stable identifiers unchanged.”

Persist the setting in [project context](templates/project-context.json) and carry it through handoffs. Opening a translated page does not by itself change a chat's saved preference.

[What the system does](README.md) · [English campaign](marketing/campaign/README.md) · [Українська реклама](marketing/campaign/README.uk.md) · [Current release](releases/current.json)

## Approved AI/data/production implementation candidate

The owner approved [passport0.2 implementation](docs/evolution/2026-11-10/README.md), also documented [in Ukrainian](docs/evolution/2026-11-10/README.uk.md). Candidate sources add source-bound context, readable requirements/decisions/deferred work, bounded history paging and seven conditional profiles without adding a mandatory framework or new skill/role. All17 capabilities remain in scope within33 core skills, two optional skills and12 roles. New generated children carry15 common resources; older children need exact compatible adoption rather than silent relabelling.

Read [what each component does, when it runs and its limits](docs/evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md). The [actual public-review study](docs/evolution/2026-11-10/REVIEW-STUDY.en.md) provides100 source-linked issues and useful product needs; agreement with one AI reviewer is not validated accuracy or proof that the new rules caused better results. The implementation record preserves historical model and service observations at their exact revisions. The current release record carries the verified publication. Confirmed regressions reject adoption; an unresolved affected gate keeps the verified baseline active. This candidate does not authorize product resets, unrelated migrations or live WORK work.
