# Магазини, мобільні збірки, інструменти й аудіо — перевірено 2026-11-01

Це дослідницький матеріал для нового сімейства. Офіційні факти відокремлено від рекомендацій архітектури. Вимоги магазинів перевіряти заново перед кожним релізом; зберігати дату, URL, версію SDK та результат перевірки в `compliance-snapshot.json`.

## 1. Різні артефакти для тесту та публікації

| Платформа / мета | Реальний артефакт | Що ще потрібно |
|---|---|---|
| Android, локальна установка | debug APK або signed release APK | `adb install -r`, сумісний пристрій; не підміняти release QA debug-поведінкою |
| Google Play | signed Android App Bundle `.aab` | upload key, Play App Signing, versionCode, listing, декларації, реальні SDK |
| iOS Simulator | simulator `.app` та/або Xcode project, simulator destination | macOS, Xcode, відповідний simulator SDK; цей `.app` не встановлюється на iPhone |
| iPhone локально | device build через Xcode signing | Apple Account / Personal Team або paid team, provisioning, довіра/Developer Mode за вимогою пристрою |
| iOS distribution | `.xcarchive`; `.ipa` лише після належного export/signing | paid Apple Developer Program для App Store/TestFlight; provisioning/export method; build upload та review |
| iOS external beta | build у App Store Connect → TestFlight | beta metadata, перший external build проходить review, тестери встановлюють TestFlight |

Підтвердження AAB: https://developer.android.com/guide/app-bundle (відкрито).
Godot iOS/macOS/Xcode та renderer limitation Simulator: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html (відкрито). Godot stable вказує Compatibility renderer для Simulator; це не доказ поведінки на реальному iPhone.
TestFlight: https://developer.apple.com/testflight/ (відкрито).
Free Personal Team: до 10 App IDs, 3 devices, 3 apps/device, provisioning 7 днів за поточною сторінкою: https://developer.apple.com/help/account/basics/about-your-developer-account (відкрито). Не називати free signing повноцінним distribution.

## 2. Актуальні store gates

- Google Play new/update для звичайної мобільної гри: Android 16 / API 36+ з 31.08.2026. Target SDK і min SDK — різні речі. URL: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en (відкрито).
- Android native libraries / engine / ad/billing SDK перевіряти на 16 KB pages. Поточна сторінка каже, що оновлення без підтримки блокуватимуться з 01.02.2027. Не переносити старий дедлайн 2025 без перевірки. URL: https://developer.android.com/guide/practices/page-sizes (відкрито).
- Нові personal Play accounts після 13.11.2023: closed test із мінімум 12 testers, opted in безперервно 14 днів, далі заявка production access; це не автоматичний дозвіл. URL: https://support.google.com/googleplay/android-developer/answer/14151465 (відкрито).
- Apple з 28.04.2026: Xcode 26+ та SDK iOS26+; з 09.09.2026 upload app має target iOS13+. Deployment minimum не дорівнює build SDK. URL: https://developer.apple.com/news/upcoming-requirements/ (відкрито).
- Privacy, permissions, ads, IDFA/tracking consent, child/audience settings, account deletion за наявності акаунта, age rating, export compliance, third-party SDK disclosures та privacy manifests мають відповідати фактичному binary та backend. Не заповнювати декларації шаблонними «нічого не збираємо».
- Google Data safety охоплює також SDK: https://support.google.com/googleplay/android-developer/answer/10787469 (відкрито).
- Apple App privacy: https://developer.apple.com/app-store/app-privacy-details/ (відкрито). Privacy manifests/required reason APIs: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk (відкрито, HTML потребує JS; текст індексований official search).

## 3. Монетизація: store facts та рекомендований контракт

Apple/Google правила мають регіональні винятки для external billing. Базова реалізація digital goods — native StoreKit / Play Billing; не підміняти їх Stripe/вебпосиланням без перевірки storefront та entitlement. Apple куплена валюта не має спливати; відновлювані покупки потребують restore. Обидва магазини вимагають показувати ймовірності paid randomized items перед покупкою. Це правило магазинів, а локальні обмеження/вікові вимоги перевіряються окремо для цільових країн.

Офіційні джерела (відкрито):
- https://developer.apple.com/app-store/review/guidelines/ — 3.1.1, 3.1.2.
- https://support.google.com/googleplay/android-developer/answer/9858738 — payments, ціни, virtual currency.
- https://support.google.com/googleplay/android-developer/answer/18265346?hl=en — effective 29.10.2026, randomized-items odds.
- https://developer.android.com/google/play/billing/integrate — purchase lifecycle.
- https://developer.android.com/google/play/billing/security — verify token, PURCHASED vs PENDING, acknowledge, voided purchases.
- https://developer.apple.com/documentation/storekit/in-app-purchase — StoreKit verification/server notifications; HTML потребує JS, official search містить summary.

Рекомендований технічний контракт: catalog/version → price from store → user confirmation → pending/verified/rejected → atomic idempotent grant → acknowledge/finish → entitlement. Android dedupe за purchaseToken, не orderId; iOS за верифікованою transaction identity. Не видавати entitlement для PENDING. Визначити duplicate callbacks, restart між debit/grant/ack, cross-device restore, refund/revoke, chargeback, expired/cancelled subscription, offline retry, clock tampering, account migration. Покупки/винагороди/валюта — журнал операцій з atomicity та reconciliation. Sandbox покупки не є live revenue.

## 4. Вартість та вибір рушія

Публікація має обов'язкові зовнішні витрати, незалежно від підписки ChatGPT/Codex: Play $25 одноразово; Apple Developer Program $99/рік, регіональна валюта/податки можуть різнитись. Юридична організація Apple потребує legal entity/D-U-N-S/повноваження; особисте ім'я продавця не можна замінити брендом у формі individual.
Джерела: https://support.google.com/googleplay/android-developer/answer/6112435 (відкрито), https://developer.apple.com/help/account/membership/program-enrollment/ (відкрито).

Рекомендація, не універсальний факт: Godot як перший кандидат без royalty для 2D/стилізованої 3D, Unity як кандидат за значно сильніших потрібних mobile SDK/production workflows. Вибір тільки після representative device/export/plugin spike, а не за абстрактним «кращий рушій». Зафіксувати exact engine/export template/JDK/SDK/NDK/plugin versions і сумісність.

Godot MIT/commercial/credits: https://godotengine.org/license/ (відкрито). Stable Android recipe вказує OpenJDK17 та SDK35; він наразі відстає від Play API36 policy, тож його не можна копіювати як готовий compliance proof: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html (відкрито).
Unity Personal eligibility залежить від Total Finances за останні 12 місяців, поточний threshold $200k; не обіцяти «Unity безкоштовний завжди»: https://unity.com/pages/license-compliance (відкрито).

## 5. Реалістичний безплатний authoring pipeline

| Потреба | Кандидат | Що доводить приймання |
|---|---|---|
| 3D mesh, rig, skin weights, animation, LOD, collision exports | Blender | source `.blend`, export, scale/axes/units, material/shader conformance, deformation tests |
| 2D paint/texture/UI | Krita; vector editor за потреби | editable source, exact palette, licensed fonts, slicing/atlas/import settings |
| Composition/synthesis | доступний DAW + Surge XT / власні MIDI/stems | композиція і єдиний sonic palette; інструмент сам не гарантує modern premium quality |
| Record/edit/master/loop | Audacity, FFmpeg analysis | clean source, stems, seamless loop, peak/loudness report, on-device mix listening |
| Licensed coherent asset kit | Kenney CC0 / інші перевірені пакети | license-per-file, style adaptation, attribution, provenance; випадкова суміш пакетів не прийнятна |
| Runtime adaptive audio | Godot audio buses / AudioStreamInteractive або відповідник рушія | transition table, ducking, voices, interrupt/resume, latency, memory/device tests |

Krita commercial artwork: https://krita.org/en/about/license/ (відкрито). Blender artwork commercial: https://www.blender.org/about/license/ (official indexed; direct open returned 402, не підтверджено отриманням сторінки).
Audacity free/open source: https://www.audacityteam.org/faq/ (відкрито). Surge XT: https://surge-synthesizer.github.io/ (відкрито). Kenney asset pages CC0: https://kenney.nl/support (відкрито; цей дозвіл не поширюється на логотип Kenney).
Godot runtime: https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html і https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html (відкрито).

Suno free tracks призначені для noncommercial; оплата пізніше не дає автоматичної retroactive commercial license. Тому Suno не можна включати як обов'язкову безплатну production залежність. Якщо existing paid plan і права підтверджено — optional source із proof/license snapshot; потрібні stems/loop-edit та style QA. Немає доказу, що будь-який довільний безплатний генератор стабільно дорівнює Suno за якістю; такої обіцянки робити не можна.
Джерела: https://help.suno.com/en/articles/9601601 і https://help.suno.com/en/articles/2425729 (відкрито).

## 6. Haptics разом із музикою та візуалом

Підтверджена Android рекомендація — subtle/consistent, сила відповідно до важливості й частоти, predefined effects/primitives, co-design із візуалом/аудіо, fallback для різних актуаторів; тривалий buzzy fallback краще вимкнути. https://developer.android.com/develop/ui/views/haptics/haptics-principles (відкрито).
Apple official HIG: https://developer.apple.com/design/human-interface-guidelines/playing-haptics (відкрито, JS shell; official search підтверджує avoid overusing).
Рекомендований event schema: event ID → visual frame/phase → sound cue → haptic semantic pattern/priority → cooldown → device fallback → opt-out/accessibility. Перевірити на реальному iPhone/Android у gameplay density; Simulator не відчуває якість актуатора. Ніяких універсальних magic ms/Hz чисел без контексту пристрою.

## 7. Наслідки для навичок

Кожна стадія видає executable evidence або чесний blocker. Без Mac не стверджувати iOS export/test. Без signing не стверджувати installable IPA. Без реального прослуховування не називати аудіо прийнятим. Без store upload не називати гру опублікованою. Ранній exact screenshot — це контракт intent; motion/rig/physics/audio не відновлюються з одного кадру, тому потрібні representative runtime scene + motion/audio reference + вимірювані критерії. Якщо fidelity не досяжна за budget/hardware, поставити конкретний вибір користувачу до заміни стилю/рушія/механіки.

## Перевірені первинні орієнтири для commerce QA 3.0

Звірено 2026-11-02 за офіційними матеріалами; повторно відкрити актуальну сторінку перед конкретним release, не переносити API/строки вічними числами. Це platform contracts/testing guidance, а не доказ, що обрана модель монетизації буде комерційно успішною.

- Apple, [Testing at all stages of development with Xcode and the sandbox](https://developer.apple.com/documentation/StoreKit/testing-at-all-stages-of-development-with-xcode-and-the-sandbox): середовище Xcode й sandbox мають різні можливості; обрати належний метод для restore, pending/deferred/interrupted/failed, refund і subscription lifecycle за actual product type. Наявність local StoreKit config не підтверджує App Store Connect catalog/live readiness.
- Google, [Play Billing security](https://developer.android.com/google/play/billing/security): перевіряти purchase до entitlement, розрізняти purchased/pending, захищати duplicate grant та acknowledgement/consumption. Purchase identity не підміняти довільним order ID. Backend route і API обрати за чинною platform guidance та actual architecture.
- Google, [Policies for ad units that offer rewards](https://support.google.com/admob/answer/7313578): оголосити required action/reward до opt-in; відмова не заважає normal usage; обіцяну винагороду видати після належної дії.
- Google, [Create a rewarded ad unit](https://support.google.com/admob/answer/7311747): frequency caps і server-side verification є інструментами реалізації. Їхня конфігурація сама не доводить виконання game-specific attempt budget або durable grant.

Для current project snapshot зберегти checked URL/date, applicable rule, chosen SDK/API/product versions, exact RC та actual test/evidence. Одне посилання без перевірки binary/config не закриває compliance.

## Застосування дослідницьких snapshots у 4.0

Усі датовані числа/fees/SDK constraints вище зберігають історичне походження; це не lockfile current проєкту. Перед actualrelease повторно відкрити officialdocs і bind до exactengine/exporter/plugin/SDK/target/signed artifact. Нові provider/catalogcapabilities перевіряти peroperation/плану/правам, не за брендом.

Cloudcontinuation/OSbackup/purchaserestore різні mechanisms. Google/AppleSDK/native bridges мають actualversion/OS support/conformance probe; наявність account або store публікації не доводить save. Не змінювати мінімальний OS абододаватиплатний backend автоматично.
