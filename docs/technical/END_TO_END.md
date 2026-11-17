# Build a reservation workflow with Codex

A warehouse team needs a small web app to reserve a loading dock. Two coordinators may choose the same slot. The system confirms one reservation, shows the other coordinator which slots remain, and lets that person try again. Use this example in a disposable project with placeholder users and slots. For an existing app, substitute its actual requirement and decision sources.

| Requirement | Observable result |
| --- | --- |
| `R-101` Reserve an available slot | The service records one reservation and returns its stable reference. Repeating the same request after a lost reply returns the same reference. |
| `R-102` Handle competing reservations | Two distinct coordinators request the same slot. One gets a confirmation. The other gets a conflict and can select another available slot. |
| `R-103` Make the choice and recovery accessible | At a 390-pixel browser width and by keyboard, a coordinator can complete the journey, see why a slot became unavailable, and reach the next action. |

## Start one coordinating conversation

Open Codex in the app's project folder. Call the optional Orchestrator if you installed it. You can also start with `$app-atelier-director`. Keep the coordinating chat for decisions and integration. Start workers in separate sessions when they need their own Git worktrees.

```text
$atelier-orchestrator

Coordinate a loading dock reservation pilot in the current project. The pilot has
one screen for choosing a slot and a recovery path when another person takes it.
Start with the project requirements, decisions, existing code, and current Git
commit. Use R-101, R-102, and R-103 from the worked example for an empty project.

Keep work in the local project until I identify a tracker target and authorize
individual changes. Prepare evidence for a release decision. Local preparation
is the current scope. Return the next decision and the project record I can
open to continue later.
```

Use the director to own the app lifecycle and choose the next stage. If the Codex host exposes the managed roles, give each role a scoped assignment. Otherwise use the matching skills or separate Codex sessions with the same input and ownership.

| Responsibility | Useful worker | Result for the coordinator |
| --- | --- | --- |
| App director | `$app-atelier-director` | Current project record, acceptance checks, named owners, and the next decision |
| Product | `foundry-product` or `$app-atelier-specification` | A brief and PRD that identify the coordinator, booking policy, and success criteria |
| Architecture | `foundry-architecture` with the specification skill | The API and data contract, including how the service enforces one winner and handles a replay |
| Experience | `$app-atelier-experience` | Reviewed design and experience documents, plus an interactive browser walkthrough |
| Build | Separate `$app-atelier-build` sessions | Independent commits for service behavior and the web flow, each with checks |
| Review | `$app-atelier-qa` or `foundry-qa` in an independent session | Observations against the integrated commit, including failure and recovery paths |
| Release | `$app-atelier-release` | An exact candidate and rollout plan for an owner decision |

Use the project's accepted language and preserve exact IDs through the handoffs. [Optional Orchestrator](../INSTALL.md#optional-components) · [Routes and subagents](../OPERATING_MODEL.md#routes-and-subagents) · [Managed role files](../../agent-profiles/manifest.json)

## Settle the rules and walk the experience

Keep interview notes and current decisions in the project. Ask product and architecture to settle the policy for a collision and a lost response. For this example, the owner accepts a single winner, replaying the same request identity returns its original result, and a second coordinator can choose a different slot. The director records that decision and links it to the relevant requirement IDs.

```text
Prepare the reservation PRD and architecture from the project notes and the
accepted booking rule. Cite the exact source passage for each requirement.
Keep the replay rule and the competing-request rule distinct. Show which part
of the contract the client can depend on while the service is still being built.

Ask Experience for separate DESIGN.md and EXPERIENCE.md documents. In the
browser walkthrough I want to choose a slot, submit it, encounter a conflict,
choose another slot, and reach confirmation. Include a pending screen and
make the conflict message and next action reachable by keyboard. Bind each
screen to the reviewed source passage.
```

Use product facilitation to draft a brief or PRFAQ and preserve the positions behind the decision. Use the template registry for a reviewed, repeatable document structure. Capture the PRD and architecture together so a change to the booking rule tells you which documents and tickets need attention. [Product facilitation](PRODUCT_FACILITATION.md) · [Document templates](DOCUMENT_TEMPLATES.md) · [PRD and architecture review](TICKET_PRODUCT_SPEC.md)

Walk the interactive HTML before implementation. Exercise confirmation and conflict, start from the keyboard, check focus and feedback at the narrow target width, and reload during one path. Save the downloaded walkthrough with its reviewed source pins. The walkthrough establishes which simulated transitions the team exercised. Test two real browser sessions against the integrated service later to establish the reservation behavior. [Build and test the prototype](UX_PROTOTYPE.md#build-and-test)

## Turn the decisions into work

Keep the ticket projection as the coordinating project record. Select one epic and two build tickets. Keep the shared API contract and integration changes with the coordinator.

| Ticket | Write ownership | Inputs and return |
| --- | --- | --- |
| `DOCK-API` | Service and service-test files for reservations | The accepted API contract and R-101/R-102. Return the service commit and the replay and collision check results. |
| `DOCK-WEB` | Web reservation UI and its own test files | The same API contract, walkthrough and R-102/R-103. Return the client commit and observations of the conflict and keyboard paths. |

Use the current projection to pick ready work. The web worker can use a fixture implementing the accepted responses until integration. Record the combined service and browser check as a dependency of acceptance. If the project changes to a temporary hold rather than a firm reservation, keep the old source and compare the revised rule against both tickets and their acceptance checks before updating the plan. Use the reviewed local replan if a current ticket needs to be split or replaced. [Project ticket tree](TICKET_TREE.md) · [Requirement change review](TICKET_CHANGE_REVIEW.md) · [Approved replan and Builder handoff](TICKET_REPLAN.md#hand-the-ready-ticket-to-builder)

If an external board is in scope, select one authorized provider container, set the mapping to the actual local project and stable remote IDs, and record already observed field values. Preview a single change to an existing ticket or the creation of `DOCK-API`. Review the target, marker and proposed effect. If an authorized writer applies it, read the result back and review the returned mapping before planning the next action. A changed tracker field comes back as an inbound proposal to the project owner. In the event of a lost response, read back the original approval and keep an unknown operation pending. [Tracker configuration](TRACKER_PROVIDERS.md) · [Preview, apply and read-back commands](TRACKER_SYNC.md)

```text
Prepare the two ready tickets and handoffs for the same Git base. For each,
show the requirement IDs, exact source paths, writable files and starting
bytes, observable acceptance check, and where the worker returns its result.
Keep the shared API contract with the coordinator.

If I give you an authorized tracker project, preview one separate outbound
effect against its stable ID. Bring me the exact proposed effect and its
read-back plan before any write.
```

## Build in two worktrees and resume one

Follow the worktree guide to prepare each binding at the same Git base and check it against its Builder handoff. Choose actual file paths from the project. Configure the host's writable scope for each worker. Start one worker per worktree and keep binding files and interruption records where the workers cannot edit them. [Prepare an independent assignment](TICKET_WORKTREES.md#prepare-an-independent-assignment)

```text
Service Builder, use the admitted DOCK-API worktree and its recorded write
paths. Implement the accepted reservation and replay contract. Exercise one
successful call, a retry with the same request identity, and two distinct
requests for the same slot. Return the exact commit and each observed result
to the coordinator.

Web Builder, use the admitted DOCK-WEB worktree and its recorded write paths.
Use the reviewed UX and API contract to implement the pending, conflict,
recovery, and confirmation states. Report your commit and the checks you
could observe on the exact client. Keep any service assumptions explicit.
```

Suppose the web session stops after adding the conflict screen. Check the original worker's state on the host. Once the worker has stopped and its effects are reconciled, capture the interruption and preserved local edits with the existing checkpoint commands. If the work has a dispatch reservation, use its documented continuation procedure. Open the fresh worker on the same worktree and verify the checkpoint before continuing.

```text
Resume DOCK-WEB from its existing worktree and saved interruption checkpoint.
Verify the exact checkpoint, expected Git base and writable files. Read the
persisted conflict screen. Continue at the next action recorded in the
checkpoint and return the exact result to the coordinating conversation.
```

The coordinator validates each returned commit, previews integration in a clean third worktree and reads back the combined commit. Keep the pre-integration returns so the reviewer can identify which change affected any failing check. [Capture and resume a checkpoint](TICKET_WORKTREES.md#resume-after-a-confirmed-interruption) · [Continue a reserved worktree](TICKET_WORKTREES.md#continue-a-reserved-worktree-after-a-confirmed-interruption) · [Review and integrate](TICKET_WORKTREES.md#review-and-integrate-the-exact-returns)

## Review the candidate and hand over a release decision

Ask QA to run the combined service and browser with separate placeholder users. With both tabs on the same slot, send the two distinct requests concurrently. Confirm one stored reservation, the losing tab's recovery action, and successful selection of another slot. In the local test harness, drop the first successful reply and replay the original request identity. Check that the stored reservation and returned reference remain the same. Walk the client by keyboard at the target width. Attach the exact candidate, requirements, environment, fixture, and observed artifacts to the review.

```text
$app-atelier-qa

Review the integrated reservation candidate as an independent reviewer. Use
the exact Git commit, accepted PRD, architecture, design and experience
documents, and R-101 through R-103. Check both browser sessions against the
same service, the lost-response replay, and keyboard recovery at 390 pixels.
Return the expected and observed result and its artifact for each case. Mark
unobserved cases and unresolved external effects explicitly.
```

Run the quality gate with the pinned plan and the independent review. A tracker status and a screenshot of the prototype are useful evidence at their own scope. The release owner needs current evidence from the integrated candidate. Retain the proof, decision and open checks for the next session. Prepare the exact version, delivery target and rollback with App Atelier Release. Submit to the named target only within the owner's release authorization, then read the actual target back. [Candidate evidence gate](TICKET_QUALITY_GATE.md) · [App Atelier Release](../../kit/skills/app-atelier-release/SKILL.md)

## Reuse a specialist when the work recurs

The app project can keep its review rubric. If several apps repeatedly need the same link between a reservation rule, API replay behavior, and observed browser recovery, ask Agent Foundry to construct a read-only reviewer with that focused responsibility. A specialist should request a change in the product record when it finds a discrepancy and return the evidence to the actual owner.

```text
$agent-foundry

Design a reusable read-only Reservation Review specialist for apps that book
one resource at a time. It receives a project root, current requirement IDs,
the reviewed reservation and replay rules, and an exact candidate with test
observations. It returns one finding per requirement with source, observation,
and suggested next check. Use example data and return the investigation to
the project owner when a required source or test observation is missing.

Show me the passport, including scope, allowed reads, the return format, and
acceptance cases for the single winner, a lost reply, a conflict that recovers,
and a stale candidate. Wait for the passport decision before construction.
```

Once the owner approves the passport, build and stage the package through Foundry's documented route. In a fresh Codex session, run the specialist on this pilot. Then give it a stale candidate and check that it leaves the affected requirement open. Use actual discovery, observed review output and the owner's adoption decision to establish that the package is ready for later projects. [Agent Foundry passport, build and verification](../../kit/skills/agent-foundry/SKILL.md) · [Native installation and discovery](../INSTALL.md#verify)
