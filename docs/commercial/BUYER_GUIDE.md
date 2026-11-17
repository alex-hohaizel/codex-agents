# Install your commercial candidate

This is a local **release candidate**, not an active sales listing. The buyer
supplies a supported authenticated Codex account. Models, API calls and external
services have their own fees. [Product composition](../../commercial/product.json)
and [license terms](LICENSING.md) distinguish the local package from those services.

## Receive and verify

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

Open `START_HERE.html` (English) or `ПОЧАТИ.html` (Ukrainian) in the verified
folder. Open `Start.command` on Mac or run the setup tool on a supported POSIX
system. The setup shows prerequisites and each component separately. Python
3.9+ is required; use [the official installer](https://www.python.org/downloads/)
when it is missing. The setup does not download dependencies or use admin rights.

The recommended selection contains all 33 core skills, Atelier Orchestrator,
the managed profile and twelve roles. Repository Maintenance remains an owner
tool. The workbench is a separate ready-built Mac runtime candidate. Buying the
toolkit does not install a model or create an external tracker account.

Use the setup's `doctor` and `audit`, review the exact destinations and
conflicts, then use the returned plan identity for `install`. Keep the saved
plan and journal outside skill discovery. Run `verify`, then `discover`
from a fresh Codex host and `first-task`. If role discovery needs explicit
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

For interrupted work, retain the exact plan and use the identified installation
journal to resume. Read back an unknown result before repeating an operation.
Use that journal for rollback. Uninstall checks ownership and preserves later
user changes and unrelated skills. Workbench data has its own schema and backup
procedure: do not roll back a binary over newer data without a compatible backup.

Use the diagnostics in a support report, with product and component versions,
platform, order reference and the failing step. Do not send Codex credentials,
API tokens, your private projects or full chat history. The private commercial
support address is an owner-supplied prerequisite before public sale; generic
non-sensitive source bugs can use the public repository issue tracker.
