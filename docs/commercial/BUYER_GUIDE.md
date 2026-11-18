# Install your Codex Agent System package

The ready technical Release has a local installer for Windows, macOS and Linux. Commercial Solo/Team terms and delivery remain an owner-reviewed **release candidate**, not an active sales listing. The buyer
supplies a supported authenticated Codex account. Models, API calls and external
services have their own fees. [Product composition](../../commercial/product.json)
and [license terms](LICENSING.md) distinguish the local package from those services.

## Receive and verify

For the technical release, download the ready Universal or matching-platform asset from the [official stable Release](https://github.com/alex-hohaizel/codex-agents/releases/latest). Extract the whole archive. GitHub's automatic Source code ZIP contains the source and navigation page; select a ready Release asset for the bundled runtimes and browser installer. Match the source commit, checksums, provenance and native test receipts to the exact artifact. Technical publication does not issue a purchase entitlement or activate sales.

The following separately trusted commercial delivery route remains available when the owner authorizes that delivery:


Receive the Solo or Team archive, your purchase/license document, the release
index and its signature through the seller's trusted delivery. Obtain the
verification public key through that trusted receipt independently of the ZIP.
A checksum in the same archive only detects inconsistency.

For this local RC, use the provided verification helper and the separately
delivered **test** public key. OpenSSL with Ed25519 support is needed for this
signature route; if it is absent, install supported OpenSSL or use an independently
trusted seller delivery path. Never choose a new public key from an untrusted ZIP.

```sh
python3 -B commercial/verify_distribution.py \
  --archive "$ARCHIVE" --index "$INDEX" --signature "$SIGNATURE" \
  --public-key "$TRUSTED_PUBLIC_KEY" --expected-source "$SOURCE_COMMIT" \
  --output "$NEW_STAGING_FOLDER" --openssl "$SUPPORTED_OPENSSL"
```

## Set up and start

Open `START_HERE.html` (English) or `ПОЧАТИ.html` (Ukrainian) in the verified folder, then open the platform launcher:

| Windows x64 / ARM64 | macOS Intel / Apple Silicon | Linux x64 / ARM64 |
| --- | --- | --- |
| `Start.cmd` | `Start.command` | `Start.sh` |

The launcher starts a private local browser wizard. The ready package includes Python, Node and the built interface; no separate runtime installation, npm build or administrator installation is required for this route. HTML alone cannot execute the installation. OS trust prompts and product signing status remain explicit release facts. If Linux extraction drops executable permission, enable execution in the file manager or use `chmod +x Start.sh` before `./Start.sh`.

Choose **Check now**, then **Prepare plan**. Review target folders, component changes, preserved settings and conflicts. Approve that exact plan, select **Install reviewed plan**, then **Verify files** and **Check in Codex**. The recommended selection contains all 33 core skills, Atelier Orchestrator, the managed profile and twelve roles. Repository Maintenance remains a separate owner tool; its complete source is included under `product/maintenance-skill` for supported skill-manager installation. The optional workbench has `Start-Workbench.cmd`, `Start-Workbench.command` and `Start-Workbench.sh`. Buying or installing the toolkit does not install a model or create an external tracker account.

Choose **Create practice project**, inspect it with **Open folder**, and request **Open Codex**. Copy its prompt into the opened session. The launcher targets the new practice folder, registers the installed roles and uses your own Codex account. Verify the heading repair and unchanged note. Setup only prepares this exercise. It does not execute a model or certify the task result.

Generated launchers preserve a working project Python/venv and Node. `AGENT_SYSTEM_PYTHON` and `AGENT_SYSTEM_NODE` identify the retained toolkit interpreters for its own helper scripts. A host without legitimate Python gets the bundled fallback; no global PATH or registry is changed. The command-line route is still available through the platform `Start` launcher with `--help` and the same engine:

Use the setup's `doctor` and `audit`, review the exact destinations and
conflicts, then use the returned plan identity for `install`. Keep the saved
plan and journal outside skill discovery. Run `verify`, then `discover`
from a fresh Codex host and `first-task` or `prepare-first-task`. If role discovery needs explicit
registration, use the launch flags returned by setup; source files alone do
not prove a configured native role. The setup `--help` supplies exact options.

For a first useful task, copy `examples/first-task` to a disposable workspace
and ask the installed Orchestrator to correct its one misspelled heading while
preserving `notes.txt`. Check the resulting files. Model execution uses your
existing Codex account and permission boundaries.

## Update, restore and remove

Keep your entitlement document and prior package. A same-major update does not
replace previously acquired rights. Repeat audit for the new trusted package.
Unknown local edits are conflicts to resolve; there is no blanket force option.
A supported repeated installation must preserve one installed copy.

For interrupted work, refresh **Continue or recover**, select the identified installation, retain the exact plan and use its checked journal to resume. Read back an unknown result before repeating an operation.
Use that journal for rollback. Uninstall checks ownership and preserves later
user changes and unrelated skills. Workbench data has its own schema and backup
procedure: do not roll back a binary over newer data without a compatible backup.

Use the diagnostics in a support report, with product and component versions,
platform, order reference and the failing step. Do not send Codex credentials,
API tokens, your private projects or full chat history. The owner-provided
support/privacy contact is **Oleksandr Hohaizel**, **aleksandrhohaizel@gmail.com**.
This email is not a postal address or proof of legal status. The contact must
be confirmed operational; staffed hours and remaining legal seller facts
still require completion before public sale. Generic non-sensitive source
bugs can use the public repository issue tracker.

The ready Universal archive includes the workbench interface and runtimes for all six declared desktop targets. Use the matching `Start-Workbench` file and the [runtime/data recovery guide](WORKBENCH_RUNTIME.md). The retained legacy commercial builder can also include separate Mac architecture archives under `runtime/`; those use their own `Launch.command`. Availability, native OS/CPU execution, graphical interaction, signing and model tasks are distinct checks. Read the exact Release receipts for performed checks and remaining limits; do not infer six-platform validation from one local run.
