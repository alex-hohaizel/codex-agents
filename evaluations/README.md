# Production and context acceptance

Use `production-context-cases.json` alongside the actual request, accepted reference and medium-specific production profile. A contract or score does not prove the artifact. Produce a representative real slice, independently inspect it in its intended medium, record observed failures and retest changes before wider production.

The 6.0.0 release evaluates the actual local workbench, source/context compilation, evidence admission and recovery. It does not claim that this task generated and accepted a new artifact in every medium. Image/audio/motion/document/deck/data/3D scenarios remain reusable evaluation contracts until an actual authorized product task supplies its own artifacts and observations.

Keep raw project paths, outputs, private accounts and tool traces out of reusable reports. `governance/RELEASE_6_VERIFICATION.json` contains the sanitized observed release matrix; exact private receipts stay in the audit workspace.

## Run a focused native Codex canary

Use the synthetic [case suite](native-canary-fixtures.json) and [input and receipt schema](native-canary.schema.json) from the checkout being evaluated. The cases cover a direct repair, a bilingual continuation with a project role, and a generated skill's passport and first use. The runner keeps fixture data and raw native events in a private temporary directory. Choose a new private receipt path outside the checkout. The report records source digests, actual runtime completion, artifact checks, scope changes and usage as separate facts. Redirect or retain the private scratch path for an independent reviewer.

Use Python 3.9+, Git, a supported native Codex CLI, and an existing ChatGPT login. Confirm the available model and pin it when comparing two versions. The runtime excludes personal Codex configuration and disables apps, web search and shell network in the fixture. Each run copies the selected skill into the disposable project and disables known same-name installed paths for that invocation. The runner distinguishes an exact skill body observed in tool output from a command that only shows a read at the project path. Source discovery and source reading are separate observations.

Prepare P1, P2 and the passport without making model calls:

```sh
python3 -B evaluations/native_canary.py --prepare-only \
  --case p01-direct --case p02-handoff --case p03-passport \
  --output "$private_prepare_receipt"
```

For P1 and P2, omit `--prepare-only` and use a new receipt file. P1 must add no extra work and keep the other file intact. P2 uses a persisted synthetic turn because native subagent spawn needs the parent rollout. Its trace must show the named role, a returned wait and an exact product artifact. The runner pins the role configuration path for that invocation and matches the new fixture parent's rollout and its uniquely linked child. It checks the child's exact received developer instructions and completion, and records the parent's role invocation and model separately. Other local rollouts are considered only by their parent metadata; the receipts contain no instruction text or raw events. These cases exercise actual behavior in the supplied fixtures. Broader regression coverage, implicit routing and providers require their own cases.

The constructor has an explicit review boundary. Run `p03-passport` alone. `awaiting-exact-passport-review` means the builder has returned a review request; it is an intermediate stage. Review the exact saved revision, digest, accepted inputs and effects, then continue the constructor under its documented approval contract to produce the approved single-entry `canary-invoice-checker` package. Preserve the construction receipt. With a reviewed unpacked kit and matching authorized manifest digest, run the actual installed consumer against an independent invoice fixture:

```sh
python3 -B evaluations/native_canary.py --case p03-consumer \
  --approved-kit "$reviewed_kit" \
  --approved-manifest-sha256 "$reviewed_manifest_sha256" \
  --output "$private_consumer_receipt"
```

The consumer uses the supported preflight, apply and verify commands in a fresh fixture, then opens a read-only Codex turn. Check the native command's JSON output and the captured source read. A successful manifest check, successful preparation or an intermediate review state does not establish a completed canary. Keep raw events, diagnostics, configuration, account details and scratch paths private.
