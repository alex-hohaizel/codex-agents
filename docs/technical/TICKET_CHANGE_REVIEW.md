# Review a plan when a requirement changes

This preview extends the [project ticket tree](TICKET_TREE.md) from inspecting a
single revision to comparing two project revisions and preparing a reviewable
refinement. It runs against files you select. The project or tracker still owns
requirements, decisions, status, assignees, and evidence.

Use it for changes that cross tasks or acceptance boundaries: for example, a
data rule changes after a story was accepted, while the interface is being
updated and a dependent release check has not started.

For authored PRD and architecture documents, see the [companion review](TICKET_PRODUCT_SPEC.md) to check their coverage and refresh their exact review after a requirement change.

## Read the change and separate responsibilities

| Actor | Reads | Returns |
| --- | --- | --- |
| Integration owner (Orchestrator or project director) | Change decision, current project identity, exact old and new projections | Change scope, impact report, one review owner, approved stop/continue boundary |
| Product and affected domain owners | Exact requirements and relevant PRD, architectural, UX, or implementation sections | Old-to-new edits, options to adjust, roll back or change scope, and an order of work |
| Independent reviewer | Relevant source passages, proposed edits, actual dependency owners and proof changed by the request | Missing impact, verified retained scope, new evidence due, blocking defects and separate verdict |
| Project owner, then implementation owner | Proposal and independent verdict; latest authoritative native records | Decision binding the exact proposal; write authorization; implementation or deliberately deferred work |

Give each reviewer only the applicable sources, IDs, permissions and output
contract. The author cannot sign their own independent review. Continue unrelated
work where the project allows it. For work already underway, review the change
with its current owner before rescheduling or replacing the plan. Preserve
accepted history; record fresh proof on the exact new revision when due.

## Compare two captured revisions

Run from the reviewed repository checkout. Use independently captured views of
the same project, not two revisions manufactured from an edited copy after
losing the original. An external tracker still needs its own authorized export.
Choose an output directory outside both authoritative source roots.

```sh
TOOLS="$PWD/scripts"
BEFORE="/absolute/path/to/project-r1"
AFTER="/absolute/path/to/project-r2"
OUT="/absolute/path/to/review"
mkdir -p "$OUT"

python3 -B "$TOOLS/ticket_impact.py" capture --root "$BEFORE" --input tickets.json > "$OUT/before.json"
python3 -B "$TOOLS/ticket_impact.py" capture --root "$AFTER"  --input tickets.json > "$OUT/after.json"
shasum -a 256 "$OUT/before.json" "$OUT/after.json"
python3 -B "$TOOLS/ticket_impact.py" compare \
  --before "$OUT/before.json" --before-sha256 YOUR_BEFORE_SHA256 \
  --after "$OUT/after.json" --after-sha256 YOUR_AFTER_SHA256 > "$OUT/impact.json"
```

Keep the digests with the capture receipts. Check the distinction between a
different file hash, a changed requirement row, an affected task and a receipt
that no longer binds to the current revision. Group rollups and dependency
paths show why a task appears; a listed task is a review candidate. An unchanged
task can still have a current binding warning. Old proof retains historical
meaning; neither a digest nor metadata proves who approved something or that an
implementation satisfies a criterion.

## Prepare a refinement

Use a disposable review copy of the selected project revision if the proposal
request must stay outside the authoritative source directory. Keep historical
files and source bytes unchanged. In this example, `VIEW` is that copy with the
same relative paths and hashes as the current project view.

```sh
python3 -B "$TOOLS/ticket_refine.py" brief \
  --root "$VIEW" --input tickets.json --select TICKET-21 > "$OUT/refinement-brief.json"
python3 -B "$TOOLS/ticket_refine.py" propose \
  --root "$VIEW" --input tickets.json --proposal refinement-request.json > "$OUT/refinement.json"
```

Between commands, write `refinement-request.json` under `VIEW` using the
brief's project, revision and projection digest. Replace the example values
with values from the brief and actual source. Each source citation pins an
exact path, digest and literal excerpt. A requirement citation also names its
ID. For an acceptance edit, cite a linked requirement. A link change requires
citations to the affected requirement IDs.

```json
{
  "schema_version": "atelier.ticket-refinement/1",
  "project_id": "example-project",
  "native_revision": "r2",
  "projection_sha256": "<digest from brief.projection.sha256>",
  "changes": [
    {
      "ticket_id": "TICKET-21",
      "rationale": "The current export decision removes an optional field.",
      "patch": {
        "acceptance": "The header and every exported row omit the retired field."
      },
      "sources": [
        {
          "path": "requirements.json",
          "sha256": "<native requirements digest>",
          "requirement_id": "REQ-EXPORT",
          "excerpt": "Do not include the retired field."
        }
      ]
    }
  ]
}
```

The request may propose changes to an existing ticket's title, acceptance
criterion, parent, dependency order or requirement links. The tool reports
before and after values, verified citations, graph and coverage changes, original
recorded status and evidence, and the next review role. It rejects drift,
invalid dependencies and loss of existing mandatory coverage. A source excerpt
proves where words occur, so a fresh reviewer must still decide whether the
words support the proposed interpretation. Leave proposed edits to accepted or
in-flight work in review. Retain their original plan, proof and owner until a
separate native decision authorizes any action. Nothing here writes to the
tracker, marks a ticket accepted, starts a run or changes the deployed system.

## Turn the report into a decision

Present the trigger and supporting facts; impact on requirements, stories,
architecture, UX, releases and historical proof; and concrete old-to-new edits
with responsible roles. Record why direct adjustment, rollback or a scope change
fits the evidence. List what can continue, what needs coordination or fresh
acceptance, and the exact decision still due.

Send changed artifacts and proof to a fresh reviewer before asking the owner to
accept the exact proposal. After separately authorized changes, recapture the
native revision and validate readiness before delegating implementation. If a
source changed in review, regenerate the affected packet. Manual dependency
discovery, tracker writes, automatically pausing active jobs and adopting an
unchanged old receipt on a new revision remain outside this preview.

For a project whose native backlog is the ticket projection, see the
[approved replan and Builder handoff](TICKET_REPLAN.md).

## Scope the next acceptance review

When you observe an acceptance test for a leaf ticket, retain its project and revision, ticket,
receipt and exact execution inputs. Save the `atelier.ticket-proof-scope/1`
record in the historical view with `project_id`, `native_revision`, `ticket_id`,
a `receipt` file pin and an `inputs` array of file pins. Include the actual
test and relevant runtime inputs. Keep the scope file's digest separately,
along with the approval and source references.

```sh
python3 -B "$TOOLS/ticket_proof_scope.py" \
  --before-root "$BEFORE" --after-root "$AFTER" --projection tickets.json \
  --scope review/proof-scope.json --scope-sha256 "$SCOPE_SHA"
```

A requirement, dependent ticket, proof subject or declared test input that
changed can call for fresh proof. If the change was outside the recorded
scope and exact inputs still match, the earlier result is eligible for a new
independent reuse review. The reviewer confirms the completeness of the
scope, actual environment and semantic fit. Keep the original receipt fixed
to its own revision, and record any new acceptance decision separately.
