---
name: gamedev-liveops
description: "Game Atelier: супроводжувати beta або випущену гру — telemetry/cohorts, incidents, навчання/повернення, механічна різноманітність, progression/rewards/economy/магазин, content lifecycle, experiments, save migrations, hotfix/rollback і витрати. Використовувати для конкретного завершеного раунду аналізу чи розвитку; відділяти live факти від моделей, гіпотез та дизайнерських обіцянок. Відновлювати actual released state й причинні traces, production attempts, continuity та сумісність змін."
---

Відповідати за завершений раунд фактичного спостереження, діагностики й адресного покращення. Відтворювати released state, зберігати права й прогрес; не заявляти фонове спостереження без реально запущеного сервісу.

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

# Game Atelier 5.0.0 · Супровід

## Спільний спосіб роботи5.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Працювати українською як предметний модуль `gamedev-director`. Основне середовище — canonical game repository й actual providers у Codex; Work придатний для research/analytics/creative bridge через доступні джерела. Передавати findings/checkpoint, а не покладатися на невидиму спільну пам’ять. Toolkit 5.0.0 не змінює автоматично game/save/handoff version і не запускає виробництво при аудиті навичок.

## 1. Прийняти runtime й конкретне доручення

Прочитати [єдиний вхід](references/unified-agent.md), [спільний контракт](references/core-contract.md), [досвід](references/experience-contract.md), [системний задум](references/systemic-design.md), [game-model workflow](references/game-model-workflow.md), [формат моделі](references/model-format.md), [handoff](references/handoff-contract.md), [вимоги](references/requirements.md), [контекст команди](references/agents-context.md), [liveops playbook](references/liveops-playbook.md). Для записів використовувати [форми](assets/liveops-templates.md) і [питання аналізу](assets/liveops-question-catalog.json).

Прийняти release-handoff та actual store/build/source/config/content/economy/catalog/save/experiment versions, studio/runtime masters, accepted model/rules, device matrix, entitlements, runbooks, alerts/support/known issues й rollback boundaries. Зіставити actual provider/client state з input hashes; `git HEAD` і старий ZIP не доводять current production. Немає read access — provenance/time-window export або exact blocker.

Визначити bounded round: incident, diagnosis, content, experiment, cost audit або patch; назвати affected cohort/platform/regions/time window і stop. Перенести чинні рішення/дозволи. Невідомі material choices — prices/catalog/paid randomness/irreversible progression/production/services/spend/regions — підготувати до рішення. Read-only analysis не дає права production write. Відсутність відповіді не є новим вибором.

## 2. Вивести належні питання й evidence

За actual features/model domains, player journeys, claims, impact graph і stage вивести обов’язкові diagnostics/regression; optional caller flags не скасовують активні domains. Disabled field при наявній runtime feature — contradiction upstream. Не ставити N/A через відсутній datasource/device: позначати limitation/not-tested й наступний спосіб доказу. Без покупок/ворогів/online не додавати їх штучно.

Structural/model, runtime, physical-device, human та live evidence — різні шари. `concept|preproduction|slice|beta|release` задають due gate за спільним workflow; liveops працює з поточним gate і фактичною доступністю когорти. Simulation показує outcome за assumptions; одноразова відповідь «повернувся б» не є retention; actual live measurement потребує datasource й часу. Фінальний звіт не підвищує рівень доказу.

Кожний finding має query/export/hash, time window/timezone, numerator/denominator/cohort/eligible/excluded/sample, build/platform/config/experiment/acquisition mix, event version/quality, uncertainty/confounders та decision impact. Відділяти bots/internal/sandbox. Перевіряти lost/duplicate/offline buffered events, clock skew/schema drift. Кореляція не є причинністю, відсутність даних не заповнюється «галузевими» цифрами.

## 3. Аналізувати весь досвід

- **Learning/journey:** first meaningful action, failure understanding/retry, tool/ability learning і transfer в новий encounter, assistance/dropoff, reward comprehension, next goal/return. Completion tutorial screen не доводить розуміння. Returning/lapsed player має знову знайти контекст і добровільну ціль.
- **Механічна різноманітність:** конкретні choices/builds/routes/encounters/resource trade-offs, strongest simple policy, dead systems/resources, camera/input overload і telegraph readability. Відмінний seed/колір/HP не є новим рішенням. Перевіряти які можливості реально використовують і в якому контексті; популярність не доводить єдину оптимальність, а рідкість — непотрібність без аналізу доступу/навчання.
- **Прогресія/нагороди/предмети:** time-to-meaningful-choice/unlock distributions, old-task-after-unlock, early/mid/late/mastery/collection/world goals, acquisition/caps/sinks, property/build synergy, failed-run value, повтори й exhaustion finite launch scope. Винагорода повинна відкривати зрозумілу можливість; інфляція чисел не заміняє розвитку.
- **Світ/AI/content:** encounter families/agent intentions/counters, reachable risk routes/optional return objectives, dynamic material/events, novelty/repetition budget та чесні generation constraints. Новий tool вимагає сумісних obstacles/encounters/teaching/rewards, а не лише нового item icon. Зберегти finite authoring capacity й production cost.
- **Commerce/shop:** exposure/decline/trial/purchase/pending/verified/use/expiry/restore/refund, precise price/content/duration/caps, free/no-offer route, paid cumulative portfolio/boosters/attempt economy. Вимірювати не лише conversion/revenue, а complaints/refunds/churn/fairness/value reuse й cost. Revenue не покращувати через приховано зіпсований baseline, штучні тупики або невказану зміну odds.
- **Technical/craft:** crashes/ANR/save/payment duplication/softlocks, sustained device performance/thermal/memory/network/audio/haptic/input, identity drift і accessible recovery. Стежити за accepted camera/style/animation/audio/UI/provenance при кожній релевантній зміні, а не лише при першому релізі.

Для людських питань використовувати actual добровільні feedback/playtests без вигаданих participants/quotes. Support/reviews — сигнали з bias, не репрезентативна когорта. Не збирати raw input/PII заради абстрактної аналітики.

Використовувати [4.0 diagnostic boundaries](references/v4-route.md): causal damage/death/crash traces, State/Continuity ownership, capability×opportunity та production attempts. Розділяти scenario lab, reason inspector і repro capsule; це setup, пояснення й повтор дефекту з різними доказами.

## 4. Сформувати й перевірити зміну

Проєктний урок записати з source/scope/confidence/applicability/dependencies; він не змінює автоматично глобальну навичку чи consent. Для patch/content/experiment створити точний mechanism hypothesis, affected rules/entities/journeys, expected observable/changed decision, resource/content/cost budget, migration й rollback-forward. Розповсюдити impact по camera/input/learning/art/audio/commerce/save/analytics dependencies.

Порядок за ризиком: model/invariants → staging/runtime → потрібні physical-device/store sandbox/human checks → незалежний QA → дозволений rollout. Code/native patch проходить build → QA → release; content-only теж потребує grammar/assets/gameplay/economy/compatibility checks. Підвищена complexity не є виправданням пропущеної контргри чи навчання.

Захистити earned progress і paid entitlements; не reset saves «для ремонту». Versioned source/sink ledger, draw/odds/pity/duplicate rules де обрані, carryover/expiry/grace, old-client compatibility, interruptible/idempotent migrations, restore proof і irreversible boundaries — до production. Subscription cancelled не завжди expired; consumed consumable не restore grant; refund/revocation мають заздалегідь визначену player recovery/support policy.

Для A/B спочатку визначити чи потрібний експеримент замість deterministic fix. Якщо потрібний: hypothesis/mechanism, assignment/sticky unit/eligibility, exposure, primary metric/guardrails, sample/duration/statistical method, stop/decision date, confounders/privacy. Не peek до зручної значущості, не приховувати змінені catalogs/odds, не робити персоналізоване погіршення гри за вразливістю. Low traffic → чесна uncertainty/qualitative test, не fabricated confidence.

## 5. Виконати дозволене й закрити раунд

Production actions лише в конкретному чинному scope; перед новим необхідним рішенням підготувати reviewable patch/config/rollback. Не перепитувати вже надане. Unknown outcome спочатку reconcile за provider receipt/state, потім вирішувати повтор. Для incident зберегти timeline/raw evidence, player impact, owner і точні mitigation receipts; комунікації іншим лише коли доручені.

Розрізняти halt rollout, exact feature/content/offer flag disable, compatible config/backend rollback і forward binary hotfix. Mobile binary downgrade не обіцяти миттєвим. Сумісність старих active clients, entitlement preservation й save recovery перевірити перед mitigation.

Повернути director checkpoint: exact sources/versions/hashes, observations vs hypotheses, queries/raw evidence/limitations, decisions, actual actions/receipts/customer-visible effects, case/metric coverage, support/runbooks, unresolved owners і next route. Перенести лише unchanged dependency evidence; style/economy/shared asset зміна відкриває downstream scope.

Не запускати нескінченний self-improvement/monitoring loop. Якщо recurring робота доручена, використовувати actual scheduler з frequency/source/privacy/cost cap/notification/stop rules; відсутній scheduler — точний manual route без заяви про background service. Витрати accounts/hosting/egress/API/tooling і післялімітні free-tier ціни аналізувати на actual provider terms.

Відкрити actual `--help` `scripts/game_model.py`, `scripts/atelier.py`, `scripts/pipeline.py`; використовувати спільні contracts. Structural exit 0 не сертифікує human interest або live revenue. Фінал: що встановлено, що фактично змінено, як перевірено, реальні наслідки/обмеження і конкретна next action.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
