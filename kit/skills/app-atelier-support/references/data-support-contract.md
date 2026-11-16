# Data, support and access boundaries

## Product data

Use the minimum necessary data and prioritize local storage where the profile calls for it. Justify accounts, synchronization and cloud storage. Map field → source/purpose → subject/role → allowed recipient → storage/retention → redaction → export/delete/revoke → backup/restore fence. Cover analytics, support, AI providers, conversations, logs, caches and indexes separately. Tool convenience does not authorize moving private data into another context.

## Support

A support bot is a separate product deliverable. A skill's presence does not establish that the bot is running. Where the product has accounts, support guest and authorized personal modes. Guests have the public knowledge base and their own bounded session. Signed-in users receive only their explicitly authorized records. Authorize every read and action in the backend outside the language model. A text email, ID or username does not prove identity. Without signup, do not promise cross-device personal history.

App, web and selected external bot channels share a support contract and knowledge base. Identify the necessary channels, audience, account type and actual API or connector capability. Telegram requires an explicit channel decision. Specify the platform adapter through `@chatbot-atelier-integrations` by [component handoff](cross-family-routing.md). Bind channel identity to the internal subject, including expiry, replay resistance, revocation, transport verification and authorization before effect or delivery. For a selected Telegram route, use a short-lived single-use challenge from authorized app/web to the private bot and confirm the link in the active app/web session. Bind the numeric sender ID. Credentials and personal information stay out of the challenge. Private support rejects public, group or unrelated audiences. A shared use case requires its own agreed scope and security evidence.

Start with read-only help. An allowed change or financial or administrative effect uses a specific authorized API with current scope, confirmation, idempotency and receipt. Distinguish advice, proposed action, actual execution and unknown outcome. Do not invent a refund, recovery, access, operator or SLA.

Version the knowledge base by product and language. Record sources, owners, freshness and correction rules. Obtain pricing and availability from current sources. Support requests do not rewrite policy or enter public knowledge. Treat user inputs and retrieved documents as untrusted data with no authority to expand access.

For an unresolved case give a safe response, case ID, minimal permitted diagnostics and status, and group applicable evidence into a technical task for the agent. More unresolved manual exceptions call for a review of the operating model. For AI use help/FAQ, then retrieval or a bounded call only where needed. Define user, session and global caps, timeout, cache, circuit breaker and fallback. Do not promise 100% automated resolution of arbitrary requests.

## Checks before personal access

Test A-to-B attempts through IDs, cache, history, attachments and channels, plus guest-to-private access. Check expired, replayed, intercepted and revoked challenges, forged webhooks, group updates, logout and cached data, stale or injected knowledge, AI outage and cap, duplicate or unknown effects, delete, revoke and restore. Record skill behavior and product/backend/client integration evidence separately.

Keep secrets out of chats, screenshots, packages, fixtures and logs. Retention and deletion cover derived data. Verify actual deletion and mark any incomplete external cleanup blocked. Do not restore revoked access or data from an old backup.
