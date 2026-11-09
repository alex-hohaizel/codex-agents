import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { join } from "node:path";
import { lstat } from "node:fs/promises";
import { atomicWrite, fail } from "./utils.mjs";

const equal = (left, right) => {
  if (typeof left !== "string" || typeof right !== "string") return false;
  const a = Buffer.from(left),
    b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
};

/** The launcher reads this private key; browsers receive only a 60s one-use token. */
export function launchToken(controlKey, now = Date.now()) {
  const payload = `${now + 60_000}.${randomBytes(18).toString("base64url")}`;
  const signature = createHmac("sha256", Buffer.from(controlKey, "base64url"))
    .update(payload)
    .digest("base64url");
  return `${payload}.${signature}`;
}

export function ownerProof(controlKey, nonce, instanceId) {
  fail(
    typeof nonce === "string" && /^[A-Za-z0-9_-]{16,80}$/.test(nonce),
    "INVALID_PROBE",
    "Invalid owner-instance probe",
  );
  return createHmac("sha256", Buffer.from(controlKey, "base64url"))
    .update(`atelier.instance.${instanceId}.${nonce}`)
    .digest("base64url");
}

export function verifyOwnerProof(controlKey, nonce, instanceId, proof) {
  return equal(ownerProof(controlKey, nonce, instanceId), proof);
}

export class OwnerSession {
  constructor({
    controlKey = randomBytes(32).toString("base64url"),
    now = () => Date.now(),
  } = {}) {
    fail(
      typeof controlKey === "string" && /^[A-Za-z0-9_-]{43}$/.test(controlKey),
      "INVALID_OWNER_KEY",
      "Invalid owner key",
    );
    this.controlKey = controlKey;
    this.session = randomBytes(32).toString("base64url");
    this.csrf = randomBytes(32).toString("base64url");
    this.now = now;
    this.used = new Map();
  }

  authenticated(cookie) {
    return equal(cookie, this.session);
  }
  controlAuthorized(value) {
    return equal(value, this.controlKey);
  }
  csrfAuthorized(value) {
    return equal(value, this.csrf);
  }
  proof(nonce, instanceId) {
    return ownerProof(this.controlKey, nonce, instanceId);
  }

  claim(token) {
    fail(
      typeof token === "string" && token.length < 240,
      "OWNER_LAUNCH_REQUIRED",
      "Open Agent Atelier through its local launcher",
      401,
    );
    const [expiryText, nonce, signature, extra] = token.split(".");
    const expiry = Number(expiryText),
      current = this.now();
    fail(
      !extra &&
        Number.isSafeInteger(expiry) &&
        expiry > current &&
        expiry <= current + 90_000 &&
        /^[A-Za-z0-9_-]{24}$/.test(nonce ?? "") &&
        /^[A-Za-z0-9_-]{43}$/.test(signature ?? ""),
      "OWNER_LAUNCH_REQUIRED",
      "The launcher link expired; open the local launcher again",
      401,
    );
    const expected = createHmac(
      "sha256",
      Buffer.from(this.controlKey, "base64url"),
    )
      .update(`${expiryText}.${nonce}`)
      .digest("base64url");
    fail(
      equal(signature, expected),
      "OWNER_LAUNCH_REQUIRED",
      "Invalid launcher link",
      401,
    );
    for (const [key, end] of this.used)
      if (end <= current) this.used.delete(key);
    fail(
      !this.used.has(nonce),
      "OWNER_LAUNCH_REPLAY",
      "This launcher link was already used; reopen the launcher",
      401,
    );
    fail(
      this.used.size < 4096,
      "SESSION_CAPACITY",
      "Too many pending launcher links",
      429,
    );
    this.used.set(nonce, expiry);
    return { session: this.session, csrf_token: this.csrf };
  }

  async persistOwnerKey(dataDir, instanceId) {
    const path = join(dataDir, "owner-credentials.json");
    try {
      const stat = await lstat(path);
      fail(
        stat.isFile() && !stat.isSymbolicLink(),
        "INVALID_OWNER_KEY",
        "Owner key path must be a regular file",
      );
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    await atomicWrite(
      path,
      JSON.stringify({
        schema_version: "atelier.owner-key/1",
        instance_id: instanceId,
        control_key: this.controlKey,
      }) + "\n",
    );
  }
}
