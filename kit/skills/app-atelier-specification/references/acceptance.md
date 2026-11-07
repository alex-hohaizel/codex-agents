# Прийми специфікацію за доказами

## Зміст

1. Розділи spec і майбутні gates.
2. Перевір власні due requirements.
3. Перевір наскрізні вимоги.
4. Пройди negative cases.
5. Передай findings і статус.

## 1. Розділи spec і майбутні gates

Використай common requirements/decisions/evidence contracts, не створюй паралельний registry.
Збережи reviewer/date/method/inputs/hash/finding/REQ-ID/status/limits кожної перевірки.
Назви роботу автора self-check; independent QA вимагай від фактичного іншого reviewer.
Schema/link validation не видавай за семантичну повноту PRD/TDD.

| Gate/status | Підтвердь | Не підміняй |
|---|---|---|
| draft/blocked | Назви придатні частини й exact blocker. | Не приймай headings як готовий контракт. |
| spec-ready | Підтвердь предметну достатність документів, оцінок, due checks і рішень. | Не стверджуй working product, store access або proven demand. |
| slice_planned | Підтвердь виконуваний risk-based plan. | Не називай план actual pass. |
| before-full-build | Вимагай actual slice й решту prerequisites. | Не проходь gate лише за PRD/TDD. |
| before-release | Вимагай current tests/permissions/owner readiness. | Не успадковуй readiness від ранньої feasibility. |

Приймай spec без binary, production API чи live покупки за достатніми контрактами.
Не відкладай невідомий due spec must під виглядом future test.
За недоступної external feasibility збережи перевірену документацію й блокуй саме залежне production рішення; не гарантуй route.

## 2. Перевір власні due requirements

### REQ-11 — мінімальна залежність від AI/API

Перевір concrete value кожної dependency, варіант без неї й реальну альтернативу/fallback.
Вимагай current source/date для price/limits/commercial/data/license rights, offline, exit і caps.
Включи expected/stress usage, abuse/retries й витрати в економіку.
Для відсутності APIs вимагай пояснення предметної достатності, не порожню таблицю.
Відхили free tier без quota/overage або наявну підписку як необмежений production API.
Відхили one-time purchase з неврахованими довічними платними викликами.
Познач unknown price/license/account доступ blocker залежного effect.
Вимагай dependency-options, cost model, data map, fallback/exit і trace до feature/API.

### REQ-16 — локальні дані й мінімальний збір

Вимагай повну карту fields/copies/transfers, local/cloud comparison і функціональну причину cloud branch.
Визнач purpose, access/authz, retention/export/delete/revoke/restore для кожного data kind.
Вимагай explicit no-account/guest/account branches; не приймай неявне створення identity.
Перевір sync conflicts/offline queue/tombstones/migrations/backups і restore межі.
Перевір support/dialogs/logs/cache/index/AI/telemetry окремо від primary records.
Відхили default telemetry й мовчазне відправлення всіх локальних даних у cloud.
Відхили public KB або AI context з приватних звернень поза дозволеною картою.
Вимагай data-auth contract, access matrix, state/sync rules, lifecycle policy, negative fixtures і data gate status.

### REQ-19 — завершений обсяг і чесний строк

Вимагай core із входом, корисним результатом, повторним використанням і recovery на трьох клієнтах.
Порівняй core/wider за однаковими time/resource assumptions.
Вимагай packages, ranges, critical path, dependencies, integration/QA/release/support effort і buffer.
Вимагай конкретного reuse evidence; «AI швидко напише» не приймай.
Перевір приховане зниження якості, втрату платформи або ручний сервіс власника.
Не вигадуй deadline й не стискай estimate заради бажаного результату.
Вимагай scope table, client-core matrix, assumptions, risks, slice plan, roadmap і scope decision.

### REQ-38 — рання здійсненність релізу

Вимагай dated primary rules/fees, platform routes, account type/access evidence, signing/build host і required testing map.
Зістав prerequisites із budget/no-human profile до production scope/значного build.
Без доступу познач unverified, exact dependency, blocked action і спосіб наступної перевірки.
Не приховуй mandatory fee; не симулюй особу, тестувальників, підпис чи MFA.
Вимагай before-release recheck й event-driven recheck при зміні account/platform/model.
Вимагай feasibility source/date/status/cost/conflict/alternative/recheck і owner delta для budget/scope за потреби.

## 3. Перевір наскрізні вимоги

| REQ | Перевір у spec | Збережи межу |
|---|---|---|
| REQ-03 | Зістав setup/recurring/usage зі cap й покажи zero-budget conflicts. | Не створюй зовнішніх витрат. |
| REQ-04, REQ-09 | Задай recurring automation, faults і unresolved cases. | Не закладай щоденну ручну бізнес-роботу власника. |
| REQ-10 | Задай повний independent core Android/iOS/web і acceptance. | Actual client pass залиш build/QA. |
| REQ-12, REQ-15 | Пов'яжи value, monetization, recurring benefit і costs. | Не гарантуй попит або profit. |
| REQ-17 | Заборони intentional human research/testing/A/B на всіх фазах. | Synthetic/public reviews/owner review не називай user validation. |
| REQ-18 | Задай automated acquisition від zero audience з rights/caps/stop. | Activation залиш окремому gate. |
| REQ-20, REQ-21 | Передай design states/accessibility/device/offline constraints. | Не обирай дизайн за власника й не приймай placeholder. |
| REQ-24 | Використай чинні owner decisions у exact scope. | Не перепитуй без delta й не обирай reserved decisions. |
| REQ-28, REQ-30, REQ-31 | Задай guest/auth/data/KB/read-only/fallback contracts. | Не розширюй context або bot actions автоматично. |
| REQ-32 | До досліду задай metric/threshold/horizon/budget/stop/next action. | Не змінюй поріг після невдачі й не додавай human experiment. |
| REQ-35, REQ-36 | Збережи status/detail/chat, versions/hashes/checkpoint. | Не втрачай requirements і не повторюй unknown effect. |
| REQ-37, REQ-40 | Назви actual authors/reviewers, bounded jobs й caps. | Не називай self-check незалежним QA. |
| REQ-43 | Задай model-specific entitlement/restore/events/refund/expiry/cancel. | Actual provider-backed tests залиш build/QA; не нав'язуй subscription. |

Перевір experience handoff: journeys/objects/states/platform constraints й owner design choice.
Перевір build handoff: transitions/invariants/schemas/errors/events/conflicts/slice oracle/fixtures.
Перевір support handoff: version/language/KB sources/context fields/link/revoke/retention/cost/fallback/action boundary.
Перевір release handoff: prerequisites, unverified items, exact blocked effect, source age/recheck.
Перевір growth/operations handoff: economics/automation/caps/stop/recovery/exit без прихованої ручної рутини.

## 4. Пройди negative cases

Пройди tabletop із synthetic fixtures; для кожного case знайди expected rule/state/output й artifact section.
За відсутності однозначної відповіді відкрий finding.
Не видавай walkthrough за runtime test, експеримент на людях або proven usability.

| Case | Введи | Вимагай |
|---|---|---|
| NEG-SPEC-01 | Почни web core без mobile client. | Отримай повний core result; відхили landing-only заміну. |
| NEG-SPEC-02 | Виконай command у забороненому стані на трьох клієнтах. | Отримай однакову domain відмову й визначений recovery. |
| NEG-SPEC-03 | Зміни запис offline на двох клієнтах і sync у reverse order. | Визнач conflict result без мовчазної втрати даних/ownership. |
| NEG-SPEC-04 | Видали record/account і віднови old backup/offline device. | Збережи delete/revoke/tombstone; не відроджуй видалене. |
| NEG-SPEC-05 | Передай ID B в session A через API/support/cache/history/channel. | Відхили backend access; не повертай чужий context. |
| NEG-SPEC-06 | Зроби guest merge з duplicates і partial failure. | Визнач ownership proof, merge/retry без чужого доступу. |
| NEG-SPEC-07 | Зміни display name/username або підроби link/transport credential вибраного каналу. | Вимагай server proof, expiry/replay/revoke. |
| NEG-SPEC-08 | Перевищ API quota або отримай offline/stale/invalid result. | Застосуй bounded retry/fallback і visible limit без cap overrun. |
| NEG-SPEC-09 | Зміни vendor price/license або припини API. | Визнач blocker/recheck/exit й economics/scope impact. |
| NEG-SPEC-10 | Дай one-time покупцю максимальний recurring usage. | Покажи sustainability/caps/rights, не unbounded loss. |
| NEG-SPEC-11 | Повтори provider event, достав refund до delayed purchase, розірви мережу після provider success. | Визнач dedupe/reconcile й authoritative rights без double grant. |
| NEG-SPEC-12 | Зроби restore/new device/account change/sign-out/offline після expiry. | Узгодь заявлені rights Android/iOS/web і recovery. |
| NEG-SPEC-13 | Cancel/refund/частково спожив usage. | Застосуй різні model-correct transitions. |
| NEG-SPEC-14 | Обери ads/affiliate/no-purchase model. | Обґрунтуй N/A branches; не додавай subscription. |
| NEG-SPEC-15 | Увімкни «корисну аналітику» або AI diagnostics без data decision. | Залиш pending; не передавай нові fields/private dialogs. |
| NEG-SPEC-16 | Назви synthetic UX доказом demand або passive metrics дозволом A/B. | Обмеж висновок і відхили human experiment. |
| NEG-SPEC-17 | Вияв mandatory fee/human store testing за zero-budget/no-human profile. | Познач conflict, blocked route, allowed alternative/delta/stop. |
| NEG-SPEC-18 | Не май developer account/signing access. | Познач unverified prerequisite, не store-ready. |
| NEG-SPEC-19 | Додай wider scope без готового reuse за того самого строку. | Зроби re-estimate/critical path/decision; не стискай QA. |
| NEG-SPEC-20 | Не розв'яжи recurring support/moderation/content case автоматично. | Відкрий operational feasibility finding; не маскуй щоденну працю власника. |
| NEG-SPEC-21 | Візьми красивий mockup без persistence/auth/API ризику. | Відхили як representative slice для такого ризику. |
| NEG-SPEC-22 | Отримай повну spec без binary. | Дозволь spec-ready за її доказами; залиш actual gates pending. |
| NEG-SPEC-23 | Зміни data/API/paid rights після baseline. | Перевідкрий affected evidence/estimates/decisions, збережи superseded. |
| NEG-SPEC-24 | Вичерп cap після двох однакових невдалих дослідів. | Збережи checkpoint, зміни діагностику/stop; не знижуй must. |

Додай product-specific cases: empty/max size, units, timezone/DST, localization, permissions denied, stale external data, migration incompatibility.
Обирай fixtures за ризиком, без дублювання implementation.

## 5. Передай findings і статус

Для finding запиши ID, REQ-ID, artifact/hash/section, expected/actual, severity, blocked gate, owner, repair/retest.
Розрізняй spec blocker, future implementation acceptance, external prerequisite і hypothesis/evidence gap.
Не маскуй критичне unknown словом assumption без impact й due verification.
Зупини залежну дію за незакритого due must, reserved decision delta, невідомих data/effect rights або cap overrun.
Продовж незалежні незаблоковані документальні роботи в чинних межах.
Перевір links/REQ-ID/paths/hashes, семантичну узгодженість і відсутність незаповнених шаблонів.
Видай spec-ready лише з accepted documents, due checks і відсутністю spec blockers.
Окремо назви actual future gates, unverified prerequisites, hypotheses й точну наступну дію.
Достав короткий статус, докладні матеріали й пояснення рішень; не називай spec delivery створенням продукту.
