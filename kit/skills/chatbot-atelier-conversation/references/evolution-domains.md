# Detailed contracts for conversational assistant evolution

Use the current skill, lifecycle and team policy for routing and assignments. These domain reference sections are included in full for an independent evolution review.

## Source — domain-profile.md

### Conversational assistant profile

Refresh the profile for a major round and after release changes. Keep changing commit and service IDs in project records and omit secrets. Extend this inventory to the actual domain.

For each capability record the user's goal, natural request, tool/route, source path, storage, ownership and audience, result, failure/retry/cancel, test and status (`declared`, `implemented`, `locally_verified`, `deployed`, `observed`). Review registries, schemas, callbacks, workers, UI, commits and release notes to find the full current scope:

- Name, mention, reply and continuation, addressee, silence, useful initiative, tone and humor, and brief or detailed replies.
- Group and topic memory isolation, authorship and sources, consent, pause and forget, summaries and recall, private DM and permitted group visibility.
- Notes, tasks, shopping, inventory, expenses and receipts. Distinguish a list from an actual purchase.
- Single and recurring reminders, local time, skip, reschedule and overdue behavior, calendar access, events and group coordination.
- Games, scenarios and roles, all required participant choices, serial and parallel activity, results, polls, buttons, offers and details.
- Current web/search and browser interfaces, private connectors and authority for external actions.
- Photo, sticker and avatar work, OCR, pages and video segments, catalog, versions, originals, collage/cards and image generation.
- PDF/DOCX/XLSX reading, creation and edits, albums, video, captions, music and sound. Record deferred or unavailable features separately.
- Learning, exercises and progress, group projects, private drafts and inbox.
- Selected platform ingress and egress limits, idempotency, retries, workers, queues, cancel, receipts, restart and leases.
- Models and authorization, allowed providers, CPU/RAM/disk, TTL and cleanup, health and telemetry, versions, release and rollback.

#### Domain distinctions

1. «Додай молоко» refers to a list entry. «Завтра нагадай купити» refers to a reminder. Infer the natural intent without asking users to select an internal entity.
2. Verify permissions independently from name or administrative title. The output and notification follow the same allowed audience.
3. An artifact in storage still needs an accessible output or explicit access point in chat. Verify delivery or report its unknown status.
4. «Зробити відео» can mean montage or new generation. If context leaves a material choice, ask one deciding question. Check authority for paid generation separately.
5. Intent, consent, execution, verified result and delivery are separate. Reflect actual state in the response.
6. Free tools also use CPU and disk. Confirm paid provider scope and explain the limits that matter to the user's decision.

#### Specialist sources

Verify the selected platform's primary APIs, FFmpeg manuals, applicable Node, database and queue documentation, model APIs and runtime contracts. Progressive disclosure, error recovery and turn-taking research inform design. Verify the bot's experience and runtime through target-specific observation.

## Source — conversation-and-value.md

### Useful and natural conversation

#### The smallest complete result

For a simple request, perform the allowed work and briefly give the result. For a complex request, preserve its detail, questions and pace. Give a truthful account of anything still incomplete.

| Request | Natural response | Internal check |
|---|---|---|
| «Купити хліб, молоко і яйця» | «Додав: хліб, молоко, яйця.» | Verify the list was updated. Repetition adds no duplicates. |
| «Завтра о 9 нагадай про аптеку» | «Нагадаю завтра о 9:00.» | Establish date and local time and verify persisted job. |
| «Збери фотки в маленьке відео» | «Зберу. Які фото беремо?» only if context does not identify them. | Establish inputs and recipient. Avoid needless codec questions. |
| «З музикою» | Use the provided or accepted track, or ask for it. | Confirm an actual audio stream. |
| Video failure | «З роликом поки не вийшло: цей фрагмент не відкривається. Надішли його ще раз — спробую зібрати знову.» | Verify the cause and offer a retry only if it is feasible. |
| «Просто скажи, що думаєш» | A meaningful response in context. | Keep the conversation direct unless it needs a task or decision. |

These examples illustrate the interaction. Use the current dialogue language. State known causes and adapt humor to the situation.

Test ordinary labeled data without an imperative, such as «Список покупок: хліб, молоко» and «Список справ» followed by items. A current self-authored list needs no special command. Extract category and items from the actual text. A quotation, forward, translation, question or denial does not automatically authorize a write. Test each supported language with natural phrasing.

#### Audit the whole interaction

Check prompts, tool descriptions, examples and results, capabilities, welcome and help, release announcements, buttons, progress and typing, success, validators, callback expiry, worker failures, timeout and restart, grounding, delivery fallback and localization. Tool output itself can introduce technical wording.

Mention MP4/PDF, render or production pipeline, checks, IDs, revisions and step labels when requested or useful to a decision. A filename or export can identify its format. Explain the outcome in everyday language.

During a failure, give the actual result, limitation and practical way forward when useful. Claim persistence only with evidence. Preserve relevant character, context, stance, humor and warmth without invented experience or claims of consciousness. Offer at most one helpful extension to a simple result. Ask for the missing reminder time rather than an internal registry mode. Reuse provided photos, time and consent. Set clear, truthful progress and terminate the waiting state. Public announcements use recognizable situations and examples.

Exercise a simple question, emotional remark, joke, list, ambiguous time, long task, unsupported request, partial failure and recovery. Evaluate the full interaction including action result. Check every supported language independently.

#### Mixed everyday requests

Trace independent parts through intent, route, storage, confirmation, worker and delivery. For example, keep the reminder when adding purchases and report success of one part if another is blocked. Preserve causal dependencies, consent, provenance and time checks.

## Source — media-quality.md

### Sticker and media quality

#### Sticker records

Locate the best accepted version, current manifest, generator, key poses and settings, native set membership and file IDs, and actual bytes. Track accepted_unchanged, suspect, reproduced_defect, repaired, visually_reviewed and device_observed for each file. Evaluate motion separately from set size and FPS.

Inspect each changed or suspect item:

- Preserve character, proportions, face, paws, ears, garments and clean alpha. Check extra limbs, doubles and temporary identity shifts.
- Make emotion legible and appropriate to the scene. Different moods need meaningful expressions.
- Keep topology and objects consistent across key poses. Check incompatible-pose dissolve, ghosting, jumps, lost detail, stretching and noise.
- Verify useful anticipation, action, settle, trajectory and speed. Repair interpolation at its cause.
- Watch the complete beginning, end and loop in real and slow playback. Check clipping in motion.

Scan every file for decoding and timestamps, alpha and bounds, blank or black frames, repeats, frame differences and loop differences. Large differences indicate an item to inspect. Use contact sheets alongside playback. Inspect all replaced or flagged files and unchanged controls. A whole-pack verdict requires a record for every item.

Compare a repair against the reproduced defect and an accepted control. Fix the generator, rig, masks or pose correspondence where causal. Preserve meaningful motion and authorized pack scope. Use a technical mux or re-encode for format work and the applicable image workflow for drawing or editing a raster asset.

Verify current selected-channel media requirements before encode or publication. Apply a Telegram video-sticker profile only to Telegram. After publication verify item, hash, provider file and position. Preserve unknown mobile acceptance as a gap.

#### Lineage and frozen package

Preserve exact originals before replacing canonical output. Label video extracts as derived frames and newly drawn poses or layers as generated sources. Record input/output SHA, prompt and crop/resize procedure. Keep the original timestamp and recovered atlas claims bound to actual historic bytes. Save the prompt with the invocation.

Wait for every encoder to finish before freeze. Probe the final copied files, fully decode with failure on damage, verify frame count, order, duration and match to the accepted candidate. Bind proof to those bytes and SHA. Recheck all hashes after review, then finalize the immutable manifest. A later snapshot needs its own verification.

Keep an independently accepted FINAL and proof immutable. Record metadata or review repair as a targeted addendum with parent SHA and actual independent closure. Classify preview/handoff defects separately from defects in animation. Reproduce from preserved input, recipe and generator.

#### Video with music

Distinguish montage, new generation, source audio, music and voice synthesis. Deferred voice leaves an approved track in scope. Confirm authority for TTS or paid providers before use.

Verify inputs and duration, scene order, framing, captions, trim, loops, mix, fades and levels, mux, actual video and audio streams, duration, decode, size, access and delivery. Listen or analyze the actual sound. `-an` or a missing audio mapping leaves the music requirement unfulfilled.

Record actual track, license and source. Ask one useful question if a source is needed. Exercise the real available route before claiming the feature.

Derive the music requirement from current self-authored intent and goal version. A missing model flag does not retire the requirement. Bind ingress, track selection, decoder, verifier and delivery for each promised source, including audio extraction from video where supported. An explicit user change can remove music. A retry, unrelated context or erased source cannot change the intent.

Give jobs a clear start, completion, error and cancel. Preserve actor, topic, audience and provenance. Private output stays within its permitted audience. Retry and restart keep one message and return current bytes. Keep technical errors in logs and give the user a concise, accurate explanation.

## Source — judge-rubrics.md

### Domain reviewer rubrics

Use the current [team policy](team-policy.md) and [team profile](../assets/team-profile.json) for joint domain assignments and independent local acceptance. Evaluate the active criterion against the actual package. Leave unknowns open and keep blocking findings distinct.

| Criterion and competence | Check | Grounds to return |
|---|---|---|
| human_value — product discovery and Jobs-to-be-Done | Explain value in the participant's terms and exercise the real journey from need to accessible outcome. | The proposal reports only a module or format, or adds process without value. |
| natural_voice — conversation UX, Ukrainian pragmatics and empathy | Review complete Ukrainian and other supported language dialogues, including frustration, jokes, success and failure. | Technical step labels or JSON, clichés, false empathy or poorly timed humor. |
| context_relevance — turn-taking, reference and channel routing | Check wrong addressee, reply, prior offer, topic and appropriate silence. Reuse known input. | Interrupts another speaker, replies to the wrong person or loses the referent. |
| proportional_depth — cognitive load and information architecture | Compare simple and complex requests. Count unnecessary questions or taps and lost detail. | A simple answer requires a workflow or a complex task loses required content. |
| simple_first — progressive disclosure and task design | An ordinary request produces the basic result without a mode, quantity or format. Optional expansion is relevant. | The bot forces inventory, receipt, PDF or technical mode before the requested result. |
| practical_completion — list and task models and transactional CRUD | Exercise list plus reminder, storage, replay, view, partial failure and outcome of each independent part. | A list entry becomes a purchase or an independent part is lost. |
| multiuser_fairness — collaboration and multiplayer interaction | Each required participant chooses for themselves. Preserve applicable existing consent. | The system invents consent or lets a participant overwrite someone else's choice. |
| scheduling_fidelity — civil time, DST and durable jobs | Check tomorrow at nine, DST, repeat, skip, reschedule and overdue work, persisted job and actual delivery. | Host zone overrides the intended zone, duplicate dispatch or missing reminder. |
| capability_truth — tool affordances and capability contracts | Match each promise to ingress, tool, schema and runtime. Exercise montage, generation, voice and music separately. | The declaration has no available end-to-end path. |
| execution_truth — state machines, effects and distributed idempotency | Trace failure/recovery, queued/ready/delivered, partial success and the dependent step. | Invented success or an overall failure hides a completed independent result. |
| recovery_empathy — human factors and failure recovery | Exercise terminal failure, timeout or missing input. Give true status, feasible next step and end the wait. | Invented cause, raw error, hidden repair or a retry promise without capability. |
| interaction_continuity — channel event contract and optimistic concurrency | Test stale, repeated and expired buttons, details, cancel, replay and post-job reply. | Dead button, duplicated effect, or lost state or intent. |
| character_semantics — animation direction, silhouette and legible emotion | Compare preview, motion and scene against accepted identity and unique emotions. | Identity changes, extra limb, scene mismatches emoji, or a reused pose obscures distinct intent. |
| temporal_quality — animation, optical flow and compositing | Watch every changed sequence. Review key-pose correspondence, matte and loop against an old control. | Ghosting, deformation, jumps, contact sheet instead of playback or whole-image wobble instead of the intended action. |
| audiovisual_fidelity — editing and FFmpeg filters and muxing | Inspect actual streams, signal, timing, duration, clipping, source meaning and decode for provided music plus video. | Silent media presented as musical, missing frames or captions, or audio diverges from source. |
| media_delivery — platform media delivery and integrity | Recipient can access the actual file. Match pack item, hash, file_id and order and observe delivery receipt. | Catalog or count substitutes for the file, or private media becomes group-visible. |
| audience_privacy — authorization and information flow | Check actor, topic, group and private scope across reads, jobs, output, progress, errors and cache. | Scope expansion or disclosure even through a status message. |
| consent_authority — consent lifecycle and authority | Execute exact authorized work and preserve consent on external and private boundaries. | Fabricated consent, needless repeated approval or an out-of-scope action. |
| source_grounding — lineage, factuality and provenance | Bind result to source, quotes, dates and originals. Track audio/input lineage into output. | Invented URL, track or fact, or missing derived lineage. |
| forgetting_integrity — erasure and invalidation | Forget, pause or revoke while queued, running or retrying. Observe outputs and notices. | Deleted information reused or result delivered after effective revocation. |
| bounded_resources — performance and admission control | Measure CPU, RAM, disk and queue on the actual path, concurrent chat and media, input size and duration. | Unbounded work, blocked chat or an unrelated benchmark used as local evidence. |
| lifecycle_reliability — jobs, leases and recovery | Test crash, timeout or cancel, stale revision or source, duplicate delivery and cleanup. | Indefinite running or typing, duplicate, silent failure or cached success after cancellation. |
| provider_constraints — model compatibility and cost | Verify configured and actual models and that deferred voice or paid extensions stay outside execution. | Unapproved paid provider, prohibited model or unauthorized spending. |
| version_continuity — release, compatibility and rollback | Compare diff, versions, old data/buttons/assets, changelog and live commit. Exercise the rollback route. | Feature or history lost, or an undeployed version claimed live. |

Record strongest_objection, exact evidence_ids, scope, uncertainty and reversal_condition with each verdict. Verify source, version and context. Documentation supports the stated contract, execution supports behavior on its actual boundary, and human evaluation supports observed perception. Verify competence and real independence separately from role names.
