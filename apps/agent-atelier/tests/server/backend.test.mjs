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
import { parseStrictJson, safeFile, digest, sha, ServiceError } from "../../server/utils.mjs";
import { Store } from "../../server/store.mjs";
import { Application } from "../../server/application.mjs";
import { createServer } from "../../server/index.mjs";
import { launchToken } from "../../server/session.mjs";
import { localProfile } from "../../server/permissions.mjs";
import { readInstalledSource } from "../../server/skills.mjs";
import { selectRequirements } from "../../server/context.mjs";
const repoRoot = resolve(import.meta.dirname, "../../../..");

function writeProductionChoice(project, targetKind = "script") {
  const python = process.env.AGENT_SYSTEM_PYTHON || (process.platform === "win32" ? "python" : "python3");
  const source = "import sys; sys.path.insert(0, 'scripts/tests'); " +
    "from fixture_production_choices import make_choice; make_choice(sys.argv[1], target_kind=sys.argv[2])";
  execFileSync(python, ["-B", "-c", source, project, targetKind], { cwd: repoRoot });
}

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
  async turn(_threadId, _capsule, onDispatch, verifyBeforeDispatch) {
    await verifyBeforeDispatch?.();
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
test("production prepare and dispatch bind a decision and stop changed masters before the native start", async () => {
  const f = await fixture();
  const request = {
    objective: "Prepare an approved web implementation",
    acceptance: "Preserve the master and navigation",
    scope: "read-only",
    production_phase: "implement",
    deadline_seconds: 60,
  };
  const target = { project_id: f.binding.id, expected_revision: f.binding.revision };
  try {
    const missing = await f.command("task.prepare", request, target);
    assert.equal(missing.error.code, "PRODUCTION_CHOICE_REQUIRED");
    writeProductionChoice(f.project, "web");
    const prep = await f.command("task.prepare", request, target);
    assert.equal(prep.status, "completed");
    const { task, capsule } = prep.result;
    assert.equal(capsule.production_choice.phase, "implement");
    assert.equal(capsule.production_choice.sha256, sha(await readFile(join(f.project, "production-choices.json"))));
    const master = join(f.project, "_choice-fixture", "master.html");
    const original = await readFile(master);
    await writeFile(master, "<main>Unapproved replacement</main>");
    const denied = await f.command("task.dispatch", { task_id: task.id }, target);
    assert.equal(denied.error.code, "PRODUCTION_CHOICE_REQUIRED");
    assert.match(denied.error.message, /master\.html/);
    assert.equal(f.codex.starts, 0);
    await writeFile(master, original);
    const retry = await f.command("task.prepare", request, target);
    assert.equal(retry.status, "completed");
    const run = await f.command("task.dispatch", { task_id: retry.result.task.id }, target);
    assert.equal(run.status, "completed");
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});
test("new writable tasks require an approved choice even when labeled repair", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  const request = {
    objective: "Fix the cable label in the synthetic source",
    acceptance: "Only the documented label changes",
    scope: "workspace-write",
    allowed_paths: ["src"],
    deadline_seconds: 60,
  };
  try {
    await mkdir(join(f.project, "src"));
    assert.equal(f.binding.production_choice_policy, 1);
    const automatic = await f.command("task.prepare", request, target);
    assert.equal(automatic.error.code, "PRODUCTION_CHOICE_REQUIRED");
    const fakeRepair = await f.command("task.prepare", { ...request, production_phase: "repair" }, target);
    assert.equal(fakeRepair.error.code, "PRODUCTION_CHOICE_REQUIRED");
    assert.deepEqual(f.app.store.list("task"), []);
    assert.equal(f.codex.starts, 0);
    writeProductionChoice(f.project);
    const prepared = await f.command("task.prepare", request, target);
    assert.equal(prepared.status, "completed");
    assert.equal(prepared.result.capsule.production_choice.phase, "implement");
  } finally {
    await f.close();
  }
});

test("explicit legacy repair keeps the existing writer route and rejects a newly appearing choice", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  const request = {
    objective: "Fix the cable label in the synthetic source",
    acceptance: "Only the documented label changes",
    scope: "workspace-write",
    allowed_paths: ["src"],
    deadline_seconds: 60,
  };
  try {
    await mkdir(join(f.project, "src"));
    const { production_choice_policy: policy, ...legacy } = f.app.projects.get(f.binding.id);
    assert.equal(policy, 1);
    f.app.store.put("project", legacy.id, legacy, legacy.record_revision);
    const implicit = await f.command("task.prepare", request, target);
    assert.equal(implicit.error.code, "PRODUCTION_CHOICE_REQUIRED");
    const prepareRepair = () => f.command("task.prepare", { ...request, production_phase: "repair" }, target);
    const prepared = await prepareRepair();
    assert.equal(prepared.status, "completed");
    assert.deepEqual(prepared.result.capsule.production_choice, { phase: "repair", legacy: true });
    assert.deepEqual(prepared.result.capsule.allowed_paths, ["src"]);
    const started = await f.command("task.dispatch", { task_id: prepared.result.task.id }, target);
    assert.equal(started.status, "completed");
    assert.equal(started.result.job.status, "running");
    assert.equal(f.codex.starts, 1);
    f.codex.emit("notification", {
      method: "turn/completed",
      params: { threadId: "thread-test", turn: { id: "turn-test", status: "completed" } },
      observed_at: new Date().toISOString(),
    });
    assert.equal(f.app.store.get("job", started.result.job.id).status, "completed");
    const stale = await prepareRepair();
    assert.equal(stale.status, "completed");
    writeProductionChoice(f.project);
    const denied = await f.command("task.dispatch", { task_id: stale.result.task.id }, target);
    assert.equal(denied.error.code, "SOURCE_DRIFT");
    assert.equal(f.codex.starts, 1);
    const current = await prepareRepair();
    assert.equal(current.status, "completed");
    assert.equal(current.result.capsule.production_choice.phase, "implement");
  } finally {
    await f.close();
  }
});

test("legacy repair rejects normalized root-wide paths and mixed bounds", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  try {
    const { production_choice_policy: _policy, ...legacy } = f.app.projects.get(f.binding.id);
    f.app.store.put("project", legacy.id, legacy, legacy.record_revision);
    await mkdir(join(f.project, "src"));
    for (const allowed_paths of [["."], ["././"], ["src", "."]]) {
      const result = await f.command("task.prepare", {
        objective: "Fix a label in an existing module",
        acceptance: "Only the named label changes",
        scope: "workspace-write",
        production_phase: "repair",
        allowed_paths,
        deadline_seconds: 60,
      }, target);
      assert.equal(result.error?.code, "PRODUCTION_CHOICE_REQUIRED", JSON.stringify(allowed_paths));
    }
    assert.deepEqual(f.app.store.list("task"), []);
    assert.equal(f.codex.starts, 0);
  } finally {
    await f.close();
  }
});

test("old unbound writer cannot dispatch or resume and retains its history", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  try {
    const { production_choice_policy: _policy, ...legacy } = f.app.projects.get(f.binding.id);
    f.app.store.put("project", legacy.id, legacy, legacy.record_revision);
    await mkdir(join(f.project, "src"));
    const prepared = await f.command("task.prepare", {
      objective: "Fix a label in an existing module",
      acceptance: "Only the named label changes",
      scope: "workspace-write",
      production_phase: "repair",
      allowed_paths: ["src"],
      deadline_seconds: 60,
    }, target);
    assert.equal(prepared.status, "completed");
    const { production_choice: _choice, capsule_sha256: _digest, ...previousCapsule } = prepared.result.capsule;
    const capsule = { ...previousCapsule, capsule_sha256: digest(previousCapsule) };
    const task = { ...prepared.result.task, capsule };
    f.app.store.put("task", task.id, task);
    let hostCalls = 0;
    const connect = f.codex.connect.bind(f.codex);
    f.codex.connect = async () => {
      hostCalls++;
      return connect();
    };
    const dispatched = await f.command("task.dispatch", { task_id: task.id }, target);
    assert.equal(dispatched.error?.code, "PRODUCTION_CHOICE_REQUIRED");
    assert.match(dispatched.error.message, /prepare/i);

    f.app.store.put("task", task.id, { ...task, status: "paused" });
    const prior = { id: randomUUID(), project_id: f.binding.id, task_id: task.id,
      scope: "workspace-write", thread_id: "thread-test", status: "paused" };
    f.app.store.put("job", prior.id, prior);
    const oldTask = f.app.store.get("task", task.id);
    const oldJob = f.app.store.get("job", prior.id);
    const continued = await f.command("task.continue", { task_id: task.id }, target);
    assert.equal(continued.error?.code, "PRODUCTION_CHOICE_REQUIRED");
    assert.match(continued.error.message, /prepare/i);
    assert.deepEqual(f.app.store.get("task", task.id), oldTask);
    assert.deepEqual(f.app.store.get("job", prior.id), oldJob);
    assert.equal(hostCalls, 0);
    assert.equal(f.codex.starts, 0);
    assert.equal(f.codex.interrupted, undefined);

    const reader = await f.command("task.prepare", {
      objective: "Check the saved task history",
      acceptance: "All project files stay read-only",
      scope: "read-only",
    }, target);
    assert.equal(reader.status, "completed");
    assert.equal(reader.result.capsule.production_choice, undefined);
    const read = await f.command("task.dispatch", { task_id: reader.result.task.id }, target);
    assert.equal(read.status, "completed");
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});

test("legacy repair requires a governing source outside its write scope", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  try {
    const { production_choice_policy: _policy, ...legacy } = f.app.projects.get(f.binding.id);
    f.app.store.put("project", legacy.id, legacy, legacy.record_revision);
    await rm(join(f.project, "AGENTS.md"));
    await rm(join(f.project, ".appatelier"), { recursive: true });
    await mkdir(join(f.project, "src"));
    await writeFile(join(f.project, "src/settings.txt"), "Original settings");
    const request = {
      objective: "Fix a label in an existing module",
      acceptance: "Only the named label changes",
      scope: "workspace-write",
      production_phase: "repair",
      allowed_paths: ["src"],
      source_paths: ["src/settings.txt"],
      deadline_seconds: 60,
    };
    const denied = await f.command("task.prepare", request, target);
    assert.equal(denied.error.code, "PRODUCTION_CHOICE_REQUIRED");
    assert.match(denied.error.message, /governing project source/);
    await mkdir(join(f.project, "docs"));
    await writeFile(join(f.project, "docs/requirements.md"), "Keep the established behavior.");
    const alias = join(f.project, "DOCS");
    let sameDirectory = false;
    try {
      sameDirectory = realpathSync(alias) === join(f.project, "docs");
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    for (const path of sameDirectory ? ["docs", "DOCS"] : ["docs"]) {
      const enclosed = await f.command("task.prepare", { ...request, allowed_paths: [path] }, target);
      assert.equal(enclosed.error.code, "PRODUCTION_CHOICE_REQUIRED");
    }
    await rm(join(f.project, "docs"), { recursive: true });
    await writeFile(join(f.project, "README.md"), "The existing input contract must stay compatible.");
    const prepared = await f.command("task.prepare", request, target);
    assert.equal(prepared.status, "completed");
    await rm(join(f.project, "src"), { recursive: true });
    const dispatch = await f.command("task.dispatch", { task_id: prepared.result.task.id }, target);
    assert.equal(dispatch.error.code, "SOURCE_DRIFT");
    assert.match(dispatch.error.message, /directory changed/);
    assert.equal(f.codex.starts, 0);
  } finally {
    await f.close();
  }
});

test("legacy repair rechecks a changed governing choice after native resume before starting a turn", async () => {
  const f = await fixture();
  const target = { project_id: f.binding.id };
  try {
    const { production_choice_policy: _policy, ...legacy } = f.app.projects.get(f.binding.id);
    f.app.store.put("project", legacy.id, legacy, legacy.record_revision);
    await mkdir(join(f.project, "src"));
    const request = {
      objective: "Fix a label in an existing module",
      acceptance: "Only the named label changes",
      scope: "workspace-write",
      production_phase: "repair",
      allowed_paths: ["src"],
      deadline_seconds: 60,
    };
    const prepared = await f.command("task.prepare", request, target);
    assert.equal(prepared.status, "completed");
    const task = prepared.result.task;
    f.app.store.put("task", task.id, { ...task, status: "paused" });
    const prior = {
      id: randomUUID(), project_id: f.binding.id, task_id: task.id,
      scope: "workspace-write", thread_id: "thread-test", status: "paused",
    };
    f.app.store.put("job", prior.id, prior);
    const saved = f.app.store.get("job", prior.id);
    let resumed = false, turns = 0;
    f.codex.readThread = async () => ({
      thread: { id: prior.thread_id, cwd: f.project, status: { type: "idle" } },
    });
    f.codex.resume = async () => {
      resumed = true;
      writeProductionChoice(f.project);
      return { thread: { id: prior.thread_id } };
    };
    f.codex.turn = async (_threadId, _capsule, _onDispatch, verifyBeforeDispatch) => {
      await verifyBeforeDispatch?.();
      turns++;
      throw new Error("Unbound turn started");
    };
    const result = await f.command("task.continue", { task_id: task.id }, target);
    assert.equal(result.error?.code, "SOURCE_DRIFT");
    assert.equal(resumed, true);
    assert.equal(turns, 0);
    assert.deepEqual(f.app.store.get("job", prior.id), saved);
    assert.equal(f.app.store.list("job").find((job) => job.id !== prior.id).host_dispatch_started, false);
  } finally {
    await f.close();
  }
});

test("current choice drift after native open never reaches turn/start", async (t) => {
  for (const stage of ["thread open", "turn preflight"]) {
    await t.test(stage, async () => {
      const f = await fixture();
      const target = { project_id: f.binding.id };
      try {
        writeProductionChoice(f.project);
        const record = join(f.project, "production-choices.json");
        const original = await readFile(record, "utf8");
        const replaceChoice = () => writeFile(record, original + "\n");
        const prepared = await f.command("task.prepare", {
          objective: "Fix a label using the approved production choice",
          acceptance: "Record identity and the other settings stay unchanged",
          scope: "workspace-write",
          allowed_paths: ["."],
        }, target);
        assert.equal(prepared.status, "completed");
        assert.equal(prepared.result.capsule.production_choice.sha256, sha(original));
        let sent = 0;
        const start = f.codex.start.bind(f.codex);
        f.codex.start = async () => {
          const opened = await start();
          if (stage === "thread open") await replaceChoice();
          return opened;
        };
        f.codex.turn = async (threadId, capsule, onDispatch, verifyBeforeDispatch) => {
          if (stage === "turn preflight") await replaceChoice();
          await verifyBeforeDispatch?.();
          onDispatch();
          sent++;
          return { turn: { id: threadId + "-turn" } };
        };
        const result = await f.command("task.dispatch", { task_id: prepared.result.task.id }, target);
        assert.equal(result.error?.code, "PRODUCTION_CHOICE_REQUIRED");
        assert.equal(f.codex.starts, 1);
        assert.equal(sent, 0);
        const [job] = f.app.store.list("job");
        assert.equal(job.thread_id, "thread-test");
        assert.equal(job.host_dispatch_started, false);
      } finally {
        await f.close();
      }
    });
  }
});

test("native model mismatch records the acknowledged thread before rejecting any turn", async () => {
  const f = await fixture();
  try {
    f.codex.start = async (_root, _capsule, acknowledge) => {
      const started = {
        thread: { id: "acknowledged-native-thread" },
        model: "foreign-fixture-model",
        modelProvider: "openai",
        reasoningEffort: "high",
        instructionSources: [],
      };
      acknowledge(started, { model: "gpt-6.2-sol", effort: "ultra" });
      const [live] = f.app.store.list("job");
      assert.equal(live.thread_id, started.thread.id);
      assert.equal(live.native_model, started.model);
      assert.equal(live.native_model_provider, started.modelProvider);
      assert.equal(live.native_reasoning_effort, "high");
      assert.equal(live.requested_model, "gpt-6.2-sol");
      assert.equal(live.requested_reasoning_effort, "ultra");
      throw new ServiceError("MODEL_UNAVAILABLE", "Wrong model for this governed task", 409);
    };
    let turns = 0;
    f.codex.turn = async () => { turns++; throw new Error("Unexpected model request"); };
    const scope = { project_id: f.binding.id };
    const prepare = await f.command("task.prepare", { objective: "Read the accepted instructions", acceptance: "Return pinned evidence" }, scope);
    assert.equal(prepare.status, "completed");
    const dispatch = await f.command("task.dispatch", { task_id: prepare.result.task.id }, scope);
    assert.equal(dispatch.error.code, "MODEL_UNAVAILABLE");
    const [job] = f.app.store.list("job");
    assert.equal(job.status, "failed");
    assert.equal(job.thread_id, "acknowledged-native-thread");
    assert.equal(job.native_thread_acknowledged, true);
    assert.equal(job.host_dispatch_started, false);
    assert.equal(turns, 0);
  } finally {
    await f.close();
  }
});

test("misidentified resume ACK is quarantined without granting authority across restart", async () => {
  const f = await fixture();
  const scope = { project_id: f.binding.id };
  let restarted;
  const requested = "authorized-idle-native-chat";
  const reported = "different-idle-chat-in-the-same-project";
  const readback = [];
  const resumeCalls = [];
  let turns = 0;
  f.codex.readThread = async (threadId) => {
    readback.push(threadId);
    return { thread: { id: threadId, cwd: f.project, status: { type: "idle" } } };
  };
  f.codex.resume = async (threadId, _root, _capsule, acknowledge) => {
    resumeCalls.push(threadId);
    const result = {
      thread: { id: reported, sessionId: "observed-foreign-session" },
      model: "gpt-6.2-sol",
      modelProvider: "openai",
      reasoningEffort: "ultra",
    };
    acknowledge(result);
    return result;
  };
  f.codex.turn = async () => { turns++; throw new Error("Unexpected native turn"); };
  const prepare = async (command, thread) => {
    const preview = await command("thread.preview", { thread_id: thread }, scope);
    const adoption = await command("thread.adopt", {
      preview_id: preview.result.preview_id,
      confirmed_idle_handoff: true,
    }, scope);
    const task = await command("task.prepare", {
      objective: "Read the prepared native handoff",
      acceptance: "Preserve the exact chat identity",
      thread_binding_id: adoption.result.thread_binding.id,
    }, scope);
    assert.equal(task.status, "completed");
    return { task_id: task.result.task.id };
  };
  try {
    const task = await prepare(f.command, requested);
    const separatelyPrepared = [
      await prepare(f.command, requested),
      await prepare(f.command, reported),
    ];
    const first = await f.command("task.dispatch", task, scope);
    assert.equal(first.error.code, "SCOPE_MISMATCH");
    const [job] = f.app.store.list("job");
    assert.equal(job.thread_id, requested);
    assert.equal(job.native_thread_requested_id, requested);
    assert.equal(job.native_thread_acknowledged_id, reported);
    assert.equal(job.native_thread_acknowledged_session_id, "observed-foreign-session");
    assert.equal(job.native_model, "gpt-6.2-sol");
    assert.equal(job.native_reasoning_effort, "ultra");
    assert.equal(job.native_model_provider, "openai");
    assert.equal(job.native_thread_identity_conflict, true);
    assert.equal(job.status, "outcome_unknown");
    assert.equal(job.turn_id, null);
    assert.equal(job.host_dispatch_started, false);

    await f.app.close();
    restarted = new Application({ dataDir: join(f.root, "data"), repoRoot, codex: f.codex });
    const command = (operation, payload, extra) => restarted.execute({
      command_id: randomUUID(), operation, payload, ...extra,
    });
    const readsBeforeReconcile = readback.length;
    const reconciliation = await command("job.reconcile", { job_id: job.id }, scope);
    assert.equal(reconciliation.error.code, "OUTCOME_UNKNOWN");
    assert.equal(readback.length, readsBeforeReconcile);
    const continuation = await command("task.continue", task, scope);
    assert.equal(continuation.error.code, "OUTCOME_UNKNOWN");
    for (const alternate of separatelyPrepared) {
      const dispatch = await command("task.dispatch", alternate, scope);
      assert.equal(dispatch.error.code, "OUTCOME_UNKNOWN");
    }
    assert.equal(restarted.store.get("job", job.id).native_thread_acknowledged_id, reported);
    assert.deepEqual(resumeCalls, [requested]);
    assert.equal(turns, 0);
  } finally {
    if (restarted) {
      await restarted.close();
      await rm(f.root, { recursive: true, force: true });
    } else await f.close();
  }
});

test("pausing while a native ACK is pending preserves the chat and prevents the turn", async () => {
  const f = await fixture();
  try {
    let entered, release;
    const started = new Promise((resolve) => { entered = resolve; });
    const barrier = new Promise((resolve) => { release = resolve; });
    let turns = 0;
    f.codex.start = async (_root, _capsule, acknowledge) => {
      entered();
      await barrier;
      const reply = { thread: { id: "paused-native-chat" }, model: "gpt-6.2-sol", modelProvider: "openai", reasoningEffort: "ultra" };
      acknowledge(reply);
      return reply;
    };
    f.codex.turn = async () => { turns++; throw new Error("Unexpected native turn"); };
    const scope = { project_id: f.binding.id };
    const prepared = await f.command("task.prepare", {
      objective: "Read an authorized source",
      acceptance: "Pause before model dispatch",
    }, scope);
    const task = { task_id: prepared.result.task.id };
    const pending = f.command("task.dispatch", task, scope);
    await started;
    try {
      assert.equal((await f.command("task.pause", task, scope)).status, "completed");
    } finally {
      release();
    }
    assert.equal((await pending).error.code, "TASK_PAUSED");
    const [job] = f.app.store.list("job");
    assert.equal(job.status, "paused");
    assert.equal(job.thread_id, "paused-native-chat");
    assert.equal(job.host_dispatch_started, false);
    assert.equal(turns, 0);
  } finally {
    await f.close();
  }
});

test("unknown native start reserves the outcome and blocks unacknowledged replay", async () => {
  const f = await fixture();
  try {
    f.codex.start = async () => {
      f.codex.starts++;
      throw new ServiceError("HOST_TIMEOUT", "Native thread result unknown", 504, { operation: "thread/start", outcome: "unknown" });
    };
    const scope = { project_id: f.binding.id };
    const prepare = () => f.command("task.prepare", { objective: "Inspect native input", acceptance: "Report exact outcome" }, scope);
    const task = await prepare();
    const dispatch = await f.command("task.dispatch", { task_id: task.result.task.id }, scope);
    assert.equal(dispatch.error.code, "HOST_TIMEOUT");
    const [job] = f.app.store.list("job");
    assert.equal(job.status, "outcome_unknown");
    assert.equal(job.native_thread_operation, "thread/start");
    assert.equal(job.thread_id, null);
    assert.equal(job.host_dispatch_started, false);
    const continued = await f.command("task.continue", { task_id: task.result.task.id }, scope);
    assert.equal(continued.status, "failed");
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});

test("English interface and task defaults preserve original Ukrainian source and explicit preferences", async () => {
  const f = await fixture();
  try {
    assert.equal((await f.app.bootstrap("test")).locale, "en");
    await f.command("service.settings", { locale: "fr" });
    assert.equal((await f.app.bootstrap("test")).locale, "fr");
    const request = { objective: "Прочитай точну вимогу", acceptance: "Збережи MUST-1" };
    const scope = { project_id: f.binding.id };
    let prepare = await f.command("task.prepare", request, scope);
    assert.equal(prepare.result.capsule.output_locale, "en");
    assert.equal(prepare.result.capsule.objective, request.objective);
    const contextRef = "selected/project-context.json";
    const contextPath = join(f.project, contextRef);
    const context = JSON.stringify({ schema_version: "codex-agents.project-context/1", preferred_language: "uk" });
    await mkdir(join(f.project, "selected"));
    await writeFile(contextPath, context);
    const pinnedTask = { ...request, source_paths: [contextRef] };
    prepare = await f.command("task.prepare", pinnedTask, scope);
    assert.equal(prepare.result.capsule.output_locale, "uk");
    assert.ok(prepare.result.capsule.original_sources.some((pin) => pin.path === contextRef && pin.sha256 === sha(context)));
    const explicit = await f.command("task.prepare", { ...pinnedTask, output_locale: "de" }, scope);
    assert.equal(explicit.result.capsule.output_locale, "de");
    assert.equal(await readFile(contextPath, "utf8"), context);
    const malformed = '{"preferred_language":';
    await writeFile(contextPath, malformed);
    const optional = await f.command("task.prepare", pinnedTask, scope);
    assert.equal(optional.status, "completed");
    assert.equal(optional.result.capsule.output_locale, "en");
    assert.ok(optional.result.capsule.original_sources.some((pin) => pin.path === contextRef && pin.sha256 === sha(malformed)));
    await mkdir(join(f.project, ".atelier"));
    const declared = join(f.project, ".atelier", "context-bindings.json");
    await writeFile(declared, JSON.stringify({
      schema: "atelier.context-bindings/1",
      project_root: f.project,
      sources: [{ path: contextRef, sha256: sha(malformed), role: "project-context" }],
    }));
    const required = await f.command("task.prepare", pinnedTask, scope);
    assert.equal(required.error.code, "INVALID_JSON");
    assert.equal(await readFile(contextPath, "utf8"), malformed);
    await rm(declared);
    const path = join(f.project, ".appatelier", "profile.json");
    const profile = JSON.stringify({ schema_version: "app-atelier-profile/1", preferred_language: "uk", goal: "Збережи джерело" });
    await writeFile(path, profile);
    prepare = await f.command("task.prepare", request, scope);
    assert.equal(prepare.result.capsule.output_locale, "uk");
    assert.ok(prepare.result.capsule.original_sources.some((pin) => pin.path === ".appatelier/profile.json" && pin.sha256 === sha(profile)));
    assert.equal(prepare.result.capsule.acceptance, request.acceptance);
    const override = await f.command("task.prepare", { ...request, output_locale: "de" }, scope);
    assert.equal(override.result.capsule.output_locale, "de");
    assert.equal((await f.app.bootstrap("test")).locale, "fr");
    const invalid = await f.command("task.prepare", { ...request, output_locale: "uk-UA" }, scope);
    assert.equal(invalid.error.code, "INVALID_INPUT");
    assert.equal(await readFile(path, "utf8"), profile);
  } finally {
    await f.close();
  }
});

test("one current writer blocks competing write; observed turn completes then owner review stays separate", async () => {
  const f = await fixture();
  try {
    writeProductionChoice(f.project);
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
  let integrationReads = 0;
  const app = new Application({
    dataDir: join(root, "data"),
    repoRoot,
    codex: new FakeCodex(),
    integrations: {
      async run(input) {
        integrationReads++;
        assert.equal(input.operation, "openverse.images.search");
        return { status: "completed", count: 1 };
      },
    },
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
    const { csrf_token: browserProof } = await claim.json();
    const bootstrap = await (
      await fetch(running.origin + "/api/v1/bootstrap", { headers: { cookie, "X-Atelier-CSRF": browserProof } })
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
    const lookup = (headers) =>
      fetch(running.origin + "/api/v1/integrations/read", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify({
          operation: "openverse.images.search",
          arguments: { query: "garden" },
        }),
      });
    assert.equal((await lookup({ Origin: running.origin })).status, 401);
    assert.equal(
      (await lookup({ cookie, Origin: running.origin })).status,
      403,
    );
    assert.equal(
      (
        await lookup({
          cookie,
          Origin: "https://hostile.example",
          "X-Atelier-CSRF": bootstrap.csrf_token,
        })
      ).status,
      403,
    );
    assert.equal(integrationReads, 0);
    const beforeLookup = app.store.db
      .prepare("SELECT count(*) AS n FROM commands")
      .get().n;
    const publicLookup = await lookup({
      cookie,
      Origin: running.origin,
      "X-Atelier-CSRF": bootstrap.csrf_token,
    });
    assert.equal(publicLookup.status, 200);
    assert.deepEqual(await publicLookup.json(), {
      status: "completed",
      count: 1,
    });
    assert.equal(integrationReads, 1);
    assert.equal(
      app.store.db.prepare("SELECT count(*) AS n FROM commands").get().n,
      beforeLookup,
    );
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
      { headers: { cookie, "X-Atelier-CSRF": browserProof } },
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
test("HTTP image generation requires owner origin and CSRF and leaves no command receipt", async (t) => {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-image-http-"),
  );
  const prompt = { prompt: "A blue enamel icon for the project status board" };
  const result = {
    kind: "generated_image",
    operation: "codex.image.generate",
    status: "completed",
    artifact: { filename: "atelier-image.png", base64: "cG5n" },
  };
  const requests = [];
  const app = new Application({
    dataDir: join(root, "data"),
    repoRoot,
    codex: new FakeCodex(),
    imageGeneration: {
      async generate(input) {
        requests.push({ ...input });
        return result;
      },
      async close() {},
    },
  });
  let running;
  t.after(async () => {
    try {
      if (running) await running.close();
      else await app.close();
    } finally {
      await rm(root, { recursive: true, force: true });
    }
  });
  running = await createServer({ port: 0, application: app });
  const origin = running.origin;
  const claim = await fetch(origin + "/api/v1/session", {
    method: "POST",
    headers: { Origin: origin, "Content-Type": "application/json" },
    body: JSON.stringify({
      launch_token: launchToken(running.ownerSession.controlKey),
    }),
  });
  assert.equal(claim.status, 200);
  const cookie = claim.headers.get("set-cookie").split(";")[0];
  const { csrf_token: csrf } = await claim.json();
  const generate = (headers) =>
    fetch(origin + "/api/v1/integrations/generation", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: JSON.stringify(prompt),
    });
  assert.equal((await generate({ Origin: origin })).status, 401);
  assert.equal((await generate({ cookie, Origin: origin })).status, 403);
  assert.equal(
    (
      await generate({
        cookie,
        Origin: "https://hostile.example",
        "X-Atelier-CSRF": csrf,
      })
    ).status,
    403,
  );
  assert.deepEqual(requests, []);

  const commands = app.store.db.prepare("SELECT * FROM commands");
  const before = commands.all();
  const response = await generate({
    cookie,
    Origin: origin,
    "X-Atelier-CSRF": csrf,
  });
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("cache-control"), "no-store");
  assert.deepEqual(await response.json(), result);
  assert.deepEqual(requests, [prompt]);
  assert.deepEqual(commands.all(), before);
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
    f.codex.turn = async (_threadId, _capsule, onDispatch, verifyBeforeDispatch) => {
      await verifyBeforeDispatch?.();
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
    await f.command("service.settings", { locale: "uk" });
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

test("idle native metadata cannot grant continuation when the isolated executor lacks paginated history", async () => {
  const f = await fixture();
  try {
    f.codex.readThread = async (threadId) => ({
      thread: {
        id: threadId,
        cwd: f.project,
        status: { type: "idle" },
        historyMode: "paginated",
      },
    });
    f.codex.historyTurns = async () => ({ data: [] });
    const preview = await f.command(
      "thread.preview",
      { thread_id: "existing" },
      { project_id: f.binding.id },
    );
    assert.equal(preview.result.execution_context_available, false);
    const rejected = await f.command(
      "thread.adopt",
      { preview_id: preview.result.preview_id, confirmed_idle_handoff: true },
      { project_id: f.binding.id },
    );
    assert.equal(rejected.error.code, "CAPABILITY_UNVERIFIED");
    assert.equal(f.app.store.list("thread-binding").length, 0);
    f.codex.historyTurns = async () => ({ data: [{ id: "persisted-turn" }] });
    const available = await f.command(
      "thread.preview",
      { thread_id: "existing" },
      { project_id: f.binding.id },
    );
    assert.equal(available.result.execution_context_available, true);
    const adopted = await f.command(
      "thread.adopt",
      { preview_id: available.result.preview_id, confirmed_idle_handoff: true },
      { project_id: f.binding.id },
    );
    assert.equal(adopted.status, "completed");
  } finally {
    await f.close();
  }
});

test("atomic reservation survives concurrent dispatch awaits and consumes each task once", async () => {
  const f = await fixture();
  try {
    writeProductionChoice(f.project);
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
    let release, enteredResolve;
    const entered = new Promise((resolve) => {
      enteredResolve = resolve;
    });
    f.codex.connect = () =>
      new Promise((resolve) => {
        release = resolve;
        enteredResolve();
      });
    const first = f.command(
      "task.dispatch",
      { task_id: a.result.task.id },
      { project_id: f.binding.id },
    );
    await entered;
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
    writeProductionChoice(f.project);
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
    f.codex.turn = async (_thread, _capsule, onDispatch, verifyBeforeDispatch) => {
      await verifyBeforeDispatch?.();
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
    writeProductionChoice(f.project);
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
      const roots = { parent: f.project, child: childRoot };
      const writers = new Set();
      if (scenario.first_scope === "workspace-write") writers.add(scenario.first);
      if (scenario.second_scope === "workspace-write") writers.add(scenario.second);
      for (const project of writers) writeProductionChoice(roots[project]);
      f.codex.start = async () => {
        f.codex.starts++;
        return { thread: { id: "overlap-thread-" + f.codex.starts } };
      };
      f.codex.turn = async (threadId, _capsule, onDispatch, verifyBeforeDispatch) => {
        await verifyBeforeDispatch?.();
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
    writeProductionChoice(f.project);
    writeProductionChoice(sibling);
    f.codex.start = async () => {
      writeProductionChoice(f.project);
    writeProductionChoice(sibling);
    f.codex.starts++;
      return { thread: { id: "disjoint-thread-" + f.codex.starts } };
    };
    f.codex.turn = async (threadId, _capsule, onDispatch, verifyBeforeDispatch) => {
      await verifyBeforeDispatch?.();
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
    f.codex.turn = async (threadId, _capsule, onDispatch, verifyBeforeDispatch) => {
      await verifyBeforeDispatch?.();
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

test("legacy or changed governing instruction context never reaches a model turn", async () => {
  const f = await fixture();
  let turns = 0;
  try {
    const prepared = await f.command(
      "task.prepare",
      {
        objective: "Inspect fixture",
        acceptance: "Preserve content",
        scope: "read-only",
        deadline_seconds: 60,
      },
      { project_id: f.binding.id },
    );
    const task = prepared.result.task;
    const old = { ...task, capsule: { ...task.capsule } };
    delete old.capsule.instruction_manifest;
    f.app.store.put("task", task.id, old);
    let connects = 0;
    const connect = f.codex.connect.bind(f.codex);
    f.codex.connect = () => {
      connects++;
      return connect();
    };
    const legacy = await f.command(
      "task.dispatch",
      { task_id: task.id },
      { project_id: f.binding.id },
    );
    assert.equal(legacy.error.code, "TASK_NOT_READY");
    assert.equal(connects, 0);
    f.app.store.put("task", task.id, task);
    const start = f.codex.start.bind(f.codex);
    f.codex.start = async () => {
      const result = await start();
      await writeFile(
        join(f.project, "AGENTS.override.md"),
        "New governing precedence after bootstrap",
      );
      return result;
    };
    f.codex.turn = async () => {
      turns++;
      throw new Error("Unexpected turn");
    };
    const drift = await f.command(
      "task.dispatch",
      { task_id: task.id },
      { project_id: f.binding.id },
    );
    assert.equal(drift.error.code, "SOURCE_DRIFT");
    assert.equal(turns, 0);
    assert.equal(f.codex.starts, 1);
  } finally {
    await f.close();
  }
});
