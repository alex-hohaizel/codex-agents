# Preserve the approved reference in the playable game

## Lock the reference

Preserve the exact approved image, audio, or motion sample with version and hash, full resolution, intended device, aspect ratio, scene, camera and state, and the actual owner decision. Derive a construction specification for silhouettes and proportions, forms, palette and color space, materials and shading, light and exposure and postprocessing, depth, camera projection, field of view and distance, world scale, framing and anchors, font binaries and weights and sizes, icon system, UI dimensions, VFX timing and readability, motion language, audio palette and motifs, mix, and haptics. Identify ambiguous or infeasible details in generated references before scaling production.

Create further approved targets for unseen surfaces, topology, rig, motion, sound, and other views. Ask the owner only if a choice materially changes identity. Reconstruction from raster introduces choices about geometry. If physical or budget constraints prevent the reference, present the source-of-truth trade-off before adjusting it.

## Three related baselines

1. **Creative reference** preserves the exact approved original and intent.
2. **Construction baseline** provides reproducible tokens, assets, scene, camera, lighting and render settings, accepted ranges, and remaining unknowns.
3. **Runtime slice** is the actual scene with input, physics, movement, HUD, VFX, music, effects, haptics, and evidence from a specific build and device.

The runtime slice must match the approved visible result and feel within the accepted tolerances. Establish tolerances for differences in GPU, aspect ratio, and animation timing. Character, typeface, art, and composition changes remain subject to the approved identity.

## Work in order

- Reconstruct a normal scene and a peak overlap scene using the representative source and export path.
- Pin deterministic camera, pose and time, seed, resolution, UI state, lighting, quality, and capture method.
- Compare target and actual side by side and as an overlay. Inspect the full composition and critical details at phone scale.
- For deterministic static UI, icons, and layout, use image comparison with documented masks and tolerances. For animated world scenes, combine structure, color, silhouette, and layout checks with independent perceptual review and motion capture.
- Review timing, controls, and physics with traces. Capture actual time-based motion, audio, and haptics where required.
- Record each deviation as a permitted derivative, a baseline defect, or a material creative change requiring the owner's choice.
- Resolve critical identity and feel differences before mass production.

Aesthetic equivalence requires perceptual judgment alongside quantitative metrics. Runtime fidelity requires a capture from the actual game pipeline. Each receipt binds the exact scene, source and export hashes, build, device profile, and capture settings.

## Control changes

Lock creative properties and allowable bounds for palette and color space, silhouette and proportions, typefaces, UI anchors, camera family, action timing, motifs and timbre, relative loudness, and restrained haptics. LOD, compression, safe-area adaptation, and platform audio encodings qualify as derivatives when they stay within those bounds and pass QA. Recoloring, new models, different fonts or melodies, weapon feel, and camera style are material when they change identity or player experience. Review a representative sample with the owner and retest affected artifacts.

## Assembly before mass production

Cover required domain interactions in one connected sequence. Follow input and camera through contact and physics, actors and effects, animation, VFX, audio and haptics, state and resources, reward and save, and return. Verify relevant normal, peak, cancellation, and failure paths, the source round trip and import checks, low-tier budget, and actual proof types. Observe the integrated scene as well as any individual rig or clip.

Record `AssemblyEvidence` for exact inputs, versions, build, configuration, components, scenario, invariant outcomes, captures or traces, and gaps. Keep missing SDK, device, and listening evidence as named obligations. A source claimed to be native compatible still needs actual native verification.
