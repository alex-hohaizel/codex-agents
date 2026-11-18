import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { homedir } from "node:os";
import { resolveNativeCommand } from "./platform.mjs";
import { lstat, readdir, realpath } from "node:fs/promises";
import { runtimeEnvironment } from "./environment.mjs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import {
  digest,
  fail,
  isWithin,
  parseStrictJson,
  safeFile,
  ServiceError,
  text,
} from "./utils.mjs";
const run = promisify(execFile);

export const NATIVE_AUTHORITY_NAMES = Object.freeze([
  ".git",
  ".agents",
  ".codex",
  ".agent-foundry",
  ".appatelier",
  ".chatbotatelier",
  ".chatbot-atelier",
  ".gameatelier",
  ".atelier",
]);
const nativeNames = new Set(NATIVE_AUTHORITY_NAMES);
const globCharacters = /[\\*?\[\]{}]/;
const nativePath = (path) => process.platform === "win32" ? path.replaceAll("\\", "/") : path;
const absoluteGlob = (path) => globCharacters.test(nativePath(path));
const escapeLiteral = (path) =>
  nativePath(path).replace(/[\\*?\[\]{}]/g, (character) => "\\" + character);
const nativePattern = (name) =>
  name.replace(
    /[a-z]/g,
    (character) => `[${character}${character.toUpperCase()}]`,
  );

export function taskMemoryMode(value) {
  const mode = value === undefined ? "inherit" : value;
  fail(
    typeof mode === "string" && ["inherit", "disabled"].includes(mode),
    "INVALID_INPUT",
    "memory_mode must be inherit or disabled",
  );
  return mode;
}

// Resolve the existing native home without changing it or reading its config.
// Both lexical and canonical paths matter when a supported home/store is linked.
export async function codexMemoryDenyRoots(
  codexHome = process.env.CODEX_HOME ?? join(homedir(), ".codex"),
) {
  const supported = (path) =>
    typeof path === "string" &&
    isAbsolute(path) &&
    !path.includes("\0") &&
    !absoluteGlob(path);
  fail(
    supported(codexHome),
    "CAPABILITY_UNVERIFIED",
    "The existing Codex home cannot be represented safely for task-only memory isolation",
    409,
  );
  const home = resolve(codexHome);
  let canonicalHome;
  try {
    canonicalHome = await realpath(home);
    fail(
      supported(canonicalHome) && (await lstat(canonicalHome)).isDirectory(),
      "CAPABILITY_UNVERIFIED",
      "The existing Codex home is not a supported directory for task-only memory isolation",
      409,
    );
  } catch (error) {
    if (error instanceof ServiceError) throw error;
    throw new ServiceError(
      "CAPABILITY_UNVERIFIED",
      "Cannot resolve the existing Codex home for task-only memory isolation",
      409,
    );
  }
  const roots = new Set();
  for (const name of ["memories", "memories_v2"]) {
    const path = join(home, name);
    roots.add(path);
    roots.add(join(canonicalHome, name));
    try {
      const target = await realpath(path);
      fail(
        supported(target) && (await lstat(target)).isDirectory(),
        "CAPABILITY_UNVERIFIED",
        "A native memory store cannot be isolated with the supported path contract",
        409,
      );
      roots.add(target);
    } catch (error) {
      // Also deny a not-yet-created native store; never create it here.
      if (error.code === "ENOENT") {
        try {
          await lstat(path);
        } catch (missing) {
          if (missing.code === "ENOENT") continue;
          throw new ServiceError(
            "CAPABILITY_UNVERIFIED",
            "Cannot inspect a native memory-store path for task-only isolation",
            409,
          );
        }
        throw new ServiceError(
          "CAPABILITY_UNVERIFIED",
          "A dangling native memory-store link cannot be isolated safely",
          409,
        );
      }
      if (error instanceof ServiceError) throw error;
      throw new ServiceError(
        "CAPABILITY_UNVERIFIED",
        "Cannot resolve a native memory store for task-only memory isolation",
        409,
      );
    }
  }
  return [...roots].sort();
}

export function writablePaths(paths) {
  return paths.map((value) => {
    const path = text(value, "writable relative path", 1, 4096);
    const parts = path.split("/").filter((part) => part !== "" && part !== ".");
    fail(
      !path.startsWith("/") && !parts.includes("..") && !path.includes("\0"),
      "OUTSIDE_ROOT",
      "Writable paths must be relative to the selected project",
    );
    fail(
      !parts.some((part) => nativeNames.has(part.toLowerCase())),
      "PRIVATE_PATH",
      "Native authority directories are read-only; choose an artifact directory",
      409,
    );
    fail(
      !globCharacters.test(path),
      "CAPABILITY_UNVERIFIED",
      "The installed Codex parser cannot represent this literal writable path safely; choose a directory without glob metacharacters",
      409,
    );
    return parts.join("/") || ".";
  });
}

// Inventory supplies exact read exceptions to recursive deny rules. Never follow
// links or silently truncate: an omitted native root would lose its normal read.
export async function nativeAuthoritySnapshot(
  projectRoot,
  allowedPaths,
  { maxEntries = 200000, maxDepth = 128 } = {},
) {
  const root = await realpath(projectRoot);
  fail(
    root === resolve(projectRoot),
    "OUTSIDE_ROOT",
    "Use the canonical project root",
    409,
  );
  const paths = [...new Set(writablePaths(allowedPaths))].sort();
  const roots = [];
  for (const path of paths) {
    const target = await safeFile(root, path, { directory: true });
    const stat = await lstat(target);
    roots.push({ path, device: String(stat.dev), inode: String(stat.ino) });
  }
  const pending = roots.map(({ path }) => ({
    path: resolve(root, path),
    depth: 0,
  }));
  const visited = new Set(),
    protectedPaths = [];
  let entriesSeen = 0;
  while (pending.length) {
    const current = pending.pop();
    if (visited.has(current.path)) continue;
    visited.add(current.path);
    fail(
      current.depth <= maxDepth,
      "CAPABILITY_UNVERIFIED",
      "Native authority inventory exceeds the supported depth; choose a narrower write directory",
      409,
    );
    const stat = await lstat(current.path);
    fail(
      !stat.isSymbolicLink() &&
        stat.isDirectory() &&
        (await realpath(current.path)) === current.path &&
        isWithin(root, current.path),
      "OUTSIDE_ROOT",
      "Native authority inventory changed or crossed a symlink",
      409,
    );
    const entries = await readdir(current.path, { withFileTypes: true });
    entriesSeen += entries.length;
    fail(
      entriesSeen <= maxEntries,
      "CAPABILITY_UNVERIFIED",
      "Native authority inventory exceeds the supported size; choose a narrower write directory",
      409,
    );
    for (const entry of entries) {
      const target = resolve(current.path, entry.name);
      if (nativeNames.has(entry.name.toLowerCase())) {
        const native = await lstat(target);
        fail(
          !native.isSymbolicLink() && (native.isDirectory() || native.isFile()),
          "CAPABILITY_UNVERIFIED",
          "Native authority paths must be regular files or directories, not links",
          409,
        );
        const path = relative(root, target).replaceAll("\\", "/");
        fail(
          !absoluteGlob(path),
          "CAPABILITY_UNVERIFIED",
          "A native authority read path contains unsupported literal glob metacharacters; choose a narrower write directory",
          409,
        );
        protectedPaths.push({
          path,
          kind: native.isDirectory() ? "directory" : "file",
          device: String(native.dev),
          inode: String(native.ino),
        });
      }
      if (entry.isDirectory())
        pending.push({ path: target, depth: current.depth + 1 });
    }
  }
  protectedPaths.sort((a, b) =>
    a.path < b.path ? -1 : a.path > b.path ? 1 : 0,
  );
  const snapshot = {
    schema_version: "atelier.native-authority-scope/1",
    root,
    roots,
    protected_paths: protectedPaths,
  };
  return { ...snapshot, sha256: digest(snapshot) };
}

export function localProfile(
  scope = "read-only",
  allowedPaths = [],
  readRoots = [],
  projectRoot = null,
  denyRoots = [],
  nativeAuthority = null,
) {
  const workspace = { ".": "read" };
  const writes = scope === "workspace-write" ? writablePaths(allowedPaths) : [];
  if (scope === "workspace-write")
    for (const path of writes)
      workspace[
        path === "." || path === "" ? "." : path.replaceAll("\\", "/")
      ] = "write";
  for (const path of NATIVE_AUTHORITY_NAMES) workspace[path] = "read";
  if (nativeAuthority) {
    fail(
      nativeAuthority.root === resolve(projectRoot),
      "SCOPE_MISMATCH",
      "Native authority inventory belongs to another project",
      409,
    );
    for (const { path } of nativeAuthority.protected_paths)
      workspace[path] = "read";
  }
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
  const extraDenies = Object.fromEntries(
    denyRoots.map((path) => [escapeLiteral(path), "deny"]),
  );
  const nativeDenies = {};
  if (writes.length) {
    fail(
      projectRoot,
      "CAPABILITY_UNVERIFIED",
      "Workspace writes need an exact selected project root",
      409,
    );
    // Absolute escaped deny globs avoid Codex0.166's broken expansion of scoped
    // globs when the selected root contains '['. Exact relative reads above
    // preserve existing native sources; unknown/future metadata paths stay deny.
    for (const path of writes) {
      const target = resolve(projectRoot, path);
      for (const name of NATIVE_AUTHORITY_NAMES)
        nativeDenies[`${escapeLiteral(target)}/**/${nativePattern(name)}`] =
          "deny";
    }
  }
  return {
    description: "Explicit local task roots; no ambient external tools",
    ...(projectRoot ? { workspace_roots: { [projectRoot]: true } } : {}),
    filesystem: {
      ":root": "deny",
      ":minimal": "read",
      ":slash_tmp": "deny",
      ":tmpdir": "deny",
      ":workspace_roots": workspace,
      ...(process.platform === "darwin" ? { "/opt/homebrew": "read", "/Library/Developer/CommandLineTools": "read" } : {}),
      [resolve(homedir(), ".agents/skills")]: "read",
      [resolve(homedir(), ".codex/skills")]: "read",
      [dirname(process.execPath)]: "read",
      ...extraReads,
      ...extraDenies,
      ...nativeDenies,
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
  const native = await resolveNativeCommand(executable);
  let entries;
  try {
    const result = await run(native.command, [...native.args, "mcp", "list", "--json"], {
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
      if (row.transport?.type === "stdio") {
        overrides[`mcp_servers.${row.name}.command`] = process.platform === "win32" ? process.execPath : "/usr/bin/false";
        if (process.platform === "win32") overrides[`mcp_servers.${row.name}.args`] = ["-e", "process.exit(1)"];
      }
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
      native.command,
      [
        ...native.args,
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
      `${key}=${typeof value === "string" || Array.isArray(value) ? JSON.stringify(value) : String(value)}`,
  );
}
