# Якість кожної функції

## Feature receipt

До коду: requirement IDs → frozen decision/data refs → test fixtures → expected player-visible outcome. Після коду: changed source/assets → imported runtime bindings → actual build/device → raw evidence → independent reviewer. `assets/feature-slice.example.json` показує форму; приклад не є actual receipt.

| Напрям | Приймання функції |
|---|---|
| Gameplay | input/cancel/edge cases, correct timing/physics, readable feedback, success/fail/retry |
| Presentation | approved materials/palette/fonts/layout, whole-frame composition, correct asset IDs |
| Motion | anticipation/contact/recovery, collision/rig, interruption/blend, camera, no full-frame fake bounce |
| Audio/haptics | exact cue event mapping, mix/polyphony/ducking, contextual feedback, mute/reduced/no-support |
| UI/state | every relevant loading/empty/error/offline/disabled state, focus/back/touch ownership |
| Data | atomic writes, migrations, idempotency, clock/network/state conflicts |
| Performance | representative lower-tier device, worst-case content, frame-time/memory budget |
| Rights/accessibility | provenance/license, contrast/scale/reduced motion/audio captions where applicable |

Для маленької invisible fix не вимагати новий soundtrack. Задокументувати dependency impact і повторити реально зачеплені checks. Для нової видимої функції не відкладати motion/audio/UX до невизначеного фінального polish.

## Причинний scope функції

Feature receipt має current model hash/object IDs, dependency closure, runtime bindings і canonical scenario IDs. Expected outcome задавати до реалізації з design oracle; observed behavior записувати після actual run. Для нової capability перевірити changed decision і without-rule counterfactual; для actor/world/equipment — релевантну комбінацію з іншою системою; для reward/offer — durable grant і meaningful use/free alternative. Не вимагати full-game replay для invisible repair, але не закривати видиму системну функцію тестом одного setter.

До масового контенту потрібен representative slice; до beta — повний approved finite inventory/flows; до release — per-platform QA та актуальні store/commerce/privacy вимоги. Непроведені device/human checks лишаються scoped gaps із owner/due gate. Model structural pass і independently observed outcome зберігати окремо.

## Repair cycle

1. Reproduce на exact build/state/input; зберегти failing evidence.
2. Порівняти із frozen expected outcome незалежно від implementation.
3. Знайти cause й affected dependency closure.
4. Зробити найменший повний repair, включно з source asset/data якщо дефект там.
5. Targeted regression + required adjacent checks.
6. Незалежний від автора QA підтверджує closure; для material change повернути user decision.

Після двох однакових безуспішних attempts змінити діагностику: instrumentation, minimal repro, інший owner/tool, rule/source audit. Не ганяти всю stage council для зміни відступу. Не закривати баг словами «має працювати».

## Fidelity та performance conflict

Спершу profile, потім оптимізація. Визначити CPU/GPU/memory/IO bottleneck, зміряти representative scene, запропонувати оптимізацію без зміни observable target: batching, atlas, LOD із tested silhouettes, mesh compression, pooling, audio voices, deterministic scheduling. Якщо в межах target hardware baseline недосяжна — показати actual comparison і tradeoff користувачу; не вимикати важливий ефект мовчки.

## Test selection

Писати тести для invariants, boundary/fault cases, recurrence ризиків і deterministic data validation. Не створювати сотні checks лише для test count або mirrors implementation. Перевірка getter/setter без ризику не замінює purchase duplicate callback, content softlock або corrupted save. Після потрібних checks не повторювати все без нових changes/concerns.

## 4.0 acceptance cases

Для affected feature перевірити all relevant rule/state/catalog/operation→consumer edges та due evidence. Damage effect: duplicate hurtboxes, snapshot/live buffs, DoT expiry/resume, actual HP vs barrier predicates, boss phase/death/cleanup й reward killboundary. Save: killed/stale/disk-full writes, two offline branches, old account callback, golden migration. Production: ignored parameter/semantic loss/unknown attempt/assembly mismatch.

Повторити design-derived cases після зміни closure; self-check і незалежний review різні. Structural pass не закриваєту modality, яку feature обіцяє.
