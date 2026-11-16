# Behavior, mathematics, damage and physics 4.0

## Navigation

1. Rule types and contracts
2. Damage resolution
3. Capture, time, RNG and cascades
4. Physics adapter
5. Death, failure and recovery
6. Oracles, acceptance and sources

Use for numeric and timed mechanics, resources, in-game damage, motion, contact, state and randomness. HP, critical hits, enemies, ragdolls and repair are conditional game features. Active mechanics require exact rules at any scope.

## 1. Choose the rule representation

Use a function, table or curve for transformations, a state machine, decision table or algorithm for discrete behavior, and an engine solver contract for physics and navigation. Specify exact boundaries between models. Keep arbitrary eval and ad hoc execution languages out of JSON data.

`behavior-rule.template.json` gives the rule framework: ID, version, owner, requirement references, purpose, typed inputs and outputs with units, domain and precision, source of truth, guards, algorithm or function ID, update order, time base, capture, RNG, state reads and writes, effects, invariants, bounds and errors, presentation, persistence, fixtures and consumers. Local scripts and data implement compatible behavior or pass shared oracle cases.

At C1 specify the model and rationale, material dimensions, interactions and exceptions. Tuning may remain in a bounded range with a plan. At T specify executable ordering, initial values and tolerances. Include units and domain.

Distinguish additive and multiplicative operators, percentage points and relative percentages, current, maximum and missing resources, base, derived and cached values, source and target, and definition and instance. Specify priority and tie-breaking for overrides, and the placement of caps. Define rejection of NaN, infinity, division by zero, overflow and invalid negatives.

## 2. Build the in-game damage resolution contract

Separate intention, physical contact, eligibility, calculation, outcome and presentation. A marker can open an active window. An actual query or solver adapter supplies a contact candidate, then gameplay rules decide eligibility.

| Stage | Inputs and required outcome |
|---|---|
| Action commitment | Guard, cost and cooldown, active window, cancel and refund → action instance |
| Contact candidate | Tick, method, engine and version, IDs and generation, shape and part, point and normal, available velocity or impulse |
| Hit eligibility | Authority, team and friendly fire, category, range, occlusion, window, immunity, dodge and repetition → acceptance or reason |
| Channels | Typed effect components with separate delivery, damage channel, status and material dimensions |
| Scaling and defenses | Capture, flat, additive, multiplicative, override, conversion, critical, armor, resist, penetration and block order → intermediate values |
| Resources and parts | Barrier, HP, components and overflow mapping, actual loss and overkill without double debiting |
| Secondary effects | Buildup, damage over time, stagger, interruption, knockback and observation under exact predicates |
| Outcome | Lethal, part break, phase, objective, credit and reward intents with arbitration |
| Simulation commit | Consistent application in the gameplay model → immediate hit feedback |
| Durability | Separate persistence of causal groups and critical confirmations under the persistence contract |

Choose and version the order and balance rules for this game.

An effect packet includes root, parent, action, effect and hit IDs, source and target instance and generation, instigator and credit owner, current team as specified, part, tick, and rules and catalog versions. Projectile ownership, kill credit and team can differ. A generation guard prevents a stale callback from affecting a reused ID.

Define deduplication scope. One hit can use `(action,target,active_window)`, allowed multi-hit adds hit index, and a damage-over-time tick can use `(effect,target,tick)`. Match the key to the mechanic. Multiple hurtboxes and replay, resume or repeated callbacks cannot duplicate an effect without a rule that allows it.

An effect or statistic contract covers type, units, domain, base, current and derived values, scaling references, modifier groups, capture timing per input, duration, tick, stack and cap, immunity, cleanup, source and credit, RNG, save state, cues and oracle. Specify attack penetration, target armor reduction and projectile piercing independently. Healing needs its own rule.

A barrier defines channel eligibility, shared or per-channel pools, layer priority, decay, spillover and concurrent channels. For parts define routing to global HP, effects of part integrity on function, and collider, AI and control changes. Keep buildup and stagger separate from HP loss. Choose `accepted_hit`, `positive_mitigated`, `barrier_loss`, `actual_hp_loss` or another explicit predicate for each trigger.

## 3. Specify capture, time and RNG

Name when each scaling input is read from snapshot or live state: commitment, spawn, application, impact or tick. A weapon swap after firing changes an existing projectile only when the rule says so. A source buff can be snapshotted for damage over time while resistance reads live state. Make the choice explicit.

For damage over time specify rate in HP/s, tick interval and time base, first and last tick, tick-before-expiry or other priority, partial ticks, refresh or independent stacking, cap and overflow, pause and time scale, scene exit, source death, cleansing, offline and catch-up, and maximum work. Resume from the next tick.

An RNG record defines eligibility, distribution and weights, conditional dependence, algorithm and version, seed, state or counter key, roll consumption policy, stream, history, pity, duplicates and accepted outcomes. Determine dependence among hit, critical and activation. One exact wrapper uses `u∈[0,9999]` and success iff `u<p_bp`. Test 0 and 10000 if selected.

Separate combat, loot, generation and cosmetic streams. An added sound variation must preserve combat results. Bind replay to seed, algorithm, version and environment. Test cross-platform physics determinism independently of a fixed timestep.

Reflection, retaliation, lifesteal and conversion form a bounded causal tree with root and parent IDs, their own scaling and a recursion guard. Specify maximum chain depth and work, reflective child behavior, zero effects and death. Verify that reflect → leech → retaliate terminates.

Process simultaneous events under a named atomic boundary and total order, for example `(tick,priority,stable_sequence)`. Explicitly arbitrate lethal, phase, stagger, expiry, resurrection and objective behavior. Avoid relying on actor map traversal to decide deaths or grants.

## 4. Define the physics adapter

Choose scripted motion, character controller, rigid body or a hybrid for the intended game behavior. Specify engine, backend and version, world units and scale, mass and inertia, timestep, substeps and catch-up cap, CCD, sleep, constraints, friction and restitution, layers and masks, query order, teleport, pause and slow motion, and transform ownership.

In the collision matrix distinguish blocking, hit and hurt, perception, interactable, pickup, support and debris. Verify sensor, CCD and contact semantics on the pinned engine. If a sweep callback has no impulse, record `unavailable` and apply the defined fallback. Recheck Box2D advice across versions.

Use relative contact-point velocity, normal, materials and parts and required provenance. In 2D, `v_contact=v_COM+ω×r`. For an idealized single contact without friction or additional constraints:

`1/m_eff=1/mA+1/mB+(rA×n)^2/IA+(rB×n)^2/IB`.

`J=(1+e)*m_eff*s`, where s is normal closing speed and e is restitution. A static wall has zero inverse mass and inertia. Use this as an analytical oracle within those assumptions, alongside the scene solver.

Contact-to-damage rules specify measure, units and domain, aggregation window, threshold, curve, material and part mapping, saturation, exceptions and version. Convert quantities explicitly before combining joules, N·s, m/s and HP. If additional gameplay knockback applies, distinguish it from solver impulse.

Define how a moving platform affects inherited velocity, detachment, crushing, removed support and teleport. Through controller, ragdoll and respawn assign one transform writer, velocities, contact reset and camera ownership. Interpolation changes presentation and leaves original contact authority intact.

Materials have distinct physics, gameplay and presentation mappings. A wet-looking shader does not establish conductivity or traction. An authoritative break changes applicable collider, mass, support, function, topology, navigation, visibility, cover and save. Cosmetic debris uses a separate lifetime and budget.

After topology revision invalidate or recompute dependent paths, cover and visibility caches, encounter legality and goals. Define accepted irreversibility or rescue and alternative access. Verify that required goals stay reachable.

## 5. Define lifecycle and failure

Distinguish alive, downed, disabled, dead, despawned and respawning according to design. Representation despawn and animation completion are separate from kill authority. A game collision can damage a part, tip a vehicle, restrict controls, immobilize or end a run under explicit rules.

A failure profile records cause, guard and authority, entry effects and allowed actions, timer, resources and parts, projectiles and statuses, collision and body, AI reservations, camera and cues, cargo and loot, terminal condition, recovery, rescue and retry, cost or refund, checkpoint or reset, aftermath and persistence.

Test simultaneous player and boss death, lethal with phase and stagger, timer with resurrection, two rescues, reward callback after despawn and stale contact after respawn. Define whether phases can be skipped, and threshold clamp and spillover.

Recovery restores neutral input, appropriate position and camera, resources, world and encounter state, already granted rewards and a usable next action. Choose permadeath, gear loss or paid continuation only when part of design. Explain defeat using information available before the event and feasible responses (D1Q01–02).

### Separate simulation and durable commit

Simulation commit applies one outcome to authoritative game state and immediately provides hit, UI, VFX, SFX and haptic feedback. Durable commit separately persists important state. Tie critical reward, spend and victory confirmation to the actual durable boundary. Define a bounded dirty or checkpoint window, writer queue, previous-good generation and recovery.

Asynchronous saves must preserve and deduplicate confirmed rewards. Ordinary contact cues remain immediate without waiting for disk or cloud. State the actual post-failure guarantee to the player.

## 6. Exercise oracles and counterexamples

For each golden trace record inputs, exact intermediate values, capture, timing and order, expected final state, emitted and rejected events, durability obligations and tolerances. Use an independent oracle beyond the same runtime function.

Illustrative damage oracle. Physical 100 plus flat 20, increased 25%, multiplied by 1.1 and critical 1.5. Fire 40 times 1.25, with critical only for physical. Armor 100 and K 100, percent penetration .2 and flat 10. Fire resistance .25 − .10 = .15, a decrease of 10 percentage points from 25%. Physical block 20 follows mitigation. Apply ties-to-even per channel, barrier 30 physical-first, HP 100. Physical before rounding is 125.588235…, fire 42.5, rounding to 126 and 42. After barrier, 138 reaches HP, actual loss 100 and overkill 38. These are fixture assumptions.

Illustrative damage-over-time oracle. Rate 6 HP/s, ticks .25 through 2.00 inclusive. Resistance .25 on ticks 1–4 and .5 on 5–8, barrier 1.5 and HP 10. Total mitigated amount 7.5, actual HP loss 6 and final HP 4. Stagger +2 on each positive HP loss gives 14. HP after tick 4 is 7; resume starts at tick 5.

Illustrative physics oracle. At central contact of an 800 kg game body against a static wall, normal speed 5 m/s and restitution .2 give effective mass 800 kg and impulse 4800 N·s, with initial normal energy 10000 J and loss 9600 J. At a .5 m lever and inertia 200 kg·m², effective mass is 400 kg and impulse 2400 N·s. These fixture values describe simulated contact.

Evaluate strategies beyond mean DPS. For HP 30 and first attempt at 1 s, guaranteed 10/s finishes at 3 s. A hit of 20 with independent probability .5 has the same expected 10 per attempt, with mean 4 s, median 3 s and p95 8 s. Include overkill, thresholds, time, resources, geometry, risk and opportunity beyond `HP/E[D]`.

Required negatives include multiple hurtboxes, stale pooled IDs, zero, immune and barrier-only outcomes, expiry with refresh and tick, capture changes between spawn and impact, NaN and overflow, reflection cycle, simultaneous death and phase, support break, time scale or missed render, cold restore and grant-once. Verify thresholds, parameter sensitivity and the paid portfolio. Record actual engine, native and human claims separately from structural and mathematical checks.

## Sources and freshness

P1/D1/D2 research is dated 2026-11-02. Verify version-specific docs and probe the actual engine binding. The models above use the stated assumptions.

- Epic Gameplay Effects and lifetime, stacks and cues: https://dev.epicgames.com/documentation/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine
- Box2D Simulation and engine-specific contacts, sensors, events and timestep: https://box2d.org/documentation/md_simulation.html
- Erin Catto, Sequential Impulses, 2006: https://box2d.org/files/ErinCatto_SequentialImpulses_GDC2006.pdf
- Godot physics introduction: https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html
- Godot RNG, seed and state limits: https://docs.godotengine.org/en/stable/classes/class_randomnumbergenerator.html
- W3C SCXML state and event interpretation: https://www.w3.org/TR/scxml/
