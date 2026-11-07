# Маршрутизація та повернення upstream

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

## Короткий зміст

1. Об’єкт виконання.
2. Контракти етапів.
3. Прийняття вибору і повернення.
4. Режими запуску.
5. Негативні приклади.

## 1. Об’єкт виконання

Окремі об’єкти: suite source (інструкції й scripts), studio identity package (бренд і account plan), game source repo, stage handoff, build artifact, store release, liveops change. Вони не замінюють одне одного. «Створив release skill» не означає «випустив гру». «Запакував studio assets» не означає «зареєстрував юридичну особу».

До кожного пакета додавати читабельний next-action: точна skill, primary host, потрібний input, capability prerequisites, що користувач має зробити сам, acceptance gate. Різні hosts можуть мати різні функції; capability report має пріоритет над назвою продукту.

Актуальний машинний каталог — `assets/stage-catalog.json`, внутрішній робочий цикл — [orchestrator-workflow.md](orchestrator-workflow.md). Agent інтерпретує природну мову, сам читає навичку й обирає реальні tools; local runtime перевіряє структуровані записи. Для незрозумілого матеріального наміру — пояснене питання, не мовчазне keyword routing. Користувач не зобов’язаний знати назву skill/script.

## 2. Контракти етапів

| Етап | Мінімальний зміст прийнятого результату | Не доведено одним таким пакетом |
| --- | --- | --- |
| Studio | Approved master identity, production exports/source, fonts/licenses, placements, developer/account/tooling plan, owner setup steps | Name clearance, legal entity, active paid accounts, connected payouts |
| Concepts | Alternatives/market evidence, explicit core loop/progression/variation/economy, master visual target, feasibility/cost assumptions, chosen concept and questions | Player retention/revenue, physics from image, all production assets |
| Preproduction | Versioned GDD/TDD, exhaustive state/input flows, simulation configs/formulas, concrete content/authoring matrices, build/QA plan, closed critical choices | Complete game, user playtests, store acceptance |
| Assets | Real source/export files, identity conformance, complete audio/animation/collision/material definitions, provenance, integration smoke evidence | Runtime performance on all devices, completed gameplay |
| Build | Native source, deterministic content/config inputs, reproducible build setup, actual test artifacts, runtime capture, integration evidence | Independent release acceptance, valid distribution signing without credentials |
| QA | Independent requirement/fidelity/gameplay/device/monetization tests, results and defects, release recommendation | Zero bugs, future revenue, review approval by stores |
| Release | Real release artifact + submission assets, verified current policies, staged rollout/rollback, owner actions and observed store/backend status | Published status before confirmation by actual service |
| Liveops | Versioned incident/change plan and deployed results only when executed, economy/content changes and telemetry | Permanent autonomous monitoring without a running authorized scheduler |

Common handoff contract supplies exact required paths/statuses; this table explains meaning, not a competing schema.

## 3. Прийняття вибору і повернення

Без прийнятого concept selection не вибирати фінальну гру за таблицею оцінок мовчки. Можна завершити дослідження, порівняння й recommendation до рішення користувача. За accepted studio identity переносити originals, не відтворювати логотип генерацією.

Saved favorites не є production selection. Preview-only/search-only або pause after artifact дає зрозумілий проміжний пакет без accepted production status. Перед кожним job звіряти current stop; перед наступним етапом не трактувати «гарно» чи рейтинг як згоду на двигун, економіку або випуск. Адресна incident/feature робота використовує catalog return routes й зачеплені acceptance, зберігаючи решту прийнятого задуму.

Матеріальна зміна включає: platforms, core control/physics model, engine/rendering compatibility, visual/audio identity, progression type/paid advantage, account/online architecture, user audience/region, платні tools/cloud. Повернути конкретне питання з tradeoffs і впливом; не повертати весь stage до нуля.

Змінився input hash → побудувати impact graph requirement → spec/config → asset/code → test → build/release. Старі докази придатні лише для незмінених транзитивних залежностей. Зміна логотипа не вимагає повторного game-economy research; зміна economy odds вимагає simulation, disclosure й purchase/UX checks навіть без коду gameplay.

## 4. Режими запуску

- **New:** intake → critical decisions → stage routing.
- **Resume:** current checkpoint + input/lock verification → next incomplete task.
- **Audit:** inspect artifacts against requirements; findings cannot become independent QA of newly self-authored repair.
- **Repair:** bounded defect set → affected acceptance only.
- **Handoff:** verify files/hashes/studio carry-forward and next invocation.
- **Release:** demand observed ready candidate and real external authority; do not manufacture credentials/certificates/store record.
- **Liveops:** scope time window and desired action; use separate scheduling mechanism for future recurring execution.

Одночасно відкривати лише потрібний режим. Директор не читає всі GDD, усі assets і всі logs щоразу; шукає потрібні IDs та докази.

## 5. Негативні приклади

- «R06 рекомендував parkour, отже починаю її реалізацію» — потрібне actual user selection/current package.
- «Mac skill є, отже web Work теж її бачить» — потрібний inventory/capability check.
- «Зробив png екран, він гарантує точну гру» — потрібні specifications + real runtime comparison.
- «Не можу зібрати iOS тут, отже завершив обидві платформи» — Android evidence і iOS blocker окремо.
- «Кожен reviewer переглядає весь архів після зміни одного рядка» — застосувати dependency impact.
- «Плагін встановлено, бо є zip» — окремі package-prepared та cloud-installed результати.
