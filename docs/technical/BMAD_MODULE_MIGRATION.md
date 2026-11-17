# Import and rehearse a BMad module migration in Codex

Use the module importer for reviewed local BMad sources. Give it the directory
with a single-skill `bmod.toml`, or the directory that contains a
`bmod-<code>` record beside its member skill folders. Stable modules can use
the directory containing `module.yaml` or its parent. The importer checks
native names, membership, required and recommended skills, dependency source
and minimum version, and conflicting installed entries. Record help, templates,
roster, knowledge documents and declared runtime files travel with the skills.
[Module files and dependency rules](https://docs.bmad-method.org/reference/module-files/)

Run the importer with Python 3.11 or newer. Stable YAML import also needs
PyYAML in that interpreter. Start from a reviewed unpacked distribution and
use its release version, archive identity and license. To import a stable
module's shared runtime, pass its reviewed `src/scripts` directory as
`--legacy-runtime`. The operator invokes reviewed runtime commands in the
staged project with the interpreter and dependencies required by those scripts.

## Audit and stage the project

```bash
IMPORTER="$PWD/kit/skills/agent-foundry/scripts/bmad_module.py"
python3.13 -B "$IMPORTER" audit \
  --source "$CORE_TOOLS" --source "$METHOD" \
  --project "$PROJECT" --license "$LICENSE" > "$PLAN"
PLAN_SHA="$(jq -er 'select(.ready) | .plan_sha256' "$PLAN")"
```

For a stable npm distribution, use its `src/core-skills` and
`src/bmm-skills` directories as the two sources and add
`--legacy-version 6.12.4 --legacy-runtime "$LEGACY_RUNTIME"`, substituting
the version actually in use. The original YAML setup descriptors and help
CSV remain available under `.bmad-import/modules/`. The audit identifies
packaged interpreter cache files and copies the original source scripts.

Add `--convert-legacy "$UPDATE_SOURCE"` to create a current `bmod.toml`
module record, a membership descriptor per skill, a help page from the CSV,
and a roster when the legacy module defines agents. Supply the intended BMad
source URI, for example `file:/path/to/reviewed/skills`. The converted copy
retains original prompts, runtime paths and raw YAML and CSV. The audit lists
legacy configuration behavior that needs review before distribution, including
custom defaults with result substitutions and select constraints.

Review `blockers`, `dependencies`, `target_entries`, `customization_moves`,
`retired_customizations`, `numbered_migrations` inside each module record,
and the exact staged files and modes. Use one or more `--previous "$OLD_SOURCE"`
arguments to identify installed members whose exact prior bytes and modes
match an independently reviewed older release. An unknown installed revision
or a different override at a rename destination blocks staging.

```bash
python3.13 -B "$IMPORTER" stage \
  --source "$CORE_TOOLS" --source "$METHOD" \
  --project "$PROJECT" --license "$LICENSE" \
  --expect "$PLAN_SHA" --output "$NEW_PROJECT"
python3.13 -B "$IMPORTER" verify --output "$NEW_PROJECT" --expect "$PLAN_SHA"
```

Reuse the same source, previous source, license and migration arguments in
audit and stage. Inspect the `BMAD-IMPORT.json` receipt. Keep the audit,
stage and personal settings local to the project. Stage opens a fresh
directory with project-local Codex skills and the selected BMad runtime.
The importer preserves the audited project, so recovery can return to that
project or start a new rehearsal. It applies recognized retirement renames
to separate team and personal files in the copy, retains removed overrides
for review, and sets personal-file permissions to owner access. Open the
new directory in a fresh Codex session and run a representative skill task.

Install messages, setup questions, and unknown metadata remain available for
the operator. Treat any declared activation steps and module runtime code as
reviewable source. Source catalog membership can establish which skills
will be staged. Actual discovery, execution and the result of the task each
need their own check.

## Rehearse a numbered migration

Read the original migration text and its checklist in the audit. The guide
may require decisions about source ownership, ticket semantics or repository
history. Create a reviewed JSON change set to rehearse the explicit outcome.
For each affected file, give the old project-relative path and SHA-256,
the new project-relative path, and a replacement path relative to the
change-set file when the contents need rewriting.

```json
{
  "schema": "bmad-project-migration/1",
  "module": "method",
  "number": 2,
  "definition_sha256": "<sha256 from numbered_migrations>",
  "roots": ["_bmad-output"],
  "files": [
    {
      "path": "_bmad-output/initiative-orders/tickets.toml",
      "sha256": "<sha256 of the original ticket index>",
      "to": "_bmad-output/initiative-orders/tickets/tickets.toml"
    },
    {
      "path": "_bmad-output/initiative-orders/initiative-orders.md",
      "sha256": "<sha256 of the original initiative>",
      "to": "_bmad-output/initiative-orders/initiative-orders.md",
      "replacement": "reviewed/initiative-orders.md"
    }
  ]
}
```

Add `--change-set "$CHANGES"` to both audit and stage. Paths stay under the
explicitly selected project artifact roots. The importer carries every
selected file and its original mode, applies only the listed moves and
replacements, checks the numbered guide's digest, and re-audits before
publishing the new directory. Read the staged ticket or document indexes
and run each check listed in `guide_checklist_pending` using the project
runtime. Record any semantic conversion, link, or Git history verification
separately before adopting the copy. The stage's source identities and
verification are useful when a second reviewer checks the same inputs.

For help assessing the old-format conversion and project layout, consult the
original workflow and numbered migrations in the admitted BMad distribution.
[Old module migration](https://docs.bmad-method.org/toolsmith/migrate-an-old-module/)
