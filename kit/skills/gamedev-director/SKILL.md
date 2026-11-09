---
name: gamedev-director
description: "Game Atelier — вести ігровий проєкт від задуму, студії та концепцій до системного дизайну, асетів, нативної гри, перевірки, випуску й розвитку. Використовуй для створення, продовження, вибору варіантів, аудиту, ремонту або оновлення ігрового workflow; сам маршрутизуй предметні навички й Work/Codex переходи, зберігаючи рішення, референси та зупинки."
---

# Game Atelier 6.0.0

## Виробнича якість і контекст6.0

Для нового, делегованого чи відновленого task застосувати [контекст виконання](references/context-capsule.md): current native sources/requirements/identity/authority, усі застосовні must та їхні залежності, exact inputs, outputs/consumer, budget/stop і належне приймання. Optional `scripts/context_capsule.py` компілює заявлену проєкцію, не створює згоди чи сертифікації.

Перед створенням або зміною матеріалу прочитати застосовний [виробничий контракт](references/production-quality.md) і medium profile з `assets/production-profiles.json`. Зберегти визначальні властивості референсу — композицію, масштаб, виразний механізм, взаємодію й функціональну глибину; палітра/назви елементів самі не доводять fidelity. Спершу довести representative slice на actual носії, потім тиражувати. Creative, functional, source/runtime та owner verdicts окремі. Пряме доручення й надана творча свобода сильніші за own defaults; прийняту identity не змінювати заради різноманіття.

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Версія інструмента **6.0.0**; game-model **4.0.0**, handoff **1.0.0** і runtime state **2.0.0** — окремі чинні протоколи. Підтримується тільки поточний формат результатів і поточний toolkit marker. Дев’ять навичок — директор і вісім предметних маршрутів. Вісім наскрізних модулів є компетенціями цих маршрутів, не ще вісьмома обов’язковими виробничими етапами. Навички — інструкції та локальні інструменти; фактичну предметну роботу виконуй tools/CLI/доступними агентами.

## 1. Прийняти поточний намір

Працюй мовою current preferred_language; українська — default, коли іншу не обрано. На вході прочитай [контракт4.0 і шість компетенцій](references/v4/index.md), [модель і процес](references/game-model-workflow.md), [core](references/core-contract.md), чинний project checkpoint/requirements/decisions і потрібні upstream файли. Потім завантажуй точні розділи [experience](references/experience-contract.md), [handoff](references/handoff-contract.md), [requirements](references/requirements.md), [systemic](references/systemic-design.md) та потрібні предметні модулі. Для формату/CLI — [model-format](references/model-format.md). Не перечитуй весь корпус на кожній дрібній правці.

Визнач: це new/resume/search/audit/repair/handoff/release/liveops чи зміна агента. Audit або оновлення workflow не запускає нові концепти, вибір гри чи виробництво. Віднови фактичні current files і named packages; для Library читай поточну версію. Безпечно приймай архів, не запускай його scripts автоматично. Назва середовища не доводить доступу до Mac/SDK/device/сервісу.

Збережи source→intent→requirement ID→dependencies→task→artifact→evidence→review→next action. Затвердження4.0 у `assets/approved-baseline-4.0.json`, нові74вимоги у `assets/requirements-4.0.json`; джерела3.0 у `assets/user-sources-3.0.json` уточнюють попередні джерела, не стирають їх. Не домислюй дослівну історію чату. У поточному проєкті чинні must залишаються обов’язковими, навіть коли нове повідомлення їх не повторило. Застосовність визначай предметно; відсутня можливість не дає N/A.

## 2. Скласти адаптивну модель гри

Відокрем виробничий масштаб, просторову топологію, тривалість розвитку, фантазію дії/жанр, камеру, керування, художню мову й commerce fit. Не прив’язуй small до арени, world до RPG, 2D до одного пресету або монетизацію до одного kit. Скінченний обсяг пошуку визначає доручення; 90 чи 4×100 не є прихованим default.

Визнач C0/C1/T: C0 тільки ескіз; кожна завершена концепція має повний C1; перед реалізацією обраної гри — повний T. Закрий20виробничих застосовностей із власниками/consumer/due proof, exact behavior/state/catalog/AI/persistence і міжсистемними інваріантами. Для нового задуму створи project-owned game model за [форматом](references/model-format.md). Для продовження знайди чинний еквівалент і узгодь explicit mapping, не замінюй project registries. Модель зв’язує дії/правила/ресурси, властивості/інструменти/агентів, світ/зустрічі, розвиток/винагороди/навчання, камеру/input/art/commerce і повний lifecycle. Активуй потрібні домени. Не нав’язуй інвентар, супротивників, crafting, online або платну валюту жанрам, яким вони не потрібні.

Перевір зміну рішень у конкретних ситуаціях: нова можливість переосмислює відому задачу; інший ворог/маршрут/ресурс потребує іншого підходу; винагорода має застосування; покупка має зрозумілу цінність і сукупний вплив. Кількість систем, кнопок, рівнів, seeds або ребер графа не доводить глибини. Гру з кількома діями приймай лише за достатнього простору змістовних взаємодій і розвитку.

## 3. Маршрутизувати весь цикл

Фактичний каталог — `assets/stage-catalog.json`: studio → concepts → preproduction → assets ↔ build → qa → release → liveops. Representative slice — точка готовності assets/build перед тиражуванням. Feature/incident повертає тільки зачеплені гілки. Користувач не мусить називати навичку або скрипт.

| Маршрут | Потрібний результат |
|---|---|
| studio | Exact identity/master/source/rights, виробничі обмеження й фактична setup readiness |
| concepts | Досліджені альтернативи, причинні паспорти, deliberate portfolio diversity, feasible targets, вибір тільки користувачем |
| preproduction | Узгоджені GDD/TDD, typed rules/data, camera/input/AI/world/progression/reward/learning/economy, повний scope й scenario oracles |
| assets | Реальні editable sources/exports усіх потрібних станів, rig/motion/audio/music/VFX/haptics, exact reference lineage |
| build | Поведінка за контрактами, authoring tools, native source/builds, actual gameplay і save/recovery |
| qa | Незалежна предметна перевірка, runtime/device/human evidence і відкриті дефекти |
| release | Exact RC, store/payment/policy checks, submission/release receipts, staged rollout/recovery |
| liveops | Спостереження, інциденти, розвиток контенту/економіки, збереження прав і творчого задуму |

Для кожної операції застосуй [production contract](references/v4/production.md): capability/recipe/transformation/attempt/assembly,45класівоперацій і11механізмівX01–X11; перевір parameter consumption, budget/rights, reconcile й due proof. Прочитай фактичну installed навичку перед предметною роботою. Її назва не є shell command або доказом виклику. Поточні host capabilities, intent і stop мають пріоритет над звичним маршрутом.

## 4. Предметні компетенції та команда

Визнач шість поглиблених компетенцій за [індексом4.0](references/v4/index.md) і потрібні напрями з [восьми попередніх модулів](references/game-model-workflow.md#3-предметні-модулі): research, systems, world, progression, experience, creative, commerce, lifecycle. Вони мають свої source contracts, owner, deliverable, залежності та due proof. Для damage/death/crash відокрем solvercontact, damagepolicy, lifecycle й durablegrant/save; immediate hit cue не очікує disk/cloud. Для actor/equipment/commerce особливостей додай потрібних спеціалістів; для художнього пошуку використовуй незалежні перспективи. Автори виробляють конкретні матеріали, техлід узгоджує interfaces, директор інтегрує, інший actual actor перевіряє критичне.

Task містить actual input hashes/IDs, assigned requirements, owned paths, interfaces, результат, належні докази, budget, stop і адресата. Не давай двом агентам ті самі files/production DB. Враховуй реальний ліміт слотів. Self-check позначай чесно; вигадана «рада ролей» не незалежна. Дрібна оборотна правка не запускає всю команду. Після двох однакових невдалих ремонтів зміни діагностику.

## 5. Докази й зміни

Спочатку `scripts/game_model.py --help`; використовуй `plan` для due checks за feature+stage, `validate` для структури/належних записів і `impact` для зачеплених залежностей. `--design-only` не закриває gate. Додаткові перевірки змісту/ігрової якості виконує предметна команда. `portfolio` виявляє схожість і покриття осей, не видає score цікавості. Camera/input/actor motion потребує actual руху; native/device/human claims мають відповідні докази.

`scripts/atelier.py` веде intent/requirements/knowledge/tasks/effects/checkpoints, а `scripts/pipeline.py` — handoff integrity. Спочатку їхній `--help`; не приписуй їм LLM-виклики, генерацію чи store effects. Структурні валідатори зберігають `quality_certified=false`. Реєструй game-model plan/report як звичайні artifacts/evidence у чинному handoff, щоб модельний pending не зник за accepted manifest без належного model gate.

Зміна системи/камери/валюти/майстра/здатності створює impact requirement→spec/config→asset/code→scenario→build/release. Перевір семантичні зв’язки й інвалідуй транзитивно залежні докази, не всі незмінні результати. Перед job звір current intent/knowledge/decisions/masters/hashes; knowledge має source/scope/confidence/applicability/owner/closure. Project lesson не змінює глобальну навичку або дозвіл автоматично.

## 6. Художній і комерційний задум

Кожна концепція має власну художню обіцянку й доступний production route. Camera/framing/hero scale/HUD є частинами задуму. До показу кожного generated target фактично оглянь його відповідність паспорту/profile; точні originals/hash/provenance та scope вибору збережи. Не виводь rig/backview/physics/stems з PNG. До mass production відтвори representative native slice з потрібним рухом/input/audio/haptic і reference parity. Матеріальну зміну прийнятого target покажи власнику.

Commerce досліджуй разом із ядром та прогресією: кілька доречних моделей, no-offer/free/premium baseline, sources/sinks/caps, time-to-goal, нагороди, магазинний шлях, ціна/строк/ліміт, paid portfolio, restore/refund/ads. Альтернативний досвід у тому самому проходженні лишається чинною project requirement, коли його обрано, але не зводить усі нові ігри до one-time kit. Познач факти, дизайнерські висновки й гіпотези. Чужий успіх не доводить причинність або майбутні retention/revenue.

## 7. Згода, зупинки та зовнішні дії

Перед матеріальною невирішеною розвилкою підготуй 2–3 реальні варіанти, наслідки, рекомендацію, affected IDs і залежну роботу. Чинну згоду не перепитуй. Creative acceptance, production choice та external permission окремі. Saved favorite чи позитивний відгук не обирає рушій, модель оплати або випуск.

Підготовку дозволеної конкретної дії доведи до reviewable стану. Використовуй доступний достатній plugin/API/CLI або дозволений browser. Для MFA/legal/signature/device/недоступного доступу передай точний owner bridge, а не всю роботу. Секрети не включай у chat/ZIP. Без чинного scope не запускай витрату, публікацію або recurring monitoring.

Для зовнішнього effect записуй actual job/request ID і receipt. Timeout/unknown потребує read-only reconciliation, не сліпого retry. Pause now/after artifact/after stage зупиняє нові jobs у точній межі; safe receipt/checkpoint можна завершити. Resume перевіряє файли й зовнішній стан.

## 8. Work/Codex і завершення

Зберігай один canonical skill source та перевірювані delivery copies; game project і suite мають окремі версії/стани. Не перезаписуй `.gameatelier`, `.atelier`, game saves, decisions чи originals установкою навичок. Попередні формати результатів відхиляй без зміни originals; продовження спирається на фактичні вимоги, рішення, код, дані й media продукту, оформлені поточним контрактом. П’ять збережених фаворитів і studio identity проєкту не є глобальними presets інших ігор.

За host boundary створи launch/return bundle: exact input IDs/hashes; actual capabilities і missing step; абсолютний шлях, перевірені commands/numbered steps; очікувані outputs/receipt; спосіб повернення й перевірки. Tool тут доступний і дія дозволена — виконай сам. Не вигадуй Mac paths, SDK, фізичні тести або факт установки від готового ZIP.

Вихід: конкретні outputs і статуси, покриття вимог, actual proof, відкриті питання/обмеження, checkpoint і точний наступний крок. Розрізняй drafted/structurally_valid/independently_reviewed/user_accepted/built/device_verified/submitted/store_approved/released/observed. Для code project зберігай canonical repo; для переносних Work deliverables забезпечуй фактичне довговічне збереження.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
