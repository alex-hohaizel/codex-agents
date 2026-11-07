# QA: незалежне приймання 4.0

## Визначити scope і layer

Прийняти exact revision/inputs/build/config/content/catalog/save/toolchain, source requirements, model maturity C0/C1/T та implementation stage. C1 перевіряє повноту задуму всіх представлених завершених концепцій; T — визначеність поведінки/каталогів/production handoff. Runtime/device/human/live obligations належать до due gates; паперова рецензія не підвищує layer.

Для кожного активного з 20 напрямів вивести claims, залежності, oracle source, denominator та належний спосіб перевірки. За N/A вимагати game-specific rationale, за missing capability — not-tested/blocked. Незалежний actor фактично читає/виконує артефакт; не називати автора незалежним через іншу назву ролі.

## Обов’язкові критичні зрізи

| Scope | Власні контрприклади та очікувана перевірка |
|---|---|
| Math/effects | Units/domain/round/clamp/stack/capture, NaN/∞, thresholds, channels/barrier/parts/overkill, proc dependencies; intermediate golden traces |
| Contact/time | Кілька hurtboxes/substeps на одну дію, pooled ID reuse, DoT expiry/tick/resume, pause/slow/hit stop; exact dedup/predicate |
| Death/crash | Simultaneous player/boss lethal+phase+stagger, two rescues, cleanup callbacks, reward/kill/save/retry; deterministic expected priority |
| Physics/world | Relative contact/rotational lever, missing impulse≠zero, moving support/crush/teleport, controller/ragdoll ownership, broken topology/nav/visibility/reachability |
| AI/boss | Unseen player/no knowledge, stale/shared facts, decision tie/abort/fallback, reservations, unfair overlapping attacks, phase transition/status/projectile cleanup |
| Generation/progression | Key behind own lock, unavailable counter, repair budget/fallback, novelty vs seed, capability×opportunity, late unlock/exhaustion |
| Input/learning | Pointer-index change, cancel/lost focus/modal clickthrough, peak reposition/occlusion, camera request conflict, error diagnosis/transfer/reorientation |
| Economy/commerce | Paid cumulative portfolio, partial ownership, reward once/caps/overflow, retry/pending/refund/consumed restore/offline branches; sandbox evidence |
| Persistence | Kill на кожній критичній межі, stale write/disk full/corruption, precision, two offline branches, delayed old-account callback, golden migration, cold restore/delete |
| Production | Descriptor/catalog/argument drift, ignored material parameter, output without layers/rig/stems, units/axes/contact-time loss, source roundtrip/import/assembly mismatch |
| Runtime/craft | Cold shader/audio/attack, transition memory/ownership, actual frame/input/thermal, cue arbitration/locales/mute/haptic fallback, whole-scene parity |
| Release/ops | Exact symbols/patch base/content epoch, actual data egress/SDK rights, service loss/offboarding за fit, old-client compatibility |

Simulation commit і durable commit перевіряти окремо: ordinary hit feedback не чекає cloud/disk; critical confirmed reward/spend/victory не губиться й не повторюється поза визначеною гарантією. Документальна policy не дорівнює failure-injection test.

## Приймання виробничого методу

Для operation перевірити ToolCapabilityRecord, executable recipe, semantic edges, actual attempts/unknown-outcome reconciliation і assembly evidence. Catalog verified не є operation tested; installed tool не є native integrated. Quality must не компенсується середнім score чи наявністю назви програми.

Новий consumer без попереднього чату відтворює named scenario/expected results із пакета. Брак потрібних inputs/rules/launch catalogue/state assets або прихований behavior TBD повертається відповідному owner; QA не вигадує missing design.

## Verdict

Записати per-criterion passed/failed/not_tested/blocked/hypothesis/N/A, actual evidence/time/actor/method/inputs, independent counterexample, uncertainty і coverage denominator. Для числових distributions врахувати variance/tails/thresholds; mean DPS не доводить TTK або human balance. Для perceptual/haptic/comfort/retention потрібний відповідний фактичний метод.

Repair перевіряти за causal impact closure. Після двох однакових невдач — нова діагностика. Незмінні dependencies дозволяють scoped proof carry-forward; старі 3.0 reviews не стають 4.0 acceptance. QA pass не надає publish permission.
