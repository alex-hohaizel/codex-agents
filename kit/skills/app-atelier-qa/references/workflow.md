# Workflow незалежної перевірки

Зміст: план → тип доказу → агент → продукт → критичні області → finding/повтор.

## План і актуальність

Зафіксувати subject, scope, author, requested observer, source/artifact hashes та залежності.
Звірити current requirements/decisions/knowledge із фактичними файлами; summary лише допомагає знайти їх.
Визначити due must, майбутні докази й неперевірені припущення.
Перевірити available tools/hosts/accounts/device budget; не планувати недоступну дію як виконану.
Обрати найменшу достатню перевірку, що може спростувати суттєву обіцянку.
Скласти coverage matrix: ID, acceptance, negative case, method, artifact, actor, stage, outcome, limits.
Перед витратами/зовнішніми змінами звірити право; sandbox/local fixture обрати всюди, де цього досить.
Зберегти stop boundary; не продовжувати після досягнення погодженого результату.

## Типи доказу

| Метод | Що може засвідчити | Чого не засвідчує сам по собі |
|---|---|---|
| Schema/link/syntax | Структуру, формат, доступність локальних refs | Предметну якість і роботу продукту |
| Document review | Узгодженість вимог, плану, аргументів, scope | Фактичне виконання плану |
| Raw forward case | Поведінку агента на конкретних сирих входах | Довільну майбутню надійність |
| Code/unit/contract | Перевірені invariants у заданому контурі | Фізичний пристрій або live provider |
| Sandbox integration | Доступну перевірену інтеграцію в sandbox | Production entitlement або прибуток |
| Device/E2E | Спостережуваний сценарій у точному environment | Всі платформи/пристрої та зручність для людей |
| Provider/deploy read-back | Фактичний зовнішній стан у своєму scope | Безстрокову доступність чи ринковий успіх |

Позначати self-check/independent окремо від методу; метод не робить автора незалежним.
Hashes доводять тотожність bytes, а не волю користувача, користь, дохід чи факт невиконаної дії.

## Forward cases агента

Використати 44 contracted cases як стартове покриття, звіривши поточний suite/версію.
Призначити реального іншого виконавця, коли оцінюється авторський результат.
Дати виконавцю звичайний запит, потрібні raw artifacts і навичку без oracle, hints або попереднього діагнозу.
Не включати фразу «правильна відповідь повинна...» у task-local prompt.
Для різних cases ізолювати outputs, щоб наступний actor не успадкував підказку від попереднього.
Evaluator застосовує criteria до фактичного результату й tool effects; не оцінює лише формулювання.
При відсутньому independent actor чесно зберегти self-check і відкритий gate.
Не робити live витрат, customer data access або production mutations для доказу здібності.

## Product acceptance

Для кожного core journey сформувати begin/success/invalid/empty/cancel/interrupted/retry/recovery path.
Перевірити межі модулів: клієнт↔API, identity↔data, provider↔entitlement, KB↔support, code↔schema.
Додати realistic fixtures попередніх версій/пошкоджених/великих даних за ризиком.
Не обмежуватися happy path і не копіювати implementation branches як єдину специфікацію.
Для Android/iOS/web записати окремі build/platform/browser/device versions і доступні докази.
Пройти accepted design states, потрібні motion/feedback, keyboard/text/accessibility, offline/degraded behavior.
Задати relevant performance budgets до замірів, зберегти процедуру, samples і environment.
Недоступний representative physical proof має blocker/bridge, не підміну симулятором.
Не називати synthetic UI pass підтвердженням зрозумілості реальним людям.

## Критичні області

Auth/privacy: guest/A/B/tenant, IDOR-like identifiers, cache/history/attachments, logs/AI egress, revoke/delete/restore.
Billing: provider verification, restore, duplicate/out-of-order/delayed events, lifecycle, offline/reconciliation.
Support: public+personal matrix, challenge/revoke, webhook authenticity, group rejection, stale KB, injections, cap/outage.
Reliability: cancel/timeout/unknown, retry dedupe, kill/network loss, backup/restore, migration/rollback compatibility.
Automation: повторювані manual exceptions, підтримка/контент/модерація, реальні cost/monitoring dependencies.
Release: current store/account/testing/signing/cost prerequisites до full build і повторно перед submission.
Acquisition/economics: перевірні джерела, припущення, recurring costs та stop criteria без гарантії доходів.
Офіційні актуальні правила й SDK перевіряти за primary docs; не виводити їх із пам’яті або чужого кейсу.

## Finding і повторне приймання

Зберегти raw reproduction, observed property, violated requirement, subject hash, environment і impact.
Відрізняти reproduced defect, document inconsistency та untested concern.
Показати мінімальний достатній repair scope; автор сам реалізує, незалежний reviewer повторно перевіряє.
Після fix звірити bytes/dependencies й виконати failed case та affected regressions.
Не переносити green verdict на нові bytes без перевірки відповідного scope.
Для unknown external outcome спершу status reconciliation, не повторювати effect.
Закрити тільки доведені IDs; майбутній stage proof лишити pending з власником і due gate.
Завершити коротким scoped verdict, evidence refs, residual limits і exact next action.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: звірка сирих вимог, незалежні сценарії/оракули, прив’язані до ревізії findings і висновок для кожного due must. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: адекватність оракула й компетенції перевіряльника, відсутні вимоги та реальні межі доказу. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
