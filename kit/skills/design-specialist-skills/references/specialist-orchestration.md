# Discover specialists and coordinate a shared product

## Discover existing methods

Before creating a reusable agent or skill or making a material extension, discover current specialists through available skill metadata and approved local sources. The examples below are starting points. Consider new specialists through the same process. Read the actual `SKILL.md` and relevant contracts and resources. Record the frontmatter slug, host and origin, actual version and hash, and hashes of consumed dependencies. Review source directly when a capability card is missing.

Compare capability, input, output, stages, compatibility, permissions, limits, and fit to the requirement IDs. Choose `reuse` for one suitable method, `compose` for several with explicit interfaces and owners, `extend` for uncovered requirements on a useful existing base, or `create_gap` after evidence-backed discovery finds no fit. Resolve unread, ambiguous, stale, and unknown candidates before treating them as evidence of a gap. A suitable but unavailable specialist is a blocker or a candidate for a handoff to a capable host. Apply these rules in every child using the [inheritance contract](inheritance-contract.md).

Track archived and uninstalled sources separately from active installations. Disambiguate multiple active sources for a stable slug and establish exact version and scope. Record `available`, `installed`, `source_checked`, and actual invocation separately. Verify counterparts on each host. After moving from Work to Codex or vice versa, resolve and inspect the actual source again. Stable selectors are `@<frontmatter-name>` in Work and `$<frontmatter-name>` in Codex, without a display version. Confirm permissions, budget, and effect scope independently of reuse.

Give a new specialist a bounded project task or handoff. Include parent intent and authority, requirement IDs, scope and stop, actual inputs and hashes, owned paths, outputs and consumer interfaces, acceptance, budget and allowed effects, unresolved work and checkpoint, next action, and `return_to`. To change `planned` to `performed`, record the actual actor, source snapshot, and operation or output receipt. `atelier-component-handoff/1` supports the typed `agent_skill`, `app`, and `chatbot` routes. A new family defines acceptance for its own domain. Bundle required discovery and briefing materials and helpers locally in each child.

## One product intent and accountable owners

Agent Foundry recovers the problem, need for an agent, product components, requirements, decisions, current state, and scope of authority. The installation of a component skill has no effect on product scope. Start from the supplied plan, idea, or repository and reconcile actual sources. Keep uncertain components as proposals with their rationale and selection condition.

Keep accepted intent and authority in a single project-owned source. A component handoff is its portable view. Each component owns its outputs, consumer and evidence. Assign a named owner to shared decisions and contracts. Reconcile requirements across the Ateliers against the same project source.

## Select the relevant skill

| Intent | Stable ID | Application |
|---|---|---|
| Produce or rebuild a reusable specialist skill or family | `design-specialist-skills` | Turn accepted competences and child contracts into domain workflows, methods, templates, and verification. Use only when a reusable specialist is needed. |
| The product includes an application | `app-atelier-director` | Own the accepted app scope and required stages. Execute product changes only within their authority. |
| The product includes a chatbot | `chatbot-atelier-director` | Own applicable bot stages. Establish selected channels, audience, and real constraints. |

Skill Creator performs supported initialization, validation, and saving of personal skills. The specialized skill constructor defines domain methods, team design, and acceptance. A code- or config-only agent can use its own production method. Use a direct method for a simple one-off repair when it suffices.

In Work select `@design-specialist-skills`, `@app-atelier-director`, or `@chatbot-atelier-director` and check frontmatter when the picker shows display names. In Codex use `$design-specialist-skills`, `$app-atelier-director`, or `$chatbot-atelier-director`. Resolve the installed revision from actual host metadata, read the source, and record its version, hash, and scope. Use the stable ID in calls.

A bounded known stage can be selected directly with `@chatbot-atelier-integrations` or `$chatbot-atelier-integrations`, for example, or `@app-atelier-support` or `$app-atelier-support`. Record the actual stage used and carry forward the accepted product baseline. The [route catalogue](../assets/specialist-routes.json) lists current stable stage IDs. Confirm installation from skills and files on the active host and read the selected entry before use. Resolve again after a host change.

## Delegate using the accepted passport

After passport approval, Foundry sends the exact scope, criteria and child contracts, sources, known decisions, outputs, permissions, and acceptance to the specialized skill constructor. Reconcile against the underlying task, fill only methodological gaps, and build the artifacts. Reuse unchanged discovery, passport, and approval. Return a material capability, external effect, or cost to the integrator as an exact change with its authority consequences.

If the constructor is unavailable, use an equivalent local method from the bundled domain, inheritance, and production contracts and Skill Creator where suitable. Record `embedded_method`, actual actor, and acceptance. If a suitable method or tool is unavailable, prepare a precise handoff and continue independent work.

Required app or chatbot scope stays blocked until a capable specialist or an explicitly chosen and verified domain alternative is available. Send the actual package to the capable environment. Unavailable tools remain a blocker, with N/A reserved for requirements excluded by the accepted design.

## Coordinate an application and chatbot

An app and bot can operate on one order. The parent owner defines identity, access and tenant scope, IDs, transitions, APIs and events, idempotency, version, privacy and retention and deletion, deep links, and common copy. The app owner handles its complete journey. The bot owner handles the selected channel, platform adapter, conversation, actions, and delivery. Keep one order status, balance, and consent authority where shared.

Give components the same shared contract ID and hash, named owner, and `component_ids`. Specify actual source-to-consumer reads, writes, events, and failures. Open both affected workstreams for a contract change and agree the revision before integration. A localized UI copy change reaches server logic only if it changes or depends on a shared contract.

A support bot can be a bounded app support component using an accepted product baseline. A standalone bot journey, catalogue, and ongoing operation needs a separate component scope and acceptance.

## Prepare and receive the component handoff

Use `assets/component-handoff.template.json` with `atelier-component-handoff/1`. Include product and component IDs, parent intent and authority, inherited and owned requirements, scope and stop, permissions and budget, accepted decisions, actual capabilities, inputs and hashes, shared contract references and owners and consumers, deliverables and acceptance, actual jobs and evidence, unresolved items, checkpoint, and next action. `return_to` contains the stable parent selector and component ID. `orchestrator_chain` records actual ownership. Its final selector is `invocation.selector` and the previous selector is `return_to.selector`. Use stable slugs without display versions.

For a bot, distinguish `proposed_channels` and `selected_channels`. An unchosen channel is an open decision. `platform_adapter_contract_refs` points to included contract IDs. These arrays may be empty for another component type.

`invocation.status=planned` records proposed work. `performed` requires an actual actor, a resolved skill snapshot, and evidence receipts with actual bytes and hashes. Derive the snapshot ID from the first frontmatter, ignoring body examples such as `name:`. Each receipt's `actor` equals `invocation.actor`. The receipt also has the current `component_id` and nonempty `requirement_ids` from owned requirements. Use `claim/method/scope` to state what was established. Inspect the evidence for the claim's truth.

`invocation.activity` is separate from the skill name and grant. `planning` covers reading, analysis, research, and decision artifacts and is allowed by each of the three supported grants. `skill_construction` is reusable skill creation or modification for `agent_skill` and requires `construction_only`. `product_execution` is app or bot implementation and requires `component_execution`. Authorize any installation of new reusable personal skills separately from product execution. `performed`, embedded construction, and ready-to-receive scope must satisfy the grant matrix. A draft can explicitly propose unauthorized future work. Deployment, messaging, and service spending require corresponding authority.

`deliverables` always lists actual files with path and hash and is verified in every status. Describe future outputs under scope and acceptance. Each `open_questions` element contains `question`, boolean `blocking`, and `status=pending|resolved`. A resolved question requires `resolution_ref`. Reject invalid types or states and keep outstanding blocking questions out of ready status.

Run `python3 -B scripts/check_component_handoff.py HANDOFF.json --root PROJECT_DIR` and add `--ready` for a ready-to-receive package. It checks shape, references, file bytes and hashes, selectors, and declared activity scope. Check domain completeness, consent authority, and actual tool invocation separately. For production acceptance, verify required integration, human, and provider evidence.

A fresh receiver verifies sources, permission and versions, reproduces the expected scenario, and returns outputs and hashes, verdict, and limits. Return missing or stale input, incompatible rules, or a material change to `return_to` with exact requirement IDs. Preserve accepted originals and completed work. Update the same parent registry and checkpoint after each product stage.
