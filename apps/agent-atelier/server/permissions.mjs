import { dirname, relative, resolve } from "node:path";
import { homedir } from "node:os";
import { runtimeEnvironment } from "./environment.mjs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fail, parseStrictJson, ServiceError } from "./utils.mjs";
const run = promisify(execFile);

export function localProfile(
  scope = "read-only",
  allowedPaths = [],
  readRoots = [],
  projectRoot = null,
  denyRoots = [],
) {
  const workspace = { ".": "read" };
  if (scope === "workspace-write")
    for (const path of allowedPaths)
      workspace[
        path === "." || path === "" ? "." : path.replaceAll("\\", "/")
      ] = "write";
  for (const path of [
    ".git",
    ".agents",
    ".codex",
    ".agent-foundry",
    ".appatelier",
    ".chatbotatelier",
    ".chatbot-atelier",
    ".gameatelier",
    ".atelier",
  ])
    workspace[path] = "read";
  workspace[".aws"] = "deny";
  // Global basename denies preserve the same sensitive-file boundary without
  // interpolating literal project paths into globs (Codex 0.166 treats '[' as
  // pattern syntax when materializing scoped glob rules).
  const secretDenies = Object.fromEntries(
    [
      "/**/.env*",
      "/**/*.pem",
      "/**/*.key",
      "/**/auth.json",
      "/**/owner-credentials.json",
      "/**/credentials*",
      "/**/id_rsa",
      "/**/id_ed25519",
      "/**/.ssh",
      "/**/.aws",
      "/**/*.p12",
      "/**/*.pfx",
    ].map((pattern) => [pattern, "deny"]),
  );
  for (const path of readRoots)
    fail(
      !/[?*\[\]]/.test(path),
      "CAPABILITY_UNVERIFIED",
      "The installed Codex profile parser cannot represent a literal permission path containing glob metacharacters. Choose a service data directory without these characters; the selected project path itself remains supported.",
      409,
    );
  const extraReads = Object.fromEntries(
    readRoots.map((path) => [path, "read"]),
  );
  const escapedLiteral = (path) =>
    path.replace(/[\\*?\[\]{}]/g, (character) => "\\" + character);
  const extraDenies = Object.fromEntries(
    denyRoots.map((path) => [escapedLiteral(path), "deny"]),
  );
  return {
    description: "Explicit local task roots; no ambient external tools",
    ...(projectRoot ? { workspace_roots: { [projectRoot]: true } } : {}),
    filesystem: {
      ":root": "deny",
      ":minimal": "read",
      ":slash_tmp": "deny",
      ":tmpdir": "deny",
      ":workspace_roots": workspace,
      "/opt/homebrew": "read",
      "/Library/Developer/CommandLineTools": "read",
      [resolve(homedir(), ".agents/skills")]: "read",
      [resolve(homedir(), ".codex/skills")]: "read",
      [dirname(process.execPath)]: "read",
      ...extraReads,
      ...extraDenies,
      ...secretDenies,
    },
    network: { enabled: false },
  };
}
export function profileOverrides(profileName, profile) {
  const toml = (value) => {
    if (typeof value === "string") return JSON.stringify(value);
    if (typeof value === "boolean") return String(value);
    if (value && typeof value === "object")
      return `{ ${Object.entries(value)
        .map(([key, child]) => `${JSON.stringify(key)} = ${toml(child)}`)
        .join(", ")} }`;
    throw new Error("Unsupported profile value");
  };
  return [
    `default_permissions=${JSON.stringify(profileName)}`,
    `permissions.${profileName}=${toml(profile)}`,
  ];
}
export async function externalToolDenials(executable, cwd) {
  let entries;
  try {
    const result = await run(executable, ["mcp", "list", "--json"], {
      cwd,
      env: runtimeEnvironment(),
      timeout: 8000,
      maxBuffer: 2 * 1024 * 1024,
    });
    entries = parseStrictJson(result.stdout);
  } catch {
    throw new ServiceError(
      "CAPABILITY_UNVERIFIED",
      "Cannot establish the local MCP tool boundary; inspect the supported Codex configuration before dispatch",
      409,
    );
  }
  fail(
    Array.isArray(entries),
    "CAPABILITY_UNVERIFIED",
    "Unexpected MCP inventory format",
    409,
  );
  const overrides = {
    "features.apps": false,
    "apps._default.enabled": false,
    web_search: "disabled",
    "features.skill_mcp_dependency_install": false,
  };
  for (const row of entries) {
    fail(
      typeof row.name === "string" && /^[A-Za-z0-9_-]{1,120}$/.test(row.name),
      "CAPABILITY_UNVERIFIED",
      "Unsupported MCP server identifier; explicit configuration review required",
      409,
    );
    if (row.enabled === true) {
      overrides[`mcp_servers.${row.name}.enabled`] = false;
      if (row.transport?.type === "stdio")
        overrides[`mcp_servers.${row.name}.command`] = "/usr/bin/false";
      else if (row.transport?.type === "streamable_http")
        overrides[`mcp_servers.${row.name}.url`] =
          "http://127.0.0.1:9/disabled";
      else
        throw new ServiceError(
          "CAPABILITY_UNVERIFIED",
          "Unsupported MCP transport; explicit configuration review required",
          409,
        );
    }
  }
  let effective;
  try {
    const checked = await run(
      executable,
      [
        ...overridesToArgv(overrides).flatMap((value) => ["-c", value]),
        "mcp",
        "list",
        "--json",
      ],
      {
        cwd,
        env: runtimeEnvironment(),
        timeout: 8000,
        maxBuffer: 2 * 1024 * 1024,
      },
    );
    effective = parseStrictJson(checked.stdout);
  } catch {
    throw new ServiceError(
      "CAPABILITY_UNVERIFIED",
      "Could not verify disabled ambient MCP configuration; no job dispatched",
      409,
    );
  }
  fail(
    Array.isArray(effective) && effective.every((row) => row.enabled === false),
    "CAPABILITY_UNVERIFIED",
    "Ambient external MCP tools remain enabled; no job dispatched",
    409,
  );
  return { overrides, disabled_server_count: effective.length };
}
export function overridesToArgv(overrides) {
  return Object.entries(overrides).map(
    ([key, value]) =>
      `${key}=${typeof value === "string" ? JSON.stringify(value) : String(value)}`,
  );
}
