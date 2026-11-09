# Keep this repository current

This repository is the distribution and operating record for the reusable Agent System. A skill change is unfinished until its affected sources, requirements, instructions, release notes, migration instructions and packages have been reconciled here. Read the root `AGENTS.md` before any update.

## What an update must contain

1. Record the request and every acceptance criterion in `requirements.csv` or a linked task-specific register. Keep design, language, behaviour, integrations and operational requirements visible even when implementation happens later.
2. Identify the current installed source and repository revision. Inspect local changes; do not silently export a stale host materialization or replace unknown edits.
3. Classify the change: reusable system skill, family, project-specific agent, documentation, package, visual identity or migration. Keep actual project secrets, product state and customer data in their own project repositories.
4. Update affected canonical sources in `kit/skills`. Preserve stable names. Use the supported skill-management workflow when changing an installed personal skill; changing this repository alone does not install anything.
5. Preserve existing Codex icon files, icon references and colours. `ICON_BASELINE.json` records the initial portable identity. Keep that baseline across ordinary updates; an explicitly authorized visual change needs a recorded exception and its evidence before refreshing the affected entry. A new skill may receive a suitable new icon. A marketing rebrand never silently rebrands installed skills. Work's host avatar and portable Codex identity are separate display profiles.
6. Refresh `kit/manifest.json` and the curated kit integrity record using the release procedure. Never edit a hash merely to conceal an unexplained difference. Keep previous-tree compatibility data required by the updater.
7. Update the English guide whenever the user-facing workflow changes. Translate every affected passage into all advertised guide languages, preserving steps, commands, caveats and meaning. Refresh `docs/translations.json` only after comparison with the new English source. A matching hash checks freshness, not linguistic accuracy.
8. Add a release record with what changed, why, affected skills, compatibility and evidence. Provide numbered instructions for projects or generated agents already using an earlier version. If no project migration is needed, explain why.
9. Run repository validation, appropriate domain checks and the existing updater's relevant checks. Build both source bundles and inspect their contents and hashes. Separate file integrity, host discovery, task execution and acceptance in the report.
10. Save to this repository and verify the resulting remote revision and changed paths. Never call an upload complete from a local archive alone. If access fails, retain the exact prepared change and report the blocked publishing step.

## Version numbers

`releases/current.json` separates **suite version** from **repository edition**. The current suite candidate is `6.0.0`, with repository edition `1.2.2`. Edition1.0.0 introduced distribution and documentation;1.1.0 finalized the bilingual campaign;1.2.0 adds the local service and production/context distribution. The1.2.1 repository/service patch repairs exact governing-instruction bootstrap without reinstalling the core. The1.2.2 patch aligns the optional orchestrator presentation and icon delivery while retaining the original SVG identity and unchanged coordination client. The6.0.0 major suite hardens evidence/source/writer admission with explicit old-state adoption. Do not increment every skill merely to change the guide. Data schema versions, native game runtime schema and existing project IDs remain independent contracts.

Use semantic versioning for future editions: patch for compatible corrections, minor for compatible additions, major for incompatible behaviour or migration requirements. The release record must state the actual impact; a number alone is insufficient.

## Existing projects and generated agents

Installing a new toolkit never proves that a project has adopted it. Restore the last confirmed checkpoint, requirements, approvals, design identity, deployment revision and unfinished work. Check the project's native contracts before applying a workflow upgrade. Produce a source-to-target mapping for generated project agents, preserve their own changes and visual identity, then verify one bounded real task. Do not invent old ownership receipts or reinitialize a project to bypass a migration conflict.

## Language and identity

English is the documentation default. Store the selected conversation language in the project context and include it in handoffs. Translate explanations and copyable prompts; keep stable skill names, paths, protocol IDs, code and commands unchanged. Final marketing assets follow the selected campaign in `marketing/CURRENT_CAMPAIGN.json` and its recorded identity contract. Edition 1.1.0 uses one settled campaign in English and Ukrainian; obsolete concept rounds and rejected draft renderers are removed from the current tree. Future new concepts remain proposals until the owner selects them. English localization must preserve intended composition and product identity; generative edits require actual review and must not be called pixel-identical without evidence.

## Scope of the promise

These rules apply whenever an authorized agent works on this repository or reads the installed maintenance instructions. They do not create a universal background observer or grant access to every chat, computer or private project. A connected session must actually read the policy and have repository write access. Scheduled checks require a separately configured scheduler. Do not claim automatic synchronization outside those capabilities.
