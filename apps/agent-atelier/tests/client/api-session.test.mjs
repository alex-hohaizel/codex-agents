import test from "node:test";
import assert from "node:assert/strict";

let importSequence = 0;

async function client(fragment, respond) {
  const calls = [];
  const history = [];
  const location = {
    pathname: "/",
    search: "?locale=uk",
    hash: fragment,
  };
  globalThis.window = {
    location,
    history: {
      state: { retained: true },
      replaceState(state, title, path) {
        history.push({ state, title, path });
        location.hash = path.includes("#") ? `#${path.split("#")[1]}` : "";
      },
    },
  };
  globalThis.fetch = async (path, init) => {
    calls.push({ path, init, hashAtRequest: location.hash });
    const { body, status = 200 } = respond(path, init, calls.length);
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  const module = await import(
    `../../client/src/api.ts?session-test=${++importSequence}`
  );
  return { ...module, calls, history, location };
}

test("owner bootstrap leaves the URL before a single token POST", async () => {
  const c = await client(
    "#keep=visible&atelier_launch=synthetic-test-token",
    (p) => ({
      body: p.endsWith("/session")
        ? { csrf_token: "fixture" }
        : { projects: [] },
    }),
  );
  assert.equal(c.calls.length, 0);
  assert.equal(c.location.hash, "#keep=visible");
  assert.deepEqual(c.history, [
    { state: { retained: true }, title: "", path: "/?locale=uk#keep=visible" },
  ]);
  await c.api.bootstrap();
  await c.api.bootstrap();
  const sessions = c.calls.filter((call) => call.path.endsWith("/session"));
  assert.equal(sessions.length, 1);
  assert.equal(sessions[0].init.method, "POST");
  assert.deepEqual(JSON.parse(sessions[0].init.body), {
    launch_token: "synthetic-test-token",
  });
  assert.ok(
    c.calls.every((call) => !call.hashAtRequest.includes("atelier_launch")),
  );
});

test("plain unauthenticated URL cannot mint a session", async () => {
  const c = await client("", () => ({
    status: 401,
    body: { error: { code: "OWNER_LAUNCH_REQUIRED", message: "Use launcher" } },
  }));
  await assert.rejects(c.api.bootstrap(), { code: "LAUNCH_REQUIRED" });
  assert.equal(c.calls.length, 1);
  assert.equal(c.calls[0].init.method, undefined);
  assert.equal(c.history.length, 0);
});

test("replayed or expired token is removed and never POSTed again", async () => {
  const c = await client("#atelier_launch=expired-fixture", () => ({
    status: 401,
    body: {
      error: {
        code: "OWNER_LAUNCH_REPLAY",
        message: "Fresh launcher required",
      },
    },
  }));
  await assert.rejects(c.api.bootstrap(), { code: "LAUNCH_REQUIRED" });
  await assert.rejects(c.api.bootstrap(), { code: "LAUNCH_REQUIRED" });
  assert.equal(c.location.hash, "");
  assert.deepEqual(
    c.calls.map((call) => call.init.method ?? "GET"),
    ["POST", "GET"],
  );
});

test("an existing browser cookie uses GET without any owner bootstrap", async () => {
  const c = await client("#section", (path) => ({
    body: path.endsWith("/session")
      ? { csrf_token: "fixture" }
      : { projects: [] },
  }));
  await c.api.bootstrap();
  assert.ok(c.calls.every((call) => call.init.credentials === "same-origin"));
  assert.equal(c.calls[0].init.method, undefined);
  assert.equal(c.location.hash, "#section");
  assert.equal(c.history.length, 0);
});

test("a launcher fragment can recover an already-open unauthenticated tab", async () => {
  let claimed = false;
  const c = await client("", (path, init) => {
    if (path.endsWith("/session") && init.method === "POST") claimed = true;
    return claimed
      ? { body: { projects: [] } }
      : { status: 401, body: { error: { code: "OWNER_LAUNCH_REQUIRED" } } };
  });
  await assert.rejects(c.api.bootstrap(), { code: "LAUNCH_REQUIRED" });
  c.location.hash = "#atelier_launch=fresh-fixture&keep=visible";
  await c.api.bootstrap();
  assert.equal(c.location.hash, "#keep=visible");
  assert.equal(c.calls.filter((call) => call.init.method === "POST").length, 1);
  assert.ok(
    c.calls.every((call) => !call.hashAtRequest.includes("atelier_launch")),
  );
});
