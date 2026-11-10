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

The repository currently describes **source candidate1.4.0-rc.3 / core6.1.0 / Orchestrator1.2.0 / maintenance1.1.0 / service0.3.1**, not an automatically adopted stable update. Read the [6.1 migration and current gates](releases/migrations/6.1.0.md) first. Full29-case acceptance remains in progress; actual evidence, independent case closure and owner acceptance are separate. CPA accuracy remains unverified without representative data; current A10 uses owner-approved guards/abstention. The bounded source-only continuation case A25 passed all three R4 trials. LIGHT BOT runtime and owner acceptance remain open. Read the [real-task handbook](docs/evolution/2026-11-10/REAL-WORLD.en.md) and [rc.3 migration](releases/migrations/repository-1.4.0-rc.3.md). The compatible service patch covers focus, stable artifact selection, unavailable-source recovery and readable source-checked Markdown reports; these source changes require their own runtime proof. The reproduced P1 nested native-state write issue was repaired and retested with93 filesystem readbacks for the named macOS/Codex route; that narrow result does not adopt the candidate. Keep the verified stable installation active where a gate is unknown or failed. The advanced task API optionally accepts `memory_mode`; ordinary tasks/legacy capsules keep `inherit`, while explicit disabled requires a fresh service-owned chat and its native/file guards. It preserves global preferences and rejects changing an adopted user chat. The initial, R2 and R3 trials retain their NOT_ADMITTED verdicts. All three R4 continuations passed G01–G10. Use the handbook for the limits of this result. New selected skills have a separate immutable execution copy and retained private archive, without wider access. STORE JSON is not an archive-file backup; read the detailed handbook before use. WORK live work remains deferred.

GitHub Actions passed on implementation commit `b49dfcb7cb7eecaedf6aac541f9dea8fc2df3e19` in PR #2 and published both build artifacts. Check the installation record for the local running copy. [GitHub Actions run 42905363916](https://github.com/alex-hohaizel/codex-agents/actions/runs/42905363916).

1. Sign in to the Work or Codex surface available to your account.
2. Enable the GitHub connection and grant `alex-hohaizel/codex-agents` access. Repository visibility remains private.
3. Read the guide in your language and copy its bootstrap request into the skills-management conversation. It includes the language preference and asks the agent to verify actual source and tools.
4. If repository access is unavailable, download it while signed in to GitHub using **Code → Download ZIP**, extract it and provide the folder through the host's supported file-access mechanism.
5. Follow Work or Codex installation, then verify source integrity, saved installation, discovery and a bounded real task separately.

For a product you already work on, open that existing project and continue from its accepted requirements, decisions, identity and checkpoint. A new conversation is not a new product.

The owner accepted the shown revision6 visual foundation, not every function or an installation. Start with its documented work map: select real work/result, read evidence, then choose an admitted next action. Source documents / Compare changes retains the full technical view. Source-declared checkpoint progress is distinct from runtime or accepted deliverables. The completed fresh task passed9/9 independent bound-source checks. Compatible-update admission still needs its affected-invariant ledger and exact-source CI; all29 full cases remain open.

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

Read [what each component does, when it runs and its limits](docs/evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md). The [actual public-review study](docs/evolution/2026-11-10/REVIEW-STUDY.en.md) provides100 source-linked issues and useful product needs; agreement with one AI reviewer is not validated accuracy or proof that the new rules caused better results. A candidate0.3 restart, earlier model jobs, source integrity, installation/discovery, operational adoption, publication and CI are separate evidence. Confirmed regressions reject adoption; an unresolved affected gate keeps the verified baseline active. This candidate does not authorize product resets, unrelated migrations or live WORK work.
