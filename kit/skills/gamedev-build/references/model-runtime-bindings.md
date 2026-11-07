# Canonical model → виконувана гра

Читати перед importer/data architecture і кожною зміною системи. Об’єкти, правила й залежності canonical game model визначено у [model format](model-format.md); цей документ описує runtime binding та фактичну перевірку. GDD, CSV, engine resources і UI labels — керовані проєкції одних правил.

## Binding і generation

Для кожного imported object/rule зафіксувати model ID/domain/revision/hash, canonical field path, runtime target path/type/unit, adapter/schema version, event consumers, fixtures/oracle/scenarios. Розділяти generated files і authoring sources; ручна зміна generated numeric data не є зміною дизайну. Одне поле може мати кілька consumers з явним mapping, але не кілька незалежних джерел істини.

Стартова форма — `assets/runtime-bindings.template.json`. Evidence додається тільки після actual observation. Зміни знаходити через model dependencies та runtime consumer map; `game_model.py impact MODEL --changed ID` допомагає знайти structural closure, але не виявляє всіх семантичних наслідків автоматично.

| Domain | Runtime binding | Змістовний oracle |
|---|---|---|
| Camera | Projection/FOV/zoom, tracking/dead zones/lookahead, transitions, aspect/visibility/collision rules | На gameplay speed видно потрібні action/threat/contact; wide overview не підміняє follow policy |
| Input | Intent/gesture thresholds, context/cancel/hold/release, UI ownership, simultaneous actions | Задумана комбінація зручно доступна; однаковий gesture не виконує непередбачувану дію |
| Systems/equipment | State/effect formulas, units/stack/cap order, interaction preconditions, cost/recovery | Предмет змінює конкретне рішення; межа/контра працює і після swap/restart |
| Actors | Perception/knowledge/memory, decision/action graph, cooldown/telegraphs, navigation/team roles | Ворог/агент реагує на actual доступне знання; різні ролі змінюють відповідь гравця |
| World | Authored topology/grammar, gates/routes, interactable state, event/pacing budgets, revisits | Reachable/fair composition, змістовний risk/reward, сталі наслідки, bounded fallback |
| Progression | Unlock/access graph, capability changes, resets/catch-up, long-arc milestones | Reachability from zero; нова можливість переосмислює знайомий контекст |
| Rewards | Trigger/authority/grant identity, table/pool/odds/guarantee/cap/duplicates, UI presentation | Durable grant exactly once; meaningful use; bad RNG/cap/failure recovery не губить ціль |
| Learning | Skill dependency/unlock, trigger/hint/mastery/skip/re-entry policy | Гравець самостійно використовує вивчене; hidden prerequisite не блокує прогрес |
| Art | Source/import settings/animation/events/audio buses/haptic adapter/quality | Exact baseline lineage й читабельність у normal/peak і unsupported-device fallback |
| Commerce | Eligibility/offer/store price/entitlement/transaction/reconciliation/ad cap | No-offer/free path, pending/cancel/refund/restore/restart; cumulative purchases перевірено |
| Lifecycle | Atomic save/migration/checkpoint/RNG/pending work, offline/auth/sync/telemetry | Kill/resume/corruption/version/cloud conflict не дублюють і не втрачають прогрес |

## Семантика подій та влада над станом

Визначити owner симуляційного стану й порядок одночасних подій. Gameplay rule створює semantic event; animation/audio/UI споживають його. Presentation completion не надає винагороду, damage або entitlement. Візуальний anticipatory feedback може з’явитися до confirmed durable result лише коли його значення відрізняється й rollback/reconcile зрозумілий.

Physics/render/input timestamps мають explicit clock/tick policy. Не прив’язувати game speed до FPS; не припускати cross-platform bit determinism від seed. Replay fixtures містять engine/content versions та tolerances. RNG streams для content/reward/cosmetic відокремити за design. Повторний callback, reconnect чи scene re-entry не повторює durable effect.

## Сценарії та приймання

Кожний scenario задає initial state, action і expected observable незалежно від коду, changed decision та counterfactual without-rule за форматом моделі. Додати actual input/seed/save/build/device/repro, observed evidence і verdict у виконувану test receipt. CSV `assets/system-scenarios.template.csv` є проєкцією scenario IDs, не другою версією expected behavior.

Використати змішані перевірки: deterministic numeric/property tests; state/event integration; authored/seed content validation; visual/motion/audio review; device touch/thermal/haptic checks; людський playtest для зрозумілості й задоволення. Автосимуляція balance/extreme policies є модельним результатом, не виміряним retention/revenue або доказом fun.

Перед масовим контентом native slice перевіряє найризиковіші спільні bindings. Beta охоплює весь finite approved scope, boundary/lifecycle і target devices. Release додає актуальні platform/store/privacy/commerce gates. Недоступний gate лишається blocked/unperformed; не підвищувати статус через існування receipt file.

## Негативні контролі

- Importer використовує старі числові значення при новому model hash — drift.
- Equipment description обіцяє інший playstyle, але consumer змінює лише damage multiplier — semantic mismatch.
- Дві AI family мають ті самі perception/decision/action і відрізняються HP — не доказ змістовного diversity.
- World generator проходить count check, але створює softlock або одну оптимальну відповідь усюди — content failure.
- Навчання вимагає locked ability або tutorial success фіксується натисканням «далі» — learning defect.
- Native build успішний, а camera/HUD/input не відтворює accepted experience — build proof не закриває якість.

## Semantic edges й виробничі записи

Runtime binding перевіряє не тільки ID/path, а unit/precision/capture/timebase/axis/color/audio/motion semantics. SemanticTransformation містить exact source/target convention, preserved properties, intentional loss й discriminating validator. Shared golden fixtures перевіряють reference/runtime parity; однакова formula prose не достатня.

Для production DAG вказати accepted inputs/interfaces/owner/resource locks, actual supported operation/recipe/outputs/consumer. Attempt/unknown job reconciliation, semantic cache freshness, post-import lint/source roundtrip і whole-scene AssemblyEvidence пов’язані зі current model. Нова operation або tool version не переносить старий witness автоматично.
