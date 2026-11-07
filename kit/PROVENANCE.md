# Agent System 5.0.0 portable core

This curated distribution contains the 33 reusable skills from the verified
Agent System 5.0.0 Codex release dated 2026-11-07. The original canonical
`manifest.json` and every one of its 2,955 declared skill files are preserved
byte for byte. Suite ID: `agent-system-5.0.0`.

## Included

- `skills/`: constructors (2), App Atelier (11), ChatBot Atelier (11), Game Atelier (9), including their operating references, templates, icons, helpers, and original tests.
- `portable/update_skill_suite.py`: local audit, exact-plan apply, verify, and rollback for the 33-skill suite.
- `portable/install_agent.py`: installer for separately prepared, declared project-agent kits. It does not create a project-agent kit by itself.
- `portable/check_generated_inheritance.py`: checks a generated child using the bundled constructor.
- `prepare_existing_project_update.py`: prepares adoption of a separately supplied project-agent source. Always pass an explicit `--source-root` pointing to the appropriate verified source kit; this distribution intentionally has no default `PROJECT_AGENT_SOURCE/`. Read `--help` before use.
- `verify_release.py` and a newly scoped `BUILD_VERIFICATION.json`: integrity for this curated core, including this provenance document.

## Intentionally excluded

The original project-specific `PROJECT_AGENT_SOURCE/`, prior personal installation
archive `compatibility/`, private installation/evaluation receipts, `evidence/`,
and historical project documentation are not part of this reusable distribution.
Source-machine locations, account identifiers, unpublished product knowledge,
and prior chat histories are not prerequisites for installation. The suite
manifest retains historical hash baselines needed by its drift-aware updater;
these contain hashes and file descriptors, not prior private file contents.

The empty ChatBot handoff templates retain the legacy schema identifier
`lumen.handoff/3` for format compatibility. They contain no Lumen product history
or live project data. Renaming a schema requires a separate compatibility change.

## Verification boundaries

The curated integrity record is newly generated. It is not a signature and does
not replace verification of source provenance, trusted transport, host discovery,
real task behavior, device results, or product acceptance. All 33 canonical
skill versions remain 5.0.0; repository documentation changes do not claim a new
skill runtime release.

Work can normalize presentation metadata and managed avatar bytes. A Work
read-back and this frozen portable source are separate evidence. Installing or
reading this repository does not automatically launch another session or adopt
the new standard into existing project agents. Existing local icons must be
preserved through the updater's actual apply journal and verify result.

## Check this copy

From the repository root:

```sh
python3 -B kit/verify_release.py
python3 -B kit/portable/update_skill_suite.py --help
```

See the repository user guide for first installation, language selection,
Work plus Codex handoff, existing-project migration, and rollback.
