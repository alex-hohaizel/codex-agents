# Causal rules, equipment and game agents

## Applicability, inputs and owned outputs

Use for a game's rules. Include equipment, vehicles, opponents and combat when the design calls for them. Start with the fantasy, system profile, input and camera, world map and progression. Deliver an executable rulebook, interaction matrix, applicable actor, ability and equipment catalogs, decision scenarios and invariants. The [system rulebook template](../../assets/domain-templates/system-rulebook.template.json) guides authoring. Use canonical domains `systems`, `actors` and `equipment` with current `source_requirement_ids`, features, scenarios, dependencies and evidence. Demonstrate depth in play or a relevant model.

## Mechanics as rules

Specify ID, player purpose, state variables, units and ranges, inputs and triggers, guards, authority, phases and timing, transformation, cost, outcome, feedback, error and counterplay, recovery, persistence and reset. Specify event order, clamp, rounding and tie-breaking, fixed or variable time, collision ownership and interruptions. Keep one authoritative runtime or config source and reference it from description and UI.

Count an interaction when a rule changes an available action, position, timing, risk, priority or outcome of another rule. Show concrete loops across relevant movement, tools, environment, agents, resources and objectives. A small set of interacting rules can support depth. Shared color, currency or the label «синергія» (“synergy”) alone does not establish a causal edge.

For an important combination trace starting state, intent, input, changes, world or agent response, next choice, failure and recovery. Show different sensible decisions with the same tool in different contexts. Test an ablation to see which behavior is lost without a rule, whether complexity only triggers a canned effect, and whether the cheapest policy dominates.

## Resources, attributes and equipment

Choose meaningful resources such as HP, stock, heat, momentum, noise or concentration. Define sources and sinks, capacity and regeneration, spend and opportunity cost, overflow and depletion, recovery, cues, reset and persistence, and related actions. Where healing is part of the design, specify its decisions and cost.

For an item or ability define function, acquisition or unlock, actions, targets, reach or shape, startup, active, recovery and cancel windows, charges and cooldowns, modifiers, compatibility, strengths, limits and counters, equip and switching rules, and progression links. For status effects specify duration, stack cap, additive, multiplicative or exclusive composition, refresh and replacement, immunity, cleansing, death, scene and reset rules, and cues. Demonstrate different choices beyond equivalent damage values.

If vehicles are central, distinguish chassis and handling, propulsion, functional modules and attachments, budgets and compatibility. Show how selected properties such as mass, balance, power or capacity influence actions and routes. Specify assembly, comparison, saved loadout, trial, module changes, invalid configurations, repair and recovery. Customization should produce a distinct experience.

## Agents, opponents and counterplay

For an applicable agent define role in the challenge, body and movement affordances, senses, ranges and occlusion, memory and forgetting, uncertainty, intent, decision priorities or utility, actions, navigation, resource use, transitions, coordination, retreats and recovery. Separate world state from perceived and remembered state. Define the effect of noise, tracks, damage, geometry and other actors. Select finite state, utility, behavior tree or other representation based on fit.

For an in-game threat, define telegraph, readable commitment, hit and avoidance conditions, response opportunity, counters, interruptibility, cooldown and consequence. Align offscreen behavior with the camera and provide a fair response. Difficulty can change behaviors and coordination within stated bounds. Check adaptation against hidden input reading and difficulty distortions intended to prompt purchases.

The opponent and challenge catalog distinguishes tactical role, effect on player choices, combinations and exclusions, learning prerequisites, environment and production cost. Use ordinary, elite, special and boss forms where the design needs them. Require a distinct role beyond skin and HP changes. Without combat, apply these principles to rivals, physical obstacles, tasks or other relevant challenges.

## Dependencies and verification

Connect rules to [input, feedback and learning](experience.md), [world and encounters](world.md), [unlocks and rewards](progression.md), [art, motion and audio](creative.md), [commerce](commerce.md), and save and analytics in [lifecycle](lifecycle.md). Hit timing changes reopen animation, camera, telegraph and control checks. A new paid tool needs interaction and dominance review as well as its SKU test.

Concepts need causal scenarios and explicit unknowns. Preproduction needs typed values and contracts and boundary examples. Exercise identical inputs at the slice with recorded state and seed. Observe normal, peak, error and recovery, animation and contact, and actual touch. At beta observe how people read intent and counterplay. At release independently check critical save, money and authority paths. Use models to find soft locks and dominance and observe player experience separately.

Systems authors define rules, AI and encounter specialists define applicable agents, runtime engineers implement and trace, and UX and creative specialists design cues. Independent reviewers exercise counterexamples. An author may hold multiple design roles and still needs an independent reviewer for the affected claims.

## Sources and status of recommendations

- [Epic: AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine) documents a specific tool. Separating perception, memory and decisions applies independently of its API.
- [Epic: Behavior Tree Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview) documents a concrete implementation option.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) illustrates how abilities can change the experience.
- Rulebooks, ablation and evidence gates above are Game Atelier requirements. Choose and verify numeric values for the actual game.
