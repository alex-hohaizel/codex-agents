# Контракт етапу chatbot-atelier-build

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати обґрунтований вибір мови/framework/storage й компонентних меж, фактичний diff і наскрізний виконаний шлях, релевантні тести, точну ревізію та межу mocked/integrated/live. Погоджений дизайн, мови й інші пізні результати зберегти як окремі вимоги до їхнього due stage.

## Обов’язковий предметний маршрут

## Відновити проєкт і контракт

Current repo/branch/SHA/tree/diff, AGENTS, package/toolchains, environment selectors, schema/test/asset baseline. Не віддавати pseudocode/mock/feature flags як завершений продукт. Scope і applicable contract/operations мають конкретний receiver/acceptance. Збережені functions/actions/media/privacy не видаляти заради швидкої smooth demo.

Вибрати мову/framework/storage/SDK за предметною потребою, installed capabilities, primary docs і required quality. Використовувати релевантні language/security/data/testing skills, якщо доступні; їх назва не є quality proof. Порівняти ADR альтернативи за complexity/ownership/cost/portability/performance; не додавати queue/Redis/workflow/vector service автоматично. Boundaries/auth/data/architecture коректні без зайвої церемонії.

## Реальний slice й масштабування

Platform event→normalized scope→authorization→atomic state/dedup→provider effect→verified outcome→scoped delivery→recoverable checkpoint. UI/prompt/persona feedback походить із logical result; не чекає непотрібної remote роботи і не оголошує її завершеною. Typed schema/API/events/tests/doc/rollout узгодити.

Implement failure/cancel/expiry/retry/reconcile/restart/wrong actor/forget/version fences до масштабування feature catalog. Long media/jobs із resource bounds не блокують чат. Source→asset transform→export→runtime import зберігає semantic meaning/units/timing/audio/audience; один хороший файл не підтверджує весь набір. Functional provider integration proof має explicit actual vs mocked boundary.

## Перевірки та передача

До зміни baseline; після зміни build/static/type checks і meaningful targeted tests, integration/negative tests за ризиком, full regression за shared/critical scope. Tests мають перевіряти поведінку, а не повторювати код. Після passing required checks не повторювати їх без нової причини. Автор не незалежний QA; передати raw diff/artifact/commands/receipts/limitations.

Вихід: runnable code/source/assets/config examples без secrets, migrations, fixtures, tests/CI, operation attempts/receipts, integration evidence, current version/known gaps, recovery і cold handoff. Release permission не випливає з самого доручення писати код; уже явний exact deploy scope не запитувати повторно.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: practical_completion, execution_truth, bounded_resources, lifecycle_reliability, provider_constraints, version_continuity. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
