import { basename, isAbsolute, resolve } from "node:path";
import { homedir } from "node:os";
import { assertProjectRoot, inspectProject } from "./projects.mjs";
import {
  digest,
  fail,
  isWithin,
  now,
  publicError,
  redact,
  sha,
  text,
} from "./utils.mjs";

const emptyGoal = () => ({
  status: "unknown",
  text: "",
  source_ref: null,
  source_sha256: null,
});
const clipped = (value, limit = 1600) =>
  typeof value === "string" ? redact(value).slice(0, limit) : "";
const statusOf = (row) =>
  typeof row.status === "string" ? row.status : (row.status?.type ?? "unknown");
const itemText = (item) =>
  clipped(
    item.text ??
      item.content
        ?.filter?.((x) => x.type === "text" || x.type === "inputText")
        .map((x) => x.text ?? "")
        .join("\n") ??
      "",
    8000,
  );
const workIdentity = (item) =>
  JSON.stringify(
    item.thread_id && item.turn_id
      ? ["native-turn", item.thread_id, item.turn_id]
      : ["record", item.id],
  );
const uniqueRecords = (records) => [
  ...new Map(records.map((record) => [digest(record), record])).values(),
];
function mergeWork(previous, incoming) {
  if (!previous) return incoming;
  const preferred =
    incoming.source === "native-history"
      ? incoming
      : previous.source === "native-history"
        ? previous
        : incoming;
  const secondary = preferred === incoming ? previous : incoming;
  const owner_review = incoming.owner_review ?? previous.owner_review ?? null;
  return {
    ...secondary,
    ...preferred,
    task_id: incoming.task_id ?? previous.task_id ?? null,
    job_id: incoming.job_id ?? previous.job_id ?? null,
    service_job_id:
      incoming.service_job_id ??
      previous.service_job_id ??
      (incoming.source === "service" ? incoming.job_id : null) ??
      (previous.source === "service" ? previous.job_id : null) ??
      null,
    owner_review,
    acceptance:
      owner_review !== null
        ? owner_review === "accepted"
          ? "owner-review"
          : "not_inferred"
        : previous.acceptance === "owner-review" ||
            incoming.acceptance === "owner-review"
          ? "owner-review"
          : (preferred.acceptance ?? "not_inferred"),
    evidence_refs: uniqueRecords([
      ...(previous.evidence_refs ?? []),
      ...(incoming.evidence_refs ?? []),
    ]),
    skills: uniqueRecords([
      ...(previous.skills ?? []),
      ...(incoming.skills ?? []),
    ]),
    warnings: uniqueRecords([
      ...(previous.warnings ?? []),
      ...(incoming.warnings ?? []),
    ]),
    response_observed:
      previous.response_observed === true ||
      incoming.response_observed === true,
    execution_observed:
      previous.execution_observed === true ||
      incoming.execution_observed === true,
  };
}

export function projectWorkGroups(items) {
  const permissionReviews = items.filter(
    (item) => item.work_type === "permission_review",
  );
  const primaryWork = items.filter(
    (item) => item.work_type !== "permission_review",
  );
  const definitions = [
    [
      "attention",
      [
        "failed",
        "interrupted",
        "outcome_unknown",
        "awaiting_approval",
        "awaiting_input",
      ],
    ],
    [
      "active",
      [
        "in_progress",
        "inProgress",
        "running",
        "queued",
        "dispatching",
        "gating",
      ],
    ],
    ["results", ["answer_received", "completed"]],
    ["recorded", ["recorded"]],
    ["prepared", ["prepared", "paused"]],
  ];
  const assigned = new Set();
  const groups = definitions.map(([id, statuses]) => {
    const grouped = primaryWork.filter((x) => statuses.includes(x.status));
    for (const row of grouped) assigned.add(row.id);
    return { id, title: id, count: grouped.length, items: grouped };
  });
  const other = primaryWork.filter((x) => !assigned.has(x.id));
  if (other.length)
    groups.push({
      id: "other",
      title: "other",
      count: other.length,
      items: other,
    });
  if (permissionReviews.length)
    groups.push({
      id: "system_checks",
      title: "system_checks",
      count: permissionReviews.length,
      items: permissionReviews,
    });
  return groups.filter((x) => x.count);
}

export function turnWork(thread, turn) {
  const permissionReview =
    thread.thread_source === "guardian_review" ||
    thread.threadSource === "guardian_review" ||
    thread.source?.subAgent?.other === "guardian";
  const items = Array.isArray(turn.items) ? turn.items : [];
  const objective =
    items
      .filter((x) => x.type === "userMessage")
      .map(itemText)
      .find(Boolean) ?? clipped(thread.title, 1000);
  const answers = items
    .filter((x) => x.type === "agentMessage")
    .map(itemText)
    .filter((value) => value.trim());
  const skills = [];
  for (const item of items.filter((x) => x.type === "userMessage")) {
    for (const input of item.content ?? []) {
      if (input.type === "skill" && typeof input.name === "string")
        skills.push({
          name: clipped(input.name, 100),
          status: "selected",
          source_ref: `thread:${thread.id}/turn:${turn.id}/item:${item.id}`,
          path: clipped(input.path, 4096),
        });
      if (input.type === "text" || input.type === "inputText") {
        for (const match of (input.text ?? "").matchAll(
          /(?:\$|@)([a-z][a-z0-9-]{2,99})\b/g,
        ))
          if (!skills.some((x) => x.name === match[1]))
            skills.push({
              name: match[1],
              status: "mentioned",
              source_ref: `thread:${thread.id}/turn:${turn.id}/item:${item.id}`,
            });
      }
    }
  }
  const evidence_refs = [];
  for (const item of items) {
    if (item.type === "fileChange") {
      for (const change of item.changes ?? [])
        evidence_refs.push({
          kind: "file_change",
          path: clipped(change.path, 4096),
          native_status: clipped(item.status, 80),
          source_ref: `thread:${thread.id}/turn:${turn.id}/item:${item.id}`,
        });
    }
    if (item.type === "commandExecution")
      evidence_refs.push({
        kind: "command_observation",
        exit_code: Number.isInteger(item.exitCode) ? item.exitCode : null,
        native_status: clipped(item.status, 80),
        source_ref: `thread:${thread.id}/turn:${turn.id}/item:${item.id}`,
      });
    if (item.type === "imageView")
      evidence_refs.push({
        kind: "image_observation",
        path: clipped(item.path, 4096),
        source_ref: `thread:${thread.id}/turn:${turn.id}/item:${item.id}`,
      });
  }
  const response_observed = answers.length > 0;
  const warnings =
    turn.status === "completed" && !response_observed
      ? [
          {
            code: "NATIVE_COMPLETED_WITHOUT_ANSWER",
            message:
              "Native completion has no observed agent response; a saved user message or partial history is not a received result",
          },
        ]
      : [];
  return {
    id: `native-${sha(thread.id + ":" + turn.id).slice(0, 20)}`,
    thread_id: thread.id,
    turn_id: turn.id,
    objective: objective.slice(0, 1600),
    outcome: (answers.at(-1) ?? "").slice(0, 5000),
    status:
      turn.status === "completed"
        ? response_observed
          ? "answer_received"
          : "recorded"
        : turn.status === "inProgress"
          ? "in_progress"
          : (turn.status ?? "unknown"),
    native_status: turn.status,
    source: "native-history",
    work_type: permissionReview ? "permission_review" : "native_work",
    native_session_source: redact(thread.source ?? null),
    native_thread_source:
      clipped(thread.thread_source ?? thread.threadSource, 100) || null,
    parent_thread_id:
      clipped(thread.parent_thread_id ?? thread.parentThreadId, 160) || null,
    ...(permissionReview
      ? { product_result: false, independent_qa: false }
      : {}),
    source_ref: `thread:${thread.id}/turn:${turn.id}`,
    source_sha256: digest(turn),
    evidence_refs: evidence_refs.slice(0, 100),
    skills,
    started_at: turn.startedAt ?? null,
    completed_at: turn.completedAt ?? null,
    acceptance: "not_inferred",
    items_view: turn.itemsView ?? "unknown",
    response_observed,
    execution_observed: evidence_refs.length > 0,
    warnings,
  };
}

// This facade deliberately exposes only public read methods. Execution continues
// through Application's isolated dispatcher and its existing ownership gates.
export class NativeHistoryReader {
  #codex;
  constructor(codex) {
    this.#codex = codex;
  }
  list(options) {
    return this.#codex.allThreads(options);
  }
  read(id) {
    return this.#codex.readThread(id);
  }
  turns(id, options) {
    return this.#codex.historyTurns(id, options);
  }
}

export class PortfolioManager {
  constructor({ store, codex, dataDir }) {
    this.store = store;
    this.history = new NativeHistoryReader(codex);
    this.dataDir = dataDir;
    this.rows = new Map();
    this.threadRows = new Map();
    this.details = new Map();
    this.observedPages = new Map();
    this.busy = false;
    this.generation = 0;
    this.snapshot = {
      status: "not_checked",
      checked_at: null,
      coverage: {
        source: "public-native-thread-history",
        complete: false,
        pages: 0,
        native_threads: 0,
        registered_projects: "not_available",
        work_history: "not_loaded",
      },
      summary: {
        projects: 0,
        threads: 0,
        work_items: 0,
        active: 0,
        attention: 0,
      },
      projects: [],
      warnings: [],
    };
  }
  get() {
    const bindings = this.store.list("project");
    const projects = this.snapshot.projects.map((row) => {
      const binding = bindings.find((x) => x.root === row.root);
      return {
        ...row,
        binding_id: binding?.id ?? null,
        name: binding?.name ?? row.name,
      };
    });
    return {
      ...this.snapshot,
      projects,
      summary: {
        ...this.snapshot.summary,
        work_items: projects.reduce(
          (sum, row) => sum + row.known_work_items,
          0,
        ),
      },
    };
  }
  invalidate() {
    this.generation++;
    this.rows.clear();
    this.threadRows.clear();
    this.details.clear();
    this.observedPages.clear();
    this.snapshot = {
      ...this.snapshot,
      status: "not_checked",
      projects: [],
      summary: {
        projects: 0,
        threads: 0,
        work_items: 0,
        active: 0,
        attention: 0,
      },
      warnings: [],
      coverage: {
        ...this.snapshot.coverage,
        complete: false,
        pages: 0,
        native_threads: 0,
        work_history: "not_loaded",
      },
    };
  }
  #privateRoot(root) {
    return [
      this.dataDir,
      resolve(homedir(), ".codex"),
      resolve(homedir(), "Library/Application Support"),
    ].some((base) => isWithin(base, root) || isWithin(root, base));
  }
  async refresh(payload = {}) {
    fail(
      !this.busy,
      "CATALOG_BUSY",
      "Portfolio discovery is already running",
      409,
    );
    fail(
      payload.include_archived === undefined ||
        typeof payload.include_archived === "boolean",
      "INVALID_INPUT",
      "include_archived must be a boolean",
    );
    const maxPages = payload.max_pages ?? 50;
    fail(
      Number.isInteger(maxPages) && maxPages >= 1 && maxPages <= 50,
      "INVALID_INPUT",
      "max_pages must be1..50",
    );
    this.busy = true;
    const generation = this.generation;
    try {
      const threads = new Map(),
        warnings = [],
        states = payload.include_archived === false ? [false] : [false, true];
      let pages = 0,
        complete = true;
      for (const archived of states) {
        let cursor;
        const seen = new Set();
        do {
          if (pages >= maxPages) {
            complete = false;
            break;
          }
          const page = await this.history.list({
            cursor,
            archived,
            limit: 100,
          });
          pages++;
          fail(
            Array.isArray(page.data),
            "HOST_PROTOCOL_ERROR",
            "Native thread list did not return a page",
            502,
          );
          for (const row of page.data) {
            if (
              typeof row.id !== "string" ||
              typeof row.cwd !== "string" ||
              !isAbsolute(row.cwd)
            )
              continue;
            threads.set(row.id, {
              id: row.id,
              cwd: row.cwd,
              title: clipped(row.name ?? row.preview, 500) || "Untitled",
              status: statusOf(row),
              source:
                typeof row.source === "string"
                  ? clipped(row.source, 100)
                  : row.source && typeof row.source === "object"
                    ? redact(row.source)
                    : "unknown",
              thread_source: clipped(row.threadSource, 100) || null,
              updated_at: row.updatedAt,
              created_at: row.createdAt,
              parent_thread_id: clipped(row.parentThreadId, 160) || null,
              archived,
            });
          }
          cursor = page.nextCursor ?? null;
          if (cursor) {
            fail(
              typeof cursor === "string" && !seen.has(cursor),
              "HOST_PROTOCOL_ERROR",
              "Native history repeated its cursor",
              502,
            );
            seen.add(cursor);
          }
        } while (cursor);
      }
      const groups = new Map();
      for (const thread of threads.values()) {
        let root = resolve(thread.cwd),
          rootError = null;
        try {
          assertProjectRoot(root);
        } catch (error) {
          rootError = publicError(error);
        }
        if (this.#privateRoot(root))
          rootError = {
            code: "PRIVATE_PATH",
            message:
              "Native session root overlaps private application/account data; content was not read",
          };
        const key = "discovered-" + sha(root).slice(0, 20);
        if (!groups.has(key))
          groups.set(key, {
            id: key,
            root,
            name: basename(root),
            threads: [],
            root_error: rootError,
          });
        groups.get(key).threads.push(thread);
      }
      for (const project of this.store.list("project")) {
        const key = "discovered-" + sha(project.root).slice(0, 20);
        if (!groups.has(key))
          groups.set(key, {
            id: key,
            root: project.root,
            name: project.name,
            threads: [],
            root_error: null,
          });
      }
      this.rows.clear();
      this.details.clear();
      this.observedPages.clear();
      for (const group of groups.values()) {
        const binding = this.store
          .list("project")
          .find((x) => x.root === group.root);
        let view = null;
        if (!group.root_error)
          try {
            const currentRoot = assertProjectRoot(group.root);
            fail(
              currentRoot === group.root,
              "SOURCE_DRIFT",
              "Bound project root identity changed; inspect its new identity explicitly",
              409,
            );
            fail(
              !this.#privateRoot(currentRoot),
              "PRIVATE_PATH",
              "Bound project overlaps private service or account data",
              403,
            );
            view = await inspectProject(group.root, {
              sourceRefs: binding?.source_refs ?? [],
            });
          } catch (error) {
            group.root_error = publicError(error);
          }
        const jobs = binding
          ? this.store.list("job").filter((x) => x.project_id === binding.id)
          : [];
        const tasks = binding
          ? this.store.list("task").filter((x) => x.project_id === binding.id)
          : [];
        const next_actions = [...(view?.next_actions ?? [])];
        if (!view?.goal?.text)
          next_actions.push({
            text: "Establish the current project goal from a native source before dependent work",
            status: "proposed",
            source_ref: null,
          });
        if (!binding)
          next_actions.push({
            text: "Review and bind this discovered project before execution",
            status: "proposed",
            source_ref: null,
          });
        if (jobs.some((x) => x.status === "outcome_unknown"))
          next_actions.unshift({
            text: "Reconcile the unknown native job before another dispatch",
            status: "proposed",
            source_ref: null,
          });
        const known = [
          ...(view?.work_records ?? []),
          ...this.#serviceWork(binding?.id),
        ];
        const row = {
          id: group.id,
          name: binding?.name ?? group.name,
          root: group.root,
          binding_id: binding?.id ?? null,
          thread_count: group.threads.length,
          phase: view?.phase ?? "not_recorded",
          kind: view?.kind ?? binding?.kind ?? "generic",
          status: group.root_error
            ? "unavailable"
            : jobs.some((x) => x.status === "outcome_unknown")
              ? "attention"
              : "observed",
          goal: view?.goal ?? emptyGoal(),
          next_actions: next_actions.slice(0, 12),
          agents: view?.agents ?? [],
          work_groups: projectWorkGroups(known).map(
            ({ items, ...rest }) => rest,
          ),
          known_work_items: known.length,
          active: group.threads.filter((x) => x.status === "active").length,
          warnings: [
            ...(view?.warnings ?? []),
            ...(group.root_error ? [group.root_error] : []),
          ],
          source_revision: view?.revision ?? null,
          history_status: "not_loaded",
          native_state_present: view?.native_state_present ?? false,
        };
        this.rows.set(row.id, {
          row,
          threads: group.threads,
          root_error: group.root_error,
        });
      }
      fail(
        generation === this.generation,
        "SOURCE_DRIFT",
        "Service privacy/restore boundary changed during discovery; refresh again",
        409,
      );
      this.threadRows = threads;
      const projects = [...this.rows.values()]
        .map((x) => x.row)
        .sort((a, b) => b.active - a.active || a.name.localeCompare(b.name));
      this.snapshot = {
        status: "ready",
        checked_at: now(),
        coverage: {
          source: "public-native-thread-history",
          source_kinds: "all-supported-native-kinds",
          state_db_only: true,
          complete,
          truncated: !complete,
          pages,
          native_threads: threads.size,
          registered_projects: "not_available",
          work_history: "selected-project-only",
          include_archived: states.includes(true),
        },
        summary: {
          projects: projects.length,
          threads: threads.size,
          work_items: projects.reduce((n, x) => n + x.known_work_items, 0),
          active: projects.reduce((n, x) => n + x.active, 0),
          attention: projects.filter((x) => x.status !== "observed").length,
        },
        projects,
        warnings,
      };
      return this.snapshot;
    } catch (error) {
      if (generation !== this.generation) {
        this.rows.clear();
        this.threadRows.clear();
        this.details.clear();
        this.observedPages.clear();
      }
      this.snapshot = {
        ...this.snapshot,
        status: "stale",
        warnings: [publicError(error)],
      };
      throw error;
    } finally {
      this.busy = false;
    }
  }
  #serviceWork(projectId) {
    if (!projectId) return [];
    const tasks = this.store
      .list("task")
      .filter((x) => x.project_id === projectId);
    const jobs = this.store
      .list("job")
      .filter((x) => x.project_id === projectId);
    return tasks.map((task) => {
      const job = jobs.find((x) => x.task_id === task.id);
      const outcome = clipped(
        job?.output_text ?? job?.output ?? job?.result?.text,
        5000,
      );
      return {
        id: job?.id ?? task.id,
        task_id: task.id,
        job_id: job?.id ?? null,
        thread_id: job?.thread_id ?? null,
        turn_id: job?.turn_id ?? null,
        objective: clipped(task.objective, 1600),
        outcome,
        status:
          job?.status === "completed"
            ? outcome.trim()
              ? "answer_received"
              : "recorded"
            : (job?.status ?? task.status),
        native_status: job?.status ?? task.status,
        source: "service",
        source_ref: job ? `job:${job.id}` : `task:${task.id}`,
        evidence_refs: job
          ? [{ kind: "service_job", source_ref: `job:${job.id}` }]
          : [],
        skills: (task.capsule?.selected_skills ?? []).map((x) => ({
          name: x.name,
          status: "selected",
        })),
        owner_review: job?.review_status ?? null,
        acceptance:
          job?.review_status === "accepted" ? "owner-review" : "not_inferred",
        response_observed: !!outcome.trim(),
        execution_observed: job?.host_dispatch_started === true,
      };
    });
  }
  #observeProjectPage(id, found, result) {
    let observed = this.observedPages.get(id);
    if (
      !observed ||
      observed.snapshot !== result.coverage.snapshot_checked_at ||
      observed.revision !== result.project.source_revision
    ) {
      observed = {
        snapshot: result.coverage.snapshot_checked_at,
        revision: result.project.source_revision,
        pages: new Map(),
      };
      this.observedPages.set(id, observed);
    }
    observed.pages.set(result.coverage.thread_offset, result);
    const pages = [...observed.pages.values()].sort(
      (a, b) => a.coverage.thread_offset - b.coverage.thread_offset,
    );
    const work = new Map(),
      threadIds = new Set(),
      warnings = new Map();
    let contiguous = 0;
    for (const page of pages) {
      if (page.coverage.thread_offset === contiguous)
        contiguous += page.threads.length;
      for (const thread of page.threads) threadIds.add(thread.id);
      for (const group of page.work_groups)
        for (const item of group.items) {
          const key = workIdentity(item);
          work.set(key, mergeWork(work.get(key), item));
        }
      for (const warning of page.warnings)
        warnings.set(JSON.stringify(warning), warning);
    }
    const complete =
      contiguous === found.threads.length &&
      pages.every((page) => page.coverage.page_complete) &&
      this.snapshot.coverage.complete;
    Object.assign(found.row, {
      goal: result.goal,
      agents: result.agents,
      phase: result.project.phase,
      source_revision: result.project.source_revision,
      known_work_items: work.size,
      work_groups: projectWorkGroups([...work.values()]).map(
        ({ id: groupId, title, count }) => ({ id: groupId, title, count }),
      ),
      history_status: complete ? "observed" : "partial",
      history_coverage: {
        complete,
        threads_total: found.threads.length,
        threads_observed: threadIds.size,
        next_thread_offset:
          contiguous < found.threads.length ? contiguous : null,
        warnings: [...warnings.values()].length,
      },
    });
  }
  async project(
    id,
    {
      max_threads = 40,
      max_turn_pages = 4,
      thread_offset = 0,
      snapshot_checked_at,
    } = {},
  ) {
    const snapshotToken = this.snapshot.checked_at;
    const generation = this.generation;
    const found = this.rows.get(text(id, "discovered project id"));
    fail(
      found,
      "PROJECT_NOT_FOUND",
      "Refresh the native portfolio before selecting this project",
      404,
    );
    fail(
      found.root_error?.code !== "PRIVATE_PATH",
      "PRIVATE_PATH",
      "This native session root is private; history content is not imported",
      403,
    );
    fail(
      found.root_error?.code !== "SOURCE_DRIFT",
      "SOURCE_DRIFT",
      "The recorded project root changed; review its native identity explicitly",
      409,
    );
    fail(
      Number.isInteger(max_threads) && max_threads >= 1 && max_threads <= 100,
      "INVALID_INPUT",
      "max_threads must be1..100",
    );
    fail(
      Number.isInteger(max_turn_pages) &&
        max_turn_pages >= 1 &&
        max_turn_pages <= 20,
      "INVALID_INPUT",
      "max_turn_pages must be1..20",
    );
    fail(
      Number.isInteger(thread_offset) &&
        thread_offset >= 0 &&
        thread_offset <= found.threads.length,
      "INVALID_INPUT",
      "thread_offset must identify a position inside the discovered project history",
    );
    fail(
      (thread_offset === 0 && snapshot_checked_at === undefined) ||
        snapshot_checked_at === snapshotToken,
      "SOURCE_DRIFT",
      "Project history inventory changed; refresh before reading another page",
      409,
    );
    let current = null;
    const binding = this.store
      .list("project")
      .find((x) => x.root === found.row.root);
    if (!found.root_error) {
      const currentRoot = assertProjectRoot(found.row.root);
      fail(
        currentRoot === found.row.root,
        "SOURCE_DRIFT",
        "Discovered project root changed; refresh its native identity",
        409,
      );
      fail(
        !this.#privateRoot(currentRoot),
        "PRIVATE_PATH",
        "Project overlaps private service or account data",
        403,
      );
      current = await inspectProject(found.row.root, {
        sourceRefs: binding?.source_refs ?? [],
      });
    }
    const items = [
        ...(current?.work_records ?? []),
        ...this.#serviceWork(binding?.id),
      ],
      warnings = [];
    let pageComplete = true,
      pages = 0,
      turnsObserved = 0,
      threadsRead = 0,
      emptyHistoryThreads = 0;
    const sourceThreads = found.threads.slice(
      thread_offset,
      thread_offset + max_threads,
    );
    const nextThreadOffset =
      thread_offset + sourceThreads.length < found.threads.length
        ? thread_offset + sourceThreads.length
        : null;
    for (const thread of sourceThreads) {
      try {
        const meta = await this.history.read(thread.id);
        fail(
          meta.thread?.id === thread.id &&
            resolve(meta.thread.cwd) === resolve(thread.cwd),
          "SOURCE_DRIFT",
          "Native thread changed project ownership",
          409,
        );
        threadsRead++;
        const observedThread = {
          ...thread,
          source: meta.thread.source ?? thread.source,
          thread_source:
            clipped(meta.thread.threadSource ?? thread.thread_source, 100) ||
            null,
          parent_thread_id:
            clipped(
              meta.thread.parentThreadId ?? thread.parent_thread_id,
              160,
            ) || null,
        };
        let cursor;
        let threadTurns = 0;
        const seen = new Set();
        for (let i = 0; i < max_turn_pages; i++) {
          const page = await this.history.turns(thread.id, {
            cursor,
            limit: 50,
          });
          pages++;
          fail(
            Array.isArray(page.data),
            "HOST_PROTOCOL_ERROR",
            "Native turns did not return a page",
            502,
          );
          threadTurns += page.data.length;
          turnsObserved += page.data.length;
          for (const turn of page.data) {
            if (turn.itemsView && turn.itemsView !== "full") {
              pageComplete = false;
              warnings.push({
                thread_id: thread.id,
                turn_id: turn.id,
                code: "HISTORY_ITEMS_PARTIAL",
                message: "The native host returned a summary or unloaded items",
              });
            }
            const work = turnWork(observedThread, turn);
            if (work.warnings.length) {
              pageComplete = false;
              warnings.push(
                ...work.warnings.map((row) => ({
                  ...row,
                  thread_id: thread.id,
                  turn_id: turn.id,
                })),
              );
            }
            items.push(work);
          }
          cursor = page.nextCursor ?? null;
          if (!cursor) break;
          fail(
            typeof cursor === "string" && !seen.has(cursor),
            "HOST_PROTOCOL_ERROR",
            "Native turns repeated cursor",
            502,
          );
          seen.add(cursor);
        }
        if (cursor) {
          pageComplete = false;
          warnings.push({
            thread_id: thread.id,
            code: "NATIVE_TURN_PAGE_LIMIT",
            message:
              "More persisted turns remain beyond this page's configured turn limit",
            max_turn_pages,
          });
        }
        if (threadTurns === 0) {
          pageComplete = false;
          emptyHistoryThreads++;
          warnings.push({
            thread_id: thread.id,
            code: "NATIVE_HISTORY_EMPTY",
            message:
              "Native thread metadata exists but no persisted turns were returned; work-history coverage is unverified",
          });
        }
      } catch (error) {
        pageComplete = false;
        warnings.push({ thread_id: thread.id, ...publicError(error) });
      }
    }
    fail(
      generation === this.generation &&
        this.rows.get(id) === found &&
        this.snapshot.checked_at === snapshotToken,
      "SOURCE_DRIFT",
      "Service privacy/restore boundary changed during history read; refresh again",
      409,
    );
    const merged = new Map();
    for (const item of items) {
      const key = workIdentity(item);
      merged.set(key, mergeWork(merged.get(key), item));
    }
    const work = [...merged.values()];
    const project = {
      ...found.row,
      binding_id: binding?.id ?? null,
      name: binding?.name ?? found.row.name,
      ...(current
        ? {
            goal: current.goal,
            agents: current.agents,
            phase: current.phase,
            source_revision: current.revision,
          }
        : {}),
      history_status: "observed",
      known_work_items: work.length,
    };
    const complete =
      thread_offset === 0 &&
      nextThreadOffset === null &&
      pageComplete &&
      this.snapshot.coverage.complete;
    const result = {
      project,
      threads: sourceThreads,
      work_groups: projectWorkGroups(work),
      goal: project.goal,
      next_actions: project.next_actions,
      agents: project.agents,
      coverage: {
        complete,
        page_complete: pageComplete,
        discovery_complete: this.snapshot.coverage.complete,
        snapshot_checked_at: snapshotToken,
        thread_offset,
        next_thread_offset: nextThreadOffset,
        truncated: !complete,
        threads_total: found.threads.length,
        threads_read: threadsRead,
        threads_attempted: sourceThreads.length,
        turns_observed: turnsObserved,
        empty_history_threads: emptyHistoryThreads,
        turn_pages: pages,
        items: work.length,
        limits: { max_threads, max_turn_pages },
        native_acceptance_inferred: false,
      },
      warnings: [...project.warnings, ...warnings],
      checked_at: now(),
    };
    this.details.set(id, result);
    this.#observeProjectPage(id, found, result);
    return result;
  }
}
