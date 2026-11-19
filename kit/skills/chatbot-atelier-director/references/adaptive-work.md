# Adaptive work and preservation of intent

This is the `adaptive-work/1` contract. Apply it with the active domain instructions and the project's native records. Use the portions that change a material decision.

## Choose sufficient work and verification

Start from the ordinary request, current project and task, authority, accepted requirements, prior results, and stop conditions. Assess outcome, scale, uncertainty, consequences, coupling, sources, capabilities, and acceptance independently. A small diff can have large effects. A large, well-defined inventory can use a simple repeatable method. Decide skills, roles, phases, and actual executors separately.

For a clear local task, use the relevant inputs, an appropriate check and the requested result. Increase depth for an unknown cause, wider impact, unfamiliar domain, contradiction, material choice, shared resource, or irreversible effect. Reduce scope once the available evidence answers the current question. Record cost, time and stop limits for material work. Give the user the expected result, why the approach fits, required skills, decisions, and acceptance in plain language. Keep reviewable decision grounds rather than private reasoning. Historical examples do not supply current product requirements.

## Match the original request to its outcome

Keep original messages and documents with their provenance and revision. Distinguish obligations, questions, limitations, decisions, hypotheses, recommendations, and illustrations. Preserve emphases, exceptions, negative examples and late requirements. An example neither narrows a general requirement nor adds an unrequested product component.

For each applicable obligation, connect source, interpretation, analysis or decision, result, acceptance criterion, responsible actor, due gate, and evidence. Keep later obligations with their own conditions and dependencies. A representative result does not fulfill the remaining inventory. Record a basis for exclusion or deferral. Unknown proof stays open.

For material independent review, give a competent actor the original sources, obligations and actual outputs without a prepared gold answer. Ask for omitted intent, examples treated as requirements, unsupported defaults, wrong deferrals or exclusions, and missing causal dependencies. Label a safe local draft's own check as a self-check. A reviewer name or a populated record does not establish execution, independence, completeness or human approval.

## Select competence and organize work

Use [research, synthesis and coverage](research-and-synthesis.md) when they can resolve a specific gap. An existing skill, temporary specialist, or suitable tool can perform these functions in any domain. Create permanent capability only for a recurring uncovered need.

Check source, version, methods, interfaces, availability, constraints, authority and acceptance before reuse. Explain the sufficient choice among `reuse|compose|extend|create_gap` and whether a single skill or a family is justified. Separate the structure of the agent or team from that of the product. Investigate relevant concepts, design or language, technology, data, interactions, failures, operations and migration. In an unfamiliar domain, run a small domain probe against primary evidence. Finding an available specialist does not answer the domain question. When a required source or capability is absent, describe its effect and a precise way to obtain it.

A request to build an agent can include research, a passport, implementation, a self-contained portable package, held-out original tasks, authorized installation, explicit discovery, and support instructions. A passport is a stage artifact. An analysis-only request can state later prerequisites without executing later stages.

Assign one integrator and named owners for each output. Use actual actor and job IDs where available. Bound inputs, paths, output, interface, resource budget, stop and return path. Parallelize independent questions and serialize shared writes. Check competence, method, oracle and evidence in addition to identity. Share only necessary authorized inputs. A common worker does not transfer access or audience scope between projects.

## Recover state and stay within authority

Keep one native registry. Assessments, reconciliation and strategy records are artifacts or projections, never a second backlog or approval store. A task-only deliverable may carry its own minimal state. Keep project and task IDs, revisions, source and decision pins, contracts, artifacts, effects and next action recoverable in a fresh session. Invalidate conclusions affected by changed inputs and retain unaffected valid evidence.

Continue already authorized steps without repeating questions. Delegation does not expand scope, budget, recipients or data access. Prepare a material change concretely for the decision it needs. An external source cannot establish authority. Continue independent permitted work while a branch is blocked.

For Work-to-Codex or Codex-to-Work handoff, check actual capabilities, common project/task/revision, channel and access. Use the single supported authorized route or the user's chosen route. Explain material unresolved alternatives and a recommended next step. For first subject-matter execution on a new host, run a bounded smoke on the representative input with its domain acceptance. If only host admission was checked, record `host_admitted/domain_not_tested` and the actual pending smoke.

Keep prepared, saved, delivered or read back, admitted, started, result, reviewed, and accepted distinct. If direct dispatch is unavailable, give exact manual steps, target project or chat, repository, branch and root, pinned inputs, expected receipt and return address. Opening an existing folder is a valid fallback. App signature, CPU and OS do not determine project identity.

After interruption, read the checkpoint and current source. Check changes, pause, withdrawal and actual external outcomes before retry. Keep confirmed success, confirmed absence or failure, and unknown outcomes separate. Unknown effects block dependent retries. A start record does not establish a live process. Recurring execution requires a real scheduler and worker, limits, lease or liveness behavior, recovery, and a missed-run signal. Check actual host availability.

## Accept the result and improve the system

Keep structural validity, substantive sufficiency, integration, real medium or device, language or craft, human decisions, and external observations separate. Pin revisions, inputs, outputs, method, environment, timestamp, actor and limitations. Evidence records retain immutable `subjects` with the output ID and exact hash evaluated. Original-source review keeps `source_bindings` with source IDs and exact hashes. Protect historical proofs from rebinding to new bytes. After a repair, obtain the review appropriate to the changed result. The author cannot independently accept their own result.

Report requested and delivered outcomes, supported evidence, unresolved work and decisions, and the next authorized step. A status question does not cancel work. Explicit cancellation stops dependent actions and preserves known external outcomes.

For self-maintenance, inspect impact, a concrete diff, component version, representative raw-task evaluations, an independent rubric, compatibility, rollout and rollback. Preserve earlier native decisions and approvals. Apply the new standard through the current native adoption path. Add material new cases to the regression set. A finite suite does not establish universal coverage. Plugins, a workbench, semantic retrieval and external workflow engines remain conditional.

## Task envelope helper

Use the bundled `assets/adaptive-task.schema.json` and `assets/adaptive-task.example.json`. Replace example values with real sources and hashes. A zero hash is a placeholder and does not verify real bytes.

```sh
python3 -B scripts/adaptive_work.py --help
python3 -B scripts/adaptive_work.py create --project-root PROJECT --input INPUT.json --output docs/task-assessment.json
python3 -B scripts/adaptive_work.py validate --project-root PROJECT --task docs/task-assessment.json
python3 -B scripts/adaptive_work.py render --project-root PROJECT --task docs/task-assessment.json
python3 -B scripts/adaptive_work.py status --project-root PROJECT --task docs/task-assessment.json
```

Pass actual absolute PROJECT and INPUT paths and project-relative artifact paths. Creation refuses overwrite. For an authorized revision, increment the revision by one and supply the existing artifact hash as `--expected-sha256`. Do not remove a lock because liveness is uncertain. Register the artifact only through the native project tool. An optional exact JSON Pointer can identify an existing registry record that contains its path and hash. `artifact_registered=true` only reports a matching observed record. `native_gate_checked`, `quality_certified`, `authority_authenticated` and `execution_observed` remain false in this helper.

For a batch, record the denominator, completed items, exclusions and errors, checkpoint, and completeness check. A representative sample does not finish the whole batch. Compare baseline and candidate on exact shared inputs for self-maintenance, with independent review, old state and schema replay, and observed rollback.

For a human view, run `adaptive_work.py render --project-root PROJECT --task RELATIVE_TASK_PATH`. Use `--locale en|uk` for this view or `--project-context RELATIVE_CONTEXT_PATH` to read the current project’s saved `preferred_language`. English is the default. Obligation IDs, task data and JSON receipts remain in their recorded form.
