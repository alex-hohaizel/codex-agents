#!/usr/bin/env python3
"""Apply an approved replan to one project-owned projection or recover its receipt."""

import argparse
from contextlib import contextmanager
import importlib.util as _platform_import
from pathlib import Path as _PlatformPath
_platform_spec = _platform_import.spec_from_file_location('_agent_system_platform', _PlatformPath(__file__).with_name('platform_support.py'))
platform_support = _platform_import.module_from_spec(_platform_spec)
exec(compile(_PlatformPath(__file__).with_name('platform_support.py').read_bytes(),
             str(_PlatformPath(__file__).with_name('platform_support.py')), 'exec'), platform_support.__dict__)
fcntl = platform_support
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
import ticket_tree as tree

context = tree.context
DECISION = "atelier.ticket-replan-decision/1"
RECEIPT = "atelier.ticket-replan-receipt/1"
RESULT = "atelier.ticket-replan-result/1"
HISTORY = "replan_receipts"
LOCK_NAME = ".ticket-replan.lock"
BINDING = ("project_id", "native_revision", "target_revision", "projection", "request")
DECISION_FIELDS = {*BINDING, "schema_version", "decision", "operation_id", "plan_sha256", "authority_ref"}
RECEIPT_FIELDS = {
    *BINDING, "schema_version", "operation_id", "plan_sha256", "decision", "decision_sha256",
    "target_content_sha256", "previous_receipt_sha256", "created_ticket_ids", "changed_ticket_ids",
}


def build_plan(root, projection_name, request_name):
    request = context.json_object(context.bound_bytes(root, request_name))
    if request.get("schema_version") == "atelier.ticket-replan-correction-request/1":
        from ticket_replan_correction import build_correction
        return build_correction(root, projection_name, request_name)
    from ticket_replan_plan import build_plan as build
    return build(root, projection_name, request_name)


def plan_sha256(plan):
    return context.digest(context.canonical(plan))


def check_digest(digest, label):
    context.require(isinstance(digest, str) and context.HASH.fullmatch(digest), f"invalid {label} SHA-256")


def checked_identifier(row, key):
    value = context.text(row, key)
    context.require(value == value.strip() and len(value) <= 240, f"invalid {key}")
    return value


def check_binding(row):
    for key in ("project_id", "native_revision", "target_revision", "operation_id"):
        checked_identifier(row, key)
    context.require(row["native_revision"] != row["target_revision"], "replan must advance the native revision")
    tree.pins([row["projection"], row["request"]])
    check_digest(row["plan_sha256"], "plan")


def read_decision(root, name, digest, projection_name, request_name):
    check_digest(digest, "decision")
    raw = context.bound_bytes(root, name)
    context.require(context.digest(raw) == digest, "decision digest mismatch")
    decision = context.json_object(raw)
    context.require(set(decision) == DECISION_FIELDS and decision["schema_version"] == DECISION
                    and decision["decision"] == "approve", "expected an exact approving decision record")
    check_binding(decision)
    context.text(decision, "authority_ref")
    context.require(decision["projection"]["path"] == projection_name
                    and decision["request"]["path"] == request_name,
                    "decision scope does not match the projection and request")
    return decision


def projection_path(root, name):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    path = context.local(root, name)
    context.require(path.name.casefold() != LOCK_NAME, "the replan lock path cannot be a projection")
    file = path.lstat()
    context.require(stat.S_ISREG(file.st_mode) and file.st_nlink == 1,
                    "replan requires a regular projection without hard links")
    return path


def read_projection(root, name):
    raw = context.bound_bytes(root, name)
    current = context.json_object(raw)
    context.require(current.get("schema_version") == tree.PROJECTION, "unsupported ticket projection schema")
    for field in ("project_id", "native_revision"):
        checked_identifier(current, field)
    return raw, current


def read_history(projection, name):
    history = projection.get(HISTORY, [])
    context.require(isinstance(history, list), "invalid replan receipt history")
    seen_operations, seen_revisions = set(), set()
    last = None
    for receipt in history:
        context.require(isinstance(receipt, dict) and set(receipt) == RECEIPT_FIELDS
                        and receipt["schema_version"] == RECEIPT, "invalid replan receipt")
        check_binding(receipt)
        tree.pins([receipt["decision"], receipt["projection"], receipt["request"]])
        check_digest(receipt["target_content_sha256"], "receipt target")
        context.require(receipt["decision_sha256"] == receipt["decision"]["sha256"], "invalid decision receipt pin")
        context.require(receipt["project_id"] == projection["project_id"], "receipt belongs to a different project")
        context.require(receipt["projection"]["path"] == name, "receipt belongs to a different projection")
        context.require(receipt["previous_receipt_sha256"] == last, "broken replan receipt history")
        created = set(context.bounded_ids(receipt["created_ticket_ids"], "created ticket IDs"))
        changed = set(context.bounded_ids(receipt["changed_ticket_ids"], "changed ticket IDs"))
        context.require(not created.intersection(changed), "ambiguous replan ticket scope")
        context.require(receipt["operation_id"] not in seen_operations, "duplicate replan operation ID")
        context.require(receipt["target_revision"] not in seen_revisions, "reused replan revision")
        seen_operations.add(receipt["operation_id"])
        seen_revisions.update((receipt["native_revision"], receipt["target_revision"]))
        last = plan_sha256(receipt)
    return history, seen_revisions


def content_sha256(projection):
    return plan_sha256({key: value for key, value in projection.items() if key != HISTORY})


def projection_bytes(projection):
    return (json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def result(raw, projection, name, receipt, status, is_latest):
    current = is_latest and projection["native_revision"] == receipt["target_revision"]
    if current:
        context.require(content_sha256(projection) == receipt["target_content_sha256"]
                        and projection_bytes(projection) == raw,
                        "current projection does not match the committed replan target")
    return {
        "schema_version": RESULT,
        "status": status if current else "historical",
        "projection": {"path": name, "sha256": context.digest(raw)},
        "native_revision": projection["native_revision"],
        "verified_readback": current,
        "authority_authenticated": False,
        "receipt": receipt,
    }


def known_receipt(history, operation_id):
    return next((row for row in history if row["operation_id"] == operation_id), None)


def read_receipt(root, projection_name, operation_id, plan_digest):
    check_digest(plan_digest, "plan")
    projection_path(root, projection_name)
    raw, projection = read_projection(root, projection_name)
    history, _ = read_history(projection, projection_name)
    receipt = known_receipt(history, operation_id)
    context.require(receipt is not None, "replan receipt not found")
    context.require(receipt["plan_sha256"] == plan_digest, "operation ID is bound to a different plan")
    return result(raw, projection, projection_name, receipt, "verified", receipt is history[-1])


@contextmanager
def projection_lock(path):
    # A fixed lock name covers projection names that alias each other on macOS.
    lock_path = path.parent / LOCK_NAME
    fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0), 0o600)
    try:
        if platform_support.WINDOWS: platform_support.fchmod(fd,0o600)
        info = os.fstat(fd)
        context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "invalid replan lock file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise context.ContextError("projection is busy; reconcile the previous operation first") from error
        yield
    finally:
        os.close(fd)


@contextmanager
def coordinator_lock(root, projection):
    # Dispatch holds the same coordinator lock before entering a nested projection.
    with projection_lock(root / LOCK_NAME):
        if projection.parent == root:
            yield
        else:
            with projection_lock(projection):
                yield


def check_dispatch_reservations(root, projection_name, plan, receipt):
    from ticket_dispatch import ACTIVE, job, ledger_path, phase, read_ledger
    from ticket_handoff import comparable_path

    _, ledger = read_ledger(root, ledger_path(root))
    target = comparable_path(projection_name)
    reservations = [row for row in ledger["reservations"]
                    if comparable_path(row["projection"]["path"]) == target]
    if not reservations:
        return
    context.require(ledger["project_id"] == plan["project_id"],
                    "dispatch ledger binds this projection to a different project")
    readiness = plan.get("readiness")
    rows = readiness.get("affected_tickets") if isinstance(readiness, dict) else None
    context.require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows),
                    "replan needs its affected-ticket scope to reconcile Builder reservations")
    affected = set(receipt["created_ticket_ids"]) | set(receipt["changed_ticket_ids"])
    affected.update(checked_identifier(row, "ticket_id") for row in rows)
    corrected = plan.get("correction", {}).get("corrects_operation_id")
    for reservation in reservations:
        active = phase(reservation) in ACTIVE
        if corrected is not None and reservation["operation_id"] == corrected:
            context.require(not active and job(reservation) is None,
                            "correction conflicts with an unresolved or previously started Builder reservation")
        key = reservation["ticket_id"]
        context.require(not active or key not in affected,
                        f"replan affects an unresolved Builder reservation: {key}")


def atomic_replace(path, raw, precondition):
    mode = stat.S_IMODE(path.lstat().st_mode)
    if platform_support.WINDOWS and platform_support.private_acl_report(path)['private']:
        mode = 0o600
    fd, name = tempfile.mkstemp(prefix=".ticket-replan-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            platform_support.fchmod(stream.fileno(), mode)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        precondition()
        os.replace(name, path)
        platform_support.sync_dir(path.parent)
    finally:
        Path(name).unlink(missing_ok=True)


def new_receipt(plan, decision, decision_pin, current, target, history):
    before = context.records(current, "tickets")
    after = context.records(target, "tickets")
    return {
        "schema_version": RECEIPT,
        "operation_id": decision["operation_id"],
        **{field: plan[field] for field in BINDING},
        "plan_sha256": decision["plan_sha256"],
        "decision": decision_pin,
        "decision_sha256": decision_pin["sha256"],
        "target_content_sha256": content_sha256(target),
        "previous_receipt_sha256": plan_sha256(history[-1]) if history else None,
        "created_ticket_ids": sorted(after.keys() - before.keys()),
        "changed_ticket_ids": sorted(key for key in before.keys() & after.keys() if after[key] != before[key]),
    }


def apply_plan(root, projection_name, request_name, decision_name, decision_sha256):
    path = projection_path(root, projection_name)
    context.require(len({projection_name, request_name, decision_name}) == 3,
                    "expect separate projection, request and decision paths")
    decision = read_decision(root, decision_name, decision_sha256, projection_name, request_name)
    decision_pin = {"path": decision_name, "sha256": decision_sha256}
    with coordinator_lock(root, path):
        before, projection = read_projection(root, projection_name)
        context.require(decision["project_id"] == projection["project_id"], "decision belongs to a different project")
        history, revisions = read_history(projection, projection_name)
        prior = known_receipt(history, decision["operation_id"])
        if prior is not None:
            context.require(prior["decision"] == decision_pin and prior["plan_sha256"] == decision["plan_sha256"],
                            "operation ID is bound to a different decision or plan")
            return result(before, projection, projection_name, prior, "replayed", prior is history[-1])
        context.require(decision["native_revision"] == projection["native_revision"]
                        and decision["projection"]["sha256"] == context.digest(before),
                        "stale replan baseline; regroup against the current projection")
        context.require(decision["target_revision"] not in revisions, "replan would reuse a historical revision")
        plan = build_plan(root, projection_name, request_name)
        context.require(all(plan[field] == decision[field] for field in BINDING)
                        and plan_sha256(plan) == decision["plan_sha256"], "plan differs from the reviewed decision")
        target = plan["target"]
        context.require(target["project_id"] == projection["project_id"]
                        and target["schema_version"] == tree.PROJECTION
                        and target["native_revision"] == decision["target_revision"]
                        and target.get(HISTORY, []) == history, "replan target identity or receipt history changed")
        receipt = new_receipt(plan, decision, decision_pin, projection, target, history)
        check_dispatch_reservations(root, projection_name, plan, receipt)
        content = {**target, HISTORY: [*history, receipt]}
        raw = projection_bytes(content)
        context.require(len(raw) <= context.MAX_BOUND_SOURCE, "updated projection exceeds the native size limit")

        def confirm_baseline():
            context.require(plan_sha256(build_plan(root, projection_name, request_name)) == decision["plan_sha256"],
                            "source or request drift before commit")
            context.require(context.digest(context.bound_bytes(root, decision_name)) == decision_sha256,
                            "decision changed before commit")
            projection_path(root, projection_name)
            context.require(context.bound_bytes(root, projection_name) == before,
                            "projection drift before commit")
            check_dispatch_reservations(root, projection_name, plan, receipt)

        atomic_replace(path, raw, confirm_baseline)
        observed, current = read_projection(root, projection_name)
        context.require(observed == raw, "unknown replan outcome; read the receipt before retrying")
        return result(observed, current, projection_name, receipt, "applied", True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("apply", "receipt"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--projection", required=True)
        if name == "apply":
            command.add_argument("--request", required=True)
            command.add_argument("--decision", required=True)
            command.add_argument("--decision-sha256", required=True)
        else:
            command.add_argument("--operation-id", required=True)
            command.add_argument("--plan-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "apply":
            record = apply_plan(args.root, args.projection, args.request, args.decision, args.decision_sha256)
        else:
            record = read_receipt(args.root, args.projection, args.operation_id, args.plan_sha256)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    except (context.ContextError, OSError, UnicodeError, RecursionError) as error:
        print(json.dumps({"status": "replan-error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
