# Native builds and toolchains

## Before configuring a build

Create a profile with engine version and hash, renderer, dependency lock, toolchain versions, target and minimum OS, architectures, build type, bundle or package ID, version and build number, signing reference, export procedure, and expected output. Verify current store rules at build and release. Engine instructions may lag store policy.

These official references were reviewed on 2026-11-01. Verify them again for the actual build.

- [Godot Android export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html).
- [Godot iOS export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html).
- [Google Play target API](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en).
- [Android App Bundle](https://developer.android.com/guide/app-bundle).
- [Android 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes).
- [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/).
- [Apple account capabilities](https://developer.apple.com/help/account/basics/about-your-developer-account).

Record the actual policy snapshot and date, chosen SDK, and observed compatibility. Inspect third-party native libraries for ABI and page-size compatibility.

## Android

Use compatible engine export templates, JDK, Android SDK and NDK, build tools, ABI selection, and signing. Keep debug and release key custody separate. Exclude secrets, keystores, and passwords from Git and packages.

Install and test APKs. Validate the release AAB through splits derived with the supported `bundletool` or the Play internal track. Check asset, language, and ABI delivery and install and update behavior on that route.

These template commands assume a verified Godot export preset. Pin the actual preset, output extension, and engine version in the repository. Check `godot --help` and pinned documentation before use.

```bash
godot --headless --path /absolute/path/game --export-debug "Android" /absolute/path/build/game-debug.apk
godot --headless --path /absolute/path/game --export-release "Android" /absolute/path/build/game-release.aab
adb install -r /absolute/path/build/game-debug.apk
```

The preset selects the actual format, build mode, and architectures. Write output outside immutable inputs. Inspect package ID, version, minimum and target SDK, native ABIs, permissions, debuggable flag, signing, asset delivery, and binary hash with SDK tools. Retain sanitized metadata, full diagnostic log, and actual device installation result in separate receipts.

## iOS

Build on a Mac with supported Xcode and SDK and the applicable signing and export flow. Track Linux shared-code tests separately. Verify current rights and durations for Personal Team, paid Developer Program, registered devices, and TestFlight before choosing a test route. Keep private signing keys out of chat.

| Artifact | Supported claim | Verify separately |
|---|---|---|
| Source or Xcode project | Project source for the required toolchain | Build and installation |
| Simulator `.app` | Output for a simulator architecture and runtime | Physical iPhone, production renderer, and its performance |
| `.xcarchive` | Xcode archive with metadata and products | Signed IPA export and allowed distribution methods |
| Signed `.ipa` | Device package for a specific profile and method | Supported device installation and App Store approval |
| TestFlight build | Uploaded and processed Apple beta | Public release and physical coverage of each target tier |

Check the engine export against pinned documentation. Retain its project and log. Resolve the actual project or workspace and scheme with `xcodebuild -list`. Adapt this template to the verified settings:

```bash
xcodebuild -project /absolute/path/Game.xcodeproj -scheme Game -destination 'generic/platform=iOS' -archivePath /absolute/path/build/Game.xcarchive archive
xcodebuild -exportArchive -archivePath /absolute/path/build/Game.xcarchive -exportOptionsPlist /absolute/path/ExportOptions.plist -exportPath /absolute/path/build/export
```

The verified adapter provides signing settings, export method, and destinations for the current account, engine and Xcode. Exclude credentials. Verify bundle ID, version, architectures, entitlements, privacy manifests, required-reason APIs and SDKs, assets, and actual export and installation. Keep the accepted renderer or record an explicit change when the simulator needs another renderer.

## CI and reproducibility

Use a clean checkout, exact dependencies and cache key, secret references, export templates, reproducible versioning, and artifact retention. Reproduce a clean build of an actual release candidate and retain logs and tool versions. Compare inputs and recipes and record differences from signing and timestamps. Verify remote build and CI capacity and Apple account costs separately from the Codex subscription.

## Release adapters and artifact conformance

For relevant SDK operations, exercise debug and signed release callbacks, threads, cancellation, accounts, lifecycle, minification, and ABI. Verify required operations from the actual cloud, IAP, and haptic plugins. Record versions, configuration, artifact hash, logs, symbols, and current official platform constraints.

After export, verify installation, run, sandbox, and device behavior with the exact output bytes. Cache keys pin source, assets, configuration, toolchain, and importers. Verify behavior and quality separately from provenance. Reconcile an unknown remote build or upload before retry. An iOS handoff needs exact input and return manifests.
