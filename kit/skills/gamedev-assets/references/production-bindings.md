# From the game model to production assets

Read this contract before creating an inventory, editable source, or state-dependent change. Use the canonical rules in the [model workflow](game-model-workflow.md) and keep production decisions and observations bound to them.

## Binding record

Use `assets/domain-templates/production-bindings.template.json`. Record exact model path, digest and revision, domain, object, state and event IDs, required representation, accepted target and locked properties, sources, exports, recipes and importers, runtime consumers, scenario and evidence IDs, owner, and status. For each exported game-rule parameter, document derivation or a copied-from binding and detect drift. Leave incomplete drafts open.

| Design input | Required production material | Boundary and context review |
|---|---|---|
| Camera and input | Actual scene camera configuration, framing and viewport rules, UI controls and feedback | Follow, zoom, transition, narrow aspect, thumb occlusion, precision, peak, reduced motion |
| Systems and resources | Readable state transitions and cues | Exhaustion, recovery, overlap, cancellation, equivalent sensory feedback |
| Actors and equipment | Silhouettes, rig, clips, contact and collision representations, attachments, mode and status cues | Telegraph, commit, recovery, damage, charge, heat, extreme poses and swaps |
| World | Kit, modules and connectors, interactive changes, navigation and occlusion data, compositions | Readable routes and revisits, persistent changes, rare legal combinations |
| Progression and rewards | Actual unlock, equip, collection and reward screens, contextual cues, use of new abilities | Earned, unclaimed, duplicate, capped and pending. Confirm after durable grant. |
| Learning | Affordance, highlight, help and control variants that preserve the rule | First try, failure, retry, independent use, return, optional hints |
| Commerce and lifecycle | Store, offer, price, status, restore, refund, loading, error and offline flows | Decline, no offer, interrupted payment or reward, stale price and offline |

Derive state coverage from the actual enabled features and model objects. `absent_by_design` requires a domain reason and reference to a decision or source. Missing tools keep affected operations blocked.

## Feasibility and identity

The production profile records actual source operations, editable representations, exporters and importers, supported runtime effects, licenses, costs, device budgets, and observed limits. Develop a visual target achievable through that route. Supply additional sources or samples for back views, rigs, topology, procedural behavior, or audio when required alongside a PNG.

Bind the exact style original and implementable mapping for camera, scale, form, surface, light, UI, motion and audio. For camera specify projection, follow, zoom and composition ranges and context-specific cues from the model. Show an implementable sequence when motion or interaction is central.

## Representative proof before scaling

Choose a small set covering shared risk: key mechanic, changed world or resource state, representative actor or prop, actual camera and HUD, and layered sensory feedback. After actual source, export and import, verify phone scale, normal and peak conditions, boundary contact and transitions, and platform budgets. Record the exact tested scope, including which rigs and platforms were observed.

Capture build, state, seed, time, camera, resolution and quality, source and export hashes, observer and independence, and deviations. Record observations separately from expectations. Register proof in the canonical evidence system using actual observer and build data.

## Changes and handback

A material change to camera, silhouette, materials, motion semantics, or sensory hierarchy reopens affected design, build, learning and QA. Repair routine exports within accepted tolerances. If the representative proof misses the intended result, pause dependent scaling and return a concrete change in route or target with an actual sample.

## Five operational records

For each item, use ToolCapabilityRecord, ProductionRecipe, and SemanticTransformation. Add ProductionAttempt after an observed invocation and AssemblyEvidence after integration. Use current model, requirement, artifact and evidence IDs.

Record accepted inputs and hashes, supported command, API or GUI preset and arguments, DAG, prerequisites, outputs and consumer, budget and allowed effects, technical, semantic and perceptual checks, repair and stop. Record transformation units, axes, pivot, scale, timebase, contact, color, alpha and audio conventions, preserved properties and intentional losses. Record actual job or request, status, outputs, hashes and cost. Reconcile unknown outcomes before retrying.

Verify that the tool and importer consume every material parameter. Confirm actual operation separately from descriptors and catalogs. Cache identity includes input, model, recipe, exporter and importer semantics. Rebuild affected derivatives and preserve approved originals.
