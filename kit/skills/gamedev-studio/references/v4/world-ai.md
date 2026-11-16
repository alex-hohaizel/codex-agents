# World, situations, opponents and bosses 4.0

## Navigation

1. Five layers of the world
2. Generation and diversity
3. Actor, knowledge, action and decision
4. Encounters and bosses
5. Integration, persistence and checks

Use for spatial structure, routes and scenes, dynamic environments, NPCs and opponents, and generation. Include enemies, procedural content, RPG features, open worlds, bosses and LLM agents only when the design needs them.

## 1. Design a coherent world

| Layer | Contract | Check |
|---|---|---|
| Authored foundation | Identity, geography and topology, canon, landmarks and irreplaceable scenes | Variation preserves recognition and causality |
| Mission and progression | Goals, prerequisites, available abilities, learning, risks and rewards | Required abilities become available before the challenge |
| Space | Modules, tracks and rooms, transitions, routes, visibility and reachability | Goals are reachable and transitions legal |
| Situation | Threat roles, resources, weather, events, object state and pacing | Combinations preserve intended responses |
| Durable consequences | Memory, factions, rebuilding and destruction, discoveries and reactions | Restoration and return preserve the causal state |

Distinguish production scale, spatial topology, progression duration and complexity. A small game can have a deep compact world and a large one can use connected authored scenes. Lifecycle includes progression and return beyond a track count. Authored and hybrid scenes can define where and why other layers vary.

At C1 specify world structure, functional situation families, complete progression, return and ending, and actual player choice types. At T provide topology, mission and progression graphs, module ports and parameters, exact conditions and weights, sources, generation algorithms, validation, repair and fallback, and fixtures.

For each route edge specify availability and conditions, state change, required abilities and resources, pre-choice information, risk, gameplay distinction, reward, commitment, return or escape, presentation and persistence. Show the distinct decision behind surface changes. Preserve optional risk and keep purchases within the agreed model.

## 2. Implement bounded generation

Inputs include accepted player and world revision, capabilities and loadout, progression stage, learned mechanics and exposure, difficulty profile, session budget, history, and isolated generator RNG and version.

1. Compute eligible goals and the context boundary.
2. Choose mission structure and authored anchors under the rules.
3. Lay out spatial modules with port, type, scale, navigation and material compatibility.
4. Build routes, keys, resources, encounters and events within constraints.
5. Check reachability, prerequisites, feasible resources, timing and counterplay, lore, semantic diversity and budget.
6. Apply named local repairs within the specified count and time.
7. Sample again only within limits and use a verified compatible fallback when exhausted.
8. Record accepted result, seed, algorithm version, history and repair reasons. Keep rejected results out of player state.

Validation considers a key behind its own lock, mutually exclusive flags, a requirement to use a tool after the last opportunity to obtain it, infeasible resources, unavoidable unseen threats, removed support, exit without a return and performance bounds. Propagate topology and content revision to consumers.

Define semantic signatures from decisions, required capabilities, role combinations, route tradeoffs, resource pressure, environmental interaction and known or new mechanics. Measure actual repetition, coverage and novelty streaks under named player policies. State simulation scope and which cases remain unexplored.

Model pacing, difficulty and progression separately. Pacing can alternate intensity and recovery. Check hidden adaptation after success or purchase against the accepted product. Optional transparent assistance and difficulty use their own contract.

Record challenge across spatial precision, reaction time, simultaneous demands, information and resource pressure, and penalty. Isolate the intended dimension when tuning. For mechanics unused for a long time check exposure and accessible alternatives (D1Q05,Q09,Q10).

## 3. Design AI from player experience and available knowledge

### Actor contract

For each family define role, observable distinction, player response, prerequisite or tool, strong and weak contexts, combinations and progression position. Treat numeric tiers and palette changes as variants unless behavior differs.

The actor record covers definition and instance IDs, motivation and goals, body, scale and shape, movement, turning and acceleration, collision, hit, hurt, parts and materials, resources, stats, armor, resistance and statuses, abilities, perception, knowledge, decision, navigation and positioning, coordination, signals and counterplay, progression and variants, failure, recovery and despawn, rewards and credit, state, save, LOD, budgets and diagnostics.

For allied actors check obstruction, lost player agency or reward, scene interruptions and intrusiveness. Sleeping or simplified actors return without a completed unseen attack. Give body, collider and animation a consistent transform authority.

### Knowledge contract

Separate authoritative world truth, observation and belief. A fact record includes subject, predicate and value, source and channel, time, location and uncertainty, confidence, TTL and decay, refresh and forgetting, sharing audience, delay and range, privacy and authority. Define memory and tracking after loss of sight.

Limit AI sensors to actual allowed observations. Exclude uncommitted inputs, future random outcomes and hidden world truth. A sound may reveal a last-known area. Communicate current position only through actual observation. Define channel and timing for any shared faction knowledge.

### Action and decision contracts

An action covers eligibility and guards, costs, startup and telegraph, targeting lock and tracking, active geometry and window, commitment, combination transitions, interruption, cancel, recovery, cooldown, refund, movement or physics ownership, capture and RNG, cues, expected result and failure.

A decision covers alternatives and eligibility, score or priority, tie-break, reevaluation cadence, commitment and hysteresis, abort conditions, resource limits and fallback. Choose FSM or HFSM, behavior tree, utility, GOAP or HTN for authoring, debugging and runtime needs.

Trace known facts, eligible alternatives, decision reason, command, actual outcome and replanning. Bound log size and retention and preserve hidden information. Record reasons and fallbacks for removed support, occupied slots or unavailable resources.

For a threat compare the reachable response time with cue availability and visibility, input latency and startup. Evaluate actual comfort separately. A bad position can be unrecoverable when the player could know the relevant risk before committing.

## 4. Define encounter and boss contracts

An encounter specifies purpose and objective, arena, routes and visibility, permitted roles and combinations, prerequisites, spawn, entry and exit, resource bounds, attack concurrency, coordination, pacing and recovery, win, fail and abort, reward, save and resume, and budgets.

Test beyond threat totals. Check combined crowd control, indefinite mutual healing, inaccessible responses, spawn near the player, obstruction, camera occlusion and resource starvation. Where attack slots, position reservations or team roles are useful, assign owner, TTL, release, cancel and death behavior, fairness and starvation policy.

A boss blueprint defines its intended function, such as mastery assessment, narrative turn, reinterpretation of systems, optional apex or spectacle. Evaluate the function beyond number of phases.

Required boss fields include prerequisites, arena and camera, complete action catalog, phase graph, exact triggers and priority, HP threshold and overflow, stagger and interruption, projectile and status retention or removal, body, parts and weak points, minions, combinations and RNG bounds, teaching and accessibility, loss, retry and checkpoint, resources, reward and world flags, save and migration, content and budgets.

Choose what happens when lethal, phase and stagger coincide and when player and boss die together. Rewards follow authoritative state. On transition remove invalid colliders, invulnerability, reservations and duplicate grants. Define phase skip and excess damage.

## 5. Integrate dynamic world behavior

Use schedules, local events, weather, sound, ecological and resource responses, NPC routines and persistent aftermath where they improve play. Define activation and simulation radii, offscreen approximation, update rates, maximum active entities, LOD transitions and authoring ownership.

Preserve meaningful invariants under offscreen simplification and rule out impossible outcomes. Treat ambient animation as presentation. A dynamic world can use a compact playable area and bounded background simulation.

Bind actor, action and variant to rig, clip, contact markers, VFX, SFX, haptics, UI, runtime and scene. A break changes topology revision and plans. Death releases slots, cancels invalid commands and creates an exact reward intent.

Give each AI field a persistence, recompute or reset rule. Restore logical state and knowledge, then recalculate paths and planning pointers. Restore dependencies in this order: world topology, actors and resources, knowledge, decisions, presentation and neutral input. For engine or content updates verify golden saves and actor bindings.

## 6. Exercise cross-system counterexamples

- A key behind its own door is deterministically rejected, repaired or replaced by fallback. Record cause and seed.
- A new tool with no generated opportunity is a coverage defect, independently of selection rate.
- An opponent without relevant sensory evidence lacks exact player coordinates.
- Two actors compete for a slot. The owner's death frees it without starving the other actor.
- A support is destroyed during planning. Invalidate the path and cancel the outdated jump.
- Individually valid actions combine into an unavoidable situation. Reject the encounter.
- Effects, finger, camera or language obscure a cue. Check the actual peak scene.
- Phase, stagger and lethal coincide. The oracle does not depend on actor iteration.
- Process termination between boss victory and reward restores one causal group.
- A waking actor cannot connect an old attack before a new readable cue.
- Revision and generation checks reject callbacks from before respawn or profile switch.
- A new recipient reconstructs encounter, phase and retry from the specification without chat and produces a counterexample.

Record scene, native, device and human evidence at their actual boundaries. Exercise a representative slice and measure representative production throughput before scaling.

## Primary materials

P1/D1/D2 research was verified on 2026-11-02. Recheck the actual project's pinned APIs.

- Valve, The AI Systems of Left4Dead, about perception, navigation, behavior and pacing: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- Epic AI Perception: https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine
- Epic Behavior Trees: https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine
- Epic Environmental Query System: https://dev.epicgames.com/documentation/unreal-engine/environment-query-system-in-unreal-engine
- Dormans, Adventures in Level Design: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
- Godot Navigation introduction: https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_introduction_2d.html
