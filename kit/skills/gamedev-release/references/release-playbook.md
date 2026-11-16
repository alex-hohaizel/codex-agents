# Release playbook

## 1. Inputs and decisions

Require a hash-locked upstream QA manifest, Git commit or tag, target platform and device matrix, accepted visual and runtime identity, asset and import receipts, economy and catalogue and save versions, exact candidate test results, the applicable studio masters and hashes, unresolved issues, and a recorded risk decision. Preserve `blocked` and unproven claims until the required evidence exists.

Record an open material decision with its question, alternatives, recommendation, trade-off, affected requirements and files, and dependent action. Account type can change seller identity, privacy, and test requirements. Purchase authority changes fraud, cost, and restoration. Platform choice affects toolchain, asset budgets, and signing. Age and markets affect ads, random rewards, and legal review. Bind choices to the owner's actual decision for this game.

## 2. Studio and account readiness

Execute authorized and supported studio, account, and store operations using a sufficient plugin, API, CLI, or permitted browser. For owner-only MFA, legal or signature and payout confirmation, or missing permission, give the exact blocked step, prepared fields and files, expected result, and safe way to return evidence. Verify the actual outcome without disclosing private information.

### Google Play

1. Use official Play Console enrollment. Select the correct account type and complete applicable identity, fee, and device verification. Select an organization account only for an actual verified organization.
2. Verify legal and public developer names, contact and address exposure, payments merchant, and banking and tax readiness. Store public identifiers and completion status in the package. Leave private details with the provider.
3. Create the app record with the accepted name, default language, game classification, and free or paid model. Pin the application ID under the studio namespace before first upload. Record brand and legal identity separately.
4. Define Play App Signing and upload-key custody and recovery. Keep private keys out of Git and packages. Record public certificate fingerprint and the secret reference.
5. Configure required internal or closed testing and tester management. Verify current cohort and duration requirements for applicable personal accounts and record actual participants.
6. Add service account or API access only when required, restricted to the app and least permissions. Keep secrets in the CI secret store.

### Apple

1. Choose individual or verified organization enrollment. Verify the current seller-name display rules and any organizational D-U-N-S, website, email, and signatory requirements.
2. The owner completes Apple Account, MFA, and personal agreements when required. Execute supported authorized configuration. Before commerce, check program and team, contracts, tax, banking, and permissions.
3. Create an explicit App ID and applicable capabilities, bundle identifier under the studio namespace, SKU, and App Store Connect record. Bind the exact team in Xcode.
4. Configure automatic signing or document the justified manual path. Establish custody and revocation. Enable APNs, iCloud, and Game Center only when the game requires them.
5. Configure applicable sandbox testers, IAP products, TestFlight group, reviewer contact, and test login. Use an App Store Connect API key only when needed and only from a secret store.
6. Observe and record the actual outcome of MFA, agreements, and payment actions.

Check the current console for field names. If the available connection is read-only, give the exact manual field mapping.

## 3. Build receipts and native QA

For each artifact, record source commit, dependency lock hash, engine and export templates, host OS and architecture, SDK/JDK/NDK/Xcode, build command or CI run, UTC timestamp, platform and ABI, application ID, version and build, signing mode and public certificate fingerprint, artifact path and hash and size, symbols path and hash, runtime configuration and catalogue and content versions, tests, and limitations in `build-receipt`.

Use a debug APK for a quick local install and a signed release APK for representative QA. An AAB is a publishing format. Use `bundletool` or an internal track to validate device-specific splits from that exact AAB. Track local installation and provider upload acceptance separately.

The iOS Simulator `.app` targets simulator architecture and destination. A device build requires its own compile, sign, and install procedure. `.xcarchive` includes the archive and dSYM. `.ipa` depends on export method and provisioning. Document reprovisioning and the limits of a free Personal Team. TestFlight uses its authorized distribution route. Exclude local credential paths and secret values from release artifacts.

Cover clean install, upgrade from supported prior saves, cold and warm launch, interrupted launch and download, background and foreground, calls and audio interruptions, supported rotation, safe areas and cutouts, memory and thermal and battery pressure, airplane mode and network change, restoration, purchase pending/cancel/retry/duplicate, ad no-fill, sound and haptics, text scale and accessibility, and language and fonts. Profile frame-time p95 and p99 and sustained sessions on representative minimum devices. Each required profile needs its own trace. Smoke test the server with the exact candidate configuration. Record unavailable devices and release impact.

## 4. Commerce, ads, and backend adapters

For each provider adapter, record `provider`, `version`, `license`, official documentation URL and date, actual SDK or tool route, host requirements, test credentials reference, live setup owner, recurring cost estimate and cap, data classes, permissions, age and market restrictions, success and error contract, retry and idempotency, fixture, rollback, and uninstall or revocation. Add dependencies as needed. Start with the smallest sandbox transaction or verified export on the target device.

Map internal product ID to Apple product ID and Play product or base plan, type, entitlement, currency grant, markets, exact duration and expiry, restoration, and refund. Read price from the store API. For random rewards, record disclosure version, pool, weights, pity, and caps before purchase, with atomic draw and grant and an audit record. Preserve accepted free paths and power limits. Check current market-specific rules with appropriate sources.

Model the entitlement workflow from received through verified, rejected, or pending, committed grant, and platform acknowledgment or finish. Use grant deduplication, applicable outbox and inbox, reconciliation, retry budget, and failure queue ownership. Handle duplicate and out-of-order callbacks and later refunds. Preserve grant-once behavior. Verify the Google Play purchase token's identity contract and the selected Apple signed-transaction chain and claims through the current pinned SDK or API. Use the provider's supported transaction identity. Restore durable ownership without reissuing consumed goods.

Map each ad placement to triggering moment, reward, cap and cooldown, consent, test and live mode, cancellation, no-fill and offline paths, server-side verification where applicable, and idempotent grant. Verify voluntary decline and return. Keep test identifiers out of live setup and use authorized test traffic during QA. Separate revenue telemetry from simulated impressions.

Deploy backend and services to staging first. Validate configuration, dry-run migrations, verify backups and restore, and apply least privilege, applicable TLS and security headers, request and cost limits, health checks, alerts, status and support ownership, region, retention, and deletion. Plan rollback for database migrations independently of flags. Bundle code and public configuration and retain secrets in the approved secret store.

## 5. Store metadata and privacy

Track `field → source file → locale → validation → console target → status`. Cover title, subtitle, short and full descriptions, keywords, category, ratings, screenshots, icon, feature graphic, video, support and privacy and marketing links, reviewer instructions and contact and login, availability, pricing, and IAP descriptions. Copy exact accepted studio assets and attribution from the corresponding master.

Capture screenshots and video from the runtime candidate at current store dimensions and locales. Identify marketing illustrations separately. Verify readable HUD and touch controls, clean captures without debug or personal data, and supported feature claims. Check actual store specifications for required device sizes.

For each SDK and backend, inventory data, purposes, collection and sharing, linkage and tracking, consent and lawful route, retention and deletion, recipients and regions, encryption, and source evidence. Check observed network and runtime behavior, permissions, and manifest. Implement applicable Apple ATT with a usable game when declined. Align privacy policy and disclosures with actual build behavior. For accounts, cover required deletion, guest upgrade, and restore conflicts. Check current age, ads, privacy, SDK, and store requirements for child-directed products.

## 6. Beta, launch, and rollback

Sequence the local release candidate, internal beta, applicable closed or external beta, frozen exact RC, review submission, approval, staged rollout, and monitored expansion. Choose rollout percentage, duration, and stop thresholds from the product and sample. D1 and D7 require real cohorts and elapsed time. An initial release may use a measurement plan for still-pending results.

Before an external action, record target, track, version, hash, build, configuration, store fields, price scope, and authority. After it, record the provider receipt and observed status. Track upload success, review approval, and availability in each region as distinct facts.

Stop for meaningful crash or ANR regressions, missing or duplicate entitlements, corrupted saves, unacceptable input, audio or thermal problems, privacy discrepancies, or unsustainable cost. Options include halting rollout, disabling an affected offer, ad, or event, pinning or reverting content and configuration, applying a backward-compatible backend rollback, and shipping a forward binary fix. Confirm the store's actual rollback options. Keep older active clients compatible through the defined window and preserve purchased entitlements when disabling a feature.

## 7. Handoff and acceptance

Include immutable prior package references and hashes, applicable studio assets, exact candidate and build and store IDs, runtime configurations without secrets, metadata and catalogue and odds and privacy and license snapshots, install instructions, coverage and defects, deployment evidence, backup and restore, symbols and debug mapping, measured dashboards and alerts, save, content, and economy migrations, rollback and roll-forward, support contacts, credential references, and next action in `release-handoff`.

Ready to release requires passing checks and explicit remaining provider approvals. Released requires an actual receipt, channel availability, and a post-action smoke test. Support ready requires validated ownership, runbooks, access, and alerts. Record exact blockers and reproducible next steps when a native toolchain, signature, device tests, or access is missing.

## Launch acceptance matrix

Before review, derive cases from actual features, current model, launch scope, and affected dependencies using `assets/release-case-catalog.json`. Add product-specific journeys. Preserve all proof obligations. The QA freeze records the denominator for launch content, screens and states, progression phases, offers, and target platforms. Run the required cases beyond the representative slice.

Bind internal offers to actual product type, entitlement and content version, trial and earning options, localized price, duration, cap, overlap, expiry, restoration and refund, UI entry and decline and use, and ledger events. For boosts and attempt limits, check clock drift, overlap and upgrades and expiry, restart and restore, and the strongest cumulative portfolio. Preserve state across switches unless the accepted rule explicitly changes it.

The listing and reviewer instructions show actual content, learning, and return. Disclose finite launch content and online or download requirements. Market retention and revenue require actual cohorts. Record a reproducible measurement plan.

## Release candidate continuity and operational identity

Verify full launch coverage, exact signed adapter conformance, source, assets, configuration, catalogue and content, save epoch, matching symbols, and actual QA. Add damage, death, crash and retry through reward and durable save, cold restore, representative saved-data migration, profile and account conflicts, ignored parameters, import semantics, and feature-specific assembly parity.

Activation must preserve a coherent dependency closure and client compatibility. Verify downloads, stage, and activate atomically or keep the old coherent set. An incremental patch pins exact released base bytes and hash and an authorized complete fallback. Verify the save schema against the previous reader before using a rollback route. The monitoring handoff includes actual source, query, and alert-delivery receipt, or a clear unconfigured status.
