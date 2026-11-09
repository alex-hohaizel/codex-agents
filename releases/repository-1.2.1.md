# Repository 1.2.1 / Agent Atelier 0.1.1

A real read-only smoke on 0.1.0 exposed an instruction-bootstrap failure: Codex needed the selected project's governing `AGENTS.md` sources outside the immediate task directory, while the restricted profile correctly denied unrelated ancestor reads. A path containing glob metacharacters also prevented direct exact-file permission keys. The failed attempt stopped before native thread creation; independent durable-state review confirmed zero model turns.

## Resulting behavior

Task preparation records the actual governing instruction candidates, including absence, override precedence, root markers, native loading settings and content hashes. Dispatch verifies them, admits only the exact selected regular files through service-owned per-task aliases, compares the native host's actual loaded source set and rechecks before starting a model turn. Alias paths serialize exact-file permissions; their targets are not broadened to parent directories. Instruction files remain read-only. Siblings, private service data, credentials and unrelated temporary paths stay denied.

Changed instructions/settings, unexpected links and older tasks without these pins require fresh preparation. Existing task/job history and native product files are preserved. Input-cache cleanup also removes verified instruction aliases without following or deleting their targets; pending cleanup retains the exact reviewed alias map.

The local route verifies existing ChatGPT authentication and the resolved OpenAI route before a turn. Custom providers or base URLs require their own reviewed resource route; a source file or signed-in account alone does not establish billing authority.

## Versions and evidence

The core suite stays 6.0.0; no core skill, installed icon or role model changes. The local service advances 0.1.0→0.1.1 and repository edition 1.2.0→1.2.1. Native project and service-state formats remain unchanged. Full guides retain equivalent current instructions in all seven languages. See [the patch migration](migrations/repository-1.2.1.md) and [release verification](../governance/RELEASE_6_VERIFICATION.json) for observed tests, the separately authorized single model smoke and its limits. A source implementation alone is not a successful model execution.

The separately authorized actual smoke completed exactly one OpenAI/ChatGPT turn in18,176ms, returned the random file text, preserved the whole fixture tree and removed the fixture. Independent SQL/native-event/output/source review passed. Additional model execution is not implied. Raw paths, chat IDs and private receipts remain outside this repository.
