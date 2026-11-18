# Ready-to-run Agent Atelier for Windows, macOS and Linux

The buyer artifact includes the exact built interface, the current server and
its canonical runtime resources, and the official pinned runtimes. Ready desktop assets do not
require npm, TypeScript, developer dependencies, Homebrew or separate Node/Python
installation. The advanced skills-only source package keeps its own host
requirements. The server listens on loopback and uses the buyer's own Codex
account only when an authorized operation connects it.

The standalone runtime carries `LICENSE.txt`, `THIRD_PARTY_NOTICES.txt`, the
complete canonical `commercial/legal/` terms and notices, `commercial/offer.json`,
`RIGHTS.md` and its linked licensing guide. Node and every compiled production
dependency retain their complete upstream notices under `notices/`.

## Choose the artifact

Use the ready Universal or matching-platform asset attached to the exact Release. The Universal package carries Windows x64/ARM64, macOS x64/ARM64 and Linux x64/ARM64. `START_HERE.html` explains the download and `Start.cmd`, `Start.command` or `Start.sh` opens the local installer. For the workbench, open `Start-Workbench.cmd` on Windows, `Start-Workbench.command` on macOS, or `Start-Workbench.sh` on Linux. Match the release's supported OS minimums, architecture and native receipts before treating your target as tested.

The technical distribution does not claim product-level Authenticode, Developer ID signing or notarization from a vendor runtime signature. Actual native execution, browser acceptance and completed model work remain separate receipts. The original Mac standalone packaging route is retained below:

| Legacy standalone target | Runtime | Declared boundary |
| --- | --- | --- |
| Apple Silicon | `Agent-Atelier-<service-version>-macOS-arm64.zip` | macOS 13.5 or newer; match the exact artifact's execution receipt. |
| Intel | `Agent-Atelier-<service-version>-macOS-x64.zip` | Same minimum; Intel execution requires its own receipt. |
| Windows / Linux | Ready Universal or matching-platform asset | Use the native launcher; the legacy Mac ZIP does not contain these targets. |

The official Node v24 platform reference sets the minimum macOS to 13.5.
An upstream-supported minimum is different from an actual OS-version or device
check of this product. The included binary is unchanged; Node's own embedded
Developer ID signature is independent of product signing and notarization.

The workbench distribution remains an **unsigned and unnotarized RC** until
the owner supplies a valid product signing identity and completes an approved
notarization workflow. The builder never relabels Node's signature as the
product's signature. Follow the commercial artifact delivery and trust check
before opening an RC. A matching checksum by itself is byte consistency.

## Start, inspect, and stop

For a ready Universal package, the platform's `Start` launcher also exposes the same workbench CLI by adding `--workbench`, for example:

| Windows | macOS | Linux |
| --- | --- | --- |
| `.\Start.cmd --workbench verify` | `./Start.command --workbench verify` | `./Start.sh --workbench verify` |
| `.\Start.cmd --workbench start` | `./Start.command --workbench start` | `./Start.sh --workbench start` |
| `.\Start.cmd --workbench status` | `./Start.command --workbench status` | `./Start.sh --workbench status` |
| `.\Start.cmd --workbench doctor` | `./Start.command --workbench doctor` | `./Start.sh --workbench doctor` |
| `.\Start.cmd --workbench stop` | `./Start.command --workbench stop` | `./Start.sh --workbench stop` |

Its runtime directories are private to this product. It does not silently adopt an earlier workbench database. Default product data is `%LOCALAPPDATA%\Codex Agent System\Agent Atelier` on Windows, `~/Library/Application Support/Codex Agent System/Agent Atelier` on macOS, and `${XDG_DATA_HOME:-~/.local/share}/codex-agent-system/agent-atelier` on Linux. Use an explicit reviewed `--data-dir` for another state. Keep the installer journals distinct from workbench data.

The following `Runtime.command` examples remain the Mac standalone route; for Universal use the appropriate `Start` launcher followed by `--workbench` and the same verb/arguments.


Extract into a permanent folder and open `Launch.command`. The wrapper verifies
its entire runtime inventory, target architecture, and Node version before it
starts the unchanged app launcher. Use `Stop.command` to stop that instance.
All mutations and ownership checks continue through the existing app mechanisms.

The runtime uses separate default data under
`~/Library/Application Support/Codex Agent System/Agent Atelier`. It does not
adopt the previous Mac workbench data automatically. To use another reviewed
state folder, pass `--data-dir` explicitly. A running instance or unknown owner
at the requested port blocks a second writer.

```sh
./Runtime.command verify
./Runtime.command start --data-dir '/absolute/private/workbench state' --port 4317 --no-open
./Runtime.command status --data-dir '/absolute/private/workbench state' --port 4317
./Runtime.command doctor --data-dir '/absolute/private/workbench state' --port 4317
./Runtime.command stop --data-dir '/absolute/private/workbench state' --port 4317
```

A healthy HTTP endpoint establishes local runtime readiness. Fresh skill/role
discovery, model authentication and a completed native task have separate checks.
Do not share launch fragments, owner credentials, local databases, or account
logs in public screenshots or support records.

## Runtime and data rollback

Keep the previous runtime and its manifest. Stop the instance before snapshotting.
The offline route acquires the same instance lock as the server, checks SQLite's
`user_version`, copies exact files and modes, and produces a private receipt.
A snapshot omits `instance.lock` and `runtime.json`, which are process metadata.
A symlink, active owner, content change or newer schema blocks the operation.

```sh
./Runtime.command snapshot --data-dir '/absolute/current state' --output '/absolute/new snapshot'
./Runtime.command restore --snapshot '/absolute/new snapshot' --sha256 SNAPSHOT_RECEIPT_SHA \
  --output '/absolute/new restored state'
./Runtime.command start --data-dir '/absolute/new restored state'
```

`restore` only creates a **new** directory. It never overwrites the current state
or edits external projects. It checks exact snapshot integrity and rejects a
schema newer than the chosen runtime supports. Start and inspect that restored
state before selecting it as the active installation. Private snapshots must be
retained and protected by their owner. For ordinary live backups, keep the
workbench's existing reviewed backup/restore procedure; it has its own merge and
operation-reconciliation semantics.

## Build the Mac standalone developer artifact (retained route)

Build from a clean reviewed commit. The client build occurs on the developer's
machine; it is not a buyer prerequisite.

```sh
cd apps/agent-atelier
npm ci --ignore-scripts
npm run build -- --manifest
cd ../..
python3 -B scripts/build_workbench_runtime.py --output /absolute/build-output --arch arm64 \
  --node-archive /absolute/node-v24.22.2-darwin-arm64.tar.gz \
  --signed-checksums /absolute/SHASUMS256.txt.asc --keyring /absolute/nodejs-keyring.kbx
```

Use `--arch x64` and the corresponding official archive for Intel. The pinned
source URLs, archive SHA-256, signing fingerprint and keyring digest are in
`commercial/runtime/node-sources.json`. The builder invokes `gpgv` against the
exact signed checksum content and allowlisted signer before extracting only
Node and its full license notices. It preserves production client dependencies'
notices and rejects linked or hardlinked input files and linked source directories.
Source files come only from the exact HEAD's committed regular-file allowlist;
ignored and untracked files are never included, even when Git reports a clean
checkout. The separately generated client uses only `index.html` and the hashed
outputs explicitly declared by Vite's build manifest. Extra files in `dist` are
excluded. Node and dependency licenses use their own explicit inputs. The runtime
manifest records this selection and the Vite manifest hash; the Vite developer
manifest itself is not delivered. The builder inventories the complete selected
closure and creates a reproducible ZIP with executable modes. It records the
actual HEAD and refuses dirty sources. `--allow-dirty` exists for local rehearsal
only and marks the
result nonrelease. Never ship that rehearsal instead of the exact final commit.

After building, run `verify`, inspect the loaded interface, run the isolated
start/doctor/stop and snapshot/restore sequence, and retain receipts against the
exact runtime ZIP and source commit. Validate a clean extracted copy, not just
the source tree. A new code, dependency, source or manifest revision needs a new
artifact and affected proof; older observations remain tied to their own bytes.

Sources: [Node binary verification](https://github.com/nodejs/node/blob/v24.22.2/README.md#verifying-binaries),
[Node release keyring](https://github.com/nodejs/release-keys),
[Node v24 platforms](https://github.com/nodejs/node/blob/v24.22.2/BUILDING.md#platform-list).
