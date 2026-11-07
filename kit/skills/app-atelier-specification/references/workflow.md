# Специфікуй предметний продукт

## Зміст

1. Зафіксуй baseline.
2. Побудуй предметну модель й core.
3. Визнач дані, identity та sync.
4. Обери архітектуру й залежності.
5. Опиши монетизацію, операції й залучення.
6. Сплануй обсяг, зріз і здійсненний реліз.
7. Достав пакет і керуй змінами.

## 1. Зафіксуй baseline

Прочитай `.appatelier/profile.json` та `.appatelier/state.json` за common contracts.
Використай typed registries requirements/decisions/knowledge/jobs/artifacts/evidence/executions/capabilities/grants/effects; не створюй паралельну пам'ять.
Візьми accepted concept з ID, revision, рішенням власника, evidence і hashes входів.
Витягни аудиторію, ринок/мови, recurring value, monetization hypotheses, операційну карту й acquisition route.
Не перезапускай пошук напряму через звичайне технічне питання.
Якщо потрібна зміна концепції, зафіксуй affected REQ-ID, наслідки й delta для рішення власника через директора.

Створи `spec-index.json`:

| Поле | Запиши |
|---|---|
| `spec_id/revision/status` | Задай ідентичність і draft/spec-ready/blocked/superseded. |
| `inputs` | Запиши exact path/ID, hash, revision і призначення входу. |
| `profile_version/requirements_version/decision_ids` | Зафіксуй джерела обмежень і згод. |
| `outputs` | Задай path, hash, evidence type, REQ-ID і owner кожного документа. |
| `gaps/blockers/recheck` | Назви невідоме, blocked action, due gate, owner й наступну перевірку. |
| `resource_cap/stop/checkpoint` | Задай межі проходу й відновлення. |

Розділяй факт, припущення й рішення. Мінливі API/ліцензії/ціни/platform rules перевіряй за чинною первинною документацією; зазнач URL, дату, версію, регіон і межу доступу.
Не виконуй live підключень, купівель або реєстрацій задля spec.
Без read-only доступу познач unknown і affected gate; не підставляй згаданий із пам'яті факт як verified.

## 2. Побудуй предметну модель й core

Створи `prd.md`: проблема, сегмент, контекст, корисний результат, recurring value, release scope й non-goals без вилучення must.
Задай success outcomes і technical indicators окремо; synthetic UX не доводить demand/willingness to pay.

Створи `domain-model.md`. Для кожного об'єкта запиши:

- Визнач ID, значення для користувача, source of truth і owner.
- Задай fields/types/units/constraints/default/nullability й validation.
- Опиши states/transitions: actor, guard, command/event, effect, resulting state.
- Задай invariants, relations/cardinality, терміни й delete semantics.
- Визнач duplicates/concurrency, time/timezone/expiry, retries і recovery/compensation.
- Додай valid/invalid synthetic records та boundary cases.

Опиши `RULE-ID`: передумова → рішення → observable result → відмова/відновлення.
Не залишай реалізаторам довільний вибір дозволеного переходу.
Для зовнішніх даних задай provenance/freshness/confidence і stale/partial поведінку.

Створи `client-core-matrix.md`. Розклади core на кроки першого запуску, отримання цінності, повторного використання й recovery.
Для кожного кроку визнач Android/iOS/web, shared rule, platform difference й acceptance ID.
Забезпеч самостійний повний core у кожному клієнті; не підміняй web лендингом, а iOS Android-тестом.
Не прирівнюй shared code до перевіреної поведінки всіх платформ.
Для істотних екранів/операцій задай loading/empty/success/invalid/permission denied/error/offline/stale/retry.
Передай experience терміни, hierarchy, content types, стани й обмеження; залиш design choice власнику.
Обґрунтуй OS/browser/device support, font scaling, keyboard/screen reader, contrast, input і performance budgets.
Оціни accessibility/старі пристрої/offline навіть без спеціального мінімуму в профілі.

## 3. Визнач дані, identity та sync

Створи `data-auth-contract.md` і schemas для усунення двозначностей.
Порівняй local без акаунта, optional sync/account і necessary cloud за функцією, витратами, правами й відновленням.
Рекомендуй достатній мінімум даних; не відкидай cloud автоматично й не обирай його мовчки.

| Аспект | Визнач для кожного поля/потоку |
|---|---|
| Значення | Тип, чутливість, owner/source, purpose й necessity. |
| Copies | Device/backend/vendor/backup/log/cache/index, включно з похідними. |
| Права | Actor/role, resource/action і server guard; окремо guest/account. |
| Передача | Recipient, transport, region за потреби, AI scope й redaction. |
| Lifecycle | Retention/expiry/export/delete/revoke, backup retention і restore semantics. |
| Gate | Source/decision, consent/config, test ID і specified/verified status. |

Для identity визнач necessity акаунта, guest lifecycle, sign-in/out, recovery, delete й device change за застосовності.
Для guest-to-account merge задай ownership proof, duplicate resolution, partial failure й safe retry.
Якщо акаунтів немає, обґрунтуй незастосовні branches; не додавай identity лише заради маркетингових даних.
Для backend визнач authz кожного resource/action, tenant boundary, replay/idempotency; не довіряй client-supplied user ID.

Для sync задай source of truth, revision/version, conflict detection/resolution, tombstones, retry queue і visibility pending changes.
Опиши offline create/edit/delete, concurrent edits, clock skew, stale cache й sync після тривалого розриву.
Не дозволяй старому backup/offline device відродити delete/revoked дані всупереч контракту.
Визнач schema migration, compatibility, rollback code/data, backup/restore acceptance і limits.

Специфікуй support окремо: public KB, власну guest session, дозволений account context і app/web і вибраний channel linking за його platform contract.
Вимагай server proof для identity/link, scope/expiry/revoke; не зв'язуй людей лише за username або user ID у тексті.
Задай dialogs/attachments/logs/indexes/caches/AI inputs/outputs окремими потоками.
Не перетворюй приватні звернення на public KB, training або unrestricted diagnostics.
Залиш initial support read-only; mutating scope вимагай окремо з auth/confirm/idempotency/receipt.
Залиш telemetry disabled/pending до event/property/purpose/consent/retention/cost gate.
Розрізняй operational signals, product analytics й intentional experiment; дозвіл одного не розширює інше.

## 4. Обери архітектуру й залежності

Створи `tdd.md`, `api-contracts/` і `dependency-options.md`.
Виведи architecture drivers із domain/privacy/offline/platform/cost/resource constraints до вибору framework/vendor.
Порівняй здійсненний baseline і сильного кандидата; не вигадуй штучні альтернативи заради кількості.
Розглянь native/shared/web технології за core; покажи components, ownership, interfaces, deploy units, trust boundaries і failure propagation.

Для API задай protocol/path/method, schema/validation, auth/authz, errors, pagination, rate/cost caps, timeout/retry/idempotency і compatibility.
Для event визнач producer, ID/schema/version, consumer, ordering/dedupe, out-of-order/poison handling і retention.
Не залишай retry зовнішнього ефекту без відмінності unknown outcome від safe repeat.
Для secrets визнач storage/injection/rotation без реальних значень у документах чи клієнті.

| Залежність | Порівняй |
|---|---|
| Потреба | Вкажи concrete value/quality boundary й варіант без постачальника. |
| Ціна | Задай setup/recurring/per-unit/overage, free limits, currency/date/tax assumptions і cap. |
| Права | Перевір commercial use/attribution/redistribution/derived data/cache/export/termination/platform restrictions. |
| Дані | Вкажи transmitted fields, retention, documented training policy, region/delete boundary. |
| Якість | Задай freshness/accuracy/latency/availability, uncertainty й unacceptable failure. |
| Відмова | Визнач quota/outage/stale/offline handling, fallback і visible limitation. |
| Заміна | Опиши portable schema/adapter, exit/export, migration effort і lock-in. |

Познач unknown price/license exact blocker або bounded assumption за наслідками, не verified факт.
Включи expected/low/stress usage, abuse/retry storms і runaway cost у cost envelope.
Для AI задай allowed task/data/effect, output validation, model failure/fallback і user/system caps.
Не гарантуй коректність зовнішнього результату лише через використання моделі/API.

## 5. Опиши монетизацію, операції й залучення

Створи `economics-operations-growth.md`; перевикористай accepted model і явно познач delta assumptions.
Залиш обрані й умовні free/paid/ads/module/subscription/usage/team/affiliate branches, не нав'язуй одну модель.
Визнач value, offer moment, price hypothesis, free/paid paths, costs/refunds і recurring sustainability.
Покажи operating profit як revenue мінус fees/refunds/infra/AI/API/data/acquisition/support/content/other operating costs.
Відокрем особисті податки й час власника; уникай double counting.
Покажи sensitivity conversion/retention/usage/refund/margin/vendor price; не видавай ціль за прогноз або гарантію.
Не фінансуй unbounded recurring costs one-time оплатою без caps/reserves/обґрунтування.

Створи `billing-entitlements.md` під обрану модель.
Задай paid product/provider identity, entitlement, scope/duration/units, source of truth, platform/region і portability limits.
Розділи purchase intent, transaction, verification, entitlement state й user-visible access.
Визнач застосовні pending/active/grace/expired/revoked/refunded/cancelled states; cancel не прирівнюй автоматично до expiry.
Задай provider validation/signature, dedupe key, replay, delayed/out-of-order resolution і authoritative reconciliation.
Опиши restore/new device, sign-out/in, guest linking, account recovery, offline allowance/expiry й crash після provider success до local record.
Покажи Android/iOS/web access matrix за чинними store rules; не обіцяй безпідставний cross-store transfer.
Визнач refund/chargeback/partial consumption/expiry/cancel за застосовності.
Для no-purchase запиши `not_applicable` для точних branches із причиною; збережи застосовні ads/affiliate/usage правила.
Визнач provider/sandbox tests для build/QA; не вимагай live purchase для приймання spec.

Побудуй operations map: trigger → job/tool → input/output → permission → cap → failure/retry → unresolved case.
Включи content/data refresh, moderation за потреби, support, incident triage, billing reconcile, backup, updates і vendor changes.
Для unresolved case задай ID, дозволені diagnostics/status і автоматичну технічну задачу; не вигадуй оператора/SLA.
За recurring manual flow поверни модель на перегляд; не приховуй щоденну працю власника як виняток.
Пов'яжи acquisition від zero audience з каналом, automated production/distribution, rights/cadence/cap/metric/stop.
Передай growth plan до full build; activation залиш після actual product й окремого gate.
Не запускай повідомлення, outreach, ads, публікації або schedules у цій фазі.

## 6. Сплануй обсяг, зріз і здійсненний реліз

Створи `scope-estimate-roadmap.md`; порівняй завершений core і ширший scope за тими самими ресурсами й часовими припущеннями.
Розбий варіанти на work packages Android/iOS/web/backend/data/design/support/QA/release/operations.
Задай effort ranges, critical path, integration effort, unknowns, buffer й host/resource caps.
Доведи reuse конкретними components/licenses/readiness; generated code не прирівнюй до integration-ready.
Якщо wider scope подовжує строк або знижує якість, назви це й поверни вибір власнику.
Не вигадуй deadline: використовуй profile або range із dependencies.

Створи `representative-slice-plan.md` за найбільшим архітектурним ризиком.
Включи реальний core path через потрібні layers: client/domain/persistence/sync/API/permission/recovery; paid path додай, якщо він критичний ризик.
Задай fixtures, цільові environments/clients, inputs, observable output/oracle, threshold, failure injection, cap і stop.
Включи найдорожчу/найневідомішу dependency і безпечний спосіб перевірки без live ефекту за можливості.
Передай виконання build як bounded slice job до full build; не реалізовуй продукт у spec-завданні.
Залиш `slice_planned`, доки не отримано actual artifacts/logs/tests; план не є working slice.

Створи `release-feasibility.md` із release-навичкою до production scope/значного build.
Перевір dated primary rules/fees, routes Android/iOS/web, developer account type/status/access, ownership, signing/build host, testing/submission/privacy/commercial prerequisites.
Без read-only account evidence познач `unverified`; не називай його готовим.
Покажи mandatory fees, обладнання й recurring costs навіть за zero-new-spend profile.
Зістав required humans/testing з no-human invariant; не рекрутуй людей і не симулюй їх.
Для MFA/payment/signature/legal decision назви exact external prerequisite й blocked effect.
Дай allowed route, scope/time/budget delta для власника або stop; не обходь conflict.
Задай `recheck_due: before-release` для rules/prices/accounts/signing/testing і event-trigger при зміні platform/account/model.

| Gate | Вимагай |
|---|---|
| `spec-ready` | Вимагай concrete contracts, estimates, due checks і відсутність spec blockers. |
| `before-full-build` | Вимагай accepted scope/design, economics/operations/acquisition, cap, early feasibility й actual slice. |
| `before-release` | Вимагай actual client/support/billing tests, current prerequisites, data/brand/model decisions і owner readiness/effect. |

Не вимагай готового продукту для spec-ready; зовнішню unresolved feasibility залиш blocker залежної production дії.
Не надавай spec-ready за невизначених предметних правил, due spec must або критичного рішення spec.

## 7. Достав пакет і керуй змінами

Збережи результати у `project/specification/`; за малим scope об'єднуй files зі збереженням named sections і trace IDs.
Створи `acceptance-matrix.md`: REQ-ID → concrete artifact/rule → platform/model applicability → test/fixture → due gate → evidence/status → blocker/owner.
Для REQ-11/REQ-16/REQ-19 запиши предметні перевірки, додай ранній REQ-38 й наскрізні must.
Залиш future build/QA/release acceptance `specified_not_implemented` або відповідним common статусом; не став passed за описом.
Для `not_applicable` зафіксуй причину/scope/decision; не використовуй для обходу must.
Передай experience стани/терміни, build rules/schemas/API/slice, support data/auth/KB, QA fixtures/oracles, release recheck, growth/operations costs/jobs/caps.
Додай exact inputs/outputs/hashes, decisions, evidence limits, blocked gates, stop й точну наступну дію за handoff-contract.
Для зміни object/data/API/paid rights/platform задай change ID, affected REQ-ID, consumers, invalidated evidence і recheck.
Не повторюй неушкоджені перевірки без причини й не приховуй вплив на строк/ціну/згоду/release.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: предметна модель цілого й компонентів, мови/стек та ADR за потреби, точні правила/контракти, fixtures і due acceptance. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: семантична повнота, архітектурні компроміси, реальна здійсненність і відсутні залежності. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
