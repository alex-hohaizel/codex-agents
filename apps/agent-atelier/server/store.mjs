import { DatabaseSync } from "node:sqlite";
import { mkdirSync, chmodSync, existsSync, realpathSync } from "node:fs";
import { dirname, resolve } from "node:path";
import {
  canonical,
  digest,
  fail,
  now,
  isWithin,
  parseStrictJson,
  ServiceError,
} from "./utils.mjs";
// Readers and writers share the same durable JSON capacity; oversized native
// context must fail before inserting a record that future reads cannot decode.
const encode = (value) => {
  const bytes = canonical(value);
  fail(
    Buffer.byteLength(bytes) <= 2 * 1024 * 1024,
    "CAPACITY_LIMIT",
    "Durable context exceeds 2 MiB; narrow optional inputs or split the task without dropping must requirements",
    409,
  );
  return bytes;
};
export class Store {
  constructor(path) {
    this.path = resolve(path);
    mkdirSync(dirname(this.path), {
      recursive: true,
      mode: 448,
    });
    this.db = new DatabaseSync(this.path);
    chmodSync(this.path, 0o600);
    this.db.exec(
      "PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000; PRAGMA foreign_keys=ON;",
    );
    const version = this.db.prepare("PRAGMA user_version").get().user_version;
    fail(
      version <= 1,
      "UNSUPPORTED_SCHEMA",
      "The service database is newer than this application",
      409,
    );
    this.db.exec(
      `CREATE TABLE IF NOT EXISTS records(kind TEXT NOT NULL,id TEXT NOT NULL,data TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 1,updated_at TEXT NOT NULL,PRIMARY KEY(kind,id)); CREATE TABLE IF NOT EXISTS commands(id TEXT PRIMARY KEY,digest TEXT NOT NULL,data TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT NOT NULL,data TEXT NOT NULL,created_at TEXT NOT NULL); PRAGMA user_version=1;`,
    );
  }
  transaction(fn) {
    this.db.exec("BEGIN IMMEDIATE");
    try {
      const value = fn();
      this.db.exec("COMMIT");
      return value;
    } catch (error) {
      this.db.exec("ROLLBACK");
      throw error;
    }
  }
  get(kind, id) {
    const row = this.db
      .prepare("SELECT data,revision FROM records WHERE kind=? AND id=?")
      .get(kind, id);
    return row
      ? {
          ...parseStrictJson(row.data),
          record_revision: row.revision,
        }
      : null;
  }
  list(kind) {
    return this.db
      .prepare(
        "SELECT data,revision FROM records WHERE kind=? ORDER BY updated_at DESC",
      )
      .all(kind)
      .map((row) => ({
        ...parseStrictJson(row.data),
        record_revision: row.revision,
      }));
  }
  put(kind, id, data, expectedRevision) {
    return this.transaction(() => {
      const old = this.db
        .prepare("SELECT revision FROM records WHERE kind=? AND id=?")
        .get(kind, id);
      if (expectedRevision !== undefined)
        fail(
          old?.revision === expectedRevision,
          "REVISION_CONFLICT",
          "This record changed; refresh before retrying",
          409,
        );
      const clean = { ...data };
      delete clean.record_revision;
      const stamp = now();
      this.db
        .prepare(
          "INSERT INTO records(kind,id,data,revision,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data,revision=records.revision+1,updated_at=excluded.updated_at",
        )
        .run(
          kind,
          id,
          encode({
            ...clean,
            updated_at: stamp,
          }),
          1,
          stamp,
        );
      return this.get(kind, id);
    });
  }
  reserveJob(taskId, projectId, candidate, activeStates, authorityEpoch) {
    return this.transaction(() => {
      const task = this.get("task", taskId);
      fail(
        task && task.project_id === projectId && task.status === "prepared",
        "TASK_NOT_READY",
        "This task was already dispatched, paused or changed",
        409,
      );
      fail(
        task.capsule.authority_epoch === authorityEpoch,
        "SCOPE_MISMATCH",
        "Task authority changed; prepare again",
        409,
      );
      fail(
        !task.input_cache_pruned && !task.requires_prepare,
        "TASK_NOT_READY",
        "Task inputs were pruned or revoked; prepare again",
        409,
      );
      const project = this.get("project", projectId);
      let root;
      try {
        root = realpathSync(project?.root);
      } catch {
        throw new ServiceError(
          "SOURCE_DRIFT",
          "The bound project root is unavailable; refresh before dispatch",
          409,
        );
      }
      fail(
        root === project.root && root === task.capsule.root,
        "SOURCE_DRIFT",
        "The canonical project root changed; prepare again",
        409,
      );
      const active = this.list("job").filter((row) =>
        activeStates.includes(row.status),
      );
      const overlapping = active.filter((row) => {
        // New jobs keep their exact boundary; old durable jobs fall back to the
        // immutable task capsule, then the binding. Unknown roots fail closed.
        const pinned =
          row.project_root ??
          this.get("task", row.task_id)?.capsule?.root ??
          this.get("project", row.project_id)?.root;
        let otherRoot;
        try {
          otherRoot = realpathSync(pinned);
          if (otherRoot !== pinned) return true;
        } catch {
          return true;
        }
        return isWithin(root, otherRoot) || isWithin(otherRoot, root);
      });
      fail(
        !overlapping.some(
          (row) =>
            row.scope === "workspace-write" || task.scope === "workspace-write",
        ),
        "WRITER_CONFLICT",
        "An active or unresolved job owns an overlapping canonical project boundary",
        409,
      );
      fail(
        overlapping.length < 2,
        "CAPACITY_LIMIT",
        "At most two read-only jobs run across overlapping project roots",
        409,
      );
      candidate = { ...candidate, project_root: root };
      if (candidate.thread_id)
        fail(
          !active.some((row) => row.thread_id === candidate.thread_id),
          "WRITER_CONFLICT",
          "Another job owns this exact thread",
          409,
        );
      const stamp = now(),
        consumed = { ...task, status: "dispatched", updated_at: stamp };
      delete consumed.record_revision;
      this.db
        .prepare(
          "UPDATE records SET data=?,revision=revision+1,updated_at=? WHERE kind='task' AND id=?",
        )
        .run(encode(consumed), stamp, taskId);
      this.db
        .prepare(
          "INSERT INTO records(kind,id,data,revision,updated_at) VALUES('job',?,?,1,?)",
        )
        .run(candidate.id, encode(candidate), stamp);
      return this.get("job", candidate.id);
    });
  }
  remove(kind, id) {
    this.db.prepare("DELETE FROM records WHERE kind=? AND id=?").run(kind, id);
  }
  commandStart(command) {
    return this.transaction(() => {
      const fingerprint = digest(command);
      const old = this.db
        .prepare("SELECT * FROM commands WHERE id=?")
        .get(command.command_id);
      if (old) {
        fail(
          old.digest === fingerprint,
          "COMMAND_ID_REUSE",
          "This command ID was already used for a different request",
          409,
        );
        return {
          existing: true,
          receipt: parseStrictJson(old.data),
          status: old.status,
        };
      }
      const stamp = now();
      const receipt = {
        command_id: command.command_id,
        status: "prepared",
        operation: command.operation,
        created_at: stamp,
      };
      this.db
        .prepare("INSERT INTO commands VALUES(?,?,?,?,?,?)")
        .run(
          command.command_id,
          fingerprint,
          encode(receipt),
          "prepared",
          stamp,
          stamp,
        );
      return {
        existing: false,
        receipt,
      };
    });
  }
  commandFinish(id, receipt) {
    this.db
      .prepare("UPDATE commands SET data=?,status=?,updated_at=? WHERE id=?")
      .run(encode(receipt), receipt.status, now(), id);
    return receipt;
  }
  commandGet(id) {
    const row = this.db.prepare("SELECT data FROM commands WHERE id=?").get(id);
    return row ? parseStrictJson(row.data) : null;
  }
  latestEventSequence() {
    return this.db
      .prepare("SELECT COALESCE(MAX(sequence),0) value FROM events")
      .get().value;
  }
  commands() {
    return this.db
      .prepare("SELECT data FROM commands ORDER BY created_at DESC LIMIT 100")
      .all()
      .map((x) => parseStrictJson(x.data));
  }
  event(event, data) {
    const stamp = now();
    const r = this.db
      .prepare("INSERT INTO events(event,data,created_at) VALUES(?,?,?)")
      .run(event, encode(data), stamp);
    return {
      sequence: Number(r.lastInsertRowid),
      event,
      data,
      created_at: stamp,
    };
  }
  events(after = 0, limit = 100) {
    return this.db
      .prepare(
        "SELECT * FROM events WHERE sequence>? ORDER BY sequence LIMIT ?",
      )
      .all(after, limit)
      .map((x) => ({
        ...x,
        data: parseStrictJson(x.data),
      }));
  }
  export() {
    return {
      schema_version: "agent-atelier.backup/1",
      created_at: now(),
      records: this.db
        .prepare(
          "SELECT kind,id,data,revision,updated_at FROM records ORDER BY kind,id",
        )
        .all(),
      commands: this.db.prepare("SELECT * FROM commands ORDER BY id").all(),
      events: this.db.prepare("SELECT * FROM events ORDER BY sequence").all(),
    };
  }
  restore(
    snapshot,
    transformRecord = (_kind, value) => value,
    transformEvent = (value) => value,
    transformCommand = (value) => value,
  ) {
    const current = this.export();
    const merge = (before, after, key) => [
      ...new Map([...before, ...after].map((row) => [key(row), row])).values(),
    ];
    snapshot = {
      ...snapshot,
      records: merge(
        snapshot.records,
        current.records.filter((row) => row.kind !== "settings"),
        (row) => row.kind + "\0" + row.id,
      ),
      commands: merge(snapshot.commands, current.commands, (row) => row.id),
      events: merge(snapshot.events, current.events, (row) => row.sequence),
    };
    fail(
      snapshot.schema_version === "agent-atelier.backup/1",
      "UNSUPPORTED_SCHEMA",
      "Unsupported backup format",
    );
    snapshot.records = snapshot.records.flatMap((row) => {
      const transformed = transformRecord(row.kind, parseStrictJson(row.data));
      return transformed === null
        ? []
        : [
            {
              ...row,
              data: encode(transformed),
              revision: row.revision + 1,
              updated_at: now(),
            },
          ];
    });
    snapshot.events = snapshot.events.flatMap((row) => {
      const transformed = transformEvent(row);
      return transformed === null
        ? []
        : [
            {
              ...transformed,
              data:
                typeof transformed.data === "string"
                  ? transformed.data
                  : encode(transformed.data),
            },
          ];
    });
    snapshot.commands = snapshot.commands.map((row) => {
      const transformed = transformCommand(row);
      fail(
        transformed &&
          transformed.id === row.id &&
          transformed.digest === row.digest,
        "INVALID_BACKUP",
        "Restore must preserve command deduplication identity",
        409,
      );
      return transformed;
    });
    this.transaction(() => {
      this.db.exec(
        "DELETE FROM records; DELETE FROM commands; DELETE FROM events;",
      );
      for (const row of snapshot.records)
        this.db
          .prepare("INSERT INTO records VALUES(?,?,?,?,?)")
          .run(row.kind, row.id, row.data, row.revision, row.updated_at);
      for (const row of snapshot.commands)
        this.db
          .prepare("INSERT INTO commands VALUES(?,?,?,?,?,?)")
          .run(
            row.id,
            row.digest,
            row.data,
            row.status,
            row.created_at,
            row.updated_at,
          );
      for (const row of snapshot.events)
        this.db
          .prepare(
            "INSERT INTO events(sequence,event,data,created_at) VALUES(?,?,?,?)",
          )
          .run(row.sequence, row.event, row.data, row.created_at);
    });
  }
  close() {
    this.db.close();
  }
}
