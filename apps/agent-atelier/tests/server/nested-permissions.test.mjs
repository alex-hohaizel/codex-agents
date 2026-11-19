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
import { realpathSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import {
  NATIVE_AUTHORITY_NAMES,
  writablePaths,
  nativeAuthoritySnapshot,
  localProfile,
} from "../../server/permissions.mjs";
import { compileContext } from "../../server/context.mjs";
import { readSource } from "../../server/utils.mjs";
import { CodexAdapter } from "../../server/codex.mjs";

async function fixture(t) {
  const container = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-native-permissions-"),
  );
  t.after(() => rm(container, { recursive: true, force: true }));
  const root = join(container, "project[bracket]");
  await mkdir(join(root, "child/deeper"), { recursive: true });
  for (const base of ["", "child", "child/deeper"])
    for (const name of NATIVE_AUTHORITY_NAMES) {
      await mkdir(join(root, base, name), { recursive: true });
      await writeFile(
        join(root, base, name, "marker.txt"),
        "synthetic native source\n",
      );
    }
  return { root, container };
}
function capsule(root, allowed_paths = ["child"]) {
  return {
    task_id: "synthetic-task",
    root,
    scope: "workspace-write",
    allowed_paths,
    instruction_manifest: {
      settings: {
        native_route: { provider: "openai" },
        project_doc_fallback_filenames: [],
      },
    },
    capability_scope: {},
  };
}

test("write admission rejects native segments while native source reads remain available", async (t) => {
  const { root } = await fixture(t);
  for (const path of [
    "child/.agent-foundry",
    "child/.atelier/state",
    "child/.GIT",
    ".codex",
  ]) {
    assert.throws(() => writablePaths([path]), { code: "PRIVATE_PATH" });
    await assert.rejects(
      compileContext({
        project: { id: "synthetic", root },
        workspace: {
          project: { revision: 1 },
          requirements: [],
          sources: [],
          decisions: [],
          warnings: [],
        },
        payload: {
          objective: "Synthetic task",
          acceptance: "Native state preserved",
          scope: "workspace-write",
          allowed_paths: [path],
        },
        taskId: "synthetic",
        authorityEpoch: 1,
        instructionManifest: {},
      }),
      { code: "PRIVATE_PATH" },
    );
  }
  assert.equal(
    (await readSource(root, "child/.agent-foundry/marker.txt")).text,
    "synthetic native source\n",
  );
  assert.deepEqual(writablePaths([".", "./child"]), [".", "child"]);
  assert.throws(() => writablePaths(["child/../elsewhere"]), {
    code: "OUTSIDE_ROOT",
  });
  assert.throws(() => writablePaths(["child[other]"]), {
    code: "CAPABILITY_UNVERIFIED",
  });
});

test("inventory preserves every existing nested native read and confines recursive denies to writable roots", async (t) => {
  const { root } = await fixture(t);
  const snapshot = await nativeAuthoritySnapshot(root, ["child"]);
  assert.equal(snapshot.protected_paths.length, 18);
  const profile = localProfile(
    "workspace-write",
    ["child"],
    [],
    root,
    [],
    snapshot,
  );
  for (const base of ["child", "child/deeper"])
    for (const name of NATIVE_AUTHORITY_NAMES)
      assert.equal(
        profile.filesystem[":workspace_roots"][base + "/" + name],
        "read",
      );
  assert.equal(profile.filesystem[":workspace_roots"].child, "write");
  assert.equal(profile.filesystem[":workspace_roots"]["."], "read");
  const dynamic = Object.keys(profile.filesystem).filter((key) =>
    key.includes("/**/.["),
  );
  assert.equal(dynamic.length, 9);
  assert.ok(
    dynamic.every((key) => key.includes("project\\[bracket\\]/child/")),
  );
  assert.equal(profile.filesystem["/**/.git"], undefined);
});

test("inventory does not follow links and refuses ambiguous or incomplete native read exceptions", async (t) => {
  const { root, container } = await fixture(t);
  const outside = join(container, "outside");
  await mkdir(outside);
  await mkdir(join(outside, ".atelier"));
  await symlink(outside, join(root, "child/ordinary-link"));
  const snapshot = await nativeAuthoritySnapshot(root, ["child"]);
  assert.ok(
    !snapshot.protected_paths.some((entry) =>
      entry.path.includes("ordinary-link"),
    ),
  );
  await assert.rejects(
    nativeAuthoritySnapshot(root, ["child"], { maxEntries: 1 }),
    { code: "CAPABILITY_UNVERIFIED" },
  );
  await assert.rejects(
    nativeAuthoritySnapshot(root, ["child"], { maxDepth: 0 }),
    { code: "CAPABILITY_UNVERIFIED" },
  );
  await mkdir(join(root, "child/odd[branch]/.atelier"), { recursive: true });
  await assert.rejects(nativeAuthoritySnapshot(root, ["child"]), {
    code: "CAPABILITY_UNVERIFIED",
  });
  await rm(join(root, "child/odd[branch]"), { recursive: true });
  await mkdir(join(root, "child/linked"));
  await symlink(outside, join(root, "child/linked/.atelier"));
  await assert.rejects(nativeAuthoritySnapshot(root, ["child"]), {
    code: "CAPABILITY_UNVERIFIED",
  });
});

test("task configuration includes the actual inventory and turn rejects its drift before dispatch", async (t) => {
  const { root, container } = await fixture(t);
  const fakeExecutable = join(container, "fake-codex");
  await writeFile(fakeExecutable, "#!/bin/sh\nprintf '[]\\n'\n", {
    mode: 0o700,
  });
  const instructions = {
    aliases: async () => [],
    verify: async () => {},
    verifyLoaded: () => {},
  };
  const adapter = new CodexAdapter({
    dataDir: join(container, "data"),
    executable: fakeExecutable,
    instructions,
  });
  adapter.runtimeReadRoots = [];
  const cap = capsule(root);
  const configured = await adapter.taskConfiguration(root, cap);
  assert.equal(configured.nativeAuthority.protected_paths.length, 18);
  assert.equal(
    configured.config["permissions.atelier-task"].filesystem[
      ":workspace_roots"
    ]["child/deeper/.atelier"],
    "read",
  );
  adapter.connect = async () => {};
  adapter.status.auth_mode = "chatgpt";
  adapter.instructionSettings = async () => ({});
  adapter.taskConfiguration = async () => configured;
  const calls = [];
  adapter.rpc = async (method) => {
    calls.push(method);
    return {
      thread: { id: "synthetic-thread" },
      modelProvider: "openai",
        model: "gpt-6.2-sol",
        reasoningEffort: "ultra",
      instructionSources: [],
    };
  };
  await adapter.start(root, cap);
  let dispatched = 0;
  await adapter.turn("synthetic-thread", cap, () => dispatched++);
  assert.equal(dispatched, 1);
  assert.ok(calls.includes("turn/start"));
  calls.length = 0;
  await mkdir(join(root, "child/new-native/.atelier"), { recursive: true });
  await assert.rejects(
    adapter.turn("synthetic-thread", cap, () => dispatched++),
    { code: "SOURCE_DRIFT" },
  );
  assert.equal(dispatched, 1);
  assert.deepEqual(calls, []);
  await assert.rejects(adapter.turn("unknown-thread", cap), {
    code: "CAPABILITY_UNVERIFIED",
  });
});
