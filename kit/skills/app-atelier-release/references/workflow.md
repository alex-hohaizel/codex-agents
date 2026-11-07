# Релізний контракт

## Ранні виходи
Створити release-feasibility record: target clients/countries/distribution, official sources/date, actual account/tool/device readiness, one-time/monthly/variable costs, testing prerequisites, exact unknowns/owner/due gate. Невідомий акаунт не заважає широкому пошуку, але до full build конфлікт має бути видимим і власник вирішує залежний scope.

## Release packet
Вхід: accepted concept/design/budget, PRD/TDD, actual builds/web/backend/support, hashes, QA, privacy/data flow, conditional billing lifecycle, resources і authorization. Вихід: reproducible build/config/source, current checklist і source links, store metadata/media, signing/setup без secrets, migration/runbook, release plan/rollback і готові exact actions. Test placeholders або Android screenshot не замінюють iOS/core evidence.

Перевірити upgrade/restore на реалістичних версіях і даних; code rollback не обіцяє rollback зовнішньої транзакції чи несумісної міграції. Store/billing rules можуть залежати від країни, типу товару й акаунта; підтвердити актуальні первинні умови. Не фіксувати універсальну комісію або ціну з пам’яті.

## Effect protocol
Concrete target/parameters/current hashes -> capability check -> sufficient grant -> local pending -> actual call -> receipt -> read-back. Не дублювати unknown upload/payment/deploy. Provider idempotency за наявності, local ledger не гарантує remote exactly-once. Зміна artifacts/target/cost/permission до dispatch вимагає перевірки чинності scope.

## Корисний запуск
Показати окремо local build, device verified, submitted, approved, released, externally available, observed core action. Для web перевірити реальний URL/health/core; для stores стан і доступність; для support канали/auth/fallback. Неперевірені runtime/monitoring не оголошувати активними.

## Особистий bridge
Вказати точну причину, verified URL/working path, підготовлені файли/hashes, minimal owner action, очікуваний receipt і return validation. Не перекладати на власника весь setup. Не надавати фіктивного шляху або command flag.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: готовність точного артефакту, маршрут випуску, чинний effect scope, квитанції й фактична доступність. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: readiness окремо від дозволу, актуальні platform/account умови, migration/rollback і зовнішній read-back. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
