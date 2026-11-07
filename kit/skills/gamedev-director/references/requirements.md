# Наскрізні вимоги Game Atelier

> Чинний контракт4.0: спочатку [зрілість/компетенції/authority](v4/index.md), потім потрібні предметні розділи. GA4-P1/D1/D2 доповнюють GA3/UA26 та старі IDs. C1 потрібен для кожної завершеної концепції, T — для виробничої передачі; evidence відповідного gate не замінюється документацією. Історичні джерела й approvals зберегти. R6-профілі, один масштаб, стиль, камера чи one-time kit не є глобальними defaults.

Кожен запуск копіює релевантні IDs до project registry з owner, acceptance, stage та доказами. IDs не зникають при handoff. Це baseline сімейства; конкретна гра додає свої, а не замінює ці слова абстрактним score. N/A має предметну причину й scope. Номери U відповідають пунктам запиту користувача; U2.1…U2.12 — вкладеним пунктам, PS — різниці середовищ.

| ID | Джерело | Обов'язкова поведінка / доказ | Власник етапу |
|---|---|---|---|
| ENV-01 | U1, PS | Work/Codex split з причиною, capability report, конкретне наступне середовище | director |
| ENV-02 | PS | Одне versioned source, plugin/local exports, hash sync-check; жодної обіцянки auto-sync чатів чи skills | director |
| ENV-03 | U1, U2.8 | Mac setup, installation, doctor, dependency adapters, smoke use, uninstall/upgrade instructions | director/release |
| FLOW-01 | U1 | Повний цикл studio→research→design→craft→build→QA→release→liveops, inputs/outputs/DoD/return | director |
| PACK-01 | U1,U2.11 | Portable archives із manifest, hashes, records, інструкцією і всіма фактично потрібними bytes | all |
| PACK-02 | U2.11 | Studio identity, approved masters, legal/public/product identifiers і licenses проходять усі етапи | all |
| BRAND-01 | U2.10 | Master студії не підмінюється новим vector art без узгодженого visual delta | studio |
| BRAND-02 | U2.11 | Studio accounts/setup/ads/analytics/storage runbook; доступна автоматизація в чинному scope, точний owner bridge для фактично недоступних MFA/legal/signing кроків; статус перевірений перед release | studio/release |
| IDEA-01 | U2, UA26-EXP-10 | Скінченний режим пошуку за актуальним наміром і різноманітністю; без універсальної кількості. Явно замовлені 4×100 мають точний відбір/outputs/stop, без автоматичного production choice | concepts |
| IDEA-02 | U2.2 | Масова привабливість/core fun/novelty/learning/challenge/virality мають causal design, контрприклад і тест | concepts |
| FID-01 | U2.1,U2.5 | Exact original/hash + element decomposition + source/export/node links + controlled runtime match | concepts/preproduction/assets/build/qa |
| FID-02 | U2.1 | Параметри відповідності й допустимі delta погодити; frame+motion+audio+device slice до mass production | preproduction/assets/build/qa |
| REP-01 | U2.2 | Run beginning/middle/end, repeated attempts, mastery/meta, finite launch scope і late-game variation | concepts/preproduction |
| REP-02 | U2.2 | Content grammar/seed/version/constraints/solvability/diversity/fallback, не просто випадковість | preproduction/build/qa |
| PROG-01 | U2.2 | Граф unlock, dependencies, formulas, curves, skill vs permanent power, early/mid/end progression | preproduction/build |
| PROG-02 | U2.2 | Сценарії першого, десятого, п'ятдесятого та тривалого повернення; час/варіанти — гіпотези до tests | concepts/qa/liveops |
| ECON-01 | U2.3 | Всі currencies sources/sinks/exchange caps/earn curves/inflation і free path у даних/симуляції | preproduction/build/qa |
| ECON-02 | U2.3 | Offers прив'язані до mechanics/unlocks/sidegrades/context/cadence/price; зрозуміла цінність; допустима функціональна перевага часу/можливостей/сили має прозорий розрахунок і окремі змагальні умови за P1-C | concepts/preproduction/qa |
| ECON-03 | U2.3 | Nonpayer/low payer/payer порівняння dominance/time-to-unlock/failure walls; player enjoyment первинний | qa/liveops |
| ECON-04 | U2.3 | Випадкові paid rewards лише за вибором: disclosed odds, duplicates/pity/audit/age-market eligibility | preproduction/release |
| ECON-05 | U2.3 | Season pass/subscription/ads/bundles не нав'язувати списком; обрані моделі мають всі state/error/refund cases | build/release |
| UX-01 | U2.4 | Screen/state/transition atlas: first open→menus→gameplay→results→shop→settings→account→all errors | preproduction/build/qa |
| UX-02 | U2.4 | Кожний input→condition→state/effect→animation/audio/haptic→save→analytics/recovery | preproduction/build |
| UX-03 | похідна | Accessibility, localization/UA glyphs, safe areas, thumbs, font scaling/reduced motion/color/audio controls | preproduction/qa |
| ART-01 | U2.5,U2.7 | Universe/character/props/materials/light/UI coherent art bible й actual editable sources | assets |
| PHYS-01 | U2.4,U2.7 | Per object/body mass/collider/friction/restitution/joints/contact, fixed tick/units/input/camera | preproduction/build |
| ANIM-01 | U2.7 | Per-limb rig/weights/constraints/IK, clip curves/events/blends/contact and engine import proof | assets/build |
| AUDIO-01 | U2.6 | Повне music/SFX/ambience/UI audio design з першого menu до кожної action та interruption | preproduction/assets |
| AUDIO-02 | U2.6 | Actual quality music/session/stems/loops/transitions/SFX/mix/listening; no primitive WAV substitute | assets/qa |
| AUDIO-03 | U2.6,U2.7 | Узгоджені sound palette/visual motif, provenance/licenses/commercial use, доступний quality tool route | assets |
| HAPT-01 | U2.6 | Event-specific restrained haptics, intensity/duration/cooldown/native fallback/settings/real device tests | preproduction/build/qa |
| TOOL-01 | U2.7 | Tools вибираються за actual task/quality/device/license/budget; без автоматичних платних subscriptions | director/assets |
| TOOL-02 | U2.7,U2.8 | Потрібний plugin/MCP/CLI discover/install/test/rollback; capability bridge Work↔Codex | director |
| NATIVE-01 | U2.8,U2.9 | Запит platform scope до залежних робіт, engine/renderer ADR, pinned compatible toolchain | preproduction |
| NATIVE-02 | U2.8 | Android debug APK і release AAB у обраному scope з receipts; actual signing/test status | build |
| NATIVE-03 | U2.8 | iOS simulator .app, xcarchive, device/IPA/TestFlight — різні outputs, Mac/signing/UDID/access constraints | build/release |
| STORE-01 | U2.8 | Current official store SDK/API/privacy/payment/test/metadata requirements перевірені на date release | release |
| CHOICE-01 | U2.9 | Матеріальні розвилки питаються до залежних дій; чинні відповіді зберігаються без повторних анкет | all |
| DATA-01 | похідна | Save schema migration/rollback/conflict/offline/cloud/clock/device interruption; reproducible seed state | build/qa |
| MONEY-01 | похідна | Receipt validation/idempotent grants/restore/refund/revoke/offline pending; sandbox≠real payout | build/qa/release |
| PRIV-01 | похідна | Data inventory/SDK consent/deletion/account/auth/privacy manifests/retention; не вигадувати legal policy | studio/build/release |
| PERF-01 | похідна | Representative devices: FPS/frame pacing/memory/thermal/battery/loading/download/audio voices | build/qa |
| QA-01 | U1,U2.12 | Незалежні actual reviews, requirement evidence, hashes, regression by dependency; не рольовий театр | all |
| QA-02 | U2.2,U2.3 | Real user playtests/cohorts відокремлені від AI critique/simulation/desk research | concepts/qa/liveops |
| OPS-01 | U1 | Rollout/monitoring/alerts/support/incident/hotfix/rollback/forward-save migration/maintenance | release/liveops |
| OPS-02 | U2.2,U2.3 | Content cadence, live economy version/kill switch/experiments with guardrails/statistical limits | liveops |
| AI-01 | U2.12 | File-based context, requirement index, selective retrieval/RAG тільки за потребою, source provenance | director |
| AI-02 | U2.12 | Resource-aware decomposition, adaptive actual agents/QA, checkpoints/caps, no redundant broad loops | director |
| AI-03 | U2.12 | No mandatory LangChain/paid APIs/vector DB; useful orchestration/MCP only measured task fit | director |
| LIC-01 | U2.6,U2.7 | Rights ledger per asset/font/audio/plugin/engine, license notices/runtime/store compatibility | studio/assets/release |
| GUIDE-01 | U1, PS | Людський full step-by-step guide, commands/prompt/environment/output/next step на кожному етапі | director |

Жоден validator наявності файлів не доводить, що ці вимоги по суті виконані. Scope requirements, негативні сценарії, actual evidence та незалежний предметний висновок є обов'язковими. Універсальні retention/доходні цільові цифри не закладати як факт; їх задають проєктні гіпотези й перевіряють відповідними спостереженнями.

## Обов’язкове уточнення 2.0.0

UA26-EXP-01…10 з [experience-contract.md](experience-contract.md) уточнюють, а не скасовують наявні ID. Точні вихідні слова і відображення містить `assets/user-intent-sources.json`; brief є інтерпретацією, не дослівним user message. У проекті зберігати фактичний current source та scope. Ієрархія: чинні прямі вимоги й дозволи користувача → прийнятий задум та обов’язкові предметні обмеження → специфікації/контракти → виконання. Новий запит не стирає незгадані must; конфлікт матеріальних вимог виносити на рішення з впливом, а не мовчки послаблювати.

Перед залежною роботою перевіряти поелементно due must, decisions, knowledge та hashes. Future-stage доказ залишається pending з due gate; missing capability — blocked, не N/A. Жоден середній score не компенсує проваленого must. Coverage з’єднує джерело → requirement → interaction/progression/commerce/art → spec/asset/code → актуальний evidence → review/acceptance. Нове знання має source/confidence/scope/dependencies; відкриває лише залежні перевірки.

## Обов’язкове уточнення 3.0.0

Джерела — точні витяги запиту `dd9e0086-c436-4300-b7b9-51cd0302dc42` у `assets/systemic-user-sources.json`, дата 02.11.2026 (Europe/Kyiv). Зберігати старі IDs/джерела; наведені checks конкретизують їх. Виконання — за [systemic-design.md](systemic-design.md).

| ID / source | Due check | Подальше споживання |
|---|---|---|
| UA26-SYS-01 | До кожного зображення: перевірений доступний visual production profile, підтриманий camera/HUD/animation/source route, scene budget і element-to-assembly map; після вибору exact original/hash лишається референсом. Actual native/device parity довести на належному пізнішому gate. | preproduction/assets/build/qa:source→runtime parity; release/liveops:truthful continuity |
| UA26-SYS-02 | Для кожного ілюстрованого кандидата: причинний граф сімейств механік, замкнені міжсистемні ланцюги, різні рішення у конкретних контекстах і контрфактична перевірка; кількість правил не доводить глибини. | preproduction/build/qa:виконувані взаємодії й counterfactual regression |
| UA26-SYS-03 | Карта action intent → input/context → readable state; стабільні жести, two-thumb simultaneous-load case, first/normal/peak HUD і передбачення/помилка/відновлення без прихованої незручності. | preproduction/assets/build/qa:control/UI/state/accessibility contracts |
| UA26-SYS-04 | Змістовна гіпотеза додаткового досвіду: baseline та альтернатива в тій самій ситуації, відмінні рішення/ритм, tradeoffs, trial, повторне використання, повна free/no-offer арка та cumulative dominance counterexample; декор не підміняє цей brief. | preproduction/build/qa/release/liveops:actual offer/entitlement та cumulative fairness |
| UA26-SYS-05 | Ранній/середній/пізній досвід змінює можливості, розуміння й цілі; нова можливість переосмислює стару задачу. Content grammar має конкретно різні рішення, finite launch capacity й причину повернення; seeds/арени/+HP самі не закривають вимогу. | preproduction/build/qa/liveops:unlock/content/return regression |
| UA26-SYS-06 | Контекстні ресурси/характеристики мають джерело, перетворення, альтернативну витрату, cue, відновлення та наслідки в інших системах; показати конфлікт витрат і decision-changing cycle, не квоту валют чи смуг. | preproduction/build/qa/liveops:resource transforms/save/economy regression |
| UA26-SYS-07 | Зрозуміла цілісна фантазія, цілі й арка відкриттів поєднують системи в повну гру; дивний гачок або одна вузька активність не заміняють багатошарову концепцію. | all:цілісна promised experience й збереження scope |

У concepts checks застосовні до **кожного** кандидата до ілюстрації; actual image inspection — до показу. На наступних стадіях ті самі IDs посилаються на розгорнуті spec/source/code/evidence, а не закриваються заново порожнім текстом. Structural pass не є semantic pass; native/device/human claims мають окремі due evidence.
