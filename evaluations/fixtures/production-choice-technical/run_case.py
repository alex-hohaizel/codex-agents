"""Run the technical production-choice slice under a disposable local directory."""

import argparse
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time


FIXTURE = Path(__file__).resolve().parent
DEFAULT_ENGINE = FIXTURE.parents[2] / "standards/production_choices.py"
AUTHOR = "/root/choice_contract"
REQUIREMENTS = ("R-LOCAL", "R-ONCE", "R-ACCESS", "R-FAIL", "R-RESTORE", "R-MAINTAIN")
DOCUMENTED_CHECK_DATE = date(2026, 11, 20)


def check(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=True, indent=2) + "\n",
                    encoding="utf-8")


def pin(root, relative):
    raw = (root / relative).read_bytes()
    return {"path": str(relative), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def invoke(script, args, cwd, expected=0):
    result = subprocess.run([sys.executable, "-B", str(script), *map(str, args)], cwd=cwd,
                            check=False, capture_output=True, text=True, timeout=10)
    check(result.returncode == expected,
          f"{script.name} {args}: wanted {expected}, got {result.returncode}: {result.stdout or result.stderr}")
    return {"operation": list(map(str, args)), "exit": result.returncode,
            "result": json.loads(result.stdout)}


def populate(root):
    for name in ("review_queue.py", "architecture.md", "requirements.md", "README.md"):
        shutil.copyfile(FIXTURE / name, root / name)
    write(root / "submit.json", {
        "action": "submit", "event": "delivery-one", "request": "request-one", "title": "Review local evidence",
    })
    write(root / "conflict.json", {**read(root / "submit.json"), "title": "Different payload"})
    write(root / "approve.json", {"action": "approve", "event": "review-one", "request": "request-one"})


def queue(root, label):
    db = f"{label}.sqlite"
    script = root / "review_queue.py"
    observations = []

    def call(operation, *extra, expected=0, database=db):
        result = invoke(script, [operation, "--db", database, *extra], root, expected)
        observations.append(result)
        return result["result"]

    call("init")
    empty = call("status")
    call("apply", "--input", "submit.json", "--actor", "operator", "--simulate-failure", expected=1)
    check(call("status") == empty, "a failed transaction wrote a partial effect")
    command = [sys.executable, "-B", str(script), "apply", "--db", db,
               "--input", "submit.json", "--actor", "operator"]
    children = []
    try:
        with closing(sqlite3.connect(root / db, isolation_level=None)) as lock:
            lock.execute("BEGIN IMMEDIATE")
            for _ in range(2):
                children.append(subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, text=True))
            time.sleep(.05)
            check(all(child.poll() is None for child in children), "concurrent workers did not overlap")
            lock.execute("COMMIT")
        concurrent = []
        for child in children:
            stdout, stderr = child.communicate(timeout=10)
            check(child.returncode == 0, f"concurrent worker failed: {stderr or stdout}")
            concurrent.append(json.loads(stdout))
        concurrent.sort(key=lambda result: result["effect"])
        check([result["effect"] for result in concurrent] == ["applied", "replayed"],
              "duplicate delivery effects differ")
    finally:
        for child in children:
            if child.poll() is None:
                child.kill()
                child.communicate()
    pending = call("status")
    check(pending["events"] == 1 and len(pending["requests"]) == 1
          and pending["requests"][0]["status"] == "pending", "duplicate changed persisted state")
    wrong_role = call("apply", "--input", "approve.json", "--actor", "operator", expected=1)
    conflict = call("apply", "--input", "conflict.json", "--actor", "operator", expected=1)
    check("role cannot" in wrong_role["reason"], "role error lost its meaning")
    check("different content" in conflict["reason"], "identity conflict lost its meaning")
    check(call("status") == pending, "refused work affected state")
    call("apply", "--input", "approve.json", "--actor", "supervisor")
    before = call("status")
    check(before["events"] == 2 and before["requests"][0]["status"] == "approved",
          "authorized workflow did not finish")
    backup = f"{label}-backup.sqlite"
    restored = f"{label}-restored.sqlite"
    call("backup", "--copy", backup)
    call("migrate")
    current = call("status")
    check(current == {**before, "schema": 2}, "migration did not preserve consumer state")
    call("restore", "--copy", backup, database=restored)
    check(call("status", database=restored) == before, "restored state does not match original")
    call("restore", "--copy", backup, database=db, expected=1)
    check(call("status") == current, "restoring over existing output changed live state")
    return {"concurrent_workers_observed": 2, "concurrent": concurrent,
            "before_migration": before, "after_migration": current,
            "restored": before, "observations": observations}


def requirement_record(root):
    today = datetime.now(timezone.utc).date()
    # The fixture never automatically claims a new date of external research.
    expiry = DOCUMENTED_CHECK_DATE + timedelta(days=90)
    check(DOCUMENTED_CHECK_DATE <= today <= expiry,
          "Recheck the primary sources and update the fixture evidence date before reuse.")
    source = pin(root, "requirements.md")
    check_source = DOCUMENTED_CHECK_DATE.isoformat()
    return {
        "schema": "atelier.production-choices/1",
        "id": "local-review-queue",
        "revision": 1,
        "author": AUTHOR,
        "objective": "Local read, review and restore with one committed effect per delivery ID",
        "target": "Disposable system temporary directory and two local CLI callers",
        "target_kind": "cli",
        "experiment": {
            "candidate_id": "stdlib-sqlite",
            "purpose": "Compare atomic delivery and durable recovery for identical local events",
            "inputs": [pin(root, name) for name in ("submit.json", "conflict.json", "approve.json")],
            "procedure": pin(root, "README.md"),
            "success_criteria": ["One committed effect per delivery", "Denied writes leave the snapshot intact",
                                 "The V1 report remains readable after V2 migration and exact restore"],
            "temporary_boundary": "Disposable fixture databases and two local processes only",
        },
        "requirements": [
            {"id": key, "source": source, "hard": True, "description": description}
            for key, description in zip(REQUIREMENTS, (
                "No network, daemon or dependency installation",
                "Deduplicate concurrent delivery and refuse a conflicting replay",
                "Prevent an operator from approving a request",
                "Roll back all writes if the command fails before commit",
                "Preserve records during migration and restore into a fresh path",
                "Use a readable ownership map and reproducible commands",
            ))
        ],
        "candidates": [
            {
                "id": "stdlib-sqlite", "description": "Python commands and one local SQLite file",
                "reason": "Transactions and backup through the existing runtime",
                "mode": "feasible",
                "components": [
                    {"role": "runtime", "name": "Python", "version": sys.version.split()[0]},
                    {"role": "storage", "name": "SQLite", "version": sqlite3.sqlite_version},
                ],
                "checks": dict.fromkeys(REQUIREMENTS, "unknown"),
                "sources": [{
                    "url": "https://www.sqlite.org/lang_transaction.html",
                    "checked_on": check_source, "review_by": expiry.isoformat(),
                    "claim": "Immediate transaction and rollback semantics for local writers",
                }, {
                    "url": "https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup",
                    "checked_on": check_source, "review_by": expiry.isoformat(),
                    "claim": "Standard-library connection and consistent backup support",
                }],
            }, {
                "id": "plain-json", "description": "One JSON file plus standard-library CLI",
                "reason": "The simple JSON approach does not provide transaction or replay control itself",
                "mode": "excluded",
                "components": [{"role": "storage", "name": "JSON file", "version": "RFC 8259"}],
                "checks": {**dict.fromkeys(REQUIREMENTS, "unknown"), "R-ONCE": "fail"},
                "sources": [],
            }, {
                "id": "server-database", "description": "Use a separate database service",
                "reason": "A new database service violates the local no-daemon requirement",
                "mode": "excluded",
                "components": [{"role": "storage", "name": "Client/server database", "version": "tbd"}],
                "checks": {**dict.fromkeys(REQUIREMENTS, "unknown"), "R-LOCAL": "fail"},
                "sources": [],
            },
        ],
    }, expiry.isoformat()


def author_run(root, engine):
    root.mkdir(mode=0o700)
    populate(root)
    record = root / "production-choices.json"
    value, deadline = requirement_record(root)
    write(record, value)
    commands = []

    def gate(phase, expected=0):
        result = invoke(engine, ["verify", ".", "--phase", phase, "--required-kind", "cli"],
                        root, expected)
        commands.append(result)
        return result["result"]

    gate("explore")
    gate("implement", 1)
    control = queue(root, "without-choice-preflight")
    write(root / "probe.json", control)
    chosen = value["candidates"][0]
    chosen["checks"] = dict.fromkeys(REQUIREMENTS, "pass")
    chosen["probe"] = pin(root, "probe.json")
    value["decision"] = {
        "selected": chosen["id"], "reason": "Observed transaction, role, migration and recovery behavior",
        "review_by": deadline, "configuration": [pin(root, p) for p in ("review_queue.py", "architecture.md")],
        "masters": [], "flows": [pin(root, "README.md")],
        "adaptations": "Applicable to the disposable local CLI. Any change to execution or storage reopens review.",
    }
    write(record, value)
    subject = invoke(engine, ["subject", "."], root)["result"]["decision_sha256"]
    (root / "authority.txt").write_text(
        "Integration owner delegated the isolated S1 technical sample and choice of SQLite or a"
        " justified alternative to /root/choice_contract. No owner acceptance of the sample is claimed.\n",
        encoding="utf-8",
    )
    write(root / "approval.json", {
        "schema": "atelier.production-choice-approval/1", "subject_sha256": subject,
        "actor": AUTHOR, "scope": "Delegated implementation choice for disposable synthetic fixture only",
        "source": pin(root, "authority.txt"),
    })
    value["decision"]["approval"] = pin(root, "approval.json")
    write(record, value)
    check(gate("implement")["decision_sha256"] == subject, "authoring digest does not agree")
    check(gate("scale", 1)["ok"] is False, "scale passed without independent evidence")
    check(gate("accept", 1)["ok"] is False, "accept passed without independent evidence")
    candidate = queue(root, "with-choice-preflight")
    for key in ("concurrent", "before_migration", "after_migration", "restored"):
        check(control[key] == candidate[key], f"business behavior drift: {key}")
    configuration = root / "architecture.md"
    original = configuration.read_bytes()
    try:
        configuration.write_bytes(original + b"\nChanged without approval.\n")
        check("stale implementation configuration" in gate("implement", 1)["error"],
              "gate did not explain changed configuration")
    finally:
        configuration.write_bytes(original)
    gate("implement")
    write(root / "candidate.json", candidate)
    write(root / "gate-probes.json", commands)
    write(root / "author-report.json", {
        "schema": "atelier.production-choice-technical-author/1",
        "actor": AUTHOR,
        "decision_sha256": subject,
        "candidate": pin(root, "candidate.json"),
        "control": pin(root, "probe.json"),
        "gate_probes": pin(root, "gate-probes.json"),
        "engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
        "baseline_scope": "Same exact fixture CLI and inputs without the new choice preflight. "
                          "This is not a reproduction of a historical project.",
        "implementation": "Real fixture CLI runtime and persisted state observed",
        "independent_review": "pending",
    })


def apply_review(root, engine, review):
    review = review.resolve()
    observation = read(review)
    author_pin = pin(root, "author-report.json")
    check(observation.get("author_report") == author_pin, "review does not cite the exact authored report")
    check(observation.get("schema") == "atelier.production-choice-technical-review/1",
          "unsupported independent review record")
    actor = observation.get("actor")
    check(isinstance(actor, str) and actor.strip() and actor.strip().casefold() != AUTHOR.casefold(),
          "independent review requires a different actor")
    check(observation.get("decision_sha256") == read(root / "author-report.json")["decision_sha256"],
          "review is not tied to the exact decision")
    check(set(observation.get("passed", [])) >= {"A07", "A08", "A09"}
          and str(observation.get("environment", "")).strip(),
          "actual comparison, recovery and maintenance evidence must be recorded")
    check(isinstance(observation.get("observations"), list) and observation["observations"],
          "include independent procedures and observations")
    receipt = root / "independent-review.json"
    check(not receipt.exists(), "review already attached")
    if review != receipt:
        with receipt.open("xb") as target:
            target.write(review.read_bytes())
    path = root / "production-choices.json"
    value = read(path)
    subject = observation["decision_sha256"]
    case_evidence = []
    for stage in ("scale", "accept"):
        case_evidence.append({
            "id": stage + "-technical-queue", "phase": stage, "decision_sha256": subject,
            "author": AUTHOR, "reviewer": actor, "method": "cli",
            "environment": observation["environment"], "outcome": "pass",
            "artifacts": [pin(root, "review_queue.py"), pin(root, "candidate.json")],
            "receipt": pin(root, receipt.name),
            "controls": [
                {"id": "maintained-runtime", "expect": "positive", "outcome": "pass",
                 "observation": pin(root, "candidate.json")},
                {"id": "changed-source-and-failures", "expect": "negative", "outcome": "pass",
                 "observation": pin(root, "gate-probes.json")},
            ],
        })
    value["evidence"] = case_evidence
    write(path, value)
    outcomes = [
        invoke(engine, ["verify", ".", "--phase", stage, "--required-kind", "cli"], root)
        for stage in ("scale", "accept")
    ]
    write(root / "admission-report.json", {"observations": outcomes})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--review", type=Path, help="Attach a separately produced independent review")
    args = parser.parse_args()
    root, engine = args.root.resolve(), args.engine.resolve(strict=True)
    if args.review is None:
        author_run(root, engine)
        print(json.dumps(read(root / "author-report.json"), indent=2))
    else:
        apply_review(root, engine, args.review)
        print(json.dumps(read(root / "admission-report.json"), indent=2))


if __name__ == "__main__":
    main()
