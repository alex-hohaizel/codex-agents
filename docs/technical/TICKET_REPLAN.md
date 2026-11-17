# Apply an approved project replan

This workflow uses the [project ticket tree](TICKET_TREE.md) and extends the
[change review](TICKET_CHANGE_REVIEW.md) from a preview to an authorized local
project update. The project remains authoritative for its requirements, evidence
and work ownership. The file adapter acts in a project that has adopted the
ticket projection as its native backlog. A derived export from another tracker
still needs its own write adapter.

A common route is to split one planned story into implementation and verification,
update the planned work that depends on it, and hand the first ready ticket to
Builder. Keep the prior record and evidence for historical review. A completed or
active ticket calls for a separate plan and coordination with its owner.

## Compare registered requirements

When product and implementation sources describe the same requirement in
different ways, compare their pinned records before applying the affected
replan. The `atelier.ticket-spec-sources/1` request contains `project_id`,
`native_revision`, a `sources` array of registry path and SHA-256 pins and
`requirement_ids` to check. Use an empty list to compare all recorded IDs.
The command follows requirement dependencies and returns the exact statements
and fields that differ, or a missing ID. Review differences with the project
owner and retain the selected rule as a decision. Matching records alone do
not prove complete sourcing or semantic equivalence.

```sh
python3 -B "$TOOLS/ticket_spec_review.py" --root "$PROJECT" \
  --input review/source-review.json --require-clean
```

## Draft, review and apply

Run these commands from the matching repository checkout. Use a canonical
absolute project directory. All filenames passed to the workflow are project
relative. Store previews, decisions and handoffs in the reviewed project location.

```sh
TOOLS="$PWD/scripts"
python3 -B "$TOOLS/ticket_replan_plan.py" --root "$PROJECT" \
  --projection tickets.json --request review/request.json
```

The request declares `atelier.ticket-replan-request/1`, the project ID, current
native revision, exact projection digest, proposed target revision and changes.
Each operation names an action, rationale and exact source citations. A
citation carries a path, SHA-256 and literal excerpt, with its requirement ID
when it refers to a requirement. Actions and their additional keys are:

| Action | Requested change |
| --- | --- |
| `create` | `ticket`, a planned initiative, epic or leaf |
| `replace` | `ticket_id` for a planned leaf and `ticket` for its replacement |
| `split` | `ticket_id` for a planned leaf and `tickets` for two or more new leaves |
| `drop` | `ticket_id` for a planned leaf with no affected live dependent |

A new ticket includes an ID, kind, title, parent as applicable, dependencies,
requirement IDs and an observable criterion. Review all implicit dependency
edits in the draft. The proposed target keeps retired originals as deferred.
Check plan requirements, stages and active task ownership with the relevant
specialists. Record inaccessible sourcing or a conflict as a pending decision.
The machine checks the cited bytes, structure and coverage. It takes a
subject-matter reviewer to judge whether the source supports the proposal.

After a confirmed owner decision, the authorized operator supplies a separately
retained decision file and its exact digest. This operation relies on the real
approval channel and its permissions. A model-created approval file carries
no owner authority. The file schema is `atelier.ticket-replan-decision/1`,
with keys `decision` (`approve`), `operation_id`, `project_id`,
`native_revision`, `target_revision`, `projection`, `request`,
`plan_sha256` and `authority_ref`. The projection and request pins come from
the reviewed plan. The operator supplies the decision digest as a separate
input. When a source or proposal changes, return the affected draft for review.

```sh
python3 -B "$TOOLS/ticket_replan_store.py" apply --root "$PROJECT" \
  --projection tickets.json --request review/request.json \
  --decision review/owner-decision.json --decision-sha256 "$DECISION_SHA"
python3 -B "$TOOLS/ticket_replan_store.py" receipt --root "$PROJECT" \
  --projection tickets.json --operation-id "$OPERATION" --plan-sha256 "$PLAN_SHA"
```

The file adapter serializes its writers, compares the expected baseline,
updates the projection with its receipt and reads it back. Use the same
operation ID when reconciling a lost response. A current verified result
permits evaluating the next step. A historical receipt shows an earlier
application and calls for review of the current revision. A conflicting or
partially observed result needs reconciliation before reuse. Correct a landed
change with a separately reviewed revision. Retain the historic transaction.

## Hand the ready ticket to Builder

Name only writable product files the actual authorization covers. Also name a
new return file under an existing review directory. Use the production
project's intended committed Git worktree. Keep the handoff at a separate
project-relative path such as `review/builder-handoff.json`.

```sh
python3 -B "$TOOLS/ticket_handoff.py" prepare --root "$PROJECT" \
  --projection tickets.json --operation-id "$OPERATION" --plan-sha256 "$PLAN_SHA" \
  --ticket "$TICKET" --write-path src/export.py \
  --return-path review/builder-result.json > "$PROJECT/review/builder-handoff.json"
```

Send the new session the handoff path and a separately recorded SHA-256.
At admission the receiving session runs:

```sh
python3 -B "$TOOLS/ticket_handoff.py" verify --root "$PROJECT" \
  --handoff review/builder-handoff.json --handoff-sha256 "$HANDOFF_SHA"
```

Admission checks the current receipt, Git root and HEAD, readiness, exact
authority artifacts, selected requirement text, scoped starting files and
unused return path. If circumstances changed, reconcile in the authoritative
project and prepare a new handoff. Check authorization and actual host write
permissions separately before editing. Report the durable result and test
locations back to the integration owner. The Builder `atelier.ticket-builder-return/1`
binds the handoff digest and ticket, records `status: changes-prepared`, supplies
an `artifacts` array of changed path and SHA-256 pins, and lists reported
`checks`. Read the actual saved changes before sending the exact result and
acceptance criteria to an independent reviewer.

```sh
python3 -B "$TOOLS/ticket_handoff.py" verify-result --root "$PROJECT" \
  --handoff review/builder-handoff.json --handoff-sha256 "$HANDOFF_SHA"
```

An admission result verifies
inputs and readiness at that time. Starting a role, completing work and
independently accepting the result each require their own observed evidence.

## Correct an unstarted replan after it landed

Retain the original exact projection in the project review area before applying.
If the last operation needs correcting, first reconcile the execution system.
The correction route applies only when an authorized operator has verified
that work from the operation did not start. A missing response or a blank
status does not establish that fact.

Create an `atelier.ticket-replan-no-dispatch/1` record with
`status: no-dispatch-observed`, the project ID, current native revision,
original operation ID, verified projection pin, original plan digest and
an `authority_ref` to the actual reconciliation. Have the authorized
operator supply this record.

Prepare `atelier.ticket-replan-correction-request/1` with the project ID,
current revision and projection digest, new target revision, rationale, original
operation ID in `undo_operation_id`, its digest in `undo_plan_sha256` and
`baseline` and `no_dispatch` file pins. The baseline must be the exact
pre-apply document retained under the original projection digest.

```sh
python3 -B "$TOOLS/ticket_replan_correction.py" --root "$PROJECT" \
  --projection tickets.json --request review/correction.json
```

Review the new plan and use the same decision and apply procedure with the
new plan hash and a new operation ID. The adapter restores the prior planned
leaf rows and dependencies, keeps introduced leaf IDs as retired history,
and retains existing receipts. Existing handoffs tied to the earlier
revision cease to be current. A running task, missing source, prior pending
write or later conflicting revision requires reconciliation before correction.
The local adapter checks the recorded authority reference and bytes. The
owning execution system establishes whether execution took place.

## Reserve shared execution paths

Use one canonical coordinator checkout for this local ledger. Before asking
the host to start a Builder, claim the reviewed handoff and writable paths.
Choose a reservation ID once, and retain it with the planned native launch.

```sh
python3 -B "$TOOLS/ticket_dispatch.py" claim --root "$PROJECT" \
  --handoff review/builder-handoff.json --handoff-sha256 "$HANDOFF_SHA" \
  --reservation-id "$RESERVATION"
python3 -B "$TOOLS/ticket_dispatch.py" status --root "$PROJECT" \
  --reservation-id "$RESERVATION"
```

A repeat reads the same reservation and does not grant another launch. A
recorded launch blocks a new reservation for that same ticket and revision,
including a packet with a different return path. When a dispatch result is
uncertain, check the actual execution host for the exact operation before
starting work or releasing the reservation. If the host confirms a launch, record
the exact job and readback reference. Use the same job for its terminal
result. Release an unlaunched reservation only when an operator has
confirmed absence of a launch.

```sh
python3 -B "$TOOLS/ticket_dispatch.py" observe --root "$PROJECT" \
  --reservation-id "$RESERVATION" --handoff-sha256 "$HANDOFF_SHA" \
  --phase running --native-job-ref "$NATIVE_JOB" --readback-ref "$READBACK"
```

Finish through `--phase finished` with the same job and a verified terminal
readback, or use `--phase released` with a verified no-launch readback for
a reserved job. Distinct active tickets can claim disjoint paths. A local
replan refuses changes that affect an active reservation. Independent work can
continue, with any result from a prior project revision reconciled at return.
Correction also checks whether the original operation has a recorded launch.
The ledger coordinates local operators that use it. The execution host still enforces
the actual file scope and reports job outcomes. Use the current native
worktree, permission and merge mechanisms for team execution. See
[the coordinated worktree workflow](TICKET_WORKTREES.md) for interruption and integration.

The [FieldSlate evaluation](../../evaluations/replan_delivery.py) exercises
application, readback, scoped Builder delivery and independent QA on a
disposable WSGI project.
