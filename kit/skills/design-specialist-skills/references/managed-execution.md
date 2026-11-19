# Managed execution for a generated agent

The bundled `assets/managed-model.json` identifies the standard model for new managed work. Carry it and this reference into each child skill. Use the supported host selector to choose the model.

For Codex, start the agent in its target project using the normal managed launcher or using `codex --model <id>` from that project root, with the exact bundled `id`. For a governed noninteractive run pass the same option to `codex exec`. Keep the approved working directory, permission profile and project data. Verify native session metadata for the actual task before crediting the observed execution. A launch argument records the requested model.

A role may inherit from a verified current session only when the native host supports that inheritance. Verify the child model from native metadata. Use the Work model picker when the authenticated host exposes the required model. If the host cannot select it or confirm effective use, record that capability gap and the exact supported route to the pending consumer. Keep preparing any unrelated permitted outputs.

Output language follows the current action, applicable project or surface preference, then English. Preserve quoted text, stable identifiers, commands, paths and existing handoff bytes. For an existing agent, consult its ownership and adoption record before changing its own pins, sources, or project configuration.
