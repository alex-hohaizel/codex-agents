# Architecture and verified feasibility

## Engine and tool selection

Compare feasible options for the actual game across rendering, visual target, mobile physics and input, asset import, animation and audio and haptics, native plugins, commerce, ads and analytics, build and signing, skills, licenses, support and total cost. Evaluate Godot, Unity, or another engine where appropriate. Inspect current official docs, pin versions and plugins, and run a representative import and build probe. Verify store readiness in the correct native environment.

Prefer available lawful local or free tooling when it meets quality. Verify separate subscriptions, API access, Suno commercial rights, assets, Apple enrollment, and CI capacity. At operation level record installed, executable, authenticated, permitted and licensed, output, import, and cost. If unavailable, identify setup, alternative, and owner.

## TDD sections

1. Modules, scenes and services, dependency direction, state authority, public interfaces, and lifecycle ownership.
2. Input sampling, fixed-step simulation, rendering at variable frame rate, collision and event order, pause and time scale, and replay.
3. Camera, movement, VFX, audio, and UI with typed semantic event IDs and data bindings.
4. Save schemas, migration, atomic commit, checksum and backup, crash recovery, corrupt-save user experience, offline progress, and cloud conflicts and account merge.
5. Conditional backend for authentication and guest upgrade, inventory and commerce authority, leaderboards, abuse prevention, schedule, limits and retries and idempotency, and regional data policy.
6. Content delivery, catalogue and configuration versioning, compatibility, verification, rollback, and flags. Restrict content to supported data and declarative rules.
7. Analytics and observability with event schema, consent and minimization, cohorts, crash and frame and memory evidence, and support traces.
8. Security covering trust boundaries, separation of secrets, receipt verification, secure transport, tampering and replay safeguards, clock authority, and applicable privacy, deletion, and export.
9. Platform adapters for purchase and restore, permissions and notifications, audio focus and haptics, links, lifecycle, safe areas, graphics, and store SDKs.
10. Build and release covering dependencies, version locks, clean restore, debug/test/release, signing ownership, output inventory, and explicit platform verification.

## Numerical contracts

Use explicit meters or world units, seconds, radians or degrees, normalized input, and pixel or logical coordinates. Define fixed ticks, gravity, acceleration and deceleration, jump and apex and air control, friction and restitution, collision layers and geometry, mass and constraints, penetration, moving surfaces, and fast-object tunneling. Apply the canonical design values from actual runtime configuration.

Separate visible root motion and simulation authority. Define clips and blends and state priorities, root locks, applicable foot and hand IK, hit and footstep and event markers, cancel windows, ragdoll entry and exit, and recovery. For 2D and sprites, specify pivots, ordering, deformation, and clips appropriate to the medium.

## Budgets and actual devices

Select representative low, mid, and high tiers and quality profiles. Specify frame rate and frame-time budget, peak memory, draw calls and overdraw, textures, meshes, animation, VFX, audio voices, install and download size, cold load, scene transitions, network, and battery and thermal behavior. Record measured probe results or explicit assumptions. Test representative worst-case scenes and sustained play. Keep editor, emulator, and physical results separate.

Check actual Android output formats and API requirements, native libraries, and Play setup at release. Record iOS Simulator, signed device package, Mac and Xcode and signing and provisioning separately. Claim builds only for observed supported routes.

## Production and continuity

Specify each actual tool and SDK operation with input and output contract, schema and actual parameter consumption, versioned recipe, and consumer. Probe native thread and lifecycle behavior, cancellation, errors, profile, and release signing. Keep desired support separate from observed operation.

The State Catalogue records every mutable field's class (durable, reconstructible, ephemeral, cache, or secret), exact type and encoding, authority and scope, commit and consistency, restoration and migration and merge and deletion. Preserve 64-bit IDs and seeds exactly. Accept only supported data from untrusted inputs. Define cloud identity and sync, OS backup, and purchase restoration independently and test the actual host and SDK.

Design scoped development-only interfaces for the scenario lab, reason inspector, and repro capsule. Define methods and thresholds for first cold use, scene residency and overlap and unloading, atomic content epoch, matching symbols, and observed data egress.
