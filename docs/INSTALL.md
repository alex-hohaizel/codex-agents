# Install Codex Agent System

Start with the 33 core skills. Add the managed Codex profile and twelve role definitions when you need the provided roles. Atelier Orchestrator, the maintenance skill, and Agent Atelier for Mac have separate controls. [Current component versions](../releases/current.json)

## Before

- Open a Codex session with access to the intended local skill directories. On macOS or Linux, the commands below use Bash, Python 3.9+, Git, and an authenticated GitHub CLI (`gh`). The workbench runs locally on Mac with Node.js installed.
- Use the official stable GitHub release and its `CODEX` asset. GitHub’s generic source archive is useful for source inspection and isolated rehearsals. The signed release archive is the input for managed installation. [Stable release](https://github.com/alex-hohaizel/codex-agents/releases/latest)
- Choose `fresh` for an empty managed core install. Use the verified installed core version for a recognized existing suite. The audit will stop on unknown local changes or ambiguous sources. Keep setup files and journals outside skill-discovery roots.

## Steps

### Stage the official archive

Set `setup_mode` to `fresh` or to the installed suite version you have verified. This block opens a private setup directory, resolves the exact official tag to a commit, checks out the trusted verifier there, and admits the ZIP using the published asset digest and that commit’s manifest. The attestation binds the ZIP to the repository, commit, source ref, and workflow.

```bash
setup_mode=fresh
setup_dir="$(mktemp -d)"
(
  set -eu
  cd "$setup_dir"
  repository=alex-hohaizel/codex-agents
  tag="$(gh release view --repo "$repository" --json tagName --jq .tagName)"
  commit="$(gh api "repos/$repository/commits/$tag" --jq .sha)"
  git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repository.git" source
  git -C source sparse-checkout set --no-cone \
    /scripts/ /kit/portable/ /kit/manifest.json /releases/current.json
  git -C source checkout --quiet --detach "$commit"
  manifest_digest="$(python3 -c 'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("source/kit/manifest.json").read_bytes()).hexdigest())')"
  suite="$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["suite_version"])')"
  edition="$(python3 -c 'import json; print(json.load(open("source/releases/current.json"))["repository_version"])')"
  asset="Agent_System_${suite}_CODEX.zip"
  archive_digest="$(gh api "repos/$repository/releases/tags/$tag" --jq ".assets[] | select(.name == \"$asset\") | .digest")"
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
    --kit "$admitted_kit" --plan "$setup_dir/review-pending-core.json"
  python3 - admission.json review-pending-core.json <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    receipt = json.load(f)
with open(sys.argv[2], encoding="utf-8") as f:
    plan = json.load(f)
if (receipt["status"] != "admitted-for-updater-audit" or not plan["ready"]
        or receipt["kit"] != plan["kit"]
        or receipt["manifest_sha256"] != plan["manifest_sha256"]):
    raise SystemExit("The plan does not match the admission receipt or is blocked.")
if receipt["installation_mode"] == "fresh" and plan["discovered"]:
    raise SystemExit("Managed skills already exist. Confirm the installed version and rerun setup as an update.")
PY
  mv review-pending-core.json core-plan.json
)
```

If a GitHub deployment uses a different attestation ref or workflow from the official repository, use that release’s independently verified signer and source pins. The commands above target this repository’s official release path. Select explicit `--destination`, `--legacy-root`, or `--project-root` during audit only when your Codex configuration requires them. Use the same target roots in verification. Ask Codex to inspect a plan in your language if you want a guided installation.

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

### Profile and roles

The managed profile preserves instructions outside its marked block. The role files install separately. Run the audit first and review its output. If the target differs from your plan, stop and inspect the affected paths.

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
- For the local Mac workbench, use the [Agent Atelier build and launch guide](../apps/agent-atelier/README.md#build-and-launch). For ChatGPT Work, use the host’s supported personal-skill interface and the [package guide](../governance/PACKAGES.md). Check what the native host actually saved and loaded.

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
