# Agent Foundry depth acceptance

Contents: model creation → gates → claim matrix → negative cases → fresh recipient. Read before accepting a passport, generated family, production output or change to a dependent tool.

## Create a model from current sources

Build a new `foundry-depth/2` from the template. Set `is_template=false` only after filling it with actual content. Bind the subject to current blueprint ID, revision, digest and approval source. `blueprint_sha256` is the canonical semantic digest used by `foundry.py`, not the digest of arbitrary JSON formatting. M0 can leave the subject pending. M1 and M2 require all four fields. A JSON field does not grant consent. Current `foundry.py` owns authority, tasks and effects in its own ledger; the depth model is not another authority store.

Records:

- `requirements`: id/source/owner/acceptance/negative_case/due_gate/applicability, with reasons for pending or N/A.
- `systems`: id/purpose/owner/input_contract/output_contract/invariants/depends_on.
- `rules`: id/requirement_ids/input_contract/steps/output_contract/oracle/failure_policy/state_ids, with exact domain semantics.
- `state_fields`: id/type/authority/persistence/consistency_group/migration/recovery_oracle, and default, range and retention as applicable.
- `capabilities`: id/tool/operation/environment/status/evidence_ids, with linked support for schema or catalog, rights, cost and freshness.
- `operations`: id/requirement_ids/capability_id/recipe_id/consumer_id/output_ids/parameter_bindings. Bindings have requirement_id/field/status/consumption_check. Material status is supported_not_tested/consumed/unsupported/unknown; ready requires consumed.
- `recipes`: id/operation_ids/input_ids/output_ids/consumer_id/steps/validators/repair_policy. Add budgets, authority and current input hashes from the actual production recipe.
- `artifacts`: id/path/sha256/owner/kind. Use a relative contained path without links or escapes. Leave the hash pending until bytes exist.
- `evidence`: id/artifact_ids/subject_sha256/level/result/observer/independent/environment/method/scope. Map every subject ID to its actual hash. Levels: source/structural/semantic/operation/integration/human/operational. Results: pass/fail/not_run/inconclusive.
- `modules`: id/name/path/requirement_ids/inherited_contracts. Path contains SKILL.md. Each inherited contract has kind core/domain/production/evaluation, contained path and hash. One file can hold several contracts. The reviewer inspects substance; kind is a machine label.
- `assemblies`: id/artifact_ids/required_evidence_ids/consumer_id/scenario/expected_result. Keep actual observations as artifact or evidence.

The model is not a provider activity log. Keep attempts and receipts in the current project ledger and link exact references and digests in the recipe or evidence. Do not copy secrets, private conversations or project state into a reusable skill.

## Two machine gates and domain acceptance

`check_foundry_depth.py MODEL --root PACKAGE` checks structure, IDs and references, required fields, inherited contracts and evidence bounds. Pending production artifacts are valid plans. A pass claim needs complete subject pins. M0 or M1 is not M2.

`check_foundry_depth.py MODEL --root PACKAGE --ready --session SESSION` also requires current accepted Foundry state; exact subject ID, revision, semantic digest and approval source; M2; current output bytes and hashes; applicability of every requirement; an operation per applicable requirement; consumed material parameters; a capability with a suitable passing witness; and a consumer assembly with passing integration, human or operational evidence for its exact artifact set. If `PACKAGE` is an initialized session with `.agent-foundry/state.json`, the checker infers `--session`. Other roots need the exact session path to bind current authorization.

The checker reads under the session's lock. It verifies journal and snapshot, current sources, suite, pause, and canonical authority through the bundled runtime in memory. It does not `save`, dispatch or call providers. A copied gate report does not stand in for the session. The report pins actual model bytes and digest, and the read session's state digest, revision and scope. The planning check does not need future approval or claim current authority without `--session`. It does not certify professional quality, rights or authenticity of observations.

Next use a domain reviewer and a fresh recipient. For applicable claims gather real human, device, provider or production observations. `foundry.py build-gate`, `bundle-check`, current Skill Creator validation and shared `verify_depth.py` have separate purposes. Include the depth model and report in any new generated package and run the gates before `package_agent.py`. A supported format or toolkit number does not confer domain acceptance on an external package.

## Claim matrix

| Claim | Appropriate proof | Insufficient on its own |
|---|---|---|
| Complete domain passport | Applicable jobs, rules, states, failures, dependencies, and accountable domain review | Role count or text length |
| Tool supports critical parameter | Actual operation and schema, bound value, and consumption observation | Description or prompt |
| Generated skill is competent | Raw task, real artifact, and a differentiating check by another actor | SKILL.md or metadata exists |
| Integration produces the result | Exact assembly, scenario and observations | Separate unit tests |
| Independent acceptance | Different actual reviewer, raw artifacts, specific scope and output | Renamed self-check |
| Reliable external effect | Provider receipt, read-back or domain reconciliation | Dispatch flag or timeout |
| Work or Codex ready | Separate placement, discovery, source/version and safe invocation | ZIP or matching names |
| Sustained service outcome | Authorized observation that actually ran for the claimed interval | Runbook or promise |

## Negative cases

Exercise missing recipe, consumer or rule; unsupported material parameter; stale source, importer, schema or hash; dangling proof; source-only evidence used as integration; missing or malformed inherited contract; author as reviewer; competing writers; replay of unknown remote effects; rounding, time or ID conversion loss; changed authorization; partial output, crashes or disk failure where applicable; restore after deletion or revocation; invalid host return; a pending requirement marked N/A; and a template presented as completed.

Inject an actual defect that the test would reject. Use an independent oracle or fixture and examine the strongest objection. Do not make live payments, deployments, messages or expensive generations just to validate a route.

## Fresh recipient and closure

An independent recipient starts from raw request and package without chat history. They should find current intent and approval, skill, inputs, exact steps, output and consumer, oracle, gaps, and next permitted action without inventing rules or asking for known facts.

Pin exact artifacts, proofs, dependencies and verdict per requirement at closure. Repair only affected branches and preserve accepted originals. A toolkit or model change does not update a historical proof. Report agent construction, installation and invocation, end result and actual operation separately.
