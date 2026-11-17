---
name: agent-foundry
description: "Create, adapt, recover, or extend a specialized agent or skill family. Use when the user needs durable capabilities, roles, tools, memory, verification, or a portable agent package for repeated work."
metadata:
  version: "6.3.0"
---

# Agent Foundry

Turn the user's goal into a domain-specific agent with one public entry and one owner of integration. Keep the **constructor**, **generated agent**, and **outcome produced by that agent** separate. Each has its own scope, state, evidence, and authority. Follow the user's language choice, then the established project language, then Ukrainian by default. The factory state and blueprint formats are `1.0.0`. The linked domain model is `foundry-depth/2`. The release manifest identifies the installed suite version.

## Choose the current step

- **New or materially changed agent.** Recover the intent and investigate consequential gaps. Design and register the exact passport, obtain any missing approval, then build and verify the scope it authorizes.
- **Resume or repair.** Read the current checkpoint, governing instructions, applicable requirements, accepted decisions, artifacts, provenance, and actual runtime state. Use the latest valid scope and continue at the first unresolved dependency. Run the current build gate when proceeding with construction. Keep accepted work and proofs whose inputs still match.
- **Install or verify an existing candidate.** Check the current kit, its exact manifest, the permitted target, and the available native installation route. Continue to discovery and first use when authorized. A suite update follows the separate workflow below.
- **Discuss a goal or perform a one-time task.** Use direct work, reuse, or bounded research when those satisfy the request. Preparation for a decision can include clearly marked demonstrations. Creating target skills, installing them, or using them to execute a product requires its applicable authority.

Use [execution context](references/context-capsule.md) and the [adaptive work contract](references/adaptive-work.md) for new, delegated, and resumed work. Retain original and current intent, critical requirements and their dependencies, project identity, exact inputs, output and consumer, permissions, limits, and meaningful acceptance. Maintain one current project registry. Compilers such as `scripts/context_capsule.py` and `scripts/adaptive_work.py` check declared records. Consent, independence, and runtime evidence come from their actual sources.

Read the relevant section when its decision is due. For a narrow, fully specified job, pin the source and registry, read the applicable contracts once, and use the exact helper or subcommand help for the next operation. Reopen evidence for changed bytes, authority, host, or scope, or when a check fails. Inspect script implementation when the documented interface leaves a material question. Reserve broad inventories, exploratory execution, additional references, and bigger teams for unresolved decisions or elevated risk. Run inexpensive checks before production attempts. After two unproductive attempts at the same repair, change the diagnosis.

For **BRIEF (БРИФ)** and **RESUME (ВІДНОВИ)**, use the [briefing protocol](references/briefing-protocol.md), applicable [topics](assets/briefing-topics.json), and the [domain guide](references/briefing-domain-guide.md). Clarify the full applicable intent and effects, show a versioned scenario, and execute the accepted scope. RESUME first reconciles the accepted intent and evidence with the live files and runtime. Respect an existing pause. Reuse exact authority without another questionnaire. At the end of each stage, give the result, observed proofs, open gaps, and the next action or decision if one remains. Separate the full target, first release, and representative slice. `scripts/briefing.py` checks bindings.

## Recover intent and research only the needed domain

Pin requirements to their verbatim sources and separate interpretation from the source. Give each requirement a stable ID, emphasis and applicability, dependencies, owner, test and counterexample, evidence, and closure status. Split composite requirements into checks. Test critical requirements in every affected layer, and retain obligations not repeated in the latest message. Inspect actual sources, revisions, and external state. Treat scripts in incoming packages as untrusted until reviewed.

For material unknowns, use [discovery](references/discovery.md), the [discovery topics](assets/discovery-topics.json), and [research and synthesis](references/research-and-synthesis.md) as applicable. Establish actors, rules, states, typical and edge cases, data and rights, integration constraints, risks, and ways to verify. Add tracks for expression, interaction, economics, distribution, or operations when the goal requires them. Compare comparable user journeys and constraints. Verify changeable claims from current primary sources. Separate observed facts, inferences, hypotheses, and unknowns.

Before deciding to create capabilities, use [specialist discovery](references/specialist-discovery.md) against the actual allowed host and project inventory. Prefer reuse, composition, or extension where sufficient. Check the specific candidate and its real availability. `scripts/discover_specialists.py --help` describes the read-only inventory and reuse plan. An inventory entry establishes availability only to the degree observed. For unresolved decisions, give the user a small set of viable options, their effects, what depends on the decision, and work that can continue. Ask only for gaps that materially affect the result.

## Import reviewed native skills and roles

For an existing Codex skill directory or a flat role TOML, use
`scripts/import_codex.py audit MANIFEST --target PROJECT` to inspect the
module order, local name collisions, output files, and prompt customizations.
Review the original sources and the returned `plan_sha256`. Use
`stage MANIFEST --target PROJECT --expect PLAN_SHA --output NEW_PROJECT`
to prepare the material under the native discovery paths in a new directory.
Open that directory in a fresh Codex session and verify the exact task
before adopting it. Run the importer with Python 3.11+ when the manifest
contains roles. The tool's `--help` provides the command contract.

## Design and approve the passport

Before designing a passport or building the target, apply the relevant sections of the [architecture contract](references/architecture-contract.md) and [generated agent contract](references/generated-agent-contract.md). Use the [requirements baseline](assets/requirements-baseline.json), [blueprint template](assets/blueprint.template.json), and [runtime records](assets/runtime-records.json) for the exact supported inputs. The baseline is a constructor checklist and the project's own requirements still govern the domain.

The readable passport and machine blueprint describe the same revision and scope. Cover all known applicable capabilities, quality requirements, data and resources, positive and negative outcomes, and acceptance criteria. Include:

- Mission, actors, boundaries, desired state, current rules, inputs and outputs, and the source-linked requirements registry.
- The proposed public entry, exact modules and capabilities, interfaces, owners and writable paths, and specialist or independent reviewer roles where needed.
- Dependencies, phase gates, handoff and return, work that can proceed in parallel, pause and recovery, and the permitted scope of external effects.
- Actual tools and hosts, versions, install and transition routes, permissions and license or cost constraints, evidence gaps, and concrete fallback steps.
- First use, acceptance in the target environment, operations, safe update, and rollback. Give future decisions a responsible owner and due gate.

Choose a single module for cohesive work. Use a family when capabilities, outputs, allowed actions, acceptance stages, or reuse differ. A skill, a workflow phase, and a person or model instance are distinct. Staff and parallelize proportional to the evidence and actual host limits. Apply the [cross-domain core](references/cross-domain-core.md) and [domain model](references/domain-model-2.md) before material design. Preserve relevant AF, AD, and AX requirements and use the [production recipes](references/production-recipes-2.md) and [depth evaluation](references/depth-evaluation-2.md) when the corresponding work is due.

Show the user the exact proposal, scope, component list, tradeoffs, material gaps, and cost or authority decisions. Before creating or editing target skills, record an actual positive response that authorizes this passport revision, SHA-256, and scope. Use existing exact consent when it applies. Ask only when that consent is missing or a substantive delta exceeds it. A recommendation, JSON field, old approval, or elapsed time cannot satisfy the gate. Verify the current `build-gate` before each dependent build and continue any independent authorized preparation. Treat authority to construct, install in a designated target, or execute the original task as distinct decisions. One exact user response may grant more than one of them. External publication, data transfer, spending, and monitoring need their own active authority.

Keep M0 exploration, M1 complete passport, and M2 exact delivery distinct. For each accepted output, connect requirements and contracts to the operation, recipe, attempt, assembly, and observed evidence. Record inaccessible required capabilities as blocked or pending. Use [agent model](assets/agent-model-2.template.json) and [production recipe](assets/production-recipe-2.template.json) where the depth contract applies.

## Build, verify, install, and use the result

After approval, use the current `skill-creator` instructions for skill authoring. Use `design-specialist-skills` when the approved components actually require reusable specialist skills. See [specialist orchestration](references/specialist-orchestration.md). If an approved outcome includes an app or chatbot, keep the stable routes `app-atelier-director` and `chatbot-atelier-director` with concrete component owners, handoff contracts, and one lineage for shared data and decisions.

Implement the approved rules, materials, data, executable code, or tool adapters. Apply [production quality](references/production-quality.md) and the relevant medium profile in `assets/production-profiles.json` before making or changing material. Carry forward approved originals, identity, interfaces, languages, rights, and unresolved work. Preserve the actual composition, interaction, and depth of accepted references. Prove a representative slice in the intended medium before scaling. Keep the current support and recovery routes. Use [visual identity](references/visual-identity.md) for stable icons and colors and distinct identity for new public agents.

Bundle each generated skill's own applied rules and self-contained runtime resources. Apply the [inheritance contract](references/joint-use-inheritance.md) to every new module and package. Follow the exact documented resource and reference set, including the conditional AI/data resources. Keep private or changing project state outside general skill files and link it through approved project-local records. When meaningful data, LLM or retrieval work, prediction, adaptation, media production, or evaluation is involved, consult applicable parts of the [AI and data workflow](references/ai-production.md). Prefer the sufficient existing method. Evaluate any justified addition against permissions, cost, versions, and a measured baseline.

Use the [operating protocol](references/operating-protocol.md) and the exact subcommand help for `python3 -B <ACTIVE_SKILL>/scripts/foundry.py`. For current state, proof bindings, or read-only summary, use the [interaction protocol](references/interaction-protocol.md) and `python3 -B scripts/interaction.py status --source PROJECT --format markdown` from the skill root as applicable. These helpers validate declared properties or provide a view of current records. They do not generate professional output or run external operations.

Before transfer, run the syntax, link, schema, source, and applicability checks that bind the exact deliverable. Use `python3 -B <ACTIVE_SKILL>/scripts/check_foundry_depth.py MODEL --root PACKAGE` and [verify_depth.py](scripts/verify_depth.py) per the current help where applicable. A claimed verified M2 outcome also needs `check_foundry_depth.py MODEL --root PACKAGE --ready --session SESSION`. Apply the [evaluation contract](references/evaluation.md) to raw forward cases and meaningful failures. Record who ran each check and the exact sources and bytes they used. Author smoke checks and review by an independent actor have separate evidence. Keep any unavailable check open.

Use [tools and delivery](references/tools-and-delivery.md), [package_agent.py](scripts/package_agent.py), [install_agent.py](scripts/install_agent.py), and the [delivery manifest template](assets/delivery-manifest.template.json) for observed packaging and installation. Keep a portable kit outside the target root for installation and retain file modes when extracting it. If the native sandbox protects the destination, deliver the complete verified kit with the permitted operator route, exact target, next command, expected receipt, and return check. Run preflight before an authorized apply. Run verify afterward. Use the actual supported host discovery route and a fresh session on the correct project to confirm which installed source is active.

If the approved task also calls for using the generated agent, have an authorized consumer execute the original task. Verify the underlying action and its result against the initial acceptance criteria, with a different applicable input when the task calls for repeatability. Check scope boundaries and rejection of prohibited or invalid requests. Record prepared artifact, structural check, independent review, installation, discovery, invocation, and accepted user outcome according to observed evidence. For a requested staged trial, exercise the exact staged code and report the separately pending host discovery.

## Run, resume, and maintain

Keep versioned project intent, current requirements and decisions, evidence pins, knowledge, and run limits in the project. See [memory and evidence](references/memory-and-evidence.md). Record lessons with scope, supporting sources, applicability, confidence, and the effects on dependent work. Use structured or lexical lookup and readable checkpoints first. Add vector retrieval, workflow infrastructure, remote tracing, or an SDK when an evidenced need justifies it. Record decision evidence rather than private reasoning.

For host choice, cross-host handoff, unavailable execution, and resumption, read the relevant part of [Work and Codex continuity](references/joint-work-codex.md). For external operations verify the exact destination, method, rights, scope, cost, and outcome using [tool compatibility](references/tool-compatibility.md). If the response to a consuming action is lost, reconcile the native state before any retry. Respect pause before the next job and retain completed, active and pending work, known job IDs, unknown effects, and the exact resume step. Protect secrets from inclusion in skill instructions, chat output, or portable archives.

Use [lifecycle and support](references/lifecycle-and-support.md) for observation, maintenance, feedback, incident repair, earned capability changes, recovery, and readable handoff. Treat installed skills, deployed products, observed production behavior, and recurring jobs as separate facts. Start monitoring only with an actual authorized runtime and distinguish between prepared, verified, and delivered work.

For a requested installed suite update, use `python3 -B scripts/update_skill_suite.py --help` and the [suite-update contract](references/suite-update.md). Apply changes only after a source and target audit for the recognized set. Verify journal and target state before rollback. Unknown drift is a conflict to reconcile. Retain the input denominator and completed, skipped, and failed entries for a batch, then check completeness. For a self-update compare baseline and candidate on equal inputs with an independent rubric, replay or adopt existing state formats, and verify recovery.
