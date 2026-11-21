# Production choices, approved design, and implementation

[Documentation](../INDEX.md) · [Task entry point](../../START_HERE.md) · [Update and recovery](../INSTALL.md)

Start in the project that owns the work. Select **Atelier Orchestrator** or invoke the appropriate specialist directly. Provide the requirement source, who uses the result, the first useful scenario, the actual target, and any existing decision or accepted master. The agent should explain which comparison matters in plain language and show how to review the result in the intended medium.

| Before | What to prepare | What to demonstrate |
| --- | --- | --- |
| A material draft or experiment | Requirements and source pins, candidate combinations, experiment purpose, constraints, checked sources, and comparable inputs | Why this first probe uses those tools and what remains experimental |
| Dependent implementation | A current decision, defining settings, explicit authority for the exact subject, original masters, required flows, and adaptation limits | How the task uses the pinned files, behavior, tools, and scope |
| Replication | A source-linked representative result, actual runtime or medium, positive and failure controls, and reviewed evidence | The defining behavior on the intended target |
| Acceptance | The exact deliverable, independent observations, workflows and affected controls, including repair and recovery where relevant | Fidelity, usable behavior, and the conditions under which the evidence applies |

For a narrow repair, carry forward the current choices and prove the affected risk. A material change to the stack, an accepted layout or state, navigation, data, permissions, or recovery reopens its decision. Record the proposed changes, affected requirements, tests and artifacts, and migration or rollback. Retain unrelated valid proofs.

## Make a project record

Use `production-choices.json` at the governed project root. The [production choices contract](../../standards/production-choices.md) defines how to prepare the inputs. The [technology catalog](../../standards/technology-catalog.json) includes candidates from research, web and mobile, games, art and media, languages, data, integrations, AI, deployment and maintenance. Search by candidate, platform or tool capability. For example, `jq '.categories[] | select(.id | contains("data"))' standards/technology-catalog.json` shows category entries, and `rg -in 'renderer|kotlin|sqlite|migration' standards/technology-catalog.json` searches across categories. Check the current official source and the host for facts that affect your decision. A catalog update does not change a project decision.

- `requirements` gives each requirement its stable ID, description, pinned source, and `hard` flag. `references` labels source material as `inspiration`, `constraint`, `master`, or `rejected`.
- `experiment` names a feasible `candidate_id`, purpose, common input pins, a procedure pin, plain-language success criteria and a `temporary_boundary`. Fill it before generating any material probe. Compare later choices with the same inputs, retaining the rationale and original evidence.
- `candidates` records considered combinations, component versions, the same requirement checks, dated sources, probe and reasons for inclusion or exclusion. Work out rights, costs, access, import/export and recovery in the pinned comparison and configuration.
- `decision` names the selected candidate, reasons, review date, configuration, approved masters, defining flows, adaptation limits, and the exact `approval` receipt. The approval has a separate authority source and binds the result of `subject`. Keep approval of a creative direction and acceptance of a delivery as distinct records.
- `evidence` binds a phase, independent reviewer, result, method, environment, observable artifacts and positive and negative controls to the exact decision. Every project source pin uses a normalized project-relative `path` and `sha256`.

Set `HELPER` to the actual installed skill helper path or the checkout's `standards/production_choices.py`. From the checkout, substitute the owning project directory for `<PROJECT>`.

```bash
HELPER=standards/production_choices.py
TOOLKIT_PYTHON="${AGENT_SYSTEM_PYTHON:-python3}"
"$TOOLKIT_PYTHON" "$HELPER" catalog --capability renderer --platform browser
"$TOOLKIT_PYTHON" "$HELPER" verify <PROJECT> --phase explore
"$TOOLKIT_PYTHON" "$HELPER" subject <PROJECT>
"$TOOLKIT_PYTHON" "$HELPER" verify <PROJECT> --phase implement
"$TOOLKIT_PYTHON" "$HELPER" verify <PROJECT> --phase scale
"$TOOLKIT_PYTHON" "$HELPER" verify <PROJECT> --phase accept
```

Set the target, techniques, and documented permissions before launching the experiment. Record what the experiment measured and what its result cannot establish. Use `subject` to get the canonical hash for the authorized approval record. The full record hash used to bind a handoff can change when new evidence is appended. Depending only on a specific still-current decision requires its exact decision hash. An existing approval cannot be reused for changed source bytes, stack, masters or flow.

## Follow the consuming route

- **App experience.** Compare actual rendered scenarios. `ux_prototype.py` offers an offline navigation simulation. The `verify-master` route checks a separate runnable approved artifact and its flow against the project's exact record. The executor must still demonstrate input, permissions and behavior in the browser or device.
- **App, ChatBot, and Game.** Use the native stage and project records to carry decision pins and own the correct acceptance stage. An isolated runtime is useful evidence when its boundary is stated. An emulator, a locally imported file, and a physical production target have distinct claims.
- **Skill constructors.** Check the approved blueprint before creation and the exact staged child files before packaging. Run the built portable or role-based installer in an isolated target before adopting it. Project-agent migration is explicit. Existing packages remain readable through their compatible branch.
- **Workbench.** New writable tasks require a current `production-choices.json` record. Preparation, dispatch and resume also recheck a declared choice or explicitly selected phase for read-only tasks. Choose **Narrow repair using existing decisions** in a pre-update bound project for a behavior-preserving repair. Name the affected directories below the project root. The repair uses the project’s discoverable instructions or its bound governing sources. For a project with a current choice, the repair reuses the same implementation decision. If an earlier writable task lacks either a current choice or a bounded repair scope, re-prepare it from the saved objective and current inputs. The earlier task and its history remain available. This includes resume. A project-backed image request must pass its applicable phase before the provider call. The generated file still requires review. An unbound legacy scratch request keeps its original scope. [Workbench API](../../apps/agent-atelier/shared/API.md)
- **Ticket and document workflows.** Bind the choice to project-owned sources, include it in a specification that depends on it, and rerun change review and acceptance if the approved inputs or the exact artifact change. Existing low-level format, re-render and archive tools can operate on an unclassified historical record. Material production using those outputs requires the owning managed stage and its exact choice.
- **External or direct execution.** Follow the governing instructions and run the provided verifier before dependent work. The product can check supported executable routes and packaged instructions. Host commands outside them have their own execution and permissions. See the [coverage map](../../governance/production-choice-coverage.json) for the enforcement and proof boundary of each surface.

If verification rejects the task, read the specific cause and locate the project-owned record. Restore its authorized bytes when the change was accidental. For an intended change, record a new candidate or revision, evaluate the affected workflow and evidence, and obtain the applicable approval before retrying. Never rewrite the expected hash simply to clear an error. Keep old package and approved artifacts available for restoration.
