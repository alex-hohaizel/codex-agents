# Review source-bound PRD and architecture revisions

Use this workflow when a product-grade specification spans the product
requirements and architecture decisions. Keep the authored Markdown in the
project and run the commands from the reviewed Codex Agent System checkout.
Set `TOOLS="$PWD/scripts"`. Use the project’s native ticket projection, accepted raw sources and
current decisions. The helper checks what the documents cover and what a
requirement change affects.

Use these fields in a project-local `atelier.ticket-product-spec-manifest/1` object.

- `project_id`, `native_revision` and `projection_sha256` from the exact ticket projection
- `author` for the person or agent that prepared both documents
- `documents` with a `prd` and `architecture` path/SHA-256 pin for editable Markdown
- `sources`, `decision_sources` and `comparison_sources` arrays of path/SHA-256 pins.
  Use the last array when other teams maintain separate structured requirement
  registers. Use an empty array when there are none.
- `coverage` records with each native requirement `id`, `source_path`,
  a literal `source_excerpt` present in the raw source and the native rule,
  `decision_ids` for current decisions that the criterion depends on, and
  `prd_excerpt` and `architecture_excerpt` present in the actual companions

Include every applicable must and always-review criterion plus its requirement
dependencies. The product owner and architectural reviewer decide whether
the cited passages express the rule and its acceptance path.

```sh
python3 -B "$TOOLS/ticket_product_spec.py" capture --root "$PROJECT" \
  --projection tickets.json --input spec/manifest.json > "$RECORDS/spec-r1.json"
```

Keep the captured revision and its digest. After an authorized change, update
the native requirements and decisions, both Markdown documents and their
manifest. Compare the live candidate with the archived capture.

```sh
python3 -B "$TOOLS/ticket_product_spec.py" compare --root "$PROJECT" \
  --projection tickets.json --input spec/manifest.json \
  --before "$RECORDS/spec-r1.json" --before-sha256 "$PRIOR_CAPTURE_SHA"
```

The comparison reports impact from changed requirement content and from
changes to each ticket's effective requirements. A moved requirement can
affect two tickets even when both documents retain their original wording.

Give an independent reviewer the exact new bundle, original excerpts, decisions
and linked acceptance criteria. The reviewer returns a separate
`atelier.ticket-product-spec-review/1` object containing the capture's
`bundle_sha256`, `reviewer`, `verdict` (`approve` or
`changes-requested`), `summary`, and one check per requirement with
`id`, `outcome` (`matches` or `needs-change`) and `observation`.

```sh
python3 -B "$TOOLS/ticket_product_spec.py" review --root "$PROJECT" \
  --projection tickets.json --input spec/manifest.json \
  --review spec/independent-review.json --review-sha256 "$REVIEW_SHA"
```

A changed pin, omitted criterion or review for another bundle exits 2. A
well-formed `changes-requested` review exits 3 and lists its findings.
Review checks the relation between the captured files and declared results.
The established project process still confirms reviewer identity, owner
acceptance and observed application behavior. The CLI leaves project files
untouched.
