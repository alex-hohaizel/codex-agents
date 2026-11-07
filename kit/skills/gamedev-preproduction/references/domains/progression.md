# Розвиток, винагороди й довгі цілі

## Застосування, вхід і власний результат

Застосовувати до розвитку досвіду в часі; RPG-статистики, loot, crafting, сезони й постійну силу не нав'язувати. Прийняти правила, структуру світу/контенту, навчальний граф, доступний launch scope і бізнес-модель. Власний результат — progression/reward graphs, typed unlock rules, player journeys, pace/balance model і novelty/exhaustion plan. Використовувати [шаблон](../../assets/domain-templates/development-rewards.template.json) як authoring fragment, а не альтернативний registry.

## Визначити, що саме розвивається

Відокремити застосовні шари: майстерність і знання; стан у межах спроби/матчу/задачі; сталі можливості персонажа/інструментів/техніки; collection/loadouts; світ/access/consequences; optional social/team goals; довгий postgame. Непотрібний шар вимкнути з предметним поясненням. Навіть без permanent power гравець може розвивати знання, інструментарій і доступ; не замінювати розвиток нескінченним лічильником.

Для вузла графа задати ID, player goal, prerequisites, unlock/grant, нову дію/можливість, trade-off, застосування, старий контекст, який він переосмислює, наступну видиму ціль, earned/paid relation, persistence/reset/cap і evidence. Для ребра — умова, authority, cost/time, presentation, reversible/irreversible behavior, failure/recovery. Значення й формули мають units/ranges/rounding, source/rationale й один runtime/config source.

Глибина предметів/навичок/техніки визначається відмінними рішеннями. Нова дальність, режим, взаємодія з матеріалом, мобільність або обмеження можуть бути значущими; десять +1 не створюють десять playstyles. Власні характеристики й enemy progression мають зрозумілу для гравця роль, cues і межі. Якщо є дерево/набір модулів, задати сумісність, previews/comparison, respec/switch rules, duplicate handling і відсутність dead choices. Не вимагати випадкового loot за прикладом іншої гри.

## Винагорода як завершений цикл

Для reward family описати за що вона надається, яке зусилля/ризик визнає, що очікує гравець, точний предмет/право/зміну стану, claim/presentation, реальне застосування й наступну змістовну мету. Це можуть бути здібність, інструмент, предмет, світ/access, знання, customization або визнання — за задумом, а не загальний «XP».

Задати guaranteed/chance/choice, pool/weights/version за застосовності, доступну гравцю інформацію, repetition/duplicates, eligibility, caps, expiry/claim window, authoritative grant, retry/deduplication, persistence/revoke. Рідкісність не є цінністю без змістовного використання. Підсилення presentation не повинно приховувати нульову функціональну різницю. Випадкова нагорода й paid randomness — різні продуктові рішення.

Зв'язати reward із конкретним progression node і сценарієм використання. Порівняти винагороду за mastery, exploration, risk, completion, comeback та інші застосовні до гри причини. Не примушувати всі ці категорії. Reward schedule має підтримувати player agency й чесні цілі; не створювати штучний frustration wall для продажу полегшення.

## Пейсинг і повна арка

Скласти конкретні journeys: перший вхід/перший завершений цикл; наступне повернення; рання, середня й пізня гра; перерва/повернення; завершення launch content; postgame. Часові точки обрати за жанром і scope, не як універсальну квоту. Для кожної — що гравець знає/може, які нові рішення й контексти має, яку нагороду отримує/використовує, чому хоче продовжити й що може набриднути.

Показати розвиток як послідовність introduction → practice → combination → meaningful variation → mastery/новий контекст. [Навчальний граф](experience.md) забезпечує потрібні знання до перевірки. [Світ](world.md) дає нові можливості й добровільне повернення. Відкрита зона без нової ролі або весь розвиток через більший HP не закриває арку.

Для скінченного launch scope визначити content exhaustion, можливі завершення, optional challenges і допустимий повтор. Довга гра не зобов'язана вимагати нескінченного grind або щотижневого ручного event. Якщо передбачений ongoing content, пов'язати cadence з реальною authoring/QA місткістю й витратами.

## Моделювання й контрприклади

За складних кривих виконати модель з casual/regular/skilled, newcomer/returning, lucky/unlucky, nonpayer/payer profiles за обраною моделлю. Записати playtime/session assumptions, performance policies, seeds/config/version і raw outputs. Перевірити time-to-meaningful-unlock, starvation/overflow, stranding, mandatory unlocks, snowball, catch-up, dominant build, content exhaustion, платний cumulative advantage та softlocks. Coverage класів важливіша за довільну кількість seeds.

Контрприклади: нагорода, яку ніде застосувати; гілка без корисного сценарію; обов'язковий paid counter; новий інструмент обходить усі старі обмеження; повторна покупка дає прихований refill; повернення дає лише той самий бій без нової мети; «50 годин» дорівнює невідомому множнику grind. Виправляти причину, а не додавати ще валюту.

## Строк доказу, взаємодії й ролі

Concepts доводить причинний ранній/середній/пізній задум та використання нагород, не точний баланс. Preproduction задає typed graphs/rules й concrete worked examples. Slice реалізує unlock→presentation→use→save→return у реальному runtime; застосовні device/control cues перевіряються фактично. Beta перевіряє розуміння, tempo, бажання повернутися й meaningful choice на людях. Release незалежно перевіряє critical grant/save/purchase integrity. Liveops використовує реальні cohorts без видавання targets за факти.

Progression/reward specialist готує graphs/models; systems/world/UX/commerce узгоджують їхні наслідки; runtime реалізує ті самі IDs; independent review шукає dead paths і домінантність. Зміна reward price, tool capability або world access відкриває пов'язані model/UX/content/commerce/save перевірки.

## Джерела й статус рекомендацій

- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) — приклад collectable abilities, варіативного проходження й доступу; не шаблон обов'язкового метапрогресу.
- [Roblox: Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques) — рекомендації платформи щодо навчання в момент релевантної взаємодії.
- Typed unlock/reward graphs, симуляційні профілі й due gates — правила агента. Симуляція не доводить retention, попит або бажаність нагороди для людей.
