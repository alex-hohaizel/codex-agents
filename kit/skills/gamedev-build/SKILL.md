---
name: gamedev-build
description: "Game Atelier: реалізуй або продовжуй нативну мобільну гру за прийнятою моделлю систем, GDD/TDD і production assets. Використовуй для gameplay, AI/світу, camera/input/gamefeel, UI/навчання, progression/rewards/economy, магазину, save/offline, Android/iOS та ремонту. Зберігай творчий задум, canonical data й lineage; доводь результат реальними збірками та передавай на незалежне QA. Реалізовувати точні damage/physics/lifecycle та state-continuity контракти, перевірені native adapters і збірку систем."
---

Відповідати за виконану поведінку і збірки: типізовані правила й дані, engine/native adapters, збірку систем, save/recovery та точні докази. Відсутній design contract повертати предметному власнику, а не вигадувати його між рядками коду.

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

# Game Atelier 6.0.0 · Реалізація

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Працювати українською як предметна гілка `gamedev-director` (остання актуальна версія). Створювати виконану гру в погодженому scope: source/data/assets, native artifacts, receipts і handoff. Основне середовище — Codex із actual toolchain/devices; Work — research/creative/inspection bridge. Назва host не доводить engine/Xcode/generator/device access.

Зберігати handoff protocol **1.0.0**, runtime state **2.x**, project IDs/рішення/originals. Версія моделі гри не мігрує old state/save автоматично. Не підміняти accepted rules/style/camera/масштаб «простішим MVP» без матеріального user decision.

## Intake та джерела

Перед залежною роботою прочитати [unified intake](references/unified-agent.md), [core](references/core-contract.md), [handoff](references/handoff-contract.md), [requirements](references/requirements.md), [experience](references/experience-contract.md), [systemic](references/systemic-design.md), [game model workflow](references/game-model-workflow.md) і [model format](references/model-format.md). Звірити current files/decisions/knowledge/hashes/tasks/owners, доступи/ресурси та stop boundary. За локального repair читати лише зачеплені зрізи після визначення впливу.

| Scope | Прочитати до реалізації |
|---|---|
| Rules, actors, equipment/resources | [Systems](references/domains/systems.md) |
| Локації, encounters/routes/variation | [World](references/domains/world.md) |
| Unlocks, growth/rewards/long arc | [Progression](references/domains/progression.md) |
| Camera/input/HUD/onboarding/flows | [Experience](references/domains/experience.md) |
| Style/motion/audio/haptics | [Creative](references/domains/creative.md) |
| Economy/shop/IAP/ads | [Commerce](references/domains/commerce.md) |
| Save/offline/backend/operations | [Lifecycle](references/domains/lifecycle.md) |

Предметні посібники: [production plan](references/intake-production.md), [runtime architecture](references/runtime-architecture.md), [model→runtime bindings](references/model-runtime-bindings.md), [systems/economy/save](references/systems-economy-save.md), [feature DoD](references/feature-dod.md), [native builds](references/native-builds.md), [delivery](references/delivery.md).

## Єдина модель та виконувані дані

Прийняти maturity T (або explicit bounded spike), current model objects/IDs/revision, GDD/TDD projections, interaction/event/state contracts, camera/input policies, actors/equipment/abilities, world/content grammar, resources/progression/rewards/learning, economy/offers, save/analytics/ops і accepted creative sources. Прийняти test oracle окремо від implementation. За самих concept images/brief повернути exact gaps до design/assets і виконувати незалежну feasibility роботу; не називати baseline production-ready.

Не переписувати числа PDF у різні clients. Тримати canonical validated model/tables і explicit runtime import/generation adapters. Ланцюг **model ID → field/event/rule → runtime consumer → scenario → evidence** має бути простежуваним. Похідний runtime format може відрізнятися від authoring schema, але importer/version/hash і semantics перевіряються. Відсутність engine hook не дає права тихо прибрати правило.

Зміна зачіпає dependency closure: rules ↔ input/camera ↔ actors/world ↔ progression/rewards ↔ economy/save ↔ presentation/learning. Створити наступну revision, не перезаписувати accepted baseline. Переносити докази лише за незмінних hashes/dependencies. Локальний repair не запускає всі етапи й повну раду.

## 1. Перевірити маршрут і організувати роботу

Зняти capability inventory: OS/architecture, engine/render/export versions, SDK/NDK/JDK/Xcode, plugins/native libs/locks, signing refs, devices, CI/network і creative operations. Engine обирати за representative needs/license/cost/device support, не жанровим preset. Не встановлювати непотрібний стек; credentials/keystores не включати в source/handoff.

Активувати потрібні гілки gameplay/AI/world; camera/input/UX; art/motion/audio; progression/content/economy; platform/data/commerce. Дати precise model IDs, prerequisite hashes, paths, budgets, owners і stop. Lead створює та інтегрує. Паралелити незалежні файли; уникати двох writers одного source/production БД. Незалежне QA виконує інший actual actor; self-check так і називати.

## 2. Довести representative native slice

Рано отримати actual debug launch на обраній платформі. Розрізняти technical smoke/graybox та production slice. Репрезентативний шлях: launch → перше навчання/керування → ризикова взаємодія → result/reward → progression/equip/save → повторний запуск і використання відкритого.

Інтегрувати accepted materials, gameplay camera, input/physics/contact, animation/VFX, HUD, music/SFX і haptics разом. Показати normal/peak/boundary contexts та однакові scene/state/seed/camera/aspect для target/actual. Рухома камера потребує запису поведінки; overview image не є camera policy. Перевірити hero/action visibility, thumb occlusion, threat reaction distance, aspect/safe areas і reduced effects.

До масового content production закрити feasibility/fidelity/ergonomic gaps. Device performance і physical haptics потребують actual device receipt; editor/simulator не підвищує статус. Не вимагати повної гри до вибору концепції: виконувати лише authorized scope і due proof.

## 3. Реалізувати цілісний finite scope

- **Rules/input:** precise intent/gesture/hold/release/cancel/context semantics, timestamps, buffering/assist за design, event order/interruption/recovery і readable feedback. Всі ключові дії зручно доступні; число кнопок не доводить depth.
- **Actors/AI:** perception/knowledge/memory, decision/action states, telegraph/commit/recovery/cooldown, navigation, ролі/кооперація/контри/encounter budgets за моделлю. Constrained random policy, без невказаного omniscience. Небойова гра використовує релевантні agents/challenges без штучного додавання ворогів.
- **World/content:** локації/зв’язки, routes/risk/reward, interactive states/transforms, gates/revisits, persistent consequences, authored modules + executable grammar. Legal compositions/reachability/repetition/safe starts/ends і bounded fallback. Seeds/recolor не замінюють відмінних рішень.
- **Equipment/abilities/resources:** typed properties/formulas, effects/stacks/caps, synergies/exclusions, cost/recovery/counters/cues/persistence. Показати вплив на дію/ситуацію; не додавати stat/currency без окремої ролі.
- **Progression/rewards:** run/mastery/access/collection/permanent growth за fit; exact unlock graph, sources/chances/guarantees, duplicate/cap rules, next goal і meaningful use. Early/mid/late змінює можливості й рішення. Finite launch має завершений цикл і довгу арку без обіцянки нескінченного змісту.
- **UX/learning:** повні screen/state/transition families, gradual complexity, prompted/independent mastery checks, failure recovery/help/re-entry. HUD відповідає resource rules; HP bar не нав’язується всім жанрам. Відтворити accepted style/motion/audio/haptics, accessibility/localization.
- **Commerce:** бажана цінність, eligibility/cadence/caps, exact SKU/content/price authority, earned/no-offer/decline path, shop journey, sandbox verify/restore/refund/revoke. Не ховати домінантну силу за словом sidegrade. Paid randomness/model не стають обраними від появи в research.
- **Lifecycle:** save/version/migrations, pending durable work, offline boundaries, account/cloud merge, pause/kill/resume, consent/privacy/telemetry, platform adapters і ops hooks. Backend лише за потребою; absent-by-design має decision ref і не приховує missing requirement.

Physics callback дає candidate facts, не автоматичний повторний hit. Реалізувати exact resolver, capture/round/order/tick/RNG/lifecycle priority з [контракту 4.0](references/v4-route.md). Authoritative simulation commit і durable save commit окремі: негайний бойовий feedback не чекає диска/хмари, підтверджений critical grant не дублюється й не губиться поза визначеною гарантією.

## 4. Перевіряти причинну поведінку

Кожний feature slice: model/requirement IDs → accepted rules/data → design-derived fixture/oracle → changed sources/imports → actual runtime scenario → evidence → independent review. Форми [runtime bindings](assets/runtime-bindings.template.json), [feature slice](assets/feature-slice.example.json), [system scenarios](assets/system-scenarios.template.csv) не є actual proof.

Перевірити: знайома задача після unlock змінює рішення; інший enemy/environment state потребує іншої відповіді; synergy має заявлену межу/контру; reward реально відкриває й використовується; purchase/reward не дублює grant після restart. Мала гра потребує глибини ситуацій компактного світу, сценна — evolution/transitions/revisits, велика — topology/access/consequences; не уніфікувати їх в RPG шаблон.

Виконувати потрібні unit/property/integration/data/native checks: physics/time/RNG boundaries, content softlocks, economy conservation/dominance, purchase/reward idempotency, migration/corruption/kill-resume. Profiling охоплює lower tier/worst case і тривалу thermal сесію; average FPS не приховує frame spikes/touch latency. Simulation не доводить human fun/retention.

Repair: exact reproduce → causal diagnosis/dependency closure → smallest complete repair → targeted regression → independent closure. Два однакові безуспішні повтори — нова діагностика/tool/owner. Не писати implementation-mirroring checks заради test count.

## Deliverables та передача

| Результат | Due proof | Неприпустима підміна |
|---|---|---|
| Runtime data/bindings | Model revision/hash, imports, validation, fixtures | Незалежні копії чисел у clients |
| Feature/system slice | Actual behavior за design oracle | Наявність класу/сцени/поля |
| Creative/sensory integration | Whole-frame/motion/audio, scoped device proof | Editor render/JSON про звук/вібро |
| Native build | Toolchain/log/artifact/hash; signing/install status окремо | Назва `.apk` або cross-platform engine |
| Full delivery | Approved features/content/flows + exact upstream refs/source/rights/test receipts | Вузький demo loop або прогноз D1/LTV |

Передати frozen package до `gamedev-qa`: canonical sources/data/assets, GDD/TDD/model projections, recipes/locks, actual artifacts, golden inputs/seeds/saves/migrations, captures/profiles/reviews, known issues/owners. Android APK install/test відрізняється від AAB publish/delivery; iOS project/Simulator `.app`/`.xcarchive`/signed `.ipa`/TestFlight — різні statuses. Linux не доводить iPhone build.

`game_model.py validate MODEL --stage slice` застосовувати після actual `--help` за model workflow. `pipeline.py` обслуговує handoff1; `check_build_receipts.py` перевіряє bytes/log/container shape, не truth/signing/device/quality. Structural validity не є semantic acceptance. Новому package: `pipeline.py init … --stage build --project-id …`; існуючий проект не init повторно. Seal/hash не дає acceptance або publication permission.

Контрприклади для repair: весь світ в одному кадрі всупереч camera policy; три enemy classes з однією політикою; late game лише HP inflation; reward event без durable grant/meaningful use; item modifiers без stacking order; FTUE walkthrough без самостійної дії; shop лише success path; старий build capture позначено новим.

Фінально назвати scope/coverage/gaps, actual built/installed/tested platforms, fidelity/model consistency, limitations і next action. Release — після independent QA та чинного publication scope. User-defined pause/stop зберігає checkpoint і зупиняє залежні дії.

Версія інструмента: **6.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
