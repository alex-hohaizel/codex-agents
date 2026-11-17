#!/usr/bin/env python3
"""Exercise a reviewed replan and native handoff on a disposable FieldSlate WSGI app."""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import native_canary as native


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "replan_delivery"
REVIEW = "review"
REQUEST = f"{REVIEW}/request.json"
DECISION = f"{REVIEW}/decision.json"
HANDOFF = f"{REVIEW}/handoff.json"
BUILDER = f"{REVIEW}/builder.json"
PROJECTION = "tickets.json"
REQUIREMENTS = "requirements.json"
TICKET = "EXP-V2"
OPERATION = "fieldslate-delivery-v2"
SCOPE = {"src.py", BUILDER}
BASELINE = "R3.1"
TARGET = "R3.2"
SKILLS = ("app-atelier-build", "atelier-orchestrator")
TOOLS = (
    "scripts/ticket_tree.py",
    "scripts/ticket_refine.py",
    "scripts/ticket_replan_plan.py",
    "scripts/ticket_replan_store.py",
    "scripts/ticket_replan_correction.py",
    "scripts/ticket_handoff.py",
    "standards/context_capsule.py",
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write_json(root, relative, value):
    path = native.safe_path(root, relative)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def pin(root, relative):
    return {"path": relative, "sha256": native.sha(native.safe_path(root, relative).read_bytes())}


def run(argv, root, timeout=30, env=None):
    return subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          encoding="utf-8", timeout=timeout, env=env, check=False)


def command_json(argv, root):
    result = run(argv, root)
    need(result.returncode == 0, f"{Path(argv[0]).name} failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def git(root, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    result = run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                  "-c", "user.name=FieldSlate Fixture", "-c", "user.email=fixture@example.invalid",
                  *args], root, env=env)
    need(result.returncode == 0, f"Fixture git failed: {result.stderr.strip()}")
    return result.stdout.strip()


def python_tool(project, name, *args):
    path = f"candidate-tools/scripts/{name}"
    need(native.safe_path(project, path).is_file(), f"Missing fixture tool: {name}")
    return [sys.executable, "-B", path, *map(str, args)]


def inventory(project):
    result = {}
    for current, directories, files in os.walk(project):
        folder = Path(current)
        if folder == project and ".git" in directories:
            directories.remove(".git")
        for name in directories + files:
            path = folder / name
            need(not path.is_symlink(), f"Unexpected fixture symlink: {path}")
        for name in files:
            path = folder / name
            need(path.is_file(), f"Unexpected fixture file type: {path}")
            result[path.relative_to(project).as_posix()] = [
                native.sha(path.read_bytes()), stat.S_IMODE(path.stat().st_mode),
            ]
    return result


def changes_from(before, after):
    return sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))


def row(ident, title, kind="story", status="planned", parent="E-EXPORT",
        requirements=(), depends=(), criterion=None):
    item = {"id": ident, "title": title, "kind": kind, "status": status, "parent": parent,
            "requirement_ids": list(requirements), "depends_on": list(depends)}
    if criterion is not None:
        item["acceptance"] = criterion
    return item


def project_inputs(project, historical):
    criterion = "Both R3.1 routes return exactly five CSV columns, scope access to the caller's district, and record v1 audit metadata."
    write_json(project, "evidence/exp-12-result.json", historical)
    write_json(project, "evidence/exp-12.json", {
        "schema_version": "atelier.ticket-acceptance/1",
        "project_id": "fieldslate", "native_revision": BASELINE, "ticket_id": "EXP-12",
        "criterion_sha256": native.sha(criterion.encode()),
        "subject": pin(project, "evidence/exp-12-result.json"),
    })
    delivered = row("EXP-12", "Export v1", status="accepted", requirements=["R-CSV"], criterion=criterion)
    delivered["evidence"] = [pin(project, "evidence/exp-12.json")]
    write_json(project, PROJECTION, {
        "schema_version": "atelier.ticket-projection/1",
        "project_id": "fieldslate", "native_revision": BASELINE,
        "requirement_sources": [pin(project, REQUIREMENTS)],
        "tickets": [
            row("I-R3", "FieldSlate R3", kind="initiative", parent=None),
            row("E-EXPORT", "Roster export", kind="epic", parent="I-R3"),
            delivered,
            row("REL-19", "Plan release instructions and export verification",
                requirements=["R-UX", "R-ROLLOUT"],
                criterion="Prepare user-facing instructions and an operating checklist."),
            row("REL-25", "Review release follow-up", requirements=["R-ROLLOUT"],
                depends=["REL-19"], criterion="Check that both follow-up items are prepared."),
            row("REL-30", "Restore the legacy fallback if needed", requirements=["R-OFF"],
                criterion="If the current export is unavailable, restore the old export."),
            row("E-SCHED", "Scheduling", kind="epic", parent="I-R3"),
            row("UI-07", "Scheduling keyboard help", status="in-progress", parent="E-SCHED",
                requirements=["R-HELP"], criterion="Check keyboard tooltip copy."),
        ],
    })


def request(project, target):
    requirement_pin = pin(project, REQUIREMENTS)
    requirements = {r["id"]: r["text"] for r in native.load_json(project / REQUIREMENTS)["requirements"]}

    def cite(*identifiers):
        return [{**requirement_pin, "requirement_id": ident, "excerpt": requirements[ident]}
                for ident in identifiers]

    return {
        "schema_version": "atelier.ticket-replan-request/1",
        "project_id": "fieldslate", "native_revision": BASELINE, "target_revision": target,
        "projection_sha256": pin(project, PROJECTION)["sha256"],
        "changes": [
            {"action": "create",
             "rationale": "Implement the new shared roster contract while retaining EXP-12 as history.",
             "sources": cite("R-CSV", "R-AUDIT", "R-OFF"),
             "ticket": row(TICKET, "Implement the v2 roster download in both entry points",
                           requirements=["R-CSV", "R-AUDIT", "R-OFF"],
                           criterion="Both routes preserve district isolation and return the four UTF-8 CSV columns. "
                           "Successful audit uses exact metadata and v2. Unavailable export returns 503 without "
                           "data or success audit, and an unauthorized caller is still denied.")},
            {"action": "split", "ticket_id": "REL-19",
             "rationale": "Let product and operations finish independently after the implementation.",
             "sources": cite("R-UX", "R-ROLLOUT"),
             "tickets": [
                 row("REL-DOC", "Write the user-facing export notes", requirements=["R-UX"], depends=[TICKET],
                     criterion="Document the four current columns and describe district selection."),
                 row("REL-OPS", "Prepare the export enablement checklist", requirements=["R-ROLLOUT"],
                     depends=[TICKET], criterion="Document how to verify the disabled state and audit."),
             ]},
            {"action": "drop", "ticket_id": "REL-30",
             "rationale": "The current requirements forbid restoring the old download.",
             "sources": cite("R-OFF")},
        ],
    }


def copy_review_tool(project, filename):
    path = project / REVIEW / filename
    need(not path.exists(), f"Review tool already exists: {filename}")
    shutil.copy2(FIXTURE / filename, path)


def prepare(case):
    need(not case.exists(), "Use a new case directory")
    project = case / "project"
    (project / REVIEW).mkdir(parents=True, mode=0o700)
    (project / "evidence").mkdir()
    for filename in ("src.py", REQUIREMENTS, "change-request.md"):
        shutil.copy2(FIXTURE / filename, project / filename)
    copy_review_tool(project, "oracle.py")
    oracle = [sys.executable, "-B", f"{REVIEW}/oracle.py"]
    historical = command_json([*oracle, "historical"], project)
    bad_current = run([*oracle, "current"], project)
    need(bad_current.returncode != 0 and "exact header" in bad_current.stderr,
         "Current requirements unexpectedly pass on the historical source")
    (project / REVIEW / "oracle.py").unlink()
    project_inputs(project, historical)
    write_json(project, REQUEST, request(project, TARGET))
    write_json(project, f"{REVIEW}/competing.json", request(project, "R3.2-competing"))
    for ref in TOOLS:
        path = project / "candidate-tools" / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(native.REPO / ref, path)
    for name in SKILLS:
        native.pin_skill(project, name, native.skill_source(name))
    profile = project / ".codex/agents/foundry-qa.toml"
    profile.parent.mkdir(parents=True)
    shutil.copy2(native.REPO / "agent-profiles/foundry-qa.toml", profile)
    (project / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    git(project, "init", "--quiet", "--template=")
    git(project, "add", "--all")
    git(project, "commit", "--quiet", "-m", "Prepare FieldSlate fixture and proposed project revisions")
    write_json(case, "fixture.json", {
        "schema_version": "atelier.replan-delivery-fixture/1",
        "baseline_commit": git(project, "rev-parse", "HEAD"), "historical_runtime": historical,
        "historical_fails_current": True, "baseline_inventory": inventory(project),
    })
    return {"status": "prepared", "baseline_commit": git(project, "rev-parse", "HEAD"),
            "historical_runtime_checks": len(historical["checks"])}


def open_project(case):
    project = case / "project"
    need(project.is_dir() and not project.is_symlink() and (case / "fixture.json").is_file(),
         "Select the prepared disposable fixture")
    fixture = native.load_json(native.safe_path(case, "fixture.json"))
    need(fixture.get("schema_version") == "atelier.replan-delivery-fixture/1"
         and fixture["baseline_commit"] == git(project, "rev-parse", "HEAD"),
         "Fixture baseline commit changed")
    return project, fixture


def create_owner_decision(project, request_path, path, op):
    # The evaluator is the owner of this disposable fixture. It binds each decision
    # to the exact plan compiled by the production tool from current fixture bytes.
    result = command_json(python_tool(project, "ticket_replan_plan.py", "--root", project,
                                      "--projection", PROJECTION, "--request", request_path), project)
    plan = result["plan"]
    decision = {
        "schema_version": "atelier.ticket-replan-decision/1", "decision": "approve",
        "operation_id": op, "project_id": plan["project_id"], "native_revision": plan["native_revision"],
        "target_revision": plan["target_revision"], "projection": plan["projection"], "request": plan["request"],
        "plan_sha256": result["plan_sha256"], "authority_ref": "fieldslate-disposable-owner:replan-delivery-evaluation",
    }
    write_json(project, path, decision)
    return decision


def store_args(project, operation, *rest):
    return python_tool(project, "ticket_replan_store.py", operation, "--root", project,
                       "--projection", PROJECTION, *rest)


def check_projection(before, after):
    old = {record["id"]: record for record in before["tickets"]}
    new = {record["id"]: record for record in after["tickets"]}
    need(after["native_revision"] == TARGET, "Wrong applied revision")
    need(new["EXP-12"] == old["EXP-12"] and new["UI-07"] == old["UI-07"],
         "Historical or unrelated active task changed")
    need(new[TICKET]["status"] == "planned", "New Builder task is not planned")
    need(new["REL-19"]["status"] == "deferred" and new["REL-30"]["status"] == "deferred",
         "Expected old work preserved and retired")
    need(set(new["REL-25"]["depends_on"]) == {"REL-DOC", "REL-OPS"},
         "Expected release verification to follow both pieces of the split")
    for key in ("REL-DOC", "REL-OPS"):
        need(new[key]["depends_on"] == [TICKET], f"{key} must wait for implementation")


def apply(case):
    project, fixture = open_project(case)
    need(inventory(project) == fixture["baseline_inventory"], "Fixture changed before the plan")
    before = native.load_json(project / PROJECTION)
    decision = create_owner_decision(project, REQUEST, DECISION, OPERATION)
    competitor_path = f"{REVIEW}/competing-decision.json"
    competitor = create_owner_decision(project, f"{REVIEW}/competing.json", competitor_path, "competing-plan")
    apply_command = store_args(project, "apply", "--request", REQUEST, "--decision", DECISION)
    original = pin(project, PROJECTION)
    wrong = run([*apply_command, "--decision-sha256", "0" * 64], project)
    need(wrong.returncode != 0 and pin(project, PROJECTION) == original,
         "An invalid decision changed the projection")
    approved = [*apply_command, "--decision-sha256", pin(project, DECISION)["sha256"]]
    applied = command_json(approved, project)
    need(applied["status"] == "applied" and applied["verified_readback"] is True, "Apply did not complete")
    updated = pin(project, PROJECTION)
    # Query the owner store independently using only the expected operation identity,
    # as a caller would do if it did not see the original command return.
    readback = command_json(store_args(project, "receipt", "--operation-id", OPERATION,
                                       "--plan-sha256", decision["plan_sha256"]), project)
    need(readback["status"] == "verified" and readback["receipt"] == applied["receipt"],
         "Independent readback does not identify the applied transaction")
    replay = command_json(approved, project)
    need(replay["status"] == "replayed" and pin(project, PROJECTION) == updated,
         "Duplicate approval changed the projection")
    stale = run(store_args(project, "apply", "--request", f"{REVIEW}/competing.json",
                           "--decision", competitor_path, "--decision-sha256",
                           pin(project, competitor_path)["sha256"]), project)
    need(stale.returncode != 0 and pin(project, PROJECTION) == updated, "Stale decision wrote changes")
    check_projection(before, native.load_json(project / PROJECTION))

    board = command_json(python_tool(project, "ticket_tree.py", "board", "--root", project,
                                     "--input", PROJECTION), project)
    need(TICKET in board["board"]["ready"] and "REL-DOC" in board["board"]["blocked"]
         and "REL-OPS" in board["board"]["blocked"], "Unexpected applied readiness")
    need("UI-07" in board["board"]["in-progress"] and "EXP-12" in board["unsupported_acceptance_claims"],
         "Historical proof or independent work lost")
    handoff = command_json(python_tool(project, "ticket_handoff.py", "prepare", "--root", project,
                                       "--projection", PROJECTION, "--operation-id", OPERATION,
                                       "--plan-sha256", decision["plan_sha256"], "--ticket", TICKET,
                                       "--write-path", "src.py", "--return-path", BUILDER), project)
    write_json(project, HANDOFF, handoff)
    handoff_sha = pin(project, HANDOFF)["sha256"]
    verified = command_json(python_tool(project, "ticket_handoff.py", "verify", "--root", project,
                                        "--handoff", HANDOFF, "--handoff-sha256", handoff_sha), project)
    post_apply = inventory(project)
    need(all(post_apply[ref] == fixture["baseline_inventory"][ref]
             for ref in fixture["baseline_inventory"] if ref != PROJECTION),
         "Planning changed protected inputs")
    report = {"status": "applied-and-ready", "wrong_decision_exit_code": wrong.returncode,
              "stale_decision_exit_code": stale.returncode, "competing_plan_sha256": competitor["plan_sha256"],
              "applied": applied, "readback": readback, "replay_status": replay["status"],
              "ready": board["board"]["ready"], "blocked": board["board"]["blocked"],
              "handoff": pin(project, HANDOFF), "handoff_verified": verified,
              "builder_inventory": post_apply}
    write_json(case, "apply.json", report)
    return {"status": report["status"], "handoff": report["handoff"],
            "ready": report["ready"], "blocked": report["blocked"]}


def policy_command(project, codex, model, role):
    conflicts = sorted({ref for name in SKILLS for ref in native.installed_conflicts(name)})
    configured = ",".join("{path=" + json.dumps(ref) + ",enabled=false}" for ref in conflicts)
    denied = {str(path.resolve()) for path in (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
                                              Path("/etc/agents/skills"), Path("/etc/codex/skills"))
              if path.is_dir()}
    rules = {":slash_tmp": "read", ":tmpdir": "read", **{path: "none" for path in denied}}
    if role == "builder":
        rules.update({str(project / ref): "write" for ref in SCOPE})
    serialized = ",".join(json.dumps(key) + "=" + json.dumps(value) for key, value in sorted(rules.items()))
    policy = 'permissions={delivery={extends=":read-only",filesystem={' + serialized + '},network={enabled=false}}}'
    command = [codex, "-a", "never", "exec", "--ignore-user-config", "--strict-config", "--json",
               "--disable", "apps", "--disable", "memories", "--disable", "hooks", "--disable", "plugins",
               "-c", 'web_search="disabled"', "-c", 'model_reasoning_effort="low"',
               "-c", "skills.config=[" + configured + "]",
               "-C", str(project), "--model", model, "-c", 'default_permissions="delivery"', "-c", policy]
    if role == "builder":
        command += ["--ephemeral"]
    else:
        profile = project / ".codex/agents/foundry-qa.toml"
        command += ["-c", "agents.foundry-qa.config_file=" + json.dumps(str(profile)),
                    "-c", "agents.max_threads=2", "-c", "agents.max_depth=1"]
    # Avoid bytecode writes during a controlled read of the runnable fixture.
    return [*command, "-c", 'shell_environment_policy.set={PYTHONDONTWRITEBYTECODE="1"}', "-"]


def native_stage(case, project, args, role, prompt):
    subdir = case / role
    subdir.mkdir(mode=0o700)
    before = inventory(project)
    argv = policy_command(project, args.codex, args.model, role)
    (subdir / "prompt.md").write_text(prompt, encoding="utf-8")
    elapsed_from = time.monotonic()
    trace = subdir / "events.jsonl"
    with trace.open("xb") as out, (subdir / "diagnostics.log").open("xb") as err:
        code = native.run_native(argv, prompt.encode(), out, err, args.deadline)
    events = native.rows(trace)
    turns = [event for event in events if event.get("type") == "turn.completed"]
    threads = [event["thread_id"] for event in events if event.get("type") == "thread.started"]
    messages = [event["item"]["text"] for event in events if event.get("type") == "item.completed"
                and event.get("item", {}).get("type") == "agent_message"]
    after = inventory(project)
    report = {
        "model_requested": args.model, "thread_count": len(threads),
        "configured_exact_writable_paths": sorted(SCOPE) if role == "builder" else [],
        "thread_sha256": native.sha(threads[0].encode()) if len(threads) == 1 else None,
        "exit_code": code, "complete_turns": len(turns), "changed_paths": changes_from(before, after),
        "event_trace": pin(subdir, "events.jsonl"), "prompt": pin(subdir, "prompt.md"),
        "elapsed_ms": round((time.monotonic() - elapsed_from) * 1000),
    }
    if messages:
        answer = subdir / "answer.md"
        answer.write_text(messages[-1] + "\n", encoding="utf-8")
        report["answer"] = pin(subdir, "answer.md")
    return report, events, threads


def builder_return(project, handoff_sha):
    expected = {
        "schema_version": "atelier.ticket-builder-return/1",
        "handoff_sha256": handoff_sha,
        "ticket_id": TICKET,
        "status": "changes-prepared",
        "artifacts": [pin(project, "src.py")],
    }
    try:
        checked = command_json(python_tool(project, "ticket_handoff.py", "verify-result", "--root", project,
                                           "--handoff", HANDOFF, "--handoff-sha256", handoff_sha), project)
        if checked["status"] != "returned-artifacts-verified":
            return False
        result = native.load_json(native.safe_path(project, BUILDER))
        if set(result) != {*expected, "checks"} or any(result[key] != value for key, value in expected.items()):
            return False
        checks = result["checks"]
        return isinstance(checks, list) and bool(checks) and all(
            isinstance(check, str) and check.strip() for check in checks
        )
    except (OSError, ValueError, TypeError):
        return False


def builder(case, args):
    project, _ = open_project(case)
    applied = native.load_json(case / "apply.json")
    need(applied["builder_inventory"] == inventory(project), "Builder inputs drifted after application")
    sha = applied["handoff"]["sha256"]
    prompt = f"""$app-atelier-build
You are a fresh Builder session for the FieldSlate fixture. Begin with the exact ready-task handoff.
Run python3 -B candidate-tools/scripts/ticket_handoff.py verify --root "$PWD" --handoff {HANDOFF} --handoff-sha256 {sha}
Only continue if this returns verified-at-admission. Use its requirement excerpts, ticket and allowed scope.
Read .agents/skills/app-atelier-build/SKILL.md for the Builder workflow.
Read src.py and implement the approved shared v2 export of that one ticket. Do not change the app's interface.
Only src.py and {BUILDER} can be changed. Leave all ticket, decision, Git and evidence records untouched.
Use synthetic fixture data and local tools. Do not commit, send, deploy or access external sites.
Run your own bounded checks of both WSGI routes. Write {BUILDER} as one JSON object with exactly these keys:
schema_version (atelier.ticket-builder-return/1), handoff_sha256 ({sha}), ticket_id ({TICKET}),
status (changes-prepared), artifacts (an array containing path src.py and the sha256 of its actual new bytes),
and checks (a nonempty array of strings naming the checks you ran and what happened).
An independent reviewer will judge the actual output later. In your final answer include the checks you ran.
"""
    report, events, _ = native_stage(case, project, args, "builder", prompt)
    successful = [item for item in native.observed_commands(events) if item.get("exit_code") == 0]
    report["verified_handoff_observed"] = any("ticket_handoff.py verify" in item.get("command", "")
                                              and sha in item.get("command", "") for item in successful)
    report["skill_read"] = native.project_skill_read(successful, project, "app-atelier-build")
    report["return_record"] = pin(project, BUILDER) if (project / BUILDER).is_file() else None
    report["implementation"] = pin(project, "src.py")
    report["return_record_verified"] = builder_return(project, sha)
    success = (report["exit_code"] == 0 and report["complete_turns"] == 1 and report["thread_count"] == 1
               and set(report["changed_paths"]) == SCOPE and report["verified_handoff_observed"]
               and report["skill_read"] != "unverified" and report["return_record_verified"])
    report["status"] = "builder-returned" if success else "builder-needs-review"
    write_json(case, "builder-observation.json", report)
    need(success, "Builder has no complete verified bounded return; inspect the private observation")
    return {"status": report["status"], "implementation": report["implementation"],
            "return_record": report["return_record"], "skill_read": report["skill_read"]}


def child_oracle_observed(parent_id, child_sha, expected, command_marker="review/oracle.py current"):
    # Read only the linked fixture child's tool trace. Other transcripts contribute
    # their first metadata row solely to establish the parent linkage.
    sessions = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    now = datetime.now().astimezone()
    for offset in (-1, 0, 1):
        day = sessions / (now + timedelta(days=offset)).strftime("%Y/%m/%d")
        for path in day.glob("rollout-*.jsonl"):
            if not path.is_file() or path.is_symlink():
                continue
            with path.open(encoding="utf-8") as stream:
                try:
                    event = json.loads(stream.readline())
                except ValueError:
                    continue
                source = event.get("payload", {}).get("source")
                if event.get("type") != "session_meta" or not isinstance(source, dict):
                    continue
                spawn = source.get("subagent", {}).get("thread_spawn", {})
                if spawn.get("parent_thread_id") != parent_id:
                    continue
                if native.sha(path.read_bytes()) != child_sha:
                    return False
                calls = set()
                for line in stream:
                    tool = json.loads(line).get("payload", {})
                    if tool.get("type") in {"function_call", "custom_tool_call"}:
                        invocation = tool.get("input") or tool.get("arguments") or ""
                        if tool.get("name") in {"exec", "exec_command"} and command_marker in invocation:
                            calls.add(tool.get("call_id"))
                    if (tool.get("type") not in {"function_call_output", "custom_tool_call_output"}
                            or tool.get("call_id") not in calls):
                        continue
                    output = tool.get("output")
                    parts = [output] if isinstance(output, str) else [
                        part["text"] for part in output or [] if isinstance(part, dict) and "text" in part
                    ]
                    for part in parts:
                        for record in part.splitlines():
                            try:
                                observed = json.loads(record.strip())
                            except ValueError:
                                continue
                            if observed == expected:
                                return True
                            if isinstance(observed, dict) and observed.get("status") == "fulfilled":
                                observed = observed.get("value")
                            if not isinstance(observed, dict) or observed.get("exit_code") != 0:
                                continue
                            shell_output = observed.get("output")
                            if not isinstance(shell_output, str):
                                continue
                            for shell_line in shell_output.splitlines():
                                try:
                                    value = json.loads(shell_line)
                                except ValueError:
                                    continue
                                if value == expected:
                                    return True
                return False
    return False


def qa(case, args):
    project, _ = open_project(case)
    applied = native.load_json(case / "apply.json")
    builder_obs = native.load_json(case / "builder-observation.json")
    need(builder_obs["status"] == "builder-returned" and builder_obs["implementation"] == pin(project, "src.py")
         and builder_obs["return_record"] == pin(project, BUILDER), "Builder output changed before QA")
    after_builder = inventory(project)
    need(set(changes_from(applied["builder_inventory"], after_builder)) == SCOPE,
         "Builder changed more than the implementation and return record")
    checked_return = builder_return(project, applied["handoff"]["sha256"])
    need(checked_return, "Builder return is out of date")
    copy_review_tool(project, "oracle.py")
    pin_source = pin(project, "src.py")["sha256"]
    current = command_json([sys.executable, "-B", f"{REVIEW}/oracle.py", "current"], project)
    prompt = f"""Independently review the FieldSlate implementation in this fresh session. Use one fresh non-forked foundry-qa subagent. It must run python3 -B {REVIEW}/oracle.py current and compare the actual result to requirements.json and the pinned implementation SHA {pin_source}. It should inspect {HANDOFF} and {BUILDER}, check both WSGI download entry points, confirm old evidence is historical, and report any missing proof. No writes, no external sites, no production acceptance. Wait for its review. Return its explicit QA_VERDICT=PASS or QA_VERDICT=FAIL, the full observed implementation SHA, and the checks actually observed.
"""
    report, events, threads = native_stage(case, project, args, "qa", prompt)
    profile = native.safe_path(project, ".codex/agents/foundry-qa.toml")
    provenance = native.owned_role_provenance(threads[0], "foundry-qa", profile.read_text(encoding="utf-8")) \
        if len(threads) == 1 else None
    answer_path = case / "qa" / "answer.md"
    verdict = answer_path.read_text(encoding="utf-8") if answer_path.is_file() else ""
    successful = [item for item in native.observed_commands(events) if item.get("exit_code") == 0]
    report["runtime_oracle"] = current
    report["exact_implementation"] = {"path": "src.py", "sha256": pin_source}
    report["child_provenance"] = provenance
    report["observed_child_runtime_result"] = child_oracle_observed(
        threads[0], provenance["child_rollout_sha256"], current
    ) if provenance and provenance["observed"] else False
    report["observed_parent_runtime_command"] = any("oracle.py current" in item.get("command", "")
                                                    for item in successful)
    report["checked_builder_return"] = checked_return
    success = (report["exit_code"] == 0 and report["complete_turns"] == 1 and not report["changed_paths"]
               and report["thread_sha256"] != builder_obs["thread_sha256"]
               and provenance is not None and provenance["observed"] is True
               and report["observed_child_runtime_result"] and "QA_VERDICT=PASS" in verdict
               and "QA_VERDICT=FAIL" not in verdict
               and pin_source in verdict and current["status"] == "passed")
    report["status"] = "independent-review-passed" if success else "independent-review-needs-check"
    write_json(case, "qa-observation.json", report)
    need(success, "QA has no complete verified role return; inspect the private observation")
    return {"status": report["status"], "runtime_checks": len(current["checks"]),
            "implementation": report["exact_implementation"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["prepare", "apply", "builder", "qa"])
    parser.add_argument("--case-dir", required=True, type=Path)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--deadline", type=int, default=300)
    args = parser.parse_args()
    case = args.case_dir.absolute()
    try:
        need(case == case.resolve(), "Use a canonical case path without symlinks")
        if args.stage == "prepare":
            result = prepare(case)
        elif args.stage == "apply":
            result = apply(case)
        else:
            need(args.codex and native.auth_ok(args.codex), "Native Codex requires existing ChatGPT login")
            need(args.deadline > 0, "Expected a positive deadline")
            result = builder(case, args) if args.stage == "builder" else qa(case, args)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
