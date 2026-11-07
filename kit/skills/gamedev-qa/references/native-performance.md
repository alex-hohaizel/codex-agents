# Нативність, пристрої та performance

## Platform evidence

Артефакт прив'язаний до source commit, baseline hash, toolchain/config і actual build log. Перевірити package/bundle ID, version/build, architectures, min/target OS, permissions/entitlements, signing status, SDK/native-library compatibility та artifact SHA. Не робити висновок з розширення файла.

Android APK локально встановити й пройти launch/update smoke. AAB перевірити через derived splits або internal track; перевірити assets/ABI/language delivery. Android native libraries і page size перевіряти поточними SDK tools та відповідним device/emulator profile. iOS Simulator `.app`, archive і device-signed IPA/TestFlight мають окремі claims; Simulator не доводить haptics, thermal чи production renderer.

Офіційні live references: [Android App Bundle](https://developer.android.com/guide/app-bundle), [Android page sizes](https://developer.android.com/guide/practices/page-sizes), [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/). Store requirements recheck при release; QA snapshot має дату/URL/результат.

## Device matrix

Для обраних платформ визначити lower/mid/high target tiers, OS range, phone/tablet лише якщо підтримується, aspect ratios/safe areas/notches, renderer/refresh-rate variations, storage/memory constraints. Кожний row має actual availability, build, test scenarios, result і remaining risk. Один flagship не закриває lower tier; emulator не позначати physical device.

План не може обіцяти всі devices світу. Scope обґрунтувати support policy та representative risks. Якщо потрібен cloud device lab, вказати actual access/вартість; підписка Codex не означає включені device-lab хвилини.

## Методика вимірювання

Фіксувати build quality tier, scenario/seed, duration, warm-up, battery/temperature state, power mode, network, refresh rate й profiler overhead. Міряти frame-time distribution/p95/p99 та hitch count, CPU/GPU bottleneck, peak/steady memory/allocations/leaks, startup/load time, battery/thermal behavior, network requests/latency та IO.

Порівнювати із frozen budgets; averages недостатньо. Sustained representative gameplay достатньої тривалості визначається ризиком thermal/session design. Не вигадувати 60 FPS за коротким editor demo. Для audio перевірити latency/underruns/polyphony, для touch input-to-feedback — виміряти доступним методом із його похибкою.

Worst-case scenes: максимальний accepted enemy/particle/audio count, stacked modifiers, long run/high collection state, content streaming, network retries, opening heavy UI, season/shop inventory, low storage, repeated resume. Перевірити graceful degradation без зникнення важливих telegraphs.

## Lifecycle та interruptions

Pause/resume/kill, OS memory pressure, incoming call/audio focus, headphones/Bluetooth change, lock/unlock, notification/deep link, permissions denied/revoked, network airplane/slow/flaky switch, battery saver/thermal throttling, background purchase/reward callbacks. Progress/save/reward state має зберігати invariants і зрозумілий player recovery.

## Artifact lineage

Raw profile/capture/log містить build hash/device/OS/time/procedure. Скріншот профайлера без trace може бути допоміжним; відсутній raw result не підміняти точними числами. Retest після optimization має порівнюваний scenario. Release binary відрізняється від profiled debug — провести релевантний release smoke та назвати вимірювальну різницю.

## Cold use, transition і adaptive quality

Профілювати cold install/cache/driver/first shader/effect/animation/audio/load окремо від warmrun. Вимір transition включає old+newscene overlap, decode/UI buffers, owner/lifetime/unload і повторніпереходи; filesize не RAM/VRAM. Для qualitycontroller перевірити threshold/hysteresis/cooldown івідсутність oscillation/втрати criticalcue/зміни physics.

Nativeadapterconformance виконуєтьсяпід signed release для neededcallbacks/lifecycle/account/cancel/errors. Input-to-present latency має namedmethod/errorbar;60FPS не гарантує one-frame response. Зіставити exactcrashsymbols з buildidentity й actualnetworkegress зі privacyclaims.
