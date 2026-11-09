import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  writeFile,
  readFile,
  cp,
  chmod,
  readdir,
  stat,
  rm,
} from "node:fs/promises";
import { realpathSync, existsSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { tmpdir } from "node:os";
import { OptionalUpdates } from "../../server/optional_updates.mjs";
import { sha, digest } from "../../server/utils.mjs";

async function pins(root) {
  const result = {};
  async function walk(p) {
    for (const e of await readdir(p, { withFileTypes: true })) {
      const f = join(p, e.name);
      if (e.isDirectory()) await walk(f);
      else {
        const s = await stat(f);
        result[relative(root, f)] = {
          sha256: sha(await readFile(f)),
          bytes: s.size,
          mode: s.mode & 0o777,
        };
      }
    }
  }
  await walk(root);
  return result;
}
async function fixture(t) {
  const home = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-optional-update-"),
  );
  const repoRoot = join(home, "repo"),
    dataDir = join(home, "private"),
    installedRoot = join(home, "installed");
  const source = join(repoRoot, "optional-skills/atelier-orchestrator"),
    target = join(installedRoot, "atelier-orchestrator");
  await mkdir(join(source, "agents"), { recursive: true });
  await mkdir(join(source, "assets"));
  await mkdir(join(source, "scripts"));
  await mkdir(dataDir);
  await writeFile(
    join(source, "SKILL.md"),
    "---\nname: atelier-orchestrator\ndescription: Coordinate the synthetic result.\n---\n\n# Orchestrator1.0.1\n",
  );
  await writeFile(
    join(source, "agents/openai.yaml"),
    'interface:\n  icon_small: "./assets/icon.svg"\n  icon_large: "./assets/icon.svg"\n  brand_color: "#21CFC4"\npolicy:\n  allow_implicit_invocation: true\n',
  );
  await writeFile(
    join(source, "assets/icon.svg"),
    '<svg xmlns="http://www.w3.org/2000/svg"/>',
  );
  await writeFile(
    join(source, "scripts/helper.py"),
    'print("synthetic helper, never executed")\n',
  );
  await chmod(join(source, "scripts/helper.py"), 0o755);
  await cp(source, target, { recursive: true });
  const before = await pins(target);
  await writeFile(
    join(repoRoot, "optional-skills/UPDATE_BASELINES.json"),
    JSON.stringify({
      skills: { "atelier-orchestrator": { "1.0.1": { files: before } } },
    }),
  );
  await writeFile(
    join(source, "SKILL.md"),
    (await readFile(join(source, "SKILL.md"), "utf8")).replace(
      "1.0.1",
      "1.1.0",
    ),
  );
  await writeFile(join(source, "assets/routing.json"), "{}\n");
  const map = new Map([["settings:owner", { authority_epoch: "epoch" }]]);
  const store = {
    get: (k, id) => map.get(k + ":" + id),
    put: (k, id, v) => {
      map.set(k + ":" + id, structuredClone(v));
      return v;
    },
    list: (k) =>
      [...map].filter(([s]) => s.startsWith(k + ":")).map(([, v]) => v),
  };
  const manager = new OptionalUpdates({
    store,
    repoRoot,
    dataDir,
    installedRoot,
  });
  t.after(() => rm(home, { recursive: true, force: true }));
  return {
    source,
    target,
    repoRoot,
    dataDir,
    installedRoot,
    manager,
    store,
    before,
  };
}
const exact = (p) => ({
  preview_id: p.preview_id,
  sha256: p.sha256,
  confirmed: true,
});

test("rollback preserves a later deletion of an existing managed file", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" });
  const done = await f.manager.apply(exact(p));
  await rm(join(f.target, "scripts/helper.py"));
  const current = digest(await pins(f.target));
  await assert.rejects(
    f.manager.rollback({
      journal_id: done.id,
      current_sha256: current,
      confirmed: true,
    }),
    (e) => e.code === "SOURCE_DRIFT",
  );
  await assert.rejects(readFile(join(f.target, "scripts/helper.py")), {
    code: "ENOENT",
  });
});

test("optional update preserves icon/policy, verifies all bytes/modes, backs up and rolls back exactly", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" });
  assert.equal(p.ready, true);
  assert.equal(p.installed_version, "1.0.1");
  assert.equal(p.candidate_version, "1.1.0");
  const done = await f.manager.apply(exact(p));
  assert.equal(done.status, "completed");
  assert.equal(done.host_discovery_verified, false);
  assert.deepEqual(await pins(f.target), await pins(f.source));
  assert.deepEqual(
    await pins(join(f.dataDir, "optional-updates", done.id, "before")),
    f.before,
  );
  const verified = await f.manager.verify({ journal_id: done.id });
  assert.equal(verified.installed_source_verified, true);
  const rolled = await f.manager.rollback({
    journal_id: done.id,
    current_sha256: verified.current_sha256,
    confirmed: true,
  });
  assert.equal(rolled.status, "rolled_back");
  assert.deepEqual(await pins(f.target), f.before);
});

test("unknown installed edits and visual/policy changes never become an automatic overwrite", async (t) => {
  const f = await fixture(t);
  await writeFile(
    join(f.target, "scripts/helper.py"),
    "Local specialized behavior.",
  );
  const p = await f.manager.preview({ name: "atelier-orchestrator" });
  assert.equal(p.ready, false);
  assert.ok(p.conflicts.length);
  await assert.rejects(
    f.manager.apply(exact(p)),
    (e) => e.code === "PREVIEW_REQUIRED",
  );
  assert.equal(
    await readFile(join(f.target, "scripts/helper.py"), "utf8"),
    "Local specialized behavior.",
  );
  await writeFile(
    join(f.source, "assets/icon.svg"),
    "<svg>Changed identity</svg>",
  );
  await assert.rejects(
    f.manager.preview({ name: "atelier-orchestrator" }),
    (e) => e.code === "IDENTITY_CONFLICT",
  );
});

test("exact preview pins candidate/installed source and owner authority before any write", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" });
  await assert.rejects(
    f.manager.apply({ ...exact(p), confirmed: false }),
    (e) => e.code === "PREVIEW_REQUIRED",
  );
  await writeFile(
    join(f.source, "assets/routing.json"),
    "Changed after preview",
  );
  await assert.rejects(
    f.manager.apply(exact(p)),
    (e) => e.code === "SOURCE_DRIFT",
  );
  assert.deepEqual(await pins(f.target), f.before);
  const fresh = await f.manager.preview({ name: "atelier-orchestrator" });
  f.store.put("settings", "owner", { authority_epoch: "changed" });
  await assert.rejects(
    f.manager.apply(exact(fresh)),
    (e) => e.code === "SOURCE_DRIFT",
  );
});

test("read-only verification reconciles a lost response without replay; later edits prevent rollback", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" }),
    done = await f.manager.apply(exact(p));
  f.store.put("optional-update", done.id, { ...done, status: "pending" });
  const resumed = new OptionalUpdates({
    store: f.store,
    repoRoot: f.repoRoot,
    dataDir: f.dataDir,
    installedRoot: f.installedRoot,
  });
  assert.equal(
    f.store.get("optional-update", done.id).status,
    "outcome_unknown",
  );
  const proof = await resumed.verify({ journal_id: done.id });
  assert.equal(proof.status, "completed");
  assert.match(proof.reconciled_by, /no replay/);
  await writeFile(
    join(f.target, "scripts/helper.py"),
    "Later owner customization.",
  );
  const current = digest(await pins(f.target));
  await assert.rejects(
    resumed.rollback({
      journal_id: done.id,
      current_sha256: current,
      confirmed: true,
    }),
    (e) => e.code === "SOURCE_DRIFT",
  );
});

test("expired before-copies cannot be claimed as rollback support", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" }),
    done = await f.manager.apply(exact(p));
  const observed = await f.manager.verify({ journal_id: done.id });
  f.store.put("optional-update", done.id, { ...observed, backup_pruned: true });
  await assert.rejects(
    f.manager.rollback({
      journal_id: done.id,
      current_sha256: observed.current_sha256,
      confirmed: true,
    }),
    (e) => e.code === "SOURCE_DRIFT",
  );
});

test("staging failure has a consumed preview and owned terminal journal before any private copy or target write", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" });
  await writeFile(
    join(f.dataDir, "optional-updates"),
    "A file blocks the staging directory.",
  );
  await assert.rejects(
    f.manager.apply(exact(p)),
    (e) => e.code === "ENOTDIR" || e.code === "EEXIST",
  );
  const rows = f.store.list("optional-update");
  assert.equal(rows.length, 1);
  const failed = rows[0];
  assert.equal(failed.status, "failed");
  assert.equal(failed.phase, "staging");
  assert.ok(failed.completed_at);
  assert.ok(failed.stage_error);
  assert.deepEqual(failed.written, []);
  assert.deepEqual(failed.removed, []);
  assert.equal(f.manager.busy, false);
  assert.deepEqual(await pins(f.target), f.before);
  await assert.rejects(
    f.manager.apply(exact(p)),
    (e) => e.code === "PREVIEW_REQUIRED",
  );
});

test("source drift during staging leaves every private copy owned and the installed source unchanged", async (t) => {
  const f = await fixture(t),
    p = await f.manager.preview({ name: "atelier-orchestrator" }),
    put = f.store.put;
  let stagedId = null;
  f.store.put = (kind, ident, row) => {
    const value = put(kind, ident, row);
    if (
      kind === "optional-update" &&
      row.status === "pending" &&
      row.phase === "staging"
    ) {
      stagedId = ident;
      assert.equal(
        existsSync(join(f.dataDir, "optional-updates", ident)),
        false,
      );
      assert.equal(f.manager.previews.has(p.preview_id), true);
      writeFileSync(
        join(f.source, "assets/routing.json"),
        "Changed after preflight while entering staging.",
      );
    }
    return value;
  };
  await assert.rejects(
    f.manager.apply(exact(p)),
    (e) => e.code === "SOURCE_DRIFT",
  );
  const failed = f.store.get("optional-update", stagedId);
  assert.equal(failed.status, "failed");
  assert.equal(failed.phase, "staging");
  assert.match(failed.stage_error, /staging/);
  assert.ok(failed.completed_at);
  assert.equal(f.manager.previews.has(p.preview_id), false);
  assert.deepEqual(await pins(f.target), f.before);
  assert.deepEqual(
    await pins(join(f.dataDir, "optional-updates", stagedId, "before")),
    f.before,
  );
  assert.ok(existsSync(join(f.dataDir, "optional-updates", stagedId, "after")));
  assert.deepEqual(failed.written, []);
  assert.deepEqual(failed.removed, []);
});
