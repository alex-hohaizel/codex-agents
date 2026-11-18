# Verify the product

[Repository home](../README.md) · [Evals and evidence](../docs/OPERATING_MODEL.md#evals-and-evidence) · [Native Codex canary](../evaluations/README.md#run-a-focused-native-codex-canary)

## Check the sources

```sh
python3 -B kit/verify_release.py
python3 -B scripts/materialize_standards.py --check
python3 -B scripts/check_repository.py
```

The repository check verifies the 33 core skill identities and files, component pins, optional assets, role configurations, installation entry point, requirements and the complete guide locales. Review media and gallery exports using their [build instructions](../marketing/README.md). Run the [release workflow](../.github/workflows/validate.yml) for repeatable domain, service, campaign and archive checks.

## Verify behavior in the actual host

[Native canaries](../evaluations/README.md) cover a direct task, a source-bound handoff, and the construction and use of a local candidate. Use controlled fixtures and compare actual changed files, resolved sources, expected results, permission refusals and operation receipts. Explicit invocation and natural routing need their own observations. A catalog entry and a successful import give useful evidence for discovery. Test the actual consuming step separately.

[Troubleshoot and verify the workbench](../apps/agent-atelier/README.md) with its built client, supported CLI, loopback owner session, and source-scoped project fixtures. Verify preserved source records and qualified outputs. Only claim actual device, provider, or production results when the corresponding operation and destination were observed for the exact version and scope.

## Verify installation and rollback

Verify the exact original and installed trees, the journal, protected icon and policy metadata, and host discovery from a fresh workspace. Keep native project data and the workbench store in their own preservation and recovery records. Follow [installation and operation](../docs/INSTALL.md).

## Commercial candidate

Run the [commercial contract](COMMERCIAL_PRODUCT_CONTRACT.md) checks against
the actual package and exact commit. Run `python3 -B scripts/check_commercial.py`
and the standard-library tests under `commercial/tests`. Test through the
buyer entry point with a fresh isolated user home, then preserve a prior
installation and its user edits. Record C01–C28 separately, including missing
hardware, seller facts, signing identities and provider access. New sales and
publication need their own owner approval.

## Universal installation maintenance

Apply [the universal installation contract](../governance/UNIVERSAL_INSTALLATION.md) to affected changes. Preserve all six
native Windows/macOS/Linux x64/ARM64 paths, explicit retained Python/Node helpers,
project environments, full source/resources, private permissions, recovery and
unknown drift. Ready installers and source archives are separate deliverables.
The root HTML must survive GitHub source downloads and link to ready assets.
Require exact-commit native package and real-browser evidence before release;
keep INSTALLER-BUILD.json distinct from the legacy two-archive BUILD.json.
Commercial purchase rights and owner sale gates remain unchanged.
