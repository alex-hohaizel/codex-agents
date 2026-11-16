# Game operations templates

## Evidence card

Finding ID / question / source/query/export hash / time window+timezone / cohort+sample+denominator / platform+build+config / exclusions/data quality / observation / hypothesis / uncertainty / decision / owner.

## Experiment card

Hypothesis / mechanism / treatment+control / eligible cohort / sticky assignment unit / exposure event / primary metric / guardrails / sample+duration+method / privacy scope / known confounders / stop/rollback / authorization / actual result / decision.

## Content release card

Manifest+schema+minimum client / asset/source hashes+licenses / accepted identity baseline / gameplay novelty / generator grammar+seed suite / progression placement / rewards+economy version / UX/localization/audio/haptic map / device budgets / migration+old-client behavior / QA evidence / rollout+stop / receipt.

## Incident card

ID / severity / user impact / affected versions+cohorts / first observed+detected / evidence / owner / authorization scope / mitigation+receipts / recovery proof / financial/save reconciliation / root cause vs hypothesis / follow-up+next action.

## Review table

| Area | Facts and evidence | Risks and unknowns | Next action and owner |
|---|---|---|---|
| Stability/performance | | | |
| Progression/retention | | | |
| Economy/commerce | | | |
| Content/fidelity/audio/haptics | | | |
| Privacy/support | | | |
| Cost/capacity | | | |

## Domain impact record 3.0

Change/observation → accepted rule/entity ID → actual feature/domain → affected scenario/journey → changed decision/expected observable → learning/camera/input/world/actor/progression/reward/commerce/save/analytics dependencies → due gate → proof layer → actual evidence/unknown → owner/closure. Use `liveops-question-catalog.json` for question patterns; do not treat a completed form as measured improvement.

## Populated diagnosis example — not measured

Question `OPS-LEARNING-TRANSFER`: players complete the teaching step but may fail the same mechanic in a new context. Needed: eligible players who actually saw that teaching version, named build/context, assistance/error/dropoff, actual transfer observation and event quality checks. Compare accessibility/unlock visibility before concluding the tool is weak. Outcome: unknown until real records are read; no invented conversion, sample, participant or retention. Proposed repair requires a distinct changed-decision scenario and relevant learning/input/encounter regression.
