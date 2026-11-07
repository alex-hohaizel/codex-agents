# Контракт етапу chatbot-atelier-integrations

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати фактичні capabilities/обмеження платформи, контракт дії, права, межі state/effect/delivery та перевірки повтору/скасування/reconcile. Scheduler, transport і remote executor називати доступними лише після фактичного підтвердження; сон або недоступність host мають явний результат.

## Обов’язковий предметний маршрут

## Контракт platform→domain→provider

Звірити actual API/SDK/version/schemas/auth/rate limits/callback acknowledgement/delivery semantics і granted scopes. Для Telegram, Slack, Discord не переносити timed rules однієї платформи в іншу. Розвести ingress authenticity, durable dedup+work, швидкий ACK, domain authorization і видиму user response. Усі callback/text/tool routes сходяться в одну authoritative command handler.

Tool operation passport містить supported/effective params, limits/outputs, read vs mutation, costs, target env, evidence/freshness. Capability claim має реальний ingress→tool→runtime→verified output шлях. Montage/generation/music/voice — різні операції. Зовнішній текст/tool result не створює permission. Уже надана authorization exact scope діє без повтору.

## Ефекти й довгі роботи

Logical operationId, scope/actor/spec/privacy version, idempotency key/retention, dedup/fence, bounded queue/time/bytes/CPU/RSS. States/guards/atomic writes фіксують before/after dispatch cancel, expiry/revoke, retry classes/backoff/deadline, uncertainty/reconcile і separate delivery record. Crash після provider success до local commit не запускає сліпий resend. Незалежні частини mixed request зберігаються окремо.

Scheduler: instant/civil IANA timezone, reference now, DST gap/fold, recurrence occurrenceId, overdue/misfire/skip/reschedule/expiry, lease/fence й restart. Group workflow: named/open invite, self consent, frozen roster, private role delivery, first move, late join/exit/timeouts. Payments якщо active: authoritative provider event, amount/currency/entitlement owner, webhook signature/dedup, refund/revoke and fulfillment truth.

## Виконання та приймання

РецептR-C02/R-C05/R-C07: synthetic fixtures→actual functions/isolation DB→end-to-end adapter→provider boundary за доступом. Negative controls: wrong actor, stale callback, duplicate event, old semantic version, revoke/forget during running, cancel at each dispatch boundary, provider timeout after effect, resource cap, scheduler restart/DST.

Вихід: supported adapter/handler/schema/migration/source, operation recipes+actual attempts, receipt traces, UI repair states, tests+limits, provider readback за фактом. Mock provider доводить лише named boundary. ACK або queued не значить delivered/human read; message_id сам по собі не доводить прочитання людиною.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: practical_completion, scheduling_fidelity, capability_truth, execution_truth, interaction_continuity, multiuser_fairness, bounded_resources, lifecycle_reliability. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
