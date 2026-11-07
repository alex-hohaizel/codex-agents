# Liveops playbook

## Зміст
1. Джерело правди та telemetry contracts
2. Діагностика progression/retention
3. Економіка та покупки
4. Контент і сезон
5. Експерименти
6. Інциденти/patch/migrations
7. Витрати/privacy/support
8. Вихід та escalation

## 1. Джерело правди та telemetry contracts

Поточний runtime не визначається лише git HEAD. Зіставити store build, client config/content manifest, backend deploy, catalog/economy/save schema, feature flag cohort і studio/game identity revisions. Query або export з часом і exact source зберегти поруч із висновком. Агрегати не повинні містити необов'язковий PII; pseudonymous ID не означає автоматично anonymous data.

Подія має: event ID/name/version, logical occurrence identity, timestamp та clock/source, session/run/player pseudonymous key за релевантності, platform/build/config/experiment, allowed props/types/units, consent requirements, delivery/retry/dedupe policy, destination/retention/deletion. Надійність funnel перевіряється: lost/duplicate events, app kills, offline buffering, clock skew, schema drift, bots/internal tests. Purchase server truth та client purchase UI — різні сигнали.

Збір мінімум потрібний для продуктових питань: first launch → tutorial step → first meaningful action → run start/build choice → death/win/abandon → reward accepted → unlock → next run; market exposure/decline/store sheet/pending/verified/refund; content seed/version і obstacle/build IDs для аналізу. Не трекати кожен frame або raw input без потреби. Помилки/креші зі symbols і safe context; не викидати auth tokens/особисті тексти в logs.

Для metric dictionary визначити numerator, denominator, window, timezone, eligible/excluded users, session boundary, platform and acquisition filters. Retention calendar-day і rolling 24h відрізняються — вибрати й позначити. Між build/cohort порівняннями враховувати mix країни/device/channel та temporal confounders.

## 2. Діагностика progression/retention

Розкласти причини повернення: learn/master movement; discover meaningful combinations; complete run arc; pursue unlock/collection/meta milestones; challenge higher difficulty; social challenge/share; new curated content. Для кожної — state/decision/feedback/reward/future opportunity і expected learning evidence. «Буде затягувати» без цих зв'язків — hypothesis, не дизайн.

Для run-local progression вимірювати час до нового meaningful choice, viable build diversity, completion/abandon distribution, cause of death/readability, failed-run retained value, повтор encounter/route. Для meta — time-to-unlock distribution, optional grind, power ceiling, difficulty unlock, remaining meaningful goals, content exhaustion. Проста кількість перестановок не доводить різноманіття: комбінації можуть давати той самий optimal strategy або бути непрохідними.

План repair має конкретний механічний вплив: новий traversal verb → obstacle grammar та teaching beats → additional valid routes → build/score trade-off → content production cost → onboarding/UI/audio/haptic changes → tests. Нову арену не називати progression, якщо вона не змінює вибір/навички. Не переносити Dead Cells/Vampire Survivors структуру механічно на кожну гру; порівнювати функції (run arc, unlock gates, combinations, mastery) з core input конкретної гри.

Збирати player feedback добровільно в доступних рамках; review/support claims — сигнал, не репрезентативна вибірка. Аналізувати behavior + qualitative evidence. Надмірна довга сесія сама по собі не є success: перевіряти зрозумілі паузи/фінал, frustration й повернення.

## 3. Економіка та покупки

Баланс зберігається як ledger операцій: source/sink, item/currency, amount in integer units, balance, reason, transaction/reward identity, catalog/economy version. Перевірити conservation, duplicate grants, negative balance rules, offline merge, restore/refund semantics, inflation, resource hoarding, endgame sinks. Simulator має відтворюваний seed, cohort assumptions, uncertainty/sensitivity та output; він не замінює real telemetry.

Для кожного offer: audience eligibility, unlock timing, explicit value, store price, purchase type, earned/free route, power envelope, duration/expiry, UI entry/exit, cap, cancellation/pending/failure, restore/refund, telemetry, operating cost. Player sees whole offer before commitment; multi-currency conversion не приховує реальну вартість. Зайва валюта має доведену роль у game loop; не додавати п'ять ресурсів лише за зразком іншої гри.

Characters/weapons/skills мають sidegrade tests: range, aiming, movement, timing, counters, skill ceiling, viable builds, nonpaying path/time, PvP fairness якщо є. «Не pay-to-win» доводиться power bounds і outcomes за подібної mastery, а не словом у PDF. Випадкові paid items: pool/version/weights/pity/duplicate conversion/guarantees/caps/disclosure + real draw audit, country/age review. Шанси не змінювати потай у liveops.

Refund/chargeback: відв'язати legitimate cancellation від fraud; не знищувати save або карати гравця автоматично без визначеної політики. Спожита валюта, negative balances і revocation — продуктове рішення з UX/support; реалізація має бути deterministic/reconcilable. Subscription cancelled може зберігати access до expiry; «cancelled» не завжди «expired».

## 4. Контент і сезон

Кожний content release: manifest version, compatibility/min client, dependency hashes, editable source/runtime exports/provenance, curated progression placement, difficulty/reward budget, generator grammar/constraints, seed suite, novelty/repetition budget, teaching/feedback, UI/localization, sound/music/haptics, memory/download/performance budgets. Перевірити unreachable geometry, broken collisions, unfair spawns, impossible item combinations, no-escape states, stale thumbnails та missing audio events. Нескінченний генератор без validated grammar не є нескінченним хорошим контентом.

Сезон: start/end/timezone, eligibility, free/paid tracks, XP sources/caps, expected completion distribution для різних cohort, carryover/claim grace, rewards after season, purchase close time, offline/time skew, refund, entitlement retention, old client behavior, remote config validation. Вказувати реальні production/QA hours і asset budget. Для solo studio не обіцяти щотижня нову дорогу біому без authoring capacity.

Identity conformance: ті самі accepted master files/tokens, model proportions/topology/rig/deformation, lighting/camera/materials, UI components/fonts/icons/motion, sonic motif/instrument palette/stems, haptic semantic patterns. Golden comparisons за однакових scene/seed/camera/device capture. Якщо art direction змінюється — material choice + new baseline, а не приховане «оновлення якості».

## 5. Експерименти

Спочатку перевірити, чи достатній observational diagnosis або deterministic regression test. A/B — не обов'язковий overhead кожної правки. Якщо потрібний: hypothesis/mechanism, primary metric, guardrails (crash, churn, frustration, complaints, purchase/refund, fairness), eligibility/randomization unit, persistent allocation, exposure logging, duration/sample plan, statistical method, expected confounders, stop/rollback, ethics/privacy scope, owner і decision date.

Не змішувати changing build/content/economy з treatment без плану; не оголошувати causality з самовибраних cohort; не закривати тест після першого зручного p-value. Статистична значущість не доводить практичну користь або відсутність шкоди. Low traffic → uncertainty interval/qualitative study/longer collection, не fabricated confidence. Сегменти не використовувати для прихованих exploitation цін або погіршення baseline у вразливих гравців.

## 6. Інциденти/patch/migrations

Incident record: start/detection/scope, affected build/platform/regions/cohorts, user impact, timeline/facts, severity, owner, evidence, mitigation scope/authorization, exact actions/provider receipts, recovery verification, follow-up. Спершу зберегти evidence; не робити destructive repair за припущенням. Комунікації іншим/гравцям лише за окремим дозволом або прямо дорученим workflow.

Triage: crash/ANR, save loss, payment duplication/loss, generator softlock, performance/thermal, ad compliance, privacy leak, backend outage/cost. Mitigation: halt rollout, disable exact flag/offer/content, server config revert, backend rollback, safe save repair, binary forward hotfix. Store binary rollback не миттєвий. Для save/economy migration: source+destination schema/version, idempotence, interruption recovery, backup, checksum, downgrade/read compatibility, older clients, replay/duplicate handling, restore test, rollback або explicit irreversible boundary. Local users' progress не можна просто «reset для виправлення» без дозволеного recovery policy.

Code/native changes → build → independent QA → release. Content-only changes → schema/assets/gameplay/economy/compatibility QA → manifest/signature/hash → staging → allowed rollout. Reuse evidence лише для unchanged dependency closure; shared material/rig/audio bus/economy coefficient змінює downstream acceptance.

## 7. Витрати/privacy/support

Cost record: fixed account/hosting, variable requests/storage/egress/analytics/ads tooling, projected realistic cohort, free-tier limit і післялімітна ціна, alerts/caps, offline fallback, vendor lock-in/export path. ChatGPT/Codex subscription не покриває backend/API accounts/paid generation. Paid provider, upgrade/scale або commercial asset purchase — material budget decision.

Deletion/export requests: verified minimal identity, defined data map/retention, execute across backend/analytics/vendors/save/account links відповідно до policy, audit completion without extra PII, distinguish legitimate financial retention requirements. Secret rotation/revocation, backup restore drills, least privilege review; не робити зайвий security theater для кожного cosmetic patch, але actual payment/privacy ризики покривати.

Support taxonomy прив'язана до build/run/transaction/content IDs без таємних даних; FAQ/known issues, owner/SLA, escalation, recovery options. Не обіцяти цілодобову службу без ресурсу. Recurring automation має explicit schedule/data sources/cost cap/notifications/stop rule; одна liveops команда — один завершений раунд.

## 8. Вихід та escalation

Пакет `liveops-handoff`: exact runtime/source versions; source queries/exports/time windows; metrics dictionary/quality notes; findings/hypotheses/confidence; decisions; repair/content/experiment specs; new assets+studio subset if needed; simulations/test evidence; migration/rollback; action receipts; updated support/runbooks; unresolved blockers; owner/next command. Може повертати upstream design/assets/build/release за dependency impact, не повторюючи всі стадії без причини.

Acceptance: reproducible evidence, no fabricated revenue/retention, no hidden style/economy changes, fair nonpaying baseline, compatibility/transaction integrity, actual cost awareness, truthful action status. Немає реального datasource — deliver diagnosis plan/templates та blocker, не «оптимізовану гру».

## Адаптивне покриття досвіду 4.0

Перед раундом зіставити actual features/domains/dependencies/scenarios з `assets/liveops-question-catalog.json`; активний domain і claim відкривають релевантні питання навіть без optional task flag. Missing telemetry/device/human evidence — unknown/not-tested з owner і способом добору; N/A дозволено лише за agreed feature absence. Вимірювальний catalog не є другою authority registry: accepted model і metric dictionary лишаються source of truth.

Зв’язати learning prerequisite → teaching opportunity → transfer task → player capability → encounter/route choice → reward/use → next voluntary goal. Це дозволяє відрізнити непомітний unlock від слабкого інструмента, непрочитаний telegraph від завеликої складності й technical grant failure від незрозумілої нагороди.

Для small/scenes/world оцінювати decision novelty, а не просторовий розмір: які constraints/стратегії/можливості змінюються, чому стара найпростіша policy вже має trade-off, як це навчається й що коштує виробництву. Finite launch exhaustion і можливості після mastery мають явні висновки. Новий content/boost/actor змінює learning, camera/input, encounters/world, rewards/progression, commerce/save/analytics залежно від власного impact; не відкривати несуміжні branches лише за звичкою.

## 4.0 cause-to-change loop

Відновити released build/config/content/save/experiment і matching symbols, actual observability/service health. Для damage/AI/failure аналізувати контекст/knowledge/input/contact/capture/resources/lifecycle/reward/save/return, а не один середній DPS. Для variation/progression зв’язати можливість×нагода/exposure/exhaustion;для paid portfolio виміряти саме погоджені power/time/access межі.

Нова recipe/tool/importer/config інвалідує залежні production witnesses/derivatives;actual attempt ledger зберігає job/outcome/cost/reconcile. Semantic transformation, cold first use/transition memory/whole assembly й signed native adapter регресії потрібні за impact. Compatibility/content epoch/patch base/golden saves/deletion tombstone захищають continuity при patch/offboarding.

Завершити bounded раунд actual findings/actions/receipts/limitations і next instruction checkpoint. Не заявляти постійний агент/моніторинг без реального сервісу/automation; нове звернення звіряє фактичний стан.
