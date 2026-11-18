import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  cp,
  readFile,
  writeFile,
  rm,
  rename,
  symlink,
  chmod,
} from "node:fs/promises";
import { realpathSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync, spawn } from "node:child_process";
import { NativeControllers } from "../../server/controllers.mjs";
import { sha } from "../../server/utils.mjs";

const repoRoot = resolve(import.meta.dirname, "../../../..");
async function fixture(t, options = {}) {
  const home = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-native-controller-"),
  );
  const root = join(home, "project [literal]"),
    dataDir = join(home, "private"),
    foundryRoot = join(home, "foundry");
  await mkdir(root);
  await mkdir(dataDir);
  await cp(join(repoRoot, "kit/skills/agent-foundry"), foundryRoot, {
    recursive: true,
  });
  const records = new Map([
    ["settings:owner", { authority_epoch: "owner-epoch" }],
  ]);
  const store = {
    get: (kind, id) => records.get(`${kind}:${id}`),
    put: (kind, id, value) => {
      records.set(`${kind}:${id}`, structuredClone(value));
      return value;
    },
    list: (kind) =>
      [...records].filter(([k]) => k.startsWith(kind + ":")).map(([, v]) => v),
  };
  const projects = { get: (id) => ({ id, root }) };
  const manager = new NativeControllers({
    store,
    repoRoot,
    dataDir,
    projects,
    foundryRoot,
    ...options,
  });
  t.after(() => rm(home, { recursive: true, force: true }));
  return { home, root, dataDir, foundryRoot, store, projects, manager };
}
async function initialize(f) {
  const preview = await f.manager.preview("project", {
    operation: "init",
    session_path: "factory",
    params: { project_id: "synthetic-agent", purpose: "factory" },
  });
  return f.manager.apply("project", {
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
}
const exact = (preview) => ({
  preview_id: preview.preview_id,
  sha256: preview.sha256,
  confirmed: true,
});

test("source-bound native initialization and context run through original controller, retaining actual state and backup", async (t) => {
  const f = await fixture(t);
  const created = await initialize(f);
  assert.equal(created.status, "completed");
  assert.equal(created.result.initialized, true);
  assert.equal(created.executes_model_or_external_effect, false);
  const statePath = join(f.root, "factory/.agent-foundry/state.json"),
    before = await readFile(statePath);
  const preview = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  assert.equal(preview.child_filesystem_permission_expansion, false);
  const result = await f.manager.apply("project", exact(preview));
  assert.equal(result.status, "completed");
  assert.equal(result.result.project_id, "synthetic-agent");
  assert.deepEqual(
    await readFile(
      join(f.dataDir, "controller-backups", result.backup_id, "state.json"),
    ),
    before,
  );
  assert.deepEqual(await readFile(statePath), before);
  await assert.rejects(
    f.manager.apply("project", exact(preview)),
    (error) => error.code === "PREVIEW_REQUIRED",
  );
  await assert.rejects(
    initialize(f),
    (error) => error.code === "NATIVE_STATE_CONFLICT",
  );
});

test("native operations require exact owner preview and refuse other project, expired epoch or state changes", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const p = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  await assert.rejects(
    f.manager.apply("other", exact(p)),
    (error) => error.code === "PREVIEW_REQUIRED",
  );
  await assert.rejects(
    f.manager.apply("project", { ...exact(p), confirmed: false }),
    (error) => error.code === "PREVIEW_REQUIRED",
  );
  f.store.put("settings", "owner", { authority_epoch: "new-owner-epoch" });
  await assert.rejects(
    f.manager.apply("project", exact(p)),
    (error) => error.code === "SOURCE_DRIFT",
  );
  const fresh = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  const state = join(f.root, "factory/.agent-foundry/state.json");
  await writeFile(state, (await readFile(state, "utf8")) + "\n");
  await assert.rejects(
    f.manager.apply("project", exact(fresh)),
    (error) => error.code === "REVISION_CONFLICT",
  );
});

test("compare-and-set admission occurs inside the actual exclusive native lock, including a last-moment external change", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const p = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  const nativeRun = f.manager.run;
  const statePath = join(f.root, "factory/.agent-foundry/state.json");
  const stateBefore = JSON.parse(await readFile(statePath, "utf8"));
  f.manager.run = async (...args) => {
    await writeFile(statePath, (await readFile(statePath, "utf8")) + "\n");
    return nativeRun(...args);
  };
  const result = await f.manager.apply("project", exact(p));
  assert.equal(result.status, "rejected");
  assert.match(
    result.result.error,
    /Native state changed since the reviewed preview/,
  );
  assert.deepEqual(JSON.parse(await readFile(statePath, "utf8")), stateBefore);
});

test("trusted-source and record drift are rejected before native mutation", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  await writeFile(
    join(f.root, "factory/record.json"),
    JSON.stringify({
      id: "lesson-one",
      source: "Synthetic owner fixture",
      verbatim: "Keep the tested result",
      summary: "Synthetic lesson",
    }),
  );
  const p = await f.manager.preview("project", {
    operation: "lesson",
    session_path: "factory",
    record_path: "record.json",
  });
  await writeFile(join(f.root, "factory/record.json"), "{}");
  await assert.rejects(
    f.manager.apply("project", exact(p)),
    (error) => error.code === "SOURCE_DRIFT",
  );
  const context = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  await writeFile(
    join(f.foundryRoot, "SKILL.md"),
    (await readFile(join(f.foundryRoot, "SKILL.md"), "utf8")) +
      "\nChanged controller source.",
  );
  await assert.rejects(
    f.manager.apply("project", exact(context)),
    (error) => error.code === "SOURCE_DRIFT",
  );
});

test("staged platform adapter tampering is rejected before the native state is created", async (t) => {
  const f = await fixture(t), nativeRun = f.manager.run;
  f.manager.run = async (python, args, ...rest) => {
    const directory = args[args.indexOf("--operation-dir") + 1];
    const helper = join(directory, "platform_support.py");
    await chmod(helper, 0o600);
    await writeFile(helper, (await readFile(helper, "utf8")) + "\n# changed after staging\n");
    return nativeRun(python, args, ...rest);
  };
  const result = await initialize(f);
  assert.equal(result.status, "rejected");
  assert.match(result.result.error, /Reviewed platform adapter changed/);
  await assert.rejects(readFile(join(f.root, "factory/.agent-foundry/state.json")), { code: "ENOENT" });
});

test("controller paths, private nested references, parameters and operation catalog cannot escape the bound project", async (t) => {
  const f = await fixture(t);
  for (const session_path of [
    "../elsewhere",
    "/private/tmp",
    ".ssh",
    ".env",
    "missing/.aws",
  ])
    await assert.rejects(
      f.manager.preview("project", {
        operation: "init",
        session_path,
        params: { project_id: "safe" },
      }),
    );
  await assert.rejects(
    f.manager.preview("project", { operation: "arbitrary-shell", params: {} }),
    (error) => error.code === "UNSUPPORTED_OPERATION",
  );
  await assert.rejects(
    f.manager.preview("project", {
      operation: "init",
      params: { project_id: "safe", command: "echo unsafe" },
    }),
    (error) => error.code === "INVALID_INPUT",
  );
  await initialize(f);
  await writeFile(
    join(f.root, "factory/record.json"),
    JSON.stringify({ id: "unsafe", path: "missing/.env" }),
  );
  await assert.rejects(
    f.manager.preview("project", {
      operation: "artifact",
      session_path: "factory",
      record_path: "record.json",
    }),
    (error) => error.code === "PRIVATE_PATH",
  );
  await assert.rejects(
    f.manager.preview("project", {
      operation: "context",
      session_path: "factory",
      params: [],
    }),
    (error) => error.code === "INVALID_INPUT",
  );
});

test("unknown native outcome blocks replay until exact current-state reconciliation, including restart recovery", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const p = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  f.manager.run = async () => ({
    error: { killed: true, signal: "SIGTERM" },
    stdout: "",
    stderr: "",
  });
  const unknown = await f.manager.apply("project", exact(p));
  assert.equal(unknown.status, "outcome_unknown");
  const another = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  await assert.rejects(
    f.manager.apply("project", exact(another)),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  const view = await f.manager.reconcile("project", { receipt_id: unknown.id });
  await assert.rejects(
    f.manager.reconcile("project", {
      receipt_id: unknown.id,
      sha256: "stale",
      confirmed: true,
    }),
    (error) => error.code === "REVISION_CONFLICT",
  );
  const result = await f.manager.reconcile("project", {
    receipt_id: unknown.id,
    sha256: view.sha256,
    confirmed: true,
  });
  assert.equal(result.status, "reconciled_unclassified");
  assert.equal(result.automatic_replay, false);
  f.store.put("native-controller", "interrupted", {
    id: "interrupted",
    root: f.root,
    status: "pending",
  });
  new NativeControllers({
    store: f.store,
    projects: f.projects,
    repoRoot,
    dataDir: f.dataDir,
    foundryRoot: f.foundryRoot,
  });
  assert.equal(
    f.store.get("native-controller", "interrupted").status,
    "outcome_unknown",
  );
});

test("native approval cannot be fabricated without a real registered blueprint and reviewed owner text", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const before = sha(
    await readFile(join(f.root, "factory/.agent-foundry/state.json")),
  );
  await assert.rejects(
    f.manager.preview("project", {
      operation: "approve",
      session_path: "factory",
      owner_approval_text: "Approve this exact candidate",
    }),
    (error) => error.code === "NATIVE_STATE_CONFLICT",
  );
  assert.equal(
    sha(await readFile(join(f.root, "factory/.agent-foundry/state.json"))),
    before,
  );
});

test("panel-only owner approval derives exact native subject and opens only the construction gate", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const fixtureSource = join(
    repoRoot,
    "kit/skills/agent-foundry/scripts/tests/test_foundry.py",
  );
  const blueprint = execFileSync(
    "python3",
    [
      "-B",
      "-c",
      "import runpy,sys,json; m=runpy.run_path(sys.argv[1]); print(json.dumps(m['blueprint']()))",
      fixtureSource,
    ],
    { encoding: "utf8" },
  );
  await writeFile(join(f.root, "factory/blueprint.json"), blueprint);
  const plan = await f.manager.preview("project", {
    operation: "blueprint",
    session_path: "factory",
    record_path: "blueprint.json",
  });
  const registered = await f.manager.apply("project", exact(plan));
  assert.equal(registered.status, "completed");
  assert.equal(registered.result.ready_for_approval, true);
  const owner = await f.manager.preview("project", {
    operation: "approve",
    session_path: "factory",
    owner_approval_text:
      "Synthetic owner approves exactly the displayed candidate construction scope.",
  });
  assert.equal(owner.subject.revision, 1);
  assert.equal(owner.subject.scope, "fixture-construction");
  assert.equal(owner.params.sha256, owner.subject.sha256);
  assert.equal(owner.record.actor, "user");
  const approved = await f.manager.apply("project", exact(owner));
  assert.equal(approved.status, "completed");
  assert.equal(approved.result.approval_ref.status, "confirmed");
  const gate = await f.manager.preview("project", {
    operation: "build-gate",
    session_path: "factory",
  });
  const result = await f.manager.apply("project", exact(gate));
  assert.equal(result.status, "completed");
  assert.equal(result.result.ready, true);
  const native = JSON.parse(
    await readFile(join(f.root, "factory/.agent-foundry/state.json"), "utf8"),
  );
  assert.deepEqual(native.executions, {});
  assert.deepEqual(native.grants, {});
});

test("a replaced bound root cannot disclose or mutate an outside native session during preview/apply/reconcile", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  const p = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  const saved = join(f.home, "original-project");
  await rename(f.root, saved);
  const outside = join(f.home, "outside");
  await mkdir(outside);
  await mkdir(join(outside, ".agent-foundry"));
  const canary = JSON.stringify({
    revision: 999,
    blueprint: { data: { goal: "outside private canary" } },
  });
  await writeFile(join(outside, ".agent-foundry/state.json"), canary);
  await symlink(outside, f.root);
  await assert.rejects(
    f.manager.preview("project", { operation: "context" }),
    (e) => e.code === "SOURCE_DRIFT",
  );
  await assert.rejects(
    f.manager.apply("project", exact(p)),
    (e) => e.code === "SOURCE_DRIFT",
  );
  f.store.put("native-controller", "lost", {
    id: "lost",
    root: f.root,
    project_id: "project",
    session_path: ".",
    status: "outcome_unknown",
  });
  await assert.rejects(
    f.manager.reconcile("project", { receipt_id: "lost" }),
    (e) => e.code === "SOURCE_DRIFT",
  );
  assert.equal(
    await readFile(join(outside, ".agent-foundry/state.json"), "utf8"),
    canary,
  );
});

test("late normative source changes cannot alter the reviewed native closure", async (t) => {
  const f = await fixture(t),
    nativeRun = f.manager.run;
  const ref = "references/adaptive-work.md",
    expected = sha(await readFile(join(f.foundryRoot, ref)));
  f.manager.run = async (...args) => {
    await writeFile(join(f.foundryRoot, ref), "Changed after Node admission");
    return nativeRun(...args);
  };
  const result = await initialize(f);
  assert.equal(result.status, "completed");
  const state = JSON.parse(
    await readFile(join(f.root, "factory/.agent-foundry/state.json"), "utf8"),
  );
  assert.equal(state.suite[ref], expected);
  assert.notEqual(sha(await readFile(join(f.foundryRoot, ref))), expected);
  const p = await f.manager.preview("project", {
    operation: "context",
    session_path: "factory",
  });
  f.manager.run = async (...args) => {
    const script = args[1][args[1].indexOf("--script") + 1];
    await chmod(join(script, "../../references/adaptive-work.md"), 0o600);
    await writeFile(
      join(script, "../../references/adaptive-work.md"),
      "Changed staged normative source",
    );
    return nativeRun(...args);
  };
  const rejected = await f.manager.apply("project", exact(p));
  assert.equal(rejected.status, "rejected");
  assert.match(rejected.result.error, /closure changed/);
});

test("failed controller staging stays journal-owned and never mutates the native project", async (t) => {
  const f = await fixture(t);
  await writeFile(
    join(f.dataDir, "controller-backups"),
    "Parent deliberately unavailable",
  );
  await assert.rejects(initialize(f));
  const rows = f.store.list("native-controller");
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, "rejected");
  assert.equal(rows[0].phase, "staging_failed");
  assert.ok(rows[0].completed_at);
  assert.equal(rows[0].backup_id, rows[0].id);
  await assert.rejects(
    readFile(join(f.root, "factory/.agent-foundry/state.json")),
    { code: "ENOENT" },
  );
});

test("restart during staging can reconcile without an adapter that was never staged", async (t) => {
  const f = await fixture(t);
  f.store.put("native-controller", "staging-crash", {
    id: "staging-crash",
    project_id: "project",
    root: f.root,
    session_path: "factory",
    operation: "init",
    operation_guard: 1,
    phase: "staging",
    status: "pending",
    backup_id: "staging-crash",
  });
  const resumed = new NativeControllers({
    store: f.store,
    projects: f.projects,
    repoRoot,
    dataDir: f.dataDir,
    foundryRoot: f.foundryRoot,
  });
  const view = await resumed.reconcile("project", {
    receipt_id: "staging-crash",
  });
  assert.equal(view.current_sha256, "missing");
  const resolved = await resumed.reconcile("project", {
    receipt_id: "staging-crash",
    sha256: view.sha256,
    confirmed: true,
  });
  assert.equal(resolved.status, "reconciled_unclassified");
  assert.equal(resolved.automatic_replay, false);
});

test("reconciliation cannot clear a live native writer and revokes a not-yet-started invocation", async (t) => {
  const f = await fixture(t);
  await initialize(f);
  await writeFile(
    join(f.root, "factory/pause.json"),
    JSON.stringify({ reason: "Synthetic pause", boundary: "now" }),
  );
  const p = await f.manager.preview("project", {
    operation: "pause",
    session_path: "factory",
    record_path: "pause.json",
  });
  const nativeRun = f.manager.run;
  let invocation;
  f.manager.run = async (...args) => {
    invocation = args;
    return {
      error: { killed: true, signal: "SIGTERM" },
      stdout: "",
      stderr: "",
    };
  };
  const unknown = await f.manager.apply("project", exact(p));
  assert.equal(unknown.status, "outcome_unknown");
  const lock = join(
    f.dataDir,
    "controller-backups",
    unknown.id,
    "operation.lock",
  );
  const child = spawn("python3", [
    "-B",
    "-c",
    "import fcntl,sys,time; f=open(sys.argv[1],'r+'); fcntl.flock(f,fcntl.LOCK_EX); print('ready',flush=True); time.sleep(30)",
    lock,
  ]);
  t.after(() => child.kill("SIGKILL"));
  await new Promise((resolve, reject) => {
    child.stdout.once("data", resolve);
    child.once("error", reject);
  });
  await assert.rejects(
    f.manager.reconcile("project", { receipt_id: unknown.id }),
    (e) => e.code === "WRITER_CONFLICT",
  );
  assert.equal(
    f.store.get("native-controller", unknown.id).status,
    "outcome_unknown",
  );
  const exited = new Promise((resolve) => child.once("exit", resolve));
  child.kill("SIGKILL");
  await exited;
  const view = await f.manager.reconcile("project", { receipt_id: unknown.id });
  await f.manager.reconcile("project", {
    receipt_id: unknown.id,
    sha256: view.sha256,
    confirmed: true,
  });
  const late = await nativeRun(...invocation);
  assert.ok(late.error);
  assert.match(late.stderr, /revoked/);
  const state = JSON.parse(
    await readFile(join(f.root, "factory/.agent-foundry/state.json"), "utf8"),
  );
  assert.equal(state.pause.active, false);
});
