# Current work formats

Each data type has one supported format. Earlier readers and automatic migrations of agent outputs are absent. Format versions and toolkit versions are separate. `chatbot.blueprint/3`, `chatbot.round/1`, `chatbot.team/1`, `chatbot.team-profile/1`, `chatbot.review/1` and `chatbot.adapter/1` are different current contracts. The shared graph contract defines `depth/2`.

## Blueprint and adapter

`chatbot.blueprint/3` holds the domain model, applicability, exact rules and interactions, journeys, operations, recipes, attempts and evidence. Readiness is draft, specified or integrated. `check_chat_contract.py` rejects any other format identifier. `chatbot.adapter/1` binds a selected platform, account, environment and its trust, acknowledgment, dispatch, delivery and probe contracts. `check_platform_adapter.py` checks the declaration. Actual API support and receipts need direct evidence.

## Round and team

`chatbot.round/1` contains the brief, 24 canonical requirement IDs and approved project-owned IDs with active or unchanged impact, findings, decisions, changes, evidence, runs, reviews, mandatory `team_policy`, completion and checkpoint. The value is `team_policy.schema_version=chatbot.team/1`. Take profile_version from the current `assets/team-profile.json` and keep it separate from the skill version.

A canonical run has `id`, `actor_id`, `kind`, `status`, `requirement_ids`, `domain_ids`, `output_ref` and `output_sha256`. Add a verdict and appropriate review fields after actual acceptance. Readers accept current fields exclusively. Establish authorship and independence from observed work. `completion.stage` records the achieved level. `completion.status` records scoped_complete or stage_complete.

`python3 scripts/teamctl.py plan ROUND.json --kind local --active ID` creates a current draft. `hashes` records observed bytes, `freeze` binds the package digest and `check` validates team records. `python3 scripts/check_round.py ROUND.json` requires the current team policy for every acceptance path. Verify naturalness, experience, delivery and authors' claims through suitable independent evidence.

Feature, critical, and stage rounds use the owning project's `production-choices.json`. `bind-inputs` verifies the experiment rationale for planning runs and the approved decision for dependent runs. Keep that binding when delegating and resuming. `freeze` checks the recorded decisions against the current project before it creates a package hash. `check --ready` and `check_round.py` check the evidence due for current acceptance. Use `--project-root PROJECT` if the record lives outside the round directory. `check_round.py --historical` reads retained traceability without admitting the prior round into current work.

`chatbot.review/1` allows reuse of an unexpired same-format result from this project when the exact inputs, dependencies and environment still match. Changed or unknown dependencies and revoked data invalidate the affected acceptance.

## Unsupported input and existing projects

Reject other result formats as machine inputs. Recreate the current model from authoritative requirements and observed sources. Keep the user's original file intact. Additional legacy readers or automatic imports are outside this format contract.

For an existing bot, restore the current repository and tree, configuration, approved assets, completed checks and provider world state. Create a current checkpoint. Preserve actual data, stable requirement IDs, behavior and product database or schema migrations under their own contracts. A previous agent dossier is optional.

## Relationships and readiness

Blueprint systems.rules is a nonempty array of records with a unique id, algorithm:string, types:string[] and order:string[]. Include types and order for every rule. Operation capability_status is unverified, candidate, catalog_verified, specified, configured, exercised or unsupported. Every claimed integrated operation must have exercised evidence. Bind a recipe and its operations both ways. Map each active requirement to a system, a journey, an operation and a recipe. The [evidence contract](evidence-and-delivery.md) defines current subject, attempt and evidence hash bindings and explicit scope exclusions.

Project round extensions retain the baseline. Each added requirement has source_ref, owner, domain_id, acceptance and negative_probe. Assignments and actual reviews cover the entire approved ID set. Apply scope and reviewer independence requirements to any number of domain criteria.

`completion.assessments` holds independent specification, code, integration, device and human axes. Each records status=not_assessed|pending|passed|failed|not_applicable, scope and evidence_ids. Passed requires evidence for that axis. Actual device and human observations need their own evidence. Document the reason for not_applicable. `human_validated` can be a historical label in project source. It is not a current completion.stage. Retain original human evidence and assess the current scope and revision from its contents.

## Bind actual reviewer inputs and producer provenance

Before a new actual run, create a prepared, planned or running record with the real context and scope. Run `python3 scripts/teamctl.py bind-inputs ROUND.json --run RUN_ID`. This records the `chatbot.run-inputs/1` input_snapshot: scoped components with SHA and environment, hashes of canonical and project requirements, reviewed_outputs and reviewed_evidence. It does not execute the role, issue a verdict or mark completion. Resolve unknown inputs before running and record actual artifacts.

Determine inputs for QA, guardian, qa_signoff, judge, orchestrator and supreme from their actual requirement scopes, assignments and transitive dependencies. Bind current components, author outputs, primary evidence and an applicable carried-evidence receipt. An empty input_component_ids does not waive required inputs. input_run_ids or input_component_ids can add dependencies. The current ready check verifies each immutable consumer snapshot. A changed component, environment, criterion, author artifact or evidence needs new review, even after refreeze. An unaffected scoped run with the same explicit inputs retains its validity.

The producer snapshot records what it consumed before legitimate writes. A new output without prior bytes can declare input_component_ids=[] with a nonempty input_scope_reason. Accepted requirements stay bound. Binding needs no placeholder output. Freeze actual producer output_ref and output_sha256. Later QA compares the precise producer output with the current target.

`hashes` retains the input_snapshot for completed runs and rejects changes to frozen producer bytes. `freeze` pins a package. It does not refresh QA. `bind-inputs` preserves saved snapshots and completed runs. Start a new run for a new actual review, keeping previous evidence and signatures. Compare declared identities and hashes with actual execution, authority and adjudication sources.
