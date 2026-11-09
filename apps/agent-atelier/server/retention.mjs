import { lstat, readdir, rm, readFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { ACTIVE_JOB_STATES } from "../shared/contracts.mjs";
import {
  atomicWrite,
  canonical,
  digest,
  fail,
  id,
  now,
  parseStrictJson,
  sha,
} from "./utils.mjs";

const DEFAULT_POLICY = Object.freeze({
  event_days: 30,
  history_days: 90,
  input_cache_days: 30,
  backup_days: 90,
  automatic: false,
  reviewed: false,
});
const DAY = 86_400_000;
const terminal = new Set(["completed", "failed", "cancelled"]);
const older = (value, days, at) =>
  days !== null &&
  Number.isFinite(Date.parse(value)) &&
  Date.parse(value) < at - days * DAY;
const identifier = (value) =>
  typeof value === "string" && /^[A-Za-z0-9_-]{1,180}$/.test(value);
const references = (
  value,
  ids,
  depth = 0,
  roots = [],
  rootHashes = new Set(),
) => {
  if (depth > 20) return false;
  if (typeof value === "string") {
    if (
      ids.has(value) ||
      roots.some((root) => value === root || value.startsWith(root + "/"))
    )
      return true;
    if (value.startsWith("/")) {
      let prefix = "";
      for (const part of value.split("/").filter(Boolean)) {
        prefix += "/" + part;
        if (rootHashes.has(sha(prefix))) return true;
      }
    }
    return false;
  }
  if (value && typeof value === "object")
    return Object.values(value).some((child) =>
      references(child, ids, depth + 1, roots, rootHashes),
    );
  return false;
};

/** Local service retention only. Native projects/provider copies are never deleted. */
export class RetentionManager {
  constructor({ store, dataDir, clock = () => Date.now() }) {
    this.store = store;
    this.dataDir = resolve(dataDir);
    this.clock = clock;
    this.previews = new Map();
    this.exportPreviews = new Map();
  }

  policy() {
    return {
      ...DEFAULT_POLICY,
      ...(this.store.get("settings", "owner")?.retention ?? {}),
    };
  }

  configure(payload) {
    fail(
      payload?.confirmed === true &&
        payload.policy &&
        typeof payload.policy === "object",
      "SCOPE_MISMATCH",
      "Review and confirm the service-only retention policy",
      409,
    );
    const result = { ...DEFAULT_POLICY, reviewed: true };
    for (const key of [
      "event_days",
      "history_days",
      "input_cache_days",
      "backup_days",
    ]) {
      const value = payload.policy[key];
      fail(
        value === null ||
          (Number.isSafeInteger(value) && value >= 1 && value <= 3650),
        "INVALID_INPUT",
        `${key} must be 1–3650 days or null to retain`,
      );
      result[key] = value;
    }
    fail(
      payload.policy.automatic !== true,
      "UNSUPPORTED_OPERATION",
      "This release uses explicit cleanup previews; no automatic TTL is claimed",
      409,
    );
    const settings = this.store.get("settings", "owner");
    this.store.put(
      "settings",
      "owner",
      { ...settings, retention: result },
      settings.record_revision,
    );
    return {
      policy: result,
      scope:
        "Service-owned history, indexes and caches only; cleanup remains explicit",
    };
  }

  assertIdle() {
    fail(
      !this.store
        .list("job")
        .some((job) => ACTIVE_JOB_STATES.includes(job.status)),
      "WRITER_CONFLICT",
      "Reconcile or finish active/unknown jobs before cleanup",
      409,
    );
  }

  async file(relative) {
    fail(
      typeof relative === "string" &&
        !relative.startsWith("/") &&
        !relative
          .split("/")
          .some((part) => !part || part === ".." || part === "."),
      "OUTSIDE_ROOT",
      "Invalid service cache path",
      403,
    );
    fail(
      ["task-inputs", "codex-logs", "backups"].includes(relative.split("/")[0]),
      "OUTSIDE_ROOT",
      "Only service-owned cache/log/backup paths are eligible",
      403,
    );
    const path = join(this.dataDir, relative);
    let current = this.dataDir;
    for (const part of relative.split("/")) {
      current = join(current, part);
      try {
        fail(
          !(await lstat(current)).isSymbolicLink(),
          "OUTSIDE_ROOT",
          "Linked cleanup path rejected",
          403,
        );
      } catch (error) {
        if (error.code === "ENOENT") return null;
        throw error;
      }
    }
    let count = 0,
      bytes = 0;
    const entries = [];
    const visit = async (target) => {
      const stat = await lstat(target);
      fail(
        !stat.isSymbolicLink(),
        "OUTSIDE_ROOT",
        "Linked cleanup entry rejected",
        403,
      );
      fail(
        ++count <= 10_000,
        "CAPACITY_LIMIT",
        "Cleanup tree is too large for one preview",
        409,
      );
      if (stat.isDirectory())
        for (const name of (await readdir(target)).sort())
          await visit(join(target, name));
      else {
        fail(
          stat.isFile(),
          "OUTSIDE_ROOT",
          "Unexpected special cache entry",
          403,
        );
        bytes += stat.size;
        fail(
          stat.size <= 32 * 1024 * 1024 && bytes <= 128 * 1024 * 1024,
          "CAPACITY_LIMIT",
          "Cleanup preview exceeds its bounded content scan",
          409,
        );
        entries.push({
          path: target.slice(path.length),
          size: stat.size,
          mtime_ms: stat.mtimeMs,
          sha256: sha(await readFile(target)),
        });
      }
    };
    await visit(path);
    const stat = await lstat(path);
    return {
      relative,
      bytes,
      files: count,
      mtime_ms: stat.mtimeMs,
      directory: stat.isDirectory(),
      contents_sha256: digest(entries),
    };
  }

  async plan(payload = {}, at = this.clock()) {
    this.assertIdle();
    const policy = this.policy();
    fail(
      policy.reviewed ||
        payload.forget_project_ids?.length ||
        payload.forget_job_ids?.length,
      "SCOPE_MISMATCH",
      "Choose retention durations or explicit service history to forget first",
      409,
    );
    const projectIds = payload.forget_project_ids ?? [],
      explicitJobIds = payload.forget_job_ids ?? [];
    for (const list of [projectIds, explicitJobIds])
      fail(
        Array.isArray(list) && list.length <= 100 && list.every(identifier),
        "INVALID_INPUT",
        "Expected bounded service record IDs",
      );
    for (const value of projectIds)
      fail(
        this.store.get("project", value),
        "NOT_FOUND",
        "Project binding not found",
        404,
      );
    const tasks = this.store.list("task");
    fail(
      !tasks.some(
        (task) => projectIds.includes(task.project_id) && task.paused,
      ),
      "WRITER_CONFLICT",
      "Paused tasks must be resolved before forgetting a project binding",
      409,
    );
    const taskMap = new Map(tasks.map((task) => [task.id, task]));
    const jobIds = new Set(),
      cacheTasks = new Set();
    for (const job of this.store.list("job")) {
      const task = taskMap.get(job.task_id);
      const explicit =
        explicitJobIds.includes(job.id) || projectIds.includes(job.project_id);
      if (explicit)
        fail(
          terminal.has(job.status) && !task?.paused,
          "WRITER_CONFLICT",
          "Unfinished/paused work cannot be forgotten through retention",
          409,
        );
      const end = job.completed_at ?? job.finished_at ?? job.updated_at;
      if (terminal.has(job.status) && !task?.paused) {
        if (explicit || older(end, policy.history_days, at)) jobIds.add(job.id);
        if (explicit || older(end, policy.input_cache_days, at))
          if (task && identifier(task.id)) cacheTasks.add(task.id);
      }
    }
    for (const value of explicitJobIds)
      fail(this.store.get("job", value), "NOT_FOUND", "Job not found", 404);
    const forgottenTasks = new Set(
      this.store
        .list("job")
        .filter((job) => jobIds.has(job.id))
        .map((job) => job.task_id),
    );
    for (const task of tasks)
      if (projectIds.includes(task.project_id)) {
        forgottenTasks.add(task.id);
        if (identifier(task.id)) cacheTasks.add(task.id);
      }
    const ids = new Set([...projectIds, ...jobIds, ...forgottenTasks]);
    const roots = projectIds
      .map((projectId) => this.store.get("project", projectId).root)
      .filter((root) => typeof root === "string");
    const candidates = this.store.db
      .prepare("SELECT kind,id,data FROM records ORDER BY kind,id")
      .all()
      .filter(
        (row) =>
          !["settings", "backup"].includes(row.kind) &&
          !row.kind.startsWith("privacy-"),
      );
    fail(
      candidates.length <= 20_000,
      "CAPACITY_LIMIT",
      "Too many records for one cleanup preview",
      409,
    );
    const dependent = new Map();
    let changed = true;
    while (changed) {
      changed = false;
      for (const row of candidates) {
        const key = row.kind + ":" + row.id;
        if (
          !dependent.has(key) &&
          (ids.has(row.id) ||
            references(parseStrictJson(row.data), ids, 0, roots))
        ) {
          dependent.set(key, {
            kind: row.kind,
            id: row.id,
            sha256: sha(row.data),
          });
          if (!ids.has(row.id)) {
            ids.add(row.id);
            changed = true;
          }
        }
      }
    }
    const recordRows = [...dependent.values()].sort((a, b) =>
      (a.kind + a.id).localeCompare(b.kind + b.id),
    );
    const receipts = this.store.db
      .prepare("SELECT * FROM commands ORDER BY id")
      .all()
      .filter((row) => {
        const value = parseStrictJson(row.data);
        return (
          !["prepared", "dispatching"].includes(row.status) &&
          (older(row.updated_at, policy.history_days, at) ||
            references(value, ids, 0, roots))
        );
      });
    const events = this.store.db
      .prepare("SELECT * FROM events ORDER BY sequence")
      .all()
      .filter(
        (row) =>
          older(row.created_at, policy.event_days, at) ||
          references(parseStrictJson(row.data), ids, 0, roots),
      );
    const files = [];
    for (const taskId of cacheTasks) {
      const file = await this.file(`task-inputs/${taskId}`);
      if (file) files.push(file);
    }
    const backups = this.store
      .list("backup")
      .sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
    const backupIds = [];
    for (const backup of backups.slice(2))
      if (
        identifier(backup.id) &&
        older(backup.created_at, policy.backup_days, at)
      ) {
        const file = await this.file(`backups/${backup.id}.json`);
        if (file) files.push(file);
        backupIds.push(backup.id);
      }
    let logs = [];
    try {
      logs = await readdir(join(this.dataDir, "codex-logs"), {
        withFileTypes: true,
      });
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    for (const entry of logs)
      if (entry.isFile()) {
        const file = await this.file(`codex-logs/${entry.name}`);
        if (
          file &&
          policy.event_days !== null &&
          file.mtime_ms < at - policy.event_days * DAY
        )
          files.push(file);
      }
    files.sort((a, b) => a.relative.localeCompare(b.relative));
    const subject = {
      policy,
      record_rows: recordRows,
      root_hashes: roots.map(sha).sort(),
      project_ids: projectIds.slice().sort(),
      job_ids: [...jobIds].sort(),
      task_ids: [...forgottenTasks].sort(),
      cache_tasks: [...cacheTasks].sort(),
      backup_ids: backupIds.sort(),
      command_rows: receipts
        .map((row) => ({
          id: row.id,
          digest: row.digest,
          data_sha256: digest(row.data),
        }))
        .sort((a, b) => a.id.localeCompare(b.id)),
      event_rows: events.map((row) => ({
        sequence: row.sequence,
        digest: digest(row.data),
      })),
      files,
    };
    return { ...subject, subject_sha256: digest(subject), at };
  }

  async preview(payload = {}) {
    const plan = await this.plan(payload),
      previewId = id("cleanup");
    this.previews.set(previewId, {
      plan,
      payload,
      expires_at: this.clock() + 5 * 60_000,
    });
    return {
      preview_id: previewId,
      sha256: plan.subject_sha256,
      policy: plan.policy,
      counts: {
        associated_records: plan.record_rows.length,
        projects: plan.project_ids.length,
        jobs: plan.job_ids.length,
        tasks: plan.task_ids.length,
        input_caches: plan.cache_tasks.length,
        events: plan.event_rows.length,
        receipts_redacted: plan.command_rows.length,
        backups: plan.backup_ids.length,
        files: plan.files.reduce((sum, file) => sum + file.files, 0),
        bytes: plan.files.reduce((sum, file) => sum + file.bytes, 0),
      },
      scope:
        "Service projections/history/cache only. Native projects and provider copies untouched. Backups follow their separate retention, with the newest two preserved. This is not secure physical erasure.",
      pending_restore_filter:
        "Forgotten record tombstones prevent logical revival from a service backup",
    };
  }

  async apply(payload) {
    const preview = this.previews.get(payload?.preview_id);
    fail(
      payload?.confirmed === true &&
        preview &&
        preview.expires_at > this.clock() &&
        preview.plan.subject_sha256 === payload.sha256,
      "SCOPE_MISMATCH",
      "Confirm a current cleanup preview and exact digest",
      409,
    );
    const current = await this.plan(preview.payload, preview.plan.at);
    fail(
      current.subject_sha256 === preview.plan.subject_sha256,
      "REVISION_CONFLICT",
      "Cleanup targets changed; preview again",
      409,
    );
    const plan = preview.plan;
    this.store.transaction(() => {
      for (const row of plan.record_rows) {
        const kind = row.kind,
          recordId = row.id;
        const tombstone = {
          id: `${kind}:${recordId}`,
          kind,
          record_id: recordId,
          forgotten_at: now(),
        };
        this.store.db
          .prepare(
            "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('privacy-tombstone',?,?,1,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=records.revision+1,updated_at=excluded.updated_at",
          )
          .run(tombstone.id, canonical(tombstone), now());
        this.store.db
          .prepare("DELETE FROM records WHERE kind=? AND id=?")
          .run(kind, recordId);
      }
      for (const row of plan.command_rows)
        this.store.db
          .prepare(
            "UPDATE commands SET data=?,status='forgotten',updated_at=? WHERE id=? AND digest=?",
          )
          .run(
            canonical({
              command_id: row.id,
              status: "forgotten",
              content_removed: true,
              replay_allowed: false,
            }),
            now(),
            row.id,
            row.digest,
          );
      for (const row of plan.event_rows)
        this.store.db
          .prepare("DELETE FROM events WHERE sequence=?")
          .run(row.sequence);
      for (const recordId of plan.backup_ids)
        this.store.db
          .prepare("DELETE FROM records WHERE kind='backup' AND id=?")
          .run(recordId);
      const eventCutoff =
        plan.policy.event_days === null
          ? null
          : new Date(plan.at - plan.policy.event_days * DAY).toISOString();
      const privacy = this.store.get("privacy-policy", "owner") ?? {};
      const cutoff =
        [privacy.event_cutoff, eventCutoff].filter(Boolean).sort().at(-1) ??
        null;
      this.store.db
        .prepare(
          "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('privacy-policy','owner',?,1,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=records.revision+1,updated_at=excluded.updated_at",
        )
        .run(canonical({ id: "owner", event_cutoff: cutoff }), now());
      for (const hash of plan.root_hashes) {
        const key = "root:" + hash;
        this.store.db
          .prepare(
            "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('privacy-tombstone',?,?,1,?) ON CONFLICT(kind,id) DO NOTHING",
          )
          .run(
            key,
            canonical({
              id: key,
              kind: "root",
              root_sha256: hash,
              forgotten_at: now(),
            }),
            now(),
          );
      }
      for (const taskId of plan.cache_tasks) {
        const task = this.store.get("task", taskId);
        if (!task) continue;
        delete task.record_revision;
        this.store.db
          .prepare(
            "UPDATE records SET data=?,revision=revision+1,updated_at=? WHERE kind='task' AND id=?",
          )
          .run(
            canonical({
              ...task,
              input_cache_pruned: true,
              requires_prepare: true,
            }),
            now(),
            taskId,
          );
      }
      const pending = {
        id: payload.preview_id,
        files: plan.files,
        status: "pending_file_cleanup",
        created_at: now(),
      };
      this.store.db
        .prepare(
          "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('privacy-cleanup',?,?,1,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data",
        )
        .run(pending.id, canonical(pending), now());
    });
    await this.finishFiles(payload.preview_id);
    this.previews.delete(payload.preview_id);
    return {
      status: "completed",
      sha256: plan.subject_sha256,
      native_projects_changed: false,
      provider_deletion_performed: false,
      secure_erasure_claimed: false,
      deduplication_identities_preserved: true,
    };
  }

  async finishFiles(recordId) {
    const pending = this.store.get("privacy-cleanup", recordId);
    fail(pending, "NOT_FOUND", "Cleanup receipt not found", 404);
    this.assertIdle();
    // A crash does not authorize deleting a replacement at the same path.
    const targets = [];
    for (const expected of pending.files) {
      fail(
        expected && typeof expected.relative === "string",
        "REVISION_CONFLICT",
        "Cleanup receipt lacks reviewed target hashes; preview again",
        409,
      );
      const current = await this.file(expected.relative);
      if (!current) continue; // Already removed before interruption.
      fail(
        digest(current) === digest(expected),
        "REVISION_CONFLICT",
        "Cleanup target changed after interruption; review a new preview",
        409,
      );
      targets.push(expected.relative);
    }
    for (const relative of targets)
      await rm(join(this.dataDir, relative), { recursive: true, force: false });
    for (const task of this.store.list("task"))
      if (
        pending.files.some((file) => file.relative === `task-inputs/${task.id}`)
      )
        this.store.put("task", task.id, {
          ...task,
          input_cache_pruned: true,
          requires_prepare: true,
        });
    this.store.put("privacy-cleanup", recordId, {
      ...pending,
      files: [],
      status: "completed",
      completed_at: now(),
    });
    return { status: "completed", cleanup_id: recordId };
  }

  sanitizeRestored(kind, value) {
    if (
      !kind.startsWith("privacy-") &&
      kind !== "settings" &&
      kind !== "backup" &&
      this.privacyReferences(value)
    )
      return null;
    if (this.store.get("privacy-tombstone", `${kind}:${value?.id}`))
      return null;
    if (
      ["job", "task"].includes(kind) &&
      this.store.get("privacy-tombstone", `project:${value?.project_id}`)
    )
      return null;
    if (
      kind === "job" &&
      this.store.get("privacy-tombstone", `task:${value?.task_id}`)
    )
      return null;
    if (kind === "settings") return { ...value, retention: this.policy() };
    return value;
  }

  privacyReferences(value) {
    const tombstones = this.store.list("privacy-tombstone");
    return references(
      value,
      new Set(tombstones.map((item) => item.record_id).filter(Boolean)),
      0,
      [],
      new Set(tombstones.map((item) => item.root_sha256).filter(Boolean)),
    );
  }

  sanitizeRestoredCommand(row) {
    if (!this.privacyReferences(parseStrictJson(row.data))) return row;
    return {
      ...row,
      status: "forgotten",
      data: canonical({
        command_id: row.id,
        status: "forgotten",
        content_removed: true,
        replay_allowed: false,
      }),
      updated_at: now(),
    };
  }

  sanitizeRestoredEvent(row) {
    const cutoff = this.store.get("privacy-policy", "owner")?.event_cutoff;
    if (
      (cutoff && row.created_at < cutoff) ||
      this.privacyReferences(parseStrictJson(row.data))
    )
      return null;
    return row;
  }

  diagnosticPreview({ version, capabilities } = {}) {
    const counts = {};
    for (const job of this.store.list("job"))
      counts[job.status] = (counts[job.status] ?? 0) + 1;
    const data = {
      schema_version: "atelier.diagnostic-export/1",
      created_at: now(),
      version,
      counts: { projects: this.store.list("project").length, jobs: counts },
      capabilities: {
        status: capabilities?.status ?? "unknown",
        auth_mode: capabilities?.auth_mode ?? "unknown",
        cli_version: capabilities?.cli_version ?? "unknown",
      },
      retention: this.policy(),
      omitted: [
        "project names/paths",
        "source content",
        "task text",
        "chat/account IDs",
        "model output",
        "credentials",
        "raw logs",
      ],
    };
    const previewId = id("diagnostic"),
      hash = digest(data);
    this.exportPreviews.set(previewId, {
      data,
      sha256: hash,
      expires_at: this.clock() + 5 * 60_000,
    });
    return {
      preview_id: previewId,
      sha256: hash,
      data,
      scope:
        "Review this aggregate redacted content before local export; no external transmission",
    };
  }

  async diagnosticExport(payload) {
    const preview = this.exportPreviews.get(payload?.preview_id);
    fail(
      payload?.confirmed === true &&
        preview &&
        preview.expires_at > this.clock() &&
        preview.sha256 === payload.sha256,
      "SCOPE_MISMATCH",
      "Review the diagnostic preview before export",
      409,
    );
    const filename = `${payload.preview_id}.json`;
    await atomicWrite(
      join(this.dataDir, "exports", filename),
      JSON.stringify(preview.data, null, 2) + "\n",
    );
    this.exportPreviews.delete(payload.preview_id);
    return {
      filename,
      sha256: preview.sha256,
      content: preview.data,
      transmitted_externally: false,
    };
  }
}
