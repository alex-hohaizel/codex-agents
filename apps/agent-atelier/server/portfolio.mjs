import { basename, isAbsolute, resolve } from "node:path";
import { homedir } from "node:os";
import { assertProjectRoot, inspectProject } from "./projects.mjs";
import {
  advanceAttachments,
  advanceInventory,
  nativeInventory,
  newAttachmentInventory,
  streamCoverage,
} from "./native-catalog.mjs";
import {
  digest,
  fail,
  id as newId,
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
const allowsRootBinding = (row) => row.binding_scope === "root";
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
  if (
    incoming.history_item_continuation &&
    previous.source === "native-history"
  ) {
    const responseObserved =
      previous.response_observed || incoming.response_observed;
    incoming = {
      ...incoming,
      objective: previous.objective_observed
        ? previous.objective
        : incoming.objective,
      objective_observed:
        previous.objective_observed || incoming.objective_observed,
      outcome: previous.response_observed ? previous.outcome : incoming.outcome,
      response_observed: responseObserved,
      status:
        incoming.native_status === "completed"
          ? responseObserved
            ? "answer_received"
            : "recorded"
          : incoming.status,
      response_item_id: previous.response_item_id ?? incoming.response_item_id,
    };
  }
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
    objective_observed: items.some(
      (item) => item.type === "userMessage" && itemText(item).trim(),
    ),
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
    response_item_id:
      items
        .filter((item) => item.type === "agentMessage" && itemText(item).trim())
        .at(-1)?.id ?? null,
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
  get projectCatalogAvailable() {
    return typeof this.#codex.projectCatalog === "function";
  }
  projectCatalog(options) {
    return this.#codex.projectCatalog(options);
  }
  get attachedThreadPaging() {
    return typeof this.#codex.attachedThreads === "function";
  }
  attachedThreads(owner, options) {
    return this.#codex.attachedThreads(owner, options);
  }
  read(id) {
    return this.#codex.readThread(id);
  }
  turns(id, options) {
    return this.#codex.historyTurns(id, options);
  }
  get itemPaging() {
    return typeof this.#codex.historyItems === "function";
  }
  items(id, options) {
    return this.#codex.historyItems(id, options);
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
    this.itemCursors = new Map();
    this.inventory = null;
    this.inventoryToken = null;
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
        registered_projects: "not_checked",
        registered_project_count: 0,
        registered_project_pages: 0,
        continuation: null,
        thread_streams: null,
        local_inventory_complete: false,
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
      const binding = allowsRootBinding(row)
        ? bindings.find((x) => x.root === row.root)
        : null;
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
    this.itemCursors.clear();
    this.inventory = null;
    this.inventoryToken = null;
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
        continuation: null,
        thread_streams: null,
        registered_projects: "not_checked",
        registered_project_count: 0,
        registered_project_pages: 0,
        local_inventory_complete: false,
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
  #rootError(root) {
    if (this.#privateRoot(root))
      return {
        code: "PRIVATE_PATH",
        message:
          "Native session root overlaps private application/account data; content was not read",
      };
    try {
      assertProjectRoot(root);
      return null;
    } catch (error) {
      return publicError(error);
    }
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
    const continuing = payload.continue_from !== undefined;
    fail(
      !continuing ||
        (typeof payload.continue_from === "string" &&
          payload.continue_from === this.inventoryToken &&
          this.inventory &&
          (payload.include_archived === undefined ||
            payload.include_archived === this.inventory.includeArchived)),
      "SOURCE_DRIFT",
      "This inventory continuation is no longer current; refresh the portfolio",
      409,
    );
    this.busy = true;
    const generation = this.generation;
    try {
      const { inventory, threads, warnings, projectError, overlapCount } =
        await advanceInventory(
          continuing
            ? this.inventory
            : nativeInventory(
                payload.include_archived !== false,
                this.history.projectCatalogAvailable,
              ),
          this.history,
          maxPages,
        );
      const active = streamCoverage(inventory.active),
        archived = streamCoverage(inventory.archived),
        catalog = streamCoverage(inventory.projects);
      const complete =
        active.complete &&
        (!archived || archived.complete) &&
        overlapCount === 0;
      const nextToken = [active, archived, catalog].some(
        (stream) => stream && !stream.exhausted,
      )
        ? newId("catalog")
        : null;
      const registeredProjects = !catalog
        ? "not_available"
        : catalog.complete && !projectError
          ? "observed"
          : catalog.count
            ? "partial"
            : projectError
              ? "unavailable"
              : "partial";
      const groups = new Map();
      const nativeProjects = [...(inventory.projects?.rows.values() ?? [])].map(
        (project) => ({
          ...project,
          roots: [...new Set(project.roots.map((root) => resolve(root)))],
        }),
      );
      const rootCounts = new Map();
      for (const project of nativeProjects)
        for (const root of project.roots)
          rootCounts.set(root, (rootCounts.get(root) ?? 0) + 1);
      const rootGroup = (root, nativeProject, unresolved = false) => {
        const shared = (rootCounts.get(root) ?? 0) > 1;
        const bindingScope = unresolved
          ? "native-unresolved-root"
          : nativeProject && shared
            ? "native-shared-root"
            : "root";
        const key =
          "discovered-" +
          sha(
            root && bindingScope === "root"
              ? root
              : JSON.stringify(["native-project", nativeProject.id, root]),
          ).slice(0, 20);
        if (!groups.has(key))
          groups.set(key, {
            id: key,
            root,
            name: nativeProject?.name || (root ? basename(root) : "Untitled"),
            threads: [],
            binding_scope: bindingScope,
            ownership_warning: unresolved
              ? {
                  code: "NATIVE_PROJECT_ROOT_UNRESOLVED",
                  message:
                    "The chat's native project assignment has no unique registered folder in this inventory",
                }
              : shared
                ? {
                    code: "NATIVE_PROJECT_ROOT_CONFLICT",
                    message:
                      "Multiple native projects use this folder. Chats with explicit assignments are shown with their own project",
                  }
                : null,
            native_project_ids: new Set(),
            root_error: root
              ? this.#rootError(root)
              : {
                  code: "NATIVE_PROJECT_WITHOUT_ROOT",
                  message: "This native project has no local folder",
                },
          });
        const group = groups.get(key);
        if (nativeProject) group.native_project_ids.add(nativeProject.id);
        return group;
      };
      const catalogGroups = new Map();
      const catalogById = new Map(
        nativeProjects.map((project) => [project.id, project]),
      );
      for (const project of nativeProjects) {
        catalogGroups.set(
          project.id,
          (project.roots.length ? project.roots : [null]).map((root) =>
            rootGroup(root, project),
          ),
        );
      }
      for (const thread of threads.values()) {
        const cwd = resolve(thread.cwd);
        const assigned = catalogGroups.get(thread.native_project_id) ?? [];
        const containing = assigned
          .filter((group) => group.root && isWithin(group.root, cwd))
          .sort((a, b) => b.root.length - a.root.length)[0];
        const canGroup = !this.#privateRoot(cwd);
        const assignedGroup =
          canGroup && (containing || (assigned.length === 1 && assigned[0]));
        const group =
          assignedGroup ||
          (thread.native_project_id
            ? rootGroup(
                cwd,
                catalogById.get(thread.native_project_id) ?? {
                  id: thread.native_project_id,
                },
                true,
              )
            : rootGroup(cwd));
        group.threads.push(thread);
      }
      const bindings = this.store.list("project");
      for (const project of bindings) rootGroup(project.root);
      const rows = new Map();
      for (const group of groups.values()) {
        const canBind = allowsRootBinding(group) && !!group.root;
        const binding = canBind
          ? bindings.find((x) => x.root === group.root)
          : null;
        let view = null;
        if (
          canBind &&
          !group.root_error &&
          (binding || group.threads.length > 0)
        )
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
        const next_actions = [...(view?.next_actions ?? [])];
        if (canBind && !view?.goal?.text)
          next_actions.push({
            text: "Establish the current project goal from a native source before dependent work",
            status: "proposed",
            source_ref: null,
          });
        if (canBind && !binding && !group.root_error)
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
        const nativeProjectIds = [...group.native_project_ids];
        const row = {
          id: group.id,
          name: binding?.name ?? group.name,
          root: group.root,
          binding_id: binding?.id ?? null,
          binding_scope: group.binding_scope,
          native_project_id:
            nativeProjectIds.length === 1 ? nativeProjectIds[0] : null,
          native_project_ids: nativeProjectIds,
          catalog_source:
            nativeProjectIds.length &&
            group.binding_scope !== "native-unresolved-root"
              ? "native_project_catalog"
              : group.threads.length
                ? "native_thread_history"
                : "service_binding",
          thread_count: group.threads.length,
          active_thread_count: group.threads.filter(
            (thread) => !thread.archived,
          ).length,
          archived_thread_count: group.threads.filter(
            (thread) => thread.archived,
          ).length,
          phase: view?.phase ?? "not_recorded",
          kind: view?.kind ?? binding?.kind ?? "generic",
          status: group.root_error
            ? "unavailable"
            : group.ownership_warning ||
                jobs.some((x) => x.status === "outcome_unknown")
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
            ...(group.ownership_warning ? [group.ownership_warning] : []),
            ...(group.root_error ? [group.root_error] : []),
          ],
          source_revision: view?.revision ?? null,
          history_status: "not_loaded",
          native_state_present: view?.native_state_present ?? false,
        };
        rows.set(row.id, {
          row,
          listedThreads: group.threads,
          threads: group.threads,
          root_error: group.root_error,
          attachments: null,
          attachmentToken: null,
          attachmentScan: null,
          historyGeneration: 0,
        });
      }
      fail(
        generation === this.generation,
        "SOURCE_DRIFT",
        "Service privacy/restore boundary changed during discovery; refresh again",
        409,
      );
      this.rows = rows;
      this.details.clear();
      this.observedPages.clear();
      this.itemCursors.clear();
      this.threadRows = threads;
      this.inventory = inventory;
      this.inventoryToken = nextToken;
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
          pages: active.pages + (archived?.pages ?? 0),
          native_threads: threads.size,
          scope: "local-native-index",
          thread_streams: { active, archived },
          registered_projects: registeredProjects,
          registered_project_count: catalog?.count ?? 0,
          registered_project_pages: catalog?.pages ?? 0,
          local_inventory_complete:
            complete && !!archived && registeredProjects === "observed",
          continuation: nextToken,
          attached_threads: this.history.attachedThreadPaging
            ? "selected-project-only"
            : "not_available",
          work_history: "selected-project-only",
          include_archived: !!archived,
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
        this.itemCursors.clear();
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
    const previous = observed.pages.get(result.coverage.thread_offset);
    if (result.coverage.item_continuation && previous) {
      const merged = new Map();
      for (const group of [...previous.work_groups, ...result.work_groups])
        for (const row of group.items)
          merged.set(
            workIdentity(row),
            mergeWork(merged.get(workIdentity(row)), row),
          );
      const cursors = new Map(
        (previous.coverage.item_cursors ?? []).map((row) => [
          row.thread_id,
          row,
        ]),
      );
      for (const row of result.coverage.item_cursors)
        cursors.set(row.thread_id, row);
      const pending = [...cursors.values()].some((row) => row.next_cursor);
      const nonItemComplete =
        previous.coverage.non_item_page_complete &&
        result.coverage.non_item_page_complete;
      const terminal = result.coverage.item_cursors.find(
        (row) => row.thread_id === result.coverage.item_thread_id,
      )?.items_complete;
      if (terminal)
        for (const row of merged.values())
          if (row.thread_id === result.coverage.item_thread_id)
            row.items_view = "full";
      observed.pages.set(result.coverage.thread_offset, {
        ...previous,
        project: result.project,
        work_groups: projectWorkGroups([...merged.values()]),
        coverage: {
          ...previous.coverage,
          item_cursors: [...cursors.values()],
          non_item_page_complete: nonItemComplete,
          page_complete: nonItemComplete && !pending,
        },
        warnings: uniqueRecords([
          ...previous.warnings.filter(
            (row) =>
              !(
                row.thread_id === result.coverage.item_thread_id &&
                ["NATIVE_ITEM_PAGE_LIMIT", "NATIVE_TURN_PAGE_LIMIT"].includes(
                  row.code,
                )
              ),
          ),
          ...result.warnings,
        ]),
      });
    } else observed.pages.set(result.coverage.thread_offset, result);
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
      result.coverage.discovery_complete;
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
  async #projectAttachments(found, continuation, assertCurrent) {
    if (!this.history.attachedThreadPaging) {
      fail(
        continuation === undefined,
        "CAPABILITY_UNVERIFIED",
        "The native host does not expose attached chat discovery",
        409,
      );
      return {
        status: "not_available",
        count: 0,
        pages: 0,
        complete: false,
        continuation: null,
      };
    }
    if (continuation !== undefined) {
      fail(
        typeof continuation === "string" &&
          continuation === found.attachmentToken,
        "SOURCE_DRIFT",
        "This attached chat continuation is no longer current; refresh the project",
        409,
      );
      fail(
        !found.attachmentScan,
        "CATALOG_BUSY",
        "Attached chat discovery is already running",
        409,
      );
    }
    if (
      !found.attachmentScan &&
      (!found.attachments || continuation !== undefined)
    ) {
      const previous =
        found.attachments ??
        newAttachmentInventory(
          found.listedThreads,
          this.snapshot.coverage.include_archived,
        );
      found.attachmentScan = (async () => {
        const verifiedOwners = new Map();
        const next = await advanceAttachments(
          previous,
          async (owner, options) => {
            if (!allowsRootBinding(found.row)) {
              if (!verifiedOwners.has(owner.id))
                verifiedOwners.set(
                  owner.id,
                  this.history.read(owner.id).then(({ thread }) => {
                    fail(
                      thread?.id === owner.id &&
                        thread.cwd === owner.cwd &&
                        (thread.projectId ?? null) === owner.native_project_id,
                      "SOURCE_DRIFT",
                      "An attachment owner changed its native project assignment",
                      409,
                    );
                  }),
                );
              await verifiedOwners.get(owner.id);
            }
            return this.history.attachedThreads(owner.id, options);
          },
          (thread) => {
            const cwd = resolve(thread.cwd);
            const sameRoot =
              cwd === found.row.root ||
              found.listedThreads.some((listed) => resolve(listed.cwd) === cwd);
            const belongs = thread.native_project_id
              ? found.row.native_project_ids.includes(thread.native_project_id)
              : sameRoot;
            return belongs && !this.#rootError(cwd);
          },
        );
        assertCurrent();
        found.attachments = next;
        found.attachmentToken = next.queue.length ? newId("attachments") : null;
        found.threads = [...found.listedThreads, ...next.rows.values()];
        found.row.thread_count = found.threads.length;
        found.row.active_thread_count = found.threads.filter(
          (thread) => !thread.archived,
        ).length;
        found.row.archived_thread_count = found.threads.filter(
          (thread) => thread.archived,
        ).length;
        if (continuation !== undefined) {
          found.historyGeneration++;
          this.details.delete(found.row.id);
          this.observedPages.delete(found.row.id);
          for (const thread of found.threads)
            this.itemCursors.delete(JSON.stringify([found.row.id, thread.id]));
        }
      })().finally(() => {
        found.attachmentScan = null;
      });
    }
    await found.attachmentScan;
    const state = found.attachments;
    const complete = !state.queue.length && !state.warnings.length;
    return {
      status: complete ? "observed" : "partial",
      count: state.rows.size,
      pages: state.pages,
      complete,
      continuation: found.attachmentToken,
    };
  }
  async #pagedTurns(threadId, maxTurnPages, prior) {
    const turns = new Map(),
      metadata = new Map(prior?.turn_metadata),
      unmatched = new Set(prior?.unmatched_turn_ids),
      warnings = [],
      metadataCursors = new Set(prior?.seen_turn_cursors);
    let cursor = prior?.turn_cursor,
      turnPages = 0,
      metadataTurns = 0;
    for (
      let pageIndex = 0;
      cursor !== null && pageIndex < maxTurnPages;
      pageIndex++
    ) {
      let page;
      try {
        page = await this.history.turns(threadId, {
          cursor,
          limit: 50,
          itemsView: "notLoaded",
        });
      } catch (error) {
        if (
          !prior &&
          error.code === "CODEX_RPC_ERROR" &&
          [-32601, -32602].includes(error.details?.rpc_code)
        )
          return { fallback: true };
        throw error;
      }
      turnPages++;
      fail(
        Array.isArray(page.data) && page.data.length <= 50,
        "HOST_PROTOCOL_ERROR",
        "Native turn metadata did not return a page",
        502,
      );
      for (const turn of page.data) {
        fail(
          typeof turn?.id === "string",
          "HOST_PROTOCOL_ERROR",
          "Native turn metadata has no turn identity",
          502,
        );
        if (!metadata.has(turn.id)) metadataTurns++;
        const record = { ...turn, items: [] };
        metadata.set(turn.id, record);
        turns.set(turn.id, { ...record, items: [] });
        unmatched.delete(turn.id);
      }
      const next = page.nextCursor ?? null;
      if (
        next &&
        (typeof next !== "string" ||
          next.length > 16384 ||
          metadataCursors.has(next))
      ) {
        warnings.push({
          code: "HOST_PROTOCOL_ERROR",
          message: "Native turns repeated or returned an invalid cursor",
        });
        cursor = null;
        break;
      }
      cursor = next;
      if (cursor) metadataCursors.add(cursor);
    }
    const maxItemPages = maxTurnPages * 2,
      itemCursors = new Set(prior?.seen_item_cursors),
      itemIds = new Set();
    let itemCursor = prior?.native_item_cursor ?? undefined,
      itemPages = 0,
      requests = 0,
      limit = 50,
      itemCount = 0,
      exhausted = prior?.items_exhausted === true,
      terminalError = prior?.items_terminal_error === true;
    while (
      !exhausted &&
      !terminalError &&
      itemPages < maxItemPages &&
      requests < maxItemPages + 6
    ) {
      let page;
      requests++;
      try {
        page = await this.history.items(threadId, {
          cursor: itemCursor,
          limit,
        });
      } catch (error) {
        if (
          !prior &&
          error.code === "CODEX_RPC_ERROR" &&
          error.details?.rpc_code === -32601
        )
          return { fallback: true };
        const oversized =
          error.code === "HOST_DISCONNECTED" &&
          /Protocol message exceeded limit/i.test(error.message);
        if (oversized && limit > 1) {
          limit = Math.max(1, Math.floor(limit / 2));
          continue;
        }
        warnings.push(
          oversized
            ? {
                code: "NATIVE_ITEM_TOO_LARGE",
                message:
                  "One persisted item exceeds the transport limit; its original content remains unread",
              }
            : publicError(error),
        );
        itemCursor = null;
        terminalError = true;
        break;
      }
      if (!Array.isArray(page.data) || page.data.length > limit) {
        warnings.push({
          code: "HOST_PROTOCOL_ERROR",
          message: "Native item history did not return a page",
        });
        itemCursor = null;
        terminalError = true;
        break;
      }
      itemPages++;
      let invalid = false;
      for (const entry of page.data) {
        if (
          typeof entry?.turnId !== "string" ||
          typeof entry.item?.id !== "string"
        ) {
          warnings.push({
            code: "HOST_PROTOCOL_ERROR",
            message: "A native item page has no usable turn/item identity",
          });
          invalid = true;
          continue;
        }
        const key = JSON.stringify([entry.turnId, entry.item.id]);
        if (itemIds.has(key)) continue;
        itemIds.add(key);
        itemCount++;
        if (!turns.has(entry.turnId)) {
          const known = metadata.get(entry.turnId);
          if (!known) unmatched.add(entry.turnId);
          turns.set(
            entry.turnId,
            known
              ? { ...known, items: [] }
              : {
                  id: entry.turnId,
                  status: "unknown",
                  items: [],
                  metadata_observed: false,
                },
          );
        }
        turns.get(entry.turnId).items.push(entry.item);
      }
      const next = page.nextCursor ?? null;
      if (invalid) {
        itemCursor = null;
        terminalError = true;
        break;
      }
      if (!next) {
        itemCursor = null;
        exhausted = true;
        break;
      }
      if (
        typeof next !== "string" ||
        next.length > 16384 ||
        itemCursors.has(next)
      ) {
        warnings.push({
          code: "HOST_PROTOCOL_ERROR",
          message: "Native items repeated or returned an invalid cursor",
        });
        itemCursor = null;
        terminalError = true;
        break;
      }
      itemCursors.add(next);
      itemCursor = next;
    }
    if (!exhausted && itemCursor)
      warnings.push({
        code: "NATIVE_ITEM_PAGE_LIMIT",
        message:
          "More persisted items remain; continue from this thread's observed item cursor",
        max_item_pages: maxItemPages,
      });
    if (!cursor)
      for (const turnId of unmatched)
        warnings.push({
          code: "NATIVE_ITEM_TURN_UNAVAILABLE",
          turn_id: turnId,
          message:
            "The native item has no matching turn metadata in the available history",
        });
    const totalItems = (prior?.total_items_observed ?? 0) + itemCount;
    if (exhausted && !cursor && metadata.size > 0 && totalItems === 0)
      warnings.push({
        code: "NATIVE_ITEMS_EMPTY",
        message:
          "Turn metadata exists but no persisted items were observed; content coverage is unverified",
      });
    for (const turn of turns.values()) {
      // Public item pages are descending; turnWork expects chronological items.
      turn.items.reverse();
      turn.itemsView =
        exhausted && !prior && !cursor && !warnings.length ? "full" : "partial";
    }
    const allTurns = [...turns.values()];
    return {
      turns: allTurns,
      completedTurnIds: [...metadata.values()]
        .filter((turn) => turn.status === "completed")
        .map((turn) => turn.id),
      answeredTurnIds: allTurns
        .filter((turn) =>
          turn.items.some(
            (item) => item.type === "agentMessage" && itemText(item).trim(),
          ),
        )
        .map((turn) => turn.id),
      turnPages,
      metadataTurns,
      totalMetadataTurns: metadata.size,
      turnCursor: cursor,
      itemPages,
      requests,
      itemCount,
      nextItemCursor: itemCursor ?? (cursor ? newId("history") : null),
      exhausted: exhausted && !cursor,
      limit,
      maxItemPages,
      warnings,
      continuationState: {
        turn_metadata: metadata,
        unmatched_turn_ids: unmatched,
        turn_cursor: cursor,
        seen_turn_cursors: metadataCursors,
        native_item_cursor: itemCursor,
        items_exhausted: exhausted,
        items_terminal_error: terminalError,
        seen_item_cursors: itemCursors,
        total_items_observed: totalItems,
      },
    };
  }
  async project(
    id,
    {
      max_threads = 40,
      max_turn_pages = 4,
      thread_offset = 0,
      snapshot_checked_at,
      item_thread_id,
      item_cursor,
      attachment_continue,
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
      attachment_continue === undefined ||
        (thread_offset === 0 &&
          snapshot_checked_at === snapshotToken &&
          item_thread_id === undefined &&
          item_cursor === undefined),
      "SOURCE_DRIFT",
      "Continue attached chats from the current project's first history page",
      409,
    );
    let historyGeneration;
    const assertCurrent = () =>
      fail(
        generation === this.generation &&
          this.rows.get(id) === found &&
          this.snapshot.checked_at === snapshotToken &&
          (historyGeneration === undefined ||
            historyGeneration === found.historyGeneration),
        "SOURCE_DRIFT",
        "Service privacy/restore boundary changed during history read; refresh again",
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
    const attachmentCoverage = await this.#projectAttachments(
      found,
      attachment_continue,
      assertCurrent,
    );
    historyGeneration = found.historyGeneration;
    const discoveryComplete =
      this.snapshot.coverage.complete &&
      (!this.history.attachedThreadPaging || attachmentCoverage.complete);
    let current = null;
    const canBind = allowsRootBinding(found.row);
    const binding = canBind
      ? this.store.list("project").find((x) => x.root === found.row.root)
      : null;
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
      if (canBind)
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
      nonItemPageComplete = true,
      pages = 0,
      itemPages = 0,
      itemRequests = 0,
      historyItemsObserved = 0,
      turnsObserved = 0,
      threadsRead = 0,
      emptyHistoryThreads = 0;
    const continuingItems =
      item_thread_id !== undefined || item_cursor !== undefined;
    let admission;
    if (continuingItems) {
      fail(
        this.history.itemPaging &&
          typeof item_thread_id === "string" &&
          typeof item_cursor === "string" &&
          item_cursor.length > 0 &&
          item_cursor.length <= 16384,
        "INVALID_INPUT",
        "Item continuation needs a supported thread and exact bounded item cursor",
      );
      admission = this.itemCursors.get(JSON.stringify([id, item_thread_id]));
      fail(
        admission &&
          admission.cursor === item_cursor &&
          admission.snapshot === snapshotToken &&
          admission.generation === generation &&
          admission.source_revision === (current?.revision ?? null) &&
          snapshot_checked_at === snapshotToken,
        "SOURCE_DRIFT",
        "This item cursor is not current for the selected project and source snapshot; refresh its history",
        409,
      );
      fail(
        found.threads.some((thread) => thread.id === item_thread_id),
        "SCOPE_MISMATCH",
        "This thread does not belong to the selected project",
        409,
      );
      nonItemPageComplete = admission.non_item_page_complete;
    }
    const sourceThreads = continuingItems
      ? [found.threads.find((thread) => thread.id === item_thread_id)]
      : found.threads.slice(thread_offset, thread_offset + max_threads);
    const nextThreadOffset = continuingItems
      ? admission.next_thread_offset
      : thread_offset + sourceThreads.length < found.threads.length
        ? thread_offset + sourceThreads.length
        : null;
    const itemContinuations = [];
    const pendingItemCursors = new Map();
    for (const thread of sourceThreads) {
      try {
        const cwd = resolve(thread.cwd);
        fail(
          !this.#privateRoot(cwd),
          "PRIVATE_PATH",
          "The native chat points to private application/account data",
          403,
        );
        if (cwd !== found.row.root) assertProjectRoot(cwd);
        const meta = await this.history.read(thread.id);
        fail(
          meta.thread?.id === thread.id &&
            typeof meta.thread.cwd === "string" &&
            isAbsolute(meta.thread.cwd) &&
            resolve(meta.thread.cwd) === cwd &&
            (meta.thread.projectId ?? null) === thread.native_project_id,
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
        if (this.history.itemPaging) {
          const observed = await this.#pagedTurns(
            thread.id,
            max_turn_pages,
            admission?.continuation_state,
          );
          if (!observed.fallback) {
            pages += observed.turnPages;
            turnsObserved += observed.metadataTurns;
            itemPages += observed.itemPages;
            itemRequests += observed.requests;
            historyItemsObserved += observed.itemCount;
            const answered = new Set([
              ...(admission?.answered_turn_ids ?? []),
              ...observed.answeredTurnIds,
            ]);
            const threadWarnings = [...observed.warnings];
            if (observed.turnCursor)
              threadWarnings.push({
                code: "NATIVE_TURN_PAGE_LIMIT",
                message:
                  "More persisted turns remain beyond this page's configured turn limit",
                max_turn_pages,
              });
            if (observed.totalMetadataTurns === 0) {
              emptyHistoryThreads++;
              threadWarnings.push({
                code: "NATIVE_HISTORY_EMPTY",
                message:
                  "Native thread metadata exists but no persisted turns were returned; work-history coverage is unverified",
              });
            }
            if (observed.exhausted) {
              for (const turnId of observed.completedTurnIds.filter(
                (turnId) => !answered.has(turnId),
              ))
                threadWarnings.push({
                  code: "NATIVE_COMPLETED_WITHOUT_ANSWER",
                  turn_id: turnId,
                  message:
                    "Native completion has no observed agent response after the item stream was read",
                });
            }
            if (
              threadWarnings.some(
                (warning) =>
                  ![
                    "NATIVE_ITEM_PAGE_LIMIT",
                    "NATIVE_TURN_PAGE_LIMIT",
                  ].includes(warning.code),
              )
            )
              nonItemPageComplete = false;
            if (threadWarnings.length || !observed.exhausted)
              pageComplete = false;
            warnings.push(
              ...threadWarnings.map((warning) => ({
                ...warning,
                thread_id: thread.id,
              })),
            );
            for (const turn of observed.turns) {
              const work = turnWork(observedThread, turn);
              work.history_item_continuation = continuingItems;
              // Missing answers remain provisional until the actual item stream is exhausted.
              if (!observed.exhausted || answered.has(turn.id))
                work.warnings = [];
              items.push(work);
            }
            const continuation = {
              thread_id: thread.id,
              next_cursor: observed.nextItemCursor ?? null,
              pages: observed.itemPages,
              items_observed: observed.itemCount,
              limit: observed.limit,
              items_complete: observed.exhausted,
              thread_offset: admission?.thread_offset ?? thread_offset,
            };
            itemContinuations.push(continuation);
            const key = JSON.stringify([id, thread.id]);
            pendingItemCursors.set(
              key,
              observed.nextItemCursor
                ? {
                    cursor: observed.nextItemCursor,
                    snapshot: snapshotToken,
                    generation,
                    source_revision: current?.revision ?? null,
                    answered_turn_ids: [...answered],
                    thread_offset: admission?.thread_offset ?? thread_offset,
                    next_thread_offset: nextThreadOffset,
                    continuation_state: observed.continuationState,
                  }
                : null,
            );
            continue;
          }
        }
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
              nonItemPageComplete = false;
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
              nonItemPageComplete = false;
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
          nonItemPageComplete = false;
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
          nonItemPageComplete = false;
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
        nonItemPageComplete = false;
        warnings.push({ thread_id: thread.id, ...publicError(error) });
      }
    }
    assertCurrent();
    if (continuingItems)
      fail(
        this.itemCursors.get(JSON.stringify([id, item_thread_id])) ===
          admission,
        "SOURCE_DRIFT",
        "This history continuation was already consumed; use the current page",
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
      known_work_items: work.length,
    };
    pageComplete = pageComplete && nonItemPageComplete;
    for (const [key, pending] of pendingItemCursors)
      if (pending)
        this.itemCursors.set(key, {
          ...pending,
          non_item_page_complete: nonItemPageComplete,
        });
      else this.itemCursors.delete(key);
    const complete =
      !continuingItems &&
      thread_offset === 0 &&
      nextThreadOffset === null &&
      pageComplete &&
      discoveryComplete;
    const result = {
      project: {
        ...project,
        history_status: complete ? "observed" : "partial",
      },
      threads: sourceThreads,
      work_groups: projectWorkGroups(work),
      goal: project.goal,
      next_actions: project.next_actions,
      agents: project.agents,
      coverage: {
        complete,
        page_complete: pageComplete,
        non_item_page_complete: nonItemPageComplete,
        item_continuation: continuingItems,
        ...(continuingItems
          ? { item_thread_id, consumed_item_cursor: item_cursor }
          : {}),
        item_cursors: itemContinuations,
        discovery_complete: discoveryComplete,
        attachments: attachmentCoverage,
        snapshot_checked_at: snapshotToken,
        thread_offset: admission?.thread_offset ?? thread_offset,
        next_thread_offset: nextThreadOffset,
        truncated: !complete,
        threads_total: found.threads.length,
        threads_read: threadsRead,
        threads_attempted: sourceThreads.length,
        turns_observed: turnsObserved,
        empty_history_threads: emptyHistoryThreads,
        turn_pages: pages,
        item_pages: itemPages,
        history_item_requests: itemRequests,
        history_items_observed: historyItemsObserved,
        items: work.length,
        limits: {
          max_threads,
          max_turn_pages,
          max_item_pages_per_thread: max_turn_pages * 2,
          max_item_requests_per_thread: max_turn_pages * 2 + 6,
          items_per_page: 50,
        },
        native_acceptance_inferred: false,
      },
      warnings: [
        ...project.warnings,
        ...(found.attachments?.warnings ?? []),
        ...warnings,
      ],
      checked_at: now(),
    };
    this.details.set(id, result);
    this.#observeProjectPage(id, found, result);
    return result;
  }
}
