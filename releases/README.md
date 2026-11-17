# Current release

**Codex Agent System v1.7.0** is the repository release. Select this edition in GitHub Releases to download the matching package. The Codex and Work archives carry the same edition and core version.

| Component | Version | What the version identifies |
| --- | --- | --- |
| Codex Agent System release | 1.7.0 | The repository edition, handbook, showcase, and package downloads |
| Core and both constructors | 6.4.0 | The 33 bundled skills, including Agent Foundry and Design Specialist Skills |
| Codex profile and roles | 6.2.0 | The managed production profile and twelve role definitions |
| Atelier Orchestrator | 1.5.0 | The optional routing and handoff skill |
| Maintenance | 1.2.1 | The optional repository maintenance skill |
| Agent Atelier for macOS | 0.7.0 | The local workbench and its runtime |

Use the edition number when asking for a download or reporting an issue. Use a component version when checking what is installed or comparing behavior. Components advance when their distributed content changes. The edition can advance with the same runtime or role definitions. Protocol and file format identifiers track data compatibility for their own consumers.

The [component record](current.json) is the source for these values and the core manifest digest. The [published release](https://github.com/alex-hohaizel/codex-agents/releases/tag/v1.7.0) identifies the exact commit and attested artifacts. Start with [installation](../docs/INSTALL.md) or the [multilingual handbook](../START_HERE.md).

## What changed in v1.7.0

- Build an offline interactive UX walkthrough whose screens refer to exact
  design and experience sources. Exercise conflict and recovery, then export
  the path and source binding. [UX prototype](../docs/technical/UX_PROTOTYPE.md)
- Use a reusable template registry with reviewed sources, conditional or repeat
  sections, and companion documents. [Document templates](../docs/technical/DOCUMENT_TEMPLATES.md)
- Inspect and stage current and legacy module trees and reviewed migration changes separately
  from the active project. [Module migration](../docs/technical/MODULE_MIGRATION.md)
- Compare a local ticket tree against mapped GitHub, Linear, Jira Cloud, Notion
  or Trello objects. Preview outgoing changes, identify incoming changes and
  conflicts, and reconcile lost responses before another effect. Provider
  capabilities and observed deployments are tracked separately.
  [Tracker tree](../docs/technical/TRACKER_SYNC.md) · [Provider setup](../docs/technical/TRACKER_PROVIDERS.md)

The new [front page](../README.md) shows the latest workflows and an
illustrated route from one conversation to specialist work and release
evidence. [Start with one task](../START_HERE.md) or follow the
[worked project](../docs/technical/END_TO_END.md).

The release includes these workflow implementations. Check the provider
and browser notes for tested targets, unsupported operations and the line
between a verified local case and live provider or device acceptance.

## What changed in v1.6.0

- Continue a release or product workshop from its exact record. Select methods
  from a reviewed catalog, change technique between rounds, and export the
  evidence and decisions to Markdown or HTML. Build a brief, PRFAQ or separate
  design and experience documents that show open questions and affected
  requirements. [Workshop](../docs/technical/WORKSHOP.md) ·
  [Product facilitation](../docs/technical/PRODUCT_FACILITATION.md)
- Audit local modules and stage existing Codex skills and roles in a new
  project. Preserve native identities and apply team and personal prompt
  customizations in order. [Import](../docs/technical/CONSTRUCTOR_IMPORT.md)
- Read mapped GitHub Issues and preview a single title, state or relationship
  change. Recheck the affected state before sending the request and read back
  the result if the response is lost. [Mapped GitHub work](../docs/technical/TICKET_GITHUB.md)
- Preserve the original sprint, link editable product and architecture documents
  to requirements, and keep worktree handoffs and release evidence tied to
  exact bytes. Agent Atelier reads the exact recorded Codex turn after restart
  and preserves an explicit pause or cancellation while the outcome is unknown.
  [Project workflow](../docs/OPERATING_MODEL.md) · [Workbench API](../apps/agent-atelier/shared/API.md)

Native Codex sessions exercised workshop continuation and staged imports.
A controlled HTTP target exercised GitHub writes and recovery while live
GitHub requests verified read and preview behavior. Other providers,
other optional workflows, and target-device runs have their own acceptance
work. The release covers the behavior listed here.
