# Game Atelier · Супровід за єдиним входом

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

**Вхід:** actual release/provider state і specific incident/diagnosis/content/experiment/cost/patch intent. Порівняй store build/source/config/content/catalog/economy/save/flag cohort із handoff; старий ZIP не є current production. Read-only audit не дає дозволу змінити підписки/ціни/production.

**Робота:** causal findings спираються на actual query/export/time window/timezone/denominator/cohort/sample/build/config/bias/uncertainty. Sandbox/bots/internal testers не стають paid cohorts. Lesson записуй із source/scope/confidence/stage applicability/impact; project learning не переписує глобальний skill або approved art/economy.

| Розрізнювальна перевірка | Доказ та межа |
|---|---|
| Core/functional growth | Новий verb/kit/content змінює старі задачі, grammar/skill/build decisions і next goal, а не лише reskin. Cohort progression/return + actual qualitative observations; predicted retention не є observed D1/D7/profit. |
| Sensory/identity regression | Exact masters/source lineage і targeted normal/peak motion/audio/input capture для changed dependencies. Новий сезон проходить whole-frame/cue/mix/physical haptic proofs за relevant scope, а не отримує exemption. |
| Accessibility/input parity | Нові cues/screen states не ламають two-thumb, mute/no-haptic/reduced-motion/no-support; regressions на supported devices прив'язані до build. |
| Commercial continuity | Кожен offer: desire/trial/earned/optional paid/repeated use/next goal; exact contents/moment/cohort/recurrence/cost і cumulative access/power. Перевір no-offer/alternative, paid dominance, complaints/refunds/churn поруч із revenue. Entitlements/earned progress не губляться. |
| Native/reach/cost | Порівнювані sustained profiles на affected device tiers, project FPS/reach budgets, actual production capacity/cost caps. Online/backend/config change не вважається безкоштовним або автоматично дозволеним. |
| Experiment/integrity | Versioned treatment/exposure/assignment/guardrails/stop plan; save/content/old-client compatibility і sandbox money proofs. Малий/biased sample не створює causality; replayed callbacks не дають double grant. |

Не оптимізуй дохід через зіпсований free baseline або hidden odds/difficulty. Новий paid model/randomness/price/production spend/identity change — material choice у його scope. Спершу reviewable offline/staging patch і independent proportional QA; дозволені mitigations виконувати за фактичними tools і scope, до недоступного кроку дати точний bridge.

**Вихід/acceptance:** один скінченний раунд із findings vs hypotheses, exact raw queries/evidence/versions, lessons/decisions, actual action receipts, before/after tests/metrics, migrations/rollback, customer impact і remaining owners. Missing data дає diagnosis plan+gap, а не «оптимізовано».

**Повернення:** director маршрутизує лише needed fragment: rule→preproduction, art/audio→assets, binary→build→QA→release, content→targeted asset/data/economy/compatibility QA→allowed rollout. Stop/pause зберігає jobs/flags/actions state. Recurring monitoring тільки через доручений actual scheduler з frequency/source/cost cap/notification/stop; за відсутності capability — concrete manual bridge без обіцянки фону.

## Наскрізне приймання 4.0 зі збереженими source IDs

Перед залежною роботою спожити canonical model, C0/C1/T та production/evidence refs разом із збереженими вимогами `UA26-SYS-01…07`. Для кожного ілюстрованого кандидата concept-specific causal/UX/resource/progression/alternate-experience/feasibility evidence due до генерації; actual image inspection due до показу. Для downstream зберегти ці IDs до spec/assets/code/test; зміна взаємодії відкриває тільки залежний regression. Це не другий source of truth і не автоматичний master acceptance. Після узгодження кандидатів продовжувати вже доручений scope без повторного запиту того самого дозволу.

## Робоча межа поточного маршруту

Застосувати [предметний контракт 4.0](v4-route.md): maturity визначає повноту задуму/специфікації, implementation stage — належний actual proof. Кожний task має accepted inputs/hashes, operation/host, owned paths, consumer, acceptance, ресурсний cap, allowed effects і reconcile/stop. На виході звірити coverage й semantic bindings, а не число документів. Для Game of 2027 нативні Android/iOS, пряме динамічне керування, практичне широке покриття й ціль 60 FPS вже збережені; їх не перетворювати на нові відкриті питання.
