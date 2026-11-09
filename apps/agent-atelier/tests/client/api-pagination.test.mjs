import test from "node:test";
import assert from "node:assert/strict";
import { api, mergePortfolioPage } from "../../client/src/api.ts";

function page(offset, count, total, { complete = true, warnings = [] } = {}) {
  const items = Array.from({ length: count }, (_, i) => ({
    id: `native-${offset + i}`,
    objective: `Observed work ${offset + i}`,
  }));
  return {
    project: { id: "project", source_revision: "source-pins" },
    threads: items.map((item) => ({ id: item.id })),
    work_groups: [
      { id: "results", items, count },
      {
        id: "recorded",
        items: [{ id: "source-row", objective: "Existing source-backed work" }],
        count: 1,
      },
    ],
    warnings,
    coverage: {
      snapshot_checked_at: "inventory-1",
      thread_offset: offset,
      next_thread_offset: offset + count < total ? offset + count : null,
      threads_total: total,
      threads_read: count,
      threads_attempted: count,
      turns_observed: count,
      turn_pages: count,
      empty_history_threads: warnings.length,
      page_complete: complete,
      discovery_complete: true,
      complete: false,
    },
  };
}

test("client reads all project pages, deduplicates source work and never counts a repeated page twice", () => {
  const first = page(0, 40, 79),
    next = page(40, 39, 79);
  let accumulated = mergePortfolioPage(null, first);
  assert.equal(accumulated.coverage.complete, false);
  accumulated = mergePortfolioPage(accumulated, next);
  assert.equal(accumulated.threads.length, 79);
  assert.equal(accumulated.coverage.items, 80);
  assert.equal(
    accumulated.work_groups.find((group) => group.id === "recorded").count,
    1,
  );
  assert.equal(accumulated.coverage.threads_read, 79);
  assert.equal(accumulated.coverage.next_thread_offset, null);
  assert.equal(accumulated.coverage.complete, true);
  const repeated = mergePortfolioPage(accumulated, next);
  assert.equal(repeated, accumulated);
  assert.equal(repeated.coverage.turn_pages, 79);
});

test("empty native histories and actual turn limits remain incomplete after loading the last project page", () => {
  const warnings = Array.from({ length: 16 }, (_, i) => ({
    code: "NATIVE_HISTORY_EMPTY",
    thread_id: `empty-${i}`,
  }));
  const first = page(0, 40, 42, { complete: false, warnings });
  const next = page(40, 2, 42);
  const accumulated = mergePortfolioPage(mergePortfolioPage(null, first), next);
  assert.equal(accumulated.coverage.complete, false);
  assert.equal(accumulated.coverage.truncated, true);
  assert.equal(accumulated.coverage.empty_history_threads, 16);
  assert.equal(accumulated.warnings.length, 16);
  assert.equal(accumulated.coverage.items, 43);
});

test("project, snapshot, source-revision and ordering drift cannot merge into another work map", () => {
  const first = mergePortfolioPage(null, page(0, 40, 80));
  const next = page(40, 40, 80);
  for (const changed of [
    { ...next, project: { ...next.project, id: "other-project" } },
    {
      ...next,
      project: { ...next.project, source_revision: "changed-source" },
    },
    {
      ...next,
      coverage: { ...next.coverage, snapshot_checked_at: "new-inventory" },
    },
    page(60, 20, 80),
  ])
    assert.throws(
      () => mergePortfolioPage(first, changed),
      (error) => error.code === "SOURCE_DRIFT",
    );
  assert.throws(
    () => mergePortfolioPage(null, next),
    (error) => error.code === "SOURCE_DRIFT",
  );
});

test("portfolio detail requests carry the bounded thread offset and inventory token", async (t) => {
  const original = globalThis.fetch;
  const paths = [];
  globalThis.fetch = async (path) => {
    paths.push(path);
    return new Response("{}", {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  t.after(() => {
    globalThis.fetch = original;
  });
  await api.portfolioProject("project/encoded", {
    thread_offset: 40,
    snapshot_checked_at: "2026-11-09T12:00:00.000Z",
  });
  const url = new URL(paths[0], "http://127.0.0.1");
  assert.equal(url.pathname, "/api/v1/portfolio/projects/project%2Fencoded");
  assert.equal(url.searchParams.get("thread_offset"), "40");
  assert.equal(
    url.searchParams.get("snapshot_checked_at"),
    "2026-11-09T12:00:00.000Z",
  );
});

function correlatedRows() {
  const sharedProof = { path: "result.txt", sha256: "shared-proof" };
  const native = (n) => ({
    id: `native-${n}`,
    thread_id: `thread-${n}`,
    turn_id: `turn-${n}`,
    source: "native-history",
    status: "answer_received",
    outcome: `Native answer ${n}`,
    owner_review: null,
    acceptance: "not_inferred",
    response_observed: true,
    execution_observed: false,
    evidence_refs: [
      { kind: "native-output", turn_id: `turn-${n}` },
      sharedProof,
    ],
    skills: [{ name: "specialist", status: "mentioned" }],
    warnings: [{ code: "NATIVE_PARTIAL", turn_id: `turn-${n}` }],
  });
  const service = {
    id: "job-0",
    job_id: "job-0",
    task_id: "task-0",
    thread_id: "thread-0",
    turn_id: "turn-0",
    source: "service",
    status: "completed",
    outcome: "Service output",
    owner_review: "accepted",
    acceptance: "owner-review",
    response_observed: false,
    execution_observed: true,
    evidence_refs: [
      { kind: "service-job", source_ref: "job:job-0" },
      { sha256: "shared-proof", path: "result.txt" },
    ],
    skills: [{ name: "specialist", status: "selected" }],
    warnings: [{ code: "SERVICE_NOTE" }],
  };
  const source = {
    id: "source-work",
    source: "native-project",
    objective: "Keep source work",
  };
  const unpaired = {
    id: "unpaired-job",
    source: "service",
    task_id: "unpaired-task",
    objective: "Keep unpaired work",
  };
  return { native, service, source, unpaired };
}

for (const order of ["service-first", "native-first"]) {
  test(`correlated native and service turns deduplicate across pages in ${order} order without losing review or evidence`, () => {
    const { native, service, source, unpaired } = correlatedRows();
    const first = page(0, 1, 2),
      next = page(1, 1, 2);
    const nativeGroup = { id: "results", items: [native(0)] };
    const serviceGroup = { id: "prepared", items: [service] };
    first.work_groups = [
      ...(order === "service-first"
        ? [serviceGroup, nativeGroup]
        : [nativeGroup, serviceGroup]),
      { id: "recorded", items: [source, unpaired] },
    ];
    next.work_groups = [
      { id: "prepared", items: [service] },
      { id: "results", items: [native(1)] },
      { id: "recorded", items: [source, unpaired] },
    ];
    let merged = mergePortfolioPage(mergePortfolioPage(null, first), next);
    const items = merged.work_groups.flatMap((group) => group.items);
    assert.equal(items.length, 4);
    assert.equal(
      items.filter((item) => item.thread_id && item.turn_id).length,
      2,
    );
    assert.equal(merged.coverage.items, 4);
    const turn = items.find((item) => item.thread_id === "thread-0");
    assert.equal(turn.id, "native-0");
    assert.equal(turn.source, "native-history");
    assert.equal(turn.status, "answer_received");
    assert.equal(turn.outcome, "Native answer 0");
    assert.equal(
      merged.work_groups.find((group) => group.items.includes(turn)).id,
      "results",
    );
    assert.equal(turn.job_id, "job-0");
    assert.equal(turn.service_job_id, "job-0");
    assert.equal(turn.task_id, "task-0");
    assert.equal(turn.owner_review, "accepted");
    assert.equal(turn.acceptance, "owner-review");
    assert.equal(turn.evidence_refs.length, 3);
    assert.equal(turn.skills.length, 2);
    assert.equal(turn.warnings.length, 2);
    assert.equal(turn.response_observed, true);
    assert.equal(turn.execution_observed, true);
    assert.ok(items.some((item) => item.id === "source-work"));
    assert.ok(items.some((item) => item.id === "unpaired-job"));
    const repeated = mergePortfolioPage(merged, next);
    assert.equal(repeated, merged);
    assert.equal(repeated.coverage.items, 4);
    assert.equal(repeated.coverage.turn_pages, 2);
  });
}

test("service-first history gains native identity while a later explicit nonaccepted review clears stale acceptance", () => {
  const { native, service } = correlatedRows();
  const first = page(0, 1, 2),
    next = page(1, 1, 2);
  first.work_groups = [{ id: "prepared", items: [service] }];
  next.work_groups = [
    { id: "results", items: [native(0), native(1)] },
    {
      id: "prepared",
      items: [
        {
          ...service,
          owner_review: "needs_changes",
          acceptance: "owner-review",
        },
      ],
    },
  ];
  const merged = mergePortfolioPage(mergePortfolioPage(null, first), next);
  const items = merged.work_groups.flatMap((group) => group.items);
  assert.equal(items.length, 2);
  const turn = items.find((item) => item.turn_id === "turn-0");
  assert.equal(turn.id, "native-0");
  assert.equal(turn.source, "native-history");
  assert.equal(turn.owner_review, "needs_changes");
  assert.equal(turn.acceptance, "not_inferred");
  assert.equal(turn.evidence_refs.length, 3);
  assert.equal(turn.response_observed, true);
  assert.equal(turn.execution_observed, true);
  assert.equal(
    merged.work_groups.find((group) => group.items.includes(turn)).id,
    "results",
  );
});

for (const order of ["service-first", "native-first"]) {
  test(`typed permission review keeps its system group and native provenance across ${order} paginated service collisions`, () => {
    const { native, service } = correlatedRows();
    const first = page(0, 1, 2),
      next = page(1, 1, 2);
    const sessionSource = { subAgent: { other: "guardian" } };
    const review = {
      ...native(0),
      work_type: "permission_review",
      native_session_source: sessionSource,
      native_thread_source: "guardian_review",
      parent_thread_id: "parent-thread",
    };
    const reviewGroup = { id: "system_checks", items: [review] };
    const serviceGroup = { id: "results", items: [service] };
    first.work_groups =
      order === "service-first"
        ? [serviceGroup, reviewGroup]
        : [reviewGroup, serviceGroup];
    const ordinary = {
      ...native(1),
      objective:
        "Guardian permission review is mentioned in an ordinary user task",
    };
    next.work_groups = [{ id: "results", items: [service, ordinary] }];
    const merged = mergePortfolioPage(mergePortfolioPage(null, first), next);
    assert.deepEqual(
      merged.work_groups.map((group) => group.id),
      ["results", "system_checks"],
    );
    const checks = merged.work_groups.find(
      (group) => group.id === "system_checks",
    );
    assert.equal(checks.count, 1);
    assert.equal(checks.items[0].id, "native-0");
    assert.equal(checks.items[0].work_type, "permission_review");
    assert.equal(checks.items[0].status, "answer_received");
    assert.equal(checks.items[0].response_observed, true);
    assert.deepEqual(checks.items[0].native_session_source, sessionSource);
    assert.equal(checks.items[0].native_thread_source, "guardian_review");
    assert.equal(checks.items[0].parent_thread_id, "parent-thread");
    assert.equal(checks.items[0].job_id, "job-0");
    assert.equal(checks.items[0].owner_review, "accepted");
    assert.equal(checks.items[0].acceptance, "owner-review");
    assert.equal(checks.items[0].evidence_refs.length, 3);
    assert.equal(
      merged.work_groups.find((group) => group.id === "results").items[0].id,
      ordinary.id,
    );
    assert.equal(merged.coverage.items, 2);
    assert.equal(mergePortfolioPage(merged, next), merged);
  });
}

test("a typed native review arriving after a raw service row moves that identity out of product results", () => {
  const { native, service } = correlatedRows();
  const first = page(0, 1, 2),
    next = page(1, 1, 2);
  first.work_groups = [{ id: "results", items: [service] }];
  next.work_groups = [
    {
      id: "results",
      items: [
        {
          ...native(0),
          work_type: "permission_review",
          native_thread_source: "guardian_review",
        },
        native(1),
      ],
    },
  ];
  const merged = mergePortfolioPage(mergePortfolioPage(null, first), next);
  assert.equal(
    merged.work_groups.find((group) => group.id === "system_checks").items[0]
      .id,
    "native-0",
  );
  assert.equal(
    merged.work_groups.find((group) => group.id === "results").count,
    1,
  );
  assert.equal(merged.coverage.items, 2);
});
