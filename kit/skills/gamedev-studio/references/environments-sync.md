# Середовища, доставка і синхронізація

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

## Основне правило

Одне канонічне versioned source сімейства → кілька перевірюваних delivery forms. Дані гри мають власний source repo й checkpoints. Skill installation не переносить chat history, browser session, локальні файли або game backend.

## Матриця можливостей

| Поверхня | Що застосувати | Що перевіряти окремо |
| --- | --- | --- |
| Work web / mobile | Bundled plugin skills за наявності install/save; передавати stage packages | Cloud filesystem, current tools, generation rights, service authorization |
| Work desktop | Реально доступні standalone/plugin skills | Cloud чи local execution; local tools/access не припускати |
| Codex desktop Local | Repo `.agents/skills` або підтримуваний plugin | Відкритий game repo, OS deps, permissions, device access |
| Codex Worktree | Той самий tracked skill snapshot у конкретному checkout | Setup deps, branch state; зовнішні DB/store accounts не ізольовані worktree |
| Codex Cloud | Committed repo skills у task checkout або доступний plugin, published env deps | Local Mac/browser/signing sessions не перенесені; environment changes окремо |
| Codex CLI | Repo skills або встановлений plugin; `$skill-name` / `/skills` | CWD/root, exact version, доступна команда CLI |
| Codex IDE extension | Repo/user standalone skills | Plugins офіційно не підтримуються; не обіцяти plugin UI |

Це baseline за офіційними docs від 2026-11-01; перевіряти конкретний host та актуальні зміни під час setup.

## Доставка без конфліктів

Готовий комплект toolkit **4.3.0** має `install_codex.py`, manifest із hashes і дев’ять skill folders. Installer виконує audit/apply/verify, зберігає backups і дає rollback та автоматичне відновлення для перерваного update. Це установка інструкцій, а не game environment/SDK або proof host discovery. Він замінює лише точні Game Atelier skills у погодженому install scope, зберігаючи unrelated files. Для tracked product repository потрібні явні `--project /absolute/project --project-skills in-place` і точний `--skills-root /absolute/project/.agents/skills` або `.codex/skills`; шляхи наявних skill folders та AGENTS references зберігаються. Personal remote-skills checkout та вкладені managed source repositories цим режимом не редагуються. Точні commands і повернення описані в `UPDATE_CODEX_UA.md` комплекту; агент виконує їх у дозволеному scope.

- Repo installs у `<project>/.agents/skills/<name>` робити зі stable source. Не редагувати generated installed copy, якщо це не цілеспрямований suite development.
- User-wide install у `$HOME/.agents/skills` має ширший scope. Не робити його default для окремої гри; інші проєкти можуть потребувати іншої suite version.
- Однакові skill names у plugin + repo + user paths можуть дублюватися; Codex не зливає їх. Залишити один активний канал на host. Не видаляти unrelated skill або global configuration для приховання конфлікту.
- Plugin archive підготовлено ≠ plugin збережено/встановлено у cloud account. Якщо save/import capability недоступна, явно зафіксувати межу й залишити готовий installable package. Не створювати вигадані посилання.
- Для поточного personal skills checkout використовувати штатний Skill Creator save/validation/Git flow. Це окрема дія від установки на Mac користувача.

## Version discipline

Порівнювати toolkit version, contract schema/suite protocol, package identity та actual file hashes. Toolkit **4.3.0**, game-model **4.0.0**, handoff schema/suite protocol **1.0.0** і runtime state **2.0.0** — різні чинні версійні області. Handoff/runtime вимагають точний toolkit marker; попередні формати результатів не читаються. Назва «останній.zip» не визначає свіжість. За конфлікту двох edited copies не брати більший timestamp автоматично: зіставити source commit, accepted decisions і manifest parents, сформувати change/impact report.

Для update: canonical source change → validate + forward tests → new package → explicit project update → sync-check → read impact report. Зберегти старий accepted package для rollback; не перегенеровувати media для простої зміни instruction text.

## Передача через host boundary

Work → Codex: approved brief, current studio assets, specs/configs/content matrices, source media where produced, license/provenance, manifest+hashes, decisions and gaps, exact next skill/host. Codex → Work: review extracts, real captures, asset requests, identity masters і IDs, не secrets або весь database dump.

Generation bridge має окремий job/request manifest. У ньому: request ID, master file hashes, selection status, locked features, allowed creative variation, dimensions/duration/export requirements, provider/license/cost constraints, required return files. Після повернення compare з masters; modified output стає новим versioned asset лише після acceptance.

## MCP / plugins / CLI

CLI достатній → не встановлювати MCP лише заради модної архітектури. MCP до зовнішнього сервісу додавати за реальною потребою та з мінімальними правами; перевірити доступність у потрібному host. Browser login не означає MCP OAuth і навпаки. Secret values не входять у suite/game archives, logs або screenshots.

За Cloud localhost MCP не вважати доступним. Документувати transport/host/network/auth prerequisites; залишити owner setup step, якщо немає дозволеного supported connector. Не використовувати неперевірені третьосторонні server executables або «безкоштовні» API як обов’язкову залежність.

## Офіційні джерела

- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/plugins
- https://learn.chatgpt.com/docs/environments/modes
- https://learn.chatgpt.com/docs/extend/mcp?surface=cli
- https://learn.chatgpt.com/docs/enterprise/plugin-management

Workspace marketplace sync потребує admin-доступу; не рекомендувати його як гарантоване personal account рішення. Підтримуваність формату не доводить feature flag або permissions користувача.

Установлення toolkit не змінює game saves чи project registries. Звичайні команди `atelier.py` приймають лише поточний toolkit marker та runtime schema **2.0.0**. Для чинного native workflow4.2→4.3 є явний `workflow-upgrade` preview/apply за [сценарієм](orchestrator-workflow.md): exact source/target hashes, reviewed authority, незмінний backup, journal receipt та адресні impact IDs. Він не запускається suite installer автоматично, не змінює продукт і не повторює tasks/effects. Інші попередні формати не читаються як чинні: відновити їх фактичний accepted intent і джерела до окремого рішення. Reconcile suite hashes перед залежною роботою, не перезаписувати canonical approval чи masters.
