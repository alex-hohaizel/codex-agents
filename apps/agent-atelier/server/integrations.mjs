import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { runtimeEnvironment } from "./environment.mjs";
import {
  containsObviousCredential,
  fail,
  now,
  parseStrictJson,
  redact,
  ServiceError,
  text,
} from "./utils.mjs";

const executeFile = promisify(execFile);
const GITHUB_REPOSITORY_READ = "github.repository.read";
const repositoryNamePattern =
  /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\/[A-Za-z0-9_.-]{1,100}$/;
const OPENVERSE_ORIGIN = "https://api.openverse.org";
const MEDIA_RESULT_LIMIT = 10;
const MEDIA_RESPONSE_LIMIT = 1024 * 1024;
const mediaOperations = new Map([
  [
    "openverse.images.search",
    { endpoint: "images", medium: "image", label: "Find images" },
  ],
  [
    "openverse.audio.search",
    { endpoint: "audio", medium: "audio", label: "Find audio" },
  ],
]);

function displayText(value, limit, fallback = null) {
  if (typeof value !== "string") return fallback;
  return (
    redact(value)
      .replace(/[\u0000-\u001f\u007f]/g, " ")
      .trim()
      .slice(0, limit) || fallback
  );
}

function inventoryIdentifier(value) {
  return (
    typeof value === "string" &&
    /^\w[\w.@:/+-]{0,239}$/.test(value) &&
    !value.includes("://") &&
    !containsObviousCredential(value)
  );
}

function publicLink(value) {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (
      url.protocol !== "https:" ||
      url.username ||
      url.password ||
      [...url.searchParams.keys()].some((key) =>
        /token|secret|password|signature|credential|key/i.test(key),
      )
    )
      return null;
    return url.href;
  } catch {
    return null;
  }
}

function handoff(name, kind, locale) {
  const subject = kind === "media" ? "media" : "plugin";
  const text =
    locale === "uk"
      ? `У цьому чаті Codex перевір, чи доступний ${name} для моєї задачі. Перед зовнішньою дією звір точну операцію, дані, дозволи й можливі витрати. Після дії покажи фактичний результат і джерело.`
      : `In this Codex chat, check whether ${name} is available for my ${subject} task. Before an external action, verify the exact operation, data, permissions, and any cost. After the action, show the actual result and its source.`;
  return { kind: "codex", target: name, text };
}

function catalogEntry({
  kind,
  id,
  name,
  status,
  description = null,
  version = null,
  locale,
}) {
  const target = kind === "media" ? name : id;
  return {
    kind,
    id,
    name,
    description,
    status,
    version,
    actions: [],
    handoff: handoff(target, kind, locale),
  };
}

async function readConfiguredMcp(executable, cwd) {
  const { stdout } = await executeFile(executable, ["mcp", "list", "--json"], {
    cwd,
    env: runtimeEnvironment(),
    timeout: 8000,
    maxBuffer: 2 * 1024 * 1024,
  });
  return parseStrictJson(stdout);
}

function githubOptions(cwd, timeout) {
  return {
    cwd,
    timeout,
    maxBuffer: 32 * 1024,
    env: {
      ...runtimeEnvironment(),
      GH_PROMPT_DISABLED: "1",
      GH_NO_UPDATE_NOTIFIER: "1",
      GH_NO_EXTENSION_UPDATE_NOTIFIER: "1",
    },
  };
}

async function readGithubRepository(executable, cwd, repository) {
  try {
    const { stdout } = await executeFile(
      executable,
      [
        "api",
        "--hostname",
        "github.com",
        "--method",
        "GET",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        `repos/${repository}`,
        "--jq",
        "{full_name,default_branch,visibility,archived}",
      ],
      githubOptions(cwd, 12000),
    );
    return parseStrictJson(stdout, 32 * 1024);
  } catch (error) {
    const diagnostic = typeof error.stderr === "string" ? error.stderr : "";
    if (error.code === "ENOENT")
      throw new ServiceError(
        "INTEGRATION_UNAVAILABLE",
        "GitHub CLI is unavailable on this Mac",
        503,
      );
    if (error.code === 4 || /HTTP 401/.test(diagnostic))
      throw new ServiceError(
        "INTEGRATION_AUTH_REQUIRED",
        "Sign in to GitHub CLI to read this repository",
        409,
      );
    if (/HTTP 404/.test(diagnostic))
      throw new ServiceError(
        "INTEGRATION_TARGET_UNAVAILABLE",
        "GitHub could not find this repository with the current access",
        404,
      );
    if (/HTTP 429|rate limit/i.test(diagnostic))
      throw new ServiceError(
        "INTEGRATION_RATE_LIMITED",
        "GitHub rate limit reached. Try again later.",
        429,
      );
    throw new ServiceError(
      "INTEGRATION_UNAVAILABLE",
      "GitHub CLI could not read the repository with the current access",
      502,
    );
  }
}

function githubCatalog(available, locale) {
  const entry = catalogEntry({
    kind: "connector",
    id: "github-cli",
    name: "GitHub CLI",
    status: available ? "ready" : "unverified",
    locale,
  });
  if (!available)
    return { ...entry, handoff: handoff("GitHub", "connector", locale) };
  return {
    ...entry,
    handoff: null,
    actions: [
      {
        id: GITHUB_REPOSITORY_READ,
        label: "Read repository metadata",
        inputs: [
          {
            name: "repository",
            label: "Repository",
            type: "text",
            required: true,
            max_length: 140,
          },
        ],
      },
    ],
  };
}

function operationInput(input, field, min, max) {
  fail(
    input &&
      typeof input === "object" &&
      Object.keys(input).length === 1 &&
      Object.hasOwn(input, field),
    "INVALID_INPUT",
    `${field} is the only input for this read operation`,
  );
  const value = text(input[field], field, min, max);
  fail(
    !containsObviousCredential(value),
    "INVALID_INPUT",
    "Use input without credentials",
  );
  return value;
}

async function inventory(source, load, project) {
  try {
    const { entries, partial = false } = project(await load());
    return { source, status: partial ? "partial" : "available", entries };
  } catch {
    return { source, status: "unavailable", entries: [] };
  }
}

function plugins(response, locale) {
  if (
    !Array.isArray(response?.marketplaces) ||
    !Array.isArray(response?.marketplaceLoadErrors)
  )
    throw new Error("Invalid plugin catalog");
  const entries = new Map();
  let partial = response.marketplaceLoadErrors.length > 0;
  for (const marketplace of response.marketplaces) {
    if (!Array.isArray(marketplace?.plugins)) {
      partial = true;
      continue;
    }
    for (const plugin of marketplace.plugins) {
      if (plugin?.installed !== true) continue;
      if (!inventoryIdentifier(plugin.id)) {
        partial = true;
        continue;
      }
      entries.set(
        plugin.id,
        catalogEntry({
          kind: "plugin",
          id: plugin.id,
          name: displayText(
            plugin.interface?.displayName ?? plugin.name,
            120,
            plugin.id,
          ),
          status:
            plugin.enabled === true &&
            plugin.availability !== "DISABLED_BY_ADMIN"
              ? "native_only"
              : "disabled",
          description: displayText(plugin.interface?.shortDescription, 500),
          version: displayText(plugin.localVersion ?? plugin.version, 100),
          locale,
        }),
      );
    }
  }
  return { entries: [...entries.values()], partial };
}

function connectors(response, locale) {
  if (!Array.isArray(response?.apps))
    throw new Error("Invalid connector catalog");
  const entries = response.apps
    .filter((app) => inventoryIdentifier(app?.id))
    .map((app) =>
      catalogEntry({
        kind: "connector",
        id: app.id,
        name: displayText(app.runtimeName, 120, app.id),
        status:
          app.enabled === false
            ? "disabled"
            : app.callable === true
              ? "native_only"
              : "unverified",
        locale,
      }),
    );
  return { entries, partial: entries.length !== response.apps.length };
}

function mcpServers(response, locale) {
  if (!Array.isArray(response))
    throw new Error("Invalid configured MCP catalog");
  const entries = response
    .filter((row) => inventoryIdentifier(row?.name))
    .map((row) =>
      catalogEntry({
        kind: "mcp",
        id: row.name,
        name: row.name,
        status: row.enabled === false ? "disabled" : "unverified",
        locale,
      }),
    );
  return { entries, partial: entries.length !== response.length };
}

function mediaEntries(locale) {
  return [
    {
      ...catalogEntry({
        kind: "media",
        id: "openverse",
        name: "Openverse",
        status: "ready",
        locale,
      }),
      handoff: null,
      actions: [...mediaOperations].map(([id, { label }]) => ({
        id,
        label,
        inputs: [
          {
            name: "query",
            label: "Search terms",
            type: "text",
            required: true,
            max_length: 120,
          },
        ],
      })),
    },
    catalogEntry({
      kind: "media",
      id: "native-media",
      name: "Codex",
      status: "native_only",
      locale,
    }),
  ];
}

function mediaHit(hit, medium) {
  if (!hit || hit.mature === true || !inventoryIdentifier(hit.id)) return null;
  return {
    id: hit.id,
    title: displayText(hit.title, 240),
    creator: displayText(hit.creator, 160),
    license: displayText(
      [hit.license, hit.license_version]
        .filter((value) => typeof value === "string")
        .join(" "),
      80,
    ),
    license_url: publicLink(hit.license_url),
    source_url: publicLink(hit.foreign_landing_url),
    source: displayText(hit.source, 100),
    medium,
  };
}

async function readMediaJson(response) {
  const body = response.body;
  fail(
    body &&
      /^application\/json(?:\s*;|$)/i.test(
        response.headers.get("content-type") ?? "",
      ),
    "INTEGRATION_RESPONSE_INVALID",
    "Openverse did not return a JSON search result",
    502,
  );
  const chunks = [];
  let size = 0;
  for await (const chunk of body) {
    size += chunk.byteLength;
    fail(
      size <= MEDIA_RESPONSE_LIMIT,
      "INTEGRATION_RESPONSE_INVALID",
      "Openverse search result exceeded the size limit",
      502,
    );
    chunks.push(chunk);
  }
  try {
    return parseStrictJson(
      Buffer.concat(chunks).toString("utf8"),
      MEDIA_RESPONSE_LIMIT,
    );
  } catch {
    throw new ServiceError(
      "INTEGRATION_RESPONSE_INVALID",
      "Openverse returned invalid search data",
      502,
    );
  }
}

export class IntegrationsManager {
  constructor({
    dataDir,
    nativeRpc,
    executable = "codex",
    readMcpInventory,
    fetchImpl = fetch,
    githubExecutable = "gh",
    githubAvailable,
    readRepository,
  } = {}) {
    this.dataDir = dataDir;
    this.nativeRpc = nativeRpc;
    this.readMcpInventory =
      readMcpInventory ?? ((cwd) => readConfiguredMcp(executable, cwd));
    this.fetch = fetchImpl;
    this.githubAvailable =
      githubAvailable ??
      (async () => {
        try {
          await executeFile(
            githubExecutable,
            ["--version"],
            githubOptions(dataDir, 4000),
          );
          return true;
        } catch {
          return false;
        }
      });
    this.readRepository =
      readRepository ??
      ((name) => readGithubRepository(githubExecutable, dataDir, name));
  }

  async list({ cwd, locale } = {}) {
    const [pluginCatalog, connectorCatalog, configuredMcp, githubAvailable] =
      await Promise.all([
        inventory(
          "codex_plugins",
          () => this.nativeRpc("plugin/installed", cwd ? { cwds: [cwd] } : {}),
          (result) => plugins(result, locale),
        ),
        inventory(
          "codex_connectors",
          () => this.nativeRpc("app/installed", { forceRefresh: false }),
          (result) => connectors(result, locale),
        ),
        inventory(
          "codex_mcp",
          () => this.readMcpInventory(cwd ?? this.dataDir),
          (result) => mcpServers(result, locale),
        ),
        this.githubAvailable(),
      ]);
    const sources = [pluginCatalog, connectorCatalog, configuredMcp];
    return {
      checked_at: now(),
      sources: [
        ...sources.map(({ source, status }) => ({ source, status })),
        { source: "openverse", status: "configured" },
        {
          source: "github_cli",
          status: githubAvailable ? "configured" : "unavailable",
        },
      ],
      entries: [
        ...sources.flatMap(({ entries }) => entries),
        ...mediaEntries(locale),
        githubCatalog(githubAvailable, locale),
      ],
    };
  }

  async inspect({ kind, id, cwd, locale } = {}) {
    fail(
      ["plugin", "connector", "mcp", "media"].includes(kind) &&
        inventoryIdentifier(id),
      "INVALID_INPUT",
      "Choose an integration from the current catalog",
    );
    const { entries, sources } = await this.list({ cwd, locale });
    let entry = entries.find((item) => item.kind === kind && item.id === id);
    fail(
      entry,
      "NOT_FOUND",
      "Integration is absent from the current catalog",
      404,
    );
    const source = {
      plugin: "codex_plugins",
      connector: entry.id === "github-cli" ? "github_cli" : "codex_connectors",
      mcp: "codex_mcp",
      media: entry.id === "openverse" ? "openverse" : "codex",
    }[entry.kind];
    let tools = [];
    let status =
      sources.find((item) => item.source === source)?.status ?? "configured";
    if (source === "codex_connectors") {
      try {
        const result = await this.nativeRpc("app/read", {
          appIds: [entry.id],
          includeTools: true,
        });
        const app =
          Array.isArray(result?.apps) &&
          result.apps.find((row) => row?.id === entry.id);
        if (!app) throw new Error("Connector metadata is unavailable");
        const name = displayText(app.name, 120, entry.name);
        entry = {
          ...entry,
          name,
          description: displayText(app.description, 500),
        };
        tools = (Array.isArray(app.toolSummaries) ? app.toolSummaries : [])
          .filter((row) => inventoryIdentifier(row?.name))
          .map((row) => ({
            name: row.name,
            title: displayText(row.title, 120, row.name),
            description: displayText(row.description, 500),
            enabled: row.isEnabled === true,
            read_only: row.isReadOnly === true,
          }));
      } catch {
        status = "partial";
      }
    }
    return { checked_at: now(), entry, tools, source, status };
  }

  async run(request) {
    fail(
      request &&
        typeof request === "object" &&
        Object.keys(request).length === 2 &&
        Object.hasOwn(request, "operation") &&
        Object.hasOwn(request, "arguments"),
      "INVALID_INPUT",
      "An integration read requires an operation and its arguments",
    );
    const { operation, arguments: input } = request;
    if (operation === GITHUB_REPOSITORY_READ)
      return this.#githubRepository(input);
    const route = mediaOperations.get(operation);
    fail(
      route,
      "INTEGRATION_OPERATION_UNAVAILABLE",
      "Choose a supported read operation or continue in Codex",
      409,
    );
    const query = operationInput(input, "query", 2, 120);
    const url = new URL(`/v1/${route.endpoint}/`, OPENVERSE_ORIGIN);
    url.searchParams.set("q", query);
    url.searchParams.set("page_size", String(MEDIA_RESULT_LIMIT));
    url.searchParams.set("mature", "false");
    let response;
    try {
      response = await this.fetch(url, {
        method: "GET",
        redirect: "error",
        credentials: "omit",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "User-Agent": "Agent-Atelier/Openverse-Search",
        },
        signal: AbortSignal.timeout(15000),
      });
    } catch {
      throw new ServiceError(
        "INTEGRATION_UNAVAILABLE",
        "Openverse could not be reached from this host",
        503,
      );
    }
    if (!response.ok) {
      await response.body?.cancel().catch(() => {});
      if (response.status === 429)
        throw new ServiceError(
          "INTEGRATION_RATE_LIMITED",
          "Openverse rate limit reached. Try again later.",
          429,
        );
      throw new ServiceError(
        "INTEGRATION_UNAVAILABLE",
        "Openverse did not complete the search",
        502,
      );
    }
    let data;
    try {
      data = await readMediaJson(response);
    } catch (error) {
      if (error instanceof ServiceError) throw error;
      throw new ServiceError(
        "INTEGRATION_UNAVAILABLE",
        "Openverse search ended before returning a result",
        503,
      );
    }
    fail(
      Array.isArray(data?.results),
      "INTEGRATION_RESPONSE_INVALID",
      "Openverse search results are missing",
      502,
    );
    const content = data.results
      .slice(0, MEDIA_RESULT_LIMIT)
      .map((hit) => mediaHit(hit, route.medium))
      .filter(Boolean);
    return {
      kind: "media",
      operation,
      checked_at: now(),
      provider: "Openverse",
      tool: `${route.endpoint}.search`,
      status: "completed",
      content,
      count: content.length,
    };
  }

  async #githubRepository(input) {
    const name = operationInput(input, "repository", 3, 140);
    const slug = name.split("/")[1];
    fail(
      repositoryNamePattern.test(name) && slug !== "." && slug !== "..",
      "INVALID_INPUT",
      "Enter a GitHub repository as owner/repository",
    );
    const result = await this.readRepository(name);
    fail(
      typeof result?.full_name === "string" &&
        result.full_name.toLowerCase() === name.toLowerCase(),
      "INTEGRATION_TARGET_MISMATCH",
      "GitHub returned a different repository. Enter its current owner and name.",
      409,
    );
    return {
      kind: "repository",
      operation: GITHUB_REPOSITORY_READ,
      checked_at: now(),
      provider: "GitHub CLI",
      tool: "repository.read",
      status: "completed",
      repository: {
        name: result.full_name,
        default_branch: displayText(result.default_branch, 240),
        visibility: ["public", "private", "internal"].includes(
          result.visibility,
        )
          ? result.visibility
          : null,
        archived: typeof result.archived === "boolean" ? result.archived : null,
        source_url: `https://github.com/${result.full_name}`,
      },
    };
  }
}
