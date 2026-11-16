# Update the personal skill suite in Work or Codex

Contents: scope → manifest → audit, apply and verify → recovery → evidence limits.

`scripts/update_skill_suite.py` is a standard-library helper for exactly 33 personal skills. It does not publish to Work, execute a product, or change `AGENTS.md`, Codex configuration, roles, system skills, or plugin caches. Save personal Work skills through the supported Work operation.

## Kit manifest

The kit root contains `manifest.json` and `skills/<stable-name>/...`. The format is `atelier.skill-suite/1`. Its fields include:

- `suite_id`: a non-empty identifier for the verified kit.
- `skills`: exactly 33 distinct stable names from the helper's allowlist.
- Each skill: `name`, `version`, `files`, and optional `previous_trees`.
- `files`: POSIX relative path → `{sha256, size, mode}`. Mode is an integer POSIX permission value, for example 420 for `0644` or 493 for `0755`.
- `previous_trees`: verified predecessors identified by `{tree_sha256, source}`. These are accepted source bindings. Do not add an arbitrary hash to hide installed drift.

For an agreed new release add top-level `visual_identity_policy: "preserve-existing/v1"`. It preserves existing local icons, their `icon_small` and `icon_large` references, and `brand_color`. The manifest remains `atelier.skill-suite/1`. An older kit without this policy retains strict full-tree matching.

To accept a local visual difference from a verified predecessor, include in its `previous_trees` record the full canonical `files` manifest without volatile caches and `ui_yaml`, the exact UTF-8 text of `agents/openai.yaml`. The helper checks logical hash, YAML bytes and size, and the file records. Take these from the actual verified predecessor. Unknown drift is not a canonical baseline.

## Preserving visual identity

Audit compares behavior-bearing sources against the new canonical or an explicit previous baseline. Permitted differences are the three `interface` fields `icon_small`, `icon_large`, and `brand_color`, and bytes and modes of the referenced local images. Remaining YAML, including prompt, policy, and dependencies, and all other files must match a known source. Take the new visible name from canonical `display_name` and preserve frozen icons.

Supported assets are relative paths under `assets/` with image suffix `.svg/.png/.jpg/.jpeg/.webp/.gif/.ico`. Missing files, paths outside the root, traversal, symlinks, special files, case or Unicode collisions, and file-directory collisions block the update. A pointer cannot hide changes to scripts, policy, or other non-icon files from any declared baseline. Both icon fields may refer to one image. The one historical `./assets/…` prefix normalizes for lookup only. Preserve exact `icon_small` and `icon_large` strings. Double `././`, traversal, and arbitrary alternative forms are blockers.

The restricted YAML reader handles only single scalar visual fields in a plain `interface` mapping. It checks other fields against the exact baseline, without running a general YAML parser or executing tags or aliases. Unexpected formatting elsewhere can require separate reconciliation and does not permit behavior drift.

Audit records `visual_preservation` and effective `desired_files` separately from the canonical manifest. Apply rechecks the binding, backs up the whole tree, and takes icon bytes only from that verified copy. New code and instructions come from the kit. The journal records exact before and after hashes. Rollback restores previous YAML, icons, other files and modes.

To verify continuity of customized local icons, use the exact completed apply journal. Current files alone do not prove which icons were present before the update. Do not substitute a journal from another kit, target, or unfinished operation.

Do not merge different visual identities of personal duplicates. Reconcile the intended canonical target first. Do not quietly retire differing icons with `--retire-known-duplicates`. Project agents are outside this core installer's scope. Update and preserve them through their own project-local adoption.

Logical tree hash is the SHA-256 of UTF-8 sorted records `relative_posix_path + NUL + file_sha256_hex + LF`. Only `__pycache__/...` and `.DS_Store` are excluded from the logical hash. Full snapshots and backups preserve all files, empty directories and permission bits, including caches. Unknown files are not ignored. Reject traversal, links, special files, case and Unicode collisions, and unexpected kit bytes.

Unpacking a ZIP can change source modes. The helper checks source bytes, size and path, then sets and verifies declared target modes. Special permission bits are unsupported.

## Audit → apply → verify

From the portable kit root when the helper is under `portable/`:

```bash
python3 portable/update_skill_suite.py audit --kit . --plan ../skill-update-plan.json
python3 portable/update_skill_suite.py apply --plan ../skill-update-plan.json
python3 portable/update_skill_suite.py verify --kit . --journal /absolute/backup/run-ID/journal.json
```

Default target is `~/.agents/skills`, additional personal discovery root is `~/.codex/skills`, and backup root is `~/Codex_Skill_Backups`. Set `--destination`, `--legacy-root`, and `--backup-root` explicitly in `audit` when needed. Keep backup and plan outside discovery roots. `audit` without `--plan` only prints JSON and creates no installation or backup directory.

For `verify --journal`, use the actual `journal` returned by completed apply. For a canonical install with no visual overlay, `verify --kit .` verifies bytes but cannot prove continuity without its receipt.

`apply` uses the exact `--plan` and rechecks kit and recorded target snapshots. Unknown drift, a new name in an occupied canonical target, and changes after audit block the operation. There is no blanket `--force`. Make a complete verified backup for each changed skill. Prepare payload outside the discovery roots, replace each tree using same-filesystem rename, and journal the action. This is a recoverable per-skill transaction. It does not make the whole 33-skill update atomic or guarantee recovery from disk failure. Require exclusive control of the relevant source and target ancestors while applying.

An unchanged canonical target is a no-op. Applying an already finished plan again does not duplicate work if its targets still match the receipt. Changed targets require a new audit.

## Duplicates and search scope

Discovery reads frontmatter without assuming that the directory name is the stable name. Check immediate personal skill entries and skip system and hidden directories. Unresolved links in a discovery root block audit because their scope cannot be verified without following them.

Additional `--project-root /absolute/project` options report duplicates under project `.agents/skills` and `.codex/skills`. These findings are read-only. Project files and arbitrary nested source kits are not automatically moved or removed.

A known personal duplicate can be included in a specific plan by running audit again with `--retire-known-duplicates`. Its logical tree must match the new tree or a verified `previous_trees` entry. Back up the complete copy before retiring it from personal discovery. Unknown personal and project duplicates remain blockers.

## Interruption and rollback

Apply returns the exact `journal` at backup `run-.../journal.json`. If execution started and failed, the JSON error also includes the journal path.

```bash
python3 portable/update_skill_suite.py apply --plan ../skill-update-plan.json --resume /absolute/backup/run-ID/journal.json
python3 portable/update_skill_suite.py rollback --journal /absolute/backup/run-ID/journal.json
```

Resume checks the same plan and kit and observes actual trees. It recovers only unambiguous backup, preparation, old move, and new install phases. Do not bypass an active lock. Recover a stale lock only for the same operation and plan on the same host after confirming the old PID is gone. A different host, live or reused PID, or ambiguous state blocks automatic replay.

If a process stops after locking but before the first `journal.json`, find the operation path in `backup-root/.skill-suite.lock`. The same `apply --plan ... --resume <operation>/journal.json` restarts only if plan and lock match, the PID is gone, all audited targets and kit are unchanged, and no unknown operation or staging data exists. Preserve unknown files. An ambiguous missing-journal case requires manual reconciliation.

Rollback first checks conflicts across the suite and integrity of all required backups. Preserve later user changes. Restore exact preceding trees and modes, or remove newly created targets that did not exist before. The same rollback command can resume an interrupted rollback with unambiguous state. Reconcile an unknown state before starting another operation.

## What verify proves

`verify` checks placement, bytes, modes, stable names, and personal duplicates. With `--journal` it also checks effective payload and preserved visual identity. It reports separate `canonical_core_verified`, `visual_preservation_verified`, and `preserved_visual_identities` values. The output explicitly sets `runtime_discovery_verified=false` and `behavior_verified=false`. Refresh the catalog or open a fresh session in actual Codex, confirm the resolved source, and run the agreed bounded interaction scenarios. A ZIP and successful hash check do not prove installation, owner acceptance, or native, device, or provider behavior.
