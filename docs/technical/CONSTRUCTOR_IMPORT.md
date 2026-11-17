# Import reviewed native Codex skills and roles

Use Agent Foundry's importer when the original materials already contain a
Codex-style skill directory or a flat role definition. Review those files
and their rights before using them. The constructor stages a new project
with the actual native discovery paths. Open that project in a fresh Codex
session and check that it runs the representative task.

In a manifest with schema `codex-agent-import/1`, list modules with an ID,
version and members. Each member has a `kind` of `skill` or `role`, its
native `name`, and a `source` relative to the manifest. Use `requires` for
required module IDs and `optional` for optional module IDs. The plan
reports absent optional modules and rejects missing required modules and
dependency cycles. Use Python 3.11 or later for native TOML roles.

```json
{
  "schema": "codex-agent-import/1",
  "modules": [
    {
      "id": "review-tools",
      "version": "1.0.0",
      "members": [
        {"kind": "skill", "name": "record-review", "source": "sources/record-review"},
        {"kind": "role", "name": "review-specialist", "source": "sources/review-specialist.toml"}
      ]
    }
  ]
}
```

An optional `customizations` array binds a member by `kind` and `name`.
Each layer provides `scope` (`team` or `personal`), `mode`
(`replace`, `prepend` or `append`), a relative text `source`, and the
`expected_sha256` of the member entry before the layer. Inspect the team
layer result to pin the input for a personal layer. These layers amend the
prompt body and retain skill identity, UI policy, and role configuration.

```bash
IMPORTER="$PWD/kit/skills/agent-foundry/scripts/import_codex.py"
python3 -B "$IMPORTER" audit "$MANIFEST" --target "$PROJECT"
python3 -B "$IMPORTER" stage "$MANIFEST" --target "$PROJECT" \
  --expect "$PLAN_SHA" --output "$NEW_PROJECT" > stage.json
```

Read the observed target, blockers and `plan_sha256` before staging.
Staging checks the same inputs, rejects conflicting names, and publishes
the reviewed files into the new directory. Keep the original source and
review report so the task and any later customization can be reproduced.
For a fresh launch that does not load project configuration, pass each
`role_launch_overrides` string from `stage.json` as its own `-c` argument.
This explicitly registers the staged roles for that launch. For example,
from the directory containing `stage.json` (requires `jq` and Bash):

```bash
role_flags=()
while IFS= read -r setting; do
  role_flags+=(-c "$setting")
done < <(jq -r '.role_launch_overrides[]' stage.json)
codex -C "$NEW_PROJECT" "${role_flags[@]}"
```

Check from a new session that the named skill is discoverable and that the
named role executes a task that distinguishes its reviewed instructions.
Use the normal project adoption workflow when the staged skills and roles
are ready for a managed destination.
