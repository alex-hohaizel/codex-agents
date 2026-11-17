# Buyer setup and recovery

The launcher calls `setup.py` inside the verified buyer package. With no action
and a terminal it opens an English or Ukrainian menu. All mutating operations
show the exact audited target and use the existing core and host installers.
The local workbench is a separately described runtime artifact; the setup does
not build TypeScript, download development dependencies, or migrate live panel
stores.

Use the exact Python and package paths from the received archive. Put global
options before the action:

```sh
python3 setup/setup.py --package "$PACKAGE" --locale uk doctor
python3 setup/setup.py --package "$PACKAGE" --json audit --plan "$PLAN"
python3 setup/setup.py --package "$PACKAGE" --json install --plan "$PLAN" --approve "$PLAN_SHA"
python3 setup/setup.py --package "$PACKAGE" --json verify --journal "$JOURNAL"
python3 setup/setup.py --package "$PACKAGE" --json discover --journal "$JOURNAL" --cwd "$PROJECT"
```

`audit` reports the exact plan digest and recovery journal path before the
first installed-file mutation. It caches the verified package under
`~/.local/share/codex-agent-system/packages/<manifest-sha256>` and keeps
plans, native updater journals, purchase documents and backups outside skill
discovery roots. The received Downloads copy can then be moved or removed.
The cached package is needed to interpret that operation's recovery record;
do not clean it while an operation is unresolved.

The default scope installs all 33 stable skills, Atelier Orchestrator, the
production profile and twelve roles. The core updater preserves recognized
local icons and refuses unknown policy or prompt drift. The host installer
retains valid local model/reasoning choices. Unknown Orchestrator changes are
held for an explicit merge; the setup has no force option. Your other skills
and existing projects are outside its write scope. Audit a new plan after
accepting a local merge.

A generated `Open Codex.command` registers the installed roles as launch
configuration without modifying the user's `config.toml`. Start Codex through
that launcher when you want those explicit roles. A successful file check is
separate from `discover`, and native role execution is separate from discovery.
The `first-task` action provides a small correction with a preserved note;
run it in a disposable project and verify the changed files.

For an interrupted installation, retain its original plan and digest:

```sh
python3 setup/setup.py --package "$PACKAGE" install --plan "$PLAN" \
  --approve "$PLAN_SHA" --resume "$JOURNAL"
python3 setup/setup.py --package "$PACKAGE" rollback --journal "$JOURNAL"
python3 setup/setup.py --package "$PACKAGE" uninstall --journal "$JOURNAL"
```

Resume verifies the exact package and subplans and reconciles the core
updater's actual consumption record. A home-scoped nonblocking writer lock
serializes buyer mutations even if two callers select different state
folders. Each sub-installer retains its own journal. Rollback restores the
recorded prior trees and profile; uninstall removes only still-exact managed
content and keeps projects, purchase documents and recovery backups.
Later unknown local changes block destructive recovery before it starts.

`--home` selects an explicit isolated target for a test user. `--state`
changes only the non-discovery storage root. Do not interpret a synthetic
home's file verification as a physical clean-machine result. Run native
`discover` in the actual consuming host and compare every resolved path.
`CODEX_HOME` selects the target's supported Codex configuration/authentication
root; sign in there using the buyer's own account when needed.

A retained purchase document is not authenticated solely because its JSON can
be read. The delivery/signature boundary authenticates it. Setup preserves its
exact bytes independently from subsequent catalog prices or store availability;
it never deletes projects because a store is unavailable.
