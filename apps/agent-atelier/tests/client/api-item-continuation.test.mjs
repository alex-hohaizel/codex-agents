import test from "node:test";
import assert from "node:assert/strict";
import { api, mergePortfolioPage } from "../../client/src/api.ts";

function turn(thread, overrides = {}) {
  return {
    id: `${thread}-turn`,
    thread_id: thread,
    turn_id: `${thread}-turn`,
    source: "native-history",
    native_status: "completed",
    status: "answer_received",
    objective: `Original ${thread} request`,
    objective_observed: true,
    outcome: `Newest ${thread} answer`,
    response_observed: true,
    response_item_id: `${thread}-final`,
    acceptance: "not_inferred",
    owner_review: null,
    evidence_refs: [{ kind: "native-output", id: `${thread}-final` }],
    skills: [{ name: "existing-specialist", status: "mentioned" }],
    warnings: [],
    ...overrides,
  };
}
function outer(offset, { pending = false, nonItemComplete = true } = {}) {
  const thread = offset === 0 ? "thread-a" : "thread-b";
  return {
    project: { id: "project", source_revision: "source-pins" },
    threads: [{ id: thread, title: `Chat ${thread}` }],
    work_groups: [{ id: "results", items: [turn(thread)] }],
    warnings: pending
      ? [{ code: "NATIVE_ITEM_PAGE_LIMIT", thread_id: thread }]
      : [],
    coverage: {
      snapshot_checked_at: "snapshot-1",
      thread_offset: offset,
      next_thread_offset: offset === 0 ? 1 : null,
      discovery_complete: true,
      page_complete: !pending && nonItemComplete,
      non_item_page_complete: nonItemComplete,
      threads_total: 2,
      threads_read: 1,
      threads_attempted: 1,
      turns_observed: 1,
      turn_pages: 1,
      item_pages: pending ? 2 : 1,
      history_items_observed: pending ? 100 : 10,
      item_cursors: [
        {
          thread_id: thread,
          next_cursor: pending ? "a:next" : null,
          pages: pending ? 2 : 1,
          items_observed: pending ? 100 : 10,
          items_complete: !pending,
          thread_offset: offset,
        },
      ],
    },
  };
}
function continuation({ complete = true, nonItemComplete = true } = {}) {
  return {
    project: { id: "project", source_revision: "source-pins" },
    threads: [{ id: "thread-a", title: "Chat thread-a" }],
    work_groups: [
      {
        id: "recorded",
        items: [
          turn("thread-a", {
            objective: "Older user fragment",
            objective_observed: true,
            outcome: "Older commentary",
            response_observed: false,
            response_item_id: null,
            status: "recorded",
            history_item_continuation: true,
            evidence_refs: [{ kind: "native-input", id: "a-original" }],
            skills: [{ name: "earlier-specialist", status: "mentioned" }],
          }),
        ],
      },
    ],
    warnings: complete
      ? []
      : [{ code: "NATIVE_ITEM_PAGE_LIMIT", thread_id: "thread-a" }],
    coverage: {
      item_continuation: true,
      item_thread_id: "thread-a",
      consumed_item_cursor: "a:next",
      snapshot_checked_at: "snapshot-1",
      thread_offset: 0,
      next_thread_offset: 1,
      discovery_complete: true,
      non_item_page_complete: nonItemComplete,
      page_complete: complete && nonItemComplete,
      threads_total: 2,
      threads_read: 1,
      threads_attempted: 1,
      turns_observed: 1,
      turn_pages: 1,
      item_pages: 1,
      history_items_observed: 25,
      item_cursors: [
        {
          thread_id: "thread-a",
          next_cursor: complete ? null : "a:last",
          pages: 1,
          items_observed: 25,
          items_complete: complete,
          thread_offset: 0,
        },
      ],
    },
  };
}
const work = (page) => page.work_groups.flatMap((group) => group.items);

test("offset-zero item continuation preserves other loaded pages, newer response, original objective and outer pagination", () => {
  const first = mergePortfolioPage(null, outer(0, { pending: true }));
  const previous = mergePortfolioPage(first, outer(1));
  assert.equal(previous.coverage.complete, false);
  const page = continuation();
  const merged = mergePortfolioPage(previous, page);
  assert.equal(merged.threads.length, 2);
  assert.equal(work(merged).length, 2);
  const row = work(merged).find((item) => item.thread_id === "thread-a");
  assert.equal(row.objective, "Original thread-a request");
  assert.equal(row.outcome, "Newest thread-a answer");
  assert.equal(row.response_item_id, "thread-a-final");
  assert.equal(row.status, "answer_received");
  assert.equal(
    merged.work_groups.find((group) => group.items.includes(row)).id,
    "results",
  );
  assert.equal(row.evidence_refs.length, 2);
  assert.equal(row.skills.length, 2);
  assert.equal(merged.coverage.next_thread_offset, null);
  assert.deepEqual(merged.coverage.loaded_thread_offsets, [0, 1]);
  assert.equal(merged.coverage.latest_thread_offset, 1);
  assert.equal(merged.coverage.threads_read, 2);
  assert.equal(merged.coverage.turns_observed, 2);
  assert.equal(merged.coverage.item_pages, 4);
  assert.equal(merged.coverage.history_items_observed, 135);
  assert.equal(
    merged.coverage.item_cursors.find((item) => item.thread_id === "thread-a")
      .pages,
    3,
  );
  assert.equal(merged.coverage.complete, true);
  assert.equal(
    merged.warnings.some((item) => item.code === "NATIVE_ITEM_PAGE_LIMIT"),
    false,
  );
  assert.equal(mergePortfolioPage(merged, page), merged);
});

test("remaining cursors and unrelated missing-history gaps cannot become a dummy complete result", () => {
  let previous = mergePortfolioPage(null, outer(0, { pending: true }));
  previous = mergePortfolioPage(previous, outer(1, { nonItemComplete: false }));
  previous.warnings.push({
    code: "NATIVE_HISTORY_EMPTY",
    thread_id: "thread-b",
  });
  const merged = mergePortfolioPage(previous, continuation());
  assert.equal(merged.coverage.complete, false);
  assert.equal(merged.coverage.truncated, true);
  assert.ok(
    merged.warnings.some((item) => item.code === "NATIVE_HISTORY_EMPTY"),
  );
  const stillPending = mergePortfolioPage(
    mergePortfolioPage(null, outer(0, { pending: true })),
    continuation({ complete: false }),
  );
  assert.equal(stillPending.coverage.complete, false);
  assert.equal(stillPending.coverage.item_cursors[0].next_cursor, "a:last");
});

test("item continuation requires the exact observed source/snapshot/thread/cursor and a loaded outer page", () => {
  const previous = mergePortfolioPage(null, outer(0, { pending: true }));
  assert.throws(
    () => mergePortfolioPage(null, continuation()),
    (e) => e.code === "SOURCE_DRIFT",
  );
  for (const change of [
    { item_thread_id: "other-thread" },
    { consumed_item_cursor: "invented" },
    { snapshot_checked_at: "stale-snapshot" },
    { thread_offset: 99 },
  ]) {
    const page = continuation();
    page.coverage = { ...page.coverage, ...change };
    assert.throws(
      () => mergePortfolioPage(previous, page),
      (e) => e.code === "SOURCE_DRIFT",
    );
  }
  const source = continuation();
  source.project.source_revision = "changed-source";
  assert.throws(
    () => mergePortfolioPage(previous, source),
    (e) => e.code === "SOURCE_DRIFT",
  );
});

test("an older slice can fill an unobserved objective/response without losing another turn", () => {
  const initial = outer(0, { pending: true });
  initial.work_groups = [
    {
      id: "recorded",
      items: [
        turn("thread-a", {
          objective: "Native turn",
          objective_observed: false,
          outcome: "",
          response_observed: false,
          response_item_id: null,
          status: "recorded",
        }),
      ],
    },
  ];
  const page = continuation();
  page.work_groups[0].items[0] = turn("thread-a", {
    history_item_continuation: true,
  });
  const merged = mergePortfolioPage(mergePortfolioPage(null, initial), page);
  assert.equal(work(merged)[0].objective, "Original thread-a request");
  assert.equal(work(merged)[0].outcome, "Newest thread-a answer");
  assert.equal(work(merged)[0].status, "answer_received");
});

test("typed system-check provenance and explicit owner-review changes survive item slices", () => {
  const initial = outer(0, { pending: true });
  initial.work_groups = [
    {
      id: "system_checks",
      items: [
        turn("thread-a", {
          work_type: "permission_review",
          native_thread_source: "guardian_review",
          owner_review: "accepted",
          acceptance: "owner-review",
        }),
      ],
    },
  ];
  const page = continuation();
  page.work_groups = [
    {
      id: "system_checks",
      items: [
        turn("thread-a", {
          work_type: "permission_review",
          native_thread_source: "guardian_review",
          history_item_continuation: true,
          owner_review: "needs_changes",
          acceptance: "not_inferred",
        }),
      ],
    },
  ];
  const merged = mergePortfolioPage(mergePortfolioPage(null, initial), page);
  assert.equal(merged.work_groups[0].id, "system_checks");
  assert.equal(work(merged)[0].native_thread_source, "guardian_review");
  assert.equal(work(merged)[0].owner_review, "needs_changes");
  assert.equal(work(merged)[0].acceptance, "not_inferred");
});

test("API item-cursor requests preserve opaque values and the native inventory token", async (t) => {
  const old = globalThis.fetch;
  let requested;
  globalThis.fetch = async (path) => {
    requested = path;
    return new Response("{}", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  t.after(() => {
    globalThis.fetch = old;
  });
  await api.portfolioProject("project/a", {
    item_thread_id: "thread/a",
    item_cursor: "opaque:?& value",
    snapshot_checked_at: "snapshot-1",
  });
  const url = new URL(requested, "http://127.0.0.1");
  assert.equal(url.pathname, "/api/v1/portfolio/projects/project%2Fa");
  assert.equal(url.searchParams.get("item_thread_id"), "thread/a");
  assert.equal(url.searchParams.get("item_cursor"), "opaque:?& value");
  assert.equal(url.searchParams.get("snapshot_checked_at"), "snapshot-1");
});
