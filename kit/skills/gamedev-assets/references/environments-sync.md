# Environments, delivery, and synchronization

Read the [maturity, competence, and authority index](v4/index.md) for current Game Model semantics. GA4-P1/D1/D2 supplement GA3/UA26 and earlier IDs. Complete concepts require C1 and production handoff requires T. Collect actual evidence at the appropriate gate. Preserve historical sources and approvals. R6 profile, scale, style, camera, and one-time kits belong to their selected concepts.

## Source and runtime boundaries

Build different delivery forms from one versioned suite source. Keep the game in its own repository with its own checkpoints. Verify chat history, browser session, local files, and game backend separately from skill installation.

## Host matrix

Use the following as a 2026-11-01 documentation snapshot. Verify the actual host, version, and available capabilities during setup.

| Host | Route described in the snapshot | Verify for actual use |
|---|---|---|
| Work web or mobile | Bundled plugin skills where install or save is available, and portable stage packages | Cloud filesystem, current tools, generation rights, and service authority |
| Work desktop | Actual standalone or plugin skills | Whether execution is cloud or local and actual local access |
| Codex desktop Local | Repository `.agents/skills` or a supported plugin | Open game repository, host dependencies and permissions, device access |
| Codex Worktree | Exact tracked snapshot in the intended checkout | Dependencies and branch, plus shared databases and store accounts outside the worktree |
| Codex Cloud | Committed task-checkout skills or available plugin and published environment dependencies | Local Mac, browser and signing boundaries, and independently authorized environment changes |
| Codex CLI | Repository skills or installed plugin, `$skill-name` or `/skills` where available | Current directory and root, version and actual CLI options |
| Codex IDE extension | Repository or user standalone skills in that snapshot | Current plugin support and actual UI |

## Supported delivery and duplicate resolution

The archived toolkit **4.3.0** kit comprised `install_codex.py`, a hash manifest, and nine skill folders, with audit, apply, verify, backups, rollback, and interrupted-update recovery. Its `UPDATE_CODEX_UA.md` describes exact commands. The project installation used `--project /absolute/project --project-skills in-place` and the exact `--skills-root /absolute/project/.agents/skills` or `.codex/skills` for a tracked repository. It preserved existing skill paths and host rules and excluded personal remote-skill repositories and nested managed sources. Use the actual candidate release's supported installer and documentation for current deployment. Track installation, actual discovery, and game environment readiness separately.

- Install project skills in `<project>/.agents/skills/<name>` using a stable source. Edit installed copies only for a specifically scoped suite development workflow.
- A user-wide install at `$HOME/.agents/skills` affects independent projects. Choose it only within current user authorization and confirm compatibility.
- Resolve duplicate names across plugin, repository, and user roots for the actual host. Keep one applicable active source for the selected ID and scope. Preserve unrelated skills and global configuration.
- Track package preparation separately from actual cloud import, save, and discovery. If the host cannot install it, deliver the valid package and exact blocker.
- For a personal skills checkout, use supported Skill Creator save, validation, and Git flow. Verify native Mac installation separately.

## Versions

Compare the toolkit, schema and protocol, package identity, and actual hashes. Toolkit **4.3.0** identifies the historical kit above. The separate game model **4.0.0**, handoff schema and suite protocol **1.0.0**, and runtime state **2.0.0** remain distinct. Match the actual runtime or handoff compatibility marker from the installed tool. For edited copies, compare source commits, accepted decisions, and manifest ancestry and record affected work.

Update the canonical source, run targeted validation and behavioral checks, package, use the authorized project updater, check synchronization, and inspect impact. Retain the accepted package for rollback. Reuse media unaffected by text-only changes.

## Host transfer

From Work to Codex, include the approved brief, current studio assets, design and config and content, source media, licenses and lineage, manifest and hashes, decisions and gaps, and exact next skill and host. From Codex to Work, include relevant review extracts and actual captures, asset requests and identity master references, without credentials or unrelated database contents.

For generation in another environment, record job or request ID, master hashes, selection status, fixed properties and permitted variation, size or duration and export, provider and license and cost, and required return files. Compare the actual return with the masters. Version and accept derivatives before dependent use.

## MCP, plugins, and CLI

Use an existing CLI when sufficient. Choose MCP only for an actual operation and verify host availability, authentication, and least privilege. Check browser login and MCP authorization independently. Exclude secrets from archives, logs and captures.

Check whether a cloud host can reach a required service. Document transport, host, network, and authorization prerequisites and the exact owner step for any missing approved connector. Bind only verified executables and services as dependencies.

## Official references

- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/plugins
- https://learn.chatgpt.com/docs/environments/modes
- https://learn.chatgpt.com/docs/extend/mcp?surface=cli
- https://learn.chatgpt.com/docs/enterprise/plugin-management

Check current marketplace permissions and actual feature availability for the account. Confirm administrator access if the selected route requires it.

Skill installation preserves game saves and registries. `atelier.py` ordinary commands require the actual current toolkit marker and runtime schema **2.0.0**. The prior 4.2 to 4.3 route was a separate reviewed workflow upgrade. Use the currently declared `WORKFLOW_UPGRADE_FROM` table and the [preview and apply procedure](orchestrator-workflow.md) for any supported change. Bind source and target hashes, actual authority, exact backup, journal receipt, and affected IDs. Installation does not trigger project migration. Unsupported formats are sources for a scoped reconstruction and decision. Reconcile suite hashes before following dependencies and preserve approved masters and authority.
