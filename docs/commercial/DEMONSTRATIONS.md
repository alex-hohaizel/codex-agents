# Observe the actual candidate

These are controlled runs of the agent system with existing host prerequisites,
not conceptual illustrations or a claim about every environment.

## Buyer installation and first result

[Short video](../../commercial/media/Buyer-Install-and-First-Result.mp4)
records real execution in a labeled local process viewer. The viewer is demo
instrumentation, not an advertised product setup interface. It invokes the
packaged setup, verifies installed files, requests a fresh native catalog and
executes the first task through the installed Orchestrator. The observed run
took 52.429 seconds on Apple M1 with macOS27.0.1, installed Python3.13 and an
already authenticated Codex0.166.0. This does not include creating a Codex
account or installing prerequisites and is not a universal timing claim.
[Exact recording provenance](../../commercial/media/BUYER-DEMO-PROVENANCE.json)

To reproduce, obtain and verify the buyer archive, select an empty test user's
home through setup, then run audit/install/verify/discover. Copy the first-task
fixture to a disposable project and use the installed Orchestrator to correct
the heading. Compare every other byte and notes.txt before/after. Use the
generated native launcher when role registration is needed. An ephemeral CLI
session can execute a direct task; a persisted session may be needed when
this host must look up its parent record for real subagents.

## Source-linked planning

The [copyable input, exact task and recorded outputs](../../commercial/examples/dock-planning/README.md)
make this scenario reproducible. In a separate small project, supply owner notes for a loading-dock reservation:
one confirmed booking per slot; the same request identity replays the same
reference; another coordinator gets a conflict and can select another slot.
Ask Orchestrator and App Atelier Specification to produce a PRD and architecture
with separate source-linked R-101–103, two Builder scopes, QA criteria and a
continuation record. Keep hosting and model budget unresolved unless chosen
by the owner. Check that planning output does not claim a deployment or
completed reservation service. The release acceptance report retains the
actual output hashes, runtime events and independent content review.

## Screenshots and runtime

The three [workbench images](../../commercial/media/WORKBENCH-PROVENANCE.json)
come from the real prebuilt server and client with authored clean fixture data.
No personal native history was connected. Their source and runtime hashes are
preserved. The original campaign images remain explicitly illustrative.
