# Resumable artifact and publication work

[Українська](RESUMABLE_WORK.uk.md)

This contract protects completed work when an executor, tool or conversation stops. It cannot change a conversation's read-only state or establish why the host ended it. Artifact completion and platform diagnosis require separate evidence.

## Recover one confirmed stage

1. Read the saved checkpoint and actual repository head. Record the reviewed baseline, requested deliverables, selected campaign, accepted decisions, artifact paths, completed checks, unresolved external outcomes and exact next action. Load only the sources needed for that action.
2. Reuse completed output only when its input and output fingerprints still match. A running, failed or interrupted receipt is unfinished work even when files exist. Do not reconstruct or regenerate accepted completed artwork merely because a new chat began.
3. Execute one bounded stage at a time. Persist its status before execution and its verified result immediately afterward; report a concise stage result and continue already authorized work.
4. Keep private execution receipts, inventories, logs and temporary stage files outside curated source/package inputs. Do not publish conversation histories, credentials or host-specific evidence in reusable sources.
5. If an external write outcome is uncertain, inspect the destination before retrying. For Git publication, reconcile the current head, use the expected parent and verify the final remote ref/tree plus changed and removed paths. A local commit, successful upload attempt or passing local test is not remote publication.
6. Deliver actual files and final revision links. Distinguish source integrity, visual localization, execution checks, archives, remote publication, CI, host discovery and product acceptance.

## Current campaign stages

Read `marketing/CURRENT_CAMPAIGN.json` and the active campaign README. The current source is `marketing/campaign/`, with corresponding English and Ukrainian artwork. Preserve the exact Ukrainian source-cover checksum; keep the English composition tied to its Ukrainian counterpart. Do not resume a retired gallery or rejected renderer.

```sh
python3 -B marketing/campaign/build_campaign.py
python3 -B marketing/campaign/check_campaign.py
python3 -B kit/verify_release.py
python3 -B scripts/check_repository.py
python3 -m unittest discover -s scripts/tests -v
python3 -B scripts/build_packages.py
```

The compatible `scripts/showcase_pipeline.py` runner uses `export` → `build` → `validate` → `package` for this current source. Canonical outputs are `marketing/campaign/index.html`, `en.html`, `uk.html`, compact `pdf/Campaign.en.pdf` and `pdf/Campaign.uk.pdf`, and `exports.json`. Full-quality PDFs and standalone galleries remain private delivery artifacts under `reports/local-campaign-artifacts/`; they are not duplicate Git sources. The default `reports/local-showcase-pipeline.json` checkpoint name remains compatible. Its checkpoint and logs are local execution data, not release artifacts. Keep their paths outside packaged roots and stage outputs. A moved checkout needs a new path-bound receipt; retain the old one as evidence rather than rewriting it to fabricate continuity.

## Acceptance and interruption

Only one runner may own a repository at a time. Bound command duration and log size. Termination must stop owned child processes, retain an interrupted state and exit; cleanup must never bypass a host termination decision or silently resume after it.

Prepare output in a temporary staging location, validate the complete expected set and only then replace local published output files. Individual file replacement can be atomic without being a whole-directory transaction. A hard stop may leave a mixed set; unfinished receipts and source/output checks must reject it on resume. Missing, modified or partially generated output requires another run. Changed inputs during execution prevent acceptance.

The current campaign builder and checker own their dependency and artifact requirements; read that README. Missing dependencies are a concrete local blocker, not proof of a corrupted chat. Neither a source archive nor this contract installs a skill, deploys a product, starts another conversation or repairs a server-side task.

## Diagnose read-only conversations separately

Preserve the conversation URL/ID, event time and timezone, model, app version and explicit termination notice when available. Check the same conversation on web. A screenshot proves the displayed symptom, not its underlying event. Platform support needs event evidence to investigate; smaller stages or a new checkpoint are not a confirmed fix for the ChatGPT service.

These are compatible repository controls. Existing verified 5.0.0 installations need no reinstall; native product state and installed icon identity remain unchanged. To stop using a local runner, retain its receipts and continue from verified artifacts using the ordinary manual checks and authorized publication procedure.
