# Visual, motion, audio, and haptic fidelity

## Establish the baseline

A generated concept image can define a target frame. Runtime acceptance needs the exact reference hash, scene and object IDs, layout, camera, lighting and material tokens, source to export to runtime lineage, animation and physics specifications, and approved sensory samples. Record unresolved target details without inventing expectations after seeing the result.

## Compare controlled captures

Use the same build, quality tier, aspect ratio, safe area, locale, scene, seed, state, camera and time. Capture runtime without debug overlays. Compare side by side, use alpha overlays or crops, and measure relevant color and layout properties. Keep raw images and capture procedure. Repeat in other states when their fidelity is in scope.

| Area | Check |
|---|---|
| Composition | Camera, FOV and perspective, silhouettes, layers, focal hierarchy, scale and spacing. |
| Character and world | Model family, proportions, anatomy, attachments, materials and palette. |
| Lighting and VFX | Direction, exposure, contact shadow, depth, bloom and particles, readable hazards. |
| UI | Exact fonts and licenses, tokens, layout, wrapping, icons, touch targets and localization. |
| Brand | Supplied studio mark, clear space and colors, credit and legal references, correct export. |
| Device tiers | Accepted fidelity range and deviations, preserved visibility of important telegraphs. |

Set tolerances before capture. Specify permitted scaling and anti-aliasing alongside prohibited silhouette, font, palette or layout changes. Require pixel equality for nondeterministic particles, anti-aliasing or renderers only under an appropriate controlled capture. Hash equality establishes asset identity. Use SSIM and perceptual scores to locate differences and inspect artistic fidelity in context.

## Observe motion and physics

Record representative and worst-case gameplay video with input and timing references. Inspect anticipation, action, contact and recovery, weight, root and collision alignment, foot and hand contact, rig extremes, props, interruption and blending, idle loop, death and retry, and camera damping and shake. Exercise low and high FPS, pause and resume, and multi-touch.

Verify true articulation when required, including motion of limbs beyond moving the full PNG. Check contact audio against impact and telegraphs against collision windows. Observe native frame pacing separately from an editor capture.

## Listen to runtime

Listen to the exact runtime mix on headphones and device speakers through quiet, intense and interrupted sections. Review motif, timbre, arrangement, intro, loop and outro, stem transitions at musical boundaries, clipping, clicks, fatigue, loudness balance, and masking of critical cues. Confirm full music phrases through actual listening.

For each UI or gameplay cue, check correct trigger and state, information, duplicate or late delivery, polyphony, priority, cooldown, spatial behavior, mute, volume, and accessibility. Use loudness, peaks and loop analysis alongside listening. If listening is unavailable, record `listening_not_performed` and provide a specific handoff for a person or capable tool.

## Test haptics

Observe physical devices with different hardware. Check semantic match, timing, comfort, intensity and cadence, fatigue during repetition, unsupported fallback, app controls, system-disabled and reduced modes. Record simulator and video evidence separately from actual sensation. Match each pattern to cue importance and maintain visual or audio feedback when haptics are off.

Use the [Android haptic principles](https://developer.android.com/develop/ui/views/haptics/haptics-principles) as an official reference. Verify current APIs and capabilities for selected platforms.

## Findings

For each deviation provide a screenshot, video or timecode, or audio cue, expected reference, severity and impact, and owner. Route it to repair against the baseline, acceptance within existing tolerances, or a material change request. Only the authorized decision can change accepted style. A QA statement such as «схвалює» cannot silently change the baseline.
