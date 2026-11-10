# Actual native model adaptation trial

This optional, explicitly launched experiment exercises the existing ADAPTATION owner method on a real public-product feedback task. It adds no mandatory framework, skill, scheduler or operational model. The result is a **rejected operational candidate**: actual training/export/inference worked, but quality and complexity did not justify replacing the existing route. [Observed results](RESULTS.en.md) retain that distinction.

## M01 — When this route is appropriate

First restore the accepted task and existing source/identity/settings. Compare simpler available routes and measure a gap. Consider adaptation only when task data/labels, rights, native hardware, budget, evaluation and actual consuming route are available. An API prompt, retrieval or existing owner competence can remain the better method. This trial does not add claimed professional experience to an agent or assert that every task needs model tuning.

The exact trial used [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct), Apache-2.0, revision `12fd25f77366fa6b3b4b768ec3050bf629380bac`, original weights SHA256 `5af571cbf074e6d21a03528d2330792e532ca608f24ac70a143f6b369968ab8c`. The isolated prepared runtime was MLX0.32.4/mlx-lm0.32.2/Transformers5.22.2 on actual available Apple Metal. Official [MLX-LM adaptation documentation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) describes the native method; execution here used inspected installed APIs and recorded exact local artifacts. These commands download or install nothing.

## M02 — Components and actual boundaries

| Source | Responsibility | What it does not prove |
| --- | --- | --- |
| `STUDY.json` | Fixed task, weak-label policy, protected split, prompts, selection, training and resource limits | Human truth or future model quality |
| `safe_model.py` | Regular-file/path/SHA/header/tensor-offset/type/shape and configuration allocation checks before native loading | License authentication or successful model execution |
| `native_trial.py` | Explicit prepare→comparison→fit→selection→export→fresh inference phases using real MLX operations | Installation, independent review or operational adoption |
| `assess_trial.py` | Actual byte/signature/output comparison, drift, rejection and preserved route | Independent judgment or whole-programme acceptance |
| `test_loader.py` | Five generic malicious-header/format/allocation/path controls | Real training or business accuracy |

The loader supports this narrow reviewed llama/safetensors route. Its rejection of executable serialization, extra shards or other architectures does not globally remove reviewed PyTorch, other formats or other existing methods. Native MLX's optional `__metadata__: null` is accepted as non-executable absence; non-null metadata still requires string pairs. All actual model/tokenizer/template files are pinned. No unreviewed remote/custom Python is loaded. An exported tokenizer Jinja file is bounded and included in its exact native runtime-member pins.

## M03 — Frozen real task and rights

The owner's existing100-public-Codex-issue snapshot supplied actual title/body text. Earlier candidate AI category judgments supplied training/validation weak labels. The original20 reserved issues remained protected; their independent AI judgments were read for evaluation only after training and seed selection. Author groups and identical normalized bodies were joined before splitting. The actual split was64training/16validation/20test issues in63/15/20groups.

The nine existing categories are collapsed by one fixed priority into a single digit1..9. This mechanical policy is not separately human-adjudicated “main need.” Prompt text is explicitly untrusted input, truncated only within its source-text budget to188prompt tokens; training adds one label token and EOS within192tokens. No source text is followed as a tool command. Private text, author groups, labels, per-record predictions and model weights stay outside this reusable repository.

The frozen plan compares existing keyword reuse and two native base prompts before fitting. Prompt and seed choices use only validation accuracy, then macro-F1, then fixed tie rules. No heldout retuning is allowed. A later transparent majority-frequency sanity comparator was added after seed7, before seed19/heldout; it was not used to retune or select training. Its timing remains recorded instead of rewriting the original plan.

## M04 — Explicit commands

Run from the repository root. `$NATIVE_PY` is the already prepared isolated native Python, `$MODEL` the exact reviewed local directory, `$RT05` the authorized private source snapshot, and `$TRIAL` a new private output directory outside this repository. Read source rights and `STUDY.json` first. New costs/downloads/installation need their own actual authorization. `prepare` refuses an existing frozen plan; completed/unknown training attempts cannot be silently rerun.

```sh
python3.13 evaluations/ai-production/real-world/model-adaptation/native_trial.py prepare --model "$MODEL" --rt05 "$RT05" --out "$TRIAL"
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py compare --model "$MODEL" --rt05 "$RT05" --out "$TRIAL"
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py fit --model "$MODEL" --seed 7 --out "$TRIAL"
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py fit --model "$MODEL" --seed 19 --out "$TRIAL"
python3.13 evaluations/ai-production/real-world/model-adaptation/native_trial.py choose --model "$MODEL" --out "$TRIAL"
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py export --model "$MODEL" --variant merged --out "$TRIAL"
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py export --model "$MODEL" --variant quantized4 --out "$TRIAL"
```

Each `fit` performs30actual iterations, batch1, rank4 LoRA on q/v projections of the last4layers, Adam1e-4, prompt-masked loss and gradient checkpointing. Two seeds total60iterations. Process checks enforce≤60seconds per command,1GiB MLX allocation and2GiB process RSS; the combined training upper bound remains below600seconds and private trial disk below2GiB. These are isolated evaluation caps, not a deployment SLA. HF offline mode and disabled telemetry prohibit a hidden network model acquisition.

For each `base`, `adapter`, `merged`, `quantized4`, run this command in a fresh native process, substituting `$VARIANT` with the exact enum:

```sh
"$NATIVE_PY" evaluations/ai-production/real-world/model-adaptation/native_trial.py evaluate --model "$MODEL" --rt05 "$RT05" --variant "$VARIANT" --out "$TRIAL"
```

Every variant actually loads its own pinned weights/tokenizer and produces20constrained classifications plus a separate maximum4token free-generation probe. The merged and4bit exports are actual native weight files, not JSON substitutes. Class, logit and generation parity are measured separately; quantized bytes never inherit another export's proof.

```sh
python3.13 evaluations/ai-production/real-world/model-adaptation/assess_trial.py --model "$MODEL" --rt05 "$RT05" --out "$TRIAL"
python3.13 -m unittest discover -s evaluations/ai-production/real-world/model-adaptation -p test_loader.py -v
```

## M05 — Observed checkpoint recovery

During this actual trial seed7 completed all30iterations and wrote its real adapter; post-save inspection then rejected native null metadata. The checkpoint, failed attempt, full log, old source bytes and frozen plan were retained. The narrow compatibility repair used an explicit `execution-revision.json` binding previous/current code and loader hashes while retaining the unchanged study. The reviewed `recover` command fresh-loaded and validated the existing seed7 checkpoint; it did not retrain. It is specific to that recorded failure, not a generic bypass or a step for a new successful trial.

Seed7's old per-iteration resource guards all returned, but its exact old telemetry was not persisted. The record preserves this gap and its≤60second/1GiB/2GiB guard bounds rather than inventing peak values. Seed19 durably saved each actual monitor observation. Code changes never relabel old training as execution of new bytes; source-bound recovery/export/inference have new proofs.

## M06 — Adoption and preservation

Actual signatures bind the exact base, tokenizer, adapter, input/output policy, plan, execution revision and inference-report bytes. Wrong base hashes and changed base/tokenizer/adapter/report bindings are rejected. Generic tests cover unsafe metadata, serialization/link/path/extra-shard/index escape, nonfinite/duplicate JSON and excessive allocations. The trial does not deliberately allocate unsafe memory to “test” a crash.

The original base files and explicit `existing-owner-human-review` route remain unchanged; no skill, model or service was installed or activated. The actual selected LoRA is rejected against simpler comparators, and4bit serving drift is retained. Missing human labels, tiny protected samples and weak primary-policy labels prevent a production accuracy claim. Independent review, project adoption, owner acceptance and original29case closure remain separate root-owned decisions.
