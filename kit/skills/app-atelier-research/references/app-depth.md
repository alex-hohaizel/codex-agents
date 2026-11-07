# App Atelier: дослідження як предметна модель доказів

Зміст: intake → decomposition → порівняння → джерела → synthesis → передача.

## Визначити питання і межі
Після `cross-domain-core.md` і `app-system-contract.md` перетворити запит на research questions із decision impact: хто має потребу, коли, який наслідок, як нині вирішує, чому потрібен новий app, що має змінитися, хто платить, як досягається аудиторія, хто експлуатує. Розділити широку карту й поглиблення вже прийнятого напряму. Кожне питання має джерельний метод, cutoff/географію, owner, expected artifact, cap, критерій достатності та контрдоказ. Не шукати наперед лише докази улюбленої функції.

## Повна предметна декомпозиція
Побудувати taxonomy потреб/ситуацій/типів користувача/платника/частоти/перешкод/невдалих станів. Застосовні app-system tracks використовувати як контроль перехресних меж: дані, права, sync/offline, correctness, accessibility, канал, cost, support, exit. Не нав’язувати фінтех чи медичні критерії всім доменам. Для спеціалізованої сфери підняти її власні якісні первинні матеріали, стандарти й operational practices; запланувати предметну компетенцію, якщо наслідки помилки цього потребують. Інструмент/домен без доступного підтвердження лишити unknown.

Знайти direct alternatives та непрямі: OS feature, таблиці, месенджер, діючий процес, existing service, nothing. Порівняти однаковий job/end-to-end outcome, дані/експорт/перенесення, limitations, комерційну модель, crossplatform, adoption friction, операційні dependencies. «Не знайшов» має query log/межі й не означає «не існує». Скриншот не доводить доступність/якість runtime, pricing page — actual margin, review volume — TAM.

## Claim/evidence contract
Для substantive claim: ID; exact statement; fact/source-claim/observation/inference/calculation/hypothesis/unknown; source/URL; accessed_at; event/version date; geography/segment; quotation або власний paraphrase; evidence scope; limitation; freshness trigger; dependent decisions. Одне джерело/передруки не є незалежними спостереженнями. Відкривати оригінал і контекст, не приймати search snippet за перевірку. Технічний факт SDK перевірити actual docs/version; юридичний/платіжний — належними поточними первинними джерелами та окремими невідомостями.

Відокремити заявлену на сайті функцію від виконаної операції. Якщо є allowed read-only product access, зафіксувати platform/build/scenario/expected/observed. Не створювати акаунт, контакт, оплату або людський дослід у межах desk research. Синтетичні users/scenarios підтримують reasoning, але не підтверджують потребу людей чи willingness-to-pay.

## Синтез для рішення
Картка напряму: user job/trigger/current workaround→перевірена прогалина→потенційна користь app→цілісні core/edge/recovery scenarios→конкурентний exception→платіжна й acquisition hypotheses→операційна модель→applicability tracks→потрібні technical probes→найсильніший reject case. Для завершеної research shortlist кожна картка має порівнювану повноту; коротку ідею позначити sketch.

Must-фільтри перед weighted rank. Не підганяти кількість кандидатів слабкими. Відсутність доведеного попиту не маскувати сильним craft score; сформулювати вузький висновок, що справді підтримують джерела. Розбіжні дані показати з альтернативними поясненнями й material next question. Припинити пошук за визначеною достатністю/cap, а не нескінченними раундами без нових доказів.

## Передача й актуальність
Cold receiver отримує research plan/query log, opportunity map, source/claim ledger, comparison matrix, rejected branches, applicability/unknowns, decision packet і affected REQ-ID. Точні hashes/input versions реєструються в canonical state. Новий тариф/видалена функція/регуляторна зміна інвалідує залежні висновки й економіку, не переписує всю історію. Незалежний reviewer перевіряє матеріальні claims на оригіналах та найсильніший контраргумент. Structural coverage не є empirical validation.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: питання й джерельна карта, перевірні claims, альтернативи, контрдокази, невідомості та рішення, яке підтримує кожний висновок. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: достатність джерел, незалежність підтверджень і переносимість висновків у конкретний домен. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
