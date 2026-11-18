# Universal installer: build, verify and maintain

[Home](../../README.md) · [Buyer installation](../INSTALL.md) · [Platform contract](../../governance/UNIVERSAL_INSTALLATION.md)

The ready installer is the normal Windows, macOS and Linux route on x64 and
ARM64. `START_HERE.html` is tracked at repository root so GitHub source ZIP
users can find the ready Release assets. The extracted ready package launches
the same local browser wizard through `Start.cmd`, `Start.command` or `Start.sh`.
It contains its own native Python and Node. A Codex account, browser and any
domain SDKs/services used by a project remain separate.

## One implementation and compatible entry points

`commercial/setup/web.mjs` serves only loopback and translates authenticated
owner button actions into the existing `setup.py` commands. Saved plan SHA
approval, one-writer locks, retained packages and exact journals stay in that
engine. The static HTML does not execute filesystem changes itself. CLI
lifecycle arguments through `Start.command` remain supported. The existing
portable updater, optional skills, source packages and standalone runtime
controller keep their separate contracts.

The installer never changes system PATH or replaces a project's working Python,
virtual environment or Node. `AGENT_SYSTEM_PYTHON/NODE` identify retained toolkit
helpers. The generated native project launcher points Codex at the selected
practice project; opening it is a launch request, separate from observing a
model task. Removing a download does not remove its installed retained package.

## Supported targets and boundaries

| Package | Native target | Launcher |
| --- | --- | --- |
| Universal | All six below in one ZIP | Choose the native launcher |
| Windows-x64 / Windows-arm64 | Native Windows x64 / ARM64 | `Start.cmd` |
| macOS-x64 / macOS-arm64 | Intel / Apple Silicon | `Start.command` |
| Linux-x64 / Linux-arm64 | glibc Linux x64 / ARM64 | `Start.sh` |

The pinned Node24 runtime has upstream floors of macOS13.5, Windows10/Server2016
and Linux kernel4.18/glibc2.28/libstdc++GLIBCXX3.4.25, subject to vendor lifecycle
support. Windows11 is the recommended Windows target. Native CI identifies its
actual OS image; it does not certify every minimum-version device. Alpine/musl,
32-bit systems, Android/iOS and other operating systems have no ready package.
See [the upstream platform table](https://github.com/nodejs/node/blob/v24.22.2/BUILDING.md#platform-list).

Product launchers are unsigned. Vendor binary signatures remain where supplied;
Apple Developer ID/notarization and product Windows signing are not claimed.
Use the documented native OS warning/permission flow for a trusted download.
Private Windows state uses an actual protected current-user/SYSTEM DACL. Public
payload modes are a documented NTFS projection; content SHA stays exact.
Windows file flush + atomic rename + journal recovery proves process interruption
semantics, not an independent power-loss guarantee.

## Clean developer build

Use a clean reviewed Git checkout, build Python3.13, Node24.22.2 and npm.
These are developer prerequisites, not buyer setup requirements. No vendor input
or compiled client may enter a package without its reviewed inventory.

```bash
npm --prefix apps/agent-atelier ci --ignore-scripts
npm --prefix apps/agent-atelier run build -- --manifest
python scripts/check_repository.py
python scripts/check_commercial.py
python scripts/check_universal.py
python scripts/runtime_bundle.py --target linux-x64 --cache /tmp/agent-runtime-inputs --output /tmp/agent-runtime --verify-node-signature
python scripts/build_installer.py --runtime-bundle /tmp/agent-runtime/runtime-linux-x64.zip --output /tmp/agent-ready
```

Use native writable output paths on Windows. `--verify-node-signature` requires
developer `gpgv`; Linux CI verifies the official Node signed checksums against
the reviewed immutable public keyring. Every target checks the pinned archive
SHA. Python standalone and PyYAML source inputs have exact URLs/SHA, full
redistribution notices and no buyer pip step. Only reviewed in-namespace vendor
links are materialized; buyer ZIPs contain regular files.

Repeat `--runtime-bundle` with all six exact-commit runtime ZIPs to build Universal.
One target builds one smaller package. Other incomplete sets fail. Source,
compiled-client output, notices and platform binaries enter one canonical
buyer-stage assembly; `--allow-dirty` is engineering rehearsal only and is
refused by the release index. Preserve its explicit `source_clean:false` label.

```bash
python scripts/installer_index.py --artifacts-dir /tmp/all-native-inputs --output /tmp/installer-release --require-all
```

`INSTALLER-BUILD.json` and `INSTALLER-SHA256SUMS` describe the seven ready assets.
The legacy `BUILD.json` and `SHA256SUMS` still describe the two existing
WORK/CODEX source archives. Never substitute one format for the other.
The old commercial Solo/Team builder and trusted-delivery verifier remain
available; downloading a technical package does not issue a paid entitlement.

## Exact-archive acceptance and publication

The `Build and accept universal installers` workflow builds each of the six
native packages on the corresponding public standard runner, exercises the
received ZIP with isolated synthetic buyer data, and drives the real browser
wizard. It then assembles Universal from those exact six runtime inputs and
runs the Universal ZIP on all six native targets again.

Each receipt binds archive SHA, source commit, manifest and native target.
Checks cover writer exclusion; actual interrupted writes and resume; verify,
discovery and practice; preservation, rollback and uninstall; all controller
entry points and product-family workflows; and actual workbench boot,
authenticated backup/restore, snapshots and schema guards. A model call is a
separate observation; CI discovery does not imply a completed model task.

Main-only attestation waits for all12 backend+browser receipts and verifies
coverage against the seven artifact SHAs. A pull-request merge test is not the
published main source. After integration, rebuild and accept the exact main
commit before creating its visible latest GitHub Release. Verify its tag,
assets, checksums, attestations, source ZIP root HTML and direct download links.

Only reviewed redacted synthetic receipts and page screenshots may leave the
native test job. Never upload test HOME directories, runtime session keys,
private ready tokens, browser profiles, real account credentials or raw project
data. Native runner administrator privileges, if present, are an evidence limit;
they do not justify an unsupported non-admin execution claim.

Keep historical acceptance tied to its original bytes. Future changes must
refresh affected proof, maintain the [U01–U08 trace](../../governance/universal-requirements.json)
and preserve the immutable commercial contract and C01–C28 rights boundaries.
