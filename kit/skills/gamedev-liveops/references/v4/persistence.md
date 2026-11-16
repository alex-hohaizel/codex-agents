# Complete state, save, resume and cloud 4.0

## Navigation

1. State catalog
2. Simulation and durable commit
3. Restore and migration
4. Cloud, identity and conflicts
5. Time, RNG, purchase and deletion
6. Failure suite and sources

Use for every game and any state change. Persist or reconstruct all state meaningful to the player. Give temporary particles, pointers and physics frames an explicit reset or reconstruction policy. An uncovered field remains a gap.

## 1. Build the State Catalogue

Derive mutable fields from active systems, reachable transitions and adapters. For each record ID, system and owner, type, units, precision and bounds, initial state and meaning, lifetime, profile, device, run or account scope, authority and mutation sources, persistence class, commit trigger, consistency group, restore order, reconstruction, schema and content version, merge, migration, deletion, retention and privacy, and fixtures.

| Class | Policy | Example |
|---|---|---|
| Durable | Persist reliably at the defined boundary | Unlock, inventory instance, spent resource, granted reward |
| Reconstructible | Keep canonical inputs and reconstruct by version | Derived stats, path or plan, UI projection |
| Ephemeral | Reset or transition safely | Finger contact, held accelerator, particles |
| Cache | Discard and obtain or build again | Downloaded derivative, thumbnails |
| Secret | Use suitable separate storage | Credential, token, key |

Check profile, mastery and collection, inventory, loadout, durability and craft, currency, grants, pity and limits, world, quests, NPCs, doors and destruction, run, position, objectives, resources and effects, AI, bosses and encounters, generation and accepted results, metagame clocks, purchase projections, tutorial, goal and context, settings, layout and accessibility, UGC and replays when present, and derived and temporary state.

Specify exact logical snapshot or an agreed checkpoint with bounded progress loss. Make any loss of meaningful progress explicit. Pause or system interruption is abandonment only under an accepted product rule. Design the returning player's goal, equipment and change context separately from byte restoration.

## 2. Separate the commit boundaries

**Simulation commit** applies the outcome atomically to the authoritative gameplay model. Hit, UI, VFX, SFX and haptics respond immediately and independently of disk flush or cloud acknowledgement. **Durable commit** records important causal changes under the adapter's guarantee. Confirm critical reward, spend and victory at their due durable boundary. Cloud acknowledgement is a third distinct state.

Record command and operation ID, validated outcome, consistency group, snapshot or event transaction, new generation, write and check, durable adapter acknowledgement, confirmed revision and cloud queue. Use a bounded dirty or checkpoint window and a write budget for frequent noncritical state.

A logical writer queue uses sequence or revision, backpressure or coalescing, and protection from late saves replacing newer ones. Commit spending, crafted item and claim flag as a consistent outcome. Process failure at any point must restore a valid causal result.

Choose two generations or a previous-good snapshot, or a transactional database according to complexity. Verify `tmp+rename` durability on the actual OS, filesystem and API. For SQLite record journal and synchronous assumptions and supported snapshot export. Copying only the main file of an active WAL database can lose current state.

Disk full, serialization, I/O and permission failures keep previous-good intact and must not show Saved. Lifecycle callbacks provide another flush opportunity. Termination may bypass them. Preserve progress outside disposable cache or temporary paths.

A consistency group lists causal command IDs, member fields, valid commits, rollback and retry, and reconciliation. If 6 earned parts are spent to make a claimed kit, a merge cannot keep both the kit and the same 6 unspent parts.

## 3. Specify the envelope and restore

An envelope records save and profile IDs, schema and build compatibility, content, catalog, economy and generator versions, revision, generation and parent ancestry as applicable, committed marker, logical position, RNG contracts, payload length and checksum, and referenced modules. Timestamp can aid explanation. Use ancestry or a domain policy as conflict authority.

Restore pipeline:

1. Bound size, depth and types and parse data without constructing objects, running code or loading arbitrary resources.
2. Validate envelope and integrity, owner and profile scope, and supported schema, content and build.
3. Preserve the original and apply a known migration. Return an understandable error for an unsupported newer schema.
4. Verify unique instance IDs, balances, prerequisites, causal grants and quest state, and valid references.
5. Apply the consistent logical state atomically.
6. Restore world, topology, entities, resources and AI in dependency order, and rebuild derived caches.
7. Reconcile entitlements and pending operations with the actual authority. Preserve accepted random results.
8. Restore camera, presentation and goal with neutral input before enabling controls.

Integrity, authenticity, atomicity and semantic validity each require appropriate evidence. Keep cloud and imported saves data-only. Exclude credentials from reproductions and exports.

Migrations cover schema, content IDs, catalog and economy, generators, removed DLC and modules, and stable identity. Define compensation or retention for deletion and remap where applicable. Golden saves for supported transitions open with the expected result. Treat binary rollback and migrated save rollback separately, and specify downversion compatibility.

## 4. Design cloud as an adapter

The offline core works locally. Offer progress protection and transfer contextually and in settings. Keep cloud opt-in and management distinct from automatic platform authentication. An SDK may provide system UI. Expose only controls supported by the actual API.

Distinguish game profile or guest, platform player, in-game account, cloud owner, store account and device. On account switch prevent old data from reaching the new owner. Verify operation, profile, session and revision on callbacks before applying them.

Show local saved, pending or offline, syncing, confirmed cloud revision, conflict, quota, authentication or error according to actual state. Show synced after remote acknowledgement. Treat timeout as unknown and bound reconciliation and retries. Prevent duplicate uploads and grants.

### Choose a route for the supported OS

Google PGS Saved Games or Snapshots requires integration and console enablement plus application schema, identity, conflict and quota handling. PGS v2 platform ID is separate from game accounts. Android Auto Backup is an OS backup with its own contract. As researched on 2026-11-02, Saved Games limits were 3MB for a blob and 800KB for cover, and Auto Backup 25MB. Verify current limits before binding the project.

Apple GameSave was available from iOS and iPadOS 26 at the research date. Preserve the accepted minimum OS and evaluate GameKit, GKSavedGame or a compatible adapter for earlier supported versions. Keep Game Center identity and iCloud ownership distinct. Verify actual save API coverage of the native plugin.

Record pinned SDK, plugin, OS and export versions, entitlement, capability and signing setup, callbacks, threading and lifecycle, local, offline and online behavior, conflicts, account switch and cold restore. Cloud needs actual integration and proof beyond store publication. Cross-platform Android and iOS profiles need deliberate identity, storage, authority and cost decisions.

### Reconcile causal branches

Detect divergence through revision ancestry or the platform conflict API. Define a whole consistent branch selection or a domain-specific merge. Check timestamps, maximum or summed balances and inventory union against the actual consistency rules before using them.

Safe independent monotonic unlocks can sometimes be united. Spending, crafting, purchase grants, mutually exclusive quests and active boss state need causal consistency. An event log cannot authorize two offline spends of one resource. For a complex offline economy use an authority, reservation, constrained offline scope or valid branch choice.

Preserve both originals until conflict resolution. Show the contents, progress and consequences of both branches in the UI. Recompute thumb zones for the new device rather than storing aspect-specific layout as an account invariant.

## 5. Time, RNG, purchase and deletion

Distinguish simulation time, active time, elapsed real time and calendar UTC. A monotonic session clock does not provide a continuous timestamp across reboot. Specify anchor, cap, accepted claim IDs, time zone, forward and backward jumps for offline production and rewards. Ground date assurance in an independent authority if the local clock can be altered.

Preserve RNG stream, algorithm, version and state or counter key, accepted choices and pity state. Encode large 64-bit seeds, IDs and counters exactly and test round trips. Godot JSON numeric float conversion can lose integer precision. Use generator version alongside seed to preserve the same world.

Cloud progress, OS backup, transfer and purchase restore have separate authority. Local entitlement projects store or server state. Reconcile missed callbacks, offline state and another device, and keep idempotent grant and consume records. A previous backup cannot restore refunded access or regrant a consumable.

Distinguish run reset, local copy removal, disabling sync, unlinking and profile deletion. Use deletion or tombstone retention to prevent an old offline client from reviving data. Where service loss or offboarding applies, define access, progress, purchases, export and support based on actual commitments.

Verify uninstall and device-loss recovery only when cloud or backup support exists. When cloud is enabled, exercise a cold restore on another actual device. Keep secrets and private saves out of public support capsules. Measure data egress for consent, offline and cloud states.

## 6. Required failure suite

- Terminate before and after the critical command, serialization, write, durable acknowledgement and UI confirmation.
- Boss death, reward, quest flag and pause restore as one causal outcome.
- Disk full, truncated or corrupt input or newer save preserves previous-good.
- An asynchronous revision N write completes after N+1 and cannot replace the newer revision.
- Two offline branches spend the same parts. Restore must not grant a kit plus returned materials.
- Account switch, guest with existing cloud data and late callback must preserve profile isolation.
- Quota, lost network and unknown upload preserve local play and use bounded reconciliation.
- Round-trip maximum IDs and seeds. Restored RNG yields the next sample and preserves accepted grants.
- Current boss, damage over time or checkpoint restore avoids repeated ticks and rewards or uncued attacks.
- Refund, consumed item and restore reconcile rights without trusting old JSON.
- Profile deletion and an old offline device cannot recreate deleted state.
- Exercise cold reinstall restore using the actual platform adapter and a supported older version.

Retain failure logs, fixtures, expected outcomes, exact adapter, build and profile bindings, and known limits. Evidence for durability, cloud behavior and devices requires corresponding execution.

## Primary sources

Reviewed on 2026-11-02. Check current docs and actual export when selecting the SDK and OS.

- SQLite atomic commit: https://www.sqlite.org/atomiccommit.html
- SQLite WAL: https://www.sqlite.org/wal.html
- SQLite online backup: https://www.sqlite.org/backup.html
- Android process lifecycle: https://developer.android.com/guide/components/activities/process-lifecycle
- PGS Saved Games: https://developers.google.com/games/services/common/concepts/savedgames
- PGS v2 identity: https://developer.android.com/games/pgs/android/android-signin
- Android Auto Backup: https://developer.android.com/identity/data/autobackup
- Apple GameSave: https://developer.apple.com/documentation/gamesave
- Apple GKSavedGame: https://developer.apple.com/documentation/gamekit/gksavedgame
- Godot JSON: https://docs.godotengine.org/en/stable/classes/class_json.html
- Godot Variant deserialization warnings: https://docs.godotengine.org/en/stable/classes/class_%40globalscope.html
- Play Billing lifecycle: https://developer.android.com/google/play/billing/lifecycle
