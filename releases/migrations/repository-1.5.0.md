# Component migration for repository 1.5.0

Start with [the core migration](6.2.0.md) for managed local skills and the [current component record](../current.json) for the exact versions. Repository publication does not install a global skill or replace an existing product.

Agent Atelier source moves from 0.5.0 to 0.6.0. The native local API and database keep their existing schema versions. The optional updates manager reads a compatible declared component version from current skill metadata and retains the version heading fallback for legacy installations. Verify the optional preview and staged rehearsal before working with active settings.

Build and check the exact service revision with its lockfile. Use a disposable service data directory and loopback port to check the launcher, bindings, context, next actions, preserved versions and recovery. Compare existing source ownership and state. Use the same durable store only after the approved backup and ownership checks. Follow the [workbench operator instructions](../../apps/agent-atelier/README.md) and [launch contract](../../apps/agent-atelier/shared/LAUNCH.md). Restore a prior compatible build on rollback and reconcile any new records or unknown effects before restoring data.
