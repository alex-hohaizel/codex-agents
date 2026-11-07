# Цілісний аудіодизайн і приємна тактильність

## Аудіоідентичність до генерації

Define sonic fantasy, instruments/timbres, harmonic/rhythmic language, motifs, energy curve, space/reverb, dynamic range, UI vs world hierarchy and relationship to material/character/color/movement style. Build an audition board with actual audible candidates and contextual mixes. Random licensed tracks or individually generated clips do not constitute a cohesive score.

One scene sequence must demonstrate boot→menu→navigation→enter run→normal action→peak→pause/resume→win/fail→reward→return. Auditions include full phrases, valid loops and transitions; a cropped few-second WAV/tone/oscillator/MIDI metadata is not finished modern music. Procedural/synth/MIDI production can be excellent if actual arrangement/timbres/mix and listening meet the agreed artistic target; the method alone neither passes nor fails quality.

## Music production

For each music state provide actual track or stem assembly, editable project/recipe where available lawfully, available stems/layers, BPM/meter/key when relevant, intro/loop/outro markers, bar/sample alignment, transition rules, stingers, intensity layers, crossfade/ducking and silence/ambient strategy. Seamless loop must be auditioned over multiple repetitions; no click, tail truncation, mismatched phrase or abrupt energy reset. Dynamic transition aligns to musical boundaries where intended and handles immediate gameplay interruption.

Licensed finished tracks may not include DAW/stems. Do not invent them; include lawful source/audio, license/receipt, actual editable integration/mix assembly and required derivative permissions. If the game requires adaptive stems, a stereo-only license that prohibits editing is insufficient. A generated file's existence does not establish commercial rights; verify plan/date/terms for that exact production route.

## SFX/voice inventory

Every semantic action/event needs an explicit cue or intentional silence: UI navigate/confirm/cancel/error; movement/contact/footstep/surface; attack/projectile/impact/damage/near-miss; abilities/status; pickups/progression/currency/reward; environment/ambience; win/fail/transition; system/commerce errors. Define family/variants, material/character mappings, deterministic or seeded selection, pitch/volume variation bounds, cooldown, voice limits, spatialization/distance, priority, ducking, tail handling and accessibility alternative.

Variations must not sound like random unrelated libraries. Compare consistent transients/timbres/space across all cues. Check repetitive fatigue, harsh high frequency, low-end masking, menu annoyance and reward loudness. Voice is optional and requires agreed language/character/rights; do not substitute a mismatched generic TTS voice.

## Runtime event map

Use semantic event IDs linked to gameplay/UX, not direct file playback scattered across code. For each: event schema, source authority, cue/music/haptic mapping, timing, concurrency group, priority, cooldown, surface/character/state modifiers, stop/restart/resume semantics and quality settings. Event dedupe/replay rules prevent duplicate rewards/voices after reconnect or lifecycle resume. Audio completion callback never grants gameplay currency.

Supply mixer buses (master/music/SFX/UI/voice/ambience as relevant), gain staging, limiter/ducking/compression where appropriate, sample rate/bit depth/channel conventions, runtime encoding/stream vs preload, memory/CPU/voice budget and device-speaker/headphone checks. Peak/loudness targets are context-specific and documented; do not impose one arbitrary LUFS as proof of quality. Preserve enough headroom in dense combat; no clipping or drowned critical cue.

## Haptics as orchestration

Map only meaningful contacts/confirmations/intensity changes; declare intentional silence for frequent low-value events. Each pattern: semantic ID, platform mapping, intensity/sharpness/duration/transients, priority, minimum spacing, cooldown, aggregation/drop rules, cancellation, system support/fallback, user off/intensity controls and reduced-sensory option. Sync with actual contact/audio/VFX event; avoid constant buzz, UI barrage or every-frame vibration.

Apple Core Haptics/Android haptic APIs and engine plugins require actual availability verification and physical-device testing. Emulator/simulator cannot prove pleasant tactile feel. On unsupported hardware degrade gracefully; haptic absence cannot hide essential information. Respect system settings and lifecycle cancellation. Do not issue haptics while backgrounded or ignore opt-out.

## Listening and sensory QA

Technical format/FFT/loudness checks are useful but are not listening. A reviewer must actually hear exact files/context and report timecoded observations and limitations. If agent cannot access audio playback, provide auditions and human review procedure with status unperformed; never claim «прослухано» from code. Check at low volume, device speaker, headphones, dense gameplay and long repeated use; physical haptics require independent device observations. Record exact audio hashes, mixer/config, build/device and capture context.

## Causal event і production consumption

Для confirmed simulation contact передати event/root/parent identity, material/part, bounded force feature/outcome/position; один manifold або кілька hurtboxes не дублюють cue без правила. Continuous scrape має start/update/end/cleanup, bounded voices і fatigue policy. Cosmetic audio RNG ізольований від combat/loot/generation.

Ordinary hit cue не чекає disk/cloud; critical purchase/reward success cue відповідає verification/durable boundary. У combined attention scene danger/resource/objective/reward мають priorities/mix/defer/aggregate і no-sound/no-haptic equivalents. Окремий повний track не доводить stems/MIDI: перевірити actual extraction/export operation, rights/format/quality. Деякі providers підтримують такі окремі операції; не заперечувати їх універсально.

Semantic audio transfer задає actual sample rate/channels/format, loop/sample boundaries/tails, musical bar/timebase, normalization/mix/streaming choice і named runtime consumer. Перевірити full-phrase transition та lifecycle interruption у конкретній pinned engine version, не лише DAW.
