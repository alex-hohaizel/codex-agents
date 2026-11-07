# Візуал, рух, звук та вібрація

## Що є baseline

Одна generated concept image — ціль конкретного кадру, а не повна специфікація runtime. Для acceptance потрібні exact reference hash, scene/object IDs, layout/camera/light/material tokens, source→export→runtime lineage, animation/physics specs та actual approved sensory samples. За відсутності потрібної деталі позначити gap, не винаходити target під перевірюваний результат.

## Контрольний кадр

Встановити однакові build/quality tier/aspect ratio/safe area/localization, scene/seed/state, camera й capture time. Захопити runtime без debug overlays; comparison може містити side-by-side, alpha overlay, crops та measured color/layout differences. Зберегти raw images і capture procedure. Scene-perfect screenshot не гарантує gameplay fidelity інших станів.

| Категорія | Предметна перевірка |
|---|---|
| Composition | camera/FOV/perspective, silhouettes, layering, focal hierarchy, scale/spacing |
| Character/world | exact model family, body proportions, anatomy, attachments, materials, palette |
| Lighting/FX | direction, exposure, contact shadow, depth, bloom/particles, readable hazards |
| UI | exact fonts/licenses, tokens, layout, text wrapping, icons, touch areas, localization |
| Brand | supplied studio mark/clearspace/colors, credits/legal identity refs, correct export |
| Device tiers | agreed fidelity envelope and deviations; no important telegraph disappears |

Pixel equality не вимагати для недетермінованих particles/AA/renderers без спеціально контрольованого capture. Hash equality підтверджує asset bytes, не whole-frame appearance. SSIM/perceptual score лише допомагає знайти відхилення; він не сертифікує artistic identity. Tolerances мають бути погоджені до capture: allowed scaling/AA vs prohibited silhouette/font/palette/layout changes.

## Motion та physics

Записати representative і worst-case gameplay video з input/timing refs. Перевірити anticipation/action/contact/recovery, weight, root motion/hitbox alignment, foot/hand contacts, rig extremes, props, interruption/blending, idle loops, death/retry, camera damping/shake. Тестувати низький і високий FPS, pause/resume та multi-touch.

Штучний рух усього PNG вгору-вниз не приймається як character animation, якщо target потребує articulation. Audio contact не повинен розходитися з impact; телеграфи мають відповідати collision window. Відео з editor не доводить native frame pacing.

## Listening acceptance

Прослухати actual runtime mix на headphones і device speakers, із low/high intensity та interruptions. Music перевіряється як цілісна композиція, узгоджена з identity: motif/timbre/arrangement, intro/loop/outro, stem transitions на musical boundary, відсутність clipping/clicks/drone fatigue, balanced loudness і маскування важливого SFX. Короткий sine-wave/метадані WAV не є production music.

Кожен SFX/UI cue: correct trigger/state, clear information, no duplicate/late cues, polyphony/priority/cooldown, spatial behavior, mute/volume/accessibility. Loudness/peak/loop analysis допомагає engineering перевірці, але не замінює фактичне слухання. Якщо роль не може слухати — `listening_not_performed` і адресний handoff людині/доступному tool, без fabricated praise.

## Haptics

Перевірити на physical devices із різним hardware: semantic match, timing, комфорт, intensity/cadence, repeated-action fatigue, no-support fallback, app settings/system disabled/reduced modes. Simulator чи відео не передають відчуття. Вібрація не має дублювати кожен frame/event; важливість cue й підтримка feedback визначає pattern. Audio/visual feedback зберігається коли haptics вимкнені.

Офіційний орієнтир: [Android haptic principles](https://developer.android.com/develop/ui/views/haptics/haptics-principles). Поточні APIs/capabilities перевіряти під selected platforms.

## Результат

Кожне відхилення має screenshot/video/timecode/audio cue, expected reference, severity/impact і owner. Рішення: repair до baseline; accepted within existing tolerance; або material change request. QA не «схвалює» новий стиль мовчки.
