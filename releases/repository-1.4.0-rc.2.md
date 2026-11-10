# Repository 1.4.0-rc.2 — operator workbench design revision

The owner requested rework of the actual first candidate's visual foundation. This revision puts a human project overview, source-backed work map, selected result and next action at the center. The complete source/diff workbench remains available through an explicit tab. Earlier checks and source records retain their provenance; a historical QA task is not presented as current execution.

The workbench separates declared project work, actual service jobs, partial native history, returned answers and owner acceptance. One explicitly bound, required and hash-verified checkpoint can expose its declared current stage and next action. Missing or ambiguous checkpoint data stays unknown; the native project phase and authority are unchanged.

Core6.1.0, Orchestrator1.2.0, maintenance1.1.0, service0.3.0, all35 reusable sources and12 roles remain. No new framework, model policy, project migration or database schema is introduced. Existing icons, colors, bindings and role settings are preserved. See [implementation observations](../docs/evolution/2026-11-10/IMPLEMENTATION.en.md), [the component handbook](../docs/evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md) and [migration](migrations/6.1.0.md).

This remains an unadopted source candidate while actual design/runtime review and the remaining full-case gates are open. Exact CI42827961302 passed for the previous8c3a557 source only; it is not proof for these changed bytes. The new revision needs its own source, browser, package and CI observations. WORK remains deferred.
