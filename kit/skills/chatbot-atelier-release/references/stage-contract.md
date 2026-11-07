# Контракт етапу chatbot-atelier-release

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати readiness точного артефакту, чинний scope authorization, вплив на старі jobs/state/дані, перевірку rollback/compensation та реальні квитанції. Установка нової навички не означає міграцію або випуск продукту.

## Обов’язковий предметний маршрут

## Підготовка до зовнішньої дії

Звірити target platform/service/environment/account й source/build/assets identity, required checks на точному artifact, independent QA/evidence, migrations/data ownership, secrets separation, privacy/retention/tombstones, resource/cost limits, rollout/stop/rollback. Виконати оборотну підготовку в чинному scope до питання дозволу. Наявна exact authorization залишається чинною; не питати повторно через слово«реліз».

Зелений CI не доводить deployed/live delivered або naturalness. Provider docs/version/SDK/schema й installed commands перевірити current. Історичний runbook/test names/deploy service/sticker count не live truth. Не розгортати довільний new paid resource як «технічну деталь» без належного scope.

## Compatibility й rollout

Старі pending jobs/buttons/semantic versions, database state/migrations, model/tool contracts, memory privacy epochs/tombstones, approved media fingerprints і delivery dedup лишаються узгодженими. Backup/restore/rollback перевірити на isolated environment; old backup не resurrect erased data. Назвати forward-only migration/compensation, якщо rollback фактично неможливий.

Фіксувати actual deploy/publication ID та pinned source/build/hash. Poll existing job, не submit duplicate. На uncertain API response спочатку status/readback/reconcile. Observe provider health/version/logs, run bounded platform smoke for requested feature and actual media membership/readback where relevant. Human read/задоволеність не доводяться send accepted.

## Deliver і передача

Release receipts target/source/build/deploy/time/env/checks/health/delivery/rollback; actual failed and partial outcomes; owner/support contact, recovery/export/retention за обіцянкою. Успіх одного сервісу не приховує failure залежної доставки. За недоступної live межі фінал«підготовлено/локально перевірено» з exact blocker і виконуваним next step.

Operations receiver отримує evidence limits, SLI/alerts/incident owner, current source/provider state, unresolved jobs/retries, migration/restore policy і support routes. Сам реліз не запускає бездоручену recurring automation.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: version_continuity, audience_privacy, forgetting_integrity, media_delivery, execution_truth, provider_constraints. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
