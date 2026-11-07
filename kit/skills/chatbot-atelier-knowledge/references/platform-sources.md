# Офіційні джерела та контракти каналів чатбота

Перевірено: **2026-11-03 UTC**. Лише первинні матеріали постачальників: Telegram, Slack, Discord, Meta (включно з колекціями `postman.com/meta`), Microsoft. Реальних акаунтів, токенів, підключень і надсилань не створювали. Це дослідницькі нотатки для навичок, а не готова конфігурація конкретного акаунта.

## Висновки для універсального процесу

- Канал обирають за явно названою платформою або уточненим контекстом. Слово «смак» не доводить, що користувач мав на увазі Slack.
- Розрізняти **runtime API/webhook**, **офіційний MCP для операцій**, **MCP для документації або налаштування**, **наявний у сесії connector**, **SDK/CLI**, **сторонній MCP**. Один клас не доводить наявність іншого.
- Офіційний MCP уже підтверджений у Slack. Офіційний Meta index підтверджує Social Technologies MCP для створення/конфігурації застосунків. Ствердження «у Meta немає офіційного MCP» застаріле. Повний набір Meta MCP tools та їх доступність конкретному акаунту тут не встановлено.
- Архітектурний висновок: адаптер приймає платформний envelope, перевіряє автентичність, зберігає inbox/dedupe key, швидко ack/defer за контрактом каналу; окремий worker виконує діалог/модель/дії, outbox контролює надсилання, статуси та повтори. Це наша рекомендація на основі контрактів нижче, не гарантія exactly-once від постачальника.
- Для вихідного timeout не припускати, що надсилання не відбулося. Повтор може породити дубль. Реалізація має встановити можливість idempotency/reconciliation конкретного endpoint, а не вигадувати універсальний `idempotency_key`.

## Telegram

**Setup та доступ.** [Офіційний tutorial](https://core.telegram.org/bots/tutorial) описує створення бота через BotFather `/newbot` та токен, який автентифікує саме бота. [Features](https://core.telegram.org/bots/features) описує group privacy mode та права; command scopes не є авторизацією команд. Для тестування рекомендується окремий bot account; `file_id` залежить від bot ID.

**Доставка.** [Bot API](https://core.telegram.org/bots/api): `getUpdates` і webhook взаємовиключні; pending updates зберігаються не довше 24 годин. `update_id` допомагає розпізнавати дублікати/порядок; після тривалої перерви послідовність може змінитися. Long polling підтверджує offset вище обробленого ID. Webhook надсилає HTTPS POST; non-2xx спричиняє повтори, але точний розклад/кількість у контракті не обіцяні. `setWebhook.secret_token` передається як `X-Telegram-Bot-Api-Secret-Token` — це shared secret, а не HMAC-підпис payload. `allowed_updates` є фільтром. `getWebhookInfo` дає стан/помилки. Flood control може повернути `parameters.retry_after`. Числові throughput limits у навичку не вшивати.

**Версія.** На момент читання заголовок changelog показує Bot API **10.3, 2026-08-24**. Це snapshot, не вимога назавжди зафіксувати цю версію; перед реалізацією перевірити changelog та сумісність SDK. Офіційний Telegram MCP у цьому дослідженні не підтверджений; відсутність у знайдених джерелах не доводить відсутності продукту.

## Slack

**Setup.** [OAuth](https://docs.slack.dev/authentication/installing-with-oauth/): Slack app встановлюють через OAuth v2, запитані scopes визначають доступ. [Events API](https://docs.slack.dev/apis/events-api/): підписки та granted scopes разом визначають події/видимість. Для HTTP delivery ack 2xx протягом 3 секунд; невдала доставка повторюється, є `x-slack-retry-num` / `x-slack-retry-reason`; envelope містить `event_id`. Подія доставки не є бізнес-обробкою — довгі LLM calls не вкладати в ack handler.

**HTTP security.** [Підпис](https://docs.slack.dev/authentication/verifying-requests-from-slack/) обчислюють над raw body та timestamp з signing secret; перевіряють `X-Slack-Signature`, свіжість `X-Slack-Request-Timestamp`, constant-time comparison. Старий verification token deprecated. [URL verification](https://docs.slack.dev/apis/events-api/using-http-request-urls) — окремий handshake з поверненням challenge; він не замінює перевірку кожного runtime request.

**Socket Mode.** [Офіційний guide](https://docs.slack.dev/apis/events-api/using-socket-mode/) дає delivery через WebSocket без публічного HTTP endpoint. Потрібен app-level token; URL отримують через `apps.connections.open`, він оновлюється. Ack використовує `envelope_id`; потрібен lifecycle reconnect. Не переносити HTTP signature/challenge контракт на Socket Mode механічно.

**Rate limit.** [Rate limits](https://docs.slack.dev/apis/web-api/rate-limits/) задаються за API method/workspace/app; HTTP 429 містить `Retry-After`. Ліміти конкретного методу, історії розмов і типу розповсюдження перевіряти під час реалізації.

**Офіційний MCP.** [Slack MCP overview](https://docs.slack.dev/ai/slack-mcp-server/): `https://mcp.slack.com/mcp`, Streamable HTTP, OAuth, зареєстрований Slack app/fixed app ID, admin approval та scopes. На цій сторінці доступ обмежений Marketplace/internal apps; unlisted apps не дозволені. MCP не скасовує API rate limits. Ця наявність не означає, що в поточній сесії connector має достатні tools/permissions, або що MCP замінює inbound Events API.

## Discord

**App/install.** [Application Commands](https://docs.discord.com/developers/docs/interactions/slash-commands): `applications.commands` може працювати без bot user; bot scope не обов'язковий для кожного command-only app. Installation context, permissions і спосіб отримання подій обирають відповідно до поведінки продукту.

**Interactions.** [Receiving/responding](https://docs.discord.com/developers/interactions/receiving-and-responding): для interactions HTTP webhook і Gateway — взаємовиключні delivery modes. Початкова response/defer має бути протягом 3 секунд; interaction token для follow-up діє 15 хвилин. Навіть interaction із Gateway отримує response через HTTP. Interaction ID — доступний candidate dedupe key; гарантований retry schedule у прочитаній сторінці не встановлено.

**Security.** [Overview](https://docs.discord.com/developers/interactions/overview): HTTP endpoint мусить відповідати на PING payload `type:1` через PONG `type:1`/200 і перевіряти Ed25519 signature над timestamp+raw body (`X-Signature-Ed25519`, `X-Signature-Timestamp`) публічним ключем app; invalid signature → 401. Це відрізняється від HMAC Slack.

**Message bots.** [Gateway](https://docs.discord.com/developers/events/gateway): потрібні intents; `MESSAGE_CONTENT` — privileged intent, що впливає на доступні поля, а не окрема подія. Його enable/review не вимагати для всіх interaction bots. [Rate limits](https://docs.discord.com/developers/topics/rate-limits): не hardcode; читати bucket/rate headers і реакцію 429. [API reference](https://docs.discord.com/developers/reference) — джерело чинних versions/deprecation. Офіційний Discord MCP тут не підтверджений.

## Instagram Messaging / Meta

**Перевірене.** [Meta Instagram collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) розділяє Facebook Login (із linked Page) та Instagram Login. [Instagram Login folder](https://www.postman.com/meta/instagram/folder/1z5vxzu/instagram-api-with-instagram-login) називає professional accounts — business/creator — і `instagram_business_basic`, `instagram_business_manage_messages`. [Send API опис](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-af579d08-121e-4897-8f45-5fd41ace49df) вимагає professional account token/permission та попереднє повідомлення від одержувача; group messaging не підтримується. Приклад endpoint використовує `graph.instagram.com/{{api_version}}/{{ig_user_id}}/messages`.

**Не змішувати.** Linked Facebook Page — підтверджена умова Facebook Login configuration; її не переносити на Instagram Login автоматично. Точні scopes залежать від configuration/endpoint; список усіх permissions з publishing guide не видавати за мінімум messaging.

**Прогалини.** Поточні Meta documentation URLs повертали 429. Чинні App Review/business verification criteria, webhook fields/signature/retries/ACK deadline, conversational window та rate-limit policy необхідно перечитати перед build/release. Тут не підтверджено точних чисел, не варто подавати їх як current факт. Офіційний root: [Instagram Platform](https://developers.facebook.com/docs/instagram-platform/).

## WhatsApp Cloud API / Meta

**Перевірене.** [Офіційна Meta collection](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api?entity=request-13382743-6a3563f7-9101-4fc0-b0ec-ac0e6a2b93a2) описує `whatsapp_business_management`, `whatsapp_business_messaging`; `business_management` потрібен додатково лише для відповідних portfolio operations. [Messages](https://www.postman.com/meta/whatsapp-business-platform/folder/o48mro7/messages) описує endpoint `/{{Phone-Number-ID}}/messages`, permission та message ID, за яким відстежують статус у webhook. Тому successful send response не можна ототожнювати з delivery/read. [Webhooks folder](https://www.postman.com/meta/whatsapp-business-platform/folder/6lt7to2/webhooks) має окремі subscribe/unsubscribe app-to-WABA operations.

**Security evidence boundary.** [Офіційний архівний Node SDK](https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/) розділяє GET verify-token → `hub.challenge` та POST `x-hub-signature-256` з app secret. Це первинне підтвердження відмінності handshake/signature, але сторінка явно archived; не рекомендувати цей SDK як підтримуваний production вибір і перевірити чинний webhook guide перед реалізацією.

**Актуальні зміни, що потребують перевірки.** Офіційні Meta матеріали 2026 описують [BSUID/usernames](https://developers.meta.com/resources/videos/whatsapp-usernames/), [WAAC/PMA account evolution](https://developers.meta.com/resources/videos/whatsapp-account-model-evolution/), [Embedded Signup v4](https://developers.meta.com/resources/videos/unified-onboarding-whatsapp/) та [Direct Send utility messages](https://developers.meta.com/resources/videos/whatsapp-direct-send-api/). Це summary descriptions, не докладні contracts і не доказ rollout для кожного акаунта. Вони достатні, щоб не закладати назавжди старі phone-number identity/account/template assumptions.

**Прогалини.** [Поточний webhook guide](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview) повертав 429. Популярне твердження про retries «до 7 днів» знайдено в сторонньому mirror, тому **не вважається тут current verified**. Аналогічно ціни, messaging windows, throughput tiers та template/consent eligibility залишаються live checks.

## Meta MCP і необов'язковий Teams

[Офіційний Meta news index](https://developers.meta.com/resources/blog/) прямо описує Social Technologies MCP: створення/конфігурація apps, зв'язування Business Portfolios та додавання use cases на кшталт WhatsApp messaging. [Linked article](https://developers.facebook.com/blog/post/2026/10/26/new-on-social-technologies-mcp/) повертав 429. Підтверджено існування setup/config capability; endpoint, authentication, конкретні tools, runtime messaging coverage і доступність акаунту **не встановлено**. Не підмінювати це стороннім `meta-mcp-server` repository.

Для Teams старий [bot overview](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/what-are-bots) перенаправляє у `previous-versions` і повідомляє про перейменування Teams AI library на Teams SDK та deprecated v1. Поточний [Teams SDK quickstart](https://learn.microsoft.com/en-us/microsoftteams/platform/teams-sdk/getting-started/quickstart) використовує Teams Developer CLI для scaffold/register/manage. Вбудована підтримка MCP у SDK не доводить існування одного універсального hosted Teams MCP server чи готового connector для цієї сесії.

## Рекомендовані поля adapter capability contract

Це інженерний висновок для навичок, а не vendor schema:

`platform`, `api_family`, `api_version_checked_at`, `account/install_context`, `credential_kind`, `granted_scopes`, `required_reviews`, `ingress_transport`, `verification_handshake`, `request_authentication`, `ack_or_defer_deadline`, `dedupe_key`, `ordering_scope`, `delivery_retry_policy`, `outbound_idempotency_support`, `rate_limit_scope`, `retry_hint`, `message_status_events`, `reply_window_policy`, `media_constraints`, `consent_policy`, `available_tools`, `owner_actions_remaining`, `evidence_url`.

Невідоме значення має бути явним `unknown/needs_live_check`, а не вигаданою гарантією. Фінальний checklist прив'язувати до реального обраного каналу, use case й доступного tool surface.
