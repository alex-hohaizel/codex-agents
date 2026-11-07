# Каталог, сумісність, розвиток і винагороди 4.0

## Навігація

1. Вхід і виходи
2. Сімейства й конфігурації
3. Розвиток і opportunity
4. Винагороди й завершення
5. Приймання

Це окрема компетенція P1, застосовна до будь-якої системи змінних можливостей: інструменти, предмети, техніка, зброя, власні навички, здібності AI, модулі світу, колекції. Не перетворювати всі ігри на inventory RPG. Статична гра без upgrade може мати розвиток знання/доступних ситуацій; зафіксувати саме її модель.

## 1. Відновити inputs і межі

Прочитати player fantasy, active systems, mechanics/rules, world/encounter opportunities, progression position, reward/economy, art/audio budgets, save authority і commerce decisions. Зібрати чинні catalog IDs/instances, а не починати нову таблицю з несумісними назвами.

На C1 передати повну запускову таксономію, functional axes, family roles, progression lines, acquisition, compatibility, usable configurations, context trade-offs, видимий/звуковий feedback і виробничу здійсненність. Кілька demo upgrades не є повним простором задуму.

На T передати всі launch entries або точний генератор, ranges/types/units, function IDs, slot/tag/constraint predicates, weights, unlock/reward tables, fixture coverage, content-state inventory і authoring procedure. Якщо каталог generated, валідувати кожний accepted result; теоретична grammar без executable legality/fallback не закриває передачу.

Використати `catalog-progression.template.json`; completed status потребує конкретних IDs/даних/доказів, а не заповнення пустих масивів словом «комплексно».

## 2. Спроєктувати meaningful families

Для family створити:

- Role і player decision; сильний/слабкий context.
- Behavior/interaction difference, delivery/action/resource cycle.
- Typed parameter set із точним mathematical meaning, capture/time semantics.
- Requirements/slots/tags/exclusions/dependencies; composition rules.
- Acquisition/unlock/ownership/consume/repair/respec/loss.
- Learning/opportunity і горизонтальну/вертикальну progression.
- Asset/audio/animation/UI/physics bindings та persistent instance state.
- Test scenarios, known limits, production route/budget.

Відділити definition ID, instance ID і derived loadout stats. Великі IDs кодувати точно. Пошкодження/модифікація instance не переписує definition. Gameplay stats не дублювати незалежними числами в shop/UI/simulator/runtime.

Для легального loadout обчислити normalized typed components, prerequisites, allowed combinations, aggregate stats/effects, conflicts, resource capacity й result reasons. Override/stack/cap order посилається на behavior rules. `Invalid loadout` має конкретний reason code/поле/версію (D1Q29).

Перевіряти окремо item, family, pairwise interaction, extreme legal configurations і paid portfolio. Для малих просторів повний перебір; для великих risk-based boundary/combinatorial/property/state tests із явною межею. Не заявляти exhaustiveness за кількома random samples.

Dominance analysis виконується по однакових сценаріях/доступності/ціні/ризику/потребі у майстерності. One best item може бути задумним tier upgrade; пояснити, де старий лишається корисним або чому чесно retired. Простий сумарний score не приховує, що новий комплект прибрав усі weaknesses.

User-facing aggregate «керованість/пробиття/витривалість» має визначені weights/conditions і допомагає вибору. Додати зрозумілий опис поведінки; не видавати `+5` за універсальне покращення без одиниці/контексту.

## 3. Зв’язати розвиток і реальні нагоди

Progression node/edge: starting capability, prerequisites, condition/cost/mastery, exact change, newly possible decision, next goal, limits, world/encounter opportunity, tutorial/exposure, save/reset/loss/respec, presentation і acceptance.

Вести окремі graphs: run power, permanent unlock, equipment specialization, skill of human, collection, campaign/world access. Не підміняти розвиток генеративною перестановкою або однаковим HP scaling. Визначити early/mid/late/completed і repeat play meaningful decisions.

Capability×opportunity matrix пов’язує кожне сімейство з фактичними stages/biomes/encounters/generator contexts, частотою/доступністю, prerequisite timing і альтернативними рішеннями. Low pick rate не доводить слабкий баланс, якщо opportunity відсутня. Reward після останньої придатної сцени є дефектом timing.

Exposure graph задає відкриття, безпечне освоєння, transfer, combination, reinterpretation і recall після довгої перерви. Критичний late challenge має підготовку по різних routes або доступну альтернативу. Не нав’язувати всім одну лінійну школу.

Перевірити prerequisites graph на reachability, cycles/no useful exit, softlocks, forced grind, trap choices, недоступні currency sinks і complete build без шансів функціонально застосувати його. Respec/відсутність respec — продуктове рішення з ціною/commitment/rollback правилами.

## 4. Оформити reward як причинну операцію

Для кожного reward: trigger/eligibility, source/claim identity, deterministic amount або full distribution, roll timing/stream/pity, once/repeat scope, inventory destination, duplicates, cap/overflow, presentation, durable boundary, next use і retry/reconciliation.

Reward може відкрити action/route/world/property/knowledge/tool; абстрактне число без використання не закриває контракт. Підтверджена видача має durable consistency group із condition/cost/craft/quest flags. Animation, звук і cloud merge не є authority для нового grant.

Невдача/retry/repair/loot/rescue мають спільний аналіз exploit cycles і softlocks. `Death→insurance→repair→profit` не проходить лише тому, що кожне правило окремо валідне. Розподіл часу до цілі включає tails/guarantees, а не лише mean.

На completion/max upgrades/full collection визначити: excess currency/materials, duplicate conversion, pity/guarantee exhausted state, offers, valid next goals, authored ending, replay і future content boundary. Не обіцяти невипущений контент як готовий.

## 5. Прийняти дані й authoring

Автор змінює canonical entry→semantic validation→preview/runtime fixture→diff→consumer acceptance. Інший виконавець має додати легальний family/варіант без копіювання формул по файлах (D1Q27). Нелегальний entry пояснює конкретну причину.

Негативні cases: перефарбовані «нові сімейства»; missing asset state; incompatible modules; cycle prerequisites; paid portfolio closes all trade-offs; overflow на повній collection; duplicate grant; shared RNG changed через cosmetic; migration removed definition; old save restored consumed item; tool unlocked after opportunity exhausted.

Перед mass production провести один representative entry через concept→source→export→import→integration→QA й виміряти actual repair/cost/cadence (Q36). Обіцяний каталог має виконуваний pipeline, а не лише арифметичне число combinatorial variants.

Зберегти structural/math/simulation/runtime/native/device/human status окремо. Meaningful diversity/comfort не доводяться довжиною таблиці.

## Джерела

Опорні джерела досліджено2026-11-02; formulas/generator instances обирає конкретна гра.

- Epic Data Driven Gameplay, typed data/curves: https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine
- Godot RNG, versioned state limitations: https://docs.godotengine.org/en/stable/classes/class_randomnumbergenerator.html
- Valve AI Director, opportunity/pacing context: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- Steam bundles, ownership-aware composition example: https://partner.steamgames.com/doc/store/application/bundles
