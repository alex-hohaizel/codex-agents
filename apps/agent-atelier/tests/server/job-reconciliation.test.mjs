import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { EventEmitter } from "node:events";
import { realpathSync } from "node:fs";
import { mkdir, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import { Application } from "../../server/application.mjs";
import { CodexAdapter } from "../../server/codex.mjs";
import { ServiceError } from "../../server/utils.mjs";

const repoRoot = resolve(import.meta.dirname, "../../../..");

function historyFixture(pages) {
  const adapter = new CodexAdapter();
  const requests = [];
  adapter.connect = async () => {};
  adapter.rpc = async (method, params, timeout) => {
    assert.equal(method, "thread/turns/list");
    assert.ok(timeout > 0 && timeout <= adapter.rpcTimeoutMs);
    requests.push(params);
    return pages[requests.length - 1];
  };
  return { adapter, requests };
}

test("exact turn lookup follows native history pages without loading items", async () => {
  const { adapter, requests } = historyFixture([
    { data: [{ id: "neighbor", status: "inProgress" }], nextCursor: "opaque" },
    { data: [{ id: "recorded-turn", status: "completed" }], nextCursor: null },
  ]);
  assert.deepEqual(await adapter.readTurn("recorded-thread", "recorded-turn"), {
    id: "recorded-turn",
    status: "completed",
  });
  assert.deepEqual(requests, [
    {
      threadId: "recorded-thread",
      limit: 100,
      sortDirection: "desc",
      itemsView: "notLoaded",
    },
    {
      threadId: "recorded-thread",
      limit: 100,
      sortDirection: "desc",
      itemsView: "notLoaded",
      cursor: "opaque",
    },
  ]);
});

test("turn lookup holds on malformed, cyclic or bounded incomplete history", async () => {
  for (const pages of [
    [{ data: null, nextCursor: null }],
    [
      { data: [], nextCursor: "same" },
      { data: [], nextCursor: "same" },
    ],
    Array.from({ length: 10 }, (_, page) => ({
      data: [],
      nextCursor: `cursor-${page}`,
    })),
  ]) {
    const { adapter, requests } = historyFixture(pages);
    await assert.rejects(adapter.readTurn("thread", "recorded-turn"), {
      code: "HISTORY_LOOKUP_INCOMPLETE",
    });
    assert.equal(requests.length, pages.length);
  }
  const { adapter } = historyFixture([{ data: [], nextCursor: null }]);
  assert.equal(await adapter.readTurn("thread", "recorded-turn"), null);
});

async function fixture(t) {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-reconcile-"),
  );
  const project = join(root, "project");
  const dataDir = join(root, "data");
  await mkdir(project);
  const native = new EventEmitter();
  const reads = [];
  native.close = async () => {};
  native.resume = () =>
    assert.fail("reconciliation must never resume a native thread");
  native.start = () =>
    assert.fail("reconciliation must never start a native thread");
  native.turn = () => assert.fail("reconciliation must never send a turn");
  native.interrupt = () =>
    assert.fail("reconciliation must never interrupt a turn");
  native.readThread = async (id) => {
    reads.push(["thread", id]);
    return { thread: { id, cwd: project, status: { type: "active" } } };
  };
  native.readTurn = async (id, turnId) => {
    reads.push(["turn", id, turnId]);
    return null;
  };
  let app = new Application({ dataDir, repoRoot, codex: native });
  t.after(async () => {
    app.store.close();
    await rm(root, { recursive: true, force: true });
  });
  const command = (operation, payload, project_id) =>
    app.execute({ command_id: randomUUID(), operation, payload, project_id });
  const preview = await command("project.preview", { root: project });
  const binding = await command("project.bind", {
    preview_id: preview.result.preview_id,
  });
  const stored = {
    id: "job",
    project_id: binding.result.project.id,
    task_id: "task",
    thread_id: "thread",
    turn_id: "turn",
    status: "running",
    events: [],
    pending_requests: [{ id: 1 }],
  };
  app.store.put("job", stored.id, stored);
  function restart() {
    // Reopen the same SQLite service store, as after a hard process restart.
    app.store.close();
    native.removeAllListeners();
    app = new Application({ dataDir, repoRoot, codex: native });
  }
  restart();
  assert.equal(app.store.get("job", stored.id).status, "outcome_unknown");
  return {
    get app() {
      return app;
    },
    project,
    stored,
    native,
    reads,
    restart,
    run: (operation, payload) => command(operation, payload, stored.project_id),
    reconcile: () =>
      command("job.reconcile", { job_id: stored.id }, stored.project_id),
  };
}

test("restart reconciles only the recorded turn and keeps missing evidence unknown", async (t) => {
  const f = await fixture(t);
  const missing = await f.reconcile();
  assert.equal(missing.error, undefined);
  assert.equal(missing.result.job.status, "outcome_unknown");
  assert.equal(missing.result.job.host_observation.turn_status, "not_returned");
  assert.deepEqual(f.reads, [
    ["thread", "thread"],
    ["turn", "thread", "turn"],
  ]);
  f.native.readTurn = async () => ({ id: "other-turn", status: "completed" });
  assert.equal((await f.reconcile()).result.job.status, "outcome_unknown");
  f.native.readTurn = async () => {
    throw new ServiceError("HOST_TIMEOUT", "fixture timeout", 504);
  };
  const unconfirmed = (await f.reconcile()).result.job;
  assert.equal(unconfirmed.status, "outcome_unknown");
  assert.equal(unconfirmed.host_observation.turn_status, "history_unconfirmed");
  f.native.readTurn = async () => ({ id: "turn", status: "completed" });
  const completed = (await f.reconcile()).result.job;
  assert.equal(completed.status, "completed");
  assert.equal(completed.host_observation.turn_status, "completed");
  assert.deepEqual(completed.pending_requests, []);
});

test("missing exact turn identity makes no native read and other checkouts are refused", async (t) => {
  const f = await fixture(t);
  f.app.store.put("job", "job", {
    ...f.stored,
    turn_id: null,
    status: "outcome_unknown",
  });
  assert.match(
    (await f.reconcile()).result.job.unknown_reason,
    /No exact native turn identity/,
  );
  assert.deepEqual(f.reads, []);
  const known = { ...f.stored, status: "outcome_unknown" };
  const before = f.app.store.put("job", "job", known);
  f.native.readThread = async (id) => ({
    thread: {
      id,
      cwd: join(f.project, "different"),
      status: { type: "active" },
    },
  });
  const wrongProject = await f.reconcile();
  assert.equal(wrongProject.error.code, "SCOPE_MISMATCH");
  assert.deepEqual(
    JSON.parse(JSON.stringify(f.app.store.get("job", "job"))),
    JSON.parse(JSON.stringify(before)),
  );
  assert.deepEqual(f.reads, []);
});

test("active exact turn observation retains pause and never overwrites a terminal event", async (t) => {
  const f = await fixture(t);
  f.native.readTurn = async () => ({ id: "turn", status: "inProgress" });
  const active = (await f.reconcile()).result.job;
  assert.equal(active.status, "running");
  f.app.store.put("job", "job", { ...active, status: "pause_pending" });
  assert.equal((await f.reconcile()).result.job.status, "pause_pending");
  f.native.readTurn = async () => {
    f.native.emit("notification", {
      method: "turn/completed",
      params: {
        threadId: "thread",
        turn: { id: "turn", status: "interrupted" },
      },
    });
    return { id: "turn", status: "inProgress" };
  };
  assert.equal((await f.reconcile()).result.job.status, "paused");
});

test("pause persists through a missing receipt and restart without repeating a native interrupt", async (t) => {
  const f = await fixture(t);
  f.app.store.put("task", "task", {
    id: "task",
    project_id: f.stored.project_id,
    status: "dispatched",
  });
  f.app.store.put("job", "job", f.stored);
  const interrupts = [];
  f.native.interrupt = async (...args) => interrupts.push(args);
  const pause = () => f.run("task.pause", { task_id: "task" });
  const requested = (await pause()).result.job;
  assert.equal(requested.status, "pause_pending");
  assert.equal(requested.interruption_intent, "pause");
  assert.equal((await pause()).result.job.status, "pause_pending");
  const unknown = (await f.reconcile()).result.job;
  assert.equal(unknown.status, "outcome_unknown");
  assert.equal(unknown.interruption_intent, "pause");
  f.restart();
  f.native.readTurn = async () => ({ id: "turn", status: "inProgress" });
  assert.equal((await f.reconcile()).result.job.status, "pause_pending");
  f.native.emit("notification", {
    method: "turn/started",
    params: { threadId: "thread", turn: { id: "turn", status: "inProgress" } },
  });
  f.native.readTurn = async () => ({ id: "turn", status: "interrupted" });
  assert.equal((await f.reconcile()).result.job.status, "paused");
  assert.deepEqual(interrupts, [["thread", "turn"]]);
});

test("an exact interrupted notification preserves legacy task pause but honors explicit job cancel", async (t) => {
  const f = await fixture(t);
  f.app.store.put("task", "task", {
    id: "task",
    project_id: f.stored.project_id,
    status: "paused",
  });
  const notify = (id) =>
    f.native.emit("notification", {
      method: "turn/completed",
      params: { threadId: "thread", turn: { id, status: "interrupted" } },
    });
  notify("unknown-turn");
  assert.equal(f.app.store.get("job", "job").status, "outcome_unknown");
  notify("turn");
  assert.equal(f.app.store.get("job", "job").status, "paused");

  f.app.store.put("job", "job", f.stored);
  const interrupts = [];
  f.native.interrupt = async (...args) => interrupts.push(args);
  const cancel = await f.run("job.interrupt", { job_id: "job" });
  assert.equal(cancel.result.job.interruption_intent, "cancel");
  f.restart();
  f.native.readTurn = async () => ({ id: "turn", status: "inProgress" });
  assert.equal((await f.reconcile()).result.job.status, "cancel_requested");
  notify("turn");
  assert.equal(f.app.store.get("job", "job").status, "cancelled");
  assert.deepEqual(interrupts, [["thread", "turn"]]);
});

test("restart retains known legacy pause and cancel requests before marking the receipt unknown", async (t) => {
  const f = await fixture(t);
  f.native.readTurn = async () => ({ id: "turn", status: "interrupted" });
  for (const [pending, intent, terminal] of [
    ["pause_pending", "pause", "paused"],
    ["cancel_requested", "cancel", "cancelled"],
  ]) {
    f.app.store.put("job", "job", { ...f.stored, status: pending });
    f.restart();
    const unknown = f.app.store.get("job", "job");
    assert.equal(unknown.status, "outcome_unknown");
    assert.equal(unknown.interruption_intent, intent);
    assert.equal((await f.reconcile()).result.job.status, terminal);
  }
});
