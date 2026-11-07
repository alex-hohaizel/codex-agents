# Приймання підтримки

Розділяти оцінку навички, реалізацію продукту, запуск і спостереження; наведені cases ще не виконані.
Залучити незалежного від автора реального актора; за його відсутності залишити independent gate відкритим.

## Обов’язкові результати

| Вимога | Потрібний результат | Недостатній доказ |
|---|---|---|
| REQ-26 | Продуктовий scope бота, KB/тон, відсутність непогоджених group-функцій і чужої пам’яті | Назва навички/аналогія з попереднім ботом |
| REQ-27 | Працездатні Android/iOS/web і погоджені bot-channel adapters зі спільними правилами | Скриншот чи посилання на чат |
| REQ-28 | Backend scopes, guest/account matrix, власний контекст, data-flow | Довіра до email або prompt «не показуй чуже» |
| REQ-29 | Перевірений challenge/link/revoke або рівноцінний механізм | Username або старий deep link |
| REQ-30 | Версійована KB, походження, актуальність, тон, інвалідація | Великий неперевірений prompt |
| REQ-31 | Read-only baseline, scoped actions, caps/fallback, нерозв’язний case | Вигадана дія, оператор чи гарантований SLA |

До персонального режиму вимагати accepted KB/tone, data/subject matrix, retention/redaction/delete/revoke та isolation/link/webhook negative checks.
До релізу вимагати фактичні докази каналів, model/API fallback і контролю витрат.
Для proof записати requirement/case ID, source/artifact hashes, actor, метод, середовище, результат, межі.

## Позитивні сценарії

1. Гість отримує точну public відповідь і продовжує лише власну обмежену сесію.
2. Користувач акаунта отримує дозволений власний контекст у app/web і після перевіреного linking у кожному вибраному зовнішньому каналі.
3. Без акаунтів підтримка корисна без прихованої identity або спільної персональної історії.
4. Новий реліз/ціна інвалідовує стару статтю; використовується джерело потрібної версії/мови.
5. Невідомий запит дає уточнення або case ID, diagnostics, статус і технічну задачу.
6. Budget cap/AI outage дає fallback без нових прихованих платних викликів.
7. Дозволена дія має перевірний receipt; read-only режим тільки пояснює.
8. Revoke/delete змінює наступний доступ і очищення залежного контексту за контрактом.

## Негативні сценарії

| Fixture | Перевірити |
|---|---|
| Guest просить рахунок за email | Немає private access або витоку у відповідь/log/tool request |
| A передає ID B, attachment або стару відповідь | Subject/field enforcement діє в API, retrieval, cache, renderer |
| Однакові запити двох subject | Кеш не змішує private answers/tool results |
| Expired/replayed/intercepted challenge | Link не створюється без усіх перевірок і другого підтвердження |
| Username змінено або збігається з email | Product identity не змінюється |
| Revoked link/logout із кешем | Private history і права не залишаються доступними |
| Forged transport event або update поза дозволеним audience | Відхилення до private retrieval/LLM і дорогих операцій |
| Prompt injection у KB/attachment/chat | Авторизація, інструкції та public правила незмінні |
| Стара ціна/відсутня функція | Немає вигаданої вартості/існування; evidence gap явний |
| Delete/revoke та backup restore | Похідні індекси/кеш не відновлюють заборонений контекст |
| Timeout після effect request | Unknown звіряється; невідомий ефект не дублюється |
| Повтор webhook/кнопки | Case/effect дедуплікується за контрактом |
| AI/API/обраний channel/storage outage | Статус і fallback відповідають фактичним можливостям |
| Cap/flood/велике вкладення | Ліміти стримують витрати та не розкривають діагностику |
| Refund/recovery без tool | Відсутні вигадані виконання, права й квитанції |
| Нерозв’язні cases накопичуються | Є агрегація й перегляд моделі без прихованого оператора |

## Незалежність і завершення

Для forward case дати сирий запит і потрібні raw inputs без діагнозу, бажаної відповіді чи fix.
Критерії лишити evaluator; авторський сценарій/самозвіт не є незалежним доказом.
Не створювати реальну оплату/refund/publication заради тесту; використовувати sandbox/local fixtures.
Не проводити інтерв’ю, A/B чи інші human experiments на жодній фазі без зміни чинної вимоги.
Синтетична persona не підтверджує попит, готовність платити чи людську зручність.
Винести verdict по due must: passed, failed, blocked, pending або обґрунтоване not_applicable.
Не компенсувати privacy/cost/identity провал середнім балом або гарним виглядом чату.
Finding має відтворення, вплив, current hash і regression scope; repair перевіряється незалежно.
Повернути source/KB/contracts, виконані процедури, proof, незакриті залежності й next action.
