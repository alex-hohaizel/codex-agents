# Candidate components: what they do and how to use them

The optional task-memory field has its own [purpose, source paths, triggers, input/output, access limits and recovery card](REAL-WORLD.en.md). It is an additive advanced API contract, not a new installed skill or an accepted cold-context result.

Current rc.3 real-task additions, all34evaluation files, inputs/outputs/consumers/access and recovery are documented separately in [the real-task handbook](REAL-WORLD.en.md). The recorded priority implementation below retains its original source/proof scope.

[Українська](IMPLEMENTED-COMPONENTS.uk.md) · [Implementation status](IMPLEMENTATION.en.md) · [Source cards](implementation-components.json)

This is the implementation overlay for source candidate **1.4.0-rc.2 / core 6.1.0**. The earlier [component catalogue](CURRENT-SYSTEM.en.md) and [helper catalogue](HELPERS.en.md) describe their recorded audit baseline. They remain useful history; this overlay records the additions rather than silently rebinding their old proofs. None of the following files establishes host installation, model accuracy, deployment or owner acceptance.

## 1. Original sources and task continuity

The project keeps its native requirements, decisions, identity and checkpoint. A task packet is a derived view for one executor. The optional `atelier.context-bindings/1` record names one exact project root, 1–40 explicit source files and their SHA-256 hashes, expected requirement IDs/musts and optional literal source-to-requirement excerpts. It is neither another backlog nor a consent store.

For direct skill work, [context_capsule.py](../../../standards/context_capsule.py) reads an explicit native projection, imports supported bound native records and builds or verifies the packet. The input is the projection plus declared local sources; the output is a deterministic capsule with retained source provenance, dependencies, current decisions and deferred work. The next specialist or constructor consumes that packet. Use it when a substantial task is delegated, resumed or needs a declared-source check; a short conversation does not need another file merely to use a skill.

For the panel, [context-bindings.mjs](../../../apps/agent-atelier/server/context-bindings.mjs), [projects.mjs](../../../apps/agent-atelier/server/projects.mjs) and [context.mjs](../../../apps/agent-atelier/server/context.mjs) implement the same declaration contract in JavaScript. The service does not invoke Python as hidden memory infrastructure. It exposes coverage in the workspace and includes it in task preparation.

Required missing/changed sources, another root, omitted/weakened musts, lost declared excerpts and conflicting decision identities block dependent preparation. Explicit `supersedes` IDs choose current decisions while retaining the earlier records; list order and timestamps do not decide authority. An undeclared original or omitted meaning can still escape a declaration check, so independent raw-source reconciliation remains necessary. Existing projects without a declaration remain usable and explicitly unverified. On drift, review current native sources and create a new packet revision; keep the old proof with its original bytes.

The helper uses Python’s standard library and local reads; the service uses its existing Node runtime. Neither creates a vector database or calls a model. RAG remains a separate conditional knowledge-retrieval technique. A semantic index cannot override current native task status, permission or decision records. Read [the full context contract](../../../standards/context-capsule.md) for the exact limits and commands.

## 2. A readable operational workspace

[context-workbench.tsx](../../../apps/agent-atelier/client/src/context-workbench.tsx), [workbench.ts](../../../apps/agent-atelier/client/src/workbench.ts), [App.tsx](../../../apps/agent-atelier/client/src/App.tsx) and [views.tsx](../../../apps/agent-atelier/client/src/views.tsx) consume actual workspace records. They show source checks, readable requirements, current decisions, deferred work, task links and operational project rows. Original source and JSON inspection remain available.

This activates when the user opens a bound project; it grants no new rights. The displayed record status is labelled **Status in source**. A historical source saying “awaiting approval” is preserved as history rather than promoted above a later current decision. Project acceptance is still obtained from the supported native approval record, not a title, response or inferred summary.

Until the matching project workspace is loaded, the UI shows loading or unavailable state with recovery. It does not present an absent object as verified zero sources/requirements. A successful retry clears only its own read error; a newer unrelated task/controller error remains visible. Full mobile navigation includes the existing views, keyboard focus containment, Enter activation and Escape return. Seven locales retain their existing values and receive the new labels.

The source is React/TypeScript/CSS on the existing lockfile, with no new UI framework, font service or paid design dependency. Actual desktop/mobile renders and bounded interactions were inspected against the accepted rich direction. Those observations support the named candidate builds, not every future page, device or task. A mismatch is repaired in the actual view, then the affected source/build/interaction proof is renewed.


The design revision makes the operator work map the normal project's first view. Select a real work/result to inspect evidence and choose a next action; its inspector starts closed. Source documents / Compare changes explicitly opens the complete technical workspace. Native history is loaded on demand, with partial coverage visible. Only a corresponding active runtime job can establish running work; a historical dispatched task cannot. Human profile labels and seven locales remain, with initial Ukrainian UI and saved preferences respected. A source grouping or file count cannot become a delivered-result claim.

The owner rejected8c3a557, then accepted the shown revision6 visual foundation: “Так, цю основу приймаю”. Earlier CI/craft proof remains bound to its old bytes. Actual revision6 service checks passed179/179, with49 client checks, real report/source links, all29 requirements, mobile navigation, seven locale selection and corrected cold/reflow routes observed in their bounded scope. Later helper changes need their own exact checks; visual acceptance does not close the full A26 case or any complete case/adoption gate.

## 3. Large native work histories

[codex.mjs](../../../apps/agent-atelier/server/codex.mjs), [portfolio.mjs](../../../apps/agent-atelier/server/portfolio.mjs) and [api.ts](../../../apps/agent-atelier/client/src/api.ts) separate bounded turn metadata from paginated actual items. This route activates when the public native history adapter supports item paging. Existing full-turn/custom-adapter behavior remains supported.

The input is the selected project/discovery snapshot and observed native thread/item cursor. The output retains work provenance and exposes the remaining cursor, partial coverage or unavailable history. The client merges continuation by native identity without replacing a newer answer or dropping other pages. The interface offers further reading of the observed remaining items. The read-only transport does not gain chat mutation rights.

The transport limit remains in force; oversized item pages shrink within bounds. One item that still exceeds the limit remains an explicit gap. Empty persisted history does not prove that no work ever existed. Cold restart clears ephemeral discovery; reconnect and refresh the supported portfolio before comparing installed/observed-agent hints with a previously populated session. These are supported local reads; they do not schedule a background scan or repair a vendor’s inaccessible history. See [the API contract](../../../apps/agent-atelier/shared/API.md).

## 4. Seven responsibilities within the existing team

[ai-production.md](../../../standards/ai-production.md) provides conditional recipes for DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA and EVALUATION. It is loaded only for the relevant task under its existing integrator. The 35 reusable sources and 12 host roles remain the composition; the profile names are neither seven installed skills nor seven launched workers.

Each recipe starts with the user’s decision and real consumer, restores the native context, checks actual tools/access/cost, chooses sufficient existing methods and states the production and acceptance steps. DATA connects source acquisition to a dependable dataset; ANALYSIS distinguishes reports, verified causes and inferred needs; LLM connects a bounded function to its user journey. PREDICTION checks available-at-time features, splits and honest uncertainty/CPA. ADAPTATION first requires a measured gap and actual resource/serving feasibility. MEDIA preserves masters and checks the actual destination. EVALUATION separates source, function, craft, runtime, independent review and owner acceptance.

These recipes require the actual collector, model, editor, player, runtime or deployment route needed by the task. They create none of those services and do not turn the developer’s Codex login into a commercial product API credential. Existing sufficient native contracts remain usable; a limited helper is not a global ban on separately reviewed native workflows. Missing required capability remains a gap with a concrete handoff.

## 5. Thirteen optional records and their consumers

[ai-production.schema.json](../../../standards/ai-production.schema.json) describes the fixed types below. Each is a derived artifact referenced from the native project ledger. Instantiate only applicable types and their real dependencies. All share exact project identity, an owner, local consumed-file pins and a typed payload; domain additions can be retained in `extensions` without becoming checked semantics.

| Record | When to create it; inputs and useful output | Consumer and actual check boundary |
| --- | --- | --- |
| `SourceContract` | Before controlled collection: source/operation, rights/privacy/schema references, consumer and rate/resource bounds | Collector/data owner; required declarations and pinned local references, not authenticated rights or acquisition |
| `DatasetManifest` | After normalization: source contracts, retained IDs, transform, received/accepted/duplicate/quarantine/excluded counts and coverage | Analysis/training consumer; unique retained IDs and full accounting, with incomplete coverage visible |
| `SplitManifest` | Before fitting/tuning: dataset membership, exclusions, groups, times, feature/label availability and cutoffs | Feature/training/evaluation owners; disjoint complete membership and declared chronology, including train→test with empty validation |
| `FeatureManifest` | When producing predictive inputs: dataset/split, feature sources, fit rows and availability | Training/inference pipeline; training-only preprocessing fit and no declared future feature |
| `PredictionContract` | Before making a prediction: decision, target/unit/horizon, forbidden inputs and applicable CPA semantics | Inference/UI consumer; exclusions and honest zero-acquisition/currency/window policy, not forecast accuracy |
| `WorkflowRun` | During actual work: nodes, attempts, completion IDs, effects, receipts and any bounded retry policy | Existing recovery controller; unfinished/unknown effects cannot be hidden or automatically replayed |
| `EvaluationPlan` | Before comparison: cases/musts, baseline/candidate/rubric, author, proof types and independence need | Evaluator; explicit full denominator and exact consumed source pins |
| `EvaluationReport` | After the check: exact canonical current-plan digest, consumed plan pins, reviewer, all verdicts and observations | Adoption/model/media consumer; old review cannot be rebound to changed plan/rubric/input bytes; no omitted required results or concealed fail/unknown |
| `TrainingRecipe` | Only for justified training: data/split, base/tokenizer/template/license, measured gap, method/config/environment and bounds | Actual trainer; compatible declarations and nonempty training split, not a training service or completed run |
| `ModelBundle` | For delivery: actual weights/tokenizer/signature and applicable adapter members, revisions, evaluation and serving records | Actual loader/serving pipeline; file membership/current evidence binding in the utility’s narrow route, without loading weights or authenticating inference |
| `BatchPlan` | Before a material series: full item/variant matrix, recipe, masters, consumers and cost cap | Actual generation/editing owner; unique requested pairs and pinned references |
| `ItemManifest` | For one result: planned pair/master, actual exports and review/consumer records | Integration/review owner; planned identity and current output/master evidence, not craft or playback certification |
| `GenerationBatch` | To reconcile a series: all attempts, outcomes, unknowns, costs and editing/export/import/QA overheads | Integrator/cost owner; full denominator, output relation, retry/unknown/currency/cap accounting and qualified accepted-unit cost |

## 6. What the read-only checker actually executes

[ai_production.py](../../../standards/ai_production.py) reads explicitly supplied local JSON artifacts and their dependencies, checks its fixed schema and relevant cross-record invariants, hashes bounded regular files and reports the performed checks. It rejects duplicate/nonfinite JSON, unsafe or credential paths, wrong projects, changed/missing pins, temporal leakage, unsafe retries and stale evidence bindings. It uses only Python’s standard library; it does not fetch data, load a model, execute a workflow, render media or spend through a provider.

`schema` emits the matching fixed JSON Schema. `digest` reports canonical identity and shape only; it does not verify pins, dependencies or authority. `check` validates the explicitly supplied record set. An evaluation report consumes every current plan input and binds the entire plan’s canonical digest. A retry declaration needs known failed/rejected state, a failure receipt and pinned bounded policy; dispatched/unknown/successful work cannot request a retry. Actual controllers still enforce operational identity, permissions, idempotency and budgets.

From an installed or generated bundle, use its own `scripts/ai_production.py`; from this repository, use `standards/ai_production.py`. Read `--help` before supplying actual files. Repair an invalid record at its native producer, preserve the old evidence, create a new revision and rerun the affected closure. Do not fabricate a field or rename a model format merely to obtain a pass. `quality_certified`, `authority_authenticated` and `actual_execution_authenticated` stay false. Costs with unknown charges stay unknown, not zero.

The implementation has 38 synthetic boundary tests plus 14 independently repeated adversarial controls for the reviewed bytes. Four independently found P2 defects and a nonfinite JSON gap were repaired before this source admission. These checks establish the stated utility boundaries; no real LoRA, forecast, model serving or media operation follows from them.

## 7. Packaging, inheritance and activation state

The actual review case produced four checked records: `SourceContract`, `DatasetManifest`, `EvaluationPlan`, `EvaluationReport`. The dataset explicitly remains PARTIAL100of5746; the report INCOMPLETE with12 exact label-set agreements and8 disagreements. Controls falsely declaring complete coverage, rebinding the old plan and using a wrong project were blocked. Private/raw inputs were unchanged. This is actual declared-record checking, not execution or quality authority.

The [host-profile installer](../../../scripts/install_host_profile.py) recognizes reviewed current and historical managed blocks, preserves outside text, and blocks unknown customized content inside the managed block. Its15 tests passed. The actual read-only audit covered13 rows: one planned managed-block change and12 unchanged role files. No host application follows from that audit. Reconcile a customized block before any later admitted apply; do not overwrite it as an upgrade shortcut.

[materialize_standards.py](../../../scripts/materialize_standards.py) copies seven reviewed masters into 33 core bundles and the existing optional Orchestrator: 238 exact copies. The bundles are self-contained when the authoring repository or constructor is absent. New 6.1 generated children carry 15 common resources and seven local reference links; supported 6.0 children retain twelve and 5.x children eight. The constructor/installer checks distinguish these versions rather than retrospectively certifying old packages.

The maintenance skill applies preservation, evidence and publication rules without copying an irrelevant generation runtime. Its version is separate. The twelve role configurations retain their models and restrictions. Source materialization, installer fixtures, an actual apply journal, host discovery, bounded execution and project adoption remain separate facts. Preserve unknown edits and the native formats; use [the 6.1 migration](../../../releases/migrations/6.1.0.md) and actual before-copies for an admitted update or rollback.

## 8. Scoped writes without changing native authority

An admitted local write task may create product artifacts while its native requirements, settings and history remain readable and protected. [permissions.mjs](../../../apps/agent-atelier/server/permissions.mjs) inventories existing native authority, builds exact read exceptions and recursive case-aware deny rules for nine protected metadata names. [context.mjs](../../../apps/agent-atelier/server/context.mjs) binds the inventory to preparation; [codex.mjs](../../../apps/agent-atelier/server/codex.mjs) rechecks it before dispatch. The inputs are the exact selected root, allowed relative artifact paths and filesystem snapshot; the output is the bounded native permission profile or a visible capability error. The existing adapter consumes it; it adds no controller or background process.

The reproduced P1 was repaired and retested on the actual macOS/Codex0.166 route. Native reads and normal admitted writes remained available; child/root metadata writes, future paths, uppercase names and late aliases were blocked in the checked scenarios. Ninety-three filesystem readbacks and the [dedicated tests](../../../apps/agent-atelier/tests/server/nested-permissions.test.mjs) support that bounded result. Final service tests passed159/159. A separate source reviewer found no new concrete P1/P2 within that review; full owner/system acceptance remains open. Exact checked source hashes are in the machine source card.

Inventory is limited to200000 entries and128 levels. Ambiguity, protected symlinks, unreadable traversal and unsupported relative literal glob characters block dispatch. Choose a supported narrower artifact directory or reconcile the actual source, then reprepare; do not bypass the check. The pre-turn comparison is not an atomic fence against an external concurrent writer. The synthetic OS probe used local canaries without network, provider/model calls or real native-state mutation. Another OS, CLI parser or native schema needs its corresponding evidence.

The current state is a prepared source candidate with bounded actual context/panel observations, independent source/craft review and the [real feedback analysis](REVIEW-STUDY.en.md). Full R01–R27/A01–A29 acceptance, relevant remaining model/media/provider/device cases, installation, final release and owner acceptance remain open where unproved. WORK remains deferred. No component silently trades an existing working feature for a new one.


## 9. Source-declared current checkpoint

[projects.mjs](../../../apps/agent-atelier/server/projects.mjs) adds current_checkpoint without replacing the native project phase or state format. It activates only when an explicit project binding contains exactly one required source with role checkpoint, its current bytes match all declared/loaded pins and its bounded JSON shape is supported. The input is that source's phase, completed and in_progress text arrays and next text. The output retains those values with source_ref, source_sha256 and status declared. The operator workspace consumes this view; it may present the source's next action without turning it into permission or acceptance.

Absent, optional, wrong-role, multiple, changed or unsupported checkpoint declarations return null with a visible nonblocking projection gap. The ordinary native workflow stays usable; an existing required-source drift issue retains its own blocking effect. Text is redacted through the existing privacy route. The projection needs only existing local service reads, no extra API, framework or cost. Repair by reconciling the actual native checkpoint and explicit binding, then reread; never infer a current stage from a convenient filename or old proposal.

The [seven focused cases](../../../apps/agent-atelier/tests/server/checkpoint-projection.test.mjs) passed with13 existing context cases:20/20 for that subset. The actual first slice read16 sources/29 requirements and showed five source-declared work records, four completed and one current, with zero active runtime jobs. These are declarations, not verified runtime completions or owner-accepted deliverables;250 inventoried files are not250 results. Revision6 has its own bounded full-service/browser observations; later helper/data changes require new applicable proof. The current source snapshot has17 bound sources/29 requirements and7 declared work records,6completed/1compatibleupdateinprogress; source declarations are not runtime or accepted deliverables.


## 10. What the actual design failure changes for every applicable UI task

The owner-rejected Atelier screen exposed a reusable failure: the code pane and visual shell of the rich reference were copied while the operator's real work remained secondary. The shared [production-quality.md](../../../standards/production-quality.md) and UI profile in [production-profiles.json](../../../standards/production-profiles.json) now require an intended-user demonstration: identify the outcome, actual work/result, attention and useful next action; select a record, read an understandable result/proof and continue within the correct scope. A promotional code pane or map must be translated into the current task's working mechanism. Irrelevant technical hierarchy, repeated brief text, invented edges/progress or a file-count-as-results display fails this test.

The rule activates when a loaded skill creates or reviews a human interface and proves its representative slice. Its inputs are the actual task, intended user, accepted reference and real state; its output is a task-specific view and observable journey, consumed by the integrator and independent reviewer. The supported materializer copied these current rules into the existing33 core bundles and optional orchestrator. This is shared behavior guidance, not a new framework, role or background service; no new access or spending is granted.

Exact source hashes and their materialization are inspectable in the candidate source card. A loaded instruction cannot guarantee model behavior, certify a design or retrospectively overturn rejection of older bytes. Actual new UI evidence and owner acceptance remain separate. Repair a failed representative view by changing its composition/mechanism on real records, retain accepted functionality/identity, then rerender and repeat the intended-user journey.


## 11. Current work must survive a source update

[workbench.ts](../../../apps/agent-atelier/client/src/workbench.ts) merges the current workspace and optionally read native history. It uses actual source/native/service identifiers, not a mutable task title, to correlate work where identity exists. Source-revision mismatches or missing current provenance stay in history instead of recreating an obsolete active task. Cached history may add correlated transcript/evidence, but cannot overwrite current status, owner review or authority.

The inputs are the selected current workspace, source pins and supported history records; the output is a traceable operator work map, with current versus historical observations kept distinct. This uses existing local records and adds no service or provider cost. Helper7 had53 client checks and a5/5 replay of actual earlier/current source snapshots. Helper8 repairs prepared/paused service-origin correlation and history duplication; final source8 passed184/184 service checks,54 client plus130 server. A fresh actual read-only source8 task completed using a candidate source snapshot; independent response review passed9/9 for the exact bound-source continuation; exact Git/CI/admission remains pending. This is not host installation or discovery. If correlation is uncertain, retain history with its gap; do not guess an alias from a similar objective or claim the old activity is current. Layout acceptance only carries over unchanged visual dependencies.

## 12. Compatible update preflight and known predecessors

The [optional-source controller](../../../apps/agent-atelier/server/optional_updates.mjs) uses [UPDATE_BASELINES.json](../../../optional-skills/UPDATE_BASELINES.json) to recognize exact reusable predecessors. The installed optional orchestrator1.1.0 matched the canonical Git predecessor with40 files, including bytes and modes. Its previous unknown-source conflict was caused by a missing known predecessor entry, not local edits. Restoring that exact canonical entry made the1.1.0→1.2.0 preview ready; unknown edits still block overwrite.

The consumer is the reviewed update preview/apply/verify route. It reads exact installed/source snapshots and preservation facts; a ready preview is not apply, installation/discovery or behavior proof. The current core33 plan has no blockers. The host audit has13 rows: one managed-block proposal and12 role files unchanged. No host apply is inferred. Maintenance1.1 source exists but was not installed, and that absence is preserved rather than inventing an extra installation.

A bounded context/design/panel update needs its own affected-invariant ledger, closed material defects, fresh exact-source read-only task and CI. At this checkpoint admission is not yet granted; full17-capability/29-case acceptance remains open even if a narrower update is later admitted. Retain backups, identity, settings and unknown edits; use the exact source-target plan, then verify actual applied bytes and discovery separately.

## Compatible execution-input custody

[skills.mjs](../../../apps/agent-atelier/server/skills.mjs) retains canonical manifests/private archives and prepares a separate immutable selected-input namespace; [retention.mjs](../../../apps/agent-atelier/server/retention.mjs) removes only explicitly reviewed task-owned copies. Complete task/input ownership and exact bytes govern dispatch; true legacy capsules are preserved. Purpose, trigger, input/output, consumer, access, generic tests, limits and recovery are in the [transport card](REAL-WORLD.en.md). STORE JSON backup excludes archive payload files. Initial/R2/R3 source-only trials remain NOT_ADMITTED; R4 native retests are pending.
