# Repository verification record

The active published candidate on `main` is repository 1.4.0-rc.5 with core 6.1.0, optional Atelier Orchestrator 1.2.0, optional maintenance 1.1.0 and Agent Atelier 0.5.0. The repository records the scoped publication and runtime evidence separately from full programme acceptance. [Current release record](../releases/current.json) · [Requirements](requirements.csv) · [0.5.0 verification](../releases/repository-1.4.0-rc.5.md)

The 0.5.0 release passed 234 service tests and 65 browser checks. The verified scope includes a prepared task with its full next-action objective, real OpenAI Docs links and a downloaded native Codex PNG. The personal Mac update retained the SQLite file and existing records. The checked release source is `c86ce907544410afcb8bbd19181f1640446aefb7`, merged through PR #4 at `e1e6cbbbf534dbb04f2d6a2265b53ad6c9cccb96`. [PR #4](https://github.com/alex-hohaizel/codex-agents/pull/4) · [PR validation](https://github.com/alex-hohaizel/codex-agents/actions/runs/42934649314) · [Main validation](https://github.com/alex-hohaizel/codex-agents/actions/runs/42935500589)

Earlier evidence remains bound to the original source and observed scope. [Historical core and service verification](RELEASE_6_VERIFICATION.json) · [1.3.0 universal-entry verification](UNIVERSAL_ENTRY_1_3_VERIFICATION.json) · [1.3.2 passport revision](../releases/repository-1.3.2.md) · [Historical campaign closeout](history/TASK_CLOSEOUT-1.1.0.json)

## Source and identity

The core 6.1.0 kit contains 33 stable skills, 3,187 declared skill files and 3,194 curated source/support files. The release record binds the exact manifest. Verified predecessor descriptors and Git trees remain available for updater admission. Existing icon bytes, references and colors are checked against the identity baseline. [Current release record](../releases/current.json) · [Icon baseline](ICON_BASELINE.json)

No product state is reset or adopted merely by installation. Native format versions, generated-agent toolkit locks, service state and repository edition remain separate.

## Required release checks

```sh
python3 -B scripts/materialize_standards.py --check
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -B marketing/campaign/check_campaign.py
python3 -B -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

After reviewed core edits, use `scripts/refresh_kit_manifest.py --predecessor EXACT_COMMIT --write` to bind the exact prior Git source and recompute descriptors/integrity. The tool does not establish semantic approval; review source changes before using it. Run domain tests appropriate to changed contracts and the local service check/test/build described in its README.

Check both archive CRC/inventories/hashes; exclude private project/audit/account material, local state, dependencies and built transient files. Source packages do not install skills or prove Work parity. Exact installed updater journals, host-profile receipt, optional skill discovery, model behavior, browser/craft review, publication and remote CI are separate observations.

For universal entry, test direct work without forced agent construction, verified project-agent continuation, one brief/inherited authority, maintenance preservation and the full factory-to-original-result path. Check that every documented helper command resolves to a pinned local file or a verified explicit dependency. Routing declarations do not certify semantic fit or consent. Native portfolio checks cover pagination/partial access, project grouping, received-answer versus accepted-result provenance, skill mention versus actual source selection, planned-agent status, idle ownership and protected-controller preconditions. At least one complex case must produce an integrated final output against its original brief/reference; a routing protocol or collection of successful reports is insufficient.

Seven full guides preserve translated steps/commands and corresponding hashes. Seven UI catalogs must cover all current keys; actual language/layout review remains separate from key parity. The current marketing images are historical accepted references, not screenshots of a live product or certification of all illustrated capabilities.

## Publication

Read the authorized destination branch, reconcile intervening changes, publish the verified reusable files and confirm the resulting remote commit and tree. Record the exact checked source revision and applicable CI result. Retain private raw evidence outside reusable sources. [Publication contract](UPDATE_CONTRACT.md)
