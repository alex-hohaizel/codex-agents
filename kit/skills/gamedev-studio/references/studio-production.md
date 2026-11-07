# Виробництво ідентичності та налаштування студії

У 3.0 використовувати [creative](domains/creative.md), [lifecycle](domains/lifecycle.md) та [Game Model workflow](game-model-workflow.md) за предметом роботи. Прийнятий brand envelope обмежує studio assets/usage; game-specific style, camera, engine, сюжет і монетизацію визначати окремо. Не перетворювати runtime/DCC constraints поточного host на глобальну заборону художніх напрямів.

## Канонічна ідентичність

Статуси розрізняються: chosen name, chosen visual direction, approved master, production derivative, configured account/service. Один не виводиться з іншого. Файл record містить `asset_id, family, source_id, source_sha256, operations, export_path, export_sha256, dimensions, format, color_space, alpha, usage, limitations, rights_ref, inspection_ref, approval_ref`.

Original master зберігається незмінно. Похідні не повинні незалежно перемальовуватися щоразу новим prompt. Для точного reuse робити extraction/crop/compositing/export із тих самих sources. Якщо text/mark існує лише у raster concept, editable recreation потребує explicit design target і actual comparison; файл із розширенням SVG може містити raster або нову геометрію, і ці випадки треба підписати правдиво.

## Що перевіряє visual QA

| Ознака | Перевірка | Провал |
|---|---|---|
| Знак/персонаж | silhouette, proportions, expression, details, edge/texture language | Ті самі кольори, але інше обличчя або форма |
| Wordmark | exact lettering, spacing, baseline, irregularities, proportions | Підставлений «схожий» шрифт або нові літери |
| Матеріал/світло | intentional texture, depth, shadow, contrast і color role | Плоский polygon замінює об'ємний папір/дерево без вибору |
| Composition | relative placement/scale, clear space, crop envelope | Compact export довільно міняє взаємне розташування |
| Повнота | full board/profile/header/store families; readable small sizes | Один гарний board, неперевірені похідні |
| Source chain | actual source→operation→output; fonts/images rights | «Векторний» заявлений лише за extension |

Technical hash перевіряє bytes, а не візуальну еквівалентність. QA використовує actual image view з exact subject refs; не вигадує перегляд недоступного зображення. За збільшенням не можна обіцяти відновлення втрачених detail без нового рішення.

## Переносний production scope

За потребою студії: primary/wordmark/icon, light/dark/mono/compact, RGB/alpha exports, developer profiles/header, website/social, splash/about/credits usage, font files/license, palette/tokens, clear space/min size. Немає потреби створювати довільні social accounts або 50 розмірів без реального target. Неактуальні store pixel constraints перевіряти перед export; template не замінює чинні вимоги.

## Реєстр studio operations

Для кожного `task_id`: purpose, required_or_optional, target_environment, required_access, owner, upstream_tasks, exact verified official URL/date, action_steps, expected_cost, ongoing_cost, output_identifier, done_check, observed_state, blocker, rollback_or_recovery, next_skill_use.

Групи: identity/контакти; account/entity/verification; domain/site/support/privacy; repo/CI/signing/secrets; platform accounts/agreements/payouts; analytics/crashes/consent; commerce/ads/backend/storage лише за потребою. Прізвище/бренд/юридична назва не взаємозамінні. Невідомий legal entity/account ID лишається pending, не вигаданим рядком. Студія як бренд не створює legal incorporation.

Виконуй підтримувані account/setup actions достатнім доступним plugin/API/CLI або дозволеним browser у чинному scope згоди. Власнику передавай точний blocked step для MFA, особистого legal/signature confirmation чи відсутнього доступу; не роби весь setup ручним автоматично. Інструкція має вести click/command→expected result→verification для конкретного середовища, без заяви про виконаний крок до спостереження. Зміни тарифів, store policy й fees перевіряються на момент дії офіційно. Платний account може бути неминучим для публікації; це показують окремо від нульової додаткової вартості локальних tools.

## Operation admission замість списку software

Для actual target вибрати input→tool/API/CLI/GUI operation→editable output→export/import→consumer→validation. Must-фільтри формату/quality/платформи/прав/privacy/доступу/бюджету перед score. Перевірити schema/catalog/required fields/parameter consumption; generic prompt не породжує автоматично layers/rig/geometry/stems.

Witness фіксує exact input/output hashes/version/host/target/method/limitations і freshness. Unknown remote job outcome спочатку reconcile;нові витрати лише у чинному scope. Для native SDK операцій operation witness не замінює signed release conformance.
