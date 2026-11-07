# Production: від вимоги до фактичного результату

Версія контракту 4.0.0. Зміст: 1—межі й запуск; 2—записи; 3—admission; 4—рецепти; 5—перетворення; 6—repair/cache; 7—докази; 8—передачі; 9—джерела. Завантажувати для feasibility, виготовлення/імпорту ресурсів, коду, builds, QA, release, liveops і зміни агента. Каталог класів: `assets/v4-production/operation-catalog.json`; шаблони п’яти записів та дев’ять family recipes у тому ж каталозі. Ці матеріали — інструкції, не звіти про наявні SDK/отримані assets.

## 1. Замкнути обсяг, не встановлювати весь каталог

Одиниця вибору — операція з відомим виходом і отримувачем. Для agreed scope перелічити всі потрібні artifact/action/state/variant/locale/platform класи; приписати `requirement_id → obligation_id → recipe_id → output_id → consumer`. Для кожного невикористаного класу записати `absent_by_design` із причиною; відсутній tool/host — blocked, не N/A. Початкові O01–O45 — стартова таксономія; додати специфічні операції, якщо гра вимагає інших.

На C0 дати ризик і досяжний маршрут ключової відмінності. Для кожної завершеної C1 дати повний класовий inventory і production profile, усі неочевидні переходи й due probes. На T встановити executable recipes, exact data/config/source formats, витрати, contact/event/clock contracts, validators та адреси тестових fixtures для всього launch scope. Повні сімейства/правила варіацій у C1 не підміняти 2–3 прикладами. T не вимагає вже виготовити всю гру: строк фактичного output/proof задає obligation. Ризиковий bounded spike дозволений до повного T. Перед масовим тиражуванням прийняти representative native assembly із реальним керуванням/камерою, розвитком/нагородою, звуком і performance evidence належного виду.

Must-фільтри tool selection: потрібні inputs/outputs/редагованість; платформа/версія; права/дані; доступ; бюджет; реальний метод перевірки. Потім порівняти контроль, час, якість, maintenance. Жодний weighted score не компенсує відсутність required rig/source/native callback. Зберігати прийнятий рушій. Для нового scope Godot + typed GDScript — відкритий кандидат; C#/C++/інший engine — за конкретною потребою та probe. Backend, PostgreSQL, middleware, cloud/ads/social — умовні. Мова backend залежить від продукту, а не механічно від Go/PHP досвіду власника.

## 2. П’ять записів у тій самій Game Model

Зберігати `production.operations.{capabilities,recipes,transformations,attempts,assemblies,obligations}` в канонічній моделі або linked project artifacts із stable IDs. Не вести другу authority задуму. При посиланні на зовнішній JSON перевірити його digest і включити його в dependency graph. `scripts/production_contract.py FILE` перевіряє форму/refs/DAG/declared proof boundaries; він не запускає інструмент, не підтверджує якість/правдивість receipt і не замінює domain review.

| Record | Обов’язок і конкретні поля |
|---|---|
| ToolCapabilityRecord | operation ID; provider/tool/host/target/toolchain; actual schema/catalog refs; підтримані outputs; unsupported features; input-field/parameter consumption; formats/limits; access/rights/data/cost; proof level; probe/witness; subject digest/freshness triggers; fallback |
| ProductionRecipe | requirement refs; accepted inputs+hashes; owner/competence; consumer; ordered step DAG; точний bound argv/API або numbered GUI actions; outputs+editable masters; transformations; semantic/technical/perceptual validators; budget/allowed effects; repair/stop |
| SemanticTransformation | source/target artifact refs; units/axes/scale/timebase/color/audio/ID conventions; preserved invariants; intentional changes; known losses/uncertainty; actual mapping; independent validator+oracle/tolerance |
| ProductionAttempt | stable attempt/effect identity до side effect; recipe/input/toolchain digests; parameters/seed state; job/request/run refs; append-only observations; actual costs/output hashes/receipts; retry/reconciliation; achieved proof |
| AssemblyEvidence | exact scene/build/config hashes; component hashes+runtime bindings; виконаний scenario; expected/observed invariants; author/reviewer IDs; modality/device/human evidence та gaps |

Не приховувати `unknown`, `not_exposed`, `not_tested`. Seed пишеться лише за фактичної підтримки. Accepted AI original, editable source master і runtime derivative — різні entities з immutable hashes/revisions. Відкрита ліцензія інструмента не означає ліцензію кожного font/sample/mesh. Rights ledger прив’язати до parents, terms/date, commercial/edit/distribute/source-transfer permissions, credits та receipts.

Рівні capability: candidate → descriptor_discovered/schema_discovered → catalog_verified → configured → operation_tested → integrated → native_verified. Descriptor і schema — різні факти, не універсальна лінійна шкала; вищі claims потребують відповідних окремих witnesses. `native_verified` завжди називає operation/platform/build/device; не переносити його на весь бренд. PATH discovery не доводить semantic operation. Catalog entry не доводить якість результату.

## 3. Admission і команда

До виконання кожного node перевірити: current accepted input hashes; доступний capability; матеріальні arguments справді приймає схема/модель і є спосіб перевірити споживання; права/чинний effect scope; cost/time cap; output/consumer interface; вільний ресурс; owner. Визначити owned paths, account/device/GPU/export slot; один writer для source/scene. Ізольовані каталоги не ізолюють спільний SDK/device/provider job. Lease timeout без reconciliation не дає права захопити remote job повторно.

Компетенції активувати за результатом: systems/math; world/AI/lore; UX/touch/accessibility; illustration/technical art/rig/animation; composition/audio/haptics; runtime/native/data; QA/performance; release/operations. Це не 20 постійних агентів. Прочитати фактичну skill перед делегуванням; переконатися у входах/виходах, не вибирати за ключовим словом. Actual agent ID і outputs записувати після роботи. Для material decision/critical acceptance author і незалежний reviewer — різні actors; self-check лишається self-check.

Recipe template має `status=template` і не виконується. Інстанціювати з project IDs, actual pinned toolchain і exact steps. `command` — argv array без shell interpolation; `api` — актуальні tool/model IDs та bound fields; `procedure` — конкретні numbered GUI actions із preset paths й expected observations. Невідомий critical binding блокує відповідний node; інша незалежна робота триває.

Descriptor/schema/catalog/arguments перевірити окремо. Якщо generic description називає model, якого немає в каталозі, не вигадувати alias. Public HTTPS model URL у rig API не створює дозволу публікувати приватний source. Prompt field, який модель ігнорує, не закриває вимогу. Для кожного material parameter записати `requirement → schema field → provider capability → consumption check`; необов’язковий cosmetic параметр можна зняти лише явним рішенням, must — ні.

## 4. Дев’ять family recipes

Файли `recipe-*.json` задають конкретні алгоритми; числові caps/tolerances прив’язати до гри до виконання. Family template не є завершеним project recipe. Кожний отримувач має вміти відкрити source, повторити export, імпортувати та перевірити очікувану поведінку без історії чату.

| Recipe | Source → editing/transform → output → acceptance |
|---|---|
| R01 2D states | Accepted image+style/camera/action inventory → construction layers+route frame/cutout/3D-render → frames/atlas/clip metadata → identity/pivot/alpha/contact/cancel/actual scene |
| R02 3D rig/clips | Approved dimensions/views → mesh inspect/retopo/UV/bake → editable rig/weights/actions → GLB+markers+import config → stress poses/sockets/root/contact/gear swaps/native profile |
| R03 VFX/UI | Exact hazard shape/time and UI states/strings → vector/engine source+timeline → VFX/themes/fonts/bindings → collision overlay, crowded/narrow/mute/reduced effects, device budget |
| R04 Adaptive music | Sonic brief/motifs/state graph → composition/session/aligned stems → loop/transition table → every transition/pause/cold decode/voice budget/listening |
| R05 Material contact audio | Semantic contact/material/outcome → lawful raw/transient/body/tail families → export+bounded curves/dedup → scrape start/update/stop, resting jitter, crowded mix |
| R06 Attack SFX/haptics | Windup/swing/block/hit/miss semantics → source variants/patterns → event routing/priority/cancel → actual muted/mono/no-haptic parity and physical tactile test |
| R07 Mechanic/runtime | Exact rules/data/states/oracle → typed modules+engine/native adapters → real scene/binary → boundary/property/differential/scene/native/human scope |
| R08 Progress spend/save | State catalogue/consistency group → versioned local transaction+optional cloud → commit/migrate/recovery adapter → duplicate/kill/disk-full/old-save/restore corpus |
| R09 Conditional commerce/RC | Offer/SKU/state/authority → native conformance+sandbox → exact signed RC+symbols → grant-once/pending/refund/update/store-channel/native receipt |

2D: missing back/overlap becomes authored task, не автоматично відновлене знання. Frame generation/video не є consistent animation; після key/contact sample приймати identity до in-betweens. Clip frame numbers переводити в seconds за explicit fps. Trimming має зберегти pivot/offset, padding/extrusion проти bleed. Hit/hurt geometry має own authority.

3D: image-to-mesh лише input candidate. Перевіряти hidden surfaces, manifold за потреби, deformation topology, UV/texel/padding, normal/ORM/color conventions. Auto-remesh не доводить retopology. Control rig не дорівнює exported deform skeleton. Rest/bind/weights/sockets, extreme poses, root-motion vs controller ownership, constraints bake, clip export inclusion і marker sidecar — explicit. Валідний GLB не доводить silhouette/contact/performance. Прямий .blend import потребує Blender на import host.

Аудіо: full stereo track не доводить stems/MIDI/loop; окремі extraction/export операції можливі, але перевірити plan/schema/rights/bleed/phase. Зберігати session/dependencies/raw takes. Tempo/meter/bar/sample alignment фіксувати: при 96 BPM, 4/4, 48 kHz beat=30000 samples, 8bars=960000 samples без tails. Це fixture, не універсальний темп. Немає універсального game LUFS. Числовий аналіз не замінює listening. Імпортер normalize/compress/loop flags фіксувати; mix buses/ducking/voice limits/steal/drop/no-repeat/cold-first-use мають конкретні правила.

Контактні cues споживають simulation commit негайно; не чекати disk/cloud. Durable grant/confirmation має окрему D1 межу. Whoosh можна прив’язати до animation marker; accepted hit/block/break — лише до authoritative outcome. Cosmetic RNG ізолювати від combat. Paused/cancelled/despawned emitter закриває continuous sound/haptic. Capability залежить від hardware; не вимагати amplitude/primitives від усіх телефонів. Без actual playback/device evidence listening/tactile лишається unperformed.

Код: виділити rules/immutable definitions/session state/engine adapter/presentation за причиною зміни. FSM/components/commands/events/data-oriented route брати за задачею; не додавати ECS/DI/CQRS/microservices разом заради назв. Precision/rounding/time/capture/tie-break перевіряти спільними fixtures reference→runtime. GUT або GdUnit4 обрати за pinned compatibility; pytest/Hypothesis — Python tooling, не автоматичний GDScript test. Meaningful negative має падати при навмисному дефекті; parser pass ≠ integration.

Дані/native: точні IDs/RNG/counters не втрачати при JSON conversion; untrusted deserialize не створює objects. SQLite/JSON route обрати за обсягом і перевірити actual bridge. Native callbacks/thread/account/lifecycle/cancel/release stripping/signing — conformance scene. Невідомий transaction/job state спочатку reconcile. Android AAB не встановлювати як APK; device splits і signing scope перевірити. Apple archive/export/install різні операції й потребують реального Mac/Xcode route. Secret references передати через host facility, не включати values у package.

## 5. Семантичні ребра й складання

На spec→source→export→import→runtime назвати preserved invariants, intentional changes і uncertainty. Типові межі: pixels↔metres; degrees↔radians; Y-up/Z-up; linear/sRGB; straight/premultiplied alpha; normal/ORM channel; seconds/frame/sample; marker IDs/root policy; collision geometry↔rendered cue; mono/stereo/spatial/music time; definition/instance/generation IDs. Не додавати несумірні величини. Форматний validator ловить структуру, окремий oracle — зміст.

Assembly зафіксувати до тесту: scene/build/config/component hashes, consumer bindings, scenario/actions/initial state/RNG/time, expected outcomes/tolerances, platform/device/quality, modality. Відтворити input→camera→action→contact→resources→AI/world→presentation→save/reward→resume. Перевірити одночасні cancel/lethal/phase/interrupt, reduced effects, cold first use й peak overlap. Окремо прийняті animation/audio/UI не доводять assembly. Немає byte-identical GPU frame обіцянки; semantic/perceptual parity має предметні допуски.

Машинна coverage map знаходить outputs без recipe, dangling refs, цикли planned execution DAG, missing due proof та unresolved external attempt. Gameplay feedback cycles дозволені; production pass має DAG. Repair створює нову revision/attempt, а не прихований нескінченний workflow cycle. Closure охоплює death/cancel/recovery/locale/gear variants, не тільки idle/run sample.

## 6. Attempt, repair і cache

Перед costly/external side effect append pending attempt зі stable effect key і current hashes. Після submission зберегти actual provider request/job ID; observations append-only. Timeout = unknown, не failed. Спочатку status/output/cost reconciliation, потім отримання наявних bytes або доказ effect_absent. Cancel requested не дорівнює cancelled. Idempotency існує лише коли provider її підтримує. Не повторювати operation із тим самим unresolved effect key; reserve unknown cost до з’ясування. Append final receipt і immutable accepted output hash; запланований fake job не записувати як actual.

Failure class: input_contract / unsupported_operation / craft_generation / format_import / integration / environment_access / transient_provider / acceptance_defect. Задати changed variable, expected correction, next validator, time/spend cap. Після двох невдалих однакових гіпотез змінити діагноз/метод або точний blocker. Відсутній rig capability не ремонтується п’ятьма prompts. Поріг не скасовує must і не авторизує нові витрати.

Cache key = recipe revision + operation + input digests + relevant model/toolchain/exporter/importer revisions + platform/profile + parameters + data scope. Accepted original лишається за hash; зміна importer скидає derivative/proof, не переписує master. Поточні terms/access/schema/provider revision — freshness triggers. Bitwise regeneration opaque AI не гарантується. Cache reuse не створює native/human proof. Невиконаний review або нечинний proof не стає поточним доказом через копіювання файла.

## 7. Виміряти належне твердження

Окремі verdicts: structural, semantic, craft/perceptual, integration, native/device, human, revenue. None implies the others. QA — інший actual actor для незалежного verdict. Logs/format pass/hash/provenance не доводять fun, licensed input, comfort або відсутність vulnerabilities. Gate непідтвердженого обов’язкового твердження — pending/blocked із owner/наступною дією, не зелене число coverage.

60FPS означає приблизно16.67ms/frame target, не автоматичний pass за average. До виміру задати сцени/тривалість/percentiles/cold/peak/thermal/memory/input/IO budgets. Фізичні devices потрібні для touch/audio/haptics/thermal claims; editor/headless/simulator мають власний scope. Непідтриманий hardware fallback зберігає gameplay-critical cues, не стирає їх. Support envelope не звужувати мовчки.

Рекомендований bounded CI DAG: data/IDs → format/types/parser → unit/property/state → importer/scene/adapter → platform build → artifact inspection → due device/sandbox/human → release preparation. Untrusted code не отримує signing/store secrets. Dependency cache відділити від immutable output. Exact build ID зв’язує source/model/data/catalog/config/save schema/toolchain/symbols/logs/QA. Test мутацією підтверджує, що check знаходить його заявлений дефект.

## 8. Передати й завершити фактично

Host bridge створювати тільки за реальною межею: producer/target host, preflight, cwd, input hashes, exact tool/argv/API або numbered actions, allowed outputs, secret refs, expected receipt, return digest/semantic validation, next action. Старий Android receipt не доводить новий iOS build. Доступну тут дозволену роботу завершити до ручної передачі. Повернення перевірити до зміни ready.

Release scope має actual channel/status: prepared/uploaded/processing/testers_available/approved/live. Halt не відкочує встановлену binary; config rollback має compatibility, інакше forward fix. Store requirements/SDK/licensing перевірити за поточною версією перед RC. Provenance (SLSA/PROV) допомагає exact inputs→activity→outputs, не сертифікує quality.

Після дозволеного запуску записати released build/config/save contract, actual monitoring setup/observation, open incidents/cost/rights/service-loss bounds. Новий запит: actual state→impact→bounded design/build/QA/release. Не заявляти фоновий моніторинг без фактичного сервісу/scheduler й чинного доручення. Очікування нової вказівки зберігає checkpoint, не потребує удаваної active команди.

## 9. Первинні джерела й актуальність

Нижче технічна основа, перевірена під час D2 02.11.2026; поточні `stable/latest`, provider plans/API та store правила перевіряти на pinned toolchain перед виконанням. Наші record schema, gates і рецепти — адаптація, не універсальний GDD-стандарт.

- glTF2: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html — interchange scope, skin/material/animation conventions; не craft guarantee.
- Blender glTF: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html — підтримані exports; retopology: https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html .
- Krita animation export: https://docs.krita.org/en/reference_manual/render_animation.html ; Inkscape CLI: https://inkscape.org/doc/inkscape-man.html .
- Godot animation/retarget: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html ; root: https://docs.godotengine.org/en/stable/classes/class_animationtree.html .
- Godot interactive/synchronized music: https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html ; https://docs.godotengine.org/en/stable/classes/class_audiostreamsynchronized.html ; audio import: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html . Stable prose/API BPM discrepancy потребує pinned probe.
- Ardour stems: https://manual.ardour.org/working-with-sessions/interchange-with-other-daws/stem-exports/ ; FFmpeg filters: https://ffmpeg.org/ffmpeg-filters.html ; Audacity normalize: https://manual.audacityteam.org/man/normalize.html .
- Apple haptics: https://developer.apple.com/documentation/corehaptics ; Android: https://developer.android.com/develop/ui/views/haptics/haptics-apis .
- GUT: https://gut.readthedocs.io/ ; GdUnit4: https://mikeschulze.github.io/gdUnit4/ ; Hypothesis: https://hypothesis.readthedocs.io/ . Перевірити compatibility, не припускати latest.
- Godot Android/iOS export: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html ; https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html .
- SLSA provenance: https://slsa.dev/spec/v1.2/provenance ; W3C PROV: https://www.w3.org/TR/prov-dm/ ; NIST SSDF1.1 final: https://csrc.nist.gov/pubs/sp/800/218/final ; Bazel cache concept: https://bazel.build/remote/caching . Не вимагають змінити engine/build system.
