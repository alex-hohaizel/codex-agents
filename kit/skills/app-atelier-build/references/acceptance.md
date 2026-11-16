# Build acceptance

Assess every due must separately, including code authored, build passed, device verified, independently reviewed and released. Label author checks as self-checks.

## Outputs and evidence

| Area | Acceptable proof |
| --- | --- |
| REQ-10 | The useful core actually works in standalone Android, iOS and web clients. |
| Accepted experience | Real screens, states and assets match accepted masters and approved deviations by digest. |
| Data/auth | Contracts, migrations, subject/field isolation, recovery and negative checks. |
| REQ-43 | Provider-backed entitlements, lifecycle, restore, retries, refund and revocation as applicable. |
| Production route | Early store/account/cost/testing feasibility and actual SDK, build and signing prerequisites. |
| CI | Reproducible build with exact configurations, checks and artifact provenance. |
| Devices | Exact environment, version, device, procedure, observation and limits. Label simulator proof accurately. |
| Handoff | Source/build hashes, commands, results, known limits and precise next action. |

A landing page cannot stand in for the web client, Android evidence cannot cover iOS, and a mock cannot prove a live provider integration. For missing device, SDK or signing, record the blocked evidence and an exact launch/return bridge. Verify without real charges, production migrations or publication when those effects exist only to demonstrate a test.

## End-to-end product cases

1. New state, core action, correct domain result, persistence, restart and the same allowed result.
2. Invalid, empty and oversized input gives a comprehensible error without leaving incorrect partial state.
3. Interruption, kill, backgrounding or network loss does not duplicate actions or permanently lose confirmed data.
4. A retry after timeout reconciles state and does not repeat a known transaction or effect.
5. User A or a guest cannot view B's records through API IDs, cache, files, support history or deep link.
6. Logout, revocation and deletion remove the relevant grants and context. Old caches or backups do not restore them outside policy.
7. The agreed local/offline mode fulfills its promise and reports unavailable functions before claiming completion.
8. App and schema upgrade from realistic prior data keeps invariants and has tested recovery.
9. Denied/revoked platform permissions, differing viewports or input methods and accessibility settings do not break the core.
10. External API outage, quota or cost cap uses the accepted degraded behavior without a hidden paid loop.

## Billing and entitlement cases by model

| Case | Check |
| --- | --- |
| Provider sandbox success | Entitlement follows trusted verification rather than a UI success message. |
| Pending, aborted or failed checkout | No incorrect paid access and no loss of already valid access. |
| Restore, reinstall or device switch | Exactly the stated applicable entitlements return. |
| Duplicate event, callback or webhook | No duplicate effect, credit or extension. |
| Delayed or reordered event | An old message cannot replace current state. |
| Expiry, cancellation or renewal failure | Timing and access follow the provider model. Cancellation does not imply immediate revocation. |
| Refund or revocation | Authoritative route confirms the necessary state change. |
| Offline or recovery | Access and re-verification timing fit the promise and threat model. |
| Cross-client access | Agreed Android, iOS and web access without promising unsupported portability. |
| Unknown outcome | Reconcile before retrying to avoid a duplicate purchase or effect. |
| Price and plan disclosure | Show the real cost, period, limits and terms. |
| Ads failure, cap and ad-free restore | Core remains usable, advertising is labeled and unobtrusive, and paid ad-free access restores. |

Missing provider access cannot make a branch N/A. Justify inapplicability from the selected model. A one-time product does not require a subscription, and one-time revenue cannot cover unmodeled indefinite API or AI costs.

## Regression and closure

For a repair, reproduce the raw case, identify the cause, fix it and test affected behavior. Repeat the full suite only when justified by impact. Time or unavailable tools cannot silently lower agreed coverage. Honor current human-test constraints and distinguish owner or synthetic observations from demand evidence. Give a different actual QA actor code, builds, raw logs and criteria without a suggested verdict. Register real commands, exit/result, hashes, platform, environment and residual risks in canonical state. When a due must fails or is blocked, record the exact dependency and next action before claiming readiness.
