---
name: gamedev-preproduction
description: "Game Atelier: розгорнути обрану концепцію в повний узгоджений GDD/TDD і спільну модель гри — механіки, камера й керування, противники та світ, предмети й здібності, прогресія, винагороди, навчання, художні й комерційні контракти, дані та перевірюваний виробничий план Android/iOS. Використовувати для нового дизайн-пакета, його ревізії, усунення суперечностей або передачі до assets/build без втрати прийнятого задуму. Замикати виробничий T: точні damage/physics/AI/save правила, каталоги, ресурси, рецепти й незалежні oracles."
---

Відповідати за T: усі застосовні системи погодженого запуску, їхні точні правила, дані, каталоги, переходи, ресурси й незалежні oracles. Consumer assets/build не повинен самостійно вигадувати відсутню продуктову поведінку.

## Виробнича якість і контекст6.0

Для нового, делегованого чи відновленого task застосувати [контекст виконання](references/context-capsule.md): current native sources/requirements/identity/authority, усі застосовні must та їхні залежності, exact inputs, outputs/consumer, budget/stop і належне приймання. Optional `scripts/context_capsule.py` компілює заявлену проєкцію, не створює згоди чи сертифікації.

Перед створенням або зміною матеріалу прочитати застосовний [виробничий контракт](references/production-quality.md) і medium profile з `assets/production-profiles.json`. Зберегти визначальні властивості референсу — композицію, масштаб, виразний механізм, взаємодію й функціональну глибину; палітра/назви елементів самі не доводять fidelity. Спершу довести representative slice на actual носії, потім тиражувати. Creative, functional, source/runtime та owner verdicts окремі. Пряме доручення й надана творча свобода сильніші за own defaults; прийняту identity не змінювати заради різноманіття.

## Контракт 4.0 та предметне завантаження

Перед новим scope прочитати [вихід і приймання цього маршруту](references/v4-route.md). Звірити maturity **C0 / C1 / T** окремо від фактичного implementation stage. C0 — позначений ескіз; C1 — повний задум кожного представленого завершеного кандидата; T — точний виробничий контракт прийнятої до розробки гри. Ранній обмежений spike дозволений до T; він має питання, inputs, oracle й межу, а не статус готової реалізації.

Шість логічних компетенцій P1 завантажувати за предметом, а не як шість додаткових етапів:

| Компетенція | Точний ресурс |
|---|---|
| Поведінка, математика, фізика, стани, RNG | [Math](references/v4/math.md) |
| Каталоги, сумісність, комплекти, розвиток, винагороди | [Catalogs/progression](references/v4/catalog-progression.md) |
| Світ, генерація, маршрути, encounters, ритм, AI | [World/AI](references/v4/world-ai.md) |
| Лор, знання, сюжет/діалоги, реактивний канон | [Lore/narrative](references/v4/lore-narrative.md) |
| Намір, touch, камера, UX, навчання, мультимодальність | [Experience](references/v4/experience-commerce.md) |
| Метагра, економіка, монетизація, магазин, платежі | [Commerce](references/v4/experience-commerce.md) |

Наскрізно підключати [Persistence](references/v4/persistence.md) для state/continuity й [Production](references/v4/production.md) для операцій/ролей/recipes/доказів. Логічний поділ компетенцій не вимагає одного файла або одного агента на кожну. Source IDs й accepted masters зберігати. Для продовження відновити фактичні вимоги, рішення й матеріали продукту та створити поточні contracts; попередні формати результатів не читати й не конвертувати.

Для активних систем вести один зв’язок requirement → rule/state/catalog → production operation → consumer → scenario → actual evidence. Перевіряти застосовність усіх 20 виробничих напрямів; не вимагати 20 окремих документів чи агентів. Missing tool/device — блокер належного доказу, а не `absent_by_design`.

# Game Atelier 6.0.0 · Дизайн

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Версія навички **4.0.0**.

Перетворювати прийнятий задум на конкретну цілісну гру в погодженому scope. Основне середовище — Codex з canonical project; Work підтримує дослідження, творчі порівняння й доступні модальності через точний bridge. Назва середовища не доводить наявність SDK, генераторів, пристроїв або прав.

## Вхід та спільна модель

Це предметна навичка єдиного `gamedev-director`. Перед залежною роботою прочитати [unified-agent](references/unified-agent.md), [core](references/core-contract.md), [experience](references/experience-contract.md), [systemic](references/systemic-design.md), [вимоги](references/requirements.md), [handoff](references/handoff-contract.md) і [workflow спільної моделі](references/game-model-workflow.md). Формат записів та перевірку визначає [model-format](references/model-format.md). Версія навичок 4.0 не змінює самостійно чинні handoff 1/runtime 2; не ініціалізувати повторно існуючий project state.

Прийняти actual latest files, рішення, первинні зауваження, паспорти кандидатів, accepted originals/hash, knowledge, відкриті ризики та user-defined stop. Saved favorite, recommendation, visual proposal, selected concept і production permission мають різні значення. Не починати повний дизайн невибраної гри замість аудиту або візуального відбору.

Спільна модель — джерело IDs, правил, залежностей і статусів; GDD/TDD, картки, таблиці та runtime config є узгодженими поданнями. Не вести другу незалежну «правильну» прогресію в PDF. Старі дані зберігати з походженням; мігрувати через явний mapping. Стартові `assets/domain-templates/` є draft forms, а не готовою моделлю чи доказом виконання.

## Читати предметно

- [Вхід і рішення](references/intake-decisions.md) — intake та material change.
- [Виробничі дані](references/design-data.md) і [design→runtime mapping](references/design-runtime-mapping.md) — до декомпозиції та handoff.
- [Systems](references/domains/systems.md), [world](references/domains/world.md), [progression](references/domains/progression.md) та [прогресія/контент](references/progression-content.md) — причинні механіки, актори, предмети, світ, винагороди й довга арка.
- [Experience](references/domains/experience.md) і [UX states](references/ux-state-machines.md) — camera/input/HUD, навчання й весь шлях гравця.
- [Creative](references/domains/creative.md) і [fidelity/slice](references/fidelity-slice.md) — конструктивний стиль, motion/audio/haptics і здійсненний reference.
- [Commerce](references/domains/commerce.md) та [economy](references/economy-commerce.md) — fit моделі доходу, баланс і магазин.
- [Lifecycle](references/domains/lifecycle.md), [архітектура](references/engineering-architecture.md) — save/offline/platform/performance/support.
- [Приймання](references/design-acceptance.md) — перед freeze; [agents/context](references/agents-context.md) — ownership та незалежний review.

Локальний ремонт читає актуальні зачеплені розділи й транзитивні залежності. Не завантажувати всі довідники повторно на кожну правку. Дослідження аналогів виконувати за [research](references/domains/research.md), розрізняючи офіційне обмеження, практику студії, власний висновок і неперевірену гіпотезу.

## Порядок роботи

1. **Заморозити вхід і знайти конфлікти.** Зберегти studio context, обрану концепцію, усі retained/rejected рішення й точні творчі originals. Для кожної слабкості визначити retain/repair/test/branch/reject, owner, залежності та closure. Невідома деталь не перетворюється на універсальний engine, RPG-прогресію або один stylized preset.
2. **Погодити тільки матеріальні розвилки.** Взяти чинні платформу/аудиторію/бюджет/стиль/керування/offline/монетизацію з джерел. Для справді відкритої розвилки дати здійсненні альтернативи, sample й наслідки до залежної реалізації. Рутинні рішення в прийнятому envelope виконувати самостійно; незалежні гілки не блокувати.
3. **Визначити повний продукт.** Зафіксувати finite launch scope, змістовне завершення/післягру й довгу еволюцію. Відокремити виробничу вартість, просторову структуру й тривалість досвіду: мала гра не обмежується примітивною ареною, великий світ не виправдовує порожнечу. Кожний елемент має роль у загальній системі.
4. **Побудувати причинні контракти.** Описати states, guards, дії, витрати, transforms, порядок розрахунків, наслідки, feedback, reset/persistence та counterplay. Зв'язати інструменти/навички/ресурси з умовами світу й поведінкою акторів. Показати, як одна система змінює рішення в іншій; кількість механік не доводить глибини.
5. **Розгорнути весь розвиток.** Спроєктувати mastery/run/persistent/world layers лише за fit. Для кожного unlock визначити нову можливість, застосування, комбінації, обмеження, зрозумілу наступну мету й переосмислення знайомого виклику. Винагороди мають grant, цінність, спосіб використання та persistence. Нові стати без зміни досвіду не замінюють прогресії.
6. **Зв'язати видимість, керування й навчання.** Задати gameplay camera як поведінку в часі, масштаб керованого об'єкта на телефоні, потрібну дистанцію реакції, framing/occlusion та aspect rules. Обрати input grammar для механіки, two-thumb concurrency, cancel/error/recovery і feedback. Навчати через безпечну дію, застосування, комбінацію та самостійний перенос знання; не показувати всі системи одним туторіалом.
7. **Побудувати весь шлях гравця.** Задати reachable screens/states/переходи від launch до гри, прогресу, нагород, оснащення, магазину, помилки, збереження й повернення. Для UI/HUD ресурсу визначити, яке рішення він пояснює, як змінюється/відновлюється та не перевантажує кадр. Описати відмову від покупки й функціональний базовий шлях.
8. **Уточнити художнє виробництво.** Перенести exact reference у constructive style/camera/material/light/type/motion/audio/haptic contracts та finite asset scope. Для кожного функціонального стану потрібний source/clip/cue/UI consumer. Перевірити operation-level production route, editable sources, права, export/import і runtime budget; не обіцяти mesh/rig/stems з одного растра.
9. **Виконати моделі й ранню перевірку ризику.** Запустити потрібні numeric/content/economy simulations із config/version/seeds/raw outputs. Малий PoC перевіряє конкретне припущення. Доручити assets/build representative native slice з найризиковішою системною взаємодією, реальним craft, camera/input, HUD, sensory feedback, save/recovery. Недоступний device лишає названий блокер; mass production не починати на непідтвердженому критичному маршруті.
10. **Замкнути залежності й передати.** Зіставити модель→GDD/TDD→production items→runtime bindings→design-derived tests. Незалежний reviewer перевіряє реальні артефакти й контрприклади. Consumer assets/build відкриває пакет і підтверджує, що не мусить заново придумувати правила. Після pause/stop зберегти checkpoint і не відкривати наступні jobs.

Для кожного перетворення spec→source→export→runtime зафіксувати збережені semantic properties і допустимі втрати. Damage/physics/lifecycle, State Catalogue, consistency groups, production operations/recipes/attempts та cross-system oracles — застосовні частини T, не необов’язковий додаток після реалізації; точний склад у [контракті 4.0](references/v4-route.md).

## Контракти та перевірка за напрямами

| Напрям | Що довести до design freeze | Що потребує пізнішого фактичного доказу |
|---|---|---|
| Камера/стиль | Camera states/переходи, object screen-size envelope, focal hierarchy, aspect/occlusion; distinct constructive art direction | Actual phone-scale frames і motion, source→native parity |
| Керування/gamefeel | Gesture ownership, одночасні дії, thresholds, latency targets, cancel/buffer/assist, feedback | Touch latency, comfort та reduced-motion на пристроях |
| Actors/world | Поведінки/намір/пам'ять/telegraphs/counters; topology, routes, materials, події, constraints | Actual encounter behaviors, fairness/solvability і семантична різниця |
| Предмети/здібності | Units/formulas, stacking, caps, synergies/exclusions, acquisition/upgrades, runtime authority | Сценарії dominance/exploits і зміна рішень у грі |
| Прогресія/винагороди | Unlock graph, grant semantics, early/mid/late/postgame journeys, повернення й exhaustion | Human comprehension/mastery/мотивація; retention тільки фактичними спостереженнями |
| Навчання/UX | Learn→practice→combine→transfer, triggers/skip/return; весь state graph і accessibility | Незнайомий гравець розуміє й застосовує можливості без підказки автора |
| Економіка/магазин | Model fit, concrete offers/grants/caps, free/paid journeys, cumulative portfolio, failure/refund/restore | Sandbox transactions, actual cohort/доходи; simulation не є попитом |
| Production/platform | Sources/rights/assets/events, finite inventory, TDD/budgets/save/migrations, named devices/toolchain | Reopen/export/import, audio listening, tactile feel, native/thermal/clean-build receipts |

Усі застосовні вимоги зберігати з source ID, owner, due gate і доказом; `absent_by_design` обґрунтовувати конкретною грою. Не додавати ворогів, інвентар, валюти, backend або нескінченні сезони лише для заповнення форм.

## Команда й вихід

Оркестратор інтегрує; предметні автори створюють gameplay/systems/world, progression/economy, experience/creative, runtime/platform contracts. Розподіляти реальні deliverables і файли у фактичному ліміті слотів, без порожніх менеджерських поверхів. Незалежне приймання виконує інший actual actor; self-check називати self-check. Після двох однакових невдалих repair змінювати діагностику.

Пакет містить current model і його version/hash, exact upstream/studio payload, GDD/TDD та derived data, acceptance scenarios, creative originals/construction specs, finite asset/event/screen inventory, costs/rights/capability map, actual PoC/slice evidence, requirement coverage, рішення, issues/owners і next action. Перед запуском структурних інструментів відкрити actual `scripts/game_model.py --help` та `scripts/pipeline.py --help`. Перевірити модель через `python3 <SKILL_DIR>/scripts/game_model.py validate /absolute/model.json --stage preproduction`; зміни аналізувати через `impact MODEL --changed ID` за actual help. Не вигадувати прапорці. Структурний pass не засвідчує fun, баланс, fidelity або user acceptance.

Design complete T означає замкнений погоджений scope: усі застосовні алгоритми, каталоги/граматики, data, states, exceptions, ресурси, операційні recipes, fixtures й receiver review; невизначений behavior блокує залежну передачу. Вироблені assets, built/installed/device-tested, independently accepted, released і observed лишаються окремими станами з фактичними доказами. У фіналі назвати завершене, перевірене, блокери та точну передачу; не запускати іншу гру, зовнішню оплату чи публікацію замість цього доручення.

Версія інструмента: **6.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
