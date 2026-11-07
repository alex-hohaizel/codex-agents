# Робочий сценарій єдиного агента

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

Це внутрішня інструкція. Користувач ставить мету звичайною мовою; агент сам знаходить фактичну навичку, підготовляє records і запускає потрібні tools. `atelier.py` веде облік і шлюзи, а не розуміє текст, не викликає LLM і не виконує зовнішні дії. Підтримуваний локальний runtime — Python 3 стандартної бібліотеки, POSIX flock на Linux/macOS. Для іншого host перевірити можливість або передати проект у сумісне середовище; не заявляти нативну Windows-сумісність.

## 1. Намір і поточний проект

Прочитати project AGENTS, canonical state/decisions/requirements, handoff, originals і [контракт досвіду](experience-contract.md). Зберегти дослівний current user source; класифікувати намір як new_project, intake, stage, research, feature, incident або resume. Вибрати точні stage/scope/operation. `assets/stage-catalog.json` визначає предметну skill, inputs, outputs, choices, capabilities, gaps і return routes. Людські слова інтерпретує агент: за неоднозначності з суттєво різними результатами поставити питання, не вгадувати його через keyword regex.

Розрізняти: запам’ятати фаворита; продовжити пошук; обрати концепт для виробництва; повністю припинити пошук; змінити сам workflow. Цей toolkit не дозволяє самовільно відновити гру лише через наявність її архіву. Матеріальні defaults одного проєкту не успадковувати іншими іграми; історичний приклад див. у [джерелах спадщини](historical-project-profiles.md).

## 2. Мінімальний реальний цикл

Знайти абсолютний шлях активної skill зі списку хоста. Прочитати `scripts/atelier.py --help`, а форми records — `assets/runtime-records.json`. Нижче внутрішні команди; ATELIER/PROJECT — змінні, яким агент надає фактичні шляхи, не універсальні команди для копіювання користувачем.

```bash
python3 "$ATELIER" project-init "$PROJECT" --project-id my-game
python3 "$ATELIER" intake "$PROJECT" --source /absolute/path/original.zip --record provenance.json
python3 "$ATELIER" route "$PROJECT" --intent intent.json
python3 "$ATELIER" ledger "$PROJECT" --kind requirement --record requirement.json
python3 "$ATELIER" task "$PROJECT" --record task.json
python3 "$ATELIER" context "$PROJECT" --stage concepts
python3 "$ATELIER" readiness "$PROJECT" --task TASK-CONCEPT
python3 "$ATELIER" start "$PROJECT" --task TASK-CONCEPT
```

`project-init` лише для нового sidecar; існуючий не перезаписувати. `intake` перевіряє безпечні шляхи/ліміти/bytes, переносить originals з походженням і не виконує imported scripts. Agent додатково перевіряє зміст/права/версію. Після start фактично прочитати обрану skill і виконати її предметну роботу. Записати реальні файли та перевірку:

```bash
python3 "$ATELIER" artifact "$PROJECT" --record artifact.json
python3 "$ATELIER" evidence "$PROJECT" --record evidence.json
python3 "$ATELIER" ledger "$PROJECT" --kind requirement --record closed-requirement.json
python3 "$ATELIER" complete "$PROJECT" --task TASK-CONCEPT --evidence EV-CONCEPT
python3 "$ATELIER" brief "$PROJECT"
```

Task містить owner/skill/goal/scope/dependencies, due requirements/decisions/evidence/capabilities/modalities, outputs і stop. `fulfills_requirements` дозволяє працювати над pending must; completion потребує actual closure. Чужий pass не створювати зі свого self-check. Exit 0 означає read/record, 1 — blocked gate/invalid handoff, 2 — invalid request; жодне не доводить якість художнього задуму або успіх у магазині.

`required_modalities` використовує той самий registry, що й evidence: `visual`, `audio`, `haptic`, `play`, `device`, `build`, `document`, `external_receipt`. Непідтримувана назва відхиляється до реєстрації task; legacy task із такою назвою не проходить readiness/start/complete. `simulation` може описувати фактичний метод, а не нову modality: JSON результат локальної симуляції чесно записують як `document` із точним method/source; це не створює play/device/native-build доказу.

Для вже наявного planned/running task дозволена лише вузька команда `reconcile-task-modalities PROJECT --record correction.json`. Спочатку отримати актуальні `task_token` і `task_status` через readiness; приклад форми correction:

```json
{
  "id": "TASK-SYSTEMS-SPIKE",
  "expected_task_token": "<exact current task_token from readiness>",
  "expected_status": "running",
  "modality_replacements": {"simulation": ["document"]},
  "source": "<actual original task and observed proof source>",
  "reason": "<why these supported modalities truthfully represent the required proof>"
}
```

Mapping має покрити рівно всі непідтримувані назви непорожніми supported replacements. Чинні supported requirements, independent review, outputs, scope/goal/authority, dependencies, started state, pause та effects зберігаються; будь-які інші request fields відхиляються. Завершений/stale task, змінений token/status, unresolved suite/integrity або task-linked pending/unknown external outcome блокують correction. Інший pending effect не дозволяється виконати чи повторити через цю команду. Correction додає journal та exact old/new audit, інвалідує лише залежну closure і не починає/повторює/завершує роботу. Після нього перечитати readiness; наявний реальний proof можна використати лише за звичайних exact scope/coverage/independence gates. Зміну суті продуктового proof promise такою технічною корекцією не прикривати; для матеріальної зміни потрібне чинне відповідне рішення.

## 3. Матеріальні питання

Перед залежним кроком сформувати decision packet: конкретна невизначеність; чому відповідь змінить результат; 2–3 реальні опції й наслідки; рекомендація; exact scope/inputs/hash; що можна продовжити незалежно. Наприклад, engine обирати після platform/art/device/physics feasibility; не питати про кожен оборотний helper. Чинну згоду імпортувати з точного джерела.

`decision --record` створює pending, а `confirm --id --choice --scope --decision-revision --project-revision --authority` записує фактичну відповідь. Перед confirm перечитати поточні revisions. JSON не створює дозвіл. Canonical decision ID у старому registry має exact canonical_ref/sha; sidecar не підмінює його. Позитивний дозвіл на effect описує `approval:{option:"approve",effects:["upload"],artifact_ids:["ART-ID"]}` з фактичними значеннями; record pin-ить точні hashes. Підтверджений варіант «ні» нічого не дозволяє. Для master потрібні effects:["master"], exact approved_sha256 і scope; derivative має новий ID. Для production потрібні окремі рішення припинити пошук та обрати концепт; список saved_only цього не виконує. `full_concepts` є завершенням C1 кандидатів на stage=concepts і доступний до вибору гри. Operation успадковується matching task із тим самим source/scope: його не можна мовчки знизити до visual_previews. Вибір production лишається окремим рішенням.

## 4. Нове знання і контекст

`ledger --kind knowledge --record` отримує source/verbatim/text/scope/confidence/stages/impact_ids/impact_reason. Перед кожним job `context` і `readiness` звіряють актуальні знання, canonical files, artifact/proof hashes і suite lock. Agent перевіряє семантичний impact, не тільки файли: нова вимога доступності може змінити input/UI/audio/haptic/economy journey. Реєструвати залежності spec → asset/code → evidence; не знімати must заради зеленого статусу.

Runtime lock pin-ить точні bytes усіх executable Python та нормативних ресурсів із `assets/suite-shared-paths.json`. Stage-local guides, SKILL і UI належать окремому `observed_suite_sources` provenance; їхня відмінність між delivery forms не змінює shared runtime identity. Зміна executable/shared contract вимагає impact review; `refresh --accept-suite-update --authority REVIEW_SOURCE [--impact ID]` записує виконану агентом перевірку. Виправлення інструкції без семантичного впливу не потребує повторного user consent. Якщо вплив є — перелічити IDs та відкрити відповідні докази. State у `.gameatelier/orchestrator` зберігає journal/checkpoint; старі canonical файли не перезаписуються. `context --query` — structured/lexical retrieval із closure, не vector RAG. Додавати інші системи лише після виміряної потреби, з міграцією й тестами.

Для task, що потребує незалежного висновку, явно задати `independent_review_required:true`. Bounded self-observation допустиме як self-check іншої чернетки, але не незалежний pass. Accepted stage gate звіряє due runtime must/decisions тим самим selector stage/stages/scope, що й task readiness, і актуальний `stage_context_snapshot` з `context --stage STAGE --scope SCOPE`; за наявності stage records пакет pin-ить його в optional `manifest.project_context`. При зміні контексту перебудувати відповідні package records/reviews та snapshot, не просто переклеїти hash. Старі порожні-ledger handoff 1.0.0 сумісні; їх історія не доводить нові вимоги.

## 5. Зовнішня дія і невідомий результат

Спочатку підготувати reviewable outputs, task/action, точні параметри акаунта/каналу/збірки/ціни/даних. Capability перевірити реальним способом; доступність ≠ дозвіл. Якщо чинного дозволу бракує, одне конкретне питання після готовності пакета. Записати action+decision, почати task, `dispatch --id --project-revision` заносить pending **до** фактичного tool call. Агент викликає зовнішній tool один раз і відразу записує `receipt --outcome succeeded|failed|unknown --record` із provider proof. Runtime нічого не надсилає.

Pending/unknown після розриву зв’язку — read-only status query, не повторний upload/payment/deploy. Лише actual reconciliation proof з `reconciled=true` закриває невідомий outcome. Немає exactly-once гарантії від одного local JSON; використовувати provider idempotency/deduplication там, де підтримується. Секрети/ключі не потрапляють у records/ZIP/chat.

## 6. Паузи й повернення

`pause --when now` зупиняє work gates; `--when artifact --target ART-ID` — після реєстрації саме цього final/reference; `--when stage --target STAGE` — лише після фактичного accepted stage-check того самого проекту. Для «зупинись після картинок» agent ставить точний фінальний artifact ID, не чекає accepted production concept. Не переходити далі через те, що пауза ще не викликала загальний stage acceptance.

Зберегти readable checkpoint: готове, поточне, pending questions/jobs/effects, stop, next action, inputs/toolkit versions і повернення. `resume` звіряє стан, не повторює виконане й не знімає матеріальних blockers. Дозволено завершити безпечний запис доказу/receipt після паузи, але не починати новий job.

## 7. Ручний міст замість недоступної можливості

`handoff --record` створює читабельний checkpoint. Record має ID, exact environment, absolute working_path, argv command, numbered launch_steps, expected_result, absolute return_path, return_instructions, scope і missing_capability. Agent додає реальний portable package та integrity check через `pipeline.py`; команда не створює його сама.

Показати: «Відкрийте цей проект у …; додайте ці файли; виконайте …; очікується …; поверніть …». Для MFA/юридичного підпису/API без потрібних можливостей це лише конкретний заблокований крок; дозволену підготовку завершити. Після повернення перевірити файли/hashes/provider state і продовжити у тому ж scope. Звичайна назва Work/Codex або скрипта без launch/return не є bridge.

## 8. Адресний розвиток випущеної гри

Інцидент починається з production build ID/telemetry/repro/authority, далі обмежений route до design/assets/build/QA/release. Feature або сезон зберігають accepted art/input/audio/progression/economy promise; зміна цього promise є окремою розвилкою. Знову проходять лише зачеплені acceptance gates. Реальний постійний monitoring потребує запущеної дозволеної scheduler/service capability; локальний CLI не є фоновим оператором.


## Типізовані перевірки до вибору гри

Для незалежного C1 огляду використовувати QA operation `design_review`; для огляду предметних контрактів — `contract_review`. Task успадковує exact source/scope/operation; `work_class=review` не вимагає production choice та не може містити external_actions. Звичайний full-stage QA, build/release і operation `production` зберігають свої production gates. Review не означає дозвіл реалізувати чи випустити гру.

Завершений C1 одного кандидата передається як concepts `game_model.acceptance_scope=candidate_completion` з конкретними scope_ref/scope_description, повними C1 rules і due evidence. Це не selected production concept. Full-stage selected handoff та пізні production gates залишаються окремими.

## Явне оновлення наявного workflow state

Установлення навичок не змінює проєктні state чи game saves. Для native state schema2.0 існує лише явно підтриманий workflow upgrade4.2→4.3. Команда `workflow-upgrade PROJECT` спочатку повертає read-only preview з source_state_sha256, target_suite_sha256, pause й незвіреними effects. Відсутність доступного шляху не дозволяє мовчазного reset.

Після фактичного review викликати `workflow-upgrade PROJECT --apply --expected-state-hash SOURCE_SHA --target-suite-hash TARGET_SHA --authority ACTUAL_REVIEW_SOURCE [--impact ID]`. Обидва SHA беруться з актуального preview. Apply перевіряє journal/snapshot, незмінність джерела й цільової suite, зберігає exact backup та додає journal receipt. Невідомі/попередні схеми не конвертуються. Повтор того самого receipt є no-op; чужий/змінений input вимагає нового preview.

Accepted originals, IDs, decisions, favorites, pause, pending/unknown effects та історія зберігаються; код гри не виконується і жодний effect не повторюється. Нові hashes не створюють людського погодження. Лише названі reviewed impact IDs і їхня залежна closure стають stale; фактична зміна files/proofs під час source reconciliation також відображається. Історичні stage checks залишаються історією й не сертифікуються новим toolkit автоматично. Після apply перевірити context/readiness exact наступної задачі; активна pause знімається окремим дозволеним resume.


Completion evidence має бути застосовним до exact task stage/scope. Project-scoped proof може покривати bounded task; доказ іншого candidate scope — ні. QA proof може явно оголосити `stages:["qa","concepts"]`, якщо фактичний review справді покриває обидва споживачі. Primary `stage` завжди застосовний; `stages` його доповнює. Вхідний upstream proof залишається required_evidence залежністю, а не автоматичним доказом завершення нового результату. Та сама застосовність перевіряється для met requirement closure та stage acceptance, включно з відновленими native records. Зміна metadata не створює відсутнього спостереження.


Canonical links зберігають original full-file `canonical_sha256`, exact `canonical_record_sha256` і `canonical_envelope_sha256`; `canonical_observed_sha256` є поточним source provenance, не новою згодою. За явного items/name container зміна лише сусіднього рядка не інвалідує незмінний record і його незалежні результати. Глобальний schema/policy envelope, власний row чи declared depends_on змінюють відповідну closure. Bare/unknown record shapes, незрозумілі додаткові поля та попередні links без fragment pins залишаються conservative і потребують exact reconciliation; їх не підв’язувати до нового source мовчки. Канонічні залежності йдуть у runtime ledger, а missing upstream records є blocker. Оригінальні канонічні файли цей runtime не переписує.
