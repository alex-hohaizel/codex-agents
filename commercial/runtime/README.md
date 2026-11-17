# Agent Atelier for Mac — ready runtime candidate

Extract the archive into a permanent folder and double-click **Launch.command**.
It uses the included Node.js runtime and compiled interface. Do not run npm,
TypeScript or a developer build. Your Codex login and model access remain your
own. For Apple security warnings, first verify the delivery and package
signature. This candidate has not been notarized for public distribution.

The runtime is architecture-specific. macOS 13.5 or newer is required by the
included Node.js v24 binary. `arm64` is Apple Silicon; `x64` is Intel. Running
on an Apple Silicon Mac does not establish execution on an M1 or an Intel Mac.
See the artifact's actual acceptance record before buying for a target.

The default state is separate from the runtime under
`~/Library/Application Support/Codex Agent System/Agent Atelier`. Existing
Agent Atelier data and other projects are not automatically adopted.

Advanced controls from the extracted directory:

```sh
./Runtime.command verify
./Runtime.command start --no-open
./Runtime.command status
./Runtime.command doctor
./Runtime.command stop
```

For a self-contained test use `--data-dir /absolute/private/test-folder` and a
free `--port`. The app listens only on loopback. Keep launch URLs and private
owner credentials out of screenshots and support requests.

Before a runtime update, stop the app. An exact offline snapshot preserves all
state files apart from stale process metadata. It never rewrites a running store.
Restore into a **new** directory, leaving the original and the snapshot intact:

```sh
./Runtime.command snapshot --data-dir /absolute/current-data --output /absolute/new-snapshot
./Runtime.command restore --snapshot /absolute/new-snapshot --sha256 RECEIPT_SHA --output /absolute/new-restored-data
./Runtime.command start --data-dir /absolute/new-restored-data
```

Keep the previous runtime until the new runtime and state are verified. The
builder records SQLite schema support separately; a store newer than the
runtime is blocked. Use the application-level verified backup/restore for
normal live operation and the snapshot route for an explicitly stopped store.
Snapshots contain private local state and must remain on the owner's computer.
