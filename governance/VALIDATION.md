# Verify the product

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
