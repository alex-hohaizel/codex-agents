# Coordinate Builder work in separate Git worktrees

Use one coordinator to own the integration branch. Agree on an exact base
commit, divide the work by file ownership and give each Builder a separate
linked worktree. A Builder needs the assigned task, its requirements, the
allowed writable files, and the result to return. Configure the execution
host to enforce those paths. The Git commands check the resulting scope
and do not grant operating system permissions.

## Prepare an independent assignment

Run the commands from the reviewed Codex Agent System repository, and use
canonical absolute paths. Keep binding and recovery records outside the
writable worker worktrees.

```sh
TOOLS="$PWD/scripts"
python3 -B "$TOOLS/ticket_worktree.py" prepare --root "$PROJECT" \
  --base "$BASE" --worktree "$WORKER_ONE" --branch codex/worker-one \
  --write-path catalog.py > "$RECORDS/worker-one.json"
python3 -B "$TOOLS/ticket_worktree.py" prepare --root "$PROJECT" \
  --base "$BASE" --worktree "$WORKER_TWO" --branch codex/worker-two \
  --write-path quote.py > "$RECORDS/worker-two.json"
```

Retain each binding digest. For a ready project ticket, check that its
reviewed Builder handoff and the worker's exact Git baseline agree.

```sh
python3 -B "$TOOLS/ticket_worktree_assignment.py" --root "$PROJECT" \
  --handoff review/builder-handoff.json --handoff-sha256 "$HANDOFF_SHA" \
  --binding "$RECORDS/worker-one.json" --binding-sha256 "$ONE_BINDING_SHA"
```

The check binds the current replan receipt, ready ticket, Git base, exact
writable files and their starting bytes and modes. Keep the authoritative
project and return path in the coordinator checkout. Start the two Builders
with their own worktree as the code target. Give shared contracts as read inputs and assign a single
writer to any shared file. A separate worktree isolates the normal Git
working copy; read/write permission scope is still set by the host.

## Resume after a confirmed interruption

Before continuing, use the actual execution host to confirm that the old
worker stopped and determine whether there are unresolved effects. If the
outcome is uncertain, keep the task and its files held while reconciling
the native operation. Avoid sending another launch for the original job.

For a stopped Builder with durable local edits and an unchanged HEAD, save
an `atelier.worktree-interruption/1` record with `binding_sha256`,
`state: interrupted`, `native_run_ref`, `readback_ref` and `next_action`.
The operator supplies actual host/run references and pins the record. The
checkpoint checks that external record and the current Git state. It
requires uncommitted in-scope edits and an unchanged index. It rejects
staged changes and ignored or untracked files outside the declared scope.

```sh
python3 -B "$TOOLS/ticket_worktree_checkpoint.py" capture \
  --binding "$RECORDS/worker-one.json" --binding-sha256 "$ONE_BINDING_SHA" \
  --interruption "$RECORDS/interruption.json" --interruption-sha256 "$STOP_SHA" \
  > "$RECORDS/checkpoint.json"
python3 -B "$TOOLS/ticket_worktree_checkpoint.py" resume \
  --checkpoint "$RECORDS/checkpoint.json" --checkpoint-sha256 "$CHECKPOINT_SHA"
```

A fresh session rechecks this admission before editing. It reads the
persisted partial work and continues from the stated next action. A drifted
file, revised HEAD, changed binding or unresolved host result needs
reconciliation. Preserve the worktree until the result is accepted.

## Continue a reserved worktree after a confirmed interruption

Bind the linked worktree to the original reservation before launching the
first Builder. Save the binding and its digest outside the worker checkout.

```sh
python3 -B "$TOOLS/ticket_dispatch.py" claim --root "$PROJECT" \
  --reservation-id "$RESERVATION" --handoff review/builder-handoff.json \
  --handoff-sha256 "$HANDOFF_SHA" --binding "$RECORDS/worker-one.json" \
  --binding-sha256 "$ONE_BINDING_SHA"
```

Use `observe --phase running` to record the job identity from the host.
After an interruption, wait for that exact worker to stop and reconcile
its effects against their destinations. Keep the work held while anything
is uncertain. Capture the worktree checkpoint as described above. Use the
same job reference in the interruption record and the dispatch ledger.

```sh
python3 -B "$TOOLS/ticket_dispatch.py" reserve-resume --root "$PROJECT" \
  --reservation-id "$RESERVATION" --handoff-sha256 "$HANDOFF_SHA" \
  --checkpoint "$RECORDS/checkpoint.json" --checkpoint-sha256 "$CHECKPOINT_SHA" \
  --effects-readback-ref "$EFFECTS_READBACK"
```

The coordinator rechecks the approved handoff, recorded worktree, stopped
attempt and persisted bytes. The pending continuation keeps the worktree
and files reserved. One coordinator consumes the reservation and records
the fresh host job through `observe --phase running` with its new reference.
The resumed worker reruns the checkpoint's `resume` command before making
changes. After the fresh job ends, record `observe --phase finished` under
that job and keep independent acceptance of the result separate.

If a response is lost, inspect `status` and use the actual host to determine
whether the continuation started. A replay or local status response grants
no further launch. Resume from a confirmed terminal event only after the
operator reconciles all effects. The ledger records the operator's host
readback references. It leaves host authentication, subprocess launching
and permission enforcement to the operator and the execution host.

When the owning host confirms that the pending continuation never
started, record that specific observation against the current
reservation and checkpoint:

```sh
python3 -B "$TOOLS/ticket_dispatch.py" abort-resume --root "$PROJECT" \
  --reservation-id "$RESERVATION" --handoff-sha256 "$HANDOFF_SHA" \
  --checkpoint-sha256 "$CHECKPOINT_SHA" --readback-ref "$NO_START_READBACK"
```

The `resume-aborted` receipt releases the worktree and paths while
retaining the earlier launched attempts and partial files. A normal
`reserve-resume` retry cannot reopen the aborted checkpoint.
If the continuation did start, record its actual native job with
`observe --phase running`. If its outcome is unknown, leave the
reservation held until the host can resolve it.

To retry the same unchanged work after a verified no-start, get the exact
`abort_sha256` from the receipt or `status`, a fresh readback from the owning
host and a new attempt ID. Use the current handoff and checkpoint:

```sh
python3 -B "$TOOLS/ticket_dispatch.py" retry-resume --root "$PROJECT" \
  --reservation-id "$RESERVATION" --handoff-sha256 "$HANDOFF_SHA" \
  --checkpoint-sha256 "$CHECKPOINT_SHA" --abort-sha256 "$ABORT_SHA" \
  --attempt-id "$ATTEMPT" --readback-ref "$FRESH_NO_START_READBACK"
```

The coordinator rechecks source, scope and durable bytes, then reclaims
the worktree and write paths as one transaction. An overlapping live
reservation needs resolution first. Use the same `--attempt-id "$ATTEMPT"`
when recording the new start or another confirmed no-start. Exact retries
read the saved receipt. The new native job's identity governs its completion.

## Review and integrate the exact returns

The coordinator reviews and commits each in-scope contribution. Use a
separate, clean integration worktree with an attached branch at the same
base. Validate exact worker commits and preview the integration. Do not
accept a branch label as a substitute for reviewed commit bytes.

```sh
python3 -B "$TOOLS/ticket_worktree.py" candidate \
  --binding "$RECORDS/worker-one.json" --binding-sha256 "$ONE_BINDING_SHA" \
  --commit "$ONE_COMMIT"
python3 -B "$TOOLS/ticket_worktree.py" plan --root "$PROJECT" \
  --integration "$INTEGRATION" \
  --binding "$RECORDS/worker-one.json" --binding-sha256 "$ONE_BINDING_SHA" --commit "$ONE_COMMIT" \
  --binding "$RECORDS/worker-two.json" --binding-sha256 "$TWO_BINDING_SHA" --commit "$TWO_COMMIT" \
  > "$RECORDS/integration.json"
python3 -B "$TOOLS/ticket_worktree.py" apply \
  --plan "$RECORDS/integration.json" --plan-sha256 "$INTEGRATION_SHA"
```

The integration preview checks disjoint scopes and exact Git identities.
After applying, read back the integration commit and run the combined
scenario in its intended runtime. Use an independent reviewer on the
integrated result, including cross-component behavior and failure paths.
Keep the exact commit and observed result with the ticket. The host launch,
independent verdict, owner acceptance and release each have separate evidence.

## Close the cycle and retain the lessons

After integrating an epic or batch, ask the coordinator to save a retrospective
alongside the project's own records. Bind the original ticket scope and
criterion sources, planned and integrated commits, accepted and open results,
and independent QA. Read the diff, key decisions and interruption receipts.
Mark a missing receipt or ambiguous provider effect as open.

Use a fresh reviewer when a finding could affect other work or future
acceptance. Ask what actually happened, what the evidence can establish,
which earlier plan or boundary contributed, and what single change could be
verified next. Invite the affected roles when they have distinct evidence.
Keep a recorded finding and a proposed correction as separate items.

A finding includes the evidence, consequence, relevant requirement and exact
affected revision. A follow-up names its owner, preferred due milestone and
observable result. Link an existing ticket when it already owns the work.
Use the [project replan](TICKET_REPLAN.md) when a new task or updated criterion
needs a native project decision. Revisit accepted actions in the next
retrospective against their actual outcomes. The retrospective retains its
historical revision even after the follow-up is implemented.
