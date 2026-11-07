# Камера, керування, навчання й повний шлях гравця

## Застосування, вхід і власний результат

Застосовувати до всіх взаємодій; spatial camera потрібна лише просторовому досвіду, а fixed camera є повноцінним вибором, не N/A. Прийняти fantasy, core rules, target devices/orientation, world/encounters, progression/rewards і creative envelope. Власні результати: camera/input contracts, screen/state atlas, learning curriculum, multimodal event map і usability scenarios. Використати [шаблон](../../assets/domain-templates/camera-input-experience.template.json); canonical model domains — `camera`, `input`, `learning` із посиланнями на чинні project IDs.

## Камера як поведінка, а не один кадр

Окремо задати projection/view angle; tracking/follow; focus subject; framing/subject scale; world bounds; orientation/aspect profiles. Side view не означає нерухому камеру, а зображення сцени цілком не доводить, що весь світ має вміщатися в екрані. Розглянути релевантні fixed/follow/scroll/zone/over-shoulder/vehicle/іншим чином керовані режими з конкретними перевагами й ризиками; не примушувати всю гру до одного з них.

Визначити стани normal/traversal/aim/interaction/peak/transition або інші потрібні: trigger, target/offset, desired subject fraction of viewport, bounds, dead/soft zones, look-ahead, damping/velocity limits, zoom rules, occlusion handling, transition/cancel, offscreen signaling і return. Частку висоти героя вимірювати у частках viewport та пояснювати дією, дистанцією читання й видимим майбутнім викликом. Не встановлювати єдиний відсоток для всіх жанрів. Герой може тимчасово змінювати розмір, якщо це передбачувано й не забирає важливу інформацію.

Перевірити запас видимості до загрози з урахуванням closing speed, telegraph duration, camera travel, input latency, action startup і можливості ухилення. Оцінка часу до контакту за відстанню/швидкістю є діагностикою, не універсальним нормативом реакції. Встановити та перевірити цільові вікна за жанром/аудиторією. Для offscreen attacks, руху назад, вертикальних перепадів, поворотів, погоні й пікового VFX визначити читабельний cue або fair behavior limit. Збільшувати огляд лише коли це підтримує рішення; не зменшувати персонажа автоматично, щоб сховати всю сцену в кадрі.

Для відбору показувати справжній gameplay framing. Якщо механіка потребує зміни огляду, дати послідовність ключових станів/кадрів або рух у релевантному scope; називати generation storyboard пропозицією, а не runtime доказом. Після вибору переносити camera rules й approved framing у assets/build/QA.

## Зручний доступ до глибини

Для input action задати intent, gesture/device, контекст, hit area/ownership, thresholds/units, simultaneous contacts, priority/arbitration, hold/release/cancel, buffer, invalid reason, recovery й feedback. Пов'язати movement/aim/tool/camera actions з фазами правил, а не лише іконками HUD. Контекстний input має передбачуваний target/action preview; у неоднозначному випадку дати стабільне правило, явний вибір або безпечне скасування.

Порівняти доречні control schemes на тій самій задачі: one/two hands, direct drag/steer, virtual controls, gestures, contextual actions, assist та інші за fit. Обрати схему за жанром, точністю, темпом і player comfort, не за звичним шаблоном. Глибина може походити з напрямку, timing, стану, комбінації інструментів і позиції; кількість кнопок не є метою.

Побудувати peak-load episode: рух, прицілювання, дія, зміна інструмента, реакція/камера, пальцеві перекриття та system edges. Задати, що можна виконати одночасно й що навмисно послідовно. Перевірити на реальному телефоні доступність цілі, втому, великі/малі руки, handedness, чутливість, pause/interruption. Desktop pointer не доводить touch feel. Assist не повинен приховано міняти куплені права чи примушувати до слабшої схеми.

## Feedback, HUD і game feel

Для ключової дії скласти prediction → input → rule/contact → animation/VFX → SFX/music → haptic → cost/reward/world change → next decision. Описати latency/timing, cue priority, overlap/cooldown, intensity, interruption і ownership. Cues попереджають, підтверджують, пояснюють помилку й відновлення. Звук/вібрація підсилюють видиме, а не є єдиним носієм essential information. Reduced motion/effects, mute/no-haptic, color/contrast та localization не повинні ламати розуміння.

HUD показує потрібний для наступного рішення стан: value/range/trend, небезпеку, доступну дію й recovery за fit. Health/resources можуть бути bars, discrete cues, diegetic states або іншим читабельним поданням. Не множити індикатори без рішення, яке вони підтримують; не ховати системну глибину за однаковими умовними сердечками. Перевірити first-play/normal/peak/late states на phone size й різних aspect/font scales.

## Навчальний граф і шлях поза core gameplay

Для кожної потрібної навички/системи задати teaches, prerequisites, момент потреби, cue, safe practice, assessment без постійної підказки, remediation й transfer у новий контекст. Не видавати побачену інструкцію за засвоєну навичку. Розкривати неосновні можливості в момент їх релевантності; не вивантажувати інвентар/магазин/десять ресурсів до першої зрозумілої дії. Допомога залежить від спостереженої помилки/затримки, має припинятись після успіху й не заважати досвідченому гравцю. Задати skip/replay/practice та resume після перерви, без втрати прогресу.

Інвентар охоплює first launch, loading, consent за потребою, hub/menu, settings/accessibility, tutorial/practice, selection, loadout/collection/upgrades, shop, gameplay/pause, win/fail/reward/retry, unlock, offline/reconnect, suspend/resume/update, support/credits й усі застосовні errors. Кожен reachable state має purpose, guard, data authority, visible content, actions/back, pending/empty/locked/error, side effects, persistence і recovery. Непотрібні акаунти/соціальні системи не додавати заради списку. Animation не видає нагороду й не підтверджує платіж.

## Взаємодії, доказ і ролі

Камера/input змінюють [world/actor fairness](world.md), [systems](systems.md), [learning/progression](progression.md), [creative](creative.md), commerce discovery/decline та save/return. Зміна масштабу героя може змінити telegraphs, encounters, HUD і performance — відкривати ці залежності.

Concepts потребує causal camera/input/learning design і first/peak examples. Preproduction — typed values, state/transition/curriculum contracts та measurement plan. Slice — реальний runtime, timed input/camera/motion evidence, native/device readability й tactile/audio observation за фактичним доступом. Beta — людська помилка, розуміння, самостійна дія, comfort/return; вибірка й сценарії мають відповідати питанню. Release — independent critical state/purchase/save reviews і device checks. UX/input/camera author, gameplay engineer, learning/accessibility та creative specialists працюють над спільними IDs; independent reviewer не підміняє playtest гравців.

## Джерела й статус рекомендацій

- [Roblox: Onboarding techniques](https://create.roblox.com/docs/production/game-design/onboarding-techniques) — офіційні рекомендації платформи щодо contextual tutorials, timed hints і feedback; їхню ефективність для нашої гри вимірювати.
- [Nintendo: Wonder, chapter 3](https://www.nintendo.com/sg/interview/aqmx/03.html) — практика доступних альтернатив проходження й здібностей.
- Camera contracts, visibility analysis й stage gates вище — правила агента, не універсальні фізіологічні чи індустріальні пороги.
