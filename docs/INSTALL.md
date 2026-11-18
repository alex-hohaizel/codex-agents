# Install Codex Agent System

[Repository home](../README.md) · [Your first task](../START_HERE.md#install-and-verify) · [Component versions](../releases/README.md)

Start with the 33 core skills. Add the managed Codex profile and twelve role definitions when you need the provided roles. The ready installer includes Atelier Orchestrator, the profile and roles. The maintenance skill and optional Agent Atelier workbench retain separate controls. [Current component versions](../releases/current.json)

## Recommended: local browser installer

1. Open the [latest stable Release](https://github.com/alex-hohaizel/codex-agents/releases/latest) and download its **ready Universal installer**, or the ready asset matching your OS and CPU. The Universal archive carries Windows, macOS and Linux runtimes for x64 and ARM64. Check the release's declared platform minimums and exact native test receipts. GitHub's automatic **Source code** ZIP is source material: its HTML start page directs you to the ready assets; it is not the bundled installer.
2. Extract the complete ZIP into a normal folder. Open `START_HERE.html` or `ПОЧАТИ.html` for the visual directions, then open the launcher below. The launcher starts a private local browser wizard. Opening HTML alone cannot install files. Keep all folders from the archive together.

   | Your system | Installer | Optional workbench |
   | --- | --- | --- |
   | Windows x64 / ARM64 | `Start.cmd` | `Start-Workbench.cmd` |
   | macOS Intel / Apple Silicon | `Start.command` | `Start-Workbench.command` |
   | Linux x64 / ARM64 | `Start.sh` | `Start-Workbench.sh` |

   Ready assets include Python, Node and the built interface. No separate Python/Node install, npm build or administrator installation is required for this route. On Linux, a file manager may require **Allow executing file as a program**; the terminal equivalent is `chmod +x Start.sh` followed by `./Start.sh`. macOS extraction tools that drop executable flags may similarly need `chmod +x Start.command`. Follow your OS trust policy and the release's signing status; package checksums do not establish a product code-signing identity.
3. Choose **Check now**, then **Prepare plan**. Review the component actions, destination folders, existing local changes and exact plan identity. The normal selection is **33 core skills + Atelier Orchestrator + managed profile + twelve roles**. Unknown changes remain conflicts. Check the approval box and choose **Install reviewed plan** only for that reviewed plan.
4. Choose **Verify files**, then **Check in Codex**. Files, fresh native discovery, account authentication and a completed task are separate observations. Codex must be installed and authenticated with your own account for native use; model/provider charges and project-specific SDKs remain separate.
5. Choose **Create practice project**. Use **Open folder** to inspect the new files, **Open Codex** to request opening its generated launcher, and **Copy prompt** to paste the task into that Codex session. Compare the repaired heading and preserved note yourself. Preparing/opening the project does not run a model. [First useful task](FIRST_RUN.md)

The wizard is available in English and Ukrainian; the seven language guides explain the same route. Setup keeps its owned plans, retained package and recovery journals under `~/.local/share/codex-agent-system` by default, including on Windows beneath the selected user home. It preserves unrelated skills and project files. Keep that state and your entitlement document when moving or updating a package. **Continue or recover** reads actual journals after a refresh or interruption; explicitly select the checked operation before resume, rollback or uninstall.

The bundled runtime is for Agent System helpers. Generated Codex launchers preserve an existing project/virtual-environment Python and Node in PATH. When no legitimate Python exists, the bundled Python supplies a fallback; Windows Store execution aliases are not treated as a working interpreter. `AGENT_SYSTEM_PYTHON` and `AGENT_SYSTEM_NODE` identify the exact retained toolkit runtimes. Use those variables for toolkit helpers, and the project's declared interpreter for project builds and tests. No global PATH or registry change is made.

For CLI setup without installing Python separately, use the platform's `Start` launcher with `--help` and the documented `doctor`, `audit`, `install`, `verify`, `discover`, `operations`, `prepare-first-task`, `rollback` and `uninstall` commands. It invokes the same engine and approval-bound journals as the wizard. The [buyer guide](commercial/BUYER_GUIDE.md) covers commercial delivery trust and rights; a public technical release does not activate a shop or finalize seller terms.

## Advanced source and signed core route

The following procedures remain available for source inspection, separately controlled core/profile installation, and existing administrator automation. They are distinct from the bundled browser installer above.

## Before

- Open a Codex session with access to the intended local skill directories. On macOS or Linux, the commands below use Bash, Python 3.9+, Git, and an authenticated GitHub CLI (`gh`). A workbench source build additionally uses its documented Node/npm prerequisites; ready workbench assets carry their runtimes.
- Use the official stable GitHub release and its `CODEX` asset. GitHub’s generic source archive is useful for source inspection and isolated rehearsals. The signed release archive is the input for managed installation. [Stable release](https://github.com/alex-hohaizel/codex-agents/releases/latest)
- Choose `fresh` for an empty managed core install. Use the verified installed core version for a recognized existing suite. The audit will stop on unknown local changes or ambiguous sources. Keep setup files and journals outside skill-discovery roots.

## Steps

### Stage the official archive

Set `setup_mode` to `fresh` or to the installed suite version you verified. This block selects the published stable release, fixes its tag and commit for the entire operation, and checks out the portable tools from that commit. It reads the archive digest from GitHub’s release metadata and the manifest pin from that commit’s release record. The verifier checks the attestation against the archive, repository, commit, source ref, and workflow.

```bash
setup_mode=fresh
setup_dir="$(mktemp -d)"
(
  set -eu
  cd "$setup_dir"
  repository=alex-hohaizel/codex-agents
  tag="$(gh release view --repo "$repository" --json tagName,isDraft,isPrerelease \
    --jq 'select(.isDraft == false and .isPrerelease == false) | .tagName')"
  [ -n "$tag" ]
  commit="$(gh api "repos/$repository/commits/$tag" --jq .sha)"
  git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repository.git" source
  git -C source sparse-checkout set --no-cone \
    /scripts/ /kit/portable/ /kit/manifest.json /releases/current.json
  git -C source checkout --quiet --detach "$commit"
  [ "$tag" = "$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["release_tag"])')" ]
  manifest_digest="$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["source_manifest_sha256"])')"
  suite="$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["suite_version"])')"
  edition="$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["repository_version"])')"
  [ "$manifest_digest" = "$(python3 -c 'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("source/kit/manifest.json").read_bytes()).hexdigest())')" ]
  asset="Agent_System_${suite}_CODEX.zip"
  archive_digest="$(gh api "repos/$repository/releases/tags/$tag" \
    --jq ".assets[] | select(.name == \"$asset\") | .digest")"
  gh release download "$tag" --repo "$repository" --pattern "$asset"
  if [ "$setup_mode" = fresh ]; then
    set -- --fresh-install
  else
    set -- --installed-suite-version "$setup_mode"
  fi
  python3 -B source/scripts/admit_codex_bundle.py \
    --archive "$setup_dir/$asset" --stage "$setup_dir/admitted" \
    --source-sha "$commit" --source-ref refs/heads/main \
    --signer-workflow .github/workflows/validate.yml \
    --archive-sha256 "${archive_digest#sha256:}" --manifest-sha256 "$manifest_digest" \
    --repository-version "$edition" --suite-version "$suite" "$@" \
    > admission.json
  admitted_kit="$(python3 -c 'import json; print(json.load(open("admission.json"))["kit"])')"
  python3 -B source/kit/portable/update_skill_suite.py audit \
    --kit "$admitted_kit" --plan "$setup_dir/review-pending-core.json" \
    --backup-root "$setup_dir/core-recovery"
  python3 - admission.json review-pending-core.json "$setup_mode" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    receipt = json.load(f)
with open(sys.argv[2], encoding="utf-8") as f:
    plan = json.load(f)
if (receipt["status"] != "admitted-for-updater-audit" or not plan["ready"]
        or receipt["kit"] != plan["kit"]
        or receipt["manifest_sha256"] != plan["manifest_sha256"]):
    raise SystemExit("The plan does not match the admission receipt or is blocked.")
if sys.argv[3] == "fresh" and (receipt.get("installation_mode") != "fresh" or plan["discovered"]):
    raise SystemExit("First installation is blocked. Check the admission mode and any discovered managed skills.")
PY
  mv review-pending-core.json core-plan.json
)
```

Use the official package source pins in this procedure. Select explicit `--destination`, `--legacy-root`, or `--project-root` during audit only when your Codex configuration requires them. Use the same target roots in verification. Ask Codex to inspect a plan in your language if you want a guided installation.

### Review and apply

Read the audit output before running this block. Check that the plan lists the expected 33 skill names, the correct destination, and any icon-preservation decisions. Resolve a pending conflict before proceeding. Keep the original plan and the reported journal.

```bash
(
  set -eu
  cd "$setup_dir"
  admitted_kit="$(python3 -c 'import json; print(json.load(open("admission.json"))["kit"])')"
  python3 -B source/kit/portable/update_skill_suite.py apply \
    --plan "$setup_dir/core-plan.json" > core-apply.json
  journal="$(python3 -c 'import json; print(json.load(open("core-apply.json"))["journal"])')"
  python3 -B source/kit/portable/update_skill_suite.py verify \
    --kit "$admitted_kit" --journal "$journal"
  printf 'Core journal: %s\n' "$journal"
)
```

If apply is interrupted before it prints `core-apply.json`, open the
`core-recovery` directory chosen during audit and find the journal that
belongs to the saved `core-plan.json`. Match the journal's embedded plan to
the saved plan, including the destination and kit. The updater checks this
binding again. For a matching interrupted operation, use
`apply --plan "$setup_dir/core-plan.json" --resume "$journal"` and then run
verification. If the operation cannot be identified from the journal and
the actual destination, reconcile the installed files before another apply.

### Profile and roles

The managed profile preserves instructions outside its marked block. The role files install separately. If the installed role instructions and identity match the approved source, the audit preserves valid local model and reasoning selections, including inherited settings. Other unknown changes require reconciliation. Run the audit first and review its output. If the target differs from your plan, stop and inspect the affected paths.

```bash
(
  set -eu
  cd "$setup_dir"
  admitted_kit="$(python3 -c 'import json; print(json.load(open("admission.json"))["kit"])')"
  python3 -B source/scripts/install_host_profile.py audit \
    --repo "$(dirname "$admitted_kit")" --plan "$setup_dir/host-plan.json"
)
```

```bash
(
  set -eu
  cd "$setup_dir"
  python3 -B source/scripts/install_host_profile.py apply \
    --plan "$setup_dir/host-plan.json" --journal "$setup_dir/host-journal.json"
  python3 -B source/scripts/install_host_profile.py verify --journal "$setup_dir/host-journal.json"
)
```

### Optional components

- Orchestrator and maintenance can be installed individually from their directories in the admitted bundle. In Agent Atelier, open the skill catalog, select **Review this skill update**, inspect the exact files and target, then apply and verify. The same interface handles a fresh optional installation. Follow it with a fresh Codex session.
- For Codex without the panel, install each complete optional source in the personal skills location your host discovers using its supported skill management. Point the manager at `optional-skills/atelier-orchestrator` or `maintenance-skill` in the admitted bundle. For a manual first installation, copy the entire folder to a new personal skill directory only after checking the canonical and alternate locations for duplicate names. Confirm that the directory contains `SKILL.md`, `agents/openai.yaml`, and the required relative resources. Use the existing manager’s plan and journal for an installed source.
- For the ready Windows/macOS/Linux workbench, use the platform `Start-Workbench` file and [runtime guide](commercial/WORKBENCH_RUNTIME.md). The [source build and launch guide](../apps/agent-atelier/README.md#build-and-launch) remains available. For ChatGPT Work, use the host’s supported personal-skill interface and the [package guide](../governance/PACKAGES.md). Check what the native host actually saved and loaded.

## Verify

The core file check reports the installed source inventory, compatibility with the approved kit, and preservation confirmed by the exact journal. In a fresh Codex session in the product folder, check the resolved source path for a core skill and any optional skill you installed. Then run the [first small task](../START_HERE.md#install-and-verify). With role support, give one bounded subagent named inputs, permissions, and a result to return. The [native suite](../evaluations/README.md) provides a repeatable example.

## Rollback

Use the saved journal. Resolve any in-flight native task or uncertain effect first. After a restore, verify the result and open a fresh Codex session to check discovery.

```bash
(
  set -eu
  cd "$setup_dir"
  journal="$(python3 -c 'import json; print(json.load(open("core-apply.json"))["journal"])')"
  python3 -B source/kit/portable/update_skill_suite.py rollback --journal "$journal"
)
```

For the profile and roles, use `python3 -B source/scripts/install_host_profile.py rollback --journal "$setup_dir/host-journal.json"` from the setup directory. Roll back an optional skill from its own journal in Agent Atelier. Workbench recovery uses its data backup and exact runtime rollback procedure.

## Existing projects

Open the original project and recover its identity, checkpoint, accepted decisions, requirements, and permissions before continuing. If the environment reports unknown local skill edits, inspect and preserve the differences. Adopt a new generated agent in its explicit product scope, then check discovery, continuity, and a bounded original task in the actual host. [Engineering guide](OPERATING_MODEL.md#project-context-and-handoffs)
