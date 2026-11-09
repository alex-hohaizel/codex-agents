# Game Atelier4.0 — модель і процес

Зміст: вхід → authority → gates → orchestration → handoff → зміни.

## Вхід

Читай [v4/index](v4/index.md) і current intent/checkpoint. Визнач C0/C1/T та відповідний scope. Нові завершені концепції4.0 мають C1; production передача T. Studio не вигадує game model до появи гри. Пошук, аудит, update/pause не обирають гру й не запускають новий раунд.

## Одна модель

Project-owned `design/game-model.json` або чинний equivalent має stableIDs/source/constraints/features/domains/dependencies/scenarios/evidence. Розширення4.0 `production` зберігається в тому самому envelope; з нього походять20tracks/behavior/catalog/state/production contracts. Підключені specs/data мають exact path/hash. Чинні requirements/decisions лишаються authority; sidecar є pin/mapping. Формат/CLI — [model-format](model-format.md). Six logical competencies та conditional applicability — [v4/index](v4/index.md).

Не прив’язуй small до арени, projection до tracking, world доRPG, genre доart/input/commerce. Disabled має предметну причину; missing tool не вимикає потрібної фічі. Фіксована камера залишається activecamera, коли вона існує в грі. Actor може бути NPC/суперником/союзником. No-offer/premium baseline не отримує обов’язкових IAP/ads.

## Gates

| Gate | Належний результат |
|---|---|
| concept | ПовнийC1, причинні сценарії й counterexamples, feasibility profile, незалежне смислове приймання; C0 тільки internal preliminary |
| preproduction | T: exact contracts/launch catalogue/generator/persistence/recipes/assets/input/AI/math, fixtures і pinned specs; cold receiver може почати реалізацію |
| slice | Actual native representative assembly для declaredplatforms: input/camera/motion/contact/visual/audio/haptic/save; due device proof |
| beta | Реальне людське навчання/перенесення/late mastery/різноманітність/цінність і scope вибірки |
| release | ExactRC/signing/config/epoch/schema/symbols, purchase/cloud sandbox за обсягом, device/performance/policy/recovery |

`plan` перелічує due checks; `validate --design-only` перевіряє authoring і завжди `stage_ready:false`. Ніякий прапорець не усуває must. `quality_certified:false`: schema/link/bytes/check не є fun/balance/device/human/revenue. Валідатор читає тільки поточну модель. Для нового або відновленого контексту автор наповнює C0 фактичними contracts і отримує належні C1/T та stage докази.

## Реальна команда

Директор інтегрує, предметні автори виробляють outputs, техлід узгоджує interfaces, інший actualactor перевіряє critical. Один writer на path і sharedresource; actualslots є межею. Task має input/hash, assignedIDs, ownedpaths, acceptance/consumer, capability/operation/host, dueevidence, budget/stop/cancel/reconcile. Відокрем independent author alternatives від reviewer. Немає фіксованої ради за кожний рядок.

Після двох однакових невдалих ремонтів зміни причину/діагностику/route; не множ generators/promptretries за відсутньої capability. Recipe й productionattempts — [production](v4/production.md). World/physics/commerce/currentnativeSDKdetails перевіряй першоджерелами під pinnedversions; acceptedmodel не робить toolavailable.

## Handoff

`pipeline.py` використовує чинний transport/schema/suite **1.0.0**, `atelier.py` — чинний state **2.0.0**; обидва вимагають toolkit **6.0.0**. Nonstudio accepted handoff має `game_model:{path,sha256}` з поточною моделлю **4.0.0** й належним stage proof. Попередній формат результату відхиляється також у draft. `seal` hashes не є дозволом чи review. Companion modelplan/report/traces входять як звичайні artifacts.

Defaultstage→gate: concepts→concept; preproduction→preproduction; assets/build→slice; qa→beta; release/liveops→release. QA може мати design_review/contract_review/slice_review/beta_review/release_readiness; liveops incident_analysis/design_change/runtime_change/player_experiment/release_change. Scope потребує scope_ref на поточну requirement/decision і опис; scopedreview не обирає productionconcept/engine. Release таrelease_change не знижуються доslice. Деталі — [handoff](handoff-contract.md).

## Impact і продовження

Зміна → semanticreads/writes/contracts → залежні specs/data → assets/code → scenarios → builds/release. Граф має причину кожного ребра; gameplayfeedbackcycles допустимі, unlock/DAG prerequisites — ні. `impact` допомагає записаним closure, не виявляє пропущені смислові ребра. Зміна grip може відкрити routes/input/economy, але не studiooriginal.

Scoped evidence reuse враховує declareddependencyclosure/toolchain/recipe/version/outputs; не переписуй hash як заміну review. Nativeobservations bind exact build/scene/config/scenarios. Acceptedoriginal лишається byteidentical; stochasticprovider не має гарантії повторного identicalgeneration.

Installskill не переписує game saves, раунди, decisions, .gameatelier або .atelier чинного проєкту. Work і кожний Codexhost перевіряються окремо. Недоступний host отримує inputpinned launch/returnbundle з exactcommands, outputs/receipts і returnvalidation. Після release лишається actualstate/checkpoint; schedulerбезфактичногозапуску не існує.
