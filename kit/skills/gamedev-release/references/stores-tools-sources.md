# Store, mobile build, authoring, and audio source snapshot — checked 2026-11-01

This source snapshot supports release planning. Preserve dated platform findings separately from design recommendations. Recheck store requirements before release and record date, URL, SDK version and result in `compliance-snapshot.json`.

## 1. Artifacts for installation and distribution

| Target | Actual artifact | Prerequisites |
|---|---|---|
| Android local installation | Debug APK or signed release APK | `adb install -r` and compatible device. Verify release behavior in its own build. |
| Google Play | Signed Android App Bundle `.aab` | Upload key, Play App Signing, versionCode, listing, declarations and actual SDKs. |
| iOS Simulator | Simulator `.app` or Xcode project and simulator destination | macOS, Xcode and simulator SDK. A simulator `.app` cannot install on an iPhone. |
| Local iPhone | Device build signed through Xcode | Apple Account and Personal Team or paid team, provisioning, trust and Developer Mode where required. |
| iOS distribution | `.xcarchive`; `.ipa` after appropriate export and signing | Paid Apple Developer Program for App Store or TestFlight, provisioning and export path, upload and review. |
| External iOS beta | App Store Connect build in TestFlight | Beta metadata, review of first external build, testers install TestFlight. |

- AAB documentation, opened: https://developer.android.com/guide/app-bundle
- Godot iOS export, macOS and Xcode, and simulator renderer limitations, opened: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_ios.html. The stable documentation described Compatibility for Simulator. Measure physical iPhone behavior independently.
- TestFlight, opened: https://developer.apple.com/testflight/
- Apple Personal Team page, opened: https://developer.apple.com/help/account/basics/about-your-developer-account. The snapshot recorded up to 10 App IDs, 3 devices, 3 apps per device, and 7-day provisioning. Treat personal signing and distribution as separate routes.

## 2. Dated store gates

- The snapshot recorded Android 16 / API 36+ targeting for new and updated standard mobile games from 31.08.2026. Target and minimum SDK differ. Source opened: https://support.google.com/googleplay/android-developer/answer/11926878?hl=en
- Verify 16 KB page support for native libraries, engines, and ad and billing SDKs. The snapshot recorded update blocking from 01.02.2027. Recheck before relying on either that date or the earlier 2025 deadline. Source opened: https://developer.android.com/guide/practices/page-sizes
- For personal Play accounts created after 13.11.2023, the snapshot recorded a closed test of at least 12 continuously opted-in testers over 14 days before an application for production access. Observe the actual access decision. Source opened: https://support.google.com/googleplay/android-developer/answer/14151465
- The Apple snapshot recorded Xcode 26+ and iOS26+ SDK from 28.04.2026 and iOS13+ minimum deployment target for uploads from 09.09.2026. Record build SDK and deployment target separately. Source opened: https://developer.apple.com/news/upcoming-requirements/
- Derive privacy, permissions, ads, IDFA or tracking consent, child and audience settings, account deletion where relevant, age rating, export compliance, third-party SDK disclosure, and privacy manifests from the real binary and backend. Verify any declaration such as «нічого не збираємо».
- Google Data safety includes SDKs. Source opened: https://support.google.com/googleplay/android-developer/answer/10787469
- Apple App privacy, opened: https://developer.apple.com/app-store/app-privacy-details/. Apple privacy manifests and required reason APIs, opened as JS shell with indexed official text: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk

## 3. Store facts and a commerce implementation contract

Verify regional exceptions and entitlements for external billing. Native StoreKit and Play Billing are the baseline routes for digital goods. The snapshot recorded that bought Apple currency should not expire, restorable products need restore, and both stores require disclosing paid random-item odds before purchase. Check applicable regional and age rules independently.

Official sources previously consulted:

- https://developer.apple.com/app-store/review/guidelines/ — 3.1.1 and 3.1.2.
- https://support.google.com/googleplay/android-developer/answer/9858738 — payment, prices and currency.
- https://support.google.com/googleplay/android-developer/answer/18265346?hl=en — randomized items disclosure effective 29.10.2026 in the snapshot.
- https://developer.android.com/google/play/billing/integrate — purchase lifecycle.
- https://developer.android.com/google/play/billing/security — token verification, PURCHASED and PENDING, acknowledgement and voids.
- https://developer.apple.com/documentation/storekit/in-app-purchase — StoreKit verification and server notifications, opened as JS shell with official search summary.

Suggested lifecycle: catalog and revision, store price, user confirmation, pending, verified or rejected, atomic idempotent grant, acknowledgement or finish, and entitlement. Use verified purchaseToken for Android and verified transaction identity for iOS. Android orderId cannot replace purchaseToken as the deduplication key. Keep PENDING outside grants. Cover duplicates, restart between debit, grant and acknowledgement, cross-device restore, refund, revoke, chargeback, expired and cancelled subscriptions, offline retry, clock changes, and account migration. Record purchases, rewards and currency with atomicity and reconciliation. Report sandbox transactions independently of live revenue.

## 4. Cost and engine selection

The historical source recorded Play enrollment at $25 once and Apple Developer Program at $99 per year, subject to regional currencies and taxes. Verify current fees independently of ChatGPT or Codex subscription. An Apple organization account needs a legal entity, D-U-N-S, and signing authority. Verify individual seller identity constraints. Sources opened: https://support.google.com/googleplay/android-developer/answer/6112435 and https://developer.apple.com/help/account/membership/program-enrollment/.

Consider Godot first for suitable 2D and stylized 3D without royalty. Consider Unity where needed SDK and production capabilities are materially stronger. Select after a representative device, export, and plugin probe rather than a generic claim of «кращий рушій». Pin engine, exporter, JDK, SDK, NDK, plugins and compatibility.

- Godot MIT, commercial use and credits, opened: https://godotengine.org/license/. The stable Android export recipe named OpenJDK17 and SDK35 while the Play snapshot recorded API36. Verify the actual compatible toolchain before claiming policy readiness. Source opened: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html
- The Unity snapshot recorded Personal eligibility based on Total Finances over the previous 12 months and a $200k threshold. Verify the plan and limits before making a claim such as «Unity безкоштовний завжди». Source opened: https://unity.com/pages/license-compliance

## 5. Candidate authoring stack without new software costs

| Need | Candidate | Evidence for acceptance |
|---|---|---|
| 3D mesh, rig, skin weights, animation, LOD and collision | Blender | Source `.blend`, export, axes, scale and units, materials and shader conformity, deformation checks. |
| 2D paint, textures and UI | Krita and vector editor where needed | Editable source, exact palette, licensed fonts, slices, atlas and import settings. |
| Composition and synthesis | Available DAW with Surge XT, own MIDI or stems | Actual composition, coherent sound palette and observed quality. |
| Recording, editing, mastering and loops | Audacity and FFmpeg analysis | Clean source, stems, seamless loop, peak and loudness report and device mix audition. |
| Licensed coherent assets | Kenney CC0 or other verified packages | Per-file rights, style adaptation, attribution and provenance. |
| Runtime adaptive audio | Godot audio buses and AudioStreamInteractive or equivalent | Transition table, ducking, voices, interruption and resume, latency, memory and devices. |

- Krita commercial artwork, opened: https://krita.org/en/about/license/. Blender commercial artwork: https://www.blender.org/about/license/ was officially indexed, and direct request returned 402. Original page retrieval was unverified.
- Audacity and Surge XT, opened: https://www.audacityteam.org/faq/ and https://surge-synthesizer.github.io/.
- Kenney CC0 assets, opened: https://kenney.nl/support. The cited asset license excludes the Kenney logo.
- Godot audio, opened: https://docs.godotengine.org/en/stable/tutorials/audio/audio_buses.html and https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html.

Suno's free generated tracks were noncommercial under the policies in the snapshot, with no automatic retroactive commercial rights after upgrade. Use an existing paid route only after checking current rights for the specific output. Check editable stems, loops and style as applicable. Any claim of consistently comparable quality needs actual auditions. Sources opened: https://help.suno.com/en/articles/9601601 and https://help.suno.com/en/articles/2425729.

## 6. Integrate haptics, music, and visual feedback

Android's official guidance recommended subtle, consistent, meaningful effects, system effects and primitives, coordination with visual and audio feedback, and fallbacks according to actuator. Omit sustained buzzing fallbacks when they degrade the experience. Source opened: https://developer.android.com/develop/ui/views/haptics/haptics-principles.

Apple HIG: https://developer.apple.com/design/human-interface-guidelines/playing-haptics was opened as a JS shell and the official search supported limiting repetition.

Recommended event contract: event ID, visual frame or phase, sound cue, semantic haptic pattern and priority, cooldown, device fallback, opt-out and accessibility. Observe actual iPhone and Android hardware under gameplay density. Derive timing and frequency from context and devices.

## 7. Evidence expected from skills

Each stage returns executable evidence or an accurate blocker. Verify Mac and Xcode route for iOS export and testing, signing before claiming an installable IPA, actual listening before audio acceptance, and store upload and availability as distinct facts. An exact early screenshot binds intent. Verify motion, rig, physics and audio separately with representative runtime and appropriate criteria. When budget or hardware prevents the accepted target, bring concrete choices to the owner before changing style, engine or mechanics.

## Primary references for commerce QA 3.0

Checked on 2026-11-02. Recheck official APIs and timelines before release and bind them to the exact candidate. Use these sources to establish platform testing contracts. Commercial success requires its own evidence.

- Apple, [Testing at all stages of development with Xcode and the sandbox](https://developer.apple.com/documentation/StoreKit/testing-at-all-stages-of-development-with-xcode-and-the-sandbox). Use the correct environment and product type for restore, pending, deferred, interrupted, failed, refund and subscription tests. Verify App Store Connect catalog and live readiness separately.
- Google, [Play Billing security](https://developer.android.com/google/play/billing/security). Verify purchases before granting and distinguish purchased and pending. Check idempotent grants, acknowledgement and consumption with the provider purchase identity. Choose backend and API from current guidance and actual architecture.
- Google, [Policies for ad units that offer rewards](https://support.google.com/admob/answer/7313578). Explain the action and reward before opt-in, preserve normal use after decline, and deliver the promised reward once requirements are met.
- Google, [Create a rewarded ad unit](https://support.google.com/admob/answer/7311747). Check frequency caps and server-side verification alongside the actual game's attempt budget and grant durability.

For the project, record checked URL, date and applicable rule, exact SDK, API and product versions, candidate and test evidence. Check actual binary and config as applicable.

## Apply dated source snapshots in 4.0

Preserve the provenance of all historical figures, fees, and SDK constraints above. Before actual release, check current official docs and bind requirements to engine, exporter, plugin, SDK, target and signed artifact. Verify provider and catalog capabilities per operation, plan and rights.

Treat cloud continuity, OS backup and purchase restore as distinct. Verify native bridges and SDK versions, OS support, and conformance through actual probes. Verify persistence independently of accounts and store publication. Change minimum OS or add a paid backend only where the product requires it and current authority permits.
