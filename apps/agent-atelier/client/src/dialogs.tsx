import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  Boxes,
  Braces,
  Check,
  ChevronRight,
  FileCheck2,
  FolderOpen,
  Play,
  Search,
  ShieldCheck,
  Workflow,
} from "lucide-react";
import type { CommandFn, Inspection, View } from "./App";
import { api, rows, text, type Data, type Project } from "./api";
import {
  Button,
  CodeViewer,
  Field,
  Modal,
  ProgressSteps,
  RecordDetails,
  Status,
  SurfaceNotice,
  type T,
} from "./ui";
import type { Locale } from "./i18n";
import { profileLabel, type Profile } from "./profiles";

export function BindingDialog({
  initialRoot = "",
  t,
  command,
  busy,
  onClose,
  onConnected,
}: {
  initialRoot?: string;
  t: T;
  command: CommandFn;
  busy: string;
  onClose: () => void;
  onConnected: (id: string) => void;
}) {
  const [root, setRoot] = useState(initialRoot);
  const [name, setName] = useState("");
  const [kind, setKind] = useState("generic");
  const [preview, setPreview] = useState<Data | null>(null);
  const [error, setError] = useState("");
  async function inspect() {
    setError("");
    try {
      const result = await command("project.preview", { root });
      setPreview(result.preview ?? result);
      setName(result.name ?? result.project?.name ?? "");
      setKind(result.kind ?? result.project?.kind ?? "generic");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function connect() {
    setError("");
    try {
      const result = await command("project.bind", {
        preview_id: preview?.preview_id ?? preview?.id,
        name: name.trim() || undefined,
        view_profile: kind,
      });
      const project = result.project ?? result.binding ?? result;
      if (project.id) onConnected(project.id);
      else setError(t("previewIncomplete"));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <Modal
      title={t("connectProject")}
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose}>{t("cancel")}</Button>
          {preview ? (
            <Button
              tone="primary"
              icon={Check}
              onClick={() => void connect()}
              disabled={Boolean(busy)}
            >
              {busy ? t("processing") : t("connectThis")}
            </Button>
          ) : (
            <Button
              tone="primary"
              icon={FolderOpen}
              disabled={!root.startsWith("/") || Boolean(busy)}
              onClick={() => void inspect()}
            >
              {busy ? t("processing") : t("previewFolder")}
            </Button>
          )}
        </>
      }
    >
      <ProgressSteps
        labels={[t("source"), t("preview"), t("connectThis")]}
        current={preview ? 1 : 0}
      />
      <p className="dialog-lead">{t("bindingHelp")}</p>
      <Field label={t("projectRoot")}>
        <input
          autoFocus
          value={root}
          onChange={(e) => {
            setRoot(e.target.value);
            setPreview(null);
          }}
          placeholder={t("directoryPlaceholder")}
          autoComplete="off"
          spellCheck={false}
        />
      </Field>
      {preview && (
        <>
          <div className="form-grid">
            <Field label={t("projectName")}>
              <input value={name} onChange={(e) => setName(e.target.value)} />
            </Field>
            <Field label={t("kind")}>
              <select value={kind} onChange={(e) => setKind(e.target.value)}>
                {[
                  "app",
                  "bot",
                  "game",
                  "agent",
                  "research",
                  "document",
                  "mixed",
                  "generic",
                ].map((kind) => (
                  <option key={kind} value={kind}>
                    {t(profileLabel(kind as Profile))}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <div className="binding-preview">
            <header>
              <FileCheck2 size={17} />
              <strong>{t("bindingPreview")}</strong>
              <Status value={preview.status ?? "source_only"} />
            </header>
            <RecordDetails value={preview} t={t} />
          </div>
        </>
      )}
      {error && <SurfaceNotice tone="error">{error}</SurfaceNotice>}
      <SurfaceNotice>
        <ShieldCheck size={16} />
        {t("bindingNoReset")}
      </SurfaceNotice>
    </Modal>
  );
}

export function TaskDialog({
  preset,
  t,
  selected,
  projects,
  onProjectSelected,
  demo,
  command,
  busy,
  locale,
  onClose,
  onDispatched,
}: {
  preset?: Data | null;
  t: T;
  selected: Project | null;
  projects: Project[];
  onProjectSelected: (id: string) => void;
  demo: boolean;
  command: CommandFn;
  busy: string;
  locale: Locale;
  onClose: () => void;
  onDispatched: (job: Data) => void;
}) {
  const [objective, setObjective] = useState(preset?.objective ?? "");
  const [acceptance, setAcceptance] = useState(preset?.acceptance ?? "");
  const [scope, setScope] = useState("read-only");
  const [paths, setPaths] = useState("");
  const [deadline, setDeadline] = useState(300);
  const [publicWebRead, setPublicWebRead] = useState(false);
  const [prepared, setPrepared] = useState<Data | null>(null);
  const scopeReviewRef = useRef<HTMLParagraphElement>(null);
  const [reviewed, setReviewed] = useState(false);
  const [error, setError] = useState("");
  const universal =
    preset?.universal_entry !== false && !preset?.selected_skills;
  useEffect(() => {
    if (prepared) scopeReviewRef.current?.focus();
  }, [prepared]);
  const [intent, setIntent] = useState(preset?.route ?? "auto");
  const [routePreview, setRoutePreview] = useState<Data | null>(null);
  const [maintenanceKind, setMaintenanceKind] = useState(
    preset?.maintenance?.target_kind ?? "orchestrator",
  );
  const [maintenanceRefs, setMaintenanceRefs] = useState(
    (preset?.maintenance?.target_refs ?? []).join("\n"),
  );
  useEffect(() => {
    setRoutePreview(null);
  }, [objective, intent, maintenanceKind, maintenanceRefs]);
  async function previewRoute() {
    if (!selected) return;
    setError("");
    try {
      setRoutePreview(
        await command(
          "task.route",
          {
            objective,
            ...(intent !== "auto" ? { route: intent } : {}),
            ...(intent === "maintain_system"
              ? {
                  maintenance: {
                    target_kind: maintenanceKind,
                    target_refs: maintenanceRefs
                      .split("\n")
                      .map((value: string) => value.trim())
                      .filter(Boolean),
                  },
                }
              : {}),
          },
          selected,
        ),
      );
    } catch (error) {
      setError((error as Error).message);
    }
  }
  async function prepare() {
    if (!selected) return;
    try {
      setError("");
      const result = await command(
        "task.prepare",
        {
          objective,
          acceptance,
          universal_entry: universal,
          ...(intent !== "auto" ? { route: intent } : {}),
          ...(intent === "maintain_system"
            ? {
                maintenance: {
                  target_kind: maintenanceKind,
                  target_refs: maintenanceRefs
                    .split("\n")
                    .map((value: string) => value.trim())
                    .filter(Boolean),
                },
              }
            : {}),
          scope,
          allowed_paths: paths
            .split("\n")
            .map((p) => p.trim())
            .filter(Boolean),
          deadline_seconds: deadline,
          capability_scope: { public_web_read: publicWebRead },
          ...(preset?.selected_skills
            ? { selected_skills: preset.selected_skills }
            : {}),
          ...(preset?.planning_only ? { planning_only: true } : {}),
          ...(threadBinding ? { thread_binding_id: threadBinding.id } : {}),
        },
        selected,
      );
      setPrepared(result);
      setReviewed(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  const [threads, setThreads] = useState<Data[] | null>(null);
  const [threadPreview, setThreadPreview] = useState<Data | null>(null);
  const [threadBinding, setThreadBinding] = useState<Data | null>(null);
  const [handoff, setHandoff] = useState(false);
  const [loadingThreads, setLoadingThreads] = useState(false);
  const [threadCursor, setThreadCursor] = useState<string | undefined>();
  useEffect(() => {
    setPrepared(null);
    setReviewed(false);
    setRoutePreview(null);
    setThreadBinding(null);
    setThreadPreview(null);
    setThreads(null);
    setThreadCursor(undefined);
  }, [selected?.id]);
  useEffect(() => {
    if (preset?.thread_id && selected && !demo)
      void previewThread(preset.thread_id);
  }, [preset?.thread_id, selected?.id]);
  async function loadThreads(append = false) {
    if (!selected) return;
    setLoadingThreads(true);
    setError("");
    try {
      const result = await api.threads(
        selected.id,
        append ? threadCursor : undefined,
      );
      const incoming = rows(result.data ?? result.threads ?? result);
      setThreads((previous) =>
        append
          ? [
              ...new Map(
                [...(previous ?? []), ...incoming].map((item) => [
                  item.id,
                  item,
                ]),
              ).values(),
            ]
          : incoming,
      );
      setThreadCursor(result.nextCursor ?? result.next_cursor ?? undefined);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingThreads(false);
    }
  }
  async function previewThread(id: string) {
    if (!selected) return;
    try {
      setThreadPreview(
        await command("thread.preview", { thread_id: id }, selected),
      );
      setHandoff(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function adoptThread() {
    if (!selected || !threadPreview) return;
    try {
      const result = await command(
        "thread.adopt",
        {
          preview_id: threadPreview.preview_id,
          confirmed_idle_handoff: handoff,
        },
        selected,
      );
      setThreadBinding(result.thread_binding);
      setThreadPreview(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function dispatch() {
    if (!selected || !prepared) return;
    try {
      const result = await command(
        "task.dispatch",
        { task_id: prepared.task?.id ?? prepared.task_id ?? prepared.id },
        selected,
      );
      onDispatched(result.job ?? result);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <Modal
      title={
        prepared
          ? t("preparedTask")
          : universal
            ? t("universalEntry")
            : t("newTask")
      }
      onClose={onClose}
      wide
      footer={
        <>
          <Button
            onClick={
              prepared
                ? () => {
                    setPrepared(null);
                    setReviewed(false);
                  }
                : onClose
            }
          >
            {prepared ? t("back") : t("cancel")}
          </Button>
          {prepared ? (
            <Button
              icon={Play}
              tone="primary"
              onClick={() => void dispatch()}
              disabled={!reviewed || demo || Boolean(busy)}
            >
              {busy ? t("processing") : t("dispatch")}
            </Button>
          ) : (
            <Button
              icon={ArrowRight}
              tone="primary"
              disabled={
                !selected ||
                !objective.trim() ||
                !acceptance.trim() ||
                !Number.isFinite(deadline) ||
                deadline < 30 ||
                deadline > 3600 ||
                demo ||
                Boolean(busy) ||
                (scope === "workspace-write" && !paths.trim())
              }
              onClick={() =>
                void (universal && !routePreview ? previewRoute() : prepare())
              }
            >
              {busy
                ? t("processing")
                : universal && !routePreview
                  ? t("reviewRoute")
                  : t("prepareTask")}
            </Button>
          )}
        </>
      }
    >
      <ProgressSteps
        labels={[t("objective"), t("scopeReview"), t("execution")]}
        current={prepared ? 1 : 0}
      />
      {universal && (
        <div className="universal-task-intro">
          <Workflow size={22} />
          <div>
            <strong>{t("entryQuestion")}</strong>
            <p>{t("entryDescription")}</p>
          </div>
        </div>
      )}
      {preset?.selected_skills && (
        <div className="selected-competencies">
          <Braces size={15} />
          <span>{t("competence")}</span>
          {preset.selected_skills.map((name: string) => (
            <code key={name}>{name}</code>
          ))}
        </div>
      )}
      {preset?.planning_only && (
        <SurfaceNotice>{t("planningOnly")}</SurfaceNotice>
      )}
      {!selected ? (
        <SurfaceNotice tone="warning">{t("connectBeforeTask")}</SurfaceNotice>
      ) : (
        <div className="task-project-context">
          <span className="project-icon">
            <Boxes size={17} />
          </span>
          <strong>{selected.name}</strong>
          <code title={selected.root}>{selected.root}</code>
          <Status value="read-only" label={t("statePreserved")} />
        </div>
      )}
      {!prepared && projects.length > 1 && (
        <Field label={t("projectSelection")}>
          <select
            value={selected?.id ?? ""}
            onChange={(event) => onProjectSelected(event.target.value)}
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </Field>
      )}
      {prepared ? (
        <>
          <p className="dialog-lead" ref={scopeReviewRef} tabIndex={-1}>
            {t("reviewCapsule")}
          </p>
          <div className="scope-summary">
            <div>
              <small>{t("objective")}</small>
              <strong>{objective}</strong>
            </div>
            <div>
              <small>{t("scope")}</small>
              <span>{scope}</span>
            </div>
            <div>
              <small>{t("deadline")}</small>
              <span>{deadline}</span>
            </div>
          </div>
          <CodeViewer
            value={prepared.capsule ?? prepared}
            fileName="context-capsule.json"
            locale={locale}
          />
          <SurfaceNotice>{t("taskPreparedNote")}</SurfaceNotice>
          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={reviewed}
              onChange={(e) => setReviewed(e.target.checked)}
            />
            <span>{t("confirmExactScope")}</span>
          </label>
        </>
      ) : (
        <>
          <Field label={t("objective")}>
            <textarea
              autoFocus
              rows={4}
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder={t("objectivePlaceholder")}
            />
          </Field>
          {universal && (
            <Field label={t("workIntent")} help={t("intentHelp")}>
              <select
                value={intent}
                onChange={(event) => setIntent(event.target.value)}
              >
                {[
                  "auto",
                  "direct",
                  "specialist",
                  "project_agent",
                  "director",
                  "compose",
                  "create_agent",
                  "maintain_system",
                  "bridge",
                ].map((value) => (
                  <option key={value} value={value}>
                    {t(
                      (
                        {
                          auto: "routeAuto",
                          direct: "routeDirect",
                          specialist: "routeSpecialist",
                          project_agent: "routeProjectAgent",
                          director: "routeDirector",
                          compose: "routeCompose",
                          create_agent: "routeCreateAgent",
                          maintain_system: "routeMaintain",
                          bridge: "routeBridge",
                        } as const
                      )[value as "auto"],
                    )}
                  </option>
                ))}
              </select>
            </Field>
          )}
          {universal && intent === "maintain_system" && (
            <div className="maintenance-target-fields">
              <Field label={t("maintenanceTarget")}>
                <select
                  value={maintenanceKind}
                  onChange={(event) => setMaintenanceKind(event.target.value)}
                >
                  {[
                    "orchestrator",
                    "skill",
                    "constructor",
                    "project_agent",
                    "agent",
                    "system",
                  ].map((value) => (
                    <option key={value} value={value}>
                      {t(
                        (
                          {
                            orchestrator: "targetOrchestrator",
                            skill: "targetSkill",
                            constructor: "targetConstructor",
                            project_agent: "targetProjectAgent",
                            agent: "targetAgent",
                            system: "targetSystem",
                          } as const
                        )[value as "orchestrator"],
                      )}
                    </option>
                  ))}
                </select>
              </Field>
              <Field
                label={t("targetSourcePaths")}
                help={t("targetSourcePathsHelp")}
              >
                <textarea
                  value={maintenanceRefs}
                  rows={2}
                  onChange={(event) => setMaintenanceRefs(event.target.value)}
                  placeholder="optional-skills/atelier-orchestrator"
                  spellCheck={false}
                />
              </Field>
            </div>
          )}
          <Field label={t("acceptance")}>
            <textarea
              rows={3}
              value={acceptance}
              onChange={(e) => setAcceptance(e.target.value)}
              placeholder={t("acceptancePlaceholder")}
            />
          </Field>
          <div className="form-grid">
            <Field label={t("scope")}>
              <select
                value={scope}
                disabled={preset?.planning_only === true}
                onChange={(e) => setScope(e.target.value)}
              >
                <option value="read-only">{t("readOnly")}</option>
                <option value="workspace-write">{t("workspaceWrite")}</option>
              </select>
            </Field>
            <Field label={t("deadline")}>
              <input
                type="number"
                min={30}
                max={3600}
                value={deadline}
                onChange={(e) => setDeadline(Number(e.target.value))}
              />
            </Field>
          </div>
          <Field label={t("allowedPaths")} help={t("pathsHelp")}>
            <textarea
              rows={2}
              value={paths}
              onChange={(e) => setPaths(e.target.value)}
              placeholder="src/&#10;tests/"
              spellCheck={false}
            />
          </Field>
          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={publicWebRead}
              onChange={(event) => setPublicWebRead(event.target.checked)}
            />
            <span>
              {t("sourceAccess")} · <code>public_web_read</code>
              <small>{t("readOnly")}</small>
            </span>
          </label>
          {routePreview && (
            <div className="route-preview">
              <div>
                <NetworkRoute />
                <span>
                  <small>{t("proposedRoute")}</small>
                  <strong>
                    {routeLabel(
                      routePreview.routing?.route ?? routePreview.route,
                      t,
                    )}
                  </strong>
                </span>
                <Status value="prepared" label={t("proposed")} />
              </div>
              <p>
                {(routePreview.routing ?? routePreview).requested_route
                  ? `${t("workIntent")}: ${routeLabel((routePreview.routing ?? routePreview).route, t)}`
                  : (routePreview.routing ?? routePreview)
                        .preferred_project_agent
                    ? `${t("routeProjectAgent")}: ${(routePreview.routing ?? routePreview).preferred_project_agent}`
                    : t("intentHelp")}
              </p>
              {(routePreview.routing ?? routePreview).capability_gaps?.length >
                0 && (
                <SurfaceNotice tone="warning">
                  {(routePreview.routing ?? routePreview).capability_gaps.map(
                    (gap: Data) => (
                      <p key={gap.code}>
                        <code>{gap.code}</code> ·{" "}
                        {gap.code === "PROJECT_AGENT_UNVERIFIED"
                          ? t("notTested")
                          : t("nativeControllerHelp")}
                      </p>
                    ),
                  )}
                </SurfaceNotice>
              )}
              <dl>
                <dt>{t("responsibleExecutor")}</dt>
                <dd>
                  {text(
                    routePreview.routing?.execution_owner ??
                      routePreview.execution_owner,
                    "atelier-orchestrator",
                  )}
                </dd>
              </dl>
              <SurfaceNotice>{t("routePreviewHelp")}</SurfaceNotice>
            </div>
          )}
          <details className="thread-binding" open={Boolean(preset?.thread_id)}>
            <summary>
              <Workflow size={15} />
              {t("threads")}
              <ChevronRight size={14} />
            </summary>
            <div>
              <p>{t("threadHelp")}</p>
              {threadBinding ? (
                <div className="thread-bound">
                  <Check size={16} />
                  <span>
                    {t("threadBinding")}
                    <code>{threadBinding.thread_id}</code>
                  </span>
                  <Button small onClick={() => setThreadBinding(null)}>
                    {t("chooseNewThread")}
                  </Button>
                </div>
              ) : (
                <>
                  <Button
                    small
                    icon={Search}
                    disabled={demo || loadingThreads || Boolean(busy)}
                    onClick={() => void loadThreads()}
                  >
                    {loadingThreads ? t("processing") : t("loadThreads")}
                  </Button>
                  {threads && (
                    <div className="thread-options">
                      {threads.length ? (
                        threads.map((thread) => (
                          <button
                            key={thread.id}
                            onClick={() => void previewThread(thread.id)}
                            disabled={Boolean(busy)}
                          >
                            <span>
                              <strong>
                                {text(
                                  thread.name ??
                                    thread.title ??
                                    thread.preview ??
                                    thread.id,
                                )}
                              </strong>
                              <code>{thread.id}</code>
                            </span>
                            <Status
                              value={thread.status?.type ?? thread.status}
                            />
                            <ChevronRight size={13} />
                          </button>
                        ))
                      ) : (
                        <p>{t("noThreads")}</p>
                      )}
                    </div>
                  )}
                  {threadCursor && (
                    <Button
                      small
                      disabled={loadingThreads || Boolean(busy)}
                      onClick={() => void loadThreads(true)}
                    >
                      {t("loadMoreThreads")}
                    </Button>
                  )}
                  {threadPreview && (
                    <div className="thread-handoff">
                      <strong>{t("idleHandoff")}</strong>
                      <RecordDetails value={threadPreview} t={t} compact />
                      <label className="checkbox-field">
                        <input
                          type="checkbox"
                          checked={handoff}
                          onChange={(e) => setHandoff(e.target.checked)}
                        />
                        <span>{t("handoffConfirmed")}</span>
                      </label>
                      <Button
                        small
                        tone="primary"
                        disabled={
                          !handoff ||
                          Boolean(busy) ||
                          !["idle", "notLoaded"].includes(
                            threadPreview.host_status,
                          )
                        }
                        onClick={() => void adoptThread()}
                      >
                        {t("adoptThread")}
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
          </details>
          <SurfaceNotice>
            <ShieldCheck size={16} />
            {t("actualExecution")}
          </SurfaceNotice>
        </>
      )}
      {demo && (
        <SurfaceNotice tone="warning">{t("disabledInDemo")}</SurfaceNotice>
      )}
      {error && <SurfaceNotice tone="error">{error}</SurfaceNotice>}
    </Modal>
  );
}

export function SearchDialog({
  t,
  projects,
  skills,
  onClose,
  selectProject,
  navigate,
  inspect,
}: {
  t: T;
  projects: Project[];
  skills: Data[];
  onClose: () => void;
  selectProject: (id: string) => void;
  navigate: (view: View) => void;
  inspect: (item: Inspection) => void;
}) {
  const [query, setQuery] = useState("");
  const result = useMemo(() => {
    const q = query.toLocaleLowerCase();
    return {
      projects: projects.filter((p) =>
        `${p.name} ${p.kind} ${p.summary}`.toLocaleLowerCase().includes(q),
      ),
      skills: skills
        .filter((s) =>
          `${s.name} ${s.description} ${s.display_name}`
            .toLocaleLowerCase()
            .includes(q),
        )
        .slice(0, 12),
    };
  }, [projects, skills, query]);
  const actions: { label: string; view: View; icon: typeof Boxes }[] = [
    { label: t("products"), view: "overview", icon: Boxes },
    { label: t("skillLibrary"), view: "skills", icon: Braces },
    { label: t("jobs"), view: "jobs", icon: Workflow },
    { label: t("doctor"), view: "integrations", icon: ShieldCheck },
  ];
  return (
    <Modal title={t("searchShort")} onClose={onClose}>
      <div className="command-search">
        <Search size={19} />
        <input
          autoFocus
          data-autofocus
          placeholder={t("searchHint")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <kbd>ESC</kbd>
      </div>
      <div className="command-results">
        <h3>{t("actions")}</h3>
        {actions
          .filter((a) =>
            a.label.toLocaleLowerCase().includes(query.toLocaleLowerCase()),
          )
          .map((a) => (
            <button key={a.view} onClick={() => navigate(a.view)}>
              <a.icon size={17} />
              <span>{a.label}</span>
              <ChevronRight size={14} />
            </button>
          ))}
        {result.projects.length > 0 && <h3>{t("products")}</h3>}
        {result.projects.map((p) => (
          <button key={p.id} onClick={() => selectProject(p.id)}>
            <Boxes size={17} />
            <span>
              <strong>{p.name}</strong>
              <small>{p.kind}</small>
            </span>
            <ChevronRight size={14} />
          </button>
        ))}
        {result.skills.length > 0 && <h3>{t("agents")}</h3>}
        {result.skills.map((s) => (
          <button
            key={s.id ?? s.path ?? s.name}
            onClick={() => {
              navigate("skills");
              inspect({
                title: text(s.display_name ?? s.name),
                kind: "skill",
                data: s,
              });
            }}
          >
            <Braces size={17} />
            <span>
              <strong>{text(s.display_name ?? s.name)}</strong>
              <small>{text(s.description, "")}</small>
            </span>
            <ChevronRight size={14} />
          </button>
        ))}
        {!result.projects.length && !result.skills.length && query && (
          <p className="search-empty">{t("nothingFound")}</p>
        )}
      </div>
    </Modal>
  );
}

function NetworkRoute() {
  return <Workflow size={20} />;
}
function routeLabel(value: string, t: T) {
  const keys = {
    direct: "routeDirect",
    specialist: "routeSpecialist",
    project_agent: "routeProjectAgent",
    director: "routeDirector",
    compose: "routeCompose",
    create_agent: "routeCreateAgent",
    maintain_system: "routeMaintain",
    bridge: "routeBridge",
  } as const;
  return t(keys[value as keyof typeof keys] ?? "routeAuto");
}
