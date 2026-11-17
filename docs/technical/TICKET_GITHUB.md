# Reconcile a project ticket board with GitHub Issues

Use the project's local [ticket projection](TICKET_TREE.md) and explicitly
map its tickets to issues in a selected GitHub.com repository. Match the
repository and issue numeric IDs as well as the repository name and issue
number. This prevents an issue at the same number in another repository
from being treated as the selected issue.

Save the map as `github-issues.json` in the project. In this example use
the actual project ID, GitHub repository name and numeric IDs from the
authorized API response.

```json
{
  "schema_version": "atelier.ticket-github-map/1",
  "project_id": "quotes",
  "repository": {"full_name": "example-org/quotes", "id": 12345678},
  "tickets": [
    {"ticket_id": "QUOTE-API", "number": 42, "id": 90123456}
  ]
}
```

Run from the reviewed Codex Agent System checkout:

```sh
python3 -B scripts/ticket_github.py --root "$PROJECT" \
  --projection tickets.json --mapping github-issues.json --require-clean
```

Public issues can be read anonymously. For a private repository, supply
`GH_TOKEN` or `GITHUB_TOKEN` through the operator's existing environment
with read access to the selected repository and its issues. The adapter
uses GitHub.com's REST API and issues GET requests. Check the reported
HTTP status and request IDs when investigating a partial read.

Compare titles, open/closed state, blocked-by relationships and mapped
sub-issues. Read local acceptance and outside-scope remote relationships
in their own fields. A closed issue never serves as local acceptance
evidence. GitHub open corresponds to planned, in progress, in review or
blocked. A closure as completed corresponds to recorded acceptance and a
closure as not planned corresponds to deferral. Map connected tickets to
compare their links. An unmapped linked ticket, replaced issue identity, rate limit or
unavailable endpoint is visible in the report. Resolve differences using
the owning source before updating either system. The adapter does not
apply changes to GitHub or the local projection.

With `--require-clean` the command exits 2 for a difference or an incomplete
read. Without it, the command can return 0 for a complete read containing
differences. Use the `status` and per-ticket findings in both cases.

A report reflects multiple reads over its reported interval. If a decision
depends on the current tracker state, check the current issue before acting.
[GitHub issue endpoint](https://docs.github.com/en/rest/issues/issues#get-an-issue) ·
[Dependencies endpoint](https://docs.github.com/en/rest/issues/issue-dependencies#list-dependencies-an-issue-is-blocked-by) ·
[Sub-issues endpoint](https://docs.github.com/en/rest/issues/sub-issues#list-sub-issues)

## Apply a reviewed change to a mapped issue

Use `ticket_github_update.py` when the project owner has authorized one
outbound change. Supported changes are title, state, adding or removing a
blocker, and adding or removing a sub-issue. The adapter uses the project
projection and the existing mapping as its sources. A completed state
requires matching local acceptance evidence. For a blocker or child,
pass another mapped local ticket with `--related`.

```bash
python3 -B scripts/ticket_github_update.py preview --root "$PROJECT" \
  --projection tickets.json --mapping tracker/github.json \
  --ticket T-42 --change add-blocker --related T-19 \
  > "$PROJECT/tracker/change-preview.json"
```

Inspect the repository, stable issue IDs, proposed request and exact
GitHub state captured in the preview. Record the file SHA-256 with approval.
Then run one commit and check the reported state.

```bash
python3 -B scripts/ticket_github_update.py commit --root "$PROJECT" \
  --preview tracker/change-preview.json --sha256 "$APPROVED_SHA"
python3 -B scripts/ticket_github_update.py read-back --root "$PROJECT" \
  --preview tracker/change-preview.json --sha256 "$APPROVED_SHA"
```

The tool rechecks the local sources and current GitHub state before sending
the request. GitHub's supported write operations do not provide an atomic
comparison with the preview, so coordinate writers to the same issues.
The preview is bound to its original checkout. Keep the preview and
journal in that checkout for commit and read-back. A completed no-op also
records the observed state, so an older approval cannot replay later drift.
The local journal persists the attempt before the provider call. A
repeated command checks the destination after an uncertain result. Keep
that journal available when moving to another session. Resolve divergences
with the owner and inspect the authoritative issue before preparing a new
change. An explicit provider rejection has its own reviewed retry option.
