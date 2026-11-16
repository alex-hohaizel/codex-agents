# Concept 4.0 fidelity through production

Read [creative](domains/creative.md), [experience](domains/experience.md), and the [Game Model workflow](game-model-workflow.md). Bind camera, controls, graphics and states to stable model IDs. Verify native scenes separately from templates and generated frames.

## Independent camera decisions

| Decision | Record | Why |
|---|---|---|
| Projection | Orthographic or perspective, side, top, isometric or other axis, world scale. | A fixed projection supports different camera movements and locations. |
| Tracking | Target, follow, dead zones, lookahead, damping, bounds, respawn and recenter. | Show the area and reaction time needed for movement. |
| Framing | Hero, tool and target size, focus, HUD, safe areas and offscreen cues. | Derive scale from contact precision and speed. A universal 12% target does not apply. |
| Zoom and modes | Trigger, purpose, limits, transition and target readability. | Precision tool behavior and navigation can need different framing. |
| Coverage | Authored geometry, layers and tiles, occlusion and cutaways, visible horizon. | Avoid exposing unfinished views or hiding relevant hazards. |
| Input and comfort | Thumb overlap, targeting, camera workload and reduced motion. | Preserve comfortable and unambiguous controls during camera movement. |

Provide normal, peak, critical-contact and transition scenarios for each candidate. Define framing when character size, vehicle or state changes. Choose static framing, scroll, follow or context zoom based on the action. Label cutscenes and promotional angles. A single viewport shows a scoped portion of topology and content.

Use the [camera-framing](../assets/domain-templates/camera-framing.template.json) and [visual-state-coverage](../assets/domain-templates/visual-state-coverage.template.csv) aids. Use [model format](model-format.md) for authoritative schema and field names.

## Define the art system before generation

Describe fantasy and emotional promise and define shapes, silhouettes, proportions, lines and edges, palette roles, materials and textures, light and contrast, architecture, characters, enemies and props, type, icons, HUD and menus, motion and contact, VFX, music and audio, and haptics. For each family record fixed, variable and prohibited properties. Compare actual art direction beyond color. Shared tooling can support different styles.

The production profile distinguishes intended and available authoring, export and runtime tools, versions and evidence, rights, cost and capacity, editable sources, sprite, model, rig and animation representations, camera and scene coverage, materials, light, VFX and UI, asset state families and due proof. Choose a feasible 2D, 2.5D or 3D route. A missing local DCC may require a handoff. Verify modeling, rigging, physics and capacity through their own operations.

Before promising cloth and fluids, hand contacts, free camera rotation, PBR or GI, or large volumes of unique assets, identify the achievable route. Preserve the quality target and use bounded source, assembly or motion proof for material risks. Give unresolved prerequisites before selection.

## Inspect each frame

1. Bind source requirements and model IDs, camera, element and state references, production profile, and current causal scenario to generation.
2. Generate an ordinary gameplay viewport with realistic scale and density, functional HUD, core action and achievable source and motion representation. Derive touch controls from the input grammar.
3. **Inspect each actual frame before showing it.** Check projection and tracking implications, hero, tool and target sizes, readable causal state, contacts, hazards, hierarchy, HUD and input mapping, thumb occlusion and profile limits. Mark any uninspected frame.
4. Record observer and image digest, scope, deviations, verdict and repair. Keep a sampled independent review at its observed coverage. Text, metadata and hashes establish distinct properties.
5. Repair the image, authored design, or route before showing a deviation. For material choices provide directly comparable samples. Reconstructing a source requires its own proof.

Keep original bytes and hash, resolution, aspect, color, generation and input provenance, rights and limitations. Each visible element has a stable ID, bounding box, layer and depth as needed, role and interactions, style, camera and light, source and assembly route, evidence status, owner and closure. Verify any hidden geometry, back view, rig, font binaries, physics and stems separately from a PNG.

## Lock references and expand the chosen direction

Bind owner acceptance to exact revision and scope. A concept choice, HUD acceptance and production authority are distinct. Record accepted original and hash, camera and framing, character and world, materials, light and UI, source lineage and permitted changes. Reuse unchanged sources byte-for-byte and bind derivatives to a recipe.

Before scaling, prepare:

- Whole-frame target and annotated elements.
- Tokens and silhouette, materials, line, light, camera, UI and type rules, font rights or pending choice.
- First play, normal and peak states, relevant locations, menus, store, inventory and recovery.
- Locomotion, tools, enemies and interaction variants, contact phases, and physics and collision constraints.
- Audio cue families, music states and transitions, haptics, and actual authorized auditions.
- Finite inventory, source, export and import settings, budgets, rights, gaps and next proof.

Extend rooms and assets through shared style and state rules and sources. Mark audio or haptics unperformed until auditioned or observed natively as required. A source, import and native slice must preserve camera, contacts, interaction and the art target. Measure performance, thermal behavior, memory, input and session behavior on appropriate devices. A target of 60 FPS needs actual measurement.

Compare target and actual under controlled aspect, camera, state, seed and time. Use pixel difference where conditions allow, and evaluate artistic fidelity and feel with their own methods. Track screenshots, native builds and player observations as different evidence.

## Manage drift

Recheck affected encounters, learning, art, import, performance, and QA after camera distance or tracking, rig, silhouette, animation contact, material, shader, HUD, input or audio changes. Use upstream repair, actual sample and owner decision before scaling a material downgrade. A generic primitive cannot stand in for «тим самим стилем» or a canned contact for «тою самою фізикою». Verify production sound design through listening.

## Bind the production operation before the promise

Before showing the target, verify the capability and recipe with actual input and output formats, schema, catalog and argument bindings, representation, rights, cost, host, semantic invariants and due proof. Verify the operation separately from discovery. Identify source, clip, collision and cue states for motion, death, crash, and destruction.

Check camera and input grammar, visible props and abilities, accessible progression, state and resources, and outcome together. Keep model metrics distinct from native measurements. When a generator ignores a required parameter, repair the route before promising the exact result.
