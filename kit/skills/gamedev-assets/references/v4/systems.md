# Системи, каталоги, розвиток і передача 4.0

## Навігація

1. Межі та виходи C0/C1/T
2. Реєстр двадцяти систем
3. Залежності й зміна
4. Каталоги та розвиток
5. Лор і причинність
6. Приймання і джерела

Застосовувати до задуму, технічного дизайну, зміни реалізації й повернення з QA. Реєстр нижче використовує canonical track IDs `TR01..TR20`. Канонічна модель проєкту є єдиною authority для IDs, правил і чинних рішень; цей довідник визначає спосіб її наповнення. Не створювати другу незалежну модель у GDD, таблиці, симуляторі чи prompt.

Шість погоджених компетенцій P1 мають явні ресурси: `math.md` — поведінка/математика; `catalog-progression.md` — каталоги/розвиток; `world-ai.md` — світ/AI; `lore-narrative.md` — лор; `experience-commerce.md` §§1–3 — досвід; той самий файл §4 — метагра/комерція. `systems.md` координує реєстр і передачу; `persistence.md` й операційний production довідник є наскрізними ресурсами D1/D2. Кількість файлів не визначає кількість агентів або обов’язкових фіч гри.

## 1. Зафіксувати межі виходу

| Вихід | Що передати | Що може залишитися відкритим |
|---|---|---|
| C0: ескіз | Фантазія, головне рішення, відмінність, ризик, груба здійсненність | Неопрацьовані системи явно позначені; це не завершена концепція |
| C1: завершена концепція | Усі активні системи, сімейства, цикли, розвиток, світ, повний шлях гравця, стиль, керування, економіка, виробничий маршрут, сценарії | Числове налаштування з діапазоном, метою і способом вибору; жодного прихованого продуктового рішення |
| T: виробнича передача | Повний запусковий каталог/генератор, типізовані правила, exact базові числа, стани/переходи, ресурси, алгоритми, adapters, fixtures, бюджети й план | Лише явно параметризоване подальше tuning із початковим значенням і процедурою; поведінкове TBD блокує споживача |

Доводити кожного представленого як готовий кандидата до C1. Картинки, три екрани або презентація є видами цього пакета, не його заміною. T розробляти для концепцій, прийнятих у реалізацію. Ранні ризикові spikes дозволені з обмеженим питанням/метрикою/критерієм відхилення; дослідний код не успадковує production статус.

Сформувати scope ledger: включено зараз / пізніше / предметно N/A / невідомо. N/A пояснювати задумом, а не браком SDK чи часу. Невідома доступність потрібного пристрою означає неперевірений доказ. Зберегти пряме динамічне керування, native targets, FPS і прийняті матеріали там, де вони підтверджені чинним project profile; новий раунд не перетворює прийняті рішення на припущення. Новому проєкту не приписувати targets з [історичного прикладу](../historical-project-profiles.md).

## 2. Вести реєстр двадцяти систем

| ID | Система | Мінімальний предметний контракт |
|---|---|---|
| TR01 | Задум і досвід | Аудиторія, фантазія, основні рішення, стовпи, межі й критерії відхилення |
| TR02 | Лор і наратив | Канон, причинність, знання, персонажі, фракції, квести/діалоги за обсягом |
| TR03 | Стан сутностей | Життя, ресурси, ownership, стани, відновлення, смерть/відмова |
| TR04 | Дії й фізика | Намір, commitment, час, контакт, solver mapping, взаємодія |
| TR05 | Предмети й можливості | Сімейства, характеристики, слоти, сумісність, комплект, отримання |
| TR06 | AI та інші учасники | Сприйняття, знання, рішення, дії, координація, навігація |
| TR07 | Структура світу | Топологія, місця, маршрути, переходи, стійкі наслідки |
| TR08 | Складання ситуацій | Авторські опори/генерація, legality, новизна, ритм, repair/fallback |
| TR09 | Проходження | Сесія, етапи/кампанія, виклики, повернення, завершення |
| TR10 | Розвиток гравця | Майстерність, unlocks, спеціалізації, колекції, постійне/тимчасове |
| TR11 | Винагороди й економіка | Джерела/витрати, цінність, гарантоване/випадкове, ліміти, repair |
| TR12 | Монетизація | Товари, метасистеми, вплив, магазин, оплата, права й відновлення |
| TR13 | Керування й камера | Намір→жест→дія, хват, pointer ownership, режим/ракурс, cancel |
| TR14 | Повний UX | Запуск/навчання/сесія/помилка/вихід/повернення/налаштування/підтримка |
| TR15 | Зображення | Стиль по елементах/станах, читабельність, анімація, VFX, budgets |
| TR16 | Звук і haptics | Події/стани, SFX/музика/голос, sync, mix, пріоритети, альтернативи |
| TR17 | Технічна платформа | Runtime/data/save/offline, умовна мережа, продуктивність, безпека |
| TR18 | Виробництво контенту | Редаговані джерела, recipes, авторинг, імпорт/експорт, локалізація |
| TR19 | Перевірка й вимірювання | Oracles, контрприклади, simulation/engine/native/device/human evidence |
| TR20 | Випуск і розвиток | Версії, міграції, exact release, фактичні спостереження, підтримка |

В authoring view для кожного запису визначити застосовність і причину, власника й отримувача, призначення, джерельні вимоги, reads/writes, правила, контент, розвиток, feedback, persistence, budget, інваріанти й due acceptance. Застосувати `assets/v4-domain-templates/system-register.template.json` як каркас роботи, не як completed proof або перелік literal canonical fields.

При записі в `game-model.json` використовувати точні поля чинної схеми: `production.tracks[]` має `id/name/enabled/rationale/owner/receiver/requirement_ids/summary/reads/writes/contract_ids/invariants/scenario_ids/progression/content/feedback/persistence/budget/concept_refs/spec_refs`. `concept_refs/spec_refs` містять `path/sha256`. Українські пояснення й authoring worksheets не підміняють canonical field names.

Реальні правила записувати в `production.contracts[]` через `id/kind/version/track_id/owner/requirement_ids/purpose/status/inputs/outputs/read_refs/write_refs/depends_on/algorithm/invariants/cases/feedback/persistence/telemetry/body`. Status: `unresolved/defined/tuning`; typed input/output: `name/type/units/encoding/capture`, числові precision/rounding за T. Kind-specific `body` перевіряється `scripts/v4_contract.py`; templates є authoring worksheets з явним `materialization`, а не напряму валідними моделями. State fields належать `production.state_fields`, не довільному другому save registry.

### Перенести дванадцять authoring views у канонічну модель

У шаблонах `template_only=true/status=draft`, null і пусті масиви навмисно позначають незавершений ввід. Не передавати їх як defined contracts. Прийняті деталізовані документи/таблиці зберігати як companion artifacts з path/sha256 у `concept_refs/spec_refs` чи `algorithm_ref`; canonical contract зберігає їхні IDs, типізований інтерфейс, поведінку й `cases`. Не дублювати незалежно редагований параметр у companion й runtime.

| Worksheet | Canonical target і перетворення |
|---|---|
| system-register | `systems[].id/name`→`production.tracks[].id/name`; applicability→enabled, consumer→receiver, purpose→summary, rules→contract_ids; references→concept_refs/spec_refs; due acceptance→scenarios/cases/evidence obligations |
| behavior-rule | `production.contracts[] kind behavior/numeric/state_machine/rng`; type/unit/capture→inputs/outputs `type/units/capture`; concrete algorithm/function→algorithm/algorithm_ref; exact details→kind-specific body |
| damage-resolution | kind damage,TR03/04; pipeline_order→body.pipeline with canonical nine step names; dedup→repeat_gate; capture_inputs→capture; channels require numeric_contract_ref; outcome_priority→lifecycle_priority; simulation/durable remain distinct |
| physics-contact | kind physics,TR04; engine→engine_version; step→fixed_timestep/substeps/solver_config; collision matrix→collision_layers/queries; measurement/curve→contact_adapter; destruction→destruction_topology; motion/crash→crash_policy |
| lifecycle-failure | kind state_machine/behavior,TR03/09; states/transitions/initial→body.state semantics; profiles/priority/retry→algorithm/body; negative cases→cases with concrete scenario IDs |
| catalog-progression | kind family,TR05/10; dimensions/compatibility/progression/opportunities/dominance_counterexample/launch_catalog_ref→body; reward values→kind economy,TR11; instances→state_fields |
| world-generation | kind generator,TR07/08; generation inputs/constraints/repair/attempt/fallback/RNG→matching body fields; semantic_novelty→novelty_signature; progression→progression_envelope; exact authored transitions→state_machine |
| actor-boss | kind ai,TR06; families/knowledge/actions/decision/navigation→body actor_families/knowledge/actions/decision_model/navigation; boss→boss_policy and concrete state_machine; state/save→state_fields |
| persistence-continuity | state_fields→`production.state_fields` using classification/units/consistency_group/commit/restore/merge/migration/retention; kind persistence body contains consistency_groups/transaction/recovery/restore_pipeline/identity/cloud_policy; envelope remains pinned companion |
| input-camera | kind input,TR13; intent_action_map→intents/bindings; input_profiles→recognizer/pointer_ownership/cancel/simultaneity/accessibility; camera→camera_arbitration; first/peak/late→cases/peak_case |
| experience-commerce | kind journey/presentation/economy/commerce acrossTR11/12/14/15/16; atlas/attention→states/failure/recovery/acceptance; commerce earned/paid/portfolio/partial/grant/refund/reconcile→matching body; event matrices remain pinned companions |
| lore-narrative | kind behavior/state_machine,TR02; canon/knowledge/quest/scene conditions and changes→typed inputs/outputs/reads/writes, states/transitions/algorithm; exact authored text/graphs→pinned companion; restore choices→state_fields |

Виконати поточний schema/semantic checker після перенесення. Ця таблиця не замінює kind-specific required keys у `scripts/v4_contract.py`; вона запобігає плутанині between richer worksheets і strict model envelope.

Не вимагати зв’язку кожної пари систем. Для реального ребра записати source/output, target/input, тип/одиницю/timebase, допустимі стани, версію, втрату при перетворенні, помилку, owner і consumer check. Наприклад, пробиття колеса змінює grip, steering, доступні траси, camera cue, repair cost і save; логотип студії може бути незалежним.

## 3. Здійснювати зміни через причинний вплив

1. Прочитати exact поточні inputs/версії та рішення; відновити незакінчені задачі, не повторювати завершені jobs.
2. Визначити змінювані IDs і контракт: які reads/writes/поведінка/формати/асети змінюються.
3. Пройти прямі й транзитивні залежності; перевірити пропущені ребра предметним читанням.
4. Скласти bounded repair пакет із одним writer на файл/scene і точним consumer.
5. Зберегти незалежні outputs/evidence; залежні позначити stale до нового приймання.
6. Виконати потрібні contract/integration/native/human перевірки за твердженням.
7. Оновити model revision, рішення, migration, виконані факти й наступну дію.

Hash підтверджує відповідність байтів, не повноту змісту. Перевірений перенос доказу потребує незмінних семантичних inputs, версій адаптера/інструмента, середовища й scope. Стара review receipt не підтверджує нову фізику. Не скидати незалежну студійну ідентичність через зміну damage curve.

## 4. Будувати каталог через простір рішень

У C1 визначити повну таксономію запускових сімейств, механічні осі, лінії розвитку, джерела отримання, сумісність і контексти. Не замінювати систему трьома прикладами. У T дати повні дані або точну grammar/generator зі всіма constraints, ranges, weights, versions і перевіреним fallback.

Для кожного сімейства описати:

1. Роль і рішення, яке воно додає гравцю.
2. Delivery/дію/цикл/ресурс і вимоги, а не лише `+stat`.
3. Параметри з типами/одиницями/діапазонами, формулами або rule refs.
4. Slot/tag/dependency/exclusion правила, legal/illegal приклади комплектів.
5. Користь у контекстах, ціну, слабкість, синергії й контрстратегії.
6. Acquisition/unlock/craft/repair/consume/respec із економічними й save refs.
7. Візуальні/звукові/анімаційні відмінності та потрібні resource states.
8. Реальні нагоди використання після відкриття, до й після completion.

Розрізняти definition ID, instance ID й варіант; статичний опис не містить runtime ownership. Комбіновані показники для гравця виводити з точних параметрів і однакових тестових сценаріїв. «Прохідність» має названі conditions/weights; UI не приховує, що саме перевірено.

Перевіряти домінування по контекстах і paid portfolio, а не лише попарний середній DPS. Визначити мінімальне meaningful coverage сімейств/сценаріїв; не встановлювати універсальну квоту 50 предметів. Для великого простору застосувати boundary/constraint/property/combinatorial checks, зазначивши неперебрані поєднання.

### Прогресія та винагороди

Для кожної progression edge задати source capability, prerequisites, витрату/досягнення, exact delta, нове рішення, наступну ціль, opportunity, reset/loss/transfer, UI/навчання, save й перевірку. Окремо вести run power, permanent unlock, навичку людини, колекцію та проходження світу.

Перевірити граф на недосяжні prerequisites, непотрібні цикли, пастки вибору, softlocks, обов’язкові порожні повтори й нагороду після останньої нагоди. Відкрити→освоїти→перенести→комбінувати→переосмислити є функціональними зв’язками, не примусовою однаковою послідовністю всім жанрам (D1Q09–10).

Кожна reward rule визначає trigger, eligibility, amount/distribution, generation/claim ID, once/repeat scope, duplicates, cap/overflow, inventory destination, durable boundary, повторний callback, наступне використання. Відмова/retry/repair не створюють вигідний нескінченний цикл. На max level/повній колекції/фіналі визначити excess rewards, duplicate conversion, закриті offers і чесне завершення (Q14).

## 5. Оформити лор як ігрову причинність

Розділити world truth, character knowledge, belief/rumor і presentation. Canon record містить `fact_id`, truth conditions, time/region, actors knowing it, allowed changes, conflicts, dependent missions/assets/audio. Не зараховувати довгу енциклопедію без ігрового впливу як завершений narrative design.

Для scene/quest/dialogue задати prerequisites, knowledge guards, priority/tie-break, speaker/target, choices, commitment/irreversibility, effects, interruption/resume/repeat, localization IDs, save й fallback. Не допустити одночасно взаємовиключні фінали через save merge. Лор дефіциту має узгоджуватися з джерелами/витратами економіки, а смерть/відродження — з правилами failure.

Визначити функціональне пояснення переходів: навіщо гравець іде далі, що втрачає/зберігає, як змінилися знання/завдання, як може повернутися. Перед поверненням показувати зрозумілу бажану нагороду/умову/шанс за задумом; не створювати примусовий backtracking заради заповнення карти.

## 6. Прийняти пакет споживачем

Отримувач без історії чату має відтворити: першу дію; late/peak ситуацію; failure/recovery; нове відкриття й нагороду; pause/cold return; conditional purchase/sync. Він називає прочитані IDs/версії, отримані outcomes, пропуски й власний контрприклад. Авторський self-check не називати незалежним review.

Негативні перевірки: сімейство лише перефарбоване; unlock не має opportunity; reward без застосування; max collection ламає магазин; lore flag змінюється двома writers; приймач вигадує правило; зміна grip не скинула залежний route proof; доступний SDK помилково позначено integrated.

Для dev/test визначити лабораторію станів: exact fixture/seed/loadout/locale/input profile, legitimate state transition, reset і очікуваний outcome (D1Q16). Лабораторія відрізняється від bounded gameplay repro capsule (Q28) й runtime reason inspector (Q29); жодна не є ще одним джерелом правил. Режим debug/cheat не потрапляє до release без окремої product причини.

Пакет готовий лише за scoped критеріїв відповідного виходу. Structural pass не доводить fun, баланс, native performance чи revenue. Зберегти статуси досліджено/специфіковано/обчислено/симульовано/інтегровано/перевірено на пристрої/перевірено людиною окремо.

## Джерельна основа

Методика 4.0 є адаптацією затверджених P1/D1/D2, не універсальним стандартом GDD. Первинні матеріали перевірено під час дослідження 2026-11-02; version-specific факти повторно перевіряти при binding реального проєкту.

- MDA, зв’язок mechanics/dynamics/experience: https://www.cs.northwestern.edu/~hunicke/MDA.pdf
- Epic Data Driven Gameplay, таблиці й криві; не наказ використовувати Unreal: https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine
- W3C SCXML, події/стани/переходи; без обов’язкового XML runtime: https://www.w3.org/TR/scxml/
- W3C PROV-DM, entities/activities/agents/derivation; provenance не доводить якість: https://www.w3.org/TR/prov-dm/
- Dormans, місійна й просторова структури: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
