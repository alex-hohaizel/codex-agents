# Document templates and reviewed revisions

Use the document template tool for an editable planning document whose sections,
coaching order, assumptions and separate files come from a reviewed template.
The existing [product facilitation](PRODUCT_FACILITATION.md) and
[ticket specifications](TICKET_PRODUCT_SPEC.md) still accept their original inputs.

Use Python 3.9 or later. Work in a canonical project directory with Markdown
templates and a JSON registry of relative paths and SHA-256 hashes.

## List and inspect

```sh
TOOL=/path/to/codex-agents/scripts/document_templates.py
python3 -B "$TOOL" --root "$PROJECT" list --registry templates.json
python3 -B "$TOOL" --root "$PROJECT" inspect --registry templates.json \
  --template release-note > "$PROJECT/template-plan.json"
```

A registry uses `atelier.document-template-registry/1`. Each layer specifies
`scope`, `templates` and optionally `resources`. Each pin is a
`{"path":"templates/note.md","sha256":"<64 hex characters>"}` object.
Precedence increases from `module` to `agent`, `library`, `personal` and `team`.
Keep only one layer per scope. When a scope replaces a base using its template
ID, lower priority extensions are excluded. An extension uses `extends` to
apply changes without copying the base. Keep the base file version and all
registry and resource hashes visible in the returned plan.

Choose `template: release-note` and a `version` in a Markdown template's
frontmatter. Use `##` headings for sections. A normal section is required.
A leading `optional` comment makes it optional. A leading `include when:`
comment records a condition the operator evaluates against the actual case.
`facilitation_order: [audience, verification, rollout?]` is the coaching order,
independent of document order. `paced: true` exposes the first unsettled
section. A bare `## Table of Contents` generates linked entries for included
sections. Use `purpose`, `stance`, `inputs`, `writing`, `done when`,
`companions`, `view` and `next` comments to carry task-specific instructions.
The inspection result includes each section's instructions and any starter text.

An extension may patch an existing heading or add a section with a leading
`First.`, `Before Heading.` or `After Heading.` comment. An existing heading
with an `Adds to` comment appends coaching instructions. Giving an extension
its own `facilitation_order` replaces the entire order and names removed
sections in the report. A missing named anchor is reported for correction.
List and inspect again after any upstream template or overlay change.

## Prepare, update and review

Create a JSON request using `atelier.document-template-request/1` with a
stable `id`, `title`, `owner`, `sources` as file pins and a `sections` object
keyed by each section's ID. Each included section has `include: true` and
an `items` list. An item has a unique `id`, Markdown `body`, a list of source
paths and optionally a `title`. Use separate items for repeated material such
as alternatives or customer questions. Optional and conditional decisions
include a `reason` whether included or omitted. Use progress with a partial
`sections` object to return to the current coaching step in a new session.

Optional `assumptions` contain an `id`, `text` and a `status` of `open`,
`accepted` or `corrected`. A resolved assumption requires `resolution` and
pinned `sources`. An open assumption remains visibly marked and gates review.

A backticked Markdown filename in the template's companion declaration may
use `{id}` and `{slug}`. Key the request's `companions` object by the resulting
filename. Supply a decision and a reason even when the file is omitted. An
included companion has its own sourced items and is delivered as an editable
Markdown file beside the main document.

```sh
PLAN_SHA=$(jq -er .plan_sha256 "$PROJECT/template-plan.json")
python3 -B "$TOOL" --root "$PROJECT" progress --registry templates.json \
  --template release-note --request request.json
python3 -B "$TOOL" --root "$PROJECT" draft --registry templates.json \
  --template release-note --request request.json --expect-template "$PLAN_SHA" \
  --output release-note-v1
V1_SHA=$(jq -er .draft_sha256 "$PROJECT/release-note-v1/receipt.json")
python3 -B "$TOOL" --root "$PROJECT" update --registry templates.json \
  --template release-note --request request-v2.json --expect-template "$PLAN_SHA" \
  --draft release-note-v1/draft.json --expect-draft "$V1_SHA" --output release-note-v2
```

An update needs a `change_reason`, keeps the old revision and reports changed
section hashes. Every successful draft or update writes a new output directory
with the editable files, structured draft and final receipt. Use a fresh
directory after an incomplete write. Retain the previous artifacts and receipt
for review. Their exact file hashes are part of the draft's identity.

A separate reviewer reads the included sections, companions and referenced
rubric and sources. Supply a JSON review using
`atelier.document-template-review-input/1`, exact `draft_sha256`, a
`reviewer` distinct from the document owner, and `findings` with one
`{"status":"pass","note":"..." }` or `revise` record per included section
and companion. Companion keys are prefixed with `companion/`. Run the exact
review and retain its response.

```sh
V2_SHA=$(jq -er .draft_sha256 "$PROJECT/release-note-v2/receipt.json")
python3 -B "$TOOL" --root "$PROJECT" review --registry templates.json \
  --template release-note --draft release-note-v2/draft.json \
  --expect-draft "$V2_SHA" --findings findings.json
```

The tool checks the reviewed revision, exact rendered artifacts, current
template plan and source pins. It checks declared findings and reviewer fields.
The reviewer establishes substantive source fidelity and owner acceptance.

## Offline views

A template's `html_view` is `always`, `offer` or `never`. The registry
can disable HTML for all templates. With `offer`, include `"html":true` in
the request to render. `view: slides` renders a printable sequence of
sections. A pinned HTML layout uses `data-field`, `data-section`, optional
`data-body` inside that section, and `data-rest`. Omitted sections remove
their slots. If the layout leaves content unplaced the receipt lists it.
Styles and content stay offline. HTML views render a safe Markdown subset
with headings, emphasis, lists, tables, code, links and Mermaid source.
Use a reviewed diagram renderer separately when a drawn Mermaid diagram is
required. Template comments, method catalogs and rubrics guide the review.
They are input data and do not run scripts.

## Use the pinned BMad Method catalog

The catalog identifies the 18 Method templates and their associated view,
guidance, rubric and method assets by SHA-256. It omits their contents.
Acquire the exact upstream tree in an approved local directory under the
project. Preserve its MIT license and notices, including with any distributed
upstream layout or CSS. The pinned source and inventory are available here.

- [Upstream Method template reference](https://docs.bmad-method.org/reference/document-templates/)
- [Upstream source commit](https://github.com/bmad-code-org/BMAD-METHOD/tree/e435a22574fe55722841086e5566420178b98df3)
- [Pinned local catalog](../../scripts/document_templates_catalog.json)

```sh
git clone https://github.com/bmad-code-org/BMAD-METHOD.git "$PROJECT/upstream-bmad"
git -C "$PROJECT/upstream-bmad" checkout --detach e435a22574fe55722841086e5566420178b98df3
python3 -B "$TOOL" --root "$PROJECT" upstream-registry --upstream upstream-bmad \
  > "$PROJECT/templates.json"
python3 -B "$TOOL" --root "$PROJECT" list --registry templates.json
```

The catalog covers Method's analyst, PM and module templates. Other modules
can supply compatible local files through the registry. Use the source
template's optional sections, decisions, methods and rubric in a real
document before adopting it.
