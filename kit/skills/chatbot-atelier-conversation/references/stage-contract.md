# Контракт етапу chatbot-atelier-conversation

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати карту розмовних станів, мов/тону й адресатів, реальні варіанти/приклади та контрастні evals; відділити AI-оцінку від людського приймання природності. Ранні технічні кроки не знімають погоджених вимог до мови й досвіду.

## Обов’язковий предметний маршрут

## Намір, адресат і характер

Відновити місію/аудиторію/стиль поточного бота. Кожен response decision перевіряє recipient/referent/reply/topic, direct vs ambient intent, явну паузу й freshness. Дві offers+«давай» не повинні запускати чужу дію; уточнити тільки вирішальну неоднозначність. Інша людина говорить іншій — часто доречне мовчання. Прямий новий запит не губити через pause/proactive policy.

Persona: own stance/warmth/humor за контекстом, підтримані мови, культурна доречність, avoid repetitive offers/therapeutic templates/false biography. Не показувати людям team modes/registry/step IDs і не змушувати обирати технічний формат для простого списку. Спочатку найменший достатній результат, потім максимум одне доречне розширення. Складний запит не обрізати заради штучної короткості.

## Дії й взаємодія

Зіставити utterances/welcome/help/tool descriptions/examples/results/progress/errors/final з фактичними operation capabilities і state. «Підготував», «в черзі», «запущено», «готово», «надіслано» мають різні докази. Не лікувати false success теплішою фразою; repair має фактичний next step. Не створювати паралельний controller з другим owner.

Buttons/details/start/continue/cancel/retry мають видимі decision facts, state/version binding, expiry й meaningful outcome. Long text split/localization/display перевірити в target platform/device. Групова activity має optional join/exit, self-authored consent/choices, immutable round roster, late join rule, private instructions й first meaningful move. Згода host не є згодою всіх; відмова одного не губить independent accepted task.

## Оцінювання

Frozen old/new contexts8 strata: direct, indirect, human-to-human, playful/emotional, pause, ambiguous, failure/repair, memory return. Minimal pairs і1/5/20-turn continuation з synthetic fixtures; кожна підтримана мова має actual phrasing. Вести false speech/silence/wrong-recipient/extra-question/task-loss counts із denominators. Human blind A/B має ties/both bad і voluntary scope; LLM score не доводить human naturalness.

Вихід: versioned persona/policy/dialogue states, callback/participation contracts, fixtures/eval report, actual quality limitations і integration acceptance. Naturalness не компенсує privacy/consent/tool truth; code tests не доводять доречність розмови. Після deployment реальна chat observation окремо.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: natural_voice, context_relevance, proportional_depth, simple_first, recovery_empathy, multiuser_fairness, interaction_continuity. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
