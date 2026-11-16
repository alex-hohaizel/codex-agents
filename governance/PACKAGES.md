# Obtain and check the source bundles

The active GitHub branch stores the versioned sources, requirements and build instructions. Generated archives are ignored by Git so that repeated builds do not enlarge the source history.

## Build locally

From the repository root, run:

```bash
python3 scripts/check_repository.py
python3 scripts/build_packages.py
```

The build reads the core version from the current release record and writes these files to `dist/`:

- `Agent_System_<core-version>_WORK.zip`
- `Agent_System_<core-version>_CODEX.zip`
- `SHA256SUMS`
- `BUILD.json`

The Work and Codex bundles deliberately carry the same canonical sources, complete guides, migrations, templates and the current bilingual campaign. Each has a different `PACKAGE.json` and `PACKAGE_README.md` identifying its installation workflow. Work installation uses the supported personal-skill manager. Codex installation uses the portable updater. Extracting either archive alone performs no installation.

Use `PACKAGE.json` and `BUILD.json` to identify the branch, repository edition and core suite. Follow the current release record for optional component and local service versions and the matching migration. [Current release](../releases/current.json) · [Requirements](requirements.csv)

The optional `maintenance-skill/` and `optional-skills/atelier-orchestrator/` sources are separate from the 33 baseline skills and are not installed by the baseline updater. The source bundles exclude private project-specific agents, host backups and project histories.

## Download a completed GitHub Actions build

1. Open this repository on GitHub using an account with access.
2. Open **Actions**, then select **Validate sources, service and release bundles**.
3. Select a completed successful run for the exact revision you want. Use the latest verified revision of the active branch for current instructions. The [current release record](../releases/current.json) also links the original feature release bundles. If there is no successful run yet, build locally or run **Run workflow** if your permissions and repository settings allow it.
4. In that run's **Artifacts** section, download **agent-system-bundles**. GitHub may require sign-in. Artifact availability and retention depend on repository settings.
5. Extract GitHub's artifact archive. It contains the two source ZIP files, `SHA256SUMS` and `BUILD.json`.
6. Compare the bundle hashes with `SHA256SUMS`. In the extracted artifact directory, run `shasum -a 256 -c SHA256SUMS` on macOS or `sha256sum -c SHA256SUMS` on Linux. For source inspection or a disposable fixture, review the extracted `PACKAGE_README.md` and `START_HERE.md`. For managed Codex adoption, verify the stable archive and its GitHub attestation, and audit the exact staged kit from the admission receipt. Follow the migration in the [current release record](../releases/current.json); checksums packaged next to the ZIP do not replace provenance.

The workflow definition is included in this repository. Its presence does not prove that a run has already happened or that downloadable artifacts currently exist. A GitHub Actions artifact is also separate from a published GitHub Release.

The source bundles include the local service source/lockfile, shared production/context masters and host/role profiles. They exclude `node_modules`, built client assets, local service data, private audit reports and installation backups. Build the service as described in `apps/agent-atelier/README.md`. WORK live installation remains a separate host task requiring actual manager/readback evidence.
