import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  writeFile,
  readFile,
  rename,
  rm,
  symlink,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import { join } from "node:path";
import { resolve } from "node:path";
import { EventEmitter } from "node:events";
import {
  PortfolioManager,
  NativeHistoryReader,
  turnWork,
} from "../../server/portfolio.mjs";
import {
  inspectProject,
  projectSignals,
  ProjectAdapter,
} from "../../server/projects.mjs";
import { proposeRoute } from "../../server/routing.mjs";
import { CodexAdapter, CodexHistoryAdapter } from "../../server/codex.mjs";
import { digest, sha, ServiceError } from "../../server/utils.mjs";
import { Application } from "../../server/application.mjs";

const store = (records = {}) => ({ list: (kind) => records[kind] ?? [] });
async function fixture(t) {
  const home = await mkdtemp(
    join(realpathSync(tmpdir()), "atelier-portfolio-test-"),
  );
  const root = join(home, "product"),
    dataDir = join(home, "service");
  await mkdir(root);
  await mkdir(dataDir);
  t.after(() => rm(home, { recursive: true, force: true }));
  return { home, root, dataDir };
}

test("native discovery traverses all pages/archive states without model operations or implicit binding", async (t) => {
  const { root, dataDir } = await fixture(t);
  await writeFile(
    join(root, "AGENTS.md"),
    "Preserve current product identity.\n",
  );
  const calls = [];
  const native = {
    allThreads: async (o) => {
      calls.push(o);
      if (o.archived)
        return {
          data: [
            {
              id: "old",
              cwd: root,
              name: "Older work",
              status: { type: "idle" },
            },
          ],
          nextCursor: null,
        };
      return o.cursor
        ? {
            data: [
              {
                id: "two",
                cwd: root,
                name: "Second work",
                status: { type: "active" },
              },
            ],
          }
        : {
            data: [
              {
                id: "one",
                cwd: root,
                name: "First work",
                status: { type: "idle" },
              },
            ],
            nextCursor: "page2",
          };
    },
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  const value = await manager.refresh();
  assert.equal(value.coverage.complete, true);
  assert.equal(value.coverage.pages, 3);
  assert.equal(value.coverage.native_threads, 3);
  assert.equal(value.projects.length, 1);
  assert.equal(value.projects[0].binding_id, null);
  assert.equal(value.projects[0].active, 1);
  assert.equal(value.projects[0].goal.status, "unknown");
  assert.deepEqual(
    calls.map((x) => [x.archived, x.cursor]),
    [
      [false, undefined],
      [false, "page2"],
      [true, undefined],
    ],
  );
  assert.equal(typeof new NativeHistoryReader(native).start, "undefined");
});

test("pagination bounds and repeated cursors are visible, never declared a complete inventory", async (t) => {
  const { root, dataDir } = await fixture(t);
  const native = {
    allThreads: async () => ({
      data: [{ id: "one", cwd: root, status: { type: "idle" } }],
      nextCursor: "same",
    }),
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  const partial = await manager.refresh({ max_pages: 1 });
  assert.equal(partial.coverage.complete, false);
  assert.equal(partial.coverage.truncated, true);
  await assert.rejects(
    () => manager.refresh({ max_pages: 4 }),
    (error) => error.code === "HOST_PROTOCOL_ERROR",
  );
  assert.equal(manager.get().status, "stale");
});

test("a bound project with no native session still has its source-backed goal and work map", async (t) => {
  const { root, dataDir } = await fixture(t);
  await mkdir(join(root, "docs/project"), { recursive: true });
  await writeFile(
    join(root, "docs/project/CHECKPOINT_UA.md"),
    "## Мета\nPreserve a real source-backed objective.\n\n## Наступний крок\n- Verify recovery.\n\n- [x] Recovery implementation.\n",
  );
  const manager = new PortfolioManager({
    store: store({ project: [{ id: "bound", root, name: "Bound project" }] }),
    codex: { allThreads: async () => ({ data: [] }) },
    dataDir,
  });
  const snapshot = await manager.refresh();
  assert.equal(snapshot.projects.length, 1);
  assert.equal(snapshot.projects[0].binding_id, "bound");
  const view = await manager.project(snapshot.projects[0].id);
  assert.equal(view.threads.length, 0);
  assert.equal(view.goal.status, "declared");
  assert.match(view.goal.text, /real source-backed/);
  assert.equal(view.work_groups.find((x) => x.id === "recorded").count, 1);
  assert.equal(view.coverage.complete, true);
});

test("private native roots stay metadata-only and arbitrary discovery IDs cannot read paths", async (t) => {
  const { root, dataDir } = await fixture(t);
  await writeFile(join(dataDir, "AGENTS.md"), "## Goal\nPRIVATE-CANARY\n");
  const native = {
    allThreads: async () => ({
      data: [{ id: "private", cwd: dataDir, status: { type: "idle" } }],
    }),
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  const value = await manager.refresh({ include_archived: false });
  assert.equal(value.projects[0].status, "unavailable");
  assert.equal(value.projects[0].goal.status, "unknown");
  assert.ok(!JSON.stringify(value).includes("PRIVATE-CANARY"));
  await assert.rejects(
    () => manager.project(value.projects[0].id),
    (error) => error.code === "PRIVATE_PATH",
  );
  await assert.rejects(
    () => manager.project("../../other"),
    (error) => error.code === "PROJECT_NOT_FOUND",
  );
});

test("recorded native and bound roots cannot be rebound through a link to outside source data", async (t) => {
  const { home, root, dataDir } = await fixture(t);
  const outside = join(home, "outside");
  await mkdir(outside);
  const canary = "## Goal\nOUTSIDE-OWNERSHIP-CANARY\n";
  await writeFile(join(outside, "AGENTS.md"), canary);
  await mkdir(join(root, ".agent-foundry"));
  const nativeBefore = '{"schema":"native-fixture","identity":"original"}\n';
  await writeFile(join(root, ".agent-foundry/state.json"), nativeBefore);
  const binding = { id: "bound", root, name: "Bound" };
  const records = { project: [binding] };
  const native = {
    allThreads: async () => ({ data: [{ id: "one", cwd: root }] }),
    readThread: async () => {
      throw new Error("Rebound native history must not be read");
    },
  };
  const manager = new PortfolioManager({
    store: store(records),
    codex: native,
    dataDir,
  });
  const before = await manager.refresh({ include_archived: false });
  await rename(root, root + "-original");
  await symlink(outside, root);
  await assert.rejects(
    () => manager.project(before.projects[0].id),
    (error) => error.code === "SOURCE_DRIFT",
  );
  const refreshed = await manager.refresh({ include_archived: false });
  assert.equal(refreshed.projects.length, 1);
  assert.equal(refreshed.projects[0].status, "unavailable");
  assert.ok(!JSON.stringify(refreshed).includes("OUTSIDE-OWNERSHIP-CANARY"));
  await assert.rejects(
    () => manager.project(refreshed.projects[0].id),
    (error) => error.code === "SOURCE_DRIFT",
  );
  const adapter = new ProjectAdapter(
    { ...store(records), get: () => binding },
    dataDir,
  );
  await assert.rejects(
    () => adapter.workspace("bound"),
    (error) => error.code === "SOURCE_DRIFT",
  );
  assert.equal(await readFile(join(outside, "AGENTS.md"), "utf8"), canary);
  assert.equal(
    await readFile(
      join(root + "-original", ".agent-foundry/state.json"),
      "utf8",
    ),
    nativeBefore,
  );
});

test("native history turns group actual outcomes and provenance; completed response is not accepted product", async (t) => {
  const { root, dataDir } = await fixture(t);
  const thread = {
    id: "one",
    cwd: root,
    name: "Implement current feature",
    status: { type: "idle" },
  };
  const native = {
    allThreads: async () => ({ data: [thread] }),
    readThread: async () => ({ thread }),
    historyTurns: async (_id, o) =>
      o.cursor
        ? { data: [{ id: "t0", status: "failed", items: [] }] }
        : {
            data: [
              {
                id: "t1",
                status: "completed",
                itemsView: "full",
                items: [
                  {
                    id: "u",
                    type: "userMessage",
                    content: [
                      {
                        type: "text",
                        text: "Use $mentioned-skill to repair current feature",
                      },
                      {
                        type: "skill",
                        name: "selected-skill",
                        path: "/approved/SKILL.md",
                      },
                    ],
                  },
                  {
                    id: "f",
                    type: "fileChange",
                    status: "completed",
                    changes: [{ path: join(root, "feature.mjs") }],
                  },
                  {
                    id: "c",
                    type: "commandExecution",
                    status: "completed",
                    exitCode: 0,
                  },
                  {
                    id: "a",
                    type: "agentMessage",
                    text: "Implemented feature with observed checks",
                  },
                ],
              },
            ],
            nextCursor: "older",
          },
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  await manager.refresh({ include_archived: false });
  const detail = await manager.project(manager.get().projects[0].id);
  assert.equal(detail.coverage.complete, true);
  assert.equal(detail.coverage.turn_pages, 2);
  const result = detail.work_groups.find((x) => x.id === "results").items[0];
  assert.equal(result.status, "answer_received");
  assert.equal(result.acceptance, "not_inferred");
  assert.equal(result.evidence_refs.length, 2);
  assert.deepEqual(
    result.skills.map((x) => [x.name, x.status]),
    [
      ["mentioned-skill", "mentioned"],
      ["selected-skill", "selected"],
    ],
  );
  assert.equal(
    detail.work_groups.find((x) => x.id === "attention").items[0].turn_id,
    "t0",
  );
});

test("only exact native Guardian metadata separates system checks; identical user content stays user work", async (t) => {
  const { root, dataDir } = await fixture(t);
  const title = "Guardian review";
  const threads = [
    {
      id: "typed-thread-source",
      cwd: root,
      name: title,
      source: "vscode",
      threadSource: "guardian_review",
      parentThreadId: "actual-parent",
    },
    {
      id: "typed-session-source",
      cwd: root,
      name: title,
      source: { subAgent: { other: "guardian" } },
      parentThreadId: "actual-parent",
    },
    {
      id: "ordinary-user",
      cwd: root,
      name: title,
      source: "vscode",
      threadSource: "user",
      parentThreadId: null,
    },
  ];
  const answer = JSON.stringify({
    risk_level: "low",
    user_authorization: "high",
    outcome: "allow",
    rationale: "Same structured text must not classify user work.",
  });
  const manager = new PortfolioManager({
    store: store(),
    dataDir,
    codex: {
      allThreads: async () => ({ data: threads }),
      readThread: async (id) => ({
        thread: threads.find((thread) => thread.id === id),
      }),
      historyTurns: async (id) => ({
        data: [
          {
            id: `turn-${id}`,
            status: "completed",
            itemsView: "full",
            items: [{ type: "agentMessage", text: answer }],
          },
        ],
      }),
    },
  });
  const snapshot = await manager.refresh({ include_archived: false });
  const detail = await manager.project(snapshot.projects[0].id);
  const reviews = detail.work_groups.find(
    (group) => group.id === "system_checks",
  );
  const work = detail.work_groups.find((group) => group.id === "results");
  assert.equal(reviews.count, 2);
  assert.equal(work.count, 1);
  assert.equal(work.items[0].thread_id, "ordinary-user");
  assert.equal(work.items[0].work_type, "native_work");
  assert.equal(work.items[0].outcome, answer);
  assert.ok(
    reviews.items.every(
      (item) =>
        item.status === "answer_received" &&
        item.native_status === "completed" &&
        item.response_observed &&
        item.product_result === false &&
        item.independent_qa === false,
    ),
  );
  assert.ok(
    reviews.items.every((item) => item.parent_thread_id === "actual-parent"),
  );
  assert.equal(
    reviews.items.find((item) => item.thread_id === "typed-thread-source")
      .native_thread_source,
    "guardian_review",
  );
  assert.deepEqual(
    reviews.items.find((item) => item.thread_id === "typed-session-source")
      .native_session_source,
    { subAgent: { other: "guardian" } },
  );
  assert.deepEqual(
    detail.threads.find((thread) => thread.id === "typed-session-source")
      .source,
    { subAgent: { other: "guardian" } },
  );
  assert.equal(
    detail.threads.find((thread) => thread.id === "typed-thread-source")
      .thread_source,
    "guardian_review",
  );
  assert.equal(manager.get().projects[0].known_work_items, 3);
  const nearMatch = turnWork(
    {
      id: "near-match",
      title,
      source: { subAgent: { other: "guardian-like" } },
      thread_source: "guardian_reviewed",
    },
    {
      id: "near-turn",
      status: "completed",
      items: [{ type: "agentMessage", text: answer }],
    },
  );
  assert.equal(nearMatch.work_type, "native_work");
});

test("completed user-message-only, whitespace response and unloaded history never become received results", () => {
  for (const items of [
    [],
    [
      {
        id: "u",
        type: "userMessage",
        content: [{ type: "text", text: "Begin the task" }],
      },
    ],
    [{ id: "a", type: "agentMessage", text: "   " }],
  ]) {
    const value = turnWork(
      { id: "thread", title: "Saved request" },
      { id: "turn", status: "completed", items, itemsView: "notLoaded" },
    );
    assert.equal(value.status, "recorded");
    assert.equal(value.response_observed, false);
    assert.equal(value.outcome, "");
    assert.equal(value.native_status, "completed");
    assert.equal(value.warnings[0].code, "NATIVE_COMPLETED_WITHOUT_ANSWER");
  }
  const action = turnWork(
    { id: "thread", title: "Observed command" },
    {
      id: "turn",
      status: "completed",
      items: [
        { id: "c", type: "commandExecution", status: "completed", exitCode: 0 },
      ],
    },
  );
  assert.equal(action.status, "recorded");
  assert.equal(action.execution_observed, true);
  assert.equal(action.response_observed, false);
});

test("history detects a thread moving to another project and does not expose its turns", async (t) => {
  const { root, dataDir, home } = await fixture(t);
  let called = false;
  const native = {
    allThreads: async () => ({ data: [{ id: "one", cwd: root }] }),
    readThread: async () => ({
      thread: { id: "one", cwd: join(home, "different") },
    }),
    historyTurns: async () => {
      called = true;
      return { data: [] };
    },
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  await manager.refresh({ include_archived: false });
  const detail = await manager.project(manager.get().projects[0].id);
  assert.equal(detail.coverage.complete, false);
  assert.equal(called, false);
  assert.equal(detail.warnings.at(-1).code, "SOURCE_DRIFT");
});

test("privacy invalidation during native reads rejects the old projection", async (t) => {
  const { root, dataDir } = await fixture(t);
  let release;
  const native = {
    allThreads: async () => ({ data: [{ id: "one", cwd: root }] }),
    readThread: async () => ({ thread: { id: "one", cwd: root } }),
    historyTurns: () =>
      new Promise((r) => {
        release = r;
      }),
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  await manager.refresh({ include_archived: false });
  const pending = manager.project(manager.get().projects[0].id);
  while (!release) await new Promise((r) => setTimeout(r, 1));
  manager.invalidate();
  release({ data: [] });
  await assert.rejects(
    () => pending,
    (error) => error.code === "SOURCE_DRIFT",
  );
  assert.equal(manager.get().projects.length, 0);
});

test("listed native metadata with empty persisted turn pages never certifies complete work history", async (t) => {
  const { root, dataDir } = await fixture(t);
  const thread = {
    id: "known-native",
    cwd: root,
    preview: "Actual earlier request",
    status: "notLoaded",
  };
  const manager = new PortfolioManager({
    store: store(),
    dataDir,
    codex: {
      allThreads: async () => ({ data: [thread] }),
      readThread: async () => ({
        thread: { ...thread, historyMode: "paginated", turns: [] },
      }),
      historyTurns: async () => ({ data: [], nextCursor: null }),
    },
  });
  const snapshot = await manager.refresh({ include_archived: false });
  const detail = await manager.project(snapshot.projects[0].id);
  assert.equal(detail.coverage.complete, false);
  assert.equal(detail.coverage.turns_observed, 0);
  assert.equal(detail.coverage.empty_history_threads, 1);
  assert.equal(detail.warnings[0].code, "NATIVE_HISTORY_EMPTY");
  assert.equal(detail.work_groups.length, 0);
});

test("project thread pages cover every native thread without overlap and update deduplicated global observed work", async (t) => {
  const { root, dataDir } = await fixture(t);
  await mkdir(join(root, "docs/project"), { recursive: true });
  await writeFile(
    join(root, "docs/project/CHECKPOINT.md"),
    "## Goal\nKeep current product identity.\n\n- [x] Existing source-backed work.\n",
  );
  const threads = Array.from({ length: 3 }, (_, i) => ({
    id: `thread-${i}`,
    cwd: root,
    status: "notLoaded",
  }));
  const reads = [];
  const native = {
    allThreads: async () => ({ data: threads }),
    readThread: async (id) => ({
      thread: threads.find((row) => row.id === id),
    }),
    historyTurns: async (id) => {
      reads.push(id);
      return {
        data: [
          {
            id: `turn-${id}`,
            status: "completed",
            itemsView: "full",
            items: [
              {
                type: "agentMessage",
                id: `response-${id}`,
                text: `Observed result for ${id}.`,
              },
            ],
          },
        ],
      };
    },
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  const snapshot = await manager.refresh({ include_archived: false });
  const ident = snapshot.projects[0].id,
    token = snapshot.checked_at;
  const pages = [];
  for (let offset = 0; offset < 3; offset++) {
    const page = await manager.project(ident, {
      max_threads: 1,
      thread_offset: offset,
      snapshot_checked_at: token,
    });
    pages.push(page);
    assert.deepEqual(
      page.threads.map((row) => row.id),
      [`thread-${offset}`],
    );
    assert.equal(page.coverage.page_complete, true);
    assert.equal(page.coverage.complete, false);
    assert.equal(
      page.coverage.next_thread_offset,
      offset < 2 ? offset + 1 : null,
    );
    assert.equal(manager.get().summary.work_items, offset + 2);
    assert.equal(manager.get().projects[0].known_work_items, offset + 2);
    assert.equal(
      manager.get().projects[0].history_coverage.complete,
      offset === 2,
    );
    assert.equal(manager.get().checked_at, token);
  }
  assert.deepEqual(
    reads,
    threads.map((row) => row.id),
  );
  const uniqueWork = new Map(
    pages
      .flatMap((page) => page.work_groups.flatMap((group) => group.items))
      .map((item) => [item.id, item]),
  );
  assert.equal(uniqueWork.size, 4);
  await manager.project(ident, {
    max_threads: 1,
    thread_offset: 1,
    snapshot_checked_at: token,
  });
  assert.equal(manager.get().summary.work_items, 4);
  await assert.rejects(
    () => manager.project(ident, { thread_offset: 1 }),
    (error) => error.code === "SOURCE_DRIFT",
  );
  await assert.rejects(
    () =>
      manager.project(ident, { thread_offset: 4, snapshot_checked_at: token }),
    (error) => error.code === "INVALID_INPUT",
  );
  await new Promise((resolve) => setTimeout(resolve, 2));
  await manager.refresh({ include_archived: false });
  assert.equal(manager.get().summary.work_items, 1);
  assert.equal(manager.get().projects[0].history_status, "not_loaded");
  await assert.rejects(
    () =>
      manager.project(ident, { thread_offset: 1, snapshot_checked_at: token }),
    (error) => error.code === "SOURCE_DRIFT",
  );
});

test("turn-page limits remain an explicit incomplete warning after project-thread pagination", async (t) => {
  const { root, dataDir } = await fixture(t);
  const thread = { id: "thread", cwd: root };
  const manager = new PortfolioManager({
    store: store(),
    dataDir,
    codex: {
      allThreads: async () => ({ data: [thread] }),
      readThread: async () => ({ thread }),
      historyTurns: async () => ({
        data: [{ id: "turn", status: "inProgress", items: [] }],
        nextCursor: "older-turns",
      }),
    },
  });
  const snapshot = await manager.refresh({ include_archived: false });
  const page = await manager.project(snapshot.projects[0].id, {
    max_turn_pages: 1,
  });
  assert.equal(page.coverage.next_thread_offset, null);
  assert.equal(page.coverage.page_complete, false);
  assert.equal(page.coverage.complete, false);
  assert.equal(page.warnings[0].code, "NATIVE_TURN_PAGE_LIMIT");
  assert.equal(manager.get().projects[0].history_coverage.complete, false);
});

test("native/service work keeps one canonical thread-turn identity across pages and preserves explicit review", async (t) => {
  for (const serviceFirst of [false, true]) {
    const { root, dataDir } = await fixture(t);
    const threads = [0, 1].map((i) => ({ id: `thread-${i}`, cwd: root }));
    if (serviceFirst) threads.reverse();
    const records = {
      project: [{ id: "binding", root, name: "Synthetic fixture" }],
      task: [
        {
          id: "paired-task",
          project_id: "binding",
          objective: "Existing completed task",
          status: "completed",
          capsule: {},
        },
      ],
      job: [
        {
          id: "paired-job",
          task_id: "paired-task",
          project_id: "binding",
          thread_id: "thread-0",
          turn_id: "turn-thread-0",
          status: "completed",
          output_text: "Observed answer",
          review_status: "accepted",
        },
      ],
    };
    const native = {
      allThreads: async () => ({ data: threads }),
      readThread: async (id) => ({
        thread: threads.find((row) => row.id === id),
      }),
      historyTurns: async (id) => ({
        data: [
          {
            id: `turn-${id}`,
            status: "completed",
            itemsView: "full",
            items: [
              { type: "agentMessage", text: "Observed answer" },
              {
                type: "commandExecution",
                id: `command-${id}`,
                status: "completed",
                exitCode: 0,
              },
            ],
          },
        ],
      }),
    };
    const manager = new PortfolioManager({
      store: store(records),
      codex: native,
      dataDir,
    });
    const snapshot = await manager.refresh({ include_archived: false });
    const pages = [];
    for (const offset of [0, 1])
      pages.push(
        await manager.project(snapshot.projects[0].id, {
          max_threads: 1,
          thread_offset: offset,
          snapshot_checked_at: snapshot.checked_at,
        }),
      );
    const containingNative = pages[serviceFirst ? 1 : 0].work_groups
      .flatMap((group) => group.items)
      .find((item) => item.thread_id === "thread-0");
    assert.match(containingNative.id, /^native-/);
    assert.equal(containingNative.source, "native-history");
    assert.equal(containingNative.job_id, "paired-job");
    assert.equal(containingNative.service_job_id, "paired-job");
    assert.equal(containingNative.owner_review, "accepted");
    assert.equal(containingNative.acceptance, "owner-review");
    assert.ok(
      containingNative.evidence_refs.some(
        (evidence) => evidence.kind === "service_job",
      ),
    );
    assert.ok(
      containingNative.evidence_refs.some(
        (evidence) => evidence.kind === "command_observation",
      ),
    );
    assert.equal(manager.get().projects[0].known_work_items, 2);
    assert.equal(manager.get().summary.work_items, 2);
    await manager.project(snapshot.projects[0].id, {
      max_threads: 1,
      thread_offset: 1,
      snapshot_checked_at: snapshot.checked_at,
    });
    assert.equal(manager.get().summary.work_items, 2);
    records.task.push({
      id: "unpaired-task",
      project_id: "binding",
      objective: "Prepared independent work",
      status: "prepared",
      capsule: {},
    });
    await mkdir(join(root, "docs/project"), { recursive: true });
    await writeFile(
      join(root, "docs/project/CHECKPOINT.md"),
      "- [x] Source-record-only work.\n",
    );
    const fresh = await manager.refresh({ include_archived: false });
    for (const offset of [0, 1])
      await manager.project(fresh.projects[0].id, {
        max_threads: 1,
        thread_offset: offset,
        snapshot_checked_at: fresh.checked_at,
      });
    assert.equal(manager.get().summary.work_items, 4);
    assert.equal(
      manager
        .get()
        .projects[0].work_groups.find((group) => group.id === "prepared").count,
      1,
    );
    assert.equal(
      manager
        .get()
        .projects[0].work_groups.find((group) => group.id === "recorded").count,
      1,
    );
  }
});

test("App singular groups and Markdown checkpoints preserve source-backed work and next steps", async (t) => {
  const { root } = await fixture(t);
  await mkdir(join(root, ".appatelier"));
  await mkdir(join(root, "docs/project"), { recursive: true });
  await writeFile(
    join(root, ".appatelier/state.json"),
    JSON.stringify({
      schema_version: "app-state/1",
      requirement: {
        r1: { text: "Keep original requirement", priority: "must" },
      },
      decision: { d1: { text: "Keep identity" } },
      job: { j1: { objective: "Repair current draft", status: "completed" } },
    }),
  );
  await writeFile(
    join(root, "docs/project/CHECKPOINT_UA.md"),
    "# Checkpoint\n\n## Мета\nKeep the accepted product meaning.\n\n## Наступний крок\n- Verify persisted draft.\n\n- [x] Implemented draft persistence.\n",
  );
  const view = await inspectProject(root);
  assert.equal(view.requirements[0].id, "r1");
  assert.equal(view.decisions[0].id, "d1");
  assert.equal(view.goal.status, "declared");
  assert.match(view.goal.text, /accepted product meaning/);
  assert.match(view.next_actions[0].text, /Verify persisted/);
  assert.equal(view.work_records.length, 2);
  assert.ok(view.work_records.every((x) => x.source_ref && x.source_sha256));
});

test("completed Markdown checkboxes stay recorded work and never become future next actions", () => {
  const source = "docs/project/CHECKPOINT_UA.md";
  const completed = Array.from(
    { length: 7 },
    (_, i) => `- [${i % 2 ? "X" : "x"}] Completed step ${i}.`,
  ).join("\n");
  const signals = projectSignals(
    [
      {
        path: source,
        data: {
          markdown: `## Наступний крок\n${completed}\n- [ ] Verify the next scenario.\n- Preserve the agreed identity.\nContinue with the independent review.\n`,
        },
      },
    ],
    [{ path: source, sha256: "a".repeat(64) }],
  );
  assert.deepEqual(
    signals.next_actions.map((action) => action.text),
    [
      "[ ] Verify the next scenario.",
      "Preserve the agreed identity.",
      "Continue with the independent review.",
    ],
  );
  assert.equal(signals.work_records.length, 7);
  assert.ok(
    signals.work_records.every((item) => item.native_status === "checked"),
  );
  assert.ok(
    signals.next_actions.every(
      (action) =>
        !/Completed step/.test(action.text) && action.source_ref === source,
    ),
  );
});

test("goal acceptance needs current pinned canonical approval, never a title or unpinned approval flag", () => {
  const bp = { goal: "One preserved product", revision: 2 };
  const hash = digest(bp);
  const authority = {
    schema_version: "foundry-authority/1",
    items: [
      {
        id: "a1",
        actor: "user",
        decision: "approve",
        scope: "agent",
        subject_sha256: hash,
      },
    ],
  };
  const authorityHash = sha(JSON.stringify(authority));
  const state = {
    blueprint: { data: bp, sha256: hash },
    design_revision: 3,
    approval: {
      actor: "user",
      decision: "approve",
      status: "confirmed",
      scope: "agent",
      blueprint_revision: 2,
      design_revision: 3,
      blueprint_sha256: hash,
      canonical_authority: {
        path: "approval.json",
        sha256: authorityHash,
        record_id: "a1",
      },
    },
  };
  const docs = [
    { path: ".agent-foundry/state.json", data: state },
    { path: "approval.json", data: authority },
  ];
  const sources = [
    { path: docs[0].path, sha256: "s" },
    { path: "approval.json", sha256: authorityHash },
  ];
  assert.equal(projectSignals(docs, sources).goal.status, "accepted");
  state.approval.canonical_authority.sha256 = "changed";
  assert.equal(projectSignals(docs, sources).goal.status, "declared");
  state.approval.canonical_authority.sha256 = authorityHash;
  authority.items[0].decision = "revoke";
  assert.equal(projectSignals(docs, sources).goal.status, "declared");
});

test("source locators reject escapes and symlinked document folders are not traversed", async (t) => {
  const { root, home } = await fixture(t);
  const outside = join(home, "outside");
  await mkdir(outside);
  await writeFile(join(outside, "CHECKPOINT.md"), "## Goal\nDO-NOT-READ\n");
  await symlink(outside, join(root, "docs"));
  const view = await inspectProject(root);
  assert.ok(!JSON.stringify(view).includes("DO-NOT-READ"));
  await assert.rejects(
    () => inspectProject(root, { sourceRefs: ["../outside/CHECKPOINT.md"] }),
    (error) => error.code === "OUTSIDE_ROOT",
  );
});

test("routing distinguishes planned agents, actual discovered agents and unchanged authority", () => {
  const project = { id: "p", root: "/project" };
  const workspace = {
    project: { revision: "r" },
    sources: [],
    agents: [
      { name: "project-agent", availability: "planned", status: "declared" },
    ],
  };
  const payload = {
    objective: "Continue the accepted project",
    acceptance: ["Preserve requirements"],
  };
  let value = proposeRoute({
    project,
    workspace,
    skills: { entries: [] },
    payload,
  });
  assert.equal(value.route, null);
  assert.equal(value.preferred_project_agent, null);
  assert.equal(value.model_execution_observed, false);
  workspace.agents[0].availability = "installed";
  workspace.agents[0].source_ref = ".agents/skills/project-agent/SKILL.md";
  workspace.agents[0].source_sha256 = "a".repeat(64);
  value = proposeRoute({
    project,
    workspace,
    skills: {
      entries: [
        {
          name: "project-agent",
          path: "/project/.agents/skills/project-agent/SKILL.md",
          source_sha256: "a".repeat(64),
          discovery_status: "host_discovered",
          execution_supported: true,
          source_id: "host:a",
        },
      ],
    },
    payload,
  });
  assert.equal(value.route, "project_agent");
  assert.equal(value.execution_owner, "project-agent");
  const factory = proposeRoute({
    project,
    workspace,
    skills: { entries: [] },
    payload: { ...payload, route: "create_agent" },
  });
  assert.equal(factory.capability_gaps[0].code, "NATIVE_CONTROLLER_REQUIRED");
  assert.equal(
    factory.authority,
    "projection-only; no new rights or accepted product result",
  );
  assert.throws(
    () =>
      proposeRoute({
        project,
        workspace,
        skills: { entries: [] },
        payload: {
          ...payload,
          route: "maintain_system",
          maintenance: {
            target_kind: "orchestrator",
            target_refs: ["/other/skills"],
          },
        },
      }),
    (error) => error.code === "OUTSIDE_ROOT",
  );
});

test("project-agent routing binds exact source path and hash and never chooses the first duplicate origin", () => {
  const project = { id: "p", root: "/project" };
  const agent = {
    name: "project-agent",
    availability: "installed",
    status: "observed",
    source_ref: ".agents/skills/a/SKILL.md",
    source_sha256: "a".repeat(64),
  };
  const row = {
    name: agent.name,
    source_id: "host:a",
    source_path: "/project/.agents/skills/a/SKILL.md",
    source_sha256: agent.source_sha256,
    discovery_status: "host_discovered",
    execution_supported: true,
  };
  const workspace = {
    project: { revision: "r" },
    sources: [],
    agents: [agent],
  };
  const payload = { objective: "Continue current work" };
  const route = (entries) =>
    proposeRoute({ project, workspace, skills: { entries }, payload });
  assert.equal(
    route([{ ...row, source_path: "/project/.agents/skills/b/SKILL.md" }])
      .route,
    null,
  );
  assert.equal(route([{ ...row, source_sha256: "b".repeat(64) }]).route, null);
  assert.equal(route([{ ...row, enabled: false }]).route, null);
  assert.equal(
    route([{ ...row, source_path: "/project/.agents/skills/x/../a/SKILL.md" }])
      .route,
    "project_agent",
  );
  workspace.agents.push({
    ...agent,
    source_ref: ".agents/skills/b/SKILL.md",
    source_sha256: "b".repeat(64),
  });
  const value = route([
    row,
    {
      ...row,
      source_id: "host:b",
      source_path: "/project/.agents/skills/b/SKILL.md",
      source_sha256: "b".repeat(64),
    },
  ]);
  assert.equal(value.route, null);
  assert.equal(value.preferred_project_agent, null);
  assert.equal(value.project_agents.length, 2);
  assert.ok(
    value.project_agents.every(
      (entry) =>
        entry.discovery_status === "ambiguous" && !entry.execution_supported,
    ),
  );
  assert.equal(value.capability_gaps[0].code, "PROJECT_AGENT_AMBIGUOUS");
});

test("project-agent source projection reads initial frontmatter and retains every declared and installed origin", async (t) => {
  const { root } = await fixture(t);
  await mkdir(join(root, ".agent-foundry"));
  await writeFile(
    join(root, ".agent-foundry/state.json"),
    JSON.stringify({ project_agent: "project-agent" }),
  );
  for (const [folder, source] of Object.entries({
    a: "---\nname: project-agent\n---\n# Agent A\n",
    b: "---\nname: project-agent\n---\n# Agent B\n",
    body: "# Documentation\nname: body-only\n",
    example: "---\ndescription: Example\n---\nname: body-example\n",
  })) {
    await mkdir(join(root, ".agents/skills", folder), { recursive: true });
    await writeFile(join(root, ".agents/skills", folder, "SKILL.md"), source);
  }
  const view = await inspectProject(root);
  assert.equal(view.agents.length, 3);
  assert.equal(
    view.agents.filter((agent) => agent.availability === "planned").length,
    1,
  );
  const installed = view.agents.filter(
    (agent) => agent.availability === "installed",
  );
  assert.equal(installed.length, 2);
  assert.deepEqual(installed.map((agent) => agent.source_ref).sort(), [
    ".agents/skills/a/SKILL.md",
    ".agents/skills/b/SKILL.md",
  ]);
  assert.notEqual(installed[0].source_sha256, installed[1].source_sha256);
  assert.equal(
    view.sources.filter((source) => source.kind === "project-agent").length,
    2,
  );
  await writeFile(
    join(root, ".agents/skills/a/SKILL.md"),
    "---\nname: project-agent\n---\n# Changed source\n",
  );
  assert.notEqual((await inspectProject(root)).revision, view.revision);
});

test("public Codex discovery explicitly requests all kinds and state-db-only pages", async () => {
  const native = new CodexAdapter({ dataDir: "/unused" });
  const calls = [];
  native.connect = async () => {};
  native.rpc = async (method, params) => {
    calls.push({ method, params });
    return { data: [] };
  };
  await native.allThreads({ cursor: "opaque", archived: true });
  await native.historyTurns("thread", { cursor: "older" });
  await native.historyTurns("thread", { itemsView: "notLoaded" });
  await native.historyItems("thread", { cursor: "older-items", limit: 20 });
  assert.equal(calls[0].method, "thread/list");
  assert.equal(calls[0].params.useStateDbOnly, true);
  assert.ok(!Object.hasOwn(calls[0].params, "cwd"));
  assert.ok(calls[0].params.sourceKinds.includes("subAgent"));
  assert.equal(calls[0].params.archived, true);
  assert.equal(calls[1].params.itemsView, "full");
  assert.equal(calls[2].params.itemsView, "notLoaded");
  assert.equal(calls[3].method, "thread/items/list");
  assert.equal(calls[3].params.cursor, "older-items");
  assert.equal(calls[3].params.sortDirection, "desc");
  assert.equal(calls[3].params.limit, 20);
});

test("native-index history transport has a private read facade and rejects all mutating RPC admission", async (t) => {
  const { dataDir } = await fixture(t);
  const denied = new CodexAdapter({ dataDir, historyReadOnly: true });
  let writes = 0;
  denied.child = { stdin: { writable: true, write: () => writes++ } };
  for (const [method, params] of [
    ["thread/start", {}],
    ["thread/resume", {}],
    ["thread/fork", {}],
    ["thread/unarchive", {}],
    ["turn/start", {}],
    ["command/exec", {}],
    ["account/read", { refreshToken: true }],
    ["thread/list", {}],
    ["thread/read", { includeTurns: true }],
    ["thread/turns/list", { itemsView: "full", limit: 1000 }],
    ["thread/turns/list", { itemsView: "summary", limit: 10 }],
    [
      "thread/items/list",
      { threadId: "thread", sortDirection: "desc", limit: 1000 },
    ],
    [
      "thread/items/list",
      {
        threadId: "thread",
        sortDirection: "desc",
        limit: 10,
        cursor: { arbitrary: true },
      },
    ],
  ]) {
    assert.throws(
      () => denied.rpc(method, params),
      (error) => error.code === "SCOPE_MISMATCH",
    );
  }
  assert.throws(
    () => denied.notify("turn/start", {}),
    (error) => error.code === "SCOPE_MISMATCH",
  );
  assert.equal(writes, 0);
  const methods = [],
    argv = [];
  const executable = join(dataDir, "synthetic-codex");
  await writeFile(executable, "#!/bin/sh\nprintf '[]\\n'\n", { mode: 0o755 });
  const reader = new CodexHistoryAdapter({
    dataDir,
    executable,
    spawnProcess: (_exe, args) => {
      argv.push(...args);
      const child = new EventEmitter();
      child.stdout = new EventEmitter();
      child.stderr = new EventEmitter();
      child.exitCode = null;
      child.stdin = {
        writable: true,
        write(raw, callback) {
          const request = JSON.parse(raw);
          methods.push(request.method);
          if (request.id)
            queueMicrotask(() =>
              child.stdout.emit(
                "data",
                JSON.stringify({
                  id: request.id,
                  result:
                    request.method === "initialize"
                      ? { userAgent: "test", platformOs: "test" }
                      : request.method === "account/read"
                        ? { account: { type: "test" } }
                        : { data: [] },
                }) + "\n",
              ),
            );
          callback?.();
        },
        end() {
          child.exitCode = 0;
          queueMicrotask(() => child.emit("exit", 0));
        },
      };
      child.kill = () => {
        child.exitCode = 0;
        child.emit("exit", 0);
      };
      return child;
    },
  });
  assert.equal(reader.rpc, undefined);
  assert.equal(reader.start, undefined);
  assert.equal(reader.resume, undefined);
  assert.equal(reader.turn, undefined);
  await reader.allThreads({ limit: 1 });
  await reader.historyTurns("scoped-thread", { limit: 5 });
  await reader.historyItems("scoped-thread", { limit: 5 });
  await reader.close();
  assert.equal(
    argv.some((value) => value.startsWith("sqlite_home=")),
    false,
  );
  assert.ok(argv.some((value) => value.startsWith("log_dir=")));
  assert.deepEqual(methods, [
    "initialize",
    "initialized",
    "account/read",
    "thread/list",
    "thread/turns/list",
    "thread/items/list",
  ]);
});

async function itemHistoryFixture(
  t,
  historyItems,
  {
    turns = [
      { id: "turn", status: "completed", itemsView: "notLoaded", items: [] },
    ],
  } = {},
) {
  const { root, dataDir } = await fixture(t);
  await writeFile(join(root, "AGENTS.md"), "Original source instructions.");
  const calls = [];
  const native = {
    allThreads: async ({ archived }) => ({
      data: archived
        ? []
        : [
            {
              id: "large",
              cwd: root,
              name: "Metadata title",
              status: { type: "idle" },
            },
          ],
    }),
    readThread: async (id) => ({ thread: { id, cwd: root } }),
    historyTurns: async (_id, options) => {
      calls.push(["turns", options]);
      return { data: turns, nextCursor: null };
    },
    historyItems: async (id, options) => {
      calls.push(["items", options]);
      return historyItems(id, options);
    },
  };
  const manager = new PortfolioManager({
    store: store(),
    codex: native,
    dataDir,
  });
  const catalog = await manager.refresh();
  return {
    root,
    manager,
    id: catalog.projects[0].id,
    snapshot: catalog.checked_at,
    calls,
  };
}
const entry = (id, type, body = {}) => ({
  turnId: "turn",
  item: { id, type, ...body },
});

test("large history uses metadata and bounded actual item pages, shrinking an oversized page without increasing the transport cap", async (t) => {
  const f = await itemHistoryFixture(t, async (_id, { limit }) => {
    if (limit > 12)
      throw new ServiceError(
        "HOST_DISCONNECTED",
        "Protocol message exceeded limit",
        503,
      );
    return {
      data: [
        entry("answer", "agentMessage", { text: "Actual final answer" }),
        entry("command", "commandExecution", {
          exitCode: 0,
          status: "completed",
        }),
        entry("request", "userMessage", {
          content: [{ type: "text", text: "Actual owner objective" }],
        }),
      ],
      nextCursor: null,
    };
  });
  const result = await f.manager.project(f.id);
  assert.equal(f.calls[0][1].itemsView, "notLoaded");
  assert.deepEqual(
    f.calls
      .filter(([kind]) => kind === "items")
      .map(([, params]) => params.limit),
    [50, 25, 12],
  );
  assert.equal(result.coverage.complete, true);
  assert.equal(result.coverage.history_items_observed, 3);
  const work = result.work_groups.flatMap((group) => group.items)[0];
  assert.equal(work.objective, "Actual owner objective");
  assert.equal(work.objective_observed, true);
  assert.equal(work.outcome, "Actual final answer");
  assert.equal(work.response_item_id, "answer");
  assert.equal(work.evidence_refs[0].kind, "command_observation");
});

test("bounded item continuation retains exact cursor admission, newer answers and cumulative project coverage", async (t) => {
  const f = await itemHistoryFixture(t, async (_id, { cursor }) =>
    cursor === "b"
      ? {
          data: [
            entry("older-comment", "agentMessage", {
              text: "Older commentary",
            }),
            entry("request", "userMessage", {
              content: [{ type: "text", text: "The original owner objective" }],
            }),
          ],
          nextCursor: null,
        }
      : cursor === "a"
        ? {
            data: [entry("command", "commandExecution", { exitCode: 0 })],
            nextCursor: "b",
          }
        : {
            data: [
              entry("latest-answer", "agentMessage", {
                text: "Newest actual answer",
              }),
            ],
            nextCursor: "a",
          },
  );
  const first = await f.manager.project(f.id, { max_turn_pages: 1 });
  assert.equal(first.coverage.complete, false);
  assert.equal(first.coverage.non_item_page_complete, true);
  assert.equal(first.coverage.item_cursors[0].next_cursor, "b");
  await assert.rejects(
    f.manager.project(f.id, {
      item_thread_id: "large",
      item_cursor: "wrong",
      snapshot_checked_at: f.snapshot,
    }),
    (error) => error.code === "SOURCE_DRIFT",
  );
  const next = await f.manager.project(f.id, {
    item_thread_id: "large",
    item_cursor: "b",
    snapshot_checked_at: f.snapshot,
    max_turn_pages: 1,
  });
  assert.equal(next.coverage.item_continuation, true);
  assert.equal(next.coverage.item_cursors[0].next_cursor, null);
  assert.equal(next.coverage.item_cursors[0].items_complete, true);
  const observed = f.manager.observedPages.get(f.id).pages.get(0);
  const work = observed.work_groups.flatMap((group) => group.items)[0];
  assert.equal(work.outcome, "Newest actual answer");
  assert.equal(work.objective, "The original owner objective");
  assert.equal(work.status, "answer_received");
  assert.equal(observed.coverage.page_complete, true);
  assert.equal(f.manager.get().projects[0].history_status, "observed");
  await assert.rejects(
    f.manager.project(f.id, {
      item_thread_id: "large",
      item_cursor: "b",
      snapshot_checked_at: f.snapshot,
    }),
    (error) => error.code === "SOURCE_DRIFT",
  );
});

test("repeated item cursors, a single oversized item and empty answer text remain explicit coverage gaps", async (t) => {
  const repeated = await itemHistoryFixture(t, async () => ({
    data: [entry("answer", "agentMessage", { text: "Observed response" })],
    nextCursor: "same",
  }));
  const result = await repeated.manager.project(repeated.id);
  assert.equal(result.coverage.complete, false);
  assert.ok(result.warnings.some((row) => row.code === "HOST_PROTOCOL_ERROR"));
  assert.equal(result.coverage.item_cursors[0].next_cursor, null);
  const oversized = await itemHistoryFixture(t, async () => {
    throw new ServiceError(
      "HOST_DISCONNECTED",
      "Protocol message exceeded limit",
      503,
    );
  });
  const unread = await oversized.manager.project(oversized.id);
  assert.equal(unread.coverage.complete, false);
  assert.ok(
    unread.warnings.some((row) => row.code === "NATIVE_ITEM_TOO_LARGE"),
  );
  assert.ok(oversized.calls.length <= 8);
  const empty = await itemHistoryFixture(t, async () => ({
    data: [
      entry("answer", "agentMessage", { text: "  " }),
      entry("request", "userMessage", {
        content: [{ type: "text", text: "Actual request" }],
      }),
    ],
    nextCursor: null,
  }));
  const emptyResult = await empty.manager.project(empty.id);
  assert.equal(emptyResult.coverage.non_item_page_complete, false);
  assert.equal(
    emptyResult.work_groups.flatMap((group) => group.items)[0].status,
    "recorded",
  );
  assert.ok(
    emptyResult.warnings.some(
      (row) => row.code === "NATIVE_COMPLETED_WITHOUT_ANSWER",
    ),
  );
});

test("an item continuation cannot cross changed project source or a refreshed inventory", async (t) => {
  const f = await itemHistoryFixture(t, async (_id, { cursor }) => ({
    data: [entry(cursor ?? "first", "agentMessage", { text: "Observed" })],
    nextCursor: `${cursor ?? "start"}-next`,
  }));
  const first = await f.manager.project(f.id, { max_turn_pages: 1 });
  const cursor = first.coverage.item_cursors[0].next_cursor;
  const calls = f.calls.length;
  await writeFile(join(f.root, "AGENTS.md"), "Changed governing source.");
  await assert.rejects(
    f.manager.project(f.id, {
      item_thread_id: "large",
      item_cursor: cursor,
      snapshot_checked_at: f.snapshot,
    }),
    (error) => error.code === "SOURCE_DRIFT",
  );
  assert.equal(f.calls.length, calls);
  await f.manager.refresh();
  await assert.rejects(
    f.manager.project(f.id, {
      item_thread_id: "large",
      item_cursor: cursor,
      snapshot_checked_at: f.snapshot,
    }),
    (error) => error.code === "SOURCE_DRIFT",
  );
});

class LocalCodex extends EventEmitter {
  constructor() {
    super();
    this.status = { status: "connected" };
    this.lastSkills = [];
  }
  async close() {}
}
test("universal entry requires current actually discovered installed source, never a canonical-only declaration", async (t) => {
  const { root, dataDir } = await fixture(t);
  const app = new Application({
    dataDir,
    repoRoot: resolve(import.meta.dirname, "../../../.."),
    codex: new LocalCodex(),
  });
  t.after(() => app.close());
  app.skills.list = async () => ({
    entries: [
      {
        name: "atelier-orchestrator",
        managed_by: "optional",
        source_sha256: "current",
      },
    ],
  });
  await assert.rejects(
    () => app.universalSource(),
    (error) => error.code === "CAPABILITY_UNVERIFIED",
  );
  app.skills.hostSources.set("host:orchestrator", {
    name: "atelier-orchestrator",
    source_id: "host:orchestrator",
    enabled: true,
    execution_supported: true,
    discovery_status: "host_discovered",
    source_sha256: "old",
  });
  await assert.rejects(
    () => app.universalSource(),
    (error) => error.code === "SOURCE_DRIFT",
  );
  app.skills.hostSources.get("host:orchestrator").source_sha256 = "current";
  assert.equal(await app.universalSource(), "host:orchestrator");
});

test("unknown native controller blocks overlapping dispatch and service maintenance, and pending state survives restart as unknown", async (t) => {
  const { root, dataDir } = await fixture(t);
  const repoRoot = resolve(import.meta.dirname, "../../../..");
  const app = new Application({ dataDir, repoRoot, codex: new LocalCodex() });
  app.store.put("project", "p", { id: "p", root, revision: "r" });
  app.store.put("task", "t", {
    id: "t",
    project_id: "p",
    status: "prepared",
    capsule: {},
  });
  app.store.put("native-controller", "operation", {
    id: "operation",
    project_id: "p",
    root,
    status: "pending",
  });
  await assert.rejects(
    () => app.dispatch("p", { task_id: "t" }),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  let executed = false;
  await assert.rejects(
    () =>
      app.maintain("cleanup", async () => {
        executed = true;
      }),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  assert.equal(executed, false);
  assert.equal(app.doctor().status, "attention");
  await app.close();
  const resumed = new Application({
    dataDir,
    repoRoot,
    codex: new LocalCodex(),
  });
  t.after(() => resumed.close());
  assert.equal(
    resumed.store.get("native-controller", "operation").status,
    "outcome_unknown",
  );
  assert.equal(resumed.activeNativeControllers().length, 1);
});

test("unknown global optional update blocks dispatch, while independent receipt reconciliation can break a cross-unknown deadlock", async (t) => {
  const { dataDir, root } = await fixture(t);
  const repoRoot = resolve(import.meta.dirname, "../../../..");
  const app = new Application({ dataDir, repoRoot, codex: new LocalCodex() });
  app.store.put("optional-update", "optional", {
    id: "optional",
    name: "atelier-orchestrator",
    status: "pending",
  });
  await assert.rejects(
    () => app.dispatch("missing", { task_id: "missing" }),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  await assert.rejects(
    () => app.maintain("native-controller", async () => {}),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  assert.equal(
    await app.maintain(
      "optional-rollback",
      async () => "permitted-own-rollback",
    ),
    "permitted-own-rollback",
  );
  app.store.put("native-controller", "native", {
    id: "native",
    root,
    status: "outcome_unknown",
  });
  await assert.rejects(
    () => app.maintain("optional-rollback", async () => {}),
    (error) => error.code === "OUTCOME_UNKNOWN",
  );
  assert.equal(
    await app.maintain(
      "native-controller-reconcile",
      async () => "receipt-only-reconciliation",
    ),
    "receipt-only-reconciliation",
  );
  await app.close();
  const resumed = new Application({
    dataDir,
    repoRoot,
    codex: new LocalCodex(),
  });
  t.after(() => resumed.close());
  assert.equal(
    resumed.store.get("optional-update", "optional").status,
    "outcome_unknown",
  );
  assert.equal(resumed.activeOptionalUpdates().length, 1);
});
