import { mkdir, open, readFile, unlink } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { fail, parseStrictJson, now, ServiceError } from "./utils.mjs";

// The lock is acquired before opening SQLite or classifying interrupted jobs.
// A second launcher must never turn the first instance's running jobs into unknowns.
export async function acquireInstance(dataDir) {
  await mkdir(dataDir, { recursive: true, mode: 0o700 });
  const path = join(dataDir, "instance.lock");
  const nonce = randomUUID();
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const handle = await open(path, "wx", 0o600);
      await handle.writeFile(
        JSON.stringify({ pid: process.pid, nonce, started_at: now() }),
      );
      await handle.sync();
      return async () => {
        await handle.close();
        try {
          const current = parseStrictJson(await readFile(path, "utf8"));
          if (current.nonce === nonce) await unlink(path);
        } catch (error) {
          if (error.code !== "ENOENT") throw error;
        }
      };
    } catch (error) {
      if (error.code !== "EEXIST") throw error;
      let previous;
      try {
        previous = parseStrictJson(await readFile(path, "utf8"));
      } catch {
        throw new ServiceError(
          "INSTANCE_CONFLICT",
          "The instance lock is invalid; inspect it before recovery",
          409,
        );
      }
      fail(
        Number.isSafeInteger(previous.pid) &&
          previous.pid > 0 &&
          typeof previous.nonce === "string",
        "INSTANCE_CONFLICT",
        "Invalid instance lock",
        409,
      );
      let alive = true;
      try {
        process.kill(previous.pid, 0);
      } catch (probe) {
        if (probe.code === "ESRCH") alive = false;
        else
          throw new ServiceError(
            "INSTANCE_CONFLICT",
            "Cannot establish whether the previous service still owns this data directory",
            409,
          );
      }
      fail(
        !alive,
        "INSTANCE_CONFLICT",
        "Another service process owns this data directory; use its existing window or reconcile it first",
        409,
      );
      const rechecked = parseStrictJson(await readFile(path, "utf8"));
      fail(
        rechecked.nonce === previous.nonce,
        "INSTANCE_CONFLICT",
        "Instance ownership changed during recovery",
        409,
      );
      await unlink(path);
    }
  }
  throw new ServiceError(
    "INSTANCE_CONFLICT",
    "Could not acquire exclusive service ownership",
    409,
  );
}
