# Продовження наявного бота

Маршрут: **ВІДНОВИ → фактичний стан → предметне анкетування → версійний сценарій → чинне погодження → виконання й докази**. Це розвиток чинного продукту через `chatbot-atelier-director`, без нового bootstrap і другого інтегратора.

## Достатній старт і команда ВІДНОВИ

Достатньо доступного репозиторію або актуальної копії source, бажаної наступної зміни й відомих обмежень. Прийняті рішення, checkpoint, media masters або незавершену задачу, яких немає в source, надати адресно; весь архів чатів не потрібний. Секрети й реальні приватні переписки не запитувати. Якщо доступний наявний продуктовий чат, використати його релевантні рішення, не приписуючи доступу до інших чатів.

Work: `@chatbot-atelier-director ВІДНОВИ`; Codex: `$chatbot-atelier-director ВІДНОВИ`. У Codex працювати з фактичним checkout; у Work — з доступним підключенням або current source/checkpoint. Locator сам по собі не доводить доступу. Якщо source недоступний, виконати незалежний доступний аналіз, позначити межу й підготувати exact передачу в придатне середовище, не вигадуючи code/live стан.

`ВІДНОВИ` відновлює точку продовження й готує перевірний сценарій. Саме це слово не дає нового права змінювати продукт, читати secrets, мігрувати дані, публікувати чи робити deployment. Уже чинне явне доручення на конкретні дії зберігає силу; не вимагати його повторного підтвердження.

## Відновити факти з актуальних джерел

1. Прочитати user intent/constraints/stop, чинні `AGENTS.md`, profile і прийняті проєктні рішення. Встановити repo identity, branch/HEAD SHA/tree, dirty/staged/unstaged changes, version та власників. Не робити reset/перезапис source і не починати нового бота поверх існуючого.
2. Знайти актуальні README/architecture/release notes, commands/dependencies, tests/CI, data/API/events, schema/migrations, jobs/queues, configured models/providers/tools, accepted assets/manifest. Назви файлів і виконувані команди брати з current source; історична назва відсутнього скрипту не є інструментом.
3. Відновити канали й adapter contracts, entrypoints, identity/persona/мови, audience, capabilities/promises, memory/privacy/forget, consent/authority, actions/groups/games, callbacks, scheduling/recovery та ресурси. Це перевірка inventory, а не наказ додати відсутні функції. Не підставляти платформу, стек, хост, модель, кількість активів чи тестів за замовчуванням.
4. Зіставити checkpoint/issue/останній результат з actual tree. Відокремити completed, unverified, reported defect, reproduced defect, hypothesis і нове побажання. Фактичний baseline checks/CI прив'язати до source і середовища; pre-existing failure не називати новою регресією. Виконувати лише доступні дозволені перевірки, не тестувати на production DB.
5. Deployed build/SHA/config/health і provider receipts перевіряти лише через реально доступні дозволені interfaces, із часом спостереження. Source, успішний build, deployment, delivery й людське приймання — окремі факти. Unknown deployment не блокує незалежний аналіз source і не дає release claim.
6. Зберегти pending jobs/locks/remote IDs, pinned owner/version, uncertain effects, cancel/expiry/retry/reconcile і вже виконані незалежні частини. Перед повторним submit з'ясувати actual status; не відновлювати ефект сліпо за старою нотаткою.

## Project-owned контекст і один інтегратор

`chatbot-atelier-director` інтегрує розвиток; потрібні conversation/knowledge/integrations/media/build/qa/release/operations виконують свої предметні етапи. Project authority походить із чинного доручення, проєктних `AGENTS.md`, рішень і контрактів, а не з окремої проєктної навички. Продовження не потребує встановлення чи виклику попереднього інтегратора.

Унікальні правила конкретного бота, незмінні requirement IDs, прийняті критерії якості/безпеки, capabilities, persona, asset approvals, rights/budget, source/runtime facts і next action зберігати в його поточних project documents/checkpoint. Використовувати наявні авторитетні записи замість другої істини. Загальний метод ChatBot Atelier не переписує прийняту ідентичність і не вбудовує правила конкретного продукту у свої defaults.

Зберегти всі чинні предметні вимоги, прийняті originals/masters, media lineage, дані, незалежні результати й незавершену роботу. Для 24 companion requirement IDs і project-specific criteria вести applicability/impact та `source → criterion/contract → owner → destination → evidence`. Unknown не є unchanged або pass. Виявлений конфлікт із новішим авторським рішенням оформити адресним рішенням про supersession, не мовчазним вилученням.

Не створювати двох координаторів або writers одного source/БД/runtime. Делегувати owned artifacts і незалежні reviews за реальними capabilities/slot/cost limits; reviewer не оцінює власну реалізацію як незалежну. Локальний ремонт не починати з повторного повного research.

## Предметне анкетування

Спочатку прочитати доступні джерела й назвати вже встановлені факти. Потім скласти коротку анкету лише про вирішальні прогалини: user value/бажаний результат, scope, незбережені рішення або прийняті активи, acceptance, справжні зовнішні targets/rights, budget/stop. Не питати відоме, не вимагати вибору внутрішніх registry/modes і не перетворювати простий запит на церемонію.

Кожне питання пов'язати з рішенням, на яке впливає відповідь. Безпечні оборотні припущення позначити явно; відсутню авторизацію чи матеріальний критерій приймання не вигадувати. Поки відповідь не надана, продовжувати незалежну доступну роботу. Відповіді доповнюють project-owned context; не перетворювати тимчасове побажання на постійний профіль.

## Версійний сценарій і чинне погодження

До залежного продуктового виконання підготувати конкретний reviewable сценарій із revision/ID, exact source/context hashes, user goal, before/after, scope/owned paths, affected requirements/contracts, ordered actions, потрібними capabilities/targets/permissions, cost/stop, expected outputs, positive/negative acceptance, checks/evidence limits, rollback і receiver/next action. Назви й команди мають існувати в поточному середовищі. Версія сценарію — запис виконання, не новий runtime або legacy format.

Зіставити сценарій із чинним явним approval: хто дозволив, яку дію/target/effect і за яких меж. За достатньої авторизації виконувати без повторного gate. Якщо доручено лише відновити/підготувати сценарій, або з'явився новий істотний target/effect/permission, спочатку завершити конкретний перевірний результат для owner review; запитати лише відсутнє рішення. Не називати draft затвердженим.

Перед виконанням звірити актуальність source/context/permissions. Зміна hashes або суттєвого scope потребує оновленого diff/сценарію та звірки approval; не продовжувати старий сценарій навмання. Уже прийняті незалежні результати з незмінними залежностями зберігати. Належний release/operations виконувати лише в дозволеному scope через фактичний host/provider; відновлення контексту й оновлення навичок не запускають auto-redeploy.

## Поточний checkpoint і Work/Codex

Сформувати поточний handoff за чинними protocols цього сімейства: exact source snapshot/dirty patch/hashes, intent/constraints, рішення й IDs, domain/adapter contracts, accepted masters/manifest, current checks/failed baseline, attempts/jobs/unknown outcomes, owned paths/locks, rights/cost cap/stop, сценарій і approval scope, receiver/next action/acceptance. Project context є джерелом конкретних фактів; встановлена навичка сама не доводить їх.

Не будувати reader або adapter для старих agent-output schemas. Потрібний людський намір із історичного документа відновити з авторитетних джерел у поточний запис; original не переписувати. Runtime/DB migration, якщо вона справді потрібна за current data contract, є окремою предметною зміною з власними доказами й дозволами.

Work може вести аналіз, UX/діалог, підготовку сценарію, роботу з наданими матеріалами/дозволеними connectors і приймання повернених результатів; за доступних executor/provider interfaces — виконувати відповідні дозволені дії. Codex самостійно проводить весь доручений цикл у checkout; Work не є передумовою. Автоматичного доступу між приватними чатами, локальним комп'ютером, каналом і production немає. Повернений пакет звірити з input hashes, owned scope і receiving acceptance.

## Приклад достатнього доручення

Work: `@chatbot-atelier-director ВІДНОВИ`; Codex: `$chatbot-atelier-director ВІДНОВИ`.

«Продовжуємо чинного бота з [точний locator/відкритий checkout/current source]. Наступна мета: [конкретна зміна]. Збережи всі чинні можливості, правила, дані, прийняті медіа й незавершені jobs. Віднови фактичний стан і baseline, постав лише вирішальні питання та підготуй версійний сценарій із exact inputs/outputs/acceptance. Чинні дозволи й обмеження: [scope]. Виконай уже дозволені конкретні дії; для відсутнього істотного рішення поверни готовий сценарій на перегляд. Зафіксуй current checkpoint, докази й unresolved».

Фінал відділяє prepared / locally_verified / independently_reviewed / deployed / observed_in_chat; людське приймання показує окремою віссю completion.assessments.human зі scope та належними actual evidence. Історичну мітку human_validated і первинні людські докази зберегти у project context, перевіривши актуальність; вона не створює автоматичного passed або нового completion.stage. Незалежний cold receiver має продовжити з current source, project-owned context і мети без історії приватного чату чи попереднього інтегратора. Структурна валідація handoff не доводить живість, actual effect або delivery.
