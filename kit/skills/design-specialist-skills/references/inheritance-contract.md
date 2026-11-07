# Успадкування вимог створеними навичками

Чинний контракт. Обов'язок конструктора — створити виконуваний предметний метод, а не додати загальне «працюй якісно». Кожна child skill має child contract у blueprint та власний self-contained manifest. Це застосовується і до одну навички, і до сімейства.

## Мінімальний child contract

- Stable child/stage IDs, вузький trigger, предмет/користувач/result/consumer, inherited requirement IDs і локальні IDs з source lineage. Жодна обов'язкова вимога не зникає при paraphrase.
- Needed inputs і їхній maturity, applicable/absent_by_design/blocked; typed interfaces/units/state/authority, allowed effects/permissions і межа задачі. Для domain state або формул навести точні правила й очікувані outcomes, не універсальний каркас.
- Ordered workflow з entry/exit, компетенціями/actual ownership, tool capability/recipe bindings, evidence types, budgets, self-check vs independent review, локальним acceptance та return upstream.
- Source/editable master/runtime derivative lineage, коли вони існують; current actual jobs/credentials/checkpoints залишаються в project state, не reusable source.
- Case IDs для нормального шляху, boundary/failure/retry і cold return за застосовністю; exact fixtures/oracles і негативний приклад. Семантичне приймання має належного reviewer, а не лише JSON/schema check.
- Handoff format/consumer, dependency closure/invalidation, carry-forward, repair escalation, recovery/stop/end-of-service і next action. Факт permanent monitoring можливий лише за реально запущеного дозволеного механізму.
- Discovery/reuse до нового engine або матеріального розширення: актуальні current-host metadata/approved sources, actual source read/version/hash, capabilities/inputs/outputs/stages/compatibility/rights/limits/need fit і обґрунтоване `reuse|compose|extend|create_gap`. Нові вузькі спеціалісти не залежать від whitelist; без capability card аналізувати source. Archive/duplicate/stale не обирати мовчки, counterpart іншого host — unverified до власної перевірки. Availability, installed, source_checked і actual invocation — окремі факти; permissions/cost/effects не успадковуються з самого reuse.
- Повний локальний `briefing/1`: БРИФ, ВІДНОВИ та stage closeout з актуальних `references/briefing-protocol.md`, domain guide/topics, intake/execution-script/closeout templates; якщо використовується controller — включити `scripts/briefing.py` й залежності. Topic guide адаптувати до предмета child, зберігаючи протокол. Resume звіряє actual files/hashes/authority/unknown effects; closeout зберігає доведений scope, outputs/evidence/limits, unresolved, checkpoint і next action/stop/return. Саме повернення не дає нового дозволу.

Для невеликої аналітичної навички ці пункти можуть бути кількома точними секціями; не вимагати HTTP, DB, server або custom validator без предметної причини. Для коду/інтеграції/реального deployment потрібні відповідні контракти й виконання, а не документ з назвою production.

## Перевірка успадкування

1. Звірити всі parent requirement IDs з child assignments; coverage має включати явно N/A лише з прийнятою предметною причиною. Немає інструмента → blocked.
2. Зіставити кожний child output із реальним consumer і acceptance. Якщо consumer мусить вигадати правило, scope ще не передано.
3. Перевірити загублені constraints у скороченому SKILL, metadata та family handoff. Посилання на parent без bundled content не є самодостатнім child skill.
4. Відкрити artifact у чистому контексті: сирий task, потрібні files, без діагнозу/очікуваної відповіді. Виконати bounded positive й negative сценарій без live mutation. Фактичні outputs зберегти окремо від reusable examples.
5. Якщо extension змінює material goal, budget, external effects або product choice, створити нову версію blueprint; не сфабрикувати approval. Доручене routine repair у чинному scope не запускає повторне погодження.
6. Перевірити self-contained discovery/reuse і `briefing/1` у чистому контексті: новий невідомий заздалегідь вузький спеціаліст, відсутня картка/counterpart, ambiguous/stale source, cold resume та завершення етапу. Потрібні content/scripts/templates мають локальні paths і manifest/hashes, без залежності від невстановленого sibling. Generic specialist отримує bounded project task/handoff; app/chatbot validator не видавати за універсальний.

Приймання child skill підтверджує конкретний assessed scope. Воно не гарантує компетентність на будь-якій невідомій задачі й не є сертифікацією продукту, який ця навичка колись створить.

## Успадкований процес взаємодії

Створюваний агент зберігає один чинний предметний реєстр, короткий огляд мети/перевіреного/поточної роботи/gaps/потрібного рішення й точне продовження. Власник приймає матеріальні рішення та результат етапу; routine work виконується за чинним scope. Погодження не перепитується через дочірній виклик; зміна відкриває причинно зачеплений обсяг. Формати приймання specification/code/integration/device/human розділені; terminal scope не потребує нового завдання. Читати чинний `references/interaction-protocol.md`; підтриманий read-only view може використовувати `scripts/interaction.py` і `assets/status-view.schema.json`. Для власного іншого domain state виготовити й перевірити його предметний adapter або еквівалентну проєкцію; недоступний generic adapter не називати виконаним. Другої authority/беклогу чи фонового сервісу ці файли не створюють.

Self-contained child включає застосовний protocol, `assets/decision-card.template.md`, tool-compatibility і фактичний helper/schema лише коли вони використовуються; зберегти versions/hashes і випробувати cold receiver. Умовні ресурси не нав'язують чужий предмет чи engine. Пакетний runtime/model/permission факт перевіряється на actual host. Source/structural PASS не замінює actual tool run, незалежну предметну перевірку або відповідь власника.

## Переносний загальний стандарт і візуальна сталість

Кожний новий child включає точні поточні локальні копії `references/adaptive-work.md`, `references/research-and-synthesis.md`, `references/visual-identity.md`, `references/joint-work-codex.md`, `scripts/adaptive_work.py`, `scripts/visual_identity.py`, `assets/adaptive-task.schema.json`, `assets/adaptive-task.example.json`. У точці входу посилатися на всі чотири references та застосовувати їх предметно. Власні domain/depth/workflows зберігаються. Перед збереженням виконати `scripts/check_generated_inheritance.py` конструктора для кожного child root, також у переносному output. Gate звіряє bytes/links, а семантичний coverage review сирих джерел і behavioral cases є окремим прийманням.

Успадкувати незалежну оцінку масштабу/невизначеності/наслідків/зв'язності, source reconciliation (must/питання/приклад/гіпотеза), видиму strategy/competence карту й late requirement due gates. Для довільної компетенції передати bounded task envelope; typed App/ChatBot routes — додаткові adapters. Використовувати callable research/synthesis/coverage методи з `research-and-synthesis.md`, коли вони потрібні, без обов'язкового нового сімейства або фіксованого штату.

Нові project agents мають class `project` і виразно відмінний стиль; іконку створити лише коли немає чинної. Чинні icon paths/bytes/brand_color не змінюються через випуск нової версії; нові project identities фіксуються за `visual-identity.md`. Legacy adoption звіряє фактичний стан і сумісність, зберігаючи чинні IDs, approvals й outputs; історичне виконання нового review не вигадується.

## Фіксація візуальної ідентичності child

Клас обирати за призначенням у чинному прийнятому scope, незалежно від місця встановлення. Лише предметно прив'язаний до певного проєкту агент одержує `class=project` і новий project-card-v1. Новий загальний reusable tool або системна компетенція має `class=system` та продовжує чинний системний стиль; project-local копія такого інструмента також може залишатися системною. Класифікація не дає глобальних прав і не потребує повторного погодження вже прийнятого завдання.

Для `class=system` в origin зафіксувати `scope=reusable_system` і `scope_basis={source,reason}` з фактичного accepted task. Це підстава класифікації, а не запис про дозвіл зовнішніх дій. Для нової системної іконки додати `style_reference={path,sha256}`: окремий фактичний зразок чинного системного стилю під `assets/`, включений у manifest. Перевірити реальну відповідність стилю предметним visual review; byte/link check не сертифікує художню якість. Project-card не можна перейменувати в newly-created system icon. Зразок не може бути самою щойно створеною іконкою.

Для наявної іконки зберегти точний prior snapshot, її попередній class, paths/bytes/brand color. `freeze --class system|project` має збігатися з цим class; origin `kind=preserved` pin-ить справжній prior snapshot. Для системної спеціалізації зберігається source basis reusable_system. Оновлення або project-local placement не є приводом для регенерації чи прихованого перепризначення class. Routine installer відхиляє зміну вже відомого class до явної фактичної міграції scope; це не вимога повторного людського погодження незміненого завдання. Збережений prior snapshot порівнюється разом із class, його не можна мовчки переписати для обходу нового стилю.

Для нової іконки проєктно-специфічного агента виконати `scripts/visual_identity.py create-project --root CHILD --glyph XX` лише за відсутності чинних refs/icon assets, потім прив'язати `interface.icon_small` і `icon_large` до returned path. Зберегти JSON фактичного `freeze --root CHILD --class project` у `assets/visual-identity.lock.json`. `assets/visual-identity-origin.json` має `{"schema":"visual-identity-origin/1","kind":"created"}`. Gate перевіряє actual SVG project-card-v1, project class і bytes, а читаність додатково оглядається.

Для наявної іконки її не генерувати й не перефарбовувати. Зберегти справжній prior freeze як локальний source artifact (наприклад `assets/visual-identity-prior.json`), зафіксувати його SHA-256; origin має `kind=preserved` і `prior_snapshot={path,sha256}`. Поточний lock мусить точно збігатися з prior snapshot. Дата/назва/поле preserved самі не доводять історичне походження: конструктор зберігає справжнє джерело спостереження в чинному project registry і перевіряє його в semantic review. Не видавати щойно створену системну іконку за стару для обходу окремого project style.
