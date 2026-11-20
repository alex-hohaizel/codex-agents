# Local review queue

| ID | Required behavior |
| --- | --- |
| R-LOCAL | Use one local standard-library process per command. The routine path needs no network, daemon, model, package install or new billing. |
| R-ONCE | Two concurrent deliveries of the same event commit its effect once. The other returns replay. A reused event ID with different content is refused. |
| R-ACCESS | The trusted fixture caller assigns the operator or supervisor role. An operator cannot approve. Refused work leaves the queue and the event counter unchanged. |
| R-FAIL | An interruption between writes and commit leaves neither a partial request nor an event claim. A legitimate repeat after rollback applies once. |
| R-RESTORE | The first format migrates transactionally to the next. A verified pre-migration backup restores into a fresh path with the old records and original schema. |
| R-MAINTAIN | A maintainer can find owners of input, state, database migration and recovery, reproduce normal and error cases, and test a small change without additional tools. |

The example uses control inputs, not real customer data. `--actor` represents a
role assigned by the local caller. It is not authentication for a shared host.
The demonstration intentionally avoids device sharing, distributed storage and
remote writes. A requirement for remote authenticated users or more writers
requires a new decision for the affected path.
