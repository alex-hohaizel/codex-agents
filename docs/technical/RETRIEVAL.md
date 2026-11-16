# Retrieval and RAG

[Repository home](../../README.md) · [Engineering topics](../OPERATING_MODEL.md#engineering-topics) · [Install](../INSTALL.md) · [Illustrated retrieval workflow](../../marketing/en/README.md#showcase-retrieval)

Retrieval-augmented generation (RAG) gives a model relevant source passages for a question so its answer can cite evidence. An exact record lookup, a lexical search, or a semantic index can supply that evidence. Choose the simplest route that meets the question, access rules, and acceptance criteria.

[Worked example](#worked-example) · [Access and source freshness](#access-and-source-freshness) · [Evaluate retrieval and answers](#evaluate-retrieval-and-answers) · [Implementation choices](#implementation-choices)

## Worked example

In the fictional Global Logistics scenario, an operator asks whether a delayed shipment can be rerouted. The authorized system of record supplies the shipment's status. An approved dispatch policy supplies the rules. The answer cites the policy revision and reports the actual status observed for that shipment. [Global Logistics illustration](../../marketing/en/README.md#showcase-operations)

1. **Resolve the record by ID.** Read the shipment from the current operational API or database under the operator's permissions. Retain the observed status, timestamp or revision, and accountable owner.
2. **Find the governing document.** If the policy ID is known, open it directly. Otherwise search the allowed policy corpus by terms such as `reroute` and `dispatch approval`. Supply the exact clause and revision to the answer step.
3. **Measure misses before adding an index.** Test the same question as a paraphrase and in the languages operators use. If keyword search misses the relevant clause, evaluate semantic or hybrid ranking over the same authorized corpus. Keep exact shipment lookup for the record.
4. **Answer within the evidence.** Report the current status, cite the governing clause, and state which approval is needed. If the policy is unavailable or ambiguous, ask for the appropriate source or route the question to the responsible reviewer. Any actual reroute uses the authorized operation and verified receipt. [Tool and effect controls](../OPERATING_MODEL.md#tools-evidence-and-recovery)

| Case to replay | Expected behavior |
| --- | --- |
| An allowed shipment ID and a known policy ID | Load both exact sources and cite the current clause |
| A paraphrase changes “reroute” to “switch to a different hub” | Retrieve the applicable policy passage and retain the same source citation |
| A question arrives in a second supported language | Retrieve the same governing evidence and answer in the caller's language |
| The only match is revoked or belongs to another account | Withhold details and return the same safe response used for missing evidence |
| The shipment record changed after the answer was prepared | Reread current state before any decision or effect |

## Access and source freshness

- **Corpus.** Define the source owner, permitted readers and uses, effective revisions, retention, and withdrawal process. Keep current operational state in its authoritative system. Treat indexed passages and embeddings as derived copies. Keep retrieved text in the evidence boundary so it cannot expand the request's permissions.
- **Query and answer.** Resolve caller, account, and access scope before retrieval. Apply those constraints inside the backend query so unauthorized matches never reach the model. Validate the current source revision and access again before citation. If an embedding or reranking service receives the query or corpus, include that transfer in the authorized scope.
- **Freshness and recovery.** Associate chunks with source IDs, revisions, parser and chunking settings, embedding model and index versions, and access policy. Include those bindings in cache keys. On change, withdraw stale results and invalidate dependent caches. Verify deletion and replay withdrawal records when restoring an older copy. Keep a direct or lexical fallback for a failed rebuild.

[Knowledge skill and deletion contract](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · [Context capsule contract](../../standards/context-capsule.md)

## Evaluate retrieval and answers

Freeze allowed sources and held-out cases with expected source passages, allowed claims, and abstention behavior. Run the exact or lexical baseline and any candidate ranker with identical cases and authorization rules. Where possible, pin the prompt, answer model, and tool settings while comparing retrievers.

| Layer | What to measure |
| --- | --- |
| Retrieval | Whether relevant passages appear in the first results, how many returned passages are useful, and the rank of the first relevant passage |
| Answer | Whether each material claim follows from its cited clause and whether the response abstains when evidence is insufficient |
| Access and freshness | Denied, revoked, stale, and cross-account cases through query, answer, cache, and restore |
| Operation | End-to-end latency, query and ingestion cost, failure recovery, and the time required to withdraw content |

Choose adoption criteria before the comparison. Improve retrieval where the existing route misses relevant evidence, and require every access and protected behavior case to pass. A measured ranking improvement earns further review of the answer and its actual consumer. [Repository evals](../OPERATING_MODEL.md#evals-and-evidence) · [AI and data profiles](../../standards/ai-production.md)

## Implementation choices

The repository provides the [knowledge workflow](../../kit/skills/chatbot-atelier-knowledge/SKILL.md), [context and evidence contracts](../../standards/context-capsule.md), and [evaluation patterns](../../evaluations/README.md). Choose and operate the retrieval backend for your application. Structured queries or lexical search can already cover exact and clearly worded requests. A semantic index compares meaning via embeddings. A hybrid index combines text and embedding signals. When the comparison justifies that infrastructure, document ingestion, updates, permission enforcement, deletion, and fallback before adopting it. [OpenAI's retrieval API and ranking options](https://developers.openai.com/api/docs/guides/retrieval)
