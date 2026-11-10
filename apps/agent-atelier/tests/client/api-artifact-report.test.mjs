import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { api } from "../../client/src/api.ts";

const path = "reports/REPORT.uk.md";
const raw = "# Actual report\n\nA source-only result.\n";
const hash = createHash("sha256").update(raw).digest("hex");
const bytes = Buffer.byteLength(raw);
const artifact = { path, bytes, modified_at: "2026-11-10T12:00:00Z" };
const source = { path, bytes, sha256: hash };
const answer = { ...source, content: raw };

function reply(t, payload = answer, status = 200) {
  const original = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push({ url, options });
    return new Response(JSON.stringify(payload), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  t.after(() => {
    globalThis.fetch = original;
  });
  return requests;
}

test("artifact report uses the scoped readonly source route and exact indexed pin", async (t) => {
  const requests = reply(t);
  const controller = new AbortController();
  const result = await api.artifactReport(
    "project/a",
    artifact,
    source,
    controller.signal,
  );
  assert.equal(result.source_observation, "matched-indexed-pin");
  assert.equal(result.content, raw);
  assert.equal(result.content_redacted, true);
  const request = requests[0];
  const url = new URL(request.url, "http://127.0.0.1");
  assert.equal(url.pathname, "/api/v1/projects/project%2Fa/source");
  assert.equal(url.searchParams.get("path"), path);
  assert.equal(request.options.credentials, "same-origin");
  assert.equal(request.options.signal, controller.signal);
});

test("ordinary unbound artifact gets a fresh SOURCE-ONLY observation, not invented pin acceptance", async (t) => {
  reply(t, { ...answer, owner_acceptance: true, job_id: "not-a-binding" });
  const result = await api.artifactReport("project/a", artifact);
  assert.equal(result.source_observation, "fresh-source-only");
  assert.equal(result.sha256, hash);
  assert.equal(result.owner_acceptance, undefined);
  assert.equal(result.job_id, undefined);
});

test("redacted preview text is not hashed as original file bytes", async (t) => {
  reply(t, { ...answer, content: "# [REDACTED]\n" });
  const result = await api.artifactReport("project/a", artifact, source);
  assert.equal(result.sha256, hash);
  assert.equal(result.content, "# [REDACTED]\n");
  assert.equal(result.content_redacted, true);
});

test("drift, truncation, missing response proof and binary text reject readable preview", async (t) => {
  const original = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = original;
  });
  for (const change of [
    { path: "another.md" },
    { bytes: bytes + 1 },
    { sha256: "0".repeat(64) },
    { sha256: undefined },
    { content: undefined },
    { content: "a\0b" },
    { content: "x".repeat(1024 * 1024 + 1) },
    { truncated: true },
  ]) {
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ ...answer, ...change }), {
        headers: { "Content-Type": "application/json" },
      });
    await assert.rejects(api.artifactReport("project/a", artifact, source), {
      code: "SOURCE_DRIFT",
    });
  }
});

test("invalid or oversized selection and conflicting source pins fail before any fetch", async (t) => {
  const requests = reply(t);
  for (const change of [
    { path: "../REPORT.md" },
    { path: "/REPORT.md" },
    { path: "report.html" },
    { bytes: undefined },
    { bytes: "12" },
    { bytes: 1024 * 1024 + 1 },
  ]) {
    await assert.rejects(
      api.artifactReport("project/a", { ...artifact, ...change }, source),
      {
        code: "ARTIFACT_REPORT_UNAVAILABLE",
      },
    );
  }
  await assert.rejects(
    api.artifactReport(
      "project/a",
      { ...artifact, sha256: "0".repeat(64) },
      source,
    ),
    { code: "SOURCE_DRIFT" },
  );
  assert.equal(requests.length, 0);
});

test("an unrelated project's source pin cannot become this artifact's expected pin", async (t) => {
  reply(t);
  const result = await api.artifactReport("project/a", artifact, {
    ...source,
    path: "different.md",
    sha256: "0".repeat(64),
  });
  assert.equal(result.source_observation, "fresh-source-only");
});

test("server source loss remains a real error for UI retry/download recovery", async (t) => {
  reply(
    t,
    { error: { code: "SOURCE_MISSING", message: "Source disappeared" } },
    404,
  );
  await assert.rejects(api.artifactReport("project/a", artifact, source), {
    code: "SOURCE_MISSING",
    status: 404,
  });
});
