# Concept 4.0 → та сама виробнича гра

Читати [creative](domains/creative.md), [experience](domains/experience.md) та [Game Model workflow](game-model-workflow.md). Цей reference визначає subject-level fidelity. Камера, керування, графіка й стани пов'язані stable IDs з моделлю; template чи згенерований кадр не є фактичною native сценою.

## Незалежні рішення camera contract

| Рішення | Що зафіксувати | Чому це потрібно |
|---|---|---|
| Projection | Orthographic/perspective, side/top/isometric/інше, axis/world scale | Фіксована проєкція не означає нерухому камеру або одну арену |
| Tracking | Target, follow/dead zones, look-ahead, smoothing, bounds, respawn/recenter | Показати потрібну ділянку й час для відповіді під час руху |
| Framing | Hero/tool/target size, action focus, HUD/safe areas, offscreen cues | Масштаб вивести з точності контакту й швидкості, не з universal 12% |
| Zoom/режими | Коли й навіщо змінюється, limits, transition, target readability | Близька робота з інструментом і навігація можуть потребувати різного focus |
| Coverage | Authored geometry/layers/tiles, occlusion/cutaways, visible horizon | Не відкривати непобудовані боки/ділянки чи ховати критичну загрозу |
| Input/comfort | Thumb overlap, targeting, camera control load, reduced motion | Рух камери не повинен робити керування незручним або двозначним |

Дати candidate-specific normal/peak/critical-contact і transition scenarios. Для героя, що змінює масштаб/транспорт/стан, визначити відповідне правило framing. Static whole-scene view допустимий за fit, як і scrolling/follow/context zoom; жоден не є універсальним default. Не продавати cutscene/beauty angle як ordinary gameplay. Один viewport є фрагментом світу, не доказом його topology чи content capacity.

Авторські aids: [camera-framing](../assets/domain-templates/camera-framing.template.json), [visual-state-coverage](../assets/domain-templates/visual-state-coverage.template.csv). Для нового Model schema/field names користуватися [model format](model-format.md), не копіювати template як schema.

## Художня система до generation

Визначити fantasy/emotional promise і конкретні правила: shape/silhouette/proportions, line/edge, palette roles, material/texture, світло/контраст, навколишня архітектура, персонажі/вороги/props, typography/icons/HUD/menus, motion/contact, VFX, audio/music і haptics. Для кожної сім'ї показати що незмінне, що варіюється й що неприпустиме. Одна інша палітра не доводить іншого art direction; один технічний pipeline не примушує до однакового стилю.

Production profile містить actual/planned authoring/export/runtime tools, versions/evidence за наявності, license/cost/capacity, editable sources, sprite/model/rig/animation representation, camera/scene envelope, materials/light/VFX/UI, asset state families і blockers/due proofs. Допустимі 2D/2.5D/3D за реалістичного підтриманого маршруту; відсутність DCC тут не є глобальною забороною. Наявність PNG generator не доводить 3D model, rig, physics або production capacity.

Не обіцяти без route cloth/fluid/hand contacts, free camera rotation, PBR/GI чи нескінченні unique assets. Водночас не знижувати запропоновану якість автоматично до примітивної геометрії або flat redraw. Якщо ризик істотний, створити bounded source/assembly/animation proof або показати конкретний unresolved prerequisite до вибору; не пояснювати недосяжність уже після acceptance.

## Перевірка кожного кадру

1. Прив'язати source requirement/model IDs, camera/element/state refs, profile й точний поточний causal scenario до generation intent.
2. Генерувати ordinary gameplay viewport: реальні scale/density, функціональний HUD, visible core action і підтримуване source/animation representation. Форма touch-controls випливає з input grammar, а не з одного універсального UI preset.
3. **Фактично оглянути кожний кадр до показу користувачу.** Звірити projection/tracking implications, hero/tool/target scale, readable causal state, контакти, hazards, visual hierarchy, HUD/input correspondence, thumb occlusion та profile limits. Frame без огляду лишається uninspected.
4. Записати actual observer/image hash, scope, deviations, verdict й repair. Обмежену незалежну visual вибірку не називати перевіркою всього портфеля. Text/metadata/hash не замінює actual observation.
5. За відхиленням ремонтувати image, authored intent або route до показу; якщо змінюється material choice, надати конкретні зіставні samples. Повторний generated image не доводить source reconstruction.

Зберегти original bytes/hash/resolution/aspect/color, generation/source provenance/rights та відомі limitations. Для кожного visible element мати stable ID, bbox/layer/depth за потреби, роль/взаємодії, style/camera/light, source/assembly route, known/unknown/blocked і owner/closure. PNG не містить recoverable hidden geometry, backview, rig, exact font binaries, фізику чи audio stems.

## Reference lock і розширення обраного напряму

User acceptance стосується exact revision та scope: concept choice не є прийняттям кожного HUD елемента або production permission. Після прийняття lock містить originals/hash, прийняті camera/framing, character/world design, матеріали/light/UI, source lineage й допустимі відхилення. Не підміняти прийнятий master схожою картинкою. Незмінний asset використовувати byte-identical; derived export має явний recipe.

До масового виробництва розгорнути selected target pack:

- whole-frame target й annotated element map;
- tokens, silhouette/material/line/light/camera/UI/type rules, lawful font route або pending choice;
- first-play/normal/peak, різні релевантні місця, меню/shop/inventory й recovery states;
- locomotion/tool/enemy/interaction variants, contact phases, physics/collision constraints;
- audio event families, music states/transitions, haptic feedback та actual auditions у дозволеному scope;
- finite production inventory, source/export/import settings, budgets, rights, known gaps і next proof.

Нові rooms/assets розвивати з тих самих style/state laws і sources, не незалежними prompts. Audio/haptics proposals без actual audition/native evidence позначати unperformed. Source→import→native runtime representative slice має зберегти camera, core contacts, взаємодії й художню обіцянку; actual device перевіряє perf/thermal/memory/input/session. Ціль 60 FPS не є measured result.

Порівнювати target/actual за контрольованих aspect/camera/state/seed/time. Pixel-diff корисний для controlled capture, але не сертифікує художню тотожність чи feel. Source screenshot або native build самі не доводять ігрової якості; відповідна modality/player observation має власний gate.

## Управління drift

Зміна camera distance/tracking, rig, silhouette, animation contacts, material, shader, HUD/input чи audio cues відкриває impact на encounters, навчання, art/import/performance й QA. Перевіряти affected dependencies, а не повторювати всі unchanged jobs. Material downgrade → upstream repair/actual sample і рішення користувача перед тиражуванням. Не називати primitives «тим самим стилем», canned contact «тою самою фізикою» чи простий beep готовим sound design.

## Operation-level production promise

До показу зв’язати потрібну операцію з capability record і recipe: реальні input/output formats, schema/catalog/argument bindings, representation/rights/ціна/host, semantic invariants і due proof. Descriptor або catalog presence не дорівнюють перевіреній операції. Для руху/смерті/аварії/руйнування показати, які source/clip/collision/cue states ще потрібні; один кадр не закриває їх.

У кадрі звірити одночасно camera/input grammar, видимі предмети/навички, доступну прогресію, status/resources і outcome. Метрики з model-only прикладу не оформлювати як measured native result. Якщо потрібний матеріальний параметр ігнорується generator, виправити route до обіцянки exact результату.
