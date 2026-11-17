# Comparing Codex workflows on the same task

A comparison keeps the case, inputs, model, effort, scope and budget fixed. Run
each variant in a separate project copy and retain its source pins, raw native
events and reviewed result. Include failures and incomplete runs. The local
comparator checks whether the submitted evidence supports a comparison.

## Run the evidence check

The four variants are bare Codex, pinned BMad Stable, the current released
Codex Agent System and the candidate. Keep independent review records and log
output changes. Keep matched reports out of a public package if they include
private project or account details.

```sh
python3 -B evaluations/compare_codex_results.py \
  --root "$EVIDENCE_ROOT" --case case.json \
  --receipt bare-codex=runs/bare.json \
  --receipt bmad-stable=runs/bmad.json \
  --receipt codex-agents-stable=runs/stable.json \
  --receipt candidate=runs/candidate.json
```

`EVIDENCE_ROOT` is an absolute canonical directory with pinned input and scope
files. A case with schema `atelier.codex-comparison/1` declares those file pins,
the common model and effort, maximum time and input/output token budgets,
required check IDs, the four variant source digests, and the registered observer
and reviewer IDs.

An `atelier.codex-comparison-run/1` record identifies the case, exact case
digest and variant. It records the input, source and scope digests, common
constraints, observer and reviewer, the native thread ID and a pinned JSONL
trace, wall time and token counters, and a result with pinned evidence for
each required check. See the [contract tests](../../evaluations/tests/test_compare_codex_results.py)
for complete temporary data. Each file reference uses a relative path and its
SHA-256.

The comparator cross-checks native thread, terminal outcome and reported token
counts against the event files. A recorded failure remains a result in the
comparison. Missing, invalid or unmatched artifacts leave the report incomplete.
Exit 0 means the data is comparable, exit 1 means incomplete and exit 2 means
the case could not be evaluated. An evaluable report does not authenticate
producer identity, model choice, permissions or human independence. Check these
at the actual operation and review. A single pilot on every variant does not
establish repeatable superiority.

## Small planning pilot

`evaluations/bmad_planning_probe.py` gives the three baseline lanes the same
label-export source, compatibility rules and planning task. It creates
disposable projects and can execute one named lane when supplied with a valid
local Codex login, the specified model and an admitted BMad distribution. BMad
Method 6.12.4 uses its own project-local installer and requires uv with Python
3.11 or newer to render the planning workflow. Admit the exact dependency
artifacts independently. [BMad installation](https://github.com/bmad-code-org/BMAD-METHOD/blob/bab9082c3e884e0d72c759bcd1a6d90bcc01be84/docs/start/install-bmad.md)

The BMad planning lane is evidenced by a successful render and the written
`ready-for-dev` specification. The planning probe preserves final messages,
changed paths, trace hashes and usage for adjudication. Review the actual plans
against the compatibility rules before recording any comparison. A changed
product file, a missing output or a failed run remains visible.

A Git fixture exercises the BMad Git preflight, which needs to refresh the index.
A protected Git directory can yield a valid blocked result there. The probe also
supports a separate `prepare --no-vcs` case. Its lanes use the same pinned files
without Git, and BMad follows its documented path when version control is absent.
Keep results for those two cases separate.
