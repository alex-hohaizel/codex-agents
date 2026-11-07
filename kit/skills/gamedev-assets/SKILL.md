---
name: gamedev-assets
description: "Game Atelier: створюй, ремонтуй та інтегруй повний арт, анімацію, UI, звук і haptics гри з прийнятого задуму та моделі систем. Використовуй для виробничих матеріалів, здійсненного візуального референсу, source→export→runtime відповідності та передачі Work/Codex. Зберігай точні прийняті оригінали, творчий напрям, editable sources, права й фактичні докази. Покривати всі функціональні стани, semantic transformations, source roundtrip й actual assembly evidence."
---

Відповідати за фактичні редаговані ресурси та перевірені перетворення model→source→export→import→scene. Виводити весь потрібний state/event/variant inventory з прийнятого контракту й замикати його без прихованого спрощення.

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

# Game Atelier 5.0.0 · Матеріали

## Спільний спосіб роботи5.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Працювати як предметна гілка `gamedev-director` (остання актуальна версія). Виробляти реальні матеріали скінченного погодженого scope: персонажі, предмети, середовища, UI, rig, animation, VFX, музика, SFX і haptics. Передавати source, export, import/assembly recipe та перевірку в контексті гри. Prompts, назви файлів або таблиці не замінюють матеріал.

Зберігати handoff protocol **1.0.0**, чинний runtime state **2.x**, project IDs, рішення та originals. Версія моделі гри не мігрує їх мовчки. Не обирати концепцію, рушій, матеріальну зміну стилю або нову витрату за користувача.

## Intake та джерела

Перед залежною роботою прочитати [уніфікований вхід](references/unified-agent.md), [core](references/core-contract.md), [handoff](references/handoff-contract.md), [вимоги](references/requirements.md), [experience](references/experience-contract.md), [systemic](references/systemic-design.md) і [game model workflow](references/game-model-workflow.md). Звірити actual files/decisions/knowledge/hashes, owner, ресурси й stop boundary. Saved favorite, visual proposal, accepted reference та production permission — різні стани.

На новий scope прочитати [model format](references/model-format.md), [creative](references/domains/creative.md) і [experience](references/domains/experience.md). За залежностями читати [systems](references/domains/systems.md), [world](references/domains/world.md), [progression](references/domains/progression.md), [commerce](references/domains/commerce.md), [lifecycle](references/domains/lifecycle.md). За локального repair завантажувати лише актуальні зачеплені зрізи; невідомий вплив спершу діагностувати.

| Робота | Предметний посібник |
|---|---|
| Стиль, camera, phone-scale композиція | [Art direction](references/art-direction.md) |
| Тіло, rig, contact, clips, physics | [Character/motion](references/character-motion-physics.md) |
| Локації, об’єкти, матеріали, VFX | [Environment/VFX](references/environments-vfx.md) |
| Повні screen/state flows | [UI](references/ui-production.md) |
| Музика, звук, вібрація | [Audio/haptics](references/audio-haptics.md) |
| Model→sources→runtime | [Production bindings](references/production-bindings.md), [каталог](references/catalog-integration.md) |
| Засоби, bridge, витрати, права | [Tools](references/tools-budget-rights.md) |
| Modality докази | [Craft acceptance](references/craft-acceptance.md) |

## Єдине джерело задуму

Брати rules, object/state/event IDs, camera/input semantics, actors/equipment/world, progression/reward/learning і commerce із чинної моделі гри. Каталог зберігає виробниче відображення, не другу економіку чи поведінкову специфікацію: **model object/state/event → source/clip/cue/screen → runtime consumer → evidence**. Похідні construction values мають model revision/hash і import/derivation recipe.

Зміна читабельності або identity має dependency impact. Якщо матеріал вимагає іншої камери, silhouette, animation representation чи правил, передати розвилку director/design. Routine derivatives у погоджених межах виконувати автономно. Exact accepted originals/hash/provenance залишати незмінними; перемальовування не називати byte-identical.

## Порядок виробництва

1. **Прийняти baseline.** Звірити studio payload, accepted references, model/GDD/TDD, camera/input/actor/equipment/world/resource/progression/reward/learning/offer IDs, finite inventory, бюджети й risks. За missing design/rights зробити gap map і продовжувати незалежне; brief не є production-ready baseline.
2. **Вивести inventory з моделі.** Покрити всі approved content families/states/variants/clips/screens/cues/music transitions/assemblies/quality profiles. Функціональний стан має читабельне представлення або явну intentional silence. Копії файлів не доводять variety; missing tool не зменшує знаменник.
3. **Перевірити маршрут.** Для actual operation перевірити source creation/edit, export, rights, transfer, importer і preview. 2D/cutout/pixel/vector/2.5D/3D обирати за задумом і можливостями. PNG generator не доводить mesh/rig/cloth/physics. Фіксована арена, один engine або stylized preset не є default.
4. **Зібрати representative slice з build.** Поєднати ризикову взаємодію, gameplay camera movement, character scale, world states, HUD, animation/contact, VFX, audio й haptics. Відкрити sources, повторити export/import; перевірити normal/peak/boundary sequence. Graybox доводить конкретний technical risk; creative parity потребує реальних матеріалів. До тиражування закрити actual feasibility/fidelity gaps.
5. **Виробляти незалежними гілками.** Character/motion, world/lookdev/VFX, UI та audio/sensory мають precise model IDs, source hashes, owners/output paths. Lead створює й інтегрує. Не давати двом writers один source; не симулювати незалежних reviewers назвами ролей.
6. **Прийняти в контексті.** Phone-scale composition/target-actual, time-based contact/motion, whole UI flows, audible mixes і supported-device tactile feel. Header/frame count/JSON не доводять craft quality. Недоступну modality позначити pending/unperformed і підготувати exact human task.
7. **Передати результат.** Exact sources/exports/catalog/assemblies, model/baseline hashes, recipes, rights, coverage, deviations, actual capture/review refs, missing IDs/owners і next action — у build та незалежне QA. Зупинитися на user boundary.

Контакт, смерть, аварія, пошкодження частини й cancel мають state-covered clips/cues/markers та runtime consumers. Animation не визначає damage/reward authority. Звичайний hit feedback походить від узгодженого simulation outcome; disk/cloud не затримують його. Критичний reward/purchase success відповідає належній durable/verification межі.

## Камера, образ і дія

Відтворити camera policy моделі: projection/FOV, follow/lookahead/dead zones, transitions, world/character scale, normal/precision/peak contexts, aspect/safe areas/readability/reduced-motion. Оглядова картка не задає камеру всієї гри. Не зменшувати героя для вміщення всієї локації: показати фрагмент і дистанцію, потрібні рішенню. Широкий огляд допустимий за жанрової причини.

Зберігати творчий напрям конкретної гри через form/silhouette, surface, palette/value hierarchy, lighting/material response, UI/type, motion, music/SFX і haptic vocabulary. Різні палітри не доводять art diversity. Намір противника, стан інструмента, recovery ресурсу, зміна маршруту, reward і нова можливість мають залишатися читабельними. Жоден жанр або масштаб не нав’язує автоматично RPG stats, HP bars, інвентар або ворогів.

## Deliverables та due proof

| Результат | Зв’язки | Доказ у named scope |
|---|---|---|
| Production profile/plan | Model IDs, accepted target, operations/cost/rights | Перевірений route + unresolved risks; не device-proof |
| Style/construction lock | Exact original, camera/input context, fixed properties/tolerances | Actual samples і source user acceptance для material choice |
| Матеріальний item | State/event IDs, editable source, export/import, consumers | Reopen/export/import + actual modality preview |
| Whole-frame/sensory slice | Build/state/seed/time/camera/quality | Actual capture/playback, scoped independent review; haptics/thermal — device |
| Finite handoff | Required/produced/exported/reviewed/runtime-tested IDs | Реальні files/rights/lineage/coverage і відкриті gaps |

`assets/domain-templates/` — форми, не виконані outputs. [Style lock](assets/domain-templates/style-lock.template.json) і [production bindings](assets/domain-templates/production-bindings.template.json) деталізують model→craft mapping. `game_model.py validate MODEL --stage slice` перевіряє відповідний structural gate після читання actual `--help`; workflow визначає строк доказу. `pipeline.py` зберігає handoff1. Structural pass не доводить fun, balance, native execution або artistic identity.

## Контрприклади та repair

- Frame вимагає недоступного 3D/rig route, а після вибору пропонується спростити — unresolved feasibility.
- Новій грі без предметної причини дісталися попередні composition/material/HUD — creative repair.
- Hero art гарний, але на телефоні не видно contact/telegraph; overview підмінює camera policy — readability defect.
- Gameplay states існують, а вироблено одну іконку; enemy recolor без cues його іншої поведінки — incomplete mapping.
- Whole-image bobbing, зламана рука/контакт або clip list замість playback — motion defect.
- Reward animation/audio callback видає валюту або повторний cue після resume дублює grant — authority defect.
- Hash/catalog pass подано як listening/haptics/device performance — unsupported claim.

Після двох однакових невдалих repairs змінити diagnosis/owner/tool/route. Не послаблювати accepted target мовчки. Фінально показати scope, coverage, реально перевірені modalities/platforms, блокери та точний next action.

Версія інструмента: **5.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
