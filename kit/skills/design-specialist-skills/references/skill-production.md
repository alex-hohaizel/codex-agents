# Producing a specialized skill

## Records and execution

Use one project-owned blueprint or linked manifest to trace stable IDs from requirement through domain contract, operation, recipe, attempt, assembly, and evidence. Record the digest and dependencies of external JSON and sources. Keep one authoritative record of intent. The [common core](cross-domain-core.md) specifies evidence and execution records. This document adds skill-production requirements.

For each capability, specify the exact operation, tool, model, host, target, version, parameter schema, supported inputs and outputs, editable source, limits, permissions, data, cost, unsupported flags, verification of material parameters, and fallback. Track descriptor, schema, catalogue, configuration, testing, and integration separately. Inspect actual outputs to establish suitability.

Each recipe records the exact accepted inputs and hashes, competence, owner, consumer, ordered steps or dependency graph, bound argument array or API operation, or numbered GUI steps. Include output formats, masters and derivatives, transformations, validators and oracles, budget and effect scope, repair, and stopping conditions. Bind a template to the project and real toolchain before execution. On API timeout, reconcile an unknown external result by request or effect ID before deciding whether to retry.

Allocate an attempt and effect identity before the side effect. Record input, toolchain, and recipe digests, actual arguments, seeds where supported, job and run references, append-only observations, actual outputs and hashes, cost, and evidence produced. Keep run-specific values outside the reusable skill. Assembly records the exact package, version and configuration, components, executed scenario, expected and observed results, actual authors and reviewers, evidence type, and unresolved gaps.

## Production recipes

### R-SK1 — turn requirements into a domain contract and skill

- **Input.** Accepted requirement registry, vocabulary, current capabilities, constraints, and authorization scope.
- **Steps.** Assess applicability. Select a primary method. Write typed contracts and scenarios. Define the stage, competence, and consumer. Build the child `SKILL.md` and resources. Resolve local links and CLI references, and verify lineage. Run positive and negative cases and hand off to a receiver without the prior conversation.
- **Output.** Installable source, child manifest, exact test and review records, gaps, and next action. Preserve musts, scope, permissions, and rejected simplifications in the transformation from source to instructions.
- **Acceptance.** The receiver completes the example with defined rules, rejects the counterexample correctly, and reconciles all inherited IDs. A runtime requires its own scope.

### R-SK2 — turn a skill family into independent stages and handoffs

- **Input.** Exact stage graph and contract ownership.
- **Steps.** Identify actual boundaries for artifacts, access, and independent reuse. Assign a single owner to each authority. Bundle self-contained, versioned common resources. For each edge define input and output format, hashes, consumer validation, and the conditions for failure or reopening. Verify the package without sibling paths or conversation history.
- **Output.** Independently installable skills, shared manifest and lineage, a positive handoff, and negative cases for missing and stale dependencies.
- **Acceptance.** The downstream stage reuses accepted research and rejects incomplete upstream work. Returning work upstream retains decisions and originals and reopens the exact affected IDs. Install only the skills required by the scoped work.

### R-SK3 — change, verify, and save in Work or Codex

- **Input.** Current skill and blueprint, exact user request, accepted originals, versioned backup, and actual operation capabilities.
- **Steps.** Inventory the current source before editing. Review the semantic diff and preservation of coverage. Copy required reusable resources. Run `quick_validate`, consistency checks, and domain tests as appropriate. Have a separate actor test the bounded task using raw input. Save a single supported skill operation through the native Skill Creator in Work and read back the exact saved content. For Codex export, package the same sources with a manifest and hashes and provide audit, apply, verify, and rollback procedures. Keep project data and production outside the export operation.
- **Acceptance.** Each must survives. External effects remain within authorization. The skill works independently of unbundled siblings. Revalidate affected outputs before carrying forward readiness. Confirm the actual saved Work version before reporting its update.

## Evidence and changes

Separate schema, byte, reference, and arithmetic checks from domain semantics, source accuracy, user experience, perceptual quality, actual deployment, and operational results. Establish independence from actors and artifact provenance. Each generated child needs its own cases and acceptance evidence.

After a change, follow affected dependencies through semantic inputs, source, model, exporter, toolchain, platform, and configuration versions. Carry evidence forward only for an explicitly unaffected scope. A stale receipt cannot prove the changed result. Two identical unsuccessful repair attempts require a different causal hypothesis and investigation. Set a budget and stopping condition. On stopping, leave a checkpoint with actual files, version and hashes, completed, pending, and blocked work, any unknown external outcome, and the next action.
