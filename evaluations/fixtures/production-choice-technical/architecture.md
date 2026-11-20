# Decision and ownership map

The target is a review queue on one local workstation. JSON events and CLI
output are stable, documented interfaces. Python provides the runtime with
standard-library argument parsing, JSON and SQLite support. SQLite owns the
request state and event-replay record in one transaction. It serializes the
bounded number of local writers. Keep the request and event updates together.
This choice is specific to the requested local workload.

Plain JSON is suitable for read-only inspection but does not by itself provide
atomic commit of both records across concurrent writers. A server database
would add an unmanaged service while the brief calls for a disposable local
case. A file-lock and atomic rename design is a serious local alternative,
but needs a separate safe lock protocol, wraparound of crash behavior, and a
versioned backup procedure. The candidate uses SQLite instead. A genuine
change to concurrent multi-host work reopens the decision.

| Owner in `review_queue.py` | Responsibility |
| --- | --- |
| `read_event`, `ROLES` | Input contract and fixture caller role. The event has `event`, `request`, `action`, and a `title` only for `submit`. |
| `apply_event`, `transaction` | Atomic state transition and idempotency. Only one transaction is permitted per event. |
| `status` | Read-only reporting contract. Readers get one consistent snapshot. Keep stable ordering by request ID. |
| `version`, `migrate` | Schema compatibility boundary. V2 adds `source_tag` without rewriting request IDs or the old reporting contract. |
| `copy_database` | Consistent backup into a new path and integrity check. `restore` uses the same audited operation. |

No service or deployment is needed. Python must include the SQLite module.
The probe reports actual runtime versions. Backup and restore target an unused
path. Fatal errors return nonzero JSON and never announce success.

- [SQLite transaction behavior](https://www.sqlite.org/lang_transaction.html)
- [SQLite appropriate uses](https://www.sqlite.org/whentouse.html)
- [Python sqlite3 backup API](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup)
