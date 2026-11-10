# Current system: what each component does

This source-backed catalogue describes commit [8951398b38a9610854823302ea612cb3844d52e6](https://github.com/alex-hohaizel/codex-agents/tree/8951398b38a9610854823302ea612cb3844d52e6), reviewed on2026-11-10. It explains what exists, where it lives and when it is used. It does not release a new suite, install anything or certify a future result. [Повна українська версія](CURRENT-SYSTEM.uk.md). Both documents have the same component IDs and complete equivalent cards. This appendix is EN/UK; the existing seven-language general guides retain their separate coverage.

## Read the system in four layers

1. **One entry and accountable owner.** Start with atelier-orchestrator when you want one conversation. Describe the desired result in ordinary language. It can answer directly, reuse a specialist/project agent, coordinate a director, compose several parts or route approved construction/maintenance. It does not force a new agent.
2. **Reusable methods.** The33-core suite contains two constructors,11 application stages,11 chatbot stages and9 game stages. A director coordinates a product; a specialist produces a defined part. Direct calls remain supported.
3. **Actual execution.** The AI host reads the skill and uses real available tools. Local Python helpers validate/record/plan particular things; they are not an autonomous expert workforce. The optional Mac service offers real bounded Codex execution and specific control operations when started and connected.
4. **Evidence and ownership.** Native project sources stay authoritative. Source/tool/runtime observations, independent review and owner acceptance are distinct. An installed file, role title, screenshot, green schema or completed turn cannot stand in for all of them.

A generated project agent is not a36th core component. It has its own source, version, requirements, identity and native state inside its product project. This catalogue does not publish private project agents, account entries or customer data. Vendor/system/plugin skills are outside the35 owner-maintained reusable-source count.

## Versions and practical entry

| Object | Baseline version | Meaning |
|---|---|---|
|Repository edition|1.3.0|Documentation/distribution and service integration edition|
|33-core suite|6.0.0|Constructors and App/ChatBot/Game reusable sources|
|Optional orchestrator|1.1.0|Universal conversational/panel entry|
|Optional maintenance skill|1.0.0|Repository maintenance contract|
|Local Agent Atelier|0.2.0|Personal Mac workbench/runtime|
|Game native contracts|Model4 / handoff1 / runtime2|Independent product formats, not suite versions|

In Codex, explicitly select a discovered skill with $atelier-orchestrator, $agent-foundry or another stable name below. Automatic selection depends on the actual host and installed description. Read the actual source before delegating. Section R names role configurations, not $skill selectors.

For an existing product, restore its checkpoint, requirements, decisions, accepted originals/persona, settings, unfinished/unknown work and current authority. Reuse its verified project agent. After creating an agent, the orchestrator should recommend continuing through it; later requests to the orchestrator retain that binding. Construction and product execution keep separate scopes. A simple request does not need a passport or team; a new target-agent design requires approval of its exact constructor passport.

**Example:** “Help turn this prototype into a reliable product.” The entry inspects its actual source and accepted behavior, selects the needed director/specialists and closes real production gaps. Useful design/code should remain. A genuine reusable-agent gap can go through Foundry; changing frameworks or creating an agent is not the default completion criterion.

## How to read a card

Instructions are a method the current AI must perform with real tools. A structural helper checks declared records/references/bytes. A local controller also owns specific native state transitions. A filesystem tool performs scoped package/install/source changes. Service runtime executes its documented commands after launch. None alone proves the entire final product.

Each card names trigger, input, output and evidence limits. Optional sources are outside the33-core updater. Logical groups can share implementation files; the catalogue does not claim75 separate processes.

## Terms in ordinary language

The stable technical names remain visible so you can find their files and receipts. They mean:

| Term used in cards | Practical meaning |
|---|---|
|source / source pin|The actual input/file and its exact recorded revision or content hash|
|checkpoint / native state|Saved progress and the project’s own authoritative records, rather than a chat recollection|
|scope / authority|The specific work and actions currently authorized, with their limits|
|passport / blueprint|A versioned description of what an agent/skill must do before its creation is approved|
|contract / consumer / handoff|What a component promises, who actually uses its output, and the exact package transferred|
|capsule|A bounded task packet containing relevant requirements, inputs, decisions and limits|
|master / derivative / lineage|The approved original, its adapted output and the trace connecting them|
|recipe / attempt / receipt|The reproducible method, an actual run of it and the observed record of what occurred|
|render / playback / import|Actually displaying, playing or loading the material into its destination|
|schema / structural PASS|Correct declared format/links/bytes; useful, but not proof of meaning, taste or live operation|
|runtime / provider / device proof|Observed behavior of running code, an external service or a particular physical device|
|fixture / negative control|A test input and an intentionally faulty case that must be rejected|
|independent QA / owner acceptance|A different reviewer’s examination and the owner’s own acceptance; these are distinct|
|installation / discovery / adoption|Copying managed sources, the host finding them, and an existing project actually using them|
|idempotency / reconciliation|Preventing repeated logical actions and checking an uncertain result before retry|
|model / dataset / features|The learned/prompted component, the versioned data used, and input values supplied for a decision|
|tenancy / ACL / tombstone|Separation of users/projects, access rules and a deletion marker respected during later work/restore|
|rollback|A qualified return to known prior source/state; it cannot automatically undo external effects|

## C · The33 core reusable skills

### Constructors

### C01 · agent-foundry · 6.0.0

Source: [kit/skills/agent-foundry/SKILL.md](../../../kit/skills/agent-foundry/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Design and deliver a reusable specialist agent, including its lifecycle, tools, memory, team and verification.
- **Use when / activation:** An explicit request to create/adapt an agent, or a verified capability gap routed by the orchestrator. Target creation requires approval of the exact versioned passport.
- **Input → result:** Plain-language objective, existing sources and constraints → researched domain, M0 sketch, M1 full passport, M2 delivery with inherited requirements, sources and launch/return instructions.
- **Evidence and limits:** The constructor, generated agent and its eventual product are separate objects. Structural/depth checks do not prove expert quality, installation, execution or deployment.

### C02 · design-specialist-skills · 6.0.0

Source: [kit/skills/design-specialist-skills/SKILL.md](../../../kit/skills/design-specialist-skills/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Create a focused reusable skill or coherent skill family with specialist ownership and inherited quality contracts.
- **Use when / activation:** A skill/family creation request or an approved Foundry child assignment; read Skill Creator and approve the exact blueprint before target creation.
- **Input → result:** Task, requirements, competencies and current tools → versioned skill.blueprint/2, self-contained skills, UI metadata, references/helpers and checked handoff.
- **Evidence and limits:** Blueprint approval records are not authenticated consent. Current tooling does not read/convert every historic blueprint format; creating a skill is not running its product.


### App Atelier · application lifecycle

### C03 · app-atelier-director · 6.0.0

Source: [kit/skills/app-atelier-director/SKILL.md](../../../kit/skills/app-atelier-director/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Coordinate the complete application lifecycle and keep one product owner.
- **Use when / activation:** A new application, multi-stage continuation or cross-component decision.
- **Input → result:** Idea/current checkpoint → selected stage owners, scoped tasks, integrated evidence and next action.
- **Evidence and limits:** Coordination instructions do not start an app runtime or prove a release.

### C04 · app-atelier-research · 6.0.0

Source: [kit/skills/app-atelier-research/SKILL.md](../../../kit/skills/app-atelier-research/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Find actual user needs and credible opportunities; compare existing alternatives.
- **Use when / activation:** An opportunity search, market question or missing domain evidence.
- **Input → result:** Audience/markets/limits → source and claim ledger, alternatives, need map, shortlist, counterarguments and unknowns.
- **Evidence and limits:** Public reviews and synthetic scenarios are not validated demand, paying customers or causal market evidence.

### C05 · app-atelier-concepts · 6.0.0

Source: [kit/skills/app-atelier-concepts/SKILL.md](../../../kit/skills/app-atelier-concepts/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Turn research into complete product options with useful core, commercial model and operating economics.
- **Use when / activation:** A researched direction needs comparison and owner selection.
- **Input → result:** Need/alternatives/constraints → concepts, journeys, monetization options, unit economics, automation/dependency map and selection brief.
- **Evidence and limits:** Forecasts remain assumptions. A selected concept does not authorize build, campaigns, paid tools or publication.

### C06 · app-atelier-specification · 6.0.0

Source: [kit/skills/app-atelier-specification/SKILL.md](../../../kit/skills/app-atelier-specification/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Translate the accepted concept into implementable product and technical contracts.
- **Use when / activation:** The owner has selected a concept, or an existing specification needs a bounded change.
- **Input → result:** Accepted intent → PRD/TDD, entities, data/auth/API/payment/support contracts, platform journeys, estimates, dependencies and acceptance matrix.
- **Evidence and limits:** A complete specification is not working code, provider access, store feasibility or proven economics.

### C07 · app-atelier-experience · 6.0.0

Source: [kit/skills/app-atelier-experience/SKILL.md](../../../kit/skills/app-atelier-experience/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Produce the application brand, UX/UI, interactive prototype and production design materials.
- **Use when / activation:** A new design, state/flow repair or accepted design needs production handoff.
- **Input → result:** Requirements, real references and current masters → journeys/states, style rules/tokens, editable assets, prototype, representative integrated slice and handoff.
- **Evidence and limits:** A screenshot is not interaction; matching colors is not identity. Actual medium, accessibility and native/device fidelity need their own observations.

### C08 · app-atelier-build · 6.0.0

Source: [kit/skills/app-atelier-build/SKILL.md](../../../kit/skills/app-atelier-build/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Implement the accepted application with proportionate architecture, data, access, billing and recovery.
- **Use when / activation:** Approved implementation scope and actual source/toolchain are available.
- **Input → result:** PRD/TDD, masters and current repository → real end-to-end slice, client/backend implementation, tests, reproducible builds and delivery package.
- **Evidence and limits:** Compilation, simulator, physical device and production are different proof levels. Known platform/research contradictions below remain unresolved in this baseline.

### C09 · app-atelier-support · 6.0.0

Source: [kit/skills/app-atelier-support/SKILL.md](../../../kit/skills/app-atelier-support/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Build and maintain product help, support knowledge and a safely scoped support bot.
- **Use when / activation:** A product needs support design, implementation, integration or repair.
- **Input → result:** Actual product versions, cases and chosen channels → authenticated channel linking, scoped knowledge, support flows/actions, cost caps and recovery.
- **Evidence and limits:** Knowledge files alone do not start support service. A user-supplied name/email is not authorization; RAG is conditional, not a required stack.

### C10 · app-atelier-qa · 6.0.0

Source: [kit/skills/app-atelier-qa/SKILL.md](../../../kit/skills/app-atelier-qa/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Independently evaluate requirements, agent behavior and the actual application.
- **Use when / activation:** A frozen artifact/change reaches an applicable acceptance gate.
- **Input → result:** Exact sources, raw cases, builds and author identity → positive/negative tests, findings, coverage, scoped verdict and repair handoff.
- **Evidence and limits:** Author self-check is not independent QA; schema PASS is not device proof, market demand or permission to release.

### C11 · app-atelier-release · 6.0.0

Source: [kit/skills/app-atelier-release/SKILL.md](../../../kit/skills/app-atelier-release/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Prepare and perform an authorized application release, including early feasibility checks.
- **Use when / activation:** Early store/account feasibility or a specific approved release candidate.
- **Input → result:** Exact RC/source/assets, QA and target permissions → signing/store materials, migration/rollback plan, actual submission/readback receipts and operational handoff.
- **Evidence and limits:** Submitted, approved, available and observed are separate states. No new spending/publication follows merely from selecting this skill.

### C12 · app-atelier-growth · 6.0.0

Source: [kit/skills/app-atelier-growth/SKILL.md](../../../kit/skills/app-atelier-growth/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Plan and operate permitted acquisition with truthful content, automation and measurable economics.
- **Use when / activation:** Before substantial build, or for an explicitly scoped post-release channel/measurement task.
- **Input → result:** Segments, product value, budget and actual channel access → funnel, channel/content plan, automation jobs/caps, approved activation receipts and observations.
- **Evidence and limits:** A plan is not an active campaign; publishing/outreach/spend require their actual scope. Correlation and estimates do not establish uplift or future CPA.

### C13 · app-atelier-operations · 6.0.0

Source: [kit/skills/app-atelier-operations/SKILL.md](../../../kit/skills/app-atelier-operations/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Maintain an existing application, investigate incidents and manage actual operating costs and continuity.
- **Use when / activation:** A real incident, maintenance request, approved monitoring task or lifecycle change.
- **Input → result:** Current source/deploy, symptom, logs and authority → causal diagnosis, bounded repair, measured metrics/costs, restore/export/end-of-life steps.
- **Evidence and limits:** Old status is not current health. Monitoring runs only through a real authorized scheduler/runtime; binary rollback does not undo data or provider effects.


### ChatBot Atelier · chatbot lifecycle

### C14 · chatbot-atelier-director · 6.0.0

Source: [kit/skills/chatbot-atelier-director/SKILL.md](../../../kit/skills/chatbot-atelier-director/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Coordinate a complete chatbot while retaining its domain, persona and native project state.
- **Use when / activation:** A chatbot idea, continuation or multi-part change.
- **Input → result:** Intent/current checkpoint → system applicability, dynamic team, stage tasks, integrated result and continuation.
- **Evidence and limits:** A stage report does not prove a live bot, natural conversation or delivered action.

### C15 · chatbot-atelier-research · 6.0.0

Source: [kit/skills/chatbot-atelier-research/SKILL.md](../../../kit/skills/chatbot-atelier-research/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Research user needs, domain mechanisms, platforms and feasible operations.
- **Use when / activation:** An unclear domain or missing evidence/capability.
- **Input → result:** Audience/current workflow/constraints → JTBD, alternatives, primary sources, operation passports, gaps and recommendation.
- **Evidence and limits:** A listed API/model is not a verified callable/integrated route; research does not authorize external actions.

### C16 · chatbot-atelier-specification · 6.0.0

Source: [kit/skills/chatbot-atelier-specification/SKILL.md](../../../kit/skills/chatbot-atelier-specification/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Define the bot’s causal rules and typed contracts across state, tools and delivery.
- **Use when / activation:** An accepted direction needs implementation detail or a contract repair.
- **Input → result:** Requirements and domain sources → actors/scopes, units/algorithms, lifecycle guards, transactions, memory/time/media contracts, vectors and acceptance.
- **Evidence and limits:** Specified behavior is not execution. LLM outcomes retain uncertainty; exactly-once claims need a proven bounded meaning.

### C17 · chatbot-atelier-conversation · 6.0.0

Source: [kit/skills/chatbot-atelier-conversation/SKILL.md](../../../kit/skills/chatbot-atelier-conversation/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Design natural conversation, persona, listening, initiative and shared interaction.
- **Use when / activation:** A new conversation policy or a real dialogue defect.
- **Input → result:** Actual intent/recipient/context and approved persona → conversation rules, meaningful buttons, examples, minimal pairs and multi-turn evaluation.
- **Evidence and limits:** A conversational claim cannot replace a completed tool effect. LLM ratings are not human naturalness evidence.

### C18 · chatbot-atelier-knowledge · 6.0.0

Source: [kit/skills/chatbot-atelier-knowledge/SKILL.md](../../../kit/skills/chatbot-atelier-knowledge/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Implement scoped memory, sources, retrieval and correction/forget/restore lifecycle.
- **Use when / activation:** The bot needs durable knowledge or an existing memory/privacy path changes.
- **Input → result:** Sources, ACL, purpose and retention → memory/knowledge schemas, conditional RAG, retrieval/attribution tests, deletion lineage and restore limits.
- **Evidence and limits:** Embeddings/summaries inherit source access. A tombstone does not certify immediate physical erasure of every immutable backup.

### C19 · chatbot-atelier-integrations · 6.0.0

Source: [kit/skills/chatbot-atelier-integrations/SKILL.md](../../../kit/skills/chatbot-atelier-integrations/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Connect platform events, tools, reliable jobs, groups and provider operations.
- **Use when / activation:** A real action, callback, schedule, payment or external integration is required.
- **Input → result:** Actor/scope/spec and actual API → adapters, dedup/fence/retry, uncertain-outcome reconciliation, schedules, receipts and failure tests.
- **Evidence and limits:** Transport acknowledgement is not domain success or human reading. Mocks do not prove provider delivery or group consent.

### C20 · chatbot-atelier-media · 6.0.0

Source: [kit/skills/chatbot-atelier-media/SKILL.md](../../../kit/skills/chatbot-atelier-media/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Produce and integrate images, character motion, audio/music/voice and video.
- **Use when / activation:** The task calls for a new/changed media artifact or delivery repair.
- **Input → result:** Purpose, approved originals, rights and exact operation capability → recipes/attempts, editable sources, final files/manifest, playback/decode and integration/readback evidence.
- **Evidence and limits:** Source track, full motion/audio playback and runtime membership are separate. A PNG or frame count cannot prove rig, action or sound.

### C21 · chatbot-atelier-build · 6.0.0

Source: [kit/skills/chatbot-atelier-build/SKILL.md](../../../kit/skills/chatbot-atelier-build/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Implement the actual chatbot from source through action and delivery/recovery.
- **Use when / activation:** Approved build/repair scope with actual repository and runtime context.
- **Input → result:** Contracts/current source/toolchain → event→authorized state→effect→verified outcome→delivery slice, production code, isolated tests and handoff.
- **Evidence and limits:** No required Redis/vector/workflow stack by default. Mock boundaries and local tests are not live platform proof.

### C22 · chatbot-atelier-qa · 6.0.0

Source: [kit/skills/chatbot-atelier-qa/SKILL.md](../../../kit/skills/chatbot-atelier-qa/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Independently test conversation, state, memory, actions, media and runtime together.
- **Use when / activation:** A frozen change/result is due for acceptance.
- **Input → result:** Raw cases, sources/config/assets and actors → negative/race/restart/privacy tests, eight conversation strata, media checks and scoped verdict.
- **Evidence and limits:** A high conversation score cannot compensate for privacy/authority/false-success defects. Human, live and device gates require actual access.

### C23 · chatbot-atelier-release · 6.0.0

Source: [kit/skills/chatbot-atelier-release/SKILL.md](../../../kit/skills/chatbot-atelier-release/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Perform an authorized compatible bot release with exact source/assets and rollback limits.
- **Use when / activation:** A prepared release/migration or an approved publication operation.
- **Input → result:** Frozen RC, QA, migrations and target authority → rollout/stop/rollback, actual deploy/publication identity, bounded smoke/readback and operations handoff.
- **Evidence and limits:** Deployment, message delivery, media membership and human satisfaction are separate; uncertain remote writes are reconciled before retry.

### C24 · chatbot-atelier-operations · 6.0.0

Source: [kit/skills/chatbot-atelier-operations/SKILL.md](../../../kit/skills/chatbot-atelier-operations/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Repair and evolve an existing bot without losing its capabilities or identity.
- **Use when / activation:** An incident, real defect, scoped enhancement or requested operational review.
- **Input → result:** Current source/provider/checkpoint and symptom → causal repair, dependency-based retest, cost/quality metrics, support/restore/export and next action.
- **Evidence and limits:** No imaginary background monitoring. Prompt/model/generator updates invalidate affected evidence while unchanged evidence can carry forward with proof.


### Game Atelier · game lifecycle

### C25 · gamedev-director · 6.0.0

Source: [kit/skills/gamedev-director/SKILL.md](../../../kit/skills/gamedev-director/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Coordinate a game from studio/concept through design, craft, native implementation, release and evolution.
- **Use when / activation:** A game idea, resumed project or cross-system decision.
- **Input → result:** Intent/current Game Model → applicable domains, dynamic competencies, production graph, integrated acceptance and next stage.
- **Evidence and limits:** Game Model4, handoff1 and runtime2 are separate contracts. Director instructions and model validation are not a playable game or proof of fun.

### C26 · gamedev-studio · 6.0.0

Source: [kit/skills/gamedev-studio/SKILL.md](../../../kit/skills/gamedev-studio/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Preserve/create studio identity and prepare lawful masters, derivatives and operational setup.
- **Use when / activation:** New studio setup, brand continuation, asset derivation or account-readiness review.
- **Input → result:** Accepted originals/rights and current accounts → style/master catalogue, exact derivatives, setup dependencies, human guide and studio payload.
- **Evidence and limits:** Approved name, graphic master, legal entity and configured account are distinct. A redraw is not the byte-identical approved original.

### C27 · gamedev-concepts · 6.0.0

Source: [kit/skills/gamedev-concepts/SKILL.md](../../../kit/skills/gamedev-concepts/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Research and compare complete game concepts with causal depth and feasible visual direction.
- **Use when / activation:** A new concept search, repair or explicit owner selection task.
- **Input → result:** Intent/studio/profile → diverse C0 sketches, complete C1 candidates, mechanics/world/progression/economics, camera/art production envelope and comparison.
- **Evidence and limits:** Concept count, recolors or many mechanics do not prove diversity/depth. A concept frame is not runtime, full world scope or a production permission.

### C28 · gamedev-preproduction · 6.0.0

Source: [kit/skills/gamedev-preproduction/SKILL.md](../../../kit/skills/gamedev-preproduction/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Define the complete implementable game and its source→runtime contracts.
- **Use when / activation:** An accepted concept needs GDD/TDD or rules require a controlled change.
- **Input → result:** Accepted C1/model/studio → rules/state/units/oracles, camera/input/world/reward/commerce contracts, asset scope, representative native slice plan and handoff.
- **Evidence and limits:** Simulation tests a named hypothesis, not human comprehension, sensory comfort, retention or revenue. No genre/economy/engine preset is mandatory.

### C29 · gamedev-assets · 6.0.0

Source: [kit/skills/gamedev-assets/SKILL.md](../../../kit/skills/gamedev-assets/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Produce the full game art, animation, UI, sound and haptics and integrate their real consumers.
- **Use when / activation:** Accepted model states and production assets need creation, repair or integration.
- **Input → result:** Model IDs, exact references, rights and available operations → editable masters, 2D/vector/3D/rig/clips/VFX/UI/audio, exports/catalogue, actual assembly and modality evidence.
- **Evidence and limits:** PNG generation does not supply mesh/rig/physics. Actual source reopen/export/import, motion/listening and device haptics have separate proof gates.

### C30 · gamedev-build · 6.0.0

Source: [kit/skills/gamedev-build/SKILL.md](../../../kit/skills/gamedev-build/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Implement native gameplay, systems, persistence and platform integration from the accepted model.
- **Use when / activation:** Approved implementation scope and a verified engine/export/toolchain route.
- **Input → result:** Model/GDD/TDD, assets and real project → native slice, finite launch scope, tests, save/recovery, actual build files and receipts.
- **Evidence and limits:** An APK, AAB, simulator app, archive and TestFlight availability differ. Structural build receipts do not prove signing, thermal behavior, physical input or fun.

### C31 · gamedev-qa · 6.0.0

Source: [kit/skills/gamedev-qa/SKILL.md](../../../kit/skills/gamedev-qa/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Independently test the game’s rules, experience, craft and actual native implementation.
- **Use when / activation:** A named design/slice/release gate is due.
- **Input → result:** Frozen model/source/build/assets and raw scenarios → design-derived positives/negatives, interactions, commerce/save/privacy tests, sensory/device/human limits and verdict.
- **Evidence and limits:** A schema/byte PASS cannot establish balance, touch comfort or human enjoyment. Author, independent QA and final judge are distinct actors.

### C32 · gamedev-release · 6.0.0

Source: [kit/skills/gamedev-release/SKILL.md](../../../kit/skills/gamedev-release/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Prepare and execute an authorized native game release against current platform rules.
- **Use when / activation:** Early release feasibility or a specific frozen release candidate.
- **Input → result:** Exact binaries/config/content/QA, target accounts and rights → compliance snapshot, store/privacy/commerce material, controlled rollout, receipts and recovery handoff.
- **Evidence and limits:** Upload, review, approval, tester availability and live release differ. Store rollback may need a forward fix; SDK/account/device prerequisites remain real.

### C33 · gamedev-liveops · 6.0.0

Source: [kit/skills/gamedev-liveops/SKILL.md](../../../kit/skills/gamedev-liveops/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Maintain and evolve a released/beta game using observed player and runtime evidence.
- **Use when / activation:** An incident, player-experience problem, approved measurement or scoped evolution.
- **Input → result:** Actual build/store/config/economy/save versions and observations → diagnostics, causal repair proposals, retests, permitted changes, support and checkpoint.
- **Evidence and limits:** Observational cohorts and simulations are not causal retention/LTV proof. Recurring operation and human research require actual task scope.


## O · Two optional reusable skills

### O01 · atelier-orchestrator · 1.1.0

Source: [optional-skills/atelier-orchestrator/SKILL.md](../../../optional-skills/atelier-orchestrator/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Provide one conversational entry, select a sufficient route and integrate the original result.
- **Use when / activation:** Explicit invocation accepts any request; also project continuation, multiple components, portfolio or system maintenance.
- **Input → result:** User outcome and actual sources → direct work, specialist/director/project-agent reuse, composition, approved construction/maintenance or an exact host bridge; optional loopback commands.
- **Evidence and limits:** It does not require a new agent for every request, replace the project owner, grant permissions or create panel availability. check_routing.py validates declarations only.

### O02 · codex-agents-maintenance · 1.0.0

Source: [maintenance-skill/SKILL.md](../../../maintenance-skill/SKILL.md). Type: Instructions executed by the current AI host.

- **Purpose:** Keep authorized reusable-system changes, documentation, migration, packages and publication coherent.
- **Use when / activation:** Creating/changing/releasing the owner’s agent system, or recovering incomplete publication.
- **Input → result:** Actual repository/source diff and current policy → version/impact decision, compatible update/adoption/rollback instructions, equivalent docs and verified distribution/publication record.
- **Evidence and limits:** Repository presence is not installation; local commit/archive is not remote publication. It grants no new spending, product deployment, visibility or license change.


## R · Twelve actual role profiles

Optional competence profiles, not a mandatory twelve-person team. The parent assigns actual deliverables and owned files within real slots. Independent review needs a different actual actor. Shared role restrictions remain in force. Only foundry-cost pins a model; other profiles have no fixed override.

### R01 · foundry-architecture

Source: [agent-profiles/foundry-architecture.toml](../../../agent-profiles/foundry-architecture.toml). Type: Subagent role configuration.

System architecture and state-machine lead.

- **Purpose:** Compare 2–3 feasible designs; own module boundaries, ERD, API/events, concurrency, idempotency, recovery, resource and rollout. Prefer simplest coherent vertical slice.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R02 · foundry-backend

Source: [agent-profiles/foundry-backend.toml](../../../agent-profiles/foundry-backend.toml). Type: Subagent role configuration.

Backend and data implementation specialist.

- **Purpose:** Implement only assigned files and tests. Keep state ownership, schema, migrations, idempotency, privacy lineage and error handling coherent.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R03 · foundry-conversation

Source: [agent-profiles/foundry-conversation.toml](../../../agent-profiles/foundry-conversation.toml). Type: Subagent role configuration.

Conversation, personality and social interaction specialist.

- **Purpose:** Design natural, context-aware conversation, listening, clarification, initiative, humor, consent, tone, temporary preferences and human evaluation.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R04 · foundry-cost

Source: [agent-profiles/foundry-cost.toml](../../../agent-profiles/foundry-cost.toml). Type: Subagent role configuration.

Cost and performance auditor.

- **Purpose:** Reduce context, agents, retries, unnecessary media processing and test duplication; measure real costs, never sacrifice hard gates.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** `gpt-6-luna` / `medium`

### R05 · foundry-integrations

Source: [agent-profiles/foundry-integrations.toml](../../../agent-profiles/foundry-integrations.toml). Type: Subagent role configuration.

External tools, provider contracts and permission specialist.

- **Purpose:** Verify provider APIs, auth scopes, failure modes, actual receipts, retries, quotas and cost. Never treat an API stub as a working integration.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R06 · foundry-judge

Source: [agent-profiles/foundry-judge.toml](../../../agent-profiles/foundry-judge.toml). Type: Subagent role configuration.

Independent evidence and release judge.

- **Purpose:** Separate hypothesis, code inspection, isolated test, integration, provider observation and human feedback. Reject unknown hard gates and fabricated completion.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R07 · foundry-platform

Source: [agent-profiles/foundry-platform.toml](../../../agent-profiles/foundry-platform.toml). Type: Subagent role configuration.

Telegram/Discord/Slack platform UX and API specialist.

- **Purpose:** Check platform-specific callback/interaction semantics, permissions, message formatting, rate limits, transport receipts, group roles and device behavior.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R08 · foundry-privacy

Source: [agent-profiles/foundry-privacy.toml](../../../agent-profiles/foundry-privacy.toml). Type: Subagent role configuration.

Security, privacy and adversarial access reviewer.

- **Purpose:** Threat-model data scopes, consent, secrets, prompt injection, forget, revoke, restore, logging and cross-user leakage. Return exploit scenarios or honest unknowns.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R09 · foundry-product

Source: [agent-profiles/foundry-product.toml](../../../agent-profiles/foundry-product.toml). Type: Subagent role configuration.

Product discovery and user-value lead.

- **Purpose:** Define audience, concrete value, JTBD, user journeys, non-goals, success metrics, ethical boundaries and acceptance; challenge decorative features.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R10 · foundry-qa

Source: [agent-profiles/foundry-qa.toml](../../../agent-profiles/foundry-qa.toml). Type: Subagent role configuration.

Independent quality assurance lead.

- **Purpose:** Independently review frozen contract and diff. Produce positive, negative, race, stale, wrong-actor, duplicate, cancel, restart, privacy tests with actual evidence.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R11 · foundry-reliability

Source: [agent-profiles/foundry-reliability.toml](../../../agent-profiles/foundry-reliability.toml). Type: Subagent role configuration.

Reliability and operations specialist.

- **Purpose:** Design bounded queues, retries, recovery, cancellation, timeouts, health, metrics, backup/restore and deploy safety.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.

### R12 · foundry-skeptic

Source: [agent-profiles/foundry-skeptic.toml](../../../agent-profiles/foundry-skeptic.toml). Type: Subagent role configuration.

Independent skeptic and design challenger.

- **Purpose:** Find the strongest concrete counterexamples and alternative explanations; focus on correctness, user burden, hidden cost and regression.
- **Use when / activation:** The parent selects this competence when its concrete deliverable or independent review is needed; a supported host must actually launch the assigned actor.
- **Input → result:** Assigned raw task, exact sources/contracts and owned scope → the domain output described above, negative scenarios, actual evidence, uncertainties and handoff.
- **Evidence and limits:** A role profile is instructions, not a standalone skill, separate sandbox, licensed human expert or proof a review occurred. Its instructions prohibit secrets/private chats and production/publication/deployment/paid/irreversible external effects.
- **Model setting:** Inherits parent/host model and effort; no fixed override.


## H · Helpers, controllers and shared contracts

Read actual --help before commands. Relative scripts belong to the skill source that was actually read. Logical groups below explain controls; copies in self-contained skills are not extra capabilities or independent reviews. Fixtures are tests, not executed user work.

### H01 · Foundry native controller

Source: [kit/skills/agent-foundry/scripts/foundry.py](../../../kit/skills/agent-foundry/scripts/foundry.py). Type: Executable local state controller/checks.

- **Purpose:** Manage local approval subjects, coverage and workflow state.
- **Use when / activation:** A supported native operation; inspect actual --help first.
- **Input → result:** Current session and exact record → validated local state/receipt under native locks and gates.
- **Evidence and limits:** No model or external executor; stored approval needs actual user authority.

### H02 · Packaging and project installation

Source: [kit/skills/agent-foundry/scripts/package_agent.py](../../../kit/skills/agent-foundry/scripts/package_agent.py), [kit/skills/agent-foundry/scripts/install_agent.py](../../../kit/skills/agent-foundry/scripts/install_agent.py). Type: Executable filesystem/package tool.

- **Purpose:** Package authored agent content and install a declared set into one project.
- **Use when / activation:** A reviewed delivery/install task with exact build gate and target.
- **Input → result:** Authored source/manifest → delivery kit; reviewed kit/project → managed files/receipts.
- **Evidence and limits:** No expert-content generation, registration, upload/deploy or product-state migration. Same-user ancestor replacement is outside its security boundary.

### H03 · Core suite updater

Source: [kit/skills/agent-foundry/scripts/update_skill_suite.py](../../../kit/skills/agent-foundry/scripts/update_skill_suite.py). Type: Executable filesystem/package tool.

- **Purpose:** Audit, plan, apply, verify and roll back the exact33-core personal suite.
- **Use when / activation:** Reviewed install/update with actual ownership/journal and preservation checks.
- **Input → result:** Candidate and installed tree → plan/diff, before-copy, managed update/verification or qualified rollback.
- **Evidence and limits:** Does not manage optional sources, plugins, model defaults, AGENTS.md or product data. Files are not host discovery.

### H04 · App ledger and checks

Source: [kit/skills/app-atelier-director/scripts/state.py](../../../kit/skills/app-atelier-director/scripts/state.py), [kit/skills/app-atelier-director/scripts/check_model.py](../../../kit/skills/app-atelier-director/scripts/check_model.py), [kit/skills/app-atelier-director/scripts/doctor.py](../../../kit/skills/app-atelier-director/scripts/doctor.py). Type: Executable local state controller/checks.

- **Purpose:** Record App requirements, decisions, work/effects, authority and evidence; inspect consistency.
- **Use when / activation:** An applicable App native state/check operation and accepted profile.
- **Input → result:** Profile/state and typed records → ledger, status/coverage and consistency findings.
- **Evidence and limits:** No remote/model execution, UI rendering, support runtime or market proof.

### H05 · ChatBot round/team/domain checks

Source: [kit/skills/chatbot-atelier-director/scripts/teamctl.py](../../../kit/skills/chatbot-atelier-director/scripts/teamctl.py), [kit/skills/chatbot-atelier-director/scripts/team_policy.py](../../../kit/skills/chatbot-atelier-director/scripts/team_policy.py), [kit/skills/chatbot-atelier-director/scripts/check_round.py](../../../kit/skills/chatbot-atelier-director/scripts/check_round.py), [kit/skills/chatbot-atelier-director/scripts/check_chat_contract.py](../../../kit/skills/chatbot-atelier-director/scripts/check_chat_contract.py), [kit/skills/chatbot-atelier-director/scripts/check_platform_adapter.py](../../../kit/skills/chatbot-atelier-director/scripts/check_platform_adapter.py). Type: Executable structural helper.

- **Purpose:** Plan/freeze rounds and validate declared bot/domain/platform records.
- **Use when / activation:** A gate applicable to current chatbot.round/1 and native contracts.
- **Input → result:** Requirements, team plan, hashes and fixtures → structural errors/validity and frozen round metadata.
- **Evidence and limits:** Does not execute roles, authenticate consent or prove natural conversation/provider delivery.

### H06 · Game state/model/production/build checks

Source: [kit/skills/gamedev-director/scripts/atelier.py](../../../kit/skills/gamedev-director/scripts/atelier.py), [kit/skills/gamedev-director/scripts/game_model.py](../../../kit/skills/gamedev-director/scripts/game_model.py), [kit/skills/gamedev-director/scripts/pipeline.py](../../../kit/skills/gamedev-director/scripts/pipeline.py), [kit/skills/gamedev-director/scripts/production_contract.py](../../../kit/skills/gamedev-director/scripts/production_contract.py), [kit/skills/gamedev-director/scripts/check_build_receipts.py](../../../kit/skills/gamedev-director/scripts/check_build_receipts.py), [kit/skills/gamedev-director/scripts/concept_gate.py](../../../kit/skills/gamedev-director/scripts/concept_gate.py). Type: Executable local state controller/checks.

- **Purpose:** Maintain workflow/handoff and check model, production, concepts and exact build receipts.
- **Use when / activation:** Applicable concept/slice/release gate; preserve model4/handoff1/runtime2 and read actual help.
- **Input → result:** Model/state and linked files/receipts → consistency, coverage, impact and workflow records.
- **Evidence and limits:** No engine execution, model/API generation, signing/device performance, fun or retention certification.

### H07 · Context and adaptive task helpers

Source: [kit/skills/agent-foundry/scripts/context_capsule.py](../../../kit/skills/agent-foundry/scripts/context_capsule.py), [kit/skills/agent-foundry/scripts/adaptive_work.py](../../../kit/skills/agent-foundry/scripts/adaptive_work.py), [kit/skills/agent-foundry/scripts/verify_depth.py](../../../kit/skills/agent-foundry/scripts/verify_depth.py). Type: Executable structural helper.

- **Purpose:** Compile declared task context and check dependency/depth/adaptive-work structure.
- **Use when / activation:** Material direct/delegated/resumed work; load only the applicable profile.
- **Input → result:** Native requirements/decisions/identity/authority and input pins → derived capsule/checks for a named consumer.
- **Evidence and limits:** No new permission, replacement native truth, job execution or quality certificate. Skill-local copies are self-contained.

### H08 · Briefing, status and identity helpers

Source: [kit/skills/agent-foundry/scripts/briefing.py](../../../kit/skills/agent-foundry/scripts/briefing.py), [kit/skills/agent-foundry/scripts/interaction.py](../../../kit/skills/agent-foundry/scripts/interaction.py), [kit/skills/agent-foundry/scripts/visual_identity.py](../../../kit/skills/agent-foundry/scripts/visual_identity.py). Type: Executable local state controller/checks.

- **Purpose:** Bind briefing/script/decision files, show recorded status and freeze/check icon identity.
- **Use when / activation:** A material briefing, status/continuation question or identity-preserving update.
- **Input → result:** Exact records or existing icons → bound records, read-only views and identity checks; SVG creation only when absent.
- **Evidence and limits:** No interview/consent authentication, paused-job resume, craft certification, UI installation or monitoring.

### H09 · Discovery, proposal, inheritance and routing checks

Source: [kit/skills/agent-foundry/scripts/discover_specialists.py](../../../kit/skills/agent-foundry/scripts/discover_specialists.py), [kit/skills/agent-foundry/scripts/check_generated_inheritance.py](../../../kit/skills/agent-foundry/scripts/check_generated_inheritance.py), [kit/skills/agent-foundry/scripts/check_component_handoff.py](../../../kit/skills/agent-foundry/scripts/check_component_handoff.py), [optional-skills/atelier-orchestrator/scripts/check_routing.py](../../../optional-skills/atelier-orchestrator/scripts/check_routing.py), [kit/skills/design-specialist-skills/scripts/blueprint.py](../../../kit/skills/design-specialist-skills/scripts/blueprint.py). Type: Executable structural helper.

- **Purpose:** Inventory specialist sources and check proposal/inheritance/handoff/routing records.
- **Use when / activation:** Source-backed reuse, construction, component handoff or a material route.
- **Input → result:** Source metadata, requirement IDs and exact blueprint/route → inventory and declared completeness/conflict findings.
- **Evidence and limits:** Metadata match is not semantic competence, invocation, approval authentication or execution.

### H10 · Shared production and tool contracts

Source: [standards/production-quality.md](../../../standards/production-quality.md), [standards/production-profiles.json](../../../standards/production-profiles.json), [standards/context-capsule.md](../../../standards/context-capsule.md), [kit/skills/agent-foundry/references/tool-compatibility.md](../../../kit/skills/agent-foundry/references/tool-compatibility.md), [kit/skills/gamedev-director/references/v4/production.md](../../../kit/skills/gamedev-director/references/v4/production.md), [kit/skills/chatbot-atelier-media/references/production-recipes.md](../../../kit/skills/chatbot-atelier-media/references/production-recipes.md). Type: Instructions executed by the current AI host.

- **Purpose:** Preserve references/masters and select operation-specific production, rights, transformation and acceptance.
- **Use when / activation:** Any material artifact; select actual medium/consumer before batching.
- **Input → result:** Task/reference/medium/tool schema → representative slice, recipes, lineage, actual playback/import/assembly requirements and distinct gates.
- **Evidence and limits:** Contracts are not installed DCC/renderer/media models or proof of sensory quality; missing must capability is blocked, not N/A.

### H11 · Repository materialization, packaging and validation

Source: [scripts/materialize_standards.py](../../../scripts/materialize_standards.py), [scripts/refresh_kit_manifest.py](../../../scripts/refresh_kit_manifest.py), [scripts/build_packages.py](../../../scripts/build_packages.py), [scripts/check_repository.py](../../../scripts/check_repository.py), [kit/verify_release.py](../../../kit/verify_release.py), [scripts/install_host_profile.py](../../../scripts/install_host_profile.py). Type: Executable filesystem/package tool.

- **Purpose:** Synchronize reviewed common copies, compute manifests, build/check distribution and install a selected host profile.
- **Use when / activation:** A scoped repository release/check or explicit host-profile installation.
- **Input → result:** Reviewed sources/requirements/identity baseline → materialized copies, hashes, archives/checks or managed host profile.
- **Evidence and limits:** Integrity PASS is not remote publication, host discovery, unchanged products or all future output quality.


## S · Agent Atelier0.2.0: local runtime and control

These groups describe executable workbench components, not proof a checkout is running. They share the actual API and durable command model. The personal Mac release is not a multi-user/team authorization service.

### S01 · Mac launcher and instance ownership · 0.2.0

Source: [apps/agent-atelier/launcher/atelier.mjs](../../../apps/agent-atelier/launcher/atelier.mjs), [apps/agent-atelier/launcher/Agent Atelier.command](../../../apps/agent-atelier/launcher/Agent%20Atelier.command), [apps/agent-atelier/server/instance.mjs](../../../apps/agent-atelier/server/instance.mjs). Type: Local service runtime/control.

- **Purpose:** Start/open, inspect and stop the personal loopback instance.
- **Use when / activation:** After pinned dependency install/build: start, status, doctor or stop; optional --no-open/--port/--data-dir.
- **Input → result:** Built local sources and explicit instance directory → verified listener, one-use60-second owner link, browser or conflict/status result.
- **Evidence and limits:** Does not enable login auto-start. Same-OS-owner credential readers are within the local trust boundary.

### S02 · HTTP API and owner session · 0.2.0

Source: [apps/agent-atelier/server/index.mjs](../../../apps/agent-atelier/server/index.mjs), [apps/agent-atelier/server/session.mjs](../../../apps/agent-atelier/server/session.mjs), [apps/agent-atelier/shared/API.md](../../../apps/agent-atelier/shared/API.md), [apps/agent-atelier/shared/contracts.mjs](../../../apps/agent-atelier/shared/contracts.mjs), [apps/agent-atelier/client/src/api.ts](../../../apps/agent-atelier/client/src/api.ts). Type: Local service runtime/control.

- **Purpose:** Serve the UI/API and authenticate local owner commands.
- **Use when / activation:** Launcher claim; supported /api/v1 reads or durable POST commands.
- **Input → result:** Verified launch token → HttpOnly SameSite session/CSRF; exact command_id+input → durable response.
- **Evidence and limits:** Static page/plain URL grants no control session. No external CORS; a command receipt is not proof its long-running job succeeded.

### S03 · Service-owned store and receipts · 0.2.0

Source: [apps/agent-atelier/server/store.mjs](../../../apps/agent-atelier/server/store.mjs), [apps/agent-atelier/server/utils.mjs](../../../apps/agent-atelier/server/utils.mjs). Type: Local service runtime/control.

- **Purpose:** Persist service projects, tasks, jobs, commands, evidence and event ordering.
- **Use when / activation:** Normal service operations and actual database migrations/transactions.
- **Input → result:** Validated commands/native observations → service-owned SQLite records, monotonic events and durable receipts.
- **Evidence and limits:** This database is not the native product source of truth or a private Codex database. Known redaction patterns do not detect every arbitrary secret.

### S04 · Project preview, binding and source views · 0.2.0

Source: [apps/agent-atelier/server/projects.mjs](../../../apps/agent-atelier/server/projects.mjs). Type: Local service runtime/control.

- **Purpose:** Inspect an exact project and expose bounded source/context/identity/artifact/diff views.
- **Use when / activation:** project.preview → project.bind; explicit profile/source_refs and refresh.
- **Input → result:** Reviewed folder and known native records → binding, revision pins, requirements/decisions/readiness, source hashes and safe media/diff views.
- **Evidence and limits:** No Home scan or product migration. Unsupported schemas remain warnings; title/Markdown claims are not authenticated owner acceptance.

### S05 · Native Codex portfolio and work map · 0.2.0

Source: [apps/agent-atelier/server/portfolio.mjs](../../../apps/agent-atelier/server/portfolio.mjs), [apps/agent-atelier/server/codex.mjs](../../../apps/agent-atelier/server/codex.mjs). Type: Local service runtime/control.

- **Purpose:** Discover native work and group actual outcomes by canonical project rather than show only chat titles.
- **Use when / activation:** portfolio.refresh; on-demand project/work-group history and bounded pagination.
- **Input → result:** Public read-only app-server history → active/archived project groups, source-backed turns/outcomes, goal/agent status, next-action proposals and coverage gaps.
- **Evidence and limits:** Read transport rejects mutation/model execution. Empty projects without threads are invisible; unavailable pages remain incomplete coverage. Discovery does not authorize safe chat continuation.

### S06 · Universal route proposal · 0.2.0

Source: [apps/agent-atelier/server/routing.mjs](../../../apps/agent-atelier/server/routing.mjs). Type: Local service runtime/control.

- **Purpose:** Store a source-backed route proposal while the actual orchestrator makes the semantic choice.
- **Use when / activation:** task.route; universal_entry preparation with reviewed route pins.
- **Input → result:** Objective, current project/agent sources and creation/maintenance scope → direct/specialist/project_agent/director/compose/create_agent/maintain_system/bridge proposal.
- **Evidence and limits:** A route is not invocation or consent. No keyword classifier is advertised as expert reasoning; ambiguous sources require a choice.

### S07 · Context, instructions and source snapshots · 0.2.0

Source: [apps/agent-atelier/server/context.mjs](../../../apps/agent-atelier/server/context.mjs), [apps/agent-atelier/server/instructions.mjs](../../../apps/agent-atelier/server/instructions.mjs). Type: Local service runtime/control.

- **Purpose:** Prepare exact governing instructions, native must/dependency closure and verified selected-skill snapshots.
- **Use when / activation:** task.prepare; current instruction/source rechecks before dispatch.
- **Input → result:** Objective/acceptance/scope, native sources and up to4 selected skills → bounded capsule with hashes, source set, aliases and capability constraints.
- **Evidence and limits:** Changed pins or unsupported source loading block/reprepare; snapshots are read grants, not global installation or permission expansion.

### S08 · Codex execution adapter and permission profile · 0.2.0

Source: [apps/agent-atelier/server/codex.mjs](../../../apps/agent-atelier/server/codex.mjs), [apps/agent-atelier/server/permissions.mjs](../../../apps/agent-atelier/server/permissions.mjs), [apps/agent-atelier/server/environment.mjs](../../../apps/agent-atelier/server/environment.mjs). Type: Local service runtime/control.

- **Purpose:** Run a bounded real model turn through the supported public app-server with isolated executor state.
- **Use when / activation:** codex.connect/skills and explicit task.dispatch after supported existing ChatGPT access and exact task checks.
- **Input → result:** Prepared task, verified skills and limits → actual thread/turn/tool requests, outputs and terminal/unknown receipts.
- **Evidence and limits:** Default denies ambient MCP/apps/shell network/web and unrelated/private roots. Explicit public-web read is narrower than arbitrary APIs. Custom providers/billing and unavailable tools need reviewed routes.

### S09 · Task/job lifecycle and chat handoff · 0.2.0

Source: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/shared/contracts.mjs](../../../apps/agent-atelier/shared/contracts.mjs). Type: Local service runtime/control.

- **Purpose:** Coordinate prepare/dispatch/continue/pause/interrupt/reconcile and owner review with writer reservations.
- **Use when / activation:** Task/job commands; exact idle thread.preview/adopt for existing chats.
- **Input → result:** Approved bounded task and source revision → correlated running/terminal/unknown states, outputs, durable events and owner review.
- **Evidence and limits:** Interrupt is pending until terminal evidence. Unknown outcome is not replayed. Independent desktop writers are not fenced; model completion/owner review is not product acceptance/independent QA.

### S10 · Source-pinned native Foundry operations · 0.2.0

Source: [apps/agent-atelier/server/controllers.mjs](../../../apps/agent-atelier/server/controllers.mjs), [apps/agent-atelier/server/foundry_cas.py](../../../apps/agent-atelier/server/foundry_cas.py). Type: Local service runtime/control.

- **Purpose:** Preview and apply a fixed native controller catalog without broad model write permissions.
- **Use when / activation:** controller.preview/apply; receipt-specific reconcile after unknown outcomes.
- **Input → result:** Exact trusted source closure, current state and input hashes → reviewed argv/authority subject, native locked validation/write and actual receipt.
- **Evidence and limits:** No model/provider/deploy/product runtime. Reconciliation observes state and revokes delayed invocation only under the reviewed lease; it does not replay or certify the original result.

### S11 · Core skills discovery and update UI · 0.2.0

Source: [apps/agent-atelier/server/skills.mjs](../../../apps/agent-atelier/server/skills.mjs). Type: Local service runtime/control.

- **Purpose:** Inspect canonical/installed/discovered sources and expose native33-core updater operations.
- **Use when / activation:** skills audit/update-plan/diff/apply/verify/rollback; codex.skills refresh after installation.
- **Input → result:** Exact candidate/installed source and journal → source/diff/plan, managed update receipts and verified rollback conditions.
- **Evidence and limits:** One global writer; unknown customization is a conflict. Installed files and host discovery/use are separate; WORK has no implied control route.

### S12 · Optional-source maintenance · 0.2.0

Source: [apps/agent-atelier/server/optional_updates.mjs](../../../apps/agent-atelier/server/optional_updates.mjs). Type: Local service runtime/control.

- **Purpose:** Manage only the declared optional orchestrator and maintenance sources with full-tree preservation.
- **Use when / activation:** skills.optional-preview/apply/verify/rollback with exact preview/journal hashes.
- **Input → result:** Known canonical source and exact installed predecessor → reviewed changes, owned staging/before-copy, apply/verify/qualified rollback.
- **Evidence and limits:** Unknown local edits/icon/policy drift block overwrite. Unknown outcomes block shared-skill dispatch until reconciled; installed files still need discovery refresh.

### S13 · Service backup, restore and update boundary · 0.2.0

Source: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/server/store.mjs](../../../apps/agent-atelier/server/store.mjs), [apps/agent-atelier/README.md](../../../apps/agent-atelier/README.md). Type: Local service runtime/control.

- **Purpose:** Create exact service backups and preview controlled restore/update.
- **Use when / activation:** service.backup/restore-preview/restore at an idle/reconciled boundary.
- **Input → result:** Current service-owned records and approved backup digest → backup/restore receipts with newer durable receipts retained and old dispatch authority invalidated.
- **Evidence and limits:** Does not restore native project files/databases, external effects or independent chats. Test restore on an isolated instance.

### S14 · Retention, forgetting and cleanup · 0.2.0

Source: [apps/agent-atelier/server/retention.mjs](../../../apps/agent-atelier/server/retention.mjs), [apps/agent-atelier/client/src/privacy.tsx](../../../apps/agent-atelier/client/src/privacy.tsx). Type: Local service runtime/control.

- **Purpose:** Preview/apply service-local retention and cleanup with tombstones and resumable file cleanup.
- **Use when / activation:** service.retention; cleanup-preview/apply/resume with current digest and idle/reconciled work.
- **Input → result:** Reviewed policy or forget IDs → exact scope/counts, private cleanup receipt, logical invalidation and preserved recovery boundaries.
- **Evidence and limits:** No automatic TTL is claimed. Does not delete native/provider data or guarantee secure physical erasure; newest two retained backups remain protected by policy.

### S15 · Adaptive multilingual workbench · 0.2.0

Source: [apps/agent-atelier/client/src/App.tsx](../../../apps/agent-atelier/client/src/App.tsx), [apps/agent-atelier/client/src/views.tsx](../../../apps/agent-atelier/client/src/views.tsx), [apps/agent-atelier/client/src/dialogs.tsx](../../../apps/agent-atelier/client/src/dialogs.tsx), [apps/agent-atelier/client/src/profiles.ts](../../../apps/agent-atelier/client/src/profiles.ts), [apps/agent-atelier/client/src/i18n.ts](../../../apps/agent-atelier/client/src/i18n.ts), [apps/agent-atelier/client/src/app.css](../../../apps/agent-atelier/client/src/app.css), [apps/agent-atelier/client/src/demo.ts](../../../apps/agent-atelier/client/src/demo.ts). Type: Local service runtime/control.

- **Purpose:** Present portfolio, task/source/diff/outcome panes, evidence, updates and recovery for the selected project profile.
- **Use when / activation:** Open the live owner session; choose language and app/bot/game/agent/research/document/mixed/generic view.
- **Input → result:** Actual API state → usable project/work navigation, inspection, reviewable commands and localized operational status.
- **Evidence and limits:** Seven locales are existing runtime catalogs, not proof of perfect linguistic/craft quality. ?demo=1 is fictional and executes no real commands. Presentation profile does not mutate native product state.

### S16 · Orchestrator loopback client · 0.2.0

Source: [optional-skills/atelier-orchestrator/scripts/atelier_client.py](../../../optional-skills/atelier-orchestrator/scripts/atelier_client.py). Type: Local service runtime/control.

- **Purpose:** Let the orchestration skill use supported service operations from the current host.
- **Use when / activation:** Read --help, then status/doctor; prepare/dispatch/interrupt only for an available instance and current scope.
- **Input → result:** Fresh local session/CSRF and persisted command identity → bounded correlated HTTP command/status receipts.
- **Evidence and limits:** Loopback only; no credential searching or implicit authority. If the service is absent, continue supported native work or give an exact bridge.

### S17 · Reviewed diagnostic export · 0.2.0

Source: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/shared/API.md](../../../apps/agent-atelier/shared/API.md). Type: Local service runtime/control.

- **Purpose:** Prepare an aggregate service diagnostic without transmitting private project content.
- **Use when / activation:** service.diagnostic-preview then diagnostic-export with the reviewed digest.
- **Input → result:** Current aggregate counts/capabilities → reviewable sanitized JSON and approved private local export.
- **Evidence and limits:** Omits project paths, task text, account/chat IDs, source/output and credentials; export is local, not external transmission or universal secret detection.


## Current deficiencies: present in the baseline, not silently fixed

These are source-inspection findings. The remedies are **proposed**, not implemented by this documentation.

- **App platforms conflict.** [build:61](../../../kit/skills/app-atelier-build/SKILL.md#L61) uses the accepted platform set; [build:118](../../../kit/skills/app-atelier-build/SKILL.md#L118) unconditionally asks for Android+iOS+web. [release:47](../../../kit/skills/app-atelier-release/SKILL.md#L47) and [qa:87](../../../kit/skills/app-atelier-qa/SKILL.md#L87) repeat three-client expectations. Proposed remedy: derive applicability consistently from the accepted profile; retain existing three-client obligations.
- **App research conflict.** [build:63](../../../kit/skills/app-atelier-build/SKILL.md#L63) permits profile-authorized research; [build:120](../../../kit/skills/app-atelier-build/SKILL.md#L120) bans all human tests/experiments. [research:55](../../../kit/skills/app-atelier-research/SKILL.md#L55) and [qa:109](../../../kit/skills/app-atelier-qa/SKILL.md#L109) already use profile conditions. Proposed remedy: remove historical-profile leakage from generic rules while retaining each existing restriction. Product use, owner review, passive observation and intentional recruited research are different activities.
- **Declared versus executed routes.** H01/H04/H05/H06 distinguish state/structural tools from external execution. Production methods are substantial, including Game3D/rig/audio recipes, but they are not an installed universal renderer/generator/device lab. Proposed remedy: operation-specific observed availability and actual consumer proof, preserving existing methods.
- **Medium specificity.** [production-profiles.json:125](../../../standards/production-profiles.json#L125) combines vector and3D. Game references already detail mesh/rig/source/export/import; ChatBot media already requires playback/freeze/readback. Proposed remedy: reuse these abstractions with distinct medium profiles and downstream checks, without a second native product model.
- **New domain claims require cases.** This catalogue does not certify an already-delivered business predictor, LoRA training route, production collector or every-platform game. Current methods can guide implementation; each new route needs actual data/access/toolchain, representative end-to-end output, appropriate evaluation and operating evidence.

## First useful local-service task

From the repository root, after selecting the reviewed baseline and checking prerequisites:

```sh
cd apps/agent-atelier
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

The source baseline declares Node>=24.22.2<27 and a pinned lockfile; that is compatibility metadata, not an evergreen platform recommendation. On Mac, built launcher/Agent Atelier.command also opens the workbench. Stop with node launcher/atelier.mjs stop. No login auto-start is implied. Preserve the separate private service data directory and actual backups; keep them outside this reusable repository.

Use: refresh native portfolio → inspect exact project/work/goal provenance → preview and bind the intended folder → enter objective and acceptance → review route/capsule/scope → explicit dispatch → inspect real outputs → scoped review/next action. Observed skill mention, verified installed source, host discovery, running turn and accepted result have different statuses. Inaccessible/empty history is incomplete discovery, not proof no work exists.

A project presentation profile changes the view, not product truth. Source-only goals stay declared; accepted goals require matching observed native approval and pinned authority. Existing-chat continuation requires exact identity/cwd, idle handoff and restorable context. Otherwise use the native chat or prepare a fresh reviewed task. The panel cannot fence an unrelated desktop writer.

See [actual API payloads/limits](../../../apps/agent-atelier/shared/API.md) and [service operations](../../../apps/agent-atelier/README.md). A confirmed command is not a blanket future spending/publication grant. WORK live audit/control stays deferred until supported host access returns.

## Preservation and updating

This catalogue changes documentation only: no native schema adoption, installed skill, model default, icon, binding, account, product or running instance changes. For real updates use [the1.3.0 adoption record](../../../releases/migrations/repository-1.3.0.md). Preserve stable names, accepted originals/persona, UI settings, native state/IDs, requirements/decisions, permissions and unknown effects. Installation, generated-agent adoption, host discovery, execution and owner acceptance are separate steps. Qualified rollback uses actual unchanged-target before-copies/journals; source rollback cannot undo external effects.

## Verification and limits

[current-components.json](current-components.json) contains complete EN/UK card text, counts and SHA-256 source pins. The35 names were compared with the33-core release list plus two declared optional sources;12 TOMLs and all linked sources were compared with8951398. Groups cover instructions, helpers/controllers and local runtime/control; some share implementation files.

Review used actual entrypoints and relevant source/reference sections. It did not execute every support file, live host/device/media/provider operation or private product. Historical [core6.0 evidence](../../../governance/RELEASE_6_VERIFICATION.json) and [repository1.3 evidence](../../../governance/UNIVERSAL_ENTRY_1_3_VERIFICATION.json) have their own scope. Their counts do not prove new bytes, platforms, future craft quality or current host health. No new live proof is fabricated here.
