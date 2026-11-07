---
name: app-atelier-release
description: "App Atelier - підготовка й дозволений випуск Android/iOS/web продукту: рання перевірка досяжності stores/акаунтів/бюджету/тестування, signing, listings, billing/privacy передумови, deployment, receipts/read-back і rollback. Використовувати до повного build для release feasibility, перед beta/production поданням, при ремонті релізу або передачі Work/Codex."
---

# App Atelier 5.0.0 · Випуск

## Спільний спосіб роботи5.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Редакція інструментарію **5.0.0**. Перед залежною предметною роботою прочитати [наскрізний контракт](references/cross-domain-core.md) та [виробничу глибину етапу](references/app-depth.md) і [модель систем застосунку](references/app-system-contract.md). Інстанціювати потрібні [рецепти й матрицю покриття](assets/app-depth.templates.json) у проєктних artifacts і реєструвати їх у чинному canonical state; шаблон не є виконаною операцією або доказом.

Обов’язок входу: До significant build сформувати повну operation-level feasibility для Android/iOS/web/support/data/billing за застосовності; до dispatch pin-ити exact release assembly, чинні prerequisites, migration/rollback і current effect scope. Не підміняти missing account або signing N/A.

Обов’язок виходу: Після dispatch зберегти actual provider IDs/receipts/read-back, відрізнити submitted/approved/released/available/core-observed, передати operations точні версії/сигнали/recovery/open gates. Timeout спершу reconcile; completed upload не є доказом доступного продукту.


Читати [core](references/core-contract.md), [workflow](references/workflow.md), [acceptance](references/acceptance.md); перед витратами/effects - [budget](references/budget-contract.md), [handoff](references/handoff-contract.md), [evidence](references/evidence-contract.md), для даних - [data/support](references/data-support-contract.md).

## Ранній feasibility до full build
Відкрити project profile/state, обраний сценарій, платформи й бюджети. Перевірити за поточними первинними джерелами доступний маршрут Android/iOS/web, тип/стан акаунтів, власника, signing, пристрої, toolchain, організаційні вимоги, обов’язкові витрати й тестування. Датовані довідки з попереднього пакета - підказка до повторної перевірки, не чинний доказ.

Зіставити store requirements із забороною людських дослідів/нульовим бюджетом/географією. Не видавати синтетичних користувачів за обов’язкових tester accounts, не обіцяти обхід або автоматичне схвалення. Unknown access не дорівнює доступному релізу. Конфлікт показати до значної реалізації з конкретним scoped blocker та допустимими варіантами; власницький scope не змінювати мовчки.

## Підготувати конкретний release
1. Pin-ити exact app/web/backend/support versions, source commits/artifact hashes, build configs, environment, data migrations і QA/evidence. Перевірити три самостійні core paths, product entitlements і support data scope.
2. Зібрати current account/SDK/signing/store/billing/privacy/age/content/accessibility/legal prerequisites за застосовністю. Для медичних/фінансових/дитячих/інших відповідальних доменів залучити потрібну компетенцію; її відсутність - blocker залежного випуску.
3. Підготувати listings, screenshots/preview фактичного продукту, опис/локалізації, support/privacy URLs, review notes/demo route, product IDs/entitlements і return/cancel/restore сценарії. Не вигадувати реальний досвід, сертифікацію чи відгуки.
4. Перевірити разові/регулярні витрати, production limits, safe rollback/recovery, support/monitoring readiness. До exact readiness вибору власника дати читабельний release packet із gaps.
5. Для кожного external effect перевірити достатній чинний scope, capability/account, current prepared artifacts і parameters. Точні CLI/state records читати в локальній довідці; dispatch не є зовнішнім виконанням.
6. Виконати реально доступною інтеграцією/API/CLI; зберегти provider reference/receipt, перевірити актуальний зовнішній стан. Submission/store approval/deploy/availability відрізняти. При timeout - reconciliation до повтору.

## Передача й післядія
Підготувати точний launch/return для особистих MFA/signature/device кроків після завершення решти. Не просити секрети в chat/ZIP. У межах доручення виконати доступну автоматизацію самостійно. Передати product URL/build, observed useful operation, support/runbook, rollback/data compatibility й next step. Нове подання після repair проходить зачеплений QA і чинний effect scope.

## Компоненти іншого агента або чатбота

Перед прийомом компонента Agent Foundry, делегуванням у ChatBot Atelier або створенням нової спеціалізованої методики прочитати [стабільні виклики й межі компонентів](references/cross-family-routing.md). Використовувати поточні джерела за незмінним `name`, shared product/requirement/contract IDs та точний launch/return пакет; не починати окремий продуктовий цикл для локальної підтримки.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
