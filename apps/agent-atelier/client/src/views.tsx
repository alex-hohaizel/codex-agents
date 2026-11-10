import { useEffect, useLayoutEffect, useRef, useState } from "react";
import {
  Activity,
  Archive,
  ArrowDownToLine,
  ArrowRight,
  AudioLines,
  BookOpen,
  Boxes,
  Braces,
  Cable,
  Check,
  ChevronRight,
  Circle,
  Database,
  ExternalLink,
  FileCheck2,
  FileCode2,
  FileImage,
  FileStack,
  FileText,
  Fingerprint,
  FolderGit2,
  FolderOpen,
  GitCompareArrows,
  GitPullRequest,
  Globe2,
  Image,
  Layers3,
  ListChecks,
  LockKeyhole,
  Network,
  Pause,
  Plus,
  Radio,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Terminal,
  TerminalSquare,
  TriangleAlert,
  Workflow,
} from "lucide-react";
import {
  api,
  mergePortfolioPage,
  pretty,
  rows,
  shortHash,
  text,
  type Bootstrap,
  type Data,
  type Project,
  type Workspace,
} from "./api";
import type { CommandFn, Inspection, View } from "./App";
import { PrivacySettings } from "./privacy";
import {
  profileDefinitions,
  profileLabel,
  projectProfile,
  type Profile,
} from "./profiles";
import { localeNames, catalogs, type Locale, type MessageKey } from "./i18n";
import {
  ContextCoveragePanel,
  ContextSignal,
  ContextTrailPanels,
} from "./context-workbench";
import {
  contextTrail,
  observedJobCounts,
  activeJobStatuses,
  requirementPresentation,
  workspaceDirection,
  operatorWorkspace,
  operatorSummary,
  workResultSources,
} from "./workbench";
import {
  Button,
  CodeViewer,
  Disclosure,
  Empty,
  Field,
  IconButton,
  Modal,
  Panel,
  RecordDetails,
  Status,
  SurfaceNotice,
  type T,
} from "./ui";

export interface ViewProps {
  t: T;
  locale: Locale;
  demo: boolean;
  selected: Project | null;
  workspace: Workspace | null;
  boot: Bootstrap | null;
  portfolio?: Data | null;
  nativeDetail?: Data | null;
  nativeHistoryLoading?: boolean;
  nativeHistoryError?: string;
  loadMoreNativeHistory?: (itemCursor?: Data) => void;
  observePortfolio?: () => Promise<void>;
  busy: string;
  command: CommandFn;
  inspect: (value: Inspection) => void;
  expand: (title: string, value: unknown) => void;
  selectProject: (id: string) => void;
  connectProject: () => void;
  connectDiscovered: (root: string) => void;
  newTask: (preset?: Data) => void;
  navigate: (view: View) => void;
}

export function Portfolio(p: ViewProps) {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [focus, setFocus] = useState<Data | null>(null);
  const [detail, setDetail] = useState<Data | null>(null);
  const [detailError, setDetailError] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const detailIdentityRef = useRef("");
  const detailMoreRef = useRef(false);
  const catalog = p.demo ? null : p.portfolio;
  const detailIdentity = `${p.demo}:${focus?.id ?? ""}:${catalog?.checked_at ?? ""}`;
  detailIdentityRef.current = detailIdentity;
  const activeDetail =
    detail?.project?.id === focus?.id &&
    detail?.coverage?.snapshot_checked_at === catalog?.checked_at
      ? detail
      : null;
  const discovered = rows(catalog?.projects);
  const roots = new Set(discovered.map((item) => item.root));
  const projects: Data[] = [
    ...discovered,
    ...(p.boot?.projects ?? [])
      .filter((item) => !roots.has(item.root))
      .map((item) => ({
        ...item,
        binding_id: item.id,
        goal: { status: "unknown", text: "" },
        next_actions: [],
        agents: [],
        work_groups: [],
        thread_count: 0,
      })),
  ];
  const filtered = projects.filter((project) => {
    const kind =
      project.kind === "application"
        ? "app"
        : project.kind === "chatbot"
          ? "bot"
          : (project.kind ?? "generic");
    return (
      (filter === "all" || kind === filter) &&
      `${project.name} ${project.goal?.text ?? ""} ${project.root}`
        .toLowerCase()
        .includes(query.toLowerCase())
    );
  });
  useEffect(() => {
    const identity = detailIdentity;
    detailMoreRef.current = false;
    if (!focus || p.demo || !discovered.some((item) => item.id === focus.id)) {
      setDetail(null);
      setDetailLoading(false);
      setDetailError("");
      return;
    }
    let cancelled = false;
    setDetailLoading(true);
    setDetailError("");
    setDetail(null);
    api
      .portfolioProject(focus.id, { snapshot_checked_at: catalog?.checked_at })
      .then((value) => {
        if (!cancelled && detailIdentityRef.current === identity) {
          setDetail(mergePortfolioPage(null, value));
          void p.observePortfolio?.();
        }
      })
      .catch((error) => {
        if (!cancelled && detailIdentityRef.current === identity)
          setDetailError(error.message);
      })
      .finally(() => {
        if (!cancelled && detailIdentityRef.current === identity)
          setDetailLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [detailIdentity]);
  async function loadMoreDetail(itemCursor?: Data) {
    const offset = detail?.coverage?.next_thread_offset;
    if (
      !focus ||
      !detail ||
      detail.project?.id !== focus.id ||
      detail.coverage?.snapshot_checked_at !== catalog?.checked_at ||
      (!itemCursor && !Number.isInteger(offset)) ||
      (itemCursor &&
        !detail.coverage?.item_cursors?.some(
          (item: Data) =>
            item.thread_id === itemCursor.thread_id &&
            typeof item.next_cursor === "string" &&
            item.next_cursor === itemCursor.next_cursor,
        )) ||
      detailMoreRef.current
    )
      return;
    const identity = detailIdentity;
    detailMoreRef.current = true;
    setDetailLoading(true);
    setDetailError("");
    try {
      const page = await api.portfolioProject(focus.id, {
        ...(itemCursor
          ? {
              item_thread_id: itemCursor.thread_id,
              item_cursor: itemCursor.next_cursor,
            }
          : { thread_offset: offset }),
        snapshot_checked_at: detail.coverage.snapshot_checked_at,
      });
      if (detailIdentityRef.current === identity) {
        setDetail(mergePortfolioPage(detail, page));
        void p.observePortfolio?.();
      }
    } catch (error) {
      if (detailIdentityRef.current === identity)
        setDetailError(error instanceof Error ? error.message : String(error));
    } finally {
      if (detailIdentityRef.current === identity) {
        detailMoreRef.current = false;
        setDetailLoading(false);
      }
    }
  }
  const attention = projects.filter(
    (project) =>
      project.warnings?.length ||
      ["blocked", "attention", "outcome_unknown"].includes(project.status) ||
      project.goal?.status === "unknown",
  );
  function open(item: Data) {
    setFocus(item);
    p.inspect({ title: item.name, kind: "project", data: item });
  }
  if (focus)
    return (
      <div className="page-content portfolio-view">
        <button className="back-to-portfolio" onClick={() => setFocus(null)}>
          <ArrowRight size={14} />
          {p.t("backToPortfolio")}
        </button>
        <NativeProjectDetail
          {...p}
          project={activeDetail?.project ?? focus}
          detail={activeDetail}
          loading={detailLoading}
          error={detailError}
          loadMore={loadMoreDetail}
        />
      </div>
    );
  return (
    <div className="page-content portfolio-view">
      <PageHeading
        eyebrow={p.t("personal")}
        title={p.t("portfolioTitle")}
        description={p.t("portfolioDescription")}
        action={
          <div className="heading-actions">
            <Button
              icon={FolderGit2}
              onClick={p.connectProject}
              disabled={p.demo}
            >
              {p.t("connectProject")}
            </Button>
            <Button
              tone="primary"
              icon={RefreshCw}
              disabled={p.demo || Boolean(p.busy)}
              onClick={() =>
                void p
                  .command("portfolio.refresh", { max_pages: 20 })
                  .catch(() => {})
              }
            >
              {p.busy === "portfolio.refresh"
                ? p.t("processing")
                : p.t("discoverCodex")}
            </Button>
          </div>
        }
      />
      <div className="portfolio-entry">
        <span className="portfolio-entry__symbol">
          <Workflow size={25} strokeWidth={1.3} />
        </span>
        <div>
          <span className="eyebrow">{p.t("universalEntry")}</span>
          <h2>{p.t("entryQuestion")}</h2>
          <p>{p.t("entryDescription")}</p>
        </div>
        <Button
          icon={ArrowRight}
          tone="primary"
          disabled={p.demo}
          onClick={() =>
            p.selected
              ? p.newTask({ universal_entry: true })
              : p.connectProject()
          }
        >
          {p.selected ? p.t("describeOutcome") : p.t("connectFirstProject")}
        </Button>
      </div>
      <div className="metric-strip portfolio-metrics">
        <Metric icon={Boxes} value={projects.length} label={p.t("products")} />
        <Metric
          icon={FileStack}
          value={catalog?.summary?.work_items ?? "—"}
          label={p.t("documentedWork")}
        />
        <Metric
          icon={Activity}
          value={
            catalog?.summary?.active ??
            p.boot?.jobs.filter((item) =>
              ["running", "queued", "dispatching"].includes(item.status),
            ).length ??
            0
          }
          label={p.t("activeJobs")}
        />
        <Metric
          icon={ShieldCheck}
          value={attention.length}
          label={p.t("needsAttention")}
        />
      </div>
      {!catalog?.checked_at && !p.demo && (
        <div className="catalog-onboarding">
          <Network size={24} />
          <div>
            <strong>{p.t("discoverFirst")}</strong>
            <p>{p.t("discoverFirstHelp")}</p>
          </div>
          <span className="step-number">01 → 02 → 03</span>
        </div>
      )}
      {catalog?.checked_at && (
        <div className="coverage-line">
          <span
            className={`status__dot ${catalog.coverage?.truncated ? "coverage-warning" : ""}`}
          />
          <span>
            {p.t("historyCoverage")} · {catalog.coverage?.native_threads ?? 0}{" "}
            {p.t("threads")}
          </span>
          <span>
            {catalog.coverage?.complete
              ? p.t("coverageComplete")
              : p.t("coveragePartial")}
          </span>
          <button
            onClick={() =>
              p.expand(p.t("coverageDetails"), {
                checked_at: catalog.checked_at,
                coverage: catalog.coverage,
                warnings: catalog.warnings,
              })
            }
          >
            {p.t("coverageDetails")}
            <ChevronRight size={12} />
          </button>
        </div>
      )}
      <div className="portfolio-layout">
        <Panel
          title={p.t("workLedger")}
          icon={Boxes}
          className="portfolio-products"
          tools={
            <div className="inline-search">
              <Search size={14} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={p.t("searchShort")}
                aria-label={p.t("searchShort")}
              />
            </div>
          }
        >
          <div className="filter-tabs">
            {[
              "all",
              "app",
              "bot",
              "game",
              "research",
              "document",
              "agent",
              "generic",
            ].map((kind) => (
              <button
                key={kind}
                onClick={() => setFilter(kind)}
                className={filter === kind ? "is-active" : ""}
              >
                {kind === "app"
                  ? p.t("application")
                  : kind === "bot"
                    ? p.t("chatbot")
                    : kind === "agent"
                      ? p.t("agents")
                      : p.t(kind as MessageKey)}
                {kind === "all" && <span>{projects.length}</span>}
              </button>
            ))}
          </div>
          <div className="portfolio-ledger-intro">{p.t("workLedgerHelp")}</div>
          <div className="portfolio-ledger-head" aria-hidden="true">
            <span>{p.t("product")}</span>
            <span>{p.t("outcome")}</span>
            <span>{p.t("nextStep")}</span>
          </div>
          <div className="portfolio-card-grid portfolio-work-ledger">
            {filtered.map((project) => (
              <button
                className={`portfolio-project-card ${project.goal?.status === "accepted" ? "has-accepted-goal" : ""}`}
                key={project.id}
                onClick={() => open(project)}
              >
                <div className="portfolio-card-heading">
                  <span
                    className={`project-icon project-icon--${project.kind ?? "generic"}`}
                  >
                    <ProductSymbol kind={project.kind ?? "generic"} />
                  </span>
                  <span>
                    <strong>{project.name}</strong>
                    <small>
                      {project.phase && project.phase !== "not_recorded"
                        ? project.phase
                        : p.t("sourceReview")}
                    </small>
                  </span>
                  <ChevronRight size={15} />
                </div>
                <div className="portfolio-card-goal">
                  <small>
                    <ShieldCheck size={11} />
                    {goalLabel(project.goal, p.t)}
                  </small>
                  <p>{project.goal?.text || p.t("goalUnknownHelp")}</p>
                </div>
                <div className="portfolio-card-stats">
                  <span>
                    <FileStack size={12} />
                    {project.thread_count ?? 0} {p.t("threads")}
                  </span>
                  <span>
                    <Braces size={12} />
                    {project.agents?.length ?? 0} {p.t("agents")}
                  </span>
                  <span className={project.binding_id ? "binding-ready" : ""}>
                    {project.binding_id
                      ? p.t("connected")
                      : p.t("discoveredOnly")}
                  </span>
                </div>
                <div className="portfolio-card-next">
                  <ArrowRight size={12} />
                  <span>{nextActionText(project.next_actions?.[0], p.t)}</span>
                </div>
              </button>
            ))}
          </div>
          {!filtered.length && (
            <Empty icon={FolderGit2} title={p.t("noPortfolioMatches")}>
              <p>
                {projects.length
                  ? p.t("changePortfolioFilter")
                  : p.t("discoverFirstHelp")}
              </p>
            </Empty>
          )}
        </Panel>
        <div className="portfolio-side">
          <Panel
            title={p.t("needsAttention")}
            icon={ShieldCheck}
            tools={<span className="tag">{attention.length}</span>}
          >
            <div className="attention-list">
              {attention.slice(0, 8).map((item) => (
                <button key={item.id} onClick={() => open(item)}>
                  <span className="attention-marker" />
                  <span>
                    <strong>{item.name}</strong>
                    <small>
                      {text(
                        item.warnings?.[0]?.message ?? item.warnings?.[0],
                        p.t("goalUnknownHelp"),
                      )}
                    </small>
                  </span>
                  <ChevronRight size={13} />
                </button>
              ))}
              {!attention.length && (
                <p className="panel-padding muted">
                  {p.t("noObservedAttention")}
                </p>
              )}
            </div>
          </Panel>
          <Panel title={p.t("activity")} icon={Activity}>
            <ActivityList items={p.boot?.activity ?? []} {...p} />
          </Panel>
        </div>
      </div>
      <Panel
        title={p.t("portfolioMap")}
        icon={Network}
        tools={<span className="tag tag--subtle">{p.t("actualRecords")}</span>}
      >
        <div className="portfolio-map" aria-label={p.t("portfolioMap")}>
          <div className="portfolio-map-root">
            <Boxes size={25} />
            <strong>{p.t("personal")}</strong>
            <span>
              {projects.length} {p.t("products")}
            </span>
          </div>
          <div className="portfolio-map-projects">
            {projects.map((item) => (
              <button key={item.id} onClick={() => open(item)}>
                <ProductSymbol kind={item.kind ?? "generic"} />
                <span>
                  <strong>{item.name}</strong>
                  <small>
                    {item.thread_count ?? 0} {p.t("threads")} ·{" "}
                    {goalLabel(item.goal, p.t)}
                  </small>
                </span>
                <ChevronRight size={13} />
              </button>
            ))}
            {!projects.length && (
              <p className="muted">{p.t("discoverFirstHelp")}</p>
            )}
          </div>
        </div>
      </Panel>
    </div>
  );
}

export function nextActionText(action: Data | undefined, t: T) {
  if (!action?.text) return t("reviewProjectSources");
  if (action.status === "proposed" && !action.source_ref) {
    if (action.text.startsWith("Establish the current project goal"))
      return t("reviewProjectSources");
    if (action.text.startsWith("Review and bind this discovered project"))
      return t("connectThis");
    if (action.text.startsWith("Reconcile the unknown native job"))
      return t("restoreUnknown");
  }
  return text(action.text);
}
function goalLabel(goal: Data | undefined, t: T) {
  return t(
    goal?.status === "accepted"
      ? "acceptedTarget"
      : goal?.status === "declared"
        ? "declaredTarget"
        : "goalNotConfirmed",
  );
}

function NativeProjectDetail(
  p: ViewProps & {
    project: Data;
    detail: Data | null;
    loading?: boolean;
    error?: string;
    loadMore?: (itemCursor?: Data) => void;
  },
) {
  const project = p.project;
  const bound = (p.boot?.projects ?? []).find(
    (item) => item.id === project.binding_id || item.root === project.root,
  );
  const goal = p.detail?.goal ?? project.goal;
  const next = p.detail?.next_actions ?? project.next_actions ?? [];
  const agents = p.detail?.project?.agents ?? project.agents ?? [];
  return (
    <>
      <PageHeading
        eyebrow={p.t("nativeCodexProject")}
        title={project.name}
        description={project.root}
        action={
          <div className="heading-actions">
            {bound ? (
              <>
                <Button
                  icon={FolderOpen}
                  onClick={() => p.selectProject(bound.id)}
                >
                  {p.t("openProject")}
                </Button>
                <Button
                  tone="primary"
                  icon={Workflow}
                  onClick={() => {
                    p.selectProject(bound.id);
                    p.newTask({
                      universal_entry: true,
                      objective: next[0] ? nextActionText(next[0], p.t) : "",
                    });
                  }}
                >
                  {p.t("continueWithOrchestrator")}
                </Button>
              </>
            ) : (
              <Button
                tone="primary"
                icon={FolderGit2}
                onClick={() => p.connectDiscovered(project.root)}
              >
                {p.t("connectThis")}
              </Button>
            )}
          </div>
        }
      />
      {!bound && <SurfaceNotice>{p.t("discoveryReadOnly")}</SurfaceNotice>}
      {p.error && <SurfaceNotice tone="warning">{p.error}</SurfaceNotice>}
      <div className="project-direction-grid">
        <section
          className={`project-target ${goal?.status === "accepted" ? "project-target--accepted" : ""}`}
        >
          <div className="target-label">
            <ShieldCheck size={16} />
            <span>{goalLabel(goal, p.t)}</span>
            <span className="tag">{goal?.status ?? "unknown"}</span>
          </div>
          <h2>{goal?.text || p.t("goalUnknownHelp")}</h2>
          {goal?.source_ref && (
            <button
              className="source-ref-button"
              onClick={() =>
                p.inspect({
                  title: p.t("targetSource"),
                  kind: "goal",
                  data: goal,
                  sourcePath: goal.source_ref,
                })
              }
            >
              <FileText size={12} />
              <span>{goal.source_ref}</span>
              <code>{shortHash(goal.source_sha256)}</code>
              <ChevronRight size={12} />
            </button>
          )}
          <p>{p.t("targetProvenanceHelp")}</p>
        </section>
        <Panel title={p.t("nextActions")} icon={ArrowRight}>
          <div className="next-action-list">
            {next.length ? (
              next.map((action: Data, index: number) => (
                <button
                  key={index}
                  onClick={() => {
                    if (bound) {
                      p.selectProject(bound.id);
                      p.newTask({
                        universal_entry: true,
                        objective: nextActionText(action, p.t),
                      });
                    } else p.connectDiscovered(project.root);
                  }}
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <strong>{nextActionText(action, p.t)}</strong>
                    <small>
                      {action.status === "declared"
                        ? p.t("fromProjectSource")
                        : p.t("proposedNextAction")}
                    </small>
                  </div>
                  <ChevronRight size={14} />
                </button>
              ))
            ) : (
              <p className="panel-padding muted">
                {p.t("reviewProjectSources")}
              </p>
            )}
          </div>
        </Panel>
      </div>
      <div className="project-team-strip">
        <Braces size={16} />
        <strong>{p.t("projectAgents")}</strong>
        {agents.length ? (
          agents.map((agent: Data) => (
            <button
              key={agent.name}
              onClick={() =>
                p.inspect({
                  title: agent.name,
                  kind: "agent",
                  data: agent,
                  sourcePath: agent.source_ref,
                })
              }
            >
              <span>{agent.name}</span>
              <small>
                {agent.availability === "installed"
                  ? p.t("installed")
                  : agent.availability === "planned"
                    ? p.t("plannedAgent")
                    : p.t("notTested")}
              </small>
            </button>
          ))
        ) : (
          <span className="muted">{p.t("noProjectAgentRecorded")}</span>
        )}
      </div>
      <Panel
        title={p.t("projectWorkMap")}
        icon={Network}
        tools={
          <span className="tag">
            {p.loading ? p.t("loading") : p.t("actualRecords")}
          </span>
        }
      >
        <WorkMap
          groups={p.detail?.work_groups ?? []}
          goal={goal}
          projectName={project.name}
          {...p}
          bound={bound}
        />
        <HistoryPagination
          {...p}
          detail={p.detail}
          loading={p.loading}
          loadMore={p.loadMore}
        />
      </Panel>
      <div className="native-history-boundary">
        <FileCheck2 size={14} />
        <p>{p.t("nativeWorkBoundary")}</p>
        <button
          onClick={() =>
            p.expand(
              p.t("coverageDetails"),
              p.detail
                ? { coverage: p.detail.coverage, warnings: p.detail.warnings }
                : project,
            )
          }
        >
          {p.t("coverageDetails")}
          <ChevronRight size={12} />
        </button>
      </div>
    </>
  );
}

function HistoryPagination(
  p: ViewProps & {
    detail?: Data | null;
    loading?: boolean;
    error?: string;
    loadMore?: (itemCursor?: Data) => void;
  },
) {
  if (!p.detail && !p.loading && !p.error) return null;
  const coverage = p.detail?.coverage;
  return (
    <div className="panel-padding">
      {p.error && <SurfaceNotice tone="warning">{p.error}</SurfaceNotice>}
      {coverage && (
        <div className="coverage-line">
          <span
            className={`status__dot ${coverage.complete ? "" : "coverage-warning"}`}
          />
          <span>
            {p.t("historyCoverage")} · {coverage.threads_read ?? 0}/
            {coverage.threads_total ?? 0}
          </span>
          <span>
            {coverage.complete
              ? p.t("coverageComplete")
              : p.t("coveragePartial")}
          </span>
          <button
            onClick={() =>
              p.expand(p.t("coverageDetails"), {
                coverage,
                warnings: p.detail?.warnings ?? [],
              })
            }
          >
            {p.t("coverageDetails")}
            {p.detail?.warnings?.length ? ` · ${p.detail.warnings.length}` : ""}
            <ChevronRight size={12} />
          </button>
        </div>
      )}
      {Number.isInteger(coverage?.next_thread_offset) && (
        <Button
          disabled={p.loading}
          onClick={() => p.loadMore?.()}
          icon={ArrowDownToLine}
        >
          {p.loading ? p.t("loading") : p.t("loadMoreThreads")}
        </Button>
      )}
      {rows(coverage?.item_cursors).filter(
        (item) =>
          typeof item.next_cursor === "string" && item.next_cursor.length > 0,
      ).length > 0 && (
        <div className="history-item-continuations">
          <p>{p.t("historyItemsRemaining")}</p>
          {rows(coverage?.item_cursors)
            .filter(
              (item) =>
                typeof item.next_cursor === "string" &&
                item.next_cursor.length > 0,
            )
            .map((item) => (
              <Button
                key={item.thread_id}
                disabled={p.loading}
                icon={ArrowDownToLine}
                onClick={() => p.loadMore?.(item)}
              >
                <span>
                  {p.loading ? p.t("loading") : p.t("loadMoreHistoryItems")}
                  <small>
                    {text(
                      p.detail?.threads?.find(
                        (thread: Data) => thread.id === item.thread_id,
                      )?.title,
                      shortHash(item.thread_id),
                    )}
                  </small>
                </span>
              </Button>
            ))}
        </div>
      )}
      {!coverage && p.loading && (
        <span className="muted">{p.t("loading")}</span>
      )}
    </div>
  );
}

function WorkMap(
  p: ViewProps & {
    groups: Data[];
    goal?: Data;
    bound?: Project;
    projectName?: string;
  },
) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  if (!p.groups.length)
    return (
      <Empty compact icon={Network} title={p.t("noWorkReadYet")}>
        <p>{p.t("noWorkReadHelp")}</p>
      </Empty>
    );
  return (
    <div className="work-map">
      <div className="work-map-origin">
        <span>
          <Fingerprint size={17} />
        </span>
        <strong>
          {p.goal?.text || p.projectName || p.selected?.name || p.t("product")}
        </strong>
        <small>{goalLabel(p.goal, p.t)}</small>
      </div>
      <div className="work-map-lanes">
        {p.groups.map((group) => {
          const items = rows(group.items);
          const systemChecks = group.id === "system_checks";
          const visible = expanded[group.id]
            ? items
            : systemChecks
              ? []
              : items.slice(0, 4);
          return (
            <section className="work-map-lane" key={group.id}>
              <header>
                <span className="work-lane-node" />
                <strong>{workGroupTitle(group, p.t)}</strong>
                <span>{items.length}</span>
              </header>
              <div className="work-map-items">
                {visible.map((item) => (
                  <article className="work-map-item" key={item.id}>
                    <button
                      className="work-item-main"
                      onClick={() =>
                        p.inspect({
                          title: item.objective || item.id,
                          kind: "work",
                          data: item,
                        })
                      }
                    >
                      <div>
                        <Status
                          value={item.status}
                          label={workStatus(item.status, p.t, item.work_type)}
                        />
                        <small>
                          {item.source === "native-history"
                            ? p.t("nativeHistory")
                            : item.source === "service"
                              ? p.t("serviceStore")
                              : p.t("nativeFiles")}
                        </small>
                      </div>
                      <strong>{item.objective || p.t("noDescription")}</strong>
                      {item.outcome && <p>{text(item.outcome)}</p>}
                    </button>
                    {item.skills?.length > 0 && (
                      <div className="work-item-skills">
                        {item.skills.map((skill: Data) => (
                          <span key={skill.name}>
                            <Braces size={10} />
                            {skill.name}
                            <small>
                              {skill.status === "selected"
                                ? p.t("skillSelected")
                                : p.t("skillMentioned")}
                            </small>
                          </span>
                        ))}
                      </div>
                    )}
                    <footer>
                      <button
                        onClick={() =>
                          p.expand(p.t("evidence"), {
                            source: item.source,
                            evidence_refs: item.evidence_refs,
                            thread_id: item.thread_id,
                            turn_id: item.turn_id,
                            status: item.status,
                          })
                        }
                      >
                        <FileCheck2 size={11} />
                        {p.t("provenance")}
                      </button>
                      {p.bound && (
                        <button
                          onClick={() => {
                            p.selectProject(p.bound!.id);
                            p.newTask({
                              universal_entry: true,
                              objective: item.objective || "",
                              ...(item.thread_id
                                ? { thread_id: item.thread_id }
                                : {}),
                            });
                          }}
                        >
                          {p.t("continue")}
                          <ArrowRight size={12} />
                        </button>
                      )}
                    </footer>
                  </article>
                ))}
                {!items.length && (
                  <span className="muted">{p.t("noRecords")}</span>
                )}
                {(items.length > 4 || (systemChecks && items.length > 0)) && (
                  <button
                    className="work-map-more"
                    onClick={() =>
                      setExpanded((value) => ({
                        ...value,
                        [group.id]: !value[group.id],
                      }))
                    }
                  >
                    {expanded[group.id]
                      ? p.t("collapse")
                      : `${p.t("showAllWork")} · ${items.length}`}
                  </button>
                )}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
function workStatus(value: string, t: T, workType?: string) {
  if (workType === "permission_review") return t("systemChecks");
  const keys: Record<string, MessageKey> = {
    answer_received: "answerReceived",
    in_progress: "running",
    gating: "checking",
    dispatching: "running",
    running: "running",
    failed: "failed",
    interrupted: "interruptedWork",
    recorded: "recordedWork",
  };
  return t(keys[value] ?? "unknown");
}
function workGroupTitle(group: Data, t: T) {
  const keys: Record<string, MessageKey> = {
    completed: "completedWork",
    answers: "completedWork",
    active: "activeWork",
    running: "activeWork",
    results: "completedWork",
    prepared: "preparedTask",
    other: "documentedWork",
    attention: "needsAttention",
    recorded: "recordedWork",
    native: "nativeHistory",
    service: "serviceStore",
    system_checks: "systemChecks",
  };
  return keys[group.id]
    ? t(keys[group.id])
    : text(group.title, t("documentedWork"));
}

export function WorkspaceView(p: ViewProps) {
  const [mode, setMode] = useState<"work" | "sources">("work");
  useEffect(() => setMode("work"), [p.selected?.id]);
  if (!p.selected) return <Welcome {...p} />;
  if (p.demo) return <TechnicalWorkspaceView {...p} />;
  return (
    <div className="operator-workspace">
      <nav className="operator-view-switch" aria-label={p.t("workspace")}>
        <button
          data-operator-mode="work"
          className={mode === "work" ? "is-active" : ""}
          onClick={() => setMode("work")}
          aria-pressed={mode === "work"}
        >
          <Workflow size={15} />
          {p.t("operatorOverview")}
        </button>
        <button
          data-operator-mode="sources"
          className={mode === "sources" ? "is-active" : ""}
          onClick={() => setMode("sources")}
          aria-pressed={mode === "sources"}
        >
          <FileCode2 size={15} />
          {p.t("operatorSources")}
        </button>
        <button
          className="operator-context-link"
          onClick={() => p.navigate("context")}
        >
          <Fingerprint size={14} />
          {p.t("context")}
          <ChevronRight size={12} />
        </button>
      </nav>
      {mode === "work" ? (
        <OperatorCanvas {...p} openSources={() => setMode("sources")} />
      ) : (
        <TechnicalWorkspaceView {...p} />
      )}
    </div>
  );
}

function OperatorCanvas(p: ViewProps & { openSources: () => void }) {
  const model = operatorWorkspace(p.workspace, p.selected?.id, p.nativeDetail);
  const [stageId, setStageId] = useState("");
  const [requirementsExpanded, setRequirementsExpanded] = useState(false);
  const [workId, setWorkId] = useState("");
  const [expandedLanes, setExpandedLanes] = useState<Record<string, boolean>>(
    {},
  );
  const [showHistory, setShowHistory] = useState(false);
  const [historyDiscovering, setHistoryDiscovering] = useState(false);
  const [historyDiscoveryError, setHistoryDiscoveryError] = useState("");
  const historyRegion = useRef<HTMLElement | null>(null);
  const historyRequest = useRef(0);
  const [report, setReport] = useState<Data | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const reportRead = useRef(0);
  useEffect(() => {
    setStageId("");
    setRequirementsExpanded(false);
    setWorkId("");
    setExpandedLanes({});
    setShowHistory(false);
    historyRequest.current++;
    setHistoryDiscovering(false);
    setHistoryDiscoveryError("");
    reportRead.current++;
    setReport(null);
    setReportLoading(false);
  }, [p.selected?.id]);
  const focusedWork =
    model.work.find((item) => item.id === workId) ?? model.current;
  const mapWork = model.work.some((item) => item.source === "native-record")
    ? model.work.filter((item) => item.source === "native-record")
    : model.work;
  const selectedStage = model.stages.find((stage) => stage.id === stageId);
  const visibleRequirements =
    stageId === "__unassigned"
      ? model.unstagedRequirements
      : (selectedStage?.requirements ?? model.requirements);
  const trail = contextTrail(p.workspace);
  const action = model.next[0];
  const decision = trail.decisions[0];
  const artifacts = p.workspace?.artifacts ?? [];
  const sourceResults = model.results.filter(
    (item) => item.source === "native-record",
  );
  const result = [
    ...(sourceResults.length ? sourceResults : model.results),
  ].sort((a, b) =>
    String(b.record.completed_at ?? b.record.updated_at ?? "").localeCompare(
      String(a.record.completed_at ?? a.record.updated_at ?? ""),
    ),
  )[0];
  const inspectGoal = () =>
    p.inspect({
      title: p.t("targetSource"),
      kind: "goal",
      data: model.goal ?? {},
      sourcePath: model.goal?.source_ref,
    });
  const sourceTitle = (item: Data) =>
    text(item.name ?? item.path ?? item.id)
      .split(/[\\/]/)
      .pop();
  const inspectWork = (item: (typeof model.work)[number]) =>
    p.inspect({ title: item.title, kind: "work", data: item.record });

  const resultPaths = workResultSources(focusedWork?.record);
  function openHistory() {
    setShowHistory(true);
    requestAnimationFrame(() => {
      const reduced = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
      historyRegion.current?.scrollIntoView({
        block: "start",
        behavior: reduced ? "auto" : "smooth",
      });
      historyRegion.current?.focus({ preventScroll: true });
    });
  }
  async function discoverHistory() {
    const generation = ++historyRequest.current;
    setHistoryDiscovering(true);
    setHistoryDiscoveryError("");
    try {
      await p.command("portfolio.refresh", { max_pages: 20 });
    } catch (error) {
      if (generation === historyRequest.current)
        setHistoryDiscoveryError(
          error instanceof Error ? error.message : String(error),
        );
    } finally {
      if (generation === historyRequest.current) setHistoryDiscovering(false);
    }
  }
  async function readReport(path: string) {
    if (!p.selected) return;
    const generation = ++reportRead.current;
    setReport({ path });
    setReportLoading(true);
    try {
      const source = await api.source(p.selected.id, path);
      if (generation === reportRead.current) setReport({ ...source, path });
    } catch (error) {
      if (generation === reportRead.current)
        setReport({
          path,
          error: error instanceof Error ? error.message : String(error),
        });
    } finally {
      if (generation === reportRead.current) setReportLoading(false);
    }
  }

  return (
    <div className="operator-canvas">
      <section className="operator-mission" aria-labelledby="operator-goal">
        <span className="operator-mission-mark">
          <Layers3 size={26} strokeWidth={1.4} />
        </span>
        <div>
          <div className="operator-section-label">
            <ShieldCheck size={13} />
            {goalLabel(model.goal, p.t)}
          </div>
          <h2 id="operator-goal">
            {model.goal?.text || p.t("goalUnknownHelp")}
          </h2>
          <button className="operator-source-link" onClick={inspectGoal}>
            <FileText size={12} />
            {p.t("targetSource")}
            <ChevronRight size={12} />
          </button>
        </div>
        <div className="operator-mission-context">
          <ContextSignal
            workspace={p.workspace}
            t={p.t}
            onOpen={() => p.navigate("context")}
          />
          <span>
            {p.workspace?.sources?.length ?? 0} {p.t("sourcesCount")}
            <i />
            {model.requirements.length} {p.t("mustCount")}
          </span>
        </div>
      </section>

      <div className="operator-main-grid">
        <section
          className="operator-process"
          aria-labelledby="operator-map-title"
        >
          <header className="operator-panel-heading">
            <div>
              <Network size={18} />
              <h2 id="operator-map-title">{p.t("operatorMap")}</h2>
            </div>
            <button data-open-native-history onClick={openHistory}>
              {p.t("nativeHistory")}
              <ArrowRight size={13} />
            </button>
          </header>
          {mapWork.length > 0 && (
            <div
              className="operator-work-map"
              data-source-work-count={
                mapWork.filter((item) => item.source === "native-record").length
              }
            >
              <div className="operator-work-anchor">
                <span>
                  <Layers3 size={23} />
                </span>
                <div>
                  <small>{p.t("operatorSourceState")}</small>
                  <strong>
                    {model.checkpoint?.phase || p.t("fromProjectSource")}
                  </strong>
                </div>
                <button
                  onClick={inspectGoal}
                  aria-label={p.t("targetSource")}
                  title={p.t("targetSource")}
                >
                  <Fingerprint size={14} />
                </button>
              </div>
              <div className="operator-work-lanes">
                {(["active", "attention", "results", "recorded"] as const).map(
                  (lane) => {
                    const items = mapWork.filter((item) => item.lane === lane);
                    if (!items.length) return null;
                    return (
                      <section
                        key={lane}
                        className={`operator-work-lane operator-work-lane--${lane}`}
                      >
                        <header>
                          <span />
                          <strong>
                            {p.t(
                              lane === "active"
                                ? "activeWork"
                                : lane === "attention"
                                  ? "needsAttention"
                                  : lane === "results"
                                    ? "completedWork"
                                    : "recordedWork",
                            )}
                          </strong>
                          <small>{items.length}</small>
                        </header>
                        {(expandedLanes[lane] ? items : items.slice(0, 4)).map(
                          (item) => (
                            <button
                              key={item.id}
                              className={
                                focusedWork?.id === item.id ? "is-selected" : ""
                              }
                              onClick={() => setWorkId(item.id)}
                              aria-pressed={focusedWork?.id === item.id}
                            >
                              <span className="operator-work-node">
                                {lane === "results" ? (
                                  <FileCheck2 size={17} />
                                ) : lane === "attention" ? (
                                  <TriangleAlert size={17} />
                                ) : (
                                  <Workflow size={17} />
                                )}
                              </span>
                              <span>
                                <strong>{item.title}</strong>
                                <small>
                                  {item.source === "native-record"
                                    ? p.t("fromProjectSource")
                                    : item.source === "service"
                                      ? p.t("serviceStore")
                                      : p.t("nativeHistory")}
                                </small>
                              </span>
                              <ChevronRight size={13} />
                            </button>
                          ),
                        )}
                        {items.length > 4 && (
                          <button
                            className="operator-lane-more"
                            data-expand-work-lane={lane}
                            aria-expanded={Boolean(expandedLanes[lane])}
                            onClick={() =>
                              setExpandedLanes((current) => ({
                                ...current,
                                [lane]: !current[lane],
                              }))
                            }
                          >
                            {expandedLanes[lane]
                              ? p.t("collapse")
                              : `${p.t("showAllWork")} · ${items.length}`}
                            <ChevronRight size={13} />
                          </button>
                        )}
                      </section>
                    );
                  },
                )}
              </div>
              <div className="operator-map-caption">
                <FileCheck2 size={12} />
                <span>{p.t("targetProvenanceHelp")}</span>
              </div>
            </div>
          )}
          <details
            className="operator-requirements-map"
            open={!mapWork.length || undefined}
          >
            <summary>
              <ListChecks size={14} />
              {p.t("requirementsCoverage")}
              <span>{model.requirements.length}</span>
              <ChevronRight size={13} />
            </summary>
            <div className="operator-source-map">
              <div className="operator-map-root">
                <Fingerprint size={26} />
                <strong>{p.selected?.name}</strong>
                <small>{p.t("sourceTruth")}</small>
              </div>
              <div className="operator-map-branches">
                <button
                  data-requirement-branch="all"
                  className={`operator-stage ${stageId === "" ? "is-selected" : ""}`}
                  onClick={() => {
                    setStageId("");
                    setRequirementsExpanded(false);
                  }}
                  aria-pressed={stageId === ""}
                >
                  <ListChecks size={15} />
                  <strong>{p.t("all")}</strong>
                  <span>
                    {model.requirements.length} {p.t("mustCount")}
                  </span>
                </button>
                {model.unstagedRequirements.length > 0 && (
                  <button
                    data-requirement-branch="unassigned"
                    className={`operator-stage ${stageId === "__unassigned" ? "is-selected" : ""}`}
                    onClick={() => {
                      setStageId("__unassigned");
                      setRequirementsExpanded(false);
                    }}
                    aria-pressed={stageId === "__unassigned"}
                  >
                    <span className="operator-node-dot" />
                    <strong>{p.t("operatorUnassigned")}</strong>
                    <span>
                      {model.unstagedRequirements.length} {p.t("mustCount")}
                    </span>
                  </button>
                )}
                {model.stages.length ? (
                  model.stages.map((stage) => (
                    <button
                      key={stage.id}
                      data-requirement-branch={stage.id}
                      className={`operator-stage ${selectedStage?.id === stage.id ? "is-selected" : ""}`}
                      onClick={() => {
                        setStageId(stage.id);
                        setRequirementsExpanded(false);
                      }}
                      aria-pressed={selectedStage?.id === stage.id}
                    >
                      <span className="operator-node-dot" />
                      <strong>{stage.id}</strong>
                      <span>
                        {stage.requirements.length} {p.t("mustCount")}
                      </span>
                    </button>
                  ))
                ) : (
                  <button
                    className="operator-stage is-selected"
                    onClick={() => p.navigate("requirements")}
                  >
                    <ListChecks size={18} />
                    <strong>{p.t("requirements")}</strong>
                    <span>
                      {model.requirements.length} {p.t("actualRecords")}
                    </span>
                  </button>
                )}
              </div>
            </div>
            <div className="operator-map-caption">
              <Network size={12} />
              <span>{p.t("operatorStagesHelp")}</span>
              <button
                onClick={() =>
                  p.inspect({
                    title: p.t("requirementsCoverage"),
                    kind: "requirements",
                    data: {
                      stages: model.stages,
                      dependencies: model.dependencies,
                      phase: p.selected?.phase,
                    },
                  })
                }
              >
                {p.t("provenance")}
                <ChevronRight size={11} />
              </button>
            </div>
            <div className="operator-requirement-detail">
              <div className="operator-section-label">
                <ListChecks size={13} />
                {selectedStage?.id ? `${selectedStage.id} · ` : ""}
                {p.t("requirements")}
              </div>
              {(requirementsExpanded
                ? visibleRequirements
                : visibleRequirements.slice(0, 3)
              ).map((requirement) => {
                const presentation = requirementPresentation(
                  requirement,
                  p.locale,
                );
                return (
                  <button
                    key={requirement.id}
                    data-requirement-id={requirement.id}
                    onClick={() =>
                      p.inspect({
                        title: presentation.title,
                        kind: "requirement",
                        data: requirement,
                      })
                    }
                  >
                    <code>{requirement.id}</code>
                    <span>{presentation.title}</span>
                    <ChevronRight size={14} />
                  </button>
                );
              })}
              {!visibleRequirements.length && (
                <p className="muted">{p.t("noRecords")}</p>
              )}
              {visibleRequirements.length > 3 && (
                <button
                  className="operator-requirements-more"
                  onClick={() => setRequirementsExpanded(!requirementsExpanded)}
                >
                  {requirementsExpanded
                    ? p.t("collapse")
                    : `${p.t("all")} · ${visibleRequirements.length}`}
                  <ChevronRight size={13} />
                </button>
              )}
            </div>
          </details>
        </section>

        <section
          className="operator-action"
          aria-labelledby="operator-next-title"
        >
          {focusedWork && (
            <div className="operator-focus">
              <span className="operator-section-label">
                <Workflow size={14} />
                {p.t("operatorSelectedWork")}
              </span>
              <h3>{focusedWork.title}</h3>
              <span className="tag tag--subtle">
                {focusedWork.source === "native-record"
                  ? p.t("fromProjectSource")
                  : focusedWork.status === "completed"
                    ? p.t("answerReceived")
                    : workStatus(focusedWork.status, p.t)}
              </span>
              {focusedWork.record.outcome && (
                <p>{operatorSummary(focusedWork.record.outcome, 180)}</p>
              )}
              <div className="operator-result-actions">
                {resultPaths.length > 0 && (
                  <Button
                    tone="primary"
                    small
                    icon={BookOpen}
                    disabled={reportLoading}
                    onClick={() => void readReport(resultPaths[0])}
                  >
                    {p.t("operatorReadResult")}
                  </Button>
                )}
              </div>
              <button
                className="operator-source-link"
                onClick={() => inspectWork(focusedWork)}
              >
                {p.t("provenance")}
                <ChevronRight size={12} />
              </button>
            </div>
          )}
          <span className="operator-section-label">
            <ArrowRight size={14} />
            {p.t("nextStep")}
          </span>
          <h2 id="operator-next-title">
            {operatorSummary(nextActionText(action, p.t), 180)}
          </h2>
          <span className="operator-action-origin">
            <FileCheck2 size={13} />
            {action?.source_ref
              ? p.t("fromProjectSource")
              : p.t("proposedNextAction")}
          </span>
          <Button
            tone={resultPaths.length ? "default" : "primary"}
            icon={ArrowRight}
            disabled={Boolean(p.busy)}
            onClick={() =>
              p.newTask({
                universal_entry: true,
                objective: action ? nextActionText(action, p.t) : "",
              })
            }
          >
            {p.t("operatorPrepareNext")}
          </Button>
          {action?.source_ref && (
            <button
              className="operator-source-link"
              onClick={() =>
                p.inspect({
                  title: p.t("nextStep"),
                  kind: "next_action",
                  data: action,
                  sourcePath: action.source_ref,
                })
              }
            >
              {p.t("provenance")}
              <ChevronRight size={12} />
            </button>
          )}
          {decision && (
            <div className="operator-decision">
              <GitPullRequest size={17} />
              <div>
                <small>{p.t("currentDecisions")}</small>
                <button
                  onClick={() =>
                    p.inspect({
                      title: p.t("currentDecisions"),
                      kind: "decision",
                      data: decision,
                      sourcePath: decision.source_ref ?? decision.source_path,
                    })
                  }
                >
                  {text(
                    decision.summary ??
                      decision.text ??
                      decision.title ??
                      decision.id,
                  )}
                  <ChevronRight size={12} />
                </button>
              </div>
            </div>
          )}
          {trail.deferred.length > 0 && (
            <button
              className="operator-deferred"
              onClick={() => p.navigate("context")}
            >
              <Pause size={13} />
              <span>
                {p.t("deferredWork")} · {trail.deferred.length}
              </span>
              <ChevronRight size={12} />
            </button>
          )}
        </section>
      </div>

      <div className="operator-work-strip">
        <section className="operator-live-work">
          <header className="operator-panel-heading">
            <div>
              <ShieldCheck size={17} />
              <h2>{p.t("operatorAcceptance")}</h2>
            </div>
            <button onClick={() => p.navigate("evidence")}>
              {p.t("evidence")}
              <ArrowRight size={13} />
            </button>
          </header>
          <div className="operator-readiness">
            {readinessRows(p.workspace?.readiness)
              .slice(0, 4)
              .map((axis) => (
                <button
                  key={axis.id ?? axis.name}
                  onClick={() =>
                    p.inspect({
                      title: axisLabel(axis, p.t),
                      kind: "evidence",
                      data: axis,
                    })
                  }
                >
                  <span>{axisLabel(axis, p.t)}</span>
                  <Status value={axis.status ?? axis.value} />
                  <ChevronRight size={12} />
                </button>
              ))}
          </div>
          <button
            className="operator-panel-runs"
            onClick={() => p.navigate("jobs")}
          >
            <TerminalSquare size={14} />
            <span>{p.t("serviceStore")}</span>
            <strong>
              {observedJobCounts(p.workspace?.jobs).active} ·{" "}
              {p.t("activeWork")}
            </strong>
            <ArrowRight size={12} />
          </button>
        </section>
        <section className="operator-returned-work">
          <header className="operator-panel-heading">
            <div>
              <FileCheck2 size={17} />
              <h2>{p.t("answerReceived")}</h2>
            </div>
            <button onClick={() => p.navigate("evidence")}>
              {p.t("evidence")}
              <ArrowRight size={13} />
            </button>
          </header>
          {result ? (
            <button
              className="operator-result-summary"
              onClick={() => inspectWork(result)}
            >
              <span className="tag tag--subtle">{p.t("recordedWork")}</span>
              <strong>{result.title}</strong>
              <p>
                {typeof (result.record.outcome ?? result.record.output_text) ===
                "string"
                  ? operatorSummary(
                      result.record.outcome ?? result.record.output_text,
                      220,
                    )
                  : p.t("targetProvenanceHelp")}
              </p>
              <span className="operator-source-link">
                {p.t("inspect")}
                <ArrowRight size={13} />
              </span>
            </button>
          ) : (
            <div className="operator-no-result">
              <FileCheck2 size={22} />
              <p>{p.t("noOutputHelp")}</p>
            </div>
          )}
        </section>
      </div>

      <section className="operator-deliverables">
        <header className="operator-panel-heading">
          <div>
            <FileStack size={17} />
            <h2>{p.t("operatorFiles")}</h2>
            <span className="tag tag--subtle">
              {artifacts.length} {p.t("actualRecords")}
            </span>
          </div>
          <button onClick={() => p.navigate("artifacts")}>
            {p.t("all")}
            <ArrowRight size={13} />
          </button>
        </header>
        <div className="operator-file-shelf">
          {artifacts.slice(0, 5).map((artifact, index) => (
            <button
              key={artifact.id ?? artifact.path ?? index}
              onClick={() => {
                p.inspect({
                  title: text(artifact.name ?? artifact.path),
                  kind: "artifact",
                  data: artifact,
                  sourcePath: artifact.path,
                });
              }}
            >
              <span className="operator-file-mark">
                <FileText size={22} strokeWidth={1.3} />
              </span>
              <span>
                <strong>{sourceTitle(artifact)}</strong>
                <small>
                  {text(artifact.kind ?? artifact.type, p.t("nativeFiles"))}
                </small>
              </span>
              <ChevronRight size={13} />
            </button>
          ))}
          {!artifacts.length && (
            <p className="muted">{p.t("noArtifactsHelp")}</p>
          )}
        </div>
        <p className="operator-inventory-note">
          {p.t("operatorInventoryHelp")}
        </p>
      </section>

      <section
        className="operator-history"
        id="operator-native-history"
        ref={historyRegion}
        tabIndex={-1}
        aria-label={p.t("nativeHistory")}
      >
        <button
          className="operator-history-toggle"
          aria-expanded={showHistory}
          onClick={() => setShowHistory(!showHistory)}
        >
          <Network size={17} />
          <span>
            <strong>{p.t("documentedWork")}</strong>
            <small>{p.t("nativeWorkBoundary")}</small>
          </span>
          <ChevronRight size={16} className={showHistory ? "is-open" : ""} />
        </button>
        {showHistory && (
          <>
            {historyDiscoveryError && (
              <SurfaceNotice tone="error">
                {historyDiscoveryError}
              </SurfaceNotice>
            )}
            <WorkMap
              {...p}
              groups={p.nativeDetail?.work_groups ?? []}
              goal={model.goal}
              bound={p.selected ?? undefined}
            />
            <HistoryPagination
              {...p}
              detail={p.nativeDetail}
              loading={p.nativeHistoryLoading}
              error={p.nativeHistoryError}
              loadMore={p.loadMoreNativeHistory}
            />
            {!p.nativeDetail && (
              <Button
                data-discover-native-history
                small
                icon={RefreshCw}
                disabled={
                  historyDiscovering ||
                  p.nativeHistoryLoading ||
                  Boolean(p.busy)
                }
                onClick={() => void discoverHistory()}
              >
                {historyDiscovering ? p.t("loading") : p.t("discoverCodex")}
              </Button>
            )}
          </>
        )}
      </section>
      <div className="operator-bottom-bar">
        <button onClick={p.openSources}>
          <FileCode2 size={14} />
          {p.t("operatorSources")}
          <ArrowRight size={12} />
        </button>
        <span>
          {p.t("revision")} <code>{shortHash(p.selected?.revision)}</code>
        </span>
      </div>

      {report && (
        <Modal
          title={report.path.split("/").pop() || p.t("operatorReadResult")}
          onClose={() => setReport(null)}
          wide
          footer={
            <>
              <span className="operator-reader-pin">
                <Fingerprint size={12} />
                {shortHash(report.sha256)}
              </span>
              <Button
                onClick={() => {
                  setReport(null);
                  p.expand(report.path, report.content ?? report);
                }}
                icon={FileCode2}
              >
                {p.t("showRaw")}
              </Button>
            </>
          }
        >
          {reportLoading ? (
            <SurfaceNotice>{p.t("loadingSource")}</SurfaceNotice>
          ) : report.error ? (
            <SurfaceNotice tone="error">{report.error}</SurfaceNotice>
          ) : (
            <ReadableWorkReport
              content={
                typeof report.content === "string"
                  ? report.content
                  : pretty(report.content)
              }
            />
          )}
        </Modal>
      )}
    </div>
  );
}

function ReadableWorkReport({ content }: { content: string }) {
  const lines = content.split("\n"),
    blocks = [];
  const inline = (value: string) =>
    value
      .split(/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g)
      .map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**"))
          return <strong key={index}>{part.slice(2, -2)}</strong>;
        if (part.startsWith("`") && part.endsWith("`"))
          return <code key={index}>{part.slice(1, -1)}</code>;
        const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^)]+)\)$/);
        if (link)
          return (
            <a key={index} href={link[2]} target="_blank" rel="noreferrer">
              {link[1]}
            </a>
          );
        return part;
      });
  for (let index = 0; index < lines.length; index++) {
    const line = lines[index].trim();
    if (!line) continue;
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      blocks.push(
        heading[1].length === 1 ? (
          <h2 key={index}>{inline(heading[2])}</h2>
        ) : (
          <h3 key={index}>{inline(heading[2])}</h3>
        ),
      );
      continue;
    }
    if (line.startsWith("```")) {
      const start = index,
        code = [];
      while (++index < lines.length && !lines[index].startsWith("```"))
        code.push(lines[index]);
      blocks.push(<pre key={start}>{code.join("\n")}</pre>);
      continue;
    }
    if (line.startsWith("|")) {
      const start = index,
        table = [];
      do {
        if (!/^\|\s*:?-/.test(lines[index]))
          table.push(
            lines[index]
              .split("|")
              .slice(1, -1)
              .map((cell) => cell.trim()),
          );
        index++;
      } while (index < lines.length && lines[index].trim().startsWith("|"));
      index--;
      blocks.push(
        <div className="operator-reader-table" key={start}>
          <table>
            <thead>
              <tr>
                {table[0]?.map((cell, i) => (
                  <th key={i}>{inline(cell)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.slice(1).map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{inline(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }
    if (/^[-*]\s/.test(line)) {
      const start = index,
        items = [];
      do {
        items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
        index++;
      } while (index < lines.length && /^[-*]\s/.test(lines[index].trim()));
      index--;
      blocks.push(
        <ul key={start}>
          {items.map((item, i) => (
            <li key={i}>{inline(item)}</li>
          ))}
        </ul>,
      );
      continue;
    }
    blocks.push(<p key={index}>{inline(line)}</p>);
  }
  return <article className="operator-readable-report">{blocks}</article>;
}

function ArtifactReportPreview({
  projectId,
  artifact,
  indexedSource,
  downloadURL,
  t,
}: {
  projectId: string;
  artifact: Data;
  indexedSource?: Data;
  downloadURL: string;
  t: ViewProps["t"];
}) {
  const [report, setReport] = useState<Data | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [retry, setRetry] = useState(0);
  const [settledKey, setSettledKey] = useState("");
  const previewRef = useRef<HTMLDivElement | null>(null);
  const verifiedHeight = useRef(0);
  const path = artifact.path ?? artifact.relative_path;
  const bytes = artifact.bytes ?? artifact.size;
  const inputKey = JSON.stringify([
    projectId,
    path,
    bytes,
    artifact.sha256,
    artifact.modified_at,
    indexedSource?.path,
    indexedSource?.sha256,
    indexedSource?.bytes,
    retry,
  ]);
  const pending = loading || settledKey !== inputKey;
  const currentReport = pending ? null : report;
  useLayoutEffect(() => {
    if (currentReport && previewRef.current)
      verifiedHeight.current = previewRef.current.getBoundingClientRect().height;
  }, [currentReport]);
  useEffect(() => {
    const controller = new AbortController();
    let current = true;
    setLoading(true);
    setReport(null);
    setError("");
    api
      .artifactReport(projectId, artifact, indexedSource, controller.signal)
      .then((value) => {
        if (current) setReport(value);
      })
      .catch((failure) => {
        if (current)
          setError(
            failure instanceof Error ? failure.message : String(failure),
          );
      })
      .finally(() => {
        if (current) {
          setSettledKey(inputKey);
          setLoading(false);
        }
      });
    return () => {
      current = false;
      controller.abort();
    };
  }, [inputKey]);
  return (
    <div
      className="panel-padding"
      data-artifact-readable-report
      ref={previewRef}
      style={{ minHeight: pending ? verifiedHeight.current : undefined }}
    >
      <div className="table-toolbar">
        <span className="operator-reader-pin">
          <BookOpen size={14} />
          {t("readOnlyPreview")}
          {currentReport && (
            <span data-artifact-report-pin={currentReport.sha256}>
              {t("sourceInput")} · {t("observedHash")}:{" "}
              {shortHash(currentReport.sha256)}
            </span>
          )}
        </span>
        <a
          className="button"
          href={downloadURL}
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink size={14} />
          {t("openArtifact")}
        </a>
      </div>
      <p className="muted">
        <code>{path}</code>
      </p>
      {pending ? (
        <SurfaceNotice>{t("loadingSource")}</SurfaceNotice>
      ) : error ? (
        <div data-artifact-report-error>
          <SurfaceNotice tone="error">
            {t("previewIncomplete")}: {error}
          </SurfaceNotice>
          <Button
            small
            icon={RefreshCw}
            onClick={() => setRetry((value) => value + 1)}
          >
            {t("retry")}
          </Button>
        </div>
      ) : currentReport ? (
        <div data-artifact-report-observation={currentReport.source_observation}>
          <ReadableWorkReport content={currentReport.content} />
        </div>
      ) : null}
    </div>
  );
}

function TechnicalWorkspaceView(p: ViewProps) {
  const [fileIndex, setFileIndex] = useState(0);
  const [fileContent, setFileContent] = useState<unknown>(undefined);
  const [sourceError, setSourceError] = useState("");
  const [sourceLoading, setSourceLoading] = useState(false);
  const [diffResult, setDiffResult] = useState<Data | null>(null);
  const [diffError, setDiffError] = useState("");
  const [centerTab, setCenterTab] = useState<"source" | "context" | "diff">(
    "source",
  );
  const [rightTab, setRightTab] = useState<"result" | "execution">("result");
  const sources = p.workspace?.sources ?? [];
  const currentSource = sources[fileIndex] ?? sources[0];
  const jobs = p.workspace?.jobs ?? [];
  const activeJob = jobs.find((job) => activeJobStatuses.has(job.status));
  const latestJob = activeJob ?? jobs[0];
  const requirements = p.workspace?.requirements ?? [];
  const profile = projectProfile(p.selected);
  const profileDefinition = profileDefinitions[profile];
  useEffect(() => {
    if (centerTab !== "diff" || p.demo || !p.selected) return;
    let cancelled = false;
    setDiffResult(null);
    setDiffError("");
    api
      .diff(p.selected.id, currentSource?.path)
      .then((result) => {
        if (!cancelled) setDiffResult(result);
      })
      .catch((error) => {
        if (!cancelled) setDiffError(error.message);
      });
    return () => {
      cancelled = true;
    };
  }, [
    centerTab,
    p.selected?.id,
    p.selected?.revision,
    currentSource?.path,
    p.demo,
  ]);
  useEffect(() => {
    const preferred = sources.findIndex((source) =>
      profileDefinition.source.test(source.path ?? source.name ?? ""),
    );
    setFileIndex(preferred >= 0 ? preferred : 0);
    setCenterTab("source");
  }, [p.selected?.id, profile, sources.map((source) => source.path).join("|")]);
  useEffect(() => {
    if (!currentSource || !p.selected) {
      setFileContent(undefined);
      return;
    }
    setSourceError("");
    setFileContent(currentSource.content ?? currentSource.text ?? undefined);
    if (
      currentSource.content !== undefined ||
      currentSource.text !== undefined ||
      p.demo
    )
      return;
    let cancelled = false;
    setSourceLoading(true);
    api
      .source(
        p.selected.id,
        currentSource.path ?? currentSource.relative_path ?? currentSource.name,
      )
      .then((result) => {
        if (!cancelled) setFileContent(result.content);
      })
      .catch((error) => {
        if (!cancelled) setSourceError(error.message);
      })
      .finally(() => {
        if (!cancelled) setSourceLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [currentSource?.path, p.selected?.id, p.demo, currentSource?.sha256]);
  if (!p.selected) return <Welcome {...p} />;
  const sourceName = text(
    currentSource?.name ?? currentSource?.path,
    p.t("source"),
  );
  const task =
    p.demo && p.selected.id === "global-logistics"
      ? p.t("sampleTask")
      : text(
          latestJob?.objective ||
            latestJob?.title ||
            p.workspace?.context?.objective ||
            p.selected.summary,
          p.t("noTaskSelected"),
        );
  const diff =
    diffResult?.diff ??
    p.workspace?.context?.diff ??
    p.workspace?.context?.git?.diff;
  return (
    <div className="workbench-content">
      {!p.demo && <WorkspaceDirection {...p} />}
      <div className="domain-mode">
        <span>
          <Layers3 size={14} />
          {p.t(profileDefinition.title)}
        </span>
        <div>
          <select
            aria-label={p.t("kind")}
            value={profile}
            disabled={p.demo || Boolean(p.busy)}
            onChange={(event) =>
              void p
                .command(
                  "project.profile",
                  { view_profile: event.target.value },
                  p.selected ?? undefined,
                )
                .catch(() => {})
            }
          >
            {(
              [
                "app",
                "bot",
                "game",
                "agent",
                "research",
                "document",
                "mixed",
                "generic",
              ] as Profile[]
            ).map((value) => (
              <option value={value} key={value}>
                {p.t(profileLabel(value))}
              </option>
            ))}
          </select>
          <button
            disabled={p.demo}
            onClick={() =>
              p.newTask({ selected_skills: [profileDefinition.skill] })
            }
          >
            <Braces size={13} />
            {p.t("useSkill")}
            <ChevronRight size={12} />
          </button>
        </div>
      </div>
      <div className="task-ribbon">
        <span className="task-ribbon__icon">
          <Workflow size={16} />
        </span>
        <span>
          <small>
            {p.t(
              p.demo || activeJob
                ? "currentTask"
                : latestJob
                  ? "operatorPriorChecks"
                  : "currentScope",
            )}
          </small>
          <strong>{task}</strong>
        </span>
        <button
          onClick={() =>
            p.inspect({
              title: p.t("taskContext"),
              kind: "context",
              data: p.workspace?.context ?? {},
            })
          }
        >
          <Braces size={14} />
          <span>{p.t("showContext")}</span>
          <ChevronRight size={13} />
        </button>
      </div>
      <div className="workspace-subtabs">
        <button
          className={centerTab === "source" ? "is-active" : ""}
          onClick={() => setCenterTab("source")}
        >
          <FileCode2 size={14} />
          {p.t("contractCheck")}
        </button>
        <button
          className={centerTab === "context" ? "is-active" : ""}
          onClick={() => setCenterTab("context")}
        >
          <Network size={14} />
          {p.t("taskContext")}
        </button>
        <button
          className={centerTab === "diff" ? "is-active" : ""}
          onClick={() => setCenterTab("diff")}
        >
          <GitCompareArrows size={14} />
          {p.t("diff")}
        </button>
        <div />
        <span>
          {p.t("revision")} <code>{shortHash(p.selected.revision)}</code>
        </span>
      </div>
      <div className="operating-grid">
        <Panel
          title={
            centerTab === "context"
              ? p.t("taskContext")
              : centerTab === "diff"
                ? p.t("changeProposal")
                : p.demo
                  ? p.t("sampleSource")
                  : p.t("selectedSource")
          }
          icon={centerTab === "diff" ? GitCompareArrows : FileCode2}
          className="contract-panel"
          tools={
            <>
              <span className="tag tag--subtle">
                {p.demo ? "v1.3.0" : p.selected.kind}
              </span>
              <IconButton
                icon={ArrowDownToLine}
                label={p.t("showRaw")}
                onClick={() =>
                  p.expand(
                    sourceName,
                    fileContent ?? p.workspace?.context ?? {},
                  )
                }
              />
            </>
          }
        >
          {centerTab === "source" ? (
            <>
              {sources.length > 0 && (
                <div className="source-switcher">
                  <FolderGit2 size={14} />
                  <select
                    aria-label={p.t("source")}
                    value={Math.min(fileIndex, Math.max(0, sources.length - 1))}
                    onChange={(e) => setFileIndex(Number(e.target.value))}
                  >
                    {sources.map((source, index) => (
                      <option
                        key={source.id ?? source.path ?? index}
                        value={index}
                      >
                        {text(source.path ?? source.name)}
                      </option>
                    ))}
                  </select>
                  <button
                    aria-label={p.t("provenance")}
                    onClick={() =>
                      p.inspect({
                        title: sourceName,
                        kind: "source",
                        data: currentSource,
                        sourcePath: currentSource.path,
                      })
                    }
                  >
                    <Fingerprint size={14} />
                  </button>
                </div>
              )}
              {sourceLoading && (
                <div className="source-loading">
                  {p.t("loadingSource")}
                  <span />
                </div>
              )}
              {sourceError ? (
                <div className="panel-padding">
                  <SurfaceNotice tone="error">{sourceError}</SurfaceNotice>
                </div>
              ) : fileContent !== undefined ? (
                <CodeViewer
                  value={fileContent}
                  fileName={sourceName}
                  language={
                    sourceName.endsWith(".md")
                      ? "markdown"
                      : sourceName.endsWith(".yaml")
                        ? "yaml"
                        : "json"
                  }
                  selectedLine={
                    p.demo && p.selected.id === "global-logistics"
                      ? 18
                      : undefined
                  }
                  locale={p.locale}
                />
              ) : (
                <Empty icon={FileCode2} title={p.t("noSources")}>
                  {p.t("noSourcesHelp")}
                </Empty>
              )}
            </>
          ) : centerTab === "context" ? (
            <CodeViewer
              value={p.workspace?.context ?? {}}
              fileName="context-capsule.json"
              locale={p.locale}
            />
          ) : p.demo && p.selected.id === "global-logistics" ? (
            <ContractDiff t={p.t} />
          ) : diffError ? (
            <div className="panel-padding">
              <SurfaceNotice tone="warning">{diffError}</SurfaceNotice>
            </div>
          ) : diff ? (
            <CodeViewer
              value={diff}
              fileName="working-tree.diff"
              language="diff"
              locale={p.locale}
            />
          ) : (
            <Empty
              icon={GitCompareArrows}
              title={diffResult ? p.t("matched") : p.t("checking")}
            >
              {diffResult?.notice ?? p.t("readOnlyPreview")}
            </Empty>
          )}
          <div className="panel-statusline">
            <span>
              <Fingerprint size={11} />
              {shortHash(currentSource?.sha256 ?? currentSource?.digest)}
            </span>
            <span>{p.demo ? p.t("exampleOnly") : p.t("readOnlyPreview")}</span>
          </div>
        </Panel>
        <div className="execution-stack">
          <Panel
            title={p.t("apiResponse")}
            icon={TerminalSquare}
            className="response-panel"
            tools={<span className="tag">{p.demo ? "EXAMPLE" : "LOCAL"}</span>}
          >
            {p.demo && p.selected.id === "global-logistics" ? (
              <>
                <div className="request-line">
                  <span className="http-method">POST</span>
                  <code>/shipments</code>
                  <span className="request-label">{p.t("exampleOnly")}</span>
                </div>
                <CodeViewer
                  value={{
                    orderId: "GL-78421",
                    weight: 1250.5,
                    cargoType: "general",
                  }}
                  fileName="request.json"
                  locale={p.locale}
                />
                <div className="response-status">
                  <span>{p.t("response")}</span>
                  <Status value="failed" label="400 · Bad Request" />
                </div>
                <div className="api-error-code">
                  <code>{'{ "code": "INVALID_TYPE",'}</code>
                  <code>{'  "field": "weight",'}</code>
                  <code>{'  "expected": "number" }'}</code>
                </div>
              </>
            ) : (
              <>
                <div className="response-tabs">
                  <button
                    onClick={() => setRightTab("result")}
                    className={rightTab === "result" ? "is-active" : ""}
                  >
                    {p.t("currentScope")}
                  </button>
                  <button
                    onClick={() => setRightTab("execution")}
                    className={rightTab === "execution" ? "is-active" : ""}
                  >
                    {p.t("execution")}
                  </button>
                </div>
                {rightTab === "result" ? (
                  <CodeViewer
                    value={{
                      project: p.selected.name,
                      adapter:
                        p.selected.adapter ??
                        p.selected.adapter_id ??
                        p.selected.kind,
                      revision: p.selected.revision,
                      status: p.selected.status ?? "source_only",
                      capabilities: p.selected.capabilities ?? {},
                    }}
                    fileName="project-observation.json"
                    locale={p.locale}
                  />
                ) : latestJob ? (
                  <CodeViewer
                    value={
                      latestJob.output_text ??
                      latestJob.output ??
                      latestJob.result ??
                      latestJob
                    }
                    fileName="execution-result.json"
                    locale={p.locale}
                  />
                ) : (
                  <Empty compact icon={Terminal} title={p.t("noOutput")}>
                    {p.t("noOutputHelp")}
                  </Empty>
                )}
              </>
            )}
          </Panel>
          <Panel
            title={p.t("outcome")}
            icon={ShieldCheck}
            className="outcome-panel"
          >
            {p.demo && p.selected.id === "global-logistics" ? (
              <>
                <div className="outcome-finding">
                  <TriangleAlert size={17} />
                  <strong>{p.t("sampleResult")}</strong>
                </div>
                <p>{p.t("sampleIssue")}</p>
                <div className="recommendation">
                  <small>{p.t("changeProposal")}</small>
                  <p>{p.t("sampleRecommendation")}</p>
                </div>
                <div className="outcome-footer">
                  <Status value="source_only" label={p.t("sampleBuild")} />
                  <button onClick={() => setCenterTab("diff")}>
                    {p.t("diff")}
                    <ArrowRight size={13} />
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="evidence-pills">
                  {readinessRows(p.workspace?.readiness)
                    .slice(0, 4)
                    .map((axis) => (
                      <button
                        key={axis.id ?? axis.name}
                        onClick={() =>
                          p.inspect({
                            title: axisLabel(axis, p.t),
                            kind: "evidence",
                            data: axis,
                          })
                        }
                      >
                        <span>{axisLabel(axis, p.t)}</span>
                        <Status value={axis.status ?? axis.value} />
                      </button>
                    ))}
                </div>
                <div className="outcome-footer">
                  <span>{p.t("evidencePending")}</span>
                  <button onClick={() => p.navigate("evidence")}>
                    {p.t("inspect")}
                    <ArrowRight size={13} />
                  </button>
                </div>
              </>
            )}
          </Panel>
        </div>
      </div>
      <div className="context-grid">
        <Panel
          title={p.t("relatedWork")}
          icon={Network}
          className="topology-panel"
          tools={<span className="tag tag--subtle">{p.t("sourceTruth")}</span>}
        >
          {p.nativeDetail?.work_groups?.length ? (
            <WorkMap
              {...p}
              groups={p.nativeDetail.work_groups}
              goal={p.nativeDetail.goal}
              bound={p.selected ?? undefined}
            />
          ) : (
            <Topology
              sources={sources}
              taskCount={jobs.length}
              t={p.t}
              projectName={p.selected.name}
              onSelect={(source) =>
                p.inspect({
                  title: text(source.name ?? source.path),
                  kind: "source",
                  data: source,
                  sourcePath: source.path,
                })
              }
            />
          )}
          <HistoryPagination
            {...p}
            detail={p.nativeDetail}
            loading={p.nativeHistoryLoading}
            error={p.nativeHistoryError}
            loadMore={p.loadMoreNativeHistory}
          />
        </Panel>
        <Panel
          title={p.t("sourceDocuments")}
          icon={Layers3}
          className="linked-sources-panel"
        >
          <div className="linked-sources">
            {sources.slice(0, 4).map((source, index) => (
              <button
                key={source.id ?? source.path ?? index}
                onClick={() => {
                  setFileIndex(index);
                  setCenterTab("source");
                }}
              >
                <FileCode2 size={14} />
                <span>{text(source.name ?? source.path)}</span>
                <code>{text(source.version, shortHash(source.sha256))}</code>
                <span
                  className={`mini-state mini-state--${source.status === "needs_review" ? "warning" : "neutral"}`}
                />
              </button>
            ))}
            {!sources.length && <Empty compact title={p.t("noSources")} />}
          </div>
        </Panel>
      </div>
      <div className="requirements-queue">
        <div>
          <ListChecks size={15} />
          <strong>{p.t("requirementsCoverage")}</strong>
          <span>
            {requirements.length} {p.t("mustCount")}
          </span>
        </div>
        <div>
          {requirements.slice(0, 3).map((req) => (
            <button
              key={req.id}
              onClick={() =>
                p.inspect({
                  title: text(req.title ?? req.id),
                  kind: "requirement",
                  data: req,
                })
              }
            >
              <code>{req.id}</code>
              <span>{text(req.title ?? req.description ?? req.text)}</span>
              <Status value={req.status ?? "source_only"} />
            </button>
          ))}
        </div>
        <button
          className="text-link"
          onClick={() => p.navigate("requirements")}
        >
          {p.t("all")}
          <ArrowRight size={13} />
        </button>
      </div>
    </div>
  );
}

export function ContextView(p: ViewProps) {
  if (!p.selected) return <Welcome {...p} />;
  const context = p.workspace?.context ?? {};
  return (
    <div className="page-content">
      <SectionHeading
        icon={Network}
        title={p.t("context")}
        description={p.t("contextGraph")}
      />
      <div className="context-control-grid">
        <ContextCoveragePanel {...p} />
        <ContextTrailPanels {...p} />
      </div>
      <div className="context-reader-grid">
        <Panel
          title={p.t("contextRecord")}
          icon={Braces}
          onExpand={() => p.expand(p.t("contextRecord"), context)}
          t={p.t}
        >
          <CodeViewer
            value={context}
            fileName="current-context.json"
            locale={p.locale}
          />
        </Panel>
        <div className="context-side-stack">
          <Panel title={p.t("decisions")} icon={GitPullRequest}>
            {(p.workspace?.decisions ?? []).length ? (
              <RecordList
                entries={p.workspace?.decisions ?? []}
                kind="decision"
                {...p}
              />
            ) : (
              <Empty compact title={p.t("noDecisions")}>
                {p.t("noDecisionsHelp")}
              </Empty>
            )}
          </Panel>
          <Panel title={p.t("sourceIdentity")} icon={Fingerprint}>
            <div className="panel-padding">
              <RecordDetails
                value={{
                  project: p.selected.name,
                  root: p.selected.root,
                  revision: p.selected.revision,
                  adapter: p.selected.adapter_id ?? p.selected.kind,
                }}
                t={p.t}
              />
              <SurfaceNotice>{p.t("statePreserved")}</SurfaceNotice>
            </div>
          </Panel>
        </div>
      </div>
      <Panel title={p.t("dependentWork")} icon={Workflow}>
        <Topology
          sources={p.workspace?.sources ?? []}
          taskCount={p.workspace?.jobs.length ?? 0}
          t={p.t}
          projectName={p.selected.name}
          onSelect={(data) =>
            p.inspect({
              title: text(data.name ?? data.path),
              kind: "source",
              data,
            })
          }
        />
      </Panel>
    </div>
  );
}

export function RequirementsView(p: ViewProps) {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const reqs = (p.workspace?.requirements ?? []).filter(
    (req) =>
      (filter === "all" ||
        req.priority === filter ||
        requirementPresentation(req, p.locale).status === filter) &&
      pretty(req).toLowerCase().includes(query.toLowerCase()),
  );
  if (!p.selected) return <Welcome {...p} />;
  return (
    <div className="page-content">
      <SectionHeading
        icon={ListChecks}
        title={p.t("requirements")}
        description={p.t("sourceTruth")}
      />
      <Panel
        title={p.t("inventory")}
        icon={ListChecks}
        tools={<span className="tag">{reqs.length}</span>}
      >
        <div className="table-toolbar">
          <div className="inline-search">
            <Search size={15} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label={p.t("searchShort")}
              placeholder={p.t("searchShort")}
            />
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            aria-label={p.t("filter")}
          >
            <option value="all">{p.t("all")}</option>
            <option value="must">{p.t("mandatory")}</option>
            <option value="deferred">{p.t("deferred")}</option>
            <option value="pending">{p.t("pending")}</option>
          </select>
        </div>
        {reqs.length ? (
          <div className="requirements-table">
            <div className="requirements-table__head">
              <span>ID</span>
              <span>{p.t("requirements")}</span>
              <span>{p.t("source")}</span>
              <span>{p.t("statusInSource")}</span>
            </div>
            {reqs.map((req, index) => (
              <button
                key={req.id ?? index}
                onClick={() =>
                  p.inspect({
                    title: text(
                      requirementPresentation(req, p.locale).title || req.id,
                    ),
                    kind: "requirement",
                    data: req,
                  })
                }
              >
                <code>{text(req.id)}</code>
                <span>
                  <strong>
                    {text(requirementPresentation(req, p.locale).title)}
                  </strong>
                  {req.acceptance && <small>{text(req.acceptance)}</small>}
                </span>
                <span className="source-reference">
                  <FileText size={12} />
                  {text(req.source ?? req.source_ref ?? req.source_id)}
                </span>
                <Status value={requirementPresentation(req, p.locale).status} />
              </button>
            ))}
          </div>
        ) : (
          <Empty icon={ListChecks} title={p.t("noRequirements")}>
            {p.t("noRequirementsHelp")}
          </Empty>
        )}
      </Panel>
    </div>
  );
}

export function IdentityView(p: ViewProps) {
  if (!p.selected) return <Welcome {...p} />;
  const records = rows(p.workspace?.identity);
  const identity = p.workspace?.identity ?? {};
  const palette = rows(
    (identity as Data).palette ?? (identity as Data).tokens?.colors,
  );
  return (
    <div className="page-content">
      <SectionHeading
        icon={Sparkles}
        title={p.t("identity")}
        description={p.t("noIdentityChange")}
      />
      <div className="identity-grid">
        <Panel title={p.t("currentIdentity")} icon={Fingerprint}>
          <div className="identity-header">
            <span
              className={`identity-monogram project-icon--${p.selected.kind}`}
            >
              {p.selected.name.slice(0, 1)}
            </span>
            <div>
              <h2>{p.selected.name}</h2>
              <Status
                value={
                  (identity as Data).status ??
                  (records.length ? "source_only" : "not_observed")
                }
              />
            </div>
          </div>
          {records.length ? (
            <div className="panel-padding">
              <RecordDetails
                value={
                  Array.isArray(identity) ? { records: identity } : identity
                }
                t={p.t}
              />
              <Button
                small
                tone="quiet"
                icon={Braces}
                onClick={() => p.expand(p.t("currentIdentity"), identity)}
              >
                {p.t("showRaw")}
              </Button>
            </div>
          ) : (
            <Empty compact icon={Fingerprint} title={p.t("noIdentity")}>
              {p.t("noIdentityHelp")}
            </Empty>
          )}
        </Panel>
        <Panel title={p.t("palette")} icon={Image}>
          {palette.length ? (
            <div className="palette-grid">
              {palette.map((color, index) => {
                const value = color.value ?? color.hex;
                return (
                  <button
                    key={index}
                    onClick={() =>
                      p.inspect({
                        title: text(color.name ?? color.id),
                        kind: "identity",
                        data: color,
                      })
                    }
                  >
                    <span
                      style={{
                        backgroundColor: /^#[0-9a-f]{3,8}$/i.test(value ?? "")
                          ? value
                          : "var(--surface-deep)",
                      }}
                    />
                    <strong>{text(color.name ?? color.id)}</strong>
                    <code>{text(value)}</code>
                  </button>
                );
              })}
            </div>
          ) : (
            <Empty compact icon={Layers3} title={p.t("noRecords")}>
              {p.t("noIdentityHelp")}
            </Empty>
          )}
        </Panel>
      </div>
      <Panel title={p.t("artifacts")} icon={FileStack}>
        <RecordList
          entries={p.workspace?.artifacts ?? []}
          kind="artifact"
          {...p}
        />
      </Panel>
    </div>
  );
}

export function EvidenceView(p: ViewProps) {
  if (!p.selected) return <Welcome {...p} />;
  const axes = readinessRows(p.workspace?.readiness);
  const evidence = [
    ...rows(p.workspace?.evidence ?? p.workspace?.context?.evidence),
    ...rows(p.workspace?.service_evidence),
  ];
  return (
    <div className="page-content">
      <SectionHeading
        icon={ShieldCheck}
        title={p.t("evidence")}
        description={p.t("noEvidenceHelp")}
      />
      <div className="readiness-grid">
        {axes.map((axis, index) => (
          <button
            key={axis.id ?? index}
            className="readiness-axis"
            onClick={() =>
              p.inspect({
                title: axisLabel(axis, p.t),
                kind: "evidence",
                data: axis,
              })
            }
          >
            <div>
              <span className="axis-index">
                {String(index + 1).padStart(2, "0")}
              </span>
              <ShieldCheck size={19} strokeWidth={1.3} />
            </div>
            <h2>{axisLabel(axis, p.t)}</h2>
            <Status value={axis.status ?? axis.value} />
            <p>
              {text(
                axis.scope ?? axis.description ?? axis.reason,
                p.t("notTested"),
              )}
            </p>
            <span className="axis-inspect">
              {p.t("inspect")}
              <ChevronRight size={13} />
            </span>
          </button>
        ))}
      </div>
      <Panel title={p.t("receipts")} icon={FileCheck2}>
        {evidence.length ? (
          <RecordList entries={evidence} kind="evidence" {...p} />
        ) : (
          <Empty icon={FileCheck2} title={p.t("noEvidence")}>
            {p.t("noEvidenceHelp")}
          </Empty>
        )}
      </Panel>
      <Panel title={p.t("execution")} icon={Activity}>
        <RecordList entries={p.workspace?.jobs ?? []} kind="job" {...p} />
      </Panel>
      <Panel title={p.t("ownerAcceptance")} icon={ShieldCheck}>
        <RecordList
          entries={(p.workspace?.jobs ?? [])
            .filter((job) => job.review_status)
            .map((job) => ({
              id: job.id,
              title: job.objective ?? job.id,
              status: job.review_status,
              scope: p.t("ownerReviewOnly"),
              kind: "owner-review",
              independent_qa: false,
              capsule_sha256: job.capsule_sha256,
            }))}
          kind="owner-review"
          {...p}
        />
      </Panel>
    </div>
  );
}

export function ArtifactsView(p: ViewProps) {
  const [selection, setSelection] = useState<{
    projectId: string;
    path: string;
  } | null>(null);
  const [query, setQuery] = useState("");
  const previewRef = useRef<HTMLDivElement | null>(null);
  const artifactKey = (artifact: Data) =>
    text(artifact.path ?? artifact.relative_path ?? artifact.id);
  const currentArtifacts: Data[] = p.workspace?.artifacts ?? [];
  const selected =
    p.selected && selection?.projectId === text(p.selected.id)
      ? (currentArtifacts.find(
          (artifact) => artifactKey(artifact) === selection.path,
        ) ?? null)
      : null;
  const artifacts = currentArtifacts.filter((a) =>
    pretty(a).toLowerCase().includes(query.toLowerCase()),
  );
  useEffect(() => {
    if (!selected) return;
    // Only a changed user selection reveals the preview; polling never moves it.
    previewRef.current
      ?.closest(".panel")
      ?.querySelector(".panel__header")
      ?.scrollIntoView({
        block: "nearest",
        inline: "nearest",
        behavior: "auto",
      });
  }, [selection?.projectId, selection?.path]);
  if (!p.selected) return <Welcome {...p} />;
  const mediaURL =
    selected && !p.demo
      ? `/api/v1/projects/${encodeURIComponent(p.selected.id)}/artifact?path=${encodeURIComponent(selected.path ?? selected.relative_path)}`
      : "";
  const name = text(selected?.name ?? selected?.path);
  const extension = name.toLowerCase().split(".").pop();
  const selectedPath = selected?.path ?? selected?.relative_path;
  const reportSource = (p.workspace?.sources ?? []).find(
    (source) => source.path === selectedPath,
  );
  return (
    <div className="page-content">
      <SectionHeading
        icon={FileStack}
        title={p.t("artifacts")}
        description={
          p.t("sourceInput") +
          " · " +
          p.t("editableMaster") +
          " · " +
          p.t("returnedOutput")
        }
      />
      <div className="artifact-workspace">
        <Panel title={p.t("artifacts")} icon={FileStack}>
          <div className="table-toolbar">
            <div className="inline-search">
              <Search size={14} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={p.t("searchShort")}
                aria-label={p.t("searchShort")}
              />
            </div>
          </div>
          {artifacts.length ? (
            <div className="artifact-list">
              {artifacts.map((artifact, index) => (
                <button
                  key={artifact.id ?? artifact.path ?? index}
                  title={text(artifact.path ?? artifact.name)}
                  aria-label={text(artifact.path ?? artifact.name)}
                  className={
                    selected && artifactKey(selected) === artifactKey(artifact)
                      ? "is-selected"
                      : ""
                  }
                  onClick={() => {
                    setSelection({
                      projectId: text(p.selected?.id),
                      path: artifactKey(artifact),
                    });
                    p.inspect({
                      title: text(artifact.name ?? artifact.path),
                      kind: "artifact",
                      data: artifact,
                      sourcePath: artifact.path,
                    });
                  }}
                >
                  <FileSymbol name={artifact.name ?? artifact.path} />
                  <span>
                    <strong>{text(artifact.name ?? artifact.path)}</strong>
                    {artifact.path && artifact.path !== artifact.name && (
                      <small style={{ overflowWrap: "anywhere" }}>
                        {text(artifact.path)}
                      </small>
                    )}
                    <small>
                      {text(artifact.kind ?? artifact.type)} ·{" "}
                      {text(artifact.bytes ?? artifact.size)} B
                    </small>
                  </span>
                  <ChevronRight size={14} />
                </button>
              ))}
            </div>
          ) : (
            <Empty icon={FileStack} title={p.t("noArtifacts")}>
              {p.t("noArtifactsHelp")}
            </Empty>
          )}
        </Panel>
        <Panel
          title={selected ? name : p.t("preview")}
          icon={FileImage}
          tools={
            selected && <Status value={selected.status ?? "source_only"} />
          }
        >
          {selected ? (
            <div className="artifact-preview" ref={previewRef}>
              {mediaURL && /\.(md|markdown)$/i.test(selectedPath ?? "") ? (
                <ArtifactReportPreview
                  key={JSON.stringify([p.selected.id, selectedPath])}
                  projectId={p.selected.id}
                  artifact={selected}
                  indexedSource={reportSource}
                  downloadURL={mediaURL}
                  t={p.t}
                />
              ) : mediaURL &&
                ["png", "jpg", "jpeg", "webp", "gif"].includes(
                  extension ?? "",
                ) ? (
                <img
                  src={mediaURL}
                  alt={text(
                    selected.description ?? selected.name ?? selected.path,
                  )}
                />
              ) : mediaURL &&
                ["mp3", "wav", "ogg", "m4a"].includes(extension ?? "") ? (
                <audio controls src={mediaURL} />
              ) : mediaURL &&
                ["mp4", "webm", "mov"].includes(extension ?? "") ? (
                <video controls src={mediaURL} />
              ) : selected.content ? (
                <CodeViewer
                  value={selected.content}
                  fileName={name}
                  locale={p.locale}
                />
              ) : (
                <div className="panel-padding">
                  <RecordDetails value={selected} t={p.t} />
                  {mediaURL && (
                    <a
                      className="button"
                      href={mediaURL}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <ExternalLink size={14} />
                      {p.t("openArtifact")}
                    </a>
                  )}
                </div>
              )}
            </div>
          ) : (
            <Empty icon={FileImage} title={p.t("noSelection")}>
              {p.t("noSelectionHelp")}
            </Empty>
          )}
        </Panel>
      </div>
    </div>
  );
}

export function JobsView(p: ViewProps) {
  const [job, setJob] = useState<Data | null>(null);
  const [taskToReview, setTaskToReview] = useState<Data | null>(null);
  const [scopeReviewed, setScopeReviewed] = useState(false);
  const [tab, setTab] = useState<"output" | "trace" | "context">("output");
  const jobs = p.boot?.jobs ?? [];
  const preparedTasks = rows(p.boot?.tasks).filter(
    (task) => task.status === "prepared",
  );
  const selectedJob = job ?? jobs[0];
  useEffect(() => {
    if (!job?.id || p.demo) return;
    const current = jobs.find((j) => j.id === job.id);
    if (current) setJob(current);
  }, [p.boot?.jobs]);
  async function selectJob(value: Data) {
    setJob(value);
    p.inspect({
      title: text(value.title ?? value.id),
      kind: "job",
      data: value,
    });
    if (!p.demo)
      try {
        const detail = await api.job(value.id);
        setJob(detail.job ?? detail);
      } catch {
        /* keep observed summary */
      }
  }
  const pending = rows(selectedJob?.pending_requests ?? selectedJob?.approvals);
  return (
    <div className="page-content jobs-view">
      <PageHeading
        eyebrow={p.t("operations")}
        title={p.t("jobs")}
        description={p.t("noJobsHelp")}
        action={
          <Button
            tone="primary"
            icon={Plus}
            onClick={p.newTask}
            disabled={!p.selected || p.demo}
          >
            {p.t("newTask")}
          </Button>
        }
      />
      <div className="jobs-workspace">
        <Panel
          title={p.t("runHistory")}
          icon={Activity}
          tools={<span className="tag">{jobs.length}</span>}
        >
          {preparedTasks.length > 0 && (
            <div className="prepared-task-list">
              <h3>{p.t("preparedTask")}</h3>
              {preparedTasks.map((task) => (
                <button
                  key={task.id}
                  onClick={() => {
                    setTaskToReview(task);
                    setScopeReviewed(false);
                  }}
                >
                  <FileCheck2 size={16} />
                  <span>
                    <strong>{text(task.objective)}</strong>
                    <small>{task.scope}</small>
                  </span>
                  <ChevronRight size={13} />
                </button>
              ))}
            </div>
          )}
          {jobs.length ? (
            <div className="job-list">
              {jobs.map((item) => (
                <button
                  key={item.id}
                  className={selectedJob?.id === item.id ? "is-selected" : ""}
                  onClick={() => void selectJob(item)}
                >
                  <span className="job-symbol">
                    <Workflow size={17} />
                  </span>
                  <span>
                    <strong>
                      {text(item.title ?? item.objective ?? item.id)}
                    </strong>
                    <small>
                      {text(item.project_name ?? item.project_id)} ·{" "}
                      {formatTime(item.created_at, p.locale)}
                    </small>
                    <Status value={item.status} />
                  </span>
                  <ChevronRight size={13} />
                </button>
              ))}
            </div>
          ) : (
            <Empty icon={Workflow} title={p.t("noJobs")}>
              {p.t("noJobsHelp")}
            </Empty>
          )}
        </Panel>
        <Panel
          title={p.t("console")}
          icon={TerminalSquare}
          tools={selectedJob && <Status value={selectedJob.status} />}
          className="job-console"
        >
          {selectedJob ? (
            <>
              <div className="console-heading">
                <div>
                  {selectedJob.task_id &&
                    ["running", "dispatching"].includes(selectedJob.status) && (
                      <Button
                        small
                        icon={Pause}
                        disabled={p.demo || Boolean(p.busy)}
                        onClick={() =>
                          void p
                            .command(
                              "task.pause",
                              { task_id: selectedJob.task_id },
                              p.boot?.projects.find(
                                (project) =>
                                  project.id === selectedJob.project_id,
                              ),
                            )
                            .catch(() => {})
                        }
                      >
                        {p.t("pauseTask")}
                      </Button>
                    )}
                  {selectedJob.task_id &&
                    ["paused", "cancelled", "failed"].includes(
                      selectedJob.status,
                    ) && (
                      <Button
                        small
                        icon={Workflow}
                        disabled={p.demo || Boolean(p.busy)}
                        onClick={() =>
                          void p
                            .command(
                              "task.continue",
                              { task_id: selectedJob.task_id },
                              p.boot?.projects.find(
                                (project) =>
                                  project.id === selectedJob.project_id,
                              ),
                            )
                            .then((result) => {
                              if (result.job) setJob(result.job);
                            })
                            .catch(() => {})
                        }
                      >
                        {p.t("continueTask")}
                      </Button>
                    )}
                  <code>{selectedJob.id}</code>
                  <h2>{text(selectedJob.objective ?? selectedJob.title)}</h2>
                </div>
                <div>
                  {[
                    "running",
                    "dispatching",
                    "awaiting_approval",
                    "awaiting_input",
                  ].includes(selectedJob.status) && (
                    <Button
                      small
                      tone="danger"
                      icon={Pause}
                      disabled={p.demo || Boolean(p.busy)}
                      onClick={() =>
                        void p
                          .command("job.interrupt", { job_id: selectedJob.id })
                          .catch(() => {})
                      }
                    >
                      {p.t("interrupt")}
                    </Button>
                  )}
                  {[
                    "outcome_unknown",
                    "reconciling",
                    "cancel_requested",
                  ].includes(selectedJob.status) && (
                    <Button
                      small
                      icon={RefreshCw}
                      disabled={p.demo || Boolean(p.busy)}
                      onClick={() =>
                        void p
                          .command("job.reconcile", { job_id: selectedJob.id })
                          .catch(() => {})
                      }
                    >
                      {p.t("reconcile")}
                    </Button>
                  )}
                </div>
              </div>
              <div className="console-tabs">
                {(["output", "trace", "context"] as const).map((value) => (
                  <button
                    className={tab === value ? "is-active" : ""}
                    key={value}
                    onClick={() => setTab(value)}
                  >
                    {p.t(value)}
                  </button>
                ))}
              </div>
              {tab === "output" ? (
                <div className="execution-output">
                  <pre>
                    {typeof selectedJob.output_text === "string"
                      ? selectedJob.output_text
                      : typeof selectedJob.output === "string"
                        ? selectedJob.output
                        : selectedJob.output
                          ? pretty(selectedJob.output)
                          : selectedJob.result
                            ? pretty(selectedJob.result)
                            : p.t("noOutput")}
                  </pre>
                </div>
              ) : tab === "trace" ? (
                <div className="event-trace">
                  {rows(selectedJob.events ?? selectedJob.activity).map(
                    (event, index) => (
                      <button
                        key={event.id ?? index}
                        onClick={() =>
                          p.inspect({
                            title: text(event.type ?? event.method),
                            kind: "event",
                            data: event,
                          })
                        }
                      >
                        <span className="trace-marker" />
                        <time>
                          {formatTime(
                            event.created_at ??
                              event.timestamp ??
                              event.observed_at,
                            p.locale,
                          )}
                        </time>
                        <code>{text(event.type ?? event.method)}</code>
                        <span>
                          {text(
                            event.message ??
                              event.summary ??
                              event.status ??
                              event.params?.item?.text ??
                              event.params?.turn?.status,
                          )}
                        </span>
                      </button>
                    ),
                  )}
                  {!rows(selectedJob.events).length && (
                    <Empty compact title={p.t("noRecords")} />
                  )}
                </div>
              ) : (
                <CodeViewer
                  value={
                    selectedJob.capsule ?? selectedJob.context ?? selectedJob
                  }
                  fileName="execution-context.json"
                  locale={p.locale}
                />
              )}
              {pending.length > 0 && (
                <div className="approval-region">
                  <h3>
                    <ShieldCheck size={17} />
                    {p.t("awaitingApproval")}
                  </h3>
                  <p>{p.t("approvalHelp")}</p>
                  {pending.map((request, index) => (
                    <div
                      className="approval-request"
                      key={request.id ?? request.request_id ?? index}
                    >
                      <CodeViewer
                        value={request}
                        fileName={text(request.method ?? request.id)}
                        locale={p.locale}
                      />
                      {request.method === "item/tool/requestUserInput" ? (
                        <HostQuestionForm
                          request={request}
                          job={selectedJob}
                          {...p}
                        />
                      ) : (
                        <>
                          {request.can_accept !== true && (
                            <SurfaceNotice tone="warning">
                              {text(request.scope_notice, p.t("scopeBoundary"))}
                            </SurfaceNotice>
                          )}
                          <div>
                            <Button
                              small
                              tone="danger"
                              disabled={p.demo || Boolean(p.busy)}
                              onClick={() =>
                                void p
                                  .command("approval.respond", {
                                    job_id: selectedJob.id,
                                    request_id:
                                      request.request_id ?? request.id,
                                    decision: "decline",
                                  })
                                  .catch(() => {})
                              }
                            >
                              {p.t("decline")}
                            </Button>
                            <Button
                              small
                              tone="primary"
                              disabled={
                                p.demo ||
                                Boolean(p.busy) ||
                                request.can_accept !== true
                              }
                              onClick={() =>
                                void p
                                  .command("approval.respond", {
                                    job_id: selectedJob.id,
                                    request_id:
                                      request.request_id ?? request.id,
                                    decision: "accept",
                                  })
                                  .catch(() => {})
                              }
                            >
                              {p.t("approve")}
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {selectedJob.status === "completed" && (
                <JobReview job={selectedJob} {...p} />
              )}
              <div className="panel-statusline">
                <span>
                  <LockKeyhole size={12} />
                  {text(selectedJob.scope ?? selectedJob.task?.scope)}
                </span>
                <span>
                  {p.demo ? p.t("exampleOnly") : p.t("actualExecution")}
                </span>
              </div>
            </>
          ) : (
            <Empty icon={Terminal} title={p.t("noTaskSelected")}>
              {p.t("noOutputHelp")}
            </Empty>
          )}
        </Panel>
      </div>
      {taskToReview && (
        <Modal
          title={p.t("preparedTask")}
          onClose={() => setTaskToReview(null)}
          wide
          footer={
            <>
              <Button onClick={() => setTaskToReview(null)}>
                {p.t("close")}
              </Button>
              <Button
                tone="primary"
                icon={Workflow}
                disabled={!scopeReviewed || p.demo || Boolean(p.busy)}
                onClick={() =>
                  void p
                    .command(
                      "task.dispatch",
                      { task_id: taskToReview.id },
                      p.boot?.projects.find(
                        (project) => project.id === taskToReview.project_id,
                      ),
                    )
                    .then((result) => {
                      setTaskToReview(null);
                      if (result.job) setJob(result.job);
                    })
                    .catch(() => {})
                }
              >
                {p.t("dispatch")}
              </Button>
            </>
          }
        >
          <SurfaceNotice>{p.t("taskPreparedNote")}</SurfaceNotice>
          <CodeViewer
            value={taskToReview.capsule ?? taskToReview}
            fileName="context-capsule.json"
            locale={p.locale}
          />
          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={scopeReviewed}
              onChange={(event) => setScopeReviewed(event.target.checked)}
            />
            <span>{p.t("confirmExactScope")}</span>
          </label>
        </Modal>
      )}
    </div>
  );
}

function JobReview(p: ViewProps & { job: Data }) {
  const [note, setNote] = useState("");
  const [recorded, setRecorded] = useState<Data | null>(null);
  async function review(verdict: "accepted" | "rework") {
    try {
      const result = await p.command(
        "job.review",
        { job_id: p.job.id, verdict, note },
        p.boot?.projects.find((project) => project.id === p.job.project_id),
      );
      setRecorded(result.review);
    } catch {
      /* global command error is visible */
    }
  }
  return (
    <div className="owner-review">
      <h3>
        <ShieldCheck size={16} />
        {p.t("reviewResult")}
        {p.job.review_status && <Status value={p.job.review_status} />}
      </h3>
      <p>{p.t("ownerReviewOnly")}</p>
      <Field label={p.t("reviewNote")}>
        <textarea
          rows={3}
          value={note}
          onChange={(event) => setNote(event.target.value)}
        />
      </Field>
      <div>
        <Button
          small
          disabled={p.demo || Boolean(p.busy) || note.trim().length < 3}
          onClick={() => void review("rework")}
        >
          {p.t("rework")}
        </Button>
        <Button
          small
          tone="primary"
          disabled={p.demo || Boolean(p.busy) || note.trim().length < 3}
          onClick={() => void review("accepted")}
        >
          {p.t("acceptResult")}
        </Button>
      </div>
      {recorded && (
        <SurfaceNotice tone="good">
          {p.t("actionRecorded")} · {recorded.verdict}
        </SurfaceNotice>
      )}
    </div>
  );
}

function HostQuestionForm(p: ViewProps & { request: Data; job: Data }) {
  const questions = rows(p.request.params?.questions ?? p.request.questions);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const complete = questions.every((question) =>
    Boolean(answers[question.id]?.trim()),
  );
  async function respond() {
    const response = Object.fromEntries(
      questions.map((question) => [
        question.id,
        { answers: [answers[question.id]] },
      ]),
    );
    try {
      await p.command("approval.respond", {
        job_id: p.job.id,
        request_id: p.request.id,
        decision: { answers: response },
      });
    } catch {
      /* global command error is visible */
    }
  }
  return (
    <div className="host-questions">
      {questions.map((question) => (
        <fieldset key={question.id}>
          <legend>{text(question.header ?? question.question)}</legend>
          <p>{text(question.question)}</p>
          {rows(question.options).length > 0 && (
            <div className="question-options">
              {rows(question.options).map((option, index) => (
                <label key={index}>
                  <input
                    type="radio"
                    name={question.id}
                    value={option.label}
                    checked={answers[question.id] === option.label}
                    onChange={() =>
                      setAnswers({ ...answers, [question.id]: option.label })
                    }
                  />
                  <span>
                    <strong>{text(option.label)}</strong>
                    <small>{text(option.description, "")}</small>
                  </span>
                </label>
              ))}
            </div>
          )}
          <textarea
            rows={2}
            aria-label={text(question.question)}
            value={answers[question.id] ?? ""}
            onChange={(event) =>
              setAnswers({ ...answers, [question.id]: event.target.value })
            }
          />
        </fieldset>
      ))}
      <Button
        small
        tone="primary"
        disabled={!complete || p.demo || Boolean(p.busy)}
        onClick={() => void respond()}
      >
        {p.t("confirm")}
      </Button>
    </div>
  );
}

export function SkillsView(p: ViewProps) {
  const [construction, setConstruction] = useState<"agent" | "skill" | null>(
    null,
  );
  const [constructionGoal, setConstructionGoal] = useState("");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Data | null>(null);
  const [operation, setOperation] = useState<
    "audit" | "plan" | "diff" | "apply" | "verify" | "rollback"
  >("audit");
  const [planId, setPlanId] = useState("");
  const [planHash, setPlanHash] = useState("");
  const [journalId, setJournalId] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<Data | null>(null);
  const [error, setError] = useState("");
  const [skillSource, setSkillSource] = useState<Data | null>(null);
  const [optionalUpdate, setOptionalUpdate] = useState<string | null>(null);
  const [optionalJournal, setOptionalJournal] = useState<string | null>(null);
  const [sourceTab, setSourceTab] = useState<"canonical" | "installed">(
    "canonical",
  );
  useEffect(() => {
    setSkillSource(null);
    setSourceTab("canonical");
  }, [selected?.name]);
  async function loadSkillSource() {
    if (!selected || p.demo) return;
    try {
      setSkillSource(await api.skillSource(selected.name));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  const skills = (p.boot?.skills.entries ?? []).filter((skill) =>
    pretty(skill).toLowerCase().includes(query.toLowerCase()),
  );
  const run = async () => {
    try {
      setError("");
      const names = {
        audit: "skills.audit",
        plan: "skills.update-plan",
        diff: "skills.diff",
        apply: "skills.apply",
        verify: "skills.verify",
        rollback: "skills.rollback",
      };
      const payload = ["diff", "apply"].includes(operation)
        ? { plan_id: planId, plan_sha256: planHash, confirmed }
        : ["verify", "rollback"].includes(operation)
          ? { journal_id: journalId, confirmed }
          : {};
      const response = await p.command(names[operation], payload);
      setResult(response);
      const newPlan = response.plan ?? response;
      if (newPlan.plan_id ?? newPlan.id) {
        setPlanId(newPlan.plan_id ?? newPlan.id);
        setPlanHash(
          newPlan.plan_sha256 ?? newPlan.sha256 ?? newPlan.digest ?? "",
        );
      }
      if (response.journal_id ?? response.journal?.id)
        setJournalId(response.journal_id ?? response.journal.id);
    } catch (e) {
      setError((e as Error).message);
    }
  };
  return (
    <div className="page-content skills-view">
      <PageHeading
        eyebrow={p.t("competence")}
        title={p.t("skillLibrary")}
        description={p.t("auditHelp")}
        action={
          <div className="constructor-actions">
            <Button
              icon={Boxes}
              disabled={!p.selected || p.demo}
              onClick={() => {
                setConstruction("agent");
                setConstructionGoal("");
              }}
            >
              {p.t("createSpecialist")}
            </Button>
            <Button
              tone="primary"
              icon={Braces}
              disabled={!p.selected || p.demo}
              onClick={() => {
                setConstruction("skill");
                setConstructionGoal("");
              }}
            >
              {p.t("createSkill")}
            </Button>
          </div>
        }
      />
      <div className="skill-workspace">
        <Panel title={p.t("inventory")} icon={Braces} className="skill-library">
          <div className="skill-search">
            <Search size={16} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={p.t("skillSearch")}
              aria-label={p.t("skillSearch")}
            />
            <kbd>⌘ K</kbd>
          </div>
          <div className="skill-list">
            {skills.map((skill, index) => (
              <button
                key={skill.id ?? skill.path ?? index}
                className={selected === skill ? "is-selected" : ""}
                onClick={() => {
                  setSelected(skill);
                  p.inspect({
                    title: text(skill.display_name ?? skill.name),
                    kind: "skill",
                    data: skill,
                  });
                }}
              >
                <span className="skill-symbol">
                  <Braces size={18} strokeWidth={1.4} />
                </span>
                <span>
                  <strong>{text(skill.display_name ?? skill.name)}</strong>
                  <small>{text(skill.description, p.t("noDescription"))}</small>
                  <span className="skill-meta">
                    <code>
                      {p.t("source")} · {text(skill.version, "—")}
                    </code>
                    <span>{text(skill.scope ?? skill.source_kind)}</span>
                    {skill.installation_status && (
                      <Status
                        value={
                          skill.installation_status === "primary_matches"
                            ? "observed"
                            : skill.installation_status === "primary_differs"
                              ? "needs_review"
                              : "not_observed"
                        }
                        label={
                          skill.installation_status === "primary_matches"
                            ? p.t("matched")
                            : skill.installation_status === "primary_differs"
                              ? p.t("diff")
                              : p.t("notTested")
                        }
                      />
                    )}
                  </span>
                </span>
                <ChevronRight size={14} />
              </button>
            ))}
            {!skills.length && <Empty compact title={p.t("noSkills")} />}
          </div>
        </Panel>
        <div className="skill-tools">
          <Panel
            title={
              selected
                ? text(selected.display_name ?? selected.name)
                : p.t("selectedSource")
            }
            icon={FileCode2}
          >
            {selected ? (
              <div className="panel-padding">
                <p className="skill-description">
                  {text(selected.description)}
                </p>
                <Button
                  tone="primary"
                  icon={Workflow}
                  disabled={!p.selected || p.demo}
                  onClick={() =>
                    p.newTask({ selected_skills: [selected.name] })
                  }
                >
                  {p.t("useSkill")}
                </Button>
                {["atelier-orchestrator", "codex-agents-maintenance"].includes(
                  selected.name,
                ) && (
                  <Button
                    icon={GitCompareArrows}
                    disabled={p.demo || Boolean(p.busy)}
                    onClick={() => {
                      setOptionalJournal(null);
                      setOptionalUpdate(selected.name);
                    }}
                  >
                    {p.t("reviewOptionalUpdate")}
                  </Button>
                )}
                <RecordDetails value={selected} t={p.t} />
                <Button
                  small
                  icon={Braces}
                  onClick={() => p.expand(text(selected.name), selected)}
                >
                  {p.t("showRaw")}
                </Button>
                <Button
                  small
                  icon={FileCode2}
                  disabled={p.demo}
                  onClick={() => void loadSkillSource()}
                >
                  {p.t("readSource")}
                </Button>
                {skillSource && (
                  <div className="skill-source-editor">
                    <div className="console-tabs">
                      <button
                        className={sourceTab === "canonical" ? "is-active" : ""}
                        onClick={() => setSourceTab("canonical")}
                      >
                        {p.t("source")}
                      </button>
                      <button
                        className={sourceTab === "installed" ? "is-active" : ""}
                        onClick={() => setSourceTab("installed")}
                        disabled={!skillSource.installed}
                      >
                        {p.t("installed")}
                      </button>
                      <Status
                        value={
                          skillSource.primary_equal ? "pass" : "needs_review"
                        }
                        label={
                          skillSource.primary_equal
                            ? p.t("matched")
                            : p.t("diff")
                        }
                      />
                    </div>
                    <CodeViewer
                      value={skillSource[sourceTab]?.content ?? {}}
                      fileName={`${selected.name}/SKILL.md`}
                      language="markdown"
                      locale={p.locale}
                    />
                  </div>
                )}
              </div>
            ) : (
              <Empty compact icon={Braces} title={p.t("noSelection")}>
                {p.t("noSelectionHelp")}
              </Empty>
            )}
          </Panel>
          {rows(p.boot?.optional_updates).length > 0 && (
            <Panel title={p.t("commandReceipt")} icon={ShieldCheck}>
              <div className="optional-journal-list">
                {rows(p.boot?.optional_updates)
                  .slice(-10)
                  .reverse()
                  .map((journal) => (
                    <div key={journal.id}>
                      <span>
                        <strong>{journal.name}</strong>
                        <small>{journal.id}</small>
                      </span>
                      <Status value={journal.status} />
                      <Button
                        small
                        icon={ShieldCheck}
                        disabled={Boolean(p.busy) || p.demo}
                        onClick={() => {
                          setOptionalJournal(journal.id);
                          setOptionalUpdate(journal.name);
                        }}
                      >
                        {p.t("verify")}
                      </Button>
                    </div>
                  ))}
              </div>
            </Panel>
          )}
          <Panel title={p.t("operations")} icon={GitCompareArrows}>
            <div className="operation-selector">
              {(
                [
                  "audit",
                  "plan",
                  "diff",
                  "apply",
                  "verify",
                  "rollback",
                ] as const
              ).map((op) => (
                <button
                  key={op}
                  className={operation === op ? "is-active" : ""}
                  onClick={() => {
                    setOperation(op);
                    setConfirmed(false);
                  }}
                >
                  <span>
                    {p.t(
                      (
                        {
                          plan: "updatePlan",
                          audit: "audit",
                          diff: "diff",
                          apply: "apply",
                          verify: "verify",
                          rollback: "rollback",
                        } as const
                      )[op],
                    )}
                  </span>
                </button>
              ))}
            </div>
            <div className="panel-padding">
              <p className="muted">
                {["audit", "plan"].includes(operation)
                  ? p.t("auditHelp")
                  : p.t("updateHelp")}
              </p>
              {["diff", "apply"].includes(operation) && (
                <>
                  <Field label="Plan ID">
                    <input
                      value={planId}
                      onChange={(e) => setPlanId(e.target.value)}
                      spellCheck={false}
                    />
                  </Field>
                  {operation === "apply" && (
                    <Field label={p.t("sourceDigest")}>
                      <input
                        value={planHash}
                        onChange={(e) => setPlanHash(e.target.value)}
                        spellCheck={false}
                      />
                    </Field>
                  )}
                </>
              )}
              {["verify", "rollback"].includes(operation) && (
                <Field label="Journal ID">
                  <input
                    value={journalId}
                    onChange={(e) => setJournalId(e.target.value)}
                    spellCheck={false}
                  />
                </Field>
              )}
              {["apply", "rollback"].includes(operation) && (
                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={confirmed}
                    onChange={(e) => setConfirmed(e.target.checked)}
                  />
                  <span>{p.t("confirmExactScope")}</span>
                </label>
              )}
              <Button
                tone={
                  ["apply", "rollback"].includes(operation)
                    ? "danger"
                    : "primary"
                }
                icon={operation === "rollback" ? Archive : ShieldCheck}
                disabled={
                  p.demo ||
                  Boolean(p.busy) ||
                  (["apply", "rollback"].includes(operation) && !confirmed) ||
                  (["diff", "apply"].includes(operation) && !planId) ||
                  (operation === "apply" && !planHash) ||
                  (["verify", "rollback"].includes(operation) && !journalId)
                }
                onClick={() => void run()}
              >
                {p.busy
                  ? p.t("processing")
                  : p.t(
                      (
                        {
                          plan: "updatePlan",
                          audit: "audit",
                          diff: "diff",
                          apply: "apply",
                          verify: "verify",
                          rollback: "rollback",
                        } as const
                      )[operation],
                    )}
              </Button>
              {error && <SurfaceNotice tone="error">{error}</SurfaceNotice>}
              {result && (
                <Disclosure title={p.t("commandReceipt")} initialOpen>
                  <CodeViewer
                    value={result}
                    fileName="updater-receipt.json"
                    locale={p.locale}
                  />
                </Disclosure>
              )}
            </div>
          </Panel>
        </div>
      </div>
      {optionalUpdate && (
        <OptionalUpdateDialog
          {...p}
          name={optionalUpdate}
          journalId={optionalJournal}
          onClose={() => setOptionalUpdate(null)}
        />
      )}
      {construction && (
        <Modal
          title={p.t(
            construction === "agent" ? "createSpecialist" : "createSkill",
          )}
          onClose={() => setConstruction(null)}
          footer={
            <>
              <Button onClick={() => setConstruction(null)}>
                {p.t("cancel")}
              </Button>
              <Button
                tone="primary"
                icon={Workflow}
                disabled={constructionGoal.trim().length < 8}
                onClick={() => {
                  p.newTask({
                    objective: `${p.t(construction === "agent" ? "createSpecialist" : "createSkill")}: ${constructionGoal}\n\n${p.t("planningOnly")}`,
                    acceptance: p.t("planningAcceptance"),
                    selected_skills: [
                      construction === "agent"
                        ? "agent-foundry"
                        : "design-specialist-skills",
                    ],
                    planning_only: true,
                  });
                  setConstruction(null);
                }}
              >
                {p.t("prepareTask")}
              </Button>
            </>
          }
        >
          <SurfaceNotice>{p.t("planningOnly")}</SurfaceNotice>
          <Field label={p.t("objective")}>
            <textarea
              autoFocus
              rows={5}
              value={constructionGoal}
              onChange={(event) => setConstructionGoal(event.target.value)}
              placeholder={p.t("objectivePlaceholder")}
            />
          </Field>
        </Modal>
      )}
    </div>
  );
}

function OptionalUpdateDialog(
  p: ViewProps & {
    name: string;
    journalId?: string | null;
    onClose: () => void;
  },
) {
  const [preview, setPreview] = useState<Data | null>(null);
  const [receipt, setReceipt] = useState<Data | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [rollbackConfirmed, setRollbackConfirmed] = useState(false);
  const [error, setError] = useState("");
  const [catalog, setCatalog] = useState<Data | null>(null);
  const journal = receipt?.id;
  async function run(operation: string, payload: Data) {
    setError("");
    try {
      const result = await p.command(operation, payload);
      if (operation === "skills.optional-preview") {
        setPreview(result);
        setConfirmed(false);
        setReceipt(null);
      } else {
        setReceipt(result);
        setRollbackConfirmed(false);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    if (p.journalId)
      void run("skills.optional-verify", { journal_id: p.journalId });
    else void run("skills.optional-preview", { name: p.name });
  }, [p.name, p.journalId]);
  return (
    <Modal
      title={`${p.t("reviewOptionalUpdate")} · ${p.name}`}
      onClose={p.onClose}
      footer={
        <>
          <Button onClick={p.onClose}>{p.t("close")}</Button>
          {!receipt && preview && (
            <Button
              tone="primary"
              disabled={
                p.demo || Boolean(p.busy) || !preview.ready || !confirmed
              }
              onClick={() =>
                void run("skills.optional-apply", {
                  preview_id: preview.preview_id,
                  sha256: preview.sha256,
                  confirmed: true,
                })
              }
            >
              {p.t("applyOptionalUpdate")}
            </Button>
          )}
        </>
      }
    >
      <SurfaceNotice>{p.t("optionalUpdateHelp")}</SurfaceNotice>
      {error && <SurfaceNotice tone="error">{error}</SurfaceNotice>}
      {!preview && !receipt && !error && (
        <p className="muted">{p.t("loading")}</p>
      )}
      {preview && (
        <div className="optional-update-preview">
          <div className="optional-version-pair">
            <span>
              <small>{p.t("installed")}</small>
              <strong>{preview.installed_version ?? p.t("notTested")}</strong>
            </span>
            <ArrowRight size={18} />
            <span>
              <small>{p.t("candidateVersion")}</small>
              <strong>{preview.candidate_version}</strong>
            </span>
            <Status
              value={preview.ready ? "pass" : "blocked"}
              label={
                preview.noop
                  ? p.t("matched")
                  : preview.ready
                    ? p.t("ready")
                    : p.t("needsAttention")
              }
            />
          </div>
          <Field label={p.t("source")}>
            <code className="optional-source-path">{preview.source_root}</code>
          </Field>
          <Field label={p.t("targetSourcePaths")}>
            <code className="optional-source-path">{preview.target_root}</code>
          </Field>
          <Field label={p.t("sourceDigest")}>
            <code className="optional-source-path">
              {preview.source_sha256}
            </code>
          </Field>
          <p className="muted">{p.t("optionalPreservation")}</p>
          <Disclosure
            title={`${p.t("optionalChangedFiles")} · ${preview.changes?.length ?? 0}`}
            initialOpen
          >
            <div className="optional-file-list">
              {rows(preview.changes).map((item) => (
                <div key={item.path}>
                  <Status
                    value={item.change}
                    label={p.t(
                      item.change === "added"
                        ? "optionalFileAdded"
                        : item.change === "removed"
                          ? "optionalFileRemoved"
                          : "optionalFileChanged",
                    )}
                  />
                  <code>{item.path}</code>
                </div>
              ))}
            </div>
          </Disclosure>
          {rows(preview.conflicts).length > 0 && (
            <SurfaceNotice tone="warning">
              <strong>{p.t("optionalLocalConflict")}</strong>
              {rows(preview.conflicts).map((item, index) => (
                <p key={index}>{text(item.value ?? item)}</p>
              ))}
            </SurfaceNotice>
          )}
          <Disclosure title={p.t("optionalExactPreview")}>
            <CodeViewer
              value={preview}
              fileName="optional-source-preview.json"
              locale={p.locale}
            />
          </Disclosure>
          {!receipt && (
            <label className="confirmation-check">
              <input
                type="checkbox"
                checked={confirmed}
                disabled={!preview.ready || Boolean(p.busy)}
                onChange={(e) => setConfirmed(e.target.checked)}
              />
              <span>{p.t("confirmOptionalUpdate")}</span>
            </label>
          )}
        </div>
      )}
      {receipt && (
        <div className="optional-update-result">
          <SurfaceNotice
            tone={receipt.installed_source_verified ? "good" : "warning"}
          >
            {receipt.installed_source_verified
              ? p.t("optionalSourceVerified")
              : p.t("optionalReviewReceipt")}
          </SurfaceNotice>
          <div className="heading-actions">
            {journal && (
              <Button
                disabled={Boolean(p.busy)}
                icon={ShieldCheck}
                onClick={() =>
                  void run("skills.optional-verify", { journal_id: journal })
                }
              >
                {p.t("verify")}
              </Button>
            )}
            <Button
              disabled={Boolean(p.busy)}
              icon={RefreshCw}
              onClick={() => {
                setError("");
                void p
                  .command("codex.skills")
                  .then(setCatalog)
                  .catch((e) => setError(e.message));
              }}
            >
              {p.t("refreshHostCatalog")}
            </Button>
          </div>
          {catalog && (
            <SurfaceNotice>
              {p.t("hostCatalogRead")}{" "}
              <button
                className="text-button"
                onClick={() => p.expand(p.t("inventory"), catalog)}
              >
                {p.t("showRaw")}
              </button>
            </SurfaceNotice>
          )}
          <Disclosure title={p.t("commandReceipt")}>
            <CodeViewer
              value={receipt}
              fileName="optional-source-receipt.json"
              locale={p.locale}
            />
          </Disclosure>
          {journal && receipt.status !== "rolled_back" && (
            <Disclosure title={p.t("rollback")}>
              <p className="muted">{p.t("optionalRollbackHelp")}</p>
              <label className="confirmation-check">
                <input
                  type="checkbox"
                  checked={rollbackConfirmed}
                  onChange={(e) => setRollbackConfirmed(e.target.checked)}
                  disabled={!receipt.current_sha256}
                />
                <span>{p.t("confirmOptionalRollback")}</span>
              </label>
              <Button
                tone="danger"
                disabled={
                  Boolean(p.busy) ||
                  !rollbackConfirmed ||
                  !receipt.current_sha256
                }
                onClick={() =>
                  void run("skills.optional-rollback", {
                    journal_id: journal,
                    current_sha256: receipt.current_sha256,
                    confirmed: true,
                  })
                }
              >
                {p.t("rollback")}
              </Button>
            </Disclosure>
          )}
        </div>
      )}
    </Modal>
  );
}

export function SystemView(
  p: ViewProps & {
    section: "settings" | "integrations";
    changeLocale: (locale: Locale) => Promise<void>;
  },
) {
  const [doctor, setDoctor] = useState<Data | null>(null);
  const [backup, setBackup] = useState<Data | null>(null);
  const [backupId, setBackupId] = useState("");
  const [digest, setDigest] = useState("");
  const [preview, setPreview] = useState<Data | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState("");
  const [stopReviewed, setStopReviewed] = useState(false);
  async function diagnose() {
    try {
      setDoctor(await api.doctor());
      setError("");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    if (!p.demo) void diagnose();
  }, [p.demo]);
  async function runBackup() {
    try {
      const result = await p.command("service.backup");
      setBackup(result);
      setBackupId(result.backup_id ?? result.id);
      setDigest(result.sha256 ?? result.digest ?? "");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function runRestorePreview() {
    try {
      const result = await p.command("service.restore-preview", {
        backup_id: backupId,
      });
      setPreview(result);
      if (result.sha256) setDigest(result.sha256);
      setConfirmed(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function runRestore() {
    try {
      const result = await p.command("service.restore", {
        backup_id: backupId,
        sha256: digest,
        confirmed,
      });
      setPreview(result);
      setConfirmed(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <div className="page-content system-view">
      <PageHeading
        eyebrow={p.t("local")}
        title={p.t(p.section === "settings" ? "settings" : "integrations")}
        description={p.t(p.section === "settings" ? "aboutHelp" : "healthHelp")}
        action={
          <Button
            icon={RefreshCw}
            onClick={() => void diagnose()}
            disabled={p.demo}
          >
            {p.t("runDoctor")}
          </Button>
        }
      />
      <div className="system-grid">
        <Panel title={p.t("codex")} icon={TerminalSquare}>
          <div className="connection-card">
            <div className="connection-card__symbol">
              <TerminalSquare size={31} strokeWidth={1.25} />
            </div>
            <div>
              <h2>Codex</h2>
              <Status
                value={p.boot?.capabilities.codex?.status ?? "not_connected"}
              />
              <p>
                {text(
                  p.boot?.capabilities.codex?.message ??
                    p.boot?.capabilities.codex?.reason,
                  p.t("noExecution"),
                )}
              </p>
            </div>
          </div>
          <div className="panel-padding">
            <RecordDetails
              value={p.boot?.capabilities.codex ?? { status: "not_observed" }}
              t={p.t}
            />
            <Button
              icon={Radio}
              disabled={p.demo || Boolean(p.busy)}
              onClick={() =>
                void p
                  .command("codex.connect")
                  .then((result) =>
                    p.inspect({
                      title: "Codex",
                      kind: "capability",
                      data: result,
                    }),
                  )
                  .catch(() => {})
              }
            >
              {p.t("probe")}
            </Button>
          </div>
        </Panel>
        <Panel title="WORK" icon={Cable}>
          <div className="connection-card">
            <div className="connection-card__symbol is-deferred">
              <Cable size={31} strokeWidth={1.25} />
            </div>
            <div>
              <h2>WORK</h2>
              <Status value="deferred" label={p.t("workDeferred")} />
              <p>{p.t("workDeferred")}</p>
            </div>
          </div>
          <div className="panel-padding">
            <SurfaceNotice>{p.t("displayOnly")}</SurfaceNotice>
          </div>
        </Panel>
      </div>
      <div className="settings-grid">
        <Panel title={p.t("doctor")} icon={ShieldCheck}>
          {doctor ? (
            <div className="panel-padding">
              <DoctorResult value={doctor} {...p} />
            </div>
          ) : (
            <Empty compact icon={ShieldCheck} title={p.t("notTested")}>
              {p.t("healthHelp")}
            </Empty>
          )}
        </Panel>
        <Panel title={p.t("retention")} icon={Archive}>
          <div className="panel-padding">
            <p className="muted">{p.t("restoreHelp")}</p>
            <Button
              icon={Archive}
              onClick={() => void runBackup()}
              disabled={p.demo || Boolean(p.busy)}
            >
              {p.t("backup")}
            </Button>
            {backup && (
              <div className="backup-receipt">
                <Check size={15} />
                <code>{shortHash(backup.backup_id ?? backup.id)}</code>
                <span>{shortHash(backup.sha256)}</span>
              </div>
            )}
            <div className="form-divider" />
            <Field label="Backup ID">
              <input
                value={backupId}
                onChange={(e) => {
                  setBackupId(e.target.value);
                  setPreview(null);
                }}
                spellCheck={false}
              />
            </Field>
            <Button
              small
              icon={Search}
              onClick={() => void runRestorePreview()}
              disabled={!backupId || p.demo || Boolean(p.busy)}
            >
              {p.t("restorePreview")}
            </Button>
            {preview && (
              <>
                <Disclosure title={p.t("restorePreviewReady")} initialOpen>
                  <CodeViewer
                    value={preview}
                    fileName="restore-preview.json"
                    locale={p.locale}
                  />
                </Disclosure>
                <label className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={confirmed}
                    onChange={(e) => setConfirmed(e.target.checked)}
                  />
                  <span>{p.t("confirmExactScope")}</span>
                </label>
                <Button
                  tone="danger"
                  icon={Archive}
                  disabled={!confirmed || !digest || p.demo || Boolean(p.busy)}
                  onClick={() => void runRestore()}
                >
                  {p.t("restoreApply")}
                </Button>
              </>
            )}
          </div>
        </Panel>
      </div>
      {p.section === "settings" && <PrivacySettings {...p} />}
      {p.section === "settings" && (
        <div className="settings-grid">
          <Panel title={p.t("language")} icon={Globe2}>
            <div className="panel-padding">
              <p className="muted">{p.t("languageHelp")}</p>
              <div className="locale-options">
                {(Object.keys(localeNames) as Locale[])
                  .filter((locale) => Boolean(catalogs[locale]))
                  .map((locale) => (
                    <button
                      key={locale}
                      className={p.locale === locale ? "is-selected" : ""}
                      onClick={() => void p.changeLocale(locale)}
                    >
                      <span>{localeNames[locale]}</span>
                      {p.locale === locale && <Check size={15} />}
                    </button>
                  ))}
              </div>
            </div>
          </Panel>
          <Panel title={p.t("dataOwnership")} icon={Database}>
            <div className="data-ownership">
              <div>
                <FolderGit2 size={20} />
                <span>
                  <strong>{p.t("nativeFiles")}</strong>
                  <small>{p.t("sourceTruth")}</small>
                </span>
              </div>
              <div>
                <Database size={20} />
                <span>
                  <strong>{p.t("serviceStore")}</strong>
                  <small>{p.t("privateLocal")}</small>
                </span>
              </div>
              <SurfaceNotice>{p.t("noBackgroundPromise")}</SurfaceNotice>
            </div>
          </Panel>
        </div>
      )}
      {p.section === "settings" && (
        <Panel title={p.t("localServer")} icon={TerminalSquare}>
          <div className="panel-padding">
            <RecordDetails
              value={{
                version: p.boot?.version,
                instance: p.boot?.instance_id,
                status: p.demo ? "example_only" : "observed",
              }}
              t={p.t}
            />
            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={stopReviewed}
                onChange={(event) => setStopReviewed(event.target.checked)}
              />
              <span>
                {p.t("stopService")} · {p.t("noBackgroundPromise")}
              </span>
            </label>
            <Button
              tone="danger"
              icon={Pause}
              disabled={!stopReviewed || p.demo || Boolean(p.busy)}
              onClick={() => void p.command("service.stop").catch(() => {})}
            >
              {p.t("stopService")}
            </Button>
          </div>
        </Panel>
      )}
      {error && <SurfaceNotice tone="error">{error}</SurfaceNotice>}
    </div>
  );
}

function Welcome(p: ViewProps & { compact?: boolean }) {
  return (
    <div className={`welcome ${p.compact ? "welcome--compact" : ""}`}>
      <div className="welcome-copy">
        <span className="eyebrow">{p.t("welcome")}</span>
        <h1>{p.t("firstTitle")}</h1>
        <p>{p.t("firstDescription")}</p>
        <div>
          <Button
            tone="primary"
            icon={Plus}
            onClick={p.connectProject}
            disabled={p.demo}
          >
            {p.t("connectProject")}
          </Button>
          <a className="button button--quiet" href="?demo=1">
            <Layers3 size={16} />
            {p.t("exploreDemo")}
            <ArrowRight size={14} />
          </a>
        </div>
      </div>
      <div className="welcome-system">
        <div className="welcome-system__aura" />
        <div className="welcome-system__core">
          <Boxes size={45} strokeWidth={1.1} />
          <strong>Agent Atelier</strong>
          <span>{p.t("local")}</span>
        </div>
        <div className="welcome-node welcome-node--source">
          <FileCode2 size={17} />
          <span>{p.t("source")}</span>
        </div>
        <div className="welcome-node welcome-node--contract">
          <ListChecks size={17} />
          <span>{p.t("contract")}</span>
        </div>
        <div className="welcome-node welcome-node--execution">
          <Workflow size={17} />
          <span>{p.t("execution")}</span>
        </div>
        <div className="welcome-node welcome-node--evidence">
          <ShieldCheck size={17} />
          <span>{p.t("evidence")}</span>
        </div>
        <svg className="welcome-lines" viewBox="0 0 460 320" aria-hidden="true">
          <path d="M70 90C130 90 160 130 230 160S330 230 390 230M70 230C140 230 165 180 230 160S330 90 390 90" />
        </svg>
      </div>
      <div className="welcome-steps">
        {(["firstStep1", "firstStep2", "firstStep3"] as const).map(
          (key, index) => (
            <div key={key}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>{p.t(key)}</strong>
                <p>{p.t(`${key}Body` as MessageKey)}</p>
              </div>
            </div>
          ),
        )}
      </div>
    </div>
  );
}

function Topology({
  sources,
  taskCount,
  t,
  projectName,
  onSelect,
}: {
  sources: Data[];
  taskCount: number;
  t: T;
  projectName: string;
  onSelect: (source: Data) => void;
}) {
  return (
    <div className="source-map">
      <div className="source-map-heading">
        <Fingerprint size={18} />
        <strong>{projectName}</strong>
        <span>
          {sources.length} {t("sources")} · {taskCount} {t("jobs")}
        </span>
      </div>
      {sources.length ? (
        <div className="source-map-nodes">
          {sources.map((source, index) => (
            <button
              key={source.path ?? source.id ?? index}
              onClick={() => onSelect(source)}
            >
              <FileCode2 size={15} />
              <span>
                <strong>{text(source.name ?? source.path ?? source.id)}</strong>
                <small>{shortHash(source.sha256 ?? source.revision)}</small>
              </span>
              <ChevronRight size={12} />
            </button>
          ))}
        </div>
      ) : (
        <Empty compact icon={Network} title={t("noRecords")}>
          <p>{t("noWorkReadHelp")}</p>
        </Empty>
      )}
      <div className="topology-caption">
        <span className="status__dot" />
        {t("sourceRelationships")}
      </div>
    </div>
  );
}

function WorkspaceDirection(p: ViewProps) {
  const [controllerOpen, setControllerOpen] = useState(false);
  const { goal, next, agents } = workspaceDirection(
    p.workspace,
    p.selected?.id,
  );
  const jobs = observedJobCounts(p.workspace?.jobs);
  const trail = contextTrail(p.workspace);
  const currentDecision = trail.explicitlyCurrent
    ? trail.decisions[0]
    : undefined;
  return (
    <>
      <div className="workspace-direction">
        <div
          className={`workspace-goal ${goal?.status === "accepted" ? "is-accepted" : ""}`}
        >
          <span className="target-label">
            <ShieldCheck size={14} />
            {goalLabel(goal, p.t)}
          </span>
          <strong>{goal?.text || p.t("goalUnknownHelp")}</strong>
          {goal?.source_ref && (
            <button
              onClick={() =>
                p.inspect({
                  title: p.t("targetSource"),
                  kind: "goal",
                  data: goal,
                  sourcePath: goal.source_ref,
                })
              }
            >
              <FileText size={11} />
              <span>{goal.source_ref}</span>
              <code>{shortHash(goal.source_sha256)}</code>
            </button>
          )}
          {currentDecision && (
            <button
              className="workspace-current-decision"
              onClick={() =>
                p.inspect({
                  title: p.t("currentDecisions"),
                  kind: "decision",
                  data: currentDecision,
                  sourcePath:
                    currentDecision.source_ref ?? currentDecision.source_path,
                })
              }
            >
              <GitPullRequest size={14} />
              <span>
                <small>{p.t("currentDecisions")}</small>
                <strong>
                  {text(
                    currentDecision.summary ??
                      currentDecision.text ??
                      currentDecision.title ??
                      currentDecision.id,
                    p.t("noDescription"),
                  )}
                </strong>
                <code>
                  {text(
                    currentDecision.source_ref ??
                      currentDecision.source_path ??
                      currentDecision.id,
                  )}
                </code>
              </span>
              <ArrowRight size={12} />
            </button>
          )}
          <div className="workspace-context-bar">
            <ContextSignal
              workspace={p.workspace}
              t={p.t}
              onOpen={() => p.navigate("context")}
            />
            <div className="workspace-source-counters">
              <button onClick={() => p.navigate("context")}>
                <FileText size={13} />
                <strong>{p.workspace?.sources?.length ?? 0}</strong>
                <span>{p.t("sourcesCount")}</span>
              </button>
              <button onClick={() => p.navigate("requirements")}>
                <ListChecks size={13} />
                <strong>{p.workspace?.requirements?.length ?? 0}</strong>
                <span>{p.t("mustCount")}</span>
              </button>
              <button onClick={() => p.navigate("jobs")}>
                <Activity size={13} />
                <strong>{jobs.active}</strong>
                <span>{p.t("activeWork")}</span>
              </button>
            </div>
          </div>
        </div>
        <div className="workspace-direction-next">
          <span className="eyebrow">{p.t("nextStep")}</span>
          <p>{nextActionText(next[0], p.t)}</p>
          <Button
            small
            icon={ArrowRight}
            tone="primary"
            onClick={() =>
              p.newTask({
                universal_entry: true,
                objective: next[0] ? nextActionText(next[0], p.t) : "",
              })
            }
            disabled={Boolean(p.busy)}
          >
            {p.t("continueWithOrchestrator")}
          </Button>
          {agents.length > 0 && (
            <div className="workspace-agent-hint">
              <Braces size={12} />
              <span>
                {agents
                  .map(
                    (item: Data) =>
                      `${item.name} · ${item.availability === "installed" ? p.t("installed") : item.availability === "planned" ? p.t("plannedAgent") : p.t("notTested")}`,
                  )
                  .join(" / ")}
              </span>
            </div>
          )}
          <button
            className="native-controller-link"
            onClick={() => setControllerOpen(true)}
          >
            <Braces size={12} />
            {p.t("nativeAgentWorkflow")}
            <ChevronRight size={11} />
          </button>
        </div>
      </div>
      {controllerOpen && p.selected && (
        <NativeControllerDialog
          {...p}
          project={p.selected}
          onClose={() => setControllerOpen(false)}
        />
      )}
    </>
  );
}

function NativeControllerDialog(
  p: ViewProps & { project: Project; onClose: () => void },
) {
  const [operation, setOperation] = useState("context");
  const [sessionPath, setSessionPath] = useState(".");
  const [recordPath, setRecordPath] = useState("");
  const [projectSlug, setProjectSlug] = useState("");
  const [ownerText, setOwnerText] = useState("");
  const [preview, setPreview] = useState<Data | null>(null);
  const [receipt, setReceipt] = useState<Data | null>(null);
  const [reviewed, setReviewed] = useState(false);
  const [error, setError] = useState("");
  const [reconciliation, setReconciliation] = useState<Data | null>(null);
  const [reconcileReviewed, setReconcileReviewed] = useState(false);
  const labels = {
    context: "controllerContext",
    check: "controllerCheck",
    "build-gate": "controllerGate",
    init: "controllerInit",
    blueprint: "controllerBlueprint",
    approve: "controllerApprove",
  } as const;
  async function prepare() {
    setError("");
    try {
      const value = await p.command(
        "controller.preview",
        {
          controller: "foundry",
          session_path: sessionPath,
          operation,
          ...(recordPath.trim() ? { record_path: recordPath.trim() } : {}),
          ...(operation === "approve"
            ? { owner_approval_text: ownerText.trim() }
            : {}),
          params:
            operation === "init"
              ? { project_id: projectSlug.trim(), purpose: "factory" }
              : {},
        },
        p.project,
      );
      setPreview(value);
      setReviewed(false);
      setReceipt(null);
    } catch (error) {
      setError((error as Error).message);
    }
  }
  async function apply() {
    if (!preview) return;
    setError("");
    try {
      const value = await p.command(
        "controller.apply",
        {
          preview_id: preview.preview_id,
          sha256: preview.sha256,
          confirmed: reviewed,
        },
        p.project,
      );
      setReceipt(value);
      setPreview(null);
      setReviewed(false);
    } catch (error) {
      setError((error as Error).message);
    }
  }
  async function reconcile(confirm = false) {
    if (!receipt?.id) return;
    setError("");
    try {
      const value = await p.command(
        "controller.reconcile",
        {
          receipt_id: receipt.id,
          ...(confirm && reconciliation
            ? { sha256: reconciliation.sha256, confirmed: reconcileReviewed }
            : {}),
        },
        p.project,
      );
      if (confirm) {
        setReceipt(value);
        setReconciliation(null);
      } else {
        setReconciliation(value);
        setReconcileReviewed(false);
      }
    } catch (error) {
      setError((error as Error).message);
    }
  }
  return (
    <Modal
      wide
      title={p.t("nativeAgentWorkflow")}
      onClose={p.onClose}
      footer={
        <>
          <Button onClick={p.onClose}>{p.t("close")}</Button>
          {preview ? (
            <Button
              tone="primary"
              icon={Check}
              disabled={!reviewed || Boolean(p.busy)}
              onClick={() => void apply()}
            >
              {p.t("applyControllerPreview")}
            </Button>
          ) : !receipt ? (
            <Button
              tone="primary"
              icon={ShieldCheck}
              disabled={
                Boolean(p.busy) ||
                !sessionPath.trim() ||
                (operation === "blueprint" && !recordPath.trim()) ||
                (operation === "approve" && !ownerText.trim()) ||
                (operation === "init" && !projectSlug.trim())
              }
              onClick={() => void prepare()}
            >
              {p.t("reviewControllerAction")}
            </Button>
          ) : null}
        </>
      }
    >
      <p className="dialog-lead">{p.t("nativeControllerHelp")}</p>
      {!preview && !receipt && (
        <>
          <div className="form-grid">
            <Field label={p.t("nativeControllerAction")}>
              <select
                value={operation}
                onChange={(event) => {
                  setOperation(event.target.value);
                  setRecordPath("");
                }}
              >
                {Object.entries(labels).map(([value, key]) => (
                  <option key={value} value={value}>
                    {p.t(key)}
                  </option>
                ))}
              </select>
            </Field>
            <Field
              label={p.t("factorySessionPath")}
              help={p.t("factorySessionPathHelp")}
            >
              <input
                value={sessionPath}
                onChange={(event) => setSessionPath(event.target.value)}
                spellCheck={false}
              />
            </Field>
          </div>
          {operation === "init" && (
            <Field label={p.t("nativeProjectId")}>
              <input
                value={projectSlug}
                onChange={(event) => setProjectSlug(event.target.value)}
                placeholder="my-agent"
                spellCheck={false}
              />
            </Field>
          )}
          {operation === "blueprint" && (
            <Field
              label={p.t("passportRecordPath")}
              help={p.t("passportRecordPathHelp")}
            >
              <input
                value={recordPath}
                onChange={(event) => setRecordPath(event.target.value)}
                placeholder="records/blueprint.json"
                spellCheck={false}
              />
            </Field>
          )}
          {operation === "approve" && (
            <Field
              label={p.t("ownerApprovalText")}
              help={p.t("ownerApprovalTextHelp")}
            >
              <textarea
                rows={3}
                value={ownerText}
                onChange={(event) => setOwnerText(event.target.value)}
              />
            </Field>
          )}
        </>
      )}
      {preview && (
        <>
          <div className="controller-subject">
            <span className="eyebrow">{p.t("exactControllerSubject")}</span>
            <h3>
              {preview.subject?.goal ||
                p.t(labels[operation as keyof typeof labels])}
            </h3>
            <Field label={p.t("projectName")}>
              <strong>{p.project.name}</strong>
            </Field>
            <Field label={p.t("projectRoot")}>
              <code className="optional-source-path">{preview.root}</code>
            </Field>
            <Field label={p.t("factorySessionPath")}>
              <code className="optional-source-path">
                {preview.session_path === "."
                  ? preview.root
                  : `${preview.root}/${preview.session_path}`}
              </code>
            </Field>
            {preview.operation === "init" && (
              <div className="form-grid">
                <Field label={p.t("nativeProjectId")}>
                  <code>{preview.params?.project_id}</code>
                </Field>
                <Field label={p.t("scope")}>
                  <code>{preview.params?.purpose ?? "factory"}</code>
                </Field>
              </div>
            )}
            <Field label={p.t("sourceDigest")}>
              <code className="optional-source-path">
                {preview.controller_source_sha256}
              </code>
            </Field>
            <RecordDetails
              value={
                preview.subject ?? {
                  operation: preview.operation,
                  session: preview.session_path,
                  native_revision: preview.native_revision,
                  native_state_sha256: preview.native_state_sha256,
                }
              }
              t={p.t}
              compact
            />
            <Disclosure title={p.t("exactPlan")}>
              <CodeViewer
                value={preview}
                fileName="native-controller-preview.json"
                locale={p.locale}
              />
            </Disclosure>
          </div>
          <SurfaceNotice>{p.t("controllerEffectsHelp")}</SurfaceNotice>
          {preview.record && (
            <Disclosure title={p.t("request")}>
              <CodeViewer
                value={preview.record}
                fileName="reviewed-record.json"
                locale={p.locale}
              />
            </Disclosure>
          )}
          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={reviewed}
              onChange={(event) => setReviewed(event.target.checked)}
            />
            <span>{p.t("confirmControllerAction")}</span>
          </label>
          <Button
            small
            tone="quiet"
            onClick={() => {
              setPreview(null);
              setReviewed(false);
            }}
          >
            {p.t("back")}
          </Button>
        </>
      )}
      {receipt && (
        <>
          <Status value={receipt.status} />
          <CodeViewer
            value={receipt.result ?? receipt}
            fileName="native-controller-receipt.json"
            locale={p.locale}
          />
          <SurfaceNotice>{p.t("controllerReceiptHelp")}</SurfaceNotice>
          {receipt.status === "outcome_unknown" ? (
            <>
              <Button
                small
                icon={RefreshCw}
                onClick={() => void reconcile(false)}
                disabled={Boolean(p.busy)}
              >
                {p.t("reconcileControllerState")}
              </Button>
              {reconciliation && (
                <>
                  <RecordDetails value={reconciliation} t={p.t} />
                  <label className="checkbox-field">
                    <input
                      type="checkbox"
                      checked={reconcileReviewed}
                      onChange={(event) =>
                        setReconcileReviewed(event.target.checked)
                      }
                    />
                    <span>{p.t("confirmControllerReconcile")}</span>
                  </label>
                  <Button
                    small
                    disabled={!reconcileReviewed || Boolean(p.busy)}
                    onClick={() => void reconcile(true)}
                  >
                    {p.t("recordReconciliation")}
                  </Button>
                </>
              )}
            </>
          ) : (
            <Button
              small
              onClick={() => {
                setReceipt(null);
                setError("");
              }}
            >
              {p.t("nextActions")}
            </Button>
          )}
        </>
      )}
      {error && (
        <p className="dialog-error" role="alert">
          {error}
        </p>
      )}
    </Modal>
  );
}

function ContractDiff({ t }: { t: T }) {
  return (
    <div className="contract-diff">
      <div className="diff-header">
        <GitCompareArrows size={14} />
        <span>shipment-api.yaml</span>
        <span>v1.3.0 → proposal</span>
      </div>
      <div className="diff-context">
        <code>16</code>
        <pre>properties:</pre>
      </div>
      <div className="diff-context">
        <code>17</code>
        <pre> orderId: {"{ type: string }"}</pre>
      </div>
      <div className="diff-line diff-line--remove">
        <code>18 −</code>
        <pre> weight: {"{ type: string }"}</pre>
      </div>
      <div className="diff-line diff-line--add">
        <code>18 +</code>
        <pre> weight: {"{ type: number }"}</pre>
      </div>
      <div className="diff-context">
        <code>19</code>
        <pre> cargoType: {"{ type: string }"}</pre>
      </div>
      <div className="diff-summary">
        <span>−1</span>
        <span>+1</span>
        <p>
          {t("exampleOnly")} · {t("sampleRecommendation")}
        </p>
      </div>
    </div>
  );
}
function RecordList(p: ViewProps & { entries: Data[]; kind: string }) {
  return (
    <div className="record-list">
      {p.entries.length ? (
        p.entries.map((record, index) => (
          <button
            key={record.id ?? record.path ?? index}
            onClick={() =>
              p.inspect({
                title: text(
                  record.title ?? record.name ?? record.id ?? record.path,
                ),
                kind: p.kind,
                data: record,
                sourcePath: record.path,
              })
            }
          >
            <span className="record-list__icon">
              {p.kind === "job" ? (
                <Workflow size={16} />
              ) : p.kind === "decision" ? (
                <GitPullRequest size={16} />
              ) : (
                <FileText size={16} />
              )}
            </span>
            <span>
              <strong>
                {text(
                  record.title ??
                    record.name ??
                    record.objective ??
                    record.id ??
                    record.path,
                )}
              </strong>
              <small>
                {text(
                  record.description ??
                    record.summary ??
                    record.source ??
                    record.scope,
                  "",
                )}
              </small>
            </span>
            <Status value={record.status ?? "source_only"} />
            <ChevronRight size={13} />
          </button>
        ))
      ) : (
        <Empty compact title={p.t("noRecords")} />
      )}
    </div>
  );
}
function ActivityList(p: ViewProps & { items: Data[] }) {
  return (
    <div className="activity-list">
      {p.items.length ? (
        p.items.slice(0, 12).map((event, index) => (
          <button
            key={event.id ?? index}
            onClick={() =>
              p.inspect({
                title: text(
                  event.title ?? event.operation ?? event.type ?? event.event,
                ),
                kind: "activity",
                data: event,
              })
            }
          >
            <span className="activity-marker">
              <Circle size={7} fill="currentColor" />
            </span>
            <span>
              <strong>
                {text(
                  event.title ?? event.operation ?? event.type ?? event.event,
                )}
              </strong>
              <small>
                {text(
                  event.message ??
                    event.summary ??
                    event.status ??
                    event.data?.project_id ??
                    event.data?.task_id,
                  "",
                )}
              </small>
              <time>
                {formatTime(event.created_at ?? event.timestamp, p.locale)}
              </time>
            </span>
          </button>
        ))
      ) : (
        <Empty compact icon={Activity} title={p.t("noRecords")}>
          {p.t("noBackgroundPromise")}
        </Empty>
      )}
    </div>
  );
}
function DoctorResult(p: ViewProps & { value: Data }) {
  const checks = rows(p.value.checks ?? p.value.results ?? p.value);
  return (
    <div className="doctor-results">
      {checks.map((check, index) => (
        <button
          key={check.id ?? check.name ?? index}
          onClick={() =>
            p.inspect({
              title: text(check.name ?? check.id),
              kind: "diagnosis",
              data: check,
            })
          }
        >
          <ShieldCheck size={17} />
          <span>
            <strong>{text(check.name ?? check.id)}</strong>
            <small>
              {text(
                check.message ?? check.reason ?? check.summary ?? check.value,
                "",
              )}
            </small>
          </span>
          <Status
            value={
              check.status ??
              (check.ok === true
                ? "pass"
                : check.ok === false
                  ? "fail"
                  : "not_observed")
            }
          />
        </button>
      ))}
    </div>
  );
}
function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}
function SectionHeading({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof Boxes;
  title: string;
  description: string;
}) {
  return (
    <header className="section-heading">
      <span>
        <Icon size={21} strokeWidth={1.4} />
      </span>
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </header>
  );
}
function Metric({
  icon: Icon,
  value,
  label,
}: {
  icon: typeof Boxes;
  value: number;
  label: string;
}) {
  return (
    <div className="metric">
      <span>
        <Icon size={18} strokeWidth={1.4} />
      </span>
      <strong>{value.toLocaleString()}</strong>
      <small>{label}</small>
    </div>
  );
}
function ProductSymbol({ kind }: { kind: string }) {
  return kind === "game" ? (
    <Sparkles size={17} />
  ) : kind === "chatbot" ? (
    <Cable size={17} />
  ) : kind === "research" ? (
    <Network size={17} />
  ) : kind === "document" ? (
    <FileText size={17} />
  ) : (
    <Boxes size={17} />
  );
}
function FileSymbol({ name }: { name: string }) {
  return /\.(png|jpe?g|webp|svg)$/i.test(name) ? (
    <FileImage size={18} />
  ) : /\.(mp3|wav|ogg)$/i.test(name) ? (
    <AudioLines size={18} />
  ) : (
    <FileCode2 size={18} />
  );
}
function readinessRows(value: unknown): Data[] {
  const records = rows(value);
  return records.length
    ? records
    : ["source", "code", "integration", "device", "owner_acceptance"].map(
        (name) => ({ id: name, name, status: "not_observed" }),
      );
}
function axisLabel(axis: Data, t: T) {
  const map: Record<string, MessageKey> = {
    source: "sourceReview",
    code: "code",
    integration: "integration",
    independent_review: "independentReview",
    owner_acceptance: "ownerAcceptance",
    device: "device",
    runtime: "execution",
    human: "ownerAcceptance",
  };
  const id = axis.name ?? axis.id ?? axis.axis;
  return map[id] ? t(map[id]) : text(axis.label ?? id);
}
function formatTime(value: unknown, locale: string): string {
  if (!value) return "—";
  const date = new Date(String(value));
  return Number.isNaN(date.valueOf())
    ? text(value)
    : new Intl.DateTimeFormat(locale, {
        hour: "2-digit",
        minute: "2-digit",
        day: "2-digit",
        month: "short",
      }).format(date);
}
