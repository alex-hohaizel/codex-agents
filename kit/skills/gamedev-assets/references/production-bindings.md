# Від моделі гри до виробничого матеріалу

Читати до inventory, першого source або зміни системного стану. Canonical intent/rules знаходяться у моделі гри за [model workflow](game-model-workflow.md). Цей контракт зберігає виробничі рішення й докази, а не другу предметну істину.

## Binding record

Використати `assets/domain-templates/production-bindings.template.json`. Вказати exact model path/hash/revision; domain/object/state/event IDs; required representation; accepted target/property locks; sources/exports/recipes/importers; runtime consumers; scenario/evidence IDs; owner/status. Для кожного exported параметра, що відтворює правило гри, задати derivation або copied-from binding і перевірку drift. Empty draft fields лишають record incomplete; назва шаблону не дає acceptance.

| Предметний вхід | Що матеріально виробити | Boundary/context review |
|---|---|---|
| Camera/input | Real scene camera config, framing/viewport rules, UI controls/feedback | Follow/zoom/transition, narrow aspect, thumb occlusion, precision/peak, reduced motion |
| Systems/resources | Distinct readable state transitions and cues | Exhaust/recover/overlap/cancel; sensory fallback не губить інформацію |
| Actor/equipment | Silhouette, rig/clip/contact/collision representation, attachments, mode/status cues | Telegraph/commit/recovery, damaged/charged/overheated states, extreme poses, swaps |
| World | Kit/modules/connectors, interactive transformations, navigation/occlusion data, compositions | Route/readability/revisit, persistent change, rare legal composition |
| Progression/rewards | Actual unlock/equip/collection/reward screens, context cues, використання нового | Earned/unclaimed/duplicate/capped/pending; presentation після durable grant |
| Learning | Affordance/highlight/help/control variants без заміни правила | First attempt/failure/retry/independent use/re-entry, optional hints |
| Commerce/lifecycle | Store/offer/price/status/restore/refund/loading/error/offline flows | Decline/no-offer, interrupted purchase/reward, stale price, missing network |

Не додавати весь каталог станів кожному жанру: брати enabled features і actual model objects. `absent_by_design` має предметну причину й decision/source ref; unavailable tool не є такою причиною.

## Здійсненність і стиль

Production profile охоплює фактичні source operations, editable representation, exporter/importer, підтримані runtime effects, ліцензії, витрати, device budgets і перевірені обмеження. Візуальний target показувати в рамках цього маршруту. PNG не визначає backview, rig, topology, procedural behavior або audio; потрібні actual secondary samples/sources, коли вони входять у scope.

Style lock має точний original і конструктивне відображення camera/scale/form/surface/light/UI/motion/audio. Для camera вказати projection/follow/zoom/composition ranges та per-context cues з моделі; не використовувати один загальний ракурс лише заради картки. Показувати реалізовну temporal sequence, коли movement/interaction є суттю обіцянки.

## Representative proof до тиражування

Обрати невеликий набір, який покриває **спільні ризики**, а не лише красивий easy case: ключова механіка + changed world/resource state + representative actor/prop + actual camera/HUD + layered sensory feedback. Після actual source→export→import перевірити phone scale, normal/peak, boundary contact/transition і platform budget. Точний scope доказу записати; один actor не доводить усі rigs, а Android frame не доводить iOS haptics.

Зберегти capture build/state/seed/time/camera/resolution/quality, source/export hashes, observer/independence і deviations. Довідка про expected result не є observation. Actual assets evidence додавати до canonical evidence registry за форматом моделі; не заповнювати receipts вигаданими observers/builds.

## Зміни й повернення

Зміна camera/silhouette/material/motion semantics чи sensory hierarchy відкриває потрібні залежності design/build/learning/QA; не переробляти все без impact. Routine export/repair у прийнятих tolerances виконується автономно. Якщо репрезентативний proof не зберігає обіцянку, зупинити лише залежне тиражування та повернути конкретний route/target tradeoff з actual sample.

## П’ять operational records

Кожний item прив’язати до ToolCapabilityRecord, ProductionRecipe і SemanticTransformation; після фактичної спроби додати ProductionAttempt, після збирання — AssemblyEvidence. Використовувати чинні model/requirement/artifact/evidence IDs, не нову authority.

Recipe містить accepted inputs/hashes, exact supported command/API/GUI preset/argument mapping, DAG/preconditions/outputs/consumer, budgets/allowed effects, technical+semantic+perceptual checks, repair/stop. Transformation фіксує units/axes/pivot/scale/timebase/contact/color/alpha/audio conventions, preserved invariants і intentional losses. Attempt містить actual job/request/status/outputs/hashes/cost; timeout спочатку reconcile.

Перевірити, що кожний material parameter був реально прийнятий/спожитий tool і importer. Descriptor label/catalog row не закривають operation witness. Cache key включає input/model/recipe/exporter/importer semantics; змінені derivatives rebuild, immutable accepted original зберігається.
