# Приймання реалізації

Оцінювати кожний due must окремо. Розділяти code authored, build passed, device verified, independently reviewed і released.
Самоперевірка автора не є незалежною перевіркою.

## Вихід і докази

| Область | Прийнятний доказ |
|---|---|
| REQ-10 | Основний корисний сценарій фактично проходить у самостійних Android, iOS і web клієнтах |
| Accepted experience | Реальні screens/states/assets відповідають hashes/masters і погодженим відступам |
| Data/auth | Контракти, migrations, subject/field isolation, recovery та негативні перевірки |
| REQ-43 | Provider-backed права, lifecycle, restore/retries/refund/revoke за застосовності |
| Production route | Рання store/account/cost/testing feasibility; фактичні SDK/build/signing prerequisites |
| CI | Відтворювана збірка з точними конфігураціями, checks і artifact provenance |
| Пристрої | Environment/version/device, процедура, спостереження й межі; симулятор позначений симулятором |
| Передача | Source/build hashes, commands, results, known limits, exact next action |

Не приймати landing page за web client, Android результат за iOS proof або mock за live provider integration.
За відсутнього пристрою/SDK/signing підготувати конкретний launch/return bridge і залишити proof blocked.
Не вимагати реального платежу, production migration або публікації заради тесту.

## Наскрізні cases продукту

1. Новий стан → основна дія → коректний domain result → збереження → перезапуск → той самий дозволений результат.
2. Невалідний/порожній/надвеликий ввід дає зрозумілу помилку без часткового некоректного стану.
3. Interrupt/kill/background/network loss не створює дубль або безповоротну втрату вже підтверджених даних.
4. Повтор запиту після timeout звіряє стан; відомий transaction/effect не застосовується повторно.
5. User A/guest не бачить записи B через API IDs, кеш, файли, support history або deep link.
6. Logout/revoke/delete прибирає належні права/контекст і не відновлюється старим cache/backup без правила.
7. Обраний local/offline режим працює в межах обіцянки; unavailable функції повідомляються до хибного завершення.
8. App/schema upgrade з реалістичних попередніх даних зберігає invariants і має перевірний recovery.
9. Platform permissions denied/revoked, різні viewport/input і доступність не руйнують core.
10. External API unavailable/quota/cost cap дає погоджений degraded шлях без прихованої платної петлі.

## Billing/entitlement cases за моделлю

| Case | Перевірити |
|---|---|
| Provider sandbox успіх | Право надається після довіреної verification, а не UI success |
| Pending/aborted/failed checkout | Немає хибного paid доступу або втрати вже чинного права |
| Restore/reinstall/device switch | Повертаються саме заявлені належні права |
| Duplicate event/callback/webhook | Відсутній подвійний ефект/credit/продовження |
| Delayed/out-of-order event | Старе повідомлення не перекриває актуальний стан |
| Expiry/cancel/renewal failure | Строки й дозволи відповідають provider model; cancel не дорівнює негайному revoke |
| Refund/revoke | Потрібна зміна стану підтверджена authoritative route |
| Offline/recovery | Право й час повторної verification відповідають обіцянці та загрозам |
| Cross-client access | Android/iOS/web дають погоджені права без обіцянки непідтримуваної переносимості |
| Unknown outcome | Спершу reconciliation; повтор не дублює покупку або effect |
| Price/plan disclosure | Користувач бачить реальну вартість, період, ліміти й умови |
| Ads failure/cap/ad-free restore | Core не ламається; реклама позначена, ненав’язлива, paid ad-free відновлюється |

Не оголошувати всі branches N/A через відсутній доступ до provider. N/A потребує предметної причини обраної моделі.
Subscription не нав’язується разовому продукту; one-time purchase не фінансує невраховані безстрокові AI/API витрати.

## Регресія й завершення

Для bugfix відтворити raw failing case, зафіксувати причину, виправити та пройти affected regressions.
Не повторювати весь тестовий набір без нової причини, якщо локальні зміни й ризики вже закриті.
Не знижувати quality/coverage без рішення через короткий строк чи недоступний інструмент.
Не проводити людські тести/експерименти; owner review і synthetic personas не є доказом ринкового попиту.
Передати іншому реальному QA actor код/builds/raw logs та критерії, не підказаний verdict.
Зберегти фактичні commands, result/exit status, hashes, platform/env та залишкові risks у canonical state refs.
При failed/blocked due must передати точну залежність і наступний крок; не називати release готовим.
