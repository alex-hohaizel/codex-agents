# App Atelier support system

Contents: 1 coverage, 2 knowledge and data, 3 dialogue, 4 production, 5 acceptance and continuity.
Read cross-domain-core, data and support, workflow, and acceptance. Bind the `assets/app-depth.templates.json` template to a project artifact. Canonical state owns requirements, effects, and proof.

Use the [app system model](app-system-contract.md) for cross-cutting contracts. It owns requirements and state authority.

## 1. Design support around the useful outcome

Map `product rule/version → issue category → user mode → channel/state → required facts → allowed action → answer/case → proof`. Cover public and applicable account help, access, payment, errors and outages, absent features, stale knowledge, unsupported requests, and unresolved cases. Android, iOS, web, and agreed external bot channels share product semantics and use their own UI, transport, and identity adapters. Include group scenarios only when the support scope calls for them.

Define whether each category needs explanation, guidance, authoritative read, authorized operation, or tracked case. Mark «resolved» only after the defined observation. Categories preserve product policy and rights.

Classify capabilities as required, conditional, or absent_by_design. Choose the minimal sufficient route, including structured help when it works. Add LLM, RAG, vector database, voice, or CRM only when justified. Obtain domain review and explicit boundaries for professional, financial, children's, or other consequential subjects.

## 2. Specify knowledge and private context

Each knowledge item has stable ID, product, release, language and region, authoritative source and hash, valid_from and valid_until when needed, claim scope, owner, review and freshness triggers, and fallback. Resolve price, policy, and entitlement from authoritative sources. Release, plan, or policy changes reopen dependent answers, embeddings, caches, and cases. Preserve accepted originals for reproduction.

Give public documents, private customer records, case history, tool results, and receipts separate access policies. For each field specify source, purpose, authority, subject or tenant, recipient, retention, deletion and revocation, and backup behavior. Apply access constraints before searching and again before answering. Cache by subject, tenant and permission revision, product, release and locale, and source version.

Distinguish trusted instruction, verified fact, user claim, and untrusted retrieved content. Attachments, knowledge and chat cannot grant tool permission, change refund rules, or disable isolation. Keep secrets and private reasoning out of chats, logs, and skills. Report missing facts and unavailable results explicitly.

If Telegram linking is in scope, retain a challenge created in authenticated app or web, the private sender's numeric ID, expiry and usage state, and explicit confirmation for that link on app or web. Test replay, interception, account switching, revocation, and logout as distinct transitions. Username, claimed email, and expired or superseded links convey no rights.

## 3. Specify turns, actions, and cases

A turn records user, session and channel identity, transport ID, admitted input type and size, context revision, retrieval budget, answer claims and citations, tool allowlist, timeout and cancellation, cost cap, and output validation. Deduplicate repeated webhook, edit, or button events according to product rules. Distinguish dialogue, transport, action, and case IDs.

An action moves requested → validated → authorized → pending → succeeded, failed, or unknown → reconciled. Define actor and authority, prerequisites, exact parameters, idempotency scope, expected state and receipt, retry and compensation, and user wording. Reconcile unknown effects before repeating them. Use «повернено кошти» only after authoritative receipt and read-back.

A case uses applicable locally_drafted, received, triaged, awaiting_information, queued_for_repair, resolved, and closed states. Keep offline drafts distinct from received cases. Enforce authorization separately from case ID. Define retention, deduplication, reopen, aggregation for engineering, and proof of resolution. Commit to staffing, SLA, or owner work only when operational capacity exists.

Prove a degraded route with versioned cached public help, truthful status, local draft, or durable case via available storage. Set quantitative session, user and global limits, attachment sizes, timeout, breaker, and retrieval fallback from the cost model. Terms like «дешево» or «необмежено» need measured bounds.

## 4. Produce and integrate

Cover knowledge ingestion, chunking and indexing where needed, structured retrieval, channel adapters, authenticated tools, answer evaluation, case workflow, deployment and monitoring. Record tool, schema and platform, exact input and output format, rights, egress and cost, editable source, exact steps, consumer, and validator. Verify production LLM API and token budget independently of skill availability.

Check schema, catalog, and actual parameter consumption. Treat HTML and Markdown, encoding, URLs, and file extraction as distinct transformations with bounds, provenance, preserved IDs and locale, and known losses. Retrieval scores measure their defined ranking signal. For audio or voice, verify transcription, consent and data scope, pronunciation and interruption, and text alternatives.

Record pending attempts before external or costly actions and actual request, job IDs, and outputs when observed. Retain model, prompt, policy, knowledge and toolchain hashes, authorized data scope, observed tokens and costs, and fallback. Prompt repair records failure class, a new hypothesis, cap, and counterexample.

## 5. Verify the integrated support path

Pin exact client, backend, model, policy, knowledge and config hashes, tenant, subject and link state, channel, raw scenario, expected answer or action properties, budget, and environment. Run `user input → auth → retrieval → response/action → presentation → case/receipt → restart/revoke/resume`. Verify availability and security at the integration level.

Positive fixtures cover guest public help, own-account help, authorized linked channel, version-specific knowledge, unanswerable question, cap or outage fallback, authorized receipted action, and access after revoke or delete. Negative fixtures cover A→B IDs, cache and files, stale knowledge and price, forged, group or replayed events, prompt injection, expired challenge, concurrent account switch, late tool results after revocation, duplicate action or case, disk full, and unresolved effects at restart. Run these as authorized defensive checks under the appropriate scope.

Evaluate factual correctness, groundedness, useful next action, tone, privacy and scope, tool correctness, resolution evidence, latency and cost, and accessibility separately. Treat mandatory privacy and permission requirements as hard gates. Use automated oracles for verifiable facts and authoritative product sources for the correct answer. Provide independent reviewers raw prompts and inputs without the expected answer.

Changes to knowledge, model, policy, and tools invalidate affected cases, caches and assembly. Apply revocation to running and queued work and through restore. Test each channel on its actual environment when available. Give blocked channels or devices an exact handoff. Verify separate proof of running service and scheduler.

Return contracts, knowledge and editable sources, matrices and fixtures, attempts, receipts and evidence, caps and recovery, gaps, and next action. Keep private material in permitted project scope.

## Visible result and proportionality

Apply the [adaptive workflow](adaptive-work.md). Show support contract, channels and rights, knowledge sources, case lifecycle, and an observable resolution path. Distinguish completed work, inherited decisions, and future results with due gates. Scale depth and roles to uncertainty, consequence, and coupling. Use a local repair for a local change.

For material gaps, use the relevant [research, synthesis, or reconciliation mode](research-and-synthesis.md). Review factual and operational correctness, privacy, delegation boundaries, and observed outcome. Inspect raw inputs for omissions. Verify reviewer competence beyond actor ID and keep structural checks at their actual evidence level. Preserve context, approvals, and unaffected results.
