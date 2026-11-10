# Чинна система: що робить кожний компонент

English source SHA-256: `3556e3fa5984124e52d26c22c8b3639cf4d6a6475c61e96aa61fcf3d59820af9`.

Каталог за фактичними джерелами описує commit [8951398b38a9610854823302ea612cb3844d52e6](https://github.com/alex-hohaizel/codex-agents/tree/8951398b38a9610854823302ea612cb3844d52e6), перевірений2026-11-10. Він пояснює, що існує, де розташовано й коли застосовується. Не випускає нового suite, нічого не встановлює й не засвідчує майбутніх результатів. [Повна англійська версія](CURRENT-SYSTEM.en.md). Обидва документи мають однакові component IDs та повні рівнозначні картки. Цей додаток доступний EN/UK; чинні загальні інструкції сімома мовами зберігають окреме покриття.

## Чотири шари системи

1. **Один вхід і відповідальний за результат.** Починайте з atelier-orchestrator, коли потрібна одна розмова. Опишіть бажаний результат звичайною мовою. Він може відповісти прямо, використати спеціаліста/проєктного агента, координувати директора, з’єднати частини або спрямувати погоджене створення/супровід. Новий агент для кожного запиту не потрібний.
2. **Багаторазові методики.**33-core suite містить два конструктори,11 стадій застосунків,11 стадій чатботів і9 стадій ігор. Директор координує продукт; спеціаліст виготовляє визначену частину. Прямі виклики зберігаються.
3. **Фактичне виконання.** AI host читає навичку й використовує реальні доступні tools. Локальні Python helpers перевіряють/фіксують/планують конкретні речі; вони не є автономною командою експертів. Optional Mac service після запуску й підключення забезпечує фактичне обмежене виконання Codex і конкретні control operations.
4. **Докази й відповідальність.** Native project sources залишаються authoritative. Source/tool/runtime observations, незалежний review та owner acceptance відокремлені. Installed file, назва ролі, screenshot, green schema або completed turn не замінюють їх усі разом.

Створений проєктний агент не є36-м core component. Він має власні source, version, requirements, identity й native state у проєкті продукту. Каталог не публікує private project agents, account entries або customer data. Vendor/system/plugin skills не входять до35 багаторазових джерел власника.

## Версії та практичний вхід

| Об’єкт | Версія бази | Значення |
|---|---|---|
|Repository edition|1.3.0|Редакція документації/distribution та інтеграції сервісу|
|33-core suite|6.0.0|Reusable sources конструкторів і App/ChatBot/Game|
|Optional orchestrator|1.1.0|Універсальний розмовний/panel вхід|
|Optional maintenance skill|1.0.0|Контракт супроводу repository|
|Local Agent Atelier|0.2.0|Особиста Mac workbench/runtime|
|Game native contracts|Model4 / handoff1 / runtime2|Незалежні формати продукту, а не suite versions|

У Codex явно обирайте фактично виявлену навичку через $atelier-orchestrator, $agent-foundry або інший stable name нижче. Automatic selection залежить від actual host та installed description. Перед делегуванням прочитайте фактичне джерело. Розділ R називає role configurations, а не $skill selectors.

Для чинного продукту відновіть checkpoint, requirements, decisions, accepted originals/persona, settings, незавершені/невідомі роботи й чинні повноваження. Використовуйте його перевіреного project agent. Після створення агента оркестратор має рекомендувати продовжувати через нього; наступні запити до оркестратора зберігають цю прив’язку. Створення й виконання продукту мають окремі scope. Простий запит не потребує паспорта чи команди; проєктування нового цільового агента потребує погодження точного паспорта конструктора.

**Приклад:** «Допоможи довести цей прототип до надійного продукту». Вхід оглядає фактичні source і прийняту поведінку, обирає потрібного директора/спеціалістів та закриває реальні production gaps. Придатні дизайн/код мають зберегтися. Справжня прогалина reusable agent може передаватися Foundry; зміна framework або створення агента не є типовим критерієм завершення.

## Як читати картку

Інструкції — метод, який чинний AI має виконати реальними tools. Structural helper перевіряє declared records/references/bytes. Local controller також керує конкретними native state transitions. Filesystem tool виконує обмежені package/install/source зміни. Service runtime після запуску виконує documented commands. Жоден окремо не доводить цілого кінцевого продукту.

Картка визначає trigger, input, output і evidence limits. Optional sources не входять до33-core updater. Logical groups можуть використовувати ті самі implementation files; каталог не стверджує існування75 окремих процесів.

## Терміни звичайною мовою

Стабільні технічні назви збережені, щоб ви могли знайти відповідні файли й квитанції. Вони означають:

| Термін у картках | Практичне значення |
|---|---|
|source / source pin|Фактичний вхідний матеріал/файл та зафіксована точна версія або хеш його вмісту|
|checkpoint / native state|Збережений поступ і власні головні записи проєкту замість переказу розмови|
|scope / authority|Конкретна дозволена зараз робота й дії з їхніми межами|
|passport / blueprint|Версійований опис того, що має робити агент/навичка, до погодження створення|
|contract / consumer / handoff|Що обіцяє компонент, хто фактично використовує його результат і який точний пакет передається|
|capsule|Обмежений пакет завдання з потрібними вимогами, входами, рішеннями й лімітами|
|master / derivative / lineage|Прийнятий оригінал, його адаптований результат і простежуваний зв’язок між ними|
|recipe / attempt / receipt|Відтворюваний метод, його фактичний запуск і спостережений запис того, що відбулося|
|render / playback / import|Фактичне відображення, відтворення або завантаження матеріалу в потрібне середовище|
|schema / structural PASS|Правильні заявлені формат, зв’язки або байти; це корисно, але не доводить змісту, смаку чи роботи вживу|
|runtime / provider / device proof|Спостережена поведінка запущеного коду, зовнішнього сервісу або конкретного фізичного пристрою|
|fixture / negative control|Вхідні дані перевірки та навмисно хибний випадок, який має бути відхилений|
|independent QA / owner acceptance|Перевірка іншим рецензентом і прийняття самим власником; це різні факти|
|installation / discovery / adoption|Запис керованих джерел, їх виявлення середовищем та фактичне застосування чинним проєктом|
|idempotency / reconciliation|Захист від повторної логічної дії та звірка невідомого результату перед повтором|
|model / dataset / features|Навчений або керований запитом компонент, версійовані дані та вхідні значення для рішення|
|tenancy / ACL / tombstone|Відокремлення користувачів/проєктів, правила доступу та позначка видалення, яку враховує подальша робота/відновлення|
|rollback|Належне повернення відомих попередніх джерел/стану; воно не скасовує зовнішніх дій автоматично|

## C ·33 основні багаторазові навички

### Конструктори

### C01 · agent-foundry · 6.0.0

Джерело: [kit/skills/agent-foundry/SKILL.md](../../../kit/skills/agent-foundry/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Спроєктувати й передати багаторазового спеціалізованого агента: його життєвий цикл, інструменти, пам’ять, команду та перевірки.
- **Коли потрібний / активація:** Пряме доручення створити/адаптувати агента або підтверджена прогалина, передана оркестратором. Створення цільового агента потребує погодження точної версії паспорта.
- **Вхід → результат:** Задум звичайною мовою, чинні джерела й обмеження → досліджена область, начерк M0, повний паспорт M1, передача M2 з успадкованими вимогами, джерелами й інструкцією запуску/повернення.
- **Докази й межі:** Конструктор, створений агент і його майбутній продукт — різні об’єкти. Structural/depth checks не доводять експертної якості, установлення, виконання чи деплою.

### C02 · design-specialist-skills · 6.0.0

Джерело: [kit/skills/design-specialist-skills/SKILL.md](../../../kit/skills/design-specialist-skills/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Створити вузьку багаторазову навичку або узгоджене сімейство з предметними відповідальними й успадкованими контрактами якості.
- **Коли потрібний / активація:** Доручення створити навичку/сімейство або погоджене дочірнє завдання Foundry; перед створенням прочитати Skill Creator й погодити точний blueprint.
- **Вхід → результат:** Задача, вимоги, компетенції й чинні tools → версійований skill.blueprint/2, самодостатні навички, UI metadata, references/helpers і перевірена передача.
- **Докази й межі:** Запис погодження blueprint не автентифікує згоду. Чинні tools не читають/конвертують кожний історичний формат; створити навичку не означає виконати її продукт.


### App Atelier · життєвий цикл застосунків

### C03 · app-atelier-director · 6.0.0

Джерело: [kit/skills/app-atelier-director/SKILL.md](../../../kit/skills/app-atelier-director/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Координувати повний цикл застосунку та зберігати одного власника продуктового стану.
- **Коли потрібний / активація:** Новий застосунок, продовження кількох стадій або міжкомпонентне рішення.
- **Вхід → результат:** Задум/чинний checkpoint → відповідальні за стадії, обмежені завдання, інтегровані докази й наступна дія.
- **Докази й межі:** Інструкції координації не запускають runtime застосунку й не доводять реліз.

### C04 · app-atelier-research · 6.0.0

Джерело: [kit/skills/app-atelier-research/SKILL.md](../../../kit/skills/app-atelier-research/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Знайти реальні потреби й обґрунтовані напрями; порівняти наявні альтернативи.
- **Коли потрібний / активація:** Пошук напряму, питання ринку або нестача предметних доказів.
- **Вхід → результат:** Аудиторія/ринки/ліміти → реєстр джерел і тверджень, альтернативи, карта потреб, shortlist, контраргументи й невідоме.
- **Докази й межі:** Публічні відгуки й синтетичні сценарії не доводять попит, наявність платників або причинні ринкові висновки.

### C05 · app-atelier-concepts · 6.0.0

Джерело: [kit/skills/app-atelier-concepts/SKILL.md](../../../kit/skills/app-atelier-concepts/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Перетворити дослідження на цілісні варіанти продукту з корисним core, комерційною моделлю та економікою експлуатації.
- **Коли потрібний / активація:** Досліджений напрям потребує порівняння та вибору власника.
- **Вхід → результат:** Потреба/альтернативи/обмеження → концепції, шляхи користувача, варіанти монетизації, unit economics, карта автоматизації/залежностей і матеріал для вибору.
- **Докази й межі:** Прогнози лишаються припущеннями. Вибір концепції не дозволяє автоматично build, кампанії, платні tools або публікацію.

### C06 · app-atelier-specification · 6.0.0

Джерело: [kit/skills/app-atelier-specification/SKILL.md](../../../kit/skills/app-atelier-specification/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Перетворити прийняту концепцію на придатні до реалізації продуктові й технічні контракти.
- **Коли потрібний / активація:** Власник обрав концепцію або чинна специфікація потребує обмеженої зміни.
- **Вхід → результат:** Прийнятий задум → PRD/TDD, сутності, контракти даних/auth/API/оплат/підтримки, платформні сценарії, оцінки, залежності й матриця приймання.
- **Докази й межі:** Повна специфікація не є робочим кодом, доступом до provider, здійсненним store-випуском або доведеною економікою.

### C07 · app-atelier-experience · 6.0.0

Джерело: [kit/skills/app-atelier-experience/SKILL.md](../../../kit/skills/app-atelier-experience/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Створити бренд, UX/UI, інтерактивний прототип та виробничі дизайн-матеріали застосунку.
- **Коли потрібний / активація:** Новий дизайн, ремонт стану/сценарію або виробнича передача прийнятого дизайну.
- **Вхід → результат:** Вимоги, фактичні референси й чинні masters → сценарії/стани, правила стилю/tokens, редаговані assets, прототип, представницький інтегрований зріз і передача.
- **Докази й межі:** Скриншот не доводить взаємодію; збіг кольорів не доводить ідентичність. Фактичний носій, доступність і native/device відповідність потребують окремих спостережень.

### C08 · app-atelier-build · 6.0.0

Джерело: [kit/skills/app-atelier-build/SKILL.md](../../../kit/skills/app-atelier-build/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Реалізувати прийнятий застосунок із пропорційною архітектурою, даними, доступом, оплатами й відновленням.
- **Коли потрібний / активація:** Є погоджений scope реалізації та фактичні source/toolchain.
- **Вхід → результат:** PRD/TDD, masters і чинний репозиторій → справжній наскрізний зріз, клієнти/backend, тести, відтворювані builds і пакет передачі.
- **Докази й межі:** Компіляція, simulator, фізичний пристрій і production — різні рівні доказу. Описані нижче суперечності платформ/досліджень у цій базі ще не усунені.

### C09 · app-atelier-support · 6.0.0

Джерело: [kit/skills/app-atelier-support/SKILL.md](../../../kit/skills/app-atelier-support/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Створити й супроводжувати допомогу продукту, базу підтримки та support bot з належними межами дій.
- **Коли потрібний / активація:** Продукт потребує проєктування, реалізації, інтеграції чи ремонту підтримки.
- **Вхід → результат:** Фактичні версії продукту, cases і вибрані канали → автентифіковане зв’язування каналів, scoped knowledge, сценарії/дії підтримки, ліміти витрат і відновлення.
- **Докази й межі:** Файли knowledge самі не запускають support service. Надані ім’я/email не є повноваженням; RAG застосовується за потреби, а не як обов’язковий стек.

### C10 · app-atelier-qa · 6.0.0

Джерело: [kit/skills/app-atelier-qa/SKILL.md](../../../kit/skills/app-atelier-qa/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Незалежно перевірити вимоги, поведінку агента та фактичний застосунок.
- **Коли потрібний / активація:** Заморожений матеріал/зміна досяг належного етапу приймання.
- **Вхід → результат:** Точні джерела, сирі cases, builds та автор → позитивні/негативні перевірки, findings, покриття, висновок у межах scope й передача ремонту.
- **Докази й межі:** Авторський self-check не є незалежним QA; schema PASS не доводить пристрій, ринковий попит або дозвіл на випуск.

### C11 · app-atelier-release · 6.0.0

Джерело: [kit/skills/app-atelier-release/SKILL.md](../../../kit/skills/app-atelier-release/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Підготувати й провести дозволений випуск застосунку, включно з ранньою перевіркою здійсненності.
- **Коли потрібний / активація:** Рання перевірка store/account або конкретний погоджений release candidate.
- **Вхід → результат:** Точні RC/source/assets, QA та права цілі → signing/store матеріали, план міграції/відкату, фактичні submission/readback квитанції й передача супроводу.
- **Докази й межі:** Надіслано, схвалено, доступно й спостережено — різні стани. Вибір навички сам не дозволяє нових витрат/публікації.

### C12 · app-atelier-growth · 6.0.0

Джерело: [kit/skills/app-atelier-growth/SKILL.md](../../../kit/skills/app-atelier-growth/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Спроєктувати й виконувати дозволене залучення з правдивим контентом, автоматизацією та вимірюваною економікою.
- **Коли потрібний / активація:** До значного build або для явно обмеженої післярелізної роботи з каналом/вимірюванням.
- **Вхід → результат:** Сегменти, користь продукту, бюджет і фактичний доступ до каналів → funnel, план каналів/контенту, jobs/caps автоматизації, дозволені activation receipts і спостереження.
- **Докази й межі:** План не є активною кампанією; публікація/outreach/витрати потребують чинного scope. Кореляція й оцінки не доводять uplift або майбутній CPA.

### C13 · app-atelier-operations · 6.0.0

Джерело: [kit/skills/app-atelier-operations/SKILL.md](../../../kit/skills/app-atelier-operations/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Супроводжувати чинний застосунок, розслідувати інциденти й керувати фактичними витратами та безперервністю.
- **Коли потрібний / активація:** Реальний інцидент, запит на супровід, дозволений моніторинг або зміна життєвого циклу.
- **Вхід → результат:** Чинні source/deploy, симптом, logs і повноваження → причинна діагностика, обмежений ремонт, виміряні метрики/витрати, restore/export/end-of-life кроки.
- **Докази й межі:** Старий status не доводить чинне здоров’я. Моніторинг працює лише через фактичний дозволений scheduler/runtime; відкат binary не скасовує дані чи provider effects.


### ChatBot Atelier · життєвий цикл чатботів

### C14 · chatbot-atelier-director · 6.0.0

Джерело: [kit/skills/chatbot-atelier-director/SKILL.md](../../../kit/skills/chatbot-atelier-director/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Координувати повний чатбот, зберігаючи його домен, persona й native state.
- **Коли потрібний / активація:** Задум чатбота, продовження або складена зміна.
- **Вхід → результат:** Задум/чинний checkpoint → застосовність систем, адаптивна команда, завдання стадій, інтегрований результат і продовження.
- **Докази й межі:** Звіт стадії не доводить live bot, природної розмови чи доставленої дії.

### C15 · chatbot-atelier-research · 6.0.0

Джерело: [kit/skills/chatbot-atelier-research/SKILL.md](../../../kit/skills/chatbot-atelier-research/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Дослідити потреби, механізми домену, платформи й здійсненні операції.
- **Коли потрібний / активація:** Нечіткий домен або нестача доказів/можливості.
- **Вхід → результат:** Аудиторія/чинний workflow/обмеження → JTBD, альтернативи, primary sources, паспорти операцій, прогалини й рекомендація.
- **Докази й межі:** Перелічений API/model не доводить callable/integrated route; research не дозволяє зовнішні дії.

### C16 · chatbot-atelier-specification · 6.0.0

Джерело: [kit/skills/chatbot-atelier-specification/SKILL.md](../../../kit/skills/chatbot-atelier-specification/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Визначити причинні правила й typed contracts стану, інструментів і доставки чатбота.
- **Коли потрібний / активація:** Прийнятий напрям потребує деталей реалізації або ремонту контракту.
- **Вхід → результат:** Вимоги й джерела домену → actors/scopes, одиниці/алгоритми, lifecycle guards, транзакції, memory/time/media контракти, vectors і приймання.
- **Докази й межі:** Специфікована поведінка не є виконанням. LLM outcomes зберігають невизначеність; exactly-once потребує доведеного обмеженого значення.

### C17 · chatbot-atelier-conversation · 6.0.0

Джерело: [kit/skills/chatbot-atelier-conversation/SKILL.md](../../../kit/skills/chatbot-atelier-conversation/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Спроєктувати природну розмову, persona, слухання, ініціативу й спільну взаємодію.
- **Коли потрібний / активація:** Нова розмовна політика або фактичний дефект діалогу.
- **Вхід → результат:** Фактичні намір/адресат/контекст і прийнята persona → правила розмови, змістовні кнопки, приклади, minimal pairs і multi-turn evaluation.
- **Докази й межі:** Розмовне твердження не замінює виконаного tool effect. LLM ratings не є людським доказом природності.

### C18 · chatbot-atelier-knowledge · 6.0.0

Джерело: [kit/skills/chatbot-atelier-knowledge/SKILL.md](../../../kit/skills/chatbot-atelier-knowledge/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Реалізувати scoped memory, джерела, retrieval та життєвий цикл виправлення/забуття/відновлення.
- **Коли потрібний / активація:** Боту потрібні тривалі знання або змінюється чинний memory/privacy маршрут.
- **Вхід → результат:** Джерела, ACL, мета й retention → memory/knowledge schemas, умовний RAG, retrieval/attribution перевірки, deletion lineage і restore limits.
- **Докази й межі:** Embeddings/summaries успадковують доступ до джерела. Tombstone не засвідчує миттєвого фізичного стирання кожного immutable backup.

### C19 · chatbot-atelier-integrations · 6.0.0

Джерело: [kit/skills/chatbot-atelier-integrations/SKILL.md](../../../kit/skills/chatbot-atelier-integrations/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** З’єднати platform events, інструменти, надійні jobs, групи й provider operations.
- **Коли потрібний / активація:** Потрібна фактична дія, callback, schedule, payment або зовнішня інтеграція.
- **Вхід → результат:** Actor/scope/spec і фактичний API → adapters, dedup/fence/retry, reconciliation невідомого outcome, schedules, receipts і failure tests.
- **Докази й межі:** Transport acknowledgement не є доменним успіхом або прочитанням людиною. Mocks не доводять provider delivery чи згоди групи.

### C20 · chatbot-atelier-media · 6.0.0

Джерело: [kit/skills/chatbot-atelier-media/SKILL.md](../../../kit/skills/chatbot-atelier-media/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Виготовити й інтегрувати зображення, рух персонажа, audio/music/voice та video.
- **Коли потрібний / активація:** Задача потребує нового/зміненого media artifact або ремонту доставки.
- **Вхід → результат:** Мета, прийняті originals, права й точна capability операції → recipes/attempts, редаговані sources, final files/manifest, playback/decode та integration/readback докази.
- **Докази й межі:** Source track, повний motion/audio playback і runtime membership — окремі факти. PNG або frame count не доводить rig, дію чи звук.

### C21 · chatbot-atelier-build · 6.0.0

Джерело: [kit/skills/chatbot-atelier-build/SKILL.md](../../../kit/skills/chatbot-atelier-build/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Реалізувати фактичний чатбот від source до дії та delivery/recovery.
- **Коли потрібний / активація:** Погоджений build/repair scope з фактичним repository і runtime context.
- **Вхід → результат:** Контракти/чинні source/toolchain → event→authorized state→effect→verified outcome→delivery зріз, production code, ізольовані тести й передача.
- **Докази й межі:** За замовчуванням немає обов’язкового Redis/vector/workflow стека. Mock boundaries й локальні тести не доводять live platform.

### C22 · chatbot-atelier-qa · 6.0.0

Джерело: [kit/skills/chatbot-atelier-qa/SKILL.md](../../../kit/skills/chatbot-atelier-qa/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Незалежно перевірити разом розмову, стан, пам’ять, дії, медіа й runtime.
- **Коли потрібний / активація:** Заморожена зміна/результат потребує належного приймання.
- **Вхід → результат:** Сирі cases, sources/config/assets та actors → negative/race/restart/privacy перевірки, вісім conversation strata, media checks і висновок у межах scope.
- **Докази й межі:** Високий conversation score не компенсує privacy/authority/false-success дефекти. Human, live і device gates потребують фактичного доступу.

### C23 · chatbot-atelier-release · 6.0.0

Джерело: [kit/skills/chatbot-atelier-release/SKILL.md](../../../kit/skills/chatbot-atelier-release/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Провести дозволений сумісний випуск бота з точними source/assets і межами відкату.
- **Коли потрібний / активація:** Підготовлений release/migration або дозволена publication operation.
- **Вхід → результат:** Заморожений RC, QA, міграції й повноваження цілі → rollout/stop/rollback, фактична deploy/publication identity, обмежений smoke/readback і передача супроводу.
- **Докази й межі:** Deployment, доставка повідомлення, media membership і людська задоволеність — різні факти; невідомі remote writes звіряються до retry.

### C24 · chatbot-atelier-operations · 6.0.0

Джерело: [kit/skills/chatbot-atelier-operations/SKILL.md](../../../kit/skills/chatbot-atelier-operations/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Ремонтувати й розвивати чинного бота без втрати його можливостей та ідентичності.
- **Коли потрібний / активація:** Інцидент, фактичний дефект, обмежене вдосконалення або запитаний операційний огляд.
- **Вхід → результат:** Чинні source/provider/checkpoint і симптом → причинний ремонт, retest за залежностями, cost/quality метрики, support/restore/export і наступна дія.
- **Докази й межі:** Немає уявного фонового моніторингу. Prompt/model/generator зміни інвалідують зачеплені докази, а незмінені можуть переноситися з обґрунтуванням.


### Game Atelier · життєвий цикл ігор

### C25 · gamedev-director · 6.0.0

Джерело: [kit/skills/gamedev-director/SKILL.md](../../../kit/skills/gamedev-director/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Координувати гру від studio/concept через дизайн, craft, нативну реалізацію, випуск і розвиток.
- **Коли потрібний / активація:** Задум гри, відновлення проєкту або міжсистемне рішення.
- **Вхід → результат:** Задум/чинна Game Model → застосовні домени, адаптивні компетенції, production graph, інтегроване приймання й наступна стадія.
- **Докази й межі:** Game Model4, handoff1 і runtime2 — окремі контракти. Інструкції директора й model validation не є playable game або доказом цікавості.

### C26 · gamedev-studio · 6.0.0

Джерело: [kit/skills/gamedev-studio/SKILL.md](../../../kit/skills/gamedev-studio/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Зберегти/створити ідентичність студії та підготувати законні masters, derivatives й операційну основу.
- **Коли потрібний / активація:** Початкова організація студії, продовження бренду, похідні assets або перевірка account-readiness.
- **Вхід → результат:** Прийняті originals/права й чинні accounts → style/master catalogue, точні derivatives, setup dependencies, людська інструкція й studio payload.
- **Докази й межі:** Прийнята назва, graphic master, legal entity і configured account — різні об’єкти. Redraw не є byte-identical прийнятим original.

### C27 · gamedev-concepts · 6.0.0

Джерело: [kit/skills/gamedev-concepts/SKILL.md](../../../kit/skills/gamedev-concepts/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Дослідити й порівняти цілісні концепції гри з причинною глибиною та здійсненним visual direction.
- **Коли потрібний / активація:** Новий пошук концепцій, ремонт або явна задача вибору власником.
- **Вхід → результат:** Задум/studio/profile → різні C0 начерки, повні C1 candidates, mechanics/world/progression/economics, camera/art production envelope і порівняння.
- **Докази й межі:** Кількість концепцій, recolors або багато механік не доводять різноманітності/глибини. Кадр концепції не є runtime, повним світом або production permission.

### C28 · gamedev-preproduction · 6.0.0

Джерело: [kit/skills/gamedev-preproduction/SKILL.md](../../../kit/skills/gamedev-preproduction/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Визначити повну придатну до реалізації гру й контракти source→runtime.
- **Коли потрібний / активація:** Прийнята концепція потребує GDD/TDD або правила потребують контрольованої зміни.
- **Вхід → результат:** Прийняті C1/model/studio → rules/state/units/oracles, camera/input/world/reward/commerce контракти, asset scope, план representative native slice і передача.
- **Докази й межі:** Simulation перевіряє названу гіпотезу, а не людське розуміння, sensory comfort, retention чи revenue. Жодний genre/economy/engine preset не є обов’язковим.

### C29 · gamedev-assets · 6.0.0

Джерело: [kit/skills/gamedev-assets/SKILL.md](../../../kit/skills/gamedev-assets/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Виготовити повний art, animation, UI, sound і haptics гри та інтегрувати їхніх фактичних consumers.
- **Коли потрібний / активація:** Прийняті model states і production assets потребують створення, ремонту чи інтеграції.
- **Вхід → результат:** Model IDs, точні референси, права й доступні операції → editable masters, 2D/vector/3D/rig/clips/VFX/UI/audio, exports/catalogue, actual assembly і modality evidence.
- **Докази й межі:** PNG generation не створює mesh/rig/physics автоматично. Source reopen/export/import, motion/listening і device haptics мають окремі proof gates.

### C30 · gamedev-build · 6.0.0

Джерело: [kit/skills/gamedev-build/SKILL.md](../../../kit/skills/gamedev-build/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Реалізувати нативні gameplay, systems, persistence та platform integration з прийнятої моделі.
- **Коли потрібний / активація:** Погоджений scope реалізації та перевірений engine/export/toolchain маршрут.
- **Вхід → результат:** Model/GDD/TDD, assets і фактичний project → native slice, finite launch scope, tests, save/recovery, actual build files і receipts.
- **Докази й межі:** APK, AAB, simulator app, archive та TestFlight availability — різні результати. Structural build receipts не доводять signing, thermal behavior, physical input або fun.

### C31 · gamedev-qa · 6.0.0

Джерело: [kit/skills/gamedev-qa/SKILL.md](../../../kit/skills/gamedev-qa/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Незалежно перевірити правила, досвід, craft і фактичну native implementation гри.
- **Коли потрібний / активація:** Настав названий design/slice/release gate.
- **Вхід → результат:** Заморожені model/source/build/assets і сирі scenarios → design-derived positives/negatives, interactions, commerce/save/privacy tests, sensory/device/human межі й verdict.
- **Докази й межі:** Schema/byte PASS не доводить balance, touch comfort або людську цікавість. Автор, незалежний QA та final judge — різні actors.

### C32 · gamedev-release · 6.0.0

Джерело: [kit/skills/gamedev-release/SKILL.md](../../../kit/skills/gamedev-release/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Підготувати й виконати дозволений native game release за чинними platform rules.
- **Коли потрібний / активація:** Рання release feasibility або конкретний frozen release candidate.
- **Вхід → результат:** Точні binaries/config/content/QA, target accounts і права → compliance snapshot, store/privacy/commerce матеріали, controlled rollout, receipts і recovery handoff.
- **Докази й межі:** Upload, review, approval, tester availability і live release відрізняються. Store rollback може потребувати forward fix; SDK/account/device prerequisites залишаються фактичними.

### C33 · gamedev-liveops · 6.0.0

Джерело: [kit/skills/gamedev-liveops/SKILL.md](../../../kit/skills/gamedev-liveops/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Супроводжувати й розвивати released/beta гру за спостереженими player і runtime evidence.
- **Коли потрібний / активація:** Інцидент, проблема player experience, дозволене вимірювання або обмежений розвиток.
- **Вхід → результат:** Фактичні build/store/config/economy/save versions і спостереження → diagnostics, причинні repair proposals, retests, дозволені зміни, support і checkpoint.
- **Докази й межі:** Observational cohorts і simulations не є причинним доказом retention/LTV. Регулярна експлуатація й human research потребують чинного task scope.


## O · Дві optional багаторазові навички

### O01 · atelier-orchestrator · 1.1.0

Джерело: [optional-skills/atelier-orchestrator/SKILL.md](../../../optional-skills/atelier-orchestrator/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Надати один розмовний вхід, обрати достатній маршрут та інтегрувати первинний результат.
- **Коли потрібний / активація:** Явний виклик приймає будь-який запит; також продовження проєкту, кілька компонентів, портфель або супровід системи.
- **Вхід → результат:** Результат користувача й фактичні джерела → пряме виконання, specialist/director/project-agent reuse, композиція, погоджене створення/супровід або точний host bridge; optional loopback commands.
- **Докази й межі:** Не вимагає нового агента для кожного запиту, не замінює власника проєкту, не надає прав і не створює доступності панелі. check_routing.py перевіряє лише декларації.

### O02 · codex-agents-maintenance · 1.0.0

Джерело: [maintenance-skill/SKILL.md](../../../maintenance-skill/SKILL.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Узгоджувати дозволені зміни reusable system, документацію, міграцію, пакети й публікацію.
- **Коли потрібний / активація:** Створення/зміна/випуск агентної системи власника або відновлення незавершеної публікації.
- **Вхід → результат:** Фактичні repository/source diff і чинна policy → version/impact рішення, сумісні update/adoption/rollback інструкції, рівнозначні docs і перевірений distribution/publication record.
- **Докази й межі:** Наявність у repository не є установленням; local commit/archive не є remote publication. Не надає нових витрат, product deployment, зміни visibility чи license.


## R · Дванадцять фактичних role profiles

Optional competence profiles, а не обов’язкова команда із дванадцяти. Parent доручає actual deliverables й owned files у межах реальних slots. Незалежний review потребує іншого actual actor. Shared role restrictions залишаються чинними. Лише foundry-cost фіксує модель; інші profiles не мають fixed override.

### R01 · foundry-architecture

Джерело: [agent-profiles/foundry-architecture.toml](../../../agent-profiles/foundry-architecture.toml). Тип: Конфігурація ролі subagent.

Архітектура й причинна модель

- **Призначення:** Порівнює2–3 здійсненні архітектури; визначає межі модулів, ERD, API/events, concurrency, idempotency, recovery, resources і rollout. Обирає найпростіший достатній наскрізний зріз.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R02 · foundry-backend

Джерело: [agent-profiles/foundry-backend.toml](../../../agent-profiles/foundry-backend.toml). Тип: Конфігурація ролі subagent.

Backend і дані

- **Призначення:** Реалізує лише доручені файли й перевірки; узгоджує власність стану, schema/migrations, idempotency, privacy lineage та errors.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R03 · foundry-conversation

Джерело: [agent-profiles/foundry-conversation.toml](../../../agent-profiles/foundry-conversation.toml). Тип: Конфігурація ролі subagent.

Розмова й характер

- **Призначення:** Проєктує доречну розмову, слухання, уточнення, ініціативу, гумор, згоду, tone, тимчасові побажання й людське оцінювання.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R04 · foundry-cost

Джерело: [agent-profiles/foundry-cost.toml](../../../agent-profiles/foundry-cost.toml). Тип: Конфігурація ролі subagent.

Вартість і продуктивність

- **Призначення:** Скорочує зайвий контекст, агентів, retries, media processing і дубльовані перевірки; вимірює реальні витрати без послаблення must.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** `gpt-6-luna` / `medium`

### R05 · foundry-integrations

Джерело: [agent-profiles/foundry-integrations.toml](../../../agent-profiles/foundry-integrations.toml). Тип: Конфігурація ролі subagent.

Інтеграції й контракти provider

- **Призначення:** Перевіряє provider API, auth scopes, failure modes, фактичні receipts, retries, quotas і cost. Не видає API stub за робочу інтеграцію.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R06 · foundry-judge

Джерело: [agent-profiles/foundry-judge.toml](../../../agent-profiles/foundry-judge.toml). Тип: Конфігурація ролі subagent.

Незалежний суддя доказів

- **Призначення:** Розділяє гіпотезу, code inspection, isolated test, integration, provider observation і human feedback. Відхиляє невідомі hard gates та вигадане завершення.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R07 · foundry-platform

Джерело: [agent-profiles/foundry-platform.toml](../../../agent-profiles/foundry-platform.toml). Тип: Конфігурація ролі subagent.

Платформа та її UX/API

- **Призначення:** Перевіряє callbacks/interactions, permissions, формат повідомлень, rate limits, transport receipts, ролі груп і поведінку пристрою.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R08 · foundry-privacy

Джерело: [agent-profiles/foundry-privacy.toml](../../../agent-profiles/foundry-privacy.toml). Тип: Конфігурація ролі subagent.

Безпека й приватність

- **Призначення:** Моделює загрози data scopes, consent, secrets, prompt injection, forget/revoke/restore, logging і cross-user leakage. Повертає exploit scenarios або чесні невідомі.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R09 · foundry-product

Джерело: [agent-profiles/foundry-product.toml](../../../agent-profiles/foundry-product.toml). Тип: Конфігурація ролі subagent.

Потреби й користь продукту

- **Призначення:** Визначає аудиторію, конкретну користь, JTBD, шляхи користувача, non-goals, success metrics, етичні межі та приймання; відсіює декоративні функції.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R10 · foundry-qa

Джерело: [agent-profiles/foundry-qa.toml](../../../agent-profiles/foundry-qa.toml). Тип: Конфігурація ролі subagent.

Незалежна якість

- **Призначення:** Незалежно перевіряє frozen contract/diff; готує positive/negative/race/stale/wrong-actor/duplicate/cancel/restart/privacy перевірки з фактичними доказами.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R11 · foundry-reliability

Джерело: [agent-profiles/foundry-reliability.toml](../../../agent-profiles/foundry-reliability.toml). Тип: Конфігурація ролі subagent.

Надійність і супровід

- **Призначення:** Проєктує bounded queues/retries, recovery/cancel/timeouts, health/metrics, backup/restore та безпечний випуск.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.

### R12 · foundry-skeptic

Джерело: [agent-profiles/foundry-skeptic.toml](../../../agent-profiles/foundry-skeptic.toml). Тип: Конфігурація ролі subagent.

Незалежний опонент

- **Призначення:** Шукає найсильніші контрприклади й альтернативні пояснення; перевіряє коректність, тягар для людини, приховану вартість і регресії.
- **Коли потрібний / активація:** Parent обирає цю компетенцію, коли потрібний її конкретний результат або незалежний review; підтриманий host має фактично запустити дорученого actor.
- **Вхід → результат:** Доручена сира задача, точні sources/contracts і належний scope → описаний вище предметний результат, negative scenarios, фактичні докази, невідоме й передача.
- **Докази й межі:** Role profile — інструкції, а не самостійна навичка, окрема sandbox, ліцензований експерт-людина або доказ проведеного review. Його інструкції забороняють secrets/private chats і production/publication/deployment/paid/irreversible external effects.
- **Налаштування моделі:** Успадковує модель і effort parent/host; фіксованого override немає.


## H · Helpers, controllers і shared contracts

Перед командою прочитайте actual --help. Relative scripts належать фактично прочитаному skill source. Logical groups нижче пояснюють controls; копії в self-contained skills не є додатковими capabilities або independent reviews. Fixtures — тести, а не виконана робота користувача.

### H01 · Foundry native controller

Джерело: [kit/skills/agent-foundry/scripts/foundry.py](../../../kit/skills/agent-foundry/scripts/foundry.py). Тип: Виконуваний локальний state controller/checks.

- **Призначення:** Керувати локальними предметами погодження, покриттям і workflow state.
- **Коли потрібний / активація:** Підтримана native operation; спочатку прочитати actual --help.
- **Вхід → результат:** Чинна session і точний record → перевірений local state/receipt з native locks і gates.
- **Докази й межі:** Не виконує model або external executor; збережене погодження потребує actual user authority.

### H02 · Packaging and project installation

Джерело: [kit/skills/agent-foundry/scripts/package_agent.py](../../../kit/skills/agent-foundry/scripts/package_agent.py), [kit/skills/agent-foundry/scripts/install_agent.py](../../../kit/skills/agent-foundry/scripts/install_agent.py). Тип: Виконуваний filesystem/package tool.

- **Призначення:** Пакувати створений agent content і встановлювати declared set в один проєкт.
- **Коли потрібний / активація:** Перевірена delivery/install задача з точними build gate і target.
- **Вхід → результат:** Створені source/manifest → delivery kit; перевірені kit/project → managed files/receipts.
- **Докази й межі:** Не генерує expert content, не реєструє, не upload/deploy і не мігрує product-state. Same-user ancestor replacement поза його security boundary.

### H03 · Core suite updater

Джерело: [kit/skills/agent-foundry/scripts/update_skill_suite.py](../../../kit/skills/agent-foundry/scripts/update_skill_suite.py). Тип: Виконуваний filesystem/package tool.

- **Призначення:** Аудитувати, планувати, застосовувати, перевіряти й відкочувати точний personal suite із33 core skills.
- **Коли потрібний / активація:** Перевірені install/update з actual ownership/journal і preservation checks.
- **Вхід → результат:** Candidate та installed tree → plan/diff, before-copy, managed update/verification або належний rollback.
- **Докази й межі:** Не керує optional sources, plugins, model defaults, AGENTS.md або product data. Файли не доводять host discovery.

### H04 · App ledger and checks

Джерело: [kit/skills/app-atelier-director/scripts/state.py](../../../kit/skills/app-atelier-director/scripts/state.py), [kit/skills/app-atelier-director/scripts/check_model.py](../../../kit/skills/app-atelier-director/scripts/check_model.py), [kit/skills/app-atelier-director/scripts/doctor.py](../../../kit/skills/app-atelier-director/scripts/doctor.py). Тип: Виконуваний локальний state controller/checks.

- **Призначення:** Фіксувати App requirements, decisions, work/effects, authority й evidence; перевіряти узгодженість.
- **Коли потрібний / активація:** Застосовна App native state/check operation і прийнятий profile.
- **Вхід → результат:** Profile/state і typed records → ledger, status/coverage та consistency findings.
- **Докази й межі:** Не виконує remote/model, UI rendering, support runtime і не доводить ринок.

### H05 · ChatBot round/team/domain checks

Джерело: [kit/skills/chatbot-atelier-director/scripts/teamctl.py](../../../kit/skills/chatbot-atelier-director/scripts/teamctl.py), [kit/skills/chatbot-atelier-director/scripts/team_policy.py](../../../kit/skills/chatbot-atelier-director/scripts/team_policy.py), [kit/skills/chatbot-atelier-director/scripts/check_round.py](../../../kit/skills/chatbot-atelier-director/scripts/check_round.py), [kit/skills/chatbot-atelier-director/scripts/check_chat_contract.py](../../../kit/skills/chatbot-atelier-director/scripts/check_chat_contract.py), [kit/skills/chatbot-atelier-director/scripts/check_platform_adapter.py](../../../kit/skills/chatbot-atelier-director/scripts/check_platform_adapter.py). Тип: Виконуваний structural helper.

- **Призначення:** Планувати/freeze-ити rounds і перевіряти declared bot/domain/platform records.
- **Коли потрібний / активація:** Gate, застосовний до чинних chatbot.round/1 та native contracts.
- **Вхід → результат:** Requirements, team plan, hashes і fixtures → structural errors/validity та frozen round metadata.
- **Докази й межі:** Не запускає ролі, не автентифікує згоду й не доводить natural conversation/provider delivery.

### H06 · Game state/model/production/build checks

Джерело: [kit/skills/gamedev-director/scripts/atelier.py](../../../kit/skills/gamedev-director/scripts/atelier.py), [kit/skills/gamedev-director/scripts/game_model.py](../../../kit/skills/gamedev-director/scripts/game_model.py), [kit/skills/gamedev-director/scripts/pipeline.py](../../../kit/skills/gamedev-director/scripts/pipeline.py), [kit/skills/gamedev-director/scripts/production_contract.py](../../../kit/skills/gamedev-director/scripts/production_contract.py), [kit/skills/gamedev-director/scripts/check_build_receipts.py](../../../kit/skills/gamedev-director/scripts/check_build_receipts.py), [kit/skills/gamedev-director/scripts/concept_gate.py](../../../kit/skills/gamedev-director/scripts/concept_gate.py). Тип: Виконуваний локальний state controller/checks.

- **Призначення:** Вести workflow/handoff і перевіряти model, production, concepts та exact build receipts.
- **Коли потрібний / активація:** Застосовний concept/slice/release gate; зберегти model4/handoff1/runtime2 і прочитати actual help.
- **Вхід → результат:** Model/state і linked files/receipts → consistency, coverage, impact та workflow records.
- **Докази й межі:** Не виконує engine, model/API generation і не засвідчує signing/device performance, fun або retention.

### H07 · Context and adaptive task helpers

Джерело: [kit/skills/agent-foundry/scripts/context_capsule.py](../../../kit/skills/agent-foundry/scripts/context_capsule.py), [kit/skills/agent-foundry/scripts/adaptive_work.py](../../../kit/skills/agent-foundry/scripts/adaptive_work.py), [kit/skills/agent-foundry/scripts/verify_depth.py](../../../kit/skills/agent-foundry/scripts/verify_depth.py). Тип: Виконуваний structural helper.

- **Призначення:** Компілювати declared task context і перевіряти dependency/depth/adaptive-work структуру.
- **Коли потрібний / активація:** Матеріальна пряма/делегована/відновлена робота; завантажувати лише застосовний profile.
- **Вхід → результат:** Native requirements/decisions/identity/authority та input pins → похідні capsule/checks для названого consumer.
- **Докази й межі:** Не створює дозволів, не замінює native truth, не виконує job і не сертифікує якість. Skill-local copies самодостатні.

### H08 · Briefing, status and identity helpers

Джерело: [kit/skills/agent-foundry/scripts/briefing.py](../../../kit/skills/agent-foundry/scripts/briefing.py), [kit/skills/agent-foundry/scripts/interaction.py](../../../kit/skills/agent-foundry/scripts/interaction.py), [kit/skills/agent-foundry/scripts/visual_identity.py](../../../kit/skills/agent-foundry/scripts/visual_identity.py). Тип: Виконуваний локальний state controller/checks.

- **Призначення:** Пов’язувати briefing/script/decision files, показувати recorded status і freeze/check icon identity.
- **Коли потрібний / активація:** Матеріальний бриф, питання status/продовження або оновлення зі збереженням identity.
- **Вхід → результат:** Точні records або existing icons → bound records, read-only views та identity checks; SVG створюється лише за відсутності.
- **Докази й межі:** Не проводить інтерв’ю/автентифікації згоди, не resume paused jobs, не засвідчує craft, не встановлює UI й не створює monitoring.

### H09 · Discovery, proposal, inheritance and routing checks

Джерело: [kit/skills/agent-foundry/scripts/discover_specialists.py](../../../kit/skills/agent-foundry/scripts/discover_specialists.py), [kit/skills/agent-foundry/scripts/check_generated_inheritance.py](../../../kit/skills/agent-foundry/scripts/check_generated_inheritance.py), [kit/skills/agent-foundry/scripts/check_component_handoff.py](../../../kit/skills/agent-foundry/scripts/check_component_handoff.py), [optional-skills/atelier-orchestrator/scripts/check_routing.py](../../../optional-skills/atelier-orchestrator/scripts/check_routing.py), [kit/skills/design-specialist-skills/scripts/blueprint.py](../../../kit/skills/design-specialist-skills/scripts/blueprint.py). Тип: Виконуваний structural helper.

- **Призначення:** Інвентаризувати specialist sources і перевіряти proposal/inheritance/handoff/routing records.
- **Коли потрібний / активація:** Source-backed reuse, створення, component handoff або матеріальний route.
- **Вхід → результат:** Source metadata, requirement IDs і точні blueprint/route → inventory та declared completeness/conflict findings.
- **Докази й межі:** Metadata match не доводить semantic competence, invocation, автентифікацію погодження або виконання.

### H10 · Shared production and tool contracts

Джерело: [standards/production-quality.md](../../../standards/production-quality.md), [standards/production-profiles.json](../../../standards/production-profiles.json), [standards/context-capsule.md](../../../standards/context-capsule.md), [kit/skills/agent-foundry/references/tool-compatibility.md](../../../kit/skills/agent-foundry/references/tool-compatibility.md), [kit/skills/gamedev-director/references/v4/production.md](../../../kit/skills/gamedev-director/references/v4/production.md), [kit/skills/chatbot-atelier-media/references/production-recipes.md](../../../kit/skills/chatbot-atelier-media/references/production-recipes.md). Тип: Інструкції, які виконує чинний AI host.

- **Призначення:** Зберігати references/masters та обирати предметні production, rights, transformation і acceptance для операції.
- **Коли потрібний / активація:** Будь-який material artifact; до batch обрати actual medium/consumer.
- **Вхід → результат:** Task/reference/medium/tool schema → representative slice, recipes, lineage, вимоги actual playback/import/assembly та окремі gates.
- **Докази й межі:** Контракти не є встановленими DCC/renderer/media models або доказом sensory quality; missing must capability — blocked, а не N/A.

### H11 · Repository materialization, packaging and validation

Джерело: [scripts/materialize_standards.py](../../../scripts/materialize_standards.py), [scripts/refresh_kit_manifest.py](../../../scripts/refresh_kit_manifest.py), [scripts/build_packages.py](../../../scripts/build_packages.py), [scripts/check_repository.py](../../../scripts/check_repository.py), [kit/verify_release.py](../../../kit/verify_release.py), [scripts/install_host_profile.py](../../../scripts/install_host_profile.py). Тип: Виконуваний filesystem/package tool.

- **Призначення:** Узгоджувати перевірені common copies, обчислювати manifests, будувати/перевіряти distribution та встановлювати selected host profile.
- **Коли потрібний / активація:** Обмежений repository release/check або явне встановлення host profile.
- **Вхід → результат:** Перевірені sources/requirements/identity baseline → materialized copies, hashes, archives/checks або managed host profile.
- **Докази й межі:** Integrity PASS не доводить remote publication, host discovery, незмінність продуктів або якість усіх майбутніх результатів.


## S · Agent Atelier0.2.0: local runtime і control

Групи описують виконувані workbench components, а не доводять запуск checkout. Вони використовують actual API та durable command model. Personal Mac release не є multi-user/team authorization service.

### S01 · Mac launcher and instance ownership · 0.2.0

Джерело: [apps/agent-atelier/launcher/atelier.mjs](../../../apps/agent-atelier/launcher/atelier.mjs), [apps/agent-atelier/launcher/Agent Atelier.command](../../../apps/agent-atelier/launcher/Agent%20Atelier.command), [apps/agent-atelier/server/instance.mjs](../../../apps/agent-atelier/server/instance.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Запускати/відкривати, перевіряти й зупиняти особистий loopback instance.
- **Коли потрібний / активація:** Після pinned dependency install/build: start, status, doctor або stop; optional --no-open/--port/--data-dir.
- **Вхід → результат:** Зібрані local sources і explicit instance directory → verified listener, одноразове60-second owner посилання, browser або conflict/status result.
- **Докази й межі:** Не вмикає login auto-start. Процеси того самого OS owner із доступом до credential перебувають у local trust boundary.

### S02 · HTTP API and owner session · 0.2.0

Джерело: [apps/agent-atelier/server/index.mjs](../../../apps/agent-atelier/server/index.mjs), [apps/agent-atelier/server/session.mjs](../../../apps/agent-atelier/server/session.mjs), [apps/agent-atelier/shared/API.md](../../../apps/agent-atelier/shared/API.md), [apps/agent-atelier/shared/contracts.mjs](../../../apps/agent-atelier/shared/contracts.mjs), [apps/agent-atelier/client/src/api.ts](../../../apps/agent-atelier/client/src/api.ts). Тип: Runtime/control локального сервісу.

- **Призначення:** Обслуговувати UI/API та автентифікувати локальні owner commands.
- **Коли потрібний / активація:** Launcher claim; підтримані /api/v1 reads або durable POST commands.
- **Вхід → результат:** Verified launch token → HttpOnly SameSite session/CSRF; точні command_id+input → durable response.
- **Докази й межі:** Static page/plain URL не надає control session. Немає external CORS; command receipt не доводить успіх тривалого job.

### S03 · Service-owned store and receipts · 0.2.0

Джерело: [apps/agent-atelier/server/store.mjs](../../../apps/agent-atelier/server/store.mjs), [apps/agent-atelier/server/utils.mjs](../../../apps/agent-atelier/server/utils.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Зберігати service projects, tasks, jobs, commands, evidence й порядок events.
- **Коли потрібний / активація:** Звичайні service operations і фактичні database migrations/transactions.
- **Вхід → результат:** Validated commands/native observations → service-owned SQLite records, monotonic events і durable receipts.
- **Докази й межі:** Ця database не є native product source of truth або private Codex database. Known redaction patterns не знаходять кожний довільний secret.

### S04 · Project preview, binding and source views · 0.2.0

Джерело: [apps/agent-atelier/server/projects.mjs](../../../apps/agent-atelier/server/projects.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Оглядати точний проєкт і надавати bounded source/context/identity/artifact/diff views.
- **Коли потрібний / активація:** project.preview → project.bind; explicit profile/source_refs і refresh.
- **Вхід → результат:** Перевірена тека й відомі native records → binding, revision pins, requirements/decisions/readiness, source hashes і safe media/diff views.
- **Докази й межі:** Немає Home scan або product migration. Unsupported schemas лишаються warnings; title/Markdown claims не є authenticated owner acceptance.

### S05 · Native Codex portfolio and work map · 0.2.0

Джерело: [apps/agent-atelier/server/portfolio.mjs](../../../apps/agent-atelier/server/portfolio.mjs), [apps/agent-atelier/server/codex.mjs](../../../apps/agent-atelier/server/codex.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Знаходити native work і групувати фактичні результати за canonical project, а не показувати лише назви чатів.
- **Коли потрібний / активація:** portfolio.refresh; on-demand project/work-group history і bounded pagination.
- **Вхід → результат:** Public read-only app-server history → active/archived project groups, source-backed turns/outcomes, goal/agent status, next-action proposals і coverage gaps.
- **Докази й межі:** Read transport забороняє mutation/model execution. Empty projects без threads невидимі; unavailable pages лишаються incomplete coverage. Discovery не дозволяє автоматично безпечне продовження чату.

### S06 · Universal route proposal · 0.2.0

Джерело: [apps/agent-atelier/server/routing.mjs](../../../apps/agent-atelier/server/routing.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Зберігати source-backed route proposal, тоді як actual orchestrator робить semantic choice.
- **Коли потрібний / активація:** task.route; universal_entry preparation з reviewed route pins.
- **Вхід → результат:** Objective, current project/agent sources і creation/maintenance scope → direct/specialist/project_agent/director/compose/create_agent/maintain_system/bridge proposal.
- **Докази й межі:** Route не є invocation або consent. Keyword classifier не видається за expert reasoning; ambiguous sources потребують вибору.

### S07 · Context, instructions and source snapshots · 0.2.0

Джерело: [apps/agent-atelier/server/context.mjs](../../../apps/agent-atelier/server/context.mjs), [apps/agent-atelier/server/instructions.mjs](../../../apps/agent-atelier/server/instructions.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Готувати точні governing instructions, native must/dependency closure й verified selected-skill snapshots.
- **Коли потрібний / активація:** task.prepare; current instruction/source rechecks до dispatch.
- **Вхід → результат:** Objective/acceptance/scope, native sources і до4 selected skills → bounded capsule з hashes, source set, aliases та capability constraints.
- **Докази й межі:** Changed pins або unsupported source loading спричиняють block/reprepare; snapshots — read grants, а не global installation або permission expansion.

### S08 · Codex execution adapter and permission profile · 0.2.0

Джерело: [apps/agent-atelier/server/codex.mjs](../../../apps/agent-atelier/server/codex.mjs), [apps/agent-atelier/server/permissions.mjs](../../../apps/agent-atelier/server/permissions.mjs), [apps/agent-atelier/server/environment.mjs](../../../apps/agent-atelier/server/environment.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Запускати обмежений actual model turn через supported public app-server з isolated executor state.
- **Коли потрібний / активація:** codex.connect/skills та explicit task.dispatch після перевірки supported existing ChatGPT access і exact task.
- **Вхід → результат:** Prepared task, verified skills і limits → actual thread/turn/tool requests, outputs і terminal/unknown receipts.
- **Докази й межі:** За замовчуванням заборонено ambient MCP/apps/shell network/web і unrelated/private roots. Explicit public-web read вужчий за довільні APIs. Custom providers/billing і unavailable tools потребують reviewed routes.

### S09 · Task/job lifecycle and chat handoff · 0.2.0

Джерело: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/shared/contracts.mjs](../../../apps/agent-atelier/shared/contracts.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Координувати prepare/dispatch/continue/pause/interrupt/reconcile та owner review із writer reservations.
- **Коли потрібний / активація:** Task/job commands; exact idle thread.preview/adopt для чинних чатів.
- **Вхід → результат:** Approved bounded task і source revision → correlated running/terminal/unknown states, outputs, durable events та owner review.
- **Докази й межі:** Interrupt очікує terminal evidence. Unknown outcome не replay-иться. Independent desktop writers не fenced; model completion/owner review не дорівнює product acceptance/independent QA.

### S10 · Source-pinned native Foundry operations · 0.2.0

Джерело: [apps/agent-atelier/server/controllers.mjs](../../../apps/agent-atelier/server/controllers.mjs), [apps/agent-atelier/server/foundry_cas.py](../../../apps/agent-atelier/server/foundry_cas.py). Тип: Runtime/control локального сервісу.

- **Призначення:** Попередньо оглядати й застосовувати fixed native controller catalog без broad model write permissions.
- **Коли потрібний / активація:** controller.preview/apply; receipt-specific reconcile після unknown outcomes.
- **Вхід → результат:** Exact trusted source closure, current state та input hashes → reviewed argv/authority subject, native locked validation/write і actual receipt.
- **Докази й межі:** Не виконує model/provider/deploy/product runtime. Reconciliation спостерігає state й revokes delayed invocation лише під reviewed lease; не replay і не сертифікує original result.

### S11 · Core skills discovery and update UI · 0.2.0

Джерело: [apps/agent-atelier/server/skills.mjs](../../../apps/agent-atelier/server/skills.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Оглядати canonical/installed/discovered sources і надавати native33-core updater operations.
- **Коли потрібний / активація:** skills audit/update-plan/diff/apply/verify/rollback; codex.skills refresh після installation.
- **Вхід → результат:** Exact candidate/installed source і journal → source/diff/plan, managed update receipts і verified rollback conditions.
- **Докази й межі:** Один global writer; unknown customization — conflict. Installed files і host discovery/use відокремлені; WORK не отримує implied control route.

### S12 · Optional-source maintenance · 0.2.0

Джерело: [apps/agent-atelier/server/optional_updates.mjs](../../../apps/agent-atelier/server/optional_updates.mjs). Тип: Runtime/control локального сервісу.

- **Призначення:** Керувати лише declared optional orchestrator і maintenance sources з full-tree preservation.
- **Коли потрібний / активація:** skills.optional-preview/apply/verify/rollback з exact preview/journal hashes.
- **Вхід → результат:** Known canonical source і exact installed predecessor → reviewed changes, owned staging/before-copy, apply/verify/qualified rollback.
- **Докази й межі:** Unknown local edits/icon/policy drift блокують overwrite. Unknown outcomes блокують shared-skill dispatch до reconciliation; installed files ще потребують discovery refresh.

### S13 · Service backup, restore and update boundary · 0.2.0

Джерело: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/server/store.mjs](../../../apps/agent-atelier/server/store.mjs), [apps/agent-atelier/README.md](../../../apps/agent-atelier/README.md). Тип: Runtime/control локального сервісу.

- **Призначення:** Створювати exact service backups і попередньо перевіряти controlled restore/update.
- **Коли потрібний / активація:** service.backup/restore-preview/restore на idle/reconciled boundary.
- **Вхід → результат:** Current service-owned records і approved backup digest → backup/restore receipts зі збереженням newer durable receipts та invalidation старої dispatch authority.
- **Докази й межі:** Не відновлює native project files/databases, external effects або independent chats. Restore перевіряється в isolated instance.

### S14 · Retention, forgetting and cleanup · 0.2.0

Джерело: [apps/agent-atelier/server/retention.mjs](../../../apps/agent-atelier/server/retention.mjs), [apps/agent-atelier/client/src/privacy.tsx](../../../apps/agent-atelier/client/src/privacy.tsx). Тип: Runtime/control локального сервісу.

- **Призначення:** Попередньо оглядати/застосовувати service-local retention і cleanup з tombstones та resumable file cleanup.
- **Коли потрібний / активація:** service.retention; cleanup-preview/apply/resume з current digest та idle/reconciled work.
- **Вхід → результат:** Reviewed policy або forget IDs → exact scope/counts, private cleanup receipt, logical invalidation і збережені recovery boundaries.
- **Докази й межі:** Немає обіцянки automatic TTL. Не видаляє native/provider data й не гарантує secure physical erasure; newest two retained backups захищені policy.

### S15 · Adaptive multilingual workbench · 0.2.0

Джерело: [apps/agent-atelier/client/src/App.tsx](../../../apps/agent-atelier/client/src/App.tsx), [apps/agent-atelier/client/src/views.tsx](../../../apps/agent-atelier/client/src/views.tsx), [apps/agent-atelier/client/src/dialogs.tsx](../../../apps/agent-atelier/client/src/dialogs.tsx), [apps/agent-atelier/client/src/profiles.ts](../../../apps/agent-atelier/client/src/profiles.ts), [apps/agent-atelier/client/src/i18n.ts](../../../apps/agent-atelier/client/src/i18n.ts), [apps/agent-atelier/client/src/app.css](../../../apps/agent-atelier/client/src/app.css), [apps/agent-atelier/client/src/demo.ts](../../../apps/agent-atelier/client/src/demo.ts). Тип: Runtime/control локального сервісу.

- **Призначення:** Показувати portfolio, task/source/diff/outcome panes, evidence, updates і recovery для selected project profile.
- **Коли потрібний / активація:** Відкрити live owner session; обрати мову й app/bot/game/agent/research/document/mixed/generic view.
- **Вхід → результат:** Actual API state → project/work navigation, inspection, reviewable commands і localized operational status.
- **Докази й межі:** Сім мов — existing runtime catalogs, а не доказ бездоганної linguistic/craft якості. ?demo=1 — fictional і не виконує real commands. Presentation profile не змінює native product state.

### S16 · Orchestrator loopback client · 0.2.0

Джерело: [optional-skills/atelier-orchestrator/scripts/atelier_client.py](../../../optional-skills/atelier-orchestrator/scripts/atelier_client.py). Тип: Runtime/control локального сервісу.

- **Призначення:** Дозволяти orchestration skill користуватися supported service operations із current host.
- **Коли потрібний / активація:** Прочитати --help, потім status/doctor; prepare/dispatch/interrupt лише для available instance і current scope.
- **Вхід → результат:** Fresh local session/CSRF і persisted command identity → bounded correlated HTTP command/status receipts.
- **Докази й межі:** Лише loopback; немає credential searching або implicit authority. За відсутності service продовжити supported native work або дати exact bridge.

### S17 · Reviewed diagnostic export · 0.2.0

Джерело: [apps/agent-atelier/server/application.mjs](../../../apps/agent-atelier/server/application.mjs), [apps/agent-atelier/shared/API.md](../../../apps/agent-atelier/shared/API.md). Тип: Runtime/control локального сервісу.

- **Призначення:** Готувати aggregate service diagnostic без передавання private project content.
- **Коли потрібний / активація:** service.diagnostic-preview, потім diagnostic-export із reviewed digest.
- **Вхід → результат:** Current aggregate counts/capabilities → reviewable sanitized JSON і approved private local export.
- **Докази й межі:** Не містить project paths, task text, account/chat IDs, source/output і credentials; export локальний, не external transmission і не universal secret detection.


## Чинні недоліки: збережені в базі, а не мовчки виправлені

Це висновки source inspection. Виправлення **запропоновані**, але не реалізуються цією документацією.

- **Конфлікт App platforms.** [build:61](../../../kit/skills/app-atelier-build/SKILL.md#L61) використовує accepted platform set; [build:118](../../../kit/skills/app-atelier-build/SKILL.md#L118) безумовно вимагає Android+iOS+web. [release:47](../../../kit/skills/app-atelier-release/SKILL.md#L47) і [qa:87](../../../kit/skills/app-atelier-qa/SKILL.md#L87) повторюють очікування трьох клієнтів. Пропозиція: послідовно виводити applicability із accepted profile; зберегти чинні three-client obligations.
- **Конфлікт App research.** [build:63](../../../kit/skills/app-atelier-build/SKILL.md#L63) дозволяє profile-authorized research; [build:120](../../../kit/skills/app-atelier-build/SKILL.md#L120) забороняє всі human tests/experiments. [research:55](../../../kit/skills/app-atelier-research/SKILL.md#L55) і [qa:109](../../../kit/skills/app-atelier-qa/SKILL.md#L109) уже застосовують profile conditions. Пропозиція: прибрати historical-profile leakage із generic rules зі збереженням кожного чинного restriction. Product use, owner review, passive observation і intentional recruited research — різні дії.
- **Declared та executed routes.** H01/H04/H05/H06 відокремлюють state/structural tools від external execution. Production methods змістовні, включно з Game3D/rig/audio recipes, але не є installed universal renderer/generator/device lab. Пропозиція: показувати observed availability конкретної операції й actual consumer proof зі збереженням наявних методик.
- **Специфіка носіїв.** [production-profiles.json:125](../../../standards/production-profiles.json#L125) об’єднує vector і3D. Game references уже деталізують mesh/rig/source/export/import; ChatBot media вже вимагає playback/freeze/readback. Пропозиція: повторно застосувати ці абстракції з окремими medium profiles та downstream checks без другої native product model.
- **Нові domain claims потребують cases.** Каталог не засвідчує вже переданий business predictor, LoRA training route, production collector або гру для кожної платформи. Чинні методики можуть вести реалізацію; кожний новий route потребує actual data/access/toolchain, representative end-to-end output, належних evaluation та operating evidence.

## Перша корисна задача в локальному сервісі

Із repository root, після вибору reviewed baseline і перевірки передумов:

```sh
cd apps/agent-atelier
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

Source baseline визначає Node>=24.22.2<27 і pinned lockfile; це compatibility metadata, а не вічна platform recommendation. На Mac зібраний launcher/Agent Atelier.command також відкриває workbench. Зупинка: node launcher/atelier.mjs stop. Login auto-start автоматично не вмикається. Зберігайте separate private service data directory й actual backups поза reusable repository.

Маршрут: refresh native portfolio → огляд exact project/work/goal provenance → preview і bind потрібної теки → objective та acceptance → огляд route/capsule/scope → explicit dispatch → огляд реальних outputs → scoped review/next action. Observed skill mention, verified installed source, host discovery, running turn і accepted result мають різні статуси. Inaccessible/empty history — incomplete discovery, а не доказ відсутності роботи.

Presentation profile проєкту змінює view, а не product truth. Source-only goals залишаються declared; accepted goals потребують matching observed native approval і pinned authority. Продовження чинного чату потребує exact identity/cwd, idle handoff і restorable context. Інакше використайте native chat або підготуйте fresh reviewed task. Панель не може fence unrelated desktop writer.

Дивіться [actual API payloads/limits](../../../apps/agent-atelier/shared/API.md) та [service operations](../../../apps/agent-atelier/README.md). Confirmed command не є blanket future spending/publication grant. WORK live audit/control лишається відкладеним до відновлення supported host access.

## Збереження та оновлення

Каталог змінює лише документацію: не змінюються native schema adoption, installed skills, model defaults, icons, bindings, accounts, products або running instances. Для реального update застосовуйте [adoption record1.3.0](../../../releases/migrations/repository-1.3.0.md). Зберігайте stable names, accepted originals/persona, UI settings, native state/IDs, requirements/decisions, permissions і unknown effects. Installation, generated-agent adoption, host discovery, execution та owner acceptance — окремі кроки. Належний rollback використовує actual unchanged-target before-copies/journals; source rollback не скасовує external effects.

## Перевірка й межі

[current-components.json](current-components.json) містить повний EN/UK текст карток, counts і SHA-256 source pins.35 назв зіставлено з33-core release list та двома declared optional sources;12 TOMLs і всі linked sources звірено з8951398. Групи охоплюють instructions, helpers/controllers і local runtime/control; деякі використовують ті самі implementation files.

Огляд спирався на actual entrypoints і relevant source/reference sections. Він не виконував кожний support file, live host/device/media/provider operation або private product. Historical [core6.0 evidence](../../../governance/RELEASE_6_VERIFICATION.json) і [repository1.3 evidence](../../../governance/UNIVERSAL_ENTRY_1_3_VERIFICATION.json) мають власний scope. Їхні counts не доводять new bytes, платформи, майбутню craft quality або current host health. Нові live proofs тут не вигадуються.
