# Portable studio payload

Use the manifest and hash format from `handoff-contract.md`. This file defines studio-specific contents. Reference studio records from the canonical Game Model by stable IDs following the [model format](model-format.md). The studio payload owns identity, source, export, and service facts. The Game Model owns dependent uses and effects. Keep one authoritative Game Model and consent registry, with game-specific camera and art decisions.

## Contents

- `studio/identity.json` records stable `studio_id`, `display_name`, legal name and status, public developer contacts and support and privacy URLs, brand revision, and payload identifiers. Use null and an issue ID for unknown legal or service fields.
- `studio/brand/` contains immutable master, actual source materials, final exports, tokens, fonts and licenses, approved variants, usage rules, original decisions, and change records. Verify redistribution rights separately. For restrictions, give a lawful restoration path and exact limits.
- `studio/services.json` records capability, target environment, account and configuration identity without secrets, owner, setup status, usage limits, cost and approval, and current evidence. Keep secrets in the approved store and record references and provisioning steps.
- `studio/setup/` records exact instructions, dependencies, checklist, and observed confirmation without private documents. `studio/usage-map.json` records actual game and store use, asset IDs, dimensions, and variants needed next.

## Consumer rules

1. Intake checks actual bytes, paths, hashes, and current revision alongside brand guidance.
2. Concepts adds the studio usage map and transfers the required lawful payload, retaining the actual studio name.
3. Preproduction defines applicable boot, splash, about, credits, legal, contact, and listing uses with exact source IDs.
4. Assets uses approved exports and sources. Review identity for a new compact or monochrome variant.
5. Build imports exact originals or approved derivatives and records runtime import and compression in the recipe.
6. QA compares actual screens and store fields to brand and legal identity and pending issues. Release uses the exact legal and public fields.
7. A studio update creates a revision and an impact map. Preserve existing source outputs and historical approvals, and migrate affected dependencies explicitly.
8. Resolve source and evidence IDs to portable package-relative paths with bytes and hashes, or an explicit remote restoration route. Flag unavailable historic materials. Retain actual proof independent of scratch paths.

Identify names, image and font bytes, legal and service status, and their sources. Keep credentials and private identity documents out of delivery artifacts.

## Operations and portable source

Include relevant operation IDs, capability witnesses, exact recipes and transformations, and lawful source and export bindings. Use the existing IDs for the five operational record types. Exact host transfers pin inputs, toolchain, allowed outputs, and return checks. Track installation and catalogue status separately from native evidence.

When redistribution is restricted, transfer the allowed output, verified restoration path, and limits. Preserve exact accepted masters. Invalidate only derivatives affected by changed semantic inputs.
