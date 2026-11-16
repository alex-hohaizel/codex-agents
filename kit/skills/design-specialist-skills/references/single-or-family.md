# One skill or a family

Estimate the actual scope before deciding how many files and roles are needed. Compare the options in the proposal.

An installable unit and a workflow phase are independent. One skill can lead multiple phases and multiple skills can contribute to the same phase. `architecture.kind=single` describes one module and can cover several stages. For `family`, explicitly define `architecture.modules`. Include at least two entries with a portable `name` and nonempty `stage_ids`. All IDs refer to the current DAG and together cover every phase. The same explicit single-module list is valid for `single`. When the list is omitted, the single-module decision covers its current phases. Derive the number of skills from independent responsibilities and reuse.

| Condition | Organization |
| --- | --- |
| One result, related sources and competencies, one acceptance process | One specialist skill with conditional branches |
| The approach needs to be chosen from meaningful alternatives | Separate research work or an explicit research phase |
| Implementation must consume exact approved rules, UI, data, or materials | A separate design or authoring handoff |
| Code, builds or production assets have their own long cycles | A separate implementation skill |
| Publishing has different credentials, owners, risks and external states | A separate deployment or operations phase |
| A small task with phases that have no separate reuse | One skill |

Justify each boundary with the stable artifact, consumer, decision already made, and the work that carries forward. Prefer the simpler arrangement when a boundary has no practical role.

Every handoff contains identity and version, the original brief and amendments, requirement coverage, exact artifacts and hashes, actual evidence, approved choices, rights, open issues, rejected alternatives, scope, and the next owner. Route changes to a shared contract to the affected owner and stages.

A weekly analysis report often fits one skill. A paid web service may need research, design, implementation, deployment and support when the user approved that scope. A prepared deployment checklist establishes preparation. Persistent monitoring and recurring operations require actual resources, a responsible owner, and permission.
