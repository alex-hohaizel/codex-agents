# Loading dock reservation architecture

Planning specification v0.1. The [PRD](PRD.md) owns the literal requirement trace. The contract below maps those requirements to storage, API behavior, and observable QA checks.

## Data and access

Use a shared transactional store so coordinators see one authoritative booking outcome. A database constraint enforces the slot invariant even when requests arrive concurrently.

| Record | Minimum fields and constraints |
| --- | --- |
| Slot | `slot_id` primary key, `starts_at` and `ends_at` as UTC timestamps, with start before end. The pilot uses a preloaded catalog. A slot is available when no reservation references it. |
| Reservation | `reservation_ref` opaque primary key, `slot_id` foreign key and unique, `coordinator_id` from authenticated identity, and `request_id`. The pair `(coordinator_id, request_id)` is unique. Each row is a confirmation. |

Authenticated pilot coordinators can list available slots and request a reservation. They can recover their own confirmation with its original request identity and slot. A different coordinator using the same request ID is in a separate identity namespace. No reservation lookup endpoint is exposed. Availability and conflict responses expose neither the winning coordinator nor their reference. Keep confirmation and replay fields for the pilot lifetime to support recovery. Define any longer retention before a live pilot.

## API v1

All endpoints require a verified coordinator principal with pilot access. The service derives coordinator identity from that principal.

- `GET /v1/slots?status=available` returns `200` with `{"slots":[{"slot_id":"S1","starts_at":"2026-12-01T09:00:00Z","ends_at":"2026-12-01T09:30:00Z"}]}`. An empty result uses `"slots":[]`. Availability is a snapshot, so a listed slot can be taken before submission.
- `POST /v1/reservations` takes `Idempotency-Key: <UUID>` and `{"slot_id":"S1"}`. A new confirmation returns `201` with `{"reservation_ref":"<opaque reference>","slot_id":"S1"}`. A replay returns `200` with the same fields and exact original values.
- Errors use `{"code":"<stable code>"}`. Return `400 INVALID_REQUEST` for missing or malformed input, `401 UNAUTHENTICATED` for missing or invalid authentication, `403 FORBIDDEN` for an authenticated principal without pilot access, and `404 SLOT_NOT_FOUND` for an unknown slot on a fresh request.
- Return `409 SLOT_TAKEN` when a different request already confirmed that slot. Return `409 REQUEST_ID_REUSED` when a successful request identity is reused for a different slot by the same coordinator. The client refreshes availability for `SLOT_TAKEN`. It treats `REQUEST_ID_REUSED` as a request-state error and keeps the prior attempt available for recovery.
- A transient service or commit uncertainty returns `503 TEMPORARILY_UNAVAILABLE` when a response is possible. On a 503, timeout, or connection drop, the client resends the original slot and key. It persists the pending pair in coordinator-scoped client storage before sending so a reload can recover it. A deliberate new selection uses a fresh key.

## Reservation transaction

1. After authorization and input validation, look up the coordinator and request ID. An existing row with the same slot returns the original reference. An existing row with a different slot returns `REQUEST_ID_REUSED`. This check precedes slot availability (R-102).
2. For a fresh identity, verify the slot exists and insert the confirmed row in a transaction. The same row binds the slot and request identity. Return `201` only after commit. The unique slot constraint is the final arbiter (R-101).
3. If an insert hits a uniqueness conflict, roll back the attempted write and use a fresh authoritative read after the competing transaction resolves. Check request identity first and apply step 1 if found. Otherwise a confirmed row for the requested slot yields `SLOT_TAKEN` (R-103). If no committed outcome can be established, return the retryable error. A rejected attempt creates no reservation or replay record.

## Future builder split

| Builder | Owned scope | Handoff and proof |
| --- | --- | --- |
| Builder 1 | Storage schema, constraints, transaction and replay logic, authorization, and both v1 endpoints. | Owns service files and provides a local fixture service, contract examples, and a lost-response fault hook for QA. Demonstrates committed row counts and response behavior. |
| Builder 2 | Coordinator client, available-slot view, pending request persistence, confirmation, and conflict/retry flow. | Owns client files and can start from the v1 examples. Integrates against Builder 1’s fixture service and demonstrates recovery and alternative-slot selection through the client. |

Builder 1 owns contract integration. Both builders review any interface changes before integration and update the same v1 contract and fixtures. The first build slice, if later authorized, uses two coordinators and two seeded slots. QA has its own reviewer and returns findings to both builders for repair and retest.

## Independent QA plan

Use a clean fixture per case with authenticated coordinators A and B, available slots S1 and S2, and an empty reservation table. Use distinct UUIDs unless a case intentionally repeats a key. The reviewer must be someone other than either builder. Capture case ID, exact artifact revision, request and response evidence, reservation counts, and the client result where applicable.

| Case | Setup and action | Expected evidence |
| --- | --- | --- |
| QA-101 · R-101 | Submit A and B's distinct requests for S1 concurrently. | Exactly one `201`, one `409 SLOT_TAKEN`, and one confirmed S1 row. No second reference is issued. |
| QA-102 · R-102 | Let A's S1 request commit, capture its reference with the fault hook, and drop the response before it reaches the client. Reload the client and retry A's original slot and key. | `200` with the captured reference. The coordinator sees confirmation and there is still one S1 row. |
| QA-103 · R-103 | Confirm S1 as A. Have B act on an earlier list that included S1, deliberately using the same UUID as A. Then choose S2 with a fresh UUID. | B sees `409 SLOT_TAKEN` without A's reference. Refresh omits S1 and offers S2. B receives `201` for S2, with one row per slot. |
| QA-104 · R-102 | After A confirms S1, submit S2 as A with the same key. | `409 REQUEST_ID_REUSED`, no write to S2, and A can still recover the original S1 reference. |
| QA-105 · R-101/R-102 | Send two overlapping copies of A's same S1 request. Separately, force a failure before commit and retry the original request from a clean fixture. | Overlapping copies yield one `201` and one `200` with matching references and one row. Pre-commit failure leaves zero rows and the retry creates exactly one confirmation. |
| QA-106 · Access and input | Try a reservation with missing credentials, with authenticated non-pilot credentials, with a malformed key, and with an unknown slot. As B, attempt to look up A’s reference directly. | Respectively `401`, `403`, `400`, and `404`, with no writes. Direct lookup has no route and exposes no record. |

## Fresh-session checkpoint

- **Project and sources.** Resume in this Dock Planning folder. Read [OWNER_NOTES.md](OWNER_NOTES.md) first, then [PRD.md](PRD.md) and this v0.1 contract. The owner notes SHA-256 is `aeda2b41de3d8627dc2ff1ed1d990f1f6da7f7672db2a5e5abb54ac41345dfbd`. If the source changes, reconcile the literal trace and revisit the affected contract and QA cases before relying on this revision.
- **Evidence.** Local planning artifacts authored using installed Atelier Orchestrator 1.5.0 and App Atelier Specification 6.4.0. Independent review, runtime QA, owner acceptance, and release acceptance are pending.
- **Open decisions.** The owner still holds hosting vendor and model budget. Client platform, pilot identity wiring, and retention beyond the pilot are open planning dependencies for a future build. The local contract review can proceed without these decisions.
- **Next action.** Reconcile R-101 through R-103 against the two documents and walk through QA-101 through QA-106 with the synthetic fixtures. Record any findings against the affected requirement and section. Local planning is the current authority. Builder assignments and runtime QA become actionable only with separate build authorization. Provider calls, deployment, vendor selection, and tracker writes remain outside scope.
