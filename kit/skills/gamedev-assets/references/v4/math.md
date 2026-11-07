# Поведінка, математика, пошкодження й фізика 4.0

## Навігація

1. Форми правил і контракт
2. Damage resolution
3. Час, RNG і каскади
4. Фізичний adapter
5. Смерть, аварія, recovery
6. Еталони, приймання і джерела

Завантажити для будь-якої числової/часової механіки, ресурсів, damage, руху, контактів, станів і випадковості. HP, crit, вороги, ragdoll та repair є умовними можливостями гри. Точність власної активної механіки обов’язкова незалежно від масштабу.

## 1. Вибрати форму правила

Використати функцію/таблицю/криву для перетворення; автомат/decision table/алгоритм для дискретної поведінки; engine solver contract для фізики/навігації. Пов’язати змішані моделі exact boundary. Не створювати власний довільний eval/DSL всередині JSON.

`behavior-rule.template.json` задає каркас: ID/version/owner/requirement refs; purpose; typed inputs/outputs із units/domain/precision; source of truth; guards; алгоритм/function ID; update order; timebase; capture; RNG; state reads/writes; side effects; invariants; bounds/errors; presentation; persistence; fixtures; consumers. Локальні scripts/дані мають виконувати ту саму поведінку або проходити спільні еталони.

На C1 визначити характер і причину моделі, всі суттєві осі/взаємодії/винятки; tuning може мати обмежений діапазон і план. На T зафіксувати виконуваний порядок, початкові числа й допустимі tolerances. Формула без units і domain не є виробничим правилом.

Розрізняти additive від multiplicative, процентні пункти від відносного відсотка, current/max/missing resource, base/derived/cache, source/target і definition/instance. Для кожного override вказати priority/tie-break, для cap — місце застосування. NaN/∞, division by zero, overflow і недопустимі від’ємні значення відхиляти визначеним шляхом.

## 2. Побудувати damage-resolution contract

Розділити intention, фізичний контакт, eligibility, обчислення, наслідок і presentation. Callback overlap/solver не є готовим наказом зняти HP. Animation marker відкриває вікно, а факт контакту дає відповідний query/solver adapter.

| Етап | Вхід і обов’язковий вихід |
|---|---|
| Action commitment | Guard, витрата/cooldown, active window, cancel/refund → action instance |
| Contact candidate | Tick, method, engine/version, IDs+generation, shape/part, point/normal, доступні velocity/impulse |
| Hit eligibility | Authority/team/friendly fire/category/range/occlusion/window/immunity/dodge/repeat → accepted/reason |
| Канали | Typed effect components; delivery, damage channel, status і material окремі осі |
| Scaling/defenses | Capture + flat/additive/mult/override/conversion/crit/armor/resist/penetration/block order → intermediate values |
| Resources/parts | Barrier/HP/components/overflow mapping, actual loss і overkill без подвійного списання |
| Secondary effects | Buildup, DoT, stagger, interrupt, knockback, observation з exact predicates |
| Outcome | Lethal/part-break/phase/objective/credit/reward intents з arbitration |
| Simulation commit | Узгоджене застосування outcome в gameplay model → негайний hit feedback |
| Durability | Окреме збереження причинних груп/критичних confirmations за persistence contract |

Вибрати й версіонувати порядок конкретної гри. Ця таблиця задає потрібні рішення, не універсальний баланс або однакову armor curve.

Пакет повинен мати root/parent/action/effect/hit IDs, source/target instance+generation, instigator і credit owner, current team за правилом, part, tick, rules/catalog versions. Projectile ownership, kill credit і team можуть відрізнятися. Pooled ID guard захищає нову сутність від старого callback.

Визначити dedup scope. Один удар: `(action,target,active_window)`; multi-hit додає дозволений hit index; DoT: `(effect,target,tick)`. Це приклади, конкретний ключ залежить від механіки. Collider ID не множить удар по кількох hurtboxes автоматично. Replay/resume/repeated callback не створюють нового права на вплив.

Effect/stat contract охоплює type/units/domain, base/current/derived, scaling references, modifier groups, capture moment кожного входу, duration/tick/stack/cap, immunity, cleanup, source/credit, RNG, state/save, cues і oracle. Attack penetration не тотожне target armor reduction. Projectile piercing не означає обхід armor/barrier. Negative damage не стає heal без окремого healing rule.

Barrier визначає channel permissions, shared/per-channel pools, layer priority, decay, spillover і одночасність каналів. Parts визначають routing до global HP, чи залежить функція від part integrity, як змінюється collider/AI/control. Status buildup і stagger не тотожні HP loss. Кожний trigger обирає `accepted_hit`, `positive_mitigated`, `barrier_loss`, `actual_hp_loss` або інший названий predicate.

## 3. Зафіксувати capture, час і RNG

Кожний scaling input читається snapshot/live у названій точці: commitment/spawn/application/impact/tick. Заміна зброї після пострілу не змінює вже випущений projectile без такого правила. Source buff у DoT може snapshot, а target resist — live; це рішення, не випадкова поведінка коду.

DoT визначає rate в HP/s, tick interval/timebase, перший/останній tick, tick-before-expiry або інший пріоритет, partial tick, refresh vs independent stack, cap/overflow, pause/time-scale, scene exit, source death, cleanse, offline/catch-up і maximum work. Resume зберігає next tick, а не повторює останній.

RNG record визначає eligibility, distribution/weights, conditional dependencies, algorithm/version, seed/state або counter keys, consumed-roll policy, stream, history/pity/duplicates і accepted outcomes. Не припускати незалежність hit/crit/proc. `u∈[0,9999]`, success iff `u<p_bp` є можливим точним wrapper; якщо обраний, 0 і10000 мають граничні тести.

Ізолювати combat/loot/generation/cosmetic streams. Доданий випадковий SFX не змінює crit. Seed без algorithm/version/environment не гарантує довічний replay. Fixed timestep не гарантує кросплатформний детермінізм physics.

Reflection/retaliation/lifesteal/conversion формують bounded causal tree з root/parent IDs, own scaling і recursion guard. Вказати maximum chain depth/work, правила reflective children, нульового впливу й death. Test повинен завершити цикл reflect→leech→retaliate без нескінченних callbacks.

Одночасні події обробляти в названій atomic boundary й total order, наприклад `(tick,priority,stable_sequence)`. Lethal/phase/stagger/expiry/resurrection/objective отримують явний arbitration. Порядок обходу actor map не вирішує, хто помер або чи видано нагороду.

## 4. Визначити фізичний adapter

Обрати scripted motion, character controller, rigid body або гібрид за потрібним результатом. Вказати engine/backend/version, world units/scale, mass/inertia, timestep/substeps/catch-up cap, CCD, sleep, constraints, friction/restitution, layers/masks, query order, teleport, pause/slow-motion і transform ownership.

Collision matrix окремо охоплює blocking, hit/hurt, perception, interactable, pickup, support, debris. Sensor/CCD/contact semantics перевірити на pinned engine version. Відсутній impulse у sweep callback не означає фізичний нуль; зберегти `unavailable` і визначений fallback. Не переносити пораду Box2D між несумісними версіями без probe.

Контакт використовує відносну швидкість у точці, нормаль, матеріали/частини й потрібну provenance. Для 2D `v_contact=v_COM+ω×r`. За ідеалізованого одиночного контакту без тертя/інших constraints:

`1/m_eff=1/mA+1/mB+(rA×n)^2/IA+(rB×n)^2/IB`.

`J=(1+e)*m_eff*s`, де s — normal closing speed, e — restitution. Статична стіна має нульові inverse mass/inertia. Це допоміжний аналітичний oracle для зазначених припущень, не заміна solver для довільної сцени.

Contact-to-damage rule називає measurement, units/domain, aggregation window, threshold, curve, material/part mapping, saturation, exceptions і версію. Джоулі, Н·с, м/с і HP не додаються без перетворення. Gameplay knockback не дублює solver impulse непомітно.

Для moving platform визначити успадкування швидкості, detach, crushing, зникнення опори й teleport. Для controller→ragdoll→respawn визначити єдиного transform writer, velocities, contact reset і camera ownership. Interpolation змінює показ, не authority контакту.

Матеріали мають окремі physics properties, gameplay properties і presentation mapping. Shader «мокре» сам не змінює conductivity/traction. Authoritative break змінює collider/mass/support/function/topology/nav/visibility/cover/save; cosmetic debris має окремі lifetime/budget без сюжетної authority.

Після topology revision скасувати/перерахувати залежні paths, cover/visibility caches, encounter legality й цілі. Спроєктувати допустиму незворотність або rescue/альтернативний доступ. Не залишати обов’язкову ціль недосяжною випадково.

## 5. Описати життєві стани й failure

Розрізняти alive/downed/disabled/dead/despawned/respawning за задумом. Despawn representation і завершення death animation не означають kill authority. Аварія може ушкодити part, перекинути, обмежити керування, знерухомити чи завершити run; не прирівнювати всі contacts до смерті.

Failure profile містить cause/guard/authority, entry effects, permitted actions, timer, resources/parts, projectiles/statuses, collision/body, AI reservations, camera/cues, cargo/loot, terminal condition, recovery/rescue/retry, cost/refund, checkpoint/reset, world aftermath і persistence.

Перевірити одночасну смерть player/boss; lethal+phase+stagger; timer+resurrection; два rescue; reward callback після despawn; старий contact після respawn. Зафіксувати можливість skip phase/threshold clamp/spillover; не додумувати її в коді.

Recovery має повернути neutral input, коректну позицію/камеру, ресурси, world/encounter state, granted rewards і доступну наступну дію. Permadeath, втрата gear або платне продовження не є defaults. Причина поразки має спиратися на known-before-event інформацію й доступні responses (D1Q01–02).

### Не змішувати дві межі commit

Simulation commit узгоджує authoritative gameplay state одного outcome й одразу дає hit/UI/VFX/SFX/haptics. Він не чекає disk flush або cloud acknowledgement. Durable commit — окрема persistence операція для значущого стану. Critical reward/spend/victory confirmation прив’язати до належної durable межі; визначити bounded dirty/checkpoint window, writer queue, previous-good generation і recovery.

Асинхронний save не дозволяє втрачати підтверджену нагороду чи дублювати її. Водночас звичайний combat cue не перетворювати на очікування cloud. Конкретна гарантія після аварії має бути чесно описана гравцю.

## 6. Виконати еталони й контрприклади

Для кожного golden trace зберегти inputs, exact intermediate values, capture/time/order, expected final state, emitted/rejected events, durable obligation і tolerances. Independent oracle не отримує результат лише з тієї самої runtime функції.

Обраний ілюстративний damage oracle: physical100+flat20, increase25%, mult1.1, crit1.5; fire40×1.25; crit тільки physical. Armor100, K100, percent penetration.2, flat10; fire resist.25−.10=.15, тобто25% мінус10процентних пунктів; physical block20 після mitigation; ties-to-even по каналу; barrier30 physical-first; HP100. Physical до round125.588235…, fire42.5 →126/42; до HP138, actual loss100, overkill38. Це тест обраних припущень, не баланс нової гри.

DoT oracle: rate6HP/s, ticks.25…2.00 inclusive, target resist.25 на1–4 і.5 на5–8, barrier1.5, HP10. Total mitigated7.5, actual HP loss6, final HP4; stagger+2 тільки positive HP loss →14. Після tick4 HP7, resume починає tick5.

Physics oracle: центральний удар800kg у статичну стіну, s5m/s, e.2 →m_eff800kg, J4800N·s, initial normal energy10000J, loss9600J. За lever.5m і inertia200kg·m² m_eff400kg, J2400N·s. Числа не є HP чи прогнозом реальної травми.

Не оцінювати стратегії лише mean DPS. За HP30 і першої спроби t=1s: guaranteed10/s завершує3s;20 із незалежнимp.5 має те саме expected10/attempt, але mean4s, median3s, p95=8s. Врахувати overkill/threshold/time/resource/geometry/risk/opportunity, а не `HP/E[D]` як універсальний TTK.

Обов’язкові negative cases: кілька hurtboxes; stale pooled ID; zero/immune/barrier-only; expiry+refresh+tick; capture change між spawn/impact; NaN/overflow; reflection cycle; simultaneous death/phase; support break; time-scale/render skip; cold restore й grant-once. Перевірити thresholds, parameter sensitivity і платний portfolio. Structural/mathematical pass не доводить engine/native/human відчуття.

## Джерела й актуальність

Дослідження P1/D1/D2: 2026-11-02. При реальному engine binding читати відповідну version документацію й виконати probe; наведені моделі — наш вибір із названими припущеннями.

- Epic Gameplay Effects, attributes/effects/lifetime/stack/cues: https://dev.epicgames.com/documentation/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine
- Box2D Simulation, engine-specific contact/sensor/events/timestep: https://box2d.org/documentation/md_simulation.html
- Erin Catto, Sequential Impulses,2006: https://box2d.org/files/ErinCatto_SequentialImpulses_GDC2006.pdf
- Godot physics introduction: https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html
- Godot RNG, seed/state й implementation limits: https://docs.godotengine.org/en/stable/classes/class_randomnumbergenerator.html
- W3C SCXML, precise state/event interpretation: https://www.w3.org/TR/scxml/
