# App Atelier: досвід від наміру до runtime

Зміст: journeys → input/state → production → доступність → комерція → assembly.

## Причинний UX
Після `cross-domain-core.md` і `app-system-contract.md` зіставити accepted concept/domain/state/API з intention→input→rule→feedback→durable result→next action. Повна карта включає first-use, core, returning, empty/loading/error, offline/conflict, cancel/undo/retry, interrupted/resumed, permissions/auth switch, export/delete/support і conditional payment. Для кожної видимої дії існує власний domain command/response/error contract. Відсутня backend функція не маскується привабливою кнопкою.

Визначити touch/mouse/keyboard/assistive input, selection/focus, gestures/threshold/priority, drag/cancel, navigation/deep link, timeout та repeated tap. Для app lifecycle описати background/foreground, process death/reopen, unsaved work, modal stacking і late callbacks. Анімація показує логічний стан, а не створює предметну істину. Local optimistic/pending/durable/cloud confirmed мають різний правдивий feedback. Critical purchase/save confirmation не видавати до визначеної authority.

## Платформи й різноманіття станів
Android/iOS/web самостійно завершують core; визначити parity і допустимі platform-native differences. Орієнтації, viewport/density/font scaling, safe areas, keyboard, navigation/back, screen reader й system permission flows мають explicit expected layout/behavior. Сумісність старих пристроїв вибрати за профілем і SDK feasibility, не за модою нового ефекту. Зберігати accepted original, tokens, components, state variants, typography/content, locales і hashes.

Стани компонентів вивести з data/domain, а не від довільного UI kit: idle/focused/pressed/disabled/loading/partial/success/error/blocked/revoked за застосовності. Пріоритет одночасних feedback/notifications і interrupt/cancel задається точно. Reduced motion/mute/no haptic/no color не втрачають потрібної інформації. Відсутні media features позначити absent_by_design; не створювати музику/voice для кожної утиліти.

## Виробнича досяжність reference
Концепт-кадр відображає досяжний layout/complexity/materials/animation за обраним route. До прийняття напряму показати cost/limits інструментів, runtime support і що потребує authorship. Image generation output→editable/vector/layered masters→tokens/assets→export/import→actual screen є окремими операціями. Видалення фону не створює vector path; текст на raster не стає локалізованим або доступним UI. Скласти capability/schema/parameter consumption check для material property; недоступний source/rig/motion не ремонтується повторенням того самого prompt.

Recipe містить accepted inputs/hash, tool/version, editable source, steps, export settings, runtime bindings, screen/state/device/locale scenario і validators. Transformation фіксує pixels↔density units, typography metrics, color/alpha, frame↔second, locale grammar, accessible name/role/state, focus order. Прийнятий master не перегенеровувати для downstream repair; змінити похідний artifact або винести material delta на рішення. Для audio/motion — source/session/timeline/events, loop/cancel/lifecycle/perceptual checks, licensing і runtime budget за потреби.

## Доступність і контент
Вибрати WCAG scope/level для web та native accessibility criteria за current platform docs; conformance не зводити до одного automated checker. Перевіряти назви/ролі/стани, keyboard/focus path, text scaling/reflow, contrast і noncolor alternatives, targets, error identification/recovery, reduced motion. Відрізняти heuristic/synthetic, owner review і actual assistive/device evidence. Не рекрутувати людей або ставити A/B всупереч чинному обмеженню. Для locales: довгі рядки/plurals/number/date/time/currency/RTL за аудиторією; text embedded in image є окремим localization defect.

## Комерція та довіра
Показати обсяг/ціну/період/renewal/limits до payment, корисний free/trial шлях і доступ після покупки за концепцією. Pending/refused/refunded/expired/restore/account-switch мають точні UI states. Множинні offers/ads/bundles перевірити разом; не маскувати зовнішню рекламу під кнопку або відновлення даних. Delete/reset/unlink/disable sync не об’єднувати в один невизначений діалог. Для destructive action показати фактичний предмет і наслідок за прийнятим contract.

## Приймання assembly
Перший зріз має реальні input/navigation, domain data, persistence/reopen, feedback і optional billing/sync/support. Зафіксувати exact build/config/assets/tokens/hash, scenario, expected/actual, target/viewport/input/accessibility settings. Порівняти runtime із reference за предметними tolerances, не обіцяти pixel equality усіх GPU/platform. Перевірити cold start/peak data/long strings/slow network/permission denial. Статичний рендер не є prototype; prototype не є native proof. Cold receiver отримує masters+tokens+state map+content/rights+recipes+runtime acceptance, не лише screenshot.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: сценарії взаємодії й станів, справді різні дизайн-напрями, прийняті masters, прототип і критерії відповідності реалізації. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: мовна, візуальна й інтеракційна якість, доступність і узгодженість досвіду. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
