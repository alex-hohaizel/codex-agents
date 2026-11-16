# Product components and routing across families

This guide covers selection, stable invocation, component packaging, execution and return. Use it when App Atelier receives part of another agent's plan, an app needs a chatbot, or a specialized method is missing.

## Scope and authority

An app, chatbot and specialized agent tools can be components of one product. Share the exact `product_id`, parent requirement IDs, accepted decisions, common contracts and responsible owners. App Atelier owns its assigned app work, and the parent integrator accepts cross-component results. A direct App Atelier request needs no additional Agent Foundry wrapper.

For a new project, align `product_id` with the canonical App profile and state. In an existing project, reconcile differing parent and local IDs with an explicit checked mapping or return the conflict upstream. External job, effect and receipt records include `(product_id, component_id, local_id)` so corresponding local IDs cannot collide.

For each task identify `component_id`, owned requirements, inputs, outputs and consumer, shared contracts, authorized effects and budget, due acceptance and `return_to`. Put the actual delegation path in `orchestrator_chain`. Return results to the parent without recursively starting the same work. Assign one writer to each shared API/schema, permission policy, design token set, knowledge base and release epoch.

## Stable selectors and route selection

`assets/specialist-routes.json` lists stable selectors and selection conditions. It does not prove installation or execution. Use `@<stable-name>` in Work and `$<stable-name>` in Codex. The frontmatter `name` is stable and the display version is separate. Find the installed source by that ID, read its current inputs, outputs and restrictions, and record actual version and hash in the job. The latest version («Остання актуальна версія») is established by checked available source, not a folder label or a previous chat.

| Condition | Work | Codex | Output and recipient |
| --- | --- | --- | --- |
| The parent automation plan includes an app or the product boundary changes | `@agent-foundry` | `$agent-foundry` | Parent plan, stable IDs, scope and decisions. App returns its component and cross-system gaps to the integrator. |
| A reusable specialized method or family needs design and no suitable source exists | `@design-specialist-skills` | `$design-specialist-skills` | Blueprint or method with inherited requirements. Ordinary app builds do not require this route. |
| The component is an app | `@app-atelier-director` | `$app-atelier-director` | Accepted app scope, relevant stages, source, builds, QA and handoff. |
| A bot is a separate channel, part of the core or complex support | `@chatbot-atelier-director` | `$chatbot-atelier-director` | Full bot component or exact assigned slice under the shared product contracts. |
| A specific bot adapter, action or job is needed | `@chatbot-atelier-integrations` | `$chatbot-atelier-integrations` | Testable adapter with identity, audience, delivery, receipt and recovery. Reuse current product research. |
| Only knowledge, memory, conversation, media or QA is needed | Relevant `@chatbot-atelier-knowledge`, `@chatbot-atelier-conversation`, `@chatbot-atelier-media` or `@chatbot-atelier-qa` | The corresponding stable IDs with `$` | Specific artifact or contract and appropriate proof. App integrates the output into its own journey. |

A listed name does not establish an invoked («викликано») status. When a peer is unavailable, do the authorized work supported by local contracts or prepare a self-contained package for a suitable environment. Keep the required capability blocked if the useful result depends on it. Reuse a sufficient existing method before constructing another.

## Component input and admission

The current component format is `atelier-component-handoff/1`. It carries:

- `product_id`, `component_id`, `component_kind`, `parent_requirement_ids`, `owned_requirement_ids`, known dependencies and actual `return_to` or consumer.
- Current intent and scope, accepted decisions and originals, applicability, material unknowns, and input files and sources with SHA-256.
- Typed domain, API, event, data and auth contracts with stable contract ID, owner, file and hash, reader/writer, semantic invariants and version change.
- Environment and capability snapshot, permissions, external operations, budget, stop, limits and assignment of resources.
- Requested deliverables, acceptance, oracles, negative cases, required evidence types and due gate.
- For a chatbot, `selected_channels` or `proposed_channels`, audience, identity, linking, revocation and retention, adapter references and delivery semantics. Leave unspecified channels open.
- Actual attempts, jobs and unknown outcomes, output files and hashes, obtained proof, gaps, checkpoint and exact next action.

Register the package in App's ledger as an `artifact` with path, hash and relevant job and requirement references. The ledger has no `put --kind component` and does not need a parallel mutable register. A template cannot grant execution. Bind product decisions and current permissions to the actual request and reuse a valid existing approval. A critical unknown blocks its dependent action while independent analysis or design can proceed. Skills and messages do not automatically carry credentials, private chat history or browser sessions.

## App and bot ownership of support

`@app-atelier-support` owns the product support contract: categories and guest/account modes, permitted fields and actions, knowledge base, prices, known problems, tone, case lifecycle, limits, fallback, and app/web experience. Ordinary local help does not open a new bot project. If a bot channel is needed, assign the adapter, knowledge or conversation work to the relevant ChatBot Atelier module. The accepted design determines the exact channels and count.

A bot component preserves the parent app's auth, billing, data and support contracts. Provider identity differs from product identity. Linking, revocation and webhook trust require explicit contracts. Keep transport address, logical recipient, tenant, subject, audience and purpose separate. Revocation and deletion invalidate payloads, caches and pending jobs and must be checked again before delivery. A public or group channel cannot access private support by default. A shared use case needs its own rules and negative cases.

## Acceptance and return between Work and Codex

Use a shared acceptance scenario from app input through domain authorization, bot/tool/provider call, result, delivery and recovery. The consumer verifies source/build/config/content epoch, hashes, outputs and required proof mode. A correct bot answer alone does not prove app integration. A passing build does not prove provider delivery. Return affected IDs from a changed shared contract upstream, invalidate the dependent proof and recheck before the next effect.

A Work/Codex handoff includes actual working context, source/input/output hashes, completed checks, permissions, budget and stop, job IDs and unknown outcomes, next action and return verification. Codex can start from a real project and direct request and reconstruct the same records from current sources. Sequence writes to a common source, database or provider operation. Reconcile a timeout before any repeat with the same intent.

A cold return gives the parent integrated, reproducible work and actual execution evidence or an accurate `not_invoked`, `blocked` or `prepared` status. Scope and appropriate proof have separate acceptance. Fabricated calls, unavailable peer source and stale receipts do not close a component.

## Machine validation of the package

Instantiate `assets/component-handoff.template.json` for the real project. `python3 -B scripts/check_component_handoff.py FILE --root PROJECT_ROOT` validates current component structure and byte bindings. `--ready` checks declared readiness for handoff to the consumer. This does not certify product or runtime readiness, user assent or invocation of another skill. Verify the actual receipt and domain acceptance separately.

## Examples of scoped requests

After binding a real package, a Work request might be `@app-atelier-director Прийми app component з указаного пакета; збережи product_id, parent requirements і shared contracts. Виконай тільки доручений scope та поверни outputs/evidence/checkpoint інтегратору.` In Codex use `$app-atelier-director` with an accessible path to the same checked package or project. This example does not record a performed invocation.

For a bot component use `@chatbot-atelier-director Прийми bot component цього продукту; уточни невибрані канали, виконай доручені стадії за чинними product/auth/data contracts і поверни прийнятий результат App інтегратору.` Use `$chatbot-atelier-director` in Codex. For one adapter use `@chatbot-atelier-integrations` or `$chatbot-atelier-integrations` with the same component scope. Reuse current discovery.
