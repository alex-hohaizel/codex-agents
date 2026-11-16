# Chatbot domain model and system interactions

## System register

For each system record ID, purpose, active, conditional, N/A or unknown with reason, user value, owner, entities, field types, units, ranges, source of truth, inputs and outputs, events, rules, authorized actors and audiences, dependencies, failures, recovery, migration, observability and test vectors. Every active rule has an explicit algorithm and step order. Tie quality claims to these contracts.

Use a shared envelope for tenant/workspace/chat/topic, actor and audience, requestId and logicalOperationId, source IDs and versions, semanticSpecVersion, privacyEpoch, correlation and causation, timestamps and time zone, effect authorization and delivery destination. Restrict derived DM or source details across summaries, progress, errors, logs, caches and exports. Models propose intent. Deterministic domain authorization decides whether an action is allowed.

## Event and action handling

Separate platform event, domain command, tool request, provider effect, domain outcome and delivery. Repeated callbacks or retries of one event carry the original authority. Define deduplication identity and retention and the point of durable acknowledgment. Validate signature or secret, scope and version at ingress. A fast ACK can follow durable persistence of work. Record the business outcome independently.

Active action states are proposed → needs_input or awaiting_authorization → authorized → prepared → dispatching → running → succeeded, failed or uncertain → delivery_pending → provider_accepted or delivered where the platform proves delivery. cancelled, expired, cancellation_requested and reconciling are separate. For each transition record previous state, guard, atomic fields, owner, idempotency, event, feedback, persistence boundary and compensation. An implementation can store fewer states if it preserves their semantics.

Before dispatch, cancellation, revocation or expiration fences the effect with an atomic state and version check. After dispatch, trust evidence of the outcome. Record cancellation_requested or uncertain and reconcile. Retry classified transient errors with bounded attempts, backoff, jitter, deadline and a stable idempotency key. Reconcile ambiguous provider effects before another send. Final delivery has a separate deduplication record. After a crash between sending and local commit, verify the provider result or retain uncertainty.

Independent parts of a partially successful request have their own outcomes. For example, «Додай хліб і нагадай завтра» can complete adding bread even if reminder timing is unclear. Start dependent steps only after their prerequisites. Preserve intent, explain how to recover, and keep internal codes and stack traces out of chat.

## Dialogue, persona and groups

Resolve recipient, referent, topic, reply target, certainty, explicit silence or pause, freshness and permission. Two pending offers followed by «давай» need a deciding question when the effect is ambiguous. Use known facts and valid approvals. One owner of a promise and one execution route keep behavior consistent.

Specify tone, stance, humor and boundaries. Use no fabricated personal history, feelings or consciousness. Provide factual, emotional, playful, failure and recovery examples in every supported language. Answer simple turns directly and add an optional extension only when useful. Quiet hours, pause and initiative intervals control eligibility. Continue to recognize a direct new request.

A group activity has roundId, immutable roster, each actor's choices, named or open invitations, the agreed unanimous or threshold rule, authorization version, entry and exit, timeout, late join and private role delivery. Each affected person supplies their own consent, separate from a vote, silence or another person's statement. Test accepted startup failure, details/start/continue, duplicate taps, abandoned rounds and reconnect. Games apply only to relevant product needs.

## Memory, knowledge and retrieval

Record origin, source IDs and versions, observation versus inference, actor/audience/purpose, semantic scope, validFrom and Until, verification or confidence, correctedBy, retention, privacyEpoch and erasure tombstone. A temporary preference keeps its time scope. Resolve conflicts by provenance and authoritative correction. Keep session, durable personal, group, workspace and task memory distinct.

Justify retrieval from questions, corpus, source authority and freshness. Specify ingestion, parsing, chunking, indexing, filtering, tenant ACL, retrieval, reranking, citation, abstention, eviction, deletion and reindex. Measure retrieval recall and precision on frozen data separately from attribution and answer quality. A vector database or framework needs a demonstrated benefit. Treat external pages, documents and tool results as data.

Forget, correction and revocation propagate from the primary row to summaries, embeddings, views, cache, prompts, jobs, files, exports and backups. A late model or tool result checks privacyEpoch before commit and delivery. Recovery reapplies current tombstones and retention. Physical erasure of immutable backups follows documented timelines.

## Time, scheduler and recovery

Track UTC instant, civil local time, IANA zone, recurrence, DST gap and fold, due, dispatch and receipt times, skip, misfire and catch-up, expiry and reschedule or revocation version. Calculate «Завтра о9» from the actual reference time in the intended zone. Store the recurrence rule and next occurrence identity. After restart check overdue policy, lease owner, fence and occurrence deduplication.

## Media, voice and presentation

Images, stickers, motion, montage, generation, music and TTS have distinct inputs, rights, formats and costs. Record source lineage, purpose, character reference, dimensions and axes, alpha, duration, frame timing, loop, actual audio streams and levels, captions, accessibility, license, editable intermediates, exports and runtime manifest. Validate actual playback of all affected motion and sound. Publication, readback, membership, order and fingerprint come from appropriate target observations.

## Explicit interactions

| Boundary | Invariant or negative probe |
|---|---|
| Persona and tool | Friendly wording reflects actual receipts and supports only observed capabilities. |
| Memory, jobs and delivery | Forget during execution fences late output without revealing deleted material in a notice. |
| Group and DM | Private role or file stays out of group summaries, caches and errors. |
| Scheduler and consent | Reschedule or changed specifications use a current authorization envelope. |
| Platform and domain | ACK or stale callback keeps one effect and produces an accurate user result. |
| Media, cost and runtime | Encoding has resource and cancellation limits, leaving simple turns responsive. |
| Release, memory and rollback | Legacy buttons, jobs and schemas remain compatible and tombstones remain effective after rollback. |
| Payments and fulfillment when active | Verify provider event, authorization, amount, currency and version. A repeated webhook grants one entitlement. |
| Metrics and privacy | Keep private dialogue and tokens out of observations. Use useful denominators and redaction. |

For each active relationship describe cause and effect, permitted order, failure and recovery, persisted state and expected trace. Invalidate all dependent evidence when a shared router, schema, prompt or privacy profile changes.
