# Release packages

The [component record](../releases/current.json) identifies the current repository edition, core, optional skills, role and host profiles, and Agent Atelier. The [installation guide](../docs/INSTALL.md) contains the operator steps for installation, updates, discovery, and recovery.

## Download and verify

Open [GitHub Releases](https://github.com/alex-hohaizel/codex-agents/releases/tag/v1.6.0). Download the archive for your host and the accompanying `SHA256SUMS`. Select the exact tag and commit recorded in the release notes. Verify the downloaded digest, repository, signing workflow `.github/workflows/validate.yml`, source ref `refs/heads/main`, and approved commit. The Codex admission command checks all these pins and stages the archive outside skill discovery roots.

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
