# Actual native adaptation results — 2026-11-10

Native local model adaptation, export and fresh-process inference were actually executed. **Operational LoRA adoption is rejected** for this task. The existing owner/human-review route remains unchanged. Successful training is not a quality improvement.

The exact model/runtime and reproduction are in [README.en.md](README.en.md). The actual source was the existing100public-issue product-feedback snapshot, with64training/16validation/20original protected test issues. Labels are earlier AI judgments; the test reference is a separate independent AI judgment, not human truth. One fixed priority collapses the existing nine categories to a digit, which may obscure a user's main need. No private chats or human-label accuracy are claimed.

| Validation16issues | Accuracy agreement | Macro-F1, nine labels |
| --- | ---: | ---: |
| Reused existing keyword rules |31.25%|0.1243|
| Native base, simple prompt |25.00%|0.0468|
| Native base, semantic prompt |25.00%|0.0468|
| Native LoRA seed7 |25.00%|0.0468|
| Native LoRA seed19 |31.25%|0.0741|

The semantic prompt won the fixed tie rule before training. Two actual native Metal LoRA fits each ran30iterations, batch1, max192tokens, rank4 on q/v of the last4layers:60iterations total and30720trainable adapter parameters per seed. Seed19 was selected by validation only. A transparent training-majority sanity comparator added after seed7, before seed19/heldout, scored50% validation agreement; it never altered training choices.

| Original protected20test issues, independent AI reference | Accuracy agreement | Macro-F1 |
| --- | ---: | ---: |
| Existing keyword reuse |35.00%|0.1668|
| Training-majority sanity |45.00%|0.0690|
| Native base |5.00%|0.0106|
| Actual native LoRA adapter |5.00%|0.0123|
| Actual merged native weights |5.00%|0.0123|
| Actual merged4bit weights |5.00%|0.0117|

The small model and this brief weak-label protocol do not solve the triage task. Falling loss and a better-shaped one-digit generation are insufficient. The result supports keeping the existing expert/human-review route and improving data/evaluation before considering a different model study. It does not establish that LoRA is generally ineffective, or that any better existing capability should be removed.

Actual artifacts remained private:

| Artifact | Bytes | Actual SHA256 |
| --- | ---: | --- |
| Selected seed19 adapter |124556|`31a2db88cbd7341b88edcc2d0b2a650417eebb13fabcab4e3adbd67d48ff7e17`|
| Merged native weights |269060381|`1e7858cb752a2d1a172300dfee6c71237adef8665e16af7b420c4ded4e4053cc`|
| Native4bit weights |75790438|`8fd0969d271cae1b05de0677d8d73d5554d3aff5bf2a5ca0d177f04838f8c5f4`|

Each form had its own fresh native load,20classifications and separate maximum4token free-generation probe. Adapter→merged class outputs matched20/20; maximum label-logit absolute difference was0.25 and the free-generation text matched. The4bit form changed1/20classes, maximum logit delta3.125, and free-generation text differed. **The4bit form is not admitted as serving-equivalent.** A smaller file is not compensation for that observed drift.

Seed7 finished actual training but hit a post-save native-null-metadata checker mismatch. Its real checkpoint/log/old code were preserved; a narrowly pinned compatibility revision recovered it through fresh native loading without retraining. Its exact old telemetry was unpersisted and stays unclaimed; all30per-iteration≤60second/1GiB MLX/2GiB RSS guards returned. Seed19's durable full phase took7.86seconds with peak432585001MLX bytes and243466240RSS bytes. Recorded inference/export phases stayed below5seconds each; recorded native peaks were below433MB and RSS below421MB. The actual trial retained about352.5MB of private artifacts, excluding the separately prepared base/runtime. No extra download or spending was made by this worker.

Actual base SHA mismatch and changed base/tokenizer/adapter/inference-signature bindings were rejected. Five generic malicious-header/allocation/path/serialization tests passed. Original base/tokenizer bytes and the explicit human-review route stayed unchanged. No global installation, operational activation, provider API, deployment, paying users, independent release certification or complete29case acceptance is claimed.
