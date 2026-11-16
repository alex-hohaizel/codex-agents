# Production from requirement to delivered result

Contract version 4.0.0. This reference covers scope and entry, records, admission, recipes, transformations, repair and cache, evidence, handoffs and sources. Use it for feasibility, production or import of assets, code, builds, QA, release, live operations and agent changes. The operation catalog is `assets/v4-production/operation-catalog.json`. The same directory contains templates for five records and nine recipe families. Verify actual SDKs and received assets separately.

## 1. Close the agreed scope

Choose operations with known outputs and consumers. Inventory required artifact, action, state, variant, locale and platform classes for the agreed scope. Map `requirement_id → obligation_id → recipe_id → output_id → consumer`. Record each excluded class as `absent_by_design` with its reason. Missing tools or hosts make applicable work blocked. O01–O45 provide a starting taxonomy and the game can require additional operations.

At C0 identify risk and a feasible route for the key distinction. For every complete C1 deliver the complete class inventory and production profile, material transitions and due probes. At T bind executable recipes, exact data, config and source formats, cost, contact, event and clock contracts, validators and fixture locations for the launch scope. C1 needs complete families and variation rules, with examples as illustrations. At T an obligation determines when the actual output and proof are due. A bounded risk spike can precede complete T. Accept a representative native assembly before mass production, including actual controls and camera, progression and reward, sound and applicable performance proof.

First filter tools for inputs, outputs and editability, platform and version, rights and data constraints, access, budget and an executable verification method. Then compare control, time, quality and maintenance. A required rig, source or native callback remains a gate. Keep the accepted engine. Godot with typed GDScript is one candidate for new work. Evaluate C#, C++ or other engines against a specific need and probe. Backend, PostgreSQL, middleware, cloud, advertising and social are conditional. Choose backend language for the product, with owner experience part of the evidence.

## 2. Five records in the existing Game Model

Store `production.operations.{capabilities,recipes,transformations,attempts,assemblies,obligations}` in the canonical model or linked project artifacts with stable IDs. Retain the existing source of authority. Verify referenced external JSON digests and include them in the dependency graph. `scripts/production_contract.py FILE` checks structure, references, DAG and declared evidence boundaries. Actual invocation, quality, receipt truth and domain review require evidence at their own boundaries.

| Record | Obligation and concrete fields |
|---|---|
| ToolCapabilityRecord | Operation ID, provider, tool, host, target and toolchain. Actual schema and catalog references, supported outputs, unsupported features, input-field and parameter consumption, formats, limits, access, rights, data and cost, proof level, probe and witness, subject digest, invalidation cases and fallback. |
| ProductionRecipe | Requirements, accepted inputs and hashes, owner and competence, consumer, ordered step DAG, exact argv or API binding or numbered GUI actions, outputs and editable masters, transformations, semantic, technical and perceptual validators, budget, allowed effects, repair and stop. |
| SemanticTransformation | Source and target artifact references, units, axes, scale, time base, color, audio and ID conventions, preserved invariants, intended changes, known loss and uncertainty, actual mapping, independent validator, oracle and tolerance. |
| ProductionAttempt | Stable attempt and effect identity before an effect, recipe, input and toolchain digests, parameters and seed state, job, request and run references, append-only observations, actual costs, output hashes and receipts, retry and reconciliation, achieved proof. |
| AssemblyEvidence | Exact scene, build and config hashes, component hashes and runtime bindings, executed scenario, expected and observed invariants, author and reviewer identities, modality, device and human evidence and gaps. |

Preserve `unknown`, `not_exposed` and `not_tested`. Record a seed only when the operation actually supports it. Accepted AI originals, editable source masters and runtime derivatives each have their own immutable hashes and revisions. Check rights for the actual font, sample or mesh independently of tool licensing. Bind the rights ledger to parents, terms and date, commercial, edit, distribution and source-transfer permissions, credits and receipts.

Capability states include candidate, descriptor_discovered or schema_discovered, catalog_verified, configured, operation_tested, integrated and native_verified. Descriptor and schema are separate observations. Each stronger claim needs its appropriate witness. `native_verified` always names the operation, platform, build and device. Verify the operation beyond PATH discovery and verify output beyond a catalog entry.

## 3. Admission and staffing

Before each node, check current accepted input hashes, available capability, actual schema and model support for material arguments and verification of consumption, rights and effect scope, cost and duration limits, output and consumer interface, resource availability and owner. Assign owned paths and account, device, GPU and export slots. Use one writer per source or scene. Verify isolation for shared SDKs, devices and provider jobs separately from file directories. Reconcile a remote job before reclaiming a timed-out lease.

Choose competencies for the outcome across systems and math, world, AI and lore, UX, touch and accessibility, illustration, technical art, rigging and animation, composition, audio and haptics, runtime, native and data, QA and performance, and release and operations. Staff to actual need. Read the actual skill and verify input and output fit before delegating. Record actual agent ID and outputs after work. A material decision or critical acceptance needs a reviewer independent from the author. Record self-checks as the author's own evidence.

A recipe with `status=template` requires instantiation with project IDs, pinned toolchain and exact steps. `command` uses an argv array without shell interpolation, `api` names actual tool and model IDs and bound fields, and `procedure` gives numbered GUI actions, preset paths and expected observations. A missing critical binding blocks its node. Continue independent work.

Verify descriptor, schema, catalog and parameters independently. Resolve model IDs against the actual catalog. A rig API that takes a public HTTPS model URL still needs authorization for any publication of private sources. Verify model consumption of prompts. Record `requirement → schema field → provider capability → consumption check` for every material parameter. An explicit decision can remove an optional cosmetic field. Preserve required parameters.

## 4. Nine recipe families

Files named `recipe-*.json` define algorithms. Bind numeric limits and tolerances to the game before execution. Instantiate each family as a project recipe. The recipient should be able to open the source, rerun export, import and verify behavior without chat history.

| Recipe | Source → editing/transform → output → acceptance |
|---|---|
| R01 2D states | Accepted image, style, camera and action inventory → construction layers and frame, cutout or 3D render route → frames, atlas and clip metadata → identity, pivot, alpha, contact, cancel and actual scene. |
| R02 3D rig/clips | Approved dimensions and views → mesh inspection, retopology, UV and bake → editable rig, weights and actions → GLB, markers and import config → stress poses, sockets, root, contact, gear swaps and native profile. |
| R03 VFX/UI | Exact hazard shape and time and UI states and strings → vector or engine source and timeline → VFX, themes, fonts and bindings → collision overlay, crowded and narrow use, mute, reduced effects and device budget. |
| R04 Adaptive music | Sonic brief, motifs and state graph → composition, session and aligned stems → loop and transition table → every transition, pause, cold decode, voice budget and listening. |
| R05 Material contact audio | Semantic contact, material and outcome → lawful raw, transient, body and tail families → export, bounded curves and deduplication → scrape start, update and stop, resting jitter and crowded mix. |
| R06 Attack SFX/haptics | Windup, swing, block, hit and miss meaning → source variants and patterns → event routing, priority and cancel → parity in mute, mono and no-haptic modes and physical tactile test. |
| R07 Mechanic/runtime | Exact rules, data, states and oracle → typed modules, engine and native adapters → actual scene or binary → boundary, property, differential, scene, native and human checks as applicable. |
| R08 Progress spend/save | State catalog and consistency group → versioned local transaction and optional cloud → commit, migration and recovery adapter → duplicate, process kill, disk full, old save and restore cases. |
| R09 Conditional commerce/RC | Offer, SKU, state and authority → native conformance and sandbox → exact signed candidate and symbols → grant-once, pending, refund, update, store channel and native receipt. |

For 2D, missing reverse views and overlap become explicit authoring work. Verify frame or video generation against animation identity and contact before in-betweening. Convert frame numbers to seconds with explicit FPS. Preserve pivot and offset when trimming, and apply padding and extrusion against bleed. Hit and hurt geometry has its own authority.

For 3D, treat image-to-mesh as a candidate input. Inspect hidden surfaces, manifold geometry where applicable, deformation topology, UV, texel and padding, and normal, ORM and color conventions. Validate topology after automated remeshing. Establish exported deform skeleton independently from the control rig. Specify rest and bind pose, weights, sockets, extreme poses, root motion and controller ownership, constraint baking, selected clips and marker sidecar. Format validation and silhouette, contact and performance each need evidence. Direct .blend import requires Blender on the import host.

For audio, verify stems, MIDI and loops independently from the full stereo track. If deriving them, verify plan, schema, usage rights, bleed and phase. Preserve sessions, dependencies and raw takes. Record tempo, meter, bar and sample alignment. At 96 BPM, 4/4 and 48 kHz, one beat is 30000 samples and 8 bars are 960000 samples without tails. This is a fixture. Choose loudness for the game and verify by listening alongside analysis. Record importer normalization, compression and loop flags, and concrete bus, ducking, voice limit, stealing, dropping, no-repeat and first-use behavior.

Use simulation commitment immediately for contact cues. Keep the durable grant and confirmation at a separate D1 boundary. A whoosh can follow an animation marker. An accepted hit, block or break follows the authoritative simulation result. Isolate cosmetic RNG from combat. Pause, cancel or emitter despawn stops continuous sound and haptics. Verify supported intensity and primitives for the actual hardware. Keep listening or tactile claims open when playback or device evidence is missing.

For code, separate rules, immutable definitions, session state, engine adapter and presentation where they change independently. Choose FSMs, components, commands, events or data-oriented representations as the task requires. Add ECS, DI, CQRS or microservices only for demonstrated needs. Check precision, rounding, timing, capture and tie-breaking using shared fixtures from reference to runtime. Choose GUT or GdUnit4 by pinned compatibility. pytest and Hypothesis apply to Python tooling. Validate a meaningful negative by showing it fails under the intended defect. Integration needs its own test.

For data and native boundaries, preserve exact IDs, RNG and counters through JSON conversion. Keep untrusted deserialization data-only. Choose SQLite or JSON for the actual needs and test the bridge. Use a conformance scene for callbacks, threads, accounts, lifecycle, cancel, release stripping and signing. Reconcile unknown transaction or job state first. Android AAB and APK have distinct install pathways. Verify device splits and signing scope. Apple archive, export and install are separate operations requiring an actual Mac and Xcode route. Pass secret references through the host facility and exclude secret values from the package.

## 5. Semantic transformations and assembly

For spec, source, export, import and runtime, identify preserved invariants, intended changes and uncertainty at each edge. Typical boundaries include pixels and metres, degrees and radians, Y-up and Z-up, linear and sRGB, straight and premultiplied alpha, normal and ORM channels, seconds, frames and samples, marker IDs and root policy, collision and displayed cues, mono, stereo, spatial and music time, and definition, instance and generation IDs. Combine only commensurate values. Use format validators for structure and a separate semantic oracle.

Before testing bind assembly to scene, build, config and component hashes, consumer bindings, scenario, actions, initial state, RNG and time, expected outcomes and tolerances, platform, device, quality setting and modality. Trace input, camera, action, contact, resources, AI and world, presentation, save and reward, and resume. Exercise simultaneous cancel, lethal, phase and interruption, reduced effects, cold first use and peak overlap. Exercise integrated behavior in addition to reviewing individual animation, audio and UI. Use domain-appropriate perceptual and semantic tolerances, including where GPU output differs at the byte level.

Machine coverage checks find outputs without recipes, dangling references, planned execution DAG cycles, missing due proof and unresolved external attempts. Gameplay can contain feedback cycles. Keep each production pass acyclic and record repair in a new revision or attempt. Check death, cancel, recovery, locale and gear variants when required.

## 6. Attempts, repair and cache

Before a costly or external effect, append a pending attempt with stable effect key and current hashes. After submission record the actual provider request or job ID. Append observations. A timeout leaves the outcome unknown. Reconcile status, output and cost first, then obtain available bytes or verify effect_absent. Confirm cancellation independently of the request. Use provider idempotency only when supported. Keep unresolved keys out of dispatch and reserve unknown cost until reconciliation. Append final receipt and immutable accepted output hash from the actual job.

Classify failures as input_contract, unsupported_operation, craft_generation, format_import, integration, environment_access, transient_provider or acceptance_defect. Identify the variable changed, expected correction, next validator, time and spending limits. After two identical unsuccessful hypotheses change the diagnosis or method, or report the precise blocker. A missing rig operation needs a verified route. Retain due requirements and spending authority.

Key caches by recipe revision, operation, input digests, relevant model, toolchain, exporter and importer revisions, platform and profile, parameters and data scope. Preserve the accepted original by hash. An importer change invalidates its derivative and associated proof. Terms, access, schema and provider revision can invalidate earlier observations. Preserve original output bytes when opaque AI cannot guarantee identical regeneration. Validate native and human claims independently of cache hits. Keep absent or stale review proof open.

## 7. Measure the specific claim

Keep separate verdicts for structure, semantics, craft and perception, integration, native and device, human outcomes, and revenue. Record an actual independent QA actor for independent verdicts. Verify fun, input rights, comfort and security according to their evidence needs. An unsupported required claim stays pending or blocked with an owner and next action.

A 60FPS target allows about 16.67ms per frame. Define scene, duration, percentiles, cold and peak cases, thermal, memory, input and I/O budgets before measurement. Exercise touch, audio, haptics and thermal behavior on appropriate devices. Keep editor, headless and simulator results in their observed scope. Hardware fallback preserves gameplay-critical cues and agreed device coverage.

A bounded CI DAG can check data and IDs, format, types and parser, unit, properties and state, importer, scene and adapter, platform build, artifact inspection, due device, sandbox or human checks, then release preparation. Isolate signing and store secrets from untrusted code. Keep dependency caches separate from immutable outputs. Bind exact build ID to source, model, data, catalog, config, save schema, toolchain, symbols, logs and QA. Use a targeted mutation to verify that a check catches its supposed defect.

## 8. Complete handoff and release

Use a host bridge where an actual boundary requires it. Specify producer and target, preflight, working directory, input hashes, exact tool and argv, API or numbered procedure, permitted outputs, secret references, expected receipt, return digest, semantic validation and next action. Verify each platform build with its own receipt. Complete authorized work on the current host before manual handoff. Verify the return before updating readiness.

Record release channel and exact status: prepared, uploaded, processing, testers_available, approved or live. Stopping rollout prevents later distribution. Already installed binaries need their own compatible recovery. A config rollback needs compatibility or a forward fix. Check current requirements, SDKs and licenses before the release candidate. SLSA and PROV can record exact inputs, actions and outputs. Establish quality separately.

After an authorized launch record released build, config and save contract, actual monitoring setup and observations, open incidents, cost, rights and service-loss limits. Start a new request from actual state, impact and scoped design, build, QA and release. Background monitoring needs a running service or scheduler and current authority. Preserve a checkpoint while waiting for a new instruction.

## 9. Primary references and freshness

These references were verified for D2 on 2026-11-02. Recheck `stable/latest`, provider plans and APIs, and store rules when binding the toolchain. The record schema, gates and recipes are Game Atelier adaptations.

- glTF2 interchange, skin, material and animation conventions: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Blender glTF export and retopology: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html and https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html
- Krita animation export and Inkscape CLI: https://docs.krita.org/en/reference_manual/render_animation.html and https://inkscape.org/doc/inkscape-man.html
- Godot animation, retargeting and root motion: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html and https://docs.godotengine.org/en/stable/classes/class_animationtree.html
- Godot interactive and synchronized music and audio import: https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html and https://docs.godotengine.org/en/stable/classes/class_audiostreamsynchronized.html and https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html . Check differences between documented BPM behavior and the actual pinned API.
- Ardour stems, FFmpeg filters and Audacity normalization: https://manual.ardour.org/working-with-sessions/interchange-with-other-daws/stem-exports/ and https://ffmpeg.org/ffmpeg-filters.html and https://manual.audacityteam.org/man/normalize.html
- Apple and Android haptics: https://developer.apple.com/documentation/corehaptics and https://developer.android.com/develop/ui/views/haptics/haptics-apis
- GUT, GdUnit4 and Hypothesis: https://gut.readthedocs.io/ and https://mikeschulze.github.io/gdUnit4/ and https://hypothesis.readthedocs.io/ . Verify actual compatibility.
- Godot Android and iOS export: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html and https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html
- SLSA provenance, W3C PROV, NIST SSDF 1.1 and Bazel cache concepts: https://slsa.dev/spec/v1.2/provenance and https://www.w3.org/TR/prov-dm/ and https://csrc.nist.gov/pubs/sp/800/218/final and https://bazel.build/remote/caching . Apply the relevant concepts within the chosen engine and build system.
