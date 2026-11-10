import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  writeFile,
  readFile,
  readdir,
  chmod,
  rm,
  symlink,
  rename,
  lstat,
} from "node:fs/promises";
import { realpathSync } from "node:fs";
import { join, dirname } from "node:path";
import { tmpdir } from "node:os";
import { EventEmitter } from "node:events";
import {
  SkillsManager,
  executionInputPaths,
  executionInputLocation,
  verifyExecutionInputTask,
} from "../../server/skills.mjs";
import { RetentionManager } from "../../server/retention.mjs";
import { Store } from "../../server/store.mjs";
import { Application } from "../../server/application.mjs";
import { localProfile } from "../../server/permissions.mjs";
import { sha } from "../../server/utils.mjs";

const taskId = "task_transport";
const OLD = "2025-01-01T00:00:00.000Z";
async function fixture(t) {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-execution-input-"),
  );
  t.after(() => rm(root, { recursive: true, force: true }));
  const repoRoot = join(root, "repository"),
    dataDir = join(root, "service-data");
  const source = join(repoRoot, "kit/skills/selected");
  await mkdir(join(source, "references"), { recursive: true });
  await mkdir(join(source, ".git"));
  await mkdir(dataDir);
  await writeFile(
    join(source, "SKILL.md"),
    "# Approved selected skill\nRead references/method.md.\n",
  );
  await writeFile(
    join(source, "references/method.md"),
    "APPROVED_PAYLOAD_ONLY\n",
  );
  await writeFile(
    join(source, ".git/control.txt"),
    "UNAPPROVED_SOURCE_CONTROL\n",
  );
  await writeFile(
    join(dataDir, "owner-credentials.json"),
    "PRIVATE_SERVICE_CONTROL\n",
  );
  const manager = new SkillsManager({ repoRoot, dataDir });
  const select = () => manager.selections(["selected"], taskId);
  return { root, repoRoot, source, dataDir, manager, select };
}

test("selected execution inputs are exact immutable copies outside control state with narrow read identity", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  const paths = executionInputPaths(f.dataDir, taskId);
  assert.equal(dirname(paths.namespace), dirname(f.dataDir));
  assert.match(paths.namespace, /AgentAtelierExecutionInputs-[a-f0-9]{24}$/);
  assert.ok(!selected.snapshot_root.startsWith(f.dataDir + "/"));
  assert.equal(
    selected.archive_root,
    join(f.dataDir, "task-inputs", taskId, "skills/selected"),
  );
  assert.equal(selected.path, join(selected.snapshot_root, "SKILL.md"));
  assert.equal(selected.source_locator, f.source);
  assert.deepEqual(await readdir(selected.snapshot_root), [
    "SKILL.md",
    "references",
  ]);
  assert.equal(
    await readFile(
      join(selected.snapshot_root, "references/method.md"),
      "utf8",
    ),
    "APPROVED_PAYLOAD_ONLY\n",
  );
  assert.equal((await lstat(selected.path)).mode & 0o777, 0o400);
  assert.equal(
    (await lstat(join(selected.archive_root, "SKILL.md"))).mode & 0o777,
    0o400,
  );
  await f.manager.verifySelections([selected]);
  await assert.rejects(f.manager.verifySelections([selected], "task_other"), {
    code: "SOURCE_DRIFT",
  });
  const owner = await verifyExecutionInputTask(
    f.dataDir,
    taskId,
    selected.execution_transport.task_binding_sha256,
  );
  assert.equal(
    owner.owner.selections[0].source_tree_sha256,
    selected.source_tree_sha256,
  );
  const profile = localProfile(
    "read-only",
    [],
    [selected.snapshot_root],
    f.root,
    [f.dataDir],
  );
  assert.equal(profile.filesystem[selected.snapshot_root], "read");
  for (const path of [
    paths.namespace,
    paths.taskRoot,
    dirname(f.dataDir),
    f.source,
  ])
    assert.equal(profile.filesystem[path], undefined);
  assert.equal(profile.filesystem[f.dataDir], "deny");
});

test("the approved multi-skill task set cannot omit or duplicate a selected input", async (t) => {
  const f = await fixture(t);
  const second = join(f.repoRoot, "kit/skills/second");
  await mkdir(second);
  await writeFile(join(second, "SKILL.md"), "# Second approved skill\n");
  const selected = await f.manager.selections(
    ["selected", "second"],
    "task_pair",
  );
  await f.manager.verifySelections(selected, "task_pair");
  await assert.rejects(f.manager.verifySelections([selected[0]], "task_pair"), {
    code: "SOURCE_DRIFT",
  });
  await assert.rejects(
    f.manager.verifySelections([selected[0], selected[0]], "task_pair"),
    { code: "SOURCE_DRIFT" },
  );
});

test("an existing task ownership binding rejects an empty supplied skill set", async (t) => {
  const f = await fixture(t);
  await f.select();
  await assert.rejects(f.manager.verifySelections([], taskId), {
    code: "SOURCE_DRIFT",
  });
  await assert.rejects(f.manager.verifySelections(undefined, taskId), {
    code: "SOURCE_DRIFT",
  });
});

test("an existing task ownership binding rejects every input stripped to equal-byte legacy canonical paths", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  const stripped = {
    source_locator: f.source,
    source_tree_sha256: selected.source_tree_sha256,
    snapshot_root: f.source,
    path: join(f.source, "SKILL.md"),
  };
  await assert.rejects(f.manager.verifySelections([stripped], taskId), {
    code: "SOURCE_DRIFT",
  });
  await f.manager.verifySelections([selected], taskId);
});

test("canonical, control archive and execution bytes are independently required", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  const target = join(selected.archive_root, "references/method.md");
  await chmod(target, 0o600);
  await writeFile(target, "changed archive\n");
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
  await writeFile(target, "APPROVED_PAYLOAD_ONLY\n");
  await chmod(target, 0o400);
  await f.manager.verifySelections([selected]);
  await writeFile(
    join(f.source, "references/method.md"),
    "changed canonical\n",
  );
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
});

test("missing execution copy fails closed without recreating or rebinding the archive", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  const archiveBefore = sha(
    await readFile(join(selected.archive_root, "SKILL.md")),
  );
  await rm(selected.snapshot_root, { recursive: true });
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
  assert.equal(
    sha(await readFile(join(selected.archive_root, "SKILL.md"))),
    archiveBefore,
  );
  await assert.rejects(lstat(selected.snapshot_root), { code: "ENOENT" });
});

test("extra files, ignored-cache names and empty directories are rejected in execution and archive copies", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  const extra = join(selected.snapshot_root, ".DS_Store");
  await writeFile(extra, "unapproved", { mode: 0o400 });
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
  await rm(extra);
  await mkdir(join(selected.snapshot_root, "__pycache__"), { mode: 0o700 });
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
  await rm(join(selected.snapshot_root, "__pycache__"), { recursive: true });
  await writeFile(join(selected.archive_root, "unknown.txt"), "unapproved", {
    mode: 0o400,
  });
  await assert.rejects(f.manager.verifySelections([selected]), {
    code: "SOURCE_DRIFT",
  });
});

test("transport binding cannot be reassigned to another service, task or input path", async (t) => {
  const f = await fixture(t);
  const [selected] = await f.select();
  for (const change of [
    { snapshot_root: f.source, path: join(f.source, "SKILL.md") },
    { archive_root: f.source },
    { source_locator: f.dataDir },
    {
      execution_transport: {
        ...selected.execution_transport,
        task_id: "../outside",
      },
    },
    {
      execution_transport: {
        ...selected.execution_transport,
        data_dir_sha256: "0".repeat(64),
      },
    },
    {
      execution_transport: {
        ...selected.execution_transport,
        task_binding_sha256: "0".repeat(64),
      },
    },
    { execution_transport: null },
    { execution_transport: undefined, archive_root: undefined },
  ])
    await assert.rejects(
      f.manager.verifySelections([{ ...selected, ...change }]),
    );
  await f.manager.verifySelections([selected]);
});

test("namespace and archive links never copy into an unrelated directory", async (t) => {
  const f = await fixture(t);
  const outside = join(f.root, "unrelated");
  await mkdir(outside);
  await writeFile(join(outside, "keep.txt"), "preserve\n");
  const paths = executionInputPaths(f.dataDir, taskId);
  await symlink(outside, paths.namespace);
  await assert.rejects(f.select(), { code: "SOURCE_DRIFT" });
  assert.deepEqual(await readdir(outside), ["keep.txt"]);
  await rm(paths.namespace);
  await symlink(outside, join(f.dataDir, "task-inputs"));
  await assert.rejects(f.select(), { code: "SOURCE_DRIFT" });
  assert.deepEqual(await readdir(outside), ["keep.txt"]);
});

test("pre-existing unowned namespace is never silently adopted", async (t) => {
  const f = await fixture(t);
  const paths = executionInputPaths(f.dataDir, taskId);
  await mkdir(paths.namespace);
  await writeFile(join(paths.namespace, "unknown-journal"), "preserve\n");
  await assert.rejects(f.select());
  assert.deepEqual(await readdir(paths.namespace), ["unknown-journal"]);
});

test("memory-store ancestry and dangling targets are rejected before namespace creation without env mutation", async (t) => {
  const f = await fixture(t);
  const nativeHome = join(f.root, "synthetic-native-home");
  await mkdir(nativeHome);
  const paths = executionInputPaths(f.dataDir, taskId);
  await symlink(paths.namespace, join(nativeHome, "memories"));
  await assert.rejects(executionInputLocation(f.dataDir, taskId, nativeHome), {
    code: "CAPABILITY_UNVERIFIED",
  });
  await assert.rejects(lstat(paths.namespace), { code: "ENOENT" });
  await rm(join(nativeHome, "memories"));
  await symlink(f.root, join(nativeHome, "memories_v2"));
  await assert.rejects(executionInputLocation(f.dataDir, taskId, nativeHome), {
    code: "CAPABILITY_UNVERIFIED",
  });
  await assert.rejects(lstat(paths.namespace), { code: "ENOENT" });
});

test("legacy capsules keep their original private snapshot contract without a silent execution rebind", async (t) => {
  const f = await fixture(t);
  const before = await f.manager.tree(f.source);
  const legacyRoot = join(f.dataDir, "legacy-snapshot");
  await mkdir(join(legacyRoot, "references"), { recursive: true });
  for (const row of before.manifest)
    await writeFile(
      join(legacyRoot, row.path),
      await readFile(join(f.source, row.path)),
      { mode: 0o400 },
    );
  const legacy = {
    source_locator: f.source,
    source_tree_sha256: before.tree_sha256,
    snapshot_root: legacyRoot,
    path: join(legacyRoot, "SKILL.md"),
  };
  const prior = JSON.stringify(legacy);
  await f.manager.verifySelections([legacy]);
  await f.manager.verifySelections([legacy], taskId);
  assert.equal(JSON.stringify(legacy), prior);
  await assert.rejects(
    lstat(executionInputPaths(f.dataDir, taskId).namespace),
    { code: "ENOENT" },
  );
});

async function retained(t) {
  const f = await fixture(t);
  const selected = await f.select();
  const store = new Store(join(f.dataDir, "service.sqlite"));
  t.after(() => store.close());
  store.put("settings", "owner", { id: "owner", locale: "uk" });
  store.put("project", "project_fixture", {
    id: "project_fixture",
    root: join(f.root, "native-product"),
  });
  store.put("task", taskId, {
    id: taskId,
    project_id: "project_fixture",
    status: "dispatched",
    capsule: { selected_skills: selected },
  });
  store.put("job", "job_old", {
    id: "job_old",
    task_id: taskId,
    project_id: "project_fixture",
    status: "completed",
    completed_at: OLD,
  });
  const retention = new RetentionManager({
    store,
    dataDir: f.dataDir,
    clock: () => Date.parse("2026-11-10T00:00:00Z"),
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
  return { ...f, selected, store, retention };
}

test("explicit retention prunes only its derived task and control cache, preserving sources and unknown siblings", async (t) => {
  const f = await retained(t);
  const paths = executionInputPaths(f.dataDir, taskId);
  await mkdir(join(paths.namespace, "unknown-task"));
  await writeFile(join(paths.namespace, "unknown-task/journal"), "preserve\n");
  const preview = await f.retention.preview({ forget_job_ids: ["job_old"] });
  assert.ok(
    f.retention.previews
      .get(preview.preview_id)
      .plan.files.some(
        (file) =>
          file.relative === "execution-inputs/" + taskId &&
          file.owned_execution,
      ),
  );
  await f.retention.apply({
    preview_id: preview.preview_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  await assert.rejects(lstat(paths.taskRoot), { code: "ENOENT" });
  await assert.rejects(lstat(join(f.dataDir, "task-inputs", taskId)), {
    code: "ENOENT",
  });
  assert.equal(
    await readFile(join(paths.namespace, "unknown-task/journal"), "utf8"),
    "preserve\n",
  );
  assert.equal(
    await readFile(join(f.source, "references/method.md"), "utf8"),
    "APPROVED_PAYLOAD_ONLY\n",
  );
  assert.equal(
    await readFile(join(f.dataDir, "owner-credentials.json"), "utf8"),
    "PRIVATE_SERVICE_CONTROL\n",
  );
});

test("retention rejects forged external ownership, linked replacements and unreviewed extra files", async (t) => {
  const f = await retained(t);
  const transport = f.selected[0].execution_transport;
  await assert.rejects(
    f.retention.file("execution-inputs/" + taskId, null, null, {
      ...transport,
      task_id: "other",
    }),
    { code: "OUTSIDE_ROOT" },
  );
  await writeFile(
    join(f.selected[0].snapshot_root, "unknown.txt"),
    "keep unknown",
    { mode: 0o400 },
  );
  await assert.rejects(f.retention.preview({ forget_job_ids: ["job_old"] }), {
    code: "SOURCE_DRIFT",
  });
  await rm(join(f.selected[0].snapshot_root, "unknown.txt"));
  const paths = executionInputPaths(f.dataDir, taskId);
  const outside = join(f.root, "outside");
  await mkdir(outside);
  await writeFile(join(outside, "keep"), "unrelated\n");
  await rename(paths.taskRoot, paths.taskRoot + "-retained");
  await symlink(outside, paths.taskRoot);
  await assert.rejects(f.retention.preview({ forget_job_ids: ["job_old"] }), {
    code: "SOURCE_DRIFT",
  });
  assert.deepEqual(await readdir(outside), ["keep"]);
});

test("store-JSON backup/restore preserves archive bytes, revokes dispatch and does not rebuild missing execution inputs", async (t) => {
  const f = await fixture(t);
  const codex = new EventEmitter();
  codex.close = async () => {};
  codex.status = { status: "not_started" };
  const app = new Application({
    dataDir: f.dataDir,
    repoRoot: f.repoRoot,
    codex,
  });
  t.after(() => app.close());
  const selected = await app.skills.selections(["selected"], taskId);
  const projectRoot = join(f.root, "native-product");
  await mkdir(projectRoot);
  app.store.put("project", "project_fixture", {
    id: "project_fixture",
    root: projectRoot,
  });
  app.store.put("task", taskId, {
    id: taskId,
    project_id: "project_fixture",
    status: "prepared",
    capsule: { selected_skills: selected },
  });
  const archive = join(selected[0].archive_root, "references/method.md");
  const before = sha(await readFile(archive));
  const backup = await app.backup();
  const backupRecord = app.store.get("backup", backup.backup_id);
  assert.ok(
    !(await readFile(backupRecord.path, "utf8")).includes(
      "APPROVED_PAYLOAD_ONLY",
    ),
  );
  const preview = await app.restorePreview({ backup_id: backup.backup_id });
  await app.restore({
    backup_id: backup.backup_id,
    sha256: preview.sha256,
    confirmed: true,
  });
  assert.equal(sha(await readFile(archive)), before);
  assert.equal(
    app.store.get("task", taskId).status,
    "restored_requires_preparation",
  );
  await assert.rejects(app.dispatch("project_fixture", { task_id: taskId }), {
    code: "TASK_NOT_READY",
  });
  await rm(selected[0].snapshot_root, { recursive: true });
  await assert.rejects(app.skills.verifySelections(selected), {
    code: "SOURCE_DRIFT",
  });
  assert.equal(sha(await readFile(archive)), before);
});
