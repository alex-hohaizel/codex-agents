# Resumable artifact and publication work

[Українська](RESUMABLE_WORK.uk.md)

This contract protects completed work when an executor, tool or conversation stops. It cannot change a conversation's read-only state or establish why the host ended it. Artifact completion and platform diagnosis require separate evidence.

## Recover one confirmed stage

1. Read the saved checkpoint and actual repository head. Record the reviewed baseline, requested deliverables, selected campaign, accepted decisions, artifact paths, completed checks, unresolved external outcomes and exact next action. Load only the sources needed for that action.
2. Reuse completed output only when its input and output fingerprints still match. A running, failed or interrupted receipt is unfinished work even when files exist. Do not reconstruct or regenerate accepted completed artwork merely because a new chat began.
3. Execute one bounded stage at a time. Persist its status before execution and its verified result immediately afterward; report a concise stage result and continue already authorized work.
4. Keep private execution receipts, inventories, logs and temporary stage files outside curated source/package inputs. Do not publish conversation histories, credentials or host-specific evidence in reusable sources.
5. If an external write outcome is uncertain, inspect the destination before retrying. For Git publication, reconcile the current head of the active target branch, use the expected parent and verify the merged remote revision plus changed and removed paths. [Active branch rule](UPDATE_CONTRACT.md#publish-to-the-active-branch) A local commit, successful upload attempt or passing local test is not remote publication.
6. Deliver actual files and final revision links. Distinguish source integrity, visual localization, execution checks, archives, remote publication, CI, host discovery and product acceptance.

## Current campaign stages

Read [the current campaign record](../marketing/CURRENT_CAMPAIGN.json) and [gallery build notes](../marketing/campaign/README.md). Preserve the original PNG master digests and all decoded pixels of the English and Ukrainian artwork. Maintain the seven localized captions and routes to the matching diagrams and guides.

```sh
python3 -B marketing/campaign/build_campaign.py
python3 -B marketing/campaign/check_campaign.py
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

The `scripts/showcase_pipeline.py` runner stages export, build, validation, and packaging. The repository keeps the language selector, seven HTML editions, the PDF of the current illustrations, and the export manifest in `marketing/campaign/`. The runner builds the standalone `Showcase.zip` under `reports/local-campaign-artifacts/`. It contains both visual layers and links to the guides. Keep the checkpoint and logs outside packaged roots and stage outputs. For a moved checkout, create a new path-bound receipt and retain the previous one as historical evidence.

## Acceptance and interruption

Only one runner may own a repository at a time. Bound command duration and log size. Termination must stop owned child processes, retain an interrupted state and exit; cleanup must never bypass a host termination decision or silently resume after it.

Prepare output in a temporary staging location, validate the complete expected set and only then replace local published output files. Individual file replacement can be atomic without being a whole-directory transaction. A hard stop may leave a mixed set; unfinished receipts and source/output checks must reject it on resume. Missing, modified or partially generated output requires another run. Changed inputs during execution prevent acceptance.

The current campaign builder and checker own their dependency and artifact requirements; read that README. Missing dependencies are a concrete local blocker, not proof of a corrupted chat. Neither a source archive nor this contract installs a skill, deploys a product, starts another conversation or repairs a server-side task.

## Diagnose read-only conversations separately

Preserve the conversation URL/ID, event time and timezone, model, app version and explicit termination notice when available. Check the same conversation on web. A screenshot proves the displayed symptom, not its underlying event. Platform support needs event evidence to investigate; smaller stages or a new checkpoint are not a confirmed fix for the ChatGPT service.

Retain local runner receipts and continue from the verified artifacts using the authorized checks and publication procedure.
