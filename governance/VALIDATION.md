# Repository verification record

Repository edition 1.2.1; reusable suite 6.0.0. Current scoped results belong in [RELEASE_6_VERIFICATION.json](RELEASE_6_VERIFICATION.json). Historical campaign closeout remains under `history/TASK_CLOSEOUT-1.1.0.json`.

## Source and identity

The current kit contains33 stable skills,3,088 declared skill files and3,095 curated source/support files. `releases/current.json` binds the exact current manifest. Its predecessor 5.0.0 manifest descriptors, original interfaces and historical trees remain available for exact updater admission. Existing core icon bytes/bindings/colors remain bound to `ICON_BASELINE.json`;6.0.0 intentionally changes reviewed instructions/helpers.

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

Seven full guides preserve translated steps/commands and corresponding hashes. Seven UI catalogs must cover all current keys; actual language/layout review remains separate from key parity. The current marketing images are historical accepted references, not screenshots of a live product or certification of all illustrated capabilities.

## Publication

Read the current remote ref, reconcile intervening changes, publish authorized reusable files, then verify the actual ref/tree/changed paths. Observe CI for that exact commit before recording success. Retain private raw evidence outside reusable sources; publish only sanitized scope/results/limitations.

The5.0.0 campaign release and its tests are historical. The current verification record does not reuse them as proof of6.0.0 source behavior, installation or model operation.
