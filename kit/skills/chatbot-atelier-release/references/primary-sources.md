# Primary technical sources

These references were reviewed using web retrieval on 2026-11-03. Use them for contract design. Verify the current operation, API version and limits for implementation.

- Telegram Bot API https://core.telegram.org/bots/api covers transport, updates and callbacks. answerCallbackQuery clears the client wait. Verify the domain action separately.
- Slack Events API https://docs.slack.dev/apis/events-api/ covers event identity, retries and opt-in delayed events. Recheck current permission and version on delayed replay.
- Slack interactions https://docs.slack.dev/interactivity/handling-user-interaction/ separates acknowledgement from a later visible response.
- Discord API documentation source https://github.com/discord/discord-api-docs/blob/main/developers/interactions/receiving-and-responding.mdx covers initial response and follow-up token lifetime. Check current timing against the dependent recipe.

Durable state, authority and version checks, privacy lineage and integrated acceptance are engineering adaptations of these sources. Verify actual bot credentials, calls and delivery separately.
