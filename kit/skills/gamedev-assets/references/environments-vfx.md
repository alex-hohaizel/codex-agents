# Світ, предмети та ефекти

## Environment kit

Виробити весь approved authored vocabulary: terrain/floors/walls/architecture/vegetation/props/background/sky, surfaces/material variants, colliders/navigation/occluders, lights/camera profiles, procedural sockets and scene assemblies. Include all explicit authored locations; a procedural generator does not excuse missing finite kit parts. Keep units/pivots/grid/texel density/material channel conventions consistent.

For each kit part define source/export, placement dimensions, snap sockets, reachability/clearance, collision/material response, destruction/moving behavior, LOD/culling, lightmap/probe requirements, allowed adjacency, biome/style tags and budgets. Preview tiles/joins/edges and unusual rotations. No floating pieces, visible seams, z-fighting, sudden scale changes or empty gray areas hidden outside hero shot.

## Світ як інтерактивний продукт

Виробничі scene/module IDs походять з model world/topology/route/interactable records. Покрити entry/exit/connector states, traversal/camera clearance, landmarks, risk/reward branches, hazard/actor placement cues, bonus/goal visibility, persistence і revisit variants. Інтерактивний kit містить readable before/during/after transforms, collision/navigation changes і restore/reset behavior, коли вони входять у правила.

Мала просторова сцена може мати довгу еволюцію матеріалів/цілей/акторів і комбінацій; сценна гра потребує осмислених переходів та відкриттів; велика — зрозумілої топології, access і consequences. Finite launch inventory має підтримувати саме погоджену арку. Не видавати додаткові textures або permutations тієї самої арени за нові змістовні ситуації. Authored levels допустимі; процедурність не є універсальною вимогою.

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

## Руйнування та revision світу

Authoritative break відокремити від cosmetic debris. Прийнятий contract визначає зміни collider/support/mass/inertia/function, topology revision, nav/visibility/cover/cache invalidation, AI fallback й відновлення зі save. Зламаний міст не лишає required goal недосяжною поза навмисним правилом.

Матеріал має окремі physics coefficients, gameplay reactions і shader/audio representation. Вигляд «мокре» не дає автоматично traction/conductivity. VFX/drop/LOD/tier не змінюють hitboxes, damage або critical cues без design decision.
