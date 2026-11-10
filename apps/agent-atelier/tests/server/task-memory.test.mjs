import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, symlink, writeFile } from "node:fs/promises";
import { realpathSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { compileContext } from "../../server/context.mjs";
import { CodexAdapter } from "../../server/codex.mjs";
import {
  codexMemoryDenyRoots,
  taskMemoryMode,
} from "../../server/permissions.mjs";
import { digest, ServiceError } from "../../server/utils.mjs";

const request = (payload = {}) => ({
  project: { id: "synthetic-project", root: "/synthetic/project" },
  workspace: {
    project: { revision: 1 },
    requirements: [],
    sources: [],
    decisions: [],
    warnings: [],
  },
  payload: {
    objective: "Read the declared source packet",
    acceptance: "Preserve the declared task scope",
    ...payload,
  },
  taskId: "synthetic-task",
  authorityEpoch: 1,
  instructionManifest: {},
});

async function fixture(t) {
  const directory = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-task-memory-"),
  );
  const home = join(directory, "native-home");
  const root = join(directory, "project");
  const dataDir = join(directory, "service-data");
  const snapshot = join(dataDir, "task-inputs/task/skills/selected");
  const alias = join(dataDir, "instruction-aliases/task/source.md");
  await mkdir(join(home, "memories"), { recursive: true });
  await mkdir(root);
  await mkdir(snapshot, { recursive: true });
  t.after(async () => {
    await rm(directory, { recursive: true, force: true });
  });
  const executable = join(directory, "fake-codex");
  await writeFile(executable, "#!/bin/sh\nprintf '[]\\n'\n", { mode: 0o700 });
  const adapter = new CodexAdapter({
    dataDir,
    executable,
    memoryRootResolver: () => codexMemoryDenyRoots(home),
    instructions: {
      aliases: async () => [{ path: alias }],
      verify: async () => {},
      verifyLoaded: () => {},
    },
  });
  adapter.runtimeReadRoots = [executable];
  adapter.status.auth_mode = "chatgpt";
  adapter.connect = async () => {};
  adapter.instructionSettings = async () => ({});
  const capsule = {
    task_id: "synthetic-task",
    root,
    scope: "read-only",
    allowed_paths: [],
    capability_scope: {},
    selected_skills: [
      {
        name: "selected",
        snapshot_root: snapshot,
        path: join(snapshot, "SKILL.md"),
        source_locator: "/provenance-only/selected",
      },
    ],
    instruction_manifest: {
      settings: {
        native_route: { provider: "openai" },
        project_doc_fallback_filenames: [],
      },
    },
  };
  const calls = [];
  const reply = (method, params) => {
    if (method === "thread/start" || method === "thread/resume")
      return {
        thread: { id: params.threadId ?? "owned-thread" },
        modelProvider: "openai",
        instructionSources: [],
      };
    if (method === "thread/memoryMode/set") return {};
    return { turn: { id: "fake-turn" } };
  };
  adapter.rpc = async (method, params) => {
    calls.push({ method, params });
    return reply(method, params);
  };
  return {
    directory,
    home,
    root,
    dataDir,
    snapshot,
    alias,
    adapter,
    capsule,
    calls,
    reply,
  };
}

test("memory mode is typed, inherited by default and bound into the new capsule hash", async () => {
  assert.equal(taskMemoryMode(undefined), "inherit");
  const inherited = await compileContext(request());
  const disabled = await compileContext(request({ memory_mode: "disabled" }));
  assert.equal(inherited.memory_mode, "inherit");
  assert.equal(disabled.memory_mode, "disabled");
  const { capsule_sha256, ...unsigned } = disabled;
  assert.equal(capsule_sha256, digest(unsigned));
  assert.notEqual(
    capsule_sha256,
    digest({ ...unsigned, memory_mode: "inherit" }),
  );
  for (const value of [null, false, 1, [], {}, "", "enabled", "false"])
    await assert.rejects(compileContext(request({ memory_mode: value })), {
      code: "INVALID_INPUT",
    });
  await assert.rejects(
    compileContext(
      request({ memory_mode: "disabled", thread_binding_id: "native-binding" }),
    ),
    { code: "CAPABILITY_UNVERIFIED" },
  );
});

test("disabled task configuration adds only typed memory overrides and exact denies, preserving existing reads and guards", async (t) => {
  const f = await fixture(t);
  const before = await f.adapter.taskConfiguration(f.root, f.capsule);
  const after = await f.adapter.taskConfiguration(f.root, {
    ...f.capsule,
    memory_mode: "disabled",
  });
  assert.equal(Object.hasOwn(before.config, "memories.use_memories"), false);
  assert.equal(
    Object.hasOwn(before.config, "memories.generate_memories"),
    false,
  );
  assert.equal(after.config["memories.use_memories"], false);
  assert.equal(after.config["memories.generate_memories"], false);
  const oldFS = before.config["permissions.atelier-task"].filesystem;
  const newFS = after.config["permissions.atelier-task"].filesystem;
  assert.deepEqual(after.memoryDenyRoots, [
    join(f.home, "memories"),
    join(f.home, "memories_v2"),
  ]);
  for (const path of after.memoryDenyRoots) assert.equal(newFS[path], "deny");
  for (const [path, rule] of Object.entries(oldFS))
    assert.deepEqual(newFS[path], rule, path);
  assert.equal(newFS[f.snapshot], "read");
  assert.equal(newFS[f.alias], "read");
  assert.equal(newFS[f.dataDir], "deny");
  assert.equal(newFS[":root"], "deny");
  assert.equal(newFS["/**/auth.json"], "deny");
  assert.equal(newFS[":workspace_roots"][".agents"], "read");
  assert.equal(newFS[":workspace_roots"][".aws"], "deny");
  assert.equal(newFS[f.home], undefined);
  assert.equal(newFS["/provenance-only/selected"], undefined);
});

test("memory path guard covers actual linked stores and rejects missing, dangling or unrepresentable homes", async (t) => {
  const f = await fixture(t);
  const actual = join(f.directory, "actual-memory");
  await mkdir(actual);
  await symlink(actual, join(f.home, "memories_v2"));
  assert.ok((await codexMemoryDenyRoots(f.home)).includes(actual));
  for (const home of [
    "relative/home",
    join(f.directory, "odd[home]"),
    join(f.directory, "absent"),
  ])
    await assert.rejects(codexMemoryDenyRoots(home), {
      code: "CAPABILITY_UNVERIFIED",
    });
  await rm(join(f.home, "memories_v2"));
  await symlink(join(f.directory, "not-created"), join(f.home, "memories_v2"));
  await assert.rejects(codexMemoryDenyRoots(f.home), {
    code: "CAPABILITY_UNVERIFIED",
  });
});

test("a source input inside a native memory store cannot override the task-only deny", async (t) => {
  const f = await fixture(t);
  await assert.rejects(
    f.adapter.taskConfiguration(join(f.home, "memories"), {
      ...f.capsule,
      memory_mode: "disabled",
    }),
    { code: "CAPABILITY_UNVERIFIED" },
  );
  await assert.rejects(
    f.adapter.taskConfiguration(f.root, {
      ...f.capsule,
      memory_mode: "disabled",
      selected_skills: [{ snapshot_root: join(f.home, "memories/selected") }],
    }),
    { code: "CAPABILITY_UNVERIFIED" },
  );
});

test("owned disabled start/resume confirms native setter before turn without inventing readback", async (t) => {
  const f = await fixture(t);
  const capsule = { ...f.capsule, memory_mode: "disabled" };
  const started = await f.adapter.start(f.root, capsule);
  assert.deepEqual(
    f.calls.map((x) => x.method),
    ["thread/start", "thread/memoryMode/set"],
  );
  assert.equal(f.calls[0].params.config["memories.use_memories"], false);
  assert.deepEqual(f.calls[1].params, {
    threadId: "owned-thread",
    mode: "disabled",
  });
  assert.equal(started.memory_control.acknowledged, true);
  assert.equal(started.memory_control.injection_efficacy_verified, false);
  assert.match(started.memory_control.mode_readback, /not_exposed/);
  let dispatched = 0;
  await f.adapter.turn("owned-thread", capsule, () => dispatched++);
  assert.equal(dispatched, 1);
  const prompt = f.calls.at(-1).params.input.at(-1).text;
  assert.match(prompt, /aliases.*transport, not a prerequisite/);
  assert.match(
    prompt,
    /source_locator is provenance, not an extra access grant/,
  );
  assert.match(prompt, /Honor any actual read failure/);
  assert.match(
    prompt,
    /not an assertion that every readable project file is allowlisted/,
  );
  f.calls.length = 0;
  await f.adapter.resume("owned-thread", f.root, capsule);
  await f.adapter.turn("owned-thread", capsule);
  assert.deepEqual(
    f.calls.map((x) => x.method),
    ["thread/resume", "thread/memoryMode/set", "turn/start"],
  );
});

test("legacy and explicit inherit tasks preserve native memory settings and adopted-chat route", async (t) => {
  const f = await fixture(t);
  const started = await f.adapter.start(f.root, f.capsule);
  assert.equal(started.memory_control, undefined);
  assert.equal(
    f.calls.some((x) => x.method === "thread/memoryMode/set"),
    false,
  );
  assert.equal(
    Object.hasOwn(f.calls[0].params.config, "memories.use_memories"),
    false,
  );
  await f.adapter.resume("adopted-thread", f.root, {
    ...f.capsule,
    memory_mode: "inherit",
    existing_thread: { thread_id: "adopted-thread" },
  });
  assert.equal(
    f.calls.some((x) => x.method === "thread/memoryMode/set"),
    false,
  );
});

test("disabled adopted chats and invalid modes are rejected before any native connection or setting effect", async (t) => {
  const f = await fixture(t);
  let connections = 0;
  f.adapter.connect = async () => connections++;
  for (const operation of ["start", "resume"]) {
    const invoke = (capsule) =>
      operation === "start"
        ? f.adapter.start(f.root, capsule)
        : f.adapter.resume("native-chat", f.root, capsule);
    await assert.rejects(invoke({ ...f.capsule, memory_mode: "invalid" }), {
      code: "INVALID_INPUT",
    });
    await assert.rejects(
      invoke({
        ...f.capsule,
        memory_mode: "disabled",
        existing_thread: { thread_id: "native-chat" },
      }),
      { code: "CAPABILITY_UNVERIFIED" },
    );
  }
  assert.equal(connections, 0);
  assert.deepEqual(f.calls, []);
});

test("unsupported, unknown and malformed setter outcomes leave no dispatchable receipt and retain known chat identity", async (t) => {
  const f = await fixture(t);
  const capsule = { ...f.capsule, memory_mode: "disabled" };
  for (const failure of [
    new ServiceError("CODEX_RPC_ERROR", "method unsupported", 409, {
      rpc_code: -32601,
    }),
    new ServiceError("HOST_TIMEOUT", "outcome unknown", 504),
    null,
  ]) {
    f.calls.length = 0;
    f.adapter.rpc = async (method, params) => {
      f.calls.push({ method, params });
      if (method === "thread/memoryMode/set") {
        if (failure) throw failure;
        return null;
      }
      return f.reply(method, params);
    };
    await assert.rejects(f.adapter.start(f.root, capsule), (error) => {
      assert.equal(error.code, "CAPABILITY_UNVERIFIED");
      assert.equal(error.details.thread_id, "owned-thread");
      assert.equal(
        error.details.outcome,
        failure?.code === "CODEX_RPC_ERROR" ? "rejected" : "unknown",
      );
      return true;
    });
    await assert.rejects(f.adapter.turn("owned-thread", capsule), {
      code: "CAPABILITY_UNVERIFIED",
    });
    assert.equal(
      f.calls.some((x) => x.method === "turn/start"),
      false,
    );
  }
});

test("failed resume invalidates an earlier acknowledgement instead of allowing a stale turn", async (t) => {
  const f = await fixture(t);
  const capsule = { ...f.capsule, memory_mode: "disabled" };
  await f.adapter.start(f.root, capsule);
  f.adapter.rpc = async () => {
    throw new ServiceError("HOST_DISCONNECTED", "offline", 503);
  };
  await assert.rejects(f.adapter.resume("owned-thread", f.root, capsule), {
    code: "HOST_DISCONNECTED",
  });
  await assert.rejects(f.adapter.turn("owned-thread", capsule), {
    code: "CAPABILITY_UNVERIFIED",
  });
});

test("changed memory-store alias blocks the next turn without widening or mutating the store", async (t) => {
  const f = await fixture(t);
  const capsule = { ...f.capsule, memory_mode: "disabled" };
  await f.adapter.start(f.root, capsule);
  const moved = join(f.directory, "new-memory-target");
  await mkdir(moved);
  await symlink(moved, join(f.home, "memories_v2"));
  f.calls.length = 0;
  await assert.rejects(f.adapter.turn("owned-thread", capsule), {
    code: "SOURCE_DRIFT",
  });
  assert.deepEqual(f.calls, []);
});
