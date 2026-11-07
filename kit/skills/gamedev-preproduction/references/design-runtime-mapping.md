# Перетворення задуму на дані та runtime

Використовувати common model format як authority для назв типів і полів. Наведений нижче domain checklist уточнює семантику; це не друга конкуруюча schema. Суб'єктні форми в `assets/domain-templates/` залишаються draft attachments до записів моделі, доки їх не заповнено й не прив'язано до IDs.

## Один ланцюг ідентичності

`джерело/намір → model record → правило/дані → runtime consumer → сценарій → observed evidence`.

Для кожного record визначити owner, dependencies, source decision, stage/due gate та evidence kind. Для кожного runtime consumer: actual scene/component/module/config field, import/generation recipe, update/reset/persistence authority й acceptance scenario. Документ, таблиця і runtime не мають власних незалежних копій значень. Похідні exports містять source model version/hash, recipe version і mapping; після зміни inputs їх перевипускати.

| Контракт | Предметні поля, які треба вирішити | Залежні consumers/перевірки |
|---|---|---|
| Камера | Projection, follow/lookahead/limits/damping/zoom, mode transitions, key-object screen envelope, reaction visibility, occlusion/offscreen, aspect/reduced motion | Camera controller, world geometry, HUD, art density; normal/peak/transition captures |
| Керування | Gesture/action, units/thresholds, ownership/concurrency, context guards, press/release/cancel, buffer/assist, feedback/latency target | Input adapter, gameplay intent, animation, camera, UI; interrupted/two-thumb/low-FPS fixtures |
| Дія/здібність | Preconditions, phases, costs, target rules, resolution order, state transforms, cooldown/cancel, counters, consequences | Simulation, actor AI, collision, events, UI forecast, save; before/after scenarios |
| Actor | Role, senses/knowledge/memory, decision states/goals, actions, navigation, telegraph/commit/recovery, adaptation bounds, counters, spawn/composition budgets | Behavior implementation, encounter grammar, motion/cues, perf; composition and unfairness tests |
| Предмет/властивість | Units/formula, affected rule, range/cap, stacking/refresh/order, synergy/exclusion, availability, equip/use/upgrade, reset/persistence | Inventory, rule resolver, collection/shop, cues, migrations; meaningful use and exploit fixtures |
| Світ/маршрут | Topology/access, connector/entry/exit, materials/interactables, risk/reward choices, event constraints, revisit objective/chance/persistence | Scenes/generator/navigation, encounters, camera, progression/save; reachability and novelty classes |
| Розвиток | Prerequisites/costs, capability gained, practice context, combination, known task reinterpreted, next goal, catch-up/reset | Unlock authority, content gates, learning/UI, rewards; zero-state reachability and long-arc scenarios |
| Винагорода | Trigger/eligibility, pool/version/probability when relevant, exact grant, duplicate policy, persistence, notification, first use | Reward ledger, progression/inventory/world, presentation, analytics; duplicate/restart/revoke cases |
| Навчання | Knowledge prerequisite, trigger, cue, safe practice, application, combination, independent transfer, failure help/skip/return | Onboarding director, level/encounter, input/UI, save, measurements; first-time player task |
| Commerce | Concrete desire/offer, model fit, eligibility/caps, SKU/grant/price authority, free/decline path, cumulative effects, pending/refund/restore | Catalog/store adapter, economy, inventory, UI, support; transaction-state and portfolio cases |
| Craft | Exact target/hash, fixed properties/tolerances, editable source/export/import, functional state variants, semantic events, rights | Assets/materials/rig/clips/UI/audio/haptics, runtime assembly; source reopen and contextual review |

## Проєктувати конфлікти до коду

Задати правила одночасних ефектів, пріоритети й tie-break: дві дії на той самий об'єкт; перехід сцени під час нагороди; витрата останнього ресурсу й upgrade; заміна kit без refill/reset; AI telegraph при закритій камері; смерть під час grant; offline return до простроченого offer. Значущі недетерміновані рішення мають policy/version і відтворюваний evidence context; не обіцяти cross-platform bit-identical physics без відповідної реалізації.

Пройти щонайменше релевантні класи: початківець/майстер; рання/середня/пізня гра; базове/альтернативне оснащення; ризиковий/безпечний маршрут; удача/поганий draw; mute/no-haptic/reduced-motion; вузький/широкий пристрій; переривання/повернення. Кількість прогонів визначається покриттям ризиків, а не довільною великою цифрою.

## Сценарій як oracle

Записати точний initial state/config/seed, доступні дії, очікувані наслідки й **рішення, яке має змінитися**. Прив'язати cue/asset/UI/data IDs. Відокремити розрахований результат, review of design і фактичне runtime спостереження. Метрика «заповнено 100% полів» не доводить осмисленість.

Приклади провалу: нова здібність відкриває лише більший damage; різні вороги завжди змушують той самий маневр; інша локація міняє текстуру; camera target вміщує все, зменшуючи потрібну дію; нагорода не використовується; куплений набір обходить усі слабкості; навчання показане, але гра не перевіряє розуміння. Автор має усунути причину або явно змінити scope, а не переписати опис.

## Due proof

Design freeze потребує узгоджених конкретних контрактів, виконаних необхідних моделей і незалежного semantic review. Representative slice потребує actual source→import→runtime та названих перевірок before mass production. Physical comfort/haptics/thermal потребують пристрою; human fun/comprehension — людей; revenue/retention — реального спостереження. Незавершений пізніший доказ має owner й due gate, але не стає завершеним сьогодні.

## Сумісність і gates

Поточну schema4.0 та CLI визначає [model format](model-format.md); попередні формати результатів не імпортуються. Предметна карта використовує domains camera/input/systems/actors/world/progression/rewards/learning/art/commerce/lifecycle/equipment і stable IDs. Зберігати dependencies та scenarios з initial_state/action/expected_observable/changed_decision/without_rule; evidence записувати лише після actual observation. Чинні gates: concept, preproduction, slice, beta, release. Design freeze перевіряється preproduction; вузькі assets/build роботи — slice. Handoff1.0.0 і runtime2.0.0 є чинними окремими протоколами з marker toolkit4.3.0.

## Контакт, outcome та продовження

Пов’язати action instance/target generation/window → contact facts/provenance → eligibility → typed channels → exact modifiers/defenses → resources/parts → statuses/reactions → lifecycle/objective/credit/reward intents. Hit dedup не забороняє явно спроєктований multi-hit; DoT має effect/target/tick identity, capture і expiry priority. Contact impulse/energy не є HP без окремого unit-safe mapping.

Simulation commit застосовує coherent gameplay state й негайний hit cue; durable commit забезпечує critical reward/spend/victory гарантію; cloud acknowledgement відділений. Матриця містить kill/retry/reorder/duplicate/resume та actor+b о ss simultaneous death. Декоративний cleanup не authoritative kill.

Кожне spec→source→export→import→runtime ребро задає preserved properties/units/axes/timebase/color/audio, intentional losses, actual mapping і validator. Valid GLB або WAV не доводить deformation/contact/loop/semantic parity.
