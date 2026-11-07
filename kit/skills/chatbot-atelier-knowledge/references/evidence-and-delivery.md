# Докази, рішення й відновлення

Організація поточних запусків: [team-policy.md](team-policy.md) і [team-profile.json](../assets/team-profile.json). Усі предметні вимоги та докази нижче зберігаються; Current scope використовує grouped domain assignments та локальне незалежне приймання.

Поточний round має `schema_version="chatbot.round/1"`; brief {id,version,user_intent,baseline,constraints,authorization}; requirements (усі 24 baseline IDs та прийняті project-owned IDs зі state=active/unchanged і reason); findings; decisions; changes; evidence; runs; reviews; обов’язковий team_policy; completion; checkpoint. Local scope має точний короткий зміст без заяви повної ради, але той самий чинний формат і явну карту впливу.

- Finding: id, requirement_ids, version, reported/reproduced/hypothesis/preference, scenario, actual/expected, evidence_ids, severity, cause/falsifier, audit_status.
- Decision: id, finding_ids, options/chosen/reason, expert_sources, tradeoffs, affected IDs, verification/rollback. URL без прочитання не є джерелом.
- Evidence: id, version/hash, kind (source/code/execution/human/telemetry), provenance (reported/inspected/reproduced), artifact, procedure/result/limitations. tests_green не означає audio_audible чи natural_conversation.
- Run: `id`, `actor_id`, `kind`, `status`, `requirement_ids`, `domain_ids`, `output_ref`, `output_sha256`; для належних review також package_hash/verdict/context. Aliases role/artifact/agent_id не є current fields. Невиконане лишати pending; не вигадувати UUID.
- Review: requirement_id, actor_id, run_id, package_hash, verdict (accept/revise/block/unknown), evidence_ids, strongest_objection, uncertainty/reversal_condition. Не усереднювати.
- Completion: stage (prepared/locally_verified/independently_reviewed/deployed/observed_in_chat), scope, status, unresolved_requirement_ids, deployed_version, dissent. `assessments` окремо може містити specification/code/integration/device/human. Для кожної осі потрібні status, scope, evidence_ids; passed потребує успішного доказу, human/device — належного actual_observation_ref. Відсутня вісь означає not assessed; стадія не успадковує їй pass.

Changes містить before/after, артефакти, вплив усіх active/unchanged. Material revision інвалідує залежні evidence/reviews; unchanged має причину. Після відновлення звірити checkpoint із repo/deploy й паралельними змінами, продовжити незалежну роботу.

До ремонту — baseline і аудит/відтворення або явне побажання. До приймання — конкретний diff/output, значущі checks, межі. До independent claim — actual незалежні runs. До релізу — чинний дозвіл, rollback, потрібні checks/assets/міграції. До done — live version/receipt, якщо scope включав публікацію; інакше точно назвати підготовлену стадію.

Непов’язаний блокер не зупиняє всю роботу. Недоступний деплой не заважає виправленню; дефект стікера не дозволяє прибрати календарі. Не придумувати додатковий permission gate.

Звітувати по користі й доказах: «відео перевірене з наданою доріжкою», «переглянуті N/M анімацій; решта ще не прийнята». Інженерний журнал відокремити від анонсу. Не включати секрети/приватну переписку в dossier; не розсилати без дозволу.

## Предметні вимоги та точні докази

Канонічні 24 IDs залишаються незмінними. Кожний додатковий project-owned рядок у requirements має сталі id, source_ref, owner, domain_id, acceptance, negative_probe, state і reason. Посилання source_ref звірити з фактичним прийнятим джерелом; написаний агентом рядок не створює згоди. `teamctl.py plan` переносить domain_id додаткової вимоги до assignment; canonical domain ownership не перевизначається. На independent completion нова вимога має те саме повне приймання, actual actors і primary evidence, що й baseline.

Для `chatbot.blueprint/3` specified — завершена предметна декларація без вигаданих attempts. Кожна active requirement має зворотне покриття systems, journeys, operations та recipes. За explicit deferred/excluded/not_applicable потрібні scope_decision_ref і reason; deferred також due_gate. Наявність рядка не автентифікує реальне рішення; прийнятий scope перевіряється за джерелом.

На integrated journey містить explicit operation_ids, поточні attempt_ids та evidence_ids і verification=passed. Кожний вибраний attempt має result=passed, actual_run_id, input_snapshot.hash, effective_parameters, зв’язані operation_ids/recipe_ids та subject {brief_id,brief_version,brief_sha256}. brief_sha256 обчислює `brief_hash(brief)` у check_chat_contract.py: SHA-256 UTF-8 JSON із sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False. ID/revision/hash прив’язують доказ до поточного brief; вони не засвідчують авторизацію користувача.

Evidence має artifact, SHA-256 вихідного артефакта, procedure/result/limitations та exact attempt_ids/attempt_sha256s. Кожний attempt_sha256s[attempt_id] дорівнює `attempt_hash(attempt)` за тими самими canonical JSON правилами. Зміна входів, effective parameters, scope або outcome не використовує старий proof. Поточні journey attempts з failed/unknown/cancelled/uncertain/pending/running і пов’язані unsuccessful evidence блокують integrated. Історичні невдалі спроби зберігаються в attempts; вони не підставляються як прийнята поточна path. Кожна claimed operation має exercised capability і успішний linked execution/integration/device/live_provider proof; source review чи human verdict самі не доводять виконання.

Успішна структурна перевірка цих зв’язків не перевіряє байти зовнішнього артефакта, правдивість provider receipt, людське схвалення чи реальну якість. Їх треба звірити відповідним tool/read-back/independent observation. Prepared round, specified blueprint, integrated execution, live availability й human assessment відображаються окремо.

Виконувані синтетичні приклади поточного контракту: `specified()` та `integrated()` у scripts/test_chat_contract.py; `extended_prepared()` і `independently_reviewed()` у scripts/test_round_current.py. Це test fixtures із явною міткою SYNTHETIC, не production evidence і не підстава вигадувати actual run.

## Успіх і актуальність review

Round evidence.result має явний статус із pass/passed/accept/accepted/observed/fail/failed/reject/rejected/pending/not_run/running/unknown/uncertain/cancelled/inconclusive/blocked. Детальні виміри й пояснення зберігати окремо; довільний рядок не є outcome. Для accepting review потрібні непорожні валідні evidence IDs із positive result pass/passed/accept/accepted. observed саме по собі не означає приймання критерію; failed/not_run/unknown зберігаються чесно без promotion.

Current run має declared input_snapshot за [протоколом](protocols.md) і actual frozen output. Для accepting QA/judge та інших споживачів це точна прив’язка перевірених inputs до current requirements/components/producer outputs/primary evidence. Після зміни target чи primary observation повторне обчислення hashes/package hash не заміняє реальний новий review. Producer inputs зберігаються історично, щоб його власний легітимний запис не робив його результат автоматично stale; якість нового target підтверджує належний свіжий споживач.
