# Release playbook

## Зміст
1. Input та decision gates
2. Studio/account readiness
3. Build receipts і native QA
4. Commerce, ads та backend adapters
5. Store metadata й privacy
6. Beta, launch, rollback
7. Handoff та критерії приймання

## 1. Input та decision gates

Потрібні: hash-locked manifest попереднього QA, git commit/tag, target platform/device matrix, accepted visual/runtime identity, assets/runtime import receipts, economy/catalog/save versions, test results для release candidate, studio master/subset з hashes, unresolved issues та risk decision. Якщо пакет має `blocked` або недоказану властивість, не підвищувати його до ready за наявністю красивого PDF.

Відкриті матеріальні рішення оформити `decision` із питанням, варіантами, рекомендацією, trade-off, affected requirements/files і залежною дією. Приклади: account personal vs organization впливає на seller/privacy/test requirements; offline vs online purchase authority впливає на fraud/cost/restore; Android-only vs dual-platform впливає на toolchain/asset budgets/signing; target age/countries впливають на ads/random rewards/legal review. Факт, що користувач навів приклад dual-platform, не є його вибором конкретної гри.

## 2. Studio/account readiness

Навичка виконує підтримувані studio/account/store actions достатнім наявним plugin/API/CLI або дозволеним browser у чинному scope. Для персональних MFA/legal/signature/payout підтверджень чи відсутніх прав передає лише точний blocked step з готовими полями/files, expected result і safe receipt return; перевіряє actual результат без витоку приватного:

### Google Play
1. Відкрити офіційний Play Console signup, вибрати відповідний account type, пройти legal identity/verification, fee та device verification якщо потрібна. Organization не обирати для маскування особистого seller.
2. Перевірити legal/public developer name, address/contact exposure, payments merchant, bank/tax readiness. У package лишити public identifiers і completion status; приватні реквізити — в належному provider account.
3. Створити app з approved name/default language/game/free-or-paid; package/application ID із studio namespace зафіксувати до першого upload. Назва бренду та юридичне ім'я — різні поля.
4. Визначити Play App Signing/upload key custody та recovery owner. Private key не додавати в git/ZIP. У receipt записати certificate fingerprint та secret reference, а не secret.
5. Налаштувати internal/closed test і tester management. Для applicable new personal account зібрати потрібний час/кількість реальних testers; симуляція та AI accounts їх не замінюють.
6. Підключити service account/API доступ лише якщо потрібний; мінімальні права, конкретний app, secrets у CI secret store.

### Apple
1. Вибрати individual або підтверджену legal organization. Apple individual seller відображає legal name; brand logo не змінює це правило. Organization enrollment може потребувати D-U-N-S/website/work email/authority.
2. Apple Account/MFA та особисті юридичні підтвердження власник завершує там, де потрібна його участь. Доступні інші account/config actions виконати в чинному scope; перевірити program/team, contracts/tax/banking перед продажем, ролі доступу.
3. Створити explicit App ID/capabilities; bundle identifier зі studio namespace, SKU та app record у App Store Connect. Пов'язати exact team із Xcode/project.
4. Налаштувати signing automatic або обґрунтований manual маршрут; documented secret custody/revocation. APNs/iCloud/Game Center capability лише якщо реально потрібні.
5. Створити sandbox testers/IAP products, TestFlight group, review contact/login. App Store Connect API key — optional і secret-store only.
6. Ручне завершення MFA/угод/платежів не підміняти автоматичним текстом «виконано».

Конкретні UI labels перевіряти у поточній консолі; не вимагати від користувача знайти застарілу вкладку. Якщо connector підтримує лише reads — передати manual exact field mapping.

## 3. Build receipts і native QA

`build-receipt` для кожного артефакту: source commit, dependency lock hash, engine+export templates, host OS/architecture, SDK/JDK/NDK/Xcode, build command/CI run, UTC timestamp, platform/ABI, application ID, version/build, signing mode і public certificate fingerprint, artifact path/hash/size, symbols path/hash, runtime config/catalog/content versions, tests та limitations.

APK: debug для швидкої установки; signed release APK для representative QA. AAB: publication format; локально не ставити через `adb install`. За потреби bundletool/device-specific APKs з перевіреного AAB; install proof не дорівнює upload acceptance.

iOS: Simulator `.app` тільки для simulator architecture/destination. Device build — окрема compile/sign/install процедура. `.xcarchive` — archive + dSYM; `.ipa` залежить від export method/provisioning. Для free Personal Team пояснити reprovisioning/обмеження; не використовувати це як TestFlight маршрут. Не архівувати локальні absolute credentials.

Release device QA мінімум: clean install, upgrade from supported previous save, cold/warm launch, interrupted launch/download, background/foreground, calls/audio interruptions, rotation/safe areas/device cutouts за підтримки, low memory/thermal/battery, airplane mode/network switch, restore, purchase pending/cancel/retry/duplicate, ad no-fill, sound/haptics options, text scale/accessibility, language/font coverage. Профілювати frame time p95/p99 і довгі сесії на minimum representative devices; середній FPS приховує stutter. Server smoke test проти exact candidate config. Якщо бракує пристрою, записати missing coverage та release impact.

## 4. Commerce, ads та backend adapters

Кожний provider adapter має `provider`, `version`, `license`, official docs URL/date, available SDK/tool route, host requirements, test credentials reference, live setup owner, recurring cost estimate/cap, data categories, permissions, regions/age restrictions, success/error contract, retry/idempotency, test fixture, rollback, uninstall/revoke steps. Не встановлювати десяток MCP/SDK наперед. Перший proof — мінімальна sandbox transaction/export на цільовому пристрої.

IAP catalog: internal product ID ↔ Apple product ID ↔ Play product/base plan ↔ type ↔ entitlement ↔ currency grant ↔ regional availability ↔ exact duration/expiry/restore/refund policy. Ціну брати з store API; не тримати постійний hardcoded `$1.99` у UI. Random reward: disclosure version/pool/weights/pity/caps до покупки, atomic draw + grant, audit record; free acquisition paths та power envelope затверджені у game design. Region-specific law не вгадувати.

Backend entitlement state machine: received → verified/rejected/pending → grant committed → acknowledged/finished. Grant dedupe, outbox/inbox за потреби, reconciliation, retry budget, failure queue/owner. Callback order і доставка повторюються; refund може прийти пізніше. Не давати безкінечну валюту за repeated webhook. Android token globally unique; orderId не universal id. Apple verification за signed transaction і належною chain/claims перевіркою через чинний SDK/API. Належне відновлення не означає повторну видачу спожитих consumables.

Ads: placement ID ↔ moment ↔ reward ↔ cap/cooldown ↔ consent ↔ test/live mode ↔ cancellation/no-fill/offline ↔ SSV/verification ↔ idempotent grant. Перевірити, що гравець може відмовитись і повернутися в зрозумілий стан. Тестові ad IDs не випускати як live setup, але production ad requests під час QA також не зловживати. Revenue telemetry не змішувати з simulated impressions.

Backend/service deploy: staging first, config validation, migrations dry run/backups/restore proof, least privilege, TLS/security headers за релевантності, request limits/cost caps, health checks, alerts, status page/support owner, region/data retention/deletion. Reversible flags не замінюють rollback DB migration. Код і public config у handoff, secrets у зовнішньому secret store.

## 5. Store metadata й privacy

Матриця `field → source file → locale → validation → console target → status` охоплює app title/subtitle/short description/full description/keywords/category/content ratings/screenshots/icon/feature graphic/video/support/privacy/marketing links/reviewer instructions/contact/login/availability/pricing/IAP descriptions. Exact accepted studio logo та attribution копіювати із studio master; не генерувати нову «схожу» версію.

Screenshots/video робити з runtime candidate і в правильних розмірах/locale; marketing illustration відділити. Перевірити readable HUD/touch controls, no debug overlays/test personal data, no unsupported feature claims. Перелік потрібних device sizes отримати з чинних store specs, не з пам'яті.

Privacy data inventory для кожного SDK/backend: data, purpose, collection/sharing/linkage/tracking, consent/lawful route, retention/deletion, destination/region, encryption, source evidence. Перевірити network/runtime behavior, permissions і manifest. Відображення Apple ATT тільки коли застосовне; відмова не ламає core game. Privacy policy і store disclosures мають узгоджуватися з реальною збіркою. Account creation → передбачити релевантне account deletion/guest upgrade/restore conflict; child-directed game → окремі age/ads/privacy вимоги до SDK та stores, не автоматично general audience.

## 6. Beta, launch, rollback

Порядок: local release candidate → internal beta → applicable closed/external beta → freeze exact RC → review submission → approval → staged production rollout → monitored expand. Конкретні %, тривалість і metric thresholds — рішення для гри/розміру вибірки; не копіювати універсальні числа. D1/D7 retention потребує реальних когорт і часу; release можна провести без вигаданих D7 результатів, із чітким планом.

Перед зовнішньою дією сформувати target/track/version/hash/build/config/store fields/price scope та permission evidence. Після — provider receipt і current state. Не приймати upload success за approval; approval за доступність у всіх регіонах.

Stop rules: crash/ANR regressions, purchase entitlement loss/duplication, save corruption, unacceptable input/audio/thermal issues, privacy mismatch, cost runaway. Mitigations: halt rollout, disable конкретний offer/ad/event, pin/revert content/config, rollback backend із сумісністю, hotfix binary forward. Store binary version downgrade користувачам загалом не є instant rollback. Backend/content має підтримувати старі active clients у compatibility window. Вимкнення фічі не повинно знищувати куплені entitlements.

## 7. Handoff та критерії приймання

`release-handoff` містить immutable prior package refs/hash, studio subset, exact candidate/build/store IDs, runtime configs without secrets, metadata/catalog/odds/privacy/license snapshots, install steps, test coverage/defects, deployment evidence, backup/restore, symbols/debug mapping, dashboard/alerts check, save/content/economy migrations, rollback/roll-forward, support/contact owner, credentials references, next action.

Ready-to-release: checks pass, remaining external approvals explicitly listed, no false published claim. Released: factual receipt + channel availability + post-action smoke. Support-ready: owner/runbooks/access/alerts validated. Якщо native toolchain, signing, реальні device tests або права відсутні — exact blocker і відтворювані кроки; не дописувати фальшиві receipts.

## Предметна release матриця 4.0

Перед release-review вивести required cases з actual features/current model/launch scope і dependency impact за `assets/release-case-catalog.json`. Каталог доповнюється product-specific journeys; жоден caller flag не скасовує належний proof. У QA release freeze має бути denominator всього launch content, screens/states, progression phases, offers і target platforms; representative slice не підміняє цей scope.

Пов’язати internal offer із product type, exact entitlement/content version, trial/earn path, local store price, duration/cap/overlap/expiry/restore/refund, UI entry/decline/use і ledger events. Для boosts/attempt budgets перевірити time skew, overlap/upgrade/expiry, restart/restore та cumulative portfolio; нічого не обнуляється/не відновлюється через switch без явного правила.

Store listing і reviewer instructions відображають реальний content/learning/return flow. Вказати finite launch scope й online/download dependencies чесно; future content не продавати як already included. Не робити live retention/revenue доказом до наявності фактичної когорти; реліз має відтворюваний measurement plan.

## 4.0 RC continuity й operational identity

Звірити full launch closure, exact signed adapter conformance, source/assets/config/catalog/content/save epoch, matching symbols і actual QA. Додати damage/death/crash/retry→reward→durable save cases, cold restore/golden migration/profile/account conflicts, ignored parameter/import semantics і assembly parity за feature.

Atomic activation має dependency closure/client compatibility/verified download/staging→activate або залишити старий coherent набір. Incremental patch має exact released base bytes/hash і permitted full fallback. Binary rollback не миттєвий; save schema може блокувати старий reader. Monitoring handoff містить actual source/query/alert delivery receipt або explicit unconfigured state, не обіцянку фонової роботи.
