export type Data = Record<string, any>;

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    credentials: "same-origin",
    ...init,
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
    return await request(
      "/session",
      token
        ? {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ launch_token: token }),
          }
        : undefined,
    );
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      throw new ApiError(
        "Open this browser session with the Mac launcher.",
        "LAUNCH_REQUIRED",
        { cause: error.code },
        error.status,
      );
    }
    throw error;
  }
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
      return await request<Bootstrap>("/bootstrap");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        sessionReady = null;
        await prepareSession();
        return request<Bootstrap>("/bootstrap");
      }
      throw error;
    }
  },
  workspace: (id: string) =>
    request<Workspace>(`/projects/${encodeURIComponent(id)}/workspace`),
  doctor: () => request<Data>("/doctor"),
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
  threads: (projectId: string) =>
    request<Data>(`/projects/${encodeURIComponent(projectId)}/threads`),
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
