# Independent review workflow

Contents include plan, evidence type, agent cases, product acceptance, critical areas, and finding and retest.

## Plan and freshness

Pin subject, scope, author, requested observer, sources and artifact hashes, and dependencies. Verify current requirements, decisions, and facts against owning files. Use summaries as pointers. Identify due musts, future proofs, and unverified assumptions. Check actual tools, hosts, accounts, devices, and budget. Choose the smallest check that can disprove a material claim.

Record ID, acceptance, negative case, method, artifact, actor, stage, outcome, and limits. Verify authority before spending or external changes and use sandbox or local fixtures when sufficient. Stop at the agreed boundary.

## Evidence types

| Method | Directly supports | Requires separate evidence |
|---|---|---|
| Schema, links, syntax | Structure, format, local references | Domain quality and product operation |
| Document review | Requirement and plan consistency, arguments, scope | Execution of the plan |
| Raw forward case | Agent behavior on the given inputs | General reliability across future inputs |
| Code, unit or contract tests | Covered invariants in the test scope | Physical device or live provider behavior |
| Sandbox integration | Observed sandbox integration | Production entitlement or profit |
| Device or end-to-end (E2E) | Observed scenario in the exact environment | All platforms, devices, or human usability |
| Provider or deploy read-back | Scoped external state | Indefinite availability or market success |

Track whether proof comes from self-check or independent review separately from method. Digests bind bytes. Owner intent, value, revenue, and actual actions require their own evidence.

## Agent forward cases

Start with the 44 contracted cases and check the current suite and version. Use a different actual actor to evaluate author work. Give the actor an ordinary request, raw artifacts, and the skill. Keep oracle, hints, and diagnosis outside the task prompt. Preserve examples such as «правильна відповідь повинна...» only in evaluator material. Isolate case outputs so one case cannot disclose hints to another. Judge actual results and effects. If independent review is unavailable, retain self-check and keep the gate open. Use scoped fixtures without live spending, customer access, or production mutation to test capability.

## Product acceptance

For each core journey, define entry, success, invalid and empty inputs, cancel, interruption, retry, and recovery. Check interfaces between client and API, identity and data, provider and entitlement, knowledge and support, code and schema. Use previous-version, corrupt, and large data fixtures where risk warrants them. Derive oracles from requirements and exercise negative paths.

Record distinct build, platform, browser, and device versions and evidence for Android, iOS and web. Test accepted design states, motion and feedback, keyboard, text, accessibility, offline and degraded behavior. Set budgets before measurement and retain environment, samples and procedure. Keep missing physical device proof blocked with a handoff. Treat synthetic UI results as synthetic observations.

## Critical areas

- Auth and privacy: guest and A/B tenant cases, object ownership, cache, history and attachments, logs and AI egress, revocation, deletion and restore.
- Billing: provider verification, restore, duplicate, reordered and delayed events, lifecycle, offline and reconciliation.
- Support: public and personal scope, challenge and revocation, webhook authenticity, group rejection, stale knowledge, prompt injection defenses, caps and outage.
- Reliability: cancel, timeout and unknown outcome, retry deduplication, process death and network loss, backup and restore, migration and rollback compatibility.
- Automation: repeated manual exceptions, support, content and moderation, cost and monitoring dependencies.
- Release: current store, account, testing, signing, and cost before full build and again before submission.
- Acquisition and economics: traceable sources, assumptions, recurring costs and stopping criteria. Treat revenue as unproven until observed.

Verify mutable rules and SDKs from current primary sources.

## Finding and retest

Record raw reproduction, observed property, violated requirement, subject hash, environment, and impact. Distinguish reproduced defects, document inconsistency, and untested concerns. Provide the narrow sufficient repair scope. The author repairs and the independent reviewer retests. After repair, check current bytes and dependencies and rerun the failed case and relevant regressions. Bind any carried verdict to its valid dependencies. Reconcile unknown external effects before repeating them. Close only evidenced IDs and assign pending proofs owners and due gates. Return a scoped verdict, evidence references, limitations, and exact next action.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show raw requirements reconciliation, independent scenarios and oracles, revision-bound findings, and a verdict for every due requirement. Distinguish completed work, inherited decisions, and future results with due gates. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review oracle validity, reviewer competence, missing requirements, and evidence limits. Review raw sources for omissions. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve context, approvals, and unaffected results.
