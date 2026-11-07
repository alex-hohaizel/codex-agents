# Контракт етапу chatbot-atelier-research

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати питання→джерела/контрдокази→невідомості→альтернативи→рекомендація→момент рішення. Дослідити будь-яку застосовну потребу, включно з новою областю поза каталогом сімейства; попередній фаворит не є підставою відкинути альтернативу.

## Обов’язковий предметний маршрут

## Розкласти проблему та область

Побудувати stakeholder/JTBD map, actors/audiences, current workflow, pain/frequency/criticality, доступність даних, регуляторні/професійні межі за сферою, channels і adoption barriers. Розглянути альтернативу без нового бота; визначити, де саме розмова/груповий контекст/notification дають перевагу. Не переносити companion persona у сервісну задачу без підстави.

Виділити області знань і компетенції: domain expert, platform, UX/мови, data/privacy, automation/reliability, media за потреби. Для кожного requirement: джерело/намір, priority, owner, acceptance/negative case, потрібний evidence type. Зберігати contradictions/unknowns; не перетворювати бажання на перевірений факт.

## Доказове дослідження

Почати з primary docs/досліджень/чинного коду; фіксувати URL/title/version/date/scope, exact claim і limitations. Перевірити platform transport/callback/permission/rate/delivery semantics, доступний SDK/tool, environment/cost/license, editable outputs, support/deprecation. Для domain-specific best practices визначити конкретний failure/потрібний результат, потім source і метод перевірки. Де документація розходиться з tool schema/actual operation — записати gap і обмежений probe.

Скласти паспорти операцій: catalogued/callable/executed/artifact_checked/integrated/live_observed. Потрібний недоступний доступ не N/A. Умовні RAG/voice/payments/games/social automation активувати тільки за наміром і даними. Платну/зовнішню дію не виконувати через сам research; allowed read-only probes провести за реальною можливістю.

## Вихід

Brief, sources/claim map, applicability, systems/actors, concrete journeys, alternatives із tradeoffs, capability gaps, costs як measured/estimated/unknown, risk/evidence plan і recommendation. Передати specification exact unresolved choices, не загальний список технологій. Research не оголошує попит/природність/ефективність доведеними без відповідних користувацьких даних.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: human_value, capability_truth, source_grounding. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
