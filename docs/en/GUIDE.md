# Agent System — the complete Work + Codex guide

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [中文](../zh-CN/GUIDE.md)

**Guide baseline:** Agent System6.0.0, 9 November2026. **Reusable suite:** 33 skills. This guide covers a new installation, everyday work, sharing a project between Work and Codex, and updating an existing project. Repository documentation and package revisions can change without changing the underlying skill version; consult the release record before updating.


**Current release:** suite6.0.0, repository1.2.0, optional Atelier Orchestrator1.0.0 and local Agent Atelier0.1.0. Read [the exact6.0 migration](../../releases/migrations/6.0.0.md) before updating. The previous1.1.0 campaign remains unchanged: [English advertising](../../marketing/campaign/README.md) and [Ukrainian advertising](../../marketing/campaign/README.uk.md), ten materials per language. Advertising is EN/UK; guides and the service UI cover all seven advertised locales. Work live audit, update, installation and control are deferred to a separate task; a source archive or repository connection is not an installation receipt.

## 0. Update to6.0 and open the local workbench

1. Select an exact verified release commit. Preserve the current33-skill sources, icon files/bindings/colors/classes, local changes and ownership. Save native project requirements, accepted identity/persona, decisions, permissions, pending tasks and unknown effects. Installation does not migrate a product.
2. From `kit/`, read the portable updater help, then audit the exact candidate. Inspect all33 entries, conflicts and visual preservation before apply. Keep plans/backups outside skill-discovery roots.

```bash
python3 portable/update_skill_suite.py --help
python3 portable/update_skill_suite.py audit --kit . --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py apply --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py verify --kit . --journal /actual/apply/journal.json
```

3. Replace the journal placeholder only with the actual path returned by apply. Unknown drift must be reconciled; do not force an overwrite. Check actual discovery/source loading and one bounded task separately. Existing icons and unrelated skills remain preserved.
4. Audit the Codex host profile separately from the repository root: `python3 scripts/install_host_profile.py audit --plan /absolute/host-plan.json`. Apply with `apply --plan /absolute/host-plan.json --journal /absolute/host-journal.json`, then `verify --journal /absolute/host-journal.json`. The managed block preserves existing global instructions; the twelve bounded roles retain their models and external-effect restrictions. Loading in an actual host is a separate check.
5. Install optional `atelier-orchestrator` through the supported skill manager from `optional-skills/atelier-orchestrator` at the selected commit. It is separate from the33-core updater; source presence does not establish installation or successful execution. The existing maintenance skill remains separately optional.
6. To build the local service from source, use the pinned lockfile with Node.js24.22.2 or a supported later runtime. From `apps/agent-atelier/`, run the following. Network access is needed for first dependency installation, with no new paid service implied.

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

7. On Mac, `apps/agent-atelier/launcher/Agent Atelier.command` provides the double-click launch after building. The launcher opens loopback, reuses its own running instance and does not enable login auto-start. Select and preview an explicit project root, then bind it. A binding is read-only project discovery, not product adoption or permission for every future task. Demo mode contains fictional data and performs no commands.
8. Prepare a task with exact scope, inputs, acceptance and bounds, then dispatch through the supported Codex adapter. Source, craft, integration, device, independent review and owner acceptance are different states. Cancellation is confirmed only after the actual host outcome. Existing chats require exact identity/cwd and an idle handoff; another desktop writer is not fenced by a service lease. Reconcile an unknown effect before retrying.
9. Existing Foundry sessions use `suite-update-plan` and a reviewed `refresh --accept-suite-update` record with exact source-state/target hashes. App state/1 needs no toolkit-format migration. Chat integrated evidence needs current contract subject pins and a real new observation; old proof is not retrofitted. Game uses its supported5-to6 workflow upgrade while retaining runtime2/model4/handoff1. Generated agents require source-to-target comparison and cold continuation; no project is reset.
10. Service backup/restore is service-owned only: preview and validate the exact backup, reconcile jobs and preserve revoked authority; it does not restore product databases or external effects. Skill rollback uses the actual updater journal; host-profile rollback uses its own journal and rejects later drift. Work live installation/control remains deferred. Read [the detailed migration](../../releases/migrations/6.0.0.md) and [service guide](../../apps/agent-atelier/README.md) for recovery and supported limits.

## 1. What this gives you

Describe a result in ordinary language. The system helps turn it into a concrete task, brings in the relevant specialties, keeps the decisions and requirements together, and checks the result against the agreed outcome.

For example, “Help me reduce database load in this backend” can become a focused investigation of queries, transaction boundaries, caching, performance measurements and a tested change. “Create a mobile application for this audience” needs a broader route: research, product choices, design, architecture, implementation, quality checks, release preparation and operation. A small repair should stay a small repair. A whole product should retain its whole set of requirements, including the parts scheduled after the first working version.

A **skill** is a reusable set of working instructions, references and sometimes scripts. An **agent** applies a role and those instructions to a task. A **director** coordinates a product family. A **constructor** designs a specialist agent or a reusable set of skills when the existing families do not cover the job. They operate through ChatGPT or Codex and the tools actually available in that environment. Installing instructions does not create a running server, buy services, grant repository permissions or launch a permanent background worker.

The value is the organized workflow: a shared brief, explicit requirements, relevant specialists, preserved decisions, verifiable handoffs and a way to resume work. The repository does not claim measured superiority, guaranteed income, guaranteed store acceptance or automatic production readiness.

## 2. Choose where to start

| Your situation | Start with | A useful first request |
| --- | --- | --- |
| You want a specialist agent tailored to a recurring job | `agent-foundry` | “Create an agent that investigates performance problems in our Go services. First clarify its responsibilities, evidence and access.” |
| You want one reusable skill or a coordinated skill family | `design-specialist-skills` | “Design a reusable review workflow for our event-driven integrations, including failure recovery.” |
| You want an application or an existing product developed | `app-atelier-director` | “Continue this application from its checkpoint. Preserve its accepted requirements and identify the next useful deliverable.” |
| You want a chatbot, support bot or conversational companion | `chatbot-atelier-director` | “Design a bot for this audience and these channels, including its language, memory, actions and operating costs.” |
| You want a mobile game or to continue an existing game | `gamedev-director` | “Develop game concepts around this experience, with meaningful controls, progression and a feasible production route.” |
| You know the exact stage already | The relevant specialist below | “Review this payment screen against the approved design and acceptance criteria.” |

You do not have to memorize all 33 names. Use a director for a product, or a constructor for a new specialist workflow. You can also request a skill explicitly from the host's skill selector. In Work the customary form is `@skill-name`; in Codex it is `$skill-name`. Available selectors and display names can differ between host versions. Ask the host to show the exact loaded source when you need certainty.

### The complete catalog

#### Two constructors

| Skill | What it helps you produce |
| --- | --- |
| `agent-foundry` | A specialist agent or coordinated agent family, shaped around a real domain, responsibilities, tools, knowledge, checks and a workable operating route. Its first job is to design the agent, rather than silently doing the agent's eventual project. |
| `design-specialist-skills` | Reusable skills and skill families for a defined task: the right specialties, quality criteria, references, tools and sequence of work. |

#### Application team — 11 skills

| Skill | What it does in human terms |
| --- | --- |
| `app-atelier-director` | Keeps the application project coherent from the first idea through development and operation. |
| `app-atelier-research` | Investigates users, needs, alternatives and market evidence before the team invests in a product direction. |
| `app-atelier-concepts` | Compares complete product options: usefulness, experience, business model, costs and realistic scope. |
| `app-atelier-specification` | Turns the chosen product into precise requirements, behavior, data, API, authentication and payment contracts. |
| `app-atelier-experience` | Creates and checks the brand, screens, states, onboarding, accessibility, localization and production design materials. |
| `app-atelier-build` | Implements the agreed Android, iOS and web clients, backend and integrations where required, with reproducible builds. |
| `app-atelier-support` | Designs and implements the product's support bot and knowledge workflow, including escalation and controlled actions. |
| `app-atelier-qa` | Independently checks the requirements, design, implementation, payments, privacy, recovery and release readiness when an independent actor is available. |
| `app-atelier-release` | Checks release feasibility early, then prepares signing, store listings, deployments, receipts and rollback within the granted scope. |
| `app-atelier-growth` | Evaluates and prepares relevant acquisition channels, content and measurement, then activates an authorized route when the product is ready. |
| `app-atelier-operations` | Handles incidents, product metrics, support cases, costs, backups, changes and continued operation. |

#### Chatbot team — 11 skills

| Skill | What it does in human terms |
| --- | --- |
| `chatbot-atelier-director` | Coordinates a bot's full lifecycle and preserves its existing capabilities when work resumes. |
| `chatbot-atelier-research` | Investigates the audience, subject domain, platform constraints, integrations and practical feasibility. |
| `chatbot-atelier-specification` | Defines the bot's rules, state, data, tools, events, errors, privacy and acceptance criteria. |
| `chatbot-atelier-conversation` | Develops its language, character, useful questions, initiative, buttons and behavior in personal or group conversations. |
| `chatbot-atelier-knowledge` | Designs knowledge sources and scoped memory, retrieval where useful, corrections, expiry, deletion and privacy. |
| `chatbot-atelier-integrations` | Builds platform adapters, callbacks, tools, scheduled jobs and reliable external actions with recovery and delivery evidence. |
| `chatbot-atelier-media` | Creates and integrates the bot's visual identity, images, animation, audio and voice through available tools. |
| `chatbot-atelier-build` | Implements the complete agreed bot, including the necessary runtime and production integration work. |
| `chatbot-atelier-qa` | Checks conversation, knowledge, privacy, actions, media, runtime and negative scenarios against actual evidence. |
| `chatbot-atelier-release` | Prepares and performs an authorized release with exact source/build identification, delivery checks, data compatibility and rollback. |
| `chatbot-atelier-operations` | Maintains reliability, conversation quality, support, costs, migrations and ongoing development. |

#### Game team — nine skills

| Skill | What it does in human terms |
| --- | --- |
| `gamedev-director` | Coordinates the game project while preserving its accepted creative direction, decisions and checkpoints. |
| `gamedev-studio` | Establishes or restores the studio identity, accepted brand masters, developer identity and account readiness. |
| `gamedev-concepts` | Produces distinct game concepts with controls, interacting systems, progression, art direction and a feasible production route. |
| `gamedev-preproduction` | Expands the chosen concept into detailed game and technical design, numerical rules, catalogs, states and a production plan. |
| `gamedev-assets` | Creates and integrates art, animation, UI, sound and haptics, preserving accepted sources and the relationship to runtime assets. |
| `gamedev-build` | Implements the native mobile game: controls, camera, gameplay, enemies, world, progression, economy, saves and platform builds. |
| `gamedev-qa` | Checks actual gameplay, device behavior, controls, saves, performance and requirements, distinguishing real runtime evidence from document checks. |
| `gamedev-release` | Prepares signing, exact binaries, store materials, purchases, privacy, rollout and recovery for an authorized release. |
| `gamedev-liveops` | Develops and maintains the released game using observed telemetry, incidents, progression, content, economy and compatible changes. |

These are responsibilities, not a promise that 33 agents run simultaneously. The system should select the team and level of effort that the task needs. Independent review is only independent when another actor actually performs it; an author's self-check must be labeled accordingly.

## 3. Select your language before installation

Open the translated guide from the links above. English is the default when no preference is supplied. The translated guides cover the same steps; code, stable skill names, file names and protocol identifiers remain unchanged so that commands work consistently.

At the beginning of your installation or project, paste this and replace the language:

```text
My working language is English (en). Use it for explanations, questions,
status updates, handoff instructions and user-facing reports. Keep stable
skill names, command syntax and technical identifiers unchanged. Record
this preference in the project's saved context and handoffs. Ask separately
about the language of the product we are building.
```

A documentation language, conversation language and product language are separate choices. For example, you may read the Ukrainian guide, work with the agent in Ukrainian and ship an application in English and German. State all three when relevant. Record the preference in the project context template, or an existing equivalent file, and include it in each handoff. Changing a browser's page language alone does not set the language of another chat.

## 4. Prepare your accounts and sources

1. Sign into the ChatGPT or Codex account in which you intend to use the suite. Check that the required mode and skill-management tools are actually available in that account or workspace.
2. Open `https://github.com/alex-hohaizel/codex-agents`. The owner currently controls repository visibility. A private repository requires an authorized GitHub account and a connection with access to that exact repository.
3. In Work, connect or select GitHub through the available Plugins/connection interface. If access is restricted to selected repositories, include `alex-hohaizel/codex-agents`. Ask Work to read `README.md` and report the branch and revision it can actually access.
4. In local Codex, authorize local Git access if you intend to clone a private repository. A Work GitHub connection does not prove that Terminal on your computer can authenticate.
5. Use a named release or an exact commit for installation. Save that identifier. Reading an unpinned `main` branch while it is changing can mix versions.
6. Download the chosen repository revision through GitHub's **Code → Download ZIP**, or clone it with Git. Extract a downloaded archive before installation. You should see `kit/manifest.json`, `kit/portable/` and `kit/skills/`.
7. Do not place the download, plans or backups inside a skill-discovery directory. A normal folder such as Downloads or a dedicated skills-management workspace is suitable.

For local Git, use a confirmed branch and a new destination that does not contain other work:

```bash
git clone --branch main https://github.com/alex-hohaizel/codex-agents.git "codex-agents"
cd "codex-agents"
git rev-parse HEAD
git status --short
```

A clone on `main` is a convenient source checkout. Before applying an update, confirm that its SHA matches the release you chose. Do not paste access tokens into chat, project files, shell commands or handoff documents. Use the platform's account connection or credential flow.

## 5. Install in Work from a fresh account

### What this route does

It saves the 33 reusable skills as personal skills through the host's supported skill-management process. Merely connecting GitHub, uploading a ZIP, reading this guide or adding repository files as project sources does not establish that a skill was installed or loaded.

### Step by step

1. Open Work and create or open a skills-management project. This is where you manage the toolkit, rather than the product you will later build.
2. Select your language with the block in section 3.
3. Provide access to the selected repository revision. If Work cannot read private GitHub files, connect that repository or attach the curated package through the available file interface.
4. Invoke the available Skill Creator/skill-management capability. Ask it to inspect the package before changing installed records.
5. Paste the installation block below. It authorizes the scoped installation and the necessary verification.
6. Let Work inspect the existing skill inventory by stable name. For a fresh account it should create missing entries; for an existing account it should update the matching personal entries and preserve unrelated skills.
7. Keep the installation report. It must identify each of the 33 skills, version, source revision, result and unresolved failures.
8. Refresh or reopen the Skills page if its display is stale. Open a new chat in the intended product project and run the loading and practical check below.

```text
Install the 33 reusable personal skills from the selected, verified revision
of alex-hohaizel/codex-agents, using kit/manifest.json and kit/skills/.
My working language is English (en).

Use the host's supported personal-skill management process. Inspect existing
records by stable name, verify the package, preserve unrelated skills and
existing visual identity, and install or update the matching entries. Keep
backups and exact source provenance. Do not install project-specific agents
globally. Do not change product data, production services or account settings.

Report each stable name, version, source revision and create/update/noop/failure
status. Distinguish a saved skill from host discovery and actual task use.
If skill management is unavailable, explain the precise missing capability;
do not describe an uploaded or read-only copy as installed.
```

Work's supported management procedure may save skills one at a time. A partial result should name the completed entries and remaining entries, allowing safe continuation rather than starting over. A portable Codex updater run in a cloud filesystem is not proof that your Work personal-skill directory was updated.

## 6. Install or update in Codex

### The easiest route: ask Codex to do the controlled installation

1. Download or clone the chosen revision as described above.
2. Open Codex in your existing skills-management workspace. If this is your first installation, open the checkout or another normal management folder; a new product repository is unnecessary.
3. Give Codex the exact checkout path. On a Mac, select the folder in Finder and press **Option + Command + C** to copy its full path.
4. Paste the block below after setting your preferred language.
5. Review the final installation report and keep its journal and backup location.
6. Open a new chat in the actual product project for the loading and practical checks.

```text
Install the 33 baseline personal skills from the verified kit/ directory in
this checkout of alex-hohaizel/codex-agents. Use the selected release revision.
My working language is English (en).

This authorizes local audit → apply → verify, exact plans and backups for this
suite. Read kit/manifest.json and the updater's --help. Verify package integrity.
Audit the personal directories and any known project copies. Save plans and
backups outside skill-discovery roots. Apply only the exact ready plan. Preserve
unknown local changes and report conflicting files; do not bypass drift checks.

Preserve existing icon_small, icon_large, brand_color, icon paths and icon bytes,
including historical ./assets/ references. Verify using the exact journal
returned by apply. Report canonical_core_verified, visual_preservation_verified,
updated/noop counts, blockers, failures and duplicates.

Do not change products, production, plugins or environment configuration.
Then separately check host discovery of both constructors and the App, ChatBot
and Game directors. Do not treat installed files as proof of actual task use.
```

### Terminal route for someone who wants the exact commands

The portable updater requires Python 3.9 or later and uses the standard library. Run these commands from the repository root. The audit reads the package and installation locations and writes a proposed plan. Apply makes the planned installation changes and records a journal.

```bash
python3 kit/portable/update_skill_suite.py --help
python3 kit/portable/update_skill_suite.py audit --kit kit --plan ../agent-system-plan.json
python3 kit/portable/update_skill_suite.py apply --plan ../agent-system-plan.json
```

Read the result of `apply`. Copy its exact `journal` path into the verification command:

```bash
python3 kit/portable/update_skill_suite.py verify --kit kit --journal /absolute/path/from-apply/journal.json
```

The final path above is a placeholder. Replace it; do not run it literally. By default the updater targets `~/.agents/skills` and checks the legacy `~/.codex/skills` root. If your environment uses another supported personal root, use explicit `--destination` and `--legacy-root` arguments consistently. Inspect `audit --help` first. Add `--project-root /absolute/path/to/product` to audit relevant product-local copies. The updater does not automatically remove a project copy that shadows a personal skill.

A successful file installation means 33 sources verified at the intended version, no unresolved blockers/failures/duplicates, `canonical_core_verified=true` and `visual_preservation_verified=true` from verification using the actual apply journal. A hash check without that journal cannot prove preservation of your existing icons. Stop on a conflict and preserve the local work; do not use a force replacement to make the report appear clean.

### Check loading separately from installation

Ask Codex or Work in a fresh product chat:

```text
Before changing anything, identify the exact loaded source and version of
agent-foundry, design-specialist-skills and the three product directors.
Confirm which adaptive, research, visual-identity and Work↔Codex instructions
you actually read. Report unavailable sources separately.
```

Then give a small real task with a known input and acceptance criterion. For example, ask the application director to review a single screen's error states against an existing requirement, or ask a constructor to outline the responsibilities of one specialist agent. This checks behavior. It does not certify every product capability. Keep file installation, host loading, practical use and product acceptance as separate results.

## 7. Use the system on a real task

### A narrow engineering task

```text
Investigate repeated database queries in this endpoint. Preserve its API and
business behavior. First read the code and existing measurements. Identify
which evidence is missing, propose the smallest useful investigation and
implement a justified repair within this branch. Verify correctness and show
before/after measurements where the environment makes them possible.
```

This does not need a new company, product, brand or full market study. A constructor can design a reusable investigator if you want this workflow as an enduring agent; for a one-off task, use the existing relevant tools and instructions. The system should not manufacture a new agent just because a task is technical.

### A complete application

```text
BRIEF: I want an application for [audience] that solves [problem]. The target
platforms are [platforms], budget is [budget], and my role is [role]. Clarify
unknowns, investigate real alternatives and prepare complete options. Keep
all my requirements, including design, language, support and monetization,
visible throughout the plan. Do not silently select a concept for me.
```

The team should investigate what matters, compare options and identify release or account obstacles before a large build. After choosing a concept, keep the selected design references and all agreed requirements. An early working version is a checkpoint in that plan, not permission to discard the rest.

### A mobile game

```text
BRIEF: Develop distinct mobile game concepts for [audience/experience]. Cover
controls and feedback, interacting systems, enemies, meaningful progression,
art direction, monetization and a feasible Android/iOS production route.
Show comparable visual concepts. Preserve the selected identity through
assets and the playable implementation. Define actual device checks.
```

A concept image cannot prove animation, touch controls, performance or save recovery. The game workflow should connect the selected visual promise to editable source assets and a representative playable slice before producing the whole asset set.

## 8. Work and Codex on the same project

Work is useful where the necessary sources, research tools, design tools and connected services are available. Codex is useful where the source checkout, runtime, build tools and device or local integrations are available. Either mode may do more when it has the right capabilities. Choose by actual access and evidence, rather than assigning every thinking task to one mode and every code task to the other.

Create one identity for the product. Names such as `My Product [WORK]` and `My Product [CODEX]` help navigation, but they do not prove that the two projects contain the same product. Record the repository, branch, subdirectory, project identifiers and checkpoint sources. A new chat should remain inside that existing project.

### Keep a small shared context

Use the repository's project-context template or an existing equivalent in your product. Record at least: project identifier; repository and branch; current full commit SHA; task identifier; current stage; working and product languages; toolkit version and install receipt; accepted decisions; complete requirements source; design reference source; granted scope; current checkpoint; unresolved effects or decisions; and next action. Keep credentials out of this record.

### Work → local Codex, step by step

1. Ask Work: “Continue this stage in Codex. Prepare the handoff for this existing project.”
2. Work should identify the exact next deliverable and the evidence required to accept it. It should save or provide the relevant requirements, decisions, sources and checkpoint.
3. If an authorized shared channel is available, Work can save the handoff and verify the saved revision. Saving a file does not prove that another Codex session started.
4. Open the existing local checkout. If there is no local copy, clone the confirmed repository and branch into the chosen folder. Authenticate locally for private repositories.
5. Before updating the checkout, inspect it:

```bash
git remote get-url origin
git branch --show-current
git rev-parse HEAD
git status --short
```

6. If the working tree is clean and an update on that branch is required, use `git pull --ff-only origin <confirmed-branch>` with the real branch name. Confirm the resulting full SHA. If local changes or divergent history exist, preserve them and resolve the discrepancy before dependent work.
7. Open the exact folder in Codex's project interface. For an existing product, use its existing project; add the folder through the available project editing interface if necessary.
8. Paste the filled handoff block below. Codex first confirms repository identity, revision, local changes, permissions and checkpoint, then works on the scoped action.
9. Keep its result report, commit/build references and test evidence for the return handoff.

### Codex → Work, step by step

1. Ask Codex to prepare a result handoff or a new task handoff for the same existing project.
2. Include the actual changed files, full SHA or artifact revision, checks performed, limitations, open decisions and next action. State whether changes are local, committed or published.
3. If publishing the agreed changes to a named branch is authorized, publish only that scope and verify the remote revision. Otherwise provide a controlled artifact through the available channel. A local Mac path is not automatically readable from Work.
4. Open the existing Work project, connect the relevant repository or attach the exact artifact, and paste the handoff.
5. Work reads the actual sources and checks the input revision before reviewing or continuing. It should report inaccessible files explicitly.
6. Record acceptance separately from delivery and execution. A report that a build exists is not the same as product acceptance.

### Copyable handoff

Replace every bracketed field before using this block:

```text
Continue the existing project [project ID/name] in [Work/Codex].
Working language: [language/code]. Product languages: [languages].
Repository: [URL]. Branch/subdirectory: [branch/path].
Input revision: [full SHA or exact artifact revision].
Task ID and stage: [ID/stage].
Checkpoint: [exact accessible source].
Requirements and accepted decisions: [exact sources].
Design references and identity: [exact sources, if relevant].
Expected deliverable and acceptance: [concrete result/checks].
Authorized scope: [what may be changed or published].
Completed work and evidence: [facts and references].
Open decisions, blockers or uncertain external effects: [details/none].
Next action: [one concrete action].

First verify the project identity, revision, available tools and permissions.
Preserve every accepted requirement and decision. Do not reinitialize the
product. Distinguish prepared handoff, verified delivery, receipt, execution,
result and acceptance. Continue the authorized work that is actually possible.
```

## 9. Resume after an interrupted chat

Open a new chat in the same project and ask it to restore the last verified checkpoint. Supply the checkpoint source if it is not already accessible. It should reconcile the task, requirements, source revision, current files and actual external results before continuing.

```text
Restore this existing task from its last verified checkpoint and actual sources.
Preserve requirements, decisions, permissions, completed results and uncertain
external effects. Verify the current revision and the next action's owner.
Before repeating a deployment, payment, message or other external action,
check whether the previous attempt actually completed. Continue the available
authorized work and record a new checkpoint.
```

A stalled conversation is not evidence that its last operation failed. Recovery must check the real result before retrying an action that could be duplicated.

## 10. Update versions without losing an existing project

### Read the release record first

Each release should explain what changed, which users are affected, prerequisites, installation steps, project adoption steps, verification, known limitations and rollback. The general guide must also change when the normal workflow changes. Do not rely on a version number alone.

The6.0.0 release preserves the33 stable names and icon identity while hardening evidence, source dependencies, JSON admission and state writes. It adds self-contained production/context profiles and explicit reference fidelity. Historical protocol and native runtime schema numbers remain distinct; renaming an old schema to the suite number without a migration breaks compatibility.

### Existing Agent Systems 2.3 / Game 4.3 projects

1. Save the current project checkpoint, accepted requirements, decisions, design masters, source revision, toolkit version and known external effects.
2. Record where each skill or project agent is actually loaded from. Inventory personal and project-local copies; do not assume that changing one global directory changes every project.
3. Install the target suite through the applicable Work or Codex route above. Keep the source version and installation receipt.
4. Reopen the existing project and run a read-only compatibility review before the next dependent action.
5. Ask its director or constructor to compare the current project state with the new workflow. Identify an explicit native-state refresh or workflow upgrade only where needed. Preserve product behavior, accepted choices and unknown effects.
6. Preview the exact changes. If a state migration is required, use its supported tool and actual `--help`; bind the preview to the source-state hash, target-suite hash and authority source. Apply the authorized reviewed plan rather than inventing a historical approval.
7. Recheck every affected requirement and the current stage's acceptance criteria. Run a small real continuation task and save its evidence.
8. Record the adopted toolkit version in the product checkpoint. Keep the migration record so the next chat can explain the transition.

Game6.0.0 contains a reviewed workflow-upgrade route for4.2.0/4.3.0/5.0.0 projects while keeping runtime schema 2.0.0. Its use depends on the actual project state and the tool's supported inputs. App and ChatBot projects likewise need their own state and compatibility review; they must not be passed through a game migration merely because the suite has one shared version.

### Agents previously built with a constructor

Updating the constructor does not rewrite agents it created earlier. Those agents may contain project-specific rules, tools, knowledge and visual identity. Inventory them in their own projects. Compare old source, local changes and the proposed new source. Preserve the original ownership/installation evidence. If that evidence is missing, prepare an explicit adoption comparison and plan; do not fabricate an old receipt. Run regression cases for the agent's actual responsibilities and record the adopted version separately.

The reusable repository excludes private product-agent source bundles. An individual project's update belongs in that project's controlled source and migration record, not in everyone's global skill installation.

### Preserve visual identity

Existing Codex icons, icon paths, color and icon bytes must survive routine updates. A new version is not an instruction to redesign an existing skill or product. New skills without an identity can receive the appropriate system or project style. Work may manage a service avatar itself; keep its host display behavior distinct from the portable Codex identity. Preserve selected product and game design originals, not merely a verbal description of them.

### Roll back carefully

For a Codex suite installation, use the exact installation journal:

```bash
python3 kit/portable/update_skill_suite.py rollback --journal /absolute/path/from-apply/journal.json
```

The rollback checks backups and protects later unknown changes. It reverses the skill installation represented by that journal. It does not undo a product data migration, deployment, message, purchase or other external action. Work restoration should use its supported skill-management route and the saved prior source. A product-state rollback needs its own reviewed recovery procedure.

## 11. Keep future updates complete

For every future toolkit change, update this repository with the canonical sources, requirements affected, package contents, version record, migration steps, verification evidence and any required guide or translation changes. Preserve previous release records. Rebuild packages and integrity metadata from the checked sources; avoid publishing an archive assembled from a stale host cache.

Run the repository's check and package commands according to their current `--help` and maintainer documentation. Confirm the remote commit after publishing. “Saved locally”, “committed”, “published”, “installed”, “loaded” and “adopted by a project” are separate statuses. If access prevents publication, preserve the completed work and report the exact unsynchronized revision.

A repository rule is effective when a future agent reads it in an environment with the needed access. It is not a global listener for all other chats and computers. Begin a future skills-management task by connecting this repository and reading its `AGENTS.md`, requirements and latest release record. A separate scheduled synchronization service would require its own actual runtime and authorization; the suite does not silently create one.

## 12. Troubleshooting

| Symptom | What to check next |
| --- | --- |
| Work cannot read the repository | Verify the GitHub account, exact private repository grant and selected connection; ask it to read one known file. |
| Local clone asks for authentication | Set up local Git authorization using the platform's credential flow. Work's connection is separate. |
| Skills do not appear after saving | Refresh or reopen the Skills page, then use a fresh project chat and verify actual source discovery. |
| Two copies of the same skill appear | Audit stable names in personal and project roots. Preserve local changes and resolve the exact duplicate source; do not delete unrelated skills. |
| Updater reports drift or a conflict | Save the local diff and compare the named files with the selected source. Use a reviewed reconciliation plan. |
| A file check passed but the agent behaves as before | Verify the source actually loaded by the host, then run a small task; file integrity alone is insufficient. |
| Work cannot see code changed on a Mac | Publish the authorized scope or attach an exact artifact; a local path alone gives no access. |
| A new chat has lost decisions | Restore the checkpoint and complete requirements sources before continuing. Update the saved context. |
| The first working version omits agreed design or language | Reconcile the requirement ledger; retain those requirements in the plan and name their implementation and acceptance steps. |
| Deployment, store submission or device checks are unavailable | Name the exact missing account, tool, device or access and continue independent preparation. Do not claim the unavailable check passed. |
| An agent claims it started another session | Ask for a verified launch/receipt reference. A handoff file proves only the status actually observed. |
| You want continuous jobs | Confirm a real scheduler, executor, credentials, liveness checks and recovery route. Skill installation alone does not supply them. |

## 13. Official documentation and scope of evidence

The host's interfaces and account availability can change. Consult the actual interface and current official documentation when installing or connecting services. Product behavior references checked for this guide on 7 November 2026:

- [Build skills — ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills): reusable skill structure, local discovery and installation concepts.
- [Plugins — ChatGPT Learn](https://learn.chatgpt.com/docs/plugins): plugin directory, connection and distribution concepts.

This repository distributes a reusable suite and its controlled installation workflow. A public marketplace plugin, commercial license, permanent hosted runtime, third-party paid tools and credentials are separate deliverables unless a specific release explicitly supplies and verifies them. The marketing concepts illustrate workflows and intended uses; final promotional claims must match verified capabilities and evidence.
