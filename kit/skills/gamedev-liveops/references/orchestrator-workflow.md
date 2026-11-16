# Local Game Atelier orchestration workflow

Read the [maturity, competence, and authority index](v4/index.md) for current Game Model semantics. GA4-P1/D1/D2 supplement GA3/UA26 and earlier IDs. Complete concepts require C1 and production handoff requires T. Collect actual evidence at each gate. Preserve historical sources and approvals. Apply R6 profiles, scale, style, camera, and one-time kits only where accepted.

Use this implementation reference when the local workflow runtime is part of the project. The owner states goals in ordinary language. The agent resolves the actual skill, prepares records, and invokes tools. `atelier.py` maintains structured state and validates gates. The supported runtime uses the Python 3 standard library and POSIX `flock` on Linux and macOS. Verify any other host or transfer the work to a compatible environment.

## 1. Recover intent and current project

Read the project `AGENTS.md`, canonical state and decisions and requirements, handoff, accepted originals, and the [experience contract](experience-contract.md). Preserve the exact current user source and determine whether this is `new_project`, `intake`, `stage`, `research`, `feature`, `incident`, or `resume`. Select exact stage, scope, and operation. `assets/stage-catalog.json` gives the role, inputs, outputs, decisions, capabilities, gaps, and return routes. Ask about consequential ambiguity in ordinary language.

Distinguish saving a favorite, continuing or terminating the search, selecting a production concept, and changing workflow. Resume only the project and scope actually authorized. Derive material defaults from the current game. See the [retained historical examples](historical-project-profiles.md).

## 2. Minimal local workflow

Resolve the actual skill directory from the current host. Read `scripts/atelier.py --help` and `assets/runtime-records.json`. Set `ATELIER` and `PROJECT` to the actual absolute paths before adapting these examples.

```bash
python3 "$ATELIER" project-init "$PROJECT" --project-id my-game
python3 "$ATELIER" intake "$PROJECT" --source /absolute/path/original.zip --record provenance.json
python3 "$ATELIER" route "$PROJECT" --intent intent.json
python3 "$ATELIER" ledger "$PROJECT" --kind requirement --record requirement.json
python3 "$ATELIER" task "$PROJECT" --record task.json
python3 "$ATELIER" context "$PROJECT" --stage concepts
python3 "$ATELIER" readiness "$PROJECT" --task TASK-CONCEPT
python3 "$ATELIER" start "$PROJECT" --task TASK-CONCEPT
```

Run `project-init` only for a new sidecar. Preserve existing state. `intake` checks safe paths, size, and bytes, carries originals and lineage, and leaves imported scripts inert. Review actual semantics, rights, and versions. After starting, read the assigned skill and perform its actual work. Record real files and evidence.

```bash
python3 "$ATELIER" artifact "$PROJECT" --record artifact.json
python3 "$ATELIER" evidence "$PROJECT" --record evidence.json
python3 "$ATELIER" ledger "$PROJECT" --kind requirement --record closed-requirement.json
python3 "$ATELIER" complete "$PROJECT" --task TASK-CONCEPT --evidence EV-CONCEPT
python3 "$ATELIER" brief "$PROJECT"
```

A task records owner, skill, goal, scope and dependencies, due requirements and decisions, evidence, capabilities and types, outputs, and stop. `fulfills_requirements` allows work on an open must. Completion requires actual closure. Distinguish author checks and independent reviews. Exit 0 signifies a successful read or record, 1 a blocked gate or invalid handoff, and 2 an invalid request. Evaluate artistic quality and store outcomes separately.

`required_modalities` uses the evidence registry `visual`, `audio`, `haptic`, `play`, `device`, `build`, `document`, `external_receipt`. Unsupported values block registration and existing unsupported tasks fail readiness, start and complete. For a local simulation, record `document` with an accurate method and source. Evidence for play, device, and actual native builds is separate.

Change unsupported modality labels of an existing planned or running task only with `reconcile-task-modalities PROJECT --record correction.json`. Read current `task_token` and `task_status` with readiness and use this shape:

```json
{
  "id": "TASK-SYSTEMS-SPIKE",
  "expected_task_token": "<exact current task_token from readiness>",
  "expected_status": "running",
  "modality_replacements": {"simulation": ["document"]},
  "source": "<actual original task and observed proof source>",
  "reason": "<why these supported modalities truthfully represent the required proof>"
}
```

The mapping covers exactly every unsupported label with nonempty supported replacements. Preserve existing supported requirements, independent review, outputs, goal and scope and authority, dependencies, start state, pause, and effects. The command rejects unrelated fields. Completed or stale tasks, mismatched token or state, unresolved integrity, and associated pending or unknown effects block correction. This command only journals an exact before and after and reopening of affected acceptance. It preserves activity and effects. Run readiness again. Use existing proof only after scope, coverage, and independence checks. Obtain a material decision before changing a product proof promise.

## 3. Resolve material decisions

For a dependent choice, provide exact unknown and consequence, two or three feasible options with effects, recommendation, exact scope and input hashes, and independent work that can continue. Choose an engine after actual platform, art, device, and physics feasibility. Handle reversible details within scope and import existing authority from its source.

`decision --record` creates a pending decision. `confirm --id --choice --scope --decision-revision --project-revision --authority` records the actual answer with current revisions. Canonical IDs bind `canonical_ref` and SHA. The sidecar preserves that authority. For an approved effect, use `approval:{option:"approve",effects:["upload"],artifact_ids:["ART-ID"]}` with actual values and pinned hashes. A denied decision grants no authority. For an approved master, use `effects:["master"]`, exact `approved_sha256`, and scope. Give a derivative a distinct ID. For production, record search closure and actual concept selection. `saved_only` preserves favorites. `full_concepts` closes C1 candidates in `stage=concepts` before production selection. Preserve the matching task's source, scope, and operation. A request for `full_concepts` requires deeper delivery than `visual_previews`.

## 4. Update knowledge and context

`ledger --kind knowledge --record` consumes `source`, `verbatim`, `text`, `scope`, `confidence`, `stages`, `impact_ids`, and `impact_reason`. Before a job, `context` and `readiness` reconcile knowledge, canonical files, artifact and evidence hashes, and suite lock. Verify semantic impact. An accessibility change may affect controls, UI, audio and haptics, and economy. Preserve musts and link specifications to source and evidence.

The runtime lock pins executable Python and normative resources in `assets/suite-shared-paths.json`. Stage-local guides, `SKILL.md`, and UI use separate `observed_suite_sources` provenance. For changed executable or shared contracts, perform impact review. Use `refresh --accept-suite-update --authority REVIEW_SOURCE [--impact ID]` to record an actual review. Carry valid authority through semantically unchanged corrections. Open impacted IDs and proof when semantics change. State, journal, and checkpoint live in `.gameatelier/orchestrator`. Preserve canonical source files. `context --query` uses structured and lexical retrieval over dependencies. Add retrieval infrastructure only for a measured need with a migration and tests.

Use `independent_review_required:true` for tasks requiring independent judgment. Mark bounded author observations as self-check. Accepted stage checks use the same stage or stages or scope selectors as readiness. When stage records exist, pin current `stage_context_snapshot` from `context --stage STAGE --scope SCOPE` to optional `manifest.project_context`. Update actual package records, reviews, and snapshot after context changes. Historical handoff 1.0.0 packages with empty ledgers remain structurally compatible. Verify current requirements from current proof.

## 5. External action and unknown result

Prepare actual reviewable artifacts, a task and intended action, and exact account, channel, build, prices, and data. Verify capability and authorization. Obtain missing material authorization for the prepared scope. Record the action and decision and start the task. Use `dispatch --id --project-revision` to record pending before the invocation. Invoke the actual external tool once and immediately record `receipt --outcome succeeded|failed|unknown --record` with actual provider evidence. The agent performs the invocation outside the local state tool.

For pending or unknown results, use read-only provider status before deciding on a retry. Close unknown outcomes with actual evidence and `reconciled=true`. Use provider idempotency or deduplication where supported. Exclude secrets from records, archives, and chat.

## 6. Pause and resume

`pause --when now` stops work gates. `--when artifact --target ART-ID` stops after that exact final or reference artifact. `--when stage --target STAGE` stops after the same project's accepted stage check. For a stop after images, use the actual artifact boundary. Observe the stop before future dependent work.

Leave a readable checkpoint with completed, current and pending work, questions and jobs and effects, stopping point, next action, input and toolkit versions, and return. `resume` reconciles state and retains completed work and material blockers. A safe evidence or receipt write can finish after pause. A new job must wait for authorized resumption.

## 7. Transfer an unavailable operation

`handoff --record` records a readable checkpoint. Include ID, actual environment, absolute `working_path`, argv, numbered `launch_steps`, `expected_result`, absolute `return_path`, `return_instructions`, scope, and `missing_capability`. Prepare the real portable package separately and verify it with `pipeline.py`.

Tell the recipient which project and files to use, exact action, expected output, and how to return it. Give only the blocked step for MFA, owner signature, or unavailable API. Complete the preparation already authorized. On return, verify bytes and hashes and provider state before continuing within scope.

## 8. Extend released games within scope

Start an incident with production build, telemetry, reproduction, and authority, then route to affected design, assets, build, QA, or release. Preserve accepted art, controls, sound, progression, and economy. A material deviation needs its own decision. Recheck affected gates. Verify that authorized recurring monitoring is actually scheduled before reporting it as active.

## Typed reviews before concept selection

Use QA `design_review` for C1 and `contract_review` for domain contracts. Carry exact source, scope, and operation. A task with `work_class=review` can precede production choice and excludes `external_actions`. Full-stage QA, build and release, and `production` use their respective authority and gates.

For one complete C1 candidate, use concepts `game_model.acceptance_scope=candidate_completion`, exact `scope_ref` and `scope_description`, complete C1 rules, and due evidence. Full selected concept handoff and production remain separate.

## Explicit workflow-state upgrade

Skill installation preserves product state and saves. For runtime schema 2.0.0, use the current `WORKFLOW_UPGRADE_FROM` declaration in `scripts/atelier.py`. The controller determines which source formats it can adopt. Run `workflow-upgrade PROJECT` for a read-only preview with `source_state_sha256`, `target_suite_sha256`, pause, and unsettled effects. Preserve state when no path is supported.

After actual review run `workflow-upgrade PROJECT --apply --expected-state-hash SOURCE_SHA --target-suite-hash TARGET_SHA --authority ACTUAL_REVIEW_SOURCE [--impact ID]` using exact hashes from the latest preview. Apply verifies journal and snapshot and both endpoints, preserves an exact backup, and adds a journal receipt. Unsupported schemas are rejected. Repeating the same receipt is a no-op. A changed input needs a fresh preview.

The operation preserves originals, IDs, decisions, favorites, pause, pending and unknown effects, and history. It neither executes game code nor retries effects. Keep prior authority bound to its proof. Reviewed impact IDs and affected closure become stale. Capture changes observed during source reconciliation. Preserve historical stage checks and use actual evidence for the current toolkit. After apply, check context and readiness of the exact next task. Resume separately if authorized.

Completion evidence must match task stage and scope. Project-scope evidence can apply to a bounded task. Candidate evidence applies to its own candidate. QA can declare `stages:["qa","concepts"]` when actual review supports both. Primary `stage` always applies. Input `required_evidence` remains a dependency with its original claims. Verify the same applicability for requirements and stage acceptance, including restored native records. Bind observations to their actual scope.

Canonical links keep original full-file `canonical_sha256`, exact `canonical_record_sha256` and `canonical_envelope_sha256`. `canonical_observed_sha256` records the latest observed source. With a recognized items or named container, modifying a neighboring record preserves unchanged evidence. Envelope, row, or declared `depends_on` changes invalidate affected work. Reconcile unknown shapes, fields, or prior links without fragment pins conservatively. Keep missing canonical dependencies blocked. Preserve original canonical files.
