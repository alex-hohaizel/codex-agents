# Оновлення персонального набору Work / Codex

Зміст: scope → manifest → audit/apply/verify → відновлення → межі доказу.

`scripts/update_skill_suite.py` — stdlib helper для **точно 33** персональних
навичок. Він не публікує Work, не виконує продукт, не змінює `AGENTS.md`,
конфігурацію Codex, ролі, системні навички або plugin caches. Повне збереження
персональних Work-навичок лишається штатною операцією відповідного середовища.

## Manifest комплекту

Корінь комплекту містить `manifest.json` і `skills/<stable-name>/...`.
Формат — `atelier.skill-suite/1`, поля:

- `suite_id`: непорожній ідентифікатор перевіреного комплекту.
- `skills`: список рівно 33 унікальних поточних stable names із allowlist helper.
- Кожний запис: `name`, `version`, `files`, необов'язковий `previous_trees`.
- `files`: словник POSIX relative path → `{sha256, size, mode}`. `mode` — ціле
  POSIX permission значення, наприклад 420 для `0644`, 493 для `0755`.
- `previous_trees`: список `{tree_sha256, source}` відомих перевірених
  попередників. Це approved source bindings комплекту, а не довільний hash,
  який можна дописати лише щоб обійти встановлену невідповідність.

Для нового узгодженого релізу додати top-level
`visual_identity_policy: "preserve-existing/v1"`. Це вмикає збереження
наявних локальних іконок, їхніх `icon_small`/`icon_large` і `brand_color`.
Manifest лишається `atelier.skill-suite/1`; старі комплекти без цього
поля зберігають попередню строгість повного tree hash.

Щоб допустити локальну косметичну відмінність від перевіреного попередника,
його запис `previous_trees` додатково має `files` — повний канонічний file
manifest попередника без volatile caches — і `ui_yaml`, точний UTF-8 текст
його `agents/openai.yaml`. Helper звіряє logical hash, YAML bytes/size і
file records. Брати ці дані з фактично перевіреного попереднього релізу;
не оголошувати невідомий drift канонічним лише для обходу перевірки.

## Збереження візуальної ідентичності

Audit порівнює функціональну частину з канонічним новим або явним попереднім
baseline. Дозволена відмінність обмежена трьома полями `interface`:
`icon_small`, `icon_large`, `brand_color` та bytes/modes їхніх локальних
image assets. Решта YAML, включно з prompt, policy і dependencies, та всі
інші файли мають відповідати відомому джерелу. Видима нова версія береться
з канонічного нового `display_name`; заморожені іконки не перегенеровуються.

Підтримувані icon assets — відносні шляхи всередині `assets/` з image
suffix `.svg/.png/.jpg/.jpeg/.webp/.gif/.ico`. Відсутній файл, зовнішній шлях,
traversal, symlink, special file, case/Unicode або file/directory collision
блокують оновлення. Icon pointer не може приховати зміну скрипта, policy
або іншого неіконкового файла будь-якого оголошеного baseline. Малий і
великий варіант можуть посилатися на один і той самий image asset.
Історичний одиничний префікс `./assets/…` нормалізується лише для file lookup;
точні рядки `icon_small`/`icon_large` зберігаються. Подвійні `././`, traversal
та довільні альтернативні форми шляху лишаються blocker.

YAML reader навмисно обмежений одиничними скалярними visual fields у plain
`interface` mapping. Інші поля зіставляються з точним baseline, без запуску
загального YAML parser чи виконання тегів/anchors. Неочікувана зміна
форматування інших полів може вимагати окремої звірки; вона не є дозволом
ігнорувати функціональний drift.

Audit записує `visual_preservation` і effective `desired_files` окремо від
канонічного manifest. Apply повторно перевіряє binding, робить повну копію
дерева, а icon bytes бере лише з перевіреної копії. Новий код та інструкції
встановлюються з комплекту. Журнал містить точні before/after hashes;
rollback повертає попередній YAML, іконки, решту дерева й modes.

Для доведення незмінності локально налаштованих іконок verify потребує
**точного завершеного apply journal**. Перевірка лише поточного файла не
доводить, що це та сама іконка, яка була до оновлення. Не підставляти старий
журнал іншого комплекту, destination або незавершеної операції.

Різні візуальні ідентичності персональних дублікатів не об’єднуються
автоматично. Спочатку звірити обраний canonical target; варіант із відмінними
іконками не можна тихо прибрати через `--retire-known-duplicates`.
Проєктні агенти не входять у цей 33-core installer; їх оновлення й
відокремлений visual style проходять явний project-local adoption.

Логічний tree hash: SHA-256 UTF-8 послідовності відсортованих рядків
`relative_posix_path + NUL + file_sha256_hex + LF`. Із логічного hash вилучені
лише `__pycache__/...` і `.DS_Store`. Повний передопераційний snapshot і backup
зберігають **усі** файли, порожні каталоги й permission bits, включно з кешами.
Інші невідомі файли не ігноруються. Шляхи з traversal, symlinks, special files,
case/Unicode collisions або непередбачені bytes комплекту відхиляються.

Спосіб розпакування ZIP може змінити mode вихідних файлів. Helper перевіряє
їхні bytes/size/path, потім явно встановлює й перевіряє declared **target** modes.
Спеціальні permission bits не підтримуються.

## Audit → apply → verify

З кореня готового переносного комплекту, якщо helper покладено в `portable/`:

```bash
python3 portable/update_skill_suite.py audit --kit . --plan ../skill-update-plan.json
python3 portable/update_skill_suite.py apply --plan ../skill-update-plan.json
python3 portable/update_skill_suite.py verify --kit . --journal /absolute/backup/run-ID/journal.json
```

За замовчуванням target — `~/.agents/skills`, додатковий personal discovery
root — `~/.codex/skills`, backups — `~/Codex_Skill_Backups`. Назви коренів можна
передати явно через `--destination`, `--legacy-root`, `--backup-root` у `audit`.
Backup root і plan мають бути поза skill-discovery roots. `audit` без `--plan`
лише друкує JSON і не створює installation/backup directories.
У `verify --journal` передати фактичний `journal` із результату завершеного
apply. Для канонічної установки без локального visual overlay звичайний
`verify --kit .` перевіряє bytes, але не заявляє continuity без receipt.

`apply` споживає точний `--plan`: повторно перевіряє комплект і всі зафіксовані
target snapshots. Невідомий локальний drift, нове ім'я в зайнятому canonical
target або зміна після audit дають blocker. Загального `--force` немає.
Кожна змінювана навичка має повну перевірену копію до заміни. Новий payload
готується поза discovery roots; заміна дерева виконується rename на тому самому
filesystem і фіксується в journal. Це per-skill transaction із відновленням,
а не атомарна транзакція всіх 33 навичок чи гарантія відмовостійкості диска.
Потрібний ексклюзивний контроль обраних source/target ancestors на час операції.

Фактично незмінні canonical targets — no-op. Повтор застосування вже
завершеного plan не створює друге оновлення, якщо його targets залишилися
точно такими, як записано в receipt. Після подальших змін потрібно новий audit.

## Дублікати й межі пошуку

Пошук читає frontmatter без припущення, що назва каталогу дорівнює stable name.
Перевіряються безпосередні skill entries у personal roots; системні/приховані
каталоги не обходяться. Невивчені symlinks у discovery root блокують audit,
бо helper не може підтвердити scope без переходу за посиланням.

Додаткові `--project-root /absolute/project` показують дублікати у його
`.agents/skills` і `.codex/skills` як **report-only**. Проєктні файли й довільні
вкладені source kits автоматично не переносяться та не видаляються.

Відомий personal duplicate можна включити в точний plan повторним audit з
`--retire-known-duplicates`. Для цього його logical tree має збігтися з новим
або одним із перевірених `previous_trees`. Копія повністю зберігається в backup,
після чого прибирається з активного personal discovery root. Unknown duplicate
і project duplicate лишаються blocker; їх не перезаписують і не підміняють N/A.

## Переривання й rollback

Результат apply містить точний `journal` у backup `run-.../journal.json`.
Якщо виконання почалося й впало, journal додається також до JSON error.

```bash
python3 portable/update_skill_suite.py apply --plan ../skill-update-plan.json --resume /absolute/backup/run-ID/journal.json
python3 portable/update_skill_suite.py rollback --journal /absolute/backup/run-ID/journal.json
```

Resume перевіряє той самий plan і комплект, спостерігає фактичні дерева та
відновлює лише однозначні фази backup/preparation/old move/new install.
Active lock не обходиться; stale lock відновлюється лише для того самого
operation/plan на тому самому host після перевірки, що попередній PID відсутній.
Інший host, живий/reused PID або неоднозначний стан блокують автоматичний повтор.

Якщо процес припинився після створення lock, але до першого `journal.json`,
точний operation path можна прочитати з `backup-root/.skill-suite.lock`.
Та сама `apply --plan ... --resume <operation>/journal.json` відновить початок
лише за збігу plan/lock, відсутності живого PID, незмінності всіх audited targets
і комплекту та відсутності невідомих operation/staging даних. Невідомі файли не
видаляються; неоднозначний missing-journal випадок потребує ручного звірення.

Rollback спершу перевіряє конфлікти всього набору та цілісність потрібних backups.
Післяопераційні зміни користувача не перезаписуються. Потім відновлюються точні
попередні дерева й modes або прибираються нові targets, яких раніше не було.
Перерваний rollback можна продовжити тією самою командою, коли стан однозначний.
Unknown state спершу звіряється, а не стирається новим operation ID.

## Що доведено після verify

`verify` перевіряє placement, bytes, modes, stable names і personal duplicates.
З `--journal` він додатково звіряє effective payload і збережені visual
identities, окремо повертаючи `canonical_core_verified`,
`visual_preservation_verified` і список `preserved_visual_identities`.
Його результат явно має `runtime_discovery_verified=false` і
`behavior_verified=false`. Наступний крок у **фактичному** Codex host — оновити
каталог/відкрити свіжу сесію, звірити resolved source і виконати погоджені
bounded interaction scenarios. ZIP і зелений hash-check не є встановленим
production продуктом, прийманням власника або доказом native/device/provider дій.
