# App Atelier: виконувана специфікація

Зміст: domain model → межі взаємодій → exact rules → state → production handoff → приймання.

## Єдиний предметний контракт
Читати `cross-domain-core.md` і `app-system-contract.md`; конкретизувати всі required tracks із accepted concept, не додавати непогоджених продуктів. Призначити requirement→rule/state→API/UI→operation→recipe→output→test→consumer. Наявність розділу в PRD не закриває requirement: дати спостережуваний критерій і due evidence. Не вимагати готового binary на spec gate; не називати spec production proof.

Кожна entity/definition/instance має stable ID, owner/tenant, типи/units/ranges, semantic null/default, mutability, version, authority і access policy. Дані від клієнта не визначають tenant/auth identity. Для command описати actor/input, auth/preconditions, validation order, момент читання значень, atomic group, next state/events/response, idempotency/effect identity, errors, cancel/timeout/reconcile, durable acknowledgement. Типова таблиця error містить code, retryability, user message, state change, telemetry без sensitive values і support path. API/network timeout не означає command absent.

## Правила й комбінації
Формули, таблиці, curves і правила композиції мають exact order/units/rounding/clamp/capture/tie-break. Приклад: quota availability, purchase entitlement і account role перевіряються визначеною authority/ревізією; не зводити різні рівні доступу до одного boolean. Для часових правил вказати calendar/timezone/DST або elapsed clock, expiry semantics, clock rollback/jump policy. Випадковий/AI output визначити як діапазон дозволених results, модель/version/параметри, validation/fallback і cost cap, а не «якісна відповідь».

Catalogue coverage включає повний launch set або точну grammar, prerequisites/exclusions/compatibility, ownership, entitlement, migrations і aliases/removals. Interaction matrix фіксує які системи читають/змінюють стан інших та наслідок; не all-to-all. Цикли feedback у продукті можливі, execution plan — DAG із bounded repeats. Cascading events мають termination/budget/dedup, щоб не отримати нескінченний запуск notifications чи генерацій.

## Стан і persistence
Для field: scope/lifetime/authority/serialization/consistency group/commit trigger/recovery/retention. Розділити optimistic UI, local committed, pending remote, synced/conflict/error. Restore pipeline та migration зберігають original і previous-good; unknown newer schema не reset. Визначити допустиму втрату даних і підтвердження для critical spend/grant/user work. Offline/local-first route порівняти з мінімальним альтернативним; cloud не типова вимога.

Для sync: conflict detection, revision ancestry, causal merge policy per entity/command, idempotent replay, owner/session binding, tombstones, quota/retention, cancel/revoke/restore. Не використовувати universal max/sum/latest timestamp для незалежно витраченого ресурсу. Adapter має typed native callbacks/thread/lifecycle/account transitions; late callback не змінює нову session. Backup, cloud sync, transfer і purchase restore — різні interfaces.

## Наскрізна production передача
Повний inventory: client screens/states/accessibility/locales, data/schema/migrations, domain/API/native adapters, conditional commerce/support, content/media, CI/build/config/symbols/release і ops jobs. Для кожного — exact producer/consumer format, editable source, tool capability/schema/parameter proof, pinned compatible toolchain і ordered recipe. Довести semantic transforms: timezone/date, currency/precision, enum/null/ID, font/density/locale, callback/thread/account, source/export/import. Не нав’язувати framework/DDD/CQRS/ECS/DI/microservices лише за модністю; вибрати мінімальну достатню структуру за причинами змін/ризиком/measurement.

Test design має shared domain fixtures для всіх погоджених clients, negative/boundary/property tests за користю, adapter conformance, persistence fault corpus, accessibility/performance/security і exact assembly scenario. Для кожного oracle — initial state, action, expected intermediate/final values, tolerance, diagnostics і належний evidence level. Обіцянку «швидко» замінити target/percentile/device/data/load/measurement; числа визначаються продуктом, не копіюються з гри.

## Передача без вигадування downstream
Використати assets/app-depth.templates.json як форму specification contract. Шаблон лишається template до project binding. Незалежний receiver має з документа відтворити core/edge/recovery story й test outcomes; критичні unresolved values блокують залежний build node. Відділити tuneable baseline/range/owner/acceptance від critical unknown. Передати build/support/experience/QA/release exact versions, accepted masters, current constraints, capabilities/probes, due gates і next action. Зміна upstream інвалідує тільки залежну closure.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: предметна модель цілого й компонентів, мови/стек та ADR за потреби, точні правила/контракти, fixtures і due acceptance. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: семантична повнота, архітектурні компроміси, реальна здійсненність і відсутні залежності. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
