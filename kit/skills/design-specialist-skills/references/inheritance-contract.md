# Preserve requirements in generated skills

The constructor provides an executable domain method. Each child has a contract in the blueprint and its own self-contained manifest. The same requirements apply to a single skill and a family.

## Minimum child contract

- Give the child and stage stable IDs, a precise trigger, domain, user, result, and consumer. Trace all inherited and local requirement IDs to their sources. Preserve every must when paraphrasing.
- Define needed inputs and maturity, `applicable`/`absent_by_design`/`blocked`, typed interfaces and units, state and authority, permitted effects and permissions, and the task boundary. Specify actual domain-state rules, formulas, and expected outcomes where relevant.
- Define the ordered workflow with entry and exit criteria, competence and actual ownership, tool and recipe bindings, evidence types, budgets, self-checks and independent review, local acceptance, and return upstream.
- Trace sources, editable masters, and runtime derivatives where applicable. Store live jobs, credentials, and checkpoints only in the appropriate project state.
- Assign case IDs for applicable normal, boundary, failure, retry, and cold-return scenarios, with exact fixtures and oracles and a negative case. Use a reviewer with relevant competence for semantic acceptance.
- Define the handoff format and consumer, affected dependency closure and invalidation, what carries forward, repair escalation, recovery, stopping and end-of-service, and the next action. Claim persistent monitoring only when an authorized mechanism actually runs.
- Discover and assess reuse before adding an engine or materially expanding scope. Check current host metadata and approved sources, read exact source and record version and hash, then assess capabilities, inputs, outputs, stages, compatibility, permissions, limits, and fit. Record `reuse|compose|extend|create_gap` with a rationale. Consider new specialists beyond the known catalogue and inspect source when no capability card exists. Flag archived, duplicate, and stale candidates and verify counterparts separately for each host. Track availability, installation, source inspection, and actual invocation separately. Confirm permissions, costs, and effects for the selected operation.
- Include complete local `briefing/1` for BRIEF (`БРИФ`), RESUME (`ВІДНОВИ`), and stage closeout, using current `references/briefing-protocol.md`, domain guide and topics, and intake, execution-script, and closeout templates. If a controller is used, bundle `scripts/briefing.py` and its dependencies. Adapt topics to the child's domain while preserving the protocol. RESUME reconciles actual files, hashes, authority, and unknown effects. Closeout records proven scope, outputs, evidence, limits, unresolved work, checkpoint, and next action, stop, or return. Keep authority tied to its source.

For a small analytical skill these requirements can fit in a few precise sections. Add HTTP, a database, a server, or a custom validator only when the domain requires it. Code, integration, and deployment need their corresponding contracts and execution evidence.

## Verify inheritance

1. Reconcile every parent requirement ID with a child assignment. Record an accepted domain rationale for each N/A. Missing tooling is blocked.
2. Match each child output to its actual consumer and acceptance. Resolve gaps that would force the consumer to invent a rule.
3. Review the concise `SKILL.md`, metadata, and family handoff for lost constraints. Bundle the content that the child needs locally.
4. Use a fresh context with the raw task and required files. Keep the diagnosis and expected results with the reviewer. Run bounded positive and negative cases without live mutation. Store measured outputs separately from reusable examples.
5. Revise the blueprint when an extension changes a material goal, budget, external effect, or product choice. Bind actual approval to the change. Use existing authorization for routine repair inside its scope.
6. Verify self-contained discovery and reuse and `briefing/1` in a fresh context. Cover a previously unknown specialist, missing capability card or counterpart, ambiguous or stale source, cold resumption, and phase closeout. Pin required local content, scripts, and templates in the manifest with hashes. Verify that uninstalled siblings are unnecessary. A generic specialist consumes a bounded project task or handoff. Apply app or chatbot validators only to their supported domain.

Record child acceptance for the specific assessed scope. Assess each later product and novel task using its own evidence.

## Inherited interaction workflow

Keep one current domain registry, a short view of the goal, verified work, current activity, gaps and needed decisions, and exact continuation. The owner makes material choices and accepts stage results. Routine work uses the current scope. Reuse valid approvals across calls and reopen affected dependencies after a change. Record specification, code, integration, device, and human acceptance separately. Stop at the terminal scope.

Read current `references/interaction-protocol.md`. The supported read-only view can use `scripts/interaction.py` and `assets/status-view.schema.json`. For another domain state, implement and verify its own adapter or equivalent projection. Confirm availability through actual operation. Maintain the single project authority and backlog. Background operation requires a separate running mechanism and authorization.

Where applicable, bundle the protocol, `assets/decision-card.template.md`, tool compatibility and the actual helper and schema used. Pin versions and hashes and test with a receiver who starts without the prior context. Adapt to the actual domain and engine. Verify the package's runtime, models, and permissions on the target host. Track actual tool execution, independent domain review, and the owner's response separately from structural checks.

## Portable operating standard and visual continuity

Each generated child includes exact current local copies of `references/adaptive-work.md`, `references/research-and-synthesis.md`, `references/visual-identity.md`, `references/joint-work-codex.md`, `scripts/adaptive_work.py`, `scripts/visual_identity.py`, `assets/adaptive-task.schema.json`, and `assets/adaptive-task.example.json`. Link the four references from the entry point and apply them in the specific domain. Retain the child's own depth and workflows. Before saving, run the constructor's `scripts/check_generated_inheritance.py` against each child root and the portable output. Separately review coverage of raw sources and actual behavioral cases. See the complete operating standard below for all current resources.

Assess scope, uncertainty, consequence, and coupling separately. Reconcile musts, questions, examples, and hypotheses with their sources. Show the strategy and responsible competences, with due gates for later requirements. Transfer an arbitrary competence as a bounded task. Typed App and ChatBot routes are additional adapters. Use methods from `research-and-synthesis.md` as needed, with the smallest effective structure and team.

Give new project agents a distinct `project` identity. Create an icon only when no current icon exists. Preserve current paths, bytes, and `brand_color` across releases. Pin new project identities using `visual-identity.md`. Updating an existing agent reconciles actual state and compatibility, retains existing IDs, approvals, and outputs, and records the actual date and scope of new review.

## Lock the child's visual identity

Choose the class from the purpose in the accepted scope, independent of the installation location. A project-specific agent has `class=project` and a new project-card-v1 where an icon is needed. A reusable tool or system competence has `class=system` and follows the system style, including when installed in a single project. Authorize external actions independently of class. Reuse the accepted task for routine classification.

For `class=system`, record `scope=reusable_system` and `scope_basis={source,reason}` in origin using the accepted task. The record establishes classification. A new system icon also records `style_reference={path,sha256}` for an actual separate sample of the system style in `assets/`, pinned in the manifest. Inspect the visual match independently of byte and link checks. A project card retains its own class, and the generated icon requires a different source sample.

For an existing icon, preserve its actual prior snapshot, class, paths, bytes, and brand color. `freeze --class system|project` must match its existing class. Set origin `kind=preserved` and pin the actual prior snapshot. Keep the source basis `reusable_system` for system specializations. Preserve identity during routine updating and project-local placement. The installer rejects a class change until an explicit migration of scope. Compare the prior snapshot and class without rewriting prior evidence.

For a new project-specific icon when existing icon references and assets are absent, run `scripts/visual_identity.py create-project --root CHILD --glyph XX`, then bind `interface.icon_small` and `icon_large` to the returned path. Write the actual `freeze --root CHILD --class project` JSON to `assets/visual-identity.lock.json`. Set `assets/visual-identity-origin.json` to `{"schema":"visual-identity-origin/1","kind":"created"}`. The gate checks the SVG project-card-v1, class, and bytes. Inspect actual legibility separately.

For an existing icon, preserve the original appearance and store an authentic prior freeze as a local source artifact, such as `assets/visual-identity-prior.json`. Record its SHA-256. Origin uses `kind=preserved` with `prior_snapshot={path,sha256}`. The current lock must match that prior snapshot. Record the actual source observation in the project registry and inspect provenance in semantic review. Mark a new icon as created.

## Production, context, and AI operating resources

Use the `RESOURCES` and `ENTRY_LINKS` declared by `scripts/check_generated_inheritance.py`. Bundle the listed resources and link the local references from the actual entrypoint. Choose the applicable medium profile and preserve the defining reference mechanisms, identity, functional depth, and exact task context. Accept a representative slice on the actual medium before scaling. Record semantics, craft, authorization, and runtime proof separately. For an existing agent, compare exact source and target and test the affected workflow in a fresh context.

For the current generated-agent standard, inherit the [managed execution contract](managed-execution.md) and exact release model policy in each child. Verify effective use in the target consumer.
