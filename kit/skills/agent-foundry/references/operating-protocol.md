# Operating protocol

Contents: scope → current inputs and state → blueprint → target construction → jobs → effects → pause → transfer.

## Tool scope

`scripts/foundry.py` is an internal Python CLI for versioned state, graph and coverage checks, source pins, approval, readiness, and recording observed results. It does not interpret natural language, produce domain content, call external tools, or grant authority. The agent interprets intent, researches the domain, supplies expertise, and performs actual actions. Every authority or evidence field must correspond to a real response or observation.

Before use, read `python3 -B <ACTIVE_SKILL>/scripts/foundry.py --help`, the relevant subcommand help, and the [record contracts](../assets/runtime-records.json). Substitute the active source path from the skill list. A path from another system is not a command the user can run. The standard local runtime requires compatible Python and POSIX locking. Report the operating systems and versions actually tested in the current QA record.

## Separate session roots

Select an explicit root and purpose for both the factory session and the product execution session. For an existing project, use a separate construction workspace that preserves product state and accepted packages. `init` creates a new ledger; it does not migrate arbitrary old records or select capabilities on the user's behalf. Preserve and pin authoritative files. Do not use a sidecar to turn an earlier refusal into a new approval.

After import, verify raw bytes, versions, rights, and source. Separate historical metadata from current authorization. Check archive paths, symlinks, and resource limits. Do not execute inbound code. Transfer large materials in bounded parts or through versioned artifact storage with hashes and a recipe. Retain originals and verification.

## Passport before the gate

Populate the actual blueprint according to the [architecture contract](architecture-contract.md). Bind capabilities, the phase DAG, roles, components, outputs, tests, discovery applicability, questions, and constraints. Phase count does not determine skill count. Structural validation is necessary. A human and a reviewer verify domain completeness and quality.

Present the readable passport and component list **before** producing target skills. Pin approval to the exact blueprint ID, revision, content hash, scope, and actual source of the affirmative response. A filled template is not approval. If material content, dependent knowledge, or authority changes, assess impact and reopen the affected decision. Negative, pending, revoked, or stale approval blocks the build.

Run the current `build-gate` before authoring, before an expensive dependent job, and before packaging. It admits a specific construction scope and does not run work on its own. After the gate, use Skill Creator and the relevant domain tools to build actual outputs, run QA, register artifacts and evidence, and check the bundle against the approved entry, skill set, and coverage. An empty or incomplete template is not a ready target.

## Execution by the generated agent

Product execution needs an actual grant identifying the current goal, boundaries, and phase IDs. The same response may authorize construction and execution if the user clearly requested both. Preserve the granted scope. Acceptance of the blueprint does not authorize execution by itself.

For each work unit, state its concrete goal, owner and skill, current source, exact inputs and dependencies, phase prerequisites, requirements and decisions due, evidence, capabilities, outputs, limits, and stop condition. Check `readiness` before `start`; call `complete` after the actual output, proof, and closure. A pending requirement can be the task's subject and need not block task creation. Close it before claiming fulfillment. Omitting a `depends_on` edge does not bypass phase readiness or scoped prerequisite evidence.

Pin outputs, proof, and dependencies at completion. Reopen affected work and reviews if bytes, knowledge, source, or permissions change. If independent review is required, give it an explicit gate; a bounded self-check is separate evidence. Apply newly discovered domain requirements to their specific acceptance conditions and due gates.

## External effects

Prepare a concrete reviewable result. Verify the actual capability, environment, target, outputs, hashes, parameters, and current positive authorization. Effect approval is distinct from blueprint approval and execution permission, and must identify the exact scope and bytes. Approval of a no-action option does not authorize an effect.

Record pending dispatch, make one actual tool call, then retain the actual receipt or provider proof. The Foundry CLI does not execute the effect. On error, missing receipt, or unknown outcome, reconcile through read-only status before retry. Use provider-supported idempotency or deduplication when available. A local ledger does not guarantee distributed exactly-once effects.

## Pause, context, and reopening

Check stop state before a dependent action. A stop marked now blocks new jobs; a future stop identifies the exact artifact or phase boundary. Restating the task or setting a future stop does not clear an active pause. Safely record a returned receipt or checkpoint during the pause. Start no new job while the stop applies.

Keep a readable current brief: completed, current, and pending work; exact source and blueprint versions; questions and gaps; actual jobs and effects; limits; and the next permitted action, host, and return path. Load current records and relevant sources. The brief does not supply automatic semantic memory across projects. Before resuming, check files, hashes, knowledge, permissions, and external outcomes. Do not repeat completed effects.

An incident, small change, or new knowledge reopens the affected part of the workflow. A suite change needs a compatibility review and stated impact. Routine compatible cleanup needs no new intake. Ask for a concrete decision if capability, rights, quality, or cost changes materially.

## Delivery and manual return

Give each required transition a readable packet containing actual files, hashes, checkpoint, and authority; concrete launch steps and working path; argv or verified UI actions; expected outputs and receipts; and return validation. Isolate the specific scope blocked by an unavailable capability. Offer the user one clear next action without asking them to choose internal modules or repeat known sources.

Interpret CLI exit and status results according to actual help and the record contract. A successful state write only verifies the record. User approval, tool effects, artifact quality, and live product behavior each need relevant evidence.

## Production admission and checkpoints

Before a work unit, verify operation and recipe IDs, which material parameters the current operation supports and consumes, the consumer, and the resources. Record maturity, depth model path and hash, operation, recipe and attempt references, reserved unknown cost, assembly and evidence gaps, and the exact next validator. Keep attempt data in the project ledger. Reusable source must not contain current provider IDs or secrets. A change in recipe, semantic inputs, importer, target profile, or rights reopens dependent outputs and proofs. Preserve the source master unless the change requires it. After two identical repairs without progress, change the hypothesis or report the specific blocker. On resume, reconcile unfinished effects before continuing with the authorized node.

## Concise review for the owner

At a material milestone, prepare a [read-only overview](interaction-protocol.md) from current state. For a minor repair, show the actual diff, check, and result without a new product cycle. Carry existing authorization within its exact scope; no local state or template grants additional authority. Show the owner decisions and their consequences. Keep technical details and raw traces available when needed.
