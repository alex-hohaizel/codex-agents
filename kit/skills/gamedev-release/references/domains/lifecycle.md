# Повний продукт, експлуатація й розвиток на доказах

## Застосування, вхід і власний результат

Застосовувати до кожної гри, включно з offline/premium/no-offer. Прийняти launch scope, всі активні domain contracts, accepted masters, platforms/devices, capabilities, права й budget. Власний результат — product lifecycle map, finite content/cadence plan, save/update/support contracts, measurement/experiment plan, release/rollback criteria та checkpoint/return bundle. Використати [шаблон](../../assets/domain-templates/lifecycle-measurement.template.json); не створювати другу authority registry або фонову службу з одного файлу.

## Весь досвід і скінченний launch scope

Описати first acquisition/store promise → install/first open → learning/first satisfying loop → early/mid/late progression → completion/postgame → return after absence → support/update/offboarding за застосовності. Scope містить реальні content units/families, meaningful differences, authored vocabulary, composition/forbidden combinations, novelty decisions, milestones, ending й повторну цінність. «Гра готова» не означає лише одну сцену з рухом і меню.

Для кожної обіцянки знайти rule/data/asset/runtime/user-state consumers і строк доказу. Надто великий scope відсікти через конкретні trade-offs до production commitment; не маскувати відсутні системи словами «MVP», якщо вони є accepted must. Малий продукт може мати концентровану глибину; велика кількість сцен не компенсує повторювані рішення. Не підміняти завершений продукт нескінченним backlog.

## Збереження, offline, переривання й оновлення

Задати authoritative state, save boundaries, schema/version, atomic commit/backup/integrity, corrupt-save recovery, migration/rollback, inventory/unlocks/world state, settings/curriculum й session resume. Для offline-first описати допустимі дії/clock changes/claims, sync/conflict/account merge лише якщо є backend. Не створювати аккаунт чи server заради чекліста. Unknown purchase outcome не розв'язується переписуванням локального балансу.

Suspend/resume/kill/network loss/audio focus/notifications/deep links за застосовності мають конкретний player-visible outcome. Гравець після повернення бачить актуальну ціль, обладнання/ресурсний стан, нагороду рівно один раз і доступне продовження. Update має сумісність content/config/save, safe rollout/rollback, rights/SDK recheck й fair paid-entitlement handling. Відновлення старої збірки не повинно повторювати зовнішні ефекти.

Підтримка містить repro/build/device IDs, мінімальний privacy-safe trace, receipt/state lookup для обраної commerce, triage/severity/owner, player message, recovery й escalation. Не збирати повні персональні дані чи production DB «про всяк випадок». Закриття сервісу/кінцевого контенту, якщо релевантне, потребує зрозумілої політики доступу/збережень/прав; не обіцяти безстрокову інфраструктуру без плану.

## Growth, утримання й органічне поширення

Гіпотеза повернення посилається на конкретну player value: нове рішення, mastery, очікуваний unlock/reward, відкриття світу, добровільну спільну мету або інший зміст. Не вважати push/streak/штучний deficit доказом цікавості. Для sharing описати самодостатній момент/результат, добровільний capture/share, користь глядача, attribution за можливості й шлях до гри без вимоги спаму. Вартість content production/support включити навіть за нульового рекламного бюджету.

Для метрики задати назву, event/schema/version, numerator/denominator, population/cohort, calendar/time zone, observation window, exclusion/missing-data policy, uncertainty, privacy/consent і рішення, яке вона підтримує. Відрізняти install, first open, activation, completed loop, return, engaged time, payer і actual receipt; не підміняти їх один одним. D1/D7/retention targets не є спостереженим результатом; маленька вибірка й selection bias обмежують висновок.

Player tests записують question, recruitment/participant limits, сценарії, assistance policy, observed behavior/errors, фактичні builds/devices, anonymized outcomes і residual risks. AI critique й simulation можуть підготувати/аналізувати test, але не створюють учасників чи факти їхніх дій. Для experiment — assignment/control, hypothesis, primary/guardrail measures, exposure, duration rationale, stop/rollback і decision rule до перегляду результатів. Не називати кореляцію causal uplift без відповідного дизайну.

## Контентна cadence й адаптація

Новий контент має змінювати decisions/взаємодії, а не лише inflation/recolor. Задати vocabulary growth, production/QA cost, reuse, compatibility, сезонні overlaps/expiry за потребою, exhaustion horizon і власника. Немає універсального обов'язку live service: завершена premium гра може мати інший support/update lifecycle.

Нова вимога, дефект чи спостереження проходить provenance → affected IDs → causal impact → scoped task → actual output/evidence → review → closure. Прийняті решения/masters не переписувати під назвою self-learning. Урок гри не стає автоматично загальним правилом сімейства або ширшим дозволом. Запропоноване покращення агента зберігати окремим scope; canonical requirements/decisions лишаються чинними.

Відкривати транзитивно залежні checks: зміна камери торкає input/readability/AI/creative; progression price — rewards/commerce/pacing; shared rig/shader — усі залежні assets/runtime captures; save schema — migrations/resume. Незмінні hashes/умови дозволяють переносити попередні докази. Два однакові невдалі ремонти запускають нову діагностику, не нескінченне повторення review.

## Stage gates, ролі й продовження

Concepts потребує цілісної launch/lifecycle arc, causal retention/growth hypothesis і чесних production constraints. Preproduction — typed contracts/data/spec_refs і executable risk models. Slice — actual source→native runtime→device observations, збереження/повернення й peak behavior. Beta — реальні люди/кохорти в заявленому scope. Release — current independent review, actual builds/devices, критичні money/save/privacy/authorization checks, current platform requirements і конкретний дозвіл зовнішніх дій. Liveops — actual telemetry/support/provider outcomes, а не припущення за старим чат-переказом.

Producer інтегрує scopes/залежності; предметні автори створюють contracts; runtime/platform/ops owners забезпечують actual behavior; QA незалежно перевіряє relevant claims; люди оцінюють людський досвід. Наявність назв ролей не доводить їх виконання. Команда пропорційна задачі й реальним слотам; локальний repair не запускає всю студію.

На паузі/переході Work↔Codex зберегти current source/version/hash, accepted choices/favorites, готове/поточне, pending external outcome, точну межу, next action і перевірюваний launch/return bundle. Одночасні writers одного проекту/production resource повинні мати явне ownership/locking; інший чат не створює ізоляцію. Установка навичок не переносить chat history або локальні toolchains. Фоновий monitoring/schedule існує лише після фактичного дозволеного створення.

## Джерела й статус рекомендацій

- [Roblox: Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques) — офіційні рекомендації про contextual learning і тестування підказок; не гарантія retention.
- [Google Play: purchase lifecycle](https://developer.android.com/google/play/billing/lifecycle/one-time) — офіційні state/reconciliation integration requirements для застосовного продукту.
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) — актуальну policy перевіряти перед залежним release; не фіксувати її назавжди в skill.
- Lifecycle/measurement/impact gates вище — правила агента; вони не доводять комерційний результат або людське задоволення автоматично.
