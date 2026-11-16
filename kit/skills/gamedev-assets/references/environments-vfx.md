# Game environments, props, and effects

## Environment kit

Produce the complete approved authored vocabulary: terrain/floors/walls/architecture/vegetation/props/background/sky, surfaces/material variants, colliders/navigation/occluders, lights/camera profiles, procedural sockets and scene assemblies. Include all explicit authored locations; a procedural generator does not excuse missing finite kit parts. Keep units/pivots/grid/texel density/material channel conventions consistent.

For each kit part define source/export, placement dimensions, snap sockets, reachability/clearance, collision/material response, destruction/moving behavior, LOD/culling, lightmap/probe requirements, allowed adjacency, biome/style tags and budgets. Preview tiles/joins/edges and unusual rotations. No floating pieces, visible seams, z-fighting, sudden scale changes or empty gray areas hidden outside hero shot.

## Environments as interactive systems

Derive scene and module IDs from the model’s world, topology, route and interactable records. Cover entry, exit and connector states, traversal and camera clearance, landmarks, risk and reward branches, hazard and actor placement cues, reward and objective visibility, persistence, and revisit variants. Where applicable, the kit shows readable before, during and after states, collision and navigation changes, and restore and reset.

A small space can evolve through materials, objectives, actors and combinations. A scene-based game needs meaningful transitions and discoveries. A large world needs navigable topology, access rules and consequences. The finite release inventory supports the accepted arc. Count texture variants and arena permutations as new situations only when they change play meaningfully. Use authored or procedural levels according to fit.

## Procedural world fidelity

Generator source/config/version/seeds must create actual outputs. Validate grammar, semantic diversity, navigation/traversal/combat solvability, safe starts/ends, camera clearance, telegraph visibility, difficulty/pacing and fallback. Compare representative normal/boundary/rare seeds. Each generation class must preserve approved art direction; random palette/asset assortment does not become coherent variety.

Provide deterministic reproduction command and saved failed seeds. Repair/reject policy must terminate and use a lawful authored fallback. Do not claim «infinite levels» from a combinatorial count of visually or strategically identical pieces.

## VFX production

Each effect needs real source (particle graph, shader, flipbook, mesh, curves), export/config, spawn/attach transform, timing timeline, audio/haptic event IDs, priority, pooling/lifetime, bounds, quality tiers, reduced-effects alternative and preview. Distinguish anticipation/telegraph, impact/contact, aftermath and dissipate. Key gameplay feedback cannot vanish under optimization without an alternative.

Test in layered sequences: multiple hits/statuses, overlapping UI, camera movement, slow/fast timescale, pause/resume and device thermal quality reduction. Preserve readability of target/hazard/player/ball/landing route; no opaque bloom cloud or excess screen shake. VFX never grants damage/reward itself; semantic gameplay event is the authority.

## Materials/lighting

Supply actual shaders/material graphs/textures/channel packing, color-space settings, normal conventions, alpha/blend/cull/depth behavior, tiling/mips and import settings. DCC procedural shader is not assumed portable; bake or recreate with verified equivalence. Lighting/camera/exposure/postprocess source is part of the asset package. A hero render under studio lights cannot establish in-game shading.

## Budgets

Measure representative and peak scenes for triangle/vertex/skinning/draw/texture/particle/overdraw/light/shader costs on target profiles. Optimize with declared LOD/atlas/pooling/culling/compression while preserving silhouette, hierarchy and event meaning. Record exact before/after captures, affected IDs and build. Editor estimates remain provisional until native measurement.

## Destruction and world revision

Separate authoritative destruction from cosmetic debris. The accepted contract defines collider, support, mass, inertia and function changes, topology revision, navigation, visibility, cover and cache invalidation, AI fallback, and recovery from saved state. Keep required objectives reachable after a bridge breaks unless a deliberate rule says otherwise.

Keep physics coefficients, gameplay reactions, and shader and audio representations distinct. A surface that looks «мокре» gains traction or conductivity behavior only through a rule. Changes to hitboxes, damage or critical cues from VFX, drop policies, LOD or quality tiers need a design decision.
