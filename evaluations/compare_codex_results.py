#!/usr/bin/env python3
"""Compare the evidence from one frozen Codex case across four variants.

This reads local files only. The case binds input and scope files by SHA-256.
Each run binds a native JSONL trace and adjudication artifacts. Matching evidence
does not authenticate the records' origin, actor independence, or task quality.
Exit 0 means the comparison is complete, including failed variants. Exit 1
means evidence is incomplete, and exit 2 means the case or CLI input is invalid.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
from uuid import UUID

CASE_SCHEMA = "atelier.codex-comparison/1"
RUN_SCHEMA = "atelier.codex-comparison-run/1"
RESULT_SCHEMA = "atelier.codex-comparison-result/1"
VARIANTS = ("bare-codex", "bmad-stable", "codex-agents-stable", "candidate")
BUDGET_KEYS = {"max_wall_ms", "max_input_tokens", "max_output_tokens"}
USAGE_KEYS = {"input_tokens", "cached_input_tokens", "output_tokens"}
CASE_KEYS = {
    "schema", "case_id", "input", "scope_profile", "model", "effort", "budget",
    "required_checks", "variants", "observers", "reviewers",
}
RUN_KEYS = {
    "schema", "case_sha256", "case_id", "variant", "input_sha256", "source_sha256",
    "scope_sha256", "model", "effort", "budget", "observer", "reviewer",
    "native", "metrics", "checks",
}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,79}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RECORD_LIMIT = 256 * 1024
EVIDENCE_LIMIT = 8 * 1024 * 1024
TOTAL_LIMIT = 64 * 1024 * 1024


def check(condition, message):
    if not condition:
        raise ValueError(message)


def object_keys(value, keys, label):
    check(isinstance(value, dict) and set(value) == keys, f"{label} has unexpected fields")
    return value


def integer(value, label):
    check(type(value) is int and value >= 0, f"{label} must be a nonnegative integer")
    return value


def identifier(value, label):
    check(isinstance(value, str) and ID.fullmatch(value), f"invalid {label}")
    return value


def digest(value, label):
    check(isinstance(value, str) and SHA256.fullmatch(value), f"invalid {label} SHA-256")
    return value


def unique_ids(values, label):
    check(isinstance(values, list) and 1 <= len(values) <= 64,
          f"{label} needs 1 to 64 entries")
    ids = [identifier(value, label) for value in values]
    check(len(ids) == len(set(ids)), f"{label} contains duplicate IDs")
    return ids


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(_value):
    raise ValueError("non-finite JSON number")


def json_object(raw):
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                            parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ValueError("invalid JSON object") from error
    check(isinstance(result, dict), "expected a JSON object")
    return result


class Evidence:
    def __init__(self, root):
        check(root.is_absolute() and root.is_dir() and root == root.resolve(),
              "use a canonical absolute evidence root")
        self.root = root
        self.remaining = TOTAL_LIMIT

    def read(self, ref, limit):
        check(isinstance(ref, str) and 0 < len(ref) <= 1024
              and ":" not in ref and "\\" not in ref and "\x00" not in ref,
              "invalid evidence path")
        parts = ref.split("/")
        check(all(part not in ("", ".", "..", ".git") for part in parts),
              "evidence path must stay within the evidence root")
        path = self.root
        for part in parts:
            path /= part
            check(not path.is_symlink(), "symlink is out of evidence scope")
        limit = min(limit, self.remaining)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            check(stat.S_ISREG(info.st_mode), "evidence must be a regular file")
            check(info.st_size <= limit, "evidence exceeds the read budget")
            raw = stream.read(limit + 1)
        check(len(raw) <= limit, "evidence exceeds the read budget")
        self.remaining -= len(raw)
        return raw

    def verify(self, value, *, read=False):
        ref = object_keys(value, {"path", "sha256"}, "evidence reference")
        expected = digest(ref["sha256"], "evidence reference")
        path = ref["path"]
        check(isinstance(path, str), "invalid evidence path")
        raw = self.read(path, EVIDENCE_LIMIT)
        check(sha256(raw).hexdigest() == expected, "evidence SHA-256 differs")
        return raw if read else None


def read_case(evidence, path):
    raw = evidence.read(path, RECORD_LIMIT)
    case = object_keys(json_object(raw), CASE_KEYS, "case")
    check(case["schema"] == CASE_SCHEMA, "unsupported comparison schema")
    identifier(case["case_id"], "case ID")
    identifier(case["model"], "model")
    identifier(case["effort"], "effort")
    budget = object_keys(case["budget"], BUDGET_KEYS, "budget")
    for key, value in budget.items():
        check(integer(value, key) > 0, f"{key} must be positive")
    unique_ids(case["required_checks"], "required checks")
    unique_ids(case["observers"], "observers")
    unique_ids(case["reviewers"], "reviewers")
    object_keys(case["variants"], set(VARIANTS), "variants")
    for value in case["variants"].values():
        digest(value, "variant source")
    evidence.verify(case["input"])
    evidence.verify(case["scope_profile"])
    return case, sha256(raw).hexdigest()


def usage(value):
    check(isinstance(value, dict) and USAGE_KEYS <= set(value), "missing usage counters")
    counts = {key: integer(value[key], key) for key in sorted(USAGE_KEYS)}
    check(counts["cached_input_tokens"] <= counts["input_tokens"],
          "cached tokens exceed input tokens")
    return counts


def native_facts(evidence, declaration):
    declaration = object_keys(declaration, {"thread_id", "terminal", "trace"}, "native")
    thread = identifier(declaration["thread_id"], "thread ID")
    check(str(UUID(thread)) == thread, "expected a canonical native thread UUID")
    state = declaration["terminal"]
    check(state in ("completed", "failed", "interrupted"), "invalid native terminal")
    trace = evidence.verify(declaration["trace"], read=True)
    threads = []
    terminals = []
    for number, line in enumerate(trace.splitlines(), 1):
        if not line.strip():
            continue
        event = json_object(line)
        if event.get("type") == "thread.started":
            threads.append((number, event.get("thread_id")))
        if event.get("type") in ("turn.completed", "turn.failed"):
            terminals.append((number, event))
    check(len(threads) == 1 and threads[0][1] == thread,
          "native trace does not contain exactly one matching thread start")
    if state == "interrupted":
        check(not terminals, "interrupted run has a terminal event")
        return thread, state, None
    check(len(terminals) == 1 and terminals[0][0] > threads[0][0]
          and terminals[0][1]["type"] == f"turn.{state}",
          "native trace does not contain exactly one matching terminal event")
    payload = terminals[0][1].get("usage")
    if state == "failed" and payload is None:
        return thread, state, None
    return thread, state, usage(payload)


def verify_requirements(evidence, requirements, adjudications):
    check(isinstance(adjudications, dict) and set(adjudications) <= set(requirements),
          "adjudications contain unknown check IDs")
    results = {}
    for name in requirements:
        entry = adjudications.get(name)
        if entry is None:
            results[name] = {"status": "unverified", "reason": "check missing"}
            continue
        try:
            entry = object_keys(entry, {"status", "evidence"}, f"check {name}")
            reported = entry["status"]
            check(reported in ("pass", "fail", "unverified"), "invalid reported check status")
            refs = entry["evidence"]
            check(isinstance(refs, list) and len(refs) <= 8, "invalid check evidence list")
            if reported != "unverified":
                check(bool(refs), "adjudicated check needs evidence")
            for ref in refs:
                evidence.verify(ref)
        except (OSError, ValueError) as error:
            results[name] = {"status": "unverified", "reason": str(error)}
            if isinstance(entry, dict) and entry.get("status") in ("pass", "fail"):
                results[name]["reported_status"] = entry["status"]
        else:
            results[name] = {"status": reported}
    return results


def assess_run(evidence, case, case_sha, variant, path):
    if path is None:
        return {"status": "incomplete", "issues": ["receipt missing"]}
    result = {"status": "incomplete", "issues": []}
    try:
        receipt = object_keys(json_object(evidence.read(path, RECORD_LIMIT)), RUN_KEYS, "run")
        expected = {
            "schema": RUN_SCHEMA, "case_sha256": case_sha, "case_id": case["case_id"],
            "variant": variant, "input_sha256": case["input"]["sha256"],
            "scope_sha256": case["scope_profile"]["sha256"],
            "source_sha256": case["variants"][variant],
            "model": case["model"], "effort": case["effort"], "budget": case["budget"],
        }
        for key, value in expected.items():
            check(type(receipt[key]) is type(value) and receipt[key] == value,
                  f"run {key} differs from frozen case")
        for key, value in receipt["budget"].items():
            integer(value, key)
        check(receipt["observer"] in case["observers"], "observer is not registered")
        check(receipt["reviewer"] in case["reviewers"], "reviewer is not registered")
        check(receipt["observer"] != receipt["reviewer"], "observer and reviewer IDs coincide")
        thread, state, observed = native_facts(evidence, receipt["native"])
        metrics = object_keys(receipt["metrics"], {"wall_ms", "usage"}, "metrics")
        wall = integer(metrics["wall_ms"], "wall milliseconds")
        declared_usage = metrics["usage"]
        if declared_usage is not None:
            object_keys(declared_usage, USAGE_KEYS, "declared usage")
            declared_usage = usage(declared_usage)
        check(declared_usage == observed, "reported usage differs from native trace")
        result.update(thread_id=thread, terminal=state, observer=receipt["observer"],
                      reviewer=receipt["reviewer"], observer_wall_ms=wall,
                      trace_usage=observed)
        checks = verify_requirements(evidence, case["required_checks"], receipt["checks"])
        result["checks"] = checks
    except (OSError, ValueError) as error:
        result["issues"].append(str(error))
        return result
    failures = []
    if state == "failed":
        failures.append("native turn failed")
    if wall > case["budget"]["max_wall_ms"]:
        failures.append("wall budget exceeded")
    if observed is not None:
        for key in ("input_tokens", "output_tokens"):
            if observed[key] > case["budget"][f"max_{key}"]:
                failures.append(f"{key} budget exceeded")
    failures.extend(f"check {key} failed" for key, row in checks.items()
                    if row["status"] == "fail")
    result["failures"] = failures
    if state == "interrupted":
        result["issues"].append("native turn has no observed terminal event")
    if any(row["status"] == "unverified" for row in checks.values()):
        result["issues"].append("one or more required checks are unverified")
    if not result["issues"]:
        result["status"] = "failed" if failures else "passed"
    return result


def compare(root, case_path, receipt_paths):
    evidence = Evidence(root)
    case, case_sha = read_case(evidence, case_path)
    runs = {variant: assess_run(evidence, case, case_sha, variant, receipt_paths.get(variant))
            for variant in VARIANTS}
    thread_ids = [row["thread_id"] for row in runs.values() if "thread_id" in row]
    for row in runs.values():
        if "thread_id" in row and thread_ids.count(row["thread_id"]) > 1:
            row["status"] = "incomplete"
            row["issues"].append("native thread reused across variants")
    complete = all(row["status"] != "incomplete" for row in runs.values())
    return {
        "schema": RESULT_SCHEMA,
        "case_id": case["case_id"],
        "case_sha256": case_sha,
        "comparison_status": "complete" if complete else "incomplete",
        "native_origin_authenticated": False,
        "reviewer_independence_authenticated": False,
        "runs": runs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--root", type=Path, required=True, help="canonical evidence directory")
    parser.add_argument("--case", required=True, help="frozen case path relative to --root")
    parser.add_argument("--receipt", action="append", default=[], metavar="VARIANT=PATH",
                        help="run receipt path relative to --root; repeat once per variant")
    args = parser.parse_args()
    receipt_paths = {}
    try:
        for item in args.receipt:
            variant, separator, path = item.partition("=")
            check(variant in VARIANTS and separator and path and variant not in receipt_paths,
                  "each receipt needs a known and distinct VARIANT=PATH")
            receipt_paths[variant] = path
        result = compare(args.root, args.case, receipt_paths)
    except (OSError, ValueError) as error:
        print(json.dumps({"schema": RESULT_SCHEMA, "comparison_status": "invalid",
                          "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["comparison_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
