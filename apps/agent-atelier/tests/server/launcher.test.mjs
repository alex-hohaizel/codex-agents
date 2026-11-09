import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, writeFile, rm } from "node:fs/promises";
import { join, resolve } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { randomUUID, randomBytes } from "node:crypto";
import http from "node:http";
const run = promisify(execFile),
  appRoot = resolve(import.meta.dirname, "../.."),
  launcher = join(appRoot, "launcher/atelier.mjs");
const invoke = async (args) => {
  const result = await run(process.execPath, [launcher, ...args], {
    cwd: appRoot,
    timeout: 12000,
    maxBuffer: 1024 * 1024,
  });
  return JSON.parse(result.stdout);
};
test(
  "launcher starts one verified instance, reports status/doctor and stops that instance",
  { timeout: 30000 },
  async () => {
    const data = await mkdtemp(
      join(realpathSync(tmpdir()), "atelier-launcher-"),
    );
    const portServer = http.createServer();
    await new Promise((resolve) => portServer.listen(0, "127.0.0.1", resolve));
    const port = portServer.address().port;
    await new Promise((resolve) => portServer.close(resolve));
    const flags = ["--data-dir", data, "--port", String(port), "--no-open"];
    let started = false;
    try {
      const first = await invoke(["start", ...flags]);
      started = true;
      assert.equal(first.status, "started");
      const second = await invoke(["start", ...flags]);
      assert.equal(second.status, "already_running");
      assert.equal(second.instance_id, first.instance_id);
      assert.equal(second.pid, first.pid);
      assert.equal((await invoke(["status", ...flags])).status, "running");
      const doctor = await invoke(["doctor", ...flags]);
      assert.equal(doctor.instance_id, first.instance_id);
      assert.equal(doctor.database.engine, "SQLite");
      const stopped = await invoke(["stop", ...flags]);
      assert.equal(stopped.status, "completed");
      for (let n = 0; n < 30; n++) {
        if ((await invoke(["status", ...flags])).status === "stopped") {
          started = false;
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      assert.equal(started, false);
      const key = JSON.parse(
        await readFile(join(data, "owner-credentials.json"), "utf8"),
      );
      assert.match(key.control_key, /^[A-Za-z0-9_-]{43}$/);
      assert.equal(JSON.stringify(first).includes(key.control_key), false);
    } finally {
      if (started)
        try {
          await invoke(["stop", ...flags]);
        } catch {}
      await rm(data, { recursive: true, force: true });
    }
  },
);
test(
  "launcher never sends owner key to a listener spoofing only public runtime identity",
  { timeout: 10000 },
  async () => {
    const data = await mkdtemp(
      join(realpathSync(tmpdir()), "atelier-listener-"),
    );
    const instance = "instance_" + randomUUID(),
      key = randomBytes(32).toString("base64url");
    let sensitiveHeader = false,
      sessionCalls = 0;
    const listener = http.createServer((req, res) => {
      if (req.headers["x-atelier-control"]) sensitiveHeader = true;
      if (req.url.startsWith("/api/v1/session")) sessionCalls++;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ status: "ok", instance_id: instance }));
    });
    await new Promise((resolve) => listener.listen(0, "127.0.0.1", resolve));
    const port = listener.address().port,
      origin = "http://127.0.0.1:" + port;
    try {
      await writeFile(
        join(data, "runtime.json"),
        JSON.stringify({
          pid: process.pid,
          instance_id: instance,
          port,
          origin,
          data_dir: data,
        }),
      );
      await writeFile(
        join(data, "owner-credentials.json"),
        JSON.stringify({ instance_id: instance, control_key: key }),
        { mode: 0o600 },
      );
      await assert.rejects(
        invoke(["doctor", "--data-dir", data, "--port", String(port)]),
        (error) =>
          JSON.parse(error.stdout).message ===
          "Local listener ownership could not be verified",
      );
      assert.equal(sensitiveHeader, false);
      assert.equal(sessionCalls, 0);
    } finally {
      await new Promise((resolve) => listener.close(resolve));
      await rm(data, { recursive: true, force: true });
    }
  },
);
