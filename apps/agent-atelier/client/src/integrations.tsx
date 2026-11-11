import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  AudioLines,
  Copy,
  ExternalLink,
  Image,
  Plug,
  RefreshCw,
  Search,
} from "lucide-react";
import { api, ApiError, rows, text, type Data } from "./api";
import type { MessageKey } from "./i18n";
import {
  Button,
  Empty,
  Field,
  Panel,
  Status,
  SurfaceNotice,
  type T,
} from "./ui";
import "./integrations.css";

const kindLabels: Record<string, MessageKey> = {
  plugin: "pluginKind",
  connector: "pluginConnector",
  mcp: "pluginConnector",
  media: "pluginMedia",
};

const statusLabels: Record<string, MessageKey> = {
  ready: "ready",
  native_only: "pluginNative",
  disabled: "pluginUnavailable",
  unverified: "unknown",
};

const mediaActions = new Map<string, MessageKey>([
  ["openverse.images.search", "pluginSearchImages"],
  ["openverse.audio.search", "pluginSearchAudio"],
]);
const repositoryAction = "github.repository.read";
const repositoryVisibility: Record<string, MessageKey> = {
  public: "pluginRepositoryPublic",
  private: "pluginRepositoryPrivate",
  internal: "pluginRepositoryInternal",
};

function integrationKey(entry: Data) {
  return `${entry.kind}:${entry.id}`;
}

export function PluginIntegrations({
  t,
  demo,
  csrf,
}: {
  t: T;
  demo: boolean;
  csrf?: string;
}) {
  const [catalog, setCatalog] = useState<Data | null>(null);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const requestPending = useRef(false);
  const filterInput = useRef<HTMLInputElement>(null);
  const initialPanel = useRef<HTMLDivElement>(null);
  const entries = rows(catalog?.entries).sort(
    (left, right) =>
      Number(right.status === "ready") - Number(left.status === "ready") ||
      text(left.name).localeCompare(text(right.name)),
  );
  const filtered = entries.filter((entry) =>
    `${entry.name} ${t(kindLabels[entry.kind] ?? "integration")}`
      .toLocaleLowerCase()
      .includes(filter.trim().toLocaleLowerCase()),
  );
  const selection = filtered.find(
    (entry) => integrationKey(entry) === selected,
  );
  const partial = rows(catalog?.sources).some(
    ({ status }) => status === "partial" || status === "unavailable",
  );
  useEffect(() => {
    if (document.activeElement !== document.body) return;
    if (catalog) filterInput.current?.focus();
    else if (error) initialPanel.current?.querySelector("button")?.focus();
  }, [catalog, error]);

  async function refresh() {
    if (demo || requestPending.current) return;
    requestPending.current = true;
    setLoading(true);
    setError("");
    setCatalog(null);
    try {
      const next = await api.integrations();
      setCatalog(next);
      setSelected((key) =>
        rows(next.entries).some((entry) => integrationKey(entry) === key)
          ? key
          : "",
      );
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      requestPending.current = false;
      setLoading(false);
    }
  }

  return (
    <Panel
      title={t("pluginMediaTitle")}
      icon={Plug}
      className="integrations-panel"
      tools={
        catalog && (
          <Button icon={RefreshCw} small onClick={() => void refresh()}>
            {t("refresh")}
          </Button>
        )
      }
    >
      {loading ? (
        <div className="panel-padding muted" role="status">
          {t("pluginChecking")}
        </div>
      ) : !catalog ? (
        <div className="panel-padding" ref={initialPanel}>
          {error ? (
            <div role="alert">
              <SurfaceNotice tone="error">{error}</SurfaceNotice>
            </div>
          ) : (
            <p className="muted">
              {t(demo ? "disabledInDemo" : "pluginCheckHelp")}
            </p>
          )}
          <Button icon={Search} disabled={demo} onClick={() => void refresh()}>
            {t(error ? "retry" : "pluginCheck")}
          </Button>
        </div>
      ) : (
        <>
          {partial && (
            <div className="integrations-panel__coverage" role="status">
              <SurfaceNotice tone="warning">
                {t("pluginDiscoveryPartial")}
              </SurfaceNotice>
            </div>
          )}
          {entries.length === 0 ? (
            <Empty icon={Plug} compact title={t("pluginNoConnections")} />
          ) : (
            <div className="integrations-panel__body">
              <div className="integrations-panel__catalog">
                <Field label={t("pluginSearch")}>
                  <input
                    ref={filterInput}
                    type="search"
                    value={filter}
                    onChange={(event) => setFilter(event.target.value)}
                  />
                </Field>
                <ul className="integrations-panel__entries">
                  {filtered.map((entry) => {
                    const key = integrationKey(entry);
                    const Icon = entry.kind === "media" ? Image : Plug;
                    return (
                      <li key={key}>
                        <button
                          type="button"
                          aria-pressed={key === selected}
                          onClick={() => setSelected(key)}
                        >
                          <Icon size={15} aria-hidden="true" />
                          <span>
                            <strong>{text(entry.name)}</strong>
                            <small>
                              {t(kindLabels[entry.kind] ?? "integration")}
                            </small>
                          </span>
                          <IntegrationStatus entry={entry} t={t} />
                        </button>
                      </li>
                    );
                  })}
                </ul>
                {filtered.length === 0 && (
                  <p className="muted" role="status">
                    {t("pluginNoMatches")}
                  </p>
                )}
              </div>
              {selection ? (
                <IntegrationDetail
                  key={integrationKey(selection)}
                  entry={selection}
                  t={t}
                  csrf={csrf}
                />
              ) : (
                <Empty icon={Plug} compact title={t("pluginSelect")} />
              )}
            </div>
          )}
        </>
      )}
    </Panel>
  );
}

function IntegrationStatus({ entry, t }: { entry: Data; t: T }) {
  return (
    <Status
      value={entry.status}
      label={t(statusLabels[entry.status] ?? "unknown")}
    />
  );
}

function IntegrationDetail({
  entry,
  t,
  csrf,
}: {
  entry: Data;
  t: T;
  csrf?: string;
}) {
  const [inspection, setInspection] = useState<Data | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toolFilter, setToolFilter] = useState("");
  const observed = inspection?.entry ?? entry;
  const tools = rows(inspection?.tools);
  const visibleTools = tools.filter((tool) =>
    `${tool.name} ${tool.title ?? ""}`
      .toLocaleLowerCase()
      .includes(toolFilter.trim().toLocaleLowerCase()),
  );
  const actions = rows(entry.actions);
  const readActions = actions.filter(({ id }) => mediaActions.has(id));
  const hasRepositoryLookup = actions.some(({ id }) => id === repositoryAction);

  async function inspect() {
    if (loading) return;
    setLoading(true);
    setError("");
    setInspection(null);
    try {
      setInspection(await api.integrationDetails(entry.kind, entry.id));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className="integrations-panel__detail"
      aria-label={text(observed.name)}
    >
      <div className="integrations-panel__heading">
        <h3>{text(observed.name)}</h3>
        <IntegrationStatus entry={observed} t={t} />
      </div>
      {observed.description && <p className="muted">{observed.description}</p>}
      {entry.kind !== "media" && !hasRepositoryLookup && (
        <>
          <Button
            icon={Plug}
            small
            onClick={() => void inspect()}
            disabled={loading}
          >
            {t(loading ? "pluginChecking" : "pluginInspect")}
          </Button>
          {error && (
            <div role="alert">
              <SurfaceNotice tone="error">{error}</SurfaceNotice>
            </div>
          )}
          {inspection && (
            <div className="integrations-panel__tools">
              {tools.length > 0 ? (
                <>
                  {tools.length > 8 && (
                    <Field label={t("pluginFilterTools")}>
                      <input
                        type="search"
                        value={toolFilter}
                        onChange={(event) => setToolFilter(event.target.value)}
                      />
                    </Field>
                  )}
                  <ul className="integrations-panel__tool-list">
                    {visibleTools.map((tool) => (
                      <li className="integrations-panel__tool" key={tool.name}>
                        <div>
                          <strong>{text(tool.title ?? tool.name)}</strong>
                          {tool.description && (
                            <p className="muted">{tool.description}</p>
                          )}
                        </div>
                        {tool.enabled === false ? (
                          <Status
                            value="unavailable"
                            label={t("pluginUnavailable")}
                          />
                        ) : tool.read_only === true ? (
                          <Status value="read_only" label={t("readOnly")} />
                        ) : null}
                      </li>
                    ))}
                  </ul>
                  {visibleTools.length === 0 && (
                    <p className="muted" role="status">
                      {t("nothingFound")}
                    </p>
                  )}
                </>
              ) : (
                <p className="muted" role="status">
                  {t("pluginNoToolMetadata")}
                </p>
              )}
            </div>
          )}
        </>
      )}
      {entry.status === "ready" && readActions.length > 0 && (
        <MediaSearch actions={readActions} t={t} csrf={csrf} />
      )}
      {entry.status === "ready" && hasRepositoryLookup && (
        <RepositoryLookup t={t} csrf={csrf} />
      )}
      {observed.handoff?.kind === "codex" && (
        <NativeHandoff
          value={
            typeof observed.handoff.target === "string"
              ? t("pluginHandoffPrompt").replace(
                  "{target}",
                  () => observed.handoff.target,
                )
              : text(observed.handoff.text)
          }
          t={t}
        />
      )}
    </section>
  );
}

function NativeHandoff({ value, t }: { value: string; t: T }) {
  const [status, setStatus] = useState<"" | "copied" | "failed">("");
  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setStatus("copied");
    } catch {
      setStatus("failed");
    }
  }
  return (
    <details className="integrations-panel__handoff">
      <summary>{t("pluginHandoff")}</summary>
      <p className="muted">{t("pluginHandoffHelp")}</p>
      <pre>{value}</pre>
      <Button icon={Copy} small onClick={() => void copy()}>
        {t(status === "copied" ? "copied" : "pluginCopyHandoff")}
      </Button>
      <span className="muted" role="status">
        {status === "failed"
          ? t("pluginCopyUnavailable")
          : status
            ? t("copied")
            : ""}
      </span>
    </details>
  );
}

function useIntegrationRead(csrf: string | undefined, t: T) {
  const [response, setResponse] = useState<Data | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const pending = useRef(false);

  function clear() {
    setResponse(null);
    setError("");
  }

  async function read(operation: string, args: Record<string, string>) {
    if (!csrf || pending.current) return;
    pending.current = true;
    setLoading(true);
    clear();
    try {
      const result = await api.readIntegration(operation, args, csrf);
      if (result.status !== "completed" || result.operation !== operation)
        throw new ApiError(t("pluginReadFailed"), "INVALID_RESPONSE");
      setResponse(result);
    } catch (cause) {
      setError(
        cause instanceof ApiError && cause.status === 429
          ? t("pluginReadRateLimited")
          : cause instanceof ApiError && cause.status === 403
            ? t("connectionNeeded")
            : t("pluginReadFailed"),
      );
    } finally {
      pending.current = false;
      setLoading(false);
    }
  }
  return { response, error, loading, clear, read };
}

function ReadFeedback({
  request,
  t,
}: {
  request: ReturnType<typeof useIntegrationRead>;
  t: T;
}) {
  return (
    <>
      <div role="status">
        {request.loading && <p className="muted">{t("running")}</p>}
        {request.response && (
          <p className="muted">
            {t("apiResponse")} · {text(request.response.provider)}
          </p>
        )}
      </div>
      {request.error && (
        <div role="alert">
          <SurfaceNotice tone="error">{request.error}</SurfaceNotice>
        </div>
      )}
    </>
  );
}

function MediaSearch({
  actions,
  csrf,
  t,
}: {
  actions: Data[];
  csrf?: string;
  t: T;
}) {
  const [operation, setOperation] = useState<string>(actions[0].id);
  const [query, setQuery] = useState("");
  const request = useIntegrationRead(csrf, t);
  const { response, loading } = request;
  const normalized = query.trim();
  const canRead =
    Boolean(csrf) && normalized.length >= 2 && normalized.length <= 120;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (canRead) void request.read(operation, { query: normalized });
  }

  return (
    <form className="integrations-panel__media" onSubmit={submit}>
      <div className="integrations-panel__query">
        <Field label={t("pluginMediaType")}>
          <select
            value={operation}
            disabled={loading}
            onChange={(event) => {
              setOperation(event.target.value);
              request.clear();
            }}
          >
            {actions.map(({ id }) => (
              <option key={id} value={id}>
                {t(mediaActions.get(id) ?? "pluginMedia")}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t("pluginQuery")}>
          <input
            type="search"
            value={query}
            maxLength={120}
            minLength={2}
            required
            disabled={loading}
            onChange={(event) => {
              setQuery(event.target.value);
              request.clear();
            }}
          />
        </Field>
        <Button type="submit" icon={Search} disabled={!canRead || loading}>
          {t(loading ? "running" : "searchShort")}
        </Button>
      </div>
      <p className="muted">{t("pluginOpenverseTerms")}</p>
      <ReadFeedback request={request} t={t} />
      {response && <MediaResults results={rows(response.content)} t={t} />}
    </form>
  );
}

function RepositoryLookup({ csrf, t }: { csrf?: string; t: T }) {
  const [name, setName] = useState("");
  const request = useIntegrationRead(csrf, t);
  const repository = request.response?.repository;
  const link = sourceLink(repository?.source_url);
  const visibility =
    repositoryVisibility[String(repository?.visibility).toLowerCase()];
  const normalized = name.trim();
  const canRead =
    Boolean(csrf) &&
    normalized.length <= 140 &&
    /^[a-z\d-]+\/[a-z\d._-]+$/i.test(normalized);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (canRead)
      void request.read(repositoryAction, { repository: normalized });
  }

  return (
    <form className="integrations-panel__media" onSubmit={submit}>
      <div className="integrations-panel__query integrations-panel__query--single">
        <Field label={t("pluginRepository")}>
          <input
            value={name}
            placeholder="owner/repository"
            maxLength={140}
            spellCheck={false}
            autoComplete="off"
            required
            disabled={request.loading}
            onChange={(event) => {
              setName(event.target.value);
              request.clear();
            }}
          />
        </Field>
        <Button
          type="submit"
          icon={Search}
          disabled={!canRead || request.loading}
        >
          {t(request.loading ? "running" : "pluginReadRepository")}
        </Button>
      </div>
      <p className="muted">{t("pluginGithubHelp")}</p>
      <ReadFeedback request={request} t={t} />
      {repository && (
        <div className="integrations-panel__repository">
          <div className="integrations-panel__heading">
            <strong>{text(repository.name)}</strong>
            {visibility && (
              <Status label={t(visibility)} value={repository.visibility} />
            )}
            {repository.archived === true && (
              <Status label={t("archivedCodexChats")} value="archived" />
            )}
          </div>
          <dl>
            <dt>{t("pluginDefaultBranch")}</dt>
            <dd>{text(repository.default_branch, t("unknown"))}</dd>
          </dl>
          {link && (
            <div className="integrations-panel__links">
              <a href={link} target="_blank" rel="noopener noreferrer">
                {t("source")} <ExternalLink size={12} aria-hidden="true" />
              </a>
            </div>
          )}
        </div>
      )}
    </form>
  );
}

function sourceLink(value: unknown) {
  if (typeof value !== "string") return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}

function MediaResults({ results, t }: { results: Data[]; t: T }) {
  if (results.length === 0) {
    return <p className="muted">{t("pluginMediaEmpty")}</p>;
  }
  return (
    <>
      <ul className="integrations-panel__results">
        {results.map((item) => {
          const source = sourceLink(item.source_url);
          const license = sourceLink(item.license_url);
          const Icon = item.medium === "audio" ? AudioLines : Image;
          return (
            <li key={item.id}>
              <Icon size={16} aria-hidden="true" />
              <div>
                <strong>{text(item.title, t("pluginUntitled"))}</strong>
                {item.creator && <p>{item.creator}</p>}
                <div className="integrations-panel__links">
                  {source && (
                    <a href={source} target="_blank" rel="noopener noreferrer">
                      {t("source")}{" "}
                      <ExternalLink size={12} aria-hidden="true" />
                    </a>
                  )}
                  {license ? (
                    <a href={license} target="_blank" rel="noopener noreferrer">
                      {text(item.license, t("pluginLicense"))}
                      <ExternalLink size={12} aria-hidden="true" />
                    </a>
                  ) : (
                    <span>{text(item.license, t("unknown"))}</span>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
      <p className="muted">{t("pluginLicenseHelp")}</p>
    </>
  );
}
