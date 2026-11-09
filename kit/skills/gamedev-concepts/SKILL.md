---
name: gamedev-concepts
description: "Game Atelier — дослідити, порівняти й довести до вибору цілісні концепції динамічної мобільної гри. Використовувати для задумів, нового пошуку, візуального відбору, аудиту кандидатів, ремонту механік і продовження чинного пошуку; охоплювати системи, світ, розвиток, навчання, керування, художній задум, комерційну модель та здійсненний виробничий маршрут без автоматичного вибору гри. Використовувати для повних C1, ескізів C0, системної різноманітності й перевірки здійсненності."
---

Відповідати за повний C1 кожної гри, представленої як завершена концепція. Перевіряти цілісну архітектуру, змістовну різноманітність і реалістичне виробництво до презентації; матеріал C0 явно називати ескізом.

## Виробнича якість і контекст6.0

Для нового, делегованого чи відновленого task застосувати [контекст виконання](references/context-capsule.md): current native sources/requirements/identity/authority, усі застосовні must та їхні залежності, exact inputs, outputs/consumer, budget/stop і належне приймання. Optional `scripts/context_capsule.py` компілює заявлену проєкцію, не створює згоди чи сертифікації.

Перед створенням або зміною матеріалу прочитати застосовний [виробничий контракт](references/production-quality.md) і medium profile з `assets/production-profiles.json`. Зберегти визначальні властивості референсу — композицію, масштаб, виразний механізм, взаємодію й функціональну глибину; палітра/назви елементів самі не доводять fidelity. Спершу довести representative slice на actual носії, потім тиражувати. Creative, functional, source/runtime та owner verdicts окремі. Пряме доручення й надана творча свобода сильніші за own defaults; прийняту identity не змінювати заради різноманіття.

## Контракт 4.0 та предметне завантаження

Перед новим scope прочитати [вихід і приймання цього маршруту](references/v4-route.md). Звірити maturity **C0 / C1 / T** окремо від фактичного implementation stage. C0 — позначений ескіз; C1 — повний задум кожного представленого завершеного кандидата; T — точний виробничий контракт прийнятої до розробки гри. Ранній обмежений spike дозволений до T; він має питання, inputs, oracle й межу, а не статус готової реалізації.

Шість логічних компетенцій P1 завантажувати за предметом, а не як шість додаткових етапів:

| Компетенція | Точний ресурс |
|---|---|
| Поведінка, математика, фізика, стани, RNG | [Math](references/v4/math.md) |
| Каталоги, сумісність, комплекти, розвиток, винагороди | [Catalogs/progression](references/v4/catalog-progression.md) |
| Світ, генерація, маршрути, encounters, ритм, AI | [World/AI](references/v4/world-ai.md) |
| Лор, знання, сюжет/діалоги, реактивний канон | [Lore/narrative](references/v4/lore-narrative.md) |
| Намір, touch, камера, UX, навчання, мультимодальність | [Experience](references/v4/experience-commerce.md) |
| Метагра, економіка, монетизація, магазин, платежі | [Commerce](references/v4/experience-commerce.md) |

Наскрізно підключати [Persistence](references/v4/persistence.md) для state/continuity й [Production](references/v4/production.md) для операцій/ролей/recipes/доказів. Логічний поділ компетенцій не вимагає одного файла або одного агента на кожну. Source IDs й accepted masters зберігати. Для продовження відновити фактичні вимоги, рішення й матеріали продукту та створити поточні contracts; попередні формати результатів не читати й не конвертувати.

Для активних систем вести один зв’язок requirement → rule/state/catalog → production operation → consumer → scenario → actual evidence. Перевіряти застосовність усіх 20 виробничих напрямів; не вимагати 20 окремих документів чи агентів. Missing tool/device — блокер належного доказу, а не `absent_by_design`.

# Game Atelier 6.0.0 · Концепції

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

## Вхід і спільна модель

Працювати українською як предметний модуль `gamedev-director`. Приймати звичайний запит і повертати конкретний результат у його scope; не вимагати ручного керування навичками. До залежної роботи прочитати [workflow 4.0](references/game-model-workflow.md), [формат Game Model](references/model-format.md), [intake і повернення](references/unified-agent.md), [core](references/core-contract.md), [handoff](references/handoff-contract.md) та актуальні вимоги/рішення/knowledge проекту. Звірити source hashes, checkpoint, budget, права й user-defined stop. Прямий виклик concepts проходить ті самі gates.

Вести одну канонічну Game Model зі stable IDs і залежностями; card, паспорт, GDD, asset brief та порівняння є її узгодженими проєкціями. Зв'язувати user source → requirement → правило/стан → залежності → артефакт → доказ → reviewer → closure. Не створювати другу authority registry. Розрізняти designed, simulated, built, device-tested, player-observed і user-accepted.

Завантажувати модулі за реальною роботою: [research](references/domains/research.md) для доказів/портфеля; [systems](references/domains/systems.md) для дій/характеристик/агентів; [world](references/domains/world.md) для простору/зустрічей/повернення; [progression](references/domains/progression.md) для розвитку/винагород; [experience](references/domains/experience.md) для input/camera/навчання/UI; [creative](references/domains/creative.md) для art/motion/audio; [commerce](references/domains/commerce.md) для економіки/магазину; [lifecycle](references/domains/lifecycle.md) для повноти продукту й підтримки. Застосовність визначати змістом гри; missing capability не є N/A. Не завантажувати всі references для дрібного repair.

Предметні процедури: [product systems](references/product-systems.md), [fidelity](references/concept-fidelity.md), [research evidence](references/research-evidence.md), [команда](references/agents-context.md), [бюджет](references/model-budget.md). [Experience](references/experience-contract.md) і [systemic](references/systemic-design.md) зберігають незнижувані вимоги 2.1; конкретні вимоги 3.0 уточнюють їх. `concept_gate.py` перевіряє чинний systemic passport перед ілюстрацією; він не замінює повну модель або предметний review. Нову вимогу не перетворювати на формально заповнену клітинку.

## 1. Відновити намір і можливості

Відкрити актуальні названі файли, exact studio revision/master/rights і потрібний lawful payload. Зберігати прийняті знак і назву чинної студії; не виводити тіло, костюм, лор або стиль усіх ігор з логотипа. Saved favorite, рекомендація, visual proposal, chosen concept, accepted master і production permission — різні стани.

Зберегти чинні кандидати, фаворити й історію як проєктні джерела; нові вимоги оформити successor revision/impact map. Не обирати гру й не запускати production під час workflow-аудиту. [Історичні профілі](references/historical-project-profiles.md) підвантажувати адресно. Конфлікт display/internal ID вирішувати через джерело й aliases.

Перевірити host, image/audio/DCC tools, native SDK, права, пристрої та ліміти. Work придатний для research/visual/briefing; Codex — для моделювання й виробничих перевірок за actual capability. Недоступний тут Blender/рушій не є глобальною забороною 3D; майбутній маршрут має prerequisites й due proof. Не обіцяти можливість через назву інструмента й не знижувати accepted fidelity через відсутню модальність.

Уточнювати лише невирішені material choices: аудиторія/вік/ринки, платформи, orientation, online/offline/co-op, engine з істотними наслідками, hardware/охоплення, бюджет і commercial boundaries. Чинні рішення переносити без повторного запиту; незалежну дозволену роботу продовжувати.

## 2. Спроєктувати пошук із навмисною різноманітністю

Визначити скінченний обсяг/output/stop із доручення. 90, 100 або 4×100 не є default. Новий пошук, repair, resume, visual selection та аудит мають різні task contracts. Старі ідеї використовувати як labelled controls/lineage, а не нові назви тих самих hooks.

Розділити осі: виробничі зусилля/вартість; обсяг контенту й життя продукту; арка сесії; topology/переходи; жанр/провідна дія; camera projection/tracking/framing; input grammar; art direction; progression/replay; commerce fit. «Мала» не означає одну нерухому арену; великий світ не означає open world; масштаб не визначає жанр або досвід. Старі Small/Scenes/World зберігати як зрозуміле групування з mapping, а не примусову архітектуру гри.

Скласти карту перспективних відмінних напрямів. Для кожного кандидата визначити причину присутності, найближчих сусідів і різницю в рішеннях/ритмі/досвіді. Не перемножувати випадкові жанри/камери/стилі для квот. Два незалежні творчі погляди доречні; один інтегратор зводить fantasy/gameplay/world/progression/UX/art/economy. Спеціаліст має assigned IDs, inputs, output path, cap і done check; не створювати порожні менеджерські поверхи.

Використовувати [portfolio template](assets/domain-templates/portfolio-review.template.json) як авторську допомогу. Окремо перевіряти новизну/відсутність копії та різноманіття набору. Один art pipeline може підтримувати різні стилі; інша палітра не доводить іншої гри. Кластери схожих рішень ремонтувати до дорогого batch generation. Брак різноманіття не приховувати жанровими ярликами.

## 3. Побудувати цілісного кандидата до ілюстрації

Кожний C0 preview має labelled causal sketch/Game Model; кожна завершена концепція для остаточного вибору має повний C1 за [контрактом маршруту](references/v4-route.md). Не називати короткий passport завершеним C1; повний виробничий T створювати наступним етапом для прийнятої гри. До кадру пояснити ким і навіщо грає людина, її дію зараз, арку спроби, розвиток, взаємодії, виграш/помилку/відновлення, довгу власну мету та здійсненний production route. Reader card є проєкцією цих рішень.

Задати правила через state, condition, player intent/input, cost/limit, contact/response, next state, counterplay і recovery. Показати, як зміна одного правила змінює рішення в іншому. Порівняти щонайменше два причинні контексти з тими самими інструментами та іншою найкращою дією. Виконати remove-system і strongest-simple-policy checks. Дві-три дії допустимі за глибокого простору рішень; десяток інструментів без різної логіки й взаємодій не доводить глибину.

Активувати потрібні пласти: власний рух/характеристики/стани; інструменти/техніка/inventory; супротивники/союзники/мешканці; матеріали/геометрія/ризики; ресурси; задачі/власність/наслідки світу. Для значущого предмета/властивості пояснити функцію, набуття/розвиток, сумісність/обмеження, помітний ефект і залежності. Не нав'язувати RPG-інвентар, бій чи валюту кожній грі.

Для ворогів/викликів визначити ролі/наміри, сприйняття/пам'ять, стани/рішення, telegraphs, атаки/здібності, взаємодію з оточенням/іншими ролями, контргру, ускладнення і fairness. Показати encounter, де комбінація ролей змінює стратегію. Більше HP і recolor не є новим супротивником; адаптація не означає прихованого читання input. Для гри без бою дати предметну поведінку її викликів.

Live control перевіряти input now/later/absent. Не видавати canned animation після походового вибору за динамічне ядро цього brief. Керування, camera distance, читабельність і системна складність повинні узгоджуватися; засоби доступності зберігають причинність гри.

Damage, crash і death/failure є частиною C1 ризику та відновлення: визначити причинну модель, термінальні/проміжні стани, kept/lost/cost/retry і persistence. Для C1 не залишати їх невідомими під словом «бойова система»; точні formulas/capture/ticks/priority замикаються у T.

## 4. Замкнути світ, розвиток, нагороди й навчання

Описати topology, маршрути/входи/виходи, encounter families, навігаційні cues, risk/reward та альтернативи. Камера показує потрібний фрагмент, а не обов'язково весь світ. Інтерактивність світу змінює доступ/можливості/наслідки; продумані локації й переходи допустимі без open world. Погоду/агентів/події/геометрію комбінувати за constraints. Непередбачуваність не повинна ламати вивчені закони чи чесну відповідь гравця.

Розвести mastery, run progression, сталі unlocks/builds/колекції та зміни світу. Для early/middle/late показати нову можливість і переосмислення знайомої задачі. Визначити дальшу мету, discovery, prerequisites, нагороду, її застосування й наступний вибір. Для повернення в стару локацію дати добровільну ціль, новий контекст/доступ, відомий чи явно невідомий шанс, tracking та захист від порожнього гринду. Не примушувати всі жанри до однакової метапрогресії.

Побудувати reward loop: за що → як визначається нагорода → коли/як видається → яку можливість змінює → що гравець робить далі. Пов'язати винагороди з навичками, предметами, властивостями, маршрутами/світом, колекціями чи mastery за fit. Стати/модифікатори мають власний ефект, межі й stacking. HP/витривалість/стани потребують витрати, відновлення, читабельності та наслідків; не додавати смугу заради складності.

Побудувати навчання від першої дії до пізньої комбінації: безпечна спроба, видимий наслідок, самостійний перенос, наступний виклик, повернення після паузи й повторна допомога. Зазначити prerequisite knowledge для encounters/unlocks. Не ховати можливості в одному текстовому туторіалі й не примушувати досвідченого до повтору інструкцій. First-play/normal/peak і повний player journey охоплюють також меню, налаштування, inventory, результати, магазин, suspend/save/return і помилки.

Визначити finite launch scope й content grammar: authored vocabulary, комбінації, заборонені/нечесні стани, відмінні ситуації, production capacity і досвід після стартового набору без обов'язкової щотижневої ручної події. Seeds не є нескінченним змістом; 10 переставлених арен не є доказом повноцінної довгої гри.

## 5. Порівняти економіку, монетизацію й магазин

Досліджувати механізми релевантних успішних ігор за актуальними первинними джерелами. Відрізняти правила продукту, публічні результати й припущення про причину успіху. Порівнювати придатні моделі: premium, expansion/content, playstyles/колекції, pass/сезон, обмежені rewarded можливості/спроби, consumables/валюта, convenience/acceleration та інші за fit. No-offer control допомагає перевірити вплив пропозицій; він не обирає бізнес-модель за користувача. Не обіцяти вивчення буквально всіх ігор чи однакове застосування всіх моделей.

Визначити бажання з core, функцію покупки/реклами, earned/paid шлях, cap/expiry/replenishment, повторну цінність, сумарний вплив портфеля, вартість підтримки й контрприклад домінантної платної стратегії. Якщо пропонуються extra attempts, booster чи limited currency, описати конкретну дію, доступ без платежу, межі й decline/no-fill; не обирати енергію для всієї гри автоматично. Paid randomness, recurring spend і store integration мають власні матеріальні choices.

Вимогу альтернативного досвіду зберегти як предметну цінність там, де застосовна. Не зводити всі жанри до одноразового sidegrade kit; не вимагати окремої кампанії/save для альтернативи в тому самому проходженні. Перевіряти cumulative access/synergies, відсутність прихованого refill/reset від зміни комплекту, повноту базового досвіду та конкурентний доступ. Для F2P гіпотези перевіряти повну free/no-offer арку; premium не зобов'язаний мати всю гру безкоштовно. Latest user requirement має пріоритет над давнім шаблоном.

Проєктувати магазин як journey: discovery → зрозуміла пропозиція/проба → порівняння/ціна/доступ → підтвердження → receipt/entitlement → використання → restore/refund/failure/recovery. Розкласти sources/sinks, час отримання, eligibility, localized price source, grant exactly once та offline очікування. На C1 потрібна повна архітектура економіки/метасистем, каталог сімейств і journeys з ризиковими моделями; точні запускові числові й транзакційні контракти з oracles замикаються у T до залежної реалізації. Симуляція не є revenue, людським бажанням чи доказом чесного pace.

## 6. Визначити camera/art contract і показати здійсненний кадр

Перед generation заповнити camera/framing, art direction і visual state coverage з посиланнями на Game Model. [Camera template](assets/domain-templates/camera-framing.template.json) розділяє projection, tracking, framing, zoom, transitions, scale й offscreen information; [coverage template](assets/domain-templates/visual-state-coverage.template.csv) зв'язує стани з sources/captures. Шаблон є авторською допомогою, не доказом виконання.

Вивести ракурс/близькість із ключової дії, швидкості, часу передбачення й екрану. Визначити normal/peak contact, персонажа/інструмент/ціль, thumb occlusion, HUD hierarchy і допустимі зміни framing. Не успадковувати 12% героя, whole-arena, fixed camera чи два диски як default. За руху камери перевіряти authored coverage, непобудовані боки, навігацію, offscreen threats і комфорт. Кадр позначати поточним фрагментом, не доказом розміру світу; за потреби показати кілька зв'язаних станів/ділянок, motion sample — лише якщо реально створено.

Для art direction мати production profile: actual/planned tools, source/export/import route, licenses/cost/capacity, representation/rig/animation/contact, material/light/VFX/UI та scene budget hypotheses. Задати silhouette/proportions, line/shape/material/palette/light, оточення, typography, UI, motion, audio/music/haptics і як вони пояснюють дію. Не підміняти art direction палітрою одного пресету. Не вигадувати editable layers, backviews, rig чи stems із PNG.

Генерувати gameplay target у цих межах: видимий causal moment, правильні scale/camera/HUD, підтримувана щільність/матеріальність. Фактично оглянути **кожний кадр до показу**, звірити з camera/element/state/input contract, записати image hash, observer, deviations/verdict і repair. Незалежний visual review може бути пропорційним, із точною вибіркою; він не замінює огляд решти. Недосяжну обіцянку ремонтувати до показу, без «потім спростимо» після вибору.

Зберегти originals/hash/provenance, element→source/assembly і known/unknown. Статус — feasibility-reviewed proposal; exact user acceptance створює reference lock у погодженому scope. Source→import→native runtime→device parity і feel перевірити в representative slice до mass production. Synthetic compositor, generated screenshot чи ціль 60 FPS не є native/device proof.

## 7. Відсіяти й передати без втрат

Виконати model checks за фактичним `scripts/game_model.py --help` і [model format](references/model-format.md): stage `concept` для Game Model; handoff pipeline має stage `concepts`. Для чинних systemic passports застосувати `concept_gate.py` з profiles/reviews/images. Структурні receipts не доводять цікавої гри. Незалежний actual reviewer перевіряє причинний зміст, strongest objection, розвиток/контент/магазин, camera/art відповідність і portfolio variety. Self-check не називати незалежним review. Невиконаний must не компенсувати score; пізній доказ не вимагати раніше due gate, але відсутність називати чесно.

Після двох однакових невдалих ремонтів змінити діагностику/підхід. За нуль придатних кандидатів надати bounded repair/test і причини. Дорогі generation jobs запускати після дешевих checks і до заданого stop. Recommendation не є user choice; завершений C0 preview не дає статусу C1, а C1 acceptance не є production permission.

Передати director briefing/порівняння, Game Model й linked passports/cards, research sources, originals, production/camera/element/state contracts, моделі/outputs, review/evidence, requirements coverage, risks і unresolved choices з owner/due/closure. Зберегти lawful studio payload і фаворити. Пакет має package-relative paths, замкнені refs/hashes; unavailable historical sources не реконструювати як originals.

Для `gamedev-preproduction` передати exact accepted revision/hash, frozen/defined/open decisions і consumer intake; не втрачати системи під словом MVP. Якщо scope лише visual selection — залишити checkpoint у concepts. Після погодженого вибору продовжувати вже доручений scope без повторного дозволу. Для Work↔Codex надати inputs, перевірені prerequisites/команди або launch prompt, expected outputs/receipt та return validation; не вигадувати local paths чи автоматичну спільність історії.

Версія інструмента: **6.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
