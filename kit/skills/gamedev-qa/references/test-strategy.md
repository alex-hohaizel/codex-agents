# Стратегія незалежної перевірки

## Незалежність

Автор може виконувати unit tests, smoke й self-check; reviewer відповідного результату має бути іншою фактичною особою/агентом. Фінальне full-stage приймання за істотного scope має новий незалежний погляд; не створювати формальну «раду» з повторного авторського переказу. Actual actor identity, task scope й output refs зберігати після виконання. AI roles не є людськими playtesters.

## Scope та шари доказів

| Шар | Приклад | Дозволений висновок |
|---|---|---|
| Structural | schema/files/hashes/refs | Передані bytes повні за контрактом |
| Deterministic model | economy property test, grammar validation | Модель задовольняє перевірені invariants/assumptions |
| Engine/runtime | replay, scene check, integration | Runtime у named environment відтворив case |
| Native device | install, profiler, haptics/audio focus | Named build/device пройшов визначений сценарій |
| Human playtest | actual observation/interview | Названі учасники показали спостережувану реакцію |
| Live cohort | measured retention/conversion/refunds | Названа когорта за період дала виміряний показник |

Не підвищувати шар доказу автоматично. Mock purchase не є sandbox store purchase; sandbox purchase не є real revenue; screenshots не доводять animation quality; full test suite не доводить fun.

## Матриця

Кожен requirement ID має owner, expected artifact, test method, oracle ref, current revision, actual evidence і status. Кілька IDs можуть закриватися одним scenario, якщо він справді discriminates їх. Не створювати дублікати case лише для числа тестів.

Обов'язкові групи: end-to-end user journeys; every screen/state/transition; mechanics/control/physics; generator/content/repetition; run/meta/mastery; economy/commerce; saves/migration/offline; account/privacy; audio/haptics/accessibility/localization; native/platform/performance; rights/brand/source lineage.

Для кожного вказати happy, boundary, interruption/fault і recovery cases. Пріоритет — money/data loss/privacy/softlocks/install failures, потім core gameplay/fidelity/performance, потім polish. Severity виходить із player impact, не складності fix.

## Oracles

Expected outcome має походити з approved rule/table/design, official platform contract або відтворюваного invariant. Незалежно обчислити boundary examples. Порівняння implementation із копією тієї самої формули не ловить помилкову формулу. Додати metamorphic/property tests: rerender не змінює reward; duplicate callback не змінює balance; resource conversion не створює value; generator output satisfies reachability; migration не втрачає inventory.

## Невідомості

Суперечливі design specs — `blocked` із upstream decision. Відсутній пристрій — `not_tested`; не fake pass і не автоматичний дефект реалізації. Необрана platform — `absent_by_design` якщо так визначено scope. Порожній/unsupported test account — test setup gap, не product pass. Продовжувати незалежні перевірки, поки окремий блокер чекає.

## Нормативне виведення scope 4.0

До task скласти case set за `scope-derivation.md`, current game-model/actual features, due gate та dependency impact. `qa-case-catalog.json` — patterns, не граничний перелік гри. Порожні task modality/review flags не знімають proof, потрібний фактичній feature/claim. Розбіжність model/runtime — upstream contradiction, не можливість вибрати зручніший scope. Застосовність, denominator й not-tested зберігати окремо від pass.

## Scope completeness й cold receiver

C1/T completeness перевірити окремо від files/schema: незнайомий consumer без історії чату знаходить required inputs і відтворює named сценарій/expected trace. Pass потребує конкретного artifact/method/output, не назви reviewer. Due production proof розрізняє descriptor/catalog/installed/operation-tested/integrated/native; artistic/perceptual/human/livestatus окремі.

Для numeric/riskdistribution перевірити tails/thresholds/overkill, не лише means. Для D1/D2 cross-systemcases потрібні actual expectedpriority/capture/persistence semantics; кількість tests непоказникповноти. Historical3.0proof зберегти з provenance, не успадковувати4.0acceptance.
