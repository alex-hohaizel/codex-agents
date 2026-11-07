# Приймання та виробничий план

## Вхідна карта

| Вхід | Що звірити | Куди повернути gap |
|---|---|---|
| Studio bundle | studio_id, canonical mark, legal display name refs, rights, contact URLs, splash/credits policy | gamedev-studio |
| Product decisions | platform/orientation/audience/regions, 2D/3D, offline/online, scope and spend, pricing model | gamedev-director |
| Canonical game model | schema/revision/hash, enabled domains, object IDs, dependencies/scenarios, source requirements, due gates | gamedev-preproduction/director |
| Frozen GDD/TDD | exact mechanics, controls, goals/failures, physics, animation, stage grammar, progression, economy, save/network schema | gamedev-preproduction |
| Craft baseline | accepted reference hashes, editable sources, runtime exports, import settings, motion/audio samples, rights | gamedev-assets |
| Test oracle | expected outcomes derived from design, reproducible seeds, input replays, screenshots and device budgets | gamedev-preproduction/qa |
| Runtime constraints | host, engine/render path, platform adapters, signing refs, CI/toolchain, target devices | current build owner |

Кожен gap має ID, owner, залежні tasks, stop boundary, closure evidence. Не блокувати data cleanup через недоступний iPhone; не називати всю гру готовою, якщо iPhone є обраною платформою й не перевірений.

## Зміни baseline

Використовувати immutable approved revision; не перезаписувати її файли. Зміна потребує delta manifest: requirement IDs, affected assets/screens/formulas, new samples, expected player effect, device/performance/cost impact, user choice source коли матеріально. Створити наступну revision й перенести чинні докази за exact dependency closure. SHA доводить тотожність байтів, а не схвалення або автора.

Приклад матеріальної зміни: із 3D rig перейти на 2D sprites; вимкнути dynamic shadows, що формують читабельність перешкоди; змінити physics на auto-run; прибрати платну mechanically distinct character family. Приклад routine repair: повернути font/offset до затвердженого token, полагодити duplicate reward, зменшити texture atlas без видимої зміни у прийнятих tolerances.

## План slices

Frozen GDD/TDD та runtime tables є проєкціями current model. До кожного slice додати model object IDs, expected changed decision, without-rule counterfactual за релевантністю та runtime binding/import plan. Дані самостійно не доводять actual behavior. Не переходити до масового content виробництва, доки ризиковий representative route/fidelity не закрито.

Не будувати спершу «всю логіку», потім «увесь polish». Кожен slice включає interaction, actual craft, data, errors та device/performance evidence.

1. Repository/bootstrap/export feasibility, порожня native launch (технічний smoke).
2. Representative production slice із найризиковішою механікою й кадром.
3. Повний run lifecycle та мінімум одна завершена content/progression loop.
4. Meta/economy/commerce із authoritative reward/save semantics у sandbox.
5. Усі content families, screens/states, accessibility/localization, maintenance flows.
6. Hardening, real-device matrix, packaging та independent QA.

До кожного: explicit scope, file ownership, prerequisite hashes, input fixture, expected outcome, build/device cost, stopping criterion, evidence output. Додавати паралельні tasks лише коли вони справді незалежні. Root інтегрує після частих small checkpoints, не наприкінці одного великого divergent branch.

## Definition of done реалізації

Всі погоджені features і asset IDs наявні та linked; немає placeholder substitutions у final-facing surface. Залежні native builds виконані, відсутні exports/signing названі блокерами. Runtime data відтворює frozen rules; actual screens/motion/audio порівняні з accepted targets. Самоперевірки завершені у названому scope; незалежне QA не підміняється авторським sign-off. Невиміряні retention/revenue лишаються hypotheses навіть після повної технічної реалізації.

## T admission й точний host bridge

Вхід T має повний launch catalogue/grammar, numeric/state/physics/lifecycle/AI/save/UX/creative contracts, independent expected traces, finite material inventory й executable production recipes. Behavior TBD блокує лише залежного consumer; narrow early spike допускається із питанням/inputs/oracle/stop і не називається production-complete.

Task admission перевіряє competency/host/input hash/interface/resource availability; isolated directories не ізолюють shared device/account/exportjob. Bridge фіксує exact inputs/toolchain/allowed effects/outputs/evidence і returnvalidation. Відсутній Mac/SDK/слухання не створює готовий артефакт.
