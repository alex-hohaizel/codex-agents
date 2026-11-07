# Намір, touch, камера, UX, відгук і метагра 4.0

## Навігація

1. Повний шлях гравця
2. Input і camera contracts
3. Навчання, доступність, presentation
4. Метасистеми й commerce
5. Приймання та джерела

Завантажити для задуму, будь-якої взаємодії, представлення стану, навчання, reward/shop/payment/return. Продуктова глибина не вимірюється кількістю кнопок, HUD bars, систем або товарів. Підбирати доречні засоби конкретній грі й перевіряти складну реальну ситуацію.

## 1. Покрити весь шлях гравця

Створити state atlas: launch/first run, consent за обсягом, profile/load/recovery, settings, onboarding/practice, gameplay, pause/interruption, fail/retry/abandon, reward/equip/upgrade, progression/world navigation, conditional shop/purchase/sync, return/reorientation, completion, support. Для кожного entry/exit/guard, allowed inputs, side effects, commitments, failure states, timeouts, save й return target.

Short/normal/long session мають minimum meaningful action, safe pause/exit і continuation policy. Телефонне переривання не означає abandon автоматично. Після реальної перерви повернути мету/комплект/контекст і суттєві зміни без повтору всього tutorial. Підказка дослідницькій грі не повинна силоміць розкривати рішення (D1Q08,Q15).

Commitment table розрізняє preview→commit→apply→irreversible boundary→recovery для дії, crafting, respec, route, story choice і purchase. Скасування до й після commit має різну точну семантику. Не додавати confirmation modal на кожний клік без причини.

## 2. Розділити чотири input моделі

| Модель | Потрібний зміст |
|---|---|
| Намір | Що гравець хоче зараз: move/aim/guard/choose/cancel |
| Ігрова дія | Eligibility, states, costs, commitment, time, outcome |
| Recognition | Pointer ownership, zone/gesture/threshold, state/competition, cancel |
| Presentation | Visible/temporary cue, affordance, preview, feedback; реальна invite-to-action |

Не використовувати одну стандартну схему для всіх ігор. Порівняти доречні профілі на першій дії, піковій і late складній ситуації. Якщо profile вимагає пряме dynamic control, не підміняти його відкладеним вибором/готовою анімацією; застосовність вивести з джерел поточного проєкту.

Input contract: supported device/orientation/grip/handedness, safe area/system edge gestures, contact count, stable pointer IDs, ownership acquire/release, zone capture, physical/logical threshold units, deadzone/curve/hysteresis, sensitivity, tap/hold/drag/swipe recognizer, gesture competition/priority, preview/commit/cancel, input buffering, remap, exit zone, second finger reorder, focus loss, modal handoff, pause/resume, saved settings й traces.

UI hit testing і gameplay contacts мають ownership. Дотик, що відкрив магазин, не може «провалитися» в покупку; старий hold не лишає газ після system cancel. Втрата другого пальця не змінює власника steering. Не спиратися на pressure, якого немає на цільових телефонах.

Для аналогового drag точно задати origin/floating origin, deadzone, нормалізацію, transfer curve, max, recenter/release і touch occlusion. Намальовані стрілки не повинні виглядати двома кнопками, якщо модель очікує continuous drag. Для complex sword interaction розділити preview/commit/contact/cancel, щоб correction guard не стала атакою або старий gesture у новому state не став новим прийомом.

### Camera request policy

Camera contract: projection/angle/follow, subject scale у кадрі, visible action horizon, deadzone/lookahead/zoom bounds, occlusion/collision, motion/acceleration limits, zones/transitions/cut, aim/interaction/boss requests, owner/priority/tie-break, blend/release/return, hysteresis й comfort alternatives.

Масштаб персонажа визначати механікою/читабельністю/стилем; не тримати весь світ у кадрі за замовчуванням. Camera movement, scene transition і маршрут мають бути показані в концепті. Одночасні requests не можуть стрибати між owners або перевертати touch direction без правила.

Надати trace: tick/input/recognizer state/intent/action/camera request/owner/transform/cue. Вимірювати input→recognition→simulation→render/present→screen на actual targets;60FPS не доводить one-frame latency або tactile comfort.

## 3. Побудувати навчання, feedback і доступність

Для кожної механіки: discover→understand intent→execute input→see result→safe practice→transfer→combine→late reinterpretation. Визначити what player knows, affordance/cue, goal, opportunity, evidence of mastery, retry/remediation і skip/relearn. Не створювати довгий текст замість інтерактивної практики.

Learning diagnosis table розрізняє unnoticed opportunity, misunderstood rule, unknown input, misrecognition, timing error і deliberate experiment. Правильна альтернативна стратегія не є tutorial failure. Evidence→remediation не є психологічним профілюванням гравця (D1Q07,Q10).

Failure feedback пов’язує information-before-event, доступні responses, actual action, cause/outcome, lost/retained, next meaningful step. Відділяти брак знання/виконання від technical defect. Не пояснювати промах текстом «недостатньо сили», якщо hit був rejected через range.

### Мультимодальний словник і attention

Semantic dictionary визначає meaning, invariant visual/audio/haptic cues, permitted stylistic variation, forbidden ambiguity, novice/late examples і alternative channels. Новий biome/art не змінює вивчене «можна чіплятися» на небезпеку без навчання. Різні концепції мають різні художні мови, не лише різний palette.

Event/state matrix пов’язує ID/predicate із animation/VFX/UI/SFX/haptics, priority, timing domain, dedup key, duration/start-update-end, source/location/intensity, suppression/aggregation/defer, stale expiry і alternative mode. Один physics manifold не запускає SFX на кожну точку. Hit feedback використовує simulation outcome; durable reward cue має іншу межу.

Attention policy визначає concurrency, critical precedence, ducking, clutter/flash/motion limits і fallback. Test peak scene: danger+objective+reward+critical resource, слабший profile, finger occlusion, muted/no-haptic modes. Deferred cue не виглядає новою актуальною загрозою (D1Q03,Q11,Q13).

### Стиль, асети й localization

На C1 поелементно визначити silhouette, proportions, scale, palette/contrast, material/texture language, edges/shading/light, environment composition, character/equipment/UI/VFX, animation timing, camera relation; sound palette/motifs/mix/feedback. Обґрунтувати achievable 2D/3D pipeline й presentation fidelity. Generated concept image не доводить editable layers, rig, native performance чи production source.

На T кожен важливий gameplay state/transition має asset/audio/haptic mapping, exact marker/timebase, collision/pivot/attachment, import/export, budget й test scene. Health/heat/guard/durability не копіювати однаковими bars: спосіб показу випливає з decision frequency/urgency/precision; простий лічильник допустимий з обґрунтуванням.

Localization contract: stable string IDs, context/speaker, placeholders/types/plural/select, glossary, number/unit/currency/price formatting, font/glyph/license/fallback/shaping, text scaling, subtitles, RTL за мовним scope. Text change не змінює save ID чи формулу. Long strings не приховують price/cancel; псевдомова не доводить підтримане письмо (D1Q12).

### Assist semantics

Альтернативи жестам/довгому hold, zones/sensitivity/handedness, vibration/audio/motion/text options мають зберігати meaningful actions. Settings доступні без складного gesture, який користувач змінює. Інформація не лише одним кольором/звуком/вібрацією.

Assist record визначає intervention, які decisions збережено/змінено, rule/time/resource effect, switching, save, compatibility, score/competition за обсягом. Не карати фізичну доступність універсальною втратою rewards. Скорингові наслідки показати до участі; assist toggle не reset витрату/claim (D1Q06).

## 4. Проєктувати commerce як частину метасистем

Почати з player needs/loops і оцінити доречні моделі: premium/unlock, expansions/content, cosmetics/identity, functional ready sets, capacity/convenience, memberships/meta services, capped extra opportunities/rewarded ads, deterministic currency/seasonal structures за задумом. Не розмножувати один skin offer між усіма кандидатами; не додавати всі моделі кожній грі.

Затверджені default decisions: functional paid sets можуть давати time/options/power advantage за доречності; ефект чесно обчислити й обмежити; competition окремо. Детерміновані покупки default; earned RNG прозорий; paid RNG потребує окремого явного рішення. Hidden success/purchase-based difficulty adaptation не є default. Network/backend/new recurring costs активуються лише проєктним рішенням.

### Порівняти paid і earned системи

Для кожного offer вказати target need і metaloop, components/compatibility, complete usable result, доступні earned routes, time/resource/risk distributions, prerequisites, power/option/time delta, restrictions, caps/expiry, partial ownership, duplicate/overflow, upgrades/respec, recovery і content lifetime.

Ready kit може завершувати задачу, яку гравець довше складає з earned частин; не обмежувати його випадковим окремим `+stat`. Водночас порівняти цілий портфель товарів: разом вони можуть прибрати всі задумні weaknesses. Sum item scores не доводить portfolio balance.

Opportunity/attempt boosters визначають cap, refresh/calendar, earned/purchased limits, stacking, duration, timezone/offline, failed run, ad no-fill і unspent value. Extra opportunity не є unlimited attempts за замовчуванням. Для member benefit після expiry визначити access/read/use/overflow; не руйнувати inventory через завершення періоду.

Economy contract: sources/sinks, currencies/units, authority, caps/inflation, production/repair/transfer, rewards/duplicates/pity, baseline cohorts/policies, early/late/completion states, time-to-goal distributions, expected vs tails, sensitivity і exploit cycles. Не видавати simulation за revenue. Фінальні store policies/regions/age scope перевірити актуальними офіційними джерелами перед release.

### Shop journey і платежі

Offer discovery→зрозумілий preview/result→local/store price→eligibility/ownership→confirmation/platform sheet→pending→verified success→idempotent grant→durable record→store acknowledge/finish за actual SDK→reconciliation. Точний порядок визначає platform contract, не загальна схема.

Покрити loading/empty/offline/unavailable/parental decline/cancel/deferred/pending/unknown outcome/failed/granted/already owned/partial bundle/refund/revoked/restore/account switch й повторні callbacks. Не показувати success до відповідної authority/durable boundary. Store token не пишеться в public logs; client `owns=true` не є authority.

Задати canonical product/offer IDs, store mappings, country/currency/price source, validation authority, operation/grant dedup keys, consumable/nonconsumable/lease semantics, partial-set price/compensation, refund effects, offline projections, rollback/migration й support evidence. Local economy й real-money transaction не змішувати непомітно.

Store purchase restore не тотожне cloud progress restore. Consumed item не видається знову зі старого snapshot; refunded access не воскресає через merge. External dependency failure має deadline/bounded backoff/cancel/reconcile/fallback; no-fill/cloud/store timeout не заморожує локальну гру (D1Q34).

### Умовні спільна гра й поширення

Якщо прийнято co-op/competitive scope, задати lobby/join/leave/disconnect/rejoin, authority, participant ownership, input/latency envelope, shared/individual progress/rewards, pause/assist/score і conflict recovery. Не переносити NPC coordination як готовий multiplayer protocol. Якщо network scope відсутній, не додавати сервер заради D1Q17.

Якщо прийнято sharing/UGC scope, визначити capture/export contents, rights, privacy/hidden knowledge, naming/locale, size/format/compatibility, cancellation, safe import й user intent перед зовнішнім поширенням. Screenshot/replay не повинен включати payment token або private account data. D1Q18 не є автоматичним дорученням публікувати чи надсилати будь-що.

## 5. Приймання

Consumer відтворює зі специфікації first/peak/late/return/completion, failed input/cancel, failure/recovery й conditional purchase без додумування. Окремо перевірити модель→visible invitation→real action: drag не виглядає двома buttons; tap/hold/swipe не змінюються непомітно в новому state.

Негативні fixtures: reordered pointers; edge gesture/cancel/focus loss; stale contact у modal shop; aim+boss+zone camera; guard correction interpreted as attack; inaccessible settings; blocked critical cue; wrong tutorial remediation; long localized price/cancel; completed collection reward; paid portfolio dominance; pending timeout+retry grant; partial bundle+refund+cloud old save.

Human evidence: реальні task, device/profile, participant scope, observed errors/occlusion/fatigue/understanding і limits. Документальний review/input trace не доводить комфорт. Native build не доводить магазинний sandbox; configured analytics не доводить actual data egress або revenue. Scope status зберігати окремо.

## Первинні джерела

Методики адаптовано з P1/D1/D2, джерела досліджено2026-11-02. Ці приклади не є гарантією нашого успіху або вимогою копіювати систему. Actual SDK/політику/price/capabilities перевіряти перед використанням.

- Android multitouch, stable pointer IDs: https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi
- Microsoft XAG107 input: https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
- Microsoft XAG108 difficulty: https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/108
- Microsoft XAG103 additional channels: https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103
- Android localization: https://developer.android.com/guide/topics/resources/localization
- Warframe Prime Access, ready functional set example: https://support.warframe.com/hc/en-us/articles/200092159-Prime-Access-FAQ
- ESO Plus, metabenefit lifecycle example: https://help.elderscrollsonline.com/app/answers/detail/a_id/26343/kw/plus
- Steam bundles, partial ownership semantic example: https://partner.steamgames.com/doc/store/application/bundles
- Play Billing lifecycle: https://developer.android.com/google/play/billing/lifecycle
- Apple StoreKit transactions: https://developer.apple.com/documentation/storekit/transaction
