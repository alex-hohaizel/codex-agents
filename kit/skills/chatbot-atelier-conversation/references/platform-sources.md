# Primary chatbot channel sources and contracts

Source review date: **2026-11-03 UTC**. Evidence comes from Telegram, Slack, Discord, Meta including `postman.com/meta`, and Microsoft. The research used no account creation, credentials, connection or sending. Verify account and tool access for the actual project.

## Findings for the shared workflow

- Resolve the channel from the user's actual platform or relevant context. Ask a focused question when a name such as «смак» is ambiguous.
- Separate runtime API and webhooks, official operation MCP, documentation or setup MCP, available session connectors, SDK or CLI and third-party MCP. Verify each needed boundary.
- The recorded sources establish official Slack MCP and Meta Social Technologies MCP for app setup and configuration. Specific Meta operations and availability for an account remain unverified.
- A recommended adapter verifies the platform envelope, persists inbox work and the deduplication key, then acknowledges or defers under the platform contract. An independent worker handles dialogue, models and actions. The outbox tracks sends, statuses and retries. Confirm the actual idempotency boundary.
- Reconcile outbound timeouts before resending. Verify the endpoint's actual idempotency or readback options before relying on an `idempotency_key`.

## Telegram

**Setup and access.** The [official tutorial](https://core.telegram.org/bots/tutorial) describes BotFather `/newbot` and the credential belonging to that bot. [Features](https://core.telegram.org/bots/features) covers group privacy and permissions. Check actual authorization separately from command scope. Use an isolated test bot when available. `file_id` depends on bot identity.

**Delivery.** [Bot API](https://core.telegram.org/bots/api) defines exclusive `getUpdates` and webhook modes. The recorded contract keeps pending updates up to 24 hours. `update_id` can help detect order and duplication. Its sequence can change after a long pause. Long polling acknowledges through an offset higher than a processed ID. Webhooks use HTTPS POST and retry non-2xx results without a contractually fixed schedule or count in the checked source. `setWebhook.secret_token` arrives as shared secret `X-Telegram-Bot-Api-Secret-Token`. This verifies the secret, distinct from an HMAC body signature. `allowed_updates` filters delivery. `getWebhookInfo` exposes status and errors. Flood control can return `parameters.retry_after`. Verify actual limits before implementation.

**Version.** The reviewed changelog showed Bot API **10.3, 2026-08-24**. Check the current changelog and SDK compatibility at build time. The review did not establish an official Telegram MCP.

## Slack

**Setup.** [OAuth](https://docs.slack.dev/authentication/installing-with-oauth/) defines OAuth v2 app installation and requested scopes. [Events API](https://docs.slack.dev/apis/events-api/) ties subscriptions and granted scopes to event visibility. The recorded HTTP ACK deadline was 3 seconds. Delivery can retry with `x-slack-retry-num` and `x-slack-retry-reason`, while `event_id` identifies the event. Keep long model work outside the ACK handler.

**HTTP verification.** [Request signing](https://docs.slack.dev/authentication/verifying-requests-from-slack/) builds the signature using raw body and timestamp with the signing secret. Verify `X-Slack-Signature` and freshness of `X-Slack-Request-Timestamp` in constant time as applicable. Use the current signature procedure. [URL verification](https://docs.slack.dev/apis/events-api/using-http-request-urls) is a separate challenge handshake. Verify each subsequent runtime request.

**Socket Mode.** The [official guide](https://docs.slack.dev/apis/events-api/using-socket-mode/) describes WebSocket delivery without a public HTTP endpoint and an app-level token. Use `apps.connections.open` to obtain and refresh an endpoint. Acknowledge using `envelope_id` and handle reconnect. Follow the protocol for that transport.

**Rate limits.** [Rate limits](https://docs.slack.dev/apis/web-api/rate-limits/) depend on API method, workspace and app. HTTP 429 carries `Retry-After`. Verify actual rates for method, history and distribution during implementation.

**Official MCP.** [Slack MCP overview](https://docs.slack.dev/ai/slack-mcp-server/) records `https://mcp.slack.com/mcp`, Streamable HTTP, OAuth, registered app and fixed ID, admin approval and scopes. The reviewed page restricted access to Marketplace or internal apps and excluded unlisted apps. MCP remains subject to API rate limits. Check actual session permission and tool availability. Inbound events have a separate API contract.

## Discord

**App and installation.** [Application Commands](https://docs.discord.com/developers/docs/interactions/slash-commands) allows `applications.commands` without a bot user for applicable command-only apps. Choose installation context, permission and event delivery for actual product behavior.

**Interactions.** [Receiving/responding](https://docs.discord.com/developers/interactions/receiving-and-responding) describes HTTP webhooks and Gateway as exclusive delivery modes for interactions. The recorded initial response or defer limit was 3 seconds. Follow-up tokens lasted 15 minutes. Gateway interactions still receive responses through HTTP. Interaction ID is a candidate deduplication key. A fixed retry schedule was not established by the reviewed page.

**HTTP security.** [Overview](https://docs.discord.com/developers/interactions/overview) requires responding to PING `type:1` with PONG `type:1`/200 and verifying the Ed25519 signature over timestamp and raw body using app public key and `X-Signature-Ed25519` and `X-Signature-Timestamp`. Invalid signature returns 401. Apply the provider-specific signing method.

**Message bots.** [Gateway](https://docs.discord.com/developers/events/gateway) describes intents. `MESSAGE_CONTENT` is privileged access to fields. Enable or request review only when necessary. Use [Rate limits](https://docs.discord.com/developers/topics/rate-limits), bucket and response headers, and HTTP 429 handling. [API reference](https://docs.discord.com/developers/reference) lists current versions and deprecations. The recorded review did not establish official Discord MCP.

## Instagram Messaging / Meta

**Verified at review.** The [Meta Instagram collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) distinguishes Facebook Login with linked Page and Instagram Login. The [Instagram Login folder](https://www.postman.com/meta/instagram/folder/1z5vxzu/instagram-api-with-instagram-login) identifies professional business/creator accounts and `instagram_business_basic` and `instagram_business_manage_messages`. The [Send API description](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-af579d08-121e-4897-8f45-5fd41ace49df) needs professional account authorization and a previous message from the recipient and does not support group messaging. Example route: `graph.instagram.com/{{api_version}}/{{ig_user_id}}/messages`.

**Select the exact login configuration.** Verify linked Facebook Page requirements for Facebook Login and separately verify Instagram Login. Derive messaging scopes from actual configuration and endpoint, distinct from publishing scopes.

**Open checks.** Other applicable Meta documentation returned 429 at review. Recheck App Review and business verification, webhook fields, signatures, retries and ACK deadlines, messaging windows and rate policy before build or release. [Instagram Platform](https://developers.facebook.com/docs/instagram-platform/).

## WhatsApp Cloud API / Meta

**Verified at review.** The official [Meta collection](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api?entity=request-13382743-6a3563f7-9101-4fc0-b0ec-ac0e6a2b93a2) documents `whatsapp_business_management` and `whatsapp_business_messaging`. Add `business_management` only for relevant portfolio operations. [Messages](https://www.postman.com/meta/whatsapp-business-platform/folder/o48mro7/messages) describes `/{{Phone-Number-ID}}/messages`, permission and message ID for webhook status tracking. Capture actual delivered/read state separately from accepted sent response. [Webhooks](https://www.postman.com/meta/whatsapp-business-platform/folder/6lt7to2/webhooks) describes separate app-to-WABA subscribe and unsubscribe operations.

**Security evidence.** The official [archived Node SDK](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/) distinguishes GET verify-token and `hub.challenge` from POST `x-hub-signature-256` using the app secret. Use it as historical evidence of separate boundaries. Verify current webhook guidance and a supported production SDK.

**Current changes to verify.** Meta's 2026 materials describe [BSUID and usernames](https://developers.meta.com/resources/videos/whatsapp-usernames/), [WAAC/PMA account evolution](https://developers.meta.com/resources/videos/whatsapp-account-model-evolution/), [Embedded Signup v4](https://developers.meta.com/resources/videos/unified-onboarding-whatsapp/) and [Direct Send utility messages](https://developers.meta.com/resources/videos/whatsapp-direct-send-api/). Verify actual account rollout and contract. Treat phone-number identities, accounts and template requirements as versioned.

**Open checks.** The [current webhook guide](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview) returned 429 at review. A third-party mirror mentioned retries of up to seven days. This value remains unverified. Check prices, messaging windows, throughput tiers and template and consent eligibility on the target.

## Meta MCP and optional Teams

The official [Meta news index](https://developers.meta.com/resources/blog/) describes Social Technologies MCP for creating and configuring applications, linking Business Portfolios and adding use cases such as WhatsApp messaging. The [linked article](https://developers.facebook.com/blog/post/2026/10/26/new-on-social-technologies-mcp/) returned 429. Setup and configuration capability was established. Endpoint, authentication, exact tools, runtime messaging and account availability remain open. Treat `meta-mcp-server` as a separate third-party project.

The old Teams [bot overview](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/what-are-bots) redirects to `previous-versions` and reports Teams AI library renaming to Teams SDK and v1 deprecation. The [current Teams SDK quickstart](https://learn.microsoft.com/en-us/microsoftteams/platform/teams-sdk/getting-started/quickstart) uses Teams Developer CLI to scaffold, register and manage apps. Verify actual hosted MCP and session connectors separately from SDK MCP support.

## Suggested adapter capability fields

This is a repository contract adaptation. Fields:

`platform`, `api_family`, `api_version_checked_at`, `account/install_context`, `credential_kind`, `granted_scopes`, `required_reviews`, `ingress_transport`, `verification_handshake`, `request_authentication`, `ack_or_defer_deadline`, `dedupe_key`, `ordering_scope`, `delivery_retry_policy`, `outbound_idempotency_support`, `rate_limit_scope`, `retry_hint`, `message_status_events`, `reply_window_policy`, `media_constraints`, `consent_policy`, `available_tools`, `owner_actions_remaining`, `evidence_url`.

Use `unknown/needs_live_check` for unknown fields. Bind verification to selected channel, exact use and actual tools.
