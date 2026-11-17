# Preview and reconcile a mapped tracker tree

The ticket projection remains the project record. Choose one target container
and a retained mapping for that project. The tracker preview reads the
container and remote issues and compares the projection, prior observed
fields and current state. Review outbound actions, inbound proposals,
conflicts and unrelated objects before approving one effect.

Use the exact provider configuration and stable target controls in
[Tracker providers](TRACKER_PROVIDERS.md). Keep actual credentials and
approval/receipt files outside reusable packages. The auth object contains
environment variable names, not credential values.

A separate mapping file uses this shape:

```json
{
  "schema_version": "codex-agents.tracker-mapping/1",
  "project_id": "verified-release",
  "provider": "github",
  "container_id": "123456789",
  "statuses": {
    "planned": "open",
    "accepted": "closed:completed",
    "deferred": "closed:not_planned"
  },
  "tickets": [
    {
      "ticket_id": "INIT",
      "id": "98765432",
      "key": "17",
      "last": {"title": "Verify the release", "status": "open", "parent_id": null}
    }
  ]
}
```

Use immutable provider IDs and the provider's native selector for each status.
When mapping a preexisting object, review its exact repository/project/board,
identity and current state. Copy only observed baseline values into `last`.
A remote change by itself produces a proposal. It never closes an accepted
requirement or overwrites local project intent.

```sh
python3 -B scripts/tracker_sync.py preview --root "$PROJECT" \
  --projection tickets.json --config tracker/config.json --mapping tracker/mapping.json \
  > "$PROJECT/tracker/preview.json"
python3 -B scripts/tracker_sync.py apply --root "$PROJECT" \
  --preview tracker/preview.json --sha256 "$APPROVED_SHA" --action "$ACTION_ID"
python3 -B scripts/tracker_sync.py read-back --root "$PROJECT" \
  --preview tracker/preview.json --sha256 "$APPROVED_SHA" --action "$ACTION_ID"
```

Publish one reviewed effect per command. The preview puts parents before
children; a new child needs an observed parent and a provider that exposes
its parent relationship. Prepare the next preview after reviewing and
adopting a returned mapping candidate in the project-owned mapping file.
Create operations publish title and a stable marker. Apply the separate
status or parent update after the new identity is read back. Relationships
with missing mapped endpoints stay pending. Unsupported fields stay visible
rather than being removed from the project.

By design, this adapter stages inbound observations for review instead of
editing the native projection. Confirm conflicting or unsupported statuses,
and preserve unchanged `last` fields when accepting a partial observation.
Use the existing [GitHub-specific adapter](TICKET_GITHUB.md) for one already
mapped state, blocker or sub-issue change when it supports a route the tree
preview does not yet offer.

Save each original approval and the project-local journal under
`.atelier/tracker-sync/`. Before an external request, a durable journal
binds the effect to the checkout. After a failed or missing response, read
back the original approval, even if the local projection has moved on.
Restore the original provider config for that read. An unobserved effect is
pending and won't be resent by a refreshed approval for the same issue field
or creation marker. A separate writer can still change a tracker between
read and write; use one writer for a shared container. Unknown provider
effects and mapping repairs require operator reconciliation before another
write. The journal is checkout-local and is not a provider transaction.

Use `apply --retry-rejected` only when the previous journal records a
definite rejection. Prepare and review a fresh exact preview after fixing
the cause. The command rechecks the destination and retains the earlier
rejection in the journal. An uncertain response never takes this path.
