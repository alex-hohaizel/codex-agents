import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Archive,
  ArrowRight,
  BookOpen,
  Boxes,
  Braces,
  Cable,
  Check,
  ChevronRight,
  CircleHelp,
  FileCode2,
  FileStack,
  FolderOpen,
  Layers3,
  ListChecks,
  Menu,
  Network,
  PanelRightClose,
  PanelRightOpen,
  Plus,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Workflow,
  X,
} from "lucide-react";
import {
  api,
  ApiError,
  mergePortfolioPage,
  shortHash,
  text,
  type Bootstrap,
  type Data,
  type Project,
  type Workspace,
} from "./api";
import {
  catalogs,
  LocaleContext,
  localeNames,
  translate,
  type Locale,
  type MessageKey,
} from "./i18n";
import { demoBootstrap, demoWorkspace } from "./demo";
import { profileDefinitions, profileLabel, projectProfile } from "./profiles";
import {
  recoveredWorkspaceError,
  workspaceReadState,
  workspaceDirection,
} from "./workbench";
import {
  Button,
  CodeViewer,
  Empty,
  IconButton,
  Modal,
  RecordDetails,
  Status,
  SurfaceNotice,
  type T,
} from "./ui";
import { BindingDialog, TaskDialog, SearchDialog } from "./dialogs";
import {
  Portfolio,
  nextActionText,
  WorkspaceView,
  ContextView,
  RequirementsView,
  IdentityView,
  EvidenceView,
  ArtifactsView,
  JobsView,
  SkillsView,
  SystemView,
} from "./views";

export type View =
  | "overview"
  | "workspace"
  | "context"
  | "requirements"
  | "identity"
  | "artifacts"
  | "evidence"
  | "jobs"
  | "skills"
  | "integrations"
  | "settings";
export type Inspection = {
  title: string;
  kind: string;
  data: Data;
  sourcePath?: string;
  projectRoot?: string;
};
export type CommandFn = (
  operation: string,
  payload?: Data,
  project?: Project,
) => Promise<Data>;

const projectIcons: Record<string, typeof Boxes> = {
  app: Boxes,
  application: Boxes,
  chatbot: Cable,
  bot: Cable,
  game: Sparkles,
  research: Network,
  document: BookOpen,
  generic: Layers3,
  agent: Braces,
  mixed: Layers3,
};

export default function App() {
  const initialQuery = useMemo(
    () => new URLSearchParams(window.location.search),
    [],
  );
  const [demo, setDemo] = useState(initialQuery.get("demo") === "1");
  const [locale, setLocale] = useState<Locale>(
    (initialQuery.get("locale") as Locale) || "uk",
  );
  const [live, setLive] = useState<Bootstrap | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [projectId, setProjectId] = useState(initialQuery.get("project") || "");
  const [view, setView] = useState<View>(
    initialQuery.get("project") ? "workspace" : "overview",
  );
  const [portfolio, setPortfolio] = useState<Data | null>(null);
  const [nativeDetailState, setNativeDetail] = useState<Data | null>(null);
  const [nativeHistoryLoading, setNativeHistoryLoading] = useState(false);
  const [nativeHistoryError, setNativeHistoryError] = useState("");
  const nativeIdentityRef = useRef("");
  const nativeMoreRef = useRef(false);
  const portfolioSnapshotRef = useRef<string | undefined>(undefined);
  portfolioSnapshotRef.current = portfolio?.checked_at;
  const [bindingRoot, setBindingRoot] = useState("");
  const [loading, setLoading] = useState(true);
  const [workspaceLoading, setWorkspaceLoading] = useState(false);
  const [workspaceReadAttempt, setWorkspaceReadAttempt] = useState(0);
  const workspaceReadError = useRef<{
    projectId: string;
    error: ApiError;
  } | null>(null);
  const [connectionError, setConnectionError] = useState<ApiError | null>(null);
  const [actionError, setActionError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState("");
  const [binding, setBinding] = useState(false);
  const [taskOpen, setTaskOpen] = useState(false);
  const [taskPreset, setTaskPreset] = useState<Data | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const navigationRef = useRef<HTMLElement | null>(null);
  const [inspectorOpen, setInspectorOpen] = useState(window.innerWidth >= 1170);
  const [inspectorTab, setInspectorTab] = useState<
    "details" | "provenance" | "recovery"
  >("details");
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [expanded, setExpanded] = useState<{
    title: string;
    value: unknown;
  } | null>(null);
  const [receipt, setReceipt] = useState<Data | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const t = useCallback((key: MessageKey) => translate(locale, key), [locale]);

  const boot = demo ? demoBootstrap : live;
  const projects = boot?.projects ?? [];
  const bindingProject = projects.find((p) => p.id === projectId) ?? null;
  const selected =
    bindingProject && workspace?.project?.id === bindingProject.id
      ? {
          ...bindingProject,
          ...workspace.project,
          view_profile:
            bindingProject.view_profile ?? workspace.project.view_profile,
        }
      : bindingProject;
  const selectedProfile = projectProfile(selected);
  const nativeDiscovery = portfolio?.projects?.find(
    (item: Data) =>
      item.binding_id === projectId || item.root === selected?.root,
  );
  const nativeIdentity = `${demo}:${projectId}:${nativeDiscovery?.id ?? ""}:${portfolio?.checked_at ?? ""}`;
  nativeIdentityRef.current = nativeIdentity;
  const nativeDetail =
    nativeDetailState?.project?.id === nativeDiscovery?.id &&
    nativeDetailState?.coverage?.snapshot_checked_at === portfolio?.checked_at
      ? nativeDetailState
      : null;
  const ProjectIcon = projectIcons[selectedProfile] ?? Layers3;
  const inspectedProject =
    inspection?.kind === "project" && typeof inspection.data?.root === "string"
      ? inspection.data
      : inspection?.projectRoot
        ? (portfolio?.projects?.find(
            (project: Data) => project.root === inspection.projectRoot,
          ) ??
          projects.find((project) => project.root === inspection.projectRoot))
        : null;
  const contextProject =
    view === "overview" && inspectedProject ? inspectedProject : selected;
  const contextRevision =
    contextProject?.revision ?? contextProject?.source_revision;
  const inspectorProject = inspectedProject
    ? (projects.find((project) => project.root === inspectedProject.root) ??
      null)
    : selected;
  const inspectorDirection =
    workspace?.project?.id === inspectorProject?.id
      ? workspaceDirection(workspace, inspectorProject?.id)
      : null;
  const inspectorGoal = inspectorDirection
    ? inspectorDirection.goal
    : nativeDetail?.goal;
  const inspectorNextActions =
    inspectorDirection?.next ??
    (inspectedProject
      ? (inspectedProject.next_actions ??
        (inspectedProject.root === selected?.root
          ? nativeDetail?.next_actions
          : []))
      : nativeDetail?.next_actions);

  const refresh = useCallback(
    async (quiet = false) => {
      if (demo) {
        setLoading(false);
        return;
      }
      if (!quiet) setLoading(true);
      try {
        const data = await api.bootstrap();
        setLive(data);
        try {
          setPortfolio(await api.portfolio());
        } catch {
          /* preserve the last observed catalog */
        }
        setConnectionError(null);
        if (!initialQuery.get("locale") && data.locale && !live)
          setLocale(data.locale as Locale);
        setProjectId((current) =>
          current && data.projects.some((p) => p.id === current)
            ? current
            : (data.projects[0]?.id ?? ""),
        );
      } catch (error) {
        setConnectionError(asError(error));
      } finally {
        setLoading(false);
      }
    },
    [demo, initialQuery, Boolean(live)],
  );

  useEffect(() => {
    const identity = nativeIdentity;
    nativeMoreRef.current = false;
    setNativeHistoryError("");
    if (demo || !nativeDiscovery) {
      setNativeDetail(null);
      setNativeHistoryLoading(false);
      return;
    }
    let cancelled = false;
    setNativeDetail(null);
    setNativeHistoryLoading(true);
    api
      .portfolioProject(nativeDiscovery.id, {
        snapshot_checked_at: portfolio?.checked_at,
      })
      .then((result) => {
        if (!cancelled && nativeIdentityRef.current === identity) {
          setNativeDetail(mergePortfolioPage(null, result));
          void observePortfolio();
        }
      })
      .catch((error) => {
        if (!cancelled && nativeIdentityRef.current === identity)
          setNativeHistoryError(asError(error).message);
      })
      .finally(() => {
        if (!cancelled && nativeIdentityRef.current === identity)
          setNativeHistoryLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [nativeIdentity]);
  async function loadMoreNativeHistory(itemCursor?: Data) {
    const offset = nativeDetail?.coverage?.next_thread_offset;
    if (
      !nativeDiscovery ||
      !nativeDetail ||
      (!itemCursor && !Number.isInteger(offset)) ||
      (itemCursor &&
        !nativeDetail.coverage?.item_cursors?.some(
          (item: Data) =>
            item.thread_id === itemCursor.thread_id &&
            typeof item.next_cursor === "string" &&
            item.next_cursor === itemCursor.next_cursor,
        )) ||
      nativeMoreRef.current
    )
      return;
    const identity = nativeIdentity;
    nativeMoreRef.current = true;
    setNativeHistoryLoading(true);
    setNativeHistoryError("");
    try {
      const page = await api.portfolioProject(nativeDiscovery.id, {
        ...(itemCursor
          ? {
              item_thread_id: itemCursor.thread_id,
              item_cursor: itemCursor.next_cursor,
            }
          : { thread_offset: offset }),
        snapshot_checked_at: nativeDetail.coverage.snapshot_checked_at,
      });
      if (nativeIdentityRef.current === identity) {
        setNativeDetail(mergePortfolioPage(nativeDetail, page));
        void observePortfolio();
      }
    } catch (error) {
      if (nativeIdentityRef.current === identity)
        setNativeHistoryError(asError(error).message);
    } finally {
      if (nativeIdentityRef.current === identity) {
        nativeMoreRef.current = false;
        setNativeHistoryLoading(false);
      }
    }
  }
  async function observePortfolio() {
    const snapshot = portfolioSnapshotRef.current;
    try {
      const observed = await api.portfolio();
      if (
        snapshot === portfolioSnapshotRef.current &&
        observed.checked_at === snapshot
      )
        setPortfolio(observed);
    } catch {
      /* Preserve the current catalog if the observation cannot be refreshed. */
    }
  }
  useEffect(() => {
    void refresh();
  }, [demo]);
  useEffect(() => {
    const claimLauncher = () => {
      if (
        new URLSearchParams(window.location.hash.slice(1)).has("atelier_launch")
      )
        void refresh();
    };
    window.addEventListener("hashchange", claimLauncher);
    return () => window.removeEventListener("hashchange", claimLauncher);
  }, [refresh]);
  useEffect(() => {
    if (demo) {
      setProjectId((current) =>
        demoBootstrap.projects.some((p) => p.id === current)
          ? current
          : demoBootstrap.projects[0].id,
      );
      setLoading(false);
    }
  }, [demo]);
  useEffect(() => {
    if (!selected) {
      setWorkspace(null);
      setWorkspaceLoading(false);
      return;
    }
    let cancelled = false;
    if (demo) {
      setWorkspace(demoWorkspace(selected.id));
      setWorkspaceLoading(false);
      return;
    }
    setWorkspaceLoading(true);
    setWorkspace(null);
    api
      .workspace(selected.id)
      .then((data) => {
        if (!cancelled) {
          setWorkspace(data);
          const recoveredFailure = workspaceReadError.current;
          setActionError((current) =>
            recoveredWorkspaceError(current, recoveredFailure, data.project.id),
          );
          if (recoveredFailure?.projectId === data.project.id)
            workspaceReadError.current = null;
          setInspection(null);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          const readError = asError(error);
          workspaceReadError.current = {
            projectId: selected.id,
            error: readError,
          };
          setActionError(readError);
        }
      })
      .finally(() => {
        if (!cancelled) setWorkspaceLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, demo, bindingProject?.revision, workspaceReadAttempt]);
  useEffect(() => {
    if (demo) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const events = new EventSource("/api/v1/events");
    const update = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        void refresh(true);
        if (projectId)
          api
            .workspace(projectId)
            .then(setWorkspace)
            .catch(() => {});
      }, 250);
    };
    events.onmessage = update;
    events.addEventListener("change", update);
    events.addEventListener("job", update);
    events.addEventListener("activity", update);
    events.addEventListener("update", update);
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") update();
    }, 6000);
    return () => {
      events.close();
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [demo, projectId]);
  useEffect(() => {
    let previous = window.innerWidth;
    const resize = () => {
      const current = window.innerWidth;
      if (previous >= 1170 && current < 1170) setInspectorOpen(false);
      if (current > 760) setMobileNav(false);
      previous = current;
    };
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);
  useEffect(() => {
    if (!mobileNav) return;
    const previous =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    const rail = navigationRef.current;
    const focusable = () =>
      Array.from(
        rail?.querySelectorAll<HTMLElement>(
          'button:not(:disabled), a[href], select:not(:disabled), input:not(:disabled), [tabindex="0"]',
        ) ?? [],
      ).filter((element) => element.getClientRects().length > 0);
    const frame = requestAnimationFrame(() => focusable()[0]?.focus());
    const keydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setMobileNav(false);
      } else if (event.key === "Tab") {
        const items = focusable();
        const first = items[0],
          last = items.at(-1);
        if (
          event.shiftKey &&
          (document.activeElement === first ||
            !rail?.contains(document.activeElement))
        ) {
          event.preventDefault();
          last?.focus();
        } else if (
          !event.shiftKey &&
          (document.activeElement === last ||
            !rail?.contains(document.activeElement))
        ) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    window.addEventListener("keydown", keydown);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("keydown", keydown);
      if (previous?.isConnected && previous.getClientRects().length)
        previous.focus();
    };
  }, [mobileNav]);
  useEffect(() => {
    document.documentElement.lang = locale;
    document.title = `${contextProject?.name ? `${contextProject.name} · ` : ""}Agent Atelier`;
  }, [locale, contextProject?.name]);
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setMobileNav(false);
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(null), 5000);
    return () => clearTimeout(timer);
  }, [notice]);

  const command: CommandFn = async (operation, payload = {}, project) => {
    if (demo) throw new ApiError(t("disabledInDemo"), "EXAMPLE_ONLY");
    if (!live) throw new ApiError(t("connectionNeeded"), "HOST_DISCONNECTED");
    if (
      receipt?.status === "outcome_unknown" &&
      receipt.operation === operation &&
      receipt.project_id === project?.id
    )
      throw new ApiError(t("restoreUnknown"), "OUTCOME_UNKNOWN");
    setBusy(operation);
    setActionError(null);
    try {
      const result = await api.command(
        operation,
        payload,
        live.csrf_token,
        project,
      );
      setReceipt(result);
      if (result.status === "failed")
        throw new ApiError(
          result.error?.message ?? t("commandFailed"),
          result.error?.code,
          result.error?.details,
        );
      await refresh(true);
      if (operation === "portfolio.refresh")
        setPortfolio(result.result ?? result);
      if (project) {
        try {
          setWorkspace(await api.workspace(project.id));
        } catch {
          /* retain the last observed workspace */
        }
      }
      return result.result ?? result;
    } catch (error) {
      const e = asError(error);
      if (
        e.code === "COMMAND_OUTCOME_UNKNOWN" &&
        e.details &&
        typeof e.details === "object"
      )
        setReceipt({ ...e.details, status: "outcome_unknown" });
      setActionError(e);
      throw e;
    } finally {
      setBusy("");
    }
  };

  function navigate(next: View) {
    setView(next);
    setMobileNav(false);
  }
  function openTask(preset?: Data) {
    setTaskPreset(preset ?? null);
    setTaskOpen(true);
  }
  function inspect(next: Inspection) {
    const root =
      next.kind === "project" && typeof next.data?.root === "string"
        ? next.data.root
        : view === "overview"
          ? (inspection?.projectRoot ?? inspectedProject?.root)
          : selected?.root;
    if (next.kind === "project" && root) {
      const binding = projects.find((project) => project.root === root);
      if (binding) setProjectId(binding.id);
    }
    setInspection({ ...next, ...(root ? { projectRoot: root } : {}) });
    setInspectorTab("details");
    setInspectorOpen(true);
  }
  function selectProject(id: string) {
    setProjectId(id);
    setInspection(null);
    setMobileNav(false);
    setView("workspace");
  }
  function toggleDemo(value: boolean) {
    setDemo(value);
    setInspection(null);
    setReceipt(null);
    setActionError(null);
    setView("workspace");
    const url = new URL(window.location.href);
    value ? url.searchParams.set("demo", "1") : url.searchParams.delete("demo");
    url.searchParams.delete("project");
    window.history.replaceState({}, "", url);
  }
  async function changeLocale(value: Locale) {
    setLocale(value);
    if (!demo && live) {
      try {
        await command("service.settings", { locale: value });
      } catch {
        /* the local view still reflects the selected locale */
      }
    }
  }

  const workspaceState = workspaceReadState(
    workspace,
    selected?.id,
    workspaceLoading,
  );
  const needsWorkspace =
    Boolean(selected) &&
    [
      "workspace",
      "context",
      "requirements",
      "identity",
      "artifacts",
      "evidence",
      "jobs",
    ].includes(view);
  const shared = {
    t,
    locale,
    demo,
    selected,
    workspace: workspaceState === "ready" ? workspace : null,
    boot,
    portfolio,
    nativeDetail,
    nativeHistoryLoading,
    nativeHistoryError,
    loadMoreNativeHistory,
    observePortfolio,
    busy,
    command,
    inspect,
    expand: (title: string, value: unknown) => setExpanded({ title, value }),
    selectProject,
    connectProject: () => setBinding(true),
    connectDiscovered: (root: string) => {
      setBindingRoot(root);
      setBinding(true);
    },
    newTask: openTask,
    navigate,
  };
  const mainViews: { id: View; key: MessageKey; icon: typeof Boxes }[] = [
    { id: "overview", key: "products", icon: Boxes },
    { id: "workspace", key: "operations", icon: Workflow },
    { id: "skills", key: "agents", icon: Braces },
    { id: "jobs", key: "jobs", icon: Activity },
    { id: "integrations", key: "integrations", icon: Cable },
    { id: "settings", key: "settings", icon: Settings2 },
  ];
  const projectViews: { id: View; key: MessageKey; icon: typeof Boxes }[] = [
    { id: "workspace", key: "overview", icon: Layers3 },
    { id: "context", key: "context", icon: Network },
    { id: "requirements", key: "requirements", icon: ListChecks },
    { id: "identity", key: "identity", icon: Sparkles },
    { id: "artifacts", key: "artifacts", icon: FileStack },
    { id: "evidence", key: "evidence", icon: ShieldCheck },
  ];
  projectViews.sort(
    (a, b) =>
      profileDefinitions[selectedProfile].order.indexOf(a.id) -
      profileDefinitions[selectedProfile].order.indexOf(b.id),
  );
  const globalView = [
    "overview",
    "skills",
    "jobs",
    "integrations",
    "settings",
  ].includes(view);
  const viewTitle =
    (
      mainViews.find((v) => v.id === view) ??
      projectViews.find((v) => v.id === view)
    )?.key ?? "workspace";

  return (
    <LocaleContext.Provider value={locale}>
      <div
        className={`atelier-shell ${mobileNav ? "nav-open" : ""} ${inspectorOpen ? "" : "inspector-hidden"} ${demo ? "is-demo" : ""}`}
      >
        <a className="skip-link" href="#main-content">
          {t("workspace")}
        </a>
        {demo && (
          <div className="demo-strip">
            <span>
              <span className="demo-strip__dot" />
              {t("demoBanner")}
            </span>
            <button onClick={() => toggleDemo(false)}>
              {t("exitDemo")}
              <ArrowRight size={13} />
            </button>
          </div>
        )}
        <header className="platform-bar">
          <div className="brand-group">
            <IconButton
              icon={Menu}
              label={t("menu")}
              className="mobile-menu"
              aria-expanded={mobileNav}
              aria-controls="project-navigation-drawer"
              onClick={() => setMobileNav(!mobileNav)}
            />
            <button
              className="brand"
              onClick={() => navigate("overview")}
              aria-label="Agent Atelier"
            >
              <span className="brand-mark">
                <Boxes size={26} strokeWidth={1.3} />
              </span>
              <span>
                Agent <strong>Atelier</strong>
                <small>{t("platform")}</small>
              </span>
            </button>
          </div>
          <nav className="platform-navigation" aria-label={t("platform")}>
            {mainViews.map((item) => (
              <button
                key={item.id}
                data-view={item.id}
                aria-current={
                  view === item.id || (item.id === "workspace" && !globalView)
                    ? "page"
                    : undefined
                }
                onClick={() => navigate(item.id)}
              >
                <item.icon size={15} strokeWidth={1.7} />
                <span>{t(item.key)}</span>
                {item.id === "jobs" &&
                  (boot?.jobs.filter((j) =>
                    ["running", "queued", "awaiting_approval"].includes(
                      j.status,
                    ),
                  ).length ?? 0) > 0 && (
                    <i className="nav-count">
                      {
                        boot?.jobs.filter((j) =>
                          ["running", "queued", "awaiting_approval"].includes(
                            j.status,
                          ),
                        ).length
                      }
                    </i>
                  )}
              </button>
            ))}
          </nav>
          <div className="platform-tools">
            <IconButton
              icon={Search}
              label={t("search")}
              onClick={() => setSearchOpen(true)}
            />
            <select
              className="locale-select"
              aria-label={t("language")}
              value={locale}
              onChange={(e) => void changeLocale(e.target.value as Locale)}
            >
              {(Object.keys(localeNames) as Locale[])
                .filter((l) => Boolean(catalogs[l]))
                .map((l) => (
                  <option key={l} value={l}>
                    {l === "zh-CN" ? "中文" : l.toUpperCase()}
                  </option>
                ))}
            </select>
            <span className="owner-avatar" title={t("personal")}>
              O
            </span>
          </div>
        </header>

        {mobileNav && (
          <button
            className="navigation-scrim"
            aria-label={t("close")}
            tabIndex={-1}
            onClick={() => setMobileNav(false)}
          />
        )}
        <aside
          className="navigation-rail"
          id="project-navigation-drawer"
          ref={navigationRef}
          role={mobileNav ? "dialog" : undefined}
          aria-modal={mobileNav || undefined}
          aria-label={t("workspace")}
        >
          <div className="rail-heading">
            <span className="workspace-orb">
              <Layers3 size={18} />
            </span>
            <div>
              <strong>{t("personal")}</strong>
              <small>{t("local")}</small>
            </div>
            <span
              className={`connection-dot ${live && !connectionError ? "is-connected" : ""}`}
              title={
                live && !connectionError ? t("connected") : t("notConnected")
              }
            />
            <IconButton
              className="rail-close"
              icon={X}
              label={t("close")}
              onClick={() => setMobileNav(false)}
            />
          </div>
          <nav className="rail-global-navigation" aria-label={t("platform")}>
            {mainViews.map((item) => (
              <button
                key={item.id}
                data-view={item.id}
                aria-current={
                  view === item.id || (item.id === "workspace" && !globalView)
                    ? "page"
                    : undefined
                }
                onClick={() => navigate(item.id)}
              >
                <item.icon size={16} strokeWidth={1.7} />
                <span>{t(item.key)}</span>
                {view === item.id && <ChevronRight size={13} />}
              </button>
            ))}
          </nav>
          <div className="rail-section-title">
            <span>{t("products")}</span>
            <button
              aria-label={t("connectProject")}
              onClick={() => {
                setMobileNav(false);
                setBinding(true);
              }}
              disabled={demo}
            >
              <Plus size={14} />
            </button>
          </div>
          <div className="project-list">
            {projects.map((project) => {
              const Icon = projectIcons[project.kind] ?? Layers3;
              return (
                <button
                  key={project.id}
                  className={
                    contextProject?.root === project.root ? "is-selected" : ""
                  }
                  onClick={() => selectProject(project.id)}
                >
                  <span
                    className={`project-icon project-icon--${project.kind}`}
                  >
                    <Icon size={16} strokeWidth={1.5} />
                  </span>
                  <span>
                    <strong>{project.name}</strong>
                    <small>{project.kind}</small>
                  </span>
                  {contextProject?.root === project.root && (
                    <ChevronRight size={13} />
                  )}
                </button>
              );
            })}
            {!projects.length && (
              <button
                className="connect-inline"
                onClick={() => {
                  setMobileNav(false);
                  setBinding(true);
                }}
              >
                <Plus size={16} />
                <span>{t("connectProject")}</span>
              </button>
            )}
          </div>
          <div className="rail-divider" />
          <div className="rail-section-title">{t("workspace")}</div>
          <nav className="project-navigation" aria-label={t("workspace")}>
            {projectViews.map((item) => (
              <button
                key={item.id}
                data-view={item.id}
                aria-current={view === item.id ? "page" : undefined}
                className={view === item.id ? "is-active" : ""}
                onClick={() => navigate(item.id)}
              >
                <item.icon size={15} strokeWidth={1.6} />
                <span>{t(item.key)}</span>
                {item.id === "requirements" &&
                  Boolean(workspace?.requirements.length) && (
                    <small>{workspace?.requirements.length}</small>
                  )}
              </button>
            ))}
          </nav>
          <div className="rail-bottom">
            <button onClick={() => navigate("integrations")}>
              <span className="host-symbol">
                <TerminalSquare size={15} />
              </span>
              <span>
                <strong>Codex</strong>
                <small>
                  {demo
                    ? t("exampleOnly")
                    : text(boot?.capabilities.codex?.status, t("notConnected"))}
                </small>
              </span>
              <span
                className={`connection-dot ${boot?.capabilities.codex?.status === "ready" ? "is-connected" : ""}`}
              />
            </button>
            <button onClick={() => navigate("settings")}>
              <CircleHelp size={15} />
              <span>{t("documentation")}</span>
              <ChevronRight size={13} />
            </button>
            <div className="privacy-note">
              <ShieldCheck size={12} />
              {t("privateLocal")}
              <span>v{boot?.version ?? "—"}</span>
            </div>
          </div>
        </aside>

        <div className="main-region">
          <div className="workspace-toolbar">
            <div className="breadcrumbs">
              <button onClick={() => navigate("overview")}>
                {t("products")}
              </button>
              <ChevronRight size={11} />
              <span>{contextProject?.name ?? t("personal")}</span>
              <ChevronRight size={11} />
              <strong>{t(viewTitle)}</strong>
            </div>
            <div className="toolbar-actions">
              <span className="local-signal">
                <span />
                {demo ? t("demo") : t("liveState")}
              </span>
              <IconButton
                icon={RefreshCw}
                label={t("refresh")}
                onClick={() =>
                  portfolio?.checked_at && !demo
                    ? void command("portfolio.refresh", {
                        max_pages: 20,
                      }).catch(() => {})
                    : void refresh()
                }
                disabled={loading || Boolean(busy)}
              />
              <IconButton
                icon={inspectorOpen ? PanelRightClose : PanelRightOpen}
                label={t("inspector")}
                onClick={() => setInspectorOpen(!inspectorOpen)}
              />
            </div>
          </div>
          <main
            id="main-content"
            tabIndex={-1}
            data-current-view={view}
            data-workspace-state={workspaceState}
            aria-busy={needsWorkspace && workspaceState === "loading"}
          >
            {connectionError && !demo && (
              <div className="connection-warning">
                <Cable size={18} />
                <div>
                  <strong>
                    {t(
                      connectionError.code === "LAUNCH_REQUIRED"
                        ? "launcherRequired"
                        : "noNetwork",
                    )}
                  </strong>
                  <p>
                    {t(
                      connectionError.code === "LAUNCH_REQUIRED"
                        ? "launcherRequiredBody"
                        : "noNetworkBody",
                    )}
                  </p>
                  <code>{connectionError.code}</code>
                </div>
                <Button small icon={RefreshCw} onClick={() => void refresh()}>
                  {t("retry")}
                </Button>
              </div>
            )}
            {actionError && (
              <div className="action-error" role="alert">
                <ShieldCheck size={17} />
                <div>
                  <strong>{actionError.code}</strong>
                  <p>{actionError.message}</p>
                </div>
                <IconButton
                  icon={X}
                  label={t("dismiss")}
                  onClick={() => setActionError(null)}
                />
              </div>
            )}
            {loading && !boot ? (
              <Loading t={t} />
            ) : (
              <>
                {!globalView && selected && (
                  <header className="product-heading">
                    <div className="product-heading__identity">
                      <span
                        className={`product-emblem product-emblem--${selected.kind}`}
                      >
                        <ProjectIcon size={23} strokeWidth={1.3} />
                      </span>
                      <div>
                        <div className="product-heading__eyebrow">
                          <span>{t(profileLabel(selectedProfile))}</span>
                          <i />
                          <span>
                            {demo
                              ? t("exampleOnly")
                              : selected.phase &&
                                  ![
                                    "unbound",
                                    "not_recorded",
                                    "unknown",
                                  ].includes(selected.phase)
                                ? selected.phase
                                : t("sourceReview")}
                          </span>
                        </div>
                        <h1>
                          {demo && selected.id === "global-logistics"
                            ? t("sampleTitle")
                            : selected.name}
                        </h1>
                        <p>
                          {demo && selected.id === "global-logistics"
                            ? t("sampleSubtitle")
                            : selected.summary || t("aboutHelp")}
                        </p>
                      </div>
                    </div>
                    <div className="product-heading__actions">
                      <Status
                        value={
                          demo
                            ? "example_only"
                            : (selected.status ?? "source_only")
                        }
                        label={
                          demo
                            ? t("exampleOnly")
                            : text(selected.status, t("sourceOnly"))
                        }
                      />
                      <Button
                        tone="primary"
                        icon={Plus}
                        onClick={() => openTask()}
                        disabled={demo || Boolean(busy)}
                      >
                        {t("newTask")}
                      </Button>
                    </div>
                  </header>
                )}
                {workspaceLoading && (
                  <div className="thin-progress" aria-label={t("loading")} />
                )}
                {needsWorkspace && workspaceState !== "ready" ? (
                  <div className="page-content" role="status">
                    <SurfaceNotice>
                      {t(
                        workspaceState === "loading" ? "loading" : "notLoaded",
                      )}
                    </SurfaceNotice>
                    {workspaceState !== "loading" && (
                      <Button
                        icon={RefreshCw}
                        onClick={() =>
                          setWorkspaceReadAttempt((attempt) => attempt + 1)
                        }
                      >
                        {t("refresh")}
                      </Button>
                    )}
                  </div>
                ) : (
                  <>
                    {view === "overview" && <Portfolio {...shared} />}
                    {view === "workspace" && <WorkspaceView {...shared} />}
                    {view === "context" && <ContextView {...shared} />}
                    {view === "requirements" && (
                      <RequirementsView {...shared} />
                    )}
                    {view === "identity" && <IdentityView {...shared} />}
                    {view === "artifacts" && <ArtifactsView {...shared} />}
                    {view === "evidence" && <EvidenceView {...shared} />}
                    {view === "jobs" && <JobsView {...shared} />}
                    {view === "skills" && <SkillsView {...shared} />}
                    {(view === "integrations" || view === "settings") && (
                      <SystemView
                        {...shared}
                        section={view}
                        changeLocale={changeLocale}
                      />
                    )}
                  </>
                )}
              </>
            )}
          </main>
          <footer className="workspace-statusbar">
            <span>
              <span
                className={`statusbar-dot ${connectionError ? "is-error" : ""}`}
              />
              {demo
                ? t("exampleOnly")
                : live
                  ? t("connected")
                  : t("notConnected")}
            </span>
            <span>
              <FolderOpen size={12} />
              {contextProject?.name ?? t("noProject")}
            </span>
            {contextRevision && (
              <span className="statusbar-revision" title={contextRevision}>
                <GitMark />
                {shortHash(contextRevision)}
              </span>
            )}
            <button onClick={() => navigate("integrations")}>
              <ShieldCheck size={12} />
              {t("sourceTruth")}
            </button>
            <span className="statusbar-right">{t("workDeferred")}</span>
          </footer>
        </div>

        {inspectorOpen && (
          <aside className="context-inspector">
            <header>
              <div>
                <span className="eyebrow">{t("inspector")}</span>
                <h2>
                  {inspection?.title ??
                    (demo && selected?.id === "global-logistics"
                      ? t("sampleResult")
                      : (selected?.name ?? t("personal")))}
                </h2>
              </div>
              <IconButton
                icon={X}
                label={t("close")}
                onClick={() => setInspectorOpen(false)}
              />
            </header>
            <nav aria-label={t("inspector")}>
              {(["details", "provenance", "recovery"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setInspectorTab(tab)}
                  className={inspectorTab === tab ? "is-active" : ""}
                >
                  {t(tab)}
                </button>
              ))}
            </nav>
            <div className="inspector-content">
              {inspectorTab === "details" && (
                <>
                  {inspection ? (
                    <>
                      <div className="inspector-kind">
                        <span className="tag">{inspection.kind}</span>
                        <Status value={inspection.data.status} />
                      </div>
                      {inspection.data.description && (
                        <p>{text(inspection.data.description)}</p>
                      )}
                      {inspection.data.summary && (
                        <p>{text(inspection.data.summary)}</p>
                      )}
                      <RecordDetails value={inspection.data} t={t} compact />
                      <Button
                        small
                        tone="quiet"
                        icon={Braces}
                        onClick={() =>
                          setExpanded({
                            title: inspection.title,
                            value: inspection.data,
                          })
                        }
                      >
                        {t("showRaw")}
                      </Button>
                    </>
                  ) : demo && selected?.id === "global-logistics" ? (
                    <DemoInspector t={t} inspect={inspect} />
                  ) : (
                    <>
                      <div className="inspector-callout">
                        <ShieldCheck size={20} />
                        <strong>
                          {inspectorGoal?.status === "accepted"
                            ? t("acceptedTarget")
                            : t("sourceTruth")}
                        </strong>
                        <p>{inspectorGoal?.text || t("aboutHelp")}</p>
                      </div>
                      {selected ? (
                        <RecordDetails
                          value={{
                            kind: selected.kind,
                            revision: selected.revision,
                            phase: selected.phase,
                            status: selected.status,
                          }}
                          t={t}
                          compact
                        />
                      ) : (
                        <Empty compact icon={Layers3} title={t("noProject")}>
                          {t("emptyPortfolioBody")}
                        </Empty>
                      )}
                      <div className="inspector-section">
                        <h3>{t("capabilities")}</h3>
                        <CapabilityLine
                          title="Codex"
                          value={boot?.capabilities.codex?.status}
                        />
                        <CapabilityLine title="WORK" value="deferred" />
                      </div>
                    </>
                  )}
                  <div className="inspector-section">
                    <h3>{t("nextStep")}</h3>
                    {inspectorNextActions?.[0]?.text && (
                      <p className="inspector-next-copy">
                        {nextActionText(inspectorNextActions[0], t)}
                      </p>
                    )}
                    <button
                      className="inspector-action"
                      onClick={() => {
                        if (inspectorProject) {
                          setProjectId(inspectorProject.id);
                          openTask({
                            universal_entry: true,
                            objective: inspectorNextActions?.[0]
                              ? nextActionText(inspectorNextActions[0], t)
                              : "",
                          });
                        } else {
                          setBindingRoot(inspectedProject?.root ?? "");
                          setBinding(true);
                        }
                      }}
                      disabled={demo}
                    >
                      {inspectorProject
                        ? t("continueWithOrchestrator")
                        : inspectedProject
                          ? t("connectThis")
                          : t("connectProject")}
                      <ArrowRight size={15} />
                    </button>
                  </div>
                </>
              )}
              {inspectorTab === "provenance" && (
                <>
                  <div className="inspector-callout">
                    <Network size={20} />
                    <strong>{t("attachedSource")}</strong>
                    <p>{t("contextGraph")}</p>
                  </div>
                  {inspection?.sourcePath && (
                    <div className="inspector-file">
                      <FileCode2 size={15} />
                      <code>{inspection.sourcePath}</code>
                    </div>
                  )}
                  <RecordDetails
                    value={
                      inspection?.data ?? {
                        project: selected?.name,
                        root: selected?.root,
                        revision: selected?.revision,
                        instance: boot?.instance_id,
                      }
                    }
                    t={t}
                  />
                  <SurfaceNotice>
                    {demo ? t("demoBanner") : t("statePreserved")}
                  </SurfaceNotice>
                </>
              )}
              {inspectorTab === "recovery" && (
                <>
                  <div className="inspector-callout">
                    <Archive size={20} />
                    <strong>{t("recovery")}</strong>
                    <p>{t("restoreUnknown")}</p>
                  </div>
                  <ol className="recovery-list">
                    <li>
                      <span>1</span>
                      {t("checkpoint")}
                    </li>
                    <li>
                      <span>2</span>
                      {t("reconcile")}
                    </li>
                    <li>
                      <span>3</span>
                      {t("scopeReview")}
                    </li>
                    <li>
                      <span>4</span>
                      {t("continue")}
                    </li>
                  </ol>
                  <SurfaceNotice>{t("noBackgroundPromise")}</SurfaceNotice>
                  <Button
                    icon={ShieldCheck}
                    onClick={() => navigate("integrations")}
                  >
                    {t("doctor")}
                  </Button>
                </>
              )}
              {receipt && (
                <div className="inspector-section">
                  <h3>{t("lastReceipt")}</h3>
                  <button
                    className="receipt-chip"
                    onClick={() =>
                      setExpanded({
                        title: t("commandReceipt"),
                        value: receipt,
                      })
                    }
                  >
                    <Check size={14} />
                    <code>{shortHash(receipt.command_id)}</code>
                    <ChevronRight size={14} />
                  </button>
                  {receipt.status === "outcome_unknown" && (
                    <Button
                      small
                      icon={RefreshCw}
                      onClick={() =>
                        void api
                          .receipt(receipt.command_id)
                          .then((result) => {
                            setReceipt(result);
                            setActionError(null);
                          })
                          .catch((error) => setActionError(asError(error)))
                      }
                    >
                      {t("reconcile")}
                    </Button>
                  )}
                </div>
              )}
            </div>
            <footer>
              <span className="inspector-footer-mark">
                <Layers3 size={16} />
              </span>
              <p>{t("subtitle")}</p>
            </footer>
          </aside>
        )}

        {binding && (
          <BindingDialog
            initialRoot={bindingRoot}
            t={t}
            command={command}
            busy={busy}
            onClose={() => {
              setBinding(false);
              setBindingRoot("");
            }}
            onConnected={(id) => {
              setBinding(false);
              setBindingRoot("");
              selectProject(id);
            }}
          />
        )}
        {taskOpen && (
          <TaskDialog
            preset={taskPreset}
            t={t}
            selected={selected}
            projects={projects}
            onProjectSelected={(id) => setProjectId(id)}
            demo={demo}
            command={command}
            busy={busy}
            locale={locale}
            onClose={() => setTaskOpen(false)}
            onDispatched={(job) => {
              setTaskOpen(false);
              navigate("jobs");
              inspect({
                title: text(job.title ?? job.id),
                kind: "job",
                data: job,
              });
            }}
          />
        )}
        {searchOpen && (
          <SearchDialog
            t={t}
            projects={projects}
            skills={boot?.skills.entries ?? []}
            onClose={() => setSearchOpen(false)}
            selectProject={(id) => {
              selectProject(id);
              setSearchOpen(false);
            }}
            navigate={(next) => {
              navigate(next);
              setSearchOpen(false);
            }}
            inspect={(item) => {
              inspect(item);
              setSearchOpen(false);
            }}
          />
        )}
        {expanded && (
          <Modal title={expanded.title} onClose={() => setExpanded(null)} wide>
            <CodeViewer
              value={expanded.value}
              fileName={expanded.title}
              locale={locale}
            />
          </Modal>
        )}
        {notice && (
          <div className="toast" role="status">
            <Check size={16} />
            {notice}
          </div>
        )}
      </div>
    </LocaleContext.Provider>
  );
}

function CapabilityLine({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="capability-line">
      <span>{title}</span>
      <Status value={value} />
    </div>
  );
}
function Loading({ t }: { t: T }) {
  return (
    <div className="loading-workspace">
      <span className="loading-orbit">
        <Boxes size={28} />
      </span>
      <h2>{t("loading")}</h2>
      <div className="loading-lines">
        <i />
        <i />
        <i />
      </div>
    </div>
  );
}
function GitMark() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden="true"
    >
      <path d="M4 3v8m0-5h4a4 4 0 0 0 4-4" stroke="currentColor" />
      <circle cx="4" cy="3" r="1.5" stroke="currentColor" />
      <circle cx="4" cy="12" r="1.5" stroke="currentColor" />
      <circle cx="12" cy="2" r="1.5" stroke="currentColor" />
    </svg>
  );
}
function asError(error: unknown): ApiError {
  return error instanceof ApiError
    ? error
    : new ApiError(error instanceof Error ? error.message : String(error));
}
function DemoInspector({
  t,
  inspect,
}: {
  t: T;
  inspect: (value: Inspection) => void;
}) {
  return (
    <>
      <div className="finding-banner">
        <ShieldCheck size={18} />
        <span>{t("sampleResult")}</span>
      </div>
      <div className="inspector-section">
        <h3>{t("issues")}</h3>
        <div className="finding-item">
          <span className="finding-index">01</span>
          <div>
            <strong>API-01</strong>
            <p>{t("sampleIssue")}</p>
          </div>
        </div>
      </div>
      <div className="inspector-section">
        <h3>{t("sampleRecommendation")}</h3>
        <div className="mini-diff">
          <span className="mini-diff__old">− weight: {"{ type: string }"}</span>
          <span className="mini-diff__new">+ weight: {"{ type: number }"}</span>
        </div>
      </div>
      <div className="inspector-section">
        <h3>{t("evidenceAxes")}</h3>
        <CapabilityLine title={t("sourceReview")} value="source_only" />
        <CapabilityLine title={t("execution")} value="not_tested" />
        <CapabilityLine title={t("independentReview")} value="pending" />
      </div>
      <button
        className="text-link"
        onClick={() =>
          inspect({
            title: "API-01",
            kind: t("exampleOnly"),
            data: {
              requirement: "API-01",
              issue: t("sampleIssue"),
              recommendation: t("sampleRecommendation"),
              scope: "Fictional example; no service called",
            },
          })
        }
      >
        {t("showRaw")}
        <ArrowRight size={13} />
      </button>
    </>
  );
}
