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
import { tmpdir } from "node:os";
import { join } from "node:path";
import { inspectProject } from "../../server/projects.mjs";
import { compileContext } from "../../server/context.mjs";
import { sha } from "../../server/utils.mjs";

async function fixture(t, { conventional = true } = {}) {
  const root = await mkdtemp(join(realpathSync(tmpdir()), "atelier-context-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(join(root, ".atelier"));
  await mkdir(join(root, ".appatelier"));
  await mkdir(join(root, "sources"));
  await writeFile(
    join(root, "AGENTS.md"),
    "Keep native authority and accepted identity.\n",
  );
  await writeFile(
    join(root, ".appatelier/state.json"),
    JSON.stringify({
      schema: "fixture-native/1",
      phase: "implementation",
      objective: "Improve the actual working project",
      requirements: [
        {
          id: "UNDOCUMENTED-MUST",
          text: "Preserve the existing recovery route",
          priority: "must",
        },
      ],
    }),
  );
  await writeFile(
    join(root, "sources/owner.md"),
    "Пріоритет — контекст, дизайн і робоча панель. WORK відкладено.\n",
  );
  await writeFile(
    join(root, "sources/requests.json"),
    JSON.stringify({
      schema: "ai-data-production.request-register/1",
      requirements: [
        {
          id: "R24",
          source_text_uk: "Пріоритет — контекст, дизайн і робоча панель.",
          requirement_en: "Context, design and a working panel first",
          priority: "must",
        },
      ],
    }),
  );
  await writeFile(
    join(root, "sources/checkpoint.json"),
    JSON.stringify({
      decisions: [
        { id: "D0", text: "Earlier documentation-only stage" },
        {
          id: "D1",
          text: "Current bounded implementation stage",
          supersedes: ["D0"],
        },
      ],
      deferred_work: [
        { id: "WORK", reason: "Owner deferred WORK until access recovery" },
      ],
      identity: [
        {
          id: "accepted-master",
          path: "sources/master.svg",
          status: "declared",
        },
      ],
    }),
  );
  await writeFile(
    join(root, "sources/master.svg"),
    '<svg xmlns="http://www.w3.org/2000/svg"><title>Original master</title></svg>',
  );
  const manifestPath = conventional
    ? ".atelier/context-bindings.json"
    : "sources/bindings.json";
  const pin = async (path, role, requirement_ids = []) => ({
    path,
    role,
    sha256: sha(await readFile(join(root, path))),
    requirement_ids,
  });
  const manifest = {
    schema: "atelier.context-bindings/1",
    project_root: root,
    expected_requirement_ids: ["R24"],
    expected_must_ids: ["R24"],
    requirement_links: [
      {
        requirement_id: "R24",
        source_path: "sources/owner.md",
        source_excerpt: "Пріоритет — контекст, дизайн і робоча панель.",
      },
    ],
    sources: [
      await pin("sources/owner.md", "original-request"),
      await pin("sources/requests.json", "requirements", ["R24"]),
      await pin("sources/checkpoint.json", "checkpoint"),
      await pin("sources/master.svg", "accepted-identity"),
    ],
  };
  const save = () =>
    writeFile(join(root, manifestPath), JSON.stringify(manifest));
  await save();
  const inspect = () =>
    inspectProject(root, { sourceRefs: conventional ? [] : [manifestPath] });
  const prepare = async (payload = {}) => {
    const workspace = await inspect();
    return compileContext({
      project: { id: "project-test", root },
      workspace: { ...workspace, project: { revision: workspace.revision } },
      payload: {
        objective: "Continue the current bounded task",
        acceptance: "Report actual evidence and unresolved work",
        requirement_ids: [],
        ...payload,
      },
      taskId: "task-test",
      authorityEpoch: 1,
      instructionManifest: {},
    });
  };
  return { root, manifest, manifestPath, save, inspect, prepare };
}

test("standard project context is implicitly pinned and linked replacements are refused", async (t) => {
  const f = await fixture(t);
  const path = "project-context.json";
  const bytes = JSON.stringify({
    schema_version: "codex-agents.project-context/1",
    project_id: "project-test",
    preferred_language: "uk",
  });
  await writeFile(join(f.root, path), bytes);
  const workspace = await f.inspect();
  const exactPin = (row) => row.path === path && row.sha256 === sha(bytes);
  assert.ok(workspace.sources.some(exactPin));
  const capsule = await f.prepare();
  assert.ok(capsule.original_sources.some(exactPin));

  await rm(join(f.root, path));
  await writeFile(join(f.root, "sources/replacement.json"), bytes);
  await symlink("sources/replacement.json", join(f.root, path), "file");
  const linked = await f.inspect();
  assert.ok(
    linked.warnings.some((row) => row.path === path && row.code === "OUTSIDE_ROOT"),
  );
  assert.ok(!linked.sources.some((row) => row.path === path));
});

test("declared source reconciliation preserves all musts, actual bilingual source, current corrections and deferred work", async (t) => {
  const f = await fixture(t);
  const workspace = await f.inspect();
  const capsule = await f.prepare();
  assert.equal(workspace.phase, "implementation");
  assert.equal(workspace.context_coverage.status, "verified-declared-bindings");
  assert.equal(
    workspace.context_coverage.source_completeness_authenticated,
    false,
  );
  assert.equal(capsule.source_completeness_authenticated, false);
  assert.equal(
    capsule.context_coverage.requirement_checks[0].status,
    "verified-excerpt",
  );
  assert.deepEqual(
    capsule.requirements.map((row) => row.id),
    ["R24", "UNDOCUMENTED-MUST", "task-test:request"],
  );
  const request = capsule.requirements.find((row) => row.id === "R24");
  assert.equal(
    request.verbatim,
    "Пріоритет — контекст, дизайн і робоча панель.",
  );
  assert.equal(
    request.interpretation,
    "Context, design and a working panel first",
  );
  assert.equal(request.source_sha256, f.manifest.sources[1].sha256);
  assert.equal(capsule.decisions.length, 2);
  assert.deepEqual(
    capsule.current_decisions.map((row) => row.id),
    ["D1"],
  );
  assert.equal(capsule.corrections[0].source_ref, "sources/checkpoint.json");
  assert.equal(capsule.deferred_work[0].id, "WORK");
  assert.equal(capsule.identity[0].path, "sources/master.svg");
  assert.ok(
    capsule.original_sources.some((row) => row.path === "sources/master.svg"),
  );
  assert.equal(
    new Set(capsule.original_sources.map((row) => row.path)).size,
    capsule.original_sources.length,
  );
  assert.equal(workspace.goal.status, "declared");
});

test("an explicitly selected binding works without imposing a new native state file", async (t) => {
  const f = await fixture(t, { conventional: false });
  const capsule = await f.prepare();
  assert.equal(
    capsule.context_coverage.manifest_ref.path,
    "sources/bindings.json",
  );
  assert.equal(capsule.context_coverage.source_checks.length, 4);
});

test("legacy projects remain readable and executable with honest unverified source coverage", async (t) => {
  const f = await fixture(t);
  await rm(join(f.root, f.manifestPath));
  const capsule = await f.prepare();
  assert.equal(capsule.context_coverage.status, "unverified");
  assert.ok(capsule.requirements.some((row) => row.id === "UNDOCUMENTED-MUST"));
});

test("stale original bytes change the native revision and block task preparation", async (t) => {
  const f = await fixture(t);
  const before = await f.inspect();
  await writeFile(
    join(f.root, "sources/owner.md"),
    "A later owner correction must not be hidden by an older source pin.",
  );
  const after = await f.inspect();
  assert.notEqual(after.revision, before.revision);
  assert.equal(after.context_coverage.source_checks[0].status, "changed");
  await assert.rejects(f.prepare(), (error) => error.code === "SOURCE_DRIFT");
});

test("the same-shaped packet from another project cannot be used for this project", async (t) => {
  const f = await fixture(t);
  f.manifest.project_root = join(f.root, "different-project");
  await f.save();
  await assert.rejects(f.prepare(), (error) => error.code === "SCOPE_MISMATCH");
});

test("duplicate decision IDs without supersedes remain ambiguous and block only bound admission", async (t) => {
  const f = await fixture(t);
  const path = join(f.root, "sources/checkpoint.json");
  const data = JSON.parse(await readFile(path));
  data.decisions = [
    { id: "D1", text: "Retain accepted identity" },
    { id: "D1", text: "Replace the identity" },
  ];
  await writeFile(path, JSON.stringify(data));
  f.manifest.sources.find((row) => row.path === "sources/checkpoint.json").sha256 = sha(await readFile(path));
  await f.save();
  const view = await f.inspect();
  assert.equal(view.current_decisions.length, 2);
  assert.equal(view.context_coverage.status, "conflict");
  await assert.rejects(f.prepare(), (error) => error.code === "CONTEXT_CONFLICT");
  await rm(join(f.root, ".atelier/context-bindings.json"));
  const legacy = await inspectProject(f.root, { sourceRefs: ["sources/checkpoint.json"] });
  assert.equal(legacy.current_decisions.length, 2);
  assert.ok(legacy.context_coverage.issues.every((row) => row.blocking === false));
  const result = await compileContext({ project: { root: f.root, id: "P", revision: legacy.revision }, workspace: { ...legacy, project: { revision: legacy.revision } }, taskId: "T", authorityEpoch: "E", payload: { objective: "Read the legacy current state", acceptance: "Report ambiguous decisions with source", scope: "read-only" }, instructionManifest: {} });
  assert.equal(result.current_decisions.length, 2);
});

test("an omitted or weakened expected must blocks instead of passing a valid but incomplete graph", async (t) => {
  const f = await fixture(t);
  f.manifest.expected_must_ids.push("MISSING-MUST");
  await f.save();
  const view = await f.inspect();
  assert.deepEqual(view.context_coverage.missing_must_ids, ["MISSING-MUST"]);
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
  f.manifest.expected_must_ids = ["R24"];
  const path = join(f.root, "sources/requests.json");
  const data = JSON.parse(await readFile(path));
  data.requirements[0].priority = "could";
  await writeFile(path, JSON.stringify(data));
  f.manifest.sources[1].sha256 = sha(await readFile(path));
  await f.save();
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});

test("missing required originals stay visible and cannot be relabeled as successful context", async (t) => {
  const f = await fixture(t);
  await rm(join(f.root, "sources/owner.md"));
  const view = await f.inspect();
  assert.equal(view.context_coverage.source_checks[0].status, "missing");
  assert.equal(view.context_coverage.status, "incomplete");
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});

test("source requirement claims need observed parsed native records and the exact source path", async (t) => {
  const f = await fixture(t);
  f.manifest.sources[0].requirement_ids = ["R24"];
  await f.save();
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
  f.manifest.sources[0].requirement_ids = [];
  const path = join(f.root, "sources/requests.json");
  await writeFile(
    path,
    JSON.stringify({ unknown_schema: "opaque only", text: "R24" }),
  );
  f.manifest.sources[1].sha256 = sha(await readFile(path));
  await f.save();
  const view = await f.inspect();
  assert.equal(
    view.context_coverage.source_checks[1].projection_status,
    "unsupported",
  );
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});

test("a stable requirement ID cannot hide a lost declared original quote", async (t) => {
  const f = await fixture(t);
  const path = join(f.root, "sources/requests.json");
  const data = JSON.parse(await readFile(path));
  data.requirements[0].source_text_uk = "Зробити щось простіше.";
  await writeFile(path, JSON.stringify(data));
  f.manifest.sources[1].sha256 = sha(await readFile(path));
  await f.save();
  const view = await f.inspect();
  assert.equal(
    view.context_coverage.requirement_checks[0].status,
    "quote-not-in-requirement",
  );
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});

test("correction cycles or unknown predecessors preserve all decisions and stop dependent work", async (t) => {
  const f = await fixture(t);
  const path = join(f.root, "sources/checkpoint.json");
  const data = JSON.parse(await readFile(path));
  data.decisions[0].supersedes = ["D1"];
  await writeFile(path, JSON.stringify(data));
  f.manifest.sources[2].sha256 = sha(await readFile(path));
  await f.save();
  const view = await f.inspect();
  assert.equal(view.current_decisions.length, 2);
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_CONFLICT",
  );
  data.decisions[0].supersedes = ["UNKNOWN"];
  await writeFile(path, JSON.stringify(data));
  f.manifest.sources[2].sha256 = sha(await readFile(path));
  await f.save();
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_CONFLICT",
  );
});

test("binding sources cannot escape the selected project through traversal or a link", async (t) => {
  const f = await fixture(t);
  f.manifest.sources[0].path = "../outside.md";
  await f.save();
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
  await symlink(
    join(f.root, "sources/owner.md"),
    join(f.root, "sources/link.md"),
  );
  f.manifest.sources[0].path = "sources/link.md";
  await f.save();
  const view = await f.inspect();
  assert.equal(view.context_coverage.source_checks[0].status, "unreadable");
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});

test("an unreadable conventional binding cannot silently fall back to the legacy path", async (t) => {
  const f = await fixture(t);
  await writeFile(
    join(f.root, f.manifestPath),
    '{"schema":"atelier.context-bindings/1","schema":"duplicate"}',
  );
  const view = await f.inspect();
  assert.equal(view.context_coverage.status, "incomplete");
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
  await rm(join(f.root, f.manifestPath));
  await symlink(join(f.root, "sources/owner.md"), join(f.root, f.manifestPath));
  await assert.rejects(
    f.prepare(),
    (error) => error.code === "CONTEXT_INCOMPLETE",
  );
});
