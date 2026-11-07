# Персонаж і тіло як система

## Character production contract

For each character/creature/prop family supply turnaround and action silhouettes; real editable 2D/3D source; topology/UV or layer/sprite organization; materials/textures; scale/axes/pivot; rig/skin; collision/interaction shapes; attachments/sockets; clips/blends/events; exports/import settings; gameplay-scale previews. Portrait art alone is not a character model. Do not force 3D fields for a 2D design; equivalent pivot/deformation/layer/sprite contracts remain required.

Record landmarks and dimensions for head/torso/pelvis/limbs/hands/feet/accessories. Each body part's behavior must be explicit where it affects action: joint range/constraints, contact role, IK target, collision/hitbox, weapon/prop socket, damage reaction, secondary motion and visibility. This is game-relevant fidelity, not a demand for simulated biology where it adds no value.

## Rig and deformation

Include bind/rest pose, bone/control/socket map, weights/influence limits, skin/export settings, facial controls where required, retarget constraints, root and orientation convention. Check extreme poses: shoulder/arm elevation, elbow/wrist bend, hip/knee/ankle, grip, crouch/landing, attack, death. No mesh collapse, noodle arms, inverted joints, detached hands, floating attachments or uncontrolled stretch. Bake constraints that the engine importer cannot execute; record how editable source maps to baked export.

## Motion inventory

Every named clip has source/export, rig ID, duration/fps, looping/in-place/root motion, event tracks, anticipation/action/recovery phases, contact points, start/end conditions, cancel/interrupt windows, transition/blend rules, camera contribution and acceptance preview. Do not relabel one idle as six actions. Animated breathing/sleep is actual secondary motion with restrained cadence, not whole-image bobbing.

Validate foot/hand contact, weight transfer, arcs, timing/spacing, follow-through, recovery, loop seam, blend continuity, root drift, ground penetration, foot sliding and event synchronization. Every clip must be seen in real-time and slowed where needed; metadata/fps counts alone cannot prove motion quality.

## Physics and animation authority

Use exact simulation units, scale, fixed tick and gravity/friction/restitution/mass/damping/constraints from design. Specify physics body type and collision layer/mask per part/item; hitbox vs hurtbox vs interaction/trigger; moving platform transfer; CCD for fast motion; ragdoll/kinematic transitions; swept collision/contact policy. Define whether movement is controller-, physics- or root-motion-authoritative and how rendering interpolates. Double authority causes drift and must be avoided.

Object interactions have explicit approach/contact/grasp/release/throw/bounce/break/recovery state rules and matching animation/audio/VFX/haptic events. Hit reaction cannot silently change competitive hit geometry. Visual limbs may use IK to meet a socket, but do not modify core movement rules without design change.

## Поведінка, властивості та progression cues

Планувати actor/equipment variants з model object/state/event IDs. Telegraph/commit/recovery/cooldown, status, damage/resource availability, tool mode/charge/heat, upgrade або нова ability мають відтворювану видиму/звукову мову. Не придумувати AI або числа ефектів під animation; source clips і events споживають accepted rules. Новий рівень предмета не обов’язково потребує нового mesh, але його функціональна відмінність і межі мають читатися за задумом.

Для complex interaction задати approach/contact/grip/use/release/recovery, доступні interrupts, simultaneous actions і source authority. Перевірити той самий actor/tool у різних world/material states та після релевантного unlock. Не називати recolor новою поведінкою й не додавати бойові сімейства небойовій грі для заповнення inventory.

## Delivery checks

Open editable sources and export in a clean/pinned toolchain. Reimport into actual engine project and compare scale/orientation/materials/rig/clips. Capture normal and boundary interactions, multiple camera angles and peak concurrency. Bind evidence to exact source/export hashes. Device-native feel/performance needs actual device receipt; DCC playback is source evidence only.

## Damage і lifecycle representation

Collision дає facts; resolver визначає accepted hit/state outcome. Виробити hit/hurt/part/collision markers, telegraph/commit/recovery/cancel/death/disabled/rescue/respawn states лише за design. Root motion/IK/ragdoll не привласнюють damage або reward authority; death-animation completion не дає повторного grant.

Задати controller→ragdoll→respawn transform ownership, contact timebase, spawn/despawn/pooled-generation cleanup та bounded debris. Для broken part оновити source geometry/rig/collision/attachments/cues і actual function binding. Stress poses й integrated contact scene перевірити з current physics backend/timestep; fixed tick не доводить bitwise determinism.
