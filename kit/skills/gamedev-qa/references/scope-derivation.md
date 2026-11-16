# Derive the required QA scope

Use this procedure to derive scope and cases from authoritative sources and the due gate. Files under `assets` supply test plans. Actual results have separate evidence.

## Sources and priority

1. Read current owner requirements and decisions, the accepted target, current model maturity (C0/C1/T), actual content and runtime inventory, and dependency impact. Reconcile against the original requirements.
2. Compare `features[domain].enabled/rationale`, `domains`, scenarios, and runtime behavior. A disabled flag for an implemented purchase or enemy signals a conflict. Repair the model or implementation, or obtain a material scope decision.
3. Carry forward requirements and scheduled proofs from the shared model. Include applicable journeys beyond a single screen, such as menus and loading, learning and transfer, play and failure and retry, rewards and inventory and upgrades, shop and purchases, returning and exhaustion, and settings, account, or support.
4. Determine affected systems and transitive dependencies. Investigate unknown impact and expand scope where necessary. Money, privacy, authentication, data loss, and release changes are critical even in a small diff.

## Select cases

Choose applicable patterns from `assets/qa-case-catalog.json` and connect them to actual requirement, rule, and scenario IDs. Bind generic preconditions to concrete states and data. Add feature-specific boundaries, fault and recovery paths, and historical defects outside the catalogue.

The required scope follows actual capability, the due gate, and material claims. Optional flags may add checks. Each required type of proof and independent review remains due. Mark N/A with the accepted rule that excludes a feature, such as a game intentionally excluding purchases or enemies. Missing tools or access remain blockers. A game without enemies may still require readable hazards and failure.

## Evidence due at each gate

| Gate | Minimum suitable evidence for the named scope |
|---|---|
| concept | Label C0 as a sketch. Each completed C1 candidate covers the applicable 20 areas, mechanic, world, progression, risk, and commerce architecture, the full concept handoff, and scenarios that change decisions. Include independent semantic review, a feasibility profile, and inspection before showing images. Reserve native, enjoyment, and retention claims for their actual evidence. |
| preproduction | Complete T rules, state, data, journey, launch catalogue or grammar, StateCatalogue, production recipes, semantic dependencies, and receiver intake. Verify reachability, budgets and limits, economy assumptions, computable properties and invariants, and the test plan with independent oracles. |
| slice | Actual engine or runtime trace for representative systems and their intersections. Verify source-to-runtime visuals, motion, and audio, and use physical devices for claimed touch, thermal, and haptic behavior. Include sandbox commerce in scope when applicable. Carry forward excluded features as future obligations. |
| beta | Verify the actual beta build, agreed journeys and recovery, and platform checks. Observe human first use, learning transfer, and play. A longitudinal claim requires actual repeat visits. |
| release | Cover the full launch scope and named platform matrix, critical journeys, final assets and configuration, installation and updates and saves, sustained device performance, real store sandbox and ad error behavior, policy, rights, and privacy. Match required human observations to product claims. Market success has a separate evidence base. |

For live operations, distinguish actual cohorts from beta, simulations, and internal tests. With unavailable production data, supply a diagnosis and measurement plan. Use canonical evidence fields and types from `model-format.md`.

## Specify a case

Record case ID, source requirement and rule IDs, model/artifact/build hashes, domain and feature and applicability trigger, due gate, precise preconditions and state and seed, action and procedure, expected observation and independent oracle, changed decision and counterexample where relevant, boundary or fault, required evidence types, actual result and status, raw proof references, observer, author, reviewer, limits, and owner.

A scenario inherited from the model has `id,domains,initial_state,action,expected_observable,changed_decision,without_rule`. Keep those fields and attach execution details in the QA packet. Create canonical `evidence` after execution, storage of raw proof, and an evidence record with checksum and provenance. Use distinct case and evidence IDs.

Derive expectations from an accepted rule or table, an official platform contract, or an independently derived invariant. Avoid copying the implementation formula as the oracle. Set observable acceptance and procedure for UX and craft in advance.

## Assess coverage

Record the denominator and actual tested and untested cases for journeys and transitions, rule families, enemy and encounter families, item and ability interactions, content phases, offers, and platforms in scope. Check completeness of the inventory before claiming full coverage.

Compare the strongest simple policy in different contexts, removing a rule or resource, revisiting a task after an unlock, early/mid/late contexts, baseline and alternative and full paid portfolio, and no offer. Record which decisions changed and why. Seeds, recolors, health inflation, and additional controls need observable decision differences to establish variety.

Use risk-based pairwise testing, known critical interactions across three or more factors, boundary and recovery behavior, curated seeds, and property and fuzz tests when a meaningful oracle exists. Review complex systems directly and choose combinations from known risks.

## Close the scope

Use structural validators for references and byte integrity. An independent reviewer checks raw evidence against the expected rule and scoped coverage. Mark missing evidence `not_tested` or `blocked`. Record actual actors. Resolve an open must by repair, a named test scope, or an explicit decision under the relevant authority. State the exact boundary of the next gate. Assess product readiness through product evidence.

## Derive cases from actual Game Model contracts

Create cases for the resolver, contact and lifecycle, Actor/Knowledge/Action/Decision/Encounter/Boss, State Catalogue and Consistency Groups, production dependency graph, and semantic transformations. Inventory the applicable 20 areas, actual variation, opportunity and exhaustion, native adapter conformance, first cold use, transition memory, network egress, and symbol matching. See the [QA route and counterexamples](v4-route.md).

Include applicable multi-hurtbox and substep deduplication, pooled generation, damage-over-time tick/expiry/snapshot, simultaneous death/phase/reward/kill, topology break/navigation/restoration, partial bundles and offline conflicts, ignored parameters, wrong axes or contact timing, and reconciliation after timeout. Physical device evidence is due at the actual claim or gate. Keep future obligations tracked.
