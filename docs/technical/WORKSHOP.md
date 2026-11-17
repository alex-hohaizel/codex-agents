# Facilitate a workshop across Codex sessions

Start with a concrete decision and the people it affects. Use a brainstorming
round to develop options, then invite a different perspective to challenge
the weakest assumption. For a pressure test, retain the questions, answers
and the evidence that changed the recommendation. Use the
[team deliberation guide](../../optional-skills/atelier-orchestrator/references/team-deliberation.md)
when the work benefits from real independent roles.

`scripts/workshop.py` reads the BMad brainstorming and advanced elicitation
CSV formats used by stable 6.12.4 and the reviewed v7 preview. Supply the
catalog as a project file and verify its digest from a trusted source. The
[stable brainstorming catalog](https://github.com/bmad-code-org/BMAD-METHOD/blob/bab9082c3e884e0d72c759bcd1a6d90bcc01be84/src/core-skills/bmad-brainstorming/assets/brain-methods.csv),
[stable elicitation catalog](https://github.com/bmad-code-org/BMAD-METHOD/blob/bab9082c3e884e0d72c759bcd1a6d90bcc01be84/src/core-skills/bmad-advanced-elicitation/assets/methods.csv),
and [preview elicitation catalog](https://github.com/bmad-code-org/BMAD-METHOD/blob/e435a22574fe55722841086e5566420178b98df3/skills/core-tools/bmad-advanced-elicitation/assets/methods.csv)
use their original field names. The catalog view retains the technique,
category or direction, output format, and the audience or goal metadata
where supplied. Use `--goal` to narrow the view by a catalog tag or category.
Omit it to review all techniques suitable for the audience.

Run the tools from the distribution checkout. In these examples
`PROJECT` is the workspace root and `CATALOG_SHA` is the reviewed SHA-256.

```bash
TOOLS="$PWD/scripts"
python3 -B "$TOOLS/workshop.py" catalog --root "$PROJECT" \
  --catalog planning/methods.csv --catalog-sha256 "$CATALOG_SHA" \
  --audience group

python3 -B "$TOOLS/workshop.py" start --root "$PROJECT" \
  --catalog planning/methods.csv --catalog-sha256 "$CATALOG_SHA" \
  --mode pressure-test --audience group --limit 6 \
  --goal "Decide whether the receipt recovery workflow is ready" \
  --evidence planning/receipt-requirements.md > "$PROJECT/planning/workshop-r0.json"
```

Keep a revision for each completed round. A round record has a `method` from
the exact catalog, `actor`, `topic`, `question`, `response`, and `ideas`.
Each new idea has a stable `id` and `text`. Use a different technique
when it helps move from exploration to comparison. A fresh facilitator can
read the exact latest state and ask the next question using the same evidence.

```bash
python3 -B "$TOOLS/workshop.py" append --root "$PROJECT" \
  --state planning/workshop-r0.json --state-sha256 "$R0_SHA" \
  --record planning/round-1.json > "$PROJECT/planning/workshop-r1.json"
```

When a decision is made, record `decided_by` and a `decisions` array. Include
each idea ID with its `outcome` (`continue`, `reframe`, or `drop`) and a
`reason`. Use the latest state and its SHA-256 with `decide`, then pass the
new state and digest to `report`. Each change returns a new revision to
stdout. Keep the old revision and share the new path and digest with the
next facilitator. The tool checks the selected catalog, evidence,
round budget and decision completeness. Publication and implementation
follow the project's normal approval and verification path.

```bash
python3 -B "$TOOLS/workshop.py" decide --root "$PROJECT" \
  --state planning/workshop-r1.json --state-sha256 "$R1_SHA" \
  --record planning/decisions.json > "$PROJECT/planning/workshop-r2.json"
python3 -B "$TOOLS/workshop.py" report --root "$PROJECT" \
  --state planning/workshop-r2.json --state-sha256 "$R2_SHA" \
  --format html > "$PROJECT/planning/workshop.html"
```

Use `--format markdown` when continuing the work in a brief or project issue.
