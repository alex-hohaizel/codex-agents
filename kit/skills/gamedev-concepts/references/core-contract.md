# Game Atelier — спільний виробничий контракт

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

Інструмент 4.0.0, сумісний handoff protocol 1.0.0. Це виконувані правила роботи агента, а не обіцянка результатів гри. Читати на старті кожного етапу разом із experience-contract.md, handoff-contract.md та requirements.md і [systemic-design.md](systemic-design.md). Специфічні references свого етапу читати за предметом задачі.

## Межі й порядок

`gamedev-director` координує studio → concepts → preproduction → assets ↔ build → qa → release → liveops. Studio та concepts зручні у Work; preproduction, assets, build, qa, release, liveops мають canonical repo у Codex. Work залишається research/visual/audition/consultation bridge, якщо саме там доступна модальність. Середовище не визначати за назвою застосунку: спочатку перевірити filesystem, tools, network, native SDK, devices, генератори та права.

Користувач уже може мати студію/гру. Прийняти актуальні файли й провести адресний intake, не запускати перейменування або повторний research автоматично. Зберегти підтверджений вибір назви/студії чинного проєкту; готовність старого artwork перевіряється окремо. Історичні профілі доступні адресно в [джерелах спадщини](historical-project-profiles.md). Ця навичка не вимагає наперед обрати одну гру, рушій або дві платформи для всіх майбутніх проєктів.

## Рішення користувача

Перед залежною реалізацією запитувати матеріальні розвилки: Android/iOS/обидві; портрет/ландшафт; 2D/2.5D/3D; core mechanics; online/offline/co-op; engine з суттєвими наслідками; цільові пристрої; аудиторія/вікові групи/ринки; модель продажу/реклами/випадкових покупок; дані акаунта й cloud save; paid tools/backend; графічний/audio master; юридична особа/публічні контакти/продакшн-публікація. Показати 2–3 реальні опції, наслідки та рекомендацію. Зберегти дослівне джерело/посилання на відповідь і точний scope. Невідповідь не є вибором. Незалежні гілки роботи продовжувати.

Не перепитувати вже надану чинну згоду; не просити погоджувати кожну кнопку чи оборотний технічний ремонт. Якщо дія не входить у чинне доручення (витрати, реєстрація, публікація, destructive migration), підготувати конкретний reviewable результат до запиту. Не підміняти користувацьке рішення AI-оцінкою або записом JSON.

## Збереження ідентичності

Перший схвалений frame/audio audition є canonical intent, а не редагованою сценою. Записати asset ID, точний оригінал, sha256, resolution/color profile, source/generation provenance, дозволи, scope схвалення. Не вигадувати font/model/rig/stems, яких зображення/аудіофайл не містить.

Розкласти зображення на camera/projection/lens, композицію й safe areas, proportions/silhouettes, world scale, palette/material/texture, lighting/shadows, geometry/layers, typography з ліцензованими binaries, UI tokens, VFX; рух на clips, curves, contact phases, per-limb constraints, collisions і фізичні параметри. Зв'язати кожну частину з реальним source, export, import settings і scene node. Для звуку — motifs/instrument palette/темп/key/texture, event map, stems/loops/transitions/mix і runtime routing.

Byte-identical reuse обов'язковий для unchanged canonical asset. Derived export має явний рецепт. Векторизація, перемальовування, інша поза/персонаж/шрифт не стає «ідентичним» через схожу палітру. Допустиму зміну показати поруч із master та погодити. До масового виробництва відтворити canonical scene у цільовому рушії, на цільовому пристрої, з тим самим aspect/camera/state/seed. User acceptance включає кадр, motion/contact clip, audio в gameplay, input/haptic feel. Pixel-diff корисний у контрольованому capture; він не доводить художню чи фізичну тотожність і залежить від рендера. Непідтверджену тотожність позначати pending, не обіцяти математично неможливу гарантію з одного JPEG.

## Ціла гра

Описувати дію пальця → правило/розрахунок → фізичну відповідь → animation/VFX/audio/haptic → reward/cost → next state → save/analytics. Для replay визначити run loop, завершення, failure/recovery, mastery, build variety, content grammar, meta progression, long-term content cadence і межі скінченного launch scope. Нескінченні seeds не є нескінченним змістом. Не підміняти відчутну різницю косметичним recolor.

Економіка починається з корисного базового досвіду відповідно до обраної моделі: для F2P потрібна повна free/no-offer арка, для premium — чесний обсяг після купівлі; безплатний доступ до всієї premium гри не вимагається. Монетизація є спроєктованим шаром системи з source/sink, earn/spend, unlock/entitlement, sidegrades, cadence, безкоштовним шляхом, purchase failure/refund/restore та перевіркою домінантної платної стратегії. Кількість валют або скриньок не є якістю. Випадкові платні предмети — окремий матеріальний вибір і актуальна store/legal перевірка для ринків. Гіпотези утримання/доходу не видавати за фактичні D1/D7/ARPU.

## Команда і приймання

Один producer/director веде requirement IDs, рішення та integration. Предметні техліди самі виробляють артефакти: gameplay/progression/content/economy; UX/accessibility; art/animation/technical art; audio/haptics; runtime/backend/stores. Активувати лише потрібних спеціалістів у фактичному ліміті слотів. Кожен має artifact path, assigned IDs, inputs, resource cap, stop і адресата. Ніяких порожніх менеджерських поверхів.

Автор не є незалежним QA власного артефакту. Записувати реальних actor IDs і output paths; якщо subagents недоступні, чесно self-check, потім зовнішнє/людське QA pending. Не симулювати незалежну раду ролями в одному повідомленні. Фінального окремого рецензента активувати для великого freeze, спірної вимоги або критичної зміни, не для кожної правки. Докази попередніх перевірок переносити за незмінних hashes та залежностей. Зміна shared shader, schema, currency чи brand master відкриває всі транзитивно залежні перевірки.

Local repair: автор усуває причину й проганяє релевантний check → QA відтворює тільки зачеплений scope → integration. Після двох безрезультатних повторів змінити діагностику/підхід. Не крутити безмежний цикл суддів. Critical money/privacy/authorization/save migration/release потребують незалежної перевірки незалежно від розміру diff.

## Чесність результату

Розрізняти: drafted; structurally_valid; independently_reviewed; user_accepted; built; device_verified; submitted; store_approved; released; observed_in_production. Файл APK не доводить тест на пристрої; README про музику не є музикою; прослуховування не замінює вимір, вимір не замінює прослуховування. Статус accepted у manifest — декларація, що перевіряється і протоколом, і людиною; seal рахує hashes і не дає дозволу.

Жоден етап не називає майбутню роботу виконаною. За відсутності оплаченої можливості/SDK/device/license дати blocked scope, локально готові частини, точну інструкцію завершення й наступний executable крок. Не погіршувати якість до примітивних звуків/геометрії без матеріального рішення користувача.

## Наскрізний досвід і виконання

Кожний seed поєднує дію, функціональний розвиток персонажа/інструментів і світу, потенційну добровільну цінність покупки та особливий художній задум. Кількість кнопок/валют/рівнів не доводить глибину. Показати, як одна система змінює рішення в іншій, як росте майстерність і як нові можливості переосмислюють старі задачі. Від першого кадру до магазинів тримати art/audio/input/commerce як частини одного досвіду; різні ідеї не отримують один графічний preset автоматично.

Для ключових взаємодій визначити передбачення → дія → рух/контакт → animation/VFX/audio/haptic → результат → навчання/наступне рішення; перевіряти mute/no-haptic/reduced-motion паритет. Для кожного offer: конкретне бажання, проба, earned/decline path, optional purchase, повторне використання, наступна мета та сумарний вплив колекції/доступу на payer/nonpayer. No-offer і змістовна альтернатива допустимі. Гіпотези про успіх й прибуток відокремлювати від чужих доказів і власних вимірів.

Director звіряє current intent/knowledge/decisions/dependencies перед job, записує проектну особливість і вплив, не змінює глобальну політику під назвою self-learning. Pause now/after artifact/after stage зупиняє подальші jobs у точному scope; checkpoint містить готове, поточне, невідомі external outcomes і наступний крок. Запам’ятаний фаворит, прев’ю та прийнята виробнича концепція — різні рішення. Автоматичний маршрут не скасовує матеріального вибору користувача.

## Системний поріг ілюстрованого пошуку 3.0.0

[Системний контракт](systemic-design.md) уточнює чинні must через `UA26-SYS-01…07`. До ілюстрації кожного кандидата потрібні пов’язаний паспорт, доступний visual production profile й незалежний смисловий review; до показу — actual огляд кожного кадру. Довжина картки, кількість кандидатів і preview-only не знижують поріг. Повний GDD, native/device доказ та user acceptance мають свої пізніші due gates. Не створювати другу authority registry або повторне погодження вже дорученого scope.
