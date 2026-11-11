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
  if (!selectedId || workspace?.project?.id !== selectedId)
    return { goal: undefined, next: [], agents: [] };
  const checkpoint = record(workspace.current_checkpoint);
  const next =
    typeof checkpoint?.next === "string" && checkpoint.next.trim()
      ? [
          {
            text: checkpoint.next,
            status: "declared",
            source_ref: checkpoint.source_ref,
            source_sha256: checkpoint.source_sha256,
          },
        ]
      : records(workspace.next_actions);
  return {
    goal: record(workspace.goal) ?? undefined,
    next,
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
  "gating",
  "awaiting_approval",
  "awaiting_input",
  "cancel_requested",
  "pause_pending",
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

export interface OperatorWork {
  id: string;
  title: string;
  status: string;
  source: string;
  lane: "active" | "attention" | "results" | "recorded";
  record: Data;
}

/** A compact presentation keeps the unmodified original in the record inspector. */
export function operatorSummary(value: unknown, maximum = 220) {
  if (typeof value !== "string") return "";
  let summary = value.replace(/\s+/g, " ").trim();
  const locator = summary.search(/\b(?:reports|docs|artifacts|output)\//);
  if (locator >= 0)
    summary = summary
      .slice(0, locator)
      .replace(/(?:Джерело|Source|Evidence|Proof)\s*[:—-]?\s*$/i, "")
      .trim();
  if (summary.length <= maximum) return summary;
  const boundary = summary.lastIndexOf(" ", maximum);
  return (
    summary.slice(0, boundary > maximum * 0.6 ? boundary : maximum).trimEnd() +
    "…"
  );
}

/** Locators are proposals for a user-triggered bounded source read, never file authority. */
export function workResultSources(record: Data | null | undefined): string[] {
  const declared = records(record?.evidence_refs).map((item) =>
    string(item.path),
  );
  const text = string(record?.outcome ?? record?.result);
  const mentioned = [
    ...text.matchAll(
      /\b((?:docs|reports|artifacts|output)\/[A-Za-z0-9_./-]+\.(?:md|txt))\b/g,
    ),
  ].map((match) => match[1]);
  return [...new Set([...declared, ...mentioned])]
    .filter(
      (path) =>
        /^(?:docs|reports|artifacts|output)\//.test(path) &&
        /\.(?:md|txt)$/.test(path) &&
        !path.split("/").includes("..") &&
        path.length < 1000,
    )
    .slice(0, 6);
}

/** Project work is observed data, not a guess based on prompt wording or recency. */
export function operatorWorkspace(
  workspace: Workspace | null,
  selectedId: string | undefined,
  detail?: Data | null,
) {
  const current =
    selectedId && workspace?.project?.id === selectedId ? workspace : null;
  const validDetail =
    current &&
    detail &&
    typeof current.project.root === "string" &&
    detail.project?.root === current.project.root
      ? detail
      : null;
  const work = new Map<string, OperatorWork>();
  const workspaceIds = new Set<string>();
  const aliases = new Map<string, string>();
  const sourceHistory: Data[] = [];
  const sourcePins = new Map<string, string | null>();
  const hasSourceInventory = Array.isArray(current?.sources);
  const pinSource = (path: unknown, hash: unknown) => {
    const ref = string(path);
    if (!ref) return;
    const pin = string(hash) || null;
    sourcePins.set(
      ref,
      sourcePins.has(ref) && sourcePins.get(ref) !== pin ? null : pin,
    );
  };
  if (hasSourceInventory) {
    for (const source of records(current?.sources))
      pinSource(source.path, source.sha256);
  } else {
    // Legacy packets can establish only the pins of their own current records.
    for (const item of [
      ...records(current?.work_records),
      ...records(current?.tasks),
    ])
      pinSource(item.source_ref, item.source_sha256);
  }
  const active = new Set([
    ...activeJobStatuses,
    "pause_pending",
    "in_progress",
    "inProgress",
    "active",
    "gating",
  ]);
  const attention = new Set([
    "failed",
    "blocked",
    "outcome_unknown",
    "interrupted",
    "awaiting_approval",
    "awaiting_input",
  ]);
  const add = (item: Data, origin: string, fromWorkspace = false) => {
    const source = ["native-project", "native-record"].includes(origin)
      ? "native-record"
      : origin;
    const sourceRef = string(item.source_ref);
    const nativeId =
      (typeof item.native_id === "string" && item.native_id.length > 0) ||
      (typeof item.native_id === "number" && Number.isFinite(item.native_id))
        ? item.native_id
        : undefined;
    const keys =
      source === "native-record"
        ? sourceRef && nativeId !== undefined
          ? [`source:${JSON.stringify([sourceRef, nativeId])}`]
          : typeof item.id === "string" && item.id
            ? [`source-record:${JSON.stringify([sourceRef || null, item.id])}`]
            : []
        : [
            ...(item.thread_id && item.turn_id
              ? [`turn:${JSON.stringify([item.thread_id, item.turn_id])}`]
              : []),
            ...[
              item.service_job_id,
              item.job_id,
              ...(source === "service" ? [item.id] : []),
            ]
              .filter((value) => typeof value === "string" && value)
              .map((value) => `service:${value}`),
            ...(typeof item.id === "string" && item.id
              ? [`record:${JSON.stringify([source, item.id])}`]
              : []),
          ];
    const identity =
      keys.map((key) => aliases.get(key)).find(Boolean) ?? keys[0];
    if (!identity) return;
    const existing = work.get(identity);
    if (
      !fromWorkspace &&
      source === "native-record" &&
      !(existing && workspaceIds.has(identity))
    ) {
      const pin = sourcePins.get(sourceRef);
      const reason = !sourceRef
        ? "missing-source-provenance"
        : !sourcePins.has(sourceRef)
          ? hasSourceInventory
            ? "source-not-current"
            : "current-source-unverified"
          : !pin || !string(item.source_sha256)
            ? "current-source-unverified"
            : pin !== item.source_sha256
              ? "source-revision-changed"
              : null;
      if (reason) {
        sourceHistory.push({
          reason,
          current: false,
          source_ref: sourceRef || null,
          current_source_sha256: pin ?? null,
          record: item,
        });
        return;
      }
    }
    for (const key of keys) aliases.set(key, identity);
    if (item.work_type === "permission_review") {
      work.delete(identity);
      return;
    }
    if (existing && workspaceIds.has(identity) && !fromWorkspace) {
      // The current workspace is the sole state/authority record. A cached page
      // may add only correlated transcript, native identity and evidence facts.
      const merged = { ...existing.record };
      const observation = Object.fromEntries(
        [
          "id",
          "native_id",
          "objective",
          "outcome",
          "source",
          "source_ref",
          "source_sha256",
          "thread_id",
          "turn_id",
          "status",
          "native_status",
          "review_status",
          "owner_review",
          "acceptance",
          "evidence_refs",
        ]
          .filter((field) => Object.hasOwn(item, field))
          .map((field) => [field, item[field]]),
      );
      merged.history_observations = [
        ...new Map(
          [
            ...(Array.isArray(existing.record.history_observations)
              ? existing.record.history_observations
              : []),
            observation,
          ].map((value) => [JSON.stringify(value), value]),
        ).values(),
      ];
      const sameSource =
        existing.source !== "native-record" ||
        (typeof existing.record.source_sha256 === "string" &&
          existing.record.source_sha256.length > 0 &&
          existing.record.source_ref === item.source_ref &&
          existing.record.source_sha256 === item.source_sha256);
      if (sameSource) {
        for (const field of [
          "outcome",
          "output_text",
          "response_item_id",
          "thread_id",
          "turn_id",
        ]) {
          if (
            (merged[field] === undefined ||
              merged[field] === null ||
              merged[field] === "") &&
            typeof item[field] === "string" &&
            item[field]
          )
            merged[field] = item[field];
        }
        merged.evidence_refs = [
          ...new Map(
            [
              ...(Array.isArray(existing.record.evidence_refs)
                ? existing.record.evidence_refs
                : []),
              ...(Array.isArray(item.evidence_refs) ? item.evidence_refs : []),
            ].map((value) => [JSON.stringify(value), value]),
          ).values(),
        ];
      }
      work.set(identity, { ...existing, record: merged });
      return;
    }
    const status = string(item.status) || "recorded";
    // Native record status is a declaration about work, not an observed host run.
    const laneStatus =
      source === "native-record"
        ? string(item.native_status) || status
        : status;
    const lane =
      attention.has(laneStatus) || laneStatus === "rework"
        ? "attention"
        : active.has(laneStatus)
          ? "active"
          : ["completed", "answer_received"].includes(laneStatus)
            ? "results"
            : "recorded";
    if (fromWorkspace) workspaceIds.add(identity);
    work.set(identity, {
      id: identity,
      title: string(item.objective ?? item.title ?? item.name) || identity,
      status,
      source,
      lane,
      record: { ...(existing?.record ?? {}), ...item },
    });
  };
  for (const item of records(current?.jobs)) add(item, "service", true);
  for (const item of records(current?.work_records))
    add(item, "native-record", true);
  for (const item of records(current?.tasks)) {
    if (!records(current?.jobs).some((job) => job.task_id === item.id))
      add(item, "service", true);
  }
  for (const group of records(validDetail?.work_groups)) {
    for (const item of records(group.items))
      if (
        group.id !== "system_checks" ||
        item.work_type === "permission_review"
      )
        add(
          item,
          string(item.source) ||
            ((item.thread_id && item.turn_id) ||
            item.job_id ||
            item.service_job_id
              ? "native-history"
              : "history-record"),
        );
  }
  const requirements = records(current?.requirements);
  const stages = new Map<string, Data[]>();
  const dependencies: { from: string; to: string }[] = [];
  const requirementIds = new Set(requirements.map((item) => string(item.id)));
  for (const requirement of requirements) {
    for (const stage of ids(requirement.stages)) {
      stages.set(stage, [...(stages.get(stage) ?? []), requirement]);
    }
    for (const dependency of ids(
      requirement.dependencies ?? requirement.depends_on,
    )) {
      if (requirementIds.has(dependency))
        dependencies.push({ from: dependency, to: string(requirement.id) });
    }
  }
  const entries = [...work.values()];
  const { goal, next } = workspaceDirection(current, selectedId);
  return {
    goal,
    next,
    work: entries,
    sourceHistory,
    current: entries.find((item) => item.lane === "active") ?? null,
    attention: entries.filter((item) => item.lane === "attention"),
    results: entries.filter((item) => item.lane === "results"),
    stages: [...stages]
      .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
      .map(([id, requirements]) => ({ id, requirements })),
    dependencies,
    requirements,
    unstagedRequirements: requirements.filter(
      (item) => !ids(item.stages).length,
    ),
    coverage: validDetail?.coverage ?? null,
    nativeRead: validDetail !== null,
    checkpoint: record(current?.current_checkpoint),
  };
}
