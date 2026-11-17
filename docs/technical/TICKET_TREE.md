# Project ticket tree and board

The ticket tree reads a project-owned projection of initiatives, epics, stories,
bugs and spikes. Use it to find work that is ready, see which preceding task or
evidence is missing, and identify requirements without an actionable ticket.

```sh
python3 -B scripts/ticket_tree.py board --root "$PROJECT_ROOT" --input tickets.json
python3 -B scripts/ticket_tree.py validate --root "$PROJECT_ROOT" --input tickets.json
python3 -B scripts/ticket_tree.py validate --root "$PROJECT_ROOT" --input tickets.json --require-complete
```

Use a canonical absolute project root. All inputs and proofs name relative files
inside it. The projection with schema `atelier.ticket-projection/1` declares the
`project_id`, `native_revision`, pinned `requirement_sources` and `tickets`.
Projects continue to own their original requirements and workflow state.

Each ticket declares an `id`, `kind`, `title` and `status`. Use `parent` for
hierarchy, `depends_on` for prerequisites, `requirement_ids` for work coverage,
`acceptance` for the observable criterion and `evidence` for pinned files.
A file pin contains `path` and `sha256`. Use an explicit `blocked_reason` for
a recorded block. The supported statuses are `planned`, `in-progress`,
`in-review`, `blocked`, `accepted` and `deferred`.

The board preserves record status and derives execution disposition. Planned work
can become ready after its prerequisites have checked acceptance evidence.
Dependencies are inherited from parent groups. Held or deferred work prevents
downstream dispatch while supported past acceptance remains visible. Group
relationships and prerequisites must form an acyclic tree and dependency graph.
Work coverage comes from story, bug or spike requirements, including their
dependency closure. Strict validation reports uncovered applicable mandatory
requirements and separates explicitly deferred coverage.

## Acceptance records

To support an accepted ticket, include a pinned JSON evidence record with
`schema_version` set to `atelier.ticket-acceptance/1`. It binds the current
`project_id`, `native_revision`, `ticket_id`, the SHA-256 of the UTF-8 acceptance
criterion and a pinned `subject`. The subject must be the actual independent
output, distinct from its receipt, the projection and the governing requirement
sources. The owner or reviewing system creates and authorizes this record.

Changes to the declared sources, proof bytes or acceptance criterion invalidate the
affected validation. The utility checks the declared structure and exact file
contents. It neither modifies the project nor provides human acceptance or proof
of functional behavior. Invalid input or unsupported acceptance produces exit
code 2 in validation mode. `board` exposes unsupported recorded claims as blockers
so the operator can fix them.

See the [isolated room-booking case](../../scripts/tests/test_ticket_tree.py) for
the working projection and negative checks. It includes two initiatives, a
dependent epic, a verified result and deliberately held work.

## Inspect a sprint selection

```sh
python3 -B scripts/ticket_tree.py sprint --root "$PROJECT_ROOT" --input tickets.json \
  --select E-NOSHOW --select B-CLOCK
```

Repeat `--select` for tickets or groups. Groups expand to their work tickets in a
stable order. The view distinguishes ready, held, blocked, future and accepted
work. It identifies prerequisites inside and outside the selection, including
partly selected groups. Group membership does not imply completed group
acceptance. Work held by an ancestor retains recorded acceptance when supported
and keeps the dependent tasks out of ready work. The view does not create or edit a sprint
store, tracker or Git state. The held bucket includes selected work already in
progress or review. Its original status stays visible.

## Keep a sprint plan while the backlog changes

Prepare a timebox from the current board with an objective and explicit
selectors. Review the resulting record and preserve it at the project's
chosen path. The plan pins the source revision, initial members and their
requirements and acceptance contracts. The board supplies current status.

```sh
python3 -B scripts/ticket_sprint.py plan --root "$PROJECT_ROOT" --projection tickets.json \
  --sprint-id checkout-01 --goal "Verify checkout receipt recovery" \
  --starts-on 2026-11-17 --ends-on 2026-11-30 --select E-CHECKOUT \
  > "$REVIEW_DIR/sprint-draft.json"
```

After reviewing and saving the sprint at its project-relative path, keep its
file digest. Use that original plan as the backlog moves.

```sh
python3 -B scripts/ticket_sprint.py status --root "$PROJECT_ROOT" --projection tickets.json \
  --sprint sprint/checkout-01-r1.json --sprint-sha256 "$SPRINT_SHA"
```

The progress view recalculates status, evidence and prerequisites from the
current board for the recorded members. It separately lists removed or
retired work, unavailable selectors, members moved outside the selected
groups and new work that would enter under current group membership. Changed
member contracts, a replaced projection path and a reused revision with
different bytes call for scope review. The project board still owns readiness. For example, a newly proposed
prerequisite can block a selected story while the prerequisite remains
outside this sprint's recorded selection.

Use a new `plan` command with `--previous sprint/checkout-01-r1.json`
and `--previous-sha256 "$SPRINT_SHA"` to propose changes to the same sprint.
Keep the earlier plan, review the difference and record the chosen revision
through the project's authority. This command drafts and reads project-local
scope. It does not start tickets, resolve holds or update a tracker.
