# App Atelier local runtime

Supported formats are `app-atelier-profile/1`, `app-atelier-state/1` and `app-atelier-economics/1`. The tools reject other versions. They provide neither an older-format reader nor automatic conversion of results. Format revisions are independent of the toolkit release.

Requires Python 3.9+ standard library and macOS/Linux POSIX `flock`. The tools do not call models, access the network, execute external effects, set up accounts or make payments. The CLI pins actual sources and authority records. It cannot authenticate a person's intent. Read `python3 <actual-skill>/scripts/state.py --help` and the relevant subcommand help before use.

## Project paths

Place `--project ABS` before the subcommand. Use an existing directory. `.appatelier/profile.json` is the imported owner profile and `.appatelier/state.json` is the canonical ledger. The requirement, decision, knowledge, job, artifact, evidence, execution, capability, grant and effect namespaces are ledger keys. Keep versioned product artifacts in ordinary files and register relative paths and hashes.

All put records contain `id`, `source` and `verbatim`. A source identifies the actual message, file or observation. Record affirmative consent only when it exists. The actual `state.py` implementation defines semantic record content and derived hashes. Unspecified fields remain unverified.

## Main commands

- `init --profile FILE` imports the supported `app-atelier-profile/1`, creates state and seeds pending requirements. It preserves existing state and does not grant execution.
- `status` returns read-only profile, pause, pending, unknown and stale status. `context --query TEXT` retrieves records. Read their current sources and dependencies after retrieval.
- `put --kind KIND --record FILE` writes a typed current record and retains prior revisions in history. Create actual outputs and proofs with the relevant tools before registration.
- `subject --kind decision|execution|effect|grant|profile|requirement --record FILE` reports the exact subject and hash. It includes current artifact hashes for effect and decision subjects. It does not create authority.
- `gate --job ID` reports blockers. `start --job ID` records a running state after the gate and does not execute the task. `complete --job ID` requires actual outputs, current proof and fulfilled requirements.
- `phase-check --phase NAME`, `phase-complete --phase NAME` consider due musts and all declared jobs and normalize current `PH-*` phase labels. Omitting `decision_ids` does not bypass profile rules or dependencies.
- `pause --boundary now|after_job|after_phase|after_artifact --target ID --record FILE` accepts `now` without a target or an exact future boundary. `resume --record FILE` needs the actual user request. Reconcile unknown effects first. A future stop does not weaken an active pause.
- `dispatch --effect ID` checks the current grant, capability, hashes and caps and records pending with `executes=false`. The agent then makes one exact authorized call on the host.
- `receipt --effect ID --record FILE` records `provider_ref`, `proof_path` and `succeeded`, `failed` or `unknown` outcome. Failure requires `confirmed_no_effect`. `reconcile --effect ID --record FILE` adds an actual `read_only_status_check=true` to receipt fields. It does not grant replay.
- `amend-profile --profile FILE --record FILE` needs exact user authority covering both old and new subjects. The returned `impact` identifies changed fields and requirements, affected phases and invalidated or carried-forward IDs. Non-operational top-level `metadata`, `annotations`, and `audit_annotation` do not change execution scope. Keep product rules and permissions out of these fields. Validate phase gate and requirement changes against actual dependencies. Unknown fields, global constraints or requirements without a proved impact boundary cause conservative global invalidation. Carry independent bindings only from the prior current profile and preserve history and authority subjects. Earlier stale records stay stale. Amend through the controller rather than writing the raw profile.

## Records

**Requirement** has intent, priority, acceptance, owner, `due_phase` or `phase`, applicable emphasis and applicability, `evidence_ids` and status. A semantic must change needs `change_authority` for the exact subject. Old proofs pin `requirement_hashes` and cannot close the new definition.

**Execution** has `scope`, `phase_ids`, `authority` and `status=current`. Authority includes `actor=user`, source, verbatim text, `subject_sha256` and an affirmative decision. The CLI derives the subject from the actual parameters. Agent construction approval does not grant product execution.

**Decision** has category, scope, question, options, `status=confirmed`, answer, authority and `artifact_ids` when applicable. Optional `requirement_ids` and `job_ids` declare dependency boundaries and are included in the subject when supplied. Categories are direction, concept, design, budget and `release_readiness`. The exact answer and accepted bytes are part of the subject. The decision applies only to its scope, profile and current artifacts. Reassess unbound decisions conservatively after a material requirement change.

**Job** has phase, scope, owner, goal, `execution_id`, lists `depends_on`, `requirement_ids`, `fulfills_requirements`, `artifact_ids`, `evidence_ids`, `decision_ids` and `effect_ids`, `inputs=[{path,sha256}]`, and applicable `human_experiment` and `requires_owner_operations`. A dependent effect needs a known terminal result and current proof. Record experiment metric, threshold, horizon, `budget_usd` and stop before starting. Use the actual phase and intent rather than hiding an operation behind a false flag.

**Artifact** has path and `author_ids`. Supplied `sha256` must match the actual file. Do not use ledger internals as product outputs. **Evidence** has `artifact_ids`, applicable `requirement_ids`, `proof_path`, observer, method, environment, status `pass`, `fail` or `blocked`, and an `independent` boolean. The CLI pins artifact, proof and requirement hashes. An independent observer did not author the artifact.

**Capability** has scope, environment, `effect_types` and an `available` boolean. Record actual verified capability only. **Effect** has type, scope, target, parameters, `artifact_ids`, `spend_usd`, `recurring_usd`, `idempotency_key` and `grant_id`. Current `artifact_hashes` are part of the exact subject. **Grant** has `effect_id`, the effect's `subject_sha256`, `capability_id`, authority for the grant subject, and `status=current`. Changed bytes, parameters, scope or cost cannot reuse the earlier grant.

**Knowledge** has text, confidence, scope, `impact_ids`, source and verbatim text, and pinned inputs where needed. The agent evaluates the content and impact and reopens affected requirements, reviews and jobs. Adding a record cannot establish accuracy or automatically invalidate semantic dependencies. Mark an affected requirement with obsolete semantic intent `status=stale`, then create the targeted repair and a fresh proof. A user must needs a valid decision to change.

## Limits

A change to current artifacts, proof, requirements, decisions or dependencies makes dependent closure stale. Local JSON is not evidence of a person's assent or a provider's actual state. OS locking and atomic replacement protect cooperating local writers. They do not protect against a hostile same-user process with workspace control. Archive a very large ledger in a controlled way while retaining references and access. Keep history intact.

At `start` the job records `input_requirement_hashes` for all declared inputs. Must and emphasized inputs must be current before dependent work. `fulfills_requirements` may be pending at start and must be closed by completion. An open should or explore input does not block completion. It appears in `optional_input_gaps`, and changes to its definition invalidate the pinned job. Admission, completion and freshness use the same semantics. An older running or completed job with assigned requirements and no input snapshot needs targeted repair or reconciliation. Do not invent a missing historical binding.

At `complete` the controller creates `completion_hashes` for outputs and `completion_evidence_hashes` for all accepted proof records. The semantic pin includes observer, independence, method, environment, status, real proof path and hash, artifact/requirement bindings, source, verbatim text and other semantic fields. It excludes only controller bookkeeping `_profile_sha256`, `created_at`, `updated_at` and `recorded_at`. The actual observation timestamp remains meaningful, for example `observed_at`. Subsequent status, dependency and phase checks verify current proof, coverage of each output, any independent-review requirement, and exact agreement with the snapshot. Replacing proof under its earlier ID makes dependent closure stale without invalidating independent jobs. Carrying profile bookkeeping forward does not change the semantic pin. A historical completed job without an evidence snapshot needs a targeted repair with actual proof. Do not fabricate a backdated snapshot.

The director's economic `check_model.py` accepts JSON numbers, decimal strings and Python `Decimal`. It uses bounded base-10 Decimal precision and range before comparisons and ceiling operations. Display uses six places with `ROUND_HALF_EVEN`. `exact_decimal` preserves unrounded decision values. Do not assume provider per-transaction rounding. Include the provider's actual convention in the product model. The result is a calculation from assumptions and does not establish demand or guaranteed income.

## Other tools

`doctor.py [--project ABS] [--skill-root ABS] [--strict]` inventories tools and duplicate sources without reading accounts or secrets. It is available in the root kit and director scripts, and is not assumed to be present in every standalone module.

`check_model.py --example` shows the exact `app-atelier-economics/1` JSON. `--model FILE [--target-profit N]` calculates USD/month scenarios. Include dated assumptions, paying and free cohorts, prices, charges and refunds, and variable, fixed and acquisition costs. The utility applies commission to retained revenue after refunds. Verify actual provider practice and model any difference. For one-time purchases, `paid_users` are current-month newly paid units. Existing active owners need a separate cost cohort. Required scale holds other assumptions fixed and is not demand or revenue evidence. The utility is available in the root kit and director scripts.
