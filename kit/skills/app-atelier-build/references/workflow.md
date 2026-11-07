# Виробничий workflow застосунку

Зміст: приймання → стек/межі → зріз → контракти → billing → платформи/CI → передача.

## Приймання завдання

Відновити поточні repo/files, approved intent, requirement IDs, design masters, resource cap і stop.
Зіставити current bytes/hash із попереднім review; новий input інвалідовує лише залежні докази.
Розкласти роботу на tasks із owned paths, входами, interfaces, output, DoD і перевіркою.
Паралелити незалежні зміни; shared schema/state/міграції та інтеграцію виконувати послідовно.
Worktree ізолює файли, а не спільну production БД або provider account.
До повного build отримати early release/account/store/testing/cost feasibility; повторити його перед випуском.
Відсутній доступ не прирівнювати до готовності або незастосовності.
Не починати нові витрати/публікації/міграції поза чинним scope.

## Стек і межі

Скласти коротку матрицю: use case, platform capability, offline, data lifecycle, latency/cost, maintainability.
Порівняти достатні маршрути; обирати не за модою або попереднім ігровим проєктом.
Залишити матеріальний вибір власнику; рутинні бібліотеки в погоджених межах обрати самостійно.
Перевірити чинні primary docs, ліцензії, цільові SDK і доступний toolchain.
Сервер додавати для потрібних shared/auth/integration функцій, не механічно для кожної утиліти.
Один бренд і продукт не вимагають передачі всіх локальних даних або одного runtime для всіх клієнтів.
Задати контракти помилок, cancellation, timeout, idempotency та compatibility до паралельного виконання.

## Репрезентативний зріз

Вибрати найбільш ризиковий реальний шлях, а не найлегший UI-екран.
Включити accepted assets/motion, domain result, persistence, recovery і потрібну external integration.
При платній моделі включити sandbox purchase/entitlement; support interface передбачити разом із правами.
Показати success, empty, loading, error, interrupted і resumed стани в цільових клієнтах.
Записати source commit/hash, build configuration, platform/device, процедуру й спостереження.
Перевірити відмінності клавіатури, touch/back navigation, permissions, resize/safe areas за застосовності.
Недоступну iOS/web/physical перевірку чесно залишити відкритою з bridge; Android success не закриває її.
Після підтвердженого зрізу масштабувати; scope/fidelity компроміс приймати адресно.

## Domain, дані та інтеграції

Сформулювати domain invariants незалежно від UI та provider response.
Перевіряти вхідні типи/розміри/формати й auth на межі, не розкидати правила між екранами.
Визначити data ownership, retention/delete/export, encryption/keys і дозволені recipients.
Для local/cloud порівняти користь і вартість; узгодити конфлікти, sync retry, recovery та offline limits.
Будувати migrations як сумісні переходи; перевірити backup і restore до небезпечного застосування.
Зовнішній API обмежити deadline, retry policy, quota, cost cap та поведінкою при зміні/недоступності.
Не повторювати effect після timeout без reconciliation; застосувати provider idempotency за наявності.
Обмежити зовнішні файли/URL/команди, secrets та права згідно з реальною поверхнею атаки.
Виключити customer records і секрети з screenshots/logs/CI artifacts/skills.
Підтримку інтегрувати typed allowlist API; account context надає backend, не довільний запит моделі.

## Billing і entitlement за застосовності

Визначити модель окремо для storefront/платформи, recurring value, free path і розрахунок собівартості.
Спроєктувати entitlement як перевірний предметний стан із provenance provider event/receipt.
Визначити trusted verification layer; accountless/local продукт не перетворювати мовчки на account/backend продукт.
Зафіксувати permitted account/device/platform переносимість та route restore до рекламування цих властивостей.
Не відкривати paid feature через сам client success callback або повернення на success URL.
Задати stable event/transaction identities, deduplication, verification, reconciliation та audit без зайвих даних.
Розділяти checkout, payment state, entitlement state і UI; timeout не є доведеною невдачею платежу.
Визначити active, pending, expiry, renewal failure, grace/hold за provider model, cancel, refund/revoke.
Порівнювати авторитетний стан/періоди; старі чи переставлені notifications не відновлюють відкликане право.
Обробити restore/reinstall/device switch, повтор callbacks, webhook replay та offline expiry/recovery.
Не забирати вже оплачений період через скасування наступного поновлення без відповідної підстави.
Перевірити upgrades/downgrades та plan changes лише якщо вони входять у модель.
Для ads визначити placement, disclosure, cap, dismiss/failure, ad-free restore і недопустимі критичні переривання.
Rewarded unlock має підтверджений сигнал за доступним SDK; відмова реклами не ламає основний шлях.
Перевірити official provider sandbox; недоступний sandbox — blocker відповідного proof, не simulated success.
Для відсутніх покупок/ads обґрунтувати N/A за вимогою, не нав’язуючи зайвої монетизації.

## Клієнти, CI і докази

Реалізувати complete core у Android, iOS, web: вхід, корисний результат, збереження, повернення, помилки.
Дотримати accepted design masters; не завершувати з placeholder, якщо він не погоджений як final.
Перевірити доступність, text resize, focus/keyboard, контраст, reduced motion за обраними сценаріями.
Підтримувані OS/browser/device/offline режими обґрунтувати; не обіцяти максимальне покриття без доказів.
Налаштувати lockfiles, clean build, lint/static checks, meaningful tests і reproducible artifact generation.
Зберігати signing/production secrets поза repo/chat/ZIP; build без signing не називати store-ready.
У CI ізолювати test/prod конфігурації, не під’єднувати live оплату заради smoke test.
Виміряти ключові сценарії, memory/startup/latency/network size за продуктово потрібними budgets.
Додати recovery з kill/background/network loss і app/schema upgrade.
Автоматичні перевірки не замінюють відсутній actual device proof або ринкові факти.
Передати незалежному QA raw artifacts/commands/proofs і невідомості без бажаного висновку.
Повернути source, builds, contracts, migrations/runbook, actual results, current hashes та відкриті gates.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: працюючий погоджений зріз або зміна, рішення щодо технологій за фактичними обмеженнями, точний diff/build і належні перевірки. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: цілісність інтеграції, коректність і ризик змін, відповідність accepted design/spec. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
