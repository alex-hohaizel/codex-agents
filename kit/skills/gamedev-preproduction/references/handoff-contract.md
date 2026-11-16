# Stage handoff, schema 1.0.0

Read [maturity, competences, and authority](v4/index.md) before the applicable domain sections. GA4-P1/D1/D2 supplement GA3/UA26 and the earlier IDs. Every complete concept requires C1, and a production handoff requires T. The responsible stage supplies actual evidence. Preserve historical sources and approvals. The R6 profiles, scale, style, camera, and one-time kit are specific to their approved scope.

## Canonical project and portable package

The source of truth is one product Git repository containing `.gameatelier/{state,decisions,requirements,toolchain,capabilities,sync-lock}.json`, `docs/`, `game/`, `assets/`, `tests/`, and `artifacts/`. Use LFS or object storage for large binaries when available, with pinned hashes and an executable download and import procedure. Keep project authority in that repository. Avoid duplicating the product repository in Library. Transfer an exact archive of the required snapshot to Work. Exclude secrets, signing keys, production tokens, and user data from packages.

A handoff is an independent, portable directory containing `START_HERE.md`, `manifest.json`, `records/{requirements,decisions,reviews,claims}.json`, and the required files under `studio/`, `specs/`, `data/`, `assets/`, `source/`, `builds/`, `evidence/`, and `reports/`. Include only real files. Carry required unchanged studio masters, licenses, identifiers, product IDs, fonts, and contracts into each dependent package without copying upstream history recursively. `studio_identity` references the actual identity JSON. Public legal and account fields may remain pending during design. Verify them at release.

The manifest records `schema_version`, `suite_version`, `toolkit_version`, `package_id`, `project_id`, `stage`, `revision`, `stage_status`, `upstream` package ID/hash/schema, and `artifacts`. Each artifact contains `id`, `path`, `kind`, `status` (`draft`, `final`, or `reference`), `author_ids`, `depends_on`, and `sha256`. `seal` inventories files, preserves metadata for existing paths, and updates hashes. The author must classify new artifacts that receive draft/unknown. The manifest excludes itself from the inventory hashes. Records and `START_HERE.md` are included. Editing a sealed source requires a new revision and renewed review.

`requirements.json` is an object with `items` containing `id`, `source`, `priority`, `owner`, `status` (`pending`, `met`, `blocked`, or `not_applicable`), `acceptance`, `artifact_ids`, `evidence_ids`, and `rationale`. Supply a domain justification for `not_applicable`. Track build requirements at research without claiming they have been met.

`decisions.json` contains `items` with `id`, `question`, `material`, `status` (`pending`, `confirmed`, or `superseded`), `answer`, `authority_ref`, and `scope`. A critical pending decision blocks acceptance of dependent scope. `authority_ref` identifies the exact owner's answer or applicable policy.

The minimum material decision IDs are `DEC-BRAND` at every stage, `DEC-PLATFORMS` and `DEC-CONCEPT` for accepted concepts and later stages, and `DEC-ENGINE` and `DEC-MONETIZATION` for accepted preproduction and later stages. `init` creates them as pending. Concept exploration can proceed while platform and concept are open. An accepted handoff for dependent implementation requires answers. Add any other material decisions required by the project.

`reviews.json` has `items` with `id`, `reviewer_id`, `artifact_ids`, `status` (`pass`, `fail`, or `pending`), `evidence_ids`, and `notes`. Bind the review through the `artifact_hashes` object. `dependency_hashes` contains hashes for all transitive `depends_on` artifacts, and `evidence_hashes` for all `evidence_ids`. Changing a dependency or evidence invalidates the previous pass even when the reviewed file's bytes match. An independent reviewer is absent from `author_ids` for reviewed artifacts. `claims.json` records `items` with `id`, `claim`, `status` (`hypothesis`, `observed`, or `blocked`), `evidence_ids`, `evidence_hashes`, `method`, and `limitations`. Pin the evidence hashes for each observed claim. Structural validation establishes reference and hash consistency. Check the truth of a claim against its actual evidence.

## Stage acceptance evidence

A draft may contain partial work. Full-stage acceptance requires these artifact kinds in `final` or `reference` status, local requirements `met` or `not_applicable`, resolved material decisions, and an independent passing review of final artifacts.

| Stage | Minimum kinds in addition to records and START_HERE |
|---|---|
| studio | studio_identity, brand_master, brand_rules, setup_runbook, rights_ledger |
| concepts | studio_identity, concept_comparison, selected_concept, progression_model, economy_model, visual_baseline, validation_plan |
| preproduction | studio_identity, gdd, tdd, interaction_atlas, progression_model, economy_model, fidelity_spec, asset_plan, audio_design, test_plan |
| assets | studio_identity, editable_sources, runtime_exports, asset_registry, rights_ledger, visual_comparison, audio_audition, import_receipt |
| build | studio_identity, source_snapshot, toolchain_lock, build_receipt, native_artifact, implementation_coverage, save_migration |
| qa | studio_identity, test_report, device_matrix, fidelity_report, economy_report, defects, release_recommendation |
| release | studio_identity, release_manifest, store_metadata, privacy_inventory, purchase_validation, rollback_plan, operator_runbook |
| liveops | studio_identity, telemetry_plan, support_runbook, content_cadence, experiment_plan, incident_runbook |

These kinds are the machine-readable minimum. Complete the stage's domain checks, including Android/iOS output against decisions, toolchain, and build receipts. A simulator artifact can fulfill `native_artifact` within simulator scope only. Device/store readiness requires corresponding evidence. A browser mockup establishes browser behavior. An audio audition establishes the tested material. Complete all additional production-audio checks before claiming its acceptance.

## Commands

Replace `<SKILL_DIR>` with the active skill directory resolved from Codex's available skills. Use the path for the current installation.

```bash
python3 <SKILL_DIR>/scripts/pipeline.py init ./handoff --stage concepts --project-id my-game
python3 <SKILL_DIR>/scripts/pipeline.py seal ./handoff
python3 <SKILL_DIR>/scripts/pipeline.py verify ./handoff
python3 <SKILL_DIR>/scripts/pipeline.py verify ./handoff --require-accepted
python3 <SKILL_DIR>/scripts/pipeline.py impact ./handoff --changed ART-0001
python3 <SKILL_DIR>/scripts/pipeline.py pack ./handoff --output ./handoff.zip
```

`init` creates a draft. `verify` accepts a directory or ZIP and returns a nonzero status for checksum errors, unsafe paths, broken references, self-review, or stale review. `--require-accepted` also checks the stage minimum and blockers. `pack` verifies then archives the sealed snapshot. Check the stage status before dependent work because drafts can be packed. Inspect and authorize scripts from incoming ZIPs before executing them.

## Intake and resumption

1. Verify the supported schema/protocol, exact toolkit marker, project ID, bytes, and `stage_status`. Reject an unsupported format without editing the original. Recover actual requirements, decisions, and product artifacts to construct a current package. Review the recovered evidence for current acceptance.
2. Identify accepted outputs and the choices or resources still pending. R06 recommendation diagnostics leave the choice of production concept open.
3. Plan the next scope and trace requirement to specification and data, asset and source, runtime, evidence, and release.
4. For an upstream defect, record the issue ID, current hashes, reproduction, affected dependency IDs, and proposed owner. Fix the source, advance its revision, and invalidate transitive evidence.
5. Deliver the archive and readable `START_HERE.md` with the exact next command, skill, and environment, known blockers, and the local verification format. Relative links must resolve in the snapshot.

## Current project context

The handoff's `schema_version` and `suite_version` are **1.0.0**. `toolkit_version` uses the compatibility marker in `scripts/pipeline.py`, currently **6.0.0**. Include `records/intent-lock.json`, `records/experience-coverage.json`, relevant project lessons and knowledge, and a readable checkpoint as normal artifacts with kind, status, `depends_on`, and `sha256`. Link actual requirement, decision, and review IDs so a context copy retains the original authority. Files under `assets` provide templates.

The director's live records reside in `.gameatelier/orchestrator/state.json`. Preserve existing `.gameatelier/state.json`, requirements, decisions, and game saves. The sidecar pins canonical authority files and hashes. Transfer the relevant checkpoint and context, inputs and masters, open decisions, stopping boundary, knowledge, and dependencies. Include internal logs only when needed. Keep an unknown external outcome open with the action ID and a status query until reconciliation.

When runtime state has stage records, reconcile current due requirements, decisions, and knowledge with package records and independent reviews before an accepted `stage-check`. `context --stage STAGE` returns `stage_context_snapshot`. Save it under optional `manifest.project_context`, reseal, and review affected artifacts. Reconcile semantic gaps explicitly. The orchestrator checks current project context. `pipeline.py` validates package structure.

`START_HERE.md` explains the result and one next action in plain language. Invoke the needed skill or tool directly when the environment permits. For a manual handoff, specify where to open the project, exact file versions, what to run, expected output and receipt, what to return, and how to verify it. A pause or search-only package can satisfy its intermediate scope with draft status. Production depends on accepted evidence for the next gate.

Transfer the current systemic passports, visual production profiles, structural receipts, independent semantic reviews, and actual image inspections as artifacts and evidence with pinned hashes and current requirement IDs. Preview readiness leaves the accepted concept gate open until the owner chooses the concept. Runtime state uses schema **2.0.0** with the compatible **6.0.0** toolkit marker from `scripts/atelier.py`.

## Scoped acceptance profiles

For bounded packages, the following profiles replace the full-stage minimum kinds and material decision IDs. Current project requirements and decisions that apply to the scope remain binding, including each open must. Every scope requires actual artifacts and hashes, independent review, and the applicable game-model gate.

| Stage / acceptance_scope | Model gate | Required kinds | Minimum production decision IDs |
|---|---|---|---|
| concepts / candidate_completion | concept (complete C1) | studio_identity, concept_candidate, progression_model, economy_model, visual_baseline, validation_plan | None. A candidate has no production selection yet. |
| qa / design_review | concept | test_report, defects | None. The review leaves production selection open. |
| qa / contract_review | preproduction | test_report, defects, validation_plan | None |
| qa / slice_review | slice | test_report, device_matrix, fidelity_report, defects | None |
| qa / beta_review | beta | test_report, device_matrix, fidelity_report, economy_report, defects | None |
| qa / release_readiness | release | All QA stage kinds | All current production decisions |
| liveops / incident_analysis | concept | incident_report, support_runbook | None |
| liveops / design_change | preproduction | change_plan, validation_plan | None |
| liveops / runtime_change | slice | change_plan, test_report | None |
| liveops / player_experiment | beta | experiment_plan, test_report | None |
| liveops / release_change | release | release_manifest, rollback_plan, operator_runbook | All current production decisions |

`manifest.game_model` contains `path`, `sha256`, `acceptance_scope`, `scope_ref`, and `scope_description`. `scope_ref` must identify a current package requirement or decision. The description names the bounded review or repair. Omitted scope uses the full-stage profile. Release requires its own scope. `pipeline.py model_gate/acceptance_profile` defines valid labels. `slice_review` applies through the slice gate.

Every linked model, including drafts, uses schema **4.0.0**. Accepted non-studio packages require each due C1/T/evidence obligation. `current_toolkit_ready` indicates acceptance at the current toolkit gate, while `quality_certified` remains false. `pipeline init` emits the supported toolkit marker. The verifier rejects unsupported older formats or markers.

## Current project requirements and scope

An accepted manifest may declare `scope` for the exact project or task. The default is `project`. This axis is independent of `game_model.acceptance_scope`, which indicates maturity. Obtain a binding with `atelier.py context PROJECT --stage STAGE --scope SCOPE`. Project-scoped requirements apply in every scope. Another bounded scope does not block independent work.

For an accepted claim, `stage-check` validates applicable current musts even without `--require-accepted` by primary stage or typed stages array, closure status and evidence, and package inclusion. Each due must must appear in `records/requirements` with the same ID, status, owner, and acceptance. Current material decisions must appear in `records/decisions` with the same answer and authority. `manifest.project_context` pins their current definition tokens. Reconcile content and review together with hashes. Validate against the canonical project state for current authority.

## Admission compatibility

Pin task `consumed_sources` separately from shared runtime identity. A changed consumed source makes the affected task stale. Use a reviewed or new task when older records lack pins. Runtime 2, model 4, and handoff 1 remain the schema identities. The toolkit compatibility marker and supported workflow adoption govern operating-version changes.
