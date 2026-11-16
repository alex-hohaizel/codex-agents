# Local launcher and operator contract

Use macOS, Node.js in the supported range `>=24.22.2 <27`, a supported Codex CLI, and the owner's existing Codex sign-in. Use the current release record to select the source revision and migration for the installed version. WORK remains deferred. [Current release record](../../../releases/current.json) · [Current update and rollback](../../../releases/migrations/repository-1.5.0.md)

From `apps/agent-atelier` inside the canonical checkout:

```sh
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

On macOS the packaged `launcher/Agent Atelier.command` runs the same start route; its Node resolver may use an already installed fnm Node 24. It does not install a runtime. `start` opens the browser; `--no-open` starts quietly. `--port 4317` and `--data-dir /absolute/selected/directory` select an isolated instance. Repeat the same data-directory selection for status, doctor and stop. A repeated start reopens the verified existing instance and does not launch another writer.

The production server serves the built `dist/client` and `/api/v1` on `http://127.0.0.1:4317`. It accepts loopback hosts only. Development uses the Vite proxy and `ATELIER_DEV_ORIGIN` configured in the existing package scripts. Do not expose the port through a public tunnel.

The default private data directory is `~/Library/Application Support/Agent Atelier`. It contains the service's SQLite records, durable command receipts/events, immutable skill input snapshots, supported Codex adapter state/logs, update plans/journals and service backups. Files are private to the current OS owner. It does not replace a project's native registries or independently owned Codex storage. Protect this directory and its backups as private project data.

`runtime.json` is a public-to-the-owner instance locator and contains no bearer credential. `owner-credentials.json` is a separate 0600 file. The launcher verifies the listener's HMAC proof before sending its control key. Browser opening uses a 60-second one-use HMAC token in a URL fragment; the client removes that fragment before requesting private data. Plain static page loading or unauthenticated `/api/v1/session` never grants control. Reopen the launcher if a launch link expired or the service restarted. This is a personal Mac application; it does not claim isolation from a malicious process running as the same OS owner.

Bind a project explicitly: preview its exact existing root, review the native adapter/source revision, then bind it. Changing the service's adaptive view profile changes presentation only. It does not migrate the product. The source and artifact viewer is read-only. Task preparation records the original objective, acceptance, all applicable must requirements and dependency closure, identity/decisions, pinned source hashes, selected skill snapshots, approved paths, deadline and stop/recovery rules. Dispatch rechecks the exact authority and source revision. Skill constructor routes prepare a planning-only M1 proposal; target installation is a distinct reviewed action.

The service uses the public Codex app-server protocol, actual `skills/list`, thread reads/start/resume, correlated turns, live questions, interrupt and reconciliation. The catalog distinguishes the core 33, optional sources, actual host-discovered skills, and role profile source metadata. A role file's presence does not prove a runtime role invocation. Native suite updates use the existing fixed-argument suite updater and apply only its exact reviewed ready plan. Vendor/plugin caches are read-only.

Default tasks deny ambient MCP/apps, shell network and public web search. An explicit `capability_scope.public_web_read` can request the supported public search route; private project data must never be included in queries. Other external effects or required unavailable tools block dispatch and require a capable reviewed host route. A permission request cannot enlarge the prepared task's scope through a generic accept button.

Review the observed scope for the exact service release. The 0.5.0 checks cover preparation from the displayed next action, OpenAI Docs search and a downloaded native Codex image. Regular job dispatch still depends on the selected project's authority, source and filesystem checks. Capability failures and `operation_tested: false` remain visible until the exact host operation is verified. [0.5.0 verification](../../../releases/repository-1.4.0-rc.5.md)

One active service job owns a project's write scope. A timeout, disconnect or restart without a terminal receipt becomes `outcome_unknown`; reconciliation reads the actual thread/turn before another attempt. Interrupt is a request until the host confirms a terminal interruption. Existing chats require exact ID/cwd preview, idle state and explicit handoff. A service lease does not fence an independent Codex Desktop client: do not continue the same chat concurrently in both interfaces. Owner review and independent QA/product acceptance are separate records.

Service backup/restore covers the service's own records, not native product files or all Codex chats. Restore requires preview, exact backup confirmation and idle jobs; old task/handoff authority is invalidated and newer command receipts are retained. A separate file-system backup is needed for native projects. Service retention/forget operations expose their own exact preview and do not delete product files or independently stored native chats.
