# Work control, decisions and status

One director or integrator owns the accepted result and its integration. The native project ledger has authority. Status views, decision cards, chat and handoffs describe that state.

## Assign and decide

Recover the goal and target, current scope, decisions, actual capabilities and nearest outstanding choice. Read existing sources before asking. A local reversible repair can use a precise short route. A substantial new scope may need the applicable briefing workflow. Keep the full target, first release and representative slice distinct.

The owner decides goals, material product choices, material changes, and stage acceptance. Carry out ordinary authorized work and repairs autonomously. Before changing audience, behavior, release platform, monetization, data or access rules, or significant dependencies, verify current authority and delegated limits. Do not ask again for the same exact authorization or invent a budget.

Use `assets/decision-card.template.md` for a material choice. State the question, why it is due, recommendation and grounds, feasible alternatives and consequences, exact scope and version, inherited decisions and actual response. Acceptance, refusal, changes, deferrals and partial acceptance have different consequences. A declaration, hash, recommendation, silence or executor's statement does not supply user authority.

Reopen only the decisions and results causally affected by a material change. Preserve independent results. Resolve unknown dependencies or explain a justified wider check. Assign one integration owner for shared writes and verify revisions. Record owner acceptance separately from a technical pass.

## Show progress and continue

State the goal, observed results and revisions, active work, actual blocked dependencies, and the decision needed from the owner if any. Report substantive changes and evidence boundaries. Provide logs and IDs when useful. Counts of documents, roles or calls do not measure quality.

A clarifying question leaves current work active. A request to continue resumes the authorized step. Keep pause, cancellation, blocked, waiting for evidence and complete distinct. Reconcile an external effect before retrying it. Background execution requires an actual authorized scheduler and runtime.

For closure, include the result, due requirements, checked scenarios, material gaps and continuation. A completed scope can close without a new stage or questionnaire. Keep the exact launch and return context only in the artifact or handoff where it is useful.

## Inspect recorded state with the read-only helper

`scripts/interaction.py` reads existing records and returns JSON or Markdown. Its output describes recorded source state. The actual domain and runtime controls establish execution, access and acceptance.

```sh
python3 -B scripts/interaction.py status --source /absolute/project --format markdown
python3 -B scripts/interaction.py status --source /absolute/project/.appatelier/state.json --format json
python3 -B scripts/interaction.py status --source /absolute/project/round.json --project-root /absolute/project --format markdown
python3 -B scripts/interaction.py decision --source /absolute/project --id D-1 --format markdown
```

| Domain | Native schema and path |
| --- | --- |
| Foundry | `1.0.0` with native layout, `.agent-foundry/state.json` |
| Game | `2.0.0` with toolkit and journal layout, `.gameatelier/orchestrator/state.json` |
| App | `app-atelier-state/1`, `.appatelier/state.json` |
| ChatBot round | `chatbot.round/1`, pass the exact existing file |
| ChatBot blueprint | `chatbot.blueprint/3`, pass the exact existing file |

Select the exact source if several native ledgers exist. `--scope VALUE` selects exact scope matches including related evidence. Leave it unset for a full view. The projection schema is `assets/status-view.schema.json`. A revision and digest identify the observed bytes.

Foundry and Game snapshot or journal hashes are checked. App and ChatBot record the lack of that native signature. Keep `specification/code/integration/device/human` separately as `recorded_pass`, `recorded_failed`, `recorded_pending`, `recorded_unresolved` or `unknown`. Chatbot `completion.assessments` respect failed and pending records even when other evidence is positive. A passed record needs a successful linked proof. `not_assessed` and `not_applicable` do not establish readiness. Maturity, stage or reviewer names do not establish proof.

The controlling outcome for Foundry, Game and App is native `status`; ChatBot uses `result`. Other result fields cannot override native modality, test kind or status. Stale proof is not a pass. ChatBot round `stage_complete` and `scoped_complete` describe recorded scope. Determine outstanding requirements from unresolved IDs, reviews and carry claims, rather than applicability flags. Blueprint `attempt.result` shows running, passed or failed separately from maturity and delivery.

The helper reads only the selected file or fixed ledger. It does not scan credentials or execute referenced components. The consumer checks referenced artifact freshness. Inputs reject symbolic links, ambiguous layout, inconsistent journals, duplicate JSON keys, nonfinite numbers and oversize files. Output selects fields and masks common secrets, including quoted JSON assignments, on a best-effort basis. Keep secret values out of ledger material.

Use domain review for substantive completeness, independence, actual builds, external receipts and owner acceptance. A workbench can display this projection after integration. Work chat control requires its own supported capability.

See [adaptive work](adaptive-work.md) for visible strategy, evidence and exact continuation and [visual identity](visual-identity.md) for stable presentation.
