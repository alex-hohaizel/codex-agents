# Передача між етапами, schema 1.0.0

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

## Канонічний проєкт і переносний пакет

Source of truth — один Git repo продукту: `.gameatelier/{state,decisions,requirements,toolchain,capabilities,sync-lock}.json`, `docs/`, `game/`, `assets/`, `tests/`, `artifacts/`. Великі binaries — LFS/object storage за реальною можливістю, із pinned hashes та download/import recipe. Work chat memory не є source of truth. Product repository не дублювати до Library; у Work передавати чіткий архів потрібної snapshot. Секрети, signing keys, production tokens, користувацькі дані в пакети не включати.

Handoff — незалежний portable каталог з `START_HERE.md`, `manifest.json`, `records/{requirements,decisions,reviews,claims}.json`, потрібними `studio/`, `specs/`, `data/`, `assets/`, `source/`, `builds/`, `evidence/`, `reports/`. Додати лише фактичні файли; upstream history не дублювати рекурсивно. Незмінні потрібні studio masters, ліцензії, ідентифікатори, product IDs, font files і контракти переносити до кожного залежного пакета. `studio_identity` посилається на фактичний identity JSON; публічні legal/account поля можуть бути pending у design, але release gate їх перевіряє.

Manifest містить `schema_version`, `suite_version`, `toolkit_version`,  `package_id`, `project_id`, `stage`, `revision`, `stage_status`, `upstream` (package ID/hash/schema), `artifacts`. Кожен artifact: `id`, `path`, `kind`, `status` (draft/final/reference), `author_ids`, `depends_on`, `sha256`. `seal` інвентаризує файли, зберігає metadata наявних paths і оновлює hashes; новим artifacts дає draft/unknown, які автор мусить класифікувати. Manifest не хешує сам себе. Records та START_HERE теж входять у hashes. Ніколи не редагувати sealed source без нового revision і повторного review.

`requirements.json` — object з `items`: `id`, `source`, `priority`, `owner`, `status` (pending/met/blocked/not_applicable), `acceptance`, `artifact_ids`, `evidence_ids`, `rationale`. Професійне обґрунтування not_applicable обов'язкове; не переносити всі build requirements у research як уже met.

`decisions.json` — `items`: `id`, `question`, `material`, `status` (pending/confirmed/superseded), `answer`, `authority_ref`, `scope`. Критичні pending зупиняють accepted наступного залежного scope. `authority_ref` — точне джерело користувацької відповіді або чинної політики, не вигаданий запис «approved».

Мінімальні матеріальні decision IDs: `DEC-BRAND` на всіх стадіях; `DEC-PLATFORMS` і `DEC-CONCEPT` від accepted concepts; `DEC-ENGINE` та `DEC-MONETIZATION` від accepted preproduction. `init` створює їх pending. Пошук концептів може йти до фінального вибору platform/concept, але accepted handoff для залежної реалізації потребує відповіді. Окремі матеріальні розвилки проєкту додаються понад цей мінімум.

`reviews.json` — `items`: `id`, `reviewer_id`, `artifact_ids`, `status` (pass/fail/pending), `evidence_ids`, `notes`. Review прив'язаний до hashes через `artifact_hashes` object; `dependency_hashes` містить hashes усіх транзитивних depends_on IDs, `evidence_hashes` — усіх evidence_ids. Зміна залежності чи доказу робить старий pass нечинним навіть за незмінних bytes дочірнього файла. Незалежний reviewer не входить у author_ids своїх artifacts. `claims.json` — `items`: `id`, `claim`, `status` (hypothesis/observed/blocked), `evidence_ids`, `evidence_hashes`, `method`, `limitations`. Observed claim теж має pin hashes доказів. Structural validator перевіряє references та hashes, а не правдивість написаного людиною/агентом.

## Види доказів для stage acceptance

У draft можлива часткова робота. Для full-stage accepted потрібні наведені artifact kinds із final/reference status, met/not_applicable локальні requirements, закриті матеріальні рішення й незалежний pass review фінальних artifacts:

| Stage | Мінімальні kinds, крім records і START_HERE |
|---|---|
| studio | studio_identity, brand_master, brand_rules, setup_runbook, rights_ledger |
| concepts | studio_identity, concept_comparison, selected_concept, progression_model, economy_model, visual_baseline, validation_plan |
| preproduction | studio_identity, gdd, tdd, interaction_atlas, progression_model, economy_model, fidelity_spec, asset_plan, audio_design, test_plan |
| assets | studio_identity, editable_sources, runtime_exports, asset_registry, rights_ledger, visual_comparison, audio_audition, import_receipt |
| build | studio_identity, source_snapshot, toolchain_lock, build_receipt, native_artifact, implementation_coverage, save_migration |
| qa | studio_identity, test_report, device_matrix, fidelity_report, economy_report, defects, release_recommendation |
| release | studio_identity, release_manifest, store_metadata, privacy_inventory, purchase_validation, rollback_plan, operator_runbook |
| liveops | studio_identity, telemetry_plan, support_runbook, content_cadence, experiment_plan, incident_runbook |

Kinds — машинний мінімум, не повний DoD. Android/iOS output вимоги перевіряти за decisions/toolchain/build receipts у предметному review. `native_artifact` може бути simulator artifact лише для simulator scope; це не дає device/store-ready статусу. Browser mockup не замінює native. Audio audition не є закриттям всього production audio. Product acceptance потребує деталізованих перевірок етапу, а не лише наявності цих назв файлів.

## Команди

Замість `<SKILL_DIR>` підставити фактичний каталог активної навички. У Codex попросити агента визначити його зі списку доступних skills; не копіювати шлях іншого Mac.

```bash
python3 <SKILL_DIR>/scripts/pipeline.py init ./handoff --stage concepts --project-id my-game
python3 <SKILL_DIR>/scripts/pipeline.py seal ./handoff
python3 <SKILL_DIR>/scripts/pipeline.py verify ./handoff
python3 <SKILL_DIR>/scripts/pipeline.py verify ./handoff --require-accepted
python3 <SKILL_DIR>/scripts/pipeline.py impact ./handoff --changed ART-0001
python3 <SKILL_DIR>/scripts/pipeline.py pack ./handoff --output ./handoff.zip
```

`init` створює draft, не готову гру. `verify` приймає каталог або ZIP; помилка checksum, небезпечний path, broken references, self-review, stale review — nonzero. `--require-accepted` додатково перевіряє stage мінімум і blockers. `pack` спершу verify, архівує sealed snapshot; дозволяє draft, тому статус завжди читати до запуску наступного етапу. Не виконувати невідомі скрипти з вхідного ZIP автоматично.

## Intake і повернення

1. Перевірити чинні schema/protocol, точний toolkit marker, project ID, bytes та stage_status. Непоточний формат результату відхилити без змін файла. Для продовження відновити фактичні вимоги, рішення й матеріали продукту та створити поточний пакет; старі результати не отримують автоматичного acceptance.
2. Показати що реально прийнято, які choices чи ресурси лишилися pending. Для R06 recommendation diagnostic ≠ selected production concept.
3. Побудувати план лише наступного scope й зв'язати requirement→spec/data→asset/source→runtime→evidence→release.
4. За upstream defect дати issue ID, current hashes, repro, affected dependency IDs, пропонований owner. Ремонтувати джерело, підняти revision, інвалідувати транзитивно залежні докази. Не маскувати новий дизайн нижче pipeline.
5. Передати архів, людський `START_HERE.md`, точну команду/навичку/середовище наступного кроку, відомі blockers і формат локальної перевірки. Відносні посилання мусять існувати всередині snapshot.

## Поточний контекст проєкту

Чинний handoff protocol має `schema_version` і `suite_version` **1.0.0**, а поточний `toolkit_version` — **6.0.0**. До пакетів додавати `records/intent-lock.json`, `records/experience-coverage.json`, проєктні lessons/knowledge та readable checkpoint як звичайні artifacts з kind/status/depends_on і sha256. Використовувати фактичні requirement/decision/review IDs; контекст не є другим джерелом згоди. Приклади в assets — шаблони, не готові докази.

Живий облік director лежить у `.gameatelier/orchestrator/state.json`; наявні `.gameatelier/state.json`, requirements/decisions та game saves не перезаписувати. Sidecar pin-ить canonical authority файли і hashes. Для передачі включати потрібний checkpoint/контекст, inputs/masters, open decisions, stop boundary, знання та залежності; не всі внутрішні журнали. Невідомий outcome зовнішньої дії лишається unknown з ID/status-query до встановлення результату.

Якщо runtime має stage records, перед accepted stage-check звірити поточні due requirements/decisions/knowledge з package records і незалежними reviews. `context --stage STAGE` повертає `stage_context_snapshot`; зберегти його в optional `manifest.project_context` та reseal/review зачеплене. Hash сам по собі не усуває semantic gap. Це поле поточного handoff, яке перевіряє orchestrator; pipeline.py лишається structural validator.

`START_HERE.md` описує результат простими словами й одну наступну дію. Якщо середовище дозволяє — агент сам викликає потрібну навичку/tool. Для ручної передачі: де відкрити проект, точні файли/версії, що запустити, очікувані output/receipt, що повернути, як перевірити. Назва навички без input/output і повернення недостатня. Pause/search-only пакет може бути draft і повноцінним проміжним результатом; це не accepted production handoff.

Передавати чинні systemic passports, visual production profiles, structural check receipts, незалежні semantic reviews та actual image inspections як звичайні artifacts/evidence з pinned hashes і чинними requirement IDs. Preview-ready не підміняє accepted concepts із chosen-concept decision; не вигадувати production choice для завершення карток. Поточна runtime state schema — **2.0.0**; її marker також має бути **6.0.0**.

## Чинні scoped профілі4.0

Для обмеженого QA/liveops пакета таблиця нижче замінює full-stage мінімум kinds і materialdecisionIDs. Вона не змінює чинні projectrequirements/decisions у scope й не дозволяє приховати незакритий must. Для всіх scope лишаються actual artifacts/hashes/independentreview і відповідний game-model gate.

| Stage / acceptance_scope | Model gate | Required kinds | MinimumproductiondecisionIDs |
|---|---|---|---|
| concepts / candidate_completion | concept (повний C1) | studio_identity, concept_candidate, progression_model, economy_model, visual_baseline, validation_plan | немає: кандидат ще не обраний для production |
| qa / design_review | concept | test_report, defects | немає: огляд не обирає гру |
| qa / contract_review | preproduction | test_report, defects, validation_plan | немає |
| qa / slice_review | slice | test_report, device_matrix, fidelity_report, defects | немає |
| qa / beta_review | beta | test_report, device_matrix, fidelity_report, economy_report, defects | немає |
| qa / release_readiness | release | fullQAstage kinds | повні чинні productionchoices |
| liveops / incident_analysis | concept | incident_report, support_runbook | немає |
| liveops / design_change | preproduction | change_plan, validation_plan | немає |
| liveops / runtime_change | slice | change_plan, test_report | немає |
| liveops / player_experiment | beta | experiment_plan, test_report | немає |
| liveops / release_change | release | release_manifest, rollback_plan, operator_runbook | повні чинні productionchoices |

`manifest.game_model` містить `path`, `sha256`, `acceptance_scope`, `scope_ref`, `scope_description`. `scope_ref` має існувати у поточних package requirements/decisions; опис називає конкретний boundedreview/repair. Без scope діє fullstage; release не приймає lower-scopelabel. Доступні labels визначає `pipeline.py model_gate/acceptance_profile`. Scoped slice_review не є fullbeta абоreleaseacceptance.

Кожна linked model, включно з draft, має чинну schema **4.0.0**. Nonstudio accepted package додатково потребує due C1/T/evidence. `current_toolkit_ready` показує accepted поточний toolkit gate; `quality_certified` залишається false. `pipeline init` використовує toolkit **6.0.0**. Інші markers або попередні формати результатів не приймаються.


## Поточні проєктні вимоги та scope

Accepted manifest може містити `scope` — exact project/task scope; без нього scope=`project`. Це окрема вісь від `game_model.acceptance_scope`, який визначає зрілість приймання. Отримати binding через `atelier.py context PROJECT --stage STAGE --scope SCOPE`. Project-scoped вимоги застосовні до кожного scope, а чужі bounded scopes не блокують незалежну роботу.

`stage-check` для accepted claim (також без прапорця --require-accepted) перевіряє current applicable must за primary stage або типізованим масивом stages, status/closure/evidence та package inclusion. Кожний due must має бути в records/requirements із тим самим ID, status, owner й acceptance; current material decisions — у records/decisions із тим самим answer/authority. Manifest.project_context pin-ить їхні актуальні definition tokens. Просто скопіювати hash без оновлення змісту/review не є reconciliation. Pipeline transport checks без canonical project state самі не підтверджують актуальність project authority.


## Admission6.0

Tasks pin consumed_sources окремо від shared runtime identity. Зміна такого source робить affected task stale; old missing pins потребують reviewed/new task. Runtime2/model4/handoff1 schema IDs лишаються; тільки current toolkit marker6.0.0 і supported workflow adoption змінюють operating version.
