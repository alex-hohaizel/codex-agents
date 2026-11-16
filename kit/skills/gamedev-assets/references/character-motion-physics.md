# Characters, bodies, and motion as a system

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

## Behavior, properties, and progression cues

Plan actor and equipment variations with model object, state and event IDs. Establish reproducible visual and audio cues for telegraph, commit, recovery and cooldown, status, damage and resource availability, tool mode, charge or heat, upgrades and new abilities. Source clips and events consume accepted rules, including AI behavior and effect values. Reuse a mesh for a new item tier when it still communicates the designed functional difference and limits.

For complex interactions specify approach, contact, grip, use, release and recovery, available interruptions, simultaneous actions and authority. Test the same actor or tool in different world and material states and after a relevant unlock. Record recoloring as a visual variation. Scope combat families to products that need them.

## Delivery checks

Open editable sources and export in a clean/pinned toolchain. Reimport into actual engine project and compare scale/orientation/materials/rig/clips. Capture normal and boundary interactions, multiple camera angles and peak concurrency. Bind evidence to exact source/export hashes. Device-native feel/performance needs actual device receipt; DCC playback is source evidence only.

## Damage and lifecycle representation

Collision supplies contact facts. The resolver decides the accepted hit and resulting state. Produce hit, hurt, part and collision markers and telegraph, commit, recovery, cancel, death, disabled, rescue and respawn states where designed. Keep damage and reward authority outside root motion, IK, ragdoll, and death animation callbacks. Deduplicate grants at their authority.

Define transform ownership from controller to ragdoll to respawn, contact timebase, cleanup for spawn, despawn and pooled generations, and debris limits. For broken parts update source geometry, rig, collision, attachments, cues, and actual function bindings. Test stress poses and integrated contacts with the current physics backend and timestep. Verify any bitwise determinism claim separately from fixed tick.
