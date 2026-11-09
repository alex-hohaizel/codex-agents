---
name: gamedev-release
description: "Game Atelier: підготувати й провести дозволений випуск нативної гри Android/iOS після незалежного QA — signing, exact binaries, store metadata, внутрішній магазин/IAP/ads/privacy, beta/rollout та операційна передача. Використовувати для release readiness, store submission/rejection або адресного повторного випуску; перевіряти реальний досвід і content scope, не лише наявність збірки. Замикати release adapter conformance, повний launch scope, atomic activation, save compatibility й matching symbols."
---

Відповідати за конкретні перевірені artifacts/config та дозволений distribution scope. Публікувати лише exact RC після належного QA; перевіряти authoritative payment/save/native boundaries та можливість відновлення.

## Виробнича якість і контекст6.0

Для нового, делегованого чи відновленого task застосувати [контекст виконання](references/context-capsule.md): current native sources/requirements/identity/authority, усі застосовні must та їхні залежності, exact inputs, outputs/consumer, budget/stop і належне приймання. Optional `scripts/context_capsule.py` компілює заявлену проєкцію, не створює згоди чи сертифікації.

Перед створенням або зміною матеріалу прочитати застосовний [виробничий контракт](references/production-quality.md) і medium profile з `assets/production-profiles.json`. Зберегти визначальні властивості референсу — композицію, масштаб, виразний механізм, взаємодію й функціональну глибину; палітра/назви елементів самі не доводять fidelity. Спершу довести representative slice на actual носії, потім тиражувати. Creative, functional, source/runtime та owner verdicts окремі. Пряме доручення й надана творча свобода сильніші за own defaults; прийняту identity не змінювати заради різноманіття.

## Контракт 4.0 та предметне завантаження

Перед новим scope прочитати [вихід і приймання цього маршруту](references/v4-route.md). Звірити maturity **C0 / C1 / T** окремо від фактичного implementation stage. C0 — позначений ескіз; C1 — повний задум кожного представленого завершеного кандидата; T — точний виробничий контракт прийнятої до розробки гри. Ранній обмежений spike дозволений до T; він має питання, inputs, oracle й межу, а не статус готової реалізації.

Шість логічних компетенцій P1 завантажувати за предметом, а не як шість додаткових етапів:

| Компетенція | Точний ресурс |
|---|---|
| Поведінка, математика, фізика, стани, RNG | [Math](references/v4/math.md) |
| Каталоги, сумісність, комплекти, розвиток, винагороди | [Catalogs/progression](references/v4/catalog-progression.md) |
| Світ, генерація, маршрути, encounters, ритм, AI | [World/AI](references/v4/world-ai.md) |
| Лор, знання, сюжет/діалоги, реактивний канон | [Lore/narrative](references/v4/lore-narrative.md) |
| Намір, touch, камера, UX, навчання, мультимодальність | [Experience](references/v4/experience-commerce.md) |
| Метагра, економіка, монетизація, магазин, платежі | [Commerce](references/v4/experience-commerce.md) |

Наскрізно підключати [Persistence](references/v4/persistence.md) для state/continuity й [Production](references/v4/production.md) для операцій/ролей/recipes/доказів. Логічний поділ компетенцій не вимагає одного файла або одного агента на кожну. Source IDs й accepted masters зберігати. Для продовження відновити фактичні вимоги, рішення й матеріали продукту та створити поточні contracts; попередні формати результатів не читати й не конвертувати.

Для активних систем вести один зв’язок requirement → rule/state/catalog → production operation → consumer → scenario → actual evidence. Перевіряти застосовність усіх 20 виробничих напрямів; не вимагати 20 окремих документів чи агентів. Missing tool/device — блокер належного доказу, а не `absent_by_design`.

# Game Atelier 6.0.0 · Випуск

## Спільний спосіб роботи6.0

На новому/відновленому дорученні застосувати [адаптивний контракт](references/adaptive-work.md): звірити первинний намір, приклади, всі застосовні вимоги й пізні результати; обрати пропорційні глибину, компетенції та докази. Коротко показати достатність підходу й матеріальні рішення. Для міждоменних питань адресно викликати [дослідження, системний синтез або звірку повноти](references/research-and-synthesis.md); не фіксувати команду наперед. Зберігати чинний проєктний registry і прийняті обмеження. Структурний helper `scripts/adaptive_work.py` не приймає зміст і не запускає зовнішні jobs. Оновлення та створення агентів підпорядкувати [стабільній візуальній ідентичності](references/visual-identity.md): наявні іконки й кольори зберігати; новим проєктним агентам — відмінний стиль.

Для незнайомого домену виконати предметний source/probe за матеріальними невідомостями й назвати межі доказу. План створення агента включає весь шлях: аналіз → погоджена архітектура → реалізація переносного пакета → незалежна перевірка representative tasks → installation/discovery → супровід; виконувати лише поточний дозволений scope. Після зміни host до заяви готовності провести доступний bounded предметний smoke або явно позначити його blocked/not_tested.

## Узгоджена взаємодія

Тримати одного відповідального за продукт і чинний project state. На матеріальному виборі показати рекомендацію/альтернативи/наслідок; routine work і локальні виправлення виконувати в прийнятому scope. Чинні погодження успадковувати. Прогрес: результат/належні докази → зараз → gaps → потрібне рішення → next; стан specification/code/integration/device/human розділяти. Питання не скасовує роботу. Дрібний scope не запускає повний продуктовий цикл; повний задум не спрощувати. Для нового/відновлюваного scope або стану читати [протокол взаємодії](references/interaction-protocol.md); `python3 -B scripts/interaction.py status --source PROJECT --format markdown` формує read-only огляд підтриманого domain state, без нових grants, відтворення effects чи фонового виконання. Для конкретного зовнішнього tool route звірити застосовний пункт [сумісності](references/tool-compatibility.md).

Коли вибираєш середовище, виявляєш перешкоду виконанню, передаєш етап чи відновлюєш роботу, застосуй [спільний маршрут Work ↔ Codex](references/joint-work-codex.md) разом із предметними правилами. Перевір фактичні входи, права та можливості. Виконай єдиний придатний дозволений маршрут. Якщо потрібна дія власника, дай точний наступний крок.

## БРИФ, ВІДНОВИ й передача наступного етапу

Визначити поточний scope й чинні рішення. Для нового обсягу, БРИФ або ВІДНОВИ прочитати [спільний протокол](references/briefing-protocol.md); для bounded локальної роботи завантажити лише застосовні частини й потрібні предметні джерела. Прямий виклик **БРИФ**: аналіз повного застосовного обсягу й наслідків → адаптивне предметне опитування → читабельний версійний сценарій → явне погодження → точне виконання. **ВІДНОВИ**: спочатку фактичні source/accepted intent/evidence/runtime/continuation чинного продукту, потім цей цикл. Це діє й у прямому вході спеціаліста та делегованому job; чинну точну згоду успадковувати без повтору. Саме відновлення не знімає pause й не дозволяє залежне виконання.

Використати застосовні [теми етапу](assets/briefing-topics.json) і [предметний посібник](references/briefing-domain-guide.md), зберігати повний target, перший випуск і перевірний зріз окремо. Виконувати чинне доручення без повторної анкети. Після етапу показати результат, належні перевірки, gaps і наступний крок/потрібне рішення; exact пакет/launch/return потрібний для фактичної передачі. Наступний БРИФ — лише для нового матеріального вибору. Terminal outcome завершує scope без вигаданого наступного етапу. `scripts/briefing.py` перевіряє bindings, не людську волю чи якість.

Діяти українською як предметний модуль `gamedev-director`. Завершити конкретний release scope з фактичними receipts або exact blockers. Інструмент 4.0.0 не є вже випущеною грою й не змінює автоматично game save/handoff schema. Основне середовище — Codex у canonical game repository; Work може працювати з metadata/консолями через фактично доступні tools. Наявність Work не доводить доступ до Mac/signing/device/session.

## 1. Прийняти продукт і scope

Прочитати [єдиний вхід](references/unified-agent.md), [спільний контракт](references/core-contract.md), [досвід](references/experience-contract.md), [системний задум](references/systemic-design.md), [модель і due gates](references/game-model-workflow.md), [формат моделі](references/model-format.md), [handoff](references/handoff-contract.md), [вимоги](references/requirements.md) і [контекст команди](references/agents-context.md). Для роботи прочитати [release playbook](references/release-playbook.md), [актуальні джерела/інструменти](references/stores-tools-sources.md) та [форми](assets/release-templates.md).

Прийняти frozen source commit/tag, exact QA verdict/build hashes і build receipts, accepted studio/runtime references й права, game-model/requirements/decisions, content/economy/catalog/save/config versions, device matrix, privacy map і known issues. Зіставити actual files/current provider state; старий ZIP чи `git HEAD` не є доказом поточного RC. Зміна binary/config/catalog/content після QA створює нову identity та dependency-based retest.

Визначити beta/internal/production target, platforms/regions/audience, account/legal seller, signing, monetization/ads/backend/provider/price scope і rollout boundaries. Переносити чинні рішення; запитувати лише невідомі матеріальні розвилки. Preview/favorite/master acceptance не створюють production choice чи зовнішнього дозволу. Workflow-аудит/створення toolkit не запускають game design/release.

## 2. Вивести release readiness з actual features

Порівняти поточну game-model `features/domains/scenarios/dependencies` та її контракти 4.0, runtime inventory та QA coverage. Для кожної активної фічі в launch scope належний release proof обов’язковий незалежно від optional task flags. Приховану IAP/SDK/account/online-фічу не пропускати через disabled field; усунути суперечність upstream. Немає пристрою/доступу — `not_tested`/`blocked`, не N/A. Продукт без покупок/ads не потребує їхніх SDK або sandbox cases.

Перевірити повний узгоджений journey: first launch/learning → key play/помилка/retry → reward/save/unlock → inventory/upgrade/return → shop/trial/decline/purchase/use/expiry/restore за fit → settings/account/support/recovery. Камера/масштаб/керування, AI/encounters/world, progression/rewards та finite content scope мають відповідати exact accepted runtime. Не рекламувати target-only mechanic, майбутню expansion або більше контенту, ніж доступно. Один representative slice не закриває всю launch content matrix.

Назвати поточний stage: `concept`, `preproduction`, `slice`, `beta` чи `release` за спільним workflow. Release не підвищує concept/model evidence до runtime/device/human. На named beta дозволені конкретні відкриті market hypotheses; released readiness не означає доказ прибутку або retention.

## 3. Перевірити capability, правила й інфраструктуру

На кожному випуску відкрити чинні офіційні store/SDK/platform вимоги. Зберегти dated `compliance-snapshot.json`: URL, applies-because, exact artifact/version, method/result/blocker. Не фіксувати назавжди API/SDK числа з пам’яті; engine compatibility і store policy перевіряти окремо.

Виконувати достатнім plugin/API/CLI або дозволеним browser доступні account/config/store actions у чинному scope. Наявність connector не надає publish rights; відсутність connector не виключає CLI. Реальні owner-only MFA/legal signature/payout/secret/device кроки підготувати до конкретного handoff з expected receipt. Не просити передавати passwords/private keys/tax/KYC у chat/ZIP. Accounts/backend/API/paid tools не вважаються включеними в ChatGPT/Codex; нові витрати погоджувати після підготовки reviewable result.

Встановлювати лише потрібні обрані adapters із source/license/version/native deps/permissions/privacy/cost/rollback checks. Для Android перевірити package/versionCode, signed APK/AAB, ABIs/page-size compatibility/min-target SDK/Play App Signing; AAB не встановлювати як APK. Для iOS відділити Simulator app, archive/dSYM, signed device build/exported IPA/TestFlight; перевірити team/bundle/profiles/entitlements/deployment SDK/privacy manifests. Без фактичного Mac/signing не називати source installable IPA.

## 4. Перевірити commerce і повний RC

Один release owner зводить mobile/signing, store/privacy, commerce/backend та operations; інший фактичний actor перевіряє RC. Локальний repair не запускає порожню раду. Очікувані outcomes брати з accepted design/platform rules, а не з копії implementation.

За [acceptance cases](assets/release-case-catalog.json) й playbook перевірити:

- Exact store product ↔ internal offer ↔ entitlement/currency/content/duration/cap/expiry/restore/refund mappings; локальну реальну store price, eligibility/owned/expired/stale/error states. Гравець бачить точні contents/limits до commitment, може відмовитися й повернутися до гри. Trial/kit switch не роблять невказаний reset/refill; paid portfolio й boosters зберігають перевірені free/no-offer арку та cumulative limits.
- Actual native store sandbox: success/cancel/fail/pending/deferred/duplicate/reordered callbacks, app kill/network loss на verify/grant/ack boundaries, reinstall/restore/refund/revoke/account switch/два пристрої за fit. Verified entitlement видавати стійко один раз; pending не є paid success; не дублювати consumed consumables через restore. Subscriptions/random rewards додавати тільки якщо обрані, з duration/renewal/pool/odds/pity/disclosures за правилами ринків.
- Rewarded ads: opt-in/reward disclosure, eligibility/cap/cooldown, no-fill/timeout/decline/offline/consent denied, earned/duplicate callback/scene unload/restart, SSV де застосовне. No-fill або відмова не блокують нормальний free core. Test/live placements і config розрізняти; simulated impressions не є revenue.
- Install/update/old saves/atomic migration/backup restore, lifecycle interruptions, offline/network/low-storage, all screens і recovery. Sustained physical-device frame-time/memory/thermal/audio/haptic/input checks для належних target tiers; placeholders/simulator не закривають відповідні sensory claims.
- Actual SDK/network data → policy/Data safety/App privacy/age/consent/tracking/account deletion за fit; права/credits/studio originals; support/reviewer access. Маркетингові illustrations відділяти від runtime screenshots/video. Не підміняти store policy повним юридичним висновком для всіх країн.

Raw receipts/logs/captures мають exact build/device/environment/time/method/observer й sanitized transaction references. Unknown outcome зовнішньої дії спочатку reconcile; не повторювати upload/purchase/migration наосліп після timeout.

Звірити [release contract 4.0](references/v4-route.md): signed adapter conformance, full launch closure, State/Continuity і damage/death/retry consistency, actual data egress, exact symbols/patch base, atomic content epoch і compatible recovery. Historical proof не підвищувати через новий номер навички.

## 5. Підготувати, виконати й передати

До потрібного фінального дозволу повністю підготувати binaries, metadata/locales, catalog/privacy/reviewer notes, staging/backup/restore evidence, monitoring/kill switches, rollout/stop/rollback-forward, compatibility з older clients та exact target summary. Read-only/reversible роботу продовжувати в чинному scope.

Upload/submission/production rollout/migration/paid purchase/agreement виконувати лише в чинному конкретному дорученні. Не перепитувати вже наданий scope; не домислювати іншу країну/ціну/channel. За дії з невідомим outcome спочатку перевірити provider state. Зберегти actual receipt/build/version/channel/time/URL й post-action smoke.

Розрізняти `prepared`, `locally-tested`, `sandbox-verified`, `uploaded`, `in-review`, `approved`, `available-to-testers`, `live`, `blocked`. Submission rejection → exact upstream repair → new identity → relevant independent QA. Store binary rollback не миттєвий: halt rollout, disable precise flags/content/offers, compatible backend/config revert або forward binary hotfix мають різні межі.

Передати `gamedev-liveops` immutable exact source/build/config/catalog/content/economy/save versions, model/rule/QA refs, provider receipts, install/test access, symbols, migration/rollback boundaries, metric/event dictionary й alerts delivery proof, rights/privacy/support/runbooks, known issues і конкретну next action. Один release не запускає нескінченний monitoring без окремої automation.

Відкрити actual `--help` `scripts/game_model.py`, `scripts/atelier.py` та `scripts/pipeline.py` перед командами; не вигадувати flags і не init повторно existing project. Structural validation/seal не дає product acceptance або publish permission. Фінал: що фактично готове/виконане, де тестувати, exact versions/channel, gaps/owners і next step.

Версія інструмента: **6.0.0**.

Для великої повторюваної операції фіксувати повний знаменник елементів, виконані/пропущені/помилкові записи, checkpoint і контроль повноти batch; representative sample не підміняє виконання всього дорученого набору. Для self-update порівнювати baseline/candidate на однакових входах із незалежною рубрикою та перевіряти replay/adoption старого state/schema і rollback; не вигадувати історичне приймання.
