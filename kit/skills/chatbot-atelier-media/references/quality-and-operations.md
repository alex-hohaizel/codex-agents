# Якість, доказовість і супровід

## Незалежні осі

Окремо вести: design quality, evidence maturity, authorization, product scope. Prepared spec не є runnable product; mocked tool не є integration; provider accepted не є human read; observed E4 не є human delight E5. Для must — pass/fail/unknown/N/A із причиною; critical unknown забороняє заяву про готовність цього шляху. Не компенсувати privacy/consent/false-success середнім UX score.

Рівні: E0 hypothesis; E1 inspected source/version; E2 isolated deterministic execution із mocks; E3 integrated execution в названій межі; E4 live provider/transport observation; E5 human assessment. E5 не заміняє E3/E4, а рівні не є однією універсальною шкалою «краще». Для кожного claim потрібен відповідний вид evidence.

## Вимоги до доказу

Evidence record: ID, requirement/claim IDs, artifact/version/hash, environment/config/model/tool versions, procedure, actual result, limitations, actor/run, author/reviewer, dependency snapshot, observedAt/expiry. Рецензент читає raw artifacts, не лише авторське «pass». Current schema graph не доводить справжність receipt; звірити фактичне джерело. Чужий benchmark і офіційна документація не є власним measurement.

Матриця J01–J12 збережена: соціальна увага; reference/clarification; persona/naturalness; useful initiative; consent/authorship; execution/recovery; platform UX; creative composition; memory/long presence; truth/repair; privacy; resources/architecture. Кожна активна має окремий verdict/обjection/uncertainty. Це критерії, не кількість модельних викликів.

## Повнота наміру й придатність стратегії

За матеріального нового scope незалежно звірити первинні повідомлення й джерела з requirement map: кожна вимога, акцент і питання має інтерпретацію, потрібний результат, owner, due gate та доказ або явну причину відкладення/незастосовності. Рецензент отримує сирі джерела, а не лише вже відібраний автором список. Ілюстративний приклад не стає глобальною вимогою. Незаписаний зміст не знаходиться hashes або schema pass; структурний validator не сертифікує семантичну повноту.

Порівнювати застосовні альтернативи й результат за [адаптивною роботою](adaptive-work.md) та [дослідженням/синтезом](research-and-synthesis.md). Рішення має показувати достатність способу роботи, компетенцій і reuse, змістовий контрдоказ та межі впевненості. Природність, мова, медіа, знання, коректність коду й live effects мають власні способи приймання; один PASS не заміняє інші.

Для зміни самої навички або конструктора порівнювати baseline/candidate на різнорідних первинних задачах зі свіжими reviewers і наперед заданою рубрикою; ризикові/нестійкі випадки повторити. Перевірити пропущений акцент, зайву команду/погодження, невідомий домен, зміну джерела, cold resume й невідомий зовнішній ефект. Planned case відділяти від фактичного прогону; скінченний набір не доводить усі майбутні сценарії. До adoption чинних проєктів перевірити сумісність state, незачеплених доказів і rollback.

## Тести й оцінювання

Прив’язати positive, boundary, negative й failure probes до IDs. Contracts tests перевіряють version/type/payload/authorization; model evals — response/retrieval/abstention/referent; integration — actual durable state→effect→delivery; platform smoke — фактичний mobile/web UI; люди — природність/користь/доступність. Негативні: cross-chat/DM leak, untrusted tool policy injection, duplicate event, stale callback/spec/privacy epoch, revoke/forget race, cancel before/after dispatch, lease split/restart, provider uncertainty, resource exhaustion, unsupported operation, degraded mode.

Time/cost/load сценарії мають explicit denominator, input size, hardware/env, concurrency, p50/p95/p99 за потреби, warm/cold і quality impact. Не оптимізувати лише average latency й не вигадувати credits з кількості команд. Огортка інструмента, timeout і retry входять у той самий causal trace.

## Збереження та зміна

Одна authoritative domain state; atomic transitions/transactions, single-owner/version fences, outbox/inbox або інший обґрунтований механізм для DB↔external effect. Не додавати чергу/Redis/workflow engine лише через відомий патерн. Backup/restore перевіряти реально на ізольованому середовищі; версії, retention/tombstones і міграції узгоджувати з memory/privacy. Зберігати workflow progress і remote IDs до довгих кроків.

Carry-forward можливий тільки коли exact artifacts та транзитивні dependencies незмінні, environment/tool/model identity і proof freshness чинні. Shared prompt/router/generator/SDK/DB schema зміна активує залежні claims. Не перепідписувати старий review; прикласти immutable receipt й нову перевірку незачепленості.

## Release і operations

До release виконати підготовку/перевірки в чинному дозволі; authorization scope звірити перед конкретним зовнішнім ефектом. Явне доручення на точну дію не потребує повторного «дозволяю». Підготовка навички не дає права деплоїти бота. За failed gate залишити конкретний blocked scope, а не зупиняти незалежну роботу.

При rollout фіксувати source/build/deploy ID, target, migrations, observed health/delivery і rollback trigger. Incident: severity/user impact, containment, actual evidence, causal hypothesis/test, recovery, data correctness, communication, prevention. Support escalation має destination/owner, delivery state і очікувану відповідь; не вигадувати SLA.

Під час супроводу відстежувати completion/error/uncertain/retry/duplicate/queue-age, response silence/false initiative, retrieval failures/abstention, cost, latency/resource і feedback з privacy-safe telemetry. Зміни моделі/provider/schema потребують impact review та адресних evals. Перевірити export/портативність/завершення сервісу, якщо обіцяно тривале зберігання.


## Admission6.0

Integrated attempt subject requires current contract_sha256 from check_chat_contract.py --subject. Normative contract/requirement/recipe/operation/adapter changes invalidate dependent acceptance. Never add current pins to an old observation retroactively. Code/integration evidence needs an admissible kind, build_ref and environment; integration also needs actual_observation_ref. teamctl mutations require the current revision/CAS; raw save without expected_sha256 cannot overwrite stale state.
