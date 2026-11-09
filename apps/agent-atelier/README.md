# Agent Atelier 0.1.0 — local Mac workbench

Agent Atelier binds explicitly selected product roots, shows their native sources/context/requirements/identity, prepares bounded tasks and runs them through the supported Codex app-server. Its multi-pane interface includes source/diff/outcome views, task/jobs, evidence, skill update plans and recovery. `?demo=1` is a separate fictional design preview; it performs no real commands.

The 33-core skill suite, optional orchestrator and this service have separate versions and installation facts. A binding does not migrate a product or grant every future job. Work audit/update/installation/control is deferred. Existing desktop chat adoption requires exact identity/cwd, an idle handoff and current task scope; the service does not fence independent desktop writers.

## Build and launch

Use the pinned lockfile and Node.js24.22.2 or a verified compatible runtime. From this directory:

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

1. Open the live workbench, choose your language and preview the exact project directory. Inspect its detected schema/source/revision/warnings, then bind it. There is no automatic Home scan.
2. Open actual sources, requirements/context and identity. Source-only, observed integration, independent review and owner acceptance are distinct. Unsupported schemas/capabilities retain explicit warnings rather than reset state.
3. Prepare a bounded task with objective, acceptance, filesystem scope and deadline. Review its exact capsule/source pins, obligations, allowed roots and current capability scope. Missing required access blocks dispatch or produces a concrete handoff.
4. Dispatch only the approved scope. Follow actual host/thread/turn receipts and outputs. Pause prevents new dependent work; interruption is `cancel_requested` until the host confirms a terminal outcome.
5. Review the actual result against the original task and accepted references. Owner review is not independent QA. A completed model turn does not establish a successful build, artifact delivery or production acceptance.

The default job profile denies sibling projects, native approval/state roots, credentials, private service data, unrelated temporary files and ambient external tools. Exactly selected verified skill snapshots are separate read grants. Extra read grants currently require a service data directory without glob metacharacters; the default location is supported. Unsupported plugin/tool routes stay visible as requiring a capable host. Enabling public-web read is an explicit task choice; there is no deterministic filter guaranteeing that every outbound query is free of private text.

The local executor's default scopes prohibit ambient production/publication/spending and do not silently inherit every external plugin. Actual supported capability/permission policies are reported by the adapter. If the task needs another host/API/tool, preserve the requirement and use the exact supported bridge; do not downgrade the requested result or advertise an unavailable operation.

## Skills and optional agent

Search competence/source metadata, audit the exact canonical candidate, inspect the native updater plan/diff, and apply only the ready reviewed plan. Global skill mutations have one writer and use actual journals. Verify installation separately from discovery/use; preserve unrelated records and unknown customizations. Rollback requires the actual unchanged-target journal.

`optional-skills/atelier-orchestrator` is installed through the supported skill manager at an exact release revision, separately from the 33-core updater. Its loopback client supports status, context and correlated task commands; mutating calls require a persisted command identity. It can also coordinate approved work through actual native skills when the service is unavailable, without inventing runtime access.

## Backup, restore and update

Use the service recovery screen to create an exact service-owned backup and inspect restore preview/digest. Restore requires an idle/reconciled boundary, current preview, explicit scope and no revival of revoked dispatch authority. It preserves newer durable receipts; it does not restore product files/DB or external effects. Test restore on an isolated instance before relying on a backup.

To update: stop new dispatch, reconcile running/unknown jobs, create/verify backup, select an exact compatible source/build, install its lockfile and build, then restart and run doctor. Unknown newer schemas reject. Code rollback only works with a compatible service schema or a separately reviewed restore. See [the suite migration](../../releases/migrations/6.0.0.md) for native project adoption and toolkit rollback.

## Retention, forgetting and diagnostic export

Settings let the owner choose service-history/event/input-cache/backup periods or retain them. Cleanup is manual: inspect exact counts and digest, select any explicit project/job history to forget, then confirm. Active/unknown work and paused project tasks block cleanup. Service indexes, associated records, task caches and matching receipts/events are removed or redacted; command IDs/digests remain to prevent replay. Native project files and provider-side copies are untouched. Shared raw logs and backups follow their separate policy; the newest two backups remain. This is logical service cleanup, not secure physical erasure.

Forgotten record/root tombstones filter restores. Pending file cleanup stores reviewed target hashes; a replacement at the same path requires a fresh preview. Pruned task inputs revoke dispatch/continue until a new preparation. Diagnostic export first shows only redacted aggregates for review, then writes/downloads that exact content locally; it sends nothing externally.

## Verification and maintenance

```sh
npm run check
npm test
npm run build
```

Server tests use isolated fixtures; real loopback/model/browser checks require the corresponding local runtime permissions. Their observed scopes and final release status are in `governance/RELEASE_6_VERIFICATION.json` at repository root. Private execution IDs, inventories and logs are kept outside distributable sources. No universal creative, accessibility or device certification is claimed.

`shared/API.md` describes commands, receipts and boundaries. Server modules separate native project reads, context compilation, store/command recovery, Codex transport and supported skill updates. Client components separate the stable workbench, adaptive views, dialogs, API state and localization. Formatting, pinned dependencies and focused tests support ordinary human maintenance.
