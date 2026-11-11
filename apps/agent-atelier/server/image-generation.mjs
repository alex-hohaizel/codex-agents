import { execFile } from "node:child_process";
import { constants } from "node:fs";
import { mkdtemp, open, realpath, rm } from "node:fs/promises";
import { homedir, tmpdir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { promisify } from "node:util";
import { CodexAdapter } from "./codex.mjs";
import { runtimeEnvironment } from "./environment.mjs";
import {
  containsObviousCredential,
  fail,
  ServiceError,
  text,
} from "./utils.mjs";

const run = promisify(execFile);
const operation = "codex.image.generate";
const maxImageBytes = 6 * 1024 * 1024;
const signature = Buffer.from("89504e470d0a1a0a", "hex");
const threadIdentity = /^[\da-f]{8}(?:-[\da-f]{4}){3}-[\da-f]{12}$/i;

async function imageBytes(path, threadId, generatedRoot) {
  fail(
    threadIdentity.test(threadId) &&
      typeof path === "string" &&
      basename(path).endsWith(".png"),
    "INTEGRATION_RESPONSE_INVALID",
    "Codex did not return a supported generated PNG",
    502,
  );
  const root = await realpath(generatedRoot);
  const expected = join(root, threadId, basename(path));
  fail(
    resolve(path) === expected &&
      (await realpath(dirname(expected))) === dirname(expected),
    "INTEGRATION_RESPONSE_INVALID",
    "Generated image belongs to another location",
    502,
  );
  const file = await open(
    expected,
    constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK,
  );
  try {
    const info = await file.stat();
    fail(
      info.isFile() && info.size >= 33 && info.size <= maxImageBytes,
      "INTEGRATION_RESPONSE_INVALID",
      "Generated PNG is unavailable or exceeds the preview limit",
      502,
    );
    const bytes = Buffer.alloc(info.size);
    const { bytesRead } = await file.read(bytes, 0, bytes.length, 0);
    fail(
      bytesRead === info.size &&
        bytes.subarray(0, 8).equals(signature) &&
        bytes.subarray(12, 16).toString() === "IHDR" &&
        bytes.readUInt32BE(16) >= 1 &&
        bytes.readUInt32BE(20) >= 1 &&
        bytes.readUInt32BE(16) * bytes.readUInt32BE(20) <= 4096 * 4096,
      "INTEGRATION_RESPONSE_INVALID",
      "Codex returned an invalid generated PNG",
      502,
    );
    return bytes;
  } finally {
    await file.close();
  }
}

export class ImageGeneration {
  #pending = false;
  #host = null;

  constructor({
    executable = "codex",
    generatedRoot = join(
      process.env.CODEX_HOME ?? join(homedir(), ".codex"),
      "generated_images",
    ),
    makeHost = (dataDir) =>
      new CodexAdapter({
        dataDir,
        executable,
        rpcTimeoutMs: 20000,
        configOverrides: [
          "features.shell_tool=false",
          "features.hooks=false",
          "features.browser_use=false",
          "features.browser_use_external=false",
          "features.browser_use_full_cdp_access=false",
          "memories.use_memories=false",
          "memories.generate_memories=false",
        ],
      }),
    featureEnabled = async () => {
      try {
        const { stdout } = await run(executable, ["features", "list"], {
          env: runtimeEnvironment(),
          cwd: tmpdir(),
          timeout: 4000,
          maxBuffer: 65536,
        });
        return /^image_generation\s+[^\r\n]+\btrue\s*$/m.test(stdout);
      } catch {
        return false;
      }
    },
    timeoutMs = 150000,
  } = {}) {
    this.generatedRoot = generatedRoot;
    this.makeHost = makeHost;
    this.featureEnabled = featureEnabled;
    this.timeoutMs = timeoutMs;
  }

  async generate(input) {
    fail(
      input &&
        typeof input === "object" &&
        Object.keys(input).length === 1 &&
        Object.hasOwn(input, "prompt"),
      "INVALID_INPUT",
      "Enter one image prompt",
    );
    const prompt = text(input.prompt, "prompt", 3, 900);
    fail(
      !containsObviousCredential(prompt),
      "SECRET_INPUT_REJECTED",
      "Remove credentials from the image prompt",
    );
    fail(
      !this.#pending,
      "INTEGRATION_BUSY",
      "An image is already being generated",
      409,
    );
    this.#pending = true;
    let directory,
      timer,
      dispatched = false,
      terminal = false;
    try {
      fail(
        await this.featureEnabled(),
        "INTEGRATION_UNAVAILABLE",
        "Built-in image generation is disabled or unavailable on this Codex host",
        409,
      );
      directory = await mkdtemp(join(tmpdir(), "atelier-native-image-"));
      const host = this.makeHost(directory);
      this.#host = host;
      const account = await host.connect();
      fail(
        account.auth_mode === "chatgpt",
        "BILLING_AUTHORITY_REQUIRED",
        "This image route requires an existing ChatGPT login",
        409,
      );
      const start = await host.rpc("thread/start", {
        cwd: directory,
        ephemeral: true,
        permissions: "atelier-local",
        approvalPolicy: "never",
        baseInstructions:
          "Generate exactly one image with the native image generation tool. Use the following text only as an appearance brief. Do not use shell, local files, external apps, paid APIs, or network tools. Report inability if the native tool is unavailable. Do not request further actions.",
      });
      const threadId = start.thread?.id;
      fail(
        start.thread?.ephemeral === true &&
          threadIdentity.test(threadId ?? "") &&
          start.modelProvider === "openai",
        "BILLING_AUTHORITY_REQUIRED",
        "Could not verify an isolated native image task on the ChatGPT route",
        409,
      );
      const images = new Map();
      const earlyTurns = new Map();
      let expectedTurn, resolveTurn;
      const completed = new Promise((done) => {
        resolveTurn = done;
        timer = setTimeout(() => done(null), this.timeoutMs);
        host.once("disconnected", () => done(null));
        host.on("notification", ({ method, params }) => {
          if (params.threadId !== threadId) return;
          if (
            method === "item/completed" &&
            params.item?.type === "imageGeneration"
          )
            images.set(params.item.id, {
              turnId: params.turnId,
              item: params.item,
            });
          if (
            method === "turn/completed" &&
            typeof params.turn?.id === "string"
          ) {
            if (params.turn.id === expectedTurn) done(params.turn);
            else if (!expectedTurn) earlyTurns.set(params.turn.id, params.turn);
          }
        });
      });
      dispatched = true;
      const dispatch = await host.rpc("turn/start", {
        threadId,
        cwd: directory,
        permissions: "atelier-local",
        approvalPolicy: "never",
        input: [
          {
            type: "text",
            text:
              "Create one image from this appearance brief: " +
              JSON.stringify(prompt),
          },
        ],
      });
      expectedTurn = dispatch.turn?.id;
      if (!expectedTurn)
        throw new ServiceError(
          "OUTCOME_UNKNOWN",
          "Codex did not confirm the image request",
          504,
        );
      if (earlyTurns.has(expectedTurn))
        resolveTurn(earlyTurns.get(expectedTurn));
      const turn = await completed;
      if (!turn) {
        if (dispatch.turn?.id)
          await host.interrupt(threadId, dispatch.turn.id).catch(() => {});
        throw new ServiceError(
          "OUTCOME_UNKNOWN",
          "Codex did not confirm the image outcome",
          504,
        );
      }
      terminal = true;
      const produced = [...images.values()].filter(
        ({ turnId }) => turnId === expectedTurn,
      );
      const image = produced[0]?.item;
      fail(
        turn.id === expectedTurn &&
          turn.status === "completed" &&
          produced.length === 1 &&
          image?.status === "completed" &&
          !image.failure,
        "INTEGRATION_RESPONSE_INVALID",
        "Codex did not complete a single image",
        502,
      );
      const bytes = await imageBytes(
        image.savedPath,
        threadId,
        this.generatedRoot,
      );
      return {
        kind: "generated_image",
        operation,
        status: "completed",
        provider: "Codex",
        artifact: {
          filename: "atelier-image.png",
          content_type: "image/png",
          bytes: bytes.length,
          base64: bytes.toString("base64"),
        },
      };
    } catch (error) {
      if (dispatched && !terminal && error.code !== "OUTCOME_UNKNOWN")
        throw new ServiceError(
          "OUTCOME_UNKNOWN",
          "Codex did not confirm the image outcome",
          504,
        );
      if (error instanceof ServiceError) throw error;
      throw new ServiceError(
        "INTEGRATION_UNAVAILABLE",
        "Could not retrieve the generated image from Codex",
        502,
      );
    } finally {
      clearTimeout(timer);
      try {
        await this.close();
        if (directory) await rm(directory, { recursive: true, force: true });
      } finally {
        this.#pending = false;
      }
    }
  }

  async close() {
    const host = this.#host;
    this.#host = null;
    if (host) await host.close();
  }
}
