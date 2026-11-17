# Review acceptance evidence for a candidate

Use the same project ticket IDs and requirements that guided implementation.
Start while planning the selected tickets and repeat the review after the
candidate is assembled. For a simple, local change, run its expected check
directly. The gate is for coordinated work with multiple criteria, evidence
or unresolved operations.

1. The QA lead identifies failure scenarios with the product and technical
   owners. For each one, record the consequence, priority, procedure and
   observable expected result. Include negative paths and applicable device,
   service, performance, reliability or access checks. Select tickets or a
   group from the project's own [ticket projection](TICKET_TREE.md). Selecting
   a group includes its active tickets, nested groups, and any criteria
   recorded for the selected or nested groups themselves.
2. Pin the exact candidate files and test inputs. Use a clean checkout of the
   candidate when available. Before execution, run the command with the plan
   alone to inspect each requirement's source, mapped checks, uncovered
   requirements and external prerequisites.
3. Assign someone other than the candidate producer to run the checks in the
   applicable medium. Keep the actual observable results. For an ambiguous
   external effect, record `unknown-effect` and reconcile at the destination.
4. Recompute the gate against the same plan and the review. If a candidate or
   test input changed, prepare a revised plan and rerun affected checks. Keep
   prior review files with their original pins. Send the gate and its actual
   evidence to the person authorized to accept or publish the result.

## Project-local plan and review

Save a plan under the project root. Replace the example names, placeholders
and digests with those of the candidate. The projection supplies the project
ID, native revision and requirement registry. Pin the implementation and
execution inputs, including tests and applicable configuration.

```json
{
  "schema_version": "atelier.ticket-quality-plan/1",
  "project_id": "quotes",
  "native_revision": "r2",
  "projection_sha256": "<tickets.json SHA-256>",
  "select": ["QUOTE-API"],
  "producer": "builder",
  "subject": [
    {"path": "service.py", "sha256": "<service.py SHA-256>"},
    {"path": "tests/test_quote.py", "sha256": "<test SHA-256>"}
  ],
  "checks": [
    {
      "id": "BAD-SKU",
      "ticket_id": "QUOTE-API",
      "requirement_ids": ["REQ-SKU"],
      "priority": "P0",
      "risk": "A quote could charge for the wrong item.",
      "procedure": "Request a quote for an unknown SKU.",
      "expected": "Return HTTP 400 with an invalid-quote result."
    }
  ]
}
```

Save a separate review with the exact plan digest and one observed result
per check. Use `pass`, `fail`, `unobserved` or `unknown-effect`. An observed
pass or failure includes at least one project-local artifact with its digest.
A check can refer to a device capture, a test transcript or a provider readback
that the reviewer actually inspected. Keep raw private evidence in the project.

```json
{
  "schema_version": "atelier.ticket-quality-review/1",
  "plan_sha256": "<quality-plan.json SHA-256>",
  "reviewer": "independent-qa",
  "results": [
    {
      "id": "BAD-SKU",
      "outcome": "pass",
      "observation": "HTTP 400 and invalid-quote response observed.",
      "artifacts": [{"path": "review/no-sku.txt", "sha256": "<artifact SHA-256>"}]
    }
  ]
}
```

```sh
TOOLS="$PWD/scripts"
python3 -B "$TOOLS/ticket_quality_gate.py" --root "$PROJECT" \
  --projection tickets.json --plan quality-plan.json --plan-sha256 "$PLAN_SHA"
python3 -B "$TOOLS/ticket_quality_gate.py" --root "$PROJECT" \
  --projection tickets.json --plan quality-plan.json --plan-sha256 "$PLAN_SHA" \
  --review quality-review.json --review-sha256 "$REVIEW_SHA" --require-pass
```

## Read the gate

| Result | Meaning for this review |
| --- | --- |
| `PASS` | Each scoped requirement and dependency has a mapped check. Every declared check has current passing evidence, and the selected work has no unresolved external prerequisite or explicit hold. |
| `CONCERNS` | At least one check is unobserved, uncertain or has stale evidence, there is an unmapped requirement, or the project still has an applicable hold. |
| `FAIL` | At least one current observed failure requires repair or a separately authorized exception. |
| `WAIVED` | Current non-P0 failures have applicable, unexpired recorded exceptions, and every other check and prerequisite meets the gate. |

Treat P0 as a non-waivable check in this workflow. If the project authorizes a
non-P0 failure exception, attach `waiver` to the failing result with `by`,
`reason`, `expires_on` (YYYY-MM-DD, inclusive) and a `decision` path/digest
pair for the separately recorded decision. The operator verifies the decision
maker's authority and the waiver's actual scope. Evaluate on the current date.
Use `--as-of` to reproduce a historical decision on its original date.

The tool exits 2 for invalid inputs or drift in a pinned plan, candidate or
review. With `--require-pass`, it exits 3 on any verdict other than `PASS`.
The script checks binding and declared coverage. The reviewer checks whether
the procedure proves the actual criterion, the evidence comes from this candidate in the intended
runtime, and the recorded identities and approvals are authentic. The
project retains its recorded statuses and release approval.
