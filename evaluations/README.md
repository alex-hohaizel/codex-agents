# Production and context acceptance

Use `production-context-cases.json` alongside the actual request, accepted reference and medium-specific production profile. A contract or score does not prove the artifact. Produce a representative real slice, independently inspect it in its intended medium, record observed failures and retest changes before wider production.

Test the actual local workbench, source and context compilation, evidence admission, and recovery in the relevant environment. Media, device, model, and provider outcomes each require their own fixtures and observations.

Keep raw project paths, outputs, private accounts, and tool traces in private evaluation records. Record the reproducible scope and public assertions in [verification guidance](../governance/VALIDATION.md).

## Exercise the production choice lifecycle

The [production choices guide](../docs/technical/PRODUCTION_CHOICES.md) pairs project decisions with exact accepted inputs, actual implementation and separate review. Use the [coverage map](../governance/production-choice-coverage.json) to find the affected new and historical routes.

- [Review queue and recovery](fixtures/production-choice-technical/README.md) exercises concurrent delivery, role refusal, maintenance, migration and readback from a restored backup.
- The [review cabinet and editorial campaign](fixtures/production-choice-web/requirements.md) share controlled inputs but test separate product workflows and compositions. Open the actual browser pages and exercise the defined interactions.
- [Game import and runtime](fixtures/production-choice-game/README.md), [audio production](fixtures/production-choice-audio/RIGHTS.md), [local feed integration](fixtures/production-choice-integration/README.md), and [uncatalogued runtime](fixtures/production-choice-uncatalogued/README.md) cover their actual consumers.

Keep reproduction outputs outside the reusable source tree. Review the intended target, exact source and tool versions before claiming an outcome.

## Run a focused native Codex canary

Use the synthetic [case suite](native-canary-fixtures.json) and [input and receipt schema](native-canary.schema.json) from the checkout being evaluated. The cases cover a direct repair, a bilingual continuation with a project role, and a generated skill's passport and first use. The runner keeps fixture data and raw native events in a private temporary directory. Choose a new private receipt path outside the checkout. The report records source digests, actual runtime completion, artifact checks, scope changes and usage as separate facts. Redirect or retain the private scratch path for an independent reviewer.

Use Python 3.9+, Git, a supported native Codex CLI and an existing ChatGPT login. Managed native runs read both settings from the release record and request GPT-6.2 Sol Ultra. An alternate effort is accepted only on an explicit historical baseline lane. [Release record](../releases/current.json) The runner forwards allowlisted process variables and uses the existing native sign-in. It skips personal Codex configuration and disables apps, plugins, hooks, memory tools, web search and shell network. The fixture gets a copied project skill, with known same-name skills disabled and ambient skill folders denied. The write profile keeps workspace protections and allows writes inside the test project. General temporary directories are read-only. A receipt distinguishes an observed project path from an exact skill body captured in a tool result.

Prepare P1, P2 and the passport without invoking a model.

```sh
python3 -B evaluations/native_canary.py --prepare-only \
  --case p01-direct --case p02-handoff --case p03-passport \
  --output "$private_prepare_receipt"
```

Run the direct repair from the repository root.

```sh
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct \
  --output "$receipt_dir/direct.jsonl"
cat "$receipt_dir/direct.jsonl"
```

The expected change replaces `cheklist` with `checklist` in `README.md` and preserves the original `notes.md`. The direct repair and consumer run use ephemeral native chats by default. Add `--persist-model-receipt` to explicitly retain a disposable chat for exact model and effort readback from its typed `turn_context` event. Raw traces and diagnostics stay private. An ephemeral run records its artifact outcome and leaves the effective model unverified. A missing or different model or effort in a persisted run blocks model acceptance.

Run P2 with `--case p02-handoff` and a new receipt path. This fixture uses a persisted synthetic turn for linked native role evidence. Its trace must include one named role, a completed wait and an exact output artifact. The runner identifies the child from the exact parent’s native tool activity, matches the child’s parent reference, checks the child’s received developer instructions, and records the child’s model, effort and completion.

For an explicit model comparison, use `--stage baseline --baseline-source "$reviewed_checkout" --model "$observed_baseline_model" --effort "$observed_baseline_effort"` and a new receipt path. For exact model comparison, add `--persist-model-receipt` on both runs. Run the candidate on the current checkout with the same fixture parameters and criteria. Keep the actually observed model, source inventory, runtime, usage and protected file observations for each lane.

The constructor has an explicit review boundary. Run `p03-passport` alone. `awaiting-exact-passport-review` means the builder has returned a review request; it is an intermediate stage. Review the exact saved revision, digest, accepted inputs and effects, then continue the constructor under its documented approval contract to produce the approved single-entry `canary-invoice-checker` package. Preserve the construction receipt. With a reviewed unpacked kit and matching authorized manifest digest, run the installed consumer against an independent invoice fixture.

```sh
python3 -B evaluations/native_canary.py --case p03-consumer \
  --approved-kit "$reviewed_kit" \
  --approved-manifest-sha256 "$reviewed_manifest_sha256" \
  --output "$private_consumer_receipt"
```

The consumer runs preflight, apply and verify in a fresh fixture before opening a read-only native turn. Check the actual JSON emitted by the installed script, the project skill read, the typed model receipt and the terminal turn.


## Project replan and Builder delivery

`replan_delivery.py` prepares a disposable Git project containing a runnable
FieldSlate WSGI app, a historical result and ongoing independent work. The
`apply` stage checks the proposed plan, exact authorized test decision, write
and readback, same-operation replay and stale competing decision. The separate
`builder` and `qa` native stages use fresh Codex sessions. Builder receives
exact write paths. QA exercises the application through both routes and checks
the actual returned implementation digest. Use a supported signed-in Codex CLI for the native stages. Add
`--persist-model-receipt` for a disposable Builder rollout with model readback. Keep raw session evidence under the selected private
case directory. To compare exact released settings, pass `--baseline-source` at preparation and `--baseline-replay --model` and `--effort` with the recorded settings while running that baseline’s native stages.

```bash
python3 -B evaluations/replan_delivery.py --help
```


## Planning and worktree comparisons

`planning_probe.py` takes a reviewed Orchestrator source for the baseline and uses the current source for the candidate. When explicitly replaying an earlier model, select `product-baseline` and pass the recorded `--model` and `--effort`. Use `--persist-model-receipt` on both lanes when comparing observed models. Evaluate the returned plan against the same protected files and requirements. A successful observation still needs artifact review.

`worktree_delivery.py` binds independent write scopes to two real Git worktrees and observes their overlap, interruption, durable checkpoint, fresh-session recovery, integration readback and independent QA. Run it under a disposable system temporary directory on a supported POSIX host. Worker runs are ephemeral by default. Add `--persist-model-receipt` for model readback. Freeze the model receipts and product oracles alongside the artifact hashes. The captured-review replay verifies the existing reviewed fixture using its original evidence.
