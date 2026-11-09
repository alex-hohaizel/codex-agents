import type { Bootstrap, Workspace, Data, Project } from "./api";

const project = (
  id: string,
  name: string,
  kind: string,
  phase: string,
  summary: string,
): Project => ({
  id,
  name,
  kind,
  phase,
  summary,
  root: `/example/${id}`,
  revision: "example-revision",
  status: "source_only",
  capabilities: {
    read: true,
    execution: false,
    reason: "Fictional example workspace",
  },
});
export const demoProjects = [
  project(
    "global-logistics",
    "Global Logistics",
    "application",
    "contract_review",
    "API contracts, service boundaries and integration compatibility.",
  ),
  project(
    "copper-support",
    "Copper · Support",
    "chatbot",
    "conversation_review",
    "A support agent with scoped knowledge and explicit action contracts.",
  ),
  project(
    "cedar-trail",
    "Cedar Trail",
    "game",
    "fidelity_slice",
    "An exploration game: one accepted identity across world, sound and interaction.",
  ),
  project(
    "signal-research",
    "Signal Research",
    "research",
    "evidence_synthesis",
    "Research questions, source quality, counterevidence and decisions.",
  ),
  project(
    "field-report",
    "Field Notes",
    "document",
    "editorial_review",
    "A concise report with source-backed graphics and a reusable editorial system.",
  ),
];

export const shipmentContract = `openapi: "3.1.0"
info:
  title: Shipment service
  version: "1.3.0"
paths:
  /shipments:
    post:
      operationId: createShipment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [orderId, weight, cargoType]
              properties:
                orderId: { type: string }
                weight: { type: string }
                cargoType: { type: string }
      responses:
        "201":
          description: Shipment created`;

const sampleReqs: Data[] = [
  {
    id: "API-01",
    title: "Contract and service accept the same weight type",
    priority: "must",
    status: "needs_review",
    source: "shipment-api.yaml",
    acceptance:
      "A valid numeric weight is accepted; invalid types have a stable error.",
    dependencies: ["shipment-api.yaml", "createShipment"],
  },
  {
    id: "API-02",
    title: "Existing consumers retain compatible behavior",
    priority: "must",
    status: "pending",
    source: "accepted-scope.md",
    acceptance: "Versioned clients and error payloads remain compatible.",
  },
  {
    id: "OPS-01",
    title: "A retry cannot create a duplicate shipment",
    priority: "must",
    status: "not_tested",
    source: "accepted-scope.md",
    acceptance: "Repeated action identity returns the original outcome.",
  },
  {
    id: "REL-01",
    title: "Independent review before release",
    priority: "must",
    status: "pending",
    source: "release-contract.md",
    acceptance: "A reviewer checks the exact source and affected clients.",
  },
];

const sampleJob: Data = {
  id: "example-contract-review",
  title: "Service contract review",
  objective:
    "Review the shipment service contract and prepare a compatible change.",
  status: "review_pending",
  scope: "read-only",
  project_id: "global-logistics",
  created_at: "2026-11-09T10:00:00Z",
  note: "Illustrative record. No actual execution occurred.",
  output:
    "Contract mismatch: `weight` is declared as string, while the request uses a number. Align the contract, then verify the affected consumers and validation behavior.",
  events: [
    { type: "example/source", message: "shipment-api.yaml · v1.3.0" },
    { type: "example/finding", message: "API-01: weight type mismatch" },
    {
      type: "example/review",
      message: "The proposed change requires independent review.",
    },
  ],
};

export const demoBootstrap: Bootstrap = {
  version: "Example",
  instance_id: "fictional-example",
  csrf_token: "",
  locale: "uk",
  projects: demoProjects,
  jobs: [sampleJob],
  skills: {
    summary: { count: 4, installed: 0 },
    entries: [
      {
        name: "platform-architect",
        display_name: "Platform architect",
        description:
          "Service boundaries, API contracts, compatibility and integration design.",
        version: "example",
        scope: "example",
        status: "example_only",
      },
      {
        name: "api-contract-review",
        display_name: "API contract review",
        description:
          "Compare the contract, request, response and affected consumers.",
        version: "example",
        scope: "example",
        status: "example_only",
      },
      {
        name: "integration-quality",
        display_name: "Integration quality",
        description:
          "Readiness across source, code, runtime and independent review.",
        version: "example",
        scope: "example",
        status: "example_only",
      },
      {
        name: "product-continuity",
        display_name: "Product continuity",
        description: "Accepted intent, identity, decisions and exact handoffs.",
        version: "example",
        scope: "example",
        status: "example_only",
      },
    ],
  },
  capabilities: {
    codex: {
      status: "example_only",
      message: "No executor in demonstration mode",
    },
    work: { status: "deferred" },
  },
  activity: [
    {
      id: "example-finding",
      title: "Contract mismatch",
      type: "example",
      status: "needs_review",
      message: "API-01 · shipment-api.yaml",
    },
    {
      id: "example-source",
      title: "Source attached",
      type: "example",
      status: "source_only",
      message: "Example service contract · v1.3.0",
    },
  ],
  metrics: {},
};

export function demoWorkspace(id: string): Workspace {
  const p = demoProjects.find((p) => p.id === id) ?? demoProjects[0];
  const isAPI = p.id === "global-logistics";
  const sources = isAPI
    ? [
        {
          id: "shipment-api",
          path: "contracts/shipment-api.yaml",
          name: "shipment-api.yaml",
          kind: "contract",
          version: "1.3.0",
          sha256: "example-source-digest",
          content: shipmentContract,
          status: "needs_review",
        },
        {
          id: "tracking-api",
          path: "contracts/tracking-api.yaml",
          name: "tracking-api.yaml",
          kind: "contract",
          version: "2.1.0",
          status: "source_only",
          content:
            'openapi: "3.1.0"\ninfo:\n  title: Tracking service\n  version: "2.1.0"\n# Illustrative source; no service was called.',
        },
        {
          id: "pricing-api",
          path: "contracts/pricing-api.yaml",
          name: "pricing-api.yaml",
          kind: "contract",
          version: "1.5.2",
          status: "source_only",
          content:
            'openapi: "3.1.0"\ninfo:\n  title: Pricing service\n  version: "1.5.2"\n# Illustrative source; no service was called.',
        },
      ]
    : [
        {
          id: `${p.id}-intent`,
          name: "accepted-intent.md",
          path: "docs/accepted-intent.md",
          kind: "intent",
          status: "source_only",
          content: `# ${p.name}\n\n${p.summary}\n\nThis fictional record demonstrates a project-specific workspace.\nNo product state, acceptance or execution is claimed.`,
        },
        {
          id: `${p.id}-contract`,
          name: "product-contract.json",
          path: "docs/product-contract.json",
          kind: "contract",
          status: "source_only",
          content: {
            example: true,
            product: p.name,
            domain: p.kind,
            phase: p.phase,
            source_of_truth: "native project files",
            execution: "disabled in example",
          },
        },
      ];
  return {
    project: p,
    sources,
    requirements: isAPI
      ? sampleReqs
      : [
          {
            id: "INTENT-01",
            title: p.summary,
            priority: "must",
            status: "source_only",
            source: "accepted-intent.md",
            acceptance: "Illustrative requirement; not owner acceptance.",
          },
          {
            id: "CTX-01",
            title: "Preserve accepted source, identity and unfinished work",
            priority: "must",
            status: "pending",
            source: "product-contract.json",
          },
        ],
    decisions: [
      {
        id: "D-01",
        title: isAPI
          ? "Align weight with the actual service"
          : "Preserve the accepted direction",
        status: "proposed",
        scope: "example only",
        rationale: "This is an illustrative proposal, not an owner decision.",
        source: "Example workspace",
      },
    ],
    artifacts: [
      {
        id: "example-contract",
        path: sources[0].path,
        name: sources[0].name,
        kind: "source",
        status: "source_only",
        content: sources[0].content,
      },
    ],
    identity: {
      status: "example_only",
      name: p.name,
      source: "Fictional example",
      fixed: ["Product name", "Accepted intent", "Source identity"],
      allowed_adaptations: ["Responsive layout", "Accessible presentation"],
      master: "No real product master imported",
    },
    jobs: isAPI ? [sampleJob] : [],
    context: {
      project: p.name,
      objective: isAPI ? sampleJob.objective : p.summary,
      source_refs: sources.map((s) => s.path),
      assigned_requirement_ids: isAPI
        ? ["API-01", "API-02", "OPS-01", "REL-01"]
        : ["INTENT-01", "CTX-01"],
      scope: "example only",
      outputs: [
        "Reviewable result",
        "Exact source references",
        "Independent review",
      ],
      execution_enabled: false,
    },
    readiness: [
      {
        id: "source",
        name: "source",
        status: "source_only",
        scope: "Illustrative contract",
      },
      { id: "code", name: "code", status: "not_tested" },
      { id: "integration", name: "integration", status: "not_tested" },
      {
        id: "independent_review",
        name: "independent_review",
        status: "pending",
      },
      {
        id: "owner_acceptance",
        name: "owner_acceptance",
        status: "not_observed",
      },
    ],
  };
}
