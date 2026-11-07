# Preproduction: виробничий контракт T у 4.0

## Вхід і дозвіл

Прийняти обрану C1 revision/hash, accepted originals/decisions, чинні budgets/platforms та authorized scope. C1 визначає продукт; T замикає всі поведінкові та виробничі рішення для реалізації. Не перетворювати favored candidate на selected game. Ранній spike має окремий вузький експериментальний контракт.

## Розгорнути кожну активну систему

Для кожного з 20 напрямів зафіксувати purpose/owner/consumer, read/write state, правила, залежності, launch catalogue/grammar, progression, UI/camera/audio, authority/save, бюджет, invariants, oracle і due proof. Непов’язана гілка може продовжуватися, коли інша має blocker; consumer невизначеного behavior не починає production.

1. **Rule Contract:** stable ID/revision, typed units/domain/precision, initial state, guards, function/table/curve/state machine/solver config, update/priority/tie-break, capture time, side effects, presentation, save й golden examples. Параметр tuning має початкове значення, range, мету й change procedure; behavior TBD не допускається.
2. **Damage/physics/lifecycle:** intent→contact facts→eligibility→channels→modifier/defense order→barrier/HP/parts→statuses/reactions→terminal/objective/credit/reward. Окремі delivery/channel/material/status; dedup за action/target/window або effect/tick. Snapshot/live на кожному input, DoT schedule/expiry, RNG streams/roll consumption, recursion guards. Contact impulse/energy не є HP без unit-safe policy.
3. **Failure semantics:** alive/downed/disabled/dead/despawn/respawn за fit; simultaneous lethal/phase/stagger/objective, projectiles/DoT/slots/colliders cleanup, loss/keep/cost/retry/recovery. Simulation commit дає негайний combat feedback; durable commit критичного reward/spend/victory і cloud ack — окремі межі.
4. **AI/world/narrative:** знання/пам’ять із каналом/TTL/confidence, decision/action traces, encounter legality, boss phases/priorities, topology revision при руйнуванні, nav/visibility invalidation, lore flags. Генератор має executable constraints, repair budget і fallback; зміна difficulty не маскує progression.
5. **Каталоги:** повний launch inventory або визначений generator, сімейства/compatibility/slots/tags/caps, sources/chances/pity/guarantees, upgrade/build/respec/repair. Перевіряти allowed/forbidden combinations, strongest simple policy, cumulative paid portfolio й capability×opportunity.
6. **UX/input/craft:** state atlas з back/cancel/empty/error/commit, touch traces/pointer ownership/recognizer, camera request arbitration, learning diagnosis/transfer/reorientation, localization contract. Functional states→editable sources/clips/cues/screens/variants; timing/units/axes/color/loop/markers і sensory fallback точні.
7. **Persistence:** повний State Catalogue, schema/envelope/consistency groups, atomic generations або transactions, dirty window, migration/merge/delete/retention, golden saves й failure injections. Platform identity, cloud owner, store account та game profile різні; cloud/OS backup/purchase restore окремі.
8. **Runtime/production:** idiomatic module interfaces, pinned engine/exporter/platform adapters, validated data mapping, 45operation applicability, recipes/transformation obligations/attempt ledger/assembly evidence. Не додавати backend чи універсальну DSL заради форм.

## Замкнути вихід

| Вихід | Обов’язковий зміст |
|---|---|
| GDD/TDD projections | Versioned canonical IDs, всі стани/винятки/алгоритми/порядок/час/units; без окремої authority у PDF |
| Data/content package | Full launch rows/curves/graphs або generator + constraints + fallback; semantic validation |
| Production package | State-covered asset/audio/UI/localization inventory, sources/rights, exact operations/recipes/bindings/consumers/budgets |
| Test package | Independent oracles, intermediate numeric traces, boundary/fault/composition cases, golden saves/input traces, engine/native/human due layers |
| Receiver acknowledgement | Assets/build відкриває пакет без чату, запускає дозволені examples і знаходить всі needed inputs; exact gaps/owner |

Валідний JSON, named formula чи reviewer receipt не доводять повноту T. Перевірити interaction edges: нове пошкодження колеса змінює handling, routes/generation, touch/camera, presentation, repair/economy, learning/save й tests. Не створювати зв’язки всіх пар без предметної причини.

## Контрприклади

Непроставлений rounding/capture/stack order; key behind own lock; simultaneous boss/player death залежить від actor iteration; max/union cloud дублює spent material; два rescue списують ресурс двічі; reward animation виступає grant authority; GLB без contact/scale semantics; TDD не описує exhaustion. Усі мають точний expected trace або визначену відмову.

Перед mass production потрібний representative native slice за due modality. Недоступний device не знімає obligation; structural T acceptance не доводить fun/comfort/60FPS. Передати hashes, actual evidence, unresolved future proof й authorized next action.
