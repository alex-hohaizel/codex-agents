import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  writeFile,
  rm,
  readlink,
  symlink,
} from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import { randomUUID } from "node:crypto";
import {
  InstructionsManager,
  instructionSettings,
} from "../../server/instructions.mjs";
async function fixture() {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-instructions-"),
  );
  const home = join(root, "home"),
    repo = join(root, "repo [literal]"),
    project = join(repo, "child"),
    state = join(root, "state");
  await mkdir(home);
  await mkdir(join(repo, ".git"), { recursive: true });
  await mkdir(project);
  await mkdir(state);
  for (const path of [
    join(home, "AGENTS.md"),
    join(repo, "AGENTS.md"),
    join(project, "AGENTS.md"),
  ])
    await writeFile(path, "Synthetic governing instruction.\n");
  return {
    root,
    home,
    repo,
    project,
    state,
    manager: new InstructionsManager({ dataDir: state, codexHome: home }),
    close: () => rm(root, { recursive: true, force: true }),
  };
}
test("governing pins retain chain, candidate absence, native precedence and instruction bytes", async () => {
  const f = await fixture();
  try {
    const m = await f.manager.capture(f.project);
    assert.deepEqual(
      m.sources.map((x) => x.path),
      [
        join(f.home, "AGENTS.md"),
        join(f.repo, "AGENTS.md"),
        join(f.project, "AGENTS.md"),
      ],
    );
    assert.equal(
      m.candidates.find((x) => x.path === join(f.project, "AGENTS.override.md"))
        .present,
      false,
    );
    await f.manager.verify(m);
    await writeFile(join(f.project, "AGENTS.override.md"), "");
    await assert.rejects(
      f.manager.verify(m),
      (error) => error.code === "SOURCE_DRIFT",
    );
    const empty = await f.manager.capture(f.project);
    assert.equal(
      empty.sources.some((row) => row.path === join(f.project, "AGENTS.md")),
      false,
    );
    assert.equal(
      empty.sources.find(
        (row) => row.path === join(f.project, "AGENTS.override.md"),
      ).nonempty,
      false,
    );
    f.manager.verifyLoaded(
      empty,
      empty.sources.filter((row) => row.nonempty).map((row) => row.path),
    );
    await writeFile(join(f.home, "AGENTS.md"), "Changed global rule");
    await assert.rejects(
      f.manager.verify(empty),
      (error) => error.code === "SOURCE_DRIFT",
    );
  } finally {
    await f.close();
  }
});
test("exact instruction aliases reject unexpected targets, linked sources and unpinned host source sets", async () => {
  const f = await fixture();
  try {
    const m = await f.manager.capture(f.project),
      task = "task_" + randomUUID(),
      aliases = await f.manager.aliases(m, task);
    assert.equal(aliases.length, 3);
    assert.equal(await readlink(aliases[0].path), m.sources[0].path);
    await rm(aliases[0].path);
    await symlink(join(f.repo, "AGENTS.md"), aliases[0].path);
    await assert.rejects(
      f.manager.aliases(m, task),
      (error) => error.code === "SOURCE_DRIFT",
    );
    assert.throws(
      () =>
        f.manager.verifyLoaded(m, [
          ...m.sources.map((row) => row.path),
          join(f.repo, "unreviewed.md"),
        ]),
      (error) => error.code === "CAPABILITY_UNVERIFIED",
    );
    await rm(join(f.project, "AGENTS.md"));
    await symlink(join(f.repo, "AGENTS.md"), join(f.project, "AGENTS.md"));
    await assert.rejects(
      f.manager.capture(f.project),
      (error) => error.code === "SOURCE_DRIFT",
    );
  } finally {
    await f.close();
  }
});
test("native instruction config refuses secret fallbacks, disabled budgets and custom billing routes", () => {
  for (const name of [
    ".env",
    "auth.json",
    "owner-credentials.json",
    "../AGENTS.md",
    "private.md",
  ])
    assert.throws(() =>
      instructionSettings({ project_doc_fallback_filenames: [name] }),
    );
  assert.throws(() => instructionSettings({ project_doc_max_bytes: 0 }));
  assert.throws(
    () => instructionSettings({ model_provider: "external-provider" }),
    (error) => error.code === "BILLING_AUTHORITY_REQUIRED",
  );
  assert.throws(
    () =>
      instructionSettings({
        model_provider: "openai",
        model_providers: { openai: { base_url: "https://example.test/api" } },
      }),
    (error) => error.code === "BILLING_AUTHORITY_REQUIRED",
  );
  assert.throws(
    () => instructionSettings({ chatgpt_base_url: "https://example.test/api" }),
    (error) => error.code === "BILLING_AUTHORITY_REQUIRED",
  );
  assert.throws(
    () =>
      instructionSettings({
        native_route: {
          provider: "openai",
          custom_provider: false,
          base_url_override: false,
        },
        model_providers: { openai: { base_url: "https://example.test/api" } },
      }),
    (error) => error.code === "BILLING_AUTHORITY_REQUIRED",
  );
  assert.equal(
    instructionSettings({
      chatgpt_base_url: "https://chatgpt.com/backend-api/",
    }).native_route.base_url_override,
    false,
  );
  assert.throws(
    () =>
      instructionSettings({
        chatgpt_base_url: "https://chatgpt.com/backend-api/other",
      }),
    (error) => error.code === "BILLING_AUTHORITY_REQUIRED",
  );
  assert.equal(instructionSettings().native_route.provider, "openai");
});
test("native budget and new root marker cannot silently reduce the pinned instruction chain", async () => {
  const f = await fixture();
  try {
    await assert.rejects(
      f.manager.capture(
        f.project,
        instructionSettings({ project_doc_max_bytes: 1 }),
      ),
      (error) => error.code === "CAPACITY_LIMIT",
    );
    const m = await f.manager.capture(f.project);
    await mkdir(join(f.project, ".git"));
    await assert.rejects(
      f.manager.verify(m),
      (error) => error.code === "SOURCE_DRIFT",
    );
  } finally {
    await f.close();
  }
});
