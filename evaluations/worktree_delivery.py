#!/usr/bin/env python3
"""Observe parallel native Builder work, actual interruption and integration."""

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import shlex
import signal
import subprocess
import sys
import time

import native_canary as native
from replan_delivery import (changes_from, child_oracle_observed, command_json,
                             git, inventory, need, pin, run, write_json)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "worktree_delivery"
SKILL = "app-atelier-build"
ORACLE = [sys.executable, "-B", "oracle.py"]
FILES = {
    "catalog": ("catalog.py", "review/catalog-checkpoint.json", "review/catalog-return.json"),
    "quote": ("quotation.py", "review/quote-return.json"),
}
BRANCHES = {"catalog": "codex/catalog", "quote": "codex/quote",
            "integration": "codex/integration"}
SYSTEM_SCOPE = ("catalog.py", "quotation.py")
SCHEMA = "atelier.worktree-fixture-return/1"
WORKTREE_TOOL = native.REPO / "scripts/ticket_worktree.py"
CHECKPOINT_TOOL = native.REPO / "scripts/ticket_worktree_checkpoint.py"


def stage_git(git_root, worktree, branch, base):
    git(git_root, "worktree", "add", "-b", branch, str(worktree), base)
    need(git(worktree, "rev-parse", "HEAD") == base, "Worktree started at a different commit")
    need(git(worktree, "symbolic-ref", "--short", "HEAD") == branch, "Worktree branch differs")


def snapshot(root):
    # .git in a linked checkout is a locator file, not product content.
    result = inventory(root)
    result.pop(".git", None)
    return result


def changed(root, expected):
    return set(changes_from(expected, snapshot(root)))


def prepare(case, source=native.REPO):
    for path in (WORKTREE_TOOL, CHECKPOINT_TOOL):
        expected = source / path.relative_to(native.REPO)
        need(expected.read_bytes() == path.read_bytes(),
             f"Reference verification tool differs from the active evaluation harness: {path.name}")
    case.mkdir(mode=0o700)
    repo = case / "project"
    repo.mkdir()
    for path in FIXTURE.iterdir():
        if path.is_file():
            shutil.copy2(path, repo / path.name)
    native.pin_skill(repo, SKILL, native.skill_source(SKILL, source))
    profile = repo / ".codex/agents/foundry-qa.toml"
    profile.parent.mkdir(parents=True)
    shutil.copy2(source / "agent-profiles/foundry-qa.toml", profile)
    (repo / "review").mkdir()
    for paths in FILES.values():
        for name in paths[1:]:
            (repo / name).write_text("{}\n", encoding="utf-8")
    git(repo, "init", "--quiet", "--template=")
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "-m", "Quoted produce fixture baseline")
    base = git(repo, "rev-parse", "HEAD")
    for name, branch in BRANCHES.items():
        stage_git(repo, case / name, branch, base)
    baseline = snapshot(repo)
    need(all(snapshot(case / name) == baseline for name in BRANCHES),
         "Fixture worktrees did not reproduce the same baseline")
    failures = {}
    for lane in ("catalog", "quote", "combined"):
        failure = run([*ORACLE, lane], repo)
        expected_failure = "ValueError: unknown sku" if lane != "quote" else "AssertionError: quote:"
        need(failure.returncode != 0 and expected_failure in failure.stderr,
             f"Baseline unexpectedly satisfies the {lane} oracle")
        failures[lane] = native.sha(failure.stderr.encode())
    for lane, paths in FILES.items():
        binding = command_json([sys.executable, "-B", str(WORKTREE_TOOL), "bind",
                                "--root", str(repo), "--base", base,
                                "--worktree", str(case / lane), "--branch", BRANCHES[lane],
                                *(part for path in paths for part in ("--write-path", path))], repo)
        write_json(case, f"{lane}-binding.json", binding)
    prepared = {"baseline_commit": base, "baseline_files": baseline,
                "baseline_oracle_failures": failures,
                "verification_tool_sha256": {
                    str(path.relative_to(native.REPO)): native.sha(path.read_bytes())
                    for path in (WORKTREE_TOOL, CHECKPOINT_TOOL)
                }}
    write_json(case, "prepared.json", prepared)
    return {"status": "prepared", "baseline_commit": base,
            "worktrees": {key: str(case / key) for key in BRANCHES}}


def policy_command(args, root, scope, *, reviewer=False):
    conflicts = ",".join(
        "{path=" + json.dumps(ref) + ",enabled=false}" for ref in native.installed_conflicts(SKILL)
    )
    denied = {str(path.resolve()) for path in (
        Path.home() / ".agents/skills", Path.home() / ".codex/skills",
        Path("/etc/agents/skills"), Path("/etc/codex/skills"),
    ) if path.is_dir()}
    # Git still needs the shared metadata, while source files in sibling worktrees
    # belong to other assignments.
    avoid_siblings = {str(root.parent / name / path): "none"
                      for name in ("project", *BRANCHES)
                      if (root.parent / name) != root for path in SYSTEM_SCOPE}
    rules = {":slash_tmp": "read", ":tmpdir": "read", **avoid_siblings,
             **{path: "none" for path in denied},
             **{str(root / path): "write" for path in scope}}
    serialized = ",".join(json.dumps(key) + "=" + json.dumps(value)
                          for key, value in sorted(rules.items()))
    policy = 'permissions={worktree={extends=":read-only",filesystem={' + serialized + '},network={enabled=false}}}'
    command = [
        args.codex, "-a", "never", "exec", "--ignore-user-config", "--strict-config", "--json",
        "--disable", "apps", "--disable", "memories", "--disable", "hooks", "--disable", "plugins",
        "-c", 'web_search="disabled"', "-c", f'model_reasoning_effort="{args.effort}"',
        "-c", "skills.config=[" + conflicts + "]",
        "-C", str(root), "--model", args.model, "-c", 'default_permissions="worktree"', "-c", policy,
    ]
    if reviewer:
        profile = root / ".codex/agents/foundry-qa.toml"
        command += ["-c", "agents.foundry-qa.config_file=" + json.dumps(str(profile)),
                    "-c", "agents.max_threads=2", "-c", "agents.max_depth=1"]
    elif not args.persist_model_receipt:
        command.append("--ephemeral")
    return command + ["-c", 'shell_environment_policy.set={PYTHONDONTWRITEBYTECODE="1"}', "-"]


def read_events(path):
    records = []
    with path.open("rb") as stream:
        for line in stream:
            if line.endswith(b"\n") and line.strip():
                records.append(json.loads(line))
    return records


class NativeRun:
    def __init__(self, stack, args, root, evidence, scope, prompt, reviewer=False):
        evidence.mkdir(mode=0o700)
        self.root, self.evidence, self.scope = root, evidence, scope
        self.model, self.effort = args.model, args.effort
        self.persisted = reviewer or args.persist_model_receipt
        self.trace = evidence / "events.jsonl"
        self.baseline = snapshot(root)
        (evidence / "prompt.md").write_text(prompt, encoding="utf-8")
        output = stack.enter_context(self.trace.open("xb"))
        errors = stack.enter_context((evidence / "diagnostics.log").open("xb"))
        self.started = time.monotonic_ns()
        self.process = subprocess.Popen(policy_command(args, root, scope, reviewer=reviewer),
                                        cwd=root, stdin=subprocess.PIPE, stdout=output,
                                        stderr=errors, start_new_session=True,
                                        env=native.native_environment())
        stack.callback(self.stop)
        self.process.stdin.write(prompt.encode())
        self.process.stdin.close()

    def events(self):
        return read_events(self.trace)

    def threads(self):
        return [item["thread_id"] for item in self.events() if item.get("type") == "thread.started"]

    def stop(self):
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.process.pid, signal.SIGKILL)
                self.process.wait(timeout=5)

    def observe(self, deadline):
        self.process.wait(timeout=deadline)
        observed_at = time.monotonic_ns()
        events = self.events()
        threads = self.threads()
        messages = [event["item"]["text"] for event in events if event.get("type") == "item.completed"
                    and event.get("item", {}).get("type") == "agent_message"]
        if messages:
            (self.evidence / "answer.md").write_text(messages[-1] + "\n", encoding="utf-8")
        now = snapshot(self.root)
        turns = [event for event in events if event.get("type") == "turn.completed"]
        model_receipt = native.native_turn_receipt(threads[0]) if self.persisted and len(threads) == 1 else None
        return {
            "exit_code": self.process.returncode,
            "turn_count": len(turns),
            "model_requested": self.model, "effort_requested": self.effort,
            "persisted": self.persisted,
            "model_receipt": model_receipt,
            "matches_requested_model": native.matches_model(model_receipt, self.model, self.effort),
            "usage": turns[0].get("usage") if len(turns) == 1 else None,
            "thread_count": len(threads),
            "thread_sha256": native.sha(threads[0].encode()) if len(threads) == 1 else None,
            "pid": self.process.pid, "started_monotonic_ns": self.started,
            "observed_monotonic_ns": observed_at,
            "git_head": git(self.root, "rev-parse", "HEAD"),
            "branch": git(self.root, "symbolic-ref", "--short", "HEAD"),
            "worktree": str(self.root),
            "events_sha256": native.sha(self.trace.read_bytes()),
            "prompt_sha256": native.sha((self.evidence / "prompt.md").read_bytes()),
            "configured_write_paths": list(self.scope),
            "changed": sorted(changed(self.root, self.baseline)),
            "write_pins": {path: now[path] for path in self.scope if path in now},
            "observed_skill": native.project_skill_read(
                native.observed_commands(events), self.root, SKILL),
        }


def return_prompt(file, receipt, lane):
    artifact_example = f'{{"path": "{file}", "sha256": "ACTUAL_SHA256"}}'
    return f"""
Use python3 -B oracle.py {lane} before returning. Write {receipt} with the exact JSON
fields schema_version "{SCHEMA}", artifact {artifact_example}, and checks as a
nonempty JSON array of check names actually observed. Use the actual source hash
as ACTUAL_SHA256. Change only {file} and {receipt}. Leave Git operations to the coordinator.
"""


INTERRUPT_PROMPT = """$app-atelier-build
This is the catalog Builder in a disposable worktree. Read .agents/skills/app-atelier-build/SKILL.md
and catalog.py. Implement exactly ONE partial step: normalize supplied text with .strip().upper()
before the existing lookup, leaving the rest of the function for a continuation. The next session
will enforce ASCII, including whitespace, and run the acceptance checks. Leave PRICES unchanged.
Only catalog.py and review/catalog-checkpoint.json may change. Write the checkpoint JSON with
exact fields schema_version "atelier.worktree-fixture-checkpoint/1", artifact with path "catalog.py"
and the sha256 of the actual saved file, and next_action "Enforce ASCII input and run the catalog oracle".
Apply the source and checkpoint changes and save them before the next shell tool call. Then call
python3 -B hold.py and wait. This read-only fixture command lets the coordinator intentionally
interrupt this session after the real source checkpoint is durable.
"""
QUOTE_PROMPT = """$app-atelier-build
This is the quotation Builder in a disposable worktree. Read .agents/skills/app-atelier-build/SKILL.md
and quotation.py. Update only quotation.py: valid quantity is an int from 1 to 100 inclusive
and bool is invalid. Invalid quantity must raise ValueError. Use Decimal arithmetic and rounding
half up to two fractional digits. Keep the quantity and total fields and return currency USD.
""" + return_prompt("quotation.py", "review/quote-return.json", "quote")


def verify_return(root, file, receipt):
    record = native.load_json(root / receipt)
    need(set(record) == {"schema_version", "artifact", "checks"}
         and record["schema_version"] == SCHEMA
         and record["artifact"] == pin(root, file)
         and isinstance(record["checks"], list)
         and record["checks"]
         and all(isinstance(check, str) and check.strip() for check in record["checks"]),
         f"Builder return failed actual artifact verification for {file}")
    return record


def catalog_checkpoint(root):
    try:
        record = native.load_json(root / "review/catalog-checkpoint.json")
        wanted = {"schema_version": "atelier.worktree-fixture-checkpoint/1",
                  "artifact": pin(root, "catalog.py"),
                  "next_action": "Enforce ASCII input and run the catalog oracle"}
        return record == wanted
    except (OSError, ValueError):
        return False


def parallel(case, args):
    prepared = native.load_json(case / "prepared.json")
    baseline = prepared["baseline_files"]
    repo = case / "project"
    for lane, paths in FILES.items():
        current = product_call(
            WORKTREE_TOOL, repo, "bind", "--root", repo, "--base", prepared["baseline_commit"],
            "--worktree", case / lane, "--branch", BRANCHES[lane],
            *(part for path in paths for part in ("--write-path", path)),
        )
        need(current == native.load_json(case / f"{lane}-binding.json")
             and snapshot(case / lane) == baseline, f"The {lane} worktree changed before launch")
    catalog, quote = case / "catalog", case / "quote"
    evidence = case / "native"
    evidence.mkdir(mode=0o700)
    with ExitStack() as stack:
        first = NativeRun(stack, args, catalog, evidence / "catalog-first",
                          FILES["catalog"][:2], INTERRUPT_PROMPT)
        second = NativeRun(stack, args, quote, evidence / "quote",
                           FILES["quote"], QUOTE_PROMPT)
        deadline = time.monotonic() + args.deadline
        confirmed_overlap = False
        observed_hold = False
        while time.monotonic() < deadline:
            events_a, events_b = first.events(), second.events()
            if (first.process.poll() is None and second.process.poll() is None
                    and first.threads() and second.threads()):
                confirmed_overlap = True
            observed_hold = any(event.get("type") == "item.started"
                                and event.get("item", {}).get("type") == "command_execution"
                                and "python3 -B hold.py" in event["item"].get("command", "")
                                for event in events_a)
            if observed_hold and catalog_checkpoint(catalog) and first.process.poll() is None:
                break
            need(first.process.poll() is None,
                 "First native session exited ahead of the intended interruption")
            time.sleep(0.25)
        need(observed_hold and catalog_checkpoint(catalog) and first.process.poll() is None,
             "The durable catalog checkpoint and live hold were not observed")
        partial = pin(catalog, "catalog.py")
        first.stop()
        stopped = first.observe(5)
        need(stopped["exit_code"] in (-signal.SIGTERM, -signal.SIGKILL)
             and stopped["turn_count"] == 0 and stopped["thread_count"] == 1
             and (not stopped["persisted"] or stopped["matches_requested_model"]),
             "Native catalog interruption did not stop a live unfinished turn")
        need(catalog_checkpoint(catalog) and pin(catalog, "catalog.py") == partial,
             "Catalog checkpoint changed after termination")
        need(confirmed_overlap, "Both fresh native sessions were not observed live together")
        need(changed(catalog, baseline) == set(FILES["catalog"][:2]),
             "Interrupted Builder modified files outside its checkpoint scope")
        rejection = run([*ORACLE, "catalog"], catalog)
        need(rejection.returncode != 0 and "permitted" in rejection.stderr,
             "Partial catalog already passed, or failed the wrong behavior")
        returned = second.observe(max(5, deadline - time.monotonic()))
        need(returned["exit_code"] == 0 and returned["turn_count"] == 1
             and returned["thread_count"] == 1 and returned["observed_skill"] != "unverified"
             and (not returned["persisted"] or returned["matches_requested_model"]),
             "Independent quotation Builder did not complete its native role")
        need(changed(quote, baseline) == set(FILES["quote"]),
             "Independent Builder modified files outside scope")
        need(stopped["thread_sha256"] != returned["thread_sha256"],
             "Workers shared a native session")
        verify_return(quote, *FILES["quote"])
        oracle = command_json([*ORACLE, "quote"], quote)
    report = {"status": "native-parallel-interruption-observed",
              "catalog_initial": stopped, "quote": returned, "quote_oracle": oracle,
              "concurrent_native_processes_observed": confirmed_overlap,
              "partial_source": partial,
              "durable_partial_checkpoint": pin(catalog, "review/catalog-checkpoint.json"),
              "partial_catalog_oracle_failure_sha256": native.sha(rejection.stderr.encode())}
    write_json(case, "parallel.json", report)
    return report


def product_call(tool, cwd, operation, *argv):
    return command_json([sys.executable, "-B", str(tool), operation, *map(str, argv)], cwd)


def checkpoint_options(case):
    return ["--checkpoint", str(case / "catalog-resume-checkpoint.json"),
            "--checkpoint-sha256", pin(case, "catalog-resume-checkpoint.json")["sha256"]]


def checkpoint(case):
    observed = native.load_json(case / "parallel.json")
    catalog = case / "catalog"
    need(observed["status"] == "native-parallel-interruption-observed"
         and catalog_checkpoint(catalog)
         and pin(catalog, "catalog.py") == observed["partial_source"],
         "The live stopped worker no longer matches its recorded partial work")
    binding_sha = pin(case, "catalog-binding.json")["sha256"]
    interrupted = observed["catalog_initial"]
    record = {
        "schema_version": "atelier.worktree-interruption/1",
        "binding_sha256": binding_sha, "state": "interrupted",
        "native_run_ref": "codex-thread-sha256:" + interrupted["thread_sha256"],
        "readback_ref": ("codex-exec-process-wait:exit=" + str(interrupted["exit_code"])
                         + ";events-sha256:" + interrupted["events_sha256"]),
        "next_action": "Enforce ASCII input and run the catalog oracle",
    }
    write_json(case, "catalog-interruption.json", record)
    snapshot_state = product_call(
        CHECKPOINT_TOOL, catalog, "capture",
        "--binding", case / "catalog-binding.json", "--binding-sha256", binding_sha,
        "--interruption", case / "catalog-interruption.json",
        "--interruption-sha256", pin(case, "catalog-interruption.json")["sha256"],
    )
    write_json(case, "catalog-resume-checkpoint.json", snapshot_state)
    # Change one authorized byte in the disposable fixture, check refusal, and restore the
    # exact interrupted content. The native recovery starts only after the original pin matches.
    partial = catalog / "catalog.py"
    raw = partial.read_bytes()
    try:
        partial.write_bytes(raw + b"\n")
        refused = run([sys.executable, "-B", str(CHECKPOINT_TOOL), "resume",
                       *checkpoint_options(case)], catalog)
        need(refused.returncode != 0 and "checkpoint is stale" in refused.stderr,
             "The product resume gate admitted modified partial bytes")
    finally:
        partial.write_bytes(raw)
    admission = product_call(CHECKPOINT_TOOL, catalog, "resume", *checkpoint_options(case))
    need(admission["status"] == "ready-to-resume" and admission["worktree"] == str(catalog),
         "The exact interrupted worktree did not pass resume admission")
    report = {"status": "native-resume-admitted", "admission": admission,
              "stale_fixture_rejected": True,
              "refusal_sha256": native.sha(refused.stderr.encode())}
    write_json(case, "checkpoint.json", report)
    return report


def matches_shell_command(command, expected):
    try:
        argv = shlex.split(command)
        if len(argv) == 3 and Path(argv[0]).name in {"sh", "bash", "zsh"} and argv[1] in {"-c", "-lc"}:
            argv = shlex.split(argv[2])
        return argv == expected
    except ValueError:
        return False


def resume(case, args):
    before = native.load_json(case / "parallel.json")
    catalog = case / "catalog"
    admitted = native.load_json(case / "checkpoint.json")["admission"]
    current = product_call(CHECKPOINT_TOOL, catalog, "resume", *checkpoint_options(case))
    need(current == admitted, "Actual recovery admission changed since coordinator readback")
    command = ["python3", "-B", str(CHECKPOINT_TOOL), "resume", *checkpoint_options(case)]
    prompt = f"""$app-atelier-build
This is a new session continuing the stopped catalog Builder in the same disposable worktree.
Before changing any file, run this exact command and read its actual output:
{shlex.join(command)}
Proceed following ready-to-resume. Read .agents/skills/app-atelier-build/SKILL.md and catalog.py.
Preserve the already saved strip+uppercase normalization and the PRICES constant. Add a check
before normalization that rejects non-ASCII input, including non-ASCII whitespace, with
ValueError. The existing lookup must still refuse unknown and internally spaced SKUs.
""" + return_prompt("catalog.py", "review/catalog-return.json", "catalog")
    with ExitStack() as stack:
        process = NativeRun(stack, args, catalog, case / "native/catalog-resume",
                            (FILES["catalog"][0], FILES["catalog"][2]), prompt)
        observed = process.observe(args.deadline)
        successful = [item for item in native.observed_commands(process.events())
                      if item.get("exit_code") == 0]
    need(observed["exit_code"] == 0 and observed["turn_count"] == 1
         and observed["thread_count"] == 1
         and (not observed["persisted"] or observed["matches_requested_model"])
         and observed["thread_sha256"] not in {before["catalog_initial"]["thread_sha256"],
                                             before["quote"]["thread_sha256"]},
         "The resumed work did not complete in a new native session")
    need(observed["observed_skill"] != "unverified", "Resumed Builder skill readback missing")
    need(observed["changed"] == ["catalog.py", "review/catalog-return.json"],
         "Resumed native Builder changed paths outside its assignment")
    need(any(matches_shell_command(item.get("command", ""), command)
             and '"status": "ready-to-resume"' in item.get("aggregated_output", "")
             and before["partial_source"]["sha256"] in item.get("aggregated_output", "")
             for item in successful), "No successful native resume gate with the actual partial pin was observed")
    result = verify_return(catalog, "catalog.py", "review/catalog-return.json")
    runtime = command_json([*ORACLE, "catalog"], catalog)
    need(pin(catalog, "review/catalog-checkpoint.json") == before["durable_partial_checkpoint"],
         "Resumed Builder modified the original checkpoint")
    report = {"status": "fresh-native-resume-passed", "native_resume": observed,
              "checkpoint_admission_observed_in_native_thread": True, "runtime": runtime,
              "worker_return": result}
    write_json(case, "resume.json", report)
    return report


def freeze_worker(case, lane):
    worktree = case / lane
    source = FILES[lane][0]
    evidence = case / "native" / f"{lane}-accepted"
    evidence.mkdir(mode=0o700)
    review_paths = FILES[lane][1:]
    review = {}
    for ref in review_paths:
        relative = Path(ref).name
        shutil.copy2(worktree / ref, evidence / relative)
        review[ref] = pin(evidence, relative)["sha256"]
    # Git ignores worker report files as candidates. Retain their original bytes beside the
    # event traces first. Restore only those fixture placeholders before making the source commit.
    git(worktree, "restore", "--worktree", "--", *review_paths)
    baseline = native.load_json(case / "prepared.json")["baseline_files"]
    need(changed(worktree, baseline) == {source}, "Only the assigned source may become a candidate commit")
    git(worktree, "add", "--", source)
    git(worktree, "commit", "--quiet", "-m", f"Native {lane} Builder return")
    commit = git(worktree, "rev-parse", "HEAD")
    binding = f"{lane}-binding.json"
    digest = pin(case, binding)["sha256"]
    candidate = product_call(WORKTREE_TOOL, worktree, "candidate",
                             "--binding", case / binding, "--binding-sha256", digest,
                             "--commit", commit)
    write_json(case, f"{lane}-candidate.json", candidate)
    return {"binding_path": str(case / binding), "binding_sha256": digest, "commit": commit,
            "archived_worker_review": review, "source": pin(worktree, source)}


def require_both_workers(case):
    isolated_failures = {}
    for lane, expected in (("catalog", "AssertionError: quote:"),
                           ("quote", "ValueError: unknown sku")):
        isolated = run([*ORACLE, "combined"], case / lane)
        need(isolated.returncode != 0 and expected in isolated.stderr,
             f"The {lane} worktree alone lacks the expected combined failure")
        isolated_failures[lane] = native.sha(isolated.stderr.encode())
    return isolated_failures


def integrate(case):
    base = native.load_json(case / "prepared.json")
    outcome = native.load_json(case / "resume.json")
    need(outcome["status"] == "fresh-native-resume-passed", "Fresh resume did not pass")
    repo, integration = case / "project", case / "integration"
    need(git(integration, "rev-parse", "HEAD") == base["baseline_commit"],
         "Integration must start from the recorded untouched base")
    isolated_failures = require_both_workers(case)
    workers = [freeze_worker(case, lane) for lane in ("catalog", "quote")]
    flags = [token for worker in workers for token in (
        "--binding", worker["binding_path"], "--binding-sha256", worker["binding_sha256"],
        "--commit", worker["commit"],
    )]
    plan = product_call(WORKTREE_TOOL, repo, "plan", "--root", repo,
                        "--integration", integration, *flags)
    need(git(integration, "rev-parse", "HEAD") == base["baseline_commit"],
         "Preparing the integration plan moved the integration branch")
    write_json(case, "integration-plan.json", plan)
    ref = str(case / "integration-plan.json")
    digest = pin(case, "integration-plan.json")["sha256"]
    args = ["--plan", ref, "--plan-sha256", digest]
    first = product_call(WORKTREE_TOOL, repo, "apply", *args)
    replay = product_call(WORKTREE_TOOL, repo, "apply", *args)
    need(first["status"] == "integrated" and replay["status"] == "already-integrated"
         and first["head"] == replay["head"], "Integration did not land exactly once")
    expected_parents = [base["baseline_commit"], *(worker["commit"] for worker in workers)]
    observed_parents = git(integration, "rev-list", "--parents", "-n", "1", first["head"]).split()[1:]
    need(observed_parents == expected_parents, "Integration lost a worker commit")
    need(git(repo, "rev-parse", "HEAD") == base["baseline_commit"]
         and snapshot(repo) == base["baseline_files"], "Starting checkout changed during integration")
    need(changed(integration, base["baseline_files"]) == set(SYSTEM_SCOPE),
         "Integration changed files outside both verified worker assignments")
    for item in workers:
        source = item["source"]
        need(pin(integration, source["path"]) == source, "Integrated source differs from native return")
    oracle = command_json([*ORACLE, "combined"], integration)
    report = {"status": "native-returns-integrated-and-verified", "workers": workers,
              "apply": first, "replay": replay, "parent_commits": observed_parents,
              "starting_checkout_preserved": True, "combined_oracle": oracle,
              "unintegrated_oracle_failures": isolated_failures}
    write_json(case, "integration.json", report)
    return report


def review(case, args):
    before = native.load_json(case / "parallel.json")
    resumed = native.load_json(case / "resume.json")
    outcome = native.load_json(case / "integration.json")
    root = case / "integration"
    source_pins = [pin(root, ref) for ref in SYSTEM_SCOPE]
    expected = command_json([*ORACLE, "combined"], root)
    need(outcome["combined_oracle"] == expected, "Combined behavior changed ahead of independent QA")
    prompt = f"""Independently verify the integrated quote service in this disposable worktree.
Use one fresh non-forked foundry-qa child. It must run python3 -B oracle.py combined,
execute the actual WSGI service, and compare file pins against {json.dumps(source_pins)}.
Require it to report exact observed source hashes and all checks actually observed.
Use local read-only tools. Wait for the reviewer. Report QA_VERDICT=PASS or QA_VERDICT=FAIL
and both current SHA-256 values with its evidence.
"""
    if args.replay_captured_review:
        qa = case / "native/qa"
        trace = qa / "events.jsonl"
        events = native.rows(trace)
        threads = [item["thread_id"] for item in events if item.get("type") == "thread.started"]
        head = git(root, "rev-parse", "HEAD")
        need(head == outcome["apply"]["head"] and not git(root, "status", "--porcelain")
             and source_pins == [item["source"] for item in outcome["workers"]],
             "The integrated worktree does not match the observed pre-review commit and source")
        observed = {
            "mode": "rechecked-captured-native-review",
            "turn_count": sum(item.get("type") == "turn.completed" for item in events),
            "thread_count": len(threads),
            "thread_sha256": native.sha(threads[0].encode()) if len(threads) == 1 else None,
            "worktree": str(root), "git_head": head,
            "git_readback_clean_after_review": True,
            "events_sha256": native.sha(trace.read_bytes()),
            "prompt_sha256": pin(qa, "prompt.md")["sha256"],
        }
    else:
        with ExitStack() as stack:
            process = NativeRun(stack, args, root, case / "native/qa", (), prompt, reviewer=True)
            observed = process.observe(args.deadline)
            threads = process.threads()
        write_json(case, "qa-parent-observation.json", observed)
    profile = (root / ".codex/agents/foundry-qa.toml").read_text(encoding="utf-8")
    model, effort = (None, None) if args.replay_captured_review else (args.model, args.effort)
    provenance = (native.owned_role_provenance(threads[0], "foundry-qa", profile, model, effort)
                  if len(threads) == 1 else None)
    verdict = (case / "native/qa/answer.md").read_text(encoding="utf-8")
    child_check = child_oracle_observed(provenance["child_thread_id"], provenance["child_rollout_sha256"], expected,
                                        command_marker="oracle.py combined") if provenance and provenance["observed"] else False
    preserved = (observed["git_readback_clean_after_review"] if args.replay_captured_review
                 else observed["exit_code"] == 0 and not observed["changed"] and observed["matches_requested_model"])
    need(preserved and observed["turn_count"] == 1 and observed["thread_count"] == 1
         and observed["thread_sha256"] not in {before["catalog_initial"]["thread_sha256"],
                                             before["quote"]["thread_sha256"],
                                             resumed["native_resume"]["thread_sha256"]}
         and child_check and "QA_VERDICT=PASS" in verdict and "QA_VERDICT=FAIL" not in verdict
         and all(item["sha256"] in verdict for item in source_pins),
         "No complete independent native QA return with exact combined runtime evidence")
    report = {"status": "independent-native-worktree-review-passed", "review_thread": observed,
              "child_provenance": provenance, "child_observed_combined_oracle": True,
              "runtime": expected, "implementation": source_pins}
    write_json(case, "review.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "parallel", "checkpoint", "resume", "integrate", "review"))
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--model", help="Alternate model pin requires the explicit baseline replay")
    parser.add_argument("--baseline-replay", action="store_true")
    parser.add_argument("--baseline-source", type=Path, help="Use the reviewed baseline checkout when preparing")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default=native.DEFAULT_EFFORT)
    parser.add_argument("--deadline", type=int, default=300)
    parser.add_argument("--persist-model-receipt", action="store_true",
                        help="Allow disposable Builder rollouts for exact model readback")
    parser.add_argument("--replay-captured-review", action="store_true",
                        help="Verify previously captured native QA without launching another session")
    args = parser.parse_args()
    case = args.case_dir.resolve()
    try:
        temp = Path("/tmp").resolve()
        need(case != temp and case.is_relative_to(temp), "Use a disposable case under /tmp")
        need(30 <= args.deadline <= 600, "Deadline must be between 30 and 600 seconds")
        need(args.baseline_source is None or args.stage == "prepare",
             "Set the reviewed reference source when preparing")
        if args.replay_captured_review:
            need(args.stage == "review", "Captured review replay applies only to the review stage")
            result = review(case, args)
        elif args.stage == "prepare":
            result = prepare(case, args.baseline_source.resolve() if args.baseline_source else native.REPO)
        elif args.stage == "checkpoint":
            result = checkpoint(case)
        elif args.stage == "integrate":
            result = integrate(case)
        else:
            args.model = native.managed_model(args.model, baseline=args.baseline_replay)
            need(args.codex and native.auth_ok(args.codex), "Existing ChatGPT login required")
            result = {"parallel": parallel, "resume": resume, "review": review}[args.stage](case, args)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "worktree-delivery-incomplete", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
