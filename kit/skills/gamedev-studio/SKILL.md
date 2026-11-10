---
name: gamedev-studio
description: "Game Atelier — створити, відновити або перевірити ідентичність і готовність ігрової студії. Використовувати для бренду, логотипа, developer identity, store/account/service setup, розбіжностей похідних і передачі studio payload; зберігати exact accepted masters і не перезапускати неймінг або художній стиль гри через оновлення агента. Перевіряти operation capability, права, виробничі witnesses та точний host bridge."
---

Відповідати за прийняті identity/rights та доступність потрібних виробничих операцій. Передавати не список програм, а точні capability records, lawful sources й перевірені prerequisites для наступного виконавця.

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

# Game Atelier 6.1.0 · Студія

## Умовні AI/data та виробничі профілі6.1

Коли задача справді потребує збору чи аналізу даних, LLM/RAG, прогнозування, адаптації моделі, серійного виробництва матеріалів або їх оцінювання, прочитати лише застосовні частини [AI/data виробничого маршруту](references/ai-production.md). Обрати потрібні DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA чи EVALUATION всередині чинної предметної команди. Спочатку достатній наявний виконавець і метод; нові агент, framework чи глобальний індекс не є типовою передумовою.

Зберегти первинний результат, усі застосовні вимоги, прийняті оригінали, налаштування, дозволи й відкладене в тому самому рідному стані. Типізовані матеріали та `scripts/ai_production.py` використовувати лише для доречних оголошених перевірок. Їхній PASS не доводить фактичного збору, навчання, якості, споживання, незалежності чи прийняття власником. Виявлена втрата прийнятої працюючої властивості відхиляє кандидата; неперевірений потрібний доказ лишається відкритим.

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

## Вхід і роль у продукті

Працювати українською як предметний модуль `gamedev-director`; користувач не керує переходами між навичками вручну. До залежної дії прочитати [workflow 4.0](references/game-model-workflow.md), [Game Model](references/model-format.md), [intake](references/unified-agent.md), [core](references/core-contract.md), [handoff](references/handoff-contract.md), актуальні project requirements/decisions/knowledge та exact upstream files/hashes. Звірити scope, permissions, budget і stop. Прямий виклик studio не обходить ці правила.

Завантажувати [creative](references/domains/creative.md) для identity/derivatives й [lifecycle](references/domains/lifecycle.md) для readiness/services; [research](references/domains/research.md) — для пошуку назви/ринку, [commerce](references/domains/commerce.md) — для залежностей оплат/ads за наявності задачі. Інші модулі залучати за project impact, не запускати весь game-design цикл для експорту логотипа. Дотримуватися [experience](references/experience-contract.md), [systemic](references/systemic-design.md), [вимог](references/requirements.md), [команди](references/agents-context.md) і [бюджету](references/model-budget.md).

Вести studio identity/asset/service records як пов'язані джерела канонічної Game Model, а не окрему конкуруючу модель гри. Studio виробляє прийняту identity та переносний lawful payload. Concepts визначає гру; studio не нав'язує їй genre, camera, engine, art medium, orientation чи монетизацію. Прийнятий знак студії не погоджує повне тіло героя, новий лор або однакову графіку всіх ігор. Дані студії використовувати у splash/about/credits/store за фактичним usage map.

## 1. Відновити чинну ідентичність і матеріальні рішення

Відкрити поточні studio archive/master/source/approval history та зберігати підтверджені назву, права й exact accepted originals. Історичні профілі застосовувати тільки до підтвердженого збігу проєкту за [правилом](references/historical-project-profiles.md). Назва Master не є доказом згоди.

Розрізняти chosen name, visual proposal, approved master, approved derivative, правову особу та configured account/service. Зображення містить видимий задум; не вигадувати з нього editable layers, font binaries, невидиму геометрію, rig або права. Перевірити actual imagegen/DCC/export capability перед обіцянкою source formats.

З'ясувати лише відкриті material choices: нова/чинна студія, brand/legal entity, stores/платформи, країна/тип developer account, публічні контакти, ongoing budget/services, exact reuse чи material redraw. Переносити дослівне джерело, scope й чинні згоди без повторного запиту. Невідоме legal/service ID залишати null із owner/closure, не вигадувати production-like значення. Незалежна інвентаризація/дизайн/інструкції можуть тривати, поки залежна дія очікує рішення.

Для production capability використовувати operation-level witness, semantic transformations і exact host bridge з [контракту 4.0](references/v4-route.md); installed/catalog status не підвищувати до integrated/native.

## 2. Організувати предметну роботу

Один lead зводить brand direction, source/export та studio operations. Незалежні brand production й account/service research можна розпаралелювати з окремими owned paths. Для кожної роботи видати requirement IDs, exact inputs/hashes, output, cap і done check. Visual reviewer фактично порівнює originals із derivative families; operations reviewer перевіряє steps/джерела/невідомі. Не називати авторський self-check незалежним QA й не створювати окремого керівника на кожний експорт.

## 3. Замкнути master → похідні → використання

1. Для нового напряму підготувати зіставні варіанти з різними художніми мовами, rationale й доступним production route. Назву, trademarks/domains і store rules перевіряти актуальними джерелами; пошук не видавати за правову гарантію.
2. Зафіксувати exact selected original bytes/hash, provenance/rights, revision, scope та реальну відповідь користувача. Вибір назви не приймає автоматично новий lettering або redraw.
3. Описати знак/персонажа/wordmark/lettering, proportions, texture/contours/light, palette/type, clear space, min size й допустимі scale/crop. Позначити frozen і open властивості. Для незмінного asset використовувати byte-identical original; derived export має рецепт.
4. Виробляти SVG/PNG/profile/header/store derivatives із тих самих lawful sources. Raster master/crop є допустимим source, але перемальований SVG не називати exact original. Vector/mono/compact потребує визначеного target, actual comparison і delta review.
5. Перевірити кожну variant family у композиції й малих розмірах: alpha/background, safe areas, color pipeline, readability, fonts/license, export reproducibility. Palette match не доводить shape/face/lettering identity. Не обіцяти відновлення втрачених деталей upscale.
6. Матеріальна зміна silhouette/face/material/lettering/layout відкриває upstream repair або конкретний user decision до тиражування. Не називати її непомітною адаптацією. Зміна studio revision інвалідує тільки залежні uses/reviews, зі збереженням історії.

Специфіка — [studio production](references/studio-production.md). Візуальна перевірка потребує actual image view; hashes доводять bytes, а не художню еквівалентність. Один board не закриває всі outputs. Не робити 50 довільних розмірів без потрібного target.

## 4. Підготувати й виконати реальний setup

За актуальними офіційними джерелами визначити developer verification/accounts, legal/display names, agreements/tax/payout, domain/site/support/privacy, signing/CI/secrets, repo/backups, analytics/crashes, consent/ads/IAP та backend/storage за потребою гри. Для кожної задачі записати necessity, preconditions/dependencies, owner/env/access, verified URL/date, exact steps, expected cost/recurring cost, done check, observed outcome, blocker/recovery і next consumer. Брендбук не робить реєстрацію, signing або deployment виконаними.

Обирати найменшу достатню інфраструктуру; не додавати account/auth/database/ads SDK у всі ігри. Уточнення потреб гри повертається versioned studio update з impact map. Нуль додаткових витрат локальних tools не означає безкоштовних store accounts чи довільних API. Не створювати платні послуги/публічні аккаунти/recurring monitoring без відповідного доручення.

Виконувати дозволені підтримувані setup/config/account actions через достатні tools/API/CLI або дозволений browser, а не робити їх усі ручними за замовчуванням. MFA, особистий legal/signature confirmation, physical hardware чи відсутні права потребують точного owner bridge: що вже готово, єдиний blocked step, перевірений URL/команда, expected receipt, що повернути без секретів і return validation. Не просити передавати credentials у чат/архів. За timeout/unknown outcome звірити зовнішній стан до retry.

## 5. Передати точний studio payload всьому циклу

Передати human guide, machine catalogue, immutable master, lawful sources/exports, rights, tokens/usage rules, font/license files, current legal/display identifiers, services/setup dependencies, actual evidence й unresolved choices. [Payload contract](references/studio-payload.md) задає вміст без нового top-level manifest. Стартові authoring aids — `assets/studio-catalogue.template.json` і `assets/studio-setup.template.csv`.

Кожний use у Game Model посилається на studio revision/asset IDs; не дублювати невідомі значення в документах. Concepts переносить потрібні originals і envelope; preproduction визначає usage; assets використовує approved derivatives; build фіксує import recipe; QA звіряє actual screens/metadata; release розділяє legal і display identity. Новий export не змінює автоматично gameplay art, камеру, модель персонажа чи lore.

Використовувати package-relative paths, resolver і hashes; unavailable historical evidence позначати чесно. Не включати credentials, private keys, банківські номери чи посвідчення. Для restricted-redistribution materials надати законний restore route й точні limitations. При Work↔Codex передачі вказати конкретні inputs, prerequisites, launch steps, expected outputs і перевірку повернення; не припускати автоматичний sync локальних чатів/логінів.

## 6. Прийняти й повернути результат director

Перевіряти окремо identity/art, reproducibility exports, rights/provenance, documented setup і actual account/service readiness. Pending paid account/legal ID не блокує незалежні assets; missing required master або непогоджена заміна блокує конкретне використання. Зберігати чесні stage statuses й user-defined stop.

Запустити actual `--help` для `scripts/pipeline.py` і застосовних model checks, перевірити paths/hashes/requirements/derivative coverage. Порожній template чи structural pass не є художнім/правовим/операційним прийманням. Для матеріальних змін виконати незалежний focused review, повторюючи лише affected checks. Після двох невдалих однакових ремонтів змінити діагностику.

Повернути director actual artifacts/evidence, requirement coverage, точні accepted/open decisions, service receipts, risks/owner/closure, exact package revision/hash і next action/environment. Зберегти checkpoint та весь незмінний контекст; оновлення агента не є оновленням матеріалів гри або новою production згодою.

Версія інструмента: **6.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
