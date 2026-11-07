# Прогресія й різноманітність, що змінюють гру

## Чотири взаємопов'язані шари

1. **Майстерність.** Що гравець навчається робити: точність, timing, читання telegraphs, маршрути, комбінації, ризик. Назвати observable mastery signals і як гра дає зворотний зв'язок. Зростання чисел без нових рішень не є майстерністю.
2. **У межах спроби.** Тимчасові weapons/abilities/modifiers/routes/risk-rewards, buildup, climax, завершення. Для кожного вибору задати trade-off і вплив на керування/тактику; три кнопки з однаковим +damage не доводять три playstyles.
3. **Між спробами.** Unlocks, characters, movement verbs, locations, recipes, collection, bounded power, knowledge та challenge tiers. Задати що зберігається/скидається, навіщо повтор і як уникати power wall.
4. **Довгий горизонт.** Mastery goals, evolving challenge, content updates, seasonal rules або social aspirations за жанром. Нескінченний counter без нового контексту не є нескінченним змістом.

Для кожного шару: concrete loop, duration distribution target, inputs/choices, failure/recovery, feedback, content dependency, free/paid relation, novelty exhaustion і evidence. Не змушувати всі ігри бути roguelite; альтернативна структура має виконати ті самі player-value вимоги.

## Контентна граматика

Розділити authored vocabulary, generation rules та resulting instances. Задати змістовні dimensions: geometry, traversal/combat verbs, surface/obstacle/enemy behavior, objective, resources, environment, opponent/AI, camera, hazards, build synergies, temporal schedule. Арена з іншою текстурою не рахується новим tactical situation. Нові enemy stats без патерну дії не доводять новий encounter.

Генератор мусить мати seed та version, entry/exit/socket contracts, reachability/clearance checks, difficulty budget, compatibility/exclusion rules, pacing grammar, affordance readability, safe start, bounded unfairness, deterministic resolution, repair/reject policy та fallback. Спершу скласти finite authored kit, потім генерацію. Для geometry перевірити jump/reach/collision із реальними movement constants; random placements без solver не проходять.

Приклад паркуру: route grammar чергує learn→combine→risk choice→recovery; sockets мають position/orientation/velocity bounds, максимальний gap визначений control physics; seed validation не дозволяє unavoidable blind landing. Варіативність з новими wall-run/slides/branch/flow combos змінює рішення; випадкове переміщення тих самих трьох platforms саме по собі недостатнє.

Приклад arena sport: arena topology, rebound materials, goal conditions, ball behavior, team/opponent strategies, temporary rule modifiers і player kit змінюють angle/timing/risk. Зберегти readable fairness і camera visibility; зміна кольору фону або приховане прискорення ворога не замінює контент.

## Показати player journey

Зробити конкретну таблицю first launch→run 1→run 2→run 3→session 2→hours 5/20→late game. Для кожного: що нове, що зрозумів/уміє, які рішення відкрились, наскільки змінилась стратегія, що буде наступним, як пояснюється прогрес, що стає одноманітним. Зафіксувати час до першого значущого unlock і choice; не вводити десять валют до розуміння core.

Змоделювати diverse seeds/builds/player policies, включно з найслабшим початківцем, сильним гравцем, unlucky draw, dominant strategy і exploit. Виміряти content repetition window, decision diversity, reachable builds, failure causes, resource starvation, softlocks і progression time distributions. Seed count обґрунтувати coverage; 10000 однотипних прогонів не замінюють пропущений клас.

## Перевірка новизни та виснаження

- Порахувати semantic encounter signatures, а не перестановки чи комбінації арифметично.
- Задати novelty floor на ранній/середній/пізній фазі й playtest, що гравець розрізняє нові ситуації.
- Виявити dominant build, mandatory unlock, dead choice, runaway snowball, grind plateau і sunk-cost-only return.
- Дати fair recovery і challenge ladder, щоб mastery лишалась суттєвою після meta power.
- Визначити закінчення доступного контенту й чесну postgame loop. Не обіцяти нескінченну ручну різноманітність без ресурсного плану.

Референси на Dead Cells/Vampire Survivors/Acecraft використовувати для декомпозиції принципів; не копіювати їхні конкретні системи й не приписувати їм невивчені властивості. Перевірка retention вимагає реальних гравців; simulation лише знаходить структурні проблеми.

## Capability, reward і світ у спільній моделі 4.0

Для кожного засобу розвитку зв'язати `що одержано → яка дія/властивість змінилася → де це використати → як пояснено → яка нова ціль`. Item/vehicle/character/ability розвиток має власний meaningful graph, властивості з units/formulas, поєднання й обмеження; він не зобов'язаний наслідувати RPG loot. Якщо достатньо майстерності без інвентаря, обґрунтувати її повну арку.

Винагороди задавати як конкретні grants: інструмент/здатність/властивість/доступ/зміна світу/колекція або інша цінність за fit. Визначити trigger, eligibility, pool/chance, duplicate, guarantee, persistence, presentation і першу можливість застосування. Пов'язати нагороду з добровільною довгою метою; reward animation без grant чи корисного наслідку недостатня.

Світ описувати як граф розвитку досвіду: пов'язані локації/етапи/стани, доступ, маршрути, повернення, знання/інструменти й сталі наслідки. Для revisit визначити зрозумілий objective, очікувану цінність/шанс, нове рішення та добровільний exit. Велика площа, десять завершених кімнат або сто seeds не є довгою аркою. Finite launch scope та exhaustion/postgame не приховувати обіцянкою майбутніх сезонів.

Для противників і небоєвих викликів описати behavior families, roles, perception/knowledge, дію/telegraph/counter/recovery, контекстні поєднання й зміну тактики гравця. Local AI не потребує LLM. Випадкові події мають читабельні причини, constraints і recovery, щоб змінювати стратегію без довільної несправедливості.

## Opportunity, exposure та вичерпання

Вести capability×opportunity: сімейство/розвиток → коли відкрите → частка/умови корисних ситуацій → навчання/перенос/комбінація → повертання у новому контексті → наступна мета. Генератор читає current progression і exposure history, але не підміняє unlock graph випадковістю. Шанс/гарантія/дублікати/overflow мають exact policy.

Описати all-unlocks/max-upgrades/full-collection/final/postgame/surplus states. Чесний authored фінал допустимий; не обіцяти відсутнє content. Retry/repair/reward/return cycles перевірити на ресурсний exploit/softlock. Після складного unlock гравець повинен мати ще корисну нагоду застосувати його.
