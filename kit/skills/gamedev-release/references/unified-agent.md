# Game Atelier · Випуск за єдиним входом

> Для нових результатів 4.0 застосувати [game-model workflow](game-model-workflow.md), [формат](model-format.md) і належні предметні модулі. Поточні due gates закриваються тільки належними доказами.

## Обов'язковий intake та reconciliation

1. Прийми task від єдиного `gamedev-director` або віднови його через director intake. Зафіксуй current intent: дослівний запит/source, project/revision, дозволений scope, потрібний результат, non-goals, budget/consent, stop boundary і next gate. Слова «продовжуй», saved favorite, recommendation, чернетка й user acceptance мають різні наслідки. Не піднімай статус наміру самостійно.
2. Прочитай actual checkpoint/project files, orchestrator state `.gameatelier/orchestrator/state.json`, requirement registry, knowledge/lessons, decision history і релевантні upstream bytes/hashes. Фактичні project decisions/requirements збережи й звір із джерелами, не overwrite; runtime ledger має поточний формат і toolkit marker. Safe import перевіряє archive paths/symlinks/resource limits і manifest; чужі scripts не виконуються автоматично. Наявну version/master/approval history зберігай, не переписуй під новий workflow. Resume звіряє також actual external job/provider/store state до retry.
3. Для кожної нової/зміненої вимоги збережи stable ID, verbatim source, intent, stage, dependencies, artifact/evidence refs, status, owner і closure criterion. Усі раніше чинні must переносити навіть коли новий запит їх не повторив. `not_applicable` потребує предметної причини й scope; missing modality не дає N/A. Один невиконаний must не закривається середнім score.
4. Project knowledge/lesson має source, scope, confidence, applicable stages і dependency impact. Перед залежною роботою звір його з вимогами, рішеннями та hashes; суперечність відкриває адресний issue. Нова lesson інвалідує лише залежні outputs/reviews, не змінює глобальні skills, дозвіл чи прийнятий target мовчки.
5. Невирішений material choice подай як ID + scope + 2–3 feasible options + наслідки/витрати/права + рекомендація з поясненням + affected IDs. Дочекайся відповіді до залежної роботи; повторно не запитуй чинну згоду. Поки відповідь pending, заверши все незалежне й дозволене, щоб потрібне погодження стосувалося конкретного reviewable результату.

[Experience contract](experience-contract.md) і [системний контракт](systemic-design.md) застосовуються разом із предметними references: artistic intent, implementation parity, device proof і user acceptance — окремі твердження. Кожна дія зв'язує input→правило→рух/контакт→animation/VFX→audio/music→haptic→наслідок→наступне рішення. Зберігай predictive/confirmatory/error/recovery cues, two-thumb/accessibility, mute/no-haptic parity. Не вводь універсальний stylized 3D preset, engine, backend чи commerce kit. Broad practical reach і 60 FPS стають перевірними budgets, коли їх обрав проєкт; не оголошуй їх універсальними доказаними властивостями кожної гри.

## Реальні можливості та межі дій

Перевір actual operation, credentials scope, середовище, rights, output format, cost і smoke result, а не назву plugin. Використай достатні доступні tools/CLI/skills; task-local агенту дай IDs, exact inputs/hashes, owned paths, cap і stop. Runtime тільки зберігає/перевіряє стан та gates: він не є LLM, connector або постійним сервером. Independent QA виконує інший actual actor пропорційно ризику; self-check позначай чесно.

Account/setup/upload/store/config actions можуть виконуватись доступним достатнім connector/API/CLI або дозволеним browser у чинному scope згоди. Історична фраза «власник робить setup» не є blanket ручним обмеженням. Де потрібні MFA, особисте legal/signature confirmation, фізичний hardware чи відсутні права, створи owner bridge: exact blocked operation і причина; уже готові inputs/хеші; поточне середовище/verified URL; launch/click/command steps; expected result; що повернути без secrets; return validation і наступна дія. Не проси власника заново зробити все, що можеш завершити дозволеними tools. Витрати/публічні/destructive effects потребують чинної конкретної згоди; якщо її нема, спочатку завершуй локальний пакет. Unknown outcome зовнішньої дії означає status reconciliation, не сліпий retry.

## Повернення та пауза

На межі task поверни director: input/output hashes, actual artifacts, вимога→spec/data→source/asset→runtime→QA/production evidence, choices/lessons, independent verdict, missing IDs/owner/closure і next route. Structural validation не засвідчує побачений/прослуханий/зіграний досвід чи дохід. Не створюй нову гру, paid service або deployment під час ремонту workflow.

`pause now` зупиняє запуск нових робіт; поточну операцію безпечно зупини/збережи її actual job ID і state. `after artifact` / `after stage` завершує лише названу межу. Checkpoint містить readable brief, completed/current jobs, pending choices/evidence, exact next action/environment і return instructions. Не переходь user-defined stop. Resume відновлює факти з files/external state й перевіряє locks; user не мусить сам обирати назву наступної skill. Recurring checks/monitoring — лише за дорученням через фактично доступний scheduler; інакше передай конкретний ручний check/runbook.

## Предметний task contract

**Вхід:** exact independently checked candidate, source/build/config/content/catalog/economy/save versions, studio/legal state, rights/privacy inventory, device verdicts, consent/rollout limits. Build-ready, QA accepted, upload authorization, store approval і actual live availability — окремі стани.

**Робота:** заново перевір поточні official store/SDK/payment/privacy/test requirements, actual capability і permissions. Виконай доступні підтримувані account/config/catalog/upload/submission/rollout actions, коли чинне доручення охоплює exact target/scope; назва connector не дає права. Наявний дозвіл не перепитуй, MFA/legal/payout confirmation не вигадуй. До потрібного останнього approval заверши локальні binaries/metadata/field mappings/rollback/smoke plan.

| Розрізнювальна перевірка | Доказ та межа |
|---|---|
| Exact candidate parity | Release binary/config hash збігається з прийнятим або має targeted new QA; store captures з actual runtime, exact studio master/fonts/rights. Marketing frame не підмінює gameplay screenshot. |
| Input/sensory/device | Release smoke з критичними input/contact/feedback, audio focus/mute/no-haptic/accessibility, long-session/min-device checks за project budgets. Signing/export/optimization не може мовчки погіршити controls/art/audio/FPS. |
| Commercial correctness | Native product mapping exact contents/price source/eligibility/trial/earned/recurrence/restore/refund; actual catalog does not change free path/cumulative access/power чи paid dominance від прийнятого design. Sandbox proofs та live billing readiness розділені. |
| Account/privacy/legal | Actual public developer/seller IDs, agreements/tax/payout state, SDK data behavior→disclosures; pending IDs не вигадуються. Current store policy snapshot не є blanket юридичним висновком. |
| Action truth/recovery | Provider receipt/time/target/channel/version/state, availability/smoke і halt/rollback/forward-hotfix rules. Unknown upload outcome спершу reconcile; mobile binary downgrade не обіцяй instant. |

Owner bridge точний: наприклад verified App Store/Play page + готові field values/files/hashes + MFA/особистий agreement step + expected receipt/status + безпечний return. Відсутній macOS/signing віддає точний build/export task і inputs, не «власник розгортає все». Не вводь новий paid backend, підписку, paid randomness чи price model під виглядом релізного налаштування.

**Вихід/acceptance:** prepared/submitted/in-review/approved/testable/live states лише з actual evidence. Manifest/store metadata/product/privacy snapshots, sanitized receipts, rollout/stop plan, symbols/migrations/runbooks та known gaps. Якщо final publish не дозволений, готовий reviewable пакет і exact scope permission request є чесним завершеним локальним результатом.

**Повернення:** director→liveops після фактичної release/beta handoff; rejection/signing/binary/commerce/art issues адресуються відповідному owner і targeted QA. Моніторинг запускається лише за окремим дорученням та реальною scheduler capability. Не видавай workflow/toolkit за випущену гру.

## Наскрізне приймання 4.0 зі збереженими source IDs

Перед залежною роботою спожити canonical model, C0/C1/T та production/evidence refs разом із збереженими вимогами `UA26-SYS-01…07`. Для кожного ілюстрованого кандидата concept-specific causal/UX/resource/progression/alternate-experience/feasibility evidence due до генерації; actual image inspection due до показу. Для downstream зберегти ці IDs до spec/assets/code/test; зміна взаємодії відкриває тільки залежний regression. Це не другий source of truth і не автоматичний master acceptance. Після узгодження кандидатів продовжувати вже доручений scope без повторного запиту того самого дозволу.

## Робоча межа поточного маршруту

Застосувати [предметний контракт 4.0](v4-route.md): maturity визначає повноту задуму/специфікації, implementation stage — належний actual proof. Кожний task має accepted inputs/hashes, operation/host, owned paths, consumer, acceptance, ресурсний cap, allowed effects і reconcile/stop. На виході звірити coverage й semantic bindings, а не число документів. Для Game of 2027 нативні Android/iOS, пряме динамічне керування, практичне широке покриття й ціль 60 FPS вже збережені; їх не перетворювати на нові відкриті питання.
