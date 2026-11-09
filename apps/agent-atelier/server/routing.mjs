import { isAbsolute, resolve } from "node:path";
import { digest, fail, isWithin, redact, text } from "./utils.mjs";

export const ROUTES = [
  "direct",
  "specialist",
  "project_agent",
  "director",
  "compose",
  "create_agent",
  "maintain_system",
  "bridge",
];
const TARGETS = [
  "orchestrator",
  "skill",
  "constructor",
  "project_agent",
  "agent",
  "system",
];

export function proposeRoute({
  project,
  workspace,
  skills,
  payload,
  controllerAvailable = false,
}) {
  const objective = text(payload.objective, "objective", 3, 20000);
  const requested =
    payload.route ??
    (payload.intent === "auto" ? null : payload.intent) ??
    null;
  fail(
    requested === null || ROUTES.includes(requested),
    "INVALID_INPUT",
    "Unsupported orchestration route",
  );
  const nativeAgents = workspace.agents ?? [];
  const observed = skills.entries ?? [];
  const candidates = nativeAgents.map((agent) => {
    const expected =
      typeof agent.source_ref === "string"
        ? resolve(project.root, agent.source_ref)
        : null;
    const catalogs = observed.filter(
      (x) =>
        agent.availability === "installed" &&
        expected &&
        isWithin(resolve(project.root, ".agents/skills"), expected) &&
        x.name === agent.name &&
        x.enabled !== false &&
        x.host_enabled !== false &&
        typeof (x.source_path ?? x.host_source_path ?? x.path) === "string" &&
        resolve(x.source_path ?? x.host_source_path ?? x.path) === expected &&
        /^[a-f0-9]{64}$/.test(agent.source_sha256 ?? "") &&
        x.source_sha256 === agent.source_sha256 &&
        x.discovery_status === "host_discovered",
    );
    const catalog = catalogs.length === 1 ? catalogs[0] : null;
    return {
      ...agent,
      discovery_status:
        catalogs.length > 1
          ? "ambiguous"
          : catalog
            ? "host_discovered"
            : (agent.discovery_status ?? "unverified"),
      source_id: catalog?.source_id ?? null,
      execution_supported: catalog?.execution_supported === true,
    };
  });
  const executable = candidates.filter(
    (x) => x.availability === "installed" && x.execution_supported,
  );
  const origins = new Map();
  for (const agent of executable)
    origins.set(agent.name, (origins.get(agent.name) ?? 0) + 1);
  for (const agent of candidates)
    if ((origins.get(agent.name) ?? 0) > 1) {
      agent.discovery_status = "ambiguous";
      agent.execution_supported = false;
    }
  const existing =
    executable.length === 1 && executable[0].execution_supported
      ? executable[0]
      : null;
  const route = requested ?? (existing ? "project_agent" : null);
  const maintenance = payload.maintenance ?? null;
  if (maintenance !== null) {
    fail(
      maintenance &&
        typeof maintenance === "object" &&
        !Array.isArray(maintenance),
      "INVALID_INPUT",
      "maintenance must be an object",
    );
    fail(
      TARGETS.includes(maintenance.target_kind),
      "INVALID_INPUT",
      "Unsupported maintenance target kind",
    );
    fail(
      Array.isArray(maintenance.target_refs) &&
        maintenance.target_refs.length >= 1 &&
        maintenance.target_refs.length <= 25,
      "INVALID_INPUT",
      "List1..25 exact maintenance targets",
    );
    for (const ref of maintenance.target_refs) {
      text(ref, "maintenance target", 1, 4096);
      fail(
        !ref.includes("\0") && !ref.split(/[\\/]/).includes(".."),
        "OUTSIDE_ROOT",
        "Maintenance references cannot traverse outside the bound project",
      );
      fail(
        !isAbsolute(ref) || isWithin(project.root, resolve(ref)),
        "OUTSIDE_ROOT",
        "Maintenance paths must belong to the bound project; choose the canonical system project for reusable maintenance",
      );
    }
  }
  const capability_gaps = [];
  if (
    executable.length > 1 ||
    candidates.some((agent) => agent.discovery_status === "ambiguous")
  )
    capability_gaps.push({
      code: "PROJECT_AGENT_AMBIGUOUS",
      detail:
        "Multiple project-agent sources require an explicit source-bound choice before routing",
    });
  if (route === "project_agent" && !existing)
    capability_gaps.push({
      code: "PROJECT_AGENT_UNVERIFIED",
      detail:
        "No enabled project-agent source was actually discovered; a passport declaration is not installation",
    });
  if (route === "create_agent" && !controllerAvailable)
    capability_gaps.push({
      code: "NATIVE_CONTROLLER_REQUIRED",
      detail:
        "Native factory state remains protected; prepare/review a supported controller operation before construction",
    });
  const result = {
    schema_version: "atelier.routing/1",
    status: "proposed",
    route,
    requested_route: requested,
    reason: requested
      ? "Owner selected this route; the executor must verify exact scope, sources and capability"
      : existing
        ? "An installed and host-discovered project agent is available; restore its native context"
        : "The orchestration skill will decide from the full request and native context; no keyword classifier is treated as an expert decision",
    execution_owner:
      existing && route === "project_agent"
        ? existing.name
        : "atelier-orchestrator",
    project_id: project.id,
    native_revision: workspace.project.revision,
    original_objective: objective,
    original_result_acceptance:
      typeof payload.acceptance === "string"
        ? payload.acceptance
        : Array.isArray(payload.acceptance)
          ? payload.acceptance
          : [],
    project_agents: candidates,
    preferred_project_agent: existing?.name ?? null,
    creation_scope: payload.creation_scope ?? null,
    execution_scope: {
      scope: payload.scope ?? "read-only",
      allowed_paths: payload.allowed_paths ?? [],
    },
    maintenance: maintenance ? redact(maintenance) : null,
    capability_gaps,
    continuation: {
      return_to: "atelier-orchestrator",
      preferred_project_agent: existing?.name ?? null,
      message: existing
        ? `Continue through ${existing.name}; this entry can still route future requests to it`
        : "The integrator retains the initial objective through any specialist/factory handoff",
    },
    authority: "projection-only; no new rights or accepted product result",
    source_pins: workspace.sources ?? [],
    model_execution_observed: false,
  };
  return { ...result, routing_sha256: digest(result) };
}
