# Передача реалізації до QA

## Self-contained package

- Manifest із game/studio IDs, schema/revision, source commit, exact upstream package refs/hashes, chosen platforms та станом кожної.
- Canonical source, engine project, imported assets/config, content/economy/settings data, dependency locks і build adapters. Exclude caches, secrets, unnecessary generated intermediates; include незамінні authoring sources та rights.
- Frozen GDD/TDD, decisions, requirement trace, style tokens, canonical images/motion/audio references, allowed deviations, studio logo/fonts/credits/contact identity.
- Реальні build artifacts і receipts; якщо немає platform artifact — exact blocker, не пустий placeholder із `.apk` у назві.
- Golden inputs/seeds/saves, migration fixtures, API/contracts/mock boundaries, test logs, runtime captures/profiles, known issues й independent-review status.
- Clean-restore instructions, toolchain/version inventory, local test instructions, signing references без private material, backend/environment config keys без values, deploy migrations/rollback boundaries.

Для другої платформи зберегти transferable source/data/craft; її статус не підвищувати лише від cross-platform engine. QA отримує actual per-platform results й remaining gaps.

## Модель і runtime consistency

Додати canonical game model exact bytes/hash, derived GDD/TDD/data versions, runtime adapter/import inventory, model→consumer bindings, dependency-impact report, design-derived scenario fixtures й actual observations. Включити camera/input/actor/equipment/world/progression/reward/learning/commerce/lifecycle coverage за застосовними features. Модель, sidecar/runtime state і handoff manifest мають окремі schema versions; не оголошувати їх усі «3.0» і не reset старі decisions/saves.

Source completeness, structural validity, independent semantic review, actual build/device proof і human experience acceptance мають окремі scope/status. Відомий змістовний gap не закривається hash pass. Unknown external transaction/deploy outcome передавати з actual request ID та reconciliation next action без сліпого повтору.

## Build receipt поля

Document має `kind="actual_build_receipts"` і непорожній `receipts` array. Кожен запис: `receipt_id`, `game_id`, `platform`, `artifact_type`, `artifact_path` (relative to package), `artifact_sha256`, `source_commit`, `baseline_sha256`, `toolchain`, `command`, `exit_code`, `log_path`, `signing_status`, `built_at`, `build_profile`, `limitations`. Для folder artifacts — deterministic inventory/hash policy. Build logs можуть містити secrets: redact values з явною позначкою redaction, зберігати діагностичний зміст.

`signing_status` — verified конкретним tool/result або `unsigned`/`not_checked`; не ставити `verified` за існування `.ipa`. Усі execution receipts мають походити з actual run. Шаблон чи dry-run лишається `example`/`planned` і не проходить actual evidence gate.

## Test receipt поля

Build hash; platform/device model/OS; case/scenario/seed/input; procedure; environment/network/consent/account type; start/duration; expected outcome із design ref; observed raw output/capture/profile; verdict; actor role й independence; limitations. Не записувати real credentials, PII або raw payment receipts у передаваний архів.

## Чотири різні твердження

1. Source/package complete у named scope.
2. Build виконано actual toolchain із artifact.
3. Artifact встановлено/запущено на named device/runtime.
4. Independent QA прийняв defined product criteria.

Ці твердження не замінюють одне одного. Store publish і measured market success — пізніші окремі claims. Структурний валідатор перевіряє completeness/bytes, не fun, visual identity, execution truth або реальних платників.

## Handoff запит

«Використай `$gamedev-qa`. Прийми пакет [path/ID], revision/hash [value], platforms [value]. Перевір scope [IDs], actual builds [receipt refs], unresolved gaps [IDs]. Не змінюй baseline; defects повертай із reproducible evidence до build/assets/design owner».

Для directory artifact digest — SHA256 UTF-8 JSON [[relative_posix_path,file_sha256],...] зі sorted paths, ensure_ascii=False та separators=(",",":"); symlinks не допускаються. Це byte inventory, не signature або execution attestation.

## Повна передача 4.0

Включити model maturity/current version,20 track applicability/coverage, T contracts/catalogue/grammar, State Catalogue/golden saves/migrations, exact damage/physics/lifecycle fixtures, input traces, capability/recipe/transformation/attempt refs і AssemblyEvidence. Передавати matching symbols, importer/toolchain locks, content epoch і patch base якщо обрані. Усі приклади/planned outputs відокремити від actual receipts.

Новий QA receiver без історії чату запускає named scenario й порівнює independent expected outcome; incomplete input/behavior повертає causal owner. Linux source не доводить signed iOS, старий build receipt не доводить current artifact, cached proof переноситься лише за unchanged semantic dependencies.
