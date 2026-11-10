# Observed data/model results — 2026-11-10

This records actual bounded execution, not whole-system acceptance or a new model framework. Raw inputs, review text, source-author buckets, per-record predictions, weights and detailed receipts remain private. Reproduction and source citations are in [README.en.md](README.en.md); methods were fixed in [STUDY.json](STUDY.json) before fitting.

## Data and parsing

Two official UCI archives were actually downloaded:873714 bytes in two requests. Four additional public GitHub requests retrieved retrospective issue-count snapshots. No packages, model weights, paid APIs or new services were acquired. The existing 100 issue sample was reused locally.

The controlled source transported100 actual public issue records plus one duplicate and one declared malformed control. Crash-before-cursor exit97 left0 committed rows and0 pages. Recovery accepted100 unique records from102 received, retained1 duplicate/1 quarantine accounting, committed4 pages, and made no request on completed replay. Source drift, missing page, login HTML, repeated cursor and off-origin redirect failed visibly. Both static HTML and actual Chrome-rendered JavaScript DOM yielded all100 records; selector/unit/login/incomplete HTML controls were rejected. These are controlled transports, not live-site scraping certification.

## Feedback needs and trends

Actual TF-IDF clustering kept every denominator: at cosine thresholds0.18/0.25/0.32 the sample produced12/13/6 groups and31/67/88 noise records. Mean pair-assignment Jaccard across12 deterministic80% resamples was0.533/0.696/0.594. This moderate sensitivity argues for source inspection and a human theme review, not automatic feature prioritization.98 source-author groups are not98 verified people.

At threshold0.25, exploratory neighborhoods included sandbox/socket execution, command-policy rejection, usage allowances, stuck queues, account/project switching, scrolling, pairing and remote connections. One neighborhood also retained feedback-dialog boilerplate: lexical grouping alone is insufficient semantic validation. Useful next work is to inspect linked failures, separate submission boilerplate from the underlying problem, and validate themes with users before deciding roadmap priority. No measured semantic gain is attributed to the new conditional profile.

Public GitHub search returned22 context-labelled reports among1026 app-labelled issues created19–25 October2026, then18 among850 created26 October–1 November:2.144% → 2.118%, a change of-0.027percentage points. These current-label retrospective counts are essentially flat descriptive shares, not evidence that needs are rising or falling. The original26 hour/latest100 sample abstains from a historical trend claim. Neither sample covers all users, feedback channels or historical label states.

## Human-labelled multilingual review classification

[UCI Paper Reviews](https://archive.ics.uci.edu/dataset/410/paper+reviews) contained405 reviews across172 papers.399 nonempty reviews were retained;6 empty reviews were quarantined. Group splits contained258 training,70 validation and71held-out rows. The holdout was70 Spanish and1 English review; a general English-quality claim is unsupported. Human labels represent perceived orientation, distinct from original reviewer evaluation or confirmed intent.

| Held-out71 reviews | Training-majority baseline | Validation-selected NB candidate |
| --- | ---: | ---: |
| Accuracy |39.44%|32.39%|
| Mean absolute error on -2..2 scale |0.8592|0.8310|
| Macro-F1 over all five labels |0.1131|0.1822|

The candidate is **rejected for default adoption** because accuracy fell. Better F1/MAE does not compensate for that protected loss. The actual API consumer retains the baseline and flags human review; it does not quietly ship the weaker candidate. Raw NB probabilities are uncalibrated. The one held-out English example was wrong; this is one observation, not an English-accuracy estimate. Better training data/representation would need a new study and untouched holdout, rather than tuning against these results.

## Actual operational-demand model

[UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) supplied731 daily2011–2012 observations. Calendar and available lagged counts were used with declared two-day label delay. The final chronological holdout contained92 days,1October–31December2012. Tuning selected ridge alpha 0.1 before this holdout.

| Same92 holdout days | Fitted weekday mean | Seasonal lag7 | Ridge candidate |
| --- | ---: | ---: | ---: |
| MAE, rentals/day |1726.36|1457.59|1132.85|
| RMSE, rentals/day |2030.38|2047.17|1628.20|
| Empirical interval coverage |97.83%|70.65%|78.26%|

The ridge point error is22.28% lower than seasonal lag7 on this historical slice. This supports a small fitted model for this task without adding a framework; it is not contemporary business accuracy or CPA forecasting. Ridge MAE was1038.41on66 weekdays and1372.57on26 weekend days. Nominal90% residual intervals covered72/92 days, **so that interval is not admitted for90% coverage**. The consumer exposes the measured deficit and requires human review. Future labels, missing lag history and out-of-period dates are rejected or abstain; no holdout-driven retuning occurred.

## Delivery, reuse and remaining gates

The actual10 member JSON/source/signature/model-card bundle was copied to its own private directory. Its copied fresh-process authenticated loopback adapter produced exactly matching forecast points and respected the rejected-review fallback. Authentication, origin, schema, duplicate fields, tool/path payloads, byte cap and request 25/rate cap were tested with actual HTTP. Changed delivered weights were rejected by their pinned manifest. The process and ephemeral key were removed. This is same-Mac/Python evidence, not deployment, cross-device validation or paying users.

Actual isolated source-derived cache/features/job/proof consumers all rejected a changed or revoked source and changed proof bytes. No original product or source state was altered. Source injection stayed data with no provider or external effect.

**CPA remains a real data gate:** no representative pre-launch campaign features and spend/conversion outcomes were available. Actual refusal and declared synthetic zero-conversion/leakage controls prove a boundary, not a fitted CPA model. LoRA/LLM adaptation is separately owned and not claimed from NB. Eleven generic boundary tests supplement these actual operations; they are not substitute business evidence. Independent review, portfolio/UI consumption, affected preservation, owner acceptance and original 29-case closure remain separate decisions.

## Subsequent independent findings and actual boundary closure

The original fit/score and ten-member delivery records above remain historical. A later independent import-shadow finding led to an eleven-member format that rejects unlisted modules, symlinks and bytecode directories before execution; copied Python runs with `-E -B`. Actual isolated `json.py`/`__pycache__`/symlink negatives were rejected without execution. The original owned bundle was not observed compromised.

The A06 oracle was frozen before running. Three controlled lexical theme pairs remained stable with a retained noise outlier. A declared90-copy single-author burst changed raw alpha share from 30% to 96/110 while author-weighted share remained 30%; 20→10 cohort coverage caused abstention. These explicit synthetic controls bind the separate actual 100-issue clustering report and real two-week counts, without becoming new real needs/accuracy evidence.

The actual copied-model HTTP consumer now checks its real source→model→signature before inference. Valid input produced the same forecast; changing actual copied source bytes and an isolated project-test withdrawal each returned HTTP 409 with zero additional model invocations. Restoring the source restored the same prediction. A seven-zero-lag counterfactual reached the actual predictor and abstained for unsupported intermittent history. Source/model coefficients and fit selection stayed unchanged in a new pinned inference-admission revision; no fitting or heldout retuning occurred. Fourteen generic boundary tests passed. Independent review and case acceptance remain separate.
