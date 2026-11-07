# App Atelier: повна концепція і точна економіка

Зміст: результат → системи/шляхи → комерція → числа → виробнича здійсненність → рішення.

## Повнота кандидата
Читати `cross-domain-core.md` і `app-system-contract.md`; зберегти accepted direction/REQ-ID та джерела. Розрізняти sketch і завершену концепцію: кожний фіналіст для остаточного вибору має purpose/audience/trigger, core/edge/recovery/revisit journeys, повну applicability map, предметні сутності/стани/правила на рівні характеру, launch scope, паритет погоджених платформ, UX/brand/content direction, local state й optional sync, authority/permissions/privacy, support/ops, cost/commerce/acquisition, assumptions/ризики/probes/reject criteria. Дві картки екранів не підміняють продуктову систему.

Будувати причинний ланцюг: подія потреби→дія→правило→результат→підтверджений стан→наступне використання. Розкрити перехресні межі: offline і expiry; guest і покупка; data export і privacy; недоступний API і core; support і tenant isolation; тривалий service cost і one-time price. Предметно пояснити, які дані змінює кожна core-дія, хто authority й що станеться при відмові. Не вимагати в концепції всіх exact числових coefficients, але невідомий параметр має range/method/due, а не сховану зміну суті.

## Комерційна система за fit
Для доречних моделей описати offer catalogue/definitions, сумісність пакетів/лімітів, free/trial/paid journeys, повторювану користь і собівартість, restore/expiry/refund, account/platform scope. Визначити чому оплата виникає після зрозумілої користі, що людина отримує і як це працює після покупки. Не нав’язувати рекламу, підписку, штучне утримання, платний RNG або ігрові механіки. Умовні bundles/credits мають прозорі cumulative effects: дві покупки не продають двічі одне право, expiry не відбирає неправомірно власні дані.

Для взаємодій можливостей скласти catalogue/family rules: prerequisites, compatibility/exclusion, versions, quotas, consumer/platform, entitlement й failure. Перевірити повні сімейства запуску/правила варіацій, не лише два приклади. Розвиток продукту після launch — явна content/feature roadmap з операційною спроможністю й cost, не невичерпна обіцянка.

## Числова модель з oracle
Всі економічні inputs мають kind, source/date, одиниці/період/currency, range і залежність. Розділити gross revenue, refunds, commissions, contribution, fixed/variable/API/AI/support/growth cost, owner time/taxes за визначенням target. Порядок fees/refund/rounding уточнити для фактичного provider. Run check_model.py для арифметики дозволено; output не доводить попит чи майбутній прибуток. Не підвищувати protocol economics/1 через нову версію навички.

Три або більше обґрунтованих сценарії та sensitivity до weakest input. Залежності масштабу включають step-fixed capacity, quotas/overage, churn/cohorts, lag виплат і cash runway за застосовності. Не тримати acquisition cost чи one-time purchases сталими, коли це ламає висновок. Worked example фіксує проміжні значення, conversion/retention definitions, decimal precision і boundary zero/negative margin. Для probabilistic outcome розподіл/percentiles за потреби, не лише average. Дані зі схожого продукту лишаються analog estimate, а не actual metric нового.

## Реалістичне виробництво й операції
Назвати класи потрібних outcomes, можливі actual routes/tools, editable sources, platform adapters, доступи/ліцензії, recurring costs, probes й due validators. Генерація красивого UI не доводить clickable UX або реальний native client. Для ризикового differentiated feature підготувати bounded prototype/slice question з metric/threshold/horizon/cap/stop. До mass build довести representative complete path; не оголошувати запланований spike виконаним.

Операційна карта має тригери, runtime/schedule, bounded automatic action, unknown outcome reconciliation, escalation, monitoring costs, service-loss fallback/exit. Якщо профіль забороняє щоденну ручну працю, не називати людського менеджера AI-автоматизацією. Показати acquisition route з нульової аудиторії й constraints; дохід без досяжного каналу лишається pending hypothesis.

## Вибір
Незалежний критик перевіряє найсильнішу альтернативу/контраргумент, математичні припущення й must failures. Cold packet містить повний concept, alternative comparison, source/economic model, system applicability, catalog/journeys, production/ops/acquisition plan, unknowns, decision delta. Власник обирає продукт у чинному scope; подальші дрібні technical choices не вимагають повторного вибору. Не починати full build або spend із самого score.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: повна застосовна концепція, причинні користувацькі й комерційні шляхи, архітектура систем, виробнича здійсненність і порівняння альтернатив. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: цілісність досвіду, найсильніший контраргумент і припущення економіки. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
