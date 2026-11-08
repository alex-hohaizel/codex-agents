# Advertising cleanup scope

The owner authorized removing superseded advertising and replacing it with the selected English/Ukrainian campaign. This cleanup concerns the current tree; it does not rewrite Git history, change repository visibility, alter installed skill icons or remove product data.

Retire old concept galleries, scripts/manifests used only to build those galleries, concept briefs, obsolete campaign drafts and their artwork under `marketing/` and `assets/marketing/`. Keep the new `marketing/campaign/`, `marketing/CURRENT_CAMPAIGN.json`, `marketing/selection.json`, marketing language entry points and `assets/marketing/campaign/{en,uk}/`. Historical requirement registers whose evidence points to deleted drafts are replaced by `governance/campaign-requirements.csv`.

Root navigation, release/migration notes, current-campaign metadata, package descriptions, validators, workflow references and all seven guide entries must use the new paths. Full canonical skill sources, portable updater, manifests, installed-icon baseline, rights notices and historical suite release/migration records remain intact. Supporting scripts/tests may be adapted to the current campaign without retaining obsolete draft data.

The publishing executor records the exact removed paths and final remote proof in `governance/TASK_CLOSEOUT.json`. Until that proof is observed, local removal and prepared publication remain distinct statuses.
