# App Atelier: предметна модель і наскрізне виробництво

Зміст: застосовність → предметні правила → стан → перетворення → виробничі записи → зріз → зміни → джерела.
Читати разом із `cross-domain-core.md`, чинними core/workflow/runtime і профілем. Цей контракт доповнює збережені REQ-ID, а не замінює їх. Профіль, ledger та economics мають окремі чинні формати, які перевіряються точними schema IDs. Попередні формати результатів не підтримуються. Встановлення навички не мігрує продукт, БД чи дані користувачів.

## 1. Вивести застосовність із продукту

Для кожного напряму в `assets/app-system.template.json` записати `required`, `conditional`, `absent_by_design` або `unknown` з причиною та due gate. Не підключати всі напрями автоматично. Відсутній SDK, інструмент, доступ або доказ для потрібної властивості — blocker, не absent_by_design. Критичний unknown має owner, питання або перевірний spike, ліміт і наступне рішення.

Зіставити: користувач/платник/предметна подія; визначення й каталог можливостей; причинні правила/обчислення; user journeys; Android/iOS/web; guest/auth/tenant; local state/restore; optional sync; API/integrations; документи/медіа/генерація; UX/motion/audio/haptic; accessibility/locales; commerce/entitlement; support/knowledge; distribution/acquisition; security/privacy; performance/cost; deploy/operations/exit. Немає універсально обов’язкових AI, cloud, microservices, підписки, RAG або аналітики. Android/iOS/web — профільна пропозиція сімейства, а не універсальна вимога до кожного доручення. Для нового продукту явно показати запропоновані платформи й зафіксувати застосовний scope до залежної обіцянки/реалізації. Для чинного продукту зберегти його погоджений набір клієнтів; зменшення потребує адресного рішення про зміну. Відсутній target/SDK не знімає вже прийняту вимогу.

Розрізняти три рівні результату: ескіз напряму; повна концепція для свідомого вибору; виконувана специфікація/виробнича передача. У концепції відомі всі потрібні системи, користувацькі шляхи, операційна модель, здійсненність і критичні невідомості; параметри можуть мати діапазон та due. У передачі розробник не вигадує предметні переходи, значення, формули, authorities, permissions або error behavior. Настроюваний параметр має baseline/range/owner/criterion, а не довільний TBD. Ранній bounded spike допускається до повної передачі, але не закриває її.

## Профіль, загальний метод і чинні рішення

Загальний метод вимагає повного застосовного наміру, причинних контрактів і належних доказів. Платформи, комерційна модель, участь власника, допустимі людські досліди, витрати й цілі продукту походять із конкретного profile/джерел. Налаштування сімейства показати як явні пропозиції; історія іншого продукту не встановлює policy. Нульова зовнішня витрата, заборона human experiments або щоденної ручної праці зберігаються там, де вони прийняті або діють як чинні консервативні runtime defaults; не створювати дозвіл їхнім мовчазним вилученням. Новий дозволений спосіб роботи має точний scope і джерело рішення.

Перед матеріальним scope застосувати [адаптивну роботу](adaptive-work.md); за потреби дослідження, системного синтезу або незалежної звірки — [спільні компетенції](research-and-synthesis.md). Це зареєстровані артефакти чинного ledger, без нового authority store. Показати користувачу достатність підходу й межі доказів; локальну визначену правку вести коротким impact-based шляхом.

## 2. Точний предметний контракт

Для кожної сутності визначити stable definition/instance ID, owner/tenant, типи полів, одиниці, допустимі діапазони, optional/null/absent, authority, чутливість, зміни/версії. Не переносити floating point у гроші без предметного правила. Для дат відділити UTC instant, локальну календарну дату, timezone, монотонний elapsed час і display format. Великі integer IDs перевірити round-trip між клієнтом, JSON, API й БД.

Для кожної команди: actor/authorization; input/schema; preconditions; момент фіксації значень; atomic consistency group; порядок перевірок/обчислень/округлення; transitions; response; visible feedback; durable acknowledgement; emitted events; idempotency; cancellation/expiry; timeout unknown outcome; компенсація. Event delivery/callback не визначає автоматично нову предметну дію. Вхідне повторне натискання, повторний webhook чи background replay повинні мати задану поведінку.

Таблиця переходів містить початковий стан, подію, guard, next state, зміни даних, forbidden transition, retry/reconcile і oracle. За одночасних подій назвати priority/tie-break/concurrency revision. Для probabilistic/AI output — джерело варіативності, модель/версія, supported parameters, допустимі результати, malformed/refusal/fallback і критерій якості; не обіцяти bitwise reproducibility opaque generator. Обчислення мають worked fixtures з проміжними значеннями, boundary cases та tolerances.

Ресурси/квоти/підписки/права описувати як причинні стани, а не розрізнені boolean. Термін дії на сервері, запізніла локальна подія й локальний кеш не отримують однакової authority. Той самий сценарій використовує однакові domain fixtures в усіх погоджених клієнтах; платформні адаптації мають explicit differences, а не сховану втрату core.

## 3. Збереження, синхронізація і відмова

Поле стану має scope, lifetime, authority, serialization, sensitivity, consistency group, commit trigger, recovery/migration/delete. Derived cache відділити від canonical record. Для local writes визначити atomicity/durability/ordering і previous-good; UI Saved не показувати після I/O failure. Process termination може статись без lifecycle callback. Local optimistic feedback і durable/remote confirmation — різні стани з правдивим UI.

Restore: bounded untrusted parse → integrity/owner/schema/content compatibility → збереження оригіналу → відома migration → semantic invariants → atomic logical apply → dependency-order recovery → reconciliation pending operations → UI з нейтральним input. Новіша невідома схема не перетворюється на silent reset. Backup/checksum/encryption не замінюють semantics або права доступу. Для SQLite snapshot використовувати сумісний actual backup route; звичайна копія активної WAL БД не є універсальним backup.

Sync є окремим adapter. За потреби визначити revision ancestry/conflict, queue, retry/backoff/cap, lease, account/session binding і delete tombstones. Універсальні max/sum/latest-time merge не підходять усім предметам. Подвійна offline витрата одного ресурсу не стає законною лише через event log. Старий callback після зміни акаунта не пише новому користувачу. Невідомий remote effect спочатку reconcile; дозволений локальний core продовжує працювати відповідно до задуму.

Перевірити disk full, truncated/corrupt/newer schema, kill до/після commit, out-of-order writes, offline divergence, auth expiry/switch, quota/timeout, delayed callback, duplicate grant/spend, restore після delete/revoke. Результат backup restore фіксувати за exact build/schema; старий binary не відкочує автоматично мігровані дані.

## 4. Перетворення і повний inventory

Створити inventory launch scope: features/rules/data, screens/states, assets, контент/локалі, API/native bridges, billing products, support articles, builds/configs/symbols, operational jobs. Для кожного потрібного output назвати recipient, recipe, input hashes, editable master/source, runtime derivative, validators, due proof. Каталог — стартова таксономія, не стеля й не наказ виробити все.

На кожному переході spec→design→source→export→import→client→release записати preserved invariants, intentional changes і losses. Типові межі: units/precision/rounding/currency; timezone/calendar/DST; enum/schema/null/ID; tokens/font metrics/density; color/alpha; frame/second/sample; accessibility semantics/focus; native callback/thread/account/session; locale grammar/length; content rights. Форматний PASS не доводить семантичної відповідності, вигляду, звучання або доступності.

Imagegen може створити concept raster; editable vector, layered source, UI tokens і доступні компоненти — окремі операції. Screenshot, clickable prototype, runtime screen і store screenshot мають окрему authority. Зберігати accepted original/hash; не перемальовувати прийняте при кожному repair. Музика/голос/animation лише за користю продукту, з rights, editable sources, runtime routing та listening/device proof; не нав’язувати їх таблиці чи утиліті.

## 5. Виробнича операція і реальний доказ

Для кожного класу роботи інстанціювати capability → recipe → semantic transformation → attempt → assembly. Capability називає операцію, host/toolchain/model, actual schema/catalog, supported/unsupported parameters, права/вартість/ліміти, потребу probe та freshness triggers. Опис plugin, наявність binary і actual operation test — різні факти. Для material input установити `requirement → schema field → provider support → consumption check`.

Recipe містить accepted inputs/hash, output/interface/consumer, competence/owner/owned paths, ordered steps/DAG, actual bound argv/API або numbered GUI procedure, exact toolchain, validators/oracles/tolerances, budget/effects/repair/stop. Шаблон не є executed recipe. Перед costly/external action створити pending attempt зі stable effect identity; після виклику — реальні request/job IDs, append-only observations, outputs/hash, cost і receipt. Timeout unknown зберігається до reconciliation. Відсутній job не заповнюється вигаданим.

Активувати компетенції за артефактами: product/domain research, requirements/math, UX/accessibility/content, client/native, API/data/security, commerce, QA/perf, release/ops. Лід виробляє й інтегрує результат; reviewer critical claim — інший actual actor. Один writer на спільний source/state/device/account, незалежно від worktree. Після двох однакових unsuccessful repairs змінити гіпотезу/метод. Cache key включає semantic input hashes, recipe/tool/model/export/import/platform/data scope. Новий importer інвалідує derivatives, а не accepted master.

## 6. Приймання інтегрованого застосунку

Перед масовим виробництвом прийняти representative assembly: exact source/build/config/component hashes, actors, initial data, account/network/device conditions, дії, expected/actual results, modalities і gaps. Наскрізний сценарій проходить useful action→domain state→persistence→presentation→restart/recovery, плюс conditional sync/payment/support. Кожний погоджений client core перевірити окремо, включно з Android/iOS/web за їхньої застосовності. Device/performance/native purchases вимагають належного actual target, а не desktop-only screenshot.

Тести поділити на structural, arithmetic/domain, integration, accessibility/perceptual, platform/device, security і observational business evidence. Один не підвищує інший. Meaningful negative має виявити конкретну помилку; складність тестування пропорційна наслідкам. Не вимагати programmatic test для простого оборотного текстового рішення. Концепція й spec можуть бути complete за своїм gate без готового binary, але не production-ready.

Змінений input/permission/toolchain/schema/target інвалідує транзитивно залежні claims. Cold receiver отримує точний index, sources/hashes, contracts, launch/return steps, oracles, blockers і наступну дію без історії чату. Чинний profile/state зберігає authority; linked model assets реєструються як artifacts із hashes, не стають паралельним mutable ledger. Реліз/спостереження/очікування нового запиту мають exact checkpoint; закрита сесія не виконує background monitoring.

## Первинні джерела й межі

Перевірено 2026-11-03. Це методичні опори; проєктні SDK/права/ліміти перевіряти знову на момент binding.
- Android offline-first architecture: https://developer.android.com/topic/architecture/data-layer/offline-first — локальна/мережева модель, writes/conflicts; не готовий sync для довільного домену.
- W3C WCAG2.2: https://www.w3.org/TR/WCAG22/ — перевірні web accessibility criteria; conformance scope/level вибирати й доводити, не переносити web automation PASS на всі native accessibility властивості.
- SQLite atomic commit/WAL: https://www.sqlite.org/atomiccommit.html та https://www.sqlite.org/wal.html — commit assumptions/recovery; конкретна durability залежить від режиму й платформи.
