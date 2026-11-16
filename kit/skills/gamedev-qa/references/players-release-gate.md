# Playtesting and release decisions

## Evidence from people

Use actual human observations for enjoyment and feel, control comprehension, meaningful variation, desire for another attempt, sustained motivation, audio and haptic comfort, and perceived fairness. AI and code or model review can identify logical risks and help design the test. Track execution with real players separately.

## Playtest protocol

Write the research question and falsifiable criteria in advance. Select relevant audience, access needs, and devices, and record actual recruitment and consent. Give participants the raw game and task without promotional framing about the expected reaction. Avoid first-use coaching unless specified in the protocol. Collect only necessary personal data.

Examples include a new player independently understanding the goal, controls and failure and finding a retry or next objective, a player who can describe new decision trade-offs across runs, a player who understands a loss and finds a free improvement path, participants who see clear trade-offs in a paid mechanical variant and encounter no concealed barriers along the free path, and a returning player finding a new objective without losing progress or context.

Record actual sample size, recruitment bias, duration, build and device, task, observations and timecodes, quotes with consent, drop-off and assistance, conclusions, and limitations. A small formative study can expose usability problems. Market D7 or LTV requires separate evidence. A longitudinal test needs actual return visits at the specified times. Record stated intent to return separately from measured retention.

## Monetization and fairness

Simulation estimates acquisition time, price, and rewards under stated assumptions. Human tests show comprehension, pressure, and perceived fairness. A live cohort measures actual conversion, refunds, revenue, and retention. Preserve the evidence level for each finding. Report negative responses accurately and send the underlying mechanism issue to its design owner.

## Full-stage verdict

Agree the exact product scope and platforms. Each must has a current verdict and evidence or an explicit blocker. Acceptance requires independent review where applicable, native platform checks, fidelity and craft review, data, commerce, and privacy checks, required human evidence, and closure of release blockers. A named beta may test open hypotheses. Establish any market result from actual market evidence.

- `accepted_for_named_test` authorizes the named test or beta objective within the existing scope. Remaining hypotheses stay open.
- `accepted_for_release_review` passes the technical and product gates for the named scope. `gamedev-release` verifies actual store setup and submission requirements.
- `blocked` identifies missing required evidence, defects, rights, signing, or platform coverage.
- `scoped_complete` completes the named local check.

After closing the named scope, reopen only for a new change, evidence, dependency, or invalidated prior claim. Record any unknowns the owner accepts for the specific beta. Full release readiness requires its own evidence.

## Handoff to release

Include exact accepted source and build, sanitized evidence manifest, requirements matrix, per-platform status, known defects, store policy snapshot, rights and brand package, privacy and data map, store SKU and contracts, migrations and rollback, test access, and next action. Confirm current authorization for production publication separately from the QA verdict.

## Learning transfer and variation

For each material skill the game teaches, define teaching, practice, and transfer tasks. Transfer uses the same causal rule in a new context without repeating instruction when that is the intended design. Record actual success, errors, help, time, and the player's explanation. Route failed transfer to the onboarding or readability owner and record tutorial completion separately. Set thresholds in advance from the risk and audience.

For variation, choose contexts with different constraints and observe actual choices, counters, and trade-offs. Avoid steering toward a preferred build. Separate awareness and availability of an option from its strength. For voluntary return, present visible goals, record the actual choice, and observe later visits using a longitudinal protocol. Record any visits that were not observed.

## Failure, reorientation, and assists

Observe whether participants can distinguish a rule they understood, an available counter, a recognition defect, and an execution mistake. Failure causes and recovery should give them a meaningful next step. After a real break, test whether they recover their goal, context, and loadout without replaying the whole tutorial.

Define assist behavior, scoring, persistence, and compatibility. Any change to rewards requires an explicit design rule. Paying and free participants assess the accepted power, time, and access policy. Document allowed advantages and test the free baseline for hidden harm.
