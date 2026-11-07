# Причинні правила, спорядження та агенти

## Застосування, вхід і власний результат

Застосовувати до правил будь-якої гри; обладнання, техніку, ворогів і бій активувати лише за задумом. Прийняти fantasy, системний паспорт, input/камеру, карту світу й розвиток. Власний результат — виконуваний rulebook, interaction matrix, каталоги застосовних actor/ability/equipment, сценарії рішень і invariants. [Шаблон](../../assets/domain-templates/system-rulebook.template.json) деталізує авторську роботу; у canonical model використовувати domains `systems`, `actors`, `equipment` та чинні `source_requirement_ids`, features, scenarios, dependencies, evidence. Не оголошувати заповнений шаблон доказом глибини.

## Механіка як правило

Задати ID, player purpose, state variables, units/ranges, input/trigger, guards, authority, phases/timing, transform, cost, outcome, feedback, error/counterplay, recovery, persistence/reset. Вказати порядок подій, clamp/rounding/tie-break, fixed/variable time, collision ownership і interrupt rules. Один runtime/config source; опис і UI посилаються на нього.

Ребро взаємодії зараховувати, коли зміна однієї системи змінює доступну дію, позицію, timing, ризик, пріоритет або наслідок іншої. Спільний колір, валюта чи слово «синергія» ребром не є. Показати конкретні цикли через застосовні movement/tool/environment/agent/resource/objective layers. Невелика кількість добре взаємодіючих правил допустима; число кнопок/предметів/статів не доводить глибини.

Для важливої комбінації описати стартовий стан → намір → input → зміни → відповідь світу/агента → наступний вибір → помилка/відновлення. Дати той самий інструмент у різних контекстах із різними розумними рішеннями. Провести ablation: що перестає працювати без правила; чи «складна система» лише відтворює заготовлений спецефект; чи найдешевша політика перемагає все.

## Ресурси, властивості та спорядження

Ресурс може бути HP, запасом, теплом, імпульсом, шумом, концентрацією або іншим значущим станом. Вибрати тільки потрібні. Для кожного задати sources/sinks, capacity/regen, витрату й альтернативну витрату, overflow/depletion, recovery, cue, reset/persistence й пов'язані дії. HP не зобов'язаний мати складну підсистему лікування; якщо вона є, її вибори й ціна повинні бути конкретними.

Для предмета/здібності визначити функціональну роль, acquisition/unlock, actions, targets, reach/shape, startup/active/recovery/cancel, charges/cooldowns, modifiers, compatibility, strengths/limits/counters, equip/switch rules і progression links. Status effects задають duration, stack cap, additive/multiplicative/exclusive composition, refresh/replace, immunity, cleansing, death/scene/reset і cues. Різні назви з тим самим +damage не є різними способами гри.

Для техніки, якщо вона є ядром, розділити chassis/handling, propulsion, functional modules, attachments й їхні budgets/compatibility. Показати, як маса/баланс/живлення/місткість або інші обрані властивості змінюють дію й маршрут. Не нав'язувати всі перелічені параметри. Описати складання, порівняння, збереження loadout, пробу, зміну модуля, недійсну конфігурацію, repair/recovery. Кастомізація має давати різний досвід, а не десятки декоративних слотів.

## Агенти, супротивники й контргра

Для застосовного агента задати роль у виклику, body/movement affordances, senses/ranges/occlusion, memory/forgetting, knowledge uncertainty, intent, decision priorities/utility, actions, navigation, resource use, transitions, coordination, retreats/recovery. Відокремити actual world state від того, що агент сприйняв і пам'ятає. Визначити, як шум, сліди, пошкодження, геометрія й дії інших змінюють рішення. FSM, utility, behavior tree або інша структура — реалізаційний вибір за fit, не обов'язкова технологія.

Для небезпечної дії задати telegraph, readable commitment, hit/avoid conditions, reaction opportunity, counters, interruptability, cooldown і наслідок помилки. Зв'язати offscreen behavior із камерою; не додавати невидимі неминучі атаки. Складність може змінювати поведінковий набір і координацію в описаних межах, але не приховано читати input чи вигадувати силу заради купівлі. Відокремити чесну адаптацію від таємного підтасовування.

Каталог ворогів/викликів містить відмінну tactical role, зміну рішення гравця, комбінації/заборони, навчальні prerequisites, середовище й production cost. Звичайні, елітні, особливі й босові форми потрібні лише за задумом. Нова шкіра/HP без нової ролі не закриває відмінність. Без бою ці ж принципи застосовуються до суперників, фізичних перешкод, задач або інших релевантних джерел виклику.

## Зв'язки й перевірки

Пов'язати правило з [input/feedback/learning](experience.md), [world/encounters](world.md), [unlock/rewards](progression.md), [елементами art/motion/audio](creative.md), [commerce](commerce.md) та save/analytics у [lifecycle](lifecycle.md). Зміна hit timing відкриває залежні animation/camera/telegraph/control checks; новий платний інструмент — не лише SKU test, а interaction/dominance review.

До концепту потрібні причинні сценарії та чесні невідомі. До preproduction — typed values/contracts і межові приклади. На slice виконати ті самі inputs із recorded state/seed; спостерігати normal/peak/error/recovery, animation/contact та реальний touch. На beta перевірити людське читання намірів/контргри. Перед release незалежно перевірити critical save/money/authority paths. Модель може знайти softlock чи домінантність, але не сертифікує fun.

Gameplay/systems author виробляє правила; AI/encounter specialist — застосовні агенти; runtime engineer — реалізацію/trace; UX/creative — cues; незалежний reviewer перевіряє контрприклади. Одна людина/агент може виконувати кілька авторських компетенцій; це не робить self-check незалежним.

## Джерела й статус рекомендацій

- [Epic: AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine) — офіційна документація інструмента; відокремлення сприйняття, пам'яті й рішень придатне як принцип, API не переноситься автоматично.
- [Epic: Behavior Tree Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview) — документація конкретної реалізації, не вимога обрати Unreal або behavior tree.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) — практика зміни досвіду через здібності, а не вимога копіювати badges.
- Rulebook, ablation й due-proof gates вище — правила агента; їхні числові значення обираються й перевіряються для конкретної гри.
