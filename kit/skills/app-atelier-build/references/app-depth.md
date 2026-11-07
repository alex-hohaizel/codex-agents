# Виробнича глибина реалізації App Atelier

Зміст: 1 — обсяг; 2 — предметні правила; 3 — дані й синхронізація; 4 — production; 5 — складання; 6 — передача.
Читати разом із чинними workflow/acceptance, cross-domain-core та [моделлю систем застосунку](app-system-contract.md). Цей документ задає належну роботу, а не звітує про виконані builds. `assets/app-depth.templates.json` — шаблони для project artifacts, посилання на які реєструються у canonical state; вони не замінюють його.

## 1. Перетворити обіцянки на повний обсяг

Побудувати inventory `requirement → use case → state/variant/platform → rule → output → consumer → proof`. Для кожного класу описати генеративне правило варіацій і крайні значення; кілька красивих екранів не закривають усі стани. Обсяг продукту включає loading/empty/invalid/permission denied/offline/conflict/pending/revoked/upgrade/resume, локалі, text scale й доступні методи вводу за застосовності. Відсутність інструмента — blocked, предметна відсутність функції — обґрунтоване N/A.

Задати відповідального за кожний модуль і output. Розділити domain rules, immutable definitions, mutable state, storage/network/platform adapters і presentation за причинами зміни. Архітектурні патерни обирати за конкретним coupling/risk; не підключати одночасно microservices/DDD/CQRS/event sourcing лише за назвами. Складна фінансова чи професійна область потребує відповідного предметного спеціаліста й джерел, а не вдаваної сертифікації AI.

Для ризикової бібліотеки або можливості перевірити точну операцію: фактичні version/platform/host, accepted inputs, supported parameters, editable outputs, права/дані/витрати, probe та відомі втрати. Наявний CLI або опис plugin не доводить імпорт, native callback чи працездатну інтеграцію.

## 2. Формалізувати й реалізувати кожне правило

Предметний контракт має input types/units/ranges/null semantics, preconditions/authority, момент читання параметрів, ordered calculation, rounding/precision, output, state transition, error/cancel/timeout, deduplication й invariant. Визначити, які значення фіксуються на початку операції, а які читаються при commit. Ціна зі старого екрана не повинна мовчки стати новою; policy визначає revalidation і повідомлення користувачу.

Числові правила перевірити незалежними golden vectors і граничними прикладами. Гроші не зберігати неявним binary float без обґрунтованої моделі; назвати валюту/масштаб, порядок знижки/податків/комісії й округлення. Calendar date, timezone, instant і duration не зливати. Для строків і повторів визначити clock ownership, DST, monotonic deadline, порядок одночасних подій і політику зміни часу пристрою. Для ймовірнісного алгоритму за застосовності визначити distribution/seed scope та метрики розподілу; середня latency чи точність не приховує tail/failure rate.

Команда користувача, transport event, durable operation і UI notification мають різні IDs і межі. Один tap/повтор callback не означає нову бізнес-операцію. Задати `command_id`, `entity_id`, `revision`, `operation_key` і retention deduplication. API retry не створює exactly-once без provider-supported identity та reconciliation.

Додати failure lifecycle, а не лише exception handler: created → validated → pending → committed/failed/unknown → reconciled/compensated за предметною потребою. Cancel request не означає скасований effect. Для багатокрокової операції визначити point of no return, partial result, compensation ownership, retry boundary і те, що compensation не може відкотити.

## 3. Дані, sync та continuity

Кожне поле отримує stable ID, type/unit, default, owner/authority, source, persistence class, schema version, privacy scope, retention/delete rule й migration. Розділити definition/reference data, user/session state, transient presentation і derived cache. Derived state перебудовується лише з дозволених актуальних джерел.

Для consistency group назвати atomic boundary та commit acknowledgement. UI може показати локальне прийняття, server confirmation чи queued status лише з відповідним формулюванням. Не чекати хмари для незалежного локального feedback; незворотне підтвердження покупки/права/нагороди має належну durable межу. Storage full, write interruption, corruption, process kill і restore отримують точні очікувані наслідки.

Offline queue має durable identity, ordering/dependency, cap, expires_at, account binding і pending UI. При переході A→B не відправляти A-команди як B. Conflict policy задається по полю/операції: version precondition, merge, authoritative replacement або explicit conflict; last-write-wins не є універсальним рішенням. Clock skew не повинен робити довільний client timestamp вищою владою.

Delete/revoke/tombstone покоління переживають повтор і backup restore; старий snapshot не відновлює заборонені записи або права. Перевірити upgrade з реальних попередніх schema versions і двосторонню сумісність code/data до rollback. Migration повторно запускається лише за її точним контрактом, не через generic retry.

## 4. Виконати рецепти й перетворення

Для кожного виробничого output підготувати bound recipe: accepted input hashes, компетенція/owner paths, exact toolchain, argv array/API fields/numbered GUI steps, DAG, outputs/editable masters, consumer bindings, validators, cost/time cap, fallback і stop. Template із невідомими bindings не виконувати як готову команду.

Матеріальні параметри звірити `requirement → schema field → actual support → consumption proof`. Для AI-generated source/asset зберегти accepted original, editable source і runtime derivative окремо. Ліцензія інструмента не передає права на шрифт, sample або input. Аудіо/анімацію/UI імпортувати з event/time/scale/colour/encoding контрактом, не тільки шляхом до файлу.

Перед costly/external операцією створити pending attempt з input/toolchain/recipe hashes і stable key. Після submission зберегти actual job/request ID, спостереження, витрати, output hashes та receipts. Timeout — unknown; спершу з’ясувати існуючий результат/вартість. Зміна prompt без нової гіпотези не є причинним ремонтом. Після двох однакових невдалих гіпотез змінити діагностику/метод або залишити точний blocker.

Cache включає inputs, recipe/tool/model/exporter/importer versions, target profile, parameters, права й data scope. Зміна SDK відкриває залежний derivative/proof; accepted master не переписується. Не переносити чужий device proof на новий platform build.

## 5. Прийняти спільне складання

Зафіксувати exact source/build/config/component hashes, runtime bindings, initial state, scenario/actions, expected invariants/tolerances, platform/device/modality та actor IDs. Пройти `input → rule → state/storage/provider → UI/accessibility → support → restart/resume`. Репрезентативний зріз включає найбільш ризикову взаємодію, accepted assets і цільовий клієнт.

Перевірити одночасні submit/cancel, timeout із фактично committed effect, permission revoke під час роботи, offline→online, account switch, schema upgrade, delayed notification, quota cap, cold start і peak load. Для billing додати sandbox receipt, restore, duplicate/reordered/refund/expiry та узгоджені cross-client права. Для UI перевірити keyboard/touch/back/focus/text scale/reduced motion/mute за застосовності.

Виміряти budgets у точному сценарії: startup/latency p50/p95/p99 за доречності, memory, storage growth, network/cost та background work. Числові пороги вивести з аудиторії та продуктового результату, не копіювати game FPS. Compile, emulator/simulator, browser E2E, physical device і live service proof — окремі факти.

## 6. Передати без прихованих залежностей

Надати spec/rule fixtures, source/builds, lockfiles/config, editable assets і rights, migrations/recovery, operation attempts, assembly evidence та open due gates. Команди й paths перевірити у фактичному пакеті. Передати raw inputs/outputs незалежному QA без бажаного verdict. Незмінний proof переносити з dependency justification; зміна canonical intent/input/model/toolchain відкриває лише залежний scope.

Сам текст рецепта, JSON validity і unit pass не доводять реальний Android/iOS/web або released product. Неперевірене залишається pending/blocked з owner, середовищем та exact next action.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: працюючий погоджений зріз або зміна, рішення щодо технологій за фактичними обмеженнями, точний diff/build і належні перевірки. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: цілісність інтеграції, коректність і ризик змін, відповідність accepted design/spec. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
