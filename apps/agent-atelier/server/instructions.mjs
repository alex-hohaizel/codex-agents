import {
  lstat,
  readFile,
  realpath,
  mkdir,
  symlink,
  readlink,
  readdir,
} from "node:fs/promises";
import { join, dirname, resolve, basename } from "node:path";
import { homedir } from "node:os";
import { digest, sha, fail, ServiceError } from "./utils.mjs";
const defaults = {
  project_root_markers: [".git"],
  project_doc_fallback_filenames: [],
  project_doc_max_bytes: 32768,
};
const names = (values, label) => {
  fail(
    Array.isArray(values) &&
      values.length <= 20 &&
      values.every(
        (value) =>
          typeof value === "string" &&
          value.length > 0 &&
          value.length <= 120 &&
          !/[\\/\0]/.test(value) &&
          ![".", ".."].includes(value),
      ),
    "CAPABILITY_UNVERIFIED",
    "Unsupported native instruction " + label,
    409,
  );
  return [...new Set(values)];
};
export function instructionSettings(config = {}, { normalized = false } = {}) {
  const markers = names(
    config.project_root_markers ?? defaults.project_root_markers,
    "root marker set",
  );
  const fallback = names(
    config.project_doc_fallback_filenames ?? [],
    "fallback set",
  );
  fail(
    fallback.every((name) =>
      [
        "AGENTS.md",
        "AGENTS.override.md",
        "TEAM_GUIDE.md",
        ".agents.md",
      ].includes(name),
    ),
    "CAPABILITY_UNVERIFIED",
    "Configured fallback is not a reviewed governing instruction filename; no private/arbitrary-file alias will be created",
    409,
  );
  const budget = config.project_doc_max_bytes ?? defaults.project_doc_max_bytes;
  fail(
    Number.isSafeInteger(budget) && budget > 0 && budget <= 256 * 1024,
    "CAPABILITY_UNVERIFIED",
    "Native instruction loading is disabled or outside the supported bounded budget",
    409,
  );
  const provider = normalized
    ? config.native_route?.provider
    : (config.model_provider ?? "openai");
  const customProvider = normalized
    ? config.native_route?.custom_provider
    : Object.hasOwn(config.model_providers ?? {}, provider);
  const base =
    config.model_providers?.[provider]?.base_url ??
    config.openai_base_url ??
    config.chatgpt_base_url;
  // config/read materializes this packaged default even without an override.
  // Accept only the exact native ChatGPT URL, never merely a matching host.
  const defaultChatgpt =
    config.chatgpt_base_url === undefined ||
    config.chatgpt_base_url === null ||
    config.chatgpt_base_url === "https://chatgpt.com/backend-api/";
  const override = normalized
    ? config.native_route?.base_url_override
    : config.model_providers?.[provider]?.base_url != null ||
      config.openai_base_url != null ||
      !defaultChatgpt;
  let host = normalized ? (config.native_route?.base_url_host ?? null) : null;
  if (!normalized && base)
    try {
      host = new URL(base).hostname;
    } catch {
      host = "invalid";
    }
  fail(
    typeof customProvider === "boolean" && typeof override === "boolean",
    "CAPABILITY_UNVERIFIED",
    "Native provider route metadata is incomplete",
    409,
  );
  fail(
    provider === "openai" && !customProvider && !override,
    "BILLING_AUTHORITY_REQUIRED",
    "Custom provider/base URL requires a separately reviewed billing/resource route; existing ChatGPT access alone is insufficient",
    409,
  );
  return {
    native_route: {
      provider,
      custom_provider: customProvider,
      base_url_override: override,
      base_url_host: host,
    },
    project_root_markers: markers,
    project_doc_fallback_filenames: fallback,
    project_doc_max_bytes: budget,
  };
}
export class InstructionsManager {
  constructor({
    dataDir,
    codexHome = process.env.CODEX_HOME ?? join(homedir(), ".codex"),
  } = {}) {
    this.dataDir = dataDir;
    this.codexHome = resolve(codexHome);
  }
  async pin(path) {
    let info;
    try {
      info = await lstat(path);
    } catch (error) {
      if (error.code === "ENOENT") return { path, present: false };
      throw error;
    }
    fail(
      info.isFile() &&
        !info.isSymbolicLink() &&
        (await realpath(path)) === path,
      "SOURCE_DRIFT",
      "Governing instruction must be an unlinked regular file: " +
        basename(path),
      409,
    );
    fail(
      info.size <= 64 * 1024,
      "CAPACITY_LIMIT",
      "Governing instruction exceeds the bounded file size",
      409,
    );
    const bytes = await readFile(path);
    fail(
      bytes.length === info.size,
      "SOURCE_DRIFT",
      "Instruction changed while pinning",
      409,
    );
    new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    return {
      path,
      present: true,
      sha256: sha(bytes),
      bytes: bytes.length,
      nonempty: bytes.toString("utf8").trim().length > 0,
    };
  }
  async capture(root, settings = instructionSettings()) {
    settings = instructionSettings(settings, { normalized: true });
    root = await realpath(root);
    const markers = [];
    let projectRoot = root,
      found = false;
    if (settings.project_root_markers.length)
      for (let cursor = root, depth = 0; depth < 100; depth++) {
        for (const name of settings.project_root_markers) {
          const path = join(cursor, name);
          let kind = "absent";
          try {
            const info = await lstat(path);
            kind = info.isDirectory()
              ? "directory"
              : info.isFile()
                ? "file"
                : info.isSymbolicLink()
                  ? "link"
                  : "special";
          } catch (error) {
            if (error.code !== "ENOENT") throw error;
          }
          markers.push({ path, kind });
          if (kind !== "absent") {
            projectRoot = cursor;
            found = true;
            break;
          }
        }
        if (found || dirname(cursor) === cursor) break;
        cursor = dirname(cursor);
      }
    const dirs = [];
    for (let cursor = root; ; cursor = dirname(cursor)) {
      dirs.push(cursor);
      if (cursor === projectRoot) break;
    }
    dirs.reverse();
    const candidates = [],
      sources = [];
    const filenames = [
      ...new Set([
        "AGENTS.override.md",
        "AGENTS.md",
        ...settings.project_doc_fallback_filenames,
      ]),
    ];
    for (const directory of [this.codexHome, ...dirs]) {
      let selected = false;
      for (const filename of directory === this.codexHome
        ? ["AGENTS.override.md", "AGENTS.md"]
        : filenames) {
        const pin = await this.pin(join(directory, filename));
        candidates.push(pin);
        if (pin.present && !selected) {
          sources.push({
            ...pin,
            scope: directory === this.codexHome ? "global" : "project",
          });
          selected = true;
        }
      }
    }
    const projectBytes = sources
      .filter((row) => row.scope === "project")
      .reduce((sum, row) => sum + row.bytes, 0);
    fail(
      projectBytes <= settings.project_doc_max_bytes,
      "CAPACITY_LIMIT",
      "Governing project instructions exceed native loading budget; retain full instructions and review the budget before dispatch",
      409,
    );
    const result = {
      schema_version: "atelier.governing-instructions/1",
      root,
      codex_home: this.codexHome,
      settings,
      markers,
      candidates,
      sources,
      project_bytes: projectBytes,
      native_consumption:
        "requires actual instructionSources and post-bootstrap pin verification",
    };
    result.sha256 = digest(result);
    return result;
  }
  async verify(manifest, settings = manifest?.settings) {
    fail(
      manifest?.schema_version === "atelier.governing-instructions/1",
      "TASK_NOT_READY",
      "This task has no current governing-instruction pins; prepare a new capsule",
      409,
    );
    const current = await this.capture(manifest.root, settings);
    fail(
      current.sha256 === manifest.sha256,
      "SOURCE_DRIFT",
      "Governing instruction bytes, precedence, candidate set or native settings changed; prepare again",
      409,
    );
    return current;
  }
  async aliases(manifest, taskId) {
    await this.verify(manifest);
    fail(
      /^task_[a-f0-9-]{36}$/.test(taskId),
      "INVALID_INPUT",
      "Invalid instruction alias task identity",
    );
    const parent = join(this.dataDir, "instruction-aliases"),
      directory = join(parent, taskId);
    await mkdir(directory, { recursive: true, mode: 0o700 });
    fail(
      (await realpath(parent)) === parent &&
        (await realpath(directory)) === directory,
      "SOURCE_DRIFT",
      "Instruction alias directory identity changed",
      409,
    );
    const aliases = [];
    for (const source of manifest.sources) {
      const alias = join(directory, sha(source.path) + ".md");
      try {
        await symlink(source.path, alias);
      } catch (error) {
        if (error.code !== "EEXIST") throw error;
      }
      const info = await lstat(alias);
      fail(
        info.isSymbolicLink() &&
          (await readlink(alias)) === source.path &&
          (await realpath(alias)) === source.path,
        "SOURCE_DRIFT",
        "Instruction alias target changed",
        409,
      );
      const current = await this.pin(source.path);
      fail(
        current.present && current.sha256 === source.sha256,
        "SOURCE_DRIFT",
        "Instruction alias source changed",
        409,
      );
      aliases.push({ path: alias, target: source.path, sha256: source.sha256 });
    }
    const actual = await readdir(directory);
    fail(
      actual.length === aliases.length &&
        actual.every((name) =>
          aliases.some((row) => basename(row.path) === name),
        ),
      "SOURCE_DRIFT",
      "Unexpected instruction alias entries",
      409,
    );
    return aliases;
  }
  verifyLoaded(manifest, observed) {
    fail(
      Array.isArray(observed),
      "CAPABILITY_UNVERIFIED",
      "Native host did not expose loaded instruction sources",
      409,
    );
    const expected = manifest.sources
        .filter((row) => row.nonempty)
        .map((row) => row.path),
      actual = observed.map((path) => resolve(path));
    fail(
      expected.every((path) => actual.includes(path)) &&
        actual.every((path) => expected.includes(path)),
      "CAPABILITY_UNVERIFIED",
      "Native loaded instruction set differs from pinned governing sources; no model turn dispatched",
      409,
    );
  }
}
