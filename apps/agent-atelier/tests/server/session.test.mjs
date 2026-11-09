import { tmpdir } from "node:os";
import { realpathSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, stat, rm, symlink } from "node:fs/promises";
import { join } from "node:path";
import {
  OwnerSession,
  launchToken,
  verifyOwnerProof,
} from "../../server/session.mjs";

test("owner launcher token expires, is one-use and cannot cross instances", () => {
  let now = 100_000;
  const owner = new OwnerSession({ now: () => now });
  const token = launchToken(owner.controlKey, now);
  const result = owner.claim(token);
  assert.equal(owner.authenticated(result.session), true);
  assert.equal(owner.csrfAuthorized(result.csrf_token), true);
  assert.throws(() => owner.claim(token), { code: "OWNER_LAUNCH_REPLAY" });
  assert.throws(() => new OwnerSession({ now: () => now }).claim(token), {
    code: "OWNER_LAUNCH_REQUIRED",
  });
  const expired = launchToken(owner.controlKey, now);
  now += 60_001;
  assert.throws(() => owner.claim(expired), { code: "OWNER_LAUNCH_REQUIRED" });
});

test("malformed control/cookie/token never grants owner access", () => {
  const owner = new OwnerSession();
  for (const value of [undefined, "", "👁".repeat(43), "fake", owner.csrf]) {
    assert.equal(owner.authenticated(value), false);
    assert.equal(owner.controlAuthorized(value), false);
  }
  assert.equal(owner.controlAuthorized(owner.controlKey), true);
  for (const token of [
    null,
    "",
    "1.x.y",
    `${Date.now() + 1_000_000}.abcdefghijklmnopqrstuvwx.fake`,
  ])
    assert.throws(() => owner.claim(token), { code: "OWNER_LAUNCH_REQUIRED" });
});

test("owner-instance proof prevents sending the private control key to an unrelated local listener", () => {
  const owner = new OwnerSession();
  const nonce = "public-fixture-probe-42";
  const proof = owner.proof(nonce, "instance-A");
  assert.equal(
    verifyOwnerProof(owner.controlKey, nonce, "instance-A", proof),
    true,
  );
  assert.equal(
    verifyOwnerProof(owner.controlKey, nonce, "instance-B", proof),
    false,
  );
  assert.equal(
    verifyOwnerProof(owner.controlKey, nonce + "x", "instance-A", proof),
    false,
  );
  assert.equal(
    verifyOwnerProof(new OwnerSession().controlKey, nonce, "instance-A", proof),
    false,
  );
});

test("owner control key is private, separate from public runtime and rejects linked target", async () => {
  const dir = await mkdtemp(join(realpathSync(tmpdir()), "atelier-owner-"));
  try {
    const owner = new OwnerSession();
    await owner.persistOwnerKey(dir, "fixture-instance");
    const path = join(dir, "owner-credentials.json");
    assert.equal((await stat(path)).mode & 0o777, 0o600);
    assert.equal(
      JSON.parse(await readFile(path, "utf8")).instance_id,
      "fixture-instance",
    );
    await rm(path);
    await symlink(join(dir, "outside"), path);
    await assert.rejects(owner.persistOwnerKey(dir, "fixture-instance"), {
      code: "INVALID_OWNER_KEY",
    });
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});
