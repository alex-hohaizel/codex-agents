import assert from "node:assert/strict";
import { EventEmitter } from "node:events";
import {
  access,
  mkdir,
  mkdtemp,
  realpath,
  rm,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { ImageGeneration } from "../../server/image-generation.mjs";

const threadId = "a156230a-9999-4eaa-ace1-123456789abc";
const otherThread = "b155130b-9999-4eaa-ace1-123456789abc";
const turnId = "image-turn";
const otherTurn = "unrelated-turn";
const prompt = "A blue enamel icon for the project status board";
const samplePng = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGOQiO0BAAGSAQLTeV5QAAAAAElFTkSuQmCC",
  "base64",
);

class ImageHost extends EventEmitter {
  calls = [];
  closed = 0;

  constructor({ account, savedPath, imageTurn = turnId, effort = "ultra" }) {
    super();
    this.account = account;
    this.savedPath = savedPath;
    this.imageTurn = imageTurn;
    this.effort = effort;
  }

  async connect() {
    return { auth_mode: this.account };
  }

  async rpc(method, params) {
    this.calls.push({ method, params });
    if (method === "thread/start")
      return {
        thread: { id: threadId, ephemeral: true },
        modelProvider: "openai",
        model: "gpt-6.2-sol",
        reasoningEffort: this.effort,
      };
    assert.equal(method, "turn/start");
    this.emit("notification", {
      method: "turn/completed",
      params: { threadId, turn: { id: otherTurn, status: "completed" } },
    });
    this.emit("notification", {
      method: "item/completed",
      params: {
        threadId: otherThread,
        turnId,
        item: {
          id: "foreign-image",
          type: "imageGeneration",
          status: "completed",
          savedPath: this.savedPath,
        },
      },
    });
    this.emit("notification", {
      method: "item/completed",
      params: {
        threadId,
        turnId: this.imageTurn,
        item: {
          id: "owned-image",
          type: "imageGeneration",
          status: "completed",
          savedPath: this.savedPath,
        },
      },
    });
    this.emit("notification", {
      method: "turn/completed",
      params: { threadId, turn: { id: turnId, status: "completed" } },
    });
    return { turn: { id: turnId } };
  }

  async close() {
    this.closed++;
  }
}

async function fixture(
  t,
  { account = "chatgpt", pathThread = threadId, imageTurn, effort } = {},
) {
  const root = await realpath(
    await mkdtemp(join(tmpdir(), "atelier-image-test-")),
  );
  t.after(() => rm(root, { recursive: true, force: true }));
  const generatedRoot = join(root, "generated_images");
  const imageFolder = join(generatedRoot, pathThread);
  await mkdir(imageFolder, { recursive: true });
  const savedPath = join(imageFolder, "image.png");
  await writeFile(savedPath, samplePng);
  const host = new ImageHost({ account, savedPath, imageTurn, effort });
  const generation = new ImageGeneration({
    generatedRoot,
    makeHost: () => host,
    featureEnabled: async () => true,
    timeoutMs: 100,
  });
  return { generation, host };
}

test("native image generation verifies and returns the PNG from its isolated thread", async (t) => {
  const { generation, host } = await fixture(t);
  const result = await generation.generate({ prompt });
  assert.equal(result.status, "completed");
  assert.equal(result.operation, "codex.image.generate");
  assert.equal(result.kind, "generated_image");
  assert.deepEqual(result.artifact, {
    filename: "atelier-image.png",
    content_type: "image/png",
    bytes: samplePng.length,
    base64: samplePng.toString("base64"),
  });
  const [start, turn] = host.calls;
  assert.equal(start.method, "thread/start");
  assert.equal(start.params.ephemeral, true);
  assert.equal(start.params.model, "gpt-6.2-sol");
  assert.equal(start.params.config.model_reasoning_effort, "ultra");
  assert.equal(start.params.permissions, "atelier-local");
  assert.equal(turn.params.threadId, threadId);
  assert.equal(turn.params.model, "gpt-6.2-sol");
  assert.equal(turn.params.effort, "ultra");
  assert.equal(turn.params.cwd, start.params.cwd);
  assert.ok(turn.params.input[0].text.endsWith(JSON.stringify(prompt)));
  assert.equal(host.closed, 1);
  await assert.rejects(access(start.params.cwd), { code: "ENOENT" });
});

test("a completed notification cannot substitute a PNG from another thread", async (t) => {
  const { generation, host } = await fixture(t, { pathThread: otherThread });
  await assert.rejects(generation.generate({ prompt }), {
    code: "INTEGRATION_RESPONSE_INVALID",
  });
  assert.equal(host.closed, 1);
});

test("an image event from a different turn cannot supply this generation", async (t) => {
  const { generation, host } = await fixture(t, { imageTurn: otherTurn });
  await assert.rejects(generation.generate({ prompt }), {
    code: "INTEGRATION_RESPONSE_INVALID",
  });
  assert.equal(host.closed, 1);
});

test("an API-key account is rejected before creating an image thread", async (t) => {
  const { generation, host } = await fixture(t, { account: "apiKey" });
  await assert.rejects(generation.generate({ prompt }), {
    code: "BILLING_AUTHORITY_REQUIRED",
  });
  assert.deepEqual(host.calls, []);
  assert.equal(host.closed, 1);
});

test("an unconfirmed native reasoning effort blocks the image turn", async (t) => {
  for (const effort of ["high", null]) {
    const { generation, host } = await fixture(t, { effort });
    await assert.rejects(generation.generate({ prompt }), {
      code: "MODEL_EFFORT_UNAVAILABLE",
    });
    assert.deepEqual(host.calls.map(({ method }) => method), ["thread/start"]);
    assert.equal(host.closed, 1);
  }
});
