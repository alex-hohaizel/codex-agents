# Game Atelier · Концепти за єдиним входом

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

**Вхід:** current studio revision/hash, actual research run і intent lock. Scope «visual previews», «audit», «saved favorites» або «продовжити R4» не стає full-concept/production choice. Кількість кандидатів визначається скінченним brief/current intent і реальною різноманітністю, без mandatory count; `4×100` лише за explicit chosen search mode. Stop-search/chosen-concept потребує свого user source. TatterJack favorites не обирають гру. Ескізні previews лишаються C0; кожний кандидат, представлений як готова концепція для остаточного вибору, має повний C1. Кількість кадрів не зменшує цю повноту; T для прийнятої гри — наступний етап.

**Робота:** кожен начерк одразу поєднує дію, зростання можливостей і потенційну optional purchase value. Depth показуй тим, як зміна однієї системи змінює рішення в іншій, а не числом валют/кнопок. Компактні й великі різні жанри допустимі; для власного scope визнач цілісний mastery/run/build/meta/world/content-grammar досвід, late-game reason to replay/return і межу launch content. Не нав'язуй RPG структуру спортивній майстерності.

| Розрізнювальна перевірка | Доказ та межа |
|---|---|
| Live input + progression | Same situation: input now/later/absent; нова здобута можливість змінює стару задачу/trajectory/timing/route. Causal card/model/доступний PoC з raw output; desk description не є touch playtest. |
| Art + sensory identity | Comparable direction samples в рамках intent; fantasy/tempo/mechanics визначають camera/form/material/light/UI/type/motion/audio/haptic. Exact originals і known/unknown map; actual auditions/motion samples тільки коли виконано. |
| Economy from birth | desire→trial→earned route→optional purchase→repeated use→next meaningful goal. Для кожного offer exact contents, eligible moment, reason/trial, earned pace, cohort impact, recurrence, production cost, cumulative access/power і paid-dominance counterexample; no-offer та meaningful alternative. |
| Demand/feasibility | Current primary-source research і конкретний production route/native-slice test plan. Competitor success/синтетичні числа не стають нашими retention/profit. |

Порівнюй kits/content/art ensembles/pass/resources/acceleration за fit; не додавай весь commerce список. Direct power не є обов'язковою paid value, але artistic collection/alternative playstyle теж потребує конкретної повторної цінності. Paid randomness, extra spend і material implementation model лишаються окремими choices.

**Вихід/acceptance:** точно позначений C0 або повний C1 output у погодженому scope, comparison, originals/hashes, causal progression/economy models, art/audio/input feasibility і validation gaps. Кожен must має mechanism, strongest objection, evidence/limitation і наступний discriminating test. Жодний score не закриває провалений must.

**Повернення:** director показує рекомендацію, яка не є user choice. Preproduction отримує full accepted concept тільки за explicit chosen-concept gate; продовження пошуку/12-preview stop залишається в concepts із checkpoint. Unknown backview/rig/stems/physics мають owner/due-stage, не випадкові downstream здогадки.

## Наскрізне приймання 4.0 зі збереженими source IDs

Перед залежною роботою спожити canonical model, C0/C1/T та production/evidence refs разом із збереженими вимогами `UA26-SYS-01…07`. Для кожного ілюстрованого кандидата concept-specific causal/UX/resource/progression/alternate-experience/feasibility evidence due до генерації; actual image inspection due до показу. Для downstream зберегти ці IDs до spec/assets/code/test; зміна взаємодії відкриває тільки залежний regression. Це не другий source of truth і не автоматичний master acceptance. Після узгодження кандидатів продовжувати вже доручений scope без повторного запиту того самого дозволу.

## Робоча межа поточного маршруту

Застосувати [предметний контракт 4.0](v4-route.md): maturity визначає повноту задуму/специфікації, implementation stage — належний actual proof. Кожний task має accepted inputs/hashes, operation/host, owned paths, consumer, acceptance, ресурсний cap, allowed effects і reconcile/stop. На виході звірити coverage й semantic bindings, а не число документів. Для Game of 2027 нативні Android/iOS, пряме динамічне керування, практичне широке покриття й ціль 60 FPS вже збережені; їх не перетворювати на нові відкриті питання.
