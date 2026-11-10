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
} from "../../client/src/workbench.ts";

test("current workspace direction retains the current declared goal and next action without upgrading its approval", () => {
  const goal = { text: "Current owner scope", status: "declared", source_ref: "current.json" };
  const next = [{ text: "Repair and retest the current blocker" }];
  const agents = [{ name: "current-specialist", availability: "installed" }];
  const current = { project: { id: "project-a" }, goal, next_actions: next, agents };
  assert.deepEqual(workspaceDirection(current, "project-a"), { goal, next, agents });
  assert.equal(workspaceDirection(current, "project-a").goal.status, "declared");
  assert.equal(workspaceDirection({ ...current, goal: { text: "", status: "unknown" }, next_actions: [] }, "project-a").goal.status, "unknown");
  assert.deepEqual(workspaceDirection({ ...current, next_actions: [] }, "project-a").next, []);
});

test("missing or wrong-project workspace direction never fills the goal from another project", () => {
  const current = { project: { id: "project-a" }, goal: { text: "Old accepted goal", status: "accepted" }, next_actions: [{ text: "Old next action" }] };
  for (const value of [workspaceDirection(null, "project-a"), workspaceDirection(current, "project-b"), workspaceDirection(current, undefined)])
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
