# Економіка, що належить самій грі

## Почати з player value

Спершу визначити satisfying безкоштовний/базовий шлях, його mastery і змістовні unlocks. Для кожного платного класу пояснити: яку потребу він обслуговує, як змінює взаємодію, хто/коли його бачить, earned route, вплив на challenge, альтернативи й downside. Не вставляти магазин поверх слабкого core. Не вимагати десяток валют/гачу/season pass у кожній грі лише тому, що приклад їх має.

Матеріальна монетизаційна розвилка потребує user choice. Показати whole player journey і платний/неплатний баланс, а не тільки ціни. «Не pay-to-win» перевіряти визначеними межами: ranked parity/normalization, no mandatory paid counter, earned access, no hidden disadvantage, effect sizes, time-to-access і actual scenarios. Sidegrade із іншою weapon mechanic все одно може домінувати й потребує balance tests.

## Повна карта цінності

| Система | Проєктувати явно |
|---|---|
| Currencies | Stable ID, purpose, earn/spend/exchange, tradability, paid/earned provenance, caps, precision, expiry, inventory authority |
| Characters/weapons/build options | Input/mechanical differences, synergies, counters, skill floor/ceiling, base availability, unlock/upgrade trees, power envelope |
| Catalog/offers | SKU, platform product kind, localized display source, grant, eligibility, price schedule, duration, limits, stock, dependencies, fallback |
| Bundles/pass/subscription | Exact contents, free/paid tracks, level cadence, eligibility, expiry, missed rewards, duplicate items, renewal/cancel/restore, entitlement lifetime |
| Rewarded ads | Voluntary trigger, reward/value, frequency/fatigue caps, no-fill/offline/fail/cancel, grant-once authority, interruption/resume, child/privacy eligibility |
| Random rewards if chosen | Full pool/version, weights/probability display, pity/guarantee, reset, duplicate conversion, caps, earned route, purchase boundary, audit |
| Events | Entry/exit, calendar/clock authority, progression overlap, event currency expiry/conversion, late arrival/catch-up, post-event claims |
| Support/refunds | Receipt/status lookup, restore/revoke, consumed consumables, negative balance policy, support trace and user message |

Включити directed graph faucet→wallet→sink→reward→gameplay→next need. У кожного ребра: exact quantities/formula, prerequisites, time/cost, authority, transaction/retry/persistence semantics і UI representation. Не дозволяти валюті існувати лише як абстрактний «diamond» без ролі у flow.

## Balance and simulation

Виконувана модель має policy profiles: casual/regular/skilled, nonpayer/payer, lucky/unlucky, new/returning. Inputs: sessions/playtime, performance, earn rates, offer exposure, caps, unlock costs, season lengths. Outputs: time to each meaningful unlock, dominant progression route, currency inflation/stranding, paid advantage distributions, frustration walls, content exhaustion, expected spend limits, uncertainty. Revenue assumptions позначати як сценарії; не називати їх фактом попиту.

Окремо розвести difficulty curve та conversion. Не налаштовувати навмисні near-fail/непрозоре погіршення skill для примусу купити. Якщо задана випадковість, failure reasons мають бути читабельними й відтворюваними. Показати приклади, де гравець купив content option і все одно мусить освоїти його; перевірити, що без покупки він має повний дієвий шлях.

## Commerce is a state machine

Specify product discovery→eligible→store sheet→pending/success/cancel/fail→verification→grant→acknowledge/finish→inventory/UI. Include retries, duplicate callback, app kill before/after payment, offline return, revoked/refunded transaction, account switch, restore and parental approval. IDs for purchase/order/transaction/grant are separate; grant-once key persists across reconnect. Never trust client currency writes or screenshot receipts as financial authority.

Store policy varies by region, entitlement, age, product type and date. Verify current official requirements during release; do not hardcode external checkout as universal. Paid randomized items require current platform/legal check and disclosed odds where applicable; do not claim legislation is checked by a design checklist. Real-money gambling/cash-out is a different product boundary and needs explicit scope and specialist review.

## UX and analytics

Ціна/валюта/вміст/термін/умови мають бути зрозумілі до підтвердження. Позначати actual purchase context, без оманливих кнопок, фальшивих countdowns або прихованого renewal. Events reference offer/catalog version, eligibility, source, purchase/grant/refund state, real/virtual currency and experiment assignment; minimize personal data. Experiment balance cannot silently change paid entitlement.

## Fit і магазин 4.0

Обирати модель доходу через досліджену взаємодію із конкретним loop/progression/content demand; порівняти релевантні premium, content, playstyle, convenience, capped attempts/boosts, voluntary ads, passes або інші моделі, не вставляючи всі в кожну гру. Для аналога відокремити observable implementation, commercial evidence, distribution/IP effects і висновок про переносимість. Чужий успіх не доводить fit.

Якщо обрані додаткові спроби/часові переваги/спеціальна валюта, визначити exact cap, reset/clock authority, earned/paid provenance, stacking, expiry, conversion, challenge effect і безкоштовний шлях. «Rewarded continue» без правил спроб/наслідків/повернення не є завершеним дизайном. Не приписувати paid randomness, subscription або recurring spend погодженням концепту.

Магазин має journey discovery→understanding→trial/use preview→choice/decline→purchase/grant→use→restore/support; state/data/UX зв'язані з тією ж моделлю. Для кожного offer показати конкретну цінність у грі, сумарний портфель покупок і сильний counterexample домінування. Простий скін може бути доречним, але не закриває вимогу змістовної альтернативи там, де вона явно встановлена brief.

## Погоджені commercial boundaries 4.0

Функціональна покупка може давати доречну перевагу часу/можливостей/сили: виміряти її прозоро, задати межі й окремо fairness/ranked policy. Не проголошувати non-dominance універсальною забороною всіх power goods. Якщо модель чи межа вже погоджені, не просити повторного дозволу; нову material зміну оформити конкретно.

Default — deterministic purchase і прозорий earned RNG; paid RNG лише окремим явним рішенням. Bundle contract: повний функціональний склад/compatible slots/learning/cost, free acquisition distributions і tails, partial ownership/missing components/duplicates/compensation, trial/decline, receipt/grant/restore/refund/offline, cumulative paid portfolio. Commerce може належати виробництву/експедиціям/контенту/колекції/сервісу за fit, а не лише equipment.

Reward/economy spend і результат мають consistency group та durable identity. Cloud save/OS backup/store restore не дублюють consumed currency/consumables. Смерть/crash/repair/continue не додають платного rescue за замовчуванням і не псують базову арку заради conversion.
