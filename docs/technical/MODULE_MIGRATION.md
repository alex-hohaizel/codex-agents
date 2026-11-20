# Import and rehearse project module migrations

Start with the module directories and license files you have reviewed. The
importer accepts a single skill with a `bmod.toml` registry, a module record
beside its member skill folders, or a legacy directory described by
`module.yaml` and a help CSV. It checks native skill names, membership,
required and recommended dependencies, minimum versions, runtime resource
paths, and conflicting installed entries.

Use Python 3.11 or newer. Legacy YAML inputs need PyYAML in that interpreter.
Provide the source archives, files and license terms from your own reviewed
sources. The staged copy keeps module help, templates, roster, knowledge
documents and declared runtime files with their originating module.

## Audit and stage the project

Run this from the reviewed toolkit checkout. Replace the paths with your
actual module source, project and license.

```bash
IMPORTER="$PWD/kit/skills/agent-foundry/scripts/module_migration.py"
python3.13 -B "$IMPORTER" audit \
  --source "$MODULE_SOURCE" --project "$PROJECT" --license "$LICENSE" > "$PLAN"
PLAN_SHA="$(jq -er 'select(.ready) | .plan_sha256' "$PLAN")"
```

Repeat `--source` for a module with a dependency supplied separately.
For legacy input, add `--legacy-version "$LEGACY_VERSION"` using its exact
release version when the source does not declare it. The original YAML
and help CSV are carried under `.module-import/modules/`. Packaged Python
bytecode caches are identified in the audit. The staged copy takes the
source files.

Use `--runtime-root "$RUNTIME_ROOT" --artifact-root "$ARTIFACT_ROOT"` to
match the paths expected by the source project. Both are relative to
the project and default to `_modules` and `_module-output`. Supply
`--shared-runtime "$REVIEWED_SCRIPTS"` for each reviewed directory of
shared Python source files. Shared scripts are staged in the runtime
root's `scripts/` directory. Module-local scripts declared by members
are staged under their module code. The operator invokes the runtime
with the interpreter and dependencies it expects.

Add `--convert-legacy "$UPDATE_SOURCE"` to generate a current
`bmod.toml` record, membership descriptors, a help page from the CSV,
and a roster from supported agent entries. Supply the intended module
source URI, such as `file:/path/to/reviewed/skills`. The staged copy
retains the original prompts, YAML and CSV. The audit lists where
legacy configuration behavior still needs review, including custom
default substitutions and select constraints.

Review `blockers`, `dependencies`, `target_entries`, the customization
moves and retained retired overrides. Inspect the numbered migration
entries under the module record. Use `--previous "$OLD_SOURCE"` to
recognize a previously installed entry when its files and modes match a
reviewed older source. An unknown installed revision or a conflicting
rename destination blocks staging.

```bash
python3.13 -B "$IMPORTER" stage \
  --source "$MODULE_SOURCE" --project "$PROJECT" --license "$LICENSE" \
  --expect "$PLAN_SHA" --output "$NEW_PROJECT"
python3.13 -B "$IMPORTER" verify --output "$NEW_PROJECT" --expect "$PLAN_SHA"
```

Pass the same inputs and layout options to audit and stage. Read
`MODULE-IMPORT.json` and keep it with the audit and private settings.
Team and personal overrides keep their content through recognized
renames in the new project. Removed overrides remain available for
review, and the personal copies have owner-only permissions. The
original project remains available for recovery. Open a fresh chat in
the new project and run a representative task using the loaded skill.

For an earlier verified stage with a different receipt filename and
format identifier, pass its original name and schema with
`verify --receipt-name "$RECEIPT_NAME" --receipt-schema "$RECEIPT_SCHEMA"`
and the original plan digest. This checks the existing receipt and stage
without editing them.

## Rehearse a numbered migration

Read the module's original migration guide and checklist. A guide can
ask for decisions about permissions, document meaning, or repository
history. Prepare the explicit file changes you want to rehearse. For
each selected file, give the original project-relative path and its
SHA-256, the target project-relative path, and a replacement relative
to the change-set file if its contents need to change.

```json
{
  "schema": "codex-agents.project-module-migration/1",
  "module": "dock",
  "number": 2,
  "definition_sha256": "<sha256 from numbered_migrations>",
  "roots": ["_module-output"],
  "files": [
    {
      "path": "_module-output/initiative-orders/tickets.toml",
      "sha256": "<sha256 of the original ticket index>",
      "to": "_module-output/initiative-orders/tickets/tickets.toml"
    },
    {
      "path": "_module-output/initiative-orders/initiative-orders.md",
      "sha256": "<sha256 of the original initiative>",
      "to": "_module-output/initiative-orders/initiative-orders.md",
      "replacement": "reviewed/initiative-orders.md"
    }
  ]
}
```

Add `--change-set "$CHANGES"` to both audit and stage. If a previously
reviewed change set has a different schema identifier and the same
fields, pass `--change-set-schema "$ORIGINAL_SCHEMA"` to both commands.
With a change set that moves or replaces files, add
`--plan-file "$CHOICE_ROOT/migration-plan.json"` to the audit. Pin that
exact file in the approved [production choice's](PRODUCTION_CHOICES.md)
`configuration`. Add `--choice-root "$CHOICE_ROOT"` to stage when the
record is outside the audited project. Use a new plan file for each
reviewed revision. Staging checks these dependencies again before it
publishes the new directory.

The importer checks the exact migration guide, file paths and contents
before staging. It copies the selected artifact roots, applies the
listed moves and replacements, and checks the inputs again before
publishing the new directory. Check the cited links and indexes in the
new project and run each item under `guide_checklist_pending`. Keep
semantic changes and Git history findings with the migration evidence.
