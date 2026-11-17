# Review Codex runs on a frozen task

Run bare Codex, the released product, and the candidate in separate copies of
one project. Keep the same task, model, reasoning effort, permissions and
budget. Register an observer to collect what happened and a separate reviewer
to check the outputs. Retain mismatches, unverified checks and failed runs.

## Check the evidence

```sh
python3 -B evaluations/compare_codex_results.py \
  --root "$EVIDENCE_ROOT" --case case.json \
  --receipt bare-codex=runs/bare.json \
  --receipt product-baseline=runs/baseline.json \
  --receipt candidate=runs/candidate.json
```

Use a canonical absolute evidence directory. Save the task and scope profile
as pinned files. A case with schema `atelier.codex-comparison/2` declares
the case ID, task and scope pins, common model and effort, maximum wall time
and token counts, required check IDs, observer and reviewer IDs, and the
source SHA-256 for each variant. A case may additionally declare a
`reference` source under the same terms. Supply its `--receipt` only when
the case declares that variant.

Each `atelier.codex-comparison-run/2` receipt binds the exact case, input,
scope and source. It records the observer and reviewer, native thread UUID,
terminal state and pinned JSONL trace, wall time, token counters, and an
evidence result for each check. Use relative paths and SHA-256 digests.
The contract tests provide a complete example with temporary data. Keep
private observations with their project. [Evidence fixtures](../../evaluations/tests/test_compare_codex_results.py)

The checker matches the native thread, terminal event and token counts
against the trace. It detects a reused native thread. An observed failure
remains in the result. Exit 0 means the declared runs include complete
evidence, including any failures. Exit 1 means evidence is incomplete.
Exit 2 means the case, scope or CLI input is invalid. The reviewer checks
the authenticity of events, actor independence and the actual output.
Historical receipts keep their original format and source pins.

## Run the small planning pilot

`evaluations/planning_probe.py` prepares a task that adds case-insensitive
label deduplication while preserving the first spelling, original order and
public function signature. The task calls for a plan. It asks for exact
checks for whitespace and Unicode without editing the protected files.

Set `BASELINE_SKILL` to the Orchestrator directory from the reviewed
release. The candidate defaults to the Orchestrator source in the current
checkout. Use the installed Codex CLI with local sign-in.

```sh
case_parent="$(mktemp -d)"
case_dir="$case_parent/planning"
python3 -B evaluations/planning_probe.py prepare \
  --case-dir "$case_dir" --baseline-source "$BASELINE_SKILL"

for route in bare-codex product-baseline candidate; do
  python3 -B evaluations/planning_probe.py run --case-dir "$case_dir" \
    --variant "$route" --model "$CODEX_MODEL" --effort low
done
```

Each lane records the staged source inventory, requested model, native
thread events, changed paths, time, usage and final plan when available.
Have the reviewer open the plans and check the original compatibility
rules. Use a fresh case if recreating a run. The `prepare --no-vcs` mode
creates the same case without Git metadata, using the pinned compatibility
rules. Keep its observations with that case.

### Optional local reference route

An operator can stage an independently reviewed, project-local skill
directory using `prepare --reference-config`. The JSON descriptor uses
schema `atelier.planning-reference/1`, canonical absolute `source`
directory, `skill` from the skill's exact front matter, and the approved
`source_sha256` computed from its file SHA-256 and permission inventory
in sorted JSON. Inspect the directory and digest before staging. The
descriptor can additionally set a relative `artifact_directory`,
`ready_status`, and a literal `observed_command` to look for among
successful commands in the native trace. The runner records these
observations for review. Provide any separately prepared native reference
receipt directly to the evidence checker with the matching frozen case.
