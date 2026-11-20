# Review an interactive UX prototype

Use the installed App Atelier Experience skill when a product decision depends
on what a person can actually do. Keep **DESIGN.md** (identity, visual tokens,
layout) and **EXPERIENCE.md** (tasks, rules, transitions, recovery, accessibility)
as separate reviewed sources. An imported mock or kept prototype may be a
third, explicitly pinned source. Record mismatches as decisions for the owner;
a prototype does not silently change either document.

## Describe the journey

The JSON input uses `codex-agents.ux-prototype/1`. Supply a stable `id`,
`title`, `summary`, BCP 47 language tag such as `en` or `uk`, and the
`start` screen ID. The `theme` object has six-digit hex `background`,
`surface`, `ink`, `accent`, and `onAccent` values. The builder checks
contrast for text and focus. Select actual reviewed product colors.

`sources` entries have `id`, `kind` (`design`, `experience`,
`requirement` or `decision`), project-relative `path`, and exact
`sha256`. Bind reviewed text, including at least one design and one experience
source. Use a literal `excerpt` from a pinned source each time a screen
`refs` entry names its `source` ID.

Each screen includes:
- Stable `id`, short walkthrough `label`, `heading`, and `body`.
- `state`: `normal`, `pending`, `conflict`, or `success`.
- Optional `details` of `label` and `value` pairs and optional `fields`.
  A field has an `id`, `label`, `type` (`text`, `check` or `choice`),
  optional `help`, and `options` for choices.
- `actions` with `id`, `label`, `to` screen ID, optional `style`
  (`primary` or `secondary`), and optional `requires` field IDs.
  Empty actions end a path. Give every screen a path to an ending and
  include a success ending. Model meaningful alternatives explicitly.

Use representative examples, failures, and recovery actions. Fields gate
simulated actions; field values are neither saved nor exported. The
walkthrough layout and engine UI are provided by the skill. For a design
that requires precise brand layout, motion, media or native interaction,
also produce and test the applicable client slice alongside this route.

## Build and test

Set `EXPERIENCE_SKILL` to the actual detected skill folder and `PROJECT`
to the reviewed project root. Before creating a walkthrough, record the
requirements, candidate approaches, and purpose of the experiment in the
[project's production choice](PRODUCTION_CHOICES.md). Choose a new local
destination every time a binding changes. The `verify` command still checks
exact bytes of an existing walkthrough against its original sources.

```sh
TOOLKIT_PYTHON="${AGENT_SYSTEM_PYTHON:-python3}"
"$TOOLKIT_PYTHON" -B "$EXPERIENCE_SKILL/scripts/ux_prototype.py" build \
  --root "$PROJECT" --input prototype.json --artifact "$ARTIFACT"
"$TOOLKIT_PYTHON" -B "$EXPERIENCE_SKILL/scripts/ux_prototype.py" verify \
  --root "$PROJECT" --input prototype.json --artifact "$ARTIFACT"
```

Open the generated HTML in the browser. Test the normal and blocked routes,
keyboard and focus, required input feedback, and the narrow target width.
Reload mid-path to check restoration in the same browser and artifact.
Use **Download walkthrough** to preserve screen and transition identities
with the exact source binding; it records a simulated run without owner
acceptance. Compare the real browser evidence to both reviewed documents.
A repeatable HTML build does not verify behavior. A narrow browser
emulation is separate from testing a physical target device.

When a design or experience source changes, review the changed excerpts and
restore a new binding before testing again. Keep the original walk and its
evidence attached to the original bytes. For product adoption, pass the
reviewed documents, exact artifact, observed receipt, device limits and any
remaining assumptions to the build and QA owners.

## Carry the accepted visual master into implementation

Save the editable master, styles, data or asset dependencies, and exact
interaction flow in the owning project. Pin the master and flows in the
production decision and pin their supporting files in its configuration.
Use the approval for that exact revision. Check the same files again
before handoff, repeat, implementation, or resumption.

```sh
"$TOOLKIT_PYTHON" -B "$EXPERIENCE_SKILL/scripts/ux_prototype.py" verify-master \
  --root "$PROJECT" --artifact "$PROJECT/design/review.html"
```

This check identifies the current decision, exact artifact and flow.
Demonstrate the real interaction in its intended browser or device and
record the actual observation separately. The
[Riverdesk and Riverlines examples](../../evaluations/fixtures/production-choice-web/requirements.md)
use the same source data with different reading orders, actions, and
interaction patterns.
