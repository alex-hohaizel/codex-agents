import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  contextCoverage,
  contextTrail,
  observedJobCounts,
  requirementPresentation,
  workspaceReadState,
  recoveredWorkspaceError,
  workspaceDirection,
  operatorWorkspace,
  operatorSummary,
  workResultSources,
} from "../../client/src/workbench.ts";

test("the exact verified checkpoint next action wins over unrelated parsed Markdown next sections", () => {
  const checkpoint = {
    next: "Review this design",
    status: "declared",
    source_ref: "checkpoint.json",
    source_sha256: "sha",
  };
  const model = operatorWorkspace(
    {
      project: { id: "p" },
      current_checkpoint: checkpoint,
      next_actions: [{ text: "Old report closing paragraph" }],
    },
    "p",
  );
  assert.deepEqual(model.next, [
    {
      text: checkpoint.next,
      status: "declared",
      source_ref: "checkpoint.json",
      source_sha256: "sha",
    },
  ]);
  assert.equal(checkpoint.next, "Review this design");
});

test("paged native-project copies cannot replace the fresh declared source work map", () => {
  const sourceWork = [
    {
      id: "design",
      objective: "Rework design",
      status: "recorded",
      native_status: "in_progress",
      source_ref: "current.json",
      source_sha256: "fresh",
    },
    ...[1, 2, 3, 4].map((n) => ({
      id: `done-${n}`,
      objective: `Observed bounded task ${n}`,
      status: "recorded",
      native_status: "completed",
      source_ref: "current.json",
      source_sha256: "fresh",
    })),
  ];
  const current = {
    project: { id: "p", root: "/fixture" },
    work_records: sourceWork,
  };
  const history = {
    project: { root: "/fixture" },
    work_groups: [
      {
        id: "recorded",
        items: sourceWork.map((item) => ({
          ...item,
          source: "native-project",
          source_sha256: "older",
        })),
      },
    ],
  };
  const model = operatorWorkspace(current, "p", history);
  assert.equal(model.current.title, "Rework design");
  assert.equal(model.results.length, 4);
  assert.equal(
    model.work.filter((item) => item.source === "native-record").length,
    5,
  );
  assert.equal(model.current.record.source_sha256, "fresh");
  assert.equal(model.current.status, "recorded");
});

test("renaming a source objective keeps native identity and cannot resurrect its older in-progress record", () => {
  const source = "docs/project/current.json";
  const current = {
    project: { id: "p", root: "/fixture" },
    sources: [{ path: source, sha256: "new-pin" }],
    work_records: [
      {
        id: "generated-new-title",
        native_id: "operator-design-rework",
        objective: "Refine the accepted visual foundation",
        status: "recorded",
        native_status: "completed",
        source_ref: source,
        source_sha256: "new-pin",
      },
    ],
  };
  const detail = {
    project: { root: "/fixture" },
    work_groups: [
      {
        id: "recorded",
        items: [
          {
            id: "generated-old-title",
            native_id: "operator-design-rework",
            objective: "Rework the operational panel",
            status: "recorded",
            native_status: "in_progress",
            source: "native-project",
            source_ref: source,
            source_sha256: "old-pin",
          },
        ],
      },
    ],
  };
  const before = JSON.stringify({ current, detail });
  const model = operatorWorkspace(current, "p", detail);
  assert.equal(model.work.length, 1);
  assert.equal(model.current, null);
  assert.equal(model.results[0].title, current.work_records[0].objective);
  assert.equal(model.results[0].record.source_sha256, "new-pin");
  assert.equal(
    model.results[0].record.history_observations[0].id,
    "generated-old-title",
  );
  assert.equal(
    model.results[0].record.history_observations[0].objective,
    "Rework the operational panel",
  );
  assert.equal(JSON.stringify({ current, detail }), before);
  const nextRename = {
    ...current,
    work_records: [
      {
        ...current.work_records[0],
        id: "generated-third-title",
        objective: "Another current presentation",
      },
    ],
  };
  assert.equal(operatorWorkspace(nextRename, "p").work[0].id, model.work[0].id);
});

test("removed source records from an older source pin are quarantined while native history remains visible", () => {
  const source = "docs/project/current.json";
  const current = {
    project: { id: "p", root: "/fixture" },
    sources: [{ path: source, sha256: "new-pin" }],
    work_records: [
      {
        id: "current-id",
        native_id: "retained",
        objective: "Completed current work",
        status: "recorded",
        native_status: "completed",
        source_ref: source,
        source_sha256: "new-pin",
      },
    ],
  };
  const stale = {
    id: "current-id",
    native_id: "removed",
    objective: "Removed old source task",
    status: "recorded",
    native_status: "in_progress",
    source: "native-project",
    source_ref: source,
    source_sha256: "old-pin",
    outcome: "Original historical source trail",
  };
  const turn = {
    id: "current-id",
    thread_id: "thread",
    turn_id: "turn",
    objective: "A separate native turn",
    status: "running",
    source: "native-history",
    source_ref: source,
    source_sha256: "old-pin",
  };
  const model = operatorWorkspace(current, "p", {
    project: { root: "/fixture" },
    work_groups: [
      { id: "recorded", items: [stale] },
      { id: "active", items: [turn] },
    ],
  });
  assert.equal(model.work.length, 2);
  assert.equal(model.results.length, 1);
  assert.equal(model.current.title, turn.objective);
  assert.equal(model.current.source, "native-history");
  assert.equal(model.sourceHistory.length, 1);
  assert.equal(model.sourceHistory[0].reason, "source-revision-changed");
  assert.equal(model.sourceHistory[0].record.outcome, stale.outcome);
  assert.equal(model.sourceHistory[0].current_source_sha256, "new-pin");
});

test("source native IDs and generated IDs are namespaced by their exact source path", () => {
  const a = {
    id: "same-id",
    native_id: "same-native-id",
    objective: "Source A complete",
    status: "recorded",
    native_status: "completed",
    source_ref: "docs/a.json",
    source_sha256: "a-pin",
  };
  const b = {
    ...a,
    objective: "Source B current",
    native_status: "in_progress",
    source: "native-project",
    source_ref: "docs/b.json",
    source_sha256: "b-pin",
  };
  const model = operatorWorkspace(
    {
      project: { id: "p", root: "/fixture" },
      sources: [
        { path: "docs/a.json", sha256: "a-pin" },
        { path: "docs/b.json", sha256: "b-pin" },
      ],
      work_records: [a],
    },
    "p",
    {
      project: { root: "/fixture" },
      work_groups: [{ id: "recorded", items: [b] }],
    },
  );
  assert.equal(model.work.length, 2);
  assert.equal(model.results.length, 1);
  assert.equal(model.current.title, b.objective);
  assert.notEqual(model.work[0].id, model.work[1].id);
});

test("a source missing from the fresh observed inventory remains historical rather than a current task", () => {
  const stale = {
    id: "old",
    native_id: "removed",
    source: "native-project",
    source_ref: "docs/no-longer-observed.json",
    source_sha256: "old-pin",
    objective: "Unobserved source work",
    status: "recorded",
    native_status: "in_progress",
  };
  const model = operatorWorkspace(
    { project: { id: "p", root: "/fixture" }, sources: [], work_records: [] },
    "p",
    {
      project: { root: "/fixture" },
      work_groups: [{ id: "recorded", items: [stale] }],
    },
  );
  assert.equal(model.current, null);
  assert.equal(model.work.length, 0);
  assert.equal(model.sourceHistory[0].reason, "source-not-current");
  assert.equal(model.sourceHistory[0].record.source_ref, stale.source_ref);
});

test("fresh terminal service observations win over stale native running while gaining missing output and evidence", () => {
  const current = {
    project: { id: "p", root: "/fixture" },
    jobs: [
      {
        id: "job",
        thread_id: "thread",
        turn_id: "turn",
        status: "completed",
        objective: "Finished check",
        evidence_refs: [{ path: "fresh-proof" }],
      },
    ],
  };
  const detail = {
    project: { root: "/fixture" },
    work_groups: [
      {
        id: "active",
        items: [
          {
            id: "native-turn",
            job_id: "job",
            thread_id: "thread",
            turn_id: "turn",
            status: "running",
            objective: "Old title",
            outcome: "Observed response",
            evidence_refs: [{ path: "native-proof" }],
          },
        ],
      },
    ],
  };
  const model = operatorWorkspace(current, "p", detail);
  assert.equal(model.current, null);
  assert.equal(model.results.length, 1);
  assert.equal(model.results[0].title, "Finished check");
  assert.equal(model.results[0].status, "completed");
  assert.equal(model.results[0].record.outcome, "Observed response");
  assert.deepEqual(model.results[0].record.evidence_refs, [
    { path: "fresh-proof" },
    { path: "native-proof" },
  ]);
  assert.equal(model.results[0].record.acceptance, undefined);
});

test("all 29 obligations retain the two explicit owner musts with no invented stage", () => {
  const requirements = [
    ...Array.from({ length: 27 }, (_, i) => ({
      id: `R${i + 1}`,
      stages: ["S1"],
    })),
    { id: "CURRENT-OWNER-REQUEST" },
    { id: "CURRENT-REVIEW-SELECTION" },
  ];
  const model = operatorWorkspace({ project: { id: "p" }, requirements }, "p");
  assert.equal(model.requirements.length, 29);
  assert.equal(model.stages[0].requirements.length, 27);
  assert.deepEqual(
    model.unstagedRequirements.map((item) => item.id),
    ["CURRENT-OWNER-REQUEST", "CURRENT-REVIEW-SELECTION"],
  );
  assert.equal(
    model.unstagedRequirements.every((item) => item.stages === undefined),
    true,
  );
  assert.equal(model.nativeRead, false);
});

test("a correlated typed permission review is removed from the product map without changing its stored job", () => {
  const job = {
    id: "job",
    thread_id: "thread",
    turn_id: "turn",
    status: "completed",
    objective: "Native review",
  };
  const model = operatorWorkspace(
    { project: { id: "p", root: "/fixture" }, jobs: [job] },
    "p",
    {
      project: { root: "/fixture" },
      work_groups: [
        {
          id: "system_checks",
          items: [
            {
              id: "review",
              thread_id: "thread",
              turn_id: "turn",
              work_type: "permission_review",
              status: "completed",
            },
          ],
        },
      ],
    },
  );
  assert.equal(model.work.length, 0);
  assert.equal(job.status, "completed");
});

test("stale approval, permissions and unknown future state never enter an authoritative fresh service record", () => {
  for (const review of [
    { review_status: "rework" },
    { review_status: null },
    {},
  ]) {
    const job = {
      id: "job",
      thread_id: "thread",
      turn_id: "turn",
      status: "completed",
      objective: "Current result",
      ...review,
    };
    const model = operatorWorkspace(
      { project: { id: "p", root: "/fixture" }, jobs: [job] },
      "p",
      {
        project: { root: "/fixture" },
        work_groups: [
          {
            id: "results",
            items: [
              {
                id: "native",
                thread_id: "thread",
                turn_id: "turn",
                source: "native-history",
                status: "running",
                owner_review: "accepted",
                acceptance: "owner-review",
                permission_scope: "expanded",
                future_acceptance: true,
                outcome: "Transcript response",
                evidence_refs: [{ path: "actual-proof" }],
              },
            ],
          },
        ],
      },
    );
    const actual = model.results[0].record;
    assert.equal(model.current, null);
    assert.equal(actual.review_status, job.review_status);
    assert.equal(actual.owner_review, undefined);
    assert.equal(actual.acceptance, undefined);
    assert.equal(actual.permission_scope, undefined);
    assert.equal(actual.future_acceptance, undefined);
    assert.equal(actual.outcome, "Transcript response");
    assert.equal(actual.history_observations[0].owner_review, "accepted");
    assert.deepEqual(actual.evidence_refs, [{ path: "actual-proof" }]);
  }
});

test("all loaded source work remains selectable even beyond the collapsed four-item lane", () => {
  const records = Array.from({ length: 7 }, (_, i) => ({
    id: `result-${i}`,
    objective: `Source result ${i}`,
    status: "recorded",
    native_status: "completed",
  }));
  const model = operatorWorkspace(
    { project: { id: "p", root: "/fixture" }, work_records: records },
    "p",
    null,
  );
  assert.equal(model.results.length, 7);
  assert.deepEqual(
    model.work.map((item) => item.record.id),
    records.map((item) => item.id),
  );
  assert.equal(model.nativeRead, false);
});

test("a gated service run remains active without implying acceptance", () => {
  const model = operatorWorkspace(
    {
      project: { id: "p" },
      jobs: [{ id: "g", objective: "Check current scope", status: "gating" }],
    },
    "p",
  );
  assert.equal(model.current.status, "gating");
  assert.equal(observedJobCounts([{ status: "gating" }]).active, 1);
  assert.equal(model.current.record.acceptance, undefined);
});

test("operator summaries keep raw locators in the original and offer only bounded relative report reads", () => {
  const record = {
    outcome:
      "A useful completed source analysis. Джерело: reports/study/NEEDS-REPORT.uk.md",
    evidence_refs: [
      { path: "reports/../secret.md" },
      { path: "/Users/private.md" },
      { path: "docs/proof.txt" },
      { path: "reports/study/NEEDS-REPORT.uk.md" },
    ],
  };
  const before = JSON.stringify(record);
  assert.equal(
    operatorSummary(record.outcome),
    "A useful completed source analysis.",
  );
  assert.deepEqual(workResultSources(record), [
    "docs/proof.txt",
    "reports/study/NEEDS-REPORT.uk.md",
  ]);
  assert.equal(JSON.stringify(record), before);
  assert.equal(
    operatorSummary(
      "A long source sentence that should remain available in the unmodified record",
      25,
    ).endsWith("…"),
    true,
  );
});

test("operator current work never resurrects a dispatched task whose linked job completed", () => {
  const workspace = {
    project: { id: "p", root: "/fixture" },
    jobs: [
      { id: "j", task_id: "t", status: "completed", objective: "Prior check" },
    ],
    tasks: [{ id: "t", status: "dispatched", objective: "Prior check" }],
  };
  const model = operatorWorkspace(workspace, "p");
  assert.equal(model.current, null);
  assert.equal(model.work.length, 1);
  assert.equal(model.results.length, 1);
  assert.equal(model.results[0].record.owner_review, undefined);
});

test("an owned prepared or paused task without a job stays one service record after the normal portfolio projection", () => {
  for (const status of ["prepared", "paused"]) {
    const task = {
      id: "task-prepared",
      project_id: "p",
      status,
      objective: "Saved bounded task",
    };
    const current = {
      project: { id: "p", root: "/fixture" },
      tasks: [task],
      jobs: [],
    };
    // Exact no-job shape emitted by Portfolio.#serviceWork.
    const projected = {
      id: task.id,
      task_id: task.id,
      job_id: null,
      thread_id: null,
      turn_id: null,
      objective: task.objective,
      outcome: "",
      status,
      native_status: status,
      source: "service",
      source_ref: `task:${task.id}`,
      evidence_refs: [],
      skills: [],
      owner_review: null,
      acceptance: "not_inferred",
      response_observed: false,
      execution_observed: false,
    };
    const before = JSON.stringify({ current, projected });
    const model = operatorWorkspace(current, "p", {
      project: { root: "/fixture" },
      work_groups: [{ id: "prepared", items: [projected] }],
    });
    assert.equal(model.work.length, 1);
    assert.equal(model.work[0].source, "service");
    assert.equal(model.work[0].record.id, task.id);
    assert.equal(model.work[0].status, status);
    assert.equal(model.work[0].title, task.objective);
    assert.equal(model.current, null);
    assert.equal(model.results.length, 0);
    assert.equal(model.sourceHistory.length, 0);
    assert.equal(model.work[0].record.acceptance, undefined);
    assert.equal(JSON.stringify({ current, projected }), before);
  }
});

test("declared work status groups a source record without turning it into host execution or acceptance", () => {
  const record = {
    id: "design",
    objective: "Owner design rework",
    status: "recorded",
    native_status: "in_progress",
    source_ref: "current.json",
    source_sha256: "pin",
  };
  const workspace = {
    project: { id: "p", root: "/fixture" },
    work_records: [record],
    jobs: [],
    tasks: [],
  };
  const model = operatorWorkspace(workspace, "p");
  assert.equal(model.current.title, record.objective);
  assert.equal(model.current.status, "recorded");
  assert.equal(model.current.source, "native-record");
  assert.equal(model.current.record.source_sha256, "pin");
  assert.equal(model.current.record.execution_observed, undefined);
  assert.equal(model.current.record.acceptance, undefined);
  assert.deepEqual(record, workspace.work_records[0]);
});

test("operator graph uses declared stage memberships and known dependencies only; ignores other projects", () => {
  const workspace = {
    project: { id: "p", root: "/fixture" },
    requirements: [
      { id: "R1", stages: ["S3", "S1"], dependencies: ["R2", "MISSING"] },
      { id: "R2", stages: ["S1"] },
    ],
    current_checkpoint: { phase: "Declared phase", status: "declared" },
  };
  const before = JSON.stringify(workspace);
  const model = operatorWorkspace(workspace, "p", {
    project: { root: "/other" },
    work_groups: [
      { id: "active", items: [{ id: "foreign", status: "running" }] },
    ],
  });
  assert.deepEqual(
    model.stages.map((s) => s.id),
    ["S1", "S3"],
  );
  assert.deepEqual(model.dependencies, [{ from: "R2", to: "R1" }]);
  assert.equal(model.current, null);
  assert.equal(model.nativeRead, false);
  assert.equal(model.checkpoint.status, "declared");
  assert.equal(operatorWorkspace(workspace, "another").checkpoint, null);
  assert.equal(operatorWorkspace(workspace, "another").work.length, 0);
  assert.equal(JSON.stringify(workspace), before);
});

test("permission review remains out of the operator product map and completed answers stay unaccepted", () => {
  const workspace = { project: { id: "p", root: "/fixture" } };
  const model = operatorWorkspace(workspace, "p", {
    project: { root: "/fixture" },
    work_groups: [
      {
        id: "system_checks",
        items: [
          { id: "guard", status: "completed", work_type: "permission_review" },
        ],
      },
      {
        id: "results",
        items: [
          {
            id: "answer",
            status: "answer_received",
            response_observed: true,
            outcome: "An answer",
          },
        ],
      },
    ],
  });
  assert.equal(model.work.length, 1);
  assert.equal(model.results[0].status, "answer_received");
  assert.equal(model.results[0].record.acceptance, undefined);
});

test("current workspace direction retains the current declared goal and next action without upgrading its approval", () => {
  const goal = {
    text: "Current owner scope",
    status: "declared",
    source_ref: "current.json",
  };
  const next = [{ text: "Repair and retest the current blocker" }];
  const agents = [{ name: "current-specialist", availability: "installed" }];
  const current = {
    project: { id: "project-a" },
    goal,
    next_actions: next,
    agents,
  };
  assert.deepEqual(workspaceDirection(current, "project-a"), {
    goal,
    next,
    agents,
  });
  assert.equal(
    workspaceDirection(current, "project-a").goal.status,
    "declared",
  );
  assert.equal(
    workspaceDirection(
      { ...current, goal: { text: "", status: "unknown" }, next_actions: [] },
      "project-a",
    ).goal.status,
    "unknown",
  );
  assert.deepEqual(
    workspaceDirection({ ...current, next_actions: [] }, "project-a").next,
    [],
  );
});

test("missing or wrong-project workspace direction never fills the goal from another project", () => {
  const current = {
    project: { id: "project-a" },
    goal: { text: "Old accepted goal", status: "accepted" },
    next_actions: [{ text: "Old next action" }],
  };
  for (const value of [
    workspaceDirection(null, "project-a"),
    workspaceDirection(current, "project-b"),
    workspaceDirection(current, undefined),
  ])
    assert.deepEqual(value, { goal: undefined, next: [], agents: [] });
});

test("successful workspace recovery clears only that matching read error and preserves unrelated action failures", () => {
  const readError = new Error("REQUEST_FAILED");
  const failure = { projectId: "project-a", error: readError };
  assert.equal(recoveredWorkspaceError(readError, failure, "project-a"), null);
  assert.equal(
    recoveredWorkspaceError(readError, failure, "project-b"),
    readError,
  );
  const jobErrorWithSameMessage = new Error("REQUEST_FAILED");
  assert.equal(
    recoveredWorkspaceError(jobErrorWithSameMessage, failure, "project-a"),
    jobErrorWithSameMessage,
  );
  assert.equal(
    recoveredWorkspaceError(readError, null, "project-a"),
    readError,
  );
  assert.equal(recoveredWorkspaceError(null, failure, "project-a"), null);
});

test("all 27 actual request-register rows show their native meaning and status in both supported source languages", () => {
  const { requirements } = JSON.parse(
    fs.readFileSync(
      new URL(
        "../../../../docs/evolution/2026-11-10/REQUESTS.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  assert.equal(requirements.length, 27);
  const original = JSON.stringify(requirements);
  for (const requirement of requirements) {
    assert.equal(
      requirementPresentation(requirement, "uk").title,
      requirement.source_text_uk,
      requirement.id,
    );
    assert.equal(
      requirementPresentation(requirement, "en").title,
      requirement.requirement_en,
      requirement.id,
    );
    assert.equal(
      requirementPresentation(requirement, "fr").title,
      requirement.requirement_en,
      requirement.id,
    );
    assert.equal(
      requirementPresentation(requirement, "uk").status,
      requirement.current_status,
      requirement.id,
    );
    assert.ok(
      requirementPresentation(requirement, "en").title.length > 10,
      requirement.id,
    );
  }
  assert.equal(JSON.stringify(requirements), original);
});

test("requirement fallback preserves every established field's priority, source and explicit status", () => {
  const raw = {
    id: "R-native",
    title: "Original title",
    description: "Description",
    text: "Text",
    requirement: "Requirement",
    source_text_uk: "Оригінальний запит",
    requirement_en: "English meaning",
    status: "deferred",
    current_status: "pending",
    source_ref: "requirements.json#R-native",
    source_sha256: "source-pin",
  };
  const original = structuredClone(raw);
  for (const field of ["title", "description", "text", "requirement"]) {
    assert.equal(requirementPresentation(raw, "uk").title, raw[field]);
    assert.equal(requirementPresentation(raw, "uk").status, "deferred");
    delete raw[field];
  }
  assert.equal(
    requirementPresentation(raw, "uk").title,
    original.source_text_uk,
  );
  assert.equal(raw.source_ref, original.source_ref);
  assert.equal(raw.source_sha256, original.source_sha256);
  assert.equal(
    requirementPresentation({ source_text_uk: "Лише оригінал" }, "en").title,
    "Лише оригінал",
  );
  assert.equal(
    requirementPresentation({ requirement_en: "Only English" }, "uk").title,
    "Only English",
  );
});

test("unloaded or failed workspaces remain explicit states and cannot supply empty verified counters", () => {
  assert.equal(workspaceReadState(null, "project-a", true), "loading");
  assert.equal(workspaceReadState(null, "project-a", false), "unavailable");
  const loaded = {
    project: { id: "project-a" },
    sources: [],
    requirements: [],
  };
  assert.equal(workspaceReadState(loaded, "project-a", false), "ready");
  assert.equal(workspaceReadState(loaded, "project-b", true), "loading");
  assert.equal(workspaceReadState(loaded, "project-b", false), "unavailable");
});

test("native owner obligations retain verbatim meaning and an unrecognized current status without inventing completion", () => {
  const native = Object.freeze({
    id: "CURRENT-OWNER-REQUEST",
    verbatim: "Повний вихідний запит власника",
    interpretation: "Derived explanation",
    current_status: "explicit owner scope; verification pending",
    source_ref: "owner-request.json",
    source_sha256: "owner-source-pin",
  });
  assert.equal(requirementPresentation(native, "uk").title, native.verbatim);
  assert.equal(requirementPresentation(native, "en").title, native.verbatim);
  assert.equal(
    requirementPresentation(native, "en").status,
    native.current_status,
  );
  assert.equal(
    requirementPresentation({ interpretation: native.interpretation }, "en")
      .title,
    native.interpretation,
  );
  assert.equal(native.source_ref, "owner-request.json");
  assert.equal(native.source_sha256, "owner-source-pin");
});

test("a project without declared bindings remains unverified even when it has source files", () => {
  const value = contextCoverage({
    sources: [{ path: "README.md", sha256: "source" }],
  });
  assert.equal(value.state, "unverified");
  assert.equal(value.completenessAuthenticated, false);
  assert.equal(value.verifiedSources, 0);
});

test("matching declared files never authenticates complete capture of the original brief", () => {
  const value = contextCoverage({
    context_coverage: {
      status: "verified-declared-bindings",
      source_completeness_authenticated: true,
      source_checks: [
        {
          path: "brief.md",
          required: true,
          status: "verified",
          expected_sha256: "pin",
          observed_sha256: "pin",
        },
      ],
    },
  });
  assert.equal(value.state, "verified-declared-bindings");
  assert.equal(value.verifiedSources, 1);
  assert.equal(value.completenessAuthenticated, false);
});

test("the actual manifest object and nested capsule coverage retain source and requirement bindings", () => {
  const check = {
    requirement_id: "R1",
    source_path: "brief.md",
    status: "verified-excerpt",
  };
  const value = contextCoverage({
    context: {
      coverage: {
        status: "verified-declared-bindings",
        manifest_ref: { path: "context.json", sha256: "manifest-pin" },
        source_checks: [],
        requirement_checks: [check],
      },
    },
  });
  assert.equal(value.manifestRef, "context.json");
  assert.equal(value.manifestHash, "manifest-pin");
  assert.deepEqual(value.requirements, [check]);
  assert.equal(value.completenessAuthenticated, false);
});

test("an observed missing must or required source cannot disappear behind a success status", () => {
  for (const coverage of [
    { missing_must_ids: ["M1", "M1", "M2"] },
    { missing_requirement_ids: ["R7"] },
    {
      source_checks: [{ path: "brief.md", required: true, status: "missing" }],
    },
    {
      source_checks: [
        { path: "brief.md", required: true, status: "unreadable" },
      ],
    },
  ]) {
    const value = contextCoverage({
      context_coverage: { status: "verified-declared-bindings", ...coverage },
    });
    assert.equal(value.state, "incomplete");
  }
  assert.deepEqual(
    contextCoverage({
      context_coverage: { missing_must_ids: ["M1", "M1", "M2"] },
    }).missingMustIds,
    ["M1", "M2"],
  );
});

test("a changed required source retains conflict priority over incomplete gaps", () => {
  const value = contextCoverage({
    context_coverage: {
      status: "verified-declared-bindings",
      missing_must_ids: ["M1"],
      source_checks: [
        {
          path: "decision.md",
          role: "decision",
          required: true,
          status: "changed",
          expected_sha256: "old",
          observed_sha256: "new",
        },
      ],
    },
  });
  assert.equal(value.state, "conflict");
  assert.equal(value.sources[0].record.expected_sha256, "old");
});

test("optional source loss remains visible without silently rewriting the native declaration", () => {
  const value = contextCoverage({
    context_coverage: {
      status: "verified-declared-bindings",
      source_checks: [
        { path: "optional.md", required: false, status: "missing" },
      ],
    },
  });
  assert.equal(value.state, "verified-declared-bindings");
  assert.equal(value.sources[0].status, "missing");
  assert.equal(value.verifiedSources, 0);
});

test("current decisions and deferred work preserve explicit native records and do not infer precedence from dates", () => {
  const first = { id: "decision-a", date: "2030-01-01" };
  const second = { id: "decision-b", date: "2020-01-01" };
  const deferred = {
    id: "later",
    status: "deferred",
    source_ref: "checkpoint.json",
  };
  assert.deepEqual(contextTrail({ decisions: [first, second] }).decisions, [
    first,
    second,
  ]);
  assert.equal(contextTrail({ decisions: [first] }).explicitlyCurrent, false);
  const value = contextTrail({
    decisions: [first, second],
    current_decisions: [second],
    deferred_work: [deferred],
  });
  assert.deepEqual(value.decisions, [second]);
  assert.equal(value.explicitlyCurrent, true);
  assert.deepEqual(value.deferred, [deferred]);
});

test("observed job counts retain cancellation/unknown states without inventing accepted outcomes", () => {
  assert.deepEqual(
    observedJobCounts([
      { status: "completed" },
      { status: "cancel_requested" },
      { status: "outcome_unknown" },
      { status: "awaiting_input" },
    ]),
    { total: 4, active: 2, attention: 1 },
  );
});
