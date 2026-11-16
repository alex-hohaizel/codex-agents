# Progression, rewards and long-term goals

## Applicability, inputs and owned outputs

Apply to how the experience develops over time. Add RPG stats, loot, crafting, seasons or permanent power when they serve the design. Read the rules, world and content structure, learning graph, available launch scope and business model. Deliver progression and reward graphs, typed unlock rules, player journeys, pacing and balance model, and novelty and exhaustion plan. Use the [development and rewards template](../../assets/domain-templates/development-rewards.template.json) within the authoritative project records.

## Define what develops

Distinguish applicable layers: mastery and knowledge, state within a run, match or task, persistent character, tool or vehicle abilities, collections and loadouts, world, access and consequences, optional social and team goals, and long-term postgame. Give a domain reason for unused layers. Games without permanent power can develop player knowledge, tools and access. Progression needs an effect beyond incrementing a counter.

For a graph node specify ID, player goal, prerequisites, unlock or grant, new action or opportunity, tradeoff, use, older context it reinterprets, next visible goal, earned and paid relationship, persistence, reset and cap, and evidence. For an edge specify condition, authority, cost or time, presentation, reversibility, failure and recovery. Bind values and formulas to units, ranges, rounding, source and rationale, and one runtime or config source.

Depth in items, skills and vehicles comes from distinct decisions such as range, mode, material interaction, mobility or a constraint. Repeated +1 increases need evidence of distinct play. Give player stats and enemy progression understandable roles, cues and bounds. For trees or modules specify compatibility, preview and comparison, respec and switching, duplicates and useful choices. Add random loot only where it serves this game.

## Rewards as a complete cycle

For each reward family describe the reason, effort or risk recognized, player expectation, exact item, entitlement or state change, claim and presentation, practical use and next meaningful goal. Depending on the design this can be an ability, tool, item, world access, knowledge, customization or recognition. Use XP when it has a defined role.

Specify guaranteed, random or chosen outcome, pool, weights and version as applicable, information available to the player, repetition and duplicates, eligibility, cap, expiry and claim window, authoritative grant, retry and deduplication, persistence and revocation. Show meaningful use separately from rarity and presentation. Earned randomness and paid randomness are distinct product choices.

Connect each reward to a progression node and use scenario. Compare rewards for mastery, exploration, risk, completion, returning and other relevant goals. Choose applicable reasons. Preserve player agency and fair goals. Avoid deliberately blocking enjoyment to sell relief.

## Pacing and complete arc

Define first opening and completed loop, next return, early, middle and late play, absence and return, launch-content completion and postgame. Choose time markers for this genre and scope. For each record what the player knows and can do, new decisions and contexts, rewards and uses, reasons to continue and what could become repetitive.

Show introduction, practice, combination, meaningful variation, and mastery or reinterpretation in a new context. The [learning graph](experience.md) supplies needed knowledge before assessment. The [world](world.md) supplies opportunities and reasons for voluntary return. Prove new roles and decisions when opening zones or increasing stats.

For finite launch scope define content exhaustion, endings, optional challenges and useful replay. A long game can sustain play without indefinite grind or weekly manual events. If ongoing content is in scope, tie cadence to actual authoring and QA capacity and costs.

## Modeling and counterexamples

For complex curves model casual, regular and skilled players, newcomers and returning players, lucky and unlucky outcomes, and nonpayers and payers where the business model applies. Record playtime and session assumptions, performance policies, seeds, config and version, and raw outputs. Check time to meaningful unlock, scarcity and overflow, stranding, mandatory unlocks, snowballing, catch-up, dominant builds, content exhaustion, cumulative paid advantage and soft locks. Prioritize scenario-class coverage over an arbitrary count of seeds.

Counterexamples include unusable rewards, a branch without a useful scenario, a mandatory paid counter, a tool that bypasses all existing limitations, repeat purchase that creates a hidden refill, return that only repeats the same fight without a new goal, and an unsupported «50 годин» (“50 hours”) estimate based on a grind multiplier. Repair the cause before adding currency.

## Evidence timing, interactions and roles

Concepts establish a causal early, middle and late arc and reward use. Exact balance is a separate claim. Preproduction defines typed graphs and rules with concrete worked examples. The slice exercises unlock, presentation, use, save and return in the actual runtime and verifies applicable device and input cues. Beta observes understanding, pacing, reasons to return and meaningful choices with players. Release independently checks critical grant, save and purchase integrity. Live operations rely on real cohorts and distinguish targets from observations.

The progression and rewards specialist owns graphs and models. Systems, world, UX and commerce coordinate implications. Runtime uses the same IDs. Independent reviewers look for dead paths and dominance. A change to reward price, tool capability or world access reopens affected model, UX, content, commerce and save checks.

## Sources and status of recommendations

- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) illustrates collectible abilities, varied routes and access.
- [Roblox: Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques) covers teaching at the moment of relevant interaction.
- Typed unlock and reward graphs, simulation profiles and evidence timing are Game Atelier requirements. Observe retention, demand and player valuation independently from simulation.
