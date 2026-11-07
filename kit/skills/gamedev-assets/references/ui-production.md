# Повний UI-пакет

Start from design screen/state/transition inventory. Produce editable complete screens and component masters; tokens; licensed font binaries/glyph coverage; icon/illustration sources; atlases/slices/exported sizes; layout constraints; motion timelines and actual context previews. Wireframes, a generic component library or one pretty menu cannot close all screens.

## Screen-state production row

For each ID define target image, editable source, runtime scene/prefab/component, data bindings, states/variants, anchors/safe-area/insets, typography/icon tokens, focus/input/back behavior, animation, semantic audio/haptic cue IDs, platform/locale/accessibility variants, export hashes and acceptance evidence. Standard repeated component mappings are valid if all consumers and exceptions are listed.

Include boot/onboarding, hub/settings/account if present, collection/loadout/progression, store/pass/events if present, HUD/pause/results/reward/retry, offline/loading/empty/error/locked/pending/refund/reconnect and lifecycle. Device keyboard, long text/locale expansion, narrow/wide aspect, notch/system bars, scale and reduced-motion settings are real states. No dead CTA, invisible disabled reason or overlapping critical button.

## Навчання, винагороди та магазин у тому самому досвіді

Споживати model learning/reward/progression/commerce IDs. Кожна learning interaction має потрібні affordance/cue, safe practice, success/failure/help, optional skip/replay і повернення після перерви. Візуальна підказка не замінює спостережувану самостійну дію. Не показувати весь інструментарій на першому екрані лише тому, що він існує в грі; reveal follows accepted learning dependencies.

HUD пояснює ресурси й наступне рішення: наявність/витрату/відновлення, альтернативний стан і причину недоступності. Health, heat, stamina, noise чи інший показник використовувати за model fit, а не як однакову смужку в кожній грі. Якість — у читабельності й корисній інформації, не в числі gauges.

Reward flow відображає actual earned/granted/unclaimed/duplicate/capped status, приріст можливостей і перше використання. Shop показує exact contents/use/limits/price/currency/eligibility, trial/earned/decline path та pending/cancel/error/restore/refund states за обраною моделлю. Offer presentation не може підмінити або прискорити durable grant; purchase outcome походить від commerce authority. Перевірити перехід shop→equip/use у поточному save, коли це обіцяна цінність.

## Visual specifications

Use exact fonts/weights/size/line height/letter spacing, spacing grid, color/material roles, border/radius/shadow, icon optical alignment and minimum gameplay-size legibility. Do not swap fonts during export because a local machine lacks the original; include lawful fonts or explicit material replacement choice. Logos are exact studio assets, not newly approximated text.

UI touch targets, gesture ownership and thumb occlusion must match input design. Essential information cannot rely on color alone; signal status with shape/text/icon as appropriate. Preserve screen-reader/alternative labels when the runtime/platform supports them, and state tested limitations. Accessible variants stay stylistically integrated.

## Motion and feedback

Specify ease/duration/delay/overshoot, focus/press/release/disabled/selected transitions, interruption/reversal, queue/cancel behavior and reduced-motion alternative. Animation communicates state change; it does not become the transaction authority. Avoid high-frequency sound/haptics from repeated held input. Reward presentation follows actual grant, with reconcile-safe replay/skip.

## Acceptance

Review complete flows, not individual artboards only. Capture same state/data/resolution for target/actual comparisons; diff layout/font/color/icon critical regions and inspect on phone size. Run narrow/wide devices and long locale strings. Every runtime state must map to actual source/target or documented inherited component coverage. Missing final UI state means that scope remains partial.

## Committed action, localization і continuity

Input presentation відповідає actual recognizer: drag не малювати як дві самостійні кнопки; складна дія може мати contextual/gesture profile зі stable pointer ownership, preview/commit/cancel. Pointer loss/menu transition не спричиняє stuck control чи clickthrough purchase.

Виробити State Catalogue-related local-saved/cloud-pending/synced/conflict/error displays, reorientation/current goal, failure cause/recovery, exhaustion/partial-owned bundle states за fit. String IDs/context/plural/select/placeholders/terms/numbers/units/price/font glyphs/shaping/RTL задаються мовним scope; screen-state parity перевірити з actual strings.
