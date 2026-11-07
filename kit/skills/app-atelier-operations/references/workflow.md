# Довготривала робота продукту

## Runbook
Описати actual deployment/config/source/build, services/data/providers, account owners, health/cost/product signals, їхню свіжість, scheduler і cadence, contacts/канали без secrets, permitted containment, restore/rollback, release route, privacy/retention, open risks і exit. Числові SLA/limits визначаються продуктом; не вигадувати 24/7 coverage.

## Signals і decisions
Для сигналу зберегти source/time/subject, expected range, actual observation, confidence й limitations. Error rate, latency, cost, conversion/retention, support unresolved та прибуток не взаємозамінні. Показати когорти/період/вибірку там, де доступно; не робити causal висновок із кореляції. Невідомі account/data не вигадувати.

Рішення continue/pivot/stop мати до витрат/проходу: metric, threshold, horizon, cap, owner і дозволені дії. При недосягненні зберегти fail, проаналізувати джерела, запропонувати допустимий delta. Scope закриття й фінансові effects потребують достатньої чинної згоди.

## Recovery
Backup strategy визначає дані, частоту, retention, encryption/access, restore environment, прийнятну втрату й час відновлення, перевірку та costs. Провести actual restore; файл backup не доводить відновлюваності. Сумісність code/data rollback оцінити окремо, зовнішні effects звірити з провайдером. Delete/revoke tombstones або еквівалентний механізм не дозволяють повернути відкликане.

## Підтримка й нові знання
Support case має ID/status/diagnostics у дозволених межах. Aggregate повтори у технічні jobs, public known-issue KB оновлювати лише з перевіреної інформації. Приватні діалоги не публікувати. Lesson має scope/source/confidence/applicability/impact; generic skill змінюється окремим дозволеним upgrade, не тіньовим навчанням.

## Оновлення
Зміна provider price/license/policy, SDK, security issue чи продуктового intent відкриває залежні перевірки. Порівняти версії/джерела, зберегти прийняті originals, дані й unrelated files. Targeted tests після impact достатні, повний цикл не повторювати без причини. Фактичний deployment і operational observation різні.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: актуальна причинна карта сервісу, сигнали/свіжість, діагноз, достатній repair, recovery та залишковий ризик. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: актуальність спостережень, причина інциденту, належний runtime/restore proof й вплив на ціле. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
