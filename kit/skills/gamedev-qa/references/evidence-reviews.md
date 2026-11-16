# Evidence, defects, and regression coverage

## Case result

Record `case_id`, requirement IDs, scope, baseline/source/build hashes, platform/device/OS, preconditions, scenario, seed and input, expected outcome and design reference, procedure or fault, observed outcome, raw artifact references and hashes, execution actor and time, independent reviewer, verdict, and limitations. Write the actual result after execution and label templates as examples.

## Defect record

Include ID, severity and player impact, requirement IDs, exact failing revision and build, reproduction steps, state and seed, expected design or official rule, actual result, raw screenshot/video/audio/log/profile, repair owner, affected dependency closure, repair revision, retest evidence, and closure. For an audio defect, record the cue, timecode, and triggering condition, such as clipping on `ui.confirm` during a repeated event.

## Evidence requirements

- Hash the exact observed bytes. Review evidence for a new revision before carrying acceptance forward.
- An independent reviewer differs from the artifact author. Record actual work and evidence as well as actor identity.
- Carrying forward evidence from an earlier source or build requires a recorded decision and dependency assessment.
- Distinguish build receipts, test results, listening acceptance, human observations, and market metrics.
- Mark missing evidence `not_tested` or `blocked`.
- Exclude credentials, private keys, raw payment tokens, and personal data from portable evidence.

## Select regression cases

Trace the change through direct dependencies and transitive product effects to the required checks. A font change affects font consumers, layout, localization, and screenshots. An economy table change affects acquisition, saves, offers, analytics, and migration. A collision layer change affects all associated actor and arena contacts. An audio bus change affects every associated cue family, interruption, mute behavior, and device mix.

Retain acceptance for unchanged bytes when dependencies remain unaffected. Investigate unknown impact and expand checks only as the consequences require. The same independent QA actor retests a localized repair. A material redesign needs an updated target or decision and an applicable review.

## Archive and final report

Use the common handoff schema and validator. Include the machine-readable matrix and a short report. Start with the outcome, tested scope, platform and build, strongest evidence, blockers and untested hypotheses, exact repair owner, and next action. Summarize passing tests by the risks they address.

Freeze the accepted package and keep repair work on a separate branch. Send the exact accepted revision to release. When a release candidate changes, assess impact and retest affected claims before accepting the changed bytes.

## Bind domain evidence

For canonical game-model evidence, record exact `domain,stage,modality,proof_path,sha256,observer_id,author_ids,method,observed_at,environment,origin` as defined in `model-format.md`. Connect executed cases to current requirements, rules, and scenarios, and to the observed build, state, and seed. A structural validator checks records and bytes. The reviewer checks the adequacy of actual proof and the expected outcome. A template or document review needs further evidence for any device, human, or live claim. Distinguish authors and reviewers, and simulated results and actual players.

## Freshness and independence

Pin semantic inputs, rule/data/recipe/importer/toolchain/build/configuration versions, and actual evidence type. Follow affected dependencies when an input or relationship changes, and preserve accepted originals. Record actual author, observer, and reviewer IDs and raw outputs. Establish independence from evidence of their actual roles.

Keep the operation witness, production attempt, assembly test, native run, physical observation, human playtest, and live query as separate outputs. An unknown external result carries the job or request ID and stays open for reconciliation before the retry decision.
