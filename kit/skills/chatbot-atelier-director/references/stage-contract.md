# Контракт етапу chatbot-atelier-director

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати цілісну карту продукту, звірку наміру й повного обсягу, альтернативи архітектури рішення та окреме обґрунтування складу агентної роботи. Один інтегратор утримує контракти компонентів і майбутні due outputs; кількість skill-файлів не є доказом достатності.

## Обов’язковий предметний маршрут

## Вхід і аналіз до декомпозиції

Відновити задачу своїми словами: для кого бот, яку роботу полегшує, що люди роблять зараз, коли/де/як часто виникає потреба, наслідок помилки. Визначити platform/DM/group/workspace/topic/audience, роль/характер, мови/час, потрібні дії й дані, доступи, budget/latency/scale, наявний код/активи та completion. Відрізнити власну вимогу користувача від цитати/прикладу. Питати про вирішальне unknown, не проводити зайву анкету.

Побудувати applicability matrix і повну system/interaction map. На новому боті порівняти цілісні product concepts й архітектурні альтернативи за доказами: користь, повний journey, ціна/ризик, реальні можливості, support/операції. Не вибирати RAG/багатоагентність/монетизацію/ігри/голос без потреби. Для існуючого бота зробити impact map усіх24 інваріантів і чинних capabilities, потім адресний repair.

## Оркестрація по сімейству

Активувати research → specification, потім потрібні conversation/knowledge/integrations/media, build, QA, release, operations. Розмовний досвід проєктувати разом із виконанням, не після backend. Одна stage skill може виконати свій маршрут самостійно; директор передає самодостатній пакет із source IDs/hash, вимогами, точними доменними правилами, decisions, recipes, attempts/jobs/evidence, receiver/acceptance. Відсутній sibling skill не причина втратити required результат: потрібні загальні контракти включено локально.

## Виконання та приймання

Один root інтегрує, working leads й фахівці мають owned artifacts; independent QA/reviewer не є автором. Model/slot/cost limits беруться фактичні. Не запускати12 ролей за назвою12 критеріїв. Shared files/DB/resources мають одного mutable owner. Кожен stage вихід має cold receiver й upstream return condition.

Почати з одного повного platform event→permission/state→provider effect→outcome→delivery→recovery slice, перевірити всі його межі. Потім довести весь заявлений scope/catalog, не називати один slice повним продуктом. Перед обіцянкою великого обсягу виміряти виробництво одного репрезентативного елемента до інтегрованого QA. Кожен must має належний доказ, critical unknown не pass. Після двох безрезультатних повторів змінити гіпотезу й тест. Фінал містить exact scope/proof limits, current checkpoint і наступний виконуваний крок.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: human_value, practical_completion, version_continuity. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
