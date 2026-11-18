import test from "node:test";
import assert from "node:assert/strict";

let importSequence = 0;

async function client(fragment, respond, storage = new Map()) {
  const calls = [];
  const history = [];
  const location = {
    pathname: "/",
    search: "?locale=uk",
    hash: fragment,
  };
  globalThis.window = {
    location,
    sessionStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value), removeItem: key => storage.delete(key) },
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
  return { ...module, calls, history, location, storage };
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
  assert.equal(c.calls.length, 0);
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
    ["POST"],
  );
});

test("a refreshed browser keeps origin-scoped proof and sends it on every private GET", async () => {
  const storage = new Map([["atelier.session.csrf.v1", "fixture"]]);
  const c = await client("#section", (path) => ({
    body: path.endsWith("/session")
      ? { csrf_token: "fixture" }
      : { projects: [] },
  }), storage);
  await c.api.bootstrap();
  assert.ok(c.calls.every((call) => call.init.credentials === "same-origin"));
  assert.equal(c.calls[0].init.method, undefined);
  assert.ok(c.calls.every(call => new Headers(call.init.headers).get("X-Atelier-CSRF") === "fixture"));
  assert.equal(c.location.hash, "#section");
  assert.equal(c.history.length, 0);
});

test("a launcher fragment can recover an already-open unauthenticated tab", async () => {
  let claimed = false;
  const c = await client("", (path, init) => {
    if (path.endsWith("/session") && init.method === "POST") claimed = true;
    return claimed
      ? { body: path.endsWith("/session") ? { csrf_token: "fixture" } : { projects: [] } }
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

test("a successful claim stores proof for a real module refresh without storing its launcher token", async () => {
  const storage = new Map();
  const reply = path => ({ body: path.endsWith('/session') ? {csrf_token:'refresh-proof'} : {projects:[]} });
  const first = await client('#atelier_launch=one-use-fixture',reply,storage);await first.api.bootstrap();
  assert.equal(storage.get('atelier.session.csrf.v1'),'refresh-proof');
  assert.ok(![...storage.values()].includes('one-use-fixture'));
  const refreshed = await client('',reply,storage);await refreshed.api.bootstrap();
  assert.equal(refreshed.calls[0].init.method,undefined);
  assert.equal(new Headers(refreshed.calls[0].init.headers).get('X-Atelier-CSRF'),'refresh-proof');
});

test("authenticated fetch SSE reconnects with its durable event cursor and closes without query secrets", async () => {
  const storage = new Map([['atelier.session.csrf.v1','stream-proof']]);
  const c = await client('',path=>({body:path.endsWith('/session')?{csrf_token:'stream-proof'}:{projects:[]}}),storage);
  await c.api.bootstrap();
  const calls=[];let connection=0;
  globalThis.fetch=async(path,init)=>{
    calls.push({path,init});connection++;
    const number=connection;
    return new Response(new ReadableStream({start(controller){
      if(number===1){controller.enqueue(new TextEncoder().encode('id: 7\r\nevent: update\r\ndata: {"part":'));controller.enqueue(new TextEncoder().encode('1}\r\n\r\n'));controller.close();}
      else {controller.enqueue(new TextEncoder().encode('id: 8\nevent: update\ndata: {"part":2}\n\n'));init.signal.addEventListener('abort',()=>{try{controller.close()}catch{}});}
    }}),{headers:{'Content-Type':'text/event-stream'}});
  };
  const received=[];const stream=c.subscribeEvents(event=>received.push(event),{reconnectMs:2});
  for(let n=0;n<100&&received.length<2;n++)await new Promise(ok=>setTimeout(ok,5));
  stream.close();
  assert.deepEqual(received.map(event=>event.lastEventId),['7','8']);
  assert.equal(calls.length,2);assert.ok(calls.every(call=>call.path==='/api/v1/events'));
  assert.ok(calls.every(call=>new Headers(call.init.headers).get('X-Atelier-CSRF')==='stream-proof'));
  assert.equal(new Headers(calls[1].init.headers).get('Last-Event-ID'),'7');
  await new Promise(ok=>setTimeout(ok,10));assert.equal(calls.length,2);
});

test("media reads carry the browser proof and retain the server-forced safe MIME", async () => {
  const storage = new Map([['atelier.session.csrf.v1','media-proof']]);
  const c = await client('',path=>({body:{csrf_token:'media-proof'}}),storage);await c.api.bootstrap();
  let seen;
  globalThis.fetch=async(path,init)=>{seen={path,init};return new Response('<svg onload="unsafe()"/>',{headers:{'Content-Type':'text/plain; charset=utf-8'}})};
  const blob=await c.api.artifactBlob('project/a','unsafe.svg');
  assert.equal(new Headers(seen.init.headers).get('X-Atelier-CSRF'),'media-proof');
  assert.equal(blob.type,'text/plain;charset=utf-8');assert.ok(!seen.path.includes('media-proof'));
});
