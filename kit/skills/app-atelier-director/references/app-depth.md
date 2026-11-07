# App Atelier: наскрізне керування продуктом

Зміст: intake → повнота → команда → виробнича карта → gates → відновлення.

## Intake без втрати наміру
Прочитати `cross-domain-core.md` і `app-system-contract.md`; відновити current profile/state, accepted originals, REQ-ID, scope/stop і фактичний доступ. Перекласти вільну мову на: хто/яку подію/який корисний результат; повторне використання; поточні альтернативи; якість/відхилені спрощення; launch scope; платформи/пристрої; дані/права/наслідки помилки; економіка/експлуатація; ресурси/строки; що власник повинен вирішити; критерій завершення. Спочатку знайти відповіді в наданих джерелах. Питати лише невідоме, яке змінює обіцянку, структуру, права, cost або acceptance; дозволені незалежні дії продовжувати. Припущення мають owner, impact і спосіб перевірки.

Відразу визначити режим: новий задум, повна концепція, уточнення, design/build, repair або agent update. Режим не породжує автоматично новий ринковий раунд чи зовнішню дію. Якщо користувач уже прийняв суттєві рішення, не реконструювати анкету і не повторювати підтвердження.

## Єдина карта повноти
Інстанціювати app-system template під проєкт як linked artifact. У кожного напряму є applicability/reason/owner/артефакт/acceptance/due proof. Зберегти один canonical profile/state. Замкнути вимогу через domain rule/state, UX/content, code/adapter, operation/recipe, test/oracle, exact assembly та release/ops. Ребро пояснює читання/зміну/наслідок, а не декларацію «все пов’язано». Відсутність edge інвалідовує висновок про повне покриття.

Для кожного вибору показати справжні альтернативи, must-фільтр, доказ, контраргумент і наслідки. Рейтинг не компенсує відсутній must. Кожна завершена концепція має повний причинний продукт, operational/acquisition/economic route та всі застосовні системи; ескіз назвати ескізом. Для вибраного продукту довести production handoff з точними fixtures/правилами, а потім actual representative slice. Не вимагати всіх production proofs до завершення concept gate.

## Працююча команда
Вивести компетенції з конкретного output: product/domain lead; requirements/math; UX/accessibility; client/native; API/data/security; commerce/support/growth; QA/perf; release/ops. Один specialist може закрити близькі артефакти; жодних штучних дев’ятнадцяти підкоманд за числом tracks. Лід виробляє рішення й інтегрує, а не переповідає звіти. Critical/material acceptance робить інший actual reviewer; фінальний verdict не приписувати тому, хто його не виконав. У делегуванні exact inputs/hashes, REQ-ID, paths/device/account ownership, consumer, acceptance, budget і stop. Shared state/effects пишуться послідовно. Якщо незалежного актора немає, self-check лишається self-check і потрібний незалежний gate pending.

## Виробнича досяжність
Перелічити потрібні класи операцій від первинного дослідження/концепт-картинки до редагованих UI/assets, code/data/native integration, QA, signing/release, підтримки й завершення сервісу. Для кожної — реальна capability/schema/consumption proof, recipe, transformation, attempt і assembly. Не обирати інструмент лише за брендом або словом AI. Відсутня операція має здійсненний fallback чи exact Work↔Codex bridge з inputs, expected outputs, hashes і read-back. Повернений пакет перевірити; remote claim не стає local evidence автоматично.

Почати з найризиковішого корисного сценарію на всіх declared clients, включно зі збереженням/recovery і умовними покупкою/sync/support. До масового виробництва зіставити прийнятий reference, source, реальний UI/поведінку й performance. Доказ спроможності — виконаний повний шлях одного representative елемента, а не кількість згенерованих файлів. Estimate враховує інтеграцію/repair/QA/rights та фактичну пропускну здатність.

## Gate і зміни
Gate-пакет: due must + exact output hash + proper evidence + reviewer + gaps + чинне рішення. `verify_depth.py` перевіряє структуру linked depth artifact; state.py зберігає ledger. Жоден не оцінює якість/попит і не запускає продукт. За зміни input/schema/tool/permission інвалідувати транзитивно залежні докази, зберігаючи історію та незмінні originals. Scope repair не запускає повторно весь pipeline.

Resume звіряє current profile/files/hashes і unresolved remote outcomes до retry. Checkpoint містить завершене/поточне/blocked, jobs/effects/cost reservation, lease/resources, exact next action і stop. Продукт після релізу чекає наступного доручення; постійний monitoring має actual runtime/schedule та окремий чинний scope.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: інтегрована карта вимог і залежностей, аргумент достатності команди, власні рішення інтегратора, приймання цілого й наступний валідний крок. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: повнота первинного наміру, достатність композиції, спільні контракти та якість кінцевого цілого. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
