# Game Atelier 4.0 — вхід, зрілість і навігація

Зміст: authority → компетенції → виходи → виконання → перенесення → докази.

## Authority й обсяг

Читай цей файл на вході нового scope. Чинний запит/згода користувача → прийнятий задум і constraints → project requirements/decisions → одна project-owned game model → specs/data/code/assets → actual evidence. `assets/approved-baseline-4.0.json` зберігає згоду на оновлення сімейства; вона не обирає гру, рушій, платежі або випуск. `assets/requirements-4.0.json` додає74IDs до GA3/UA26/попередніх IDs. Копіюй застосовні вимоги до чинної project registry з owner, artifact, acceptance, due gate, evidence і closure. Відсутня capability є blocked, не N/A. Не дублюй authority в таблиці або іншій DSL.

Для чинного проєкту зберегти його підтверджені керування, студію/IP, раунди, favorites, accepted originals/hash, платформи й performance targets. Джерело — актуальний project-owned profile/requirements/decisions. Для нового проєкту показати запропоновані defaults сімейства й предметно зафіксувати застосовні targets; конкретна історія не є новою згодою. Історичні приклади винесено до [профілів спадщини](../historical-project-profiles.md), які читаються лише за відповідним project scope. Favorites не є production choice. Обсяг нового раунду визначає поточний запит; оновлення агента не запускає раунд. Скінченний scope не дорівнює невичерпності всіх можливих ігор.

P1 defaults A–F: завершений кандидат має C1; authored/hybrid допустимі; функціональна покупка може давати прозору виміряну перевагу за доречного задуму; deterministic paid default/earned RNG transparent; paid RNG — окреме рішення; hidden DDA за успіхом/покупками не є default; network/social/backend/newpaidservice conditional. Не вводь повсюдний RPG, інвентар, бойові HP, ворогів, crafting або мережу.

## Метод, профіль і поточна задача

Загальні вимоги — повнота застосовного задуму, причинні правила й належний доказ. Жанр, камера, студія, бюджет, платформи, FPS, монетизація, участь людей та мережеві можливості — явні параметри конкретного профілю або його прийняті обмеження. Чинні погоджені targets не знімати через встановлення навички, відсутній SDK чи новий раунд. Пропозиція native Android/iOS або 60 FPS не є доказом їх прийняття новим проєктом. Зміна прийнятого scope має адресний impact/рішення й належний native upgrade шлях.

Перед матеріальним scope застосувати [адаптивну роботу](../adaptive-work.md). За необхідності викликати [дослідження, системний синтез або звірку](../research-and-synthesis.md) із власним output і evidence plan; постійний новий штат не потрібний. Локальна визначена правка має короткий шлях із targeted regression. Пізні must зберігати з due gate; перший working slice не викреслює повний target.

## Шість логічних компетенцій

Завантажуй потрібні файли за дією, а не весь корпус на кожну зміну. Це напрями роботи, не фіксований штат чи нові публічні навички.

| Компетенція P1 | Ресурси в цій навичці | Коли потрібні |
|---|---|---|
| Поведінка/математика/фізика/стан/RNG | [math](math.md), [systems](systems.md) | Правила, ресурси, damage/death/crash/contact, modifiers, симуляції |
| Каталог/сумісність/розвиток/винагороди | [catalog-progression](catalog-progression.md) | Сімейства можливостей, unlock, builds, sources/sinks, opportunity |
| Світ/ситуації/маршрути/AI | [world-ai](world-ai.md) | Генерація, агенти/боси, encounters, живість, ритм |
| Лор/сюжет/знання/діалог | [lore-narrative](lore-narrative.md) | Канон, reactive narrative, NPC knowledge, quests |
| Намір/touch/camera/UX/відгук | [experience-commerce](experience-commerce.md), старий [experience](../domains/experience.md) | Перший/peak/late досвід, gestures/cancel, tutorial, accessibility, multimodal |
| Метагра/економіка/commerce | [experience-commerce](experience-commerce.md), [catalog-progression](catalog-progression.md) | Fit моделей, комплекти, cumulative effects, store/ads/purchase lifecycle |

Наскрізні опори: [persistence](persistence.md) для будь-якого mutable state; [production](production.md) для кожної операції/перетворення й інструмента. Реєстр20систем та поля handoff — [systems](systems.md). Старі8domains зберігають предметні подробиці; новіpackуточнюють3.0, не скасовують незгадані must. Для чинного формату/CLI читай [model-format](../model-format.md); машинний checker не оцінює цікавість.

## Три виходи

**C0 — попередній ескіз.** Гачок/аудиторія/дія/основні системи/світ/розвиток/камера/input/art/commerce fit/ризики. Познач C0 незавершеним. Не називай його повною концепцією або accepted handoff. Не витрачай виробництво для маскування невизначеного задуму.

**C1 — завершена концепція.** Кожний кандидат, поданий як готовий до остаточного вибору, має повний продуктовий документ: фантазія/стовпи/межі,20застосовностей, причинні цикли й всі периферійні journeys, архітектура каталогів/сумісності/стратегій/прогресії, світ/новизна/повернення/живість, ризик/damage/failure/reward, AI або предметна N/A, controls/camera/навчання/accessibility, арт/аудіо по елементах і станах, комерційні альтернативи/free path/інфраструктура, persistence, finite launch/expansion/cost, ризиковіprobes і критерії відхилення. Числове налаштування може мати діапазон/метод/due; основний характер поведінки й ціль не лишаються TBD. Три екрани лише ілюструють пакет. Cold receiver відновлює сценарії без історії чату.

**T — виробнича передача.** Для вибраної в розробку гри: повний launch catalogue або точна grammar, typed rules/functions/tables/curves/state/priority/time/capture/round/tolerance/RNG, exact baseline та fixtures, generation constraints/repair/fallback, state/persistence/authority/migration, всі asset+audio+UI+locale states, source/export/import/scene recipes, кодові й platform contracts, budgets/devices, test oracles/negative cases/diagnostics, tasks/DAG/consumer acceptance. Немає невизначеного значення, яке змушує implementer самостійно придумати поведінку. Tuneableparameter має baseline/range/owner/criterion/affectedIDs. Product choice, tuning experiment та external permission — різні речі.

Ранній технічний spike дозволений до T для перевірки ризику; він не закриває пакет. Після T — representative native slice з фактичними input/camera/art/motion/contact/audio/haptic/save на declaredplatforms; лише потім masscontent. Бета/реліз потребують додаткових device/human/purchase proofs, а не довшого GDD.

## Алгоритм кожної задачі

1. Звір current intent, stop, IDs, inputs/hash, accepted originals, capability/permissions; визнач operation і current maturity.
2. Назви owned paths, consumer, observable result, boundaries, due evidence, budget; одного writer на спільний source/device/export/account.
3. Замкни requirements→20tracks→behavior/state/catalog→asset/code→scenario→build/release. Ребро пояснює конкретне читання/зміну/наслідок. Не вимагай all-to-all.
4. Для операції обери capability/recipe/semantic transformation/attempt/assembly records за [production](production.md). Descriptor/catalog/schema — лише факт доступності; потрібне фактичне parameter consumption.
5. Виконай дозволену роботу, збережи actual files/traces/receipts. Timeout external outcome спочатку reconcile, не repeat. Після двох однакових failedrepair зміни діагностику.
6. Перевір структуру, числові й semantic invariants, negative case та належну модальність. Інший actualactor перевіряє критичне; selfcheck не перейменовуй independent.
7. Consumer читає пакет без чату й відтворює expected scenario. Не підвищуй proof strength або охоплення. Запиши output/hash/status/gaps/nextaction.

Нормальний damage cue слідує за authoritative simulation resolution; disk/cloud durable commit окремий. Critical grant/spend/victory acknowledgement має явну durableboundary; не затримуй кожний hit звуком очікування cloud. Загальна simulationorder, save consistency groups та відповідні invariants узгоджуються.

## Продовження і зміни

Поточний toolkit **4.3.0** читає тільки game-model **4.0.0**; converter попередніх результатів відсутній. Для продовження віднови фактичні вимоги, рішення й матеріали продукту та створи поточний C0/C1/T contract. Не змінюй гру, дані чи saves встановленням навички. Handoff **1.0.0** та runtime state **2.0.0** — чинні незалежні протоколи з поточним toolkit marker.

Після зміни інвалідуй транзитивно залежні evidence за фактичними semanticinputs, версіями importer/model/recipe/build і dependencyclosure. Acceptedoriginal з незмінними bytes не генеруй повторно. Відсутнє ребро не виявляється магічно: integrator перевіряє closure.

Випуск/liveops спираються на exact signedbinary/config/contentepoch/schema/symbols/receipts та actualobservations. Очікування нових вказівок має checkpoint; без запущеного дозволеного scheduler/service не заявляй постійний monitoring. При новому зверненні звір поточний releasedstate й лише зачеплені вимоги.

## Межі доказів

Машинний PASS означає тільки перевірені структурні/арифметичні/byte/link властивості. Смислова повнота, чесність authorship/observations, ергономіка, художня якість, physicalfeel/fun/revenue мають окремий accountable review/дослід. Не підміняй прогалини загальним score. `quality_certified=false` лишається у звітах.
