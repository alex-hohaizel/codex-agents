# Перевірка конструктора та створених агентів

Зміст: рівні → план → незалежність → cases → closure → випуск.

## Рівні перевірки

Розрізняти semantic domain adequacy, machine structure, implementation behavior, host delivery/discovery, actual target execution і operational outcome. Blueprint schema доводить поля/references/покриття, не повноту предметного аналізу. Skill installation доводить розміщення файлів, не правильне implicit routing. Unit fixture не є реальним користувацьким, інструментальним чи production доказом.

Кожна ключова вимога має позитивний сценарій, strongest objection/negative case, потрібний тип фактичного доказу, scope, строк перевірки й обмеження. Метод виводити з властивості: спостереження взаємодії, виконуваний результат, перевірений матеріал, вимір, provider read-back, source-based analysis або їх поєднання. Не вводити універсальний score, що дозволяє компенсувати провал must іншими перевагами.

## План до створення

У погоджуваний паспорт включити test matrix capability→requirements→phase→test→evidence→owner/independence. Вибіркові audits доповнюють, не замінюють coverage всіх due must. Дорогі перевірки робити після дешевих deterministic checks, коли вони знімають реальний ризик. Перед масштабуванням перевірити найризиковіший наскрізний шлях за предметною потребою.

Технічний план: parse metadata/schema; local links/contained paths; exact skill/entry set; protocol/version/hash consistency; API/CLI actually runnable; safe input/state recovery; import/resource limits; package ZIP inventory; permissions/secrets boundaries; установка в існуючий проект; hash verification після звичайного використання; ідемпотентне повторення. Не виконувати live mutations, платежі, масові генерації або створення акаунтів лише заради validation.

## Справжня незалежність

На складний результат призначити реального reviewer, який не є автором. Передати raw request, потрібні inputs і produced artifacts; для первинного forward test не передавати очікувану відповідь, підозрювану помилку або готову інтерпретацію. Diagnostic retest після finding може мати точний repro, але це інший вид перевірки.

Ролі мають actual actor IDs, owned paths, resource cap, expected output і stop. Не представляти кілька голосів одного повідомлення незалежною командою. За недоступності subagents — чесний self-check та pending independent review або точний людський bridge. Final reviewer не переіменовується з автора. Обсяг QA пропорційний впливу; privacy/money/authority/data migration/external release потребують незалежності за своїм ризиком.

## Обов’язкові класи негативних випадків

1. Неповний намір: з’являються пояснені предметні питання, не мовчазно вибраний напрям або preset.
2. Немає target blueprint approval, відповідь негативна або hash/revision/scope змінились: залежне створення заблоковане.
3. Одна skill із кількома фазами та сімейство з іншою кількістю фаз обидва коректні; role/phase/skill counts не зчеплені.
4. Невідома/cyclic dependency, пропущена capability→artifact→test ланка або failing due must не маскуються score чи N/A.
5. Явний user emphasis не зникає при новому запиті; нове знання відкриває відповідні результати й докази.
6. Змінений output/proof/source/hash або відкликана authority роблять залежне closure/job нечинним.
7. Self-observation не закриває independent-review gate; fabricated role не створює фактичного reviewer.
8. Pause now не скидається future-stop, переформульованим prompt або новим task; resume не повторює завершену дію.
9. Blueprint approval не є execution grant чи effect authorization; decline не дозволяє effect, unknown outcome вимагає read-only reconciliation.
10. Інтеграція, SDK, хост, документ чи tool із плану не називаються фактично доступними без перевірки; missing capability не стає N/A.
11. Нове встановлення/оновлення зберігає unrelated files/AGENTS/modes/state; dirty/unmanaged collisions, links/special files та unsafe paths відхиляються.
12. Звичайне використання не створює непередбачених змін у встановлених immutable skill files; trusted code bytes не підміняє stale bytecode cache.
13. Вхідний текст не розширює повноваження; project knowledge не переноситься до чужого проекту; revoke/delete/restore не оживляють заборонений зміст.
14. Повнота доставки перевіряється окремо від виробництва; archive prepared, installed, discovered, exercised, running та observed мають фактичні підтвердження.

## Ремонт і closure

Зберегти finding, repro, severity, input/output hashes і impact. Автор усуває причину; reviewer повторює зачеплений scope, включно з transitive dependencies. Не переписувати старий fail як pass: додати current retest/version. Два однакові безрезультатні цикли означають зміну діагностики або конкретний blocker. Не повторювати весь етап через незначущий diff, але не звужувати невідомий impact без доказу.

Поведінковий forward case оцінює зміст: правильність відновленої мети, потрібних уточнень, структури області, повноти компетенцій, етапів/команди й реального next action. Гладка відповідь або збіг keywords не є оцінкою такої якості. Для критичних якостей потрібна предметна людська/інструментальна калібровка, коли AI critique недостатня.

## Перед доставкою

Повторно звірити затверджений склад, current hashes, approvals, tests і межі. Надати фактичні outputs, статус перевірок, gaps/owners, user guide, launch/return і support instructions. Створений агент не звітує готовий кінцевий результат до його окремого виконання; запущений результат не звітує довготривалу якість без потрібного періоду спостереження.

## Чинний контракт: виміряна глибина

Застосувати [depth-evaluation-2](depth-evaluation-2.md). Перевірити нові негативні cases: відсутній recipe/consumer/inherited domain contract; source proof замість operation/integration; stale subject hash; непідтриманий material parameter; помилка units/time/rounding; unresolved remote attempt; old-state restore після delete/revoke; неправильний host return. Cold receiver має відтворити дозволений сценарій без вигадування правила й без історії чату. Спільний `verify_depth.py` та `check_foundry_depth.py` мають різні scoped reports; жоден не сертифікує предметну якість.
