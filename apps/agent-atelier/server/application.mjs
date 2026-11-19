import { EventEmitter } from "node:events";
import { readFile, mkdir } from "node:fs/promises";
import { mkdirSync, realpathSync } from "node:fs";
import { isAbsolute, join, resolve, relative } from "node:path";
import { randomUUID } from "node:crypto";
import { Store } from "./store.mjs";
import { ProjectAdapter } from "./projects.mjs";
import { CodexAdapter, CodexHistoryAdapter } from "./codex.mjs";
import { SkillsManager } from "./skills.mjs";
import { RetentionManager } from "./retention.mjs";
import { compileContext } from "./context.mjs";
import { InstructionsManager, instructionSettings } from "./instructions.mjs";
import { PortfolioManager } from "./portfolio.mjs";
import { IntegrationsManager } from "./integrations.mjs";
import { ImageGeneration } from "./image-generation.mjs";
import { proposeRoute } from "./routing.mjs";
import { NativeControllers } from "./controllers.mjs";
import { OptionalUpdates } from "./optional_updates.mjs";
import {
  ACTIVE_JOB_STATES,
  API_VERSION,
  DEFAULT_LOCALE,
  LOCALES,
  OPERATIONS,
  SERVICE_VERSION,
  TERMINAL_JOB_STATES,
  resolveLocale,
} from "../shared/contracts.mjs";
import {
  atomicWrite,
  canonical,
  digest,
  fail,
  id,
  isWithin,
  now,
  parseStrictJson,
  publicError,
  readSource,
  redact,
  sha,
  text,
  ServiceError,
  containsObviousCredential,
} from "./utils.mjs";
export class Application extends EventEmitter {
  constructor({
    dataDir,
    repoRoot,
    store,
    codex,
    historyCodex,
    integrations,
    imageGeneration,
  } = {}) {
    super();
    mkdirSync(dataDir, { recursive: true, mode: 0o700 });
    dataDir = realpathSync(dataDir);
    this.dataDir = dataDir;
    this.repoRoot = repoRoot;
    this.store = store ?? new Store(join(dataDir, "atelier.sqlite"));
    this.projects = new ProjectAdapter(this.store, dataDir);
    this.skills = new SkillsManager({
      store: this.store,
      repoRoot,
      dataDir,
    });
    this.retention = new RetentionManager({ store: this.store, dataDir });
    this.instructions = new InstructionsManager({ dataDir });
    this.codex =
      codex ??
      new CodexAdapter({ dataDir, repoRoot, instructions: this.instructions });
    // Native paginated history lives in the native index. Its read-only
    // transport cannot dispatch; model jobs retain their isolated index.
    this.historyCodex =
      historyCodex ?? (codex || new CodexHistoryAdapter({ dataDir }));
    this.portfolio = new PortfolioManager({
      store: this.store,
      codex: this.historyCodex,
      dataDir,
    });
    this.integrationCodex = integrations
      ? null
      : new CodexAdapter({ dataDir, integrationMetadataOnly: true });
    this.imageGeneration = imageGeneration ?? new ImageGeneration({ repoRoot });
    this.integrations =
      integrations ??
      new IntegrationsManager({
        dataDir,
        imageGeneration: this.imageGeneration,
        nativeAuthMode: () => this.integrationCodex.status.auth_mode,
        nativeRpc: (method, params) =>
          this.integrationCodex.integrationMetadata(method, params),
      });
    this.controllers = new NativeControllers({
      store: this.store,
      repoRoot,
      dataDir,
      projects: this.projects,
    });
    this.optionalUpdates = new OptionalUpdates({
      store: this.store,
      repoRoot,
      dataDir,
    });
    this.instanceId = id("instance");
    this.timers = new Map();
    this.previewRestores = new Map();
    this.threadPreviews = new Map();
    this.closing = false;
    this.maintenanceOperation = null;
    if (!this.store.get("settings", "owner"))
      this.store.put("settings", "owner", {
        id: "owner",
        locale: DEFAULT_LOCALE,
        authority_epoch: randomUUID(),
        created_at: now(),
      });
    for (const job of this.store.list("job"))
      if (
        ACTIVE_JOB_STATES.includes(job.status) &&
        job.status !== "outcome_unknown"
      )
        this.store.put("job", job.id, {
          ...job,
          ...this.#unconfirmedInterruption(job),
          status: "outcome_unknown",
          unknown_reason:
            "Service restarted before a terminal receipt; reconcile the actual thread/turn before retrying",
        });
    for (const operation of this.store.list("native-controller"))
      if (operation.status === "pending")
        this.store.put("native-controller", operation.id, {
          ...operation,
          status: "outcome_unknown",
          unknown_reason:
            "Service restarted before a terminal native controller receipt; reconcile without replay",
        });
    this.codex.on("notification", (event) => this.#notification(event));
    this.codex.on("request", (request) => this.#request(request));
    this.codex.on("status", (status) =>
      this.event("capability.changed", { codex: status }),
    );
    this.codex.on("disconnected", () => {
      for (const job of this.store.list("job"))
        if (
          [
            "gating",
            "queued",
            "pause_pending",
            "dispatching",
            "running",
            "awaiting_approval",
            "awaiting_input",
            "cancel_requested",
          ].includes(job.status)
        )
          this.updateJob(job.id, {
            status: "outcome_unknown",
            unknown_reason: "Host connection closed before a terminal receipt",
          });
    });
  }
  event(event, data) {
    const result = this.store.event(event, redact(data));
    this.emit("event", result);
    return result;
  }
  updateJob(jobId, delta) {
    const job = this.store.get("job", jobId);
    if (!job) return;
    const value = this.store.put("job", jobId, {
      ...job,
      ...(delta.status === "outcome_unknown"
        ? this.#unconfirmedInterruption(job)
        : {}),
      ...redact(delta),
    });
    this.event("job.changed", { job: value });
    return value;
  }
  async bootstrap(csrfToken) {
    const settings = this.store.get("settings", "owner");
    return {
      api_version: API_VERSION,
      version: SERVICE_VERSION,
      instance_id: this.instanceId,
      csrf_token: csrfToken,
      locale: resolveLocale(undefined, settings.locale),
      retention: this.retention.policy(),
      pending_cleanup: this.store
        .list("privacy-cleanup")
        .filter((row) => row.status !== "completed")
        .map((row) => ({
          id: row.id,
          status: row.status,
          files_pending: row.files.length,
        })),
      portfolio: this.portfolio.get(),
      projects: this.store.list("project"),
      jobs: this.store.list("job"),
      native_controllers: this.store.list("native-controller"),
      optional_updates: this.store.list("optional-update").map((x) => ({
        id: x.id,
        name: x.name ?? x.skill_name,
        status: x.status,
        started_at: x.started_at,
        completed_at: x.completed_at,
      })),
      tasks: this.store.list("task"),
      skills: await this.skills.list(),
      capabilities: {
        codex: this.codex.status,
        work: {
          status: "deferred",
          reason: "The owner moved Work audit/update into a separate task",
        },
      },
      activity: this.store.events(
        Math.max(0, this.store.latestEventSequence() - 70),
        70,
      ),
      metrics: {
        projects: this.store.list("project").length,
        jobs: this.store.list("job").length,
        active_jobs: this.activeJobs().length,
        unknown_outcomes:
          this.store.list("job").filter((x) => x.status === "outcome_unknown")
            .length +
          this.activeNativeControllers().filter(
            (x) => x.status === "outcome_unknown",
          ).length +
          this.activeOptionalUpdates().filter(
            (x) => x.status === "outcome_unknown",
          ).length,
      },
      notice:
        "Live local data. No project is connected until explicitly bound.",
    };
  }
  activeJobs() {
    return this.store
      .list("job")
      .filter((x) => ACTIVE_JOB_STATES.includes(x.status));
  }
  activeOptionalUpdates() {
    return this.store
      .list("optional-update")
      .filter((x) => ["pending", "outcome_unknown"].includes(x.status));
  }
  activeNativeControllers() {
    return this.store
      .list("native-controller")
      .filter((x) => ["pending", "outcome_unknown"].includes(x.status));
  }
  doctor() {
    const jobs = this.activeJobs();
    return {
      instance_id: this.instanceId,
      status:
        jobs.some((x) => x.status === "outcome_unknown") ||
        this.activeNativeControllers().length ||
        this.activeOptionalUpdates().length
          ? "attention"
          : "healthy",
      database: {
        schema: "agent-atelier.db/1",
        engine: "SQLite",
        journal: "WAL",
        path: this.store.path,
      },
      codex: this.codex.status,
      work: { status: "deferred" },
      projects: this.store.list("project").map((x) => ({
        id: x.id,
        root: x.root,
        revision: x.revision,
        adapter: x.kind,
        native_mutation: "read-only-projection",
      })),
      active_jobs: jobs,
      active_native_controllers: this.activeNativeControllers(),
      active_optional_updates: this.activeOptionalUpdates(),
      checks: [
        {
          id: "loopback",
          status: "configured",
          detail: "Only loopback HTTP is supported",
        },
        {
          id: "native-authority",
          status: "preserved",
          detail:
            "Project files remain authoritative; service restore never writes them",
        },
        {
          id: "codex",
          status: this.codex.status.status,
          detail:
            this.codex.status.reason ??
            "Connect to verify actual protocol capability",
        },
        {
          id: "unknown-effects",
          status: jobs.some((x) => x.status === "outcome_unknown")
            ? "blocked"
            : "clear",
          detail: "Unknown outcomes are never replayed automatically",
        },
      ],
    };
  }
  async execute(command) {
    text(command.command_id, "command_id", 8, 160);
    fail(
      OPERATIONS.includes(command.operation),
      "UNSUPPORTED_OPERATION",
      "This command is not in the supported operation catalog",
      404,
    );
    fail(
      command.payload === undefined ||
        (command.payload &&
          typeof command.payload === "object" &&
          !Array.isArray(command.payload)),
      "INVALID_INPUT",
      "payload must be an object",
    );
    fail(
      !containsObviousCredential(command.payload),
      "SECRET_INPUT_REJECTED",
      "Use a credential reference rather than a secret value in task or command inputs",
    );
    const reservation = this.store.commandStart(command);
    if (reservation.existing) return reservation.receipt;
    try {
      const result = await this.#operate(command);
      const receipt = {
        command_id: command.command_id,
        operation: command.operation,
        status: "completed",
        result: redact(result),
        completed_at: now(),
      };
      this.store.commandFinish(command.command_id, receipt);
      this.event("command.completed", {
        command_id: command.command_id,
        operation: command.operation,
        status: "completed",
      });
      return receipt;
    } catch (error) {
      const receipt = {
        command_id: command.command_id,
        operation: command.operation,
        status: "failed",
        error: publicError(error),
        completed_at: now(),
      };
      this.store.commandFinish(command.command_id, receipt);
      this.event("command.failed", {
        command_id: command.command_id,
        operation: command.operation,
        error: receipt.error,
      });
      return receipt;
    }
  }
  async #operate(command) {
    const payload = command.payload ?? {};
    const projectId = command.project_id;
    fail(
      !this.maintenanceOperation ||
        ["service.status", "service.doctor"].includes(command.operation),
      "SERVICE_STOPPING",
      "Service maintenance owns the current mutation boundary",
      409,
    );
    switch (command.operation) {
      case "skills.optional-preview":
        return this.optionalUpdates.preview(payload);
      case "skills.optional-verify": {
        const result = await this.optionalUpdates.verify(payload);
        this.skills.hostSources.clear();
        return result;
      }
      case "skills.optional-apply":
        return this.maintain("optional-update", async () => {
          try {
            return await this.optionalUpdates.apply(payload);
          } finally {
            this.skills.hostSources.clear();
          }
        });
      case "skills.optional-rollback":
        return this.maintain("optional-rollback", async () => {
          try {
            return await this.optionalUpdates.rollback(payload);
          } finally {
            this.skills.hostSources.clear();
          }
        });
      case "controller.preview":
        return this.controllers.preview(projectId, payload);
      case "controller.apply":
        return this.maintain("native-controller", () =>
          this.controllers.apply(projectId, payload),
        );
      case "controller.reconcile":
        return payload.confirmed === true
          ? this.maintain("native-controller-reconcile", () =>
              this.controllers.reconcile(projectId, payload),
            )
          : this.controllers.reconcile(projectId, payload);
      case "portfolio.refresh": {
        const result = await this.portfolio.refresh(payload);
        this.event("portfolio.changed", {
          summary: result.summary,
          coverage: result.coverage,
        });
        return result;
      }
      case "task.route":
        return this.route(projectId, payload);
      case "project.preview":
        return this.projects.preview(payload);
      case "project.bind": {
        const result = await this.projects.bind(payload);
        this.event("project.bound", result);
        return result;
      }
      case "project.profile": {
        fail(
          [
            "app",
            "bot",
            "game",
            "agent",
            "research",
            "document",
            "mixed",
            "generic",
          ].includes(payload.view_profile),
          "INVALID_INPUT",
          "Unsupported workspace presentation profile",
        );
        const project = this.projects.get(projectId);
        const updated = this.store.put(
          "project",
          projectId,
          { ...project, view_profile: payload.view_profile },
          project.record_revision,
        );
        this.event("project.changed", { project: updated });
        return { project: updated, native_product_written: false };
      }
      case "project.refresh": {
        const result = await this.projects.refresh(
          projectId,
          command.expected_revision,
        );
        this.event("project.changed", result);
        return result;
      }
      case "thread.preview":
        return this.previewThread(projectId, payload);
      case "thread.adopt":
        return this.adoptThread(projectId, payload);
      case "task.prepare":
        return this.prepare(projectId, payload, command.expected_revision);
      case "task.dispatch":
        fail(
          !Object.hasOwn(payload, "resume_thread_id"),
          "SCOPE_MISMATCH",
          "Raw thread overrides are not accepted; use an exact checked thread binding",
          409,
        );
        return this.dispatch(projectId, payload, command.expected_revision);
      case "task.continue":
        fail(
          !Object.hasOwn(payload, "resume_thread_id"),
          "SCOPE_MISMATCH",
          "Raw thread overrides are not accepted",
          409,
        );
        return this.continueTask(projectId, payload, command.expected_revision);
      case "task.pause": {
        const task = this.task(payload.task_id, projectId);
        const job = this.activeJobs().find((x) => x.task_id === task.id);
        const requested = job && this.#pendingInterruption(job);
        this.store.put("task", task.id, {
          ...task,
          status: "paused",
        });
        if (job) {
          const canInterrupt = job.turn_id && job.status !== "outcome_unknown";
          const defer = ["queued", "dispatching"].includes(job.status);
          this.updateJob(job.id, {
            interruption_intent: "pause",
            ...(canInterrupt ? { status: "pause_pending" } : {}),
            ...(canInterrupt && defer && !requested
              ? { interrupt_on_start: this.instanceId }
              : {}),
          });
          if (canInterrupt && !defer && !requested)
            await this.codex.interrupt(job.thread_id, job.turn_id);
        }
        return {
          task: this.store.get("task", task.id),
          job: job ? this.store.get("job", job.id) : null,
        };
      }
      case "job.interrupt": {
        const job = this.job(payload.job_id, projectId);
        fail(
          job.thread_id && job.turn_id,
          "HOST_NOT_RUNNING",
          "Job has no current host turn",
          409,
        );
        fail(
          [
            "queued",
            "dispatching",
            "running",
            "awaiting_approval",
            "awaiting_input",
            "cancel_requested",
          ].includes(job.status),
          "JOB_NOT_ACTIVE",
          "Only an active owned turn can be interrupted",
          409,
        );
        const defer = ["queued", "dispatching"].includes(job.status);
        this.updateJob(job.id, {
          status: "cancel_requested",
          interruption_intent: "cancel",
          ...(defer ? { interrupt_on_start: this.instanceId } : {}),
        });
        if (!defer) await this.codex.interrupt(job.thread_id, job.turn_id);
        return { job: this.store.get("job", job.id) };
      }
      case "job.reconcile":
        return this.reconcile(this.job(payload.job_id, projectId));
      case "job.review": {
        const job = this.job(payload.job_id, projectId);
        fail(
          job.status === "completed",
          "JOB_NOT_COMPLETED",
          "Only a completed execution can be reviewed",
          409,
        );
        fail(
          ["accepted", "rework"].includes(payload.verdict),
          "INVALID_INPUT",
          "Select accepted or rework",
        );
        const note = text(payload.note, "review note", 3, 12e3);
        const review = {
          id: id("review"),
          job_id: job.id,
          project_id: job.project_id,
          verdict: payload.verdict,
          note,
          actor: "local-owner",
          kind: "owner-review",
          independent_qa: false,
          subject_capsule_sha256: job.capsule_sha256,
          created_at: now(),
        };
        this.store.put("review", review.id, review);
        return {
          review,
          job: this.updateJob(job.id, { review_status: payload.verdict }),
        };
      }
      case "approval.respond":
        return this.respond(this.job(payload.job_id, projectId), payload);
      case "decision.record":
        return this.recordDecision(projectId, payload);
      case "evidence.register":
        return this.recordEvidence(projectId, payload);
      case "skills.search":
        return this.skills.list(payload.query ?? "");
      case "skills.audit":
      case "skills.update-plan":
        return this.skills.audit(payload);
      case "skills.diff":
        return this.skills.diff(payload);
      case "skills.apply":
        return this.maintain("skills.apply", () => this.skills.apply(payload));
      case "skills.verify":
        return this.skills.verify(payload);
      case "skills.rollback":
        return this.maintain("skills.rollback", () =>
          this.skills.rollback(payload),
        );
      case "codex.connect": {
        const codex = await this.codex.connect();
        const roots = this.store
          .list("project")
          .map((row) => row.root)
          .slice(0, 30);
        const catalog = await this.codex.skills(
          roots.length ? roots : [this.repoRoot],
        );
        const discovered = await this.skills.adoptHostCatalog(
          catalog.entries,
          roots,
        );
        return { codex, catalog: discovered };
      }
      case "codex.skills": {
        const roots = this.store
          .list("project")
          .map((row) => row.root)
          .slice(0, 30);
        const catalog = await this.codex.skills(
          roots.length ? roots : [this.repoRoot],
        );
        await this.skills.adoptHostCatalog(catalog.entries, roots);
        return catalog;
      }
      case "codex.threads":
        return this.codex.threads(
          this.projects.get(projectId).root,
          payload.cursor,
        );
      case "service.status":
      case "service.doctor":
        return this.doctor();
      case "service.settings": {
        fail(
          LOCALES.includes(payload.locale),
          "INVALID_INPUT",
          "Unsupported interface locale",
        );
        const settings = this.store.get("settings", "owner");
        const value = this.store.put("settings", "owner", {
          ...settings,
          locale: payload.locale,
        });
        this.event("settings.changed", { locale: value.locale });
        return { locale: value.locale };
      }
      case "service.retention":
        return payload.policy
          ? this.retention.configure(payload)
          : { policy: this.retention.policy() };
      case "service.cleanup-preview":
        return this.retention.preview(payload);
      case "service.cleanup-apply":
        return this.maintain("cleanup", async () => {
          const result = await this.retention.apply(payload);
          this.invalidatePrivatePreviews();
          return result;
        });
      case "service.cleanup-resume":
        return this.maintain("cleanup", async () => {
          const result = await this.retention.finishFiles(
            text(payload.cleanup_id, "cleanup_id"),
          );
          this.invalidatePrivatePreviews();
          return result;
        });
      case "service.diagnostic-preview":
        return this.retention.diagnosticPreview({
          version: SERVICE_VERSION,
          capabilities: this.codex.status,
        });
      case "service.diagnostic-export":
        return this.retention.diagnosticExport(payload);
      case "service.backup":
        return this.backup();
      case "service.restore-preview":
        return this.restorePreview(payload);
      case "service.restore":
        return this.restore(payload);
      case "service.stop": {
        this.closing = true;
        this.event("service.stopping", {});
        setTimeout(() => this.emit("stop"), 100).unref();
        return {
          status: "draining",
          active_jobs: this.activeJobs().map((x) => ({
            id: x.id,
            status: x.status,
          })),
        };
      }
      default:
        throw new ServiceError(
          "UNSUPPORTED_OPERATION",
          "Unsupported operation",
          404,
        );
    }
  }
  task(taskId, projectId) {
    const task = this.store.get("task", text(taskId, "task_id"));
    fail(
      task && (!projectId || task.project_id === projectId),
      "TASK_NOT_FOUND",
      "Task not found in this project",
      404,
    );
    return task;
  }
  job(jobId, projectId) {
    const job = this.store.get("job", text(jobId, "job_id"));
    fail(
      job && (!projectId || job.project_id === projectId),
      "JOB_NOT_FOUND",
      "Job not found in this project",
      404,
    );
    return job;
  }
  async boundThread(projectId, threadId) {
    const project = this.projects.get(projectId);
    const result = await this.codex.readThread(
      text(threadId, "thread_id", 1, 240),
    );
    const thread = result?.thread;
    fail(
      thread?.id === threadId &&
        typeof thread.cwd === "string" &&
        isAbsolute(thread.cwd) &&
        resolve(thread.cwd) === project.root,
      "SCOPE_MISMATCH",
      "Thread identity/cwd does not match the explicitly bound project",
      409,
    );
    return { thread, project };
  }
  async checkedThread(projectId, threadId) {
    const { thread, project } = await this.boundThread(projectId, threadId);
    let execution_context_available = null;
    if (thread.historyMode === "paginated") {
      // The global read-only reader may see history that this isolated
      // executor cannot resume. Metadata and an idle handoff cannot replace it.
      try {
        const page = await this.codex.historyTurns(threadId, { limit: 1 });
        execution_context_available =
          Array.isArray(page.data) && page.data.length > 0;
      } catch {
        execution_context_available = false;
      }
    }
    return {
      thread,
      host_status: thread.status?.type ?? thread.status ?? "unknown",
      project,
      execution_context_available,
    };
  }
  async previewThread(projectId, payload) {
    const observed = await this.checkedThread(projectId, payload.thread_id);
    const preview_id = id("thread-preview");
    const preview = {
      preview_id,
      project_id: projectId,
      thread_id: observed.thread.id,
      cwd: observed.project.root,
      host_status: observed.host_status,
      model_provider: observed.thread.modelProvider ?? null,
      updated_at: observed.thread.updatedAt ?? null,
      preview: observed.thread.preview ?? "",
      global_owner_verified: false,
      execution_context_available: observed.execution_context_available,
      warning:
        observed.execution_context_available === false
          ? "This isolated executor cannot restore this native paginated history. Continue that chat in its capable native host, or prepare a fresh bounded project task from reviewed sources. Read-only portfolio access is not execution context."
          : "This client cannot fence an independent desktop client. Close other writers and explicitly hand off an idle thread before execution.",
      expires_at: Date.now() + 3e5,
    };
    this.threadPreviews.set(preview_id, preview);
    return preview;
  }
  async adoptThread(projectId, payload) {
    const preview = this.threadPreviews.get(
      text(payload.preview_id, "preview_id"),
    );
    fail(
      preview &&
        preview.project_id === projectId &&
        preview.expires_at > Date.now(),
      "PREVIEW_EXPIRED",
      "Preview this exact thread again",
      409,
    );
    fail(
      payload.confirmed_idle_handoff === true,
      "SCOPE_MISMATCH",
      "An explicit manual idle handoff is required",
      409,
    );
    const observed = await this.checkedThread(projectId, preview.thread_id);
    fail(
      observed.execution_context_available !== false,
      "CAPABILITY_UNVERIFIED",
      "Native paginated history is unavailable to the isolated executor; use the native host or a fresh bounded project task with reviewed sources",
      409,
    );
    fail(
      ["idle", "notLoaded"].includes(observed.host_status),
      "WRITER_CONFLICT",
      "Thread is active or unknown; it cannot be adopted for execution",
      409,
    );
    fail(
      !this.activeJobs().some((x) => x.thread_id === preview.thread_id),
      "WRITER_CONFLICT",
      "The service already has an active or unknown job for this thread",
      409,
    );
    const binding = {
      id: id("thread-binding"),
      project_id: projectId,
      thread_id: preview.thread_id,
      cwd: preview.cwd,
      model_provider: preview.model_provider,
      handoff_kind: "owner-confirmed-idle-manual",
      handoff_valid: true,
      expires_at: Date.now() + 20 * 60 * 1e3,
      global_fencing: false,
      created_at: now(),
    };
    this.store.put("thread-binding", binding.id, binding);
    this.threadPreviews.delete(preview.preview_id);
    this.codex.status = {
      ...this.codex.status,
      existing_chat_control:
        "manual_handoff_only; other desktop clients are not fenced",
    };
    this.event("thread.adopted", { binding });
    return {
      thread_binding: binding,
      notice: preview.warning,
    };
  }
  async route(projectId, payload) {
    const project = this.projects.get(projectId),
      workspace = await this.projects.workspace(projectId);
    if (this.codex.skills) {
      const catalog = await this.codex.skills([project.root]);
      await this.skills.adoptHostCatalog(catalog.entries, [project.root]);
    }
    return {
      routing: proposeRoute({
        project,
        workspace,
        skills: await this.skills.list(),
        payload,
        controllerAvailable: !!this.controllers,
      }),
    };
  }
  async universalSource() {
    const catalog = await this.skills.list();
    const canonicalSource = catalog.entries.find(
      (x) => x.name === "atelier-orchestrator" && x.managed_by === "optional",
    );
    const installed = [...this.skills.hostSources.values()].find(
      (x) =>
        x.name === "atelier-orchestrator" &&
        x.enabled !== false &&
        x.execution_supported === true &&
        x.discovery_status === "host_discovered",
    );
    fail(
      installed,
      "CAPABILITY_UNVERIFIED",
      "Connect Codex and discover the installed orchestration skill before universal task preparation",
      409,
    );
    fail(
      installed.source_sha256 === canonicalSource?.source_sha256,
      "SOURCE_DRIFT",
      "Installed orchestration source differs from this release; update and refresh discovery first",
      409,
    );
    return installed.source_id;
  }
  async prepare(projectId, payload, expected) {
    const project = this.projects.get(projectId),
      workspace = await this.projects.workspace(projectId);
    if (expected)
      fail(
        expected === workspace.project.revision,
        "REVISION_CONFLICT",
        "Native project changed; refresh the workspace",
        409,
      );
    const taskId = id("task"),
      epoch = this.store.get("settings", "owner").authority_epoch;
    const instructionManifest = await this.instructions.capture(
      project.root,
      this.codex.instructionSettings
        ? await this.codex.instructionSettings(project.root)
        : instructionSettings(),
    );
    let routing = null;
    let selected = payload.selected_skills ?? [];
    if (payload.universal_entry === true) {
      fail(
        Array.isArray(selected),
        "INVALID_INPUT",
        "selected_skills must be an array",
      );
      routing = (await this.route(projectId, payload)).routing;
      fail(
        routing.native_revision === workspace.project.revision,
        "SOURCE_DRIFT",
        "Native context changed during route preparation; refresh again",
        409,
      );
      const orchestratorSource = await this.universalSource();
      selected = [
        orchestratorSource,
        ...selected.filter(
          (x) => x !== orchestratorSource && x !== "atelier-orchestrator",
        ),
      ];
      if (payload.routing_sha256)
        fail(
          payload.routing_sha256 === routing.routing_sha256,
          "SOURCE_DRIFT",
          "The reviewed route or its inputs changed; inspect a fresh route",
          409,
        );
    }
    const selections = await this.skills.selections(selected, taskId);
    if (payload.planning_only === true)
      fail(
        (payload.scope ?? "read-only") === "read-only",
        "SCOPE_MISMATCH",
        "Constructor planning is read-only; creation/installation requires its own exact later approval",
        409,
      );
    const capsule = await compileContext({
      project,
      workspace,
      payload,
      taskId,
      authorityEpoch: epoch,
      instructionManifest,
    });
    const preferred = payload.output_locale;
    if (preferred !== undefined)
      fail(
        LOCALES.includes(preferred),
        "INVALID_INPUT",
        "Unsupported task output language",
      );
    const projectLocales = new Set();
    if (preferred === undefined) {
      for (const pin of capsule.original_sources) {
        if (
          pin.path !== ".appatelier/profile.json" &&
          !/(?:^|\/)project-context\.json$/.test(pin.path)
        )
          continue;
        const source = await readSource(project.root, pin.path);
        fail(
          source.sha256 === pin.sha256,
          "SOURCE_DRIFT",
          "The source of the project language changed. Prepare the task again.",
          409,
        );
        let settings;
        try {
          settings = parseStrictJson(source.text);
        } catch (error) {
          const declaredRequired = capsule.context_coverage.source_checks?.some(
            (check) => check.path === pin.path && check.required,
          );
          if (declaredRequired || !["INVALID_JSON", "DUPLICATE_JSON_KEY"].includes(error.code))
            throw error;
          continue;
        }
        if (
          ["app-atelier-profile/1", "codex-agents.project-context/1"].includes(
            settings?.schema_version,
          ) &&
          LOCALES.includes(settings.preferred_language)
        )
          projectLocales.add(settings.preferred_language);
      }
      fail(
        projectLocales.size <= 1,
        "CONTEXT_CONFLICT",
        "Pinned project settings specify different output languages. Choose an output language for this task or reconcile the sources.",
        409,
      );
    }
    capsule.output_locale = resolveLocale(
      preferred,
      projectLocales.values().next().value,
    );
    if (payload.thread_binding_id) {
      const binding = this.store.get(
        "thread-binding",
        text(payload.thread_binding_id, "thread_binding_id"),
      );
      fail(
        binding &&
          binding.project_id === projectId &&
          binding.handoff_valid !== false &&
          binding.expires_at > Date.now(),
        "SCOPE_MISMATCH",
        "Existing thread binding belongs to another project",
        409,
      );
      capsule.existing_thread = {
        binding_id: binding.id,
        thread_id: binding.thread_id,
        handoff_kind: binding.handoff_kind,
      };
      delete capsule.capsule_sha256;
      capsule.capsule_sha256 = digest(capsule);
    }
    capsule.selected_skills = selections;
    if (routing) {
      capsule.entry = {
        surface: "local-panel",
        universal: true,
        original_objective: capsule.objective,
      };
      capsule.routing = routing;
      capsule.original_result_acceptance = capsule.acceptance;
      capsule.maintenance = routing.maintenance;
      capsule.creation_scope = routing.creation_scope;
      capsule.execution_scope = routing.execution_scope;
      capsule.continuation = routing.continuation;
    }
    capsule.planning_only = payload.planning_only === true;
    delete capsule.capsule_sha256;
    capsule.capsule_sha256 = digest(capsule);
    const task = {
      id: taskId,
      project_id: projectId,
      objective: capsule.objective,
      acceptance: capsule.acceptance,
      scope: capsule.scope,
      status: "prepared",
      native_revision: capsule.native_revision,
      capsule,
      created_at: now(),
    };
    this.store.put("task", task.id, task);
    this.event("task.prepared", {
      task_id: task.id,
      project_id: projectId,
    });
    return {
      task: this.store.get("task", task.id),
      capsule,
    };
  }
  #requireUnquarantinedNativeThread(threadId) {
    if (!threadId) return;
    fail(
      !this.store.list("job").some((job) =>
        job.native_thread_identity_conflict &&
        [job.native_thread_requested_id, job.native_thread_acknowledged_id].includes(threadId),
      ),
      "OUTCOME_UNKNOWN",
      "This chat was named in an unresolved native thread identity conflict. Reconcile the exact requested and acknowledged chats before retrying",
      409,
    );
  }
  async dispatch(projectId, payload, expected, internal = {}) {
    fail(
      !this.closing && !this.maintenanceOperation,
      "SERVICE_STOPPING",
      "The service is stopping or performing isolated maintenance",
      409,
    );
    fail(
      !Object.hasOwn(payload, "resume_thread_id"),
      "SCOPE_MISMATCH",
      "Raw thread overrides are not accepted",
      409,
    );
    fail(
      this.activeOptionalUpdates().length === 0,
      "OUTCOME_UNKNOWN",
      "Verify or roll back the unknown global skill update before task dispatch",
      409,
    );
    const task = this.task(payload.task_id, projectId),
      project = this.projects.get(task.project_id);
    fail(
      !this.activeNativeControllers().some(
        (row) =>
          !row.root ||
          isWithin(row.root, project.root) ||
          isWithin(project.root, row.root),
      ),
      "OUTCOME_UNKNOWN",
      "Reconcile the overlapping native controller before dispatching another task",
      409,
    );
    fail(
      !task.input_cache_pruned && !task.requires_prepare,
      "TASK_NOT_READY",
      "Task inputs were pruned or revoked; prepare a new capsule before any host action",
      409,
    );
    fail(
      task.status === "prepared",
      "TASK_NOT_READY",
      "Prepare a new capsule before dispatch/resume",
      409,
    );
    fail(
      task.capsule.instruction_manifest?.schema_version ===
        "atelier.governing-instructions/1",
      "TASK_NOT_READY",
      "Legacy task is missing governing-instruction pins; prepare a new capsule",
      409,
    );
    fail(
      task.capsule.instruction_manifest.root === project.root,
      "SCOPE_MISMATCH",
      "Governing instruction root differs from this project",
      409,
    );
    const epoch = this.store.get("settings", "owner").authority_epoch;
    fail(
      task.capsule.authority_epoch === epoch,
      "SCOPE_MISMATCH",
      "Restored task authority is invalid; prepare again",
      409,
    );
    const resumeThreadId =
      internal.resumeThreadId ?? task.capsule.existing_thread?.thread_id;
    this.#requireUnquarantinedNativeThread(resumeThreadId);
    const candidate = {
      id: id("job"),
      project_id: project.id,
      project_root: project.root,
      task_id: task.id,
      objective: task.objective,
      scope: task.scope,
      status: "gating",
      capsule_sha256: task.capsule.capsule_sha256,
      native_revision: task.native_revision,
      owned_by: this.instanceId,
      thread_id: resumeThreadId ?? null,
      native_thread_requested_id: resumeThreadId ?? null,
      turn_id: null,
      host_dispatch_started: false,
      created_at: now(),
      events: [],
      outputs: [],
      pending_requests: [],
    };
    // The writer/task reservation is one SQLite transaction before any asynchronous gate.
    const job = this.store.reserveJob(
      task.id,
      project.id,
      candidate,
      ACTIVE_JOB_STATES,
      epoch,
    );
    this.event("job.created", { job });
    try {
      await this.instructions.verify(task.capsule.instruction_manifest);
      await this.codex.connect();
      await this.instructions.verify(
        task.capsule.instruction_manifest,
        this.codex.instructionSettings
          ? await this.codex.instructionSettings(project.root)
          : task.capsule.instruction_manifest.settings,
      );
      fail(
        this.codex.status.auth_mode === undefined ||
          this.codex.status.auth_mode === "chatgpt",
        "BILLING_AUTHORITY_REQUIRED",
        "This local route requires the existing ChatGPT plan. API/cloud billing needs a separately approved resource route",
        409,
      );
      await this.skills.verifySelections(task.capsule.selected_skills, task.id);
      const workspace = await this.projects.workspace(project.id);
      fail(
        workspace.project.revision === task.native_revision &&
          (!expected || expected === task.native_revision),
        "SOURCE_DRIFT",
        "Project changed after preparation; prepare again",
        409,
      );
      for (const pin of task.capsule.original_sources) {
        const source = await readSource(project.root, pin.path);
        fail(
          source.sha256 === pin.sha256,
          "SOURCE_DRIFT",
          `Input changed: ${pin.path}`,
          409,
        );
      }
      if (resumeThreadId) {
        const observed = await this.checkedThread(project.id, resumeThreadId);
        fail(
          observed.execution_context_available !== false,
          "CAPABILITY_UNVERIFIED",
          "The isolated executor cannot restore this native thread context; do not resume it from metadata alone",
          409,
        );
        fail(
          ["idle", "notLoaded"].includes(observed.host_status),
          "WRITER_CONFLICT",
          "Existing thread is active or unknown; complete its exact idle handoff first",
          409,
        );
      }
      if (task.capsule.existing_thread && !internal.resumeThreadId) {
        const binding = this.store.get(
          "thread-binding",
          task.capsule.existing_thread.binding_id,
        );
        fail(
          binding &&
            binding.handoff_valid !== false &&
            binding.expires_at > Date.now(),
          "SCOPE_MISMATCH",
          "Existing thread handoff expired; preview and hand off again",
          409,
        );
      }
      fail(
        this.store.get("task", task.id).status !== "paused",
        "TASK_PAUSED",
        "Task was paused during gate checks",
        409,
      );
      fail(
        !this.maintenanceOperation &&
          this.store.get("settings", "owner").authority_epoch ===
            task.capsule.authority_epoch,
        "SCOPE_MISMATCH",
        "Service authority changed during gate checks",
        409,
      );
      this.#requireUnquarantinedNativeThread(resumeThreadId);
      this.updateJob(job.id, { status: "dispatching" });
      let acknowledged = false;
      const recordThread = (response, policy) => {
        const thread = response?.thread;
        fail(
          typeof thread?.id === "string" && thread.id.length > 0,
          "HOST_PROTOCOL_ERROR",
          "Codex did not return a thread identity",
          502,
        );
        const conflict = !!resumeThreadId && thread.id !== resumeThreadId;
        const conflictReason = "Native resume acknowledged a different chat. Reconcile both exact chat identities before retrying";
        this.updateJob(job.id, {
          thread_id: resumeThreadId ?? thread.id,
          native_thread_acknowledged_id: thread.id,
          native_thread_acknowledged_session_id: thread.sessionId ?? null,
          ...(conflict ? {
            status: "outcome_unknown",
            native_thread_identity_conflict: true,
            native_thread_operation: "thread/resume",
            unknown_reason: conflictReason,
          } : {
            session_id: thread.sessionId ?? null,
            instruction_sources: response.instructionSources ?? [],
          }),
          requested_model: policy?.model ?? null,
          requested_reasoning_effort: policy?.effort ?? null,
          native_model_provider: response.modelProvider ?? null,
          native_model: response.model ?? null,
          native_reasoning_effort: response.reasoningEffort ?? null,
          native_thread_acknowledged: true,
        });
        acknowledged = true;
        fail(!conflict, "SCOPE_MISMATCH", conflictReason, 409, {
          operation: "thread/resume",
          outcome: "unknown",
          requested_thread_id: resumeThreadId,
          acknowledged_thread_id: thread.id,
        });
      };
      const started = resumeThreadId
        ? await this.codex.resume(
            resumeThreadId,
            project.root,
            task.capsule,
            recordThread,
          )
        : await this.codex.start(project.root, task.capsule, recordThread);
      if (!acknowledged) recordThread(started);
      const thread = started.thread;
      await this.instructions.verify(
        task.capsule.instruction_manifest,
        this.codex.instructionSettings
          ? await this.codex.instructionSettings(project.root)
          : task.capsule.instruction_manifest.settings,
      );
      const verifyTurnReadiness = () => {
        this.#requireUnquarantinedNativeThread(thread.id);
        fail(
          this.store.get("task", task.id).status !== "paused",
          "TASK_PAUSED",
          "The native chat is recorded and the task was paused before the turn",
          409,
        );
        fail(
          !this.maintenanceOperation &&
            this.store.get("settings", "owner").authority_epoch ===
              task.capsule.authority_epoch,
          "SCOPE_MISMATCH",
          "Service authority changed before the model turn",
          409,
        );
      };
      verifyTurnReadiness();
      const result = await this.codex.turn(thread.id, task.capsule, () => {
        verifyTurnReadiness();
        this.updateJob(job.id, {
          host_dispatch_started: true,
          host_dispatch_started_at: now(),
          expected_start_pending: true,
        });
      });
      const current = this.store.get("job", job.id);
      this.updateJob(job.id, {
        turn_id: result.turn?.id ?? current.turn_id,
        expected_start_pending: false,
        pending_host_events: [],
        pending_host_requests: [],
        status: current.status === "dispatching" ? "queued" : current.status,
      });
      for (const event of current.pending_host_events ?? [])
        this.#notification(event);
      for (const request of current.pending_host_requests ?? [])
        this.#request(request);
      const remaining = Math.max(
        0,
        Date.parse(job.created_at) +
          task.capsule.budget.deadline_seconds * 1000 -
          Date.now(),
      );
      const timer = setTimeout(() => {
        const latest = this.store.get("job", job.id);
        if (
          [
            "queued",
            "dispatching",
            "running",
            "awaiting_approval",
            "awaiting_input",
          ].includes(latest?.status)
        ) {
          this.updateJob(job.id, {
            status: "cancel_requested",
            interruption_intent: "cancel",
            deadline_reached: true,
            ...(["queued", "dispatching"].includes(latest.status)
              ? { interrupt_on_start: this.instanceId }
              : {}),
          });
          if (latest.status !== "queued" && latest.status !== "dispatching")
            this.codex.interrupt(latest.thread_id, latest.turn_id).catch(() =>
              this.updateJob(job.id, {
                status: "outcome_unknown",
                unknown_reason: "Deadline interruption response unknown",
              }),
            );
        }
      }, remaining);
      timer.unref();
      this.timers.set(job.id, timer);
      return { job: this.store.get("job", job.id) };
    } catch (error) {
      const current = this.store.get("job", job.id);
      const nativeOperation = ["thread/start", "thread/resume"].includes(
        error.details?.operation,
      )
        ? error.details.operation
        : null;
      const threadOutcomeUnknown =
        nativeOperation && error.details.outcome === "unknown";
      if (
        !["completed", "cancelled", "failed", "paused"].includes(current.status)
      )
        this.updateJob(job.id, {
          status:
            current.host_dispatch_started || threadOutcomeUnknown
              ? "outcome_unknown"
              : error.code === "TASK_PAUSED"
                ? "paused"
                : "failed",
          error: publicError(error),
          ...(nativeOperation ? { native_thread_operation: nativeOperation } : {}),
          unknown_reason: current.native_thread_identity_conflict
            ? current.unknown_reason
            : current.host_dispatch_started
              ? "A turn request may have reached the host; reconcile before retrying"
              : threadOutcomeUnknown
                ? "A native thread request may have reached Codex. Reconcile the thread before retrying."
                : null,
        });
      throw error;
    }
  }
  async continueTask(projectId, payload, expected) {
    const task = this.task(payload.task_id, projectId);
    fail(
      !task.input_cache_pruned && !task.requires_prepare,
      "TASK_NOT_READY",
      "Task inputs were pruned or revoked; prepare a new capsule before continuing",
      409,
    );
    const last = this.store.list("job").find((x) => x.task_id === task.id);
    this.#requireUnquarantinedNativeThread(last?.thread_id);
    fail(
      last && ["paused", "cancelled", "failed"].includes(last.status),
      "TASK_NOT_READY",
      "Continue only a paused/cancelled/failed task after its outcome is reconciled",
      409,
    );
    fail(
      task.status === "paused" || task.status === "dispatched",
      "TASK_NOT_READY",
      "This task cannot be continued",
      409,
    );
    this.store.put("task", task.id, {
      ...task,
      status: "prepared",
    });
    return this.dispatch(projectId, payload, expected, {
      resumeThreadId: last.thread_id ?? undefined,
    });
  }
  #unconfirmedInterruption(job) {
    // Carry forward a known legacy request before replacing the observed phase.
    const fields = { interrupt_on_start: null };
    if (!job.interruption_intent && job.status === "pause_pending")
      fields.interruption_intent = "pause";
    else if (!job.interruption_intent && job.status === "cancel_requested")
      fields.interruption_intent = "cancel";
    return fields;
  }
  #pendingInterruption(job) {
    if (job.interruption_intent === "pause") return "pause_pending";
    if (job.interruption_intent === "cancel") return "cancel_requested";
    if (job.status === "pause_pending") return "pause_pending";
    if (job.status === "cancel_requested" || job.deadline_reached)
      return "cancel_requested";
    if (!job.task_id) return null;
    const task = this.store.get("task", job.task_id);
    return task?.project_id === job.project_id && task.status === "paused"
      ? "pause_pending"
      : null;
  }
  #notification(event) {
    const params = event.params ?? {};
    if (params.item?.type === "reasoning") return;
    const threadId = params.threadId ?? params.thread?.id;
    const job = this.store
      .list("job")
      .find(
        (x) =>
          x.thread_id === threadId &&
          !x.native_thread_identity_conflict &&
          ACTIVE_JOB_STATES.includes(x.status),
      );
    if (!job) return;
    const eventTurnId = params.turnId ?? params.turn?.id;
    const turnSpecific =
      event.method.startsWith("turn/") || event.method.startsWith("item/");
    if (turnSpecific) {
      if (!job.turn_id) {
        if (job.host_dispatch_started && job.expected_start_pending)
          this.updateJob(job.id, {
            pending_host_events: [
              ...(job.pending_host_events ?? []),
              redact(event),
            ].slice(-120),
          });
        return;
      }
      if (!eventTurnId || eventTurnId !== job.turn_id) return;
    }
    const safeParams = {
      threadId: params.threadId,
      turnId: params.turnId,
      delta:
        typeof params.delta === "string"
          ? params.delta.slice(0, 1200)
          : undefined,
      turn: params.turn
        ? {
            id: params.turn.id,
            status: params.turn.status,
            error: redact(params.turn.error),
          }
        : undefined,
      item: params.item
        ? {
            id: params.item.id,
            type: params.item.type,
            text:
              typeof params.item.text === "string"
                ? params.item.text.slice(0, 4e3)
                : undefined,
          }
        : undefined,
      requestId: params.requestId,
    };
    const entry = {
      method: event.method,
      params: safeParams,
      observed_at: event.observed_at,
    };
    const events = [...(job.events ?? []), entry].slice(-100);
    const delta = { events };
    if (event.method === "turn/started") {
      delta.host_dispatch_started = true;
      delta.turn_id = params.turn?.id;
      delta.status = this.#pendingInterruption(job) ?? "running";
      if (
        job.status !== "outcome_unknown" &&
        job.interrupt_on_start === this.instanceId
      ) {
        delta.interrupt_on_start = null;
        queueMicrotask(async () => {
          if (this.closing) return;
          const current = this.store.get("job", job.id);
          if (
            current?.thread_id !== threadId ||
            current.turn_id !== eventTurnId ||
            !["pause_pending", "cancel_requested"].includes(current.status)
          )
            return;
          try {
            await this.codex.interrupt(threadId, eventTurnId);
          } catch (error) {
            if (this.closing) return;
            const latest = this.store.get("job", job.id);
            if (
              latest?.thread_id === threadId &&
              latest.turn_id === eventTurnId &&
              ["pause_pending", "cancel_requested"].includes(latest.status)
            )
              this.updateJob(job.id, {
                status: "outcome_unknown",
                unknown_reason:
                  "Requested startup cancellation could not be confirmed",
                error: publicError(error),
              });
          }
        });
      }
    }
    if (event.method === "item/agentMessage/delta") {
      const output = (job.output_text ?? "") + (params.delta ?? "");
      delta.output_text = output.slice(-16e4);
    }
    if (
      event.method === "item/completed" &&
      params.item?.type === "agentMessage"
    ) {
      delta.output_text = params.item.text ?? job.output_text ?? "";
      delta.outputs = [
        ...(job.outputs ?? []),
        {
          id: params.item.id,
          type: "agentMessage",
          text: (params.item.text ?? "").slice(-2e4),
          observed_at: now(),
        },
      ].slice(-6);
    }
    if (event.method === "serverRequest/resolved")
      delta.pending_requests = (job.pending_requests ?? []).filter(
        (x) => String(x.id) !== String(params.requestId),
      );
    if (event.method === "turn/completed") {
      const status = params.turn?.status;
      delta.status =
        status === "completed"
          ? "completed"
          : status === "interrupted"
            ? this.#pendingInterruption(job) === "pause_pending"
              ? "paused"
              : "cancelled"
            : "failed";
      delta.completed_at = now();
      delta.host_status = status;
      delta.error = params.turn?.error ?? null;
      delta.pending_requests = [];
      clearTimeout(this.timers.get(job.id));
      this.timers.delete(job.id);
    }
    this.updateJob(job.id, delta);
  }
  #request(request) {
    const job = this.store
      .list("job")
      .find(
        (x) =>
          x.thread_id === request.params?.threadId &&
          !x.native_thread_identity_conflict &&
          ACTIVE_JOB_STATES.includes(x.status),
      );
    if (!job) {
      try {
        this.codex.respond(request.id, "decline");
      } catch {}
      return;
    }
    if (!job.turn_id) {
      if (job.host_dispatch_started && job.expected_start_pending)
        this.updateJob(job.id, {
          pending_host_requests: [
            ...(job.pending_host_requests ?? []),
            redact(request),
          ].slice(-20),
        });
      else
        try {
          this.codex.respond(request.id, "decline");
        } catch {}
      return;
    }
    if (request.params?.turnId !== job.turn_id) {
      try {
        this.codex.respond(request.id, "decline");
      } catch {}
      return;
    }
    const isInput = request.method === "item/tool/requestUserInput";
    const pending = {
      ...request,
      can_accept: false,
      scope_notice:
        "Privilege expansion is outside this task; decline/cancel or prepare a new exact scope. Tool questions may be answered.",
    };
    this.updateJob(job.id, {
      status: isInput ? "awaiting_input" : "awaiting_approval",
      pending_requests: [...(job.pending_requests ?? []), pending],
    });
  }
  async respond(job, payload) {
    const request = (job.pending_requests ?? []).find(
      (x) => String(x.id) === String(payload.request_id),
    );
    fail(
      request,
      "APPROVAL_EXPIRED",
      "Request is no longer pending for this job",
      409,
    );
    fail(
      request.params?.threadId === job.thread_id &&
        (!request.params.turnId || request.params.turnId === job.turn_id),
      "SCOPE_MISMATCH",
      "Request does not match the current thread/turn",
      409,
    );
    if (payload.decision === "accept")
      fail(
        request.can_accept === true,
        "SCOPE_MISMATCH",
        "This privilege expansion is outside the prepared task; prepare an exact new scope",
        409,
      );
    const result = this.codex.respond(payload.request_id, payload.decision);
    return {
      response: result,
      job: this.updateJob(job.id, {
        pending_requests: job.pending_requests.filter(
          (x) => String(x.id) !== String(payload.request_id),
        ),
        status: "running",
      }),
    };
  }
  async reconcile(job) {
    if (job.native_thread_identity_conflict)
      fail(
        false,
        "OUTCOME_UNKNOWN",
        "No trusted native turn identity was recorded. Inspect the requested and acknowledged chats in Codex to reconcile the mismatch",
        409,
        {
          requested_thread_id: job.native_thread_requested_id,
          acknowledged_thread_id: job.native_thread_acknowledged_id,
        },
      );
    if (TERMINAL_JOB_STATES.includes(job.status) || job.status === "paused")
      return { job };
    fail(
      job.thread_id,
      "HOST_NOT_FOUND",
      "No host thread identity was recorded",
      409,
    );
    let hostState = "not_returned";
    let turnStatus = "not_returned";
    if (job.turn_id) {
      try {
        const { thread } = await this.boundThread(
          job.project_id,
          job.thread_id,
        );
        hostState = thread.status?.type ?? thread.status ?? "not_returned";
        const turn = this.codex.readTurn
          ? await this.codex.readTurn(job.thread_id, job.turn_id)
          : thread.turns?.find((x) => x.id === job.turn_id);
        if (turn?.id === job.turn_id)
          turnStatus = turn.status ?? "not_returned";
      } catch (error) {
        if (!(error instanceof ServiceError) || error.code === "SCOPE_MISMATCH")
          throw error;
        turnStatus = "history_unconfirmed";
      }
    }
    const current = this.job(job.id, job.project_id);
    fail(
      current.thread_id === job.thread_id && current.turn_id === job.turn_id,
      "SOURCE_DRIFT",
      "The job's thread/turn changed while reading native history",
      409,
    );
    // A live event may have settled this job while the history request was in flight.
    if (
      TERMINAL_JOB_STATES.includes(current.status) ||
      current.status === "paused"
    )
      return { job: current };
    let status = "outcome_unknown";
    const pendingInterruption = this.#pendingInterruption(current);
    if (turnStatus === "completed") status = "completed";
    else if (turnStatus === "interrupted")
      status = pendingInterruption === "pause_pending" ? "paused" : "cancelled";
    else if (turnStatus === "failed") status = "failed";
    else if (turnStatus === "inProgress" && hostState === "active")
      status = pendingInterruption ?? "running";
    const terminal =
      TERMINAL_JOB_STATES.includes(status) || status === "paused";
    if (terminal) {
      clearTimeout(this.timers.get(job.id));
      this.timers.delete(job.id);
    }
    return {
      job: this.updateJob(job.id, {
        status,
        reconciled_at: now(),
        host_observation: {
          status: hostState,
          turn_status: turnStatus,
        },
        ...(terminal ? { host_status: turnStatus, pending_requests: [] } : {}),
        unknown_reason:
          status === "outcome_unknown"
            ? job.turn_id
              ? "No authoritative exact turn outcome returned; do not replay"
              : "No exact native turn identity was recorded; do not replay"
            : null,
      }),
    };
  }
  async recordDecision(projectId, payload) {
    const job = this.job(payload.job_id, projectId);
    fail(
      payload.subject_capsule_sha256 === job.capsule_sha256,
      "SOURCE_DRIFT",
      "Decision must pin the exact current task capsule",
      409,
    );
    const decision = {
      id: id("decision"),
      project_id: job.project_id,
      job_id: job.id,
      subject_capsule_sha256: job.capsule_sha256,
      text: text(payload.text, "decision", 3, 12e3),
      actor: "local-owner",
      scope: "service-task-review-only",
      created_at: now(),
    };
    this.store.put("decision", decision.id, decision);
    this.event("decision.recorded", { decision });
    return {
      decision,
      native_product_written: false,
    };
  }
  async recordEvidence(projectId, payload) {
    const job = this.job(payload.job_id, projectId),
      task = this.task(job.task_id, job.project_id);
    fail(
      payload.subject_capsule_sha256 === job.capsule_sha256,
      "EVIDENCE_STALE",
      "Evidence must retain exact observed subject pins",
      409,
    );
    fail(
      [
        "source",
        "code",
        "integration",
        "device",
        "human",
        "operational",
      ].includes(payload.axis),
      "EVIDENCE_AXIS_MISMATCH",
      "Select a supported evidence axis",
    );
    if (payload.axis !== "source")
      fail(
        job.status === "completed",
        "EVIDENCE_AXIS_MISMATCH",
        "Runtime evidence requires a completed actual execution",
        409,
      );
    const file = await readSource(
      this.projects.get(job.project_id).root,
      text(payload.proof_path, "proof_path", 1, 4096),
    );
    fail(
      file.sha256 === payload.proof_sha256,
      "EVIDENCE_STALE",
      "Proof bytes do not match the supplied digest",
      409,
    );
    for (const pin of task.capsule.original_sources) {
      const current = await readSource(task.capsule.root, pin.path);
      fail(
        current.sha256 === pin.sha256,
        "EVIDENCE_STALE",
        "Task dependencies changed after observation",
        409,
      );
    }
    const evidence = {
      id: id("evidence"),
      project_id: job.project_id,
      job_id: job.id,
      subject_capsule_sha256: job.capsule_sha256,
      axis: payload.axis,
      proof_path: file.path,
      proof_sha256: file.sha256,
      method: text(payload.method, "method", 3, 4e3),
      environment: text(payload.environment, "environment", 2, 4e3),
      result:
        payload.result === "pass"
          ? "pass"
          : payload.result === "fail"
            ? "fail"
            : "inconclusive",
      observer: "local-owner",
      observer_authenticated: false,
      independent_review: false,
      quality_certified: false,
      created_at: now(),
    };
    this.store.put("evidence", evidence.id, evidence);
    this.event("evidence.registered", { evidence });
    return {
      evidence,
      native_product_written: false,
    };
  }
  async backup() {
    fail(
      this.activeJobs().length === 0 &&
        this.activeNativeControllers().length === 0 &&
        this.activeOptionalUpdates().length === 0,
      "OUTCOME_UNKNOWN",
      "Pause/reconcile active or unknown jobs before backing up",
      409,
    );
    const snapshot = this.store.export(),
      bytes = JSON.stringify(snapshot, null, 2);
    const backupId = id("backup");
    await atomicWrite(join(this.dataDir, "backups", `${backupId}.json`), bytes);
    const record = {
      id: backupId,
      path: join(this.dataDir, "backups", `${backupId}.json`),
      sha256: sha(bytes),
      bytes: Buffer.byteLength(bytes),
      created_at: now(),
      schema_version: snapshot.schema_version,
    };
    this.store.put("backup", backupId, record);
    return {
      backup_id: backupId,
      sha256: record.sha256,
      bytes: record.bytes,
      scope: "service-only; product files and external effects excluded",
    };
  }
  async restorePreview(payload) {
    const backup = this.store.get(
      "backup",
      text(payload.backup_id, "backup_id"),
    );
    fail(backup, "BACKUP_NOT_FOUND", "Backup not found", 404);
    const bytes = await readFile(backup.path);
    fail(
      sha(bytes) === backup.sha256,
      "SOURCE_DRIFT",
      "Backup bytes changed",
      409,
    );
    const snapshot = parseStrictJson(bytes.toString(), 32 * 1024 * 1024);
    fail(
      snapshot.schema_version === "agent-atelier.backup/1",
      "UNSUPPORTED_SCHEMA",
      "Unsupported backup format",
      409,
    );
    for (const key of ["records", "commands", "events"])
      fail(
        Array.isArray(snapshot[key]) && snapshot[key].length <= 1e5,
        "INVALID_BACKUP",
        "Invalid bounded backup table",
      );
    for (const row of snapshot.records) {
      fail(
        typeof row.kind === "string" &&
          typeof row.id === "string" &&
          typeof row.data === "string" &&
          Number.isSafeInteger(row.revision) &&
          row.revision > 0,
        "INVALID_BACKUP",
        "Invalid backup record",
      );
      parseStrictJson(row.data);
    }
    for (const row of snapshot.commands) {
      fail(
        typeof row.id === "string" &&
          typeof row.digest === "string" &&
          typeof row.data === "string",
        "INVALID_BACKUP",
        "Invalid backup command receipt",
      );
      parseStrictJson(row.data);
    }
    for (const row of snapshot.events) {
      fail(
        Number.isSafeInteger(row.sequence) &&
          row.sequence > 0 &&
          typeof row.event === "string" &&
          typeof row.data === "string",
        "INVALID_BACKUP",
        "Invalid backup event",
      );
      parseStrictJson(row.data);
    }
    const preview = {
      backup_id: backup.id,
      sha256: backup.sha256,
      restore_policy:
        "Restore settings and missing records; retain newer durable records and receipts; invalidate all dispatch/handoff authority",
      counts: {
        records: snapshot.records.length,
        commands: snapshot.commands.length,
        events: snapshot.events.length,
      },
      current_counts: {
        projects: this.store.list("project").length,
        jobs: this.store.list("job").length,
      },
      dispatch_authority_after_restore: "invalidated; prepare new tasks",
      scope: "service-only",
      expires_at: Date.now() + 3e5,
    };
    this.previewRestores.set(backup.id, preview);
    return preview;
  }
  invalidatePrivatePreviews() {
    this.portfolio.invalidate();
    this.controllers.clear();
    this.optionalUpdates.clear();
    this.projects.previews.clear();
    this.threadPreviews.clear();
    this.previewRestores.clear();
    this.retention.previews.clear();
    this.retention.exportPreviews.clear();
    this.skills.hostSources.clear();
    this.codex.lastSkills = [];
  }
  async maintain(name, operation) {
    fail(
      !this.maintenanceOperation && !this.closing && !this.skills.busy,
      "WRITER_CONFLICT",
      "Another service or global skill maintenance operation is active",
      409,
    );
    fail(
      this.activeJobs().length === 0 &&
        (name === "native-controller-reconcile" ||
          this.activeNativeControllers().length === 0) &&
        (["optional-rollback", "native-controller-reconcile"].includes(name) ||
          this.activeOptionalUpdates().length === 0),
      "OUTCOME_UNKNOWN",
      "Finish or reconcile active/unknown jobs and native controller operations before maintenance",
      409,
    );
    this.maintenanceOperation = name;
    try {
      return await operation();
    } finally {
      this.maintenanceOperation = null;
    }
  }
  async restore(payload) {
    fail(
      !this.maintenanceOperation && !this.closing && !this.skills.busy,
      "WRITER_CONFLICT",
      "Another service maintenance operation is active",
      409,
    );
    fail(
      this.activeJobs().length === 0 &&
        this.activeNativeControllers().length === 0 &&
        this.activeOptionalUpdates().length === 0,
      "OUTCOME_UNKNOWN",
      "Reconcile all active/unknown jobs before restore",
      409,
    );
    this.maintenanceOperation = "restore";
    try {
      const preview = this.previewRestores.get(payload.backup_id);
      fail(
        preview &&
          preview.expires_at > Date.now() &&
          preview.sha256 === payload.sha256 &&
          payload.confirmed === true,
        "SCOPE_MISMATCH",
        "Confirm a current isolated restore preview and exact backup digest",
        409,
      );
      const backup = this.store.get("backup", payload.backup_id);
      const bytes = await readFile(backup.path);
      fail(
        sha(bytes) === preview.sha256,
        "SOURCE_DRIFT",
        "Backup changed after preview",
        409,
      );
      const snapshot = parseStrictJson(bytes.toString(), 32 * 1024 * 1024);
      await this.codex.close();
      if (this.historyCodex !== this.codex) await this.historyCodex.close();
      await this.integrationCodex?.close();
      await this.imageGeneration.close();
      const restoredEpoch = randomUUID();
      // Revocation and restored jobs become safe in the same SQLite commit as the restore.
      this.store.restore(
        snapshot,
        (kind, record) => {
          record = this.retention.sanitizeRestored(kind, record);
          if (record === null) return null;
          if (kind === "settings" && record.id === "owner")
            return {
              ...record,
              authority_epoch: restoredEpoch,
              restored_at: now(),
            };
          if (
            kind === "optional-update" &&
            ["pending", "outcome_unknown"].includes(record.status)
          )
            return {
              ...record,
              status: "outcome_unknown",
              unknown_reason:
                "Restored global skill update requires exact source verification; never replay automatically",
            };
          if (
            kind === "native-controller" &&
            ["pending", "outcome_unknown"].includes(record.status)
          )
            return {
              ...record,
              status: "outcome_unknown",
              unknown_reason:
                "Restored native controller requires authoritative reconciliation",
            };
          if (kind === "task")
            return { ...record, status: "restored_requires_preparation" };
          if (kind === "thread-binding")
            return { ...record, handoff_valid: false };
          if (kind === "job" && ACTIVE_JOB_STATES.includes(record.status))
            return {
              ...record,
              ...this.#unconfirmedInterruption(record),
              status: "outcome_unknown",
              unknown_reason:
                "Restored job requires authoritative reconciliation",
            };
          return record;
        },
        (event) =>
          this.retention.sanitizeRestoredEvent
            ? this.retention.sanitizeRestoredEvent(event)
            : event,
        (command) =>
          this.retention.sanitizeRestoredCommand
            ? this.retention.sanitizeRestoredCommand(command)
            : command,
      );
      this.invalidatePrivatePreviews();
      this.event("service.restored", { backup_id: payload.backup_id });
      return {
        status: "restored",
        backup_id: payload.backup_id,
        scope: "service-only",
        dispatch_authority: "invalidated",
        audit_receipts:
          "post-backup durable receipts preserved; historical records merged without overwriting newer records",
        product_files_changed: false,
      };
    } finally {
      this.maintenanceOperation = null;
    }
  }
  async close() {
    this.closing = true;
    for (const timer of this.timers.values()) clearTimeout(timer);
    for (const job of this.activeJobs())
      if (
        job.turn_id &&
        [
          "running",
          "awaiting_approval",
          "awaiting_input",
          "pause_pending",
          "cancel_requested",
        ].includes(job.status)
      ) {
        this.updateJob(job.id, {
          status: "outcome_unknown",
          unknown_reason:
            "Service stopping; reconcile the host turn before another attempt",
        });
        try {
          await this.codex.interrupt(job.thread_id, job.turn_id);
        } catch {}
      }
    await this.codex.close();
    if (this.historyCodex !== this.codex) await this.historyCodex.close();
    await this.integrationCodex?.close();
    await this.imageGeneration.close();
    this.codex.removeAllListeners();
    this.store.close();
  }
}
