# Контракт етапу chatbot-atelier-specification

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати предметну й цілісну модель, контракти компонентів, архітектурні/мовні ADR з наслідками, карту взаємодій і acceptance. Специфікація агентної команди й архітектура цільового продукту — окремі рішення; обидва мають покривати весь застосовний намір.

## Обов’язковий предметний маршрут

## Формалізувати кожну активну систему

Вести system register: ID/purpose/applicability/owner/entities/typed fields/units/ranges, authoritative state, ingress/output/events, permissions/audience, dependencies, failure, restore/migration, acceptance. Кожне правило має algorithm/order, sampling/snapshot time, validation boundaries і golden vectors. Для ймовірнісної LLM поведінки визначити допускаємі виходи/abstention/evaluation distribution; не обіцяти детермінізм, якого нема.

Визначити envelope tenant/workspace/chat/topic/actor/audience, request/logicalOperation/source/version/privacyEpoch, authorization scope і causal trace. Розвести platform event, domain command, tool request, external effect, outcome й delivery. Вибрати один owner/джерело істини для кожного commitment/consent/memory/delivery; ERD↔API↔events↔prompts↔tests↔rollout узгодити.

## Lifecycle та фізично здійсненна семантика

Визначити exact guards/atomic boundaries для proposal/needs_input/authorization/prepared/dispatch/running/succeeded/failed/uncertain/cancel/expiry/reconcile/delivery. Dedup identity/retention, version fence, retry class/attempt/deadline/backoff і recovery після кожного crash point. За external uncertainty пояснити reconcile/compensation; не писати «exactly once» без доведеного scope.

Persistence: поля, authoritative owner, transaction boundary, replay/migration/version compatibility, backup/restore, retention/tombstones. Time: UTC instant і IANA civil zone, DST gap/fold/recurrence/misfire/reschedule. Memory: provenance, corrections/TTL/privacy and derived invalidation. Group: roster/consent/authorship/late join; media: source/export/runtime/delivery identity.

## Перетини й вихід

Для кожної active pair залежності cause→effect→allowed order→failure→repair→persist boundary→UI feedback→acceptance. Обов’язково check memory/jobs/delivery, DM/group, persona/tool truth, platform/domain ACK, scheduler/revoke, media/resources, schema/rollback. Позначити conditional/N/A з причиною; unknown не unchanged.

Передати typed model, state/event/API/schema contracts, alternatives/ADR, sequences/golden vectors, all journey states/negative cases, migration/observability plan, production recipe/receiver map. Статус specified означає узгоджену специфікацію, не execution. Build повертає нездійсненні capabilities upstream із конкретним доказом, а не спрощує promise мовчки.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: execution_truth, consent_authority, lifecycle_reliability, version_continuity. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
