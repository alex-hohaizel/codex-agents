# Evidence for accepting a specification

## Contents

1. Distinguish specification and future gates.
2. Check requirements due at this stage.
3. Check cross-cutting requirements.
4. Exercise negative cases.
5. Return findings and status.

## 1. Distinguish specification and future gates

Use the existing requirements, decisions and evidence contracts. Record reviewer, date, method, inputs, hash, finding, REQ-ID, status and limits. Keep author self-check and actual independent review separate. Schema and link validation cannot establish semantic completeness of PRD/TDD.

| Gate or status | Confirm | Scope boundary |
| --- | --- | --- |
| draft/blocked | Valid parts and exact blocker. | Headings alone do not define a contract. |
| spec-ready | Sufficient domain documents, estimates, due checks and decisions. | No claim of working app, store access or proven demand. |
| slice_planned | Executable risk-based plan. | A plan does not prove an actual pass. |
| before-full-build | Actual slice and other prerequisites. | PRD/TDD alone is insufficient. |
| before-release | Current tests, permission and owner readiness. | Early feasibility does not make the candidate ready. |

Accept a sufficient spec without binary, production API or live purchase. A due specification must cannot be deferred as a future test. Preserve verified docs when external access is unavailable and block only the dependent production decision.

## 2. Check requirements due at this stage

### REQ-11 — Minimal AI and API dependence

For each dependency verify concrete value, a no-dependency option and a real alternative or fallback. Require current source and date for price, quotas, commercial and data rights, license, offline behavior, exit and caps. Include expected and stress usage, abuse and retries in costs. A no-API solution needs a reasoned domain explanation. Reject a free tier without quota/overage analysis, a subscription treated as unlimited production API use, and one-time revenue with unmodeled indefinite paid calls. Missing price, license or account access blocks the affected effect. Require options, cost model, data map, fallback and exit, and a trace to the feature or API.

### REQ-16 — Local data and minimization

Require a full field, copy and transfer map, local/cloud comparison and reason for cloud. Specify purpose, access/authz, retention/export/delete/revoke/restore for each data class. Define no-account, guest and account branches. Check sync conflict, offline queue, tombstones, migrations, backups and restore. Review support, dialogs, logs, cache, indexes, AI and telemetry separately. Reject default tracking and silent upload of local data. Keep private support out of public knowledge or model context beyond the approved map. Require data/auth contracts, access matrix, sync and state rules, lifecycle, negatives and data-gate status.

### REQ-19 — Complete scope and realistic estimates

Require entry, useful result, repeat use and recovery on the three applicable clients. Compare core and broader scope under equal time and resource assumptions. Include work packages, ranges, critical path, dependencies and integration, QA, release and support effort with contingency. Require concrete reuse evidence rather than «AI швидко напише». Check hidden loss of quality, platform scope or owner work. Do not invent a deadline or compress estimates to fit a desired answer. Require scope table, client core matrix, assumptions, risks, slice plan, roadmap and decision.

### REQ-38 — Early release feasibility

Require dated primary rules and fees, platform route, actual account type/access, signing/build host and required testing. Compare prerequisites to budget and human-work limits before production or significant build. Without access, mark the exact dependency and operation unverified and specify the next check. Do not hide required fees or simulate identity, testers, signatures or MFA. Recheck before release and after account, platform or model changes. Record source, date, status, cost, conflict, alternative, recheck and owner budget/scope delta where needed.

## 3. Check cross-cutting requirements

| REQ | Check in spec | Scope boundary |
| --- | --- | --- |
| REQ-03 | Compare setup, recurring and usage charges with the cap and show zero-budget conflicts. | No external spending. |
| REQ-04, REQ-09 | Define recurring automation, errors and unresolved cases. | No hidden daily owner work. |
| REQ-10 | Define complete standalone Android/iOS/web cores and acceptance. | Actual client proof belongs to build/QA. |
| REQ-12, REQ-15 | Link value to monetization, recurring benefit and costs. | No guaranteed demand or profit. |
| REQ-17 | Preserve applicable bans on human research, testing or A/B at every phase. | Synthetic, public reviews and owner review cannot prove human validation. |
| REQ-18 | Define acquisition from zero audience with rights, caps and stop. | Activation is a separate gate. |
| REQ-20, REQ-21 | Pass design states, accessibility, device and offline requirements. | Do not choose on behalf of the owner or accept a placeholder. |
| REQ-24 | Reuse current owner decisions in exact scope. | Reopen only an affected decision and preserve reserved choices. |
| REQ-28, REQ-30, REQ-31 | Define guest/auth/data/knowledge, read-only help and fallback. | No automatic expansion of the context or bot effects. |
| REQ-32 | Specify metric, threshold, horizon, budget, stop and next action before a test. | Preserve thresholds after failure and human-experiment restrictions. |
| REQ-35, REQ-36 | Keep status, details, chat explanation, versions, hashes and checkpoint. | Preserve requirements and reconcile unknown effects before retry. |
| REQ-37, REQ-40 | Identify actual authors and reviewers, scope of jobs and caps. | Self-check stays distinct. |
| REQ-43 | Define model-specific rights, restore, events, refund, expiry and cancellation. | Provider proof remains due in build/QA. No automatic subscription. |

Check experience handoff for journeys, objects, states, platform constraints and owner decision. Build needs transitions, invariants, schemas, errors, events, conflicts, slice oracle and fixtures. Support needs version, locale, knowledge sources, context fields, linking, revocation, retention, costs, fallback and action bounds. Release needs prerequisites, unverified items, exact blocked effect and recheck dates. Growth/operations need economics, automation, caps, stop, recovery and retirement without hidden manual work.

## 4. Exercise negative cases

Use a tabletop with synthetic fixtures. For every case require an unambiguous rule, transition, output and artifact section. Record a finding for ambiguities. A walkthrough does not establish runtime execution, actual human research or usability.

| Case | Input | Required behavior |
| --- | --- | --- |
| NEG-SPEC-01 | Start the web core without mobile. | Deliver the complete core. Reject a landing-only substitute. |
| NEG-SPEC-02 | Send a command in a forbidden state across three clients. | Same domain refusal with defined recovery. |
| NEG-SPEC-03 | Offline changes from two clients synchronize in reverse order. | Defined conflict result without loss of ownership or data. |
| NEG-SPEC-04 | Delete record/account, then restore old data or reconnect an offline client. | Respect deletion, revocation and tombstones. |
| NEG-SPEC-05 | Session A passes B's ID through API, support, cache, history or channel. | Reject backend access and keep B's context private. |
| NEG-SPEC-06 | Merge a guest session with duplicates and partial failure. | Ownership proof, defined merge and retry without access leaks. |
| NEG-SPEC-07 | Change display name or username, or present an invalid channel link or credential. | Require server proof, expiry, replay resistance and revoke. |
| NEG-SPEC-08 | Quota exhausted or offline, stale or invalid provider result. | Bounded retry or fallback and visible limit, under cap. |
| NEG-SPEC-09 | Vendor pricing, license or API availability changes. | Block/recheck/exit path with economic and scope impact. |
| NEG-SPEC-10 | One-time purchaser uses maximum recurring resources. | Verify costs, caps and permitted access. |
| NEG-SPEC-11 | Duplicate provider events, refund before late purchase, or network loss after provider success. | Deduplicate, reconcile and verify authoritative entitlement without double grant. |
| NEG-SPEC-12 | Restore, new device, account change or sign-out/offline after expiry. | Reconcile claimed cross-client rights and recovery. |
| NEG-SPEC-13 | Cancel, refund or partially consume usage. | Model-specific distinct transitions. |
| NEG-SPEC-14 | Ads, affiliate or no-purchase model. | Justify inapplicable branches. No forced subscription. |
| NEG-SPEC-15 | Enable «корисну аналітику» or AI diagnostics without a data decision. | Leave pending. Do not transfer new fields or private dialogs. |
| NEG-SPEC-16 | Use synthetic UX for demand or passive metrics as A/B consent. | Limit claims and reject the human experiment. |
| NEG-SPEC-17 | Required fee or human store testing conflicts with profile. | Record conflict, blocked route, allowed alternative, delta and stop. |
| NEG-SPEC-18 | No developer account or signing access. | Mark prerequisite unverified and leave store readiness open. |
| NEG-SPEC-19 | Add larger scope without reuse at the same deadline. | Re-estimate critical path and reopen decision without compressing QA. |
| NEG-SPEC-20 | Recurring support, moderation or content cannot be automated. | Address operational feasibility and expose required owner work. |
| NEG-SPEC-21 | A polished mock lacks persistence, auth or API risk. | Reject as representative of those risks. |
| NEG-SPEC-22 | Complete spec without binary. | Allow spec-ready when due proofs pass and actual future gates remain pending. |
| NEG-SPEC-23 | Change data, API or paid rights after baseline. | Reopen affected proof, estimates and decisions. Preserve superseded records. |
| NEG-SPEC-24 | Cap exhausted after two equivalent failed tests. | Save checkpoint and change diagnosis or stop. Preserve musts. |

Extend cases for empty/max-size inputs, units, timezones/DST, localization, denied permissions, stale external data and migration incompatibility. Choose fixtures by risk instead of replicating implementation branches.

## 5. Return findings and status

Record finding ID, REQ-ID, artifact/hash/section, expected and actual behavior, severity, blocked gate, owner, repair and retest. Distinguish spec blocker, future implementation proof, external prerequisite, hypothesis and evidence gap. Show impact and due verification for critical unknowns. Stop the dependent action for missing due must, reserved decision change, uncertain data/effect rights or cap, while continuing independent document work. Verify links, REQ-ID, paths, hashes, semantic consistency and completed documents. Report spec-ready only with accepted documents, due checks and resolved spec blockers. Identify future gates, unreliable prerequisites, hypotheses and exact next action. Deliver short status with detailed material and reasoning. Specification delivery does not establish the finished product.
