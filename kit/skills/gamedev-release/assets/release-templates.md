# Release templates for verified records

## Release summary

| Field | Value and evidence |
|---|---|
| Project / release / stage | |
| Source commit / accepted package hash | |
| Platform / countries / audience | |
| App/package ID / team / public certificate fingerprint | |
| Version / build / track | |
| APK / AAB / Xcode project / Simulator app / archive / IPA hashes | |
| Config / economy / catalog / content / save versions | |
| Exact QA evidence / missing device coverage | |
| Studio identity hash / subset | |
| Store live products / sandbox mapping | |
| Privacy snapshot / compliance date | |
| Rollout / stop / rollback or roll-forward | |
| External action / authorization evidence | |
| Provider receipt / review state / URL | |
| Owner / next command | |

## Readiness states

`not-configured`, `prepared`, `locally-tested`, `sandbox-verified`, `uploaded`, `in-review`, `approved`, `available-to-testers`, `live`, `blocked` — record the observed status separately for each platform and channel.

## Adapter setup card

Provider / purpose / version / official docs + checked date / license / free or recurring cost / selected decision / SDK+permissions+data / test setup steps / live setup owner / secret references / sandbox proof / failure cases / telemetry / rollback+revoke / blocker.

## Submission checklist record

Requirement ID / official URL / checked date / applies because / artifact hash / test/result / reviewer / remaining action. Use `not-run` until an actual result supports `pass`.

## Release scope matrix 3.0

Domain/feature → actual model/rule/scenario IDs → due gate → exact RC dependency hashes → required case/method/evidence layer → actual proof/reviewer → passed/failed/not-tested → owner/blocker. Inventory denominator: launch content/encounter families, screens/states/journeys, learning transfers, progression phases/rewards, offers/entitlement types, supported devices/platforms. `release-case-catalog.json` supplies patterns; add product-specific cases.

## Populated planning example — not execution

Case `REL-IAP-PENDING`: IAP enabled; sandbox product consumable; purchase state pending. Procedure: background app, restart, deliver pending callback twice, then verified purchased twice. Expected: pending gives no entitlement; verified purchased commits one durable grant and prescribed acknowledgement/consumption; duplicates return existing outcome. Oracle: current store contract + approved transaction state machine. Required: sandbox/device traces and sanitized ledger; actual result/proofs/reviewer remain unset until execution. No example closes a gate.
