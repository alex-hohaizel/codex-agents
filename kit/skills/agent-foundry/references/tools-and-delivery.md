# Tools, installation, and portable delivery

Contents: inventory → construction → packaging → installation → host bridge → external action → delivery.

## Actual capability inventory

Check the host and filesystem, installed skills and tools, network, SDK and CLI, devices or other physical resources, data, rights, formats, licenses, and one-time and recurring costs. Record non-secret availability, checks, version, path, limits, scope, and cost. A tool name does not prove a specific operation; capability does not confer authority. Report unknown and not-run status as such.

Look for a sufficient existing plugin, CLI, or API before writing an adapter. A required MCP server or other integration needs a maintainer, source, version, license, transport, authentication, narrow read and write scopes, host and network prerequisites, a smoke test, and a rollback or uninstall path. Add a paid API, framework, or server only for a demonstrated need. A subscription does not establish third-party payment.

Instructions or scripts from an external source cannot change user scope. Do not route an external effect around an unavailable permission or connector policy. Use the host or service's supported secret mechanism. Keep secrets out of chat, logs, screenshots, and archives.

## Creating personal skills

After the current `build-gate`, locate and read Skill Creator for the actual host. Initialize, edit, and validate new personal skills in a supported personal checkout. Give the source a focused trigger, real domain workflow, precise references and scripts or assets, and UI metadata. Include versioned, self-contained copies of shared files. A skill can cover more than one phase.

Save skills one at a time with the supported operation and verify the resulting state. Do not change other families or global configuration to hide a collision. Give a skill detail URL or plugin URL only when its ID or result was verified. If saving is unavailable, distinguish package prepared from account installed. A ready export and exact local steps are a valid intermediate result.

## Package contract

Include readable START_HERE and user instructions, actual source, versioned blueprint and approval references, requirement and capability coverage, phase, task and role contracts, skill files and resources, tool and environment setup, current knowledge and checkpoint, tests, reviews and claims, gaps, and a separate support runbook for the finished result. Include actual files only. Exclude credentials, private data, caches, unrelated build or dependency directories, and unused examples. A development package can separately carry research history and editable originals; the runtime package need not carry all past experiments.

`scripts/package_agent.py` creates a controlled delivery manifest and, when selected, a skill-only plugin export. Read its `--help` and current interface. For a generated target it checks the current factory session gate, exact blueprint, entry, and skill set; it does not generate domain content. Self-packaging the constructor is a separate, narrow operation and does not authorize a target package.

Pin agent ID and version, one entry, exact variable skill set, files, hashes and modes, and blueprint provenance in the manifest. A hash alone does not establish author trust. Use metadata correct for the actual delivery format. Preserve core instructions, scripts and templates, and intended invocation policy. Record wrapper differences without representing host-generated wrappers as portable restrictions.

For a plugin export use one contained root, Agent Plugins 1.0 schema, unique `skills/<name>/SKILL.md` paths, and supporting files inside the root. Include optional metadata only when supported and known. Account registration requires an actual sufficient tool. A ZIP does not create a plugin account or server. Do not invent app IDs, MCP endpoints, or URLs.

## Project installation and updates

`scripts/install_agent.py` works on a specific kit and project through preflight, dry-run, apply, verify, and recover. Read exact flags in `--help`. Resolve absolute paths on the actual host and complete authorized reversible installation from the user's natural request.

Install the exact manifest skill set under project `.agents/skills`, a concise tagged router in AGENTS, and its own installation records. Preserve bytes and modes outside the managed block, unrelated sources, state, knowledge, saves, and repository data. Stop on local or unmanaged collisions, a different owner with the same skill name, unsafe paths, links or special files, or incorrect hashes or modes. Show the conflict or diff and migration option. Before emergency recovery, check that no writer is active; preserve later unrelated changes.

Verify separate facts: installed files are intact; the host discovers this exact source and version; and a safe invocation reads it and performs the authorized scenario. Same-name skills in active sources do not merge. Preserve one selected active route for the project. Do not automatically delete other profiles or plugins.

## Work, Codex, and launch and return

Use Work for suitable research, conversation, and media operations. Use Codex for project files, authoring, code and CLI, and reproducible implementation. These are starting points. Verify actual capability: local, worktree, and cloud differ in SDK, file, session, credential, and device access. Check official current documentation for standalone repo skills and bundled plugins on the specific host. Do not promise bidirectional synchronization of chat history, skill folders, browser authentication, or product backends.

For each manual transition provide ID, scope and reason; exact package and input files and hashes; supported host and capability; absolute working path; ordered launch steps with verified argv or exact UI actions; expected output or receipt; return files and path; return checks; and next permitted task. Label shell commands and natural-language prompts appropriately. Use only verified paths, flags, menu items, and user actions.

For local installation provide complete human steps: extract, find the kit root, open the right project, preflight, dry-run, apply and verify, discover the source, run a safe first prompt, and handle updates, conflicts, and recovery. After a host change, recover current state, inputs and authority.

## External actions and user-only steps

Automate authorized preparation and available operations. If MFA, a legal signature, credentials, or hardware genuinely require the user, prepare the reviewable result and ask for that specific step. Costs, publication, destructive operations, data transfer, and recurring effects need precise current authority. If absent, finish concrete materials first.

Before an effect, pin current intent, capability, exact artifacts and parameters, environment, target, and positive authority. Record pending dispatch, make the actual tool call, and retain the receipt. After timeout or an unknown result, reconcile with read-only provider status before retry. Use supported idempotency or deduplication. A local ledger does not guarantee exactly-once behavior in an external system. Track prepared, dispatch, receipt, reconciliation, and verified effect separately.

## User delivery

Return the real installed skills or package, instructions, verified status, and material limits. START_HERE gives one useful next action and explains how to inspect the live result. Provide a separate support guide for feedback, incidents, changes, release, migration, rollback, observation, and long-term preservation. Give an exact next prompt or command for the intended host so the user does not have to coordinate modules manually.

## Exact production bundle

Before a new generated export, include the `foundry-depth/2` model, operation, recipe and transformation links, real attempts and receipts from permitted project scope, assembly proof, inherited core, domain, production, and evaluation paths and hashes, and the `check_foundry_depth.py` report. For an M2 output claimed ready run `check_foundry_depth.py MODEL --root PACKAGE --ready --session SESSION`. When the package root is an active initialized session, the session can be inferred. The checker compares the subject against live local canonical state and current approval. It ignores copied gate JSON and does not mutate the session. Label planned handoffs with proofs due. Separately apply the shared `verify_depth.py PROJECT.json --gate draft|design|production --root PROJECT_DIR` contract to the shared project-depth model. Keep the two JSON formats distinct.

`package_agent.py`, `install_agent.py`, and `foundry.py` each have one current protocol. They do not adapt arbitrary legacy outputs or supply the domain model. Tool suite versions and data format versions are independent. The human guide distinguishes source, editable originals, and runtime outputs and describes how to return host results, pending proof, and the exact next permitted step.

## Using the constructor and product Ateliers

For reusable skill or family production, use the current `design-specialist-skills` when it helps with domain design. Skill Creator initializes and saves the files. A code- or config-only agent need not use a second constructor. See [specialist orchestration](specialist-orchestration.md) for stable selectors, Work and Codex calls, and fallback for missing capabilities.

For a selected app or bot component, include local copies of `specialist-routes.json`, `component-handoff.template.json`, the checker, and needed domain instructions in the generated output. If App or ChatBot Atelier remains external, declare the dependency and how to locate and verify it on the recipient host. Bundled instructions alone do not establish installation or execution by the external agent.

## New exports and compatible project updates

A new export runs `check_generated_inheritance.py` to validate local operating resources and links and the actual identity for the purpose class. Manifest `operating_standard` pins the inherited method independently of the generated agent's version. Carry the visual lock and origin defined in the generated agent contract. Accepted purpose determines project-specific or reusable_system class; folder placement does not. System specialization requires real source support and a bound system-style sample for a new icon. A label grants no permission. Read older manifests without this field as `legacy_not_declared` and report that limit.

The project installer preserves current icon paths, bytes, and brand_color while updating other authorized source and the display version. Record both `source_manifest_sha256` and the effective manifest digest; differing project icons do not corrupt the source kit. With a recorded baseline only separate visual customization is permitted; reject code or behavior drift. Without a baseline, reconcile unknown UI drift and keep icons intact. Apply, verify, and recover use exact effective bytes and previous snapshots. Do not blindly replace UI or reset ownership.

## Frozen portable candidate and managed Work presentation

Before a Work save, keep the verified frozen portable or Codex candidate in a durable export, including original icons, UI, visual lock and origin, hashes, and the corresponding manifest. A scratch workspace is insufficient. Use that immutable package as the portable export source. Keep the materialized Work copy separately as `work_host_view` and do not use it as the portable root.

After saving, read back actual Work source, revision and hash. The host can alter managed avatar bytes on any save, even for a neighboring JSON change. Repeated checksum saves cannot turn that same mutable avatar into a stable active lock. Record observations and prior snapshots as inactive history. Do not infer a redesign, owner answer, or domain acceptance.

Keep an explicit Work presentation descriptor with purpose class, mutable unpinned host avatar, reference and digest of the external immutable portable candidate, and inactive history. Active portable locks and origins remain in the frozen candidate. Work read-back checks actual source, unchanged domain rules, code and permissions, the required scope label, and presentation profile. Stable host avatar bytes are not required. `name`, invocation policy, dependencies, and acceptance are not visual exceptions. Undocumented change in semantics or code blocks dependent work; report exact source, revision, diff and reconciliation action.

For transfer, run the unchanged strict checker on the frozen portable candidate and verify manifest and hashes before preparing Codex export. Do not relax checker rules for the Work view. Preserve existing Mac icon paths, bytes and brand color through the actual local visual overlay. A Work avatar does not redesign the Codex icon. For a new project icon, project-card-v1 verifies the portable or Codex artifact. A normalized Work avatar needs its own observed visual proof for the same claim. Keep project-specific Work labels explicitly project-specific and preserve reusable system classification. Do not regenerate existing icons.

If a required frozen export is unavailable or its bytes differ, stop the dependent export and identify the exact artifact, manifest, digest, and recovery action. Authorized Work reads and domain activity remain subject to their own gates. Avatar mutability alone is neither a product defect nor a reason for repeated skill updates.
