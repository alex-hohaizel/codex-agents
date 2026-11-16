# Game model 4.0: current format and executable checks

This reference covers commands, the model envelope, production, evidence, handoff, and limits.

## Commands

Find the actual `<SKILL_DIR>` of the active skill. Use the paths of the host performing the check. Python 3.10 or later is sufficient for the bundled tools.

```bash
python3 <SKILL_DIR>/scripts/game_model.py --help
python3 <SKILL_DIR>/scripts/game_model.py validate /absolute/model.json --design-only --json
python3 <SKILL_DIR>/scripts/game_model.py plan /absolute/model.json --stage concept --maturity C1 --json
python3 <SKILL_DIR>/scripts/game_model.py validate /absolute/model.json --stage preproduction --maturity T --json
python3 <SKILL_DIR>/scripts/game_model.py impact /absolute/model.json --changed RULE-ID --json
python3 <SKILL_DIR>/scripts/game_model.py portfolio /absolute/portfolio.json --json
python3 <SKILL_DIR>/scripts/production_contract.py /absolute/operations.json --root /absolute/project
python3 <SKILL_DIR>/scripts/reference_math.py <SKILL_DIR>/assets/v4/golden-arithmetic.json
python3 <SKILL_DIR>/scripts/check_suite.py --skill <SKILL_DIR>
```

Use concept, preproduction, slice, beta or release for the stage in `plan/validate`. C0, C1 and T are design maturity. From preproduction onward the minimum is T, and a lower input cannot reduce the gate. C0 remains preliminary. `--design-only` always gives `stage_ready:false`. Exit 0 covers the structural authoring scope requested. Missing due evidence at a stage gate returns a nonzero exit. Preserve `quality_certified:false`.

<a id="чинний-envelope"></a>

## Current envelope

The current only schema, `assets/game-model.schema.json`, has `schema_version:"4.0.0"` and requires `id,title,author_ids,source_requirement_ids,constraints,features,domains,dependencies,scenarios,evidence,production`. See the [exact field reference](model-contract.md) for domains, scenarios and evidence. `game_model.schema()` returns this schema. Unsupported versions are rejected.

Keep one canonical `design/game-model.json`. Project requirements and decisions govern. Typed references pin the one source set and registry. Keep actual source, code, data and specifications in pinned linked files. Include only the necessary model representation of meshes and samples.

## Production extension

`production` has the following fields.

- `maturity:C0|C1|T`.
- `tracks` has exactly TR01 through TR20 from `v4_contract.TRACKS` and [systems](v4/systems.md). Each has a stable name, enabled status and rationale, owner and receiver, requirement_ids, summary, reads and writes, contract_ids, invariants, scenario_ids, progression, content, feedback, persistence and budget, pinned concept references and specification references.
- `applicability` covers damage, physics, AI, cloud, procedural systems and purchases with enabled status and rationale. Align AI with actual autonomous actors. Derive combat and cloud needs from the chosen game.
- `contracts` contains typed behavior, state_machine, numeric, rng, family, generator, ai, persistence, damage, physics, input, presentation, economy, commerce, journey, asset, release and measurement records. Take fields from `assets/v4-model/contract.template.json`.
- `state_fields` records the typed Catalogue with classification, owner, scope, authority, storage, encoding, consistency_group, commit, restore, merge, migration, retention and initial value.
- `dependencies:[{from,to,reason}]` records upstream to dependent between existing IDs.
- `operations` records capabilities, recipes, transformations, attempts, assemblies and obligations. See [production](v4/production.md).
- `unresolved:[{id,description,owner,due:C0|C1|T,blocks:[ID]}]` blocks the corresponding maturity when due and unresolved.

Use `assets/v4-model/` and the detailed `assets/v4-domain-templates/` as authoring forms. Example models and `production.template.json` start C0 or unresolved. Replace placeholders with verified observations when available. The machine contract specifies the minimum structure. The domain owner, receiver and QA check semantic completeness.

Active C1 tracks have linked concept documents, concrete rule statuses, invariants, positive cases and negative cases. T adds pinned specifications and all state classifications. The kind-specific contract covers math domain, rounding, clamp and overflow, RNG streams and resume/version, state guards and ties, AI knowledge and action timing, damage channels and capture/deduplication/commit, solver profile, purchase/save lifecycle and operation obligations as applicable. Numeric tuning specifies initial/minimum/maximum values, goal and method. Resolve behavior before the gate. Use actual code, fixtures and oracles to verify formulas, callbacks and engines.

<a id="evidence-assembly-та-impact"></a>

## Evidence, assembly and impact

Use due domain checks and independent track reviews `v4.TRxx.concept|contract`. `plan` gives actual check IDs and scope_sha256. Bind proof to current bytes and inputs, declared dependency closure, scenario, and actual observer. Changes to authors, toolchain, recipe, inputs or required data invalidate dependent proof. The integrator investigates missing graph edges. Repeat the affected check before rebinding evidence.

The T/A/B/R production gates are T contract, actual assembly or slice A, beta B, and release R. Slice and later require assembly. A native_verified assembly's build digest matches the verified native artifact receipt. Document and sample validity cover their own tests. Device and human claims require their own observation. Use `scope_is_product_release` for actual full product release scope.

`reference_math.py` reproduces the four approved D2 arithmetic examples: channel order/round/barrier/overkill, DoT/capture/resume, TTK distribution, and ideal contact impulse. Their policies apply only to the approved examples unless explicitly adopted. For actual runtime use shared golden fixtures and differential checks.

<a id="handoff-і-продовження"></a>

## Handoff and continuation

The toolkit marker, game-model **4.0.0**, handoff protocol **1.0.0** and runtime state **2.0.0** are separate version domains. Use the exact current toolkit marker implemented by the handoff and runtime tools. Historical display editions do not set protocol compatibility. Old output formats are outside the current reader. For continuation, recover actual requirements, decisions, code, data, media and product state, then author current contracts and obtain due evidence. Installing a skill preserves those sources and game saves. See [handoff](handoff-contract.md) and [workflow](game-model-workflow.md) for scoped QA, LiveOps and production decisions.

## Limits

Structural, link, byte and freshness checks cover their observed scope. Completeness of the human intent, proof of all referenced algorithms, decision variety, enjoyment, comfort, rights and the authenticity of a receipt need their own validation. Actual generation, import, runtime, device run, player observation and revenue have distinct proof.
