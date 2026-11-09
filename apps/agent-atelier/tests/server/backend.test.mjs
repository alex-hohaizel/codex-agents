import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  writeFile,
  mkdir,
  symlink,
  readFile,
  rm,
} from "node:fs/promises";
import { join, resolve } from "node:path";
import { EventEmitter } from "node:events";
import { randomUUID } from "node:crypto";
import { execFileSync } from "node:child_process";
import { parseStrictJson, safeFile, digest, sha } from "../../server/utils.mjs";
import { Store } from "../../server/store.mjs";
import { Application } from "../../server/application.mjs";
import { createServer } from "../../server/index.mjs";
import { launchToken } from "../../server/session.mjs";
import { localProfile } from "../../server/permissions.mjs";
import { readInstalledSource } from "../../server/skills.mjs";
import { selectRequirements } from "../../server/context.mjs";
const repoRoot = resolve(import.meta.dirname, "../../../..");
class FakeCodex extends EventEmitter {
  constructor() {
    super();
    this.status = { status: "connected" };
    this.starts = 0;
    this.requests = new Map();
  }
  async start() {
    this.starts++;
    return {
      thread: { id: "thread-test" },
      instructionSources: [],
    };
  }
  async turn(_threadId, _capsule, onDispatch) {
    onDispatch?.();
    this.emit("notification", {
      method: "turn/started",
      params: {
        threadId: "thread-test",
        turn: {
          id: "turn-test",
          status: "inProgress",
        },
      },
      observed_at: new Date().toISOString(),
    });
    return { turn: { id: "turn-test" } };
  }
  async interrupt() {
    this.interrupted = true;
    return {};
  }
  async close() {}
  async connect() {
    return this.status;
  }
  async resume() {
    return { thread: { id: "thread-test" } };
  }
  async readThread() {
    return {
      thread: {
        id: "thread-test",
        status: { type: "idle" },
        turns: [],
      },
    };
  }
  respond() {
    return { status: "response_sent" };
  }
}
async function fixture() {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-server-test-"),
  );
  const project = join(root, "project");
  await mkdir(project);
  await writeFile(
    join(project, "AGENTS.md"),
    "Preserve accepted identity and all requirements.\n",
  );
  await mkdir(join(project, ".appatelier"));
  await writeFile(
    join(project, ".appatelier/state.json"),
    JSON.stringify({
      schema_version: "test/1",
      phase: "specification",
      requirements: [
        {
          id: "MUST-1",
          text: "Keep owner intent",
          priority: "must",
          acceptance: "Owner intent retained",
          dependencies: [],
        },
      ],
    }),
  );
  const codex = new FakeCodex();
  const app = new Application({
    dataDir: join(root, "data"),
    repoRoot,
    codex,
  });
  const command = (operation, payload = {}, extra = {}) =>
    app.execute({
      command_id: randomUUID(),
      operation,
      payload,
      ...extra,
    });
  const preview = await command("project.preview", { root: project });
  const binding = await command("project.bind", {
    preview_id: preview.result.preview_id,
  });
  return {
    root,
    project,
    codex,
    app,
    command,
    binding: binding.result.project,
    async close() {
      await app.close();
      await rm(root, {
        recursive: true,
        force: true,
      });
    },
  };
}
test("strict JSON rejects nested duplicate keys, overflow and non-JSON whitespace", () => {
  assert.throws(
    () => parseStrictJson('{"authority":{"scope":"read","scope":"write"}}'),
    /Duplicate/,
  );
  assert.throws(() => parseStrictJson('{"cost":1e999}'), /Non-finite/);
  assert.throws(() => parseStrictJson("\xA0{}"), /Invalid/);
  assert.deepEqual(
    JSON.parse(JSON.stringify(parseStrictJson('{"ok":[true,null,3]}'))),
    { ok: [true, null, 3] },
  );
});
test("artifact boundary rejects parent traversal, sibling and symlink escapes", async () => {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-path-"));
  try {
    await writeFile(join(root, "safe.txt"), "ok");
    await symlink("/etc", join(root, "escape"));
    await assert.rejects(safeFile(root, "../other"), /Parent traversal/);
    await assert.rejects(safeFile(root, "escape/hosts"), /Symlink/);
    await assert.rejects(safeFile(root, ".env"), /outside the artifact/);
    assert.equal(await safeFile(root, "safe.txt"), join(root, "safe.txt"));
  } finally {
    await rm(root, {
      recursive: true,
      force: true,
    });
  }
});
test("durable command identity returns previous result and rejects changed payload", async () => {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-command-"));
  const store = new Store(join(root, "state.sqlite"));
  try {
    const command = {
      command_id: "fixed-command",
      operation: "service.status",
      payload: {},
    };
    assert.equal(store.commandStart(command).existing, false);
    store.commandFinish(command.command_id, {
      command_id: command.command_id,
      status: "completed",
      result: { n: 1 },
    });
    assert.equal(store.commandStart(command).receipt.result.n, 1);
    assert.throws(
      () =>
        store.commandStart({
          ...command,
          payload: { other: true },
        }),
      /different request/,
    );
    store.put("test", "R", { id: "R" });
    assert.throws(() => store.put("test", "R", { id: "R" }, 0), /changed/);
  } finally {
    store.close();
    await rm(root, {
      recursive: true,
      force: true,
    });
  }
});
test("task capsule retains native must and rejects drift before dispatch", async () => {
  const f = await fixture();
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect project",
        acceptance: "Return observed requirements",
        scope: "read-only",
        deadline_seconds: 60,
      },
      {
        project_id: f.binding.id,
        expected_revision: f.binding.revision,
      },
    );
    assert.equal(prepared.status, "completed");
    assert.ok(
      prepared.result.capsule.requirements.some((x) => x.id === "MUST-1"),
    );
    assert.equal(prepared.result.capsule.quality_certified, false);
    await writeFile(join(f.project, "AGENTS.md"), "Changed accepted rules\n");
    const dispatch = await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(dispatch.error.code, "SOURCE_DRIFT");
    assert.equal(f.codex.starts, 0);
  } finally {
    await f.close();
  }
});
test("one current writer blocks competing write; observed turn completes then owner review stays separate", async () => {
  const f = await fixture();
  try {
    const prepare = () =>
      f.command(
        "task.prepare",
        {
          objective: "Inspect sources",
          acceptance: "Report observed result",
          scope: "workspace-write",
          allowed_paths: ["."],
          deadline_seconds: 60,
        },
        { project_id: f.binding.id },
      );
    const a = await prepare(),
      b = await prepare();
    const started = await f.command(
      "task.dispatch",
      { task_id: a.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(started.result.job.status, "running");
    const competing = await f.command(
      "task.dispatch",
      { task_id: b.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(competing.error.code, "WRITER_CONFLICT");
    f.codex.emit("notification", {
      method: "turn/completed",
      params: {
        threadId: "thread-test",
        turn: {
          id: "turn-test",
          status: "completed",
        },
      },
      observed_at: new Date().toISOString(),
    });
    const job = f.app.store.get("job", started.result.job.id);
    assert.equal(job.status, "completed");
    assert.equal(job.review_status, undefined);
    const reviewed = await f.command(
      "job.review",
      {
        job_id: job.id,
        verdict: "accepted",
        note: "Checked actual task result",
      },
      { project_id: f.binding.id },
    );
    assert.equal(reviewed.result.review.independent_qa, false);
  } finally {
    await f.close();
  }
});
test("server restart retains unknown outcome and never dispatches it", async () => {
  const f = await fixture();
  const dataDir = f.app.dataDir;
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Read source",
        acceptance: "Report result",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    await f.app.close();
    const codex = new FakeCodex();
    const app = new Application({
      dataDir,
      repoRoot,
      codex,
    });
    assert.equal(app.store.list("job")[0].status, "outcome_unknown");
    assert.equal(codex.starts, 0);
    await app.close();
  } finally {
    await rm(f.root, {
      recursive: true,
      force: true,
    });
  }
});
test("host requests cannot expand current task scope, cross-job approvals rejected", async () => {
  const f = await fixture();
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Read source",
        acceptance: "Report result",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const started = await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    f.codex.emit("request", {
      id: "approval-test",
      method: "item/commandExecution/requestApproval",
      params: {
        threadId: "thread-test",
        turnId: "turn-test",
        command: "outside scope",
      },
    });
    const accepted = await f.command(
      "approval.respond",
      {
        job_id: started.result.job.id,
        request_id: "approval-test",
        decision: "accept",
      },
      { project_id: f.binding.id },
    );
    assert.equal(accepted.error.code, "SCOPE_MISMATCH");
    const expired = await f.command(
      "approval.respond",
      {
        job_id: started.result.job.id,
        request_id: "other",
        decision: "decline",
      },
      { project_id: f.binding.id },
    );
    assert.equal(expired.error.code, "APPROVAL_EXPIRED");
  } finally {
    await f.close();
  }
});
test("HTTP rejects hostile origin, missing CSRF, duplicate JSON and unbound artifacts", async () => {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-http-"));
  const dist = join(root, "dist");
  await mkdir(dist);
  await writeFile(join(dist, "index.html"), "<html>Atelier</html>");
  const app = new Application({
    dataDir: join(root, "data"),
    repoRoot,
    codex: new FakeCodex(),
  });
  const running = await createServer({
    port: 0,
    dist,
    application: app,
  });
  try {
    const home = await fetch(running.origin);
    assert.equal(home.headers.get("set-cookie"), null);
    assert.equal((await fetch(running.origin + "/api/v1/session")).status, 401);
    const claim = await fetch(running.origin + "/api/v1/session", {
      method: "POST",
      headers: { Origin: running.origin, "Content-Type": "application/json" },
      body: JSON.stringify({
        launch_token: launchToken(running.ownerSession.controlKey),
      }),
    });
    assert.equal(claim.status, 200);
    const cookie = claim.headers.get("set-cookie").split(";")[0];
    const bootstrap = await (
      await fetch(running.origin + "/api/v1/bootstrap", { headers: { cookie } })
    ).json();
    const hostile = await fetch(running.origin + "/api/v1/bootstrap", {
      headers: {
        cookie,
        Origin: "https://hostile.example",
      },
    });
    assert.equal(hostile.status, 403);
    const noToken = await fetch(running.origin + "/api/v1/commands", {
      method: "POST",
      headers: {
        cookie,
        Origin: running.origin,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        command_id: randomUUID(),
        operation: "service.status",
      }),
    });
    assert.equal(noToken.status, 403);
    const duplicate = await fetch(running.origin + "/api/v1/commands", {
      method: "POST",
      headers: {
        cookie,
        Origin: running.origin,
        "Content-Type": "application/json",
        "X-Atelier-CSRF": bootstrap.csrf_token,
      },
      body: '{"command_id":"12345678","operation":"service.status","operation":"service.stop"}',
    });
    assert.equal(duplicate.status, 400);
    assert.equal((await duplicate.json()).error.code, "DUPLICATE_JSON_KEY");
    const other = await fetch(
      running.origin + "/api/v1/projects/not-bound/artifact?path=secret.txt",
      { headers: { cookie } },
    );
    assert.equal(other.status, 404);
  } finally {
    await running.close();
    await rm(root, {
      recursive: true,
      force: true,
    });
  }
});
test("declared requirement closure matches shared Python compiler fixture", async () => {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-context-"));
  try {
    await writeFile(join(root, "source.md"), "Accepted original\n");
    const requirements = [
      {
        id: "A",
        source_ref: "source.md",
        verbatim: "Always retain identity",
        interpretation: "Identity retained",
        priority: "must",
        applicable: true,
        dependencies: ["B"],
        acceptance: "Identity retained",
        owner: "integrator",
        due_gate: "release",
      },
      {
        id: "B",
        source_ref: "source.md",
        verbatim: "Preserve source",
        interpretation: "Source retained",
        priority: "should",
        applicable: true,
        dependencies: [],
        acceptance: "Source unchanged",
        owner: "integrator",
        due_gate: "now",
      },
      {
        id: "C",
        source_ref: "source.md",
        verbatim: "Unassigned",
        interpretation: "Later optional work",
        priority: "could",
        applicable: true,
        dependencies: [],
        acceptance: "Later",
        owner: "integrator",
        due_gate: "later",
      },
    ];
    const projection = {
      schema_version: "atelier.context-projection/1",
      project_id: "P",
      native_revision: "r1",
      requirements,
      inputs: [
        {
          id: "source",
          path: "source.md",
          sha256: sha("Accepted original\n"),
        },
      ],
      tasks: [
        {
          id: "T",
          objective: "Inspect source",
          owner: "integrator",
          authority_ref: "real-user-request",
          gate: "now",
          stop: "after result",
          recovery: "read checkpoint",
          requirement_ids: ["B"],
          input_ids: ["source"],
          budget: { seconds: 60 },
          outputs: ["report"],
        },
      ],
    };
    await writeFile(join(root, "projection.json"), JSON.stringify(projection));
    execFileSync("python3", [
      "-B",
      join(repoRoot, "standards/context_capsule.py"),
      "build",
      "--root",
      root,
      "--input",
      "projection.json",
      "--task",
      "T",
      "--output",
      "capsule.json",
    ]);
    const python = JSON.parse(
      await readFile(join(root, "capsule.json"), "utf8"),
    );
    const js = selectRequirements(requirements, ["B"]);
    assert.deepEqual(
      js.selected.map((x) => x.id),
      python.requirements.map((x) => x.id),
    );
    assert.deepEqual(
      js.omitted.map((x) => x.id),
      python.omitted_requirements.map((x) => x.id),
    );
    assert.equal(python.quality_certified, false);
    assert.equal(python.inputs[0].sha256, sha("Accepted original\n"));
  } finally {
    await rm(root, {
      recursive: true,
      force: true,
    });
  }
});
test("queued interrupt persists until actual turn start, then confirms terminal cancellation", async () => {
  const f = await fixture();
  try {
    f.codex.turn = async (_threadId, _capsule, onDispatch) => {
      onDispatch?.();
      return { turn: { id: "turn-test" } };
    };
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Read sources",
        acceptance: "Return actual sources",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const start = await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(start.result.job.status, "queued");
    const cancel = await f.command(
      "job.interrupt",
      { job_id: start.result.job.id },
      { project_id: f.binding.id },
    );
    assert.equal(cancel.result.job.status, "cancel_requested");
    assert.equal(f.codex.interrupted, undefined);
    f.codex.emit("notification", {
      method: "turn/started",
      params: {
        threadId: "thread-test",
        turn: {
          id: "turn-test",
          status: "inProgress",
        },
      },
      observed_at: new Date().toISOString(),
    });
    await new Promise((r) => setImmediate(r));
    assert.equal(f.codex.interrupted, true);
    f.codex.emit("notification", {
      method: "turn/completed",
      params: {
        threadId: "thread-test",
        turn: {
          id: "turn-test",
          status: "interrupted",
        },
      },
      observed_at: new Date().toISOString(),
    });
    assert.equal(
      f.app.store.get("job", start.result.job.id).status,
      "cancelled",
    );
  } finally {
    await f.close();
  }
});
test("backup restore preserves later command receipts and invalidates old dispatch authority", async () => {
  const f = await fixture();
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect source",
        acceptance: "Return result",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const backup = await f.command("service.backup");
    const laterId = randomUUID();
    await f.app.execute({
      command_id: laterId,
      operation: "service.settings",
      payload: { locale: "en" },
    });
    const preview = await f.command("service.restore-preview", {
      backup_id: backup.result.backup_id,
    });
    assert.equal(preview.status, "completed");
    const command = {
      command_id: randomUUID(),
      operation: "service.restore",
      payload: {
        backup_id: backup.result.backup_id,
        sha256: backup.result.sha256,
        confirmed: true,
      },
    };
    const restored = await f.app.execute(command);
    assert.equal(restored.status, "completed");
    assert.equal(
      f.app.store
        .events(0, 1000)
        .every((event) => event.data && typeof event.data === "object"),
      true,
    );
    assert.equal(f.app.store.get("settings", "owner").locale, "uk");
    assert.ok(f.app.store.commandGet(laterId));
    assert.equal(
      f.app.store.get("task", prepared.result.task.id).status,
      "restored_requires_preparation",
    );
    const replay = await f.app.execute(command);
    assert.equal(digest(replay), digest(restored));
    const dispatch = await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(dispatch.error.code, "TASK_NOT_READY");
  } finally {
    await f.close();
  }
});
test("existing thread preview/adoption rejects wrong cwd and active host status", async () => {
  const f = await fixture();
  try {
    f.codex.readThread = async (threadId) => ({
      thread: {
        id: threadId,
        cwd: "/another-project",
        status: { type: "idle" },
      },
    });
    let preview = await f.command(
      "thread.preview",
      { thread_id: "existing" },
      { project_id: f.binding.id },
    );
    assert.equal(preview.error.code, "SCOPE_MISMATCH");
    f.codex.readThread = async (threadId) => ({
      thread: {
        id: threadId,
        cwd: f.project,
        status: { type: "active" },
      },
    });
    preview = await f.command(
      "thread.preview",
      { thread_id: "existing" },
      { project_id: f.binding.id },
    );
    const active = await f.command(
      "thread.adopt",
      {
        preview_id: preview.result.preview_id,
        confirmed_idle_handoff: true,
      },
      { project_id: f.binding.id },
    );
    assert.equal(active.error.code, "WRITER_CONFLICT");
    f.codex.readThread = async (threadId) => ({
      thread: {
        id: threadId,
        cwd: f.project,
        status: { type: "idle" },
      },
    });
    preview = await f.command(
      "thread.preview",
      { thread_id: "existing" },
      { project_id: f.binding.id },
    );
    const adopted = await f.command(
      "thread.adopt",
      {
        preview_id: preview.result.preview_id,
        confirmed_idle_handoff: true,
      },
      { project_id: f.binding.id },
    );
    assert.equal(adopted.result.thread_binding.global_fencing, false);
    assert.equal(
      adopted.result.thread_binding.handoff_kind,
      "owner-confirmed-idle-manual",
    );
  } finally {
    await f.close();
  }
});

test("atomic reservation survives concurrent dispatch awaits and consumes each task once", async () => {
  const f = await fixture();
  try {
    const prepare = () =>
      f.command(
        "task.prepare",
        {
          objective: "Inspect sources",
          acceptance: "Actual result",
          scope: "workspace-write",
          allowed_paths: ["."],
          deadline_seconds: 60,
        },
        { project_id: f.binding.id },
      );
    const a = await prepare(),
      b = await prepare();
    let release;
    f.codex.connect = () =>
      new Promise((resolve) => {
        release = resolve;
      });
    const first = f.command(
      "task.dispatch",
      { task_id: a.result.task.id },
      { project_id: f.binding.id },
    );
    await new Promise((r) => setImmediate(r));
    const second = await f.command(
      "task.dispatch",
      { task_id: b.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(second.error.code, "WRITER_CONFLICT");
    release({ status: "connected" });
    await first;
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});
test("raw resume override and wrong-turn terminal cannot free current writer", async () => {
  const f = await fixture();
  try {
    const p = await f.command(
      "task.prepare",
      {
        objective: "Inspect sources",
        acceptance: "Actual result",
        scope: "workspace-write",
        allowed_paths: ["."],
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const rejected = await f.command(
      "task.dispatch",
      { task_id: p.result.task.id, resume_thread_id: "foreign-thread" },
      { project_id: f.binding.id },
    );
    assert.equal(rejected.error.code, "SCOPE_MISMATCH");
    assert.equal(f.codex.starts, 0);
    const started = await f.command(
      "task.dispatch",
      { task_id: p.result.task.id },
      { project_id: f.binding.id },
    );
    f.codex.emit("notification", {
      method: "turn/completed",
      params: {
        threadId: "thread-test",
        turn: { id: "foreign-turn", status: "completed" },
      },
      observed_at: new Date().toISOString(),
    });
    assert.equal(
      f.app.store.get("job", started.result.job.id).status,
      "running",
    );
    f.codex.emit("notification", {
      method: "item/agentMessage/delta",
      params: {
        threadId: "thread-test",
        turnId: "turn-test",
        delta: "sk-ABCDEFGHIJKLMNOP1234567890",
      },
      observed_at: new Date().toISOString(),
    });
    assert.ok(
      !JSON.stringify(f.app.store.get("job", started.result.job.id)).includes(
        "sk-ABCDEFGHIJKLMNOP",
      ),
    );
  } finally {
    await f.close();
  }
});
test("disconnect converts queued turn to unknown and prevents automatic replay", async () => {
  const f = await fixture();
  try {
    f.codex.turn = async (_thread, _capsule, onDispatch) => {
      onDispatch?.();
      return { turn: { id: "turn-test" } };
    };
    const p = await f.command(
      "task.prepare",
      {
        objective: "Inspect sources",
        acceptance: "Actual result",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const started = await f.command(
      "task.dispatch",
      { task_id: p.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(started.result.job.status, "queued");
    f.codex.emit("disconnected", {});
    assert.equal(
      f.app.store.get("job", started.result.job.id).status,
      "outcome_unknown",
    );
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});
test("single service owner is acquired before another instance opens the same SQLite state", async () => {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-singleton-"),
  );
  const dist = join(root, "dist");
  await mkdir(dist);
  await writeFile(join(dist, "index.html"), "<html>Atelier</html>");
  const first = await createServer({
    dataDir: join(root, "data"),
    repoRoot,
    dist,
    port: 0,
  });
  try {
    await assert.rejects(
      createServer({ dataDir: join(root, "data"), repoRoot, dist, port: 0 }),
      /Another service process/,
    );
  } finally {
    await first.close();
    await rm(root, { recursive: true, force: true });
  }
});

test("all supported native authority directories are read-only in task policy", () => {
  const profile = localProfile(
    "workspace-write",
    ["."],
    [],
    "/private/tmp/project",
  );
  for (const path of [
    ".agent-foundry",
    ".appatelier",
    ".chatbotatelier",
    ".chatbot-atelier",
    ".gameatelier",
    ".atelier",
  ]) {
    assert.equal(profile.filesystem[":workspace_roots"][path], "read", path);
  }
  assert.equal(profile.filesystem[":workspace_roots"]["."], "write");
});

test("installed skill previews reject linked source or ancestor escape", async () => {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-installed-"),
  );
  try {
    await mkdir(join(root, "skills"));
    await mkdir(join(root, "skills/safe-skill"));
    await writeFile(join(root, "outside.txt"), "synthetic");
    await symlink(
      join(root, "outside.txt"),
      join(root, "skills/safe-skill/SKILL.md"),
    );
    await assert.rejects(
      readInstalledSource(join(root, "skills"), "safe-skill"),
      /Symlink/,
    );
    await symlink(join(root, "skills"), join(root, "alias"));
    await assert.rejects(
      readInstalledSource(join(root, "alias"), "safe-skill"),
      /Linked installed root/,
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("private service state cannot be bound through canonical or alias root", async () => {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-private-alias-"),
  );
  let app;
  try {
    await mkdir(join(root, "state"));
    await symlink(join(root, "state"), join(root, "state-alias"));
    app = new Application({
      dataDir: join(root, "state-alias"),
      repoRoot,
      codex: new FakeCodex(),
    });
    const result = await app.execute({
      command_id: randomUUID(),
      operation: "project.preview",
      payload: { root: join(root, "state") },
    });
    assert.equal(result.error.code, "PRIVATE_PATH");
    assert.equal(app.dataDir, join(root, "state"));
    const ancestor = await app.execute({
      command_id: randomUUID(),
      operation: "project.preview",
      payload: { root },
    });
    assert.equal(ancestor.error.code, "PRIVATE_PATH");
  } finally {
    if (app) await app.close();
    await rm(root, { recursive: true, force: true });
  }
});

test("cleanup tombstones prevent service backup from reviving forgotten project content", async () => {
  const f = await fixture();
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect synthetic fixture",
        acceptance: "Report fixture",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const backup = await f.command("service.backup");
    assert.equal(backup.status, "completed");
    const cleanup = await f.command("service.cleanup-preview", {
      forget_project_ids: [f.binding.id],
    });
    assert.equal(cleanup.status, "completed");
    const applied = await f.command("service.cleanup-apply", {
      preview_id: cleanup.result.preview_id,
      sha256: cleanup.result.sha256,
      confirmed: true,
    });
    assert.equal(applied.status, "completed");
    assert.equal(f.app.store.get("project", f.binding.id), null);
    const preview = await f.command("service.restore-preview", {
      backup_id: backup.result.backup_id,
    });
    assert.equal(preview.status, "completed");
    const restored = await f.command("service.restore", {
      backup_id: backup.result.backup_id,
      sha256: backup.result.sha256,
      confirmed: true,
    });
    assert.equal(restored.status, "completed");
    assert.equal(
      f.app.store
        .events(0, 1000)
        .every((event) => event.data && typeof event.data === "object"),
      true,
    );
    assert.equal(f.app.store.get("project", f.binding.id), null);
    assert.equal(f.app.store.get("task", prepared.result.task.id), null);
    assert.equal(
      f.app.store
        .events(0, 1000)
        .some((row) => JSON.stringify(row.data).includes(f.binding.id)),
      false,
    );
  } finally {
    await f.close();
  }
});
test("cleanup maintenance reserves its barrier before asynchronous file cleanup", async () => {
  const f = await fixture();
  let release;
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect synthetic fixture",
        acceptance: "Report fixture",
        scope: "workspace-write",
        allowed_paths: ["."],
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    f.app.retention.apply = () =>
      new Promise((resolve) => {
        release = () => resolve({ status: "completed" });
      });
    const cleanup = f.command("service.cleanup-apply", {
      preview_id: "synthetic",
      sha256: "synthetic",
      confirmed: true,
    });
    assert.equal(f.app.maintenanceOperation, "cleanup");
    const blocked = await f.command(
      "task.dispatch",
      { task_id: prepared.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(blocked.error.code, "SERVICE_STOPPING");
    assert.equal(f.codex.starts, 0);
    release();
    assert.equal((await cleanup).status, "completed");
    assert.equal(f.app.maintenanceOperation, null);
  } finally {
    release?.();
    await f.close();
  }
});

test("pruned task context cannot resume or dispatch even with no selected skills", async () => {
  const f = await fixture();
  let hostCalls = 0;
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect fixture",
        acceptance: "Report fixture",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const task = prepared.result.task;
    f.app.store.put("job", "job-pruned-fixture", {
      id: "job-pruned-fixture",
      task_id: task.id,
      project_id: f.binding.id,
      status: "cancelled",
      thread_id: "thread-test",
      scope: "read-only",
    });
    f.app.store.put("task", task.id, {
      ...task,
      status: "dispatched",
      requires_prepare: true,
      input_cache_pruned: true,
    });
    f.codex.connect = async () => {
      hostCalls++;
      return f.codex.status;
    };
    f.codex.resume = async () => {
      hostCalls++;
      return { thread: { id: "thread-test" } };
    };
    const continued = await f.command(
      "task.continue",
      { task_id: task.id },
      { project_id: f.binding.id },
    );
    assert.equal(continued.error.code, "TASK_NOT_READY");
    f.app.store.put("task", task.id, {
      ...f.app.task(task.id),
      status: "prepared",
    });
    const dispatched = await f.command(
      "task.dispatch",
      { task_id: task.id },
      { project_id: f.binding.id },
    );
    assert.equal(dispatched.error.code, "TASK_NOT_READY");
    assert.equal(hostCalls, 0);
    assert.equal(f.codex.starts, 0);
  } finally {
    await f.close();
  }
});

test("oversized durable context is rejected before poisoning later reads", async () => {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-capacity-"));
  const store = new Store(join(root, "state.sqlite"));
  try {
    assert.throws(
      () =>
        store.put("task", "oversized", {
          id: "oversized",
          content: "x".repeat(2 * 1024 * 1024),
        }),
      (error) => error.code === "CAPACITY_LIMIT",
    );
    assert.equal(store.get("task", "oversized"), null);
    store.put("task", "small", { id: "small", content: "valid" });
    assert.equal(store.list("task").length, 1);
  } finally {
    store.close();
    await rm(root, { recursive: true, force: true });
  }
});

test("overlapping canonical project roots share one writer boundary", async () => {
  const scenarios = [
    {
      first: "parent",
      first_scope: "workspace-write",
      second: "child",
      second_scope: "workspace-write",
    },
    {
      first: "parent",
      first_scope: "workspace-write",
      second: "child",
      second_scope: "read-only",
    },
    {
      first: "parent",
      first_scope: "read-only",
      second: "child",
      second_scope: "workspace-write",
    },
    {
      first: "child",
      first_scope: "workspace-write",
      second: "parent",
      second_scope: "read-only",
    },
    {
      first: "child",
      first_scope: "read-only",
      second: "parent",
      second_scope: "workspace-write",
    },
    {
      first: "parent",
      first_scope: "workspace-write",
      second: "child",
      second_scope: "read-only",
      unknown: true,
    },
    {
      first: "child",
      first_scope: "read-only",
      second: "parent",
      second_scope: "workspace-write",
      unknown: true,
    },
    {
      first: "parent",
      first_scope: "workspace-write",
      second: "child",
      second_scope: "workspace-write",
      unknown: true,
      legacy: true,
    },
  ];
  for (const scenario of scenarios) {
    const f = await fixture();
    try {
      const childRoot = join(f.project, "nested");
      await mkdir(join(childRoot, ".appatelier"), { recursive: true });
      await writeFile(
        join(childRoot, "AGENTS.md"),
        await readFile(join(f.project, "AGENTS.md")),
      );
      await writeFile(
        join(childRoot, ".appatelier/state.json"),
        await readFile(join(f.project, ".appatelier/state.json")),
      );
      const preview = await f.command("project.preview", { root: childRoot });
      const bound = await f.command("project.bind", {
        preview_id: preview.result.preview_id,
      });
      const projects = { parent: f.binding, child: bound.result.project };
      f.codex.start = async () => {
        f.codex.starts++;
        return { thread: { id: "overlap-thread-" + f.codex.starts } };
      };
      f.codex.turn = async (threadId, _capsule, onDispatch) => {
        onDispatch?.();
        return { turn: { id: threadId + "-turn" } };
      };
      const prepare = async (which, scope) =>
        f.command(
          "task.prepare",
          {
            objective: "Inspect synthetic native content",
            acceptance: "Preserve native content",
            scope,
            ...(scope === "workspace-write" ? { allowed_paths: ["."] } : {}),
            deadline_seconds: 60,
          },
          { project_id: projects[which].id },
        );
      const firstTask = await prepare(scenario.first, scenario.first_scope),
        secondTask = await prepare(scenario.second, scenario.second_scope);
      const first = await f.command(
        "task.dispatch",
        { task_id: firstTask.result.task.id },
        { project_id: projects[scenario.first].id },
      );
      assert.equal(first.status, "completed");
      if (scenario.unknown)
        f.app.updateJob(first.result.job.id, { status: "outcome_unknown" });
      if (scenario.legacy) {
        const old = f.app.job(first.result.job.id);
        delete old.project_root;
        f.app.store.put("job", old.id, old);
      }
      const second = await f.command(
        "task.dispatch",
        { task_id: secondTask.result.task.id },
        { project_id: projects[scenario.second].id },
      );
      assert.equal(
        second.error?.code,
        "WRITER_CONFLICT",
        JSON.stringify({
          scenario,
          host_starts: f.codex.starts,
          first: first.status,
          second: second.status,
        }),
      );
      assert.equal(f.codex.starts, 1);
      assert.equal(f.app.task(secondTask.result.task.id).status, "prepared");
    } finally {
      await f.close();
    }
  }
});

test("disjoint canonical projects retain concurrent writer admission including unknown outcome", async () => {
  const f = await fixture();
  try {
    const sibling = join(f.root, "project-neighbor");
    await mkdir(join(sibling, ".appatelier"), { recursive: true });
    await writeFile(
      join(sibling, "AGENTS.md"),
      await readFile(join(f.project, "AGENTS.md")),
    );
    await writeFile(
      join(sibling, ".appatelier/state.json"),
      await readFile(join(f.project, ".appatelier/state.json")),
    );
    const preview = await f.command("project.preview", { root: sibling });
    const binding = await f.command("project.bind", {
      preview_id: preview.result.preview_id,
    });
    f.codex.start = async () => {
      f.codex.starts++;
      return { thread: { id: "disjoint-thread-" + f.codex.starts } };
    };
    f.codex.turn = async (threadId, _capsule, onDispatch) => {
      onDispatch?.();
      return { turn: { id: threadId + "-turn" } };
    };
    const prepare = async (project) =>
      f.command(
        "task.prepare",
        {
          objective: "Inspect synthetic native content",
          acceptance: "Preserve content",
          scope: "workspace-write",
          allowed_paths: ["."],
          deadline_seconds: 60,
        },
        { project_id: project.id },
      );
    const a = await prepare(f.binding),
      b = await prepare(binding.result.project);
    const first = await f.command(
      "task.dispatch",
      { task_id: a.result.task.id },
      { project_id: f.binding.id },
    );
    assert.equal(first.status, "completed");
    assert.equal(first.result.job.project_root, f.project);
    f.app.updateJob(first.result.job.id, { status: "outcome_unknown" });
    const second = await f.command(
      "task.dispatch",
      { task_id: b.result.task.id },
      { project_id: binding.result.project.id },
    );
    assert.equal(second.status, "completed");
    assert.equal(second.result.job.project_root, sibling);
    assert.equal(f.codex.starts, 2);
  } finally {
    await f.close();
  }
});
test("overlapping read-only roots share two readers while disjoint roots keep their own capacity", async () => {
  const f = await fixture();
  try {
    const bind = async (root) => {
      await mkdir(join(root, ".appatelier"), { recursive: true });
      await writeFile(
        join(root, "AGENTS.md"),
        await readFile(join(f.project, "AGENTS.md")),
      );
      await writeFile(
        join(root, ".appatelier/state.json"),
        await readFile(join(f.project, ".appatelier/state.json")),
      );
      const preview = await f.command("project.preview", { root });
      return (
        await f.command("project.bind", {
          preview_id: preview.result.preview_id,
        })
      ).result.project;
    };
    const child = await bind(join(f.project, "nested")),
      other = await bind(join(f.root, "project-neighbor"));
    f.codex.start = async () => {
      f.codex.starts++;
      return { thread: { id: "reader-thread-" + f.codex.starts } };
    };
    f.codex.turn = async (threadId, _capsule, onDispatch) => {
      onDispatch?.();
      return { turn: { id: threadId + "-turn" } };
    };
    const dispatch = async (project) => {
      const prepared = await f.command(
        "task.prepare",
        {
          objective: "Inspect synthetic native content",
          acceptance: "Preserve content",
          scope: "read-only",
          deadline_seconds: 60,
        },
        { project_id: project.id },
      );
      return f.command(
        "task.dispatch",
        { task_id: prepared.result.task.id },
        { project_id: project.id },
      );
    };
    assert.equal((await dispatch(f.binding)).status, "completed");
    assert.equal((await dispatch(child)).status, "completed");
    assert.equal((await dispatch(child)).error.code, "CAPACITY_LIMIT");
    assert.equal((await dispatch(other)).status, "completed");
    assert.equal((await dispatch(other)).status, "completed");
    assert.equal((await dispatch(other)).error.code, "CAPACITY_LIMIT");
    assert.equal(f.codex.starts, 4);
  } finally {
    await f.close();
  }
});
