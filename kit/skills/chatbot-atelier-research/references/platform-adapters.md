# Channel selection and platform contracts

Start with intake and channel boundaries, then define the adapter, tools, acceptance and handoff.

## Select the actual channel

Find where people already communicate, whether the bot is new or existing, the selected channel (Telegram, Instagram, Slack, Discord, WhatsApp, Teams, web or another named channel), DM/group/community/workspace, operator and application or account owner, audiences and actions, and existing accounts and connections. Resolve a material ambiguous name, such as «смак», with one short question. Continue independent work that can proceed.

Record requested, proposed and selected channels with the decision source. Add channels only for a defined need and scope. Compare feasibility, access, features, eligibility and review, permissions and privacy, UX, latency, cost and operations. If a required journey is unsupported, state the specific limit and a viable alternative. A missing permission stays an open dependency.

## Shared domain logic and distinct trust boundaries

Provider payloads map to domain commands, state, effects and memory. Normalize `channel_id`, `tenant_id`, `provider_actor_id`, `conversation_id`, `audience`, `event_id`, `event_type`, event and receive time, payload reference and policy versions. The domain checks authorization. Use exact provider identity. Link a person across channels only with a verified account link and appropriate permission.

Each channel has separate recipients, scopes, retention, connection, inbound trust, sending policy, rate budget and delivery evidence. Memory retains its access scope across channels. Forward, thread or reply does not change context ownership. Check access, consent and source version again before dispatch. Explain limits on recalling copies already delivered.

## Adapter reference matrix

Use each row to decide what needs a binding and probe for this target.

| Platform | Ingress and account boundary | Verify before implementing |
|---|---|---|
| Telegram | Bot API webhook or polling, bot/chat/user identity, DM and group scope | Webhook secret, offset and acknowledgment, deduplication, privacy mode and permissions, callback acknowledgment, media rights and current format and rate limits. |
| Instagram | Actual Instagram Login or Facebook Login configuration, professional account and scoped recipient | Verify linked Page requirements for the selected login, messaging scope, eligibility and review, webhook authenticity, allowed initiation/reply journey, window, media and rates. |
| Slack | Installed app in workspace or organization, Events HTTP or Socket Mode, DM/channel/thread scope | Raw-body HTTP signature and timestamp, separate URL verification, Socket Mode envelope ACK and reconnect, OAuth, event identity, interaction ACK/defer, method and workspace rate policy. |
| Discord | Application install context, interactions webhook or Gateway, member/guild/channel | HTTP signature and PING, initial reply or defer, follow-up expiry, Gateway intents, permissions and rate headers. For applicable scope, verify privileged message access. |
| WhatsApp | Current Cloud API configuration, verified endpoint and scoped business and user identities | Current account and identity model, permissions, webhook handshake and authentication, send statuses, and initiation/consent/template/window policy for the exact endpoint, rollout and use. |
| Teams | Current Teams app, SDK, install, channel, organization and tenant | App registration, authentication and audience, installation consent, activity and reply contract. Use current supported SDK guidance. |
| Web | Owned session, tenant and widget origin, HTTP or realtime transport | Session, CSRF and origin, reconnect and cursor, rate and abuse limits, persistence and permissions, DOM accessibility, end-to-end receipt semantics. |
| Another channel | Named provider and official documentation | Define a target-specific contract and probe. Check needed product approval before execution. |

## Adapter record

Use `assets/platform-adapter.template.json` and `python3 scripts/check_platform_adapter.py ADAPTER.json`. Record one current `chatbot.adapter/1` per channel, account and environment. A specified adapter records official documentation/version/date, eligibility and owner actions, audience and identity, authority and revocation, ingress transport and verification, deduplication key and ordering, durable boundary, sourced ACK/defer deadline, expiry and retries. Egress records endpoint and parameters, recipient resolution, consent/current-source policy, availability of idempotency, uncertain-outcome reconciliation and rate, media and error policy. Include tool, permissions, effective parameter checks, fallback and relevant probe artifacts.

Keep access tokens and signing secrets outside the package. Use a credential selector and owner and confirm identity binding to the bot, app or account. Confirm effective grants separately from presence of configuration. App setup, review and connection are distinct permitted actions with distinct outcomes.

Separate transport ACK, complete domain operation, provider acceptance, delivered/read and human observation. HTTP 200 only confirms its own boundary. Keep long generation and jobs outside a time-limited ACK. An accepted inbox meets the agreed persistence boundary. When outbound idempotency is unavailable, use reconciliation, explicit uncertainty or operator recovery supported by the real endpoint.

## API, SDK, MCP and connectors

Choose a tool for the exact operation. Distinguish runtime API and webhooks, official operation MCP, setup/configuration MCP, documentation MCP, connected session tools, SDK and CLI, and third-party MCP. A session connector and a product runtime credential have separate scopes. SDK support and server/tool availability need distinct proofs.

The recorded research identified official Slack MCP and Meta setup/config MCP. Verify the current endpoint, catalog, permissions and operational coverage before use. Slack MCP and inbound Events API serve separate boundaries. The recorded research did not establish official Telegram or Discord MCP. Treat this as an observation of that inquiry. Bind actual tool, descriptor/schema/catalog version, account and environment, grant, cost, consumed parameters and evidence for every use.

Documentation and catalog observation are distinct. Current windows, limits, prices and eligibility require a dated API/version-specific binding before build or release. Read primary sources and observed bounds in `references/platform-sources.md`.

## Recipe and negative cases

R-ADAPTER goes from selected channel and domain fixtures to account and permission feasibility, current references/catalog, typed adapter, separate authority/ACK/dispatch tests, authorized sandbox or test install, actual effect and delivery observation, integrated journey and recovery, and consumer acceptance. Work can analyze, specify and use available allowed probes. Codex can implement and verify through the actual available interfaces. Observe the relevant runtime regardless of handoff route.

Test wrong signature/token/origin, stale timestamp, replay and out-of-order events, ACK timeout and restart after durable commit, revoked OAuth between queue and dispatch, other-tenant recipient, matching display name without a verified link, expired interaction or reply window, unsupported media, 429/retry guidance, unknown send outcome, revoked source or consent during generation, provider accepted without delivery receipt, reconnect with pending queue, account/app switch, and a descriptor whose tool or scope is missing. Name platform, environment and version on fixtures and results. Mark replay separately from live evidence.

## Product or composite agent component

Accept `atelier-component-handoff/1` from `@agent-foundry` or `@app-atelier-director`. Capture product_id and component_id, parent and owned requirement IDs, shared contract owner/path/hash, scope/permissions/budget, requested and selected channels, pinned source inputs, outputs/consumer/acceptance, actual jobs, evidence and checkpoint. Parent product owns business rules, tenant and authorization, payments and data. Return scoped component results. Keep identity, knowledge, billing and product planning under the current owner unless the agreed contract calls for a change. Verify the next skill by stable name and return unresolved channel or shared-contract questions upstream.
