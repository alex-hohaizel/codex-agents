export type Data = Record<string, any>;
export function nativeRootCanBind(row?: Data | null) {
  return row?.binding_scope == null || row.binding_scope === "root";
}

export interface Project extends Data {
  id: string;
  name: string;
  root: string;
  kind: string;
  revision: string;
  phase?: string;
  status?: string;
  summary?: string;
  capabilities?: Data;
}

export interface Bootstrap extends Data {
  version: string;
  instance_id: string;
  csrf_token: string;
  locale: string;
  projects: Project[];
  jobs: Data[];
  skills: { summary: Data; entries: Data[] };
  capabilities: { codex?: Data; work?: Data };
  activity: Data[];
  metrics: Data;
}

export interface Workspace extends Data {
  project: Project;
  sources: Data[];
  requirements: Data[];
  decisions: Data[];
  artifacts: Data[];
  identity: Data | Data[];
  jobs: Data[];
  context: Data;
  readiness: Data[] | Data;
}

export class ApiError extends Error {
  code: string;
  details: unknown;
  status: number;
  constructor(
    message: string,
    code = "REQUEST_FAILED",
    details: unknown = null,
    status = 0,
  ) {
    super(message);
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

export function mergePortfolioPage(previous: Data | null, page: Data): Data {
  const incoming = page.coverage ?? {};
  const offset = Number(incoming.thread_offset ?? 0);
  const prior = previous?.coverage ?? {};
  const continuingItems = incoming.item_continuation === true;
  const consumedKey = continuingItems
    ? stableJson([incoming.item_thread_id, incoming.consumed_item_cursor])
    : "";
  if (continuingItems && !previous)
    throw new ApiError(
      "Read the project history before continuing its items.",
      "SOURCE_DRIFT",
    );
  if (previous && (offset !== 0 || continuingItems)) {
    if (
      previous.project?.id !== page.project?.id ||
      prior.snapshot_checked_at !== incoming.snapshot_checked_at ||
      (previous.project?.source_revision &&
        page.project?.source_revision &&
        previous.project.source_revision !== page.project.source_revision)
    )
      throw new ApiError(
        "Project history changed; refresh before reading another page.",
        "SOURCE_DRIFT",
      );
    if (continuingItems) {
      if ((prior.loaded_item_cursors ?? []).includes(consumedKey))
        return previous;
      const expected = (prior.item_cursors ?? []).find(
        (item: Data) => item.thread_id === incoming.item_thread_id,
      );
      if (
        typeof incoming.item_thread_id !== "string" ||
        typeof incoming.consumed_item_cursor !== "string" ||
        !incoming.consumed_item_cursor ||
        expected?.next_cursor !== incoming.consumed_item_cursor ||
        !(prior.loaded_thread_offsets ?? []).includes(offset)
      )
        throw new ApiError(
          "History item cursor changed; refresh this project before continuing.",
          "SOURCE_DRIFT",
        );
    } else if ((prior.loaded_thread_offsets ?? []).includes(offset))
      return previous;
    else if (prior.next_thread_offset !== offset)
      throw new ApiError(
        "Read the next project history page in order.",
        "SOURCE_DRIFT",
      );
  }
  const base = continuingItems ? previous : offset === 0 ? null : previous;
  if (!base && offset !== 0)
    throw new ApiError(
      "Read the first project history page again.",
      "SOURCE_DRIFT",
    );
  const groups = new Map<string, Data>();
  const items = new Map<string, { group: string; item: Data }>();
  for (const group of [
    ...(base?.work_groups ?? []),
    ...(page.work_groups ?? []),
  ]) {
    groups.set(group.id, { ...group, items: [], count: 0 });
    for (const sourceItem of group.items ?? []) {
      let item = sourceItem;
      const key =
        item.thread_id && item.turn_id
          ? `turn:${JSON.stringify([item.thread_id, item.turn_id])}`
          : `id:${item.id}`;
      const old = items.get(key);
      if (!old)
        items.set(key, {
          group:
            item.work_type === "permission_review" ? "system_checks" : group.id,
          item,
        });
      else {
        if (
          continuingItems &&
          item.source === "native-history" &&
          old.item.source === "native-history"
        ) {
          const responseObserved =
            old.item.response_observed === true ||
            item.response_observed === true;
          item = {
            ...item,
            objective: old.item.objective_observed
              ? old.item.objective
              : item.objective,
            objective_observed:
              old.item.objective_observed === true ||
              item.objective_observed === true,
            outcome: old.item.response_observed
              ? old.item.outcome
              : item.outcome,
            response_item_id:
              old.item.response_item_id ?? item.response_item_id,
            response_observed: responseObserved,
            status:
              item.native_status === "completed"
                ? responseObserved
                  ? "answer_received"
                  : "recorded"
                : item.status,
          };
        }
        const native =
          item.source === "native-history"
            ? item
            : old.item.source === "native-history"
              ? old.item
              : null;
        const merged = { ...old.item, ...item, ...(native ?? {}) };
        for (const field of ["job_id", "service_job_id", "task_id"])
          merged[field] = item[field] ?? old.item[field] ?? null;
        merged.service_job_id ??= merged.job_id;
        merged.owner_review =
          item.owner_review ?? old.item.owner_review ?? null;
        const reviewedAcceptance =
          item.owner_review != null ? item.acceptance : old.item.acceptance;
        merged.acceptance =
          merged.owner_review === "accepted"
            ? "owner-review"
            : merged.owner_review != null
              ? reviewedAcceptance === "owner-review"
                ? "not_inferred"
                : (reviewedAcceptance ?? "not_inferred")
              : (item.acceptance ?? old.item.acceptance ?? "not_inferred");
        for (const field of ["evidence_refs", "skills", "warnings"])
          merged[field] = [
            ...new Map(
              [...(old.item[field] ?? []), ...(item[field] ?? [])].map(
                (value: unknown) => [stableJson(value), value],
              ),
            ).values(),
          ];
        merged.response_observed =
          old.item.response_observed === true ||
          item.response_observed === true;
        merged.execution_observed =
          old.item.execution_observed === true ||
          item.execution_observed === true;
        items.set(key, {
          group:
            merged.work_type === "permission_review"
              ? "system_checks"
              : continuingItems && native
                ? nativeWorkGroup(merged.status)
                : native === old.item
                  ? old.group
                  : group.id,
          item: merged,
        });
      }
    }
  }
  for (const { group, item } of items.values()) {
    if (!groups.has(group))
      groups.set(group, { id: group, title: group, items: [], count: 0 });
    groups.get(group)!.items.push(item);
  }
  const work_groups = [...groups.values()]
    .filter((group) => group.items.length)
    .map((group): Data => ({ ...group, count: group.items.length }))
    .sort(
      (a, b) =>
        Number(a.id === "system_checks") - Number(b.id === "system_checks"),
    );
  const threads = [
    ...new Map(
      [...(base?.threads ?? []), ...(page.threads ?? [])].map(
        (thread: Data) => [thread.id, thread],
      ),
    ).values(),
  ];
  const warnings = [
    ...new Map(
      [
        ...(base?.warnings ?? []).filter(
          (warning: Data) =>
            !(
              continuingItems &&
              warning.thread_id === incoming.item_thread_id &&
              ["NATIVE_ITEM_PAGE_LIMIT", "NATIVE_TURN_PAGE_LIMIT"].includes(
                warning.code,
              )
            ),
        ),
        ...(page.warnings ?? []),
      ].map((warning: Data) => [stableJson(warning), warning]),
    ).values(),
  ];
  const pageStates = new Map<number, boolean>(
    (base ? (prior.thread_page_states ?? []) : []).map((item: Data) => [
      item.offset,
      item.non_item_complete === true,
    ]),
  );
  const nonItemComplete =
    incoming.non_item_page_complete === undefined
      ? incoming.page_complete === true
      : incoming.non_item_page_complete === true;
  pageStates.set(
    offset,
    continuingItems
      ? pageStates.get(offset) === true && nonItemComplete
      : nonItemComplete,
  );
  const itemCursors = new Map<string, Data>(
    (base ? (prior.item_cursors ?? []) : []).map((item: Data) => [
      item.thread_id,
      item,
    ]),
  );
  for (const cursor of incoming.item_cursors ?? []) {
    const before = itemCursors.get(cursor.thread_id);
    itemCursors.set(cursor.thread_id, {
      ...before,
      ...cursor,
      pages:
        (continuingItems ? Number(before?.pages ?? 0) : 0) +
        Number(cursor.pages ?? 0),
      items_observed:
        (continuingItems ? Number(before?.items_observed ?? 0) : 0) +
        Number(cursor.items_observed ?? 0),
    });
  }
  const allItemsComplete = [...itemCursors.values()].every(
    (item) => item.next_cursor == null && item.items_complete === true,
  );
  const allPagesComplete =
    [...pageStates.values()].every(Boolean) && allItemsComplete;
  const nextThreadOffset = continuingItems
    ? prior.next_thread_offset
    : incoming.next_thread_offset;
  const totalThreads = continuingItems
    ? (prior.threads_total ?? incoming.threads_total)
    : incoming.threads_total;
  const discoveryComplete = continuingItems
    ? prior.discovery_complete !== false &&
      incoming.discovery_complete !== false
    : incoming.discovery_complete !== false;
  const complete =
    allPagesComplete &&
    discoveryComplete &&
    nextThreadOffset == null &&
    threads.length >= (totalThreads ?? 0);
  const coverage: Data = {
    ...incoming,
    thread_offset: 0,
    latest_thread_offset: continuingItems ? prior.latest_thread_offset : offset,
    next_thread_offset: nextThreadOffset,
    threads_total: totalThreads,
    discovery_complete: discoveryComplete,
    loaded_thread_offsets: [
      ...(base ? (prior.loaded_thread_offsets ?? []) : []),
      ...(continuingItems ? [] : [offset]),
    ],
    loaded_item_cursors: [
      ...(base ? (prior.loaded_item_cursors ?? []) : []),
      ...(continuingItems ? [consumedKey] : []),
    ],
    thread_page_states: [...pageStates].map(([offset, non_item_complete]) => ({
      offset,
      non_item_complete,
    })),
    item_cursors: [...itemCursors.values()],
    accumulated_page_complete: allPagesComplete,
    complete,
    truncated: !complete,
    items: items.size,
  };
  for (const key of ["turn_pages", "item_pages", "history_items_observed"])
    coverage[key] =
      (base ? Number(prior[key] ?? 0) : 0) + Number(incoming[key] ?? 0);
  for (const key of [
    "threads_read",
    "threads_attempted",
    "empty_history_threads",
  ])
    coverage[key] = continuingItems
      ? Number(prior[key] ?? 0)
      : (base ? Number(prior[key] ?? 0) : 0) + Number(incoming[key] ?? 0);
  const nativeTurns = (groups: Data[]) =>
    new Set(
      groups.flatMap((group) =>
        (group.items ?? [])
          .filter(
            (item: Data) =>
              item.source === "native-history" &&
              item.thread_id &&
              item.turn_id,
          )
          .map((item: Data) => stableJson([item.thread_id, item.turn_id])),
      ),
    );
  coverage.turns_observed = continuingItems
    ? Number(prior.turns_observed ?? 0) +
      Math.max(
        0,
        nativeTurns(work_groups).size -
          nativeTurns(base?.work_groups ?? []).size,
      )
    : (base ? Number(prior.turns_observed ?? 0) : 0) +
      Number(incoming.turns_observed ?? 0);
  return {
    ...page,
    project: { ...page.project, known_work_items: items.size },
    threads,
    work_groups,
    warnings,
    coverage,
  };
}

function nativeWorkGroup(status: string) {
  if (
    [
      "failed",
      "interrupted",
      "outcome_unknown",
      "awaiting_approval",
      "awaiting_input",
    ].includes(status)
  )
    return "attention";
  if (
    [
      "in_progress",
      "inProgress",
      "running",
      "queued",
      "dispatching",
      "gating",
    ].includes(status)
  )
    return "active";
  if (["answer_received", "completed"].includes(status)) return "results";
  if (status === "recorded") return "recorded";
  if (["prepared", "paused"].includes(status)) return "prepared";
  return "other";
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value !== null && typeof value === "object")
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, child]) => `${JSON.stringify(key)}:${stableJson(child)}`)
      .join(",")}}`;
  return JSON.stringify(value) ?? "undefined";
}

const SESSION_PROOF_KEY = "atelier.session.csrf.v1";
const sessionSubscribers = new Set<() => void>();
function storedProof(): string | null {
  try { return typeof window === "undefined" ? null : window.sessionStorage.getItem(SESSION_PROOF_KEY); }
  catch { return null; }
}
let browserProof = storedProof();
function rememberProof(value: unknown) {
  if (typeof value !== "string" || !value || value.length > 256)
    throw new ApiError("The local session returned an invalid browser proof.", "INVALID_RESPONSE");
  browserProof = value;
  try { window.sessionStorage.setItem(SESSION_PROOF_KEY, value); } catch { /* The active tab can still use its in-memory proof. */ }
  for (const notify of sessionSubscribers) notify();
}
function clearProof() {
  browserProof = null;
  try { window.sessionStorage.removeItem(SESSION_PROOF_KEY); } catch { /* No persistent proof was available. */ }
}
function privateHeaders(initial?: HeadersInit): Headers {
  const headers = new Headers();
  if (browserProof) headers.set("X-Atelier-CSRF", browserProof);
  new Headers(initial).forEach((value, key) => headers.set(key, value));
  return headers;
}
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    credentials: "same-origin",
    ...init,
    headers: privateHeaders(init?.headers),
  });
  let body: any;
  try {
    body = await response.json();
  } catch {
    throw new ApiError(
      `HTTP ${response.status}`,
      "INVALID_RESPONSE",
      null,
      response.status,
    );
  }
  if (!response.ok || body?.error) {
    const error = body?.error ?? body;
    throw new ApiError(
      error.message ?? response.statusText,
      error.code ?? "REQUEST_FAILED",
      error.details,
      response.status,
    );
  }
  return body;
}

function takeLaunchToken(): string | null {
  if (typeof window === "undefined") return null;
  const fragment = new URLSearchParams(window.location.hash.slice(1));
  if (!fragment.has("atelier_launch")) return null;
  const token = fragment.get("atelier_launch");
  fragment.delete("atelier_launch");
  const remaining = fragment.toString();
  // Consume the owner bootstrap before rendering, fetching, or opening SSE.
  // Keep it out of history, screenshots, local storage, and subsequent links.
  window.history.replaceState(
    window.history.state,
    "",
    `${window.location.pathname}${window.location.search}${remaining ? `#${remaining}` : ""}`,
  );
  return token;
}

let launchToken = takeLaunchToken();
let sessionReady: Promise<unknown> | null = null;

async function establishSession(): Promise<unknown> {
  const token = launchToken;
  launchToken = null;
  try {
    if (!token && !browserProof)
      throw new ApiError("Open this browser session with the local launcher.", "LAUNCH_REQUIRED", null, 401);
    const session = await request<Data>(
      "/session",
      token
        ? {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ launch_token: token }),
          }
        : undefined,
    );
    rememberProof(session.csrf_token);
    return session;
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      clearProof();
      throw new ApiError(
        "Open this browser session with the local launcher.",
        "LAUNCH_REQUIRED",
        { cause: error.code },
        error.status,
      );
    }
    throw error;
  }
}

export interface ServiceEvent { type: string; data: string; lastEventId: string; }
export function subscribeEvents(onEvent: (event: ServiceEvent) => void, options: { onError?: (error: unknown) => void; reconnectMs?: number } = {}) {
  let closed = false, pausedForAuth = false, running = false;
  let controller: AbortController | null = null;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let lastEventId = "", delay = options.reconnectMs ?? 1000;
  const schedule = (milliseconds = delay) => {
    if (closed) return;
    clearTimeout(timer); timer = setTimeout(() => void connect(), milliseconds);
  };
  const sessionReadyAgain = () => { if (pausedForAuth && !closed) { pausedForAuth = false; schedule(0); } };
  sessionSubscribers.add(sessionReadyAgain);
  async function connect() {
    if (closed || running) return;
    running = true; controller = new AbortController();
    let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
    try {
      await prepareSession();
      if (closed) return;
      const headers = privateHeaders({ Accept: "text/event-stream" });
      if (lastEventId) headers.set("Last-Event-ID", lastEventId);
      const response = await fetch("/api/v1/events", { credentials: "same-origin", cache: "no-store", headers, signal: controller.signal });
      if (!response.ok) throw new ApiError("The local event stream is unavailable.", "SESSION_REQUIRED", null, response.status);
      if (!response.headers.get("content-type")?.startsWith("text/event-stream") || !response.body)
        throw new ApiError("Invalid local event stream.", "INVALID_RESPONSE");
      reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "", data: string[] = [], kind = "message", identifier: string | null = null;
      const line = (value: string) => {
        if (!value) {
          if (identifier !== null && Number(identifier) > 0) lastEventId = identifier;
          if (data.length) onEvent({ type: kind, data: data.join("\n"), lastEventId });
          data = []; kind = "message"; identifier = null; return;
        }
        if (value.startsWith(":")) return;
        const colon = value.indexOf(":"), field = colon < 0 ? value : value.slice(0, colon);
        const body = colon < 0 ? "" : value.slice(colon + 1).replace(/^ /, "");
        if (field === "data") data.push(body);
        else if (field === "event") kind = body;
        else if (field === "id" && /^\d+$/.test(body) && Number.isSafeInteger(Number(body))) identifier = body;
        else if (field === "retry" && /^\d+$/.test(body)) delay = Math.max(250, Math.min(30000, Number(body)));
      };
      while (!closed) {
        const result = await reader.read();
        if (result.done) break;
        buffer += decoder.decode(result.value, { stream: true });
        if (buffer.length + data.join("\n").length > 4 * 1024 * 1024)
          throw new ApiError("Local event frame exceeds its bound.", "CAPACITY_LIMIT");
        let ending;
        while ((ending = buffer.indexOf("\n")) >= 0) {
          line(buffer.slice(0, ending).replace(/\r$/, "")); buffer = buffer.slice(ending + 1);
        }
      }
    } catch (error) {
      if (!closed) {
        if (error instanceof ApiError && (error.status === 401 || error.status === 403)) pausedForAuth = true;
        options.onError?.(error);
      }
    } finally {
      try { await reader?.cancel(); } catch { /* The fetch may already have been aborted. */ }
      running = false;
      if (!closed && !pausedForAuth) schedule();
    }
  }
  void connect();
  return { close() { closed = true; clearTimeout(timer); controller?.abort(); sessionSubscribers.delete(sessionReadyAgain); } };
}

function prepareSession(): Promise<unknown> {
  if (!sessionReady)
    sessionReady = establishSession().catch((error) => {
      sessionReady = null;
      throw error;
    });
  return sessionReady;
}

export const api = {
  async bootstrap() {
    const incoming = takeLaunchToken();
    if (incoming) {
      launchToken = incoming;
      sessionReady = null;
    }
    await prepareSession();
    try {
      const result = await request<Bootstrap>("/bootstrap");
      if (result.csrf_token) rememberProof(result.csrf_token);
      return result;
    } catch (error) {
      if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
        sessionReady = null;
        await prepareSession();
        return request<Bootstrap>("/bootstrap");
      }
      throw error;
    }
  },
  events: subscribeEvents,
  async artifactBlob(projectId: string, path: string, signal?: AbortSignal) {
    const response = await fetch(`/api/v1/projects/${encodeURIComponent(projectId)}/artifact?path=${encodeURIComponent(path)}`, {
      credentials: "same-origin", headers: privateHeaders(), signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(body.error?.message ?? "The artifact is unavailable.", body.error?.code ?? "ARTIFACT_UNAVAILABLE", body.error?.details, response.status);
    }
    const type = response.headers.get("content-type")?.split(";")[0].toLowerCase();
    if (!type || !["image/png", "image/jpeg", "image/webp", "image/gif", "application/pdf", "audio/mpeg", "audio/wav", "audio/mp4", "video/mp4", "video/webm", "text/plain"].includes(type))
      throw new ApiError("The artifact returned an unsupported preview type.", "INVALID_RESPONSE");
    return response.blob();
  },
  workspace: (id: string) =>
    request<Workspace>(`/projects/${encodeURIComponent(id)}/workspace`),
  doctor: () => request<Data>("/doctor"),
  integrations: (locale?: string) =>
    request<Data>(locale ? `/integrations?${new URLSearchParams({ locale })}` : "/integrations"),
  generateImage: (prompt: string, csrf: string, choice?: { project_id: string; production_phase: "explore" | "implement" }) =>
    request<Data>("/integrations/generation", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Atelier-CSRF": csrf },
      body: JSON.stringify({ prompt, ...choice }),
    }),
  integrationDetails: (kind: string, id: string, locale?: string) =>
    request<Data>(`/integrations/inspect?${new URLSearchParams({ kind, id, ...(locale ? { locale } : {}) })}`),
  readIntegration: (
    operation: string,
    args: Record<string, string>,
    csrf: string,
  ) =>
    request<Data>("/integrations/read", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Atelier-CSRF": csrf },
      body: JSON.stringify({ operation, arguments: args }),
    }),
  skills: (query = "") =>
    request<Data>(`/skills?q=${encodeURIComponent(query)}`),
  skillSource: (name: string) =>
    request<Data>(`/skills/${encodeURIComponent(name)}/source`),
  diff: (projectId: string, path?: string) =>
    request<Data>(
      `/projects/${encodeURIComponent(projectId)}/diff${path ? `?path=${encodeURIComponent(path)}` : ""}`,
    ),
  job: (id: string) => request<Data>(`/jobs/${encodeURIComponent(id)}`),
  receipt: (id: string) => request<Data>(`/commands/${encodeURIComponent(id)}`),
  portfolio: () => request<Data>("/portfolio"),
  portfolioProject: (
    id: string,
    options: {
      thread_offset?: number;
      snapshot_checked_at?: string;
      item_thread_id?: string;
      item_cursor?: string;
      attachment_continue?: string;
    } = {},
  ) => {
    const query = new URLSearchParams();
    if (options.thread_offset !== undefined)
      query.set("thread_offset", String(options.thread_offset));
    if (options.snapshot_checked_at)
      query.set("snapshot_checked_at", options.snapshot_checked_at);
    if (options.item_thread_id !== undefined)
      query.set("item_thread_id", options.item_thread_id);
    if (options.item_cursor !== undefined)
      query.set("item_cursor", options.item_cursor);
    if (options.attachment_continue !== undefined)
      query.set("attachment_continue", options.attachment_continue);
    return request<Data>(
      `/portfolio/projects/${encodeURIComponent(id)}${query.size ? `?${query}` : ""}`,
    );
  },
  threads: (projectId: string, cursor?: string) =>
    request<Data>(
      `/projects/${encodeURIComponent(projectId)}/threads${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`,
    ),
  async command(
    operation: string,
    payload: Data,
    csrf: string,
    project?: Project,
  ) {
    const commandId = crypto.randomUUID();
    try {
      return await request<Data>("/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Atelier-CSRF": csrf },
        body: JSON.stringify({
          command_id: commandId,
          operation,
          project_id: project?.id,
          expected_revision: project?.revision,
          payload,
        }),
      });
    } catch (error) {
      const e =
        error instanceof ApiError
          ? error
          : new ApiError(
              error instanceof Error ? error.message : String(error),
              "COMMAND_OUTCOME_UNKNOWN",
            );
      throw new ApiError(
        e.message,
        e.status && e.status < 500 ? e.code : "COMMAND_OUTCOME_UNKNOWN",
        {
          command_id: commandId,
          operation,
          project_id: project?.id,
          cause: e.details,
        },
        e.status,
      );
    }
  },
  async source(projectId: string, path: string) {
    return request<Data>(
      `/projects/${encodeURIComponent(projectId)}/source?path=${encodeURIComponent(path)}`,
    );
  },
  async artifactReport(
    projectId: string,
    artifact: Data,
    indexedSource?: Data,
    signal?: AbortSignal,
  ) {
    const path = artifact.path ?? artifact.relative_path;
    const bytes = artifact.bytes ?? artifact.size;
    const maxBytes = 1024 * 1024;
    if (
      typeof path !== "string" ||
      path.length > 4096 ||
      !/\.(md|markdown)$/i.test(path) ||
      path.startsWith("/") ||
      path.split(/[\\/]/).includes("..") ||
      !Number.isSafeInteger(bytes) ||
      bytes < 0 ||
      bytes > maxBytes
    )
      throw new ApiError(
        "A readable report needs a current indexed path and size within 1 MiB. Refresh the project or open the original file.",
        "ARTIFACT_REPORT_UNAVAILABLE",
      );
    const boundSource =
      indexedSource?.path === path ? indexedSource : undefined;
    const declaredHashes = [artifact.sha256, boundSource?.sha256].filter(
      (hash) => hash !== undefined && hash !== null,
    );
    if (
      declaredHashes.some(
        (hash) => typeof hash !== "string" || !/^[a-f0-9]{64}$/i.test(hash),
      ) ||
      new Set(declaredHashes.map((hash: string) => hash.toLowerCase())).size >
        1 ||
      (boundSource?.bytes !== undefined && boundSource.bytes !== bytes)
    )
      throw new ApiError(
        "The indexed report source changed. Refresh the project before reading it.",
        "SOURCE_DRIFT",
      );
    const expectedHash = declaredHashes[0]?.toLowerCase();
    const source = await request<Data>(
      `/projects/${encodeURIComponent(projectId)}/source?path=${encodeURIComponent(path)}`,
      { signal },
    );
    if (
      source.path !== path ||
      source.bytes !== bytes ||
      typeof source.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/i.test(source.sha256) ||
      (expectedHash !== undefined &&
        source.sha256.toLowerCase() !== expectedHash) ||
      source.truncated === true ||
      typeof source.content !== "string" ||
      new TextEncoder().encode(source.content).byteLength > maxBytes ||
      source.content.includes("\0")
    )
      throw new ApiError(
        "The report path, hash, size or bounded text no longer matches this selection. Refresh the project or open the original file.",
        "SOURCE_DRIFT",
      );
    // /source deliberately returns redacted text and the ORIGINAL file hash.
    // Never hash that text as original bytes or infer owner/job acceptance.
    return {
      path: source.path,
      sha256: source.sha256,
      bytes: source.bytes,
      content: source.content,
      source_observation:
        expectedHash === undefined
          ? "fresh-source-only"
          : "matched-indexed-pin",
      content_redacted: true,
    };
  },
};

export function text(value: unknown, fallback = "—"): string {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function rows(value: unknown): Data[] {
  if (Array.isArray(value))
    return value.map((item, index) =>
      typeof item === "object" && item !== null
        ? item
        : { id: index, value: item },
    );
  if (value && typeof value === "object")
    return Object.entries(value).map(([key, item]) =>
      typeof item === "object" && item !== null
        ? { id: key, name: key, ...item }
        : { id: key, name: key, value: item },
    );
  return [];
}

export function pretty(value: unknown): string {
  return typeof value === "string"
    ? value
    : JSON.stringify(value ?? {}, null, 2);
}

export function shortHash(value: unknown): string {
  const s = text(value);
  return s.length > 18 ? `${s.slice(0, 8)}…${s.slice(-6)}` : s;
}
