# Route policy for material task records

The native host and user control permissions. This policy checks consistency after the integrator records relevant facts. Use it when a workflow has material dependencies, handoffs, or effects. A short local task can run directly with its ordinary check.

For new task records, add `routing.policy` to the existing `atelier.orchestrator-task/1` object. Do not retrofit new assertions into historical records.

| Field | What to record |
| --- | --- |
| `schema` | `atelier.orchestrator-policy/1` |
| `single_actor_sufficient` | Whether one current actor can deliver and verify the authorized scope. |
| `delegation_limit`, `planned_delegations` | The actual allowance and planned number of role calls. Use nonnegative integers. |
| `effect_class` | `read_only`, `local_reversible`, or `external`. Classify by the proposed operation, not the wording of the request. |
| `required_capability_gaps` | Observed gaps that prevent execution of this scope. Capabilities for optional later work belong in the follow-up. |
| `coordination_reason` | Required for `compose`. Use `independent_outputs`, `distinct_judgment`, or `independent_acceptance`. |
| `construction_basis` | Required for `create_agent`. Use `user_request` or `observed_reuse_gap`. |
| `effect_authority_ref` | Reference to the actual decision for this external target and operation. Required before recording execution. The reference is checked for presence only. |

Run `python3 -B scripts/check_routing.py TASK.json --ready` from the checked skill root. Resolve factual gaps against authoritative sources. If a dependent operation cannot run, an explicit bridge or prepared plan can still carry the remaining work. When an outside write has an unknown outcome, reconcile the target identity before dispatching it again.
