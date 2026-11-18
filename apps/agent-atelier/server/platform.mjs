/** Platform operations shared by the packaged installer and local workbench.
 * POSIX privacy remains owner-only modes. Windows privacy is a verified native
 * protected DACL, provided by the same reviewed Python adapter as the updater.
 */
import { lstat, realpath, chmod, open, readFile } from "node:fs/promises";
import { join, dirname, resolve, delimiter, isAbsolute, win32, posix } from "node:path";
import { homedir } from "node:os";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { runtimeEnvironment } from "./environment.mjs";
const run = promisify(execFile);
const here = dirname(fileURLToPath(import.meta.url));

export function platformStateRoot({ platform = process.platform, env = process.env, home = homedir(), product = false } = {}) {
  if (platform === "win32")
    return win32.join((env.LOCALAPPDATA && win32.isAbsolute(env.LOCALAPPDATA) ? env.LOCALAPPDATA : win32.join(home, "AppData", "Local")), ...(product ? ["Codex Agent System", "Agent Atelier"] : ["Agent Atelier"]));
  if (platform === "darwin")
    return posix.join(home, "Library/Application Support", ...(product ? ["Codex Agent System", "Agent Atelier"] : ["Agent Atelier"]));
  return posix.join((env.XDG_DATA_HOME && posix.isAbsolute(env.XDG_DATA_HOME) ? env.XDG_DATA_HOME : posix.join(home, ".local/share")), ...(product ? ["codex-agent-system", "agent-atelier"] : ["agent-atelier"]));
}

export function pythonExecutable(env = process.env, platform = process.platform) {
  return env.AGENT_SYSTEM_PYTHON || (platform === "win32" ? "python" : "python3");
}

async function executablePath(command, { env = process.env, platform = process.platform } = {}) {
  if (typeof command !== "string" || !command || /[\0\r\n]/.test(command)) throw new Error("Invalid native executable path");
  const explicit = isAbsolute(command) || command.includes("/") || command.includes("\\");
  const extensions = platform === "win32" && !/\.(?:exe|cmd|bat|js|mjs)$/i.test(command) ? [".exe", ".cmd", ".bat", ""] : [""];
  const paths = explicit ? [resolve(command)] : (env.PATH ?? env.Path ?? "").split(platform === "win32" ? ";" : delimiter).filter(Boolean).flatMap(folder => extensions.map(ext => join(folder, command + ext)));
  for (const path of paths) {
    try {
      if (!(await lstat(path)).isFile() && !(await lstat(path)).isSymbolicLink()) continue;
      const canonical = await realpath(path);
      if ((await lstat(canonical)).isFile()) return canonical;
    } catch (error) { if (!["ENOENT", "ENOTDIR"].includes(error.code)) throw error; }
  }
  throw new Error("Native executable is unavailable; use the ready package or install its documented host prerequisite");
}

/** Resolve an executable without ever passing an untrusted command line to a shell. */
export async function resolveNativeCommand(command, args = [], options = {}) {
  const platform = options.platform ?? process.platform;
  if (!Array.isArray(args) || args.some(v => typeof v !== "string" || v.includes("\0"))) throw new Error("Invalid native argument array");
  let path = await executablePath(command, options);
  if (/\.(?:cmd|bat)$/i.test(path)) {
    // The supported npm Codex shim has one reviewed JS entry; execute it with
    // this Node runtime instead of cmd.exe and its second quoting language.
    if (!/^codex\.(?:cmd|bat)$/i.test(path.split(/[\\/]/).at(-1))) throw new Error("Batch executables require a native executable, not shell execution");
    const candidate = join(dirname(path), "node_modules", "@openai", "codex", "bin", "codex.js");
    try {
      const metadata = JSON.parse(await readFile(join(dirname(path), "node_modules", "@openai", "codex", "package.json"), "utf8"));
      if (metadata.name !== "@openai/codex") throw new Error("Unrecognized Codex package identity");
      path = await realpath(candidate);
    }
    catch { throw new Error("Cannot resolve the installed Codex npm entry; select codex.exe or reinstall the supported Codex CLI"); }
    const info = await lstat(path);
    if (!info.isFile() || info.size > 2 * 1024 * 1024) throw new Error("Unexpected installed Codex npm entry");
  }
  if (/\.(?:js|mjs)$/i.test(path)) return { command: process.execPath, args: [path, ...args], source: path };
  if (platform === "win32" && !/\.exe$/i.test(path)) throw new Error("Windows native tools require an executable or the reviewed Codex JS entry");
  return { command: path, args: [...args], source: path };
}

export async function resolvePythonCommand(env = process.env) {
  const command = pythonExecutable(env);
  const path = await executablePath(command, { env });
  if (process.platform === "win32" && /[\\/]Microsoft[\\/]WindowsApps[\\/]/i.test(path)) throw new Error("Use the included Python runtime, not a Windows Store alias");
  return { command: path, args: [] };
}

async function windowsPrivacy(path, action, { pythonPath } = {}) {
  const command = await resolvePythonCommand(pythonPath ? { ...process.env, AGENT_SYSTEM_PYTHON: pythonPath } : process.env);
  try {
    const response = await run(command.command, [...command.args, "-I", "-X", "utf8", "-B", join(here, "platform_support.py"), action, resolve(path)], { windowsHide: true, timeout: 15000, maxBuffer: 256 * 1024, env: runtimeEnvironment(process.env) });
    JSON.parse(response.stdout);
  } catch { throw new Error("Windows private-file ACL could not be established or verified; use the ready bundle and a user-owned local folder"); }
}

export async function assertPrivatePath(path, { directory = false, pythonPath } = {}) {
  const info = await lstat(path);
  if ((directory ? !info.isDirectory() : !info.isFile()) || info.isSymbolicLink()) throw new Error("Private state must use an unlinked regular file or directory");
  if (process.platform === "win32") await windowsPrivacy(path, "--assert-private", { pythonPath });
  else if ((info.mode & 0o077) !== 0 || (typeof process.getuid === "function" && info.uid !== process.getuid())) throw new Error("Private state must be owned by the current user with owner-only permissions");
  return info;
}

export async function securePrivatePath(path, { directory = false, pythonPath } = {}) {
  const info = await lstat(path);
  if ((directory ? !info.isDirectory() : !info.isFile()) || info.isSymbolicLink()) throw new Error("Refusing to change linked or irregular private state");
  if (process.platform === "win32") await windowsPrivacy(path, "--make-private", { pythonPath });
  else await chmod(path, directory ? 0o700 : 0o600);
  return assertPrivatePath(path, { directory, pythonPath });
}

export async function syncDirectory(path) {
  // Windows rename + flushed files are the supported boundary. Opening and
  // fsync'ing a directory is unavailable there; do not pretend a POSIX fsync.
  if (process.platform === "win32") return;
  const handle = await open(path, "r");
  try { await handle.sync(); } finally { await handle.close(); }
}

export function logicalMode(info, expected) {
  if (process.platform !== "win32") return info.mode & 0o777;
  // Windows has no executable-bit representation. Keep the declared logical
  // mode while verifying its actual read-only attribute separately.
  const writable = (info.mode & 0o222) !== 0;
  if (expected !== undefined && writable === ((expected & 0o222) !== 0)) return expected;
  return info.mode & 0o666;
}

export function isPortableAbsolutePath(value) {
  return typeof value === "string" && (posix.isAbsolute(value) || win32.isAbsolute(value));
}
export function absolutePathPrefixes(value) {
  if (!isPortableAbsolutePath(value)) return [];
  const api = win32.isAbsolute(value) && !posix.isAbsolute(value) ? win32 : posix;
  const root = api.parse(value).root;
  let prefix = root;
  return value.slice(root.length).split(api.sep).filter(Boolean).map(part => (prefix = api.join(prefix, part)));
}

export function portablePathIdentity(value) {
  return typeof value === "string" && win32.isAbsolute(value) && !posix.isAbsolute(value)
    ? win32.normalize(value).toLowerCase() : value;
}
export function portablePathWithin(root, value) {
  if (!isPortableAbsolutePath(root) || !isPortableAbsolutePath(value)) return false;
  const windows = win32.isAbsolute(root) && !posix.isAbsolute(root);
  if (windows !== (win32.isAbsolute(value) && !posix.isAbsolute(value))) return false;
  const api = windows ? win32 : posix, rel = api.relative(root, value);
  return rel === "" || (!api.isAbsolute(rel) && rel !== ".." && !rel.startsWith(".." + api.sep));
}
