# Agent Atelier 0.4.0 to 0.5.0

This service update uses the existing SQLite and native project formats. Current skills and the host profile remain compatible. For an initial skills installation, use the [6.1 migration](6.1.0.md).

1. Identify the running build and its data directory. Reconcile ongoing work and keep a backup of the data directory before replacement.
2. Build the exact candidate and run its checks.

```sh
cd apps/agent-atelier
npm ci --ignore-scripts
npm run check
npm test
npm run build
```

3. Use a separate test data directory. Check that the next action fills the objective, then edit the draft and review the route. In Connections, verify OpenAI Docs results and preview a PNG from the supported native Codex image route.
4. Stop the owned service, start the reviewed build on the same data directory, and verify existing settings and records. [Launcher instructions](../../apps/agent-atelier/README.md)
5. If startup fails before new work, stop the candidate and start the retained 0.4.0 build on the existing store. If there are new records or an unresolved external operation, reconcile them before considering backup restoration.

[Release scope](../repository-1.4.0-rc.5.md) · [API](../../apps/agent-atelier/shared/API.md)
