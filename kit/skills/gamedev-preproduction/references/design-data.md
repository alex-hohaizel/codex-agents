# GDD/TDD як виробничі дані

## Обов'язкові розділи

| Документ/дані | Обов'язковий зміст | Критерій достатності |
|---|---|---|
| Product brief | Audience, fantasy, core promise, control, session shape, differentiation, full scope/non-goals | Людина розуміє перші 60 секунд, перший завершений цикл і причину повернення |
| Core rules | States, actions, inputs, guards, timing, hit/collision, score, fail/win/retry | Два виконавці отримують однаковий результат з тих самих inputs/seeds |
| Progression/content | Run/meta/skill/social layers, unlock graph, authored vocabulary, procedural grammar, pacing | Перші 3, 10 і late-game цикли показують матеріально різні рішення |
| Economy/commerce | Currency ledger, faucets/sinks, catalogs, availability, prices, earned/paid equivalence, refunds | Зрозуміло як баланс змінюється після кожної дії та збою |
| UX specification | Every screen/state/transition, layout/tokens, back/focus/keyboard, localization/accessibility | Немає неописаного reachable state або dead-end |
| Creative specification | Golden image, construction data, world/character/rig/motion/UI/VFX/audio/haptics | Asset producer знає що створювати, у яких одиницях, форматах, прийманні |
| TDD | Components/interfaces, event/data schemas, save/versioning/backend/security, lifecycle, platform | Можна скласти реалізаційний план без винаходу системної архітектури |
| Verification | Invariants, state coverage, seeded simulations, usability/fidelity/performance/device tests | Кожна requirement має artifact, owner, method, evidence type |
| Production plan | Dependency DAG, milestones, assets/components inventories, costs, risks, reopen rules | Жоден required item не схований за «інші assets» |

Створювати машинні таблиці поруч із поясненням; не копіювати значення в кілька незалежних truth sources. Документи посилаються на canonical IDs/data. Генеровані читабельні таблиці позначати як derived. Схему, одиниці, rounding, clamp, tie-break і versioning зберігати разом із даними.

## Мінімальний domain-data набір

Назви нижче — рекомендована layout, не заміна container schema спільного контракту:

- `design/core-rules.json`: actions, states, timers, units, ranges, deterministic resolution order.
- `design/input-map.json`: device/action/deadzone/gesture thresholds, buffering, cancellation, assist settings.
- `design/progression.json`: run/meta graphs, prerequisites, rewards, mastery, caps, resets, catch-up.
- `design/content-catalog.csv`: stable IDs, semantic tags, difficulty, prerequisites, weights, incompatibilities, source/asset IDs.
- `design/generation-rules.json`: grammar, budgets, constraints, seeded RNG/version, repair/fallback.
- `design/economy.json` plus `design/offers.csv`: currencies, earn/spend rules, prices, SKU, grants, availability, caps.
- `design/screens.csv` and `design/transitions.csv`: reachable state/action/guard/side effect/target/error/recovery.
- `design/events.json`: named domain events with schema/version/authority/idempotency; distinguish gameplay, audio, analytics.
- `design/asset-scope.csv`: every finite material item, variant/clip/state/consumer, quantity, dependency and acceptance.
- `design/quality-budgets.json`: target devices/FPS/frame-time/memory/install/load/battery/network/draw/texture/audio budgets.
- `design/verification.csv`: requirement→data→implementation item→test→evidence→owner.

`assets/domain-templates/` demonstrates domain forms, not universal schemas. Adapt them to the game without leaving unexplained TODO defaults. A template whose required fields are blank is draft.

## Numbers need meaning

Кажний numeric value має unit, source/rationale, allowed range, dependencies, authority, test case. «Retention 35%» без аудиторії, sample, event definition, denominator, observation window і uncertainty — target, не доведений результат. Simulated revenue — scenario, не forecast or real sales.

Повинні існувати worked examples: beginner/fair skilled/high-skill run; unlucky/lucky progression; payer/nonpayer at equivalent playtime; price/reward boundary; offline purchase return; interrupted save. Для складних формул включити виконуваний model/config/seed і raw result; повторювати тільки після зміни залежності або реальної невизначеності.

## Dependency cross-check

Одна named ability має ті самі IDs і semantics у combat, unlock, shop, UI, animation/event, save і analytics. Кожен status effect задає stacking, duration, refresh, immunity, death/reset, visual/audio feedback. Кожна reward задає source, grant, persistence, duplicate/retry і presentation. Відхилення ловити до build; не залишати «розробник розбереться».

## Спільна модель 4.0

Застосовувати [game-model-workflow](game-model-workflow.md), [model-format](model-format.md) та [design→runtime mapping](design-runtime-mapping.md). Рекомендована layout вище лишається допустимим derived export, якщо містить model IDs/version/hash і не стає другою authority. Нові camera/input/actors/world/rewards/learning forms конкретизують дані, які раніше могли лишитися всередині широких prose sections. Поле `{}` або список назв не закриває застосовний контракт.

## T: замкнений виробничий набір

Застосовні20напрямів отримують full launch rules/data/catalogue/grammar, всі reachable states/transitions/exceptions, finite asset/audio/UI/localization scope й exact production recipes. Для numeric rule задати typed inputs/units/domains, formula/table/function binding, порядок/round/clamp/capture, temporal policy, output/side effects та незалежний golden trace. Для discrete behavior — state/decision model, priorities/tie-break/commit/abort/recovery; для solver — pinned backend/config/inputs/tolerances/oracles. Не підміняти все довільним formula string/eval.

Додати State Catalogue/Consistency Groups/Save Resume Matrix/Migrations/Golden Saves; Actor/Knowledge/Action/Decision/Encounter/Boss contracts за fit; damage/contact/lifecycle profiles із dedup/ticks/RNG/priority та topology effects. Похідна layout може мати інші файли, але не іншу truth.

Для кожного material output: ToolCapabilityRecord, ProductionRecipe, SemanticTransformation, actual ProductionAttempt коли виконано, AssemblyEvidence коли зібрано. Blank template, behavior TBD, неповний launch catalogue або consumer без потрібних inputs не проходять T. Tuning uncertainty має стартове значення/range/мету/процедуру й не приховує невизначену поведінку.
