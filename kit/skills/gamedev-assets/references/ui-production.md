# Complete game UI production package

Start from design screen/state/transition inventory. Produce editable complete screens and component masters; tokens; licensed font binaries/glyph coverage; icon/illustration sources; atlases/slices/exported sizes; layout constraints; motion timelines and actual context previews. Wireframes, a generic component library or one pretty menu cannot close all screens.

## Screen-state production row

For each ID define target image, editable source, runtime scene/prefab/component, data bindings, states/variants, anchors/safe-area/insets, typography/icon tokens, focus/input/back behavior, animation, semantic audio/haptic cue IDs, platform/locale/accessibility variants, export hashes and acceptance evidence. Standard repeated component mappings are valid if all consumers and exceptions are listed.

Include boot/onboarding, hub/settings/account if present, collection/loadout/progression, store/pass/events if present, HUD/pause/results/reward/retry, offline/loading/empty/error/locked/pending/refund/reconnect and lifecycle. Device keyboard, long text/locale expansion, narrow/wide aspect, notch/system bars, scale and reduced-motion settings are real states. No dead CTA, invisible disabled reason or overlapping critical button.

## Learning, rewards, and commerce in the player journey

Consume learning, reward, progression and commerce IDs from the model. Each teaching interaction includes the required affordance or cue, safe practice, success, failure and help, optional skip and replay, and return after interruption. Observe independent action separately from following a visible cue. Reveal controls according to accepted learning dependencies.

Use the HUD to explain resources and the next decision, including availability, spending, recovery, alternatives, and why an action is unavailable. Choose displays for health, heat, stamina, noise, and other metrics according to the model. Judge their readability and usefulness.

Show actual earned, granted, unclaimed, duplicate and capped status, capability gains, and first use. The store shows exact contents, use, limits, price, currency and eligibility, trial, earned and decline routes, and pending, cancel, error, restore and refund states as applicable. Bind completed purchases to commerce authority and durable grants. Test store to equip or use on the current save when that is part of the promise.

## Visual specifications

Use exact fonts/weights/size/line height/letter spacing, spacing grid, color/material roles, border/radius/shadow, icon optical alignment and minimum gameplay-size legibility. Do not swap fonts during export because a local machine lacks the original; include lawful fonts or explicit material replacement choice. Logos are exact studio assets, not newly approximated text.

UI touch targets, gesture ownership and thumb occlusion must match input design. Essential information cannot rely on color alone; signal status with shape/text/icon as appropriate. Preserve screen-reader/alternative labels when the runtime/platform supports them, and state tested limitations. Accessible variants stay stylistically integrated.

## Motion and feedback

Specify ease/duration/delay/overshoot, focus/press/release/disabled/selected transitions, interruption/reversal, queue/cancel behavior and reduced-motion alternative. Animation communicates state change; it does not become the transaction authority. Avoid high-frequency sound/haptics from repeated held input. Reward presentation follows actual grant, with reconcile-safe replay/skip.

## Acceptance

Review complete flows, not individual artboards only. Capture same state/data/resolution for target/actual comparisons; diff layout/font/color/icon critical regions and inspect on phone size. Run narrow/wide devices and long locale strings. Every runtime state must map to actual source/target or documented inherited component coverage. Missing final UI state means that scope remains partial.

## Committed actions, localization, and continuity

Match input presentation to the actual recognizer. Show a drag as one gesture. Complex actions may use contextual input or gestures with stable pointer ownership, preview, commit and cancel. Handle lost pointers and menu transitions without stuck controls or click-through purchases.

Derive locally saved, cloud pending, synced, conflict and error displays from the State Catalogue. Cover reorientation and current goal, failure and recovery, exhaustion and partly owned bundle states where relevant. Define string IDs, context, plural and select rules, placeholders, terminology, numbers, units, prices, glyphs, shaping and RTL from language scope. Verify state parity with actual strings.
