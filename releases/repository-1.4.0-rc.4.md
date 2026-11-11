# Repository 1.4.0-rc.4 and Agent Atelier 0.4.0

Refresh the portfolio to discover the registered local Codex projects, including projects with no chats. The panel reads the local registry and the active and archived thread streams separately. It reports source coverage and shows when more pages are available. Open a project to read its actual recorded work. Native projects that share a folder keep separate history and remain read-only where folder-based control would be ambiguous. Codex remains the authority for chat state, project identity and capabilities on other hosts.

Connections lists installed plugins and apps, their observed status and available tool summaries. Use the existing GitHub CLI login to read repository metadata. Search Openverse for public image and audio references with source and license links. Native-only provider actions have a handoff for the target Codex chat. This release preserves the accepted workbench layout and adds no model turn, plugin installation or paid generation during discovery.

Core 6.1.0, Orchestrator 1.2.0, maintenance 1.1.0, all 35 skill sources and the 12 role configurations keep their existing versions. The panel uses the existing store schema and permissions. The [service guide](../apps/agent-atelier/README.md) describes the new routes. Use the [update and rollback procedure](migrations/repository-1.4.0-rc.4.md) for this candidate.

This release is scoped to the personal Mac. Full 29-case acceptance and WORK remain open under their existing scope.

## Real checks

On the local Codex installation used for verification, the native registry returned eight projects, including one without chats. The active index returned 486 records across five pages. The archive returned an empty page. A project with 105 chats retained its identity across incremental discovery. A selected older chat returned 30 turns and 29 observed responses. These counts describe the tested local installation at the time of the check.

The panel read a real installed app's tool catalog and a repository through the existing GitHub CLI login. Public image and sound searches each returned ten results with source and license links. Desktop and mobile browser checks exercised selection, keyboard access, source links and the native handoff. Fixture tests cover empty and archived project data, shared roots, stale project assignments and authorization at the new HTTP endpoint.
