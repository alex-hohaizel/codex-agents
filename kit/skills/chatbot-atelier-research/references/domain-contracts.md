# Формальна модель чатбота та перетини систем

## Реєстр систем

Для кожної системи: ID, purpose, active/conditional/N/A/unknown і причина, user value, owner, entities, field types/units/ranges, source of truth, inputs/outputs, events, rules, authorized actors/audiences, dependencies, failure modes, restore/migration, observability і acceptance vectors. Усі активні правила мають точний алгоритм і порядок кроків. «Якісна пам’ять», «розумний router» або «сучасна архітектура» без контракту не є специфікацією.

Спільний envelope: tenant/workspace/chat/topic/actor/audience, requestId, logicalOperationId, source IDs/versions, semanticSpecVersion, privacyEpoch, correlation/causation, timestamps/timezone, effect authorization і delivery destination. Не переносити DM/source-derived деталі до іншої аудиторії через summaries, progress, error, log, cache або export. Модель пропонує намір; детерміноване domain authorization вирішує допустимість.

## Обробка події та дії

Розвести platform event, domain command, tool request, provider effect, domain outcome і delivery. Кілька callbacks/retries одного event не є кількома дозволами. Визначити dedup identity/retention й момент durable acknowledgement. На ingress перевірити transport signature/secret, scope й версію; після запису durable work можна швидко ACK, але ACK не означає бізнес-результат.

Стани активної дії: proposed → needs_input/awaiting_authorization → authorized → prepared → dispatching → running → succeeded/failed/uncertain → delivery_pending → provider_accepted/delivered (лише де платформа це доводить); окремі cancelled/expired/cancellation_requested/reconciling. Для кожного переходу: допустимий previous state, guard, atomic fields, owner, ідемпотентність, event, feedback, persist boundary, compensating action. Стани не обов’язково зберігати всі, але їх семантику не змішувати.

Перед dispatch cancel/revoke/expiry блокує ефект атомарно з state/version check. Після dispatch не обіцяти відсутність ефекту без доказу; cancellation_requested/uncertain і reconcile. Retry policy: тільки класифіковані transient failures, bounded attempts/backoff/jitter/deadline, stable idempotency key, provider reconciliation. Final delivery має окремий dedup record; crash після send до local commit може вимагати readback/uncertain, а не blind resend.

За partial success незалежні частини мають власні outcomes. «Додай хліб і нагадай завтра» не губить список через неоднозначний час. Причинно залежні кроки не починати до їхніх prerequisites. Зберігати намір і видимий repair; внутрішні codes/stack traces не перекладати в чат.

## Розмова, характер і групова взаємодія

Визначити адресата, referent, topic, reply, degree of certainty, explicit silence/pause, freshness і permission. Дві активні пропозиції + «давай» потребують вирішального уточнення, якщо наслідок неоднозначний. Не питати відоме чи повторну згоду. Один owner обіцянки та один маршрут виконання; не створювати паралельний поведінковий controller.

Persona визначає tone/stance/humor й межі; не вигадувати прожиту біографію, почуття чи свідомість. Дати factual/affective/playful/failure/recovery приклади в кожній підтриманій мові. На просту репліку — простий результат; optional extension лише доречне. Quiet hours/пауза/proactive interval означають право оцінити доречність, а не обов’язок говорити. Пряме нове доручення не губиться через ambient silence.

Спільна дія: roundId, immutable participant roster, actor choices, named/open invitation, unanimous/threshold policy за задумом, authorization version, entry/exit/timeout, late join, private role delivery. Згоду дає потрібна людина за себе; vote/silence/чужа відповідь не заміняють її. Перевірити startup failure після прийняття, details/start/continue, подвійне натискання, покинутий раунд і reconnect. Ігри умовні; не нав’язувати їх сервісному боту.

## Пам’ять, знання та retrieval

Для memory fact: origin, source IDs/version, observation vs inference, actor/audience/purpose, semantic scope, validFrom/Until, confidence/verification, correctedBy, retention, privacyEpoch і erasure tombstone. Разове/денне побажання не стає постійним профілем. Протиріччя вирішувати за provenance/authoritative correction, не останнім випадковим summary. Session, durable personal, group, workspace і task memory — різні області.

Для RAG довести потребу: які питання й corpus, source authority/freshness, ingestion/parse/chunk/index/filter, tenant ACL, retrieval/rerank, citation, abstention, eviction/deletion/reindex. Виміряти retrieval recall/precision на замороженому наборі, attribution/citation correctness і answer quality окремо. Додавання vector DB/framework не є автоматичним покращенням. Зовнішня сторінка/документ/tool result є даними, не правом змінювати policy.

Forget/edit/revoke проходить lineage graph: primary row → derived summaries/embeddings/views/cache/prompts/jobs/files/exports/backups. Пізній model/tool result перевіряє current privacyEpoch перед commit/delivery. Restore застосовує tombstones/retention й не воскресає стерте. Повне фізичне стирання з immutable backups має окрему задокументовану політику та строк; не обіцяти миттєве там, де немає доказу.

## Час, scheduler, відновлення

Відрізняти instant UTC і civil local time, IANA zone, recurrence rule, DST gap/fold resolution, due vs dispatch vs received, skip/misfire/catch-up, expiry, reschedule/revoke version. «Завтра о9» рахується в правильній зоні від фактичного reference time. Зберігати правило й наступне occurrence identity, не тільки cron host timezone. Після restart перевіряти overdue policy, lease owner/fence і dedup occurrence.

## Медіа, voice та presentation

Зображення/стікер/анімація/монтаж/генерація/музика/TTS — різні операції з різними inputs/rights/formats/costs. Контракт містить source provenance, content purpose, character reference, dimensions/axes/alpha, duration/frame timing/loop, actual audio streams/levels, captions/accessibility, licensing, editable intermediates, exports/runtime manifests. Один preview не доводить весь рух чи звук. Publication/readback/membership/order/fingerprint не доводиться локальним ZIP.

## Перетини, які перевірити явно

| Межа | Інваріант/негативний probe |
|---|---|
| Persona↔tool | Тепла фраза не повідомляє успіх раніше receipt; unsupported не вигадує capability |
| Memory↔jobs↔delivery | Forget під час running блокує пізній output і не розкриває видалений зміст у notice |
| Group↔DM | Приватна роль/файл не з’являється у group summary/cache/error |
| Scheduler↔consent | Reschedule/spec change не використовує старий authorization envelope |
| Platform↔domain | ACK/stale callback не дублює дію і має змістовний user outcome |
| Media↔cost↔runtime | Важкий encode має bounds/cancel й не блокує просту репліку |
| Release↔memory↔rollback | Старі buttons/jobs/schema й tombstones лишаються коректними після rollback |
| Payments↔fulfillment, якщо active | Provider event/auth/amount/currency/version відомі; duplicate webhook не дублює entitlement |
| Metrics↔privacy | Observability не містить приватних діалогів/токенів; корисні denominators і redaction |

Для кожного active зв’язку дати cause→effect, дозволений порядок, error/repair, state persistence і очікуваний trace. Зміна спільного router/schema/prompt/privacy profile інвалідує всі залежні результати транзитивно.
