# Game systems, economy, and persistence

## Canonical executable data

Store stable IDs, schema version, localized labels, dependencies, source decision, expected binding, and fixtures. Keep validated canonical tables in the repository and generate runtime imports. Reference document values to their data source.

| System | Minimum model | Required checks |
|---|---|---|
| Content | Biome, arena, and module IDs, connector grammar, difficulty and hazards, encounter budget, exclusions and unlocks | Reachability, legal combinations, no softlocks, repetition window |
| Run | Phases, choices, rewards, checkpoints, failure and retry and exit, time and seed | Interrupt and abandon, seed replay, terminal state |
| Mastery | Skill opportunities, timing windows, feedback, score | Improvement without forced purchases and no automatic win reward |
| Metagame | Unlocks, cost and prerequisites, caps and resets and prestige, catch-up | Reachability, cycles, and long gaps |
| Mechanic variants | Effects and counters for actors, equipment, and playstyles | Distinct behavior, dominance, synergy and exclusions, readable cues |
| Economy | Precision, sources and sinks and caps, exchange, acquisition time | Conservation, overflow, negative balance, inflation, and free path |
| Offers | SKU and group and type, provider price, eligibility, cadence, contents and refund | Exact grants, expiry and missing offer, clear disclosure |
| Season | Times and timezone, pass and free track, claims and rollover | Offline and skew, season changing during a transaction, missing claims |

Generate with constrained grammar and validated modules. Classify replay by decisions and encounter types. Use curated boundary and adverse seeds, bounded repair and tested safe fallback.

## Actors, equipment, and world

Consume exact IDs in enabled model domains. Define available senses, knowledge and memory, goals, decision and action, cue and commitment and recovery and cooldown, navigation, team role, counters, and limits on adaptation. Randomness respects knowledge and telegraph rules. Verify distinct strategies in context beyond HP and speed. Include opponent AI when the experience calls for it.

The property resolver handles units, typed effects, target scope, evaluation and stacking and refresh, caps, synergy and exclusions, and persistence. Distinguish statistics from changed capabilities and access. Use the game's item, skill, and actor progression model. Keep meaningful parameters connected to decision and feedback.

Implement topology, connectors and gates, materials and interactables, authored or constrained scenarios, risk and reward routes, event pacing, and lasting effects. For revisits, define a voluntary objective, access and chances and restrictions, and useful reward. Test invalid combinations, camera and navigation clearance, softlock, overlapping cues, and repetition. Verify bounded retries lead to a safe fallback.

## Progression, reward, and learning

Derive unlock, capability, and knowledge dependencies from the model. Each meaningful unlock has source and cost, new capability, safe practice, useful combinations, a known context reinterpreted, a next objective, and reset or persistence. Provide finite launch content with a complete loop and long-term trajectory.

Each reward table or pool needs version, trigger and eligibility, exact grant and count and cap, applicable odds and guarantees and pity, duplicates and overflow and revocation, and durable identity. Presentation consumes confirmed state. Connect rewards to actual item or skill use or access or a world change. Keep grants once through time, retry, and scene change.

The learning director uses actual prerequisites, records prompted and independent use, and supports failed attempts, skip and return, and gradual reveal. Verify comprehension and mastery with actual new players for those claims.

## Economy implementation

Track run strength, persistent access, mastery, and collection separately. Record gains and costs as typed events with reason, transaction ID, before and after state, version, precision, and rounding. Every currency needs an identifiable role and usable conversion display. Model the free path, acquisition median and p95 with explicit assumptions, bottlenecks, caps, and refund adjustments. Report model outcomes as simulations.

Simulate never buying, initial purchases only, high skill and little time, low skill and more time, full collections, returning players, and bad random draws. Use playtests for enjoyment and perceived fairness. For mechanically distinct paid content, measure cumulative effects on time, access, and power and communicate trade-offs. P1C allows appropriate advantage within agreed limits. Competitive fairness is specified separately. Test dominance under full portfolio ownership. Carry forward the accepted model and present material changes for decision.

## Purchase and reward state machines

Purchase follows initiated, `store_pending`, `purchased_unverified`, verified, granted, and acknowledged or consumed, with cancelled, failed, refunded, and revoked branches. Use actual SDK and provider ordering. Keep pending separate from success. Persist grant identity using the authoritative purchase or transaction. Handle duplicate callback, retry, and restart without granting twice. Acknowledge or consume after durable fulfillment within the supported deadline. Reconcile in-progress transactions from authoritative records.

A rewarded ad goes from eligible, requested, loaded and shown to verified provider-earned event and durable grant. Cover no-fill, cancellation and error independently. Grant once across suspend and restart. Enforce frequency, consent, and age eligibility and retain the no-ad path.

When selected, test subscription pending, trial, active, renewed, grace and billing retry, hold, pause, cancelled-but-entitled, expired, refund and revoke. Verify authoritative store status, account mapping, restore, and applicable family sharing. Preserve durable rights after reinstall.

For paid randomness, pin pool, version, odds, guarantee, pity, reset, duplicate conversion, disclosure, and actual market and age rules. Record simulations, sandbox transactions, and revenue separately. Disclose changes to odds.

## Save, offline, and sync

Save schema records version, game and content and economy versions, profile, stable item IDs, progression, settings, checkpoint, RNG state and policy, durable transaction journal, pending reconciliation, and integrity or checksum. Use atomic write, backup and recovery. Distinguish corrupt bytes, unsupported version, and absent optional fields.

Verify one-way migrations against historical fixtures. A code rollback and a save rollback need separate compatibility. Allow forward reading where designed or state the rollback limit. Define deletion tombstones and guest-to-account merge. Merge using domain rules to preserve spent currency. Base financial state on authoritative journal and ownership. Use a clear recovery choice with backup when resolving relevant local and cloud conflicts.

Specify which features work offline or require network, how stale data or price displays, and how expiry works when the local clock is untrusted. Prevent replay of daily grants through clock shifts. Bound retries with jitter. Prevent stale commands from modifying the current screen.

## Privacy and telemetry

Specify event ID, schema and build and content versions, consent, minimum fields, retention and deletion. Keep access tokens, raw receipts, email, and full persistent IDs outside QA evidence. Verify age, market, consent, and applicable personal-data requirements for SDKs. Base privacy labels on actual observed data flows.

## Damage, physics, and lifecycle

Separate candidate contacts from accepted hits. Implement T's action/target generation/window deduplication, eligibility, typed channels, addition and multiplication and replacement and conversion and defense order, rounding and caps, barrier and HP and part overflow, positive loss, status and stagger and impulse, and lifecycle priorities. Define damage-over-time capture by input, ticks, expiry, refresh, stack, pause and resume and offline, effect and tick identity, and versioned random streams and roll consumption.

Reflection and retaliation need root and parent and effect identity and bounded cascades. Distinguish cleanup and despawn from kills. A collision can damage a part or disable an actor without death. Resolve concurrent actor and boss death, phase, stagger, goal and rescue independently of iteration order. Keep rewards, costs, retry, and checkpoint in their consistency group.

Use simulation commit for immediate coherent feedback, durable commit for critical reward or spending or victory, and cloud acknowledgment for sync. Ordinary hits proceed without waiting for storage or network. Show critical success only after the correct authority confirms it.

## Full State Catalogue and platform continuation

List each mutable field's type, precision, units, initial value, scope, ownership and authority, lifetime, class (durable, reconstructible, ephemeral, cache, or secret), commit and consistency, restore and migrate and merge and delete, retention and privacy. Preserve or reconstruct significant progression, equipment damage, world flags and AI phases, random states and caps, settings and learning, and pending grants. Reset or rebuild raw touches and runtime pointers safely.

Atomic generations or transactions need ordered revisions, stale-write protection, dirty and checkpoint windows, known-good prior copy, and disk-full, termination, and corruption recovery. Verify envelope, owner, version and migration, semantic invariants, coherent state, reconstructed derived values, and safe controls. Round-trip 64-bit IDs and seeds exactly. Deserialize only supported data.

Keep cloud sync, device backup, account migration, and store restoration separate. Google platform PlayerID and iCloud ownership have different authority from game profile, Game Center, and store accounts. Verify Game Save, PGS and legacy SDK bridges and OS support on the pinned build before changing platform scope. Preserve causality from spend to crafted result across two offline branches and use tombstones for deletions. A paid backend or shared cross-platform profile requires accepted scope.
