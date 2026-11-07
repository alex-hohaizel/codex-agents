# Чинні формати роботи

Підтримується один поточний формат кожного типу; читачів попередніх форматів і автоматичних міграцій результатів немає. Номер формату не є номером інструментарію. `chatbot.blueprint/3`, `chatbot.round/1`, `chatbot.team/1`, `chatbot.team-profile/1`, `chatbot.review/1` та `chatbot.adapter/1` є різними поточними контрактами, а не шарами зворотної сумісності. `depth/2` визначено спільним graph contract.

## Blueprint і адаптер

`chatbot.blueprint/3` — предметна модель, applicability, точні правила/перетини, journeys, operations/recipes/attempts/evidence і draft/specified/integrated readiness. `check_chat_contract.py` відхиляє інший format identifier. `chatbot.adapter/1` — конкретна обрана платформа/account/environment та її trust/ack/dispatch/delivery/probe contract; `check_platform_adapter.py` не доводить фактичну підтримку API чи правдивість receipts.

## Round і команда

`chatbot.round/1` містить brief,24 canonical requirement IDs плюс прийняті project-owned IDs та їх active/unchanged impact, findings/decisions/changes/evidence/runs/reviews, обов'язковий `team_policy`, completion і checkpoint. `team_policy.schema_version=chatbot.team/1`; точний profile_version читається з поточного `assets/team-profile.json`, а не з версії навички.

Один canonical run: `id`, `actor_id`, `kind`, `status`, `requirement_ids`, `domain_ids`, `output_ref`, `output_sha256`; після фактичного приймання — verdict і належні review поля. Старі field aliases не читаються. Авторство й незалежність не встановлюються назвою role. `completion.stage` описує реально досягнутий рівень, `completion.status` — scoped_complete/stage_complete; вони не взаємозамінні.

`python3 scripts/teamctl.py plan ROUND.json --kind local --active ID` створює лише current draft plan; `hashes` фіксує actual bytes, `freeze` — package hash; `check` перевіряє team records. `python3 scripts/check_round.py ROUND.json` завжди потребує current team policy; необов'язкової гілки приймання без нього немає. Сам факт PASS не підтверджує природність, UX, delivery або правдивість авторських заяв.

`chatbot.review/1` дозволяє переносити **актуальний доказ того самого формату** тільки за exact незмінних inputs/залежностей/environment. Це повторне використання перевіреного результату поточного проєкту, а не підтримка попередніх schemas. Зміни, unknown dependency або відкликання даних інвалідовують відповідне приймання.

## Непідтриманий вхід і наявний бот

Якщо дано результат іншого формату, відхилити його як машинний input і запропонувати заново інстанціювати поточну модель з авторитетних вимог та фактичних джерел. Не встановлювати додаткових адаптерів чи зберігати старі readers заради такого імпорту. Оригінальний файл користувача не редагувати й не видаляти автоматично.

Наявний бот не вимагає старого агентського dossier. Відновити current repo/tree/config/прийняті матеріали/виконані checks/provider state і створити поточний checkpoint. Реальні дані, стабільні requirement IDs, поведінка та потрібні продукту DB/schema migrations зберігаються за своїми контрактами; вимкнення підтримки старих агентських output formats не дозволяє втратити прогрес або дані бота.

## Типізовані зв’язки і межі готовності

Blueprint systems.rules — непорожній array записів з унікальними id, algorithm:string, types:string[] та order:string[]; назви алгоритму без типів/порядку не закривають контракт. Operation capability_status належить unverified/candidate/catalog_verified/specified/configured/exercised/unsupported; integrated потребує exercised для кожної claimed operation. Recipes мають взаємні operation bindings. Кожна active requirement покрита системою, journey, operation та recipe. Деталі current subject/attempt/evidence hash bindings і explicit scope exclusions — у [доказовому контракті](evidence-and-delivery.md).

Round project extension не замінює baseline: додатковий requirement містить source_ref/owner/domain_id/acceptance/negative_probe, а assignments і actual reviews покривають увесь прийнятий набір IDs. Scope та review незалежність залишаються чинними для довільної кількості предметних критеріїв.

`completion.assessments` — незалежні осі specification/code/integration/device/human, кожна із status=not_assessed|pending|passed|failed|not_applicable, scope та evidence_ids. passed не виводиться з іншої осі; actual human/device observation має окремий доказ. not_applicable потребує причини. `human_validated` може бути історичною міткою у project source, але не є допустимим completion.stage поточного round. Зберегти первинні людські докази; поточний human status визначити лише з їхнього фактичного змісту, актуального scope й редакції. Автоматичного перетворення старої мітки на passed немає.

## Входи фактичного review і producer provenance

До виконання нового фактичного run записати prepared/planned/running record із actual context і scope, потім `python3 scripts/teamctl.py bind-inputs ROUND.json --run RUN_ID`. Команда записує лише input_snapshot формату `chatbot.run-inputs/1`: scoped components із SHA/environment, hashes canonical/project requirement records, reviewed_outputs та reviewed_evidence. Вона не виконує роль, не створює verdict і не позначає результат завершеним. Якщо inputs невідомі, спершу підготувати відповідний scope; не вигадувати artifact чи actual run.

Для QA/guardian/qa_signoff/judge/orchestrator/supreme обов’язковий вхід виводиться з їхнього реального requirement scope, assignments і транзитивних dependencies: поточні компоненти, producer outputs, primary evidence та carry receipt для призначеного carry reviewer. Вказаний у payload порожній input_component_ids не вимикає цей мінімум. Окремі input_run_ids/input_component_ids можуть розширити входи, не прибрати required dependencies. Поточний ready checker звіряє immutable input_snapshot кожного такого споживача; зміна component/environment/criterion/author output/evidence не закривається простим refreeze. Незачеплений scoped run з тими самими явними inputs зберігає актуальність.

Producer input_snapshot — історичний provenance його реальних входів, які могли змінитися внаслідок легітимного запису самого producer. Він не порівнюється з post-write output як з незмінним input. Для нового результату без попереднього файла producer може явно вказати input_component_ids=[] і непорожню input_scope_reason; прийняті requirement records усе одно прив’язані. Не створювати порожній output-файл заради bind. Producer output_ref/output_sha256 залишаються frozen actual outputs; належне наступне QA звіряє поточний target і точний output producer.

`hashes` не переписує input_snapshot completed runs і відхиляє зміну вже frozen completed output bytes. `freeze` фіксує package, не робить старий QA поточним. `bind-inputs` не змінює вже збережений snapshot або завершений run. Для нового фактичного перегляду створити новий run, зберігши історичний; не підміняти rerun новим вигаданим ID чи зміною старого підпису. Actor/run records і хеші все одно є деклараціями: справжність виконання, повноважень і висновку перевіряється за реальними джерелами/інструментами, а не доводиться формою JSON.
