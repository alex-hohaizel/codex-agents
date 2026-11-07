# Системи гри, економіка та збереження

## Від опису до виконуваних даних

Дані мають stable IDs, schema version, localized labels, dependency IDs, source decision ref, expected runtime binding та fixtures. Не закодовувати повторно numbers з PDF в різних місцях. У repo зберігати canonical validated tables і генерувати runtime imports.

| Система | Мінімальна модель | Потрібні перевірки |
|---|---|---|
| Content | biome/arena/module IDs, connector grammar, difficulty tags, hazards, encounter budgets, excludes, unlocks | reachability, legal composition, no softlock, repetition window |
| Run | phase graph, choices, reward tables, checkpoints, fail/retry/exit, timer/seed | interrupted/abandoned run, seed replay, final state |
| Mastery | skill opportunities, timing windows, feedback, score meaning | improvement observable without pay; no auto-win reward |
| Meta | unlock graph, costs, prerequisites, caps, resets/prestige, catch-up | reachability from zero, unreachable/cyclic dependencies, long gaps |
| Mechanics variants | character/weapon/playstyle effects and counters | distinct behavior, dominance, synergies/exclusions, telegraphs |
| Economy | resource precision, sources/sinks/caps, exchange rules, acquisition time | conservation, overflow, negative balances, inflation, free path |
| Offers | SKU/group/type, price store ref, eligibility, cadence, content, refund policy | no duplicate grant, expired/missing offer, honest disclosure |
| Seasons | start/end/timezone, pass/free tracks, claims, rollover | offline/time skew, season end during transaction, unclaimed rewards |

Content generation використовує constrained grammar і validated modules. Не вважати кількість combinations доказом meaningful variety. Replay tests класифікують простір рішень/encounters, а curated seed suite містить boundary і погані випадки. Невдала генерація має bounded retries й tested safe fallback.

## Actors, equipment і динамічний світ

Споживати enabled model domains і exact IDs. Actor behavior включає доступні senses/knowledge/memory, goals/decision/action states, telegraph/commit/recovery/cooldown, movement/navigation, team/composition role, counters та adaptation bounds. Випадковість не дає невидимого знання або непередбачуваної атаки без cue. Test fixtures розрізняють стратегії у контексті, не лише HP/speed. Enemy AI не потрібен грі без відповідного виклику.

Equipment/property resolver має units, typed effects, target scope, evaluation/stack/refresh order, caps, synergy/exclusion і persistence. Відокремити stats від capability/access: бонус damage не замінює новий спосіб дії. Прогресія предмета/здібності/актора використовує модель конкретної гри, не обов’язкову RPG rarity tree. Для кожного залишеного параметра показати зміну рішення й відображення у UI/feedback.

World implements topology/connectors/gates, матеріальні стани/interactables, authored або constrained generated challenges, risk/reward routes, events/pacing і сталі наслідки. Revisit має зрозумілу добровільну ціль, доступ/шанс/обмеження та actual useful reward. Перевіряти invalid compositions, camera/navigation clearance, softlocks, несправедливі накладання telegraphs і repetition classes; bounded retries мають real safe fallback.

## Progression, rewards і learning

З model progression/rewards/learning вивести unlock/capability/knowledge dependency graphs. Кожне meaningful unlock має source/cost, new possibility, місце безпечного застосування, combination, known-context reinterpretation, наступну мету й reset/persistence. Finite launch повинен мати змістовний цикл і long arc; нескінченні seeds/цифрова inflation/щотижнева обіцянка контенту не підміняють спроєктований продукт.

Reward table/pool має version/trigger/eligibility, exact grant type/amount/cap, chance/guarantee/pity лише коли застосовно, duplicate/overflow/revoke і durable identity. Presentation слухає confirmed state. Нагорода повинна переходити у використання предмета/skill/access/world change; інертні очки не доводять reward system. Clock/retry/scene change не дублює grant.

Learning director активує hints/practice на actual prerequisites, розрізняє prompted і independent use, підтримує failure help/skip/re-entry та gradual reveal. Tutorial completion не дорівнює прочитаному tooltip. Human comprehension/mastery потребують окремого тесту з новим гравцем; agent walkthrough не є його заміною.

## Progression та economy implementation

Розділяти run power, persistent access, mastery та collection. Усі gains/expenses — typed events із reason, transaction ID, before/after state й version; округлення/precision явно. Не множити currencies без distinct role і зрозумілої UX conversion map. Обчислювати безкоштовний шлях, median/p95 acquisition time за явними model assumptions, bottlenecks, caps і refund corrections; це simulation results, не фактична поведінка ринку.

Автосимуляція перевіряє extreme policies: never buy, only starter purchases, high skill/low time, low skill/high time, full collection, returning player, bad RNG. Результат не доводить fun/fairness; для них є playtests. Платне mechanically different content має виміряні cumulative access/time/power effects та читабельні tradeoffs. Погоджена P1C допускає доречну перевагу часу/можливостей/сили; competitive fairness задається окремо. Не приховувати домінантний paid portfolio за словом sidegrade. Відхилення від погоджених меж повернути на конкретне рішення; не перепитувати вже затверджену модель.

## Purchase/reward state machine

Purchase: initiated → store_pending → purchased_unverified → verified → granted → acknowledged/consumed (точний порядок за актуальним SDK/store контрактом) або cancelled/failed/refunded/revoked. Не вважати `pending` успіхом. Reward grant durable idempotency key пов'язаний із authoritative purchase/transaction identity, а не лише client button press. Повторний callback/retry/restart не дає повторної винагороди. Аcknowledge/consume після durable fulfillment у дозволеному строку; server/device reconciliation відновлює незавершені операції.

Rewarded ads: eligible → requested → loaded → shown → provider-earned event → durable grant; no-fill/cancel/error не видають false reward. Винагорода рівно один раз і після background/restart; frequency cap/consent/child eligibility виконуються. Шлях без реклами лишається функціональним згідно з baseline.

Subscriptions, якщо обрані: pending, trial, active, renewal, grace/billing retry, account hold, paused, cancelled-but-entitled, expired, refunded/revoked. Перевірити authoritative store state, account mapping, restore, family-sharing якщо застосовно. Перевстановлення не повинне губити підтверджений durable entitlement.

Paid random rewards: exact pool/version/odds/guarantee/pity/reset/duplicate conversion, store disclosures та age/region rules перевіряються актуально. Purchase simulation і sandbox не є реальним revenue. Жодних undocumented hidden odds changes.

## Save, offline та sync

Save schema: version, game/content/economy version, profile identity, stable item IDs, progression, settings, run checkpoint, RNG state/policy, durable transaction journal, pending reconciliation, checksum/integrity policy. Atomic write із backup/recovery; відрізняти corrupted bytes, unsupported new schema і missing optional field.

Міграції однонапрямні й tested на historical fixtures; rollback app version не обіцяє rollback save. Дати forward-compatible reader або явний rollback boundary. Tombstones/deletion і guest→account merge мають explicit policy. Conflict resolution не «max everything»: це дублює ресурси. Серверний journal/ownership визначає monetary truth. Для local-only game cloud conflict має зрозумілий user-facing вибір із backup.

Offline: які features працюють, які чекають мережі, як повідомляється stale data/price, як expiry визначається без довіри до локального годинника. Device clock не створює infinite daily rewards. Retry bounded + jitter; stale requests не переозначують current screen state.

## Privacy та telemetry

Event schema має event ID, schema/build/content version, consent applicability, мінімальні fields, retention/deletion behavior. Не логувати access tokens, raw receipts, email або full persistent identifiers у QA artifacts. Маркетингові SDK й personal data collection вимагають належної моделі consent/age/region. Data safety/privacy labels виводити з фактичних SDK/мережевих потоків, а не зі слова «offline» у GDD.

## Damage/physics/lifecycle resolver

Розділити candidate contact facts і accepted gameplay hit. Action/target+generation/window dedup, hit eligibility, typed channels, additive/multiply/override/conversion/defense order, rounding/caps, barrier/globalHP/part overflow, positive-loss predicates, statuses/stagger/impulse й lifecycle priority походять із T. DoT має capture per input, exact tick/expiry/refresh/stack/pause/resume/offline policy, effect/tick identity; RNG streams і consumed-roll rules versioned.

Reflection/retaliation мають root/parent/effect ownership і bounded cascades. Despawn/representation cleanup не kill; crash може пошкодити модуль чи disabled без смерті. Simultaneous actor/boss lethal/phase/stagger/goal/rescue не залежить від iteration order. Rewards/costs/retry/checkpoint зберігають consistency group.

Simulation commit дає immediate coherent gameplay feedback, durable commit — підтверджену critical spend/reward/victory гарантію, cloud ack — sync status. Не чекати disk/cloud для ordinary hit, не підтверджувати durable success раніше відповідної межі.

## Повний State Catalogue і платформне продовження

Перелічити кожне mutable field із type/precision/units/initial/scope/owner/authority/lifetime, durable/reconstructible/ephemeral/cache/secret policy, commit trigger/consistency/restore/migrate/merge/delete/retention/privacy. Meaningful progress/equipment damage/world flags/AI phases/RNG/limits/settings/learning/pending grants зберігаються або відтворюються; touches/runtime pointers безпечно reset/rebuild.

Atomic generations/transactions мають serial revisions, stale-write guard, dirty/checkpoint window, good previous copy, disk-full/kill/corruption recovery. Restore перевіряє envelope/owner/version→migration→semantic invariants→coherent state→derived rebuild→safe controls. 64-bit IDs/seed round-trip точний; не завантажувати untrusted objects.

Cloud sync, OS backup, account migration та store purchase restore відокремити. Google platform PlayerID не universal primary profile; i Cloud owner не Game Center/store account. Actual Game Save/PGS/legacy SDK bridges і OS support перевірити під pinned build, не підвищувати мінімум ОС автоматично. Two-offline branches не max/union currency/inventory; spent→crafted causality та tombstone захищають consistency. Paid backend/cross-platform profile — лише обраний scope.
