# Контекст, агенти, ресурси й підключення

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

Поточний інструмент: `.gameatelier/orchestrator/state.json` — durable sidecar, чинні canonical state/decisions/requirements зберігаються. Перед dependent task звірити current intent, due must, decisions, knowledge, file/proof/suite hashes; retrieval і пам’ять чату не замінюють це. Нову особливість проекту записувати з точним джерелом/confidence/scope/stages/impact і застосовувати до всіх залежних етапів, не змінюючи глобальні skills автоматично.

## Початковий preflight

Прочитати project AGENTS.md, state/checkpoint, чинний handoff і лише потрібні reference sections. Перевірити dirty tree/branch/worktree, доступні tools/skills, ОС, native SDK і фізичні пристрої, мережу, budget та scope повноважень. Зберігати non-secret capability report: available/tested/version/location/limitations/cost/license. Наявність плагіна не доводить права; назва инструмента не доводить підтримку генерації моделі/музики.

Підписка ChatGPT/Codex не включає довільні third-party APIs, комерційні ліцензії Suno, хостинг чи store accounts. За замовчуванням без додаткових витрат: локальні open-source tools та вже реально доступні можливості підписки. Платний fallback — рішення користувача з ціною й правами, без автоматичної активації. Не обіцяти професійне аудіо чи 3D якість через відсутній інструмент.

## Context as files, retrieval за потребою

Мінімальний index: requirement ID → relative path → section/record ID → revision/hash → owner → evidence → depends_on. Почати з rg/структурованих JSON queries. Завантажувати короткий summary плюс точні залежні фрагменти. Vector/RAG додавати тільки коли вимірювано поганий retrieval у великому корпусі: versioned chunks зі source IDs/hashes, hybrid keyword+semantic, metadata filters, reranking, provenance, delete/reindex on change, retrieval eval cases. Embeddings не є source of truth і можуть мати окрему API ціну. Не вивантажувати весь repo у prompt.

Замість довгого прихованого chain-of-thought зберігати ADR: problem/options/decision/tradeoffs/evidence/rollback. Не вимагати приватного reasoning trace. LangChain/LangGraph не потрібні для звичайного Codex workflow. Додавати orchestration framework лише за реальною потребою durable external jobs, retries, state machine; з pinned dependencies, idempotent nodes, failure recovery й тестами. Немає магічного framework, що замінює quality gate.

## Декомпозиція

На feature workstream видавати artifact-level task: exact inputs/hashes, assigned requirement IDs, owned paths, interfaces, done check, resource cap, stop. Не передавати всім повний чат. Незалежні роботи розпаралелювати; dependencies, approvals, shared mutations і інтеграцію робити послідовно. Уникати двох авторів одного file. Для коду — ізольовані branches/worktrees, coordinator merges, одна production DB migration owner.

Обирати число агентів за фактичним лімітом і кількістю незалежних deliverables; root сам пише/інтегрує. Відокремити QA від авторів. Важливі первинні альтернативи дослідити незалежно; не плодити 23 однакових суддів для 23 рядків. За недоступності subagents виконати sequential production і позначити independent review pending. Не вигадувати команди чи конфіг multi-agent, яких поточний клієнт не підтримує; перевірити поточні official docs.

## Ресурсна дисципліна

Перед циклом задати time/token/generation/storage/cloud spend caps та правила checkpoint. Конкретні числа узгоджувати під проєкт, не успадковувати довільний 48h cap R06. Дешеві deterministic lint/validate/build перевірки запускати перед дорогими image/audio/native jobs. Для art спочатку один composed slice, тоді batch. Для змін assets повторювати тільки invalidated captures/tests. Два невдалі ремонти → інша діагностика. Не повторювати весь етап через косметичний diff. Не вмикати paid LLM CI без окремого рішення; deterministic CI працює без API ключа.

## MCP і tool adapters

Використовувати native CLI, офіційний SDK або достатній connected plugin. MCP корисний для docs/artifact search, Blender/editor automation, tracker, analytics і store API; не встановлювати довільний неперевірений сервер за назвою. Перед підключенням: джерело/maintainer/version/license, transport, actual tools, read/write scope, credential storage, network boundaries, install test і uninstall/rollback. Read-only default для discovery; write scope в межах доручення. Не пакетувати credentials у plugin JSON. AGENTS.md може описати connector, але не створює його.

Capability bridge Work↔Codex: запит файл зі source IDs/hashes, генератор/version/parameters/reference asset, цільовий формат/quality/licenses → actual output+provenance → local import → compare → acceptance. Якщо modality недоступна в Codex, відкрити точне завдання у Work; не замінювати його кодовим placeholder. Не припускати, що browser-login або Work account автоматично авторизує local tool.

## Checkpoint і відновлення

Після матеріального артефакту/перед дорогою операцією зберігати state: stage, project/revision, input hashes, confirmed/pending decisions, completed outputs, open defects, running job IDs (реальні), exact next command, skill version, environment, costs/limits, evidence. У resume спершу перевірити bytes й actual external state, не повторювати purchase/upload/deploy наосліп. Read/status перед retry; idempotency key для зовнішнього effect. Background monitor/recurring task створювати лише за дорученням.

## Синхронність середовищ

Canonical skill source → portable skill-only plugin та project `.agents/skills` export з однаковими file hashes і version. Work personal-skill installation, plugin account saving й Mac local install — різні факти; звітувати окремо. Автоматичного двостороннього sync чатів/локальних skill folders не припускати. Якщо plugin вже містить ті ж names, не активувати ще project copies мовчки: обрати один активний спосіб і перевірити loaded source/version. Сліпий overwrite modified skill заборонений; показати diff і зберегти власні зміни. Sync-lock перевіряє bytes, не гарантує що UI завантажив їх: нова сесія й явна smoke invocation потрібні.

Офіційні orchestration/session/compaction механізми — опційні адаптери, не виконані інтеграції від наявності цього файла. Для SDK обрати одну стратегію history, не дублювати local replay і server-managed continuation. Opaque compaction не є readable source/decision ledger. Input/output guardrails не охоплюють усі custom-tool effects: exact action authorization/idempotency/receipt перевіряються на boundary конкретного tool. Interrupt/retry може повторити тіло job; unknown effect спершу звірити read-only. Не записувати приховані reasoning traces або secrets у remote tracing.

Для ілюстрованого пошуку task contracts явно покривають усі systemic passport IDs. Автор готує причинні сценарії та фактично оглядає кожний target; інший actual actor виконує semantic review кожного потрібного паспорта. Технічний art reviewer звіряє доступний production profile до генерації; незалежний visual review може бути пропорційною чесно позначеною вибіркою. Наявність названих ролей не є proof.

## Зрозумілий спосіб роботи та належна компетенція

Використати [адаптивний контракт](adaptive-work.md), не дублюючи канонічний state. Розділити масштаб зміни, невизначеність, критичність, зв’язність і потрібний доказ. Показати коротко мету, результати поточного scope, чому цього підходу й компетенцій достатньо, потрібні рішення та спосіб приймання. Зберігати повний target і пізні must окремо від current slice.

Кожна предметна роль повертає власний перевірний output: research — питання/джерела/контрдокази; systems/preproduction — правила, взаємодії, архітектуру й fixtures; experience/assets — прийняті masters та інтегрований досвід; build — реальну збірку/зміну; QA — незалежні оракули й findings; release/liveops — exact effects і поточні спостереження. Integrator показує вплив на ціле. Метод і кваліфікація reviewer мають відповідати виду claim; інший ID не є достатнім доказом компетенції.

Для матеріального scope незалежно звірити первинні джерела з вимогами, включно з пропущеними акцентами, питаннями й відкладеними результатами. Ілюстративні приклади не стають загальною policy. Доручення режимам [дослідження/синтезу/звірки](research-and-synthesis.md) має точні inputs, outputs, cap і межі повноважень. Дані й аудиторії різних проєктів розмежовані; shared executor не переносить доступ між ними.
