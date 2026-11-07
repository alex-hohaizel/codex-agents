# Repository validation evidence

Initial repository edition: 1.0.0. Suite: 5.0.0. Checked on 7 November 2026.

## Canonical source integrity

The curated kit's `verify_release.py` checked 2,962 files with no mismatches. The source manifest SHA-256 is `489c59fa08cccb77ecdfb0d609521320e1d16504b72494f3866ec845e8d50b07`. The skill manifest contains 33 stable names and 2,955 skill files.

## Portable installation smoke

The actual portable updater was exercised in an isolated temporary destination, with audit plan and backups outside that destination. The temporary tree was removed after the check; no existing user skill installation was changed.

| Step | Observed result |
| --- | --- |
| Audit | No blockers; 33 install entries |
| Apply | `status=complete`, `changed=33` |
| Verify with the actual apply journal | `verified_skills=33`, `canonical_core_verified=true`, `visual_preservation_verified=true`, no failures or duplicates |
| Rollback using that journal | `status=rolled_back`, `restored_entries=33` |

The fresh destination had no prior custom icons, so this run verifies the fresh-install/journal path. It does not by itself prove preservation of every user's customized icon. The updater's custom-icon preservation checks and the existing installation's exact journal remain necessary for an update.

## Repository-tool tests

Seven offline tests passed: source corruption blocks packaging; a changed English guide invalidates translations; a private project export is rejected; archives are byte reproducible despite changed file modification times; symlink packaging is rejected; missing migration records/broken links are detected; and an unexpected icon redesign is caught even after its source manifest hash is refreshed.

Run current checks from the repository root:

```bash
python3 scripts/check_repository.py
python3 -m unittest discover -s scripts/tests -v
python3 scripts/build_packages.py
```

The final repository check passed with 33 skills, 2,955 canonical skill files, seven complete guide editions and no errors or warnings. All seven offline tests passed. Translation parity checks confirmed the same heading hierarchy, 44 numbered steps, 63 table rows, shell commands and 33 stable skill names across all editions; each edition records the English source hash in `docs/translations.json`.

Both source bundles were built and inspected. Each includes the complete guide set, kit integrity records, rights notice, migration and continuity templates, optional maintenance source and visual concept gallery. Neither contains excluded private project exports, host backup history or cache files. Exact current archive hashes and sizes are generated in `dist/BUILD.json` and `dist/SHA256SUMS`; [package instructions](PACKAGES.md) explain local builds and downloading a completed GitHub Actions artifact. A workflow run is not claimed by these local checks.

## What this evidence does not establish

Host discovery and real domain behaviour were not verified by the temporary installation. `runtime_discovery_verified=false` and `behavior_verified=false` are preserved as honest limits. Native-device performance, deployment access, another Work/Codex session, external actions and product acceptance require their own actual checks in the relevant project.
