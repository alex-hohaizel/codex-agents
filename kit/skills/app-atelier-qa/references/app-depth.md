# Незалежне приймання App Atelier

Зміст: 1 — coverage; 2 — oracles; 3 — interaction matrix; 4 — production audit; 5 — findings та актуальність.
Прочитати cross-domain-core, чинні workflow/acceptance/evidence. `assets/app-depth.templates.json` задає план cases і evidence, не виконані результати. TEST-01–TEST-44 зберігаються; нові cases їх розширюють.

Для наскрізних app-specific контрактів застосувати [модель систем застосунку](app-system-contract.md); її requirements/state authority не дублювати.

## 1. Вивести достатнє покриття з моделі

Побудувати `requirement/source → domain rule → state/variant/platform → interaction → artifact → method/oracle → observer → due verdict`. Перевірити не лише присутність рядків: кожна продуктова обіцянка має здійсненний causal route, owner/consumer і належний доказ. Повні класи варіацій/життєвих циклів не підміняти трьома прикладами; комбінації відбирати за залежностями та ризиком, не механічним Cartesian explosion.

Must є hard gate. Weighted rank/кількість pass/гарний UI не компенсують privacy, data integrity, billing, scope чи release fail. N/A потребує предметного рішення про відсутність функції; missing SDK/account/device — blocked. Future proof має due owner/stage, поточний due must — фактичний pass/fail/blocked.

Author/reviewer IDs звірити з фактичними outputs. Один агент у двох ролях не стає незалежним. За недоступності іншого актора зберегти self-check, залишити independent gate відкритим і дати usable raw packet. Forward actor отримує звичайне завдання, skill і raw inputs; oracle/діагноз/fix залишити evaluator.

## 2. Перевірити правила незалежним методом

Для числового правила перевірити units, ranges, precision/rounding, ordered modifiers, snapshot/read time, null/default, exact error і golden vectors. Порівняти reference calculation з runtime без копіювання тієї самої помилки. Money/currency/scale, calendar/instant/timezone/duration, locale/encoding й ID formats мають explicit boundaries. Для ймовірнісного алгоритму за застосовності оцінити distribution/tails/failure, не тільки average.

Перевірити state machine transitions і invariants після success/failure/cancel/timeout/unknown/recovery. Forbidden transition має негативний case. Додати model-based/property/metamorphic/differential перевірки лише там, де вони мають змістовний oracle. Mutation або навмисно зламаний fixture має показати, що критичний case може спростувати обіцянку; test, який повторює implementation line-for-line, слабкий.

Метод і assertion мають відповідати claim. Schema/hash/format — structure/identity; unit — domain у контурі; sandbox — sandbox integration; E2E — exact scenario/environment; physical device — measured property на цьому device; official receipt/read-back — scoped external state. Жоден не доводить automatic human usability, market demand або revenue. Профільна заборона людських експериментів діє й на QA.

## 3. Пройти причинні взаємодії

Окремі компоненти можуть бути правильними, а спільне складання — хибним. Зафіксувати assembly source/build/config/component hashes, actual bindings, initial state/input/event order, expected observations/tolerances, target/modality й actor IDs. Пройти complete core Android/iOS/web та support за scope.

| Межа | Основні контрприклади |
|---|---|
| Input→command | Double tap, stale screen, invalid/large input, cancel до/після commit |
| Command→state | Duplicate/out-of-order event, revision conflict, partial effect, missing precondition |
| State→persistence | Process kill до/після durable boundary, disk full/corruption, duplicate recovery |
| Offline→sync | Concurrent edits, dependency queue, clock skew, account switch, expired command |
| Auth→data→UI | A/B tenant, cached/late response після logout/revoke, files/logs/support leakage |
| Checkout→entitlement | Pending, valid receipt, duplicate/reordered callbacks, cancel/expiry/refund/revoke, restore |
| Permission→feature | Denied/revoked permission, OS settings change, background/foreground |
| KB→support action | Wrong version/locale/price, injection, missing fact, unauthorized effect, stale link |
| Upgrade→recovery | Old schema/client, interrupted migration, rollback mismatch, deleted data resurrection |
| Build→runtime | Release-only stripping/config/signing mismatch, native callback threading, cold first use |
| UI→accessibility | Focus/back/keyboard/touch, text resize, reduced motion/mute, localization overflow |
| Service→budget | Quota/outage, retry storm, storage growth, cap, unresolved job cost |

Два однакові середні показники не роблять досвід однаковим: перевірити p95/p99/tail за доречності, error rate і worst-case input. Пороги обґрунтувати продуктом, аудиторією та вимірюванням. Simulator/emulator/browser/physical evidence не взаємозамінні.

## 4. Аудит виробництва та передачі

Звірити кожний output із bound recipe, input/tool/model/exporter/importer hashes, actual attempt і consumer. Параметр, якого схема не підтримує або модель не споживає, не закриває requirement. Descriptor/catalog/PATH discovery не є operation-tested/native proof. Editable master і runtime derivative мають окремі digests, права й transformation invariants.

На перетвореннях перевірити units/timezone/timebase, locale/text/colour/alpha, asset scale/anchor, IDs/money precision, compression/latency і event timing. Format-valid файл може втратити semantic property. Rights/source attribution і data egress перевірити незалежно від технічного формату.

Pending/unknown attempts не приховувати. Для timeout перевірити reconciliation route до повтору upload/deploy/payment/LLM job. Циклічні planned execution dependencies, missing consumers, outputs без recipe, dangling proof refs, stale hashes і fake provider IDs — окремі findings. Canonical state залишається єдиним authority; JSON templates/звіт не створюють новий status.

Work→Codex packet перевірити за manifest/digest/actual paths, доступним toolchain, exact launch/return commands і expected proof. Не довіряти старому переданому green verdict. Скрипт перевірки структури не запускає native build і не засвідчує волю користувача.

## 5. Finding, repair та closure

Finding записує ID/severity, requirement, current subject hash, raw reproduction/expected/observed, environment/actor, proven vs suspected, impact/transitive dependencies, repair owner і next validator. Root cause гіпотеза відділена від спостереження. Repair budget має cap, змінену змінну й stop; після двох однакових безрезультатних гіпотез змінити метод/діагностику.

Після fix повторити failed case і affected regressions. Не повторювати дорогі незалежні перевірки незачеплених outputs; carry-forward вимагає unchanged dependency digests, valid environment/permissions/terms та збереженого proof. Зміна source/model/SDK/importer/policy/KB/target відкриває транзитивно залежні докази. Старий proof не отримує вищого рівня лише від оновлення suite.

Підсумковий verdict містить кожний due must, actual method/result/proof, межі й next action. QA pass не є owner readiness decision або external effect grant. Закриття без фактичного current proof заборонене, навіть коли документація повна.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: звірка сирих вимог, незалежні сценарії/оракули, прив’язані до ревізії findings і висновок для кожного due must. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: адекватність оракула й компетенції перевіряльника, відсутні вимоги та реальні межі доказу. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
