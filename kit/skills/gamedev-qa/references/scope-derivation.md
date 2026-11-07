# Виведення обов’язкового QA scope 4.0

Цей контракт доповнює загальні QA правила конкретним алгоритмом. Зміст: джерела → scope → due gates → cases → закриття. Приклади в assets — плани перевірок, не докази виконання.

## Джерела й пріоритет

1. Прочитати чинні user requirements/decisions, accepted target, current game-model із maturity C0/C1/T, actual content/runtime inventory та dependency impact. Власний дизайн не є доказом того, що всі вимоги враховано.
2. Порівняти `features[domain].enabled/rationale`, `domains`, сценарії й actual implementation. Прихована реалізована покупка або противник не звільняються від перевірки через disabled feature. Розбіжність потребує repair моделі/реалізації або чинного material decision; QA не змінює scope мовчки.
3. Успадкувати вимоги й заплановані докази зі спільної моделі. Для наявного scope додати journeys, недоступні в одному кадрі: menus/loading, learning/transfer, game/failure/retry, rewards/inventory/upgrades, shop/purchases, return/exhaustion, settings/account/support за fit.
4. Обчислити зачеплені systems і транзитивні dependencies. Unknown impact — дослідження й розширення scope, а не автоматичний full-stage запуск. Money/privacy/auth/data-loss/release — критичні навіть при малому diff.

## Правило відбору cases

Взяти застосовні patterns із `assets/qa-case-catalog.json`, зв’язати з реальними requirement/rule/scenario IDs та переписати generic preconditions у конкретні стани/дані. Додати всі feature-specific boundaries, fault/recovery й historical defects, яких каталог не покриває. Каталог не дозволяє не тестувати неназвану фічу.

Обов’язковий scope визначається **фактичними можливостями + due gate + матеріальними claims**. Опціональні task flags лише додають scope, не можуть зняти потрібну modality/незалежність. Для активної feature не приймати rationale «не попросили тест», «це small», «тільки один персонаж» або «немає tool» як N/A. N/A має посилатися на agreed product rule: наприклад, у грі немає покупок/супротивників; їхні cases не запускаються. Відсутність функції не знімає її залежності: гра без ворогів усе одно може мати hazards і readable failure.

## Due gates й evidence

| Gate | Мінімальний належний доказ у named scope |
|---|---|
| concept | C0 лише labelled sketch; C1 кожного завершеного кандидата покриває всі застосовні 20напрямів, архітектуру сімейств/світу/розвитку/ризику/commerce, full concept handoff і сценарії зміни рішень; independent semantic review; image inspection перед показом; feasibility profile. Без native/fun/retention claims. |
| preproduction | Повний T: точні rules/state/data/journey/launch catalogue або grammar, StateCatalogue, production recipes/semanticedges і receiver intake; reachability, бюджети/межі й economy assumptions; model/property/invariant checks там, де обчислювано; test plan з незалежними oracles. |
| slice | Actual engine/runtime trace для representative систем і їхніх перетинів; source→runtime visual/motion/audio parity; physical device proof для заявленого native touch/thermal/haptics; sandbox commerce, якщо commerce входить у slice. Відсутня фіча поза slice лишається future obligation. |
| beta | Зібраний agreed beta scope, journeys/recovery і platform checks; actual first-use/learning transfer та gameplay observations людей. Окремі longitudinal questions потребують реальних повторних заходів, не одноразового наміру. |
| release | Увесь заявлений launch scope/target platform matrix: критичні journeys, final assets/config, install/update/save, sustained devices, actual store sandbox/ad failures, policy/rights/privacy. Human observations за продуктовими claims; live market success не вимагається й не вигадується. |

Після release у liveops відділяти actual cohorts від beta/simulation/internal tests. Без real datasource видавати diagnosis/measurement plan, а не вигаданий retention чи revenue. Детальні modality names й canonical evidence fields брати з `model-format.md`, не створювати другу authority registry.

## Конкретний case

Записати: case ID; source requirement і rule IDs; model/artifact/build hashes; domain/feature і trigger застосовності; due gate; precise preconditions/state/seed; action/procedure; expected observable + independent oracle source; changed decision/контрприклад де доречно; boundary/fault; required evidence layer/modalities; actual result/status; raw evidence refs; observer/author/reviewer; limitations/owner.

Успадкований сценарій моделі використовує `id,domains,initial_state,action,expected_observable,changed_decision,without_rule`. У QA packet додаються execution details, не підміняючи ці поля. Файл кейсу не стає canonical `evidence` доки не виконано його метод, не збережено actual proof і не внесено відповідний evidence record із checksum/provenance. Не підставляти case ID замість evidence ID.

Expected береться з approved rule/table, офіційного platform contract або незалежно виведеного invariant. Не тестувати формулу копією тієї самої implementation formula. Для UX/craft фіксувати observable acceptance й procedure до запуску, а не підганяти target після огляду.

## Покриття без формальності

Показати denominator: кількість належних journeys/state transitions, rule families, enemy/encounter families, item/ability interactions, content phases, offers і platforms у scope; actual tested/not-tested. Не заявляти «100% гри» за закритим переліком, якщо inventory неповний.

Порівнювати strongest simple policy в різних контекстах; rule/resource ablation; old task after unlock; early/mid/late; baseline/alternate/full paid portfolio; no-offer. Записувати яке рішення й чому змінилося. Новий seed, recolor, збільшене HP або додаткова кнопка не закривають цю перевірку.

Для комбінацій застосувати risk-based pairwise та відомі критичні 3+ взаємодії, boundary/recovery й curated seeds; fuzz/property де є meaningful oracle. Повна матриця всіх випадкових комбінацій не потрібна й не підміняє огляд складних систем.

## Закриття

Валідний handoff/model доводить структуру/посилання, а не фактичне виконання. Незалежний reviewer перевіряє raw proof проти expected rule та достатність scope. Missing modality — `not_tested`/`blocked`; fake human/actor IDs заборонено. Unresolved must закривається repair, named test scope або explicit product decision в належному authority, а не середньою оцінкою. Видавати exact boundary до наступного gate; інсталяція toolkit не підтверджує продуктову готовність.

## Вивести cases 4.0 з актуальних контрактів

Розгорнути resolver/contact/lifecycle, Actor/Knowledge/Action/Decision/Encounter/Boss, State Catalogue/Consistency Groups, operation DAG і semantic transformations у concretecases. Інвентар перевіряє всі активні 20напрямів, meaningful variation/opportunity/exhaustion, native adapter conformance/cold first use/transition memory/egress/symbolmatch. Детальні контрприклади — у[маршруті4.0](v4-route.md).

Критичні слоти: multi-hurtbox/substepdedup, pooled generation, DoT tick/expiry/snapshot, simultaneousdeath/phase/reward/kill, topologybreak/nav/restore, partial bundle/offlineconflict, ignored provider parameter, wrong axis/contact time й timeout reconcile. Не вимагати actualdevice на C1 без такого claim, але не знімати future obligation.
