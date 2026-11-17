#!/usr/bin/env python3
"""Bind isolated Git worktrees and integrate reviewed, disjoint worker commits."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import ticket_handoff as handoff

context = handoff.context
BINDING = "atelier.ticket-worktree-binding/1"
PLAN = "atelier.ticket-worktree-integration/1"
OID = re.compile(r"(?:[a-f0-9]{40}|[a-f0-9]{64})")
LOCK = "atelier-ticket-worktree.lock"
REGULAR = {b"100644", b"100755"}
MAX_RECORD = 2 * 1024 * 1024
BINDING_FIELDS = {"schema_version", "root", "base", "worktree", "branch", "git_common_dir", "write_paths"}


def git(root, *args, data=None, extra_env=None, timeout=30):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
               GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
    if extra_env:
        env.update(extra_env)
    command = [
        "git", "--no-replace-objects", "--literal-pathspecs", "-C", str(root),
        "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
        "-c", "submodule.recurse=false", "-c", "commit.gpgSign=false",
        *args,
    ]
    try:
        result = subprocess.run(command, input=data, capture_output=True, env=env, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise context.ContextError(f"git {args[0]} outcome is unconfirmed: {error}") from error
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise context.ContextError(f"git {args[0]} failed: {message[:600]}")
    return result.stdout


def git_text(root, *args, **options):
    return git(root, *args, **options).decode("utf-8").rstrip("\n")


def absolute_path(value, label, *, existing=True):
    if not isinstance(value, (Path, str)):
        raise context.ContextError(f"{label} must be an absolute path")
    path = Path(value)
    context.require(path.is_absolute() and path.resolve() == path and
                    not any(ord(char) < 32 for char in str(path)),
                    f"{label} must be canonical and absolute")
    if existing:
        context.require(path.is_dir(), f"{label} is not a directory")
    return path


def expect_oid(value, label):
    context.require(isinstance(value, str) and OID.fullmatch(value), f"{label} must be a full commit ID")
    return value


def verify_commit(root, oid):
    expect_oid(oid, "commit")
    context.require(git_text(root, "rev-parse", "--verify", oid + "^{commit}") == oid,
                    "expected the commit object itself")
    return oid


def branch_name(root, branch):
    context.require(isinstance(branch, str) and branch.startswith("codex/"),
                    "expected a dedicated codex/ branch")
    git(root, "check-ref-format", "refs/heads/" + branch)
    return branch


def identity(root):
    root = absolute_path(root, "Git worktree")
    context.require(git_text(root, "rev-parse", "--show-toplevel") == str(root),
                    "target must be the root of its Git worktree")
    common = absolute_path(git_text(root, "rev-parse", "--path-format=absolute", "--git-common-dir"),
                           "Git common directory")
    head = expect_oid(git_text(root, "rev-parse", "--verify", "HEAD"), "HEAD")
    return common, head


def registered_worktrees(root):
    entries = []
    item = {}
    for line in git(root, "worktree", "list", "--porcelain", "-z").split(b"\0"):
        if not line:
            if item:
                entries.append(item)
                item = {}
            continue
        key, _, value = line.decode("utf-8").partition(" ")
        context.require(key not in item, "Git returned ambiguous worktree metadata")
        item[key] = value
    context.require(not item, "incomplete Git worktree inventory")
    return entries


def check_registered(root, target, branch, head):
    matches = [row for row in registered_worktrees(root) if row.get("worktree") == str(target)]
    context.require(len(matches) == 1 and matches[0].get("branch") == "refs/heads/" + branch
                    and matches[0].get("HEAD") == head and "prunable" not in matches[0]
                    and "bare" not in matches[0],
                    "worktree registration or active branch differs from the binding")


def clean_worktree(root):
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                 "--ignored=matching", "--ignore-submodules=none")
    context.require(not status, f"worktree is not clean: {root}")


def write_scope(root, paths):
    paths = context.string_list(paths, "write paths")
    context.require(1 <= len(paths) <= 24, "name 1 to 24 exact writable files")
    scope = []
    for ref in sorted(paths):
        context.require(not any(ord(char) < 32 for char in ref),
                        "control character in writable path")
        context.require(not any(handoff.overlaps(ref, prior) for prior in scope),
                        f"writable paths overlap or alias: {ref}")
        handoff.scoped_file(root, ref)
        scope.append(ref)
    return scope


@contextmanager
def repository_lock(common):
    path = common / LOCK
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600),
                   "w") as lock:
        info = os.fstat(lock.fileno())
        context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                        "invalid worktree lock file")
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise context.ContextError("another worktree operation holds the repository lock") from error
        yield


def distinct_paths(first, second):
    context.require(not handoff.overlaps(str(first), str(second)),
                    "worktrees must use separate, nonnested directories")


def make_binding(root, base, worktree, branch, write_paths, *, create=False):
    root = absolute_path(root, "coordinator")
    worktree = absolute_path(worktree, "worker worktree", existing=not create)
    distinct_paths(root, worktree)
    common, _ = identity(root)
    verify_commit(root, base)
    branch_name(root, branch)
    if create:
        with repository_lock(common):
            for row in registered_worktrees(root):
                distinct_paths(row["worktree"], worktree)
            context.require(worktree.parent.is_dir() and not worktree.exists() and not worktree.is_symlink(),
                            "worktree path must be absent under an existing directory")
            prepare_scope(root, base, write_paths)
            git(root, "worktree", "add", "-b", branch, "--", str(worktree), base)
    binding = {
        "schema_version": BINDING, "root": str(root), "base": base, "worktree": str(worktree),
        "branch": branch, "git_common_dir": str(common), "write_paths": write_scope(worktree, write_paths),
    }
    observed = check_binding(binding, require_clean=True)
    context.require(observed["head"] == base, "worker worktree did not start at the selected base")
    return binding


def prepare_scope(root, base, paths):
    paths = context.string_list(paths, "write paths")
    context.require(1 <= len(paths) <= 24, "name 1 to 24 exact writable files")
    # Use the committed tree to check ancestors without relying on the coordinator's dirty files.
    for index, ref in enumerate(paths):
        context.require(not any(handoff.overlaps(ref, prior) for prior in paths[:index]),
                        f"writable paths overlap or alias: {ref}")
        candidate = context.local(root, ref, existing=False)
        context.require(not any(ord(char) < 32 for char in ref), "control character in writable path")
        protected = context.PRIVATE_PARTS | {".agents", ".codex", "agents.md", ".ticket-dispatch.json",
                                             ".ticket-replan.lock"}
        context.require(not any(part.casefold() in protected or context.PRIVATE_NAME.fullmatch(part)
                                for part in candidate.relative_to(root).parts),
                        f"protected writable path: {ref}")
        parent = candidate.parent.relative_to(root).as_posix()
        if parent != ".":
            parents = tree_entries(root, base, [parent], recursive=False)
            context.require(parents.get(parent, (b"", b""))[0] == b"040000",
                            f"writable path has no existing directory in the selected tree: {ref}")
        entries = tree_entries(root, base, [ref], recursive=False)
        context.require(not entries or entries.get(ref, (b"", b""))[0] in REGULAR,
                        f"writable base entry must be a regular file: {ref}")
    return paths


def check_binding(binding, require_clean=False):
    context.require(isinstance(binding, dict) and set(binding) == BINDING_FIELDS
                    and binding["schema_version"] == BINDING, "invalid worktree binding")
    root = absolute_path(binding["root"], "coordinator")
    worktree = absolute_path(binding["worktree"], "worker worktree")
    distinct_paths(root, worktree)
    common, _ = identity(root)
    linked_common, head = identity(worktree)
    context.require(linked_common == common and str(common) == binding["git_common_dir"],
                    "worker does not share the bound Git metadata")
    verify_commit(root, binding["base"])
    branch = branch_name(root, binding["branch"])
    check_registered(root, worktree, branch, head)
    context.require(git_text(worktree, "symbolic-ref", "HEAD") == "refs/heads/" + branch,
                    "checked-out branch changed")
    context.require(write_scope(worktree, binding["write_paths"]) == binding["write_paths"],
                    "worktree binding paths are not canonical")
    if require_clean:
        clean_worktree(worktree)
    return {**binding, "head": head}


def load_record(path, digest):
    context.require(isinstance(digest, str) and context.HASH.fullmatch(digest),
                    "expected a SHA-256 record pin")
    path = Path(path)
    context.require(not path.is_symlink() and path.is_file() and path.stat().st_size <= MAX_RECORD,
                    "expected a bounded regular record file")
    raw = path.read_bytes()
    context.require(len(raw) <= MAX_RECORD and hashlib.sha256(raw).hexdigest() == digest,
                    "record SHA-256 changed")
    return context.json_object(raw)


def load_binding(path, digest):
    binding = load_record(path, digest)
    context.require(set(binding) == BINDING_FIELDS and binding["schema_version"] == BINDING,
                    "invalid worktree binding")
    return binding


def changed_paths(root, first, second):
    output = git(root, "diff-tree", "--no-commit-id", "--name-only", "--no-renames", "-r", "-z",
                 first, second, "--")
    return sorted(field.decode("utf-8") for field in output.split(b"\0") if field)


def tree_entries(root, tree, paths, *, recursive=True):
    depth = ["-r"] if recursive else []
    output = git(root, "ls-tree", "--full-tree", *depth, "-z", tree, "--", *paths)
    result = {}
    for raw in output.split(b"\0"):
        if raw:
            info, path = raw.split(b"\t", 1)
            mode, _, oid = info.split()
            result[path.decode("utf-8")] = (mode, oid)
    return result


def candidate(binding, commit):
    observed = check_binding(binding, require_clean=True)
    root = Path(binding["root"])
    verify_commit(root, commit)
    context.require(observed["head"] == commit, "worker branch advanced or differs from the reviewed commit")
    parents = git_text(root, "rev-list", "--parents", "-n", "1", commit).split()
    context.require(parents == [commit, binding["base"]],
                    "worker commit must directly follow the selected base")
    paths = changed_paths(root, binding["base"], commit)
    context.require(paths and set(paths) <= set(binding["write_paths"]),
                    "worker made no changes or changed files outside the approved scope")
    for tree in (binding["base"], commit):
        entries = tree_entries(root, tree, paths)
        context.require(set(entries) <= set(paths) and all(mode in REGULAR for mode, _ in entries.values()),
                        "worker changed a non-regular entry or crossed a directory boundary")
    return {"schema_version": "atelier.ticket-worktree-candidate/1", "binding": binding,
            "commit": commit, "changed_paths": paths}


def integration_identity(root, integration):
    root = absolute_path(root, "coordinator")
    integration = absolute_path(integration, "integration worktree")
    distinct_paths(root, integration)
    common, _ = identity(root)
    integration_common, head = identity(integration)
    context.require(integration_common == common, "integration worktree belongs to a different repository")
    ref = git_text(integration, "symbolic-ref", "HEAD")
    context.require(ref.startswith("refs/heads/"), "integration target must be a local branch")
    branch = branch_name(root, ref[len("refs/heads/"):])
    check_registered(root, integration, branch, head)
    clean_worktree(integration)
    return {"root": str(root), "worktree": str(integration), "branch": branch, "head": head,
            "git_common_dir": str(common)}


def assemble_tree(root, base, members):
    changed = sorted(path for member in members for path in member["changed_paths"])
    with tempfile.TemporaryDirectory(prefix="atelier-worktree-index-") as directory:
        env = {"GIT_INDEX_FILE": str(Path(directory) / "index")}
        git(root, "read-tree", base, extra_env=env)
        for member in members:
            patch = git(root, "diff", "--binary", "--no-ext-diff", "--no-textconv", "--no-color",
                        "--no-renames", "--src-prefix=a/", "--dst-prefix=b/", base, member["commit"], "--",
                        *member["changed_paths"])
            git(root, "apply", "--cached", "--whitespace=nowarn", "-", data=patch, extra_env=env)
        tree = expect_oid(git_text(root, "write-tree", extra_env=env), "integration tree")
    context.require(changed_paths(root, base, tree) == changed, "integration tree differs from the reviewed changes")
    for member in members:
        paths = member["changed_paths"]
        context.require(tree_entries(root, tree, paths) == tree_entries(root, member["commit"], paths),
                        "integration changed a reviewed worker's file bytes or mode")
    return tree, changed


def create_integration_commit(root, base, members, tree):
    timestamp = git_text(root, "show", "-s", "--format=%ct", base)
    context.require(timestamp.isdigit(), "selected base has an invalid commit timestamp")
    date = f"@{timestamp} +0000"
    env = {
        "GIT_AUTHOR_NAME": "Atelier integration", "GIT_AUTHOR_EMAIL": "atelier-integration@example.invalid",
        "GIT_COMMITTER_NAME": "Atelier integration", "GIT_COMMITTER_EMAIL": "atelier-integration@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    parents = [base, *(member["commit"] for member in members)]
    args = [arg for parent in parents for arg in ("-p", parent)]
    message = "Integrate reviewed worker commits\n\n" + "\n".join(parents[1:]) + "\n"
    return expect_oid(git_text(root, "commit-tree", tree, *args, data=message.encode(), extra_env=env),
                      "integration commit")


def build_plan(root, integration, pins):
    target = integration_identity(root, integration)
    context.require(2 <= len(pins) <= 8, "integration requires 2 to 8 reviewed workers")
    base = target["head"]
    workers = []
    all_scope = []
    for path, digest, commit in pins:
        path = Path(path).resolve()
        binding = load_binding(path, digest)
        context.require(binding["root"] == str(root) and binding["base"] == base,
                        "worker was prepared for a different coordinator or base")
        distinct_paths(binding["worktree"], integration)
        for prior in workers:
            distinct_paths(binding["worktree"], prior["binding"]["worktree"])
        for scope in binding["write_paths"]:
            context.require(not any(handoff.overlaps(scope, rel) for rel in all_scope),
                            f"workers have overlapping writable paths: {scope}")
        result = candidate(binding, commit)
        workers.append({**result, "binding_pin": {"path": str(path), "sha256": digest}})
        all_scope.extend(binding["write_paths"])
    context.require(len({row["commit"] for row in workers}) == len(workers),
                    "each worker must return a distinct commit")
    tree, paths = assemble_tree(root, base, workers)
    commit = create_integration_commit(root, base, workers, tree)
    context.require(integration_identity(root, integration) == target, "integration target drifted during review")
    return {"schema_version": PLAN, "target": target, "workers": workers,
            "tree": tree, "commit": commit, "changed_paths": paths}


def check_merge_object(root, plan):
    # Replay uses the existing commit object and retained plan, including the worker parents.
    expected_parents = [plan["commit"], plan["target"]["head"],
                        *(member["commit"] for member in plan["workers"])]
    for parent in expected_parents:
        verify_commit(root, parent)
    context.require(git_text(root, "rev-list", "--parents", "-n", "1", plan["commit"]).split() == expected_parents,
                    "stored integration commit has different parents")
    context.require(git_text(root, "rev-parse", plan["commit"] + "^{tree}") == plan["tree"],
                    "stored integration commit has a different tree")
    context.require(changed_paths(root, plan["target"]["head"], plan["commit"]) == plan["changed_paths"],
                    "stored integration commit changed unexpected paths")


def apply_plan(plan_path, digest):
    plan = load_record(plan_path, digest)
    context.require(set(plan) == {"schema_version", "target", "workers", "tree", "commit", "changed_paths"}
                    and plan["schema_version"] == PLAN, "invalid integration plan")
    target = plan["target"]
    root = absolute_path(target["root"], "coordinator")
    integration = absolute_path(target["worktree"], "integration worktree")
    common, _ = identity(root)
    with repository_lock(common):
        live = integration_identity(root, integration)
        context.require(all(live[key] == target[key] for key in live if key != "head"),
                        "integration worktree identity changed")
        check_merge_object(root, plan)
        if live["head"] == plan["commit"]:
            status = "already-integrated"
        else:
            context.require(live == target, "integration branch advanced since review")
            pins = [(row["binding_pin"]["path"], row["binding_pin"]["sha256"], row["commit"])
                    for row in plan["workers"]]
            context.require(build_plan(root, integration, pins) == plan,
                            "worker bindings or reviewed integration changed")
            # Git performs the checkout and branch update in the dedicated worktree.
            git(integration, "merge", "--ff-only", "--no-overwrite-ignore", plan["commit"])
            status = "integrated"
        observed = integration_identity(root, integration)
        context.require(observed == {**target, "head": plan["commit"]}, "integration read-back differs")
        return {"schema_version": "atelier.ticket-worktree-receipt/1", "status": status,
                "head": observed["head"], "tree": plan["tree"], "target": observed,
                "changed_paths": plan["changed_paths"], "plan_sha256": digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "bind"):
        mode = commands.add_parser(name)
        mode.add_argument("--root", type=Path, required=True)
        mode.add_argument("--base", required=True)
        mode.add_argument("--worktree", type=Path, required=True)
        mode.add_argument("--branch", required=True)
        mode.add_argument("--write-path", action="append", required=True)
    mode = commands.add_parser("candidate")
    mode.add_argument("--binding", type=Path, required=True)
    mode.add_argument("--binding-sha256", required=True)
    mode.add_argument("--commit", required=True)
    mode = commands.add_parser("plan")
    mode.add_argument("--root", type=Path, required=True)
    mode.add_argument("--integration", type=Path, required=True)
    mode.add_argument("--binding", type=Path, action="append", required=True)
    mode.add_argument("--binding-sha256", action="append", required=True)
    mode.add_argument("--commit", action="append", required=True)
    mode = commands.add_parser("apply")
    mode.add_argument("--plan", type=Path, required=True)
    mode.add_argument("--plan-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command in {"prepare", "bind"}:
            result = make_binding(args.root, args.base, args.worktree, args.branch, args.write_path,
                                  create=args.command == "prepare")
        elif args.command == "candidate":
            result = candidate(load_binding(args.binding, args.binding_sha256), args.commit)
        elif args.command == "plan":
            context.require(len(args.binding) == len(args.binding_sha256) == len(args.commit),
                            "each worker requires one binding, digest and commit")
            result = build_plan(args.root, args.integration, list(zip(args.binding, args.binding_sha256,
                                                                     args.commit)))
        else:
            result = apply_plan(args.plan, args.plan_sha256)
    except (context.ContextError, OSError, UnicodeError, TypeError, KeyError, ValueError) as error:
        print(json.dumps({"status": "invalid-worktree-operation", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
