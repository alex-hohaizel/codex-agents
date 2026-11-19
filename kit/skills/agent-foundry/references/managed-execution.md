# Managed execution for a generated agent

The bundled `assets/managed-model.json` identifies the model ID and reasoning effort for new managed work. Carry it and this reference into each child skill. Use the supported host selector for both values.

For Codex, open the target project with the managed launcher. From the project root, the equivalent selector is `codex --model <id> -c 'model_reasoning_effort="<reasoning_effort>"'` with the exact bundled values. For a governed noninteractive run, pass the same options to `codex exec`. Keep the approved working directory, permission profile and project data. Verify the actual model and effort in native session metadata before crediting execution. Launch arguments record the requested settings.

A role may inherit from a verified current session when the native host supports that inheritance and no role or spawn override can replace either setting. Verify the child's model and effort using native metadata. Use the Work picker when the authenticated host exposes the required settings. If the host cannot select or confirm both, record the capability gap and the supported route to the pending consumer. Continue unrelated permitted work.

A lower reasoning effort requires an explicit scoped requirement and reviewed evidence of preserved quality and a meaningful timing improvement on the same case. Record historical replays with their original settings. For an existing agent, consult its ownership and adoption record before changing its pins, sources or project configuration.

Output language follows the current action, applicable project or surface preference, then English. Preserve quoted text, stable identifiers, commands, paths and existing handoff bytes.
