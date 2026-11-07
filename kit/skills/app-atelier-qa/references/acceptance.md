# Контрактна й продуктова матриця QA

Цей каталог задає coverage, а не готовий oracle для виконавця. Прочитати актуальні case fixtures окремо.
Стартовий погоджений профіль містить 44 cases; зміни вимог адресно розширюють його.
Не оголошувати випадок пройденим через наявність його номера в звіті.

## Контрактні cases

| ID | Предмет перевірки |
|---|---|
| TEST-01 | Один продукт на роки; інцидент веде до ремонту, не нового портфеля |
| TEST-02 | Ціль прибутку з чинного профілю; розрахунок/бажання не називаються гарантією |
| TEST-03 | Нуль нових витрат до бюджету; free tier не є необмеженим |
| TEST-04 | Власник керує агентом; щоденні продажі/контент/дзвінки не приховані |
| TEST-05 | B2C пріоритет; сильний B2B допустимий без прихованих ручних продажів |
| TEST-06 | Окремі ринкові треки з профілю; не той самий перекладений список |
| TEST-07 | Домен відкритий; професійна відповідальність не підміняється AI |
| TEST-08 | Конкуренція виправдовується доказами, не словами «UX/AI краще» |
| TEST-09 | Автомодерація/автоматизація має фактичні межі й uncertain route |
| TEST-10 | Повний core самостійних Android/iOS/web; landing не є web продуктом |
| TEST-11 | API залежність і recurring cost обґрунтовані; lifetime витрати враховані |
| TEST-12 | Монетизація має причинну модель і глибину вже в концепції |
| TEST-13 | Free/paid boundary не нав’язаний і не має прихованих лімітів |
| TEST-14 | Реклама позначена, ненав’язлива, не блокує critical action |
| TEST-15 | Підписка дає recurring value; разова функція не маскується |
| TEST-16 | Local/cloud рішення явне; локальні дані не відправляються мовчки |
| TEST-17 | Немає human experiments на всіх фазах; synthetic не є demand proof |
| TEST-18 | Acquisition з нульової аудиторії автоматизований без гарантованої вірусності |
| TEST-19 | Ширший scope не отримує вигаданого строку або тихого зниження якості |
| TEST-20 | Тематичний унікальний зручний дизайн; accepted final не замінено placeholder |
| TEST-21 | Accessibility/старі пристрої/offline оцінені за аудиторією |
| TEST-22 | Окремий brand; Попередні бренди, персонажі та їхні активи не успадковані автоматично |
| TEST-23 | Work/Codex install/discovery/use розділені; ZIP не є installation |
| TEST-24 | Власник обирає напрям/концепцію/дизайн/бюджет/readiness; чинне не перепитують |
| TEST-25 | Monitoring називається активним лише після запуску/alert proof |
| TEST-26 | Компетенція support не є вже запущеним ботом або імпортом попереднього бота |
| TEST-27 | Підтримка реально в Android/iOS/web і погоджених bot channels, не лише посилання |
| TEST-28 | Own-context scopes; немає A→B access/AI egress/public index витоку |
| TEST-29 | Challenge/replay/revoke/webhook/group/logout-cache negatives |
| TEST-30 | Версійована KB/тон; stale/injection не переписує правила |
| TEST-31 | Read-only/scoped effects, cap/fallback, case workflow без fake operator |
| TEST-32 | Continue/pivot/stop thresholds не змінюються після невдачі для виправдання |
| TEST-33 | Спочатку широка карта, потім звуження; немає випадкового full build |
| TEST-34 | Інтерактивний representative prototype, не лише красивий рендер |
| TEST-35 | Короткий статус, докладні матеріали й змістовний чат-розбір |
| TEST-36 | Versioned memory/resume; unknown effects не відтворюються наосліп |
| TEST-37 | Реальний інший QA actor, метод/proof/межі; self-check не independent |
| TEST-38 | Ранній current release/account/cost/testing feasibility до значного build |
| TEST-39 | Backup/restore, code/data rollback, revoke/delete/export/end-of-life |
| TEST-40 | Один інтегратор, bounded owners/paths/caps; без постійної ради |
| TEST-41 | Реальні source/manifest/guide/install bridges; відсутні fake paths/commands |
| TEST-42 | Можна відхилити всі непридатні напрями; must не компенсує середній бал |
| TEST-43 | Conditional entitlement lifecycle, restore, duplicate/order/refund/revoke, sandbox |
| TEST-44 | Store preflight invalidation, current prerequisites і delta рішення при конфлікті |

## Додати продуктово змістовні cases

Core: повний результат, перезапуск/повернення, invalid/empty/large input, cancel/retry/recovery.
Дані: міграція зі старої версії, пошкоджений ввід, sync conflict, delete/revoke/export і backup restore.
Auth: guest, два різні subject/tenant, недовірені IDs/attachments/cache, logout/expired permissions.
Payment за моделлю: pending/success/failed, restore, duplicate/reordered event, expiry/cancel/refund/revoke, unknown result.
Support: усі адаптери, різні права, linking/revoke, KB version/injection, AI/API cap/outage, unresolved case.
UI: accepted masters/states, різні viewport/input/navigation, text/contrast/focus/accessibility та offline/degraded.
Operations: budget cap, зовнішній outage/quota, monitoring alert, rollback compatibility, secret/log hygiene.
Не вимагати всіх випадків від кожної маленької правки; застосовність/вплив обґрунтувати по scope.

## Висновок і gates

Для кожного due must потрібні actual subject hash, actor independence, метод, execution/proof і limitations.
Document review не закриває реалізацію; mocks не закривають provider/device integration.
Неперевірений доступ або недоступний пристрій — blocked; N/A має предметну причину.
Окремий майбутній proof — pending з owner/due gate, без удаваного passed.
Critical privacy/auth/billing/spend/release finding не компенсувати кількістю інших pass.
Фізичний representative device proof вимагати для заявлених властивостей; simulator чесно позначати окремо.
За store/no-human конфлікту не рекрутувати людей, не вигадувати аккаунти й не знімати платформу мовчки.
Не обіцяти прибуток або UX-валідацію реальними людьми за synthetic/desk evidence.
Завершувати QA scoped verdict; readiness та точний зовнішній випуск лишаються рішеннями власника.
