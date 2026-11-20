# Local technical slice

This fixture implements a local review queue with a small Python CLI and one
SQLite database. Read [requirements.md](requirements.md) for the intended
behavior and [architecture.md](architecture.md) for ownership and choice
boundaries. It uses synthetic inputs in a new directory.

## Run the scenario

From the repository root, run with a new path:

```sh
case_dir="$(mktemp -d)/technical-choices"
"${AGENT_SYSTEM_PYTHON:-python3}" -B evaluations/fixtures/production-choice-technical/run_case.py "$case_dir"
```

The runner uses the same interpreter and fixture bytes for two passes. The
control runs without the production-choice preflight. The candidate passes
the preflight and exercises the same business behavior. The report does not
attribute the new fixture implementation to a historical release.

Expected results:

- Before any decision, `explore` permits a bounded probe and `implement`
  refuses to proceed.
- After the scoped decision, the validator admits implementation. It still
  refuses scale and acceptance without separate observations.
- The synthetic failure rolls back both records. Two overlapping child
  processes deliver the same event. One applies it and the other reports
  replay. A duplicate identifier with different content and an unauthorized
  role both return errors while preserving the state.
- The supervisor completes one request. The V1 backup retains that state.
  V2 is compatible with the V1 reporting contract. Restore opens the V1
  state in a new file and refuses to overwrite an existing database.
- A change to the pinned architecture source stops the next dependent
  operation. Restoring the exact bytes restores admission.

The runner writes all business command outputs and exit codes to
`probe.json` and `candidate.json`, choice outputs to `gate-probes.json`, and
exact pins to `author-report.json`. Production decisions include the runtime
versions actually observed. The external source date refers to the review of
this fixture, so an overdue decision requires deliberate source refresh.

## Manual maintenance route

The following commands start at a new empty case created by the runner, where
`submit.json` and `approve.json` already exist. Execute them from within that
directory, using a distinct inspection database:

```sh
python_cmd="${AGENT_SYSTEM_PYTHON:-python3}"
"$python_cmd" -B review_queue.py init --db inspect.sqlite
"$python_cmd" -B review_queue.py apply --db inspect.sqlite --input submit.json --actor operator
"$python_cmd" -B review_queue.py status --db inspect.sqlite
"$python_cmd" -B review_queue.py apply --db inspect.sqlite --input approve.json --actor operator
"$python_cmd" -B review_queue.py status --db inspect.sqlite
"$python_cmd" -B review_queue.py apply --db inspect.sqlite --input approve.json --actor supervisor
"$python_cmd" -B review_queue.py backup --db inspect.sqlite --copy inspect-v1.sqlite
"$python_cmd" -B review_queue.py migrate --db inspect.sqlite
"$python_cmd" -B review_queue.py restore --db restored-inspect.sqlite --copy inspect-v1.sqlite
"$python_cmd" -B review_queue.py status --db restored-inspect.sqlite
```

The operator's approval returns nonzero; continue with the inspection after
observing that error. The result should have schema `1`, two recorded events,
and one approved request. Search for `apply_event` when diagnosing a duplicate,
`ROLES` when diagnosing a denied transition, and `version` and `copy_database`
for a format/recovery problem. Use a backup and verify state in a new
database before replacing any consumer path. An old data file is not a
replacement for an approved program revision.

A representative maintenance change is to add a `pending_count` field in
`status` while retaining the existing keys and semantics. Copy the script
to a disposable location, locate `status` via the ownership map, make the
change in that copy, and observe the new result for a pending request and for
an approved request. Compare the old keys and check both schema/readback and
restore. The accepted clean inputs remain unchanged. Running the changed code
in the managed candidate requires a new decision binding.

## Attach independent evidence

A different actor runs the scenario and the maintenance change. Record the
actual comparison, recovery, and maintenance observations. The author report
is an input, and the reviewer adds a separate JSON file with these fields:

- `schema`: `atelier.production-choice-technical-review/1`
- `actor`: actual review actor, distinct from the author
- `author_report`: exact relative path `author-report.json`, its SHA-256, and its byte count
- `decision_sha256`: from the authored result to be reviewed
- `passed`: A07, A08, and A09 only once actually observed
- `environment` and `observations`: actual runtime, procedures, results, and limitations

Attach that file from the repository root:

```sh
"${AGENT_SYSTEM_PYTHON:-python3}" -B evaluations/fixtures/production-choice-technical/run_case.py "$case_dir" --review /path/to/observed-technical-review.json
```

The runner binds the independent evidence and invokes `scale` and `accept`
on the resulting record. The result certifies current pins and required
structural evidence; the review receipt describes what was actually observed.
