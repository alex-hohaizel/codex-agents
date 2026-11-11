# Agent Atelier 0.3.1 to 0.4.0

Select the reviewed repository 1.4.0-rc.4 source revision. This is a local service update with the same SQLite and project state formats. Existing project bindings, jobs, task evidence, locale and retention settings keep their current records. Core and optional skills keep their existing bytes, so an already admitted installation needs no skill update for this change. For a new installation, follow the [6.1 migration](6.1.0.md).

1. Record the active launcher/source/build and check that all owned jobs and pending effects are reconciled. Preserve the service data directory with an actual backup and record the rollback source. A JSON store export does not back up private archived input files.
2. Build the candidate with the pinned lockfile and run the service checks.

```sh
cd apps/agent-atelier
npm ci --ignore-scripts
npm run check
npm test
npm run build
```

3. Test a separate data directory and port first. Use the real local Codex project registry and history. Check the active and archive page counts and open one existing project with recorded work. Inspect an installed app and read the metadata of a repository available to the current GitHub CLI login. In Connections, search for a public image and audio reference and verify the returned source and license metadata.
4. Stop the owned baseline instance and start the reviewed build with the same service data directory. Use the [launcher instructions](../../apps/agent-atelier/README.md) and keep one writer per data directory. Verify the service version, settings and original records. Leave native product state and the accepted interface design in place.
5. If the candidate fails before new work, stop it and restart the recorded 0.3.1 build on the retained store. When there is new work, reconcile it before restoring a backup so its records are preserved. No database migration is required in either direction.

The source release and installation are separate. See [release scope](../repository-1.4.0-rc.4.md) and [API details](../../apps/agent-atelier/shared/API.md).
