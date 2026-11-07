# Наскрізний studio payload

Спільний manifest/hash формат визначає handoff-contract.md. Нижче предметний вміст; він не створює альтернативний top-level manifest.

У поточній моделі studio records підключаються до канонічної Game Model через stable references за [model format](model-format.md). Studio payload лишається власником identity/source/export/service facts, а модель гри — їхніх залежних uses і впливу. Не створювати другу копію Game Model, новий реєстр згод або неявне правило «усі ігри студії мають однакову камеру/графіку».

## Склад

`studio/identity.json`: stable studio_id, display_name, legal_name/status, public developer contact/support/privacy URLs, brand revision, payload identifiers. Невідомі legal/service fields = null плюс issue ID, ніколи не production-like вигадане значення.

`studio/brand/`: immutable master, actual source materials, final exports, tokens, font/license files, approved variants, usage rules, original choices та delta records. Реальні providers/third-party rights не стають правом на репакування автоматично; за обмежень на redistribution передати законний restore route і exact limitation.

`studio/services.json`: capability, target environment, account/config identity без secret values, owner, setup status, usage constraint, cost/approval requirement і current evidence. Секрети тримати в відповідному secret store; тут тільки reference name й provisioning instructions.

`studio/setup/`: послідовна інструкція/залежності/чекліст і raw observed confirmations без приватних документів. `studio/usage-map.json`: де студія використовується у грі й store listing; яких asset IDs/dimensions/variants потребує наступний етап.

## Consumer правила

1. Intake перевіряє bytes/paths/hash/current revision; не читає тільки брендбук PDF.
2. Concept додає студійний usage map і передає весь потрібний lawful payload далі; не вводить placeholder назву іншої студії.
3. Preproduction визначає boot/splash/about/credits/legal/contact/store use cases й exact source IDs; непотрібний довгий splash не нав'язується.
4. Assets використовує approved exports/sources; новий compact/mono вариант має identity review, якщо його ще немає.
5. Build імпортує ті самі sources/approved derivatives, а runtime import/compression фіксує recipe.
6. QA звіряє actual screens/listing metadata із studio identity й legal pending issues; release не підмінює legal name display name.
7. Studio update створює нову revision з impact map. Інші producer files та історичні approvals не переписуються. Consumer мігрує залежності явно.

8. Резолвити всі передані source/evidence IDs у portable package-relative paths із bytes/hashes або явним remote restore route. Absolute path старого scratch не є переносним доказом; недоступні історичні матеріали позначати unavailable, не зараховувати їх перевіреними повторно.

Один generic README «студія TatterJack» не є payload. Точні назви, image/font bytes, current legal/status/service record мають ідентифіковані джерела. У фінальному archive не пакувати credentials або копії приватних посвідчень.

## Operation records і portable source

Для relevant brand/game production прикласти operation IDs/capability witnesses, exact recipes/semantic transformations і lawful source/exportbinding. П’ять operational record types використовуютьчинні IDs; payload невводитьдругого game-design authority. Hostbridgepinexact inputs/toolchain/allowed output і return checks; installed/catalogstatus не native proof.

Відсутні rights на redistribution не приховувати«self-contained»ярликом: передати permittedoutput+verified restore path/limitations. Current accepted master незмінний; semantic cache інвалідує тільки залежні derivatives.
