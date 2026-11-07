# Приймання концепції

Зв’язати outputs з current requirement IDs, inputs/sources і hashes; відокремити authored/self-check від незалежного висновку й owner acceptance.

| Контракт | Потрібний доказ у концепції | Негативний сценарій |
|---|---|---|
| REQ-02 / TEST-02 | Відтворювана модель потрібного масштабу для цілі профілю; сценарії, витрати, uncertainty й горизонт. | Назвати бажаний чи модельний прибуток гарантією; підмінити profit виручкою. |
| REQ-04 / TEST-04 | Операційна карта здійсненних автоматизованих залучення, сервісу й оновлень. | Покласти щоденні продажі, контент або ручну модерацію на власника. |
| REQ-09 / TEST-09 | Показати tool/cost/error/fallback для різних допустимих типів продукту. | Оголосити автомодерацію повною без негативних сценаріїв і маршруту невизначеності. |
| REQ-12 / TEST-12 | Для платної моделі визначити користь, момент, ціну-гіпотезу, собівартість, free/paid path і чутливість. | Приписати «subscription/ads» без причинного механізму. |
| REQ-13 / TEST-13 | Порівняти доречні free/trial/лімітовані/комбіновані варіанти з відкритими межами. | Нав’язати вічно безкоштовний весь core або прихований trial trap. |
| REQ-15 / TEST-15 | Для subscription назвати повторювану цінність кожного періоду та cost її виробництва. | Продавати разову функцію як регулярну послугу без обґрунтування. |
| REQ-42 / TEST-42 | Відсіяти must failures до score; дозволити reject/pending усіх кандидатів. | Обрати переможця попри порушення ресурсів/прав/ручної роботи. |

## Економічні негативні cases

- Не приймати модель із подвійним урахуванням покупок або комісій, повторним fill multiplier, безстроковим API cost за неврахованого одноразового доходу.
- Не ділити на нульову/від’ємну маржу, не змішувати monthly й annual periods, active users й installed base, cash надходження й сталий profit.
- Не приховувати free cohort cost, churn, mandatory store cost, payout delay або дефіцит коштів до виручки.
- Не приймати псевдоточні conversion/eCPM/retention без source або явного assumption; не вважати success іншого продукту власним доказом.
- Не видавати synthetic review за willingness-to-pay або довільний великий TAM за reachable customers.

## Наскрізні gates й вихід

Перевірити REQ-03 бюджет, REQ-08 competitive exception, REQ-17 all-phase human ban, REQ-24 owner choices, REQ-32 experiment thresholds, REQ-36 lineage і REQ-37 незалежний review.
Показати REQ-19 завершений core/чесний строк, REQ-20/34 реалістичний prototype/design brief, REQ-38 early release feasibility dependency.
Для REQ-43 передати billing/entitlement lifecycle requirements у specification/build; не назвати майбутні sandbox/client перевірки пройденими.
Прийняти комплект лише за наявності concept cards, inputs/sources/formulas, cost sensitivity, operations/acquisition briefs, reject log, prototype briefs і конкретного decision packet.
За зміни ціни, API, scope або конкурентного факту інвалідовувати залежні моделі/рекомендації й повторити лише зачеплені checks.
За cap залишити checkpoint, фактичні outputs, pending/unknowns і точний next step; не компенсувати брак доказів красивою презентацією.
