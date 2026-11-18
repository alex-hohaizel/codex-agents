import { homedir } from "node:os";
import { createHash, randomUUID } from "node:crypto";
import {
  lstat,
  realpath,
  readFile,
  readdir,
  mkdir,
  open,
  rename,
} from "node:fs/promises";
import { resolve, relative, sep, dirname, basename, extname, isAbsolute, parse } from "node:path";
import { securePrivatePath, syncDirectory } from "./platform.mjs";
export class ServiceError extends Error {
  constructor(code, message, status = 400, details = {}) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
  }
}
export const fail = (condition, code, message, status = 400, details) => {
  if (!condition) throw new ServiceError(code, message, status, details);
};
export const now = () => new Date().toISOString();
export const id = (prefix) => `${prefix}_${randomUUID()}`;
export const sha = (value) => createHash("sha256").update(value).digest("hex");
export const canonical = (value) =>
  JSON.stringify(value, (_, v) =>
    v && typeof v === "object" && !Array.isArray(v)
      ? Object.fromEntries(
          Object.entries(v).sort(([a], [b]) =>
            Buffer.compare(Buffer.from(a), Buffer.from(b)),
          ),
        )
      : v,
  );
export const digest = (value) => sha(canonical(value));
export const text = (value, name, min = 1, max = 1e4) => {
  fail(
    typeof value === "string" &&
      value.trim().length >= min &&
      value.length <= max,
    "INVALID_INPUT",
    `${name} must contain ${min}–${max} characters`,
  );
  return value.trim();
};
export const array = (value, name, max = 100) => {
  fail(
    Array.isArray(value) && value.length <= max,
    "INVALID_INPUT",
    `${name} must be a bounded array`,
  );
  return value;
};
// JSON.parse accepts duplicate keys and overflows such as 1e999. Admission must not.
export function parseStrictJson(input, maxBytes = 2 * 1024 * 1024) {
  fail(
    typeof input === "string" && Buffer.byteLength(input) <= maxBytes,
    "INVALID_JSON",
    "JSON exceeds the size limit",
  );
  let i = 0;
  const whitespace = () => {
    while (/[ \t\r\n]/.test(input[i] ?? "") && i < input.length) i++;
  };
  const string = () => {
    const start = i++;
    let escaped = false;
    while (i < input.length) {
      const c = input[i++];
      if (c === '"' && !escaped) {
        try {
          return JSON.parse(input.slice(start, i));
        } catch {
          throw new ServiceError("INVALID_JSON", "Invalid JSON string");
        }
      }
      if (c === "\\" && !escaped) escaped = true;
      else escaped = false;
    }
    throw new ServiceError("INVALID_JSON", "Unterminated JSON string");
  };
  const value = (depth) => {
    fail(depth <= 64, "INVALID_JSON", "JSON nesting limit exceeded");
    whitespace();
    const c = input[i];
    if (c === '"') return string();
    if (c === "{") {
      i++;
      whitespace();
      const result = Object.create(null);
      const keys = new Set();
      if (input[i] === "}") {
        i++;
        return result;
      }
      while (i < input.length) {
        whitespace();
        fail(input[i] === '"', "INVALID_JSON", "Object key must be a string");
        const key = string();
        fail(
          !keys.has(key),
          "DUPLICATE_JSON_KEY",
          `Duplicate JSON key: ${key.slice(0, 80)}`,
        );
        keys.add(key);
        whitespace();
        fail(input[i++] === ":", "INVALID_JSON", "Missing colon");
        result[key] = value(depth + 1);
        whitespace();
        const end = input[i++];
        if (end === "}") return result;
        fail(end === ",", "INVALID_JSON", "Missing object separator");
      }
    } else if (c === "[") {
      i++;
      whitespace();
      const result = [];
      if (input[i] === "]") {
        i++;
        return result;
      }
      while (i < input.length) {
        result.push(value(depth + 1));
        whitespace();
        const end = input[i++];
        if (end === "]") return result;
        fail(end === ",", "INVALID_JSON", "Missing array separator");
      }
    } else {
      for (const [literal, result] of [
        ["true", true],
        ["false", false],
        ["null", null],
      ])
        if (input.startsWith(literal, i)) {
          i += literal.length;
          return result;
        }
      const match = /^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/.exec(
        input.slice(i),
      );
      if (match) {
        i += match[0].length;
        const result = Number(match[0]);
        fail(Number.isFinite(result), "INVALID_JSON", "Non-finite JSON number");
        return result;
      }
    }
    throw new ServiceError("INVALID_JSON", "Invalid or incomplete JSON value");
  };
  const result = value(0);
  whitespace();
  fail(i === input.length, "INVALID_JSON", "Unexpected trailing JSON data");
  return result;
}
export function redact(value, depth = 0) {
  if (depth > 18) return "[depth limited]";
  if (typeof value === "string")
    return value
      .replace(
        /\b(?:sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]{12,})/g,
        "[REDACTED]",
      )
      .replace(/(https?:\/\/)[^\s/@]+:[^\s/@]+@/g, "$1[REDACTED]@")
      .slice(0, 12e4);
  if (Array.isArray(value))
    return value.slice(0, 1e3).map((v) => redact(v, depth + 1));
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value).map(([key, v]) => [
        key,
        /^(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret|client_secret|private_key|authorization|cookie)$/i.test(
          key,
        )
          ? "[REDACTED]"
          : redact(v, depth + 1),
      ]),
    );
  return value;
}
export function containsObviousCredential(value, depth = 0) {
  if (depth > 64) return true;
  if (typeof value === "string")
    return (
      /\b(?:sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]{12,})/.test(value) ||
      /(https?:\/\/)[^\s/@]+:[^\s/@]+@/.test(value)
    );
  if (Array.isArray(value))
    return value.some((child) => containsObviousCredential(child, depth + 1));
  if (value && typeof value === "object")
    return Object.values(value).some((child) =>
      containsObviousCredential(child, depth + 1),
    );
  return false;
}
export function publicError(error) {
  return {
    code: error.code ?? "INTERNAL_ERROR",
    message:
      error instanceof ServiceError
        ? redact(error.message)
        : "The operation could not be completed",
    details: redact(error.details ?? {}),
  };
}
export function isWithin(root, target) {
  const path = relative(root, target);
  return (
    path === "" ||
    (!path.startsWith(`..${sep}`) && path !== ".." && !isAbsolute(path))
  );
}
const secretName =
  /^(?:\.env(?:\..*)?|credentials(?:\..*)?|owner-credentials\.json|id_(?:rsa|ed25519)|.*\.(?:pem|key|p12|pfx)|auth\.json)$/i;
export async function projectRoot(value) {
  const input = resolve(text(value, "root", 1, 4096));
  const root = await realpath(input);
  const stat = await lstat(root);
  fail(
    stat.isDirectory(),
    "INVALID_ROOT",
    "Select an existing project directory",
  );
  fail(
    root !== parse(root).root &&
      root !== (process.env.HOME ?? homedir()) &&
      root !== dirname(process.env.HOME ?? homedir()),
    "INVALID_ROOT",
    "Select a project directory, not a home or system root",
  );
  return root;
}
export async function safeFile(
  root,
  value,
  { directory = false, maxBytes = 2 * 1024 * 1024, allowMissing = false } = {},
) {
  const ref = text(value, "relative path", 1, 4096);
  fail(
    !ref.includes("\0") && !ref.split(/[\\/]/).includes(".."),
    "OUTSIDE_ROOT",
    "Parent traversal is not allowed",
  );
  const target = resolve(root, ref);
  fail(
    isWithin(root, target),
    "OUTSIDE_ROOT",
    "Path must stay inside the selected project",
  );
  const parts = relative(root, target).split(sep).filter(Boolean);
  if (process.platform === "win32") fail(parts.every(part => !part.includes(":") && !/[. ]$/.test(part) && !/^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)/i.test(part)), "OUTSIDE_ROOT", "Windows device, stream and alias paths are not supported");
  let current = root;
  for (const part of parts) {
    fail(
      !secretName.test(part) &&
        ![".git", ".aws", ".ssh", ".config", "node_modules"].includes(part),
      "PRIVATE_PATH",
      "This path is outside the artifact access scope",
    );
    current = resolve(current, part);
    try {
      fail(
        !(await lstat(current)).isSymbolicLink(),
        "OUTSIDE_ROOT",
        "Symlink access is not allowed",
      );
    } catch (error) {
      if (error.code === "ENOENT" && allowMissing) return target;
      throw error;
    }
  }
  const stat = await lstat(target);
  fail(
    directory ? stat.isDirectory() : stat.isFile(),
    "INVALID_PATH",
    directory ? "Expected a directory" : "Expected a file",
  );
  fail(
    directory || stat.size <= maxBytes,
    "FILE_TOO_LARGE",
    "File exceeds the preview limit",
  );
  return target;
}
export async function readSource(root, ref) {
  const path = await safeFile(root, ref);
  const bytes = await readFile(path);
  return {
    path: ref,
    sha256: sha(bytes),
    bytes: bytes.length,
    text: bytes.toString("utf8"),
  };
}
export async function exists(path) {
  try {
    await lstat(path);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}
export async function atomicWrite(path, bytes) {
  await mkdir(dirname(path), {
    recursive: true,
    mode: 448,
  });
  const temporary = `${path}.${randomUUID()}.tmp`;
  const file = await open(temporary, "wx", 384);
  try {
    await securePrivatePath(temporary);
    await file.writeFile(bytes);
    await file.sync();
  } finally {
    await file.close();
  }
  await rename(temporary, path);
  await syncDirectory(dirname(path));
}
export async function listArtifacts(root, { limit = 250 } = {}) {
  const result = [];
  const scan = async (folder, depth) => {
    if (depth > 5 || result.length >= limit) return;
    let entries;
    try {
      entries = await readdir(folder, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
      if (result.length >= limit) return;
      if (
        entry.isSymbolicLink() ||
        secretName.test(entry.name) ||
        [
          ".git",
          "node_modules",
          "dist",
          "build",
          ".aws",
          ".ssh",
          ".codex",
          ".agents",
        ].includes(entry.name)
      )
        continue;
      const path = resolve(folder, entry.name);
      const ref = relative(root, path);
      if (entry.isDirectory()) {
        if (
          !entry.name.startsWith(".") ||
          [
            ".gameatelier",
            ".appatelier",
            ".chatbotatelier",
            ".agent-foundry",
          ].includes(entry.name)
        )
          await scan(path, depth + 1);
      } else if (
        /\.(?:md|json|ya?ml|txt|png|jpe?g|webp|gif|svg|pdf|mp3|wav|m4a|mp4|webm|csv|ts|tsx|js|mjs|py|go|rs|swift|kt)$/i.test(
          entry.name,
        )
      ) {
        const stat = await lstat(path);
        result.push({
          id: sha(ref).slice(0, 16),
          path: ref,
          name: basename(ref),
          bytes: stat.size,
          modified_at: stat.mtime.toISOString(),
          kind: /\.(png|jpe?g|webp|gif|svg)$/i.test(ref)
            ? "image"
            : /\.(mp3|wav|m4a)$/i.test(ref)
              ? "audio"
              : /\.(mp4|webm)$/i.test(ref)
                ? "video"
                : "source",
          extension: extname(ref).slice(1),
        });
      }
    }
  };
  await scan(root, 0);
  return result;
}
