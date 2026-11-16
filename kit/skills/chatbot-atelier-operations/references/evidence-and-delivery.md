# Evidence, decisions and recovery

Use the current [team policy](team-policy.md) and [team profile](../assets/team-profile.json) for grouped domain assignments and independent local acceptance. Apply the relevant criteria and evidence to the actual scope.

A current round uses `schema_version="chatbot.round/1"`. It records brief {id,version,user_intent,baseline,constraints,authorization}; requirements with all 24 baseline IDs and approved project-owned IDs, state=active/unchanged and reason; findings; decisions; changes; evidence; runs; reviews; mandatory team_policy; completion; and checkpoint. Keep a local round proportional while using the same format and an explicit impact map.

- Finding: id, requirement_ids, version, reported/reproduced/hypothesis/preference, scenario, actual/expected, evidence_ids, severity, cause/falsifier, audit_status.
- Decision: id, finding_ids, options/chosen/reason, expert_sources, tradeoffs, affected IDs, verification/rollback. Read a source before using it.
- Evidence: id, version/hash, kind (source/code/execution/human/telemetry), provenance (reported/inspected/reproduced), artifact, procedure/result/limitations. Record tests_green, audio_audible and natural_conversation independently.
- Run: `id`, `actor_id`, `kind`, `status`, `requirement_ids`, `domain_ids`, `output_ref` and `output_sha256`. Applicable reviews also bind package_hash, verdict and context. The aliases role, artifact and agent_id are not current fields. Leave unexecuted results pending and use actual run identities.
- Review: requirement_id, actor_id, run_id, package_hash, verdict (accept/revise/block/unknown), evidence_ids, strongest_objection and uncertainty/reversal_condition. Preserve separate verdicts.
- Completion: stage (prepared/locally_verified/independently_reviewed/deployed/observed_in_chat), scope, status, unresolved_requirement_ids, deployed_version and dissent. `assessments` may track specification, code, integration, device and human separately. Each axis records status, scope and evidence_ids. A pass needs successful evidence. Human or device proof also needs an appropriate actual_observation_ref. Missing axes remain unassessed.

Record before and after, artifacts and impact on each active or unchanged requirement. Material changes invalidate dependent evidence and reviews. Explain unchanged impact. On resume compare the checkpoint with the current repository, deployment and concurrent updates. Continue independent authorized work while blocked branches wait.

Before repair, establish a baseline, audit or reproduction, or an explicit requested change. Before acceptance, supply the actual diff or output, relevant checks and limits. Independent claims require observed independent runs. Release needs current permission, rollback, necessary checks, assets and migrations. If publication was authorized and performed, read back the live version or receipt. Report the actual prepared or accepted stage otherwise.

Keep unrelated work moving. A deployment outage can leave a local repair feasible. A sticker defect leaves calendar requirements intact. Apply the existing scope and permission contract. Describe useful results with their evidence, such as «відео перевірене з наданою доріжкою» or «переглянуті N/M анімацій; решта ще не прийнята». Keep engineering records separate from announcements. Exclude secrets and private transcripts. External delivery needs actual authorization.

## Domain requirements and exact proof

Preserve the 24 canonical IDs. For each accepted project-owned requirement keep a stable id, source_ref, owner, domain_id, acceptance, negative_probe, state and reason. Verify the source_ref against the actual approved source. `teamctl.py plan` includes the new domain_id in assignment without changing canonical ownership. Independent completion for a project extension requires the same actual actors, primary evidence and acceptance as the baseline.

For `chatbot.blueprint/3`, specified is a complete domain declaration. Each active requirement has reverse coverage by systems, journeys, operations and recipes. Explicit deferred, excluded or not_applicable requires scope_decision_ref and reason. Deferred also requires due_gate. Verify the actual decision against its source.

An integrated journey lists operation_ids, current attempt_ids and evidence_ids, and verification=passed. Each chosen attempt has result=passed, actual_run_id, input_snapshot.hash, effective_parameters, linked operation_ids and recipe_ids and subject {brief_id,brief_version,brief_sha256}. `brief_hash(brief)` in check_chat_contract.py uses SHA-256 of UTF-8 JSON with sort_keys=True, separators=(',', ':'), ensure_ascii=False and allow_nan=False. Identify proof for the exact brief without treating its ID, revision or hash as human authorization.

Evidence records artifact, output SHA-256, procedure/result/limitations and exact attempt_ids and attempt_sha256s. Each attempt_sha256s[attempt_id] equals `attempt_hash(attempt)` by the same canonical JSON rules. Changed inputs, effective parameters, scope or outcome invalidate old proof. Current attempts with failed, unknown, cancelled, uncertain, pending or running and linked unsuccessful evidence block integrated status. Retain failed historical attempts separately. Each claimed operation has exercised capability and successful linked execution, integration, device or live_provider evidence. Source and human-review evidence support their own claims.

A structural check verifies these bindings. Verify actual external artifact bytes, provider receipt, human acceptance and quality at the applicable tool, readback or independent observation boundary. Track prepared round, specified blueprint, integrated execution, live availability and human assessment separately.

`specified()` and `integrated()` in scripts/test_chat_contract.py and `extended_prepared()` and `independently_reviewed()` in scripts/test_round_current.py are executable SYNTHETIC fixtures. Use actual execution IDs and observations for accepted work.

## Review result and currency

Round evidence.result has explicit status pass/passed/accept/accepted/observed/fail/failed/reject/rejected/pending/not_run/running/unknown/uncertain/cancelled/inconclusive/blocked. Put detailed measurements and explanations separately. An accepting review requires valid nonempty evidence IDs whose results are pass, passed, accept or accepted. An observation alone leaves acceptance open. Retain failed, not_run and unknown evidence.

Each current run declares input_snapshot as defined in the [protocol](protocols.md) and a frozen observed output. Accepting consumers bind the checked inputs to current requirements and components, author outputs and primary evidence. Changed target or primary observation needs an actual new review. Refreshing hashes alone does not perform one. Keep producer input provenance historical through legitimate producer writes. Verify the new target with the appropriate fresh consumer.
