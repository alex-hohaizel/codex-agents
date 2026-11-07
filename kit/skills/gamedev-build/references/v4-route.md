# Build: реалізація за контрактами 4.0

## Admission

Прийняти selected concept і точний T/вузький spike contract, validated model/data, accepted sources, independent fixtures, versions/locks/target devices, costs/rights та authorized scope. Звірити inputs і компетенції з recipe; один writer на source/scene, окремо резервувати shared device/account/export jobs.

## Реалізувати й інтегрувати

1. Виділити pure rule/state/data частину й engine/platform boundaries. Використовувати idiomatic typed gameplay code та придатні компоненти/state machines/events; framework обирати за операцією. Backend, PostgreSQL, Go/PHP або GDExtension не додаються автоматично.
2. Завантажувати canonical validated data через versioned adapters; відображення units/precision/capture/order/timing перевіряти shared golden fixtures. Не переносити формулу в інший client без conformance tests.
3. Розділити physics detection і gameplay resolver: contact provenance/IDs+generation, eligibility, action/target/window dedup, channels/effect order/capture, resources/parts, statuses, lifecycle/credit/reward. Multi-hit/DoT tick мають власні повтори. Немає довільного eval з imported data.
4. Physical backend має pinned units/time/substeps/layers/CCD/sleep/constraints/ownership. Relative contact velocity/impulse/energy використовуються лише через design contact-to-damage policy; unavailable field не підміняється нулем. Додатковий gameplay impulse не дублює solver response.
5. Задати deterministic gameplay priority для lethal/phase/stagger/objective/rescue. Downed/disabled/dead/despawn різні; cleanup не grant authority. Transform ownership controller→ragdoll→respawn і topology revision руйнування мають навігаційний/visibility/cache fallback.
6. Застосувати coherent simulation outcome для негайного combat feedback. Durable reward/spend/victory boundary, async save queue/generations/dirty window й cloud ack окремі; frame не чекає мережі. Kill/retry не дублює effect/reward/cost.
7. AI отримує лише allowed knowledge channels/TTL/confidence; decision trace пояснює alternatives/tie-break/commit/abort/fallback. Encounter/boss states, reservations, pauses/LOD, timers і restore не запускають непоказану атаку.
8. Реалізувати content grammar, progression/rewards й economy зі constraints/novelty/opportunity/exhaustion; paid cumulative portfolio, assists і вільний базовий journey перевіряються разом із save.
9. Реалізувати stable pointer ownership, cancel/release/modal transitions, camera request arbitration, HUD/learning/error/reorientation й localization. Physical touch comfort та tactile evidence не виводити з unit tests.
10. Звести actual source/export/import recipes та asset/sound/event consumer bindings у representative native slice. Після runtime parity виконати required native/device/human checks до масового контенту.

## State & Continuity

Покрити кожне змінне поле State Catalogue: durable/reconstructible/ephemeral/cache/secret, owner/type/scope/authority/commit/consistency/restore/migrate/merge/delete. Екземпляри/64-bit seeds кодувати точно, перевіряти semantic invariants, не десеріалізувати untrusted objects. Contact pointers/input reset, значущий прогрес зберігається або відтворюється за погодженою гарантією.

Cloud sync, OS backup, store purchase restore й cross-platform account — різні contracts. Перевірити profile/account/session binding, quota/conflict/reinstall, two-offline branches і tombstone; не max/union currency/inventory. Actual Google/Apple SDK bridges потребують operation conformance та signed release tests; документація не доводить integration.

## Потрібні інструментальні outputs

| Output | Визначення |
|---|---|
| Scenario lab | Fixture/seed/loadout/locale/input/sensory profile, stress/fault setup; dev-only access |
| Reason inspector | Пояснення runtime decisions/modifiers/AI/eligibility за current state; не замінює repro |
| Repro capsule | Sanitized state/config/seed/input/event trace і точний build для повтору дефекту |
| Production attempt | Actual toolchain/invocation/job/output/cost/status; unknown outcome reconcile |
| Native artifact | Exact source/assets/config/locks→signed output/hash/symbols→install/run receipt |

Перевірити cold first-use, transition RAM/VRAM overlap, cumulative load/unload, frame-time/input distributions, thermal/low-tier, fallback profiles. Quality adaptation за окремим вибором не змінює gameplay-critical rules/cues; input responsiveness не доводиться самим 60 FPS.

## Приймання й handoff

Meaningful unit/property/model/integration/fault tests повинні відрізняти правильний outcome від контрприкладу; independent oracle не копіює implementation. Передати QA sources/data/saves/recipes/bindings/builds/symbols/exact traces й coverage/gaps. Android/iOS, editor/simulator/device і self-check/independent review мають окремі statuses. Результат встановлення навички не є прийманням гри.
