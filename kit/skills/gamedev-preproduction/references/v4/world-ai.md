# Світ, ситуації, противники й боси 4.0

## Навігація

1. П’ять шарів світу
2. Generator і різноманітність
3. Actor/knowledge/action/decision
4. Encounter і boss
5. Інтеграція, збереження й тести

Застосувати до будь-якої просторової структури, маршрутів/сцен, живого оточення, NPC/супротивників і генерації. Відсутність ворогів або PCG допускається предметним задумом. Не додавати RPG, відкритий світ, bosses чи LLM agents заради заповнення реєстру.

## 1. Скласти узгоджений світ

| Шар | Що зафіксувати | Перевірка |
|---|---|---|
| Авторська основа | Ідентичність, geography/topology, канон, орієнтири, незамінні сцени | Впізнаваність і причинність не руйнуються варіацією |
| Місія/розвиток | Цілі, prerequisites, доступні capabilities, освоєння, ризик/винагорода | Потрібна можливість доступна до виклику |
| Простір | Модулі/траси/кімнати, transitions, routes, visibility/reachability | Ціль досяжна, переходи легальні |
| Ситуація | Ролі загроз, ресурси, погода, події, стан об’єктів, темп | Поєднання лишає заплановані відповіді |
| Стійкі наслідки | Memory, фракції, відбудова/руйнування, відкриття, reaction | Restore й повернення відтворюють причинний стан |

Розділити виробничий scale, spatial topology, тривалість розвитку й complexity. Small гра може мати глибокий компактний світ; large гра може складатися з пов’язаних authored локацій. Тридцять трас не є моделлю lifecycle. Авторські/hybrid сцени дозволені з поясненням, де й чому варіюються інші шари.

На C1 описати структуру світу, функціональні сімейства ситуацій, повний маршрут розвитку/повернень/завершення та точні типи вибору. На T дати topology/mission/progression graphs, module ports, parameters, exact conditions/weights, authoring source, generation algorithms, validation/repair/fallback й fixtures.

Для route edge визначити доступність/умову, state transition, required capabilities/resources, інформацію до вибору, ризик, gameplay distinction, нагороду, commitment/return/escape, presentation і persistence. Колір коридору сам не створює іншого рішення. Необов’язковий ризик не стає прихованою вимогою купівлі.

## 2. Реалізувати bounded генерацію

Вхід: accepted player/world revision, capabilities/loadout, progression position, learned mechanics/exposure, difficulty profile, session budget, history і isolated generator RNG/version.

Алгоритм:

1. Обчислити допустимі цілі й context envelope; не семплувати несумісну ціль з надією потім виправити.
2. Вибрати mission structure та authored опори за правилами.
3. Розкласти spatial modules із port/type/scale/nav/material compatibility.
4. Побудувати маршрут/ключі/ресурси/зустрічі/події в межах constraints.
5. Перевірити reachability, prerequisites, resource feasibility, timing/counterplay, lore, semantic diversity й budgets.
6. Застосувати названі локальні repairs у maximum count/time budget.
7. Повторити sampling лише в установлених bounds; за exhaustion взяти перевірений compatible fallback.
8. Зберегти accepted result/seed/algorithm version/history/repair reasons; rejected sample не стає світом гравця.

Валідація має охоплювати ключ до власного замка; одночасні взаємовиключні flags; потрібний tool після останньої можливості його отримати; неспроможність завершити з ресурсами; невидимі неминучі attacks; знищену опору; exit без return; performance envelope. Залежні системи мають отримати topology/content revision.

Не оцінювати новизну числом seeds. Описати semantic signature: рішення, потрібні capabilities, role combination, route trade-off, resource pressure, environmental interaction, known/unseen mechanic. Вимірювати фактичні повтори/покриття/довжину novelty runs на визначених політиках гравця. Позначати обсяг симуляції й неперебраний простір.

Ритм, difficulty і progression — окремі моделі. Pacing може чергувати intensity/recovery, але не потай підсилювати ворогів рівно після кожної покупки. Hidden adaptation за успіхами/покупками не є default. Transparent optional assist/difficulty має окремий контракт.

Вести challenge vector: spatial precision, reaction time, simultaneity, information pressure, resource pressure, penalty. Зростання одного виміру не повинно випадково піднімати всі. Для давно невживаної механіки перевірити exposure і доступні альтернативи (D1Q05,Q09,Q10).

## 3. Проєктувати AI через досвід і відоме знання

### Actor contract

Для кожного family задати role→observable distinction→player response→prerequisite/tool→strong/weak context→combinations→progression position. Числовий рівень/перефарбування є варіантом, а не новою поведінковою сім’єю.

Паспорт actor: definition/instance IDs, motivation/goal, body/scale/shape, movement/turn/acceleration, collision/hit/hurt/parts/materials, resources/stats/armor/resists/statuses, abilities, perception, knowledge, decisions, navigation/positioning, coordination, signals/counterplay, progression/variants, failure/recovery/despawn, reward/credit, state/save/LOD/budgets/diagnostics.

Для союзників додатково перевірити blocking, stealing agency/rewards, scene interruption і нав’язливість. Sleeping/LOD actor не прокидається з уже завершеною невидимою атакою. Фізичне тіло, collider і animation не можуть незалежно визначати несумісні положення.

### Knowledge contract

Відділити world truth від observed fact і belief. Fact record: subject/predicate/value, source/channel, observed time, location/uncertainty, confidence, TTL/decay, refresh/forget, share recipients/delay/range, privacy/authority. Loss of sight не дорівнює миттєвому забуванню або вічному точному tracking.

AI не читає неприйнятий input, майбутній RNG чи всю world truth як sensor. Після шуму можливе дослідження last-known area, а не telepathic атака актуальної позиції. Shared knowledge має визначений канал і час; perception event не копіюється магічно всій фракції.

### Action і decision contracts

Action: eligibility/guards, costs, startup/telegraph, target lock/tracking, active geometry/window, commitment, combo transition, interrupt/cancel, recovery/cooldown, resource refund, movement/physics ownership, capture/RNG, cues, expected result і failure.

Decision: alternatives, eligibility, scoring/priority, tie-break, reevaluation cadence, commitment/hysteresis, abort conditions, budget, fallback. FSM/HFSM, behavior tree, utility, GOAP/HTN обирати за authoring/debug/runtime needs; найбільший алгоритм не є кращим автоматично.

Trace пов’язує відомі факти→допустимі альтернативи→причину вибору→команду→фактичний результат→replan. Логи обмежити бюджетом/retention, не відкривати гравцю приховане знання. Зруйнована опора/зайнятий slot/недоступний ресурс мають reason і fallback.

Для небезпеки порівняти досяжний response time з cue availability/visibility/input latency/action startup, але не видавати позитивну арифметику за доказ людського комфорту. Помилкова позиція не зобов’язана завжди бути врятовною; перевірити, що гравець міг знати до commitment.

## 4. Оформити encounter і boss як окремі contracts

Encounter: purpose/objective, arena/routes/visibility, allowed roles/compositions, prerequisites, spawn/entry/exit, resource envelope, attack concurrency, coordination, pacing/recovery, win/fail/abort, reward, save/resume і budgets.

Threat points не доводять legality. Перевірити поєднання crowd control, взаємне нескінченне лікування, закриті responses, spawn біля гравця, blocking, camera occlusion, resource starvation. За потреби attack slots/position reservations/team roles мають owner, TTL, release/cancel/death, fairness/starvation policy. Не нав’язувати slots усім жанрам.

Boss blueprint визначає призначення: перевірка mastery, narrative turn, переосмислення систем, optional apex або spectacle. Кількість фаз не є quality score.

Обов’язкові поля boss: prerequisites, arena/camera, full action catalogue, phase graph, exact triggers/priority, HP threshold/overflow, stagger/interrupt, projectiles/status keep/remove policy, body/parts/weakpoints, minions, combo grammar/RNG bounds, teaching, accessibility, loss/retry/checkpoint, resources/rewards/world flags, save/migration, content and budgets.

Вибрати outcome одночасних lethal+phase+stagger й player/boss death; animation end не видає reward. Перехід не лишає старий collider, нескінченну invulnerability, reservation або duplicate grant. Визначити, чи дозволено phase skip і куди йде excess damage.

## 5. Живість із причинністю

Розклади, локальні події, погода, шум, ecological/resource reactions, NPC routines і persistent aftermath активувати там, де вони створюють досвід. Задати activation/simulation radius, offscreen approximation, update rates, maximum active entities, LOD transitions і authoring ownership.

Offscreen simplification зберігає важливі інваріанти й не вигадує неможливі outcomes. Ambient animation не вважається повною simulation. Живий світ не вимагає величезного open world чи нескінченної фонoвої симуляції.

Пов’язати стани actor/action/variant із rig/clip/contact markers/VFX/SFX/haptic/UI, runtime bindings і сценою. При break змінити topology revision та AI plan; при death звільнити slots, скасувати неприпустимі commands, створити exact reward intent.

Кожне AI поле отримує persist/recompute/reset policy. Відновлювати logical state/knowledge за правилами; paths/planner pointers перераховувати. Restore dependencies: world topology→actors/resources→knowledge→decisions→presentation→neutral input. Зміна engine/content потребує сумісності golden saves і actor bindings.

## 6. Перевірити наскрізні контрприклади

- Ключ розміщено за власними дверима: deterministic rejection/repair/fallback, причина й seed записані.
- Новий tool відкрито, але generator ніколи не дає opportunity: coverage defect, не лише low pick rate.
- Ворог нічого не бачив/чув: немає точних player coordinates.
- Два actors претендують на slot; смерть owner звільняє його без starvation іншого.
- Зруйнована опора під час плану: path invalidated, actor не виконує старий jump.
- Correct attacks окремо утворюють unavoidable combo: encounter відхиляється.
- Cue схований VFX/пальцем/камерою/мовою: visual review проходить реальну peak scene.
- Одночасні phase/stagger/lethal: golden outcome без actor iteration dependence.
- Kill між boss victory і durable reward: одна причинна consistency group після restore.
- Sleeping actor повернувся; стара attack не влучає до нового readable telegraph.
- Late old callback після respawn/profile change відхиляється revision/generation binding.
- Приймач без чату реконструює encounter/phase/retry зі специфікації й власним counterexample.

Документальне приймання не замінює scene/native/device/human evidence. До масового тиражування контенту провести representative slice та sample production throughput.

## Первинні матеріали

Опорне дослідження P1/D1/D2 перевірено 2026-11-02; pinned engine APIs перевіряти повторно під реальний проєкт.

- Valve, The AI Systems of Left4Dead: perception/navigation/behavior/pacing, не універсальний DDA: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- Epic AI Perception: https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine
- Epic Behavior Trees: https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine
- Epic Environmental Query System: https://dev.epicgames.com/documentation/unreal-engine/environment-query-system-in-unreal-engine
- Dormans, Adventures in Level Design: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
- Godot Navigation introduction: https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_introduction_2d.html
