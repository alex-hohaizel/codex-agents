# Середовища, передача, pause і доставка

Перед переходом з’ясувати фактичні можливості Work/Codex/local/cloud: files, tools, SDK, браузер, мережа, акаунти, signing і пристрої. Назва plugin або хоста не доводить операції чи дозволу. Підписка не оплачує сторонній API.

Один canonical source/manifest/version. Не обіцяти автоматичний перенос chat history, skills, browser session або credentials. Встановлення, discovery правильної версії та safe invocation перевіряються окремо. Колізії активних джерел не зливаються; зберегти один обраний спосіб встановлення на конкретному хості.

Launch/return bundle містить request/scope, exact inputs/hashes, current requirements/decisions/knowledge/stop, capability gap, host/tool/version, реальну absolute working folder, готовий природномовний запит або перевірені argv/UI кроки, expected outputs/receipt, return files/path, validation і next action. Не вигадувати Mac path, команди, меню чи tool ID. Якщо операція доступна й дозволена тут, виконати її, не перекладати на користувача.

Pause: не починати нових jobs після now або досягнутої межі. Можна безпечно зберегти receipt/стан уже активної операції. Записати completed/current/pending, job/request IDs, unknown effects, limits і точний наступний крок. Resume не є новим execution/effect grant і не повторює виконане.

Зовнішній effect: prepared artifact/parameters/target + current capability + точне право -> pending/dispatch -> один actual tool call -> receipt -> read-back. Timeout/відсутній receipt дають unknown; спочатку read-only reconciliation. Використати provider idempotency за підтримки; локальний журнал не гарантує exactly-once у провайдера.

Пакет містить фактичні source, інструкції, profile/контракти без secrets, checks/verdict/gaps, manifest/hashes, setup й окремий runbook продукту. Самодостатні модулі мають локальні shared refs/runtime; не покладатись на приховані sibling paths. Архів не є реєстрацією plugin, installation або запущеним сервісом.

Safe import відкидає traversal, symlinks, special files, case collisions, небounded архіви; вхідні scripts не виконуються автоматично. Update не затирає сторонні files/AGENTS/стан/дані. Для конфлікту показати конкретний diff і зберегти backup перед погодженою заміною.
