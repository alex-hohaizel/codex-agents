# Архітектура runtime

Прочитати [model-runtime-bindings](model-runtime-bindings.md) і чинну модель до вибору schemas/adapters. Stable model IDs пов’язують camera/input/systems/actors/world/progression/rewards/learning/art/commerce/lifecycle/equipment з runtime. Schema validity не доводить, що engine consumers виконують ті самі правила; потрібні scenario oracles та actual observations.

## Рушій обирають доказами

Зберігати затверджений engine/render path. Якщо він не визначений, порівняти Godot, Unity чи інший відповідний рушій на representative native scene, renderer/physics/audio needs, exporter maintenance, device support, license/fees та доступності developer workflow. Godot — кандидат з відкритим кодом, не універсальний автоматичний вибір. Для дорогого або принципово іншого шляху потрібен user choice до залежної роботи. Не приписувати Codex доступ до Blender/Unity/Xcode лише тому, що є навичка про них.

Pin engine version/build SHA, export template version/hash, plugins/native libs, language toolchain, renderer, color space, physics timestep, import defaults, SDK selection та lockfiles. Вести reversible installation log. Read-only inventory/ordinary authorized installs продовжувати без зайвих підтверджень; фінансові/публічні/account identity зміни потребують чинного scope.

## Канонічне ядро та платформи

| Canonical shared | Android/iOS adapter |
|---|---|
| Rules, content IDs, economy, save schema, progression, entitlement meaning | Store transport, signing, notifications, secure storage |
| Input intent, simulation timing policy, seed stream | Touch events, safe area, hardware capability |
| Audio event IDs, bus priorities, haptic intent | Audio focus/interruption, native haptic renderer |
| Network contracts, retries, conflict policy | Connectivity, background lifecycle, platform auth |

Не дублювати «майже ту саму» економіку у двох platform clients. Renderer/OS adapters можуть відрізнятися за implementation, але не порушують agreed visual hierarchy, timings, rewards або access rules. Відмінності мають explicit permitted-deviation record та targeted parity tests.

## Input, physics та animation

- Input: capture timestamp/device orientation, normalized intent, gesture thresholds, cancellation, multi-touch policy, UI capture, pause/resume, low-FPS behavior. Не прив'язувати gameplay speed до render FPS.
- Simulation: fixed/variable step policy, substeps, collision masks/layers, units, mass/friction/restitution, gravity, restitution caps, coyote time/input buffer/aim assist лише за design. Явно визначити out-of-bounds, tunneling, stuck resolution, simultaneous events та numeric tolerance.
- RNG: content seed, reward seed, cosmetic seed окремими streams; versioned generator; input replay. Однаковий seed не гарантує bit-identical cross-platform physics без спеціальної детерміністичної реалізації.
- Character: rig hierarchy, hitbox vs hurtbox vs visual mesh, root motion authority, blend/state graph, interruption/priority, IK contacts, attachment sockets, foot/hand contact, ragdoll boundary.
- Camera: projection, FOV, target offset, damping, collision, screen shake limits, death/restart transition, safe composition on aspect ratios. Reduced motion має device-test.
- Scene assembly: import units, pivot/origin, scale, layer/depth, materials/shaders, lighting/exposure, shadows, texture filtering/mipmaps, batching, quality tiers. При зміні tier не губити gameplay telegraphs.

## Camera/input та видимість рішення

Відтворити model camera states, tracking/lookahead/dead zones, composition/screen-size envelopes, transitions, offscreen threat rules і per-aspect policies. Налаштування одного screenshot не замінюють temporal controller. Перевіряти camera collision/occlusion, різкі зміни цілі, precise action/peak events, phone-scale silhouette/contact та доступну дистанцію реакції. Не зменшувати героя для демонстрації всього світу, якщо це не approved gameplay need.

Input adapter перетворює native events у domain intents без дублювання правил. Задати who owns gesture, press/hold/drag/release/cancel, contextual guards, simultaneous two-thumb actions, hardware/accessibility alternatives, feedback visible outside finger і interruption/low-FPS behavior. Незручна трипальцева комбінація не стає готовою через існування трьох handlers. Вимірювати actual latency за named method/device; simulation timestamps не є відчуттям гри.

## Audio та haptics

Runtime споживає accepted event palette. Кожен cue має trigger, bus, gain/pitch range, max polyphony, priority, cooldown, spatial mode, transition/ducking та interruption policy. Music stems синхронізуються до musical boundary; loop seam/intro/outro працюють у грі, а не лише у DAW preview. Не зашумлювати feedback дрібними дубльованими triggers.

Haptic intent може мати intensity/sharpness/duration/profile, але реалізація враховує hardware/API capability та settings. No-support fallback зберігає visual/audio feedback. Перевірити фактичний дотик на пристрої, music ducking під interruption, silent/background, headphones та accessibility.

## Lifecycle й asynchronous work

Є owner/cancel policy для scene tasks, requests, animations і callbacks. Після unload не застосовувати response до знищеного scene/state. Pause заморожує simulation за design, а durable transactions проходять reconciliation. Kill/restart відновлює checkpoint і pending purchases/rewards без double credit. Background timing не створює negative progress або reward exploits.

## Backend та безпека

За offline single-player не створювати backend без користі. Якщо потрібен — зафіксувати authoritative systems, auth/session expiry, least privilege, server-side validation, replay/idempotency, rate limits, retries/deadlines, version compatibility, observability та deletion. Client не містить store verification secret/signing key. Local obfuscation не є довірою до monetary state; tampering risk фіксується під обраний business model.

## Runtime authority й системні probes

Collision matrix розділяє blocking, hit/hurt, interaction, perception, pickups/debris; solver event provenance і missing-value semantics перевіряються під pinned backendversion. Relative contact velocity включає rotation; impulse/energy перетворюються на HP лише defined damagepolicy. Не дублювати physics response додатковим impulse. Topology revision інвалідує nav/cover/visibility/plans, controller/ragdoll/respawn має єдиного transform owner.

Забезпечити bounded scenario lab, reason inspector і sanitized repro capsule як різні dev tools. Qualitycontroller за обраної адаптації має thresholds/hysteresis/cooldown і preserve criticalrules/cues. Cold first-use, resource residency/lifetime/unload, transition overlap і actual SDK egress мають instrumented tests. Exact releasedsymbols й content epoch лишаютьсяпов’язаними з artifact.
