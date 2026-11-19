#!/usr/bin/env python3
"""Prepare and run one exploratory Codex planning case with pinned local routes."""

import argparse
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import time

import native_canary as native

ROOT = Path(__file__).resolve().parents[1]
LOCAL_SKILL = "atelier-orchestrator"
DEFAULT_VARIANTS = ("bare-codex", "product-baseline", "candidate")
VARIANTS = (*DEFAULT_VARIANTS, "reference")
REFERENCE_SCHEMA = "atelier.planning-reference/1"
NAME = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
PROTECTED = {
    "src/labels.py": """def unique_labels(labels: list[str]) -> list[str]:
    seen = set()
    result = []
    for label in labels:
        value = label.strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
""",
    "docs/compatibility.md": """# Compatibility rules

Preserve the first nonblank trimmed spelling and the original order.
Keep the public signature, do not mutate the caller's list, and introduce no dependency.
The label exporter reads this function without any normalization of its own.
""",
}
PROMPT = """Plan a one-file fix for case-insensitive deduplication in unique_labels.
Read src/labels.py and docs/compatibility.md. Keep the committed compatibility rules.
Describe the change, concrete input/expected output checks including whitespace and a Unicode
case-folding example, and what stays out of scope. Keep product files unchanged.
Halt after planning. Return the actionable plan in the final response.
Use only this disposable checkout and the workflow installed here. External skill folders
are outside the case scope.
"""


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        out.write(content)


def write_json(path, obj):
    write(path, json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def inventory_digest(inventory):
    return sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest()


def artifact_directory(value):
    if not isinstance(value, str) or len(value) > 300 or not all(
        NAME.fullmatch(part) for part in value.split("/")
    ):
        raise ValueError("artifact directory must be a project-relative path of directory names")
    return value


def reviewed_reference(path):
    config = native.load_json(path)
    required = {"schema", "source", "source_sha256", "skill"}
    optional = {"artifact_directory", "ready_status", "observed_command"}
    if not isinstance(config, dict) or not required <= set(config) <= required | optional:
        raise ValueError("invalid reference route fields")
    if config.pop("schema") != REFERENCE_SCHEMA:
        raise ValueError("unsupported reference route schema")
    source_path = config.pop("source")
    if not isinstance(source_path, str) or not 1 <= len(source_path) <= 4096:
        raise ValueError("invalid reference source directory")
    source = Path(source_path)
    if not source.is_absolute() or source != source.resolve():
        raise ValueError("reference source must be a canonical absolute directory")
    expected = config["source_sha256"]
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("reference route requires a reviewed inventory SHA-256")
    if "ready_status" in config and "artifact_directory" not in config:
        raise ValueError("ready status needs an artifact directory")
    if "artifact_directory" in config:
        artifact_directory(config["artifact_directory"])
        status = config.setdefault("ready_status", "ready-for-dev")
        if not isinstance(status, str) or not NAME.fullmatch(status):
            raise ValueError("invalid artifact status")
    if "observed_command" in config:
        command = config["observed_command"]
        if not isinstance(command, str) or not 1 <= len(command) <= 256 or any(ord(c) < 32 for c in command):
            raise ValueError("invalid observed command text")
    return source, config


def stage_route(project, source, route):
    if source is None:
        return
    name = route.get("skill")
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("invalid route skill name")
    if not source.is_dir() or source.is_symlink():
        raise ValueError("route source is unavailable")
    if project.is_relative_to(source):
        raise ValueError("route source must be outside the disposable project")
    before = native.inspect_files(source)
    verified = inventory_digest(before)
    if route.get("source_sha256", verified) != verified:
        raise ValueError("route source inventory differs from the reviewed digest")
    skill = source / "SKILL.md"
    lines = skill.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("route skill metadata missing")
    end = lines.index("---", 1)
    names = [line.split(":", 1)[1].strip().strip(chr(34) + chr(39))
             for line in lines[1:end] if line.startswith("name:")]
    if names != [name]:
        raise ValueError("route skill identity differs from the reviewed entry")
    _, staged = native.pin_skill(project, name, source)
    if inventory_digest(staged) != verified:
        raise ValueError("route source changed during setup")
    route["source_sha256"] = verified


def prepare(base, baseline, candidate, use_git=True, reference=None):
    base.mkdir(exist_ok=False)
    prompt = PROMPT if use_git else PROMPT.replace("committed", "pinned")
    case_input = {"prompt": prompt, "files": PROTECTED, "use_git": use_git}
    write_json(base / "input.json", case_input)
    routes = {
        "bare-codex": (None, {"skill": None, "source_sha256": inventory_digest({})}),
        "product-baseline": (baseline, {"skill": LOCAL_SKILL}),
        "candidate": (candidate, {"skill": LOCAL_SKILL}),
    }
    if reference:
        routes["reference"] = reviewed_reference(reference)
    for variant, (source, route) in routes.items():
        project = base / variant / "project"
        project.mkdir(parents=True, exist_ok=False)
        for ref, content in PROTECTED.items():
            write(project / ref, content)
        stage_route(project, source, route)
        if use_git:
            clean_git = {key: value for key, value in os.environ.items()
                         if not key.startswith("GIT_")}
            clean_git.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
            subprocess.run(["git", "init", "--quiet", "--template=", str(project)],
                           env=clean_git, check=True, timeout=10)
            subprocess.run(["git", "-C", str(project), "add", "--all"], env=clean_git,
                           check=True, timeout=15)
            subprocess.run(["git", "-C", str(project), "-c", "core.hooksPath=" + os.devnull,
                            "-c", "user.name=Planning Fixture", "-c", "user.email=fixture@example.invalid",
                            "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Seal the planning fixture"],
                           env=clean_git, check=True, timeout=15)
            if subprocess.check_output(["git", "-C", str(project), "status", "--porcelain",
                                        "--untracked-files=all"], env=clean_git, timeout=10):
                raise ValueError("fixture contains uncommitted workflow setup")
        pins = native.inspect_files(project)
        if any(pins.get(ref, [None])[0] != sha256(content.encode()).hexdigest()
               for ref, content in PROTECTED.items()):
            raise ValueError("protected fixture differs after setup")
        write_json(project.parent / "before.json", pins)
        write_json(project.parent / "route.json", route)
    return {"status": "prepared", "variants": list(routes),
            "input_sha256": sha256((base / "input.json").read_bytes()).hexdigest(),
            "route_sha256": {variant: sha256((base / variant / "route.json").read_bytes()).hexdigest()
                             for variant in routes}}


def ready_specs(project, directory, status):
    specs = []
    output = native.safe_path(project, artifact_directory(directory))
    for path in sorted(output.rglob("*.md")):
        ref = path.relative_to(project).as_posix()
        path = native.safe_path(project, ref)
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError("planning artifact must be a bounded regular file")
        raw = path.read_bytes()
        lines = raw.decode("utf-8").splitlines()[:30]
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            continue
        end = lines.index("---", 1)
        statuses = [line.split(":", 1)[1].strip()
                    for line in lines[1:end] if line.startswith("status:")]
        if len(statuses) == 1 and statuses[0] in {status, repr(status), json.dumps(status)}:
            specs.append({"path": ref, "sha256": sha256(raw).hexdigest()})
    return specs


def run_lane(base, variant, binary, model, effort, deadline, persist_model_receipt=False):
    case_input = (base / "input.json").read_bytes()
    declared = json.loads(case_input)
    use_git = declared.get("use_git")
    prompt_body = PROMPT if use_git is True else PROMPT.replace("committed", "pinned")
    if type(use_git) is not bool or declared != {
        "prompt": prompt_body, "files": PROTECTED, "use_git": use_git
    }:
        raise ValueError("frozen task input differs")
    lane = base / variant
    project = lane / "project"
    before = native.load_json(lane / "before.json")
    route_raw = (lane / "route.json").read_bytes()
    route = native.load_json(lane / "route.json")
    skill = route.get("skill")
    if variant == "bare-codex":
        if skill is not None or inventory_digest({}) != route.get("source_sha256"):
            raise ValueError("bare route changed")
    else:
        if not isinstance(skill, str) or not NAME.fullmatch(skill):
            raise ValueError("invalid staged route skill")
        if variant in {"product-baseline", "candidate"} and skill != LOCAL_SKILL:
            raise ValueError("product route identity differs")
        staged = native.safe_path(project, f".agents/skills/{skill}")
        if not staged.is_dir() or inventory_digest(native.inspect_files(staged)) != route.get("source_sha256"):
            raise ValueError("staged route changed")

    if (project / ".git").exists() != use_git:
        raise ValueError("fixture version-control mode differs")
    if native.inspect_files(project) != before:
        raise ValueError("lane changed after setup")
    ambient = (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
               Path("/etc/codex/skills"), Path("/etc/agents/skills"))
    denied = sorted({str(path.resolve()) for path in ambient if path.is_dir()})
    filesystem = [':slash_tmp', ':tmpdir']
    rules = [json.dumps(name) + '="read"' for name in filesystem]
    rules.extend(json.dumps(name) + '="none"' for name in denied)
    policy = ('permissions={parity-probe={extends=":workspace",filesystem={'
              + ",".join(rules) + '},network={enabled=false}}}')
    cmd = [binary, "-a", "never", "exec", "--ignore-user-config", "--strict-config",
           "--json", "--disable", "apps", "--disable", "memories",
           "--disable", "hooks", "--disable", "plugins", "-c", 'web_search="disabled"',
           "-c", f'model_reasoning_effort="{effort}"',
           "-c", 'default_permissions="parity-probe"', "-c",
           policy,
           "--model", model, "-C", str(project)]
    if not persist_model_receipt:
        cmd.append("--ephemeral")
    if not use_git:
        cmd.append("--skip-git-repo-check")
    duplicates = native.installed_conflicts(skill) if skill else []
    configured = ",".join("{path=" + json.dumps(path) + ",enabled=false}" for path in duplicates)
    cmd.extend(["-c", "skills.config=[" + configured + "]"])
    prompt = ("$" + skill + "\n" if skill else "") + prompt_body
    started = time.monotonic()
    with (lane / "events.jsonl").open("xb") as out, (lane / "diagnostics.log").open("xb") as err:
        code = native.run_native([*cmd, "-"], prompt.encode(), out, err, deadline)
    wall_ms = round((time.monotonic() - started) * 1000)
    rows = native.rows(lane / "events.jsonl")
    turns = [row for row in rows if row.get("type") == "turn.completed"]
    ids = [row["thread_id"] for row in rows if row.get("type") == "thread.started"]
    trace = native.observed_commands(rows)
    observed_paths = [item.get("command", "") for item in trace if item.get("exit_code") == 0]
    messages = [row["item"]["text"] for row in rows if row.get("type") == "item.completed"
                and row.get("item", {}).get("type") == "agent_message"]
    after = native.inspect_files(project)
    written_specs = (ready_specs(project, route["artifact_directory"], route["ready_status"])
                     if "artifact_directory" in route else [])
    result = {
        "git_fixture": use_git,
        "case_input_sha256": sha256(case_input).hexdigest(),
        "installed_route_inventory_sha256": sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
        "variant": variant, "model_requested": model, "effort": effort, "exit_code": code,
        "threads": ids, "completed_turns": len(turns),
        "persisted": persist_model_receipt,
        "model_receipt": native.native_turn_receipt(ids[0]) if persist_model_receipt and len(ids) == 1 else None,
        "native_skill_source_path_observed": (any(skill + "/SKILL.md" in line for line in observed_paths)
                                     if skill else None),
        "reviewed_command_observed": (any(route["observed_command"] in line for line in observed_paths)
                                      if "observed_command" in route else None),
        "route_sha256": sha256(route_raw).hexdigest(),
        "route_source_sha256": route["source_sha256"],
        "ambient_skill_command_observed": any(name in command for name in denied
                                              for command in observed_paths),
        "protected_files_unchanged": all(before.get(ref) == after.get(ref) for ref in PROTECTED),
        "changed": sorted(ref for ref in set(before) | set(after)
                          if before.get(ref) != after.get(ref)),
        "wall_ms": wall_ms, "usage": turns[0].get("usage") if len(turns) == 1 else None,
        "raw_trace_sha256": sha256((lane / "events.jsonl").read_bytes()).hexdigest(),
        "written_ready_specs": written_specs,
        "artifact_status": "pending_independent_review",
    }
    result["matches_requested_model"] = native.matches_model(result["model_receipt"], model, effort)
    if messages:
        write(lane / "final-plan.md", messages[-1] + "\n")
    write_json(lane / "observation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "run"))
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--baseline-source", type=Path,
                        help="reviewed released Orchestrator source directory")
    parser.add_argument("--candidate-source", type=Path,
                        default=ROOT / "optional-skills/atelier-orchestrator")
    parser.add_argument("--reference-config", type=Path, help="optional reviewed local reference route")
    parser.add_argument("--no-vcs", action="store_true", help="prepare a case without Git")
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--model", help="Alternate model pin for the explicit product-baseline lane")
    parser.add_argument("--effort", choices=("low", "medium", "high"), default=native.DEFAULT_EFFORT)
    parser.add_argument("--deadline", type=int, default=90)
    parser.add_argument("--persist-model-receipt", action="store_true",
                        help="Allow a disposable native rollout for exact model readback")
    args = parser.parse_args()
    base = args.case_dir.resolve()
    if args.operation == "prepare":
        if args.baseline_source is None:
            parser.error("prepare needs a reviewed released Orchestrator source")
        result = prepare(base, args.baseline_source.resolve(), args.candidate_source.resolve(),
                         not args.no_vcs, args.reference_config)
    else:
        if not args.variant or not args.codex or not 1 <= args.deadline <= 120:
            parser.error("run needs a variant, Codex executable and deadline 1–120 seconds")
        if args.baseline_source is not None or args.reference_config is not None or args.no_vcs:
            parser.error("set the source and Git mode while preparing the case")
        if not (base / args.variant / "route.json").is_file():
            parser.error("the requested variant is absent from the prepared case")
        try:
            model = native.managed_model(args.model, baseline=args.variant == "product-baseline")
        except ValueError as exc:
            parser.error(str(exc))
        if not native.auth_ok(args.codex):
            parser.error("Native planning probe requires an existing authenticated ChatGPT session")
        result = run_lane(base, args.variant, args.codex, model, args.effort,
                          args.deadline, args.persist_model_receipt)
    print(json.dumps(result, ensure_ascii=False))
    return int(args.operation == "run" and (
        result["exit_code"] != 0 or result["completed_turns"] != 1
        or (args.persist_model_receipt and not result["matches_requested_model"])
    ))


if __name__ == "__main__":
    raise SystemExit(main())
