# Verify the portable core

The core suite contains 33 reusable skills. `manifest.json` lists the stable selectors, the suite version, and the exact source files, hashes, sizes, and modes. `BUILD_VERIFICATION.json` binds the manifest and curated kit inventory. The repository edition and separately installed components have their own version records. [Current components](../releases/current.json)

| Path | Purpose |
| --- | --- |
| `skills/` | The two constructors and the App, ChatBot, and Game Atelier families, with their local references, templates, icons, and helpers |
| `portable/update_skill_suite.py` | Audit, apply, verify, and roll back the managed core suite using the exact plan and journal |
| `portable/install_agent.py` | Install a separately prepared agent kit into its owned project |
| `portable/check_generated_inheritance.py` | Verify the exact declared files and entry links in a generated child |
| `prepare_existing_project_update.py` | Prepare an update for the specified existing agent using the reviewed source passed as `--source-root` |

Run the integrity check from the repository root.

```sh
python3 -B kit/verify_release.py
```

For installation, verify the official archive with its GitHub attestation and use the trusted updater to inspect the actual local target. The manifest's compatibility descriptors let the updater recognize known sources and preserve approved icon files, paths, and colors. Keep unknown edits for review. An apply journal records the exact before and after state. [Install and verify](../docs/INSTALL.md)

The kit checksum check covers file bytes and the declared inventory. Fresh host discovery establishes the source Codex resolves. A representative native task provides behavior evidence for the exercised workflow. Existing projects and separately installed agents retain their own state and approval boundary.
