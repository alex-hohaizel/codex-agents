# Первинні технічні джерела

Перевірено через web retrieval2026-11-03; це підстави контрактів, не докази власного runtime. Перед implementation звірити актуальну operation/API version і applicable limits.

- Telegram Bot API: https://core.telegram.org/bots/api — transport/update/callback interfaces; клієнтське очікування callback завершується answerCallbackQuery, окремо від виконання доменної дії.
- Slack Events API: https://docs.slack.dev/apis/events-api/ — event identity, retries і opt-in delayed events; можливий пізній повтор означає потребу перевіряти current authorization/version.
- Slack interactions: https://docs.slack.dev/interactivity/handling-user-interaction/ — acknowledgement і наступна видима відповідь є різними операціями.
- Discord official API source: https://github.com/discord/discord-api-docs/blob/main/developers/interactions/receiving-and-responding.mdx — initial response та follow-up token lifecycle; звірити часові межі перед залежним recipe.

Узагальнення про durable state, permission/version checks, privacy lineage і integrated acceptance — інженерна адаптація цих контрактів та наскрізної методики, а не дослівна вимога платформ. Документація не підтверджує, що конкретний бот має доступ до API чи вже доставив повідомлення.
