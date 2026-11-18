#!/usr/bin/env node
import { readFile, mkdir, lstat, realpath } from "node:fs/promises";
import { spawn } from "node:child_process";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { platformStateRoot, securePrivatePath, assertPrivatePath } from "../server/platform.mjs";
import { randomBytes } from "node:crypto";
import { setTimeout as delay } from "node:timers/promises";
import { runtimeEnvironment } from "../server/environment.mjs";
import { launchToken, verifyOwnerProof } from "../server/session.mjs";
const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const verb = args[0] ?? "start";
const value = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : undefined;
};
let dataDir = resolve(
  value("--data-dir") ??
    process.env.ATELIER_DATA_DIR ??
    platformStateRoot(),
);
try {
  dataDir = await realpath(dataDir);
} catch (error) {
  if (error.code !== "ENOENT") throw error;
}
const port = Number(value("--port") ?? process.env.ATELIER_PORT ?? 4317);
const print = (value) => console.log(JSON.stringify(value, null, 2));
function processAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    if (error.code === "ESRCH") return false;
    throw error;
  }
}
async function runtime() {
  try {
    const saved = JSON.parse(
      await readFile(join(dataDir, "runtime.json"), "utf8"),
    );
    const url = new URL(saved.origin);
    if (
      url.protocol !== "http:" ||
      !["127.0.0.1", "localhost", "[::1]"].includes(url.hostname) ||
      url.username ||
      url.password ||
      url.pathname !== "/" ||
      url.search ||
      url.hash
    )
      return null;
    if (
      !Number.isSafeInteger(saved.pid) ||
      saved.pid <= 0 ||
      !/^instance_[a-f0-9-]{36}$/.test(saved.instance_id ?? "") ||
      resolve(saved.data_dir ?? "") !== dataDir ||
      Number(url.port) !== saved.port
    )
      return null;
    if ((value("--port") || process.env.ATELIER_PORT) && saved.port !== port)
      return null;
    return saved;
  } catch {
    return null;
  }
}
async function health(origin, expectedInstance) {
  try {
    const response = await fetch(origin + "/health", {
      signal: AbortSignal.timeout(1500),
      redirect: "error",
    });
    if (!response.ok) return null;
    const result = await response.json();
    return result.status === "ok" &&
      /^instance_[a-f0-9-]{36}$/.test(result.instance_id ?? "") &&
      (!expectedInstance || result.instance_id === expectedInstance)
      ? result
      : null;
  } catch {
    return null;
  }
}
async function ownerKey(expectedInstance) {
  const path = join(dataDir, "owner-credentials.json");
  const info = await lstat(path);
  if (!info.isFile() || info.isSymbolicLink())
    throw new Error("Owner credentials must be a private regular file");
  await assertPrivatePath(path);
  const key = JSON.parse(await readFile(path, "utf8"));
  if (
    key.instance_id !== expectedInstance ||
    !/^[A-Za-z0-9_-]{43}$/.test(key.control_key ?? "")
  )
    throw new Error("Owner credentials belong to another instance");
  return key.control_key;
}
async function verifiedOwnerKey(current) {
  const controlKey = await ownerKey(current.instance_id),
    nonce = randomBytes(24).toString("base64url");
  const response = await fetch(
    current.origin + "/health?owner_probe=" + nonce,
    { signal: AbortSignal.timeout(3000), redirect: "error" },
  );
  const proof = await response.json();
  if (
    !response.ok ||
    proof.instance_id !== current.instance_id ||
    !verifyOwnerProof(controlKey, nonce, current.instance_id, proof.owner_proof)
  )
    throw new Error("Local listener ownership could not be verified");
  return controlKey;
}
async function launchUrl(current) {
  return (
    current.origin +
    "/#atelier_launch=" +
    launchToken(await verifiedOwnerKey(current))
  );
}
async function openBrowser(url) {
  const command = process.platform === "darwin" ? "open" : process.platform === "win32" ? "cmd" : "xdg-open";
  const argv = process.platform === "win32" ? ["/d", "/c", "start", "", url] : [url];
  const browser = spawn(command, argv, { stdio: "ignore", detached: true, windowsHide: true });
  browser.once("error", () => print({ browser_opened: false, next: "The service is running. Reopen the local launcher from a graphical desktop with a configured default browser." }));
  browser.unref();
}

async function authenticated(current, path, body) {
  const origin = current.origin;
  const controlKey = await verifiedOwnerKey(current);
  const session = await fetch(origin + "/api/v1/session", {
    headers: { "X-Atelier-Control": controlKey },
    signal: AbortSignal.timeout(3e3),
    redirect: "error",
  });
  if (!session.ok) throw new Error("Service session unavailable");
  const cookie = session.headers.get("set-cookie")?.split(";")[0];
  const token = (await session.json()).csrf_token;
  const response = await fetch(origin + path, {
    method: body ? "POST" : "GET",
    headers: {
      cookie,
      "X-Atelier-CSRF": token,
      ...(body
        ? {
            "Content-Type": "application/json",
            Origin: origin,
          }
        : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  return response.json();
}
try {
  if (verb === "start") {
    const existing = await runtime();
    if (existing && (await health(existing.origin, existing.instance_id))) {
      print({
        status: "already_running",
        ...existing,
      });
      if (!args.includes("--no-open"))
        await openBrowser(await launchUrl(existing));
      process.exit(0);
    }
    if (existing && processAlive(existing.pid))
      throw new Error(
        "A recorded service process is alive but its identity/health is unverified; reconcile it before launching another writer",
      );
    if (!Number.isSafeInteger(port) || port < 1 || port > 65535)
      throw new Error("Port must be an integer from1to65535");
    const origin = `http://127.0.0.1:${port}`;
    if (await health(origin))
      throw new Error(
        "The selected port belongs to an unregistered instance; use its recorded data directory or another port",
      );
    const major = Number(process.versions.node.split(".")[0]);
    if (major < 24) throw new Error("Node.js24or newer is required");
    try {
      await readFile(join(appRoot, "dist/client/index.html"));
    } catch {
      throw new Error(
        "The client is not built. Run npm ci and npm run build in the app directory first.",
      );
    }
    await mkdir(dataDir, {
      recursive: true,
      mode: 448,
    });
    if (process.platform === "win32") await securePrivatePath(dataDir, { directory: true });
    dataDir = await realpath(dataDir);
    const child = spawn(
      process.execPath,
      [
        join(appRoot, "server/index.mjs"),
        "--port",
        String(port),
        "--data-dir",
        dataDir,
      ],
      {
        cwd: appRoot,
        detached: true,
        windowsHide: true,
        stdio: "ignore",
        env: {
          ...runtimeEnvironment(process.env, { service: true }),
          ATELIER_DATA_DIR: dataDir,
        },
      },
    );
    child.unref();
    let result;
    for (let attempt = 0; attempt < 40; attempt++) {
      await delay(150);
      const current = await runtime();
      if (current && (await health(current.origin, current.instance_id))) {
        result = current;
        break;
      }
    }
    if (!result)
      throw new Error(
        "The local server did not become ready. Check the port, Node runtime and data directory permissions.",
      );
    print({
      status: "started",
      ...result,
    });
    if (!args.includes("--no-open")) await openBrowser(await launchUrl(result));
  } else if (verb === "status") {
    const current = await runtime();
    print(
      current && (await health(current.origin, current.instance_id))
        ? {
            status: "running",
            ...current,
          }
        : {
            status: "stopped",
            data_dir: dataDir,
          },
    );
  } else if (verb === "doctor") {
    const current = await runtime();
    if (!current || !(await health(current.origin, current.instance_id)))
      throw new Error("The service is not running");
    print(await authenticated(current, "/api/v1/doctor"));
  } else if (verb === "stop") {
    const current = await runtime();
    if (!current || !(await health(current.origin, current.instance_id))) {
      print({ status: "already_stopped" });
      process.exit(0);
    }
    print(
      await authenticated(current, "/api/v1/commands", {
        command_id: crypto.randomUUID(),
        operation: "service.stop",
        payload: {},
      }),
    );
  } else
    throw new Error(
      "Usage: node launcher/atelier.mjs start|status|doctor|stop [--data-dir PATH] [--port4317] [--no-open]",
    );
} catch (error) {
  print({
    status: "error",
    message: error.message,
  });
  process.exitCode = 1;
}
