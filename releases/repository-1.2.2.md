# Repository 1.2.2 / Atelier Orchestrator 1.0.1

This compatible patch corrects the optional orchestration skill's presentation. Its entrypoint, description, display name and starting prompt use Ukrainian, matching the owner's core-skill presentation. The guide now explains the distinction between `atelier-orchestrator`, a reusable coordination skill, and Agent Atelier 0.1.1, the separately launched local application/server. Their versions and installation records are independent.

The icon correction provides small and large PNG renderings of the existing SVG and binds them in the skill UI metadata. The original SVG, its shape, palette, system class and brand colour remain preserved. This is a delivery-format repair, not a new icon design. A valid asset or metadata reference alone does not establish that a particular host has rendered the icon; installed-source, discovery and actual display observations remain separate evidence.

## Scope and compatibility

- Optional `atelier-orchestrator`: 1.0.0 → 1.0.1. Stable name, invocation behaviour, tools, client operations, dependencies, permissions and the native-state preservation contract remain unchanged.
- Repository edition: 1.2.1 → 1.2.2. All seven complete guides retain equivalent instructions and explain the skill/application distinction.
- Core suite: 6.0.0, unchanged; no core reinstallation or icon replacement is needed.
- Agent Atelier service: 0.1.1, unchanged; no restart, database migration, project reset or product adoption is required by this patch.

The separate WORK task must still read actual registered sources, preserve customizations and verify saves through its supported manager. This release is not evidence of a live WORK update. Historical release and smoke records retain their original scope; no model or product verification is inferred from a translated instruction or PNG file.

See [the targeted update, verification and rollback procedure](migrations/repository-1.2.2.md). Actual installation, checks, package hashes, publication and remote readback are recorded by the executor after those operations occur.
