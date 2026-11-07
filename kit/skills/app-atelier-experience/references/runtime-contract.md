# Локальний runtime App Atelier

Чинні формати: `app-atelier-profile/1`, `app-atelier-state/1` та `app-atelier-economics/1`. Інші версії відхиляються; окремого читача попередніх форматів або автоматичного перетворення результатів немає. Номер формату незалежний від редакції інструментарію.

Python3.9+ stdlib, macOS/Linux POSIX flock. Інструменти не викликають LLM, network, зовнішні effects, setup акаунтів чи платежі. CLI pin-ить actual source/authority, але не автентифікує людину. Перед використанням прочитати `python3 <actual-skill>/scripts/state.py --help` і підкомандну довідку.

## Project paths
`--project ABS` вказати перед підкомандою; папка має фактично існувати. `.appatelier/profile.json` - власний імпортований профіль, `.appatelier/state.json` - canonical ledger. Namespaces requirement, decision, knowledge, job, artifact, evidence, execution, capability, grant, effect є ключами цього ledger, а не окремими registry-файлами. Product artifacts зберігати звичайними versioned файлами й реєструвати relative path/hash.

Усі put records містять id, source, verbatim. Source - реальне походження повідомлення/файла/спостереження; не вигадувати позитивної згоди. Semantic definition і похідні hashes визначає actual source state.py; неприсутні поля не вважати перевіреними.

## Основні команди
- `init --profile FILE`: імпортувати supported app-atelier-profile/1, створити state, seed requirements pending. Не перезаписує наявне й не дає execution.
- `status`: read-only статус profile/pause/pending/unknown/stale. `context --query TEXT`: вибірка records; потім прочитати їхні залежності й актуальні sources, а не тільки ranking.
- `put --kind KIND --record FILE`: typed current record, збереження попередніх revisions у history. Фактичні outputs/evidence спершу створити інструментами, потім зареєструвати.
- `subject --kind decision|execution|effect|grant|profile|requirement --record FILE`: отримати exact subject/hash. Додає актуальні artifact hashes для effect/decision. Не створює authority.
- `gate --job ID`: показати blockers. `start --job ID`: записати running після gate, не виконує task. `complete --job ID`: тільки після actual outputs/current proofs і fulfillment.
- `phase-check --phase NAME`, `phase-complete --phase NAME`: due must і всі declared jobs; поточні позначення фаз `PH-*` нормалізуються. Gate профілю й залежності не можна обійти omission decision_ids.
- `pause --boundary now|after_job|after_phase|after_artifact --target ID --record FILE`: now без target; exact future boundary. `resume --record FILE`: фактична user request; unknown effects спершу reconcile. Future stop не послаблює active pause.
- `dispatch --effect ID`: current grant/capability/hashes/caps -> pending, executes=false. Потім агент виконує exact authorized host call один раз.
- `receipt --effect ID --record FILE`: provider_ref/proof_path, outcome succeeded/failed/unknown; failed потребує confirmed_no_effect. `reconcile --effect ID --record FILE`: actual read_only_status_check=true, решта полів receipt. Не дає replay grant.
- `amend-profile --profile FILE --record FILE`: тільки exact user authority на old/new subject. Повертає `impact`: changed fields/requirements, affected phases, invalidated та carried-forward IDs. Явно неопераційні top-level `metadata`, `annotations`, `audit_annotation` не змінюють виконуваний scope; переносити до них продуктові правила чи права заборонено. Зміни phase gates і requirements звіряються з фактичними залежностями; невідомі поля, глобальні constraints або вимога без доведеної межі впливу дають conservative global invalidation. Чинні незалежні bindings переносяться лише з попереднього current profile, історія й authority subjects зберігаються; раніше stale records не оживають. Не змінювати профіль raw file write.

## Records
Requirement: intent, priority, acceptance, owner, due_phase/phase, emphasis/applicability за змістом, evidence_ids і status. Зміна semantic must потребує change_authority на exact subject; старі proofs pin-ять requirement_hashes і не закривають нове визначення.

Execution: scope, phase_ids, authority, status=current. Authority має actor=user, source, verbatim, subject_sha256 та позитивне рішення; subject рахується CLI з фактичних параметрів. Factory approval не підставляти як product execution.

Decision: category, scope, question, options, status=confirmed, answer, authority, artifact_ids за застосовності. Необов'язкові `requirement_ids` і `job_ids` визначають явні межі залежностей та, коли задані, входять у subject. Category direction/concept/design/budget/release_readiness; exact answer та accepted bytes входять у subject. Рішення актуальне лише для свого scope/profile/current artifacts. Неприв'язані рішення за матеріальної зміни requirements переоцінюються консервативно.

Job: phase, scope, owner, goal, execution_id; lists depends_on, requirement_ids, fulfills_requirements, artifact_ids, evidence_ids, decision_ids, effect_ids; inputs=[{path,sha256}], human_experiment, requires_owner_operations за змістом. Effect dependencies потребують відомого terminal результату й current proof. Experiment має metric/threshold/horizon/budget_usd/stop до старту. Не приховувати дію під хибним phase/false flag: агент відповідає за відповідність запису реальному intent.

Artifact: path, author_ids, optional supplied sha256 must match actual file. Не використовувати ledger internals як product outputs. Evidence: artifact_ids, requirement_ids за застосовності, proof_path, observer, method, environment, status pass/fail/blocked, independent boolean. CLI pin-ить artifact/proof/requirement hashes; незалежний observer не є автором.

Capability: scope, environment, effect_types, available boolean; записувати лише фактичну перевірену можливість. Effect: type, scope, target, parameters, artifact_ids, spend_usd, recurring_usd, idempotency_key, grant_id; current artifact_hashes входять у exact subject. Grant: effect_id, subject_sha256 від effect subject, capability_id, authority на grant subject, status=current. Зміна bytes/parameters/scope/cost не використовує старий grant.

Knowledge: text, confidence, scope, impact_ids, source/verbatim й pinned inputs за потреби. Агент сам оцінює зміст і impact, відкриває affected requirements/reviews/jobs; факт додавання запису не доводить його достовірності або автоматичної семантичної інвалідації. Для affected requirement зі старим semantic intent записати status=stale, потім створити адресний repair і новий proof; не змінювати user must без належного рішення.

## Межі
Зміна current artifact/proof/requirement/decision/dependency робить залежний closure stale. Не використовувати локальні JSON як самостійний доказ реальної волі людини або стану провайдера. OS lock/atomic replacement захищають cooperative local writers, а не hostile same-user процес, який контролює весь workspace. Дуже великий ledger потребує контрольованого архівування зі збереженням посилань/прав; ліміт не обходити знищенням історії.

Job на `start` зберігає `input_requirement_hashes` усіх оголошених inputs. Must/emphasized inputs мають бути current до залежної роботи; `fulfills_requirements` можуть бути pending на старті, але закриті до completion. Незакритий should/explore input не є вимогою завершення: він показується в `optional_input_gaps`, а зміна його визначення інвалідує job за pin. Admission, completion і freshness застосовують ту саму семантику. Старий running/completed job із призначеними вимогами без input snapshot потребує адресного repair/reconciliation; відсутню історичну прив'язку не вигадувати.

На `complete` controller створює `completion_hashes` outputs і `completion_evidence_hashes` усіх прийнятих evidence records. Semantic pin включає observer, independent, method, environment, status, actual proof path/hash, artifact/requirement bindings, source/verbatim та інші змістові поля; виключає лише controller bookkeeping `_profile_sha256`, `created_at`, `updated_at`, `recorded_at`. Час фактичного спостереження є змістовим полем і має окреме ім'я, наприклад `observed_at`. Наступні status/dependency/phase checks повторно перевіряють current proofs, покриття кожного output і вимогу незалежного reviewer, а також точну відповідність snapshot. Заміна evidence під старим ID робить залежне завершення stale; незалежні jobs не інвалідуються. Bookkeeping-only profile carry не змінює semantic pin. Історичний completed job без evidence snapshot потребує адресного repair із фактичними proofs; заднім числом snapshot не створювати.

Економічний `check_model.py` у директорі приймає JSON numbers, decimal strings і Python `Decimal`; обчислює до порівняння/ceil у base-10 Decimal з bounded precision/range. Numeric display має шість знаків ROUND_HALF_EVEN, `exact_decimal` зберігає неокруглені значення рішень. Provider per-transaction rounding не припускається: його реальну конвенцію потрібно явно додати у предметну модель. Результат залишається розрахунком припущень, не доказом попиту або гарантованого доходу.

## Інші інструменти
`doctor.py [--project ABS] [--skill-root ABS] [--strict]` робить read-only інвентар tools/duplicates, не акаунтів/секретів. Доступний у root kit і director/scripts; не припускати його наявності в інших standalone modules.

`check_model.py --example` показує точний JSON app-atelier-economics/1; `--model FILE [--target-profit N]` обчислює USD/month scenarios. Обов’язкові датовані assumptions, paid/free cohorts, price, fees/refunds, variable/fixed/acquisition costs. Utility застосовує commission до retained revenue після refunds; реальну provider convention перевірити й відмінності врахувати у моделі. One-time paid_users - нові оплачувані units поточного місяця, історичні активні власники мають власний cost cohort. Required scale фіксує інші припущення; це не доказ попиту/доходу. Інструмент у root kit і director/scripts.
