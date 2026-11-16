# Game Atelier requirements across stages

> Read [maturity, competence and authority](v4/index.md) first for the 4.0 contract, then the relevant domain sections. GA4-P1/D1/D2 extend GA3/UA26 and earlier IDs. Every complete concept needs C1 and production handoff needs T. Gather the evidence each gate requires. Preserve historical sources and approvals. Apply R6 profiles, scale, style, camera and one-time kit only to the scope where they were approved.

Carry applicable IDs into the project registry with owner, acceptance, stage and evidence and retain them through handoff. This is the family baseline, to which each game adds its own requirements. N/A needs a specific domain rationale and scope. U IDs are points from the user's request. U2.1…U2.12 are its subpoints and PS distinguishes environments.

| ID | Source | Required behavior or evidence | Stage owner |
|---|---|---|---|
| ENV-01 | U1, PS | Work and Codex split, rationale, capability report, precise next environment | director |
| ENV-02 | PS | One versioned source, plugin and local export with hash synchronization checks. Confirm distribution and discovery independently from chat or skill sync. | director |
| ENV-03 | U1, U2.8 | Mac setup, installation and doctor, dependency adapters, smoke use, uninstall and upgrade instructions | director/release |
| FLOW-01 | U1 | Complete route from studio and research through design, craft, build, QA, release and liveops, with inputs, outputs, completion and return | director |
| PACK-01 | U1,U2.11 | Portable archives with manifests, hashes, records, instructions and all required bytes | all |
| PACK-02 | U2.11 | Studio identity, approved masters, legal/public and product IDs, and licenses carry through all stages | all |
| BRAND-01 | U2.10 | Replacing the studio master with different vector art requires approval of the visual change | studio |
| BRAND-02 | U2.11 | Runbook for studio accounts, setup, ads, analytics and storage. Apply available authorized automation. Provide a precise owner bridge for unavailable MFA/legal/signing work, and verify actual status before release. | studio/release |
| IDEA-01 | U2, UA26-EXP-10 | Finite search from actual intent and variety. If the user orders 4×100, record selection criteria, outputs, and stop. Production choice remains a separate decision. | concepts |
| IDEA-02 | U2.2 | Broad appeal, core fun, novelty, learning, challenge and virality have a causal design, disconfirming case and test | concepts |
| FID-01 | U2.1,U2.5 | Exact original and hash, decomposition, source/export/node links and controlled runtime comparison | concepts/preproduction/assets/build/qa |
| FID-02 | U2.1 | Agree fidelity parameters and allowed deviations. Prove frame, motion, audio and device slice before mass production. | preproduction/assets/build/qa |
| REP-01 | U2.2 | Run beginning, middle and end, repeated attempts, mastery or meta progression, finite launch scope, late-game variety | concepts/preproduction |
| REP-02 | U2.2 | Content grammar, seed, version, constraints, solvability, diversity and fallback | preproduction/build/qa |
| PROG-01 | U2.2 | Unlock graph, dependencies, formulas, curves, player skill versus permanent power, early/mid/end progression | preproduction/build |
| PROG-02 | U2.2 | First, tenth, fiftieth and long-term return scenarios. Treat time and variants as hypotheses until tested. | concepts/qa/liveops |
| ECON-01 | U2.3 | Currency sources, sinks, exchange caps, earn curves, inflation and free path in data or simulation | preproduction/build/qa |
| ECON-02 | U2.3 | Offers bind mechanics, unlocks, sidegrades, context, cadence, price and understandable value. Give allowed advantages of time, opportunities or power a transparent calculation and separate competitive conditions under P1-C. | concepts/preproduction/qa |
| ECON-03 | U2.3 | Compare nonpayer, low payer and payer for dominance, time to unlock and failure walls. Preserve player enjoyment. | qa/liveops |
| ECON-04 | U2.3 | Paid random rewards only when chosen, with disclosed odds, duplicates, pity, audit and age/market eligibility | preproduction/release |
| ECON-05 | U2.3 | Choose pass, subscription, ads or bundles by fit. Chosen models cover all states, errors and refunds. | build/release |
| UX-01 | U2.4 | Screen, state and transition atlas from first open through menus, play, results, shop, settings, account and errors | preproduction/build/qa |
| UX-02 | U2.4 | Input, condition, state and effect, animation/audio/haptics, save, analytics and recovery | preproduction/build |
| UX-03 | derived | Accessibility, localization and Ukrainian glyphs, safe areas, thumb reach, font scaling, reduced motion, color and audio controls | preproduction/qa |
| ART-01 | U2.5,U2.7 | Coherent art bible and editable sources for universe, characters, props, material, light and UI | assets |
| PHYS-01 | U2.4,U2.7 | Per-object or body mass, collider, friction, restitution, joints and contact, fixed tick, units, input and camera | preproduction/build |
| ANIM-01 | U2.7 | Per-limb rig, weights, constraints and IK, clip curves, events, blending, contact and verified engine import | assets/build |
| AUDIO-01 | U2.6 | Music, SFX, ambience and UI audio from first menu through actions and interruptions | preproduction/assets |
| AUDIO-02 | U2.6 | Deliver the actual required music quality, session, stems, loops, transitions, effects and mix. Verify by listening. | assets/qa |
| AUDIO-03 | U2.6,U2.7 | Matching sound palette and visual motif, provenance, licenses and commercial use, available quality tool route | assets |
| HAPT-01 | U2.6 | Restrained event-specific haptics, intensity, duration, cooldown, native fallback, settings and real device tests | preproduction/build/qa |
| TOOL-01 | U2.7 | Tools chosen for actual task, quality, device, license and budget within spending authority | director/assets |
| TOOL-02 | U2.7,U2.8 | Discover, install, test and roll back required plugin/MCP/CLI. Verify the Work and Codex capability bridge. | director |
| NATIVE-01 | U2.8,U2.9 | Confirm platform scope before dependent work, document engine and renderer ADR, pin compatible toolchain | preproduction |
| NATIVE-02 | U2.8 | Android debug APK and release AAB in chosen scope with actual signing and test receipts | build |
| NATIVE-03 | U2.8 | Separate iOS Simulator .app, xcarchive, device/IPA and TestFlight outputs, with Mac, signing, UDID and access constraints | build/release |
| STORE-01 | U2.8 | Current official store, SDK, API, privacy, payment, test and metadata requirements verified at release date | release |
| CHOICE-01 | U2.9 | Resolve material choices before dependent action and retain current exact decisions | all |
| DATA-01 | derived | Save migration, rollback, conflict, offline and cloud, clock or device interruption, reproducible seeded state | build/qa |
| MONEY-01 | derived | Verify receipt, idempotent grants, restore, refund, revocation and offline pending. Distinguish sandbox tests and actual payout. | build/qa/release |
| PRIV-01 | derived | Actual data inventory, SDK consent, deletion, account and auth, privacy manifests and retention. Use applicable evidence for policy. | studio/build/release |
| PERF-01 | derived | FPS and frame pacing, memory, thermal, battery, loading and download, audio voices on representative devices | build/qa |
| QA-01 | U1,U2.12 | Actual independent reviews, requirement evidence, hashes and dependency-based regression | all |
| QA-02 | U2.2,U2.3 | Distinguish real player tests and cohorts from AI critique, simulation and desk research | concepts/qa/liveops |
| OPS-01 | U1 | Rollout, monitoring, alerts, support, incident, hotfix, rollback, forward save migration and maintenance | release/liveops |
| OPS-02 | U2.2,U2.3 | Content cadence, live economy version, kill switch and guardrails and statistical limits for experiments | liveops |
| AI-01 | U2.12 | File-based context and requirement index, selective retrieval or RAG where needed, with provenance | director |
| AI-02 | U2.12 | Resource-aware decomposition, real agents and QA by need, checkpoints and caps, changes drive repeated tests | director |
| AI-03 | U2.12 | Add orchestration, MCP, LangChain, paid APIs or vector DB only for measured task fit | director |
| LIC-01 | U2.6,U2.7 | Rights ledger for each asset, font, audio, plugin and engine, with license notices and compatibility with native runtime and store | studio/assets/release |
| GUIDE-01 | U1, PS | Human-readable step-by-step guide with commands, prompt, environment, output and next step at each stage | director |

File presence establishes only its observed property. Require scoped requirements, meaningful negative cases, actual evidence and an independent domain verdict. Treat retention and revenue targets as project hypotheses and measure them with appropriate observations.

<a id="обовязкове-уточнення-200"></a>

## Binding refinement 2.0.0

UA26-EXP-01…10 in [experience-contract.md](experience-contract.md) refine existing IDs. Keep exact origin and mapping from `assets/user-intent-sources.json`; the brief represents an interpretation. Record actual current source and scope in the project. Direct current user requirements and permission guide the accepted intent and mandatory domain constraints, specifications and execution. Preserve musts omitted from the latest request. Bring material conflicts to a decision with their effects.

Before dependent work reconcile each applicable due must, decision, knowledge item and hash. Future proof stays pending with its due gate. Missing capability blocks the relevant proof. A strong score leaves a failed must open. Trace source, requirement, interaction/progression/commerce/art, spec/asset/code, current evidence and review or acceptance. Record the source, confidence, scope and dependencies of new evidence and reopen dependent checks only.

<a id="обовязкове-уточнення-300"></a>

## Binding refinement 3.0.0

Exact excerpts of request `dd9e0086-c436-4300-b7b9-51cd0302dc42` come from `assets/systemic-user-sources.json`, dated 02.11.2026 (Europe/Kyiv). Preserve earlier IDs and sources. These checks make them concrete. Follow [systemic-design.md](systemic-design.md).

| ID / source | Due check | Downstream use |
|---|---|---|
| UA26-SYS-01 | Before each image verify a feasible visual production profile, camera/HUD/animation and source route, scene budget and element-to-assembly map. Preserve the exact chosen original and hash. Prove native/device parity at its later gate. | preproduction/assets/build/qa: source-to-runtime parity; release/liveops: accurate continuity |
| UA26-SYS-02 | For each illustrated candidate provide causal mechanics family graph, closed cross-system chains, different decisions in concrete contexts and a counterfactual. | preproduction/build/qa: executable interactions and counterfactual regression |
| UA26-SYS-03 | Map action intent, input and context to readable state. Test stable gestures, simultaneous two-thumb load, first/normal/peak HUD, anticipation, error and recovery. | preproduction/assets/build/qa: control/UI/state/accessibility contracts |
| UA26-SYS-04 | Give a meaningful additional experience hypothesis: baseline and alternative in the same situation, distinct decisions and rhythm, tradeoffs, trial and reuse, complete free or no-offer arc and a cumulative dominance counterexample. | preproduction/build/qa/release/liveops: actual offer/entitlement and cumulative fairness |
| UA26-SYS-05 | Early, middle and late play change options, understanding and goals. Show a new capability applied to an old challenge, genuinely different decisions from the content grammar, finite capacity and a reason to return. | preproduction/build/qa/liveops: unlock/content/return regression |
| UA26-SYS-06 | Contextual resources and attributes have a source, transformation, alternative cost, cue, recovery and effects in other systems. Show spending conflict and a cycle that changes decisions. | preproduction/build/qa/liveops: resource transforms/save/economy regression |
| UA26-SYS-07 | Coherent player fantasy, goals and discoveries integrate the systems into a complete multilayered game concept. | all: promised experience and scope preservation |

In Concepts apply the checks to every candidate before illustration and inspect each actual image before presentation. Later stages use the same IDs linked to exact specifications, source, code and current evidence. Structural, semantic, native, device and human acceptance require their respective evidence.
