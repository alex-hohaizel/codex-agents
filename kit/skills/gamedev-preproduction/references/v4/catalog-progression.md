# Catalogs, compatibility, progression and rewards 4.0

## Navigation

1. Inputs and outputs
2. Families and configurations
3. Progression and opportunity
4. Rewards and completion
5. Acceptance

P1 applies to any system of changing player or agent capabilities, including tools, items, vehicles, weapons, native skills, AI abilities, world modules and collections. Model progression appropriate to the game. A game without upgrades may still expand player knowledge or the situations they can access.

## 1. Recover inputs and boundaries

Read the player fantasy, active systems, mechanics and rules, world and encounter opportunities, progression position, reward and economy rules, art and audio budgets, save authority, and commerce decisions. Recover existing catalog and instance IDs and retain their compatibility.

At C1, deliver the full launch taxonomy, functional axes, family roles, progression lines, acquisition channels, compatibility, usable configurations, contextual tradeoffs, visible and audible feedback, and production feasibility. Demonstration upgrades cover only their declared subset.

At T, deliver every launch entry or the exact generator, ranges, types, units, function IDs, slot, tag and constraint predicates, weights, unlock and reward tables, fixture coverage, content-state inventory, and authoring procedure. For generated catalogs validate every accepted result using executable legality checks and fallback behavior.

Use `catalog-progression.template.json`. Completion needs concrete IDs, data and evidence.

## 2. Design meaningful families

For each family define:

- Its role, player decision and contexts where it is strong or weak.
- Behavioral and interaction differences, delivery, action and resource cycles.
- A typed parameter set with precise mathematical meaning and capture and time semantics.
- Requirements, slots, tags, exclusions and dependencies, and composition rules.
- Acquisition, unlock, ownership, consumption, repair, respec and loss.
- Learning, relevant opportunities, and horizontal and vertical progression.
- Asset, audio, animation, UI and physics bindings and persistent instance state.
- Test scenarios, known limits, feasible production route and budget.

Keep definition IDs, instance IDs and derived loadout stats separate. Encode large IDs exactly. Damage or modification changes the instance. Keep gameplay stats authoritative in one place across the shop, UI, simulation and runtime.

For a legal loadout calculate normalized typed components, prerequisites, allowed combinations, aggregate stats and effects, conflicts, resource capacity and outcome reasons. Bind override, stacking and cap order to behavior rules. `Invalid loadout` needs a specific reason code, field and version (D1Q29).

Test the item, family, pairwise interactions, extreme legal configurations and paid portfolio separately. Enumerate small spaces. For large spaces use risk-based boundary, combinatorial, property and state tests, and state the actual coverage limits.

Compare dominance at equal scenario, availability, price, risk and skill demand. A best item may be an intentional tier upgrade. Explain where earlier items stay useful or why they are intentionally retired. Check whether a new set removes every weakness, which an aggregate score can hide.

Give player-facing aggregates such as «керованість/пробиття/витривалість» (“handling/penetration/endurance”) defined weights and conditions that support a decision. Describe the actual behavior and give `+5` units and context.

## 3. Link progression to actual opportunities

For a progression node or edge record starting capability, prerequisites, condition, cost and mastery, exact change, newly possible decision, next goal, limits, world and encounter opportunities, instruction and exposure, save, reset, loss and respec behavior, presentation and acceptance.

Keep separate graphs for run power, permanent unlocks, equipment specialization, player mastery, collection, and campaign and world access. Use meaningful decisions in early, mid, late and completed play and repeated runs. A generative permutation or uniform HP scale needs independent evidence of meaningful progression.

The capability-by-opportunity matrix connects each family to actual stages, biomes, encounters and generator contexts, frequency and availability, prerequisite timing and alternatives. Check opportunity before interpreting a low selection rate as imbalance. A reward granted after the last usable scene has a timing defect.

The exposure graph covers discovery, safe practice, transfer of learning, combination, reinterpretation and recall after a long absence. Prepare players for a critical late challenge through different routes or an accessible alternative. Use a linear tutorial only when it serves the game.

Check prerequisites for reachability, cycles with no useful exit, soft locks, forced grinding, trap choices, inaccessible currency sinks and completed builds with no opportunity for use. Treat availability of respec as a product decision with cost, commitment and rollback rules.

## 4. Define a reward as a causal operation

For each reward specify trigger and eligibility, source and claim identity, deterministic amount or full distribution, roll timing, stream and pity mechanics, once or repeat scope, inventory destination, duplication, cap and overflow, presentation, durable boundary, next use, retry and reconciliation.

A reward can open an action, route, part of the world, property, fact or tool. Specify where the granted capability is useful. A confirmed grant belongs to a durable consistency group with its condition, cost, craft and quest flags. Animation, sound and cloud merge do not authorize a new grant.

Analyze exploit cycles and soft locks across failure, retry, repair, loot and rescue. Test the complete `Death→insurance→repair→profit` sequence even when each rule validates independently. Include tails and guarantees in time-to-goal distributions.

For completion, maximum upgrades and full collections, specify excess currency and materials, duplicate conversions, exhausted pity or guarantee state, offers, valid next goals, authored ending, replay and the boundary of future content. Describe unreleased content according to its actual state.

## 5. Accept the data and authoring workflow

An author modifies a canonical entry, validates its semantics, exercises a preview and runtime fixture, reviews the diff, and hands it to the consumer for acceptance. A different author can add a legal family or variant without duplicating formulas across files (D1Q27). Return a specific reason for an invalid entry.

Negative cases include palette swaps presented as new families, missing asset state, incompatible modules, prerequisite cycles, a paid portfolio that removes every tradeoff, full-collection overflow, duplicate grant, shared RNG affected by a cosmetic choice, migration that removed a definition, an old save restoring a consumed item, and a tool unlocking after its last opportunity.

Before mass production, follow a representative entry from concept through source, export, import, integration and QA. Measure actual repair work, cost and cadence (Q36). Verify an executable pipeline for the promised catalog and scope any combinatorial counts to what the pipeline can produce.

Keep structural, mathematical, simulation, runtime, native, device and human evidence separate. Evaluate meaningful diversity and ease of play directly.

## Sources

These references were reviewed on 2026-11-02. Each game selects its own formulas and generator instances.

- Epic Data Driven Gameplay, typed data and curves: https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine
- Godot RNG, versioned state limitations: https://docs.godotengine.org/en/stable/classes/class_randomnumbergenerator.html
- Valve AI Director, opportunity and pacing context: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- Steam bundles, ownership-aware composition example: https://partner.steamgames.com/doc/store/application/bundles
