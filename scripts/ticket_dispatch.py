#!/usr/bin/env python3
"""Reserve a ready Builder handoff locally and reconcile its observed execution."""

import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
import ticket_handoff as handoff
import ticket_worktree_assignment as assignment
import ticket_worktree_checkpoint as checkpoint

context = handoff.context
store = handoff.store
LEDGER = "atelier.ticket-dispatch-ledger/1"
RESULT = "atelier.ticket-dispatch-result/1"
FILENAME = ".ticket-dispatch.json"
LOCK_NAME = ".ticket-replan.lock"
ACTIVE = {"reserved", "running", "resume-reserved"}
TRANSITIONS = {"reserved": {"running", "released"}, "running": {"finished", "resume-reserved"},
               "resume-reserved": {"running", "resume-aborted"}, "resume-aborted": {"resume-reserved"}}
RECORD_FIELDS = {
    "reservation_id", "handoff", "projection", "native_revision", "operation_id",
    "ticket_id", "write_paths", "return_path", "events",
}


def ledger_path(root):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute coordinator checkout")
    return root / FILENAME


def path_ref(value):
    context.require(isinstance(value, str) and 0 < len(value) <= 4096 and "\0" not in value
                    and "\\" not in value, "invalid dispatch path")
    path = PurePosixPath(value)
    context.require(path.parts and not path.is_absolute() and ".." not in path.parts
                    and path.as_posix() == value, "expected a safe relative dispatch path")
    return path


def reserve_paths(row):
    return [*row["write_paths"], row["return_path"]]


def check_path_scope(row):
    context.require(isinstance(row["write_paths"], list) and 1 <= len(row["write_paths"]) <= 24,
                    "invalid dispatch writable paths")
    paths = reserve_paths(row)
    projection = path_ref(row["projection"]["path"])
    protected = {FILENAME, LOCK_NAME, str(projection.parent / LOCK_NAME),
                 row["handoff"]["path"], row["projection"]["path"]}
    for index, ref in enumerate(paths):
        path_ref(ref)
        context.require(not any(handoff.overlaps(ref, key) for key in protected),
                        f"dispatch path overlaps a coordinator record: {ref}")
        context.require(not any(handoff.overlaps(ref, prior) for prior in paths[:index]),
                        f"dispatch paths overlap: {ref}")


def event(phase, readback_ref=None, native_job_ref=None):
    row = {"phase": phase, "readback_ref": readback_ref, "native_job_ref": native_job_ref}
    if phase == "reserved":
        context.require(readback_ref is None and native_job_ref is None, "unexpected reservation observation")
    else:
        context.require(phase in {"running", "finished", "released"}, "unsupported observation phase")
        store.checked_identifier(row, "readback_ref")
        if phase == "released":
            context.require(native_job_ref is None, "release requires confirmed absence of a native job")
        else:
            store.checked_identifier(row, "native_job_ref")
    return row


def phase(row):
    return row["events"][-1]["phase"]


def job(row):
    return next((item["native_job_ref"] for item in reversed(row["events"])
                 if item["phase"] == "running"), None)


def started_jobs(row):
    return (item["native_job_ref"] for item in row["events"] if item["phase"] == "running")


def absolute_record_path(value):
    context.require(isinstance(value, (str, Path)), "expected an absolute record path")
    path = Path(value)
    context.require(path.is_absolute() and path.as_posix() == str(value)
                    and ".." not in path.parts and not any(ord(char) < 32 for char in str(path)),
                    "expected a canonical absolute record path")
    return path


def check_external_pin(pin):
    context.require(isinstance(pin, dict) and set(pin) == {"path", "sha256"}, "invalid external record pin")
    absolute_record_path(pin["path"])
    store.check_digest(pin["sha256"], "external record")


def resume_event(checkpoint_pin, native_job_ref, readback_ref, effects_readback_ref):
    check_external_pin(checkpoint_pin)
    observed = event("running", readback_ref, native_job_ref)
    observation = {**observed, "phase": "resume-reserved", "checkpoint": checkpoint_pin,
                   "effects_readback_ref": effects_readback_ref}
    store.checked_identifier(observation, "effects_readback_ref")
    return observation


def retry_fields(abort_sha256, attempt_id, readback_ref):
    store.check_digest(abort_sha256, "prior abort")
    fields = {"abort_sha256": abort_sha256, "attempt_id": attempt_id, "retry_readback_ref": readback_ref}
    for key in ("attempt_id", "retry_readback_ref"):
        store.checked_identifier(fields, key)
    return fields


def event_sha256(item):
    return context.digest(context.canonical(item))


def resume_abort_event(checkpoint_sha256, readback_ref, attempt_id=None):
    store.check_digest(checkpoint_sha256, "pending checkpoint")
    observation = {"phase": "resume-aborted", "checkpoint_sha256": checkpoint_sha256,
                   "readback_ref": readback_ref}
    store.checked_identifier(observation, "readback_ref")
    if attempt_id is not None:
        observation["attempt_id"] = attempt_id
        store.checked_identifier(observation, "attempt_id")
    return observation


def logical_ticket(row):
    return (handoff.comparable_path(row["projection"]["path"]),
            row["native_revision"], row["ticket_id"])


def check_record(row):
    context.require(isinstance(row, dict) and set(row) in (RECORD_FIELDS, RECORD_FIELDS | {"worktree_binding"}),
                    "invalid dispatch reservation")
    for key in ("reservation_id", "native_revision", "operation_id", "ticket_id"):
        store.checked_identifier(row, key)
    for key in ("handoff", "projection"):
        handoff.tree.pins([row[key]])
        path_ref(row[key]["path"])
    check_path_scope(row)
    if "worktree_binding" in row:
        binding = row["worktree_binding"]
        context.require(isinstance(binding, dict) and set(binding) == {"pin", "worker"},
                        "invalid dispatch worktree binding")
        check_external_pin(binding["pin"])
        absolute_record_path(binding["worker"])
    events = row["events"]
    context.require(isinstance(events, list) and 1 <= len(events) <= context.MAX_IDS
                    and events[0] == event("reserved"),
                    "invalid dispatch reservation history")
    used_checkpoints = set()
    attempts = set()
    last_continuation = None
    for prior, item in zip(events, events[1:]):
        context.require(isinstance(item, dict) and isinstance(item.get("phase"), str)
                        and item["phase"] in TRANSITIONS.get(prior["phase"], set()),
                        "invalid dispatch phase transition")
        fields = {"phase", "readback_ref", "native_job_ref"}
        if item["phase"] == "resume-reserved":
            resume_fields = fields | {"checkpoint", "effects_readback_ref"}
            retry = prior["phase"] == "resume-aborted"
            if retry:
                resume_fields |= {"attempt_id", "abort_sha256", "retry_readback_ref"}
            context.require("worktree_binding" in row and set(item) == resume_fields,
                            "invalid dispatch recovery observation")
            resume_event(item["checkpoint"], item["native_job_ref"], item["readback_ref"],
                         item["effects_readback_ref"])
            digest = item["checkpoint"]["sha256"]
            if retry:
                retry_fields(item["abort_sha256"], item["attempt_id"], item["retry_readback_ref"])
                context.require(item["abort_sha256"] == event_sha256(prior)
                                and item["attempt_id"] not in attempts
                                and item["retry_readback_ref"] != prior["readback_ref"]
                                and all(item[key] == last_continuation[key] for key in
                                        ("checkpoint", "native_job_ref", "readback_ref", "effects_readback_ref")),
                                "retry does not match the exact aborted continuation")
                attempts.add(item["attempt_id"])
            else:
                context.require(digest not in used_checkpoints and item["native_job_ref"] == prior["native_job_ref"],
                                "checkpoint already authorized a continuation or native job ref changed")
            used_checkpoints.add(digest)
            last_continuation = item
        elif item["phase"] == "resume-aborted":
            abort_fields = {"phase", "readback_ref", "checkpoint_sha256"}
            if "attempt_id" in prior:
                abort_fields.add("attempt_id")
            context.require(set(item) == abort_fields and item.get("attempt_id") == prior.get("attempt_id"),
                            "invalid dispatch no-start observation or attempt fence")
            resume_abort_event(item["checkpoint_sha256"], item["readback_ref"], item.get("attempt_id"))
            context.require(item["checkpoint_sha256"] == prior["checkpoint"]["sha256"],
                            "no-start observation does not match the pending checkpoint")
        else:
            context.require(set(item) == fields, "invalid dispatch observation")
            event(item["phase"], item["readback_ref"], item["native_job_ref"])
        if item["phase"] == "finished":
            context.require(item["native_job_ref"] == prior["native_job_ref"], "native job ref changed")


def path_conflict(path, exact, parents):
    return path in exact or path in parents or bool(exact.intersection(path.parents))


def admit_active(row, tickets, claimed, claimed_parents, pinned, pinned_parents, workers):
    key = row["ticket_id"]
    context.require(key not in tickets, f"ticket already reserved: {key}")
    handoff_path = handoff.comparable_path(row["handoff"]["path"])
    context.require(not path_conflict(handoff_path, claimed, claimed_parents),
                    "handoff overlaps an active reservation's output")
    for ref in reserve_paths(row):
        path = handoff.comparable_path(ref)
        context.require(not path_conflict(path, claimed, claimed_parents)
                        and not path_conflict(path, pinned, pinned_parents),
                        f"dispatch path overlaps active reservation: {ref}")
        claimed.add(path)
        claimed_parents.update(path.parents)
    pinned.add(handoff_path)
    pinned_parents.update(handoff_path.parents)
    binding = row.get("worktree_binding")
    if binding is not None:
        worker = handoff.comparable_path(binding["worker"])
        context.require(worker not in workers, "worker worktree already has an active reservation")
        workers.add(worker)
    tickets.add(key)


def active_index(rows):
    index = tuple(set() for _ in range(6))
    for row in rows:
        if phase(row) in ACTIVE:
            admit_active(row, *index)
    return index


def read_ledger(root, path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None, {"schema_version": LEDGER, "project_root": str(root), "project_id": None,
                      "reservations": []}
    context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                    "dispatch ledger must be a regular file without hard links")
    raw = context.bound_bytes(root, FILENAME)
    ledger = context.json_object(raw)
    context.require(set(ledger) == {"schema_version", "project_root", "project_id", "reservations"}
                    and ledger["schema_version"] == LEDGER and ledger["project_root"] == str(root),
                    "dispatch ledger belongs to another coordinator checkout or has an invalid schema")
    store.checked_identifier(ledger, "project_id")
    reservations = ledger["reservations"]
    context.require(isinstance(reservations, list) and 1 <= len(reservations) <= context.MAX_IDS,
                    "invalid dispatch reservation count")
    ids, hashes, jobs = set(), set(), set()
    for row in reservations:
        check_record(row)
        identifier, digest = row["reservation_id"], row["handoff"]["sha256"]
        context.require(identifier not in ids and digest not in hashes, "duplicate dispatch identity")
        ids.add(identifier)
        hashes.add(digest)
        for native_job in started_jobs(row):
            context.require(native_job not in jobs, "duplicate native dispatch job identity")
            jobs.add(native_job)
    active_index(reservations)
    return raw, ledger


def create_ledger(path, raw, precondition):
    fd, name = tempfile.mkstemp(prefix=".ticket-dispatch-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        precondition()
        # All supported writers hold the checkout lock, including the first writer.
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def commit(root, path, before, ledger, recheck=None):
    raw = store.projection_bytes(ledger)
    context.require(len(raw) <= context.MAX_BOUND_SOURCE, "dispatch ledger exceeds the native size limit")

    def precondition():
        prior, _ = read_ledger(root, path)
        context.require(prior == before, "dispatch ledger drift; inspect the current reservation before retrying")
        if recheck is not None:
            recheck()

    if before is None:
        create_ledger(path, raw, precondition)
    else:
        store.atomic_replace(path, raw, precondition)
    observed, _ = read_ledger(root, path)
    context.require(observed == raw, "unknown dispatch ledger outcome; use status before retrying")


def record_result(status, root, project_id, row=None, **fields):
    result = {
        "schema_version": RESULT, "status": status, "project_root": str(root), "project_id": project_id,
        "native_receipt_authenticated": False, "process_permissions_enforced": False,
        "launch_performed": False, **fields,
    }
    if row is not None:
        result["reservation"] = {**row, "phase": phase(row)}
        if phase(row) == "resume-aborted":
            result["abort_sha256"] = event_sha256(row["events"][-1])
    return result


def find(ledger, reservation_id):
    return next((row for row in ledger["reservations"] if row["reservation_id"] == reservation_id), None)


def claim(root, handoff_name, handoff_sha256, reservation_id, binding_path=None, binding_sha256=None):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    store.check_digest(handoff_sha256, "handoff")
    path_ref(handoff_name)
    packet_pin = {"path": handoff_name, "sha256": handoff_sha256}
    binding_pin = None
    context.require((binding_path is None) == (binding_sha256 is None),
                    "worktree binding requires both a path and SHA-256")
    if binding_path is not None:
        binding_pin = checkpoint.pin(absolute_record_path(binding_path), binding_sha256)
        check_external_pin(binding_pin)
    context.require(not any(handoff.overlaps(handoff_name, ref) for ref in (FILENAME, LOCK_NAME)),
                    "handoff overlaps a coordinator record")
    with store.projection_lock(path):
        before, ledger = read_ledger(root, path)
        existing = find(ledger, reservation_id)
        if existing is not None:
            context.require(existing["handoff"] == packet_pin, "reservation ID belongs to another handoff")
            context.require(existing.get("worktree_binding", {}).get("pin") == binding_pin,
                            "reservation ID belongs to a different worktree configuration")
            return record_result("replayed", root, ledger["project_id"], existing, admission_rechecked=False)
        reservations = ledger["reservations"]
        context.require(len(reservations) < context.MAX_IDS, "dispatch history limit reached")
        context.require(all(row["handoff"]["sha256"] != handoff_sha256 for row in reservations),
                        "handoff already has a reservation; use its exact identity")
        raw = context.bound_bytes(root, handoff_name)
        context.require(context.digest(raw) == handoff_sha256, "handoff changed")
        packet = context.json_object(raw)
        context.require(packet.get("schema_version") == handoff.HANDOFF, "unsupported handoff schema")
        projection_ref = packet.get("projection")
        handoff.tree.pins([projection_ref])
        projection = store.projection_path(root, projection_ref["path"])
        projection_lock_ref = str(PurePosixPath(projection_ref["path"]).parent / LOCK_NAME)
        context.require(not handoff.overlaps(handoff_name, projection_lock_ref),
                        "handoff overlaps the projection lock")
        nested_lock = store.projection_lock(projection) if projection.parent != path.parent else nullcontext()
        with nested_lock:
            verified = handoff.verify(root, handoff_name, handoff_sha256)["handoff"]
            project = verified["project_id"]
            context.require(ledger["project_id"] in (None, project),
                            "coordinator checkout is already bound to a different project")
            row = {
                "reservation_id": reservation_id, "handoff": packet_pin, "projection": verified["projection"],
                "native_revision": verified["native_revision"], "operation_id": verified["operation_id"],
                "ticket_id": verified["ticket"]["id"], "write_paths": [
                    item["path"] for item in verified["write_paths"]
                ], "return_path": verified["return_path"], "events": [event("reserved")],
            }
            assigned = None
            if binding_pin is not None:
                assigned = assignment.assign(root, handoff_name, handoff_sha256, binding_path, binding_sha256)
                row["worktree_binding"] = {"pin": binding_pin, "worker": assigned["worker"]["path"]}
            check_record(row)
            identity = logical_ticket(row)
            context.require(not any(job(prior) is not None and logical_ticket(prior) == identity
                                    for prior in reservations),
                            "Builder already started this ticket revision; replan before dispatching again")
            admit_active(row, *active_index(reservations))
            ledger["project_id"] = project
            reservations.append(row)

            def recheck():
                current = handoff.verify(root, handoff_name, handoff_sha256)["handoff"]
                context.require(current == verified, "handoff drift before reservation commit")
                if binding_pin is not None:
                    current = assignment.assign(root, handoff_name, handoff_sha256, binding_path, binding_sha256)
                    context.require(current == assigned, "worktree drift before reservation commit")

            commit(root, path, before, ledger, recheck)
            return record_result("reserved", root, project, row, admission_rechecked=True)


def observe(root, reservation_id, handoff_sha256, requested, readback_ref, native_job_ref=None, attempt_id=None):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    store.check_digest(handoff_sha256, "handoff")
    context.require(isinstance(requested, str) and requested in {"running", "finished", "released"},
                    "unsupported observation phase")
    item = event(requested, readback_ref, native_job_ref)
    with store.projection_lock(path):
        before, ledger = read_ledger(root, path)
        row = find(ledger, reservation_id)
        context.require(row is not None and row["handoff"]["sha256"] == handoff_sha256,
                        "observation does not match the reservation identity")
        if item in row["events"]:
            return record_result("replayed", root, ledger["project_id"], row)
        context.require(requested in TRANSITIONS.get(phase(row), set()), "invalid dispatch phase transition")
        context.require(attempt_id == row["events"][-1].get("attempt_id"),
                        "launch observation does not match the pending attempt fence")
        if requested == "finished":
            context.require(native_job_ref == job(row), "native job ref differs from the observed launch")
        if requested == "running":
            context.require(not any(native_job_ref in started_jobs(other) for other in ledger["reservations"]),
                            "native job ref was already observed for a dispatch attempt")
        row["events"].append(item)
        check_record(row)
        commit(root, path, before, ledger)
        return record_result("recorded", root, ledger["project_id"], row)


def commit_resume(root, path, before, ledger, row, checkpoint_pin, effects_readback_ref, retry=None):
    context.require("worktree_binding" in row, "dispatch needs a worktree binding recorded before launch")
    binding = row["worktree_binding"]
    checkpoint_path = Path(checkpoint_pin["path"])
    checkpoint_sha256 = checkpoint_pin["sha256"]
    record = checkpoint.read_pinned(checkpoint_path, checkpoint_sha256)
    context.require(record.get("binding") == binding["pin"], "checkpoint refers to a different dispatch worktree binding")
    native_job = job(row)
    context.require(record.get("native_run_ref") == native_job, "checkpoint does not name the current dispatch attempt")
    projection = store.projection_path(root, row["projection"]["path"])
    nested_lock = store.projection_lock(projection) if projection.parent != path.parent else nullcontext()
    with nested_lock:
        def fresh_admission():
            handoff.verify(root, row["handoff"]["path"], row["handoff"]["sha256"])
            admission = checkpoint.resume(checkpoint_path, checkpoint_sha256)
            context.require(admission["worktree"] == binding["worker"] and admission["resumed_from"] == native_job,
                            "checkpoint no longer matches the reserved worktree and stopped attempt")
            return admission

        admission = fresh_admission()
        stop_pin = record["interruption"]
        stop = checkpoint.interrupt_record(Path(stop_pin["path"]), stop_pin["sha256"], binding["pin"]["sha256"])
        event_record = resume_event(checkpoint_pin, native_job, stop["readback_ref"], effects_readback_ref)
        row["events"].append({**event_record, **(retry or {})})
        check_record(row)

        def recheck():
            context.require(fresh_admission() == admission, "recovery inputs changed before reservation commit")

        commit(root, path, before, ledger, recheck)
        return record_result("resume-reserved", root, ledger["project_id"], row,
                             admission_rechecked=True, continuation=admission)


def reserve_resume(root, reservation_id, handoff_sha256, checkpoint_path, checkpoint_sha256, effects_readback_ref):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    store.check_digest(handoff_sha256, "handoff")
    checkpoint_path = absolute_record_path(checkpoint_path)
    checkpoint_pin = checkpoint.pin(checkpoint_path, checkpoint_sha256)
    check_external_pin(checkpoint_pin)
    store.checked_identifier({"effects_readback_ref": effects_readback_ref}, "effects_readback_ref")
    with store.projection_lock(path):
        before, ledger = read_ledger(root, path)
        row = find(ledger, reservation_id)
        context.require(row is not None and row["handoff"]["sha256"] == handoff_sha256,
                        "recovery does not match the reservation identity")
        for item in row["events"]:
            recorded = item.get("checkpoint")
            if recorded is not None and recorded["sha256"] == checkpoint_sha256:
                context.require(recorded == checkpoint_pin and item["effects_readback_ref"] == effects_readback_ref,
                                "checkpoint already authorized a continuation with different inputs")
                terminal = row["events"][-1]
                context.require(not (terminal["phase"] == "resume-aborted"
                                     and terminal["checkpoint_sha256"] == checkpoint_sha256),
                                "this continuation was aborted after a confirmed no-start")
                return record_result("replayed", root, ledger["project_id"], row, admission_rechecked=False)
        context.require(phase(row) == "running", "only an observed running attempt can reserve recovery")
        return commit_resume(root, path, before, ledger, row, checkpoint_pin, effects_readback_ref)


def abort_resume(root, reservation_id, handoff_sha256, checkpoint_sha256, readback_ref, attempt_id=None):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    store.check_digest(handoff_sha256, "handoff")
    observation = resume_abort_event(checkpoint_sha256, readback_ref, attempt_id)
    with store.projection_lock(path):
        before, ledger = read_ledger(root, path)
        row = find(ledger, reservation_id)
        context.require(row is not None and row["handoff"]["sha256"] == handoff_sha256,
                        "no-start observation does not match the reservation identity")
        current = row["events"][-1]
        if current == observation:
            return record_result("replayed", root, ledger["project_id"], row)
        context.require(current["phase"] == "resume-reserved", "no pending continuation to abort")
        context.require(current["checkpoint"]["sha256"] == checkpoint_sha256,
                        "no-start observation does not match the pending checkpoint")
        context.require(current.get("attempt_id") == attempt_id,
                        "no-start observation does not match the pending attempt fence")
        row["events"].append(observation)
        check_record(row)
        commit(root, path, before, ledger)
        return record_result("resume-aborted", root, ledger["project_id"], row)


def retry_resume(root, reservation_id, handoff_sha256, checkpoint_sha256, abort_sha256, attempt_id, readback_ref):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    store.check_digest(handoff_sha256, "handoff")
    store.check_digest(checkpoint_sha256, "pending checkpoint")
    retry = retry_fields(abort_sha256, attempt_id, readback_ref)
    with store.projection_lock(path):
        before, ledger = read_ledger(root, path)
        row = find(ledger, reservation_id)
        context.require(row is not None and row["handoff"]["sha256"] == handoff_sha256,
                        "retry does not match the reservation identity")
        for item in row["events"]:
            if item["phase"] == "resume-reserved" and item.get("attempt_id") == attempt_id:
                context.require(item["checkpoint"]["sha256"] == checkpoint_sha256
                                and all(item[key] == value for key, value in retry.items()),
                                "attempt ID already belongs to different retry inputs")
                return record_result("replayed", root, ledger["project_id"], row, admission_rechecked=False)
        current = row["events"][-1]
        context.require(current["phase"] == "resume-aborted" and event_sha256(current) == abort_sha256
                        and current["checkpoint_sha256"] == checkpoint_sha256,
                        "retry does not match the current confirmed no-start")
        context.require(current["readback_ref"] != readback_ref, "retry needs a fresh no-start readback")
        admit_active(row, *active_index(ledger["reservations"]))
        prior = row["events"][-2]
        return commit_resume(root, path, before, ledger, row, prior["checkpoint"],
                             prior["effects_readback_ref"], retry=retry)


def status(root, reservation_id):
    path = ledger_path(root)
    store.checked_identifier({"reservation_id": reservation_id}, "reservation_id")
    _, ledger = read_ledger(root, path)
    row = find(ledger, reservation_id)
    return record_result("found" if row is not None else "no-local-reservation", root, ledger["project_id"], row)


def list_reservations(root):
    path = ledger_path(root)
    _, ledger = read_ledger(root, path)
    rows = [{**row, "phase": phase(row)} for row in ledger["reservations"]]
    return record_result("listed", root, ledger["project_id"], reservations=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    for name in ("claim", "observe", "reserve-resume", "abort-resume", "retry-resume", "status", "list"):
        mode = modes.add_parser(name)
        mode.add_argument("--root", type=Path, required=True)
        if name != "list":
            mode.add_argument("--reservation-id", required=True)
        if name in {"claim", "observe", "reserve-resume", "abort-resume", "retry-resume"}:
            mode.add_argument("--handoff-sha256", required=True)
        if name == "claim":
            mode.add_argument("--handoff", required=True)
            mode.add_argument("--binding", type=Path, help="absolute worktree binding saved before launch")
            mode.add_argument("--binding-sha256")
        if name == "reserve-resume":
            mode.add_argument("--checkpoint", type=Path, required=True)
            mode.add_argument("--checkpoint-sha256", required=True)
            mode.add_argument("--effects-readback-ref", required=True,
                              help="operator's reference to the reconciliation of prior effects")
        if name == "abort-resume":
            mode.add_argument("--checkpoint-sha256", required=True, help="digest of the pending checkpoint")
            mode.add_argument("--readback-ref", required=True,
                              help="authoritative host reference confirming this continuation never launched")
        if name == "retry-resume":
            mode.add_argument("--checkpoint-sha256", required=True)
            mode.add_argument("--abort-sha256", required=True, help="digest from the current resume-aborted receipt")
            mode.add_argument("--readback-ref", required=True, help="fresh authoritative no-start observation")
        if name in {"observe", "abort-resume", "retry-resume"}:
            mode.add_argument("--attempt-id", required=name == "retry-resume",
                              help="fresh fence for retry or exact pending retry attempt for an observation")
        if name == "observe":
            mode.add_argument("--phase", choices=("running", "finished", "released"), required=True,
                              help="use released only after authoritative confirmation that no launch occurred")
            mode.add_argument("--readback-ref", required=True, help="operator's reference to the observed host state")
            mode.add_argument("--native-job-ref")
    args = parser.parse_args()
    try:
        if args.mode == "claim":
            result = claim(args.root, args.handoff, args.handoff_sha256, args.reservation_id,
                           args.binding, args.binding_sha256)
        elif args.mode == "observe":
            result = observe(args.root, args.reservation_id, args.handoff_sha256, args.phase,
                             args.readback_ref, args.native_job_ref, args.attempt_id)
        elif args.mode == "reserve-resume":
            result = reserve_resume(args.root, args.reservation_id, args.handoff_sha256, args.checkpoint,
                                    args.checkpoint_sha256, args.effects_readback_ref)
        elif args.mode == "abort-resume":
            result = abort_resume(args.root, args.reservation_id, args.handoff_sha256,
                                  args.checkpoint_sha256, args.readback_ref, args.attempt_id)
        elif args.mode == "retry-resume":
            result = retry_resume(args.root, args.reservation_id, args.handoff_sha256, args.checkpoint_sha256,
                                  args.abort_sha256, args.attempt_id, args.readback_ref)
        elif args.mode == "status":
            result = status(args.root, args.reservation_id)
        else:
            result = list_reservations(args.root)
    except (context.ContextError, OSError) as error:
        print(json.dumps({"status": "invalid-dispatch", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
