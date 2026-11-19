#!/usr/bin/env python3
"""Run a small, reviewed synthetic canary against exact project-scoped skills."""

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from uuid import UUID


REPO = Path(__file__).resolve().parents[1]
SCHEMA = "atelier.native-canary-suite/1"
RESULT = "atelier.native-canary-receipts/1"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FIXTURES = Path(__file__).parent / "native-canary-fixtures.json"
MODEL_ID = re.compile(r"gpt-[0-9]+(?:\.[0-9]+)?-sol\Z")
REASONING_EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
NATIVE_ENV_KEYS = {
    "HOME", "CODEX_HOME", "USER", "LOGNAME", "PATH", "LANG", "LC_ALL",
    "TMPDIR", "TEMP", "TMP", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA",
}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def managed_policy(requested_model=None, requested_effort=None, *, baseline=False):
    try:
        release = load_json(REPO / "releases/current.json")
        policy = release.get("managed_model")
        if not isinstance(policy, dict) or set(policy) != {"id", "reasoning_effort"}:
            raise ValueError
        model, effort = policy["id"], policy["reasoning_effort"]
        if (release.get("schema_version") != "codex-agents.release/1"
                or not isinstance(model, str) or not MODEL_ID.fullmatch(model)
                or effort != "ultra"):
            raise ValueError
    except (OSError, ValueError, AttributeError) as exc:
        raise ValueError("The verified release's managed model policy is missing or invalid") from exc
    if requested_model is not None and requested_model != model:
        if not baseline or not MODEL_ID.fullmatch(requested_model):
            raise ValueError(f"This managed route requires {model}; model overrides are for explicit baseline replays")
        model = requested_model
    if requested_effort is not None and requested_effort != effort:
        if not baseline or requested_effort not in REASONING_EFFORTS:
            raise ValueError(f"This managed route requires {effort} effort; effort overrides are for explicit baseline replays")
        effort = requested_effort
    return model, effort


def native_environment():
    return {name: value for name, value in os.environ.items()
            if name.upper() in NATIVE_ENV_KEYS}


def rollout_path(thread):
    try:
        thread = str(UUID(thread))
    except (TypeError, ValueError, AttributeError):
        return None
    state = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    today = datetime.now().astimezone()
    days = [state / (today + timedelta(days=offset)).strftime("%Y/%m/%d") for offset in (-1, 0, 1)]
    matches = [path for day in days if not day.is_symlink()
               for path in day.glob(f"rollout-*-{thread}.jsonl")
               if path.is_file() and not path.is_symlink()]
    return matches[0] if len(matches) == 1 else None


def native_turn_receipts(thread):
    """Lift only typed model metadata from the exact fixture chat."""
    path = rollout_path(thread)
    if path is None:
        return []
    contexts = []
    with path.open("rb") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.endswith(b"\n"):
                continue  # An interrupted process can leave the last row incomplete.
            event = json.loads(line)
            payload = event.get("payload", {})
            if line_number == 1 and (event.get("type") != "session_meta" or payload.get("id") != thread):
                return []
            if event.get("type") == "turn_context":
                model, effort = payload.get("model"), payload.get("effort")
                if not isinstance(model, str) or not isinstance(effort, str):
                    return []
                contexts.append({
                    "observed_model": model,
                    "observed_effort": effort,
                    "event_line": line_number,
                    "event_sha256": sha(line),
                    "thread_reference_sha256": sha(thread.encode()),
                })
    return contexts


def native_turn_receipt(thread):
    contexts = native_turn_receipts(thread)
    return contexts[0] if len(contexts) == 1 else None


def matches_model(receipt, model, effort):
    return bool(receipt and receipt["observed_model"] == model
                and receipt["observed_effort"] == effort)


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Expected a project-relative path")
    target = root
    for part in Path(relative).parts:
        if part in ("..", "."):
            raise ValueError(f"Invalid relative path: {relative}")
        target = target / part
        if target.is_symlink():
            raise ValueError(f"Symlink is out of fixture scope: {relative}")
    if not target.is_relative_to(root) or target == root:
        raise ValueError(f"Path escapes fixture: {relative}")
    return target


def inspect_files(root):
    records = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            raise ValueError(f"Unsupported fixture file: {name}")
        if path.is_file():
            records[name] = [sha(path.read_bytes()), stat.S_IMODE(path.stat().st_mode)]
    return records


def skill_source(name, root=REPO):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("Invalid skill name")
    optional = root / "optional-skills" / name
    core = root / "kit/skills" / name
    source = optional if optional.is_dir() else core
    if name == "codex-agents-maintenance":
        source = root / "maintenance-skill"
    if not (source / "SKILL.md").is_file() or source.is_symlink():
        raise ValueError(f"No candidate source for {name}")
    return source


def ambient_skill_roots():
    return (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
            Path("/etc/codex/skills"), Path("/etc/agents/skills"))


def installed_conflicts(name):
    conflicts = set()
    for root in ambient_skill_roots():
        same_name = root / name / "SKILL.md"
        if same_name.is_file():
            conflicts.update((str(same_name), str(same_name.resolve())))
    return sorted(conflicts)


def pin_skill(project, name, source):
    before = inspect_files(source)
    staged = safe_path(project, f".agents/skills/{name}")
    if staged.exists():
        raise ValueError(f"Duplicate project skill: {name}")
    shutil.copytree(source, staged)
    if before != inspect_files(staged):
        raise ValueError(f"Copied skill changed: {name}")
    return staged, before


def checked_suite():
    suite = load_json(FIXTURES)
    if suite.get("schema") != SCHEMA or not suite.get("cases"):
        raise ValueError("Invalid canary suite")
    for case_id, case in suite["cases"].items():
        if not NAME.fullmatch(case_id) or not case["prompt"].strip():
            raise ValueError(f"Invalid canary: {case_id}")
        if case["sandbox"] not in ("read-only", "workspace-write"):
            raise ValueError(f"Invalid sandbox: {case_id}")
        if type(case["persist"]) is not bool:
            raise ValueError(f"Invalid persist option: {case_id}")
        if case.get("role") and (
            not case["persist"] or not NAME.fullmatch(case["role"]["name"])
        ):
            raise ValueError(f"Role requires a named, persisted run: {case_id}")
    return suite


def auth_ok(codex):
    result = subprocess.run([codex, "login", "status"], capture_output=True,
                            text=True, timeout=15, check=False, env=native_environment())
    return result.returncode == 0 and "logged in using chatgpt" in (
        result.stdout + result.stderr
    ).lower()


def rows(path):
    output = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            output.append(json.loads(line))
    return output


def observed_commands(events):
    return [
        event["item"]
        for event in events
        if event.get("type") == "item.completed"
        and event.get("item", {}).get("type") == "command_execution"
    ]


def project_skill_read(items, project, name):
    relative = f".agents/skills/{name}/SKILL.md"
    skill_path = project / relative
    if not skill_path.is_file() or skill_path.is_symlink():
        return "unverified"
    skill = skill_path.read_text(encoding="utf-8")
    plain = re.compile(r"(?<![/\w.$-])(?:\./)?" + re.escape(relative) + r"(?![\w.-])")
    for item in items:
        command = item.get("command", "")
        if str(project / relative) not in command and not plain.search(command):
            continue
        if not re.search(r"\b(cat|sed|head|less|rg|read_text|read_bytes)\b", command):
            continue
        if skill in item.get("aggregated_output", ""):
            # Later commands in a chain may fail after the successful file read.
            return "exact-output"
        if item.get("status") == "completed" and item.get("exit_code") == 0:
            return "observed-project-path"
    return "unverified"


def role_trace(events):
    calls = [
        event["item"]
        for event in events
        if event.get("type") == "item.completed"
        and event.get("item", {}).get("type") == "collab_tool_call"
        and event["item"].get("status") == "completed"
    ]
    starts = [item for item in calls if item.get("tool") == "spawn_agent"]
    waits = [item for item in calls if item.get("tool") == "wait"]
    return starts, waits


def owned_role_provenance(thread, expected_role, profile, model=None, effort=None):
    parent = rollout_path(thread)
    evidence = {"observed": False, "spawn_count": 0, "exact_child_instructions": False,
                "child_completed": False, "model": None, "rollout_sha256": None,
                "child_rollout_sha256": None, "profile_sha256": sha(profile.encode())}
    if parent is None:
        return evidence

    calls, linked, activities, rejected = {}, set(), [], set()
    for event in rows(parent):
        payload = event.get("payload", {})
        if event.get("type") == "turn_context":
            evidence["model"] = payload.get("model") or evidence["model"]
        call_id = payload.get("call_id")
        if payload.get("type") == "function_call" and payload.get("name") == "spawn_agent":
            args = json.loads(payload.get("arguments", "{}"))
            calls[call_id] = args.get("agent_type") if isinstance(args, dict) else None
        if event.get("type") == "event_msg" and payload.get("type") == "item_completed":
            activity = payload.get("item", {})
            if activity.get("type") == "SubAgentActivity" and activity.get("kind") == "started":
                activities.append(activity)
        if payload.get("type") != "function_call_output" or call_id not in calls:
            continue
        output = payload.get("output")
        text = [output] if isinstance(output, str) else [
            part.get("text", "") for part in output or [] if isinstance(part, dict)
        ]
        if isinstance(output, str) and output.startswith("failed to parse function arguments:"):
            rejected.add(call_id)
        for block in text:
            try:
                reply = json.loads(block)
                if isinstance(reply, dict) and "agent_id" in reply:
                    linked.add((call_id, str(UUID(reply["agent_id"]))))
            except (TypeError, ValueError, AttributeError):
                continue
    for activity in activities:
        call_id = activity.get("id")
        if call_id not in calls:
            continue
        try:
            linked.add((call_id, str(UUID(activity["agent_thread_id"]))))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    observed_calls = {call_id for call_id, _ in linked}
    evidence["spawn_count"] = len(linked)
    evidence["requested_spawn_attempts"] = len(calls)
    evidence["invalid_arguments_rejected_without_effect"] = len(rejected - observed_calls)
    evidence["rollout_sha256"] = sha(parent.read_bytes())
    if (len(linked) != 1 or set(calls) != observed_calls | rejected
            or rejected & observed_calls):
        return evidence
    call_id, child_id = next(iter(linked))
    if calls[call_id] != expected_role:
        return evidence

    instructions = re.search(r'(?ms)^developer_instructions = """\n(.*?)\n"""$', profile)
    if not instructions or not instructions.group(1):
        return evidence
    child = rollout_path(child_id)
    if child is None:
        return evidence
    events = rows(child)
    meta = events[0] if events else {}
    metadata = meta.get("payload", {})
    link = metadata.get("source", {})
    spawn = link.get("subagent", {}).get("thread_spawn", {}) if isinstance(link, dict) else {}
    if (meta.get("type") != "session_meta" or metadata.get("id") != child_id
            or spawn.get("parent_thread_id") != thread
            or spawn.get("agent_role", expected_role) != expected_role):
        return evidence

    for event in events:
        payload = event.get("payload", {})
        if event.get("type") == "event_msg" and payload.get("type") in ("task_complete", "turn_completed"):
            evidence["child_completed"] = True
        if payload.get("type") == "message" and payload.get("role") == "developer":
            evidence["exact_child_instructions"] |= any(
                instructions.group(1) in (part.get("text") or "")
                for part in payload.get("content", []) if isinstance(part, dict)
            )
    evidence["child_thread_id"] = child_id
    child_receipts = native_turn_receipts(child_id)
    evidence["child_model_receipt"] = child_receipts[-1] if child_receipts else None
    evidence["child_model_receipts"] = child_receipts
    evidence["child_rollout_sha256"] = sha(child.read_bytes())
    model_verified = child_receipts and all(matches_model(row, model, effort) for row in child_receipts)
    evidence["observed"] = (evidence["child_completed"] and evidence["exact_child_instructions"]
                            and (model is None or bool(model_verified)))
    return evidence


def observed_consumer_json(finished, skill, expected):
    script = f".agents/skills/{skill}/scripts/"
    expected_json = json.dumps(expected, sort_keys=True)
    for item in finished:
        command = item.get("command", "")
        if script not in command or "heldout.csv" not in command or item.get("exit_code") != 0:
            continue
        for line in item.get("aggregated_output", "").splitlines():
            try:
                if json.dumps(json.loads(line), sort_keys=True) == expected_json:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def check_artifact(project, check):
    first = safe_path(project, check["path"])
    if not first.is_file():
        return False
    if "text" in check:
        return first.read_text(encoding="utf-8") == check["text"]
    if "json" in check:
        return load_json(first) == check["json"]
    if "contains" in check:
        return check["contains"] in first.read_text(encoding="utf-8")
    raise ValueError("Unknown artifact check")


def apply_approved_kit(project, kit, expected_sha, expected_entry):
    manifest_path = safe_path(kit, "manifest.json")
    if sha(manifest_path.read_bytes()) != expected_sha:
        raise ValueError("Approved manifest digest differs from supplied package")
    manifest = load_json(manifest_path)
    names = [row["name"] for row in manifest.get("skills", [])]
    if manifest.get("entry_skill") != expected_entry or names != [expected_entry]:
        raise ValueError("Canary approves exactly its generated entry skill")
    installer = skill_source("agent-foundry") / "scripts/install_agent.py"
    receipts = {}
    for mode in ("preflight", "apply", "verify"):
        result = subprocess.run(
            ["python3", "-B", str(installer), "--kit", str(kit), "--project",
             str(project), "--mode", mode],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode or not json.loads(result.stdout).get("ok"):
            raise ValueError(f"Generated kit {mode} failed in the disposable fixture")
        receipts[mode] = sha(result.stdout.encode())
    return {"manifest_sha256": expected_sha, "command_receipt_sha256": receipts}


def run_native(argv, prompt, out, err, deadline):
    with subprocess.Popen(
        argv, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True,
        env=native_environment()
    ) as child:
        try:
            child.communicate(prompt, timeout=deadline)
            return child.returncode
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=5)
                except ProcessLookupError:
                    pass
            if isinstance(exc, KeyboardInterrupt):
                raise
            return None


def execute(case_id, case, args, raw_root):
    case_root = raw_root / case_id
    case_root.mkdir(mode=0o700)
    project = case_root / "project"
    project.mkdir(mode=0o700)
    subprocess.run(
        ["git", "init", "--quiet", "--template=", str(project)],
        capture_output=True, check=True, timeout=15,
    )
    for name, content in case["files"].items():
        if name.startswith((".agents/", ".codex/", ".git/")):
            raise ValueError("Runtime configuration is supplied by the reviewed harness")
        path = safe_path(project, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    staged = {name: pin_skill(project, name, skill_source(name, getattr(args, "source", REPO))) for name in case["skills"]}
    consumer = case.get("approved_kit_consumer")
    install_proof = None
    if consumer:
        if args.approved_kit is None:
            raise ValueError(f"{case_id} requires --approved-kit and --approved-manifest-sha256")
        install_proof = apply_approved_kit(
            project, args.approved_kit, args.approved_manifest_sha256, consumer
        )
        installed = safe_path(project, f".agents/skills/{consumer}")
        staged[consumer] = (installed, inspect_files(installed))
    role_config = []
    if "role" in case:
        role = case["role"]
        if not NAME.fullmatch(role["name"]):
            raise ValueError("Invalid fixture role name")
        target = safe_path(project, f'.codex/agents/{role["name"]}.toml')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(role["profile"], encoding="utf-8")
        role_config = ["-c", f'agents.{role["name"]}.config_file=' + json.dumps(str(target))]
    before = inspect_files(project)
    if args.prepare_only:
        return {"case": case_id, "status": "prepared", "input_sha256": sha(json.dumps(before, sort_keys=True).encode())}

    duplicate_paths = sorted({path for name in staged for path in installed_conflicts(name)})
    configured = ",".join(
        "{path=" + json.dumps(path, ensure_ascii=False) + ",enabled=false}"
        for path in duplicate_paths
    )
    # The model may only use the staged skill source. Disabled discovery alone
    # does not prevent a shell command from reading another installed copy.
    sandbox_name = ":workspace" if case["sandbox"] == "workspace-write" else ":read-only"
    rules = {":slash_tmp": "read", ":tmpdir": "read"}
    rules.update({str(path.resolve()): "none" for path in ambient_skill_roots() if path.is_dir()})
    filesystem = ",".join(json.dumps(path) + "=" + json.dumps(mode)
                          for path, mode in sorted(rules.items()))
    sandbox = ["-c", 'default_permissions="atelier-canary"', "-c",
               'permissions={atelier-canary={extends=' + json.dumps(sandbox_name)
               + ',filesystem={' + filesystem + '},network={enabled=false}}}']
    command = [args.codex, "-a", "never", "exec", "--ignore-user-config",
                "--strict-config", "--json", *sandbox,
               "-c", "skills.config=[" + configured + "]",
               "-c", 'web_search="disabled"', "--disable", "apps", "--disable", "plugins",
               "--disable", "hooks", "--disable", "memories",
               "-c", f'model_reasoning_effort="{args.effort}"',
               *role_config, "-C", str(project), "--model", args.model]
    persisted = case["persist"] or getattr(args, "persist_model_receipt", False)
    if not persisted:
        command.append("--ephemeral")
    started = time.monotonic()
    native = case_root / "events.jsonl"
    with native.open("wb") as out, (case_root / "diagnostics.log").open("wb") as err:
        exit_code = run_native(
            [*command, "-"], case["prompt"].encode(), out, err, args.deadline
        )

    wall_ms = round((time.monotonic() - started) * 1000)
    events = rows(native)
    turns = [e for e in events if e.get("type") == "turn.completed"]
    threads = [str(UUID(e["thread_id"])) for e in events if e.get("type") == "thread.started"]
    finished = observed_commands(events)
    commands = [item["command"] for item in finished]
    starts, waits = role_trace(events)
    after = inspect_files(project)
    sources = {
        name: {
            "sha256": sha(json.dumps(pins, sort_keys=True).encode()),
            "intact": pins == inspect_files(path),
            "project_skill_read": project_skill_read(finished, project, name),
        }
        for name, (path, pins) in staged.items()
    }
    checks = [check_artifact(project, check) for check in case["checks"]]
    if consumer:
        checks.append(observed_consumer_json(finished, consumer, case["check_native_stdout_json"]))
    referenced_duplicate = any(path in command for command in commands for path in duplicate_paths)
    allowed = set(case["allowed_changes"])
    changes = {path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}
    unexpected = sorted(path for path in changes if not any(
        path == item or (item.endswith("/") and path.startswith(item)) for item in allowed
    ))
    expected_spawns = int("role" in case)
    model_receipt = native_turn_receipt(threads[0]) if persisted and len(threads) == 1 else None
    provenance = (
        owned_role_provenance(threads[0], case["role"]["name"], case["role"]["profile"], args.model, args.effort)
        if expected_spawns and len(threads) == 1 else None
    )
    spawn_count = provenance["spawn_count"] if provenance is not None else len(starts)
    if exit_code != 0 or len(turns) != 1 or len(threads) != 1:
        status = "blocked-runtime"
    elif persisted and not matches_model(model_receipt, args.model, args.effort):
        status = "unverified-effective-model"
    elif (spawn_count != expected_spawns or len(waits) != expected_spawns or
          unexpected or not all(checks) or not all(s["intact"] for s in sources.values())):
        status = "failed-controlled"
    elif referenced_duplicate or any(
        s["project_skill_read"] == "unverified" for s in sources.values()
    ):
        status = "unverified-source-selection"
    elif not persisted:
        status = "unverified-effective-model"
    elif case.get("requires_passport_review"):
        status = "awaiting-exact-passport-review"
    elif provenance is not None and not provenance["observed"]:
        status = "unverified-role-provenance"
    else:
        status = "passed-controlled"
    return {
        "case": case_id,
        "status": status,
        "exit_code": exit_code,
        "turn_count": len(turns),
        "persisted": persisted,
        "model_receipt": model_receipt,
        "elapsed_ms": wall_ms,
        "thread_reference_sha256": sha(threads[0].encode()) if len(threads) == 1 else None,
        "observed_spawns": spawn_count,
        "observed_waits": len(waits),
        "disabled_duplicate_paths": len(duplicate_paths),
        "referenced_installed_duplicate": referenced_duplicate,
        "role_provenance": provenance,
        "fixture_kit_verification": install_proof,
        "checks": checks,
        "unexpected_changes": unexpected,
        "sources": sources,
        "prompt_sha256": sha(case["prompt"].encode()),
        "inputs_sha256": sha(json.dumps(before, sort_keys=True).encode()),
        "events_sha256": sha(native.read_bytes()),
        "usage": turns[0].get("usage") if len(turns) == 1 else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", required=True, help="Select one or more synthetic case IDs")
    parser.add_argument("--output", required=True, type=Path, help="New private JSONL receipt")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--model", help="Explicit comparison pin; a different model requires baseline mode")
    parser.add_argument("--effort", choices=REASONING_EFFORTS, help="Alternate effort requires an explicit historical baseline")
    parser.add_argument("--stage", choices=("baseline", "candidate"), default="candidate")
    parser.add_argument("--baseline-source", type=Path, help="Reviewed clean reference checkout for baseline only")
    parser.add_argument("--deadline", type=int, default=150, help="Seconds per native case (30–600)")
    parser.add_argument("--approved-kit", type=Path, help="Exact already reviewed package directory for the constructor consumer")
    parser.add_argument("--approved-manifest-sha256", help="SHA-256 authorized for this synthetic project installation")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare and inspect fixtures without calling the model")
    parser.add_argument("--persist-model-receipt", action="store_true",
                        help="Allow one disposable native rollout per fixture for exact model readback")
    args = parser.parse_args()
    if args.baseline_source is not None and args.stage != "baseline":
        parser.error("A baseline source requires --stage baseline")
    args.source = args.baseline_source.resolve() if args.baseline_source else REPO
    try:
        args.model, args.effort = managed_policy(args.model, args.effort, baseline=args.stage == "baseline")
    except ValueError as exc:
        parser.error(str(exc))
    suite = checked_suite()
    if len(set(args.case)) != len(args.case) or any(case not in suite["cases"] for case in args.case):
        parser.error("Select unique IDs from the bundled suite")
    if not 30 <= args.deadline <= 600:
        parser.error("Deadline must be between 30 and 600 seconds")
    if bool(args.approved_kit) != bool(args.approved_manifest_sha256):
        parser.error("Provide the approved kit and its exact authorized manifest digest together")
    if args.approved_kit and (not args.approved_kit.is_dir() or not re.fullmatch(
        r"[0-9a-f]{64}", args.approved_manifest_sha256
    )):
        parser.error("Expected a real kit directory and lowercase SHA-256")
    if args.approved_kit:
        args.approved_kit = args.approved_kit.resolve()
    if args.output.resolve().is_relative_to(REPO):
        parser.error("Select a new private receipt outside the checkout")
    if not args.prepare_only and not auth_ok(args.codex):
        parser.error("Native canary requires an existing authenticated ChatGPT session")

    raw_root = Path(tempfile.mkdtemp(prefix="atelier-native-canary-")).resolve()
    header = {"schema": RESULT, "stage": args.stage, "native": not args.prepare_only,
              "git_base_commit": subprocess.check_output(
                    ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip(),
              "checkout_modified": bool(subprocess.check_output(
                    ["git", "-C", str(args.source), "status", "--porcelain"], text=True)),
              "cli_version": None if args.prepare_only else subprocess.check_output(
                    [args.codex, "--version"], text=True, stderr=subprocess.DEVNULL,
                    timeout=15).strip(),
              "requested_model": args.model,
              "requested_effort": args.effort,
              "suite_sha256": sha(FIXTURES.read_bytes()),
              "runner_sha256": sha(Path(__file__).read_bytes())}
    old_umask = os.umask(0o077)
    failures = False
    try:
        with args.output.open("x", encoding="utf-8") as report:
            report.write(json.dumps(header) + "\n")
            for case in args.case:
                try:
                    result = execute(case, suite["cases"][case], args, raw_root)
                except (OSError, ValueError, subprocess.SubprocessError) as exc:
                    result = {"case": case, "status": "blocked-preflight", "error": type(exc).__name__}
                failures |= result["status"].startswith(("failed-", "blocked-", "unverified-"))
                report.write(json.dumps(result, ensure_ascii=False) + "\n")
                report.flush()
                print(case, result["status"], flush=True)
    finally:
        os.umask(old_umask)
    print(f"Private evidence directory: {raw_root}")
    return int(failures)


if __name__ == "__main__":
    raise SystemExit(main())
