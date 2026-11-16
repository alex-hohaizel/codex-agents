# Handoff from implementation to QA

## Self-contained package

- Manifest with game and studio IDs, schema and revision, source commit, exact upstream references and hashes, selected platforms, and status by platform.
- Canonical source, engine project, imported assets and configuration, content, economy, and settings data, dependency locks, and build adapters. Include required editable masters and rights. Exclude caches, secrets, and unnecessary generated intermediates.
- Frozen GDD and TDD, decisions and requirements trace, style tokens, canonical image, motion, and audio references, allowed deviations, and exact studio logo, fonts, credits, and contact identity.
- Actual build artifacts and receipts. Name the exact blocker for a missing platform artifact.
- Golden inputs, seeds and saves, migration fixtures, APIs and contracts and simulation boundaries, logs, runtime captures and traces, known issues, and independent-review status.
- Clean restore and local test instructions, toolchain and version inventory, signing references without private material, backend configuration keys without values, migrations and rollback boundaries.

Keep portable source, data, and craft for additional platforms. Record separate actual QA results and gaps for each one.

## Model and runtime consistency

Include exact canonical game-model bytes and hash, derived GDD/TDD and data versions, adapter and import inventory, model-to-consumer bindings, impact analysis, design-derived scenario fixtures, and actual observations. Cover applicable camera, input, actors, equipment, world, progression, reward, learning, commerce, and lifecycle features. Preserve distinct model, runtime state, and handoff schemas, along with existing decisions and save data.

Track source completeness, structure, semantic review, actual build and device evidence, and human acceptance separately. Preserve unresolved content gaps. Transfer an unknown external transaction or deployment result with its actual request ID and reconciliation action before retry.

## Build receipt fields

The document uses `kind="actual_build_receipts"` and a nonempty `receipts` array. Each item has `receipt_id`, `game_id`, `platform`, `artifact_type`, `artifact_path` relative to the package, `artifact_sha256`, `source_commit`, `baseline_sha256`, `toolchain`, `command`, `exit_code`, `log_path`, `signing_status`, `built_at`, `build_profile`, and `limitations`. Use a deterministic file inventory for directory artifacts. Redact secrets from logs with explicit markers while preserving diagnostics.

Set `signing_status` from an actual verification tool result, or use `unsigned` or `not_checked`. Record actual runs. Keep templates and dry runs `example` or `planned`.

## Test receipt fields

Record build hash, platform, device model and OS, case and scenario and seed and input, procedure, environment and network and consent and account class, start and duration, expected result and design reference, actual output or capture or trace, verdict, actor and independence, and limitations. Exclude real credentials, personal data, and raw payment receipts from the portable archive.

## Four distinct claims

1. Source and package complete for named scope.
2. Actual build with the named toolchain and exact artifact.
3. Artifact installed and run on the named device and runtime.
4. Independent QA accepted defined product criteria.

Track store publication and market outcomes separately. Structure and byte checks establish their own scope.

## Handoff example

“Use `$gamedev-qa` with package [path/ID], revision/hash [value], platforms [value]. Verify scope [IDs], builds [receipt refs], and unresolved gaps [IDs]. Preserve the baseline and return defects with reproducible evidence to their build, asset, or design owner.”

For a directory, compute SHA-256 over UTF-8 JSON `[[relative_posix_path,file_sha256],...]` with sorted paths, `ensure_ascii=False`, and `separators=(",",":")`. Reject symbolic links. The digest records the byte inventory.

## Full Game Model handoff

Include current model version and maturity, coverage of the applicable 20 tracks, production contracts and catalogue and grammar, State Catalogue, golden saves and migrations, exact damage, physics, and lifecycle fixtures, input traces, capability, recipe, transformation and attempt references, and `AssemblyEvidence`. Transfer matching symbols, importer and toolchain locks, content epoch and patch base where required. Keep examples and plans separate from receipts.

A fresh QA receiver executes the named scenario and compares the result with an independent oracle. Return incomplete input or behavior to its causal owner. Verify signed iOS with the actual route. Bind current artifacts to their own build receipts and carry forward evidence only when semantic dependencies are unchanged.
