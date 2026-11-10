import type { Data, Workspace } from "./api";

export type CoverageState =
  "unverified" | "verified-declared-bindings" | "incomplete" | "conflict";

export interface ContextSource {
  path: string;
  role: string;
  required: boolean;
  status: string;
  expectedHash: string;
  observedHash: string;
  record: Data;
}

const record = (value: unknown): Data | null =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Data)
    : null;
const string = (value: unknown) => (typeof value === "string" ? value : "");
const records = (value: unknown): Data[] =>
  Array.isArray(value) ? value.filter((item) => record(item)) : [];
const ids = (value: unknown): string[] =>
  Array.isArray(value)
    ? [
        ...new Set(
          value.filter(
            (item): item is string =>
              typeof item === "string" && item.length > 0,
          ),
        ),
      ]
    : [];

/** A loaded workspace is fresher than the separately paged portfolio snapshot. */
export function workspaceDirection(
  workspace: Workspace | null,
  selectedId: string | undefined,
) {
  if (!workspace || workspace.project?.id !== selectedId)
    return { goal: undefined, next: [], agents: [] };
  return {
    goal: record(workspace.goal) ?? undefined,
    next: records(workspace.next_actions),
    agents: records(workspace.agents),
  };
}

/** Present native fields without changing the source record or inferring acceptance. */
export function requirementPresentation(requirement: Data, locale = "en") {
  const first = (...values: unknown[]) => {
    const value = values.find(
      (item) => item !== null && item !== undefined && item !== "",
    );
    return value === undefined
      ? ""
      : typeof value === "object"
        ? JSON.stringify(value)
        : String(value);
  };
  const localized =
    locale === "uk"
      ? [requirement.source_text_uk, requirement.requirement_en]
      : [requirement.requirement_en, requirement.source_text_uk];
  return {
    title: first(
      requirement.title,
      requirement.description,
      requirement.text,
      requirement.requirement,
      ...localized,
      requirement.verbatim,
      requirement.interpretation,
    ),
    status:
      first(requirement.status, requirement.current_status) || "source_only",
  };
}

/** A different project's cached workspace cannot supply counts or evidence. */
export function workspaceReadState(
  workspace: Workspace | Data | null | undefined,
  projectId: string | null | undefined,
  loading: boolean,
) {
  if (projectId && workspace?.project?.id === projectId)
    return "ready" as const;
  return loading ? ("loading" as const) : ("unavailable" as const);
}

/** Recovery clears only that read's still-visible error, never a newer action error. */
export function recoveredWorkspaceError<T>(
  current: T | null,
  failure: { projectId: string; error: T } | null,
  recoveredProjectId: string,
): T | null {
  return failure?.projectId === recoveredProjectId && current === failure.error
    ? null
    : current;
}

/** A presentation of declared bindings, never a certification of the original brief. */
export function contextCoverage(
  workspace: Workspace | Data | null | undefined,
) {
  const raw =
    record(workspace?.context_coverage) ??
    record(workspace?.context?.coverage) ??
    record(workspace?.context?.context_coverage);
  const sources: ContextSource[] = records(raw?.source_checks).map((item) => ({
    path: string(item.path),
    role: string(item.role),
    required: item.required === true,
    status: string(item.status) || "unverified",
    expectedHash: string(item.expected_sha256),
    observedHash: string(item.observed_sha256),
    record: item,
  }));
  const missingMustIds = ids(raw?.missing_must_ids);
  const missingRequirementIds = ids(raw?.missing_requirement_ids);
  const known = new Set<CoverageState>([
    "unverified",
    "verified-declared-bindings",
    "incomplete",
    "conflict",
  ]);
  const reported = string(raw?.status) as CoverageState;
  let state: CoverageState = known.has(reported) ? reported : "unverified";
  // A contradictory success declaration must not conceal an observed required gap.
  const changed = sources.some(
    (item) => item.required && item.status === "changed",
  );
  const missing = sources.some(
    (item) => item.required && item.status !== "verified",
  );
  if (changed) state = "conflict";
  else if (
    state !== "conflict" &&
    (missing || missingMustIds.length || missingRequirementIds.length)
  )
    state = "incomplete";
  return {
    state,
    sources,
    verifiedSources: sources.filter((item) => item.status === "verified")
      .length,
    missingMustIds,
    missingRequirementIds,
    issues: records(raw?.issues),
    manifestRef:
      string(record(raw?.manifest_ref)?.path) || string(raw?.manifest_ref),
    manifestHash: string(record(raw?.manifest_ref)?.sha256),
    requirements: records(raw?.requirement_checks),
    notice: string(raw?.notice),
    // The server's file/ID checks cannot authenticate source completeness.
    completenessAuthenticated: false as const,
    record: raw,
  };
}

export function contextTrail(workspace: Workspace | Data | null | undefined) {
  const current = workspace?.current_decisions;
  return {
    decisions: records(Array.isArray(current) ? current : workspace?.decisions),
    explicitlyCurrent: Array.isArray(current),
    deferred: records(
      workspace?.deferred_work ?? workspace?.context?.deferred_work,
    ),
  };
}

export const activeJobStatuses = new Set([
  "running",
  "queued",
  "dispatching",
  "awaiting_approval",
  "awaiting_input",
  "cancel_requested",
  "reconciling",
]);

/** Count only observed jobs; a completed model turn is not product acceptance. */
export function observedJobCounts(jobs: unknown) {
  const entries = records(jobs);
  return {
    total: entries.length,
    active: entries.filter((item) => activeJobStatuses.has(string(item.status)))
      .length,
    attention: entries.filter((item) =>
      ["failed", "outcome_unknown", "blocked"].includes(string(item.status)),
    ).length,
  };
}
