# Skill construction, app, and chatbot components in one product

Contents include route selection, stable selectors, delegation, shared contracts, and acceptance.

## One product intent and accountable owners

Agent Foundry recovers the problem, agent need, product composition, requirements, decisions, current state and permission scope. Add app or chatbot components only when the product requires them. Compare the actual input whether it arrives as an idea, accepted product plan, or current repository. Record unchosen components as proposals with their rationale and selection condition.

One project-owned source governs accepted intent and authority. Component handoffs project those records for consumers. Avoid conflicting copies of product requirements across families. Each component has a distinct owner, consumer, outputs and evidence. Name a single owner for shared decisions and contracts.

## Select a specialist

| Intent | Stable ID | Scope |
|---|---|---|
| Create or restructure a reusable specialist skill or family | `design-specialist-skills` | Converts accepted competencies and child contracts into domain workflows, methods, templates and verification. Use when the deliverable needs reusable skills. |
| Deliver the app component | `app-atelier-director` | Leads the accepted app scope and required stages. Product execution needs its own scope after agent generation. |
| Deliver the chatbot component | `chatbot-atelier-director` | Leads required bot stages after establishing selected channels, audience, and operational constraints. |

Skill Creator initializes, validates and maintains personal skill packages. The specialist skills constructor designs their domain methods, team and acceptance. A code or configuration agent may need neither a separate constructor nor a new reusable skill. A narrow correction can use the direct applicable method.

In Work use `@design-specialist-skills`, `@app-atelier-director`, or `@chatbot-atelier-director`. Where search uses display names, verify the selected record in its frontmatter. In Codex use `$design-specialist-skills`, `$app-atelier-director`, or `$chatbot-atelier-director`. Selectors remain stable across display and version changes. Read the current installed instructions, record the actual version, digest, and limitations, and keep version numbers out of invocation selectors.

For a known narrow stage use its stable selector, such as `@chatbot-atelier-integrations` / `$chatbot-atelier-integrations` or `@app-atelier-support` / `$app-atelier-support`. Record the stage actually performed and reuse the accepted product baseline. The [route catalog](../assets/specialist-routes.json) describes current stable IDs. Verify actual installation and readable source on the current host. Re-resolve after moving between Work and Codex.

## Delegate within current authority

After passport acceptance, pass the constructor exact scope, criteria and child contracts, sources, decisions, outputs, permissions and acceptance. The constructor verifies the task, fills only material method gaps, and produces skill artifacts. Reuse discovery, current passport and acceptance for unchanged scope. Return a new material capability, effect or expense to the integrator as an exact delta.

When the constructor is unavailable, an equivalent local method may use bundled domain, inheritance and production contracts and Skill Creator. Record `embedded_method`, actual actor and acceptance. Report unavailable skills as unavailable. If equivalent competence or tooling is also missing, prepare a handoff and continue independent work.

An unavailable required Atelier component remains blocked pending a qualified actor or a chosen and verified domain alternative. Prepare a transfer packet for a capable environment. An absent tool does not change product applicability.

## Define app and chatbot interfaces

For example, an app and chatbot can operate on one order. The parent owner governs identity, account and tenant scope, IDs, transitions, API and events, idempotency, versions, privacy, retention and deletion, deep links and shared wording. The app owner supplies a self-contained app journey. The chatbot owner supplies the chosen channel, platform adapter, conversation, actions and delivery. Use one authoritative balance, consent record and order status where shared.

Give both components the exact shared contract ID and hash, owner, and `component_ids`. Name each source-to-consumer read, write, event and failure. Open both dependent branches if a shared contract changes and agree its revision before integration. A local UI-only change opens only affected dependencies.

A product support bot may be a narrow component. Reuse the product baseline for a support adapter. Give a distinct full chatbot journey, catalog and operations their own scope and acceptance if required.

## Hand off a self-contained component

Use `assets/component-handoff.template.json` with `atelier-component-handoff/1`. Record product and component IDs, parent intent and authority, inherited and owned requirements, scope and stop, permissions and budget, decisions, actual capabilities, input files and digests, shared contracts and owners and consumers, deliverables and acceptance, actual jobs and evidence, unresolved issues, checkpoint and next action. `return_to` contains the stable parent selector and component ID. `orchestrator_chain` records actual responsibility. Its final selector equals `invocation.selector` and its penultimate selector equals `return_to.selector`. Keep selectors as stable slugs.

For bots, distinguish `proposed_channels` and `selected_channels`. Keep an unselected channel open until a decision. `platform_adapter_contract_refs` refer to included contract IDs. These arrays may be empty for a non-bot component.

`invocation.status=planned` records intent. `performed` requires an actual actor, resolved skill snapshot, and receipt with actual bytes and digest. Resolve snapshot identity from leading frontmatter only, ignoring example `name:` entries in the body. Each referenced receipt has `actor` equal to `invocation.actor`, the current `component_id`, and nonempty `requirement_ids` contained in owned requirements. Explain evidence with `claim/method/scope`. This establishes structural binding.

Keep `invocation.activity`, skill name, and grant distinct. `planning` covers read, analysis, research and decision artifacts under any of the three valid grants. `skill_construction` changes reusable skills for an `agent_skill` component and needs `construction_only`. `product_execution` builds or changes the app or bot and needs `component_execution`. Product execution does not itself authorize installation of personal skills. Match `performed`, embedded construction and ready-to-receive scope with this matrix. A draft can record an explicitly unauthorized proposal. Deploying, sending and spending each need applicable authority beyond an agent or skill grant.

`deliverables` contains actual existing files and hashes and is checked in every state. Describe planned outputs under scope and acceptance. Each `open_questions` item has `question`, Boolean `blocking`, and `status=pending|resolved`. Resolved questions need `resolution_ref`. Correct malformed questions and resolve blocking questions before a ready handoff.

Run `python3 -B scripts/check_component_handoff.py HANDOFF.json --root PROJECT_DIR` and use `--ready` for a ready-to-receive packet. The command checks shape, refs, actual files, hashes, selectors, and bounds of claimed execution. Separately verify domain sufficiency, actual authorization, and operation evidence. Component or production acceptance needs appropriate integration, human or provider proof where claimed.

The receiver reads the packet without needing chat history, verifies sources, rights and versions, reproduces the expected scenario, and returns outputs, hashes, verdict and limitations. Return missing or stale input, incompatible rules and material changes to `return_to` with affected requirement IDs. Preserve accepted originals and finished work. Update the same parent registry and checkpoint after every stage.
