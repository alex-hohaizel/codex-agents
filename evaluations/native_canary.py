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
from uuid import UUID


REPO = Path(__file__).resolve().parents[1]
SCHEMA = "atelier.native-canary-suite/1"
RESULT = "atelier.native-canary-receipts/1"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FIXTURES = Path(__file__).parent / "native-canary-fixtures.json"


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


def skill_source(name):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("Invalid skill name")
    optional = REPO / "optional-skills" / name
    core = REPO / "kit/skills" / name
    source = optional if optional.is_dir() else core
    if name == "codex-agents-maintenance":
        source = REPO / "maintenance-skill"
    if not (source / "SKILL.md").is_file() or source.is_symlink():
        raise ValueError(f"No candidate source for {name}")
    return source


def installed_conflicts(name):
    roots = (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
             Path("/etc/codex/skills"), Path("/etc/agents/skills"))
    conflicts = set()
    for root in roots:
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
                            text=True, timeout=15, check=False)
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


def owned_role_provenance(thread, expected_role, profile):
    # Read messages only from this fixture parent and its uniquely linked child.
    # For other rollouts, examine only the metadata line to establish linkage.
    state_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    now = datetime.now().astimezone()
    days = [
        state_root / (now + timedelta(days=offset)).strftime("%Y/%m/%d")
        for offset in (-1, 0, 1)
    ]
    parents = [p for day in days for p in day.glob(f"rollout-*-{thread}.jsonl")
               if p.is_file() and not p.is_symlink()]
    evidence = {"observed": False, "spawn_count": 0, "exact_child_instructions": False,
                "child_completed": False, "model": None, "rollout_sha256": None,
                "child_rollout_sha256": None, "profile_sha256": sha(profile.encode())}
    if len(parents) != 1:
        return evidence

    observed = []
    for event in rows(parents[0]):
        payload = event.get("payload", {})
        if event.get("type") == "turn_context":
            evidence["model"] = payload.get("model") or evidence["model"]
        if payload.get("type") == "function_call" and payload.get("name") == "spawn_agent":
            observed.append(json.loads(payload.get("arguments", "{}")).get("agent_type"))
    evidence["spawn_count"] = len(observed)
    evidence["rollout_sha256"] = sha(parents[0].read_bytes())
    if observed != [expected_role]:
        return evidence

    instructions = re.search(r'(?ms)^developer_instructions = """\n(.*?)\n"""$', profile)
    if not instructions or not instructions.group(1):
        return evidence
    children = []
    for day in days:
        for path in day.glob("rollout-*.jsonl"):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                with path.open(encoding="utf-8") as stream:
                    meta = json.loads(stream.readline())
                if meta.get("type") != "session_meta":
                    continue
                source = meta.get("payload", {}).get("source", {})
                spawn = source.get("subagent", {}).get("thread_spawn", {})
                if spawn.get("parent_thread_id") == thread:
                    children.append(path)
            except (OSError, ValueError, AttributeError):
                continue
    if len(children) != 1:
        return evidence

    for event in rows(children[0]):
        payload = event.get("payload", {})
        if event.get("type") == "event_msg" and payload.get("type") in ("task_complete", "turn_completed"):
            evidence["child_completed"] = True
        if payload.get("type") == "message" and payload.get("role") == "developer":
            evidence["exact_child_instructions"] |= any(
                instructions.group(1) in (part.get("text") or "")
                for part in payload.get("content", []) if isinstance(part, dict)
            )
    evidence["child_rollout_sha256"] = sha(children[0].read_bytes())
    evidence["observed"] = evidence["child_completed"] and evidence["exact_child_instructions"]
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
        argv, stdin=subprocess.PIPE, stdout=out, stderr=err, start_new_session=True
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
    staged = {name: pin_skill(project, name, skill_source(name)) for name in case["skills"]}
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
    if case["sandbox"] == "workspace-write":
        # The built-in workspace profile permits scratch writes by default.
        # Keep its protected paths while making general temp trees read-only;
        # workspace writes remain confined to the synthetic project.
        sandbox = ["-c", 'default_permissions="atelier-canary"', "-c",
                   'permissions={atelier-canary={extends=":workspace",'
                   'filesystem={":slash_tmp"="read",":tmpdir"="read"},'
                   'network={enabled=false}}}']
    else:
        sandbox = ["--sandbox", "read-only"]
    command = [args.codex, "-a", "never", "exec", "--ignore-user-config",
                "--strict-config", "--json", *sandbox,
               "-c", "skills.config=[" + configured + "]",
               "-c", 'web_search="disabled"', "--disable", "apps",
               *role_config, "-C", str(project)]
    if not case["persist"]:
        command.append("--ephemeral")
    if args.model:
        command.extend(["--model", args.model])
    native = case_root / "events.jsonl"
    with native.open("wb") as out, (case_root / "diagnostics.log").open("wb") as err:
        exit_code = run_native(
            [*command, "-"], case["prompt"].encode(), out, err, args.deadline
        )

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
    provenance = (
        owned_role_provenance(threads[0], case["role"]["name"], case["role"]["profile"])
        if expected_spawns and len(threads) == 1 else None
    )
    spawn_count = provenance["spawn_count"] if provenance is not None else len(starts)
    if exit_code != 0 or len(turns) != 1 or len(threads) != 1:
        status = "blocked-runtime"
    elif (spawn_count != expected_spawns or len(waits) != expected_spawns or
          unexpected or not all(checks) or not all(s["intact"] for s in sources.values())):
        status = "failed-controlled"
    elif referenced_duplicate or any(
        s["project_skill_read"] == "unverified" for s in sources.values()
    ):
        status = "unverified-source-selection"
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
        "persisted": case["persist"],
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
    parser.add_argument("--model", help="Pin a model available to the authenticated ChatGPT session")
    parser.add_argument("--stage", choices=("baseline", "candidate"), default="candidate")
    parser.add_argument("--deadline", type=int, default=150, help="Seconds per native case (30–600)")
    parser.add_argument("--approved-kit", type=Path, help="Exact already reviewed package directory for the constructor consumer")
    parser.add_argument("--approved-manifest-sha256", help="SHA-256 authorized for this synthetic project installation")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare and inspect fixtures without calling the model")
    args = parser.parse_args()
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
                    ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip(),
              "checkout_modified": bool(subprocess.check_output(
                    ["git", "-C", str(REPO), "status", "--porcelain"], text=True)),
              "cli_version": None if args.prepare_only else subprocess.check_output(
                    [args.codex, "--version"], text=True, stderr=subprocess.DEVNULL,
                    timeout=15).strip(),
              "requested_model": args.model,
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
