# Facilitate a source-bound brief, PRFAQ or UX workshop

Use this workflow when a product proposal draws on notes or a workshop and
the team needs a decision before it can use the draft. Keep the original
source files and the authored content in the project. The current ticket
projection continues to own requirements and work state.

Run the examples from the distribution checkout with `TOOLS="$PWD/scripts"`. Create an `atelier.product-facilitation/1` request with `project_id`,
`native_revision`, `projection_sha256`, `author`, `title`, `route`, pinned
Markdown or text `sources`, pinned structured `decision_sources`, and the
`requirement_ids` that this workshop addresses. Every source pin contains
`path` and `sha256`. Supply evidence in `notes` entries with stable `id`,
`source_path`, `speaker` and one exact unique `excerpt`. Keep observations
and attributed proposals explicit. The helper verifies the quoted location
and source bytes. The reviewer checks speaker attribution and interpretation.

Each item in `questions` has `id`, `prompt`, `owner`, `needed_by`,
`positions` (the note IDs for possible choices) and `blocks` (the applicable
requirement IDs that need a decision). Each key in `sections` contains one or
more items with `heading`, `body` and `source_notes`.

| Route | Section keys | Readable outputs |
| --- | --- | --- |
| `brief` | `need`, `current`, `outcome`, `bounds` | `BRIEF` |
| `prfaq` | `release`, `customer`, `stakeholder` | `PRFAQ` with a draft announcement and separate FAQs |
| `ux` | `visual`, `components`, `journey`, `states`, `accessibility`, `acceptance` | Separate `DESIGN` and `EXPERIENCE` |

```sh
python3 -B "$TOOLS/product_facilitation.py" draft --root "$PROJECT" \
  --projection tickets.json --input workshop/request.json > "$RECORDS/workshop.json"

python3 -B "$TOOLS/product_facilitation.py" draft --root "$PROJECT" \
  --projection tickets.json --input workshop/request.json --document PRFAQ \
  --format html > "$RECORDS/PRFAQ.html"
```

Review the exact open question and any opposing positions. To record a real
approved choice in a native decision register, include its stable `id`,
`question_id` and `selected_note_id`. Bind `question_sha256` and the
`position_sha256` map for all discussion positions using the original draft’s
`question_sha256` and each position note’s `binding_sha256`. Keep the
previous record. Use an explicit native `supersedes` correction when replacing
a choice. Repin and render the new draft after the decision. The CLI holds
an old decision if its exact question or alternatives changed.

A separate reviewer returns an `atelier.product-facilitation-review/1`
record with `bundle_sha256`, `reviewer`, `verdict` (`approve` or
`changes-requested`), `summary` and one `checks` item per section
(`id`, `outcome` equal to `matches` or `needs-change`, and `observation`).

```sh
python3 -B "$TOOLS/product_facilitation.py" review --root "$PROJECT" \
  --projection tickets.json --input workshop/request.json \
  --review workshop/review.json --review-sha256 "$REVIEW_SHA"
```

Use `draft --require-ready` to stop with exit 3 while blocking questions remain.
The draft is still readable for the workshop. The review also exits 3 for an
open blocking decision or requested edits. Exit 2 means input drift, missing
bindings or an invalid record. The tool leaves the source, native scope
and prior records in place. Project authority and observed prototype behavior
are checked through the owning project’s process.
