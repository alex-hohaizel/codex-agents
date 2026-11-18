import http from "node:http";
import { readFile, stat, mkdir, realpath } from "node:fs/promises";
import { resolve, join, dirname, extname } from "node:path";
import { platformStateRoot, securePrivatePath } from "./platform.mjs";
import { fileURLToPath } from "node:url";
import { OwnerSession } from "./session.mjs";
import { Application } from "./application.mjs";
import { acquireInstance } from "./instance.mjs";
import {
  atomicWrite,
  fail,
  isWithin,
  now,
  parseStrictJson,
  publicError,
  ServiceError,
} from "./utils.mjs";
import { SERVICE_VERSION } from "../shared/contracts.mjs";
const here = dirname(fileURLToPath(import.meta.url));
const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".pdf": "application/pdf",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".m4a": "audio/mp4",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
};
export async function createServer({
  dataDir = process.env.ATELIER_DATA_DIR ??
    platformStateRoot(),
  repoRoot = resolve(here, "../../.."),
  port = Number(process.env.ATELIER_PORT ?? 4317),
  host = "127.0.0.1",
  dist = resolve(here, "../dist/client"),
  application,
  devOrigin = process.env.ATELIER_DEV_ORIGIN,
} = {}) {
  fail(
    ["127.0.0.1", "localhost", "::1"].includes(host),
    "INVALID_HOST",
    "Only loopback addresses are supported",
  );
  dataDir = application?.dataDir ?? dataDir;
  await mkdir(dataDir, { recursive: true, mode: 0o700 });
  if (process.platform === "win32") await securePrivatePath(dataDir, { directory: true });
  dataDir = await realpath(dataDir);
  const releaseInstance = await acquireInstance(dataDir);
  const app =
    application ??
    new Application({
      dataDir,
      repoRoot,
    });
  const ownerSession = new OwnerSession();
  await ownerSession.persistOwnerKey(dataDir, app.instanceId);
  const csrf = ownerSession.csrf;
  const sseClients = new Set();
  let origin;
  const json = (res, status, value) => {
    res.writeHead(status, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    });
    res.end(JSON.stringify(value));
  };
  const cookieName = () => `atelier_session_${server.address()?.port}`;
  const cookie = (req) =>
    (req.headers.cookie ?? "")
      .split(";")
      .map((x) => x.trim())
      .find((x) => x.startsWith(cookieName() + "="))
      ?.slice(cookieName().length + 1);
  const authenticated = (req) => ownerSession.authenticated(cookie(req));
  const setCookie = (res) =>
    res.setHeader(
      "Set-Cookie",
      `${cookieName()}=${ownerSession.session}; HttpOnly; SameSite=Strict; Path=/`,
    );
  const readJson = async (req) => {
    fail(
      (req.headers["content-type"] ?? "").split(";")[0] === "application/json",
      "INVALID_INPUT",
      "Commands require application/json",
      415,
    );
    const chunks = [];
    let size = 0;
    for await (const chunk of req) {
      size += chunk.length;
      fail(
        size <= 1024 * 1024,
        "PAYLOAD_TOO_LARGE",
        "Command exceeds 1 MiB",
        413,
      );
      chunks.push(chunk);
    }
    return parseStrictJson(Buffer.concat(chunks).toString());
  };
  const server = http.createServer(async (req, res) => {
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("Referrer-Policy", "no-referrer");
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("Cross-Origin-Resource-Policy", "same-origin");
    try {
      const hostHeader = req.headers.host;
      const allowedHosts = new Set([
        `127.0.0.1:${server.address()?.port}`,
        `localhost:${server.address()?.port}`,
        `[::1]:${server.address()?.port}`,
      ]);
      fail(
        allowedHosts.has(hostHeader),
        "INVALID_HOST",
        "Unexpected Host header",
        403,
      );
      const url = new URL(req.url, origin);
      const allowedOrigins = new Set([
        origin,
        `http://localhost:${server.address()?.port}`,
        ...(devOrigin ? [devOrigin] : []),
      ]);
      if (req.headers.origin)
        fail(
          allowedOrigins.has(req.headers.origin),
          "CROSS_ORIGIN_DENIED",
          "This local service does not accept cross-origin requests",
          403,
        );
      if (url.pathname === "/health" && req.method === "GET")
        return json(res, 200, {
          status: "ok",
          version: SERVICE_VERSION,
          instance_id: app.instanceId,
          ...(url.searchParams.has("owner_probe")
            ? {
                owner_proof: ownerSession.proof(
                  url.searchParams.get("owner_probe"),
                  app.instanceId,
                ),
              }
            : {}),
        });
      if (url.pathname === "/api/v1/session" && req.method === "GET") {
        fail(
          ownerSession.controlAuthorized(req.headers["x-atelier-control"]) ||
            (authenticated(req) && ownerSession.csrfAuthorized(req.headers["x-atelier-csrf"])),
          "OWNER_LAUNCH_REQUIRED",
          "Open Agent Atelier through its local launcher",
          401,
        );
        setCookie(res);
        return json(res, 200, { status: "ready", csrf_token: csrf });
      }
      if (url.pathname === "/api/v1/session" && req.method === "POST") {
        fail(
          req.headers.origin && allowedOrigins.has(req.headers.origin),
          "CROSS_ORIGIN_DENIED",
          "A same-origin launcher claim is required",
          403,
        );
        const body = await readJson(req);
        ownerSession.claim(body.launch_token);
        setCookie(res);
        return json(res, 200, { status: "ready", csrf_token: csrf });
      }
      if (url.pathname.startsWith("/api/")) {
        const trustedRead = req.method === "GET" && ownerSession.controlAuthorized(req.headers["x-atelier-control"]);
        fail(
          trustedRead || authenticated(req),
          "SESSION_REQUIRED",
          "Open Agent Atelier in this browser before accessing private data",
          401,
        );
        fail(
          trustedRead || ownerSession.csrfAuthorized(req.headers["x-atelier-csrf"]),
          "SESSION_REQUIRED",
          "An origin-scoped browser proof is required for private requests; reopen the local launcher",
          403,
        );
        if (req.method === "POST") {
          fail(
            req.headers.origin && allowedOrigins.has(req.headers.origin),
            "CROSS_ORIGIN_DENIED",
            "A same-origin command is required",
            403,
          );
          const body = await readJson(req);
          if (url.pathname === "/api/v1/integrations/generation")
            return json(res, 200, await app.imageGeneration.generate(body));
          if (url.pathname === "/api/v1/integrations/read")
            return json(res, 200, await app.integrations.run(body));
          fail(
            url.pathname === "/api/v1/commands",
            "NOT_FOUND",
            "Unknown command route",
            404,
          );
          const receipt = await app.execute(body);
          return json(res, receipt.status === "failed" ? 409 : 200, receipt);
        }
        fail(
          req.method === "GET",
          "METHOD_NOT_ALLOWED",
          "Unsupported method",
          405,
        );
        if (url.pathname === "/api/v1/bootstrap")
          return json(res, 200, await app.bootstrap(csrf));
        if (url.pathname === "/api/v1/integrations")
          return json(
            res,
            200,
            await app.integrations.list({
              locale: app.store.get("settings", "owner")?.locale,
            }),
          );
        if (url.pathname === "/api/v1/integrations/inspect")
          return json(
            res,
            200,
            await app.integrations.inspect({
              kind: url.searchParams.get("kind"),
              id: url.searchParams.get("id"),
              locale: app.store.get("settings", "owner")?.locale,
            }),
          );
        if (url.pathname === "/api/v1/portfolio")
          return json(res, 200, app.portfolio.get());
        const portfolioMatch = url.pathname.match(
          /^\/api\/v1\/portfolio\/projects\/([^/]+)$/,
        );
        if (portfolioMatch)
          return json(
            res,
            200,
            await app.portfolio.project(decodeURIComponent(portfolioMatch[1]), {
              thread_offset: Number(url.searchParams.get("thread_offset") ?? 0),
              snapshot_checked_at:
                url.searchParams.get("snapshot_checked_at") ?? undefined,
              item_thread_id:
                url.searchParams.get("item_thread_id") ?? undefined,
              item_cursor: url.searchParams.get("item_cursor") ?? undefined,
              attachment_continue:
                url.searchParams.get("attachment_continue") ?? undefined,
              max_threads: url.searchParams.has("max_threads")
                ? Number(url.searchParams.get("max_threads"))
                : 40,
              max_turn_pages: url.searchParams.has("max_turn_pages")
                ? Number(url.searchParams.get("max_turn_pages"))
                : 4,
            }),
          );
        if (url.pathname === "/api/v1/doctor")
          return json(res, 200, app.doctor());
        if (url.pathname === "/api/v1/skills")
          return json(
            res,
            200,
            await app.skills.list(url.searchParams.get("q") ?? ""),
          );
        if (url.pathname === "/api/v1/events") {
          const after = Number(
            url.searchParams.get("after") ?? req.headers["last-event-id"] ?? 0,
          );
          fail(
            Number.isSafeInteger(after) && after >= 0,
            "INVALID_INPUT",
            "Invalid event cursor",
          );
          res.writeHead(200, {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-store",
            Connection: "keep-alive",
          });
          res.write(": connected\n\n");
          const send = (event) =>
            res.write(
              `id: ${event.sequence}\nevent: update\ndata: ${JSON.stringify(event)}\n\n`,
            );
          for (const event of app.store.events(after, 300)) send(event);
          sseClients.add(send);
          const heartbeat = setInterval(
            () => res.write(": heartbeat\n\n"),
            2e4,
          );
          heartbeat.unref();
          req.on("close", () => {
            clearInterval(heartbeat);
            sseClients.delete(send);
          });
          return;
        }
        const skillSource = url.pathname.match(
          /^\/api\/v1\/skills\/([^/]+)\/source$/,
        );
        if (skillSource)
          return json(
            res,
            200,
            await app.skills.source(decodeURIComponent(skillSource[1])),
          );
        let match = url.pathname.match(
          /^\/api\/v1\/projects\/([^/]+)\/threads$/,
        );
        if (match)
          return json(
            res,
            200,
            await app.codex.threads(
              app.projects.get(decodeURIComponent(match[1])).root,
              url.searchParams.get("cursor") ?? undefined,
            ),
          );
        match = url.pathname.match(/^\/api\/v1\/projects\/([^/]+)\/diff$/);
        if (match)
          return json(
            res,
            200,
            await app.projects.diff(
              decodeURIComponent(match[1]),
              url.searchParams.get("path") ?? undefined,
            ),
          );
        match = url.pathname.match(/^\/api\/v1\/projects\/([^/]+)\/workspace$/);
        if (match)
          return json(
            res,
            200,
            await app.projects.workspace(decodeURIComponent(match[1])),
          );
        match = url.pathname.match(
          /^\/api\/v1\/projects\/([^/]+)\/(source|artifact)$/,
        );
        if (match) {
          const projectId = decodeURIComponent(match[1]),
            ref = url.searchParams.get("path");
          if (match[2] === "source")
            return json(res, 200, await app.projects.content(projectId, ref));
          const artifact = await app.projects.artifact(projectId, ref);
          const extension = extname(artifact.file).toLowerCase();
          const safeTypes = new Set([
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".gif",
            ".pdf",
            ".mp3",
            ".wav",
            ".m4a",
            ".mp4",
            ".webm",
          ]);
          const content = await readFile(artifact.file);
          res.writeHead(200, {
            "Content-Type": safeTypes.has(extension)
              ? mime[extension]
              : "text/plain; charset=utf-8",
            "Content-Security-Policy": "sandbox; default-src 'none'",
            "Cache-Control": "no-store",
            "Content-Disposition": safeTypes.has(extension)
              ? "inline"
              : "attachment",
          });
          return res.end(content);
        }
        match = url.pathname.match(/^\/api\/v1\/jobs\/([^/]+)$/);
        if (match)
          return json(res, 200, { job: app.job(decodeURIComponent(match[1])) });
        match = url.pathname.match(/^\/api\/v1\/commands\/([^/]+)$/);
        if (match) {
          const value = app.store.commandGet(decodeURIComponent(match[1]));
          fail(value, "NOT_FOUND", "Command receipt not found", 404);
          return json(res, 200, value);
        }
        throw new ServiceError("NOT_FOUND", "Unknown API route", 404);
      }
      fail(
        req.method === "GET" || req.method === "HEAD",
        "METHOD_NOT_ALLOWED",
        "Unsupported method",
        405,
      );
      const requested = decodeURIComponent(url.pathname);
      const staticPath = resolve(dist, `.${requested}`);
      fail(
        isWithin(dist, staticPath),
        "OUTSIDE_ROOT",
        "Invalid static path",
        403,
      );
      let file = staticPath;
      try {
        if ((await stat(file)).isDirectory()) file = join(file, "index.html");
        await stat(file);
      } catch {
        file = join(dist, "index.html");
      }
      let bytes;
      try {
        bytes = await readFile(file);
      } catch {
        return json(res, 503, {
          error: {
            code: "CLIENT_NOT_BUILT",
            message:
              "Build the client with npm run build, then restart/open this local service",
          },
        });
      }
      res.setHeader(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
      );
      res.setHeader(
        "Cache-Control",
        file.endsWith("index.html") ? "no-cache" : "public, max-age=3600",
      );
      res.writeHead(200, {
        "Content-Type": mime[extname(file)] ?? "application/octet-stream",
      });
      res.end(req.method === "HEAD" ? undefined : bytes);
    } catch (error) {
      if (!res.headersSent)
        json(res, error.status ?? 500, { error: publicError(error) });
      else res.end();
    }
  });
  app.on("event", (event) => {
    for (const send of sseClients) send(event);
  });
  let closing;
  const close = () =>
    (closing ??= (async () => {
      for (const send of sseClients)
        try {
          send({
            sequence: 0,
            event: "service.stopping",
            data: {},
            created_at: now(),
          });
        } catch {}
      server.closeAllConnections();
      await new Promise((r) => server.close(r));
      await app.close();
      await releaseInstance();
    })());
  app.on("stop", () => close());
  try {
    await new Promise((accept, reject) => {
      server.once("error", reject);
      server.listen(port, host, accept);
    });
  } catch (error) {
    await app.close();
    await releaseInstance();
    throw error;
  }
  origin = `http://${host === "::1" ? "[::1]" : host}:${server.address().port}`;
  return {
    server,
    app,
    origin,
    close,
    ownerSession,
  };
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const args = process.argv.slice(2);
  const option = (name) => {
    const index = args.indexOf(name);
    return index >= 0 ? args[index + 1] : undefined;
  };
  const running = await createServer({
    ...(option("--port") ? { port: Number(option("--port")) } : {}),
    ...(option("--data-dir") ? { dataDir: resolve(option("--data-dir")) } : {}),
    ...(option("--repo") ? { repoRoot: resolve(option("--repo")) } : {}),
  });
  const runtime = {
    pid: process.pid,
    instance_id: running.app.instanceId,
    port: running.server.address().port,
    origin: running.origin,
    version: SERVICE_VERSION,
    started_at: now(),
    data_dir: running.app.dataDir,
  };
  await atomicWrite(
    join(running.app.dataDir, "runtime.json"),
    JSON.stringify(runtime, null, 2),
  );
  console.log(
    JSON.stringify({
      status: "listening",
      ...runtime,
    }),
  );
  for (const signal of ["SIGTERM", "SIGINT"])
    process.once(signal, () => running.close().then(() => process.exit(0)));
  running.server.on("close", () => {
    if (running.app.closing) setTimeout(() => process.exit(0), 50).unref();
  });
}
