# Розумне використання моделей, агентів і контексту

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

## Бюджет перед роботою

У task contract записати: що створюємо, які інструменти реально доступні, які facts потребують refresh, кількість дорогих generation requests, allowed spend (default: без додаткових витрат), очікувані checkpoints і stopping condition. Підписка не означає unlimited runs чи автоматичну оплату всіх APIs/CI/media services.

Не закріплювати назви/ціни моделей у навичці. Вибирати з фактично доступного host: routine formatting/search/local refactor — достатній дешевший режим; cross-domain architecture/critical review — сильніший, якщо доступний і обґрунтований. Не змінювати модель користувача поза явним allowed scope.

## Команда за артефактом

Один orchestrator, предметний integration owner, потрібні компетенції, independent reviewer. Створювати subprocess/subagent лише коли незалежна задача зекономить час або покращить оцінку; не створювати ієрархію назв без роботи. Якщо subagent API недоступний, виконати дисципліни послідовно й не записувати вигадані agent IDs/independent outcomes.

Кожному worker: task ID, input paths+hashes, requirement IDs, allowed writes, очікувані outputs, acceptance method, бюджет, що повернути батькові. Main chat отримує summary + paths + evidence; noisy logs залишаються у scoped files. Shared writes передати одному інтегратору; паралельний код — isolated paths/worktrees.

Review рівні:

- Local: оборотна правка без зміни контрактів — focused check.
- Feature: конкретна subsystem — незалежний reviewer ризикових результатів.
- Critical: physics/economy/save/purchase/identity/contracts — предметна незалежна перевірка та impact graph.
- Stage: acceptance handoff за фактичними artifacts і unresolved risks; не новий повний аудит всіх unchanged inputs.

## Контекст і retrieval

Файли — авторитетне джерело; чат — steering. Тримати короткі checkpoint, decisions, manifest, requirement index та links до assets/evidence. Для task читати відповідні IDs через `rg`/file index; не завантажувати всі тексти/всі кадри щоразу. SQLite FTS доречний за розміру; remote vector RAG — лише якщо є виміряна потреба й budget.

Retrieval result повинен мати source path, version/hash і fragment context. Не змішувати superseded draft із accepted spec. Derived indexes відновлювані; не зберігати в них єдину копію рішення. LangChain/LangGraph/embeddings не default залежність: host-native orchestration + explicit state/typed handoffs достатні, доки немає доведеної зовнішньої потреби.

## Перевірка без зайвих повторів

Спершу дешеві deterministic перевірки: schema/path/hash/provenance/config/tests. Потім дорогі media/human/device оцінки за ризиком. Перевірка checksum не є quality review. Не запускати повторно 1000 tests лише тому, що вони є; вибір через changed dependencies, broad checks — перед release або за нових невідомих ризиків.

Один repair batch, повторити affected check. Після двох однакових невдалих спроб змінити діагностику, інструмент або питання. Зупиняти spend на недоступний capability; повернути конкретний альтернативний шлях, cost/quality tradeoff і required user decision.

## Докази

Окремо маркувати hypothesis, paper/design review, simulation, automated test, real build, device test, player observation, service-confirmed release. Синтетична симуляція не доводить D1/D7 retention, monetization або fun. AI reviewers не замінюють людей-гравців чи hardware tests.

Завершений цикл: accepted artifact → recorded evidence → persisted checkpoint → next exact action. Не нескінченний «ще одна рада, ще одна генерація».
