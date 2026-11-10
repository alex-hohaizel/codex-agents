# Current helper, skill and role reference

Snapshot: 2026-11-10, repository 1.3.0 / core 6.0.0 / Orchestrator 1.1.0 / Agent Atelier 0.2.0. Commit `8951398b38a9610854823302ea612cb3844d52e6`.

This reference documents the existing source surface. The systemic AI/data expansion is a proposal, not an installed AI runner or a claim that future products have passed validation.

## How to read this reference

A skill gives the model a task-specific operating method. A role profile gives a real delegated actor a bounded responsibility when the host supports it. A controller records and admits transitions. A validator checks declared structure, bytes or references. An executor actually invokes a command, model or provider. These are different objects; a successful validator cannot stand in for product behavior.

Nothing in the index grants access, spending, production deployment, publication or background work. Use the actual installed host capability and current authorization. Preserve identity, accepted references, settings, native state and unfinished work. WORK remains a separate deferred live-host task.

## Inventory and reproducibility

There are **429 tracked non-test helper/module paths**, grouped into **70 exact-content SHA256 groups**: **48 Python**, **21 JavaScript/MJS**, **1 shell launcher**. The Python groups contain 45 guarded CLI entry points, 2 imported helper libraries and 1 top-level CLI driver. Entry-point detection is static, not a safety certification.

| Scope | Paths |
|---|---:|
| `local_service_module_or_launcher` | 23 |
| `portable_helper` | 3 |
| `kit_root_helper` | 2 |
| `core_skill_helper` | 385 |
| `marketing_helper` | 2 |
| `orchestrator_helper` | 7 |
| `repository_helper` | 6 |
| `shared_standard_source` | 1 |

The denominator includes the 33 core skills, the optional Orchestrator, portable/kit-root/repository/shared-standard/campaign helpers and local-service Python/MJS/shell modules plus Vite configuration. Maintenance has no executable helper files. Test files, caches, binaries, archives, TS/TSX UI components and dependencies are outside this helper denominator. All35 current skill source cards and 12 role profiles are indexed separately.

The [machine index](helper-catalog.json) retains every path, full SHA256, byte size, exact duplicate group, static Python docstrings/functions/imports/argparse declarations,35 source-card hashes and 12 role hashes/instructions. Repeated files in different skills remain independently deliverable; deduplication here does not remove them. Argparse loops may create commands dynamically: static literal declarations are not an exhaustive CLI help transcript.

The inventory parsed source without importing or executing helpers. Test-name candidates in JSON are pointers to inspect, not proof that tests ran. The table names one representative source per exact-content group; JSON maps all aliases. The group ID is a SHA prefix; use the full hash in JSON for exact comparison.

## Shared task/context/source/identity helpers

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `04117249d73a45d5` [kit/skills/agent-foundry/scripts/adaptive_work.py](<../../../kit/skills/agent-foundry/scripts/adaptive_work.py>) | 34 | Portable structural task-artifact checks; no LLM, transport, approval or native gate. | Before handing over or reviewing a declared task artifact. |
| `389eb3db5fff80f4` [kit/skills/agent-foundry/scripts/briefing.py](<../../../kit/skills/agent-foundry/scripts/briefing.py>) | 33 | Bind a briefing/1 execution specification, human script and actual user decision. | When recording a brief, script or actual owner response. |
| `8feeb56681320e1d` [kit/skills/agent-foundry/scripts/check_component_handoff.py](<../../../kit/skills/agent-foundry/scripts/check_component_handoff.py>) | 25 | Check current Atelier component handoff records; not domain or consent certification. | Before a component handoff or acceptance of its return. |
| `a2614457a169599a` [kit/skills/agent-foundry/scripts/context_capsule.py](<../../../kit/skills/agent-foundry/scripts/context_capsule.py>) | 35 | Compile/verify a declared task context; no jobs, permissions or quality certification. | When preparing, delegating, exporting or resuming a task. |
| `faf6576b6b0974ee` [kit/skills/agent-foundry/scripts/discover_specialists.py](<../../../kit/skills/agent-foundry/scripts/discover_specialists.py>) | 2 | Read-only specialist inventory and source-pinned reuse decision checks. | Before choosing an existing specialist or creating a new one. |
| `750ad9e0b5cf9d8d` [kit/skills/agent-foundry/scripts/interaction.py](<../../../kit/skills/agent-foundry/scripts/interaction.py>) | 33 | Read-only Work/Codex status and decision views of existing project records. | When presenting current progress, decisions and next steps. |
| `fe7771d9432bb121` [kit/skills/agent-foundry/scripts/verify_depth.py](<../../../kit/skills/agent-foundry/scripts/verify_depth.py>) | 24 | Validate an additive depth/2 project projection; never certify domain quality. | When checking a depth/2 project projection and linked artifacts. |
| `6883adc2ef7cc06b` [kit/skills/agent-foundry/scripts/visual_identity.py](<../../../kit/skills/agent-foundry/scripts/visual_identity.py>) | 34 | Freeze/check existing icon identity; create a project SVG only when absent. | Before packaging/updating identity or checking its continuity. |

## Agent factory, inheritance, packaging and project installation

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `2b81c42afec24011` [kit/portable/check_generated_inheritance.py](<../../../kit/portable/check_generated_inheritance.py>) | 3 | Verify portable operating resources in newly generated agents, without execution. | Before accepting or distributing a generated agent bundle. |
| `84f18e8ba4fcdcf6` [kit/portable/install_agent.py](<../../../kit/portable/install_agent.py>) | 2 | Install a declared agent skill set into one project; Python standard library only. | After approved source review: preflight/plan/apply/verify/recover or rollback. |
| `b9dacee5a231121a` [kit/portable/update_skill_suite.py](<../../../kit/portable/update_skill_suite.py>) | 2 | Audit, install, verify or roll back the exact personal Atelier skill suite. | For an explicitly authorized core-suite installation/update with its journal. |
| `2b1c9fc919fc8d88` [kit/skills/agent-foundry/scripts/check_foundry_depth.py](<../../../kit/skills/agent-foundry/scripts/check_foundry_depth.py>) | 1 | Validate linked Foundry2 domain/production/inheritance records, never quality. | Before accepting a current Foundry depth package. |
| `2aaa1456bd890077` [kit/skills/agent-foundry/scripts/check_joint_use.py](<../../../kit/skills/agent-foundry/scripts/check_joint_use.py>) | 2 | Check the bundled Work/Codex instructions in newly generated artifacts. | When checking generated Work/Codex interoperability instructions. |
| `e8e2aecf538e59ce` [kit/skills/agent-foundry/scripts/foundry.py](<../../../kit/skills/agent-foundry/scripts/foundry.py>) | 1 | Local approval, coverage and workflow records. No model or external executor. | Explicitly during agent factory state, approvals, tasks or effect records. |
| `169035002ea8aaf1` [kit/skills/agent-foundry/scripts/package_agent.py](<../../../kit/skills/agent-foundry/scripts/package_agent.py>) | 1 | Prepare an already-authored agent delivery kit and optional private plugin export. | When preparing an approved authored agent for delivery. |

## Reusable skill and family constructor

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `88622874d813f517` [kit/skills/design-specialist-skills/scripts/blueprint.py](<../../../kit/skills/design-specialist-skills/scripts/blueprint.py>) | 1 | Versioned skill proposal checks; a recorded approval is not proof of consent. | While drafting/checking a skill or family passport and child inheritance. |
| `d42a61a1d4e18d11` [kit/skills/design-specialist-skills/scripts/check_consistency.py](<../../../kit/skills/design-specialist-skills/scripts/check_consistency.py>) | 1 | Offline consistency checks for a self-contained personal skill package. | After relevant bundle edits, before packaging or acceptance. |

## App records, economics and local prerequisites

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `fabed5d1e9266175` [kit/skills/app-atelier-build/scripts/state.py](<../../../kit/skills/app-atelier-build/scripts/state.py>) | 11 | App Atelier local ledger. Records evidence/authority; never executes a remote action or model. | During App lifecycle records, readiness, effects, pause/resume and handoff. |
| `eb6493c43bfdd7ba` [kit/skills/app-atelier-director/scripts/check_model.py](<../../../kit/skills/app-atelier-director/scripts/check_model.py>) | 1 | Calculate scenario economics from explicit assumptions; calculations never prove demand or profit. | When comparing explicit app economic assumptions and scenarios. |
| `637a022fa6617ca8` [kit/skills/app-atelier-director/scripts/doctor.py](<../../../kit/skills/app-atelier-director/scripts/doctor.py>) | 1 | Read-only local toolchain/skill inventory. Does not install, log in, inspect secrets, or probe remote accounts. | When checking available local App toolchains and duplicate skill sources. |

## ChatBot contracts and adaptive round records

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `5e9eb87b062b5af1` [kit/skills/chatbot-atelier-build/scripts/check_chat_contract.py](<../../../kit/skills/chatbot-atelier-build/scripts/check_chat_contract.py>) | 11 | Validate chatbot.blueprint/3 records. This is structural, not runtime proof. | When checking the current ChatBot subject blueprint. |
| `5f6dfbc795ce2286` [kit/skills/chatbot-atelier-build/scripts/check_consistency.py](<../../../kit/skills/chatbot-atelier-build/scripts/check_consistency.py>) | 11 | Offline checks for current self-contained ChatBot Atelier resources. | After relevant bundle edits, before packaging or acceptance. |
| `6ec3cd36e9c92478` [kit/skills/chatbot-atelier-build/scripts/check_platform_adapter.py](<../../../kit/skills/chatbot-atelier-build/scripts/check_platform_adapter.py>) | 11 | Check current channel adapter declarations; not provider/runtime proof. | Before accepting a declared channel adapter contract. |
| `1daf73dfa258a831` [kit/skills/chatbot-atelier-build/scripts/check_round.py](<../../../kit/skills/chatbot-atelier-build/scripts/check_round.py>) | 11 | Check traceability and independence, never infer product quality from structure. | Before accepting a frozen chatbot round and its evidence references. |
| `db300c7f97b75d74` [kit/skills/chatbot-atelier-build/scripts/team_policy.py](<../../../kit/skills/chatbot-atelier-build/scripts/team_policy.py>) | 11 | Adaptive team record integrity. Never certifies real agents or product quality. | Imported by ChatBot round/team controllers and validators. |
| `d1e40208e7bc3009` [kit/skills/chatbot-atelier-build/scripts/teamctl.py](<../../../kit/skills/chatbot-atelier-build/scripts/teamctl.py>) | 11 | Plan and freeze one current chatbot.round/1 record; never executes a role. | When planning/freezing a current bounded ChatBot round. |

## Game canonical model, production and handoff records

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `692c40a027d784da` [kit/skills/gamedev-assets/scripts/atelier.py](<../../../kit/skills/gamedev-assets/scripts/atelier.py>) | 9 | Game Atelier project state and gates; internal to an agent, never an executor. | During Game lifecycle state, readiness, evidence, approvals and recovery. |
| `0a39ad52a5745baf` [kit/skills/gamedev-assets/scripts/check_build_receipts.py](<../../../kit/skills/gamedev-assets/scripts/check_build_receipts.py>) | 9 | Check local receipt bytes/shape. Does not prove execution, signing or quality. | When matching a delivered package to local build receipt files. |
| `20329291904f4718` [kit/skills/gamedev-assets/scripts/check_suite.py](<../../../kit/skills/gamedev-assets/scripts/check_suite.py>) | 9 | Check installed Game Atelier4 contracts and optional nine-skill shared bytes. | When checking installed Game resources or a nine-skill suite copy. |
| `f7adfe4eb872cc19` [kit/skills/gamedev-assets/scripts/concept_gate.py](<../../../kit/skills/gamedev-assets/scripts/concept_gate.py>) | 9 | Validate systemic concept passports and their pre-illustration receipts. | Before illustration after the required systemic concept declarations. |
| `268eb8c2692a3325` [kit/skills/gamedev-assets/scripts/game_model.py](<../../../kit/skills/gamedev-assets/scripts/game_model.py>) | 9 | Typed, engine-independent design/evidence checks; Python 3.9 standard library. | When validating the canonical Game Model and evidence links. |
| `1ddc81c434213c01` [kit/skills/gamedev-assets/scripts/pipeline.py](<../../../kit/skills/gamedev-assets/scripts/pipeline.py>) | 9 | Portable handoff integrity checks; never grants approval or certifies game quality. | When preparing, importing or checking a Game stage handoff. |
| `18f72e84d51a359d` [kit/skills/gamedev-assets/scripts/production_contract.py](<../../../kit/skills/gamedev-assets/scripts/production_contract.py>) | 9 | Validate declared production contracts, never execute jobs or infer proof. | Before accepting production operations or their declared outputs. |
| `6e4f932a3a9c7511` [kit/skills/gamedev-assets/scripts/reference_math.py](<../../../kit/skills/gamedev-assets/scripts/reference_math.py>) | 9 | Exact D2 arithmetic fixtures, not a universal gameplay resolver or engine test. | For explicit illustrative arithmetic fixtures and matching golden vectors. |
| `1367f2c76c6b097d` [kit/skills/gamedev-assets/scripts/v4_contract.py](<../../../kit/skills/gamedev-assets/scripts/v4_contract.py>) | 9 | Game Model 4 production extension; structural obligations, never quality proof. | Imported by current Game production/model checks. |

## Universal entry and local panel bridge

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `3a901ba2c97f6e65` [optional-skills/atelier-orchestrator/scripts/atelier_client.py](<../../../optional-skills/atelier-orchestrator/scripts/atelier_client.py>) | 1 | Bounded loopback client for Agent Atelier API1. No implicit task/effect authority. | When an installed Orchestrator uses a running, verified local Agent Atelier. |
| `14e686ac6bbea38a` [optional-skills/atelier-orchestrator/scripts/check_routing.py](<../../../optional-skills/atelier-orchestrator/scripts/check_routing.py>) | 1 | Check a declared orchestration task; never classify intent, execute or grant authority. | When checking a proposed universal-entry route and context projection. |

## Repository release, installation and materialization

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `d9dff8a218a4d143` [kit/prepare_existing_project_update.py](<../../../kit/prepare_existing_project_update.py>) | 1 | Prepare a verified existing project agent's maintenance kit; never apply it. | Only for its supported verified legacy project-source and maintenance route. |
| `1775b0aa85ee4a3e` [kit/verify_release.py](<../../../kit/verify_release.py>) | 1 | Read-only file integrity check of this release; no hardware-bound signing. | Explicit CLI integrity verification of the declared kit release. |
| `c60737932615439c` [scripts/build_packages.py](<../../../scripts/build_packages.py>) | 1 | Build deterministic Work and Codex source bundles after repository validation. | When building reviewed source release archives. |
| `58d332758fbc0439` [scripts/check_repository.py](<../../../scripts/check_repository.py>) | 1 | Check distributable skill sources, release completeness and translation freshness. | Before packaging/publication or after relevant source/doc changes. |
| `5cd9e3a4b6f89d86` [scripts/install_host_profile.py](<../../../scripts/install_host_profile.py>) | 1 | Audit/apply/verify/rollback the managed Codex profile with exact plans and journals. | For an approved host-profile/role update, with an exact plan and journal. |
| `b044dc12650bb237` [scripts/materialize_standards.py](<../../../scripts/materialize_standards.py>) | 1 | Materialize reviewed shared resources into independently usable skill bundles. | After a shared-standard edit, or --check for byte consistency. |
| `39ab21e65e3288b5` [scripts/refresh_kit_manifest.py](<../../../scripts/refresh_kit_manifest.py>) | 1 | Rebuild reviewed kit descriptors while retaining an exact Git predecessor. | After source review; compare by default, --write only for intended descriptors. |

## Campaign production and verification

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `e63165b180927401` [marketing/campaign/build_campaign.py](<../../../marketing/campaign/build_campaign.py>) | 1 | Build and verify the canonical English/Ukrainian campaign without changing artwork. | When building the approved campaign from its actual source artwork. |
| `9df586a0a6b4e8a5` [marketing/campaign/check_campaign.py](<../../../marketing/campaign/check_campaign.py>) | 1 | Check all canonical bilingual campaign outputs without changing them. | After generating or receiving the campaign outputs. |
| `7ca2d3591659e20e` [scripts/showcase_pipeline.py](<../../../scripts/showcase_pipeline.py>) | 1 | Run bilingual campaign stages with bounded commands and verified resume receipts. | For explicit bilingual campaign build/check/package stages. |

## Local service modules and launchers

| Group / representative source | Copies | What it does and boundary | When used |
|---|---:|---|---|
| `e1a58d9f6895531b` [apps/agent-atelier/launcher/Agent Atelier.command](../../../apps/agent-atelier/launcher/Agent%20Atelier.command) | 1 | Launches the Mac entry script through an available supported Node/fnm runtime; does not install Node. | When the owner opens the Mac .command launcher. |
| `25b9d3c960500b70` [apps/agent-atelier/launcher/atelier.mjs](<../../../apps/agent-atelier/launcher/atelier.mjs>) | 1 | Local service CLI lifecycle and opening the owner interface; inspect actual command arguments before use. | Explicit local launcher commands. |
| `d2c5d73fbe50840f` [apps/agent-atelier/server/application.mjs](<../../../apps/agent-atelier/server/application.mjs>) | 1 | Coordinates API commands, service state, project jobs, native reads, reviewed maintenance and recovery. | Created by the local HTTP service and used for an admitted command. |
| `be9d058a6fe4e3f9` [apps/agent-atelier/server/codex.mjs](<../../../apps/agent-atelier/server/codex.mjs>) | 1 | Native Codex execution adapter plus separated read-only history facade; actual turn execution has bounded capsule/provider rules. | On explicit connection, bounded job dispatch/resume or history reads. |
| `405f9299a8690361` [apps/agent-atelier/server/context.mjs](<../../../apps/agent-atelier/server/context.mjs>) | 1 | Builds/checks exact task capsules, accepted outcome, source/authority boundaries and job budgets. | During prepare/continue and before execution. |
| `4bf255082f5966a8` [apps/agent-atelier/server/controllers.mjs](<../../../apps/agent-atelier/server/controllers.mjs>) | 1 | Admits source/state-pinned fixed Foundry controller commands and their recovery; not a product/provider runner. | On an explicit reviewed controller preview/apply/reconcile operation. |
| `43608d5c5447f090` [apps/agent-atelier/server/environment.mjs](<../../../apps/agent-atelier/server/environment.mjs>) | 1 | Constructs a worker environment from runtime paths and locale; does not copy caller credentials. | When spawning a service-controlled subprocess. |
| `055bcc00df5e8bc7` [apps/agent-atelier/server/foundry_cas.py](<../../../apps/agent-atelier/server/foundry_cas.py>) | 1 | Source-pinned adapter: compare state inside the native controller's own lock. | Invoked internally for a reviewed native controller operation. |
| `2c7b3fc68c77d23a` [apps/agent-atelier/server/index.mjs](<../../../apps/agent-atelier/server/index.mjs>) | 1 | Runs the loopback HTTP/API/static-file service with owner-session request handling. | When the service launcher starts the HTTP entry point. |
| `d6cfe80570d19181` [apps/agent-atelier/server/instance.mjs](<../../../apps/agent-atelier/server/instance.mjs>) | 1 | Acquires and releases local service instance ownership to prevent competing owners of the same data. | At local service startup/shutdown. |
| `b65b798872934b86` [apps/agent-atelier/server/instructions.mjs](<../../../apps/agent-atelier/server/instructions.mjs>) | 1 | Captures, pins, verifies and aliases reviewed instruction sources, and checks what the execution host loaded. | During source preparation and verification before a job. |
| `7a73fe51392fa072` [apps/agent-atelier/server/optional_updates.mjs](<../../../apps/agent-atelier/server/optional_updates.mjs>) | 1 | Plans/applies/verifies managed optional updates for the two declared sources, preserving unknown local edits and UI identity. | On explicit optional-skill update commands; not automatic vendor-cache editing. |
| `ef657f977713aafd` [apps/agent-atelier/server/permissions.mjs](<../../../apps/agent-atelier/server/permissions.mjs>) | 1 | Builds local permission profiles/overrides and checks external-tool denials; a role label is not a sandbox. | Before starting a bounded local execution route. |
| `4c63aa95655fec32` [apps/agent-atelier/server/portfolio.mjs](<../../../apps/agent-atelier/server/portfolio.mjs>) | 1 | Reads bounded native metadata/history and projects work groups into the portfolio, preserving partial-result status. | On explicit portfolio refresh or project-history reads. |
| `2699db7af5e80ac2` [apps/agent-atelier/server/projects.mjs](<../../../apps/agent-atelier/server/projects.mjs>) | 1 | Inspects allowed project sources, binds explicit projects, and provides refreshed/diffed content and artifact views. | On explicit project preview/bind/workspace/refresh/read operations. |
| `fcf71e784a999457` [apps/agent-atelier/server/retention.mjs](<../../../apps/agent-atelier/server/retention.mjs>) | 1 | Previews/applies bounded service-data retention, sanitizes restored records and exports reviewed diagnostics. | On explicit settings/cleanup/restore/diagnostic operations; not product-data erasure. |
| `607c99a20b126f1a` [apps/agent-atelier/server/routing.mjs](<../../../apps/agent-atelier/server/routing.mjs>) | 1 | Validates route proposals and source-backed specialist selection; a proposal does not launch a job. | When preparing a direct/specialist/constructor/project-agent route. |
| `d1d6dc3f8d7ae8c9` [apps/agent-atelier/server/session.mjs](<../../../apps/agent-atelier/server/session.mjs>) | 1 | Manages local owner proof/session, launch token and CSRF/control authorization. | On owner claim and authenticated API requests. |
| `a678a0a2fb8e81b1` [apps/agent-atelier/server/skills.mjs](<../../../apps/agent-atelier/server/skills.mjs>) | 1 | Inventories core/optional/host competencies, pins selected sources and wraps the exact core updater. | On catalog/source selection or an explicit reviewed core update. |
| `7ecb1d005ed8027b` [apps/agent-atelier/server/store.mjs](<../../../apps/agent-atelier/server/store.mjs>) | 1 | SQLite service records, revisions, transactions, job reservation, command receipts, events and service-state export/restore. | Internal persistence for admitted service operations. |
| `34476a49aa67b469` [apps/agent-atelier/server/utils.mjs](<../../../apps/agent-atelier/server/utils.mjs>) | 1 | Shared strict JSON, hashing, bounded source/path checks, atomic writes, IDs and error utilities. | Imported by local service modules. |
| `1d66a822677df120` [apps/agent-atelier/shared/contracts.mjs](<../../../apps/agent-atelier/shared/contracts.mjs>) | 1 | Shared API/service version, locale/state/error constants for client/server agreement. | Imported by client/server modules. |
| `b99af6b9aec1ab9a` [apps/agent-atelier/vite.config.mjs](<../../../apps/agent-atelier/vite.config.mjs>) | 1 | Configures React client build root, plugin and output; not a running product or deployment. | Loaded by explicit Vite dev/build commands. |

## What actually executes or changes data

The catalog is not a claim that every helper is read-only. Installers/update tools/materializers/builders write their declared local outputs when explicitly applied. `doctor.py` probes supported tool versions. `showcase_pipeline.py` executes bounded local campaign commands. The Mac/Node launcher starts a local process. The service Codex adapter can start a real bounded native model turn. `foundry_cas.py` invokes a reviewed native controller under its lock. In contrast, Foundry `dispatch` records pending admission and returns `executed:false`; an actual permitted host tool and receipt remain separate.

Two Python groups are imported libraries (`team_policy.py`, `v4_contract.py`). `kit/verify_release.py` parses CLI arguments at module top level: do not import it for introspection. A main guard also does not guarantee side-effect-free imports. Read the actual source/arguments and applicable task authority before using a helper.

## All current skill entry points

There are33 stable core skills plus 2 optional instructions. The optional maintenance skill has no executable helpers. The same operational responsibility can be activated directly by a named skill or selected by a source-verified orchestrator route. A direct skill invocation remains supported; using the universal entry does not require rebuilding an agent.

| Skill / source | Class | Responsibility / activation condition |
|---|---|---|
| [agent-foundry](../../../kit/skills/agent-foundry/SKILL.md) | core | Create or compatibly evolve a complete project agent, its scope, skills, team, tools and delivery. |
| [app-atelier-build](../../../kit/skills/app-atelier-build/SKILL.md) | core | Implement or continue approved Android, iOS and web clients of one product. |
| [app-atelier-concepts](../../../kit/skills/app-atelier-concepts/SKILL.md) | core | Turn research into coherent concepts, UX, monetization, economics and operations. |
| [app-atelier-director](../../../kit/skills/app-atelier-director/SKILL.md) | core | Integrate the useful-app lifecycle from idea through product development and operation. |
| [app-atelier-experience](../../../kit/skills/app-atelier-experience/SKILL.md) | core | Design brand, UX/UI, interactive prototypes and usable production materials. |
| [app-atelier-growth](../../../kit/skills/app-atelier-growth/SKILL.md) | core | Design and verify acquisition, ASO/SEO/content/partnership and product growth routes. |
| [app-atelier-operations](../../../kit/skills/app-atelier-operations/SKILL.md) | core | Operate an existing app: incidents, health, cost/revenue, support, metrics and development. |
| [app-atelier-qa](../../../kit/skills/app-atelier-qa/SKILL.md) | core | Independently verify app requirements, design, implementation, payments, support and release readiness. |
| [app-atelier-release](../../../kit/skills/app-atelier-release/SKILL.md) | core | Prepare and perform only authorized Android/iOS/web release with signing, listings and actual checks. |
| [app-atelier-research](../../../kit/skills/app-atelier-research/SKILL.md) | core | Research needs, alternatives, competitors and promising application directions. |
| [app-atelier-specification](../../../kit/skills/app-atelier-specification/SKILL.md) | core | Define PRD/TDD, domain/data/API/auth/payment contracts and complete Android/iOS/web scope. |
| [app-atelier-support](../../../kit/skills/app-atelier-support/SKILL.md) | core | Build and operate product support bot and channel/client integration. |
| [chatbot-atelier-build](../../../kit/skills/chatbot-atelier-build/SKILL.md) | core | Implement the complete approved chatbot using domain contracts and actual integrations. |
| [chatbot-atelier-conversation](../../../kit/skills/chatbot-atelier-conversation/SKILL.md) | core | Design natural context-aware language, character, listening, initiatives and shared experience. |
| [chatbot-atelier-director](../../../kit/skills/chatbot-atelier-director/SKILL.md) | core | Integrate the complete chatbot lifecycle, domain model, team, conversation, code, QA and operation. |
| [chatbot-atelier-integrations](../../../kit/skills/chatbot-atelier-integrations/SKILL.md) | core | Implement platform adapters, callbacks, actions, jobs, schedulers and real integrations. |
| [chatbot-atelier-knowledge](../../../kit/skills/chatbot-atelier-knowledge/SKILL.md) | core | Design scoped memory, sources, retrieval/RAG when needed, corrections, TTL and privacy. |
| [chatbot-atelier-media](../../../kit/skills/chatbot-atelier-media/SKILL.md) | core | Produce and integrate chatbot image, animation, audio/video and delivery identity. |
| [chatbot-atelier-operations](../../../kit/skills/chatbot-atelier-operations/SKILL.md) | core | Operate and evolve existing chatbots: incidents, repairs, conversation, support and measures. |
| [chatbot-atelier-qa](../../../kit/skills/chatbot-atelier-qa/SKILL.md) | core | Independently verify chatbot model, conversation, memory, actions, media and runtime. |
| [chatbot-atelier-release](../../../kit/skills/chatbot-atelier-release/SKILL.md) | core | Prepare and perform authorized release, migration and rollback from exact source/build/assets. |
| [chatbot-atelier-research](../../../kit/skills/chatbot-atelier-research/SKILL.md) | core | Research chatbot needs, domain, platforms, integrations and production feasibility. |
| [chatbot-atelier-specification](../../../kit/skills/chatbot-atelier-specification/SKILL.md) | core | Define causal domain/state/rule/API contracts for the approved chatbot. |
| [design-specialist-skills](../../../kit/skills/design-specialist-skills/SKILL.md) | core | Create or update a reusable specialist skill or family from a domain task. |
| [gamedev-assets](../../../kit/skills/gamedev-assets/SKILL.md) | core | Create, repair and integrate game art, animation, UI, audio and haptics. |
| [gamedev-build](../../../kit/skills/gamedev-build/SKILL.md) | core | Implement or continue the native mobile game from approved model, contracts and production assets. |
| [gamedev-concepts](../../../kit/skills/gamedev-concepts/SKILL.md) | core | Research and compare coherent dynamic mobile game concepts before selection. |
| [gamedev-director](../../../kit/skills/gamedev-director/SKILL.md) | core | Integrate game idea/studio/concepts/model/assets/native build/QA/release/live operation. |
| [gamedev-liveops](../../../kit/skills/gamedev-liveops/SKILL.md) | core | Operate beta/released games: cohorts, incidents, progression, retention and measured evolution. |
| [gamedev-preproduction](../../../kit/skills/gamedev-preproduction/SKILL.md) | core | Develop the accepted concept into GDD/TDD and a complete shared game model. |
| [gamedev-qa](../../../kit/skills/gamedev-qa/SKILL.md) | core | Independently verify game rules and native Android/iOS behavior, controls, systems and experience. |
| [gamedev-release](../../../kit/skills/gamedev-release/SKILL.md) | core | Prepare and perform authorized native Android/iOS release from exact binaries and evidence. |
| [gamedev-studio](../../../kit/skills/gamedev-studio/SKILL.md) | core | Create or restore game studio brand, identity, logo and developer readiness. |
| [codex-agents-maintenance](../../../maintenance-skill/SKILL.md) | optional | Maintain canonical sources, docs, translations, compatibility, packages and publication evidence. |
| [atelier-orchestrator](../../../optional-skills/atelier-orchestrator/SKILL.md) | optional | Universal conversational entry: restore context and choose execution, existing specialist, project agent, constructor or bridge. |

## All current role profiles

The12 profiles are bounded delegated actors, not an always-running staff. The parent selects an actor for a concrete artifact, allowed paths/resources/effects, budget, source inputs and acceptance. Independence requires a real separate actor and inspected evidence. A profile is not a separate sandbox and does not create provider access.

| Role / source | Responsibility |
|---|---|
| [foundry-architecture](../../../agent-profiles/foundry-architecture.toml) | Compare 2–3 feasible designs; own module boundaries, ERD, API/events, concurrency, idempotency, recovery, resource and rollout. Prefer simplest coherent vertical slice. |
| [foundry-backend](../../../agent-profiles/foundry-backend.toml) | Implement only assigned files and tests. Keep state ownership, schema, migrations, idempotency, privacy lineage and error handling coherent. |
| [foundry-conversation](../../../agent-profiles/foundry-conversation.toml) | Design natural, context-aware conversation, listening, clarification, initiative, humor, consent, tone, temporary preferences and human evaluation. |
| [foundry-cost](../../../agent-profiles/foundry-cost.toml) | Reduce context, agents, retries, unnecessary media processing and test duplication; measure real costs, never sacrifice hard gates. |
| [foundry-integrations](../../../agent-profiles/foundry-integrations.toml) | Verify provider APIs, auth scopes, failure modes, actual receipts, retries, quotas and cost. Never treat an API stub as a working integration. |
| [foundry-judge](../../../agent-profiles/foundry-judge.toml) | Separate hypothesis, code inspection, isolated test, integration, provider observation and human feedback. Reject unknown hard gates and fabricated completion. |
| [foundry-platform](../../../agent-profiles/foundry-platform.toml) | Check platform-specific callback/interaction semantics, permissions, message formatting, rate limits, transport receipts, group roles and device behavior. |
| [foundry-privacy](../../../agent-profiles/foundry-privacy.toml) | Threat-model data scopes, consent, secrets, prompt injection, forget, revoke, restore, logging and cross-user leakage. Return exploit scenarios or honest unknowns. |
| [foundry-product](../../../agent-profiles/foundry-product.toml) | Define audience, concrete value, JTBD, user journeys, non-goals, success metrics, ethical boundaries and acceptance; challenge decorative features. |
| [foundry-qa](../../../agent-profiles/foundry-qa.toml) | Independently review frozen contract and diff. Produce positive, negative, race, stale, wrong-actor, duplicate, cancel, restart, privacy tests with actual evidence. |
| [foundry-reliability](../../../agent-profiles/foundry-reliability.toml) | Design bounded queues, retries, recovery, cancellation, timeouts, health, metrics, backup/restore and deploy safety. |
| [foundry-skeptic](../../../agent-profiles/foundry-skeptic.toml) | Find the strongest concrete counterexamples and alternative explanations; focus on correctness, user burden, hidden cost and regression. |

`foundry-cost` explicitly uses `gpt-6-luna` with `medium` reasoning; the other current profiles inherit the host/default model. Preserve these settings unless a reviewed change explicitly updates them. Shared role restrictions preserve parent authority, forbid secrets/real private chats and prohibit unapproved production/publication/deploy/new-paid/irreversible effects.

## Current runtime limits and evidence

The local service is a real bounded execution/control route, not a universal provider runtime. Its capsule admits only `public_web_read` as an external capability, read-only/workspace-write local scopes, 30–3600-second jobs, one attempt and at most four explicitly selected competencies per job. These are job-input bounds, not a claim that a whole product can use only four skills. Unsupported API/network scope must bridge to an actually capable approved host. ChatGPT/OpenAI billing/provider checks remain in force. See [API boundary](../../../apps/agent-atelier/shared/API.md), `server/context.mjs:85–113`, `server/skills.mjs:353–359` and `server/codex.mjs:538–619`.

The [1.3 verification record](../../../governance/UNIVERSAL_ENTRY_1_3_VERIFICATION.json) contains historical tests and bounded runtime observations with their own pins. It does not prove every model route, future creative quality, WORK, device/production acceptance or the complete created-agent→installed/discovered→original-product execution loop. This catalog reruns none of those proofs. Source presence, installation, discovery, actual execution, independent review and owner acceptance must remain distinct.

## Conditional profile and admission consequences in passport0.2

The current35source/12role composition remains. Seven AI competence areas are conditional internal profiles with current owners, not an additional installed pack or new roles. Keep the two-entry optional allowlist, exact12role admission and exact33core guard with their preservation/journaling. Do not widen those controls for a hypothetical pack.

Conditional profile resources still need an explicit dependency/materialization/inheritance manifest and actual self-contained delivery. Existing four shared resources and12 inherited resources stay traceable; a new standards file alone is not distribution. Reuse current helpers and prove actual-task benefit plus preservation before production adoption. A later independently justified extraction needs a revised exact composition decision before creating/installing that new target.

The existing prepared-project updater contains specific historical WORK5.0.0 authority at prepare_existing_project_update.py:107–113. Preserve it as historical provenance; it grants no new adoption, WORK or unrelated project permission. [Current passport](PASSPORT.en.md) governs the revised proposal; [history](REVISIONS.en.md) preserves0.1.
