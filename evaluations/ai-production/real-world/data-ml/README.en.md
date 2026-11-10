# Actual bounded data and model exercises

These explicit evaluation commands support the existing conditional DATA, ANALYSIS, PREDICTION and EVALUATION methods. They install no skill, framework, scheduler, registry or persistent service. The existing project owner chooses the method; a familiar library name is not a requirement. [Observed results](RESULTS.en.md) include rejected candidates and unresolved gates.

## D01 — Scope and source rights

Use Python3.13 with its standard library and an explicitly chosen private output directory outside this reusable repository. No package or model download is needed. The executed envelope was $0, at most12 public data requests,2 MiB public downloads,60 seconds per command,180 seconds combined fits,256 MiB Python-process RSS and100 MiB retained task outputs. Browser/process-tree memory is not established by Python RSS. The headless browser is optional and uses an already available local Chrome binary.

Two actual licensed sources are used: [UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset), Hadi Fanaee-T, DOI10.24432/C5W894; [UCI Paper Reviews](https://archive.ics.uci.edu/dataset/410/paper+reviews), Brian Keith, DOI10.24432/C50G60. Both UCI pages state CC-BY4.0. Archive/member hashes and acquisition receipts stay in the private output. The issue analysis additionally consumes the owner's existing 100 public-issue source snapshot, never private chats or earlier AI labels as human ground truth. Do not distribute raw issue bodies, pseudonymous authors, raw review rows or fitted model vocabularies here.

Before a new acquisition, verify actual source rights/access/size and any new costs. `acquire.py` permits only the two fixed official UCI ZIP URLs, bounds bytes/requests, checks archive members, and verifies cached SHA256 before reuse. A source file is not evidence that an integration or model worked.

## D02 — Acquire and freeze the study

Run from the repository root. Replace placeholders with your authorized local paths; `$TASK_DATA` must be private and outside this repository. Read `STUDY.json` before fitting. Its model selection, group splits, chronological folds, forbidden features and limits were frozen before the actual fits. A changed study needs a new revision and evidence, not a rebound old report.

```sh
python3.13 evaluations/ai-production/real-world/data-ml/acquire.py --out "$TASK_DATA/raw"
```

## D03 — Actual adapter and static/dynamic parsing

```sh
python3.13 evaluations/ai-production/real-world/data-ml/exercise_ingestion.py --corpus "$ISSUE_CORPUS" --out "$TASK_DATA/ingestion" --chrome "$CHROME"
```

The controlled loopback server transports the actual frozen100 issue records. One declared malformed control and one duplicate exercise quarantine and denominator accounting. An isolated subprocess exits97 after inserts but before the data/cursor commit. The restart checks actual SQLite contents, completes the source, and verifies that another completed replay performs no request. Missing pages, login HTML, cursor loops, source changes and off-origin redirects remain visible failures. Proxy environment variables are not used.

`ArticleParser` implements one explicit static `article` contract. Existing Chrome renders a JavaScript fixture containing the same actual source rows; the parser then reads its actual DOM. Without `--chrome`, dynamic evidence remains `not-run`. This does not claim unrestricted real-site scraping, authenticated access, anti-bot bypass or live GitHub transport resilience.

## D04 — Actual lexical grouping and retrospective counts

```sh
python3.13 evaluations/ai-production/real-world/data-ml/analyze_issues.py --corpus "$ISSUE_CORPUS" --trend-counts "$TREND_COUNTS" --out "$TASK_DATA/analysis"
```

The script computes train-free TF-IDF cosine neighborhoods, mutual three-neighbor graphs at three declared thresholds, retained noise, source-author weights and12 fixed-seed80% subsample stability checks. It emits source links privately for inspection; clusters are exploratory, not human-validated need categories. The original26 hour/latest100 sample cannot establish population trends.

`$TREND_COUNTS` is an explicitly acquired private snapshot with `records[]` containing `week`, Boolean `context`, `query`, `url`, `total_count`, `incomplete_results`, and `collected_at`. The actual supplement used four read-only [GitHub issue search](https://docs.github.com/en/rest/search/search#search-issues-and-pull-requests) requests: `repo:openai/codex is:issue label:app created:2026-10-19..2026-10-25`, the same with `label:context`, and both for `2026-10-26..2026-11-01`, each `per_page=1`. Current label counts on old creation weeks are retrospective and mutable. Incomplete searches fail admission; neither author groups nor issue counts represent active users.

## D05 — Fit real baselines and candidates

```sh
python3.13 evaluations/ai-production/real-world/data-ml/forecast.py fit --source "$TASK_DATA/raw/bike/day.csv" --out "$TASK_DATA/forecast"
python3.13 evaluations/ai-production/real-world/data-ml/reviews.py fit --source "$TASK_DATA/raw/reviews/reviews.json" --out "$TASK_DATA/reviews"
```

Forecasting uses calendar features and only mature lagged counts. The two-day reporting delay is a declared conservative scenario, not observed source publication metadata. Train-only scaling/coefficients, two walk-forward tuning folds, a separate interval-calibration period and a final chronological holdout remain separate. Current target, constituent counts and future observed weather are forbidden. Missing history, delayed labels and dates outside the validated historical period produce explicit rejection/abstention.

Review classification predicts researchers' perceived orientation on the source -2..2 scale. It excludes reviewer evaluation/confidence, paper acceptance, restricted remarks and paper identity from features. Paper groups sharing exact normalized text are merged before a deterministic group split; vocabulary is fitted only on training rows. Actual denominators, quarantined empty reviews, language subgroups, confusion matrices and group bootstrap intervals are preserved. Validation selects word/character features and smoothing; the holdout is never used to retune.

An observed protected metric loss rejects candidate adoption without compensation by another score. The actual review candidate is rejected; default inference retains training majority and human review. The forecast's nominal90% interval also fails measured90% coverage and is explicitly not admitted for that coverage claim. Its historical point estimate is not an autonomous operational recommendation. No synthetic fixture is business accuracy evidence.

## D06 — Actual delivered model consumer

```sh
python3.13 evaluations/ai-production/real-world/data-ml/deliver.py --forecast-model "$TASK_DATA/forecast/model.json" --review-model "$TASK_DATA/reviews/model.json" --source "$TASK_DATA/raw/bike/day.csv" --out "$TASK_DATA/delivery"
```

This creates a private bundle with eleven members: both actual JSON models, reviewed source and source-lineage helper, explicit input/output signature, model card, source snapshot and an exact member manifest. It rejects unlisted code, symlinks and directories before executing copied Python. Existing `__pycache__` is never trusted or silently deleted; stage a clean copy of pinned members. The copied parent/child use `-E -B` to ignore ambient Python paths/cache configuration and avoid bytecode creation. Changed weights/code cannot reuse old proof. The fresh-process loopback TEST adapter makes actual HTTP predictions and verifies point-prediction parity. No pickle, remote code, framework, external provider, deployment or customers are claimed.

The adapter reads a launcher-created0600 ephemeral Bearer key, not ambient Codex/OpenAI credentials. The test deletes it and terminates the process. Exact input fields, loopback Host/Origin,4 KiB requests, text length and request 25 rejection are checked. Missing authentication, hostile origins, tool/path keys, duplicate JSON fields, invalid dates and oversized input are rejected. No request text or Authorization header is logged. Rejected review candidates remain behind the explicit baseline/human-review policy. The same-Mac/Python copied-bundle result is not cross-device or production certification.

## D07 — Source revocation and CPA honesty

```sh
python3.13 evaluations/ai-production/real-world/data-ml/source_guards.py --corpus "$ISSUE_CORPUS" --out "$TASK_DATA/guards"
```

Actual isolated cache→features→job→proof files depend on the frozen issue source. A changed or revoked source rejects every dependent consumer; changed proof bytes also fail. The original dataset is untouched. A source injection string is processed only as data with no provider/tool/effect. This is an executable isolated lineage exercise, not withdrawal of the public GitHub source or a newly installed global index.

No representative pre-launch campaign features and spend/conversion outcomes were available. The CPA gate therefore refuses a fit and an accuracy claim. Declared synthetic boundary controls retain zero-conversion campaigns, avoid undefined finite CPA, and reject future features/outcome leakage or mixed currency/attribution units. They do not close actual CPA model quality. ADAPTATION/LoRA is a separate exact-model exercise, never inferred from this classifier.

## D08 — Verification and adoption

```sh
python3.13 -m unittest discover -s evaluations/ai-production/real-world/data-ml -p 'test_*.py' -v
```

Fourteen generic adversarial tests protect boundaries; the separate source-bound reports record actual execution. Private reports are not automatically published. New output directories preserve earlier failed/fixed attempts. Neither these files nor their tests close the original 29-case programme: independent review, affected preservation, panel consumption, owner acceptance and final release remain separate root-owned gates. No existing skills, settings, icons, native projects or installation are changed by these commands.

## D09 — Independent findings and new source-bound controls

The initial ten-member bundle proof is retained as history. Independent review found an unlisted-module import-shadow gap; the current eleven-member format rejects extra code/links/directories before execution. Actual isolated clones containing `json.py`, attacker bytecode directories and symlinks were rejected without executing them. The original owned bundle was not observed compromised.

The additional A06 oracle freezes exact controlled cohort IDs, stable theme pairs, an outlier and coverage expectations **before** execution. It uses the same actual clustering/author weighting method and binds the separate real 100-issue analysis and two-week public counts. Explicit synthetic theme/text controls test stable grouping, retained noise, author-volume distortion and coverage-shift abstention; they are not new semantic labels or business accuracy.

A09 now exercises the actual HTTP predictor with a declared seven-zero-lag counterfactual and observes `intermittent_history_not_validated` abstention. The positive Bike source contains no zero-demand history. A04 uses the actual copied source→model→prediction-signature gate before HTTP inference: valid prediction succeeds; changing actual copied source bytes or withdrawing that source under the isolated project's test policy returns HTTP 409 with zero added model invocations. Restoring the source yields the same point. This never revokes UCI's public license.

`qa_controls.py freeze` must precede `run`. The controller binds the oracle, real corpus/analysis/count snapshots and actual model/source paths. It writes a new inference-admission revision with unchanged coefficients/scaling/selection and new code/model hashes; it performs no fit, weight tuning or heldout rescore. Earlier source/model/report bytes stay preserved. Independent review remains separate from these executions.

```sh
python3.13 evaluations/ai-production/real-world/data-ml/qa_controls.py freeze --out "$QA" --corpus "$ISSUE_CORPUS" --analysis "$ISSUE_ANALYSIS" --counts "$TREND_COUNTS"
python3.13 evaluations/ai-production/real-world/data-ml/qa_controls.py run --out "$QA" --corpus "$ISSUE_CORPUS" --analysis "$ISSUE_ANALYSIS" --counts "$TREND_COUNTS" --forecast-model "$FORECAST_MODEL" --review-model "$REVIEW_MODEL" --source "$TASK_DATA/raw/bike/day.csv"
```
