# System evolution: AI, data, ML and creative production

[Українська версія](README.uk.md)

**Audit and proposal, 10 November 2026.** The active implementation remains core 6.0.0 / Orchestrator 1.1.0 / Agent Atelier 0.2.0. Repository edition 1.3.1 adds this documentation, not the proposed capabilities. [STATUS.json](STATUS.json) records the reviewed passport hashes and its pending approval state.

The recommendation is a compatible extension: keep the existing constructors and product families; add seven reusable AI/data specialists, four optional host-role profiles, shared lifecycle/evaluation contracts and scoped panel execution. The proposed target is core 6.1.0 / Orchestrator 1.2.0 / service 0.3.0 / repository 1.4.0. These target sources have not been created or installed.

## Read in this order

| Your question | Read |
| --- | --- |
| What did the audit actually find? | [Findings and limits](AUDIT.en.md) |
| What will change, why, where and with whose authority? | [Complete passport 0.1](PASSPORT.en.md) |
| Is every item of the request covered? | [Request matrix](MATRIX.en.md) and [machine register](REQUESTS.json) |
| How will each capability work? | [Seven operational recipes and cross-cutting rules](CAPABILITIES.en.md) |
| What exists today in each skill, role and service component? | [Current component handbook](CURRENT-SYSTEM.en.md) and [source cards](current-components.json) |
| What do all the helper scripts actually do? | [Helper reference](HELPERS.en.md) and [complete index](helper-catalog.json) |
| How can we tell it works? | [24 acceptance cases](ACCEPTANCE.en.md) and [machine register](ACCEPTANCE.json) |
| What is the machine-checkable construction plan? | [Native skill.blueprint/2 proposal](BLUEPRINT.json), revision index1 corresponding to passport0.1; approval is empty |
| What informed technology choices? | [Dated primary sources](SOURCES.json) |
| How do I use the current system? | [Current full guide](../../en/GUIDE.md), [installation entry](../../../START_HERE.md) |

## How the parts fit

This is the proposed responsibility flow, not a live execution graph. Existing product state and authority remain in their native records.

```mermaid
flowchart TD
  U[Your requested result] --> O[Atelier Orchestrator: restore context and choose route]
  O --> D[Direct work or existing specialist]
  O --> P[Current project agent or App / ChatBot / Game integrator]
  O --> F[Agent or skill constructor when reuse is insufficient]
  F --> P
  P --> T[Task-specific team and owned artifacts]
  T --> A[Proposed AI specialists: data, analysis, LLM, prediction, adaptation, media, evaluation]
  A --> T
  T --> Q[Independent applicable verification]
  Q --> R[Integrated product, allowed release and operation]
  B[Agent Atelier panel: source-backed work, evidence and scoped actions] --- O
  B --- P
  B --- Q
```

The orchestrator is the entry and integration route. The constructor makes a justified new agent. Product directors lead their product. Specialists own bounded work. Subagents are actual delegated actors when the host supports them. The panel is an interface to real state and admitted actions. A ledger or validator records/checks work; an executor performs it. These distinctions prevent a generated package or an attractive panel from being mistaken for the finished product.

## What changes for a user

You can describe “turn reviews into useful product signals” or “harden this prototype” without naming internal modules. The system establishes the outcome, uses the existing product context and chooses the needed specialists. It should return an editable working result, readable evidence, limitations and a useful next action. For forecasting, it can explain that current data cannot support a trustworthy estimate. For media, it preserves approved identity through variants and actual product use. For a nontechnical team, the result includes the product's own usable interface and operational path.

The evidence standard is concrete. A model name, installed package, valid JSON or claimed expert role is insufficient. A new capability needs the implementation and the actual checks appropriate to its claim. Paid APIs, large downloads, training devices, external deployment and real-user studies retain their own access and authorization conditions. WORK live work remains deferred.

## Plain-language terms

| Term | Meaning here |
| --- | --- |
| Pipeline | Connected repeatable steps with known inputs, outputs and recovery |
| Dataset | A versioned collection of the data used for a result |
| Lineage | Which source, transformation and run produced an artifact |
| Feature | Information supplied to a predictive model at the time of a prediction |
| Label / target | The outcome the model learns to predict |
| Embedding | A numeric representation used for similarity; it does not establish truth |
| Leakage | Training or evaluation using information unavailable at the claimed prediction time |
| Baseline | A simple honest comparison that a more complex method must justify improving |
| Holdout | Data protected from model selection and used for final evaluation |
| Serving / inference | Using the saved model to produce an actual result for a consumer |
| LoRA | One way to adapt a compatible model with additional learned parameters |
| Drift | A relevant change in inputs, relationships or observed quality over time |
| Abstention | Explaining that a reliable answer or prediction cannot currently be given |
| Reconciliation | Checking the destination after an uncertain response before retrying an effect |
| Production-ready | Meets the particular product's verified operational requirements; never a universal certificate |

## Document scope

English is the default; every handbook document in this directory has a full Ukrainian counterpart. The current installation guide remains complete in all seven advertised languages. This proposal's detailed handbook is offered in English and Ukrainian; it does not advertise five nonexistent handbook translations. Source names, IDs and commands stay unchanged. Before the implemented release, every changed guide workflow must be translated equivalently.

The source baseline, current findings, proposed architecture, future acceptance plan and later implementation evidence are different records. No private product data, raw local inventory, credentials or account-specific packages are part of this handbook. The original request remains the authority; the machine registers make its coverage inspectable rather than replacing it.
