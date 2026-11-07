# Повнота стану, save, продовження й cloud 4.0

## Навігація

1. Реєстр стану
2. Simulation та durable commit
3. Restore і міграції
4. Cloud/identity/conflicts
5. Час, RNG, покупки й видалення
6. Failure suite і джерела

Завантажити для кожної гри й будь-якої зміни стану. Зберігати або коректно відтворювати весь значущий для гравця стан. Це не вимога серіалізувати кожну частинку, pointer чи фізичний кадр; тимчасове отримує явне reset/rebuild правило. Пропущене поле є прогалиною.

## 1. Побудувати State Catalogue

Вивести mutable fields із усіх активних систем, досяжних переходів і adapters. Для кожного записати ID/system/owner, тип/units/precision/bounds, initial state, meaning, lifetime, scope profile/device/run/account, authority, mutation sources, persistence class, commit trigger, consistency group, restore order, reconstruction, schema/content version, merge, migration, deletion/retention/privacy й fixtures.

| Клас | Політика | Приклад |
|---|---|---|
| Durable | Надійно зберегти за визначеною межею | Unlock, inventory instance, spent resource, granted reward |
| Reconstructible | Зберегти canonical inputs, відновити за версією | Derived stats, path/plan, UI projection |
| Ephemeral | Безпечний reset/transition | Finger contact, held gas, particles |
| Cache | Можна видалити й отримати/побудувати знову | Downloaded derivative, thumbnails |
| Secret | Окреме належне сховище; не переносимий gameplay save | Credential/token/key |

Перевірити профіль/майстерність/колекції; inventory/loadout/durability/craft; currency/grants/pity/limits; world/quest/NPC/door/destruction; run/position/objective/resources/effects; AI/boss/encounter; generation/accepted results; metagame clocks; purchase projections; tutorial/objective/context; settings/layout/accessibility; UGC/replays за наявності; похідне й тимчасове.

Задати гарантію продовження: exact logical snapshot або погоджений checkpoint із bounded loss window. Не вводити мовчазний rollback meaningful progress. Pause/system interruption не прирівнювати до abandon без продуктового правила. Контекст повернення людини (мета/комплект/зміни) є окремим UX контрактом від bytes restore.

## 2. Розвести дві межі commit

**Simulation commit** атомарно застосовує outcome в authoritative gameplay model; hit/UI/VFX/SFX/haptic feedback негайний. Він не чекає disk flush або cloud acknowledgement. **Durable commit** фіксує значущі причинні зміни за гарантією конкретного adapter. Critical reward/spend/victory success не підтверджувати раніше належної durable межі. Cloud acknowledgement є третім окремим станом.

Записати command/operation ID→validated outcome→consistency group→snapshot/event transaction→new generation→write/check→durable adapter acknowledgement→confirmed revision→cloud queue. Для frequent noncritical state задати bounded dirty/checkpoint window й budget; не писати диск кожного кадру.

Одна logical writer queue має sequence/revision, backpressure/coalescing й захист від старого async save поверх нового. Spend+created item+claim flag не розносити по некеровано незалежних commits. Crash у будь-якій межі повинен відновити один допустимий причинний підсумок.

Обрати дві generations/previous-good snapshot або transactional DB за складністю. `tmp+rename` не доводить універсальну power-loss durability; перевірити actual OS/filesystem/API. Для SQLite зафіксувати journal/synchronous assumptions й supported snapshot export. Копіювання тільки main файлу активної WAL DB може втратити актуальний стан.

Disk full/serialize/I/O/permission failure не показує Saved і не знищує previous-good. Lifecycle callbacks дають додаткову можливість flush; process termination не гарантує callback виходу. Cache/tmp не є єдиним сховищем прогресу.

Consistency group містить causal command IDs, полів-учасників, допустимі commits, rollback/retry і reconciliation. Наприклад, отримані6parts→спожито6→створеноkit→claimed не можна merge як kit плюс старі6parts.

## 3. Задати envelope та restore

Envelope: save/profile ID, schema/build compatibility, content/catalog/economy/generator versions, revision/generation/parent ancestry за потребою, committed marker, logical position, RNG contracts, payload length/checksum, referenced modules. Timestamp придатний для пояснення, але не універсальна authority старшинства гілки.

Restore pipeline:

1. Обмежити size/depth/types, parse без виконання objects/code/arbitrary resources.
2. Перевірити envelope/integrity, owner/profile scope, supported schema/content/build.
3. Зберегти оригінал, виконати відомий migration path; невідома newer schema — зрозуміла помилка, не reset.
4. Перевірити semantic invariants: unique instance IDs, balances, prerequisites, causal grants/quests, valid references.
5. Атомарно застосувати consistent logical state.
6. Відновити world/topology/entities/resources/AI у dependency order; derived caches перерахувати.
7. Reconcile entitlements/pending operations належною authority; не reroll accepted outcomes.
8. Повернути camera/presentation/goal context із neutral input; лише потім увімкнути дії.

Checksum не доводить authenticity, encryption не замінює atomicity, signed payload не доводить semantic validity. Не завантажувати довільні serialized objects із cloud/imported save. Credentials не включати в repro/export.

Міграція охоплює schema, content IDs, catalogs/economy, generators, removed DLC/module і stable identity. Для deletion/remap задати compensation/retention за задумом. Golden saves усіх підтриманих переходів повинні відкритися з очікуваним outcome. Rollback binary не є rollback уже мігрованого save; downversion compatibility визначити явно.

## 4. Спроєктувати cloud як окремий adapter

Offline core працює локально. Пропонувати захист/перенесення прогресу контекстно й у settings. Відділяти cloud opt-in/management від автоматичної platform authentication; SDK може керувати власним системним UX. Не вигадувати кнопку/можливість без actual API.

Розрізняти game profile/guest, platform player, in-game account, cloud owner, store account і device scope. Account switch не дозволяє завантажити старі чужі дані новому owner. Callback перевіряє operation/profile/session/revision binding; old callback не застосовується до нового профілю.

Показувати фактичні стани: local saved, pending/offline, syncing, cloud confirmed revision, conflict, quota/auth/error. Зелене synced не показувати до remote acknowledgement. Timeout має unknown outcome й bounded reconciliation/retry; не множити uploads/grants без потреби.

### Вибрати platform route за підтриманими ОС

Google PGS Saved Games/Snapshots потребує integration/console enablement, власної схеми, identity/conflict/quota. Google PGS v2 platform ID відділений від game account. Android Auto Backup — окреме OS backup, не gameplay cloud sync. На дату дослідження2026-11-02 official Saved Games limits3MB blob/800KBcover і Auto Backup25MB; перед проєктним binding перевірити актуальні межі.

Apple GameSave на дату дослідження доступний з iOS/iPadOS26; не підвищувати автоматично мінімум ОС гри заради цього route. Для старіших підтриманих ОС перевірити GameKit/GKSavedGame або інший сумісний adapter. GameCenter account не тотожний iCloud owner. Native plugin з назвою GameCenter не доводить save API coverage.

Actual adapter evidence має pinned SDK/plugin/OS/export versions, entitlement/capability/signing setup, callbacks/threading/lifecycle, local/offline/online/conflict/account-switch/cold-restore traces. Сам факт публікації в AppStore/Play не створює cloud save. Android↔iOS profile потребує окремих identity/storage/authority рішень, scope й cost; не є default backend.

### Узгоджувати причинні гілки

Виявляти divergence за revision ancestry/platform conflict API. Не застосовувати універсально latest timestamp, max currencies, sum balance або union inventory. Вибір whole consistent branch або спеціальний merge мають предметний контракт.

Безпечні незалежні monotonic unlocks іноді можна union. Витрати/crafting/purchase grants/mutually exclusive quests/active boss state — лише з причинною consistency policy. Event log сам не робить дві offline витрати одного ресурсу обидві законними. Для складного offline economy потрібна authority/reservations/limited scope або вибір гілки.

До вирішення конфлікту зберегти обидві оригінальні версії. UI показує зміст/прогрес/наслідки обох, а не JSON. Device thumb zones адаптувати до нового екрана; не переносити aspect-specific layout як account invariant.

## 5. Час, RNG, покупки й видалення

Відділити simulation time, active time, elapsed real time і calendar UTC. Монотонний clock сесії не є вічним timestamp через reboot. Offline production/rewards мають anchor, cap, accepted claim IDs, timezone/jump/backward rules. Без незалежної authority не обіцяти доказ правильної дати після довільної зміни локального clock.

RNG зберігає stream/algorithm/version/state або counter key і accepted choices/pity. Великі64bit seeds/IDs/counters мають точне кодування й round-trip fixture; Godot JSON numeric float conversion не гарантує integer precision. Seed без version не гарантує той самий світ після update.

Cloud progress, OS backup, transfer і purchase restore різні. Entitlement локально є проєкцією store/server authority. Старий backup не відновлює refunded право й не видає consumable вдруге. Reconcile після пропущеного callback, offline і іншого device; забезпечити idempotent grant/consume record.

Reset run, clear local copy, disable sync, unlink й delete profile — окремі дії. Delete/tombstone retention і старий offline client не дозволяють непомітне resurrection. При service loss/offboarding, якщо релевантно, визначити долю access/progress/purchases/export/support; не обіцяти довічну online можливість без фактичного зобов’язання.

Без cloud/backup не обіцяти відновлення після uninstall/device loss. За включеного cloud провести actual cold restore на іншому device. Секрети й увесь private save не потрапляють у public support capsule. Data egress вимірювати за consent/offline/cloud states, а не лише декларувати.

## 6. Обов’язковий failure suite

- Kill до/після critical command, serialize, write, durable acknowledgement і UI confirmation.
- Boss death+reward+quest flag+pause: один причинний restore outcome.
- Disk full/truncated/corrupted/newer save: previous-good не затерто порожнім.
- Async write ревізіїN завершився післяN+1: старий не замінює новий.
- Дві offline гілки витратили ті самі parts: немає kit+returned materials.
- Account switch/guest-existing-cloud/late callback: немає cross-profile overwrite.
- Quota/no network/unknown upload: local core працює, bounded reconciliation.
- Round-trip maximum IDs/seeds; stream state відновив next sample, не reroll grant.
- Current boss/DoT/checkpoint restore: немає повторного tick/reward/attack без cue.
- Purchase refund/consumed item/restore: rights reconciliation не довіряє old JSON.
- Delete profile і старий offline device: немає silent resurrection.
- Cold reinstall restore з actual platform adapter і підтриманою старою версією.

Зберегти failure injection logs/fixtures/expected outcomes, exact adapter/build/profile binding і limits. Structural registry pass не доводить durability, cloud або device integration.

## Первинні джерела

Досліджено2026-11-02; при виборі SDK/OS перевіряти актуальну документацію й фактичний export.

- SQLite atomic commit: https://www.sqlite.org/atomiccommit.html
- SQLite WAL: https://www.sqlite.org/wal.html
- SQLite online backup: https://www.sqlite.org/backup.html
- Android process lifecycle: https://developer.android.com/guide/components/activities/process-lifecycle
- PGS Saved Games: https://developers.google.com/games/services/common/concepts/savedgames
- PGS v2 identity: https://developer.android.com/games/pgs/android/android-signin
- Android Auto Backup: https://developer.android.com/identity/data/autobackup
- Apple GameSave: https://developer.apple.com/documentation/gamesave
- Apple GKSavedGame: https://developer.apple.com/documentation/gamekit/gksavedgame
- Godot JSON: https://docs.godotengine.org/en/stable/classes/class_json.html
- Godot Variant deserialization warnings: https://docs.godotengine.org/en/stable/classes/class_%40globalscope.html
- Play Billing lifecycle: https://developer.android.com/google/play/billing/lifecycle
