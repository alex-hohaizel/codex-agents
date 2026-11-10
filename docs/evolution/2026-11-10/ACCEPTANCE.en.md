# How the proposed update will be accepted

**Planned checks, not execution results.** The machine register is [ACCEPTANCE.json](ACCEPTANCE.json). Each case needs source-bound evidence and its own state; a fixture cannot prove a paid provider, real CPA accuracy, target-device experience or owner acceptance.

## A01 — Business idea through original product outcome

**Input:** Business idea, accepted scope/references, requirement register, initially no detailed spec.

**Required observation:** Restore/clarify only material gaps; select existing owner; version decisions; complete the agreed product case; do not stop at skill creation.

**Accountable:** Orchestrator + product director. **Requirements:** R01, R07, R08, R11, R15, R17, R23. **Status:** planned, not executed.

## A02 — API ingestion and replay

**Input:** Controlled paginated API fixture with duplicates, 429, partial fetch and crash before cursor commit.

**Required observation:** Actual adapter produces correct deduplicated dataset, full counts/quarantine, stable restart and visible partial state.

**Accountable:** Data + integrations. **Requirements:** R01, R02. **Status:** planned, not executed.

## A03 — Scraping and schema drift

**Input:** Permitted static/dynamic source fixtures, login HTML, changed type/unit/selector and missing page.

**Required observation:** Appropriate acquisition mode; no bypass; drift detected/quarantined; no false empty success; repeatable parser/browser evidence.

**Accountable:** Data + privacy reviewer. **Requirements:** R02. **Status:** planned, not executed.

## A04 — Lineage, revoke and hostile source

**Input:** Dataset versions, downstream embedding/feature/cache/job, revoked source and injected tool instruction in source text.

**Required observation:** Dependent proof invalidates on changed bytes; revocation propagates with explicit limits; source cannot gain execution rights; rates/budgets honored.

**Accountable:** Data + privacy + QA. **Requirements:** R02, R21. **Status:** planned, not executed.

## A05 — Multilingual NLP classification/extraction

**Input:** Versioned multilingual labelled review sample, held-out labels, duplicates/noise.

**Required observation:** Baseline vs candidate, language subgroup/error review, source-grounded outputs and separate training/evaluation; no invented ground truth.

**Accountable:** Analysis + independent evaluation. **Requirements:** R03, R09. **Status:** planned, not executed.

## A06 — Clustering and real trends

**Input:** Timed corpus with duplicated authors, coverage shift, outliers and stable underlying theme.

**Required observation:** Interpretable memberships incl noise, stability/sensitivity, coverage-aware trend interpretation; similarity score is not business/causal truth.

**Accountable:** Analysis + product reviewer. **Requirements:** R03, R09. **Status:** planned, not executed.

## A07 — LLM/agentic durable effects

**Input:** Task rubric, prompt/model version, fake provider timeout after consumption plus available real host/model route.

**Required observation:** Actual bounded model case if access available; typed tool inputs, spend/rate caps; pause/restart/cancel; reconcile unknown outcome before retry; checkpoint alone never claims external exactly-once.

**Accountable:** AI + integrations + evaluation. **Requirements:** R01, R04, R09, R12, R21. **Status:** planned, not executed.

## A08 — Tabular baseline and candidate

**Input:** Licensed small fixture, target/grain/features with availability, groups/time split.

**Required observation:** Actual fitted baseline and justified candidate, training-only transforms, reproducible inference/model bundle, error/subgroup/uncertainty report; fixture accuracy not market claim.

**Accountable:** ML + independent evaluation. **Requirements:** R05, R13. **Status:** planned, not executed.

## A09 — Time series and cold start

**Input:** Chronological dataset with delayed values, held-out horizon, missing series and sparse target.

**Required observation:** Walk-forward appropriate validation, no future leakage, naive forecast comparison, explicit abstention/fallback for insufficient data.

**Accountable:** ML + evaluation. **Requirements:** R05, R13. **Status:** planned, not executed.

## A10 — Prelaunch CPA honesty

**Input:** Feature available_at, campaign/account IDs, spend/conversions/currency/attribution windows, delayed/censored labels.

**Required observation:** Reject postlaunch signals; time/group holdout, baseline and uncertainty/calibration; articulate selection bias; no claimed CPA accuracy without representative authorized data. Include zero-conversion campaigns: CPA can be undefined or censored; do not silently discard them or report survivor-only accuracy.

**Accountable:** ML + growth + evaluation. **Requirements:** R05, R13. **Status:** planned, not executed.

## A11 — Adaptation feasibility to consumer

**Input:** Exact compatible base/tokenizer/adapter, rights, device/resource probe, isolated training/evaluation set.

**Required observation:** Compare simpler alternatives; bounded real permitted tuning/load/inference where feasible; mismatch rejected; serving regression/rollback; missing model/hardware/cost approval leaves runtime gate open. Reject untrusted code-executing deserialization, unreviewed remote code, malicious manifest/path and excessive allocation before unintended effects. Accept adapter, merged and quantized exports, and the serving consumer separately against their actual bytes; adapter success never proves a changed export.

**Accountable:** ML + reliability + evaluation. **Requirements:** R14, R21, R23. **Status:** planned, not executed.

## A12 — Reference identity and actual medium

**Input:** Accepted original/editable master plus requested image/vector/3D/audio/video/UI/document outputs and consumer profile.

**Required observation:** Read actual reference; approved representative slice, render/playback/listen/interaction as applicable; derivative lineage and target-consumer proof; unsupported medium explicitly unproven. Reject a palette/label-matching candidate that loses the accepted composition, scale, information depth, interaction or function; reject later derivative identity drift.

**Accountable:** Creative + domain craft + QA. **Requirements:** R04, R12, R16, R23. **Status:** planned, not executed.

## A13 — Costed batch with failures

**Input:** Versioned batch manifest, duplicate items, partial provider result, rejected variant, cancel and unknown billing response.

**Required observation:** Complete denominator and per-item state, accepted-output total cost, stable IDs/cache, no blind retry; rejected aesthetic/identity output not counted accepted.

**Accountable:** Creative + cost + integrations. **Requirements:** R04, R12, R16, R21. **Status:** planned, not executed.

## A14 — App/bot/game asset consumer

**Input:** Domain fixtures with persona/identity, platform set, game engine asset constraints or bot playback.

**Required observation:** Existing domain depth retained; asset consumed in actual relevant runtime; mesh/rig/UV/audio/UI constraints checked when applicable; source file alone insufficient.

**Accountable:** Domain director + media/assets + QA. **Requirements:** R08, R12, R15, R16. **Status:** planned, not executed.

## A15 — Useful nontechnical interface

**Input:** Working data/model result and source-backed project/work set with accepted goals, errors and partial access.

**Required observation:** Interactive complete input→progress→result→correction/recovery flow; readable agreed outcome, real map/evidence/next actions; desktop/mobile visual/keyboard checks; no dummy success controls. A generic simpler layout retaining colours/labels but dropping agreed information/navigation/function must fail.

**Accountable:** Product + experience + independent QA. **Requirements:** R01, R06, R07, R08, R16, R23. **Status:** planned, not executed.

## A16 — Prototype productionization and release

**Input:** Existing prototype with real invariants, access boundaries, jobs/data, build and operator needs.

**Required observation:** Reproducible build, API/UI seam tests, failure/recovery, deployment preparation, support/runbook/rollback; actual external deployment/users only if authorized and observed.

**Accountable:** Product + backend + reliability + QA. **Requirements:** R01, R06, R07, R15. **Status:** planned, not executed.

## A17 — Scoped execution and production auth

**Input:** Service endpoints, credential handles, path/resource limits, hostile payload, network denial, commercial consumer scenario.

**Required observation:** No arbitrary shell/MCP/ambient account access; provider auth separate from owner coding login; secrets absent logs; finite cost/time/rate limits, interrupt/reconcile and unavailable states.

**Accountable:** Reliability + privacy + integrations. **Requirements:** R06, R21. **Status:** planned, not executed.

## A18 — Host and team boundary

**Input:** Existing12 + proposed4 profile manifest, real host availability, Codex/Cursor/Claude task capsules.

**Required observation:** Bounded validated roles and actual slots; precise ownership/handoff; independent reviewer separate actor; native host config/permissions preserved; absent host/access honestly unavailable.

**Accountable:** Constructors + Orchestrator + QA. **Requirements:** R10, R17, R19, R22. **Status:** planned, not executed.

## A19 — Construct to install to original task

**Input:** Approved fixture project-agent passport and original product request, generated portable bundle, actual supported discovery root.

**Required observation:** Create/validate/package, reviewed install, actual host discovery and invocation; generated agent completes bounded original product task with source/tool receipts; no structural-only substitution.

**Accountable:** Foundry + Orchestrator + independent QA. **Requirements:** R10, R11, R17, R19, R23. **Status:** planned, not executed.

## A20 — Core/optional/role preservation and rollback

**Input:** Known installed baseline, custom icon/color/settings/local edits, unknown source and interrupted apply.

**Required observation:** 33 core remain; two existing optional sources preserved and seven new sources admitted only by manifest (nine optional targets total); before copies/journal, exact verify; unknown edits conflict notoverwrite; guarded rollback; no invented receipts.

**Accountable:** Maintenance + installer + QA. **Requirements:** R18, R19. **Status:** planned, not executed.

## A21 — Existing generated-agent adoption

**Input:** Old native state/ownership/requirements/permissions/identity, custom agent changes, unfinished/deferred work.

**Required observation:** Source-to-target plan, applicable inherited resources actually portable, native state/owner constraints retained, one real bounded continued task; unrelated products untouched. Private scope register counts actually discovered owned agents as inspected/adopted/conflicted/deferred/not inspected; all-private-agent migration is never inferred.

**Accountable:** Foundry + maintenance + product owner. **Requirements:** R18, R19. **Status:** planned, not executed.

## A22 — App profile contradiction regression

**Input:** Platform subsets Android-only/iOS-only/web-only and multiple; authorized/banned human research profiles.

**Required observation:** No unconditional allthree or general human-testban overrides actual accepted profile; existing project-specific owner bans preserved in specification/build/QA/release. Cover concepts and all eleven App phases, including applicable references/templates and generated cases.

**Accountable:** App director + independent QA. **Requirements:** R18. **Status:** planned, not executed.

## A23 — Independent full route acceptance

**Input:** Exact artifacts/bytes of data→analysis/model/LLM→API/UI→operation representative product and unresolved requirement ledger.

**Required observation:** Independent semantic and seam review, original outcome traceability; change invalidates dependentproof; structural/runtime/device/provider/owner evidence separate; no claim everyfutureproduct certified. Freeze the task rubric and raw baseline/candidate cases before an improvement claim; include held-out/adversarial cases, reduce order/author bias and retain actual independent verdicts.

**Accountable:** Independent QA + judge + current integrator. **Requirements:** R01, R06, R07, R08, R10, R11, R15, R17, R23. **Status:** planned, not executed.

## A24 — Complete documentation and exact release

**Input:** All35 current then42 proposed sources,16 profiles, resource/helper catalogues, seven affected guides, packages/Git/CI.

**Required observation:** Human purpose/path/trigger/I-O/consumer/access/tests/limits/recovery for everylogicalelement; requirements coverage; source/hash/link/translation/privacy checks; both packages CRC/hash; exact remote commit/CI readback; WORK source≠installation.

**Accountable:** Documentation + maintenance + independent review. **Requirements:** R19, R20, R22, R23. **Status:** planned, not executed.
