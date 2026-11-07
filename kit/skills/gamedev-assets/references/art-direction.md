# Одна ідентичність у кожному матеріалі

Взяти camera/art/input IDs, feature applicability і scenarios з чинної моделі гри; construction spec є виробничою проєкцією із source model hash, не альтернативним дизайном. Для нової гри спершу визначити власну form/surface/light/type/motion/audio основу, а не автоматично переносити минулий render preset. Різноманітність концепцій оцінюється до production; після прийняття конкретної гри підтримувати цілісність її напряму.

## Canonical references

Зберігати immutable exact approved image, intended scene/state/device/aspect, version/hash і джерело user choice. Розкласти його на construction data: world units, camera/projection/FOV, composition, scale, silhouette/proportion landmarks, shape language, palette/color space, value hierarchy, materials/shader behavior, light direction/temperature/exposure, postprocessing, edge/detail density, UI/font/icon tokens, motion/audio palette. Усього цього не можна однозначно витягти з картинки; unresolved задати як питання/actual sample до production.

Creative reference не перегенеровувати під виглядом «того самого». Якщо original має artifact/impossible geometry, зберегти оригінал і запропонувати правку з actual sample. Новий runtime baseline має явний mapping до reference й agreed deviations; не стерти первинний target новим generated frame.

## Style bible must be constructive

| Розділ | Що повинно бути відтворюваним |
|---|---|
| Form | Proportion landmarks, silhouette rules, bevel/roundness, sharpness, line/edge treatment, forbidden motifs |
| Color | Named palette values in declared color space, allowed roles/contrast, material response, grading/LUT if used |
| Surface | Texture density, brush/pattern family, wear/noise scale, metallic/roughness/normal conventions or 2D equivalents |
| Light/camera | Scene rig/settings, projection, framing, focal hierarchy, character screen size, quality profiles |
| Type/icons | Included licensed font binaries, weights/sizes/spacing, glyph coverage, icon grid/stroke/corner/optical rules |
| Movement | Weight, anticipation/action/recovery, timing vocabulary, squash/stretch bounds, root/camera behavior |
| VFX | Shape/color/timing hierarchy, telegraph/impact/afterglow, screen-space/overdraw limits |
| Audio/haptics | Timbre/instrument/motif/dynamic vocabulary, cue hierarchy and sensory synchronization |
| Studio | Exact approved logo/wordmark variants, placement/clear space/contrast and credits/legal use |

A moodboard is input, not this specification. Do not copy a competitor's identifiable character, logo, UI composition or extracted asset. Compare workmanship/readability with current released relevant gameplay only after actual access; page metadata does not prove video review.

## Camera та масштаб як поведінка

Розрізняти overview і реальну gameplay camera. За model camera states зафіксувати projection, FOV/orthographic size, target/follow axes, lookahead, dead zones, damping/limits, occlusion/collision, zoom/state transitions, shake/reduced motion та engine bindings. Не задавати всю гру одним кадром; stationary, follow, rail, over-shoulder, top-down чи інша політика має випливати з дії й доступної інформації.

Для normal/precision/peak contexts визначити керований об’єкт, його screen-size envelope, focal hierarchy, потрібну дистанцію реакції, видимість contact/landing/target і offscreen cues. Частку екрана обґрунтувати жанром; універсального мінімального відсотка для всіх ігор немає. Перевірити в русі та на narrow/wide aspects, safe areas, thumb occlusion, low-contrast/overlapping effects. Структура camera у style-lock template вимагає цих рішень, але заповнення форми не доводить їхню якість.

## Whole-frame validation

Create normal, peak, low-contrast/background, motion and narrow-device contexts. Every material is judged at gameplay size and in scene, not only isolated render. Texture detail that sparkles at phone scale is a defect. Strong standalone hero art with unfinished arena/HUD is not a completed frame.

Use deterministic capture conditions for comparison: seed, scene, camera, pose/time, resolution, quality, UI/data. Static UI/icon export can use pixel diff within agreed tolerance; animated 3D uses geometric/color/composition landmarks plus perceptual/motion review. Tolerance must be accepted before assessment, not widened to pass poor output.

Allowed technical derivatives (compression, mipmaps, LOD, safe-area adaptation) preserve identity and pass QA. New silhouette, font, palette family, camera or music motif needs sampled change request when material. Routine repairs to approved baseline do not need repeated permission.
