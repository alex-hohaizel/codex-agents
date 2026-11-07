# Комерційна модель, економіка й магазин

## Застосування, вхід і власний результат

Оцінювати бізнес-модель разом із механікою від концепту. Реальні IAP/ads/subscriptions активувати лише за обраним scope. Прийняти fantasy/core loop, development/reward/world graphs, аудиторію/ринки, finite launch/cadence, бюджет і platform capabilities. Власний результат — порівняння моделей, player-value journey, economy/catalog/offer contracts, shop state graph, balance/integrity evidence. Використати [шаблон](../../assets/domain-templates/commerce-player-journey.template.json). Intentional `commerce.model:none` не потребує вигаданого магазину.

## Вибирати fit, а не повторювати одну покупку

Порівняти доречні до гри моделі за player value, frequency of use, контентною місткістю, acquisition barrier, free/paid access, ongoing costs і ризиками. Не додавати всі можливі моделі. Розрізняти premium access; free trial/full unlock; paid content/expansions; optional alternative playstyles; cosmetic expression; finite resources/attempts/boosters; rewarded ads; passes; subscriptions; hybrid або no-offer. Приклад від користувача розширює простір дослідження, не стає універсальним обов'язком.

Premium може чесно вимагати придбання доступу; це не прихований paywall усередині обіцяної безкоштовної гри. Для F2P визначити самодостатню безкоштовну арку й дієві earned/decline paths. Для paid expansion явно відокремити base content, lifetime access і нову цінність. Косметика допустима за fit, але не підміняє вимогу альтернативного досвіду, коли brief її прямо ставить. Продаж інструмента з іншими властивостями потребує перевірки сукупної переваги, а не лише слова sidegrade.

Дослідити конкретну реалізацію релевантних успішних/невдалих ігор: що продають, коли виникає бажання, чим користуються повторно, що доступно earned route, як працюють limits, currency/reward loops, trial, shop, lifecycle. Дані про успіх не доводять, що саме ця покупка його спричинила; врахувати IP/маркетинг/ринок. Не обіцяти ARPU/retention за чужими прикладами.

## Вплетена цінність і спільна економіка

Для обраного offer задати desire → discovery → релевантна trial/preview → earned/paid/decline choice → verified grant/ownership → повторне використання → нова meaningful goal. У baseline/alternative сценаріях показати ті самі обставини, дії пальця, змінені рішення, limits/downside і вплив на інші системи. За вимогою same-run experience покупку можна застосувати у поточній кампанії/save без прихованого reset/refill. Trial не зобов'язаний бути універсальним або безмежним.

Для ресурсу/валюти задати purpose, earn/paid provenance, sources/sinks/exchange, precision/caps, reset/refill, persistence/expiry, authority, UI і dependencies. Відрізняти звичайний ресурс, premium currency, entitlement і доступ до досвіду. Обрана додаткова валюта має власну роль; не множити diamonds заради каталогу. До витрати показувати зрозумілий результат і умови.

Для спроб/boosters визначити activity, baseline replenishment, eligible uses, spend ordering, maximum grants/uses у session/day/week/event, stacking, duration, expiry, carryover, refunds і shared cap across earned/ad/paid routes. Підсилення на тиждень не означає нескінченні спроби. Обмеження мають існувати у rule/config та player message, а не лише в презентації. Час/офлайн/зміна акаунта не повинні непомітно обходити entitlement/caps.

Для rewarded ads визначити добровільний trigger і точну нагороду до показу, frequency/fatigue caps, eligibility, loading/no-fill/offline/fail/cancel, app suspend/return, verified completion, grant-once й reconciliation. Dismiss callback не дорівнює earned reward. Реклама не повинна бути єдиним способом виправити помилку системи або приховано змінювати результат гри.

Pass/subscription/bundle потребують exact contents, paid/free tracks за застосовності, cadence/eligibility, claimed/unclaimed/duplicate behavior, renewal/cancel/restore, expiry і entitlement lifetime. Random rewards, якщо обрані, мають pool/weights/version, guarantees/pity/duplicate policy й чинну policy/legal перевірку для конкретного ринку. Не припускати paid randomness із самої наявності random loot.

## Магазин і транзакційний життєвий цикл

Спроєктувати entry/discovery, категорії/пошук за потребою, preview/comparison/trial, owned/equipped/eligible/unavailable/locked, exact contents/price/currency/duration/limits, confirmation/cancel, pending/success/fail і after-purchase use. Візуальна мова магазину є частиною гри; ціна локалізується з platform authority. Відмова/назад зрозуміла й не руйнує прогрес. Не використовувати фальшиві таймери, оманливі CTA чи приховане renewal.

Commerce state machine: eligible → platform flow → pending/purchased/cancel/fail → verification → authoritative grant → acknowledgement/finish → inventory/UI → restore/reconcile/refund/revoke. Окремі ID purchase/order/transaction/grant; persistent deduplication key; duplicate/out-of-order callbacks, kill до/після платежу, offline return, account change, parental approval і consumed goods. UI animation або client-written currency не є фінансовою владою. Unknown external outcome спершу звірити; не повторювати покупку/upload наосліп.

## Баланс, витрати й доказ

Порівняти casual/skilled, new/returning, payer/nonpayer за релевантною моделлю й однаковим playtime: time to meaningful access, dominant strategy, collection/synergy advantage, bypassed limits, frustration walls, currency inflation/stranding, content exhaustion і spend assumptions. Перевірити strongest cumulative portfolio, а не лише один item. Paid variety може мати ситуативну цінність; однаковий DPS не доводить баланс. Не підтасовувати difficulty/near-fail заради conversion.

Оцінити net receipts, platform/ad fees, production/support/backend/QA costs, cadence capacity і невизначеність сценаріїв. Дохідна таблиця є scenario, поки немає фактичних даних. Organic acquisition не дорівнює гарантованому нульовому CAC або відсутності праці.

Concepts потребує model fit і причинної цінності; preproduction — typed economy/catalog/journeys/caps та boundary examples; slice — relevant in-game discovery/decline/use і simulated sandbox state handling у чесно названому scope; native/device/purchase integration доказ на відповідному gate. Beta — людська цінність/зрозумілість/добровільність; release — current platform policy, real sandbox receipts й independent critical money/save review; liveops — actual cohorts/value/fairness і support outcomes. Economy designer, commerce/runtime engineer, UX і independent reviewer мають окремі deliverables; pricing/model choice залишається чинним user scope.

## Джерела й статус рекомендацій

- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) — policy; перевіряти актуальні застосовні розділи для product/region/age перед release, не трактувати цей документ як юридичний висновок.
- [Google Play: one-time purchase lifecycle](https://developer.android.com/google/play/billing/lifecycle/one-time) — офіційна інтеграційна документація; конкретні SDK/API перевіряти для pinned version.
- [Google AdMob: rewarded ads](https://developers.google.com/admob/android/rewarded) — офіційна документація reward events та test integration; не доказ того, що ads підходять будь-якій грі.
- Comparative fit, shared caps й cumulative-counterexample gates вище — правила агента; комерційна успішність потребує окремого дослідження й власного виміру.
