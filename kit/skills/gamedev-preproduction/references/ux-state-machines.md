# Screen states and interaction contracts

## Reachable experience inventory

List applicable boot and splash, loading and update, first use, consent and permissions, account and guest upgrade and unlink or delete, hub, profile and settings and accessibility, controls and tutorial and practice, loadout and collection and upgrades, shop and offers and pass and events, level and run selection, gameplay HUD, pause, disconnect and reconnect, win and fail and reward and retry, progression and unlock, leaderboards and social, credits and support and privacy, errors and maintenance, suspend and resume and quit and return. Give a reason for intentionally absent branches.

For every screen, overlay and visible state, specify:

- Stable ID, purpose, guards, source of truth, empty, loading, populated, error, offline, locked, disabled, selected, and focused states.
- Exact text and assets, data IDs, hierarchy, actions, back and escape and system gestures, validation, and feedback.
- Coordinates, anchors, constraints, safe areas and cutouts and keyboard, aspect and type-scale ranges, locale expansion and RTL where supported.
- Input and ownership, hit areas, focus and order, duplicate protection, cancellation, retries, and idempotency.
- Motion timing, easing, duration, interruption, and reduced motion.
- Audio and haptic cue IDs, concurrency and priority, mute, reduction and haptic settings.
- Transitions and effects, persistence, permission and payment boundary, recovery and acceptance.

## Transition record

`from_state + event + guard → side effects + next state + feedback + persistence + recovery`.

Specify success and failure. For a purchase or upgrade, insufficient earned currency shows the deficit and earned path, pending prevents duplicates, success binds wallet and item revision and feedback, timeout triggers reconciliation, return after termination shows actual results once, and refund or revoke reconciles inventory. A UI animation consumes the authoritative result.

## Input and gameplay boundaries

Keep touch areas clear of edges, HUD, dominant thumb and camera controls. Define arbitration for tap, hold, drag, swipe and simultaneous contacts, thresholds and units, deadzones and sensitivity, applicable input buffers and coyote time, release and cancellation and pause. Align movement, jump and aim with motion and physics. Give meaningful invalid-action feedback without clutter.

Offer applicable music, effects and voice controls, mute, haptic levels and off, reduced effects and motion, color accessibility, language, inputs, and privacy and account controls. Respect background and audio focus behavior. Use alternative channels for essential information and check real target-size readability.

## Coverage

Derive a directed graph from actual data. Check unreachable states, missing transitions and exits, unsafe back behavior, duplicate purchase and claim, and unresolved modal stacks. Trace each screen entry and system lifecycle transition. Cover reachable high-risk money, save, authentication, deletion and consent transitions and injection of failures. Select other combinations by risk and show limits.

Use high-fidelity targets for every screen family and material state, including errors, commerce, loading, and late play. Reuse components with mappings and explicit exceptions. Track wireframe and visual acceptance separately. Check hierarchy and action affordances on narrow devices and with long translations.

## Camera and learning

Distinguish presentation framing from gameplay framing. Each camera state has subject-size bounds, visibility and reaction, tracking and lookahead and zoom and damping, offscreen threats and occlusion and transitions. Use a fixed or moving camera based on the mechanics and preserve playable action scale.

Model learning as a skill dependency graph. Define prior knowledge, natural trigger, concise cue, practice, meaningful application, combination, and independent transfer, with skip, repeat, return, and help after failure. Introduce UI, resources, and commerce when relevant. Observe independent action. Investigate recognition and camera causes when a gesture fails.

## Intent, commitment, and persistence

Keep intent, action, input, and presentation separate. Trace stable pointer ownership, thresholds and units and hysteresis, preview and commit and cancel and refund, system gestures and capture and modality, and pause and resume. Resolve camera ownership, priority, release and return without oscillation. Define cue aggregation, deferral, suppression, and mixing.

For back and exit, crafting, story, respec, and route decisions, state irreversible boundary and recovery. Diagnose unseen affordance, unknown rule or gesture, recognizer defect, timing error, and intentional experiment separately. Recover a meaningful goal and context on return without forced spoilers. Localization covers stable strings, context, plural rules, placeholders, terminology, units, price, script, fonts, and relevant RTL.

Distinguish local saved, cloud pending, synced, conflict, and error. Immediate ordinary combat cues run independently of storage and network. Critical success appears only after the appropriate durable and verified result.
