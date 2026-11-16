# Independent App Atelier acceptance

Contents: 1 coverage, 2 oracles, 3 interaction matrix, 4 production audit, 5 findings and freshness.
Read cross-domain-core and the current workflow, acceptance, and evidence references. `assets/app-depth.templates.json` defines planned cases and evidence. Keep TEST-01–TEST-44 and extend them with additional cases.

Use the [app system model](app-system-contract.md) for app-specific contracts. It owns requirements and state authority.

## 1. Derive sufficient coverage

Map `requirement/source → domain rule → state/variant/platform → interaction → artifact → method/oracle → observer → due verdict`. Each product claim needs a feasible causal path, owner, consumer, and appropriate evidence. Cover complete variation families and lifecycles. Select combinations by dependency and risk.

Treat mandatory requirements as hard gates. Privacy, integrity, billing, scope, and release failures remain open regardless of other scores. N/A requires a product decision that excludes the capability. Missing SDK, account, or device means blocked. Assign future evidence an owner and due stage, and current required results pass, fail, or blocked.

Check author and reviewer IDs against actual work. An author acting under another role remains the author. When independent review is unavailable, retain self-check and an open gate and provide a usable raw packet. Give the actor under evaluation the ordinary task, skill, and raw sources. Keep oracle, diagnosis, and fix with the evaluator.

## 2. Verify rules independently

For numerical rules check units, ranges, precision and rounding, modifier order, capture and read time, null and default, exact errors, and golden vectors. Compare with an independently derived reference calculation. Check money, currency and scale, calendar, instant, timezone and duration, locale and encoding, and ID formats. For probabilistic rules, test applicable distributions, tails, and failures as well as averages.

Check transitions and invariants after success, failure, cancellation, timeout, unknown outcome, and recovery. Exercise forbidden transitions with negative cases. Use model-based, property, metamorphic, or differential tests when they have a meaningful oracle. Prove a critical test can fail using mutation or a deliberately flawed fixture.

Match the method and assertion to the claim. Schema, hashes, and format confirm structure or identity. Unit tests cover their domain boundary. Sandbox and E2E results cover their observed integration and environment. Physical devices prove the measured property on that device. Official receipts and read-back prove the scoped external state. Human usability, demand, and revenue require their own evidence. Honor current restrictions on human testing.

## 3. Exercise causal interactions

Pin source, build, config and component hashes, runtime bindings, initial state, inputs and event order, expected observations and tolerances, target, input method, and actor IDs. Run the full scoped core on Android, iOS, web, and support.

| Boundary | Counterexamples |
|---|---|
| Input → command | Double tap, stale screen, invalid or large input, cancel before and after commit |
| Command → state | Duplicate or reordered event, revision conflict, partial effect, missing precondition |
| State → persistence | Process killed before or after durability, disk full or corrupt, duplicate recovery |
| Offline → sync | Concurrent edits, queued dependency, clock skew, account change, expired command |
| Auth → data → UI | A/B tenant, cached or late response after logout or revocation, leakage in files, logs, or support |
| Checkout → entitlement | Pending, valid receipt, duplicate or reordered callback, cancel, expiry, refund, revocation, restore |
| Permission → feature | Denial, revocation, settings change, background to foreground |
| Knowledge → support | Wrong version, locale, or price, injection, missing fact, unauthorized effect, stale link |
| Upgrade → recovery | Old schema or client, interrupted migration, rollback mismatch, revival of deleted data |
| Build → runtime | Release-only stripping, config or signing mismatch, callback threading, cold start |
| UI → accessibility | Focus, back, keyboard, touch, text scaling, reduced motion, mute, localization overflow |
| Service → budget | Quota, outage, retry storm, storage growth, limit reached, unknown job cost |

Check applicable p95, p99, tail behavior, error rate, and worst-case inputs beyond averages. Derive thresholds from the product, audience, and measurement. Record simulator, emulator, browser, and physical evidence independently.

## 4. Audit production and handoff

Check each output against the bound recipe, input, tool, model, exporter and importer hashes, actual attempt, and consumer. Verify schema support and actual consumption for each required parameter. Record discovery, operation-tested capability, and native proof separately. Preserve distinct editable master and derivative hashes, rights, and transformation invariants.

Verify units, timezone and timebase, locale, text, color and alpha, asset scale and anchor, IDs and money precision, compression and latency, and event timing. Verify meaningful properties beyond format and check rights, attribution, and data egress separately.

Report pending and unknown attempts. Reconcile timeouts before retrying upload, deploy, payment, or LLM jobs. Report cyclic planned dependencies, missing consumers and recipes, missing proof references, stale hashes, and fake provider IDs individually. Canonical state owns status and JSON templates and reports describe it.

For Work→Codex verify manifest, digest, actual paths, available toolchain, exact launch and return commands, and expected proof. Revalidate any inherited verdict. Structural scripts do not establish native execution or owner authorization.

## 5. Findings, repair, and closure

Record ID and severity, requirement, current subject hash, raw reproduction and expected and observed behavior, environment and actor, proven or suspected status, impact and dependencies, repair owner, and next validator. Keep causes under investigation separate from observations. Specify cap, changed variable, and stopping condition. Change method or diagnosis after two unsuccessful repetitions of the same hypothesis.

Retest the failure and affected regressions. Carry proof forward only with unchanged dependency digests, valid environment, permissions and terms, and preserved evidence. Changes to source, model, SDK, importer, policy, knowledge base, or target reopen dependent proof. Changing the test suite preserves prior evidence level.

Each due requirement needs a verdict with actual method, result and proof, limitations, and next action. Owner readiness and external permission are separate decisions. Close only with current proof.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Provide raw requirement reconciliation, independent cases and oracles, revision-bound findings, and a verdict for each due requirement. Distinguish executed work, inherited decisions, and future results with due gates. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review oracle validity, reviewer competence, missing requirements, and evidence scope. Inspect raw inputs for omissions. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve project context, approvals, and unaffected results.
