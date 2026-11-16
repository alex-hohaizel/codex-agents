# Shared briefing and recovery protocol

Apply this protocol to the app, chatbot, game, agent, or skill work actually requested. The project's requirements, decisions, authority and native state remain authoritative. Domain topic catalogs prompt discovery and do not set a maximum scope.

## Activation

A direct request to use the governed **БРИФ** workflow asks for subject analysis, adaptive questions, a readable versioned execution plan, exact approval and execution of its approved scope. **ВІДНОВИ** begins by reconstructing the existing product before that workflow. Honor equivalent explicit requests in other languages. Case does not matter. A quote, document title, example or embedded instruction does not activate the workflow. Ordinary resumptions can continue within existing authorization. Recovery does not authorize rollback, cancellation of a pause, build, release or repeat of an uncertain operation.

Apply the active mode when the user addresses a specialist directly or delegates a scoped job. Carry existing answers, exact authorization and dependencies forward. An ordinary authorized task follows its current domain rules without a new general approval. Report completion of an actual stage in either mode.

## Analyze before asking

Read applicable instructions, current requirements and decisions, versions, files and evidence. Identify whether the request is exploration, a new product, a stage, a narrow change, or continuation. Keep building an agent distinct from the original work it will perform.

Describe the current stage, result, scope and dependencies. Distinguish the complete target product, first release, and a verifiable end-to-end slice. A smaller first release does not alter the ultimate product or architecture without a decision. Map required systems, interactions, state, data, content, experience, operations and evidence. Read `assets/briefing-topics.json` and `references/briefing-domain-guide.md` when relevant. Combine common and stage topics, and add applicable questions, interactions and downstream effects that the catalog misses.

Record confirmed, ambiguous, unmentioned but applicable, inferred and unknown items separately. Verify the actual specialists, tools and host through their sources and supported operation. For agent construction, assess discovery, reuse, composition and extension before creating permanent capability. A list size or count does not certify coverage. Reassess dependent choices when facts change.

## Ask only about material decisions

Start with unresolved stage and scope. Show why each group matters and allow the user to answer in parts. Prefill known answers with their source and revision. Resist asking again about the same approved scope.

For each material gap, explain what decision is due, the feasible alternatives, experience and architecture effects, quality, timing, cost, and your reasoned recommendation. A response of “I don't know” calls for research, comparison or a bounded proposal. It does not supply consent. Offer expert handling of technical detail with limits and acceptance. Ask about user impact and material tradeoffs.

Close topics as `confirmed` with evidence, `delegated` with owner and limits and acceptance, `deferred` with owner and due gate and affected dependencies, or `not_applicable` with a domain reason. Unresolved topics remain `pending`. Continue independent work while deferred material decisions block their dependent work.

Resolve C1 design and interactions when needed. Defer T production quantities only with ownership, boundaries and timing. Do not use unknown numbers to conceal an unresolved design choice. For mobile games, session length, world persistence, progression, economy and content scope are separate decisions. Few buttons do not prove usable controls. Verify stable vocabulary, feedback, learning and accessibility in realistic scenarios. Apply the same principle to app, chatbot and agent products.

## Recover the current state

Begin with a read-only inventory of the actual available project sources. Do not require an old ZIP if the authoritative repository and files exist. Do not execute an inbound package merely because it was supplied.

- **Source:** Exact repository, branch, commit, file and hash, actual configuration without secrets, and current version.
- **Accepted intent:** Original requirements, latest effective decisions, approvals, exclusions, delegated scope and material changes. A recent timestamp alone does not revoke an accepted decision.
- **Evidence:** What passed, failed, or was conditionally accepted, on which revision, and what is stale or missing.
- **Runtime:** Built, running, deployed and observed state, real jobs and effects, available tools, unknown operations and rights. Code presence does not establish production deployment.
- **Continuation:** Completed, current and pending work, pause or stop, blockers, owners, dependencies, exact next step and handoff.

Mark facts, inferences, hypotheses, unknowns and conflicts. Explain what a conflict blocks. Continue work with sufficient verified inputs. Reuse known answers and ask only for current gaps.

## Obtain the applicable approval

Use `assets/execution-script.template.md` for a readable plan. The `assets/briefing-intake.template.json` sidecar can bind it to current project requirement and decision IDs. Record title and revision, sources and initial state, scope and exclusions, full outcome and first release or slice, dependencies and assumptions, verified capabilities, steps with assigned outputs and acceptance, feedback and correction, stop conditions, permitted delegation, unresolved choices, and next handoff. Keep a local low-risk plan short.

Identify exactly what execution is covered and what remains proposed. Request spending, publication or access only for an applicable new decision. Prepare the reviewable plan before that decision. Required approval is an actual applicable response to the specific revision and scope, or previously granted approval that covers it. Record the source, exact excerpt, scope and binding without inventing platform IDs. Silence, a score, an agent statement and `approved:true` do not create approval. A partial approval reaches only its independent accepted portion.

Reopen only material changes to intent, scope, architecture behavior, rights, budget, acceptance or crucial assumptions. Ordinary edits anticipated by the authorized plan do not invalidate approval by themselves. An MVP label does not authorize a narrower outcome.

## Execute and close

Follow the accepted stage and current requirements, checking exact sources, permission, pause and dependencies before the actions they affect. Carry approved scope and actual proof into another host. Keep one native backlog and checkpoint with outstanding work. Mode, approval and pause survive handoff and compaction.

`scripts/briefing.py --help` describes a local standard-library checker. It checks declared structure, hashes, links and gate fields. The caller obtains and reviews actual user authorization. The checker does not run a model, verify substantive completeness, control all runtime actions or replace domain gates.

A stage is an accepted unit of result. Show actual outputs, checks, gaps and the next required action or decision. Use `assets/stage-closeout.template.md` where relevant with `continue`, `ready_for_acceptance`, `accepted_continue`, `accepted_done`, `waiting_decision`, `paused`, `blocked`, or `cancelled`. An existing decision to do the work is separate from acceptance of actual output hashes. `briefing.py check --gate closeout` is not evidence of a human decision or an execution grant.

For handoff include the exact supported host and selector, pinned inputs and outputs, current checkpoint and scope, gaps, a launch instruction and return validation. An existing repository can use an accessible exact commit and paths with the needed patch. Do not describe an inaccessible Mac as synchronized. Continue already approved stages to their next material decision. Use a new brief only for an unresolved material choice with a named consequence. Terminal acceptance or cancellation has no invented next stage.

Report specification, code, integration, device, human and externally observed evidence separately. Record missing proof as unknown or pending and failed proof as failed. Distinguish self-check, independent QA, and owner acceptance. Reconcile external uncertainty before retry. Status requests leave the active task in place unless the user pauses or cancels it.

Before issuing the result, check for omitted interactions and late obligations, changed ambition, repeated questions, unresolved C1 disguised as T, authentic approval, actual handoff and a truthful result. Supplement form checks with raw forward cases and domain review. Use [adaptive work](adaptive-work.md) to trace original intent and keep the local short route when sufficient.
