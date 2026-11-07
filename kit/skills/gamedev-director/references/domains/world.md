# Світ, зустрічі та граматика контенту

## Застосування, вхід і власний результат

Застосовувати до будь-якої просторової/контентної структури; географію, кампанію, супротивників і генерацію не нав'язувати жанрам, що їх не потребують. Прийняти gameplay verbs, camera/input, actor rules, progression/rewards, художню й виробничу місткість. Власний артефакт — world/content graph, finite authored vocabulary, encounter grammar, route/revisit contracts та план життєвого циклу контенту. Використати [шаблон](../../assets/domain-templates/world-encounters.template.json); authoritative choices й evidence лишаються в чинному проекті.

## Просторова структура й повна арка

Окремо визначити географічний розмір, кількість одночасно видимого, форму переходів, довжину сесії й довгий горизонт розвитку. Невелика гра не означає довільно одну повторювану арену; у scope цього користувача одна арена з незначними перестановками не закриває повноцінний продукт. Довести заплановане різноманіття ситуацій і довгу арку. Для іншого brief коротка завершена гра допустима за явним scope, без неправдивої обіцянки нескінченного змісту.

Обрати за fit безперервний простір, зв'язані зони, hub/expeditions, маршрути/траси, серії матчів/задач чи іншу структуру. Для вузла графа задати механічну роль, objectives, prerequisites, local rules, authored content, entry/exit, rest/recovery, persistence/reset, save boundary, preview/навігацію і виробничу вартість. Для ребра — спосіб переходу, guard, travel/loading cost, information shown, failure/recovery і наслідки для стану. Великий світ не зобов'язаний бути open world.

Побудувати конкретний шлях ранньої/середньої/пізньої гри: чим займався, що дізнався/відкрив, яку нову задачу це дозволяє, чому наступна ділянка відчутно інша, що зберігається й яка власна мета видима далі. Не замінювати цей граф десятьма назвами сцен або ворогами з більшим HP. До launch визначити завершення основної арки, optional goals і чесний postgame; обсяг має відповідати виробничій місткості.

## Інтерактивне оточення й маршрути

Оточення описати як стани, дії та зміни: surfaces/materials, movable/destructible/usable elements, hazards, visibility/noise, switches/flows, ownership або інші властивості за fit. Для елемента задати affordance/cue, rule, input/target, costs, interaction partners, limits, reset/persistence і recovery. Не кожний видимий prop має бути інтерактивним, але гравець повинен розрізняти потрібні можливості.

Маршрутні варіанти потребують відмінного рішення: risk/reward, витрата ресурсу, швидкість/складність, потрібна здібність, information uncertainty, наслідок для майбутнього. Бонус не ставити випадково без перевірки досяжності й ціни. Відоме правило світу має лишатися надійним, коли ситуація ускладнюється.

Для повернення задати добровільний мотив, зрозумілу ціль, отриману інформацію, потрібний unlock, змінений контекст, reward availability/probability disclosure там, де це релевантно, repetition/expiry, shortcut і ціну дороги. Нова здібність може відкривати стару зону інакше. Не вимагати повторно проходити всю порожню дорогу або продавати покупку, що лише прибирає штучну незручність.

## Encounter grammar й керована невизначеність

Розділити authored vocabulary, правила сполучення й отримані instances. Encounter задає topology/approach, objective, actor roles, hazards/material states, доступні інструменти, resource pressure, temporal phases, camera constraints, fail/recovery й reward. Для небойової гри використати релевантні задачі/перешкоди/суперників. Показати, як комбінація змінює пріоритети й стратегію; сума двох ізольованих ворогів не автоматично є новою ситуацією.

Задати compatibility/exclusion, difficulty/pacing budgets, entry/exit sockets, movement clearance, fairness/offscreen constraints, safe starts, доступну інформацію й допустимі escalation/recovery phases. Випадкові події мають trigger/eligibility, weights, cooldown/repetition, telegraph, вплив на ціль і fallback. Гравець адаптується до читабельних змін; випадковість не повинна робити вивчені правила безглуздими або створювати unavoidable failure.

Для процедурного маршруту потрібні algorithm/version/seed, reachability/solvability checks із реальними movement constants, rejected classes, repair policy, bounded retries і authored fallback. Без solver не називати випадкове розміщення повноцінним генератором. Не оцінювати контент арифметичним добутком кольорів, seeds і статистик. Порахувати semantic situation signatures й показати, які рішення між ними змінюються.

## Місткість, зв'язки й due proof

Finite launch inventory містить сімейства локацій/encounters/викликів, механічні відмінності, reusable kits, унікальні assets, authoring effort, validation cost і novelty exhaustion. Контентна cadence пояснює, як нова порція використовує наявні системи, хто її створить і скільки це коштує. «Потім додамо нові світи щотижня» без операційного плану не закриває довгий горизонт.

Пов'язати world graph із [systems](systems.md), [progression/rewards](progression.md), [camera/learning](experience.md), [creative](creative.md), [commerce](commerce.md) і [lifecycle](lifecycle.md). Новий маршрут може вимагати іншої камери, enemy behavior, навчання, source assets і save migration; перевіряти транзитивний вплив.

На concepts — конкретна causal world/content arc і приклади різних ситуацій. На preproduction — typed topology/encounter/generation rules і production inventory. На slice — normal і peak encounters, справжні transitions, camera/readability, source/import/performance proof. На beta — player agency, route understanding, сприйнята новизна й repetition. На release — відсутність blocking progression/save faults; на liveops — фактичне виснаження й ефект доданого контенту. Level/world designer готує граф; encounter/systems і UX/technical art узгоджують; independent reviewer перевіряє рішення та fair counterexamples.

## Джерела й статус рекомендацій

- [Nintendo: Wonder, chapter 1](https://www.nintendo.com/en-za/News/2023/October/Ask-the-Developer-Vol-11-Super-Mario-Bros-Wonder-Chapter-1-2460393.html) — практика поєднання трансформацій світу й довіри до правил.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) — практика доступних маршрутів, відмінних здібностей і добровільних варіантів складності.
- Topology/grammar/signature gates — проектні правила Game Atelier; жодне джерело не доводить універсальної кількості рівнів, ворогів або годин.
