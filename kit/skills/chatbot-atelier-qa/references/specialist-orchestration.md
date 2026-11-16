# Specialist skills, an app and a bot in one product

Choose the route, resolve stable selectors, assign work, bind shared contracts and verify the result.

## Shared intent and domain ownership

Agent Foundry recovers the problem, agent need, product components, requirements, decisions, current state and permission scope. Add app or chatbot work only when the product needs it. Inputs can be an agreed plan, early idea or current repository. Inspect available evidence first. Keep undecided components as proposals with their reason and choice criterion.

A project-owned source retains accepted intent and authority. Component handoff projects its records. Keep requirements consistent across ateliers. Name each component's owner, consumer, outputs and evidence and one owner for each shared decision and contract.

## Resolve the appropriate skill

| Intent | Stable selector | Use |
|---|---|---|
| Build or refactor a reusable specialist skill or family | `design-specialist-skills` | Turn accepted competence and child contracts into practical methods, templates and verification when required. |
| Product includes an app | `app-atelier-director` | Own the approved app scope and needed stages. Begin product changes only with the relevant authority. |
| Product includes a chatbot | `chatbot-atelier-director` | Cover the needed bot stages, starting with channel and audience and observed limits. |

Skill Creator initializes, validates and saves personal skills. The specialist constructor supplies domain design, team and criteria. An agent made only of code and configuration may need neither skill construction nor another workflow. Use a direct method for a contained repair.

In Work choose `@design-specialist-skills`, `@app-atelier-director` or `@chatbot-atelier-director` and verify frontmatter when searching by display label. In Codex use `$design-specialist-skills`, `$app-atelier-director` or `$chatbot-atelier-director`. A visible version label is separate from the machine selector. Resolve the current installed source and record observed version, hash and limits.

For a known stage, use its selector such as `@chatbot-atelier-integrations` or `$chatbot-atelier-integrations`, or `@app-atelier-support` or `$app-atelier-support`. Record which stage actually operated. Known product scope does not require a new life cycle. The catalog enumerates current stable stage IDs.

The [catalog](../assets/specialist-routes.json) describes candidates. Resolve actual skills and source in the current host and read instructions before execution. Repeat resolution on Work/Codex transfer.

## Delegate using the accepted scope

After acceptance of a passport, Foundry passes exact scope, criteria and child contracts, sources, decisions, outputs, permissions and acceptance to the skill constructor. Verify against the actual user request and fill needed method gaps. Preserve existing discovery and approval. Return a material new capability, effect or cost to the integrator as a specific change.

If the constructor is unavailable, use an equivalent embedded method from bundled domain, inheritance and production contracts with Skill Creator when feasible. Record `embedded_method`, actual actor and acceptance. If needed competence or tools are unavailable, prepare a handoff and continue independent work.

For unavailable required App/ChatBot capabilities, keep the component blocked until an appropriate actor or verified domain alternative can execute it. Transfer the prepared packet to a capable host. Distinguish unavailable tools from a product decision that the component is inapplicable.

## Combined app and bot

A shared order is one example. Parent owner defines identity, tenant and access, IDs, states, API and events, idempotency, versioning, privacy/retention/delete, deep links and shared wording. App owner implements the app journey. Bot owner handles the channel, adapter, conversation, actions and delivery. Keep one balance, consent source and order status.

Bind the shared contract for both components by one ID, hash and owner and `component_ids`. Name actual source and consumer reads, writes, events and failures. A shared contract change triggers both affected paths before integration. A local UI change without server impact can remain local.

A support bot may serve one app component and its already accepted product scope. A separate complete bot journey, catalog and operations need their own component scope and acceptance.

## Self-contained handoff and receiving

Use `assets/component-handoff.template.json` and `atelier-component-handoff/1`. Record product and component IDs, parent intent and authority, inherited and owned requirements, scope/stop, permissions/budget, decisions, actual capabilities, files and hashes, shared contracts and owners/consumers, outputs and acceptance, actual jobs/evidence, unresolved work, checkpoint and next action. `return_to` records a stable parent selector and component ID. `orchestrator_chain` records actual responsibility, ends with `invocation.selector` and has `return_to.selector` immediately before it. Selectors are stable slugs without display versions.

Bot `proposed_channels` and `selected_channels` are separate. Keep channel choice open until selected. `platform_adapter_contract_refs` identifies included adapter contracts. These arrays may be empty for other components.

`invocation.status=planned` records intent. `performed` requires actual actor, resolved skill snapshot and receipt bytes/hash. Resolve the snapshot from initial frontmatter. A `name:` example in body is not identity. Each referenced receipt has `actor` equal to `invocation.actor`, current `component_id` and nonempty `requirement_ids` within the owned set. `claim/method/scope` says what was observed. Verify underlying truth independently of these bindings.

Keep `invocation.activity` separate from skill name and scope. `planning` covers read, analysis, research and decision documents under any current grant. `skill_construction` builds or changes reusable skills in `agent_skill` and requires `construction_only`. `product_execution` implements or changes the app/bot and requires `component_execution`. Product authority and personal-skill installation are distinct. `performed`, embedded construction and ready-to-receive scope follow this matrix. A draft can describe proposed work. Deployment, messaging and spending have independent authority.

`deliverables` lists only existing files by path and digest in every status. Planned outputs belong in scope and acceptance. Every `open_questions` object has `question`, boolean `blocking` and `status=pending|resolved`. Resolved requires `resolution_ref`. Reject bad types, unrecognized status or a blocking unresolved item in a ready packet.

Run `python3 -B scripts/check_component_handoff.py HANDOFF.json --root PROJECT_DIR` and add `--ready` when delivering for execution. It checks shape, references, current file hashes, selectors and declared scope boundaries. Verify completeness, consent, actual invocation and the relevant integration, human or provider result separately.

The receiver reads the packet without chat history, verifies sources, scope and versions, reproduces the expected case, and returns outputs, hashes, verdict and limits. Route stale or missing inputs, incompatibilities and consequential changes to `return_to` with exact requirement IDs. Preserve accepted originals and completed work. Update the same parent registry and checkpoint after each stage.
