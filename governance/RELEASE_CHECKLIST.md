# Release review

Copy this checklist into the release task and attach evidence, rather than checking boxes without results.

- [ ] Owner request and complete requirements recorded; no dropped deferred requirement.
- [ ] Exact current repository revision and installed-source scope identified.
- [ ] Unknown local changes reconciled; backup location outside discovery roots recorded.
- [ ] Stable skill names and system/project classification preserved.
- [ ] Suite version, repository edition and native schema changes distinguished.
- [ ] Canonical skill hashes, inventory and curated supporting-file hashes checked.
- [ ] Existing Codex icons/colours preserved; Work display profile checked separately.
- [ ] English guide and every advertised translation updated with equivalent numbered steps.
- [ ] Changelog and release-specific migration instructions included.
- [ ] Existing projects and generated agents have a preserved-context adoption path.
- [ ] Appropriate behavioural checks completed; limitations explicitly recorded.
- [ ] `python3 scripts/check_repository.py` passes.
- [ ] `python3 -m unittest discover -s scripts/tests -v` passes.
- [ ] `python3 scripts/build_packages.py` creates reproducible Work/Codex bundles.
- [ ] Archive content excludes private project agents, credentials, host backups and evidence history.
- [ ] Remote repository revision and paths verified after saving.
- [ ] File installation, host discovery, real task smoke and product acceptance reported separately.

Repository checks are evidence about these files. They do not replace domain QA, security review, native-device testing or verification of external effects.
