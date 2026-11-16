# Conversational assistant profile

Refresh the profile for a major round and after release changes. Keep changing commit and service IDs in project records and omit secrets. Extend this inventory to the actual domain.

For each capability record the user's goal, natural request, tool/route, source path, storage, ownership and audience, result, failure/retry/cancel, test and status (`declared`, `implemented`, `locally_verified`, `deployed`, `observed`). Review registries, schemas, callbacks, workers, UI, commits and release notes to find the full current scope:

- Name, mention, reply and continuation, addressee, silence, useful initiative, tone and humor, and brief or detailed replies.
- Group and topic memory isolation, authorship and sources, consent, pause and forget, summaries and recall, private DM and permitted group visibility.
- Notes, tasks, shopping, inventory, expenses and receipts. Distinguish a list from an actual purchase.
- Single and recurring reminders, local time, skip, reschedule and overdue behavior, calendar access, events and group coordination.
- Games, scenarios and roles, all required participant choices, serial and parallel activity, results, polls, buttons, offers and details.
- Current web/search and browser interfaces, private connectors and authority for external actions.
- Photo, sticker and avatar work, OCR, pages and video segments, catalog, versions, originals, collage/cards and image generation.
- PDF/DOCX/XLSX reading, creation and edits, albums, video, captions, music and sound. Record deferred or unavailable features separately.
- Learning, exercises and progress, group projects, private drafts and inbox.
- Selected platform ingress and egress limits, idempotency, retries, workers, queues, cancel, receipts, restart and leases.
- Models and authorization, allowed providers, CPU/RAM/disk, TTL and cleanup, health and telemetry, versions, release and rollback.

## Domain distinctions

1. «Додай молоко» refers to a list entry. «Завтра нагадай купити» refers to a reminder. Infer the natural intent without asking users to select an internal entity.
2. Verify permissions independently from name or administrative title. The output and notification follow the same allowed audience.
3. An artifact in storage still needs an accessible output or explicit access point in chat. Verify delivery or report its unknown status.
4. «Зробити відео» can mean montage or new generation. If context leaves a material choice, ask one deciding question. Check authority for paid generation separately.
5. Intent, consent, execution, verified result and delivery are separate. Reflect actual state in the response.
6. Free tools also use CPU and disk. Confirm paid provider scope and explain the limits that matter to the user's decision.

## Specialist sources

Verify the selected platform's primary APIs, FFmpeg manuals, applicable Node, database and queue documentation, model APIs and runtime contracts. Progressive disclosure, error recovery and turn-taking research inform design. Verify the bot's experience and runtime through target-specific observation.
