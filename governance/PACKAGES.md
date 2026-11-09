# Obtain and check the source bundles

The repository stores the exact sources and build instructions. Generated archives are ignored by Git so that repeated builds do not enlarge the source history.

## Build locally

From the repository root, run:

```bash
python3 scripts/check_repository.py
python3 scripts/build_packages.py
```

The `dist/` directory will contain:

- `Agent_System_6.0.0_WORK.zip`
- `Agent_System_6.0.0_CODEX.zip`
- `SHA256SUMS`
- `BUILD.json`

The Work and Codex bundles deliberately carry the same canonical sources, complete guides, migrations, templates and the current bilingual campaign. Each has a different `PACKAGE.json` and `PACKAGE_README.md` identifying its installation workflow. Work installation uses the supported personal-skill manager. Codex installation uses the portable updater. Extracting either archive alone performs no installation.

Obsolete advertising and rejected draft renderers are excluded from the current tree and packages. The exact build metadata records repository edition 1.3.0 separately from suite version 6.0.0. Optional Orchestrator1.1.0 includes its routing/maintenance contracts and pinned local helper dependencies; Agent Atelier0.2.0 remains separate service source, not another skill.

The optional `maintenance-skill/` and `optional-skills/atelier-orchestrator/` sources are separate from the 33 baseline skills and are not installed by the baseline updater. The source bundles exclude private project-specific agents, host backups and project histories.

## Download a completed GitHub Actions build

1. Open this repository on GitHub using an account with access.
2. Open **Actions**, then select **Validate sources, service and release bundles**.
3. Select a completed successful run for the exact source commit you intend to use. If there is no successful run yet, build locally or run **Run workflow** if your permissions and repository settings allow it.
4. In that run's **Artifacts** section, download **agent-system-bundles**. GitHub may require sign-in. Artifact availability and retention depend on repository settings.
5. Extract GitHub's artifact archive. It contains the two source ZIP files, `SHA256SUMS` and `BUILD.json`.
6. Compare the bundle hashes with `SHA256SUMS`. On macOS use `shasum -a 256 Agent_System_6.0.0_WORK.zip Agent_System_6.0.0_CODEX.zip`; on Linux use `sha256sum` with the same filenames. Then extract the required bundle and start with `PACKAGE_README.md` and `START_HERE.md`.

The workflow definition is included in this repository. Its presence does not prove that a run has already happened or that downloadable artifacts currently exist. A GitHub Actions artifact is also separate from a published GitHub Release.

The source bundles include the local service source/lockfile, shared production/context masters and host/role profiles. They exclude `node_modules`, built client assets, local service data, private audit reports and installation backups. Build the service as described in `apps/agent-atelier/README.md`. WORK live installation remains a separate host task requiring actual manager/readback evidence.
