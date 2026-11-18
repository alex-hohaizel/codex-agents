# Release packages

The [component record](../releases/current.json) identifies the current repository edition, core, optional skills, role and host profiles, and Agent Atelier. The [installation guide](../docs/INSTALL.md) contains the operator steps for installation, updates, discovery, and recovery.

## Download and verify

Open [the latest stable GitHub Release](https://github.com/alex-hohaizel/codex-agents/releases/latest). For the recommended browser setup, download the ready Universal installer or the ready ZIP matching your system and CPU. Follow [installation and recovery](../docs/INSTALL.md).

| Ready asset | Use |
| --- | --- |
| `Agent-System-<repository-version>-Universal.zip` | One complete Windows/macOS/Linux x64/ARM64 package with bundled runtimes. |
| `Agent-System-<repository-version>-<system>-<cpu>.zip` | The same product with one native runtime pair; select Windows, macOS or Linux and x64 or arm64. |
| `INSTALLER-BUILD.json` and `INSTALLER-SHA256SUMS` | Exact source, inventory and digests for the seven ready ZIPs. Verify their `.github/workflows/universal-installers.yml` attestations against `refs/heads/main` and the recorded commit. |
| `NATIVE-ACCEPTANCE.zip` and its checksum | Redacted archive-bound native receipts and actual browser screenshots, including explicit environment limits. |

For the separately controlled source-import route below, download the host archive and accompanying `SHA256SUMS`. Select the exact tag and commit recorded in the release notes. Verify the downloaded digest, repository, signing workflow `.github/workflows/validate.yml`, source ref `refs/heads/main`, and approved commit. The Codex admission command checks all these pins and stages the archive outside skill discovery roots.

| Asset | Use |
| --- | --- |
| `Agent_System_<core-version>_CODEX.zip` | Install the personal Codex core with the portable updater. The archive also supplies the optional skills and their separate installation paths. |
| `Agent_System_<core-version>_WORK.zip` | Inspect the sources and use the host's supported personal skill management. Check that each saved skill is registered and can be invoked. |
| `SHA256SUMS` and `BUILD.json` | Compare archive bytes and inspect the component and file inventory. Use the separate attestation to verify provenance. |

Use the available Work interface and your workspace permissions. Native host behavior, local workbench service data, and product state have their own verification procedures.

## Build from the current source

```sh
python3 -B scripts/check_repository.py
python3 -B scripts/build_packages.py
```

Source builds contain current documentation, executable and test sources, curated skill assets, and technical examples. GitHub Actions supplies the showcase export and source snapshots for the exact checked commit. For published installation downloads, use the files attached to the stable release and their own recorded digest and attestation. For an installed result, keep the updater journal and open a fresh Codex session to confirm discovery and one meaningful invocation.

## Buyer distributions

The [commercial builder](../scripts/build_commercial.py) derives buyer packages
from [the product descriptor](../commercial/product.json) and the component
record. The source bundles remain available for their existing workflows.
The buyer package supplies a local start page, setup, complete runtime resources,
license and third-party notices. Ready workbench distributions include the built
interface and Windows/macOS/Linux runtimes. Separate legacy Mac workbench
archives retain their own architecture and signing records. See
[the buyer guide](../docs/commercial/BUYER_GUIDE.md).

Use repeated `--runtime-artifact` arguments on the commercial builder to include the exact clean-source Mac archives in one buyer delivery. Runtime source/architecture pins must match the buyer package. A skills-only CI archive explicitly records that its optional runtime is separate.

## Universal installation maintenance

Apply [the universal installation contract](../governance/UNIVERSAL_INSTALLATION.md) to affected changes. Preserve all six
native Windows/macOS/Linux x64/ARM64 paths, explicit retained Python/Node helpers,
project environments, full source/resources, private permissions, recovery and
unknown drift. Ready installers and source archives are separate deliverables.
The root HTML must survive GitHub source downloads and link to ready assets.
Require exact-commit native package and real-browser evidence before release;
keep INSTALLER-BUILD.json distinct from the legacy two-archive BUILD.json.
Commercial purchase rights and owner sale gates remain unchanged.

## Publish accepted technical artifacts

After the exact merged `main` commit passes both source validation and all native
installer jobs, dispatch [Publish an accepted technical release manually](../.github/workflows/publish-technical-release.yml)
on `main`. Supply that full commit as `expected_source_sha`, the successful
installer run as `accepted_native_run_id`, and the source validation run as
`source_validation_run_id`. Dispatching this workflow authorizes publication of
the technical Release; it is a separate action from building a candidate.

The publisher retrieves only those accepted CI artifacts, checks all seven ready
ZIPs and twelve native/browser proofs, verifies the source bundles and exact-main
attestations, and reconciles the tag, draft and every asset against GitHub. It
uploads missing files without overwriting unknown assets, verifies the complete
remote set, then marks the Release as latest. An uncertain response leaves an
explicit reconciliation receipt; inspect its exact target before dispatching
again. The job keeps `PUBLICATION.json` as `technical-publication-receipt`.
Commercial sales, paid entitlement issuance and legal approval remain separate.
