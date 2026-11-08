# Repository verification record

Repository edition **1.1.0**; reusable suite **5.0.0**. Current task date: 2026-11-08. Final observed results and remote revision belong in `governance/TASK_CLOSEOUT.json`.

## Source and identity scope

The canonical suite baseline contains 33 stable skills and 2,955 skill files. Its release verifier covers 2,962 curated source/support files; manifest SHA-256 is `489c59fa08cccb77ecdfb0d609521320e1d16504b72494f3866ec845e8d50b07`. The edition must preserve the canonical skill and installed-icon baseline bytes. Guide files intentionally change to add localized campaign/compatibility entries, so the former comparison that included unchanged guide files is not evidence for this edition.

The original Ukrainian campaign cover is preserved with SHA-256 `ac9fad92384396039af134c824cf1663e0e00ca1d94fc3fc7767b997d4d82c4f`. English artwork is a corresponding lettering localization. Intended 1:1 composition is separate from measured pixel identity; the localization review must state what was actually inspected.

## Current required checks

```sh
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -B marketing/campaign/check_campaign.py
python3 -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

Run against the final source tree after localization and cleanup. The campaign check covers both language inventories, artifact receipts/page counts and source-image correspondence. Visual review of translated content, composition preservation and rendered PDFs is separate from file-hash checks. Record actual browser testing separately; source parsing alone is not browser layout acceptance.

The full guides remain complete in seven languages. Equivalent localized campaign/compatibility paragraphs were added without changing installation commands, numbered steps or stable skill identifiers; `docs/translations.json` records their current English source hash and localized hashes. Advertising is EN/UK only.

Current packages must include the new campaign and exclude deleted draft advertising, private product agents, credentials, chat histories and host-specific evidence. Check both archive inventories and hashes, and record reproducibility only when actually compared. Work/Codex source bundles do not perform installation merely by existing or being extracted.

## Publication and task closeout

Read the current remote head before writing, reconcile intervening changes, publish the authorized cleanup with the expected parent, and read back the final ref/tree and affected paths. An attempted upload or local passing check is not publication. Record actual remote CI separately; a workflow file is not proof of a successful run. Do not mark remote publication or CI completed before observing their results.

`TASK_CLOSEOUT.json` starts with pending evidence fields and is finalized by the publishing executor. This record intentionally does not fabricate final commit IDs, remote paths or CI outcomes.

## Historical baseline evidence

The original 1.0.0 release recorded a successful isolated portable-updater audit/apply/verify/rollback using its actual journal, seven repository-tool tests and a successful source check. Those historical results establish that baseline only; they do not prove execution on the final 1.1.0 candidate, current host discovery, device testing or product acceptance.

No product-state migration, production deployment or user-host installation is performed by this presentation/documentation task.
