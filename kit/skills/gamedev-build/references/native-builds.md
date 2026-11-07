# Нативні збірки й toolchain

## Перед кожним налаштуванням

Створити build profile з engine version/hash, renderer, dependency lock, toolchain versions, target/min OS, architecture, build type, bundle/package ID, version/build number, signing reference, export recipe та expected output. Поточні вимоги store перевіряти офіційно на дату build/release; tutorial рушія може відставати від store policy.

Офіційні джерела (перевірені 2026-11-01; повторити при виконанні):
- [Godot Android export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html).
- [Godot iOS export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html).
- [Google Play target API](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en).
- [Android App Bundle](https://developer.android.com/guide/app-bundle).
- [Android 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes).
- [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/).
- [Apple account capabilities](https://developer.apple.com/help/account/basics/about-your-developer-account).

Не фіксувати назавжди конкретний SDK як «найновіший». У receipt вказати фактичний policy snapshot/date і виконану compatibility перевірку. Для сторонніх native libs перевірити ABI/page-size compatibility, а не лише client manifest.

## Android

Потрібні відповідні engine export templates, JDK/Android SDK/NDK/build tools, ABI і signing setup. Debug keystore не є production upload/signing key. Secrets/keystores/паролі не комітити та не включати portable zip.

APK — install/test artifact. AAB — publish artifact; його не встановлюють на телефон як APK. Перевірити AAB derived APK splits через актуальний bundletool/Play internal track, потрібні languages/ABIs/assets і install/update path. APK smoke не доводить правильність AAB delivery.

Команди нижче — recipe template для вже перевіреного Godot export preset; фактичний preset name, output extension й engine version зафіксувати у repo. Перед виконанням звірити `godot --help`/документацію pinned version, не переносити flags на інший engine.

```bash
godot --headless --path /absolute/path/game --export-debug "Android" /absolute/path/build/game-debug.apk
godot --headless --path /absolute/path/game --export-release "Android" /absolute/path/build/game-release.aab
adb install -r /absolute/path/build/game-debug.apk
```

Preset має явно вибирати належний export format/build mode/architectures. Build output створити поза immutable input. Після build перевірити package ID, version, min/target SDK, native ABIs, permissions, debuggable/signing, asset delivery та binary hash інструментами SDK. У receipts зберегти sanitized metadata, повний build log та test device/install result. Не вважати команду з exit 0 підтвердженим встановленням.

## iOS

Фактичний iOS export/build потребує Mac, supported Xcode/SDK і відповідного signing/export flow. Linux може виконувати shared code tests, але не підтверджує реальну iOS native build. Personal Team, paid Developer Program, registered devices та TestFlight мають різні права/терміни; перевірити їх актуально до обіцянки способу тесту. Не просити користувача надсилати private signing key у чат.

| Артефакт | Що означає | Чого не доводить |
|---|---|---|
| Source/Xcode project | Проєкт можна відкрити/зібрати за наявності toolchain | Успішний build або встановлення |
| Simulator `.app` | Збірка під Simulator architecture/runtime | Запуск на фізичному iPhone; production renderer/performance |
| `.xcarchive` | Xcode archive з metadata/products; status верифікувати | Exported signed IPA/доступність всіх distribution methods |
| Signed `.ipa` | Exported device package за конкретним profile/method | Встановлення на довільний iPhone; Store approval |
| TestFlight build | Uploaded/processed beta за Apple flow | Public store release або real-device QA кожного tier |

Engine iOS export спочатку перевірити за pinned documentation, зберегти project/export log. Після export використовувати фактичні project/workspace й scheme; discover через `xcodebuild -list`, а не вигадувати scheme. Recipe template:

```bash
xcodebuild -project /absolute/path/Game.xcodeproj -scheme Game -destination 'generic/platform=iOS' -archivePath /absolute/path/build/Game.xcarchive archive
xcodebuild -exportArchive -archivePath /absolute/path/build/Game.xcarchive -exportOptionsPlist /absolute/path/ExportOptions.plist -exportPath /absolute/path/build/export
```

Конкретні signing settings, export method і destinations залежать від account/engine/Xcode; їх заповнює перевірений adapter. Не package private credentials. Перевірити bundle ID/version, architectures, entitlements, privacy manifests, required reason APIs/SDKs, assets та actual export/install result. Simulator compatibility може залежати від renderer; не перемикати final renderer тихо заради build.

## CI та повторюваність

CI job має clean checkout, exact dependencies/cache key, secrets references, export templates, reproducible versioning і artifact retention. Відтворити clean build хоча б одного release candidate, зафіксувати logs/tool versions. Byte-identical signed binaries не завжди досяжні; порівнювати recipe/source inputs та пояснювати timestamps/signature differences. Remote build/CI minutes і Apple account fee не входять автоматично у підписку Codex.

## Release adapter та artifact conformance

На потрібних SDK операціях перевірити debug і signed release callbacks/threading/cancel/account/lifecycle/minification/ABI; cloud/IAP/haptic pluginname не доводить підтримкукожного API. Зберегти exact versions/config/artifacthash/log/symbol identity й актуальні official platformconstraints.

Після export виконати required install/run/sandbox/device evidence на actual bytes. Cache keys pin source/assets/config/toolchain/importers; provenance не сертифікує behavior або quality. Unknownremote build/uploadoutcome reconcile перед новою спробою; iOShostbridge має exact input/return manifest.
