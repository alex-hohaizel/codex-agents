# Game Atelier — наскрізний контракт досвіду

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

Читати разом із `core-contract.md`, `requirements.md` і `handoff-contract.md` перед залежною роботою разом із [systemic-design.md](systemic-design.md). Застосовувати до нових задумів, імпорту й адресних змін; не запускати всі етапи для кожного виправлення. Контракт описує якість рішення та доказ її перевірки, а не обіцяє успіх гри. `experience-coverage.template.json` задає карту покриття, `intent-lock.template.json` — джерела, межі згоди та захист прийнятого задуму. Це шаблони записів, не новий дозвіл чи автоматичне приймання.

Зміст: джерела → пріоритети й покриття → цілісний досвід → художній задум → виробничий шлюз → commerce → докази → закриття етапів → негативні приклади.

## Джерела поточного доручення

Наведені `source_user_requirement_ids` прив'язати до оригінального повідомлення користувача в project registry. Наведені цитати — точні витяги з авторизованого `BRIEF_UA.md` від 01.11.2026, не вигадана дослівна транскрипція повного повідомлення. Імпорт не переіменовує старі requirement IDs: зберегти їх і додати ці source IDs як походження/уточнення.

| Source ID | Витяг з brief | Застосування / наявні ID |
|---|---|---|
| UA26-EXP-01 | «Кожний начерк одразу поєднує дію, розвиток можливостей і потенційну цінність покупки.» | Повний seed від першого начерку; IDEA-02, PROG-01, ECON-02 |
| UA26-EXP-02 | «Справжня глибина - зміна рішення однієї системи іншою; число кнопок/правил/валют не доказ.» | Керування, взаємодії, mastery/run/build/meta/world/replay за scope; REP-01/02, PROG-01/02 |
| UA26-EXP-03 | «Дія→правило→рух/контакт→animation/VFX→audio/music→haptic→наслідок→наступне рішення» | Multimodal loop, predictive/confirmatory/error/recovery, accessibility; UX-02/03, PHYS-01, ANIM-01, AUDIO-01/02, HAPT-01 |
| UA26-EXP-04 | «Унікальний цілісний художній задум з душею від першого концепта: різні напрями без універсального однакового stylized3D пресету.» | Усі художні шари, різні candidate directions; FID-01/02, ART-01, AUDIO-03 |
| UA26-EXP-05 | «Прийняті originals bytes/hash/provenance immutable; scope згоди точний.» | Exact originals, права, acceptance scope, невідомі backview/rig/stems/physics; FID-01, LIC-01, BRAND-01 |
| UA26-EXP-06 | «Productionpath feasibility і native representative slice до massproduction» | Перевірений production route та slice gate; FID-02, TOOL-01, NATIVE-01, PERF-01 |
| UA26-EXP-07 | «бажання→проба→earned route→optionalpurchase→багаторазове використання→наступна змістовна ціль.» | Добровільна інтегрована commerce journey; ECON-01…05, MONEY-01 |
| UA26-EXP-08 | «cumulative access/power моделюється чесно, no-offer і змістовна альтернатива.» | Cohorts, сумарний ефект, обмеження доказів; ECON-03, QA-02, OPS-02 |
| UA26-EXP-09 | «Кожну нову вимогу прив’язувати до verbatimsource/intent/ID/stage/dependencies/artifact/evidence/status/owner/closure.» | Повне покриття, hard must без усереднення, stage-scoped closure; QA-01, AI-01 |
| UA26-EXP-10 | «Жодного переходу за user-definedstop.» | Pause/stop, search mode, saved favorites ≠ production choice; CHOICE-01, FLOW-01 |

Для research, launch context і заборони вигаданих результатів також зберегти точне джерело: «Не видавати чужий успіх або синтетичну арифметику за наші retention/profit.» — UA26-EXP-08. Не застосовувати параметри одного проєкту як defaults для інших ігор.

## Пріоритети, застосовність і доказове покриття

Перед dependent step узгодити current intent, чинні decisions, requirement registry, project lessons, package revisions та hashes. Джерело повноваження і пріоритет виконання — різні поля. Дотримуватися системних обмежень і чинних меж користувацького дозволу; конкретне чинне рішення користувача має перевагу над загальною рекомендацією навички. За конфлікту однаково чинних material requirements показати конфлікт і варіанти до залежної реалізації. Не вирішувати його мовчазним downgrade.

| Priority | Правило закриття |
|---|---|
| `must` + `blocking=true` | Hard must у визначеному scope. Кожен має власний acceptance check; один fail/blocked забороняє саме залежний gate. Сильний art не компенсує broken save, а високий revenue model — примусову покупку. |
| `must` + `blocking=false` | Обов'язкова робота, строк якої ще не настав у поточному scope. Явно задати due stage/gate; не списувати як met або N/A. Перед due gate вона стає blocking. |
| `should` | Предметний quality goal. Невиконання має записаний tradeoff, вплив, owner і review; не називати повним покриттям must. |
| `explore` | Перевірна гіпотеза/варіант. Не є автоматично затвердженим scope чи підставою витрачати гроші. |

Не вигадувати weighted quality score, універсальний pass percentage або середнє, яке ховає must. Порівнювати варіанти за причинними tradeoffs, доказами, незакритими ризиками й відповідністю brief. Числа вимірювати там, де вони мають одиниці та метод: frame time, memory, earn pace, input latency, cost, розподіл unlock time. Ціль і допустимі delta погоджувати для конкретного проєкту, а не виводити з довільної оцінки «8/10».

Кожний requirement містить ID, `source_user_requirement_ids`, точне source reference/quote та intent, priority/blocking, owner, scope і залежності; stage obligations; artifact/evidence IDs і pinned hashes; acceptance method; status; closure reviewer/decision/date. Розкласти складену вимогу на дочірні checks: parent закритий лише коли всі застосовні due children закриті. Не викидати незгадані baseline must при стислому intake.

Застосовність визначати предметно: platform, device class, audience, mode, modality, feature, release channel і stage. N/A вимагає причини, exact excluded scope, authority/decision та reconsider trigger. Наприклад, online account recovery N/A для підтвердженого offline local-only scope; згодом cloud-save choice відкриває його знову. Немає доступу до телефона, tools або бюджету — це blocked/pending, не N/A. Майбутній device proof у concepts — `pending`, `due_at=representative_slice`, `blocking_here=false`; concepts intent proof може бути met окремо.

Проєктна lesson має source, scope, confidence, applicability та impact. Нова lesson чи зміна master/economy/rules/toolchain інвалідує лише транзитивно залежні outputs/reviews. Не переносити lesson у глобальні skills чи права без відповідного доручення. Структурна перевірка JSON/посилань доводить структуру; зміст, художній результат і фактичне відчуття перевіряти належною модальністю.

## Seed і граф цілого досвіду

Кожний seed, навіть короткий, має конкретну дію/контакт і наступне рішення; розвиток можливостей гравця та світу; причину повтору/повернення; добровільну потенційну цінність покупки; власну художню обіцянку. Не відкладати art або commerce до вибору «механічного прототипу». У дешевому текстовому seed достатні причинний опис та напрям; до ілюстрованого відбору кожний кандидат уже має системний паспорт, concrete UX/resources/alternate experience та здійсненний production profile. Це не вимагає готового asset set чи доведеної conversion.

Будувати `experience_graph`: input/action → rule/state/contact → multimodal response → cost/reward/world change → new choice → save/recovery/return. Для вузла/ребра задати роль, prerequisites, state change, timing, player-readable signals, failure/recovery, progression/commerce links, content dependencies, owner і due proof. Додати також menu/discovery/result/offer/decline/settings/interruption transitions. Зробити явними зміни, які одна система вносить у рішення іншої: поверхня змінює траєкторію; новий рух відкриває старий маршрут; союзник змінює timing; інструмент змінює спосіб розв'язання старої задачі. Це приклади причинного зв'язку, не жанровий шаблон.

Показати обрані провідні джерела mastery, run/session arc, build/playstyle, meta/world development і content grammar у межах жанру. Розвиток гравця і світу мусить змінювати доступні дії, контексти, цілі чи наслідки, а не тільки числовий multiplier. Не вимагати RPG inventory, crafting, фізичної симуляції або roguelite resets у кожній грі. Для спорту, гонки, ритму чи компактної arcade можливості та світ можуть розвиватися через техніки, арени/правила, суперників, маршрути й нові зв'язки між ними. Обґрунтувати scoped N/A окремого механізму без вилучення вимоги змістовного розвитку.

Мапа progression містить unlock/dependency graph, early/mid/late goals, sources/sinks, persisted/reset scope, tradeoffs, recovery/catchup і безплатний шлях. Показати, як нова можливість переосмислює вже відому задачу. Replay має варіанти рішень, скінченну launch capacity, довгу причину повернення та production route для поповнення. Для procedural content зберегти grammar, authored units, constraints, solvability/fairness fixtures, algorithm/content version і seeds; інші seeds без іншого рішення — слабкий replay. Прогноз повернення після багатьох сесій — гіпотеза до реальних спостережень.

Для ключових loops специфікувати predictive, confirmatory, error і recovery feedback у відповідних visual/motion/audio/haptic каналах. Записати що бачать/чують/відчувають до дії, при контакті та після наслідку, включно з UI response і музичними переходами. Перевіряти два великі пальці, handedness за scope, occlusion, safe areas, color/contrast/type, reduced motion, input alternatives, mute/no-haptic та interrupted audio. Вимкнення одного каналу зберігає інформацію, timing readability і можливість грати; не вимагати однакового фізичного відчуття без вібрації.

## Художній задум від першого кадру до всіх шарів

Спершу визначити фантазію, емоційний характер, механіку й темп, далі — художні рішення, що роблять саме цю гру впізнаваною. У candidate portfolio порівнювати різні аргументовані напрями: camera/proportion/shape/material/light/motion/type/audio можуть змінюватися разом із фантазією та керуванням. Зміна палітри в однаковому preset не є іншим напрямом. 2D, ілюстративні шари, 2.5D, 3D, інші матеріальні підходи допустимі за fit; жоден не універсальний default. Впливи описувати як принципи та відмінність власного виразу, не копіювання чужого asset/IP.

Дати `art_promise`: що гравець переживає, які мотиви/контрасти/характер підтримують це, які видимі й чутні рішення відрізняють гру, що зруйнує її характер. «Красивий stylized world» не є обіцянкою. Цілісність означає спорідненість усіх шарів, не однакову орнаментику чи максимальну деталізацію. Перевірити особливий характер спокійного menu, помилки, контакту, пізнього світу й storefront так само, як hero frame.

Вести повний layer inventory; на ранній стадії для кожного шару достатні intent/unknown/owner/due proof. Не вимагати всіх production bytes у концепті. Не лишати «решта generic»:

| Група | Що явно покрити |
|---|---|
| Керування й огляд | input gestures/controls, response, camera/projection/framing, tracking/occlusion, world scale й readability |
| Світ і дійові елементи | environments/architecture/terrain, interactables/props/tools/resources, characters/creatures/opponents, proportions/silhouettes, materials/palette/light/weather за scope |
| Поверхні інтерфейсу | HUD, typography/glyphs/icons, menus/navigation, onboarding, progression/results/inventory/shop, settings/accessibility, loading/pause/errors/empty/locked states, localization/safe areas |
| Рух і контакт | locomotion/poses, rig/constraints/IK за scope, clips/blends/events, collisions/contact/physics laws, camera motion, UI motion, VFX/particles/trails, state telegraphs |
| Звук і відчуття | music/motifs/arrangement/transitions, ambience, action/contact/character/UI SFX, mix/ducking/interruptions, haptic event language, channel-off information parity |
| Розвиток і цінність | unlock/reward presentation, currency/item/offer vocabulary, content/ensemble coherence, desire/trial/decline/ownership/use feedback |
| Зовнішня презентація | studio identity links, icon/key art, screenshots/trailer/store metadata presentation та відповідність реальній грі |

Зв'язувати кожний layer/element ID із requirement, source/master, authoring object, export/import recipe, scene/runtime node/event, state/camera/seed/time, evidence і closure. Один reusable token може покрити багато елементів, але явна coverage map мусить показувати, які саме. Інвентар розширюється фактичним scope, не довільною квотою objects/screens.

## Intent lock, невідомі й шлюз виробництва

Розділяти чотири незалежні твердження: `artistic_intent` (який досвід/образ прийнятий), `implementation_parity` (як runtime відповідає), `device_proof` (де фактично перевірено), `user_acceptance` (хто й що саме погодив). Одне не закриває інше. Favorite/saved preview, selected direction, approved frame, approved motion, approved build і дозвіл публікації мають різні scopes. Погоджений studio master не є погодженням будь-якого game art.

Для кожного прийнятого original зберегти фактичні bytes, sha256, media properties, source/generation provenance, права/ліцензію, authority reference, дату й точний scope. Незмінний master використовувати byte-identically; derived exports мають recipe/source hash і власний hash. Не перезаписувати master після перерендеру, crop, redraw чи compression. Додати revision та side-by-side delta, якщо зміна потрібна. Новий preview не є реконструкцією accepted source.

Із frame не відомі hidden geometry/back views, topology/rig/weights, collision laws, movement curves, lettering/font binaries, stems/mix або haptic feel. Позначити кожну невідомість, її вплив, owner, потрібний evidence/decision та due gate. Не вгадувати її мовчки в build. Частину можна авторськи розробити в чинному scope; material зміна прийнятого силуету/характеру/поведінки/якості потребує reviewable sample і рішення користувача до залежного тиражування.

Перед mass production чи batch implementation виконати окремий `representative_slice` gate. Обрати мінімальний репрезентативний наскрізний scope, який охоплює ризикові art/control/contact/audio/UI/commerce/progression залежності; це не фіксована кількість assets або тривалість. Gate може виконуватися спільно assets↔build після preproduction:

1. Зафіксувати canonical reference/state/camera/aspect/seed/time, acceptance parameters та допустимі delta до порівняння.
2. Довести route: доступні authoring tools/skills, editable sources, lawful fonts/audio/assets, export/import/assembly, pinned engine/toolchain, ресурси/бюджет. Записати фактичний proof найризиковіших переходів; README про потенційний tool не є перевіркою route.
3. Зібрати playable native slice з production source lineage. Виконати frame + motion/contact + gameplay audio + input/haptic і relevant menu/UI/decline/reward transitions у фактичному runtime.
4. На цільовому representative device за scope зібрати контрольовані captures, interaction/listening/haptic observations та performance measurements. Якщо device недоступний, позначити exact blocked gate і підготувати executable bridge; mass permit лишається false.
5. Незалежно перевірити застосовні must, rights/budget feasibility, modality evidence, deviations/unknowns; отримати user acceptance саме матеріального art/feel scope, якого ще немає. Передати точні slice hashes та дозволений batch scope.

Контрольований pixel/overlay comparison — додатковий інструмент; він не замінює perceptual review, рух, прослуховування чи відчуття контакту. Не обіцяти однакові pixels на всіх hardware. Немає доведеного route — спершу локальна спроба іншого доступного route; потім конкретний blocked result/bridge або material delta proposal. Primitive geometry, generic UI або синтетичний beep не стають accepted заміною через брак інструмента. Production route може бути простим, якщо саме така якість і характер були прийняті.

Зміна master, renderer/camera, shared shader/rig, input/contact timing, audio mix чи economy може відкрити залежну частину slice знову. Не вимагати повного remake для незалежного typo fix. `mass_production_permission` має бути виведеним із чинних evidence/review/acceptance scopes та hashes; boolean у шаблоні сам нічого не дозволяє.

## Commerce як частина бажаного досвіду

Починати з бажання гравця: новий спосіб дії/контекст/роль, виразний образ/ансамбль, володіння та збирання, змістовний контент, зручність або темп за fit. Перевіряти, чому це хочеться пробувати й повторно використовувати. Покупка не має за замовчуванням продавати перемогу, закривати створену для цього поломку чи зводитися до recolor. Художня виразність теж може бути цінністю; вся монетизація не зобов'язана бути косметикою. Не вимагати всі commerce моделі одразу й не додавати currencies для видимої «глибини».

Від seed показувати journey `desire → discovery → trial → earned route → optional purchase/decline → grant/ownership → repeated use → new meaningful goal`. На концепті це чесна гіпотеза; preproduction переводить її в state/data contracts; build/QA перевіряють фактичну поведінку; liveops — реальний use/value/cohort outcome. Розглянути доречні шари items/tools/characters/playstyles/content/expansions/pass/resources/acceleration/art ensembles та пояснити вибір і відмови. Це меню можливостей, не mandatory catalog.

Для кожного offer зафіксувати exact contents/version/entitlement; eligible moment/cohort і природну причину показу; реальну trial route або предметну альтернативу демонстрації; earned route/pace й assumptions; price source/currency/region; recurrence/duration/caps/expiry; decline/no-offer path; discoverability і повторне використання; наступну ціль; production/service cost; grant/save/restore/refund/revoke/pending/error behavior. Якщо meaningful equivalent earned route відсутній, показати межу paid content і повноцінну альтернативу досвіду, а не називати її «free unlock». Матеріальні choices paid randomness, ads, subscription, paid acceleration, backend і витрати потребують чинної згоди до реалізації.

Економічний graph пов'язує всі currency/resource sources/sinks/exchanges/caps/rounding/expiry/authority з action, unlock, offer і persistence. Кожній валюті дати унікальну роль і complexity cost; показати, що зміниться від об'єднання. Account/server/payment authority та real-store rules не виводити з design JSON. Purchase receipts/idempotent grants/restore/refund tests залишаються предметним MONEY-01 closure.

Моделювати cumulative impact у сценаріях no-offer control, engaged nonpayer, різних платників і релевантних newcomers/returners/skill/region cohorts. Порівнювати однакові content/skill/time assumptions; окремо врахувати trial, free acquisition, full owned collection, stacked boosts, repeated purchases, pass timing, interactions/synergies та одночасні offers. Виміряти access/playstyle breadth, time-to-capability, time/cost-to-goal, challenge/failure/recovery, power/dominance, social/competitive effect за scope, enjoyment/offer load і regret/decline де є реальні дані. Позначати gaps/ranges/sensitivity. Однакова DPS предметів окремо не доводить horizontal balance всієї колекції.

Revenue/retention модель відокремлює one-time/recurring gross, refunds/fees/net, variable service costs і finite production/fixed costs. Не перетворювати разову покупку на щомісячний дохід без recurrence mechanism. Не називати conversion/eCPM/LTV/retention фактами без власних належних спостережень. Хороший синтетичний сценарій може відхилити хибну модель, але не довести бажання платити або прибутковість.

## Research, launch context і межі доказів

Підтримувати ledger `fact / inference / hypothesis / unknown` із source/date, market/platform/audience scope, методом, confidence rationale, суперечливими сигналами, limitations та decision impact. У `claims.json` inference/hypothesis лишаються `hypothesis` з поясненням типу; не піднімати їх до observed заради сумісності назв. Research фіксує observable mechanics/art/commerce, demand/search/community/review signals за доступністю, comparison context, launch timing/competition/device/distribution/production constraints і відкриті питання. Чужі downloads/revenue claims перевіряти за походженням та не видавати за власні outcomes. Висновок із джерел явно називати inference.

Свіжі store/payment/privacy/SDK/market eligibility requirements перевіряти за офіційними джерелами на відповідному design/release кроці. Немає даних — позначити unknown і найдешевший meaningful test. User playtest, recording фактичного native slice, listening audition, haptic device observation, sandbox transaction, store approval та production telemetry — різні докази. Text critique, mockup, simulated cohort і build log їх не замінюють. Записати фактичного observer, setup/build/content hashes, method, result, limitations і дату.

Популярний жанр, багато систем, красивий кадр, багато валют, retention формула чи чужий успіх не гарантують масовості, replay, payer desire або прибутку. Розмір команди/кількість кандидатів теж не quality proof. Перевірки пропорційні невизначеності, наслідкам і stage; негативний контрприклад і cheapest discriminating test корисніші за вигаданий загальний бал.

## Закриття поточного етапу, не всього майбутнього

`experience-coverage` — companion до чинних handoff records: посилатися на ті самі IDs/hashes, не заводити конкуруючу істину. Stage closure потребує локально due must, актуальних artifact/evidence links, незалежного пропорційного review і чинних material decisions. Показати met/pending/blocked/N/A окремо. У цьому контракті stage acceptance не дає production/publish permission поза погодженим scope.

| Етап / gate | Що закрити зараз | Що чесно переноситься далі |
|---|---|---|
| studio | Прийнята identity/master provenance/scope, rights/setup та project intent/intake. За існуючої студії перевірити й перевикористати її. | Game art, engine, paid model можуть бути pending; студія не погоджує їх заздалегідь. |
| concepts | Кожний seed: action/progression/commerce/art promise; різні аргументовані напрями; системний паспорт кожного ілюстрованого кандидата, systemic/replay/resource/offer causal model, research ledger, усі target/profile/layer/unknown/production-route maps, actual image inspections, незалежні semantic reviews і validation plan. Selected production concept лише за чинним explicit choice. | Не вимагати production rigs/stems, завершений runtime/device proof, empirical retention чи sandbox purchase. Saved favorites і research previews не є selected production concept. |
| preproduction | Виконувані interaction/state/progression/economy contracts, all-layer art/audio/motion/haptic spec, finite launch inventory, sources/rights/tool feasibility, modality tests і representative-slice contract; закрити material choices, від яких залежать дані/код. | Physical slice proof може бути наступним assets↔build job; mass production ще заборонена. Не називати test plan виконаним тестом. |
| representative_slice | Production source→native runtime→representative device evidence; control/contact/motion/UI/audio/haptic/parity/performance за scope, незалежний review й exact user acceptance невирішеного material art/feel. | Дозволити тільки перевірений batch scope. Повна гра, store validation та production telemetry ще pending. |
| assets | Після slice: фактичні editable sources/exports, coverage layer inventory, lineage/rights/import receipts, visual/motion/audio auditions і parity за виробленим scope; unknowns до залежного batch закриті. | Не плутати окремий audition з фінальним gameplay mix або artist review з native device QA. |
| build | Фактичний native playable scope, state/input/recovery/save/purchase contracts, runtime asset links, source/toolchain/native receipts, modality/performance captures і implementation coverage. | Build completeness не є незалежним QA pass, user acceptance, store approval чи observed revenue. Незроблена platform лишається blocked/pending. |
| qa | Незалежні застосовні requirement checks на конкретних builds/devices, fidelity/motion/listening/haptic/input/accessibility, replay/progression/economy/cumulative cohorts, save/payment/errors/regression; defects із severity/owner/closure. | Симуляція не замінює human desire; непроведений user playtest лишається pending. Release decision використовує чесні limitations. |
| release | Чинний approved build/metadata parity, official policy/date checks, rights/privacy/payment/device scope, rollout/rollback/support, exact public-action authorization і receipts. | Submission ≠ approval ≠ rollout; sandbox ≠ реальний payout. Публікація не запускає неавторизований monitoring/scheduler. |
| liveops | Фактичні production signals/cohorts/costs, content/offer cumulative impact, incident/experiment bounds, dependency-scoped regression та visual/audio/gameplay continuity нових releases. | Гіпотези не стають фактами від часу; повернути тільки потрібну гілку design/assets/build/QA, не починати студію заново. |

Відсутня modality/capability дає конкретний `blocked` scope, локально готовий результат та launch/return bridge: потрібні input files/hashes, людина/середовище/tool, точні дії, expected output/receipt і команда повторної перевірки. Не знижувати quality target для формального `accepted`. Author self-check чесно позначити; він не незалежний pass.

Search mode — material intent, не прихований default. Портфель адаптувати до brief і фактичної різноманітності/доказів; не задавати mandatory candidate count. Протокол `4×100` вмикати лише як явно обраний режим пошуку з bounded execution, конкретними outputs і stop rule; він не обов'язковий для кожної гри. `pause now`, `after artifact`, `after stage`, search-only і preview-only зберігати в intent lock та runtime state. Stop перевіряти перед кожним залежним job/gate; зробити checkpoint з completed/current/pending/next/return. Resume звіряє файли, hashes та зовнішній outcome; не повторює purchase/upload/deploy з невідомим результатом.

## Негативні приклади для review

| Спроба закрити вимогу | Чому fail / належне закриття |
|---|---|
| «Три art directions»: та сама 3D сцена в різних кольорах | Немає різних художніх рішень і причинного fit. Показати відмінні camera/shape/material/motion/type/audio принципи та вплив на дію. |
| Hero image approved → усі menus, rig і музика approved | Згода мала інший scope. Додати unknowns і exact per-layer acceptance; не вигадувати bytes чи права. |
| 95% coverage, але mute приховує небезпеку | Due accessibility must не усереднюється. Додати інформаційний fallback і фактичний modality-off test. |
| «Глибина»: 12 кнопок, 5 валют, нескінченний +1% | Не доведено взаємодію систем, нові рішення чи зміну старих задач. Переробити experience/progression graph і перевірити відмінність рішень. |
| «Реплей»: мільйон seeds з однаковим timing | Нових рішень немає. Показати grammar/context/strategy differences та fixtures. |
| «Horizontal»: кожен paid tool має однакову DPS | Сумарна колекція/доступ/synergy можуть домінувати. Перевірити owned portfolio, contexts, skill і cumulative cohort impact. |
| Gameplay прототип готовий; shop і art додамо потім | Seed не мав повного promise; інтегрувати desire/earned/decline/use journey та художню причинність до наступного вибору. |
| Один PNG + музичний опис → assets done | Немає editable production sources, actual audio і import proof. Позначити scope partial та потрібні jobs. |
| Телефона немає → haptics N/A → mass production allowed | Capability gap не N/A. Block slice gate, передати executable bridge, зберегти intended quality. |
| Concepts відхилено, бо ще немає store receipts | Вимогу застосовано завчасно. Закрити concept intent/plan, перенести actual payment due gate. |
| Simulation дала LTV > cost → «прибуткова гра» | Модель залежить від assumptions; відокремити facts/inference/unknown і перевірити власні cohorts/use/value. |
| R4 previews завершено → автоматично chosen concept | Preview/search stop не дає production choice. Зберегти stop і favorites; чекати відповідного explicit decision. |

Закриття контракту — конкретні актуальні докази й чинна згода у визначеному scope. Наявність цього файла або заповненого шаблону сама нічого не доводить.

## Уточнення 3.0.0: ті самі вимоги, конкретніший доказ

Джерело `UA26-SYS-01…07` — точні витяги в `assets/systemic-user-sources.json`; їхнє тлумачення не називати дослівною цитатою. Додати сім due checks до тієї самої карти покриття й project registry. [Системний контракт](systemic-design.md) задає логічний AND: здійсненний референс, причинна глибина, зручний доступ, розвиток, ресурси, альтернативний досвід та зрозуміла ціла гра. Для preview-only не відкладати їх до фіналістів; для native/device/human outcomes не вигадувати раннього доказу. Коротка людська картка не замінює паспорт. Візуальне схвалення користувачем і gameplay/device acceptance лишаються окремими scopes.
