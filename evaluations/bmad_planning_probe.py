#!/usr/bin/env python3
"""Prepare and run one exploratory Codex planning case with pinned local routes."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import native_canary as native

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = {"bare-codex": None, "bmad-stable": "bmad-build-auto",
            "codex-agents-stable": "atelier-orchestrator"}
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


def prepare(base, bmad, use_git=True):
    base.mkdir(exist_ok=False)
    prompt = PROMPT if use_git else PROMPT.replace("committed", "pinned")
    case_input = {"prompt": prompt, "files": PROTECTED, "use_git": use_git}
    write_json(base / "input.json", case_input)
    for variant in VARIANTS:
        project = base / variant / "project"
        project.mkdir(parents=True, exist_ok=False)
        for ref, content in PROTECTED.items():
            write(project / ref, content)
        clean_git = {key: value for key, value in os.environ.items()
                     if not key.startswith("GIT_")}
        clean_git.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        if use_git:
            subprocess.run(["git", "init", "--quiet", "--template=", str(project)],
                           env=clean_git, check=True, timeout=10)
            subprocess.run(["git", "-C", str(project), "add", *PROTECTED], env=clean_git,
                           check=True, timeout=10)
            subprocess.run(["git", "-C", str(project), "-c", "core.hooksPath=" + os.devnull,
                            "-c", "user.name=Parity Fixture", "-c", "user.email=fixture@example.invalid",
                            "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "Planning fixture"],
                           env=clean_git, check=True, timeout=10)
        if variant == "bmad-stable":
            with (project.parent / "install.log").open("xb") as log:
                subprocess.run([str(bmad), "install", "--yes", "--modules", "bmm", "--tools",
                                "codex", "--directory", str(project), "--user-name", "Fixture",
                                "--communication-language", "English", "--document-output-language",
                                "English", "--no-shims"],
                               cwd=project, stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=45)
            skill = project / ".agents/skills/bmad-build-auto/SKILL.md"
            renderer = project / "_bmad/scripts/render_skill.py"
            if not skill.is_file() or not renderer.is_file():
                raise ValueError("installed BMad skill or renderer missing")
        if variant == "codex-agents-stable":
            source = ROOT / "optional-skills/atelier-orchestrator"
            destination = project / ".agents/skills/atelier-orchestrator"
            shutil.copytree(source, destination)
        if use_git:
            git_info = project / ".git/info"
            git_info.mkdir(exist_ok=True)
            with (git_info / "exclude").open("a", encoding="utf-8") as excludes:
                excludes.write("\n/.uv-tmp/\n/.uv-cache/\n/_bmad/render/\n")
            subprocess.run(["git", "-C", str(project), "add", "--all"], env=clean_git,
                           check=True, timeout=15)
            if subprocess.check_output(["git", "-C", str(project), "diff", "--cached", "--name-only"],
                                       env=clean_git, timeout=10):
                subprocess.run(["git", "-C", str(project), "-c", "core.hooksPath=" + os.devnull,
                                "-c", "user.name=Parity Fixture",
                                "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                                "commit", "--quiet", "-m", "Seal the workflow baseline"],
                               env=clean_git, check=True, timeout=15)
            if subprocess.check_output(["git", "-C", str(project), "status", "--porcelain",
                                        "--untracked-files=all"], env=clean_git, timeout=10):
                raise ValueError("fixture contains uncommitted workflow setup")
        elif (project / ".git").exists():
            raise ValueError("version-control-free fixture unexpectedly has Git metadata")
        pins = native.inspect_files(project)
        if any(pins.get(ref, [None])[0] != sha256(content.encode()).hexdigest()
               for ref, content in PROTECTED.items()):
            raise ValueError("protected fixture differs after setup")
        write_json(project.parent / "before.json", pins)
    return {"status": "prepared", "variants": list(VARIANTS), "input_sha256":
            sha256((base / "input.json").read_bytes()).hexdigest()}


def ready_specs(project):
    specs = []
    for path in sorted((project / "_bmad-output").rglob("*.md")):
        raw = path.read_bytes()
        lines = raw.decode("utf-8").splitlines()[:30]
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            continue
        end = lines.index("---", 1)
        statuses = [line.split(":", 1)[1].strip()
                    for line in lines[1:end] if line.startswith("status:")]
        if len(statuses) == 1 and statuses[0] in {
            "ready-for-dev", "'ready-for-dev'", '"ready-for-dev"'
        }:
            specs.append({"path": path.relative_to(project).as_posix(),
                          "sha256": sha256(raw).hexdigest()})
    return specs


def run_lane(base, variant, binary, model, effort, deadline, uv_dir=None):
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
    before = json.loads((lane / "before.json").read_text())
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
           "--json", "--ephemeral", "--disable", "apps", "--disable", "memories",
           "--disable", "hooks", "--disable", "plugins", "-c", 'web_search="disabled"',
           "-c", f'model_reasoning_effort="{effort}"',
           "-c", 'default_permissions="parity-probe"', "-c",
           policy,
           "--model", model, "-C", str(project)]
    if not use_git:
        cmd.append("--skip-git-repo-check")
    duplicates = sorted({path for skill in VARIANTS.values() if skill
                         for path in native.installed_conflicts(skill)})
    configured = ",".join("{path=" + json.dumps(path) + ",enabled=false}" for path in duplicates)
    cmd.extend(["-c", "skills.config=[" + configured + "]"])
    if uv_dir:
        (project / ".uv-tmp").mkdir(exist_ok=True)
        variables = {
            "PATH": str(uv_dir) + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin"),
            "UV_PYTHON": "/opt/homebrew/bin/python3.13", "UV_OFFLINE": "1",
            "UV_NO_MANAGED_PYTHON": "1", "UV_CACHE_DIR": str(project / ".uv-cache"),
            "TMPDIR": str(project / ".uv-tmp"),
        }
        table = ",".join(key + "=" + json.dumps(value) for key, value in variables.items())
        cmd.extend(["-c", "shell_environment_policy.set={" + table + "}"])
    skill = VARIANTS[variant]
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
    written_specs = ready_specs(project)
    result = {
        "git_fixture": use_git,
        "case_input_sha256": sha256(case_input).hexdigest(),
        "installed_route_inventory_sha256": sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
        "variant": variant, "model_requested": model, "effort": effort, "exit_code": code,
        "threads": ids, "completed_turns": len(turns),
        "native_skill_source_path_observed": (any(skill + "/SKILL.md" in line for line in observed_paths)
                                     if skill else None),
        "successful_render_command_observed": (any("render_skill.py" in line for line in observed_paths)
                                               if variant == "bmad-stable" else None),
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
    if messages:
        write(lane / "final-plan.md", messages[-1] + "\n")
    write_json(lane / "observation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "run"))
    parser.add_argument("--case-dir", type=Path, required=True)
    parser.add_argument("--bmad", type=Path)
    parser.add_argument("--no-vcs", action="store_true", help="prepare a case without Git")
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--effort", choices=("low", "medium"), default="low")
    parser.add_argument("--deadline", type=int, default=90)
    parser.add_argument("--uv-dir", type=Path)
    args = parser.parse_args()
    base = args.case_dir.resolve()
    if args.operation == "prepare":
        if args.bmad is None:
            parser.error("prepare needs the verified BMad executable")
        result = prepare(base, args.bmad.resolve(), not args.no_vcs)
    else:
        if not args.variant or not args.codex or not 1 <= args.deadline <= 120:
            parser.error("run needs a variant, Codex executable and deadline 1–120 seconds")
        result = run_lane(base, args.variant, args.codex, args.model, args.effort,
                          args.deadline, args.uv_dir)
    print(json.dumps(result, ensure_ascii=False))
    return int(args.operation == "run" and result["exit_code"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
