# Stage contract for chatbot-atelier-specification

## Visible result and applicability

Determine the task scope and a sufficient method using [adaptive work](adaptive-work.md). Apply [focused research and synthesis](research-and-synthesis.md) at any stage when it is relevant. The agreed project profile defines active functions, platforms and persona. Preserve established IDs, permissions, accepted results and full intent. Bind reviews to the exact observed source and version. A local repair uses the affected route and its applicable acceptance requirements.

Show a complete domain model, component contracts, architecture and language decisions with consequences, interactions and acceptance. Specify the agent team's structure and the target product architecture as separate decisions. Both must cover the applicable intent.

## Model each active system

Record ID, purpose, applicability, owner, typed fields/units/ranges, authoritative state, inputs/outputs/events, permissions/audience, dependencies, failure recovery, migration, and acceptance. Specify rule order, observation time, validation boundaries and golden cases. For probabilistic behavior, specify acceptable outputs, abstention, and evaluation distribution.

Carry tenant/workspace/chat/topic, actor and audience, request and logical operation, source and version, privacy epoch, authorization, and causal trace. Separate platform event, domain command, tool request, effect, outcome, and delivery. Maintain one source of truth for each commitment, consent, memory, and delivery across schema, API, events, prompts, tests, and rollout.

## Specify transitions and cross-system effects

Make guards and atomic boundaries explicit for proposal, needed input, authorization, preparation, dispatch, running, success, failure, uncertain outcome, cancel, expiry, reconciliation, and delivery. Define deduplication identity and retention, version fences, retry class, attempt cap and deadline/backoff, and recovery after each crash point. A planned cancellation prevents a future dispatch only when the state transition and worker fence guarantee it. Bind the request to a stable event and series ID, project the same accepted state in UI, and return the original receipt on replay. Decide how cancellation races with an in-flight send before freezing the contract. Reconcile ambiguous effects before retry; claim exactly-once only in the proved scope.

Specify persistence, replay/migration/backup/restore, retention and tombstones. Use UTC instants and IANA civil zones with DST gaps/folds, recurrence and misfire handling. Define memory provenance, correction, TTL and derived invalidation. Preserve group roster, authorship, consent and late join rules, and media source through delivery identity.

Trace active dependencies through cause, allowed order, failure, repair, persist boundary, feedback, and acceptance. Cover memory/jobs/delivery, DM/group, persona and tool truth, platform/domain ACK, scheduler/revoke, media/resources, and schema/rollback. Record conditional applicability and open unknowns. Deliver the typed model, decisions, sequences, golden and negative cases, integration and migration plans, and owner map. Feed infeasible promises back to the product owner with evidence.

## Handoff

Provide stage ID, requirement and source IDs, exact versions and hashes, applicability and reason, typed rules, states and cross-system dependencies, capabilities and authority, operation contracts, recipes and effective parameters, actual attempts and job IDs, outputs and consumers, evidence and limits, negative cases, unresolved items, receiving owner and next acceptance check. The receiver can verify the finding without chat history. Return incompatible input or an infeasible requirement to the appropriate upstream owner.

## Criteria and completion

Check applicability for these criterion IDs first: execution_truth, consent_authority, lifecycle_reliability, version_continuity. Use all 24 baseline IDs for the impact map. Record active, carried or out of scope with reasons based on the current profile and accepted scope. Retain all approved requirements. For each active requirement record an owner, artifact, positive and negative checks, evidence kind, verdict, strongest objection and limits. Unknown evidence for a critical claim blocks the affected readiness. The author and independent QA are distinct. Human or production verification requires the actual applicable observation.

Deliver the complete requested result. Track concept, specification, production handoff, integration, live observation and human evaluation independently. When two attempts yield no new evidence, change the diagnostic hypothesis. A depleted budget leaves unmet acceptance criteria visible.
