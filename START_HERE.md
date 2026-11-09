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

1. Sign in to the Work or Codex surface available to your account.
2. Enable the GitHub connection and grant `alex-hohaizel/codex-agents` access. Repository visibility remains private.
3. Read the guide in your language and copy its bootstrap request into the skills-management conversation. It includes the language preference and asks the agent to verify actual source and tools.
4. If repository access is unavailable, download it while signed in to GitHub using **Code → Download ZIP**, extract it and provide the folder through the host's supported file-access mechanism.
5. Follow Work or Codex installation, then verify source integrity, saved installation, discovery and a bounded real task separately.

For a product you already work on, open that existing project and continue from its accepted requirements, decisions, identity and checkpoint. A new conversation is not a new product.

## What suite 6.0.0 and edition 1.2.0 change

The 33 stable core skills now carry production-quality and context-continuity contracts, stronger evidence/source admission and explicit compatible adoption. Existing names, icons, accepted product requirements and native state remain preserved. Read the [6.0.0 migration](releases/migrations/6.0.0.md), audit the exact installed sources, then use the reviewed updater plan. Existing generated agents need their own source-to-target adoption; no product is reset.

The [local Mac workbench](apps/agent-atelier/README.md) and optional `atelier-orchestrator` are separate components. Follow the ten-step section0 in your full guide. WORK live audit/update/installation is deferred to the owner's separate task; reusable source bundles do not certify a live Work installation.

## Change the interaction language

Tell the agent: “Change preferred_language to [language code] in the current project context and use it for future explanations, clarification, progress, handoffs and installation advice. Keep API keys, code and stable identifiers unchanged.”

Persist the setting in [project context](templates/project-context.json) and carry it through handoffs. Opening a translated page does not by itself change a chat's saved preference.

[What the system does](README.md) · [English campaign](marketing/campaign/README.md) · [Українська реклама](marketing/campaign/README.uk.md) · [Current release](releases/current.json)
