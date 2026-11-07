# Current game-model domains and evidence

Use alongside [current model format](model-format.md). This reference describes the sole current schema and its domain/evidence contracts.

`scripts/game_model.py` is a standard-library Python 3.10+ design and evidence checker. It runs beside `atelier.py` and `pipeline.py`; it does not replace handoff 1.0 or runtime state 2.0, execute game code, certify fun, or operate stores.

## Commands

```bash
python3 <DIRECTOR>/scripts/game_model.py --help
python3 <DIRECTOR>/scripts/game_model.py validate /absolute/model.json --design-only --json
python3 <DIRECTOR>/scripts/game_model.py plan /absolute/model.json --stage slice --json
python3 <DIRECTOR>/scripts/game_model.py validate /absolute/model.json --stage slice --json
python3 <DIRECTOR>/scripts/game_model.py impact /absolute/model.json --changed RULE-ID --json
python3 <DIRECTOR>/scripts/game_model.py portfolio /absolute/portfolio.json --json
```

An explicit stage invokes its normative evidence gate. `--design-only` checks authoring structure and internal references, always returns `stage_ready:false`, and cannot satisfy a stage gate. Without either option, `validate` defaults to the concept gate. Exit 0 means the requested check passed; exit 1 means a model defect or unmet due evidence; exit 2 means malformed input/CLI. Readiness applies only to the declared model and evidence, never the actual quality of play. `quality_certified` is always false.

## Root

Required: `schema_version:"4.0.0"`, `id`, `title`, `author_ids:[string]`, `source_requirement_ids:[string]`, `constraints`, `features`, `domains`, `dependencies`, `scenarios`, `evidence`, `production`. Production contains C0/C1/T, twenty tracks, applicability, typed contracts, state, operations and unresolved work as described in [model-format](model-format.md). IDs are nonempty stable strings and globally unique across the model, rules, actions, actors, spaces, unlock nodes, rewards, lessons, offers, journeys, equipment and scenarios. Feature names are `camera,input,systems,actors,world,progression,rewards,learning,art,commerce,lifecycle,equipment`.

`constraints` contains `platforms:[string]`, `target_fps:number>0`, `extra_paid_services:boolean`. It may contain project-defined budgets. Each feature has `enabled:boolean,rationale:string`; disabled domains must have a concrete rationale and no active domain payload. `input,systems,art,lifecycle` are required. Camera can be inapplicable for a non-spatial board/UI; a fixed camera remains an enabled camera. Actors do not mean enemies: allies, opponents, vehicles or other autonomous participants are valid. No feature requires RPG inventory, IAP or combat. `commerce.model:"none"` describes an intentional no-offer decision.

## Domain payloads

The JSON schema documents primitive types. The checker additionally validates references, stage rules and evidence. Nonempty text is a completeness check, not a word-count certificate of design quality.

| Domain | Required payload |
|---|---|
| camera | `projection`, `tracking`, `focus_subject`, `states:[{id,when,behavior,readability_risk}]`. Optional `subject_fraction:{min,max}` uses fractions of viewport height, and must satisfy `0<min<=max<=1`. No universal hero size. |
| input | `scheme`, `simultaneous_contacts`, `actions:[{id,intent,gesture,context,feedback,cost_or_limit,recovery}]`, `peak_load_scenario`, `accessibility:[string]`. |
| systems | `rules:[{id,state,trigger,change,limit,counterplay,feedback}]`, `links:[{from,to,decision_effect}]`. Links reference actual rules. Feedback cycles are allowed and expected when justified. |
| actors | `agents:[{id,role,perception,states:[string],action_refs:[rule-ID],telegraph,counterplay,variation}]`. `role` is free text and can describe non-enemies. |
| world | `topology`, `spaces:[{id,purpose,interactive_states:[string],route_choices:[string]}]`, `transitions:[{from,to,condition,new_decision,return_reason}]`. A compact space is valid; transitions reference spaces. |
| progression | `nodes:[{id,unlock,prerequisites:[node-ID],new_decision,revisit_effect}]`, `reset_policy`, `long_horizon`. Only prerequisite cycles are forbidden; numeric inflation alone needs semantic review. |
| rewards | `entries:[{id,trigger,grants,feedback,purpose,cap_or_rule}]`, `fairness_recovery`. |
| learning | `curriculum:[{id,teaches,practice,assessment,remediation}]`, `timing`, `return_resume`. Optional lesson `unlock_ref` references a progression node. |
| art | `style:{shape,materials,palette,lighting,motion,ui,audio,haptics}`, `production_route:{tools:[string],editable_sources,exports,runtime_import,cost,license,risks,verified_status}`. Claims of feasibility still require evidence. |
| commerce | `model` (`none,premium,dlc,ads,iap,pass,subscription,hybrid`), `resources:[{id,sources:[string],sinks:[string],cap,reset,persistence}]`. For none: `no_offer_reason`, empty `offers` and `journeys`. Otherwise `free_path`, `dominance_counterexample`, `offers:[{id,desire,grants,earned_path,decline_path,limits,cumulative_effect,price_basis}]`, `journeys:[{id,trigger,steps:[string],cancel_recovery,restore_or_reconcile}]`. Premium may state honestly that access requires purchase. |
| lifecycle | `launch_scope:{content_units,early,mid,late,end_or_replay}`, `content_grammar:{vocabulary:[string],composition_rules:[string],forbidden_combinations:[string],novel_decisions:[string]}`, `support_plan:{save,resume,offline,update,finite_content_end}`. |
| equipment | `items:[{id,function,properties:[{name,effect,limit}],rule_refs:[rule-ID],progression,tradeoff}]`. |

Optional authored payload beyond this core may live in referenced project specifications. Do not flatten all detailed GDD/data into this file. Preproduction needs `spec_refs:[{domain,path,sha256}]` for each active domain: safe relative, existing, byte-pinned specification/config files. Concept does not require full specs. Native stages additionally need all due proof checks below.

## Causal scenarios and dependencies

Each scenario has `id,domains:[feature],initial_state,action,expected_observable,changed_decision,without_rule`. Optional `due_stage` is `slice|beta|release`, default `slice`: an endgame scenario may be due later without requiring the entire game in the representative slice. Every active domain must have at least one representative scenario due by slice; scheduling all its scenarios later cannot bypass that gate. At least one scenario must exercise two active domains; this is a minimal coverage check, not a depth score. `without_rule` states the counterfactual; independent review must determine whether it actually changes a decision.

`dependencies:[{from,to,reason}]` uses the model/domain/entity/scenario IDs. Domain IDs are their names. Edges point **upstream → dependent**. All references must resolve. Gameplay feedback may cycle; unlock prerequisite graphs may not. `impact` follows explicit edges plus domain ownership and normative cross-domain consequences; it reports checks to revisit, not approval to change accepted content.

## Evidence requirements

Every active domain needs an independent `design_review` document at concept; a separate `product.applicability` review covers enabled and disabled feature decisions. Preproduction adds an independent contract review at that stage and pinned `spec_refs`. Slice adds observed runtime captures for active domains, a real native build receipt, and physical-device observation for each declared Android/iOS platform. Beta adds player observation for input, learning, systems and lifecycle, plus actor/world/progression/reward/commerce when active. Release adds current independent release review for all active domains, another physical-device observation for each platform and, for paid/ads commerce, external integration receipt. Earlier valid checks remain required. A no-offer game does not acquire purchase/ads requirements.

Evidence record: `id,domain,check_id,stage,modality,proof_path,sha256,model_sha256,scope_sha256,observer_id,author_ids:[string],method,observed_at,environment,origin`. `model_sha256` retains whole-model provenance: SHA-256 of canonical UTF-8 JSON excluding the root `evidence` array (`ensure_ascii=False,sort_keys=True,separators=(',',':')`). New records copy the normative `scope_sha256` printed by `plan`: domain payload, owned entities, relevant scenarios/spec refs, applicability, constraints, authorship and explicit/typed upstream dependency closure. An unrelated domain edit can preserve a scoped proof even when whole-model provenance differs; a changed upstream rule cannot. Missing `scope_sha256` is invalid; a whole-model hash cannot substitute for the current dependency scope. Never refresh hashes as a substitute for performing the review. `product.applicability` is intentionally global. Native build/device receipts bind actual artifact/platform observations; domain checks establish behavioral scope. The integrator must inspect semantic dependency completeness before reusing proof, because no graph can detect an omitted design dependency automatically. Domain authors are declared in root `author_ids:[string]`; an independent review observer cannot be one of those authors or the evidence's author IDs. Actor identity and actual observation remain accountable records, not machine-verifiable truth.

Allowed modalities: `document,runtime,build,device,player,external_receipt`. Match each requirement's `origin`: `design_review,contract_review,runtime_capture,native_build,device_observation,player_observation,release_review,external_receipt`. `historical_reference` is never gate evidence. All proofs and `spec_refs` resolve relative to the model directory, remain within it, and cannot traverse a symlink outside it. Hashes must match current files. Runtime proof must contain recognizable PNG/JPEG/WebP/video bytes; a JSON renamed `.mp4` fails. Direct media evidence also requires `build_sha256` and `scenario_ids` metadata. All native-stage observations must reference a build hash backed by a validated native artifact receipt in the model. Static images can prove an observed state, not motion; camera/input/actors require video or timed trace with media samples at native gates. Recognizable bytes establish media type, not that a capture came from the claimed runtime; actual provenance and observation require accountable review.

Native `scenario_ids` must actually exercise the check's domain, not merely name any scenario. `plan.required_checks[].required_scenario_ids` lists due coverage. Multiple valid receipts may jointly cover those scenarios; missing coverage blocks readiness. Native build/device coverage is required for each declared mobile platform, and an iOS observation cannot cite an Android artifact hash. Runtime/player/external JSON receipts include `platform`; direct runtime media uses evidence-level `platform`; device receipts use `device.platform`. Historical references are retained without satisfying or poisoning gates. Superseded records may use `status:"superseded",superseded_by:"CURRENT-EVIDENCE-ID"`; replacement must be current, for the same check, and independently validated. Leaving a stale receipt current blocks its unresolved inconsistency until explicitly reconciled.

Structured receipts use `schema_version:"game-atelier-observation/1"`, matching `kind`, `build_sha256`, `scenario_ids`, and nonempty `samples:[{path,sha256,kind}]`. Device receipts additionally require `device:{platform,model,os,physical:true}`. Player receipts require `participant_count>=1`, `outcomes:[{scenario_id,observation}]` and an explicit `method`; anonymize participants. Build receipts require `platform`, `artifact_path`, `artifact_sha256`, `toolchain` and a real native artifact container; web mocks are not native builds. External receipts require `provider,operation,observed_status,transaction_reference` and supporting files. Do not invent receipts or identifiers. Machine checks inspect structure, bytes and consistency; they cannot certify physical hardware, human participation, commercial outcome or fun.

## Portfolio

Input is `{candidates:[model-object | {id,facets:{scale,topology,projection,tracking,framing,genre,input,art,commerce},decision_signature:string,source_requirement_ids:[string]}]}`. The checker keeps these axes separate, reports distributions, exact facet twins and lexical decision-signature neighbors for human review. Fixed projection is not fixed tracking; scale is not genre. Similarity findings are warnings, not automatic disqualification or quality ratings. Explicit facets are declarations and must be reviewed against the actual model/images.

The six bundled examples are illustrative draft models, not observed games or accepted production choices. `--design-only` validates their structure; stage gates remain pending until real evidence is supplied.
