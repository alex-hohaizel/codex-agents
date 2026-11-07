# Художня ідентичність, елементи й здійсненне виробництво

## Застосування, вхід і власний результат

Застосовувати від першого показуваного кандидата до store presentation і liveops. Прийняти fantasy/emotion, mechanics/camera/input, studio/IP envelope, exact accepted masters, бюджет і operation-level tool capabilities. Власні артефакти — distinct art direction, visual/audio production profile, per-element specification й state inventory, source/export/import lineage та scoped parity evidence. Використати [шаблон](../../assets/domain-templates/creative-element-spec.template.json); canonical art domain є короткою проєкцією, а не заміною виробничих матеріалів.

## Відмінний художній задум

Визначити shape language, пропорції/силуети, масштаб, materials/texture, palette/value hierarchy, lighting/shadows, composition, depth/layers, camera, typography/icons, HUD/menus, motion/contact, VFX, sound palette/music, haptic character і store expression. Кожне рішення пояснює fantasy, tempo й читабельність саме цієї гри. Різні палітри того самого render preset не дорівнюють різним напрямам. Ідентичність студії не змушує всі її продукти мати одну камеру, тіло героя або матеріальність.

Розглядати за fit 2D/sprites, painted layers, vector/cutout, 2.5D, low/high-detail stylization, 3D та інші lawful routes у межах реальної місткості. Не робити технічне спрощення прихованою причиною однакового стилю всього портфеля. Вплив описувати через принципи й власну відмінність, не копіювати чужий IP/asset.

## Кожний елемент і його стани

Інвентар формувати з фактичного scope, не зі слів «інші об'єкти». Для кожного significant element/family задати ID, mechanical/communication role, view/scale, dimensions/proportions/pivot, shape/material/palette/light, visible states, motion/contact, cues, UI/audio/haptic events, variants, consumers і acceptance. Об'єднувати повторювані елементи спільними tokens/recipes із явними exceptions; не дублювати одну істину в десятках таблиць.

Персонаж/агент потребує застосовних views/poses, silhouettes, movement/action/hurt/recovery/death або інших станів, gear attachments і читабельних telegraphs. Предмет/техніка — functional state, equip/use/cooldown/damage/recovery та зміни від розвитку. Світ — material/state transitions, interactive affordances, routes/hazards, depth/occlusion. UI — normal/selected/locked/disabled/empty/loading/error/pending, long locale/font scale, input/focus і safe areas. Кожний названий стан пов'язати з реальним правилом; зайві заготовки не виготовляти.

Motion задає poses/curves, anticipation/contact/recovery, root/pivot locks, per-limb limits/rig/weights/IK за потребою, blend/cancel windows і simulation authority. Не домислювати rig/backview/collision із одного PNG. Контакт має узгоджувати ноги/руки/інструмент/поверхню; загальний зсув картинки по Y не видавати за анімацію тіла. VFX не приховує ціль або telegraph під піковим overlap.

Для audio визначити motifs/timbres/tempo/texture, event map, real SFX/music/ambience/UI needs, stems/loops/transitions, mix/ducking/voice priorities, interruption і runtime routing. Нотний опис, waveform або примітивний tone не є готовою музикою. Для haptics — event, pattern/intensity/duration/cooldown, supported native route/fallback і actual device feel; не заявляти перевірку вібрації з відео.

## Здійсненний референс до показу

Production profile містить фактичні tools/versions й статуси installed/executable/authenticated/permitted/license/cost, доступні editable sources, sprite/model/rig/animation route, export/import settings, materials/light/VFX/UI/audio capabilities, видимий scene budget, target devices і unresolved risks. Відрізняти currently verified route, planned setup і недоступну можливість. Підписка на генератор не доводить права/доступ до API чи іншого сервісу.

Генерувати target, який цей маршрут може правдоподібно зберегти; не обіцяти реалізувати будь-який концепт-арт. Prompt прив'язати до gameplay camera, масштабу героя, density, можливого animation representation, HUD/input й обмежень. Якщо невідомі expensive cloth/fluid/geometry/animation необхідні для обіцянки, перевірити route або змінити proposal до показу. Не пропонувати після вибору «потім зробимо значно простіше» як стандартний план.

Кожний згенерований кадр фактично оглянути й звірити з паспортом/профілем: camera/framing, видимі mechanic states, art language, body/contact, density, controls/HUD і production plausibility. Записати observer/hash/deviations. Вибірковий незалежний review чесно називає свій scope; він не означає огляд решти картинок. Preview є visual proposal, не runtime capture/device proof.

## Lock, lineage і parity

Після user acceptance зберегти exact originals/hash/provenance й точний scope: що прийнято, що можна варіювати, які деталі ще невідомі. Не перевидавати перерисовку як byte-identical master. Для незміненого canonical asset зберігати exact bytes; для derived output — рецепт/source/import lineage. Кожний element/state посилається на правило, accepted reference, authoring object, export, runtime consumer й evidence.

До mass production відтворити representative normal/peak scene в реальному native runtime з production sources, відповідними camera/aspect/state/seed/time, input/physics/HUD/animation/audio/haptics і застосовними menus/commerce cues. Порівняти side-by-side/crops/overlay; static UI може мати documented pixel checks, рух/контакт/музика потребують time-based observation. Один metric не доводить художню тотожність. Допустимі quality-tier/LOD/compression/safe-area derivatives залишаються в прийнятому envelope; матеріальне зниження fidelity відкриває відповідне user decision.

## Зв'язки, due proof і ролі

Art/creative lead виробляє direction; technical artist перевіряє source/import/performance; animation/audio/UX specialists створюють фактичні матеріали; runtime engineer інтегрує; independent reviewer оцінює parity. Creative ownership не замінює права/ліцензії. Зміна camera, shader, rig, font, audio palette або interaction timing відкриває залежні source/runtime/UX checks, а не весь проект автоматично.

Concepts потребує distinct causal direction, plausible production profile й actual image inspection. Preproduction — per-element/state specs, quantities, budgets і slice contract. Slice — observed runtime/native/device proof відповідних модальностей до тиражування. Beta — людська читабельність/feel й відмінність задуму. Release — assets/licenses/actual build/store parity. Liveops — відсутність identity drift і повторна перевірка нових станів. Контрприклади: усі стилі відрізняються лише кольором; source невідомий; герой мізерний заради плакатної композиції; PNG названо rig; музика лише описана; device fidelity заявлена за editor frame.

## Джерела й статус рекомендацій

- [Nintendo: Wonder, chapter 1](https://www.nintendo.com/en-za/News/2023/October/Ask-the-Developer-Vol-11-Super-Mario-Bros-Wonder-Chapter-1-2460393.html) — практика спільного gameplay/art/audio задуму й прототипування.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) — приклад узгодження можливостей, світу й виробничої місткості.
- Exact lineage, feasibility/inspection/parity gates — правила Game Atelier. Конкретні exporter/engine/device вимоги перевіряти за чинною офіційною документацією обраного маршруту, без універсального preset.
