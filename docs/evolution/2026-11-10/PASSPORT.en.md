# AI, data and production evolution — passport 0.1

**Proposed for owner approval. No target skill has been created, installed or updated under this passport.** Prepared on 2026-11-10 against commit `8951398b38a9610854823302ea612cb3844d52e6`. This is a new passport; it does not amend the historical universal-entry passport 0.2 or borrow its approval.

## 1. What you receive

One entry for a business idea, a difficult technical task or an existing product. It restores the accepted outcome and project context, selects the needed expertise, produces and verifies the result, and explains what remains. The new competence covers the whole path from external data through AI/ML processing to an API, a usable interface, deployment preparation and continued operation. A nontechnical team should be able to use the delivered product without operating Codex or understanding its internal agents.

The requested end state is the full capability set in [REQUESTS.json](REQUESTS.json), R01–R17, with preservation and documentation obligations R18–R23. A representative implementation proves the common route; it does not reduce the requested scope to a demonstration or certify every future domain, language, model, asset or platform.

## 2. Why extend the current system

The existing constructors, context contracts, product directors, media methods, bounded execution and adoption controls are useful and should remain. The main missing part is a reusable data/model lifecycle with operational implementations and appropriate evidence. Several existing App rules also contradict their own platform and research profiles. See [the audit](AUDIT.en.md) and [the current catalogue](CURRENT-SYSTEM.en.md).

We considered three options. Adding more instructions alone is cheap but does not supply repeatable connectors, evaluation or recovery. Rebuilding everything as version 7 would put stable projects and identity at unnecessary risk. **The recommendation is a compatible extension with an optional AI competence pack**, shared standards and scoped execution. A genuine incompatible requirement discovered during implementation must be explained and returned for a revised decision; it must not be hidden under a minor version.

## 3. Exact proposed composition and versions

These are target versions, not installed versions. Current versions remain core 6.0.0, Orchestrator 1.1.0, service 0.2.0 and repository 1.3.0 until an actual release changes them. Repository 1.3.1 publishes this audit and proposal only.

| Component | Proposed change | Reason and activation |
| --- | --- | --- |
| Core suite | 6.0.0 → 6.1.0; all 33 stable names retained | Shared conditional AI/data lifecycle, clearer contracts, App contradictions repaired; ordinary non-AI work stays lightweight |
| `atelier-orchestrator` | 1.1.0 → 1.2.0 | Recognizes AI/data/ML/creative work, selects usable specialists, preserves one brief and original product scope |
| `codex-agents-maintenance` | 1.0.0 → 1.1.0 | Manages reviewed new pack inventory and adoption with existing preservation controls |
| AI competence pack | 1.0.0; seven optional skills listed below | Separate installable sources; the core denominator remains 33 |
| Host role profiles | Preserve 12; add four optional profiles | Actual expertise and artifact ownership, selected per task; up to 16 declared roles, never a mandatory team of 16 |
| Agent Atelier | 0.2.0 → 0.3.0 | Inspect and run the available capability routes; show real data/model/job/cost evidence and useful failures |
| Repository | Target 1.4.0 | Verified sources, all affected guides, migration, packages, catalogues and evidence |

Seven new stable selectors, proposed under `optional-skills/`:

| Skill | Its owned work | When it is useful |
| --- | --- | --- |
| `ai-atelier-data` | Connectors, normalization, dataset versions, lineage, quality and recovery | Repeated API/import/scraping ingestion or data reused downstream |
| `ai-atelier-analysis` | Text extraction, classification, clustering, source-backed themes and trends | Reviews, support material, segmentation and monitoring |
| `ai-atelier-llm` | LLM/RAG/agentic application logic, tool contracts, prompting, workflow recovery | A product needs model decisions, retrieval or multi-step AI actions |
| `ai-atelier-prediction` | Feature/label definitions, baselines, tabular/time-series training, validation and inference | A business decision needs an honest forecast, including a conditional CPA case |
| `ai-atelier-adaptation` | Open-model feasibility, LoRA/other tuning, model bundle and serving comparison | A measured gap justifies adapting a model rather than prompting/retrieval alone |
| `ai-atelier-media` | Costed multimodal production graphs, approved masters, variants and consumer delivery | Repeatable image/vector/3D/audio/video/document/UI asset work at product quality |
| `ai-atelier-evaluation` | Task-specific AI evaluation, release evidence, drift and productionization checks | Model/data/generated-output claims need a reproducible independent check |

Each skill has `SKILL.md`, `agents/openai.yaml`, its own appropriate new icon, scoped references, templates, examples and executable helpers where relevant. Existing icons, names and colours are preserved. The final inventory is **33 core + nine optional sources = 42 reusable skills**; nine means the existing orchestrator and maintenance skill plus seven new specialists. A skill is neither a running process nor a credential.

Four proposed role sources are `agent-profiles/foundry-data-engineer.toml`, `foundry-ai-engineer.toml`, `foundry-ml-engineer.toml` and `foundry-creative-engineer.toml`. Data owns ingestion and dataset engineering; AI owns model/tool workflows; ML owns features, learning and serving; creative engineering owns repeatable multimodal production and delivery. Existing product, architecture, backend, QA, privacy, reliability, integrations, platform, conversation, skeptic, judge and cost expertise remains. Models/settings of the existing 12 are not replaced. New roles inherit the available host model policy unless the owner makes a specific choice.

## 4. How a task moves through the system

The orchestrator restores the project first: outcome, accepted references, native state, scope, current agent, unfinished work, rights and actual capabilities. A narrow repair can go directly to an existing specialist. A product request goes through its current product integrator. Agent construction happens only when reuse is insufficient and the necessary passport is agreed. AI specialists support that integrator; there is no second AI director with a competing product plan.

The task graph is selected from discovery → specification → representative proof → full production → integration → independent verification → allowed release → operation. Phases can be parallel where their inputs and writers are independent. A defect returns to the affected branch with new source/evidence bindings. A product request remains open after the agent package is built: create → install → discover → use the agent for the original product outcome must remain traceable.

Every delegated work package carries requirement IDs, exact inputs, permitted paths/actions, owner, expected outputs, interfaces, resource caps, stopping condition, verification and return format. The host's actual concurrency limits prevail. Without subagent capability, work can proceed sequentially, with self-check honestly separated from independent review.

## 5. Where implementation will live

| Planned source | Deliverable |
| --- | --- |
| `standards/ai-data-production.md` | Shared activation, lineage, datasets/features/models, quality, deletion and downstream ownership |
| `standards/ai-workflows.md` | LLM/tools/RAG/workflow boundaries, effect identity, interruption and reconciliation |
| `standards/ai-evaluation.md` | Dataset/split/evaluation contracts, task metrics, limitations and release/adoption |
| `standards/ai-generation.md` | Multimodal batch manifests, craft proof, identity, cost, rights and consumer integration |
| `standards/coding-assistants.md` | Codex/Cursor/Claude Code capability discovery, context and permission-preserving handoff |
| `standards/ai-schemas/` | Versioned SourceContract, DatasetManifest, SplitManifest, FeatureManifest, PredictionContract, WorkflowRun, EvaluationPlan, EvaluationReport, TrainingRecipe, ModelBundle, BatchPlan, ItemManifest and GenerationBatch schemas with valid/invalid examples |
| `optional-skills/ai-atelier-*/` | The seven specialist sources, recipes, fixtures and runnable task-specific helpers |
| Existing constructors and family references | Activation and inheritance of applicable shared contracts, portable generated-agent resources, preserved native formats |
| Existing materializer/updaters/installers | Manifest-controlled admission, propagation, preservation, install/verify/rollback for the new inventory |
| `apps/agent-atelier/server/` and `shared/` | Typed scoped capability adapters, job/evidence/status projections and API contracts |
| `apps/agent-atelier/client/src/` | Adaptive project workbench for actual available routes, data/model/media runs, decisions and recovery |
| `evaluations/ai-production/` | Small reproducible execution cases and source-pinned expected boundaries; no private datasets |
| `docs/`, `releases/`, `governance/` | Complete operating documentation, requirements, migrations and release verification |

Shared files are materialized through an explicit checked resource manifest, including portable standalone bundles and generated agents. Existing four shared resources and 12 inherited resources must be reconciled deliberately; a link to a resource absent after packaging is not sufficient. The optional updater's two-item allowlist and host installer's fixed 12-role check must become reviewed bounded manifests, with path/identity/hash validation. The 33-core protection is retained. Unknown local edits require a reviewable conflict plan, not replacement or invented historical receipts.

## 6. Data and model lifecycle

The product's native checkpoint and requirements remain authoritative. Dataset, model, evaluation and generation records are versioned component artifacts referenced there; they do not create another product backlog or authority store.

The path is actual source → permitted acquisition → raw/normalized dataset → feature or LLM/media processing → independent evaluation → consumer API/UI → monitoring/repair/rollback. Records pin the relevant bytes, code, schema, model/tokenizer/adapter, environment, split and event/observation/availability times. Transformations fit on training data only. Deletion and revocation propagate through applicable embeddings, features, caches, outputs, jobs and backups with explicit limits. External source text is data, never an instruction granting the worker new tools or permissions.

For CPA, a prelaunch claim may use only features available before launch. Labels need attribution window, spend/conversion definitions, currency and delayed/censored outcomes. Campaign/account/time/group splits, selection effects and drift must be examined. Compare simple baselines; report error, calibration/intervals, uncertainty and abstention. Synthetic fixtures prove mechanics and leakage detection, not commercial predictive accuracy. Zero-conversion campaigns with undefined or censored CPA stay visible; silently excluding them would bias the result. No accuracy target is invented before a suitable authorized dataset and business decision exist.

See [the seven capability recipes](CAPABILITIES.en.md) for operations, choices, artifacts and negative cases.

## 7. Tools, environments and choices

Use the smallest adequate maintainable stack, chosen from the task and measured constraints. API/export precedes more fragile scraping when it supplies the required data; static HTTP parsing precedes a browser when sufficient. Scrapy/Playwright are possible implementations, not universal dependencies or source permissions.

Direct provider SDKs and explicit state are enough for many LLM tasks. LangGraph is considered for genuinely durable branching/stateful work; LangChain or LlamaIndex where their integration/retrieval mechanisms improve a measured need. Embeddings are useful for retrieval or clustering under their own evaluation. Framework choice needs a short explanation and a maintained exit path, not a fashion-based default.

For predictions compare a naive/statistical baseline, appropriate linear/tree methods, then XGBoost/LightGBM or a neural approach where justified. For adaptation compare prompting/retrieval/smaller models first; MLX-LM may suit compatible Apple silicon and PEFT a suitable PyTorch environment. Device memory, model licence, training rights, time and serving feasibility must be checked before weights or jobs are acquired. No CUDA, GPU service or large download is silently assumed. Adapter, merged/quantized export and actual serving consumer each need separate proof against their own bytes.

Coding assistants are the normal production aid when actually available. Codex, Cursor and Claude Code have different rules, state, tools and approval semantics. Keep their native configuration; export only the needed source-bound task/context, not credentials or a blind translation of permissions. An executable on PATH is not account readiness; a profile file is not a launched subagent. The local coding assistant and the agentic workflow inside a delivered product are different runtimes.

Local owner Codex/ChatGPT access may support the personal development workbench within its actual terms and capabilities. A hosted/commercial AI product needs its own supported production authentication and service architecture; it must not share the owner's coding login with end users. API keys remain secret handles outside manifests and logs. [Official sources](SOURCES.json) are checked again at implementation for unstable operations, models, limits and prices.

A hash identifies model bytes; it does not make their loader trustworthy. Admit model/data formats and loaders explicitly, keep unreviewed dynamic remote code disabled, and review any required custom implementation in its isolated resource-limited environment. Test malicious serialized input/manifest, path escape and oversized allocation before serving. Pickle-based loaders can execute code; custom model code is a separate trust decision. [Model persistence](https://scikit-learn.org/stable/model_persistence.html), [custom model loading](https://huggingface.co/docs/transformers/en/models).

## 8. Usable products and professional creative work

Nontechnical users receive a product interface with understandable input, progress, result, source/evidence, correction, permission and recovery paths. Errors identify the next useful action. Appropriate authentication, tenancy, export/deletion, background work, operator support and deployment runbooks are designed when the actual product requires them. There is no compulsory microservice architecture, telemetry platform or all-platform build.

Accepted visual references are read before work. Establish the product's composition, information depth, typography, interaction, illustration/3D/audio language, approved masters and derivative rules. A candidate retaining colours/labels but losing the reference’s defining composition, scale, information depth, interaction or function must fail. Prove a representative output in the actual medium before a batch. Images need visual inspection; animation/video need playback; sound needs listening; UI needs interaction; game assets need target-engine/device use at the relevant scale. Existing Game and ChatBot craft methods remain in force. No provider operation is claimed for an unsupported medium; lack of a rigging, voice, video or engine tool stays a concrete missing route.

For a batch, preserve a complete denominator: requested, attempted, succeeded, failed, rejected, cancelled and unresolved items. Use stable job/item identity, cache keys, quality acceptance and real cost receipts. The cheapest usable accepted output matters; low cost must not buy identity drift or unusable assets. Retry only after reconciling unknown consuming outcomes.

## 9. What changes in the local panel

Preserve the accepted operational-platform visual identity and current portfolio/continuation protections. The panel must connect a requested outcome with real project tasks, used skills/agents, accepted decisions, source artifacts, jobs, evidence and next actions. It must distinguish a declared capability, installed source, host discovery, actual access, observed execution and owner acceptance.

When applicable a project gets data-source health and dataset versions, analysis/trend results, workflow runs, model comparisons/validation, generation batches with reviewable previews, cost/limits and deployment readiness. These views appear for relevant work, not as empty mandatory tabs. Loading, missing access, partial history, errors, cancellation and unknown outcomes are designed states. A visual map uses real project/work relationships and can navigate to the actual work and evidence; it is not a fabricated graph.

The service adds typed, narrowly scoped adapters for admitted local data/ML/LLM/media jobs and their evidence. No unrestricted shell, arbitrary MCP server or ambient account privilege is exposed through a button. Preserve the current maximum of four selected skill snapshots per prepared task; split longer workflows into dependent jobs under the same integrator rather than silently raising permissions or limits. The existing isolated Codex executor and native-history constraints remain. Dataset/model records link to real artifacts and owning native state. Old native chat context cannot be manufactured from metadata. Local-only bind, access protection, size/path/resource limits and evidence redaction must be verified for every new endpoint.

## 10. Resources and authority

Use existing access first. This passport permits preparation, source changes and isolated local verification after approval; it does not approve new spending, production deployment, product-data migration, commercial licensing decisions or sending messages to other product chats. Each concrete external operation checks current schema, target, right, recipient, scope, cost and consuming-response reconciliation. A safe dry run must be clearly labelled as a dry run.

Before costly work set runtime, item/token/media count, CPU/GPU/memory/storage/network and money caps suitable for the task. Fixed universal budgets would be misleading. Cost estimates show their assumptions and current provider reference; actual receipts remain separate. A provider timeout can mean unknown consumption; local checkpoints alone do not guarantee exactly-once external effects.

## 11. Implementation stages and exit conditions

| Stage | Work and dependency | Reviewable exit |
| --- | --- | --- |
| S0 — baseline and approval | Freeze this passport, current manifests/settings/identity, requirements and actual installation | Exact owner decision; no inherited approval from another passport |
| S1 — contracts and compatibility | Shared lifecycle/schemas; App rule corrections; manifest/resource/inheritance design | Valid/invalid examples, contract review, preserved old fixtures/native state |
| S2 — specialist sources and teams | Seven skills, four role profiles, constructor/director/orchestrator activation | Complete source catalogue and task routing/handoff examples, independent semantic review |
| S3 — executable data/analysis/LLM route | Connector replay, datasets, NLP and workflow execution/evaluation/recovery | Actual local representative runs plus explicit unavailable provider states |
| S4 — prediction and adaptation | Features/splits/baselines/training/inference, CPA leakage checks, tuning feasibility and bundle loading | Real bounded CPU learning case; authorized compatible tuning/serving case or visible unmet capability gate |
| S5 — creative and product integration | Multimodal batch/review/delivery, consumed output in a real product slice | Actual available-medium production/playback/render/consumer proof; other media status separate |
| S6 — useful workbench | Scoped adapters, dynamic views, map, cost and recovery; retain service data | API and interactive desktop/mobile checks on real source-backed cases, no placeholder success |
| S7 — adoption and installation | Core/optional/role plans, before copies, known/unknown local edits, generated-agent inheritance | Actual apply journals, exact verification, preserved identity/settings and guarded rollback |
| S8 — full-route independent acceptance | Use created/discovered project agent to complete original scoped product case | Acceptance suite below with independent findings resolved or precisely left open |
| S9 — documentation and release | All affected seven guides, handbook, migration, two source bundles, Git/CI read-back | Exact commit/artifact/CI and installation/runtime/owner statuses; WORK remains deferred |

Stages are a dependency graph, not a promise to install everything before any useful verification. Begin with a representative real route before multiplying templates. Complete the remaining requested capabilities and document their individual proof state; a successful first slice does not close S8 or the whole upgrade.

## 12. Acceptance and honest limits

The [acceptance register](ACCEPTANCE.json) specifies 24 concrete cases A01–A24, inputs, expected observations and requirements. Core cases include schema drift/replay, multilingual NLP, durable LLM effects, honest forecasting, adapter identity, rejected media variants, UI recovery, generated-agent adoption and complete product use. Checks bind exact inputs and outputs; changed bytes reopen dependent proof. Freeze raw baseline/candidate cases and the task rubric before an improvement claim; include held-out/adversarial cases and different-style references, and reduce author/order bias. App profile regression covers all eleven phases and applicable references/templates/generated cases, including concepts.

Structural/source checks, deterministic execution, external-provider results, device/media experience, independent review and owner acceptance remain different facts. Existing historical verification is not rebound to new code. The release must not call an unavailable model, unexecuted LoRA job, unsupported medium or untested platform production-ready. A useful instruction can still be shipped with a precise not-yet-executed status; the requested complete implementation remains open wherever its required runtime proof is missing.

## 13. Existing installations and rollback

Before update audit all 33 core sources, nine proposed optional targets and role/global profiles against the actual installed revision. Existing stable names, UI files, icon bindings, colours, system/project class, model settings, local edits, native checkpoints and accepted decisions are kept. Absent optional sources are installed through reviewed admission; an unknown source never acquires ownership by matching a folder name. Preserve immutable before copies and actual apply journals outside discovery roots.

Existing generated agents receive a source-to-target adoption plan with applicable new resources and their own unchanged domain rules. A toolkit update is not project adoption. Keep a private denominator of actually discovered owned generated agents: inspected, adopted, conflicted, deferred and not inspected. Discover only through authorized explicit sources/bindings and supported host history; do not invent a complete private-project inventory or scan unrelated folders. Existing projects retain their platform set, research permissions and owner bans; correction of general App rules cannot reverse a particular owner's decision. No bulk migration of unrelated products is implied. Check one bounded original task after discovery. Rollback restores only owned changed files after comparing the exact post-update state; later unknown edits stop automatic rollback.

WORK live audit/install/control remains deferred. Both source bundles include the same reusable sources and handoff instructions; neither is evidence of installation in WORK. Cursor/Claude Code bridges are documented and capability-checked if available, with no claim of current installation or host parity.

## 14. Documentation and continuing operation

For every logical element provide its plain-language purpose, source, trigger, inputs, actions, output, consumer, dependencies, cost/access, tests, limits and repair/rollback route. The current [component catalogue](CURRENT-SYSTEM.en.md) and [helper catalogue](HELPERS.en.md) establish the baseline. New implementation updates those records and adds runnable examples and per-capability evidence. The complete machine index retains all helper paths, including exact duplicate groups; it does not pretend thousands of repeated resources are independent capabilities.

English remains the repository default. Ukrainian explanations are complete; all changed installation/operating guide passages are translated equivalently into every advertised guide language. Code/IDs stay stable, and the user's project language takes precedence during work. Source hashes are not linguistic or artistic certification.

After delivery monitor the product-specific failure, quality, drift, cost and user-value signals that were actually authorized. Repair compares baseline/candidate, diagnoses cause, invalidates affected proof and supports rollback. Self-maintenance follows the same authority and review rules; the orchestrator cannot authorize itself or erase an unresolved requirement.

## 15. What approval means

The exact subject is **passport `ai-data-production-evolution/0.1`**, its seven specialist selectors, four optional role profiles, compatible core/Orchestrator/service extension, full R01–R23 scope, acceptance cases and preservation boundaries. `STATUS.json` binds the final document and register hashes after review. Approval authorizes implementing, verifying, installing the reviewed Codex update and publishing it in the existing repository, within the stated limits. New paid operations and production actions still need their own concrete decisions. Implementation must not be declared complete by publishing this proposal.

Recommended reply: **“Approve AI/data/production passport 0.1 with its composition and boundaries.”** A substantive change to this passport requires a new exact revision and decision.
