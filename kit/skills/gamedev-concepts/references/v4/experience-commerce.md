# Player intent, touch, camera, experience, feedback, and metagame 4.0

Use this contract for concepts, interaction and state presentation, onboarding, rewards, commerce, and player return. Select controls, HUD, systems, and offers that serve the game. Verify them together in demanding play.

## 1. Cover the complete player journey

Create a state atlas covering launch and first use, applicable consent, profile and save loading and recovery, settings, onboarding and practice, gameplay, pause and interruption, failure and retry and abandonment, rewards and equipment and upgrades, progression and navigation, conditional shopping and purchase and sync, return and reorientation, completion, and support. For each state, define entry, exit, guards, permitted input, effects, commitments, failures, timeouts, save behavior, and return target.

For short, normal, and long sessions, define the smallest meaningful action, safe pause or exit, and continuation. Preserve the appropriate state through interruptions. After a real break, recover the goal, loadout, context, and important changes without repeating the tutorial. In exploratory play, give hints that respect discovery (D1Q08,Q15).

For an action, craft, respec, route, story choice, or purchase, distinguish preview, commitment, application, irreversible boundary, and recovery. Define cancellation before and after commitment. Add confirmation where its consequence warrants it.

## 2. Separate intent, action, recognition, and presentation

| Model | Required content |
|---|---|
| Intent | Desired immediate action, such as move, aim, guard, choose, or cancel |
| Game action | Eligibility, state, cost, commitment, timing, and outcome |
| Recognition | Pointer ownership, zones, gestures, thresholds, state, competing recognizers, and cancellation |
| Presentation | Persistent or temporary cue, affordance, preview, feedback, and the visible invitation to act |

Compare applicable input schemes on first use, a simultaneous peak, and a demanding late situation. Ground direct dynamic control in the accepted scope. If required, preserve its immediate interactive qualities in the runtime result.

The input contract defines supported device, orientation, grip and handedness, safe areas and edge gestures, simultaneous contacts, stable pointer IDs, ownership acquisition and release, zone capture, physical and logical threshold units, deadzone, curve and hysteresis, sensitivity, tap and hold and drag and swipe recognition, competition and priority, preview and commit and cancel, buffering, remapping, exit zones, reordered pointers, focus loss, modal handoff, pause and resume, persisted settings, and traces.

Define ownership for UI hit testing and gameplay contacts. The touch that opens a shop cannot trigger an offer inside it. A system cancel releases any throttle or held action. Losing one of two fingers must respect the steering owner's identity. Verify any pressure requirements on target devices.

For an analog drag, define fixed or floating origin, deadzone, normalization, transfer curve, maximum, recenter and release, and finger occlusion. A continuous drag needs an affordance distinct from two buttons. For complex weapon interaction, separate preview, commitment, contact, and cancellation so adjusting guard or completing a prior gesture does not trigger a new attack.

### Camera request policy

Define projection and angle and follow behavior, subject scale, visible action horizon, deadzone and lookahead and zoom bounds, occlusion and collision, motion and acceleration limits, zones and transitions and cuts, aim and interaction and boss requests, owner and priority and tie-break, blend and release and return, hysteresis, and accessible comfort options.

Derive on-screen character scale from mechanics, readability, and style. Show camera motion, scene transition, and routing at concept. Resolve concurrent requests deterministically, including what happens to touch direction.

Record tick, input, recognizer state, intent, action, camera request, owner, transform, and cue. On actual targets, measure input through recognition, simulation, rendering and presentation, and screen response. Track frame rate, latency, and tactile comfort independently.

## 3. Design learning, feedback, and accessibility

For each mechanic, map discovery, comprehension, execution, observed result, safe practice, transfer, combination, and later reinterpretation. Identify what the player knows, cues and affordances, goal, opportunity, proof of mastery, retry and remediation, and skip and relearn paths. Provide interactive practice where practice is needed.

Distinguish missed opportunity, misunderstood rule, unknown input, recognition defect, timing error, and deliberate experiment. A valid alternative can demonstrate understanding. Base remediation on observed interaction and keep personal profiling outside the task (D1Q07,Q10).

Connect failure feedback to available information and responses before the event, actual action, cause and outcome, what was lost or retained, and the next meaningful step. Distinguish lack of knowledge or execution from a technical defect. Report the actual rejection reason, such as range, for a missed hit.

### Multimodal cues and attention

Define each cue's semantic meaning, invariant visual and auditory and haptic signals, allowed stylistic variation, forbidden ambiguities, novice and late examples, and alternative channels. When a new environment changes a learned cue's meaning, teach the new behavior. Distinct concepts need a coherent visual language beyond color choice.

For each event and state, link ID and predicate to animation, VFX, UI, sound, and haptics, with priority, timebase, deduplication key, duration and start/update/end, origin and position and intensity, suppression or aggregation or deferral, stale expiry, and alternatives. Aggregate contact feedback over the relevant manifold. Bind hit cues to simulation and durable reward cues to the corresponding committed effect.

Define concurrency, precedence for critical cues, ducking, limits for clutter, flash and motion, and fallback. Test concurrent danger, goal, reward, and critical resources on the weakest target with finger occlusion and muted or haptic-free alternatives. Expire deferred cues before they imply a new threat (D1Q03,Q11,Q13).

### Style, assets, and localization

At C1, define silhouette, proportions and scale, palette and contrast, material and texture, edge and lighting language, composition, characters and equipment, UI and effects, motion timing and camera relation, sound palette and motifs, mix, and feedback. Establish a feasible 2D or 3D pipeline and target fidelity. Verify editable layers, rig, native performance, and production sources separately from concept art.

At T, map every important state and transition to assets, sound, and haptics, exact markers and timebase, collision and pivot and attachment, import and export, budget, and test scene. Choose representation for health, heat, guard, and durability based on decision frequency, urgency, and precision. Use a simple counter where it serves that decision.

Localization defines stable string IDs, context and speaker, placeholder types, plurals and selects, glossary, numbers and units and currency and price formatting, font coverage and licensing and fallback and shaping, scaling, subtitles, and applicable RTL. Keep save IDs and formulas independent of text. Verify that long localized text leaves price and cancel visible. Validate supported scripts in addition to pseudolocalization (D1Q12).

### Assist semantics

Alternatives to complex gestures and sustained holds, zones and sensitivity and handedness, and vibration, sound, motion, and text options preserve meaningful actions. Keep settings reachable without the action being remapped. Offer more than one channel for required information.

For each assist, specify intervention, decisions retained or changed, effects on rules, time or resources, switching and saving, compatibility, and scoring or competition scope. Any reward consequence requires an explicit design rule and advance disclosure. Toggling an assist preserves spent and claimed state (D1Q06).

## 4. Design commerce with the metagame

Start from player needs and loops. Compare applicable premium and full unlock, content and expansion, cosmetic identity, ready functional sets, capacity and convenience, membership and ongoing services, capped opportunities or rewarded ads, deterministic currencies, and seasonal structures. Derive offers separately for each concept.

Functional paid sets may give time, option, or power advantages where appropriate. Quantify and bound those effects and consider competition separately. Default to deterministic purchases and transparent earned randomness. Paid randomness requires an explicit decision. Exclude hidden success- or purchase-based difficulty adaptation from defaults. Add networks, backend, and recurring cost only under the accepted project decision.

### Compare paid and earned paths

For each offer, define target need and metaloop, components and compatibility, usable result, earned routes, distributions of time and resource and risk, prerequisites, difference in power, options and time, restrictions, caps and expiry, partial ownership, duplicate behavior and overflow, upgrades and respec, recovery, and content lifetime.

A ready kit can complete something a player could assemble gradually from earned parts. Check the full paid portfolio for combined effects that remove intended weaknesses. Assess actual situational interactions as well as individual item attributes.

For opportunity or attempt boosters, define caps, refresh and calendar, earned and purchased limits, stacking, duration, timezone and offline behavior, failed runs, ad no-fill, and unspent value. Use actual finite limits. For membership expiry, define access, read and use, and overflow while preserving inventory.

Define economy sources and sinks, currencies and units, authority, caps and inflation, production, repair and transfer, rewards, duplicates and pity, baseline cohorts and strategies, early and late and completion states, time-to-goal distributions and tails, sensitivity, and exploit cycles. Simulations establish scenario results. Check current store policy, markets, and age requirements before release.

### Shop and payment journey

Cover discovery, clear preview and result, localized store price, eligibility and ownership, confirmation and platform UI, pending, verified success, idempotent grant, durable record, provider acknowledgment or finish, and reconciliation. Use the exact ordering required by the supported SDK and platform.

Exercise loading, empty, offline, unavailable, parental decline, cancellation, deferred, pending, unknown outcome, failed, granted, already owned, partial bundle, refund, revocation, restoration, account switch, and repeated callbacks. Show success only after the applicable authoritative durable result. Exclude tokens from public logs and use authoritative verified ownership.

Define canonical product and offer IDs, store mappings, country and currency and price source, validation authority, operation and grant deduplication keys, consumable and non-consumable and lease behavior, partial-set price and compensation, refunds, offline projections, rollback and migration, and support evidence. Track local economy and real-money transactions with distinct authority.

Define store purchase restoration separately from cloud save restoration. An old snapshot cannot grant consumed goods again or restore refunded access through a merge. Set deadlines, bounded backoff, cancellation, reconciliation, and fallback so no-fill, cloud service failure, or store timeout preserves local play (D1Q34).

### Conditional shared play and sharing

For accepted co-op or competition, specify lobby, join, leave, disconnect and rejoin, authority, participant ownership, input and latency bounds, shared and individual progress and rewards, pause, assist, scoring, and conflict recovery. Validate an actual multiplayer protocol. Add a server only for supported scope (D1Q17).

For accepted sharing or user-generated content, define capture and export contents, rights, privacy and hidden in-game knowledge, naming and locale, size and format and compatibility, cancellation, safe import, and the user's publishing intent. Keep private account data and payment tokens out of exports. Confirm authority for each external action (D1Q18).

## 5. Acceptance

A consumer reproduces first use, peak play, late play, return, completion, failed input and cancellation, failure and recovery, and conditional purchase from the specification. Verify the sequence from model through visible invitation to actual action. A continuous drag must be recognizably continuous. Keep tap, hold, and swipe behavior consistent with documented state changes.

Negative fixtures include reordered pointers, edge gesture and system cancel and focus loss, a stale touch entering the modal shop, simultaneous aim and boss and zone camera requests, guard correction interpreted as attack, inaccessible settings, a blocked critical cue, wrong tutorial remediation, long localized price and cancel label, a reward for a complete collection, paid portfolio dominance, pending timeout and repeated grant, and partial bundle with refund and an older cloud save.

Record actual human task, device and profile, participant scope, errors, occlusion, fatigue, comprehension, and limitations. Track written review, input traces, physical comfort, native execution, store sandbox, configured analytics, observed egress, and observed revenue separately.

## Primary sources

These methods adapt P1/D1/D2 sources researched on 2026-11-02. Verify current policy, SDK, price, and capabilities for the actual target at the time of use.

- Android multitouch and stable pointer IDs. https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi
- Microsoft XAG107 input. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
- Microsoft XAG108 difficulty. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/108
- Microsoft XAG103 alternative channels. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103
- Android localization. https://developer.android.com/guide/topics/resources/localization
- Warframe Prime Access as an example of a ready functional set. https://support.warframe.com/hc/en-us/articles/200092159-Prime-Access-FAQ
- ESO Plus as a membership benefit lifecycle example. https://help.elderscrollsonline.com/app/answers/detail/a_id/26343/kw/plus
- Steam bundles as a partial-ownership example. https://partner.steamgames.com/doc/store/application/bundles
- Play Billing lifecycle. https://developer.android.com/google/play/billing/lifecycle
- Apple StoreKit transactions. https://developer.apple.com/documentation/storekit/transaction
