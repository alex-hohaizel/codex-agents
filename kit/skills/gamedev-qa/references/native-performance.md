# Native builds, devices, and performance

## Platform evidence

Bind the artifact to its source commit, baseline hash, toolchain and configuration, and actual build log. Inspect package or bundle ID, version and build, architectures, minimum and target OS, permissions and entitlements, signing status, SDK and native-library compatibility, and artifact SHA. Inspect the artifact itself.

Install the Android APK and smoke test first launch and update. Validate an AAB through derived splits or an internal track and check asset, ABI, and language delivery. Check Android native libraries and page size using current SDK tools and a relevant device or emulator profile. Record separate claims for an iOS Simulator `.app`, archive, and device-signed IPA or TestFlight. Use physical evidence for haptics, thermal behavior, and the production renderer.

Use current platform requirements for the release and record the date, URL, and result in the QA snapshot. [Android App Bundle](https://developer.android.com/guide/app-bundle) [Android page sizes](https://developer.android.com/guide/practices/page-sizes) [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/)

## Device matrix

For selected platforms, define target low, mid, and high tiers, OS range, supported phone or tablet classes, aspect ratios, safe areas and notches, renderer and refresh-rate variants, and storage and memory constraints. For each row, record actual availability, build, test scenarios, result, and remaining risk. Validate lower tiers with representative observations. Label emulator and physical results separately.

Derive coverage from the support policy and representative risks. If a cloud device lab is needed, verify actual access and cost separately from the Codex subscription.

## Measurement

Record build quality tier, scenario and seed, duration, warm-up, battery and thermal state, power mode, network, refresh rate, and profiler overhead. Measure frame-time distribution, p95, p99, and hitch count, CPU/GPU bottlenecks, peak and steady memory, allocations and leaks, startup and load time, battery and thermal effects, requests and latency, and I/O.

Compare against frozen budgets. Include tails and sustained representative gameplay long enough to cover the thermal and session risks. Claims such as 60 FPS need evidence from the required native scope. Measure audio latency, underruns, and polyphony and, for touch-to-feedback, record the measurement method and uncertainty.

Use representative worst cases, including the accepted maximum enemy, particle, and audio counts, stacked modifiers, a long run and large collection, streaming, retries, heavy UI, season and shop inventory, low storage, and repeated resumption. Verify graceful degradation and preservation of critical cues. Pin an independent trace and result for each required target profile. Report unavailable profiles with their evidence gap.

## Lifecycle and interruption

Cover pause, resume, and process termination, OS memory pressure, calls and audio focus, wired and Bluetooth equipment changes, lock and unlock, notifications and deep links, denied and revoked permissions, airplane and slow or changing network, battery saver and thermal throttling, and background purchase or reward callbacks. Preserve progress, saves, and reward invariants with a clear recovery path for the player.

## Artifact lineage

Raw profiles, captures, and logs record build hash, device, OS, time, and procedure. A screenshot of the profiler can supplement its trace. Record missing raw measurements explicitly. Optimize and retest with a comparable scenario. Run the applicable smoke test on the exact release binary and disclose the differences from the profiled build.

## Cold use, transitions, and adaptive quality

Profile first installation, cold caches and drivers, and first shader, effect, animation, sound, and loading separately from warm execution. Measure old and new scene overlap during transitions, decode and UI buffers, ownership and lifetime, unloading, and repeated transitions. Report file size, RAM, and VRAM separately. Verify threshold, hysteresis, and cooldown behavior for adaptive quality. Ensure the controller does not oscillate, lose critical cues, or change physics.

Verify native adapter conformance on a signed release for required callbacks, lifecycle, accounts, cancellation, and errors. Measure input-to-present latency with a named method and uncertainty. Record frame rate separately. Match crash symbols to exact build identity and verify observed network egress against privacy claims.
