---
name: release-handoff-review
description: Turn a supplied small-project change and its actual observations into a concise release handoff with open decisions and recovery steps.
---
# Release handoff review

Use only the project facts supplied in this chat. Ask for a missing release
identity or material requirement when it prevents a useful handoff. Preserve
the owner's language, exact requirement IDs, permitted scope and unknowns.

Produce these five sections:
1. Target: project, candidate version or commit, audience and intended change.
2. Checks: requirement, expected behavior, actual observation, and evidence
   reference. Keep a test proposal separate from a result that actually ran.
3. Open decisions: unresolved behavior, missing access, source disagreement
   and who must decide. Do not convert an unknown into a pass.
4. Delivery: files or results to hand over, the specific next allowed action,
   and approvals still needed for an external change.
5. Recovery: previous known state, backup or journal identity, how to read
   back an uncertain result, and when to stop for reconciliation.

If no tools are available, review the supplied text and clearly state that
you have not inspected files, executed code, used a provider or deployed.
When tools are present, use only those authorized for the current task.
Do not claim installation of roles, lifecycle automation, or the full local
Codex Agent System. This self-contained coaching export can be used without
local resources or a server.

Example input:
Candidate 1.2 at commit abc123. R1 requires a unique reservation reference.
Two requests returned the same reference, per test report T1. Browser
conflict recovery has not run. Previous version is 1.1; backup B17 exists.
Local review only.

A correct handoff reports the observed replay check, leaves browser recovery
open, retains the candidate and backup identities, and proposes the next
review. It does not claim a production rollout or complete acceptance.
