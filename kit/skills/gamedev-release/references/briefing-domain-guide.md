# Adaptive briefing for Game Atelier

`assets/briefing-topics.json` supplies domain topics for the shared BRIEF / RESUME protocol (`БРИФ` / `ВІДНОВИ`). Select relevant topics from the catalogue. `director` maps to `gamedev-director`. The other eight keys map to the active routes in `assets/stage-catalog.json`. Each route represents a competence. A local repair may need only one route.

Recover the current intent, sources, decisions, accepted originals, and actual artifacts first. Fill known answers with their exact source, revision, and applicability limits. Keep agreed decisions and flag conflicts or stale facts. For new work, distinguish the full target game, launch scope, and nearest probe. A time, budget, or tool constraint requires an explicit decision before it changes the genre, controls, progression, platform, or level of craft.

## Select the next topic

1. Include shared topics and applicable topics for the active route. Record the rationale for applicability, known and unknown details, answer owner, and dependent decisions. A mechanic excluded by design may be N/A. Missing tools or access cause a blocker.
2. Follow `downstream` dependencies. Ask now if a future platform, commerce model, network architecture, content source, rights decision, or persistence requirement changes the current design. A purchase that unlocks a different game tool needs its value, earned/free path, and compatibility at concepts. Store product IDs and sandbox receipts are due later.
3. Start with the first unresolved material question on which other decisions depend. Group only related decisions and adapt each round to the owner's answer and the subject. Catalogue size, presets, controls, and question rounds impose no limits on the game or briefing.
4. For each material owner decision, provide practical options, their consequences, and a recommendation grounded in evidence and the project. Verify popularity, market, and revenue claims. Accept free-form answers and “I don't know.”
5. “I don't know” delegates investigation and recommendation to the specialist. The current authorization determines who may choose the goal, creative promise, material trade-off, spend, or external action. Resolve technical details within the accepted constraints and show the consequences of a material deviation.
6. Recompute dependencies after each answer. Retire answered questions and add newly affected topics. If a material topic is missing, create a project-owned topic with a new stable ID and the same fields.

`criticality` helps set the order. `material` affects the promise, scope, or a significant choice. `technical` usually belongs to the specialist. `future` describes a later gate or operation. Surface material effects even when a topic is technical or due later. `mixed` ownership separates the user's goal from specialist implementation. Use `delegated` only when an actual handoff produces an output.

## Establish maturity and valid deferrals

C0 is an explicitly unfinished sketch. A candidate presented as a complete concept requires C1. Cover the fantasy, applicable TR01–TR20, interactions and mechanic families, available strategies, world and situations, progression arc, failure and recovery, complete player journey, controls/camera/accessibility, art/audio, commerce and free path, persistence, feasible production, and bounded launch and expansion. Resolve core architecture at C1. Establish system passports and a feasible production profile before illustration, then inspect every illustration in its actual medium before showing it.

C1 can defer numeric tuning with a range, objective, selection method, owner, due gate, and affected IDs. For example, research the duration of an established cooldown after deciding whether players trigger the action directly or it happens automatically. At T, before implementation, require an exact baseline, units, capture/time/priority, rules/state/catalogue/AI/generation/persistence, fixtures, tolerances, budgets, and consumer acceptance. Later tuning still needs a baseline, range, and criterion.

Defer future evidence only with a precise due gate and owner, keeping it pending or blocked. Native/device/human/purchase evidence belongs to its actual stage. Design choices due at concepts remain due even when proof comes later. Before scaling production, accept a representative source-to-export-to-native slice covering input, camera, art, motion, contact, audio, haptics, and saving where applicable. Track built, installed, tested, independently reviewed, and user accepted separately.

## Check domain coverage

| Dependent area | Open topics that apply |
|---|---|
| TR01–TR04: experience, lore, state, and actions | Fantasy and rejection criteria, story knowledge and consequences, lifecycle, physics/contact/time/rules |
| TR05–TR08: capabilities, AI, world, and situations | Catalogues and compatibility, perception and counterplay, routes and persistent consequences, generation/novelty/repair/fallback |
| TR09–TR12: playthrough, progression, rewards, and commerce | Full progression and returning, skill and unlocks, sources/sinks/grants, paid/earned/no-offer value and cumulative effects |
| TR13–TR16: controls, UX, visuals, and sound | Complete input grammar and concurrent demands, camera and cancellation, end-to-end journey/onboarding/accessibility, sources, motion, music, feedback, and alternative channels |
| TR17–TR20: platform, production, evidence, and evolution | Authority/save/offline/network, authoring/rights/source-export-import, oracles/device/human evidence, exact release/migrations/support/observations |

Use RPG mechanics, enemies, inventory, crafting, servers, virtual currency, and subscriptions only where the game requires them. For direct controls, identify player intent, simultaneous actions, grip, recognition and pointer ownership, physical accuracy, cancellation, camera arbitration, and accessibility before selecting an input grammar and ergonomics checks.

Before accepting an execution scenario, resolve all applicable material questions for its scope and their early downstream effects, or record the owner's explicit removal from scope. Deferred technical details must have usable bounds for the downstream consumer. The accepted scenario fixes the result, stages, dependencies, creative targets, evidence, cost, and exact stopping condition. Reopen only dependent decisions when new material information changes them.

Read [v4/index](v4/index.md), [systems](v4/systems.md), [systemic design](systemic-design.md), [controls, UX, and commerce](v4/experience-commerce.md), and [persistence](v4/persistence.md) as applicable. The active skill specifies the artifacts and acceptance checks for its route.
