# Системи та негативні сценарії

## End-to-end UX

Перший запуск: splash/brand → consent/age/permissions якщо застосовно → onboarding → control learning → завершення першої спроби → reward/save → наступна мета. Returning/guest/account player, no network, service timeout, missing asset, low storage, corrupted save, suspended/expired account та supported accessibility/localization мають окремі paths.

Screen-state inventory перевіряється проти runtime: кожен screen ID, loading/empty/error/disabled/selected/purchased/locked state, all navigation/back/deep link transitions, safe area/font scaling/long text/touch target/input focus. Не закривати matrix лише screenshot головного меню.

## Mechanics/physics/content

- Input: press/release/cancel/multitouch, OS gesture conflict, orientation, low FPS, background during hold.
- Physics: maximum speed, corners/stacking, tunneling, simultaneous hit/goal/death, out-of-bounds, stuck states, invalid spawn, tiny/large timestep, unit/scale mismatch.
- Generation: curated normal/boundary seeds, fuzzed seeds, grammar/reachability, hazard spacing, mandatory resources/checkpoints, load budgets, no impossible gated route.
- Variation: classify real decision/encounter changes; inspect repetition window and difficulty rhythm. Велика комбінаційна кількість без нового player choice не доводить variety.
- Recovery: bounded regeneration/fallback, fail/retry/abandon, checkpoint resume, completion and progression after prior failure.

## Progression/economy

Reachability від new profile до ключових unlocks, valid caps/resets/seasons, no circular prerequisite/softlock, meaningful mastery gains, free-path time and fairness under declared assumptions. Перевірити simulation policies: never pay, poor RNG, skilled/low time, low skill/high time, collector/endgame, lapsed return. Зіставити actual runtime rewards/costs із canonical data.

Resource precision/rounding, overflow/negative balances, duplicate grants, exchange cycles/arbitrage, concurrent claims, caps while purchase pending, upgrade changed during run, content version mismatch. Paid mechanical options: dominance/counters/sidegrades, readability, interaction із leaderboard/matchmaking; не проголошувати fairness без evidence. Offers: eligibility, cadence, price freshness/currency formatting, stale/expired state, cancel/error/back, honest rewards/odds.

## Store/ads

Sandbox cases: success, cancel, fail, pending/deferred, duplicate/reordered callback, network loss before/after charge/verification/grant/acknowledgement, app kill/restart, two devices, reinstall/restore, refund/revocation, account switch, already-owned, unknown SKU, price change, provider outage. Subscription lifecycle cases додати лише якщо обрані.

Перевірити durable reward рівно один раз й authoritative transaction binding. Client-side mock не є sandbox test. Чутливі purchase tokens/PII redacted; artifact містить sanitized references. Actual purchase test не повинен непередбачено витрачати реальні кошти.

Rewarded ads: no-fill/timeout/close-before-earned, duplicate earned callback, foreground/background, consent denied, offline, frequency cap, scene unload, restart before grant. Grant лише за valid earned event і policy; disabled ads не блокують free core.

## Save/offline/backend

Atomic-write kill points, corrupt/truncated save, low disk, unsupported schema, historical migration fixtures, rollback compatibility boundary, guest→account merge, cloud conflict/replay, clock skew, concurrent updates, server stale reads, idempotency retention, rate limits/retries/cancellation. Перевірити deletion cascade й local cached data; account deletion не дорівнює logout.

Security boundary: client-tampered reward/price/time/ID, expired/wrong account auth, cross-user access, replayed entitlement, network TLS/config, debug endpoints/log secrets. Не заявляти повний security audit, якщо виконаний лише narrowed check.

## Accessibility/локалізація

Color-independent cues, contrast/readability, touch ergonomics, font scale/long labels, reduced motion/camera shake, mute/music/SFX controls, captions/visual alternatives relevant to gameplay, haptics off, left/right-handed якщо обрано. Перевірити right-to-left лише для supported locales; unsupported languages не вигадувати.

## 4.0 causal fault suite

- Один action торкається кількох hurtboxes/substeps: перевірити accepted hit count, channels/barrier/part effects і cue dedup.
- Snapshot source/live target змінюються в DoT tick/expiry/phase: exact trace й RNG consumption; resume не повторює tick.
- Player/boss lethal + phase/stagger/objective + kill: визначений outcome/reward/save/retry, cleanup не видаєвдруге.
- Broken support міняє topology/nav/visibility/cover: plan fallback, reachability/rescue й restore coherent.
- Дві offline branches spent→crafted: max/union не повертає витрачений матеріал; старий accountcallback/tombstone не відроджуєдані.
- Provider output валіднийформат, але без required layers/rig/stems або з ignored parameter: capability/recipe не закривається.
- Exporter змінює scale/axis/contact marker/loop boundary: semanticvalidator ловитьдефектдо massproduction.
- Job outcome unknown після timeout: reconcile actual job/output/cost, не створювати duplicatepaid attempt.

Ordinary combat cue не чекає disk/cloud. Critical durable success тестуєтьсяна своїй commitboundary з failureinjection; це різні oracles.
