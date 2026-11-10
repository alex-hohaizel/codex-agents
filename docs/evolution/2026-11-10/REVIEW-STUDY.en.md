# Real case: public feedback about long-running agent work

[Українська](REVIEW-STUDY.uk.md) · [Implementation](IMPLEMENTATION.en.md) · [Conditional methods](IMPLEMENTED-COMPONENTS.en.md)

The owner selected public review/need analysis and delegated a challenging product choice. We selected **Codex Desktop feedback** because task continuity, agent control and project navigation directly inform the existing Atelier workbench. The useful output is an evidence-linked set of product needs and verification actions. It is not a diagnosis or repair of Codex itself.

## Data and method

Four bounded GitHub search pages returned 100 distinct issues for `repo:openai/codex is:issue label:app created:2026-10-01..2026-11-10`, sorted by creation descending. Although the search interval is longer, the actual newest-100 collection covers **9 November 2026 08:59 UTC to 10 November 2026 11:21 UTC**, about 26 hours 22 minutes. The search reported 5,746 matches. This is deliberately **partial coverage**, not a complete month or a random sample of users.

The snapshot contains 98 open and two closed issues and 98 anonymized author groups. An account group is not proof of one person or one independent incident. The classifier did not receive closure reasons; closed status was not treated as evidence that a defect had been fixed. No comments, attachments, private diagnostics or new training labels were collected. Raw responses, bodies, author records and local execution receipts stay outside the reusable repository.

A frozen transparent keyword baseline was compared with semantic classification of all 100 actual title/body records. Every semantic row retained its source URL and a literal evidence excerpt of at most 25 words. Reported problems, proposed features, inferred needs and verified causes were kept distinct; unclear reports stayed in the denominator. A separate actor reviewed 20 reserved records without seeing the candidate or baseline outputs. This was **independent AI judgment**, not human ground truth or statistically independent model behavior.

| Comparison against that one AI reviewer | Keyword baseline | Semantic output |
| --- | ---: | ---: |
| Reviewed records | 20 | 20 |
| Exact category-set agreement | 0 | 12 |
| Extra labels relative to the reviewer | 68 | 6 |
| Omitted labels relative to the reviewer | 6 | 2 |
| Micro-F1 agreement | 0.448 | 0.895 |

These numbers measure agreement for this frozen sample and label guide. They are not validated accuracy, market prevalence, proof of a causal benefit, or a comparison of Agent System 6.0 against 6.1. Existing host competence performed the semantic work; a new profile or framework cannot be credited with the difference. Eight category-set disagreements remain visible rather than being tuned away after evaluation.

## Eight useful needs for Atelier

The priorities below are our interpretation of user-control and work-loss risk in Atelier. Frequency alone does not determine them. The linked reports are first-party claims by their authors, not confirmed shared root causes.

| Need | Representative public reports | Implication and concrete check for Atelier |
| --- | --- | --- |
| **N1 · P0: resume the same actionable work** | [Original conversation recovery, #60564](https://github.com/openai/codex/issues/60564); [safe handoff at a quota boundary, #60447](https://github.com/openai/codex/issues/60447) | Preserve identity, current task/checkpoint, pending decisions and unknown effects. Reopen the same bounded task after restart and verify which action remains allowed; do not silently replace the original work with a new empty chat. |
| **N2 · P0: understand effective tools and limits** | [Unified tool-management request, #60374](https://github.com/openai/codex/issues/60374); [displayed network state versus actual denial, #60449](https://github.com/openai/codex/issues/60449) | Separate declared, installed, discovered, callable and observed states, with route/source/time. Check a real permitted operation and a denied one; explain the actual boundary without assuming owner approval overrides host restrictions. |
| **N3 · P0: stop owned work and confirm the result** | [Producer task versus child process, #60411](https://github.com/openai/codex/issues/60411); [reported sound continuing after stop, #60520](https://github.com/openai/codex/issues/60520) | Show requested, stopping, stopped/partial/unknown for the scope actually controlled. Verify the host’s terminal receipt and residual owned work. These reports concern different subsystems; Atelier cannot claim control of an unsupported external process. |
| **N4 · P1: truthful operation receipts** | [Reported timestamp without delivered image, #60415](https://github.com/openai/codex/issues/60415); [timeout with possible later effects, #60386](https://github.com/openai/codex/issues/60386) | Keep target/revision/effect identity and observed evidence. A submitted request or timeout is not confirmed delivery or proof that nothing happened. Test reconciliation before retry. |
| **N5 · P1: a portfolio with identity and coverage** | [Project organization reportedly disappearing, #60509](https://github.com/openai/codex/issues/60509); [archive-search request, #60566](https://github.com/openai/codex/issues/60566) | Preserve source-backed project/work grouping and show freshness, unavailable sources and actual search coverage. Test active/archive/partial history and an inaccessible source; zero returned rows must not become “no previous work.” |
| **N6 · P1: understandable usage and safe handoff** | [Usage explanation request, #60413](https://github.com/openai/codex/issues/60413); [context/compaction/cache visibility, #60538](https://github.com/openai/codex/issues/60538) | Show only usage/context data actually exposed, with unknown attribution visible. Keep quota, provider capacity, cumulative input and current context distinct. Test a bounded stop/handoff without inventing spare tokens or billing explanations. |
| **N7 · P1: readiness for the actual operation** | [Listing versus attaching/reading a browser tab, #60543](https://github.com/openai/codex/issues/60543); [window discovery versus screenshot, #60485](https://github.com/openai/codex/issues/60485) | Discovery, initialization, invocation, consumption, render/export and delivery need separate evidence. Run a real supported operation and inspect its consumer; a tool name or returned bytes cannot certify an image or editable artifact. |
| **N8 · P2: retain input and reading position** | [Unconfirmed annotation lost on keyboard send, #60403](https://github.com/openai/codex/issues/60403); [viewport movement while streaming, #60570](https://github.com/openai/codex/issues/60570) | For surfaces Atelier owns, preserve unsent input and stable item/reading identity. Test keyboard submission with a failed send/retry, then read during streaming and older-item loading. This does not repair another application’s closed composer. |

The underlying private analysis retains all 100 records, eight need groups and 47 linked corpus sources. The table publishes selected paraphrases, not complete bodies or an exhaustive public dataset. Similar journeys were grouped without declaring issues to be duplicates or assuming a common technical cause.

## Actual use and evidence boundaries

The case gives the existing Atelier work a concrete consumer: context recovery, current-decision/source-status clarity, operation receipts, bounded history continuation and honest capability state. Related priority UI/context changes have their own source, browser and independent-review evidence in [the implementation record](IMPLEMENTATION.en.md). This correspondence is useful design input; it is not causal proof that the public study produced those code changes, nor a claim that every proposed action is implemented.

Four actual derived records were checked: `SourceContract`, `DatasetManifest`, `EvaluationPlan` and `EvaluationReport`. The dataset deliberately remains **partial: 100 of 5,746 matching issues**. The evaluation deliberately remains **incomplete: 12 agreeing category sets and eight disagreements**. Controls that falsely claimed full coverage, rebound old evaluation to a changed plan, or used another project were rejected. This establishes the local record checker’s stated behavior, not rights authentication, completed business validation or model accuracy.

No new NLP framework, global vector index, paid provider API, model training or automatic background monitor was required. Actual usage/billing was not established as zero. The feedback case does not supply advertising CPA labels, justify LoRA, prove model serving, diagnose the unbound Svitlobot failure or close all 17 system capabilities. Those required gates remain open rather than being replaced by this successful bounded study.
