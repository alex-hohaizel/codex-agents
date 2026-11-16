# Lore, knowledge and reactive narrative 4.0

## Navigation

1. Scope and canon
2. Knowledge and causality
3. Quests, dialogue and scenes
4. Integration and save
5. Handoff acceptance and counterexamples

Treat narrative as its own competency even when it appears through brief environmental signals. Measure lore depth by effect on experience. Choose novels, dialogue and branching campaigns only where they serve the game.

## 1. Establish narrative scope

At C1 define fantasy, theme, tone, the world promise, player role and motivation, main conflict, temporal and spatial structure, character and faction identity, important world rules, stakes, failure and recovery, progression arc, optional discovery, ending and replay. Explain how these change gameplay decisions, environment, AI, art and audio.

At T deliver canon, knowledge and state tables, scoped quest, dialogue and scene graphs, conditions, priorities and effects, localization resources, interruption and resume, save and migration, and fixtures. For authored scenes specify exact staging, sequence, camera and input restrictions and reconcile them with dynamic controls.

A canon fact records stable ID and version, proposition, truth conditions, relevant time and region, initial state, permitted changes and owner, causal references, conflicts, holders of knowledge, gameplay dependencies, presentation references and tests. Distinguish immutable canon, mutable world state, rumor and editor-only notes.

Keep a project glossary, voice, style and content restrictions. Use stable localization IDs for names and terms. Translations retain the same quest or item identity.

## 2. Separate world truth from knowledge

World truth can be unknown to a player or NPC. Record a knowledge fact's subject, predicate and value, source and channel, observed time, uncertainty and confidence, lifetime, refresh, forget and share rules, and disclosure conditions. Unconfirmed guesses leave the actual state unchanged.

AI perception and narrative knowledge use compatible facts and can use separate stores. A conversation shares a secret only after the actual choice. Guard spoilers in reason views and in localized names of locked quests.

Trace the causal edge through condition, player or world action, commit, world change, observation or knowledge, and newly available action or opportunity. Test time travel, flashback and procedural ordering when part of the design. Guard reordering so it cannot create contradictions.

Define narrative semantics for death and revival, repair, scarcity, faction memory, world destruction and repeated attempts. Reconcile a quest about the «останній ресурс» (“last resource”) with any nearby unlimited supply. Save restoration must not accidentally revive a boss.

## 3. Define each quest, dialogue and scene

For each node and edge record:

- ID, version and purpose, source requirements, owner and consumer.
- World, progression, knowledge, actor availability and content ownership prerequisites.
- Eligibility, priority and tie-breaking, mutually exclusive options and once or repeat scope.
- Entry and exit, speaker and participants, place and time, staging, camera and input policy.
- Choice preview and commitment, irreversible boundaries, cancel, timeout and default.
- Exact effects on flags, resources, rewards, relationships, routes, unlocks and knowledge.
- Interruptions, dead or missing actors, exit, pause and resume, abandon and retry.
- Localization, voice, subtitles, animation and UI bindings, with a non-audio alternative.
- Save consistency group, migration or remap, and golden cases.

Choice labels accurately convey commitment and stakes. An irreversible effect needs an intentional, understandable rule. Define the purpose and effect of each choice, including ones that do not branch.

Arbitrate concurrent prompts, quest completion, combat danger, boss intros and tutorials. Specify interruption, deferral, cancellation and return of camera and input ownership. A line queued before a world change must remain truthful when played or be withdrawn.

For procedural narrative define grammar, templates and variable domains, knowledge guards, canon constraints, localization agreement, novelty and history, bounded generation, repair and fallback. Generated prose cannot independently alter authoritative world rules or grant rewards. Select NPC runtime techniques for actual needs.

## 4. Integrate relevant systems

World covers geography, landmarks, routes, return and lasting aftermath. AI covers goals, faction knowledge, perception and allowed actions. Catalog explains cultural and functional reasons for tools and acquisition. Progression can reveal meaning through play. Economy covers scarcity, sources, sinks and rewards. Paid access must preserve canon and reachable story state.

Art and audio express silhouettes, materials, architecture, leitmotifs, ambient reactions and voice. Each canonical meaning has an implemented resource or a defined production route. UI and learning enforce spoiler bounds, objective clarity and return reminders. Save keeps flags, relationships, knowledge, consumed choices and rewards causally consistent.

For content availability, DLC, locale and absent actors, specify fallback, blocking prerequisites and migration. Keep narrative changes explicit in catalog updates. An old save with a removed quest ID uses an explicit remap, compensation or understandable incompatibility while preserving the player profile.

A whole-branch or semantic merge must preserve mutual exclusivity of endings. A quest reward, resource spend and resulting flag share a consistency group. Replaying a cutscene must not grant a reward again. An animation callback is not the grant authority.

## 5. Independent handoff and negative cases

Give a new recipient canon, exact state, accepted versions and the scene and quest graph without chat history. Ask them to reconstruct motivation, what each actor knows, available choices, exact outcomes, interruption and resume, return reminders, completion and restore. Record unsupported knowledge, inferred rules and a new counterexample.

Negative fixtures:

- An NPC knows a secret before observation or sharing.
- Dialogue is delayed until the recipient dies. The queued line cannot play as current.
- Two offline saves carry mutually exclusive quest flags.
- Reward, flag and cost separate after termination at a commit boundary.
- A boss is dead but faction or route state keeps a stale unfinished objective.
- A save references paid content unavailable in the client. Fallback preserves causality.
- Translation changes identity or eligibility, or a placeholder hides an important choice.
- A cutscene interruption leaves input or camera locked or duplicates a grant.
- On return after a break, the objective is clear without spoilers or a full tutorial.
- A procedural template creates canon conflict or invalid knowledge.

Review establishes causal consistency in the scoped package. Evaluate dramatic pacing, comprehensible stakes and emotional experience in real human sessions with recorded limits.

## Sources

This approach adapts P1/D1/D2. The listed materials were reviewed on 2026-11-02. Select runtime and plugins for each project.

- MDA, mechanics to dynamics to experience: https://www.cs.northwestern.edu/~hunicke/MDA.pdf
- W3C SCXML, state, event and transition semantics: https://www.w3.org/TR/scxml/
- Dormans, mission and spatial grammar: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
- Epic AI Perception, knowledge acquisition boundary: https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine
