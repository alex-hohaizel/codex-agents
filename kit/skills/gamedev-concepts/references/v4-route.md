# Concepts: повний C1 у 4.0

## Maturity та охоплення

C0 — попередній ескіз для пошуку; явно показати невизначеність і не називати його готовою концепцією. Кожний кандидат, поданий як завершений для остаточного вибору, отримує C1. Повний TDD з усіма запусковими числовими рядами створюється для прийнятої до розробки гри на наступному етапі.

Для C1 пройти всі 20 напрямів моделі й позначити застосовність із rationale. Описати не тільки core loop, а й довгу арку, finite launch, повернення, завершення/вичерпання, повний player journey, інструментальну досяжність і cost drivers. Пряме динамічне керування Game of 2027 лишається чинною вимогою.

## Побудувати до зображення

1. Визначити fantasy/дію/основні рішення, production scale, topology, camera/input grammar, art language та commerce fit незалежними осями. Новий портфель не будувати випадковим декартовим добутком.
2. Задати повну архітектуру сімейств предметів/дій/навичок/техніки: роль, властивості, умови, сумісність, розвиток, acquisition, counterplay, representation і opportunity. Два-три приклади не видавати за всю систему.
3. Спроєктувати світ як authored macro→mission/progression→space→encounter→persistent consequences. Генерацію застосовувати за fit; authored сцени допустимі. Визначити constraints, failure repair/fallback і семантичну новизну.
4. Для AI розділити Actor/Knowledge/Action/Decision/Encounter/Boss; видимий cue, доступні відповіді, пам’ять і канали знання. Поведінкова фаза змінює рішення або має конкретну драматичну мету.
5. Для ризику визначити damage/contact-to-outcome architecture, living/downed/disabled/dead/retry лише за fit; ціну помилки, що втрачається/зберігається, recovery й anti-softlock. Не нав’язувати HP, смерть або бій небойовій грі.
6. Прокласти mastery/run/permanent/world progression, reward→meaningful use і capability×opportunity. Дати early/mid/late/exhaustion scenarios, а не фіктивну нескінченність seed.
7. Розділити intent/action/input/presentation. Порівняти доречні профілі на first/peak/late tasks; camera size/рух і touch cues мають відповідати зображенню.
8. Показати commerce на рівні метасистем, partial ownership і cumulative portfolio. Детерміновані покупки default; earned RNG прозорий; paid RNG окреме рішення. Допустиму перевагу часу/можливостей/сили описати чесно й окремо визначити competition.
9. Вказати persistence policy кожного значущого класу стану, cloud/restore/account boundaries, public capability status та required future proof. Не обіцяти автоматичний cloud від самого store.
10. Для image/profile зафіксувати actual planned representation та production recipe. Raster target не означає rig/stems/3D-ready; оглянути кожний generated frame до показу.

## Пакет C1

| Зміст | Приймання |
|---|---|
| Concept document + canonical model | Усі активні системи, roles, rules/relationships, scope, lifecycle й confidence; linked IDs |
| Сімейства/варіативність | Простір можливостей, constraints, progression й корисні контексти; не довільна item quota |
| Scenario atlas | First/normal/peak/late/failure/retry/return/completion; конкретні рішення й наслідки |
| Creative/input/camera lock | Constructive style, framing/movement, sensory grammar, actual inspected originals/hash |
| Production/economy profile | Operations/rights/costs, models/risks, due native/human proof; не вже виконана інтеграція |
| Receiver handoff | Tech-design reviewer відтворює задум без історії чату й називає визначені/open decisions |

Відкриті T-level параметри мають предметний owner, межу/мету уточнення й due stage. Відсутній концептуальний механізм, необґрунтоване N/A або неописана довга арка блокують C1. Не можна позначити весь концепт C0, щоб показати неповний результат як готовий.

## Контрприклади

Зображення кнопок замість declared drag; master artoverview замість gameplay camera; три upgrade ±стат замість архітектури; ворог знає unseen input; новий платний комплект закриває всі слабкості попередніх; нова reward після останнього opportunity; replay seed не змінює рішення; смерть не має resume/retry semantics.

Після C1 selection не означає production approval. Передати exact accepted version/hash/decisions, sources, scenarios, feasibility reviews і чітку stop boundary. Для запиту «10 ігор по 3 екрани» кількість frames не знімає C1 з жодного завершеного кандидата.
