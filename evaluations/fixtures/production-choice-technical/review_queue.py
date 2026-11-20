"""Disposable, local review queue for the production-choice consumer probe."""

import argparse
from contextlib import closing, contextmanager
import json
from pathlib import Path
import re
import sqlite3


MAX_INPUT = 16 * 1024
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
ROLES = {"submit": "operator", "approve": "supervisor"}


class QueueError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise QueueError(reason)


def read_event(path):
    with path.open("rb") as handle:
        raw = handle.read(MAX_INPUT + 1)
    require(len(raw) <= MAX_INPUT, "event exceeds the fixture input limit")

    def distinct(pairs):
        values = {}
        for key, value in pairs:
            require(key not in values, "event contains duplicate keys")
            values[key] = value
        return values

    event = json.loads(raw, object_pairs_hook=distinct)
    require(isinstance(event, dict), "event must be an object")
    action = event.get("action")
    require(isinstance(action, str) and action in ROLES, "unknown event action")
    expected = {"event", "request", "action"} | ({"title"} if action == "submit" else set())
    require(set(event) == expected, "event fields do not match the action")
    for key in ("event", "request"):
        value = event[key]
        require(isinstance(value, str) and IDENTIFIER.fullmatch(value), f"invalid {key} ID")
    if action == "submit":
        title = event["title"]
        require(isinstance(title, str) and 1 <= len(title) <= 120 and title == title.strip(),
                "title must contain 1–120 characters without edge spaces")
    return event


def connect(path, *, read_only=False):
    require(path.is_file() and not path.is_symlink(), "database must be an existing local file")
    mode = "ro" if read_only else "rw"
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode={mode}", uri=True,
                           isolation_level=None, timeout=3.0)


@contextmanager
def transaction(db, *, write=False):
    db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
    try:
        yield
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def version(db):
    result = db.execute("PRAGMA user_version").fetchone()[0]
    require(result in (1, 2), "unsupported queue schema")
    return result


def create_database(path):
    with path.open("xb"):
        pass
    try:
        with closing(connect(path)) as db, transaction(db, write=True):
            db.execute("CREATE TABLE requests (id TEXT PRIMARY KEY, title TEXT NOT NULL, "
                       "status TEXT NOT NULL CHECK (status IN ('pending', 'approved')))")
            db.execute("CREATE TABLE events (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
            db.execute("PRAGMA user_version = 1")
    except BaseException:
        path.unlink()
        raise
    return {"schema": 1}


def apply_event(path, event, actor, *, simulate_failure=False):
    require(actor == ROLES[event["action"]], "role cannot apply this action")
    body = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    with closing(connect(path)) as db, transaction(db, write=True):
        version(db)
        seen = db.execute("SELECT body FROM events WHERE id = ?", (event["event"],)).fetchone()
        if seen is not None:
            require(seen[0] == body, "event ID already belongs to different content")
            return {"effect": "replayed", "event": event["event"]}
        request = event["request"]
        if event["action"] == "submit":
            db.execute("INSERT INTO requests (id, title, status) VALUES (?, ?, 'pending')",
                       (request, event["title"]))
        else:
            changed = db.execute("UPDATE requests SET status = 'approved' "
                                 "WHERE id = ? AND status = 'pending'", (request,))
            require(changed.rowcount == 1, "request does not exist or is already closed")
        db.execute("INSERT INTO events (id, body) VALUES (?, ?)", (event["event"], body))
        if simulate_failure:
            raise QueueError("simulated interruption before commit")
    return {"effect": "applied", "event": event["event"]}


def status(path):
    with closing(connect(path, read_only=True)) as db, transaction(db):
        schema = version(db)
        rows = [
            {"id": key, "title": title, "status": state}
            for (key, title, state) in db.execute(
                "SELECT id, title, status FROM requests ORDER BY id"
            )
        ]
        events = db.execute("SELECT count(*) FROM events").fetchone()[0]
    return {"schema": schema, "requests": rows, "events": events}


def migrate(path):
    with closing(connect(path)) as db, transaction(db, write=True):
        old = version(db)
        if old == 1:
            db.execute("ALTER TABLE requests ADD COLUMN source_tag TEXT NOT NULL DEFAULT 'local'")
            db.execute("PRAGMA user_version = 2")
    return {"previous": old, "schema": 2}


def copy_database(source, destination):
    # This fixture never replaces a running or pre-existing database.
    with closing(connect(source, read_only=True)) as origin:
        version(origin)
        with destination.open("xb"):
            pass
        try:
            with closing(connect(destination)) as copy:
                origin.backup(copy)
                require(copy.execute("PRAGMA integrity_check").fetchone() == ("ok",),
                        "copied database failed integrity check")
                schema = version(copy)
        except BaseException:
            destination.unlink()
            raise
    return {"schema": schema, "copied": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("init", "apply", "status", "migrate", "backup", "restore"))
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--actor", choices=("operator", "supervisor"))
    parser.add_argument("--copy", type=Path)
    parser.add_argument("--simulate-failure", action="store_true")
    args = parser.parse_args()
    try:
        if args.operation == "apply":
            require(args.input and args.actor and not args.copy, "apply needs an input and actor")
            result = apply_event(args.db, read_event(args.input), args.actor,
                                 simulate_failure=args.simulate_failure)
        else:
            require(not (args.input or args.actor or args.simulate_failure), "only apply accepts event flags")
            if args.operation in ("backup", "restore"):
                require(args.copy, "backup and restore need a separate copy path")
                source, destination = ((args.db, args.copy) if args.operation == "backup"
                                       else (args.copy, args.db))
                result = copy_database(source, destination)
            else:
                require(not args.copy, "this operation does not accept a copy path")
                result = {"init": create_database, "status": status, "migrate": migrate}[
                    args.operation
                ](args.db)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(json.dumps({"ok": False, "reason": str(error)}))
        return 1
    print(json.dumps({"ok": True, **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
