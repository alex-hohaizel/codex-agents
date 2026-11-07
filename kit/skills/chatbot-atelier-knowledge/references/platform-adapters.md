# Вибір каналів і контракти платформ

Зміст: intake → межа каналу → адаптер → інструменти → приймання → передача.

## Спочатку вибрати канал

До platform-specific архітектури з'ясувати: де люди вже спілкуються; бот новий чи чинний; Telegram, Instagram, Slack, Discord, WhatsApp, Teams, web-віджет або інший конкретний канал; DM/group/community/workspace; хто оператор, власник застосунку й акаунта; які аудиторії та дії; які акаунти/підключення вже є. Не вважати слово «бот» Telegram за замовчуванням. Не трактувати неоднозначну назву, наприклад «смак», як підтверджений Slack: поставити одне адресне уточнення, незалежний аналіз продовжити.

Записати requested/proposed/selected канали й джерело рішення. Один канал не означає multi-channel; додаткові адаптери потребують користі й обсягу. Порівняти здійсненність, доступ користувачів, потрібні функції, account eligibility/app review, права/приватність, UX, latency, вартість та експлуатацію. Якщо платформа не дозволяє потрібний journey, повернути конкретну межу й альтернативу до product choice; не називати missing permission N/A.

## Одна предметна модель, окремі межі довіри

Доменні commands/state/actions/memory не залежать від provider payload. Адаптер нормалізує подію в `channel_id`, `tenant_id`, `provider_actor_id`, `conversation_id`, `audience`, `event_id`, `event_type`, event/receive time, payload reference і policy versions. Авторизацію визначає домен, а не display name/username або поле, запропоноване моделлю. Provider identity зберігати без втрати точності; між каналами не з'єднувати людей за збігом імені чи email без перевіреного account link та належного дозволу.

Кожний канал має окремі allowed recipients/scopes/retention, підключення, inbound trust, send policy, rate budget і delivery evidence. Multichannel memory не стає загальною автоматично. Власник контексту не змінюється через forward/thread/reply. Відкликання доступу, source version і згода перевіряються перед dispatch; already delivered copy має межі відкликання, які треба чесно пояснити.

## Матриця адаптерів

Це маршрути для binding, а не готові інтеграції або перелік установлених tools.

| Платформа | Вхід і account boundary | Що перевірити перед реалізацією |
|---|---|---|
| Telegram | Bot API, webhook **або** polling; bot/chat/user identity; DM/group rights | Верифікація webhook secret token; offset/ack/dedupe; privacy mode/permissions; callback acknowledgement; медіаправа й актуальні format/rate limits |
| Instagram | Обрана конфігурація Instagram Login або Facebook Login; professional account та scoped messaging recipient | Не переносити linked Page вимогу між login configurations; потрібні messaging scopes/account eligibility/review, webhook security, дозволений initiation/reply journey, актуальні messaging windows/media/rates |
| Slack | Установлений app/workspace/org; Events HTTP **або** Socket Mode; DM/channel/thread scopes | Raw-body signature+timestamp для HTTP; окремий URL verification; Socket Mode envelope acknowledgement/reconnect; OAuth scopes, event identity, interaction ack/defer, method/workspace rate policy |
| Discord | App/install context; interactions webhook **або** Gateway; member/guild/channel identity | HTTP signature/PING contract; initial response/defer і follow-up expiry; Gateway intents; privileged message access лише якщо потрібен; permissions/rate headers |
| WhatsApp | Чинна Cloud API/account configuration; verified endpoint та scoped business/user identity | Актуальні account/identity models і дозволи; webhook handshake **та** authentication; send status events; initiation/consent/template/window policy саме для поточного endpoint, rollout і use case |
| Teams | Поточний Teams app/SDK/channel/install context; org/tenant audience | Чинний app registration, authentication/audience, installation consent, activity/reply contract; не scaffold за deprecated SDK guide |
| Web | Власний session/tenant/widget origin; HTTP/realtime transport | Session/CSRF/origin policy, reconnect/cursor, rate/spam limits, local persistence/permissions, DOM accessibility та own end-to-end receipt semantics |
| Інший канал | Точно названа платформа й офіційна документація | Новий contract/probe та product approval за потреби; не механічна копія Telegram або Slack |

## Паспорт адаптера

Використати `assets/platform-adapter.template.json` і `python3 scripts/check_platform_adapter.py ADAPTER.json`. Один current record `chatbot.adapter/1` на конкретний channel/account/environment. Обов'язкові для specified: official documentation/version/date; account eligibility та remaining owner actions; audience/identity/auth/revoke rules; ingress transport/verification, dedupe key/order scope, durable boundary, ack/defer deadline і джерело, expiry/retries; egress endpoint/parameters, recipient resolution, consent/current-source policy, idempotency support або його відсутність, uncertain-outcome reconciliation, rates/media/error policy; tool surface/permissions/effective parameter checks/fallback; належні probe artifacts.

Не зберігати access tokens/signing secrets у пакеті. Використовувати credential selector, власника й перевірку binding до правильного bot/app/account. Configured credential не є доказом правильного grant або доступу. App setup/review/підключення — окремі операції зі своїми outputs та дозволами.

Швидкий transport ack, завершення доменної дії, provider acceptance, delivered/read та human observation — різні події. Не приписувати HTTP200 читання людиною. Довгу LLM/media/job роботу відділяти від ack, якщо канал цього вимагає; accepted inbox має відповідати визначеній durability межі. Якщо API не гарантує outbound idempotency, не вигадувати універсальний idempotency key: обрати reconcile/unknown/manual recovery за реальними можливостями endpoint.

## API, SDK, MCP і connectors

Обирати поверхню за **конкретною операцією**, а не модною назвою. Розрізняти runtime messaging API/webhook, офіційний operational MCP, setup/configuration MCP, documentation MCP, підключений у цій сесії connector, SDK/CLI та сторонній MCP. Наявний connector Work не означає runtime credential готового бота. Наявність MCP у SDK не означає hosted server або потрібний tool.

Для Slack офіційний MCP задокументований; це не заміна inbound Events API чи автоматичний grant. Meta публічно описує setup/config MCP; доступний endpoint, tools, permissions і runtime messaging coverage звіряти за поточним каталогом перед використанням. Для Telegram/Discord дослідження не встановило офіційний MCP: не писати ані «встановлений», ані абсолютне «не існує». Для кожного виклику зафіксувати descriptor/schema/catalog version, actual available tool, account/environment, потрібний grant, cost, actual parameter consumption й evidence.

Офіційна документація й capability/catalog snapshot — різні джерела. Дані про API windows/rate limits/prices/account review змінюються: binding перед build/release має дату й конкретну версію; не вшивати неперевірене число в універсальний рецепт. Первинні джерела та перевірені межі — у `references/platform-sources.md`.

## Рецепт і негативні сценарії

R-ADAPTER: selected channel + canonical domain fixtures → account/permission feasibility → current docs/catalog → typed adapter → separate auth/ack/dispatch tests → provider sandbox або погоджена test installation → actual effect+delivery observation → integrated journey/recovery → consumer acceptance. У Work дозволений повний analysis/spec/available connector probe; у Codex — самостійна реалізація/тестування за доступними interfaces. Передача не замінює фактичний probe.

Перевірити: wrong signature/token/origin; old timestamp; event replay/out-of-order; ack timeout та restart після durable commit; OAuth revoked між enqueue і dispatch; інший tenant/channel recipient; shared display name без identity link; expired interaction/reply window; unsupported media;429/retry hint; send timeout з невідомим outcome; source/consent revoke під час генерації; provider accepted без delivery receipt; reconnect із pending queue; account/app switching; MCP descriptor є, але потрібний tool або scope відсутній. Fixtures й результати мають назвати платформу/environment/version; replay не видається за live proof.

## Компонент застосунку або складеного агента

Приймати `atelier-component-handoff/1` від `@agent-foundry` або `@app-atelier-director`: product_id/component_id, parent та owned requirement IDs, shared contracts із owner/path/hash, scope/permissions/budget, selected/proposed channels, source inputs, expected outputs/consumer/acceptance, actual jobs/evidence/checkpoint. Батьківський продукт зберігає authority над business rules, tenant/auth, оплатами та даними; ChatBot Atelier реалізує погоджений bot component і повертає точні результати. Не створювати другу незалежну identity, KB, billing або product plan без потреби. Доступність наступної навички перевіряти за стабільним ім'ям; unresolved channel або shared contract повернути адресно upstream.
