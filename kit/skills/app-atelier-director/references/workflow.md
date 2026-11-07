# Інтеграційний маршрут

## Входи й поточний scope
Прийняти звичайну мову, current project records, пакети, repo/version та фактичні спостереження. Відокремити change-agent від execute-product. До execution скласти current brief: goal, audience, scope/stop, акценти, known constraints, available resources, decisions і залежності. Import/approve не повторює зроблене й не надає чужих прав.

## Точки виконання
1. Intake: actual profile, state, права, capabilities, ресурси й execution scope. Якщо owner-approved starter profile доступний, перенести його як project-local source з provenance/hash; не вбудовувати в immutable навичку.
2. Research: маршрутизувати окремі ринкові треки з профілю. Спершу коротка карта; глибину збільшувати за evidence й ресурсним планом. До наступного етапу отримати власний вибір напряму.
3. Concepts: цілісний користувацький/платіжний/операційний/залучальний шлях та повна економіка. Перевірити manual dependencies, конкурентний case, припущення. Власник обирає концепт або дозволяє обмежені прототипи.
4. Specification + experience + growth planning + release feasibility: узгодити сценарій і дизайн, data/auth/billing/support, оцінку й обмеження, реалістичний маршрут stores/SDK/budget/testing. Власник приймає material scope, design і budget.
5. Representative slice, build + support: довести ризиковий повний сценарій до масштабування. Ліди мають свої paths, API/contracts і outputs. Не домислювати недоступну платформну перевірку.
6. Independent QA: кожний due must і artifact pinned; finding відкриває конкретний repair. За відсутності незалежного актора чесно позначити self-check і pending gate.
7. Prepared release -> owner readiness -> достатня згода на exact effect -> actual tool -> receipt/read-back. Store submission, approval і production availability різні.
8. Post-release: дозволені activation/metrics/monitoring; request/incident -> impact -> targeted spec/build/QA/release. Припинення має свій data/export/delete/cost contract.

## Task contract і ресурси
Для кожного делегування: goal, input/source hashes, assigned requirement IDs, owner, paths, outputs/interfaces, evidence/acceptance, time/token/call/money caps, stop і review actor. Власник path не пише одночасно з іншим writer; worktree не ізолює production DB чи акаунт. Root/integrator єдиний інтегрує shared state й approvals.

Масштаб ролей пропорційний output. Автор не є reviewer. При недоступних subagents послідовна робота дозволена, independence status лишається чесним. Не розширювати команду/раунди після двох однакових невдалих ремонтів без нової діагностики.

## Пам’ять і корекції
Source -> requirement -> task -> artifact -> evidence -> review -> next action. Lesson має confidence/scope/applicability/impact і не змінює права. Після source/version/permission change позначити залежні checks stale. Поточний brief не замінює exact originals або receipts. При resume читати external state перш ніж retry unknown effect.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: інтегрована карта вимог і залежностей, аргумент достатності команди, власні рішення інтегратора, приймання цілого й наступний валідний крок. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: повнота первинного наміру, достатність композиції, спільні контракти та якість кінцевого цілого. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
