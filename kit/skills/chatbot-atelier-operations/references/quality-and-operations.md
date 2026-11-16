# Quality, evidence and operations

## Independent assessments

Record design quality, evidence maturity, authorization and product scope separately. Prepared specification, runnable code, mocked effect, actual integration, provider acceptance, human read and human response have separate proof. Assign pass, fail, unknown or N/A with reason to each must. Critical unknowns block claims about that path. Privacy, consent and truthful effects remain required at any UX score.

Evidence kinds are E0 hypothesis, E1 inspected source and version, E2 isolated deterministic execution with mocks, E3 integrated execution at a named boundary, E4 live provider or transport observation, and E5 human assessment. Choose the kind relevant to the claim. Human assessment and execution are independent.

## Evidence quality

Record ID, requirement and claim IDs, artifact, version and hash, environment, configuration and model/tool versions, procedure, observed result, limits, actor and execution run, author and reviewer, dependency snapshot, observedAt and expiry. The reviewer inspects raw artifacts. Check receipts with their source. Independent references and published benchmarks can support reasoning. Local measurements require an actual local run.

Keep J01–J12: social attention, referent and clarification, persona and naturalness, useful initiative, consent and authorship, execution and recovery, platform experience, composition, memory and continuity, truthful outcomes and repair, privacy, and resources and architecture. Record verdict, strongest objection and uncertainty separately for every active criterion. Assign review work by actual coverage.

## Intent coverage and choice of method

For material scope, independently compare original user messages and sources with the requirement map. Cover every requirement, emphasis and question with interpretation, expected result, owner, due gate and evidence or reason for deferral or non-applicability. Give the reviewer relevant originals. Treat an illustrative example as scoped. Structural or hash validation covers declared data. Verify semantic completeness independently.

Use [adaptive work](adaptive-work.md) and [research and synthesis](research-and-synthesis.md) to compare applicable alternatives. Explain the team's competence and why the scope and reuse are sufficient, with counterevidence and uncertainty. Naturalness, language, media, knowledge, code and live effects have distinct acceptance checks.

For skill or constructor changes, compare before and after on varied original requests. Use fresh reviewers and a frozen rubric, and repeat unstable or critical cases. Probe missed emphasis, unnecessary team or confirmation, unfamiliar domain, changed source, cold resume and unknown external effects. Keep planned and executed cases distinct. Verify existing project state compatibility, preserved evidence and rollback before adoption.

## Tests and evaluation

Bind positive, boundary, negative and failure cases to IDs. Contract tests cover versions, types, payloads and authority. Model evaluations cover wording, retrieval, abstention and referent. Integration tests observe durable state, effect and delivery. Platform smoke observes mobile or web UI. Human evaluation covers naturalness, usefulness and accessibility. Test cross-chat or DM leaks, injected authority from untrusted tools, duplicate event, stale callback or spec or privacy epoch, revoke/forget races, cancel around dispatch, split lease or restart, unknown provider outcome, exhaustion, unsupported effect and degraded operation.

Time, cost and load tests include denominator, input size, hardware and environment, concurrency, p50/p95/p99 where useful, warm/cold behavior and quality. Account for wrappers, timeout and retry in the causal trace. Report actual usage, resource consumption or measured cost.

## Preserve state and evidence through change

Keep one authoritative domain state, atomic transitions, one writer or version fences, and an outbox/inbox or another justified mechanism at the store-to-effect boundary. Use queues, Redis or a workflow engine only for an identified constraint. Test backup and restore in isolation. Keep versions, migrations, retention and tombstones aligned with memory and privacy. Persist progress and remote IDs before long operations.

Carry evidence only when exact artifacts and transitive dependencies match and the environment, tool/model identity and freshness still apply. Shared prompt, router, generator, SDK or DB schema changes invalidate dependent claims. Preserve the immutable previous receipt and add a fresh check of unaffected scope.

## Release and operations

Do authorized release preparation and checks. Confirm exact scope before the actual external effect. Reuse current explicit approval for the same action. Skill preparation and product deployment have separate scopes. A failed gate blocks affected work while independent tasks continue.

Record source/build/deployment IDs, target, migration, observed health and delivery, and rollback trigger. Incidents need severity, user impact, containment, actual evidence, causal hypothesis and test, recovery, data correctness, communication and prevention. Support escalation records destination, owner, delivery and expected response. Use the actual service commitment for SLA.

Track completion, error, uncertainty, retries, duplicates, queue age, silence and false initiative, retrieval failures and abstention, resource use, cost, latency and feedback through privacy-safe telemetry. Review affected behavior after model, provider or schema changes. Verify export, portability and termination where long-term storage is promised.

## Evidence admission

Integrated attempt subjects require current contract_sha256 from check_chat_contract.py --subject. Normative contract, requirement, recipe, operation or adapter changes invalidate dependent acceptance. Bind new pins to new observations. Code and integration proof need an admissible kind, build_ref and environment. Integration also needs actual_observation_ref. teamctl mutations use current revision/CAS. Raw saving without expected_sha256 cannot overwrite stale state.
