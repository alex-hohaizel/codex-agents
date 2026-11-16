# Live operations playbook

## 1. Production authority and telemetry

Reconcile the live store build, client configuration and content manifest, backend deployment, catalogue and economy and save schema, feature-flag cohort, and studio and game identity revisions. Keep the exact production query or export and its timestamp with each finding. Limit personal data in aggregates and classify pseudonymous IDs correctly.

For each event define ID, name and version, occurrence identity, timestamp and clock authority, applicable session and run and pseudonymous player key, platform and build and configuration and experiment, permitted properties and types and units, consent, delivery and retry and deduplication, destination, retention, and deletion. Verify funnel quality against missing and duplicate events, process termination, offline buffering, clock drift, schema drift, and test or bot traffic. Distinguish authoritative purchase state from client interface events.

Collect what the product question needs. Typical sequences cover first launch, tutorial and first meaningful action, start and build choice, death or win or abandonment, reward, unlock, and next run. Commerce includes exposure and decline, store sheet, pending, verified, and refund. Content analysis uses seed and version, obstacle and equipment IDs. Limit raw input and frame logging to a specific need. Use matching symbols and safe context for crashes and errors and exclude tokens and personal text.

Define numerator, denominator, time window and timezone, eligible and excluded users, session boundary, platform and acquisition filters. Label calendar-day or rolling-24-hour retention. Match relevant country, device, channel, and time differences between cohorts and builds.

## 2. Progression and retention diagnosis

Map reasons to return to state, decision, feedback, reward, next opportunity, and expected learning evidence. Applicable reasons include movement mastery, meaningful combinations, completing a run, unlocks and collections and metagame goals, difficulty, social challenges or sharing, and new curated content. Keep assumed appeal open until observed.

For run progression, measure time to a meaningful choice, viable build diversity, completion and abandonment distributions, death cause and readability, resources retained after a failed run, and encounter and route repetition. For metagame progression, measure unlock-time distributions, optional grind, power ceiling, difficulty access, remaining goals, and exhaustion. Inspect whether combinations change the best strategy and remain solvable.

Give each repair a concrete mechanical effect. A new movement action changes obstacle grammar and teaching opportunities, available routes, equipment or scoring choices, production cost, onboarding and UI and audio and haptics, and tests. An arena adds progression when it changes decisions or mastery. Adapt useful functions of other games to the current input and genre.

Collect voluntary feedback within scope. Combine behavior with qualitative evidence and note selection bias in reviews and support. Check frustration, useful stops, and actual return when interpreting long sessions.

## 3. Economy and purchases

Record economy operations in a ledger with source and sink, item or currency, integer amount and balance, reason, transaction or reward identity, and economy and catalogue version. Check conservation, duplicates, negative balance rules, offline merge, restore and refund, inflation, hoarding, and late-game sinks. For simulation, retain seed, cohort assumptions, sensitivity and uncertainty, and output. Track production telemetry separately.

For each offer, define audience eligibility, unlock timing, visible value, store price, purchase type, earned or free path, power bounds, duration and expiry, entry and exit, caps, cancel and pending and failure, restore and refund, telemetry, and operating cost. Show the entire offer and clear actual cost before commitment. Each currency needs a purpose in play.

For characters, weapons, and skills, compare range, aim, movement, timing, counters, skill ceiling, viable builds, nonpaying time and path, and applicable PvP fairness. Use matched mastery and actual bounds to assess paid advantage. If paid randomness is approved, require pool, version, weights, pity, duplicate conversion, guarantees, caps, disclosures, and draw audit. Verify market and age requirements. Track and disclose odds changes under the accepted scope.

Distinguish legitimate refunds and cancellations from fraud. Preserve saves unless an applicable recovery policy states otherwise. Define consumed balances, negative balances and revocation explicitly with user experience and support, then make them deterministic and reconcilable. Distinguish subscription cancellation from actual expiry.

## 4. Content and seasons

For each content release, record manifest version, minimum client and compatibility, dependency hashes, editable sources and runtime exports and provenance, progression placement, difficulty and reward budgets, grammar and constraints, seed suite, novelty and repetition limits, teaching and feedback, UI and localization, sound and music and haptics, and memory and download and performance budgets. Check reachable geometry, collision, fair spawning, item compatibility, escapes, previews, and cue events. Validate generated content against actual grammar and outcomes.

For seasons, define start, end and timezone, eligibility, free and paid tracks, XP sources and caps, completion distribution across cohorts, carryover and grace, post-season rewards, purchase-closing time, offline and clock skew, refund, entitlement retention, old clients, and remote configuration validation. Match release plans to actual authoring and QA time and asset budget.

Maintain accepted masters and tokens, proportions and topology and rig and deformation, lighting and camera and materials, UI parts and fonts and icons and movement, music motif and instruments and stems, and haptic meaning. Compare golden scenes using the same seed, camera, device, and capture setup. A material creative change requires a new accepted baseline.

## 5. Experiments

Start by checking if observational diagnosis or a deterministic regression answers the question. For a controlled experiment, specify hypothesis and mechanism, primary metric, guardrails for crashes and churn and frustration and complaints and purchases and refunds and fairness, eligibility and randomization unit, persistent assignment, exposure logs, duration and sample plan, statistical method, confounders, stop and rollback, ethics and privacy scope, owner, and decision date.

Control changes to build, content and economy. Separate self-selection from causal estimates and follow the planned stopping rule. Check practical effect and harm independently of statistical significance. With low traffic, use uncertainty intervals, qualitative study, or a longer justified observation. Keep segment choices within the agreed product and fairness policy.

## 6. Incidents, patches, and migrations

Record detection and start, scope, affected builds and platforms and regions and cohorts, player impact, timeline and facts, severity and owner, evidence, mitigation scope and authorization, exact actions and provider receipts, actual recovery verification, and follow-up. Preserve evidence before changing state. Verify before irreversible repair. Confirm authority to notify players or other teams.

Triage crashes and ANRs, lost saves, lost or duplicate payments, generator softlocks, performance and thermal problems, ad compliance, privacy, backend health, and costs. Choose a scoped mitigation such as pausing rollout, disabling an exact flag or offer or content item, reverting config, compatible server rollback, safe save repair, or binary roll-forward. Check the store's current ability to roll back. A save or economy migration needs source and destination versions, idempotency, interruption recovery, backup and checksum, old-reader and old-client compatibility, replay and duplicate handling, tested restoration, and rollback or an explicit irreversible boundary. Preserve user progress unless the accepted recovery policy authorizes its change.

For native changes follow build, independent QA, and release. For content-only changes, verify schema, assets, gameplay, economy, and compatibility, then manifest, signature and hashes, staging, and authorized rollout. Carry evidence only over unaffected dependencies. Shared materials, rigs, audio buses, and economy coefficients can affect other acceptance.

## 7. Cost, privacy, and support

Record fixed account or hosting cost, variable requests and storage and egress and analytics and ads tooling, expected usage, free-tier bounds and prices beyond them, alerts and limits, offline fallback, and export path. Verify vendor and generation costs separately from the Codex subscription. New spending, upgrades, scaling, and commercial assets need current authorization.

For data deletion or export, verify identity with minimal information, use the data map and retention policy, and complete relevant steps for backend, analytics, vendors, saves, and linked accounts. Audit completion without retaining extra personal data. Check applicable financial retention. Exercise secrets rotation and revocation, backup restoration, and least privilege when risks require them. Cover actual payment and privacy risks in the affected scope.

Tie support categories to sanitized build, run, transaction, and content IDs. Maintain FAQs and known issues, owner and service expectations, escalation, and recovery. Set recurring automation only with schedule, actual sources, cost cap, notifications, and stopping rule. One ordinary operations request delivers one completed round.

## 8. Output and escalation

Give `liveops-handoff` exact runtime and source versions, queries and exports and windows, metric definitions and quality, findings and hypotheses and confidence, decisions, repair or content or experiment specs, applicable new assets and studio subset, simulations and tests, migrations and rollback, action receipts, support and runbooks, unresolved blockers, owner, and next command. Return affected work to the responsible design, asset, build, or release owner.

Acceptance checks reproducible evidence, observed revenue and retention when claimed, approved style and economy changes, the fair nonpaying baseline, compatibility and transaction integrity, costs, and exact action status. If production data is unavailable, deliver the diagnostic plan and precise blocker.

## Adaptive experience coverage

Compare actual features, domains, dependencies, and scenarios against `assets/liveops-question-catalog.json` before each round. The active scope determines required questions. Record missing telemetry, device, and human proof as unknown or untested, with owner and how to collect it. Use N/A only for a deliberately absent capability. Keep the accepted model and metric dictionary authoritative.

Trace learning prerequisite to teaching opportunity and transfer task, player capability, encounter or route choice, reward or use, and next voluntary goal. Distinguish a hidden unlock from a weak tool, an unread warning from excessive difficulty, and a failed grant from unclear reward presentation.

Measure decision novelty from changed constraints, strategies and opportunities, trade-offs in the previously dominant simple approach, how players learn new choices, and production cost. Record exhaustion of finite launch content and what remains after mastery. For a new actor, content item, or boost, follow actual impact on learning, camera and input, encounters and world, rewards and progression, and commerce and saves and analytics. Reopen affected work only.

## Follow causes through the released build

Recover the exact released build, configuration, content, save and experiment state, and matching symbols. Check actual observability and service health. For damage, AI, and failures, examine context, actor knowledge, input, contact, capture, resources, lifecycle, rewards, saves, and return. Relate progression and variation to capability, opportunity and exposure and exhaustion. Measure the agreed power, time, and access bounds for a paid portfolio.

A changed recipe, tool, importer, or configuration invalidates dependent operation witnesses and derivatives. Record attempt, job and outcome, cost, and reconciliation. Verify affected semantic transformations, cold start, transition memory, assembled gameplay, and signed adapter regression. Preserve compatibility, content epoch, patch base, golden saves, and deletion tombstones in patches and offboarding.

Close one bounded round with actual findings, actions and receipts, limitations, and the next instruction and checkpoint. Claim ongoing monitoring only when the service or automation exists and is active. Reconcile current state on the next request.
