# Tracker provider configuration

Use an explicitly authorized repository, project, data source, or board with [tracker sync](TRACKER_SYNC.md). Keep its configuration and mapping inside the project. Each operation checks the container's stable remote ID and any configured display or route key. Configure the credential environment variable names and supply the values to the process separately. An ordinary GitHub public read can use an empty auth object.

The mapping uses the provider's stable item IDs and lookup keys. A title, a short URL, or a matching issue number in another project cannot identify an item. A Notion database ID does not substitute for its data source ID. A Trello move verifies the target list against the authorized board. Read/write permissions and a provider's configured workflows, labels, or relation properties determine which requests succeed.

| Provider | Container ID and optional key | Authentication and options | Native item status selector |
| --- | --- | --- | --- |
| GitHub | Numeric repository ID and required `owner/repository` key | Optional `auth.token_env`. Use `options.initiatives` can be `milestones` or `issues`, the default | `open`, `closed:completed`, `closed:not_planned`. Milestones use `open` and `closed:completed` |
| Linear | Project UUID and optional project `slugId` | `auth.token_env`. Use `options.auth_mode` is `api-key` or `oauth`. A project team UUID in `options.team_id` enables creation | Workflow state UUID |
| Jira Cloud | Numeric project ID and optional project key | `auth.token_env`, `auth.email_env`, and the tenant subdomain in `options.site`. Use `options.cloud_id` with a scoped API token | Numeric destination status ID, with one currently available workflow transition required |
| Notion | Data source UUID and optional parent database UUID | `auth.token_env` and `options.properties` for an existing data source schema. Default status property type is `status`, or configure `options.status_type` as `select` | Existing status or select name, resolved to the exact option ID before the write |
| Trello | Board ObjectId and optional board shortLink | `auth.key_env` and `auth.token_env`. Use `options.auth_mode` may be `oauth`, which uses `auth.token_env` alone | Active list ObjectId or `archived` |

The allowed credential variable prefixes are `GITHUB_` or `GH_`, `LINEAR_`, `JIRA_` or `ATLASSIAN_`, `NOTION_`, and `TRELLO_`. Token variables end in `_TOKEN` or `_API_KEY`. Jira email variables end in `_EMAIL` and Trello key variables end in `_KEY`. Use a credential scoped to the operation. The CLI derives the API host from the provider and the validated Jira tenant configuration. Request receipts record the operation name, status, and available request ID.

## GitHub Issues

```json
{
  "provider": "github",
  "container": {"id": "700", "key": "example-org/venue-booking"},
  "auth": {"token_env": "GH_TOKEN"},
  "options": {"initiatives": "milestones"}
}
```

Issue IDs and issue-number keys are decimal strings. With milestone representation enabled, an initiative can be created as a native milestone. Its stable ID and key use `milestone:<id>` and `milestone:<number>`, respectively. The provider checks the repository for both item types. A milestone can be selected as an issue's top-level parent through its native issue milestone assignment. A native sub-issue parent takes priority when both associations exist. Check existing milestone use before enabling this option.

Issue creation records the marker in the body. To assign a parent, blocker, or final status, map the new issue first and review the next operation. Native sub-issue and blocked-by APIs handle relationships. A milestone has title and open/closed state, with no native blocker list or assignees. The adapter uses the textual state of an issue. Map multiple local in-progress stages to `open` if they share that issue state. [Issues](https://docs.github.com/en/rest/issues/issues) · [Sub-issues](https://docs.github.com/en/rest/issues/sub-issues) · [Issue dependencies](https://docs.github.com/en/rest/issues/issue-dependencies) · [Milestones](https://docs.github.com/en/rest/issues/milestones)

## Linear

```json
{
  "provider": "linear",
  "container": {"id": "00000000-0000-0000-0000-000000000001"},
  "auth": {"token_env": "LINEAR_API_KEY"},
  "options": {"team_id": "00000000-0000-0000-0000-000000000002"}
}
```

Use the issue UUID for identity and its identifier such as `OPS-12` for the lookup key. The client reads the exact project's issue connection, including archived issues. Before creation, it confirms that the configured team belongs to the project. A project can use more than one team. Configure the team whose workflow states you mapped. The description carries the marker. Sub-issues use Linear's native parent field and blockers use incoming native `blocks` relationships. [Linear GraphQL guide](https://linear.app/developers/graphql) · [Linear GraphQL schema](https://github.com/linear/linear/blob/master/packages/sdk/src/schema.graphql)

## Jira Cloud

```json
{
  "provider": "jira",
  "container": {"id": "730", "key": "OPS"},
  "auth": {"token_env": "JIRA_TOKEN", "email_env": "JIRA_EMAIL"},
  "options": {
    "site": "example",
    "issue_types": {"initiative": "10010", "epic": "10001", "story": "10002",
                    "bug": "10003", "spike": "10004"},
    "block_link_type_id": "10000"
  }
}
```

Without `cloud_id`, the request goes to the site's Atlassian Cloud host. Specify a verified UUID `cloud_id` to use the Atlassian gateway for a scoped API token. An issue uses a numeric immutable ID and a human-readable project issue key. Configure actual issue type IDs for creation. A `default` option can cover otherwise unmapped types. Use the actual Jira hierarchy and required fields when testing that type in the project.

The marker is a Jira issue label. A status change first reads available transitions and requires one exact destination match. Blockers require the configured native issue link type and verified inward label. Configure `block_link_inward` if the Jira site names the inward direction differently from `is blocked by`. [Jira issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/) · [Search](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/) · [Link direction](https://developer.atlassian.com/cloud/jira/platform/issue-linking-model/) · [Scoped credentials](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

## Notion

```json
{
  "provider": "notion",
  "container": {
    "id": "00000000-0000-0000-0000-000000000008",
    "key": "00000000-0000-0000-0000-000000000009"
  },
  "auth": {"token_env": "NOTION_TOKEN"},
  "options": {
    "properties": {
      "title": "Name", "status": "Workflow", "marker": "Sync key",
      "parent": "Parent", "blockers": "Blocked by", "assignees": "Owner",
      "kind": "Ticket type", "description": "Description"
    }
  }
}
```

The API version is `2025-09-03`. Page identities and lookup keys use page UUIDs. Provide the title, status and dedicated rich text marker properties. The other properties are optional. Parent and blocker mappings use relation properties on the same data source. The assignee mapping uses people, kind uses select and description uses rich text. Configure selectors with existing property names or IDs. The Notion integration needs access to the data source and to read the resolved relation values. [Query a data source](https://developers.notion.com/reference/query-a-data-source) · [Data source properties](https://developers.notion.com/reference/property-object)

## Trello

```json
{
  "provider": "trello",
  "container": {"id": "000000000000000000000014", "key": "boardlink"},
  "auth": {"key_env": "TRELLO_KEY", "token_env": "TRELLO_TOKEN"},
  "options": {
    "default_list_id": "000000000000000000000016",
    "lists_by_kind": {
      "initiative": "000000000000000000000017",
      "epic": "000000000000000000000018"
    }
  }
}
```

Cards use the full ObjectId and shortLink. Assign the lists for new initiatives and epics and the default list for other cards. A status change moves the card to a verified list or archives it. Parent and blocker links live in a managed Markdown section at the end of the card description. The adapter reads the card immediately before editing its links and preserves the rest of the description. A well-formed section uses a full stable card ID and its corresponding Trello short-link URL. [Card API](https://developer.atlassian.com/cloud/trello/rest/api-group-cards/) · [Board API](https://developer.atlassian.com/cloud/trello/rest/api-group-boards/) · [Authorization](https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/)

## Read back an interrupted request

The tracker command writes an attempt receipt before sending an approved change. Read back the same container and issue after timeouts. For creates, look for the operation marker in the authorized container. The provider may take time to include a newly created item in a paginated list. Multiple marker matches need manual resolution. A create whose result is still unknown remains pending. Provider contract tests replay read, create, update and lost-response exchanges against protocol fixtures. An authenticated workspace test also needs the matching project, schema and rights.
