# Архітектура й перевірена здійсненність

## Engine/tool selection

Compare only feasible options against the actual game: 2D/3D rendering, visual target, mobile physics/input, asset import, animation/audio/haptics, native plugins, IAP/ads/analytics integration, build/signing, team skill, licenses, long-term support and total cost. Godot/Unity/another engine is a candidate, not a universal answer. Verify current official docs and pin exact version/plugins; execute representative import/build PoC before committing. A tutorial or desktop preview does not prove native store readiness.

Default to existing lawful free/local tooling when it can meet the quality floor. Subscription access does not include arbitrary APIs, Suno commercial rights, asset packs, Apple enrollment or CI minutes. Record operation-level capability: installed, executable, authenticated, permitted/license, sample output, import result, cost. If missing, provide exact setup/alternative/owner instead of inventing a tool.

## TDD sections

1. Modules/scenes/services and dependency direction, domain state authority, public interfaces and lifecycle ownership.
2. Input sampling, deterministic/fixed-step simulation, variable frame rendering, collision/event ordering, pause/time scale and replay.
3. Camera/motion/VFX/audio/UI integration with typed semantic event IDs and data bindings.
4. Save data schemas, version migrations, atomic commit/checksum/backup, crash recovery, corrupt-save UX, offline progress, cloud conflict/account merge.
5. Backend only when needed: auth/guest upgrade, inventory/commerce authority, leaderboards, anti-abuse, event schedule, rate/retry/idempotency and region/data policy.
6. Content update/delivery, catalogs/config versioning, compatibility, rollback, feature flags, validation; no remote executable policy bypass.
7. Analytics/observability with event schemas, consent/minimization, cohort definitions, crash/frame/memory measurements and support traces.
8. Security: trust boundaries, secrets outside repo, receipt verification, secure transport, tampering/replay, clock authority, privacy/delete/export if applicable.
9. Platform adapters: purchases/restore, permissions/notifications, haptics/audio focus, links, device lifecycle, safe areas, graphics capabilities and store SDKs.
10. Builds: pinned dependencies/tool versions, clean restore, debug/test/release variants, signing ownership, artifact inventory and per-platform verification.

## Numeric contracts

Physics/input specs use meters/world units, seconds, radians/degrees, normalized inputs and pixel/logical coordinates explicitly. Define fixed tick, gravity, acceleration/deceleration, jump/apex/air control, friction/restitution, collision layers/shapes, mass/constraints, penetration resolution, moving-platform transfer and high-speed tunneling strategy. Design values must enter actual runtime config; no manual second copy.

Animation distinguishes visual root motion and simulation authority. Specify clips/blend tree/state priorities, root locks, foot/hand IK if needed, hit/footstep/event tracks, cancel windows, ragdoll enter/exit and recovery. Sprite-based/2D rigs use equivalent pivot/order/deformation/clip contracts; don't force unnecessary 3D.

## Budgets and real devices

Choose representative low/mid/high target devices and quality tiers. Define target FPS with frame-time budget, peak memory, draw calls/overdraw, textures/mesh/animation/VFX/audio voices, install/download size, first load, scene transition, network, battery/thermal. Numbers require measured PoC or explicit provisional assumption. Validate worst-case encounter/HUD/effects and after extended play. Editor FPS and emulator are limited evidence, not physical-device performance.

Android output types, target APIs, native library constraints and Play setup must be checked at release. iOS Simulator app is not signed physical-device IPA; Xcode/macOS/signing/provisioning are separate capabilities. Do not promise both native binaries in an environment that cannot produce them.

## Production та continuity interfaces

Кожну потрібну tool/SDK операцію специфікувати через operation contract, actual schemas/argument consumption, versioned recipe і consumer; tool name не є capability. Для native adapters ранній conformance probe охоплює threading/lifecycle/cancel/error/profile/release-signing; desired support та observed witness окремі.

State Catalogue охоплює всі mutable fields та class durable/reconstructible/ephemeral/cache/secret. Задати exact type/encoding/authority/scope/commit/consistency/restore/migration/merge/delete. 64-bit IDs/RNG не втрачати через float JSON; untrusted objects не завантажувати автоматично. Cloud identity/sync, OS backup й purchase restore — різні контракти з actual host/SDK test.

Scenario lab, reason inspector і repro capsule мають bounded dev-only interfaces. Cold first-use, transition residency/overlap/unload, atomic content epoch, matching crash symbols і data egress observation отримують methods/targets; не залишати це загальним словом performance.
