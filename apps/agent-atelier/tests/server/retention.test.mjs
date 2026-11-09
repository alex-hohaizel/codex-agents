import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  writeFile,
  readFile,
  rm,
  symlink,
} from "node:fs/promises";
import { join } from "node:path";
import { Store } from "../../server/store.mjs";
import { RetentionManager } from "../../server/retention.mjs";

const OLD = "2025-01-01T00:00:00.000Z";
async function fixture(t) {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-retention-"),
  );
  const dataDir = join(root, "private-service");
  await mkdir(dataDir);
  const store = new Store(join(dataDir, "service.sqlite"));
  store.put("settings", "owner", { id: "owner", locale: "uk" });
  const retention = new RetentionManager({
    store,
    dataDir,
    clock: () => Date.parse("2026-11-09T12:00:00Z"),
  });
  retention.configure({
    confirmed: true,
    policy: {
      event_days: 30,
      history_days: 90,
      input_cache_days: 30,
      backup_days: 90,
      automatic: false,
    },
  });
  t.after(async () => {
    store.close();
    await rm(root, { force: true, recursive: true });
  });
  return { root, dataDir, store, retention };
}
function terminal(store, id = "job_old", task = "task_old") {
  store.put("project", "project_A", {
    id: "project_A",
    root: "/synthetic/native",
  });
  store.put("task", task, {
    id: task,
    project_id: "project_A",
    status: "dispatched",
  });
  store.put("job", id, {
    id,
    task_id: task,
    project_id: "project_A",
    status: "completed",
    completed_at: OLD,
  });
}

test("cleanup removes only reviewed service cache/history, preserves native files and replay identity", async (t) => {
  const { root, dataDir, store, retention } = await fixture(t);
  terminal(store);
  const native = join(root, "native-project");
  await mkdir(native);
  await writeFile(join(native, "state.json"), '{"keep":true}\n');
  await mkdir(join(dataDir, "task-inputs", "task_old"), { recursive: true });
  await writeFile(
    join(dataDir, "task-inputs", "task_old", "capsule.json"),
    "private cached text",
  );
  const command = {
    command_id: "dispatch_old",
    operation: "task.dispatch",
    payload: { task_id: "task_old" },
  };
  store.commandStart(command);
  store.commandFinish(command.command_id, {
    command_id: command.command_id,
    status: "completed",
    task_id: "task_old",
    output: "private output",
  });
  store.event("job.completed", { job_id: "job_old", output: "private event" });
  for (const kind of ["decision", "evidence", "thread-binding"])
    store.put(kind, kind + "_A", {
      id: kind + "_A",
      project_id: "project_A",
      note: "associated private text",
    });
  store.put("decision", "other", {
    id: "other",
    project_id: "project_B",
    note: "unrelated must remain",
  });
  const previewCommand = {
    command_id: "preview_before_bind",
    operation: "project.preview",
  };
  store.commandStart(previewCommand);
  store.commandFinish(previewCommand.command_id, {
    command_id: previewCommand.command_id,
    status: "completed",
    result: {
      root: "/synthetic/native",
      source_path: "/synthetic/native/state.json",
    },
  });
  const before = store.export();
  const preview = await retention.preview({
    forget_project_ids: ["project_A"],
  });
  assert.equal(preview.counts.projects, 1);
  assert.equal(preview.counts.input_caches, 1);
  const result = await retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  assert.equal(result.native_projects_changed, false);
  assert.equal(
    await readFile(join(native, "state.json"), "utf8"),
    '{"keep":true}\n',
  );
  assert.equal(store.get("project", "project_A"), null);
  for (const kind of ["decision", "evidence", "thread-binding"])
    assert.equal(store.get(kind, kind + "_A"), null);
  assert.ok(store.get("decision", "other"));
  assert.equal(store.commandGet(previewCommand.command_id).status, "forgotten");
  assert.equal(
    retention.sanitizeRestored("decision", {
      id: "old_unknown",
      project_id: "project_A",
      note: "restore attempt",
    }),
    null,
  );
  assert.equal(
    retention.sanitizeRestoredEvent({
      created_at: "2026-11-09T10:00:00Z",
      data: JSON.stringify({ root: "/synthetic/native/nested/file.md" }),
    }),
    null,
  );
  await assert.rejects(
    readFile(join(dataDir, "task-inputs", "task_old", "capsule.json")),
    { code: "ENOENT" },
  );
  assert.equal(store.commandStart(command).existing, true);
  assert.equal(store.commandStart(command).status, "forgotten");
  assert.equal(
    JSON.stringify(store.commandGet(command.command_id)).includes(
      "private output",
    ),
    false,
  );
  assert.equal(
    retention.sanitizeRestored(
      "project",
      JSON.parse(before.records.find((row) => row.kind === "project").data),
    ),
    null,
  );
  assert.equal(
    retention.sanitizeRestored("task", {
      id: "different_task",
      project_id: "project_A",
    }),
    null,
  );
  assert.equal(retention.sanitizeRestoredEvent(before.events[0]), null);
  const restoredCommand = retention.sanitizeRestoredCommand(
    before.commands.find((row) => row.id === "preview_before_bind"),
  );
  assert.equal(restoredCommand.status, "forgotten");
  assert.equal(
    restoredCommand.digest,
    before.commands.find((row) => row.id === "preview_before_bind").digest,
  );
  assert.equal(restoredCommand.data.includes("/synthetic/native"), false);
});

test("unknown and paused work blocks cleanup even when explicitly selected", async (t) => {
  const { store, retention } = await fixture(t);
  terminal(store);
  store.put("job", "job_old", {
    ...store.get("job", "job_old"),
    status: "outcome_unknown",
  });
  await assert.rejects(retention.preview(), { code: "WRITER_CONFLICT" });
  store.put("job", "job_old", {
    ...store.get("job", "job_old"),
    status: "completed",
  });
  store.put("task", "task_old", {
    ...store.get("task", "task_old"),
    paused: true,
  });
  await assert.rejects(
    retention.preview({ forget_project_ids: ["project_A"] }),
    { code: "WRITER_CONFLICT" },
  );
});

test("exact cleanup preview rejects changed cache content and leaves both files and history intact", async (t) => {
  const { dataDir, store, retention } = await fixture(t);
  terminal(store);
  await mkdir(join(dataDir, "task-inputs", "task_old"), { recursive: true });
  const path = join(dataDir, "task-inputs", "task_old", "input.txt");
  await writeFile(path, "original");
  const preview = await retention.preview();
  await writeFile(path, "modified");
  await assert.rejects(
    retention.apply({
      preview_id: preview.preview_id,
      sha256: preview.sha256,
      confirmed: true,
    }),
    { code: "REVISION_CONFLICT" },
  );
  assert.equal(await readFile(path, "utf8"), "modified");
  assert.ok(store.get("job", "job_old"));
});

test("cleanup refuses linked/traversal paths and preserves newest two backups", async (t) => {
  const { root, dataDir, store, retention } = await fixture(t);
  await mkdir(join(dataDir, "task-inputs"));
  await writeFile(join(root, "outside"), "preserve");
  await symlink(join(root, "outside"), join(dataDir, "task-inputs", "linked"));
  await assert.rejects(retention.file("task-inputs/linked"), {
    code: "OUTSIDE_ROOT",
  });
  await assert.rejects(retention.file("task-inputs/../../outside"), {
    code: "OUTSIDE_ROOT",
  });
  await mkdir(join(dataDir, "backups"));
  for (let index = 0; index < 3; index++) {
    const id = `backup_${index}`;
    store.put("backup", id, {
      id,
      created_at: `2025-01-0${index + 1}T00:00:00Z`,
    });
    await writeFile(join(dataDir, "backups", id + ".json"), "{}");
  }
  const preview = await retention.preview();
  assert.equal(preview.counts.backups, 1);
  await retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  assert.equal(store.list("backup").length, 2);
  assert.equal(await readFile(join(root, "outside"), "utf8"), "preserve");
});

test("input-only cleanup revokes retained task execution until preparation", async (t) => {
  const { dataDir, store, retention } = await fixture(t);
  terminal(store);
  retention.configure({
    confirmed: true,
    policy: {
      event_days: null,
      history_days: null,
      input_cache_days: 30,
      backup_days: null,
    },
  });
  await mkdir(join(dataDir, "task-inputs", "task_old"), { recursive: true });
  await writeFile(
    join(dataDir, "task-inputs", "task_old", "input.txt"),
    "cache",
  );
  const preview = await retention.preview();
  assert.equal(preview.counts.jobs, 0);
  await retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  assert.ok(store.get("job", "job_old"));
  assert.equal(store.get("task", "task_old").requires_prepare, true);
});

test("aged event tombstones survive newer retain policy and diagnostic export contains only reviewed aggregates", async (t) => {
  const { dataDir, store, retention } = await fixture(t);
  store.event("test", {
    project_id: "PRIVATE_PROJECT_ID",
    secret: "PRIVATE_TEXT",
  });
  store.db.prepare("UPDATE events SET created_at=?").run(OLD);
  const oldEvent = store.export().events[0];
  const preview = await retention.preview();
  await retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  retention.configure({
    confirmed: true,
    policy: {
      event_days: null,
      history_days: null,
      input_cache_days: null,
      backup_days: null,
    },
  });
  assert.equal(retention.sanitizeRestoredEvent(oldEvent), null);
  const diagnostic = retention.diagnosticPreview({
    version: { suite: "6.0.0" },
    capabilities: {
      auth_mode: "chatgpt",
      status: "ready",
      account_id: "PRIVATE_ACCOUNT",
    },
  });
  assert.equal(JSON.stringify(diagnostic).includes("PRIVATE_"), false);
  await assert.rejects(
    retention.diagnosticExport({
      preview_id: diagnostic.preview_id,
      sha256: "wrong",
      confirmed: true,
    }),
    { code: "SCOPE_MISMATCH" },
  );
  const exported = await retention.diagnosticExport({
    preview_id: diagnostic.preview_id,
    sha256: diagnostic.sha256,
    confirmed: true,
  });
  assert.equal(exported.transmitted_externally, false);
  assert.deepEqual(
    JSON.parse(
      await readFile(join(dataDir, "exports", exported.filename), "utf8"),
    ),
    diagnostic.data,
  );
});

test("interrupted cleanup retains reviewed hashes and refuses a replaced target on resume", async (t) => {
  const { dataDir, store, retention } = await fixture(t);
  terminal(store);
  await mkdir(join(dataDir, "task-inputs", "task_old"), { recursive: true });
  const path = join(dataDir, "task-inputs", "task_old", "input.txt");
  await writeFile(path, "reviewed original");
  const preview = await retention.preview();
  const finish = retention.finishFiles.bind(retention);
  retention.finishFiles = async () => {
    throw new Error("synthetic interrupted I/O");
  };
  await assert.rejects(
    retention.apply({
      preview_id: preview.preview_id,
      sha256: preview.sha256,
      confirmed: true,
    }),
    /interrupted I\/O/,
  );
  retention.finishFiles = finish;
  assert.equal(
    store.get("privacy-cleanup", preview.preview_id).status,
    "pending_file_cleanup",
  );
  await writeFile(path, "new unreviewed material");
  await assert.rejects(retention.finishFiles(preview.preview_id), {
    code: "REVISION_CONFLICT",
  });
  assert.equal(await readFile(path, "utf8"), "new unreviewed material");
});

test("instruction alias retention unlinks only task-derived pointers after DB forgetting and never follows targets", async (t) => {
  const { root, dataDir, store, retention } = await fixture(t);
  terminal(store);
  const target = join(root, "native-AGENTS.md"),
    missing = join(root, "removed-AGENTS.md");
  await writeFile(target, "native instructions must remain");
  const { sha } = await import("../../server/utils.mjs");
  store.put("task", "task_old", {
    ...store.get("task", "task_old"),
    capsule: {
      instruction_manifest: {
        schema_version: "atelier.governing-instructions/1",
        sources: [{ path: target }, { path: missing }],
      },
    },
  });
  const aliases = join(dataDir, "instruction-aliases", "task_old");
  await mkdir(aliases, { recursive: true });
  await symlink(target, join(aliases, sha(target) + ".md"));
  await symlink(missing, join(aliases, sha(missing) + ".md"));
  const preview = await retention.preview({
    forget_project_ids: ["project_A"],
  });
  await retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  assert.equal(store.get("task", "task_old"), null);
  await assert.rejects(readFile(join(aliases, sha(target) + ".md")), {
    code: "ENOENT",
  });
  assert.equal(
    await readFile(target, "utf8"),
    "native instructions must remain",
  );
});

test("instruction alias cleanup rejects unexpected pointers and binds retry to exact reviewed targets", async (t) => {
  const { root, dataDir, store, retention } = await fixture(t);
  terminal(store);
  const { sha } = await import("../../server/utils.mjs");
  const target = join(root, "original.md"),
    replacement = join(root, "replacement.md");
  await writeFile(target, "original");
  await writeFile(replacement, "replacement");
  store.put("task", "task_old", {
    ...store.get("task", "task_old"),
    capsule: {
      instruction_manifest: {
        schema_version: "atelier.governing-instructions/1",
        sources: [{ path: target }],
      },
    },
  });
  const aliases = join(dataDir, "instruction-aliases", "task_old");
  await mkdir(aliases, { recursive: true });
  const link = join(aliases, sha(target) + ".md");
  await symlink(target, link);
  await symlink(replacement, join(aliases, "unexpected.md"));
  await assert.rejects(retention.preview(), { code: "OUTSIDE_ROOT" });
  await rm(join(aliases, "unexpected.md"));
  const preview = await retention.preview(),
    finish = retention.finishFiles.bind(retention);
  retention.finishFiles = async () => {
    throw new Error("synthetic I/O failure");
  };
  await assert.rejects(
    retention.apply({
      preview_id: preview.preview_id,
      sha256: preview.sha256,
      confirmed: true,
    }),
    /I\/O failure/,
  );
  retention.finishFiles = finish;
  await rm(link);
  await symlink(replacement, link);
  await assert.rejects(retention.finishFiles(preview.preview_id), {
    code: "OUTSIDE_ROOT",
  });
  assert.equal(await readFile(replacement, "utf8"), "replacement");
  assert.equal(await readFile(target, "utf8"), "original");
});
