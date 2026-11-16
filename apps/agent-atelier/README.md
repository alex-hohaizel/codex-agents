# Agent Atelier — local Mac workbench

Agent Atelier provides a universal task entry and a source-backed portfolio of native Codex work. It pages active and archived thread metadata through the supported app-server, groups work by canonical project root and loads individual work groups on demand. It shows observed responses, accepted or declared goals with their provenance, installed versus planned agents and source-backed next actions. The local Codex project registry supplies registered projects even when they have no chats. The portfolio shows how much it has read from the registry and from active and archived history. Project work history opens on demand. Remote hosts and unavailable sources remain outside verified local coverage. Explicit binding is required before project control. It shows native sources/context/requirements/identity, prepares bounded tasks and runs them through the supported Codex app-server. Its multi-pane interface includes source/diff/outcome views, task/jobs, evidence, skill update plans and recovery. `?demo=1` is a separate fictional design preview; it performs no real commands.

The 33-core skill suite, optional orchestrator and this service have separate versions and installation facts. A binding does not migrate a product or grant every future job. Work audit/update/installation/control is deferred. Existing desktop chat adoption requires exact identity/cwd, an idle handoff and current task scope; the service does not fence independent desktop writers.

## Build and launch

Select the published source revision recorded for the version you need. Follow the current service migration to preserve the data directory and existing work. [Current release record](../../releases/current.json) · [Update and rollback](../../releases/migrations/repository-1.5.0.md)

Use the pinned lockfile and Node.js 24.22.2 or a verified compatible runtime. Run these commands from this directory.

```sh
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
```

On Mac, double-click `launcher/Agent Atelier.command` after building. The launcher opens its loopback workbench using a one-use 60-second owner link, reuses its own healthy instance and reports a conflicting port instead of starting a second writer. It does not enable login auto-start. `--no-open` starts without opening a browser; `--port NUMBER` and `--data-dir /absolute/path` select an explicit instance location.

```sh
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

A fresh browser must enter through the local launcher. Plain URLs do not grant owner access. The private `owner-credentials.json` and cookies remain local; the launcher/client verify an instance proof before sending a control credential to a local listener. A same-OS-user process able to read that private file remains within the local trust boundary.

Default service state is `~/Library/Application Support/Agent Atelier`, separate from repository sources and native product state. Preserve that directory and its actual backup/receipt records. Do not place credentials, databases or private exports inside this reusable repository. The actual Node-bound SQLite engine is reported by the running service; the system SQLite CLI can be a different version.

For development run the backend and Vite in separate terminals. Set an explicit `ATELIER_DEV_ORIGIN` matching the Vite origin when using its proxy; production uses one origin and serves `dist/client`.

## First useful task

1. Open the live workbench, choose your language and refresh the native Codex portfolio. Open a project to inspect its work groups, target, observed agents and next steps. Preview the exact directory and bind it before control. Existing direct-Codex work can appear through native history; there is no automatic Home scan.
2. Open actual sources, requirements/context and identity. Source-only, observed integration, independent review and owner acceptance are distinct. Unsupported schemas/capabilities retain explicit warnings rather than reset state.
3. Open the displayed next action to carry its full text into the task form, or use the universal task entry to enter your own objective. Edit the objective and acceptance before preparing the task. Review its routing proposal and available project agent; the actual orchestrator interprets context and can reuse a specialist, continue through a verified project agent, invoke the agent constructor for a genuine gap or coordinate system maintenance. A matching label alone does not verify an agent. Prepare a bounded task with filesystem scope and deadline. Review its exact capsule/source pins, obligations, allowed roots and current capability scope. Missing required access blocks dispatch or produces a concrete handoff.
4. Dispatch only the approved scope. Follow actual host/thread/turn receipts and outputs. Pause prevents new dependent work; interruption is `cancel_requested` until the host confirms a terminal outcome.
5. Review the actual result against the original task and accepted references. Owner review is not independent QA. A completed model turn does not establish a successful build, artifact delivery or production acceptance.

The default job profile denies sibling projects, native approval/state roots, credentials, private service data, unrelated temporary files and ambient external tools. Exactly selected verified skill snapshots are separate read grants. New tasks keep a private archive and a separate immutable execution copy outside the service control directory; only the selected task subtree is readable. Ownership, full membership and source/archive/execution hashes are rechecked before execution. Missing or changed copies require preparation again; old capsules retain their existing contract. Extra read grants currently require a service data directory without glob metacharacters; the default location is supported. Unsupported plugin/tool routes stay visible as requiring a capable host. Enabling public-web read is an explicit task choice; there is no deterministic filter guaranteeing that every outbound query is free of private text.

Shell scratch files must remain within the approved writable paths; use an output-local TMPDIR or a temp-free command. Ambient system temp is not an additional write grant. Read-only jobs retain no scratch write permission.

The local executor's default scopes prohibit ambient production/publication/spending and do not silently inherit every external plugin. Actual supported capability/permission policies are reported by the adapter. If the task needs another host/API/tool, preserve the requirement and use the exact supported bridge; do not downgrade the requested result or advertise an unavailable operation.

## Codex plugins and media

Open **Connections**, then **Check connections**. The catalog reads installed plugin and app metadata from a separate Codex connection. Select an app to see the tools it advertises, including which are read-only. A configured MCP server is a catalog entry until its capability is verified. These reads do not install, enable or sign in to a plugin.

For a public image or sound search, select Openverse, choose the medium and enter public search terms. The panel sends only those terms to Openverse and returns up to ten matching records with creator, license and links to the source where available. Verify the asset and license at the original source before use. Search responses stay in the current browser view and are not added to project history.

For an existing GitHub CLI login, select GitHub CLI and enter the exact repository as `owner/name` to read its metadata, including default branch and visibility. The route uses the authorized CLI access and is separate from the Codex plugin's own access.

Select **OpenAI Docs MCP** to search the official documentation. Open the returned source link to read the page.

Select **Codex Image** to generate an image with the existing ChatGPT login and supported Codex host. Enter an image brief and generate it, then preview or download the PNG. This uses included Codex limits. If Codex reports an uncertain outcome, check its generated images before retrying.

Use **Continue in Codex** for tools that need the native host. Paste the handoff into the intended project chat and select the actual plugin there. Check the exact operation, data, access and any charge before running it. A handoff leaves execution and the result pending in that host.

## Reading results and preserving context

Select a Markdown artifact to read its actual bounded contents in the workbench. The visible relative path distinguishes same-name reports. A declared matching digest and a freshly observed source-only digest are different evidence. Missing, changed or inaccessible sources clear stale results and show recovery; normal refresh preserves the selected artifact, keyboard focus and viewport. Original downloads, JSON source inspection and native PDFs retain their own views.

Ordinary and legacy tasks keep `memory_mode: inherit`. A deliberately cold comparison can prepare a fresh service-owned task with `memory_mode: disabled` through the advanced API. The adapter disables use/generation from first start, requires native acknowledgement before the turn and denies exact memory directories for that task. It never changes global preferences. Adopted user chats reject this mode before resume. The native schema has no independent mode getter, so acknowledgement alone does not prove cold execution: inspect actual source reads, output and the independent case result. This is not a general RAG service or automatic cross-chat memory.

## Governing instructions and exact read scope

Preparation pins the governing instruction candidate set, including absent files, override precedence, root markers and native loading settings. Existing sources must be bounded regular files. Dispatch checks current pins, the native host's actual loaded sources and the pins again before the model turn. Changed instructions or a legacy unpinned task require fresh preparation; history and native products remain intact.

For instruction paths containing glob metacharacters, per-task service-owned aliases serialize read permission for those exact original files. The adapter verifies each alias target/hash and never grants its parent directory. This preserves normal instruction loading while retaining sibling/credential/private-state denials. Native instruction budgets are checked rather than silently dropping required sources.

Input-cache cleanup also unlinks reviewed instruction aliases without following or deleting governing targets. Unknown/replaced pointers reject. The local route verifies native OpenAI metadata and existing ChatGPT authentication before a turn; custom provider/base-URL configurations need a separately reviewed route.

## Skills and optional agent

Search competence/source metadata, audit the exact canonical candidate, inspect the native updater plan/diff, and apply only the ready reviewed plan. Global skill mutations have one writer and use actual journals. Verify installation separately from discovery/use; preserve unrelated records and unknown customizations. Rollback requires the actual unchanged-target journal.

`optional-skills/atelier-orchestrator`1.2.0 is a universal conversational entry and panel entry, separately from the 33-core updater. It preserves direct specialist calls and an existing project owner; construction of an agent and execution of its product retain distinct scope and authority. The panel provides exact preview/apply/verify/rollback for the two declared optional sources. Known installed predecessors are hash-bound; unknown local changes, icon/policy drift and ambiguous sources block overwrite. Every staging copy is journal-owned before creation. Actual host discovery is refreshed separately after installation. Its loopback client supports status, context and correlated task commands; mutating calls require a persisted command identity. It can also coordinate approved work through actual native skills when the service is unavailable, without inventing runtime access.

Native history uses a separate public read-only transport against the native index; its RPC allowlist prohibits model execution, resume and mutation. The model executor retains its isolated index. Empty paginated history with existing metadata is incomplete coverage. A native chat can only be adopted when the executor can restore its persisted context; otherwise continue that chat in the native host or prepare a fresh bounded project task from reviewed sources. Portfolio read access alone does not grant safe continuation.

## Native controller operations

The project workbench can review and apply the existing Foundry controller operations through a fixed catalog. It shows the exact source, current state/revision, input record and approval subject before confirmation. The native controller runs from an exact staged copy of its reviewed source closure, under its unchanged validation and exclusive state lock. Approval derives its subject from the real registered blueprint; it cannot fabricate a missing blueprint or execution grant. The adapter launches no model, provider, deployment or product runtime.

Unknown native outcomes block dependent writers. Reconciliation first checks the previous process lease; a live or uncertain writer keeps the barrier. Confirmed reconciliation revokes a delayed invocation under that same lease, then observes current state. It never automatically repeats an operation or certifies the original result. Private operation copies and receipts follow their independent reviewed retention policies.

## Backup, restore and update

Use the service recovery screen to create a service STORE-JSON metadata backup and inspect restore preview/digest. This export contains records, not file payloads, selected-skill archives or execution copies. For a complete local update backup, also preserve the idle service data directory and separately owned execution-input namespace as private filesystem copies; never publish them. Restore requires an idle/reconciled boundary, current preview, explicit scope and no revival of revoked dispatch authority. It preserves newer durable receipts; it does not restore product files/DB or external effects. Test restore on an isolated instance before relying on a backup.

To update: stop new dispatch, reconcile running/unknown jobs, create/verify backup, select an exact compatible source/build, install its lockfile and build, then restart and run doctor. Unknown newer schemas reject. Code rollback requires compatible service schema and task-policy/input contracts, or a separately reviewed restore. In particular,0.3.0 does not enforce the new memory mode and execution-transport guarantees: do not resume new0.3.1 tasks on it merely because DB schema1 is unchanged. Immediate failed-start rollback requires proof of no new jobs or owner changes. Later rollback must reconcile effects, preserve new receipts and revoke or reprepare affected capsules before selecting the old runtime. See [the suite migration](../../releases/migrations/6.1.0.md) for native project adoption and toolkit rollback.

## Retention, forgetting and diagnostic export

Settings let the owner choose service-history/event/input-cache/backup periods or retain them. Cleanup is manual: inspect exact counts and digest, select any explicit project/job history to forget, then confirm. Active/unknown work and paused project tasks block cleanup. Service indexes, associated records, task caches and matching receipts/events are removed or redacted; command IDs/digests remain to prevent replay. Native project files and provider-side copies are untouched. Shared raw logs and backups follow their separate policy; the newest two backups remain. This is logical service cleanup, not secure physical erasure.

Forgotten record/root tombstones filter restores. Pending file cleanup stores reviewed target hashes; a replacement at the same path requires a fresh preview. Pruned task inputs revoke dispatch/continue until a new preparation. Diagnostic export first shows only redacted aggregates for review, then writes/downloads that exact content locally; it sends nothing externally.

The personal Mac update to 0.5.0 was verified on source `c86ce907544410afcb8bbd19181f1640446aefb7`. The service reopened through the updated launcher with the same SQLite file, four project bindings, owner settings and existing task/job history. The filesystem backup was checked before replacement. The earlier 0.3.1 observation remains available with its own source and history-coverage limits. [0.5.0 release and verification](../../releases/repository-1.4.0-rc.5.md) · [0.3.1 checkpoint](../../docs/evolution/2026-11-10/STATUS.json)

## Verification and maintenance

```sh
npm run check
npm test
npm run build
```

Server tests use isolated fixtures. Real loopback, model and browser checks require the corresponding local runtime permissions. The 0.5.0 record covers the next-action form, a persisted prepared task with zero dispatches, real OpenAI Docs results, and a downloaded Codex-generated PNG. Find earlier checks under their original release scope. [0.5.0 verification](../../releases/repository-1.4.0-rc.5.md) · [Historical 6.0 verification](../../governance/RELEASE_6_VERIFICATION.json)

`shared/API.md` describes commands, receipts and boundaries. Server modules separate native project reads, context compilation, store/command recovery, Codex transport and supported skill updates. Client components separate the stable workbench, adaptive views, dialogs, API state and localization. Formatting, pinned dependencies and focused tests support ordinary human maintenance.
