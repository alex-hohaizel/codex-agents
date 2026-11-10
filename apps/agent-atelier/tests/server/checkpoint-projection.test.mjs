import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, readFile, rm } from "node:fs/promises";
import { realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { inspectProject } from "../../server/projects.mjs";
import { sha } from "../../server/utils.mjs";

const recorded = () => ({
  phase: "Доопрацювання дизайну операційної панелі",
  completed: [
    "Зафіксовано виконання перевірки; прийняття продукту не підтверджено",
  ],
  in_progress: ["Поточне доопрацювання"],
  next: "  Перевірити показаний результат із власником.  ",
});
async function fixture(
  t,
  { role = "checkpoint", required = true, manifest = true } = {},
) {
  const root = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-checkpoint-projection-"),
  );
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(join(root, ".atelier"));
  await mkdir(join(root, ".appatelier"));
  await mkdir(join(root, "sources"));
  await writeFile(
    join(root, ".appatelier/state.json"),
    JSON.stringify({ schema: "test-native/1", phase: "native-phase" }),
  );
  const path = "sources/checkpoint.json";
  const data = recorded();
  await writeFile(join(root, path), JSON.stringify(data));
  const pin = async (path, extra = {}) => ({
    path,
    role,
    required,
    sha256: sha(await readFile(join(root, path))),
    ...extra,
  });
  const binding = {
    schema: "atelier.context-bindings/1",
    project_root: root,
    expected_requirement_ids: [],
    expected_must_ids: [],
    sources: [await pin(path)],
  };
  const save = () =>
    writeFile(
      join(root, ".atelier/context-bindings.json"),
      JSON.stringify(binding),
    );
  if (manifest) await save();
  return {
    root,
    path,
    data,
    binding,
    save,
    pin,
    inspect: () => inspectProject(root, manifest ? {} : { sourceRefs: [path] }),
  };
}

test("one verified required checkpoint preserves declared values and native phase", async (t) => {
  const f = await fixture(t);
  const view = await f.inspect();
  assert.equal(view.phase, "native-phase");
  assert.equal(view.current_checkpoint_gap, null);
  assert.deepEqual(view.current_checkpoint, {
    ...f.data,
    source_ref: f.path,
    source_sha256: f.binding.sources[0].sha256,
    status: "declared",
  });
  assert.equal(view.current_checkpoint.next, f.data.next);
  assert.equal(view.context_coverage.status, "verified-declared-bindings");
  assert.equal(view.context_coverage.source_completeness_authenticated, false);
});

test("wrong role and optional checkpoint cannot become the current phase", async (t) => {
  for (const options of [{ role: "checkpoint-notes" }, { required: false }]) {
    const f = await fixture(t, options);
    const view = await f.inspect();
    assert.equal(view.current_checkpoint, null);
    assert.equal(view.current_checkpoint_gap.blocking, false);
    assert.equal(view.phase, "native-phase");
    assert.equal(view.context_coverage.status, "verified-declared-bindings");
  }
});

test("a changed required checkpoint stays unknown and retains existing source drift", async (t) => {
  const f = await fixture(t);
  await writeFile(
    join(f.root, f.path),
    JSON.stringify({ ...f.data, phase: "Changed after pin" }),
  );
  const view = await f.inspect();
  assert.equal(view.current_checkpoint, null);
  assert.equal(
    view.current_checkpoint_gap.code,
    "CHECKPOINT_SOURCE_UNVERIFIED",
  );
  assert.equal(view.current_checkpoint_gap.blocking, false);
  assert.ok(
    view.context_coverage.issues.some(
      (issue) => issue.code === "SOURCE_DRIFT" && issue.blocking,
    ),
  );
});

test("multiple checkpoint declarations remain ambiguous without guessing a source", async (t) => {
  const f = await fixture(t);
  await writeFile(
    join(f.root, "sources/other.json"),
    JSON.stringify({ ...recorded(), phase: "Another checkpoint" }),
  );
  f.binding.sources.push(await f.pin("sources/other.json"));
  await f.save();
  const view = await f.inspect();
  assert.equal(view.current_checkpoint, null);
  assert.equal(view.current_checkpoint_gap.code, "CHECKPOINT_AMBIGUOUS");
  assert.deepEqual(view.current_checkpoint_gap.source_refs, [
    f.path,
    "sources/other.json",
  ]);
  assert.equal(view.context_coverage.status, "verified-declared-bindings");
});

test("loaded legacy checkpoint text without a manifest is not guessed or globally blocked", async (t) => {
  const f = await fixture(t, { manifest: false });
  const view = await f.inspect();
  assert.ok(view.sources.some((source) => source.path === f.path));
  assert.equal(view.current_checkpoint, null);
  assert.equal(view.current_checkpoint_gap.code, "CHECKPOINT_NOT_DECLARED");
  assert.equal(view.current_checkpoint_gap.blocking, false);
  assert.equal(view.phase, "native-phase");
  assert.ok(!view.context_coverage.issues.some((issue) => issue.blocking));
});

test("unknown or oversized checkpoint shapes return a nonblocking projection gap", async (t) => {
  const f = await fixture(t);
  for (const replacement of [
    { completed: "Not an array" },
    { completed: [{ text: "Unrecognized record shape" }] },
    { in_progress: Array(101).fill("Bounded source row") },
    { next: { text: "Do not guess nested shape" } },
    { phase: " " },
    { phase: "x".repeat(2001) },
  ]) {
    await writeFile(
      join(f.root, f.path),
      JSON.stringify({ ...recorded(), ...replacement }),
    );
    f.binding.sources = [await f.pin(f.path)];
    await f.save();
    const view = await f.inspect();
    assert.equal(view.current_checkpoint, null);
    assert.equal(
      view.current_checkpoint_gap.code,
      "CHECKPOINT_SHAPE_UNSUPPORTED",
    );
    assert.equal(view.current_checkpoint_gap.blocking, false);
    assert.equal(view.context_coverage.status, "verified-declared-bindings");
  }
});

test("checkpoint source text retains the existing privacy redaction policy", async (t) => {
  const f = await fixture(t);
  const value = {
    ...recorded(),
    completed: ["Bearer synthetic-token-0123456789"],
  };
  await writeFile(join(f.root, f.path), JSON.stringify(value));
  f.binding.sources = [await f.pin(f.path)];
  await f.save();
  const view = await f.inspect();
  assert.equal(view.current_checkpoint.status, "declared");
  assert.equal(view.current_checkpoint.completed[0], "[REDACTED]");
  assert.equal(
    view.current_checkpoint.source_sha256,
    f.binding.sources[0].sha256,
  );
});
