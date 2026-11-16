# Discover and reuse specialists before creating capability

Before a new agent, family, engine, or material extension, recover the actual need and scope, then search for relevant current specialists. An available specialist introduced after this toolkit remains a candidate. Catalog examples are discovery hints, not a list of all candidates or proof of availability.

Search by competence, user job, input and output, and stage. Record the allowed scope, observed host sources, date, question and reason to stop. Respect excluded sources before reading them. Pass exclusions to the inventory tool through `--exclude-source`.

## Verify candidates on the intended host

In Work use supported skill listing and source reading. In Codex use current metadata and approved installed source directories. Historical chats, archives and exports can help locate a source but do not establish its current state. Read actual `SKILL.md` and required resources before selecting a candidate. Take identity from the opening frontmatter `name`. Record stable slug, host, source, known version or `unknown`, and SHA-256 of actual source and dependencies.

An optional `assets/capability-card.json` can describe capability, inputs, outputs, stages, compatibility, rights and limits. Check it against source. An absent or stale card does not disqualify a relevant candidate. Record `available` as visible current metadata, `installed` as verified installed source, and `source_checked` as the actual read. Invocation and successful effect are separate.

Record a counterpart on another host separately as unverified until its source and capability are confirmed there. A portable snapshot does not establish another host's installation, local files, credentials or allowed operations. Archived, uninstalled or disabled sources do not count as active. Resolve duplicate slugs against current host binding and provenance before selecting one. Version or date alone does not resolve the collision. Changed bytes reopen the affected choice and evidence.

## Compare fit and select a route

Compare actual capabilities, inputs, outputs, stages, compatibility, rights, limits, and need fit. Map them to requirement IDs and actual source sections and hashes. Check input maturity, consumer, entry and exit, host and tools, licenses and data, budget, effect, stop and acceptance.

| Decision | Required basis |
| --- | --- |
| `reuse` | One available candidate covers the scope. Record source pin, owned requirements and actual fit. |
| `compose` | Candidates provide complementary results with owners, exact interfaces, shared parent contracts and integration acceptance. |
| `extend` | An existing method covers the base. State the reusable part, exact unmet requirements, scope of change and authority. |
| `create_gap` | A bounded source-backed search leaves a specific gap, with compared alternatives and reasons. Unread, ambiguous or unknown options do not establish absence. |

An inaccessible but suitable specialist requires an exact bridge, rather than a duplicate. If a sufficient authorized embedded method exists, record `embedded_method`, its actual owner and source, and the same acceptance. Reuse grants no new rights to install, spend, share, publish or change a product.

For other-host shortlist cases distinguish `unknown`, `bridge`, `irrelevant` and `incompatible`. Cover the actual requested requirement IDs before excluding a candidate. Known unknowns and suitable bridges block an unsupported creation conclusion, while unrelated authorized work may continue. Cross-host composition needs separate verified host decisions and bounded launch and return records.

## Invoke and hand off

Use `@<frontmatter-name>` in Work and `$<frontmatter-name>` in Codex as supported by the actual host. Display version does not enter the selector. Pass parent intent and authority, requirements, scope and stop, exact inputs and hashes, write paths, output and consumer, interfaces, acceptance, budget, allowed effects, unresolved items, checkpoint, next action and `return_to`.

A planned call stays `planned`. `performed` requires an actual actor, source resolution and observed operation or output. For typed app, chatbot and agent skill components use [specialist orchestration](specialist-orchestration.md) and `atelier-component-handoff/1` checks where applicable. A different specialist uses a project-owned bounded contract and its own domain acceptance. Do not change a component kind to satisfy an unrelated validator. App and chatbot contributors to one product share its parent requirements, identity, data and API contracts.

## Local checks

```sh
python3 -B scripts/discover_specialists.py inventory --host codex --root /ACTUAL/APPROVED/INSTALLED/ROOT --metadata /PROJECT/current-skill-metadata.json
python3 -B scripts/discover_specialists.py check-decision INVENTORY.json DECISION.json
```

The inventory reads approved sources and prints JSON. Options `--root`, `--metadata`, `--exclude-source` and `--snapshot-root` may repeat. Use explicitly approved installed directories or exact skill folders. Read Work resource URIs through a supported reader. When permitted, save a copy below an approved snapshot directory and add its `source_snapshot` to metadata without replacing the actual URI. A snapshot is read evidence, not installed source. Current listing separately supplies `listed=true`.

Metadata can use `{"entries":[{"name":"future-spectrum-lab","host":"codex","source":"/APPROVED/future/SKILL.md","listed":true,"installed":true}]}`. Optional `version` and `sha256` identify expected source. `status=archived` excludes current selection. Other-host availability remains unverified pending actual checks.

A decision carries `decision`, `reason`, `search_scope`, `authority_ref`, `requirement_ids`, `selected` and `analyses`. Per candidate provide `candidate_id`, `source_sha256`, all eight fit dimensions, `fit=usable|extend|incompatible|unknown` and covered requirements. Include checked dependency `source_files` with paths and hashes. Duplicate resolution needs `identity_resolutions` with current-host `binding_ref` and reason. For `compose` include `interface_contract_ref`. For `extend` and `create_gap` include exact `gap_requirement_ids`. Analyze each active candidate in the bounded shortlist before claiming a gap. Use metadata to justify the shortlist rather than scanning a whole catalog.

For a known counterpart, supply `counterpart_assessments` with `candidate_id`, status and reason. For statuses other than unknown, include `need_fit`, considered `requirement_ids`, and `source_review` with exact host and reference and approved snapshot path and hash. Include a bounded `bridge_ref` for a bridge. Recheck actual bytes and required coverage before excluding a candidate.

The local checker revalidates shape and source bytes. The integrator confirms search sufficiency, subject fit, permissions and actual effects. Show a short result-to-source, inputs and authority, consumer, evidence and gap map. Use [research and synthesis](research-and-synthesis.md) for a domain gap rather than assuming a separate permanent role.
