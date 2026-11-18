# Loading dock reservation pilot

Planning specification v0.1 for the buyer demonstration.

## User and pilot outcome

A dock coordinator repeatedly needs to find an available loading slot and obtain a reference for a confirmed reservation. The pilot covers viewing preloaded slots, confirming one slot, recovering a confirmation after a lost reply, and choosing another slot after a conflict.

## Owner requirements

| ID | Literal source excerpt | Pilot acceptance |
| --- | --- | --- |
| R-101 | “R-101: One available loading slot can have only one confirmed reservation.” [Owner notes, line 2](OWNER_NOTES.md#L2) | Two concurrent attempts for one available slot yield exactly one confirmation and one stored reservation for that slot. |
| R-102 | “R-102: Repeating the same request identity after a lost reply must return the original reservation reference.” [Owner notes, line 3](OWNER_NOTES.md#L3) | After a committed confirmation whose response is lost, the same coordinator resends the same request identity and slot and receives the exact original reference. The reservation count stays the same. |
| R-103 | “R-103: Another coordinator requesting the same slot receives a conflict and can choose another slot.” [Owner notes, line 4](OWNER_NOTES.md#L4) | A second coordinator receives an explicit slot conflict, sees the remaining available slots, and can confirm a different slot with a new request identity. |

## Coordinator workflow

1. View the available slots and select one. If the list is empty, show that no slots are available and offer refresh.
2. Submit the selection and show the confirmation reference when the service responds. If the outcome is unknown after a timeout or disconnect, keep the original slot and request identity and offer retry.
3. On a slot conflict, refresh availability, keep the coordinator in the selection flow, and let them submit a different slot with a new request identity. If refresh fails, show a retry action and leave the conflict visible.

## Pilot boundaries

The planning assumptions are a single pilot site, preloaded slots, identified coordinators with the same site access, one client reservation flow, and a shared reservation service. The target client platform and identity mechanism remain open. Slot administration, changes and cancellations, billing, notifications, and model-assisted features are outside this pilot. The owner retains the hosting-vendor and model-budget decisions. The service contract works without a model.

The buyer demonstration delivers local Markdown planning. Implementation, provider calls, deployment, tracker writes, and vendor selection are outside the authorized scope. The [architecture](ARCHITECTURE.md) defines the contract, future builder assignments, independent QA checks, and fresh-session checkpoint.
