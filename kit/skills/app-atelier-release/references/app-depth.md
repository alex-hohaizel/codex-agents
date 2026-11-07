# Виробничий контракт випуску App Atelier

Зміст: 1 — feasibility; 2 — release model; 3 — exact recipes; 4 — effect і recovery; 5 — evidence.
Читати cross-domain-core, workflow/acceptance/budget/data/evidence. `assets/app-depth.templates.json` — шаблон release packet, не дозвіл чи виконаний deploy. Чинні особисті prerequisites перевірити за первинними джерелами на момент залежного рішення.

Для наскрізних app-specific контрактів застосувати [модель систем застосунку](app-system-contract.md); її requirements/state authority не дублювати.

## 1. Ранній feasibility та production coverage

До significant build встановити всі потрібні класи операцій: Android build/package/install/distribute, iOS archive/sign/export/install/submit, web build/hosting/domain/TLS, backend/data migration, support channels, billing/entitlement, listing/privacy, diagnostics/monitoring. Conditional сервіси/витрати обрати за потребою; відсутній SDK/account не позначати N/A.

Для кожної операції назвати exact target/platform/region/channel, host/toolchain, account owner/organization, права, recurring/one-time/variable costs, data flows, mandatory testing/legal prerequisites, output/consumer і належний proof. Перевірити factual capability операції: доступний Mac/Xcode route для Apple, signing facilities, supported package type, actual remote build return. Загальний cloud або plugin не доводить ці можливості.

Зіставити no-human/zero-budget/platform/географічні обмеження з current store правилами до великих витрат. Протиріччя передати як concrete blocker і permissible alternatives; не скорочувати Android/iOS/web scope мовчки й не називати ботів required people. Existing approval достатнє в незмінному scope; unknown material choice не домислювати.

## 2. Зафіксувати release як узгоджене складання

Release candidate є bundle exact client/backend/support/data/config versions, build artifacts+hashes, resources/KB, environment bindings, product IDs і current QA. Не зливати source commit, build number, artifact hash і deployment ID. Кожний consumer має узгоджену версію API/schema/entitlement/policy. Single-platform pass не закриває три клієнти.

Для кожного state/API/schema поля назвати owner, version/compatibility, secret reference, data migration, downgrade/recovery limit, deletion/revoke fence і retention. Протокол roll-forward/rollback узгодити до dispatch. Старий binary не відміняє нову data schema, зовнішню покупку або видалення. Якщо rollback несумісний, потрібний forward repair/restore план із предметними межами.

Listings, screenshots, previews, support/privacy URLs і review instructions мають відповідати actual accepted candidate. Concept render не замінює screenshot працюючого продукту. SDK/privacy/billing/content декларації вивести з фактичних dependencies/data flows, не шаблонного «ми нічого не збираємо». Комерційні умови, taxes/fees і країни перевірити поточно, без універсальних цін із пам’яті.

## 3. Інстанціювати й перевірити recipes

Окремий recipe на clean build, native package/signing/export/install, submission, hosting/deploy, schema migration, post-release smoke і rollback. Bound inputs включають source/lockfiles/assets/config digests, pinned toolchain, target/account/channel, permissions, costs і expected outputs. Steps — exact argv arrays/API fields або numbered GUI procedure; критичні placeholder блокують лише залежний node.

Android AAB/APK/splits не взаємозамінні; назвати distribution та installation route. Apple archive/export/install/TestFlight/App Store — різні факти й операції. Web artifact origin/config/CSP/cache/service worker/API binding перевірити у фактичному URL; static landing не є web core. Native callbacks/permissions/billing/restoration перевіряються у потрібному runtime, не лише compile.

Перед кожним material parameter перевірити descriptor/schema/catalog, actual support і consumption. Signing material тримати в належному host secret facility, не chat/ZIP/source. Пакет містить тільки references/setup instructions, а не values. Production/test environment ізолювати; debug credentials, sandbox endpoints і sample data не потрапляють у final candidate.

Усі output hashes, logs/symbols/diagnostic mappings, provider receipts і read-back записати як actual evidence з author/observer/environment. Зберегти editable/source provenance та licenses. Validator manifest доводить bytes/refs, а не store approval чи production availability.

## 4. Виконати effect із надійним відновленням

До dispatch звірити current candidate hashes/parameters/target/cost і достатній чинний scope. Записати local pending attempt зі stable effect key; потім actual call; зберегти request/job/submission/deploy ID; reconcile status/output/cost; завершити receipt/read-back. Запис pending або поставлений job сам не є опублікованим результатом.

Timeout/втрата сесії означає unknown, доки authoritative перевірка не доведе результат. Спершу знайти submission/deploy/job за записаним ID; не дублювати upload/payment/migration. Provider idempotency перевірити фактично, local ledger не створює remote exactly-once. Cancel requested не дорівнює cancelled; unknown cost резервувати в cap до з’ясування.

Зміна artifact/SDK/store prerequisite/account/terms/permission/target відкриває залежне QA/authorization; незмінну чинну згоду не перепитувати. Два повтори тієї самої failure гіпотези змінюють діагностику чи route, а не породжують нескінченні submission loops.

Для особистих MFA/signature/legal/physical кроків завершити всю доступну підготовку й дати exact launch/return: verified path/URL, artifact hashes, minimal action, expected receipt і validation. Не просити секрет у чат і не перекладати весь setup на власника.

## 5. Прийняти фактичну доступність і передати operations

Окремо показати authored, built, signed, installed/device verified, submitted, approved, released, externally available та observed useful core. Store state й доступність у заявленому region/channel перевірити належним official read-back; web — actual URL/health/core/version; support — actual channels/auth/fallback. Неперевірене не маскувати successful command exit.

Post-release assembly проходить `fresh install/open → input → useful result → persistence → restart/resume → support` і conditional purchase/restore у дозволеному контурі. Production effects не створювати лише заради QA. Перевірити cold start, denied permission, network outage, old client/new backend і upgrade data. Physical properties потребують належного device proof.

Передати operations exact source/build/deploy/config/data versions, current signals/alerts, symbols, recovery/migration/rollback, cost caps, provider references, support/KB state, open risks і end-of-life obligations. Monitoring називати active лише після реального scheduler/service і alert proof. Чинні backups без actual restore не доводять відновлюваність.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: готовність точного артефакту, маршрут випуску, чинний effect scope, квитанції й фактична доступність. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: readiness окремо від дозволу, актуальні platform/account умови, migration/rollback і зовнішній read-back. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
