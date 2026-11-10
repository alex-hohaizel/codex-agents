import { lstat, readdir, rm, readFile, readlink } from "node:fs/promises";
import { join, resolve, dirname, basename } from "node:path";
import { ACTIVE_JOB_STATES } from "../shared/contracts.mjs";
import { verifyExecutionInputTask } from "./skills.mjs";
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
const operationCopies = {
  "native-controller": {
    category: "controller-backups",
    terminal: new Set(["completed", "rejected", "reconciled_unclassified"]),
  },
  "optional-update": {
    category: "optional-updates",
    terminal: new Set(["completed", "failed", "rolled_back"]),
  },
};
const copyKey = (kind, ident) => `${kind}:${ident}`;
const copyOwner = (kind, row) => ({
  kind,
  record_id: row.id,
  backup_id: row.backup_id,
  relative: `${operationCopies[kind].category}/${row.id}`,
});
const relatedRootHashes = (row) => [
  ...new Set(
    [row.root, row.source_root]
      .filter((value) => typeof value === "string" && value.startsWith("/"))
      .flatMap((value) => {
        let prefix = "";
        return value
          .split("/")
          .filter(Boolean)
          .map((part) => {
            prefix += "/" + part;
            return sha(prefix);
          });
      }),
  ),
];
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
    fail(
      Object.entries(operationCopies).every(([kind, spec]) =>
        this.store.list(kind).every((row) => spec.terminal.has(row.status)),
      ),
      "WRITER_CONFLICT",
      "Reconcile unfinished native controller and optional maintenance operations before cleanup",
      409,
    );
  }

  async file(
    relative,
    reviewedAliases = null,
    reviewedOperation = null,
    reviewedExecution = null,
  ) {
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
      [
        "task-inputs",
        "instruction-aliases",
        "execution-inputs",
        "codex-logs",
        "backups",
        "controller-backups",
        "optional-updates",
      ].includes(relative.split("/")[0]),
      "OUTSIDE_ROOT",
      "Only service-owned cache/log/backup paths are eligible",
      403,
    );
    const parts = relative.split("/");
    const operationKind = Object.keys(operationCopies).find(
      (kind) => operationCopies[kind].category === parts[0],
    );
    let ownedOperation = null;
    if (operationKind) {
      fail(
        parts.length === 2 && identifier(parts[1]),
        "OUTSIDE_ROOT",
        "Only a complete owned operation copy can be reviewed",
        403,
      );
      const live = this.store.get(operationKind, parts[1]);
      const retained = this.store.get(
        "operation-copy",
        copyKey(operationKind, parts[1]),
      );
      ownedOperation =
        reviewedOperation ??
        (live ? copyOwner(operationKind, live) : retained?.owner);
      fail(
        ownedOperation &&
          ownedOperation.kind === operationKind &&
          ownedOperation.record_id === parts[1] &&
          ownedOperation.backup_id === parts[1] &&
          ownedOperation.relative === relative,
        "OUTSIDE_ROOT",
        "Operation copy needs its exact original receipt or reviewed cleanup descriptor",
        403,
      );
      fail(
        !live || operationCopies[operationKind].terminal.has(live.status),
        "WRITER_CONFLICT",
        "Unreconciled operation copies cannot be removed",
        409,
      );
    }
    let ownedExecution = null;
    let executionLocation = null;
    if (parts[0] === "execution-inputs") {
      fail(
        parts.length === 2 && identifier(parts[1]),
        "OUTSIDE_ROOT",
        "Only a complete owned execution-input task can be reviewed",
        403,
      );
      const selections =
        this.store.get("task", parts[1])?.capsule?.selected_skills ?? [];
      const selected = selections.filter((entry) => entry.execution_transport);
      if (!selected.length && reviewedExecution === null) return null;
      const transport = selected[0]?.execution_transport;
      ownedExecution = reviewedExecution ?? {
        schema_version: "atelier.execution-input-transport/1",
        task_id: parts[1],
        data_dir_sha256: transport.data_dir_sha256,
        task_binding_sha256: transport.task_binding_sha256,
      };
      fail(
        ownedExecution.schema_version ===
          "atelier.execution-input-transport/1" &&
          ownedExecution.task_id === parts[1] &&
          ownedExecution.data_dir_sha256 === sha(this.dataDir) &&
          /^[a-f0-9]{64}$/.test(ownedExecution.task_binding_sha256) &&
          selected.every(
            (entry) =>
              entry.execution_transport.task_id === parts[1] &&
              entry.execution_transport.data_dir_sha256 ===
                ownedExecution.data_dir_sha256 &&
              entry.execution_transport.task_binding_sha256 ===
                ownedExecution.task_binding_sha256,
          ),
        "OUTSIDE_ROOT",
        "Execution-input cleanup needs its original task ownership binding",
        403,
      );
      try {
        executionLocation = await verifyExecutionInputTask(
          this.dataDir,
          parts[1],
          ownedExecution.task_binding_sha256,
        );
      } catch (error) {
        if (error.code === "ENOENT") return null;
        throw error;
      }
    }
    const path = executionLocation?.taskRoot ?? join(this.dataDir, relative);
    let current = executionLocation?.namespace ?? this.dataDir;
    for (const part of executionLocation ? [parts[1]] : relative.split("/")) {
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
    const aliasMode = relative.split("/")[0] === "instruction-aliases";
    let aliasTargets = null;
    if (aliasMode) {
      const parts = relative.split("/");
      fail(
        parts.length === 2 && identifier(parts[1]),
        "OUTSIDE_ROOT",
        "Only a complete owned instruction-alias cache can be reviewed",
        403,
      );
      if (reviewedAliases !== null) aliasTargets = reviewedAliases;
      else {
        const manifest = this.store.get("task", parts[1])?.capsule
          ?.instruction_manifest;
        fail(
          manifest?.schema_version === "atelier.governing-instructions/1" &&
            Array.isArray(manifest.sources),
          "REVISION_CONFLICT",
          "Instruction alias cleanup requires the original task pins or reviewed pending manifest",
          409,
        );
        aliasTargets = Object.fromEntries(
          manifest.sources.map((source) => [
            sha(source.path) + ".md",
            source.path,
          ]),
        );
      }
      fail(
        aliasTargets &&
          typeof aliasTargets === "object" &&
          !Array.isArray(aliasTargets) &&
          Object.keys(aliasTargets).length <= 256 &&
          Object.entries(aliasTargets).every(
            ([name, target]) =>
              typeof target === "string" &&
              target.startsWith("/") &&
              target.length <= 8192 &&
              !target.includes("\0") &&
              name === sha(target) + ".md",
          ),
        "OUTSIDE_ROOT",
        "Invalid reviewed instruction alias targets",
        403,
      );
    }
    let count = 0,
      bytes = 0;
    const entries = [];
    const visit = async (target) => {
      const stat = await lstat(target);
      if (aliasMode && target !== path) {
        const expected = aliasTargets[basename(target)];
        fail(
          dirname(target) === path &&
            stat.isSymbolicLink() &&
            expected &&
            (await readlink(target)) === expected,
          "OUTSIDE_ROOT",
          "Only exact task-derived instruction aliases may be unlinked",
          403,
        );
        fail(
          ++count <= 10_000,
          "CAPACITY_LIMIT",
          "Cleanup tree is too large for one preview",
          409,
        );
        bytes += stat.size;
        entries.push({
          path: basename(target),
          type: "instruction-alias",
          target_sha256: sha(expected),
          size: stat.size,
          mtime_ms: stat.mtimeMs,
        });
        return; // Never open or traverse a governing target during cleanup.
      }
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
      ...(aliasMode ? { alias_targets: aliasTargets } : {}),
      ...(ownedOperation ? { owned_operation: ownedOperation } : {}),
      ...(ownedExecution ? { owned_execution: ownedExecution } : {}),
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
    const rootHashSet = new Set(roots.map(sha));
    const ownedCopies = new Map();
    const operationHistory = new Set();
    for (const [kind, spec] of Object.entries(operationCopies)) {
      for (const row of this.store.list(kind)) {
        fail(
          identifier(row.id) &&
            row.backup_id === row.id &&
            spec.terminal.has(row.status),
          "REVISION_CONFLICT",
          "Operation copy receipt has invalid ownership or is not terminal",
          409,
        );
        const key = copyKey(kind, row.id),
          end = row.completed_at ?? row.reconciled_at ?? row.updated_at;
        ownedCopies.set(key, {
          owner: copyOwner(kind, row),
          row,
          end,
          explicit: references(row, ids, 0, roots),
          backup_due: older(end, policy.backup_days, at),
        });
        if (older(end, policy.history_days, at)) {
          operationHistory.add(key);
          ids.add(row.id);
        }
      }
    }
    for (const row of this.store.list("operation-copy")) {
      const owner = row.owner;
      fail(
        owner &&
          Object.hasOwn(operationCopies, owner.kind) &&
          identifier(owner.record_id) &&
          owner.backup_id === owner.record_id &&
          row.id === copyKey(owner.kind, owner.record_id) &&
          owner.relative ===
            `${operationCopies[owner.kind].category}/${owner.record_id}` &&
          Array.isArray(row.related_root_sha256s) &&
          row.related_root_sha256s.length <= 4096 &&
          row.related_root_sha256s.every((hash) => /^[a-f0-9]{64}$/.test(hash)),
        "REVISION_CONFLICT",
        "Retained operation copy lost its original ownership descriptor",
        409,
      );
      const explicit =
        (row.project_id && ids.has(row.project_id)) ||
        row.related_root_sha256s?.some((hash) => rootHashSet.has(hash));
      const end = row.completed_at ?? row.created_at;
      if (!ownedCopies.has(row.id))
        ownedCopies.set(row.id, {
          owner,
          row,
          marker: true,
          end,
          explicit,
          backup_due: older(end, policy.backup_days, at),
        });
      if (explicit || older(end, policy.backup_days, at)) ids.add(row.id);
    }
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
            references(parseStrictJson(row.data), ids, 0, roots) ||
            (row.kind === "operation-copy" &&
              parseStrictJson(row.data).related_root_sha256s?.some((hash) =>
                rootHashSet.has(hash),
              )))
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
      for (const category of [
        "task-inputs",
        "instruction-aliases",
        "execution-inputs",
      ]) {
        const file = await this.file(`${category}/${taskId}`);
        if (file) files.push(file);
      }
    }
    const removedRecords = new Set(
      recordRows.map((row) => copyKey(row.kind, row.id)),
    );
    const retainedCopies = [],
      prunedCopies = [];
    for (const [key, copy] of ownedCopies) {
      const rowRemoved = removedRecords.has(
        copy.marker ? copyKey("operation-copy", copy.row.id) : key,
      );
      const explicitlyForgotten =
        copy.explicit || (rowRemoved && !operationHistory.has(key));
      const removeCopy = explicitlyForgotten || copy.backup_due;
      const historyRemoved = !copy.marker && rowRemoved;
      if (!removeCopy && !historyRemoved) continue;
      const file = await this.file(copy.owner.relative);
      if (removeCopy) {
        if (file) files.push(file);
        prunedCopies.push(copy.owner);
      } else if (file) {
        // History and raw-copy policies are independent. Preserve only a small
        // association index when the receipt expires before its retained copy.
        retainedCopies.push({
          id: key,
          owner: copy.owner,
          project_id: copy.row.project_id ?? null,
          related_root_sha256s: relatedRootHashes(copy.row),
          completed_at: copy.end,
          created_at: new Date(at).toISOString(),
          history_removed: true,
        });
      }
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
      retained_operation_copies: retainedCopies,
      pruned_operation_copies: prunedCopies,
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
        operation_copies: plan.pruned_operation_copies.length,
        retained_operation_copy_indexes: plan.retained_operation_copies.length,
        files: plan.files.reduce((sum, file) => sum + file.files, 0),
        bytes: plan.files.reduce((sum, file) => sum + file.bytes, 0),
      },
      scope:
        "Service projections/history/cache only. Native projects and provider copies untouched. Service-database backups retain the newest two. Controller and optional-maintenance copies follow backup_days or explicit project forgetting; their receipts follow history_days independently. A minimal association index tracks a retained copy after its history expires. This is not secure physical erasure.",
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
      for (const marker of plan.retained_operation_copies) {
        this.store.db
          .prepare(
            "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('operation-copy',?,?,1,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=records.revision+1,updated_at=excluded.updated_at",
          )
          .run(marker.id, canonical(marker), now());
      }
      for (const owner of plan.pruned_operation_copies) {
        const key = copyKey(owner.kind, owner.record_id);
        const tombstone = {
          id: `operation-copy:${key}`,
          kind: "operation-copy",
          record_id: key,
          backup_pruned: true,
          forgotten_at: now(),
        };
        this.store.db
          .prepare(
            "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('privacy-tombstone',?,?,1,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=records.revision+1,updated_at=excluded.updated_at",
          )
          .run(tombstone.id, canonical(tombstone), now());
        const live = this.store.get(owner.kind, owner.record_id);
        if (live) {
          delete live.record_revision;
          this.store.db
            .prepare(
              "UPDATE records SET data=?,revision=revision+1,updated_at=? WHERE kind=? AND id=?",
            )
            .run(
              canonical({
                ...live,
                backup_pruned: true,
                backup_pruned_at: now(),
              }),
              now(),
              owner.kind,
              owner.record_id,
            );
        }
      }
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
      const current = await this.file(
        expected.relative,
        expected.alias_targets ?? null,
        expected.owned_operation ?? null,
        expected.owned_execution ?? null,
      );
      if (!current) continue; // Already removed before interruption.
      fail(
        digest(current) === digest(expected),
        "REVISION_CONFLICT",
        "Cleanup target changed after interruption; review a new preview",
        409,
      );
      targets.push({
        relative: expected.relative,
        ownedExecution: current.owned_execution,
      });
    }
    for (const { relative, ownedExecution } of targets) {
      const target = ownedExecution
        ? (
            await verifyExecutionInputTask(
              this.dataDir,
              ownedExecution.task_id,
              ownedExecution.task_binding_sha256,
            )
          ).taskRoot
        : join(this.dataDir, relative);
      await rm(target, { recursive: true, force: false });
    }
    for (const task of this.store.list("task"))
      if (
        pending.files.some((file) =>
          [
            `task-inputs/${task.id}`,
            `instruction-aliases/${task.id}`,
            `execution-inputs/${task.id}`,
          ].includes(file.relative),
        )
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
    if (kind === "operation-copy") {
      if (this.store.get("privacy-tombstone", `operation-copy:${value?.id}`))
        return null;
      const forgottenRoots = new Set(
        this.store
          .list("privacy-tombstone")
          .map((row) => row.root_sha256)
          .filter(Boolean),
      );
      if (value?.related_root_sha256s?.some((hash) => forgottenRoots.has(hash)))
        return null;
      // The owning receipt was deliberately forgotten before this retained raw
      // copy expired. That receipt's own tombstone must not orphan the index.
      const { owner, ...context } = value ?? {};
      if (this.privacyReferences(context)) return null;
      return value;
    }
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
    if (
      Object.hasOwn(operationCopies, kind) &&
      this.store.get(
        "privacy-tombstone",
        `operation-copy:${copyKey(kind, value?.id)}`,
      )
    )
      return { ...value, backup_pruned: true };
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
