# Усі екрани й взаємодії

## Інвентар reachable UX

Перелічити boot/splash, loading/update, first-run onboarding, consent/permissions where applicable, account/guest/link/delete, main hub, profile, settings, accessibility, controls/tutorial/practice, loadout/collection/upgrades, shop/offers/pass/events, level/run selection, gameplay HUD, pause, disconnect/reconnect, win/fail/reward/retry, progress/unlock, leaderboard/social if applicable, credits/support/privacy, error/maintenance, suspend/resume/quit/return. Категорію absent-by-design обґрунтувати; не створювати непотрібний account лише для чекліста.

Для кожного visible screen/overlay/state:

- stable screen/state ID, purpose, entry guards, source of truth, empty/loading/populated/error/offline/locked/disabled/selected/focus states;
- exact visible text/resources, source data IDs, hierarchy, CTA, back/escape/system gesture behavior, validation and feedback;
- logical coordinate system, anchors/constraints, safe areas/notch/keyboard, min/max aspect/font scale, localization expansion/RTL if supported;
- inputs, gesture ownership, hit areas, focus/order, duplicate input protection, cancel/retry/idempotency;
- animation timeline/easing/duration/interruption/reduced-motion behavior;
- audio/haptic cue IDs, concurrency/priority, mute/reduction/haptic settings;
- transitions, side effects, persistence, permission or payment boundary, failure/recovery and acceptance.

## Transition row

`from_state + event + guard → side effects + next state + feedback + persistence + recovery`.

Не описувати тільки happy path. Приклад upgrade: insufficient earned currency→disabled CTA + clear deficit/earned route; request pending→prevent duplicate; success→wallet/item revision + feedback; timeout→reconcile with authority; return after kill→show actual result once; refund/revoke→consistent inventory state. UI animation не має виконувати grant самостійно.

## Input/gameplay boundary

Touch areas must not conflict with system edges, HUD, dominant thumb or camera controls. Specify gesture arbitration (tap/hold/drag/swipe/multi-touch), thresholds/units, dead zones, sensitivity, buffering/coyote time if applicable, release/cancel semantics and pause. Movement/jump/aim action rules must match animation/physics. Feedback on invalid action should explain relevant cause without noise.

Settings include separate music/SFX/voice, mute, haptic intensity/off, reduced effects/motion, color accessibility, language, controls and privacy/account options that actually exist. Respect platform audio interruption/background behavior. Accessibility cannot rely only on color, sound or vibration to convey essential action. Test readability at target gameplay size, not only on desktop artboard.

## Coverage

Build a directed state graph from real data; check unreachable states, missing transitions, dead ends, unsafe Back, repeated purchase/claim and unresolved modal stacks. Trace every screen entry and system lifecycle transition. Critical money/save/auth/delete/consent paths need all reachable transitions and fault injection; other combinations use explicit risk coverage with residual limitations. Never claim every mathematically possible touch sequence tested.

High-fidelity targets must cover every screen family and distinct material state, including errors/purchase/loading/late game. Component reuse can cover repeated layout behavior if mappings and exceptions are explicit. Wireframes are architecture aids, not final visual approval. Long translations and narrow devices must retain hierarchy and action affordance.

## Камера й навчання як поведінка 4.0

Розділяти оглядовий кадр для презентації та gameplay framing. Для each camera state задати key-object screen-size envelope, visibility/reaction requirement, follow/lookahead/zoom/damping, offscreen threats, obstruction і transitions. Не вміщувати весь світ ціною втрати керованої дії. Не обирати рухому камеру лише заради різноманіття: фіксована теж допустима, коли обґрунтована механікою.

Навчання — граф залежностей умінь. Для кожної можливості: передумова знань, природний trigger, коротка cue, safe practice, meaningful application, combination, independent transfer; skip/replay/return та assistance після помилки. Відкривати UI/resources/shop у момент потреби. Не вважати показ повідомлення засвоєнням; окремо перевіряти дію без підказки автора. Невдало використаний жест може бути проблемою input/camera, а не «неуважністю гравця».

## Намір, commitment й збереження

Тримати intent/action/input/presentation окремо. Pointer ID ownership, recognizer thresholds/units/hysteresis, preview/commit/cancel/refund, system gesture/capture/modal transitions і pause/resume мають input traces. Camera requests мають priority/owner/release/return без oscillation; attention arbitration визначає aggregate/defer/drop/mix critical cues.

Для back/exit/crafting/story/respec/route вказати irreversible boundary і recovery. Навчальна remediation відрізняє unseen affordance, unknown rule/input, recognition defect, timing mistake й експеримент. Повторний вхід відновлює meaningful goal/context без примусової спойлерної відповіді. Локалізація включає string/context/plural/placeholders/terms/units/price/glyph/fonts/RTL за мовами.

UI status розрізняє local saved/cloud pending/synced/conflict/error; ordinary combat cue не чекає storage/network. Критичний success не випереджає належну durable/verification boundary.
