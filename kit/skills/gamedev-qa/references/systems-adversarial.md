# System behavior under failure and edge conditions

## End-to-end UX

Exercise first launch from splash and brand through applicable consent, age checks or permissions, onboarding, control learning, completion of the first attempt, reward and save, and the next goal. Give return, guest and account use, offline, service timeout, missing assets, low storage, corrupt save, suspended or expired accounts, and supported accessibility and localization their own cases.

Compare runtime against the screen and state inventory, including each screen ID, loading, empty, error, disabled, selected, purchased and locked states, navigation, back and deep links, safe area, font scaling, long strings, touch targets and focus. Verify the actual journeys.

## Mechanics, physics, and content

- Input: press, release, cancel and multi-touch, conflicting OS gestures, orientation, low FPS, and backgrounding during held input.
- Physics: maximum speed, corners and stacking, tunneling, simultaneous hit, goal and death, out-of-bounds and stuck states, invalid spawns, tiny and large timestep, unit and scale mismatch.
- Generation: curated normal and boundary seeds, fuzzed seeds, grammar and reachability, hazards and spacing, mandatory resources and checkpoints, load budgets and required routes.
- Variation: classify meaningful encounter and decision changes, repetition window, and difficulty rhythm. Count distinct choices and encounters independently from permutations.
- Recovery: bounded regeneration and fallback, failure, retry and abandon, checkpoint resume, completion and progression after prior failure.

## Progression and economy

Check reachability from new profile to key unlocks, caps, resets and seasons, cycles and softlocks, meaningful mastery gains, free-path time, and fairness within stated assumptions. Simulate no spending, poor RNG, high skill and low time, low skill and high time, collector or endgame, and return after an absence. Compare runtime costs and rewards with authoritative data.

Test precision, rounding, overflow, negative balances, duplicate and concurrent grants, exchange and arbitrage cycles, caps during pending purchases, upgrades changed mid-run, and version mismatch. For paid mechanics, test dominance, counters, sidegrades, readability, rankings and matchmaking as applicable. Model fairness with scoped evidence. For offers, check eligibility, cadence, price freshness, currency, stale and expired states, cancel, failure and back, rewards and odds.

## Store and ads

In sandbox test success, cancel, failure, pending and deferred, duplicate and reordered callbacks, network loss before or after charge, verification, grant or acknowledgement, process restart, two devices, reinstall and restore, refund and revoke, account change, already-owned and unknown SKU, price changes and outages. Include subscription lifecycle when applicable.

Verify one durable grant per authorized transaction. Keep mock and actual provider sandbox evidence separate. Redact purchase tokens and personal data and keep sanitized references. Use an authorized test environment that avoids unexpected live spending.

For rewarded ads cover no-fill, timeout, close before earned, duplicate earned callback, lifecycle changes, denied consent, offline, frequency cap, scene unload and restart before grant. Grant only after the valid earned event and policy. Core free play remains available when ads are disabled.

## Save, offline use, and backend

Test interrupted atomic writes, corrupt and truncated saves, low disk space, unsupported schemas, historical migration, rollback limits, guest-to-account merge, cloud conflict and replay, clock skew, concurrency, stale server reads, idempotency retention, rate limits, retries and cancellation. Verify cascade deletion and local caches separately from logout.

Defensively check tampered client reward, price, time and ID, expired or wrong-account authorization, cross-user access, replayed entitlement, TLS and config, debug endpoints and secrets in logs. Scope security claims to checks actually performed.

## Accessibility and localization

Check color-independent cues, contrast and legibility, touch ergonomics, font scaling and long labels, reduced motion and camera shake, mute and volume controls, captions and visual alternatives, haptics off and supported left- and right-handed controls. Test RTL for supported locales and state supported coverage.

## 4.0 causal fault suite

- For one action through multiple hurtboxes and substeps, check accepted hit count, channels, barriers and parts, and cue deduplication.
- Change source snapshot and live target across DoT tick, expiry and phase. Check exact trace and RNG consumption and ensure resume cannot repeat a tick.
- For simultaneous player and boss lethal outcomes, phase, stagger, objective and kill, verify outcome, reward, save and retry. Cleanup must preserve deduplication.
- When broken support changes topology, navigation, visibility and cover, check fallback, reachability and rescue, and coherent restore.
- For two offline branches spending into crafting, test that max or union merges cannot replenish spent material. Old callbacks and snapshots must respect account and tombstone boundaries.
- Exercise valid-format output with missing layers, rig, stems or ignored parameters. Keep required operations and recipes open.
- Verify semantic validation catches exporter changes in scale, axes, contact markers or loop boundaries before mass production.
- Reconcile unknown jobs against actual job, output and cost before any retry.

Check ordinary combat feedback independently of disk and cloud. Verify critical durable success at its own commit boundary with controlled failures and a separate oracle.
