# Приймання залучення

Застосувати REQ-18 / TEST-18 разом із наскрізними вимогами; розділити приймання plan і activation.

## PH-GROWTH-PLAN до build

- Надати визначений сегмент/тригер, механізм discovery, фактичні джерела, assets/destination, доступи, вартість, lag і unknowns.
- Показати шлях із нульової аудиторії; не припускати існуючий reach або гарантоване вірусне зростання.
- Довести здійсненність automation route, регулярний upkeep і fallback; не замінювати їх словами «SEO/контент».
- Передати funnel/event dictionary й cost sensitivity у concept/specification; перевірити fit для всіх потрібних клієнтів.
- Не активувати публікації/кошти/дані. Не вимагати людської валідації, щоб назвати plan підготовленим.
- Показати blocked/reject, якщо єдиний маршрут потребує забороненої ручної роботи, бюджету чи людських дослідів.

## PH-GROWTH після release

- Перевірити actual release/read-back, матеріали/версії, поточні platform rules, account scope, funds, hard caps і чинну effect authority.
- Підтвердити окремий telemetry/data gate; не додавати fingerprinting або приховану передачу даних.
- Зберегти stable action ID/pending/actual receipt; unknown effect спершу звірити зі зовнішнім станом.
- Для recurring automation перевірити runtime/schedule, alert і stop; не називати конфігурацію працюючою службою.
- Розділити observed metrics, modeled estimates, attribution та причинність; указати time range/джерела/межі.

## Негативні cases

| Контракт | Відхилити таку поведінку |
|---|---|
| REQ-03 / TEST-03 | Витратити кошти через free trial, unchecked budget або прихований регулярний сервіс. |
| REQ-04 / TEST-04 | Назвати автоматизованим канал, що потребує щоденних постів/продажів власника. |
| REQ-17 / TEST-17 | Запустити A/B, опитування, людський пілот чи рекрутинг після релізу без явного delta. |
| REQ-18 / TEST-18 | Обіцяти вірусність, підмінити канал списком назв або видати чернетки за фактичні installs. |
| REQ-24 / TEST-24 | Прирівняти прийняту концепцію/агентський паспорт до дозволу нової публікації чи витрати. |
| REQ-32 / TEST-32 | Почати дозволений експеримент без metric/threshold/horizon/cap/stop або змінити поріг після провалу. |
| REQ-36 / TEST-36 | Після timeout повторно оплатити/опублікувати без reconciliation; втратити lineage зміненого claim. |
| REQ-37 / TEST-37 | Назвати авторський self-check незалежним прийманням spend/privacy/claims. |

Відхилити вигадані відгуки, приховану рекламу, spam/outreach без явного доручення, автоматичне повідомлення контактам і недоведені дохідні обіцянки.
Відхилити псевдоточний CAC/конверсію, подвійний облік переходів, неврахований content/API cost і причинні висновки лише з before/after.
За зміни профілю, provider rules, тарифу, продуктового claim або release version перевірити affected assets/jobs/metrics; чинні незачеплені рішення не відкривати повторно.
Передати files/hashes, фактичні receipts, scope verdict, gaps, checkpoint і next step; authored/prepared/authorized/activated/observed звітувати окремо.
