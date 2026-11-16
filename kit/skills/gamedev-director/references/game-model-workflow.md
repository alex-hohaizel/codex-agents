# Game Atelier 4.0 game model and workflow

This reference covers intake, model authority, gates, orchestration, handoff, and changes.

<a id="вхід"></a>

## Intake

Read [v4/index](v4/index.md), the current intent, and checkpoint. Identify C0, C1 or T and the corresponding scope. New complete 4.0 concepts require C1. Production transfer requires T. Studio plans the game model only when an actual game is available. Search, audit, update and pause preserve the existing choice and round.

<a id="одна-модель"></a>

## One model

The project owns `design/game-model.json` or an existing equivalent. Keep stable IDs, sources, constraints, features, domains, dependencies, scenarios and evidence. Retain the 4.0 `production` extension in the same envelope. The 20 tracks, behavior, catalogs, state and production contracts derive from this model. Pin linked specifications and data by exact path and digest. Existing requirements and decisions govern. A sidecar provides binding and mapping. Use [model-format](model-format.md) for the schema and CLI, and [v4/index](v4/index.md) for the six logical competencies and conditional applicability.

<a id="3-предметні-модулі"></a><a id="предметні-модулі"></a>

Apply the relevant domains without equating small games with arenas, projection with tracking, world with RPG, or genre with a particular art, input or commerce pattern. A disabled feature requires a domain reason. Missing tooling leaves required work open. A fixed camera is an active camera. An actor can be an NPC, opponent or ally. Apply IAP or ads only when the accepted commerce model uses them.

## Gates

| Gate | Due result |
|---|---|
| concept | Full C1, causal scenarios and counterexamples, a feasibility profile, and independent domain acceptance. Use C0 for clearly identified early work. |
| preproduction | T with exact contracts, launch catalog, generation, persistence, recipes, assets, input, AI and math as applicable, fixtures and pinned specifications. A fresh consumer can start implementation. |
| slice | Actual native representative assembly on the declared platforms, with input, camera, motion, contact, visuals, audio, haptics and save evidence as applicable. Verify the physical-device claims due at this stage. |
| beta | Actual player learning, transfer, later mastery, variety and value, with the scope of the sample. |
| release | Exact RC, signing, config, epoch, schema, symbols, applicable purchase and cloud sandbox proof, device and performance evidence, policy and recovery. |

`plan` lists due checks. `validate --design-only` checks authoring and always returns `stage_ready:false`. A must keeps its designated proof regardless of flags. `quality_certified:false` identifies the claim boundary. Schema, link, byte and validator checks establish their observation; enjoyment, balance, native device behavior, human observation and revenue require actual evidence. The validator reads the current model format. For new and resumed work, populate C0 from actual contracts and obtain the C1, T and stage proofs that are due.

<a id="реальна-команда"></a>

## Working team

The director integrates, domain authors produce outputs, leads maintain interfaces, and a different observable actor reviews critical work. Assign one writer to each path and shared resource. Use the actual concurrency limit. Each task records inputs and hashes, assigned IDs, writable paths, consumer and acceptance, capability, operation and host, due proof, resource budget, and how to stop, cancel and reconcile. Separate independent alternatives from independent review. Choose reviewers for the work and risks.

After two attempts with the same failure, reconsider the cause, diagnosis, or available route. Check the actual capability before another generator or prompt. Find recipes and production attempts in [production](v4/production.md). Use appropriate primary sources for world, physics, commerce and the pinned native SDK. Confirm actual tool availability separately from model acceptance.

## Handoff

`pipeline.py` uses the current **1.0.0** transport, schema and suite. `atelier.py` uses current **2.0.0** state. Use the toolkit marker implemented by these tools and stated by the exact package. An accepted handoff outside Studio carries `game_model:{path,sha256}`, current model **4.0.0**, and due stage proof. Drafts also use the current supported format. A `seal` binds hashes. Authority and review remain separate. Add model plans, reports and traces as normal artifacts.

Default stage-to-gate mapping: concepts → concept, preproduction → preproduction, assets and build → slice, QA → beta, release and liveops → release. QA can use design_review, contract_review, slice_review, beta_review or release_readiness. LiveOps can use incident_analysis, design_change, runtime_change, player_experiment or release_change. Bind scope to a current requirement or decision with scope_ref and a description. A scoped review keeps product concept and engine decisions in their approval route. Release and release_change retain the release gate. See [handoff](handoff-contract.md).

<a id="impact-і-продовження"></a>

## Impact and continuation

Track changes through semantic reads, writes and contracts to dependent specifications and data, assets and code, scenarios, builds and release. Give each edge a cause. Gameplay feedback cycles can apply. Unlock and prerequisite graphs are acyclic. `impact` uses recorded dependencies. Review it for missing semantic edges. A change to grip may affect routes, input and economy, while the same studio original remains intact.

Reuse scoped evidence only for the declared dependency closure, toolchain, recipe, version and outputs it covered. Keep old observations bound to their exact inputs and repeat affected review. Bind native observations to the build, scene, config and scenarios. Retain the accepted original byte for byte. A nondeterministic provider supports only the repeatability actually measured.

Installing skills preserves game saves, rounds, decisions, .gameatelier and .atelier state. Verify Work and each Codex host separately. Where a host is unavailable, prepare a pinned launch and return bundle with exact commands, expected outputs and receipts, and verified return steps. Retain actual state and checkpoint after release. Report scheduling once it is running and observed.
