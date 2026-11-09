import { resolve } from "node:path";
import {
  array,
  digest,
  fail,
  now,
  readSource,
  safeFile,
  text,
} from "./utils.mjs";
export function selectRequirements(requirements, assigned) {
  const indexed = new Map();
  for (const row of requirements) {
    const key = text(row.id, "requirement id", 1, 240);
    fail(
      !indexed.has(key),
      "CONTEXT_CONFLICT",
      `Duplicate requirement identity: ${key}`,
      409,
    );
    indexed.set(key, row);
  }
  const selected = new Set(assigned);
  for (const row of requirements)
    if (
      row.applicable !== false &&
      (row.priority === "must" || row.always_review === true)
    )
      selected.add(row.id);
  const visiting = new Set(),
    visited = new Set();
  const visit = (key) => {
    fail(
      indexed.has(key),
      "CONTEXT_INCOMPLETE",
      `Unknown requirement dependency: ${key}`,
      409,
    );
    fail(
      !visiting.has(key),
      "CONTEXT_CONFLICT",
      `Cyclic requirement dependency: ${key}`,
      409,
    );
    if (visited.has(key)) return;
    visiting.add(key);
    const row = indexed.get(key);
    fail(
      row.applicable !== false,
      "CONTEXT_CONFLICT",
      `Required dependency is marked inapplicable: ${key}`,
      409,
    );
    for (const dependency of row.dependencies ?? []) {
      selected.add(dependency);
      visit(dependency);
    }
    visiting.delete(key);
    visited.add(key);
  };
  for (const key of [...selected]) visit(key);
  return {
    selected: [...selected].sort().map((key) => indexed.get(key)),
    omitted: requirements
      .filter((x) => !selected.has(x.id))
      .map((x) => ({
        id: x.id,
        reason:
          x.applicable === false
            ? `inapplicable: ${x.applicability_reason ?? "reason not recorded"}`
            : "not assigned/dependent/must/always-review",
      })),
  };
}
export async function compileContext({
  project,
  workspace,
  payload,
  taskId,
  authorityEpoch,
}) {
  const objective = text(payload.objective, "objective", 3, 2e4),
    acceptance = text(payload.acceptance, "acceptance", 3, 12e3);
  const scope = payload.scope ?? "read-only";
  const capability_scope = payload.capability_scope ?? {
    public_web_read: false,
  };
  fail(
    capability_scope &&
      typeof capability_scope === "object" &&
      !Array.isArray(capability_scope),
    "INVALID_INPUT",
    "capability_scope must be an object",
  );
  fail(
    Object.keys(capability_scope).every((key) => key === "public_web_read") &&
      (capability_scope.public_web_read === undefined ||
        typeof capability_scope.public_web_read === "boolean"),
    "CAPABILITY_UNVERIFIED",
    "Requested external/API/network scope is unsupported by this local route. Export the capsule to a capable approved Codex host; no narrower scope is silently substituted",
    409,
  );
  fail(
    ["read-only", "workspace-write"].includes(scope),
    "SCOPE_MISMATCH",
    "Choose read-only or workspace-write scope",
  );
  const timeout = payload.deadline_seconds ?? 600;
  fail(
    Number.isInteger(timeout) && timeout >= 30 && timeout <= 3600,
    "BUDGET_UNDEFINED",
    "Deadline must be30–3600seconds",
  );
  const paths = payload.allowed_paths ?? [];
  array(paths, "allowed_paths", 40);
  const allowedRoots = [];
  if (scope === "workspace-write") {
    fail(
      paths.length > 0,
      "SCOPE_MISMATCH",
      "Workspace writes need explicit allowed directories",
    );
    for (const ref of paths)
      allowedRoots.push(await safeFile(project.root, ref, { directory: true }));
  } else
    fail(
      paths.length === 0,
      "SCOPE_MISMATCH",
      "Read-only tasks cannot request writable paths",
    );
  const normalized = workspace.requirements.map((row, index) => {
    const nativeId =
      row.id ?? row.requirement_id ?? row.key ?? `native-row-${index + 1}`;
    const rawPriority = String(
      row.priority ?? row.severity ?? "must",
    ).toLowerCase();
    const priority = ["must", "should", "could"].includes(rawPriority)
      ? rawPriority
      : "must";
    const original =
      row.verbatim ??
      row.source_text ??
      row.text ??
      row.description ??
      row.requirement ??
      JSON.stringify(row);
    const dependencies = row.dependencies ?? row.depends_on ?? [];
    fail(
      Array.isArray(dependencies) &&
        dependencies.every((x) => typeof x === "string"),
      "CONTEXT_INCOMPLETE",
      `Requirement ${nativeId} has an unsupported dependency shape`,
      409,
    );
    return {
      id: String(nativeId),
      source_ref: row.source_ref,
      verbatim: String(original),
      interpretation: String(
        row.interpretation ??
          row.text ??
          row.description ??
          row.requirement ??
          original,
      ),
      priority,
      applicable: row.applicable !== false,
      applicability_reason: row.applicability_reason,
      always_review: row.always_review === true,
      dependencies,
      acceptance:
        row.acceptance ??
        row.acceptance_criteria ??
        "Native acceptance retained in raw record; task acceptance adds no product acceptance",
      owner: row.owner ?? "native-project-owner",
      due_gate: row.due_gate ?? row.phase ?? "native-unspecified",
      raw_native_record: row,
    };
  });
  const direct = {
    id: `${taskId}:request`,
    source_ref: `service-command:${taskId}`,
    verbatim: objective,
    interpretation: objective,
    priority: "must",
    applicable: true,
    dependencies: [],
    acceptance,
    owner: "local-owner",
    due_gate: "task-completion",
  };
  const requirements = [...normalized, direct];
  const assigned =
    payload.requirement_ids ??
    requirements.filter((x) => x.applicable !== false).map((x) => x.id);
  array(assigned, "requirement_ids", 2e3);
  const selected = selectRequirements(requirements, assigned);
  const inputs = [...workspace.sources];
  for (const ref of payload.source_paths ?? []) {
    const source = await readSource(
      project.root,
      text(ref, "source path", 1, 4096),
    );
    if (!inputs.some((x) => x.path === source.path))
      inputs.push({
        path: source.path,
        sha256: source.sha256,
        bytes: source.bytes,
        kind: "task-source",
      });
  }
  const capsule = {
    schema_version: "atelier.context-capsule.service/1",
    project_id: project.id,
    native_revision: workspace.project.revision,
    task_id: taskId,
    root: project.root,
    objective,
    scope,
    capability_scope: {
      public_web_read: capability_scope.public_web_read === true,
    },
    acceptance,
    allowed_paths: paths,
    allowed_roots: allowedRoots,
    requirements: selected.selected,
    omitted_requirements: selected.omitted,
    original_sources: inputs,
    decisions: workspace.decisions,
    identity: workspace.identity,
    readiness: workspace.readiness,
    unresolved: workspace.warnings,
    output_consumer: "local-owner and project integrator",
    expected_outputs: payload.outputs ?? [
      "Task result with actual artifacts, checks, limitations and next action",
    ],
    budget: {
      deadline_seconds: timeout,
      maximum_attempts: 1,
      new_paid_resources: 0,
      token_limit:
        "not_supported_by_this_adapter; actual provider account limits apply",
    },
    stop: "Stop at deadline/pause or required effect/access beyond task; never replay unknown effects",
    recovery:
      "Reconcile stored host thread/turn and native source pins before another attempt",
    authority_ref: `local-user-task:${taskId}`,
    authority_epoch: authorityEpoch,
    production_profile_ref: "standards/production-profiles.json",
    quality_certified: false,
    authority_authenticated: false,
    source_completeness_authenticated: false,
    projection_notice:
      "Derived from explicitly read native records and this user task; original source refs/raw records remain authoritative",
    created_at: now(),
  };
  capsule.capsule_sha256 = digest(capsule);
  return capsule;
}
