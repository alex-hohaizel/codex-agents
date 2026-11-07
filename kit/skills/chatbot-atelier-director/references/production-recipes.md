# Виробничі операції та виконувані рецепти

## Паспорт операції

Один tool/model/framework не є однією можливістю. Фіксувати operationId, exact tool/version/model/endpoint, actual supported inputs/limits/parameters, доступ/права/вартість, output format/editability, environment/target, verified evidence/date/expiry, fallback і межі. Catalogued, callable, executed, artifact_checked, integrated і live_observed — різні статуси. Перед дорогою/залежною операцією звірити опис↔schema↔каталог↔фактичний usage. Параметр, який інструмент ігнорує, не виконує вимогу.

Рецепт: входи з hashes/rights, preconditions, конкретний виконавець/competence, bounded steps/params, expected intermediate/source/output, semantic invariants, check procedures, exact receiver, failure hypothesis/falsifier, budget/stop, resume token. Actual attempt: час, виконана команда/виклик, tool version, effective params, input/output hashes, job/process ID, витрати якщо відомі, logs/receipts, outcome/limitations. Не підставляти invented job ID; не повторювати remote generation через втрачений context.

## R-C01: brief→предметна специфікація

1. Вхід: current user statements, source files, product baseline, primary sources.
2. Researcher виділяє атомарні R IDs і applicability; domain lead формує entity/state/rule/interface graph.
3. Для правила визначити типи/одиниці/межі, order, authoritative owner, user-visible effect і exact receiver.
4. Підготувати positive/negative/golden vectors, alternatives/assumptions; QA перевіряє повноту й cross-system contradictions.
5. Вихід: versioned brief+model+source map+acceptance; handoff to architecture/experience, unknown явно pending.

## R-C02: platform event→durable action→feedback

Inputs: synthetic event fixtures, platform credentials selector (без секрету в артефакті), API contract, domain action/version, target environment. Platform/backend specialists: verify source authenticity; normalize scope; persist dedup+work transaction; ACK by provider contract; worker authorizes current version; dispatch with idempotency; persist/reconcile receipt; deliver appropriate audience; finish typing/waiting. Inject duplicate, stale, wrong actor, crash before/after dispatch, timeout after provider success. Output: tested adapter, domain handler, receipt trace and UI states. Isolated mock success лишається E2, actual provider observation окремо.

## R-C03: conversational policy→observed dialogue

Inputs: agreed persona, mission, supported languages, frozen synthetic contexts, known capability contract. Conversation specialist створює normal/failure/repair wording і minimal pairs; deterministic router controls authority/action state. Evaluate 8 strata: direct, indirect, human-to-human, playful/emotional, pause, ambiguous, failure/repair, memory return. Track false response/false silence, wrong recipient, decisive clarification, completion, time/cost; denominator і context versions обов’язкові. Сліпа людська оцінка має ties/both bad, consent й rubric. LLM score є модельним судженням, не доказом human naturalness. Вихід: versioned prompt/policy, fixtures, independent code/eval report; не обіцяти живість за кілька красивих фраз.

## R-C04: source→memory/retrieval→forget/restore

Inputs: synthetic corpus з tenant/actor/audience/purpose, ground truth questions, tombstones, expected retrieval/citation. Build parse/chunk/index only if active; preserve provenance; ACL filter before exposure; answer grounded/abstain. Memory updates check corrections/TTL; deletion invalidates graph and increments privacy epoch. Run wrong-tenant query, deleted snippet cache hit, late embedding/tool result, restore old snapshot. Output: ingestion/index code, schemas/migrations, evaluation and deletion trace. Content hashing includes parser/chunker/embedding/model/ACL version; staleness invalidates relevant proof.

## R-C05: reminder→durable occurrence→delivery

Inputs: explicit user time intent, IANA timezone, now, DST policy, recurrence/misfire/cancel semantics. Parse→resolve decisive ambiguity→persist occurrence identity/state→lease/fence→dispatch→delivery receipt→next occurrence. Check gap/fold, just-before-due reschedule/revoke, clock/restart/overdue, duplicate worker, provider uncertainty, independent mixed request. Output: exact time vectors, scheduler code, observability and repair. Frozen simulation proves time logic; real scheduler/provider run needed for delivery claim.

## R-C06: image/animation/audio→runtime media

Inputs: immutable approved character/source, semantic scene/emotion, rights, target limits, audio intent. For visual generation use available required image workflow; DCC/compositing/encode separate operations. Freeze prompt/effective params and editable sources; check geometry/identity/alpha, all changed frames/loops in motion, actual streams/audio by listening, duration/decode/captions. Package exact output and manifest only after processes finish; hashes computed on frozen copies. Upload/publish only authorized; verify provider item/file/order/fingerprint separately. Failure repair changes one causal hypothesis rather than regenerate unaffected assets. Human visual/audio gaps remain gaps.

## R-C07: collaborative interaction→fair completion

Inputs: participant policy, roster, permitted private/group channels, action semantic version. Invite→record self-authored consent/choice→freeze round roster→private instructions receipts→first meaningful move→turn/state transitions→exit/timeout/restart→results. Test pending member/no DM access, newcomer, same button twice, revoked participant, independent reminder while game active, details text too long and delivery failure. Output: interaction model, templates/components, state traces and independent participant/audience QA. Never treat host agreement as every member’s choice.

## R-C08: source/build→controlled release→rollback

Inputs: exact source tree, env selectors, test reports on exact build, migration plan, authorization scope, provider target and previous version. Validate cold build, config/secrets separation, compatibility/DB backup and erasure retention; deployment action is replay-safe; observe actual source/build identity/health/logs; smoke real feature/delivery; retain rollback steps/stop. No test run implies an unrun live test. Failed provider response requires observation/reconcile before retry. Output: release receipts plus known limitations. Separate product, code, deployment and chat observation statuses.

## R-C09: incident→causal repair→continued operation

Inputs: actual symptom/version/baseline/trace. Classify reported vs reproduced vs hypothesis; smallest discriminating test; repair owned cause; independent retest on affected closure; migrate/rerun only invalidated work; update checkpoint and user-readable recovery. Measure latency, resource use, job queue/age, cost and quality separately. Recurring monitoring starts only if requested/actually scheduled. End-of-service/export/retention policies conditional but defined before committing ongoing service.

## Приймання інтегрованого сценарію

Зібрати input, conversation policy, memory state, tool effect, media, callback, scheduler, privacy і runtime в одному цільовому scenario/target. Check normal/negative/restart/revoke under realistic load/limits. Record target, exact code/assets/model versions, fixture/user context scope, commands, measured result, receiver and evidence. Passing parts do not imply their assembly passed. Перед великим каталогом виміряти повний pipeline одного репрезентативного елемента до integration/QA, а потім обґрунтувати темп і витрати.
